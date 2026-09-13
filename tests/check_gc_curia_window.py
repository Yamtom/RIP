"""Execute curial source transactions. Does not emulate native GUI or elections."""
from copy import deepcopy
from church_testlib import fixture, TRIGGERS, EFFECTS, parse
from clausewitz_testlib import read, keyed_blocks

keys = ('church_tax','blessing','indulgence','saint','usury','holy_war','legate','monopoly')
def ready():
    w,c,p=fixture('greek_catholic')
    c['variables'].update(rip_church_communion=60,rip_church_papal_standing=100)
    c['is_at_war']=True
    return w,c
def gate(w,c,key): return w.gate(TRIGGERS['rip_church_gc_can_'+key],c)
def run(w,c,key): w.run('rip_church_gc_'+key+'_effect',c)
cases=0
for key in keys:
    w,c=ready(); action='petition_'+key
    assert gate(w,c,action)
    run(w,c,action)
    assert c['treasury']==900 and c['variables']['rip_church_papal_standing']==(40 if key=='saint' else 70)
    assert w.gate(TRIGGERS['rip_church_gc_has_privilege'],c)
    saved=deepcopy(c)
    for second in keys: run(w,c,'petition_'+second)
    assert c==saved
    c['is_at_war']=False; c['variables']['rip_church_communion']=0
    assert not gate(w,c,'eastern_privilege')
    w.day=3650
    assert gate(w,c,'eastern_privilege')
    cases+=1
    for invalid in ('money','standing','opinion','war','faith','pope_faith','pope_missing','slot','east'):
        w,c=ready()
        if invalid=='money': c['treasury']=99
        if invalid=='standing': c['variables']['rip_church_papal_standing']=29
        if invalid=='opinion': w.countries['PAP']['opinions']['MOS']=49
        if invalid=='war': c['wars'].add('PAP')
        if invalid=='faith': c['religion']='orthodox'
        if invalid=='pope_faith': w.countries['PAP']['religion']='protestant'
        if invalid=='pope_missing': del w.countries['PAP']
        if invalid=='slot': c['modifiers']['rip_church_gc_infrastructure']=3650
        if invalid=='east': c['variables']['rip_church_communion']=-60
        assert not gate(w,c,action),(key,invalid)
        before=deepcopy(c); run(w,c,action); assert c==before
        cases+=1
for key,field,value in [('saint','stability',3),('monopoly','mercantilism',100),('holy_war','is_at_war',False)]:
    w,c=ready(); c[field]=value
    assert not gate(w,c,'petition_'+key)
    before=deepcopy(c); run(w,c,'petition_'+key); assert c==before; cases+=1
for emperor in (False,True):
    w,c=ready(); c['variables']['rip_church_papal_standing']=90
    if emperor: c['dlcs'].add('Emperor')
    pope=w.countries['PAP']; pope['opinions']['MOS']=30
    assert gate(w,c,'donate'); run(w,c,'donate')
    assert c['treasury']==900 and c['variables']['rip_church_papal_standing']==100
    assert pope['treasury']==(1050 if emperor else 1100) and w.curia_treasury==(50 if emperor else 0)
    assert c['variables']['rip_church_papal_opinion']==55
    assert w.opinion(c,pope)==0
    c['variables']['rip_church_papal_standing']=0
    before=deepcopy(c); run(w,c,'donate'); assert c==before
    w.day=1824; assert not gate(w,c,'donate')
    w.day=1825; assert gate(w,c,'donate') and w.opinion(pope,c)==30
    cases+=1
for invalid in ('money','standing','faith','pope_missing','pope_faith','war'):
    w,c=ready(); c['variables']['rip_church_papal_standing']=0
    if invalid=='money': c['treasury']=99
    if invalid=='standing': c['variables']['rip_church_papal_standing']=90.001
    if invalid=='faith': c['religion']='catholic'
    if invalid=='pope_missing': del w.countries['PAP']
    if invalid=='pope_faith': w.countries['PAP']['religion']='orthodox'
    if invalid=='war': c['wars'].add('PAP')
    before=deepcopy(c); run(w,c,'donate'); assert c==before; cases+=1
w,c=ready(); f=w.country('FRA','catholic'); f['is_papal_controller']=True
run(w,c,'open_curia'); assert w.targets['rip_church_gc_controller'] is f
assert w.targets['rip_church_gc_rome'] is w.countries['PAP']
assert c['variables']['rip_church_papal_opinion']==100
other=w.country('POL','greek_catholic'); w.countries['PAP']['opinions']['POL']=-40
run(w,other,'open_curia'); assert other['variables']['rip_church_papal_opinion']==-40
assert c['variables']['rip_church_papal_opinion']==100
f['is_papal_controller']=False; run(w,c,'refresh_rome')
assert 'rip_church_gc_controller' not in w.targets
assert 'rip_church_gc_controller_known' not in w.flags
run(w,c,'open_union'); assert 'rip_church_gc_curia_view' not in c['flags']
before=deepcopy(c); run(w,c,'open_synod'); assert c==before and w.events[-1]==('MOS','rip_church.6')
c['flags']['rip_church_gc_donated']=0
run(w,c,'clear_privilege')
assert 'rip_church_gc_donated' in c['flags']
ui=read('common/custom_gui/RIP_church_controls.txt')
buttons={dict(dict(parse(b))['custom_button'])['name']:dict(dict(parse(b))['custom_button']) for _,b in keyed_blocks(ui,'custom_button')}
for i,key in enumerate(keys,1):
    b=buttons['rip_church_gc_petition_'+key+'_button']
    assert dict(b['frame'])['number']==str(i)
    assert ('rip_church_gc_can_petition_'+key,'yes') in b['trigger']
    assert ('rip_church_gc_petition_'+key+'_effect','yes') in b['effect']
assert 'rip_church_help.' not in ui and '_guide_button' not in ui
print(f'GC CURIA PASS: {cases} transaction cases, office targets, opinion direction, free navigation and eight native action bindings.')
print('LIMIT: source contracts only; no native clicks or election simulation.')
