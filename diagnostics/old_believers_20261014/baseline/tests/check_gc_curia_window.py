"""Contracts for the remaining Greek Catholic synod, icons and Rome audience."""
import re
from clausewitz_testlib import named_block, keyed_blocks, read, vanilla_defines_localisation, vanilla_root
from church_testlib import parse

curia_triggers = read('common/scripted_triggers/rip_church_gc_curia_triggers.txt')
curia_effects = read('common/scripted_effects/rip_church_gc_curia_effects.txt')
opinion_modifiers = read('common/opinion_modifiers/RIP_church_relations.txt')
icon_triggers = read('common/scripted_triggers/rip_church_gc_interaction_triggers.txt')
icon_effects = read('common/scripted_effects/rip_church_gc_interaction_effects.txt')
union_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
union_effects = read('common/scripted_effects/rip_church_union_effects.txt')
controls = read('common/custom_gui/RIP_church_controls.txt')
features = read('common/custom_gui/RIP_church_gc_features.txt')
gui_generator = read('tools/build_church_gui.py')
localisation_generator = read('tools/build_church_localisation.py')
english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
interface = read('interface/countryreligionview.gui')
custom_text = read('customizable_localization/rip_church_redesign.txt')

def button(source, name):
    for _, block in keyed_blocks(source, 'custom_button'):
        if re.search(rf'\bname\s*=\s*{re.escape(name)}\b', block):
            return block
    raise AssertionError(f'missing button: {name}')

# No active numerical Communion/Papal Standing or paid petition menu.
active_sources = (curia_triggers, curia_effects, controls, features,
                  gui_generator, interface, custom_text, english)
for source in active_sources:
    for stale in ('rip_church_communion', 'rip_church_papal_standing',
                  'rip_church_standing_income', 'rip_church_gc_petition_',
                  'rip_church_gc_donate_', 'GetChurchCuriaRate',
                  'GetChurchDonationState', 'GetChurchCuriaPrivilege'):
        assert stale not in source, stale
assert 'Papal Standing' not in english
assert 'Communion Balance' not in english
assert 'Papal petitions' not in english

# Local synod remains a single ten-year institution, using only Patriarch
# Authority and ducats. It is not blocked by Curia interaction state.
assert 'rip_church_gc_can_infrastructure = yes' in union_effects
assert 'rip_church_gc_can_coexistence = yes' in union_effects
assert 'patriarch_authority = 0.2' in named_block(union_triggers, 'rip_church_gc_can_infrastructure')
assert 'patriarch_authority = 0.2' in named_block(union_triggers, 'rip_church_gc_can_coexistence')
assert 'rip_church_gc_has_curia_petition' not in union_triggers

# The three devotional icons remain a separately gated PA-priced system.
for key in ('liturgy', 'learning', 'charity'):
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in icon_effects
    assert 'add_patriarch_authority = -0.2' in named_block(
        icon_effects, f'rip_church_gc_activate_icon_{key}_effect')
    assert f'rip_church_gc_can_activate_icon_{key} = yes' in button(
        features, f'rip_church_gc_icon_{key}_button')

# Curia contact offers a non-electoral audience and a direct diplomatic gift.
gate = named_block(curia_triggers, 'rip_church_gc_can_depute_to_curia')
effect = named_block(curia_effects, 'rip_church_gc_depute_to_curia_effect')
assert 'treasury = 50' in gate and 'patriarch_authority' not in gate
assert 'had_country_flag = { flag = rip_church_gc_deputation_sent days = 1825 }' in gate
assert 'add_treasury = -50' in effect
assert 'PAP = { add_opinion = { who = ROOT modifier = rip_church_opinion_gc_deputation } }' in effect
assert 'add_opinion = { who = PAP modifier = rip_church_opinion_gc_deputation }' in effect
deputation_opinion = named_block(opinion_modifiers, 'rip_church_opinion_gc_deputation')
assert 'opinion = 25' in deputation_opinion and 'yearly_decay = 2' in deputation_opinion
assert 'rip_church_gc_deputation_button' in features
assert 'rip_church_gc_curia_note' in gui_generator
assert 'name = "rip_church_gc_curia_note"' in interface
assert 'rip_church_gui_right_' not in gui_generator
assert 'rip_church_rights_card' not in interface
assert 'rip_church_gui_right_' not in english
assert 'rip_church_gc_curia_vote_disclaimer' not in localisation_generator
assert 'rip_church_gc_curia_vote_disclaimer' not in english
assert 'no gameplay unlock for these offices' in localisation_generator
assert 'no gameplay unlock for these offices' in english
assert 'name = "rip_church_gc_controller_readout"' in interface
assert 'global_event_target = rip_church_gc_controller' in controls
assert 'event_target:rip_church_gc_controller = { is_papal_controller = yes }' in controls
assert 'Curia controller\\n' in english

# GC-only bishop art must not overwrite the native Orthodox patriarch sprites.
from pathlib import Path
import struct
from clausewitz_testlib import ROOT
for level in ('low', 'high'):
    assert f'name ="{level}_patriarch_authority" scripted = yes' in interface
    assert f'spriteType = "GFX_icon_{level}_patriarch_authority"' in interface
    assert f'name = {level}_patriarch_authority potential = {{ NOT = {{ religion = greek_catholic }} }}' in controls
    assert f'name = rip_church_gc_capacity_{level}_icon potential = {{ religion = greek_catholic }}' in controls
    data = (ROOT / f'gfx/interface/rip_church/gc_archbishop_{level}.dds').read_bytes()
    assert data[:4] == b'DDS ' and struct.unpack_from('<II', data, 12) == (38, 38)
assert 'grants +25 opinion in both directions, decaying by 2 per year' in localisation_generator
for language in ('english', 'french', 'german', 'spanish'):
    localisation = read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
    assert 'grants +25 opinion in both directions, decaying by 2 per year' in localisation
    assert 'Effect: +25 opinion in both directions, decaying by 2 per year' in localisation
assert 'grants +10 opinion in both directions' not in english
assert 'may improve the Pope’s opinion temporarily' not in english
gift_gate = named_block(curia_triggers, 'rip_church_gc_can_offer_gift_to_holy_see')
gift_effect = named_block(curia_effects, 'rip_church_gc_offer_gift_to_holy_see_effect')
assert 'treasury = 100' in gift_gate
assert 'had_country_flag = { flag = rip_church_gc_holy_see_gift_sent days = 1825 }' in gift_gate
assert 'add_treasury = -100' in gift_effect
assert 'PAP = { add_opinion = { who = ROOT modifier = rip_church_opinion_gc_donation } }' in gift_effect
assert 'add_opinion = { who = PAP' not in gift_effect
assert 'rip_church_gc_holy_see_gift_button' in features
assert 'rip_church_gc_can_offer_gift_to_holy_see = yes' in button(
    features, 'rip_church_gc_holy_see_gift_button')
assert '100 ducats' in localisation_generator
assert '+25 opinion of us, decaying by 5 per year' in localisation_generator
assert 'no Patriarch Authority, Curia vote, cardinal or electoral influence' in localisation_generator
for language in ('english', 'french', 'german', 'spanish'):
    localisation = read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
    assert 'rip_church_gc_holy_see_gift_button:0 "Send a gift to Rome"' in localisation
    assert 'The Papal State gains +25 opinion of us, decaying by 5 per year' in localisation
    assert 'rip_church_opinion_gc_donation:0 "Donation from an Eastern Catholic church"' in localisation

# All three pages share a fixed header/navigation rail.  Devotional icon art is
# the click target's card, not an empty blue button floating above the icon.
def widgets(entries):
    for kind, payload in entries:
        if not isinstance(payload, list):
            continue
        if kind in ('windowType', 'iconType', 'guiButtonType', 'instantTextBoxType'):
            yield kind, dict(payload)
        yield from widgets(payload)

pages = {}
for page, name in (('union', 'rip_church_gc_panel'), ('curia', 'rip_church_gc_curia_panel'),
                   ('parishes', 'rip_church_gc_parishes_panel')):
    block = next(block for _, block in keyed_blocks(interface, 'windowType')
                 if dict(dict(parse(block))['windowType']).get('name') == name)
    pages[page] = dict((d['name'], d) for _, d in widgets(parse(block)))

# Header and tab navigation retain the same geometry on each page. The
# concrete offsets can evolve with the native frame without weakening this.
headers = [pages[page]['rip_church_gc_heading'] for page in pages]
assert len({str(d['position']) for d in headers}) == 1
assert len({(d['maxWidth'], d['maxHeight'], d['font'], d['format']) for d in headers}) == 1
for tab in ('union', 'curia'):
    tabs = [pages[page][f'rip_church_gc_{tab}_tab_{page}'] for page in pages]
    assert len({str(d['position']) for d in tabs}) == 1
    assert all(d['quadTextureSprite'] == 'GFX_tab_small_116' for d in tabs)
assert interface.count('spriteType = "GFX_rip_church_union_frame"') >= 3
assert 'small_tiles_dialog.dds' not in read('interface/RIP_church_panels.gfx')
assert 'name = "rip_church_authority_heading" scripted = yes' in interface
assert interface.count('spriteType = "GFX_rip_church_section_banner"') >= 6
assert 'rip_church_gc_holy_see_gift_button' in pages['curia']
toggle = button(controls, 'rip_church_gc_window_toggle')
assert 'potential = { religion = greek_catholic }' in toggle
assert 'has_country_flag = rip_church_gc_window_hidden' in toggle
assert 'clr_country_flag = rip_church_gc_window_hidden' in toggle
assert 'set_country_flag = rip_church_gc_window_hidden' in toggle
assert 'rip_church_gc_window_hidden' in controls
assert 'rip_church_gc_window_toggle' in interface
toggle_widget = next(
    d for kind, d in widgets(parse(interface))
    if kind == 'guiButtonType' and d.get('name') == 'rip_church_gc_window_toggle'
)
assert toggle_widget['quadTextureSprite'] == 'GFX_closebutton2'
assert dict(toggle_widget['position']) == {'x': '372', 'y': '238'}
assert toggle_widget['scale'] == '0.7'
# The deputation and the gift each get their own button and own summary line;
# the old four-cell Cost/Peace/Rome/Cooldown grid sat under the gift button.
for stale in ('rip_church_gui_contact_peace', 'rip_church_gui_contact_rome', 'rip_church_gui_contact_cooldown'):
    assert f'name = "{stale}"' not in interface, stale
# Every scripted widget needs a binding, otherwise the engine prints the raw
# [Root.GetChurch...] token (the Curia tab showed exactly that).
bindings = controls + features
binding_types = {}
for kind, payload in parse(bindings):
    if kind.startswith('custom_'):
        binding_types.setdefault(dict(payload)['name'], set()).add(kind)
widget_types = {'windowType': 'custom_window', 'instantTextBoxType': 'custom_text_box',
                'iconType': 'custom_icon', 'guiButtonType': 'custom_button'}
english_keys = dict(re.findall(r'^\s+(\w+):0 "(.*)"$', english, re.M))
readout_names = {dict(payload)['name'] for kind, payload in parse(custom_text) if kind == 'defined_text'}

def expanded_localisation(key, trail=(), allow_native=False):
    if allow_native and key not in english_keys:
        # Orthodox fallback headings reference stock localisation, outside
        # the mod's replacement file and outside this regression's scope.
        assert vanilla_defines_localisation(key) is not False, f'GUI localisation missing: {key}'
        return ''
    assert key in english_keys, f'GUI localisation missing: {key}'
    assert key not in trail, f'circular GUI localisation: {trail + (key,)}'
    return re.sub(r'\$([^$]+)\$', lambda m: expanded_localisation(m[1], trail + (key,), allow_native), english_keys[key])

# In the scripted church UI, runtime rejected both coloured GetValue leaves
# and vanilla's quoted raw-property leaves. A defined_text must return literal
# numeric localisation here; direct GetValue belongs in the outer GUI text.
variable_value = re.compile(r'\[Root\.\w+\.GetValue\]')
for _, block in keyed_blocks(custom_text, 'defined_text'):
    entries = dict(parse(block))['defined_text']
    readout = dict(entries)['name']
    for match in re.finditer(r'\blocalisation_key\s*=\s*("[^"\r\n]*"|[^\s}]+)', block):
        token = match[1]
        leaf = token.strip('"')
        if variable_value.fullmatch(leaf):
            raise AssertionError((readout, 'runtime rejected raw GetValue leaf', leaf))
        else:
            value = expanded_localisation(leaf, allow_native=True)
            assert not variable_value.search(value), (
                readout, leaf, 'runtime rejected nested GetValue; use literal leaves or direct outer properties')

for kind, d in widgets(parse(interface)):
    if d.get('scripted') != 'yes' or not d.get('name', '').startswith('rip_church_'):
        continue
    expected = widget_types[kind]
    if kind == 'guiButtonType' and d.get('quadTextureSprite', '').startswith('GFX_shield_'):
        expected = 'custom_shield'
    assert expected in binding_types.get(d['name'], set()), (
        d['name'], 'wrong or missing scripted widget binding', expected, binding_types.get(d['name']))
    for field in ('text', 'buttonText'):
        if d.get(field):
            for readout in re.findall(r'\[Root\.(GetChurch\w+)\]', expanded_localisation(d[field])):
                assert readout in readout_names, (d['name'], 'unresolved scripted readout', readout)
# One Synod entry point in the same card as its state. A GC-only opaque cover
# prevents the native Orthodox Select control showing through or taking clicks.
assert 'rip_church_gc_native_privileges_button' in pages['union']
assert pages['union']['rip_church_gc_native_privileges_button']['quadTextureSprite'] == 'button_type_8'
native_controls = next(block for _, block in keyed_blocks(interface, 'windowType')
                       if dict(dict(parse(block))['windowType']).get('name') == 'rip_church_gc_native_controls')
assert 'rip_church_gc_native_privileges_button' not in native_controls
cover = dict((d['name'], d) for _, d in widgets(parse(native_controls)))['rip_church_gc_selector_cover']
assert cover['alwaystransparent'] == 'no'
assert cover['spriteType'] == 'GFX_rip_church_gc_selector_surface'
gfx = read('interface/RIP_church_panels.gfx')
cover_sprite = next(block for _, block in keyed_blocks(gfx, 'corneredTileSpriteType')
                    if 'name = "GFX_rip_church_gc_selector_surface"' in block)
cover_size = dict(dict(dict(parse(cover_sprite))['corneredTileSpriteType'])['size'])
cover_position = dict(cover['position'])
# The sprite's name says 71, but the installed DDS is actually 79x31. Cover
# its complete texture/click target while leaving the Convert row clear.
native_button = (vanilla_root() / 'gfx/interface/standard_button_71.dds').read_bytes()
native_height, native_width = struct.unpack_from('<II', native_button, 12)
assert int(cover_position['x']) <= 304 and int(cover_position['x']) + int(cover_size['x']) >= 304 + native_width
assert int(cover_position['y']) <= 300 and int(cover_position['y']) + int(cover_size['y']) >= 300 + native_height
assert int(cover_position['y']) + int(cover_size['y']) <= 332, 'selector mask must leave the native Convert row clear'
assert 'name = "rip_church_gui_synod"' not in interface and 'name = rip_church_gui_synod ' not in bindings
assert interface.count('rip_church_gc_open_synod_effect') == 0  # effects live in custom_gui only
assert bindings.count('rip_church_gc_open_synod_effect = yes') == 1
assert 'GFX_standard_button_140' not in gui_generator
for key in ('liturgy', 'learning', 'charity'):
    start = interface.index(f'name = "rip_church_gc_icon_{key}_button"')
    assert 'quadTextureSprite = "GFX_coptic_blessing_select"' in interface[start:interface.index('buttonFont', start)]
    icon_sprite = next(block for _, block in keyed_blocks(gfx, 'spriteType')
                       if f'name = "GFX_rip_church_gc_icon_{key}"' in block)
    assert f'gfx/interface/rip_church/gc_icon_{key}.dds' in icon_sprite
    icon_asset = ROOT / f'gfx/interface/rip_church/gc_icon_{key}.dds'
    assert icon_asset.exists(), ('missing devotional icon', key)
    raw = icon_asset.read_bytes()
    assert raw[:4] == b'DDS ' and struct.unpack_from('<II', raw, 12) == (64, 64)
# Read-only state badges share their authoritative gameplay gate and its
# complement. They cannot introduce a second action or a false ready state.
for stem, gate in (('rip_church_deputation_status', 'rip_church_gc_can_depute_to_curia'),
                   ('rip_church_gift_status', 'rip_church_gc_can_offer_gift_to_holy_see')):
    icon_bindings = {dict(payload)['name']: dict(payload)
                     for kind, payload in parse(controls) if kind == 'custom_icon'}
    assert icon_bindings[stem+'_ready']['potential'] == [(gate, 'yes')]
    assert icon_bindings[stem+'_blocked']['potential'] == [('NOT', [(gate, 'yes')])]
    for suffix in ('ready', 'blocked'):
        assert stem+'_'+suffix not in binding_types or 'custom_button' not in binding_types[stem+'_'+suffix]
assert 'name = "rip_church_gui_parish_empty_state"' in interface
assert 'name = GetChurchParishRegisterState' in custom_text

from church_testlib import fixture, TRIGGERS
w,c,p = fixture('greek_catholic')
c['treasury'] = 150
if 'PAP' not in w.countries:
    w.country('PAP','catholic')
# Execute the actual descending threshold rows for the full native opinion
# interval. This catches missing zero/negative rows and wrong row ordering.
opinion_rows = next(payload for kind, payload in parse(custom_text)
                    if kind == 'defined_text' and dict(payload)['name'] == 'GetChurchPapalOpinion')
def opinion_leaf():
    return next(dict(payload)['localisation_key'] for kind, payload in opinion_rows
                if kind == 'text' and w.gate(dict(payload)['trigger'], c))

cached_opinion = c['variables'].get('rip_church_papal_opinion')
for opinion in range(-200, 201):
    c['variables']['rip_church_papal_opinion'] = opinion
    literal = re.sub(r'§.', '', expanded_localisation(opinion_leaf()))
    assert int(literal) == opinion, ('Papal opinion readout', opinion, literal)
w.countries['PAP']['religion'] = 'orthodox'
assert opinion_leaf() == 'rip_church_gc_opinion_absent'
w.countries['PAP']['religion'] = 'catholic'
if cached_opinion is None:
    c['variables'].pop('rip_church_papal_opinion')
else:
    c['variables']['rip_church_papal_opinion'] = cached_opinion

deputation_gate = TRIGGERS['rip_church_gc_can_depute_to_curia']
assert w.gate(deputation_gate,c)
c['flags']['rip_church_gc_deputation_sent'] = w.day
assert not w.gate(deputation_gate,c)
w.day += 1824
assert not w.gate(deputation_gate,c)
w.day += 1
assert w.gate(deputation_gate,c)

gift_gate = TRIGGERS['rip_church_gc_can_offer_gift_to_holy_see']
gift_effect = 'rip_church_gc_offer_gift_to_holy_see_effect'
baseline_pap_opinion = w.opinion(w.countries['PAP'],c)
assert w.gate(gift_gate,c)
w.run(gift_effect,c)
assert c['treasury'] == 50
assert c['flags']['rip_church_gc_holy_see_gift_sent'] == w.day
assert w.opinion(w.countries['PAP'],c) == baseline_pap_opinion + 25
assert not w.gate(gift_gate,c)
w.day += 1824
assert not w.gate(gift_gate,c)
w.day += 1
c['treasury'] = 100
assert w.gate(gift_gate,c)
w.run(gift_effect,c)
assert c['treasury'] == 0
assert w.opinion(w.countries['PAP'],c) == baseline_pap_opinion + 25  # first gift has decayed away
assert not w.gate(gift_gate,c)  # insufficient funds also disables the control
c['treasury'] = 100
c['is_at_war'] = True
assert not w.gate(gift_gate,c)
c['is_at_war'] = False
w.countries['PAP']['religion'] = 'orthodox'
assert not w.gate(gift_gate,c)
w.countries['PAP']['religion'] = 'catholic'
c['religion'] = 'catholic'
assert not w.gate(gift_gate,c)
c['religion'] = 'greek_catholic'

# Community-rights counts on the Union status card. A direct
# [Root.<variable>.GetValue] prints nothing (and logs "Unknown text property" on every
# frame) while the variable has never been set, e.g. right after conversion and before
# the first monthly refresh. The counts therefore come from literal defined_text rows,
# and an unset variable must read 0.
for family, variable in (('Eastern', 'rip_church_gui_eastern_parishes'), ('Latin', 'rip_church_gui_latin_parishes')):
    count_rows = next((payload for kind, payload in parse(custom_text)
                       if kind == 'defined_text' and dict(payload)['name'] == f'GetChurch{family}Count'), None)
    assert count_rows, f'GetChurch{family}Count readout is missing'
    def count_leaf():
        return next(dict(payload)['localisation_key'] for kind, payload in count_rows
                    if kind == 'text' and w.gate(dict(payload)['trigger'], c))
    saved_count = c['variables'].pop(variable, None)
    assert re.sub(r'§.', '', expanded_localisation(count_leaf())) == '0', (family, 'an unset variable must read 0')
    for count in range(0, 151):
        c['variables'][variable] = count
        literal = re.sub(r'§.', '', expanded_localisation(count_leaf()))
        assert literal == (str(count) if count < 100 else '100+'), (family, count, literal)
    c['variables'].pop(variable)
    if saved_count is not None:
        c['variables'][variable] = saved_count
count_text = expanded_localisation('rip_church_gui_count_value')
assert '.GetValue' not in count_text, 'the count row must not read a variable directly'
assert '[Root.GetChurchEasternCount]' in count_text and '[Root.GetChurchLatinCount]' in count_text
count_tooltip = english_keys['rip_church_gui_count_value_tt'].lower()
for phrase in ('gameplay', 'canonical', 'not an exact', 'voluntary union acceptance', 'guarantee community rights'):
    assert phrase in count_tooltip, ('count tooltip must say', phrase)
count_start = interface.index('name = "rip_church_gui_count_value"')
assert 'alwaystransparent' not in interface[count_start:interface.index('\n}', count_start)], (
    'a widget with a hover tooltip must be hit-testable')

# Tooltips of the church GUI. Every key a widget points at must exist, no tooltip may
# merely repeat the text it hangs on (a box with the window title hovered over the
# status line in play), and no live text may read a variable directly (the engine
# drops such a string while the variable is unset and logs it every frame).
all_controls = controls + features
tooltip_keys = set(re.findall(r'pdx_tooltip = "(\w+)"', interface))
tooltip_keys |= set(re.findall(r'\btooltip = (\w+)', all_controls))
missing_tooltips = sorted(key for key in tooltip_keys if key not in english_keys)
assert not missing_tooltips, ('tooltip keys without localisation', missing_tooltips)
for name, tip in re.findall(r'custom_text_box = \{ name = (\w+) .*? tooltip = (\w+) \}', all_controls):
    if name in english_keys and tip in english_keys:
        assert re.sub(r'\s+', ' ', english_keys[tip]).strip() != re.sub(r'\s+', ' ', english_keys[name]).strip(), (
            name, 'the tooltip only repeats the visible text')
for window in re.findall(r'name = "(rip_church_\w+_panel)" scripted = yes[^\n]*pdx_tooltip', interface):
    raise AssertionError(('a whole window must not carry a pdx_tooltip', window))
live_text_keys = set(re.findall(r'\btext = "(\w+)"', interface))
for key in sorted(live_text_keys & set(english_keys)):
    if key.startswith(('rip_church_gui_', 'rip_church_gc_')):
        assert '.GetValue]' not in english_keys[key], (key, 'a variable read directly in a live text')

print('GC CURIA PASS: audience and gift transactions, opinion, visibility gates, cooldown boundaries')
