"""Static regression checks for CHR, PRL, and KUY mission/title/event fixes.

Static source-contract checks only — does not launch EU4.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import (
    ROOT,
    _mask_comments_and_strings,
    keyed_blocks,
    named_block,
    normalized,
    read,
    vanilla_root,
)


def _province_history_text(pid: int) -> str:
    matches = sorted(
        list((ROOT / "history/provinces").glob(f"{pid} -*.txt"))
        + list((ROOT / "history/provinces").glob(f"{pid}-*.txt"))
    )
    assert matches, f"Missing history/provinces file for province {pid}"
    return matches[0].read_text(encoding="latin-1", errors="replace")


def _top_level_body(block: str) -> str:
    """Return text directly inside a brace block, excluding nested brace bodies."""
    masked = _mask_comments_and_strings(block)
    start = masked.find("{")
    end = masked.rfind("}")
    assert start != -1 and end > start
    depth = 0
    out: list[str] = []
    for ch in masked[start + 1 : end]:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def check_prl_build_army() -> None:
    prl_text = read("missions/Pereiaslav_Missions.txt")
    mission = named_block(prl_text, "prl_build_army")
    effect = named_block(mission, "effect")
    norm_effect = normalized(effect)

    assert "east_dniepr_area" not in norm_effect, (
        "prl_build_army must not grant claims on east_dniepr_area (already PRL cores)"
    )
    area_claim = named_block(effect, "chernigov_area")
    norm_claim = normalized(area_claim)
    assert "NOT = { is_core = ROOT }" in norm_claim
    assert "NOT = { is_permanent_claim = ROOT }" in norm_claim
    assert "add_permanent_claim = ROOT" in norm_claim

    for pid in (290, 2407, 4542):
        assert re.search(r"(?m)^\s*add_core\s*=\s*PRL\b", _province_history_text(pid)), (
            f"Expected add_core = PRL in east_dniepr_area province {pid}"
        )
    for pid in (289, 1945, 4543):
        assert not re.search(r"\badd_core\s*=\s*PRL\b", _province_history_text(pid)), (
            f"Did not expect PRL core in chernigov_area province {pid}"
        )


def check_prl_orthodox_leadership() -> None:
    prl_text = read("missions/Pereiaslav_Missions.txt")
    mission = named_block(prl_text, "prl_orthodox_leadership")
    highlight = normalized(named_block(mission, "provinces_to_highlight"))
    assert "owned_by = ROOT" in highlight
    assert "NOT = { religion = ROOT }" in highlight

    trigger = named_block(mission, "trigger")
    norm_trigger = normalized(trigger)
    assert "religious_unity = 0.90" in norm_trigger or "religious_unity = 0.9" in norm_trigger
    assert not re.search(r"\breligious_unity\s*=\s*1(?:\.0+)?\b", norm_trigger), (
        "prl_orthodox_leadership must not require 100% religious_unity"
    )

    owned_count = normalized(named_block(trigger, "num_of_owned_provinces_with"))
    assert "value = 10" in owned_count
    assert "religion = ROOT" in owned_count
    assert not re.search(r"\breligion\s*=\s*orthodox\b", owned_count), (
        "prl_orthodox_leadership must check religion = ROOT rather than hardcoded orthodox"
    )


def check_prl_grounded_missions() -> None:
    prl_text = read("missions/Pereiaslav_Missions.txt")

    dip_pres = named_block(prl_text, "prl_diplomatic_prestige")
    dip_trig = normalized(named_block(dip_pres, "trigger"))
    assert "diplomatic_reputation = 2" not in dip_trig
    assert "2407 = { owned_by = ROOT development = 12 }" in dip_trig
    assert "has_dip_advisor = yes" in dip_trig

    gp_trig = normalized(named_block(named_block(prl_text, "prl_great_power_alliance"), "trigger"))
    assert "is_subject = yes" in gp_trig
    assert "any_ally = { total_development = 300 }" in gp_trig

    vassal_trig = normalized(named_block(named_block(prl_text, "prl_vassal_management"), "trigger"))
    assert "is_subject = no" in vassal_trig
    assert "is_subject = yes" not in vassal_trig
    assert "stability = 2" not in vassal_trig
    assert "num_of_subjects = 2" in vassal_trig
    assert "all_subject_country = { NOT = { liberty_desire = 50 } }" in vassal_trig
    assert "2407 = { owned_by = ROOT has_courthouse_building_trigger = yes }" in vassal_trig

    heg_trig = normalized(named_block(named_block(prl_text, "prl_regional_hegemony"), "trigger"))
    assert "army_size = 30" not in heg_trig
    assert "east_dniepr_area = { type = all country_or_non_sovereign_subject_holds = ROOT }" in heg_trig
    assert "chernigov_area = { type = all country_or_non_sovereign_subject_holds = ROOT }" in heg_trig
    assert "2407 = { owned_by = ROOT is_core = ROOT development = 20 }" in heg_trig
    assert "total_own_and_non_tributary_subject_development = 200" in heg_trig

    camp_trig = normalized(named_block(named_block(prl_text, "prl_military_campaigns"), "trigger"))
    assert "army_size = 25" not in camp_trig
    assert "has_manpower_building_trigger = yes" in camp_trig
    assert "region = ruthenia_region" in camp_trig
    assert "num_of_generals = 2" in camp_trig

    sup_trig = normalized(named_block(named_block(prl_text, "prl_military_supremacy"), "trigger"))
    assert "army_size = 40" not in sup_trig
    assert "land_forcelimit = 35" not in sup_trig
    assert "2407 = { owned_by = ROOT has_manpower_building_trigger = yes has_forcelimit_building_trigger = yes }" in sup_trig
    assert "has_forcelimit_building_trigger = yes" in sup_trig
    assert "army_size_percentage = 0.9" in sup_trig


def check_kuy_steppe_granary() -> None:
    shared_mods = read("common/event_modifiers/RIP_shared_modifiers.txt")
    assert "local_goods_produced_modifier" not in _mask_comments_and_strings(shared_mods), (
        "RIP_shared_modifiers.txt must not use invalid key local_goods_produced_modifier"
    )
    granary = normalized(named_block(shared_mods, "kuy_steppe_granary"))
    assert "trade_goods_size_modifier = 0.15" in granary
    assert "local_development_cost = -0.1" in granary

    vanilla = vanilla_root()
    if vanilla is not None:
        van_mods = (vanilla / "common/event_modifiers/00_event_modifiers.txt").read_text(
            encoding="latin-1", errors="replace"
        )
        assert re.search(r"\btrade_goods_size_modifier\b", van_mods), (
            "Expected vanilla 00_event_modifiers.txt to define trade_goods_size_modifier"
        )
        assert not re.search(r"\blocal_goods_produced_modifier\b", van_mods), (
            "Unexpected local_goods_produced_modifier in vanilla 00_event_modifiers.txt"
        )


def check_kuy_chronicle_rework() -> None:
    decision = normalized(named_block(read("decisions/KuyabaNation.txt"), "kuyaba_nation"))
    assert "has_reform = tsardom" in decision and "has_reform = ruthenian_tsardom" in decision
    assert "add_government_reform = iqta" in decision
    assert "add_government_reform = tsardom" not in decision
    assert "add_government_reform = ruthenian_tsardom" not in decision

    kuy_hist = normalized(read("history/countries/KUY - Kuyaba.txt"))
    assert "add_government_reform = iqta" in kuy_hist
    assert "ruthenian_tsardom" not in kuy_hist

    khagan_block = normalized(named_block(read("common/government_names/000_RIP_names.txt"), "kuyaba_khaganate"))
    for token in ("tag = KUY", "government = monarchy", "3 = KHAGANATE", "3 = KHAGAN", "3 = GREAT_KHATUN"):
        assert token in khagan_block, token

    kuy_missions = read("missions/Kuyaba_Missions.txt")
    guilds = named_block(kuy_missions, "KUY_magdeburg_guilds")
    assert "icon = mission_market_place_with_asian_traders" in guilds
    assert "mission_ukr_magdeburg_laws" not in guilds
    guilds_trig = normalized(named_block(guilds, "trigger"))
    assert "280 = { owned_by = ROOT has_trade_building_trigger = yes development = 15 }" in guilds_trig

    restore = normalized(named_block(kuy_missions, "KUY_restore_kuyaba"))
    assert "country_event = { id = kuy_flavor.1 }" in restore

    kuy_events = read("events/RIP_KUY_Kuyaba.txt")
    ev = [
        blk for _, blk in keyed_blocks(kuy_events, "country_event")
        if re.search(r"\bid\s*=\s*kuy_flavor\.1\b", blk) and re.search(r"(?m)^\s*title\s*=", blk)
    ]
    assert len(ev) == 1, "kuy_flavor.1 must be defined once"
    norm_ev = normalized(ev[0])
    assert "is_triggered_only = yes" in norm_ev
    assert "fire_only_once = yes" in norm_ev
    assert "picture = FEAST_eventPicture" in norm_ev
    options = [normalized(blk) for _, blk in keyed_blocks(ev[0], "option")]
    assert len(options) == 2
    assert "add_piety = 0.25" in options[0] and "name = kuy_sober_statutes" in options[0]
    assert "add_piety = -0.25" in options[1] and "name = kuy_mead_excise" in options[1]

    kuy_loc = read("localisation/RIP_KUY_realm_l_english.yml")
    assert '"Podil Akhi Guilds"' in kuy_loc
    assert '"Khaganate of Rus\'"' in kuy_loc
    assert '"Khaganate of Kuyaba"' in kuy_loc
    assert "Magdeburg" not in kuy_loc
    assert "Sultanate" not in kuy_loc
    assert "Ilarion" in kuy_loc and "Saint Sophia" in kuy_loc
    assert "986" in kuy_loc and "Volga Bulgar" in kuy_loc


def check_chr_border_compacts_highlight() -> None:
    chr_text = read("missions/Chernihiv_Missions.txt")
    mission = named_block(chr_text, "chr_border_compacts")
    highlight = named_block(mission, "provinces_to_highlight")

    top_level_pids = re.findall(r"\bprovince_id\s*=\s*\d+", _top_level_body(highlight))
    assert len(top_level_pids) <= 1, (
        f"chr_border_compacts provinces_to_highlight has implicit AND on {top_level_pids}"
    )

    or_block = normalized(named_block(highlight, "OR"))
    assert "province_id = 1945" in or_block
    assert "province_id = 4244" in or_block


def main() -> int:
    check_prl_build_army()
    check_prl_orthodox_leadership()
    check_prl_grounded_missions()
    check_kuy_steppe_granary()
    check_kuy_chronicle_rework()
    check_chr_border_compacts_highlight()
    print(
        "CHR/PRL/KUY MISSION FIXES PASS: prl_build_army claims chernigov_area, "
        "prl_orthodox_leadership uses 0.90 unity + religion = ROOT, "
        "PRL counter missions grounded and prl_vassal_management requires 2 loyal subjects, "
        "kuy_steppe_granary uses trade_goods_size_modifier, "
        "KUY uses Khagan titles, iqta, Podil Akhi Guilds, and kuy_flavor.1, "
        "chr_border_compacts highlight wraps 1945/4244 in OR (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
