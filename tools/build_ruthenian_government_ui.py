"""Build government sprites, native power widgets and owned localisation.

Raster artwork: checked-in imagegen atlas; cropping/resizing is asset packaging.
English fallback strings in non-English languages are intentional, not translations.
"""
from pathlib import Path
import argparse
import re
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CHECK = argparse.ArgumentParser()
CHECK.add_argument('--check', action='store_true')
ARGS = CHECK.parse_args()

def emit(path, data, bom=False):
    path = ROOT / path
    payload = (('\ufeff' if bom else '') + data).encode('utf-8')
    if ARGS.check:
        assert path.read_bytes() == payload, f'Stale: {path}'
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

NAMES = ['siversk_charter','siversk_towns','siversk_retinue','kyiv_snem',
         'kyiv_udil','kyiv_druzhyna','kyiv_levy','kyiv_rota',
         'kyiv_grants','knyazi','boyary','starshyna',
         'concord','prosperity','rada','siversk_principality']
atlas = Image.open(ROOT/'gfx/interface/rip_government/source/atlas.png').convert('RGBA')
# Reviewed source artwork has a slightly shorter third row. Keep the next
# row's throne finials out of the tenure/faction crops.
ROWS = (0, .25, .5, .732, 1)
sprites = []
preview = Image.new('RGB', (640, 360), '#16292b')
draw = ImageDraw.Draw(preview)
for i, name in enumerate(NAMES):
    x, y = i % 4, i // 4
    tile = atlas.crop((round(x*atlas.width/4), round(ROWS[y]*atlas.height),
                       round((x+1)*atlas.width/4), round(ROWS[y+1]*atlas.height)))
    tile = tile.resize((72,72), Image.Resampling.LANCZOS)
    # Native interaction buttons are single images; engine supplies hover/disabled states.
    path = ROOT/f'gfx/interface/rip_government/{name}.dds'
    if ARGS.check:
        assert Image.open(path).convert('RGBA').tobytes() == tile.tobytes(), path
    else:
        tile.save(path)
    preview.paste(tile.resize((64,64),Image.Resampling.LANCZOS), (x*160+48,y*90))
    draw.text((x*160+6,y*90+66),name,fill='#eed8ac')
    sprites.append(f'\tspriteType = {{ name = "GFX_rip_{name}" texturefile = "gfx/interface/rip_government/{name}.dds" }}')
    if name in ('knyazi','boyary','starshyna'):
        faction = tile.resize((104,104),Image.Resampling.LANCZOS)
        faction_path = ROOT/f'gfx/interface/rip_government/faction_{name}.dds'
        if ARGS.check:
            assert Image.open(faction_path).convert('RGBA').tobytes() == faction.tobytes()
        else:
            faction.save(faction_path)
        sprites.append(f'\tspriteType = {{ name = "GFX_faction_kru_{name}" texturefile = "gfx/interface/rip_government/faction_{name}.dds" }}')
        color = {'knyazi':'purple','boyary':'blue','starshyna':'red'}[name]
        sprites.append(f'\tspriteType = {{ name = "GFX_faction_bg_kru_{name}" texturefile = "gfx/interface/faction_{color}_frame.tga" transparencecheck = yes }}')
sprites.append('\tspriteType = { name = "government_reform_rip_siversk_principality" texturefile = "gfx/interface/rip_government/siversk_principality.dds" noOfFrames = 1 norefcount = yes }')
for power, icon in [('kyivan_throne_concord','concord'),('kyivan_peoples_gathering','prosperity'),
                    ('kyiv_princely_levy_power','kyiv_levy'),('kyiv_seat_rotation_power','kyiv_rota'),
                    ('kyiv_grant_reconfirmation_power','kyiv_grants')]:
    for key in (power,'monthly_'+power,power+'_gain_modifier'):
        # EU4 creates modifier sprites from the ideas_EU4 filename convention.
        # Supply the actual files rather than relying on a hand-named alias.
        modifier_icon = Image.open(ROOT/f'gfx/interface/rip_government/{icon}.dds').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS)
        modifier_path = ROOT/f'gfx/interface/ideas_EU4/{key}.dds'
        if ARGS.check:
            assert Image.open(modifier_path).convert('RGBA').tobytes() == modifier_icon.tobytes()
        else:
            modifier_path.parent.mkdir(parents=True,exist_ok=True)
            modifier_icon.save(modifier_path)
emit('interface/rip_ruthenian_government.gfx','spriteTypes = {\n'+'\n'.join(sprites)+'\n}\n')
if not ARGS.check:
    preview.save(ROOT/'gfx/interface/rip_government/source/preview.png')

gui = ['guiTypes = {']
for widget, icon, label in [('rip_throne_concord_power','concord','kyivan_throne_concord'),
                            ('rip_peoples_prosperity_power','prosperity','kyivan_peoples_gathering')]:
    gui.append(f''' windowType = {{
  name = "{widget}"
  size = {{ x = 300 y = 58 }}
  moveable = 0
  iconType = {{ name = "emblem" spriteType = "GFX_rip_{icon}" position = {{ x = 0 y = 2 }} scale = 0.5 }}
  instantTextBoxType = {{ name = "label" position = {{ x = 38 y = 0 }} font = "vic_18" text = "{label}" maxWidth = 250 maxHeight = 22 format = left }}
  iconType = {{ name = "government_power_bar" spriteType = "GFX_single_government_power_bar" position = {{ x = 35 y = 31 }} }}
  iconType = {{ name = "government_power_bar_frame" spriteType = "GFX_single_government_power_bar_frame" position = {{ x = 24 y = 28 }} alwaystransparent = yes }}
 }}''')
gui.append('}')
emit('interface/rip_ruthenian_powers.gui','\n'.join(gui)+'\n')

COPY = {
 'ability_siversk_patrimony_mechanic':'Siversk Patrimony',
 'chr_siversk_principality_reform':'Siversk Principality',
 'chr_siversk_principality_reform_desc':'A patrimonial principality rooted in the Siversk land. The prince maintains service through inherited rights, agreements with the towns and the muster of his druzhyna.',
 'siversk_confirm_patrimonies':'Confirm Patrimonies',
 'siversk_confirm_patrimonies_desc':'Confirm the landed houses in their inherited rights. For 50 administrative power, gain 10 years of lower unrest and greater noble loyalty, at the cost of tax revenue. Cooldown: 10 years.',
 'siversk_charter_towns':'Charter the Towns',
 'siversk_charter_towns_desc':'Settle trade privileges with the towns. For 50 diplomatic power, gain 10 years of trade efficiency and burgher loyalty while reducing noble influence. Cooldown: 10 years.',
 'siversk_muster_druzhyna':'Muster the Druzhyna',
 'siversk_muster_druzhyna_desc':'Call the prince\'s retinue into service. For 50 military power, gain 5 years of manpower recovery and army morale, with higher army maintenance. Cooldown: 10 years.',
 'rip_siversk_patrimonial_compact':'Patrimonial Compact',
 'rip_siversk_town_compact':'Town Charters',
 'rip_siversk_retinue_muster':'Druzhyna Muster',
 'desc_rip_siversk_patrimonial_compact':'The landed houses uphold the prince in exchange for confirmation of their inherited rights and a lighter tax burden.',
 'desc_rip_siversk_town_compact':'Town charters secure merchant cooperation and diminish the landed houses\' influence over trade.',
 'desc_rip_siversk_retinue_muster':'The prince\'s retinue is assembled for service. Maintaining its readiness raises the cost of the army.',
 'ability_kyivan_throne_concord_mechanic':'Throne Concord',
 'kyivan_throne_concord':'Throne Concord',
 'kyivan_throne_concord_desc':'§YThrone Concord: 0-100§!\\nHigher concord reduces the penalties to legitimacy, stability cost, advisors, coring and governing capacity.\\n\\n§YBelow 33:§! +2 unrest, -5 maximum absolutism.\\n§Y33-66:§! +1 unrest.\\n§YAbove 66:§! +5 maximum absolutism, +1 diplomatic reputation.\\n\\n§GGrowth:§! ruler administrative skill, stability at least 2, legitimacy at least 80, peace, religious unity at least 80%.\\n§RDecline:§! negative stability, legitimacy below 40, war exhaustion at least 5, any subject with at least 50% liberty desire.\\nAt 100: +10 prestige and +5 legitimacy. At 0: Throne in Disarray for 10 years. Hover the bar for current value, monthly change and active modifiers.',
 'ability_kyivan_peoples_gathering_mechanic':'People\'s Prosperity',
 'kyivan_peoples_gathering':'People\'s Prosperity',
 'kyivan_peoples_gathering_desc':'§YPeople\'s Prosperity: 0-100§!\\nThis measures the realm\'s internal consolidation.\\n\\n§GAt 100:§! +15 prestige and the permanent Peoples Gathered modifier: -2 unrest, +5% national tax, -10% stability cost. The bar resets to 0. The modifier is refreshed, not stacked. This does not accept cultures or change their slots.\\n\\n§GGrowth:§! development, peace, stability at least 2, legitimacy at least 70, religious unity at least 80%.\\n§RDecline:§! primary culture outside the East Slavic group, negative stability, religious unity below 50%, war exhaustion at least 5. Hover the bar for current value and monthly change.',
 'monthly_kyivan_peoples_gathering':'Monthly People\'s Prosperity',
 'kyivan_peoples_gathering_gain_modifier':'People\'s Prosperity Gain',
 'kru_knyazi':'Knyazi', 'kru_boyary':'Boyary', 'kru_starshyna':'Starshyna',
 'kru_knyazi_FACTION_DESC':'The princely houses defend dynastic standing, diplomacy and the service of dependent princes.\\n\\nTheir influence receives a yearly boost from legitimacy of at least 60 and from having at least two subjects. Court the Knyazi to spend 50 diplomatic power for 25 influence and 2 legitimacy. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_boyary_FACTION_DESC':'The boyar houses seek office, landed rights and control of the treasury.\\n\\nTheir influence receives a yearly boost from stability of at least 2 and a treasury of at least 300 ducats. Court the Boyary to spend 50 administrative power for 25 influence and 50 ducats. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_starshyna_FACTION_DESC':'The Cossack officers defend military service, regimental appointments and the rights of the host.\\n\\nTheir influence receives a yearly boost from army tradition of at least 40 and from war. Court the Starshyna to spend 50 military power for 25 influence and 5 army tradition. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_knyazi_influence':'Knyazi Influence','kru_boyary_influence':'Boyary Influence','kru_starshyna_influence':'Starshyna Influence',
 'ability_ruthenian_factional_court_mechanic':'Council of Three Estates',
 'ruthenian_factional_pair_system_tt':'The leading faction grants its full modifiers. Other blocs with at least 38 influence receive a junior voice. Coalition changes are checked yearly, with a 5-year cooldown.',
 'ruthenian_factional_influence_sources_tt':'Yearly influence: Knyazi gain from legitimacy of at least 60 and at least two subjects; Boyary from stability of at least 2 and 300 ducats; Starshyna from army tradition of at least 40 and war. Council abilities also add influence.',
 'rip_parliament_viche':'Viche','rip_parliament_boyar':'Boyar Rada',
 'rip_parliament_sobor':'Sobor','rip_parliament_general':'General Military Rada',
 'rip_parliament_officers':'Starshyna Rada','rip_parliament_sich':'Sich Rada',
 'rip_parliament_three':'Rada of Three Estates','rip_parliament_snem':'Princely Snem',
 'rip_parliament_estates':'Rada of the Land','rip_parliament_pany':'Pany-Rada',
 'rip_parliament_sejm':'Sejm','rip_parliament_sejmik':'Sejmik',
 'rip_parliament_komitat':'Komitat Assembly','rip_parliament_seimas':'Seimas',
}
for suffix in ('','_princes_hetmans','_boyars_hetmans'):
    key = 'ruthenian_factional_empire'+suffix+'_reform'
    COPY[key] = 'Rada of Three Estates'
    COPY[key+'_desc'] = 'Princes, boyars and Cossack officers compete in one rada. The leading faction provides its full modifiers; other blocs with at least 38 influence retain a junior voice. The ruling coalition changes through faction influence, not by selecting a separate reform.'
for power, name in [('kyiv_princely_levy_power','Princely Levy'),('kyiv_seat_rotation_power','Seat Rotation'),('kyiv_grant_reconfirmation_power','Grant Renewal')]:
    COPY[power] = name
    COPY[power+'_desc'] = {'Princely Levy':'Accumulates from the ruler\'s military skill. Spend 100 to call the senior udils\' levy. Persists on succession.', 'Seat Rotation':'Accumulates from the ruler\'s diplomatic skill. Spend 100 to rotate a restless senior udil. Persists on succession.', 'Grant Renewal':'Accumulates from the ruler\'s administrative skill. Spend 80 to renew lapsed senior-udil grants. Resets on succession.'}[name]
    COPY['monthly_'+power] = 'Monthly '+name
    COPY[power+'_gain_modifier'] = name+' Gain'

TAGS = 'KIE KRU UKR RUT CHR VLN HLC UZH PRL PDL ODS ZAZ HET KUY RPS SMY OKH IZM KHK ZLK SRK MSK TRV VTB MSL BLR PLT LIT'.split()
for tag in TAGS:
    COPY[tag+'_parliament_name'] = '[Root.GetRIPParliamentName]'
for culture in ('ruthenian','ruthenian_new','rusyn','rusyn_new','rusyn_new_new','severian','severian_new'):
    COPY[culture+'_parliament_name'] = '[Root.GetRIPParliamentName]'

# Migrate existing keys out of hand-authored files and their English fallbacks.
for path in sorted((ROOT/'localisation').rglob('*.yml')):
    if path.name.startswith('zzzz_rip_government_ui_'):
        continue
    old = path.read_text(encoding='utf-8-sig')
    lines = []
    for line in old.splitlines(keepends=True):
        match = re.match(r'\s*([^\s:]+):\d+\s',line)
        if not match or match[1] not in COPY:
            lines.append(line)
    new = ''.join(lines)
    if old != new:
        emit(str(path.relative_to(ROOT)),new,bom=True)
for language in ('english','french','german','spanish'):
    text = 'l_'+language+':\n # Generated by tools/build_ruthenian_government_ui.py; English fallback where untranslated.\n'
    text += ''.join(f' {key}:0 "{value}"\n' for key,value in COPY.items())
    emit(f'localisation/replace/zzzz_rip_government_ui_l_{language}.yml',text,bom=True)
print('RUTHENIAN UI PASS: sprites, power widgets and localisation are current.')
