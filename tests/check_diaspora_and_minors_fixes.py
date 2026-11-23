"""Static contracts for Ruthenian Diaspora & TR Russian Minors fixes.

Static only: checks source blocks, flags, triggers, mission coordinates,
modifiers, and English/fallback localisation parity; does not run EU4.
"""
from __future__ import annotations

import re
import sys

from clausewitz_testlib import keyed_blocks, matching_brace, named_block, read


diaspora_missions = read("missions/zzzz_RuthenianDiaspora_Missions.txt")
diaspora_decisions = read("decisions/RIP_RuthenianDiaspora.txt")
diaspora_events = read("events/RIP_shared_ruthenian_RuthenianDiaspora.txt")
diaspora_triggers = read("common/scripted_triggers/rip_diaspora_triggers.txt")
diaspora_effects = read("common/scripted_effects/rip_diaspora_effects.txt")
diaspora_modifiers = read("common/event_modifiers/RIP_diaspora_modifiers.txt")
minors_missions = read("missions/TR_Russian_Minors_Missions.txt")
minors_modifiers = read("common/event_modifiers/RIP_TR_minors_modifiers.txt")
dom_russia_missions = read("missions/DOM_Russia_Missions.txt")


def loc_entries(path: str) -> dict[str, str]:
    return dict(re.findall(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', read(path), re.M))


def top_level_events(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for match in re.finditer(r"(?m)^country_event\s*=\s*\{", text):
        body = text[match.start(): matching_brace(text, match.end() - 1) + 1]
        ident = re.search(r"\bid\s*=\s*([\w.]+)", body)
        assert ident, "country_event missing id"
        assert ident.group(1) not in out, f"duplicate event id {ident.group(1)}"
        out[ident.group(1)] = body
    return out


def check_diaspora_missions() -> None:
    for banned_year in ("is_year = 1750", "is_year = 1800"):
        assert banned_year not in diaspora_missions, f"{banned_year} still gates diaspora"
    for suffix in ("", "_kyiv"):
        root = named_block(diaspora_missions, f"rip_diaspora_root{suffix}")
        trigger = named_block(root, "trigger")
        or_block = named_block(trigger, "OR")
        for req in (
            "has_institution = global_trade",
            "current_age = age_of_absolutism",
            "current_age = age_of_revolutions",
        ):
            assert req in or_block, (suffix, req)
        circ = named_block(diaspora_missions, f"rip_lysianskyi_circumnavigation{suffix}")
        assert "rip_diaspora_can_commemorate_lysianskyi = yes" in named_block(circ, "trigger"), circ
        voyage = named_block(diaspora_triggers, "rip_diaspora_can_commemorate_lysianskyi")
        assert "is_year = 1806" in voyage and "has_country_flag = circumnavigation_done" in voyage
        final = named_block(diaspora_missions, f"rip_diaspora_of_rus{suffix}")
        assert "is_year" not in named_block(final, "trigger"), final


def check_diaspora_triggers_and_effects() -> None:
    for trig in (
        "rip_diaspora_colonial_convertible_culture_trigger",
        "rip_diaspora_colonial_convertible_faith_trigger",
        "rip_diaspora_mainland_convertible_culture_trigger",
        "rip_diaspora_mainland_convertible_faith_trigger",
    ):
        block = named_block(diaspora_triggers, trig)
        assert "NOT = { rip_diaspora_eligible_culture_province = yes }" in block, trig
        if "_faith_" in trig:
            assert "NOT = { religion = ROOT }" in block, trig

    for eff in (
        "rip_diaspora_convert_colonial_culture_effect",
        "rip_diaspora_convert_colonial_faith_effect",
        "rip_diaspora_convert_mainland_culture_effect",
        "rip_diaspora_convert_mainland_faith_effect",
    ):
        block = named_block(diaspora_effects, eff)
        rc = named_block(block, "random_country")
        rc_limit = named_block(rc, "limit")
        assert "NOT = { rip_diaspora_eligible_culture_province = yes }" in rc_limit, eff
        if "_faith_" in eff:
            assert "NOT = { religion = ROOT }" in rc_limit, eff


def check_diaspora_decisions() -> None:
    assert "else_if" not in diaspora_decisions, "if/else_if priority trap remains in diaspora decisions"
    assert "rip_diaspora_target_" not in diaspora_decisions, "legacy target flags remain in decisions"
    assert "rip_diaspora_settlers_cooldown" in diaspora_decisions
    assert "duration = 1825" not in diaspora_decisions

    expected = {
        "rip_diaspora_colonial_settlers": ("rip_diaspora_colonial_convertible_culture_trigger", "rip_diaspora.10"),
        "rip_diaspora_colonial_settlers_faith": ("rip_diaspora_colonial_convertible_faith_trigger", "rip_diaspora.11"),
        "rip_diaspora_mainland_settlers": ("rip_diaspora_mainland_convertible_culture_trigger", "rip_diaspora.12"),
        "rip_diaspora_mainland_settlers_faith": ("rip_diaspora_mainland_convertible_faith_trigger", "rip_diaspora.13"),
    }
    for dec_id, (trig_name, event_id) in expected.items():
        block = named_block(diaspora_decisions, dec_id)
        allow = named_block(block, "allow")
        effect = named_block(block, "effect")
        assert "NOT = { has_country_flag = rip_diaspora_choosing_settlers_flag }" in allow, dec_id
        assert trig_name in allow, (dec_id, trig_name)
        assert "set_country_flag = rip_diaspora_choosing_settlers_flag" in effect, dec_id
        assert f"id = {event_id}" in effect and "days =" not in effect, (dec_id, event_id)
        assert "add_country_modifier" not in effect and "add_stability" not in effect, dec_id
        if dec_id.endswith("_faith"):
            ai = named_block(block, "ai_will_do")
            assert "NOT = { stability = 0 }" in ai, dec_id


def check_diaspora_events() -> None:
    assert "rip_diaspora_target_" not in diaspora_events
    assert "duration = 1825" not in diaspora_events
    events = top_level_events(diaspora_events)
    assert set(events) == {
        "rip_diaspora.10", "rip_diaspora.11", "rip_diaspora.12",
        "rip_diaspora.13", "rip_diaspora.20", "rip_diaspora.21",
    }, sorted(events)

    settler_specs = {
        "rip_diaspora.10": (6, False, "rip_diaspora.10.g"),
        "rip_diaspora.11": (6, True, "rip_diaspora.11.g"),
        "rip_diaspora.12": (3, False, "rip_diaspora.12.c"),
        "rip_diaspora.13": (3, True, "rip_diaspora.13.c"),
    }
    for ev_id, (opt_count, is_faith, cancel_name) in settler_specs.items():
        ev = events[ev_id]
        assert "immediate = {" not in ev, ev_id
        after = named_block(ev, "after")
        assert "clr_country_flag = rip_diaspora_choosing_settlers_flag" in after, ev_id
        options = [b for _, b in keyed_blocks(ev, "option")]
        assert len(options) == opt_count, (ev_id, len(options))
        for opt in options[:-1]:
            assert "duration = 1095" in opt, (ev_id, opt)
            assert "_convertible_" in opt, (ev_id, opt)
            if is_faith:
                assert "add_stability = -1" in opt, (ev_id, opt)
            else:
                assert "add_stability" not in opt, (ev_id, opt)
        cancel = options[-1]
        assert f"name = {cancel_name}" in cancel, (ev_id, cancel)
        assert "trigger = {" not in cancel and "factor = 0" in cancel, (ev_id, cancel)
        assert "rip_diaspora_settlers_cooldown" not in cancel and "add_stability" not in cancel

    for ev_id, tag, region in (
        ("rip_diaspora.20", "ZLK", "manchuria_region"),
        ("rip_diaspora.21", "SRK", "central_asia_region"),
    ):
        ev = events[ev_id]
        assert "immediate = {" not in ev, f"{ev_id} must not pre-plant cores in immediate"
        options = [b for _, b in keyed_blocks(ev, "option")]
        assert len(options) == 3, (ev_id, len(options))
        opt_a, opt_b, opt_c = options
        assert f"add_core = {tag}" in opt_a and f"release = {tag}" in opt_a and f"vassalize = {tag}" in opt_a
        assert f"add_core = {tag}" in opt_b and f"release = {tag}" in opt_b and f"create_march = {tag}" in opt_b
        assert f"region = {region}" in opt_c
        assert "rip_diaspora_crown_frontier" in opt_c
        assert f"release = {tag}" not in opt_c and f"add_core = {tag}" not in opt_c

    named_block(diaspora_modifiers, "rip_diaspora_crown_frontier")


def check_russian_minors() -> None:
    expected_tags = {"OKA", "PSK", "RYA", "TVE", "YAR", "PRM", "BLO", "RSO", "NZH"}
    assert "add_permanent_claim" not in minors_missions, "TR Russian Minors must use temporary claims only"
    assert "PLT" not in minors_missions and "SMO" not in minors_missions, "PLT and SMO stay excluded"

    cells: set[tuple[int, int]] = set()
    mission_ids: list[str] = []
    for series_idx in range(1, 6):
        series = named_block(minors_missions, f"tr_russian_minors_{series_idx}")
        slot = int(re.search(r"\bslot\s*=\s*(\d+)", series).group(1))
        potential = named_block(series, "potential")
        tags = set(re.findall(r"\btag\s*=\s*(\w+)", potential))
        assert tags == expected_tags, (series_idx, tags)
        for m_id, m_body in keyed_blocks(series, r"[a-z0-9_]+"):
            pass
        for match in re.finditer(r"(?m)^\t([a-z0-9_]+)\s*=\s*\{", series):
            ident = match.group(1)
            if ident in ("potential", "potential_on_load", "ai_weight"):
                continue
            body = series[match.start(): matching_brace(series, match.end() - 1) + 1]
            pos_match = re.search(r"\bposition\s*=\s*(\d+)", body)
            assert pos_match, f"{ident} missing explicit position"
            cell = (slot, int(pos_match.group(1)))
            assert cell not in cells, f"duplicate coordinate {cell} for {ident}"
            cells.add(cell)
            mission_ids.append(ident)

    assert len(mission_ids) == 15 and len(cells) == 15, (len(mission_ids), cells)
    assert set(mission_ids) == {
        "tr_conquer_mos", "tr_independence", "tr_conquer_russia", "tr_rip_volga_marches",
        "tr_tatar_yoke", "tr_conquer_nov", "tr_cossacks", "tr_rip_gather_rus",
        "tr_stability", "tr_rip_frontier_marches", "tr_dniepr", "tr_ruthenia",
        "tr_rip_princely_domains", "tr_kiev", "tr_rip_ruthenian_charters",
    }

    stability = named_block(minors_missions, "tr_stability")
    stability_effect = named_block(stability, "effect")
    assert "east_dniepr_area" not in stability_effect
    assert "capital_scope = {" in stability_effect and "add_claim = ROOT" in stability_effect

    frontier = named_block(minors_missions, "tr_rip_frontier_marches")
    assert "required_missions = { tr_stability }" in frontier
    assert "position = 2" in frontier
    assert "tr_rip_frontier_mobilization" in frontier

    dniepr = named_block(minors_missions, "tr_dniepr")
    assert "required_missions = { tr_rip_frontier_marches }" in dniepr
    assert "position = 3" in dniepr

    domains = named_block(minors_missions, "tr_rip_princely_domains")
    assert "required_missions = { tr_stability }" in domains
    assert "position = 2" in domains
    assert "tr_rip_princely_charter" in domains

    charters = named_block(minors_missions, "tr_rip_ruthenian_charters")
    assert "required_missions = { tr_kiev }" in charters and "position = 5" in charters
    assert "slot = 5" in named_block(minors_missions, "tr_russian_minors_5")
    assert "add_accepted_culture = ruthenian" in charters and "tr_rip_ruthenian_charters" in named_block(
        charters, "effect")
    assert (5, 5) in cells

    volga = named_block(minors_missions, "tr_rip_volga_marches")
    assert "required_missions = { tr_conquer_russia }" in volga
    assert "position = 4" in volga
    assert "tr_rip_steppe_vanguard" in volga

    tatar = named_block(minors_missions, "tr_tatar_yoke")
    assert "required_missions = { tr_rip_volga_marches tr_cossacks }" in tatar

    gather = named_block(minors_missions, "tr_rip_gather_rus")
    assert "required_missions = { tr_tatar_yoke tr_ruthenia }" in gather
    assert "position = 6" in gather
    assert "tr_rip_sovereign_of_all_rus" in gather

    for mod in (
        "tr_rip_frontier_mobilization",
        "tr_rip_princely_charter",
        "tr_rip_steppe_vanguard",
        "tr_rip_sovereign_of_all_rus",
        "tr_rip_ruthenian_charters",
    ):
        named_block(minors_modifiers, mod)


def check_localisation() -> None:
    exp_en = loc_entries("localisation/RIP_shared_ruthenian_expeditions_l_english.yml")
    exp_keys = [
        "rip_diaspora_root_desc",
        "rip_lysianskyi_circumnavigation_desc",
        "rip_dec_settlers_colonial_100_tt", "rip_dec_settlers_colonial_140_tt",
        "rip_dec_settlers_mainland_100_tt", "rip_dec_settlers_mainland_140_tt",
        "rip_diaspora_colonial_settlers_desc", "rip_diaspora_colonial_settlers_faith_desc",
        "rip_diaspora_mainland_settlers_desc", "rip_diaspora_mainland_settlers_faith_desc",
        "rip_diaspora.10.t", "rip_diaspora.10.d", "rip_diaspora.10.a", "rip_diaspora.10.b",
        "rip_diaspora.10.c", "rip_diaspora.10.e", "rip_diaspora.10.f", "rip_diaspora.10.g",
        "rip_diaspora.11.t", "rip_diaspora.11.d", "rip_diaspora.11.a", "rip_diaspora.11.b",
        "rip_diaspora.11.c", "rip_diaspora.11.e", "rip_diaspora.11.f", "rip_diaspora.11.g",
        "rip_diaspora.12.t", "rip_diaspora.12.d", "rip_diaspora.12.a", "rip_diaspora.12.b", "rip_diaspora.12.c",
        "rip_diaspora.13.t", "rip_diaspora.13.d", "rip_diaspora.13.a", "rip_diaspora.13.b", "rip_diaspora.13.c",
        "rip_diaspora.20.b", "rip_diaspora.20.c",
        "rip_diaspora.21.b", "rip_diaspora.21.c",
        "rip_diaspora_crown_frontier", "desc_rip_diaspora_crown_frontier",
    ]
    for key in exp_keys:
        assert exp_en.get(key), f"missing {key} in expeditions english"
    assert "From 1750" not in exp_en["rip_diaspora_root_desc"]
    assert "From 1806" in exp_en["rip_lysianskyi_circumnavigation_desc"]
    assert "three-year" in exp_en["rip_diaspora_colonial_settlers_desc"]
    for lang in ("french", "german", "spanish"):
        fb = loc_entries(f"localisation/replace/RIP_shared_ruthenian_content_l_{lang}.yml")
        for key in exp_keys:
            assert fb.get(key) == exp_en[key], (lang, key)

    mos_en = loc_entries("localisation/RIP_MOS_RUS_realm_l_english.yml")
    mos_keys = [
        "tr_rip_frontier_marches_title", "tr_rip_frontier_marches_desc",
        "tr_rip_princely_domains_title", "tr_rip_princely_domains_desc",
        "tr_rip_volga_marches_title", "tr_rip_volga_marches_desc",
        "tr_rip_gather_rus_title", "tr_rip_gather_rus_desc",
        "tr_rip_frontier_mobilization", "desc_tr_rip_frontier_mobilization",
        "tr_rip_princely_charter", "desc_tr_rip_princely_charter",
        "tr_rip_steppe_vanguard", "desc_tr_rip_steppe_vanguard",
        "tr_rip_sovereign_of_all_rus", "desc_tr_rip_sovereign_of_all_rus",
    ]
    for key in mos_keys:
        assert mos_en.get(key), f"missing {key} in MOS_RUS english"
    for lang in ("french", "german", "spanish"):
        fb = loc_entries(f"localisation/replace/RIP_MOS_RUS_content_l_{lang}.yml")
        for key in mos_keys:
            assert fb.get(key) == mos_en[key], (lang, key)


def check_dom_russia_compat() -> None:
    patriarchate = named_block(dom_russia_missions, "mos_rus_russian_patriarchate")
    for sub in ("provinces_to_highlight", "trigger", "effect"):
        block = named_block(patriarchate, sub)
        assert "rip_faith_is_eastern_orthodox = yes" in block, sub
        assert "religion = orthodox" not in block, sub

    sudebnik = named_block(dom_russia_missions, "rus_enact_the_sudebnik")
    sudebnik_trigger = named_block(sudebnik, "trigger")
    assert "NOT = { rip_diaspora_eligible_culture = yes }" in sudebnik_trigger
    assert "primary_culture = ruthenian" not in sudebnik_trigger
    assert "primary_culture = ruthenian_new" not in sudebnik_trigger


def planted(label: str, mutate, check) -> None:
    global diaspora_missions, diaspora_decisions, diaspora_events, minors_missions, dom_russia_missions
    saved = (diaspora_missions, diaspora_decisions, diaspora_events, minors_missions, dom_russia_missions)
    try:
        mutate()
        check()
    except AssertionError:
        return
    finally:
        diaspora_missions, diaspora_decisions, diaspora_events, minors_missions, dom_russia_missions = saved
    raise SystemExit(f"planted regression not caught: {label}")


def main() -> int:
    check_diaspora_missions()
    check_diaspora_triggers_and_effects()
    check_diaspora_decisions()
    check_diaspora_events()
    check_russian_minors()
    check_localisation()
    check_dom_russia_compat()

    def readd_1800() -> None:
        global diaspora_missions
        diaspora_missions = diaspora_missions.replace("has_institution = global_trade", "is_year = 1800", 1)

    def readd_else_if() -> None:
        global diaspora_decisions
        diaspora_decisions += "\n# else_if"

    def readd_zlk_immediate() -> None:
        global diaspora_events
        diaspora_events = diaspora_events.replace(
            "id = rip_diaspora.20",
            "id = rip_diaspora.20\n\timmediate = { 1 = { add_core = ZLK } }",
            1,
        )

    def revert_dniepr_req() -> None:
        global minors_missions
        minors_missions = minors_missions.replace(
            "required_missions = { tr_rip_frontier_marches }",
            "required_missions = { tr_stability }",
            1,
        )

    def readd_perm_claim() -> None:
        global minors_missions
        minors_missions = minors_missions.replace("add_claim = ROOT", "add_permanent_claim = ROOT", 1)

    def revert_patriarchate_orth() -> None:
        global dom_russia_missions
        pat = named_block(dom_russia_missions, "mos_rus_russian_patriarchate")
        eff = named_block(pat, "effect")
        mutated_eff = eff.replace("rip_faith_is_eastern_orthodox = yes", "religion = orthodox", 1)
        dom_russia_missions = dom_russia_missions.replace(eff, mutated_eff, 1)

    def revert_sudebnik_culture() -> None:
        global dom_russia_missions
        dom_russia_missions = dom_russia_missions.replace(
            "NOT = { rip_diaspora_eligible_culture = yes }",
            "NOT = { primary_culture = ruthenian }\n\t\t\t\t\tNOT = { primary_culture = ruthenian_new }",
            1,
        )

    planted("1800 time gate returns", readd_1800, check_diaspora_missions)
    planted("else_if priority trap returns", readd_else_if, check_diaspora_decisions)
    planted("ZLK pre-cores in immediate", readd_zlk_immediate, check_diaspora_events)
    planted("tr_dniepr bypasses tr_rip_frontier_marches", revert_dniepr_req, check_russian_minors)
    planted("add_permanent_claim leaks into TR Russian Minors", readd_perm_claim, check_russian_minors)
    planted("mos_rus_russian_patriarchate drops russian_orthodox", revert_patriarchate_orth, check_dom_russia_compat)
    planted("rus_enact_the_sudebnik reverts to narrow ruthenian check", revert_sudebnik_culture, check_dom_russia_compat)

    print("PASS: Diaspora time-gate/region-choice/ZLK-SRK and TR Russian Minors fixes (static + planted checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
