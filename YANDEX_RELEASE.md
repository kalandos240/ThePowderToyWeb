# Yandex Games release checklist

This file is for the developer/release process only. It is not included in the game ZIP.

## Draft settings

- Platform: desktop + mobile.
- Mobile orientation: **landscape**.
- Languages: **Russian** and **English**.
- The game automatically selects RU/EN from `ysdk.environment.i18n.lang`; English is the fallback.
- The game must remain playable without third-party registration.
- Use the archive-hosted Yandex Games SDK path `/sdk.js`.

## Runtime requirements already integrated

- `YaGames.init()` completes before SDK-dependent calls.
- `LoadingAPI.ready()` is called only after the native game marks itself presentable.
- `GameplayAPI.start()/stop()` are integrated.
- `game_api_pause/game_api_resume` pause and resume the native Emscripten main loop.
- Mobile portrait mode is blocked with a localized rotate-device prompt; simulation/gameplay are paused while blocked.
- Desktop and mobile viewport changes, orientation changes, visualViewport changes, and fullscreen changes refit the canvas.
- Safe-area content-box sizing subtracts CSS padding before scaling the canvas; repeated mobile viewport/fullscreen tests verify that the canvas never overflows the usable app area.
- Browser scrolling, text selection, long-press selection, and the canvas context menu are disabled by the web shell.
- Local progress uses Emscripten IDBFS/IndexedDB and is flushed during the game loop and before platform pause.
- The Yandex build is pthread-free and does not require SharedArrayBuffer/cross-origin isolation.
- Upstream HTTP features and external community links/actions are removed or blocked in the Yandex UI.

## CI release gates

The build workflow currently checks:

- Russian glyph coverage in the bundled TPT font.
- Complete Russian descriptions for every upstream element.
- No visible upstream community links in the patched GUI.
- No SharedArrayBuffer/shared-memory/pthread build markers.
- Uncompressed package size <= 100 MB.
- Desktop EN and RU startup.
- Mobile EN and RU startup.
- Real desktop mouse selection and drawing.
- Real mobile touch selection and drawing.
- Portrait -> landscape behavior and repeated orientation cycles.
- Repeated fullscreen-like mobile viewport changes.
- Yandex pause/resume events.
- IndexedDB/IDBFS persistence across page reload.
- Browser smoke screenshots.
- Desktop/mobile frame-time telemetry on an approximately 20,000-particle stress scene.
- Current 20k-particle CI baseline: median 16.7 ms / ~59.88 FPS, p95 16.7 ms on both desktop and mobile emulation.

## Monetization

Yandex moderation expects monetization to be enabled by default unless the developer explicitly states that the game is intentionally non-monetized.

For a monetized release, choose at least one of:

- sticky banner configured in the Yandex Games console;
- interstitial ads at safe non-gameplay moments;
- rewarded ads tied to an optional reward mechanic;
- in-app purchases, if a suitable mechanic is added later.

The automatic startup ad does **not** count as the game's own monetization setup.

For this sandbox game, a console-configured sticky banner is the lowest-risk first option because it does not require inventing artificial level transitions. Verify on real mobile devices that the banner-adjusted available area does not cover the TPT interface.

## Final manual checks before moderation

- Test the uploaded draft through the Yandex debug panel.
- Verify Game Ready becomes green and is not called on timeout.
- Test at least one desktop browser and one real Android/iOS device.
- On mobile, repeat portrait/landscape and fullscreen transitions several times.
- Verify long press does not open a browser context menu.
- Create a real local save, reload the page, and reopen it.
- Verify RU and EN through the Yandex language mock.
- Run a heavy simulation for several minutes and check responsiveness.
- Confirm the sticky banner/ad configuration, or state in the developer comment that the game is intentionally non-monetized.
