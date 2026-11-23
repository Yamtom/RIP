"""A two-button RIP government mechanic is drawn centred in the mechanic box, not hanging to its left.

The Government view lays every mechanic out as its own row of 100-wide interaction windows from the left edge of the mechanic box; three
buttons fill the 300-wide row, two leave the right third empty (the Host of Zaporozhia: three vanilla Cossack buttons above, the two
Register resolutions to their lower left, which the author called "pretty and crooked"). The mod gives the FIRST button of every two-button
mechanic its own window, `rip_government_interaction_pair_left` (interface/RIP_shared_government_interactions.gui), which puts the pair at
the half-column offsets: on the axis of the full row above.

The geometry was measured in EU4 1.37.5 (1600x900, UI scale 1.0, probe mechanics on the Host reform): the engine centres the button in its
window and `position.x` is an offset from that centre, so a button's left edge is  x + (window width - 82) / 2  from the row's left edge.
The default window (100 wide, x = 8) gives 17, 117, 217; the pair must sit at 67 and 167. The test holds:
  1. every RIP mechanic with exactly two interactions names the pair window on the first and nothing (no `gui`, no `center`) on the second,
     and no other mechanic names it;
  2. the window exists, is 150x100, keeps the three elements the engine looks up by name, and its button x solves the equation above;
  3. when the target game is installed, the default window still is 100x100 with the button at x = 8 (the equation's other premise);
  4. every `gui =` a RIP mechanic names is a window the mod or the game defines (a typo would draw the default window silently).
planted_violations() proves each rule fires.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, matching_brace, vanilla_read, vanilla_root, _mask_comments_and_strings  # noqa: E402

PAIR_WINDOW = 'rip_government_interaction_pair_left'
BUTTON_BOX = 82            # the engine's button box; measured, not the 72-74 px of visible art
DEFAULT_WIDTH = 100
DEFAULT_X = 8
PAIR_WIDTH = 150
INTERFACE_FILE = 'interface/RIP_shared_government_interactions.gui'
NATIVE_NAMES = ('government_interaction_button', 'government_power_bar', 'government_power_bar_frame')


def left_edge(x, width):
    """Left edge of a centred button from the left edge of its window."""
    return x + (width - BUTTON_BOX) / 2


def depth_zero(body):
    """The text of a block body with every nested block cut out, so a `gui` inside `effect = { }` is not mistaken for the interaction's own."""
    masked = _mask_comments_and_strings(body)
    out, depth = [], 0
    for index, char in enumerate(masked):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
        elif depth == 0:
            out.append(char)
    return ''.join(out)


def interactions_of(text):
    """{mechanic: [(interaction, depth-zero text)]} for one mechanic file."""
    masked = _mask_comments_and_strings(text)
    result = {}
    for top in re.finditer(r'(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', masked):
        opening = text.index('{', top.start(), top.end())
        mechanic = text[opening + 1: matching_brace(text, opening)]
        inner = _mask_comments_and_strings(mechanic)
        block = re.search(r'(?m)^\s*interactions\s*=\s*\{', inner)
        if not block:
            continue
        start = mechanic.index('{', block.start(), block.end())
        body = mechanic[start + 1: matching_brace(mechanic, start)]
        found, depth, masked_body = [], 0, _mask_comments_and_strings(body)
        index = 0
        while index < len(masked_body):
            piece = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{').match(masked_body, index)
            if piece and depth == 0:
                opening2 = body.index('{', piece.start(), piece.end())
                closing2 = matching_brace(body, opening2)
                found.append((piece.group(1), depth_zero(body[opening2 + 1: closing2])))
                index = closing2 + 1
            else:
                index += 1
        result[top.group(1)] = found
    return result


def mechanic_problems(text, label):
    found = []
    for mechanic, items in interactions_of(text).items():
        guis = [re.search(r'\bgui\s*=\s*"?([A-Za-z0-9_]+)"?', body) for _, body in items]
        names = [match.group(1) if match else None for match in guis]
        if len(items) == 2:
            if names[0] != PAIR_WINDOW:
                found.append(f'{label}: {mechanic} has two buttons but its first ({items[0][0]}) does not use gui = {PAIR_WINDOW}')
            if names[1] is not None or re.search(r'\bcenter\s*=', items[1][1]):
                found.append(f'{label}: {mechanic} second button ({items[1][0]}) must keep the default window and the default centring')
        else:
            for (interaction, _), name in zip(items, names):
                if name == PAIR_WINDOW:
                    found.append(f'{label}: {interaction} of {mechanic} ({len(items)} buttons) uses the pair window, made for a row of two')
    return found


def window_block(text, name):
    masked = _mask_comments_and_strings(text)
    for match in re.finditer(r'windowType\s*=\s*\{\s*name\s*=\s*"' + re.escape(name) + '"', text):
        if masked[match.start()] != ' ':
            opening = text.index('{', match.start())
            return text[opening + 1: matching_brace(text, opening)]
    return None


def named_position(block, name):
    match = re.search(r'name\s*=\s*"' + re.escape(name) + r'"[^{}]*?position\s*=\s*\{\s*x\s*=\s*(-?\d+)\s+y\s*=\s*(-?\d+)', block, re.S)
    return (int(match.group(1)), int(match.group(2))) if match else None


def window_problems(text, label):
    block = window_block(text, PAIR_WINDOW)
    if block is None:
        return [f'{label}: window {PAIR_WINDOW} is not defined']
    found = []
    size = re.search(r'size\s*=\s*\{\s*x\s*=\s*(\d+)\s+y\s*=\s*(\d+)', block)
    width = int(size.group(1)) if size else None
    if (width, int(size.group(2)) if size else None) != (PAIR_WIDTH, 100):
        found.append(f'{label}: {PAIR_WINDOW} must be {PAIR_WIDTH}x100 (a pair is 150 + 100 = 250 wide in a 300 row), found {size.group(0) if size else "no size"}')
    for name in NATIVE_NAMES:
        if named_position(block, name) is None:
            found.append(f'{label}: {PAIR_WINDOW} lacks the element the engine looks up by name: {name} (or its position)')
    button = named_position(block, 'government_interaction_button')
    if button and width:
        first = left_edge(button[0], width)
        second = width + left_edge(DEFAULT_X, DEFAULT_WIDTH)      # the second window of the pair is the default one
        target = left_edge(DEFAULT_X, DEFAULT_WIDTH) + DEFAULT_WIDTH / 2
        if second - first != DEFAULT_WIDTH:
            found.append(f'{label}: the pair is {second - first} px apart, the three-button row is {DEFAULT_WIDTH}')
        if abs(first - target) > 0.5:
            found.append(f'{label}: first button of the pair sits at {first}, the axis of the three-button row needs {target} (x = {button[0]})')
        bar, frame = named_position(block, 'government_power_bar'), named_position(block, 'government_power_bar_frame')
        if bar and frame and (bar[0] - button[0], frame[0] - button[0]) != (12, -2):
            found.append(f'{label}: bar and frame must keep the vanilla offsets +12 and -2 from the button (found {bar[0] - button[0]}, {frame[0] - button[0]})')
    if re.search(r'\bcenter\s*=', block):
        found.append(f'{label}: a window has no `center`; that is an interaction property')
    return found


def default_window_problems():
    text = vanilla_read('interface/countrygovernmentview.gui')
    if text is None:
        return None
    block = window_block(text, 'government_interaction_type')
    if block is None:
        return ['the installed game no longer defines government_interaction_type']
    size = re.search(r'size\s*=\s*\{\s*x\s*=\s*(\d+)\s+y\s*=\s*(\d+)', block)
    button = named_position(block, 'government_interaction_button')
    if (int(size.group(1)), int(size.group(2))) != (DEFAULT_WIDTH, 100) or button != (DEFAULT_X, 4):
        return [f'the default interaction window changed (size {size.group(0)}, button {button}); the pair geometry rests on 100x100 and x = 8 and must be measured again']
    return []


def defined_windows():
    names = set()
    folders = [ROOT / 'interface']
    root = vanilla_root()
    if root is not None:
        folders.append(root / 'interface')
    for folder in folders:
        for path in folder.rglob('*.gui'):
            names.update(re.findall(r'windowType\s*=\s*\{\s*name\s*=\s*"([^"]+)"', path.read_text(encoding='utf-8-sig', errors='replace')))
    return names, root is not None


def planted_violations():
    wide = f'windowType = {{\n\tname = "{PAIR_WINDOW}"\n\tsize = {{ x = 150 y = 100 }}\n\tguiButtonType = {{\n\t\tname = "government_interaction_button"\n\t\tposition = {{ x = 33 y = 4 }}\n\t}}\n\ticonType = {{\n\t\tname = "government_power_bar"\n\t\tposition = {{ x = 45 y = 78 }}\n\t}}\n\ticonType = {{\n\t\tname = "government_power_bar_frame"\n\t\tposition = {{ x = 31 y = 74 }}\n\t}}\n}}\n'
    mechanic = 'm = {\n\tinteractions = {\n\t\ta = {\n\t\t\tgui = %s\n\t\t\ticon = x\n\t\t\teffect = {\n\t\t\t\tgui = nested\n\t\t\t}\n\t\t}\n\t\tb = {\n\t\t\ticon = y\n\t\t}\n\t}\n}\n' % PAIR_WINDOW
    cases = {
        'a two-button mechanic with the default window': (mechanic_problems, mechanic.replace('gui = %s' % PAIR_WINDOW, 'icon = z')),
        'a second button with its own window': (mechanic_problems, mechanic.replace('icon = y', 'gui = other')),
        'a second button with center = no': (mechanic_problems, mechanic.replace('icon = y', 'center = no')),
        'the pair window on a three-button mechanic': (mechanic_problems, mechanic.replace('\t\tb = {\n\t\t\ticon = y\n\t\t}\n', '\t\tb = {\n\t\t\ticon = y\n\t\t}\n\t\tc = {\n\t\t\ticon = w\n\t\t}\n')),
        'a window whose button is at the default x': (window_problems, wide.replace('x = 33 y = 4', 'x = 8 y = 4')),
        'a window of the wrong width': (window_problems, wide.replace('x = 150', 'x = 120')),
        'a window without the power bar': (window_problems, wide.replace('government_power_bar"', 'power_bar"', 1)),
    }
    clean_mechanic = mechanic_problems(mechanic.replace('\t\t\teffect = {\n\t\t\t\tgui = nested\n\t\t\t}\n', ''), 'clean')
    clean_window = window_problems(wide, 'clean')
    missed = [name for name, (check, text) in cases.items() if not check(text, 'planted')]
    return missed, clean_mechanic + clean_window, len(cases)


def main():
    problems = []
    mechanics = 0
    pairs = 0
    for path in sorted((ROOT / 'common/government_mechanics').glob('*.txt')):
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        for items in interactions_of(text).values():
            mechanics += 1
            pairs += len(items) == 2
        problems += mechanic_problems(text, path.name)
    if mechanics < 10 or pairs < 4:
        problems.append(f'the reader found {mechanics} mechanics and {pairs} two-button ones in common/government_mechanics: it is broken')
    interface = ROOT / INTERFACE_FILE
    if not interface.is_file():
        problems.append(f'{INTERFACE_FILE} is missing')
    else:
        problems += window_problems(interface.read_text(encoding='utf-8-sig'), INTERFACE_FILE)
    default = default_window_problems()
    if default:
        problems += default
    names, have_vanilla = defined_windows()
    named = set()
    for path in sorted((ROOT / 'common/government_mechanics').glob('*.txt')):
        named.update((name, path.name) for name in re.findall(r'(?m)^\s*gui\s*=\s*"?([A-Za-z0-9_]+)"?', _mask_comments_and_strings(path.read_text(encoding='utf-8-sig', errors='replace'))))
    for name, file in sorted(named):
        if name not in names:
            problems.append(f'{file}: gui = {name} is not a window the mod' + (' or the game' if have_vanilla else '') + ' defines')
    missed, false_alarms, planted = planted_violations()
    problems += [f'planted violation not caught: {name}' for name in missed]
    problems += [f'a correct sample is reported: {problem}' for problem in false_alarms]
    if problems:
        print('GOVERNMENT INTERACTION LAYOUT CHECK: FAIL')
        for problem in problems:
            print('  - ' + problem)
        return 1
    print(f'GOVERNMENT INTERACTION LAYOUT CHECK: PASS ({pairs} two-button mechanics of {mechanics} use {PAIR_WINDOW}; window geometry solved; '
          f'{len(named)} gui references resolve; {planted} planted violations caught)')
    print('LIMIT: static. The geometry (button box 82, offset from the centre) was measured in EU4 1.37.5; the picture itself was checked in the game, '
          + ('and the default window was compared with the installed game.' if default is not None else 'but the installed game was not available to compare the default window.'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
