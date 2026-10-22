"""Verify country definitions meet EU4 minimum naming requirements.

Engine requirement:
countrydatabase.cpp logs warnings if a country has less than 10 random ship names
or less than 10 leader names.
"""

from __future__ import annotations

import re
from pathlib import Path

from clausewitz_testlib import ROOT


def parse_names_block(block_text: str) -> list[str]:
    return re.findall(r'"[^"]+"|\S+', block_text)


def audit_countries(country_dir: Path) -> list[str]:
    failures: list[str] = []
    country_files = sorted(country_dir.glob("*.txt"))
    if not country_files:
        failures.append(f"No country files found in {country_dir}")
        return failures

    for path in country_files:
        text = path.read_text(encoding="utf-8", errors="replace")

        # ship_names
        m_ship = re.search(r'ship_names\s*=\s*\{([^}]*)\}', text, re.DOTALL)
        if not m_ship:
            failures.append(f"{path.name}: missing ship_names block")
        else:
            ships = parse_names_block(m_ship.group(1))
            if len(ships) < 10:
                failures.append(f"{path.name}: ship_names has {len(ships)} items (EU4 requires at least 10)")

        # leader_names
        m_leader = re.search(r'leader_names\s*=\s*\{([^}]*)\}', text, re.DOTALL)
        if not m_leader:
            failures.append(f"{path.name}: missing leader_names block")
        else:
            leaders = parse_names_block(m_leader.group(1))
            if len(leaders) < 10:
                failures.append(f"{path.name}: leader_names has {len(leaders)} items (EU4 requires at least 10)")

        # monarch_names
        if not re.search(r'monarch_names\s*=\s*\{', text):
            failures.append(f"{path.name}: missing monarch_names block")

    return failures


def test_mutation() -> None:
    # Verify mutation check trips on mock text with < 10 ship names
    mock_bad = "ship_names = { One Two Three }"
    m = re.search(r'ship_names\s*=\s*\{([^}]*)\}', mock_bad, re.DOTALL)
    assert m is not None
    assert len(parse_names_block(m.group(1))) < 10, "Mutation check failed: expected < 10"


def main() -> int:
    country_dir = ROOT / "common" / "countries"
    failures = audit_countries(country_dir)

    if failures:
        print("Country database naming failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    test_mutation()

    print("COUNTRY DATABASE NAMING PASS: All country files define at least 10 ship names and 10 leader names.")
    print("LIMIT: Static syntax and count checks; runtime random selection tested via engine rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
