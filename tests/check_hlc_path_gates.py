"""Contracts for the Galician government-path decisions."""

from clausewitz_testlib import named_block, read


decisions = read("decisions/HLCRepublicPaths.txt")
triggers = read("common/scripted_triggers/rip_path_state_triggers.txt")
localisation = read("localisation/rip_galicia_l_english.yml")

boyars = named_block(decisions, "hlc_the_boyars_take_power")
boyar_potential = named_block(boyars, "potential")
boyar_allow = named_block(boyars, "allow")
assert "hlc_boyar_succession_crisis = yes" in boyar_potential
assert "hlc_boyar_succession_crisis = yes" in boyar_allow
assert "NOT = { government = republic }" in boyar_potential
assert "is_subject = no" in boyar_potential
assert "stability = 1" in boyar_potential
assert "is_subject = no" in boyar_allow
assert "stability = 1" in boyar_allow
crisis = named_block(triggers, "hlc_boyar_succession_crisis")
assert "NOT = { has_heir = yes }" in crisis
assert "legitimacy < 60" in crisis and "legitimacy < 50" in crisis

metropolitan = named_block(decisions, "hlc_elevate_the_metropolitan")
metropolitan_potential = named_block(metropolitan, "potential")
metropolitan_allow = named_block(metropolitan, "allow")
assert "hlc_metropolitan_authority_ready = yes" in metropolitan_potential
assert "hlc_metropolitan_authority_ready = yes" in metropolitan_allow
assert "is_subject = no" in metropolitan_potential
assert "NOT = { government = theocracy }" in metropolitan_potential
assert "stability = 1" in metropolitan_potential
assert "stability = 1" in metropolitan_allow
authority = named_block(triggers, "hlc_metropolitan_authority_ready")
assert "patriarch_authority = 0.5" in authority
assert "rip_gc_hierarchy_standing_mid = yes" in authority
assert "add_patriarch_authority = 0.1" in named_block(metropolitan, "effect")
assert "add_papal_influence = 10" not in metropolitan

for key in (
    "hlc_the_boyars_take_power_title",
    "hlc_the_boyars_take_power_desc",
    "hlc_elevate_the_metropolitan_title",
    "hlc_elevate_the_metropolitan_desc",
):
    assert f"{key}:0" in localisation

print("PASS: Galician decisions are gated by succession and church conditions")
