"""A scope iterator the engine does not have derails everything after it in the same file.

EU4 1.37.5 reads `any_allied_country = { ... }` as "Unknown trigger type", loses its place, and reports the blocks that follow
as "Unexpected token" at a line far from the typo. In decisions/GreekCatholicDecisions.txt a mistyped `any_ally` in one
`ai_will_do` made `greek_catholic_education_decision` unloadable and `patronize_greek_catholic_culture_decision` a corrupt table
entry, while the error log pointed at an unrelated, correct trigger (`rip_church_union_supporter`) 19 lines below.

The vocabulary is every any_/every_/random_ block the installed game's own script uses, plus the snapshot below taken from
1.37.5 (so the check still guards when no game is installed), plus any such name the mod defines as a scripted trigger or effect.
A genuinely valid iterator that vanilla never uses has to be added to EXTRA with a note.
"""
import re
from pathlib import Path

from clausewitz_testlib import ROOT, _mask_comments_and_strings, vanilla_root

ITERATOR = re.compile(r'\b((?:any|every|random)_[a-z0-9_]+)\s*=\s*\{')

SNAPSHOT_1_37_5 = frozenset((
    'any_active_trade_node', 'any_ally', 'any_army', 'any_core_country', 'any_core_province', 'any_country',
    'any_country_active_in_node', 'any_empty_neighbor_province', 'any_enemy_country', 'any_estate_loyalty',
    'any_federation_members', 'any_friendly_coast_border_province', 'any_great_power', 'any_heretic_province',
    'any_hired_mercenary_company', 'any_known_country', 'any_neighbor_country', 'any_neighbor_province',
    'any_other_great_power', 'any_owned_province', 'any_privateering_country', 'any_province',
    'any_province_in_state', 'any_rival_country', 'any_subject_country', 'any_trade_node',
    'any_trade_node_member_country', 'any_trade_node_member_province', 'any_tribal_land', 'any_war_enemy_country',
    'every_active_trade_node', 'every_ally', 'every_claimed_province', 'every_core_country', 'every_core_province',
    'every_country', 'every_country_including_inactive', 'every_elector', 'every_empty_neighbor_province',
    'every_enemy_country', 'every_federation_member', 'every_heretic_province', 'every_known_country',
    'every_neighbor_country', 'every_neighbor_province', 'every_owned_province', 'every_province',
    'every_province_in_state', 'every_rival_country', 'every_subject_country', 'every_trade_node_member_country',
    'every_trade_node_member_province', 'every_tribal_land_province', 'every_trunk_road_province_effect',
    'every_trunk_road_province_trigger', 'every_war_enemy_country', 'random_active_trade_node', 'random_ally',
    'random_area_province', 'random_core_country', 'random_core_province', 'random_country', 'random_elector',
    'random_empty_neighbor_province', 'random_enemy_country', 'random_events', 'random_heretic_province',
    'random_hired_mercenary_company', 'random_known_country', 'random_list', 'random_neighbor_country',
    'random_neighbor_province', 'random_new_world_region', 'random_owned_area', 'random_owned_province',
    'random_privateering_country', 'random_province', 'random_province_in_state', 'random_rival_country',
    'random_subject_country', 'random_trade_node', 'random_trade_node_member_province', 'random_war_enemy_country',
))
EXTRA = frozenset()

SCANNED = ('common', 'events', 'decisions', 'missions', 'history')


def iterators_in(text):
    masked = _mask_comments_and_strings(text)
    return [(match[1], masked.count('\n', 0, match.start()) + 1) for match in ITERATOR.finditer(masked)]


def unknown_iterators(text, vocabulary):
    return [(name, line) for name, line in iterators_in(text) if name not in vocabulary]


def read_latin1(path):
    return path.read_bytes().decode('latin-1')


assert unknown_iterators('modifier = { any_allied_country = { religion = catholic } }', SNAPSHOT_1_37_5) == [('any_allied_country', 1)]
assert not unknown_iterators('modifier = { any_ally = { religion = catholic } }', SNAPSHOT_1_37_5)
assert not unknown_iterators('# any_allied_country = {\ntext = "every_nothing = {"', SNAPSHOT_1_37_5)
assert not unknown_iterators('random_list = { 10 = { } }', SNAPSHOT_1_37_5)

vocabulary = set(SNAPSHOT_1_37_5) | set(EXTRA)
game = vanilla_root()
if game:
    for directory in SCANNED:
        for path in Path(game, directory).rglob('*.txt'):
            vocabulary |= {name for name, _ in iterators_in(read_latin1(path))}
for directory in ('common/scripted_triggers', 'common/scripted_effects'):
    for path in (ROOT / directory).glob('*.txt'):
        vocabulary |= set(re.findall(r'(?m)^[ \t]*((?:any|every|random)_[a-z0-9_]+)\s*=\s*\{', _mask_comments_and_strings(read_latin1(path))))

failures = []
for directory in SCANNED:
    for path in sorted((ROOT / directory).rglob('*.txt')):
        for name, line in unknown_iterators(read_latin1(path), vocabulary):
            failures.append(f'{path.relative_to(ROOT)}:{line}: unknown scope iterator {name} (valid ones: any_ally, any_neighbor_country, ...)')
if failures:
    print('\n'.join(failures))
    raise SystemExit(1)
source = 'the installed game plus the 1.37.5 snapshot' if game else 'the 1.37.5 snapshot only (no installed game: set EU4_DIR)'
print(f'SCOPE ITERATORS PASS: {len(vocabulary)} known iterators from {source}; none unknown in {", ".join(SCANNED)}.')
