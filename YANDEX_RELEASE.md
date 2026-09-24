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
- Yandex device classification through the documented deviceInfo API with touch detection fallback.
- Real desktop mouse selection and drawing.
- Real mobile touch selection and drawing.
- Portrait -> landscape behavior and repeated orientation cycles.
- Repeated fullscreen-like mobile viewport changes.
- Desktop effective viewport checks corresponding to 80%, 100%, and 125% browser zoom, with no system scrolling or canvas overflow.
- Combined mobile lifecycle checks for portrait blocking, page visibility, and Yandex platform pause/resume reconciliation.
- Yandex pause/resume events.
- IndexedDB/IDBFS persistence across page reload.
- Full mobile local-save flow: create a CPS save, reopen it from the native local browser, and restore simulation state.
- Mobile RU IME composition handling, including duplicate post-composition input suppression and UTF-8 filename readback.
- Fatal browser-console/network error gating with retained console-log artifacts.
- Game Ready ordering: LoadingAPI.ready() exactly once after the loader is hidden and the canvas is interactive, before GameplayAPI.start().
- Native modal gameplay markup: Save, Local Browser, Settings, and other Engine modal windows stop gameplay markup while open and restore it after normal close.
- Gameplay markup reconciliation when a local blocker clears during game_api_pause before game_api_resume.
- Browser smoke screenshots.
- Yandex ZIP validation: one root index.html, safe relative paths, archive integrity, ASCII/no-whitespace filenames, and unpacked size <= 100 MB.
- Desktop/mobile frame-time telemetry on DUST and water+Newtonian-gravity scenes at approximately 20k/12k and 45k/28k particles.
- Catastrophic performance regression gate: engine FPS >= 30 and browser p95 frame time <= 50 ms on CI stress scenes.
- Current heavy-scene GitHub-runner baseline is approximately 59-60 engine FPS with p95 browser frame time around 16.7-16.8 ms.

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
- Create a real local save, reload the page, and reopen it on a physical device even though the same flow is covered in browser CI.
- Verify RU and EN through the Yandex language mock.
- Run a heavy simulation for several minutes and check responsiveness.
- Confirm the sticky banner/ad configuration, or state in the developer comment that the game is intentionally non-monetized.
