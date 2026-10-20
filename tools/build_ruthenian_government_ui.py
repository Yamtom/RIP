"""Build government sprites, native power widgets and owned localisation.

Raster artwork: checked-in imagegen sources; cropping/resizing is asset packaging.
English fallback strings in non-English languages are intentional, not translations.
"""
from pathlib import Path
import argparse
import sys
import re
from collections import deque
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_kru_rada import REFORM_IDS  # noqa: E402
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
         'concord','gathering','prosperity','rada','siversk_principality']

ICONS = [
    ('concord', 0, 3), ('gathering', 1, 3), ('prosperity', 1, 3),
    ('kyiv_levy', 2, 1), ('kyiv_rota', 3, 1), ('kyiv_grants', 0, 2),
    ('knyazi', 1, 2), ('boyary', 2, 2), ('starshyna', 3, 2),
    ('siversk_charter', 0, 0), ('siversk_towns', 0, 0),
    ('siversk_retinue', 0, 0), ('kyiv_snem', 0, 0),
    ('kyiv_udil', 0, 0), ('kyiv_druzhyna', 0, 0),
]
ART = {'siversk_charter': 'charter', 'siversk_towns': 'towns',
       'siversk_retinue': 'druzhyna', 'kyiv_snem': 'snem',
       'kyiv_udil': 'charter', 'kyiv_druzhyna': 'druzhyna',
       'kyiv_levy': 'druzhyna', 'kyiv_rota': 'snem',
       'kyiv_grants': 'charter', 'concord': 'concord', 'prosperity': 'prosperity'}
atlas = Image.open(ROOT/'gfx/interface/rip_government/source/atlas.png').convert('RGBA')
ROWS = (0, .25, .5, .732, 1)
sprites = []
preview = Image.new('RGB', (640, 180), '#16292b')
draw = ImageDraw.Draw(preview)
def remove_atlas_background(image):
    pixels = image.load()
    width, height = image.size
    background = pixels[0, 0][:3]
    visited = bytearray(width * height)
    pending = deque()

    def enqueue(x, y):
        index = y * width + x
        if not visited[index]:
            visited[index] = 1
            pending.append(index)

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(1, height - 1):
        enqueue(0, y)
        enqueue(width - 1, y)

    while pending:
        index = pending.popleft()
        x, y = index % width, index // width
        red, green, blue, alpha = pixels[x, y]
        if max(abs(red - background[0]), abs(green - background[1]),
               abs(blue - background[2])) > 24:
            continue
        pixels[x, y] = (red, green, blue, 0)
        if x:
            enqueue(x - 1, y)
        if x + 1 < width:
            enqueue(x + 1, y)
        if y:
            enqueue(x, y - 1)
        if y + 1 < height:
            enqueue(x, y + 1)
    return image

for i, (name, x, y) in enumerate(ICONS):
    tile = atlas.crop((round(x*atlas.width/4), round(ROWS[y]*atlas.height),
                       round((x+1)*atlas.width/4), round(ROWS[y+1]*atlas.height)))
    if name in ART:
        tile = Image.open(ROOT/f'gfx/interface/rip_government/source/{ART[name]}.png').convert('RGBA')
    else:
        tile = remove_atlas_background(tile)
    icon = tile.resize((72,72), Image.Resampling.LANCZOS)
    # Native 72x72 footprint; source PNG alpha is preserved for new emblems.
    if name not in ('knyazi', 'boyary', 'starshyna'):
        path = ROOT/f'gfx/interface/rip_government/{name}.dds'
        if ARGS.check:
            assert icon.getpixel((0, 0))[3] == 0
            assert Image.open(path).convert('RGBA').tobytes() == icon.tobytes(), path
        else:
            icon.save(path)
    preview_icon = icon.resize((64,64), Image.Resampling.LANCZOS)
    preview_x, preview_y = i % 4, i // 4
    preview.paste(preview_icon, (preview_x*160+48, preview_y*90),
                  preview_icon.getchannel('A'))
    draw.text((preview_x*160+6, preview_y*90+66), name, fill='#eed8ac')
    if name in ART:
        sprites.append(f'\tspriteType = {{ name = "GFX_rip_{name}" texturefile = "gfx/interface/rip_government/{name}.dds" noOfFrames = 1 norefcount = yes }}')
    if name in ('knyazi','boyary','starshyna'):
        faction = tile.resize((104,104),Image.Resampling.LANCZOS)
        faction_path = ROOT/f'gfx/interface/rip_government/faction_{name}.dds'
        if ARGS.check:
            assert Image.open(faction_path).convert('RGBA').tobytes() == faction.tobytes()
        else:
            faction.save(faction_path)
        sprites.append(f'\tspriteType = {{ name = "GFX_faction_kru_{name}" texturefile = "gfx/interface/rip_government/faction_{name}.dds" noOfFrames = 1 norefcount = yes }}')
        color = {'knyazi':'purple','boyary':'blue','starshyna':'red'}[name]
        sprites.append(f'\tspriteType = {{ name = "GFX_faction_bg_kru_{name}" texturefile = "gfx/interface/faction_{color}_frame.tga" transparencecheck = yes noOfFrames = 1 norefcount = yes }}')
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

OBSOLETE_ASSETS = [
    'gfx/interface/rip_government/rada.dds',
    'gfx/interface/rip_government/siversk_principality.dds',
    'gfx/interface/rip_government/knyazi.dds',
    'gfx/interface/rip_government/boyary.dds',
    'gfx/interface/rip_government/starshyna.dds',
    'gfx/interface/ideas_EU4/kru_knyazi_boyary_balance.dds',
    'gfx/interface/ideas_EU4/monthly_kru_knyazi_boyary_balance.dds',
    'gfx/interface/ideas_EU4/kru_knyazi_boyary_balance_gain_modifier.dds',
    'gfx/interface/ideas_EU4/kru_boyary_starshyna_balance.dds',
    'gfx/interface/ideas_EU4/monthly_kru_boyary_starshyna_balance.dds',
    'gfx/interface/ideas_EU4/kru_boyary_starshyna_balance_gain_modifier.dds',
    'gfx/interface/ideas_EU4/kru_knyazi_starshyna_balance.dds',
    'gfx/interface/ideas_EU4/monthly_kru_knyazi_starshyna_balance.dds',
    'gfx/interface/ideas_EU4/kru_knyazi_starshyna_balance_gain_modifier.dds',
]
for obsolete in OBSOLETE_ASSETS:
    path = ROOT / obsolete
    if ARGS.check:
        assert not path.exists(), f'Obsolete: {path}'
    elif path.exists():
        path.unlink()
gui = ['guiTypes = {']
for widget, icon, label in [('rip_throne_concord_power','concord','kyivan_throne_concord'),
                            ('rip_peoples_gathering_power','prosperity','kyivan_peoples_gathering')]:
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
 'siversk_confirm_patrimonies_desc':'Confirm the landed houses in their inherited rights. For 50 administrative power, gain 10 years of lower unrest and noble loyalty, at the cost of tax revenue. If Town Charters are active, reconciles estates and grants legitimacy; if the Druzhyna is mustered, supplies manpower. Cooldown: 10 years.',
 'siversk_charter_towns':'Charter the Towns',
 'siversk_charter_towns_desc':'Settle trade privileges with the towns. For 50 diplomatic power, gain 10 years of trade efficiency and burgher loyalty while reducing noble influence. If a Patrimonial Compact is active, grants customs income; if the Druzhyna is mustered, reduces war exhaustion. Cooldown: 10 years.',
 'siversk_muster_druzhyna':'Muster the Druzhyna',
 'siversk_muster_druzhyna_desc':'Call the prince\'s retinue into service. For 50 military power, gain 5 years of manpower recovery and army morale, with higher army maintenance. If a Patrimonial Compact is active, adds army tradition; if Town Charters are active, grants income. Cooldown: 10 years.',
 'rip_siversk_patrimonial_compact':'Patrimonial Compact',
 'rip_siversk_town_compact':'Town Charters',
 'rip_siversk_retinue_muster':'Druzhyna Muster',
 'desc_rip_siversk_patrimonial_compact':'The landed houses uphold the prince in exchange for confirmation of their inherited rights and a lighter tax burden.',
 'desc_rip_siversk_town_compact':'Town charters secure merchant cooperation and diminish the landed houses\' influence over trade.',
 'desc_rip_siversk_retinue_muster':'The prince\'s retinue is assembled for service. Maintaining its readiness raises the cost of the army.',
 'ability_kyivan_throne_concord_mechanic':'Throne Concord',
 'kyivan_throne_concord':'Throne Concord',
 'kyivan_throne_concord_desc':'§YThrone Concord: 0-100§!\\nHigher concord reduces the penalties to legitimacy, stability cost, advisors, coring and governing capacity.\\n\\n§YBelow 33:§! +2 unrest, -5 maximum absolutism.\\n§Y33-66:§! +1 unrest.\\n§YAbove 66:§! +5 maximum absolutism, +1 diplomatic reputation.\\n\\n§GGrowth:§! ruler administrative skill, stability at least 2, legitimacy at least 80, peace, religious unity at least 80%.\\n§RDecline:§! negative stability, legitimacy below 40, war exhaustion at least 5, any subject with at least 50% liberty desire.\\nAt 100: +10 prestige and +5 legitimacy. At 0: Throne in Disarray for 10 years. Hover the bar for current value, monthly change and active modifiers.',
 'ability_kyivan_peoples_gathering_mechanic':'Gathering of the Peoples',
 'kyivan_peoples_gathering':'Gathering of the Peoples',
 'kyivan_peoples_gathering_desc':'§YGathering of the Peoples: 0-100§!\\nThis measures how firmly the realm\'s peoples are gathered into the Kyivan polity.\\n\\n§GAt 100:§! +15 prestige and the permanent Peoples Gathered modifier: -2 unrest, +5% national tax, -10% stability cost. The bar resets to 0. The modifier is refreshed, not stacked. This does not accept cultures or change their slots.\\n\\n§GGrowth:§! development, peace, stability at least 2, legitimacy at least 70, religious unity at least 80%.\\n§RDecline:§! primary culture outside the East Slavic group, negative stability, religious unity below 50%, war exhaustion at least 5. Hover the bar for current value and monthly change.',
 'monthly_kyivan_peoples_gathering':'Monthly Gathering of the Peoples',
 'kyivan_peoples_gathering_gain_modifier':'Gathering of the Peoples Gain',
 'kru_knyazi':'Knyazi', 'kru_boyary':'Boyary', 'kru_starshyna':'Starshyna',
 'kru_knyazi_FACTION_DESC':'The princely houses defend dynastic standing, diplomacy and the service of dependent princes.\\n\\nTheir influence receives a yearly boost from legitimacy of at least 60 and from having at least two subjects. Court the Knyazi to spend 50 diplomatic power for 25 influence and 2 legitimacy. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_boyary_FACTION_DESC':'The boyar houses seek office, landed rights and control of the treasury.\\n\\nTheir influence receives a yearly boost from stability of at least 2 and a treasury of at least 300 ducats. Court the Boyary to spend 50 administrative power for 25 influence and 50 ducats. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_starshyna_FACTION_DESC':'The Cossack officers defend military service, regimental appointments and the rights of the host.\\n\\nTheir influence receives a yearly boost from army tradition of at least 40 and from war. Court the Starshyna to spend 50 military power for 25 influence and 5 army tradition. Cooldown: 6 years; unavailable at 70 influence.',
 'kru_knyazi_influence':'Knyazi Influence','kru_boyary_influence':'Boyary Influence','kru_starshyna_influence':'Starshyna Influence',
 'ability_ruthenian_factional_court_mechanic':'Council of Three Estates',
 'ruthenian_factional_pair_system_tt':'The faction in power leads the rada. The faction that is second by influence stands on the left of the States General bar and the leader on the right; the bar moves right with the leader\'s influence (50, 55, 60). The runner-up keeps a junior voice from 38 influence. The pair is checked every month and after every court ability.',
 'ruthenian_factional_influence_sources_tt':'Yearly influence: Knyazi gain from legitimacy of at least 60 and at least two subjects; Boyary from stability of at least 2 and 300 ducats; Starshyna from army tradition of at least 40 and war. Council abilities also add influence.',
 # Parliament names are generated by tools/build_parliament_names.py (title overlay, plain nouns).
 'kyivan_veche_reform':'Kyivan Veche Republic',
 'kyivan_veche_reform_desc':'The town assembly elects a posadnik in place of a prince; merchants and lineages speak in the veche, and the office answers to a term, not a bloodline.',
 'kyivan_boyar_republic_reform':'Kyivan Boyar Rada',
 'kyivan_boyar_republic_reform_desc':'The veche\'s yearly muster hardens into a standing council of boyar lineages, traders, and guildsmen, each with a settled voice in the city\'s rule.',
}
for key in REFORM_IDS:
    COPY[key] = 'Rada of Three Estates'
    COPY[key+'_desc'] = ('The rada is three blocs - the Knyazi, the Boyary and the Starshyna - and the two that lead it stand on the States General bar '
                         '(Res Publica or Winds of Change): the second by influence on the left, the dominant bloc on the right. The bar moves right with '
                         'the leader\'s influence at 50, 55 and 60, and the bloc on the left keeps a junior voice from 38.')
for power, name in [('kyiv_princely_levy_power','Princely Levy'),('kyiv_seat_rotation_power','Seat Rotation'),('kyiv_grant_reconfirmation_power','Grant Renewal')]:
    COPY[power] = name
    COPY[power+'_desc'] = {'Princely Levy':'Accumulates from the ruler\'s military skill. Spend 100 to call the senior udils\' levy. Persists on succession.', 'Seat Rotation':'Accumulates from the ruler\'s diplomatic skill. Spend 100 to rotate a restless senior udil. Persists on succession.', 'Grant Renewal':'Accumulates from the ruler\'s administrative skill. Spend 80 to renew lapsed senior-udil grants. Resets on succession.'}[name]
    COPY['monthly_'+power] = 'Monthly '+name
    COPY[power+'_gain_modifier'] = name+' Gain'
COPY.update({
 'kyivan_peoples_gathering': 'Concord of Peoples',
 'ability_kyivan_peoples_gathering_mechanic': 'Concord of Peoples',
 'monthly_kyivan_peoples_gathering': 'Monthly Concord of Peoples',
 'kyivan_peoples_gathering_gain_modifier': 'Concord of Peoples Gain',
 'kyivan_peoples_gathering_desc': 'Requires at least 10% of owned development in non-primary cultures, an owned province of an accepted non-primary culture and at least one promoted culture. Cultural development shares refresh monthly.\\nMonthly growth: +0.30 when eligible; +0.15 with three promoted cultures; +0.15 with at least 30% non-primary development; +0.10 with Throne Concord at least 60. Loss: -0.25 at 15% unaccepted development, a further -0.35 at 30%; -0.20 below 30 Throne Concord; -0.15 at 5 war exhaustion; -0.50 when ineligible.\\nAt 100: renew Peoples Gathered for 10 years, gain 10 prestige and 10 Throne Concord, reset to 40. Below 20 with at least 30% unaccepted development: one court crisis per breakdown, -15 Throne Concord and Throne in Disarray for 5 years. Rearms after reaching 40 and reducing unaccepted development below 15%.',
 'kyivan_throne_concord_desc': 'Throne Concord starts at 50. Monthly base +0.10; stability at least 2: +0.10; negative stability: -0.20; legitimacy at least 80: +0.20; below 40: -0.25; a subject at 50 liberty desire: -0.30. Eligible Concord of Peoples at 60: +0.15; unaccepted cultural development at 30%: -0.30.\\nLow concord scales legitimacy, stability-cost and advisor-cost penalties. At zero: Throne in Disarray for 5 years. At 100 there is no repeatable prestige reward.',
})

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
    emit(f'localisation/zzzz_rip_government_ui_l_{language}.yml',text,bom=True)
print('RUTHENIAN UI PASS: sprites, panels and localisation are current.')
