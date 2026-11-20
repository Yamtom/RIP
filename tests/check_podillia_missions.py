"""Static reachability and geography contracts for Podillia's mission tree."""

from __future__ import annotations

import re
from pathlib import Path

from clausewitz_testlib import (
    ROOT,
    keyed_blocks,
    named_block,
    normalized,
    read,
    vanilla_read,
    vanilla_root,
)

# Fallback EU4 1.37 province lists used only when a local vanilla install is absent.
FALLBACK_AREAS: dict[str, set[int]] = {
    "podolia_volhynia_area": {281, 1943, 4540},
    "red_ruthenia_area": {261, 1940, 2424, 2961, 4541},
    "volhynia_area": {279, 2962, 4538, 4539},
    "west_dniepr_area": {280, 1942, 1944, 4247},
    "east_dniepr_area": {290, 2407, 4542},
    "moldavia_area": {268, 1756, 2405, 4529, 4530},
    "yedisan_area": {282, 1974, 2406},
}


def load_areas() -> dict[str, set[int]]:
    area_text = None
    mod_area = ROOT / "map" / "area.txt"
    if mod_area.is_file():
        area_text = mod_area.read_text(encoding="latin-1", errors="replace")
    else:
        area_text = vanilla_read("map/area.txt")
    if not area_text:
        return dict(FALLBACK_AREAS)

    areas: dict[str, set[int]] = {}
    cleaned = re.sub(r"#[^\n]*", "", area_text)
    for match in re.finditer(r"(?m)^\s*([a-z0-9_]+_area)\s*=\s*\{([^}]*)\}", cleaned):
        areas[match.group(1)] = {int(pid) for pid in re.findall(r"\b\d+\b", match.group(2))}
    return areas


def initial_trade_good(pid: int) -> str | None:
    """Return the 1444 base trade_goods value from mod history (falling back to vanilla)."""
    candidates: list[Path] = []
    for base in (ROOT / "history" / "provinces",):
        candidates.extend(sorted(base.glob(f"{pid} -*")))
        candidates.extend(sorted(base.glob(f"{pid}-*")))
    vroot = vanilla_root()
    if not candidates and vroot is not None:
        vdir = vroot / "history" / "provinces"
        candidates.extend(sorted(vdir.glob(f"{pid} -*")))
        candidates.extend(sorted(vdir.glob(f"{pid}-*")))
    if not candidates:
        return None
    text = re.sub(r"#[^\n]*", "", candidates[0].read_text(encoding="latin-1", errors="replace"))
    # Strip dated history blocks so we inspect only the 1444 baseline goods.
    top_level = re.split(r"(?m)^\s*\d{4}\.\d+\.\d+\s*=\s*\{", text, maxsplit=1)[0]
    match = re.search(r"\btrade_goods\s*=\s*([a-z_]+)\b", top_level)
    return match.group(1) if match else None


def main() -> int:
    source = read("missions/Podillia_Missions.txt")
    areas = load_areas()

    # The opening mission cannot require the estate that later steppe conquests unlock.
    recruit = named_block(source, "PDL_recruit_cossacks")
    recruit_trigger = named_block(recruit, "trigger")
    estate_branch = normalized(named_block(recruit_trigger, "if"))
    local_branch = normalized(named_block(recruit_trigger, "else"))
    assert "limit = { has_estate = estate_cossacks }" in estate_branch
    assert "loyalty = 40" in estate_branch
    assert "owns = 281" in local_branch and "mil_power = 50" in local_branch
    assert "has_dlc" not in local_branch and "terrain" not in local_branch and "has_estate" not in local_branch
    assert "stability = 1" in local_branch
    recruit_effect = normalized(named_block(recruit, "effect"))
    assert "limit = { NOT = { has_estate = estate_cossacks } } add_mil_power = -50" in recruit_effect
    assert "set_country_flag = pdl_cossack_recruited" in recruit_effect

    # Vanilla countrymissionsview.gui exposes only five horizontal slots.
    # Additional series in the same slot stack below earlier series.
    cursors = {}
    cells = set()
    placed = {}
    for tree_name in re.findall(r"(?m)^(PDL_\w+)\s*=\s*\{", source):
        tree = named_block(source, tree_name)
        slot = int(re.search(r"\bslot\s*=\s*(\d+)", tree)[1])
        assert 1 <= slot <= 5, f"{tree_name}: outside vanilla mission UI"
        cursor = cursors.get(slot, 0)
        for mission_name in re.findall(r"(?m)^\t(PDL_\w+)\s*=\s*\{", tree):
            mission = named_block(tree, mission_name)
            row = max(cursor + 1, int(re.search(r"\bposition\s*=\s*(\d+)", mission)[1]))
            assert (slot, row) not in cells
            cells.add((slot, row))
            placed[mission_name] = (slot, row)
            cursor = row
        cursors[slot] = cursor
    assert placed["PDL_galician_compact"] == (2, 5)
    assert placed["PDL_trade_corridor"] == (2, 6)
    assert placed["PDL_khotyn_siege"] == (4, 5)
    early_fort = named_block(named_block(source, "PDL_khotyn_fortress"), "trigger")
    for fort in ("fort_15th", "fort_16th", "fort_17th", "fort_18th"):
        assert fort in early_fort, "Early Dniester mission must accept medieval and upgraded forts"

    # 1. No Pomeranian Stargard (4749) claim or placeholder anywhere in Podillia missions.
    assert not re.search(r"\b4749\b", source), "4749 (Stargard in Pomerania) must not appear in Podillia_Missions.txt"

    fortify = named_block(source, "PDL_fortify_podillia")
    fortify_effect = normalized(named_block(fortify, "effect"))
    assert "2405 = {" in fortify_effect and "add_permanent_claim = ROOT" in fortify_effect, (
        "PDL_fortify_podillia should claim 2405 (Bendery) across the Dniester"
    )

    # 2. Every area-bounded num_of_owned_provinces_with in Podillia_Missions.txt must be satisfiable on the map.
    checked_counters = 0
    for mission_name in ("PDL_withstand_ottoman_threat", "PDL_podillian_granaries", "PDL_magnate_sejm"):
        mission = named_block(source, mission_name)
        trigger = named_block(mission, "trigger")
        highlight = named_block(mission, "provinces_to_highlight")
        counters = [blk for _, blk in keyed_blocks(trigger, "num_of_owned_provinces_with")]
        assert len(counters) == 1, f"{mission_name}: expected one num_of_owned_provinces_with block"
        counter = counters[0]
        checked_counters += 1

        value_match = re.search(r"\bvalue\s*=\s*(\d+)\b", counter)
        assert value_match, f"{mission_name}: missing numeric value"
        required = int(value_match.group(1))

        trigger_areas = re.findall(r"\barea\s*=\s*([a-z0-9_]+_area)\b", counter)
        highlight_areas = re.findall(r"\barea\s*=\s*([a-z0-9_]+_area)\b", highlight)
        assert trigger_areas, f"{mission_name}: expected area constraints"
        assert set(trigger_areas) == set(highlight_areas), (
            f"{mission_name}: provinces_to_highlight areas {highlight_areas} != trigger areas {trigger_areas}"
        )

        provinces: set[int] = set()
        for area in trigger_areas:
            assert area in areas, f"{mission_name}: unknown area {area}"
            provinces |= areas[area]
        assert len(provinces) >= required, (
            f"{mission_name}: requires {required} provinces but {trigger_areas} only have {len(provinces)}"
        )

        goods = set(re.findall(r"\btrade_goods\s*=\s*([a-z_]+)\b", counter))
        if goods:
            qualifying = [pid for pid in sorted(provinces) if initial_trade_good(pid) in goods]
            assert len(qualifying) >= required, (
                f"{mission_name}: requires {required} provinces with {sorted(goods)}, "
                f"but only {len(qualifying)} exist in {trigger_areas}: {qualifying}"
            )

    # 3. Agrarian mission explicitly supports both grain and livestock (since Podillia starts with livestock).
    granaries_trigger = normalized(named_block(named_block(source, "PDL_podillian_granaries"), "trigger"))
    assert "trade_goods = grain" in granaries_trigger and "trade_goods = livestock" in granaries_trigger, (
        "PDL_podillian_granaries must accept both grain and livestock"
    )

    # 4. Khotyn campaign requires actual war/battle defense, Cossack muster, and coalition, and fires podillia_events.11.
    khotyn = named_block(source, "PDL_khotyn_siege")
    khotyn_trigger = normalized(named_block(khotyn, "trigger"))
    khotyn_effect = normalized(named_block(khotyn, "effect"))
    assert "has_country_flag = pdl_repelled_ottoman_assault" in khotyn_trigger, (
        "PDL_khotyn_siege must track real Ottoman battle/war defense"
    )
    assert "war_with = TUR" in khotyn_trigger and "war_score_against" in khotyn_trigger, (
        "PDL_khotyn_siege must allow completion during a successful Ottoman war"
    )
    assert "alliance_with = ZAZ" in khotyn_trigger and "has_estate = estate_cossacks" in khotyn_trigger, (
        "PDL_khotyn_siege must reflect the Cossack muster of 1621"
    )
    assert "alliance_with = POL" in khotyn_trigger and "alliance_with = PLC" in khotyn_trigger, (
        "PDL_khotyn_siege must reflect the Polish-Lithuanian / regional coalition of 1621"
    )
    for fort in ("fort_16th", "fort_17th", "fort_18th"):
        assert fort in khotyn_trigger, f"PDL_khotyn_siege must accept {fort}"
    assert "country_event = { id = podillia_events.11 }" in khotyn_effect, (
        "PDL_khotyn_siege must fire podillia_events.11"
    )

    on_actions = normalized(read("common/on_actions/RIP_PDL_on_actions.txt"))
    assert "on_battle_won_country = {" in on_actions and "on_war_won = {" in on_actions
    assert "set_country_flag = pdl_repelled_ottoman_assault" in on_actions

    # 5. Kamianets urban missions have distinct citadel vs market specializations (no duplicate slot-fill / +6 dev).
    citadel = normalized(named_block(source, "PDL_kamianets_capital"))
    market = normalized(named_block(source, "PDL_kamianets_development"))
    assert "num_free_building_slots" not in citadel and "num_free_building_slots" not in market
    assert "has_building = barracks" in citadel and "name = pdl_kamianets_citadel" in citadel
    assert "has_building = marketplace" in market and "has_building = workshop" in market

    # 6. Host assembly introduces real steppe territory, Cossack loyalty, and estate land-share bargain.
    host = normalized(named_block(source, "PDL_host_assembly"))
    assert "area = yedisan_area" in host and "army_tradition = 30" in host
    assert "estate_loyalty = { estate = estate_cossacks loyalty = 60 }" in host
    assert "change_estate_land_share = { estate = estate_cossacks share = 5 }" in host

    # 7. Magnate Sejm is an estate bargain firing podillia_events.13, not bare prestige.
    sejm = normalized(named_block(source, "PDL_magnate_sejm"))
    assert "estate_loyalty = { estate = estate_nobles loyalty = 60 }" in sejm
    assert "country_event = { id = podillia_events.13 }" in sejm
    pdl_events = read("events/RIP_PDL_Podillia_Events.txt")
    sejm_ev = next(
        normalized(b)
        for _, b in keyed_blocks(pdl_events, "country_event")
        if "title = podillia_events.13.t" in b
    )
    assert "name = pdl_magnate_sejm_compact" in sejm_ev and "name = pdl_crown_sejm_statutes" in sejm_ev
    assert "change_estate_land_share" in sejm_ev

    # 8. Tolerance branch tests real tolerance/multi-confessional coexistence and rewards tolerance modifiers.
    tol = normalized(named_block(source, "PDL_religious_tolerance"))
    jewish = normalized(named_block(source, "PDL_jewish_communities"))
    equil = normalized(named_block(source, "PDL_confessional_equilibrium"))
    ren = normalized(named_block(source, "PDL_cultural_renaissance"))
    assert "has_building = temple" not in tol
    assert "which = tolerance_heretic value = 1" in tol and "name = pdl_tolerance_edict" in tol
    assert "name = pdl_kahal_town_charters" in jewish and "name = jewish_merchant_charters" in jewish
    assert "religion = orthodox value = 5" not in equil
    assert "NOT = { religion = ROOT }" in equil and "which = tolerance_heretic value = 2" in equil
    assert "name = pdl_confessional_equilibrium_modifier" in equil
    assert "name = pdl_pluralist_renaissance" in ren

    # 8b. PDL_khotyn_fortress avoids fort_17th softlock, guards barracks, and creates a level 1 CoT.
    khotyn_fort = named_block(source, "PDL_khotyn_fortress")
    khotyn_fort_trig = normalized(named_block(khotyn_fort, "trigger"))
    khotyn_fort_eff = normalized(named_block(khotyn_fort, "effect"))
    for token in ("fort_15th", "fort_16th", "fort_17th", "fort_18th"):
        assert token in khotyn_fort_trig, f"PDL_khotyn_fortress trigger missing {token}"
    assert "NOT = { has_building = barracks } NOT = { has_building = training_fields }" in khotyn_fort_eff
    assert "center_of_trade = 1" in khotyn_fort_eff

    # 9. Mission titles must fit EU4's 2-line mission scroll banner (vic_18, maxWidth 90).
    vanilla = vanilla_root()
    if vanilla and (vanilla / "gfx/fonts/vic_18.fnt").is_file():
        fnt = (vanilla / "gfx/fonts/vic_18.fnt").read_text(encoding="latin-1")
        adv = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"char\s+id=(\d+).*?xadvance=(-?\d+)", fnt)}
        sp = adv.get(32, 4)

        def wrap_metrics(title: str, max_w: int) -> tuple[int, int]:
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

        en_titles = dict(
            re.findall(r'^ ([A-Za-z0-9_.\-]+_title):\d+\s+"(.*)"\s*$', read("localisation/RIP_PDL_realm_l_english.yml"), re.M)
        )
        pdl_missions = [
            m.group(1)
            for m in re.finditer(r"(?m)^\t([A-Za-z0-9_]+)\s*=\s*\{", re.sub(r"#.*", "", source))
            if m.group(1) not in ("potential", "potential_on_load")
        ]
        for mname in pdl_missions:
            title = en_titles[f"{mname}_title"]
            assert title == title.strip() and "\\n" not in title, (mname, title)
            n84, w84 = wrap_metrics(title, 84)
            n90, w90 = wrap_metrics(title, 90)
            assert n84 <= 2 and n90 <= 2 and w84 <= 84 and w90 <= 90, (mname, title, n84, w84, n90, w90)

    print(
        f"PODILLIA MISSIONS PASS: {checked_counters} area-bounded province counters satisfiable on EU4 map, "
        "PDL_podillian_granaries accepts grain/livestock, PDL_fortify_podillia claims Bendery (2405), "
        "PDL_khotyn_siege models 1621, urban/Sejm/Host pacing, 2-line titles and real tolerance contracts hold."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
