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

CI validates Cyrillic glyph coverage, absence of shared-memory runtime requirements, package size, and browser startup in Desktop EN/RU and Mobile EN/RU. Remaining work is deeper gameplay/mobile interaction testing, broader Russian translation coverage, advertising/monetization integration, performance profiling, and final Yandex moderation audit.
