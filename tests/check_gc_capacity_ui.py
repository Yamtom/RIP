"""Keep Greek Catholic Hierarchical Capacity help and art aligned with mechanics."""
import struct
import re
from decimal import Decimal
from pathlib import Path

from clausewitz_testlib import ROOT, keyed_blocks, named_block, read, vanilla_root

gui = read("interface/countryreligionview.gui")
controls = read("common/custom_gui/RIP_church_controls.txt")
def widget_position(name):
    found = re.search(
        r'name = "' + name + r'" scripted = yes (?:spriteType = "\w+" )?position = \{ x=(\d+) y=(\d+) \}', gui)
    assert found, name
    return int(found[1]), int(found[2])


def alpha_box(path, threshold=128):
    data = path.read_bytes()
    height, width = struct.unpack_from("<II", data, 12)
    assert data[:4] == b"DDS " and struct.unpack_from("<I", data, 88)[0] == 32
    pixels = data[128:]
    hits = [(x, y) for y in range(height) for x in range(width)
            if pixels[(y * width + x) * 4 + 3] >= threshold]
    return (min(x for x, _ in hits), min(y for _, y in hits),
            max(x for x, _ in hits) + 1, max(y for _, y in hits) + 1)


# Native frame GFX_ideaView_progress_frame_long sits at (84,286), 194x18; its solid
# body (alpha >= 128) is x 4..191, y 3..15. The native marker travels x = 77 + 1.58 * HC
# and carries the percentage, so the two bishops frame the bar and nothing else.
FRAME_LEFT, FRAME_RIGHT = 84 + 4, 84 + 191
BAR_CENTRE_X2, BAR_CENTRE_Y2 = FRAME_LEFT + FRAME_RIGHT, 2 * 286 + 3 + 15
COVER_X = 303
boxes = {}
for kind in ("low", "high"):
    x, y = widget_position(f"rip_church_gc_capacity_{kind}_icon")
    left, top, right, bottom = alpha_box(ROOT / f"gfx/interface/rip_church/gc_archbishop_{kind}.dds")
    boxes[kind] = (x + left, y + top, x + right, y + bottom)
low, high = boxes["low"], boxes["high"]
assert FRAME_LEFT - low[2] == high[0] - FRAME_RIGHT, ("HC icons must sit equally far from the bar ends", low, high)
assert abs((BAR_CENTRE_X2 - (low[0] + low[2])) - ((high[0] + high[2]) - BAR_CENTRE_X2)) <= 1, "HC icons are not symmetric about the bar"
for kind, box in boxes.items():
    assert abs(box[1] + box[3] - BAR_CENTRE_Y2) <= 2, (kind, "HC icon art must be vertically centred on the bar")
assert 0 <= FRAME_LEFT - low[2] <= 3, "HC icons must stay attached to the bar ends"
assert high[2] <= COVER_X - 2, "HC priest must stay clear of the covered Select area"
heading = re.search(r'name = "rip_church_gc_capacity_heading" scripted = yes position = \{ x=(\d+) y=(\d+) \}.*?maxWidth = (\d+)', gui)
assert heading and 2 * int(heading[1]) + int(heading[3]) == BAR_CENTRE_X2 - 1, "GC heading must be centred on the bar"
assert 'name = "rip_church_gc_capacity_value"' not in gui, "the percentage is the native marker text"
for level in ("low", "high"):
    binding = next(
        block for _, block in keyed_blocks(controls, "custom_icon")
        if f"name = rip_church_gc_capacity_{level}_icon " in block
    )
    assert "potential = { religion = greek_catholic }" in binding
    assert "tooltip = rip_church_gc_capacity_hover_tt" in binding
heading_binding = next(
    block for _, block in keyed_blocks(controls, "custom_text_box")
    if "name = rip_church_authority_heading " in block
)
assert "tooltip = rip_church_authority_heading_tt" in heading_binding
assert "NOT = { religion = greek_catholic }" in heading_binding, "the shared heading must hide for GC"
gc_heading_binding = next(
    block for _, block in keyed_blocks(controls, "custom_text_box")
    if "name = rip_church_gc_capacity_heading " in block
)
assert "potential = { religion = greek_catholic }" in gc_heading_binding
assert "tooltip = rip_church_authority_heading_tt" in gc_heading_binding

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
    "At 100 HC the net country effects are 0% global missionary strength and 0% church influence",
    "owned Greek Catholic provinces have -0.375 local unrest and 0% local manpower",
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

# Check the arithmetic against the installed engine bonuses and the live RIP
# corrections. Treating compensation as the final modifier reverses the meaning
# of the HC bar, so a test of phrases alone does not protect this tooltip.
def values(block):
    return {
        key: Decimal(value)
        for key, value in re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", block)
    }

native = (vanilla_root() / "common/static_modifiers/00_static_modifiers.txt").read_text(
    encoding="utf-8-sig"
)
native_values = values(named_block(native, "patriarch_authority_global"))
native_values.update(values(named_block(native, "patriarch_authority_local")))
pa_modifiers = read("common/event_modifiers/RIP_church_redesign_modifiers.txt")
gates = read("common/scripted_triggers/rip_church_redesign_triggers.txt")
assert "always = no" in named_block(gates, "rip_church_gc_eastern")
assert "always = no" in named_block(gates, "rip_church_gc_roman")
faith = named_block(read("common/religions/zz_greek_catholic.txt"), "greek_catholic")
yearly = values(named_block(faith, "country"))["yearly_patriarch_authority"] * 100
assert yearly == Decimal("7.5") and yearly / 12 == Decimal("0.625")

custom = read("customizable_localization/rip_church_redesign.txt")
capacity = next(
    block for _, block in keyed_blocks(custom, "defined_text")
    if "name = GetChurchCapacityTooltip\n" in block
)
rows = [
    (Decimal(fraction), key)
    for fraction, key in re.findall(
        r"text = \{ trigger = \{ patriarch_authority = ([\d.]+) \} "
        r"localisation_key = (\w+) \}",
        capacity,
    )
]
assert [fraction for fraction, _ in rows] == [Decimal(i) / 100 for i in range(100, -1, -1)]
tooltip_labels = {}
for language in ("english", "french", "german", "spanish"):
    text = read(f"localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml")
    labels = dict(re.findall(r'^ (\w+):0 "(.*)"$', text, re.M))
    assert labels["rip_church_gc_capacity_hover_tt"] == "[Root.GetChurchCapacityTooltip]"
    assert labels["rip_church_authority_heading_tt"] == "[Root.GetChurchAuthorityTooltip]"
    assert labels["rip_church_native_authority_tooltip"] == "$PATRIARCH_DESCRIPTION$"
    for fraction, key in rows:
        tooltip = labels[key]
        assert "[" not in tooltip and ".GetValue" not in tooltip, "numeric leaf must be literal"
        percent = int(fraction * 100)
        band = percent // 5
        corrections = values(named_block(pa_modifiers, f"rip_church_gc_pa_country_{band}"))
        corrections.update(values(named_block(pa_modifiers, f"rip_church_gc_middle_pa_local_{band}")))
        for caption, field, multiplier in (
            ("Country missionary strength", "global_missionary_strength", 100),
            ("Clergy influence", "church_influence_modifier", 100),
            ("Owned Greek Catholic province unrest", "local_unrest", 1),
            ("Owned Greek Catholic province manpower", "local_manpower_modifier", 100),
        ):
            actual = Decimal(re.search(re.escape(caption) + r": §[WGR]([+-]?[\d.]+)", tooltip)[1])
            expected = (native_values[field] * fraction + corrections[field]) * multiplier
            assert actual == expected.quantize(Decimal("0.001")), (language, percent, caption, actual, expected)
        assert "Native bonuses" not in tooltip and "correction band" not in tooltip
        assert "Whole capacity points shown; province effects apply to owned Greek Catholic provinces" in tooltip
        assert len(tooltip) < 850, "HC hover should stay concise; individual bonus tooltips explain effects"
        assert "Icon: §Y20 HC§! · §Y5 years§!" in tooltip
        assert "Synod: §Y20 HC + 75 / 100 ducats§! · §Y10 years§!" in tooltip
        assert "Parish visit: §Y5 HC + 100 ducats + 25 ADM§! · §Y10 years§!" in tooltip
        assert "+7.5 HC per year (+0.625 per month)" in tooltip
        assert "Country modifiers affect growth" in tooltip
    if language == "english":
        tooltip_labels = labels

# Values just below a boundary stay in the previous correction band. Every
# exact five-point boundary must select the next band, including the 100 cap.
for boundary in range(5, 101, 5):
    for delta in (Decimal("-0.001"), Decimal("0"), Decimal("0.001")):
        points = min(Decimal(100), Decimal(boundary) + delta)
        _, key = next(row for row in rows if points / 100 >= row[0])
        expected_value = int(points)
        assert key == f"rip_church_readout_getchurchcapacitytooltip_{100 - expected_value}", (boundary, delta)

heading_tooltip = next(
    block for _, block in keyed_blocks(custom, "defined_text")
    if "name = GetChurchAuthorityTooltip\n" in block
)
assert heading_tooltip.count("religion = greek_catholic patriarch_authority = ") == 101
assert "trigger = { always = yes } localisation_key = rip_church_native_authority_tooltip" in heading_tooltip
assert "localisation_key = rip_church_gc_capacity_hover_tt" not in heading_tooltip, "avoid nested custom-text returns"

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

print("GC CAPACITY UI PASS: live tooltip arithmetic and band boundaries, faith income, Orthodox fallback, native art geometry")
