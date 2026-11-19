"""Static contracts for UZH mission resource deductions, arrow routing, vertical compactness, and flag visibility."""
from __future__ import annotations

from collections import defaultdict
import re

from clausewitz_testlib import ROOT, keyed_blocks, normalized, read, vanilla_root


BRANCH_SERIES = {
    "branch": "UZH_missions_3_branch",
    "ruthenian": "UZH_missions_3_ruthenian",
    "rusyn": "UZH_missions_3_rusyn",
    "uhro_rusyn": "UZH_missions_3_uhro_rusyn",
}


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"#.*", "", line) for line in text.splitlines())


def extract_subblock(text: str, key: str) -> str:
    m = re.search(rf"\b{re.escape(key)}\s*=\s*\{{", text)
    if not m:
        return ""
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


def parse_missions(missions_text: str) -> dict[str, dict]:
    parsed: dict[str, dict] = {}
    cur_series = None
    slot = None
    depth = 0
    cur_mission = None
    m_lines: list[str] = []

    for raw in missions_text.splitlines():
        clean = re.sub(r"#.*", "", raw)
        if depth == 0:
            ms = re.match(r"^([A-Za-z0-9_]+)\s*=\s*\{", clean)
            if ms:
                cur_series = ms.group(1)
                slot = None
        elif depth == 1 and cur_series is not None:
            sl = re.match(r"^\s*slot\s*=\s*(\d+)", clean)
            if sl:
                slot = int(sl.group(1))
            mm = re.match(r"^\t([A-Za-z0-9_]+)\s*=\s*\{", clean)
            if mm and mm.group(1) not in ("potential", "potential_on_load"):
                cur_mission = mm.group(1)
                m_lines = [raw]
        elif cur_mission is not None:
            m_lines.append(raw)

        depth += clean.count("{") - clean.count("}")
        if cur_mission is not None and depth < 2:
            body = "\n".join(m_lines)
            clean_body = strip_comments(body)
            mp = re.search(r"\bposition\s*=\s*(\d+)", clean_body)
            mr = re.search(r"required_missions\s*=\s*\{([^}]*)\}", clean_body, re.S)
            trig = extract_subblock(body, "trigger")
            eff = extract_subblock(body, "effect")
            parsed[cur_mission] = {
                "name": cur_mission,
                "series": cur_series,
                "slot": slot,
                "pos": int(mp.group(1)) if mp else None,
                "reqs": re.findall(r"[A-Za-z0-9_]+", strip_comments(mr.group(1))) if mr else [],
                "trigger": trig,
                "effect": eff,
                "body": body,
            }
            cur_mission = None
            m_lines = []
    return parsed


def loc_entries(path) -> dict[str, str]:
    return dict(
        re.findall(
            r'^ ([A-Za-z0-9_.\-]+):\d+ "(.*)"$',
            path.read_text(encoding="utf-8-sig"),
            re.M,
        )
    )


def main() -> int:
    missions_text = read("missions/Zakarpatta_Missions.txt")
    events_text = read("events/RIP_UZH_Uzh.txt")
    missions = parse_missions(missions_text)

    # 1. Every treasury / monarch-power trigger cost must be deducted in effect
    cost_missions = set()
    for name, m in missions.items():
        trig_c = strip_comments(m["trigger"])
        eff_c = strip_comments(m["effect"])
        for res in ("treasury", "adm_power", "dip_power", "mil_power"):
            reqs = re.findall(rf"\b{res}\s*=\s*([0-9]+(?:\.[0-9]+)?)", trig_c)
            if reqs:
                spends = re.findall(rf"\badd_{res}\s*=\s*-([0-9]+(?:\.[0-9]+)?)", eff_c)
                assert reqs == spends, (name, res, reqs, spends)
                cost_missions.add(name)
    assert {
        "uz_union_compromise_plus",
        "uz_rusin_language",
        "uz_language_decree",
        "uz_identity_question",
        "uzh_solotvynska_camera",
    }.issubset(cost_missions)

    # 2. Validate grid geometry across all 4 branch views
    all_branch_names = set(BRANCH_SERIES.values())
    shared_names = {n for n, m in missions.items() if m["series"] not in all_branch_names}

    for b_key, b_series in BRANCH_SERIES.items():
        active = shared_names | {n for n, m in missions.items() if m["series"] == b_series}
        seen_cells: dict[tuple[int, int], str] = {}
        for name in active:
            m = missions[name]
            assert m["slot"] is not None and m["pos"] is not None, name
            cell = (m["slot"], m["pos"])
            assert cell not in seen_cells, (b_key, cell, seen_cells[cell], name)
            seen_cells[cell] = name

        wide_edges = []
        for dst_name in active:
            dst = missions[dst_name]
            for src_name in dst["reqs"]:
                assert src_name in active, (b_key, dst_name, src_name)
                src = missions[src_name]
                # Never point upward or horizontally
                assert dst["pos"] > src["pos"], (
                    f"{b_key}: {src_name}(S{src['slot']}P{src['pos']}) -> "
                    f"{dst_name}(S{dst['slot']}P{dst['pos']}) must go downward"
                )
                span = abs(dst["slot"] - src["slot"])
                assert span <= 2, (b_key, src_name, dst_name, span)
                if span == 2:
                    wide_edges.append((src_name, dst_name))
                if src["slot"] != dst["slot"]:
                    assert dst["pos"] - src["pos"] == 1, (
                        f"{b_key}: cross-column arrow {src_name}(S{src['slot']}P{src['pos']}) -> "
                        f"{dst_name}(S{dst['slot']}P{dst['pos']}) must span 1 row"
                    )
                elif dst["pos"] - src["pos"] > 1:
                    blockers = [
                        n
                        for n in active
                        if missions[n]["slot"] == src["slot"]
                        and src["pos"] < missions[n]["pos"] < dst["pos"]
                    ]
                    assert not blockers, (b_key, src_name, dst_name, blockers)

        assert set(wide_edges) <= {("uzh_pannonian_republic", "uzh_federalization")}, wide_edges

        # EU4 stacks multiple simultaneously active series in the same slot sequentially
        # by file order rather than interleaving their `position` numbers. Verify every
        # active series is strictly ascending and never starts at or above an earlier
        # active series's maximum row in the same slot.
        series_in_slot: dict[int, list[tuple[str, list[int]]]] = defaultdict(list)
        series_seen: dict[str, list[int]] = {}
        for m in missions.values():
            if m["name"] not in active:
                continue
            if m["series"] not in series_seen:
                positions: list[int] = []
                series_seen[m["series"]] = positions
                series_in_slot[m["slot"]].append((m["series"], positions))
            series_seen[m["series"]].append(m["pos"])
        for slot_num, slot_series in series_in_slot.items():
            prev_max = 0
            for s_name, positions in slot_series:
                assert positions == sorted(positions) and len(positions) == len(set(positions)), (
                    f"{b_key}: series {s_name} (slot {slot_num}) has non-ascending positions {positions}"
                )
                assert min(positions) > prev_max, (
                    f"{b_key}: series {s_name} (slot {slot_num}, min P{min(positions)}) interleaves with "
                    f"earlier active series ending at P{prev_max}; EU4 would stack it below P{prev_max}"
                )
                prev_max = max(positions)

    # 3. Structural repairs: no P11 hole in Uhro-Rusyn, downward palatial arrow, contiguous Slot 5 econ
    assert "UZH_missions_realm" not in missions_text
    assert [m["pos"] for m in missions.values() if m["series"] == "UZH_missions_4"] == [3, 4, 8, 9, 10, 11, 12]
    assert missions["uz_huszt_rename"]["series"] == "UZH_missions_4"
    assert missions["uz_zakarpattia_realm"]["series"] == "UZH_missions_4"
    uhro_positions = sorted(
        m["pos"] for m in missions.values() if m["series"] == "UZH_missions_3_uhro_rusyn"
    )
    assert uhro_positions == [9, 10, 11, 12], uhro_positions

    assert (missions["uz_identity_question"]["slot"], missions["uz_identity_question"]["pos"]) == (3, 7)
    assert (missions["uzh_palatial_reform"]["slot"], missions["uzh_palatial_reform"]["pos"]) == (4, 8)
    assert (missions["uz_huszt_rename"]["slot"], missions["uz_huszt_rename"]["pos"]) == (4, 9)
    assert (
        missions["uzh_constitutional_monarchy"]["slot"],
        missions["uzh_constitutional_monarchy"]["pos"],
    ) == (5, 5)
    assert missions["uzh_constitutional_monarchy"]["reqs"] == ["uzh_rusin_nobility"]

    slot5_lower = sorted(
        m["pos"]
        for m in missions.values()
        if m["slot"] == 5 and m["name"] != "uzh_constitutional_monarchy"
    )
    assert slot5_lower == [7, 8, 9, 10, 11, 12, 13], slot5_lower

    # 4. Flag gate visibility & dead-flag cleanup
    agri_trig = strip_comments(missions["uzh_agriculture"]["trigger"])
    assert missions["uzh_agriculture"]["reqs"] == []
    assert "uzh_mukachevo_privilege_confirmed" not in agri_trig

    assert set(missions["uz_rusin_language"]["reqs"]) == {
        "uz_union_compromise_plus",
        "uz_rusin_literacy",
    }
    assert "chose_ruthenian_identity" not in missions["uz_rusin_language"]["body"]
    assert "chose_uhro_rusyn_identity" not in missions["uz_rusin_language"]["body"]
    assert "uzh_pre_identity_candidate_culture = yes" in missions["uz_rusin_language"]["body"]
    assert missions["uz_language_decree"]["reqs"] == ["uz_rusin_language"]
    assert missions["uzh_trade_routes"]["reqs"] == ["uzh_solotvynska_camera"]

    # Map event flags and mission flags
    event_flags: dict[str, set[str]] = {}
    for _, ev_blk in keyed_blocks(events_text, "country_event"):
        ev_id = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", ev_blk)
        if ev_id:
            event_flags[ev_id.group(1)] = set(
                re.findall(r"set_country_flag\s*=\s*([A-Za-z0-9_]+)", strip_comments(ev_blk))
            )

    flag_setters: dict[str, list[str]] = {}
    for name, m in missions.items():
        eff_c = strip_comments(m["effect"])
        flags = set(re.findall(r"set_country_flag\s*=\s*([A-Za-z0-9_]+)", eff_c))
        for ev_id in re.findall(r"\bid\s*=\s*([A-Za-z0-9_.]+)", eff_c):
            flags |= event_flags.get(ev_id, set())
        for fl in flags:
            flag_setters.setdefault(fl, []).append(name)

    def ancestors(name: str) -> set[str]:
        seen, stack = set(), list(missions[name]["reqs"])
        while stack:
            cur = stack.pop()
            if cur in seen or cur not in missions:
                continue
            seen.add(cur)
            stack.extend(missions[cur]["reqs"])
        return seen

    unexpected_non_ancestors = []
    allowed_non_ancestors = {
        ("uzh_constitutional_monarchy", "uzh_pannonian_republic_established"),  # NOT exclusion
        ("uz_huszt_rename", "uzh_name_zakarpattia"),  # NOT exclusion
        ("uz_national_revival", "uzh_komitat_restructured"),  # wrapped in UZH_revival_komitat_condition_tt
        ("uz_carpathian_commonwealth", "uzh_komitat_restructured"),  # wrapped in UZH_revival_komitat_condition_tt
        ("uzh_pannonian_republic", "uzh_constitutional_framework"),  # wrapped in UZH_pannonian_compact_government_tt
        ("uzh_federalization", "uzh_constitutional_framework"),  # OR with direct-ancestor uzh_pannonian_compact_signed
    }
    for name, m in missions.items():
        anc = ancestors(name)
        trig_c = strip_comments(m["trigger"])
        checked = set(re.findall(r"(?:has_country_flag|flag)\s*=\s*([A-Za-z0-9_]+)", trig_c))
        for fl in sorted(checked):
            setters = flag_setters.get(fl, [])
            if setters and not any(s in anc for s in setters):
                if (name, fl) not in allowed_non_ancestors:
                    unexpected_non_ancestors.append((name, fl, setters))
    assert not unexpected_non_ancestors, unexpected_non_ancestors

    # Verify wrapped tooltips and mission name references in localisation
    for mname in ("uz_national_revival", "uz_carpathian_commonwealth"):
        assert "tooltip = UZH_revival_komitat_condition_tt" in missions[mname]["trigger"], mname
    assert "tooltip = UZH_pannonian_compact_government_tt" in missions["uzh_pannonian_republic"]["trigger"]

    en = loc_entries(ROOT / "localisation/RIP_UZH_realm_l_english.yml")
    assert "Codify the Huszt Statute" in en["UZH_pannonian_compact_government_tt"]
    assert "Komitat System" in en["UZH_revival_komitat_condition_tt"]
    for lang in ("french", "german", "spanish"):
        fb = loc_entries(ROOT / f"localisation/replace/RIP_UZH_content_l_{lang}.yml")
        for key in ("UZH_pannonian_compact_government_tt", "UZH_revival_komitat_condition_tt"):
            assert fb.get(key) == en[key], (lang, key)

    # 5. Palanok scale direction & permanent modifier balance contracts
    komitat_norm = normalized(missions["uzh_komitat_system"]["body"])
    assert "0.7" not in komitat_norm
    assert "OR = { NOT = { statists_vs_orangists = -0.5 } statists_vs_orangists = 0.5 }" in komitat_norm
    assert (
        "limit = { has_states_general_mechanic = yes has_reform = uzh_palanok_captaincy_reform statists_vs_orangists = 0.5 } add_army_tradition = 10"
        in komitat_norm
    )

    unity_eff = missions["uz_orthodox_unity"]["effect"]
    assert "uz_orthodox_metropolis" in extract_subblock(unity_eff, "capital_scope")
    for _, loop_blk in keyed_blocks(unity_eff, "every_owned_province"):
        assert "uz_orthodox_metropolis" not in loop_blk

    # Non-capstone missions must grant 25-year (9125d) rather than permanent modifiers
    for mname in (
        "uzh_pannonian_republic",
        "uz_kyivan_heritage",
        "uz_orthodox_unity",
        "uz_rusyn_autonomy",
        "uz_carpathian_federation",
        "uz_uhro_rusyn_integration",
        "uz_crown_of_saint_stephen",
        "uzh_congress_subject_hegemony",
    ):
        for _, cm_blk in keyed_blocks(missions[mname]["effect"], "add_country_modifier"):
            assert not re.search(r"\bduration\s*=\s*-1\b", cm_blk), (mname, cm_blk)

    # Parse modifier definitions from RIP_UZH_modifiers.txt and check worst-case stack bounds
    mod_defs: dict[str, dict[str, float]] = {}
    mod_text = strip_comments(read("common/event_modifiers/RIP_UZH_modifiers.txt"))
    for mm in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*\{([^}]*)\}", mod_text, re.M):
        stats: dict[str, float] = {}
        for line in mm.group(2).splitlines():
            if "=" in line:
                k, v = [p.strip() for p in line.split("=", 1)]
                try:
                    stats[k] = float(v)
                except ValueError:
                    pass
        mod_defs[mm.group(1)] = stats

    # Collect permanent country modifiers granted unconditionally by shared events (uzh.7, uzh.8)
    ev_perm_mods: set[str] = set()
    for _, ev_blk in keyed_blocks(events_text, "country_event"):
        if re.search(r"\bid\s*=\s*uzh\.(7|8)\b", ev_blk):
            for _, cm_blk in keyed_blocks(ev_blk, "add_country_modifier"):
                if re.search(r"\bduration\s*=\s*-1\b", cm_blk):
                    nm = re.search(r'\bname\s*=\s*"?([A-Za-z0-9_]+)"?', cm_blk)
                    if nm:
                        ev_perm_mods.add(nm.group(1))

    branch_caps = {
        "ruthenian": {"uz_pan_ruthenian_union"},
        "rusyn": {"uz_carpathian_commonwealth"},
        "uhro_rusyn": {"danubian_monarchy_influence"},
    }
    for b_key, b_mods in branch_caps.items():
        # Verify the branch series actually only uses those permanent country modifiers
        series_name = BRANCH_SERIES[b_key]
        found_branch_perms = set()
        for m in missions.values():
            if m["series"] == series_name:
                for _, cm_blk in keyed_blocks(m["effect"], "add_country_modifier"):
                    if re.search(r"\bduration\s*=\s*-1\b", cm_blk):
                        nm = re.search(r'\bname\s*=\s*"?([A-Za-z0-9_]+)"?', cm_blk)
                        if nm:
                            found_branch_perms.add(nm.group(1))
        assert found_branch_perms == b_mods, (b_key, found_branch_perms, b_mods)

        for gov in ("monarchy", "republic", "theocracy"):
            for congress in ("subject", "border"):
                active_mods = set(ev_perm_mods) | b_mods | {
                    "uz_danube_trade_league",
                    "uz_federal_structure",
                    "uz_federative_statutes_autonomy"
                    if gov == "republic"
                    else "uz_federative_statutes_capacity",
                    "uz_congress_border_drill" if congress == "border" else "uz_pan_ruthenian_union",
                }
                if gov == "monarchy":
                    active_mods |= {"uz_constitutional_system", "uz_statute_codification"}

                assert len(active_mods) <= 8, (b_key, gov, congress, len(active_mods), active_mods)
                totals: dict[str, float] = defaultdict(float)
                for mod_name in active_mods:
                    for stat, val in mod_defs[mod_name].items():
                        totals[stat] += val

                assert totals["governing_capacity_modifier"] <= 0.20 + 1e-9, (b_key, gov, congress, totals)
                assert totals["governing_capacity"] <= 150 + 1e-9, (b_key, gov, congress, totals)
                assert totals["diplomatic_reputation"] <= 2 + 1e-9, (b_key, gov, congress, totals)
                assert totals["all_power_cost"] == 0, (b_key, gov, congress, totals)
                assert totals["administrative_efficiency"] == 0, (b_key, gov, congress, totals)
                assert totals["num_accepted_cultures"] <= 2 + 1e-9, (b_key, gov, congress, totals)

    assert "permanently" not in en["UZH_pannonian_republic_foundation_tt"].lower()
    assert "permanently" not in en["UZH_congress_subject_hegemony_subject_tt"].lower()
    assert "+100" in en["UZH_federative_statutes_reward_tt"]
    assert "50" in en["uzh_komitat_captains_party_tt"]
    for lang in ("french", "german", "spanish"):
        fb = loc_entries(ROOT / f"localisation/replace/RIP_UZH_content_l_{lang}.yml")
        for key in (
            "uzh_komitat_captains_party_tt",
            "uzh_komitat_system_desc",
            "UZH_pannonian_republic_foundation_tt",
            "UZH_federative_statutes_reward_tt",
            "UZH_congress_subject_hegemony_subject_tt",
        ):
            assert fb.get(key) == en[key], (lang, key)

    # 6. Smooth reward spikes, remove event duplicates, remove rigid idea gates, fix 1444 start bottlenecks
    pannonian_eff = missions["uzh_pannonian_republic"]["effect"]
    assert "uz_pannonian_league" not in pannonian_eff
    assert "uz_border_guard_union" not in pannonian_eff
    assert "uzh_gain_manpower_6000" not in pannonian_eff
    assert "change_government_reform_progress = 35" in pannonian_eff

    ev_blocks = {}
    for _, ev_blk in keyed_blocks(events_text, "country_event"):
        ev_id = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", ev_blk)
        if ev_id:
            ev_blocks[ev_id.group(1)] = ev_blk

    ev5_norm = normalized(ev_blocks["uzh.5"])
    assert "uz_border_dynasty_network" not in ev5_norm
    ev202b_norm = normalized(list(keyed_blocks(ev_blocks["uzh.202"], "option"))[1][1])
    assert "uzh_gain_manpower_6000 = yes" in ev202b_norm
    assert "add_mil_power = 100" not in ev202b_norm

    exp_eff_norm = normalized(missions["uzh_pannonian_expansion"]["effect"])
    assert "uz_pannonian_drive" not in exp_eff_norm
    assert "add_mil_power" not in exp_eff_norm
    assert "id = uzh.230" in exp_eff_norm

    kyiv_trig = normalized(missions["uz_kyivan_heritage"]["trigger"])
    assert "OR = { has_idea_group = religious_ideas has_idea_group = influence_ideas AND = { religious_unity = 0.85 diplomatic_reputation = 2 } }" in kyiv_trig
    fed_trig = normalized(missions["uzh_federalization"]["trigger"])
    assert "OR = { has_idea_group = administrative_ideas AND = { stability = 2 reform_level = 6 } }" in fed_trig

    frontier_trig = normalized(missions["uzh_pannonian_frontier"]["trigger"])
    for tok in ("tag = POL", "tag = HLC", "tag = HAB", "tag = BOH", "is_rival = HUN", "is_subject_of = HUN", "fort_level = 2"):
        assert tok in frontier_trig, tok

    agri_trig = normalized(missions["uzh_agriculture"]["trigger"])
    assert "trade_goods = wine uzh_has_workshop_infrastructure" not in agri_trig
    assert "AND = { has_adm_advisor = yes num_of_owned_provinces_with = { region = carpathia_region OR = { trade_goods = grain trade_goods = livestock trade_goods = wine } base_production = 5 value = 2 } }" in agri_trig

    tisza_trig = normalized(missions["uzh_tisza_customs_convention"]["trigger"])
    assert "share = 35" in tisza_trig
    assert tisza_trig.count("share = 15") == 2

    # 7. Culture-conversion grind relief, Uhro-Rusyn crown coherence, and dynamic uzh.8 loc
    banat_trig = normalized(missions["uzh_banat_colonization"]["trigger"])
    for tok in ("is_core = ROOT", "devastation = 5", "religion = ROOT", "development = 10"):
        assert tok in banat_trig, tok
    assert "culture = rusyn" not in banat_trig

    nobility_trig = normalized(missions["uzh_rusin_nobility"]["trigger"])
    assert "uzh_identity_core_culture = yes uzh_has_courthouse_infrastructure = yes value = 3" in nobility_trig
    assert "has_owner_accepted_culture = yes" in nobility_trig and "value = 4" in nobility_trig

    exp_trig = normalized(missions["uzh_pannonian_expansion"]["trigger"])
    assert "area = alfold_area uzh_identity_core_culture = yes value = 2" in exp_trig
    assert "has_owner_accepted_culture = yes" in exp_trig and "NOT = { nationalism = 1 }" in exp_trig

    decree_trig = normalized(missions["uz_language_decree"]["trigger"])
    assert "uzh_pre_identity_candidate_culture = yes uzh_has_courthouse_infrastructure = yes value = 2" in decree_trig
    assert "region = carpathia_region uzh_has_courthouse_infrastructure = yes value = 3" in decree_trig

    id_q_trig = normalized(missions["uz_identity_question"]["trigger"])
    assert "uzh_pre_identity_candidate_culture = yes value = 3" in id_q_trig
    assert "has_owner_accepted_culture = yes" in id_q_trig and "total_development = 75" in id_q_trig
    assert "uzh_identity_core_culture = yes" not in id_q_trig

    self_id_trig = normalized(missions["uz_self_identification"]["trigger"])
    assert "uzh_identity_core_culture = yes religion = ROOT value = 5" in self_id_trig
    assert "has_owner_accepted_culture = yes" in self_id_trig and "value = 6" in self_id_trig

    stephen_trig = normalized(missions["uz_crown_of_saint_stephen"]["trigger"])
    assert "culture = rusyn_new_new value = 3" in stephen_trig
    assert "has_owner_accepted_culture = yes" in stephen_trig

    stephen_eff = missions["uz_crown_of_saint_stephen"]["effect"]
    loyal_if = normalized(extract_subblock(stephen_eff, "if"))
    assert "opinion_uz_dual_crown" in loyal_if and "add_trust = {" in loyal_if
    assert "add_casus_belli" not in loyal_if
    else_ifs = list(keyed_blocks(stephen_eff, "else_if"))
    assert len(else_ifs) >= 1 and "valid_for_personal_unions_trigger = yes" in normalized(else_ifs[0][1])
    stephen_else = normalized(extract_subblock(stephen_eff, "else"))
    assert "transdanubia_area" in stephen_else and "slovakia_area" in stephen_else
    assert "153 = { add_base_tax = 1 add_base_production = 1 }" in stephen_else

    for key in (
        "uzh.8.t",
        "uzh.8.d",
        "uzh.8.a",
        "uz_rusin_state_title",
        "uz_rusin_state_desc",
        "desc_uz_sovereign_rusin_state",
    ):
        val = en[key]
        assert "[Root.GetUZHIdentityCultureAdjective]" in val, (key, val)
        assert "Rusyn State" not in val and "sovereign Rusyn" not in val, (key, val)

    # 8. Congress pre-choice visible tooltips, zero raw flags in UI, 2-line mission titles, church tooltips
    for mname, req_tts, eff_tts in (
        (
            "uzh_congress_subject_hegemony",
            ("UZH_congress_subject_hegemony_subject_req_tt", "UZH_congress_subject_hegemony_border_req_tt"),
            ("UZH_congress_subject_hegemony_subject_tt", "UZH_congress_subject_hegemony_border_tt"),
        ),
        (
            "uzh_congress_border_bastion",
            ("UZH_congress_border_bastion_subject_req_tt", "UZH_congress_border_bastion_border_req_tt"),
            ("UZH_congress_border_bastion_subject_tt", "UZH_congress_border_bastion_border_tt"),
        ),
    ):
        trig_else = extract_subblock(missions[mname]["trigger"], "else")
        eff_else = extract_subblock(missions[mname]["effect"], "else")
        for tt in req_tts:
            assert tt in trig_else, (mname, tt)
        for tt in eff_tts:
            assert tt in eff_else, (mname, tt)

    for mname, m in missions.items():
        for sec, pats in (
            ("trigger", ("has_country_flag", "had_country_flag", "uzh_identity_core_culture")),
            ("effect", ("set_country_flag", "clr_country_flag")),
        ):
            cd = 0
            shield: list[int] = []
            for tl in strip_comments(m[sec]).splitlines():
                if re.search(r"\b(custom_trigger_tooltip|hidden_trigger|hidden_effect|limit)\s*=\s*\{", tl):
                    shield.append(cd)
                if not shield:
                    for tok in pats:
                        assert tok not in tl, f"{mname}.{sec} exposes raw {tok}: {tl.strip()}"
                cd += tl.count("{") - tl.count("}")
                while shield and cd <= shield[-1]:
                    shield.pop()

    for lang in ("english", "french", "german", "spanish"):
        church_loc = loc_entries(ROOT / f"localisation/replace/RIP_shared_church_content_l_{lang}.yml")
        for k in ("rip_church_florence_effect_tt", "rip_church_sponsor_union_effect_tt"):
            assert k in church_loc and church_loc[k].strip(), (lang, k)
            assert not re.search(r"\?[YGRWBM!]", church_loc[k]), (lang, k, church_loc[k])
    for k, val in en.items():
        assert not re.search(r"\?[YGRWBM!]|Alf\?ld|Krak\?w|B\?cska", val), (k, val)

    vanilla = vanilla_root()
    if vanilla and (vanilla / "gfx/fonts/vic_18.fnt").is_file():
        fnt = (vanilla / "gfx/fonts/vic_18.fnt").read_text(encoding="latin-1")
        adv = {int(mm.group(1)): int(mm.group(2)) for mm in re.finditer(r"char\s+id=(\d+).*?xadvance=(-?\d+)", fnt)}
        sp = adv.get(32, 4)

        def wrap_count(title: str, max_w: int) -> tuple[int, int]:
            lines_w: list[int] = []
            cur_w = 0
            for word in title.split(" "):
                ww = sum(adv.get(ord(ch), 7) for ch in word)
                if cur_w == 0:
                    cur_w = ww
                elif cur_w + sp + ww <= max_w:
                    cur_w += sp + ww
                else:
                    lines_w.append(cur_w)
                    cur_w = ww
            if cur_w:
                lines_w.append(cur_w)
            return len(lines_w), max(lines_w or [0])

        for mname in missions:
            raw_t = en[f"{mname}_title"]
            variants = (
                [raw_t.replace("[Root.GetUZHIdentityCultureAdjective]", adj) for adj in ("Rusyn", "Ruthenian", "Carpathian")]
                if "[Root.GetUZHIdentityCultureAdjective]" in raw_t
                else [raw_t]
            )
            for variant in variants:
                n84, _ = wrap_count(variant, 84)
                n90, w90 = wrap_count(variant, 90)
                assert n84 <= 2 and n90 <= 2 and w90 <= 90, (mname, variant, n84, n90, w90)

    print("PASS: UZH mission layout, costs, arrow geometry, closed gaps, flag visibility, Palanok scale, permanent balance, start/pacing, and dynamic loc contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
