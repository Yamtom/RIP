"""Source contracts only; these checks do not execute EU4 triggers."""
import json
import re
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, vanilla_root


decision = named_block(read('decisions/NovgorodZalesyeDecisions.txt'), 'nov_north_slavic_consolidation')
allow = named_block(decision, 'allow')
anchor = named_block(allow, '33')
assert 'trade_share' in anchor and 'node = novgorod' not in allow
assert 'country = ROOT' in anchor and 'share = 50' in anchor

diplomacy = read('common/new_diplomatic_actions/00_diplomatic_actions.txt')
loans = [block for _, block in keyed_blocks(diplomacy, 'add_entry') if 'name = SIZE_OF_LOANS' in block]
assert len(loans) == 2
for block, weight in zip(loans, (10, -20)):
    export = named_block(block, 'export_to_variable')
    assert 'value = trigger_value:num_of_loans' in export
    assert 'who = FROM' in export
    assert 'variable_name = ai_value' in export
    assert 'num_of_loans = 1' in named_block(block, 'FROM')
    assert f'value = {weight}' in named_block(block, 'multiply_variable')

hook = named_block(read('common/on_actions/00_on_actions.txt'), 'on_trade_good_changed')
assert 'owner = { economic_ideas = 3 }' in hook
assert 'FROM = { economic_ideas = 3 }' not in hook

# Each generated Mission node checks the share at its actual 1.37 anchor and
# buildings inside a member-province iterator, never directly at country scope.
nodes = json.loads(read('tools/data/trade_nodes_1_37.json'))['nodes']
generated = read('common/scripted_triggers/rip_church_nodes_generated.txt')
for node, province in nodes:
    gate = named_block(generated, f'rip_church_node_{node}_potential')
    anchor = named_block(gate, str(province))
    assert 'trade_share = { country = ROOT share = 50 }' in anchor
    parish = named_block(anchor, 'any_trade_node_member_province')
    assert 'has_building = temple' in parish and 'has_building = cathedral' in parish
    assert 'owned_by = ROOT' in parish
policy = read('common/trading_policies/RIP_MOS_RUS_trading_policies.txt')
for gate_name in ('can_select', 'can_maintain'):
    gate = named_block(policy, gate_name)
    assert re.search(r'FROM\s*=\s*\{\s*trade_share\s*=', gate)
    parish = named_block(gate.replace('{', '{\n'), 'any_trade_node_member_province')
    assert 'has_building = temple' in parish and 'has_building = cathedral' in parish

# Full-file overrides must contain precisely the reviewed native changes.
game = vanilla_root()
if game:
    import sys
    sys.path.insert(0, str(ROOT / 'tools'))
    from build_runtime_scope_fixes import outputs
    expected = dict(outputs(game))
    assert diplomacy == expected['common/new_diplomatic_actions/00_diplomatic_actions.txt']
    actual = read('common/on_actions/00_on_actions.txt')
    from clausewitz_testlib import normalized
    assert normalized(actual) == normalized(expected['common/on_actions/00_on_actions.txt'])
    uzh = read('common/on_actions/RIP_UZH_on_actions.txt')
    assert actual.count('uzh_sg_war_won_effect = yes') == 0
    assert named_block(uzh, 'on_war_won').count('uzh_sg_war_won_effect = yes') == 1
    # Regression: development >= 20 must keep the royal-city modifier.
    # Check that the sole removal is inside the guarded if, not its parent.
    for name in ('on_adm_exploited', 'on_dip_exploited', 'on_mil_exploited'):
        body = named_block(actual, name)
        removal = 'remove_province_modifier = estate_burghers_hungarian_royal_city_modifier'
        gates = [block for _, block in keyed_blocks(body, 'if') if removal in block]
        assert len(gates) == 1 and body.count(removal) == 1
        limit = named_block(gates[0], 'limit')
        assert 'has_province_modifier = estate_burghers_hungarian_royal_city_modifier' in limit
        assert 'NOT = { development = 20 }' in limit

else:
    print('SKIP: native full-file delta (no installed EU4)')
print(f'PASS: loan exports, trade-good owner, Novgorod scope, {len(nodes)} Mission anchors and policy gates (static only)')
