"""Verify Ryazanian uses vanilla blocks and definitions, and Severian cultural layer is removed."""

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
SEVERIAN_CULTURE_LOC = re.compile(r"(?m)^\s*(?:ryazanian|ryazanian_new|severian|severian_new)\s*:")
RUTHENIAN_CONVERTED_PROVINCES = (
    "history/provinces/1945 - Novgorod-Seversky.txt",
    "history/provinces/291 - Kharkov.txt",
    "history/provinces/297 - Bryansk.txt",
    "history/provinces/298 - Kursk.txt",
    "history/provinces/4116 - Upper Oka.txt",
    "history/provinces/4244 - Starodub.txt",
    "history/provinces/4543 - Rylsk.txt",
)
RYAZANIAN_KEPT_PROVINCES = (
    "history/provinces/300 - Tula.txt",
    "history/provinces/301 - Ryazan.txt",
    "history/provinces/4255 - Pronsk.txt",
    "history/provinces/2408 - Lipetsk.txt",
)


def main() -> int:
    failures: list[str] = []
    cultures = CULTURES.read_bytes().decode("latin-1")

    for key in ("ryazanian", "ryazanian_new"):
        count = len(re.findall(rf"(?m)^\s*{key}\s*=\s*\{{", cultures))
        if count != 1:
            failures.append(f"common/cultures/00_cultures.txt: expected one {key} block, found {count}")

    for legacy in ("severian", "severian_new"):
        count = len(re.findall(rf"(?m)^\s*{legacy}\s*=\s*\{{", cultures))
        if count != 0:
            failures.append(f"common/cultures/00_cultures.txt: legacy key {legacy} must be removed, found {count}")

    rya_block = normalized(named_block(cultures, "ryazanian"))
    if "primary = RYA" not in rya_block:
        failures.append("ryazanian must remain RYA's primary culture")
    if "Pereyaslavl" in rya_block or "Olhovych" in rya_block or "Vasiliy" not in rya_block:
        failures.append("ryazanian culture pool does not match vanilla")

    for directory in LOADED_DIRS:
        for path in sorted((ROOT / directory).rglob("*.txt")):
            if path == CULTURES:
                continue
            if LEGACY_ASSIGNMENT.search(path.read_bytes()):
                failures.append(f"{path.relative_to(ROOT)}: live script references removed Severian culture key")

    for loc_path in sorted((ROOT / "localisation/replace").glob("zzz_RIP_l_*.yml")):
        if SEVERIAN_CULTURE_LOC.search(loc_path.read_text(encoding="utf-8-sig")):
            failures.append(f"{loc_path.relative_to(ROOT)}: overrides vanilla ryazanian/severian culture localisation")

    for removed in ("common/province_names/ryazanian.txt", "common/province_names/ryazanian_new.txt"):
        if (ROOT / removed).exists():
            failures.append(f"{removed}: Severian province-name override must be removed")

    for rel in RUTHENIAN_CONVERTED_PROVINCES:
        txt = (ROOT / rel).read_text(encoding="cp1252")
        if re.search(r"(?m)\bculture\s*=\s*ryazanian\b", txt):
            failures.append(f"{rel}: still contains ryazanian culture")
        if not re.search(r"(?m)^\s*culture\s*=\s*ruthenian\b", txt):
            failures.append(f"{rel}: expected culture = ruthenian")

    for rel in RYAZANIAN_KEPT_PROVINCES:
        txt = (ROOT / rel).read_text(encoding="cp1252")
        if not re.search(r"\bculture\s*=\s*ryazanian\b", txt):
            failures.append(f"{rel}: expected ryazanian culture to remain")

    oka = (ROOT / "history/countries/OKA - Oka.txt").read_text(encoding="cp1252")
    if not re.search(r"(?m)^\s*primary_culture\s*=\s*ruthenian\b", oka):
        failures.append("history/countries/OKA - Oka.txt: expected primary_culture = ruthenian")

    smo = (ROOT / "history/countries/SMO - Smolensk.txt").read_text(encoding="cp1252")
    if not re.search(r"(?m)^\s*primary_culture\s*=\s*byelorussian\b", smo):
        failures.append("history/countries/SMO - Smolensk.txt: expected primary_culture = byelorussian")

    if failures:
        print("Culture-key compatibility failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Vanilla ryazanian culture restored; Severian culture layer removed and Siveria/Oka shifted to ruthenian")
    return 0


if __name__ == "__main__":
    sys.exit(main())
