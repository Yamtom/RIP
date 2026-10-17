"""Build read-only government explanations from native EU4 custom GUI contracts.
Uses the installed 1.37 government window; --check verifies deterministic output.
"""
from pathlib import Path
import argparse, os
ROOT = Path(__file__).resolve().parents[1]
GAME = Path(os.environ.get('EU4_DIR', 'D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV'))
LOC = {}
DYNAMIC = []
CONTROLS = []

def loc(key, value):
    LOC[key] = value
    return key

def choice(name, branches, fallback='None'):
    lines = ['defined_text = {', f' name = {name}', ' random = no']
    for i, (trigger, value) in enumerate(branches + [('always = yes', fallback)]):
        key = loc(f'rip_gov_{name}_{i}', value)
        lines.append(f' text = {{ trigger = {{ {trigger} }} localisation_key = {key} }}')
    DYNAMIC.append('\n'.join(lines + ['}']))
    return f'[Root.{name}]'

def factor(name, trigger, value, label):
    active = ('§G' if value < 0 else '§R') + f'{value:+g}§!'
    # For concord and integration, increasing values are beneficial.
    if name.startswith('Cesar'):
        active = ('§G' if value > 0 else '§R') + f'{value:+g}§!'
    return choice(name, [(trigger, active)], '0') + ' ' + label

def row(name, y, text, tip, height=22):
    loc(name, text)
    loc(name + '_tt', tip)
    CONTROLS.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{ name = "{name}" scripted = yes position = {{ x=18 y={y} }} font = "vic_18" text = "{name}" maxWidth = 434 maxHeight = {height} format = left }}'''

def panel(name, potential, rows):
    CONTROLS.append(f'custom_window = {{ name = {name} potential = {{ {potential} }} }}')
    return f'''windowType = {{ name = "{name}" scripted = yes position = {{ x=550 y=72 }} size = {{ x=470 y=290 }} moveable = 0
 iconType = {{ name = "background" spriteType = "GFX_rip_government_status_bg" position = {{ x=0 y=0 }} }}
 {chr(10).join(rows)}
}}'''

factions = [('knyazi', 'Knyazi'), ('boyary', 'Boyars'), ('starshyna', 'Starshyna')]
active = 'has_country_flag = kru_factional_dominance_active'
dominant = choice('RipGovDominant', [(f'{active} has_country_flag = kru_current_dominant_{f}', n) for f,n in factions], 'No bloc at 60')
partner = choice('RipGovPartner', [(f'{active} has_country_flag = kru_previous_dominant_{f}', n) for f,n in factions], 'No coalition')
voice = choice('RipGovJuniorVoice', [(f'has_country_modifier = KRU_junior_{f}', n) for f,n in factions], 'None')
opposition = choice('RipGovOpposition', [(f'{active} NOT = {{ has_country_flag = kru_current_dominant_{f} }} NOT = {{ has_country_flag = kru_previous_dominant_{f} }}', n) for f,n in factions], 'No coalition')
coalition_tip = 'The leading faction must have at least 60 influence to dominate. Its partner is the PREVIOUS dominant faction, not the runner-up. The third faction is the opposition. The partner receives a junior-voice modifier only at 38 influence or more.\nOn the first recorded dominance, the default partner is Boyars for Knyazi, and Knyazi for Boyars or Starshyna. Below 60 there is no coalition or junior voice; the States General scale returns to centre. The remembered previous dominant faction is retained.\nThe record refreshes monthly and after courting a faction. States General requires Res Publica or Winds of Change.'
annual = [
 ('StabZero','stability = 0 NOT = { stability = 1 }',2,'stability = 0'),
 ('StabBad','NOT = { stability = 0 }',3,'stability < 0'),
 ('War','is_at_war = yes',1,'at war'),
 ('Loans','num_of_loans = 5',1,'at least 5 loans'),
 ('Autonomy','average_autonomy = 40',1,'average autonomy at least 40%'),
 ('Legitimacy','NOT = { legitimacy = 50 }',1,'legitimacy below 50'),
 ('StabGood','stability = 2',-3,'stability at least +2'),
 ('Peace','is_at_war = no',-2,'at peace')]
annual_text = '\n'.join(factor('RipGov'+n,t,v,l) for n,t,v,l in annual)
annual_tip = 'Current conditions for the next yearly pulse; coloured values are active, 0 means inactive. Add these values together. Events can change Decadence separately; this is not a forecast of intervening events.\n' + annual_text + '\nOn the first yearly update, an uninitialised zero starts at 20 before these changes. Annual modifiers: below 40 / 40-69 / at least 70.'
crisis_tip = 'Court Crisis can start accumulating for KRU with this reform, no other disaster, and Decadence at least 90. Base monthly progress at 90+: +6; frontier centralisation +1.5, frontier liberties -1, southern recovery -1. Progress recedes below 75. An active crisis ends only when Decadence is below 60 AND stability is at least +1.\nThe first annual crossing of 90 can also trigger a separate court event; its choices reduce Decadence. A threshold does not mean the disaster starts immediately.'
kru_rows = [row('rip_gov_kru_title',12,'§YRada and Decadence§!',coalition_tip), row('rip_gov_kru_leader',40,'Dominant: '+dominant,coalition_tip),row('rip_gov_kru_partner',64,'Partner: '+partner,coalition_tip),row('rip_gov_kru_opposition',88,'Opposition: '+opposition,coalition_tip),row('rip_gov_kru_voice',112,'Junior voice: '+voice,coalition_tip), row('rip_gov_kru_decay',146,'Decadence: §Y[Root.ruthenian_decadence.GetValue]§!',annual_tip),row('rip_gov_kru_annual',174,'Yearly change: hover for active factors',annual_tip),row('rip_gov_kru_crisis',202,'Crisis: 90+ | Retreat: <75 | End: <60, stability +1',crisis_tip),row('rip_gov_kru_memory',236,'Partner follows the previous dominance.',coalition_tip)]
kru_potential = 'tag = KRU OR = { has_reform = ruthenian_factional_empire_reform has_reform = ruthenian_factional_empire_princes_hetmans_reform has_reform = ruthenian_factional_empire_boyars_hetmans_reform }'

def share(var, name):
    return choice(name, [(f'check_variable = {{ which = {var} value = {i/100:g} }}', f'{i}%') for i in range(100,0,-1)], '0%')
minority = share('rip_cesar_minority_share', 'RipGovMinorityShare')
excluded = share('rip_cesar_excluded_share', 'RipGovExcludedShare')
eligible = choice('RipGovIntegration', [('rip_cesar_integration_eligible = yes','§GEligible§!')], '§RNot eligible§!')
breakdown = choice('RipGovBreakdown', [('has_country_flag = rip_cesar_breakdown','§RBreakdown active§!')], 'No active breakdown')
lands_tip = 'Shares use total development of ALL owned provinces, including territories; subjects are excluded. The census updates monthly. Displayed whole percentages are rounded down; thresholds use the exact share.\nNon-primary: provinces whose culture differs from the owner\'s primary culture. Unaccepted: the subset of those provinces for which the engine reports no owner-accepted culture. Accepted same-group cultures therefore follow the engine\'s cultural-union rules.\nConquest, development, province loss, culture conversion and changes in accepted or primary culture alter these shares at the next census. Promoting a culture can reduce the unaccepted share without reducing the non-primary share.'
elig_tip = 'Integration requires ALL three: at least one owned non-primary province with an owner-accepted culture; at least one accepted culture; non-primary development at least 10%. A cultural union alone does not waive the accepted-culture requirement.\nThree accepted cultures add growth only while these requirements hold. Development matters, not the number of provinces.'
power = lambda p,v: f'has_government_power = {{ mechanic_type = {p}_mechanic power_type = {p} value = {v} }}'
concord = 'kyivan_throne_concord'; gathering = 'kyivan_peoples_gathering'
concord_factors = [('Stable','stability = 2',.1,'stability at least +2'),('Unstable','NOT = { stability = 0 }',-.2,'negative stability'),('Legit','legitimacy = 80',.2,'legitimacy at least 80'),('Illegit','NOT = { legitimacy = 40 }',-.25,'legitimacy below 40'),('Subjects','any_subject_country = { liberty_desire = 50 }',-.3,'any subject at 50% liberty desire'),('Compact',power(gathering,60)+' rip_cesar_integration_eligible = yes',.15,'Gathering at least 60 and integration eligible'),('Excluded','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.3,'unaccepted share at least 30%')]
gather_factors = [('Eligible','rip_cesar_integration_eligible = yes',.3,'integration eligible'),('Cultures','rip_cesar_integration_eligible = yes num_accepted_cultures = 3',.15,'eligible and at least 3 accepted cultures'),('Minority','rip_cesar_integration_eligible = yes check_variable = { which = rip_cesar_minority_share value = 0.3 }',.15,'eligible and non-primary share at least 30%'),('Throne','rip_cesar_integration_eligible = yes '+power(concord,60),.1,'eligible and Concord at least 60'),('Excluded15','check_variable = { which = rip_cesar_excluded_share value = 0.15 }',-.25,'unaccepted share at least 15%'),('Excluded30','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.35,'unaccepted share at least 30% (stacks with 15%)'),('WeakThrone','NOT = { '+power(concord,30)+' }',-.2,'Concord below 30'),('Exhausted','war_exhaustion = 5',-.15,'war exhaustion at least 5'),('Ineligible','NOT = { rip_cesar_integration_eligible = yes }',-.5,'integration not eligible')]
concord_tip = 'Monthly Concord: base +0.10, plus active values below.\n'+'\n'.join(factor('CesarConcord'+n,t,v,l) for n,t,v,l in concord_factors)+'\nAt zero Concord, Throne in Disarray lasts 1825 days.'
gather_tip = 'Monthly Gathering: base 0, plus active values below.\n'+'\n'.join(factor('CesarGather'+n,t,v,l) for n,t,v,l in gather_factors)+'\nAt 100: a 3650-day compact, +10 prestige and +10 Concord; Gathering resets to 40. This reset is not a breakdown.'
recovery_tip = 'Monthly breakdown check: unaccepted development at least 30% AND Gathering below 20. Once per breakdown: -15 Concord and Throne in Disarray for 1825 days.\nRecovery requires unaccepted development strictly below 15% AND Gathering at least 40. It clears the breakdown flag; the timed Throne in Disarray modifier remains until expiry. Falling to zero Concord can also apply that modifier.'
cesar_rows = [row('rip_gov_cesar_title',12,'§YCesarstvo: Lands and Settlement§!',lands_tip),row('rip_gov_cesar_minority',44,'Non-primary development: ~'+minority,lands_tip),row('rip_gov_cesar_excluded',72,'Unaccepted development: ~'+excluded,lands_tip),row('rip_gov_cesar_eligible',104,'Integration: '+eligible,elig_tip),row('rip_gov_cesar_concord',136,'Throne Concord: monthly factors',concord_tip),row('rip_gov_cesar_gather',164,'Gathering: monthly factors',gather_tip),row('rip_gov_cesar_breakdown',198,breakdown,recovery_tip),row('rip_gov_cesar_recovery',230,'Crisis and recovery: hover for thresholds',recovery_tip)]

# Insert within the native supported root window, after its existing widgets.
def close_brace(text, start):
    depth = 0
    for i in range(start,len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
    raise ValueError('Unclosed native window')

native = (GAME/'interface/countrygovernmentview.gui').read_text(encoding='utf-8-sig')
pos = native.index('name = "countrygovernmentview"')
start = native.rfind('{',0,pos)
end = close_brace(native,start)
gui = native[:end] + '\n# Generated read-only RIP government explanations.\n' + panel('rip_gov_kru_panel',kru_potential,kru_rows) + '\n' + panel('rip_gov_cesar_panel','has_reform = kyivan_cesarstvo_reform',cesar_rows) + '\n' + native[end:]
outputs = {'interface/rip_government_status.gfx': 'spriteTypes = { corneredTileSpriteType = { name = GFX_rip_government_status_bg size = { x = 470 y = 290 } texturefile = '+chr(34)+'gfx/interface/small_tiles_dialog.dds'+chr(34)+' borderSize = { x = 8 y = 8 } } }\n', 'interface/countrygovernmentview.gui': gui, 'common/custom_gui/rip_government_status.txt':'\n'.join(CONTROLS)+'\n', 'customizable_localization/rip_government_status.txt':'\n'.join(DYNAMIC)+'\n'}
for language in ('english','french','german','spanish'):
    outputs[f'localisation/replace/zzzz_RIP_government_status_l_{language}.yml'] = 'l_'+language+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(10), chr(92)+"n")}"' for k,v in LOC.items())+'\n'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for rel,content in outputs.items():
        data=content.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8-sig' if rel.endswith('.yml') else 'utf-8')
        path=ROOT/rel
        if args.check:
            assert path.exists() and path.read_bytes()==data, f'Stale generated file: {rel}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    print(f'Government status UI: {len(outputs)} outputs '+('verified' if args.check else 'written'))
if __name__ == '__main__': main()