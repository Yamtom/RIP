"""Focused regression checks for Zaporozhie branch victory conditions and Hetmanate missions/events."""

from __future__ import annotations

import re
import sys

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def event_block(text: str, event_id: str) -> str:
    candidates = [
        block for _, block in keyed_blocks(text, "country_event")
        if re.search(rf"\bid\s*=\s*{re.escape(event_id)}\b", block)
        and re.search(r"(?m)^\s*title\s*=", block)
    ]
    if candidates:
        return max(candidates, key=len)
    raise KeyError(f"country_event {event_id!r} not found")


def check_preserved_zaz_strengths(failures: list[str], zaz_missions: str, zaz_events: str) -> None:
    sich = named_block(zaz_missions, "ZAZ_establish_sich")
    require(failures, "283 = {" in sich and "has_building = fort_15th" in sich,
            "ZAZ_establish_sich must preserve Lower Dnieper fort requirement on 283")

    kaffa = named_block(zaz_missions, "ZAZ_TUR_slave_trade")
    require(
        failures,
        "province_id = 285" in kaffa
        and "remove_province_modifier = crimean_yasyr_market" in kaffa
        and "name = kaffa_ransom_exchange" in kaffa
        and "center_of_trade = 1" in kaffa,
        "ZAZ_TUR_slave_trade must preserve Kaffa ransom exchange and CoT development",
    )

    rel_ev = event_block(zaz_events, "zaz_flavor_m_5.1")
    require(failures, "change_religion" not in rel_ev and "zaz_ortho" in rel_ev
            and "prl_brotherhood_schools" in rel_ev,
            "the Porte settlement must offer school funding and parish rights")


def check_zaz_branch_victory_and_russia_finale(failures: list[str], zaz_missions: str) -> None:
    civic_routes = {
        "register": ("TUR_settle_south", "RUS_settle_south", "UKR_settle_south", "POL_cordon"),
        "school": ("UKR_east_dniepr", "POL_east_dniepr"),
        "collegium": ("TUR_settle_north", "RUS_settle_north", "UKR_settle_north", "POL_west_dniepr"),
    }
    for institution, routes in civic_routes.items():
        condition = f"zaz_frontier_{institution} = yes"
        for route in routes:
            mission = named_block(zaz_missions, "ZAZ_" + route)
            assert condition in named_block(mission, "trigger")
            reward = normalized(named_block(mission, "effect"))
            assert f"if = {{ limit = {{ {condition} }}" in reward and "else = {" in reward
    for name in ("ZAZ_TUR_expand_border", "ZAZ_RUS_brack_lit"):
        trigger = normalized(named_block(named_block(zaz_missions, name), "trigger"))
        assert all(token in trigger for token in ("NOT = { exists = LIT }", "NOT = { exists = PLC }", "owns = 1943", "who = PLC"))
    for name in ("ZAZ_GOL_attack_genoa", "ZAZ_UKR_attack_genoa"):
        trigger = normalized(named_block(named_block(zaz_missions, name), "trigger"))
        assert "NOT = { exists = FEO }" in trigger and "alliance_with = ROOT" in trigger
    for name in ("POL_5", "GOL_russia_3", "UKR_russia_3", "POL_russia_3"):
        reward = named_block(named_block(zaz_missions, "ZAZ_" + name), "effect")
        assert "duration = -1" in named_block(reward, "add_country_modifier")
    # 1. Distinct path victory conditions (no mandatory full Ruthenia direct conquest)
    pol_end = named_block(zaz_missions, "ZAZ_POL_ruthenia")
    pol_trig = named_block(pol_end, "trigger")
    pol_eff = named_block(pol_end, "effect")
    require(failures, "ruthenia_region" not in pol_end and "add_permanent_claim" not in pol_eff,
            "ZAZ_POL_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "rip_hadiach_ratified" in pol_trig
        and "rip_register_confirmed" in pol_trig
        and "name = zaz_pol_host_charter" in pol_eff,
        "ZAZ_POL_ruthenia must reward recognized rights of the Host",
    )

    cri_end = named_block(zaz_missions, "ZAZ_cri_crossings_compact")
    cri_trig = named_block(cri_end, "trigger")
    cri_eff = named_block(cri_end, "effect")
    require(
        failures,
        "alliance_with = CRI" in cri_trig
        and "owns = 283" in cri_trig
        and "kaffa_ransom_exchange" in cri_trig
        and "name = zaz_cri_crossings_compact_mod" in cri_eff,
        "ZAZ_cri_crossings_compact must validate Crimean crossings/captives accord",
    )

    gol_end = named_block(zaz_missions, "ZAZ_GOL_ruthenia")
    gol_trig = named_block(gol_end, "trigger")
    gol_eff = named_block(gol_end, "effect")
    require(failures, "ruthenia_region" not in gol_end and "add_permanent_claim" not in gol_eff,
            "ZAZ_GOL_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "alliance_with = GOL" in gol_trig
        and "owns = 283" in gol_trig
        and "kaffa_ransom_exchange" in gol_trig
        and "name = zaz_gol_steppe_compact" in gol_eff,
        "ZAZ_GOL_ruthenia must reward Horde crossings and captive accord",
    )

    ukr_settle = named_block(zaz_missions, "ZAZ_UKR_settle_north_1")
    require(
        failures,
        "development_in_provinces = {" in ukr_settle and "development = 650" not in ukr_settle,
        "ZAZ_UKR_settle_north_1 must use development_in_provinces instead of single-province 650 dev",
    )

    ukr_end = named_block(zaz_missions, "ZAZ_UKR_ruthenia")
    ukr_trig = named_block(ukr_end, "trigger")
    ukr_eff = named_block(ukr_end, "effect")
    require(failures, "ruthenia_region" not in ukr_end and "add_permanent_claim" not in ukr_eff,
            "ZAZ_UKR_ruthenia must not require full Ruthenia conquest or grant Russia permanent claims")
    require(
        failures,
        "is_subject = no" in ukr_trig
        and "owns_core_province = 283" in ukr_trig
        and "calc_true_if" in ukr_trig
        and "amount = 3" in ukr_trig
        and "name = zaz_ukr_unbroken_liberties" in ukr_eff,
        "ZAZ_UKR_ruthenia must require preserving liberties and enduring multi-neighbor pressure",
    )

    # 2. Optional grand-war Russian finale across all three branches
    for prefix in ("ZAZ_POL", "ZAZ_GOL", "ZAZ_UKR"):
        m1 = named_block(zaz_missions, f"{prefix}_russia")
        m2 = named_block(zaz_missions, f"{prefix}_russia_2")
        m3 = named_block(zaz_missions, f"{prefix}_russia_3")
        require(failures, "add_permanent_claim" not in m1 and "add_claim = ROOT" in m1,
                f"{prefix}_russia must grant normal claims only")
        require(
            failures,
            "295 = { country_or_non_sovereign_subject_holds = ROOT }" in normalized(m2)
            and "value = 23" in m2
            and "add_permanent_claim" not in m2
            and "add_claim = ROOT" in m2,
            f"{prefix}_russia_2 must gate full Russia claims behind Moskva (295) + 23 provinces",
        )
        require(failures, "russia_region = {" in m3 and "name = zaz_russia_buff" in m3,
                f"{prefix}_russia_3 must reward completing the optional Russia finale")


def check_hetmanate_missions_and_events(
    failures: list[str], het_missions: str, het_events: str, het_loc: str
) -> None:
    khm = named_block(het_missions, "het_khmelnytsky_uprising")
    khm_trig = named_block(khm, "trigger")
    khm_eff = named_block(khm, "effect")
    require(failures, "has_institution = renaissance" not in khm_trig,
            "het_khmelnytsky_uprising must not unlock on bare Renaissance without military/political trigger")
    require(failures, "ruthenia_region = {" not in khm_eff and "west_dniepr_area = {" in khm_eff,
            "het_khmelnytsky_uprising must scope claims to core Hetmanate areas rather than all Ruthenia")
    require(failures, 'het_khmelnytsky_uprising_title:0 "Uprising of the Host"' in het_loc,
            "het_khmelnytsky_uprising must use general title 'Uprising of the Host'")

    ortho = named_block(het_missions, "het_orthodox_defender")
    ortho_trig = named_block(ortho, "trigger")
    ortho_eff = named_block(ortho, "effect")
    require(failures, "poland_region" not in ortho_eff,
            "het_orthodox_defender must not grant permanent claims on Catholic Poland")
    require(
        failures,
        "het_orthodox_metropolis_pillar_tt" in ortho_trig
        and "het_orthodox_brotherhood_pillar_tt" in ortho_trig
        and "het_orthodox_register_pillar_tt" in ortho_trig
        and "country_event = { id = het_enhanced.9 }" in normalized(ortho_eff),
        "het_orthodox_defender must gate on Metropolis/Brotherhood/Register and fire het_enhanced.9",
    )

    ev9 = event_block(het_events, "het_enhanced.9")
    require(
        failures,
        "is_triggered_only = yes" in ev9
        and "kyiv_orthodox_metropolitanate" in ev9
        and "orthodox_brotherhoods" in ev9
        and "het_registered_cossacks_integrated" in ev9,
        "het_enhanced.9 must offer Metropolis, Brotherhoods, and Register settlement options",
    )

    maz_ren = named_block(het_missions, "het_mazepa_renaissance")
    maz_trig = named_block(maz_ren, "trigger")
    maz_eff = named_block(maz_ren, "effect")
    assert "is_year = 1687" in maz_trig
    assert all("is_year = 1687" not in block for _, block in keyed_blocks(maz_trig, "OR"))
    articles = named_block(het_missions, "het_rozumovsky_reforms")
    assert "is_year = 1710" in named_block(articles, "trigger")
    assert "het_orlyk_constitution" in named_block(articles, "effect")
    require(
        failures,
        ("has_building = university" in maz_trig or "has_building = cathedral" in maz_trig)
        and "country_event = { id = het_enhanced.10 }" in normalized(maz_eff),
        "het_mazepa_renaissance must require collegium/temple patronage and fire het_enhanced.10",
    )

    ev10 = event_block(het_events, "het_enhanced.10")
    require(
        failures,
        "is_triggered_only = yes" in ev10
        and "add_treasury = -200" in ev10
        and "kyiv_mohyla_academy" in ev10
        and "het_kyiv_mazepa_golden_age" in ev10
        and "het_cultural_center" in ev10,
        "het_enhanced.10 must allow tangible funding of collegium or Baroque cathedral",
    )

    ev5 = event_block(het_events, "het_enhanced.5")
    require(
        failures,
        "set_country_flag = mazepa_allied_sweden" in ev5
        and "set_country_flag = mazepa_remained_loyal" in ev5
        and 'name = "het_loyal_hetmanate_charter"' in ev5,
        "het_enhanced.5 must set both mazepa_allied_sweden and mazepa_remained_loyal with charter reward",
    )

    swe = named_block(het_missions, "het_swedish_alliance")
    swe_trig = named_block(swe, "trigger")
    swe_eff = named_block(swe, "effect")
    claims = named_block(swe_eff, "ruthenia_region")
    assert set(re.findall(r"province_id = (\d+)", claims)) == {"280", "1943", "289"}
    assert "russia_region" not in swe_eff and swe_eff.count("add_claim = ROOT") == 1
    require(
        failures,
        "global_trade" not in swe_trig
        and "is_year = 1708" not in swe_trig
        and "age_of_absolutism" not in swe_trig
        and "army_tradition = 80" not in swe_trig,
        "het_swedish_alliance must not allow completing without Swedish or loyalist commitment",
    )
    require(
        failures,
        "has_country_flag = mazepa_allied_sweden" in swe_trig
        and "alliance_with = SWE" in swe_trig
        and "has_country_flag = mazepa_remained_loyal" in swe_trig
        and "het_independence_struggle" in swe_eff
        and "het_loyal_autonomy_accord" in swe_eff,
        "het_swedish_alliance must accept mazepa_allied_sweden/alliance OR loyal course with distinct rewards",
    )


def iter_clausewitz_blocks(text: str) -> list[tuple[str, str]]:
    """Iterate top-level `key = { ... }` blocks in a pre-cleaned Clausewitz slice."""
    cleaned = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    blocks: list[tuple[str, str]] = []
    i = 0
    n = len(cleaned)
    while i < n:
        while i < n and cleaned[i].isspace():
            i += 1
        if i >= n:
            break
        m = re.match(r"([A-Za-z0-9_.\-]+)\s*=\s*\{", cleaned[i:])
        if not m:
            i += 1
            continue
        name = m.group(1)
        start = i + m.end()
        depth = 1
        j = start
        in_quote = False
        while j < n and depth > 0:
            ch = cleaned[j]
            if ch == '"':
                in_quote = not in_quote
            elif not in_quote:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
            j += 1
        blocks.append((name, cleaned[start:j - 1]))
        i = j
    return blocks


def check_zaz_text_labels_and_weights(
    failures: list[str], zaz_missions: str, het_missions: str, zaz_realm_loc: str
) -> None:
    loc_entries = dict(
        re.findall(r'^\s*([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', zaz_realm_loc, re.M)
    )

    # 1. Event text & glossary fixes (Krakow / Wawel, Moscow / Kremlin)
    krakow_d = loc_entries.get("zaz_flavor_m_2.1.d", "")
    require(
        failures,
        "Wawel" in krakow_d
        and "Kraków" in krakow_d
        and "lightly defended" not in krakow_d
        and "weakly held" not in krakow_d,
        "zaz_flavor_m_2.1.d must reflect Kraków/Wawel accurately without calling it a lightly defended fort",
    )

    moscow_t = loc_entries.get("zaz_flavor_m_2.2.t", "")
    moscow_d = loc_entries.get("zaz_flavor_m_2.2.d", "")
    require(
        failures,
        "Moscow" in moscow_t
        and "Moskva" not in moscow_t
        and "Moscow" in moscow_d
        and "Moskva" not in moscow_d
        and "weakly held" not in moscow_d,
        "zaz_flavor_m_2.2.t/.d must use Moscow (not Moskva) without calling it a weakly held fortress",
    )

    # 2. Historical / alternate-history labels on Rada choice missions + Horde fallback
    for mname in ("ZAZ_ally_crimea", "ZAZ_ally_pol", "ZAZ_ally_rus", "ZAZ_ally_tur"):
        eff = named_block(named_block(zaz_missions, mname), "effect")
        require(
            failures,
            "custom_tooltip = zaz_historically_accurate" in eff,
            f"{mname} must display custom_tooltip = zaz_historically_accurate",
        )
    for mname in ("ZAZ_ally_tartar", "ZAZ_only_zaz"):
        eff = named_block(named_block(zaz_missions, mname), "effect")
        require(
            failures,
            "custom_tooltip = zaz_alternate_history" in eff,
            f"{mname} must display custom_tooltip = zaz_alternate_history",
        )
    only_eff = named_block(named_block(zaz_missions, "ZAZ_only_zaz"), "effect")
    require(
        failures,
        "custom_tooltip = zaz_high_difficulty" in only_eff,
        "ZAZ_only_zaz must display custom_tooltip = zaz_high_difficulty",
    )

    tartar = named_block(zaz_missions, "ZAZ_ally_tartar")
    tartar_trig = named_block(tartar, "trigger")
    tartar_eff = named_block(tartar, "effect")
    for tag in ("GOL", "GLH", "AST", "NOG", "KAZ"):
        require(
            failures,
            f"partner = {tag}" in tartar_trig and f"create_alliance = {tag}" in tartar_eff,
            f"ZAZ_ally_tartar must support Horde successor partner {tag}",
        )

    # 3. Branch content weights and 0 claim/CB-only missions
    meta = {"slot", "generic", "ai", "has_country_shield", "potential", "potential_on_load", "ai_weight"}
    entry_branch = {
        "ZAZ_ally_crimea": "zaz_allied_cri",
        "ZAZ_ally_tur": "zaz_allied_tur",
        "ZAZ_ally_tartar": "zaz_allied_gol",
        "ZAZ_only_zaz": "zaz_only_zaz",
        "ZAZ_ally_pol": "zaz_allied_pol",
        "ZAZ_ally_rus": "zaz_allied_rus",
    }
    branch_counts: dict[str, int] = {b: 0 for b in entry_branch.values()}

    substantive_pattern = re.compile(
        r"\b(add_country_modifier|add_province_modifier|add_permanent_province_modifier|"
        r"add_trade_modifier|add_adm_power|add_dip_power|add_mil_power|"
        r"add_prestige|add_legitimacy|add_legitimacy_equivalent|add_republican_tradition|"
        r"add_army_tradition|add_navy_tradition|"
        r"add_army_professionalism|add_stability|add_treasury|add_years_of_income|"
        r"add_manpower|add_yearly_manpower|add_sailors|add_yearly_sailors|"
        r"add_base_tax|add_base_production|add_base_manpower|add_building|add_building_construction|"
        r"add_center_of_trade_level|create_general|define_general|create_admiral|"
        r"add_trust|add_historical_friend|add_historical_rival|add_estate_loyalty|"
        r"add_mercantilism|add_splendor|add_power_projection|add_government_power|"
        r"country_event|create_alliance|change_trade_goods|add_core|add_accepted_culture|"
        r"rip_faith_mission_resource_effect|set_dynasty|add_local_autonomy|"
        r"remove_province_modifier|change_religion|declare_war_with_cb)\b"
    )

    for gname, gbody in iter_clausewitz_blocks(zaz_missions):
        g_subs = dict(iter_clausewitz_blocks(gbody))
        pot = g_subs.get("potential", "")
        pot_flags = re.findall(r"^\s*has_country_flag\s*=\s*(zaz_[a-z_]+)", pot, re.M)
        if not pot_flags and "ZAZ_CRI" in gname or gname == "ZAZ_crimean_diplomacy":
            pot_flags = ["zaz_allied_cri"]
        for mname, mbody in iter_clausewitz_blocks(gbody):
            if mname in meta:
                continue
            bkey = entry_branch.get(mname) or (pot_flags[0] if len(pot_flags) == 1 else None)
            if bkey in branch_counts:
                branch_counts[bkey] += 1
            m_subs = dict(iter_clausewitz_blocks(mbody))
            eff = m_subs.get("effect", "")
            require(
                failures,
                bool(substantive_pattern.search(eff)),
                f"Zaporozhie mission {mname} must not be claim-only or CB-only",
            )

    for gname, gbody in iter_clausewitz_blocks(het_missions):
        for mname, mbody in iter_clausewitz_blocks(gbody):
            if mname in meta:
                continue
            eff = dict(iter_clausewitz_blocks(mbody)).get("effect", "")
            require(
                failures,
                bool(substantive_pattern.search(eff)),
                f"Hetmanate mission {mname} must not be claim-only or CB-only",
            )

    require(
        failures,
        branch_counts["zaz_allied_cri"] >= 20
        and branch_counts["zaz_allied_cri"] > branch_counts["zaz_allied_gol"]
        and branch_counts["zaz_allied_gol"] <= 18
        and branch_counts["zaz_only_zaz"] <= 21
        and branch_counts["zaz_allied_tur"] >= branch_counts["zaz_allied_gol"],
        f"ZAZ branch mission balance inverted: {branch_counts}",
    )


def _mod_stat(modifiers_text: str, mod_name: str, key: str) -> float:
    blk = named_block(modifiers_text, mod_name)
    m = re.search(rf"\b{re.escape(key)}\s*=\s*(-?\d+(?:\.\d+)?)", blk)
    if not m:
        raise AssertionError(f"{mod_name} missing {key}")
    return float(m.group(1))


def check_p1_p2_zaz_het_polish(
    failures: list[str], zaz_missions: str, het_missions: str, zaz_realm_loc: str, het_loc: str
) -> None:
    from clausewitz_testlib import ROOT

    het_mods = read("common/event_modifiers/RIP_HET_modifiers.txt")
    zaz_mods = read("common/event_modifiers/RIP_ZAZ_modifiers.txt")
    east_mods = read("common/event_modifiers/ruthenian_eastward_modifiers.txt")
    het_decs = read("decisions/HetmanateDecisions.txt")

    # a. Orlyk modifier alignment and bounded modifier values
    require(
        failures,
        "het_orlyk_constitution = {" in het_mods
        and "het_orlyk_constitution:0" in het_loc
        and "het_reformed_election_system" in het_decs,
        "het_orlyk_constitution must back Orlyk's Articles while keeping het_reformed_election_system active in decisions",
    )
    require(failures, _mod_stat(zaz_mods, "zaz_army", "land_forcelimit_modifier") <= 0.25, "zaz_army outlier")
    require(failures, _mod_stat(zaz_mods, "zaz_prepped", "local_defensiveness") <= 0.25, "zaz_prepped outlier")
    require(failures, _mod_stat(zaz_mods, "zaz_lit_kill", "movement_speed") <= 0.15, "zaz_lit_kill outlier")
    require(failures, _mod_stat(zaz_mods, "zaz_tur_trade", "embargo_efficiency") <= 0.25, "zaz_tur_trade outlier")
    require(
        failures,
        _mod_stat(east_mods, "khmelnitsky_uprising", "war_exhaustion") >= -0.1
        and _mod_stat(east_mods, "khmelnitsky_uprising", "morale_damage_received") < 0,
        "khmelnitsky_uprising war_exhaustion / morale_damage_received out of bounds",
    )

    # b. Zero donor / hallucinated / Moskva remnants across ZAZ/HET loc (English + replace)
    bad_pat = re.compile(r"(Rightful Khanate|Warrior Clan|Regime of Nomads|love of literature|\bMoskva\b)", re.I)
    loc_paths = [
        ROOT / "localisation/RIP_ZAZ_realm_l_english.yml",
        ROOT / "localisation/RIP_HET_realm_l_english.yml",
        ROOT / "localisation/RIP_ZAZ_HET_missions_l_english.yml",
    ] + [
        ROOT / f"localisation/replace/RIP_{tag}_content_l_{lang}.yml"
        for tag in ("ZAZ", "HET")
        for lang in ("french", "german", "spanish")
    ]
    for p in loc_paths:
        txt = p.read_text(encoding="utf-8-sig")
        require(failures, not bad_pat.search(txt), f"Donor/glossary remnant found in {p.relative_to(ROOT)}")

    # c. Distinct ZAZ vs HET mission titles (zero exact title collisions)
    loc_map: dict[str, str] = {}
    for p in sorted((ROOT / "localisation").glob("*_l_english.yml")):
        for k, v in re.findall(r'^\s*([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', p.read_text(encoding="utf-8-sig"), re.M):
            loc_map[k] = v

    meta = {"slot", "generic", "ai", "has_country_shield", "potential", "potential_on_load", "ai_weight"}
    zaz_names = [
        m for _, gb in iter_clausewitz_blocks(zaz_missions)
        for m, _ in iter_clausewitz_blocks(gb) if m not in meta
    ]
    het_names = [
        m for _, gb in iter_clausewitz_blocks(het_missions)
        for m, _ in iter_clausewitz_blocks(gb) if m not in meta
    ]
    zaz_titles = {loc_map.get(f"{m}_title", "").lower(): m for m in zaz_names if loc_map.get(f"{m}_title")}
    het_titles = {loc_map.get(f"{m}_title", "").lower(): m for m in het_names if loc_map.get(f"{m}_title")}
    collisions = set(zaz_titles) & set(het_titles)
    require(failures, not collisions, f"ZAZ/HET title collisions remain: {sorted(collisions)}")
    require(
        failures,
        loc_map.get("ZAZ_lit_title") != loc_map.get("het_break_polish_yoke_title")
        and loc_map.get("ZAZ_heroic_campaigns_title") != loc_map.get("het_age_of_heroic_campaigns_title"),
        "ZAZ/HET duplicate pairs must stay distinct",
    )

    # d. Doroshenko Crimean mission + modifier + 4-lang loc
    cri_s5 = named_block(zaz_missions, "ZAZ_CRI_missions_5")
    dor = named_block(cri_s5, "ZAZ_CRI_doroshenko_accord")
    require(
        failures,
        "zaz_cri_doroshenko_unification" in dor and "zaz_cri_doroshenko_unification = {" in zaz_mods,
        "ZAZ_CRI_doroshenko_accord must exist in ZAZ_CRI_missions_5 with zaz_cri_doroshenko_unification",
    )
    for k in (
        "ZAZ_CRI_doroshenko_accord_title",
        "ZAZ_CRI_doroshenko_accord_desc",
        "zaz_cri_doroshenko_unification",
        "desc_zaz_cri_doroshenko_unification",
    ):
        require(failures, k in zaz_realm_loc, f"Missing English loc {k}")
        for lang in ("french", "german", "spanish"):
            fb = read(f"localisation/replace/RIP_ZAZ_content_l_{lang}.yml")
            require(failures, f"{k}:0" in fb, f"Missing {lang} replace loc {k}")

    # e. Zero raw legitimacy = triggers or add_legitimacy = effects in HET missions/events/triggers
    het_script_paths = [
        ROOT / "missions/zzz_Hetmanate_Missions.txt",
        ROOT / "common/scripted_triggers/het_government_triggers.txt",
        *sorted((ROOT / "events").glob("RIP_HET_*.txt")),
    ]
    for p in het_script_paths:
        raw = "\n".join(line.split("#", 1)[0] for line in p.read_text(encoding="utf-8").splitlines())
        require(
            failures,
            not re.search(r"\b(?:add_)?legitimacy\s*=", raw),
            f"Raw legitimacy/add_legitimacy remains in {p.relative_to(ROOT)}",
        )


def main() -> int:
    failures: list[str] = []
    zaz_missions = read("missions/Zaporozhie_Missions.txt")
    zaz_events = read("events/RIP_ZAZ_ZAZmission.txt")
    zaz_realm_loc = read("localisation/RIP_ZAZ_realm_l_english.yml")
    het_missions = read("missions/zzz_Hetmanate_Missions.txt")
    het_events = read("events/RIP_HET_HetmanateEnhanced.txt")
    het_loc = read("localisation/RIP_HET_realm_l_english.yml")

    check_preserved_zaz_strengths(failures, zaz_missions, zaz_events)
    check_zaz_branch_victory_and_russia_finale(failures, zaz_missions)
    check_hetmanate_missions_and_events(failures, het_missions, het_events, het_loc)
    check_zaz_text_labels_and_weights(failures, zaz_missions, het_missions, zaz_realm_loc)
    check_p1_p2_zaz_het_polish(failures, zaz_missions, het_missions, zaz_realm_loc, het_loc)

    if failures:
        print("ZAZ/HET mission redesign contract failures:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("ZAZ/HET mission redesign contracts hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
