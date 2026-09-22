# ThePowderToyWeb

Web/Yandex Games port of **The Powder Toy**.

## Current base

- Upstream: https://github.com/The-Powder-Toy/The-Powder-Toy
- Upstream version pinned for reproducible builds: `v100.1.400`
- Runtime target: WebAssembly / Emscripten
- Distribution target: Yandex Games (desktop + mobile browsers)
- License: upstream The Powder Toy is GPL-3.0. Built game artifacts must keep the upstream license and notices.

## Port architecture

This repository intentionally keeps platform glue separate from upstream game sources.

- `index.html` — Yandex-compatible entry point.
- `src/yandex.js` — safe Yandex Games SDK initialization and gameplay markers.
- `src/main.js` — Emscripten loader and Game Ready bridge.
- `styles.css` — responsive desktop/mobile shell.
- `.github/workflows/build-yandex.yml` — builds the official upstream Emscripten target, disables upstream HTTP features for the Yandex package, and produces a ZIP artifact.

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

Stage 1 is the platform/bootstrap layer. Remaining work includes full mobile UX validation, save persistence integration, ads/pause flow, localization audit, moderation checks, and performance testing.
