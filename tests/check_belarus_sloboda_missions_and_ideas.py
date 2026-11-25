"""Regression gate for VLN/HET idea rebalance and Belarus/Sloboda mission trees."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))


def _read_text(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8-sig")


def _extract_loc_keys(rel_path: str) -> set[str]:
    keys: set[str] = set()
    for line in _read_text(rel_path).splitlines():
        m = re.match(r"^\s+([A-Za-z0-9_.-]+):\d+\s+\"", line)
        if m:
            keys.add(m.group(1))
    return keys


def _count_idea_modifiers(rel_path: str) -> tuple[int, dict[str, list[float]]]:
    txt = _read_text(rel_path)
    total = 0
    vals: dict[str, list[float]] = {}
    depth = 0
    for raw in txt.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        opens = line.count("{")
        closes = line.count("}")
        # Modifier assignments occur inside depth == 2 (traditions, bonus, 7 ideas)
        if depth == 2 and "=" in line and "{" not in line:
            k, v = [p.strip() for p in line.split("=", 1)]
            total += 1
            try:
                vals.setdefault(k, []).append(float(v))
            except ValueError:
                pass
        depth += opens - closes
    return total, vals


def test_vln_and_het_idea_caps() -> None:
    vln_count, vln_vals = _count_idea_modifiers("common/ideas/01_vln_ideas.txt")
    assert 11 <= vln_count <= 19, f"VLN modifier count {vln_count} outside 11-19"
    assert max(vln_vals.get("discipline", [0.0])) <= 0.05, vln_vals["discipline"]
    assert max(vln_vals.get("administrative_efficiency", [0.0])) <= 0.05, vln_vals[
        "administrative_efficiency"
    ]

    het_count, het_vals = _count_idea_modifiers("common/ideas/01_het_ideas.txt")
    assert 11 <= het_count <= 19, f"HET modifier count {het_count} outside 11-19"
    assert max(het_vals.get("administrative_efficiency", [0.0])) <= 0.05, het_vals[
        "administrative_efficiency"
    ]
    assert max(het_vals.get("discipline", [0.0])) <= 0.05, het_vals["discipline"]


def _extract_mission_ids(txt: str) -> list[str]:
    return [
        m
        for m in re.findall(r"^\t([a-z0-9_]+)\s*=\s*\{", txt, re.M)
        if m not in {"potential", "ai_weight"}
    ]


def test_belarus_mission_tree() -> None:
    txt = _read_text("missions/Belarus_Missions.txt")
    assert not re.search(r"\btag\s*=\s*PLT\b", txt), "Belarus_Missions.txt must not target PLT"
    assert "add_permanent_claim" not in txt, "Belarus missions must use temporary claims"
    for required_tag in ("VTB", "MSK", "MSL", "BLR"):
        assert re.search(rf"\btag\s*=\s*{required_tag}\b", txt), required_tag

    positions = [int(m) for m in re.findall(r"^\s*position\s*=\s*(\d+)", txt, re.M)]
    assert positions and max(positions) < 24, positions

    missions = _extract_mission_ids(txt)
    assert len(missions) == 28, len(missions)

    loc_files = [
        "localisation/RIP_shared_belarus_affairs_l_english.yml",
        "localisation/replace/RIP_shared_belarus_content_l_french.yml",
        "localisation/replace/RIP_shared_belarus_content_l_german.yml",
        "localisation/replace/RIP_shared_belarus_content_l_spanish.yml",
    ]
    for lf in loc_files:
        keys = _extract_loc_keys(lf)
        missing = [
            f"{m}_{suffix}"
            for m in missions
            for suffix in ("title", "desc")
            if f"{m}_{suffix}" not in keys
        ]
        assert not missing, f"{lf} missing mission keys: {missing[:10]}"

    new_mods = re.findall(r"\b(blr_[a-z0-9_]+)\b", txt)
    # Filter to modifiers (exclude mission keys starting with blr_minor_ / blr_podlasie_ etc.)
    mod_txt = _read_text("common/event_modifiers/RIP_BELARUS_modifiers.txt")
    defined_mods = set(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", mod_txt, re.M))
    used_mods = set(re.findall(r"\bname\s*=\s*([a-z0-9_]+)", txt))
    assert used_mods <= defined_mods, sorted(used_mods - defined_mods)
    for lf in loc_files:
        keys = _extract_loc_keys(lf)
        missing_mods = [
            k for m in used_mods for k in (m, f"desc_{m}") if k not in keys
        ]
        assert not missing_mods, f"{lf} missing modifier loc: {missing_mods[:10]}"


def test_sloboda_mission_tree() -> None:
    txt = _read_text("missions/Sloboda_Missions.txt")
    assert "add_permanent_claim" not in txt, "Sloboda missions must use temporary claims"
    for required_tag in ("SMY", "OKH", "IZM", "KHK"):
        assert re.search(rf"\btag\s*=\s*{required_tag}\b", txt), required_tag

    positions = [int(m) for m in re.findall(r"^\s*position\s*=\s*(\d+)", txt, re.M)]
    assert positions and max(positions) < 24, positions

    missions = _extract_mission_ids(txt)
    assert len(missions) == 19, len(missions)

    loc_files = [
        "localisation/RIP_shared_cossack_hosts_l_english.yml",
        "localisation/replace/RIP_shared_cossack_content_l_french.yml",
        "localisation/replace/RIP_shared_cossack_content_l_german.yml",
        "localisation/replace/RIP_shared_cossack_content_l_spanish.yml",
    ]
    for lf in loc_files:
        keys = _extract_loc_keys(lf)
        missing = [
            f"{m}_{suffix}"
            for m in missions
            for suffix in ("title", "desc")
            if f"{m}_{suffix}" not in keys
        ]
        assert not missing, f"{lf} missing mission keys: {missing[:10]}"

    mod_txt = _read_text("common/event_modifiers/cossack_host_modifiers.txt")
    defined_mods = set(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", mod_txt, re.M))
    used_mods = set(re.findall(r"\bname\s*=\s*([a-z0-9_]+)", txt))
    assert used_mods <= defined_mods, sorted(used_mods - defined_mods)
    for lf in loc_files:
        keys = _extract_loc_keys(lf)
        missing_mods = [
            k for m in used_mods for k in (m, f"desc_{m}") if k not in keys
        ]
        assert not missing_mods, f"{lf} missing modifier loc: {missing_mods[:10]}"


if __name__ == "__main__":
    test_vln_and_het_idea_caps()
    test_belarus_mission_tree()
    test_sloboda_mission_tree()
    print("OK: VLN/HET ideas and Belarus/Sloboda mission trees passed.")
