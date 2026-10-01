"""Source-state contracts for parish readouts and Union entry/navigation.

Does not emulate EU4 rendering or native centre target selection.
"""
from copy import deepcopy
from church_testlib import fixture, TRIGGERS, EFFECTS, parse
from clausewitz_testlib import read

cases = 0
decision = dict(dict(parse(read('decisions/GreekCatholicDecisions.txt')))['country_decisions'])
adoption = dict(decision['convert_to_greek_catholic_decision'])
assert TRIGGERS['rip_church_gui_can_adopt_union'] == adoption['potential'] + adoption['allow']
transaction = EFFECTS['rip_church_gui_adopt_union_effect']
assert len(transaction) == 1 and transaction[0][0] == 'if'
assert transaction[0][1] == [('limit', [('rip_church_gui_can_adopt_union', 'yes')])] + adoption['effect']
cases += 1

# Counts follow owned recognized parishes and current faith.
w, c, p = fixture('greek_catholic')
foreign = w.country('FRA', 'catholic')
for number, owner, faith, flags in [
    (301,c,'orthodox',['rip_church_rite_recognized']),
    (302,c,'russian_orthodox',['rip_church_rite_recognized']),
    (303,c,'catholic',['rip_church_rite_recognized']),
    (304,c,'catholic',[]),
    (305,c,'protestant',['rip_church_rite_recognized']),
    (306,foreign,'orthodox',['rip_church_rite_recognized']),
]:
    parish = w.province(number,owner,faith)
    parish['flags'].update({flag:w.day for flag in flags})
before = deepcopy(w.provinces)
resources = {key:c[key] for key in ('adm_power','dip_power','treasury','religion')}
w.run('rip_church_gui_refresh_parishes_effect',c)
names = ['rip_church_gui_'+suffix for suffix in ('eastern_parishes','latin_parishes')]
assert [c['variables'][name] for name in names] == [2,1]
assert before == w.provinces
assert resources == {key:c[key] for key in resources}
snapshot = deepcopy(c)
w.run('rip_church_gui_refresh_parishes_effect',c)
assert c == snapshot
w.provinces['301']['owner'] = foreign['id']
w.provinces['304']['religion'] = 'greek_catholic'
w.run('rip_church_gui_refresh_parishes_effect',c)
assert [c['variables'][name] for name in names] == [1,1]
cases += 3

windows = {dict(body)['name']:dict(body)['potential']
           for key,body in parse(read('common/custom_gui/RIP_church_controls.txt'))
           if key == 'custom_window' and dict(body)['name'] in {
               'rip_church_gc_panel','rip_church_gc_curia_panel',
               'rip_church_gc_parishes_panel'}}
assert 'rip_church_union_paths_panel' not in read('interface/countryreligionview.gui')
assert 'rip_church_union_paths_panel' not in read('common/custom_gui/RIP_church_controls.txt')
def visible(w,c):
    return {name for name,gate in windows.items() if w.gate(gate,c)}

for faith,sponsor,initial in [
    ('greek_catholic',False,'rip_church_gc_panel'),
    ('orthodox',False,None),
    ('catholic',False,None),
    ('catholic',True,None),
    ('russian_orthodox',False,None),
]:
    w,c,p = fixture(faith)
    if sponsor: c['flags']['rip_church_supports_union'] = w.day
    assert visible(w,c) == ({initial} if initial else set())
    resources = {key:c[key] for key in ('adm_power','dip_power','treasury','religion')}
    w.run('rip_church_gui_open_parishes_effect',c)
    allowed = faith == 'greek_catholic' or sponsor
    assert visible(w,c) == ({'rip_church_gc_parishes_panel'} if allowed else ({initial} if initial else set()))
    assert resources == {key:c[key] for key in resources}
    w.run('rip_church_gc_open_curia_effect',c)
    if faith == 'greek_catholic':
        assert visible(w,c) == {'rip_church_gc_curia_panel'}
        w.run('rip_church_gui_open_parishes_effect',c)
        assert visible(w,c) == {'rip_church_gc_parishes_panel'}
    w.run('rip_church_gc_open_union_effect',c)
    assert visible(w,c) == ({initial} if initial else set())
    assert resources == {key:c[key] for key in resources}
    cases += 1

# A stale GUI click cannot convert a Catholic patron or another non-Orthodox state.
for faith in ('catholic','greek_catholic','russian_orthodox','protestant'):
    w,c,p = fixture(faith)
    before = deepcopy(c)
    w.run('rip_church_gui_adopt_union_effect',c)
    assert c == before
    cases += 1

print(f'PASS: {cases} Union GUI source contracts; native rendering unverified')
