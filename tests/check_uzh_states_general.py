"""Contracts for the Palanok captaincy's states-general scale.

uzh_palanok_captaincy_reform carries vanilla's Res Publica "scale"
(states_general_mechanic) with two custom sides - partia_soymu on the left end
of the bar, partia_kapitaniv on the right - instead of the vanilla factions
system it used between September and October 2026. Static checks over script,
localisation and sprites: they prove the files agree with each other, not that
the engine draws or applies the scale the way the sources intend.

  * The block exists, sits inside a conditional that needs Res Publica or Winds
    of Change, names exactly two sides in left-to-right order, and the factions
    block and file are gone. The structural morale and unrest stay on the
    reform itself.
  * Each side trades something for something, no side repeats the other's
    modifier with the same sign, no side uses a currency that is a no-op in one
    of the two government types the reform is offered in, and every number is
    inside the envelope of vanilla's own sides. The net morale of each end state
    is the one the design states.
  * The bar is moved by a small, deliberate set of hooks - a war won, the three
    Palanok fortress events, three missions - each guarded by the reform and by
    has_states_general_mechanic, each with a tooltip in four languages, and
    both parties get pushed.
  * Both sides and every hook tooltip are localised in four languages; the old
    uzh_partia_* faction names are gone; vanilla's statists/orangists names are
    not overridden.
  * The art exists at the size, frame count and format of the vanilla sprite it
    stands in for (the reform card, GFX_statists, GFX_monarchists), under names
    that override no vanilla sprite.

Standard library only; the sprites themselves are redrawn and compared by
`python tools/build_uzh_states_general_icons.py --check`.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import (  # noqa: E402
    ROOT, read, named_block, matching_brace, normalized, vanilla_root, vanilla_sprite_names, _mask_comments_and_strings,
)

LANGUAGES = ("english", "french", "german", "spanish")
REFORM = "uzh_palanok_captaincy_reform"
LEFT, RIGHT = "partia_soymu", "partia_kapitaniv"
REFORM_FILE = "common/government_reforms/RIP_UZH_government_reforms.txt"
EFFECT_FILE = "common/scripted_effects/uzh_states_general_effects.txt"
GFX = "interface/rip_uzh_states_general.gfx"
ICON = "rip_gfx_reform_uzh_palanok_captaincy_icon"
# sprite -> (expected width, height, frames); the vanilla sprite each stands in for is named beside it
ART = {
    f"government_reform_{ICON}": (57, 57, 1, "a vanilla government_reform_* icon"),
    f"GFX_{LEFT}": (54, 19, 2, "GFX_statists"),
    f"GFX_{RIGHT}": (46, 25, 2, "GFX_monarchists"),
}
VANILLA_STRIPS = {"GFX_statists": "gfx/interface/republic_icon_strip.dds",
                  "GFX_monarchists": "gfx/interface/monarchism_icon_strip.dds"}
# currencies that exist in one government type only; the reform is offered as a monarchy and as a republic
TYPE_BOUND = ("republican_tradition", "legitimacy", "devotion", "horde_unity", "meritocracy", "prestige_decay")
# (hook effect, expected sign, tooltip key)
HOOK_EFFECTS = {
    "uzh_sg_captains_15_effect": (+0.15, "uzh_sg_captains_15_tt"),
    "uzh_sg_captains_20_effect": (+0.20, "uzh_sg_captains_20_tt"),
    "uzh_sg_sejm_15_effect": (-0.15, "uzh_sg_sejm_15_tt"),
    "uzh_sg_sejm_20_effect": (-0.20, "uzh_sg_sejm_20_tt"),
}
# every place the bar is moved: (file, block name, hook effect that block must call)
FORTRESS_OPTIONS = {
    "uzh_palanok.1.a": "uzh_sg_captains_15_effect",
    "uzh_palanok.1.b": "uzh_sg_sejm_15_effect",
    "uzh_palanok.2.a": "uzh_sg_captains_15_effect",
    "uzh_palanok.2.b": "uzh_sg_sejm_15_effect",
    "uzh_palanok.3.a": "uzh_sg_sejm_15_effect",
    "uzh_palanok.3.b": "uzh_sg_captains_15_effect",
}
MISSION_HOOKS = {
    "uz_mukachevo_autonomy": "uzh_sg_sejm_20_effect",
    "uz_resist_habsburgs": "uzh_sg_captains_20_effect",
    "uzh_salt_corridors": "uzh_sg_sejm_20_effect",
}
# Net land_morale: the reform's structural -5% plus the side's own modifier.
NET_MORALE = {LEFT: -0.05, RIGHT: +0.05}


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


def top_level_text(block):
    """The block's own lines with every nested block removed."""
    opening = block.index("{")
    inner = block[opening + 1: matching_brace(block, opening)]
    masked = _mask_comments_and_strings(inner)
    out, depth = [], 0
    for index, char in enumerate(masked):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0:
            out.append(char)
    return "".join(out)


def without_comments(text):
    """The text with `#` comments removed but string literals kept (normalized() blanks strings)."""
    out, in_string = [], False
    for line in text.splitlines():
        kept = []
        for char in line:
            if char == '"':
                in_string = not in_string
            if char == "#" and not in_string:
                break
            kept.append(char)
        in_string = False
        out.append("".join(kept))
    return re.sub(r"\s+", " ", "\n".join(out)).strip()


def modifiers_of(side_block):
    return {name: float(value) for name, value in re.findall(r"(\w+)\s*=\s*(-?[0-9.]+)", normalized(side_block[side_block.index("{") + 1:]))}


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
    mips = struct.unpack("<I", data[28:32])[0]
    return width, height, bits, masks, mips, data[128:]


def vanilla_side_modifiers():
    """Largest absolute value of each modifier across every vanilla states_general_mechanic side, or None."""
    root = vanilla_root()
    if root is None:
        return None
    biggest = {}
    for path in sorted((root / "common/government_reforms").glob("*.txt")):
        text = path.read_text(encoding="cp1252", errors="replace")
        masked = _mask_comments_and_strings(text)
        for match in re.finditer(r"states_general_mechanic\s*=\s*\{", masked):
            brace = text.index("{", match.start(), match.end())
            block = text[match.start(): matching_brace(text, brace) + 1]
            if block.replace(" ", "").replace("\t", "").replace("\r", "").replace("\n", "") == "states_general_mechanic={}":
                continue
            for _, side in children(block):
                for name, value in modifiers_of(side).items():
                    biggest[name] = max(biggest.get(name, 0.0), abs(value))
    return biggest


# --------------------------------------------------------------------------
# Checks: each returns a list of problems, so a planted violation can be caught
# --------------------------------------------------------------------------

def check_reform(reform_text, factions_file_exists, vanilla_envelope):
    problems = []
    try:
        reform = named_block(reform_text, REFORM)
    except KeyError:
        return [f"{REFORM} is not defined"]
    flat = normalized(reform)
    if "factions = {" in flat or factions_file_exists:
        problems.append("the reform is back on the vanilla factions system (block or common/factions/RIP_uzh_palanok_factions.txt)")
    conditionals = [block for name, block in children(reform) if name == "conditional"]
    holder = [c for c in conditionals if "states_general_mechanic" in normalized(c)]
    if len(holder) != 1:
        problems.append(f"states_general_mechanic must sit in exactly one conditional block, found {len(holder)}")
        return problems
    conditional = holder[0]
    # normalized() blanks string literals, so the DLC names are read from the comment-stripped raw text
    allow = without_comments(named_block(conditional, "allow"))
    if not re.fullmatch(r'allow = \{ OR = \{ has_dlc = "(Res Publica|Winds of Change)" has_dlc = "(Res Publica|Winds of Change)" \} \}', allow) \
            or 'has_dlc = "Res Publica"' not in allow or 'has_dlc = "Winds of Change"' not in allow:
        problems.append("the scale is not gated on Res Publica or Winds of Change")
    mechanic = named_block(conditional, "states_general_mechanic")
    sides = children(mechanic)
    names = [name for name, _ in sides]
    if names != [LEFT, RIGHT]:
        problems.append(f"the sides are {names}, expected [{LEFT}, {RIGHT}] (first block is the left end of the bar)")
        return problems
    mods = {name: modifiers_of(block) for name, block in sides}
    for name, values in mods.items():
        if not 2 <= len(values) <= 4:
            problems.append(f"{name} carries {len(values)} modifiers; vanilla's sides carry three")
        if not any(v > 0 for v in values.values()) or not any(v < 0 for v in values.values()):
            problems.append(f"{name} has no trade-off: it needs a benefit and a cost")
        for bound in TYPE_BOUND:
            if bound in values:
                problems.append(f"{name} uses {bound}, which does nothing in one of the two government types")
        if vanilla_envelope is not None:
            for modifier, value in values.items():
                limit = vanilla_envelope.get(modifier, 0.25)
                if abs(value) > limit + 1e-9:
                    problems.append(f"{name}: {modifier} = {value} is beyond vanilla's largest side value ({limit})")
    shared = [m for m in mods[LEFT] if m in mods[RIGHT] and (mods[LEFT][m] > 0) == (mods[RIGHT][m] > 0)]
    if shared:
        problems.append(f"both sides give {shared} with the same sign, so neither choice changes it")
    if set(mods[LEFT]) == set(mods[RIGHT]):
        problems.append("the two sides modify the same things; they should pull in different directions")
    own = top_level_text(reform)
    morale = re.search(r"land_morale\s*=\s*(-?[0-9.]+)", normalized("{" + named_block(reform, "modifiers")[named_block(reform, "modifiers").index("{") + 1:]))
    if "land_morale = -0.05" not in normalized(named_block(reform, "modifiers")) or "global_unrest = 1" not in normalized(named_block(reform, "modifiers")):
        problems.append("the structural land_morale -0.05 and global_unrest +1 are not on the reform itself")
    structural = float(morale.group(1)) if morale else 0.0
    for side, expected in NET_MORALE.items():
        net = round(structural + mods[side].get("land_morale", 0.0), 4)
        if abs(net - expected) > 1e-6:
            problems.append(f"net land_morale with {side} in power is {net:+.2f}, the stated design is {expected:+.2f}")
    if "has_term_election = yes" not in normalized(own) and "has_term_election = yes" not in flat:
        problems.append("the reform lost its term election")
    return problems


def check_effects(effect_text, onaction_text):
    problems = []
    for name, (amount, tooltip) in HOOK_EFFECTS.items():
        try:
            block = normalized(named_block(effect_text, name))
        except KeyError:
            problems.append(f"{name} is not defined")
            continue
        if f"has_reform = {REFORM}" not in block or "has_states_general_mechanic = yes" not in block:
            problems.append(f"{name} is not guarded by the reform and by has_states_general_mechanic")
        if f"custom_tooltip = {tooltip}" not in block:
            problems.append(f"{name} shows no tooltip ({tooltip})")
        moved = re.search(r"hidden_effect = \{ change_statists_vs_orangists = (-?[0-9.]+) \}", block)
        if not moved or abs(float(moved.group(1)) - amount) > 1e-9:
            problems.append(f"{name} does not move the bar by {amount:+.2f} inside a hidden_effect")
    try:
        war = normalized(named_block(effect_text, "uzh_sg_war_won_effect"))
        if f"has_reform = {REFORM}" not in war or "has_states_general_mechanic = yes" not in war or "total_development = ROOT" not in war \
                or not re.search(r"change_statists_vs_orangists = 0\.1", war):
            problems.append("uzh_sg_war_won_effect lost its guards or its +0.10 toward the captains")
    except KeyError:
        problems.append("uzh_sg_war_won_effect is not defined")
    if "uzh_sg_war_won_effect = yes" not in normalized(named_block(onaction_text, "on_war_won")):
        problems.append("on_war_won does not call uzh_sg_war_won_effect")
    return problems


def check_hooks(event_text, mission_text, effect_text, onaction_text):
    problems = []
    toward = {"captains": 0, "sejm": 0}
    for option, effect in FORTRESS_OPTIONS.items():
        event_id = option.rsplit(".", 1)[0]
        try:
            block = normalized(_option_block(event_text, event_id, option))
        except KeyError:
            problems.append(f"{option} is missing from events/PalanokFortress.txt")
            continue
        if f"{effect} = yes" not in block:
            problems.append(f"{option} does not call {effect}")
        toward["captains" if "captains" in effect else "sejm"] += 1
    for mission, effect in MISSION_HOOKS.items():
        try:
            block = normalized(named_block(named_block(mission_text, mission), "effect"))
        except KeyError:
            problems.append(f"mission {mission} or its effect block is missing")
            continue
        if f"{effect} = yes" not in block:
            problems.append(f"mission {mission} does not call {effect}")
        toward["captains" if "captains" in effect else "sejm"] += 1
    toward["captains"] += 1  # the war won
    komitat = normalized(named_block(mission_text, "uzh_komitat_system"))
    if "has_states_general_mechanic = yes" not in komitat or "statists_vs_orangists = 0.7" not in komitat:
        problems.append("the Komitat mission no longer reads the scale (it must wait for the Captains' Party at 0.7)")
    if min(toward.values()) < 2:
        problems.append(f"the hooks push one party only: {toward}")
    families = 1 + 1 + len(MISSION_HOOKS)  # war, fortress events, missions
    if not 2 <= families <= 6:
        problems.append(f"{families} hook families; the design allows 2 to 6")
    for effect in {e for e in list(FORTRESS_OPTIONS.values()) + list(MISSION_HOOKS.values())}:
        if effect not in HOOK_EFFECTS:
            problems.append(f"{effect} is called but is not one of the declared hook effects")
    return problems


def _option_block(event_text, event_id, option):
    event = named_block(event_text, "country_event", 1)
    # find the event whose id matches
    index = 1
    while True:
        try:
            event = named_block(event_text, "country_event", index)
        except KeyError:
            raise KeyError(event_id)
        if re.search(rf"id\s*=\s*{re.escape(event_id)}\b", event):
            break
        index += 1
    for name, block in children(event):
        if name == "option" and re.search(rf"name\s*=\s*{re.escape(option)}\b", block):
            return block
    raise KeyError(option)


def check_localisation(loc_by_language):
    problems = []
    needed = set()
    for side in (LEFT, RIGHT):
        needed.update({side, f"{side}_desc", f"{side}_MECHANIC_TOOLTIP"})
    needed.update(tooltip for _, tooltip in HOOK_EFFECTS.values())
    needed.update({REFORM, f"{REFORM}_desc", "uzh_komitat_captains_party_tt"})
    for language, keys in loc_by_language.items():
        missing = sorted(needed - keys)
        if missing:
            problems.append(f"{language}: missing {missing}")
        stale = sorted(k for k in keys if k in ("uzh_partia_soymu", "uzh_partia_kapitaniv"))
        if stale:
            problems.append(f"{language}: the old faction names are still defined: {stale}")
        renamed = sorted(k for k in keys if k in ("statists", "orangists", "monarchists"))
        if renamed:
            problems.append(f"{language}: vanilla's side names are overridden: {renamed}")
    return problems


def check_art(gfx_text, textures, reform_text, vanilla_sprites, vanilla_geometry):
    """`textures` maps a texture path to (width, height, bits, masks, mips, pixels)."""
    problems = []
    declared = {}
    for body in re.findall(r"spriteType\s*=\s*\{([^}]*)\}", gfx_text):
        name = re.search(r'name\s*=\s*"([^"]+)"', body)
        texture = re.search(r'texturefile\s*=\s*"([^"]+)"', body)
        frames = re.search(r"noOfFrames\s*=\s*(\d+)", body)
        if name and texture:
            declared[name.group(1)] = (texture.group(1), int(frames.group(1)) if frames else 1)
    for sprite, (width, height, frames, stands_in_for) in ART.items():
        if sprite not in declared:
            problems.append(f"{GFX} does not define {sprite}")
            continue
        texture, declared_frames = declared[sprite]
        if declared_frames != frames:
            problems.append(f"{sprite} declares {declared_frames} frame(s); {stands_in_for} has {frames}")
        if vanilla_sprites is not None and sprite in vanilla_sprites:
            problems.append(f"{sprite} overrides a vanilla sprite")
        info = textures.get(texture)
        if info is None:
            problems.append(f"{sprite}: {texture} does not exist")
            continue
        w, h, bits, masks, mips, pixels = info
        if (w, h) != (width, height):
            problems.append(f"{sprite}: {w}x{h}, {stands_in_for} is {width}x{height}")
        if bits != 32 or masks != (0xFF0000, 0xFF00, 0xFF, 0xFF000000) or mips > 1:
            problems.append(f"{sprite}: not uncompressed A8R8G8B8 without mipmaps like vanilla's")
        if len(pixels) < w * h * 4:
            problems.append(f"{sprite}: {len(pixels)} pixel bytes, expected {w * h * 4}")
            continue
        alpha = pixels[3: w * h * 4: 4]
        if sprite != f"government_reform_{ICON}":
            if alpha[0] != 0:
                problems.append(f"{sprite}: top-left corner is not transparent")
            if sum(1 for a in alpha if a > 128) < w * h * 0.25:
                problems.append(f"{sprite}: less than a quarter of it is opaque")
            half = w // frames
            first = [pixels[(y * w + x) * 4: (y * w + x) * 4 + 3] for y in range(h) for x in range(half)]
            second = [pixels[(y * w + half + x) * 4: (y * w + half + x) * 4 + 3] for y in range(h) for x in range(half)]
            if first == second:
                problems.append(f"{sprite}: the two frames are the same picture")
        elif min(alpha) < 255:
            problems.append(f"{sprite}: the reform card must be fully opaque like vanilla's")
        if vanilla_geometry and stands_in_for in vanilla_geometry:
            vw, vh, vframes = vanilla_geometry[stands_in_for]
            if (width, height, frames) != (vw, vh, vframes):
                problems.append(f"{sprite} does not match {stands_in_for} ({vw}x{vh}, {vframes} frames)")
    icon = re.search(r'(?m)^\s*icon\s*=\s*"([^"]+)"', named_block(reform_text, REFORM))
    if not icon or icon.group(1) != ICON:
        problems.append(f"the reform card's icon is {icon.group(1) if icon else None}, expected {ICON}")
    a, b = (textures.get(declared.get(f"GFX_{LEFT}", ("", 1))[0]), textures.get(declared.get(f"GFX_{RIGHT}", ("", 1))[0]))
    if a and b and a[5] == b[5]:
        problems.append("the two parties share one picture")
    return problems


def load_vanilla_geometry():
    root = vanilla_root()
    if root is None:
        return None
    out = {}
    for sprite, texture in VANILLA_STRIPS.items():
        path = root / texture
        if path.is_file():
            w, h, *_ = read_dds(path)
            out[sprite] = (w, h, 2)
    return out or None


# --------------------------------------------------------------------------

def planted_violations(texts, loc, textures, sprites, envelope, geometry):
    """Break the sources in memory and make sure each break is seen."""
    reform = texts["reform"]
    gfx = texts["gfx"]
    fortress = texts["events"]
    missions = texts["missions"]
    effects = texts["effects"]
    onaction = texts["onaction"]
    sample = {k: v for k, v in textures.items()}
    sprite_left = f"GFX_{LEFT}"
    left_texture = re.search(rf'name = "{sprite_left}" texturefile = "([^"]+)"', gfx)
    left_texture = left_texture.group(1) if left_texture else ""
    squashed = dict(sample)
    if left_texture in squashed:
        w, h, bits, masks, mips, pixels = squashed[left_texture]
        squashed[left_texture] = (w - 2, h, bits, masks, mips, pixels)
    cases = {
        "factions block back on the reform": check_reform(
            reform.replace("\tconditional = {\n\t\tallow = {", "\tfactions = {\n\t\tuzh_a\n\t}\n\tconditional = {\n\t\tallow = {", 1)
            .replace("\tconditional = {\r\n\t\tallow = {", "\tfactions = {\r\n\t\tuzh_a\r\n\t}\r\n\tconditional = {\r\n\t\tallow = {", 1), False, envelope),
        "factions file still present": check_reform(reform, True, envelope),
        "scale without a DLC gate": check_reform(reform.replace('has_dlc = "Winds of Change"', 'has_dlc = "Res Publica"'), False, envelope),
        "sides in the wrong order": check_reform(reform.replace(LEFT, "partia_tmp").replace(RIGHT, LEFT).replace("partia_tmp", RIGHT), False, envelope),
        "a currency that does nothing in a monarchy": check_reform(reform.replace("trade_efficiency = -0.10", "republican_tradition = -1"), False, envelope),
        "a side with no cost": check_reform(reform.replace("land_forcelimit_modifier = -0.10", "land_forcelimit_modifier = 0.10"), False, envelope),
        "a side beyond vanilla's numbers": check_reform(reform.replace("global_trade_power = 0.10", "global_trade_power = 0.60"), False, envelope) if envelope else ["no vanilla"],
        "captains' morale bonus changed": check_reform(reform.replace("land_morale = 0.10", "land_morale = 0.20"), False, envelope),
        "structural morale dropped": check_reform(reform.replace("land_morale = -0.05", "land_morale = 0.00", 1), False, envelope),
        "hook effect without its guard": check_effects(effects.replace("has_states_general_mechanic = yes", "always = yes", 1), onaction),
        "hook effect with the wrong sign": check_effects(effects.replace("change_statists_vs_orangists = -0.15", "change_statists_vs_orangists = 0.15", 1), onaction),
        "war hook dropped from on_war_won": check_effects(effects, onaction.replace("uzh_sg_war_won_effect = yes", "# gone", 1)),
        "fortress option without its hook": check_hooks(fortress.replace("uzh_sg_sejm_15_effect = yes", "# gone", 1), missions, effects, onaction),
        "mission without its hook": check_hooks(fortress, missions.replace("uzh_sg_captains_20_effect = yes", "# gone", 1), effects, onaction),
        "komitat mission no longer reads the scale": check_hooks(fortress, missions.replace("statists_vs_orangists = 0.7", "always = yes", 1), effects, onaction),
        "a hook tooltip missing in German": check_localisation({**loc, "german": loc["german"] - {"uzh_sg_sejm_15_tt"}}),
        "the faction names back in Spanish": check_localisation({**loc, "spanish": loc["spanish"] | {"uzh_partia_soymu"}}),
        "vanilla's Statists renamed": check_localisation({**loc, "english": loc["english"] | {"statists"}}),
        "a sprite the wrong size": check_art(gfx, squashed, reform, sprites, geometry),
        "a vanilla sprite overridden": check_art(gfx.replace(f"GFX_{LEFT}", "GFX_statists"), textures, reform,
                                                 (sprites or frozenset()) | {"GFX_statists"}, geometry),
        "a single-frame strip": check_art(gfx.replace("noOfFrames = 2", "noOfFrames = 1", 1), textures, reform, sprites, geometry),
        "vanilla icon back on the card": check_art(gfx, textures, reform.replace(ICON, "trading_city", 1), sprites, geometry),
    }
    return [name for name, problems in cases.items() if not problems], len(cases)


def main():
    texts = {
        "reform": read(REFORM_FILE),
        "gfx": read(GFX) if (ROOT / GFX).is_file() else "",
        "events": read("events/PalanokFortress.txt"),
        "missions": read("missions/Zakarpatta_Missions.txt"),
        "effects": read(EFFECT_FILE),
        "onaction": read("common/on_actions/RIP_UZH_on_actions.txt"),
    }
    loc = {language: loc_keys(language) for language in LANGUAGES}
    envelope = vanilla_side_modifiers()
    sprites = vanilla_sprite_names()
    geometry = load_vanilla_geometry()
    textures = {}
    for texture in re.findall(r'texturefile\s*=\s*"([^"]+)"', texts["gfx"]):
        path = ROOT / texture
        if path.is_file():
            textures[texture] = read_dds(path)
    problems = []
    problems += check_reform(texts["reform"], (ROOT / "common/factions/RIP_uzh_palanok_factions.txt").exists(), envelope)
    problems += check_effects(texts["effects"], texts["onaction"])
    problems += check_hooks(texts["events"], texts["missions"], texts["effects"], texts["onaction"])
    problems += check_localisation(loc)
    problems += check_art(texts["gfx"], textures, texts["reform"], sprites, geometry)
    unseen, planted = planted_violations(texts, loc, textures, sprites, envelope, geometry)
    problems += [f"planted violation not caught: {name}" for name in unseen]
    if problems:
        print("UZH STATES GENERAL CHECK: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    note = "" if envelope is not None else " (vanilla number envelope and sprite geometry SKIPPED: no EU4 install)"
    print(f"UZH STATES GENERAL CHECK: PASS (2 sides, {len(HOOK_EFFECTS)} hook effects + war hook, {len(FORTRESS_OPTIONS)} fortress options, "
          f"{len(MISSION_HOOKS)} missions, {len(ART)} sprites, 4 languages; {planted} planted violations caught){note}")
    print("LIMIT: static contracts. The bar, its tooltips and its art were observed in EU4 1.37.5 by hand (see docs/RUTHENIAN_GOVERNMENT_UI.uk.md); no automated render test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
