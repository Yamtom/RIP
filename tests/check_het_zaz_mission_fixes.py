"""Static contracts for the 22 November 2026 ZAZ and HET mission repairs, as merged with the Rada redesign.

ZAZ: every ambush event belongs to its own city and the Free State has its own event;
the choice of protectors opens without the raid on Constantinople; the Lithuanian
ambush is wired and no longer punishes ROOT; the Turkish "other ally" mission rejects
both Ottoman tags; the Polish branch reaches its conversion event. HET: the Moldavian
line can be won beside a free ally. (The alliance partners, the Polish claims and
Mazepa's course were redesigned on main in the same hours; check_zaz_rada.py and
check_zaz_het_mission_redesign.py hold those.)

Source-contract checks only - this does not launch EU4.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read  # noqa: E402


def mission(path: str, name: str) -> str:
    return named_block(read(path), name)


def events(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for _, block in keyed_blocks(read(path), "country_event"):
        match = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", block)
        if match:
            out[match[1]] = block
    return out


def english_loc() -> dict[str, str]:
    values: dict[str, str] = {}
    for folder in ("localisation", "localisation/replace"):
        for path in sorted((ROOT / folder).glob("*_l_english.yml")):
            for key, value in re.findall(
                r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', path.read_text(encoding="utf-8-sig"), re.M
            ):
                values[key] = value
    return values


def replace_keys(lang: str) -> set[str]:
    keys: set[str] = set()
    for path in sorted((ROOT / "localisation/replace").glob(f"*_l_{lang}.yml")):
        keys |= set(re.findall(r"^ ([A-Za-z0-9_.\-]+):\d*\s+\"", path.read_text(encoding="utf-8-sig"), re.M))
    return keys


def called_events(text: str) -> list[str]:
    return re.findall(r"country_event\s*=\s*\{[^}]*?\bid\s*=\s*([A-Za-z0-9_.]+)", text)


def required(block: str) -> list[str]:
    match = re.search(r"required_missions\s*=\s*\{([^}]*)\}", block)
    return match[1].split() if match else []


ZAZ = "missions/Zaporozhie_Missions.txt"
HET = "missions/zzz_Hetmanate_Missions.txt"


def check_zaz_events_belong_to_their_city() -> None:
    zaz_events = events("events/RIP_ZAZ_ZAZmission.txt")
    loc = english_loc()
    text = read(ZAZ)
    # mission -> (event, province ids the event takes, word its title and text must carry)
    pairs = {
        "ZAZ_lit": ("zaz_flavor_m_1.1", {272, 275, 1936}, "Lithuania"),
        "ZAZ_krakow": ("zaz_flavor_m_2.1", {262}, "Krak"),
        "ZAZ_moskva": ("zaz_flavor_m_2.2", {295}, "Moscow"),
        "ZAZ_saratov": ("zaz_flavor_m_3.2", {303}, "Saratov"),
        "ZAZ_istanbul": ("zaz_flavor_m_3.3", {151}, "Bosporus"),
    }
    for name, (event_id, provinces, word) in pairs.items():
        effect = normalized(named_block(mission(ZAZ, name), "effect"))
        assert called_events(effect) == [event_id], (name, called_events(effect))
        taken = {int(p) for p in re.findall(r"(\d+) = \{ change_controller = ROOT", normalized(zaz_events[event_id]))}
        assert taken == provinces, (event_id, taken)
        assert word in loc[f"{event_id}.t"], (event_id, loc[f"{event_id}.t"])
        assert word in loc[f"{event_id}.d"] or (word == "Bosporus" and "Constantinople" in loc[f"{event_id}.d"]), event_id
        target = re.search(r"province_id = (\d+)", normalized(named_block(mission(ZAZ, name), "provinces_to_highlight")))
        assert target and int(target[1]) in provinces, (name, target and target[1])
    for event_id in (pair[0] for pair in pairs.values()):
        assert len(re.findall(rf"\bid\s*=\s*{re.escape(event_id)}\b", text)) == 1, event_id
    # the Lithuanian ambush may not punish ROOT for provinces ROOT already owns
    lit = normalized(zaz_events["zaz_flavor_m_1.1"])
    assert lit.count("owner = {") == lit.count("NOT = { owned_by = ROOT }") == 9, lit.count("owner = {")
    assert "add_years_of_income = 5" not in lit and "add_years_of_income = 2" in lit

    finally_effect = normalized(named_block(mission(ZAZ, "ZAZ_finally"), "effect"))
    assert called_events(finally_effect) == ["zaz_flavor_m_3.1"], finally_effect
    assert "change_controller" not in normalized(zaz_events["zaz_flavor_m_3.1"])
    assert loc["zaz_flavor_m_3.1.t"] == "The Free Zaporozhian State"
    for lang in ("french", "german", "spanish"):
        keys = replace_keys(lang)
        for key in ("zaz_flavor_m_3.1.t", "zaz_flavor_m_3.2.t", "zaz_flavor_m_3.3.t", "zaz_flavor_m_3.3.d"):
            assert key in keys, (lang, key)


def check_zaz_council_without_the_bosphorus() -> None:
    assert required(mission(ZAZ, "ZAZ_finally")) == ["ZAZ_proper"]
    holders = [
        name for name in re.findall(r"(?m)^\t(ZAZ_[A-Za-z0-9_]+) = \{", read(ZAZ))
        if "ZAZ_istanbul" in required(mission(ZAZ, name))
    ]
    assert holders == ["ZAZ_heroic_campaigns"], holders


def check_zaz_turkish_other_ally_and_polish_conversion() -> None:
    pact = mission(ZAZ, "ZAZ_TUR_convert_islam")
    assert "alliance_with = TUR alliance_with = RUM" in normalized(named_block(pact, "trigger"))
    assert "religion = orthodox" in named_block(pact, "effect")
    islam = events("events/RIP_ZAZ_ZAZmission.txt")["zaz_flavor_m_5.1"]
    schools, keep = [normalized(block) for _, block in keyed_blocks(islam, "option")]
    assert "change_religion" not in islam
    assert "treasury = 50" in schools and "add_treasury = -50" in schools
    assert "prl_brotherhood_schools" in schools and "add_patriarch_authority" in keep
    different = normalized(named_block(mission(ZAZ, "ZAZ_TUR_different_ally"), "trigger"))
    assert different == "trigger = { any_ally = { NOT = { tag = TUR } NOT = { tag = RUM } } }", different

    second = mission(ZAZ, "ZAZ_POL_politics_2")
    assert "OR = { alliance_with = PLC alliance_with = POL }" in normalized(named_block(second, "trigger"))
    assert called_events(normalized(named_block(second, "effect"))) == ["zaz_flavor_m_5.2"]
    assert "religion = orthodox is_religion_enabled = greek_catholic" in normalized(named_block(second, "effect"))

    conversion = events("events/RIP_ZAZ_ZAZmission.txt")["zaz_flavor_m_5.2"]
    options = [normalized(block) for _, block in keyed_blocks(conversion, "option")]
    assert len(options) == 2
    convert, stay = options
    assert "change_religion = greek_catholic" in convert and "factor = 0.1" in convert
    assert "factor = 0.9" in stay


def check_het_moldavian_line() -> None:
    alliance = mission(HET, "het_moldovan_alliance")
    effect = normalized(named_block(alliance, "effect"))
    assert (
        "if = { limit = { NOT = { alliance_with = MOL } NOT = { MOL = { is_subject_of = ROOT } } } "
        "moldavia_area = {" in effect
    ), effect
    assert effect.count("moldavia_area = {") == 1
    assert "wallachia_area = {" in effect

    union = mission(HET, "het_absorb_moldova")
    assert required(union) == ["het_moldovan_alliance"]
    trigger = normalized(named_block(union, "trigger"))
    assert "MOL = { is_subject_of = ROOT }" in trigger
    assert "country_or_non_sovereign_subject_holds = ROOT" in trigger
    free = "AND = { alliance_with = MOL MOL = { is_subject = no } OR = { has_country_flag = het_defended_moldavia has_country_flag = het_moldavia_pressure_held } }"
    assert free in trigger, trigger
    union_effect = normalized(named_block(union, "effect"))
    assert "else_if = { limit = { alliance_with = MOL MOL = { is_subject = no } } add_country_modifier = { name = het_moldovan_sworn_alliance" in union_effect
    assert "het_moldovan_vassalization" in union_effect and "het_moldovan_conquest" in union_effect
    assert "add_claim = ROOT" in union_effect  # Danube expansion stays a full alternative
    assert required(mission(HET, "het_danube_frontier")) == ["het_absorb_moldova"]

    modifiers = read("common/event_modifiers/ruthenian_eastward_modifiers.txt")
    assert len(re.findall(r"(?m)^het_moldovan_sworn_alliance\s*=", modifiers)) == 1
    body = normalized(named_block(modifiers, "het_moldovan_sworn_alliance"))
    for token in ("diplomatic_reputation = 2", "ae_impact = -0.1", "improve_relation_modifier = 0.25", "prestige = 0.25"):
        assert token in body, token

    moldova = events("events/RIP_HET_HetmanateMoldovanExpansion.txt")
    defence = normalized(moldova["het_moldova.7"])
    assert "has_country_flag = het_unlocked_moldovan_path" in defence
    assert "alliance_with = MOL" in defence and "is_in_war = { defenders = MOL }" in defence
    assert "set_country_flag = het_defended_moldavia" in defence
    assert "is_triggered_only" not in defence and "mean_time_to_happen" in defence
    pressure = normalized(moldova["het_moldova.8"])
    assert "alliance_with = MOL" in pressure and "is_great_power = yes" in pressure
    assert "had_country_flag = { flag = het_unlocked_moldovan_path days = 1825 }" in pressure
    assert "set_country_flag = het_moldavia_pressure_held" in pressure
    assert "is_triggered_only" not in pressure and "mean_time_to_happen" in pressure

    loc = english_loc()
    for key in (
        "het_moldova.7.t", "het_moldova.7.d", "het_moldova.7.a", "het_moldova.7.b",
        "het_moldova.8.t", "het_moldova.8.d", "het_moldova.8.a", "het_moldova.8.b",
        "het_moldovan_sworn_alliance", "desc_het_moldovan_sworn_alliance",
        "het_absorb_moldova_title", "het_absorb_moldova_desc", "het_moldovan_alliance_tt",
    ):
        assert key in loc, key
        for lang in ("french", "german", "spanish"):
            assert key in replace_keys(lang), (lang, key)
    assert "free" in loc["het_absorb_moldova_desc"] and "ally" in loc["het_absorb_moldova_desc"]
    assert "!" not in " ".join(v for k, v in loc.items() if k.startswith(("het_moldova.7", "het_moldova.8")))


def main() -> int:
    check_zaz_events_belong_to_their_city()
    check_zaz_council_without_the_bosphorus()
    check_zaz_turkish_other_ally_and_polish_conversion()
    check_het_moldavian_line()
    print(
        "HET/ZAZ MISSION FIXES PASS: five ambush events fire from their own city and the Free State "
        "has its own event, the council needs ZAZ_proper only, the Turkish other-ally mission rejects "
        "TUR and RUM, the Polish branch reaches its conversion event, and the Moldavian Union accepts "
        "a defended or pressured free ally (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
