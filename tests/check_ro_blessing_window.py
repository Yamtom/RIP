"""Native Orthodox mechanics and balance contract, independent of EU4 runtime."""
from decimal import Decimal
from pathlib import Path
import os
import re
import struct
import subprocess
import sys
import tempfile
from church_testlib import World, parse
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root

icons = ('michael', 'eleusa', 'pancreator', 'nicholas')
faith = read('common/religions/russian_orthodox.txt')
assert (ROOT / 'interface/countryreligionview.gui').exists()
assert not (ROOT / 'interface/blessings.gui').exists()
for forbidden in ('fervor = yes', 'holy_sites =', 'blessings =', 'uses_piety ='):
    assert forbidden not in normalized(faith), forbidden
assert 'has_patriarchs = yes' in faith
assert 'misguided_heretic = yes' in faith

# Snapshot of EU4 1.37.5. Verified against the install below when available.
baseline = {
    'country': {'stability_cost_modifier': '-0.1', 'tolerance_own': '1'},
    'michael': {'discipline': '0.05', 'manpower_recovery_speed': '0.1'},
    'eleusa': {'global_unrest': '-3', 'harsh_treatment_cost': '-0.25'},
    'pancreator': {'development_cost': '-0.1', 'build_cost': '-0.1'},
    'nicholas': {'improve_relation_modifier': '0.25', 'ae_impact': '-0.1'},
}
def payload(block):
    # Modifier scalars before the first nested allow/visible/AI block.
    inside = block[block.index('{') + 1:]
    inside = re.split(r'\b(?:allow|visible|ai_will_do)\s*=', inside)[0]
    inside = re.sub(r'#.*', '', inside)
    return {k: Decimal(v) for k,v in re.findall(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)', inside)}

# Only target-version data may refresh this snapshot; 1.30 is a donor.
install = vanilla_root()
if install is not None:
    vanilla_path = install / 'common/religions/00_religion.txt'
    vanilla = named_block(vanilla_path.read_text(encoding='utf-8-sig'), 'orthodox')
    for name, values in baseline.items():
        block = named_block(vanilla, 'country' if name == 'country' else 'icon_' + name)
        assert payload(block) == {k: Decimal(v) for k,v in values.items()}, name
    defines = (install / 'common/defines.lua').read_text(encoding='utf-8-sig')
    assert re.search(r'ORTHODOX_ICON_DURATION_MONTHS\s*=\s*240', defines)
    assert re.search(r'ORTHODOX_ICON_AUTHORITY_COST\s*=\s*0\.1', defines)
    print('PASS: balance baseline and icon cost/duration match installed vanilla')
assert payload(named_block(faith, 'country')) == {
    'stability_cost_modifier': Decimal('-.05'), 'tolerance_own': Decimal('.5')}
for name in icons:
    old = named_block(faith, 'rip_ro_native_' + name)
    assert all(v == 0 for v in payload(old).values())
    assert 'always = no' in named_block(old, 'allow')

native = named_block(faith, 'orthodox_icons')
assert re.findall(r'(?m)^\s*(rip_ro_native_\w+)\s*=\s*\{', native) == [
    *('rip_ro_native_' + name for name in icons), 'rip_ro_native_retired_climacus']
for name in icons:
    assert 'always = no' in named_block(named_block(native, 'rip_ro_native_' + name), 'visible')
assert 'always = no' in named_block(named_block(native, 'rip_ro_native_retired_climacus'), 'visible')
assert 'rip_ro_select_' not in read('decisions/RIP_OrthodoxIcons.txt')

cleanup = read('common/scripted_effects/rip_ro_icon_effects.txt')
for name in (*icons, 'climacus'):
    assert 'remove_country_modifier = rip_ro_icon_' + name in cleanup
    assert payload(named_block(read('common/event_modifiers/RIP_faith_modifiers.txt'), 'rip_ro_icon_' + name)) == {'discipline': 0}
for name in ('sobor_of_war', 'sobor_of_the_market', 'sobor_of_the_canons'):
    assert 'remove_active_fervor = ' + name in cleanup
    retired = named_block(read('common/fervor/RIP_sobor_fervor.txt'), name)
    assert 'always = no' in named_block(retired, 'potential')
    assert payload(named_block(retired, 'effect')) == {'discipline': 0}
for _, blessing in keyed_blocks(read('common/church_aspects/RIP_ro_holy_blessings.txt'), 'modifier'):
    assert payload(blessing) == {'discipline': 0}
hooks = read('common/on_actions/RIP_religion_russian_orthodox_on_actions.txt')
assert 'rip_ro_icon_upkeep_effect = yes' in named_block(hooks, 'on_startup')
assert 'rip_ro_icon_upkeep_effect = yes' in named_block(hooks, 'on_religion_change')
assert 'country_event =' not in read('events/RIP_OrthodoxAuthority.txt').split('immediate =')[1]

decision = read('decisions/RIP_OrthodoxHolyCities.txt')
assert 'rip_ro_holy_city_register' not in decision, 'the register decision is retired in favor of the UI button'
assert not (ROOT / 'events/RIP_OrthodoxHolyCities.txt').exists(), 'the old event-popup route must be retired'

controls = read('common/custom_gui/RIP_church_controls.txt')
gui = read('interface/countryreligionview.gui')
panels_gfx = read('interface/RIP_church_panels.gfx')
site_localisation = read('localisation/rip_ro_blessing_window_l_english.yml')
custom_loc = read('customizable_localization/rip_ro_holy_cities_custom_loc.txt')
church_readouts = read('customizable_localization/rip_church_redesign.txt')
generated_loc = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
modifiers = read('common/event_modifiers/RIP_faith_modifiers.txt')
pulse_effects = read('common/scripted_effects/rip_ro_holy_cities_effects.txt')
hooks = read('common/on_actions/RIP_religion_russian_orthodox_on_actions.txt')

assert 'custom_window = { name = rip_ro_holy_cities_panel potential = { rip_church_ro_jurisdiction = yes has_country_flag = rip_ro_holy_city_register_open } }' in controls
assert 'custom_window = { name = rip_church_ro_panel potential = { rip_church_ro_jurisdiction = yes NOT = { has_country_flag = rip_church_ro_window_hidden } NOT = { has_country_flag = rip_ro_holy_city_register_open } } }' in controls

open_button = next(
    block for _, block in keyed_blocks(controls, 'custom_button')
    if re.search(r'(?m)^\s*name\s*=\s*rip_ro_holy_cities_open\b', block)
)
assert 'set_country_flag = rip_ro_holy_city_register_open' in open_button

close_button = next(
    block for _, block in keyed_blocks(controls, 'custom_button')
    if re.search(r'(?m)^\s*name\s*=\s*rip_ro_holy_cities_close\b', block)
)
assert 'clr_country_flag = rip_ro_holy_city_register_open' in close_button

city_panel = next(
    block for _, block in keyed_blocks(gui, 'windowType')
    if re.search(r'(?m)^\s*name\s*=\s*"rip_ro_holy_cities_panel"\s*', block)
)
assert 'position = { x=540 y=8 }' in city_panel and 'size = { x=475 y=560 }' in city_panel


def descendants(entries):
    for kind, body in entries:
        if isinstance(body, list):
            fields = dict(body)
            if 'name' in fields:
                yield kind, fields, body
            yield from descendants(body)


nodes = list(descendants(parse(gui)))


def one(kind, name):
    found = [(fields, body) for k, fields, body in nodes if k == kind and fields['name'] == name]
    assert len(found) == 1, (kind, name, len(found))
    return found[0]


bindings = {(kind, dict(body)['name']): body for kind, body in parse(controls) if kind.startswith('custom_')}
# Frame clauses repeat, so a binding is read as the raw list, never through dict().
def frames_of(kind, name):
    return [dict(value) for key, value in bindings[kind, name] if key == 'frame']


# ---- The three buttons the author asked to remove or move -------------------------------------------
# The native Orthodox window is the vanilla host of the faith's own controls. It must carry neither the
# Holy Cities medallion nor a cross-shaped toggle: both sat on top of the Defender of the Faith header.
host, host_body = one('windowType', 'orthodox_specific_window')
assert dict(host['position']) == {'x': '-24', 'y': '0'}, 'do not move the vanilla Orthodox panel'
host_nodes = list(descendants(host_body))
assert 'rip_ro_holy_cities_open' not in {f['name'] for _, f, _ in host_nodes}
assert not [f['name'] for k, f, _ in host_nodes
            if k == 'guiButtonType' and f.get('quadTextureSprite') in ('GFX_coptic_blessing_select', 'GFX_closebutton2')]
# The register is opened from one button, in the corner of the Muscovite Church window: a tile with
# the Russian Orthodox cross on it, not the vanilla Coptic blessing tile.
panel, panel_body = one('windowType', 'rip_church_ro_panel')
medallion, _ = one('guiButtonType', 'rip_ro_holy_cities_open')            # exactly one in the whole file
assert medallion['name'] in {f['name'] for _, f, _ in descendants(panel_body)}, 'the medallion belongs to the church window'
medallion_at = {key: int(value) for key, value in medallion['position']}
assert medallion['quadTextureSprite'] == 'GFX_rip_church_ro_holy_tile' and medallion['scale'] == '0.8'
assert medallion_at['x'] >= 400 and medallion_at['y'] >= 490, 'bottom-right corner of the 475x560 window'
assert medallion['pdx_tooltip'] == 'rip_ro_holy_cities_open_tt'
symbol, _ = one('iconType', 'rip_ro_holy_cities_open_symbol')
assert symbol['spriteType'] == 'GFX_country_icon_religion' and symbol['alwaystransparent'] == 'yes'
assert dict(bindings['custom_icon', 'rip_ro_holy_cities_open_symbol'])['frame'] == [('number', '30'), ('trigger', [('always', 'yes')])]
assert 'icon = 30' in faith, 'the medallion shows the Russian Orthodox faith frame'
assert 'GFX_coptic_blessing_select' not in {f.get('spriteType') or f.get('quadTextureSprite') for _, f, _ in descendants(panel_body)}

# ---- Art the register draws -------------------------------------------------------------------------
BAR_W, BAR_H, YEARS = 96, 22, 30
sprites = {dict(body)['name']: dict(body) for kind, body in parse(panels_gfx)[0][1] if kind == 'spriteType'}
bar_sprite = sprites['GFX_rip_church_ro_myth_bar']
assert bar_sprite['noOfFrames'] == str(YEARS + 1) and bar_sprite['textureFile'] == 'gfx/interface/rip_church/ro_myth_bar.dds'
for name, size in (('ro_myth_bar', (BAR_W * (YEARS + 1), BAR_H)), ('ro_myth_veil', (72, 36)), ('ro_holy_tile', (58, 58))):
    raw = (ROOT / f'gfx/interface/rip_church/{name}.dds').read_bytes()
    assert raw[:4] == b'DDS ' and raw[84:88] != b'DX10'
    assert struct.unpack_from('<II', raw, 12) == (size[1], size[0]), (name, 'EU4 slices a strip into equal frames')
assert sprites['GFX_rip_church_ro_holy_tile']['effectFile'] == 'gfx/FX/buttonstate.lua', 'the tile reacts to hover like a button'
result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/build_ro_register_art.py'), '--check'], capture_output=True, text=True)
assert result.returncode == 0, 'run tools/build_ro_register_art.py: ' + result.stdout + result.stderr

# ---- The five rows ----------------------------------------------------------------------------------
# A faith's frame in the religion strips is its icon = N. Read it from the files rather than trusting a
# table: the register once showed the Protestant cross for Orthodox cities and the Coptic one for Sunni Jerusalem.
def religion_icons(path):
    source = re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig', errors='replace'))
    found, stack = {}, []
    for m in re.finditer(r'([\w.\-]+)\s*=\s*\{|\}|\bicon\s*=\s*(\d+)', source):
        if m[0] == '}':
            stack and stack.pop()
        elif m[1]:
            stack.append(m[1])
        elif len(stack) == 2:
            found[stack[1]] = int(m[2])
    return found


declared_icons = {}
for folder in ([vanilla_root() / 'common/religions'] if vanilla_root() else []) + [ROOT / 'common/religions']:
    for religion_file in sorted(folder.glob('*.txt')):
        declared_icons.update(religion_icons(religion_file))
assert {'russian_orthodox': 30, 'greek_catholic': 31, 'old_believer': 32}.items() <= declared_icons.items()
if vanilla_root():
    assert declared_icons['orthodox'] == 4 and declared_icons['sunni'] == 5 and declared_icons['coptic'] == 14 and len(declared_icons) == 31

myths = {}
for key in ('novgorod', 'moscow', 'kyiv', 'constantinople', 'jerusalem'):
    block = named_block(modifiers, 'rip_ro_myth_' + key)
    myths[key] = re.findall(r'(?m)^\s*(\w+)\s*=\s*-?\d', block[block.index('{') + 1:])
    assert len(myths[key]) == 2, key
ladders = {dict(body)['name']: [(dict(row)['trigger'], dict(row)['localisation_key']) for k, row in body if k == 'text']
           for kind, body in parse(church_readouts) if kind == 'defined_text'}
loc = dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', generated_loc, re.M))
loc.update(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', site_localisation, re.M))
visible = lambda text: re.sub(r'§.', '', text)

# EU4 1.37.5 reads an upper-case ROOT in a localisation command as an event target named 'ROOT', does not find it and logs three
# lines (undefined non-dynamic flag, undefined event target, undefined monarch/heir) for every such string on every frame it is
# drawn: with the register open error.log grew by about 0.2 MB a second. Written [Root.GetX] it is the scope keyword.
assert not [key for key, value in loc.items() if '[ROOT.' in value], 'a church or register string uses [ROOT.]; write [Root.]'

world = World()
owner = world.country('MOS', 'russian_orthodox')
row_limit = 34 + 407
for city, province in (
    ('novgorod', 310),
    ('moscow', 295),
    ('kyiv', 280),
    ('constantinople', 151),
    ('jerusalem', 379),
):
    assert f'name = "rip_ro_holy_city_{city}_row"' in city_panel
    row, row_body = one('windowType', f'rip_ro_holy_city_{city}_row')
    assert dict(row['size']) == {'x': '407', 'y': '58'}
    assert int(dict(row['position'])['x']) + 407 <= row_limit
    inside = {f['name']: (k, f) for k, f, _ in descendants(row_body)}
    for field in ('name', 'owner', 'faith', 'faith_icon', 'myth_progress', 'myth_bar', 'bonus_pending', 'bonus_0', 'bonus_1',
                  'bonus_active_0', 'bonus_active_1'):
        assert f'rip_ro_holy_city_{city}_{field}' in inside, (city, field)
    assert f'[{province}.GetName]' in site_localisation
    assert f'[{province}.Owner.GetName]' in site_localisation
    assert f'Faith: [{province}.Religion.GetName]' in site_localisation, 'every row labels its faith, Moscow included'
    assert f'rip_ro_myth_{city}' in modifiers, f'bonus modifier for {city} must be defined'
    assert f'rip_ro_myth_years_{city}' in pulse_effects, f'30-year pulse must advance {city}'
    assert f'rip_ro_myth_complete_{city}' in pulse_effects
    province_scope = world.province(province, owner, 'orthodox')

    # Faith icon: the first frame clause that holds must be the faith's own icon, for every faith.
    faith_frames = frames_of('custom_icon', f'rip_ro_holy_city_{city}_faith_icon')
    for religion, icon in declared_icons.items():
        province_scope['religion'] = religion
        shown = [int(f['number']) for f in faith_frames if world.gate(f['trigger'], owner)]
        assert shown and shown[0] == icon, (city, religion, shown, icon)

    # Capacity bar: one frame per year, the first frame while the variable has never been set.
    bar_frames = frames_of('custom_icon', f'rip_ro_holy_city_{city}_myth_bar')
    assert len(bar_frames) == YEARS + 1
    variable = f'rip_ro_myth_years_{city}'
    owner['variables'].pop(variable, None)
    assert [int(f['number']) for f in bar_frames if world.gate(f['trigger'], owner)][0] == 1
    ladder = ladders['GetRipRoMythYears' + city.title()]
    for years in range(YEARS + 1):
        owner['variables'][variable] = years
        assert [int(f['number']) for f in bar_frames if world.gate(f['trigger'], owner)][0] == years + 1, (city, years)
        leaf = next(loc[key] for gate, key in ladder if world.gate(gate, owner))
        assert visible(leaf) == str(years), (city, years, leaf)
        assert leaf.startswith('§G' if years == YEARS else '§R' if years == 0 else '§Y'), (city, years, leaf)
    owner['variables'].pop(variable)
    bar = inside[f'rip_ro_holy_city_{city}_myth_bar'][1]
    assert bar['spriteType'] == 'GFX_rip_church_ro_myth_bar' and 'scale' not in bar
    assert int(dict(bar['position'])['x']) + BAR_W <= 407
    progress_tip = f'rip_ro_holy_city_{city}_myth_progress_tt'
    assert dict(bindings['custom_icon', f'rip_ro_holy_city_{city}_myth_bar'])['tooltip'] == progress_tip
    assert dict(bindings['custom_text_box', f'rip_ro_holy_city_{city}_myth_progress'])['tooltip'] == progress_tip
    assert loc[f'rip_ro_holy_city_{city}_myth_progress'] == f'[Root.GetRipRoMythYears{city.title()}] / 30 years'
    assert f'[Root.GetRipRoMythYears{city.title()}]' in loc[progress_tip]

    # Blessing: the two modifier icons of the myth, dimmed by a veil until it matures, then glowing.
    for slot, effect in enumerate(myths[city]):
        icon = inside[f'rip_ro_holy_city_{city}_bonus_{slot}'][1]
        assert icon['spriteType'] == f'GFX_rip_church_effect_{effect}', (city, slot)
        assert f'gfx/interface/ideas_EU4/{effect}.dds' in sprites[icon['spriteType']]['textureFile']
        if vanilla_root():
            assert (vanilla_root() / f'gfx/interface/ideas_EU4/{effect}.dds').exists(), effect
        assert dict(bindings['custom_icon', f'rip_ro_holy_city_{city}_bonus_{slot}'])['tooltip'] == f'rip_ro_holy_city_{city}_bonus_tt'
        assert inside[f'rip_ro_holy_city_{city}_bonus_active_{slot}'][1]['alwaystransparent'] == 'yes'
    assert inside[f'rip_ro_holy_city_{city}_bonus_pending'][1]['alwaystransparent'] == 'yes', 'the veil must not take the mouse'
    veil = dict(bindings['custom_icon', f'rip_ro_holy_city_{city}_bonus_pending'])['potential']
    glows = [dict(bindings['custom_icon', f'rip_ro_holy_city_{city}_bonus_active_{slot}'])['potential'] for slot in range(2)]
    for matured in (False, True):
        owner['flags'].pop(f'rip_ro_myth_complete_{city}', None)
        if matured:
            owner['flags'][f'rip_ro_myth_complete_{city}'] = 0
        assert world.gate(veil, owner) == (not matured)
        assert all(world.gate(glow, owner) == matured for glow in glows)
    owner['flags'].pop(f'rip_ro_myth_complete_{city}', None)

# Nothing in the register reads a variable directly: that prints nothing until the variable is set
# ('/30 yrs' with no number), and the window is opened long before the first yearly pulse.
register_keys = {key: value for key, value in loc.items() if key.startswith(('rip_ro_holy_', 'rip_ro_myth_'))}
assert register_keys and not [key for key, value in register_keys.items() if '.GetValue' in value]
assert not [key for key in register_keys if key.startswith('rip_ro_myth_bar_')], 'the text bars are retired'
assert 'GetRipRoMythBar' not in custom_loc and 'GetRipRoMythBar' not in church_readouts

# Text fits its box. Widths are the vanilla vic_18 advances (kerning ignored): the engine falls back to
# the same look for the mod's undeclared vic_14, so every register string is budgeted at vic_18.
if vanilla_root():
    advance = {}
    for line in (vanilla_root() / 'gfx/fonts/vic_18.fnt').read_text(encoding='latin-1').splitlines():
        if line.startswith('char '):
            fields = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
            advance[fields['id']] = fields['xadvance']

    def wrapped(text, width):
        lines_, current = [], ''
        for word in visible(text.replace('\\n', ' ')).split():
            candidate = (current + ' ' + word).strip()
            if sum(advance[ord(ch)] for ch in candidate) > width and current:
                lines_.append(current)
                current = word
            else:
                current = candidate
        return lines_ + [current]

    intro_box, _ = one('instantTextBoxType', 'rip_ro_holy_cities_intro')
    footer_box, _ = one('instantTextBoxType', 'rip_ro_holy_cities_footer')
    for box, key in ((intro_box, 'rip_ro_holy_cities_intro'), (footer_box, 'rip_ro_holy_cities_footer')):
        assert len(wrapped(loc[key], int(box['maxWidth']))) * 18 <= int(box['maxHeight']), (key, wrapped(loc[key], int(box['maxWidth'])))
    row_box, _ = one('instantTextBoxType', 'rip_ro_holy_city_novgorod_faith')
    for sample in ('Faith: Muscovite Orthodox', 'Faith: Greek Catholic', 'Owner: Constantinople', 'Owner: Holy Roman Empire'):
        assert len(wrapped(sample, int(row_box['maxWidth']))) == 1, sample
    years_box, _ = one('instantTextBoxType', 'rip_ro_holy_city_novgorod_myth_progress')
    assert len(wrapped('30 / 30 years', int(years_box['maxWidth']))) == 1
    assert int(years_box['maxWidth']) == BAR_W, 'the number is centred over the bar'
    # Vertical budget of the 560px window: rows, footer and button stack without touching, inside the surface.
    last_row = max(int(dict(one('windowType', f'rip_ro_holy_city_{c}_row')[0]['position'])['y']) for c in myths) + 58
    assert last_row <= int(dict(footer_box['position'])['y'])
    assert int(dict(footer_box['position'])['y']) + int(footer_box['maxHeight']) <= int(dict(one('guiButtonType', 'rip_ro_holy_cities_close')[0]['position'])['y'])
    assert int(dict(one('guiButtonType', 'rip_ro_holy_cities_close')[0]['position'])['y']) + 32 <= 547

# The layout preview draws the real generated windows with the real textures and glyph atlas in five views
# (register: new game, part-way, matured; church window: normal, schism). It fails on an overflowing multi-line box,
# a widget outside its window, a missing key or an unresolved [command]: what the screenshots of 18 October showed.
if vanilla_root():
    with tempfile.TemporaryDirectory() as scratch:
        run = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/preview_church_register.py'), '--panel', 'all', '--zoom', '1', '--quiet',
                              '--out', scratch], capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert run.returncode == 0, run.stdout[-1500:] + run.stderr[-800:]
        assert len(list(Path(scratch).glob('*.png'))) == 5, run.stdout[-800:]

assert 'rip_ro_holy_cities_open' in site_localisation
assert 'Holy Cities Register' in site_localisation
assert 'Sees, Sacred Myths and Pilgrimage Destinations' in site_localisation
assert 'rip_ro_sites.' not in site_localisation and 'rip_ro_site_' not in site_localisation
assert 'rip_ro_holy_city_count' not in controls + gui + site_localisation
assert 'rip_ro_holy_cities_yearly_pulse_effect = yes' in hooks

assert 'has_patriarchs = yes' in faith
raskol = named_block(read('common/disasters/rip_faith_disasters.txt'), 'rip_ro_raskol')
assert 'rip_ro_icon_count' not in raskol
assert 'has_country_flag = rip_ro_stage_raskol' in named_block(raskol, 'can_start')
assert 'patriarch_authority = 0.6' in named_block(raskol, 'can_end')
assert 'religious_unity' not in named_block(raskol, 'can_end'), 'a unity exit closes the Raskol on its first check'
assert 'monthly_fervor_increase' not in raskol
assert 'rip_ro_icon_count' not in read('common/scripted_effects/rip_faith_zeal_effects.txt')
print('PASS: Russian Orthodox register button in the church window, no stray cross buttons, faith frames, 31-frame myth bars, blessing icons and veil, fitted text, and Raskol guards verified')
