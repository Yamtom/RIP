"""Static contracts for UZH mission resource deductions, arrow routing, vertical compactness, and flag visibility."""
from __future__ import annotations

import re

from clausewitz_testlib import ROOT, keyed_blocks, read


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

    # 3. Structural repairs: no P11 hole in Uhro-Rusyn, downward palatial arrow, contiguous Slot 5 econ
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

    print("PASS: UZH mission layout, costs, arrow geometry, closed gaps, and flag visibility contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
