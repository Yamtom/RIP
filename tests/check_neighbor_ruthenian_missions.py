"""Static contracts for additive Ruthenian-culture / Ruthenia-region neighbor missions.

Verifies that missions/zzzzz_Neighbor_Ruthenian_Missions.txt covers Lithuania
(2 missions), Tatars/Hordes (1), Ottomans/Rum (1), and Poland/Commonwealth (1)
without overriding any of the 9 vanilla mission files or colliding with any
existing vanilla or RIP mission coordinates.

Static only: models EU4 per-slot mission placement; does not run EU4.
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict

from clausewitz_testlib import ROOT, matching_brace, named_block, read, vanilla_read, vanilla_root


VANILLA_FILES = (
    "Lithuanian Missions.txt",
    "SCA_Lithuania_Missions.txt",
    "Tatar_Missions.txt",
    "WoC_Tatar_Missions.txt",
    "zzz_WoC_Shared_Horde_Missions.txt",
    "Ottoman_Missions.txt",
    "DOM_Ottoman_Missions.txt",
    "Polish_Missions.txt",
    "SCA_Polish_Missions.txt",
)

EXPECTED_MISSIONS = {
    "rip_lit_ruthenian_chancery": ("rip_lit_ruthenian_missions", 1, 6),
    "rip_lit_princes_of_rus": ("rip_lit_ruthenian_missions", 1, 7),
    "rip_tatar_dnieper_tribute": ("rip_tatar_ruthenian_missions", 5, 20),
    "rip_tur_podillian_eyalet": ("rip_tur_ruthenian_missions", 5, 17),
    "rip_pol_ruthenian_palatinates": ("rip_pol_ruthenian_missions", 5, 15),
}

EXPECTED_MODIFIERS = (
    "rip_lit_chancery_statutes",
    "rip_lit_ruthenian_pillar",
    "rip_tatar_ruthenian_tribute",
    "rip_tur_kamianets_citadel",
    "rip_tur_northern_protectorate",
    "rip_pol_ruthenian_palatinates_mod",
)

neighbor_missions = read("missions/zzzzz_Neighbor_Ruthenian_Missions.txt")
neighbor_modifiers = read("common/event_modifiers/RIP_neighbor_ruthenian_modifiers.txt")


def parse_series_cells(text: str) -> list[tuple[str, int, str, list[tuple[str, int]]]]:
    clean = re.sub(r"#[^\n]*", "", text)
    out = []
    for match in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", clean):
        s_name = match.group(1)
        body = clean[match.start(): matching_brace(clean, match.end() - 1) + 1]
        slot_m = re.search(r"\bslot\s*=\s*(\d+)", body)
        if not slot_m:
            continue
        slot = int(slot_m.group(1))
        pot_m = re.search(r"\bpotential\s*=\s*\{", body)
        pot = body[pot_m.start(): matching_brace(body, pot_m.end() - 1) + 1] if pot_m else ""
        cur = 0
        missions = []
        for mm in re.finditer(r"(?m)^\t([A-Za-z0-9_]+)\s*=\s*\{", body):
            m_name = mm.group(1)
            if m_name in ("potential", "potential_on_load", "ai_weight"):
                continue
            m_body = body[mm.start(): matching_brace(body, mm.end() - 1) + 1]
            pm = re.search(r"\bposition\s*=\s*(\d+)", m_body)
            pos = int(pm.group(1)) if pm else cur + 1
            cur = max(cur + 1, pos)
            missions.append((m_name, pos))
        out.append((s_name, slot, pot, missions))
    return out


def loc_entries(path: str) -> dict[str, str]:
    return dict(re.findall(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', read(path), re.M))


def check_no_vanilla_overrides() -> None:
    for fn in VANILLA_FILES:
        assert not (ROOT / "missions" / fn).exists(), f"unexpected override of vanilla {fn}"


def check_neighbor_missions() -> None:
    assert "add_permanent_claim" not in neighbor_missions, "neighbor missions must use temporary claims only"
    assert "generic = yes" not in neighbor_missions, "neighbor series must set generic = no"

    series = parse_series_cells(neighbor_missions)
    assert [s[0] for s in series] == [
        "rip_lit_ruthenian_missions",
        "rip_tatar_ruthenian_missions",
        "rip_tur_ruthenian_missions",
        "rip_pol_ruthenian_missions",
    ], [s[0] for s in series]

    found_missions = {}
    for s_name, slot, pot, missions in series:
        s_block = named_block(neighbor_missions, s_name)
        assert "generic = no" in s_block, s_name
        assert slot in (1, 5), (s_name, slot)
        for m_name, pos in missions:
            found_missions[m_name] = (s_name, slot, pos)

    assert found_missions == EXPECTED_MISSIONS, found_missions

    lit_pot = named_block(named_block(neighbor_missions, "rip_lit_ruthenian_missions"), "potential")
    assert "tag = LIT" in lit_pot and "has_dlc" not in lit_pot

    tatar_pot = named_block(named_block(neighbor_missions, "rip_tatar_ruthenian_missions"), "potential")
    for tok in ("has_dlc = \"Winds of Change\"", "is_tatar_nation = yes", "is_mongol_nation = yes",
                "is_moghulistan_nation = yes", "tag = CRI", "tag = GOL", "tag = QAS", "tag = YUA", "tag = MGE"):
        assert tok in tatar_pot, tok

    tur_pot = named_block(named_block(neighbor_missions, "rip_tur_ruthenian_missions"), "potential")
    assert "tag = TUR" in tur_pot and "tag = RUM" in tur_pot and "has_dlc" not in tur_pot

    pol_pot = named_block(named_block(neighbor_missions, "rip_pol_ruthenian_missions"), "potential")
    assert "tag = POL" in pol_pot and "tag = PLC" in pol_pot and "has_dlc" not in pol_pot

    palatinates = named_block(neighbor_missions, "rip_pol_ruthenian_palatinates")
    assert "rip_pol_lviv_charters" in named_block(palatinates, "required_missions")

    # Check non-collision against RIP's existing Poland/Contacts/Diaspora trees.
    pol_re = parse_series_cells(read("missions/zzz_Poland_Commonwealth_Rework.txt"))
    contacts = parse_series_cells(read("missions/zzz_Ruthenian_Contacts.txt"))
    rip_pol_cells = {(slot, pos) for _, slot, _, ms in pol_re + contacts if True for _, pos in ms}
    assert (5, 15) not in rip_pol_cells

    if vanilla_root() is not None:
        # Verify zero coordinate collisions against installed vanilla EU4 1.37 files.
        checks = [
            ("LIT", 1, {6, 7}, ("Lithuanian Missions.txt", "SCA_Lithuania_Missions.txt")),
            ("TATAR", 5, {20}, ("Tatar_Missions.txt", "WoC_Tatar_Missions.txt", "zzz_WoC_Shared_Horde_Missions.txt", "zzzz_WoC_EoC_Yuan_Missions.txt")),
            ("TUR", 5, {17}, ("Ottoman_Missions.txt", "DOM_Ottoman_Missions.txt")),
            ("POL", 5, {15}, ("Polish_Missions.txt", "SCA_Polish_Missions.txt")),
        ]
        for label, target_slot, our_rows, files in checks:
            occupied = set()
            for fn in files:
                txt = vanilla_read(f"missions/{fn}")
                assert txt is not None, fn
                for _, slot, _, ms in parse_series_cells(txt):
                    if slot == target_slot:
                        occupied.update(pos for _, pos in ms)
            overlap = occupied & our_rows
            assert not overlap, (label, target_slot, overlap)


def check_modifiers_and_localisation() -> None:
    for mod in EXPECTED_MODIFIERS:
        named_block(neighbor_modifiers, mod)

    expected_keys = []
    for m in EXPECTED_MISSIONS:
        expected_keys.extend([f"{m}_title", f"{m}_desc"])
    for mod in EXPECTED_MODIFIERS:
        expected_keys.extend([mod, f"desc_{mod}"])

    for lang in ("english", "french", "german", "spanish"):
        entries = loc_entries(f"localisation/RIP_shared_ruthenian_neighbor_missions_l_{lang}.yml")
        for key in expected_keys:
            assert entries.get(key), (lang, key)


def planted(label: str, mutate, check) -> None:
    global neighbor_missions
    saved = neighbor_missions
    try:
        mutate()
        check()
    except AssertionError:
        return
    finally:
        neighbor_missions = saved
    raise SystemExit(f"planted regression not caught: {label}")


def main() -> int:
    check_no_vanilla_overrides()
    check_neighbor_missions()
    check_modifiers_and_localisation()

    def flip_generic() -> None:
        global neighbor_missions
        neighbor_missions = neighbor_missions.replace("generic = no", "generic = yes", 1)

    def collide_lit_row() -> None:
        global neighbor_missions
        neighbor_missions = neighbor_missions.replace("position = 6", "position = 5", 1)

    def leak_perm_claim() -> None:
        global neighbor_missions
        neighbor_missions = neighbor_missions.replace("add_claim = ROOT", "add_permanent_claim = ROOT", 1)

    planted("generic = yes leaks into neighbor series", flip_generic, check_neighbor_missions)
    planted("Lithuania mission collides with SCA row 5", collide_lit_row, check_neighbor_missions)
    planted("add_permanent_claim leaks into neighbor missions", leak_perm_claim, check_neighbor_missions)

    print("PASS: Additive Ruthenian neighbor missions (LIT x2, Tatars/Hordes x1, TUR/RUM x1, POL/PLC x1; static + planted checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
