"""Static contracts for Kyiv's shared and successor mission progression."""
import re
from clausewitz_testlib import read, named_block

shared = read('missions/Kyiv_Shared_Missions.txt')
successors = read('missions/Kyiv_Successors_Missions.txt')
kyiv = read('missions/Kyiv_Missions.txt')

for tag in ('KIE', 'KRU', 'UKR'):
    missions = {}
    for source in (shared, successors, kyiv):
        for column in re.findall(r'(?m)^(\w+) = \{', source):
            block = named_block(source, column)
            if not re.search(rf'\btag = {tag}\b', named_block(block, 'potential')):
                continue
            for mission in re.findall(r'(?m)^\t(\w+) = \{', block):
                if mission == 'potential':
                    continue
                body = named_block(block, mission)
                if 'required_missions' in body:
                    missions[mission] = re.findall(r'\b(?:KIE|UKR)_\w+', named_block(body, 'required_missions'))
    def visit(mission, path):
        assert mission in missions, (tag, mission, 'missing prerequisite')
        assert mission not in path, (tag, mission, 'cycle')
        for parent in missions[mission]:
            visit(parent, path | {mission})
    for mission in missions:
        visit(mission, set())
    print(f'{tag}: {len(missions)} missions, no missing prerequisites or cycles')

for src in (shared, kyiv, successors):
    assert 'has_completed_mission' not in src, 'invalid EU4 trigger has_completed_mission'

friend = named_block(shared, 'KIE_friend_or_foe')
gate = named_block(named_block(friend, 'trigger'), 'if')
assert 'tag = KIE' in gate
for prerequisite in ('KIE_byzantine_relations', 'KIE_subjugate_white_ruthenia'):
    assert f'mission_completed = {prerequisite}' in gate
assert friend.count('exists = GLH') == friend.count('exists = GOL') == 1

true_ruler = named_block(shared, 'KIE_true_ruler')
tr_trigger = named_block(true_ruler, 'trigger')
for forbidden in ('exists = VOL', 'exists = VLN', 'is_free_or_tributary_trigger', 'has_institution = renaissance'):
    assert forbidden not in tr_trigger, f'KIE_true_ruler trigger still blocks on {forbidden}'
tr_effect = named_block(true_ruler, 'effect')
assert tr_effect.count('cb_vassalize_mission') == 2
assert 'else_if = {' in tr_effect
tr_else = named_block(tr_effect, 'else')
assert 'volhynia_area' in tr_else and 'add_claim = ROOT' in tr_else
assert 'add_permanent_claim' not in tr_else

dniestr = named_block(kyiv, 'KIE_dniestr_trade_route')
assert 'province_trade_power' not in dniestr
assert '310' not in dniestr
for section_name in ('provinces_to_highlight', 'trigger'):
    sec = named_block(dniestr, section_name)
    assert '280' in sec and 'is_strongest_trade_power = ROOT' in sec
    assert '262' in sec and 'share = 20' in sec
    assert '1322' in sec and 'share = 25' in sec
assert 'full_idea_group = trade_ideas' in named_block(dniestr, 'trigger')

free_cities = named_block(kyiv, 'KIE_free_trade_cities')
for forbidden in ('kyivan_shogunate_reform', 'kyiv_path_shogunate'):
    assert forbidden not in free_cities, f'KIE_free_trade_cities still blocks on {forbidden}'
fc_trigger = named_block(free_cities, 'trigger')
assert 'has_estate = estate_burghers' in fc_trigger
assert 'influence = 60' in fc_trigger
assert 'province_has_center_of_trade_of_level = 1' in fc_trigger
assert 'provinces_to_highlight' in free_cities

tsyisar_trigger = named_block(named_block(successors, 'UKR_tsyisar'), 'trigger')
assert 'all_owned_province' not in tsyisar_trigger
tsyisar_scope = named_block(tsyisar_trigger, 'thrace_area')
assert 'type = all' in tsyisar_scope
assert 'country_or_non_sovereign_subject_holds = ROOT' in tsyisar_scope

# The Dnieper crossing is one pair of bank provinces plus a fort or settlement,
# not the culture of every province of the Yedisan and the Sloboda.
dniepr = named_block(successors, 'UKR_dniepr')
dniepr_trigger = named_block(dniepr, 'trigger')
assert 'all_owned_province' not in dniepr_trigger
assert 'yedisan_area' not in dniepr_trigger and 'sloboda_ukraine_area' not in dniepr_trigger
assert 'culture = ' not in dniepr_trigger, 'UKR_dniepr must not gate on distant provinces by culture'
assert 'country_or_non_sovereign_subject_holds = ROOT' in named_block(dniepr_trigger, '280')
bridgehead = named_block(dniepr_trigger, '2407')
assert 'country_or_non_sovereign_subject_holds = ROOT' in bridgehead
assert 'has_fort_building_trigger = yes' in bridgehead
assert 'has_province_modifier = cossack_settlement' in bridgehead

# The Sloboda becomes its own mission: a few hubs, not the whole area by culture.
sloboda = named_block(successors, 'UKR_sloboda_frontier')
assert 'required_missions = { UKR_dniepr KIE_dnieper_settlement }' in sloboda
sloboda_trigger = named_block(sloboda, 'trigger')
counter = named_block(sloboda_trigger, 'num_of_provinces_owned_or_owned_by_non_sovereign_subjects_with')
assert 'area = sloboda_ukraine_area' in counter and 'value = 2' in counter
assert 'type = all' not in sloboda_trigger
for culture in ('ruthenian', 'ruthenian_west_ruthenian', 'ruthenian_west_slavic'):
    assert f'culture = {culture}' in counter
assert 'has_fort_building_trigger = yes' in counter and 'has_province_modifier = cossack_settlement' in counter
assert 'required_missions = { UKR_sloboda_frontier }' in named_block(successors, 'UKR_tatar')
assert 'required_missions = { UKR_dniepr }' in named_block(successors, 'UKR_crimea')

horde = named_block(named_block(successors, 'UKR_horde'), 'trigger')
assert 'development = 70' not in horde
for index, area in enumerate(('astrakhan_area', 'lower_don_area', 'sloboda_ukraine_area'), 1):
    assert 'controlled_by = ROOT' in named_block(horde, area)
    total = named_block(horde, 'development_in_provinces', index)
    assert f'area = {area}' in total and 'value = 70' in total

def loc_entries(path):
    return dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(path), re.M))

expeditions_en = loc_entries('localisation/RIP_shared_ruthenian_expeditions_l_english.yml')
lysianskyi_desc = expeditions_en['rip_lysianskyi_circumnavigation_desc']
for token in ('Yurii Lysianskyi', 'Nizhyn', '1803-1806'):
    assert token in lysianskyi_desc, token
for lang in ('french', 'german', 'spanish'):
    shared_rep = loc_entries(f'localisation/replace/RIP_shared_ruthenian_content_l_{lang}.yml')
    assert shared_rep['rip_lysianskyi_circumnavigation_desc'] == lysianskyi_desc, lang

secure_kyiv = named_block(shared, 'KIE_secure_kyiv')
sk_trig = named_block(secure_kyiv, 'trigger')
for token in ('devastation = 1', 'local_autonomy = 20', 'development = 20', 'num_of_buildings_in_province = 1'):
    assert token in sk_trig, token
sk_eff = named_block(secure_kyiv, 'effect')
assert 'add_base_tax = 1' in sk_eff and 'add_base_production = 1' in sk_eff and 'add_base_manpower = 1' in sk_eff
assert 'add_base_tax = 2' not in sk_eff

kie_mods = read('common/event_modifiers/RIP_KIE_modifiers.txt')
gb_mod = named_block(kie_mods, 'KIE_great_building')
assert 'development_cost = -0.1' in gb_mod
assert 'development_cost = 0.1' not in gb_mod
assert 'build_cost = -0.1' in gb_mod
assert 'defensiveness = 0.15' in gb_mod
south = named_block(shared, 'KIE_secure_the_south')
assert 'duration = 5475' in south and 'duration = 730' not in south

kie_en = loc_entries('localisation/RIP_KIE_realm_l_english.yml')
assert 'monumental structure' not in kie_en['desc_KIE_great_building']
for key in ('KIE_secure_kyiv_desc', 'KIE_great_building', 'desc_KIE_great_building', 'desc_KIE_heir_of_rus'):
    for lang in ('french', 'german', 'spanish'):
        kie_rep = loc_entries(f'localisation/replace/RIP_KIE_content_l_{lang}.yml')
        assert kie_rep[key] == kie_en[key], (lang, key)

heir_mod = named_block(kie_mods, 'KIE_heir_of_rus')
for token in (
    'administrative_efficiency = 0.05',
    'governing_capacity_modifier = 0.2',
    'core_creation = -0.1',
    'diplomatic_reputation = 2',
    'num_accepted_cultures = 2',
):
    assert token in heir_mod, token
heir_mission = named_block(kyiv, 'KIE_heir_of_rus')
heir_eff = named_block(heir_mission, 'effect')
assert 'set_government_rank = 3' in heir_eff and 'is_part_of_hre = no' in heir_eff
assert 'add_adm_power = 100' in heir_eff and 'add_dip_power = 100' in heir_eff and 'add_mil_power = 100' in heir_eff
print('PASS: Kyiv successor progression contracts (static only)')
