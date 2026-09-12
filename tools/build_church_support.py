"""Generate version-pinned church support from the installed EU4 map.
Only generated church files and the explicitly named vanilla GUI overrides are written.
Run with --check to compare without writing.
"""
from pathlib import Path
import argparse, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from clausewitz_testlib import named_block, matching_brace, vanilla_root
ROOT = Path(__file__).resolve().parents[1]
GAME = vanilla_root()
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
outputs = {}
def output(path, text):
    outputs[path] = text.rstrip() + '\n'
nodes_text = (GAME/'common/tradenodes/00_tradenodes.txt').read_text(encoding='utf-8-sig')
nodes = []
for m in re.finditer(r'(?m)^(\w+)\s*=\s*\{', nodes_text):
    body = named_block(nodes_text, m[1])
    location = int(re.search(r'location\s*=\s*(\d+)', body)[1])
    nodes.append((m[1], location))

trigger = '# Generated country-scope node gates; ROOT is the country.\n'
effects = '# Generated from EU4 1.37 trade-node anchor IDs.\n'
recount, close, maintain, ai, options = [], [], [], [], []
for name, anchor in nodes:
    key = 'rip_church_node_' + name
    trigger += f'''{key}_eligible = {{
 religion = russian_orthodox has_country_flag = rip_church_icon_mission
 has_dlc = "Cradle of Civilization"
 {anchor} = {{
 has_trader = ROOT trade_share = {{ country = ROOT share = 50 }}
 any_trade_node_member_province = {{
 owned_by = ROOT controlled_by = ROOT is_core = ROOT religion = russian_orthodox
 has_province_flag = rip_church_ro_connected@ROOT
 OR = {{ has_building = temple has_building = cathedral }}
 }}
 any_trade_node_member_province = {{ rip_church_ro_propagation_target_root = yes }}
 }}
}}
{key}_can_open = {{
 {key}_eligible = yes NOT = {{ has_country_flag = {key} }}
 check_variable = {{ which = rip_church_fervor value = 12 }}
 OR = {{ NOT = {{ check_variable = {{ which = rip_church_nodes value = 1 }} }}
 AND = {{ has_country_flag = rip_church_ro_schismatic NOT = {{ check_variable = {{ which = rip_church_nodes value = 2 }} }} }} }}
}}
'''
    effects += f'''{key}_toggle_effect = {{
 rip_church_ro_recount_nodes_effect = yes
 if = {{ limit = {{ has_country_flag = {key} }} clr_country_flag = {key} }}
 else_if = {{ limit = {{ {key}_can_open = yes }}
 set_country_flag = {key}
 # First month is prepaid; later monthly upkeep charges each registered node.
 subtract_variable = {{ which = rip_church_fervor value = 2 }}
 }}
 rip_church_ro_recount_nodes_effect = yes
 rip_church_ro_maintain_nodes_effect = yes
 rip_church_ro_recount_effect = yes
}}
'''
    recount.append(f'if = {{ limit = {{ has_country_flag = {key} }} change_variable = {{ which = rip_church_nodes value = 1 }} }}')
    close.append(f'clr_country_flag = {key}')
    maintain.append(f'''if = {{ limit = {{ has_country_flag = {key} }}
 if = {{ limit = {{ NOT = {{ {key}_eligible = yes }} }} clr_country_flag = {key} }}
 else_if = {{ limit = {{ NOT = {{ has_country_flag = rip_church_ro_schismatic }} check_variable = {{ which = rip_church_nodes value = 1 }} }} clr_country_flag = {key} }}
 else = {{ change_variable = {{ which = rip_church_nodes value = 1 }} {anchor} = {{ every_trade_node_member_province = {{ set_province_flag = rip_church_ro_trade_target@ROOT }} }} }}
}}''')
    ai.append(f'if = {{ limit = {{ {key}_can_open = yes check_variable = {{ which = rip_church_fervor value = 60 }} }} {key}_toggle_effect = yes }}')
    options.append(f'''option = {{
 name = {key}_button
 trigger = {{ OR = {{ has_country_flag = {key} {key}_eligible = yes }} }}
 {key}_toggle_effect = yes
}}''')
effects += 'rip_church_ro_recount_nodes_effect = {\nset_variable = { which = rip_church_nodes value = 0 }\n'+'\n'.join(recount)+'\n}\n'
effects += 'rip_church_ro_close_all_nodes_effect = {\n'+'\n'.join(close)+'\nset_variable = { which = rip_church_nodes value = 0 }\n}\n'
effects += 'rip_church_ro_maintain_nodes_effect = {\nrip_church_ro_refresh_connections_effect = yes\nevery_province = { limit = { has_province_flag = rip_church_ro_trade_target@ROOT } clr_province_flag = rip_church_ro_trade_target@ROOT }\nset_variable = { which = rip_church_nodes value = 0 }\n'+'\n'.join(maintain)+'\n}\n'
effects += 'rip_church_ro_ai_nodes_effect = {\n'+'\n'.join(ai)+'\n}\n'
trigger += 'rip_church_ro_registered_node = { OR = {\n'
for name, anchor in nodes:
    trigger += f'AND = {{ has_country_flag = rip_church_node_{name} FROM = {{ province_id = {anchor} }} }}\n'
trigger += '} }\n'
output('common/scripted_triggers/rip_church_nodes_generated.txt', trigger)
output('common/scripted_effects/rip_church_nodes_generated.txt', effects)
output('events/RIP_ChurchNodes_generated.txt', '''namespace = rip_church_nodes
country_event = {
 id = rip_church_nodes.1 title = rip_church_nodes.1.t desc = rip_church_nodes.1.d
 picture = RELIGION_eventPicture is_triggered_only = yes
 trigger = { religion = russian_orthodox }
 immediate = { rip_church_ro_refresh_connections_effect = yes rip_church_ro_recount_nodes_effect = yes }
'''+'\n'.join(options)+'''
 option = { name = rip_church_close }
}
''')
# Preserve the complete native conversion file; add RO constraints to the shared trade profile only.
conversions = (GAME/'common/religious_conversions/00_religious_conversions.txt').read_text(encoding='utf-8-sig')
profile = named_block(conversions, 'propagate_religion_policy')
weights = named_block(profile, 'target_province_weights')
new_weights = weights.replace('factor = 5', '''factor = 5
        modifier = {
            factor = 0
            FROM = { religion = russian_orthodox }
            NOT = { rip_church_ro_propagation_target_from = yes }
        }
        modifier = {
            factor = 0.5
            FROM = { religion = russian_orthodox has_country_flag = rip_church_ro_schismatic }
            religion = orthodox
        }''', 1)
# RO has its own checked target whitelist; leave other religious policies unchanged.
new_weights = new_weights.replace('NOT = { has_country_flag = can_propagate_religion_in_abrahamic_provinces }',
                                'NOT = { has_country_flag = can_propagate_religion_in_abrahamic_provinces }\n                NOT = { religion = russian_orthodox }')
conversions = conversions.replace(profile, profile.replace(weights, new_weights), 1)
# Comment-only localization of the province name keeps the repository's ID audit precise.
conversions = re.sub(r'(province_id\s*=\s*118)\s*#.*', r'\1 # Roma', conversions)
output('common/religious_conversions/00_religious_conversions.txt', conversions)
# Construction migration picks Brest, then greatest development, then lowest numeric ID.
province_ids = sorted({int(p.name.split(' ')[0]) for p in (GAME/'history/provinces').glob('*.txt') if p.name.split(' ')[0].isdigit()}, reverse=True)
pick = '''# Generated deterministic ordering; not a random choice.
rip_church_pick_migration_seat_effect = {
 every_province = { limit = { has_province_flag = rip_church_seat_selected } clr_province_flag = rip_church_seat_selected }
 clear_global_event_target = rip_church_migration_best
 clr_global_flag = rip_church_migration_best_found
 if = { limit = { 277 = { rip_church_center_alive = yes } }
 277 = { set_province_flag = rip_church_seat_selected save_global_event_target_as = rip_church_union_seat }
 }
 else = {
'''
for pid in province_ids:
    pick += f'''{pid} = {{
 if = {{ limit = {{ rip_church_center_alive = yes }}
 if = {{ limit = {{ NOT = {{ has_global_flag = rip_church_migration_best_found }} }} save_global_event_target_as = rip_church_migration_best set_global_flag = rip_church_migration_best_found }}
 else_if = {{ limit = {{
 variable_arithmetic_trigger = {{
 export_to_variable = {{ which = rip_church_candidate_dev value = development }}
 export_to_variable = {{ which = rip_church_best_dev value = development who = event_target:rip_church_migration_best }}
 check_variable = {{ which = rip_church_candidate_dev which = rip_church_best_dev }}
 }}
 }} save_global_event_target_as = rip_church_migration_best }}
 }}
}}
'''
pick += '''
 event_target:rip_church_migration_best = { set_province_flag = rip_church_seat_selected save_global_event_target_as = rip_church_union_seat }
 }
 clear_global_event_target = rip_church_migration_best
 clr_global_flag = rip_church_migration_best_found
}
'''
output('common/scripted_effects/rip_church_center_migration_generated.txt', pick)
# Primary keys for generated node menu options.
node_loc = ''.join(f' {"rip_church_node_"+name+"_button"}:0 "Fund / close mission: ${name}$"\n' for name,_ in nodes)
for lang in ('english','french','german','spanish'):
    output(f'localisation/replace/zzzz_RIP_church_nodes_l_{lang}.yml', '\ufeffl_'+lang+':\n'+node_loc)
changed=[]
for path, text in outputs.items():
    target=ROOT/path
    current=target.read_text(encoding='utf-8') if target.exists() else None
    if current != text:
        changed.append(path)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8', newline='\n')
print(('STALE' if args.check and changed else 'GENERATED')+f': {len(nodes)} nodes; {len(province_ids)} province IDs; {len(changed)} files')
if args.check and changed:
    print('\n'.join(changed)); sys.exit(1)
