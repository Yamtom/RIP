"""Regression coverage for blank RO counters and exact-zero policy upkeep."""
from church_testlib import fixture, parse
from clausewitz_testlib import read
import re

loc = dict(re.findall(r'^\s*([^#\s:]+):\d*\s+"(.*)"\s*$',
                     read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml'), re.M))
definitions = {dict(body)['name']: body for kind, body in
               parse(read('customizable_localization/rip_church_redesign.txt')) if kind == 'defined_text'}
cases = 0
for suffix, variable, maximum in (
    ('Fervor','muscovy_fervor',100), ('Income','rip_church_fervor_income',5),
    ('Cost','rip_church_fervor_cost',18), ('Policies','rip_church_icons',4),
    ('Capacity','rip_church_capacity',4), ('Nodes','funded_nodes_count',2),
    ('PolicyCost','rip_church_fervor_policy_cost',14),
    ('NextPolicyCost','rip_church_fervor_next_policy_cost',6),
    ('Net','rip_church_fervor_net',5),
):
    values = (None, 0, 1, maximum, -1, -16) if suffix == 'Net' else (None, 0, 1, maximum)
    for value in values:
        w,c,p = fixture()
        c['variables'].pop(variable,None)
        if value is not None: c['variables'][variable] = value
        rows = [dict(row) for kind,row in definitions['GetChurchRO'+suffix] if kind == 'text']
        leaf = next(row['localisation_key'] for row in rows if w.gate(row['trigger'],c))
        expected = ('+' if suffix == 'Net' and value and value > 0 else '') + str(value or 0)
        assert loc[leaf] == expected, (suffix,value,loc[leaf],expected)
        cases += 1
for key in ('fuel','slots','network'):
    assert '.GetValue' not in loc['rip_church_ro_'+key]
assert '[Root.GetChurchRONet]' in loc['rip_church_ro_authority_link_tt']
for key in ('fuel','slots','network'):
    assert not any(fragment in loc['rip_church_ro_'+key] for fragment in ('+0','-0','drain','Monthly:','net '))
for policy in ('war','mercy','building','mission'):
    assert '[' not in loc[f'rip_church_icon_{policy}_label'], 'native button captions must be literal'
for pa,bonus,capacity in ((0,0,1),(.29,0,1),(.3,1,2),(.64,1,2),(.65,2,3),(.89,2,3),(.9,3,4),(1,3,4)):
    w,c,p=fixture()
    c['patriarch_authority']=pa
    w.run('rip_church_ro_recount_effect',c)
    assert c['variables']['rip_church_fervor_income']==2+bonus
    assert c['variables']['rip_church_capacity']==capacity
    rows=[dict(row) for kind,row in definitions['GetChurchROAuthorityBonus'] if kind=='text']
    leaf=next(row['localisation_key'] for row in rows if w.gate(row['trigger'],c))
    assert loc[leaf]==('0' if not bonus else f'§G+{bonus}§!')
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
assert c['variables']['rip_church_fervor_policy_cost'] == 0
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

# Policy upkeep is displayed separately from the funded-node charge, and the
# next button quotes only the additional upkeep implied by the next tier.
for count, expected_policy_cost, expected_next in ((0,0,2),(1,2,2),(2,4,4),(3,8,6),(4,14,0)):
    w,c,p = fixture()
    for flag in ('war','mercy','building','mission'):
        c['flags'].pop('rip_church_icon_'+flag,None)
        c['modifiers'].pop('rip_church_icon_'+flag,None)
    for flag in ('war','mercy','building','mission')[:count]:
        c['flags']['rip_church_icon_'+flag] = w.day
        c['modifiers']['rip_church_icon_'+flag] = float('inf')
    c['variables']['funded_nodes_count'] = 1
    w.run('rip_church_ro_recount_effect',c)
    assert c['variables']['rip_church_fervor_policy_cost'] == expected_policy_cost
    assert c['variables']['rip_church_fervor_next_policy_cost'] == expected_next
    assert c['variables']['rip_church_fervor_cost'] == expected_policy_cost + 2
    cases += 1
print(f'PASS: {cases} readout, exhaustion, migration and network-status cases; native rendering unverified.')
