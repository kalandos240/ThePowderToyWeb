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
- `src/yandex.js` — safe Yandex Games SDK initialization and gameplay markers.
- `src/main.js` — Emscripten loader and Game Ready bridge.
- `styles.css` — responsive desktop/mobile shell.
- `tools/patch-upstream.py` — applies Yandex/mobile/localization/single-thread changes to the pinned upstream source.
- `tools/browser-smoke.py` — launches the built game in Chrome as desktop/mobile and RU/EN.
- `.github/workflows/build-yandex.yml` — builds the official upstream Emscripten target, disables upstream HTTP features, verifies the browser runtime, and produces a Yandex ZIP artifact.

The build does **not** call Yandex SDK methods before `YaGames.init()` resolves. `LoadingAPI.ready()` is sent only after the native game calls `window.mark_presentable()`.

## Build

Run the **Build Yandex package** workflow in GitHub Actions. The resulting artifact is `ThePowderToy-Yandex.zip`.

For local development, put an Emscripten build in:

```text
game/powder.js
game/powder.wasm
```

and serve the repository over HTTP(S). Outside Yandex Games, missing `/sdk.js` is treated as local-development mode and the game still starts.

## Port status

The platform/bootstrap layer is operational: Yandex SDK initialization, Game Ready, Gameplay API, IndexedDB/IDBFS persistence, desktop/mobile Touch UI selection, responsive viewport/fullscreen handling, EN/RU localization, no-http UI cleanup, external-link blocking, and pthread-free WebAssembly are integrated.

CI validates Cyrillic glyph coverage, complete Russian descriptions for upstream elements, absence of shared-memory runtime requirements, package size, and browser startup in Desktop EN/RU and Mobile EN/RU. Mobile browser tests exercise real touch drawing, portrait blocking, repeated portrait/landscape transitions, repeated fullscreen-like viewport changes, runtime pause/resume, and IndexedDB/IDBFS persistence. Safe-area canvas sizing is based on the app content box (excluding CSS padding), preventing the intermittent bottom overflow/black-bar class of bug after repeated mobile viewport changes. CI also captures visual smoke screenshots, rejects unexpected severe browser-console errors, verifies Game Ready/gameplay ordering and native-modal gameplay state, exercises mobile IME input and save reopening, and records desktop/mobile frame-time telemetry on DUST and water+gravity stress scenes up to 45k/28k particles. The current heavy-scene GitHub-runner baseline is about 59-60 engine FPS with ~16.7-16.8 ms p95.

The Yandex build removes or blocks upstream online UI/actions and fails CI if visible community links return in the patched GUI. Remaining work is broader dialogue/localization polish, heavier gameplay/performance stress testing on representative devices, advertising/monetization integration if required for release, and final Yandex moderation audit.
