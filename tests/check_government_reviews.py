"""Execute the small institutional-review script subset against edge cases.

This is not an EU4 runtime emulator or a campaign power measurement. It reads
the actual gates/effects to catch double payment, stale event and cooldown
regressions that a brace or numeric snapshot check would miss.
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
FAMILIES = {
    "municipal": ("vln_magdeburg_rights", ("charters", "dip"), ("accounts", "adm")),
    "chancery": ("lit_ruthenian_chancery_reform", ("service", "adm"), ("rights", "dip")),
    "register": ("het_regimental_system_reform", ("muster", "mil"), ("settlement", "dip")),
}


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
                reforms={entry[0] for entry in FAMILIES.values()})


def run_scenarios():
    count = 0
    for family, (_, *choices) in FAMILIES.items():
        for choice, power in choices:
            effect = EFFECTS[f"rip_gov_{family}_{choice}_effect"]
            state = initial()
            execute(effect, state)
            assert state["treasury"] == 0 and state[power + "_power"] == 0
            assert len(state["modifiers"]) == 1
            assert set(state["modifiers"].values()) == {3650}
            paid = deepcopy(state)
            execute(effect, state)
            assert state == paid, "queued option charged twice"
            state.update(treasury=100, adm_power=100, dip_power=100, mil_power=100)
            for other in FAMILIES:
                assert not gate(TRIGGERS[f"rip_gov_can_review_{other}"], state)
            # Removal loses the benefit but retains the dated shared term.
            execute(EFFECTS[f"rip_gov_clear_{family}_effect"], state)
            assert not state["modifiers"] and state["flags"] == {"rip_gov_review_recent": 0}
            state["day"] = 3649
            assert not gate(TRIGGERS[f"rip_gov_can_review_{family}"], state)
            state["day"] = 3650
            assert gate(TRIGGERS[f"rip_gov_can_review_{family}"], state)
            execute(effect, state)
            assert state["flags"]["rip_gov_review_recent"] == 3650
            # A government change cannot leave detached benefits after cleanup.
            state["reforms"].clear()
            execute(EFFECTS["rip_gov_review_cleanup_effect"], state)
            assert not state["modifiers"] and state["flags"]
            count += 1
            for change in (dict(treasury=49), {power + "_power": 49},
                           dict(reforms=set()), dict(war=True), dict(stability=-1)):
                state = initial()
                state.update(change)
                before = deepcopy(state)
                execute(effect, state)
                assert state == before, f"stale/invalid event paid: {family} {change}"
                count += 1
    return count


def source_contracts():
    decisions = parse(read("decisions/RIP_InstitutionalReviews.txt"))["country_decisions"]
    events = read("events/RIP_InstitutionalReviews.txt")
    assert len(decisions) == 3
    assert len(re.findall(r"^country_event =", events, re.M)) == 3
    assert len(re.findall(r"is_triggered_only = yes", events)) == 3
    for number, family in enumerate(FAMILIES, 1):
        body = named_block(read("decisions/RIP_InstitutionalReviews.txt"), f"rip_gov_review_{family}")
        assert f"id = rip_gov_review.{number}" in body
        assert f"limit = {{ rip_gov_can_review_{family} = yes }}" in body
    # Cancellation is always visible, empty and cannot mint monarch power.
    parsed_events = re.findall(r"option = \{\s*name = rip_gov_review.cancel([\s\S]*?)\n\t\}", events)
    assert len(parsed_events) == 3 and all("add_" not in body and "trigger" not in body for body in parsed_events)
    reforms = "\n".join(path.read_text(encoding="cp1252") for path in (ROOT / "common/government_reforms").glob("*.txt"))
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
    own = "\n".join(p.read_text(encoding="cp1252") for p in (ROOT / "common/government_reforms").glob("*.txt"))
    native = "\n".join(p.read_text(encoding="cp1252") for p in (installed / "common/government_reforms").glob("*.txt"))
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
        live_ids.update(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", path.read_text(encoding="cp1252"), re.M))
    assert len(rows) == len(data["reforms"]) == 109 and set(rows) == live_ids
    own_tiers = reform_tiers(read("common/governments/00_governments.txt"))
    snapshots = {row["id"]: row for row in data["vanilla_comparators"]}
    installed = vanilla_root()
    native_tiers = None
    native_definitions = set()
    if installed:
        native_tiers = reform_tiers((installed / "common/governments/00_governments.txt").read_text(encoding="cp1252"))
        for path in (installed / "common/government_reforms").glob("*.txt"):
            native_definitions.update(re.findall(r"^([a-z0-9_]+)\s*=\s*\{", path.read_text(encoding="cp1252"), re.M))
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
    assert count == 115
    if installed:
        print("GOVERNMENT COMPARATOR COVERAGE: PASS (109 definitions; 115 tier rows verified against installed 1.37)")
    else:
        print("GOVERNMENT COMPARATOR COVERAGE: PASS (109 definitions; 115 saved tier rows); SKIP live vanilla tier check")


def main():
    source_contracts()
    count = run_scenarios()
    vanilla_envelopes()
    comparator_coverage()
    print(f"GOVERNMENT REVIEW CHECK: PASS ({count} payment/stale-state cases; three reviews; one shared term)")
    print("Government campaign power <=105% of EU4 1.37.5: NOT CERTIFIED by this source-contract check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
