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

    print(
        f"PODILLIA MISSIONS PASS: {checked_counters} area-bounded province counters satisfiable on EU4 map, "
        "PDL_podillian_granaries accepts grain/livestock, PDL_fortify_podillia claims Bendery (2405), "
        "and PDL_khotyn_siege models the 1621 joint war/coalition campaign."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
