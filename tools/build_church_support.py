"""Generate version-pinned church support from the installed EU4 map.
Only generated church files and the explicitly named vanilla GUI overrides are written.
Run with --check to compare without writing.

Without an install the trade-node list comes from tools/data/trade_nodes_1_37.json and the two
files that patch a vanilla file (trading policies, religious conversions) are left as committed.
With one, the list is read from the game and the cache is kept in step with it.

The mission-node economy is written here and nowhere else (see rip_church_ro_recount_effect):
a node costs NODE_COST Fervor once and pays NODE_YIELD Fervor a month; in every parish of its
trade node that has a temple or cathedral it adds the rip_church_node_courtyards modifier.
"""
from pathlib import Path
import argparse, json, re, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from clausewitz_testlib import named_block, matching_brace, vanilla_root
ROOT = Path(__file__).resolve().parents[1]
GAME = vanilla_root()
NODE_COST, NODE_YIELD = 10, 3
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
outputs = {}
def output(path, text):
    outputs[path] = text.rstrip() + '\n'
CACHE = 'tools/data/trade_nodes_1_37.json'
if GAME is not None:
    nodes_text = (GAME/'common/tradenodes/00_tradenodes.txt').read_text(encoding='utf-8-sig')
    nodes = []
    for m in re.finditer(r'(?m)^(\w+)\s*=\s*\{', nodes_text):
        body = named_block(nodes_text, m[1])
        location = int(re.search(r'location\s*=\s*(\d+)', body)[1])
        nodes.append((m[1], location))
    output(CACHE, '{\n "source": ' + json.dumps(json.loads((ROOT/CACHE).read_text(encoding='utf-8'))['source']) +
           ',\n "nodes": [\n' + ',\n'.join('  ' + json.dumps(list(n)) for n in nodes) + '\n ]\n}')
else:
    nodes = [tuple(n) for n in json.loads((ROOT/CACHE).read_text(encoding='utf-8'))['nodes']]
    print('NOTE: no EU4 install; trade nodes read from ' + CACHE)

trigger = '# Generated country-scope node gates; ROOT is the country.\n'
effects = '# Generated from EU4 1.37 trade-node anchor IDs.\n'
recount, close, maintain, ai, options = [], [], [], [], []
# A parish that carries the node: owned, controlled, core, Muscovite Orthodox, linked to the capital,
# with a temple or cathedral. The same parish is what makes a node eligible at all.
PARISH = ('owned_by = ROOT controlled_by = ROOT is_core = ROOT religion = russian_orthodox '
          'has_province_flag = rip_church_ro_connected@ROOT OR = { has_building = temple has_building = cathedral }')
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
 check_variable = {{ which = rip_church_fervor value = {NODE_COST} }}
 OR = {{ NOT = {{ check_variable = {{ which = rip_church_nodes value = 1 }} }}
 AND = {{ has_country_flag = rip_church_ro_schismatic NOT = {{ check_variable = {{ which = rip_church_nodes value = 2 }} }} }} }}
}}
'''
    effects += f'''{key}_toggle_effect = {{
 rip_church_ro_recount_nodes_effect = yes
 if = {{ limit = {{ has_country_flag = {key} }} clr_country_flag = {key} }}
 else_if = {{ limit = {{ {key}_can_open = yes }}
 set_country_flag = {key}
 # Founding is paid in full, once; from then on the node pays {NODE_YIELD} Fervor a month.
 subtract_variable = {{ which = rip_church_fervor value = {NODE_COST} }}
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
 else = {{ change_variable = {{ which = rip_church_nodes value = 1 }} {anchor} = {{ every_trade_node_member_province = {{
 set_province_flag = rip_church_ro_trade_target@ROOT
 if = {{ limit = {{ {PARISH} }} add_province_modifier = {{ name = rip_church_node_courtyards duration = 62 }} }}
 }} }} }}
}}''')
    # The AI founds a node as soon as it can pay and keep a reserve; the node pays for itself.
    ai.append(f'if = {{ limit = {{ {key}_can_open = yes check_variable = {{ which = rip_church_fervor value = {NODE_COST * 3} }} }} {key}_toggle_effect = yes }}')
    # The menu is a list of what can be funded or closed right now, each line with its price and return.
    options.append(f'''option = {{
 name = {key}_fund
 trigger = {{ {key}_can_open = yes }}
 hidden_effect = {{ {key}_toggle_effect = yes country_event = {{ id = rip_church_nodes.1 }} }}
}}
option = {{
 name = {key}_close
 trigger = {{ has_country_flag = {key} }}
 hidden_effect = {{ {key}_toggle_effect = yes country_event = {{ id = rip_church_nodes.1 }} }}
}}''')
LIFT = ('every_owned_province = { limit = { has_province_modifier = rip_church_node_courtyards } '
        'remove_province_modifier = rip_church_node_courtyards }')
effects += 'rip_church_ro_recount_nodes_effect = {\nset_variable = { which = rip_church_nodes value = 0 }\n'+'\n'.join(recount)+'\n}\n'
effects += 'rip_church_ro_close_all_nodes_effect = {\n'+'\n'.join(close)+'\nset_variable = { which = rip_church_nodes value = 0 }\n'+LIFT+'\n}\n'
effects += 'rip_church_ro_maintain_nodes_effect = {\nrip_church_ro_refresh_connections_effect = yes\nevery_province = { limit = { has_province_flag = rip_church_ro_trade_target@ROOT } clr_province_flag = rip_church_ro_trade_target@ROOT }\n'+LIFT+'\nset_variable = { which = rip_church_nodes value = 0 }\n'+'\n'.join(maintain)+'\n}\n'
effects += 'rip_church_ro_ai_nodes_effect = {\n'+'\n'.join(ai)+'\n}\n'
trigger += 'rip_church_ro_registered_node = { OR = {\n'
for name, anchor in nodes:
    trigger += f'AND = {{ has_country_flag = rip_church_node_{name} FROM = {{ province_id = {anchor} }} }}\n'
trigger += '} }\n'
trigger += 'rip_church_ro_can_open_network_menu = { religion = russian_orthodox OR = {\n check_variable = { which = rip_church_nodes value = 1 }\n'
trigger += ''.join(f'rip_church_node_{name}_can_open = yes\n' for name,_ in nodes)
trigger += '} }\n'
output('common/scripted_triggers/rip_church_nodes_generated.txt', trigger)
# Trade policies are parsed before these scripted triggers are available in EU4.
# Expand the same authoritative gates instead of leaving unresolved references.
policy_triggers = trigger + '\n' + (ROOT/'common/scripted_triggers/rip_church_propagation_triggers.txt').read_text(encoding='utf-8-sig')
def expand_policy_gate(name, stack=()):
    assert name not in stack, ('Recursive policy gate', stack, name)
    block = named_block(policy_triggers, name)
    body = block[block.index('{')+1:block.rfind('}')]
    return re.sub(r'\b(rip_church_\w+)\s*=\s*yes\b',
                  lambda m: expand_policy_gate(m[1], stack+(name,)), body)
native_gate = '\n'.join(line.rstrip() for line in expand_policy_gate('rip_church_ro_can_maintain_policy').splitlines())
output('common/trading_policies/RIP_church_mission_network.txt', '''# Generated: native gates only, because trading policies load before scripted triggers.
rip_church_mission_network = {
 unique = yes
 potential = { religion = russian_orthodox }
 can_select = {
'''+native_gate+'''
 }
 can_maintain = {
'''+native_gate+'''
 }
 show_alert = yes
 center_of_reformation = yes
 button_gfx = GFX_rip_ro_mission_policy
}
''')
output('common/scripted_effects/rip_church_nodes_generated.txt', effects)
output('events/RIP_ChurchNodes_generated.txt', '''namespace = rip_church_nodes
country_event = {
 id = rip_church_nodes.1 title = rip_church_nodes.1.t desc = rip_church_nodes.1.d
 picture = RELIGION_eventPicture is_triggered_only = yes
 trigger = { religion = russian_orthodox }
 immediate = { rip_church_ro_refresh_connections_effect = yes rip_church_ro_recount_nodes_effect = yes rip_church_ro_recount_effect = yes }
'''+'\n'.join(options)+'''
 option = { name = rip_church_close }
}
''')
if GAME is not None:
    # Preserve native policies; the church branches cannot bypass their own mechanics.
    policies = (GAME/'common/trading_policies/00_trading_policies.txt').read_text(encoding='utf-8-sig')
    policy = named_block(policies, 'propagate_religion')
    guard = '\n\t\tNOT = { religion = greek_catholic }\n\t\tNOT = { religion = russian_orthodox }'
    restricted = policy
    for gate in ('potential', 'can_select', 'can_maintain'):
        restricted = restricted.replace(gate + ' = {', gate + ' = {' + guard, 1)
    output('common/trading_policies/00_trading_policies.txt', policies.replace(policy, restricted, 1))
    # Preserve the complete native conversion file; constrain only the shared trade profile.
    conversions = (GAME/'common/religious_conversions/00_religious_conversions.txt').read_text(encoding='utf-8-sig')
    profile = named_block(conversions, 'propagate_religion_policy')
    weights = named_block(profile, 'target_province_weights')
    new_weights = weights.replace('factor = 5', '''factor = 5
        modifier = {
            factor = 0
            FROM = { religion = greek_catholic }
        }
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
# Primary keys for generated node menu options: what funding costs and what it returns, per node.
node_loc = ''.join(
    f' rip_church_node_{name}_fund:0 "Fund ${name}$: §R-{NODE_COST} Fervor§!, then §G+{NODE_YIELD} Fervor§! a month and §G+20% trade power§! in your parishes there"\n'
    f' rip_church_node_{name}_close:0 "Close ${name}$: §R-{NODE_YIELD} Fervor§! a month; the {NODE_COST} Fervor are not refunded"\n'
    for name,_ in nodes)
for lang in ('english','french','german','spanish'):
    output(f'localisation/replace/zzzz_RIP_church_nodes_l_{lang}.yml', '﻿l_'+lang+':\n'+node_loc)
changed=[]
for path, text in outputs.items():
    target=ROOT/path
    current=target.read_text(encoding='utf-8') if target.exists() else None
    if current != text:
        changed.append(path)
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8', newline='\n')
print(('STALE' if args.check and changed else 'GENERATED')+f': {len(nodes)} nodes; {len(changed)} files')
if args.check and changed:
    print('\n'.join(changed)); sys.exit(1)
