"""Source-state checks for trade-policy requirements, not EU4 rendering evidence."""
import re
import struct
from church_testlib import World, TRIGGERS, parse
from clausewitz_testlib import ROOT, read

policy_source = read('common/trading_policies/RIP_church_mission_network.txt')
policy = dict(dict(parse(policy_source))['rip_church_mission_network'])
assert policy['can_select'] == policy['can_maintain']
assert policy['button_gfx'] == 'GFX_rip_ro_mission_policy'


def references(items):
    for key, value in items:
        if key.startswith('rip_church_'):
            yield key
        if isinstance(value, list):
            yield from references(value)


assert not list(references(policy['can_select'])), 'early-loaded policies must contain native gates only'
requirements = {dict(body)['tooltip']: body for key, body in policy['can_select']
                if key == 'custom_trigger_tooltip'}
expected = {'rip_church_policy_' + suffix + '_tt'
            for suffix in ('mission', 'dlc', 'funded', 'merchant', 'share', 'parish', 'target')}
assert set(requirements) == expected
for language in ('english', 'french', 'german', 'spanish'):
    loc = read('localisation/replace/zzzz_RIP_church_redesign_l_' + language + '.yml')
    for name in expected:
        assert len(re.findall(r'(?m)^\s*' + name + r':0 ', loc)) == 1, (language, name)


def fixture():
    w = World()
    c = w.country('MOS', 'russian_orthodox')
    c['flags'].update(rip_church_icon_mission=0, rip_church_node_novgorod=0)
    c['dlcs'].add('Cradle of Civilization')
    p = w.province(295, c, 'russian_orthodox')
    p['flags']['rip_church_ro_connected@MOS'] = 0
    other = w.country('KAZ', 'sunni')
    anchor = w.province(33, other, 'russian_orthodox')
    anchor['traders'].add('MOS')
    anchor['shares']['MOS'] = 50
    target = w.province(34, other, 'sunni')
    target['neighbors'].add('295')
    w.from_scope = anchor
    return w, c, p, anchor, target, other


def marker_results(w, c):
    return {name: w.gate(body, c) for name, body in requirements.items()}


w, c, *_ = fixture()
assert all(marker_results(w, c).values())
assert w.gate(policy['can_select'], c)
assert w.gate(TRIGGERS['rip_church_ro_can_maintain_policy'], c)
cases = 1

# Each ordinary missing requirement produces its own failed marker, preserving
# the country ROOT / node-anchor FROM scope used by native trading policies.
for suffix in ('mission', 'dlc', 'funded', 'merchant', 'share', 'parish', 'target'):
    w, c, p, anchor, target, other = fixture()
    if suffix == 'mission': c['flags'].pop('rip_church_icon_mission')
    elif suffix == 'dlc': c['dlcs'].discard('Cradle of Civilization')
    elif suffix == 'funded': c['flags'].pop('rip_church_node_novgorod')
    elif suffix == 'merchant': anchor['traders'].clear()
    elif suffix == 'share': anchor['shares']['MOS'] = 49.99
    elif suffix == 'parish': p['buildings'].clear()
    elif suffix == 'target': target['has_missionary'] = True
    failed = {name for name, result in marker_results(w, c).items() if not result}
    assert failed == {'rip_church_policy_' + suffix + '_tt'}, (suffix, failed)
    assert not w.gate(policy['can_select'], c)
    assert not w.gate(TRIGGERS['rip_church_ro_can_maintain_policy'], c)
    cases += 1

# Funding a different node cannot satisfy the clicked node's registration.
w, c, p, anchor, target, other = fixture()
c['flags'].pop('rip_church_node_novgorod')
c['flags']['rip_church_node_astrakhan'] = 0
assert not marker_results(w, c)['rip_church_policy_funded_tt']
cases += 1

# Target restrictions must survive tooltip grouping and native expansion.
for protection in ('rite', 'centre', 'zeal', 'independent_orthodox', 'unsettled'):
    w, c, p, anchor, target, other = fixture()
    if protection == 'rite': target['flags']['rip_church_rite_recognized'] = 0
    elif protection == 'centre': target['modifiers']['religious_center'] = float('inf')
    elif protection == 'zeal': target['modifiers']['religious_zeal_at_conv'] = float('inf')
    elif protection == 'independent_orthodox': target['religion'] = other['religion'] = 'orthodox'
    elif protection == 'unsettled': target['is_city'] = False
    assert not marker_results(w, c)['rip_church_policy_target_tt'], protection
    if protection == 'independent_orthodox':
        c['flags']['rip_church_ro_schismatic'] = 0
        assert marker_results(w, c)['rip_church_policy_target_tt']
    cases += 1

w, c, p, anchor, target, other = fixture()
target['id'] = '118'
assert not marker_results(w, c)['rip_church_policy_target_tt'], 'Rome remains excluded'
cases += 1

# Frame dimensions are part of the native trade-button callback contract.
dds = (ROOT / 'gfx/interface/rip_ro_mission_policy.dds').read_bytes()
assert dds[:4] == b'DDS '
assert struct.unpack_from('<II', dds, 12) == (56, 112)
gfx = read('interface/RIP_church_mission.gfx')
assert 'noOfFrames = 2' in gfx
native = dict(dict(parse(read('common/trading_policies/00_trading_policies.txt')))['propagate_religion'])
assert native['button_gfx'] == 'GFX_Trading_Policy_Propagate_Religion'
print(f'PASS: {cases} RO trade-policy source cases; seven requirement markers; isolated 112x56 sprite. Runtime unverified.')
