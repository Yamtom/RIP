"""The Brest proposal's Orthodox refusal has a direct political consequence."""
import re

from clausewitz_testlib import keyed_blocks, named_block, normalized, read


events = read('events/UniateChurch.txt')
proposal = next(
    block for _, block in keyed_blocks(events, 'country_event')
    if re.search(r'(?m)^\s*id\s*=\s*uniate_church\.1\s*$', block)
)
refusal = next(
    block for _, block in keyed_blocks(proposal, 'option')
    if 'name = uniate_church.1.b' in block
)
assert 'set_country_flag = uniate_union_rejected' in refusal
assert 'add_country_modifier = { name = orthodox_revival_movement duration = 5475 }' in normalized(refusal)
assert 'add_prestige = 10' in refusal

modifier = named_block(
    read('common/event_modifiers/uniate_church_modifiers.txt'),
    'orthodox_revival_movement',
)
assert 'diplomatic_reputation = -1' in modifier

localisation = read('localisation/uniate_and_raid_l_english.yml')
assert "weakens our diplomatic standing for fifteen years" in localisation
assert 'orthodox_revival_movement:0 "Orthodox Revival Movement"' in localisation
assert "diplomatic standing by 1 for 15 years" in localisation

# The historic Brest narrative is carried by the three event blocks below.
# Keep this contract tied to keys actually referenced by the events, not merely
# to plausible-looking strings in the large shared localisation file.
brest_events = [
    block for _, block in keyed_blocks(events, 'country_event')
    if re.search(r'(?m)^\s*id\s*=\s*uniate_church\.[123]\s*$', block)
]
brest_keys = set(re.findall(
    r'\b(?:title|desc|name)\s*=\s*(uniate_church\.[123]\.[a-z])',
    '\n'.join(brest_events),
))
localised_brest_keys = set(re.findall(
    r'(?m)^\s*(uniate_church\.[123]\.[a-z]):0',
    localisation,
))
assert brest_keys == localised_brest_keys, (brest_keys, localised_brest_keys)
proposal_text = next(
    line for line in localisation.splitlines()
    if line.startswith(' uniate_church.1.d:')
)
council_text = next(
    line for line in localisation.splitlines()
    if line.startswith(' uniate_church.2.d:')
)
resistance_text = next(
    line for line in localisation.splitlines()
    if line.startswith(' uniate_church.3.d:')
)
for detail in ('1595', '1596', 'Michael Rahoza', 'Hypatius Potii',
               'Cyril Terlecki', 'Gedeon Balaban', 'Michael Kopystensky',
               'Clement VIII'):
    assert detail in proposal_text or detail in council_text, detail
assert 'separate assemblies' in council_text
assert 'Byzantine rite' in council_text
assert 'No province changes faith by this act alone' in council_text
assert 'local and uneven' in resistance_text
print('PASS: Brest refusal cost, active localization keys, episcopal positions, 1595–96 sequence, council split and bounded reach')
