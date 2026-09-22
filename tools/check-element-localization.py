#!/usr/bin/env python3
from collections import Counter
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
