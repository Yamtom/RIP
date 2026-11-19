"""Static contracts for UZH highlights, farm_estate eligibility, coal fallback, and theocracy reachability."""
from __future__ import annotations

import re

from clausewitz_testlib import ROOT, keyed_blocks, line_number, named_block, normalized, read


SYNCED_LOC_KEYS = (
    "uzh_agriculture_desc",
    "UZH_agriculture_pastures_tt",
    "uzh_pannonian_frontier_desc",
    "UZH_pannonian_compact_government_tt",
    "UZH_revival_komitat_condition_tt",
    "uzh_komitat_captains_party_tt",
    "uzh_komitat_system_desc",
    "UZH_pannonian_republic_foundation_tt",
    "UZH_pannonian_republic_reform_choice_tt",
    "UZH_federalization_authority_tt",
    "UZH_federative_statutes_reward_tt",
    "UZH_congress_subject_hegemony_subject_tt",
    "UZH_congress_border_bastion_subject_tt",
    "UZH_tisza_customs_pest_tt",
    "UZH_tisza_customs_downstream_tt",
    "UZH_rusin_nobility_court_tt",
    "UZH_pannonian_expansion_culture_tt",
    "UZH_identity_question_culture_tt",
    "uz_crown_of_saint_stephen_desc",
    "uz_rusin_state_title",
    "uz_rusin_state_desc",
    "uz_sovereign_rusin_state",
    "desc_uz_sovereign_rusin_state",
    "uzh.8.t",
    "uzh.8.d",
    "uzh.8.a",
    "uz_preserve_orthodox_faith_title",
    "uz_resist_habsburgs_title",
    "uzh_danube_trade_league_title",
    "uz_union_compromise_plus_title",
    "uz_identity_branching_1_title",
    "uz_identity_branching_2_title",
    "uz_identity_branching_3_title",
    "uz_orthodox_unity_title",
    "uz_crown_of_saint_stephen_title",
    "uz_zakarpattia_realm_title",
    "uzh_congress_subject_hegemony_title",
    "uzh_congress_border_bastion_title",
    "UZH_language_decree_timer_tt",
    "UZH_self_identification_timer_tt",
    "UZH_self_identification_provinces_tt",
    "UZH_solotvynska_camera_timer_tt",
    "UZH_pan_congress_carpathia_3_tt",
    "UZH_colonization_wave_req_tt",
    "UZH_hajduk_host_req_tt",
)


def loc_entries(path) -> dict[str, str]:
    return dict(
        re.findall(
            r'^ ([A-Za-z0-9_.\-]+):\d+ "(.*)"$',
            path.read_text(encoding="utf-8-sig"),
            re.M,
        )
    )


def main() -> int:
    missions = read("missions/Zakarpatta_Missions.txt")
    en = loc_entries(ROOT / "localisation/RIP_UZH_realm_l_english.yml")

    # 1. No numeric province-ID scope (<id> = { ... }) inside any provinces_to_highlight
    for pos, block in keyed_blocks(missions, "provinces_to_highlight"):
        norm = normalized(block)
        bad = re.search(r"\b\d+\s*=\s*\{", norm)
        assert not bad, f"Zakarpatta_Missions.txt:{line_number(missions, pos)} uses numeric scope {bad.group(0)} inside provinces_to_highlight"

    for name, pid in (
        ("uz_mukachevo_autonomy", "1952"),
        ("uz_national_revival", "1952"),
        ("uz_rusin_state", "1952"),
        ("uzh_srem_metropolis", "4173"),
        ("uz_crown_of_saint_stephen", "153"),
    ):
        hl = normalized(named_block(named_block(missions, name), "provinces_to_highlight"))
        assert f"province_id = {pid}" in hl, (name, pid)

    # 2. uzh_agriculture: never check farm_estate in 1952 (salt); only grain/livestock/wine
    agri = named_block(missions, "uzh_agriculture")
    agri_hl = normalized(named_block(agri, "provinces_to_highlight"))
    agri_trig = normalized(named_block(agri, "trigger"))
    assert "1952" not in agri_hl and "1952" not in agri_trig
    for block in (agri_hl, agri_trig):
        assert "trade_goods = grain" in block
        assert "trade_goods = livestock" in block
        assert "trade_goods = wine" in block
        assert "has_building = farm_estate" in block

    # 3. uzh_industrial_revolution: coal inside OR with non-DLC Carpathian manufactory fallback
    ind_trig = normalized(named_block(named_block(missions, "uzh_industrial_revolution"), "trigger"))
    assert "OR = { num_of_owned_provinces_with = { trade_goods = coal value = 1 }" in ind_trig
    assert "has_manufactory_trigger = yes value = 2" in ind_trig

    # 4. Eparchial theocracy path (UzhEparchyPath.txt) stays unblocked across Slots 1-5
    slot4_pot = normalized(named_block(named_block(missions, "UZH_missions_4"), "potential"))
    assert slot4_pot == "potential = { tag = UZH }", slot4_pot

    resist_trig = normalized(named_block(named_block(missions, "uz_resist_habsburgs"), "trigger"))
    assert "AND = { government = theocracy OR = { diplomatic_reputation = 2 devotion = 70 } }" in resist_trig

    komitat_eff = normalized(named_block(named_block(missions, "uzh_komitat_system"), "effect"))
    assert "else = { change_government_reform_progress = 35 }" in komitat_eff
    assert "set_country_flag = uzh_komitat_restructured" in komitat_eff

    palatial = named_block(missions, "uzh_palatial_reform")
    palatial_trig = normalized(named_block(palatial, "trigger"))
    palatial_eff = normalized(named_block(palatial, "effect"))
    assert "AND = { government = theocracy stability = 2 devotion = 70 num_of_cities = 8 }" in palatial_trig
    assert "else_if = { limit = { government = theocracy } add_devotion = 10 }" in palatial_eff
    assert "limit = { OR = { government = monarchy government = republic } }" in palatial_eff
    assert "else = { change_government_reform_progress = 50 }" in palatial_eff

    pannonian = named_block(missions, "uzh_pannonian_republic")
    pannonian_trig = normalized(named_block(pannonian, "trigger"))
    pannonian_eff_raw = named_block(pannonian, "effect")
    pannonian_eff = normalized(pannonian_eff_raw)
    assert "OR = { government = republic government = theocracy has_country_flag = uzh_constitutional_framework }" in pannonian_trig
    assert '"uz_pannonian_autonomy"' in pannonian_eff_raw and '"uz_carpathian_hegemony"' in pannonian_eff_raw
    assert "else = { add_country_modifier = { name = duration = 9125 } add_stability = 1 if = { limit = { has_estate = estate_church } add_estate_loyalty = { estate = estate_church loyalty = 10 } } set_country_flag = uzh_pannonian_charter_ratified }" in pannonian_eff

    danube_trig = normalized(named_block(named_block(missions, "uzh_danube_trade_league"), "trigger"))
    assert "has_country_flag = uzh_pannonian_charter_ratified" in danube_trig
    assert "has_country_flag = uzh_pannonian_compact_signed" in danube_trig

    bastion_eff = normalized(named_block(named_block(missions, "uzh_congress_border_bastion"), "effect"))
    assert "if = { limit = { government = theocracy } add_devotion = 10 }" in bastion_eff

    # 5. Localisation and replace fallbacks mirror all 5 updated strings
    for lang in ("french", "german", "spanish"):
        fallback = loc_entries(ROOT / f"localisation/replace/RIP_UZH_content_l_{lang}.yml")
        for key in SYNCED_LOC_KEYS:
            assert fallback.get(key) == en[key], (lang, key)

    print("PASS: UZH provinces_to_highlight, farm_estate, no-DLC coal fallback, and theocracy reachability contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
