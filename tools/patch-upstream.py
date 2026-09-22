#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
meson = root / "upstream" / "meson.build"
powder = root / "upstream" / "src" / "PowderToy.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"
game_view = root / "upstream" / "src" / "gui" / "game" / "GameView.cpp"
local_browser = root / "upstream" / "src" / "gui" / "localbrowser" / "LocalBrowserView.cpp"
local_save = root / "upstream" / "src" / "gui" / "save" / "LocalSaveActivity.cpp"
options_view = root / "upstream" / "src" / "gui" / "options" / "OptionsView.cpp"
locale_header = root / "upstream" / "src" / "YandexWebLocale.h"
task_cpp = root / "upstream" / "src" / "tasks" / "Task.cpp"
gravity_cpp = root / "upstream" / "src" / "simulation" / "gravity" / "Fft.cpp"
game_controller_cpp = root / "upstream" / "src" / "gui" / "game" / "GameController.cpp"
render_view = root / "upstream" / "src" / "gui" / "render" / "RenderView.cpp"
element_search = root / "upstream" / "src" / "gui" / "elementsearch" / "ElementSearchActivity.cpp"
colour_picker = root / "upstream" / "src" / "gui" / "colourpicker" / "ColourPickerActivity.cpp"
confirm_prompt = root / "upstream" / "src" / "gui" / "dialogues" / "ConfirmPrompt.cpp"
error_message = root / "upstream" / "src" / "gui" / "dialogues" / "ErrorMessage.cpp"
information_message = root / "upstream" / "src" / "gui" / "dialogues" / "InformationMessage.cpp"

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
include_locale(render_view, '#include "gui/game/GameView.h"\n')
include_locale(element_search, '#include "gui/game/ToolButton.h"\n')
include_locale(colour_picker, '#include "Misc.h"\n')
include_locale(confirm_prompt, '#include "graphics/Graphics.h"\n')
include_locale(error_message, '#include "graphics/Graphics.h"\n')
include_locale(information_message, '#include "graphics/Graphics.h"\n')

game_view_text = game_view.read_text(encoding="utf-8")
game_replacements = [
    ('searchButton->SetToolTip("Open a local simulation.");',
     'searchButton->SetToolTip(YandexWebText("Open a local simulation.", "Открыть локальную симуляцию."));'),
    ('"", "Reload the simulation")',
     '"", YandexWebText("Reload the simulation", "Перезагрузить симуляцию"))'),
    ('"[untitled simulation]", "", "", 19)',
     'YandexWebText("[untitled simulation]", "[без названия]"), "", "", 19)'),
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
]
for old, new in game_replacements:
    if old in game_view_text:
        game_view_text = game_view_text.replace(old, new)
game_view.write_text(game_view_text, encoding="utf-8")

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
options_view.write_text(options_text, encoding="utf-8")


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


# Additional RU/EN user-facing windows.
search_text = element_search.read_text(encoding="utf-8")
for old, new in [
    ('"Element Search"', 'YandexWebText("Element Search", "Поиск элементов")'),
    ('"Close"', 'YandexWebText("Close", "Закрыть")'),
]:
    if old in search_text:
        search_text = search_text.replace(old, new)
element_search.write_text(search_text, encoding="utf-8")

picker_text = colour_picker.read_text(encoding="utf-8")
picker_text = picker_text.replace(
    '"Done"',
    'YandexWebText("Done", "Готово")'
)
colour_picker.write_text(picker_text, encoding="utf-8")

confirm_text = confirm_prompt.read_text(encoding="utf-8")
confirm_text = confirm_text.replace(
    '"Cancel"',
    'YandexWebText("Cancel", "Отмена")'
)
confirm_prompt.write_text(confirm_text, encoding="utf-8")

error_text = error_message.read_text(encoding="utf-8")
error_text = error_text.replace(
    '"Dismiss"',
    'YandexWebText("Dismiss", "Закрыть")'
)
error_message.write_text(error_text, encoding="utf-8")

info_text = information_message.read_text(encoding="utf-8")
info_text = info_text.replace(
    '"Dismiss"',
    'YandexWebText("Dismiss", "Закрыть")'
)
information_message.write_text(info_text, encoding="utf-8")

render_text = render_view.read_text(encoding="utf-8")
render_replacements = [
    ('"Velocity display mode preset"', 'YandexWebText("Velocity display mode preset", "Режим отображения скорости")'),
    ('"Pressure display mode preset"', 'YandexWebText("Pressure display mode preset", "Режим отображения давления")'),
    ('"Persistent display mode preset"', 'YandexWebText("Persistent display mode preset", "Режим следов")'),
    ('"Fire display mode preset"', 'YandexWebText("Fire display mode preset", "Режим огня")'),
    ('"Blob display mode preset"', 'YandexWebText("Blob display mode preset", "Режим капель")'),
    ('"Heat display mode preset"', 'YandexWebText("Heat display mode preset", "Режим температуры")'),
    ('"Fancy display mode preset"', 'YandexWebText("Fancy display mode preset", "Расширенный режим")'),
    ('"Nothing display mode preset"', 'YandexWebText("Nothing display mode preset", "Базовый режим")'),
    ('"Heat gradient display mode preset"', 'YandexWebText("Heat gradient display mode preset", "Градиент температуры")'),
    ('"Alternative Velocity display mode preset"', 'YandexWebText("Alternative Velocity display mode preset", "Альтернативная скорость")'),
    ('"Life display mode preset"', 'YandexWebText("Life display mode preset", "Режим времени жизни")'),
    ('"Adds Special flare effects to some elements"', 'YandexWebText("Adds Special flare effects to some elements", "Добавляет специальные эффекты некоторым элементам")'),
    ('"Fire effect for gasses"', 'YandexWebText("Fire effect for gasses", "Эффект огня для газов")'),
    ('"Glow effect on some elements"', 'YandexWebText("Glow effect on some elements", "Свечение некоторых элементов")'),
    ('"Blur effect for liquids"', 'YandexWebText("Blur effect for liquids", "Размытие жидкостей")'),
    ('"Makes everything be drawn like a blob"', 'YandexWebText("Makes everything be drawn like a blob", "Отображает всё как капли")'),
    ('"Basic rendering, without this, most things will be invisible"', 'YandexWebText("Basic rendering, without this, most things will be invisible", "Базовый рендеринг; без него большинство объектов невидимо")'),
    ('"Glow effect on sparks"', 'YandexWebText("Glow effect on sparks", "Свечение искр")'),
    ('"Displays pressure as red and blue, and velocity as white"', 'YandexWebText("Displays pressure as red and blue, and velocity as white", "Давление красным/синим, скорость белым")'),
    ('"Displays pressure, red is positive and blue is negative"', 'YandexWebText("Displays pressure, red is positive and blue is negative", "Давление: красный — положительное, синий — отрицательное")'),
    ('"Displays the temperature of the air like heat display does"', 'YandexWebText("Displays the temperature of the air like heat display does", "Показывает температуру воздуха")'),
    ('"Displays vorticity, red is clockwise and blue is anticlockwise"', 'YandexWebText("Displays vorticity, red is clockwise and blue is anticlockwise", "Завихрение: красный по часовой, синий против часовой")'),
    ('"Gravity lensing, Newtonian Gravity bends light with this on"', 'YandexWebText("Gravity lensing, Newtonian Gravity bends light with this on", "Гравитационное линзирование света")'),
    ('"Element paths persist on the screen for a while"', 'YandexWebText("Element paths persist on the screen for a while", "Следы элементов некоторое время остаются на экране")'),
    ('"Displays temperatures of the elements, dark blue is coldest, pink is hottest"', 'YandexWebText("Displays temperatures of the elements, dark blue is coldest, pink is hottest", "Температура элементов: синий — холод, розовый — жар")'),
    ('"Displays the life value of elements in greyscale gradients"', 'YandexWebText("Displays the life value of elements in greyscale gradients", "Показывает время жизни элементов оттенками серого")'),
    ('"Changes colors of elements slightly to show heat diffusing through them"', 'YandexWebText("Changes colors of elements slightly to show heat diffusing through them", "Меняет цвета элементов, показывая распространение тепла")'),
    ('"No special effects at all for anything, overrides all other options and deco"', 'YandexWebText("No special effects at all for anything, overrides all other options and deco", "Отключает специальные эффекты и декорации")'),
]
for old, new in render_replacements:
    if old in render_text:
        render_text = render_text.replace(old, new)
render_view.write_text(render_text, encoding="utf-8")
