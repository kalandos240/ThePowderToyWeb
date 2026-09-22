#!/usr/bin/env python3
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = os.environ.get("TPT_SMOKE_URL", "http://127.0.0.1:8765")


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
                    window.__yandexLoadingReady === true &&
                    window.__yandexGameplayStarted === true
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
                canvasDisplay: canvas.style.display,
                canvasWidth: rect.width,
                canvasHeight: rect.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                maxTouchPoints: navigator.maxTouchPoints,
                coarsePointer: window.matchMedia('(pointer: coarse)').matches,
                ready: window.__yandexLoadingReady,
                gameplay: window.__yandexGameplayStarted,
            };
            """
        )

        assert state["language"] == language, (label, state)
        assert state["fatalHidden"] is True, (label, state)
        assert state["loaderHidden"] is True, (label, state)
        assert state["canvasDisplay"] == "block", (label, state)
        assert state["canvasWidth"] > 0 and state["canvasHeight"] > 0, (label, state)
        assert state["canvasWidth"] <= state["viewportWidth"] + 1, (label, state)
        assert state["canvasHeight"] <= state["viewportHeight"] + 1, (label, state)
        assert state["ready"] is True and state["gameplay"] is True, (label, state)

        if mobile:
            assert state["maxTouchPoints"] > 0 or state["coarsePointer"], (label, state)
            assert state["touchUI"] is True, (label, state)
        else:
            assert state["touchUI"] is False, (label, state)

        print(f"[smoke] {label}: OK {state}")
    finally:
        driver.quit()


if __name__ == "__main__":
    # Test both platform shapes and both supported languages.
    smoke_case("en", mobile=False)
    smoke_case("ru", mobile=False)
    smoke_case("en", mobile=True)
    smoke_case("ru", mobile=True)
