"""Minimal full-file vanilla overrides for EU4 1.37; --check never writes.

Keep the entire native files: on_actions are additive across distinct filenames.
Reject changed upstream patterns rather than silently generating an unpatched file.
"""
import argparse
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from clausewitz_testlib import ROOT, vanilla_root


def outputs(game):
    path = 'common/new_diplomatic_actions/00_diplomatic_actions.txt'
    text = (game / path).read_text(encoding='utf-8-sig')
    old = 'value = num_of_loans'
    assert text.count(old) == 2, 'Re-audit native loan exports after game update'
    # SIZE_OF_LOANS concerns the recipient, just like its FROM loan trigger.
    text = text.replace(old, 'value = trigger_value:num_of_loans\n\t\t\t\twho = FROM')
    # NOT with multiple children is NOR; split without changing its truth table.
    text, count = re.subn(
        r'NOT = \{\s*is_rival = FROM\s*is_enemy = FROM\s*\}',
        'NOT = { is_rival = FROM }\\n\\t\\t\\t\\tNOT = { is_enemy = FROM }', text)
    assert count == 1, 'Re-audit native rival/enemy check'
    yield path, text

    path = 'common/on_actions/00_on_actions.txt'
    text = (game / path).read_text(encoding='utf-8-sig')
    old = 'FROM = { economic_ideas = 3 }'
    assert text.count(old) == 1, 'Re-audit native trade-good hook after game update'
    # Trade-good setup may have no originating country; use the province owner.
    text = text.replace(old, 'owner = { economic_ideas = 3 }')
    # Preserve the clean separator at the relocated UZH hook.
    text = text.replace('\n\t\n\tFROM = { country_event = { id = flavor_cri.6 } }',
                        '\n\n\tFROM = { country_event = { id = flavor_cri.6 } }')
    # Native exploit hooks accidentally close the if before its effect.
    pattern = (
        r'(?P<i>[ \t]*)if = \{\s*limit = \{\s*'
        r'has_province_modifier = estate_burghers_hungarian_royal_city_modifier\s*'
        r'NOT = \{ development = 20 \}\s*\}\s*\}\s*'
        r'remove_province_modifier = estate_burghers_hungarian_royal_city_modifier')
    def city_gate(match):
        return (
            '\tif = {\n\t\tlimit = {\n'
            '\t\t\thas_province_modifier = estate_burghers_hungarian_royal_city_modifier\n'
            '\t\t\tNOT = { development = 20 }\n\t\t}\n'
            '\t\tremove_province_modifier = estate_burghers_hungarian_royal_city_modifier\n\t}')
    text, count = re.subn(pattern, city_gate, text)
    assert count == 3, 'Re-audit native development-exploitation hooks'
    # Preserve NOR semantics, including the nested owner/province scopes.
    pattern = (
        r'NOT = \{\s*owner = \{\s*'
        r'has_estate_privilege = estate_nobles_vegvar_system\s*\}\s*'
        r'has_fort_building_trigger = yes\s*'
        r'any_neighbor_province = \{\s*NOT = \{ owned_by = ROOT \}\s*\}\s*\}')
    replacement = (
        'NOT = { owner = { has_estate_privilege = estate_nobles_vegvar_system } }\n'
        '\t\t\tNOT = { has_fort_building_trigger = yes }\n'
        '\t\t\tNOT = { any_neighbor_province = { NOT = { owned_by = ROOT } } }')
    text, count = re.subn(pattern, lambda _: replacement, text)
    assert count == 2, 'Re-audit native Vegvar checks'
    yield path, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    game = vanilla_root()
    if game is None:
        parser.error('Installed EU4 1.37 source is required')
    changed = []
    for relative, text in outputs(game):
        target = ROOT / relative
        if not target.exists() or target.read_text(encoding='utf-8') != text:
            changed.append(relative)
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding='utf-8', newline='\n')
    print(('STALE' if args.check and changed else 'PASS') + ': runtime scope overrides; ' + str(len(changed)) + ' changed')
    return int(args.check and bool(changed))


if __name__ == '__main__':
    raise SystemExit(main())
