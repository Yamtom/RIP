"""Check encoding and balanced braces in every engine-loaded text file."""

from __future__ import annotations

import sys

from clausewitz_testlib import ROOT, brace_error


LOADED_DIRS = (
    "common",
    "customizable_localization",
    "decisions",
    "events",
    "history",
    "map",
    "missions",
)
# Interface files are parsed by the same reader: a BOM in a .gfx/.gui is logged
# as "Unexpected token" and, for a replaced vanilla window, ends in a startup crash.
INTERFACE_SUFFIXES = ("*.gfx", "*.gui")


def main() -> int:
    failures: list[str] = []
    for directory in LOADED_DIRS:
        for path in sorted((ROOT / directory).rglob("*.txt")):
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                failures.append(
                    f"{path.relative_to(ROOT)}: UTF-8 BOM is not valid in Clausewitz data files"
                )
                continue
            error = brace_error(raw.decode(encoding="utf-8", errors="replace"))
            if error:
                failures.append(f"{path.relative_to(ROOT)}: {error}")

    for suffix in INTERFACE_SUFFIXES:
        for path in sorted((ROOT / "interface").rglob(suffix)):
            raw = path.read_bytes()
            if raw.startswith(b"\xef\xbb\xbf"):
                failures.append(f"{path.relative_to(ROOT)}: UTF-8 BOM breaks the interface parser")
                continue
            error = brace_error(raw.decode(encoding="utf-8", errors="replace"))
            if error:
                failures.append(f"{path.relative_to(ROOT)}: {error}")

    # A localisation value is one physical line; a raw newline splits the key.
    import re
    for path in sorted((ROOT / "localisation").rglob("*.yml")):
        for number, line in enumerate(path.read_text(encoding="utf-8-sig").split("\n"), 1):
            if (line.strip() and not line.lstrip().startswith("#")
                    and not re.match(r'^\s*[A-Za-z0-9_.\-]+:\d*\s+"', line)
                    and not re.match(r'^l_\w+:\s*$', line)):
                failures.append(f"{path.relative_to(ROOT)}:{number}: localisation line is not a key (split value?)")

    if failures:
        print("Clausewitz brace failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Clausewitz data files are BOM-free and braces are balanced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
