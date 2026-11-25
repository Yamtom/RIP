"""Static regression checks for CHR, PRL, and KUY mission/title/event fixes.

Static source-contract checks only — does not launch EU4.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from check_donor_mission_ports import parse_series_in_file
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
    assert "stability = 2" not in vassal_trig
    assert "num_of_subjects = 2" not in vassal_trig
    assert "2407 = { owned_by = ROOT has_courthouse_building_trigger = yes }" in vassal_trig
    vassal_or = normalized(named_block(named_block(named_block(prl_text, "prl_vassal_management"), "trigger"), "OR"))
    assert "is_subject = no num_of_subjects = 1 all_subject_country = { NOT = { liberty_desire = 50 } has_opinion = { who = ROOT value = 125 } }" in vassal_or
    assert "all_ally = { has_opinion = { who = ROOT value = 150 }" in vassal_or and "amount = 2" in vassal_or
    assert "is_subject = yes overlord = { has_opinion = { who = ROOT value = 150 }" in vassal_or

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


def check_chr_crimean_compact_routes() -> None:
    mission = named_block(read("missions/Chernihiv_Missions.txt"), "chr_crimean_compact_mission")
    trigger = named_block(mission, "trigger")
    assert "chr_ruina_path_" not in trigger
    routes = named_block(trigger, "OR")
    assert "alliance_with = CRI" in normalized(named_block(routes, "custom_trigger_tooltip"))
    assert "crimea_area = { type = all owned_by = ROOT is_core = ROOT }" in normalized(routes)
    assert "CRI" not in _top_level_body(trigger) + _top_level_body(routes)


def check_prl_successor_content() -> None:
    missions = read("missions/Pereiaslav_Missions.txt")
    events = dict(
        (re.search(r"\bid = (prl_flavor\.\d+)", block)[1], block)
        for _, block in keyed_blocks(read("events/RIP_PRL_PereiaslavFlavor.txt"), "country_event")
    )
    for number, mission, flag in (
        (1, "prl_great_power_alliance", "prl_pereiaslav_council_prepared"),
        (2, "prl_regimental_organization", "prl_statute_prepared"),
        (3, "prl_brotherhood_schools", "prl_brotherhood_prepared"),
        (4, "prl_trade_dominance", "prl_trubizh_prepared"),
    ):
        event = events[f"prl_flavor.{number}"]
        assert f"set_country_flag = {flag}" in named_block(named_block(missions, mission), "effect")
        trigger = named_block(event, "trigger")
        assert "prl_has_legacy_missions = yes" in _top_level_body(trigger)
        assert f"has_country_flag = {flag}" in named_block(event, "mean_time_to_happen")
        if number in (2, 3):
            assert f"AND = {{ tag = HET has_country_flag = {flag} }}" in normalized(trigger)

    het_events = read("events/RIP_HET_HetmanateFlavor.txt")
    het_council = next(block for _, block in keyed_blocks(het_events, "country_event")
                       if re.search(r"\bid = het_flavor\.3\b", block))
    assert "NOT = { AND = { prl_has_legacy_missions = yes owns = 2407 } }" in normalized(named_block(het_council, "trigger"))
    for council in (het_council, events["prl_flavor.1"]):
        for flag in ("pereiaslav_treaty_signed", "rip_pereiaslav_council_declined"):
            assert f"NOT = {{ has_country_flag = {flag} }}" in normalized(named_block(council, "trigger"))
            assert f"set_country_flag = {flag}" in council

    decision = named_block(read("decisions/PereiaslavGovernmentDecisions.txt"), "prl_establish_regimental_republic")
    potential = normalized(named_block(decision, "potential"))
    assert "prl_has_legacy_missions = yes" in potential
    assert "AND = { tag = HET government = republic }" in potential
    reform = named_block(read("common/government_reforms/RIP_PRL_government_reforms.txt"), "prl_regimental_republic_reform")
    for gate in ("potential", "trigger"):
        assert "prl_has_legacy_missions = yes" in named_block(reform, gate)


def check_prl_slot5_and_interactive_rewards() -> None:
    prl_text = read("missions/Pereiaslav_Missions.txt")
    slot5 = named_block(prl_text, "prl_missions_5")

    expected_order = [
        ("prl_professional_army", 1, "required_missions = { }"),
        ("prl_military_campaigns", 2, "required_missions = { prl_professional_army }"),
        ("prl_regimental_organization", 3, "required_missions = { prl_military_campaigns }"),
        ("prl_military_supremacy", 4, "required_missions = { prl_regimental_organization }"),
        ("prl_sloboda_regiments", 5, "required_missions = { prl_military_supremacy }"),
    ]
    offsets = []
    for name, pos, req in expected_order:
        blk = normalized(named_block(slot5, name))
        assert f"position = {pos}" in blk, (name, pos)
        assert req in blk, (name, req)
        offsets.append(slot5.index(f"{name} = {{"))
    assert offsets == sorted(offsets), "Slot 5 missions must appear in sequential row order"

    prof_trig_raw = named_block(named_block(slot5, "prl_professional_army"), "trigger")
    prof_trig = normalized(prof_trig_raw)
    assert "prl_regimental_era" not in prof_trig
    assert 'has_dlc = "Cradle of Civilization"' in prof_trig_raw
    assert "else = { army_tradition = 30 }" in prof_trig

    camp_trig = normalized(named_block(named_block(slot5, "prl_military_campaigns"), "trigger"))
    assert "prl_regimental_era" not in camp_trig

    reg_blk = named_block(slot5, "prl_regimental_organization")
    assert "prl_regimental_era = yes" in normalized(named_block(reg_blk, "trigger"))
    reg_eff = normalized(named_block(reg_blk, "effect"))
    assert "set_country_flag = prl_statute_prepared" in reg_eff
    assert "set_country_flag = prl_regimental_republic_unlocked" in reg_eff
    assert "country_event = { id = prl_flavor.6 }" in reg_eff

    sup_eff = normalized(named_block(named_block(slot5, "prl_military_supremacy"), "effect"))
    assert "sloboda_ukraine_area = { limit = { NOT = { is_core = ROOT } NOT = { is_permanent_claim = ROOT } } add_permanent_claim = ROOT }" in sup_eff
    assert "4543 = { if = { limit = { NOT = { is_core = ROOT } NOT = { is_permanent_claim = ROOT } } add_permanent_claim = ROOT } }" in sup_eff

    slob_eff = normalized(named_block(named_block(slot5, "prl_sloboda_regiments"), "effect"))
    assert "sloboda_ukraine_area = { limit = { owned_by = ROOT } add_base_manpower = 1 add_local_autonomy = -15 }" in slob_eff

    assert "country_event = { id = prl_flavor.5 }" in normalized(named_block(named_block(prl_text, "prl_river_flotilla"), "effect"))
    trade_eff = normalized(named_block(named_block(prl_text, "prl_trade_dominance"), "effect"))
    assert "center_of_trade = 1" in trade_eff and "add_center_of_trade_level = 1" in trade_eff
    broth_eff = normalized(named_block(named_block(prl_text, "prl_brotherhood_schools"), "effect"))
    assert "add_building = university" in broth_eff
    magd_eff = normalized(named_block(named_block(prl_text, "prl_magdeburg_charter"), "effect"))
    assert "name = prl_magdeburg_charter_modifier duration = -1" in magd_eff

    events = {
        re.search(r"\bid = (prl_flavor\.\d+)", block)[1]: normalized(block)
        for _, block in keyed_blocks(read("events/RIP_PRL_PereiaslavFlavor.txt"), "country_event")
    }
    for eid in ("prl_flavor.5", "prl_flavor.6"):
        assert eid in events, eid
        assert "is_triggered_only = yes" in events[eid], eid
        assert "fire_only_once" not in events[eid], eid


def check_chr_layout_compaction() -> None:
    chr_text = read("missions/Chernihiv_Missions.txt")
    assert "UZH_this_is_a_branching_mission" not in chr_text

    series = parse_series_in_file("missions/Chernihiv_Missions.txt")
    by_name = {sname: (slot, ms) for sname, slot, _, ms in series}
    branches = (
        "chr_missions_2_branch_placeholder",
        "chr_missions_2_diplomatic",
        "chr_missions_2_frontier",
    )
    assert [(m, p) for m, p, _ in by_name["chr_missions_2_branch_placeholder"][1]] == [
        ("chr_identity_branching_1", 6),
        ("chr_identity_branching_2", 7),
        ("chr_identity_branching_3", 8),
        ("chr_identity_branching_4", 9),
    ]
    for bname in ("chr_missions_2_diplomatic", "chr_missions_2_frontier"):
        assert [p for _, p, _ in by_name[bname][1]] == [6, 7, 8, 9], bname

    for active in branches:
        cursors: dict[int, int] = {s: 0 for s in range(1, 6)}
        grid: dict[tuple[int, int], str] = {}
        placed: dict[str, tuple[int, int, list[str]]] = {}
        by_slot: dict[int, list[int]] = {s: [] for s in range(1, 6)}
        for sname, slot, _, ms in series:
            if sname in branches and sname != active:
                continue
            prev = 0
            for mname, pos, reqs in ms:
                assert pos > prev, (active, sname, mname, pos, prev)
                prev = pos
                row = max(cursors[slot] + 1, pos)
                assert row == pos, (active, mname, pos, row)
                assert (slot, row) not in grid, (active, slot, row, grid[(slot, row)], mname)
                cursors[slot] = row
                grid[(slot, row)] = mname
                placed[mname] = (slot, row, reqs)
                by_slot[slot].append(row)

        assert max(p for _, p in grid) == 14, active
        for mname, (s, p, reqs) in placed.items():
            for dep in reqs:
                ds, dp, _ = placed[dep]
                assert p - dp == 1, (active, f"{dep}(s{ds}p{dp}) -> {mname}(s{s}p{p})")
                for y in range(dp + 1, p):
                    assert (ds, y) not in grid, (active, mname, dep, grid[(ds, y)])
        assert by_slot[1] == list(range(1, 10))
        assert by_slot[2] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14]
        assert by_slot[3] == list(range(1, 15))
        assert by_slot[4] == list(range(2, 12))
        assert by_slot[5] == list(range(1, 12))
        assert grid[(5, 1)] == "chr_kiev_2"

    for mname, dep in (
        ("chr_Smolensk", "chr_conquer_states"),
        ("chr_Astrakhan", "chr_grain_guild_charters"),
        ("chr_left_bank_collegium_mission", "chr_black_soil_silos"),
        ("chr_Accept_Ruthenian", "chr_Minsk"),
    ):
        trig = normalized(named_block(named_block(chr_text, mname), "trigger"))
        assert f"mission_completed = {dep}" in trig, (mname, dep)


def check_kuy_expanded_tree() -> None:
    series = parse_series_in_file("missions/Kuyaba_Missions.txt")
    assert [sname for sname, slot, _, _ in series] == [f"KUY_missions_{i}" for i in range(1, 6)]
    all_ms = {mname: (slot, pos, reqs) for _, slot, _, ms in series for mname, pos, reqs in ms}
    assert len(all_ms) == 13, len(all_ms)
    assert all_ms["KUY_volga_bulgar_road"] == (1, 3, ["KUY_granary_of_steppe", "KUY_dnieper_crossings"])
    assert all_ms["KUY_compact_of_rus_faiths"] == (5, 1, [])
    assert all_ms["KUY_islamic_schools"] == (5, 2, ["KUY_compact_of_rus_faiths"])
    assert all_ms["KUY_caliphate_envoys"] == (5, 3, ["KUY_islamic_schools"])

    kuy_text = read("missions/Kuyaba_Missions.txt")
    volga_trig = normalized(named_block(named_block(kuy_text, "KUY_volga_bulgar_road"), "trigger"))
    assert "1082 = { country_or_non_sovereign_subject_holds = ROOT }" in volga_trig
    assert "4267 = { country_or_non_sovereign_subject_holds = ROOT }" in volga_trig
    assert "1082 = { trade_share = { country = ROOT share = 20 } }" in volga_trig
    assert "464 = { trade_share = { country = ROOT share = 20 } }" in volga_trig
    assert "kuy_volga_bulgar_road_modifier" in normalized(named_block(named_block(kuy_text, "KUY_volga_bulgar_road"), "effect"))

    assert "country_event = { id = kuy_flavor.2 }" in normalized(named_block(named_block(kuy_text, "KUY_compact_of_rus_faiths"), "effect"))
    kuy_events = read("events/RIP_KUY_Kuyaba.txt")
    ev2 = [
        blk for _, blk in keyed_blocks(kuy_events, "country_event")
        if re.search(r"\bid\s*=\s*kuy_flavor\.2\b", blk) and re.search(r"(?m)^\s*title\s*=", blk)
    ]
    assert len(ev2) == 1, "kuy_flavor.2 must be defined once"
    norm_ev2 = normalized(ev2[0])
    assert "is_triggered_only = yes" in norm_ev2 and "fire_only_once = yes" in norm_ev2
    assert "picture = PRAYING_eventPicture" in norm_ev2
    opts = [normalized(blk) for _, blk in keyed_blocks(ev2[0], "option")]
    assert len(opts) == 2
    assert "kuy_rus_mosque_endowment" in opts[0] and "add_piety = 0.25" in opts[0]
    assert "kuy_kyiv_dhimmi_charter" in opts[1] and "add_piety = -0.25" in opts[1]

    sch_blk = named_block(kuy_text, "KUY_islamic_schools")
    assert 'has_dlc = "Cradle of Civilization"' in sch_blk
    assert "add_building = university" in normalized(named_block(sch_blk, "effect"))
    assert "kuy_kyiv_madrasa_network" in normalized(named_block(sch_blk, "effect"))

    cal_blk = named_block(kuy_text, "KUY_caliphate_envoys")
    cal_trig = normalized(named_block(cal_blk, "trigger"))
    assert "is_defender_of_faith = yes" in cal_trig
    for pid in (385, 361, 410, 151):
        assert f"{pid} = {{ country_or_non_sovereign_subject_holds = ROOT }}" in cal_trig
    assert "kuy_caliphate_recognition" in normalized(named_block(cal_blk, "effect"))

    shared_mods = read("common/event_modifiers/RIP_shared_modifiers.txt")
    for mod, key in (
        ("kuy_volga_bulgar_road_modifier", "merchants = 1"),
        ("kuy_rus_mosque_endowment", "global_missionary_strength = 0.02"),
        ("kuy_kyiv_dhimmi_charter", "tolerance_heathen = 2"),
        ("kuy_kyiv_madrasa_network", "technology_cost = -0.05"),
        ("kuy_caliphate_recognition", "institution_spread_from_true_faith = 0.25"),
    ):
        assert key in normalized(named_block(shared_mods, mod)), (mod, key)


def check_kyiv_and_caravan_rewards() -> None:
    kyiv = named_block(read("missions/Chernihiv_Missions.txt"), "chr_kiev_2")
    assert "flavor_rus." not in kyiv and "name = chr_old" in kyiv
    missions = read("missions/Kuyaba_Missions.txt")
    restoration = named_block(named_block(missions, "KUY_restore_kuyaba"), "effect")
    crossings = named_block(named_block(missions, "KUY_dnieper_crossings"), "effect")
    assert "east_dniepr_area" not in restoration and "chernigov_area" not in crossings
    assert "add_permanent_claim = ROOT" in named_block(restoration, "moldavia_area")
    assert "add_claim = ROOT" in named_block(crossings, "azov_area")
    caravans = named_block(missions, "KUY_steppe_caravans")
    assert "kuy_caravan_waystation = yes" in named_block(caravans, "trigger")
    draws = list(keyed_blocks(named_block(caravans, "effect"), "random_owned_province"))
    assert len(draws) == 3
    for _, draw in draws:
        limit = normalized(named_block(draw, "limit"))
        assert "kuy_caravan_waystation = yes" in limit
        assert "NOT = { has_province_flag = kuy_caravan_improved }" in limit
        assert "set_province_flag = kuy_caravan_improved" in draw and "add_base_production = 1" in draw
    assert "clr_province_flag = kuy_caravan_improved" in named_block(caravans, "every_owned_province")

    chr_mods = read("common/event_modifiers/RIP_CHR_modifiers.txt")
    for mod in ("chr_bunchuk_tovaryshi", "chr_pantheon_samoylovych_chancery"):
        body = normalized(named_block(chr_mods, mod))
        assert "administrative_efficiency" not in body, (mod, body)
    assert "state_governing_cost = -0.1" in normalized(named_block(chr_mods, "chr_pantheon_samoylovych_chancery"))
    assert "state_maintenance_modifier = -0.15" in normalized(named_block(chr_mods, "chr_bunchuk_tovaryshi"))


def main() -> int:
    check_kyiv_and_caravan_rewards()
    check_prl_build_army()
    check_prl_orthodox_leadership()
    check_prl_grounded_missions()
    check_prl_slot5_and_interactive_rewards()
    check_prl_successor_content()
    check_kuy_steppe_granary()
    check_kuy_chronicle_rework()
    check_kuy_expanded_tree()
    check_chr_border_compacts_highlight()
    check_chr_crimean_compact_routes()
    check_chr_layout_compaction()
    print(
        "CHR/PRL/KUY MISSION FIXES PASS: prl_build_army claims chernigov_area, "
        "prl_orthodox_leadership uses 0.90 unity + religion = ROOT, "
        "PRL Slot 3 smooth diplomacy + Slot 5 unblocked before 1600 + Sloboda claims + interactive rewards, "
        "kuy_steppe_granary uses trade_goods_size_modifier, "
        "KUY expands to 13 missions (Volga-Bolgar + Slot 5 faith/schools/caliphate + kuy_flavor.2), "
        "chr_border_compacts highlight wraps 1945/4244 in OR (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
