#!/usr/bin/env python3
import json
import os
import statistics
import time
from urllib.parse import urlsplit

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("TPT_SMOKE_URL", "http://127.0.0.1:8765")
ARTIFACT_DIR = os.environ.get("TPT_SMOKE_ARTIFACT_DIR", "test-artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)


def assert_no_external_network(driver, label):
    base = urlsplit(BASE_URL)
    base_host = (base.hostname or "").lower()
    base_port = base.port

    seen = []
    external = []

    for entry in driver.get_log("performance"):
        try:
            message = json.loads(entry["message"])["message"]
        except (KeyError, TypeError, json.JSONDecodeError):
            continue

        method = message.get("method")
        params = message.get("params") or {}
        url = None
        kind = method

        if method == "Network.requestWillBeSent":
            url = (params.get("request") or {}).get("url")
        elif method == "Network.webSocketCreated":
            url = params.get("url")
        elif method == "Network.webTransportCreated":
            url = params.get("url")

        if not url:
            continue

        try:
            parsed = urlsplit(url)
        except ValueError:
            continue

        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https", "ws", "wss"}:
            continue

        record = {"kind": kind, "url": url}
        seen.append(record)

        host = (parsed.hostname or "").lower()
        port = parsed.port
        if host != base_host or port != base_port:
            external.append(record)

    report_path = os.path.join(ARTIFACT_DIR, f"{label}-network.json")
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(
            {"base_url": BASE_URL, "events": seen, "external": external},
            handle,
            ensure_ascii=False,
            indent=2,
        )

    assert not external, (
        label,
        "external HTTP/WebSocket/WebTransport traffic detected",
        external,
    )

    return seen


def measure_animation_frames(driver, sample_count=90):
    driver.set_script_timeout(30)
    return driver.execute_async_script(
        """
        const sampleCount = arguments[0];
        const done = arguments[arguments.length - 1];
        const samples = [];
        let previous = null;

        function frame(now) {
            if (previous !== null) {
                samples.push(now - previous);
            }
            previous = now;
            if (samples.length >= sampleCount) {
                done(samples);
                return;
            }
            requestAnimationFrame(frame);
        }

        requestAnimationFrame(frame);
        """,
        sample_count,
    )


def record_performance_metric(driver, label, scene, hook, target_particles):
    actual_particles = driver.execute_script(
        "return window.__tptGameModule.ccall("
        "arguments[0], 'number', ['number'], [arguments[1]])",
        hook,
        target_particles,
    )
    assert actual_particles >= target_particles, (
        label,
        scene,
        f"stress scene did not reach target particles: {actual_particles}",
    )

    # Let the simulation settle before sampling browser frame intervals.
    time.sleep(0.5)
    samples = [float(value) for value in measure_animation_frames(driver, 90)]
    ordered = sorted(samples)
    median_ms = statistics.median(ordered)
    p95_ms = ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))]
    average_ms = statistics.fmean(ordered)
    engine_fps = float(
        driver.execute_script(
            "return window.__tptGameModule.ccall('YandexWeb_TestEngineFps', 'number', [], [])"
        )
    )

    metric = {
        "label": label,
        "scene": scene,
        "particles": int(actual_particles),
        "samples": len(samples),
        "average_frame_ms": round(average_ms, 3),
        "median_frame_ms": round(median_ms, 3),
        "p95_frame_ms": round(p95_ms, 3),
        "median_fps": round(1000.0 / median_ms, 2) if median_ms > 0 else None,
        "engine_fps": round(engine_fps, 2),
    }

    # Keep this deliberately loose: GitHub runners are noisy and these are
    # regression guards, not device certification targets. The current heavy
    # scenes run at ~59-60 engine FPS with ~16.7 ms p95 on the CI runner.
    assert engine_fps >= 30.0, (
        label,
        scene,
        f"catastrophic engine FPS regression: {engine_fps:.2f}",
        metric,
    )
    assert p95_ms <= 50.0, (
        label,
        scene,
        f"catastrophic frame-time regression: p95={p95_ms:.2f} ms",
        metric,
    )

    report_path = os.path.join(ARTIFACT_DIR, "performance.json")
    report = []
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as handle:
            report = json.load(handle)
    report.append(metric)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    print(f"[performance] {metric}")
    return metric


def make_driver(
    mobile: bool,
    browser_language: str | None = None,
    page_load_strategy: str = "normal",
):
    options = Options()
    options.page_load_strategy = page_load_strategy
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,768")
    options.set_capability(
        "goog:loggingPrefs",
        {"browser": "ALL", "performance": "ALL"},
    )
    if browser_language:
        options.add_argument(f"--lang={browser_language}")
        options.add_experimental_option(
            "prefs",
            {"intl.accept_languages": f"{browser_language},ru,en"},
        )
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
        device_type = "mobile" if mobile else "desktop"
        driver.get(f"{BASE_URL}/?lang={language}&device={device_type}")

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

        sdk_mobile_platform = driver.execute_script(
            "return window.__tptSdkMobilePlatform"
        )
        assert sdk_mobile_platform is mobile, (
            label,
            "Yandex deviceInfo classification mismatch",
            sdk_mobile_platform,
        )

        ready_state = driver.execute_script(
            """
            const events = window.__yandexSdkEvents || [];
            return {
                ready: window.__yandexLoadingReady === true,
                readyCount: window.__yandexReadyCount || 0,
                snapshot: window.__yandexReadySnapshot,
                events,
                readyIndex: events.indexOf('ready'),
                gameplayStartIndex: events.indexOf('gameplay-start'),
            };
            """
        )
        assert ready_state["ready"] is True, (label, ready_state)
        assert ready_state["readyCount"] == 1, (
            label,
            "LoadingAPI.ready must be called exactly once",
            ready_state,
        )
        assert ready_state["snapshot"]["loaderHidden"] is True, (
            label,
            "LoadingAPI.ready fired before loader was hidden",
            ready_state,
        )
        assert ready_state["snapshot"]["canvasDisplay"] == "block", (
            label,
            "LoadingAPI.ready fired before canvas became visible",
            ready_state,
        )
        assert ready_state["snapshot"]["ariaBusy"] == "false", (
            label,
            "LoadingAPI.ready fired while app was still busy",
            ready_state,
        )
        assert ready_state["readyIndex"] >= 0, (label, ready_state)
        if mobile:
            assert (
                ready_state["gameplayStartIndex"] == -1
                or ready_state["gameplayStartIndex"] > ready_state["readyIndex"]
            ), (
                label,
                "GameplayAPI.start fired before LoadingAPI.ready",
                ready_state,
            )
        else:
            assert ready_state["gameplayStartIndex"] > ready_state["readyIndex"], (
                label,
                "GameplayAPI.start did not follow LoadingAPI.ready",
                ready_state,
            )

        interaction_guards = driver.execute_script(
            """
            const app = document.getElementById('app');
            const canvas = document.getElementById('canvas');
            const bodyStyle = getComputedStyle(document.body);
            const canvasStyle = getComputedStyle(canvas);
            const canvasContextEvent = new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                clientX: 20,
                clientY: 20,
            });
            const appContextEvent = new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                clientX: 2,
                clientY: 2,
            });
            const canvasDispatchResult = canvas.dispatchEvent(canvasContextEvent);
            const appDispatchResult = app.dispatchEvent(appContextEvent);
            return {
                canvasContextPrevented:
                    canvasContextEvent.defaultPrevented === true &&
                    canvasDispatchResult === false,
                appContextPrevented:
                    appContextEvent.defaultPrevented === true &&
                    appDispatchResult === false,
                bodyUserSelect: bodyStyle.userSelect,
                bodyOverscrollBehavior: bodyStyle.overscrollBehavior,
                canvasTouchAction: canvasStyle.touchAction,
                scrollWidth: document.documentElement.scrollWidth,
                scrollHeight: document.documentElement.scrollHeight,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
            };
            """
        )
        assert interaction_guards["canvasContextPrevented"] is True, (
            label,
            "canvas context menu was not prevented",
            interaction_guards,
        )
        assert interaction_guards["appContextPrevented"] is True, (
            label,
            "game-area context menu was not prevented",
            interaction_guards,
        )
        assert interaction_guards["bodyUserSelect"] == "none", (
            label,
            "browser text selection is enabled",
            interaction_guards,
        )
        assert interaction_guards["bodyOverscrollBehavior"] == "none", (
            label,
            "browser overscroll/swipe-to-refresh is enabled",
            interaction_guards,
        )
        assert interaction_guards["canvasTouchAction"] == "none", (
            label,
            "canvas browser gestures are enabled",
            interaction_guards,
        )
        assert interaction_guards["scrollWidth"] <= interaction_guards["viewportWidth"] + 1, (
            label,
            "horizontal browser scrolling is possible",
            interaction_guards,
        )
        assert interaction_guards["scrollHeight"] <= interaction_guards["viewportHeight"] + 1, (
            label,
            "vertical browser scrolling is possible",
            interaction_guards,
        )

        if not mobile:
            # Browser zoom changes the effective CSS viewport rather than
            # applying CSS zoom to the root document. Emulate the 80%-125%
            # moderation range by resizing to the corresponding CSS-pixel
            # viewport, then verify the page and canvas still fit without
            # system scrollbars.
            base_width = 1365
            base_height = 768
            for zoom in (0.8, 1.0, 1.25):
                effective_width = round(base_width / zoom)
                effective_height = round(base_height / zoom)
                driver.set_window_size(effective_width, effective_height)
                wait.until(
                    lambda d: d.execute_script(
                        """
                        const canvas = document.getElementById('canvas');
                        const rect = canvas.getBoundingClientRect();
                        return (
                            rect.width > 0 &&
                            rect.height > 0 &&
                            rect.right <= window.innerWidth + 1 &&
                            rect.bottom <= window.innerHeight + 1
                        );
                        """
                    )
                )
                zoom_state = driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    const rect = canvas.getBoundingClientRect();
                    return {
                        scrollWidth: document.documentElement.scrollWidth,
                        scrollHeight: document.documentElement.scrollHeight,
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        canvasLeft: rect.left,
                        canvasTop: rect.top,
                        canvasRight: rect.right,
                        canvasBottom: rect.bottom,
                    };
                    """
                )
                assert zoom_state["scrollWidth"] <= zoom_state["viewportWidth"] + 1, (
                    label,
                    f"horizontal scroll at browser zoom {zoom}",
                    zoom_state,
                )
                assert zoom_state["scrollHeight"] <= zoom_state["viewportHeight"] + 1, (
                    label,
                    f"vertical scroll at browser zoom {zoom}",
                    zoom_state,
                )
                assert zoom_state["canvasLeft"] >= -1 and zoom_state["canvasTop"] >= -1, (
                    label,
                    f"canvas starts outside viewport at browser zoom {zoom}",
                    zoom_state,
                )
                assert zoom_state["canvasRight"] <= zoom_state["viewportWidth"] + 1, (
                    label,
                    f"canvas exceeds viewport width at browser zoom {zoom}",
                    zoom_state,
                )
                assert zoom_state["canvasBottom"] <= zoom_state["viewportHeight"] + 1, (
                    label,
                    f"canvas exceeds viewport height at browser zoom {zoom}",
                    zoom_state,
                )

            driver.set_window_size(base_width, base_height)
            time.sleep(0.1)

        external_resources = driver.execute_script(
            """
            const origin = location.origin;
            return performance.getEntriesByType('resource')
                .map(entry => entry.name)
                .filter(name => {
                    try {
                        const url = new URL(name, location.href);
                        return (url.protocol === 'http:' || url.protocol === 'https:') &&
                               url.origin !== origin;
                    } catch {
                        return false;
                    }
                });
            """
        )
        assert external_resources == [], (
            label,
            "external runtime resources detected",
            external_resources,
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
                sdkScriptPresent: Boolean(document.getElementById('yandex-games-sdk')),
                sdkScriptAsync: document.getElementById('yandex-games-sdk')?.async === true,
                sdkScriptPath: document.getElementById('yandex-games-sdk')?.getAttribute('src') || '',
                imageRendering: getComputedStyle(canvas).imageRendering,
                canvasFit: window.__tptCanvasFit,
            };
            """
        )

        assert state["language"] == language, (label, state)
        assert state["fatalHidden"] is True, (label, state)
        assert state["loaderHidden"] is True, (label, state)
        assert state["loaderDisplay"] == "none", (label, state)
        assert state["canvasDisplay"] == "block", (label, state)
        assert state["canvasWidth"] > 0 and state["canvasHeight"] > 0, (label, state)
        assert state["canvasWidth"] >= state["viewportWidth"] - 8, (
            label,
            "canvas does not fill available width",
            state,
        )
        assert state["canvasHeight"] >= state["viewportHeight"] - 8, (
            label,
            "canvas does not fill available height",
            state,
        )
        assert state["canvasWidth"] <= state["viewportWidth"] + 1, (label, state)
        assert state["canvasHeight"] <= state["viewportHeight"] + 1, (label, state)
        if state["canvasFit"] and state["canvasFit"]["crispUpscale"]:
            assert state["imageRendering"] in ("pixelated", "crisp-edges"), (
                label,
                "upscaled canvas is being browser-smoothed",
                state,
            )
        assert state["ready"] is True, (label, state)
        assert state["sdkScriptPresent"] is True, (label, state)
        assert state["sdkScriptAsync"] is True, (label, state)
        assert state["sdkScriptPath"] == "/sdk.js", (label, state)

        lua_network_mask = int(
            driver.execute_script(
                """
                return window.__tptGameModule.ccall(
                    'YandexWeb_TestLuaNetworkApiMask',
                    'number',
                    [],
                    []
                );
                """
            )
        )
        assert lua_network_mask == 0, (
            label,
            "network/navigation Lua API survived in runtime",
            lua_network_mask,
        )

        server_control_mask = int(
            driver.execute_script(
                """
                return window.__tptGameModule.ccall(
                    'YandexWeb_TestServerControlsVisibleMask',
                    'number',
                    [],
                    []
                );
                """
            )
        )
        assert server_control_mask == 0, (
            label,
            "upstream server/account control is visible",
            server_control_mask,
        )

        native_fullscreen = driver.execute_script(
            """
            const before = Boolean(document.fullscreenElement);
            const native = window.__tptGameModule.ccall(
                'YandexWeb_TestNativeFullscreenRequest',
                'number',
                [],
                []
            );
            return {
                native,
                before,
                after: Boolean(document.fullscreenElement),
            };
            """
        )
        assert native_fullscreen["native"] == 0, (
            label,
            "native TPT fullscreen flag changed in embedded Web build",
            native_fullscreen,
        )
        assert native_fullscreen["before"] == native_fullscreen["after"], (
            label,
            "native TPT fullscreen request changed browser fullscreen state",
            native_fullscreen,
        )

        if not mobile and language == "en":
            locale_aliases = driver.execute_async_script(
                """
                const done = arguments[arguments.length - 1];
                import('./src/yandex.js').then((module) => {
                    const result = {};
                    for (const lang of ['ru', 'be', 'kk', 'uk', 'uz', 'de', 'tr']) {
                        result[lang] = module.getYandexLanguage({
                            environment: {i18n: {lang}}
                        });
                    }
                    done(result);
                }).catch((error) => done({error: String(error)}));
                """
            )
            assert "error" not in locale_aliases, (label, locale_aliases)
            assert locale_aliases["ru"] == "ru", (label, "ru", locale_aliases)
            for alias in ["be", "kk", "uk", "uz", "de", "tr"]:
                assert locale_aliases[alias] == "en", (label, alias, locale_aliases)

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
            # Cover compact-phone and tablet landscape viewports in the
            # same mobile session without multiplying full browser instances.
            for viewport_name, vw, vh, dpr in (
                ("compact", 568, 320, 2.0),
                ("tablet", 1024, 768, 2.0),
                ("baseline", 844, 390, 3.0),
            ):
                driver.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": vw,
                        "height": vh,
                        "deviceScaleFactor": dpr,
                        "mobile": True,
                        "screenOrientation": {
                            "type": "landscapePrimary",
                            "angle": 90,
                        },
                    },
                )
                driver.execute_script(
                    "window.dispatchEvent(new Event('resize'));"
                    "window.dispatchEvent(new Event('orientationchange'));"
                )
                wait.until(
                    lambda d: d.execute_script(
                        """
                        const canvas = document.getElementById('canvas');
                        const r = canvas.getBoundingClientRect();
                        return (
                            window.__tptOrientationBlocked === false &&
                            window.__tptRuntimePaused === false &&
                            window.__yandexGameplayStarted === true &&
                            r.width > 0 &&
                            r.height > 0 &&
                            r.right <= window.innerWidth + 1 &&
                            r.bottom <= window.innerHeight + 1
                        );
                        """
                    )
                )
                viewport_state = driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    const r = canvas.getBoundingClientRect();
                    return {
                        width: r.width,
                        height: r.height,
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        scrollWidth: document.documentElement.scrollWidth,
                        scrollHeight: document.documentElement.scrollHeight,
                        blocked: window.__tptOrientationBlocked,
                        paused: window.__tptRuntimePaused,
                        gameplay: window.__yandexGameplayStarted,
                    };
                    """
                )
                assert viewport_state["scrollWidth"] <= viewport_state["viewportWidth"] + 1, (
                    label,
                    viewport_name,
                    "horizontal mobile scroll",
                    viewport_state,
                )
                assert viewport_state["scrollHeight"] <= viewport_state["viewportHeight"] + 1, (
                    label,
                    viewport_name,
                    "vertical mobile scroll",
                    viewport_state,
                )

            mobile_ready_order = driver.execute_script(
                """
                const events = window.__yandexSdkEvents || [];
                return {
                    readyCount: window.__yandexReadyCount || 0,
                    events,
                    readyIndex: events.indexOf('ready'),
                    gameplayStartIndex: events.indexOf('gameplay-start'),
                };
                """
            )
            assert mobile_ready_order["readyCount"] == 1, (
                label,
                mobile_ready_order,
            )
            assert (
                mobile_ready_order["readyIndex"] >= 0
                and mobile_ready_order["gameplayStartIndex"]
                    > mobile_ready_order["readyIndex"]
            ), (
                label,
                "mobile GameplayAPI.start did not follow Game Ready after landscape resume",
                mobile_ready_order,
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
        assert resized["width"] >= resized["viewportWidth"] - 8, (
            label,
            "resized canvas does not fill available width",
            resized,
        )
        assert resized["height"] >= resized["viewportHeight"] - 8, (
            label,
            "resized canvas does not fill available height",
            resized,
        )
        assert resized["orientationBlocked"] is False, (label, resized)
        assert resized["orientationDisplay"] == "none", (label, resized)
        assert resized["gameplay"] is True, (label, resized)

        if not mobile and language == "ru":
            driver.execute_script("void window.__tptTriggerAdForTest()")
            wait.until(
                lambda d: d.execute_script(
                    """
                    const warning = document.getElementById('ad-warning');
                    return (
                        window.__tptAdWarningActive === true &&
                        warning &&
                        warning.hidden === false &&
                        window.__tptRuntimePaused === true &&
                        window.__yandexGameplayStarted === false
                    );
                    """
                )
            )
            warning_state = driver.execute_script(
                """
                return {
                    title: document.getElementById('ad-warning-title').textContent,
                    message: document.getElementById('ad-warning-message').textContent,
                    countdown: document.getElementById('ad-warning-countdown').textContent,
                };
                """
            )
            assert warning_state["title"] == "Реклама через", (label, warning_state)
            assert warning_state["message"] == "Игра поставлена на паузу.", (
                label,
                warning_state,
            )
            wait.until(
                lambda d: d.execute_script(
                    """
                    return (
                        window.__yandexAdOpenCount === 1 &&
                        window.__yandexAdCloseCount === 1 &&
                        window.__tptAdCycleActive === false &&
                        window.__tptRuntimePaused === false &&
                        window.__yandexGameplayStarted === true &&
                        document.getElementById('ad-warning').hidden === true
                    );
                    """
                )
            )

        if not mobile:
            # Prove desktop mouse input can select a real UI element and draw.
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestSelectWater', null, [], [])"
            )
            desktop_before_tap = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestActiveToolIsDust', 'number', [], [])"
            )
            assert desktop_before_tap == 0, (label, "failed to switch away from DUST before mouse UI test")

            wait.until(
                lambda d: d.execute_script(
                    """
                    const m = window.__tptGameModule;
                    if (!m) return false;
                    const w = m.ccall('YandexWeb_TestGetUiWidth', 'number', [], []);
                    const h = m.ccall('YandexWeb_TestGetUiHeight', 'number', [], []);
                    const x = m.ccall('YandexWeb_TestGetDustButtonX', 'number', [], []);
                    const y = m.ccall('YandexWeb_TestGetDustButtonY', 'number', [], []);
                    return w > 0 && h > 0 && x >= 0 && y >= 0;
                    """
                )
            )
            dust_button = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                const m = window.__tptGameModule;
                const nativeX = m.ccall('YandexWeb_TestGetDustButtonX', 'number', [], []);
                const nativeY = m.ccall('YandexWeb_TestGetDustButtonY', 'number', [], []);
                const windowX = m.ccall(
                    'YandexWeb_TestLogicalToWindowX',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowY = m.ccall(
                    'YandexWeb_TestLogicalToWindowY',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowWidth = m.ccall('YandexWeb_TestWindowWidth', 'number', [], []);
                const windowHeight = m.ccall('YandexWeb_TestWindowHeight', 'number', [], []);
                return {
                    x: r.left + (windowX / windowWidth) * r.width,
                    y: r.top + (windowY / windowHeight) * r.height,
                    nativeX,
                    nativeY,
                    windowX,
                    windowY,
                    windowWidth,
                    windowHeight,
                };
                """
            )
            driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mousePressed",
                    "x": dust_button["x"],
                    "y": dust_button["y"],
                    "button": "left",
                    "buttons": 1,
                    "clickCount": 1,
                },
            )
            driver.execute_cdp_cmd(
                "Input.dispatchMouseEvent",
                {
                    "type": "mouseReleased",
                    "x": dust_button["x"],
                    "y": dust_button["y"],
                    "button": "left",
                    "buttons": 0,
                    "clickCount": 1,
                },
            )
            time.sleep(0.15)
            desktop_after_tap = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestActiveToolIsDust', 'number', [], [])"
            )
            assert desktop_after_tap == 1, (
                label,
                f"clicking visible DUST button did not select DUST: point={dust_button}",
            )

            desktop_before_particles = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            draw_rect = driver.execute_script(
                """
                const r = document.getElementById('canvas').getBoundingClientRect();
                return {left:r.left, top:r.top, width:r.width, height:r.height};
                """
            )
            mx0 = draw_rect["left"] + draw_rect["width"] * 0.24
            my0 = draw_rect["top"] + draw_rect["height"] * 0.30
            mx1 = draw_rect["left"] + draw_rect["width"] * 0.42
            my1 = draw_rect["top"] + draw_rect["height"] * 0.40

            canvas_element = driver.find_element(By.ID, "canvas")
            start_offset_x = int(draw_rect["width"] * (0.24 - 0.50))
            start_offset_y = int(draw_rect["height"] * (0.30 - 0.50))
            move_offset_x = int(draw_rect["width"] * (0.42 - 0.24))
            move_offset_y = int(draw_rect["height"] * (0.40 - 0.30))
            (
                ActionChains(driver)
                .move_to_element_with_offset(
                    canvas_element,
                    start_offset_x,
                    start_offset_y,
                )
                .click_and_hold()
                .pause(0.05)
                .move_by_offset(move_offset_x, move_offset_y)
                .pause(0.05)
                .release()
                .perform()
            )
            time.sleep(0.2)
            desktop_after_particles = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            assert desktop_after_particles > desktop_before_particles, (
                label,
                f"desktop mouse drag did not draw particles: before={desktop_before_particles}, after={desktop_after_particles}",
            )

        if mobile:
            # Prove a real touch on the visible DUST button changes the active tool.
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestSelectWater', null, [], [])"
            )
            active_before_tap = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestActiveToolIsDust', 'number', [], [])"
            )
            assert active_before_tap == 0, (label, "failed to switch away from DUST before UI tap")

            wait.until(
                lambda d: d.execute_script(
                    """
                    const m = window.__tptGameModule;
                    if (!m) return false;
                    const w = m.ccall('YandexWeb_TestGetUiWidth', 'number', [], []);
                    const h = m.ccall('YandexWeb_TestGetUiHeight', 'number', [], []);
                    const x = m.ccall('YandexWeb_TestGetDustButtonX', 'number', [], []);
                    const y = m.ccall('YandexWeb_TestGetDustButtonY', 'number', [], []);
                    return w > 0 && h > 0 && x >= 0 && y >= 0;
                    """
                )
            )
            dust_button = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                const m = window.__tptGameModule;
                const nativeX = m.ccall('YandexWeb_TestGetDustButtonX', 'number', [], []);
                const nativeY = m.ccall('YandexWeb_TestGetDustButtonY', 'number', [], []);
                const windowX = m.ccall(
                    'YandexWeb_TestLogicalToWindowX',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowY = m.ccall(
                    'YandexWeb_TestLogicalToWindowY',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowWidth = m.ccall('YandexWeb_TestWindowWidth', 'number', [], []);
                const windowHeight = m.ccall('YandexWeb_TestWindowHeight', 'number', [], []);
                return {
                    x: r.left + (windowX / windowWidth) * r.width,
                    y: r.top + (windowY / windowHeight) * r.height,
                    nativeX,
                    nativeY,
                    windowX,
                    windowY,
                    windowWidth,
                    windowHeight,
                };
                """
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [{
                        "x": dust_button["x"],
                        "y": dust_button["y"],
                        "radiusX": 4,
                        "radiusY": 4,
                        "force": 1,
                    }],
                },
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {"type": "touchEnd", "touchPoints": []},
            )
            time.sleep(0.2)
            active_after_tap = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestActiveToolIsDust', 'number', [], [])"
            )
            assert active_after_tap == 1, (
                label,
                f"expanded touch target did not select DUST: point={dust_button}",
            )

            # Prove touch still maps into the simulation after portrait -> landscape.
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

            # Combine orientation blocking with page visibility. A user may
            # rotate to portrait, background the browser, rotate back while
            # hidden, then return. The native loop must remain paused until the
            # page is visible again and must not get stuck afterwards.
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

            driver.execute_script(
                """
                window.__tptSyntheticHidden = true;
                Object.defineProperty(document, 'hidden', {
                    configurable: true,
                    get() { return window.__tptSyntheticHidden; }
                });
                document.dispatchEvent(new Event('visibilitychange'));
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    "return document.hidden === true && "
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

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
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            driver.execute_script(
                """
                window.__tptSyntheticHidden = false;
                document.dispatchEvent(new Event('visibilitychange'));
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    "return document.hidden === false && "
                    "window.__tptOrientationBlocked === false && "
                    "window.__tptRuntimePaused === false && "
                    "window.__yandexGameplayStarted === true"
                )
            )
            visibility_orientation_state = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const rect = canvas.getBoundingClientRect();
                return {
                    hidden: document.hidden,
                    blocked: window.__tptOrientationBlocked,
                    paused: window.__tptRuntimePaused,
                    gameplay: window.__yandexGameplayStarted,
                    width: rect.width,
                    height: rect.height,
                };
                """
            )
            assert visibility_orientation_state["hidden"] is False, (
                label,
                visibility_orientation_state,
            )
            assert visibility_orientation_state["blocked"] is False, (
                label,
                visibility_orientation_state,
            )
            assert visibility_orientation_state["paused"] is False, (
                label,
                visibility_orientation_state,
            )
            assert visibility_orientation_state["gameplay"] is True, (
                label,
                visibility_orientation_state,
            )
            assert visibility_orientation_state["width"] > 0, (
                label,
                visibility_orientation_state,
            )
            assert visibility_orientation_state["height"] > 0, (
                label,
                visibility_orientation_state,
            )
            driver.execute_script(
                """
                delete document.hidden;
                delete window.__tptSyntheticHidden;
                """
            )

            # A local blocker can clear while Yandex keeps the game paused.
            # Because Yandex will not auto-start markup that was explicitly
            # stopped before game_api_pause, our resume handler must reconcile
            # the gameplay state once both blockers are gone.
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
            driver.execute_script("window.ysdk.emit('game_api_pause')")
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

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
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            driver.execute_script("window.ysdk.emit('game_api_resume')")
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptOrientationBlocked === false && "
                    "window.__tptRuntimePaused === false && "
                    "window.__yandexGameplayStarted === true"
                )
            )
            platform_resume_reconciled = driver.execute_script(
                """
                return {
                    blocked: window.__tptOrientationBlocked,
                    paused: window.__tptRuntimePaused,
                    gameplay: window.__yandexGameplayStarted,
                };
                """
            )
            assert platform_resume_reconciled["blocked"] is False, (
                label,
                platform_resume_reconciled,
            )
            assert platform_resume_reconciled["paused"] is False, (
                label,
                platform_resume_reconciled,
            )
            assert platform_resume_reconciled["gameplay"] is True, (
                label,
                platform_resume_reconciled,
            )

            # Touch must still work after several orientation transitions.
            post_cycle_before = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            cycle_rect = driver.execute_script(
                """
                const r = document.getElementById('canvas').getBoundingClientRect();
                return {left:r.left, top:r.top, width:r.width, height:r.height};
                """
            )
            cx0 = cycle_rect["left"] + cycle_rect["width"] * 0.58
            cy0 = cycle_rect["top"] + cycle_rect["height"] * 0.34
            cx1 = cycle_rect["left"] + cycle_rect["width"] * 0.70
            cy1 = cycle_rect["top"] + cycle_rect["height"] * 0.44
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [{"x": cx0, "y": cy0, "radiusX": 4, "radiusY": 4, "force": 1}],
                },
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchMove",
                    "touchPoints": [{"x": cx1, "y": cy1, "radiusX": 4, "radiusY": 4, "force": 1}],
                },
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {"type": "touchEnd", "touchPoints": []},
            )
            time.sleep(0.25)
            post_cycle_after = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
            )
            assert post_cycle_after > post_cycle_before, (
                label,
                f"touch stopped working after orientation cycles: before={post_cycle_before}, after={post_cycle_after}",
            )

            driver.save_screenshot(
                os.path.join(ARTIFACT_DIR, f"{label}-orientation-cycle-final.png")
            )

            # Stress repeated fullscreen-like viewport changes. The wrapper owns
            # fullscreen sizing for Emscripten, so canvas CSS size must be
            # recalculated from the *current* app viewport on every event.
            fullscreen_sizes = [
                (915, 412),
                (780, 360),
                (844, 390),
                (915, 412),
                (844, 390),
            ]
            for fullscreen_cycle, (fw, fh) in enumerate(fullscreen_sizes, start=1):
                driver.execute_cdp_cmd(
                    "Emulation.setDeviceMetricsOverride",
                    {
                        "width": fw,
                        "height": fh,
                        "deviceScaleFactor": 3.0,
                        "mobile": True,
                        "screenOrientation": {
                            "type": "landscapePrimary",
                            "angle": 90,
                        },
                    },
                )
                driver.execute_script(
                    "document.dispatchEvent(new Event('fullscreenchange'));"
                )
                time.sleep(0.25)
                fullscreen_state = driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    const app = document.getElementById('app');
                    const r = canvas.getBoundingClientRect();
                    const logicalWidth = canvas.width || 612;
                    const logicalHeight = canvas.height || 384;
                    const style = getComputedStyle(app);
                    const contentWidth = Math.max(
                        0,
                        app.clientWidth
                            - parseFloat(style.paddingLeft)
                            - parseFloat(style.paddingRight)
                    );
                    const contentHeight = Math.max(
                        0,
                        app.clientHeight
                            - parseFloat(style.paddingTop)
                            - parseFloat(style.paddingBottom)
                    );
                    const expectedScale = Math.min(
                        contentWidth / logicalWidth,
                        contentHeight / logicalHeight
                    );
                    return {
                        width: r.width,
                        height: r.height,
                        expectedWidth: Math.max(1, Math.floor(logicalWidth * expectedScale)),
                        expectedHeight: Math.max(1, Math.floor(logicalHeight * expectedScale)),
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        appWidth: app.clientWidth,
                        appHeight: app.clientHeight,
                        blocked: window.__tptOrientationBlocked === true,
                        gameplay: window.__yandexGameplayStarted,
                        paused: window.__tptRuntimePaused === true,
                    };
                    """
                )
                assert fullscreen_state["blocked"] is False, (
                    label,
                    fullscreen_cycle,
                    fullscreen_state,
                )
                assert fullscreen_state["gameplay"] is True, (
                    label,
                    fullscreen_cycle,
                    fullscreen_state,
                )
                assert fullscreen_state["paused"] is False, (
                    label,
                    fullscreen_cycle,
                    fullscreen_state,
                )
                # Full-slot Yandex mode intentionally stretches the native
                # framebuffer to the available player area instead of keeping
                # the old aspect-fit/letterbox dimensions.
                assert fullscreen_state["width"] >= fullscreen_state["appWidth"] - 8, (
                    label,
                    fullscreen_cycle,
                    "fullscreen-cycle canvas does not fill available width",
                    fullscreen_state,
                )
                assert fullscreen_state["height"] >= fullscreen_state["appHeight"] - 8, (
                    label,
                    fullscreen_cycle,
                    "fullscreen-cycle canvas does not fill available height",
                    fullscreen_state,
                )
                assert fullscreen_state["width"] <= fullscreen_state["appWidth"] + 1, (
                    label,
                    fullscreen_cycle,
                    fullscreen_state,
                )
                assert fullscreen_state["height"] <= fullscreen_state["appHeight"] + 1, (
                    label,
                    fullscreen_cycle,
                    fullscreen_state,
                )

            driver.save_screenshot(
                os.path.join(ARTIFACT_DIR, f"{label}-fullscreen-cycle-final.png")
            )

        # Validate the real Save primary action geometry, then prove the
        # native local-save workflow opens correctly. Browser input itself is
        # already exercised above through real DUST selection and drawing.
        save_geometry = driver.execute_script(
            """
            const m = window.__tptGameModule;
            return {
                uiWidth: m.ccall('YandexWeb_TestGetUiWidth', 'number', [], []),
                uiHeight: m.ccall('YandexWeb_TestGetUiHeight', 'number', [], []),
                x: m.ccall('YandexWeb_TestGetSaveButtonX', 'number', [], []),
                y: m.ccall('YandexWeb_TestGetSaveButtonY', 'number', [], []),
            };
            """
        )
        assert save_geometry["uiWidth"] > 0 and save_geometry["uiHeight"] > 0, (
            label,
            save_geometry,
        )
        assert 0 <= save_geometry["x"] < save_geometry["uiWidth"], (
            label,
            save_geometry,
        )
        assert 0 <= save_geometry["y"] < save_geometry["uiHeight"], (
            label,
            save_geometry,
        )

        driver.execute_script(
            "window.__tptGameModule.ccall('YandexWeb_TestOpenLocalSave', null, [], [])"
        )
        wait.until(
            lambda d: d.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], []) === 1"
            )
        )
        save_open = driver.execute_script(
            "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], [])"
        )
        assert save_open == 1, (label, "native local-save workflow did not open")

        wait.until(
            lambda d: d.execute_script(
                "return window.__tptNativeModalBlocked === true && "
                "window.__yandexGameplayStarted === false"
            )
        )
        save_modal_state = driver.execute_script(
            "return {blocked: window.__tptNativeModalBlocked, gameplay: window.__yandexGameplayStarted};"
        )
        assert save_modal_state["blocked"] is True, (label, save_modal_state)
        assert save_modal_state["gameplay"] is False, (label, save_modal_state)

        # EN performs the full native local-save path on desktop and mobile.
        # RU mobile additionally proves that the DOM/SDL bridge accepts
        # Cyrillic text, Backspace editing, and a UTF-8 filename end-to-end.
        full_save_test = language == "en" or (mobile and language == "ru")
        if full_save_test:
            save_name = "yandex-ci-save" if language == "en" else "яндекс-тест"
            driver.execute_script(
                """
                window.__tptGameModule.ccall(
                    'YandexWeb_TestRemoveLocalSaveFile',
                    null,
                    ['string'],
                    [arguments[0]]
                )
                """,
                save_name,
            )

            if mobile:
                wait.until(
                    lambda d: d.execute_script(
                        """
                        const input = document.getElementById('mobile-text-input');
                        const rect = window.__tptMobileTextInputRect;
                        return Boolean(
                            window.__tptMobileTextInputActive === true &&
                            input && !input.hidden &&
                            rect && rect.width > 0 && rect.height > 0
                        );
                        """
                    )
                )
                bridge_state = driver.execute_script(
                    """
                    const input = document.getElementById('mobile-text-input');
                    return {
                        active: window.__tptMobileTextInputActive,
                        focused: window.__tptMobileTextInputFocused,
                        hidden: input.hidden,
                        rect: window.__tptMobileTextInputRect,
                    };
                    """
                )
                assert bridge_state["active"] is True, (label, bridge_state)
                assert bridge_state["focused"] is True, (label, bridge_state)
                assert bridge_state["hidden"] is False, (label, bridge_state)

                # Rotate while the native textbox is active. Portrait should
                # dismiss the browser input; landscape must restore focus.
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
                        """
                        return window.__tptOrientationBlocked === true &&
                               window.__tptMobileTextInputActive === true &&
                               window.__tptMobileTextInputFocused === false &&
                               window.__tptGameModule.ccall(
                                   'YandexWeb_TestLocalSaveOpen', 'number', [], []
                               ) === 1;
                        """
                    )
                )

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
                        """
                        return window.__tptOrientationBlocked === false &&
                               window.__tptMobileTextInputActive === true &&
                               window.__tptMobileTextInputFocused === true &&
                               window.__tptGameModule.ccall(
                                   'YandexWeb_TestLocalSaveOpen', 'number', [], []
                               ) === 1;
                        """
                    )
                )

                mobile_input = driver.find_element(By.ID, "mobile-text-input")
                if language == "ru":
                    first_character = save_name[0]
                    driver.execute_script(
                        """
                        const input = document.getElementById('mobile-text-input');
                        const value = arguments[0];
                        input.dispatchEvent(new CompositionEvent(
                            'compositionstart',
                            { bubbles: true, data: '' }
                        ));
                        input.value = value;
                        input.dispatchEvent(new InputEvent(
                            'input',
                            {
                                bubbles: true,
                                data: value,
                                inputType: 'insertCompositionText',
                                isComposing: true,
                            }
                        ));
                        input.dispatchEvent(new CompositionEvent(
                            'compositionend',
                            { bubbles: true, data: value }
                        ));
                        input.dispatchEvent(new InputEvent(
                            'input',
                            {
                                bubbles: true,
                                data: value,
                                inputType: 'insertText',
                                isComposing: false,
                            }
                        ));
                        """,
                        first_character,
                    )
                    wait.until(
                        lambda d: d.execute_script(
                            """
                            const m = window.__tptGameModule;
                            m.ccall(
                                'YandexWeb_TestCaptureLocalSaveFilename',
                                null,
                                [],
                                []
                            );
                            return window.__tptTestLocalSaveFilename === arguments[0];
                            """,
                            first_character,
                        )
                    )
                    mobile_input.send_keys(save_name[1:] + "x")
                    mobile_input.send_keys(Keys.BACKSPACE)
                    wait.until(
                        lambda d: d.execute_script(
                            """
                            const m = window.__tptGameModule;
                            m.ccall(
                                'YandexWeb_TestCaptureLocalSaveFilename',
                                null,
                                [],
                                []
                            );
                            return window.__tptTestLocalSaveFilename === arguments[0];
                            """,
                            save_name,
                        )
                    )
                else:
                    mobile_input.send_keys(save_name)
                mobile_input.send_keys(Keys.ENTER)
            else:
                driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    canvas.tabIndex = -1;
                    canvas.focus();
                    """
                )
                ActionChains(driver).send_keys(save_name).send_keys(Keys.ENTER).perform()

            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], []) === 0"
                )
            )
            wait.until(
                lambda d: d.execute_script(
                    """
                    return window.__tptGameModule.ccall(
                        'YandexWeb_TestLocalSaveFileSize',
                        'number',
                        ['string'],
                        [arguments[0]]
                    ) > 0
                    """,
                    save_name,
                )
            )
            local_save_size = driver.execute_script(
                """
                return window.__tptGameModule.ccall(
                    'YandexWeb_TestLocalSaveFileSize',
                    'number',
                    ['string'],
                    [arguments[0]]
                )
                """,
                save_name,
            )
            assert local_save_size > 100, (label, "local CPS file too small", local_save_size)

            if not mobile and language == "en":
                # Reopen Save with the same filename so the native overwrite
                # confirmation is stacked above LocalSaveActivity.
                driver.execute_script(
                    "window.__tptGameModule.ccall('YandexWeb_TestOpenLocalSave', null, [], [])"
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptGameModule.ccall("
                        "'YandexWeb_TestLocalSaveOpen', 'number', [], []) === 1 && "
                        "window.__tptNativeModalDepth === 1 && "
                        "window.__yandexGameplayStarted === false"
                    )
                )
                ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(
                    Keys.CONTROL
                ).send_keys(save_name).send_keys(Keys.ENTER).perform()
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptNativeModalDepth === 2 && "
                        "window.__tptNativeModalBlocked === true && "
                        "window.__yandexGameplayStarted === false && "
                        "window.__tptGameModule.ccall("
                        "'YandexWeb_TestLocalSaveOpen', 'number', [], []) === 1"
                    )
                )
                driver.execute_script(
                    "window.__tptGameModule.ccall("
                    "'YandexWeb_PushKey', null, ['number'], [27])"
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptNativeModalDepth === 1 && "
                        "window.__tptNativeModalBlocked === true && "
                        "window.__yandexGameplayStarted === false && "
                        "window.__tptGameModule.ccall("
                        "'YandexWeb_TestLocalSaveOpen', 'number', [], []) === 1"
                    )
                )
                driver.execute_script(
                    "window.__tptGameModule.ccall("
                    "'YandexWeb_PushKey', null, ['number'], [27])"
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptNativeModalDepth === 0 && "
                        "window.__tptNativeModalBlocked === false && "
                        "window.__yandexGameplayStarted === true && "
                        "window.__tptGameModule.ccall("
                        "'YandexWeb_TestLocalSaveOpen', 'number', [], []) === 0"
                    )
                )

            if mobile:
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptMobileTextInputActive === false"
                    )
                )

                saved_particle_count = driver.execute_script(
                    "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
                )
                assert saved_particle_count > 0, (
                    label,
                    "saved simulation unexpectedly contains no particles",
                    saved_particle_count,
                )
                driver.execute_script(
                    "window.__tptGameModule.ccall('YandexWeb_TestClearSimulation', null, [], [])"
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], []) === 0"
                    )
                )

                # Use the actual bottom-left Open button, not a direct native
                # test hook, to prove touch navigation reaches local saves.
                open_button = driver.execute_script(
                    """
                    const canvas = document.getElementById('canvas');
                    const r = canvas.getBoundingClientRect();
                    const m = window.__tptGameModule;
                    const nativeX = m.ccall('YandexWeb_TestGetOpenButtonX', 'number', [], []);
                    const nativeY = m.ccall('YandexWeb_TestGetOpenButtonY', 'number', [], []);
                    const windowX = m.ccall(
                        'YandexWeb_TestLogicalToWindowX',
                        'number',
                        ['number', 'number'],
                        [nativeX, nativeY]
                    );
                    const windowY = m.ccall(
                        'YandexWeb_TestLogicalToWindowY',
                        'number',
                        ['number', 'number'],
                        [nativeX, nativeY]
                    );
                    const windowWidth = m.ccall('YandexWeb_TestWindowWidth', 'number', [], []);
                    const windowHeight = m.ccall('YandexWeb_TestWindowHeight', 'number', [], []);
                    return {
                        x: r.left + (windowX / windowWidth) * r.width,
                        y: r.top + (windowY / windowHeight) * r.height,
                        nativeX,
                        nativeY,
                    };
                    """
                )
                assert open_button["nativeX"] >= 0 and open_button["nativeY"] >= 0, (
                    label,
                    open_button,
                )
                driver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    {
                        "type": "touchStart",
                        "touchPoints": [{
                            "x": open_button["x"],
                            "y": open_button["y"],
                            "radiusX": 4,
                            "radiusY": 4,
                            "force": 1,
                        }],
                    },
                )
                driver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    {"type": "touchEnd", "touchPoints": []},
                )
                wait.until(
                    lambda d: d.execute_script(
                        """
                        return window.__tptGameModule.ccall(
                            'YandexWeb_TestFileBrowserOpen', 'number', [], []
                        ) === 1;
                        """
                    )
                )
                wait.until(
                    lambda d: d.execute_script(
                        """
                        return window.__tptGameModule.ccall(
                            'YandexWeb_TestFileBrowserFileCount', 'number', [], []
                        ) >= 1;
                        """
                    )
                )
                assert driver.execute_script(
                    "return window.__tptMobileTextInputActive"
                ) is False, (
                    label,
                    "local save browser unexpectedly opened the mobile keyboard",
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptNativeModalBlocked === true && "
                        "window.__yandexGameplayStarted === false"
                    )
                )
                assert driver.execute_script(
                    "return window.__tptNativeModalBlocked"
                ) is True, (label, "local save browser did not block gameplay markup")

                driver.save_screenshot(
                    os.path.join(ARTIFACT_DIR, f"{label}-local-browser.png")
                )

                try:
                    first_save = wait.until(
                        lambda d: d.execute_script(
                            """
                            const m = window.__tptGameModule;
                            const nativeX = m.ccall(
                                'YandexWeb_TestFileBrowserFirstX', 'number', [], []
                            );
                            const nativeY = m.ccall(
                                'YandexWeb_TestFileBrowserFirstY', 'number', [], []
                            );
                            if (nativeX < 0 || nativeY < 0)
                                return null;
                            const canvas = document.getElementById('canvas');
                            const r = canvas.getBoundingClientRect();
                            const windowX = m.ccall(
                                'YandexWeb_TestLogicalToWindowX',
                                'number',
                                ['number', 'number'],
                                [nativeX, nativeY]
                            );
                            const windowY = m.ccall(
                                'YandexWeb_TestLogicalToWindowY',
                                'number',
                                ['number', 'number'],
                                [nativeX, nativeY]
                            );
                            const windowWidth = m.ccall(
                                'YandexWeb_TestWindowWidth', 'number', [], []
                            );
                            const windowHeight = m.ccall(
                                'YandexWeb_TestWindowHeight', 'number', [], []
                            );
                            return {
                                x: r.left + (windowX / windowWidth) * r.width,
                                y: r.top + (windowY / windowHeight) * r.height,
                                nativeX,
                                nativeY,
                            };
                            """
                        )
                    )
                except TimeoutException as error:
                    local_browser_diag = driver.execute_script(
                        """
                        const m = window.__tptGameModule;
                        return {
                            open: m.ccall(
                                'YandexWeb_TestFileBrowserOpen', 'number', [], []
                            ),
                            count: m.ccall(
                                'YandexWeb_TestFileBrowserFileCount', 'number', [], []
                            ),
                            firstX: m.ccall(
                                'YandexWeb_TestFileBrowserFirstX', 'number', [], []
                            ),
                            firstY: m.ccall(
                                'YandexWeb_TestFileBrowserFirstY', 'number', [], []
                            ),
                        };
                        """
                    )
                    raise AssertionError(
                        (
                            label,
                            "local browser did not expose first save geometry",
                            local_browser_diag,
                        )
                    ) from error
                driver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    {
                        "type": "touchStart",
                        "touchPoints": [{
                            "x": first_save["x"],
                            "y": first_save["y"],
                            "radiusX": 4,
                            "radiusY": 4,
                            "force": 1,
                        }],
                    },
                )
                driver.execute_cdp_cmd(
                    "Input.dispatchTouchEvent",
                    {"type": "touchEnd", "touchPoints": []},
                )
                wait.until(
                    lambda d: d.execute_script(
                        """
                        return window.__tptGameModule.ccall(
                            'YandexWeb_TestFileBrowserOpen', 'number', [], []
                        ) === 0;
                        """
                    )
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptMobileTextInputActive === false"
                    )
                )
                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], []) > 0"
                    )
                )
                reopened_particle_count = driver.execute_script(
                    "return window.__tptGameModule.ccall('YandexWeb_TestParticleCount', 'number', [], [])"
                )
                assert reopened_particle_count > 0, (
                    label,
                    "local save selection closed the browser but did not restore the simulation",
                    {
                        "saved": saved_particle_count,
                        "reopened": reopened_particle_count,
                    },
                )

                wait.until(
                    lambda d: d.execute_script(
                        "return window.__tptNativeModalBlocked === false && "
                        "window.__yandexGameplayStarted === true"
                    )
                )
                assert driver.execute_script(
                    "return window.__yandexGameplayStarted"
                ) is True, (label, "local browser did not restore gameplay markup")

            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestStorageFlush', null, [], [])"
            )
            wait.until(
                lambda d: d.execute_script("return window.__tptStorageFlushed === true")
            )
            storage_error = driver.execute_script(
                "return window.__tptStorageFlushError || ''"
            )
            assert storage_error == "", (label, storage_error)
        else:
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestCloseLocalSave', null, [], [])"
            )
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], []) === 0"
                )
            )

        wait.until(
            lambda d: d.execute_script(
                "return window.__tptNativeModalBlocked === false && "
                "window.__yandexGameplayStarted === true"
            )
        )
        gameplay_after_local_modal = driver.execute_script(
            "return {blocked: window.__tptNativeModalBlocked, gameplay: window.__yandexGameplayStarted};"
        )
        assert gameplay_after_local_modal["blocked"] is False, (label, gameplay_after_local_modal)
        assert gameplay_after_local_modal["gameplay"] is True, (label, gameplay_after_local_modal)

        driver.save_screenshot(os.path.join(ARTIFACT_DIR, f"{label}-resized.png"))

        if mobile:
            # Simulate a platform-controlled safe-area/banner inset changing
            # without window.resize. ResizeObserver must refit the canvas.
            dynamic_inset = driver.execute_script(
                """
                const app = document.getElementById('app');
                const canvas = document.getElementById('canvas');
                const before = canvas.getBoundingClientRect();
                app.style.paddingRight = '28px';
                app.style.paddingBottom = '24px';
                const style = getComputedStyle(app);
                const horizontalPadding =
                    parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
                const verticalPadding =
                    parseFloat(style.paddingTop) + parseFloat(style.paddingBottom);
                const availableWidth = app.clientWidth - horizontalPadding;
                const availableHeight = app.clientHeight - verticalPadding;
                return {
                    beforeWidth: before.width,
                    beforeHeight: before.height,
                    expectedWidth: Math.max(1, Math.floor(availableWidth)),
                    expectedHeight: Math.max(1, Math.floor(availableHeight)),
                };
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    """
                    const r = document.getElementById('canvas').getBoundingClientRect();
                    return Math.abs(r.width - arguments[0]) <= 2 &&
                           Math.abs(r.height - arguments[1]) <= 2;
                    """,
                    dynamic_inset["expectedWidth"],
                    dynamic_inset["expectedHeight"],
                )
            )
            driver.execute_script(
                "const app=document.getElementById('app');"
                "app.style.paddingRight=''; app.style.paddingBottom='';"
            )
            wait.until(
                lambda d: d.execute_script(
                    """
                    const r = document.getElementById('canvas').getBoundingClientRect();
                    return Math.abs(r.width - arguments[0]) <= 2 &&
                           Math.abs(r.height - arguments[1]) <= 2;
                    """,
                    dynamic_inset["beforeWidth"],
                    dynamic_inset["beforeHeight"],
                )
            )

        # Returning through browser history/BFCache must not leave the native
        # Emscripten loop frozen after pagehide -> pageshow.
        driver.execute_script(
            "window.dispatchEvent(new PageTransitionEvent('pagehide', {persisted: true}))"
        )
        wait.until(
            lambda d: d.execute_script("return window.__tptRuntimePaused === true")
        )
        driver.execute_script(
            "window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))"
        )
        wait.until(
            lambda d: d.execute_script("return window.__tptRuntimePaused === false")
        )

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

            persisted_local_save_size = driver.execute_script(
                """
                return window.__tptGameModule.ccall(
                    'YandexWeb_TestLocalSaveFileSize',
                    'number',
                    ['string'],
                    ['yandex-ci-save']
                )
                """
            )
            assert persisted_local_save_size > 100, (
                label,
                "native local CPS save missing after browser reload",
                persisted_local_save_size,
            )

        if not mobile and language == "en":
            main_loop_raf = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestMainLoopUsesRAF', 'number', [], [])"
            )
            assert main_loop_raf == 1, (
                label,
                "Emscripten main loop is not using requestAnimationFrame",
                main_loop_raf,
            )

            # Keep cap validation deterministic on noisy shared CI runners:
            # verify the engine accepted each requested cap, then use frame/tick
            # counts only to prove the loop is alive and does not exceed the cap.
            # Sustained throughput is covered separately by the stress metrics.
            driver.execute_script(
                "window.__tptGameModule.ccall("
                "'YandexWeb_TestClearSimulation', null, [], [])"
            )
            time.sleep(0.2)

            driver.execute_script(
                "window.__tptGameModule.ccall("
                "'YandexWeb_TestSetDrawLimit', null, ['number'], [30])"
            )
            draw_cap_30 = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestEffectiveDrawCap', 'number', [], [])"
            )
            assert draw_cap_30 == 30, (
                label,
                "engine did not accept 30 FPS rendering cap",
                draw_cap_30,
            )
            draw_30_start = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestDrawFrameIndex', 'number', [], [])"
            )
            time.sleep(2.0)
            draw_30_end = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestDrawFrameIndex', 'number', [], [])"
            )
            draw_30_delta = (draw_30_end - draw_30_start) % 7200
            draw_30_rate = draw_30_delta / 2.0
            assert 0 < draw_30_rate <= 40, (
                label,
                "30 FPS rendering cap invalid or render loop stalled",
                {"frames": draw_30_delta, "rate": draw_30_rate},
            )

            driver.execute_script(
                "window.__tptGameModule.ccall("
                "'YandexWeb_TestSetDrawLimit', null, ['number'], [60])"
            )
            draw_cap_60 = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestEffectiveDrawCap', 'number', [], [])"
            )
            assert draw_cap_60 == 60, (
                label,
                "engine did not accept 60 FPS rendering cap",
                draw_cap_60,
            )
            draw_60_start = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestDrawFrameIndex', 'number', [], [])"
            )
            time.sleep(1.5)
            draw_60_end = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestDrawFrameIndex', 'number', [], [])"
            )
            draw_60_delta = (draw_60_end - draw_60_start) % 7200
            draw_60_rate = draw_60_delta / 1.5
            assert 0 < draw_60_rate <= 80, (
                label,
                "render loop stalled after restoring 60 FPS cap",
                {
                    "fps30": {"frames": draw_30_delta, "rate": draw_30_rate},
                    "fps60": {"frames": draw_60_delta, "rate": draw_60_rate},
                },
            )

            driver.execute_script(
                "window.__tptGameModule.ccall("
                "'YandexWeb_TestSetSimulationFpsLimit', null, ['number'], [20])"
            )
            sim_cap_20 = float(
                driver.execute_script(
                    "return window.__tptGameModule.ccall("
                    "'YandexWeb_TestSimulationFpsLimit', 'number', [], [])"
                )
            )
            assert abs(sim_cap_20 - 20.0) < 0.01, (
                label,
                "engine did not accept 20 FPS simulation cap",
                sim_cap_20,
            )
            sim_20_start = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestSimulationFrameCount', 'number', [], [])"
            )
            time.sleep(2.2)
            sim_20_end = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestSimulationFrameCount', 'number', [], [])"
            )
            sim_20_delta = sim_20_end - sim_20_start
            sim_20_rate = sim_20_delta / 2.2
            assert 0 < sim_20_rate <= 32, (
                label,
                "20 FPS simulation cap invalid or simulation stalled",
                {"ticks": sim_20_delta, "rate": sim_20_rate},
            )

            driver.execute_script(
                "window.__tptGameModule.ccall("
                "'YandexWeb_TestSetSimulationFpsLimit', null, ['number'], [60])"
            )
            sim_cap_60 = float(
                driver.execute_script(
                    "return window.__tptGameModule.ccall("
                    "'YandexWeb_TestSimulationFpsLimit', 'number', [], [])"
                )
            )
            assert abs(sim_cap_60 - 60.0) < 0.01, (
                label,
                "engine did not accept 60 FPS simulation cap",
                sim_cap_60,
            )
            sim_60_start = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestSimulationFrameCount', 'number', [], [])"
            )
            time.sleep(1.5)
            sim_60_end = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestSimulationFrameCount', 'number', [], [])"
            )
            sim_60_delta = sim_60_end - sim_60_start
            sim_60_rate = sim_60_delta / 1.5
            assert 0 < sim_60_rate <= 80, (
                label,
                "simulation stalled after restoring 60 FPS cap",
                {
                    "fps20": {"ticks": sim_20_delta, "rate": sim_20_rate},
                    "fps60": {"ticks": sim_60_delta, "rate": sim_60_rate},
                },
            )

            main_loop_raf_after_caps = driver.execute_script(
                "return window.__tptGameModule.ccall("
                "'YandexWeb_TestMainLoopUsesRAF', 'number', [], [])"
            )
            assert main_loop_raf_after_caps == 1, (
                label,
                "FPS cap changes moved Emscripten main loop off requestAnimationFrame",
                main_loop_raf_after_caps,
            )

        performance = None
        if language == "en":
            performance = [
                record_performance_metric(
                    driver,
                    label,
                    "dust-20k",
                    "YandexWeb_TestFillDust",
                    20000,
                ),
                record_performance_metric(
                    driver,
                    label,
                    "water-gravity-12k",
                    "YandexWeb_TestFillWaterGravity",
                    12000,
                ),
                record_performance_metric(
                    driver,
                    label,
                    "dust-45k",
                    "YandexWeb_TestFillDust",
                    45000,
                ),
                record_performance_metric(
                    driver,
                    label,
                    "water-gravity-28k",
                    "YandexWeb_TestFillWaterGravity",
                    28000,
                ),
            ]

        if mobile:
            # Open Settings through the real native button coordinates and a
            # real browser touch event. This guards tiny-hit-target regressions.
            settings_button = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                const m = window.__tptGameModule;
                const nativeX = m.ccall('YandexWeb_TestGetSettingsButtonX', 'number', [], []);
                const nativeY = m.ccall('YandexWeb_TestGetSettingsButtonY', 'number', [], []);
                const windowX = m.ccall(
                    'YandexWeb_TestLogicalToWindowX',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowY = m.ccall(
                    'YandexWeb_TestLogicalToWindowY',
                    'number',
                    ['number', 'number'],
                    [nativeX, nativeY]
                );
                const windowWidth = m.ccall('YandexWeb_TestWindowWidth', 'number', [], []);
                const windowHeight = m.ccall('YandexWeb_TestWindowHeight', 'number', [], []);
                return {
                    x: r.left + (windowX / windowWidth) * r.width,
                    y: r.top + (windowY / windowHeight) * r.height,
                    nativeX,
                    nativeY,
                };
                """
            )
            assert settings_button["nativeX"] >= 0 and settings_button["nativeY"] >= 0, (
                label,
                settings_button,
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [{
                        "x": settings_button["x"],
                        "y": settings_button["y"],
                        "radiusX": 4,
                        "radiusY": 4,
                        "force": 1,
                    }],
                },
            )
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {"type": "touchEnd", "touchPoints": []},
            )
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptGameModule.ccall('YandexWeb_TestOptionsOpen', 'number', [], []) === 1"
                )
            )
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptNativeModalBlocked === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )
            assert driver.execute_script(
                "return window.__tptNativeModalBlocked"
            ) is True, (label, "settings did not block gameplay markup")
            threaded_control_present = driver.execute_script(
                """
                return window.__tptGameModule.ccall(
                    'YandexWeb_TestThreadedRenderingPresent', 'number', [], []
                );
                """
            )
            assert threaded_control_present == 0, (
                label,
                "pthread-free web build exposed threaded rendering setting",
                threaded_control_present,
            )
            # Triple blocker race: native modal + portrait gate + hidden
            # document. Clearing any one or two blockers must never restart
            # gameplay until the final blocker is gone.
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
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            driver.execute_script(
                """
                window.__tptSyntheticHidden = true;
                Object.defineProperty(document, 'hidden', {
                    configurable: true,
                    get() { return window.__tptSyntheticHidden; }
                });
                document.dispatchEvent(new Event('visibilitychange'));
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    "return document.hidden === true && "
                    "window.__tptOrientationBlocked === true && "
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            # Clear visibility first: portrait + modal still block gameplay.
            driver.execute_script(
                """
                window.__tptSyntheticHidden = false;
                document.dispatchEvent(new Event('visibilitychange'));
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    "return document.hidden === false && "
                    "window.__tptOrientationBlocked === true && "
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            # Clear portrait next: Settings remains the last gameplay blocker.
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
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === false && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            driver.execute_script(
                """
                delete document.hidden;
                delete window.__tptSyntheticHidden;
                """
            )

            driver.save_screenshot(
                os.path.join(ARTIFACT_DIR, f"{label}-settings.png")
            )

            driver.execute_script("window.ysdk.emit('game_api_pause')")
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptRuntimePaused === true && "
                    "window.__tptNativeModalBlocked === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )
            driver.execute_script("window.ysdk.emit('game_api_resume')")
            wait.until(
                lambda d: d.execute_script(
                    "return window.__tptRuntimePaused === false && "
                    "window.__tptNativeModalBlocked === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )
            settings_platform_resume_state = driver.execute_script(
                """
                return {
                    paused: window.__tptRuntimePaused,
                    blocked: window.__tptNativeModalBlocked,
                    gameplay: window.__yandexGameplayStarted,
                };
                """
            )
            assert settings_platform_resume_state["paused"] is False, (
                label,
                settings_platform_resume_state,
            )
            assert settings_platform_resume_state["blocked"] is True, (
                label,
                settings_platform_resume_state,
            )
            assert settings_platform_resume_state["gameplay"] is False, (
                label,
                settings_platform_resume_state,
            )

            # Combined blocker race: portrait and a native modal can be
            # active together. Returning to landscape clears only the
            # orientation blocker; Settings must continue to keep gameplay
            # stopped until the modal itself closes.
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
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === true && "
                    "window.__yandexGameplayStarted === false"
                )
            )

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
                    "window.__tptNativeModalBlocked === true && "
                    "window.__tptRuntimePaused === false && "
                    "window.__yandexGameplayStarted === false"
                )
            )

            driver.execute_script(
                """
                window.__tptGameModule.ccall(
                    'YandexWeb_PushKey',
                    null,
                    ['number'],
                    [27]
                );
                """
            )
            wait.until(
                lambda d: d.execute_script(
                    """
                    return window.__tptGameModule.ccall(
                        'YandexWeb_TestOptionsOpen', 'number', [], []
                    ) === 0 &&
                    window.__tptNativeModalBlocked === false &&
                    window.__tptOrientationBlocked === false &&
                    window.__yandexGameplayStarted === true;
                    """
                )
            )
            settings_closed_state = driver.execute_script(
                """
                return {
                    open: window.__tptGameModule.ccall(
                        'YandexWeb_TestOptionsOpen', 'number', [], []
                    ),
                    blocked: window.__tptNativeModalBlocked,
                    gameplay: window.__yandexGameplayStarted,
                };
                """
            )
            assert settings_closed_state["open"] == 0, (label, settings_closed_state)
            assert settings_closed_state["blocked"] is False, (label, settings_closed_state)
            assert settings_closed_state["gameplay"] is True, (label, settings_closed_state)

        network_events = assert_no_external_network(driver, label)

        browser_logs = driver.get_log("browser")
        browser_log_path = os.path.join(
            ARTIFACT_DIR, f"{label}-browser-console.json"
        )
        with open(browser_log_path, "w", encoding="utf-8") as handle:
            json.dump(browser_logs, handle, ensure_ascii=False, indent=2)

        fatal_markers = (
            "Uncaught",
            "TypeError",
            "ReferenceError",
            "SyntaxError",
            "net::ERR",
            "Failed to load resource",
        )
        fatal_browser_logs = [
            entry
            for entry in browser_logs
            if entry.get("level") == "SEVERE"
            and "favicon.ico" not in entry.get("message", "")
            and any(marker in entry.get("message", "") for marker in fatal_markers)
        ]
        assert not fatal_browser_logs, (
            label,
            "fatal browser console errors",
            fatal_browser_logs,
        )

        unexpected_severe_logs = [
            entry
            for entry in browser_logs
            if entry.get("level") == "SEVERE"
            and "favicon.ico" not in entry.get("message", "")
        ]
        assert not unexpected_severe_logs, (
            label,
            "unexpected severe browser console entries",
            unexpected_severe_logs,
        )

        print(
            f"[smoke] {label}: OK {state}; resized={resized}; "
            f"paused={paused}; resumed={resumed}; performance={performance}; "
            f"network_events={len(network_events)}"
        )
    finally:
        driver.quit()


def smoke_sdk_script_failure():
    label = "desktop-sdk-script-failure"
    driver = make_driver(mobile=False, browser_language="ru-RU")
    started = time.monotonic()
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setBlockedURLs",
            {"urls": ["*://*/sdk.js"]},
        )
        driver.set_page_load_timeout(45)
        driver.get(f"{BASE_URL}/?lang=ru&device=desktop")

        wait = WebDriverWait(driver, 20)
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
                    window.__tptGameModule
                );
                """
            )
        )

        state = driver.execute_script(
            """
            const script = document.getElementById('yandex-games-sdk');
            return {
                sdkMissing: window.ysdk === undefined,
                yaGamesMissing: window.YaGames === undefined,
                language: window.tptLanguage,
                lockedLanguage: window.__tptLanguageLocked,
                sdkScriptPresent: Boolean(script),
                sdkScriptAsync: script?.async === true,
                sdkScriptPath: script?.getAttribute('src') || '',
                fatalHidden: document.getElementById('fatal').hidden,
                loaderHidden: document.getElementById('loader').hidden,
                canvasDisplay: document.getElementById('canvas').style.display,
            };
            """
        )
        elapsed = time.monotonic() - started

        assert elapsed < 15.0, (
            label,
            "blocked /sdk.js prevented local fallback startup",
            elapsed,
            state,
        )
        assert state["sdkMissing"] is True, (label, state)
        assert state["yaGamesMissing"] is True, (label, state)
        assert state["language"] == "ru", (label, state)
        assert state["lockedLanguage"] == "ru", (label, state)
        assert state["sdkScriptPresent"] is True, (label, state)
        assert state["sdkScriptAsync"] is True, (label, state)
        assert state["sdkScriptPath"] == "/sdk.js", (label, state)
        assert state["fatalHidden"] is True, (label, state)
        assert state["loaderHidden"] is True, (label, state)
        assert state["canvasDisplay"] == "block", (label, state)

        browser_logs = driver.get_log("browser")
        unexpected_severe_logs = [
            entry
            for entry in browser_logs
            if entry.get("level") == "SEVERE"
            and "favicon.ico" not in entry.get("message", "")
            and not (
                "sdk.js" in entry.get("message", "")
                and "ERR_BLOCKED_BY_CLIENT" in entry.get("message", "")
            )
        ]
        assert not unexpected_severe_logs, (
            label,
            "unexpected severe browser console entries",
            unexpected_severe_logs,
        )

        print(f"[smoke] {label}: OK fallback={elapsed:.2f}s {state}")
    finally:
        driver.quit()


def smoke_sdk_script_delay():
    label = "desktop-sdk-script-delay"
    # A dynamically inserted async script still participates in the document
    # load event. Selenium's normal navigation strategy would therefore wait
    # for the deliberately delayed /sdk.js before returning from driver.get(),
    # hiding the exact pre-load fallback behaviour this smoke is meant to test.
    # Use "none" only here so WebDriver returns immediately after navigation
    # starts and the assertion measures actual canvas readiness.
    driver = make_driver(
        mobile=False,
        browser_language="ru-RU",
        page_load_strategy="none",
    )
    started = time.monotonic()
    try:
        driver.set_page_load_timeout(45)
        driver.get(
            f"{BASE_URL}/?lang=ru&device=desktop&sdkScript=delay"
        )
        wait = WebDriverWait(driver, 25)

        # /sdk.js is delayed by the threaded smoke server for 15 seconds.
        # The 8-second SDK fallback must let the native game become playable
        # while that request is still in flight.
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
                    window.__tptGameModule
                );
                """
            )
        )

        fallback_elapsed = time.monotonic() - started
        fallback = driver.execute_script(
            """
            const script = document.getElementById('yandex-games-sdk');
            return {
                sdkMissing: window.ysdk === undefined,
                yaGamesMissing: window.YaGames === undefined,
                language: window.tptLanguage,
                lockedLanguage: window.__tptLanguageLocked,
                sdkScriptPresent: Boolean(script),
                sdkScriptAsync: script?.async === true,
                sdkScriptPath: script?.getAttribute('src') || '',
                loaderHidden: document.getElementById('loader').hidden,
                canvasDisplay: document.getElementById('canvas').style.display,
            };
            """
        )

        assert fallback_elapsed < 13.0, (
            label,
            "slow /sdk.js blocked game startup past the SDK timeout",
            fallback_elapsed,
            fallback,
        )
        assert fallback["sdkMissing"] is True, (label, fallback)
        assert fallback["yaGamesMissing"] is True, (label, fallback)
        assert fallback["language"] == "ru", (label, fallback)
        assert fallback["lockedLanguage"] == "ru", (label, fallback)
        assert fallback["sdkScriptPresent"] is True, (label, fallback)
        assert fallback["sdkScriptAsync"] is True, (label, fallback)
        assert fallback["sdkScriptPath"] == "/sdk.js", (label, fallback)
        assert fallback["loaderHidden"] is True, (label, fallback)
        assert fallback["canvasDisplay"] == "block", (label, fallback)

        # When the delayed script finally arrives, it must initialize and
        # reconcile the already-presentable game without a reload.
        wait.until(
            lambda d: d.execute_script(
                """
                return Boolean(
                    window.ysdk &&
                    window.__yandexReadyCount === 1 &&
                    window.__yandexLoadingReady === true &&
                    window.__yandexGameplayStarted === true
                );
                """
            )
        )

        recovered = driver.execute_script(
            """
            const events = window.__yandexSdkEvents || [];
            return {
                readyCount: window.__yandexReadyCount || 0,
                readyIndex: events.indexOf('ready'),
                gameplayStartIndex: events.indexOf('gameplay-start'),
                language: window.tptLanguage,
                detectedLanguage: window.yandexDetectedLanguage,
                lockedLanguage: window.__tptLanguageLocked,
                sdkMobilePlatform: window.__tptSdkMobilePlatform,
                loaderHidden: document.getElementById('loader').hidden,
                canvasDisplay: document.getElementById('canvas').style.display,
            };
            """
        )

        assert recovered["readyCount"] == 1, (label, recovered)
        assert recovered["readyIndex"] >= 0, (label, recovered)
        assert recovered["gameplayStartIndex"] > recovered["readyIndex"], (
            label,
            "delayed SDK script recovery did not preserve Ready -> Gameplay ordering",
            recovered,
        )
        assert recovered["language"] == "ru", (label, recovered)
        assert recovered["detectedLanguage"] == "ru", (label, recovered)
        assert recovered["lockedLanguage"] == "ru", (label, recovered)
        assert recovered["sdkMobilePlatform"] is False, (label, recovered)
        assert recovered["loaderHidden"] is True, (label, recovered)
        assert recovered["canvasDisplay"] == "block", (label, recovered)

        browser_logs = driver.get_log("browser")
        unexpected_severe_logs = [
            entry
            for entry in browser_logs
            if entry.get("level") == "SEVERE"
            and "favicon.ico" not in entry.get("message", "")
        ]
        assert not unexpected_severe_logs, (
            label,
            "unexpected severe browser console entries",
            unexpected_severe_logs,
        )

        total_elapsed = time.monotonic() - started
        print(
            f"[smoke] {label}: OK fallback={fallback_elapsed:.2f}s "
            f"recovered={total_elapsed:.2f}s"
        )
    finally:
        driver.quit()


def smoke_sdk_late_recovery():
    label = "desktop-sdk-late-recovery"
    driver = make_driver(mobile=False, browser_language="ru-RU")
    started = time.monotonic()
    try:
        driver.set_page_load_timeout(45)
        driver.get(f"{BASE_URL}/?lang=ru&device=desktop&sdk=delay")
        wait = WebDriverWait(driver, 20)

        # The native game must become presentable from the 8-second fallback
        # before the deliberately delayed SDK resolves at 11 seconds.
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
                    window.__tptGameModule
                );
                """
            )
        )

        fallback_elapsed = time.monotonic() - started
        assert fallback_elapsed < 10.5, (
            label,
            "slow YaGames.init blocked game startup instead of using timeout fallback",
            fallback_elapsed,
        )
        fallback_state = driver.execute_script(
            """
            return {
                sdkMissing: window.ysdk === undefined,
                language: window.tptLanguage,
                lockedLanguage: window.__tptLanguageLocked,
                sdkMobilePlatform: window.__tptSdkMobilePlatform,
                htmlLanguage: document.documentElement.lang,
            };
            """
        )
        assert fallback_state["sdkMissing"] is True, (
            label,
            "delayed SDK resolved before fallback state was observed",
            fallback_state,
        )
        assert fallback_state["language"] == "ru", (
            label,
            "browser-language fallback did not select Russian",
            fallback_state,
        )
        assert fallback_state["lockedLanguage"] == "ru", (label, fallback_state)
        assert fallback_state["sdkMobilePlatform"] is None, (label, fallback_state)
        assert fallback_state["htmlLanguage"] == "ru", (label, fallback_state)
        assert driver.execute_script(
            "return window.__yandexLoadingReady === false"
        ) is True, (
            label,
            "LoadingAPI.ready ran before delayed SDK recovery",
        )

        # When the original YaGames.init() eventually resolves, the running
        # game must adopt it without reload and replay platform state exactly
        # once: LoadingAPI.ready first, then GameplayAPI.start.
        wait.until(
            lambda d: d.execute_script(
                """
                return Boolean(
                    window.ysdk &&
                    window.__yandexReadyCount === 1 &&
                    window.__yandexLoadingReady === true &&
                    window.__yandexGameplayStarted === true
                );
                """
            )
        )

        recovered = driver.execute_script(
            """
            const events = window.__yandexSdkEvents || [];
            return {
                readyCount: window.__yandexReadyCount || 0,
                events,
                readyIndex: events.indexOf('ready'),
                gameplayStartIndex: events.indexOf('gameplay-start'),
                loaderHidden: document.getElementById('loader').hidden,
                canvasDisplay: document.getElementById('canvas').style.display,
                language: window.tptLanguage,
                detectedLanguage: window.yandexDetectedLanguage,
                lockedLanguage: window.__tptLanguageLocked,
                sdkMobilePlatform: window.__tptSdkMobilePlatform,
                htmlLanguage: document.documentElement.lang,
            };
            """
        )
        assert recovered["readyCount"] == 1, (label, recovered)
        assert recovered["readyIndex"] >= 0, (label, recovered)
        assert recovered["gameplayStartIndex"] > recovered["readyIndex"], (
            label,
            "late SDK recovery did not preserve Ready -> Gameplay ordering",
            recovered,
        )
        assert recovered["loaderHidden"] is True, (label, recovered)
        assert recovered["canvasDisplay"] == "block", (label, recovered)
        assert recovered["language"] == "ru", (label, recovered)
        assert recovered["detectedLanguage"] == "ru", (label, recovered)
        assert recovered["lockedLanguage"] == "ru", (label, recovered)
        assert recovered["sdkMobilePlatform"] is False, (label, recovered)
        assert recovered["htmlLanguage"] == "ru", (label, recovered)

        browser_logs = driver.get_log("browser")
        unexpected_severe_logs = [
            entry
            for entry in browser_logs
            if entry.get("level") == "SEVERE"
            and "favicon.ico" not in entry.get("message", "")
        ]
        assert not unexpected_severe_logs, (
            label,
            "unexpected severe browser console entries",
            unexpected_severe_logs,
        )
        total_elapsed = time.monotonic() - started
        print(
            f"[smoke] {label}: OK fallback={fallback_elapsed:.2f}s "
            f"recovered={total_elapsed:.2f}s"
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    # Test both platform shapes and both supported languages.
    smoke_case("en", mobile=False)
    smoke_case("ru", mobile=False)
    smoke_case("en", mobile=True)
    smoke_case("ru", mobile=True)
    smoke_sdk_script_failure()
    smoke_sdk_script_delay()
    smoke_sdk_late_recovery()
