"""Keep RIP's Severian display name on EU4's stable Ryazanian culture keys."""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import ROOT, named_block, normalized


CULTURES = ROOT / "common/cultures/00_cultures.txt"
LOADED_DIRS = ("common", "customizable_localization", "decisions", "events", "history", "missions")
LEGACY_ASSIGNMENT = re.compile(
    rb"\b(?:culture|primary_culture|change_culture|add_accepted_culture|"
    rb"remove_accepted_culture|accepted_culture|ruler_culture|heir_culture|"
    rb"consort_culture|set_ruler_culture|set_heir_culture|set_consort_culture)"
    rb"\s*=\s*severian(?:_new)?\b"
)


def main() -> int:
    failures: list[str] = []
    # This inherited full-file override contains legacy single-byte name data;
    # Latin-1 gives a lossless one-codepoint view for its ASCII Clausewitz keys.
    cultures = CULTURES.read_bytes().decode("latin-1")

    for key in ("ryazanian", "ryazanian_new", "severian", "severian_new"):
        count = len(re.findall(rf"(?m)^\s*{key}\s*=\s*\{{", cultures))
        if count != 1:
            failures.append(f"common/cultures/00_cultures.txt: expected one {key} block, found {count}")

    if "primary = RYA" not in normalized(named_block(cultures, "ryazanian")):
        failures.append("ryazanian must remain RYA's primary culture")

    for legacy in ("severian", "severian_new"):
        if normalized(named_block(cultures, legacy)) != f"{legacy} = {{ }}":
            failures.append(f"{legacy} must remain an empty save-compatibility alias")

    for directory in LOADED_DIRS:
        for path in sorted((ROOT / directory).rglob("*.txt")):
            if path == CULTURES:
                continue
            if LEGACY_ASSIGNMENT.search(path.read_bytes()):
                failures.append(f"{path.relative_to(ROOT)}: live script still writes/tests a legacy Severian key")

    if failures:
        print("Culture-key compatibility failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Severian uses vanilla ryazanian keys; legacy aliases are save-only")
    return 0


if __name__ == "__main__":
    sys.exit(main())
