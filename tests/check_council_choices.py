"""Source regressions for council choices; EU4 runtime is not emulated."""
from clausewitz_testlib import read, named_block, normalized, vanilla_grep
def action(file, name):
    return named_block(read('common/government_mechanics/'+file+'.txt'), name)
snem=action('rip_kyivan_seniority','kyiv_call_the_snem')
assert 'num_of_subjects' not in snem
assert 'any_subject_country' in snem and 'is_subject_of_type = princedom' in snem and 'is_subject_of_type = senior_udil' in snem
for name in ('chancery','settlement','cadastral','urbarial','toleration','frontier'):
    a=action('rip_hlc_austrian_reorganization','hlc_enact_'+name+'_ordinance')
    assert 'has_reform = hlc_crown_authority_reform' in named_block(a,'trigger')
mods=read('common/event_modifiers/west_ukraine_modifiers.txt')
assert 'advisor_cost = 0.1' in named_block(mods,'hlc_chancery_ordinance_modifier')
assert 'global_unrest = 1' in named_block(mods,'hlc_settlement_ordinance_modifier')
for name in ('hlc_confirm_the_boyars_in_office','hlc_counter_the_foreign_claimant','hlc_make_an_example_of_a_defiant_boyar'):
    a=action('rip_hlc_boyar_council',name)
    assert 'cooldown_token = hlc_boyar_council_session' in a
    assert 'has_reform = hlc_galician_voivodeship_reform' in named_block(a,'trigger')
consent=action('rip_lit_pany_rada','lit_seek_the_radas_confirmation')
muster=action('rip_lit_pany_rada','lit_the_radas_own_retinues')
assert 'name = lit_rada_confirmed' in consent
assert 'has_country_modifier = lit_rada_confirmed' in named_block(muster,'trigger')
assert 'remove_country_modifier = lit_rada_confirmed' in named_block(muster,'effect')
assert 'is_at_war = yes' in named_block(muster,'trigger')
assert 'cooldown_token' not in consent+muster, 'shared cooldown makes consent unusable until its expiry'
buy=action('rip_vln_magnate_senate','vln_buy_off_a_magnate_house')
assert 'years_of_income = 0.5' in named_block(buy,'trigger')
assert 'add_years_of_income = -0.5' in named_block(buy,'effect')
assert 'add_local_autonomy = 15' in buy and 'is_capital = no' in buy
banners=action('rip_vln_magnate_senate','vln_call_up_the_magnate_banners')
assert 'is_at_war = yes' in named_block(banners,'trigger')
assert 'remove_country_modifier = vln_senate_convened' in named_block(banners,'effect')
assert 'add_manpower = 0.1' in banners
print('COUNCILS PASS: subject gate, ordinance costs, reform guards, consent consumption, territorial patronage.')
