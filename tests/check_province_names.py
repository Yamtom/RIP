"""Static contract for common/province_names after the split by country.

This directory has been silently wrong twice. Both times the cause was the same
assumption - that consecutive province ids lie next to each other on the map - and
both times it survived because nothing checked it: `check_script_layer.py` audits
only files named for a country tag, so the culture files were never looked at at
all, and `check_glossary.py` reads only `localisation/*.yml`, so the toponyms that
live here were never held to the glossary either.

What this enforces:

  1. Every id exists in vanilla's definition.csv and is a land province in an area.
  2. Every renamed province lies inside a region the mod is actually set in, unless
     the file deliberately reaches further (the Ruthenian culture file does).
  3. Names are plain ASCII. Vanilla stores these files as Windows-1252; a UTF-8
     diacritic here renders as mojibake in game and cannot be seen from the script.
  4. No settlement founded after 1750. The game ends in 1821, most of it is played
     long before, and the file this replaced named nine such places.
  5. No file name collides with one vanilla ships, because a mod file of the same
     name replaces vanilla's outright instead of layering under it.
  6. A tag file does not merely repeat its own culture file. EU4 resolves names per
     province - tag, then culture, then culture group - so a repeated entry is dead
     weight that hides which states actually disagree.

Run from the mod root:  python tests/check_province_names.py
Exit code 1 on any violation, so it can gate a merge.
"""

from __future__ import annotations

import io
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clausewitz_testlib import ROOT  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PN_DIR = ROOT / "common" / "province_names"
EU4_CANDIDATES = [
    os.environ.get("EU4_DIR"),
    r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV",
]
EU4_DIR = next((d for d in EU4_CANDIDATES
                if d and os.path.isdir(os.path.join(d, "common", "province_names"))), None)

ENTRY = re.compile(r'^\s*(\d+)\s*=\s*"([^"]*)"\s*(?:#.*)?$')
ASCII_NAME = re.compile(r"^[A-Za-z0-9 '\-.()/]+$")

# Regions the mod is set in. A tag file that reaches outside one of these is
# almost certainly the consecutive-id mistake again.
MOD_REGIONS = {
    "ruthenia_region", "crimea_region", "poland_region", "carpathia_region",
    "baltic_region", "russia_region", "balkan_region", "caucasia_region",
    "ural_region",
}
# Culture files legitimately name the whole world - vanilla's east_slavic.txt does.
WORLD_FILES = {"ruthenian.txt", "byelorussian.txt", "rusyn.txt"}

# Founded, or first given this name, after 1750.
POST_1750 = {
    "ekaterinoslav", "katerynoslav", "yekaterinoslav", "sevastopol", "sebastopol",
    "nikolaev", "mykolayiv", "nikolayev", "kherson", "odessa", "odesa",
    "novocherkassk", "stavropol", "simferopol", "melitopol", "mariupol",
    "luhansk", "lugansk", "donetsk", "dnipropetrovsk", "zaporizhzhia",
    "yelisavetgrad", "elisavetgrad", "tiraspol", "pavlograd", "berdiansk",
    "feodosia", "feodosiya", "yevpatoriya", "evpatoria", "vladivostok",
    "blagoveshchensk", "novorossiysk", "pyatigorsk", "vladikavkaz",
    "yekaterinodar", "ekaterinodar", "krasnodar", "elista",
}
# Which culture file each tag falls through to, for the redundancy rule.
FALLBACK = {
    "KIE.txt": "ruthenian.txt", "KRU.txt": "ruthenian.txt", "HET.txt": "ruthenian.txt",
    "ZAZ.txt": "ruthenian.txt", "VLN.txt": "ruthenian.txt", "HLC.txt": "ruthenian.txt",
    "PDL.txt": "ruthenian.txt", "KHK.txt": "ruthenian.txt", "PRL.txt": "ruthenian.txt",
    "ODS.txt": "ruthenian.txt", "UZH.txt": "rusyn.txt",
    "MSK.txt": "byelorussian.txt", "VTB.txt": "byelorussian.txt",
    "MSL.txt": "byelorussian.txt", "BLR.txt": "byelorussian.txt",
}


def top_blocks(text: str):
    """Brace-aware. area.txt nests `color = { r g b }`, and the naive
    `([a-z_0-9]+)\\s*=\\s*\\{([^{}]*)\\}` regex swallows the colour instead of the
    area: it loses 182 provinces and mislabels 90. Everything here depends on the
    area being right, so it is parsed properly."""
    i, pattern = 0, re.compile(r"([a-z_0-9]+)\s*=\s*\{")
    while True:
        m = pattern.search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while depth and j < len(text):
            depth += (text[j] == "{") - (text[j] == "}")
            j += 1
        yield m.group(1), text[m.end():j - 1]
        i = j


def load_map(eu4: str):
    defn = {}
    for line in io.open(os.path.join(eu4, "map", "definition.csv"),
                        encoding="cp1252", errors="replace"):
        parts = line.split(";")
        if len(parts) > 4 and parts[0].isdigit():
            defn[int(parts[0])] = parts[4].strip()

    area_of = {}
    atext = re.sub(r"#.*", "", io.open(os.path.join(eu4, "map", "area.txt"),
                                       encoding="cp1252", errors="replace").read())
    for name, body in top_blocks(atext):
        inner = re.sub(r"[a-z_0-9]+\s*=\s*\{[^{}]*\}", "", body)
        for token in inner.split():
            if token.isdigit():
                area_of[int(token)] = name

    region_of = {}
    rtext = re.sub(r"#.*", "", io.open(os.path.join(eu4, "map", "region.txt"),
                                       encoding="cp1252", errors="replace").read())
    for name, body in top_blocks(rtext):
        if name.endswith("_region"):
            for area in re.findall(r"([a-z_0-9]+_area)", body):
                region_of[area] = name
    return defn, area_of, region_of


def parse(path: Path):
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace").replace("\r\n", "\n")
    rows = []
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = ENTRY.match(line)
        if m:
            rows.append((int(m.group(1)), m.group(2), number))
        else:
            rows.append((None, line, number))
    return rows, raw


def audit(eu4: str) -> list[str]:
    defn, area_of, region_of = load_map(eu4)
    vanilla_files = {p.name for p in Path(eu4, "common", "province_names").glob("*.txt")}
    failures: list[str] = []
    parsed: dict[str, dict[int, str]] = {}

    for path in sorted(PN_DIR.glob("*.txt")):
        rel = f"common/province_names/{path.name}"
        if path.name in vanilla_files:
            failures.append(
                f"{rel}: vanilla ships a file with this name, so the mod replaces it "
                f"instead of layering under it - rename, or copy vanilla's entries in")
        rows, raw = parse(path)
        if raw[:3] == b"\xef\xbb\xbf":
            failures.append(f"{rel}: has a UTF-8 BOM")
        seen: dict[int, str] = {}
        for pid, name, line in rows:
            if pid is None:
                failures.append(f"{rel}:{line}: not a `<id> = \"<Name>\"` entry: {name.strip()!r}")
                continue
            if pid in seen:
                failures.append(f"{rel}:{line}: province {pid} named twice "
                                f"({seen[pid]!r} then {name!r})")
                continue
            seen[pid] = name
            if pid not in defn:
                failures.append(f"{rel}:{line}: province {pid} does not exist")
                continue
            area = area_of.get(pid)
            if not area:
                failures.append(f"{rel}:{line}: province {pid} ({defn[pid]}) is in no "
                                f"area - a sea zone or wasteland never shows a name")
                continue
            if not ASCII_NAME.match(name):
                failures.append(f"{rel}:{line}: {name!r} is not plain ASCII - vanilla "
                                f"stores these files as Windows-1252")
            key = name.casefold()
            hit = next((bad for bad in POST_1750 if bad in key), None)
            if hit:
                failures.append(f"{rel}:{line}: {name!r} names a place founded after "
                                f"1750 ({hit}); the game ends in 1821")
            region = region_of.get(area, "")
            if path.name not in WORLD_FILES and region not in MOD_REGIONS:
                failures.append(f"{rel}:{line}: renames {pid} to {name!r}, but {pid} is "
                                f"{defn[pid]} in {area} ({region or 'no region'}) - far "
                                f"outside this tag's horizon")
        parsed[path.name] = seen

    for name_of_file, seen in parsed.items():
        # Two provinces with the same label in one file is not a script error but
        # it is unreadable on the map, and it is how a transplanted colonial name
        # collides with the homeland one it was copied from.
        by_name = defaultdict(list)
        for pid, name in seen.items():
            by_name[name].append(pid)
        for name, pids in sorted(by_name.items()):
            if len(pids) > 1:
                failures.append(
                    f"common/province_names/{name_of_file}: {name!r} is given to "
                    f"{len(pids)} provinces ({', '.join(str(p) for p in sorted(pids))})")

    for tag, culture in FALLBACK.items():
        if tag not in parsed or culture not in parsed:
            continue
        repeats = [pid for pid, name in parsed[tag].items()
                   if parsed[culture].get(pid) == name]
        if repeats:
            sample = ", ".join(str(p) for p in sorted(repeats)[:6])
            failures.append(
                f"common/province_names/{tag}: {len(repeats)} entries repeat "
                f"{culture} verbatim ({sample}) - EU4 falls through per province, so "
                f"these change nothing and hide who actually disagrees")
    return failures


def self_test(eu4: str) -> int:
    """The mod's orphan-event check was silent from the day it was written. Plant a
    violation of each rule and confirm this one is not."""
    import tempfile
    global PN_DIR
    real = PN_DIR
    defn, area_of, _ = load_map(eu4)
    sea = next(pid for pid in sorted(defn) if pid not in area_of)
    planted = {
        "sea zone or wasteland": '%d = "Nowhere"\n' % sea,
        "does not exist": '999999 = "Atlantis"\n',
        "not plain ASCII": '289 = "Cherni\u0301hiv"\n',
        "founded after 1750": '289 = "Sevastopol"\n',
        "named twice": '289 = "A"\n289 = "B"\n',
        "not a `<id>": 'chernihiv = "yes"\n',
        "is given to 2 provinces": '289 = "Twice"\n290 = "Twice"\n',
    }
    bad = 0
    for expect, body in planted.items():
        with tempfile.TemporaryDirectory() as tmp:
            PN_DIR = Path(tmp)
            (PN_DIR / "ZZZ.txt").write_text(body, encoding="utf-8")
            found = audit(eu4)
            if not any(expect in f for f in found):
                print(f"SELF-TEST FAILED: planting {expect!r} produced {found}")
                bad += 1
    PN_DIR = real
    if not bad:
        print("self-test: all %d planted violations were caught" % len(planted))
    return bad


def main() -> int:
    if not EU4_DIR:
        print("PROVINCE NAME CHECK: SKIPPED - no EU4 install found; set EU4_DIR")
        return 0
    if "--self-test" in sys.argv:
        return 1 if self_test(EU4_DIR) else 0
    if not PN_DIR.is_dir():
        print("PROVINCE NAME CHECK: no common/province_names directory")
        return 0
    failures = audit(EU4_DIR)
    files = sorted(PN_DIR.glob("*.txt"))
    total = sum(len(parse(p)[0]) for p in files)
    if failures:
        print("Province name contract failures:")
        for f in failures:
            print(f"  {f}")
        return 1
    print("PROVINCE NAME CHECK: PASS (%d files, %d names; ids, areas, encoding, "
          "period and layering hold)" % (len(files), total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
