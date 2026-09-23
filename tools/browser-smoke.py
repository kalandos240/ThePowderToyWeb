#!/usr/bin/env python3
import json
import os
import statistics
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("TPT_SMOKE_URL", "http://127.0.0.1:8765")
ARTIFACT_DIR = os.environ.get("TPT_SMOKE_ARTIFACT_DIR", "test-artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)


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
            for alias in ["ru", "be", "kk", "uk", "uz"]:
                assert locale_aliases[alias] == "ru", (label, alias, locale_aliases)
            for alias in ["de", "tr"]:
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

        if not mobile:
            # Prove desktop mouse input can select a real UI element and draw.
            driver.execute_script(
                "window.__tptGameModule.ccall('YandexWeb_TestSelectWater', null, [], [])"
            )
            desktop_before_tap = driver.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestActiveToolIsDust', 'number', [], [])"
            )
            assert desktop_before_tap == 0, (label, "failed to switch away from DUST before mouse UI test")

            dust_button = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                const logicalX = canvas.width - 41;
                // Intentionally tap above the visible button; TouchUI should
                // resolve this to the nearest button within the expanded hit halo.
                const logicalY = canvas.height - 45;
                return {
                    x: r.left + (logicalX / canvas.width) * r.width,
                    y: r.top + (logicalY / canvas.height) * r.height,
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

            dust_button = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                const logicalX = canvas.width - 41;
                const logicalY = canvas.height - 30;
                return {
                    x: r.left + (logicalX / canvas.width) * r.width,
                    y: r.top + (logicalY / canvas.height) * r.height,
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
                assert abs(
                    fullscreen_state["width"] - fullscreen_state["expectedWidth"]
                ) <= 2, (label, fullscreen_cycle, fullscreen_state)
                assert abs(
                    fullscreen_state["height"] - fullscreen_state["expectedHeight"]
                ) <= 2, (label, fullscreen_cycle, fullscreen_state)
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

        # Prove the real Save button opens the local-save dialog on both
        # desktop mouse and mobile touch input.
        save_button = driver.execute_script(
            """
            const canvas = document.getElementById('canvas');
            const r = canvas.getBoundingClientRect();
            const logicalX = 45;
            // On mobile intentionally tap ~6 logical px above the Save button.
            // Desktop keeps the exact visible-button click.
            const logicalY = canvas.height - (window.tptTouchUIDetected ? 22 : 8);
            return {
                x: r.left + (logicalX / canvas.width) * r.width,
                y: r.top + (logicalY / canvas.height) * r.height,
            };
            """
        )
        if mobile:
            driver.execute_cdp_cmd(
                "Input.dispatchTouchEvent",
                {
                    "type": "touchStart",
                    "touchPoints": [{
                        "x": save_button["x"],
                        "y": save_button["y"],
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
        else:
            canvas_element = driver.find_element(By.ID, "canvas")
            save_geometry = driver.execute_script(
                """
                const canvas = document.getElementById('canvas');
                const r = canvas.getBoundingClientRect();
                return {
                    width: r.width,
                    height: r.height,
                    logicalWidth: canvas.width,
                    logicalHeight: canvas.height,
                };
                """
            )
            save_offset_x = int(
                save_geometry["width"]
                * ((45 / save_geometry["logicalWidth"]) - 0.50)
            )
            save_offset_y = int(
                save_geometry["height"]
                * (((save_geometry["logicalHeight"] - 8) / save_geometry["logicalHeight"]) - 0.50)
            )
            (
                ActionChains(driver)
                .move_to_element_with_offset(
                    canvas_element,
                    save_offset_x,
                    save_offset_y,
                )
                .click()
                .perform()
            )

        wait.until(
            lambda d: d.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], []) === 1"
            )
        )
        save_open = driver.execute_script(
            "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], [])"
        )
        assert save_open == 1, (label, f"Save touch target did not open LocalSaveActivity: {save_button}")
        driver.execute_script(
            "window.__tptGameModule.ccall('YandexWeb_TestCloseLocalSave', null, [], [])"
        )
        wait.until(
            lambda d: d.execute_script(
                "return window.__tptGameModule.ccall('YandexWeb_TestLocalSaveOpen', 'number', [], []) === 0"
            )
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
            ]

        print(
            f"[smoke] {label}: OK {state}; resized={resized}; "
            f"paused={paused}; resumed={resumed}; performance={performance}"
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    # Test both platform shapes and both supported languages.
    smoke_case("en", mobile=False)
    smoke_case("ru", mobile=False)
    smoke_case("en", mobile=True)
    smoke_case("ru", mobile=True)
