"""Execute HET authority's actual script subset; not an EU4 runtime claim."""
from copy import deepcopy
import subprocess, sys
from clausewitz_testlib import ROOT, read, named_block
from check_government_reviews import parse

FX = dict(parse(read('common/scripted_effects/rip_het_authority.txt')))
TR = dict(parse(read('common/scripted_triggers/rip_het_authority.txt')))

def state(position=500):
    return dict(vars={'rip_het_position': position}, flags={'rip_het_position_initialized'},
                reforms={'rip_hetman_cossacks_reform'}, mods={}, day=0, power=position/10,
                adm_power=100, dip_power=100, nobles=True, loyalty=50, target=True,
                tag='HET', government='republic', events=[])

def gate(nodes, s):
    results=[]
    for key,val in nodes:
        if key=='NOT': ok=not gate(val,s)
        elif key=='OR': ok=any(gate([x],s) for x in val)
        elif key in TR: ok=gate(TR[key],s)
        elif key=='check_variable':
            a=dict(val); ok=s['vars'].get(a['which'],0)>=float(a['value'])
        elif key=='has_reform': ok=val in s['reforms']
        elif key=='has_government_mechanic': ok='rip_hetman_cossacks_reform' in s['reforms']
        elif key=='has_country_modifier': ok=s['mods'].get(val,-1)>s['day']
        elif key=='has_country_flag': ok=val in s['flags']
        elif key=='has_estate': ok=s['nobles']
        elif key=='event_target:het_target_polk': ok=s['target']
        elif key in ('tag','government'): ok=s[key]==val
        elif key in ('adm_power','dip_power'): ok=s[key]>=float(val)
        else: raise AssertionError(('unmodelled condition',key))
        results.append(ok)
    return all(results)

def run(nodes,s):
    for key,val in nodes:
        if key=='if':
            if gate(dict(val)['limit'],s): run([(k,v) for k,v in val if k!='limit'],s)
        elif key in FX: run(FX[key],s)
        elif key in ('set_variable','change_variable','subtract_variable'):
            which=[v for k,v in val if k=='which']; args=dict(val)
            amount=s['vars'].get(which[1],0) if len(which)>1 else float(args['value'])
            name=which[0]
            s['vars'][name]=amount if key=='set_variable' else s['vars'].get(name,0)+amount*(-1 if key=='subtract_variable' else 1)
        elif key in ('set_government_power','add_government_power'):
            amount=float(dict(val)['value'])
            s['power']=amount if key.startswith('set_') else s['power']+amount
        elif key=='add_country_modifier':
            a=dict(val); s['mods'][a['name']]=s['day']+int(a['duration'])
        elif key=='remove_country_modifier': s['mods'].pop(val,None)
        elif key=='set_country_flag': s['flags'].add(val)
        elif key=='clr_country_flag': s['flags'].discard(val)
        elif key=='remove_government_reform': s['reforms'].discard(val)
        elif key=='add_government_reform': s['reforms'].add(val)
        elif key in ('add_adm_power','add_dip_power'): s[key[4:]]+=float(val)
        elif key=='add_estate_loyalty': s['loyalty']+=float(dict(val)['loyalty'])
        elif key=='country_event': s['events'].append(dict(val)['id'])
        else: raise AssertionError(('unmodelled effect',key))

def effect(name,s): run(FX[name],s)

for n in range(1001):
    s=state(n); effect('rip_het_sync_effect',s)
    assert abs(s['power']-n/10)<1e-8, (n,s)
    effect('rip_het_monthly_effect',s)
    assert s['vars']['rip_het_position']==n+(1 if n<500 else -1 if n>500 else 0)
    assert abs(s['power']-s['vars']['rip_het_position']/10)<1e-8
for n in (-50,1050):
    s=state(n); effect('rip_het_sync_effect',s)
    assert 0<=s['vars']['rip_het_position']<=1000
for fx,resource,delta in [('rights','dip_power',-150),('chancery','adm_power',150)]:
    s=state(); effect('rip_het_'+fx+'_effect',s)
    assert s[resource]==50 and s['vars']['rip_het_position']==500+delta
    frozen=deepcopy(s)
    effect('rip_het_rights_effect',s);effect('rip_het_chancery_effect',s)
    assert s==frozen, 'shared term bypass'
    s['day']=1825; effect('rip_het_'+fx+'_effect',s); assert s[resource]==0
    s=state();s[resource]=49;before=deepcopy(s);effect('rip_het_'+fx+'_effect',s);assert s==before
for fx in ('rights','centralization'):
    s=state();s['target']=False;before=deepcopy(s);effect('rip_het_polk_'+fx+'_effect',s);assert s==before
s=state();effect('rip_het_polk_rights_effect',s);assert s['vars']['rip_het_position']==450
effect('rip_het_polk_centralization_effect',s);assert s['vars']['rip_het_position']==450
s['day']=1095;effect('rip_het_polk_centralization_effect',s);assert s['vars']['rip_het_position']==500
for tag in ('HET','ZAZ'):
    s=state(700);s.update(tag=tag,reforms={'rip_cossacks_reform'})
    effect('rip_het_migrate_effect',s)
    assert ('rip_hetman_cossacks_reform' in s['reforms'])==(tag=='HET')
    assert s['vars']['rip_het_position']==700, 'migration reset saved position'
s=state(0);s['flags'].clear();effect('rip_het_migrate_effect',s);assert s['vars']['rip_het_position']==500
for n in (0,1000):
    s=state(n)
    for _ in range(59): effect('rip_het_monthly_effect',s)
    assert not s['events']
    effect('rip_het_monthly_effect',s);assert len(s['events'])==1
    for _ in range(60): effect('rip_het_monthly_effect',s)
    assert len(s['events'])==1
s=state(900);s['vars']['rip_het_extreme_months']=59;effect('rip_het_monthly_effect',s)
assert s['vars']['rip_het_extreme_months']==0
events=parse(read('events/RIP_HetmanAuthority.txt'))
event=events['country_event']
compromise=next(v for k,v in event if k=='option')
for n in range(1001):
    s=state(n);run([(k,v) for k,v in compromise if k not in ('name','ai_chance')],s)
    assert s['vars']['rip_het_position']==(min(500,n+200) if n<500 else max(500,n-200))
source=read('common/government_reforms/RIP_shared_cossack_government_reforms.txt')
assert 'cossacks_mechanic' in source and 'rip_het_authority_mechanic' not in source
assert 'rip_het_migrating' in named_block(source,'removed_effect')
assert 'rip_hetman_cossacks_reform' in read('common/governments/00_governments.txt')
assert read('events/HetmanateRegimentalGovernance.txt').count('rip_het_polk_rights_effect = yes')==4
subprocess.run([sys.executable,'-B','tools/build_hetman_authority.py','--check'],cwd=ROOT,check=True)
print('HET AUTHORITY PASS: 1001 projection/drift positions, 1001 compromises, payment, shared terms, target loss, migration and extreme-duration scenarios. Runtime unverified.')
