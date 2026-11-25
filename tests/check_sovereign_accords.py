"""Static contracts for the three sovereign frontier agreements."""

from clausewitz_testlib import named_block, read


actions = read("common/new_diplomatic_actions/RIP_sovereign_accords.txt")
triggers = read("common/scripted_triggers/rip_sovereign_accord_triggers.txt")
effects = read("common/scripted_effects/rip_sovereign_accord_effects.txt")
poland = read("missions/zzz_Poland_Commonwealth_Rework.txt")
kyiv = read("missions/Kyiv_Successors_Missions.txt")
dniester = read("decisions/DniesterEstuaryDecisions.txt")

for route, entry, finale in (
    ("hadiach", poland, "pol_triatomic_commonwealth"),
    ("kyiv", kyiv, "UKR_defensive_league"),
    ("dniester", dniester, "rip_conclude_dniester_accord"),
):
    signature = f"rip_{route}_accord_signed"
    held = f"rip_{route}_accord_held"
    concluded = f"rip_{route}_accord_concluded"
    action = named_block(actions, f"rip_sign_{route}_accord")
    visible = named_block(action, "is_visible")
    assert "require_acceptance = yes" in action
    assert visible.count("is_subject = no") == 2
    assert f"NOT = {{ has_country_flag = {signature} }}" in visible
    assert f"rip_accord_{route}_partner = yes" in named_block(action, "is_allowed")
    outcome = named_block(action, "on_accept")
    assert all(token not in outcome for token in ("create_subject", "change_owner", "inherit"))
    assert f"set_country_flag = {signature}" in outcome
    assert f"modifier = rip_{route}_accord_opinion" in outcome
    assert "rip_update_sovereign_accords = yes" in outcome
    final = named_block(entry, finale)
    assert f"flag = {held} days = 1825" in final
    assert f"set_country_flag = {concluded}" in named_block(final, "effect")
    assert "rip_update_sovereign_accords = yes" in named_block(final, "effect")

active = named_block(triggers, "rip_sovereign_accord_active")
assert "is_subject = no" in active and "any_ally = {" in active
assert "modifier = $opinion$" in named_block(active, "any_ally")
upkeep = named_block(effects, "rip_update_sovereign_accord")
assert "rip_sovereign_accord_active" in upkeep
inactive = named_block(upkeep, "else")
assert "clr_country_flag = $held$" in inactive and "remove_country_modifier = $reward$" in inactive
assert "owned_by = PREV" in named_block(triggers, "rip_accord_dniester_partner")
assert "rip_dniester_port_access = yes" in named_block(dniester, "develop_dniester_estuary_trade")
assert "required_missions = { UKR_princely_compact }" in named_block(kyiv, "UKR_defensive_league")
assert "pol_triatomic_commonwealth_realized" in named_block(poland, "pol_crown_ruthenian_integration")
print("SOVEREIGN ACCORDS PASS: voluntary signatories, five-year frontier, conditional rewards, and Crown route.")
