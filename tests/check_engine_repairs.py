"""Focused source/model regressions; not an EU4 runtime emulator."""
import itertools
import re
from clausewitz_testlib import read, named_block, ROOT

def parse(text):
    tokens = re.findall(r'"[^"\n]*"|[^\s={}]+|[={} ]', re.sub(r'#[^\n]*', '', text))
    tokens = [t for t in tokens if t.strip()]
    it = iter(tokens)
    def block():
        result = []
        for key in it:
            if key == '}': return result
            assert next(it) == '=', key
            value = next(it)
            result.append((key, block() if value == '{' else value.strip('"')))
        return result
    return block()

def condition(nodes, state):
    for key, value in nodes:
        if key == 'NOT': ok = not condition(value, state)
        elif key in ('check_variable', 'is_variable_equal'):
            args = dict(value); actual = state.get(args['which'], 0); wanted = float(args['value'])
            ok = actual >= wanted if key == 'check_variable' else actual == wanted
        elif key == 'has_country_flag': ok = value in state['flags']
        elif key == 'is_at_war': ok = state[key] == value
        else: ok = state[key] >= float(value)
        if not ok: return False
    return True

def execute(nodes, state):
    for key, value in nodes:
        if key == 'if':
            limits = [v for k,v in value if k == 'limit']
            if not limits or condition(limits[0], state):
                execute([(k,v) for k,v in value if k != 'limit'], state)
        elif key in ('set_variable','change_variable'):
            args=dict(value); amount=float(args['value']); var=args['which']
            state[var] = amount if key == 'set_variable' else state.get(var,0)+amount
        elif key == 'set_country_flag': state['flags'].add(value)
        elif key == 'country_event': state.setdefault('events', []).append(dict(value)['id'])
        else: raise AssertionError(('Unexpected modeled effect', key))

pulse = dict(parse(named_block(read('events/RuthenianDecadence.txt'), 'immediate')))['immediate']
# Model actual initialization, yearly arithmetic and both clamps, before modifiers/events.
cut = next(i for i,(k,v) in enumerate(pulse) if k == 'if' and any(x == 'remove_country_modifier' for x,_ in v))
pulse = pulse[:cut]
bad = dict(flags=set(), stability=-1, is_at_war='yes', num_of_loans=5, average_autonomy=40, legitimacy=0, prestige=0)
thresholds={}
for year in range(1,101):
    execute(pulse,bad)
    assert 0 <= bad['ruthenian_decadence'] <= 100
    for threshold in (40,70,90):
        if bad['ruthenian_decadence'] >= threshold: thresholds.setdefault(threshold,year)
assert thresholds == {40:3,70:8,90:10}, thresholds
peace=dict(flags={'rip_decadence_initialized'}, ruthenian_decadence=100, stability=2, is_at_war='no',num_of_loans=0,average_autonomy=0,legitimacy=100,prestige=0)
for _ in range(100): execute(pulse,peace)
assert peace['ruthenian_decadence'] == 0
legacy=dict(peace, flags=set(), ruthenian_decadence=80)
execute(pulse,legacy)
assert legacy['ruthenian_decadence'] == 75

def check_branches(nodes, unsafe=False):
    for key,value in nodes:
        if key in ('country_event','add_opinion','reverse_add_opinion'): assert not unsafe, key
        if isinstance(value,list): check_branches(value, unsafe or key in ('else_if','else'))
for file,name in [('kru_effects','kru_confederation_recognised_effect'),('het_effects','het_pereiaslav_treaty_effect'),('zaz_crossroads_effects','zaz_crossroads_check_thresholds_effect'),('pdl_government_effects','pdl_migrate_legacy_galician_union_effect')]:
    check_branches(parse(named_block(read('common/scripted_effects/'+file+'.txt'),name)))
zaz=read('common/scripted_effects/zaz_crossroads_effects.txt')
# Each later path must re-check the flag set by an earlier winning branch.
for lean in ('host_state','sacred_order','sacred_horde'):
    assert re.search(r'NOT = \{ has_country_flag = zaz_crossroads_resolved \} check_variable = \{ which = zaz_lean_'+lean, zaz)
paths=('cantons','host_state','sacred_order','sacred_horde')
branches=dict(parse(named_block(zaz,'zaz_crossroads_check_thresholds_effect')))['zaz_crossroads_check_thresholds_effect']
for active in itertools.product((False, True), repeat=4):
    state={'flags':set()}
    state.update({f'zaz_lean_{path}':100 if enabled else 99 for path,enabled in zip(paths,active)})
    execute(branches,state)
    expected=[f'zaz_crossroads.{60+active.index(True)}'] if any(active) else []
    assert state.get('events',[]) == expected
    execute(branches,state)
    assert state.get('events',[]) == expected, 'Resolution fired twice'
mechanic=read('common/government_mechanics/rip_kyivan_cesarstvo.txt')
gui=read('interface/rip_ruthenian_powers.gui'); gfx=read('interface/rip_ruthenian_government.gfx')
for name in re.findall(r'gui = (\w+)',mechanic): assert f'name = "{name}"' in gui
for sprite in re.findall(r'spriteType = "(GFX_rip_\w+)"',gui): assert f'name = "{sprite}"' in gfx
for f in ('RIP_kru_factions','RIP_representation_monarchy_factions'):
    assert 'nobles_influence_modifier' not in read('common/factions/'+f+'.txt')
estates=read('common/estates/02_nobility.txt')
for faction,amount in [('kru_boyary',10),('rep_boyary',5)]:
    assert f'trigger = {{ faction_in_power = {faction} }}\n\t\tinfluence = {amount}' in estates
assert 'ai_will_do' not in read('common/estate_agendas/RIP_magnate_agendas.txt')
assert 'on_completed_agenda_effect_estate_nobles = yes' in named_block(read('common/scripted_effects/rip_estate_effects.txt'),'on_completed_agenda_effect_estate_magnates')
assert not re.search(r'\badd_estate_influence\s*=',read('events/FreeElection.txt'))
assert 'ZAZ_evolve_to_hetmanate = {' not in read('decisions/ZaporizhiaDecisions.txt')
assert 'tag = ZAZ' in named_block(read('decisions/HetmanateNation.txt'),'hetmanate_nation')
print(f'ENGINE REPAIRS PASS: 100-year adverse/recovery models; thresholds {thresholds}; legacy value; branch safety, GUI, estates, decisions.')
