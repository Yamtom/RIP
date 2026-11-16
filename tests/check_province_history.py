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

    # Left-Bank Cossack Hetmanate (HET) holds Poltava/Pereyaslav/Lubnie/Chernihiv/Novgorod-Siverskyi 1648..1764
    for pid in ("289", "290", "1945", "2407", "4542"):
        s_1667 = simulate_province(province_tree(by_id[pid]["rip_text"]), dt.date(1667, 1, 30))
        req(s_1667["owner"] == "HET" and s_1667["controller"] == "HET", f"{pid} must belong to HET on 1667.1.30")
        s_1764 = simulate_province(province_tree(by_id[pid]["rip_text"]), dt.date(1764, 11, 10))
        req(s_1764["owner"] == "RUS" and s_1764["controller"] == "RUS", f"{pid} must pass to RUS on 1764.11.10")

    # Right Bank 1944 Chyhyryn: HET (1648..1667) -> PDL (1667..1699) -> PLC
    s_1944_1654 = simulate_province(province_tree(by_id["1944"]["rip_text"]), dt.date(1654, 1, 18))
    req(s_1944_1654["owner"] == "HET", "1944 Chyhyryn must belong to HET in 1654")
    s_283_1720 = simulate_province(province_tree(by_id["283"]["rip_text"]), dt.date(1720, 1, 1))
    req(s_283_1720["owner"] == "ZAZ", "283 Zaporozhia must stay ZAZ during Oleshky/Kamianka Ottoman protection")
    s_4706_1778 = simulate_province(province_tree(by_id["4706"]["rip_text"]), dt.date(1778, 1, 1))
    req(s_4706_1778["owner"] == "ZAZ" and s_4706_1778["capital"] == "Dunavets", "4706 Tolcu must represent Danubian Sich from 1778")

    # ZAZ must stay landed across every diplomatic treaty window 1444.11.11..1775.6.4 and 1778..1821
    for when in (dt.date(1569, 7, 1), dt.date(1648, 6, 1), dt.date(1734, 6, 1), dt.date(1775, 6, 4), dt.date(1778, 1, 1)):
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

    # Thematic province additions & historical timeline/name contracts
    req(
        by_id["275"]["rip_1444"]["dev"] == 12 and "PLT" in by_id["275"]["rip_1444"]["cores"],
        "275 Polotsk must carry PLT core and 12 dev (5/5/2)",
    )
    req(
        simulate_province(province_tree(by_id["275"]["rip_text"]), dt.date(1569, 7, 1))["controller"] == "PLC",
        "275 must resolve controller on 1569.7.1 Union of Lublin",
    )
    req(
        "UZH" in by_id["162"]["rip_1444"]["cores"] and by_id["162"]["rip_1444"]["owner"] == "HUN",
        "162 Zemplen must grant UZH core under 1444 HUN",
    )
    req(
        simulate_province(province_tree(by_id["162"]["rip_text"]), dt.date(1626, 1, 1))["controller"] == "HAB",
        "162 must clear 1619 REB controller by 1626.1.1",
    )

    s_1756_1484 = simulate_province(province_tree(by_id["1756"]["rip_text"]), dt.date(1484, 8, 5))
    req(
        simulate_province(province_tree(by_id["1756"]["rip_text"]), dt.date(1484, 8, 4))["owner"] == "MOL"
        and s_1756_1484["owner"] == "TUR"
        and s_1756_1484["capital"] == "Akkerman",
        "1756 Budjak must fall to TUR on 1484.8.5 with Akkerman capital",
    )
    s_2405_1538 = simulate_province(province_tree(by_id["2405"]["rip_text"]), dt.date(1538, 9, 1))
    req(
        by_id["2405"]["rip_1444"]["capital"] == "Tighina"
        and s_2405_1538["owner"] == "TUR"
        and s_2405_1538["capital"] == "Bender",
        "2405 must start as Tighina and pass to TUR as Bender on 1538.9.1",
    )

    req(
        by_id["1974"]["rip_1444"]["capital"] == "Islam-Kermen"
        and by_id["1974"]["rip_1444"]["dev"] == 8
        and by_id["1974"]["rip_1821"]["capital"] == "Kherson"
        and by_id["1974"]["rip_1821"]["culture"] == "ruthenian",
        "1974 Yedishkul must fix anachronistic 1444 Kherson capital and post-1783 state",
    )
    s_2411_1739 = simulate_province(province_tree(by_id["2411"]["rip_text"]), dt.date(1739, 9, 29))
    req(
        s_2411_1739["owner"] == "ZAZ" and s_2411_1739["capital"] == "Kodak"
        and by_id["2411"]["rip_1821"]["capital"] == "Ekaterinoslav",
        "2411 Mansur must track Kodak/Nova Sich before 1775 liquidation and 1776 Ekaterinoslav",
    )
    req(
        by_id["2412"]["rip_1444"]["dev"] == 8
        and by_id["2412"]["rip_1821"]["capital"] == "Mariupol"
        and by_id["2412"]["rip_1821"]["religion"] == "orthodox",
        "2412 Kyzyl-Yar must rebalance steppe dev to 8 and transition to Orthodox Mariupol",
    )
    req(
        by_id["2409"]["rip_1821"]["culture"] == "ruthenian" and by_id["2409"]["rip_1821"]["religion"] == "orthodox",
        "2409 Bahmut must reflect Sloboda Orthodox Ruthenian settlement after 1676",
    )
    req(
        by_id["288"]["rip_1444"]["capital"] == "Bela Vezha" and by_id["288"]["rip_1821"]["capital"] == "Novocherkassk",
        "288 Cherkassk must avoid anachronistic 1444 name and track Don Host capitals",
    )
    req(
        by_id["286"]["rip_1821"]["culture"] == "crimean" and "ZAZ" not in by_id["286"]["rip_1821"]["cores"],
        "286 Azow must avoid anachronistic 1774 Russification and drop ZAZ core at 1775 liquidation",
    )
    req(
        by_id["287"]["rip_1444"]["capital"] == "Qopil"
        and simulate_province(province_tree(by_id["287"]["rip_text"]), dt.date(1783, 4, 7))["owner"] == "CRI"
        and by_id["287"]["rip_1821"]["capital"] == "Ekaterinodar"
        and by_id["287"]["rip_1821"]["culture"] == "ruthenian",
        "287 Kouban must defer Russian annexation to 1783 and reflect Black Sea Cossack Kuban",
    )
    req(
        by_id["2413"]["rip_1821"]["culture"] == "crimean" and by_id["2413"]["rip_1821"]["capital"] == "Rostov",
        "2413 Tyn must avoid ahistorical 1593 Lower Don Russification while tracking 1761 Rostov",
    )
    req(
        by_id["2414"]["rip_1444"]["dev"] == 8
        and simulate_province(province_tree(by_id["2414"]["rip_text"]), dt.date(1783, 4, 7))["owner"] == "CRI"
        and by_id["2414"]["rip_1821"]["culture"] == "ruthenian",
        "2414 Azaraba must align steppe dev to 8, annex in 1783, and settle Black Sea Cossacks in 1793",
    )
    req(
        by_id["2410"]["rip_1444"]["capital"] == "Mangup"
        and by_id["2410"]["rip_1821"]["capital"] == "Sevastopol"
        and by_id["2410"]["rip_1821"]["culture"] == "goths",
        "2410 Theodoro must fix Mangul typo to Mangup, preserve goths culture, and avoid 1783 Russification",
    )
    req(
        by_id["2447"]["rip_1821"]["capital"] == "Taman" and by_id["2447"]["rip_1821"]["culture"] == "ruthenian",
        "2447 Mantrega must record 1792.8.25 Black Sea Cossack landing at Taman",
    )


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
