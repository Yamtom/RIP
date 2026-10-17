"""Source/UI contracts, not proof of engine rendering or campaign balance."""
import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

loc = dict(re.findall(r'^ ([\w]+):\d+ "(.*)"$',read('localisation/replace/zzzz_rip_government_ui_l_english.yml'),re.M))
assert loc['kyivan_peoples_gathering'] == 'Gathering of the Peoples'
assert 'Prosperity' not in loc['kyivan_peoples_gathering_desc']
reforms = read('common/government_reforms/RIP_KIE_KRU_government_reforms.txt')
ids = ['ruthenian_factional_empire'+s+'_reform' for s in ('','_princes_hetmans','_boyars_hetmans')]
assert len({loc[i] for i in ids}) == 1

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

for power in ('kyivan_throne_concord','kyivan_peoples_gathering','kyiv_princely_levy_power','kyiv_seat_rotation_power','kyiv_grant_reconfirmation_power',
              'kru_knyazi_boyary_balance','kru_boyary_starshyna_balance','kru_knyazi_starshyna_balance'):
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
balance_powers = named_block(court,'powers')
pairs = (
    ('kru_knyazi_boyary_balance','kru_knyazi','kru_boyary','rip_kru_knyazi_boyary_balance_power'),
    ('kru_boyary_starshyna_balance','kru_boyary','kru_starshyna','rip_kru_boyary_starshyna_balance_power'),
    ('kru_knyazi_starshyna_balance','kru_knyazi','kru_starshyna','rip_kru_knyazi_starshyna_balance_power'),
)
for power, left, right, widget in pairs:
    block = named_block(balance_powers,power)
    clean = normalized(block)
    assert f'gui = {widget}' in clean and 'default = 50' in clean
    assert f'faction = {left} influence = 60' in clean
    assert f'faction = {right} influence = 60' in clean
    assert f'monthly_{power} = -0.25' in clean
    assert f'monthly_{power} = 0.25' in clean
    low, high = normalized(named_block(block,'on_min_reached')), normalized(named_block(block,'on_max_reached'))
    assert f'faction = {left} influence = 6' in low
    assert f'faction = {right} influence = -6' in low
    assert f'faction = {right} influence = 6' in high
    assert f'faction = {left} influence = -6' in high
    assert f'power_type = {power} value = 50' in low
    assert f'power_type = {power} value = 50' in high

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
        'GFX_rip_kyiv_levy',
        'GFX_rip_kyiv_rota',
        'GFX_rip_kyiv_grants',
    ],
    'rip_ruthenian_factional_court': [
        'GFX_cossacks_ability_DIP',
        'GFX_cossacks_ability_ADM',
        'GFX_cossacks_ability_MIL',
    ],
}
for file, expected in expected_ability_icons.items():
    text = read(f'common/government_mechanics/{file}.txt')
    assert re.findall(r'^\s*icon = (\w+)', text, re.M) == expected
assert 'government_reform_rip_siversk_principality' not in gfx
for icon in ('GFX_rip_concord', 'GFX_rip_prosperity'):
    assert f'name = "{icon}"' in gfx
government_gui = read('interface/rip_ruthenian_powers.gui')
for index, (power, left, right, widget) in enumerate(pairs, 3):
    window = named_block(government_gui,'windowType',occurrence=index)
    assert f'name = "{widget}"' in window
    assert f'GFX_faction_kru_{left[4:]}' in window and f'GFX_faction_kru_{right[4:]}' in window
    assert f'GFX_faction_bg_kru_{left[4:]}' in window and f'GFX_faction_bg_kru_{right[4:]}' in window
    assert 'name = "government_power_bar"' in window
    assert 'name = "government_power_bar_frame"' in window
assert 'kru_sync_reform_to_faction_effect = yes' in normalized(
    named_block(read('common/scripted_effects/kru_effects.txt'),'kru_update_dominant_pair_effect')
)
for texture in re.findall(r'texturefile = "([^"]+)"',gfx):
    if texture.startswith('gfx/interface/rip_government/'):
        assert (ROOT/texture).is_file(), texture

for language in ('english','french','german','spanish'):
    seen = {}
    for path in (ROOT/'localisation').rglob(f'*l_{language}.yml'):
        for key in re.findall(r'^ ([\w]+):\d+',path.read_text(encoding='utf-8-sig'),re.M):
            if key in loc:
                assert key not in seen, (key,seen.get(key),path)
                seen[key] = path
    assert set(loc) <= set(seen)

for name in (
    'siversk_charter', 'siversk_towns', 'siversk_retinue', 'kyiv_snem',
    'kyiv_udil', 'kyiv_druzhyna', 'rada', 'siversk_principality',
    'knyazi', 'boyary', 'starshyna',
):
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
