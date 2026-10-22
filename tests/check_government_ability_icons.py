"""Contracts for the Galician, Volhynian and Lithuanian government-ability panels.

Static checks over script, sprites and localisation: they prove the files agree
with each other, not that the engine draws the panel the way the preview does.

  * Boyar Council (3 buttons), Crown Ordinances (6), Magnate Senate (3), Pany Rada
    (3) and the three Resolution mechanics (2 each) use twenty-one different bespoke
    sprites - none of vanilla's Cossack ability icons. The Pany Rada's three share one
    shield frame that no other mechanic uses, and each button has its own sprite
    (confirm, lord, retinues), not one borrowed from a sibling mechanic.
  * The six crown ordinances are six DIFFERENT buttons (chancery, settlement,
    cadastral, urbarial, toleration, frontier guard), one picture each, each on a
    modifier of its own that stands for ten years and no engine cooldown (seen in EU4 1.37.5: the engine
    shared the cooldown of one ordinance with the other five). There is no rescind
    button: an earlier layout paired every ordinance with a rescind button wearing the
    same picture and called that six abilities.
  * Every sprite is a defined, existing 82x82 uncompressed DDS with a shaped
    alpha, and no two of them are the same picture.
  * Every button, ordinance modifier, resolution and government attribute that the
    Austrian crown and the resolution reforms show has text in all four languages.
  * The appanage privilege is attached to the nobility, the Chernihiv Ruina carries
    its government-attribute exemption twice (as vanilla's Dutch Revolt does) and
    the crown authority clears every ordinance it enacted (six modifiers, and the flags
    of the older, permanent ordinances).

Standard library only; the sprites themselves are redrawn and compared by
`python tools/build_government_ability_icons.py --check`. How the panels look in the
game window was checked by hand, not by this script.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, read, named_block, matching_brace, normalized, vanilla_root, _mask_comments_and_strings  # noqa: E402

LANGUAGES = ("english", "french", "german", "spanish")
EDGE = 82
GFX = "interface/rip_ability_icons.gfx"

RESOLUTIONS_FILE = "common/government_mechanics/rip_institutional_resolutions.txt"
MECHANICS = [
    ("common/government_mechanics/rip_hlc_boyar_council.txt", "hlc_boyar_council_mechanic", 3),
    ("common/government_mechanics/rip_hlc_austrian_reorganization.txt", "hlc_austrian_reorganization_mechanic", 6),
    ("common/government_mechanics/rip_vln_magnate_senate.txt", "vln_magnate_senate_mechanic", 3),
    ("common/government_mechanics/rip_lit_pany_rada.txt", "lit_pany_rada_mechanic", 3),
    (RESOLUTIONS_FILE, "rip_municipal_resolutions_mechanic", 2),
    (RESOLUTIONS_FILE, "rip_chancery_resolutions_mechanic", 2),
    (RESOLUTIONS_FILE, "rip_register_resolutions_mechanic", 2),
]
ORDINANCES = ("chancery", "settlement", "cadastral", "urbarial", "toleration", "frontier")
LEGACY_FLAGGED = ("chancery", "settlement", "cadastral")      # the permanent ordinances of an older save still carry a flag
ORDINANCE_ICONS = {"chancery": "GFX_rip_chancery_ordinance", "settlement": "GFX_rip_settlement_ordinance", "cadastral": "GFX_rip_cadastre_ordinance",
                   "urbarial": "GFX_rip_urbarial_ordinance", "toleration": "GFX_rip_toleration_ordinance", "frontier": "GFX_rip_frontier_ordinance"}
SPRITES = 21
# Pany Rada: button -> sprite, in file order; the frame is the shield no other mechanic uses
RADA_FILE = "common/government_mechanics/rip_lit_pany_rada.txt"
RADA_MECHANIC = "lit_pany_rada_mechanic"
RADA_BUTTONS = {
    "lit_seek_the_radas_confirmation": "GFX_rip_rada_confirm",
    "lit_win_over_a_wavering_lord": "GFX_rip_rada_lord",
    "lit_the_radas_own_retinues": "GFX_rip_rada_retinues",
}


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def children(block):
    """Top-level `name = { ... }` children of a block, in file order."""
    opening = block.index("{")
    inner = block[opening + 1: matching_brace(block, opening)]
    masked = _mask_comments_and_strings(inner)
    out, pos = [], 0
    pattern = re.compile(r"(\w+)\s*=\s*\{")
    while True:
        match = pattern.search(masked, pos)
        if not match:
            return out
        brace = inner.index("{", match.start(), match.end())
        close = matching_brace(inner, brace)
        out.append((match.group(1), inner[match.start(): close + 1]))
        pos = close + 1


def interactions(text, mechanic):
    return children(named_block(named_block(text, mechanic), "interactions"))


def icon_of(block):
    match = re.search(r"(?m)^\s*icon\s*=\s*(\w+)", block)
    return match.group(1) if match else None


def loc_keys(language):
    keys = set()
    for path in (ROOT / "localisation").rglob(f"*l_{language}.yml"):
        keys.update(re.findall(r"(?m)^ ([^\s:#]+):\d+ ", path.read_text(encoding="utf-8-sig")))
    return keys


def read_dds(path):
    data = path.read_bytes()
    assert data[:4] == b"DDS ", f"{path.name}: not a DDS file"
    height, width = struct.unpack("<2I", data[12:20])
    bits = struct.unpack("<I", data[88:92])[0]
    masks = struct.unpack("<4I", data[92:108])
    pixels = data[128:]
    return width, height, bits, masks, pixels


# --------------------------------------------------------------------------
# Checks: each returns a list of problems, so a planted violation can be caught
# --------------------------------------------------------------------------

def check_buttons(path, mechanic, expected, text, defined_sprites):
    problems = []
    found = interactions(text, mechanic)
    if len(found) != expected:
        problems.append(f"{mechanic} has {len(found)} buttons, expected {expected}")
    icons = [icon_of(block) for _, block in found]
    for name, icon in zip((n for n, _ in found), icons):
        if icon is None:
            problems.append(f"{name} has no icon")
        elif icon.startswith("GFX_cossacks_ability_"):
            problems.append(f"{name} still borrows vanilla's {icon}")
        elif icon not in defined_sprites:
            problems.append(f"{name} uses {icon}, which {GFX} does not define")
    if len(set(icons)) != len(icons):
        problems.append(f"{mechanic} reuses an icon between its buttons")
    return problems


def check_ordinance_layout(text):
    """Six different enact buttons in the order of the two rows, each with its own picture, token, term and sentence tooltip."""
    problems = []
    found = interactions(text, "hlc_austrian_reorganization_mechanic")
    names = [name for name, _ in found]
    want = [f"hlc_enact_{o}_ordinance" for o in ORDINANCES]
    if names != want:
        problems.append(f"ordinance buttons are {names}, expected the six different ordinances {want} (no rescind buttons)")
        return problems
    blocks = dict(found)
    tokens = set()
    for ordinance in ORDINANCES:
        button = blocks[f"hlc_enact_{ordinance}_ordinance"]
        modifier = f"hlc_{ordinance}_ordinance_modifier"
        token = f"hlc_{ordinance}_ordinance"
        tokens.add(token)
        if icon_of(button) != ORDINANCE_ICONS[ordinance]:
            problems.append(f"{ordinance}: wears {icon_of(button)}, expected {ORDINANCE_ICONS[ordinance]}")
        if "cooldown_years = 0" not in button or "cooldown_token" in button or "cooldown_desc" in button:
            problems.append(f"{ordinance}: must have cooldown_years = 0 and no cooldown token or name (the engine shares an ordinance cooldown between all six)")
        effect = normalized(named_block(button, "effect"))
        if f"name = {modifier} duration = 3650" not in effect:
            problems.append(f"{ordinance}: enact does not add {modifier} for ten years (3650 days)")
        if "set_country_flag" in effect:
            problems.append(f"{ordinance}: enact sets a flag; the modifier is the only record of 'in force'")
        trigger = normalized(named_block(button, "trigger"))
        if f"NOT = {{ has_country_modifier = {modifier} }}" not in trigger:
            problems.append(f"{ordinance}: enact is not blocked while the ordinance stands")
        if f"tooltip = hlc_{ordinance}_ordinance_not_in_force_tt" not in trigger:
            problems.append(f"{ordinance}: a blocked enact button shows a raw modifier name, not a sentence")
        if "tooltip = hlc_ordinance_slot_free_tt hlc_ordinance_slot_free = yes" not in trigger:
            problems.append(f"{ordinance}: enact does not require a free slot inside a sentence tooltip")
    if "rescind" in _mask_comments_and_strings(text).lower():
        problems.append("a rescind button or comment is back in the crown ordinances")
    return problems


def load_sprites():
    """The sprites the gfx file defines, and the decoded DDS behind each (None where the file is missing)."""
    definitions = dict(re.findall(r'spriteType = \{ name = "(GFX_rip_\w+)" texturefile = "([^"]+)" \}', read(GFX)))
    loaded = {}
    for name, texture in definitions.items():
        path = ROOT / texture
        loaded[name] = read_dds(path) if path.is_file() else None
    return definitions, loaded


def silhouette(pixels):
    """The opaque outline of a sprite, one byte per pixel: a frame shape shows in it alone."""
    return bytes(1 if a > 127 else 0 for a in pixels[3::4])


def differing(a, b):
    """Fraction of two equal-length byte strings that differ."""
    return sum(1 for x, y in zip(a, b) if x != y) / max(1, len(a))


def check_rada_assignment(text):
    """Each Pany Rada button wears its own sprite (confirm, lord, retinues), not one borrowed from a sibling mechanic."""
    problems = []
    found = dict(interactions(text, RADA_MECHANIC))
    for button, sprite in RADA_BUTTONS.items():
        if button not in found:
            problems.append(f"{button} is missing from {RADA_MECHANIC}")
        elif icon_of(found[button]) != sprite:
            problems.append(f"{button} uses {icon_of(found[button])}, expected {sprite}")
    return problems


def check_rada_frame(images):
    """The Pany Rada's three sprites share one frame silhouette, and no other mechanic's frame looks like it."""
    problems = []
    rada = [name for name in RADA_BUTTONS.values() if name in images]
    shapes = {name: silhouette(images[name]) for name in images}
    for first in rada:
        for second in rada:
            if first < second and differing(shapes[first], shapes[second]) > 0.01:
                problems.append(f"{first} and {second} do not share one frame shape")
    for first in rada:
        for other in shapes:
            if other not in RADA_BUTTONS.values() and differing(shapes[first], shapes[other]) < 0.08:
                problems.append(f"{first} has the frame of {other}: the Pany Rada needs a shape of its own")
    return problems


def check_rada_art(images):
    """Each Pany Rada sprite is a different picture from the Magnate Senate's buy-off, banners and summon art."""
    problems = []
    for first in (name for name in RADA_BUTTONS.values() if name in images):
        for second in (name for name in ("GFX_rip_senate_buyoff", "GFX_rip_senate_banners", "GFX_rip_senate_summon") if name in images):
            a, b = images[first], images[second]
            far = sum(1 for x in range(0, len(a), 4 * 7) if abs(a[x] - b[x]) + abs(a[x + 1] - b[x + 1]) + abs(a[x + 2] - b[x + 2]) > 30)
            if far < len(a) // (4 * 7) * 0.5:
                problems.append(f"{first} is too close to {second}")
    return problems


def check_sprites(definitions=None, loaded=None):
    problems = []
    if definitions is None:
        definitions, loaded = load_sprites()
    if len(definitions) != SPRITES:
        problems.append(f"{GFX} defines {len(definitions)} sprites, expected {SPRITES}")
    images = {}
    for name, texture in definitions.items():
        if loaded[name] is None:
            problems.append(f"{name}: {texture} does not exist")
            continue
        width, height, bits, masks, pixels = loaded[name]
        if (width, height, bits) != (EDGE, EDGE, 32):
            problems.append(f"{name}: {width}x{height} at {bits} bits, expected {EDGE}x{EDGE} at 32")
        if masks != (0xFF0000, 0xFF00, 0xFF, 0xFF000000):
            problems.append(f"{name}: pixel masks {[hex(m) for m in masks]} are not vanilla's uncompressed A8R8G8B8")
        if len(pixels) != EDGE * EDGE * 4:
            problems.append(f"{name}: {len(pixels)} pixel bytes, expected {EDGE * EDGE * 4}")
            continue
        alpha = pixels[3::4]
        if alpha[0] != 0 or alpha[EDGE * EDGE // 2 + EDGE // 2] != 255:
            problems.append(f"{name}: corner is not transparent or centre is not opaque")
        if sum(1 for a in alpha if a > 200) < EDGE * EDGE * 0.45:
            problems.append(f"{name}: less than 45% of the sprite is opaque")
        images[name] = pixels
    names = sorted(images)
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            a, b = images[first], images[second]
            differing = sum(1 for x in range(0, len(a), 4 * 7) if abs(a[x] - b[x]) + abs(a[x + 1] - b[x + 1]) + abs(a[x + 2] - b[x + 2]) > 30)
            if differing < len(a) // (4 * 7) * 0.15:
                problems.append(f"{first} and {second} are practically the same picture")
    return problems, set(definitions), images


def check_localisation(text_by_mechanic):
    problems = []
    needed = set()
    for mechanic_text, mechanic in text_by_mechanic:
        needed.add(f"ability_{mechanic}")
        for name, block in interactions(mechanic_text, mechanic):
            needed.update({name, f"{name}_desc"})
            needed.update(re.findall(r"cooldown_desc = (\w+)", block))
    for ordinance in ORDINANCES:
        needed.update({f"hlc_{ordinance}_ordinance_modifier", f"desc_hlc_{ordinance}_ordinance_modifier",
                       f"hlc_{ordinance}_ordinance_not_in_force_tt"})
    needed.update({"hlc_ordinance_slot_free_tt", "rip_resolution_none_in_force_tt",
                   "rip_resolution_lock_over_tt", "rip_resolution_cooldown_desc"})
    for modifier in ("municipal_charters", "municipal_accounts", "chancery_service", "chancery_rights", "register_muster", "register_settlement"):
        needed.update({f"rip_gov_{modifier}", f"desc_rip_gov_{modifier}"})
    needed.update({
        "hlc_incorporate_appanage", "hlc_incorporate_appanage_title",
        "hlc_incorporate_appanage_tooltip", "hlc_incorporate_appanage_desc",
        "estate_nobles_hlc_strong_appanages", "estate_nobles_hlc_strong_appanages_desc",
        "estate_nobles_hlc_strong_appanages_trigger_tooltip",
        "mechanic_hlc_enables_incorporated_appanages_yes", "mechanic_hlc_disables_chernihiv_ruina_yes",
        "kyivan_boyar_council_established_req_tt",
    })
    for language in LANGUAGES:
        missing = sorted(needed - loc_keys(language))
        if missing:
            problems.append(f"{language}: missing {missing}")
    return problems


def check_ordinance_modifiers(modifiers_text, reform_text, effects_text):
    problems = []
    for ordinance in ORDINANCES:
        name = f"hlc_{ordinance}_ordinance_modifier"
        if not re.search(rf"(?m)^{name}\s*=\s*\{{", modifiers_text):
            problems.append(f"{name} is not defined in west_ukraine_modifiers.txt")
    # removed_effect hands over to one scripted effect (also used by the yearly
    # sweep), so the flags and modifiers are checked where they are cleared.
    # tests/check_hlc_ordinances.py covers the sweep and the rest of the clean-up.
    removed = named_block(named_block(reform_text, "hlc_crown_authority_reform"), "removed_effect")
    if "hlc_clear_ordinances_effect = yes" not in removed:
        problems.append("hlc_crown_authority_reform removed_effect does not call hlc_clear_ordinances_effect")
    cleared = named_block(effects_text, "hlc_clear_ordinances_effect")
    for ordinance in ORDINANCES:
        needle = f"remove_country_modifier = hlc_{ordinance}_ordinance_modifier"
        if needle not in cleared:
            problems.append(f"hlc_clear_ordinances_effect lacks {needle}")
    for ordinance in LEGACY_FLAGGED:
        needle = f"clr_country_flag = hlc_{ordinance}_ordinance_active"
        if needle not in cleared:
            problems.append(f"hlc_clear_ordinances_effect lacks {needle} (an older save still holds the flag)")
    cadastral = named_block(modifiers_text, "hlc_cadastral_ordinance_modifier")
    if "global_tax_modifier" not in cadastral or "nobles_loyalty_modifier = -" not in cadastral:
        problems.append("the cadastral ordinance must pay its tax bonus with noble loyalty")
    return problems


def check_appanage_and_ruina(estate_text, disaster_text, reform_text):
    problems = []
    if not re.search(r"(?m)^\s*estate_nobles_hlc_strong_appanages\s*$", named_block(estate_text, "privileges")):
        problems.append("estate_nobles_hlc_strong_appanages is not listed in the nobility's privileges (engine: 'unused')")
    ruina = named_block(disaster_text, "chernihiv_ruina")
    guard = "has_government_attribute = hlc_disables_chernihiv_ruina"
    if guard not in normalized(named_block(ruina, "potential")):
        problems.append("chernihiv_ruina potential lacks the HLC exemption")
    start = normalized(named_block(ruina, "can_start"))
    if f"limit = {{ {guard} }} NOT = {{ {guard} }}" not in start:
        problems.append("chernihiv_ruina can_start lacks the second guard vanilla's Dutch Revolt carries")
    crown = named_block(reform_text, "hlc_crown_authority_reform")
    if "hlc_disables_chernihiv_ruina = yes" not in crown or "hlc_austrian_reorganization_mechanic" not in crown:
        problems.append("hlc_crown_authority_reform no longer carries the Ruina exemption and the ordinances")
    bureau = named_block(reform_text, "hlc_austrian_bureaucracy_reform")
    if "hlc_enables_incorporated_appanages = yes" not in bureau:
        problems.append("hlc_austrian_bureaucracy_reform no longer opens the Incorporate the Appanage action")
    return problems


def check_boyar_republic_tooltip(reform_text):
    trigger = named_block(named_block(reform_text, "kyivan_boyar_republic_reform"), "trigger")
    wrapped = re.search(r"custom_trigger_tooltip\s*=\s*\{\s*tooltip\s*=\s*kyivan_boyar_council_established_req_tt\s+has_country_flag\s*=\s*kyiv_boyar_council_established", trigger)
    return [] if wrapped else ["the council flag in the Boyar Republic's trigger shows as a raw flag name"]


def check_custom_attributes():
    """Every custom attribute a RIP reform sets has a tooltip: from vanilla or from this mod."""
    root = vanilla_root()
    if not root:
        return [], "SKIP vanilla attribute audit (no EU4 install found)"
    vanilla_reforms = "\n".join(p.read_text(encoding="cp1252", errors="replace") for p in (root / "common/government_reforms").glob("*.txt"))
    vanilla_loc = set()
    for path in (root / "localisation").glob("*_l_english.yml"):
        vanilla_loc.update(re.findall(r"(?m)^ ([^\s:#]+):\d+ ", path.read_text(encoding="utf-8-sig", errors="replace")))
    mod_loc = loc_keys("english")
    problems = []
    for path in sorted((ROOT / "common/government_reforms").glob("RIP_*.txt")):
        text = path.read_text(encoding="cp1252")
        for match in re.finditer(r"(?m)^\s*custom_attributes\s*=\s*\{", _mask_comments_and_strings(text)):
            block = text[match.start(): matching_brace(text, text.index("{", match.start(), match.end())) + 1]
            top = ""
            depth = 0
            for ch in block[block.index("{") + 1:-1]:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                elif depth == 0:
                    top += ch
            for attribute, value in re.findall(r"([A-Za-z0-9_]+)\s*=\s*(yes|no)", _mask_comments_and_strings(top)):
                key = f"mechanic_{attribute}_{value}"
                if key not in mod_loc and key not in vanilla_loc:
                    problems.append(f"{path.name}: attribute {attribute} = {value} has no tooltip ({key})")
    return problems, None


# --------------------------------------------------------------------------

def planted_violations(texts, sprites, images):
    """Break the sources in memory and make sure each break is seen."""
    cossack = texts["chancery"].replace("GFX_rip_chancery_ordinance", "GFX_cossacks_ability_ADM", 1)
    mechanic = named_block(texts["chancery"], "hlc_austrian_reorganization_mechanic")
    missing_button = texts["chancery"].replace(
        named_block(named_block(mechanic, "interactions"), "hlc_enact_frontier_ordinance"), "", 1
    )
    cases = {
        "vanilla icon back in the chancery": check_buttons("x", "hlc_austrian_reorganization_mechanic", 6, cossack, sprites),
        "five buttons instead of six": check_buttons("x", "hlc_austrian_reorganization_mechanic", 6, missing_button, sprites),
        "a button folded back out of the layout": check_ordinance_layout(missing_button),
        "a rescind button under another name": check_ordinance_layout(
            texts["chancery"].replace("hlc_enact_frontier_ordinance = {", "hlc_rescind_chancery_ordinance = {", 1)),
        "rows in another order": check_ordinance_layout(
            texts["chancery"].replace("hlc_enact_cadastral_ordinance = {", "hlc_swap = {", 1)),
        "two ordinances on one picture": check_ordinance_layout(
            texts["chancery"].replace("GFX_rip_toleration_ordinance", "GFX_rip_urbarial_ordinance", 1)),
        "a cooldown token back on an ordinance": check_ordinance_layout(
            texts["chancery"].replace("\t\t\tcooldown_years = 0\n", "\t\t\tcooldown_years = 0\n\t\t\tcooldown_token = hlc_chancery_ordinance\n", 1)),
        "an engine cooldown of ten years": check_ordinance_layout(
            texts["chancery"].replace("\t\t\tcooldown_years = 0\n", "\t\t\tcooldown_years = 10\n", 1)),
        "a cooldown name back on an ordinance": check_ordinance_layout(
            texts["chancery"].replace("\t\t\tcooldown_years = 0\n", "\t\t\tcooldown_years = 0\n\t\t\tcooldown_desc = hlc_ordinance_cooldown_desc\n", 1)),
        "raw modifier name in an ordinance button": check_ordinance_layout(
            texts["chancery"].replace("tooltip = hlc_chancery_ordinance_not_in_force_tt", "tooltip = nothing", 1)),
        "an ordinance that never ends": check_ordinance_layout(
            texts["chancery"].replace("name = hlc_toleration_ordinance_modifier\n\t\t\t\t\tduration = 3650", "name = hlc_toleration_ordinance_modifier\n\t\t\t\t\tduration = -1", 1)),
        "an ordinance without the slot rule": check_ordinance_layout(
            texts["chancery"].replace("hlc_ordinance_slot_free = yes", "always = yes", 1)),
        "estate without the appanage privilege": check_appanage_and_ruina(
            texts["estate"].replace("estate_nobles_hlc_strong_appanages", "estate_nobles_nothing"), texts["disaster"], texts["reform"]),
        "Ruina without its can_start guard": check_appanage_and_ruina(
            texts["estate"], texts["disaster"].replace("limit = { has_government_attribute = hlc_disables_chernihiv_ruina }", "limit = { always = no }"), texts["reform"]),
        "crown authority that leaves ordinances behind": check_ordinance_modifiers(
            texts["modifiers"], texts["reform"], texts["effects"].replace("remove_country_modifier = hlc_frontier_ordinance_modifier", "# nothing")),
        "crown authority that no longer clears them": check_ordinance_modifiers(
            texts["modifiers"], texts["reform"].replace("hlc_clear_ordinances_effect = yes", "# nothing"), texts["effects"]),
        "an older save's flag left behind": check_ordinance_modifiers(
            texts["modifiers"], texts["reform"], texts["effects"].replace("clr_country_flag = hlc_settlement_ordinance_active", "# nothing")),
        "raw council flag in the boyar republic": check_boyar_republic_tooltip(
            texts["kyiv"].replace("custom_trigger_tooltip", "hidden_trigger_x")),
        "Pany Rada button back on a vanilla Cossack icon": check_buttons(
            RADA_FILE, RADA_MECHANIC, 3, texts["rada"].replace("icon = GFX_rip_rada_confirm", "icon = GFX_cossacks_ability_ADM", 1), sprites
        ) + check_rada_assignment(texts["rada"].replace("icon = GFX_rip_rada_confirm", "icon = GFX_cossacks_ability_ADM", 1)),
        "Pany Rada button wearing the Senate's buy-off sprite": check_rada_assignment(
            texts["rada"].replace("icon = GFX_rip_rada_lord", "icon = GFX_rip_senate_buyoff", 1)),
        "Pany Rada buttons wearing three sprites of other mechanics": check_rada_assignment(
            texts["rada"].replace("GFX_rip_rada_confirm", "GFX_rip_boyar_office").replace("GFX_rip_rada_lord", "GFX_rip_boyar_claimant")
            .replace("GFX_rip_rada_retinues", "GFX_rip_boyar_example")),
        "a resolution button on a vanilla Cossack icon": check_buttons(
            RESOLUTIONS_FILE, "rip_chancery_resolutions_mechanic", 2,
            texts["resolutions"].replace("icon = GFX_rip_resolution_chancery_rights", "icon = GFX_cossacks_ability_DIP", 1), sprites),
        "two resolution buttons on one picture": check_buttons(
            RESOLUTIONS_FILE, "rip_register_resolutions_mechanic", 2,
            texts["resolutions"].replace("icon = GFX_rip_resolution_register_settlement", "icon = GFX_rip_resolution_register_muster", 1), sprites),
    }
    # pixel cases: the Rada sprite is swapped for another picture in memory (skipped when a sprite is missing, which check_sprites reports)
    if all(name in images for name in ("GFX_rip_rada_lord", "GFX_rip_rada_retinues", "GFX_rip_senate_buyoff", "GFX_rip_senate_banners")):
        cases["Pany Rada lord drawn in the Senate's arch frame"] = check_rada_frame(
            {**images, "GFX_rip_rada_lord": images["GFX_rip_senate_buyoff"]})
        cases["Pany Rada retinues copying the Senate's banners"] = check_rada_art(
            {**images, "GFX_rip_rada_retinues": images["GFX_rip_senate_banners"]})
    return [name for name, problems in cases.items() if not problems], len(cases)


def main():
    texts = {
        "chancery": read("common/government_mechanics/rip_hlc_austrian_reorganization.txt"),
        "estate": read("common/estates/02_nobility.txt"),
        "disaster": read("common/disasters/shared_ruthenian_disasters.txt"),
        "modifiers": read("common/event_modifiers/west_ukraine_modifiers.txt"),
        "reform": read("common/government_reforms/RIP_HLC_government_reforms.txt"),
        "effects": read("common/scripted_effects/rip_hlc_ordinance_effects.txt"),
        "kyiv": read("common/government_reforms/RIP_KIE_KRU_government_reforms.txt"),
        "rada": read(RADA_FILE),
        "resolutions": read(RESOLUTIONS_FILE),
    }
    sprite_problems, sprites, images = check_sprites()
    problems = list(sprite_problems)
    mechanic_texts = []
    for path, mechanic, expected in MECHANICS:
        text = read(path)
        mechanic_texts.append((text, mechanic))
        problems += check_buttons(path, mechanic, expected, text, sprites)
    problems += check_ordinance_layout(texts["chancery"])
    problems += check_localisation(mechanic_texts)
    problems += check_ordinance_modifiers(texts["modifiers"], texts["reform"], texts["effects"])
    problems += check_appanage_and_ruina(texts["estate"], texts["disaster"], texts["reform"])
    problems += check_boyar_republic_tooltip(texts["kyiv"])
    problems += check_rada_assignment(texts["rada"])
    problems += check_rada_frame(images)
    problems += check_rada_art(images)
    attribute_problems, note = check_custom_attributes()
    problems += attribute_problems
    unseen, planted = planted_violations(texts, sprites, images)
    problems += [f"planted violation not caught: {name}" for name in unseen]
    if problems:
        print("GOVERNMENT ABILITY ICONS CHECK: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"GOVERNMENT ABILITY ICONS CHECK: PASS ({SPRITES} sprites, {SPRITES} buttons in {len(MECHANICS)} mechanics, 4 languages; {planted} planted violations caught)")
    print("LIMIT: static contracts. Only the older panels were checked by eye in EU4 1.37.5 on 2026-10-17 (see docs/RUTHENIAN_GOVERNMENT_UI.uk.md); no automated render test.")
    if note:
        print(note)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
