"""Keep UZH settlement rewards aligned with identity and monument eligibility."""
import re

from clausewitz_testlib import ROOT, keyed_blocks, matching_brace, named_block, normalized, read


def atom(text, key):
    return re.search(r'\b' + key + r'\s*=\s*([\w.-]+)', text)[1]


def event(text, eid):
    return next(block for _, block in keyed_blocks(text, 'country_event')
                if re.search(r'\bid\s*=\s*' + re.escape(eid) + r'\b', block)
                and re.search(r'\btitle\s*=', block))


def top_level_clauses(block):
    body_start = block.find('{') + 1
    body_end = matching_brace(block, body_start - 1)
    clauses = []
    pos = body_start
    while pos < body_end:
        match = re.search(r'\b(if|else_if|else)\s*=\s*\{', block[pos:body_end])
        if not match:
            break
        key = match.group(1)
        open_idx = pos + match.end() - 1
        close_idx = matching_brace(block, open_idx)
        clauses.append((key, block[pos + match.start():close_idx + 1]))
        pos = close_idx + 1
    return clauses


effects = read('common/scripted_effects/uzh_effects.txt')
events = read('events/RIP_UZH_Uzh.txt')
# The repository keeps this vanilla-derived file in legacy single-byte encoding.
# Only ASCII identifiers and braces are inspected here.
cultures = (ROOT / 'common/cultures/00_cultures.txt').read_text(encoding='latin-1')
monument = named_block(read('common/great_projects/RIP_UZH_great_projects.txt'), 'palanok_fortress')
setter = named_block(effects, 'uzh_set_identity_culture')
top = top_level_clauses(setter)
branches = [(k, b) for k, b in top if k in ('if', 'else_if')]
fallbacks = [b for k, b in top if k == 'else']
options = [block for _, block in keyed_blocks(event(events, 'uzh_identity.1'), 'option')]
assert [k for k, _ in branches] == ['if', 'else_if', 'else_if'] and len(fallbacks) == 1
assert len(options) == 3

expected_slavic = {'ruthenian': 'ruthenian_new', 'rusyn': 'rusyn_new'}
for (_, branch), option in zip(branches, options):
    flag = atom(branch, 'has_country_flag')
    target = atom(option, 'change_primary_culture')
    assert flag == atom(option, 'set_country_flag')
    group = 'carpathian' if target == 'rusyn_new_new' else 'east_slavic'
    assert named_block(named_block(cultures, group), target)
    for gate in ('build_trigger', 'can_use_modifiers_trigger'):
        block = named_block(monument, gate)
        assert target in re.findall(r'\bculture\s*=\s*(\w+)', block), (gate, target)
        assert 'province_is_or_accepts_culture = yes' in block

    inner = top_level_clauses(branch)
    if target in expected_slavic:
        assert [k for k, _ in inner] == ['if', 'else'], (flag, inner)
        assert 'culture_group = slavic' in normalized(inner[0][1])
        assert atom(inner[0][1], 'change_culture') == expected_slavic[target]
        assert atom(inner[1][1], 'change_culture') == target
    else:
        assert not inner and atom(branch, 'change_culture') == target

fallback_inner = top_level_clauses(fallbacks[0])
assert [k for k, _ in fallback_inner] == ['if', 'else']
assert 'culture_group = slavic' in normalized(fallback_inner[0][1])
assert atom(fallback_inner[0][1], 'change_culture') == 'rusyn_new'
assert atom(fallback_inner[1][1], 'change_culture') == 'rusyn'

for slavic_culture in ('ruthenian_new', 'rusyn_new'):
    assert named_block(named_block(cultures, 'slavic'), slavic_culture)
    for gate in ('build_trigger', 'can_use_modifiers_trigger'):
        assert slavic_culture in re.findall(r'\bculture\s*=\s*(\w+)', named_block(monument, gate)), (gate, slavic_culture)

assert 'province_is_or_accepts_culture = yes' in named_block(monument, 'can_upgrade_trigger')

missions = read('missions/Zakarpatta_Missions.txt')
assert 'uzh_set_identity_culture = yes' in named_block(missions, 'uzh_banat_colonization')
wave = event(events, 'uzh.310')
for _, option in keyed_blocks(wave, 'option'):
    assert 'uzh_set_identity_culture = yes' in option
decision = named_block(read('decisions/UzhEparchyPath.txt'), 'uzh_launch_colonization_wave')
assert 'id = uzh.310' in decision

reward = named_block(read('common/event_modifiers/RIP_UZH_modifiers.txt'), 'danubian_monarchy_influence')
assert float(atom(reward, 'reduced_liberty_desire')) == 10
mission = named_block(missions, 'uz_danubian_monarchy')
grants = [block for _, block in keyed_blocks(mission, 'add_country_modifier')
          if 'danubian_monarchy_influence' in block]
assert len(grants) == 1 and atom(grants[0], 'duration') == '-1'
print('PASS: three UZH identity cultures match settlement rewards and Palanok gates; permanent LD reward reduces desire by 10')
