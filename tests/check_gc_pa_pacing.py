"""Exact balance contract for Greek Catholic Patriarch Authority pacing."""
from decimal import Decimal
import re

from clausewitz_testlib import ROOT, keyed_blocks, named_block, read

religions = read("common/religions/zz_greek_catholic.txt")
christian = named_block(religions, "christian")
greek_catholic = named_block(christian, "greek_catholic")
income = named_block(greek_catholic, "country")
assert re.search(
    r"(?m)^\s*yearly_patriarch_authority\s*=\s*0\.025\s*$", income
), "Greek Catholic hierarchy needs the measured passive PA income"

# Keep the passive source specific to Greek Catholicism; Russian Orthodoxy keeps
# its separate native PA balance and receives no copy of this compensation.
russian_orthodox = named_block(
    read("common/religions/russian_orthodox.txt"), "russian_orthodox"
)
assert "yearly_patriarch_authority" not in named_block(russian_orthodox, "country")

icons = read("common/scripted_effects/rip_church_gc_interaction_effects.txt")
icon_cost = Decimal("0.07")
icon_duration = Decimal("1825")
for key in ("liturgy", "learning", "charity"):
    effect = named_block(icons, f"rip_church_gc_activate_icon_{key}_effect")
    assert "add_patriarch_authority = -0.07" in effect
    assert "duration = 1825" in effect
icon_gate = named_block(
    read("common/scripted_triggers/rip_church_gc_interaction_triggers.txt"),
    "rip_church_gc_can_activate_icons",
)
assert "patriarch_authority = 0.07" in icon_gate

# AI icon choices are evaluated through the monthly lifecycle, not once per
# year or as a free automatic refresh.
hooks = read("common/on_actions/zz_RIP_religion_church_on_actions.txt")
lifecycle = read("common/scripted_effects/rip_church_lifecycle_effects.txt")
assert "on_monthly_pulse = { rip_church_v3_monthly_effect = yes }" in " ".join(hooks.split())
assert "if = { limit = { ai = yes } rip_church_ai_effect = yes }" in named_block(
    lifecycle, "rip_church_v3_monthly_effect"
)
assert "rip_church_gc_ai_icons_effect = yes" in named_block(
    lifecycle, "rip_church_ai_effect"
)

synods = read("common/scripted_effects/rip_church_union_effects.txt")
synod_gates = read("common/scripted_triggers/rip_church_union_triggers.txt")
for key in ("infrastructure", "coexistence"):
    effect = named_block(synods, f"rip_church_gc_{key}_effect")
    assert "add_patriarch_authority = -0.07" in effect
    assert "duration = 3650" in effect
    assert "patriarch_authority = 0.07" in named_block(synod_gates, f"rip_church_gc_can_{key}")

# The ten-year parish action (visit or mission) costs a Greek Catholic state 2
# and the other communions 5; both paths charge through one effect and one gate.
visit_triggers = read("common/scripted_triggers/rip_parish_visit_triggers.txt")
visit_effects = read("common/scripted_effects/rip_parish_visit_effects.txt")
gate = " ".join(named_block(visit_triggers, "rip_has_parish_action_authority").split())
assert "AND = { religion = greek_catholic patriarch_authority = 0.02 }" in gate
assert "AND = { NOT = { religion = greek_catholic } patriarch_authority = 0.05 }" in gate
payment = " ".join(named_block(visit_effects, "rip_pay_parish_action_authority_effect").split())
assert "if = { limit = { religion = greek_catholic } add_patriarch_authority = -0.02 }" in payment
assert ("if = { limit = { NOT = { religion = greek_catholic } } add_patriarch_authority = -0.05 }"
        in payment)
assert "else" not in payment

mission = named_block(
    read("common/scripted_effects/rip_religion_settlement_effects.txt"),
    "rip_faith_fund_mission_effect",
)
visit = named_block(visit_effects, "rip_fund_parish_visit_effect")
for body in (mission, visit):
    assert "rip_pay_parish_action_authority_effect = yes" in body
    assert "add_patriarch_authority" not in body
    assert "name = rip_parish_visit_recent duration = 3650" in body
assert "rip_has_parish_action_authority = yes" in named_block(visit_triggers, "rip_can_fund_parish_visit")
assert "rip_has_parish_action_authority = yes" in named_block(
    read("common/scripted_triggers/rip_religion_settlement_triggers.txt"),
    "rip_faith_can_fund_mission_trigger",
)

# A routine five-year icon, ten-year synod, and ten-year parish action consume
# 0.023 PA/year together. The 0.025 source leaves only 0.002/year headroom, and
# a state that spends nothing needs forty years, not thirteen, to fill the bar.
annual_icon = icon_cost * Decimal(365) / icon_duration
annual_synod = icon_cost * Decimal(365) / Decimal(3650)
annual_parish = Decimal("0.02") * Decimal(365) / Decimal(3650)
annual_need = annual_icon + annual_synod + annual_parish
annual_income = Decimal("0.025")
assert annual_need == Decimal("0.023")
assert annual_income - annual_need == Decimal("0.002")
assert Decimal(1) / annual_income == Decimal(40)

# Gates follow the same division as income and prices, and a price paired with a
# gate never exceeds it.
standing = read("common/scripted_triggers/rip_hierarchy_standing_triggers.txt")
for tier, bar in (("low", "0.10"), ("mid", "0.12"), ("high", "0.13")):
    assert f"patriarch_authority = {bar}" in named_block(standing, f"rip_gc_hierarchy_standing_{tier}")
decisions = read("decisions/GreekCatholicDecisions.txt")
for key, gate_value, price in (("strengthen_papal_ties_decision", "0.17", "0.08"),
                               ("preserve_eastern_rite_decision", "0.03", "0.03")):
    body = named_block(decisions, key)
    assert f"patriarch_authority = {gate_value}" in named_block(body, "allow"), key
    assert f"add_patriarch_authority = -{price}" in named_block(body, "effect"), key
    assert Decimal(price) <= Decimal(gate_value), key
brotherhoods = named_block(read("common/disasters/rip_faith_disasters.txt"), "rip_uc_brotherhoods")
assert "NOT = { patriarch_authority = 0.13 }" in named_block(brotherhoods, "progress")
unity = " ".join(named_block(read("missions/Zakarpatta_Missions.txt"), "uz_orthodox_unity").split())
assert "AND = { religion = greek_catholic patriarch_authority = 0.25 }" in unity
assert ("AND = { OR = { religion = orthodox religion = russian_orthodox } patriarch_authority = 0.75 }"
        in unity)

# One-off rewards follow the same division. Content other faiths share states
# both amounts, and the Greek Catholic one is a third of the other.
third = {"0.03": "0.01", "0.05": "0.02", "0.08": "0.03", "0.1": "0.03", "0.15": "0.05",
         "0.2": "0.07", "0.25": "0.08", "0.3": "0.1", "0.5": "0.17"}
calls = []
for folder in ("common", "events", "decisions", "missions"):
    for path in sorted((ROOT / folder).rglob("*.txt")):
        text = re.sub(r"#[^\n]*", "", path.read_text(encoding="cp1252", errors="replace"))
        for match in re.finditer(r"\b(rip_grant_authority_effect|rip_faith_mission_resource_effect)\s*=\s*\{([^{}]*)\}", text):
            values = dict(re.findall(r"\b(PA|GC)\s*=\s*([\d.]+)", match[2]))
            calls.append((path.name, match[1], values))
assert len(calls) >= 40, len(calls)
for name, effect, values in calls:
    assert set(values) == {"PA", "GC"}, (name, effect, values)
    assert values["GC"] == third[values["PA"]], (name, effect, values)
resource = " ".join(named_block(
    read("common/scripted_effects/rip_religion_settlement_effects.txt"), "rip_faith_mission_resource_effect").split())
assert "if = { limit = { religion = greek_catholic } add_patriarch_authority = $GC$ }" in resource
assert "else" not in resource

# Greek Catholic-only rewards carry the divided number directly.
for path, block, amounts in (
        ("decisions/UzhEparchyPath.txt", "uzh_road_of_the_eparchy", ["0.07"]),
        ("common/scripted_effects/greek_catholic_effects.txt", "greek_catholic_faith_bonus", ["0.02"])):
    found = re.findall(r"add_patriarch_authority = ([\d.]+)", named_block(read(path), block))
    assert found == amounts, (block, found)
for path, events in (
        ("events/RIP_shared_greek_catholic_UniateChurch.txt",
         {"uniate_church.11": "0.02", "uniate_church.13": "0.03", "uniate_church.14": "0.03",
          "uniate_church.19": "0.07"}),
        ("events/RIP_shared_greek_catholic_UniateCrownUnion.txt",
         {"uniate_crown.3": "0.02", "uniate_crown.8": "0.07"}),
        ("events/RIP_shared_church_FaithDisasters.txt",
         {"rip_faith_disaster.6": "0.03", "rip_faith_disaster.7": "0.01", "rip_faith_disaster.8": "0.03"})):
    bodies = {re.search(r"(?m)^\tid\s*=\s*([\w.]+)", body)[1]: body
              for _, body in keyed_blocks(read(path), "country_event")
              if re.search(r"(?m)^\tid\s*=", body)}
    for event_id, amount in events.items():
        found = re.findall(r"add_patriarch_authority = ([\d.]+)", bodies[event_id])
        assert found == [amount], (event_id, found)

# Penalties follow the same division. The Revolt of the Brotherhoods is the one
# place a Greek Catholic state loses authority it did not choose to spend.
brotherhoods = named_block(read("common/disasters/rip_faith_disasters.txt"), "rip_uc_brotherhoods")
assert re.findall(r"yearly_patriarch_authority = (-?[\d.]+)", brotherhoods) == ["-0.007"]
disaster_events = {re.search(r"(?m)^\tid\s*=\s*([\w.]+)", body)[1]: body
                   for _, body in keyed_blocks(read("events/RIP_shared_church_FaithDisasters.txt"), "country_event")
                   if re.search(r"(?m)^\tid\s*=", body)}
for event_id, amounts in (("rip_faith_disaster.5", ["-0.03"]), ("rip_faith_disaster.6", []),
                          ("rip_faith_disaster.7", []), ("rip_faith_disaster.8", ["-0.02"])):
    found = re.findall(r"add_patriarch_authority = (-[\d.]+)", disaster_events[event_id])
    assert found == amounts, (event_id, found)

# Texts that quote a price must quote the price the effects charge.
priced = ["rip_church_gc_icons_note", "rip_church_gc_native_privileges_button_tt",
          "rip_church_gc_infrastructure_button_tt", "rip_church_gc_coexistence_button_tt", "rip_church.6.d"]
priced += ["rip_church_gc_icon_%s_%s_tt" % (icon, kind)
           for icon in ("liturgy", "learning", "charity") for kind in ("button", "state")]
for language in ("english", "french", "german", "spanish"):
    redesign = (ROOT / ("localisation/replace/RIP_shared_church_redesign_l_%s.yml" % language)).read_text(encoding="utf-8-sig")
    for key in priced:
        text = re.search(r'(?m)^ *%s:\d* "(.*)"' % re.escape(key), redesign)[1]
        quoted = re.findall(r"(\d+) (?:HC|Hierarchical Capacity)", re.sub("\u00a7.", "", text))
        assert quoted and set(quoted) == {"7"}, (language, key, quoted)
    content = (ROOT / ("localisation/replace/RIP_shared_church_content_l_%s.yml" % language)).read_text(encoding="utf-8-sig")
    mission = re.search(r'(?m)^ *rip_fund_a_parish_mission_effect_tt:\d* "(.*)"', content)[1]
    assert "2.0% Hierarchical Capacity if Greek Catholic" in re.sub("\u00a7.", "", mission), language

print(
    "GC PA PACING PASS: +0.025/year vs 0.023/year routine demand "
    "(icons, synod, parish action); +0.002/year headroom, 40 idle years to the cap"
)
