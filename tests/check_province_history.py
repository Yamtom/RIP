"""Regression tests for RIP history/provinces against installed vanilla EU4.

Verifies timeline monotonicity, core/owner/controller integrity, keyword
standards, diplomatic/event alignment, and planted mutation detection.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools"))

from audit_country_history import read  # noqa: E402
from audit_diplomacy_history import province_tree  # noqa: E402
from audit_province_history import (  # noqa: E402
    audit_province,
    collect_audit,
    load_definitions,
    simulate_province,
)
from clausewitz_testlib import vanilla_root  # noqa: E402


def req(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def verify_live_provinces(vanilla: Path) -> None:
    """Assert zero structural errors and specific alignment contracts across RIP."""
    _, results, errors, _ = collect_audit(vanilla)
    req(not errors, f"Province audit failed with {len(errors)} error(s): {errors}")

    by_id = {r["pid"]: r for r in results}

    # Redundant dead copies removed; required test fixtures retained
    for removed in ("262 - Krakow.txt", "268 - Moldavia.txt"):
        req(not (ROOT / "history/provinces" / removed).exists(), f"Redundant override restored: {removed}")
    for fixture in ("300 - Tula.txt", "301 - Ryazan.txt", "4255 - Pronsk.txt"):
        req((ROOT / "history/provinces" / fixture).exists(), f"Missing compatibility fixture: {fixture}")

    # Expected 1444.11.11 ownership counts for RIP playable/custom anchors
    owners_1444 = [r["rip_1444"]["owner"] for r in results]
    for tag, count in (("HLC", 5), ("VLN", 5), ("KIE", 7), ("CHR", 9), ("ZAZ", 3), ("UZH", 1)):
        actual = owners_1444.count(tag)
        req(actual == count, f"Expected {tag} to own {count} overridden provinces at 1444.11.11, got {actual}")

    # Specific repaired regressions
    req("CRI" not in by_id["291"]["rip_1444"]["cores"], "291 must drop CRI core before 1444.11.11")
    req("CHR" in by_id["291"]["rip_1444"]["cores"], "291 must give CHR a core on 1444.11.11")

    s_1940_1462 = simulate_province(province_tree(by_id["1940"]["rip_text"]), dt.date(1462, 7, 1))
    req(s_1940_1462["owner"] == "POL" and s_1940_1462["controller"] == "POL", "1940 Belz must pass to POL in 1462.7.1")

    for pid in ("2407", "4542"):
        s_1667 = simulate_province(province_tree(by_id[pid]["rip_text"]), dt.date(1667, 1, 30))
        req(s_1667["owner"] == "RUS" and s_1667["controller"] == "RUS", f"{pid} must be controlled by RUS after Andrusovo")

    # ZAZ must stay landed across every diplomatic treaty window 1444.11.11..1775.6.4
    for when in (dt.date(1569, 7, 1), dt.date(1648, 6, 1), dt.date(1734, 6, 1), dt.date(1775, 6, 4)):
        zaz_count = sum(
            1 for r in results
            if simulate_province(province_tree(r["rip_text"]), when)["owner"] == "ZAZ"
        )
        req(zaz_count >= 1, f"ZAZ owns 0 provinces on {when.isoformat()} during active diplomacy")
    s_2406_1775 = simulate_province(province_tree(by_id["2406"]["rip_text"]), dt.date(1775, 6, 5))
    req(s_2406_1775["owner"] == "RUS" and "ZAZ" not in s_2406_1775["cores"], "2406 must liquidate with Sich on 1775.6.5")

    s_1944_1667 = simulate_province(province_tree(by_id["1944"]["rip_text"]), dt.date(1667, 1, 30))
    req("PDL" in s_1944_1667["cores"], "1944 must grant PDL core in 1667.1.30")

    req("rip_uzh_union.1" in by_id["1952"]["rip_text"], "1952 must preserve rip_uzh_union.1 reference comment")
    req(by_id["1952"]["rip_1821"]["religion"] == "orthodox", "1952 must remain Orthodox through 1821")
    req(by_id["2962"]["rip_1444"]["capital"] == "Rivne", "2962 capital must match Rivne spelling")


def verify_planted_mutations(vanilla: Path) -> int:
    """Confirm audit_province rejects planted timeline, core, controller, and syntax bugs."""
    defs = load_definitions(vanilla)
    van_291 = vanilla / "history/provinces/291 - Kharkov.txt"
    van_262 = vanilla / "history/provinces/262 - Krakow.txt"

    base = """
owner = LIT
controller = LIT
culture = ruthenian
religion = orthodox
hre = no
base_tax = 2
base_production = 2
trade_goods = iron
base_manpower = 1
capital = "Test"
is_city = yes
add_core = LIT
1444.11.1 = { owner = CHR controller = CHR add_core = CHR remove_core = LIT }
"""

    planted = [
        ("out-of-order date", base + "1650.1.1 = { unrest = 1 }\n1640.1.1 = { unrest = 0 }\n", "out-of-order date"),
        ("duplicate date", base + "1500.1.1 = { unrest = 1 }\n1500.1.1 = { unrest = 2 }\n", "duplicate dated block"),
        ("post-1821 date", base + "1848.3.15 = { unrest = 4 }\n", "post-1821 date"),
        ("empty block", base + "1600.1.1 = {}\n", "empty dated block"),
        ("deprecated estate", base.replace("is_city = yes\n", "is_city = yes\nestate = estate_cossacks\n"), "deprecated 'estate"),
        ("non-vanilla set_local_autonomy", base + "1500.1.1 = { set_local_autonomy = 25 }\n", "set_local_autonomy"),
        ("permanent add_province_modifier", base + '1500.1.1 = { add_province_modifier = { name = "chr_desna_watch" duration = -1 } }\n', "uses add_province_modifier"),
        ("remove missing core", base + "1500.1.1 = { remove_core = LIT }\n", "when core not active"),
        ("owner lacking core", base.replace("add_core = CHR ", ""), "owner CHR lacks core"),
        ("phantom fort_15th = no", base + "1551.1.1 = { fort_15th = no }\n", "fort_15th = no when fort not present"),
        ("lingering occupier", base + "1500.1.1 = { controller = POL }\n1510.1.1 = { owner = RUS }\n", "lingering controller stays POL"),
    ]

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for label, text, expected_substr in planted:
            p = tmpdir / "291 - Kharkov.txt"
            p.write_text(text, encoding="utf-8")
            res = audit_province("291", "Kharkov", p, van_291, defs)
            req(
                any(expected_substr in err for err in res["errors"]),
                f"Planted mutation '{label}' not caught cleanly; errors={res['errors']}",
            )

        # Zero-diff identical override outside fixture set must fail
        dup = tmpdir / "262 - Krakow.txt"
        dup.write_bytes(van_262.read_bytes())
        res_dup = audit_province("262", "Krakow", dup, van_262, defs)
        req(
            any("zero-diff override" in err for err in res_dup["errors"]),
            f"Planted identical override not caught; errors={res_dup['errors']}",
        )

    return len(planted) + 1


def main() -> None:
    vanilla = vanilla_root()
    if not vanilla:
        raise SystemExit("Set EU4_DIR to an installed EU4 1.37.5 directory")
    v = Path(vanilla)
    verify_live_provinces(v)
    caught = verify_planted_mutations(v)
    print(f"PASS: province histories aligned (0 errors; all {caught} planted violations caught)")


if __name__ == "__main__":
    main()
