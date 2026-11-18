"""Keep UZH settlement rewards aligned with identity and monument eligibility."""
import re

from clausewitz_testlib import ROOT, keyed_blocks, named_block, read


def atom(text, key):
    return re.search(r'\b' + key + r'\s*=\s*([\w.-]+)', text)[1]


def event(text, eid):
    return next(block for _, block in keyed_blocks(text, 'country_event')
                if re.search(r'\bid\s*=\s*' + re.escape(eid) + r'\b', block)
                and re.search(r'\btitle\s*=', block))


effects = read('common/scripted_effects/uzh_effects.txt')
events = read('events/RIP_UZH_Uzh.txt')
# The repository keeps this vanilla-derived file in legacy single-byte encoding.
# Only ASCII identifiers and braces are inspected here.
cultures = (ROOT / 'common/cultures/00_cultures.txt').read_text(encoding='latin-1')
monument = named_block(read('common/great_projects/RIP_UZH_great_projects.txt'), 'palanok_fortress')
setter = named_block(effects, 'uzh_set_identity_culture')
branches = [block for key in ('if', 'else_if') for _, block in keyed_blocks(setter, key)]
options = [block for _, block in keyed_blocks(event(events, 'uzh_identity.1'), 'option')]
assert len(branches) == len(options) == 3
for branch, option in zip(branches, options):
    flag = atom(branch, 'has_country_flag')
    target = atom(branch, 'change_culture')
    assert flag == atom(option, 'set_country_flag')
    assert target == atom(option, 'change_primary_culture'), (flag, target)
    group = 'carpathian' if target == 'rusyn_new_new' else 'east_slavic'
    assert named_block(named_block(cultures, group), target)
    for gate in ('build_trigger', 'can_use_modifiers_trigger'):
        block = named_block(monument, gate)
        assert target in re.findall(r'\bculture\s*=\s*(\w+)', block), (gate, target)
        assert 'province_is_or_accepts_culture = yes' in block
assert atom(named_block(setter, 'else'), 'change_culture') == 'rusyn'
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
