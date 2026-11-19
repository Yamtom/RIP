"""Static pacing, usable rewards and late realm mission layout contracts."""
import re
from clausewitz_testlib import named_block, read

missions = read('missions/Zakarpatta_Missions.txt')
for mission, predecessor, flag, days in (
    ('uz_language_decree', 'uz_rusin_language', 'uzh_language_standardized', 1095),
    ('uz_self_identification', 'uz_identity_question', 'uzh_identity_path_locked', 1825),
    ('uzh_solotvynska_camera', 'uzh_agriculture', 'uzh_agriculture_program_launched', 730),
):
    block = named_block(missions, mission)
    gate = named_block(named_block(block, 'trigger'), 'had_country_flag')
    assert f'flag = {flag}' in gate and f'days = {days}' in gate
    assert f'set_country_flag = {flag}' in named_block(named_block(missions, predecessor), 'effect')

decree = named_block(missions, 'uz_language_decree')
assert 'uzh_pre_identity_candidate_culture = yes' in named_block(decree, 'trigger')
assert 'uzh_has_courthouse_infrastructure = yes' in named_block(decree, 'trigger')
assert 'dip_power = 100' in named_block(decree, 'trigger')
assert 'add_dip_power = -100' in named_block(decree, 'effect')
assert 'if =' not in named_block(decree, 'effect')
identity = named_block(named_block(missions, 'uz_self_identification'), 'trigger')
assert all(s in identity for s in ('stability = 2', 'uzh_identity_core_culture = yes', 'religion = ROOT', 'value = 5'))
camera = named_block(missions, 'uzh_solotvynska_camera')
assert all(s in named_block(camera, 'trigger') for s in ('treasury = 150', 'base_production = 6',
           'uzh_has_workshop_infrastructure = yes', 'uzh_has_courthouse_infrastructure = yes'))
assert 'add_treasury = -150' in named_block(camera, 'effect')

frontier = named_block(named_block(missions, 'uzh_pannonian_frontier'), 'effect')
assert 'carpathia_region' not in frontier
for area in ('transylvania_area', 'slovakia_area'):
    assert 'add_permanent_claim = ROOT' in named_block(frontier, area)
assert frontier.count('add_permanent_claim') == 2
expansion = named_block(named_block(missions, 'uzh_pannonian_expansion'), 'effect')
development = named_block(expansion, 'every_owned_province')
assert 'area = alfold_area' in development and 'add_base_production = 1' in development
assert expansion.count('add_permanent_claim') == 1
assert 'add_permanent_claim = ROOT' in named_block(expansion, 'slavonia_area')
colonists = named_block(read('common/event_modifiers/RIP_UZH_modifiers.txt'), 'uz_banat_colonists')
assert 'colonist_placement_chance' not in colonists and 'global_colonial_growth' not in colonists
assert all(s in colonists for s in ('production_efficiency = 0.1', 'global_manpower_modifier = 0.1', 'development_cost = -0.1'))

slot4 = named_block(missions, 'UZH_missions_4')
assert 'slot = 4' in slot4
assert 'UZH_missions_realm' not in missions
for key, position in [('uz_huszt_rename', 9), ('uz_zakarpattia_realm', 10)]:
    assert f'position = {position}' in named_block(slot4, key)
    assert key not in named_block(missions, 'UZH_missions_3')
assert [int(p) for p in re.findall(r'\bposition\s*=\s*(\d+)', slot4)] == [3, 4, 8, 9, 10, 11, 12]
requirements = named_block(named_block(slot4, 'uz_huszt_rename'), 'required_missions')
assert 'uz_self_identification' in requirements and 'uzh_palatial_reform' in requirements
assert 'uz_huszt_rename' in named_block(named_block(slot4, 'uz_zakarpattia_realm'), 'required_missions')
print('PASS: three distinct mission stages, targeted claims, usable settlement rewards and connected late realm titles')
