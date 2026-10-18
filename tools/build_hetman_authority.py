"""Generate HET's persistent political position and native government controls.

The country variable stores integer tenths. A ten-step binary projection uses
only documented constant government-power effects; no guessed power export.
"""
from pathlib import Path
import argparse
import re

ROOT = Path(__file__).resolve().parents[1]
POWER = 'rip_het_authority'
MECHANIC = 'rip_het_authority_mechanic'
VAR = 'rip_het_position'
OUT = {}
LOC = {}

def loc(key, value):
    LOC[key] = value

def power(value, op='set'):
    return f'{op}_government_power = {{ mechanic_type = {MECHANIC} power_type = {POWER} value = {value} }}'

def change(amount):
    return f'change_variable = {{ which = {VAR} value = {amount} }} rip_het_sync_effect = yes'

def put(path, text):
    OUT[path] = text.strip() + '\n'

put('common/scripted_triggers/rip_het_authority.txt', '''
rip_het_authority_active = {
    has_reform = rip_hetman_cossacks_reform
    has_government_mechanic = rip_het_authority_mechanic
    NOT = { has_reform = het_mazepist_autocracy_reform }
    NOT = { has_reform = het_collegium_control_reform }
}
rip_het_can_confirm_rights = {
    rip_het_authority_active = yes dip_power = 50
    check_variable = { which = rip_het_position value = 1 }
    NOT = { has_country_modifier = rip_het_authority_session }
}
rip_het_can_review_chancery = {
    rip_het_authority_active = yes adm_power = 50
    NOT = { check_variable = { which = rip_het_position value = 1000 } }
    NOT = { has_country_modifier = rip_het_authority_session }
}
''')

sync = f'''rip_het_sync_effect = {{
    if = {{ limit = {{ NOT = {{ check_variable = {{ which = {VAR} value = 0 }} }} }} set_variable = {{ which = {VAR} value = 0 }} }}
    if = {{ limit = {{ check_variable = {{ which = {VAR} value = 1001 }} }} set_variable = {{ which = {VAR} value = 1000 }} }}
    if = {{ limit = {{ rip_het_authority_active = yes }}
        {power(0)}
        set_variable = {{ which = rip_het_projection which = {VAR} }}
'''
for bit in (512, 256, 128, 64, 32, 16, 8, 4, 2, 1):
    sync += f'''        if = {{ limit = {{ check_variable = {{ which = rip_het_projection value = {bit} }} }}
            subtract_variable = {{ which = rip_het_projection value = {bit} }} {power(bit / 10, 'add')}
        }}
'''
sync += '    }\n}\n'

effects = sync + '''
rip_het_migrate_effect = {
    if = {
        limit = { tag = HET government = republic has_reform = rip_cossacks_reform }
        set_country_flag = rip_het_migrating
        remove_government_reform = rip_cossacks_reform
        add_government_reform = rip_hetman_cossacks_reform
        clr_country_flag = rip_het_migrating
    }
    if = {
        limit = { has_reform = rip_hetman_cossacks_reform NOT = { has_country_flag = rip_het_position_initialized } }
        set_country_flag = rip_het_position_initialized
        set_variable = { which = rip_het_position value = 500 }
    }
    rip_het_sync_effect = yes
}
'''
for name, gate, resource, amount in [('rights', 'confirm_rights', 'dip', -150), ('chancery', 'review_chancery', 'adm', 150)]:
    effects += f'''rip_het_{name}_effect = {{
    if = {{ limit = {{ rip_het_can_{gate} = yes }}
        add_{resource}_power = -50
        add_country_modifier = {{ name = rip_het_authority_session duration = 1825 }}
        {change(amount)}
'''
    if name == 'chancery':
        effects += '        if = { limit = { has_estate = estate_nobles } add_estate_loyalty = { estate = estate_nobles loyalty = -5 } }\n'
    effects += '    }\n}\n'
for name, amount in [('rights', -50), ('centralization', 50)]:
    effects += f'''rip_het_polk_{name}_effect = {{
    if = {{ limit = {{ rip_het_authority_active = yes NOT = {{ has_country_modifier = rip_het_polk_term }}
        event_target:het_target_polk = {{ owned_by = ROOT controlled_by = ROOT }} }}
        add_country_modifier = {{ name = rip_het_polk_term duration = 1095 }}
        {change(amount)}
    }}
}}
'''
effects += '''
rip_het_monthly_effect = {
    rip_het_migrate_effect = yes
    if = { limit = { rip_het_authority_active = yes }
        # Branches are mutually exclusive after either step; integer tenths
        # avoid oscillation at the centre and floating-point accumulation.
        if = { limit = { check_variable = { which = rip_het_position value = 501 } }
            subtract_variable = { which = rip_het_position value = 1 } }
        if = { limit = { NOT = { check_variable = { which = rip_het_position value = 500 } } }
            change_variable = { which = rip_het_position value = 1 } }
        rip_het_sync_effect = yes
        if = { limit = { OR = {
            NOT = { check_variable = { which = rip_het_position value = 100 } }
            check_variable = { which = rip_het_position value = 901 }
        } }
            change_variable = { which = rip_het_extreme_months value = 1 }
        }
        if = { limit = {
            check_variable = { which = rip_het_position value = 100 }
            NOT = { check_variable = { which = rip_het_position value = 901 } }
        } set_variable = { which = rip_het_extreme_months value = 0 } }
        if = { limit = {
            check_variable = { which = rip_het_extreme_months value = 60 }
            NOT = { has_country_modifier = rip_het_negotiation_term }
        }
            set_variable = { which = rip_het_extreme_months value = 0 }
            add_country_modifier = { name = rip_het_negotiation_term duration = 3650 }
            country_event = { id = rip_het_authority.1 }
        }
    }
    if = { limit = { NOT = { rip_het_authority_active = yes } }
        set_variable = { which = rip_het_extreme_months value = 0 }
        remove_country_modifier = rip_het_contested_course
    }
}
'''
put('common/scripted_effects/rip_het_authority.txt', effects)
put('common/on_actions/rip_het_authority.txt', '''
on_startup = { rip_het_migrate_effect = yes }
on_monthly_pulse = { rip_het_monthly_effect = yes }
''')

mechanic = f'''{MECHANIC} = {{
    alert_icon_gfx = GFX_alerticons_government_mechanics alert_icon_index = 1
    available = {{ has_reform = rip_hetman_cossacks_reform }}
    powers = {{ {POWER} = {{
        gui = rip_het_authority_power min = 0 max = 100 default = 50
        reset_on_new_ruler = no base_monthly_growth = 0 is_good = yes
        range_modifier = {{ trigger = {{ rip_het_authority_active = yes }} start_value = 0 end_value = 29.9
            modifier = {{ state_maintenance_modifier = -0.1 global_manpower_modifier = -0.05 }} }}
        range_modifier = {{ trigger = {{ rip_het_authority_active = yes has_estate = estate_nobles }} start_value = 0 end_value = 29.9
            modifier = {{ nobles_loyalty_modifier = 0.05 }} }}
        range_modifier = {{ trigger = {{ rip_het_authority_active = yes }} start_value = 70.1 end_value = 100
            modifier = {{ global_manpower_modifier = 0.1 global_autonomy = -0.025 global_unrest = 1 }} }}
    }} }}
    interactions = {{
'''
for name, gate, icon in [('rights', 'confirm_rights', 'GFX_rip_siversk_charter'), ('chancery', 'review_chancery', 'GFX_rip_kyiv_snem')]:
    mechanic += f'''        rip_het_{name} = {{
            icon = {icon}
            trigger = {{ rip_het_can_{gate} = yes }}
            effect = {{ rip_het_{name}_effect = yes }}
            ai_chance = {{ factor = 0 modifier = {{ factor = 10
                {'dip_power = 150 check_variable = { which = rip_het_position value = 700 }' if name == 'rights' else 'adm_power = 150 NOT = { check_variable = { which = rip_het_position value = 300 } }'}
            }} }}
        }}
'''
mechanic += '    }\n}\n'
# ai_chance modifier factors multiply: nonzero base with explicit blockers.
mechanic = mechanic.replace('ai_chance = { factor = 0 modifier = { factor = 10', 'ai_chance = { factor = 1 modifier = { factor = 10')
put('common/government_mechanics/rip_het_authority.txt', mechanic)
put('common/event_modifiers/rip_het_authority.txt', '''
rip_het_authority_session = { }
rip_het_polk_term = { }
rip_het_negotiation_term = { }
rip_het_contested_course = { global_unrest = 2 }
''')
put('events/RIP_HetmanAuthority.txt', f'''
namespace = rip_het_authority
country_event = {{
    id = rip_het_authority.1 title = rip_het_authority.1.t desc = rip_het_authority.1.d
    picture = COURT_eventPicture is_triggered_only = yes
    trigger = {{ rip_het_authority_active = yes }}
    option = {{ name = rip_het_authority.1.a ai_chance = {{ factor = 10 }}
        set_variable = {{ which = rip_het_compromise_before which = rip_het_position }}
        if = {{ limit = {{ rip_het_authority_active = yes NOT = {{ check_variable = {{ which = rip_het_compromise_before value = 500 }} }} }}
            change_variable = {{ which = rip_het_position value = 200 }}
            if = {{ limit = {{ check_variable = {{ which = rip_het_position value = 501 }} }} set_variable = {{ which = rip_het_position value = 500 }} }}
        }}
        if = {{ limit = {{ rip_het_authority_active = yes check_variable = {{ which = rip_het_compromise_before value = 501 }} }}
            change_variable = {{ which = rip_het_position value = -200 }}
            if = {{ limit = {{ NOT = {{ check_variable = {{ which = rip_het_position value = 500 }} }} }} set_variable = {{ which = rip_het_position value = 500 }} }}
        }}
        rip_het_sync_effect = yes
    }}
    option = {{ name = rip_het_authority.1.b
        trigger = {{ rip_het_authority_active = yes NOT = {{ check_variable = {{ which = rip_het_position value = 500 }} }} dip_power = 50 }}
        ai_chance = {{ factor = 1 }}
        if = {{ limit = {{ rip_het_authority_active = yes dip_power = 50 NOT = {{ check_variable = {{ which = rip_het_position value = 500 }} }} }}
            add_dip_power = -50 add_country_modifier = {{ name = rip_het_contested_course duration = 1095 }} }}
    }}
    option = {{ name = rip_het_authority.1.c
        trigger = {{ rip_het_authority_active = yes check_variable = {{ which = rip_het_position value = 501 }} adm_power = 50 }}
        ai_chance = {{ factor = 1 }}
        if = {{ limit = {{ rip_het_authority_active = yes adm_power = 50 check_variable = {{ which = rip_het_position value = 501 }} }}
            add_adm_power = -50 add_country_modifier = {{ name = rip_het_contested_course duration = 1095 }} }}
    }}
}}
''')
put('interface/rip_het_authority.gui', '''
guiTypes = {
 windowType = {
  name = "rip_het_authority_power" size = { x = 300 y = 58 } moveable = 0
  iconType = { name = "emblem" spriteType = "GFX_rip_concord" position = { x = 0 y = 2 } scale = 0.5 }
  instantTextBoxType = { name = "label" position = { x = 38 y = 0 } font = "vic_18" text = "rip_het_authority" maxWidth = 250 maxHeight = 22 format = left }
  iconType = { name = "government_power_bar" spriteType = "GFX_single_government_power_bar" position = { x = 35 y = 31 } }
  iconType = { name = "government_power_bar_frame" spriteType = "GFX_single_government_power_bar_frame" position = { x = 24 y = 28 } alwaystransparent = yes }
 }
}
''')
for key, value in {
    'rip_hetman_cossacks_reform': 'Hetmanate Government',
    'rip_hetman_cossacks_reform_desc': 'The Cossack institutions are retained, while the distribution of authority between the officers and the Hetman replaces the Sich government interactions. Position and previous terms survive reform changes.',
    'ability_rip_het_authority_mechanic': 'Starshyna and Hetman',
    'rip_het_authority': 'Starshyna - Hetman',
    'rip_het_authority_desc': '0: officers; 100: Hetman. Below 30: -10% state maintenance, -5% manpower, +5 noble loyalty equilibrium if present. Above 70: +10% manpower, -0.025 monthly autonomy, +1 unrest. The centre has no extra modifier. Each month, position moves 0.1 towards 50. Polity changes preserve position. Mazepist autocracy and collegial control suspend the scale and its bonuses.',
    'monthly_rip_het_authority': 'Monthly Distribution of Authority',
    'rip_het_authority_gain_modifier': 'Distribution of Authority Gain',
    'rip_het_rights': 'Confirm Officers Rights',
    'rip_het_rights_desc': 'Pay 50 DIP to move 15 points towards the officers. Both mandates share a five-year term, shown among country modifiers. No payment at the left boundary.',
    'rip_het_chancery': 'Review the Chancery',
    'rip_het_chancery_desc': 'Pay 50 ADM to move 15 points towards the Hetman. Nobles lose 5 loyalty if present. Both mandates share a five-year term, shown among country modifiers.',
    'rip_het_authority_session': 'Hetmanate Mandate: Five-Year Term',
    'rip_het_polk_term': 'Regimental Political Settlement: Three-Year Term',
    'rip_het_negotiation_term': 'Negotiated Settlement: Ten-Year Term',
    'rip_het_contested_course': 'Contested Government Course',
    'rip_het_authority.1.t': 'Negotiate the Distribution of Authority',
    'rip_het_authority.1.d': 'Five consecutive years of extreme power have strained the settlement between the officers and the Hetman. Compromise moves authority twenty points towards the centre. Defending the present course costs monarch power and brings three years of unrest.',
    'rip_het_authority.1.a': 'Accept a compromise.',
    'rip_het_authority.1.b': 'Defend the officers rights: 50 DIP.',
    'rip_het_authority.1.c': 'Defend the Hetman: 50 ADM.',
}.items():
    loc(key, value)
for language in ('english', 'french', 'german', 'spanish'):
    put(f'localisation/replace/zzzz_RIP_het_authority_l_{language}.yml', 'l_' + language + ':\n' + '\n'.join(f' {k}:0 "{v}"' for k, v in LOC.items()))

# Preserve the existing Cossack rights in a separate HET base reform.
base = (ROOT / 'common/government_reforms/RIP_shared_cossack_government_reforms.txt').read_text(encoding='utf-8-sig')
base = base[base.index('rip_cossacks_reform = {'):].replace('rip_cossacks_reform', 'rip_hetman_cossacks_reform')
start = base.index('\tpotential = {')
end = base.index('\tgovernment_abilities', start)
base = base[:start] + '\tpotential = { OR = { has_reform = rip_hetman_cossacks_reform tag = HET } }\n' + base[end:]
base = base.replace('cossacks_mechanic', MECHANIC)
base = re.sub(r'\s*legacy_equivalent = cossacks_legacy_reform', '', base)
base = base.replace('valid_for_nation_designer = yes', 'valid_for_nation_designer = no').replace('valid_for_new_country = yes', 'valid_for_new_country = no')
base = base[:base.rfind('}')] + '    effect = { rip_het_migrate_effect = yes }\n' + base[base.rfind('}'):]
put('common/government_reforms/RIP_HET_authority_reform.txt', base)

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    for rel, text in OUT.items():
        path = ROOT / rel
        data = text.replace('\r\n', '\n').encode('utf-8-sig' if rel.endswith('.yml') else 'utf-8')
        if args.check:
            assert path.read_bytes() == data, f'Stale: {rel}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
    for old, new in [('kyivan_throne_concord', POWER), ('monthly_kyivan_throne_concord', 'monthly_' + POWER), ('kyivan_throne_concord_gain_modifier', POWER + '_gain_modifier')]:
        data = (ROOT / f'gfx/interface/ideas_EU4/{old}.dds').read_bytes()
        target = ROOT / f'gfx/interface/ideas_EU4/{new}.dds'
        if args.check:
            assert target.read_bytes() == data, target
        else:
            target.write_bytes(data)
    print(f'HET authority: {len(OUT)} generated files ' + ('verified' if args.check else 'written'))

if __name__ == '__main__':
    main()
