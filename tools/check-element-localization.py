#!/usr/bin/env python3
from collections import Counter
import bz2
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
upstream_elements = root / "upstream" / "src" / "simulation" / "elements"
patch_script = root / "tools" / "patch-upstream.py"

if not upstream_elements.is_dir():
    raise SystemExit("upstream element directory is missing")

expected = {
    path.stem
    for path in upstream_elements.glob("*.cpp")
    if path.stem != "NONE"
}

text = patch_script.read_text(encoding="utf-8")
found = re.findall(r'setRu\("DEFAULT_PT_([A-Z0-9]+)"', text)
counts = Counter(found)
translated = set(found)

missing = sorted(expected - translated)
unknown = sorted(translated - expected)
duplicates = sorted(code for code, count in counts.items() if count != 1)

print(f"Upstream elements: {len(expected)}")
print(f"Russian descriptions: {len(translated)}")

if missing:
    print("Missing translations:", ", ".join(missing))
if unknown:
    print("Unknown translations:", ", ".join(unknown))
if duplicates:
    print("Duplicate translations:", ", ".join(duplicates))

if missing or unknown or duplicates:
    raise SystemExit("Russian element localization coverage check failed")

print("Russian element descriptions cover every upstream element exactly once.")

# Measure authored captions with the exact bitmap font used by TextSize.
# Clipping is only a fallback for user-created names, not a translation strategy.
captions = re.findall(r'YW_TOOL\("([^"]+)", "([^"]+)"\)', text)
caption_counts = Counter(key for key, _ in captions)
assert all(count == 1 for count in caption_counts.values()), "Duplicate button caption"
caption_map = dict(captions)
required = {"DEFAULT_PT_" + code for code in expected | {"NONE"}}
for path in (root / "upstream/src/simulation/simtools").glob("*.cpp"):
    required.update(re.findall(r'Identifier = "([^"]+)"', path.read_text()))
gol_source = (root / "upstream/src/simulation/SimulationData.cpp").read_text()
required.update("DEFAULT_PT_LIFE_" + name for name in
                re.findall(r'\{ "([^"]+)",\s+GT_', gol_source))
model = (root / "upstream/src/gui/game/GameModel.cpp").read_text()
required.update(re.findall(r'"(DEFAULT_DECOR_[A-Z]+)"', model))
for path in (root / "upstream/src/gui/game/tool").glob("*.h"):
    required.update(re.findall(r'"(DEFAULT_UI_[A-Z]+)"', path.read_text()))
assert not required - caption_map.keys(), sorted(required - caption_map.keys())

font = bz2.decompress((root / "upstream/resources/font.bz2").read_bytes())
widths = {}
offset = 0
while offset < len(font):
    char = chr(int.from_bytes(font[offset:offset + 3], "little"))
    width = font[offset + 3]
    widths[char] = width
    offset += 4 + width * 3
for key, caption in captions:
    assert not re.search(r"[A-Za-z]", caption), (key, caption)
    width = sum(widths[char] for char in caption)
    assert 0 < width <= 26, (key, caption, width)
print(f"All {len(captions)} Russian captions fit the 26px content area without clipping.")
