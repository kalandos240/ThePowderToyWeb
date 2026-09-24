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
- Browser scrolling, overscroll/swipe-to-refresh, text selection, long-press selection, and the canvas context menu are disabled by the web shell.
- Local progress uses Emscripten IDBFS/IndexedDB and is flushed during the game loop and before platform pause.
- The Yandex build is pthread-free and does not require SharedArrayBuffer/cross-origin isolation.
- The Emscripten browser pump stays on `requestAnimationFrame`; TPT's native draw/tick schedulers enforce rendering and simulation FPS caps without switching the browser loop to `setTimeout`.
- Upstream HTTP features and external community links/actions are removed or blocked in the Yandex UI.

## CI release gates

The build workflow currently checks:

- Russian glyph coverage in the bundled TPT font.
- Complete Russian descriptions for every upstream element.
- No visible upstream community links in the patched GUI.
- No SharedArrayBuffer/shared-memory/pthread build markers.
- Uncompressed package size <= 100 MB.
- ZIP integrity, exactly one root `index.html`, safe archive paths, and ASCII/no-whitespace path names.
- Desktop EN and RU startup.
- Mobile EN and RU startup.
- Real desktop mouse selection and drawing.
- Real mobile touch selection and drawing.
- Portrait -> landscape behavior and repeated orientation cycles.
- Repeated fullscreen-like mobile viewport changes and dynamic safe-area/banner insets.
- Compact-phone (568x320), baseline phone, and tablet (1024x768) landscape viewport fit without page scrolling.
- Desktop layout checks across the effective 80%, 100%, and 125% browser-zoom viewport range.
- Yandex pause/resume events, BFCache pagehide/pageshow recovery, and visibility/orientation race handling.
- Game Ready ordering: LoadingAPI.ready() exactly once after the loader is hidden and before GameplayAPI.start().
- Native modal gameplay markup: Save/Open/Settings stop gameplay markup and restore it when appropriate.
- Nested native modal stacks remain blocked until the final underlying modal closes.
- Combined orientation + native-modal blockers compose correctly; clearing one blocker does not restart gameplay while the other remains active.
- Platform resume reconciliation while orientation or native-modal blockers are active.
- IndexedDB/IDBFS persistence across page reload.
- Full mobile local save create -> browser -> reopen flow, including restored simulation state.
- RU mobile text input, Backspace/Enter, UTF-8 save names, and IME composition de-duplication.
- Browser console capture with unexpected SEVERE entries rejected.
- Browser smoke screenshots.
- Desktop/mobile performance telemetry for DUST 20k/45k and water+gravity 12k/28k scenes.
- Catastrophic performance regression gates: engine FPS >= 30 and p95 frame time <= 50 ms on CI.
- Browser main-loop timing remains RAF while 30/60 rendering caps and 20/60 simulation caps are exercised through native TPT schedulers.
- Current heavy-scene GitHub-runner baseline is approximately 59.7-60.1 engine FPS with ~16.7-16.8 ms p95.

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
- Verify long press does not open a browser context menu on a real touch device.
- Create a real local save, reload the page, and reopen it on a real device.
- Verify RU and EN in the uploaded Yandex draft.
- Test the real on-screen keyboard/IME on Android or iOS.
- Run a heavy simulation for several minutes on representative hardware and check responsiveness/thermals.
- Confirm the sticky banner/ad configuration, or state in the developer comment that the game is intentionally non-monetized.
