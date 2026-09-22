#!/usr/bin/env python3
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("TPT_SMOKE_URL", "http://127.0.0.1:8765")
ARTIFACT_DIR = os.environ.get("TPT_SMOKE_ARTIFACT_DIR", "test-artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)


def make_driver(mobile: bool):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,768")
    if mobile:
        options.add_experimental_option(
            "mobileEmulation",
            {
                "deviceMetrics": {
                    "width": 390,
                    "height": 844,
                    "pixelRatio": 3.0,
                    "touch": True,
                    "mobile": True,
                },
                "userAgent": (
                    "Mozilla/5.0 (Linux; Android 14; Pixel 7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/140.0 Mobile Safari/537.36"
                ),
            },
        )
    return webdriver.Chrome(options=options)


def smoke_case(language: str, mobile: bool):
    label = f"{'mobile' if mobile else 'desktop'}-{language}"
    driver = make_driver(mobile)
    try:
        driver.set_page_load_timeout(45)
        driver.get(f"{BASE_URL}/?lang={language}")

        wait = WebDriverWait(driver, 45)
        wait.until(
            lambda d: d.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const fatal = document.getElementById('fatal');
                const loader = document.getElementById('loader');
                return Boolean(
                    canvas &&
                    canvas.style.display === 'block' &&
                    fatal && fatal.hidden &&
                    loader && loader.hidden &&
                    getComputedStyle(loader).display === 'none' &&
                    window.__yandexLoadingReady === true &&
                    (
                        window.__tptOrientationBlocked === true
                            ? window.__yandexGameplayStarted === false
                            : window.__yandexGameplayStarted === true
                    )
                );
                """
            )
        )

        state = driver.execute_script(
            """
            const canvas = document.getElementById('canvas');
            const rect = canvas.getBoundingClientRect();
            return {
                language: window.tptLanguage,
                touchUI: window.tptTouchUIDetected,
                fatalHidden: document.getElementById('fatal').hidden,
                loaderHidden: document.getElementById('loader').hidden,
                loaderDisplay: getComputedStyle(document.getElementById('loader')).display,
                canvasDisplay: canvas.style.display,
                canvasWidth: rect.width,
                canvasHeight: rect.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                maxTouchPoints: navigator.maxTouchPoints,
                coarsePointer: window.matchMedia('(pointer: coarse)').matches,
                orientationBlocked: window.__tptOrientationBlocked === true,
                orientationDisplay: getComputedStyle(document.getElementById('orientation-gate')).display,
                ready: window.__yandexLoadingReady,
                gameplay: window.__yandexGameplayStarted,
            };
            """
        )

        assert state["language"] == language, (label, state)
        assert state["fatalHidden"] is True, (label, state)
        assert state["loaderHidden"] is True, (label, state)
        assert state["loaderDisplay"] == "none", (label, state)
        assert state["canvasDisplay"] == "block", (label, state)
        assert state["canvasWidth"] > 0 and state["canvasHeight"] > 0, (label, state)
        assert state["canvasWidth"] <= state["viewportWidth"] + 1, (label, state)
        assert state["canvasHeight"] <= state["viewportHeight"] + 1, (label, state)
        assert state["ready"] is True, (label, state)

        driver.save_screenshot(os.path.join(ARTIFACT_DIR, f"{label}-initial.png"))

        if mobile:
            assert state["maxTouchPoints"] > 0 or state["coarsePointer"], (label, state)
            assert state["touchUI"] is True, (label, state)
            assert state["orientationBlocked"] is True, (label, state)
            assert state["orientationDisplay"] != "none", (label, state)
            assert state["gameplay"] is False, (label, state)
        else:
            assert state["touchUI"] is False, (label, state)
            assert state["orientationBlocked"] is False, (label, state)
            assert state["orientationDisplay"] == "none", (label, state)
            assert state["gameplay"] is True, (label, state)

        if mobile:
            driver.execute_cdp_cmd(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": 844,
                    "height": 390,
                    "deviceScaleFactor": 3.0,
                    "mobile": True,
                    "screenOrientation": {
                        "type": "landscapePrimary",
                        "angle": 90,
                    },
                },
            )
            driver.execute_script("window.dispatchEvent(new Event('orientationchange'));")
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptOrientationBlocked === false && window.__yandexGameplayStarted === true"
                )
            )
        else:
            driver.set_window_size(800, 600)

        time.sleep(0.5)
        resized = driver.execute_script(
            """
            const rect = document.getElementById('canvas').getBoundingClientRect();
            return {
                width: rect.width,
                height: rect.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                fatalHidden: document.getElementById('fatal').hidden,
                orientationBlocked: window.__tptOrientationBlocked === true,
                orientationDisplay: getComputedStyle(document.getElementById('orientation-gate')).display,
                gameplay: window.__yandexGameplayStarted,
            };
            """
        )
        assert resized["fatalHidden"] is True, (label, resized)
        assert resized["width"] > 0 and resized["height"] > 0, (label, resized)
        assert resized["width"] <= resized["viewportWidth"] + 1, (label, resized)
        assert resized["height"] <= resized["viewportHeight"] + 1, (label, resized)
        assert resized["orientationBlocked"] is False, (label, resized)
        assert resized["orientationDisplay"] == "none", (label, resized)
        assert resized["gameplay"] is True, (label, resized)

        if mobile:
            # Prove touch still maps into the simulation after portrait -> landscape.
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestSelectDust', null, [], [])"
            )
            before_particles = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            touch_rect = driver.execute_script(
                """
                const r = document.getElementById('canvas').getBoundingClientRect();
                return {left:r.left, top:r.top, width:r.width, height:r.height};
                """
            )
            x0 = touch_rect["left"] + touch_rect["width"] * 0.30
            y0 = touch_rect["top"] + touch_rect["height"] * 0.38
            x1 = touch_rect["left"] + touch_rect["width"] * 0.48
            y1 = touch_rect["top"] + touch_rect["height"] * 0.48
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [{"x": x0, "y": y0, "radiusX": 4, "radiusY": 4, "force": 1}],
                },
            )
            for step in range(1, 6):
                t = step / 5
                driver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    {
                        "type": "touchMove",
                        "touchPoints": [{
                            "x": x0 + (x1 - x0) * t,
                            "y": y0 + (y1 - y0) * t,
                            "radiusX": 4,
                            "radiusY": 4,
                            "force": 1,
                        }],
                    },
                )
                time.sleep(0.03)
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {"type": "touchEnd", "touchPoints": []},
            )
            time.sleep(0.3)
            after_particles = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            assert after_particles > before_particles, (
                label,
                f"landscape touch did not draw particles: before={before_particles}, after={after_particles}",
            )

            # Repeat portrait/landscape transitions to catch intermittent stale-viewport bugs.
            for cycle in range(2, 5):
                driver.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": 390,
                        "height": 844,
                        "deviceScaleFactor": 3.0,
                        "mobile": True,
                        "screenOrientation": {
                            "type": "portraitPrimary",
                            "angle": 0,
                        },
                    },
                )
                driver.execute_script("window.dispatchEvent(new Event('orientationchange'));")
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptOrientationBlocked === true && "
                        "window.__tptRuntimePaused === true && "
                        "window.__yandexGameplayStarted === false"
                    )
                )

                portrait_cycle = driver.execute_script(
                    """
                    const gate = document.getElementById('orientation-gate');
                    return {
                        blocked: window.__tptOrientationBlocked === true,
                        paused: window.__tptRuntimePaused === true,
                        gameplay: window.__yandexGameplayStarted,
                        gateDisplay: getComputedStyle(gate).display,
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                    };
                    """
                )
                assert portrait_cycle["blocked"] is True, (label, cycle, portrait_cycle)
                assert portrait_cycle["paused"] is True, (label, cycle, portrait_cycle)
                assert portrait_cycle["gameplay"] is False, (label, cycle, portrait_cycle)
                assert portrait_cycle["gateDisplay"] != "none", (label, cycle, portrait_cycle)

                driver.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": 844,
                        "height": 390,
                        "deviceScaleFactor": 3.0,
                        "mobile": True,
                        "screenOrientation": {
                            "type": "landscapePrimary",
                            "angle": 90,
                        },
                    },
                )
                driver.execute_script("window.dispatchEvent(new Event('orientationchange'));")
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptOrientationBlocked === false && "
                        "window.__tptRuntimePaused === false && "
                        "window.__yandexGameplayStarted === true"
                    )
                )
                time.sleep(0.2)

                landscape_cycle = driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    const r = canvas.getBoundingClientRect();
                    const app = document.getElementById('app').getBoundingClientRect();
                    return {
                        blocked: window.__tptOrientationBlocked === true,
                        paused: window.__tptRuntimePaused === true,
                        gameplay: window.__yandexGameplayStarted,
                        gateDisplay: getComputedStyle(document.getElementById('orientation-gate')).display,
                        left: r.left,
                        top: r.top,
                        right: r.right,
                        bottom: r.bottom,
                        width: r.width,
                        height: r.height,
                        appLeft: app.left,
                        appTop: app.top,
                        appRight: app.right,
                        appBottom: app.bottom,
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                    };
                    """
                )
                assert landscape_cycle["blocked"] is False, (label, cycle, landscape_cycle)
                assert landscape_cycle["paused"] is False, (label, cycle, landscape_cycle)
                assert landscape_cycle["gameplay"] is True, (label, cycle, landscape_cycle)
                assert landscape_cycle["gateDisplay"] == "none", (label, cycle, landscape_cycle)
                assert landscape_cycle["width"] > 0 and landscape_cycle["height"] > 0, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["left"] >= landscape_cycle["appLeft"] - 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["top"] >= landscape_cycle["appTop"] - 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["right"] <= landscape_cycle["appRight"] + 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["bottom"] <= landscape_cycle["appBottom"] + 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["right"] <= landscape_cycle["viewportWidth"] + 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )
                assert landscape_cycle["bottom"] <= landscape_cycle["viewportHeight"] + 1, (
                    label,
                    cycle,
                    landscape_cycle,
                )

            driver.save_screenshot(
                os.path.join(ARTIFACT_DIR, f"{label}-orientation-cycle-final.png")
            )

        driver.save_screenshot(os.path.join(ARTIFACT_DIR, f"{label}-resized.png"))

        # Yandex platform pause/resume must stop and restart the native loop.
        driver.execute_script("window.ysdk.emit('game_api_pause')")
        wait.until(lambda d: d.execute_script("return window.__tptRuntimePaused === true"))
        paused = driver.execute_script(
            "return {paused: window.__tptRuntimePaused, gameplay: window.__yandexGameplayStarted}"
        )
        assert paused["paused"] is True, (label, paused)

        driver.execute_script("window.ysdk.emit('game_api_resume')")
        wait.until(lambda d: d.execute_script("return window.__tptRuntimePaused === false"))
        resumed = driver.execute_script(
            "return {paused: window.__tptRuntimePaused, gameplay: window.__yandexGameplayStarted}"
        )
        assert resumed["paused"] is False, (label, resumed)

        # IDBFS persistence: write a marker, flush IndexedDB, reload, and read it back.
        if not mobile and language == "en":
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestStorageWrite', null, [], [])"
            )
            wait.until(
                lambda d: d.execute_script("return window.__tptStorageFlushed === true")
            )
            storage_error = driver.execute_script(
                "return window.__tptStorageFlushError || ''"
            )
            assert storage_error == "", (label, storage_error)

            driver.refresh()
            wait.until(
                lambda d: d.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    return Boolean(
                        canvas &&
                        canvas.style.display === 'block' &&
                        window.__tptGameModule &&
                        window.__yandexLoadingReady === true
                    );
                    """
                )
            )
            persisted = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestStorageRead', 'number', [], [])"
            )
            assert persisted == 1, (label, "IDBFS persistence failed")

        print(f"[smoke] {label}: OK {state}; resized={resized}; paused={paused}; resumed={resumed}")
    finally:
        driver.quit()


if __name__ == "__main__":
    # Test both platform shapes and both supported languages.
    smoke_case("en", mobile=False)
    smoke_case("ru", mobile=False)
    smoke_case("en", mobile=True)
    smoke_case("ru", mobile=True)
