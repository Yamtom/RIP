"""Guard the five-column mission layout; rows must start at one.

This checks coordinate bounds, not potential-dependent overlaps or runtime UI.
Comments and quoted strings are ignored, including archived mission trees.
"""
from __future__ import annotations

import re

from clausewitz_testlib import ROOT, _mask_comments_and_strings


def violations(text: str) -> list[tuple[int, str, int]]:
    masked = _mask_comments_and_strings(text)
    failures = []
    for match in re.finditer(r"\b(slot|position)\s*=\s*(-?\d+)\b", masked):
        key, value = match[1], int(match[2])
        if value < 1 or (key == "slot" and value > 5):
            failures.append((masked.count("\n", 0, match.start()) + 1, key, value))
    return failures


def main() -> int:
    # Exercise the regression boundary, including valid rows above five.
    assert not violations('slot = 5\nposition = 8\n# slot = 6\nname = "position = 0"')
    assert [item[2] for item in violations(
        'position = 0\nslot = 6\nslot = 7\nslot = 8\nslot = -1'
    )] == [0, 6, 7, 8, -1]
    files = sorted((ROOT / "missions").rglob("*.txt"))
    if not files:
        raise RuntimeError("No mission files found")
    errors = []
    for path in files:
        for line, key, value in violations(path.read_text(encoding="utf-8-sig")):
            errors.append(f"{path.relative_to(ROOT)}:{line}: {key} = {value}")
    if errors:
        print("MISSION COORDINATES FAIL:\n" + "\n".join(errors))
        return 1
    print(f"MISSION COORDINATES PASS: {len(files)} files; slots 1-5, positions >= 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
