"""Keep Greek Catholic Hierarchical Capacity help and art aligned with mechanics."""
import struct
from pathlib import Path

from clausewitz_testlib import ROOT, named_block, read

gui = read("interface/countryreligionview.gui")
controls = read("common/custom_gui/RIP_church_controls.txt")
assert (
    'name = "rip_church_gc_capacity_high_icon" scripted = yes '
    'spriteType = "GFX_rip_church_gc_capacity_high" position = { x=244 y=273 }'
) in gui
assert controls.count("tooltip = rip_church_gc_resources_tt") == 2

help_text = (
    "native Patriarch Authority bar (0–100)",
    "+7.5 HC per year (+0.625 per month)",
    "Country-specific decisions, events and mission rewards",
    "Liturgy grants +1 yearly prestige",
    "Learning grants -5% development cost and -5% technology cost",
    "Almsgiving grants -1 global unrest and -10% stability cost",
    "20 HC plus 75 ducats for Infrastructure",
    "20 HC plus 100 ducats for Coexistence",
    "A parish visit costs 5 HC, 100 ducats and 25 ADM",
    "five-point bands",
    "at 100, the country has -2% global missionary strength and -10% church influence",
)
localisation_generator = read("tools/build_church_localisation.py")
for phrase in help_text:
    assert phrase in localisation_generator, ("generator", phrase)
for language in ("english", "french", "german", "spanish"):
    localisation = read(
        f"localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml"
    )
    tooltip = next(
        line for line in localisation.splitlines()
        if line.startswith(" rip_church_gc_resources_tt:")
    )
    for phrase in help_text:
        assert phrase in tooltip, (language, phrase)

modifiers = read("common/event_modifiers/rip_church_gc_interaction_modifiers.txt")
assert "prestige = 1 diplomatic_reputation = 1 improve_relation_modifier = 0.2" in named_block(
    modifiers, "rip_church_gc_icon_liturgy"
)
assert "development_cost = -0.05 technology_cost = -0.05" in named_block(
    modifiers, "rip_church_gc_icon_learning"
)
assert "global_unrest = -1 stability_cost_modifier = -0.1" in named_block(
    modifiers, "rip_church_gc_icon_charity"
)

synod_modifiers = read("common/event_modifiers/RIP_church_redesign_modifiers.txt")
assert "state_maintenance_modifier = -0.1 church_loyalty_modifier = 0.05" in named_block(
    synod_modifiers, "rip_church_gc_infrastructure"
)
assert "global_unrest = -0.5 improve_relation_modifier = 0.1" in named_block(
    synod_modifiers, "rip_church_gc_coexistence"
)
parish_modifiers = read("common/event_modifiers/rip_parish_visit_modifiers.txt")
service_books = named_block(parish_modifiers, "rip_parish_service_books")
assert "local_missionary_strength = 0.01" in service_books
assert "local_tax_modifier = -0.05" in service_books
alms_register = named_block(parish_modifiers, "rip_parish_alms_register")
assert "local_unrest = -1" in alms_register
assert "local_tax_modifier = -0.05" in alms_register

centres = {}
for kind in ("low", "high"):
    path = ROOT / f"gfx/interface/rip_church/gc_archbishop_{kind}.dds"
    data = path.read_bytes()
    assert data[:4] == b"DDS "
    height, width = struct.unpack_from("<II", data, 12)
    assert (width, height) == (38, 38)
    assert struct.unpack_from("<I", data, 88)[0] == 32
    pixels = data[128:]
    assert len(pixels) == width * height * 4
    alpha_mass = 0
    x_mass = 0
    count = 0
    red = green = blue = 0
    for y in range(height):
        for x in range(width):
            offset = (y * width + x) * 4
            b, g, r, a = pixels[offset:offset + 4]
            if not a:
                continue
            count += 1
            red += r
            green += g
            blue += b
            alpha_mass += a
            x_mass += x * a
    assert count > 0 and alpha_mass > 0
    centres[kind] = x_mass / alpha_mass
    if kind == "low":
        assert blue / count > red / count, "low icon should read cooler than warm red/gold"
    else:
        assert red / count > blue / count, "high icon should read warm"
assert centres["low"] > 18.5 > centres["high"], "high icon should be mirrored toward the bar"

print("GC CAPACITY UI PASS: tooltip/mechanics contracts, native art size, cool/warm tint and mirrored high icon")
