#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
powder = root / "upstream" / "src" / "PowderToy.cpp"
sdl_emscripten = root / "upstream" / "src" / "PowderToySDLEmscripten.cpp"
game_view = root / "upstream" / "src" / "gui" / "game" / "GameView.cpp"

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
