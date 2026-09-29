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

print('PASS: Brest refusal preserves Orthodox revival and imposes a localised 15-year diplomatic cost')
