"""Generate the agreed regional-host and bounded-frontier policy helpers."""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
HOSTS = {
    'don': ('founded_don_host', 2, 'area = lower_don_area'),
    'danube': ('founded_danube_sich', 1, 'OR = { area = silistria_area province_id = 1756 AND = { area = wallachia_area OR = { province_id = 160 province_id = 4531 province_id = 4532 } } }'),
    'eastern': ('founded_eastern_host', 1, 'OR = { area = circassia_area area = nogai_area }'),
    'sloboda': ('founded_sloboda_host', 2, 'area = sloboda_ukraine_area'),
}
THEATRES = {
    'crimea': ('crimea_region', 100, 0, 50, 0, 'ruthenian_eastward_policy', 'ruthenian_eastward_mandate', 7300, 'ruthenian_eastward.1'),
    'ural': ('ural_region', 150, 0, 50, 50, 'ruthenian_ural_gate_opened', 'ruthenian_ural_gate', 9125, 'ruthenian_eastward.2'),
    'manchuria': ('manchuria_region', 200, 50, 50, 0, 'ruthenian_manchurian_horizon', 'ruthenian_manchurian_push', 9125, 'ruthenian_eastward.3'),
}

def block(name, body):
    return name + ' = {\n' + '\n'.join('\t' + line if line else '' for line in body.splitlines()) + '\n}\n'

def outputs():
    result = {}
    triggers=[]
    for key,(flag,count,geography) in HOSTS.items():
        triggers.append(block('rip_host_'+key+'_active', f'is_cossack_polity = yes\nhas_country_flag = {flag}\nnum_of_owned_provinces_with = {{ value = {count} controlled_by = ROOT is_city = yes {geography} }}'))
    triggers.append(block('rip_host_any_active', 'OR = { '+' '.join('rip_host_'+k+'_active = yes' for k in HOSTS)+' }'))
    triggers.append(block('rip_host_two_active', 'calc_true_if = { amount = 2 '+' '.join('rip_host_'+k+'_active = yes' for k in HOSTS)+' }'))
    regions=' '.join('AND = { '+geography+' ROOT = { rip_host_'+key+'_active = yes } }' for key,(_,_,geography) in HOSTS.items())
    triggers.append(block('rip_host_muster_eligible', 'controlled_by = ROOT\nis_state_core = ROOT\nrip_is_steppe_or_grasslands = yes\nOR = { '+regions+' }'))
    result['common/scripted_triggers/rip_frontier_host_triggers.txt']='\n'.join(triggers)
    upkeep='''if = {
 limit = { rip_host_any_active = yes }
 if = { limit = { NOT = { has_country_modifier = cossack_host_founded } } add_country_modifier = { name = cossack_host_founded duration = -1 } }
}
if = { limit = { NOT = { rip_host_any_active = yes } } remove_country_modifier = cossack_host_founded }
every_owned_province = {
 if = { limit = { has_province_modifier = cossack_host_muster NOT = { rip_host_muster_eligible = yes } } remove_province_modifier = cossack_host_muster }
 if = { limit = { rip_host_muster_eligible = yes NOT = { has_province_modifier = cossack_host_muster } } add_province_modifier = { name = cossack_host_muster duration = -1 } }
}'''
    result['common/scripted_effects/rip_frontier_host_effects.txt']=block('rip_host_network_upkeep_effect',upkeep)

    triggers=[block('rip_frontier_term_open', 'OR = { NOT = { has_country_flag = rip_frontier_expedition_recent } had_country_flag = { flag = rip_frontier_expedition_recent days = 3650 } }')]
    triggers.append(block('rip_frontier_capital_base', 'owned_by = ROOT\ncontrolled_by = ROOT\nis_city = yes\nis_in_capital_area = yes'))
    triggers.append(block('rip_frontier_new_claim_target', '''is_city = yes
controlled_by = owner
NOT = { country_or_non_sovereign_subject_holds = ROOT }
NOT = { is_core = ROOT }
NOT = { is_claim = ROOT }
OR = {
 AND = { ROOT = { NOT = { has_country_flag = rip_frontier_batch_started } } any_neighbor_province = { rip_frontier_capital_base = yes } }
 AND = { ROOT = { has_country_flag = rip_frontier_batch_started } any_neighbor_province = { has_province_flag = rip_frontier_batch_step_@ROOT } }
}'''))
    for key,(region,cash,adm,dip,mil,flag,modifier,duration,event) in THEATRES.items():
        terrain='\nrip_is_crimea_frontier_terrain = yes' if key=='crimea' else ''
        triggers.append(block('rip_frontier_'+key+'_target', 'region = '+region+terrain+'\nrip_frontier_new_claim_target = yes'))
        triggers.append(block('rip_frontier_'+key+'_has_target', 'any_province = { rip_frontier_'+key+'_target = yes }'))
        # Reserve one year of gross income AFTER payment: deliberately conservative,
        # includes at least the current military upkeep without an unsupported expense export.
        triggers.append(block('rip_frontier_'+key+'_ai_budget', f'''NOT = {{ num_of_loans = 1 }}
current_income_balance = 0
variable_arithmetic_trigger = {{
 custom_tooltip = rip_frontier_ai_reserve_tt
 export_to_variable = {{ which = rip_frontier_reserve value = monthly_income }}
 export_to_variable = {{ which = rip_frontier_cash value = treasury }}
 multiply_variable = {{ which = rip_frontier_reserve value = 12 }}
 change_variable = {{ which = rip_frontier_reserve value = {cash} }}
 check_variable = {{ which = rip_frontier_cash which = rip_frontier_reserve }}
}}'''))
    result['common/scripted_triggers/rip_frontier_expedition_triggers.txt']='\n'.join(triggers)
    effects=[]
    clear='every_province = { limit = { has_province_flag = rip_frontier_batch_step_@ROOT } clr_province_flag = rip_frontier_batch_step_@ROOT }\nclr_country_flag = rip_frontier_batch_started'
    effects.append(block('rip_frontier_clear_batch_effect',clear))
    for key,(region,cash,adm,dip,mil,flag,modifier,duration,event) in THEATRES.items():
        one=f'''random_province = {{
 limit = {{ rip_frontier_{key}_target = yes }}
 add_claim = ROOT
 set_province_flag = rip_frontier_batch_step_@ROOT
 ROOT = {{ set_country_flag = rip_frontier_batch_started change_variable = {{ which = rip_frontier_claims_issued value = 1 }} }}
 log = "RIP_FRONTIER CLAIM {key} [Root.GetName] [This.GetName]"
}}'''
        effects.append(block('rip_frontier_'+key+'_one_effect',one))
        pay='\n'.join(f'add_{power}_power = -{amount}\nchange_variable = {{ which = rip_frontier_{power}_spent value = {amount} }}' for power,amount in [('adm',adm),('dip',dip),('mil',mil)] if amount)
        # One-time benefits and event choices never refresh when buying another batch.
        effects.append(block('rip_frontier_'+key+'_purchase_effect',f'''if = {{
 limit = {{ rip_frontier_{key}_can_buy = yes }}
 rip_frontier_clear_batch_effect = yes
 add_treasury = -{cash}
 change_variable = {{ which = rip_frontier_ducats_spent value = {cash} }}
 {pay}
 set_country_flag = rip_frontier_expedition_recent
 set_country_flag = rip_frontier_{key}_purchased
 change_variable = {{ which = rip_frontier_batches value = 1 }}
 rip_frontier_{key}_one_effect = yes
 rip_frontier_{key}_one_effect = yes
 rip_frontier_{key}_one_effect = yes
 rip_frontier_{key}_one_effect = yes
 rip_frontier_{key}_one_effect = yes
 rip_frontier_clear_batch_effect = yes
 if = {{
  limit = {{ NOT = {{ has_country_flag = {flag} }} }}
  set_country_flag = {flag}
  set_country_flag = rip_frontier_{key}_benefit_started
  add_country_modifier = {{ name = {modifier} duration = {duration} }}
  country_event = {{ id = {event} }}
 }}
 log = "RIP_FRONTIER PURCHASE {key} [Root.GetName]"
}}'''))
    # Country gates include resource and territory rules; direct callers use these too.
    for key,(_,cash,adm,dip,mil,flag,modifier,duration,event) in THEATRES.items():
        resources='\n'.join(f'{power}_power = {amount}' for power,amount in [('adm',adm),('dip',dip),('mil',mil)] if amount)
        previous='' if key=='crimea' else 'has_country_flag = '+('ruthenian_eastward_policy' if key=='ural' else 'ruthenian_ural_gate_opened')+'\n'
        region,count,tech=('crimea_region',3,7) if key=='crimea' else ('crimea_region',6,12) if key=='ural' else ('ural_region',6,17)
        triggers.append(block('rip_frontier_'+key+'_can_buy',f'''OR = {{ tag = CHR tag = HET tag = UKR }}
{previous}is_at_war = no
adm_tech = {tech}
treasury = {cash}
{resources}
num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with = {{ region = {region} value = {count} }}
rip_frontier_term_open = yes
rip_frontier_{key}_has_target = yes
OR = {{ ai = no rip_frontier_{key}_ai_budget = yes }}'''))
    result['common/scripted_triggers/rip_frontier_expedition_triggers.txt']='\n'.join(triggers)
    # Losing a base ENDS a timed benefit; it never resets its original expiry.
    cleanup=[]
    bonuses={
        'crimea': ('crimea_region',3,['ruthenian_eastward_mandate','ruthenian_frontier_organizers','ruthenian_raiding_columns','ruthenian_frontier_patrol_licenses','ruthenian_steppe_trade_licenses']),
        'ural': ('crimea_region',6,['ruthenian_ural_gate','ruthenian_ural_fortified_line','ruthenian_ural_trade_posts']),
        'manchuria': ('ural_region',6,['ruthenian_manchurian_push','ruthenian_manchurian_wardens','ruthenian_manchurian_companies']),
    }
    for key,(region,count,mods) in bonuses.items():
        hasbase=f'num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with = {{ region = {region} value = {count} }}'
        triggers.append(block('rip_frontier_'+key+'_base',f'OR = {{ tag = CHR tag = HET tag = UKR }}\n{hasbase}\nany_owned_province = {{ rip_frontier_capital_base = yes region = {region} }}'))
        removals='\n'.join('remove_country_modifier = '+m for m in mods)
        local='\nevery_owned_province = { remove_province_modifier = steppe_border_defense remove_province_modifier = zasechnaya_cherta_province }' if key=='crimea' else ''
        cleanup.append(f'if = {{ limit = {{ NOT = {{ rip_frontier_{key}_base = yes }} }}\n{removals}{local}\n}}')
    effects.append(block('rip_frontier_expedition_upkeep_effect','\n'.join(cleanup)))
    result['common/scripted_effects/rip_frontier_expedition_effects.txt']='\n'.join(effects)
    result['common/scripted_triggers/rip_frontier_expedition_triggers.txt']='\n'.join(triggers)
    result['common/on_actions/RIP_frontier_design_on_actions.txt']='\n'.join(block(hook,'rip_host_network_upkeep_effect = yes\nrip_frontier_expedition_upkeep_effect = yes') for hook in ('on_startup','on_monthly_pulse','on_reform_changed'))
    text={
        'rip_frontier_ai_reserve_tt':'After paying, retain one year of gross income; no loans or negative monthly balance.',
        'rip_frontier_batch_tt':'Up to five NEW normal claims in one connected frontier batch. The first target must border directly controlled land connected to the capital. Existing cores, claims and dependent-subject land are excluded. Shared ten-year term across all theatres. No payment without a target. Repeat purchases never renew initial benefits.',
        'rip_host_active_basis_tt':'Regional musters require the founded Host and its controlled territorial base. Two active bases give the United Cossack Hosts name. Lost bases suspend musters; founding dates and payments remain recorded.',
        'rip_frontier_crimea_purchase_title':'Commission an Eastern Frontier Expedition',
        'rip_frontier_ural_purchase_title':'Commission a Ural Frontier Expedition',
        'rip_frontier_manchuria_purchase_title':'Commission a Manchurian Frontier Expedition',
    }
    host_descriptions={
        'don':'Organize the Don Host on the controlled lower Don.',
        'danube':'Organize a Danube Host on our controlled lower-Danube frontier. This is territorial organization, not the exile route of the Transdanubian Sich.',
        'eastern':'Organize the Eastern Host on our controlled Circassian or Nogai frontier. The broad geographical condition does not claim an exact reconstruction of a Kuban institution.',
        'sloboda':'Organize the Sloboda Host in the controlled Sloboda Ukraine area.',
    }
    for key,opening in host_descriptions.items():
        rid='found_the_'+('danube_sich' if key=='danube' else key+'_host')
        text[rid+'_desc']=opening+' Pay 50 MIL once; the foundation grants 10 army tradition. The national Host package is shared, not multiplied by the number of Hosts. Local musters require state cores of the corresponding region. Loss or occupation of the regional base suspends benefits at the next monthly review; recovery never repeats the founding reward. '+text['rip_host_active_basis_tt']
    decision_ids={'crimea':'ruthenian_eastward_frontier_policy','ural':'ruthenian_open_ural_gate','manchuria':'ruthenian_manchurian_horizon'}
    for key,(_,cash,adm,dip,mil,*_) in THEATRES.items():
        price=', '.join([str(cash)+' ducats']+[str(n)+' '+p.upper() for p,n in [('adm',adm),('dip',dip),('mil',mil)] if n])
        text['rip_frontier_'+key+'_purchase_desc']='Pay '+price+'. '+text['rip_frontier_batch_tt']+' Highlighting shows possible starting provinces. Later picks extend the chosen batch; the province is not selected manually. Losing the territorial base ends project benefits without refund or renewal.'
        text[decision_ids[key]+'_title']=text.pop('rip_frontier_'+key+'_purchase_title')
        text[decision_ids[key]+'_desc']=text.pop('rip_frontier_'+key+'_purchase_desc')
    for lang in ('english','french','german','spanish'):
        result[f'localisation/rip_frontier_design_l_{lang}.yml']='\ufeffl_'+lang+':\n'+''.join(f' {k}:0 "{v}"\n' for k,v in sorted(text.items()))
    return result

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    stale=[]
    for name,body in outputs().items():
        if not name.startswith('localisation/'):
            body='# Generated by tools/build_frontier_design.py; edit the generator.\n'+body
        data=body.encode('utf-8'); path=ROOT/name
        if not path.exists() or path.read_bytes().replace(b'\r\n',b'\n')!=data:
            stale.append(name)
            if not args.check: path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    print(('STALE' if args.check and stale else 'GENERATED' if stale else 'CURRENT')+': agreed frontier design; '+str(len(stale))+' files')
    if args.check and stale: raise SystemExit(1)

if __name__=='__main__': main()
