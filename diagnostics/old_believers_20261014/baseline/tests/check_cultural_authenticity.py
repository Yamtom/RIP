"""Regressions for period-oriented name pools and the provenance of cultural maps."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import re

from clausewitz_testlib import ROOT, named_block

BASES = ("ruthenian", "byelorussian", "ryazanian", "rusyn")
ALIASES = {
    "ruthenian_new": "ruthenian", "byelorussian_new": "byelorussian",
    "ryazanian_new": "ryazanian", "rusyn_new": "rusyn", "rusyn_new_new": "rusyn",
}
ROWS = re.compile(r'^\s*(\d+)\s*=\s*"([^"]+)"', re.M)


def name_pool(text, culture, field):
    block = named_block(named_block(text, culture), field)
    body = re.sub(r"#[^\r\n]*", "", block.split("{", 1)[1].rsplit("}", 1)[0])
    return re.findall(r'"[^"]+"|[^\s]+', body)


def main():
    failures = []
    text = (ROOT / "common/cultures/00_cultures.txt").read_bytes().decode("latin-1")
    for banned in ("Woland", "Koroviev"):
        if re.search(r"\b" + banned + r"\b", text):
            failures.append(f"fictional fallback surname reintroduced: {banned}")
    for culture in (*BASES, *ALIASES):
        for field, minimum in (("male_names", 20), ("female_names", 12), ("dynasty_names", 12)):
            values = name_pool(text, culture, field)
            if len(values) < minimum:
                failures.append(f"{culture}/{field}: missing explicit period pool; group fallback would leak in")
            if any(not value.isascii() for value in values):
                failures.append(f"{culture}/{field}: ambiguous single-byte transcription")
            if len(values) != len(set(values)):
                failures.append(f"{culture}/{field}: accidental duplicate changes draw weight")
            for banned in ("Scythia", '"of Gothia"', "Svetlana", "Svitlana"):
                if banned in values:
                    failures.append(f"{culture}/{field}: rejected fantasy or late-fashion entry {banned}")
    for alias, base in ALIASES.items():
        for field in ("male_names", "female_names", "dynasty_names"):
            if name_pool(text, alias, field) != name_pool(text, base, field):
                failures.append(f"{alias}/{field}: culture transition loses the {base} naming register")
    for culture, tag in {
        "ruthenian": "KIE", "byelorussian": "PLT", "ryazanian": "RYA",
        "rusyn": "UZH", "rusyn_new": "UZH", "rusyn_new_new": "UZH",
    }.items():
        if f"primary = {tag}" not in named_block(text, culture):
            failures.append(f"{culture}: lost inherited primary tag {tag}")

    maps = {}
    for culture in (*BASES, *ALIASES):
        p = ROOT / "common/province_names" / (culture + ".txt")
        if not p.is_file():
            failures.append(f"missing live province-name filename {p.name}")
            continue
        maps[culture] = {int(pid): value for pid, value in ROWS.findall(p.read_text(encoding="ascii"))}
    for alias, base in ALIASES.items():
        if maps.get(alias) != maps.get(base):
            failures.append(f"{alias}: province names diverge across culture transition")
    if (ROOT / "common/province_names/CHR.txt").exists():
        failures.append("general Severian names belong in ryazanian.txt, not a CHR-only duplicate")
    for pid in (289, 1945, 4543, 298, 301, 4255):
        if pid not in maps.get("ryazanian", {}):
            failures.append(f"Severian culture cannot name its princely core province {pid}")

    provenance = json.loads((ROOT / "tests/data/cultural_names_provenance.json").read_text(encoding="utf-8"))
    keys = []
    for entry in provenance["entries"]:
        culture, pid, value = entry["culture"], entry["pid"], entry["name"]
        keys.append((culture, pid))
        if maps.get(culture, {}).get(pid) != value:
            failures.append(f"stale provenance at {culture}/{pid}: {value}")
        if entry["classification"] not in {"adapted", "speculative"}:
            failures.append(f"unsupported historical claim in provenance at {culture}/{pid}")
        line = next((line for line in (ROOT / f"common/province_names/{culture}.txt").read_text(encoding="ascii").splitlines()
                     if re.match(rf"\s*{pid}\s*=", line)), "")
        marker = "SPECULATIVE:" if entry["classification"] == "speculative" else "ADAPTED:"
        if marker not in line:
            failures.append(f"{culture}/{pid}: lost in-file distinction between evidence and design")
    if any(count != 1 for count in Counter(keys).values()):
        failures.append("duplicate provenance keys")

    # An archived donor checks attribution only. It cannot certify the target map.
    donor = ROOT / provenance["donor_snapshot"] / "common/province_names"
    if donor.is_dir():
        donor_ids = {}
        for name, metadata in provenance["donor_files"].items():
            p = donor / (name + ".txt")
            if p.exists() != metadata["present"]:
                failures.append(f"donor presence changed for {name}")
            if not metadata["present"] or not p.is_file():
                continue
            if hashlib.sha256(p.read_bytes()).hexdigest() != metadata["sha256"]:
                failures.append(f"archived donor {name} hash changed")
            donor_ids[name] = {int(pid) for pid in re.findall(r"(?m)^\s*(\d+)\s*=", p.read_bytes().decode("cp1252"))}
        for entry in provenance["entries"]:
            if entry["donor"] in donor_ids and entry["pid"] not in donor_ids[entry["donor"]]:
                failures.append(f"donor anchor absent: {entry['donor']}/{entry['pid']}")
    else:
        print("SKIP: archived 1.30.3 donor attribution cannot be refreshed on this checkout")
    if failures:
        print("CULTURAL AUTHENTICITY CONTRACT FAILURES:")
        for failure in failures:
            print("  " + failure)
        return 1
    print(f"CULTURAL AUTHENTICITY CHECK: PASS (9 explicit pools, 9 map layers, {len(keys)} provenance records; source contracts only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

