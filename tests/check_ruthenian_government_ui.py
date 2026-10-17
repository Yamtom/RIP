"""Source/UI contracts, not proof of engine rendering or campaign balance."""
import re
from pathlib import Path
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, vanilla_root

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
    assert parliament_name(tag,'republic') == 'rip_parliament_viche'
    assert parliament_name(tag,'monarchy') == 'rip_parliament_estates'
for active in ids:
    assert parliament_name('KRU','monarchy',[active]) == 'rip_parliament_three'
for tag,gov,reform,want in [('KIE','monarchy','kyivan_shogunate_reform','snem'),
                           ('CHR','monarchy','chr_siversk_principality_reform','boyar'),
                           ('HLC','monarchy','hlc_crown_and_sejm_reform','sejm'),
                           ('VLN','republic','vln_sejmik_republic_reform','sejmik'),
                           ('UZH','republic','uzh_republican_komitat_system_reform','komitat'),
                           ('LIT','monarchy','lit_pany_rada_reform','pany'),
                           ('HET','monarchy','het_starshyna_oligarchy_reform','officers'),
                           ('HET','republic','','general'),('ZAZ','republic','','sich')]:
    assert parliament_name(tag,gov,[reform]) == 'rip_parliament_'+want

for power in ('kyivan_throne_concord','kyivan_peoples_gathering','kyiv_princely_levy_power','kyiv_seat_rotation_power','kyiv_grant_reconfirmation_power'):
    for key in (power,'monthly_'+power,power+'_gain_modifier'):
        assert (ROOT/f'gfx/interface/ideas_EU4/{key}.dds').read_bytes()[:4] == b'DDS '

siversk = named_block(read('common/government_reforms/RIP_CHR_government_reforms.txt'),'chr_siversk_principality_reform')
assert 'russian_mechanic' not in siversk and 'weaker_russian_ability' not in siversk
assert 'siversk_patrimony_mechanic' in siversk
mechanic = read('common/government_mechanics/rip_siversk_patrimony.txt')
for action, power in [('confirm_patrimonies','adm'),('charter_towns','dip'),('muster_druzhyna','mil')]:
    block = named_block(mechanic,'siversk_'+action)
    assert f'{power}_power = 50' in named_block(block,'trigger')
    assert f'add_{power}_power = -50' in named_block(block,'effect')
    assert 'cooldown_years = 10' in block
    assert 'has_country_modifier' in named_block(block,'trigger')

gfx = read('interface/rip_ruthenian_government.gfx')
for faction in ('knyazi','boyary','starshyna'):
    assert f'GFX_faction_kru_{faction}"' in gfx
    assert f'GFX_faction_bg_kru_{faction}"' in gfx
    assert loc[f'kru_{faction}_FACTION_DESC']
for file in ('rip_siversk_patrimony','rip_kyivan_seniority','rip_kyivan_seniorate','rip_ruthenian_factional_court'):
    text = read(f'common/government_mechanics/{file}.txt')
    for icon in re.findall(r'^\s*icon = (\w+)',text,re.M):
        assert f'"{icon}"' in gfx, icon
        assert icon.startswith('GFX_rip_')
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
