# Corresponding Source / Исходный код

This Yandex Games build is a modified WebAssembly distribution of **The Powder Toy**.

## English

- Upstream project: The Powder Toy — https://github.com/The-Powder-Toy/The-Powder-Toy
- Upstream source version used by this build: `v100.1.400`
- Yandex/Web port source and build scripts: https://github.com/kalandos240/ThePowderToyWeb
- The Yandex-specific modifications are reproducibly applied by `tools/patch-upstream.py`.
- The build recipe is stored in `.github/workflows/build-yandex.yml`.
- License: GNU General Public License version 3. See `LICENSE`.

To recreate the modified source corresponding to the distributed WebAssembly binary, check out the upstream version above and run the build workflow from this repository. The workflow checks out that exact upstream tag, applies the Yandex/Web patch script, and builds the Emscripten target.

## Русский

Эта версия для Яндекс Игр является модифицированной WebAssembly-сборкой **The Powder Toy**.

- Исходный проект: The Powder Toy — https://github.com/The-Powder-Toy/The-Powder-Toy
- Используемая версия исходного кода: `v100.1.400`
- Исходный код порта и скрипты сборки: https://github.com/kalandos240/ThePowderToyWeb
- Изменения для Web/Яндекс Игр воспроизводимо применяются скриптом `tools/patch-upstream.py`.
- Сценарий сборки находится в `.github/workflows/build-yandex.yml`.
- Лицензия: GNU General Public License version 3. См. файл `LICENSE`.

Чтобы получить модифицированный исходный код, соответствующий распространяемому WebAssembly-бинарнику, используется указанная версия upstream и скрипты данного репозитория.
