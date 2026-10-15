"""Execute policy/charter transactions and AI utility gates against source.
This is not a native EU4 test or an AI campaign simulation.
"""
from copy import deepcopy
from church_testlib import World, EFFECTS, TRIGGERS, parse
from clausewitz_testlib import read

class GovernanceWorld(World):
    def condition(self, key, value, scope, root, prev):
        if key == 'religion' and value == 'owner':
            return scope['religion'] == self.countries[scope['owner']]['religion']
        return super().condition(key, value, scope, root, prev)

w = GovernanceWorld(); c = w.country('MOS', 'russian_orthodox')
p = w.province(295, c, 'orthodox'); p['region'] = 'russia_region'
c.update(stability=1, adm_power=200, dip_power=200, num_of_loans=0)
old = p['religion']
w.run('rip_church_crown_appointments_effect', c)
assert c['adm_power'] == 125 and 'rip_church_crown_appointments' in c['modifiers']
w.run('rip_church_crown_appointments_effect', c)
assert c['adm_power'] == 125, 'duplicate click must not charge twice'
w.day = 3649
w.run('rip_church_restore_elections_effect', c)
assert 'rip_church_crown_appointments' in c['modifiers']
w.day = 3650
w.run('rip_church_restore_elections_effect', c)
assert 'rip_church_crown_appointments' not in c['modifiers'] and c['adm_power'] == 50
assert p['religion'] == old
c['modifiers']['rip_church_theological_censorship'] = float('inf')
w.run('rip_church_governance_upkeep_effect', c)
assert 'rip_church_coercion_resistance' in p['modifiers']
c['religion'] = 'catholic'
w.run('rip_church_governance_upkeep_effect', c)
assert 'rip_church_theological_censorship' not in c['modifiers']
assert 'rip_church_coercion_resistance' not in p['modifiers']

# Both negotiating paths have real costs, persist and do not repaint provinces.
for effect, modifier in [('rip_church_full_compact_effect','rip_church_episcopal_guarantees'),
                         ('rip_church_royal_compact_effect','rip_church_royal_concordat')]:
    w = GovernanceWorld(); c = w.country('RUT','greek_catholic')
    c.update(adm_power=200,dip_power=100,stability=1)
    p = w.province(280,c,'orthodox')
    w.run(effect,p)
    assert (c['adm_power'],c['dip_power'],p['religion']) == (125,50,'orthodox')
    assert modifier in p['modifiers']
    w.run(effect,p)
    assert c['adm_power'] == 125
    p['has_missionary'] = True
    w.run('rip_church_governance_upkeep_effect',c)
    assert 'rip_church_compact_broken' in p['flags'] and 'rip_church_broken_promises' in c['modifiers']
    assert modifier not in p['modifiers'] and p['religion'] == 'orthodox'
    before=deepcopy(c)
    w.run('rip_church_governance_upkeep_effect',c)
    assert c == before, 'breach must not charge prestige repeatedly'
    assert not w.gate(TRIGGERS['rip_church_can_pay_compact'],c)

# Insufficient funds never create a free charter.
w = GovernanceWorld(); c=w.country('RUT','greek_catholic'); c.update(adm_power=74,dip_power=50,stability=1)
p=w.province(280,c)
w.run('rip_church_full_compact_effect',p)
assert 'rip_church_compact' not in p['flags']

# Local Mission needs actual work, not merely a non-Orthodox population.
w=GovernanceWorld(); c=w.country('MOS','russian_orthodox'); p=w.province(295,c,'sunni')
assert not w.gate(TRIGGERS['rip_church_ai_local_mission_useful'],c)
p['has_missionary']=True
assert w.gate(TRIGGERS['rip_church_ai_local_mission_useful'],c)
p['religion']='orthodox'
assert not w.gate(TRIGGERS['rip_church_ai_local_mission_useful'],c)

# Network eligibility no longer needs Mission already active: no circular gate.
source=read('common/scripted_triggers/rip_church_nodes_generated.txt')
for name,body in parse(source):
    if name.startswith('rip_church_node_') and name.endswith('_potential'):
        assert ('has_country_flag','rip_church_icon_mission') not in body
        assert ('has_dlc','Cradle of Civilization') in body
assert 'rip_church_ro_potential_network' in TRIGGERS
# Exercise the actual AI dispatcher: idle wrong-faith land is insufficient;
# a live missionary is useful, and removing it shuts Mission down.
w=GovernanceWorld(); c=w.country('MOS','russian_orthodox'); p=w.province(295,c,'sunni')
c.update(ai=True,num_of_loans=0,is_in_important_war=False)
c['variables']['muscovy_fervor']=60
w.run('rip_church_ro_recount_effect',c)
w.run('rip_church_ai_effect',c)
assert 'rip_church_icon_mission' not in c['flags']
p['has_missionary']=True
w.run('rip_church_ai_effect',c)
assert 'rip_church_icon_mission' in c['flags']
p['has_missionary']=False
w.run('rip_church_ai_effect',c)
assert 'rip_church_icon_mission' not in c['flags']

# Breaking a promise changes another Christian state's opinion, even when
# the offender remains Catholic; expiration removes the penalty on refresh.
w=GovernanceWorld(); c=w.country('POL','catholic'); other=w.country('RUT','orthodox')
c['modifiers']['rip_church_broken_promises']=3650
w.run('rip_church_refresh_relations_effect',c)
assert (c['id'],'rip_church_opinion_broken_charter') in other['opinion_modifiers']
w.day=3651
w.run('rip_church_refresh_relations_effect',c)
assert (c['id'],'rip_church_opinion_broken_charter') not in other['opinion_modifiers']
print('PASS: governance cost/cooldown, confessional cleanup, both charter paths, breach idempotence, majority preservation, Mission usefulness and non-circular network gates.')
