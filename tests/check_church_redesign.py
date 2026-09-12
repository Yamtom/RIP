"""Execute the actual church transactions with explicit source-state fixtures.
Static evidence only: no GUI renderer, EU4 campaign or native AI is simulated.
"""
from copy import deepcopy
from itertools import permutations
import re, subprocess, sys
from church_testlib import World, fixture, TRIGGERS, EFFECTS, parse
from clausewitz_testlib import ROOT, read, named_block, normalized, vanilla_root, keyed_blocks

cases=0
def checked():
    global cases
    cases+=1

def link(a,b):
    a['neighbors'].add(b['id']); b['neighbors'].add(a['id'])

def active(c): return {k for k in ('war','mercy','building','mission') if 'rip_church_icon_'+k in c['flags']}

# Every PA point, including all three capacity boundaries and native offsets.
mods=dict(parse(read('common/event_modifiers/RIP_church_redesign_modifiers.txt')))
for authority in range(101):
    w,c,p=fixture(); c['patriarch_authority']=authority/100
    w.run('rip_church_ro_recount_effect',c)
    expected=1+(authority>=30)+(authority>=65)+(authority>=90)
    assert c['variables']['rip_church_capacity']==expected
    assert c['variables']['rip_church_fervor_income']==expected+1
    w.run('rip_church_refresh_pa_effect',c)
    band=authority//5
    assert 'rip_church_ro_pa_country_'+str(band) in c['modifiers']
    assert 'rip_church_ro_pa_local_'+str(band) in p['modifiers']
    payload=dict(mods['rip_church_ro_pa_local_'+str(band)])
    remaining=.33*authority/100+float(payload['local_manpower_modifier'])
    assert -1e-9 <= remaining < .01651
    checked()

    for balance,orientation,retained in [(-60,'east',.75),(0,'middle',.375),(60,'rome',0)]:
        w,c,p=fixture('greek_catholic'); c['patriarch_authority']=authority/100
        c['variables']['rip_church_communion']=balance
        minority=w.province(296,c,'orthodox')
        w.run('rip_church_refresh_pa_effect',c)
        name='rip_church_gc_'+orientation+'_pa_local_'+str(band)
        assert name in p['modifiers'] and not minority['modifiers']
        payload=dict(mods[name]); national=dict(mods['rip_church_gc_pa_country_'+str(band)])
        assert -1e-9<=.33*authority/100+float(payload['local_manpower_modifier'])<.01651
        assert -1e-9<=.02*authority/100+float(national['global_missionary_strength'])<.001001
        if authority%5==0:
            assert abs(-3*authority/100+float(payload['local_unrest'])+retained*authority/100)<1e-9
        checked()

# All activation orders: PA drops remove the newest, never an arbitrary icon.
for order in permutations(('war','mercy','building','mission')):
    w,c,p=fixture(); c['variables']['rip_church_fervor']=100
    for icon in order: w.run('rip_church_toggle_'+icon+'_effect',c)
    assert active(c)==set(order) and c['variables']['rip_church_fervor']==60
    assert c['variables']['rip_church_fervor_cost']==14
    c['patriarch_authority']=.64
    w.run('rip_church_ro_enforce_capacity_effect',c)
    assert active(c)==set(order[:2]) and c['variables']['rip_church_fervor']==60
    c['patriarch_authority']=.29
    w.run('rip_church_ro_enforce_capacity_effect',c)
    assert active(c)=={order[0]}
    checked()

for fuel,expected in [(0,2),(2,2),(3,3),(8,3),(9,4)]:
    w,c,p=fixture(); c['variables']['rip_church_fervor']=100
    for icon in ('war','mercy','building','mission'): w.run('rip_church_toggle_'+icon+'_effect',c)
    c['variables']['rip_church_fervor']=fuel
    w.run('rip_church_ro_monthly_effect',c)
    assert len(active(c))==expected,(fuel,active(c))
    assert c['variables']['rip_church_fervor']>=0
    checked()

for icon in ('war','mercy','building','mission'):
    w,c,p=fixture(); c['variables']['rip_church_fervor']=30
    w.run('rip_church_toggle_'+icon+'_effect',c)
    w.run('rip_church_toggle_'+icon+'_effect',c)  # The second click turns it off.
    w.run('rip_church_toggle_'+icon+'_effect',c)  # Same-year reactivation is denied.
    assert not active(c) and c['variables']['rip_church_fervor']==20
    w.day=365; w.run('rip_church_toggle_'+icon+'_effect',c)
    assert active(c)=={icon} and c['variables']['rip_church_fervor']==10
    checked()

# Startup is idempotent; resources and paid cooldowns survive reload.
for faith in ('russian_orthodox','greek_catholic'):
    w,c,p=fixture(faith); c['flags']['rip_ro_stage_patriarchate']=0
    c['modifiers']['uniate_educational_network']=10000
    w.run('rip_church_v3_initialize_effect',c)
    c['variables'].update(rip_church_fervor=41,rip_church_papal_standing=37,rip_church_communion=-20)
    c['flags']['rip_church_icon_war_used']=0
    snapshot=deepcopy(c); w.run('rip_church_v3_initialize_effect',c)
    assert c==snapshot and 'uniate_educational_network' not in c['modifiers']
    checked()

# Recognition does not require a living Byzantium, nor does a delay imply schism.
for religion in ('russian_orthodox','greek_catholic'):
    w,c,p=fixture(religion); w.run('rip_church_v3_initialize_effect',c)
    c['flags']['historic_achievement']=0
    c['variables'].update(rip_church_fervor=50,rip_church_papal_standing=50)
    w.run('rip_church_refresh_pa_effect',c)
    c['religion']='orthodox'; w.run('rip_church_v3_religion_change_effect',c)
    assert not active(c) and 'rip_church_v3_active' not in c['flags']
    assert 'historic_achievement' in c['flags'] and c['variables']['rip_church_papal_standing']==0
    assert not any('_pa_' in m for m in c['modifiers']) and not any('_pa_' in m for m in p['modifiers'])
    checked()

for year in (1589,1590,1593,1650):
    w,c,p=fixture(); w.year=year
    w.run('rip_church_ro_accept_recognition_effect',c)
    assert ('rip_church_ro_recognized' in c['flags'])==(year>=1593)
    assert 'rip_church_ro_schismatic' not in c['flags']
    w.year=1593; w.run('rip_church_ro_monthly_effect',c)
    assert 'rip_church_ro_recognized' in c['flags']
    checked()
w,c,p=fixture(); w.run('rip_church_ro_monthly_effect',c)
assert 'rip_church_ro_schismatic' not in c['flags']; checked()
w.run('rip_church_ro_choose_schism_effect',c)
w.run('rip_church_ro_begin_reconciliation_effect',c)
assert c['dip_power']==400 and c['patriarch_authority']==.8
w.run('rip_church_ro_begin_reconciliation_effect',c)
assert c['dip_power']==400
w.day=1824; w.run('rip_church_ro_monthly_effect',c)
assert 'rip_church_ro_schismatic' in c['flags']
w.day=1825; w.run('rip_church_ro_monthly_effect',c)
assert 'rip_church_ro_recognized' in c['flags']
w.run('rip_church_ro_choose_schism_effect',c)
assert c['dip_power']==400 and 'rip_church_ro_recognized' not in c['flags']; checked()

# Communion boundaries and separate PAP-dependent Standing.
# Moscow councils now pay into capacity/fuel instead of an independent bonus family.
for policy in ('lands','books','courts'):
    w,c,p=fixture(); c['patriarch_authority']=.5
    w.run('rip_ro_enact_council_policy_effect',c,POLICY='rip_ro_sobor_'+policy)
    assert c['treasury']==900 and c['adm_power']==450
    assert abs(c['patriarch_authority']-({'lands':.6,'books':.4,'courts':.5}[policy]))<1e-9
    assert c['variables'].get('rip_church_fervor',0)==(30 if policy=='books' else 0)
    paid=deepcopy(c); w.run('rip_ro_enact_council_policy_effect',c,POLICY='rip_ro_sobor_'+policy); assert c==paid
    w.day=3650; w.run('rip_ro_enact_council_policy_effect',c,POLICY='rip_ro_sobor_'+policy)
    assert c['treasury']==800; checked()

for invalid in ({'treasury':99},{'adm_power':49},{'patriarch_authority':.09},{'religion':'catholic'},{'is_at_war':True}):
    w,c,p=fixture(); c.update(invalid); paid=deepcopy(c)
    w.run('rip_ro_enact_council_policy_effect',c,POLICY='rip_ro_sobor_books'); assert c==paid; checked()

# Early union: exact payment, five years, PAP support and no country-wide recoloring.
for religion in ('orthodox','catholic'):
    w,c,p=fixture(religion); w.year=1444; p['religion']='orthodox'
    q=w.province(296,c,'orthodox')
    assert w.gate(TRIGGERS['rip_church_can_begin_florence'],c)
    w.run('rip_church_begin_florence_effect',c)
    assert (c['adm_power'],c['dip_power'],c['treasury'])==(300,400,880)
    paid=deepcopy(c); w.run('rip_church_begin_florence_effect',c); assert c==paid
    w.day=1824; w.run('rip_church_complete_florence_effect',c); assert c['religion']==religion
    w.day=1825; w.countries['PAP']['opinions']['MOS']=0
    w.run('rip_church_complete_florence_effect',c); assert c['religion']==religion
    w.countries['PAP']['opinions']['MOS']=100; w.run('rip_church_complete_florence_effect',c)
    assert c['religion']==('greek_catholic' if religion=='orthodox' else 'catholic')
    assert sum(x['religion']=='greek_catholic' for x in w.provinces.values())==1
    assert q['religion']=='orthodox'
    assert ('rip_church_supports_union' in c['flags'])==(religion=='catholic')
    snapshot=deepcopy(w.provinces); w.run('rip_church_complete_florence_effect',c); assert w.provinces==snapshot; checked()
for year,eligible in [(1443,False),(1444,True),(1501,True),(1502,False)]:
    w,c,p=fixture('orthodox'); w.year=year
    assert w.gate(TRIGGERS['rip_church_can_begin_florence'],c)==eligible; checked()

# Ecumenical eligibility includes every prerequisite and restarts after coercion.
w,c,p=fixture('greek_catholic'); p['religion']='orthodox'; p['flags']['rip_church_rite_recognized']=0
q=w.province(296,c,'catholic'); q['flags']['rip_church_rite_recognized']=0
ally=w.country('KIE','orthodox'); ally['allies'].add('MOS'); ally['opinions']['MOS']=100
c['flags'].update(rip_church_union_founded=0,rip_church_balanced_since=3650)
c['variables'].update(rip_church_communion=0,rip_church_papal_standing=60); w.day=7300
assert w.gate(TRIGGERS['rip_church_can_ecumenism'],c)
for defect in ('age','balance_age','standing','orientation','orthodox_rite','catholic_rite','ally','forced'):
    backup=deepcopy((c,p,q,ally)); day=w.day
    if defect=='age': w.day=7299
    if defect=='balance_age': c['flags']['rip_church_balanced_since']=3651
    if defect=='standing': c['variables']['rip_church_papal_standing']=59.9
    if defect=='orientation': c['variables']['rip_church_communion']=41
    if defect=='orthodox_rite': p['flags'].clear()
    if defect=='catholic_rite': q['flags'].clear()
    if defect=='ally': ally['allies'].clear()
    if defect=='forced': c['flags']['rip_church_forced_integration']=4000
    assert not w.gate(TRIGGERS['rip_church_can_ecumenism'],c),defect
    for item,original in zip((c,p,q,ally),backup): item.clear(); item.update(original)
    w.day=day; checked()
w.run('rip_church_achieve_ecumenism_effect',c)
assert 'rip_church_ecumenical' in c['flags'] and c['variables']['rip_church_papal_standing']==60
assert not any(k.startswith('rip_church_gc_') for k in c['modifiers']); checked()

# Communion boundaries and separate PAP-dependent Standing.
for balance,orientation,income in [(-100,'eastern',.1),(-40.001,'eastern',.1),(-40,'balanced',.25),(0,'balanced',.25),(40,'balanced',.25),(40.001,'roman',.5),(100,'roman',.5)]:
    w,c,p=fixture('greek_catholic'); c['variables']['rip_church_communion']=balance
    assert w.gate(TRIGGERS['rip_church_gc_'+orientation],c)
    w.run('rip_church_gc_monthly_effect',c)
    assert c['variables']['rip_church_papal_standing']==income
    authority=c['patriarch_authority']; c['wars'].add('PAP')
    w.run('rip_church_gc_monthly_effect',c)
    assert c['variables']['rip_church_papal_standing']==income and c['patriarch_authority']==authority
    del w.countries['PAP']; c['wars'].clear(); w.run('rip_church_gc_monthly_effect',c)
    assert c['variables']['rip_church_papal_standing']==income; checked()
for direction in ('east','rome'):
    w,c,p=fixture('greek_catholic')
    w.run('rip_church_gc_shift_'+direction+'_effect',c)
    assert c['adm_power']==475
    snapshot=deepcopy(c); w.run('rip_church_gc_shift_'+direction+'_effect',c); assert c==snapshot
    w.day=1825; w.run('rip_church_gc_shift_'+direction+'_effect',c); assert c['adm_power']==450; checked()

# Each privilege spends the right resource, occupies the common slot, and expires.
for option,balance in [('infrastructure',-60),('coexistence',0),('legate',60),('papal_support',0)]:
    w,c,p=fixture('greek_catholic'); c['variables'].update(rip_church_communion=balance,rip_church_papal_standing=90)
    c['treasury']=75 if option=='infrastructure' else 100
    w.run('rip_church_gc_'+option+'_effect',c)
    assert c['treasury']==0
    assert c['patriarch_authority']==(.8 if option in ('infrastructure','coexistence') else 1)
    assert c['variables']['rip_church_papal_standing']==(90 if option in ('infrastructure','coexistence') else 60)
    assert w.gate(TRIGGERS['rip_church_gc_has_privilege'],c)
    paid=deepcopy(c)
    for other in ('infrastructure','coexistence','legate','papal_support'): w.run('rip_church_gc_'+other+'_effect',c)
    assert c==paid
    w.day=3650; assert not w.gate(TRIGGERS['rip_church_gc_has_privilege'],c); checked()

# State/province-faith combinations, exact development price, minimum term and loss.
for state,parish,eligible in [('greek_catholic','orthodox',True),('greek_catholic','catholic',True),('orthodox','greek_catholic',False),('catholic','greek_catholic',False),('greek_catholic','russian_orthodox',True)]:
    w,c,p=fixture(state); p['religion']=parish; p['development']=17
    assert w.gate(TRIGGERS['rip_church_can_recognize_rite'],p)==eligible
    w.run('rip_church_recognize_rite_effect',p)
    assert c['adm_power']==500-17*eligible
    w.run('rip_church_recognize_rite_effect',p); assert c['adm_power']==500-17*eligible
    if eligible:
        w.day=3649; w.run('rip_church_revoke_rite_effect',p); assert 'rip_church_rite_recognized' in p['flags']
        w.day=3650; w.run('rip_church_revoke_rite_effect',p)
        assert 'rip_church_rite_recognized' not in p['flags'] and 'rip_church_rite_revoked' in p['modifiers']
        assert 'rip_church_forced_integration' in c['flags']
    checked()
w,c,p=fixture('greek_catholic'); p['religion']='orthodox'; c['adm_power']=11
w.run('rip_church_recognize_rite_effect',p); assert c['adm_power']==11 and not p['flags']; checked()

# Sole centre: price, occupied pause, Catholic inheritance, invalid-owner loss and term.
w,c,p=fixture('greek_catholic'); w.run('rip_church_found_center_effect',c)
assert p['is_reformation_center'] and c['adm_power']==400 and c['treasury']==880
w.run('rip_church_found_center_effect',c); assert c['adm_power']==400
q=w.province(296,c,'orthodox'); q['area']=p['area']; w.run('rip_church_rebuild_union_network_effect',c)
assert w.gate(TRIGGERS['rip_church_union_target'],q)
p['controlled_by']='PAP'; assert not w.gate(TRIGGERS['rip_church_union_target'],q)
w.flags.pop('rip_church_union_swept',None); w.run('rip_church_union_global_maintenance_effect',c)
assert not p['is_reformation_center'] and 'rip_church_center_suspended' in p['flags']
assert not w.gate(TRIGGERS['rip_church_can_found_center'],c)
p['controlled_by']='MOS'; w.flags.pop('rip_church_union_swept',None); w.run('rip_church_union_global_maintenance_effect',c)
assert p['is_reformation_center'] and 'rip_church_center_suspended' not in p['flags']
heir=w.country('POL','catholic'); heir['flags']['rip_church_supports_union']=0
p.update(owner='POL',controlled_by='POL'); w.day=28; w.run('rip_church_union_global_maintenance_effect',c)
assert p['is_reformation_center']
heir['flags'].clear(); w.day=56; w.run('rip_church_union_global_maintenance_effect',c)
assert not p['is_reformation_center']
p.update(owner='MOS',controlled_by='MOS'); w.day=7299; w.run('rip_church_found_center_effect',c); assert not p['is_reformation_center']
w.day=7300; w.run('rip_church_found_center_effect',c); assert p['is_reformation_center']; checked()

# Migration ordering: Brest, then highest development, then smallest province ID.
for brest in (True,False):
    w,c,p=fixture('greek_catholic'); p['is_reformation_center']=True; p['development']=20
    q=w.province(280,c,'greek_catholic'); q.update(is_reformation_center=True,development=20)
    if brest: w.province(277,c,'greek_catholic')['is_reformation_center']=True
    w.run('rip_church_union_center_migration_effect',c)
    centers=[x['id'] for x in w.provinces.values() if x['is_reformation_center']]
    assert centers==(['277'] if brest else ['280']),centers
    before=deepcopy(w.provinces); w.run('rip_church_union_center_migration_effect',c); assert w.provinces==before; checked()

# Area frontiers need a parish bridge, but never unanimity in the previous area.
w,c,p=fixture('greek_catholic'); p['is_reformation_center']=True
chain=[p]
for number,area in [(296,'b'),(297,'c'),(298,'d'),(299,'e'),(300,'f')]:
    q=w.province(number,c,'greek_catholic'); q['area']=area; link(chain[-1],q); chain.append(q)
holdout=w.province(301,c,'orthodox'); holdout['area']='a'
w.run('rip_church_rebuild_union_network_effect',c)
assert 'rip_church_union_ring_2' in chain[2]['flags'] and 'rip_church_union_ring_4' in chain[4]['flags']
chain[3]['religion']='orthodox'
assert not w.gate(TRIGGERS['rip_church_union_target'],chain[3])
c['flags']['rip_church_ecumenical']=0; assert w.gate(TRIGGERS['rip_church_union_target'],chain[3])
assert not chain[5]['flags']
chain[1]['religion']='orthodox'; w.run('rip_church_rebuild_union_network_effect',c)
assert 'rip_church_union_ring_2' not in chain[2]['flags']; checked()

# A merchant far from the controlled core network cannot create a missionary wave.
for schism,dlc in ((False,True),(True,True),(True,False)):
    w,c,p=fixture(); anchor=w.province(33,c,'russian_orthodox'); link(p,anchor)
    if dlc: c['dlcs'].add('Cradle of Civilization')
    target_owner=w.country('NOV','orthodox'); q=w.province(34,target_owner,'orthodox'); link(anchor,q)
    anchor['traders'].add('MOS'); anchor['shares']['MOS']=50
    c['variables']['rip_church_fervor']=100; w.run('rip_church_toggle_mission_effect',c)
    if schism: c['flags']['rip_church_ro_schismatic']=0
    w.run('rip_church_ro_refresh_connections_effect',c)
    assert w.gate(TRIGGERS['rip_church_node_novgorod_can_open'],c)==(schism and dlc)
    if schism and dlc:
        w.run('rip_church_node_novgorod_toggle_effect',c)
        assert c['variables']['rip_church_nodes']==1 and c['variables']['rip_church_fervor_cost']==4
        assert 'rip_church_ro_trade_target@MOS' in q['flags']
        w.run('rip_church_refresh_conversion_resistance_effect',c)
        assert 'rip_church_conversion_resistance' in q['modifiers']
        anchor['traders'].clear(); w.run('rip_church_ro_maintain_nodes_effect',c)
        assert c['variables']['rip_church_nodes']==0
        anchor['traders'].add('MOS'); p['neighbors'].clear(); anchor['neighbors'].discard(p['id'])
        w.run('rip_church_ro_maintain_nodes_effect',c)
        assert not w.gate(TRIGGERS['rip_church_node_novgorod_can_open'],c)
    checked()

# Symmetric pair modifiers survive either country's refresh and change with status.
w,c,p=fixture(); peer=w.country('NOV','orthodox')
w.run('rip_church_refresh_relations_effect',c)
assert ('NOV','rip_church_opinion_ro_unrecognized') in c['opinion_modifiers']
w.run('rip_church_ro_accept_recognition_effect',c)
w.run('rip_church_refresh_relations_effect',peer)
assert ('NOV','rip_church_opinion_ro_recognized') in c['opinion_modifiers']
assert ('MOS','rip_church_opinion_ro_recognized') in peer['opinion_modifiers']
w.run('rip_church_ro_choose_schism_effect',c)
assert ('NOV','rip_church_opinion_ro_recognized') not in c['opinion_modifiers']
assert ('NOV','rip_church_opinion_ro_schism') in c['opinion_modifiers']; checked()

# Source contracts: engine-specific syntax, preserved vanilla hosts/profiles and scopes.
rate_block=next(block for _,block in keyed_blocks(read('customizable_localization/rip_church_redesign.txt'),'defined_text') if 'name = GetChurchStandingRate' in block)
rate_rows=[dict(row) for key,row in dict(parse(rate_block))['defined_text'] if key=='text']
for balance,expected in [(-50,'east'),(0,'middle'),(50,'rome')]:
    for support in ('supported','war','opinion','absent'):
        w,c,p=fixture('greek_catholic'); c['variables']['rip_church_communion']=balance
        if support=='war': c['wars'].add('PAP')
        elif support=='opinion': w.countries['PAP']['opinions']['MOS']=49
        elif support=='absent': del w.countries['PAP']
        displayed=next(row['localisation_key'] for row in rate_rows if w.gate(row['trigger'],c))
        assert displayed=='rip_church_standing_rate_'+(expected if support=='supported' else 'zero')
        checked()
gc_gui=next(block for _,block in keyed_blocks(read('interface/countryreligionview.gui'),'windowType') if 'name = "rip_church_gc_panel"' in block and 'name = "countryreligionview"' not in block)
assert 'GFX_country_religion_view_bg' not in gc_gui
assert 'GFX_rip_church_union_frame' in gc_gui
assert 'rip_church_pa_display' not in read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml').split('rip_church_gc_resources:0',1)[1].split('\n',1)[0]
for file in (ROOT/'common/scripted_effects').glob('rip_church_*.txt'):
    assert not re.search(r'\bvalue\s*=\s*rip_church_',file.read_text()),file
for generator in ('build_church_support.py','build_church_gui.py','build_church_localisation.py'):
    subprocess.run([sys.executable,'-B',str(ROOT/'tools'/generator),'--check'],check=True)
gui=read('common/custom_gui/RIP_church_controls.txt')
for _,button in keyed_blocks(gui,'custom_button'):
    assert 'trigger =' in button and 'effect =' in button and 'tooltip =' in button
    if re.search(r'name = rip_church_(?:recognize_rite|revoke_rite|latin_consent)_button',button):
        assert ('owned_by','FROM') in dict(dict(parse(button))['custom_button'])['trigger']
for path,host in [('countryreligionview.gui','countryreligionview'),('provinceview.gui','province_window')]:
    actual=read('interface/'+path)
    marker='# RIP church custom controls, descendants of the supported host.'
    assert actual.count(marker)==1
    before,tail=actual.split(marker)
    # All injected windows are complete; remove them before comparing the host.
    for _,block in keyed_blocks(tail,'windowType'):
        if 'scripted = yes' in block: tail=tail.replace(block,'',1)
    donor=(vanilla_root()/'interface'/path).read_text(encoding='utf-8-sig')
    assert normalized(before+tail)==normalized(donor),path
assert 'center_of_reformation = yes' in read('common/trading_policies/RIP_church_mission_network.txt')
policies=read('common/trading_policies/00_trading_policies.txt')
donor_policies=(vanilla_root()/'common/trading_policies/00_trading_policies.txt').read_text(encoding='utf-8-sig')
guard='\n\t\tNOT = { religion = greek_catholic }\n\t\tNOT = { religion = russian_orthodox }'
assert normalized(policies.replace(guard,''))==normalized(donor_policies)
policy=dict(parse(named_block(policies,'propagate_religion')))['propagate_religion']
for gate in ('potential','can_select','can_maintain'):
    requirements=dict(policy)[gate][:2]
    for faith,allowed in [('greek_catholic',False),('russian_orthodox',False),('sunni',True),('catholic',True)]:
        w,c,p=fixture(faith)
        c['flags']['can_use_propagate_religion']=0
        assert w.gate(requirements,c)==allowed
        checked()
mission=dict(parse(read('common/trading_policies/RIP_church_mission_network.txt')))['rip_church_mission_network']
for faith,allowed in [('greek_catholic',False),('russian_orthodox',True)]:
    w,c,p=fixture(faith)
    assert w.gate(dict(mission)['potential'],c)==allowed
    checked()
native=read('common/religious_conversions/00_religious_conversions.txt')
weights=named_block(named_block(native,'propagate_religion_policy'),'target_province_weights')
assert re.search(r'modifier\s*=\s*\{\s*factor\s*=\s*0\s+FROM\s*=\s*\{\s*religion\s*=\s*greek_catholic\s*\}',weights)
donor=(vanilla_root()/'common/religious_conversions/00_religious_conversions.txt').read_text(encoding='utf-8-sig')
for name in re.findall(r'(?m)^(\w+)\s*=\s*\{',donor):
    if name!='propagate_religion_policy': assert normalized(named_block(native,name))==normalized(named_block(donor,name)),name
for field in ('patriarch_authority_local','patriarch_authority_global'):
    assert not any(re.search(r'(?m)^'+field+r'\s*=',p.read_text(encoding='utf-8-sig')) for p in (ROOT/'common/static_modifiers').glob('*.txt'))
print(f'CHURCH REDESIGN PASS: {cases} source-executed cases; transactions, migration, geography and vanilla-isolation contracts.')
print('LIMIT: native propagation, save loading, GUI and 50-year campaign effectiveness require EU4 evidence.')
