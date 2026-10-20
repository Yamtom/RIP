"""A government mechanic's `available` block may not call a scripted trigger.

Measured in EU4 1.37.5 on 2026-10-19: the engine parses `available` before it loads common/scripted_triggers, so a scripted trigger there
logs "Unknown trigger type. Key: <name>" at load - and the mechanic cannot tell whether it is available. The button blocks (`potential`,
`trigger`) of the same mechanic are parsed later and may call scripted triggers (the crown ordinances and the Rada's court buttons do).

Two mechanics broke exactly this way in the first game run of the resolutions and the Rada (rip_institutional_resolutions.txt,
rip_ruthenian_factional_court.txt); no static check had caught it. The test reads every mechanic file of the mod, collects the names used
in each `available`, and compares them with the scripted triggers the mod (and the installed game) defines. planted_violations() proves it
sees a scripted trigger put back.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, matching_brace, vanilla_root, _mask_comments_and_strings  # noqa: E402

STRUCTURE = {'OR', 'AND', 'NOT', 'NOR', 'available', 'limit', 'custom_trigger_tooltip', 'tooltip', 'hidden_trigger'}


def scripted_trigger_names():
    names = set()
    folders = [ROOT / 'common/scripted_triggers']
    root = vanilla_root()
    if root is not None:
        folders.append(root / 'common/scripted_triggers')
    for folder in folders:
        for path in sorted(folder.glob('*.txt')):
            text = _mask_comments_and_strings(path.read_text(encoding='utf-8-sig', errors='replace'))
            names.update(re.findall(r'(?m)^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', text))
    return names


def available_blocks(text):
    masked = _mask_comments_and_strings(text)
    for match in re.finditer(r'(?m)^\s*available\s*=\s*\{', masked):
        opening = text.index('{', match.start(), match.end())
        yield text[opening + 1: matching_brace(text, opening)], text.count('\n', 0, match.start()) + 1


def violations(text, scripted):
    found = []
    for block, line in available_blocks(text):
        used = set(re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*=', _mask_comments_and_strings(block))) - STRUCTURE
        for name in sorted(used & scripted):
            found.append((name, line))
    return found


def main():
    scripted = scripted_trigger_names()
    files = sorted((ROOT / 'common/government_mechanics').glob('*.txt'))
    problems = []
    blocks = 0
    for path in files:
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        blocks += sum(1 for _ in available_blocks(text))
        for name, line in violations(text, scripted):
            problems.append(f'{path.name}:{line}: `available` calls the scripted trigger {name}; use the plain triggers it expands to')
    if blocks < 10:
        problems.append(f'only {blocks} available blocks found in {len(files)} mechanic files: the reader is broken')
    planted = {
        'a scripted trigger in a resolution mechanic': 'm = {\n\tavailable = {\n\t\trip_gov_has_municipal_review = yes\n\t}\n}\n',
        'a scripted trigger nested in an OR': 'm = {\n\tavailable = {\n\t\tOR = {\n\t\t\tkru_holds_rada_reform = yes\n\t\t}\n\t}\n}\n',
    }
    unseen = [name for name, text in planted.items() if not violations(text, scripted)]
    problems += [f'planted violation not caught: {name}' for name in unseen]
    clean = 'm = {\n\tavailable = {\n\t\tOR = {\n\t\t\thas_reform = vln_magdeburg_rights\n\t\t\ttag = KRU\n\t\t}\n\t}\n}\n'
    if violations(clean, scripted):
        problems.append('plain triggers in an available block are reported as scripted ones')
    if problems:
        print('MECHANIC AVAILABLE CHECK: FAIL')
        for problem in problems:
            print('  - ' + problem)
        return 1
    print(f'MECHANIC AVAILABLE CHECK: PASS ({blocks} available blocks in {len(files)} mechanic files call no scripted trigger; {len(planted)} planted violations caught)')
    print('LIMIT: static. The rule itself was measured in EU4 1.37.5 (see the docstring).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
