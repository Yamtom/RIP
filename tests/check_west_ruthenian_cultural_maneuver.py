"""Verification suite for the West-Ruthenian and West-Slavic cultural maneuver."""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def extract_brace_block(text: str, key: str, start: int = 0) -> tuple[str, int] | None:
    """Return the content inside the outermost braces following `key = {`."""
    pattern = re.compile(rf"(?<![\w.]){re.escape(key)}\s*=\s*\{{")
    match = pattern.search(text, start)
    if not match:
        return None
    brace_start = match.end() - 1
    depth = 0
    in_quotes = False
    i = brace_start
    while i < len(text):
        ch = text[i]
        if ch == '"' and (i == 0 or text[i - 1] != "\\"):
            in_quotes = not in_quotes
        elif not in_quotes:
            if ch == "#":
                newline = text.find("\n", i)
                if newline == -1:
                    break
                i = newline
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[brace_start + 1 : i], i + 1
        i += 1
    raise AssertionError(f"Unclosed brace block for {key}")


def extract_events(text: str) -> dict[str, str]:
    """Map event id -> full country_event body."""
    events: dict[str, str] = {}
    pos = 0
    while True:
        found = extract_brace_block(text, "country_event", pos)
        if not found:
            break
        body, next_pos = found
        pos = next_pos
        id_match = re.search(r"^\s*id\s*=\s*([a-zA-Z0-9_.]+)", body, re.MULTILINE)
        if id_match:
            events[id_match.group(1)] = body
    return events


def parse_random_list_branches(rl_body: str) -> list[tuple[float, str]]:
    """Return top-level `(weight, body)` pairs inside a `random_list = { ... }` block."""
    branches: list[tuple[float, str]] = []
    i = 0
    n = len(rl_body)
    while i < n:
        while i < n and rl_body[i].isspace():
            i += 1
        if i >= n:
            break
        if rl_body[i] == "#":
            nl = rl_body.find("\n", i)
            i = n if nl == -1 else nl + 1
            continue
        m = re.match(r"([0-9]+(?:\.[0-9]+)?)\s*=\s*\{", rl_body[i:])
        if not m:
            i += 1
            continue
        weight = float(m.group(1))
        brace_idx = i + m.end() - 1
        depth = 0
        j = brace_idx
        while j < n:
            if rl_body[j] == "#":
                nl = rl_body.find("\n", j)
                j = n if nl == -1 else nl + 1
                continue
            if rl_body[j] == "{":
                depth += 1
            elif rl_body[j] == "}":
                depth -= 1
                if depth == 0:
                    branches.append((weight, rl_body[brace_idx + 1 : j]))
                    i = j + 1
                    break
            j += 1
        else:
            raise AssertionError("Unclosed branch in random_list")
    return branches


def check_cultures_and_starts() -> None:
    cultures_path = ROOT / "common" / "cultures" / "00_cultures.txt"
    raw = cultures_path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "00_cultures.txt must not have a UTF-8 BOM"
    text = raw.decode("cp1252")

    east_block = extract_brace_block(text, "east_slavic")
    slavic_block = extract_brace_block(text, "slavic")
    west_ruthenian_block = extract_brace_block(text, "west_ruthenian")
    west_slavic_block = extract_brace_block(text, "west_slavic")
    assert east_block and slavic_block and west_ruthenian_block and west_slavic_block

    east_body = east_block[0]
    slavic_body = slavic_block[0]
    wr_body = west_ruthenian_block[0]
    ws_body = west_slavic_block[0]

    for c in ("byelorussian", "rusyn", "ruthenian", "ryazanian"):
        assert re.search(rf"^\t{c}\s*=\s*\{{", east_body, re.MULTILINE), f"{c} missing from east_slavic"
    for c in ("byelorussian_new", "rusyn_new", "ruthenian_new", "ryazanian_new"):
        assert re.search(rf"^\t{c}\s*=\s*\{{", slavic_body, re.MULTILINE), f"{c} missing from slavic"

    for c in ("byelorussian_west_ruthenian", "ruthenian_west_ruthenian", "rusyn_west_ruthenian"):
        assert re.search(rf"^\t{c}\s*=\s*\{{", wr_body, re.MULTILINE), f"{c} missing from west_ruthenian"
    rut_wr = extract_brace_block(wr_body, "ruthenian_west_ruthenian")
    assert rut_wr and "primary = KIE" in rut_wr[0], "ruthenian_west_ruthenian must preserve primary = KIE"

    for c in ("byelorussian_west_slavic", "ruthenian_west_slavic", "rusyn_west_slavic"):
        assert re.search(rf"^\t{c}\s*=\s*\{{", ws_body, re.MULTILINE), f"{c} missing from west_slavic"
    rut_ws = extract_brace_block(ws_body, "ruthenian_west_slavic")
    assert rut_ws and "primary = KIE" in rut_ws[0], "ruthenian_west_slavic must preserve primary = KIE"

    # Verify 1444 country/province starts keep original east_slavic cultures
    for tag_prefix in ("BLR", "MSK", "MSL", "SMO", "VTB"):
        country_text = next((ROOT / "history" / "countries").glob(f"{tag_prefix}*")).read_text(
            encoding="utf-8", errors="ignore"
        )
        assert re.search(
            r"primary_culture\s*=\s*byelorussian\b", country_text
        ), f"{tag_prefix} 1444 must keep primary_culture = byelorussian"
    for tag_prefix in ("CHR", "HLC", "KIE", "PDL", "VOL"):
        country_text = next((ROOT / "history" / "countries").glob(f"{tag_prefix}*")).read_text(
            encoding="utf-8", errors="ignore"
        )
        assert re.search(
            r"primary_culture\s*=\s*ruthenian\b", country_text
        ), f"{tag_prefix} 1444 must keep primary_culture = ruthenian"
    uzh = next((ROOT / "history" / "countries").glob("UZH*")).read_text(encoding="utf-8", errors="ignore")
    assert re.search(r"primary_culture\s*=\s*rusyn\b", uzh), "UZH 1444 must keep primary_culture = rusyn"

    for hist_file in (ROOT / "history").rglob("*.txt"):
        ht = hist_file.read_text(encoding="utf-8", errors="ignore")
        for new_c in (
            "byelorussian_west_ruthenian",
            "ruthenian_west_ruthenian",
            "rusyn_west_ruthenian",
            "byelorussian_west_slavic",
            "ruthenian_west_slavic",
            "rusyn_west_slavic",
        ):
            assert new_c not in ht, f"1444/history file {hist_file} must not pre-assign {new_c}"


def check_province_names_and_compatibility() -> None:
    pn_dir = ROOT / "common" / "province_names"
    for target, base in (
        ("byelorussian_west_ruthenian.txt", "byelorussian.txt"),
        ("byelorussian_west_slavic.txt", "byelorussian.txt"),
        ("ruthenian_west_ruthenian.txt", "ruthenian.txt"),
        ("ruthenian_west_slavic.txt", "ruthenian.txt"),
        ("rusyn_west_ruthenian.txt", "rusyn.txt"),
        ("rusyn_west_slavic.txt", "rusyn.txt"),
    ):
        t_bytes = (pn_dir / target).read_bytes()
        b_bytes = (pn_dir / base).read_bytes()
        assert not t_bytes.startswith(b"\xef\xbb\xbf"), f"{target} must not contain BOM"
        assert t_bytes == b_bytes, f"{target} must mirror {base}"

    # Hadiach mission & event layout registration
    plc_missions = (ROOT / "missions" / "Poland_Commonwealth_Rework.txt").read_text(encoding="utf-8")
    assert plc_missions.count("rusyn_west_ruthenian") >= 2
    assert plc_missions.count("rusyn_west_slavic") >= 2
    assert plc_missions.count("ruthenian_west_ruthenian") >= 2
    assert plc_missions.count("ruthenian_west_slavic") >= 2

    event_layout = (ROOT / "tools" / "event_layout.py").read_text(encoding="utf-8")
    assert "CulturalManeuver" in event_layout

    # Compatibility references across key subsystems
    for rel_path, needle in (
        ("tools/data/rip_colonial_names.json", "byelorussian_west_ruthenian"),
        ("tools/data/rip_colonial_names.json", "ruthenian_west_slavic"),
        ("tools/build_parliament_names.py", "rusyn_west_slavic"),
        ("tools/build_parliament_names.py", "ruthenian_west_ruthenian"),
        ("decisions/GreekCatholicDecisions.txt", "rusyn_west_ruthenian"),
        ("decisions/GreekCatholicDecisions.txt", "ruthenian_west_slavic"),
        ("decisions/PolesianBelarusianNations.txt", "byelorussian_west_slavic"),
        ("decisions/RuthenianNation.txt", "ruthenian_west_ruthenian"),
        ("decisions/KuyabaNation.txt", "ruthenian_west_slavic"),
        ("decisions/CossackHostDecisions.txt", "ruthenian_west_ruthenian"),
        ("decisions/Podillia_Decisions.txt", "ruthenian_west_ruthenian"),
        ("common/ideas/zzz_RIP_group_ideas.txt", "byelorussian_west_ruthenian"),
        ("common/ideas/zzz_RIP_group_ideas.txt", "ruthenian_west_ruthenian"),
        ("common/estates/01_church.txt", "west_ruthenian"),
        ("common/estates/02_nobility.txt", "west_ruthenian"),
        ("common/estates/03_burghers.txt", "rusyn_west_ruthenian"),
        ("common/estates/03_burghers.txt", "ruthenian_west_slavic"),
        ("common/estates/04_cossacks.txt", "west_ruthenian"),
        ("common/scripted_triggers/rip_church_gui_generated.txt", "byelorussian_west_slavic"),
        ("common/scripted_triggers/rip_church_gui_generated.txt", "ruthenian_west_ruthenian"),
        ("common/scripted_triggers/kru_ruthenian_reform_triggers.txt", "ruthenian_west_slavic"),
        ("common/great_projects/RIP_UZH_great_projects.txt", "ruthenian_west_ruthenian"),
        ("common/great_projects/RIP_ZAZ_great_projects.txt", "ruthenian_west_slavic"),
        ("missions/Kyiv_Successors_Missions.txt", "ruthenian_west_ruthenian"),
        ("missions/Ruthenian_Missions.txt", "ruthenian_west_slavic"),
        ("customizable_localization/RIP_UZH_identity.txt", "rusyn_west_ruthenian"),
        ("customizable_localization/RIP_UZH_identity.txt", "rusyn_west_slavic"),
        ("customizable_localization/RIP_UZH_identity.txt", "ruthenian_west_ruthenian"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_byelorussian_stake"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_ruthenian_stake"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_rusyn_stake"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_byelorussian_from_sphere"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_ruthenian_from_sphere"),
        ("common/scripted_triggers/rip_west_ruthenian_triggers.txt", "wr_is_pure_rusyn_from_sphere"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_byelorussian_stake"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_ruthenian_stake"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_rusyn_stake"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_byelorussian_from_sphere"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_ruthenian_from_sphere"),
        ("events/RIP_shared_west_ruthenian_CulturalManeuver.txt", "wr_is_pure_rusyn_from_sphere"),
    ):
        content = (ROOT / rel_path).read_text(encoding="utf-8")
        assert needle in content, f"{rel_path} missing compatibility reference {needle}"


def check_probabilities_and_triggers() -> None:
    triggers_text = (ROOT / "common" / "scripted_triggers" / "rip_west_ruthenian_triggers.txt").read_text(
        encoding="utf-8"
    )
    effects_text = (ROOT / "common" / "scripted_effects" / "rip_west_ruthenian_effects.txt").read_text(
        encoding="utf-8"
    )
    events_text = (ROOT / "events" / "RIP_shared_west_ruthenian_CulturalManeuver.txt").read_text(
        encoding="utf-8"
    )
    decisions_text = (ROOT / "decisions" / "WestRuthenianManeuverDecisions.txt").read_text(encoding="utf-8")

    # Moscow / Russia exclusion and Stage 2 / 4 rusyn_new_new preservation
    base_trig = extract_brace_block(triggers_text, "wr_can_run_maneuver_base")
    assert base_trig is not None
    for tok in ("NOT = { tag = MOS }", "NOT = { tag = RUS }", "NOT = { primary_culture = russian }"):
        assert tok in base_trig[0], f"Missing exclusion in wr_can_run_maneuver_base: {tok}"

    rusyn_country_trig = extract_brace_block(triggers_text, "wr_is_rusyn_country")
    rusyn_prov_trig = extract_brace_block(triggers_text, "wr_is_rusyn_province")
    assert rusyn_country_trig and "rusyn_new_new" not in rusyn_country_trig[0]
    assert rusyn_prov_trig and "rusyn_new_new" not in rusyn_prov_trig[0]

    wr_conv = extract_brace_block(effects_text, "wr_convert_country_to_west_ruthenian_effect")
    ws_conv = extract_brace_block(effects_text, "wr_convert_country_to_west_slavic_effect")
    assert wr_conv and ws_conv
    assert "rusyn_new_new" not in wr_conv[0], "wr_convert_country_to_west_ruthenian_effect must not touch rusyn_new_new"
    assert "rusyn_new_new" not in ws_conv[0], "wr_convert_country_to_west_slavic_effect must not touch rusyn_new_new"

    # Progression graph: Branch A (1 -> 2) and parallel Branch B (3 -> 4)
    pot1 = extract_brace_block(triggers_text, "wr_potential_stage1")
    all1 = extract_brace_block(triggers_text, "wr_allow_stage1")
    pot2 = extract_brace_block(triggers_text, "wr_potential_stage2")
    all2 = extract_brace_block(triggers_text, "wr_allow_stage2")
    pot3 = extract_brace_block(triggers_text, "wr_potential_stage3")
    all3 = extract_brace_block(triggers_text, "wr_allow_stage3")
    pot4 = extract_brace_block(triggers_text, "wr_potential_stage4")
    all4 = extract_brace_block(triggers_text, "wr_allow_stage4")
    assert all((pot1, all1, pot2, all2, pot3, all3, pot4, all4))

    # Stage 1 -> Stage 2 strict prerequisite
    assert "has_country_flag = wr_distinctiveness_recognized" in pot2[0]
    assert "flag = wr_distinctiveness_recognized" in all2[0] and "days = 5475" in all2[0]

    # Stage 3 is parallel to Stages 1 and 2 (must NOT depend positively on Stage 1 or Stage 2, and strictly excludes them)
    for branch_a_flag in ("wr_distinctiveness_recognized", "wr_west_ruthenian_group_formed"):
        stripped_pot3 = re.sub(rf"NOT\s*=\s*\{{\s*has_country_flag\s*=\s*{branch_a_flag}\s*\}}", "", pot3[0])
        stripped_all3 = re.sub(rf"NOT\s*=\s*\{{\s*has_country_flag\s*=\s*{branch_a_flag}\s*\}}", "", all3[0])
        assert branch_a_flag not in stripped_pot3, f"Stage 3 potential must stay parallel and not require {branch_a_flag}"
        assert branch_a_flag not in stripped_all3, f"Stage 3 allow must stay parallel and not require {branch_a_flag}"

    # Stage 3 -> Stage 4 strict prerequisite
    assert "has_country_flag = wr_west_slavic_affinity_active" in pot4[0]
    assert "flag = wr_west_slavic_affinity_active" in all4[0] and "days = 10950" in all4[0]

    # High potential / allow thresholds, Circle 3 exclusion from Stages 2/4, and collective mandates
    assert "is_year = 1515" in pot1[0] and "wr_has_patron_only_potential = yes" in pot1[0]
    assert "adm_tech = 9" in all1[0] and "prestige = 20" in all1[0] and "legitimacy_equivalent = 80" in all1[0]
    assert "wr_has_primary_or_accepted_potential = yes" in pot2[0]
    assert "wr_has_patron_only_potential" not in pot2[0], "Circle 3 must not see Stage 2"
    assert "adm_tech = 12" in all2[0] and "has_institution = printing_press" in all2[0] and "stability = 2" in all2[0]
    for cult in ("byelorussian", "ruthenian", "rusyn"):
        assert f"wr_has_{cult}_collective_mandate_stage2 = yes" in all2[0], f"Missing Stage 2 mandate for {cult}"
        assert f"wr_{cult}_stage2_index_met = yes" in all2[0], f"Missing Stage 2 index check for {cult}"
        assert f"wr_has_{cult}_collective_mandate_stage4 = yes" in all4[0], f"Missing Stage 4 mandate for {cult}"
        assert f"wr_{cult}_stage4_index_met = yes" in all4[0], f"Missing Stage 4 index check for {cult}"

    # Mutual exclusion between Branch A (Stages 1->2) and Branch B (Stages 3->4)
    assert "NOT = { has_country_flag = wr_west_slavic_affinity_active }" in pot1[0]
    assert "NOT = { has_country_flag = wr_west_slavic_shift_completed }" in pot1[0]
    assert "NOT = { has_country_flag = wr_distinctiveness_recognized }" in pot3[0]
    assert "NOT = { has_country_flag = wr_west_ruthenian_group_formed }" in pot3[0]
    assert "NOT = { has_country_flag = wr_distinctiveness_recognized }" in all3[0]
    assert "NOT = { has_country_flag = wr_west_ruthenian_group_formed }" in all3[0]

    prov_s1 = extract_brace_block(effects_text, "wr_apply_stage1_charter_to_province_effect")
    prov_s3 = extract_brace_block(effects_text, "wr_apply_stage3_affinity_to_province_effect")
    assert prov_s1 and "remove_province_modifier = wr_west_slavic_shared_script_space" in prov_s1[0]
    assert prov_s3 and "remove_province_modifier = wr_chancery_prosta_mova_tradition" in prov_s3[0]

    recalc = extract_brace_block(effects_text, "wr_recalculate_maneuver_indices_effect")
    assert recalc is not None
    for cult in ("byelorussian", "ruthenian", "rusyn"):
        assert f"wr_{cult}_total" in recalc[0]
        assert f"wr_{cult}_s1_pct" in recalc[0]
        assert f"wr_{cult}_s3_pct" in recalc[0]
        s2_idx = extract_brace_block(triggers_text, f"wr_{cult}_stage2_index_met")
        s4_idx = extract_brace_block(triggers_text, f"wr_{cult}_stage4_index_met")
        assert s2_idx and f"wr_{cult}_s1_pct" in s2_idx[0] and "value = 60" in s2_idx[0]
        assert s4_idx and f"wr_{cult}_s3_pct" in s4_idx[0] and "value = 85" in s4_idx[0]
        assert f"wr_{cult}_stage2_index_met = yes" in wr_conv[0], (
            f"wr_convert_country_to_west_ruthenian_effect must gate {cult} by its index"
        )
        assert f"wr_{cult}_stage4_index_met = yes" in ws_conv[0], (
            f"wr_convert_country_to_west_slavic_effect must gate {cult} by its index"
        )

    assert "is_year = 1545" in pot3[0] and "wr_has_strong_west_slavic_bridge = yes" in pot3[0]
    assert "wr_has_patron_only_potential = yes" in pot3[0]
    assert "adm_tech = 11" in all3[0] and "has_institution = printing_press" in all3[0] and "diplomatic_reputation = 2" in all3[0]

    assert "is_year = 1615" in pot4[0] and "wr_has_strong_west_slavic_bridge = yes" in pot4[0]
    assert "wr_has_primary_or_accepted_potential = yes" in pot4[0]
    assert "wr_has_patron_only_potential" not in pot4[0], "Circle 3 must not see Stage 4"
    for req4 in (
        "adm_tech = 17",
        "has_institution = global_trade",
        "prestige = 50",
        "legitimacy_equivalent = 90",
        "has_building = university",
        "has_building = town_hall",
    ):
        assert req4 in all4[0], f"Missing Stage 4 allow requirement: {req4}"

    # Three-circle interaction definitions and dispatchers
    for circ_trig in (
        "wr_is_byelorussian_country",
        "wr_is_ruthenian_country",
        "wr_is_rusyn_country",
        "wr_has_accepted_byelorussian",
        "wr_has_accepted_ruthenian",
        "wr_has_accepted_rusyn",
        "wr_has_unaccepted_byelorussian_provinces",
        "wr_has_unaccepted_ruthenian_provinces",
        "wr_has_unaccepted_rusyn_provinces",
    ):
        assert extract_brace_block(triggers_text, circ_trig) is not None, f"Missing three-circle trigger {circ_trig}"

    for disp_eff in (
        "wr_dispatch_three_circle_congress_stage1_effect",
        "wr_dispatch_three_circle_congress_stage2_effect",
        "wr_dispatch_three_circle_congress_stage3_effect",
        "wr_dispatch_three_circle_congress_stage4_effect",
        "wr_sync_circle1_stage2_with_from_effect",
        "wr_sync_circle1_stage4_with_from_effect",
        "wr_sync_circle2_stage2_with_from_effect",
        "wr_sync_circle2_stage4_with_from_effect",
        "wr_sync_circle3_stage2_with_from_effect",
        "wr_sync_circle3_stage4_with_from_effect",
    ):
        assert extract_brace_block(effects_text, disp_eff) is not None, f"Missing collective effect {disp_eff}"

    # Stage 1-4 events & probability invariants (26 total including 3-circle congress events)
    events = extract_events(events_text)
    expected_ids = {
        f"wr_cultural_maneuver.{n}"
        for n in (
            1, 2, 3,
            10, 11, 12, 15,
            20, 21, 22,
            30, 31, 32, 35,
            41, 42, 43, 44,
            51, 52, 53, 54,
            61, 62, 63, 64,
        )
    }
    assert set(events.keys()) == expected_ids, f"Unexpected event IDs: {set(events.keys()) ^ expected_ids}"

    # Verify one-shot flags on entry events and is_triggered_only on outcome/congress events
    entry_map = {
        "wr_cultural_maneuver.1": ("wr_eligible_stage1", "wr_potential_stage1", "wr_allow_stage1", "wr_stage1_attempted"),
        "wr_cultural_maneuver.10": ("wr_eligible_stage2", "wr_potential_stage2", "wr_allow_stage2", "wr_stage2_attempted"),
        "wr_cultural_maneuver.20": ("wr_eligible_stage3", "wr_potential_stage3", "wr_allow_stage3", "wr_stage3_attempted"),
        "wr_cultural_maneuver.30": ("wr_eligible_stage4", "wr_potential_stage4", "wr_allow_stage4", "wr_stage4_attempted"),
    }
    for eid, (elig, pot, allow, flag) in entry_map.items():
        body = events[eid]
        assert elig in body, f"{eid} must check {elig}"
        imm = extract_brace_block(body, "immediate")
        assert imm and f"set_country_flag = {flag}" in imm[0], f"{eid} must set {flag} in immediate"
        elig_block = extract_brace_block(triggers_text, elig)
        pot_block = extract_brace_block(triggers_text, pot)
        assert elig_block and f"{pot} = yes" in elig_block[0] and f"{allow} = yes" in elig_block[0]
        assert pot_block and f"NOT = {{ has_country_flag = {flag} }}" in pot_block[0]

    for eid in expected_ids - set(entry_map.keys()):
        body = events[eid]
        assert "is_triggered_only = yes" in body, f"{eid} must have is_triggered_only = yes"
        assert (eid in events_text.replace(f"id = {eid}", "", 1)) or (
            eid in effects_text
        ), f"Sub-event {eid} must be invoked by script"

    # Helper to compute max random_list probability of branch containing `target_token`
    def max_rl_prob(event_body: str, success_token: str) -> float:
        rl = extract_brace_block(event_body, "random_list")
        assert rl is not None, f"Missing random_list in event"
        branches = parse_random_list_branches(rl[0])
        assert len(branches) >= 2
        succ_max = 0.0
        fail_min = 0.0
        for weight, b_body in branches:
            factors = [float(x) for x in re.findall(r"factor\s*=\s*([0-9]+(?:\.[0-9]+)?)", b_body)]
            if success_token in b_body:
                mult = 1.0
                for f in factors:
                    if f > 1.0:
                        mult *= f
                succ_max += weight * mult
            else:
                mult = 1.0
                for f in factors:
                    if f < 1.0:
                        mult *= f
                fail_min += weight * mult
        assert succ_max > 0 and fail_min > 0
        return succ_max / (succ_max + fail_min)

    def ai_trial_share(event_body: str, option_suffix: str) -> float:
        pos = 0
        opt_factors: dict[str, float] = {}
        while True:
            ob = extract_brace_block(event_body, "option", pos)
            if not ob:
                break
            o_body, pos = ob
            name_m = re.search(r"name\s*=\s*([a-zA-Z0-9_.]+)", o_body)
            ai_b = extract_brace_block(o_body, "ai_chance")
            if name_m and ai_b:
                fm = re.search(r"factor\s*=\s*([0-9]+(?:\.[0-9]+)?)", ai_b[0])
                if fm:
                    opt_factors[name_m.group(1)] = float(fm.group(1))
        assert opt_factors
        total = sum(opt_factors.values())
        key = next(k for k in opt_factors if k.endswith(option_suffix))
        return opt_factors[key] / total

    p1 = max_rl_prob(events["wr_cultural_maneuver.1"], "wr_cultural_maneuver.2")
    p2 = max_rl_prob(events["wr_cultural_maneuver.10"], "wr_cultural_maneuver.11")
    p3 = max_rl_prob(events["wr_cultural_maneuver.20"], "wr_cultural_maneuver.21")
    p4 = max_rl_prob(events["wr_cultural_maneuver.30"], "wr_cultural_maneuver.31")
    p4_sub = max_rl_prob(events["wr_cultural_maneuver.35"], "wr_convert_country_to_west_slavic_effect")
    p4_c1 = max_rl_prob(events["wr_cultural_maneuver.44"], "wr_sync_circle1_stage4_with_from_effect")
    p4_c2 = max_rl_prob(events["wr_cultural_maneuver.54"], "wr_sync_circle2_stage4_with_from_effect")
    p4_c3 = max_rl_prob(events["wr_cultural_maneuver.64"], "wr_sync_circle3_stage4_with_from_effect")

    assert p1 <= 0.50, f"Stage 1 chance {p1:.4f} exceeds 50%"
    assert p2 <= 0.30, f"Stage 2 chance {p2:.4f} exceeds 30%"
    assert p3 < 0.20, f"Stage 3 chance {p3:.4f} must be < 20%"
    for label, prob in (("Stage 4", p4), (".35", p4_sub), (".44", p4_c1), (".54", p4_c2), (".64", p4_c3)):
        assert prob < 0.05, f"{label} max chance {prob:.4f} must be < 5%"

    assert ai_trial_share(events["wr_cultural_maneuver.1"], ".1.a") <= 0.50
    assert ai_trial_share(events["wr_cultural_maneuver.10"], ".10.a") <= 0.30
    assert ai_trial_share(events["wr_cultural_maneuver.15"], ".15.a") <= 0.30
    assert ai_trial_share(events["wr_cultural_maneuver.20"], ".20.a") < 0.20
    for n in (30, 35, 44, 54, 64):
        assert ai_trial_share(events[f"wr_cultural_maneuver.{n}"], f".{n}.a") < 0.05
        assert "ai = no" not in events[f"wr_cultural_maneuver.{n}"], f"Stage 4 event .{n} must not allow ai = no bypass"

    e30 = events["wr_cultural_maneuver.30"]
    assert "wr_apply_stage4_west_slavic_transition_effect" not in e30
    assert "wr_convert_country_to_west_slavic_effect" not in e30
    # Failure on Stage 4 (.32) must preserve Stage 3 cultural affinity
    e32 = events["wr_cultural_maneuver.32"]
    assert "remove_country_modifier = wr_west_slavic_cultural_affinity" not in e32
    assert "clr_country_flag = wr_west_slavic_affinity_active" not in e32

    # Decisions must use high potential/allow gates, serious costs, only open entry events, and respect ai_will_do caps
    for dec, pot_t, allow_t, target_evt, max_ai, req_toks in (
        (
            "wr_charter_distinctiveness_decision",
            "wr_potential_stage1",
            "wr_allow_stage1",
            "wr_cultural_maneuver.1",
            0.50,
            ("adm_power = 125", "dip_power = 125", "years_of_income = 0.5"),
        ),
        (
            "wr_codify_west_ruthenian_group_decision",
            "wr_potential_stage2",
            "wr_allow_stage2",
            "wr_cultural_maneuver.10",
            0.30,
            ("adm_power = 200", "dip_power = 200", "treasury = 250"),
        ),
        (
            "wr_proclaim_west_slavic_affinity_decision",
            "wr_potential_stage3",
            "wr_allow_stage3",
            "wr_cultural_maneuver.20",
            0.20,
            ("adm_power = 150", "dip_power = 250", "years_of_income = 0.75"),
        ),
        (
            "wr_attempt_west_slavic_transition_decision",
            "wr_potential_stage4",
            "wr_allow_stage4",
            "wr_cultural_maneuver.30",
            0.05,
            ("adm_power = 250", "dip_power = 300", "treasury = 500"),
        ),
    ):
        db = extract_brace_block(decisions_text, dec)
        assert db is not None, f"Missing decision {dec}"
        assert f"{pot_t} = yes" in db[0]
        assert f"{allow_t} = yes" in db[0]
        for tok in req_toks:
            assert tok in db[0], f"{dec} missing cost gate {tok}"
        assert f"id = {target_evt}" in db[0]
        assert "wr_apply_" not in db[0] and "wr_convert_" not in db[0]
        ai_wd = extract_brace_block(db[0], "ai_will_do")
        assert ai_wd is not None
        fm = re.search(r"factor\s*=\s*([0-9]+(?:\.[0-9]+)?)", ai_wd[0])
        assert fm and float(fm.group(1)) <= max_ai

    # Diplomatic Rally Congress decisions + on_actions index sync + congress mutual exclusion
    for dec, pot_t, allow_t, target_eff, max_ai, cd_flag in (
        (
            "wr_rally_branch_a_congress_decision",
            "wr_potential_rally_branch_a",
            "wr_allow_rally_branch_a",
            "wr_rally_branch_a_congress_effect",
            0.30,
            "wr_branch_a_rally_cooldown",
        ),
        (
            "wr_rally_branch_b_congress_decision",
            "wr_potential_rally_branch_b",
            "wr_allow_rally_branch_b",
            "wr_rally_branch_b_congress_effect",
            0.20,
            "wr_branch_b_rally_cooldown",
        ),
    ):
        db = extract_brace_block(decisions_text, dec)
        assert db is not None and f"{pot_t} = yes" in db[0] and f"{allow_t} = yes" in db[0]
        assert f"{target_eff} = yes" in db[0]
        allow_b = extract_brace_block(triggers_text, allow_t)
        assert allow_b and cd_flag in allow_b[0] and "days = 3650" in allow_b[0]
        ai_wd = extract_brace_block(db[0], "ai_will_do")
        fm = re.search(r"factor\s*=\s*([0-9]+(?:\.[0-9]+)?)", ai_wd[0])
        assert fm and float(fm.group(1)) <= max_ai

    on_act_path = ROOT / "common" / "on_actions" / "rip_west_ruthenian_on_actions.txt"
    assert on_act_path.exists()
    on_act = on_act_path.read_text(encoding="utf-8")
    for hook in (
        "on_startup",
        "on_yearly_pulse",
        "on_province_owner_change",
        "on_province_culture_converted",
        "on_province_culture_changed",
    ):
        blk = extract_brace_block(on_act, hook)
        assert blk and (
            "wr_recalculate_maneuver_indices_effect" in blk[0]
            or "wr_sync_single_province_charter_effect" in blk[0]
        ), f"on_actions {hook} missing charter/index sync"

    # Diplomatic response ai_chance modifiers & mutual-exclusion triggers on Congress events
    for eid in (41, 43, 51, 53, 61, 63):
        ev_body = events[f"wr_cultural_maneuver.{eid}"]
        assert "is_subject_of = FROM" in ev_body and "alliance_with = FROM" in ev_body
        assert "wr_apply_stage1_distinctiveness_from_sphere_effect" in ev_body or "wr_grant_circle3_stage1_provinces_from_sphere_effect" in ev_body or "wr_grant_circle3_stage3_provinces_from_sphere_effect" in ev_body or "wr_apply_stage3_west_slavic_affinity_local_effect" in ev_body
    for eid in (41, 42, 51, 52, 61, 62):
        ev_body = events[f"wr_cultural_maneuver.{eid}"]
        m_trig = re.search(r"^\ttrigger\s*=\s*\{", ev_body, re.MULTILINE)
        trig_b = extract_brace_block(ev_body, "trigger", m_trig.start()) if m_trig else None
        assert trig_b and "wr_west_slavic_affinity_active" in trig_b[0]
    for eid in (43, 44, 53, 54, 63, 64):
        ev_body = events[f"wr_cultural_maneuver.{eid}"]
        m_trig = re.search(r"^\ttrigger\s*=\s*\{", ev_body, re.MULTILINE)
        trig_b = extract_brace_block(ev_body, "trigger", m_trig.start()) if m_trig else None
        assert trig_b and "wr_distinctiveness_recognized" in trig_b[0]


def check_localisation() -> None:
    expected_keys = {
        "west_ruthenian",
        "byelorussian_west_ruthenian",
        "byelorussian_west_ruthenian_adj",
        "ruthenian_west_ruthenian",
        "ruthenian_west_ruthenian_adj",
        "rusyn_west_ruthenian",
        "rusyn_west_ruthenian_adj",
        "byelorussian_west_slavic",
        "byelorussian_west_slavic_adj",
        "ruthenian_west_slavic",
        "ruthenian_west_slavic_adj",
        "rusyn_west_slavic",
        "rusyn_west_slavic_adj",
        "wr_tt_byelorussian_s2_index",
        "wr_tt_ruthenian_s2_index",
        "wr_tt_rusyn_s2_index",
        "wr_tt_byelorussian_s4_index",
        "wr_tt_ruthenian_s4_index",
        "wr_tt_rusyn_s4_index",
        "wr_west_ruthenian_distinctiveness",
        "desc_wr_west_ruthenian_distinctiveness",
        "wr_chancery_prosta_mova_tradition",
        "desc_wr_chancery_prosta_mova_tradition",
        "wr_west_ruthenian_commonwealth",
        "desc_wr_west_ruthenian_commonwealth",
        "wr_west_ruthenian_statute_autonomy",
        "desc_wr_west_ruthenian_statute_autonomy",
        "wr_west_slavic_cultural_affinity",
        "desc_wr_west_slavic_cultural_affinity",
        "wr_west_slavic_shared_script_space",
        "desc_wr_west_slavic_shared_script_space",
        "wr_west_slavic_synthesis",
        "desc_wr_west_slavic_synthesis",
        "wr_traditionalist_backlash",
        "desc_wr_traditionalist_backlash",
        "wr_collective_concord",
        "desc_wr_collective_concord",
        "wr_cultural_ferment",
        "desc_wr_cultural_ferment",
        "opinion_wr_west_slavic_kinship",
        "opinion_wr_west_ruthenian_separation",
        "opinion_wr_collective_accord",
        "opinion_wr_collective_discord",
        "wr_charter_distinctiveness_decision_title",
        "wr_charter_distinctiveness_decision_desc",
        "wr_rally_branch_a_congress_decision_title",
        "wr_rally_branch_a_congress_decision_desc",
        "wr_codify_west_ruthenian_group_decision_title",
        "wr_codify_west_ruthenian_group_decision_desc",
        "wr_proclaim_west_slavic_affinity_decision_title",
        "wr_proclaim_west_slavic_affinity_decision_desc",
        "wr_rally_branch_b_congress_decision_title",
        "wr_rally_branch_b_congress_decision_desc",
        "wr_attempt_west_slavic_transition_decision_title",
        "wr_attempt_west_slavic_transition_decision_desc",
    }
    event_opts = {
        1: ("a", "b", "c"),
        2: ("a",),
        3: ("a",),
        10: ("a", "b", "c"),
        11: ("a",),
        12: ("a",),
        15: ("a", "b"),
        20: ("a", "b", "c"),
        21: ("a",),
        22: ("a",),
        30: ("a", "b"),
        31: ("a",),
        32: ("a",),
        35: ("a", "b"),
        41: ("a", "b"),
        42: ("a", "b"),
        43: ("a", "b"),
        44: ("a", "b"),
        51: ("a", "b"),
        52: ("a", "b"),
        53: ("a", "b"),
        54: ("a", "b"),
        61: ("a", "b"),
        62: ("a", "b"),
        63: ("a", "b"),
        64: ("a", "b"),
    }
    events_text = (ROOT / "events" / "RIP_shared_west_ruthenian_CulturalManeuver.txt").read_text(encoding="utf-8")
    for eid, opts in event_opts.items():
        expected_keys.add(f"wr_cultural_maneuver.{eid}.t")
        expected_keys.add(f"wr_cultural_maneuver.{eid}.d")
        expected_keys.add(f"wr_cultural_maneuver.{eid}.d_belarus")
        expected_keys.add(f"wr_cultural_maneuver.{eid}.d_ruthenia")
        expected_keys.add(f"wr_cultural_maneuver.{eid}.d_rusyn")
        assert f"desc = wr_cultural_maneuver.{eid}.d_belarus" in events_text, (
            f"Event {eid} missing conditional Belarus description"
        )
        assert f"desc = wr_cultural_maneuver.{eid}.d_ruthenia" in events_text, (
            f"Event {eid} missing conditional Ruthenia description"
        )
        assert f"desc = wr_cultural_maneuver.{eid}.d_rusyn" in events_text, (
            f"Event {eid} missing conditional Rusnak description"
        )
        for o in opts:
            expected_keys.add(f"wr_cultural_maneuver.{eid}.{o}")

    expected_culture_loc = {
        "english": {
            "west_ruthenian": "Ruthenian",
            "byelorussian_west_ruthenian": "Bielaruski",
            "ruthenian_west_ruthenian": "Ruskyi",
            "rusyn_west_ruthenian": "Rusnacky",
            "byelorussian_west_slavic": "Bjalowruszsky",
            "ruthenian_west_slavic": "Ruszynjsky",
            "rusyn_west_slavic": "Rusznjoczky",
        },
        "french": {
            "west_ruthenian": "ruthène",
            "byelorussian_west_ruthenian": "bielaruski",
            "ruthenian_west_ruthenian": "ruskyi",
            "rusyn_west_ruthenian": "rusnacky",
            "byelorussian_west_slavic": "bjalowruszsky",
            "ruthenian_west_slavic": "ruszynjsky",
            "rusyn_west_slavic": "rusznjoczky",
        },
        "german": {
            "west_ruthenian": "Ruthenisch",
            "byelorussian_west_ruthenian": "Bielaruski",
            "ruthenian_west_ruthenian": "Ruskyi",
            "rusyn_west_ruthenian": "Rusnacky",
            "byelorussian_west_slavic": "Bjalowruszsky",
            "ruthenian_west_slavic": "Ruszynjsky",
            "rusyn_west_slavic": "Rusznjoczky",
        },
        "spanish": {
            "west_ruthenian": "rutena",
            "byelorussian_west_ruthenian": "bielaruski",
            "ruthenian_west_ruthenian": "ruskyi",
            "rusyn_west_ruthenian": "rusnacky",
            "byelorussian_west_slavic": "bjalowruszsky",
            "ruthenian_west_slavic": "ruszynjsky",
            "rusyn_west_slavic": "rusznjoczky",
        },
    }

    for lang in ("english", "french", "german", "spanish"):
        path = ROOT / "localisation" / f"RIP_shared_west_ruthenian_charters_l_{lang}.yml"
        raw = path.read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf"), f"{path.name} missing UTF-8 BOM"
        assert not raw.startswith(b"\xef\xbb\xbf\xef\xbb\xbf"), f"{path.name} has double BOM"
        text = raw.decode("utf-8-sig")
        assert text.splitlines()[0].strip() == f"l_{lang}:"
        kv = dict(re.findall(r'^\s+([a-zA-Z0-9_.]+):0\s+"((?:\\.|[^"\\])*)"', text, re.MULTILINE))
        missing = expected_keys - set(kv)
        assert not missing, f"{path.name} missing keys: {sorted(missing)}"
        for key, expected_val in expected_culture_loc[lang].items():
            assert kv.get(key) == expected_val, (
                f"{path.name}: {key} expected {expected_val!r}, got {kv.get(key)!r}"
            )
            if key != "west_ruthenian":
                assert expected_val.isascii(), (
                    f"{path.name}: coined culture name {key}={expected_val!r} must be ASCII without diacritics"
                )
                assert kv.get(f"{key}_adj") == expected_val
        for key, val in kv.items():
            try:
                val.encode("cp1252")
            except UnicodeEncodeError as exc:
                raise AssertionError(
                    f"{path.name}: key {key} contains character unsupported by EU4 Windows-1252 fonts: {val!r}"
                ) from exc


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    check_cultures_and_starts()
    check_province_names_and_compatibility()
    check_probabilities_and_triggers()
    check_localisation()
    print(
        "WEST-RUTHENIAN CULTURAL MANEUVER PASS: "
        "byelorussian/ruthenian/rusyn cultures, ASCII zero-diacritic naming, 1444 preservation, "
        "mutual branch exclusion, >=60%/>=85% global adoption indices, rally congresses, "
        "on_actions sync, probability caps (<=50%, <=30%, <20%, <5%), and EFIGS localisation hold."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
