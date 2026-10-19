"""Execute the small institutional-resolution script subset against edge cases.

The resolutions are the buttons of common/government_mechanics/rip_institutional_resolutions.txt (they used to be a decision
that opened an event). This is not an EU4 runtime emulator or a campaign power measurement. It reads the actual button gates
and effects to catch double payment, a lock that a reform change could reset, and a second resolution slipping in while one
stands, which a brace or numeric snapshot check would miss. The engine's own cooldown token is not modelled: the dated flag
is what the mod relies on, and what is tested here.
"""
from __future__ import annotations

from copy import deepcopy
import json
import re

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read, vanilla_root


def parse(text):
    text = re.sub(r"#.*", "", text)
    tokens = re.findall(r'"[^"\n]*"|[{}=]|[^\s{}=]+', text)
    position = 0

    def block():
        nonlocal position
        result = []
        while position < len(tokens) and tokens[position] != "}":
            key = tokens[position]
            assert tokens[position + 1] == "=", key
            position += 2
            if tokens[position] == "{":
                position += 1
                value = block()
                assert tokens[position] == "}"
                position += 1
            else:
                value = tokens[position]
                position += 1
            result.append((key, value))
        return result

    return dict(block())


TRIGGERS = parse(read("common/scripted_triggers/rip_government_review_triggers.txt"))
EFFECTS = parse(read("common/scripted_effects/rip_government_review_effects.txt"))
MECHANICS = parse(read("common/government_mechanics/rip_institutional_resolutions.txt"))
FAMILIES = {
    # family: (mechanic, a reform that holds it, [(button, power, modifier)])
    "municipal": ("rip_municipal_resolutions_mechanic", "vln_magdeburg_rights",
                  [("charters", "dip", "rip_gov_municipal_charters"), ("accounts", "adm", "rip_gov_municipal_accounts")]),
    "chancery": ("rip_chancery_resolutions_mechanic", "lit_ruthenian_chancery_reform",
                 [("service", "adm", "rip_gov_chancery_service"), ("rights", "dip", "rip_gov_chancery_rights")]),
    "register": ("rip_register_resolutions_mechanic", "het_regimental_system_reform",
                 [("muster", "mil", "rip_gov_register_muster"), ("settlement", "dip", "rip_gov_register_settlement")]),
}


def button(family, choice):
    interactions = dict(dict(MECHANICS[FAMILIES[family][0]])["interactions"])
    return dict(interactions[f"rip_resolution_{family}_{choice}"])


def gate(items, state):
    def condition(key, value):
        if key in TRIGGERS:
            return gate(TRIGGERS[key], state) == (value == "yes")
        if key in ("AND", "custom_trigger_tooltip"):
            return gate(value, state)
        if key == "OR":
            return any(condition(k, v) for k, v in value)
        if key == "NOT":
            return not gate(value, state)
        if key == "tooltip":
            return True
        if key == "has_reform":
            return value in state["reforms"]
        if key == "has_country_modifier":
            return state["modifiers"].get(value, -1) > state["day"]
        if key == "has_country_flag":
            return value in state["flags"]
        if key == "had_country_flag":
            fields = dict(value)
            start = state["flags"].get(fields["flag"])
            return start is not None and state["day"] - start >= int(fields["days"])
        if key == "is_at_war":
            return state["war"] == (value == "yes")
        if key in ("stability", "treasury", "adm_power", "dip_power", "mil_power"):
            return state[key] >= float(value)
        if key in ("adm_power_cost", "dip_power_cost", "mil_power_cost"):
            return state[key[:-5]] >= float(value)
        if key == "always":
            return value == "yes"
        raise AssertionError(f"unsupported gate in tested script: {key}")
    return all(condition(key, value) for key, value in items)


def execute(items, state):
    for key, value in items:
        if key in EFFECTS:
            assert value == "yes"
            execute(EFFECTS[key], state)
        elif key == "if":
            fields = dict(value)
            if gate(fields["limit"], state):
                execute([(k, v) for k, v in value if k != "limit"], state)
        elif key == "set_country_flag":
            state["flags"][value] = state["day"]
        elif key.startswith("add_") and key[4:] in state:
            state[key[4:]] += float(value)
        elif key in ("adm_power_cost", "dip_power_cost", "mil_power_cost"):
            state[key[:-5]] -= float(value)
        elif key == "add_country_modifier":
            fields = dict(value)
            state["modifiers"][fields["name"]] = state["day"] + int(fields["duration"])
        elif key == "remove_country_modifier":
            state["modifiers"].pop(value, None)
        else:
            raise AssertionError(f"unsupported effect in tested script: {key}")


def initial():
    return dict(day=0, war=False, stability=0, treasury=50, adm_power=50,
                dip_power=50, mil_power=50, flags={}, modifiers={},
                reforms={entry[1] for entry in FAMILIES.values()})


def run_scenarios():
    count = 0
    for family, (_, _, choices) in FAMILIES.items():
        for choice, power, modifier in choices:
            spec = button(family, choice)
            state = initial()
            assert gate(spec["trigger"], state), f"{family} {choice} cannot be pressed with everything in hand"
            execute(spec["effect"], state)
            assert state["treasury"] == 0 and state[power + "_power"] == 0, "the price is 50 ducats and 50 of the named power"
            assert set(state["modifiers"]) == {modifier} and set(state["modifiers"].values()) == {3650}
            assert state["flags"] == {"rip_gov_review_recent": 0}
            count += 1
            # While it stands no button of any institution can be pressed, even with money and power in hand.
            state.update(treasury=100, adm_power=100, dip_power=100, mil_power=100)
            for other_family, (_, _, others) in FAMILIES.items():
                for other_choice, _, _ in others:
                    assert not gate(button(other_family, other_choice)["trigger"], state), f"{other_family} {other_choice} stays open during {family} {choice}"
                    count += 1
            # Removal loses the benefit but retains the dated shared term.
            execute(EFFECTS[f"rip_gov_clear_{family}_effect"], state)
            assert not state["modifiers"] and state["flags"] == {"rip_gov_review_recent": 0}
            state["day"] = 3649
            assert not gate(spec["trigger"], state), "the ten-year term ended a day early"
            state["day"] = 3650
            assert gate(spec["trigger"], state), "the ten-year term did not end on its day"
            execute(spec["effect"], state)
            assert state["flags"]["rip_gov_review_recent"] == 3650
            # A government change cannot leave detached benefits after cleanup.
            state["reforms"].clear()
            execute(EFFECTS["rip_gov_review_cleanup_effect"], state)
            assert not state["modifiers"] and state["flags"]
            count += 1
            # Every refusal keeps the button shut and costs nothing.
            for change in (dict(treasury=49), {power + "_power": 49}, dict(reforms=set()), dict(war=True), dict(stability=-1)):
                state = initial()
                state.update(change)
                assert not gate(spec["trigger"], state), f"{family} {choice} opens despite {change}"
                count += 1
    return count


def source_contracts():
    for retired in ("decisions/RIP_InstitutionalReviews.txt", "events/RIP_InstitutionalReviews.txt"):
        assert not (ROOT / retired).exists(), f"{retired} is back: the resolutions are buttons now"
    mechanics = read("common/government_mechanics/rip_institutional_resolutions.txt")
    assert len(re.findall(r"^rip_\w+_resolutions_mechanic = \{", mechanics, re.M)) == 3
    assert len(re.findall(r"^\t\t(rip_resolution_\w+) = \{", mechanics, re.M)) == 6
    assert len(set(re.findall(r"icon = (GFX_\w+)", mechanics))) == 6, "six buttons need six pictures"
    # One engine cooldown token and ten years for all six: the engine greys every button and prints the date.
    assert mechanics.count("cooldown_token = rip_gov_institutional_resolution") == 6 and mechanics.count("cooldown_years = 10") == 6
    reforms = "\n".join(path.read_text(encoding="utf-8-sig") for path in (ROOT / "common/government_reforms").glob("*.txt"))
    cleanups = {
        "vln_magdeburg_rights": "municipal",
        "lit_ruthenian_chancery_reform": "chancery",
        "chr_kanceliaryst_republic_reform": "chancery",
        "het_regimental_system_reform": "register",
        "rip_cossacks_reform": "register",
        "vln_cossack_host_reform": "register",
        "prl_regimental_republic_reform": "register",
    }
    for reform, family in cleanups.items():
        assert f"rip_gov_clear_{family}_effect = yes" in named_block(named_block(reforms, reform), "removed_effect")
        assert FAMILIES[family][0] in named_block(named_block(reforms, reform), "government_abilities"), f"{reform} gives no buttons"
    for key in ("monarch_admin_power", "monarch_military_power", "administrative_efficiency", "all_power_cost"):
        assert not re.search(rf"\b{key}\s*=", normalized(reforms)), f"unbudgeted high-impact modifier: {key}"
    assert "cossacks_mechanic" not in named_block(reforms, "siversk_veche_reform")
    assert "trade_city_reform" not in named_block(reforms, "kyivan_shogunate_reform")
    # Grain production had two multiplicative layers: keep only local goods.
    assert "global_trade_goods_size_modifier" not in named_block(reforms, "chr_grain_directorate_reform")
    grain = named_block(read("common/event_modifiers/RIP_CHR_modifiers.txt"), "chr_grain_directorate_province")
    assert "local_production_efficiency" not in grain


def vanilla_envelopes():
    """Only certify complete comparable base bundles; no weighted power score."""
    installed = vanilla_root()
    if installed is None:
        print("SKIP government numeric comparators: target EU4 1.37 installation unavailable")
        return
    own = "\n".join(p.read_text(encoding="utf-8-sig") for p in (ROOT / "common/government_reforms").glob("*.txt"))
    native = "\n".join(p.read_text(encoding="utf-8-sig") for p in (installed / "common/government_reforms").glob("*.txt"))
    pairs = (
        ("chr_prykaz_tsardom_reform", "tsardom", {"global_unrest": 1}),
        ("rip_cossacks_reform", "cossacks_reform", {}),
        ("assembly_houses_reform", "parliamentary_reform", {"max_absolutism": -5}),
    )
    for reform, comparator, penalties in pairs:
        local = dict(parse(named_block(named_block(own, reform), "modifiers"))["modifiers"])
        base = dict(parse(named_block(named_block(native, comparator), "modifiers"))["modifiers"])
        for key, value in local.items():
            number = float(value)
            if key in penalties:
                assert number == penalties[key]
                continue
            assert key in base, f"extra unbudgeted axis in {reform}: {key}"
            reference = float(base[key])
            assert number * reference >= 0 and abs(number) <= abs(reference) * 1.05
    print("EU4 1.37 base-bundle envelope: PASS (Prykaz/Tsardom M1; Cossacks R1; Assembly/Parliament M6)")


def reform_tiers(governments):
    """Actual registered slots, including the invisible base-reform slot 0."""
    result = {}
    for government, prefix in (("monarchy", "M"), ("republic", "R"),
                               ("theocracy", "Th"), ("tribal", "T"), ("native", "N")):
        body = named_block(governments, government)
        base = re.search(r"\bbasic_reform\s*=\s*([a-z_]+)", normalized(body))
        if base:
            result.setdefault(base[1], set()).add(prefix + "0")
        for number, (_, block) in enumerate(keyed_blocks(named_block(body, "reform_levels"), "reforms"), 1):
            for reform in re.findall(r"[a-z][a-z0-9_]+", normalized(block))[1:]:
                result.setdefault(reform, set()).add(prefix + str(number))
    return result


def comparator_coverage():
    data = json.loads(read("docs/data/government_authenticity_inventory.json"))
    rows = {row["id"]: row for row in data["reforms"]}
    live_ids = set()
    for path in (ROOT / "common/government_reforms").glob("*.txt"):
        live_ids.update(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", path.read_text(encoding="utf-8-sig"), re.M))
    live_ids -= {
        "principality",
        "tsardom",
        "great_veche_republic",
        "lands_for_the_monasteries_reform",
        "holy_synod_reform",
        "strengthened_the_patriarchy_reform",
        "head_of_the_patriarchy_reform",
        "orthodox_patriarchate_reform",
    }
    assert len(rows) == len(data["reforms"]) == 123 and set(rows) == live_ids
    own_tiers = reform_tiers(read("common/governments/00_governments.txt"))
    snapshots = {row["id"]: row for row in data["vanilla_comparators"]}
    installed = vanilla_root()
    native_tiers = None
    native_definitions = set()
    if installed:
        native_tiers = reform_tiers((installed / "common/governments/00_governments.txt").read_text(encoding="utf-8-sig"))
        for path in (installed / "common/government_reforms").glob("*.txt"):
            native_definitions.update(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", path.read_text(encoding="utf-8-sig"), re.M))
    count = 0
    for reform, row in rows.items():
        expected_tiers = own_tiers[reform]
        assert set(row["tiers"]) == set(row["comparator_by_tier"]) == expected_tiers, reform
        assert row["comparator_role"] and row["comparator_role_match"] in ("відповідна", "часткова")
        assert row["quantitative_certified"] == (reform in data["certified_base_bundles"])
        if row["comparator_role_match"] == "часткова":
            assert row.get("comparator_limit"), f"undisclosed partial role match: {reform}"
        for tier, comparators in row["comparator_by_tier"].items():
            assert comparators and len(comparators) == len(set(comparators)), (reform, tier)
            count += 1
            for comparator in comparators:
                assert comparator in snapshots and tier in snapshots[comparator]["tiers"], (reform, tier, comparator)
                if native_tiers is not None:
                    assert comparator in native_definitions and tier in native_tiers.get(comparator, set()), (reform, tier, comparator)
    assert count == 129
    if installed:
        print("GOVERNMENT COMPARATOR COVERAGE: PASS (123 definitions; 129 tier rows verified against installed 1.37)")
    else:
        print("GOVERNMENT COMPARATOR COVERAGE: PASS (123 definitions; 129 saved tier rows); SKIP live vanilla tier check")


def main():
    source_contracts()
    count = run_scenarios()
    vanilla_envelopes()
    comparator_coverage()
    print(f"GOVERNMENT REVIEW CHECK: PASS ({count} payment/lock/refusal cases; six resolution buttons; one shared term)")
    print("Government campaign power <=105% of EU4 1.37.5: NOT CERTIFIED by this source-contract check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
