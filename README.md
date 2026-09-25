# ThePowderToyWeb

Web/Yandex Games port of **The Powder Toy**.

## Current base

- Upstream: https://github.com/The-Powder-Toy/The-Powder-Toy
- Upstream version pinned for reproducible builds: `v100.1.400`
- Runtime target: WebAssembly / Emscripten
- Distribution target: Yandex Games — desktop and mobile browsers from one WebAssembly build.
- Languages: English and Russian, selected from `ysdk.environment.i18n.lang` with English fallback.
- Browser runtime: pthread-free Emscripten build; the Yandex ZIP does not require `SharedArrayBuffer` or cross-origin isolation.
- License: GPL-3.0. The package includes the license and corresponding-source directions.

## Port architecture

This repository intentionally keeps platform glue separate from upstream game sources.

- `index.html` — Yandex-compatible entry point.
- `src/yandex.js` — non-blocking Yandex Games SDK script loading, safe initialization, late recovery, and gameplay markers.
- `src/main.js` — Emscripten loader and Game Ready bridge.
- `styles.css` — responsive desktop/mobile shell.
- `tools/patch-upstream.py` — applies Yandex/mobile/localization/single-thread changes to the pinned upstream source.
- `tools/browser-smoke.py` — launches the built game in Chrome as desktop/mobile and RU/EN, including blocked and deliberately delayed Yandex SDK startup paths.
- `tools/smoke-http-server.py` — local CI-only server that can delay only `/sdk.js` while serving the game normally; it is never included in the release ZIP.
- `tools/check-runtime-network.py` — fails packaging if authored runtime contains third-party network URLs or if the generated JS/WASM still contains upstream/community service hosts.
- `tools/browser-compat-smoke.py` — runs the exact release ZIP in Firefox and WebKit, including WebKit mobile viewport/orientation checks.
- `.github/workflows/build-yandex.yml` — builds the official upstream Emscripten target, disables upstream HTTP features, verifies the browser runtime, and produces a minimal whitelisted Yandex ZIP artifact without debug/source-map files.

The release game is self-contained and does not use third-party game servers, analytics, CDNs, community services, WebSockets, or upstream The Powder Toy network APIs. The only platform integration is the Yandex Games SDK loaded from the required same-origin path `/sdk.js`. `SOURCE.md` contains plain source-code links for GPL compliance, but it is documentation only and is never requested or opened by the game runtime.

The build loads `/sdk.js` asynchronously and does **not** call Yandex SDK methods before the loader is ready and `YaGames.init()` resolves. Engine JS/WASM startup does not wait for SDK network latency. `LoadingAPI.ready()` is sent only after the native game calls `window.mark_presentable()`. A stalled SDK cannot hold the loader forever: startup falls back after 8 seconds using the browser locale, while the original SDK initialization remains alive. SDK state is reconciled whenever initialization completes, including the race where it resolves after engine startup but before the timeout; the native UI keeps one language for the active session to avoid mixed RU/EN controls.

## Build

Run the **Build Yandex package** workflow in GitHub Actions. The resulting artifact is `ThePowderToy-Yandex.zip`.

For local development, put an Emscripten build in:

```text
game/powder.js
game/powder.wasm
```

and serve the repository over HTTP(S). Outside Yandex Games, missing `/sdk.js` is treated as local-development mode and the game still starts.

## Port status

The platform/bootstrap layer is operational: Yandex SDK initialization, Game Ready, Gameplay API, IndexedDB/IDBFS persistence, desktop/mobile Touch UI selection, responsive viewport/fullscreen handling, EN/RU localization (including core simulation/render settings), no-http UI cleanup, external-link blocking, and pthread-free WebAssembly are integrated.

CI validates Cyrillic glyph coverage, complete Russian descriptions for upstream elements, absence of shared-memory runtime requirements, package size, and browser startup in Desktop EN/RU and Mobile EN/RU. The exact generated release ZIP is also unpacked in a separate compatibility job and launched in Firefox and WebKit; WebKit additionally covers touch/mobile EN/RU and portrait-to-landscape pause/resume transitions. Mobile browser tests exercise real touch drawing, portrait blocking, repeated portrait/landscape transitions, repeated fullscreen-like viewport changes, runtime pause/resume, and IndexedDB/IDBFS persistence. Safe-area canvas sizing is based on the app content box (excluding CSS padding), preventing the intermittent bottom overflow/black-bar class of bug after repeated mobile viewport changes. CI also captures visual smoke screenshots, rejects unexpected severe browser-console errors, verifies Game Ready/gameplay ordering, nested native-modal gameplay state, visibility/orientation races, mobile IME input and save reopening, and records desktop/mobile frame-time telemetry on DUST and water+gravity stress scenes up to 45k/28k particles. The current heavy-scene GitHub-runner baseline is about 59.7-60.1 engine FPS with ~16.7-16.8 ms p95.

The Yandex build removes or blocks upstream online UI/actions and fails CI if visible community links return in the patched GUI. Remaining work is broader low-frequency dialogue/localization polish, heavier gameplay/performance stress testing on representative physical devices, advertising/monetization verification for release, and the final Yandex moderation audit.
