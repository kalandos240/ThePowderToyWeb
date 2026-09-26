#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
meson = root / "upstream" / "meson.build"
src_meson = root / "upstream" / "src" / "meson.build"
upstream_build_sh = root / "upstream" / ".github" / "build.sh"
powder = root / "upstream" / "src" / "PowderToy.cpp"
powder_sdl = root / "upstream" / "src" / "PowderToySDL.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"
game_view = root / "upstream" / "src" / "gui" / "game" / "GameView.cpp"
local_browser = root / "upstream" / "src" / "gui" / "localbrowser" / "LocalBrowserView.cpp"
local_save = root / "upstream" / "src" / "gui" / "save" / "LocalSaveActivity.cpp"
options_view = root / "upstream" / "src" / "gui" / "options" / "OptionsView.cpp"
simulation_data = root / "upstream" / "src" / "simulation" / "SimulationData.cpp"
local_browser_controller = root / "upstream" / "src" / "gui" / "localbrowser" / "LocalBrowserController.cpp"
engine_cpp = root / "upstream" / "src" / "gui" / "interface" / "Engine.cpp"
engine_h = root / "upstream" / "src" / "gui" / "interface" / "Engine.h"
window_cpp = root / "upstream" / "src" / "gui" / "interface" / "Window.cpp"
component_h = root / "upstream" / "src" / "gui" / "interface" / "Component.h"
button_h = root / "upstream" / "src" / "gui" / "interface" / "Button.h"
checkbox_cpp = root / "upstream" / "src" / "gui" / "interface" / "Checkbox.cpp"
drop_down_cpp = root / "upstream" / "src" / "gui" / "interface" / "DropDown.cpp"
button_cpp = root / "upstream" / "src" / "gui" / "interface" / "Button.cpp"
context_menu_h = root / "upstream" / "src" / "gui" / "interface" / "ContextMenu.h"
textbox_cpp = root / "upstream" / "src" / "gui" / "interface" / "Textbox.cpp"
save_button_cpp = root / "upstream" / "src" / "gui" / "interface" / "SaveButton.cpp"
label_cpp = root / "upstream" / "src" / "gui" / "interface" / "Label.cpp"
copy_text_button_cpp = root / "upstream" / "src" / "gui" / "interface" / "CopyTextButton.cpp"
locale_header = root / "upstream" / "src" / "YandexWebLocale.h"
task_cpp = root / "upstream" / "src" / "tasks" / "Task.cpp"
gravity_cpp = root / "upstream" / "src" / "simulation" / "gravity" / "Fft.cpp"
simulation_cpp = root / "upstream" / "src" / "simulation" / "Simulation.cpp"
simulation_h = root / "upstream" / "src" / "simulation" / "Simulation.h"
editing_cpp = root / "upstream" / "src" / "simulation" / "Editing.cpp"
lua_simulation_cpp = root / "upstream" / "src" / "lua" / "LuaSimulation.cpp"
air_cpp = root / "upstream" / "src" / "simulation" / "Air.cpp"
renderer_cpp = root / "upstream" / "src" / "graphics" / "Renderer.cpp"
renderer_h = root / "upstream" / "src" / "graphics" / "Renderer.h"
game_controller_cpp = root / "upstream" / "src" / "gui" / "game" / "GameController.cpp"
game_model_cpp = root / "upstream" / "src" / "gui" / "game" / "GameModel.cpp"
tool_button_cpp = root / "upstream" / "src" / "gui" / "game" / "ToolButton.cpp"
tool_button_h = root / "upstream" / "src" / "gui" / "game" / "ToolButton.h"
quick_options_cpp = root / "upstream" / "src" / "gui" / "game" / "QuickOptions.cpp"
simtools_dir = root / "upstream" / "src" / "simulation" / "simtools"
elements_dir = root / "upstream" / "src" / "simulation" / "elements"
intro_text_h = root / "upstream" / "src" / "gui" / "game" / "IntroText.h"
property_tool_cpp = root / "upstream" / "src" / "gui" / "game" / "tool" / "PropertyTool.cpp"
sign_tool_cpp = root / "upstream" / "src" / "gui" / "game" / "tool" / "SignTool.cpp"
element_search_cpp = root / "upstream" / "src" / "gui" / "elementsearch" / "ElementSearchActivity.cpp"
render_view_cpp = root / "upstream" / "src" / "gui" / "render" / "RenderView.cpp"
file_browser_cpp = root / "upstream" / "src" / "gui" / "filebrowser" / "FileBrowserActivity.cpp"
colour_picker_cpp = root / "upstream" / "src" / "gui" / "colourpicker" / "ColourPickerActivity.cpp"
confirm_prompt_cpp = root / "upstream" / "src" / "gui" / "dialogues" / "ConfirmPrompt.cpp"
error_message_cpp = root / "upstream" / "src" / "gui" / "dialogues" / "ErrorMessage.cpp"
text_prompt_cpp = root / "upstream" / "src" / "gui" / "dialogues" / "TextPrompt.cpp"
information_message_cpp = root / "upstream" / "src" / "gui" / "dialogues" / "InformationMessage.cpp"
credits_cpp = root / "upstream" / "src" / "gui" / "credits" / "Credits.cpp"
gol_tool_cpp = root / "upstream" / "src" / "gui" / "game" / "tool" / "GOLTool.cpp"
task_window_cpp = root / "upstream" / "src" / "tasks" / "TaskWindow.cpp"
client_cpp = root / "upstream" / "src" / "client" / "Client.cpp"
intro_text = root / "upstream" / "src" / "gui" / "game" / "IntroText.h"
emscripten_platform = root / "upstream" / "src" / "common" / "platform" / "Emscripten.cpp"
lua_script_interface_cpp = root / "upstream" / "src" / "lua" / "LuaScriptInterface.cpp"
lua_misc_cpp = root / "upstream" / "src" / "lua" / "LuaMisc.cpp"
lua_platform_cpp = root / "upstream" / "src" / "lua" / "LuaPlatform.cpp"

meson_text = meson.read_text(encoding="utf-8")
pthread_arg = "\t\t'-s', 'USE_PTHREADS',\n"
if pthread_arg not in meson_text:
    raise SystemExit("meson.build USE_PTHREADS anchor not found")
meson_text = meson_text.replace(pthread_arg, "", 1)

threads_anchor = """fftw_dep = dependency('fftw3f', static: is_static)
threads_dep = dependency('threads')
if host_platform == 'emscripten'"""
threads_patch = """fftw_dep = dependency('fftw3f', static: is_static)
threads_dep = []
if host_platform != 'emscripten'
\tthreads_dep = dependency('threads')
endif
if host_platform == 'emscripten'"""
if threads_anchor not in meson_text:
    raise SystemExit("meson.build threads dependency anchor not found")
meson_text = meson_text.replace(threads_anchor, threads_patch, 1)

thread_callback_arg = "\t\t'-Wl,-u,_emscripten_run_callback_on_thread',\n"
if thread_callback_arg in meson_text:
    meson_text = meson_text.replace(thread_callback_arg, "", 1)

meson.write_text(meson_text, encoding="utf-8")

# Yandex Web/no-HTTP: strip upstream server constants from the generated
# Config.h/WASM entirely. NOHTTP already disables the transport, but leaving
# the default powdertoy.co.uk strings embedded in the binary violates the
# self-contained release policy and makes static network audits ambiguous.
src_meson_text = src_meson.read_text(encoding="utf-8")
server_config_anchor = """enforce_https = get_option('enforce_https')
server = get_option('server')
static_server = get_option('static_server')
update_server = get_option('update_server')

if not (server.startswith('http://') or server.startswith('https://'))
	server = 'https://' + server
endif
if server.startswith('http://') and enforce_https
	error('enforce_https is true but server is a http:// URL base')
endif
if not (static_server.startswith('http://') or static_server.startswith('https://'))
	static_server = 'https://' + static_server
endif
if static_server.startswith('http://') and enforce_https
	error('enforce_https is true but static_server is a http:// URL base')
endif
"""
server_config_patch = """enforce_https = get_option('enforce_https')
server = get_option('server')
static_server = get_option('static_server')
update_server = get_option('update_server')

if host_platform == 'emscripten' and not get_option('http')
	# Yandex Web is deliberately serverless apart from the platform SDK.
	server = ''
	static_server = ''
else
	if not (server.startswith('http://') or server.startswith('https://'))
		server = 'https://' + server
	endif
	if server.startswith('http://') and enforce_https
		error('enforce_https is true but server is a http:// URL base')
	endif
	if not (static_server.startswith('http://') or static_server.startswith('https://'))
		static_server = 'https://' + static_server
	endif
	if static_server.startswith('http://') and enforce_https
		error('enforce_https is true but static_server is a http:// URL base')
	endif
endif
"""
if server_config_anchor not in src_meson_text:
    raise SystemExit("src/meson.build server configuration anchor missing")
src_meson_text = src_meson_text.replace(
    server_config_anchor,
    server_config_patch,
    1,
)
src_meson.write_text(src_meson_text, encoding="utf-8")

# Browser fullscreen belongs to the Yandex/player container. Keep every native
# TPT fullscreen entry point (F11, Options, Lua) from mutating Engine state.
engine_h_text = engine_h.read_text(encoding="utf-8")
fullscreen_set_anchor = "void SetFullscreen         (bool newFullscreen         ) { windowFrameOps.fullscreen          = newFullscreen;          }"
fullscreen_set_patch = """void SetFullscreen         (bool newFullscreen         )
		{
#if defined(__EMSCRIPTEN__)
			(void)newFullscreen;
			windowFrameOps.fullscreen = false;
#else
			windowFrameOps.fullscreen = newFullscreen;
#endif
		}"""
if fullscreen_set_anchor not in engine_h_text:
    raise SystemExit("Engine.h SetFullscreen anchor missing")
engine_h_text = engine_h_text.replace(fullscreen_set_anchor, fullscreen_set_patch, 1)

fullscreen_get_anchor = "bool GetFullscreen         () const { return windowFrameOps.fullscreen;          }"
fullscreen_get_patch = """bool GetFullscreen         () const
		{
#if defined(__EMSCRIPTEN__)
			return false;
#else
			return windowFrameOps.fullscreen;
#endif
		}"""
if fullscreen_get_anchor not in engine_h_text:
    raise SystemExit("Engine.h GetFullscreen anchor missing")
engine_h_text = engine_h_text.replace(fullscreen_get_anchor, fullscreen_get_patch, 1)
engine_h.write_text(engine_h_text, encoding="utf-8")

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
	EM_ASM({ window.tptTouchUIDetected = !!$0; }, browserTouchUI ? 1 : 0);
	engine.TouchUI = prefs.Get("TouchUI", browserTouchUI);
#else
	engine.TouchUI = prefs.Get("TouchUI", DEFAULT_TOUCH_UI);
#endif'''

if "browserTouchUI" not in text:
    if touch_anchor not in text:
        raise SystemExit("PowderToy.cpp TouchUI anchor not found")
    text = text.replace(touch_anchor, touch_patch, 1)

powder.write_text(text, encoding="utf-8")

# SDL2's Emscripten backend does not reliably summon a mobile browser
# keyboard. Keep TPT's native Textbox/SDL event path, but notify the web shell
# when text input is active and where the focused input rectangle is.
powder_sdl_text = powder_sdl.read_text(encoding="utf-8")
if "#include <emscripten.h>" not in powder_sdl_text:
    powder_sdl_text = powder_sdl_text.replace(
        '#include <iostream>\n',
        '#include <iostream>\n#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n',
        1,
    )

start_text_input_anchor = """void StartTextInput()
{
\tSDL_StartTextInput();
}"""
start_text_input_patch = """void StartTextInput()
{
\tSDL_StartTextInput();
#if defined(__EMSCRIPTEN__)
\tEM_ASM({
\t\tif (window.__tptMobileTextBridge)
\t\t\twindow.__tptMobileTextBridge.start();
\t});
#endif
}"""
if "window.__tptMobileTextBridge.start()" not in powder_sdl_text:
    if start_text_input_anchor not in powder_sdl_text:
        raise SystemExit("PowderToySDL.cpp StartTextInput anchor missing")
    powder_sdl_text = powder_sdl_text.replace(
        start_text_input_anchor, start_text_input_patch, 1
    )

stop_text_input_anchor = """void StopTextInput()
{
\tSDL_StopTextInput();
}"""
stop_text_input_patch = """void StopTextInput()
{
\tSDL_StopTextInput();
#if defined(__EMSCRIPTEN__)
\tEM_ASM({
\t\tif (window.__tptMobileTextBridge)
\t\t\twindow.__tptMobileTextBridge.stop();
\t});
#endif
}"""
if "window.__tptMobileTextBridge.stop()" not in powder_sdl_text:
    if stop_text_input_anchor not in powder_sdl_text:
        raise SystemExit("PowderToySDL.cpp StopTextInput anchor missing")
    powder_sdl_text = powder_sdl_text.replace(
        stop_text_input_anchor, stop_text_input_patch, 1
    )

text_rect_anchor = "\tSDL_SetTextInputRect(&rect);\n"
text_rect_patch = """\tSDL_SetTextInputRect(&rect);
#if defined(__EMSCRIPTEN__)
\tEM_ASM({
\t\tif (window.__tptMobileTextBridge)
\t\t\twindow.__tptMobileTextBridge.setRect($0, $1, $2, $3);
\t}, rect.x, rect.y, rect.w, rect.h);
#endif
"""
if "window.__tptMobileTextBridge.setRect" not in powder_sdl_text:
    if text_rect_anchor not in powder_sdl_text:
        raise SystemExit("PowderToySDL.cpp text-input rect anchor missing")
    powder_sdl_text = powder_sdl_text.replace(
        text_rect_anchor, text_rect_patch, 1
    )

powder_sdl.write_text(powder_sdl_text, encoding="utf-8")

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

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestMainLoopUsesRAF()
{
	int mode = -1;
	int value = -1;
	emscripten_get_main_loop_timing(&mode, &value);
	return mode == EM_TIMING_RAF && value == 1 ? 1 : 0;
}

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_PushTextInput(const char *text)
{
	if (!text || !*text)
		return;

	SDL_Event event{};
	event.type = SDL_TEXTINPUT;
	SDL_strlcpy(event.text.text, text, sizeof(event.text.text));
	SDL_PushEvent(&event);
}

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_PushKey(int keycode)
{
	SDL_Event down{};
	down.type = SDL_KEYDOWN;
	down.key.state = SDL_PRESSED;
	down.key.repeat = 0;
	down.key.keysym.sym = (SDL_Keycode)keycode;
	down.key.keysym.scancode = SDL_GetScancodeFromKey((SDL_Keycode)keycode);
	down.key.keysym.mod = KMOD_NONE;
	SDL_PushEvent(&down);

	SDL_Event up = down;
	up.type = SDL_KEYUP;
	up.key.state = SDL_RELEASED;
	SDL_PushEvent(&up);
}

static ui::Point YandexWeb_TestLogicalToWindowPoint(int x, int y)
{
	int wx = x;
	int wy = y;
#if SDL_VERSION_ATLEAST(2, 0, 18)
	if (sdl_renderer)
		SDL_RenderLogicalToWindow(sdl_renderer, float(x), float(y), &wx, &wy);
#else
	if (sdl_renderer)
	{
		SDL_Rect viewport{};
		int logicalWidth = 0;
		int logicalHeight = 0;
		SDL_RenderGetViewport(sdl_renderer, &viewport);
		SDL_RenderGetLogicalSize(sdl_renderer, &logicalWidth, &logicalHeight);
		if (logicalWidth > 0 && logicalHeight > 0)
		{
			wx = viewport.x + int(float(x) * float(viewport.w) / float(logicalWidth));
			wy = viewport.y + int(float(y) * float(viewport.h) / float(logicalHeight));
		}
	}
#endif
	return ui::Point(wx, wy);
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestLogicalToWindowX(int x, int y)
{
	return YandexWeb_TestLogicalToWindowPoint(x, y).X;
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestLogicalToWindowY(int x, int y)
{
	return YandexWeb_TestLogicalToWindowPoint(x, y).Y;
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestWindowWidth()
{
	int width = 0;
	int height = 0;
	if (sdl_window)
		SDL_GetWindowSize(sdl_window, &width, &height);
	return width;
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestWindowHeight()
{
	int width = 0;
	int height = 0;
	if (sdl_window)
		SDL_GetWindowSize(sdl_window, &width, &height);
	return height;
}


EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_TestStorageWrite()
{
	EM_ASM({
		window.__tptStorageFlushed = false;
		FS.writeFile('/powder/.yandex-storage-test', 'tpt-yandex-storage-ok');
		FS.syncfs(false, err => {
			window.__tptStorageFlushError = err ? String(err) : '';
			window.__tptStorageFlushed = !err;
		});
	});
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestStorageRead()
{
	return EM_ASM_INT({
		try {
			return UTF8ArrayToString(FS.readFile('/powder/.yandex-storage-test')) === 'tpt-yandex-storage-ok' ? 1 : 0;
		} catch (e) {
			return 0;
		}
	});
}

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_TestStorageFlush()
{
	EM_ASM({
		window.__tptStorageFlushed = false;
		window.__tptStorageFlushError = '';
		FS.syncfs(false, err => {
			window.__tptStorageFlushError = err ? String(err) : '';
			window.__tptStorageFlushed = !err;
		});
	});
}

EMSCRIPTEN_KEEPALIVE extern "C" int YandexWeb_TestLocalSaveFileSize(const char *filename)
{
	return EM_ASM_INT({
		try {
			const filename = UTF8ToString($0);
			return FS.stat('/powder/Saves/' + filename + '.cps').size | 0;
		} catch (e) {
			return -1;
		}
	}, filename);
}

EMSCRIPTEN_KEEPALIVE extern "C" void YandexWeb_TestRemoveLocalSaveFile(const char *filename)
{
	EM_ASM({
		try {
			const filename = UTF8ToString($0);
			FS.unlink('/powder/Saves/' + filename + '.cps');
		} catch (e) {
			// Missing file is the expected clean-start state.
		}
	}, filename);
}
'''

if "YandexWeb_PauseMainLoop" not in sdl_text:
    sdl_text = sdl_text.rstrip() + pause_patch + "\n"

fps_loop_anchor = r'''void ApplyFpsLimit()
{
	static bool mainLoopSet = false;
	if (!mainLoopSet)
	{
		emscripten_set_main_loop(MainLoopBody, 0, 0);
		mainLoopSet = true;
	}
	// this generally attempts to replicate the behaviour of EngineProcess
	std::optional<float> drawLimit;
	auto &engine = ui::Engine::Ref();
	auto fpsLimit = engine.GetFpsLimit();
	if (auto *fpsLimitExplicit = std::get_if<FpsLimitExplicit>(&fpsLimit))
	{
		drawLimit = fpsLimitExplicit->value;
	}
	else if (std::holds_alternative<FpsLimitFollowDraw>(fpsLimit))
	{
		auto effectiveDrawLimit = engine.GetEffectiveDrawCap();
		if (effectiveDrawLimit)
		{
			drawLimit = float(*effectiveDrawLimit);
		}
		// else // TODO: DrawLimitVsync
		// {
		// 	if (std::holds_alternative<DrawLimitVsync>(engine.GetDrawingFrequencyLimit()))
		// 	{
		// 		emscripten_set_main_loop_timing(EM_TIMING_RAF, 1);
		// 		std::cerr << "implicit fps limit via vsync" << std::endl;
		// 		return;
		// 	}
		// }
	}
	int delay = 0; // no cap
	if (drawLimit.has_value())
	{
		delay = int(1000.f / *drawLimit);
	}
	emscripten_set_main_loop_timing(EM_TIMING_SETTIMEOUT, delay);
	std::cerr << "explicit fps limit: " << delay << "ms delays" << std::endl;
}

// Is actually only called once at startup, the real main loop body is MainLoopBody.
void MainLoop()
{
	ApplyFpsLimit();
	MainLoopBody();
}'''

fps_loop_patch = r'''void ApplyFpsLimit()
{
	// EngineProcess already applies drawSchedule/tickSchedule caps for
	// rendering and simulation independently. Emscripten timing must not be
	// changed from UI/window setup paths before the browser main loop exists.
}

void MainLoop()
{
	// MainLoop is the one-shot startup entrypoint. Create the browser pump here,
	// after native UI initialization, rather than from Engine::ShowWindow().
	emscripten_set_main_loop(MainLoopBody, 0, 0);
	std::cerr << "web main loop via requestAnimationFrame" << std::endl;
	MainLoopBody();
}'''

if 'web main loop via requestAnimationFrame' not in sdl_text:
    if fps_loop_anchor not in sdl_text:
        raise SystemExit("PowderToySDLEmscripten.cpp ApplyFpsLimit anchor missing")
    sdl_text = sdl_text.replace(fps_loop_anchor, fps_loop_patch, 1)

if "emscripten_set_main_loop_timing" in sdl_text:
    raise SystemExit(
        "Yandex Web must keep the Emscripten browser main loop on requestAnimationFrame"
    )
if sdl_text.count("emscripten_set_main_loop(MainLoopBody, 0, 0);") != 1:
    raise SystemExit("Yandex Web must have exactly one RAF main-loop setup")
if "void ApplyFpsLimit()\n{\n\t// EngineProcess already applies" not in sdl_text:
    raise SystemExit("Yandex Web ApplyFpsLimit must not own browser timing")

sdl_emscripten.write_text(sdl_text, encoding="utf-8")

platform_text = emscripten_platform.read_text(encoding="utf-8")

# Robust browser startup: upstream defers Main() until the initial IDBFS
# populate callback fires. In some Chromium/IDBFS startup states that callback
# can be lost even though the Emscripten module itself is already initialized,
# leaving the page forever on the loader. Keep the normal populate path, but
# make MainJs idempotent and arm a one-shot fallback.
invoke_main_anchor = """int InvokeMain(int argc, char *argv[])
{
	EM_ASM({
		FS.syncfs(true, () => {
			Module.ccall('MainJs', 'number', [ 'number', 'number' ], [ $0, $1 ]);
		});
	}, argc, argv);
	return 0;
}"""
invoke_main_patch = """int InvokeMain(int argc, char *argv[])
{
	EM_ASM({
		const startMain = () => {
			Module.ccall('MainJs', 'number', [ 'number', 'number' ], [ $0, $1 ]);
		};
		const fallback = setTimeout(startMain, 5000);
		FS.syncfs(true, () => {
			clearTimeout(fallback);
			startMain();
		});
	}, argc, argv);
	return 0;
}"""
if invoke_main_anchor not in platform_text:
    raise SystemExit("Emscripten.cpp InvokeMain startup anchor missing")
platform_text = platform_text.replace(invoke_main_anchor, invoke_main_patch, 1)

main_js_anchor = """EMSCRIPTEN_KEEPALIVE extern "C" int MainJs(int argc, char *argv[])
{
	return Main(argc, argv);
}"""
main_js_patch = """EMSCRIPTEN_KEEPALIVE extern "C" int MainJs(int argc, char *argv[])
{
	static bool yandexWebMainStarted = false;
	if (yandexWebMainStarted)
		return 0;
	yandexWebMainStarted = true;
	return Main(argc, argv);
}"""
if main_js_anchor not in platform_text:
    raise SystemExit("Emscripten.cpp MainJs startup guard anchor missing")
platform_text = platform_text.replace(main_js_anchor, main_js_patch, 1)

open_uri_anchor = """void OpenURI(ByteString uri)
{
	EM_ASM({
		open(UTF8ToString($0));
	}, uri.c_str());
}"""
open_uri_patch = """void OpenURI(ByteString uri)
{
	// Yandex Web: external URI navigation is disabled.
	(void)uri;
	std::cerr << "External URI blocked in Yandex build." << std::endl;
}"""
if "external URI navigation is disabled" not in platform_text:
    if open_uri_anchor not in platform_text:
        raise SystemExit("Emscripten.cpp OpenURI anchor not found")
    platform_text = platform_text.replace(open_uri_anchor, open_uri_patch, 1)
emscripten_platform.write_text(platform_text, encoding="utf-8")

# Yandex Web: the game must never expose network-capable Lua APIs. NOHTTP
# already selects LuaSocketTCPNone.cpp, but upstream still registers the
# generic http table and the script-manager downloader. Remove both from the
# Emscripten build so scripts cannot even attempt external HTTP requests.
lua_script_text = lua_script_interface_cpp.read_text(encoding="utf-8")
lua_http_open_anchor = "\tLuaHttp::Open(L);"
lua_http_open_patch = """#if !defined(__EMSCRIPTEN__)
\tLuaHttp::Open(L);
#endif"""
if "Yandex Web: Lua HTTP API disabled" not in lua_script_text:
    if lua_http_open_anchor not in lua_script_text:
        raise SystemExit("LuaScriptInterface.cpp LuaHttp::Open anchor missing")
    lua_script_text = lua_script_text.replace(
        lua_http_open_anchor,
        "// Yandex Web: Lua HTTP API disabled in browser builds.\n" + lua_http_open_patch,
        1,
    )
# Export a runtime diagnostic so browser smoke can prove the final Lua state
# does not expose any network/navigation API after the native engine starts.
if "#include <emscripten.h>" not in lua_script_text:
    lua_include_anchor = '#include "simulation/SimulationData.h"\n'
    if lua_include_anchor not in lua_script_text:
        raise SystemExit("LuaScriptInterface.cpp Emscripten include anchor missing")
    lua_script_text = lua_script_text.replace(
        lua_include_anchor,
        lua_include_anchor + "#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n",
        1,
    )

lua_ctor_anchor = "LuaScriptInterface::LuaScriptInterface(GameController *newGameController, GameModel *newGameModel) :\n"
lua_network_diag = r'''#if defined(__EMSCRIPTEN__)
static int YandexWeb_TestLuaNetworkApiMaskValue = -1;
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestLuaNetworkApiMask()
{
	return YandexWeb_TestLuaNetworkApiMaskValue;
}
#endif

'''
if "YandexWeb_TestLuaNetworkApiMask()" not in lua_script_text:
    if lua_ctor_anchor not in lua_script_text:
        raise SystemExit("LuaScriptInterface.cpp constructor anchor missing")
    lua_script_text = lua_script_text.replace(
        lua_ctor_anchor,
        lua_network_diag + lua_ctor_anchor,
        1,
    )

lua_open_end_anchor = """	LuaSocket::Open(L);
	LuaTools::Open(L);
	{
		lua_getglobal(L, "os");"""
lua_open_end_patch = r'''	LuaSocket::Open(L);
	LuaTools::Open(L);
#if defined(__EMSCRIPTEN__)
	// Bit 0: global http table
	// Bit 1: tpt.installScriptManager
	// Bit 2: platform.openLink
	// Bit 3: socket.tcp
	YandexWeb_TestLuaNetworkApiMaskValue = 0;

	auto hasGlobal = [this](const char *name) {
		lua_getglobal(L, name);
		bool present = !lua_isnil(L, -1);
		lua_pop(L, 1);
		return present;
	};
	auto hasField = [this](const char *globalName, const char *fieldName) {
		lua_getglobal(L, globalName);
		bool present = false;
		if (lua_istable(L, -1))
		{
			lua_getfield(L, -1, fieldName);
			present = !lua_isnil(L, -1);
			lua_pop(L, 1);
		}
		lua_pop(L, 1);
		return present;
	};

	if (hasGlobal("http"))
		YandexWeb_TestLuaNetworkApiMaskValue |= 1;
	if (hasField("tpt", "installScriptManager"))
		YandexWeb_TestLuaNetworkApiMaskValue |= 2;
	if (hasField("platform", "openLink"))
		YandexWeb_TestLuaNetworkApiMaskValue |= 4;
	if (hasField("socket", "tcp"))
		YandexWeb_TestLuaNetworkApiMaskValue |= 8;
#endif
	{
		lua_getglobal(L, "os");'''
if "YandexWeb_TestLuaNetworkApiMaskValue |= 8;" not in lua_script_text:
    if lua_open_end_anchor not in lua_script_text:
        raise SystemExit("LuaScriptInterface.cpp Lua API diagnostic anchor missing")
    lua_script_text = lua_script_text.replace(
        lua_open_end_anchor,
        lua_open_end_patch,
        1,
    )

lua_script_interface_cpp.write_text(lua_script_text, encoding="utf-8")

lua_misc_text = lua_misc_cpp.read_text(encoding="utf-8")
install_manager_anchor = "static int installScriptManager(lua_State *L)\n{"
if "#if !defined(__EMSCRIPTEN__)\nstatic int installScriptManager" not in lua_misc_text:
    if install_manager_anchor not in lua_misc_text:
        raise SystemExit("LuaMisc.cpp installScriptManager anchor missing")
    lua_misc_text = lua_misc_text.replace(
        install_manager_anchor,
        "#if !defined(__EMSCRIPTEN__)\n" + install_manager_anchor,
        1,
    )

    install_manager_end_anchor = """\treturn 0;
}

void LuaMisc::Tick(lua_State *L)"""
    if install_manager_end_anchor not in lua_misc_text:
        raise SystemExit("LuaMisc.cpp installScriptManager end anchor missing")
    lua_misc_text = lua_misc_text.replace(
        install_manager_end_anchor,
        """\treturn 0;
}
#endif

void LuaMisc::Tick(lua_State *L)""",
        1,
    )

registration_anchor = "\t\tLFUNC(installScriptManager),"
if "#if !defined(__EMSCRIPTEN__)\n\t\tLFUNC(installScriptManager)," not in lua_misc_text:
    if registration_anchor not in lua_misc_text:
        raise SystemExit("LuaMisc.cpp installScriptManager registration anchor missing")
    lua_misc_text = lua_misc_text.replace(
        registration_anchor,
        "#if !defined(__EMSCRIPTEN__)\n" + registration_anchor + "\n#endif",
        1,
    )
lua_misc_cpp.write_text(lua_misc_text, encoding="utf-8")

lua_platform_text = lua_platform_cpp.read_text(encoding="utf-8")
open_link_anchor = """static int openLink(lua_State *L)
{
	GetLSI()->AssertInterfaceEvent();
	auto uri = tpt_lua_checkByteString(L, 1);
	Platform::OpenURI(uri);
	return 0;
}"""
if "#if !defined(__EMSCRIPTEN__)\nstatic int openLink" not in lua_platform_text:
    if open_link_anchor not in lua_platform_text:
        raise SystemExit("LuaPlatform.cpp openLink anchor missing")
    lua_platform_text = lua_platform_text.replace(
        open_link_anchor,
        "#if !defined(__EMSCRIPTEN__)\n" + open_link_anchor + "\n#endif",
        1,
    )

open_link_registration = "\t\tLFUNC(openLink),"
if "#if !defined(__EMSCRIPTEN__)\n\t\tLFUNC(openLink)," not in lua_platform_text:
    if open_link_registration not in lua_platform_text:
        raise SystemExit("LuaPlatform.cpp openLink registration anchor missing")
    lua_platform_text = lua_platform_text.replace(
        open_link_registration,
        "#if !defined(__EMSCRIPTEN__)\n" + open_link_registration + "\n#endif",
        1,
    )
lua_platform_cpp.write_text(lua_platform_text, encoding="utf-8")

print("Applied Yandex Web upstream patches.")


game_view_text = game_view.read_text(encoding="utf-8")

search_anchor = '''	searchButton->SetActionCallback({ [this] {
		if (CtrlBehaviour())
			c->OpenLocalBrowse();
		else
			c->OpenSearch("");
	} });'''
search_patch = '''	// Yandex Web: local-only search. The build intentionally disables HTTP.
	searchButton->SetToolTip("Open a local simulation.");
	searchButton->SetActionCallback({ [this] {
		c->OpenLocalBrowse();
	} });'''

if "Yandex Web: local-only search" not in game_view_text:
    if search_anchor not in game_view_text:
        raise SystemExit("GameView.cpp search button anchor not found")
    game_view_text = game_view_text.replace(search_anchor, search_patch, 1)

login_anchor = "	AddComponent(loginButton);"
login_patch = '''	AddComponent(loginButton);
	// Yandex Web has no connection to the upstream account/server backend.
	loginButton->Visible = false;'''

if "loginButton->Visible = false;" not in game_view_text:
    if login_anchor not in game_view_text:
        raise SystemExit("GameView.cpp login button anchor not found")
    game_view_text = game_view_text.replace(login_anchor, login_patch, 1)

game_view.write_text(game_view_text, encoding="utf-8")


# Yandex Web: hide upstream server-only controls and use browser-local wording.
game_view_text = game_view.read_text(encoding="utf-8")

server_controls_anchor = """	ResetVoteButtons();

	tagSimulationButton = new ui::Button"""
server_controls_patch = """	ResetVoteButtons();
	// Yandex Web: hide upstream server-only controls.
	upVoteButton->Visible = false;
	downVoteButton->Visible = false;

	tagSimulationButton = new ui::Button"""
if "Yandex Web: hide upstream server-only controls" not in game_view_text:
    if server_controls_anchor not in game_view_text:
        raise SystemExit("GameView.cpp server controls anchor not found")
    game_view_text = game_view_text.replace(server_controls_anchor, server_controls_patch, 1)

tag_add_anchor = "	AddComponent(tagSimulationButton);"
tag_add_patch = """	AddComponent(tagSimulationButton);
	tagSimulationButton->Visible = false;"""
if "tagSimulationButton->Visible = false;" not in game_view_text:
    if tag_add_anchor not in game_view_text:
        raise SystemExit("GameView.cpp tag button anchor not found")
    game_view_text = game_view_text.replace(tag_add_anchor, tag_add_patch, 1)

game_view_text = game_view_text.replace(
    "Overwrite the open simulation on your hard drive.",
    "Overwrite the open local simulation."
)
game_view_text = game_view_text.replace(
    "Save the simulation to your hard drive. Login to save online.",
    "Save the simulation locally in this browser."
)
game_view_text = game_view_text.replace(
    "Save the simulation to your hard drive.",
    "Save the simulation locally in this browser."
)

game_view.write_text(game_view_text, encoding="utf-8")


# Browser performance: remember whether the freshly rebuilt pmap contains
# any cell that can possibly trigger CheckStacking. This lets the Web build
# skip a full XRES*YRES scan on normal non-stacked frames.
simulation_h_text = simulation_h.read_text(encoding="utf-8")
wall_state_anchor = """	unsigned char bmap[YCELLS][XCELLS];
	unsigned char emap[YCELLS][XCELLS];

	Parts parts;"""
wall_state_patch = """	unsigned char bmap[YCELLS][XCELLS];
	unsigned char emap[YCELLS][XCELLS];

	// Yandex Web renderer hints. The existing BeforeSim wall/air scan is the
	// authoritative producer. Paused mutation paths mark the sparse cache dirty
	// so DrawWalls can safely fall back to the upstream full-grid traversal.
	bool yandexWebWallsMayExist = true;
	bool yandexWebWallCellsDirty = true;
	std::vector<int> yandexWebWallCells;

	Parts parts;"""
if wall_state_anchor not in simulation_h_text:
    raise SystemExit("Simulation.h wall-presence state anchor missing")
simulation_h_text = simulation_h_text.replace(
    wall_state_anchor, wall_state_patch, 1
)

stacking_member_anchor = "\tbool force_stacking_check = false;\n"
stacking_member_patch = (
    "\tbool force_stacking_check = false;\n"
    "\tbool yandexWebGravityMassDirty = false;\n"
    "\tbool yandexWebStackingCandidate = false;\n"
    "\tstd::vector<int> yandexWebStackingCells;\n"
    "\tstd::vector<int> yandexWebCountedCells;\n"
)
if stacking_member_anchor not in simulation_h_text:
    raise SystemExit("Simulation.h stacking candidate anchor missing")
simulation_h_text = simulation_h_text.replace(
    stacking_member_anchor, stacking_member_patch, 1
)
recalc_decl_anchor = "\tvoid RecalcFreeParticles(bool do_life_dec);\n"
recalc_decl_patch = (
    "\tvoid RecalcFreeParticles(bool do_life_dec);\n"
    "\tvoid RebuildStackingCounts();\n"
)
if recalc_decl_anchor not in simulation_h_text:
    raise SystemExit("Simulation.h RecalcFreeParticles declaration anchor missing")
simulation_h_text = simulation_h_text.replace(
    recalc_decl_anchor, recalc_decl_patch, 1
)
simulation_h.write_text(simulation_h_text, encoding="utf-8")

# Browser performance: avoid a second full particle-array scan when
# RecalcFreeParticles observed no holes/deaths. Parts::Flatten() only rebuilds
# the free list and trims the active tail, so it is a no-op for a dense array.
simulation_text = simulation_cpp.read_text(encoding="utf-8")
recalc_start = """void Simulation::RecalcFreeParticles(bool do_life_dec)
{
	FrameTime::Span span(frameTime, "Simulation::RecalcFreeParticles");
	memset(pmap, 0, sizeof(pmap));"""
recalc_start_patch = """void Simulation::RecalcFreeParticles(bool do_life_dec)
{
	FrameTime::Span span(frameTime, "Simulation::RecalcFreeParticles");
	bool yandexWebNeedsFlatten = false;


	memset(pmap, 0, sizeof(pmap));"""
if recalc_start not in simulation_text:
    raise SystemExit("RecalcFreeParticles start anchor missing")
simulation_text = simulation_text.replace(recalc_start, recalc_start_patch, 1)

recalc_pos = simulation_text.find("void Simulation::RecalcFreeParticles")
recalc_end = simulation_text.find("\nvoid Parts::Flatten()", recalc_pos)
if recalc_pos < 0 or recalc_end < 0:
    raise SystemExit("RecalcFreeParticles function bounds missing")
segment = simulation_text[recalc_pos:recalc_end]

count_reset_anchor = """	memset(pmap_count, 0, sizeof(pmap_count));"""
if count_reset_anchor not in segment:
    raise SystemExit("RecalcFreeParticles pmap_count memset anchor missing")
segment = segment.replace(count_reset_anchor, "", 1)

count_anchor = """				if (t!=PT_THDR && t!=PT_EMBR && t!=PT_FIGH && t!=PT_PLSM)
					pmap_count[y][x]++;"""
if count_anchor not in segment:
    raise SystemExit("RecalcFreeParticles pmap_count increment anchor missing")
segment = segment.replace(count_anchor, "", 1)

empty_anchor = """		if (!parts[i].type)
		{
			continue;
		}"""
empty_patch = """		if (!parts[i].type)
		{
			yandexWebNeedsFlatten = true;
			continue;
		}"""
if empty_anchor not in segment:
    raise SystemExit("RecalcFreeParticles empty-particle anchor missing")
segment = segment.replace(empty_anchor, empty_patch, 1)

for kill_anchor in [
    """				kill_part(i);
				continue;""",
]:
    # Both life-expiry branches use the same sequence. Mark each occurrence
    # strictly inside RecalcFreeParticles before continuing.
    count = segment.count(kill_anchor)
    if count < 2:
        raise SystemExit(
            f"Expected at least two RecalcFreeParticles kill anchors, found {count}"
        )
    segment = segment.replace(
        kill_anchor,
        """				yandexWebNeedsFlatten = true;
				kill_part(i);
				continue;"""
    )
    simulation_text = (
        simulation_text[:recalc_pos] + segment + simulation_text[recalc_end:]
    )

flatten_anchor = """	parts.Flatten();
	if (elementRecount)"""
flatten_patch = """	if (yandexWebNeedsFlatten)
		parts.Flatten();
	if (elementRecount)"""
if flatten_anchor not in simulation_text:
    raise SystemExit("RecalcFreeParticles Flatten anchor missing")
simulation_text = simulation_text.replace(flatten_anchor, flatten_patch, 1)

stacking_rebuild_anchor = """void Simulation::CheckStacking()
{"""
stacking_rebuild_patch = """void Simulation::RebuildStackingCounts()
{
	for (int cell : yandexWebCountedCells)
		pmap_count[cell / XRES][cell % XRES] = 0;
	yandexWebCountedCells.clear();
	yandexWebStackingCells.clear();
	yandexWebStackingCandidate = false;

	auto &elements = SimulationData::CRef().elements;
	for (int i = 0; i < parts.active; ++i)
	{
		int t = parts[i].type;
		if (t <= PT_NONE || t >= PT_NUM)
			continue;
		if (elements[t].Properties & TYPE_ENERGY)
			continue;
		if (t == PT_THDR || t == PT_EMBR || t == PT_FIGH || t == PT_PLSM)
			continue;

		int x = int(parts[i].x + 0.5f);
		int y = int(parts[i].y + 0.5f);
		if (x < 0 || y < 0 || x >= XRES || y >= YRES)
			continue;

		auto &cellCount = pmap_count[y][x];
		if (cellCount == 0)
			yandexWebCountedCells.push_back(y * XRES + x);
		cellCount++;
		if (cellCount == 6)
		{
			yandexWebStackingCandidate = true;
			yandexWebStackingCells.push_back(y * XRES + x);
		}
	}
}

void Simulation::CheckStacking()
{"""
if stacking_rebuild_anchor not in simulation_text:
    raise SystemExit("Simulation::CheckStacking insertion anchor missing")
simulation_text = simulation_text.replace(
    stacking_rebuild_anchor, stacking_rebuild_patch, 1
)

stacking_anchor = """void Simulation::CheckStacking()
{
	auto &sd = SimulationData::CRef();
	auto &elements = sd.elements;
	bool excessive_stacking_found = false;
	force_stacking_check = false;"""
stacking_patch = """void Simulation::CheckStacking()
{
	auto &sd = SimulationData::CRef();
	auto &elements = sd.elements;
	bool excessive_stacking_found = false;
	force_stacking_check = false;

	// Yandex Web: RecalcFreeParticles already observed the exact >5 threshold.
	// With no candidate, the full simulation-grid scan cannot find stacking.
	if (!yandexWebStackingCandidate)
		return;"""
if stacking_anchor not in simulation_text:
    raise SystemExit("Simulation::CheckStacking fast-path anchor missing")
simulation_text = simulation_text.replace(stacking_anchor, stacking_patch, 1)

stacking_scan_anchor = """\tfor (int y = 0; y < YRES; y++)
\t{
\t\tfor (int x = 0; x < XRES; x++)
\t\t{
\t\t\t// Use a threshold, since some particle stacking can be normal (e.g. BIZR + FILT)
\t\t\t// Setting pmap_count[y][x] > NPART means BHOL will form in that spot
\t\t\tif (pmap_count[y][x]>5)
\t\t\t{
\t\t\t\tif (bmap[y/CELL][x/CELL]==WL_EHOLE)
\t\t\t\t{
\t\t\t\t\t// Allow more stacking in E-hole
\t\t\t\t\tif (pmap_count[y][x]>1500)
\t\t\t\t\t{
\t\t\t\t\t\tpmap_count[y][x] = pmap_count[y][x] + NPART;
\t\t\t\t\t\texcessive_stacking_found = 1;
\t\t\t\t\t}
\t\t\t\t}
\t\t\t\telse if (pmap_count[y][x]>1500 || (unsigned int)rng.between(0, 1599) <= (pmap_count[y][x]+100))
\t\t\t\t{
\t\t\t\t\tpmap_count[y][x] = pmap_count[y][x] + NPART;
\t\t\t\t\texcessive_stacking_found = true;
\t\t\t\t}
\t\t\t}
\t\t}
\t}"""
stacking_scan_patch = """\t// Preserve original row-major RNG/order semantics while touching only
\t// cells that actually crossed the pmap_count > 5 threshold.
\tstd::sort(yandexWebStackingCells.begin(), yandexWebStackingCells.end());
\tfor (int cell : yandexWebStackingCells)
\t{
\t\tint y = cell / XRES;
\t\tint x = cell % XRES;
\t\tif (bmap[y/CELL][x/CELL]==WL_EHOLE)
\t\t{
\t\t\tif (pmap_count[y][x]>1500)
\t\t\t{
\t\t\t\tpmap_count[y][x] = pmap_count[y][x] + NPART;
\t\t\t\texcessive_stacking_found = 1;
\t\t\t}
\t\t}
\t\telse if (pmap_count[y][x]>1500 || (unsigned int)rng.between(0, 1599) <= (pmap_count[y][x]+100))
\t\t{
\t\t\tpmap_count[y][x] = pmap_count[y][x] + NPART;
\t\t\texcessive_stacking_found = true;
\t\t}
\t}"""
if stacking_scan_anchor not in simulation_text:
    raise SystemExit("Simulation::CheckStacking full-grid scan anchor missing")
simulation_text = simulation_text.replace(
    stacking_scan_anchor, stacking_scan_patch, 1
)

stacking_call_anchor = """		// check for stacking and create BHOL if found
		if (force_stacking_check || rng.chance(1, 10))
		{
			CheckStacking();
		}"""
stacking_call_patch = """		// pmap_count is only used by CheckStacking. Preserve the original RNG
		// decision point, then build counts only on frames that need them.
		if (force_stacking_check || rng.chance(1, 10))
		{
			RebuildStackingCounts();
			CheckStacking();
		}"""
if stacking_call_anchor not in simulation_text:
    raise SystemExit("BeforeSim CheckStacking call anchor missing")
simulation_text = simulation_text.replace(
    stacking_call_anchor, stacking_call_patch, 1
)

wire_anchor = """		// make WIRE work
		if(elementCount[PT_WIRE] > 0)
		{
			for (int nx = 0; nx < XRES; nx++)
			{
				for (int ny = 0; ny < YRES; ny++)
				{
					int r = pmap[ny][nx];
					if (!r)
						continue;
					if(parts[ID(r)].type == PT_WIRE)
						parts[ID(r)].tmp = parts[ID(r)].ctype;
				}
			}
		}"""
wire_patch = """		// make WIRE work
		if(elementCount[PT_WIRE] > 0)
		{
			// Yandex Web: preserve pmap-visible WIRE semantics while scanning
			// active particles instead of every simulation pixel.
			for (int i = 0; i < parts.active; ++i)
			{
				if (parts[i].type != PT_WIRE)
					continue;
				int x = int(parts[i].x + 0.5f);
				int y = int(parts[i].y + 0.5f);
				if (x < 0 || y < 0 || x >= XRES || y >= YRES)
					continue;
				int r = pmap[y][x];
				if (r && TYP(r) == PT_WIRE && ID(r) == i)
					parts[i].tmp = parts[i].ctype;
			}
		}"""
if wire_anchor not in simulation_text:
    raise SystemExit("Simulation WIRE grid-scan anchor missing")
simulation_text = simulation_text.replace(wire_anchor, wire_patch, 1)

gravity_mass_clear_anchor = """		DispatchNewtonianGravity();
		// gravIn::mass is now potentially garbage, which is ok, we were going to clear it for the frame anyway
		for (auto p : gravIn.mass.Size().OriginRect())
		{
			gravIn.mass[p] = 0.f;
		}"""
gravity_mass_clear_patch = """		DispatchNewtonianGravity();
		// Exchange may swap gravIn.mass while Newtonian gravity is active.
		// With gravity disabled, clear only when a gravity writer touched it.
		if (grav || yandexWebGravityMassDirty)
		{
			for (auto p : gravIn.mass.Size().OriginRect())
			{
				gravIn.mass[p] = 0.f;
			}
			yandexWebGravityMassDirty = false;
		}"""
if gravity_mass_clear_anchor not in simulation_text:
    raise SystemExit("Simulation::BeforeSim gravity-mass clear anchor missing")
simulation_text = simulation_text.replace(
    gravity_mass_clear_anchor, gravity_mass_clear_patch, 1
)

reset_gravity_anchor = """	gravIn = newGravIn;
	if (grav)
	{
		gravOut = newGravOut;"""
reset_gravity_patch = """	gravIn = newGravIn;
	yandexWebGravityMassDirty = true;
	if (grav)
	{
		gravOut = newGravOut;"""
if reset_gravity_anchor not in simulation_text:
    raise SystemExit("Simulation::ResetNewtonianGravity dirty anchor missing")
simulation_text = simulation_text.replace(
    reset_gravity_anchor, reset_gravity_patch, 1
)

wall_scan_anchor = """		// decrease wall conduction, make walls block air and ambient heat
		for (int y = 0; y < YCELLS; y++)
		{
			for (int x = 0; x < XCELLS; x++)
			{
				if (emap[y][x])
					emap[y][x] --;
				air->bmap_blockair[y][x] = (bmap[y][x]==WL_WALL || bmap[y][x]==WL_WALLELEC || bmap[y][x]==WL_BLOCKAIR || (bmap[y][x]==WL_EWALL && !emap[y][x]));
				air->bmap_blockairh[y][x] = (air->bmap_blockair[y][x] || bmap[y][x]==WL_GRAV) ? 0x8 : 0;
			}
		}"""
wall_scan_patch = """		// decrease wall conduction, make walls block air and ambient heat
		// Once a complete scan has proven that no walls exist, and no mutation
		// has dirtied that proof, the block-air maps are already all zero and
		// emap has no live wall cells to decay. Skip the fixed YCELLS*XCELLS
		// traversal entirely until a wall mutation invalidates the cache.
		if (yandexWebWallsMayExist || yandexWebWallCellsDirty)
		{
			bool yandexWebWallsPresent = false;
			yandexWebWallCells.clear();
			for (int y = 0; y < YCELLS; y++)
			{
				for (int x = 0; x < XCELLS; x++)
				{
					if (emap[y][x])
						emap[y][x] --;
					if (bmap[y][x])
					{
						yandexWebWallsPresent = true;
						yandexWebWallCells.push_back(y * XCELLS + x);
					}
					air->bmap_blockair[y][x] = (bmap[y][x]==WL_WALL || bmap[y][x]==WL_WALLELEC || bmap[y][x]==WL_BLOCKAIR || (bmap[y][x]==WL_EWALL && !emap[y][x]));
					air->bmap_blockairh[y][x] = (air->bmap_blockair[y][x] || bmap[y][x]==WL_GRAV) ? 0x8 : 0;
				}
			}
			yandexWebWallsMayExist = yandexWebWallsPresent;
			yandexWebWallCellsDirty = false;
		}"""
if wall_scan_anchor not in simulation_text:
    raise SystemExit("Simulation::BeforeSim wall-presence scan anchor missing")
simulation_text = simulation_text.replace(wall_scan_anchor, wall_scan_patch, 1)

load_wall_anchor = """		if (save->blockMap[spos])
		{
			bmap[bpos.Y][bpos.X] = save->blockMap[spos];
			fvx[bpos.Y][bpos.X] = save->fanVelX[spos];"""
load_wall_patch = """		if (save->blockMap[spos])
		{
			bmap[bpos.Y][bpos.X] = save->blockMap[spos];
			yandexWebWallsMayExist = true;
			yandexWebWallCellsDirty = true;
			fvx[bpos.Y][bpos.X] = save->fanVelX[spos];"""
if load_wall_anchor not in simulation_text:
    raise SystemExit("Simulation::Load wall-presence anchor missing")
simulation_text = simulation_text.replace(load_wall_anchor, load_wall_patch, 1)

edge_mode_anchor = """void Simulation::SetEdgeMode(int newEdgeMode)
{
	edgeMode = newEdgeMode;
	switch(edgeMode)"""
edge_mode_patch = """void Simulation::SetEdgeMode(int newEdgeMode)
{
	edgeMode = newEdgeMode;
	yandexWebWallCellsDirty = true;
	switch(edgeMode)"""
if edge_mode_anchor not in simulation_text:
    raise SystemExit("Simulation::SetEdgeMode sparse-cache anchor missing")
simulation_text = simulation_text.replace(edge_mode_anchor, edge_mode_patch, 1)

solid_edge_anchor = """	case EDGE_SOLID:
		int i;"""
solid_edge_patch = """	case EDGE_SOLID:
		yandexWebWallsMayExist = true;
		int i;"""
if solid_edge_anchor not in simulation_text:
    raise SystemExit("Simulation::SetEdgeMode wall-presence anchor missing")
simulation_text = simulation_text.replace(solid_edge_anchor, solid_edge_patch, 1)

clear_start = simulation_text.find("void Simulation::clear_sim(void)")
clear_end = simulation_text.find("\nbool Simulation::IsWallBlocking", clear_start)
if clear_start < 0 or clear_end < 0:
    raise SystemExit("Simulation::clear_sim bounds missing")
clear_segment = simulation_text[clear_start:clear_end]
clear_pmap_anchor = "\tmemset(pmap, 0, sizeof(pmap));\n"
clear_pmap_patch = (
    "\tmemset(pmap, 0, sizeof(pmap));\n"
    "\tyandexWebWallsMayExist = false;\n"
    "\tyandexWebGravityMassDirty = false;\n"
    "\tyandexWebWallCells.clear();\n"
    "\tyandexWebWallCellsDirty = false;\n"
    "\tmemset(pmap_count, 0, sizeof(pmap_count));\n"
    "\tyandexWebCountedCells.clear();\n"
    "\tyandexWebStackingCells.clear();\n"
    "\tyandexWebStackingCandidate = false;\n"
)
if clear_pmap_anchor not in clear_segment:
    raise SystemExit("Simulation::clear_sim pmap anchor missing")
clear_segment = clear_segment.replace(clear_pmap_anchor, clear_pmap_patch, 1)
simulation_text = (
    simulation_text[:clear_start] + clear_segment + simulation_text[clear_end:]
)

save_start = simulation_text.find("std::unique_ptr<GameSave> Simulation::Save")
save_end = simulation_text.find("\nvoid Simulation::SaveSimOptions", save_start)
if save_start < 0 or save_end < 0:
    raise SystemExit("Simulation::Save bounds missing")
save_segment = simulation_text[save_start:save_end]
save_loop_anchor = "	for (int i = 0; i < NPART; i++)\n"
if save_loop_anchor not in save_segment:
    raise SystemExit("Simulation::Save full NPART scan anchor missing")
save_segment = save_segment.replace(
    save_loop_anchor,
    "	// Yandex Web: slots at and beyond parts.active are guaranteed free.\n"
    "	for (int i = 0; i < parts.active; i++)\n",
    1,
)
simulation_text = (
    simulation_text[:save_start] + save_segment + simulation_text[save_end:]
)

simulation_cpp.write_text(simulation_text, encoding="utf-8")

editing_text = editing_cpp.read_text(encoding="utf-8")
restore_wall_anchor = """	std::copy(snap.BlockMap       .begin(), snap.BlockMap       .end(), &bmap[0][0]      );
	std::copy(snap.ElecMap"""
restore_wall_patch = """	std::copy(snap.BlockMap       .begin(), snap.BlockMap       .end(), &bmap[0][0]      );
	yandexWebWallsMayExist = true;
	yandexWebWallCellsDirty = true;
	std::copy(snap.ElecMap"""
if restore_wall_anchor not in editing_text:
    raise SystemExit("Simulation::Restore wall-presence anchor missing")
editing_text = editing_text.replace(restore_wall_anchor, restore_wall_patch, 1)

create_walls_start_anchor = """int Simulation::CreateWalls(int x, int y, int rx, int ry, int wall, Brush const *cBrush)
{"""
create_walls_start_patch = """int Simulation::CreateWalls(int x, int y, int rx, int ry, int wall, Brush const *cBrush)
{
	yandexWebWallCellsDirty = true;"""
if create_walls_start_anchor not in editing_text:
    raise SystemExit("Simulation::CreateWalls sparse-cache anchor missing")
editing_text = editing_text.replace(
    create_walls_start_anchor, create_walls_start_patch, 1
)

create_wall_anchor = """				else
					bmap[wallY][wallX] = wall;
			}
		}
	}
	return 1;"""
create_wall_patch = """				else
					bmap[wallY][wallX] = wall;
				if (bmap[wallY][wallX])
					yandexWebWallsMayExist = true;
			}
		}
	}
	return 1;"""
if create_wall_anchor not in editing_text:
    raise SystemExit("Simulation::CreateWalls wall-presence anchor missing")
editing_text = editing_text.replace(create_wall_anchor, create_wall_patch, 1)
clear_area_anchor = """void Simulation::clear_area(int area_x, int area_y, int area_w, int area_h)
{"""
clear_area_patch = """void Simulation::clear_area(int area_x, int area_y, int area_w, int area_h)
{
	yandexWebWallCellsDirty = true;"""
if clear_area_anchor not in editing_text:
    raise SystemExit("Simulation::clear_area sparse-cache anchor missing")
editing_text = editing_text.replace(clear_area_anchor, clear_area_patch, 1)

editing_cpp.write_text(editing_text, encoding="utf-8")

lua_simulation_text = lua_simulation_cpp.read_text(encoding="utf-8")
lua_wall_anchor = """static int wallMap(lua_State *L)
{
	auto *lsi = GetLSI();
	return LuaBlockMap(L, 0, UI_WALLCOUNT - 1, [lsi](Vec2<int> p) -> unsigned char & {
		return lsi->sim->bmap[p.Y][p.X];
	});
}"""
lua_wall_patch = """static int wallMap(lua_State *L)
{
	auto *lsi = GetLSI();
	return LuaBlockMap(L, 0, UI_WALLCOUNT - 1, [lsi](Vec2<int> p) -> unsigned char & {
		// Lua may mutate the wall map while paused. Mark conservatively even
		// for reads; the next running full wall scan can prove false again.
		lsi->sim->yandexWebWallsMayExist = true;
		lsi->sim->yandexWebWallCellsDirty = true;
		return lsi->sim->bmap[p.Y][p.X];
	});
}"""
if lua_wall_anchor not in lua_simulation_text:
    raise SystemExit("LuaSimulation wallMap wall-presence anchor missing")
lua_simulation_text = lua_simulation_text.replace(
    lua_wall_anchor, lua_wall_patch, 1
)
lua_simulation_cpp.write_text(lua_simulation_text, encoding="utf-8")

# Browser performance: FIREMODE is part of the default renderer, but most
# scenes have no active fire/glow accumulation. Avoid the expensive blur/
# decay neighbourhood pass when all fire buffers are already zero.
renderer_h_text = renderer_h.read_text(encoding="utf-8")
fire_state_anchor = """	unsigned char fire_b[YCELLS][XCELLS];
	unsigned int fire_alpha[CELL*3][CELL*3];"""
fire_state_patch = """	unsigned char fire_b[YCELLS][XCELLS];
	unsigned int fire_alpha[CELL*3][CELL*3];
	bool yandexWebFireActive = false;"""
if fire_state_anchor not in renderer_h_text:
    raise SystemExit("Renderer.h fire accumulation state anchor missing")
renderer_h_text = renderer_h_text.replace(
    fire_state_anchor, fire_state_patch, 1
)
renderer_h.write_text(renderer_h_text, encoding="utf-8")

renderer_text = renderer_cpp.read_text(encoding="utf-8")
walls_anchor = """void Renderer::DrawWalls()
{
	auto &sd = SimulationData::CRef();"""
walls_patch = """void Renderer::DrawWalls()
{
	if (!sim->yandexWebWallsMayExist)
		return;

	auto &sd = SimulationData::CRef();"""
if walls_anchor not in renderer_text:
    raise SystemExit("Renderer::DrawWalls wall-presence fast-path anchor missing")
renderer_text = renderer_text.replace(walls_anchor, walls_patch, 1)

# When the simulation scan has produced an exact wall-cell cache, render only
# those cells. If a paused edit invalidated the cache, preserve upstream
# behaviour by falling back to a complete grid traversal until the next tick.
draw_walls_start = renderer_text.find("void Renderer::DrawWalls()")
draw_walls_end = renderer_text.find(
    "\nvoid Renderer::render_fire()", draw_walls_start
)
if draw_walls_start < 0 or draw_walls_end < 0:
    raise SystemExit("Renderer::DrawWalls sparse-cache bounds missing")
draw_walls = renderer_text[draw_walls_start:draw_walls_end]

draw_walls_grid_anchor = """	auto &wtypes = sd.wtypes;
	for (int y = 0; y < YCELLS; y++)
		for (int x =0; x < XCELLS; x++)
			if (sim->bmap[y][x])
			{"""
draw_walls_grid_patch = """	auto &wtypes = sd.wtypes;
	auto yandexWebDrawWallCell = [&](int x, int y)
	{
		if (!sim->bmap[y][x])
			return;"""
if draw_walls_grid_anchor not in draw_walls:
    raise SystemExit("Renderer::DrawWalls grid prefix anchor missing")
draw_walls = draw_walls.replace(
    draw_walls_grid_anchor, draw_walls_grid_patch, 1
)

invalid_wall_anchor = """				if (wt >= UI_WALLCOUNT)
					continue;"""
invalid_wall_patch = """				if (wt >= UI_WALLCOUNT)
					return;"""
if invalid_wall_anchor not in draw_walls:
    raise SystemExit("Renderer::DrawWalls invalid-wall continue anchor missing")
draw_walls = draw_walls.replace(
    invalid_wall_anchor, invalid_wall_patch, 1
)

stream_continue_anchor = """							AddPixel({ oldX, oldY }, 0xFFFFFF_rgb .WithAlpha(255));
							continue;"""
stream_continue_patch = """							AddPixel({ oldX, oldY }, 0xFFFFFF_rgb .WithAlpha(255));
							return;"""
if stream_continue_anchor not in draw_walls:
    raise SystemExit("Renderer::DrawWalls stream continue anchor missing")
draw_walls = draw_walls.replace(
    stream_continue_anchor, stream_continue_patch, 1
)

draw_walls_suffix_anchor = "			}\n}"
suffix_pos = draw_walls.rfind(draw_walls_suffix_anchor)
if suffix_pos < 0:
    raise SystemExit("Renderer::DrawWalls sparse-cache suffix anchor missing")
draw_walls_suffix_patch = """	};

	if (!sim->yandexWebWallCellsDirty)
	{
		for (int cell : sim->yandexWebWallCells)
		{
			int y = cell / XCELLS;
			int x = cell % XCELLS;
			yandexWebDrawWallCell(x, y);
		}
		return;
	}

	for (int y = 0; y < YCELLS; ++y)
		for (int x = 0; x < XCELLS; ++x)
			yandexWebDrawWallCell(x, y);
}"""
draw_walls = (
    draw_walls[:suffix_pos]
    + draw_walls_suffix_patch
    + draw_walls[suffix_pos + len(draw_walls_suffix_anchor):]
)
renderer_text = (
    renderer_text[:draw_walls_start]
    + draw_walls
    + renderer_text[draw_walls_end:]
)

signs_anchor = """	std::vector<sign> signs = sim->signs;
	for (auto &currentSign : signs)"""
signs_patch = """	const auto &signs = sim->signs;
	for (const auto &currentSign : signs)"""
if signs_anchor not in renderer_text:
    raise SystemExit("Renderer::DrawSigns copy anchor missing")
renderer_text = renderer_text.replace(signs_anchor, signs_patch, 1)

fire_blend_anchor = """					fire_b[ny/CELL][nx/CELL] = (firea*fireb + (255-firea)*fire_b[ny/CELL][nx/CELL]) >> 8;
				}
				if(firea && (pixel_mode & FIRE_ADD))"""
fire_blend_patch = """					fire_b[ny/CELL][nx/CELL] = (firea*fireb + (255-firea)*fire_b[ny/CELL][nx/CELL]) >> 8;
					yandexWebFireActive = true;
				}
				if(firea && (pixel_mode & FIRE_ADD))"""
if fire_blend_anchor not in renderer_text:
    raise SystemExit("Renderer FIRE_BLEND active-state anchor missing")
renderer_text = renderer_text.replace(
    fire_blend_anchor, fire_blend_patch, 1
)

fire_add_anchor = """					fire_r[ny/CELL][nx/CELL] = firer;
					fire_g[ny/CELL][nx/CELL] = fireg;
					fire_b[ny/CELL][nx/CELL] = fireb;
				}
				if(firea && (pixel_mode & FIRE_SPARK))"""
fire_add_patch = """					fire_r[ny/CELL][nx/CELL] = firer;
					fire_g[ny/CELL][nx/CELL] = fireg;
					fire_b[ny/CELL][nx/CELL] = fireb;
					yandexWebFireActive = true;
				}
				if(firea && (pixel_mode & FIRE_SPARK))"""
if fire_add_anchor not in renderer_text:
    raise SystemExit("Renderer FIRE_ADD active-state anchor missing")
renderer_text = renderer_text.replace(
    fire_add_anchor, fire_add_patch, 1
)

fire_spark_anchor = """					fire_b[ny/CELL][nx/CELL] = (firea*fireb + (255-firea)*fire_b[ny/CELL][nx/CELL]) >> 8;
				}
			}
		}"""
fire_spark_patch = """					fire_b[ny/CELL][nx/CELL] = (firea*fireb + (255-firea)*fire_b[ny/CELL][nx/CELL]) >> 8;
					yandexWebFireActive = true;
				}
			}
		}"""
if fire_spark_anchor not in renderer_text:
    raise SystemExit("Renderer FIRE_SPARK active-state anchor missing")
renderer_text = renderer_text.replace(
    fire_spark_anchor, fire_spark_patch, 1
)

wall_glow_anchor = """					fire_r[y][x] = cr;
					fire_g[y][x] = cg;
					fire_b[y][x] = cb;"""
wall_glow_patch = """					fire_r[y][x] = cr;
					fire_g[y][x] = cg;
					fire_b[y][x] = cb;
					yandexWebFireActive = true;"""
if wall_glow_anchor not in renderer_text:
    raise SystemExit("Renderer powered-wall fire state anchor missing")
renderer_text = renderer_text.replace(
    wall_glow_anchor, wall_glow_patch, 1
)

fire_anchor = """void Renderer::render_fire()
{
	if(!(renderMode & FIREMODE))
		return;
	int i,j,x,y,r,g,b,a;"""
fire_patch = """void Renderer::render_fire()
{
	if(!(renderMode & FIREMODE) || !yandexWebFireActive)
		return;

	bool yandexWebNextFireActive = false;
	int i,j,x,y,r,g,b,a;"""
if fire_anchor not in renderer_text:
    raise SystemExit("Renderer::render_fire fast-path anchor missing")
renderer_text = renderer_text.replace(fire_anchor, fire_patch, 1)

fire_decay_anchor = """			fire_r[j][i] = r>4 ? r-4 : 0;
			fire_g[j][i] = g>4 ? g-4 : 0;
			fire_b[j][i] = b>4 ? b-4 : 0;
		}
}"""
fire_decay_patch = """			fire_r[j][i] = r>4 ? r-4 : 0;
			fire_g[j][i] = g>4 ? g-4 : 0;
			fire_b[j][i] = b>4 ? b-4 : 0;
			if (fire_r[j][i] || fire_g[j][i] || fire_b[j][i])
				yandexWebNextFireActive = true;
		}
	yandexWebFireActive = yandexWebNextFireActive;
}"""
if fire_decay_anchor not in renderer_text:
    raise SystemExit("Renderer::render_fire decay-state anchor missing")
renderer_text = renderer_text.replace(
    fire_decay_anchor, fire_decay_patch, 1
)

clear_accum_anchor = """	std::fill(&fire_b[0][0], &fire_b[0][0] + NCELL, 0);
	std::fill(persistentVideo.begin(), persistentVideo.end(), 0);"""
clear_accum_patch = """	std::fill(&fire_b[0][0], &fire_b[0][0] + NCELL, 0);
	yandexWebFireActive = false;
	std::fill(persistentVideo.begin(), persistentVideo.end(), 0);"""
if clear_accum_anchor not in renderer_text:
    raise SystemExit("Renderer::ClearAccumulation fire-state anchor missing")
renderer_text = renderer_text.replace(
    clear_accum_anchor, clear_accum_patch, 1
)

renderer_cpp.write_text(renderer_text, encoding="utf-8")


# Yandex Web RU/EN localisation layer.
locale_header.write_text(r'''#pragma once
#include "common/String.h"
#if defined(__EMSCRIPTEN__)
#include <emscripten.h>
#endif

inline bool YandexWebIsRussian()
{
#if defined(__EMSCRIPTEN__)
	static const bool russian = emscripten_run_script_int(
		"window.tptLanguage === 'ru' ? 1 : 0"
	) != 0;
	return russian;
#else
	return false;
#endif
}

inline String YandexWebText(const char *english, const char *russian)
{
	return ByteString(YandexWebIsRussian() ? russian : english).FromUtf8();
}

// Common native UI strings can be created from many different windows,
// including rarely opened local dialogs. Translate them at the component
// boundary so Russian mode does not depend solely on individual call-site
// replacements. The map is exact-match only, so arbitrary save names and
// simulation text are left unchanged unless they exactly equal a UI token.
inline String YandexWebTranslateUi(const String &source)
{
	if (!YandexWebIsRussian() || !source.size())
		return source;

#define YW_UI(en, ru) if (source == en) return ByteString(ru).FromUtf8()
	YW_UI("OK", "ОК");
	YW_UI("Okay", "ОК");
	YW_UI("Cancel", "Отмена");
	YW_UI("Close", "Закрыть");
	YW_UI("Dismiss", "Закрыть");
	YW_UI("Done", "Готово");
	YW_UI("Save", "Сохранить");
	YW_UI("Save as", "Сохранить как");
	YW_UI("Open", "Открыть");
	YW_UI("Load", "Загрузить");
	YW_UI("Reload", "Перезапустить");
	YW_UI("Retry", "Повторить");
	YW_UI("Copy", "Копировать");
	YW_UI("Cut", "Вырезать");
	YW_UI("Paste", "Вставить");
	YW_UI("Delete", "Удалить");
	YW_UI("Rename", "Переименовать");
	YW_UI("Select", "Выбрать");
	YW_UI("Add", "Добавить");
	YW_UI("Remove", "Удалить");
	YW_UI("Edit", "Изменить");
	YW_UI("Move", "Переместить");
	YW_UI("New", "Создать");
	YW_UI("Create", "Создать");
	YW_UI("Reset", "Сбросить");
	YW_UI("Apply", "Применить");
	YW_UI("Clear", "Очистить");
	YW_UI("Search", "Поиск");
	YW_UI("Settings", "Настройки");
	YW_UI("Options", "Настройки");
	YW_UI("Renderer", "Отображение");
	YW_UI("Render Options", "Настройки отображения");
	YW_UI("Alternative Velocity Display", "Альтернативная скорость");
	YW_UI("Velocity Display", "Скорость");
	YW_UI("Pressure Display", "Давление");
	YW_UI("Persistent Display", "Следы");
	YW_UI("Fire Display", "Огонь");
	YW_UI("Blob Display", "Сгустки");
	YW_UI("Heat Display", "Температура");
	YW_UI("Fancy Display", "Эффекты");
	YW_UI("Nothing Display", "Без эффектов");
	YW_UI("Heat Gradient Display", "Градиент температуры");
	YW_UI("Life Gradient Display", "Градиент жизни");
	YW_UI("Dynamic Heat Display", "Динамическая температура");
	YW_UI("Vorticity Display", "Завихренность");
	YW_UI("Credits", "Авторы");
	YW_UI("Stamps", "Штампы");
	YW_UI("Element Search", "Поиск элементов");
	YW_UI("Property", "Свойство");
	YW_UI("Colour", "Цвет");
	YW_UI("Color", "Цвет");
	YW_UI("Sign", "Надпись");
	YW_UI("Rescan", "Обновить");
	YW_UI("Back", "Назад");
	YW_UI("Next", "Далее");
	YW_UI("Previous", "Назад");
	YW_UI("Prev", "Назад");
	YW_UI("Yes", "Да");
	YW_UI("No", "Нет");
	YW_UI("On", "Вкл.");
	YW_UI("Off", "Выкл.");
	YW_UI("Enabled", "Включено");
	YW_UI("Disabled", "Отключено");
	YW_UI("Default", "По умолчанию");
	YW_UI("None", "Нет");
	YW_UI("Legacy", "Классический");
	YW_UI("Boussinesq", "Буссинеск");
	YW_UI("Pause", "Пауза");
	YW_UI("Resume", "Продолжить");
	YW_UI("Quit", "Выйти");
	YW_UI("Exit", "Выйти");
	YW_UI("Import", "Импорт");
	YW_UI("Export", "Экспорт");
	YW_UI("Browse", "Обзор");
	YW_UI("View History", "История");
	YW_UI("Overwrite", "Перезаписать");
	YW_UI("Confirm", "Подтвердить");
	YW_UI("Change", "Изменить");
	YW_UI("Refresh", "Обновить");
	YW_UI("Select All", "Выбрать всё");
	YW_UI("Deselect All", "Снять выбор");
	YW_UI("Open Folder", "Открыть папку");
	YW_UI("Migrate to shared data directory", "Перенести данные");

	// Core simulation/options window.
	YW_UI("Heat simulation \\bgIntroduced in version 34", "Тепловая симуляция");
	YW_UI("Can cause odd behaviour when disabled", "При отключении возможны необычные эффекты");
	YW_UI("Newtonian gravity \\bgIntroduced in version 48", "Ньютоновская гравитация");
	YW_UI("May cause poor performance on older computers", "Может снижать производительность на слабых устройствах");
	YW_UI("Ambient heat simulation \\bgIntroduced in version 50", "Фоновая тепловая симуляция");
	YW_UI("Can cause odd / broken behaviour with many saves", "Некоторые сохранения могут работать некорректно");
	YW_UI("Water equalisation \\bgIntroduced in version 61", "Выравнивание воды");
	YW_UI("May cause poor performance with a lot of water", "Большое количество воды может снижать производительность");
	YW_UI("Air simulation mode", "Режим симуляции воздуха");
	YW_UI("Pressure off", "Без давления");
	YW_UI("Velocity off", "Без скорости воздуха");
	YW_UI("No update", "Без обновления");
	YW_UI("Ambient air temperature", "Температура воздуха");
	YW_UI("Ambient air pressure", "Давление воздуха");
	YW_UI("Ambient air velocity", "Скорость воздуха");
	YW_UI("Vorticity confinement", "Усиление завихрений");
	YW_UI("Air heat convection mode", "Режим тепловой конвекции");
	YW_UI("Gravity simulation mode", "Режим гравитации");
	YW_UI("Vertical", "Вертикальная");
	YW_UI("Radial", "Радиальная");
	YW_UI("Custom", "Пользовательская");
	YW_UI("Custom Gravity", "Пользовательская гравитация");
	YW_UI("Edge mode", "Режим границ");
	YW_UI("Void", "Пустота");
	YW_UI("Solid", "Твёрдая граница");
	YW_UI("Loop", "Зацикливание");
	YW_UI("Temperature scale", "Шкала температуры");
	YW_UI("Celsius", "Цельсий");
	YW_UI("Fahrenheit", "Фаренгейт");
	YW_UI("Simulation framerate cap", "Ограничение FPS симуляции");
	YW_UI("Rendering framerate cap", "Ограничение FPS отрисовки");
	YW_UI("Exact", "Точно");
	YW_UI("Uncapped", "Без ограничения");
	YW_UI("Follow display", "По частоте экрана");
	YW_UI("Window scale factor for larger screens", "Масштаб окна для больших экранов");
	YW_UI("Resizable \\bg- allow resizing and maximizing window", "Изменяемый размер окна");
	YW_UI("Fullscreen \\bg- fill the entire screen", "Полноэкранный режим");
	YW_UI("Set optimal screen resolution", "Использовать оптимальное разрешение");
	YW_UI("Force integer scaling \\bg- less blurry", "Целочисленное масштабирование");
	YW_UI("Blurry scaling \\bg- more blurry, better on very big screens", "Сглаженное масштабирование");
	YW_UI("Include pressure", "Сохранять давление");
	YW_UI("When saving, copying, stamping, etc.", "При сохранении, копировании и создании штампов");
	YW_UI("Perfect circle brush", "Точная круглая кисть");
	YW_UI("Separate rendering thread", "Отдельный поток отрисовки");
	YW_UI("May increase framerate when fancy effects are in use", "Может повысить FPS при использовании эффектов");
	YW_UI("Colour space used by decoration tools", "Цветовое пространство декораций");
	YW_UI("Open data folder", "Открыть папку данных");
	YW_UI("Credits - Find out who contributed to TPT", "Авторы проекта");

	// Render options descriptions.
	YW_UI("Adds Special flare effects to some elements", "Добавляет специальные световые эффекты некоторым элементам");
	YW_UI("Fire effect for gasses", "Эффект огня для газов");
	YW_UI("Glow effect on some elements", "Свечение некоторых элементов");
	YW_UI("Blur effect for liquids", "Размытие жидкостей");
	YW_UI("Makes everything be drawn like a blob", "Отрисовывает элементы как сгустки");
	YW_UI("Basic rendering, without this, most things will be invisible", "Базовая отрисовка, без неё большинство элементов невидимо");
	YW_UI("Glow effect on sparks", "Свечение искр");
	YW_UI("Displays pressure as red and blue, and velocity as white", "Давление красным и синим, скорость белым");
	YW_UI("Displays pressure, red is positive and blue is negative", "Давление: красный - положительное, синий - отрицательное");
	YW_UI("Displays the temperature of the air like heat display does", "Показывает температуру воздуха");
	YW_UI("Displays vorticity, red is clockwise and blue is anticlockwise", "Показывает завихрения: красный - по часовой, синий - против");
	YW_UI("Gravity lensing, Newtonian Gravity bends light with this on", "Гравитационное линзирование при ньютоновской гравитации");
	YW_UI("Element paths persist on the screen for a while", "Следы элементов некоторое время остаются на экране");
	YW_UI("Displays temperatures of the elements, dark blue is coldest, pink is hottest", "Температура элементов: тёмно-синий - холод, розовый - жар");
	YW_UI("Displays the life value of elements in greyscale gradients", "Показывает значение жизни элементов оттенками серого");
	YW_UI("Changes colors of elements slightly to show heat diffusing through them", "Изменяет цвета элементов, показывая распространение тепла");
	YW_UI("No special effects at all for anything, overrides all other options and deco", "Отключает специальные эффекты и декорации");
#undef YW_UI
	return source;
}

inline String YandexWebCompactToolButtonText(String label)
{
	// Keep the localized word intact here. ToolButton.cpp performs the final
	// clipping by *rendered pixel width*, so Cyrillic captions use as much of
	// the fixed button width as actually fits without crossing the border.
	return label;
}

inline String YandexWebToolButtonText(
	ByteString const &identifier,
	String const &name,
	String const &description
)
{
	if (!YandexWebIsRussian())
		return name;

	// Keep canonical identifiers and element names untouched internally. Only
	// the text painted on ToolButton is localized, so saves, Lua scripts and
	// element lookup remain fully upstream-compatible.
#define YW_TOOL(id, ru) if (identifier == id) return YandexWebCompactToolButtonText(ByteString(ru).FromUtf8())
	YW_TOOL("DEFAULT_PT_WATR", "Вода");
	YW_TOOL("DEFAULT_PT_DSTW", "Дист");
	YW_TOOL("DEFAULT_PT_SLTW", "СолВ");
	YW_TOOL("DEFAULT_PT_WTRV", "Пар");
	YW_TOOL("DEFAULT_PT_ICEI", "Лёд");
	YW_TOOL("DEFAULT_PT_SNOW", "Снег");
	YW_TOOL("DEFAULT_PT_DUST", "ПЫЛЬ");
	YW_TOOL("DEFAULT_PT_SAND", "Песок");
	YW_TOOL("DEFAULT_PT_STNE", "Кам.");
	YW_TOOL("DEFAULT_PT_ROCK", "Скала");
	YW_TOOL("DEFAULT_PT_BRCK", "Кирп");
	YW_TOOL("DEFAULT_PT_DMND", "Алм.");
	YW_TOOL("DEFAULT_PT_GLAS", "Стек");
	YW_TOOL("DEFAULT_PT_WOOD", "Древ");
	YW_TOOL("DEFAULT_PT_FIRE", "Огонь");
	YW_TOOL("DEFAULT_PT_PLSM", "Плаз");
	YW_TOOL("DEFAULT_PT_LAVA", "Лава");
	YW_TOOL("DEFAULT_PT_SMKE", "Дым");
	YW_TOOL("DEFAULT_PT_OIL", "Нефт");
	YW_TOOL("DEFAULT_PT_GAS", "Газ");
	YW_TOOL("DEFAULT_PT_DESL", "Диз.");
	YW_TOOL("DEFAULT_PT_NITR", "Нитр");
	YW_TOOL("DEFAULT_PT_GUNP", "Порох");
	YW_TOOL("DEFAULT_PT_PLEX", "Плст");
	YW_TOOL("DEFAULT_PT_BOMB", "Бомб");
	YW_TOOL("DEFAULT_PT_THRM", "Терм");
	YW_TOOL("DEFAULT_PT_METL", "Мет.");
	YW_TOOL("DEFAULT_PT_BMTL", "ХрМт");
	YW_TOOL("DEFAULT_PT_IRON", "Жел.");
	YW_TOOL("DEFAULT_PT_GOLD", "Зол.");
	YW_TOOL("DEFAULT_PT_TUNG", "Влф");
	YW_TOOL("DEFAULT_PT_INSL", "Изол");
	YW_TOOL("DEFAULT_PT_SPRK", "Искр");
	YW_TOOL("DEFAULT_PT_BTRY", "Бат.");
	YW_TOOL("DEFAULT_PT_PSCN", "Кр+");
	YW_TOOL("DEFAULT_PT_NSCN", "Кр-");
	YW_TOOL("DEFAULT_PT_SWCH", "Ключ");
	YW_TOOL("DEFAULT_PT_WIFI", "Ради");
	YW_TOOL("DEFAULT_PT_WIRE", "Пров");
	YW_TOOL("DEFAULT_PT_LCRY", "ЖКр");
	YW_TOOL("DEFAULT_PT_FILT", "Фил.");
	YW_TOOL("DEFAULT_PT_PHOT", "Фот.");
	YW_TOOL("DEFAULT_PT_ELEC", "Эл-н");
	YW_TOOL("DEFAULT_PT_NEUT", "Нейт");
	YW_TOOL("DEFAULT_PT_PROT", "Прот");
	YW_TOOL("DEFAULT_PT_URAN", "Уран");
	YW_TOOL("DEFAULT_PT_PLUT", "Плут");
	YW_TOOL("DEFAULT_PT_DEUT", "Дейт");
	YW_TOOL("DEFAULT_PT_CLNE", "Клон");
	YW_TOOL("DEFAULT_PT_PCLN", "ЭКлн");
	YW_TOOL("DEFAULT_PT_BCLN", "ХКлн");
	YW_TOOL("DEFAULT_PT_CONV", "Прев");
	YW_TOOL("DEFAULT_PT_VOID", "Пуст");
	YW_TOOL("DEFAULT_PT_PVOD", "ЭПст");
	YW_TOOL("DEFAULT_PT_BHOL", "ЧД");
	YW_TOOL("DEFAULT_PT_WHOL", "БД");
	YW_TOOL("DEFAULT_PT_NBHL", "ГЧД");
	YW_TOOL("DEFAULT_PT_NWHL", "ГБД");
	YW_TOOL("DEFAULT_PT_PUMP", "Насос");
	YW_TOOL("DEFAULT_PT_GPMP", "ГНас");
	YW_TOOL("DEFAULT_PT_FRAY", "СЛуч");
	YW_TOOL("DEFAULT_PT_RPEL", "Оттл");
	YW_TOOL("DEFAULT_PT_STKM", "Чел1");
	YW_TOOL("DEFAULT_PT_STKM2", "Чел2");
	YW_TOOL("DEFAULT_PT_ACID", "Кисл");
	YW_TOOL("DEFAULT_PT_CAUS", "ЕдкГ");
	YW_TOOL("DEFAULT_PT_LNTG", "ЖАзт");
	YW_TOOL("DEFAULT_PT_LO2", "ЖКис");
	YW_TOOL("DEFAULT_PT_MERC", "Ртут");
	YW_TOOL("DEFAULT_PT_GEL", "Гель");
	YW_TOOL("DEFAULT_PT_SOAP", "Мыло");
	YW_TOOL("DEFAULT_PT_SPNG", "Губка");
	YW_TOOL("DEFAULT_PT_SALT", "Соль");
	YW_TOOL("DEFAULT_PT_CLST", "Глин");
	YW_TOOL("DEFAULT_PT_CO2", "УглГ");
	YW_TOOL("DEFAULT_PT_O2", "КисГ");
	YW_TOOL("DEFAULT_PT_H2", "ВодГ");
	YW_TOOL("DEFAULT_PT_NBLE", "Инер");
	YW_TOOL("DEFAULT_PT_BOYL", "Бойль");
	YW_TOOL("DEFAULT_PT_FOG", "Тум.");
	YW_TOOL("DEFAULT_PT_AMTR", "АнтМ");
	YW_TOOL("DEFAULT_PT_ANAR", "АнтВ");
	YW_TOOL("DEFAULT_PT_SING", "Синг");
	YW_TOOL("DEFAULT_PT_DEST", "Разр");
	YW_TOOL("DEFAULT_PT_EXOT", "Экзо");
	YW_TOOL("DEFAULT_PT_WARP", "Сдвиг");
	YW_TOOL("DEFAULT_PT_VIBR", "Вибр");
	YW_TOOL("DEFAULT_PT_BVBR", "ХВиб");
	YW_TOOL("DEFAULT_PT_BANG", "ТНТ");
	YW_TOOL("DEFAULT_PT_FUSE", "Фит.");
	YW_TOOL("DEFAULT_PT_FSEP", "ПФит");
	YW_TOOL("DEFAULT_PT_FIRW", "Сал.");
	YW_TOOL("DEFAULT_PT_FWRK", "Сал2");
	YW_TOOL("DEFAULT_PT_LIGH", "Молн");
	YW_TOOL("DEFAULT_PT_THDR", "Гром");
	YW_TOOL("DEFAULT_PT_EMBR", "Углк");
	YW_TOOL("DEFAULT_PT_TESC", "Тесла");
	YW_TOOL("DEFAULT_PT_ARAY", "Луч");
	YW_TOOL("DEFAULT_PT_BRAY", "ТЛуч");
	YW_TOOL("DEFAULT_PT_CRAY", "ЧЛуч");
	YW_TOOL("DEFAULT_PT_DRAY", "ДЛуч");
	YW_TOOL("DEFAULT_PT_DTEC", "Дет.");
	YW_TOOL("DEFAULT_PT_PSTN", "Порш");
	YW_TOOL("DEFAULT_PT_FRME", "Рама");
	YW_TOOL("DEFAULT_PT_PIPE", "Труба");
	YW_TOOL("DEFAULT_PT_PPIP", "ЭТрб");
	YW_TOOL("DEFAULT_PT_STOR", "Скл.");
	YW_TOOL("DEFAULT_PT_DLAY", "Задр");
	YW_TOOL("DEFAULT_PT_HSWC", "ТКлч");
	YW_TOOL("DEFAULT_PT_INST", "МгнП");
	YW_TOOL("DEFAULT_PT_ETRD", "Элод");
	YW_TOOL("DEFAULT_PT_NTCT", "Тр+");
	YW_TOOL("DEFAULT_PT_PTCT", "Тр-");
	YW_TOOL("DEFAULT_PT_INWR", "ИзПр");
	YW_TOOL("DEFAULT_PT_INVIS", "Нев.");
	YW_TOOL("DEFAULT_PT_LDTC", "ЛДет");
	YW_TOOL("DEFAULT_PT_TSNS", "ДТем");
	YW_TOOL("DEFAULT_PT_PSNS", "ДДав");
	YW_TOOL("DEFAULT_PT_VSNS", "ДСкр");
	YW_TOOL("DEFAULT_PT_LSNS", "ДЖиз");
	YW_TOOL("DEFAULT_PT_ACEL", "Ускр");
	YW_TOOL("DEFAULT_PT_DCEL", "Замд");
	YW_TOOL("DEFAULT_PT_BASE", "ЕдкЖ");
	YW_TOOL("DEFAULT_PT_BCOL", "КрУг");
	YW_TOOL("DEFAULT_PT_BGLA", "Оскл");
	YW_TOOL("DEFAULT_PT_BIZR", "СтрЖ");
	YW_TOOL("DEFAULT_PT_BIZRG", "СтрГ");
	YW_TOOL("DEFAULT_PT_BIZRS", "СтрТ");
	YW_TOOL("DEFAULT_PT_BREC", "ЛомЭ");
	YW_TOOL("DEFAULT_PT_BRMT", "ЛомМ");
	YW_TOOL("DEFAULT_PT_C5", "ХолВ");
	YW_TOOL("DEFAULT_PT_CBNW", "ГазВ");
	YW_TOOL("DEFAULT_PT_CFLM", "ХолО");
	YW_TOOL("DEFAULT_PT_CNCT", "Бет.");
	YW_TOOL("DEFAULT_PT_COAL", "Уголь");
	YW_TOOL("DEFAULT_PT_CRMC", "Кер.");
	YW_TOOL("DEFAULT_PT_DMG", "Удар");
	YW_TOOL("DEFAULT_PT_DRIC", "СухЛ");
	YW_TOOL("DEFAULT_PT_DYST", "МДр");
	YW_TOOL("DEFAULT_PT_E116", "Опыт");
	YW_TOOL("DEFAULT_PT_EMP", "ЭМИ");
	YW_TOOL("DEFAULT_PT_FIGH", "Боец");
	YW_TOOL("DEFAULT_PT_FRZW", "МорВ");
	YW_TOOL("DEFAULT_PT_FRZZ", "МорП");
	YW_TOOL("DEFAULT_PT_GBMB", "ГБмб");
	YW_TOOL("DEFAULT_PT_GLOW", "Свет");
	YW_TOOL("DEFAULT_PT_GOO", "Слизь");
	YW_TOOL("DEFAULT_PT_GRAV", "ГПыл");
	YW_TOOL("DEFAULT_PT_GRVT", "Грав");
	YW_TOOL("DEFAULT_PT_HEAC", "ТПрв");
	YW_TOOL("DEFAULT_PT_IGNT", "Шнур");
	YW_TOOL("DEFAULT_PT_ISOZ", "ИзЖ");
	YW_TOOL("DEFAULT_PT_ISZS", "ИзТ");
	YW_TOOL("DEFAULT_PT_LIFE", "Жизн");
	YW_TOOL("DEFAULT_PT_LITH", "Лит.");
	YW_TOOL("DEFAULT_PT_LOLZ", "Смех");
	YW_TOOL("DEFAULT_PT_LOVE", "Люб.");
	YW_TOOL("DEFAULT_PT_LRBD", "ЖРуб");
	YW_TOOL("DEFAULT_PT_MORT", "Паров");
	YW_TOOL("DEFAULT_PT_MWAX", "ЖВск");
	YW_TOOL("DEFAULT_PT_NICE", "АзЛд");
	YW_TOOL("DEFAULT_PT_PBCN", "ЭХКл");
	YW_TOOL("DEFAULT_PT_PLNT", "Рост");
	YW_TOOL("DEFAULT_PT_POLO", "Полон");
	YW_TOOL("DEFAULT_PT_PQRT", "ПКвр");
	YW_TOOL("DEFAULT_PT_PRTI", "Вход");
	YW_TOOL("DEFAULT_PT_PRTO", "Вых.");
	YW_TOOL("DEFAULT_PT_PSTE", "Паст");
	YW_TOOL("DEFAULT_PT_PSTS", "ТПст");
	YW_TOOL("DEFAULT_PT_PTNM", "Плат");
	YW_TOOL("DEFAULT_PT_QRTZ", "Кврц");
	YW_TOOL("DEFAULT_PT_RBDM", "Руб.");
	YW_TOOL("DEFAULT_PT_RFGL", "ЖХлд");
	YW_TOOL("DEFAULT_PT_RFRG", "Хлад");
	YW_TOOL("DEFAULT_PT_RIME", "Иней");
	YW_TOOL("DEFAULT_PT_RSSS", "ТРез");
	YW_TOOL("DEFAULT_PT_RSST", "Рез.");
	YW_TOOL("DEFAULT_PT_SAWD", "Опил");
	YW_TOOL("DEFAULT_PT_SEED", "Семя");
	YW_TOOL("DEFAULT_PT_SHLD1", "Щит1");
	YW_TOOL("DEFAULT_PT_SHLD2", "Щит2");
	YW_TOOL("DEFAULT_PT_SHLD3", "Щит3");
	YW_TOOL("DEFAULT_PT_SHLD4", "Щит4");
	YW_TOOL("DEFAULT_PT_SLCN", "Крем");
	YW_TOOL("DEFAULT_PT_SPAWN", "Спн1");
	YW_TOOL("DEFAULT_PT_SPAWN2", "Спн2");
	YW_TOOL("DEFAULT_PT_TRON", "Трон");
	YW_TOOL("DEFAULT_PT_TTAN", "Тит.");
	YW_TOOL("DEFAULT_PT_VINE", "Лоза");
	YW_TOOL("DEFAULT_PT_VIRS", "ВирЖ");
	YW_TOOL("DEFAULT_PT_VRSG", "ВирГ");
	YW_TOOL("DEFAULT_PT_VRSS", "ВирТ");
	YW_TOOL("DEFAULT_PT_WAX", "Воск");
	YW_TOOL("DEFAULT_PT_YEST", "Дрож");
	YW_TOOL("DEFAULT_PT_NONE", "Стер");
	YW_TOOL("DEFAULT_TOOL_COOL", "Хол.");
	YW_TOOL("DEFAULT_TOOL_HEAT", "Жар");
	YW_TOOL("DEFAULT_TOOL_VAC", "Вак.");
	YW_TOOL("DEFAULT_TOOL_AIR", "Возд");
	YW_TOOL("DEFAULT_TOOL_WIND", "Ветр");
	YW_TOOL("DEFAULT_TOOL_CYCL", "Вихрь");
	YW_TOOL("DEFAULT_TOOL_AMBM", "Фон-");
	YW_TOOL("DEFAULT_TOOL_AMBP", "Фон+");
	YW_TOOL("DEFAULT_TOOL_NGRV", "Грав-");
	YW_TOOL("DEFAULT_TOOL_PGRV", "Гр+");
	YW_TOOL("DEFAULT_TOOL_MIX", "Меш.");
	YW_TOOL("DEFAULT_DECOR_ADD", "Доб.");
	YW_TOOL("DEFAULT_DECOR_SUB", "Выч.");
	YW_TOOL("DEFAULT_DECOR_MUL", "Умн.");
	YW_TOOL("DEFAULT_DECOR_DIV", "Дел.");
	YW_TOOL("DEFAULT_DECOR_SMDG", "Маз.");
	YW_TOOL("DEFAULT_DECOR_CLR", "Стер");
	YW_TOOL("DEFAULT_DECOR_SET", "Цвет");
	YW_TOOL("DEFAULT_UI_PROPERTY", "Св-ва");
	YW_TOOL("DEFAULT_UI_SIGN", "Текс");
	YW_TOOL("DEFAULT_UI_SAMPLE", "Проба");
	YW_TOOL("DEFAULT_UI_ADDLIFE", "НовЖ");
	YW_TOOL("DEFAULT_PT_LIFE_GOL", "Жизн");
	YW_TOOL("DEFAULT_PT_LIFE_HLIF", "ВЖиз");
	YW_TOOL("DEFAULT_PT_LIFE_ASIM", "Асм.");
	YW_TOOL("DEFAULT_PT_LIFE_2X2", "2х2");
	YW_TOOL("DEFAULT_PT_LIFE_DANI", "ДнНч");
	YW_TOOL("DEFAULT_PT_LIFE_AMOE", "Амёб");
	YW_TOOL("DEFAULT_PT_LIFE_MOVE", "Ход");
	YW_TOOL("DEFAULT_PT_LIFE_PGOL", "ПЖиз");
	YW_TOOL("DEFAULT_PT_LIFE_DMOE", "ДАмб");
	YW_TOOL("DEFAULT_PT_LIFE_3-4", "3-4");
	YW_TOOL("DEFAULT_PT_LIFE_LLIF", "ДЖиз");
	YW_TOOL("DEFAULT_PT_LIFE_STAN", "Пятн");
	YW_TOOL("DEFAULT_PT_LIFE_SEED", "Зёрна");
	YW_TOOL("DEFAULT_PT_LIFE_MAZE", "Лаб.");
	YW_TOOL("DEFAULT_PT_LIFE_COAG", "Сгуст");
	YW_TOOL("DEFAULT_PT_LIFE_WALL", "Гор.");
	YW_TOOL("DEFAULT_PT_LIFE_GNAR", "Узор");
	YW_TOOL("DEFAULT_PT_LIFE_REPL", "Копия");
	YW_TOOL("DEFAULT_PT_LIFE_MYST", "Тайна");
	YW_TOOL("DEFAULT_PT_LIFE_LOTE", "Край");
	YW_TOOL("DEFAULT_PT_LIFE_FRG2", "Ляг2");
	YW_TOOL("DEFAULT_PT_LIFE_STAR", "Звзд");
	YW_TOOL("DEFAULT_PT_LIFE_FROG", "Ляг.");
	YW_TOOL("DEFAULT_PT_LIFE_BRAN", "Бр6");
#undef YW_TOOL

	if (identifier.BeginsWith("DEFAULT_PT_LIFECUST_"))
		return name;

	// Every built-in element has a localized description in the Yandex build.
	// For less common tools derive a compact visible label from its first
	// localized word instead of exposing the upstream English abbreviation.
	String label = description;
	if (String::Split split = label.SplitBy('.'))
		label = split.Before();
	if (String::Split split = label.SplitBy(':'))
		label = split.Before();
	if (String::Split split = label.SplitBy(' '))
		label = split.Before();
	if (!label.size())
		return YandexWebCompactToolButtonText(name);
	return YandexWebCompactToolButtonText(label);
}
''', encoding="utf-8")

def include_locale(path, anchor):
    source = path.read_text(encoding="utf-8")
    if '#include "YandexWebLocale.h"' not in source:
        if anchor not in source:
            raise SystemExit(f"Locale include anchor not found: {path}")
        source = source.replace(anchor, anchor + '#include "YandexWebLocale.h"\n', 1)
        path.write_text(source, encoding="utf-8")

include_locale(game_view, '#include "Config.h"\n')
include_locale(local_browser, '#include "SimulationConfig.h"\n')
include_locale(local_save, '#include "Config.h"\n')
include_locale(options_view, '#include "Config.h"\n')
include_locale(simulation_data, '#include "simulation/elements/PIPE.h"\n')
include_locale(local_browser_controller, '#include "Controller.h"\n')
include_locale(engine_cpp, '#include "Config.h"\n')
include_locale(button_cpp, '#include "gui/interface/Button.h"\n')
include_locale(button_h, '#include "common/String.h"\n')
include_locale(checkbox_cpp, '#include "Checkbox.h"\n')
include_locale(drop_down_cpp, '#include "DropDown.h"\n')
include_locale(textbox_cpp, '#include "Textbox.h"\n')
include_locale(save_button_cpp, '#include "SimulationConfig.h"\n')
include_locale(label_cpp, '#include "graphics/FontReader.h"\n')
include_locale(copy_text_button_cpp, '#include "Label.h"\n')
include_locale(game_controller_cpp, '#include "Config.h"\n')
include_locale(game_model_cpp, '#include "Config.h"\n')
include_locale(quick_options_cpp, '#include "simulation/Simulation.h"\n')
include_locale(intro_text_h, '#include "common/String.h"\n')
include_locale(property_tool_cpp, '#include "Format.h"\n')
include_locale(sign_tool_cpp, '#include "graphics/Graphics.h"\n')
include_locale(element_search_cpp, '#include "graphics/Graphics.h"\n')
include_locale(render_view_cpp, '#include "gui/game/GameView.h"\n')
include_locale(file_browser_cpp, '#include "Config.h"\n')
include_locale(colour_picker_cpp, '#include "graphics/Graphics.h"\n')
include_locale(confirm_prompt_cpp, '#include "graphics/Graphics.h"\n')
include_locale(error_message_cpp, '#include "graphics/Graphics.h"\n')
include_locale(text_prompt_cpp, '#include "graphics/Graphics.h"\n')
include_locale(information_message_cpp, '#include "graphics/Graphics.h"\n')
include_locale(credits_cpp, '#include "gui/interface/Separator.h"\n')
include_locale(gol_tool_cpp, '#include "graphics/Graphics.h"\n')
include_locale(task_window_cpp, '#include "graphics/Graphics.h"\n')
include_locale(client_cpp, '#include "Config.h"\n')
include_locale(powder, '#include "Config.h"\n')

# ToolButton uses a fixed 30px-ish element button width. Upstream truncates
# by character count, which is not sufficient for wider Cyrillic glyphs.
# Fit the painted caption against the real font metrics instead.
tool_button_text = tool_button_cpp.read_text(encoding="utf-8")
tool_button_anchor = """	//don't use "..." on elements that have long names
	buttonDisplayText = ButtonText.Substr(0, 7);
	Component::TextPosition(buttonDisplayText);"""
tool_button_patch = """	// Do not use "..." on element buttons. Fit the actual rendered glyph
	// width so localized Cyrillic labels never paint across neighbouring
	// button borders while retaining as much of the word as possible.
	buttonDisplayText = ButtonText.Substr(0, 7);
	const int yandexWebCaptionWidth = Size.X > 4 ? Size.X - 4 : 0;
	while (buttonDisplayText.size() &&
	       Graphics::TextSize(buttonDisplayText).X > yandexWebCaptionWidth)
	{
		buttonDisplayText =
			buttonDisplayText.Substr(0, buttonDisplayText.size() - 1);
	}
	Component::TextPosition(buttonDisplayText);"""
if tool_button_anchor not in tool_button_text:
    raise SystemExit("ToolButton pixel-width fitting anchor missing")
tool_button_text = tool_button_text.replace(
    tool_button_anchor, tool_button_patch, 1
)
# Reuse the same pixel fitting for subsequent SetText/SetIcon calls.
tool_button_text = tool_button_text.replace(tool_button_patch,
    "\tTextPosition(ButtonText);", 1)
tool_button_text += "\nvoid ToolButton::TextPosition(String text)\n{\n" + tool_button_patch.replace(
    "ButtonText.Substr(0, 7)", "text") + "\n}\n"
tool_button_cpp.write_text(tool_button_text, encoding="utf-8")

tool_button_h_text = tool_button_h.read_text(encoding="utf-8")
tool_button_h_anchor = """	void SetSelectionState(int state);
	int GetSelectionState();
	Tool *tool;"""
tool_button_h_patch = """	void SetSelectionState(int state);
	int GetSelectionState();
#if defined(__EMSCRIPTEN__)
	const String &YandexWebDisplayTextForTest() const { return buttonDisplayText; }
#endif
	Tool *tool;"""
if tool_button_h_anchor not in tool_button_h_text:
    raise SystemExit("ToolButton Web display-text diagnostic anchor missing")
tool_button_h_text = tool_button_h_text.replace(
    tool_button_h_anchor, tool_button_h_patch, 1
)
tool_button_h_text = tool_button_h_text.replace(
    "\tvoid Draw(const ui::Point& screenPos) override;",
    "\tvoid Draw(const ui::Point& screenPos) override;\n\tvoid TextPosition(String text) override;", 1)
tool_button_h.write_text(tool_button_h_text, encoding="utf-8")

# Translate common component-level UI strings in RU mode. This catches rare
# local buttons, tooltips, placeholders and context-menu items that are easy
# to miss with call-site-only localization.
button_text = button_cpp.read_text(encoding="utf-8")
button_ctor_anchor = """Button::Button(Point position, Point size, String buttonText, String toolTip):
	Component(position, size),
	ButtonText(buttonText),
	toolTip(toolTip),"""
button_ctor_patch = """Button::Button(Point position, Point size, String buttonText, String toolTip):
	Component(position, size),
	ButtonText(YandexWebTranslateUi(buttonText)),
	toolTip(YandexWebTranslateUi(toolTip)),"""
if button_ctor_anchor not in button_text:
    raise SystemExit("Button constructor localization anchor missing")
button_text = button_text.replace(button_ctor_anchor, button_ctor_patch, 1)
button_set_anchor = """void Button::SetText(String buttonText)
{
	ButtonText = buttonText;
	TextPosition(ButtonText);
}"""
button_set_patch = """void Button::SetText(String buttonText)
{
	ButtonText = YandexWebTranslateUi(buttonText);
	TextPosition(ButtonText);
}"""
if button_set_anchor not in button_text:
    raise SystemExit("Button::SetText localization anchor missing")
button_text = button_text.replace(button_set_anchor, button_set_patch, 1)

# Apply the same bounded caption layout to every native dialog button.
button_layout_anchor = 'void Button::TextPosition(String ButtonText)\n{\n\tbuttonDisplayText = ButtonText;\n\tif(buttonDisplayText.length())\n\t{\n\t\tif (Graphics::TextSize(buttonDisplayText).X - 1 > Size.X - (Appearance.icon ? 22 : 0))\n\t\t{\n\t\t\tauto it = Graphics::TextFit(buttonDisplayText, Size.X - (Appearance.icon ? 38 : 22));\n\t\t\tbuttonDisplayText.erase(it, buttonDisplayText.end());\n\t\t\tbuttonDisplayText += "...";\n\t\t}\n\t}\n\n\tComponent::TextPosition(buttonDisplayText);\n}\n'
button_layout_patch = 'void Button::TextPosition(String ButtonText)\n{\n\tbuttonDisplayText = ButtonText;\n\tconst int margin = Appearance.Margin.Left + Appearance.Margin.Right;\n\tconst int padding = margin > 4 ? margin : 4;\n\tconst int available = Size.X - padding - (Appearance.icon ? 15 : 0);\n\tconst int captionWidth = available > 0 ? available : 0;\n\tif (YandexWebIsRussian() && Graphics::TextSize(buttonDisplayText).X > captionWidth)\n\t{\n#define YW_SHORT(full, shortText) if (buttonDisplayText == ByteString(full).FromUtf8()) buttonDisplayText = ByteString(shortText).FromUtf8()\n\t\tYW_SHORT("Сохранить", "Сохр.");\n\t\tYW_SHORT("Сохранить как", "Сохр. как");\n\t\tYW_SHORT("Перезапустить", "Заново");\n\t\tYW_SHORT("Копировать", "Копия");\n\t\tYW_SHORT("Переименовать", "Имя");\n\t\tYW_SHORT("Переместить", "Перенос");\n\t\tYW_SHORT("Применить", "Прим.");\n\t\tYW_SHORT("Продолжить", "Далее");\n\t\tYW_SHORT("Перезаписать", "Заменить");\n\t\tYW_SHORT("Подтвердить", "Да");\n\t\tYW_SHORT("Настройки", "Настр.");\n\t\tYW_SHORT("Отображение", "Вид");\n\t\tYW_SHORT("По умолчанию", "Стандарт");\n\t\tYW_SHORT("Обновить", "Обнов.");\n\t\tYW_SHORT("Изменить", "Правка");\n\t\tYW_SHORT("Закрыть", "Закр.");\n\t\tYW_SHORT("Открыть", "Откр.");\n\t\tYW_SHORT("Загрузить", "Загр.");\n\t\tYW_SHORT("Удалить", "Удал.");\n\t\tYW_SHORT("Очистить", "Очист.");\n#undef YW_SHORT\n\t}\n\tif (Graphics::TextSize(buttonDisplayText).X > captionWidth)\n\t{\n\t\tString suffix = ".";\n\t\twhile (buttonDisplayText.size() && Graphics::TextSize(buttonDisplayText + suffix).X > captionWidth)\n\t\t\tbuttonDisplayText = buttonDisplayText.Substr(0, buttonDisplayText.size() - 1);\n\t\tif (Graphics::TextSize(suffix).X <= captionWidth)\n\t\t\tbuttonDisplayText += suffix;\n\t}\n\tComponent::TextPosition(buttonDisplayText);\n}\n'
if button_layout_anchor not in button_text:
    raise SystemExit("Common button layout anchor missing")
button_text = button_text.replace(button_layout_anchor, button_layout_patch, 1)
button_cpp.write_text(button_text, encoding="utf-8")

button_h_text = button_h.read_text(encoding="utf-8")
button_tooltip_anchor = "void SetToolTip(String newToolTip) { toolTip = newToolTip; }"
button_tooltip_patch = "void SetToolTip(String newToolTip) { toolTip = YandexWebTranslateUi(newToolTip); }"
if button_tooltip_anchor not in button_h_text:
    raise SystemExit("Button tooltip localization anchor missing")
button_h_text = button_h_text.replace(button_tooltip_anchor, button_tooltip_patch, 1)
button_h.write_text(button_h_text, encoding="utf-8")

checkbox_text = checkbox_cpp.read_text(encoding="utf-8")
checkbox_ctor_anchor = """Checkbox::Checkbox(ui::Point position, ui::Point size, String text, String toolTip):
	Component(position, size),
	text(text),
	toolTip(toolTip),"""
checkbox_ctor_patch = """Checkbox::Checkbox(ui::Point position, ui::Point size, String text, String toolTip):
	Component(position, size),
	text(YandexWebTranslateUi(text)),
	toolTip(YandexWebTranslateUi(toolTip)),"""
if checkbox_ctor_anchor not in checkbox_text:
    raise SystemExit("Checkbox constructor localization anchor missing")
checkbox_text = checkbox_text.replace(checkbox_ctor_anchor, checkbox_ctor_patch, 1)
checkbox_set_anchor = """void Checkbox::SetText(String text)
{
	this->text = text;
}"""
checkbox_set_patch = """void Checkbox::SetText(String text)
{
	this->text = YandexWebTranslateUi(text);
}"""
if checkbox_set_anchor not in checkbox_text:
    raise SystemExit("Checkbox::SetText localization anchor missing")
checkbox_text = checkbox_text.replace(checkbox_set_anchor, checkbox_set_patch, 1)
checkbox_cpp.write_text(checkbox_text, encoding="utf-8")

drop_down_text = drop_down_cpp.read_text(encoding="utf-8")
drop_draw_anchor = """		if(optionIndex!=-1)
			TextPosition(options[optionIndex].first);"""
drop_draw_patch = """		if(optionIndex!=-1)
			TextPosition(YandexWebTranslateUi(options[optionIndex].first));"""
if drop_draw_anchor not in drop_down_text:
    raise SystemExit("DropDown text-position localization anchor missing")
drop_down_text = drop_down_text.replace(drop_draw_anchor, drop_draw_patch, 1)
drop_blend_anchor = """	if(optionIndex!=-1)
		g->BlendText(Position + textPosition, options[optionIndex].first, textColour);"""
drop_blend_patch = """	if(optionIndex!=-1)
		g->BlendText(Position + textPosition, YandexWebTranslateUi(options[optionIndex].first), textColour);"""
if drop_blend_anchor not in drop_down_text:
    raise SystemExit("DropDown draw localization anchor missing")
drop_down_text = drop_down_text.replace(drop_blend_anchor, drop_blend_patch, 1)
drop_down_cpp.write_text(drop_down_text, encoding="utf-8")

context_menu_text = context_menu_h.read_text(encoding="utf-8")
context_item_anchor = "ContextMenuItem(String text, int id, bool enabled) : ID(id), Text(text), Enabled(enabled) {}"
context_item_patch = "ContextMenuItem(String text, int id, bool enabled) : ID(id), Text(YandexWebTranslateUi(text)), Enabled(enabled) {}"
if context_item_anchor not in context_menu_text:
    raise SystemExit("ContextMenuItem localization anchor missing")
context_menu_text = context_menu_text.replace(context_item_anchor, context_item_patch, 1)
context_menu_h.write_text(context_menu_text, encoding="utf-8")

label_text = label_cpp.read_text(encoding="utf-8")
label_ctor_anchor = "		SetText(labelText);"
label_ctor_patch = "		SetText(YandexWebTranslateUi(labelText));"
if label_ctor_anchor not in label_text:
    raise SystemExit("Label constructor localization anchor missing")
label_text = label_text.replace(label_ctor_anchor, label_ctor_patch, 1)
label_cpp.write_text(label_text, encoding="utf-8")

textbox_text = textbox_cpp.read_text(encoding="utf-8")
placeholder_anchor = "	placeHolder = textboxPlaceholder;"
placeholder_patch = "	placeHolder = YandexWebTranslateUi(textboxPlaceholder);"
if placeholder_anchor not in textbox_text:
    raise SystemExit("Textbox placeholder localization anchor missing")
textbox_text = textbox_text.replace(placeholder_anchor, placeholder_patch, 1)
set_placeholder_anchor = """void Textbox::SetPlaceholder(String text)
{
	placeHolder = text;
}"""
set_placeholder_patch = """void Textbox::SetPlaceholder(String text)
{
	placeHolder = YandexWebTranslateUi(text);
}"""
if set_placeholder_anchor not in textbox_text:
    raise SystemExit("Textbox::SetPlaceholder localization anchor missing")
textbox_text = textbox_text.replace(set_placeholder_anchor, set_placeholder_patch, 1)
textbox_cpp.write_text(textbox_text, encoding="utf-8")

game_view_text = game_view.read_text(encoding="utf-8")
visible_tool_anchor = "tool->Name, tool->Identifier, tool->Description"
visible_tool_patch = "YandexWebToolButtonText(tool->Identifier, tool->Name, tool->Description), tool->Identifier, tool->Description"
if visible_tool_anchor not in game_view_text:
    raise SystemExit("GameView visible tool-label anchor missing")
game_view_text = game_view_text.replace(visible_tool_anchor, visible_tool_patch, 1)
if 'int GetSplitPosition() const' not in game_view_text:
    game_view_text = game_view_text.replace(
        'bool GetShowSplit() { return showSplit; }',
        'bool GetShowSplit() { return showSplit; }\n\tint GetSplitPosition() const { return splitPosition; }',
        1
    )
if '#include <emscripten.h>' not in game_view_text:
    game_view_text = game_view_text.replace(
        '#include <SDL.h>\n',
        '#include <SDL.h>\n#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n',
        1
    )

# Export real GameView-space centres for browser UI smoke tests. Using
# native integer getters avoids confusing SDL/GameView scale with canvas backing pixels.
ui_geometry_globals = r'''
#if defined(__EMSCRIPTEN__)
static int YandexWeb_TestUiWidth = -1;
static int YandexWeb_TestUiHeight = -1;
static int YandexWeb_TestDustButtonX = -1;
static int YandexWeb_TestDustButtonY = -1;
static int YandexWeb_TestDustButtonRussian = -1;
static int YandexWeb_TestDustButtonTextWidthValue = -1;
static int YandexWeb_TestDustButtonWidthValue = -1;
static int YandexWeb_TestMaxToolButtonOverflowValue = -1;
static int YandexWeb_TestSaveButtonX = -1;
static int YandexWeb_TestSaveButtonY = -1;
static int YandexWeb_TestSettingsButtonX = -1;
static int YandexWeb_TestSettingsButtonY = -1;
static int YandexWeb_TestOpenButtonX = -1;
static int YandexWeb_TestOpenButtonY = -1;
static int YandexWeb_TestServerControlMask = -1;

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestServerControlsVisibleMask() { return YandexWeb_TestServerControlMask; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestNativeFullscreenRequest()
{
	auto &engine = ui::Engine::Ref();
	engine.SetFullscreen(true);
	return engine.GetFullscreen() ? 1 : 0;
}
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetUiWidth() { return YandexWeb_TestUiWidth; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetUiHeight() { return YandexWeb_TestUiHeight; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetDustButtonX() { return YandexWeb_TestDustButtonX; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetDustButtonY() { return YandexWeb_TestDustButtonY; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestDustButtonIsRussian() { return YandexWeb_TestDustButtonRussian; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestDustButtonTextWidth() { return YandexWeb_TestDustButtonTextWidthValue; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestDustButtonWidth() { return YandexWeb_TestDustButtonWidthValue; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestMaxToolButtonOverflow() { return YandexWeb_TestMaxToolButtonOverflowValue; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetSaveButtonX() { return YandexWeb_TestSaveButtonX; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetSaveButtonY() { return YandexWeb_TestSaveButtonY; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetSettingsButtonX() { return YandexWeb_TestSettingsButtonX; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetSettingsButtonY() { return YandexWeb_TestSettingsButtonY; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetOpenButtonX() { return YandexWeb_TestOpenButtonX; }
extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestGetOpenButtonY() { return YandexWeb_TestOpenButtonY; }
#endif

'''
game_view_ctor_anchor = 'GameView::GameView():\n'
if 'YandexWeb_TestGetDustButtonX' not in game_view_text:
    if game_view_ctor_anchor not in game_view_text:
        raise SystemExit("GameView.cpp constructor anchor missing for UI diagnostics")
    game_view_text = game_view_text.replace(
        game_view_ctor_anchor,
        ui_geometry_globals + game_view_ctor_anchor,
        1
    )

ui_geometry_anchor = '\n}\n\nvoid GameView::OnMouseMove(int x, int y, int dx, int dy)\n'
ui_geometry_patch = r'''
#if defined(__EMSCRIPTEN__)
	YandexWeb_TestUiWidth = Size.X;
	YandexWeb_TestUiHeight = Size.Y;

	// Bit 0: login, bit 1: upvote, bit 2: downvote, bit 3: tags.
	// All upstream server/account controls must remain hidden in Yandex Web.
	YandexWeb_TestServerControlMask = 0;
	if (loginButton && loginButton->Visible)
		YandexWeb_TestServerControlMask |= 1;
	if (upVoteButton && upVoteButton->Visible)
		YandexWeb_TestServerControlMask |= 2;
	if (downVoteButton && downVoteButton->Visible)
		YandexWeb_TestServerControlMask |= 4;
	if (tagSimulationButton && tagSimulationButton->Visible)
		YandexWeb_TestServerControlMask |= 8;

	if (saveSimulationButton)
	{
		// Hit the primary/left Save action, not the secondary split action.
		YandexWeb_TestSaveButtonX =
			saveSimulationButton->Position.X + saveSimulationButton->GetSplitPosition() / 2;
		YandexWeb_TestSaveButtonY =
			saveSimulationButton->Position.Y + saveSimulationButton->Size.Y / 2;
	}

	if (simulationOptionButton)
	{
		YandexWeb_TestSettingsButtonX =
			simulationOptionButton->Position.X + simulationOptionButton->Size.X / 2;
		YandexWeb_TestSettingsButtonY =
			simulationOptionButton->Position.Y + simulationOptionButton->Size.Y / 2;
	}

	if (searchButton)
	{
		YandexWeb_TestOpenButtonX =
			searchButton->Position.X + searchButton->Size.X / 2;
		YandexWeb_TestOpenButtonY =
			searchButton->Position.Y + searchButton->Size.Y / 2;
	}

	YandexWeb_TestDustButtonX = -1;
	YandexWeb_TestDustButtonY = -1;
	YandexWeb_TestDustButtonRussian = -1;
	YandexWeb_TestDustButtonTextWidthValue = -1;
	YandexWeb_TestDustButtonWidthValue = -1;
	YandexWeb_TestMaxToolButtonOverflowValue = -1;
	for (auto *button : toolButtons)
	{
		if (!button)
			continue;
		int captionWidth =
			Graphics::TextSize(button->YandexWebDisplayTextForTest()).X;
		int contentWidth = button->Size.X > 4 ? button->Size.X - 4 : 0;
		int overflow = captionWidth - contentWidth;
		if (overflow > YandexWeb_TestMaxToolButtonOverflowValue)
			YandexWeb_TestMaxToolButtonOverflowValue = overflow;
	}
	for (auto *button : toolButtons)
	{
		if (button && button->tool && button->tool->Identifier == "DEFAULT_PT_DUST")
		{
			YandexWeb_TestDustButtonX = button->Position.X + button->Size.X / 2;
			YandexWeb_TestDustButtonY = button->Position.Y + button->Size.Y / 2;
			YandexWeb_TestDustButtonRussian =
				button->GetText() == ByteString("ПЫЛЬ").FromUtf8() ? 1 : 0;
			YandexWeb_TestDustButtonTextWidthValue =
				Graphics::TextSize(button->YandexWebDisplayTextForTest()).X;
			YandexWeb_TestDustButtonWidthValue = button->Size.X;
			break;
		}
	}
#endif
}

void GameView::OnMouseMove(int x, int y, int dx, int dy)
'''
if 'YandexWeb_TestUiWidth = Size.X;' not in game_view_text:
    if ui_geometry_anchor not in game_view_text:
        raise SystemExit("GameView.cpp UI geometry anchor missing")
    game_view_text = game_view_text.replace(ui_geometry_anchor, '\n' + ui_geometry_patch, 1)

game_replacements = [
    ('searchButton->SetToolTip("Open a local simulation.");',
     'searchButton->SetToolTip(YandexWebText("Open a local simulation.", "Открыть локальную симуляцию."));'),
    ('"", "Reload the simulation")',
     '"", YandexWebText("Reload the simulation", "Перезагрузить симуляцию"))'),
    ('"[untitled simulation]", "", "", 19)',
     'YandexWebText("[untitled simulation]", "[без названия]"), "", "", 19)'),
    ('saveSimulationButton->SetText("[untitled simulation]");',
     'saveSimulationButton->SetText(YandexWebText("[untitled simulation]", "[без названия]"));'),
    ('"", "Erase everything")',
     '"", YandexWebText("Erase everything", "Очистить всё"))'),
    ('"", "Settings")',
     '"", YandexWebText("Settings", "Настройки"))'),
    ('"", "Renderer options")',
     '"", YandexWebText("Renderer options", "Настройки отображения"))'),
    ('"", "Pause/Resume the simulation")',
     '"", YandexWebText("Pause/Resume the simulation", "Пауза / продолжить симуляцию"))'),
    ('0xE065, "Search for elements")',
     '0xE065, YandexWebText("Search for elements", "Поиск элементов"))'),
    ('"", "Pick Colour")',
     '"", YandexWebText("Pick Colour", "Выбрать цвет"))'),
    ('"Overwrite the open local simulation."',
     'YandexWebText("Overwrite the open local simulation.", "Перезаписать открытую локальную симуляцию.")'),
    ('"Save the simulation locally in this browser."',
     'YandexWebText("Save the simulation locally in this browser.", "Сохранить симуляцию локально в этом браузере.")'),
    ('searchButton->SetToolTip("Open a simulation from your hard drive.");',
     'searchButton->SetToolTip(YandexWebText("Open a local simulation.", "Открыть локальную симуляцию."));'),
    ('searchButton->SetToolTip("Find & open a simulation. Hold Ctrl to load offline saves.");',
     'searchButton->SetToolTip(YandexWebText("Open a local simulation.", "Открыть локальную симуляцию."));'),
    ('"Decoration Presets."',
     'YandexWebText("Decoration presets", "Наборы цветов")'),
    ('buttonTip = "\\x0F\\xEF\\xEF\\020Click-and-drag to specify an area to create a stamp (right click = cancel)";',
     'buttonTip = YandexWebText("\\x0F\\xEF\\xEF\\020Drag to select an area for a stamp (right click = cancel)", "\\x0F\\xEF\\xEF\\020Выделите область для штампа (правый клик - отмена)");'),
    ('buttonTip = "\\x0F\\xEF\\xEF\\020Click-and-drag to specify an area to copy (right click = cancel)";',
     'buttonTip = YandexWebText("\\x0F\\xEF\\xEF\\020Drag to select an area to copy (right click = cancel)", "\\x0F\\xEF\\xEF\\020Выделите область для копирования (правый клик - отмена)");'),
    ('buttonTip = "\\x0F\\xEF\\xEF\\020Click-and-drag to specify an area to copy then cut (right click = cancel)";',
     'buttonTip = YandexWebText("\\x0F\\xEF\\xEF\\020Drag to select an area to cut (right click = cancel)", "\\x0F\\xEF\\xEF\\020Выделите область для вырезания (правый клик - отмена)");'),
]
for old, new in game_replacements:
    if old in game_view_text:
        game_view_text = game_view_text.replace(old, new)

# Imported upstream saves may contain special online Save/Thread/Search signs.
# In the Yandex build those actions are inert, so do not surface technical
# "unavailable" messages or suggest browser/server functionality to players.
external_sign_tooltip_anchor = '''		StringBuilder tooltip;
		switch (si.second)
		{
		case sign::Type::Save:
			tooltip << "Go to save ID:" << str.Substr(3, si.first - 3);
			break;
		case sign::Type::Thread:
			tooltip << "Open forum thread " << str.Substr(3, si.first - 3) << " in browser";
			break;
		case sign::Type::Search:
			tooltip << "Search for " << str.Substr(3, si.first - 3);
			break;
		default: break;
		}'''
external_sign_tooltip_patch = '''		StringBuilder tooltip;
#if !defined(__EMSCRIPTEN__)
		switch (si.second)
		{
		case sign::Type::Save:
			tooltip << "Go to save ID:" << str.Substr(3, si.first - 3);
			break;
		case sign::Type::Thread:
			tooltip << "Open forum thread " << str.Substr(3, si.first - 3) << " in browser";
			break;
		case sign::Type::Search:
			tooltip << "Search for " << str.Substr(3, si.first - 3);
			break;
		default: break;
		}
#endif'''
if "Imported online-sign tooltips disabled in Yandex Web" not in game_view_text:
    if external_sign_tooltip_anchor not in game_view_text:
        raise SystemExit("GameView.cpp external sign tooltip anchor missing")
    game_view_text = game_view_text.replace(
        external_sign_tooltip_anchor,
        "// Imported online-sign tooltips disabled in Yandex Web.\n" + external_sign_tooltip_patch,
        1,
    )

hud_replacements = [
    ('sampleInfo << "Molten " <<', 'sampleInfo << YandexWebText("Molten ", "Расплав: ") <<'),
    ('<< " with molten " <<', '<< YandexWebText(" with molten ", " с расплавом ") <<'),
    ('<< " with " <<', '<< YandexWebText(" with ", " с ") <<'),
    ('sampleInfo << " (unknown mode)";', 'sampleInfo << YandexWebText(" (unknown mode)", " (неизвестный режим)");'),
    ('sampleInfo << ", Temp: ";', 'sampleInfo << YandexWebText(", Temp: ", ", Темп.: ");'),
    ('sampleInfo << ", Life: " <<', 'sampleInfo << YandexWebText(", Life: ", ", Жизнь: ") <<'),
    ('sampleInfo << ", Tmp: " <<', 'sampleInfo << YandexWebText(", Tmp: ", ", Врем.: ") <<'),
    ('sampleInfo << ", Tmp2: " <<', 'sampleInfo << YandexWebText(", Tmp2: ", ", Врем.2: ") <<'),
    ('sampleInfo << ", Pressure: " <<', 'sampleInfo << YandexWebText(", Pressure: ", ", Давление: ") <<'),
    ('sampleInfo << "Empty, Pressure: " <<', 'sampleInfo << YandexWebText("Empty, Pressure: ", "Пусто, Давление: ") <<'),
    ('sampleInfo << "Empty";', 'sampleInfo << YandexWebText("Empty", "Пусто");'),
    ('sampleInfo << ", AHeat: ";', 'sampleInfo << YandexWebText(", AHeat: ", ", Темп. воздуха: ");'),
    ('fpsInfo << " Parts: " <<', 'fpsInfo << YandexWebText(" Parts: ", " Частиц: ") <<'),
    ('fpsInfo << "\\nSimulation";', 'fpsInfo << YandexWebText("\\nSimulation", "\\nСимуляция");'),
    ('fpsInfo << "\\n  FPS cap: ";', 'fpsInfo << YandexWebText("\\n  FPS cap: ", "\\n  Лимит FPS: ");'),
    ('fpsInfo << "none";', 'fpsInfo << YandexWebText("none", "нет");'),
    ('fpsInfo << "\\nRendering";', 'fpsInfo << YandexWebText("\\nRendering", "\\nРендер");'),
    ('fpsInfo << "\\n  Draw cap: ";', 'fpsInfo << YandexWebText("\\n  Draw cap: ", "\\n  Лимит кадров: ");'),
    ('fpsInfo << "display";', 'fpsInfo << YandexWebText("display", "экран");'),
    ('fpsInfo << ", effective: ";', 'fpsInfo << YandexWebText(", effective: ", ", фактически: ");'),
    ('fpsInfo << "\\n  SRT: ";', 'fpsInfo << YandexWebText("\\n  SRT: ", "\\n  Поток рендера: ");'),
    ('fpsInfo << "disabled";', 'fpsInfo << YandexWebText("disabled", "выкл.");'),
    ('fpsInfo << "enabled";', 'fpsInfo << YandexWebText("enabled", "вкл.");'),
    ('fpsInfo << "hindered";', 'fpsInfo << YandexWebText("hindered", "недоступен");'),
    ('fpsInfo << "\\n  Refresh rate: ";', 'fpsInfo << YandexWebText("\\n  Refresh rate: ", "\\n  Частота экрана: ");'),
    ('fpsInfo << " (default)";', 'fpsInfo << YandexWebText(" (default)", " (по умолчанию)");'),
]
for old, new in hud_replacements:
    if old in game_view_text:
        game_view_text = game_view_text.replace(old, new)

hud_state_replacements = [
    ('fpsInfo << " [REPLACE MODE]";', 'fpsInfo << YandexWebText(" [REPLACE MODE]", " [РЕЖИМ ЗАМЕНЫ]");'),
    ('fpsInfo << " [SPECIFIC DELETE]";', 'fpsInfo << YandexWebText(" [SPECIFIC DELETE]", " [ТОЧЕЧНОЕ УДАЛЕНИЕ]");'),
    ('fpsInfo << " [GRID: " <<', 'fpsInfo << YandexWebText(" [GRID: ", " [СЕТКА: ") <<'),
    ('fpsInfo << " [FIND]";', 'fpsInfo << YandexWebText(" [FIND]", " [ПОИСК]");'),
    ('description += " (Use ctrl+shift+click to toggle the favorite status of an element)";',
     'description += YandexWebText(" (Use ctrl+shift+click to toggle the favorite status of an element)", " (Ctrl+Shift+клик - добавить или убрать элемент из избранного)");'),
]
for old, new in hud_state_replacements:
    if old in game_view_text:
        game_view_text = game_view_text.replace(old, new)

filt_anchor = 'String filtModes[] = {"set colour", "AND", "OR", "AND-NOT", "red shift", "blue shift", "no effect", "XOR", "NOT", "old QRTZ scattering", "variable red shift", "variable blue shift"};'
filt_patch = '''String filtModes[] = {
						YandexWebText("set colour", "задать цвет"),
						"AND",
						"OR",
						"AND-NOT",
						YandexWebText("red shift", "сдвиг к красному"),
						YandexWebText("blue shift", "сдвиг к синему"),
						YandexWebText("no effect", "без эффекта"),
						"XOR",
						"NOT",
						YandexWebText("old QRTZ scattering", "старое рассеяние QRTZ"),
						YandexWebText("variable red shift", "переменный красный сдвиг"),
						YandexWebText("variable blue shift", "переменный синий сдвиг")
					};'''
if filt_anchor in game_view_text:
    game_view_text = game_view_text.replace(filt_anchor, filt_patch, 1)

game_view.write_text(game_view_text, encoding="utf-8")

# Remaining reachable local-only gameplay dialogs.
game_view_text = game_view.read_text(encoding="utf-8")
game_dialog_replacements = [
    (
        'new ErrorMessage("Error loading save", "Dropped file is not a TPT save file (.cps or .stm format)");',
        'new ErrorMessage(YandexWebText("Error loading save", "Ошибка загрузки"), YandexWebText("Dropped file is not a TPT save file (.cps or .stm format)", "Перетащенный файл не является сохранением TPT (.cps или .stm)"));'
    ),
    (
        'new ErrorMessage("Error loading stamp", "Dropped stamp could not be loaded: " + saveFile->GetError());',
        'new ErrorMessage(YandexWebText("Error loading stamp", "Ошибка загрузки штампа"), YandexWebText("Dropped stamp could not be loaded: ", "Не удалось загрузить перетащенный штамп: ") + saveFile->GetError());'
    ),
    (
        'new ErrorMessage("Error loading save", "Dropped save file could not be loaded: " + saveFile->GetError());',
        'new ErrorMessage(YandexWebText("Error loading save", "Ошибка загрузки сохранения"), YandexWebText("Dropped save file could not be loaded: ", "Не удалось загрузить перетащенное сохранение: ") + saveFile->GetError());'
    ),
    (
        'new ConfirmPrompt("Remove custom GOL type", "Are you sure you want to remove " + identifier.Substr(20).FromUtf8() + "?",',
        'new ConfirmPrompt(YandexWebText("Remove custom GOL type", "Удалить пользовательский тип «Жизни»"), YandexWebText("Are you sure you want to remove ", "Удалить тип ") + identifier.Substr(20).FromUtf8() + "?",'
    ),
]
for old, new in game_dialog_replacements:
    if old in game_view_text:
        game_view_text = game_view_text.replace(old, new)
game_view.write_text(game_view_text, encoding="utf-8")

gol_text = gol_tool_cpp.read_text(encoding="utf-8")
gol_replacements = [
    ('"Edit custom GOL type"', 'YandexWebText("Edit custom GOL type", "Пользовательский тип «Жизни»")'),
    ('"[name]"', 'YandexWebText("[name]", "[имя]")'),
    ('"[rule]"', 'YandexWebText("[rule]", "[правило]")'),
    ('new ErrorMessage("Could not add GOL type", "Invalid name provided");',
     'new ErrorMessage(YandexWebText("Could not add GOL type", "Не удалось добавить тип"), YandexWebText("Invalid name provided", "Недопустимое имя"));'),
    ('new ErrorMessage("Could not add GOL type", "Invalid rule provided");',
     'new ErrorMessage(YandexWebText("Could not add GOL type", "Не удалось добавить тип"), YandexWebText("Invalid rule provided", "Недопустимое правило"));'),
    ('new ErrorMessage("Could not add GOL type", "This Custom GoL rule already exists");',
     'new ErrorMessage(YandexWebText("Could not add GOL type", "Не удалось добавить тип"), YandexWebText("This Custom GoL rule already exists", "Такое пользовательское правило уже существует"));'),
    ('new ErrorMessage("Could not add GOL type", "Name already taken");',
     'new ErrorMessage(YandexWebText("Could not add GOL type", "Не удалось добавить тип"), YandexWebText("Name already taken", "Это имя уже занято"));'),
]
for old, new in gol_replacements:
    if old in gol_text:
        gol_text = gol_text.replace(old, new)
gol_tool_cpp.write_text(gol_text, encoding="utf-8")

task_window_text = task_window_cpp.read_text(encoding="utf-8")
task_window_text = task_window_text.replace(
    'new ErrorMessage("Error", task->GetError());',
    'new ErrorMessage(YandexWebText("Error", "Ошибка"), task->GetError());'
)
task_window_text = task_window_text.replace(
    'progressStatus = "Please wait...";',
    'progressStatus = YandexWebText("Please wait...", "Подождите...");'
)
task_window_cpp.write_text(task_window_text, encoding="utf-8")

client_text = client_cpp.read_text(encoding="utf-8")
client_text = client_text.replace(
    'new ErrorMessage("Error renaming stamp", "A stamp with this name already exists.");',
    'new ErrorMessage(YandexWebText("Error renaming stamp", "Ошибка переименования штампа"), YandexWebText("A stamp with this name already exists.", "Штамп с таким именем уже существует."));'
)
client_text = client_text.replace(
    'new ErrorMessage("Error renaming stamp", "Could not rename the stamp.");',
    'new ErrorMessage(YandexWebText("Error renaming stamp", "Ошибка переименования штампа"), YandexWebText("Could not rename the stamp.", "Не удалось переименовать штамп."));'
)
client_cpp.write_text(client_text, encoding="utf-8")

powder_text = powder.read_text(encoding="utf-8")
powder_local_replacements = [
    (
        'new ErrorMessage("Error", "Could not read file");',
        'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Could not read file", "Не удалось прочитать файл"));'
    ),
    (
        'new ErrorMessage("Error", "Could not open save file:\\n" + ByteString(e.what()).FromUtf8()) ;',
        'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Could not open save file:\\n", "Не удалось открыть сохранение:\\n") + ByteString(e.what()).FromUtf8()) ;'
    ),
    (
        'new ErrorMessage("Error", "Could not open file");',
        'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Could not open file", "Не удалось открыть файл"));'
    ),
    (
        'String loadingText = "Loading save...";',
        'String loadingText = YandexWebText("Loading save...", "Загрузка сохранения...");'
    ),
]
for old, new in powder_local_replacements:
    if old in powder_text:
        powder_text = powder_text.replace(old, new)
powder.write_text(powder_text, encoding="utf-8")

browser_text = local_browser.read_text(encoding="utf-8")
browser_replacements = [
    ('String("Next ")', 'YandexWebText("Next ", "Далее ")'),
    ('String(" Prev")', 'YandexWebText(" Prev", " Назад")'),
    ('"Rescan"', 'YandexWebText("Rescan", "Обновить")'),
    ('"[search]"', 'YandexWebText("[search]", "[поиск]")'),
    ('"Page"', 'YandexWebText("Page", "Страница")'),
    ('"Delete"', 'YandexWebText("Delete", "Удалить")'),
    ('"Rename"', 'YandexWebText("Rename", "Переименовать")'),
    ('String::Build("of ", pageCount)', 'String::Build(YandexWebText("of ", "из "), pageCount)'),
]
for old, new in browser_replacements:
    if old in browser_text:
        browser_text = browser_text.replace(old, new)
local_browser.write_text(browser_text, encoding="utf-8")

save_text = local_save.read_text(encoding="utf-8")
if '#include <emscripten.h>' not in save_text:
    save_text = save_text.replace('#include "Config.h"\n', '#include "Config.h"\n#include <emscripten.h>\n', 1)

local_save_diag = r'''static LocalSaveActivity *YandexWeb_TestLocalSaveActivity = nullptr;
static ui::Textbox *YandexWeb_TestLocalSaveFilenameField = nullptr;

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestLocalSaveOpen()
{
	return YandexWeb_TestLocalSaveActivity ? 1 : 0;
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestCaptureLocalSaveFilename()
{
	if (!YandexWeb_TestLocalSaveFilenameField)
	{
		EM_ASM({ window.__tptTestLocalSaveFilename = ''; });
		return;
	}
	auto value = YandexWeb_TestLocalSaveFilenameField->GetText().ToUtf8();
	EM_ASM({
		window.__tptTestLocalSaveFilename = UTF8ToString($0);
	}, value.c_str());
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestCloseLocalSave()
{
	if (YandexWeb_TestLocalSaveActivity)
	{
		auto *activity = YandexWeb_TestLocalSaveActivity;
		YandexWeb_TestLocalSaveActivity = nullptr;
		activity->Exit();
	}
}

'''
ctor_marker = 'LocalSaveActivity::LocalSaveActivity(std::unique_ptr<SaveFile> newSave, OnSaved onSaved_) :'
if local_save_diag not in save_text:
    if ctor_marker not in save_text:
        raise SystemExit("LocalSaveActivity constructor anchor missing")
    save_text = save_text.replace(ctor_marker, local_save_diag + ctor_marker, 1)

ctor_body = '''	onSaved(onSaved_)
{
'''
ctor_body_patch = '''	onSaved(onSaved_)
{
	YandexWeb_TestLocalSaveActivity = this;
'''
if ctor_body in save_text and 'YandexWeb_TestLocalSaveActivity = this;' not in save_text:
    save_text = save_text.replace(ctor_body, ctor_body_patch, 1)

dtor_marker = '''LocalSaveActivity::~LocalSaveActivity()
{
'''
dtor_patch = '''LocalSaveActivity::~LocalSaveActivity()
{
	if (YandexWeb_TestLocalSaveActivity == this)
		YandexWeb_TestLocalSaveActivity = nullptr;
	YandexWeb_TestLocalSaveFilenameField = nullptr;
'''
if dtor_marker in save_text and dtor_patch not in save_text:
    save_text = save_text.replace(dtor_marker, dtor_patch, 1)
filename_field_anchor = '''	filenameField = new ui::Textbox(ui::Point(8, 25), ui::Point(Size.X-16, 16), save->GetDisplayName(), "[filename]");
'''
filename_field_patch = filename_field_anchor + '''	YandexWeb_TestLocalSaveFilenameField = filenameField;
'''
if 'YandexWeb_TestLocalSaveFilenameField = filenameField;' not in save_text:
    if filename_field_anchor not in save_text:
        raise SystemExit("LocalSaveActivity filename field anchor missing")
    save_text = save_text.replace(filename_field_anchor, filename_field_patch, 1)

save_replacements = [
    ('"Save to computer:"', 'YandexWebText("Save locally:", "Локальное сохранение:")'),
    ('"[filename]"', 'YandexWebText("[filename]", "[имя файла]")'),
    ('"Cancel"', 'YandexWebText("Cancel", "Отмена")'),
    ('"Save"', 'YandexWebText("Save", "Сохранить")'),
    ('new ErrorMessage("Error", "Invalid filename.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Invalid filename.", "Недопустимое имя файла."));'),
    ('new ErrorMessage("Error", "You must specify a filename.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("You must specify a filename.", "Укажите имя файла."));'),
    ('new ConfirmPrompt("Overwrite file", "Are you sure you wish to overwrite\\n"+finalFilename.FromUtf8(),',
     'new ConfirmPrompt(YandexWebText("Overwrite file", "Перезаписать файл"), YandexWebText("Are you sure you wish to overwrite\\n", "Перезаписать существующий файл?\\n")+finalFilename.FromUtf8(),'),
    ('new ErrorMessage("Error", "Unable to serialize game data.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Unable to serialize game data.", "Не удалось подготовить данные сохранения."));'),
    ('new ErrorMessage("Error", "Unable to write save file.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Unable to write save file.", "Не удалось записать сохранение."));'),
]
for old, new in save_replacements:
    if old in save_text:
        save_text = save_text.replace(old, new)
local_save.write_text(save_text, encoding="utf-8")

options_text = options_view.read_text(encoding="utf-8")
if '#include <emscripten.h>' not in options_text:
    options_text = options_text.replace(
        '#include <SDL.h>\n',
        '#include <SDL.h>\n#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n',
        1,
    )

options_diag = r'''#if defined(__EMSCRIPTEN__)
static OptionsView *YandexWeb_TestOptionsView = nullptr;
static int YandexWeb_TestThreadedRenderingControlPresent = -1;

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestOptionsOpen()
{
	return YandexWeb_TestOptionsView ? 1 : 0;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestThreadedRenderingPresent()
{
	return YandexWeb_TestThreadedRenderingControlPresent;
}
#endif

'''
options_ctor_anchor = 'OptionsView::OptionsView() : ui::Window(ui::Point(-1, -1), ui::Point(320, 340))\n{'
options_ctor_patch = '''OptionsView::OptionsView() : ui::Window(ui::Point(-1, -1), ui::Point(320, 340))
{
#if defined(__EMSCRIPTEN__)
	YandexWeb_TestOptionsView = this;
#endif'''
if 'YandexWeb_TestOptionsOpen' not in options_text:
    if options_ctor_anchor not in options_text:
        raise SystemExit("OptionsView constructor anchor missing")
    diag_insert_anchor = '#include <SDL.h>\n#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n'
    if diag_insert_anchor not in options_text:
        raise SystemExit("OptionsView diagnostics include anchor missing")
    options_text = options_text.replace(
        diag_insert_anchor,
        diag_insert_anchor + '\n' + options_diag,
        1,
    )
    options_text = options_text.replace(options_ctor_anchor, options_ctor_patch, 1)

options_exit_anchor = '''void OptionsView::OnTryExit(ExitMethod method)
{
	c->Exit();
}'''
options_exit_patch = '''void OptionsView::OnTryExit(ExitMethod method)
{
#if defined(__EMSCRIPTEN__)
	if (YandexWeb_TestOptionsView == this)
		YandexWeb_TestOptionsView = nullptr;
#endif
	c->Exit();
}'''
if 'YandexWeb_TestOptionsView == this' not in options_text:
    if options_exit_anchor not in options_text:
        raise SystemExit("OptionsView exit diagnostic anchor missing")
    options_text = options_text.replace(options_exit_anchor, options_exit_patch, 1)

options_replacements = [
    ('"Settings"', 'YandexWebText("Settings", "Настройки")'),
    ('"Preview"', 'YandexWebText("Preview", "Предпросмотр")'),
    ('"Air simulation mode"', 'YandexWebText("Air simulation mode", "Режим симуляции воздуха")'),
    ('"On"', 'YandexWebText("On", "Вкл.")'),
    ('"Pressure off"', 'YandexWebText("Pressure off", "Без давления")'),
    ('"Velocity off"', 'YandexWebText("Velocity off", "Без скорости")'),
    ('"Off"', 'YandexWebText("Off", "Выкл.")'),
    ('"No update"', 'YandexWebText("No update", "Без обновления")'),
    ('"Ambient air temperature"', 'YandexWebText("Ambient air temperature", "Температура воздуха")'),
    ('"Ambient air pressure"', 'YandexWebText("Ambient air pressure", "Давление воздуха")'),
    ('"Change"', 'YandexWebText("Change", "Изменить")'),
    ('"Ambient air velocity"', 'YandexWebText("Ambient air velocity", "Скорость воздуха")'),
    ('"Vorticity confinement"', 'YandexWebText("Vorticity confinement", "Ограничение завихрения")'),
    ('"Air heat convection mode"', 'YandexWebText("Air heat convection mode", "Режим тепловой конвекции")'),
    ('"None"', 'YandexWebText("None", "Нет")'),
    ('"Legacy"', 'YandexWebText("Legacy", "Классический")'),
    ('"Gravity simulation mode"', 'YandexWebText("Gravity simulation mode", "Режим гравитации")'),
    ('"Vertical"', 'YandexWebText("Vertical", "Вертикальная")'),
    ('"Radial"', 'YandexWebText("Radial", "Радиальная")'),
    ('"Custom"', 'YandexWebText("Custom", "Своя")'),
    ('"Custom Gravity"', 'YandexWebText("Custom Gravity", "Своя гравитация")'),
    ('" Total:"', 'YandexWebText(" Total:", " Модуль:")'),
    ('"Edge mode"', 'YandexWebText("Edge mode", "Режим границ")'),
    ('"Void"', 'YandexWebText("Void", "Пустота")'),
    ('"Solid"', 'YandexWebText("Solid", "Твёрдая граница")'),
    ('"Loop"', 'YandexWebText("Loop", "Цикл")'),
    ('"Temperature scale"', 'YandexWebText("Temperature scale", "Шкала температуры")'),
    ('"Simulation framerate cap"', 'YandexWebText("Simulation framerate cap", "Лимит FPS симуляции")'),
    ('"Rendering framerate cap"', 'YandexWebText("Rendering framerate cap", "Лимит FPS отображения")'),
    ('"Exact"', 'YandexWebText("Exact", "Точный")'),
    ('"Uncapped"', 'YandexWebText("Uncapped", "Без лимита")'),
    ('"Follow display"', 'YandexWebText("Follow display", "По частоте экрана")'),
    ('"Reset"', 'YandexWebText("Reset", "Сбросить")'),
    ('"Credits"', 'YandexWebText("Credits", "Авторы")'),
]
for old, new in options_replacements:
    if old in options_text:
        options_text = options_text.replace(old, new)

extra_options_replacements = [
    ('"Heat simulation \\bgIntroduced in version 34"', 'YandexWebText("Heat simulation \\bgIntroduced in version 34", "Тепловая симуляция \\bgверсия 34+")'),
    ('"Can cause odd behaviour when disabled"', 'YandexWebText("Can cause odd behaviour when disabled", "Отключение может изменить поведение симуляции")'),
    ('"Newtonian gravity \\bgIntroduced in version 48"', 'YandexWebText("Newtonian gravity \\bgIntroduced in version 48", "Ньютоновская гравитация \\bgверсия 48+")'),
    ('"May cause poor performance on older computers"', 'YandexWebText("May cause poor performance on older computers", "Может снижать производительность на слабых устройствах")'),
    ('"Ambient heat simulation \\bgIntroduced in version 50"', 'YandexWebText("Ambient heat simulation \\bgIntroduced in version 50", "Фоновая тепловая симуляция \\bgверсия 50+")'),
    ('"Can cause odd / broken behaviour with many saves"', 'YandexWebText("Can cause odd / broken behaviour with many saves", "Некоторые старые сохранения могут работать иначе")'),
    ('"Water equalisation \\bgIntroduced in version 61"', 'YandexWebText("Water equalisation \\bgIntroduced in version 61", "Выравнивание воды \\bgверсия 61+")'),
    ('"May cause poor performance with a lot of water"', 'YandexWebText("May cause poor performance with a lot of water", "Большое количество воды может снижать FPS")'),
    ('" - Set both limits to sane defaults"', 'YandexWebText(" - Set both limits to sane defaults", " - Вернуть стандартные лимиты")'),
    ('"Window scale factor for larger screens"', 'YandexWebText("Window scale factor for larger screens", "Масштаб интерфейса")'),
    ('"current"', 'YandexWebText("current", "текущий")'),
    ('"Blurry scaling \\bg- more blurry, better on very big screens"', 'YandexWebText("Blurry scaling \\bg- more blurry, better on very big screens", "Сглаженное масштабирование \\bgдля больших экранов")'),
    ('"Momentum (old) scrolling"', 'YandexWebText("Momentum (old) scrolling", "Плавная прокрутка")'),
    ('"Accelerating instead of step scroll"', 'YandexWebText("Accelerating instead of step scroll", "Прокрутка с инерцией")'),
    ('"Sticky categories"', 'YandexWebText("Sticky categories", "Фиксировать категории")'),
    ('"Switch between categories by clicking"', 'YandexWebText("Switch between categories by clicking", "Переключать категории только нажатием")'),
    ('"Include pressure"', 'YandexWebText("Include pressure", "Сохранять давление")'),
    ('"When saving, copying, stamping, etc."', 'YandexWebText("When saving, copying, stamping, etc.", "При сохранении, копировании и создании штампов")'),
    ('"Perfect circle brush"', 'YandexWebText("Perfect circle brush", "Точная круглая кисть")'),
    ('"Better circle brush, without incorrect points on edges"', 'YandexWebText("Better circle brush, without incorrect points on edges", "Более точная форма круглой кисти")'),
    ('"Key under Esc exits console"', 'YandexWebText("Key under Esc exits console", "Клавиша под Esc закрывает консоль")'),
    ('"Disable if that key is 0 on your keyboard"', 'YandexWebText("Disable if that key is 0 on your keyboard", "Отключите, если эта клавиша вводит 0")'),
    ('"Use platform clipboard"', 'YandexWebText("Use platform clipboard", "Использовать системный буфер обмена")'),
    ('"Allows copying and pasting across TPT instances"', 'YandexWebText("Allows copying and pasting across TPT instances", "Позволяет копировать между окнами TPT")'),
    ('"Separate rendering thread"', 'YandexWebText("Separate rendering thread", "Отдельный поток рендера")'),
    ('"May increase framerate when fancy effects are in use"', 'YandexWebText("May increase framerate when fancy effects are in use", "Может повысить FPS с графическими эффектами")'),
    ('"Colour space used by decoration tools"', 'YandexWebText("Colour space used by decoration tools", "Цветовое пространство декораций")'),
    ('"Linear"', 'YandexWebText("Linear", "Линейное")'),
    ('"Save errors and other messages to a file"', 'YandexWebText("Save errors and other messages to a file", "Сохранять ошибки и сообщения в файл")'),
    ('"Developers may ask for this when trying to fix problems"', 'YandexWebText("Developers may ask for this when trying to fix problems", "Полезно для диагностики ошибок")'),
    ('" - Find out who contributed to TPT"', 'YandexWebText(" - Find out who contributed to TPT", " - Участники разработки TPT")'),
    ('"Kelvin"', 'YandexWebText("Kelvin", "Кельвин")'),
    ('"Celsius"', 'YandexWebText("Celsius", "Цельсий")'),
    ('"Fahrenheit"', 'YandexWebText("Fahrenheit", "Фаренгейт")'),
    ('"Resizable \\bg- allow resizing and maximizing window"', 'YandexWebText("Resizable \\bg- allow resizing and maximizing window", "Изменяемый размер \\bg- можно менять размер окна")'),
    ('"Fullscreen \\bg- fill the entire screen"', 'YandexWebText("Fullscreen \\bg- fill the entire screen", "Полный экран \\bg- занять весь экран")'),
    ('"Set optimal screen resolution"', 'YandexWebText("Set optimal screen resolution", "Подобрать разрешение экрана")'),
    ('"Force integer scaling \\bg- less blurry"', 'YandexWebText("Force integer scaling \\bg- less blurry", "Целочисленный масштаб \\bg- более чёткое изображение")'),
    ('"Fast quit"', 'YandexWebText("Fast quit", "Быстрый выход")'),
    ('"Always exit completely when hitting close"', 'YandexWebText("Always exit completely when hitting close", "Полностью завершать игру при закрытии")'),
    ('"Global quit shortcut"', 'YandexWebText("Global quit shortcut", "Глобальная клавиша выхода")'),
    ('"Ctrl+q works everywhere"', 'YandexWebText("Ctrl+q works everywhere", "Ctrl+Q работает во всех окнах")'),
]
for old, new in extra_options_replacements:
    if old in options_text:
        options_text = options_text.replace(old, new)

show_avatars_anchor = '''	showAvatars = addCheckbox(0, "Show avatars", "Disable if you have a slow connection", [this] {
		c->SetShowAvatars(showAvatars->GetChecked());
	});'''
show_avatars_patch = '''	if constexpr (!NOHTTP)
	{
		showAvatars = addCheckbox(0, "Show avatars", "Disable if you have a slow connection", [this] {
			c->SetShowAvatars(showAvatars->GetChecked());
		});
	}'''
if show_avatars_anchor in options_text:
    options_text = options_text.replace(show_avatars_anchor, show_avatars_patch, 1)

startup_anchor = '''	String autoStartupRequestNote = "Done once at startup";
	if (!IGNORE_UPDATES)
	{
		autoStartupRequestNote += ", also checks for updates";
	}
	autoStartupRequest = addCheckbox(0, "Fetch the message of the day and notifications", autoStartupRequestNote, [this] {
		auto checked = autoStartupRequest->GetChecked();
		if (checked)
		{
			Client::Ref().BeginStartupRequest();
		}
		c->SetAutoStartupRequest(checked);
	});
	startupRequestStatus = addButtonWithLabel("Fetch them now", "", []{
		Client::Ref().BeginStartupRequest();
	});
	UpdateStartupRequestStatus();'''
startup_patch = '''	if constexpr (!NOHTTP)
	{
		String autoStartupRequestNote = "Done once at startup";
		if (!IGNORE_UPDATES)
		{
			autoStartupRequestNote += ", also checks for updates";
		}
		autoStartupRequest = addCheckbox(0, "Fetch the message of the day and notifications", autoStartupRequestNote, [this] {
			auto checked = autoStartupRequest->GetChecked();
			if (checked)
			{
				Client::Ref().BeginStartupRequest();
			}
			c->SetAutoStartupRequest(checked);
		});
		startupRequestStatus = addButtonWithLabel("Fetch them now", "", []{
			Client::Ref().BeginStartupRequest();
		});
		UpdateStartupRequestStatus();
	}'''
if startup_anchor in options_text:
    options_text = options_text.replace(startup_anchor, startup_patch, 1)

options_text = options_text.replace(
    'void OptionsView::UpdateStartupRequestStatus()\n{',
    'void OptionsView::UpdateStartupRequestStatus()\n{\n\tif constexpr (NOHTTP)\n\t\treturn;'
)
threaded_rendering_anchor = '''\tthreadedRendering = addCheckbox(0, YandexWebText("Separate rendering thread", "Отдельный поток рендера"), YandexWebText("May increase framerate when fancy effects are in use", "Может повысить FPS с графическими эффектами"), [this] {
\t\tc->SetThreadedRendering(threadedRendering->GetChecked());
\t});'''
threaded_rendering_patch = '''#if !defined(__EMSCRIPTEN__)
\tthreadedRendering = addCheckbox(0, YandexWebText("Separate rendering thread", "Отдельный поток рендера"), YandexWebText("May increase framerate when fancy effects are in use", "Может повысить FPS с графическими эффектами"), [this] {
\t\tc->SetThreadedRendering(threadedRendering->GetChecked());
\t});
#else
\tYandexWeb_TestThreadedRenderingControlPresent = threadedRendering ? 1 : 0;
#endif'''
if threaded_rendering_anchor not in options_text:
    raise SystemExit("OptionsView localized threaded-rendering anchor missing")
options_text = options_text.replace(threaded_rendering_anchor, threaded_rendering_patch, 1)

options_text = options_text.replace(
    '\tshowAvatars->SetChecked(sender->GetShowAvatars());',
    '\tif (showAvatars)\n\t\tshowAvatars->SetChecked(sender->GetShowAvatars());'
)
options_text = options_text.replace(
    '\tautoStartupRequest->SetChecked(sender->GetAutoStartupRequest());',
    '\tif (autoStartupRequest)\n\t\tautoStartupRequest->SetChecked(sender->GetAutoStartupRequest());'
)
options_text = options_text.replace(
    '\tthreadedRendering->SetChecked(sender->GetThreadedRendering());',
    '\tif (threadedRendering)\n\t\tthreadedRendering->SetChecked(sender->GetThreadedRendering());'
)

options_view.write_text(options_text, encoding="utf-8")


simulation_text = simulation_data.read_text(encoding="utf-8")
menu_replacements = [
    ('String("Walls")', 'YandexWebText("Walls", "Стены")'),
    ('String("Electronics")', 'YandexWebText("Electronics", "Электроника")'),
    ('String("Powered Materials")', 'YandexWebText("Powered Materials", "Управляемые материалы")'),
    ('String("Sensors")', 'YandexWebText("Sensors", "Датчики")'),
    ('String("Force")', 'YandexWebText("Force", "Силы")'),
    ('String("Explosives")', 'YandexWebText("Explosives", "Взрывчатка")'),
    ('String("Gases")', 'YandexWebText("Gases", "Газы")'),
    ('String("Liquids")', 'YandexWebText("Liquids", "Жидкости")'),
    ('String("Powders")', 'YandexWebText("Powders", "Порошки")'),
    ('String("Solids")', 'YandexWebText("Solids", "Твёрдые вещества")'),
    ('String("Radioactive")', 'YandexWebText("Radioactive", "Радиоактивные")'),
    ('String("Special")', 'YandexWebText("Special", "Особые")'),
    ('String("Game Of Life")', 'YandexWebText("Game Of Life", "Игра Жизнь")'),
    ('String("Tools")', 'YandexWebText("Tools", "Инструменты")'),
    ('String("Favorites")', 'YandexWebText("Favorites", "Избранное")'),
    ('String("Decoration tools")', 'YandexWebText("Decoration tools", "Декор")'),
]
for old, new in menu_replacements:
    if old in simulation_text:
        simulation_text = simulation_text.replace(old, new)
simulation_data.write_text(simulation_text, encoding="utf-8")

browser_controller_text = local_browser_controller.read_text(encoding="utf-8")
remove_anchor = """void LocalBrowserController::RemoveSelected()
{
	StringBuilder desc;
	desc << "Are you sure you want to delete " << browserModel->GetSelected().size() << " stamp";
	if(browserModel->GetSelected().size()>1)
		desc << "s";
	desc << "?";
	new ConfirmPrompt("Delete stamps", desc.Build(), { [this] { removeSelectedC(); } });
}"""
remove_patch = """void LocalBrowserController::RemoveSelected()
{
	String desc = String::Build(
		YandexWebText("Delete selected saves: ", "Удалить выбранные сохранения: "),
		browserModel->GetSelected().size(),
		"?"
	);
	new ConfirmPrompt(
		YandexWebText("Delete saves", "Удалить сохранения"),
		desc,
		{ [this] { removeSelectedC(); } },
		YandexWebText("Delete", "Удалить")
	);
}"""
if remove_anchor in browser_controller_text:
    browser_controller_text = browser_controller_text.replace(remove_anchor, remove_patch, 1)

browser_controller_text = browser_controller_text.replace(
    'notifyStatus(String::Build("Deleting stamp [", saves[i].FromUtf8(), "] ..."));',
    'notifyStatus(String::Build(YandexWebText("Deleting save [", "Удаление сохранения ["), saves[i].FromUtf8(), "] ..."));'
)
browser_controller_text = browser_controller_text.replace(
    'new TaskWindow("Removing stamps", new RemoveSavesTask(this, selected));',
    'new TaskWindow(YandexWebText("Removing saves", "Удаление сохранений"), new RemoveSavesTask(this, selected));'
)
browser_controller_text = browser_controller_text.replace(
    'new TextPrompt("Rename stamp", "Enter a new name for the stamp:", "", "[new name]", false,',
    'new TextPrompt(YandexWebText("Rename save", "Переименовать сохранение"), YandexWebText("Enter a new name for the save:", "Введите новое имя сохранения:"), "", YandexWebText("[new name]", "[новое имя]"), false,'
)
browser_controller_text = browser_controller_text.replace(
    'new ErrorMessage("Error renaming stamp", "You have to specify the filename.");',
    'new ErrorMessage(YandexWebText("Rename error", "Ошибка переименования"), YandexWebText("You have to specify the filename.", "Укажите имя сохранения."));'
)
local_browser_controller.write_text(browser_controller_text, encoding="utf-8")

engine_text = engine_cpp.read_text(encoding="utf-8")

modal_bridge_helper = r'''
#if defined(__EMSCRIPTEN__)
static void YandexWeb_SetNativeModalBlocked(bool blocked, int depth)
{
	EM_ASM({
		if (window.__tptNativeModalBridge)
			window.__tptNativeModalBridge.setBlocked(!!$0, $1);
	}, blocked ? 1 : 0, depth);
}
#endif

'''
engine_ctor_anchor = 'Engine::Engine():\n'
if 'YandexWeb_SetNativeModalBlocked' not in engine_text:
    if engine_ctor_anchor not in engine_text:
        raise SystemExit("Engine.cpp constructor anchor missing for modal bridge")
    engine_text = engine_text.replace(
        engine_ctor_anchor,
        modal_bridge_helper + engine_ctor_anchor,
        1
    )

show_window_anchor = '''	state_ = window;
	ApplyFpsLimit();
}'''
show_window_patch = '''	state_ = window;
#if defined(__EMSCRIPTEN__)
	YandexWeb_SetNativeModalBlocked(!windows.empty(), int(windows.size()));
#endif
	ApplyFpsLimit();
}'''
if 'YandexWeb_SetNativeModalBlocked(!windows.empty(), int(windows.size()));' not in engine_text:
    if show_window_anchor not in engine_text:
        raise SystemExit("Engine.cpp ShowWindow modal anchor missing")
    engine_text = engine_text.replace(show_window_anchor, show_window_patch, 1)

close_window_pop_anchor = '''		ignoreEvents = true;
		ApplyFpsLimit();
		return 0;'''
close_window_pop_patch = '''		ignoreEvents = true;
#if defined(__EMSCRIPTEN__)
		YandexWeb_SetNativeModalBlocked(!windows.empty(), int(windows.size()));
#endif
		ApplyFpsLimit();
		return 0;'''
if engine_text.count('YandexWeb_SetNativeModalBlocked(!windows.empty(), int(windows.size()));') < 2:
    if close_window_pop_anchor not in engine_text:
        raise SystemExit("Engine.cpp CloseWindow pop modal anchor missing")
    engine_text = engine_text.replace(close_window_pop_anchor, close_window_pop_patch, 1)

close_window_root_anchor = '''		state_ = nullptr;
		ApplyFpsLimit();
		return 1;'''
close_window_root_patch = '''		state_ = nullptr;
#if defined(__EMSCRIPTEN__)
		YandexWeb_SetNativeModalBlocked(false, 0);
#endif
		ApplyFpsLimit();
		return 1;'''
if 'YandexWeb_SetNativeModalBlocked(false, 0);' not in engine_text:
    if close_window_root_anchor not in engine_text:
        raise SystemExit("Engine.cpp CloseWindow root modal anchor missing")
    engine_text = engine_text.replace(close_window_root_anchor, close_window_root_patch, 1)

engine_text = engine_text.replace(
    'new ConfirmPrompt("You are about to quit", "Are you sure you want to exit the game?", { [] {',
    'new ConfirmPrompt(YandexWebText("You are about to quit", "Выход из игры"), YandexWebText("Are you sure you want to exit the game?", "Вы уверены, что хотите выйти из игры?"), { [] {'
)
engine_cpp.write_text(engine_text, encoding="utf-8")

save_button_text = save_button_cpp.read_text(encoding="utf-8")
save_button_replacements = [
    ('new ErrorMessage("Error loading save", file->GetError());',
     'new ErrorMessage(YandexWebText("Error loading save", "Ошибка загрузки сохранения"), file->GetError());'),
    ('ContextMenuItem("Open", 0, true)', 'ContextMenuItem(YandexWebText("Open", "Открыть"), 0, true)'),
    ('ContextMenuItem("Rename", 2, true)', 'ContextMenuItem(YandexWebText("Rename", "Переименовать"), 2, true)'),
    ('ContextMenuItem("Delete", 3, true)', 'ContextMenuItem(YandexWebText("Delete", "Удалить"), 3, true)'),
    ('menu->SetItem(1, "Deselect");', 'menu->SetItem(1, YandexWebText("Deselect", "Снять выбор"));'),
    ('menu->SetItem(1, "Select");', 'menu->SetItem(1, YandexWebText("Select", "Выбрать"));'),
]
for old, new in save_button_replacements:
    if old in save_button_text:
        save_button_text = save_button_text.replace(old, new)
save_button_cpp.write_text(save_button_text, encoding="utf-8")

label_text = label_cpp.read_text(encoding="utf-8")
label_text = label_text.replace(
    'menu->AddItem(ContextMenuItem("Copy", 0, true));',
    'menu->AddItem(ContextMenuItem(YandexWebText("Copy", "Копировать"), 0, true));'
)
label_cpp.write_text(label_text, encoding="utf-8")


quick_text = quick_options_cpp.read_text(encoding="utf-8")
quick_replacements = [
    ('QuickOption("P", "Sand effect", m, Toggle)',
     'QuickOption(YandexWebText("P", "П"), YandexWebText("Sand effect", "Эффект песка"), m, Toggle)'),
    ('QuickOption("G", "Draw gravity field \\bg(ctrl+g)", m, Toggle)',
     'QuickOption(YandexWebText("G", "Г"), YandexWebText("Draw gravity field \\bg(ctrl+g)", "Поле гравитации \\bg(ctrl+g)"), m, Toggle)'),
    ('QuickOption("D", "Draw decorations \\bg(ctrl+b)", m, Toggle)',
     'QuickOption(YandexWebText("D", "Д"), YandexWebText("Draw decorations \\bg(ctrl+b)", "Декорации \\bg(ctrl+b)"), m, Toggle)'),
    ('QuickOption("N", "Newtonian Gravity \\bg(n)", m, Toggle)',
     'QuickOption(YandexWebText("N", "Н"), YandexWebText("Newtonian Gravity \\bg(n)", "Ньютоновская гравитация \\bg(n)"), m, Toggle)'),
    ('QuickOption("A", "Ambient heat \\bg(u)", m, Toggle)',
     'QuickOption(YandexWebText("A", "Т"), YandexWebText("Ambient heat \\bg(u)", "Фоновый нагрев \\bg(u)"), m, Toggle)'),
    ('QuickOption("C", "Show Console \\bg(~)", m, Toggle)',
     'QuickOption(YandexWebText("C", "К"), YandexWebText("Show Console \\bg(~)", "Показать консоль \\bg(~)"), m, Toggle)'),
]
for old, new in quick_replacements:
    if old in quick_text:
        quick_text = quick_text.replace(old, new)
quick_options_cpp.write_text(quick_text, encoding="utf-8")

model_text = game_model_cpp.read_text(encoding="utf-8")
model_replacements = [
    ('SetInfoTip("Decorations Layer: On");',
     'SetInfoTip(YandexWebText("Decorations Layer: On", "Декорации: вкл."));'),
    ('SetInfoTip("Decorations Layer: Off");',
     'SetInfoTip(YandexWebText("Decorations Layer: Off", "Декорации: выкл."));'),
    ('SetInfoTip("Gravity Grid: On");',
     'SetInfoTip(YandexWebText("Gravity Grid: On", "Поле гравитации: вкл."));'),
    ('SetInfoTip("Gravity Grid: Off");',
     'SetInfoTip(YandexWebText("Gravity Grid: Off", "Поле гравитации: выкл."));'),
]
for old, new in model_replacements:
    if old in model_text:
        model_text = model_text.replace(old, new)
game_model_cpp.write_text(model_text, encoding="utf-8")

controller_text = game_controller_cpp.read_text(encoding="utf-8")

install_anchor = '''void GameController::Install()
{
	if constexpr (CAN_INSTALL)
	{
		new ConfirmPrompt("Install " + String(APPNAME), "Do you wish to install " + String(APPNAME) + " on this computer?\\nThis allows you to open save files and saves directly from the website.", { [] {
			if (Platform::Install())
			{
				new InformationMessage("Success", "Installation completed", false);
			}
			else
			{
				new ErrorMessage("Could not install", "The installation did not complete due to an error");
			}
		} });
	}
	else
	{
		new InformationMessage("No installation necessary", "You don't need to install " + String(APPNAME) + " on this platform", false);
	}
}'''
install_patch = '''void GameController::Install()
{
#if defined(__EMSCRIPTEN__)
	// Yandex Web: desktop OS installation is not applicable in a browser.
	return;
#else
	if constexpr (CAN_INSTALL)
	{
		new ConfirmPrompt("Install " + String(APPNAME), "Do you wish to install " + String(APPNAME) + " on this computer?\\nThis allows you to open save files and saves directly from the website.", { [] {
			if (Platform::Install())
			{
				new InformationMessage("Success", "Installation completed", false);
			}
			else
			{
				new ErrorMessage("Could not install", "The installation did not complete due to an error");
			}
		} });
	}
	else
	{
		new InformationMessage("No installation necessary", "You don't need to install " + String(APPNAME) + " on this platform", false);
	}
#endif
}'''
if "Yandex Web: desktop OS installation is not applicable" not in controller_text:
    if install_anchor not in controller_text:
        raise SystemExit("GameController::Install browser guard anchor missing")
    controller_text = controller_text.replace(install_anchor, install_patch, 1)

# Compile upstream online controllers out of the browser build entirely. These
# methods are reachable from more than visible buttons (for example Lua and
# imported online-sign commands), so hiding UI alone is not enough.
def guard_online_controller_method(signature, next_signature):
    global controller_text
    marker = signature + "\n{\n#if defined(__EMSCRIPTEN__)"
    if marker in controller_text:
        return

    start = controller_text.find(signature + "\n{")
    if start < 0:
        raise SystemExit(f"GameController online method anchor missing: {signature}")
    end = controller_text.find(next_signature, start)
    if end < 0:
        raise SystemExit(
            f"GameController next method anchor missing after {signature}: {next_signature}"
        )

    segment = controller_text[start:end]
    segment = segment.replace(
        signature + "\n{",
        signature
        + "\n{\n#if defined(__EMSCRIPTEN__)\n"
        + "\t// Yandex Web: upstream online controller path disabled.\n"
        + "\treturn;\n#else",
        1,
    )
    close = segment.rfind("}\n\n")
    if close < 0:
        raise SystemExit(f"GameController method end missing: {signature}")
    segment = segment[:close] + "#endif\n" + segment[close:]
    controller_text = controller_text[:start] + segment + controller_text[end:]


for signature, next_signature in [
    ("void GameController::OpenSearch(String searchText)", "void GameController::OpenLocalSaveWindow(bool asCurrent)"),
    ("void GameController::OpenSaveDone()", "void GameController::OpenSavePreview(int saveID, int saveDate, SavePreviewType savePreviewType)"),
    ("void GameController::OpenSavePreview(int saveID, int saveDate, SavePreviewType savePreviewType)", "void GameController::OpenSavePreview()"),
    ("void GameController::OpenSavePreview()", "void GameController::OpenLocalBrowse()"),
    ("void GameController::OpenLogin()", "void GameController::OpenProfile()"),
    ("void GameController::OpenProfile()", "void GameController::OpenElementSearch()"),
    ("void GameController::OpenTags()", "void GameController::OpenStamps()"),
]:
    guard_online_controller_method(signature, next_signature)

controller_replacements = [
    ('gameModel->SetInfoTip("Gravity: Vertical");',
     'gameModel->SetInfoTip(YandexWebText("Gravity: Vertical", "Гравитация: вертикальная"));'),
    ('gameModel->SetInfoTip("Gravity: Off");',
     'gameModel->SetInfoTip(YandexWebText("Gravity: Off", "Гравитация: выкл."));'),
    ('gameModel->SetInfoTip("Gravity: Radial");',
     'gameModel->SetInfoTip(YandexWebText("Gravity: Radial", "Гравитация: радиальная"));'),
    ('gameModel->SetInfoTip("Gravity: Custom");',
     'gameModel->SetInfoTip(YandexWebText("Gravity: Custom", "Гравитация: пользовательская"));'),
    ('gameModel->SetInfoTip("Air: On");',
     'gameModel->SetInfoTip(YandexWebText("Air: On", "Воздух: вкл."));'),
    ('gameModel->SetInfoTip("Air: Pressure Off");',
     'gameModel->SetInfoTip(YandexWebText("Air: Pressure Off", "Воздух: без давления"));'),
    ('gameModel->SetInfoTip("Air: Velocity Off");',
     'gameModel->SetInfoTip(YandexWebText("Air: Velocity Off", "Воздух: без скорости"));'),
    ('gameModel->SetInfoTip("Air: Off");',
     'gameModel->SetInfoTip(YandexWebText("Air: Off", "Воздух: выкл."));'),
    ('gameModel->SetInfoTip("Air: No Update");',
     'gameModel->SetInfoTip(YandexWebText("Air: No Update", "Воздух: без обновления"));'),
    ('gameModel->SetInfoTip("Edge Mode: Void");',
     'gameModel->SetInfoTip(YandexWebText("Edge Mode: Void", "Границы: пустота"));'),
    ('gameModel->SetInfoTip("Edge Mode: Solid");',
     'gameModel->SetInfoTip(YandexWebText("Edge Mode: Solid", "Границы: твёрдые"));'),
    ('gameModel->SetInfoTip("Edge Mode: Loop");',
     'gameModel->SetInfoTip(YandexWebText("Edge Mode: Loop", "Границы: цикл"));'),
    ('new ErrorMessage("Error", "Unable to build save.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Unable to build save.", "Не удалось создать сохранение."));'),
    ('new ErrorMessage("Error", "Unable to serialize game data.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Unable to serialize game data.", "Не удалось подготовить данные сохранения."));'),
    ('new ErrorMessage("Error", "Unable to write save file.");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Unable to write save file.", "Не удалось записать сохранение."));'),
    ('gameModel->SetInfoTip("Saved Successfully");',
     'gameModel->SetInfoTip(YandexWebText("Saved Successfully", "Сохранено успешно"));'),
    ('new ErrorMessage("Error loading stamp", file->GetError());',
     'new ErrorMessage(YandexWebText("Error loading save", "Ошибка загрузки сохранения"), file->GetError());'),
    ('new ErrorMessage("Could not create stamp", "Error serializing save file");',
     'new ErrorMessage(YandexWebText("Could not create stamp", "Не удалось создать штамп"), YandexWebText("Error serializing save file", "Не удалось подготовить данные штампа"));'),
    ('new ErrorMessage("Could not create stamp", "Error generating save file");',
     'new ErrorMessage(YandexWebText("Could not create stamp", "Не удалось создать штамп"), YandexWebText("Error generating save file", "Не удалось создать данные штампа"));'),
]
for old, new in controller_replacements:
    if old in controller_text:
        controller_text = controller_text.replace(old, new)

# Imported saves may contain special signs that point to the upstream website.
# Keep local button signs functional, but make online save/thread/search signs inert.
sign_action_replacements = [
    ('''\t\t\t\t\tcase sign::Type::Save:
\t\t\t\t\t\t{
\t\t\t\t\t\t\tint saveID = str.Substr(3, si.first - 3).ToNumber<int>(true);
\t\t\t\t\t\t\tif (saveID)
\t\t\t\t\t\t\t\tOpenSavePreview(saveID, 0, savePreviewNormal);
\t\t\t\t\t\t}
\t\t\t\t\t\tbreak;''',
     '''\t\t\t\t\tcase sign::Type::Save:
#if !defined(__EMSCRIPTEN__)
\t\t\t\t\t\t{
\t\t\t\t\t\t\tint saveID = str.Substr(3, si.first - 3).ToNumber<int>(true);
\t\t\t\t\t\t\tif (saveID)
\t\t\t\t\t\t\t\tOpenSavePreview(saveID, 0, savePreviewNormal);
\t\t\t\t\t\t}
#endif
\t\t\t\t\t\tbreak;'''),
    ('''\t\t\t\t\tcase sign::Type::Thread:
\t\t\t\t\t\tPlatform::OpenURI(ByteString::Build(SERVER, "/Discussions/Thread/View.html?Thread=", str.Substr(3, si.first - 3).ToUtf8()));
\t\t\t\t\t\tbreak;''',
     '''\t\t\t\t\tcase sign::Type::Thread:
#if !defined(__EMSCRIPTEN__)
\t\t\t\t\t\tPlatform::OpenURI(ByteString::Build(SERVER, "/Discussions/Thread/View.html?Thread=", str.Substr(3, si.first - 3).ToUtf8()));
#endif
\t\t\t\t\t\tbreak;'''),
    ('''\t\t\t\t\tcase sign::Type::Search:
\t\t\t\t\t\tOpenSearch(str.Substr(3, si.first - 3));
\t\t\t\t\t\tbreak;''',
     '''\t\t\t\t\tcase sign::Type::Search:
#if !defined(__EMSCRIPTEN__)
\t\t\t\t\t\tOpenSearch(str.Substr(3, si.first - 3));
#endif
\t\t\t\t\t\tbreak;'''),
]
for old, new in sign_action_replacements:
    if old not in controller_text:
        raise SystemExit("GameController online sign action anchor missing")
    controller_text = controller_text.replace(old, new, 1)

game_controller_cpp.write_text(controller_text, encoding="utf-8")


# Localise wall/tool descriptions while preserving canonical short element/tool names.
simulation_text = simulation_data.read_text(encoding="utf-8")
wall_replacements = [
    ('String("ERASE"),           "DEFAULT_WL_ERASE",  String("Erases walls.")',
     'YandexWebText("ERASE", "СТЕРЕТЬ"),           "DEFAULT_WL_ERASE",  YandexWebText("Erases walls.", "Стирает стены.")'),
    ('String("CONDUCTIVE WALL"), "DEFAULT_WL_CNDTW",  String("Blocks everything. Conductive.")',
     'YandexWebText("CONDUCTIVE WALL", "ПРОВОДЯЩАЯ СТЕНА"), "DEFAULT_WL_CNDTW", YandexWebText("Blocks everything. Conductive.", "Блокирует всё и проводит электричество.")'),
    ('String("EWALL"),           "DEFAULT_WL_EWALL",  String("E-Wall. Becomes transparent when electricity is connected.")',
     'YandexWebText("EWALL", "ЭЛЕКТРОСТЕНА"), "DEFAULT_WL_EWALL", YandexWebText("E-Wall. Becomes transparent when electricity is connected.", "Становится проходимой при подаче электричества.")'),
    ('String("DETECTOR"),        "DEFAULT_WL_DTECT",  String("Detector. Generates electricity when a particle is inside.")',
     'YandexWebText("DETECTOR", "ДЕТЕКТОР"), "DEFAULT_WL_DTECT", YandexWebText("Detector. Generates electricity when a particle is inside.", "Создаёт электричество, когда внутри есть частица.")'),
    ('String("STREAMLINE"),      "DEFAULT_WL_STRM",   String("Streamline. Creates a line that follows air movement.")',
     'YandexWebText("STREAMLINE", "ПОТОК"), "DEFAULT_WL_STRM", YandexWebText("Streamline. Creates a line that follows air movement.", "Показывает линию движения воздуха.")'),
    ('String("FAN"),             "DEFAULT_WL_FAN",    String("Fan. Accelerates air. Use the line tool to set direction and strength.")',
     'YandexWebText("FAN", "ВЕНТИЛЯТОР"), "DEFAULT_WL_FAN", YandexWebText("Fan. Accelerates air. Use the line tool to set direction and strength.", "Ускоряет воздух. Линией задаются направление и сила.")'),
    ('String("LIQUID WALL"),     "DEFAULT_WL_LIQD",   String("Allows liquids, blocks all other particles. Conductive.")',
     'YandexWebText("LIQUID WALL", "СТЕНА ДЛЯ ЖИДКОСТЕЙ"), "DEFAULT_WL_LIQD", YandexWebText("Allows liquids, blocks all other particles. Conductive.", "Пропускает жидкости, блокирует остальные частицы. Проводит ток.")'),
    ('String("ABSORB WALL"),     "DEFAULT_WL_ABSRB",  String("Absorbs particles but lets air currents through.")',
     'YandexWebText("ABSORB WALL", "ПОГЛОЩАЮЩАЯ СТЕНА"), "DEFAULT_WL_ABSRB", YandexWebText("Absorbs particles but lets air currents through.", "Поглощает частицы, но пропускает воздух.")'),
    ('String("WALL"),            "DEFAULT_WL_WALL",   String("Basic wall, blocks everything.")',
     'YandexWebText("WALL", "СТЕНА"), "DEFAULT_WL_WALL", YandexWebText("Basic wall, blocks everything.", "Обычная стена, блокирует всё.")'),
    ('String("AIRONLY WALL"),    "DEFAULT_WL_AIR",    String("Allows air, but blocks all particles.")',
     'YandexWebText("AIRONLY WALL", "ВОЗДУШНАЯ СТЕНА"), "DEFAULT_WL_AIR", YandexWebText("Allows air, but blocks all particles.", "Пропускает воздух, но блокирует частицы.")'),
    ('String("POWDER WALL"),     "DEFAULT_WL_POWDR",  String("Allows powders, blocks all other particles.")',
     'YandexWebText("POWDER WALL", "СТЕНА ДЛЯ ПОРОШКОВ"), "DEFAULT_WL_POWDR", YandexWebText("Allows powders, blocks all other particles.", "Пропускает порошки, блокирует остальные частицы.")'),
    ('String("CONDUCTOR"),       "DEFAULT_WL_CNDTR",  String("Conductor. Allows all particles to pass through and conducts electricity.")',
     'YandexWebText("CONDUCTOR", "ПРОВОДНИК"), "DEFAULT_WL_CNDTR", YandexWebText("Conductor. Allows all particles to pass through and conducts electricity.", "Пропускает частицы и проводит электричество.")'),
    ('String("EHOLE"),           "DEFAULT_WL_EHOLE",  String("E-Hole. absorbs particles, releases them when powered.")',
     'YandexWebText("EHOLE", "ЭЛЕКТРОДЫРА"), "DEFAULT_WL_EHOLE", YandexWebText("E-Hole. absorbs particles, releases them when powered.", "Поглощает частицы и выпускает их при подаче питания.")'),
    ('String("GAS WALL"),        "DEFAULT_WL_GAS",    String("Allows gases, blocks all other particles.")',
     'YandexWebText("GAS WALL", "СТЕНА ДЛЯ ГАЗОВ"), "DEFAULT_WL_GAS", YandexWebText("Allows gases, blocks all other particles.", "Пропускает газы, блокирует остальные частицы.")'),
    ('String("GRAVITY WALL"),    "DEFAULT_WL_GRVTY",  String("Gravity wall. Newtonian Gravity has no effect inside a box drawn with this.")',
     'YandexWebText("GRAVITY WALL", "ГРАВИТАЦИОННАЯ СТЕНА"), "DEFAULT_WL_GRVTY", YandexWebText("Gravity wall. Newtonian Gravity has no effect inside a box drawn with this.", "Ньютоновская гравитация не действует внутри замкнутой области.")'),
    ('String("ENERGY WALL"),     "DEFAULT_WL_ENRGY",  String("Allows energy particles, blocks all other particles.")',
     'YandexWebText("ENERGY WALL", "ЭНЕРГЕТИЧЕСКАЯ СТЕНА"), "DEFAULT_WL_ENRGY", YandexWebText("Allows energy particles, blocks all other particles.", "Пропускает энергетические частицы, блокирует остальные.")'),
    ('String("AIRBLOCK WALL"),   "DEFAULT_WL_NOAIR",  String("Allows all particles, but blocks air.")',
     'YandexWebText("AIRBLOCK WALL", "ВОЗДУХОНЕПРОНИЦАЕМАЯ"), "DEFAULT_WL_NOAIR", YandexWebText("Allows all particles, but blocks air.", "Пропускает частицы, но блокирует воздух.")'),
    ('String("ERASEALL"),        "DEFAULT_WL_ERASEA", String("Erases walls, particles, and signs.")',
     'YandexWebText("ERASEALL", "СТЕРЕТЬ ВСЁ"), "DEFAULT_WL_ERASEA", YandexWebText("Erases walls, particles, and signs.", "Стирает стены, частицы и надписи.")'),
    ('String("STASIS WALL"),     "DEFAULT_WL_STASIS", String("Freezes particles inside the wall in place until powered.")',
     'YandexWebText("STASIS WALL", "СТАЗИС-СТЕНА"), "DEFAULT_WL_STASIS", YandexWebText("Freezes particles inside the wall in place until powered.", "Удерживает частицы неподвижно до подачи питания.")'),
]
for old, new in wall_replacements:
    if old in simulation_text:
        simulation_text = simulation_text.replace(old, new)
simulation_data.write_text(simulation_text, encoding="utf-8")

simtool_translations = {
    "AIR.cpp": ("Air, creates airflow and pressure.", "Воздух: создаёт поток и давление."),
    "VAC.cpp": ("Vacuum, reduces air pressure.", "Вакуум: уменьшает давление воздуха."),
    "MIX.cpp": ("Mixes particles.", "Перемешивает частицы."),
    "AMBP.cpp": ("Increases ambient air temperature.", "Повышает температуру окружающего воздуха."),
    "AMBM.cpp": ("Decreases ambient air temperature.", "Понижает температуру окружающего воздуха."),
    "HEAT.cpp": ("Heats the targeted element.", "Нагревает выбранный элемент."),
    "COOL.cpp": ("Cools the targeted element.", "Охлаждает выбранный элемент."),
    "WIND.cpp": ("Creates air movement.", "Создаёт движение воздуха."),
    "PGRV.cpp": ("Creates a short-lasting gravity well.", "Создаёт кратковременную положительную гравитацию."),
    "NGRV.cpp": ("Creates a short-lasting negative gravity well.", "Создаёт кратковременную отрицательную гравитацию."),
    "CYCL.cpp": ("Cyclone, produces swirling air currents", "Циклон: создаёт закрученные потоки воздуха"),
}
for filename, (english, russian) in simtool_translations.items():
    path = simtools_dir / filename
    source = path.read_text(encoding="utf-8")
    if '#include "YandexWebLocale.h"' not in source:
        include_anchor = '#include "simulation/Simulation.h"\n'
        if include_anchor in source:
            source = source.replace(include_anchor, include_anchor + '#include "YandexWebLocale.h"\n', 1)
        else:
            source = '#include "YandexWebLocale.h"\n' + source
    source = source.replace(
        f'Description = "{english}";',
        f'Description = YandexWebText("{english}", "{russian}");'
    )
    path.write_text(source, encoding="utf-8")


# Central Russian descriptions for the most frequently used elements.
simulation_text = simulation_data.read_text(encoding="utf-8")
element_anchor = """	elements = GetElements();
	init_can_move();"""
element_patch = """	elements = GetElements();
	if (YandexWebIsRussian())
	{
		for (auto &element : elements)
		{
			auto setRu = [&](const char *identifier, const char *description) {
				if (element.Identifier == identifier)
					element.Description = ByteString(description).FromUtf8();
			};
			setRu("DEFAULT_PT_WATR", "Вода. Обычная жидкость.");
			setRu("DEFAULT_PT_DSTW", "Дистиллированная вода. Не проводит электричество.");
			setRu("DEFAULT_PT_SLTW", "Солёная вода. Хорошо проводит электричество.");
			setRu("DEFAULT_PT_WTRV", "Водяной пар.");
			setRu("DEFAULT_PT_ICEI", "Лёд. Замёрзшая вода.");
			setRu("DEFAULT_PT_SNOW", "Снег. Холодный порошок.");
			setRu("DEFAULT_PT_DUST", "Пыль. Лёгкий горючий порошок.");
			setRu("DEFAULT_PT_SAND", "Песок. Обычный сыпучий материал.");
			setRu("DEFAULT_PT_STNE", "Камень. Твёрдый материал.");
			setRu("DEFAULT_PT_ROCK", "Каменная порода.");
			setRu("DEFAULT_PT_BRCK", "Кирпич. Прочный строительный материал.");
			setRu("DEFAULT_PT_DMND", "Алмаз. Очень прочный и практически неразрушимый материал.");
			setRu("DEFAULT_PT_GLAS", "Стекло. Прозрачный твёрдый материал.");
			setRu("DEFAULT_PT_WOOD", "Дерево. Горючий твёрдый материал.");
			setRu("DEFAULT_PT_FIRE", "Огонь. Нагревает и поджигает материалы.");
			setRu("DEFAULT_PT_PLSM", "Плазма. Очень горячий ионизированный газ.");
			setRu("DEFAULT_PT_LAVA", "Лава. Расплавленный материал.");
			setRu("DEFAULT_PT_SMKE", "Дым. Образуется при горении.");
			setRu("DEFAULT_PT_OIL", "Нефть. Горючая жидкость.");
			setRu("DEFAULT_PT_GAS", "Газ. Горючее газообразное вещество.");
			setRu("DEFAULT_PT_DESL", "Дизельное топливо. Горючая жидкость.");
			setRu("DEFAULT_PT_NITR", "Нитроглицерин. Взрывоопасная жидкость.");
			setRu("DEFAULT_PT_GUNP", "Порох. Горит и может создавать давление.");
			setRu("DEFAULT_PT_PLEX", "Пластичная взрывчатка. Детонирует от высокой температуры или давления.");
			setRu("DEFAULT_PT_BOMB", "Бомба. Взрывается при столкновении с материалом.");
			setRu("DEFAULT_PT_THRM", "Термит. Горит при очень высокой температуре.");
			setRu("DEFAULT_PT_METL", "Металл. Проводит тепло и электричество.");
			setRu("DEFAULT_PT_BMTL", "Хрупкий металл. Может разрушаться под давлением.");
			setRu("DEFAULT_PT_IRON", "Железо. Проводящий металл.");
			setRu("DEFAULT_PT_GOLD", "Золото. Хорошо проводит электричество.");
			setRu("DEFAULT_PT_TUNG", "Вольфрам. Очень тугоплавкий металл.");
			setRu("DEFAULT_PT_INSL", "Изолятор. Блокирует тепло, электричество и излучение.");
			setRu("DEFAULT_PT_SPRK", "Искра. Передаёт электрический сигнал через проводники.");
			setRu("DEFAULT_PT_BTRY", "Батарея. Постоянно создаёт электрические искры.");
			setRu("DEFAULT_PT_PSCN", "Положительный кремний. Электронный проводящий материал.");
			setRu("DEFAULT_PT_NSCN", "Отрицательный кремний. Электронный проводящий материал.");
			setRu("DEFAULT_PT_SWCH", "Переключатель. Проводит электричество во включённом состоянии.");
			setRu("DEFAULT_PT_WIFI", "Wi-Fi. Передаёт искру без проводов по каналам.");
			setRu("DEFAULT_PT_WIRE", "Провод. Передаёт цифровой сигнал.");
			setRu("DEFAULT_PT_LCRY", "Жидкий кристалл. Меняет прозрачность при подаче электричества.");
			setRu("DEFAULT_PT_FILT", "Фильтр. Изменяет длину волны проходящих фотонов.");
			setRu("DEFAULT_PT_PHOT", "Фотон. Частица света.");
			setRu("DEFAULT_PT_ELEC", "Электрон. Энергетическая частица с электрическими взаимодействиями.");
			setRu("DEFAULT_PT_NEUT", "Нейтрон. Проникающая частица, вызывающая ядерные реакции.");
			setRu("DEFAULT_PT_PROT", "Протон. Передаёт тепло материалам и удаляет искры.");
			setRu("DEFAULT_PT_URAN", "Уран. Радиоактивный тяжёлый материал.");
			setRu("DEFAULT_PT_PLUT", "Плутоний. Радиоактивный материал, способный к делению.");
			setRu("DEFAULT_PT_DEUT", "Дейтерий. Тяжёлая вода для ядерных реакций.");
			setRu("DEFAULT_PT_CLNE", "Клон. Копирует выбранный тип частиц.");
			setRu("DEFAULT_PT_PCLN", "Управляемый клон. Копирует частицы при подаче питания.");
			setRu("DEFAULT_PT_BCLN", "Клон с разрывом. Создаёт частицы и может пропускать давление.");
			setRu("DEFAULT_PT_CONV", "Конвертер. Преобразует окружающие частицы в выбранный тип.");
			setRu("DEFAULT_PT_VOID", "Пустота. Удаляет попадающие в неё частицы.");
			setRu("DEFAULT_PT_PVOD", "Управляемая пустота. Поглощает частицы при подаче питания.");
			setRu("DEFAULT_PT_BHOL", "Чёрная дыра. Поглощает частицы и нагревается.");
			setRu("DEFAULT_PT_WHOL", "Белая дыра. Отталкивает частицы.");
			setRu("DEFAULT_PT_NBHL", "Чёрная дыра с ньютоновской гравитацией.");
			setRu("DEFAULT_PT_NWHL", "Белая дыра с ньютоновской гравитацией.");
			setRu("DEFAULT_PT_PUMP", "Насос давления. Изменяет давление при активации.");
			setRu("DEFAULT_PT_GPMP", "Гравитационный насос. Изменяет гравитацию при активации.");
			setRu("DEFAULT_PT_FRAY", "Силовой излучатель. Толкает частицы при подаче питания.");
			setRu("DEFAULT_PT_RPEL", "Отталкиватель. Создаёт силу, отталкивающую частицы.");
			setRu("DEFAULT_PT_STKM", "Человек. Управляемый персонаж.");
			setRu("DEFAULT_PT_STKM2", "Второй человек. Управляемый вторым набором клавиш.");
			setRu("DEFAULT_PT_ACID", "Кислота. Растворяет почти всё.");
			setRu("DEFAULT_PT_CAUS", "Едкий газ. Действует подобно кислоте.");
			setRu("DEFAULT_PT_LNTG", "Жидкий азот. Очень холодный, исчезает при контакте с более тёплыми веществами.");
			setRu("DEFAULT_PT_LO2", "Жидкий кислород. Очень холодный и реагирует с огнём.");
			setRu("DEFAULT_PT_MERC", "Ртуть. Меняет объём с температурой и проводит электричество.");
			setRu("DEFAULT_PT_GEL", "Гель. Жидкость с переменной вязкостью и теплопроводностью, поглощает воду.");
			setRu("DEFAULT_PT_SOAP", "Мыло. Создаёт пузыри, смывает декоративный цвет и лечит вирус.");
			setRu("DEFAULT_PT_SPNG", "Губка. Поглощает воду и не является подвижным твёрдым телом.");
			setRu("DEFAULT_PT_SALT", "Соль. Растворяется в воде.");
			setRu("DEFAULT_PT_CLST", "Глиняная пыль. При смешивании с водой образует пасту.");
			setRu("DEFAULT_PT_CO2", "Углекислый газ. Тяжёлый газ, опускается вниз, насыщает воду CO2 и при охлаждении превращается в сухой лёд.");
			setRu("DEFAULT_PT_O2", "Кислород. Газ, легко поддерживающий горение.");
			setRu("DEFAULT_PT_H2", "Водород. Горит с кислородом, образуя воду; при высокой температуре и давлении участвует в синтезе.");
			setRu("DEFAULT_PT_NBLE", "Благородный газ. При искре ионизируется в плазму и быстро рассеивается.");
			setRu("DEFAULT_PT_BOYL", "Газ Бойля. Его давление меняется, при нагреве расширяется.");
			setRu("DEFAULT_PT_FOG", "Туман. Возникает при прохождении электрического тока через изморозь.");
			setRu("DEFAULT_PT_AMTR", "Антиматерия. Уничтожает большинство частиц.");
			setRu("DEFAULT_PT_ANAR", "Антивоздух. Очень лёгкая пыль, противодействующая гравитации и горящая с охлаждением.");
			setRu("DEFAULT_PT_SING", "Сингулярность. Создаёт огромное отрицательное давление и уничтожает всё вокруг.");
			setRu("DEFAULT_PT_DEST", "Разрушительная бомба. Способна пробивать почти любые материалы.");
			setRu("DEFAULT_PT_EXOT", "Экзотическая материя. Взрывается при избытке электронов и имеет необычные реакции.");
			setRu("DEFAULT_PT_WARP", "Искажённая материя. Вытесняет другие элементы.");
			setRu("DEFAULT_PT_VIBR", "Вибраниум. Накапливает энергию и высвобождает её мощным взрывом.");
			setRu("DEFAULT_PT_BVBR", "Разрушенный вибраниум.");
			setRu("DEFAULT_PT_BANG", "ТНТ. Взрывается весь одновременно.");
			setRu("DEFAULT_PT_FUSE", "Фитиль. Медленно горит, загорается при очень высокой температуре или от искры.");
			setRu("DEFAULT_PT_FSEP", "Порошковый фитиль. Медленно горит подобно FUSE.");
			setRu("DEFAULT_PT_FIRW", "Фейерверк. Цветной, запускается огнём.");
			setRu("DEFAULT_PT_FWRK", "Старый тип фейерверка. Активируется нагревом или нейтронами.");
			setRu("DEFAULT_PT_LIGH", "Молния. Размер кисти задаёт размер молнии.");
			setRu("DEFAULT_PT_THDR", "Молния. Очень горячая, повреждает большинство материалов и передаёт ток металлам.");
			setRu("DEFAULT_PT_EMBR", "Искры и угольки, возникающие при взрывах.");
			setRu("DEFAULT_PT_TESC", "Катушка Теслы. Создаёт молнии при подаче искры.");
			setRu("DEFAULT_PT_ARAY", "Излучатель луча. Луч создаёт точки при столкновении.");
			setRu("DEFAULT_PT_BRAY", "Точка луча. Создаётся лучевыми излучателями.");
			setRu("DEFAULT_PT_CRAY", "Излучатель частиц. Создаёт луч частиц заданного типа и длины.");
			setRu("DEFAULT_PT_DRAY", "Дублирующий луч. Копирует линию частиц перед собой.");
			setRu("DEFAULT_PT_DTEC", "Детектор. Создаёт искру, когда рядом находится частица заданного типа.");
			setRu("DEFAULT_PT_PSTN", "Поршень. Толкает частицы; PSCN выдвигает, NSCN втягивает.");
			setRu("DEFAULT_PT_FRME", "Рама. Используется с поршнями для перемещения множества частиц.");
			setRu("DEFAULT_PT_PIPE", "Труба. Перемещает частицы внутри себя.");
			setRu("DEFAULT_PT_PPIP", "Управляемая труба. PSCN включает её, NSCN выключает.");
			setRu("DEFAULT_PT_STOR", "Хранилище. Захватывает одну частицу, хранит её и выпускает при сигнале PSCN.");
			setRu("DEFAULT_PT_DLAY", "Задержка. Проводит сигнал с задержкой, зависящей от температуры.");
			setRu("DEFAULT_PT_HSWC", "Тепловой переключатель. Проводит тепло только в активном состоянии.");
			setRu("DEFAULT_PT_INST", "Мгновенный проводник. PSCN заряжает, NSCN снимает заряд.");
			setRu("DEFAULT_PT_ETRD", "Электрод. При подаче электричества создаёт плазменные дуги.");
			setRu("DEFAULT_PT_NTCT", "NTC-термистор. Проводит при температуре выше 100 °C.");
			setRu("DEFAULT_PT_PTCT", "PTC-термистор. Проводит при температуре ниже 100 °C.");
			setRu("DEFAULT_PT_INWR", "Изолированный провод. Проводит только к PSCN, NSCN, WIFI и SWCH.");
			setRu("DEFAULT_PT_INVIS", "Невидимый материал. Под давлением становится проходимым для частиц.");
			setRu("DEFAULT_PT_LDTC", "Линейный детектор. Ищет частицы по восьми направлениям и создаёт искру с противоположной стороны.");
			setRu("DEFAULT_PT_TSNS", "Датчик температуры. Создаёт искру, если рядом есть более горячая частица.");
			setRu("DEFAULT_PT_PSNS", "Датчик давления. Создаёт искру, когда давление превышает заданный температурой порог.");
			setRu("DEFAULT_PT_VSNS", "Датчик скорости. Создаёт искру, когда рядом частица движется быстрее заданного порога.");
			setRu("DEFAULT_PT_LSNS", "Датчик life. Создаёт искру, когда рядом значение life выше заданного порога.");
			setRu("DEFAULT_PT_ACEL", "Ускоритель. Ускоряет находящиеся рядом частицы.");
			setRu("DEFAULT_PT_DCEL", "Замедлитель. Замедляет находящиеся рядом частицы.");
			setRu("DEFAULT_PT_BASE", "Коррозионная жидкость. Вызывает ржавление проводящих твёрдых веществ и нейтрализует кислоту.");
			setRu("DEFAULT_PT_BCOL", "Разрушенный уголь. Тяжёлые частицы, медленно горят.");
			setRu("DEFAULT_PT_BGLA", "Битое стекло. Тяжёлые частицы, образуются при разрушении стекла давлением и могут плавиться.");
			setRu("DEFAULT_PT_BIZR", "Странная материя. Нарушает обычные фазовые переходы и окрашивает другие элементы.");
			setRu("DEFAULT_PT_BIZRG", "Газообразная странная материя.");
			setRu("DEFAULT_PT_BIZRS", "Твёрдая странная материя.");
			setRu("DEFAULT_PT_BREC", "Сломанная электроника. Возникает после EMP-взрывов; при искрах под давлением может превратиться в EXOT.");
			setRu("DEFAULT_PT_BRMT", "Разрушенный металл. Возникает при ржавлении железа или разрушении металлов давлением.");
			setRu("DEFAULT_PT_C5", "Холодная взрывчатка. Детонирует от контакта с очень холодными веществами.");
			setRu("DEFAULT_PT_CBNW", "Газированная вода. Медленно выделяет CO2.");
			setRu("DEFAULT_PT_CFLM", "Сверххолодное пламя.");
			setRu("DEFAULT_PT_CNCT", "Бетон. Может укладываться на себя или ROCK и разрушается под давлением.");
			setRu("DEFAULT_PT_COAL", "Уголь. Очень медленно горит и краснеет при нагреве.");
			setRu("DEFAULT_PT_CRMC", "Керамика. Становится прочнее под давлением.");
			setRu("DEFAULT_PT_DMG", "Создаёт разрушительное давление и ломает элементы, в которые попадает.");
			setRu("DEFAULT_PT_DRIC", "Сухой лёд. Образуется при охлаждении CO2.");
			setRu("DEFAULT_PT_DYST", "Мёртвые дрожжи.");
			setRu("DEFAULT_PT_E116", "Неудачный эксперимент с общей скоростью частиц.");
			setRu("DEFAULT_PT_EMP", "Электромагнитный импульс. Повреждает активированную электронику.");
			setRu("DEFAULT_PT_FIGH", "Боец. Пытается убить человечков; сначала ему нужно дать элемент-оружие.");
			setRu("DEFAULT_PT_FRZW", "Замораживающая вода. Жидкость, образующаяся при плавлении FRZZ.");
			setRu("DEFAULT_PT_FRZZ", "Замораживающий порошок. При плавлении образует лёд, который постоянно охлаждает окружающее.");
			setRu("DEFAULT_PT_GBMB", "Гравитационная бомба. Прилипает к объекту и создаёт сильный гравитационный толчок.");
			setRu("DEFAULT_PT_GLOW", "Светящийся материал. Светится под давлением.");
			setRu("DEFAULT_PT_GOO", "Деформируется и исчезает под давлением.");
			setRu("DEFAULT_PT_GRAV", "Очень лёгкая пыль. Меняет цвет в зависимости от скорости.");
			setRu("DEFAULT_PT_GRVT", "Гравитоны. Создают ньютоновскую гравитацию.");
			setRu("DEFAULT_PT_HEAC", "Быстрый проводник тепла.");
			setRu("DEFAULT_PT_IGNT", "Воспламенительный шнур. Медленно горит от огня и искр.");
			setRu("DEFAULT_PT_ISOZ", "Изотоп-Z. Радиоактивная жидкость, распадается на фотоны при контакте с PHOT или отрицательном давлении.");
			setRu("DEFAULT_PT_ISZS", "Твёрдая форма ISOZ. Медленно распадается на фотоны.");
			setRu("DEFAULT_PT_LIFE", "Игра Жизнь. Классическое правило B3/S23 и другие клеточные автоматы.");
			setRu("DEFAULT_PT_LITH", "Литий. Реактивный элемент, взрывается при контакте с водой.");
			setRu("DEFAULT_PT_LOLZ", "LOLZ - декоративный элемент.");
			setRu("DEFAULT_PT_LOVE", "LOVE - декоративный элемент.");
			setRu("DEFAULT_PT_LRBD", "Жидкий рубидий.");
			setRu("DEFAULT_PT_MORT", "Паровоз.");
			setRu("DEFAULT_PT_MWAX", "Жидкий воск. Затвердевает в WAX примерно при 45 °C.");
			setRu("DEFAULT_PT_NICE", "Азотный лёд. Очень холодный, при небольшом нагреве плавится в жидкий азот.");
			setRu("DEFAULT_PT_PBCN", "Управляемый разрушаемый клон.");
			setRu("DEFAULT_PT_PLNT", "Растение. Поглощает воду и растёт.");
			setRu("DEFAULT_PT_POLO", "Полоний. Сильно радиоактивен, распадается с выделением нейтронов и тепла.");
			setRu("DEFAULT_PT_PQRT", "Кварцевый порошок. Разрушенная форма QRTZ.");
			setRu("DEFAULT_PT_PRTI", "Вход портала. Частицы входят сюда; канал зависит от температуры.");
			setRu("DEFAULT_PT_PRTO", "Выход портала. Частицы выходят отсюда; канал зависит от температуры.");
			setRu("DEFAULT_PT_PSTE", "Коллоидная паста. Затвердевает под давлением.");
			setRu("DEFAULT_PT_PSTS", "Твёрдая форма PSTE.");
			setRu("DEFAULT_PT_PTNM", "Платина. Катализирует некоторые химические реакции.");
			setRu("DEFAULT_PT_QRTZ", "Кварц. Хрупкий минерал, проводит электричество, на холоде становится ломким и рассеивает фотоны.");
			setRu("DEFAULT_PT_RBDM", "Рубидий. Взрывоопасен, особенно при контакте с водой; имеет низкую температуру плавления.");
			setRu("DEFAULT_PT_RFGL", "Жидкий хладагент.");
			setRu("DEFAULT_PT_RFRG", "Хладагент. Нагревается и сжижается под давлением.");
			setRu("DEFAULT_PT_RIME", "Иней. Возникает при быстром охлаждении пара с переходом сразу в твёрдое состояние.");
			setRu("DEFAULT_PT_RSSS", "Твёрдый резист. Блокирует давление и изолирует электричество, разжижается при контакте с нейтронами.");
			setRu("DEFAULT_PT_RSST", "Резист. Затвердевает от фотонов, разрушается электронами и искрами.");
			setRu("DEFAULT_PT_SAWD", "Опилки. Плавают на воде.");
			setRu("DEFAULT_PT_SEED", "Семена. Поместите на песок и добавьте воду, чтобы вырастить дерево.");
			setRu("DEFAULT_PT_SHLD1", "Щит уровня 1. Растёт вокруг искры и разрушается давлением.");
			setRu("DEFAULT_PT_SHLD2", "Щит уровня 2.");
			setRu("DEFAULT_PT_SHLD3", "Щит уровня 3.");
			setRu("DEFAULT_PT_SHLD4", "Щит уровня 4.");
			setRu("DEFAULT_PT_SLCN", "Кремниевый порошок. Важный ингредиент для создания нескольких материалов.");
			setRu("DEFAULT_PT_SPAWN", "Точка появления STKM.");
			setRu("DEFAULT_PT_SPAWN2", "Точка появления STKM2.");
			setRu("DEFAULT_PT_TRON", "Умные частицы. Движутся по прямой, избегают препятствий и растут со временем.");
			setRu("DEFAULT_PT_TTAN", "Титан. Имеет высокую температуру плавления и полностью блокирует давление воздуха.");
			setRu("DEFAULT_PT_VINE", "Лоза. Может расти вдоль дерева.");
			setRu("DEFAULT_PT_VIRS", "Вирус. Превращает соприкасающиеся материалы в вирус.");
			setRu("DEFAULT_PT_VRSG", "Газообразный вирус. Превращает соприкасающиеся материалы в вирус.");
			setRu("DEFAULT_PT_VRSS", "Твёрдый вирус. Превращает соприкасающиеся материалы в вирус.");
			setRu("DEFAULT_PT_WAX", "Воск. Горючий материал, плавится при умеренно высокой температуре.");
			setRu("DEFAULT_PT_YEST", "Дрожжи. Растут в тепле примерно при 37 °C.");
		}
	}
	init_can_move();"""
if "Central Russian descriptions" not in simulation_text and element_anchor in simulation_text:
    simulation_text = simulation_text.replace(element_anchor, element_patch, 1)
simulation_data.write_text(simulation_text, encoding="utf-8")


intro_text = intro_text_h.read_text(encoding="utf-8")
intro_start = intro_text.find("inline ByteString IntroText()")
if intro_start < 0:
    raise SystemExit("IntroText() not found")
intro_end = intro_text.find("\n}\n", intro_start)
if intro_end < 0:
    raise SystemExit("IntroText() end not found")
intro_end += 3
intro_replacement = r'''inline ByteString IntroText()
{
	ByteStringBuilder sb;
	if (YandexWebIsRussian())
	{
		sb << "\bl\bU" << APPNAME << "\bU - Версия " << DISPLAY_VERSION[0] << "." << DISPLAY_VERSION[1] << "\n"
		      "\n"
		      "\bgНажмите \boF1\bg, чтобы показать или скрыть эту справку.\n"
		      "\n"
		      "\bgВыберите категорию справа, затем материал левой или правой кнопкой мыши.\n"
		      "Рисуйте частицами, удерживая кнопку мыши или касаясь экрана.\n"
		      "Колесо мыши или клавиши \bo[\bg и \bo]\bg меняют размер инструмента. \boTab\bg меняет форму кисти.\n"
		      "\boСредняя кнопка\bg или \boAlt+клик\bg выбирают материал с поля.\n"
		      "\boCtrl+C/V/X\bg - копировать, вставить и вырезать.\n"
		      "При вставке \boR\bg поворачивает, а \boShift+R\bg / \boShift+Ctrl+R\bg отражают область.\n"
		      "\boShift+перетаскивание\bg рисует линии, \boCtrl+перетаскивание\bg - заполненные прямоугольники.\n"
		      "\n"
		      "\boПробел\bg ставит физику на паузу. \boF\bg - один кадр, \boF5\bg - перезапуск симуляции.\n"
		      "\boCtrl+Z\bg - отмена, \boCtrl+Y\bg или \boCtrl+Shift+Z\bg - повтор.\n"
		      "\boS\bg создаёт штамп, \boL\bg загружает последний, \boK\bg открывает библиотеку штампов.\n"
		      "\n"
		      "\bo0-9\bg выбирают режим отображения. \boH\bg включает HUD. \boZ\bg - увеличение.\n"
		      "\boCtrl+F\bg подсвечивает выбранный элемент.\n"
		      "\n"
		      "\bgСохранения хранятся локально в браузере.\n";
	}
	else
	{
		sb << "\bl\bU" << APPNAME << "\bU - Version " << DISPLAY_VERSION[0] << "." << DISPLAY_VERSION[1] << "\n"
		      "\n"
		      "\bgPress \boF1\bg to show or hide this help.\n"
		      "\n"
		      "\bgChoose a category on the right, then select a material with the left or right mouse button.\n"
		      "Draw by holding a mouse button or touching the screen.\n"
		      "Use the mouse wheel or \bo[\bg and \bo]\bg to change tool size. Press \boTab\bg to change brush shape.\n"
		      "\boMiddle click\bg or \boAlt+click\bg samples material from the field.\n"
		      "\boCtrl+C/V/X\bg are copy, paste and cut.\n"
		      "When pasting, \boR\bg rotates; \boShift+R\bg and \boShift+Ctrl+R\bg mirror the selection.\n"
		      "\boShift+drag\bg draws lines; \boCtrl+drag\bg draws filled rectangles.\n"
		      "\n"
		      "\boSpace\bg pauses physics. \boF\bg advances one frame; \boF5\bg reloads the simulation.\n"
		      "\boCtrl+Z\bg is undo; \boCtrl+Y\bg or \boCtrl+Shift+Z\bg is redo.\n"
		      "\boS\bg creates a stamp, \boL\bg loads the latest one, and \boK\bg opens the stamp library.\n"
		      "\n"
		      "\bo0-9\bg selects display modes. \boH\bg toggles the HUD. \boZ\bg enables zoom.\n"
		      "\boCtrl+F\bg highlights the selected element.\n"
		      "\n"
		      "\bgSaves are stored locally in the browser.\n";
	}
	return sb.Build();
}
'''
intro_text = intro_text[:intro_start] + intro_replacement + intro_text[intro_end:]
intro_text_h.write_text(intro_text, encoding="utf-8")

property_text = property_tool_cpp.read_text(encoding="utf-8")
property_replacements = [
    ('ui::Point(Size.X-8, 14), "Edit property")',
     'ui::Point(Size.X-8, 14), YandexWebText("Edit property", "Изменить свойство"))'),
    ('ui::Point(Size.X-16, 16), "", "[value]")',
     'ui::Point(Size.X-16, 16), "", YandexWebText("[value]", "[значение]"))'),
]
for old, new in property_replacements:
    if old in property_text:
        property_text = property_text.replace(old, new)
property_tool_cpp.write_text(property_text, encoding="utf-8")

sign_text = sign_tool_cpp.read_text(encoding="utf-8")
sign_replacements = [
    ('ui::Point(Size.X-8, 15), "New sign")',
     'ui::Point(Size.X-8, 15), YandexWebText("New sign", "Новая надпись"))'),
    ('ui::Point(40, 15), "Pointer:")',
     'ui::Point(40, 15), YandexWebText("Pointer:", "Указатель:"))'),
    ('0xE020 + String(" Left")', '0xE020 + YandexWebText(" Left", " Слева")'),
    ('0xE01E + String(" Middle")', '0xE01E + YandexWebText(" Middle", " Центр")'),
    ('0xE01F + String(" Right")', '0xE01F + YandexWebText(" Right", " Справа")'),
    ('0xE01D + String(" None")', '0xE01D + YandexWebText(" None", " Нет")'),
    ('ui::Point(Size.X-16, 17), "", "[message]")',
     'ui::Point(Size.X-16, 17), "", YandexWebText("[message]", "[текст]"))'),
    ('messageLabel->SetText("Edit sign");',
     'messageLabel->SetText(YandexWebText("Edit sign", "Изменить надпись"));'),
    ('16), "Move")', '16), YandexWebText("Move", "Переместить"))'),
    ('16), "Delete")', '16), YandexWebText("Delete", "Удалить"))'),
]
for old, new in sign_replacements:
    if old in sign_text:
        sign_text = sign_text.replace(old, new)
sign_tool_cpp.write_text(sign_text, encoding="utf-8")

search_text = element_search_cpp.read_text(encoding="utf-8")
search_tool_anchor = "tool->Name, tool->Identifier, tool->Description"
search_tool_patch = "YandexWebToolButtonText(tool->Identifier, tool->Name, tool->Description), tool->Identifier, tool->Description"
if search_tool_anchor not in search_text:
    raise SystemExit("ElementSearch visible tool-label anchor missing")
search_text = search_text.replace(search_tool_anchor, search_tool_patch, 1)
search_replacements = [
    ('ui::Point(Size.X-8, 15), "Element Search")',
     'ui::Point(Size.X-8, 15), YandexWebText("Element Search", "Поиск элементов"))'),
    ('ui::Point((Size.X/2)+1, 15), "Close")',
     'ui::Point((Size.X/2)+1, 15), YandexWebText("Close", "Закрыть"))'),
]
for old, new in search_replacements:
    if old in search_text:
        search_text = search_text.replace(old, new)
element_search_cpp.write_text(search_text, encoding="utf-8")


render_text = render_view_cpp.read_text(encoding="utf-8")
render_replacements = [
    ('"Velocity display mode preset"', 'YandexWebText("Velocity display mode preset", "Режим скорости")'),
    ('"Pressure display mode preset"', 'YandexWebText("Pressure display mode preset", "Режим давления")'),
    ('"Persistent display mode preset"', 'YandexWebText("Persistent display mode preset", "Режим следов")'),
    ('"Fire display mode preset"', 'YandexWebText("Fire display mode preset", "Огненный режим")'),
    ('"Blob display mode preset"', 'YandexWebText("Blob display mode preset", "Объёмный режим")'),
    ('"Heat display mode preset"', 'YandexWebText("Heat display mode preset", "Температурный режим")'),
    ('"Fancy display mode preset"', 'YandexWebText("Fancy display mode preset", "Красивый режим")'),
    ('"Nothing display mode preset"', 'YandexWebText("Nothing display mode preset", "Базовый режим")'),
    ('"Heat gradient display mode preset"', 'YandexWebText("Heat gradient display mode preset", "Градиент температуры")'),
    ('"Alternative Velocity display mode preset"', 'YandexWebText("Alternative Velocity display mode preset", "Альтернативная скорость")'),
    ('"Life display mode preset"', 'YandexWebText("Life display mode preset", "Режим жизни")'),
    ('"Adds Special flare effects to some elements"', 'YandexWebText("Adds Special flare effects to some elements", "Добавляет специальные эффекты некоторым элементам")'),
    ('"Fire effect for gasses"', 'YandexWebText("Fire effect for gasses", "Огненный эффект для газов")'),
    ('"Glow effect on some elements"', 'YandexWebText("Glow effect on some elements", "Свечение некоторых элементов")'),
    ('"Blur effect for liquids"', 'YandexWebText("Blur effect for liquids", "Размытие жидкостей")'),
    ('"Makes everything be drawn like a blob"', 'YandexWebText("Makes everything be drawn like a blob", "Отображает всё более объёмно")'),
    ('"Basic rendering, without this, most things will be invisible"', 'YandexWebText("Basic rendering, without this, most things will be invisible", "Базовый рендер, без него большинство объектов невидимы")'),
    ('"Glow effect on sparks"', 'YandexWebText("Glow effect on sparks", "Свечение искр")'),
    ('"Displays pressure as red and blue, and velocity as white"', 'YandexWebText("Displays pressure as red and blue, and velocity as white", "Давление красным/синим, скорость белым")'),
    ('"Displays pressure, red is positive and blue is negative"', 'YandexWebText("Displays pressure, red is positive and blue is negative", "Давление: красный плюс, синий минус")'),
    ('"Displays the temperature of the air like heat display does"', 'YandexWebText("Displays the temperature of the air like heat display does", "Показывает температуру воздуха")'),
    ('"Gravity lensing, Newtonian Gravity bends light with this on"', 'YandexWebText("Gravity lensing, Newtonian Gravity bends light with this on", "Гравитационное линзирование света")'),
    ('"Element paths persist on the screen for a while"', 'YandexWebText("Element paths persist on the screen for a while", "Следы частиц некоторое время остаются на экране")'),
    ('"Displays temperatures of the elements, dark blue is coldest, pink is hottest"', 'YandexWebText("Displays temperatures of the elements, dark blue is coldest, pink is hottest", "Температура элементов: синий холодный, розовый горячий")'),
    ('"Displays the life value of elements in greyscale gradients"', 'YandexWebText("Displays the life value of elements in greyscale gradients", "Показывает время жизни элементов оттенками серого")'),
    ('"Displays velocity and positive pressure: up/down adds blue, right/left adds red, still pressure adds green"',
     'YandexWebText("Displays velocity and positive pressure: up/down adds blue, right/left adds red, still pressure adds green", "Скорость и положительное давление: вертикаль - синий, горизонталь - красный, неподвижное давление - зелёный")'),
    ('"Displays vorticity, red is clockwise and blue is anticlockwise"',
     'YandexWebText("Displays vorticity, red is clockwise and blue is anticlockwise", "Завихрение: красный - по часовой стрелке, синий - против")'),
    ('"Enables moving solids, stickmen guns, and premium(tm) graphics"',
     'YandexWebText("Enables moving solids, stickmen guns, and premium(tm) graphics", "Включает движущиеся твёрдые тела, оружие человечков и расширенные эффекты")'),
    ('"Changes colors of elements slightly to show heat diffusing through them"',
     'YandexWebText("Changes colors of elements slightly to show heat diffusing through them", "Немного меняет цвета элементов, показывая распространение тепла")'),
    ('"No special effects at all for anything, overrides all other options and deco"',
     'YandexWebText("No special effects at all for anything, overrides all other options and deco", "Отключает специальные эффекты и декорации")'),
]
for old, new in render_replacements:
    if old in render_text:
        render_text = render_text.replace(old, new)
render_view_cpp.write_text(render_text, encoding="utf-8")

file_text = file_browser_cpp.read_text(encoding="utf-8")
if '#include <emscripten.h>' not in file_text:
    include_anchor = '#include <algorithm>\n'
    if include_anchor not in file_text:
        raise SystemExit("FileBrowserActivity emscripten include anchor missing")
    file_text = file_text.replace(
        include_anchor,
        include_anchor + '#if defined(__EMSCRIPTEN__)\n#include <emscripten.h>\n#endif\n',
        1,
    )
if '#include "gui/interface/Engine.h"' not in file_text:
    engine_include_anchor = '#include "gui/interface/SaveButton.h"\n'
    if engine_include_anchor not in file_text:
        raise SystemExit("FileBrowserActivity Engine include anchor missing")
    file_text = file_text.replace(
        engine_include_anchor,
        engine_include_anchor + '#include "gui/interface/Engine.h"\n',
        1,
    )

file_browser_diag = r'''
#if defined(__EMSCRIPTEN__)
static FileBrowserActivity *YandexWeb_TestFileBrowserActivity = nullptr;
static int YandexWeb_TestFileBrowserCount = -1;
static int YandexWeb_TestFileBrowserFirstXValue = -1;
static int YandexWeb_TestFileBrowserFirstYValue = -1;

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFileBrowserOpen()
{
	return YandexWeb_TestFileBrowserActivity ? 1 : 0;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFileBrowserFileCount()
{
	return YandexWeb_TestFileBrowserCount;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFileBrowserFirstX()
{
	return YandexWeb_TestFileBrowserFirstXValue;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFileBrowserFirstY()
{
	return YandexWeb_TestFileBrowserFirstYValue;
}
#endif

'''
file_ctor_anchor = 'FileBrowserActivity::FileBrowserActivity(ByteString directory, OnSelected onSelected_):'
if 'YandexWeb_TestFileBrowserOpen' not in file_text:
    if file_ctor_anchor not in file_text:
        raise SystemExit("FileBrowserActivity constructor anchor missing")
    file_text = file_text.replace(file_ctor_anchor, file_browser_diag + file_ctor_anchor, 1)

file_ctor_body = '''	totalFiles(0)
{
'''
file_ctor_patch = '''	totalFiles(0)
{
#if defined(__EMSCRIPTEN__)
	YandexWeb_TestFileBrowserActivity = this;
	YandexWeb_TestFileBrowserCount = -1;
	YandexWeb_TestFileBrowserFirstXValue = -1;
	YandexWeb_TestFileBrowserFirstYValue = -1;
#endif
'''
if 'YandexWeb_TestFileBrowserActivity = this;' not in file_text:
    if file_ctor_body not in file_text:
        raise SystemExit("FileBrowserActivity constructor body anchor missing")
    file_text = file_text.replace(file_ctor_body, file_ctor_patch, 1)

focus_search_anchor = '\tFocusComponent(textField);\n'
focus_search_patch = '''#if defined(__EMSCRIPTEN__)
\tif (!ui::Engine::Ref().TouchUI)
\t\tFocusComponent(textField);
#else
\tFocusComponent(textField);
#endif
'''
if 'if (!ui::Engine::Ref().TouchUI)' not in file_text:
    if focus_search_anchor not in file_text:
        raise SystemExit("FileBrowserActivity search focus anchor missing")
    file_text = file_text.replace(focus_search_anchor, focus_search_patch, 1)

notify_done_anchor = '''	files = ((LoadFilesTask*)task)->TakeSaveFiles();
	createButtons = true;
	totalFiles = files.size();'''
notify_done_patch = '''	files = ((LoadFilesTask*)task)->TakeSaveFiles();
	createButtons = true;
	totalFiles = files.size();
#if defined(__EMSCRIPTEN__)
	YandexWeb_TestFileBrowserCount = int(totalFiles);
#endif'''
if 'YandexWeb_TestFileBrowserCount = int(totalFiles);' not in file_text:
    if notify_done_anchor not in file_text:
        raise SystemExit("FileBrowserActivity NotifyDone anchor missing")
    file_text = file_text.replace(notify_done_anchor, notify_done_patch, 1)

first_button_anchor = '''\t\t\tsaveButton->SetActionCallback({
\t\t\t\t[this, i] { SelectSave(i); },
\t\t\t\t[this, i] { RenameSave(i); },
\t\t\t\t[this, i] { DeleteSave(i); }
\t\t\t});

\t\t\tprogressBar->SetStatus("Rendering thumbnails");'''
first_button_patch = '''\t\t\tsaveButton->SetActionCallback({
\t\t\t\t[this, i] { SelectSave(i); },
\t\t\t\t[this, i] { RenameSave(i); },
\t\t\t\t[this, i] { DeleteSave(i); }
\t\t\t});
#if defined(__EMSCRIPTEN__)
\t\t\tif (i == 0)
\t\t\t{
\t\t\t\tYandexWeb_TestFileBrowserFirstXValue =
\t\t\t\t\tPosition.X + itemList->Position.X + saveButton->Position.X + saveButton->Size.X / 2;
\t\t\t\tYandexWeb_TestFileBrowserFirstYValue =
\t\t\t\t\tPosition.Y + itemList->Position.Y + saveButton->Position.Y + saveButton->Size.Y / 2;
\t\t\t}
#endif

\t\t\tprogressBar->SetStatus("Rendering thumbnails");'''
if 'Position.X + itemList->Position.X + saveButton->Position.X' not in file_text:
    if first_button_anchor not in file_text:
        raise SystemExit("FileBrowserActivity first SaveButton anchor missing")
    file_text = file_text.replace(first_button_anchor, first_button_patch, 1)

dtor_anchor = '''FileBrowserActivity::~FileBrowserActivity()
{
	cleanup();
}'''
dtor_patch = '''FileBrowserActivity::~FileBrowserActivity()
{
#if defined(__EMSCRIPTEN__)
	if (YandexWeb_TestFileBrowserActivity == this)
	{
		YandexWeb_TestFileBrowserActivity = nullptr;
		YandexWeb_TestFileBrowserCount = -1;
		YandexWeb_TestFileBrowserFirstXValue = -1;
		YandexWeb_TestFileBrowserFirstYValue = -1;
	}
#endif
	cleanup();
}'''
if 'YandexWeb_TestFileBrowserActivity == this' not in file_text:
    if dtor_anchor not in file_text:
        raise SystemExit("FileBrowserActivity destructor anchor missing")
    file_text = file_text.replace(dtor_anchor, dtor_patch, 1)

file_replacements = [
    ('ui::Point(Size.X-8, 18), "Save Browser")',
     'ui::Point(Size.X-8, 18), YandexWebText("Save Browser", "Сохранения"))'),
    ('ui::Point(Size.X-16, 16), "", "[search]")',
     'ui::Point(Size.X-16, 16), "", YandexWebText("[search]", "[поиск]"))'),
    ('ui::Point(200, 17), "No saves found")',
     'ui::Point(200, 17), YandexWebText("No saves found", "Сохранения не найдены"))'),
    ('String deleteMessage = "Are you sure you want to delete " + files[index]->GetDisplayName() + ".cps?";',
     'String deleteMessage = YandexWebText("Are you sure you want to delete ", "Удалить сохранение ") + files[index]->GetDisplayName() + ".cps?";'),
    ('new ConfirmPrompt("Delete Save", deleteMessage,',
     'new ConfirmPrompt(YandexWebText("Delete Save", "Удалить сохранение"), deleteMessage,'),
    ('new TextPrompt("Rename", "Change save name",',
     'new TextPrompt(YandexWebText("Rename", "Переименовать"), YandexWebText("Change save name", "Новое имя сохранения"),'),
    ('new ErrorMessage("Error", "Could not rename file");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("Could not rename file", "Не удалось переименовать файл"));'),
    ('new ErrorMessage("Error", "No save name given");',
     'new ErrorMessage(YandexWebText("Error", "Ошибка"), YandexWebText("No save name given", "Не указано имя сохранения"));'),
    ('progressBar->SetStatus("Loading files");',
     'progressBar->SetStatus(YandexWebText("Loading files", "Загрузка файлов"));'),
    ('progressBar->SetStatus("Rendering thumbnails");',
     'progressBar->SetStatus(YandexWebText("Rendering thumbnails", "Создание миниатюр"));'),
]
for old, new in file_replacements:
    if old in file_text:
        file_text = file_text.replace(old, new)
file_browser_cpp.write_text(file_text, encoding="utf-8")

confirm_text = confirm_prompt_cpp.read_text(encoding="utf-8")
confirm_text = confirm_text.replace(
    'ui::Point(Size.X-75, 16), "Cancel")',
    'ui::Point(Size.X-75, 16), YandexWebText("Cancel", "Отмена"))'
)
confirm_prompt_cpp.write_text(confirm_text, encoding="utf-8")

error_text = error_message_cpp.read_text(encoding="utf-8")
error_text = error_text.replace(
    'ui::Point(Size.X, 16), "Dismiss")',
    'ui::Point(Size.X, 16), YandexWebText("Dismiss", "Закрыть"))'
)
error_message_cpp.write_text(error_text, encoding="utf-8")

text_prompt_text = text_prompt_cpp.read_text(encoding="utf-8")
text_prompt_text = text_prompt_text.replace(
    'ui::Point((Size.X/2)+1, 16), "Cancel")',
    'ui::Point((Size.X/2)+1, 16), YandexWebText("Cancel", "Отмена"))'
)
text_prompt_text = text_prompt_text.replace(
    'ui::Point(Size.X/2, 16), "Okay")',
    'ui::Point(Size.X/2, 16), YandexWebText("Okay", "ОК"))'
)
text_prompt_cpp.write_text(text_prompt_text, encoding="utf-8")

info_text = information_message_cpp.read_text(encoding="utf-8")
info_text = info_text.replace(
    'ui::Point(Size.X, 16), "Dismiss")',
    'ui::Point(Size.X, 16), YandexWebText("Dismiss", "Закрыть"))'
)
information_message_cpp.write_text(info_text, encoding="utf-8")

# Reachable local-only UI that bypasses the generic dialogue classes.
colour_picker_text = colour_picker_cpp.read_text(encoding="utf-8")
colour_done_anchor = 'ui::Button * doneButton = new ui::Button(ui::Point(Size.X-45, Size.Y-23), ui::Point(40, 17), "Done");'
colour_done_patch = 'ui::Button * doneButton = new ui::Button(ui::Point(Size.X-45, Size.Y-23), ui::Point(40, 17), YandexWebText("Done", "Готово"));'
if colour_done_anchor not in colour_picker_text:
    raise SystemExit("ColourPickerActivity Done button anchor missing")
colour_picker_text = colour_picker_text.replace(colour_done_anchor, colour_done_patch, 1)
colour_picker_cpp.write_text(colour_picker_text, encoding="utf-8")

copy_text_button_text = copy_text_button_cpp.read_text(encoding="utf-8")
copied_anchor = 'copyTextLabel->SetText("Copied!");'
copied_patch = 'copyTextLabel->SetText(YandexWebText("Copied!", "Скопировано!"));'
if copied_anchor not in copy_text_button_text:
    raise SystemExit("CopyTextButton copied-status anchor missing")
copy_text_button_text = copy_text_button_text.replace(copied_anchor, copied_patch, 1)
copy_text_button_cpp.write_text(copy_text_button_text, encoding="utf-8")


# Native diagnostics used only by browser CI to prove that real touch input reaches TPT.
model_text = game_model_cpp.read_text(encoding="utf-8")
if '#include <emscripten.h>' not in model_text:
    model_text = model_text.replace('#include <optional>\n', '#include <optional>\n#include <emscripten.h>\n', 1)

diag_anchor = "HistoryEntry::~HistoryEntry()"
diag_block = r'''static GameModel *YandexWeb_TestGameModel = nullptr;

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestParticleCount()
{
	if (!YandexWeb_TestGameModel)
		return -1;
	return YandexWeb_TestGameModel->GetSimulation()->NUM_PARTS;
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestClearSimulation()
{
	if (!YandexWeb_TestGameModel)
		return;
	YandexWeb_TestGameModel->GetSimulation()->clear_sim();
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestWallRenderHint()
{
	if (!YandexWeb_TestGameModel)
		return -1;
	return YandexWeb_TestGameModel->GetSimulation()->yandexWebWallsMayExist ? 1 : 0;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestWallCacheDirty()
{
	if (!YandexWeb_TestGameModel)
		return -1;
	return YandexWeb_TestGameModel->GetSimulation()->yandexWebWallCellsDirty ? 1 : 0;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestWallCacheSize()
{
	if (!YandexWeb_TestGameModel)
		return -1;
	return int(YandexWeb_TestGameModel->GetSimulation()->yandexWebWallCells.size());
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestCreateWallForRenderHint()
{
	if (!YandexWeb_TestGameModel)
		return;
	auto *sim = YandexWeb_TestGameModel->GetSimulation();
	sim->CreateWalls(XCNTR, YCNTR, 0, 0, WL_WALL, nullptr);
}

extern "C" EMSCRIPTEN_KEEPALIVE double YandexWeb_TestEngineFps()
{
	return ui::Engine::Ref().GetFps();
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestDrawFrameIndex()
{
	return int(ui::Engine::Ref().FrameIndex);
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestSetDrawLimit(int fps)
{
	fps = std::max(1, std::min(fps, 1000));
	ui::Engine::Ref().SetDrawingFrequencyLimit(DrawLimitExplicit{ fps });
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestEffectiveDrawCap()
{
	auto cap = ui::Engine::Ref().GetEffectiveDrawCap();
	return cap ? *cap : -1;
}

extern "C" EMSCRIPTEN_KEEPALIVE double YandexWeb_TestSimulationFrameCount()
{
	if (!YandexWeb_TestGameModel)
		return -1.0;
	return double(YandexWeb_TestGameModel->GetSimulation()->frameCount);
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestSetSimulationFpsLimit(int fps)
{
	if (!YandexWeb_TestGameModel || !YandexWeb_TestGameModel->GetView())
		return;
	fps = std::max(3, std::min(fps, 1000));
	YandexWeb_TestGameModel->GetView()->SetSimFpsLimit(FpsLimitExplicit{ float(fps) });
}

extern "C" EMSCRIPTEN_KEEPALIVE double YandexWeb_TestSimulationFpsLimit()
{
	if (!YandexWeb_TestGameModel || !YandexWeb_TestGameModel->GetView())
		return -1.0;
	auto limit = YandexWeb_TestGameModel->GetView()->GetSimFpsLimit();
	if (auto *explicitLimit = std::get_if<FpsLimitExplicit>(&limit))
		return double(explicitLimit->value);
	return 0.0;
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestSelectDust()
{
	if (!YandexWeb_TestGameModel)
		return;
	auto *tool = YandexWeb_TestGameModel->GetToolFromIdentifier("DEFAULT_PT_DUST");
	if (!tool)
		return;
	YandexWeb_TestGameModel->SetActiveTool(0, tool);
	YandexWeb_TestGameModel->SetLastTool(tool);
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestSelectWater()
{
	if (!YandexWeb_TestGameModel)
		return;
	auto *tool = YandexWeb_TestGameModel->GetToolFromIdentifier("DEFAULT_PT_WATR");
	if (!tool)
		return;
	YandexWeb_TestGameModel->SetActiveTool(0, tool);
	YandexWeb_TestGameModel->SetLastTool(tool);
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestActiveToolIsDust()
{
	if (!YandexWeb_TestGameModel)
		return 0;
	auto *tool = YandexWeb_TestGameModel->GetActiveTool(0);
	return tool && tool->Identifier == "DEFAULT_PT_DUST";
}

extern "C" EMSCRIPTEN_KEEPALIVE void YandexWeb_TestOpenLocalSave()
{
	// CI hook: always open the Save dialog instead of silently overwriting the
	// current file, so browser smoke can exercise text input and nested prompts.
	GameController::Ref().OpenLocalSaveWindow(false);
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFillDust(int target)
{
	if (!YandexWeb_TestGameModel)
		return -1;
	auto *sim = YandexWeb_TestGameModel->GetSimulation();
	sim->clear_sim();
	YandexWeb_TestGameModel->SetNewtonianGravity(false);
	target = std::max(0, std::min(target, 50000));
	for (int y = 20; y < YRES - 20 && sim->NUM_PARTS < target; y += 2)
	{
		for (int x = 20; x < XRES - 20 && sim->NUM_PARTS < target; x += 2)
		{
			sim->create_part(-1, x, y, PT_DUST);
		}
	}
	return sim->NUM_PARTS;
}

extern "C" EMSCRIPTEN_KEEPALIVE int YandexWeb_TestFillWaterGravity(int target)
{
	if (!YandexWeb_TestGameModel)
		return -1;
	auto *sim = YandexWeb_TestGameModel->GetSimulation();
	sim->clear_sim();
	YandexWeb_TestGameModel->SetNewtonianGravity(true);
	target = std::max(0, std::min(target, 30000));
	for (int y = 40; y < YRES - 40 && sim->NUM_PARTS < target; y += 2)
	{
		for (int x = 40; x < XRES - 40 && sim->NUM_PARTS < target; x += 2)
		{
			sim->create_part(-1, x, y, PT_WATR);
		}
	}
	return sim->NUM_PARTS;
}

'''
if diag_block not in model_text:
    if diag_anchor not in model_text:
        raise SystemExit("GameModel diagnostics anchor missing")
    model_text = model_text.replace(diag_anchor, diag_block + diag_anchor, 1)

ctor_anchor = '''	view(newView)
{
	sim = Simulation::Factory();'''
ctor_patch = '''	view(newView)
{
	YandexWeb_TestGameModel = this;
	sim = Simulation::Factory();'''
if ctor_anchor in model_text:
    model_text = model_text.replace(ctor_anchor, ctor_patch, 1)

dtor_anchor = '''GameModel::~GameModel()
{
	auto &prefs = GlobalPrefs::Ref();'''
dtor_patch = '''GameModel::~GameModel()
{
	if (YandexWeb_TestGameModel == this)
		YandexWeb_TestGameModel = nullptr;
	auto &prefs = GlobalPrefs::Ref();'''
if dtor_anchor in model_text:
    model_text = model_text.replace(dtor_anchor, dtor_patch, 1)

game_model_cpp.write_text(model_text, encoding="utf-8")


credits_text = credits_cpp.read_text(encoding="utf-8")
credits_replacements = [
    (
        'addHeader("The Powder Toy is an open source project, developed by members of the community.\\n"\n'
        '\t\t\t"We\'d like to thank everyone who contributed to our \\bt{a:https://github.com/The-Powder-Toy/The-Powder-Toy|GitHub repo}\\x0E:", false);',
        'addHeader(YandexWebText('
        '"The Powder Toy is an open source project, developed by members of the community.\\nWe would like to thank everyone who contributed to the project:", '
        '"The Powder Toy - проект с открытым исходным кодом, созданный сообществом.\\nСпасибо всем, кто участвовал в разработке:"'
        '), false);'
    ),
    (
        'addHeader("Staff - volunteers that run the community and keep the site running");',
        'addHeader(YandexWebText("Staff - community volunteers", "Команда - волонтёры сообщества"));'
    ),
    (
        'addHeader("Former Staff", false);',
        'addHeader(YandexWebText("Former Staff", "Бывшие участники команды"), false);'
    ),
    (
        'addHeader("The following users have been credited in the intro text from the start.\\n"\n'
        '\t\t\t"Their contributions to the early beginnings of The Powder Toy were invaluable in shaping it into what it is today.");',
        'addHeader(YandexWebText('
        '"The following users were credited from the earliest versions of The Powder Toy.\\nTheir contributions helped shape the project.", '
        '"Эти участники упоминаются в проекте с самых ранних версий The Powder Toy.\\nИх вклад помог сформировать игру."'
        '));'
    ),
    (
        'auto components = AddCredit(username.FromUtf8(), "", Large, GetProfileUri(username), true);',
        'auto components = AddCredit(username.FromUtf8(), "", Large, "", false);'
    ),
    (
        'auto components = AddCredit(username.FromUtf8(), "", Small, "", true);',
        'auto components = AddCredit(username.FromUtf8(), "", Small, "", false);'
    ),
    (
        'auto *closeButton = new ui::Button({ 0, Size.Y - 12 }, { Size.X, 12 }, "Close");',
        'auto *closeButton = new ui::Button({ 0, Size.Y - 12 }, { Size.X, 12 }, YandexWebText("Close", "Закрыть"));'
    ),
    (
        'return "https://powdertoy.co.uk/User.html?Name=" + username;',
        'return "";'
    ),
]
for old, new in credits_replacements:
    if old in credits_text:
        credits_text = credits_text.replace(old, new)
credits_cpp.write_text(credits_text, encoding="utf-8")


# Yandex mobile: mark buttons without RTTI so touch hit testing works with -fno-rtti.
component_text = component_h.read_text(encoding="utf-8")
component_anchor = "\t\tvirtual ~Component();\n"
component_patch = "\t\tvirtual ~Component();\n\t\tvirtual bool IsButton() const { return false; }\n"
if "virtual bool IsButton() const" not in component_text:
    if component_anchor not in component_text:
        raise SystemExit("Component.h button marker anchor missing")
    component_text = component_text.replace(component_anchor, component_patch, 1)
component_h.write_text(component_text, encoding="utf-8")

button_text = button_h.read_text(encoding="utf-8")
button_anchor = "\tvirtual ~Button() = default;\n"
button_patch = "\tvirtual ~Button() = default;\n\tbool IsButton() const override { return true; }\n"
if "bool IsButton() const override" not in button_text:
    if button_anchor not in button_text:
        raise SystemExit("Button.h IsButton anchor missing")
    button_text = button_text.replace(button_anchor, button_patch, 1)
button_h.write_text(button_text, encoding="utf-8")


# Yandex mobile: make small buttons easier to tap without changing desktop geometry.
window_text = window_cpp.read_text(encoding="utf-8")
mouse_down_anchor = r'''void Window::DoMouseDown(int x_, int y_, unsigned button)
{
	//on mouse click
	int x = x_ - Position.X;
	int y = y_ - Position.Y;
	bool clickState = false;
	for (int i = Components.size() - 1; i > -1 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
		{
			if (x >= Components[i]->Position.X && y >= Components[i]->Position.Y && x < Components[i]->Position.X + Components[i]->Size.X && y < Components[i]->Position.Y + Components[i]->Size.Y)
			{
				FocusComponent(Components[i]);
				if (!DEBUG || !debugMode)
				{
					Components[i]->MouseDownInside = true;
				}
				clickState = true;
				break;
			}
		}
	}

	if (!clickState)
		FocusComponent(nullptr);

	if (debugMode)
		return;

	//on mouse down
	for (int i = Components.size() - 1; i > -1 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
			Components[i]->OnMouseDown(x, y, button);
	}

	if (!stop)
		OnMouseDown(x_, y_, button);

	if (!clickState && (x_ < Position.X || y_ < Position.Y || x_ > Position.X+Size.X || y_ > Position.Y+Size.Y))
		OnTryExit(MouseOutside);

	if (destruct)
		finalise();
}'''

mouse_down_patch = r'''void Window::DoMouseDown(int x_, int y_, unsigned button)
{
	//on mouse click
	int x = x_ - Position.X;
	int y = y_ - Position.Y;
	bool clickState = false;
	int selectedIndex = -1;

	// Preserve exact desktop-style hit testing first.
	for (int i = Components.size() - 1; i > -1 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
		{
			if (x >= Components[i]->Position.X && y >= Components[i]->Position.Y && x < Components[i]->Position.X + Components[i]->Size.X && y < Components[i]->Position.Y + Components[i]->Size.Y)
			{
				selectedIndex = i;
				break;
			}
		}
	}

	// Touch screens get a forgiving halo around buttons only. If multiple
	// halos overlap, choose the nearest button centre.
	if (selectedIndex < 0 && Engine::Ref().TouchUI)
	{
		constexpr int touchMarginX = 10;
		constexpr int touchMarginY = 10;
		int bestDistance = 0x7FFFFFFF;
		for (int i = Components.size() - 1; i > -1 && !halt; --i)
		{
			auto *component = Components[i];
			if (!component->Enabled || !component->Visible || !component->IsButton())
				continue;

			if (x >= component->Position.X - touchMarginX &&
			    y >= component->Position.Y - touchMarginY &&
			    x < component->Position.X + component->Size.X + touchMarginX &&
			    y < component->Position.Y + component->Size.Y + touchMarginY)
			{
				int centreX = component->Position.X + component->Size.X / 2;
				int centreY = component->Position.Y + component->Size.Y / 2;
				int dx = x - centreX;
				int dy = y - centreY;
				int distance = dx * dx + dy * dy;
				if (distance < bestDistance)
				{
					bestDistance = distance;
					selectedIndex = i;
				}
			}
		}
	}

	if (selectedIndex >= 0)
	{
		FocusComponent(Components[selectedIndex]);
		if (!DEBUG || !debugMode)
			Components[selectedIndex]->MouseDownInside = true;
		clickState = true;
	}
	else
	{
		FocusComponent(nullptr);
	}

	if (debugMode)
		return;

	//on mouse down
	for (int i = Components.size() - 1; i > -1 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
			Components[i]->OnMouseDown(x, y, button);
	}

	if (!stop)
		OnMouseDown(x_, y_, button);

	if (!clickState && (x_ < Position.X || y_ < Position.Y || x_ > Position.X+Size.X || y_ > Position.Y+Size.Y))
		OnTryExit(MouseOutside);

	if (destruct)
		finalise();
}'''

if mouse_down_anchor not in window_text:
    raise SystemExit("Window.cpp DoMouseDown anchor missing")
window_text = window_text.replace(mouse_down_anchor, mouse_down_patch, 1)

mouse_up_anchor = r'''void Window::DoMouseUp(int x_, int y_, unsigned button)
{
	int x = x_ - Position.X;
	int y = y_ - Position.Y;
	if (debugMode)
		return;
	//on mouse unclick
	for (int i = Components.size() - 1; i >= 0  && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
		{
			if (Components[i]->MouseDownInside && x >= Components[i]->Position.X && y >= Components[i]->Position.Y && x < Components[i]->Position.X + Components[i]->Size.X && y < Components[i]->Position.Y + Components[i]->Size.Y)
			{
				Components[i]->OnMouseClick(x - Components[i]->Position.X, y - Components[i]->Position.Y, button);
				break;
			}
		}
	}
	for (auto *component : Components)
	{
		component->MouseDownInside = false;
	}

	//on mouse up
	for (int i = Components.size() - 1; i >= 0 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
			Components[i]->OnMouseUp(x, y, button);
	}

	if (!stop)
		OnMouseUp(x_, y_, button);
	if (destruct)
		finalise();
}'''

mouse_up_patch = r'''void Window::DoMouseUp(int x_, int y_, unsigned button)
{
	int x = x_ - Position.X;
	int y = y_ - Position.Y;
	if (debugMode)
		return;
	//on mouse unclick
	for (int i = Components.size() - 1; i >= 0  && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible && Components[i]->MouseDownInside)
		{
			auto *component = Components[i];
			bool inside =
				x >= component->Position.X &&
				y >= component->Position.Y &&
				x < component->Position.X + component->Size.X &&
				y < component->Position.Y + component->Size.Y;

			if (!inside && Engine::Ref().TouchUI && component->IsButton())
			{
				constexpr int touchMarginX = 10;
				constexpr int touchMarginY = 10;
				inside =
					x >= component->Position.X - touchMarginX &&
					y >= component->Position.Y - touchMarginY &&
					x < component->Position.X + component->Size.X + touchMarginX &&
					y < component->Position.Y + component->Size.Y + touchMarginY;
			}

			if (inside)
			{
				component->OnMouseClick(
					x - component->Position.X,
					y - component->Position.Y,
					button
				);
				break;
			}
		}
	}
	for (auto *component : Components)
	{
		component->MouseDownInside = false;
	}

	//on mouse up
	for (int i = Components.size() - 1; i >= 0 && !halt; --i)
	{
		if (Components[i]->Enabled && Components[i]->Visible)
			Components[i]->OnMouseUp(x, y, button);
	}

	if (!stop)
		OnMouseUp(x_, y_, button);
	if (destruct)
		finalise();
}'''

if mouse_up_anchor not in window_text:
    raise SystemExit("Window.cpp DoMouseUp anchor missing")
window_text = window_text.replace(mouse_up_anchor, mouse_up_patch, 1)
window_cpp.write_text(window_text, encoding="utf-8")


# Yandex single-thread Emscripten fallback.
# The Yandex ZIP must not require SharedArrayBuffer or cross-origin isolation.

task_text = task_cpp.read_text(encoding="utf-8")
task_anchor = """void Task::Start()
{
	before();
	std::thread([this]() { doWork_wrapper(); }).detach();
}"""
task_patch = """void Task::Start()
{
	before();
#if defined(__EMSCRIPTEN__)
	// Run browser tasks synchronously in the pthread-free Yandex build.
	doWork_wrapper();
#else
	std::thread([this]() { doWork_wrapper(); }).detach();
#endif
}"""
if "Run browser tasks synchronously" not in task_text:
    if task_anchor not in task_text:
        raise SystemExit("Task.cpp Start anchor not found")
    task_text = task_text.replace(task_anchor, task_patch, 1)
task_cpp.write_text(task_text, encoding="utf-8")

gravity_text = gravity_cpp.read_text(encoding="utf-8")
gravity_dispatch_anchor = """void GravityImpl::Dispatch()
{
	{
		std::unique_lock lk(stateMx);
		working = true;
	}
	stateCv.notify_one();
}"""
gravity_dispatch_patch = """void GravityImpl::Dispatch()
{
#if defined(__EMSCRIPTEN__)
	Work();
#else
	{
		std::unique_lock lk(stateMx);
		working = true;
	}
	stateCv.notify_one();
#endif
}"""
if gravity_dispatch_anchor in gravity_text:
    gravity_text = gravity_text.replace(gravity_dispatch_anchor, gravity_dispatch_patch, 1)

gravity_stop_anchor = """void GravityImpl::Stop()
{
	{
		std::unique_lock lk(stateMx);
		shouldStop = true;
	}
	stateCv.notify_one();
	thr.join();
}"""
gravity_stop_patch = """void GravityImpl::Stop()
{
#if !defined(__EMSCRIPTEN__)
	{
		std::unique_lock lk(stateMx);
		shouldStop = true;
	}
	stateCv.notify_one();
	thr.join();
#endif
}"""
if gravity_stop_anchor in gravity_text:
    gravity_text = gravity_text.replace(gravity_stop_anchor, gravity_stop_patch, 1)

gravity_wait_anchor = """void GravityImpl::Wait()
{
	std::unique_lock lk(stateMx);
	stateCv.wait(lk, [this]() {
		return !working;
	});
}"""
gravity_wait_patch = """void GravityImpl::Wait()
{
#if !defined(__EMSCRIPTEN__)
	std::unique_lock lk(stateMx);
	stateCv.wait(lk, [this]() {
		return !working;
	});
#endif
}"""
if gravity_wait_anchor in gravity_text:
    gravity_text = gravity_text.replace(gravity_wait_anchor, gravity_wait_patch, 1)

thread_start_anchor = """	thr = std::thread([this]() {
		while (true)
		{
			{
				std::unique_lock lk(stateMx);
				stateCv.wait(lk, [this]() {
					return working || shouldStop;
				});
				if (shouldStop)
				{
					break;
				}
			}
			Work();
			{
				std::unique_lock lk(stateMx);
				working = false;
			}
			stateCv.notify_one();
		}
	});"""
thread_start_patch = """#if !defined(__EMSCRIPTEN__)
""" + thread_start_anchor + """
#endif"""
if "#if !defined(__EMSCRIPTEN__)\n\tthr = std::thread" not in gravity_text:
    if thread_start_anchor not in gravity_text:
        raise SystemExit("Fft.cpp worker thread anchor not found")
    gravity_text = gravity_text.replace(thread_start_anchor, thread_start_patch, 1)

# Newtonian gravity is optional and many ordinary simulations contain no
# Newtonian mass sources. Avoid the expensive FFTW planner entirely until the
# first effective non-zero mass appears in the browser build.
gravity_exchange_anchor = """	// lazy init
	if (!fftGravity->initDone)
	{
		// this takes a noticeable amount of time
		// TODO: hide the wait somehow
		fftGravity->Init();
		fftGravity->initDone = true;
	}"""
gravity_exchange_patch = """	// lazy init
#if defined(__EMSCRIPTEN__)
	if (!fftGravity->initDone)
	{
		bool yandexWebHasEffectiveMass = false;
		for (auto p : gravIn.mass.Size().OriginRect())
		{
			if (gravIn.mask[p] && gravIn.mass[p] != 0.0f)
			{
				yandexWebHasEffectiveMass = true;
				break;
			}
		}
		if (!yandexWebHasEffectiveMass)
		{
			// No initialized worker/output exists yet, so the exact gravity
			// result is already the default zero field. Remember the input
			// only so a later non-zero source is detected normally.
			fftGravity->gravIn.mass = gravIn.mass;
			fftGravity->gravIn.mask = gravIn.mask;
			return;
		}
	}
#endif
	if (!fftGravity->initDone)
	{
		// this takes a noticeable amount of time
		// TODO: hide the wait somehow
		fftGravity->Init();
		fftGravity->initDone = true;
	}"""
if gravity_exchange_anchor not in gravity_text:
    raise SystemExit("Fft.cpp lazy-init gravity anchor missing")
gravity_text = gravity_text.replace(
    gravity_exchange_anchor, gravity_exchange_patch, 1
)

# Once FFTW is initialized, keep the original one-frame exchange pipeline but
# skip the transforms when the masked mass plane is exactly zero.
gravity_work_anchor = """void GravityImpl::Work()
{
	{
		auto massBigP = MakePlane<blocks.X, blocks.Y>(blocks, massBig.get());
		for (auto p : CELLS.OriginRect())
		{
			// used to be a membwand but we'd need a new buffer for this,
			// not worth it just to make this unalinged copy faster
			massBigP[p + CELLS] = gravIn.mask[p] ? gravIn.mass[p] : 0.f;
		}
	}
	fftwf_execute(massForward.get());"""
gravity_work_patch = """void GravityImpl::Work()
{
	bool yandexWebHasEffectiveMass = false;
	{
		auto massBigP = MakePlane<blocks.X, blocks.Y>(blocks, massBig.get());
		for (auto p : CELLS.OriginRect())
		{
			// used to be a membwand but we'd need a new buffer for this,
			// not worth it just to make this unalinged copy faster
			auto value = gravIn.mask[p] ? gravIn.mass[p] : 0.f;
			massBigP[p + CELLS] = value;
			yandexWebHasEffectiveMass |= value != 0.0f;
		}
	}
#if defined(__EMSCRIPTEN__)
	if (!yandexWebHasEffectiveMass)
	{
		for (auto p : CELLS.OriginRect())
		{
			gravOut.forceX[p] = 0.0f;
			gravOut.forceY[p] = 0.0f;
		}
		return;
	}
#else
	(void)yandexWebHasEffectiveMass;
#endif
	fftwf_execute(massForward.get());"""
if gravity_work_anchor not in gravity_text:
    raise SystemExit("Fft.cpp zero-mass FFT anchor missing")
gravity_text = gravity_text.replace(gravity_work_anchor, gravity_work_patch, 1)

gravity_cpp.write_text(gravity_text, encoding="utf-8")

controller_text = game_controller_cpp.read_text(encoding="utf-8")

# Reset Air / Reset Spark are user-triggered maintenance operations. Particle
# slots at and beyond parts.active are guaranteed free, so avoid walking the
# full NPART capacity on Web builds.
reset_air_anchor = """void GameController::ResetAir()
{
	Simulation * sim = gameModel->GetSimulation();
	sim->air->Clear();
	for (int i = 0; i < NPART; i++)"""
reset_air_patch = """void GameController::ResetAir()
{
	Simulation * sim = gameModel->GetSimulation();
	sim->air->Clear();
	for (int i = 0; i < sim->parts.active; i++)"""
if reset_air_anchor not in controller_text:
    raise SystemExit("GameController::ResetAir active-range anchor missing")
controller_text = controller_text.replace(
    reset_air_anchor, reset_air_patch, 1
)

reset_spark_anchor = """void GameController::ResetSpark()
{
	auto &sd = SimulationData::CRef();
	Simulation * sim = gameModel->GetSimulation();
	for (int i = 0; i < NPART; i++)"""
reset_spark_patch = """void GameController::ResetSpark()
{
	auto &sd = SimulationData::CRef();
	Simulation * sim = gameModel->GetSimulation();
	for (int i = 0; i < sim->parts.active; i++)"""
if reset_spark_anchor not in controller_text:
    raise SystemExit("GameController::ResetSpark active-range anchor missing")
controller_text = controller_text.replace(
    reset_spark_anchor, reset_spark_patch, 1
)

controller_anchor = """bool GameController::ThreadedRenderingAllowed()
{
	return gameModel->GetThreadedRendering() && !GetPaused() && !commandInterface->HaveSimGraphicsEventHandlers();
}"""
controller_patch = """bool GameController::ThreadedRenderingAllowed()
{
#if defined(__EMSCRIPTEN__)
	return false;
#else
	return gameModel->GetThreadedRendering() && !GetPaused() && !commandInterface->HaveSimGraphicsEventHandlers();
#endif
}"""
if controller_anchor in controller_text:
    controller_text = controller_text.replace(controller_anchor, controller_patch, 1)
game_controller_cpp.write_text(controller_text, encoding="utf-8")

view_text = game_view.read_text(encoding="utf-8")
start_anchor = """void GameView::StartRendererThread()
{
	bool start = false;"""
start_patch = """void GameView::StartRendererThread()
{
#if defined(__EMSCRIPTEN__)
	return;
#else
	bool start = false;"""
if "#if defined(__EMSCRIPTEN__)\n\treturn;\n#else\n\tbool start" not in view_text:
    if start_anchor not in view_text:
        raise SystemExit("GameView.cpp StartRendererThread anchor not found")
    view_text = view_text.replace(start_anchor, start_patch, 1)
    end_anchor = """	if (notify)
	{
		DispatchRendererThread();
	}
}

void GameView::StopRendererThread()"""
    end_patch = """	if (notify)
	{
		DispatchRendererThread();
	}
#endif
}

void GameView::StopRendererThread()"""
    if end_anchor not in view_text:
        raise SystemExit("GameView.cpp StartRendererThread end anchor not found")
    view_text = view_text.replace(end_anchor, end_patch, 1)

for func, next_func in [
    ("StopRendererThread", "void GameView::PauseRendererThread()"),
    ("PauseRendererThread", "void GameView::DispatchRendererThread()"),
    ("WaitForRendererThread", "void GameView::ApplySimFpsLimit()"),
]:
    signature = f"void GameView::{func}()\n{{"
    guarded = signature + "\n#if defined(__EMSCRIPTEN__)"
    if signature in view_text and guarded not in view_text:
        view_text = view_text.replace(
            signature,
            signature + "\n#if defined(__EMSCRIPTEN__)\n\treturn;\n#else",
            1,
        )
        idx = view_text.find(signature)
        next_idx = view_text.find(next_func, idx)
        if next_idx < 0:
            raise SystemExit(f"GameView.cpp next function for {func} not found")
        segment = view_text[idx:next_idx]
        close = segment.rfind("}\n\n")
        if close < 0:
            raise SystemExit(f"GameView.cpp end for {func} not found")
        segment = segment[:close] + "#endif\n" + segment[close:]
        view_text = view_text[:idx] + segment + view_text[next_idx:]

game_view.write_text(view_text, encoding="utf-8")
