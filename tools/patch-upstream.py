#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
powder = root / "upstream" / "src" / "PowderToy.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"

text = powder.read_text(encoding="utf-8")

include_anchor = "#include <cstdlib>\n"
include_patch = "#include <cstdlib>\n#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n"
if "#include <emscripten.h>" not in text:
    if include_anchor not in text:
        raise SystemExit("PowderToy.cpp include anchor not found")
    text = text.replace(include_anchor, include_patch, 1)

touch_anchor = 'engine.TouchUI = prefs.Get("TouchUI", DEFAULT_TOUCH_UI);'
touch_patch = '''#if defined(__EMSCRIPTEN__)
	// Browser builds run on both desktop and mobile. Upstream defaults TouchUI
	// to false for Emscripten, so choose a mobile-friendly default at runtime.
	const bool browserTouchUI = emscripten_run_script_int(
		"(navigator.maxTouchPoints > 0 || "
		"(window.matchMedia && window.matchMedia('(pointer: coarse)').matches)) ? 1 : 0"
	) != 0;
	engine.TouchUI = prefs.Get("TouchUI", browserTouchUI);
#else
	engine.TouchUI = prefs.Get("TouchUI", DEFAULT_TOUCH_UI);
#endif'''

if "browserTouchUI" not in text:
    if touch_anchor not in text:
        raise SystemExit("PowderToy.cpp TouchUI anchor not found")
    text = text.replace(touch_anchor, touch_patch, 1)

powder.write_text(text, encoding="utf-8")

sdl_text = sdl_emscripten.read_text(encoding="utf-8")
pause_patch = '''

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_PauseMainLoop()
{
	// Flush pending IDBFS writes before stopping the frame loop.
	Platform::MaybeTriggerSyncFs();
	emscripten_pause_main_loop();
}

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_ResumeMainLoop()
{
	emscripten_resume_main_loop();
}
'''

if "YandexWeb_PauseMainLoop" not in sdl_text:
    sdl_text = sdl_text.rstrip() + pause_patch + "\n"

sdl_emscripten.write_text(sdl_text, encoding="utf-8")
print("Applied Yandex Web upstream patches.")
