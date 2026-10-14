"""Exact balance contract for Greek Catholic Patriarch Authority pacing."""
from decimal import Decimal
import re

from clausewitz_testlib import named_block, read

religions = read("common/religions/zz_greek_catholic.txt")
christian = named_block(religions, "christian")
greek_catholic = named_block(christian, "greek_catholic")
income = named_block(greek_catholic, "country")
assert re.search(
    r"(?m)^\s*yearly_patriarch_authority\s*=\s*0\.075\s*$", income
), "Greek Catholic hierarchy needs the measured passive PA income"

# Keep the increase specific to Greek Catholicism; Russian Orthodoxy keeps its
# separate native PA balance and receives no copy of this compensation.
russian_orthodox = named_block(
    read("common/religions/russian_orthodox.txt"), "russian_orthodox"
)
assert "yearly_patriarch_authority = 0.075" not in russian_orthodox

icons = read("common/scripted_effects/rip_church_gc_interaction_effects.txt")
icon_cost = Decimal("0.20")
icon_duration = Decimal("1825")
for key in ("liturgy", "learning", "charity"):
    effect = named_block(icons, f"rip_church_gc_activate_icon_{key}_effect")
    assert "add_patriarch_authority = -0.2" in effect
    assert "duration = 1825" in effect

# AI icon choices are evaluated through the monthly lifecycle, not once per
# year or as a free automatic refresh.
hooks = read("common/on_actions/zz_RIP_church_redesign_on_actions.txt")
lifecycle = read("common/scripted_effects/rip_church_lifecycle_effects.txt")
assert "on_monthly_pulse = { rip_church_v3_monthly_effect = yes }" in hooks
assert "if = { limit = { ai = yes } rip_church_ai_effect = yes }" in named_block(
    lifecycle, "rip_church_v3_monthly_effect"
)
assert "rip_church_gc_ai_icons_effect = yes" in named_block(
    lifecycle, "rip_church_ai_effect"
)

synods = read("common/scripted_effects/rip_church_union_effects.txt")
for key in ("infrastructure", "coexistence"):
    effect = named_block(synods, f"rip_church_gc_{key}_effect")
    assert "add_patriarch_authority = -0.2" in effect
    assert "duration = 3650" in effect

# A routine five-year icon, ten-year synod, and ten-year parish visit consume
# 0.065 PA/year together. The 0.075 source leaves only 0.01/year headroom;
# costs, durations, and separate church choices remain real constraints.
mission = named_block(
    read("common/scripted_effects/rip_religion_settlement_effects.txt"),
    "rip_faith_fund_mission_effect",
)
assert "add_patriarch_authority = -0.05" in mission
assert "name = rip_parish_visit_recent duration = 3650" in mission
visit_gate = named_block(
    read("common/scripted_triggers/rip_parish_visit_triggers.txt"),
    "rip_can_fund_parish_visit",
)
assert "patriarch_authority = 0.05" in visit_gate
visit = named_block(
    read("common/scripted_effects/rip_parish_visit_effects.txt"),
    "rip_fund_parish_visit_effect",
)
assert "add_patriarch_authority = -0.05" in visit
assert "name = rip_parish_visit_recent duration = 3650" in visit

annual_icon = icon_cost * Decimal(365) / icon_duration
annual_synod = icon_cost * Decimal(365) / Decimal(3650)
annual_parish = Decimal("0.05") * Decimal(365) / Decimal(3650)
annual_need = annual_icon + annual_synod + annual_parish
annual_income = Decimal("0.075")
assert annual_need == Decimal("0.065")
assert annual_income - annual_need == Decimal("0.010")
assert annual_income * Decimal(50) == Decimal("3.750")

print(
    "GC PA PACING PASS: +0.075/year vs 0.065/year routine demand "
    "(icons, synod, parish action); +0.010/year bounded headroom"
)
