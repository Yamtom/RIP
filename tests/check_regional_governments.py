"""Static guards for the generated regional-government system (tools/build_regional_governments.py).

Every guard pins a defect that EU4 1.37.5 wrote to logs/error.log when commit c0115a6f was first loaded (2026-10-19) and
that no text-level gate saw, because each one is a perfectly well-formed block:

1. A scripted trigger inside a mechanic's `available` ("Unknown trigger type"): the engine reads `available` before scripted
   triggers exist, so the mechanic never loaded and the player got no buttons. Triggers and ai_chance of the interactions
   may still call scripted triggers.
2. `is_port` (vanilla: `has_port`) and `has_terrain = mountains` (vanilla: `mountain`).
3. The modifier keys local_trade_power_modifier and local_goods_produced_modifier, which do not exist
   (vanilla: province_trade_power_modifier and trade_goods_size_modifier).
4. A hidden event without title / desc / picture / option: `hidden = yes` does not switch off the engine's event checks.
5. country_event, province_event or add_opinion inside else / else_if: the engine drops them there without a word. The buttons,
   the decisions and the old Podillia entry event therefore use plain `if` blocks.

The generated files must also match the generator.
"""

from __future__ import annotations

import re
import subprocess
import sys

from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, matching_brace, normalized

FAMILIES = ("chr", "uzh", "pdl", "prl", "ods")
MECHANICS = "common/government_mechanics/rip_regional_governments.txt"
TRIGGERS = "common/scripted_triggers/rip_regional_government_triggers.txt"
MODIFIERS = "common/event_modifiers/rip_regional_government_modifiers.txt"
EVENTS = "events/RIP_RegionalGovernments.txt"
# effect classes the engine drops inside else / else_if bodies (measured in 1.37.5, diagnostics/engine_probes_20260929)
DROPPED = re.compile(r"\b(country_event|province_event|add_opinion|reverse_add_opinion)\b")


def scripted_trigger_names():
    names = set()
    for path in (ROOT / "common/scripted_triggers").glob("*.txt"):
        names.update(re.findall(r"(?m)^(\w+)[ \t]*=[ \t]*\{", path.read_text(encoding="utf-8-sig")))
    return names


def test_available_has_no_scripted_trigger():
    text = read(MECHANICS)
    names = scripted_trigger_names()
    for family in FAMILIES:
        mechanic = named_block(text, f"rip_rg_{family}_mechanic")
        available = normalized(named_block(mechanic, "available"))
        used = sorted(n for n in names if re.search(rf"\b{n}\s*=\s*(yes|no)\b", available))
        assert not used, f"rip_rg_{family}_mechanic: scripted triggers in `available` ({', '.join(used)}); inline their bodies"
    # the interactions may keep calling them - that is measured to work
    assert "rip_rg_chr_bell_can = yes" in normalized(named_block(named_block(text, "rip_rg_chr_mechanic"), "rip_rg_chr_bell"))


def test_vanilla_keys():
    triggers = read(TRIGGERS)
    assert not re.search(r"\bis_port\b", triggers), "is_port does not exist; the vanilla trigger is has_port"
    assert "has_port = yes" in named_block(triggers, "rip_rg_port")
    assert not re.search(r"has_terrain\s*=\s*mountains\b", read(TRIGGERS)), "the terrain category is `mountain`"
    assert "has_terrain = mountain " in named_block(triggers, "rip_rg_uzh_guides_target")
    modifiers = read(MODIFIERS)
    for bad in ("local_trade_power_modifier", "local_goods_produced_modifier"):
        assert bad not in modifiers, f"{bad} is not a modifier key"
    assert "province_trade_power_modifier = 0.15" in named_block(modifiers, "rip_rg_chr_staple")
    salt = named_block(modifiers, "rip_rg_uzh_salt")
    assert "trade_goods_size_modifier = 0.15" in salt and "province_trade_power_modifier = 0.1" in salt
    # the province-transfer cleanup lists every modifier the actions put on a province, whatever their keys are
    effects = read("common/scripted_effects/rip_regional_government_effects.txt")
    cleanup = named_block(effects, "rip_rg_province_transfer_effect")
    for placed in ("rip_rg_chr_bell", "rip_rg_chr_staple", "rip_rg_chr_militia", "rip_rg_uzh_salt", "rip_rg_uzh_guides",
                   "rip_rg_uzh_pass", "rip_rg_border_patrol", "rip_rg_border_fort", "rip_rg_border_charter", "rip_rg_border_magnate"):
        assert f"remove_province_modifier = {placed}\n" in cleanup.replace("\r\n", "\n"), f"{placed} is not removed when a province changes hands"


def test_hidden_events_have_the_vanilla_shape():
    text = read(EVENTS)
    hidden = 0
    for _, block in keyed_blocks(text, "country_event"):
        if re.search(r"(?m)^\s*hidden\s*=\s*yes", block):
            hidden += 1
            for key in ("title", "desc", "picture"):
                assert re.search(rf"(?m)^\s*{key}\s*=", block), f"hidden event without {key}: {block.splitlines()[1].strip()}"
            assert re.search(r"(?m)^\s*option\s*=\s*\{", block), f"hidden event without an option: {block.splitlines()[1].strip()}"
    assert hidden >= 1, "rip_rg.900 (the delayed grain refresh) should be the hidden event"


def test_no_dropped_effect_in_else_bodies():
    # the buttons, the decisions, the Podillia entry event and the selection windows use plain `if` only
    for path in (MECHANICS, "decisions/RIP_RegionalGovernments.txt", "events/PodilliaBorderPolicy.txt", EVENTS):
        text = read(path)
        assert not re.search(r"\belse(_if)?\s*=\s*\{", normalized(text)), f"{path}: else / else_if (the engine drops country_event inside them)"
    # a scripted effect may keep else for effects that survive there (modifiers, flags, loyalty), but not for the dropped ones
    effects = read("common/scripted_effects/rip_regional_government_effects.txt")
    for match in re.finditer(r"\belse(?:_if)?\s*=\s*\{", normalized(effects)):
        masked = normalized(effects)
        body = masked[match.end() - 1: matching_brace(masked, match.end() - 1) + 1]
        assert not DROPPED.search(body), f"scripted effect: {DROPPED.search(body).group(1)} inside an else body is dropped by the engine"


def test_generated_files_are_current():
    subprocess.run([sys.executable, "-B", "tools/build_regional_governments.py", "--check"], cwd=ROOT, check=True)


def main():
    test_available_has_no_scripted_trigger()
    test_vanilla_keys()
    test_hidden_events_have_the_vanilla_shape()
    test_no_dropped_effect_in_else_bodies()
    test_generated_files_are_current()
    print("REGIONAL GOVERNMENTS PASS: no scripted trigger in `available` (5 mechanics), vanilla trigger/terrain/modifier keys, "
          "vanilla-shaped hidden event, no else/else_if around events, province-transfer list complete, generator in sync. Static only.")


if __name__ == "__main__":
    main()
