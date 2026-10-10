"""Keep Turov above vanilla's stale Travancore localisation in every language.

This checks the source replacement contract, not EU4 rendering or old saves.
"""

from __future__ import annotations

import re

from clausewitz_testlib import ROOT, vanilla_root


def main() -> int:
    failures: list[str] = []
    mapping = (ROOT / "common/country_tags/01_countries.txt").read_text(encoding="utf-8")
    if not re.search(r'^TRV\s*=\s*"countries/Turov\.txt"\s*$', mapping, re.M):
        failures.append("TRV must resolve to RIP's Turov country definition")

    for language in ("english", "french", "german", "spanish"):
        paths = sorted((ROOT / "localisation").rglob(f"*_l_{language}.yml"))
        for key in ("TRV", "TRV_ADJ"):
            entries = []
            for path in paths:
                for value in re.findall(
                    rf'^\s*{key}:\d*\s*"([^"\n]*)"\s*$',
                    path.read_text(encoding="utf-8-sig"), re.M,
                ):
                    entries.append((path, value))
            if len(entries) != 1:
                failures.append(f"{language}: expected one {key} override, found {len(entries)}")
            elif entries[0][0].parent.name != "replace" or entries[0][1] != "Turov":
                failures.append(f"{language}: {key} must name Turov in localisation/replace")

    vanilla = vanilla_root()
    if vanilla:
        for path in (vanilla / "common/country_tags").glob("*.txt"):
            if re.search(rb"(?m)^\s*TRV\s*=", path.read_bytes()):
                failures.append(f"live vanilla TRV tag in {path.name}; re-audit tag reuse")
    else:
        print("SKIP: installed vanilla tag collision check (EU4 installation unavailable)")

    if failures:
        print("Turov name failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("Turov name: PASS (TRV replacement name and adjective in all four languages)")
    print("LIMIT: static localisation priority; no EU4 runtime rendering claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
