"""Source/UI contracts, not proof of engine rendering or campaign balance."""
import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

loc = dict(re.findall(r'^ ([\w]+):\d+ "(.*)"$',read('localisation/zzzz_rip_government_ui_l_english.yml'),re.M))
assert loc['kyivan_peoples_gathering'] == 'Concord of Peoples'
assert 'Prosperity' not in loc['kyivan_peoples_gathering_desc']
import importlib.util
spec = importlib.util.spec_from_file_location('build_kru_rada', ROOT/'tools/build_kru_rada.py')
rada = importlib.util.module_from_spec(spec); spec.loader.exec_module(rada)
reforms = read('common/government_reforms/RIP_KRU_rada_reforms.txt')
ids = list(rada.REFORM_IDS)          # the Rada of Three Estates: six ids, the first is the one a new Confederation starts with
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

# Parliament names (the window title overlay, the rules and the plain nouns) have their own contract: check_parliament_names.py.

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

# The Rada's six reforms, the pair logic, the bar and the junior voice: check_kru_rada.py executes them. The court buttons stay here.
effects = read('common/scripted_effects/kru_effects.txt')
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
for step in ('kru_rada_rank_effect', 'kru_rada_select_reform_effect', 'kru_rada_bar_effect', 'kru_apply_junior_blocs_effect'):
    assert f'{step} = yes' in normalized(named_block(effects, 'kru_refresh_factional_court_effect')), step
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
    } <= all_keys
    # The six crown ordinances have no engine cooldown any more (seen in EU4 1.37.5: one enacted ordinance put its cooldown on the other five),
    # so their cooldown name is retired.
    assert 'hlc_ordinance_cooldown_desc' not in all_keys

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
    labels = {k:v for k,v in loc.items() if (k.startswith('ability_') or k in ids or k == 'chr_siversk_principality_reform' or k in ('siversk_confirm_patrimonies','siversk_charter_towns','siversk_muster_druzhyna','kyivan_throne_concord','kyivan_peoples_gathering'))}
    measured = [(k,len(v),sum(widths[c] for c in v)) for k,v in labels.items()]
    assert all(chars <= 28 and pixels <= 220 for _,chars,pixels in measured), measured
    print('NAME WIDTH PASS: vic_18; max',max(x[1] for x in measured),'characters;',max(x[2] for x in measured),'px; budget 220 px.')
print('RUTHENIAN GOVERNMENT UI PASS: exclusive states, costs, cooldowns, sprites, unique localisation and names.')
