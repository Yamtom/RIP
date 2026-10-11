"""Regression coverage for blank RO counters, exhausted Fervor, the variable rename and the network status."""
from church_testlib import fixture, parse
from clausewitz_testlib import read
import re

loc = dict(re.findall(r'^\s*([^#\s:]+):\d*\s+"(.*)"\s*$',
                     read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml'), re.M))
definitions = {dict(body)['name']: body for kind, body in
               parse(read('customizable_localization/rip_church_redesign.txt')) if kind == 'defined_text'}
cases = 0
# The window's own numbers are read through literal ladders (tests/check_ro_panel_readouts.py checks every
# rung against the real recount); here only the surrounding contracts of the author's regressions remain.
for key in ('rip_church_ro_fervor_value','rip_church_ro_nodes_value','rip_church_ro_policies_value'):
    assert '.GetValue' not in loc[key], 'a direct variable prints nothing before the first monthly refresh'
assert '[' not in loc['rip_church_icon_toggle_label'], 'native button captions must be literal'
for pa,bonus,capacity in ((0,0,1),(.29,0,1),(.3,1,2),(.64,1,2),(.65,2,3),(.89,2,3),(.9,3,4),(1,3,4)):
    w,c,p=fixture()
    c['patriarch_authority']=pa
    w.run('rip_church_ro_recount_effect',c)
    assert c['variables']['rip_church_fervor_income']==2+bonus
    assert c['variables']['rip_church_capacity']==capacity
    cases+=1
assert loc['rip_church_ro_authority_label'] == 'Patriarch Authority'
assert 'name = "rip_church_ro_authority_label" scripted = yes' in read('interface/countryreligionview.gui')

for fuel, remains in ((0,False),(1,True),(100,True)):
    w,c,p = fixture()
    c['patriarch_authority'] = 0
    c['variables']['muscovy_fervor'] = fuel
    c['flags']['rip_church_icon_war'] = w.day
    c['modifiers']['rip_church_icon_war'] = float('inf')
    w.run('rip_church_ro_monthly_effect',c)
    assert ('rip_church_icon_war' in c['flags']) == remains
    assert ('rip_church_icon_war' in c['modifiers']) == remains
    assert 0 <= c['variables']['muscovy_fervor'] <= 100
    cases += 1
w,c,p = fixture()
c['flags']['rip_church_v3_migrated'] = w.day
c['variables']['rip_church_fervor'] = 67
w.run('rip_church_v3_initialize_effect',c)
assert c['variables']['muscovy_fervor'] == 67
c['variables']['muscovy_fervor'] = 12
w.run('rip_church_v3_initialize_effect',c)
assert c['variables']['muscovy_fervor'] == 12, 'load must not refill the migrated resource'
cases += 1
w,c,p = fixture('orthodox')
c['religion'] = 'russian_orthodox'
c['patriarch_authority'] = 0.5
w.run('rip_church_v3_religion_change_effect',c)
assert c['variables']['rip_church_fervor_income'] == 3
assert c['variables']['rip_church_capacity'] == 2
assert c['variables']['rip_church_fervor_cost'] == 0
assert c['variables']['rip_church_fervor_net'] == 3
cases += 1
w,c,p = fixture()
c['flags']['rip_church_node_novgorod'] = w.day
w.run('rip_church_ro_recount_nodes_effect',c)
assert c['variables']['funded_nodes_count'] == 1
assert 'rip_ro_funded_trade_missions' in c['modifiers']
w.run('rip_church_ro_close_all_nodes_effect',c)
assert c['variables']['funded_nodes_count'] == 0
assert 'rip_ro_funded_trade_missions' not in c['modifiers']
cases += 1

print(f'PASS: {cases} readout, exhaustion, migration and network-status cases; native rendering unverified.')
