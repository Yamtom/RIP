"""Source/UI contracts, not proof of engine rendering or campaign balance."""
import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

loc = dict(re.findall(r'^ ([\w]+):\d+ "(.*)"$',read('localisation/replace/zzzz_rip_government_ui_l_english.yml'),re.M))
assert loc['kyivan_peoples_gathering'] == 'Concord of Peoples'
assert 'Prosperity' not in loc['kyivan_peoples_gathering_desc']
reforms = read('common/government_reforms/RIP_KIE_KRU_government_reforms.txt')
ids = ['ruthenian_factional_empire'+s+'_reform' for s in ('','_princes_hetmans','_boyars_hetmans')]
assert len({loc[i] for i in ids}) == 1
assert loc['kyivan_veche_reform'] == 'Kyivan Veche Republic'
assert loc['kyivan_boyar_republic_reform'] == 'Kyivan Boyar Rada'

def evaluate(text, held, tag='KRU', government='monarchy'):
    tokens = re.findall(r'[{}=]|[^\s{}=]+',text)
    pos = 0
    def parse(mode='AND'):
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]; assert tokens[pos+1] == '='; pos += 2
            value = tokens[pos]; pos += 1
            if value == '{':
                result.append(parse(key)); assert tokens[pos] == '}'; pos += 1
            elif key == 'has_reform': result.append(value in held)
            elif key == 'tag': result.append(value == tag)
            elif key == 'government': result.append(value == government)
            elif key == 'always': result.append(value == 'yes')
            else: raise AssertionError(key)
        return any(result) if mode == 'OR' else not any(result) if mode == 'NOT' else all(result)
    return parse()

potentials = {i:named_block(named_block(reforms,i),'potential') for i in ids}
for active in ids:
    visible = [i for i in ids if evaluate(potentials[i],{active})]
    assert visible == [active], (active,visible)
assert [i for i in ids if evaluate(potentials[i],set())] == ids[:1]
assert not any(evaluate(p,set(),'FRA') for p in potentials.values())

parliament = read('customizable_localization/rip_parliament_names.txt')
choices = [(named_block(b,'trigger'),re.search(r'localisation_key = (\w+)',b)[1]) for _,b in keyed_blocks(parliament,'text')]
def parliament_name(tag, government, held=()):
    return next(key for trigger,key in choices if evaluate(trigger,set(held),tag,government))
for tag in ('KIE','CHR','VLN','UZH','PRL','PDL','ODS','RUT'):
    assert parliament_name(tag,'theocracy') == 'rip_parliament_sobor'
    assert parliament_name(tag,'republic') == 'rip_parliament_'+tag.lower()+'_viche'
    assert parliament_name(tag,'monarchy') == 'rip_parliament_estates'
for active in ids:
    assert parliament_name('KRU','monarchy',[active]) == 'rip_parliament_three'
for tag,gov,reform,want in [('KIE','monarchy','kyivan_shogunate_reform','snem'),
                           ('CHR','republic','chr_siversk_veche_reform','siversk_veche'),
                           ('CHR','republic','chr_desna_staple_reform','desna_staple'),
                           ('CHR','republic','chr_town_union_reform','siversk_towns'),
                           ('CHR','republic','chr_rada_of_lands_reform','rada_of_lands'),
                           ('CHR','monarchy','chr_siversk_principality_reform','siversk_boyar'),
                           ('KIE','republic','kyivan_boyar_republic_reform','kyivan_boyar'),
                           ('HLC','republic','hlc_boyar_republic_reform','halych_boyar'),
                           ('HLC','monarchy','hlc_crown_and_sejm_reform','galician_sejm'),
                           ('LIT','monarchy','lit_grand_diet_reform','grand_diet'),
                           ('VLN','republic','vln_sejmik_republic_reform','volhynian_sejmik'),
                           ('UZH','republic','uzh_republican_komitat_system_reform','komitat'),
                           ('LIT','monarchy','lit_pany_rada_reform','pany'),
                           ('HET','monarchy','het_starshyna_oligarchy_reform','officers'),
                           ('HET','republic','','general'),('ZAZ','republic','','sich')]:
    assert parliament_name(tag,gov,[reform]) == 'rip_parliament_'+want

unique_parliaments = (
    'rip_parliament_siversk_veche',
    'rip_parliament_desna_staple',
    'rip_parliament_siversk_towns',
    'rip_parliament_rada_of_lands',
    'rip_parliament_siversk_boyar',
    'rip_parliament_ruthenian_principality',
    'rip_parliament_kyivan_boyar',
    'rip_parliament_halych_boyar',
    'rip_parliament_galician_sejm',
    'rip_parliament_grand_diet',
    'rip_parliament_volhynian_sejmik',
)
assert len({loc[key] for key in unique_parliaments}) == len(unique_parliaments)

for power in ('kyivan_throne_concord','kyivan_peoples_gathering','kyiv_princely_levy_power','kyiv_seat_rotation_power','kyiv_grant_reconfirmation_power'):
    for key in (power,'monthly_'+power,power+'_gain_modifier'):
        assert (ROOT/f'gfx/interface/ideas_EU4/{key}.dds').read_bytes()[:4] == b'DDS '

siversk = named_block(read('common/government_reforms/RIP_CHR_government_reforms.txt'),'chr_siversk_principality_reform')
assert 'icon = "russian_principality"' in siversk
assert 'russian_mechanic' not in siversk and 'weaker_russian_ability' not in siversk
assert 'siversk_patrimony_mechanic' in siversk
mechanic = read('common/government_mechanics/rip_siversk_patrimony.txt')
for action, power in [('confirm_patrimonies','adm'),('charter_towns','dip'),('muster_druzhyna','mil')]:
    block = named_block(mechanic,'siversk_'+action)
    assert f'{power}_power = 50' in named_block(block,'trigger')
    assert f'add_{power}_power = -50' in named_block(block,'effect')
    assert 'cooldown_years = 10' in block
    assert 'has_country_modifier' in named_block(block,'trigger')

court = read('common/government_mechanics/rip_ruthenian_factional_court.txt')
old_balances = (
    'kru_knyazi_boyary_balance',
    'kru_boyary_starshyna_balance',
    'kru_knyazi_starshyna_balance',
)
assert 'powers =' not in court
assert not any(name in court for name in old_balances)
assert 'on_min_reached' not in court and 'on_max_reached' not in court
assert 'influence = 6' not in court

state_general_pairs = {
    ids[0]: ('diplomatic_reputation = 0.5', 'discipline = 0.01'),
    ids[1]: ('legitimacy = 0.5', 'global_tax_modifier = 0.05'),
    ids[2]: ('stability_cost_modifier = -0.05', 'vassal_forcelimit_bonus = 0.05'),
}
for reform_id, effects in state_general_pairs.items():
    reform = named_block(reforms, reform_id)
    conditional = named_block(reform, 'conditional')
    allow = named_block(conditional, 'allow')
    assert 'has_dlc = "Res Publica"' in allow
    assert 'has_dlc = "Winds of Change"' in allow
    state_general = named_block(reform, 'states_general_mechanic')
    assert 'kru_rada_coalition' in state_general
    assert 'kru_rada_opposition' in state_general
    for effect in effects:
        assert effect in state_general

effects = read('common/scripted_effects/kru_effects.txt')
record = normalized(named_block(effects, 'kru_record_dominant_faction_effect'))
for faction in ('kru_knyazi', 'kru_boyary', 'kru_starshyna'):
    assert f'faction_influence = {{ faction = {faction} influence = 60 }}' in record
fallback = normalized(named_block(effects, 'kru_set_fallback_previous_dominant_effect'))
for faction in ('kru_knyazi', 'kru_boyary', 'kru_starshyna'):
    assert f'kru_previous_dominant_{faction[4:]}' in fallback
center = normalized(named_block(effects, 'kru_center_states_general_effect'))
assert 'has_states_general_mechanic = yes' in center
assert 'change_statists_vs_orangists = -10' in center
assert 'change_statists_vs_orangists = 1' in center
sync_block = named_block(effects, 'kru_sync_reform_to_faction_effect')
sync = normalized(sync_block)
assert 'influence = 33' not in sync
assert all(f'kru_previous_dominant_{faction[4:]}' in sync
           for faction in ('kru_knyazi', 'kru_boyary', 'kru_starshyna'))
for current, previous, reform_id in (
    ('kru_knyazi', 'kru_boyary', ids[0]),
    ('kru_boyary', 'kru_knyazi', ids[0]),
    ('kru_knyazi', 'kru_starshyna', ids[1]),
    ('kru_starshyna', 'kru_knyazi', ids[1]),
    ('kru_boyary', 'kru_starshyna', ids[2]),
    ('kru_starshyna', 'kru_boyary', ids[2]),
):
    assert f'faction_in_power = {current}' in sync
    assert f'has_country_flag = kru_previous_dominant_{previous[4:]}' in sync
    assert f'add_government_reform = {reform_id}' in sync
    matching = [branch for key in ('if', 'else_if')
                for _, branch in keyed_blocks(sync_block, key)
                if f'add_government_reform = {reform_id}' in branch
                and 'kru_previous_dominant_' in branch]
    assert len(matching) == 1
    alternatives = keyed_blocks(named_block(named_block(matching[0], 'limit'), 'OR'), 'AND')
    assert any(f'faction_in_power = {current}' in branch
               and f'has_country_flag = kru_previous_dominant_{previous[4:]}' in branch
               for _, branch in alternatives), (current, previous, reform_id)
pair_branches = [
    block
    for key in ('if', 'else_if')
    for _, block in keyed_blocks(sync_block, key)
]
for reform_id in ids:
    branch = next(block for block in pair_branches
                  if f'add_government_reform = {reform_id}' in block
                  and 'kru_previous_dominant_' in block)
    assert f'has_reform = {reform_id}' not in normalized(named_block(branch, 'limit'))
junior = normalized(named_block(effects, 'kru_apply_junior_blocs_effect'))
assert all(f'kru_previous_dominant_{faction[4:]}' in junior
           for faction in ('kru_knyazi', 'kru_boyary', 'kru_starshyna'))
for action in ('kru_court_the_knyazi', 'kru_court_the_boyary', 'kru_court_the_starshyna'):
    interaction = named_block(named_block(court, 'interactions'), action)
    assert 'kru_refresh_factional_court_effect = yes' in named_block(interaction, 'effect')

gfx = read('interface/rip_ruthenian_government.gfx')
for faction in ('knyazi','boyary','starshyna'):
    assert f'GFX_faction_kru_{faction}"' in gfx
    assert f'GFX_faction_bg_kru_{faction}"' in gfx
    assert loc[f'kru_{faction}_FACTION_DESC']
expected_ability_icons = {
    'rip_siversk_patrimony': [
        'GFX_rip_siversk_charter',
        'GFX_rip_siversk_towns',
        'GFX_rip_siversk_retinue',
    ],
    'rip_kyivan_seniority': [
        'GFX_rip_kyiv_snem',
        'GFX_rip_kyiv_udil',
        'GFX_rip_kyiv_druzhyna',
    ],
    'rip_kyivan_seniorate': [
        'GFX_cossacks_ability_MIL',
        'GFX_cossacks_ability_DIP',
        'GFX_cossacks_ability_ADM',
    ],
    'rip_ruthenian_factional_court': [
        'GFX_faction_kru_knyazi',
        'GFX_faction_kru_boyary',
        'GFX_faction_kru_starshyna',
    ],
}
for file, expected in expected_ability_icons.items():
    text = read(f'common/government_mechanics/{file}.txt')
    assert re.findall(r'^\s*icon = (\w+)', text, re.M) == expected

for path, mechanic, actions, years, token, cooldown_desc in (
    (
        'common/government_mechanics/rip_hlc_boyar_council.txt',
        'hlc_boyar_council_mechanic',
        ('hlc_confirm_the_boyars_in_office', 'hlc_counter_the_foreign_claimant',
         'hlc_make_an_example_of_a_defiant_boyar'),
        10,
        'hlc_boyar_council_session',
        'hlc_boyar_council_session_cd',
    ),
    (
        'common/government_mechanics/rip_lit_pany_rada.txt',
        'lit_pany_rada_mechanic',
        ('lit_seek_the_radas_confirmation', 'lit_win_over_a_wavering_lord',
         'lit_the_radas_own_retinues'),
        5,
        'lit_pany_rada_session',
        'lit_pany_rada_session_cd',
    ),
):
    buttons = named_block(named_block(read(path), mechanic), 'interactions')
    for action in actions:
        block = named_block(buttons, action)
        assert f'cooldown_years = {years}' in block
        if mechanic == 'hlc_boyar_council_mechanic':
            assert f'cooldown_token = {token}' in block
            assert f'cooldown_desc = {cooldown_desc}' in block
        else:
            assert 'cooldown_token' not in block

seniority = read('common/government_mechanics/rip_kyivan_seniority.txt')
seniority_interactions = named_block(
    named_block(seniority, 'kyivan_seniority_mechanic'), 'interactions'
)
prince_types = 'OR = { is_subject_of_type = princedom is_subject_of_type = senior_udil }'

snem = named_block(seniority_interactions, 'kyiv_call_the_snem')
snem_trigger = normalized(named_block(snem, 'trigger'))
assert 'num_of_subjects' not in snem_trigger
assert 'NOT = { num_of_subjects = 0 }' not in snem_trigger
assert f'any_subject_country = {{ {prince_types} }}' in snem_trigger
snem_effect = named_block(snem, 'effect')
snem_subject_effects = [
    normalized(block) for _, block in keyed_blocks(snem_effect, 'every_subject_country')
]
assert len(snem_subject_effects) == 1
assert f'limit = {{ {prince_types} }}' in snem_subject_effects[0]
assert 'add_liberty_desire = -20' in snem_subject_effects[0]
assert f'any_subject_country = {{ {prince_types} liberty_desire = 50 }}' in normalized(
    named_block(snem, 'ai_chance')
)

regrant = named_block(seniority_interactions, 'kyiv_regrant_the_udil')
assert f'any_subject_country = {{ {prince_types} liberty_desire = 35 }}' in normalized(
    named_block(regrant, 'trigger')
)
regrant_effect = named_block(regrant, 'effect')
regrant_subject_effects = [
    normalized(block) for _, block in keyed_blocks(regrant_effect, 'random_subject_country')
]
assert len(regrant_subject_effects) == 1
assert f'limit = {{ {prince_types} liberty_desire = 35 }}' in regrant_subject_effects[0]
assert f'any_subject_country = {{ {prince_types} liberty_desire = 60 }}' in normalized(
    named_block(regrant, 'ai_chance')
)

druzhyna = named_block(seniority_interactions, 'kyiv_summon_the_druzhyny')
assert f'any_subject_country = {{ {prince_types} }}' in normalized(
    named_block(druzhyna, 'trigger')
)

senate = named_block(
    read('common/government_mechanics/rip_vln_magnate_senate.txt'),
    'vln_magnate_senate_mechanic',
)
senate_gate = 'NOT = { has_reform = vln_cossack_host_reform }'
senate_available = normalized(named_block(senate, 'available'))
assert 'has_reform = vln_voivodeship_reform' in senate_available
assert senate_gate in senate_available
for button in (
    'vln_summon_the_senate',
    'vln_buy_off_a_magnate_house',
    'vln_call_up_the_magnate_banners',
):
    button_block = named_block(named_block(senate, 'interactions'), button)
    button_trigger = normalized(named_block(button_block, 'trigger'))
    assert 'has_reform = vln_voivodeship_reform' in button_trigger
    assert senate_gate in button_trigger

assert 'government_reform_rip_siversk_principality' not in gfx
for icon in ('GFX_rip_concord', 'GFX_rip_prosperity'):
    assert f'name = "{icon}"' in gfx
government_gui = read('interface/rip_ruthenian_powers.gui')
assert 'rip_kru_' not in government_gui
for power in old_balances:
    for key in (power, 'monthly_' + power, power + '_gain_modifier'):
        assert not (ROOT / f'gfx/interface/ideas_EU4/{key}.dds').exists(), key
assert 'kru_refresh_factional_court_effect = yes' in normalized(
    named_block(effects, 'kru_update_dominant_pair_effect')
)
assert 'kru_sync_reform_to_faction_effect = yes' in normalized(
    named_block(effects, 'kru_refresh_factional_court_effect')
)
for texture in re.findall(r'texturefile = "([^"]+)"',gfx):
    if texture.startswith('gfx/interface/rip_government/'):
        assert (ROOT/texture).is_file(), texture

for language in ('english','french','german','spanish'):
    seen = {}
    all_keys = set()
    for path in (ROOT/'localisation').rglob(f'*l_{language}.yml'):
        path_keys = re.findall(r'^ ([\w]+):\d+',path.read_text(encoding='utf-8-sig'),re.M)
        all_keys.update(path_keys)
        for key in path_keys:
            if key in loc:
                assert key not in seen, (key,seen.get(key),path)
                seen[key] = path
    assert set(loc) <= set(seen)
    assert {
        'hlc_boyar_council_session_cd',
        'lit_pany_rada_session_cd',
        'hlc_ordinance_cooldown_desc',
    } <= all_keys

for name in (
    'siversk_charter', 'siversk_towns', 'siversk_retinue', 'kyiv_snem',
    'kyiv_udil', 'kyiv_druzhyna',
):
    assert (ROOT/f'gfx/interface/rip_government/{name}.dds').is_file(), name
for name in ('rada', 'siversk_principality', 'knyazi', 'boyary', 'starshyna'):
    assert not (ROOT/f'gfx/interface/rip_government/{name}.dds').exists(), name
game = vanilla_root()
if game:
    widths = {}
    font = (game/'gfx/fonts/vic_18.fnt').read_text(encoding='latin-1')
    for code, advance in re.findall(r'char id=(\d+).*?xadvance=(-?\d+)',font):
        widths[chr(int(code))] = int(advance)
    labels = {k:v for k,v in loc.items() if (k.startswith('rip_parliament_') or k.startswith('ability_') or k in ids or k == 'chr_siversk_principality_reform' or k in ('siversk_confirm_patrimonies','siversk_charter_towns','siversk_muster_druzhyna','kyivan_throne_concord','kyivan_peoples_gathering'))}
    measured = [(k,len(v),sum(widths[c] for c in v)) for k,v in labels.items()]
    assert all(chars <= 28 and pixels <= 220 for _,chars,pixels in measured), measured
    print('NAME WIDTH PASS: vic_18; max',max(x[1] for x in measured),'characters;',max(x[2] for x in measured),'px; budget 220 px.')
print('RUTHENIAN GOVERNMENT UI PASS: exclusive states, costs, cooldowns, sprites, unique localisation and names.')

for tag, place in [('SMY','sumy'),('OKH','okhtyrka'),('KHK','kharkiv'),('IZM','izium')]:
    for gov in ('monarchy','republic'):
        assert parliament_name(tag,gov) == 'rip_parliament_'+place+'_regimental'
assert parliament_name('KIE','monarchy',['kyivan_cesarstvo_reform']) == 'rip_parliament_imperial_sobor'
