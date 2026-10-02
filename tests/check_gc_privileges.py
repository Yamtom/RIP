"""Contracts for the Greek Catholic church-estate privileges."""
import re

from clausewitz_testlib import ROOT, named_block, normalized, read

FILE = 'common/estate_privileges/RIP_greek_catholic_privileges.txt'
text = read(FILE)
keys = re.findall(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', text)
assert len(keys) == len(set(keys)) == 8, keys

# Only modifiers that exist in the engine, so a typo cannot silently drop a bonus.
ALLOWED = {
    'tolerance_heretic', 'improve_relation_modifier', 'stability_cost_modifier',
    'global_unrest', 'global_missionary_strength', 'culture_conversion_cost',
    'diplomatic_reputation', 'idea_cost', 'advisor_cost', 'global_tax_modifier',
}
GROUPS = {
    'catholic': ('rip_privilege_eastern_rite_eparchies', 'rip_privilege_latin_rite_primacy'),
    'orthodox': ('rip_privilege_brotherhood_charters', 'rip_privilege_parish_concord'),
    'greek_catholic': ('rip_privilege_roman_concordat', 'rip_privilege_eastern_ecumene',
                       'rip_privilege_synodal_courts'),
}
EXCLUSIVE = {
    'rip_privilege_eastern_rite_eparchies': 'rip_privilege_latin_rite_primacy',
    'rip_privilege_latin_rite_primacy': 'rip_privilege_eastern_rite_eparchies',
    'rip_privilege_brotherhood_charters': 'rip_privilege_parish_concord',
    'rip_privilege_parish_concord': 'rip_privilege_brotherhood_charters',
    'rip_privilege_roman_concordat': 'rip_privilege_eastern_ecumene',
    'rip_privilege_eastern_ecumene': 'rip_privilege_roman_concordat',
}
for key in keys:
    block = named_block(text, key)
    for gate in ('is_valid', 'can_select'):
        assert named_block(block, gate), (key, gate)
    for section in ('benefits', 'penalties'):
        used = set(re.findall(r'\b([a-z_]+)\s*=\s*-?\d', normalized(named_block(block, section))))
        assert used and used <= ALLOWED, (key, section, used - ALLOWED)
    # A privilege must be gained and kept only while its trigger holds.
    valid_atoms = re.findall(r'[a-z_]+ = [A-Za-z0-9_]+', normalized(named_block(block, 'is_valid')))
    select = normalized(named_block(block, 'can_select'))
    assert valid_atoms and all(atom in select for atom in valid_atoms), key
    if key in EXCLUSIVE:
        other = f'has_estate_privilege = {EXCLUSIVE[key]}'
        for gate in ('is_valid', 'can_select'):
            assert other in normalized(named_block(block, gate)), (key, gate)
for faith, group in GROUPS.items():
    for key in group:
        block = normalized(named_block(text, key))
        assert f'religion = {faith}' in block or (faith == 'orthodox' and 'religion = orthodox' in block), key
        if faith != 'greek_catholic':
            assert 'rip_gc_owns_greek_catholic_province = yes' in block, key
assert 'rip_gc_owns_orthodox_province = yes' in normalized(named_block(text, 'rip_privilege_eastern_ecumene'))
# Dated roots: Lviv stauropegion (1586), Basilian reform (1617).
assert 'is_year = 1586' in normalized(named_block(text, 'rip_privilege_brotherhood_charters'))
assert 'is_year = 1617' in normalized(named_block(text, 'rip_privilege_basilian_schools'))
assert 'exists = PAP' in normalized(named_block(text, 'rip_privilege_roman_concordat'))

triggers = read('common/scripted_triggers/rip_gc_privilege_triggers.txt')
for name in ('rip_gc_owns_greek_catholic_province', 'rip_gc_owns_orthodox_province'):
    assert re.search(rf'(?m)^{name}\s*=\s*\{{', triggers), name

estate = read('common/estates/01_church.txt')
for key in keys:
    assert len(re.findall(rf'(?m)^\s*{key}\s*$', estate)) == 1, key

for language in ('english', 'french', 'german', 'spanish'):
    path = ('localisation/rip_gc_privileges_l_english.yml' if language == 'english'
            else f'localisation/replace/zzz_rip_gc_privileges_l_{language}.yml')
    loc = read(path)
    for key in keys:
        assert f' {key}:0 "' in loc and f' {key}_desc:0 "' in loc, (language, key)
    for bad in 'ś', 'ć', '−', '!':
        assert bad not in loc, (language, bad)
# State-wide adoption is alternative history (no crown ever did it): the AI must
# take it rarely. The player is not restricted.
decision = named_block(read('decisions/GreekCatholicDecisions.txt'), 'convert_to_greek_catholic_decision')
assert re.search(r'ai_will_do\s*=\s*\{\s*factor\s*=\s*0\.02\b', normalized(named_block(decision, 'ai_will_do'))), 'AI adoption weight'
proposal = read('events/UniateChurch.txt')
accept = re.search(r'name = uniate_church\.1\.a\s*ai_chance = \{ factor = (\d+) \}', proposal)
reject = re.search(r'name = uniate_church\.1\.b\s*ai_chance = \{ factor = (\d+) \}', proposal)
assert accept and reject and int(accept[1]) * 5 <= int(reject[1]), 'AI union proposal must lean to refusal'
print('GC PRIVILEGES PASS: 8 estate privileges, exclusive pairs, gates and localisation')
