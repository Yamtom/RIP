"""Native regional ordinances: one guarded transaction, explicit province targets."""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
CHECK = False

def emit(path, text, bom=False):
    data = text.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8-sig' if bom else 'utf-8')
    dest = ROOT / path
    if CHECK:
        assert dest.read_bytes() == data, f'Stale generated output: {path}'
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)

def block(name, body):
    return name+' = {\n'+'\n'.join('\t'+line for line in body.splitlines())+'\n}\n'

LANDS = {'chr':[289,1945,4543,290,2407,4542], 'uzh':[162,1952],
         'pdl':[281,1943,4540,1944], 'prl':[2407,290,4542,291],
         'ods':[282,1974,2406,283,2411,2412]}
GRAIN = [280,281,1942,1943,1944,4247,4540,290,2407,4542,289,1945,4543,291,298,299,2408,282,1974,2406,283,2411,2412]
REFORMS = {
 'chr':['siversk_veche_reform','chr_desna_staple_reform','chr_town_union_reform','chr_rada_of_lands_reform','chr_magistrat_rule_reform','chr_kanceliaryst_republic_reform'],
 'uzh':['uzh_palanok_captaincy_reform','uzh_komitat_system_reform','uzh_republican_komitat_system_reform'],
 'prl':['prl_ancient_principality_reform','prl_regimental_republic_reform'],
 'ods':['odesa_trade_republic_reform'],
 'pdl':['pdl_clan_assembly_reform','pdl_steppe_principality_reform','pdl_voivodeship_kingdom_reform','pdl_frontier_voivodeship_reform'],
}

def ids(values): return 'OR = { '+' '.join(f'province_id = {p}' for p in values)+' }'
def cm(name,days): return f'add_country_modifier = {{ name = {name} duration = {days} }}'
def pm(name,days): return f'add_province_modifier = {{ name = {name} duration = {days} }}'
def mood(estate,n): return f'rip_estate_mood_effect = {{ ESTATE = estate_{estate} LOYALTY = {n} }}'

def generate():
    loc={'rip_rg_cancel':'Leave the Matter Unchanged','rip_rg_next':'Inspect the Next Lands',
         'rip_rg_previous':'Return to the Previous Lands','rip_rg_confirm':'Confirm the Ordinance',
         'rip_rg_select_desc':'Choose the exact land. Nothing is charged until confirmation. The final order checks ownership, control, government, resources and the shared term again.',
         'rip_rg_confirm_desc':'Target: §Y[event_target:rip_rg_target.GetName]§!. The option tooltip lists the complete payment and effects. Cancellation is free. An order already in force closes every other ordinance of this institution.',
         'rip_rg_term_tt':'This institution has no order serving its shared term. Hover the active country modifier for its expiry date.',
         'rip_rg_grain_req_tt':'At least 10 development in controlled regional grain lands.',
         'rip_rg_second':'Extend the Order to Another Town',
         'rip_rg_second_desc':'The Town Union may extend the order to one different town for 25 power. Neither the national effect nor the shared term is renewed. Declining is free.'}
    triggers=[]; effects=[]; events=['namespace = rip_rg']; mods={}; mechanics=[]; decisions=[]; actions=[]
    def modifier(key,name,payload,desc):
        mods[key]=payload; loc[key]=name; loc['desc_'+key]=desc
    for f in LANDS:
        gate='OR = { '+' '.join('has_reform = '+r for r in REFORMS[f])+' }'
        if f in ('chr','ods'): gate='government = republic\n'+gate
        if f=='uzh': gate='NOT = { government = theocracy }\n'+gate
        if f=='pdl': gate='west_ukraine_pdl_origin_country = yes\nOR = { has_country_flag = pdl_frontier_path has_country_flag = pdl_carpathian_path has_country_flag = pdl_magnate_path }'
        triggers.append(block('rip_rg_'+f,gate))
        triggers.append(block('rip_rg_'+f+'_land',ids(LANDS[f])+'\nis_city = yes'))
    triggers.append(block('rip_rg_fort','OR = { has_building = fort_15th has_building = fort_16th has_building = fort_17th has_building = fort_18th }'))
    triggers.append(block('rip_rg_port','rip_rg_ods_land = yes\nis_port = yes\nowned_by = ROOT\ncontrolled_by = ROOT\nis_blockaded = no'))
    for f in ['chr','uzh','ods']:
        modifier(f'rip_rg_{f}_term',f'{f.upper()} Shared Ordinance Term','',f'All orders of this institution remain closed until the displayed expiry date. Reform changes never refund the {10 if f=="chr" else 5}-year term.')
    definitions=[
     ('chr_bell','Veche Municipal Judges','local_unrest = -2','Town judges and militia keep order for five years.'),
     ('chr_debate','Veche Deliberations','yearly_corruption = -0.05\nstability_cost_modifier = 0.10','Audits reduce national corruption; competing petitions raise the cost of stability.'),
     ('chr_magistrat','Magistrat Deliberations','yearly_corruption = -0.05\nstability_cost_modifier = 0.05','Magistrat procedure halves the stability burden.'),
     ('chr_staple','Desna Staple Right','local_trade_power_modifier = 0.15','The landing place gains local trade power, not a multiplier to all national power in the node.'),
     ('chr_militia','Guild Militia','local_defensiveness = 0.20\nlocal_production_efficiency = -0.10','Guild workers man the walls at the expense of their workshops.'),
     ('chr_reinforce','Municipal Muster Rolls','reinforce_cost_modifier = -0.10','Reinforcements cost less for the entire army, not only infantry.'),
     ('uzh_salt','Maramorosh Salt Regalia','local_goods_produced_modifier = 0.15\nlocal_trade_power_modifier = 0.10\nlocal_unrest = 2','Monopoly output and customs grow, provoking unrest.'),
     ('uzh_guides','Highland Guides Compact','local_hostile_attrition = 1','The guides prepare local ambushes in return for ten points of autonomy.'),
     ('uzh_supply','Highland Supply Guides','land_attrition = -0.10','The entire army receives supply advice, including outside the mountains.'),
     ('uzh_pass','Carpathian Pass Works','local_defensiveness = 0.20\nlocal_fort_maintenance_modifier = -0.15\nlocal_production_efficiency = -0.10','Castle works improve the walls and upkeep but consume workshop labour.'),
     ('border_patrol','Frontier Watch Patrols','local_hostile_attrition = 1','Patrols protect this land; they do not cancel every scripted raid.'),
     ('border_fort','Carpathian Watch','local_defensiveness = 0.15','The watch reinforces an existing fort.'),
     ('border_charter','Frontier Town Charter','local_production_efficiency = 0.15','Workshops gain rights in exchange for local autonomy.'),
     ('border_magnate','Magnate Town Charter','local_production_efficiency = 0.20','Magnate sponsorship costs fifteen autonomy points.'),
     ('border_mobile','Mobile Frontier Defense','cavalry_power = 0.10\nland_maintenance_modifier = 0.05','Cavalry combat ability is national; the entire army costs more to maintain.'),
     ('ods_corsairs','Black Sea Corsair Charter','privateer_efficiency = 0.15\ntrade_efficiency = -0.10','Ordinary privateer missions improve at the expense of lawful trade. Ships and missions are still assigned by the player.'),
     ('ods_export','Black Sea Grain Freight Contract','','The contract lasts five years. Its separately displayed efficiency bonus is recalculated monthly and pauses without a controlled unblocked port or grain base.')]
    for k,n,p,d in definitions: modifier('rip_rg_'+k,n,p,d)
    for n in range(2,11): modifier(f'rip_rg_ods_grain_{n}',f'Grain Freight: {n}% Efficiency',f'trade_efficiency = {n/100:.2f}',f'The controlled regional grain base supports {n}% national trade efficiency. Updated monthly; this is not a direct treasury payment.')
    def action(key,f,title,cost,target,payload,national='',extra='',ai='factor = 1',second=False):
        actions.append(dict(key=key,f=f,title=title,cost=cost,target=target,payload=payload,national=national,extra=extra,ai=ai,second=second))
    action('chr_bell','chr','Ring the Veche Bell',{'adm':50},'', 'add_nationalism = -3\n'+pm('rip_rg_chr_bell',1825),
           'if = { limit = { has_reform = chr_magistrat_rule_reform } '+cm('rip_rg_chr_magistrat',1825)+' } else = { '+cm('rip_rg_chr_debate',1825)+' }',ai='factor = 1 modifier = { factor = 5 corruption = 2 }',second=True)
    action('chr_staple','chr','Grant the Desna Staple Right',{'dip':50},'', 'add_local_autonomy = 5\n'+pm('rip_rg_chr_staple',3650),ai='factor = 1 modifier = { factor = 3 is_at_war = no }')
    action('chr_militia','chr','Muster the Guild Militia',{'mil':50},'rip_rg_fort = yes',pm('rip_rg_chr_militia',1825),cm('rip_rg_chr_reinforce',1095),ai='factor = 1 modifier = { factor = 6 is_at_war = yes } modifier = { factor = 0 NOT = { mil_power = 150 } }',second=True)
    action('uzh_salt','uzh','Exercise the Salt Regalia',{'dip':50},'trade_goods = salt',pm('rip_rg_uzh_salt',1825),ai='factor = 1 modifier = { factor = 3 is_at_war = no }')
    action('uzh_guides','uzh','Contract the Highland Guides',{'mil':50,'ducats':30},'OR = { has_terrain = mountains has_terrain = hills has_terrain = highlands }','add_local_autonomy = 10\n'+pm('rip_rg_uzh_guides',1825),cm('rip_rg_uzh_supply',1825)+'\n'+mood('nobles',-5),ai='factor = 1 modifier = { factor = 5 is_at_war = yes }')
    action('uzh_pass','uzh','Fortify the Carpathian Pass',{'adm':50,'ducats':50},'rip_rg_fort = yes',pm('rip_rg_uzh_pass',1825),ai='factor = 1 modifier = { factor = 5 is_at_war = yes }')
    for f in ['pdl','prl']:
        for v,condition,mil,gold,devastation,mod in [
          ('base','NOT = { has_country_flag = pdl_frontier_path } NOT = { has_country_flag = pdl_carpathian_path }' if f=='pdl' else '',35,40,10,'border_patrol'),
          ('frontier','has_country_flag = pdl_frontier_path',25,30,15,'border_patrol'),
          ('carpathian','has_country_flag = pdl_carpathian_path',35,60,10,'border_fort')]:
            if f=='prl' and v!='base': continue
            action(f'{f}_patrol_{v}',f,'Send the Watch Patrols',{'mil':mil,'ducats':gold},'rip_rg_fort = yes' if v=='carpathian' else '',f'add_devastation = -{devastation}\n'+pm('rip_rg_'+mod,1825),'add_army_tradition = 3',condition,'factor = 1 modifier = { factor = 4 any_owned_province = { devastation = 10 } }')
        for v in (['base','magnate'] if f=='pdl' else ['base']):
            m=v=='magnate'
            action(f'{f}_charter_{v}',f,'Grant the Kamianets Town Statute' if f=='pdl' else 'Charter the Frontier Towns',{'adm':35 if m else 50,'ducats':30},'',f'add_local_autonomy = {15 if m else 10}\n'+pm('rip_rg_border_magnate' if m else 'rip_rg_border_charter',1825),mood('burghers',5)+ ('\n'+mood('nobles',5) if m else ''),('has_country_flag = pdl_magnate_path' if m else 'NOT = { has_country_flag = pdl_magnate_path }') if f=='pdl' else '',ai='factor = 2 modifier = { factor = 3 is_at_war = no }')
        for v in (['base','frontier','carpathian'] if f=='pdl' else ['base']):
            condition={'base':'NOT = { has_country_flag = pdl_frontier_path } NOT = { has_country_flag = pdl_carpathian_path }','frontier':'has_country_flag = pdl_frontier_path','carpathian':'has_country_flag = pdl_carpathian_path'}[v] if f=='pdl' else ''
            estate=('if = { limit = { has_reform = prl_regimental_republic_reform has_estate = estate_cossacks } '+mood('cossacks',5)+' } else = { '+mood('nobles',5)+' }') if f=='prl' else mood('nobles',5)
            action(f'{f}_mobile_{v}',f,'Muster the Mobile Defense',{'mil':35 if v=='frontier' else 50,'ducats':75 if v=='carpathian' else 50,**({'manpower':1} if v=='frontier' else {})},'', '',cm('rip_rg_border_mobile',1095)+'\n'+estate,condition,'factor = 1 modifier = { factor = 5 is_at_war = yes }')
    action('ods_freight','ods','Charter Mediterranean Freight',{'dip':50,'ducats':30},'rip_rg_port = yes','',cm('rip_rg_ods_export',1825)+'\nrip_rg_grain_refresh_effect = yes',extra='is_at_war = no\nnum_of_light_ship = 3',ai='factor = 3 modifier = { factor = 0 is_at_war = yes }')
    action('ods_corsairs','ods','Outfit Black Sea Corsairs',{'mil':50,'ducats':50},'rip_rg_port = yes','',cm('rip_rg_ods_corsairs',1825),extra='num_of_light_ship = 3\nOR = { has_dlc = "Wealth of Nations" has_dlc = "El Dorado" }',ai='factor = 1 modifier = { factor = 4 is_at_war = yes }')

    for i,a in enumerate(actions):
        k=a['key']; f=a['f']; start=100+i*20; years=10 if f=='chr' else 5
        term='pdl_recent_border_policy' if f in ('pdl','prl') else f'rip_rg_{f}_term'
        guard=f'rip_rg_{f} = yes\n{a["extra"]}\ncustom_trigger_tooltip = {{ tooltip = rip_rg_term_tt NOT = {{ has_country_modifier = {term} }} }}'
        for c,n in a['cost'].items(): guard+='\n'+{'ducats':'treasury','manpower':'manpower'}.get(c,c+'_power')+f' = {n}'
        target=f'owned_by = ROOT\ncontrolled_by = ROOT\nrip_rg_{f}_land = yes\n'+a['target']
        triggers += [block(f'rip_rg_{k}_target',target),block(f'rip_rg_{k}_can',guard)]
        loc[f'rip_rg_{k}']=a['title']; loc[f'rip_rg_{k}.t']=a['title']
        costs=', '.join(f'{n} '+{'adm':'ADM','dip':'DIP','mil':'MIL','ducats':'ducats','manpower':'thousand manpower'}[c] for c,n in a['cost'].items())
        loc[f'rip_rg_{k}_desc']=f'Choose a target; pay {costs} only on confirmation. Shared term: {years} years. Active country and province modifiers show expiry dates. Reform changes never refund the term.'
        modifier(f'rip_rg_{k}_active',a['title']+': Order in Force','',f'This order occupies the shared {years}-year term. Its chosen land carries the local effect. Shorter effects can expire before the shared term.')
        payment='\n'.join(f'{ {"ducats":"add_treasury","manpower":"add_manpower"}.get(c,"add_"+c+"_power")} = -{n}' for c,n in a['cost'].items())
        execute=payment+'\nset_country_flag = rip_rg_used\n'+cm(term,years*365)+'\n'+cm(f'rip_rg_{k}_active',years*365)+'\nevent_target:rip_rg_target = {\n'+a['payload']+'\n}\n'+a['national']
        if a['second']: execute+=f'\nclr_country_flag = rip_rg_{k}_second_done\nset_country_flag = rip_rg_{k}_issued\nif = {{ limit = {{ has_reform = chr_town_union_reform }} country_event = {{ id = rip_rg.{start+11} }} }}'
        if k=='ods_freight': execute+='\ncountry_event = { id = rip_rg.900 days = 1825 }'
        grain_guard='custom_trigger_tooltip = { tooltip = rip_rg_grain_req_tt check_variable = { which = rip_rg_grain_dev value = 10 } }' if k=='ods_freight' else ''
        effects.append(block(f'rip_rg_{k}_commit_effect',('rip_rg_grain_census_effect = yes\n' if k=='ods_freight' else '')+f'if = {{\nlimit = {{ rip_rg_{k}_can = yes {grain_guard} event_target:rip_rg_target = {{ rip_rg_{k}_target = yes }} }}\n'+execute+'\n}'))
        for page in range((len(LANDS[f])+3)//4):
            body=f'id = rip_rg.{start+page}\ntitle = rip_rg_{k}.t\ndesc = rip_rg_select_desc\npicture = COURT_eventPicture\nis_triggered_only = yes\n'
            for p in LANDS[f][page*4:page*4+4]:
                loc[f'rip_rg_province_{p}']=f'[{p}.GetName]'
                body+=block('option',f'name = rip_rg_province_{p}\ntrigger = {{ {p} = {{ rip_rg_{k}_target = yes }} }}\n{p} = {{ save_event_target_as = rip_rg_target }}\ncountry_event = {{ id = rip_rg.{start+10} }}\nai_chance = {{ factor = 1 }}')
            if page: body+=block('option',f'name = rip_rg_previous\ncountry_event = {{ id = rip_rg.{start+page-1} }}\nai_chance = {{ factor = 0 }}')
            if (page+1)*4<len(LANDS[f]): body+=block('option',f'name = rip_rg_next\ncountry_event = {{ id = rip_rg.{start+page+1} }}\nai_chance = {{ factor = 0 }}')
            body+=block('option','name = rip_rg_cancel\nai_chance = { factor = 0 }')
            events.append(block('country_event',body))
        events.append(block('country_event',f'id = rip_rg.{start+10}\ntitle = rip_rg_{k}.t\ndesc = rip_rg_confirm_desc\npicture = COURT_eventPicture\nis_triggered_only = yes\n'+('immediate = { rip_rg_grain_census_effect = yes }\n' if k=='ods_freight' else '')+block('option',f'name = rip_rg_confirm\ntrigger = {{ rip_rg_{k}_can = yes {grain_guard} event_target:rip_rg_target = {{ rip_rg_{k}_target = yes }} }}\nrip_rg_{k}_commit_effect = yes\nai_chance = {{ factor = 1 }}')+block('option','name = rip_rg_cancel\nai_chance = { factor = 0 }')))
        if a['second']:
            c=next(iter(a['cost'])); body=f'id = rip_rg.{start+11}\ntitle = rip_rg_second\ndesc = rip_rg_second_desc\npicture = COURT_eventPicture\nis_triggered_only = yes\n'
            for p in LANDS[f]:
                condition=f'rip_rg_chr = yes has_reform = chr_town_union_reform {c}_power = 25 has_country_modifier = rip_rg_{k}_active NOT = {{ had_country_flag = {{ flag = rip_rg_{k}_issued days = 1 }} }} NOT = {{ has_country_flag = rip_rg_{k}_second_done }} {p} = {{ rip_rg_{k}_target = yes NOT = {{ has_province_modifier = rip_rg_{k} }} }}'
                body+=block('option',f'name = rip_rg_province_{p}\ntrigger = {{ {condition} }}\nif = {{ limit = {{ {condition} }} add_{c}_power = -25 set_country_flag = rip_rg_{k}_second_done {p} = {{ {a["payload"]} }} }}\nai_chance = {{ factor = 1 }}')
            body+=block('option','name = rip_rg_cancel\nai_chance = { factor = 1 }'); events.append(block('country_event',body))
        a['start']=start
        launch=f'if = {{ limit = {{ ai = yes }} random_owned_province = {{ limit = {{ rip_rg_{k}_target = yes }} save_event_target_as = rip_rg_target }} rip_rg_{k}_commit_effect = yes }}\nelse = {{ country_event = {{ id = rip_rg.{start} }} }}'
        a['launch']=launch
        icon='GFX_rip_siversk_towns' if f=='chr' else 'GFX_rip_siversk_retinue'
        a['icon']=icon
        a['guard']=f'rip_rg_{k}_can = yes any_owned_province = {{ rip_rg_{k}_target = yes }}'
    # Three physical buttons per frontier government, not one button per price.
    for f in LANDS:
        groups={}
        for a in actions:
            if a['f']==f:
                group='_'.join(a['key'].split('_')[:2]) if f in ('pdl','prl') else a['key']
                groups.setdefault(group,[]).append(a)
        interactions=[]
        for group, variants in groups.items():
            first=variants[0]
            guard='OR = { '+' '.join('AND = { '+a['guard']+' }' for a in variants)+' }'
            launch='\n'.join(('if' if j==0 else 'else_if')+' = { limit = { '+a['guard']+' } '+a['launch']+' }' for j,a in enumerate(variants))
            interactions.append(block('rip_rg_'+group,f'icon = {first["icon"]}\ntrigger = {{ {guard} }}\neffect = {{ {launch} }}\nai_chance = {{ {first["ai"]} }}'))
            highlight='OR = { '+' '.join('rip_rg_'+a['key']+'_target = yes' for a in variants)+' }'
            decisions.append(block('rip_rg_'+group+'_decision',f'potential = {{ rip_rg_{f} = yes }}\nallow = {{ {guard} }}\nprovinces_to_highlight = {{ {highlight} }}\neffect = {{ {launch} }}\nai_will_do = {{ factor = 0 }}'))
            loc['rip_rg_'+group]=first['title']; loc['rip_rg_'+group+'_desc']=loc['rip_rg_'+first['key']+'_desc']+(' The Podillian path changes the final price; inspect the confirmation tooltip.' if len(variants)>1 else '')
            loc['rip_rg_'+group+'_decision_title']=first['title']; loc['rip_rg_'+group+'_decision_desc']=loc['rip_rg_'+group+'_desc']
        mechanics.append(block('rip_rg_'+f+'_mechanic',f'alert_icon_gfx = GFX_alerticons_government_mechanics\nalert_icon_index = 1\navailable = {{ rip_rg_{f} = yes }}\n'+block('interactions','\n'.join(interactions))))
    for f in LANDS:
        loc['ability_rip_rg_'+f+'_mechanic']={'chr':'Desna River Confederation','uzh':'Carpathian Border Captaincy','pdl':'Podillian Starosta Watch','prl':'Pereiaslav Frontier Watch','ods':'Black Sea Grain Emporium'}[f]
    old_pdl='id = pdl_border_policy.1\ntitle = pdl_border_policy.1.t\ndesc = pdl_border_policy.1.desc\npicture = BORDER_TENSION_eventPicture\nis_triggered_only = yes\n'
    for group,label in [('patrol','a'),('charter','b'),('mobile','c')]:
        variants=[a for a in actions if a['key'].startswith('pdl_'+group+'_')]
        guard='OR = { '+' '.join('AND = { '+a['guard']+' }' for a in variants)+' }'
        launch='\n'.join(('if' if j==0 else 'else_if')+' = { limit = { '+a['guard']+' } '+a['launch']+' }' for j,a in enumerate(variants))
        old_pdl+=block('option',f'name = pdl_border_policy.1.{label}\ntrigger = {{ {guard} }}\n{launch}\nai_chance = {{ factor = 1 }}')
        loc[f'pdl_border_policy.1.{label}']=variants[0]['title']
    old_pdl+=block('option','name = rip_rg_cancel\nai_chance = { factor = 0 }')
    loc['pdl_border_policy.1.desc']='The starosta can commission patrols, charter a town or muster mounted banners. Each order uses the existing five-year border-policy term. Inspect the exact land and price before confirming.'
    emit('events/PodilliaBorderPolicy.txt','namespace = pdl_border_policy\n\n# Generated by tools/build_regional_governments.py; old entry point, one payment.\n'+block('country_event',old_pdl))
    events.append(block('country_event','id = rip_rg.900\nhidden = yes\nis_triggered_only = yes\nimmediate = { rip_rg_grain_refresh_effect = yes }'))
    localmods=[k for k,v in mods.items() if 'local_' in v]
    effects.append(block('rip_rg_province_transfer_effect','\n'.join('remove_province_modifier = '+k for k in localmods)))
    cleanup=[]
    for f in LANDS:
        selected=[a for a in actions if a['f']==f]
        countrymods=set(); provincemods=set()
        for a in selected:
            countrymods.update(re.findall(r'add_country_modifier = \{ name = (\w+)',a['national']))
            provincemods.update(re.findall(r'add_province_modifier = \{ name = (\w+)',a['payload']))
        condition='NOT = { OR = { rip_rg_pdl = yes rip_rg_prl = yes } }' if f in ('pdl','prl') else f'NOT = {{ rip_rg_{f} = yes }}'
        body='\n'.join('remove_country_modifier = '+k for k in sorted(countrymods))
        body+='\nevery_owned_province = { '+' '.join('remove_province_modifier = '+k for k in sorted(provincemods))+' }'
        cleanup.append('if = { limit = { '+condition+' } '+body+' }')
    effects.append(block('rip_rg_cleanup_effect','if = { limit = { has_country_flag = rip_rg_used }\n'+'\n'.join(cleanup)+'\n}'))
    effects.append(block('rip_rg_grain_census_effect','set_variable = { which = rip_rg_grain_dev value = 0 }\nevery_owned_province = { limit = { '+ids(GRAIN)+' controlled_by = ROOT trade_goods = grain } owner = { export_to_variable = { which = rip_rg_grain_piece value = development who = PREV } change_variable = { which = rip_rg_grain_dev which = rip_rg_grain_piece } } }'))
    refresh='\n'.join(f'remove_country_modifier = rip_rg_ods_grain_{n}' for n in range(2,11))
    refresh+='\nif = { limit = { rip_rg_ods = yes has_country_modifier = rip_rg_ods_export any_owned_province = { rip_rg_port = yes } } rip_rg_grain_census_effect = yes\n'
    for n in range(10,1,-1): refresh+=('if' if n==10 else 'else_if')+f' = {{ limit = {{ check_variable = {{ which = rip_rg_grain_dev value = {n*5} }} }} '+cm(f'rip_rg_ods_grain_{n}',35)+' }\n'
    effects.append(block('rip_rg_grain_refresh_effect',refresh+'}'))
    emit('common/scripted_triggers/rip_regional_government_triggers.txt','\n'.join(triggers))
    emit('common/scripted_effects/rip_regional_government_effects.txt','\n'.join(effects))
    emit('common/event_modifiers/rip_regional_government_modifiers.txt','\n'.join(block(k,v) for k,v in mods.items()))
    emit('common/government_mechanics/rip_regional_governments.txt','\n'.join(mechanics))
    emit('events/RIP_RegionalGovernments.txt','\n'.join(events))
    emit('decisions/RIP_RegionalGovernments.txt',block('country_decisions','\n'.join(decisions)))
    for language in ['english','french','german','spanish']:
        emit(f'localisation/zzz_rip_regional_governments_l_{language}.yml',f'l_{language}:\n'+'\n'.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"' for k,v in loc.items())+'\n',True)
    emit('common/on_actions/RIP_shared_regional_government_on_actions.txt', '''# Generated by tools/build_regional_governments.py; edit its hook template.
# RIP - shared regional government.
on_startup = {
	rip_rg_cleanup_effect = yes
	rip_rg_grain_refresh_effect = yes
}

on_monthly_pulse = {
	rip_rg_cleanup_effect = yes
	if = {
		limit = {
			has_country_modifier = rip_rg_ods_export
		}
		rip_rg_grain_refresh_effect = yes
	}
}

on_reform_changed = {
	rip_rg_cleanup_effect = yes
	rip_rg_grain_refresh_effect = yes
}

on_province_owner_change = {
	rip_rg_province_transfer_effect = yes
}
''')
    return actions

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--check',action='store_true')
    CHECK=parser.parse_args().check; generate()
    print('Regional government outputs verified' if CHECK else 'Regional government outputs generated')
