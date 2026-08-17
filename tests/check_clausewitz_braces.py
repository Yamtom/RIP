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

    if failures:
        print("Clausewitz brace failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Clausewitz data files are BOM-free and braces are balanced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
