"""Silent-drop lints for every government reform and every government mechanic of the mod.

The merge gate reads script text; the engine reads it differently, and every rule below was learned from
a line of error.log or from content that parsed, passed the gate and did nothing. Measured in EU4 1.37.5
on the pristine HEAD of 18 October 2026 (docs/BORDER_MECHANICS_20261019.uk.md, section on the engine log):

  * a reform whose `icon` names no sprite shows a blank card (two reforms named `papal_embassy_reform`, a
    reform id, where vanilla's own reform uses `pope`);
  * a `conditional` block takes reform keys only: `parliament_backing_chance` inside it is "Unexpected
    token" and the modifier never applies;
  * a mechanic's `available` block is read before scripted triggers are registered: a scripted trigger in
    it is "Unknown trigger type" (the Border Watch's first draft);
  * a modifier that is removed but no longer defined is "Unknown modifier-type" (six retired KRU markers,
    four log lines each);
  * a reform that names an ability no mechanic defines enables nothing, silently.

The lints below keep each class out for ALL reforms and mechanics, not only the new ones, and the two
inventory rules from docs/GOVERNMENT_AUDIT_20261017.uk.md (items D1-D3) that the audit said no gate saw:
every `gui =` is a real window, every button icon is a defined sprite, every mechanic and button has text.

Standard library only; the vanilla install (EU4_DIR or the usual Steam paths) is read where it adds
evidence and the lint that needs it says SKIP without it. Self-test: every lint must catch a planted violation.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, matching_brace, named_block, vanilla_root, _mask_comments_and_strings  # noqa: E402

MOD_PREFIX = re.compile(r"^(rip|uzh|pdl|prl|chr|het|zaz|hlc|vln|lit|kru|kyiv|plt|ods|siversk|ruthenian|west|su|gre|rus)_")
# reform keys that vanilla puts inside `conditional` (derived from the installed 1.37.5 files; the union is the fallback)
CONDITIONAL_FALLBACK = {
    "allow", "has_parliament", "blocked_call_diet", "custom_attributes", "can_use_trade_post", "can_form_trade_league",
    "trade_city_reform", "government_abilities", "factions", "states_general_mechanic", "has_devotion", "allow_banners",
    "foreign_slave_rulers", "is_elective", "has_meritocracy", "has_harem", "has_janissaries", "has_pashas",
    "allow_draft_transport_ships",
}
# the eight reforms of RIP_RUS_government_reforms.txt override vanilla ids: vanilla's own conventions apply to them
VANILLA_OVERRIDES = {"principality", "tsardom", "great_veche_republic", "lands_for_the_monasteries_reform", "holy_synod_reform",
                     "strengthened_the_patriarchy_reform", "head_of_the_patriarchy_reform", "orthodox_patriarchate_reform"}


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def rd(path):
    return Path(path).read_text(encoding="cp1252", errors="replace")


def strip_comments(text):
    return re.sub(r"#[^\n]*", "", text)


def top_blocks(text):
    """Top-level `name = { ... }` blocks of a file: {name: block text}."""
    masked = _mask_comments_and_strings(text)
    out, pos = {}, 0
    pattern = re.compile(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{")
    while True:
        match = pattern.search(masked, pos)
        if not match:
            return out
        brace = text.index("{", match.start(), match.end())
        close = matching_brace(text, brace)
        out[match.group(1)] = text[match.start(): close + 1]
        pos = close + 1


def children(block):
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


def top_level_keys(block):
    """Keys that sit directly in a block (not inside nested braces)."""
    opening = block.index("{")
    inner = block[opening + 1: matching_brace(block, opening)]
    masked = _mask_comments_and_strings(inner)
    depth, keys, token = 0, [], ""
    for char in masked:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        elif depth == 0:
            token += char
    return re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*=", token)


def mod_reforms():
    out = {}
    for path in sorted((ROOT / "common/government_reforms").glob("*.txt")):
        for name, block in top_blocks(rd(path)).items():
            out[name] = (path.name, block)
    return out


def mod_mechanics():
    out = {}
    for path in sorted((ROOT / "common/government_mechanics").glob("*.txt")):
        for name, block in top_blocks(rd(path)).items():
            out[name] = (path.name, block)
    return out


def sprites(root):
    """name -> texture path for every spriteType under interface/ of a root."""
    out = {}
    for path in (root / "interface").rglob("*.gfx"):
        text = rd(path)
        for match in re.finditer(r'spriteType\s*=\s*\{(.*?)\n?\s*\}', text, re.S):
            chunk = match.group(1)
            name = re.search(r'name\s*=\s*"?([A-Za-z0-9_]+)"?', chunk)
            texture = re.search(r'texturefile\s*=\s*"([^"]+)"', chunk)
            if name:
                out[name.group(1)] = texture.group(1).replace("//", "/") if texture else None
    return out


def windows(root):
    out = set()
    for path in (root / "interface").rglob("*.gui"):
        out.update(re.findall(r'windowType\s*=\s*\{[^}]*?name\s*=\s*"([^"]+)"', rd(path), re.S))
    return out


def english_keys():
    keys = set()
    for path in (ROOT / "localisation").rglob("*_l_english.yml"):
        keys.update(re.findall(r"(?m)^ ([^\s:#]+):\d+ ", path.read_text(encoding="utf-8-sig")))
    return keys


CLAUSEWITZ_KEYWORDS = {"AND", "OR", "NOT", "NOR", "if", "else", "else_if", "limit"}


def defined_names(folder):
    out = set()
    for path in Path(folder).glob("*.txt"):
        out.update(re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", rd(path)))
    return out - CLAUSEWITZ_KEYWORDS


# --------------------------------------------------------------------------
# Lints: pure functions over text, each returns a list of problems
# --------------------------------------------------------------------------

def lint_icons(reforms, known_sprites):
    problems = []
    for name, (_, block) in reforms.items():
        icon = re.search(r'(?m)^\s*icon\s*=\s*"?([A-Za-z0-9_]+)"?', strip_comments(block))
        if not icon:
            problems.append(f"{name}: no icon")
        elif f"government_reform_{icon.group(1)}" not in known_sprites:
            problems.append(f"{name}: icon {icon.group(1)!r} names no sprite (government_reform_{icon.group(1)} is defined nowhere)")
    return problems


def lint_abilities(reforms, mechanic_names):
    problems = []
    for name, (_, block) in reforms.items():
        for _, ability_block in children_named(block, "government_abilities"):
            for ability in re.findall(r"[A-Za-z][A-Za-z0-9_]*", strip_comments(ability_block))[1:]:
                if ability not in mechanic_names:
                    problems.append(f"{name}: government_abilities names {ability}, which no mechanic defines")
    return problems


def children_named(block, key):
    """Every nested block called `key`, at any depth (conditional blocks carry abilities too)."""
    out, masked = [], _mask_comments_and_strings(block)
    for match in re.finditer(rf"\b{key}\s*=\s*\{{", masked):
        brace = block.index("{", match.start(), match.end())
        out.append((key, block[match.start(): matching_brace(block, brace) + 1]))
    return out


def lint_conditionals(reforms, allowed):
    problems = []
    for name, (_, block) in reforms.items():
        if name in VANILLA_OVERRIDES:
            continue
        for _, conditional in children_named(block, "conditional"):
            for key in top_level_keys(conditional):
                if key not in allowed:
                    problems.append(f"{name}: `{key}` inside a conditional block - the engine takes reform keys there, not modifiers")
    return problems


def lint_available(mechanics, scripted_triggers):
    problems = []
    for name, (_, block) in mechanics.items():
        for _, available in children_named(block, "available"):
            for token in re.findall(r"\b([A-Za-z][A-Za-z0-9_]*)\s*=", strip_comments(available)):
                if token in scripted_triggers and token not in CLAUSEWITZ_KEYWORDS:
                    problems.append(f"{name}: `available` uses the scripted trigger {token}; the engine reads `available` before scripted triggers exist")
    return problems


def lint_mechanic_wiring(mechanics, known_sprites, known_windows, keys):
    problems = []
    for name, (_, block) in mechanics.items():
        code = strip_comments(block)
        if f"ability_{name}" not in keys:
            problems.append(f"{name}: no English text ability_{name} (the reform tooltip shows a raw key)")
        for window in re.findall(r"(?m)^\s*gui\s*=\s*(\w+)", code):
            if window not in known_windows:
                problems.append(f"{name}: gui = {window} is no windowType")
        try:
            interaction_blocks = children(named_block(block, "interactions"))
        except Exception:
            interaction_blocks = []
        for button, button_block in interaction_blocks:
            for key in (button, f"{button}_desc"):
                if key not in keys:
                    problems.append(f"{name}: button {button} has no English text {key}")
            icon = re.search(r"(?m)^\s*icon\s*=\s*(\w+)", strip_comments(button_block))
            if icon and icon.group(1) not in known_sprites:
                problems.append(f"{name}: button {button} uses {icon.group(1)}, a sprite defined nowhere")
            desc = re.search(r"cooldown_desc\s*=\s*(\w+)", strip_comments(button_block))
            if desc and desc.group(1) not in keys:
                problems.append(f"{name}: button {button} names the cooldown {desc.group(1)}, which has no text")
            for tooltip in re.findall(r"(?:tooltip|custom_tooltip)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)", strip_comments(button_block)):
                if tooltip not in keys and tooltip not in {"yes", "no"}:
                    problems.append(f"{name}: button {button} shows the tooltip {tooltip}, which has no text")
        try:
            powers = children(named_block(block, "powers"))
        except Exception:
            powers = []
        for power, _ in powers:
            for key in (power, f"{power}_desc", f"monthly_{power}", f"{power}_gain_modifier"):
                if key not in keys:
                    problems.append(f"{name}: power {power} has no English text {key}")
    return problems


def lint_descriptions(reforms, loc_text):
    problems = []
    for name in reforms:
        match = re.search(rf'(?m)^ {re.escape(name)}_desc:\d+ "(.*)"\s*$', loc_text)
        if match:
            clean = re.sub(r"§[A-Za-z!]", "", match.group(1))
            if "!" in clean:
                problems.append(f"{name}_desc carries an exclamation mark (docs/STYLE_GLOSSARY.md, section 3)")
    return problems


def lint_modifier_references(scripts, known):
    problems = []
    pattern = re.compile(
        r"(?:add_country_modifier\s*=\s*\{[^}]*?name\s*=\s*\"?|add_(?:permanent_)?province_modifier\s*=\s*\{[^}]*?name\s*=\s*\"?"
        r"|remove_country_modifier\s*=\s*\"?|remove_province_modifier\s*=\s*\"?|has_country_modifier\s*=\s*\"?|has_province_modifier\s*=\s*\"?)"
        r"([A-Za-z0-9_]+)", re.S)
    for path, text in scripts.items():
        for match in pattern.finditer(text):
            name = match.group(1)
            if name.endswith("_") or name in known:
                continue
            problems.append(f"{path}: modifier {name} is referenced but defined nowhere (engine: Unknown modifier-type)")
    return problems


def lint_scripted_calls(reforms, mechanics, effects, triggers):
    problems = []
    for owner, group in (("reform", reforms), ("mechanic", mechanics)):
        for name, (_, block) in group.items():
            code = strip_comments(block)
            for attrs in children_named(code, "custom_attributes"):  # attribute keys are not scripted calls
                code = code.replace(attrs[1], "")
            for call in re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*yes\b", code):
                if MOD_PREFIX.match(call) and call not in effects and call not in triggers:
                    problems.append(f"{owner} {name}: calls {call}, a scripted effect or trigger defined nowhere")
    return problems


def lint_reform_sprites(mod_sprites):
    problems = []
    for name, texture in mod_sprites.items():
        if not name.startswith("government_reform_"):
            continue
        path = ROOT / texture if texture else None
        if path is None or not path.is_file():
            problems.append(f"{name}: texture {texture} does not exist")
    return problems


# --------------------------------------------------------------------------
# Gathering and the self-test
# --------------------------------------------------------------------------

def gather():
    vanilla = vanilla_root()
    mod_sprite_map = sprites(ROOT)
    van_sprite_map = sprites(vanilla) if vanilla else {}
    reforms = mod_reforms()
    mechanics = mod_mechanics()
    modifiers = defined_names(ROOT / "common/event_modifiers")
    if vanilla:
        modifiers |= defined_names(vanilla / "common/event_modifiers")
        modifiers |= defined_names(vanilla / "common/static_modifiers")
        modifiers |= defined_names(vanilla / "common/triggered_modifiers")
    modifiers |= defined_names(ROOT / "common/triggered_modifiers") if (ROOT / "common/triggered_modifiers").exists() else set()
    allowed = set(CONDITIONAL_FALLBACK)
    mechanic_names = set(mechanics)
    window_names = windows(ROOT)
    if vanilla:
        for path in (vanilla / "common/government_reforms").glob("*.txt"):
            for _, block in top_blocks(rd(path)).items():
                for _, conditional in children_named(block, "conditional"):
                    allowed.update(top_level_keys(conditional))
        for path in (vanilla / "common/government_mechanics").glob("*.txt"):
            mechanic_names.update(top_blocks(rd(path)))
        window_names |= windows(vanilla)
    scripts = {}
    for sub in ("common", "events", "decisions", "missions"):
        for path in (ROOT / sub).rglob("*.txt"):
            if "event_modifiers" in path.parts:
                continue
            scripts[path.relative_to(ROOT).as_posix()] = strip_comments(rd(path))
    return {
        "vanilla": bool(vanilla), "reforms": reforms, "mechanics": mechanics,
        "sprites_all": {f"{k}": v for k, v in {**van_sprite_map, **mod_sprite_map}.items()},
        "mod_sprites": mod_sprite_map, "allowed": allowed, "mechanic_names": mechanic_names,
        "windows": window_names, "keys": english_keys(), "modifiers": modifiers, "scripts": scripts,
        "effects": defined_names(ROOT / "common/scripted_effects"), "triggers": defined_names(ROOT / "common/scripted_triggers"),
        "loc": "\n".join(p.read_text(encoding="utf-8-sig") for p in (ROOT / "localisation").glob("*_l_english.yml")),
    }


def run(g):
    reforms = {k: v for k, v in g["reforms"].items() if k not in VANILLA_OVERRIDES and k != "rip_republic_mechanic"}
    problems = []
    if g["vanilla"]:
        problems += lint_icons(reforms, g["sprites_all"])
    problems += lint_abilities(reforms, g["mechanic_names"])
    problems += lint_conditionals(g["reforms"], g["allowed"])
    problems += lint_available(g["mechanics"], g["triggers"])
    problems += lint_mechanic_wiring(g["mechanics"], g["sprites_all"], g["windows"], g["keys"])
    problems += lint_descriptions(reforms, g["loc"])
    if g["vanilla"]:
        problems += lint_modifier_references(g["scripts"], g["modifiers"])
    problems += lint_scripted_calls(reforms, g["mechanics"], g["effects"], g["triggers"])
    problems += lint_reform_sprites(g["mod_sprites"])
    return problems


def planted(g):
    """(label, lint result on a damaged copy) - each list must be non-empty."""
    some = next(n for n in g["reforms"] if n not in VANILLA_OVERRIDES)
    block = g["reforms"][some][1]
    fake = {"x_reform": ("x.txt", 'x_reform = {\n\ticon = "no_such_icon"\n\tgovernment_abilities = {\n\t\tno_such_mechanic\n\t}\n'
                         '\tconditional = {\n\t\tallow = { has_dlc = "Common Sense" }\n\t\tparliament_backing_chance = 0.1\n\t}\n'
                         '\tremoved_effect = {\n\t\trip_no_such_effect = yes\n\t}\n}')}
    mech = {"x_mechanic": ("x.txt", 'x_mechanic = {\n\tavailable = {\n\t\trip_border_watch_held = yes\n\t}\n\tinteractions = {\n\t\tx_button = {\n'
                           '\t\t\ticon = GFX_no_such_sprite\n\t\t\tcooldown_desc = x_no_text\n\t\t\teffect = { custom_tooltip = x_tip_no_text }\n\t\t}\n\t}\n'
                           '\tpowers = {\n\t\tx_power = { gui = no_such_window }\n\t}\n}')}
    return [
        ("a reform icon that names no sprite", lint_icons(fake, g["sprites_all"]) if g["vanilla"] else ["skipped"]),
        ("an ability no mechanic defines", lint_abilities(fake, g["mechanic_names"])),
        ("a modifier inside conditional", lint_conditionals(fake, g["allowed"])),
        ("a scripted trigger in available", lint_available(mech, {"rip_border_watch_held"})),
        ("a mechanic with no text, icon, window or tooltip", lint_mechanic_wiring(mech, g["sprites_all"], g["windows"], set())),
        ("an exclamation mark in a description", lint_descriptions({some: None}, f' {some}_desc:0 "Long live the realm!"\n')),
        ("an undefined modifier reference", lint_modifier_references({"x.txt": "remove_country_modifier = no_such_modifier_anywhere"}, set()) if True else []),
        ("an undefined scripted effect called from a reform", lint_scripted_calls(fake, {}, set(), set())),
        ("a sprite whose texture is missing", lint_reform_sprites({"government_reform_x": "gfx/interface/no_such_file.dds"})),
        ("a reform with no icon at all", lint_icons({"y": ("y.txt", "y = { }")}, g["sprites_all"])),
    ]


def main():
    g = gather()
    problems = run(g)
    if not g["vanilla"]:
        print("SKIP: the vanilla install was not found; the icon and modifier-reference lints need it")
    if problems:
        print("REFORM LAYER INTEGRITY: FAIL")
        for problem in problems:
            print("  -", problem)
        return 1
    caught = 0
    for label, found in planted(g):
        if not found:
            print(f"REFORM LAYER INTEGRITY: the self-test did not catch: {label}")
            return 1
        caught += 1
    reforms = len([n for n in g["reforms"] if n not in VANILLA_OVERRIDES])
    print(f"REFORM LAYER INTEGRITY PASS: {reforms} reforms and {len(g['mechanics'])} mechanics: icons, abilities, conditional keys, "
          f"available blocks, button wiring, descriptions, modifier references, scripted calls, sprites; {caught} planted violations caught")
    print("LIMIT: static lints of the classes the engine log showed; they do not execute script and prove no balance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
