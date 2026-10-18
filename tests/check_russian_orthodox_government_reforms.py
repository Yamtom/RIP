"""Regression contracts for Muscovite/Russian government reforms upon adopting ROC (russian_orthodox).

Verifies:
1. Principality (Tier 1 Eastern Slavic Monarchy):
   - potential accepts both orthodox and russian_orthodox.
   - nation_designer_trigger accepts both orthodox and russian_orthodox.
2. Tsardom (Tier 1 Russian Monarchy):
   - potential accepts both orthodox and russian_orthodox.
   - nation_designer_trigger accepts both orthodox and russian_orthodox.
3. Great Veche Republic (Tier 1 Veche Republic):
   - potential accepts both orthodox and russian_orthodox.
   - nation_designer_trigger accepts both orthodox and russian_orthodox.
4. Ecclesiastical reforms (lands_for_the_monasteries_reform, holy_synod_reform,
   strengthened_the_patriarchy_reform, head_of_the_patriarchy_reform, orthodox_patriarchate_reform):
   - All support russian_orthodox.
5. Scripted effect rip_faith_adopt_muscovite_church_effect:
   - Explicitly preserves and re-confirms principality, tsardom, and great_veche_republic
     upon change_religion = russian_orthodox.
"""

from __future__ import annotations

from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, normalized


def test_principality():
    reforms = read("common/government_reforms/RIP_RUS_government_reforms.txt")
    principality = named_block(reforms, "principality")
    assert principality, "principality missing in RIP_RUS_government_reforms.txt"

    potential = normalized(named_block(principality, "potential"))
    assert "religion = russian_orthodox" in potential, "principality potential must include russian_orthodox"
    assert "religion = orthodox" in potential, "principality potential must include orthodox"

    trigger = normalized(named_block(principality, "nation_designer_trigger"))
    assert "religion = russian_orthodox" in trigger, "principality nation_designer_trigger must include russian_orthodox"


def test_tsardom():
    reforms = read("common/government_reforms/RIP_RUS_government_reforms.txt")
    tsardom = named_block(reforms, "tsardom")
    assert tsardom, "tsardom missing in RIP_RUS_government_reforms.txt"

    potential = normalized(named_block(tsardom, "potential"))
    assert "religion = russian_orthodox" in potential, "tsardom potential must include russian_orthodox"
    assert "religion = orthodox" in potential, "tsardom potential must include orthodox"

    trigger = normalized(named_block(tsardom, "nation_designer_trigger"))
    assert "religion = russian_orthodox" in trigger, "tsardom nation_designer_trigger must include russian_orthodox"


def test_great_veche_republic():
    reforms = read("common/government_reforms/RIP_RUS_government_reforms.txt")
    veche = named_block(reforms, "great_veche_republic")
    assert veche, "great_veche_republic missing in RIP_RUS_government_reforms.txt"

    potential = normalized(named_block(veche, "potential"))
    assert "religion = russian_orthodox" in potential, "great_veche_republic potential must include russian_orthodox"
    assert "religion = orthodox" in potential, "great_veche_republic potential must include orthodox"


def test_ecclesiastical_reforms():
    reforms = read("common/government_reforms/RIP_RUS_government_reforms.txt")
    for ref_name in [
        "lands_for_the_monasteries_reform",
        "holy_synod_reform",
        "strengthened_the_patriarchy_reform",
        "head_of_the_patriarchy_reform",
        "orthodox_patriarchate_reform",
    ]:
        block = named_block(reforms, ref_name)
        assert block, f"{ref_name} missing in RIP_RUS_government_reforms.txt"
        norm = normalized(block)
        assert "religion = russian_orthodox" in norm, f"{ref_name} must support russian_orthodox"


def test_adopt_muscovite_church_effect():
    effects = read("common/scripted_effects/rip_religion_settlement_effects.txt")
    effect_block = named_block(effects, "rip_faith_adopt_muscovite_church_effect")
    assert effect_block, "rip_faith_adopt_muscovite_church_effect missing"

    norm = normalized(effect_block)
    assert "change_religion = russian_orthodox" in norm
    assert "has_reform = principality" in norm
    assert "add_government_reform = principality" in norm
    assert "has_reform = tsardom" in norm
    assert "add_government_reform = tsardom" in norm
    assert "has_reform = great_veche_republic" in norm
    assert "add_government_reform = great_veche_republic" in norm


def main():
    test_principality()
    test_tsardom()
    test_great_veche_republic()
    test_ecclesiastical_reforms()
    test_adopt_muscovite_church_effect()
    print("RUSSIAN ORTHODOX GOVERNMENT REFORMS PASS: Muscovy/Russia maintains principality and tsardom upon adopting ROC.")


if __name__ == "__main__":
    main()
