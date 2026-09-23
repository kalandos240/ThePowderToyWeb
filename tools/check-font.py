#!/usr/bin/env python3
import bz2
from pathlib import Path

root = Path(__file__).resolve().parents[1]
font_path = root / "upstream" / "resources" / "font.bz2"
data = bz2.decompress(font_path.read_bytes())

codepoints = []
ptr = 0
while ptr < len(data):
    if ptr + 4 > len(data):
        raise SystemExit("Corrupt TPT font data")
    codepoint = int.from_bytes(data[ptr:ptr+4], "little") & 0xFFFFFF
    width = data[ptr + 3]
    if codepoint >= 0x110000 or width > 64 or ptr + 4 + width * 3 > len(data):
        raise SystemExit("Corrupt TPT font glyph")
    codepoints.append(codepoint)
    ptr += 4 + width * 3

required_cyrillic = [0x0401, 0x0451, *range(0x0410, 0x0450)]
required_ui_punctuation = [ord(ch) for ch in "-.,:;!?()[]/+%=°«»"]
required = required_cyrillic + required_ui_punctuation
missing = [cp for cp in required if cp not in set(codepoints)]

ranges = []
if codepoints:
    start = prev = codepoints[0]
    for cp in codepoints[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        ranges.append((start, prev))
        start = prev = cp
    ranges.append((start, prev))

print("TPT font glyph count:", len(codepoints))
print("TPT font ranges:", ", ".join(
    f"U+{a:04X}" if a == b else f"U+{a:04X}-U+{b:04X}"
    for a, b in ranges
))
if missing:
    print("Russian glyphs missing:", ", ".join(f"U+{cp:04X}" for cp in missing))
    raise SystemExit(2)

print("Russian Cyrillic coverage: OK")
