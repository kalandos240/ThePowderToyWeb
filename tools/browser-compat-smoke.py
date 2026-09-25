#!/usr/bin/env python3
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("TPT_COMPAT_URL", "http://127.0.0.1:8766")
ARTIFACT_DIR = Path(os.environ.get("TPT_COMPAT_ARTIFACT_DIR", "compat-artifacts"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

SDK_MOCK = r"""
window.__yandexLoadingReady = false;
window.__yandexGameplayStarted = false;
window.__yandexReadyCount = 0;
window.__yandexSdkEvents = [];
window.__yandexReadySnapshot = null;
window.YaGames = {
  init: async () => {
    const params = new URLSearchParams(location.search);
    const deviceType = params.get("device") || "desktop";
    return {
      environment: { i18n: { lang: params.get("lang") || "en" } },
      deviceInfo() {
        return {
          type: deviceType,
          isMobile() { return deviceType === "mobile"; },
          isTablet() { return deviceType === "tablet"; }
        };
      },
      features: {
        LoadingAPI: {
          ready() {
            window.__yandexLoadingReady = true;
            window.__yandexReadyCount += 1;
            window.__yandexSdkEvents.push("ready");
            const loader = document.getElementById("loader");
            const canvas = document.getElementById("canvas");
            window.__yandexReadySnapshot = {
              loaderHidden: Boolean(loader?.hidden),
              canvasDisplay: canvas ? getComputedStyle(canvas).display : "",
              ariaBusy: document.getElementById("app")?.getAttribute("aria-busy") || ""
            };
          }
        },
        GameplayAPI: {
          start() {
            window.__yandexGameplayStarted = true;
            window.__yandexSdkEvents.push("gameplay-start");
          },
          stop() {
            window.__yandexGameplayStarted = false;
            window.__yandexSdkEvents.push("gameplay-stop");
          }
        }
      },
      __listeners: {},
      on(event, callback) {
        this.__listeners[event] ??= [];
        this.__listeners[event].push(callback);
      },
      emit(event) {
        for (const callback of this.__listeners[event] || []) {
          callback();
        }
      }
    };
  }
};
"""


def run_case(browser, browser_name: str, language: str, mobile: bool):
    label = f"{browser_name}-{'mobile' if mobile else 'desktop'}-{language}"
    viewport = {"width": 844, "height": 390} if mobile else {"width": 1365, "height": 768}
    context_args = {
        "viewport": viewport,
        "device_scale_factor": 3 if mobile else 1,
        "has_touch": mobile,
        "is_mobile": mobile,
    }
    if mobile:
        context_args["user_agent"] = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 "
            "Mobile/15E148 Safari/604.1"
        )

    context = browser.new_context(**context_args)
    console_errors = []
    page_errors = []

    context.route(
        "**/sdk.js",
        lambda route: route.fulfill(
            status=200,
            content_type="application/javascript; charset=utf-8",
            body=SDK_MOCK,
        ),
    )
    page = context.new_page()
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    try:
        device_type = "mobile" if mobile else "desktop"
        page.goto(
            f"{BASE_URL}/?lang={language}&device={device_type}",
            wait_until="domcontentloaded",
            timeout=45000,
        )
        page.wait_for_function(
            """
            () => {
              const canvas = document.getElementById('canvas');
              const loader = document.getElementById('loader');
              const fatal = document.getElementById('fatal');
              return Boolean(
                canvas &&
                canvas.style.display === 'block' &&
                loader && loader.hidden &&
                fatal && fatal.hidden &&
                window.__tptGameModule &&
                window.__yandexLoadingReady === true &&
                window.__yandexGameplayStarted === true
              );
            }
            """,
            timeout=45000,
        )

        state = page.evaluate(
            """
            () => {
              const canvas = document.getElementById('canvas');
              const rect = canvas.getBoundingClientRect();
              const events = window.__yandexSdkEvents || [];
              const app = document.getElementById('app');
              const contextEvent = new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                clientX: 2,
                clientY: 2,
              });
              const dispatchResult = app.dispatchEvent(contextEvent);
              return {
                language: window.tptLanguage,
                sdkMobilePlatform: window.__tptSdkMobilePlatform,
                touchUI: window.tptTouchUIDetected,
                readyCount: window.__yandexReadyCount || 0,
                readyIndex: events.indexOf('ready'),
                gameplayStartIndex: events.indexOf('gameplay-start'),
                loaderHidden: document.getElementById('loader').hidden,
                fatalHidden: document.getElementById('fatal').hidden,
                canvasDisplay: canvas.style.display,
                canvasLeft: rect.left,
                canvasTop: rect.top,
                canvasRight: rect.right,
                canvasBottom: rect.bottom,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                scrollWidth: document.documentElement.scrollWidth,
                scrollHeight: document.documentElement.scrollHeight,
                contextMenuPrevented:
                  contextEvent.defaultPrevented === true && dispatchResult === false,
                runtimePaused: window.__tptRuntimePaused === true,
                orientationBlocked: window.__tptOrientationBlocked === true,
              };
            }
            """
        )

        assert state["language"] == language, (label, state)
        assert state["sdkMobilePlatform"] is mobile, (label, state)
        if mobile:
            assert state["touchUI"] is True, (label, "touch UI was not enabled", state)
        assert state["readyCount"] == 1, (label, state)
        assert state["readyIndex"] >= 0, (label, state)
        assert state["gameplayStartIndex"] > state["readyIndex"], (label, state)
        assert state["loaderHidden"] is True and state["fatalHidden"] is True, (label, state)
        assert state["canvasDisplay"] == "block", (label, state)
        assert state["canvasLeft"] >= -1 and state["canvasTop"] >= -1, (label, state)
        assert state["canvasRight"] <= state["viewportWidth"] + 1, (label, state)
        assert state["canvasBottom"] <= state["viewportHeight"] + 1, (label, state)
        assert state["scrollWidth"] <= state["viewportWidth"] + 1, (label, state)
        assert state["scrollHeight"] <= state["viewportHeight"] + 1, (label, state)
        assert state["contextMenuPrevented"] is True, (label, state)
        assert state["runtimePaused"] is False, (label, state)
        assert state["orientationBlocked"] is False, (label, state)

        external_resources = page.evaluate(
            """
            () => performance.getEntriesByType('resource')
              .map((entry) => entry.name)
              .filter((name) => {
                try {
                  const url = new URL(name, location.href);
                  return (
                    (url.protocol === 'http:' || url.protocol === 'https:') &&
                    url.origin !== location.origin
                  );
                } catch {
                  return false;
                }
              })
            """
        )
        assert external_resources == [], (label, "external runtime resources", external_resources)

        if mobile:
            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_function(
                """
                () =>
                  window.__tptOrientationBlocked === true &&
                  window.__tptRuntimePaused === true &&
                  window.__yandexGameplayStarted === false
                """,
                timeout=10000,
            )
            page.set_viewport_size({"width": 844, "height": 390})
            page.wait_for_function(
                """
                () =>
                  window.__tptOrientationBlocked === false &&
                  window.__tptRuntimePaused === false &&
                  window.__yandexGameplayStarted === true
                """,
                timeout=10000,
            )

        page.screenshot(path=str(ARTIFACT_DIR / f"{label}.png"), full_page=True)
        assert not page_errors, (label, "page errors", page_errors)
        assert not console_errors, (label, "console errors", console_errors)

        result = {
            "label": label,
            "browser": browser_name,
            "language": language,
            "mobile": mobile,
            "state": state,
            "external_resources": external_resources,
        }
        print(f"[compat] {label}: OK")
        return result
    except Exception as error:
        try:
            page.screenshot(
                path=str(ARTIFACT_DIR / f"{label}-failure.png"),
                full_page=True,
            )
        except Exception:
            pass

        failure = {
            "label": label,
            "browser": browser_name,
            "language": language,
            "mobile": mobile,
            "error": repr(error),
            "console_errors": console_errors,
            "page_errors": page_errors,
        }
        with (ARTIFACT_DIR / f"{label}-failure.json").open(
            "w", encoding="utf-8"
        ) as handle:
            json.dump(failure, handle, ensure_ascii=False, indent=2)
        raise
    finally:
        context.close()


def main():
    report = []
    with sync_playwright() as playwright:
        firefox = playwright.firefox.launch(headless=True)
        try:
            report.append(run_case(firefox, "firefox", "en", mobile=False))
            report.append(run_case(firefox, "firefox", "ru", mobile=False))
        finally:
            firefox.close()

        webkit = playwright.webkit.launch(headless=True)
        try:
            report.append(run_case(webkit, "webkit", "en", mobile=False))
            report.append(run_case(webkit, "webkit", "en", mobile=True))
            report.append(run_case(webkit, "webkit", "ru", mobile=True))
        finally:
            webkit.close()

    with (ARTIFACT_DIR / "compatibility.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
