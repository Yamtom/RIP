"""Static regression contract for RIP event modifiers.

The check covers the effective mod layer: unique definitions, country/system
ownership, typed country/province calls, English display names, vanilla-key
collisions, and the formatting conventions used by vanilla EU4 files.
"""

from __future__ import annotations

from collections import defaultdict
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MODIFIER_DIR = ROOT / "common" / "event_modifiers"
EU4_CANDIDATES = (
    os.environ.get("EU4_DIR"),
    r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV",
    r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis IV",
)
EU4_DIR = next(
    (
        Path(path)
        for path in EU4_CANDIDATES
        if path and Path(path, "common", "event_modifiers").is_dir()
    ),
    None,
)

COUNTRY_FILES = {
    "VOL_alt_history_modifiers.txt": (re.compile(r"^vol_"), set()),
    "VLN_government_modifiers.txt": (re.compile(r"^vln_"), set()),
    "RIP_KIE_modifiers.txt": (
        re.compile(r"^(?:KIE_|UKR_)"),
        {
            "council_of_florence",
            "subjugation_of_the_great_horde",
            "subjugation_of_the_crimeans",
        },
    ),
    "RIP_VOL_modifiers.txt": (
        re.compile(r"^(?:VOL_|vol_)"),
        {"fortress_modifier", "embraced_minority_religion", "tolerant_policy"},
    ),
    "RIP_CHR_modifiers.txt": (re.compile(r"^chr_"), set()),
    "RIP_ZAZ_modifiers.txt": (
        re.compile(r"^(?:zaz_|sich_|zich_|zaporozhian_)"),
        {
            "mobile_sich",
            "steppe_cavalry_tactics",
            "orthodox_defender_war",
            "ottoman_protected_sich",
            "cossack_freed_slaves",
            "frontier_military_culture",
            "russian_protection",
        },
    ),
    "RIP_UZH_modifiers.txt": (
        re.compile(r"^uz_"),
        {"orthodox_zeal", "hungarian_integration_zeal", "danubian_monarchy_influence"},
    ),
    "RIP_DNIESTER_modifiers.txt": (re.compile(r"^dniester_"), set()),
    "RIP_HET_modifiers.txt": (
        re.compile(r"^(?:het_|hetman_|hetmanate_|ruina_|sloboda_)"),
        {
            "left_bank_administration",
            "kyiv_autonomy_guaranteed",
            "centralized_control",
            "orthodox_protector",
            "grain_export_hub",
            "mazepa_golden_age",
            "russian_backed_hetman",
        },
    ),
    "RIP_KRU_modifiers.txt": (
        re.compile(r"^(?:KRU_|kru_)"),
        {
            "svydrigaylo_starshyna_council",
            "svydrigaylo_preparing_independence",
            "svydrigaylo_independent_ruthenian_state",
            "khmelnytsky_ferment",
            "khmelnytsky_negotiations",
            "svydrigaylo_legacy",
        },
    ),
    "RIP_POL_modifiers.txt": (re.compile(r"^pol_"), set()),
    "RIP_BELARUS_modifiers.txt": (
        re.compile(
            r"^(?:belarus_|belarusian_|polotsk_|minsk_|turov_|vitebsk_|"
            r"dvina_|mstislavl_|gdl_)"
        ),
        {"polesian_marsh_tactics", "fortified_border", "polesian_timber_trade"},
    ),
    "RIP_HAIDAMAKY_modifiers.txt": (
        re.compile(r"^(?:haidamaka_|nadvirna_|koliivshchyna_|order_)"),
        set(),
    ),
}

TYPED_CALLS = {
    "country": (
        re.compile(
            r"add_country_modifier\s*=\s*\{"
            r"(?:(?!\n\s*\}).){0,300}?name\s*=\s*\"?([A-Za-z0-9_]+)",
            re.S,
        ),
        re.compile(r"has_country_modifier\s*=\s*\"?([A-Za-z0-9_]+)"),
        re.compile(r"remove_country_modifier\s*=\s*\"?([A-Za-z0-9_]+)"),
    ),
    "province": (
        re.compile(
            r"add_(?:permanent_)?province_modifier\s*=\s*\{"
            r"(?:(?!\n\s*\}).){0,300}?name\s*=\s*\"?([A-Za-z0-9_]+)",
            re.S,
        ),
        re.compile(r"has_province_modifier\s*=\s*\"?([A-Za-z0-9_]+)"),
        re.compile(r"remove_province_modifier\s*=\s*\"?([A-Za-z0-9_]+)"),
    ),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def definitions(folder: Path) -> dict[str, list[tuple[Path, int]]]:
    result: dict[str, list[tuple[Path, int]]] = defaultdict(list)
    for path in folder.glob("*.txt"):
        for line_number, line in enumerate(read(path).splitlines(), 1):
            match = re.match(r"^([A-Za-z0-9_]+)\s*=\s*\{", line)
            if match:
                result[match.group(1)].append((path, line_number))
    return result


def english_keys() -> set[str]:
    result: set[str] = set()
    for path in (ROOT / "localisation").rglob("*_l_english.yml"):
        for line in read(path).splitlines():
            match = re.match(r"^\s*([^#\s][^:]*):\d+\s", line)
            if match:
                result.add(match.group(1).strip())
    return result


def script_files():
    for dirname in ("common", "decisions", "events", "missions", "history"):
        for path in (ROOT / dirname).rglob("*.txt"):
            if "event_modifiers" not in path.parts:
                yield path


def main() -> int:
    failures: list[str] = []
    modifier_defs = definitions(MODIFIER_DIR)

    if (MODIFIER_DIR / "RIP_event_modifiers.txt").exists():
        failures.append("RIP_event_modifiers.txt monolith must stay removed")
    if (MODIFIER_DIR / "VLN_mission_modifiers.txt").exists():
        failures.append("VLN_mission_modifiers.txt must stay split by VOL/VLN owner")
    for filename in (*COUNTRY_FILES, "RIP_shared_modifiers.txt"):
        if not (MODIFIER_DIR / filename).is_file():
            failures.append(f"missing ownership file: {filename}")

    for key, locations in modifier_defs.items():
        if len(locations) != 1:
            rendered = ", ".join(f"{p.name}:{line}" for p, line in locations)
            failures.append(f"duplicate modifier {key}: {rendered}")

    for filename, (prefix, exceptions) in COUNTRY_FILES.items():
        path = MODIFIER_DIR / filename
        if not path.exists():
            continue
        for key in definitions(path):
            if not prefix.match(key) and key not in exceptions:
                failures.append(f"{filename}: {key} violates its ownership contract")

    for path in MODIFIER_DIR.glob("*.txt"):
        for line_number, line in enumerate(read(path).splitlines(), 1):
            code = line.split("#", 1)[0]
            if line.rstrip() != line:
                failures.append(f"{path.name}:{line_number}: trailing whitespace")
            if re.match(r"^ +[^#\s]", line):
                failures.append(f"{path.name}:{line_number}: spaces used for code indentation")
            if re.search(r"(?<![\w.])-?\d+\.\d*0\b", code):
                failures.append(f"{path.name}:{line_number}: redundant decimal zero")
            if "Core_creation" in code or "local_prov_trade_power_modifier" in code:
                failures.append(f"{path.name}:{line_number}: non-vanilla modifier spelling")

    names = english_keys()
    for key in modifier_defs:
        if key not in names:
            failures.append(f"missing English display name for {key}")

    typed_uses: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for path in script_files():
        text = read(path)
        for scope, patterns in TYPED_CALLS.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    key = match.group(1)
                    if key in modifier_defs:
                        line = text.count("\n", 0, match.start()) + 1
                        typed_uses[key][scope].append(f"{path.relative_to(ROOT)}:{line}")
    for key, scopes in typed_uses.items():
        if len(scopes) > 1:
            failures.append(
                f"{key} is called through country and province APIs: {dict(scopes)}"
            )

    contracts = {
        "common/scripted_triggers/south_ukraine_triggers.txt": (
            "has_province_modifier = VOL_chumak_modifier",
            "has_province_modifier = west_ukr_chumak_trade",
        ),
        "common/scripted_triggers/zaz_mechanics_triggers.txt": (
            "has_province_modifier = hetmanate_capital",
        ),
        "events/DniesterEstuary.txt": (
            "has_province_modifier = dniester_cossack_raids_threat",
            "name = dniester_anti_raid_fortifications",
        ),
        "missions/Zaporozhie_Missions.txt": (
            "name = zaz_dniester_chumak_route",
        ),
    }
    for relative, needles in contracts.items():
        text = read(ROOT / relative)
        for needle in needles:
            if needle not in text:
                failures.append(f"{relative}: missing scope contract {needle!r}")

    if EU4_DIR:
        vanilla_defs = definitions(EU4_DIR / "common" / "event_modifiers")
        collisions = sorted(set(modifier_defs) & set(vanilla_defs))
        if collisions:
            failures.append("vanilla event-modifier key collisions: " + ", ".join(collisions))

    if failures:
        print("EVENT MODIFIER CHECK: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "EVENT MODIFIER CHECK: PASS "
        f"({len(modifier_defs)} unique definitions; no mixed-scope calls)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
