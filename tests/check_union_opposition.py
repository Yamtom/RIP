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
assert 'pursuing_uniate_union' not in refusal
proposal_acceptance = next(
    block for _, block in keyed_blocks(proposal, 'option')
    if 'name = uniate_church.1.a' in block
)
assert 'set_country_flag = pursuing_uniate_union' in proposal_acceptance

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

# The separate opposition choice is the autonomous brotherhoods outcome in
# event .3, not the earlier .1.b refusal (whose existing cost is diplomatic).
resolution = next(
    block for _, block in keyed_blocks(events, 'country_event')
    if re.search(r'(?m)^\s*id\s*=\s*uniate_church\.3\s*$', block)
)
assert 'has_country_flag = pursuing_uniate_union' in resolution
options = {
    re.search(r'name\s*=\s*(uniate_church\.3\.[abc])', block)[1]: block
    for _, block in keyed_blocks(resolution, 'option')
    if re.search(r'name\s*=\s*(uniate_church\.3\.[abc])', block)
}
assert 'set_country_flag = orthodox_brotherhoods_suppressed' in options['uniate_church.3.a']
assert 'set_country_flag = orthodox_brotherhoods_resisted' in options['uniate_church.3.b']
opposition = options['uniate_church.3.c']
assert 'set_country_flag = orthodox_brotherhoods_autonomous' in opposition
assert 'add_country_modifier = { name = orthodox_brotherhood_resistance duration = 7300 }' in normalized(opposition)
assert all(
    'orthodox_brotherhood_jurisdiction' not in options[key]
    for key in ('uniate_church.3.a', 'uniate_church.3.b')
)
target = named_block(opposition, 'random_owned_province')
assert 'religion = orthodox' in named_block(target, 'limit')
assert 'development = 12' in named_block(target, 'limit')
assert 'name = orthodox_brotherhood_jurisdiction duration = 3650' in normalized(target)
assert opposition.count('add_province_modifier') == 1
assert 'every_owned_province' not in opposition
assert 'spawn_rebels' not in opposition
assert 'orthodox_brotherhood_jurisdiction' not in refusal
jurisdiction = named_block(
    read('common/event_modifiers/uniate_church_modifiers.txt'),
    'orthodox_brotherhood_jurisdiction',
)
assert normalized(jurisdiction) == (
    'orthodox_brotherhood_jurisdiction = { local_unrest = 1 local_autonomy = 0.05 }'
)
assert 'orthodox_brotherhood_jurisdiction:0 "Brotherhood Jurisdiction Dispute"' in localisation
assert 'desc_orthodox_brotherhood_jurisdiction:0' in localisation
assert 'for ten years; no rebel army is raised.' in localisation
assert 'uniate_church.3.a:0 "Suppress the brotherhoods"' in localisation
assert 'uniate_church.3.b:0 "Negotiate coexistence"' in localisation
assert 'uniate_church.3.c:0 "Grant brotherhoods local autonomy"' in localisation
for language in ('french', 'german', 'spanish'):
    fallback = read(f'localisation/replace/zzz_RIP_untranslated_l_{language}.yml')
    assert 'uniate_church.3.a:0 "Suppress the brotherhoods"' in fallback
    assert 'uniate_church.3.b:0 "Negotiate coexistence"' in fallback
    assert 'uniate_church.3.c:0 "Grant brotherhoods local autonomy"' in fallback
    assert 'orthodox_brotherhood_jurisdiction:0 "Brotherhood Jurisdiction Dispute"' in fallback
    assert 'desc_orthodox_brotherhood_jurisdiction:0' in fallback
historical_docs = read('docs/CHURCH_REDESIGN_20260911.uk.md')
assert 'одна придатна' in historical_docs
assert 'на 10 років +1 місцевого' in historical_docs
assert 'не спавнить повстанців' in historical_docs
print('PASS: Brest refusal retains its 15-year diplomatic cost; the brotherhood-autonomy choice adds a 10-year local cost to one qualifying Orthodox province and raises no rebels')
