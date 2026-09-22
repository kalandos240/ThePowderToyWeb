#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
meson = root / "upstream" / "meson.build"
powder = root / "upstream" / "src" / "PowderToy.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"
task_cpp = root / "upstream" / "src" / "tasks" / "Task.cpp"
gravity_cpp = root / "upstream" / "src" / "simulation" / "gravity" / "Fft.cpp"
game_controller_cpp = root / "upstream" / "src" / "gui" / "game" / "GameController.cpp"
game_view_cpp = root / "upstream" / "src" / "gui" / "game" / "GameView.cpp"

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


# Yandex single-thread Emscripten fallback. ZIP hosting must not depend on
# SharedArrayBuffer / cross-origin isolation.

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
	// Yandex Web runs without pthreads.
	doWork_wrapper();
#else
	std::thread([this]() { doWork_wrapper(); }).detach();
#endif
}"""
if "Yandex Web runs without pthreads" not in task_text:
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
	// Run FFT gravity synchronously in the pthread-free browser build.
	Work();
#else
	{
		std::unique_lock lk(stateMx);
		working = true;
	}
	stateCv.notify_one();
#endif
}"""
if "Run FFT gravity synchronously" not in gravity_text:
    if gravity_dispatch_anchor not in gravity_text:
        raise SystemExit("Fft.cpp Dispatch anchor not found")
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
gravity_cpp.write_text(gravity_text, encoding="utf-8")

controller_text = game_controller_cpp.read_text(encoding="utf-8")
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
if "#if defined(__EMSCRIPTEN__)\n\treturn false;" not in controller_text:
    if controller_anchor not in controller_text:
        raise SystemExit("GameController.cpp threaded rendering anchor not found")
    controller_text = controller_text.replace(controller_anchor, controller_patch, 1)
game_controller_cpp.write_text(controller_text, encoding="utf-8")

view_text = game_view_cpp.read_text(encoding="utf-8")
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

for func in ["StopRendererThread", "PauseRendererThread", "WaitForRendererThread"]:
    signature = f"void GameView::{func}()\n{{"
    if signature in view_text and f"void GameView::{func}()\n{{\n#if defined(__EMSCRIPTEN__)" not in view_text:
        view_text = view_text.replace(signature, signature + "\n#if defined(__EMSCRIPTEN__)\n\treturn;\n#else", 1)
        # Find matching next function boundary robustly by known function order.
        next_map = {
            "StopRendererThread": "void GameView::PauseRendererThread()",
            "PauseRendererThread": "void GameView::DispatchRendererThread()",
            "WaitForRendererThread": "void GameView::ApplySimFpsLimit()",
        }
        nxt = next_map[func]
        idx = view_text.find(signature)
        next_idx = view_text.find(nxt, idx)
        if next_idx < 0:
            raise SystemExit(f"GameView.cpp next function for {func} not found")
        segment = view_text[idx:next_idx]
        close = segment.rfind("}\n\n")
        if close < 0:
            raise SystemExit(f"GameView.cpp end for {func} not found")
        segment = segment[:close] + "#endif\n" + segment[close:]
        view_text = view_text[:idx] + segment + view_text[next_idx:]

game_view_cpp.write_text(view_text, encoding="utf-8")
