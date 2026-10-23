"""Execute the agreed frontier/Host helpers; this is source modelling, not EU4."""
from copy import deepcopy
import re
import subprocess
import sys

from clausewitz_testlib import ROOT, read, named_block
from church_testlib import World as BaseWorld, parse, TRIGGERS, EFFECTS

for name in ('zaz_path_triggers', 'rip_frontier_host_triggers', 'rip_frontier_expedition_triggers'):
    TRIGGERS.update(parse(read('common/scripted_triggers/'+name+'.txt')))
for name in ('rip_frontier_host_effects', 'rip_frontier_expedition_effects'):
    EFFECTS.update(parse(read('common/scripted_effects/'+name+'.txt')))


class World(BaseWorld):
    def province(self, number, owner, religion='orthodox'):
        p = super().province(number, owner, religion)
        self.provinces[number] = p
        return p

    def condition(self, key, value, scope, root, prev):
        if key == 'calc_true_if':
            amount = int(dict(value)['amount'])
            passed = sum(1 for k, v in value if k != 'amount' and self.condition(k, v, scope, root, prev))
            return passed >= amount
        if key == 'is_in_capital_area':
            return scope.get('connected', False) == (value == 'yes')
        if key == 'is_state_core':
            return scope['core'] == self.ref(value,scope,root,prev)['id'] and scope.get('state',True)
        if key == 'country_or_non_sovereign_subject_holds':
            owner=self.countries[scope['owner']]; target=self.ref(value,scope,root,prev)
            return owner is target or (owner.get('overlord')==target['id'] and owner.get('non_sovereign',False))
        if key == 'num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with':
            fields=dict(value)
            return sum(self.condition('country_or_non_sovereign_subject_holds','ROOT',p,root,prev)
                       and self.gate([(k,v) for k,v in value if k!='value'],p,root,scope)
                       for p in self.provinces.values()) >= int(fields['value'])
        if key == 'is_claim':
            return self.ref(value,scope,root,prev)['id'] in scope.get('claims',set())
        if key == 'variable_arithmetic_trigger':
            before=deepcopy(scope['variables']); passed=True
            try:
                for k,v in value:
                    if k in ('export_to_variable','multiply_variable','change_variable'):
                        self.execute([(k,v)],scope,root,prev)
                    elif k!='custom_tooltip': passed &= self.condition(k,v,scope,root,prev)
                return passed
            finally: scope['variables']=before
        return super().condition(key,value,scope,root,prev)

    def execute(self, items, scope, root=None, prev=None):
        # Preserve if/else chains by delegating the whole list when no extra
        # leaf effects occur; nested calls return here through the base model.
        rest=[]
        for key,value in items:
            if key=='add_claim':
                tag=self.ref(value,scope,root or scope,prev)['id']
                scope.setdefault('claims',set()).add(tag)
                self.claims=getattr(self,'claims',[])+[int(scope['id'])]
            elif key=='log': pass
            else: rest.append((key,value))
        super().execute(rest,scope,root,prev)


def realm(ai=False):
    w=World(); c=w.country('HET'); foreign=w.country('MOS')
    c.update(adm_tech=20,treasury=2000,adm_power=1000,dip_power=1000,mil_power=1000,
             ai=ai,num_of_loans=0,current_income_balance=3,monthly_income=10)
    c['reforms']={'rip_hetman_cossacks_reform'}
    for number in range(1,7):
        p=w.province(number,c); p.update(region='crimea_region',terrain='steppe',connected=True,area='lower_don_area')
    for number in range(7,13):
        p=w.province(number,c); p.update(region='ural_region',terrain='steppe',connected=True,area='nogai_area')
    return w,c,foreign


def targets(w,foreign,region='crimea_region',count=12):
    for number in range(100,100+count):
        p=w.province(number,foreign); p.update(region=region,terrain='steppe',connected=False,area='other',neighbors={number-1})
    w.provinces[100]['neighbors']={1}


def gate(w,c,name): return w.gate(TRIGGERS[name],c)


def expedition_cases():
    cases=0
    for theatre,region,cash,adm,dip,mil,flag in (
        ('crimea','crimea_region',100,0,50,0,'ruthenian_eastward_policy'),
        ('ural','ural_region',150,0,50,50,'ruthenian_ural_gate_opened'),
        ('manchuria','manchuria_region',200,50,50,0,'ruthenian_manchurian_horizon')):
        w,c,foreign=realm(); targets(w,foreign,region)
        if theatre!='crimea': c['flags']['ruthenian_eastward_policy']=0
        if theatre=='manchuria': c['flags']['ruthenian_ural_gate_opened']=0
        can='rip_frontier_'+theatre+'_can_buy'; buy='rip_frontier_'+theatre+'_purchase_effect'
        assert gate(w,c,can)
        before=deepcopy(c); w.run(buy,c)
        assert w.claims==list(range(100,105)), (theatre,w.claims)
        assert c['treasury']==before['treasury']-cash
        assert all(c[p+'_power']==before[p+'_power']-v for p,v in [('adm',adm),('dip',dip),('mil',mil)])
        assert c['variables']['rip_frontier_claims_issued']==5
        assert c['variables']['rip_frontier_batches']==1
        assert not any(any('rip_frontier_batch_step' in f for f in p['flags']) for p in w.provinces.values())
        assert 'rip_frontier_batch_started' not in c['flags']
        first_mods=deepcopy(c['modifiers']); events=list(w.events)
        for day in (0,3649):
            w.day=day
            for other in ('crimea','ural','manchuria'): assert not gate(w,c,'rip_frontier_'+other+'_can_buy')
            paid=c['treasury']; w.run(buy,c); assert c['treasury']==paid
            cases+=1
        w.day=3650
        # Old claims alone are not a corridor. Conquest plus a real capital
        # connection opens the next batch; it does not reissue old rewards.
        assert not gate(w,c,can)
        for n in range(100,105):
            w.provinces[n].update(owner=c['id'],controlled_by=c['id'],connected=True)
        assert gate(w,c,can); w.run(buy,c)
        assert w.claims==list(range(100,110))
        assert c['modifiers']==first_mods and w.events==events
        assert c['flags'][flag]==0 and c['flags']['rip_frontier_expedition_recent']==3650
        assert c['variables']['rip_frontier_claims_issued']==10
        assert c['variables']['rip_frontier_ducats_spent']==cash*2
        # A model round-trip checks source persistence; engine save/load is separate.
        for n in range(105,110):
            w.provinces[n].update(owner=c['id'],controlled_by=c['id'],connected=True)
        clone=deepcopy(w); clone.day=7299
        assert not gate(clone,clone.countries['HET'],can)
        cases+=1
        for change in ('empty','enclave','occupied','own','subject','claim','core','poor','war','ai_loans','ai_deficit','ai_reserve'):
            w,c,foreign=realm(); targets(w,foreign,region)
            c['flags'].update(ruthenian_eastward_policy=0,ruthenian_ural_gate_opened=0)
            seed=w.provinces[100]
            if change=='empty': seed['is_city']=False
            if change=='enclave':
                for p in w.provinces.values(): p['connected']=False
            if change=='occupied': seed['controlled_by']='HET'
            if change=='own': seed['owner']='HET'
            if change=='subject': foreign.update(overlord='HET',non_sovereign=True)
            if change=='claim': seed['claims']={'HET'}
            if change=='core': seed['core']='HET'
            if change=='poor': c['treasury']=cash-1
            if change=='war': c['is_at_war']=True
            if change.startswith('ai_'):
                c['ai']=True
                if change=='ai_loans': c['num_of_loans']=1
                if change=='ai_deficit': c['current_income_balance']=-1
                if change=='ai_reserve': c['treasury']=cash+119
            assert not gate(w,c,can), (theatre,change)
            paid=c['treasury']; w.run(buy,c); assert c['treasury']==paid and not getattr(w,'claims',[])
            cases+=1
        w,c,foreign=realm(ai=True); targets(w,foreign,region)
        c['flags'].update(ruthenian_eastward_policy=0,ruthenian_ural_gate_opened=0)
        c['treasury']=cash+120; before=deepcopy(c['variables'])
        assert gate(w,c,can) and c['variables']==before
        w.run(buy,c); assert c['treasury']==120
        cases+=1
    return cases


def host_cases():
    w,c,foreign=realm(); p=w.provinces[1]; other=w.provinces[7]
    c['flags'].update(founded_don_host=0,founded_eastern_host=0)
    w.run('rip_host_network_upkeep_effect',c)
    assert gate(w,c,'rip_host_two_active')
    assert 'cossack_host_founded' in c['modifiers']
    assert 'cossack_host_muster' in p['modifiers'] and 'cossack_host_muster' in other['modifiers']
    outside=w.province(999,c); outside.update(area='unrelated',region='europe',terrain='steppe')
    outside['modifiers']['cossack_host_muster']=float('inf')
    w.run('rip_host_network_upkeep_effect',c)
    assert 'cossack_host_muster' not in outside['modifiers']
    # Loss/occupation suspends a region. One still-held Host keeps one national package.
    for n in range(1,7): w.provinces[n]['controlled_by']='MOS'
    w.run('rip_host_network_upkeep_effect',c)
    assert not gate(w,c,'rip_host_two_active') and 'cossack_host_muster' not in p['modifiers']
    assert 'cossack_host_founded' in c['modifiers']
    for n in range(7,13): w.provinces[n]['owner']='MOS'
    w.run('rip_host_network_upkeep_effect',c); w.run('rip_host_network_upkeep_effect',foreign)
    assert 'cossack_host_founded' not in c['modifiers']
    assert 'cossack_host_muster' not in other['modifiers']
    dates=deepcopy(c['flags']); money=c['treasury']
    for n in range(1,13): w.provinces[n].update(owner='HET',controlled_by='HET')
    w.run('rip_host_network_upkeep_effect',c)
    assert gate(w,c,'rip_host_two_active') and c['flags']==dates and c['treasury']==money
    # Changed identity loses benefits while keeping the founding dates.
    c['reforms'].clear(); w.run('rip_host_network_upkeep_effect',c)
    assert not c['modifiers'] and c['flags']==dates
    return 7


def contracts():
    result=subprocess.run([sys.executable,'-B',str(ROOT/'tools/build_frontier_design.py'),'--check'],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    for path in ('common/scripted_effects/rip_frontier_expedition_effects.txt','common/scripted_triggers/rip_frontier_expedition_triggers.txt'):
        assert 'add_permanent_claim' not in read(path)
    assert '1756' in read('decisions/DniesterEstuaryDecisions.txt')
    assert '282' in named_block(read('decisions/OdesaGovernmentDecisions.txt'),'establish_hajibey_free_port')
    for lang in ('english','french','german','spanish'):
        text=read('localisation/rip_frontier_design_l_'+lang+'.yml')
        assert 'Shared ten-year term' in text and 'five NEW normal claims' in text


if __name__=='__main__':
    contracts(); count=expedition_cases()+host_cases()
    # Counterexample: opening the term permanently must break the same tests.
    original=TRIGGERS['rip_frontier_term_open']; TRIGGERS['rip_frontier_term_open']=parse('always = yes')
    try:
        try: expedition_cases()
        except AssertionError: pass
        else: raise AssertionError('missing shared term escaped')
    finally: TRIGGERS['rip_frontier_term_open']=original
    print(f'FRONTIER DESIGN PASS: {count} source cases; bounded connected claims, AI reserve, repeated payment and Host base loss/recovery. Runtime unverified.')
