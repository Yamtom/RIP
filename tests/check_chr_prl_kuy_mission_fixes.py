"""Static regression checks for CHR, PRL, and KUY mission/modifier fixes (#6-#9).

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
    check_kuy_steppe_granary()
    check_chr_border_compacts_highlight()
    print(
        "CHR/PRL/KUY MISSION FIXES PASS: prl_build_army claims chernigov_area, "
        "prl_orthodox_leadership uses 0.90 unity + religion = ROOT, "
        "kuy_steppe_granary uses trade_goods_size_modifier, "
        "chr_border_compacts highlight wraps 1945/4244 in OR (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
