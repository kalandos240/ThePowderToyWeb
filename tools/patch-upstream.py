#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
powder = root / "upstream" / "src" / "PowderToy.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"
game_view = root / "upstream" / "src" / "gui" / "game" / "GameView.cpp"
local_browser = root / "upstream" / "src" / "gui" / "localbrowser" / "LocalBrowserView.cpp"
local_save = root / "upstream" / "src" / "gui" / "save" / "LocalSaveActivity.cpp"
options_view = root / "upstream" / "src" / "gui" / "options" / "OptionsView.cpp"
locale_header = root / "upstream" / "src" / "YandexWebLocale.h"

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
