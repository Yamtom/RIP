"""Regression contracts for Podillia's repeatable border policy.

Commit c0115a6f rewrote the policy as the regional ordinances of tools/build_regional_governments.py. The decision keeps
its name and gate, but event pdl_border_policy.1 is now only an entry point: its first three options open the
land-selection windows of the rip_rg_pdl_* ordinances (the same ones the Government-view buttons and the rip_rg_*_decision
entries open) and the last one is a free cancel. The old event - four options that applied the pdl_*_funded / _supported /
_delegated modifiers directly and ended in a "maintain the stance" option worth prestige - is gone on purpose, so this
test no longer asks for it.

Verifies:
1. Decision pdl_border_policy_decision (unchanged):
   - provinces_to_highlight present for Podillian marchland provinces.
   - Gated on west_ukraine_pdl_origin_country, peacetime, stability >= 0, cooldown.
   - Calls event pdl_border_policy.1.
2. Event pdl_border_policy.1 in events/PodilliaBorderPolicy.txt:
   - Option a = patrols, b = town statute, c = mobile defence, then a free cancel; nothing is charged by the event itself.
   - Every constitutional path has its own variant (frontier, carpathian, magnate); each variant sends the AI straight to
     its commit effect and a human to the land-selection window of the same variant (an existing rip_rg event).
   - No else / else_if: EU4 1.37.5 drops country_event inside them, which would leave the human branch without its window.
3. The variants' scripted triggers carry the path flags and the shared five-year term (pdl_recent_border_policy), and each
   commit effect starts that term.
4. Modifiers in common/event_modifiers/podillia_modifiers.txt, which saves may still carry, keep their numbers.
5. Localisation: the decision and its title are in the hand-written files, the new entry point in the generated ones.
6. The generated files match the generator.
"""

from __future__ import annotations

import re
import subprocess
import sys

from clausewitz_testlib import read_scripted_trigger_family
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized

# group -> option letter, and per variant the country flag that selects it (None: the base variant, which excludes the others)
OPTION_OF = {"patrol": "a", "charter": "b", "mobile": "c"}
VARIANTS = {
    "patrol": [("base", None), ("frontier", "pdl_frontier_path"), ("carpathian", "pdl_carpathian_path")],
    "charter": [("base", None), ("magnate", "pdl_magnate_path")],
    "mobile": [("base", None), ("frontier", "pdl_frontier_path"), ("carpathian", "pdl_carpathian_path")],
}
PATH_FLAGS = {"pdl_frontier_path", "pdl_carpathian_path", "pdl_magnate_path"}


def test_decision():
    decisions = read("decisions/Podillia_Decisions.txt")
    decision = named_block(decisions, "pdl_border_policy_decision")
    assert decision, "pdl_border_policy_decision missing in decisions/Podillia_Decisions.txt"

    assert "provinces_to_highlight" in decision, "Decision must highlight Podillian borderlands"
    assert "NOT = { has_country_modifier = pdl_recent_border_policy }" in decision
    assert "country_event = { id = pdl_border_policy.1 }" in decision

    potential = normalized(named_block(decision, "potential"))
    assert "west_ukraine_pdl_origin_country = yes" in potential
    assert "has_country_flag = pdl_frontier_path" in potential
    assert "has_country_flag = pdl_carpathian_path" in potential
    assert "has_country_flag = pdl_magnate_path" in potential


def test_events():
    events = read("events/PodilliaBorderPolicy.txt")
    assert "namespace = pdl_border_policy" in events

    root_event = named_block(events, "country_event")
    assert "id = pdl_border_policy.1" in root_event
    assert "title = pdl_border_policy.1.t" in root_event
    assert "desc = pdl_border_policy.1.desc" in root_event
    for letter in "abc":
        assert f"name = pdl_border_policy.1.{letter}" in root_event
    assert "name = rip_rg_cancel" in root_event, "the free cancel option is missing"
    assert "name = pdl_border_policy.1.d" not in root_event, "the old fourth option came back"
    options = [block for _, block in keyed_blocks(root_event, "option")]
    assert len(options) == 4, f"expected three ordinance options and a cancel, found {len(options)}"
    cancel = next(block for block in options if "name = rip_rg_cancel" in block)
    assert "country_event" not in cancel and "add_" not in cancel, "cancelling must be free"

    # the event applies nothing itself: no direct modifiers, no payment
    flat = normalized(root_event)
    assert not re.search(r"\badd_(country|province)_modifier\b|\badd_treasury\b|_power =", flat), "the entry point must not charge or apply anything itself"
    assert not re.search(r"\belse(_if)?\s*=\s*\{", flat), "else / else_if drops country_event in EU4 1.37.5; use plain `if` blocks"

    regional = read("events/RIP_RegionalGovernments.txt")
    effects = read("common/scripted_effects/rip_regional_government_effects.txt")
    for group, variants in VARIANTS.items():
        option = normalized(next(block for block in options if f"name = pdl_border_policy.1.{OPTION_OF[group]}" in block))
        for variant, _flag in variants:
            key = f"pdl_{group}_{variant}"
            # the AI pays at once for a random eligible land ...
            ai_branch = (rf"rip_rg_{key}_can = yes any_owned_province = \{{ rip_rg_{key}_target = yes \}} ai = yes \}} "
                         rf"random_owned_province = \{{ limit = \{{ rip_rg_{key}_target = yes \}} save_event_target_as = rip_rg_target \}} "
                         rf"rip_rg_{key}_commit_effect = yes \}}")
            assert re.search(ai_branch, option), f"{key}: the AI branch of option {OPTION_OF[group]} is missing"
            # ... a human gets the land-selection window of the same variant
            human = re.search(rf"rip_rg_{key}_can = yes any_owned_province = \{{ rip_rg_{key}_target = yes \}} ai = no \}} country_event = \{{ id = rip_rg\.(\d+) \}}", option)
            assert human, f"{key}: the human branch of option {OPTION_OF[group]} is missing"
            assert re.search(rf"id = rip_rg\.{human.group(1)}\s+title = rip_rg_{key}\.t\b", regional), f"{key}: event rip_rg.{human.group(1)} is not its selection window"
            assert f"rip_rg_{key}_commit_effect = {{" in effects, f"{key}: commit effect missing"


def test_variant_gates():
    triggers = read_scripted_trigger_family("regional_government_triggers")
    effects = read("common/scripted_effects/rip_regional_government_effects.txt")
    for group, variants in VARIANTS.items():
        for variant, flag in variants:
            key = f"pdl_{group}_{variant}"
            can = normalized(named_block(triggers, f"rip_rg_{key}_can"))
            assert "rip_rg_pdl = yes" in can, f"{key}: not gated on the Podillian origin"
            assert "custom_trigger_tooltip = { tooltip = rip_rg_term_tt NOT = { has_country_modifier = pdl_recent_border_policy } }" in can, f"{key}: shared term missing"
            if flag:
                assert re.search(rf"(?<!NOT = \{{ )has_country_flag = {flag}\b", can), f"{key}: not gated on {flag}"
            else:
                for other in {f for _, f in variants if f}:
                    assert f"NOT = {{ has_country_flag = {other} }}" in can, f"{key}: the base variant must exclude {other}"
            assert "rip_rg_" + key + "_target" in triggers
            commit = normalized(named_block(effects, f"rip_rg_{key}_commit_effect"))
            assert "add_country_modifier = { name = pdl_recent_border_policy duration = 1825 }" in commit, f"{key}: commit does not start the shared term"
    # a later variant of one button never fires on top of an earlier one: its limit excludes the earlier guards
    mechanics = normalized(named_block(read("common/government_mechanics/rip_regional_governments.txt"), "rip_rg_pdl_mechanic"))
    assert "NOT = { AND = { rip_rg_pdl_patrol_base_can = yes" in mechanics


def test_modifiers():
    modifiers = read("common/event_modifiers/podillia_modifiers.txt")

    defense_carpathian = named_block(modifiers, "pdl_carpathian_defense_funded")
    assert "defensiveness = 0.25" in defense_carpathian
    assert "garrison_size = 0.2" in defense_carpathian

    frontier_settlement = named_block(modifiers, "pdl_frontier_settlement_supported")
    assert "global_manpower_modifier = 0.15" in frontier_settlement

    magnate_elites = named_block(modifiers, "pdl_magnate_elites_delegated")
    assert "nobles_loyalty_modifier = 0.15" in magnate_elites
    assert "advisor_cost = -0.1" in magnate_elites


def test_localization():
    hand_written = [
        "pdl_border_policy_decision",
        "pdl_border_policy_decision_desc",
        "pdl_border_policy.1.t",
        "pdl_recent_border_policy",
        # no event applies these any more, but a save may still carry them
        "pdl_frontier_defense_funded",
        "pdl_carpathian_defense_funded",
        "pdl_magnate_defense_funded",
        "pdl_defense_funded",
        "pdl_frontier_settlement_supported",
        "pdl_carpathian_settlement_supported",
        "pdl_magnate_settlement_supported",
        "pdl_settlement_supported",
        "pdl_frontier_elites_delegated",
        "pdl_carpathian_elites_delegated",
        "pdl_magnate_elites_delegated",
        "pdl_elites_delegated",
    ]
    for lang_file in [
        "localisation/RIP_l_english.yml",
        "localisation/replace/zzz_RIP_untranslated_l_french.yml",
        "localisation/replace/zzz_RIP_untranslated_l_german.yml",
        "localisation/replace/zzz_RIP_untranslated_l_spanish.yml",
    ]:
        content = (ROOT / lang_file).read_text(encoding="utf-8-sig")
        for key in hand_written:
            assert f" {key}:" in content, f"Missing key {key} in {lang_file}"

    generated = ["pdl_border_policy.1.desc", "pdl_border_policy.1.a", "pdl_border_policy.1.b", "pdl_border_policy.1.c", "rip_rg_cancel"]
    for language in ("english", "french", "german", "spanish"):
        content = (ROOT / f"localisation/zzz_rip_regional_governments_l_{language}.yml").read_text(encoding="utf-8-sig")
        for key in generated:
            assert f" {key}:" in content, f"Missing key {key} in the generated {language} file"


def test_generated_files_are_current():
    subprocess.run([sys.executable, "-B", "tools/build_regional_governments.py", "--check"], cwd=ROOT, check=True)


def main():
    test_decision()
    test_events()
    test_variant_gates()
    test_modifiers()
    test_localization()
    test_generated_files_are_current()
    print("PODILLIA BORDER POLICY PASS: decision, three-option entry point with free cancel, per-path variants (AI commit, human window), "
          "shared-term gates, retained modifiers, localisation and generator sync verified.")


if __name__ == "__main__":
    main()
