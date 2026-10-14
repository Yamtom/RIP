"""Check Muscovite policy navigation, click targets and guarded transactions.

The bounded church interpreter executes source effects; it does not prove EU4
rendering, mouse hit testing, AI behaviour or save/load persistence.
"""
from copy import deepcopy
import re
import struct

from church_testlib import EFFECTS, fixture, parse
from clausewitz_testlib import ROOT, read, vanilla_root


def descendants(entries):
    for kind, body in entries:
        if isinstance(body, list):
            fields = dict(body)
            if 'name' in fields:
                yield kind, fields, body
            yield from descendants(body)


controls = {
    (kind, dict(body)['name']): dict(body)
    for kind, body in parse(read('common/custom_gui/RIP_church_controls.txt'))
}
gui = list(descendants(parse(read('interface/countryreligionview.gui'))))


def widget(kind, name, source=gui):
    found = [(fields, body) for k, fields, body in source
             if k == kind and fields.get('name') == name]
    assert len(found) == 1, (kind, name, len(found))
    return found[0]


def position(fields):
    return {key: int(value) for key, value in fields['position']}


def click(w, c, name):
    control = controls['custom_button', name]
    if not w.gate(control['potential'], c) or not w.gate(control['trigger'], c):
        return False
    w.execute(control['effect'], c)
    return True


toggle = 'rip_church_ro_window_toggle'
panel = controls['custom_window', 'rip_church_ro_panel']['potential']
native_cover = controls['custom_window', 'rip_church_ro_native_controls']['potential']
native, native_body = widget('windowType', 'rip_church_ro_native_controls')
native_children = list(descendants(native_body))
cover, _ = widget('iconType', 'rip_church_ro_selector_cover', native_children)
route, _ = widget('guiButtonType', toggle, native_children)
selector_symbol, _ = widget('iconType', 'rip_church_ro_selector_symbol', native_children)
assert native['scripted'] == route['scripted'] == 'yes'
assert cover['alwaystransparent'] == 'no', 'cover must intercept the retired selector'
assert cover['spriteType'] == 'GFX_rip_church_gc_selector_surface'
assert selector_symbol['spriteType'] == 'GFX_country_icon_religion'
assert selector_symbol['scripted'] == 'yes' and selector_symbol['alwaystransparent'] == 'yes'
symbol_binding = controls['custom_icon', 'rip_church_ro_selector_symbol']
assert dict(symbol_binding['frame']) == {'number': '30', 'trigger': [('always', 'yes')]}
assert 'icon = 30' in read('common/religions/russian_orthodox.txt'), 'Policies medallion must match the Russian Orthodox faith frame'
assert route['quadTextureSprite'] == 'GFX_standard_button_71'
assert route['buttonText'] == toggle
assert controls['custom_button', toggle]['effect'] == parse(
    'if = { limit = { has_country_flag = rip_church_ro_window_hidden } '
    'clr_country_flag = rip_church_ro_window_hidden } '
    'else = { set_country_flag = rip_church_ro_window_hidden }'
)

# The native callback remains present for ordinary Orthodox countries. The RO
# cover and its route share the native host, and replace the same Select button.
host, host_body = widget('windowType', 'orthodox_specific_window')
host_children = list(descendants(host_body))
assert widget('windowType', native['name'], host_children)
native_select, _ = widget('guiButtonType', 'pick_icon_button', host_children)
assert position(route) == position(native_select)
assert route['Orientation'] == native_select['Orientation'], 'replacement keeps the native host anchor'
install = vanilla_root()
if install:
    vanilla_gui = list(descendants(parse(
        (install / 'interface/countryreligionview.gui').read_text(encoding='utf-8-sig')
    )))
    for kind, name in (('iconType', 'current_patriarch_authority_progress_frame'),
                       ('iconType', 'current_patriarch_authority_progress_bg'),
                       ('iconType', 'current_patriarch_authority'),
                       ('instantTextBoxType', 'current_patriarch_authority_value'),
                       ('guiButtonType', 'pick_icon_button'),
                       ('iconType', 'no_current_icon'), ('iconType', 'current_icon')):
        assert widget(kind, name, host_children)[0] == widget(kind, name, vanilla_gui)[0], name
    for asset in ('copts_blessing_select', 'copts_blessing_slot'):
        image = (install / f'gfx/interface/{asset}.dds').read_bytes()
        assert image[:4] == b'DDS ' and struct.unpack_from('<II', image, 12) == (58, 58)
    for kind, name in (('instantTextBoxType', 'current_patriarch_authority_text'),
                       ('iconType', 'low_patriarch_authority'),
                       ('iconType', 'high_patriarch_authority')):
        fields = dict(widget(kind, name, host_children)[0])
        assert fields.pop('scripted') == 'yes'
        assert fields == widget(kind, name, vanilla_gui)[0], name

cases = 0
for faith in ('russian_orthodox', 'orthodox', 'greek_catholic', 'catholic'):
    w, c, p = fixture(faith)
    if faith == 'orthodox':
        assert not w.gate(native_cover, c), 'ordinary Orthodoxy does not inherit Moscow jurisdiction'
        c['flags']['rip_ro_stage_autocephaly'] = w.day
    before = deepcopy(c)
    eligible = faith in ('russian_orthodox', 'orthodox')
    assert w.gate(native_cover, c) == w.gate(panel, c) == eligible
    assert click(w, c, toggle) == eligible
    assert not w.gate(panel, c)
    if eligible:
        expected = deepcopy(before)
        expected['flags']['rip_church_ro_window_hidden'] = w.day
        assert c == expected, 'hiding the pane must be free and change only its visibility flag'
        assert w.gate(native_cover, c), 'reopen route must remain accessible'
        assert click(w, c, toggle) and w.gate(panel, c)
    assert c == before, 'reopening is reversible; other faiths must remain unchanged'
    cases += 1

# The four policies now have visible action buttons; the icon is decorative and
# active state uses its separate highlight frame, never a check/cross badge.
for policy in ('war', 'mercy', 'building', 'mission'):
    texture = f'gfx/interface/rip_church/ro_banner_{policy}.dds'
    assert f'textureFile = "{texture}"' in read('interface/RIP_church_panels.gfx')
    asset = (ROOT / texture).read_bytes()
    assert asset[:4] == b'DDS ' and struct.unpack_from('<II', asset, 12) == (64, 64)
    assert len(asset) == 128 + 64 * 64 * 4
    alpha = asset[131::4]
    assert min(alpha) == 0 and max(alpha) == 255, 'banners require genuine alpha'
    card, body = widget('windowType', f'rip_church_ro_{policy}_card')
    index = ('war', 'mercy', 'building', 'mission').index(policy)
    assert dict(card['size']) == {'x': '419', 'y': '74'}
    assert position(card) == {'x': 28, 'y': 188 + index * 78}
    children = list(descendants(body))
    action = f'rip_church_icon_{policy}_button'
    hit, _ = widget('guiButtonType', action, children)
    slot, _ = widget('iconType', f'rip_church_{policy}_slot', children)
    assert position(hit) == {'x': 230, 'y': 0}
    assert position(slot) == {'x': 0, 'y': 0}
    assert hit['quadTextureSprite'] == 'button_type_8'
    assert hit['buttonText'] == 'rip_church_icon_toggle_label'
    assert slot['spriteType'] == 'GFX_rip_church_policy_slot'
    control = controls['custom_button', action]
    gate = ('OR', [('has_country_flag', f'rip_church_icon_{policy}'),
                   (f'rip_church_can_activate_{policy}', 'yes')])
    assert control['trigger'] == [('rip_church_ro_jurisdiction', 'yes'), gate]
    assert control['effect'] == [(f'rip_church_toggle_{policy}_effect', 'yes')]
    assert not any(name.startswith(f'rip_church_ro_{policy}_access_') for kind,name in controls)
    assert controls['custom_icon', f'rip_church_{policy}_active_frame']['potential'] == [('has_country_flag', f'rip_church_icon_{policy}')]
    for suffix in ('label', 'benefit', 'benefit_second', 'state'):
        label, _ = widget('instantTextBoxType', f'rip_church_icon_{policy}_{suffix}', children)
        assert label['font'] == 'vic_18'
        assert label['scripted'] == 'yes'
    cases += 1

# Management and policy actions share the native button frame; navigation uses
# the separate native tab strip. Keep the province-name cell ahead of the
# religion column while allowing long Muscovite labels to remain on one row.
nodes, _ = widget('guiButtonType', 'rip_church_nodes_button')
assert nodes['quadTextureSprite'] == 'button_type_8'
assert nodes['quadTextureSprite'] == hit['quadTextureSprite']
native_action, _ = widget('guiButtonType', 'rip_church_gc_native_privileges_button')
assert native_action['quadTextureSprite'] == nodes['quadTextureSprite']
tab, _ = widget('guiButtonType', 'rip_church_gc_union_tab_union')
assert tab['quadTextureSprite'] == 'GFX_tab_small_116'
_, province_body = widget('windowType', 'countryreligionview_provincelistitem')
province_cells = list(descendants(province_body))
province_name, _ = widget('instantTextBoxType', 'name', province_cells)
province_religion, _ = widget('instantTextBoxType', 'religion', province_cells)
assert province_name['maxWidth'] == '140'
assert position(province_name)['x'] + int(province_name['maxWidth']) < position(province_religion)['x']
if install:
    font_path = install / f"gfx/fonts/{province_name['font']}.fnt"
    advances = {
        int(fields['id']): int(fields['xadvance'])
        for line in font_path.read_text(encoding='utf-8').splitlines()
        if line.startswith('char ')
        for fields in [dict(re.findall(r'(\w+)=(-?\d+)', line))]
    }
    border = dict(province_name['borderSize'])
    text_width = int(province_name['maxWidth']) - 2 * int(border['x'])
    for long_name in ('Ryapolovskiy Yuriev', 'Starodub Ryapolovskiy'):
        measured = sum(advances[ord(character)] for character in long_name)
        assert measured <= text_width, (long_name, measured, text_width)
cases += 1

# The button caption is static (a custom-localisation call inside buttonText is unproven in the engine);
# the state-driven line sits under it: ready is yellow, blocked is red, active is green.
policy_loc = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
for key, marker in (('rip_church_ro_action_ready','§Y10 now, then 3 a month'),
                    ('rip_church_ro_action_fuel','§RNeeds 10 Fervor'),
                    ('rip_church_ro_action_fuel_mission','§RNeeds 20 Fervor'),
                    ('rip_church_ro_action_slot','§RNo free policy slot'),
                    ('rip_church_ro_action_cooldown','§RCooldown: one year'),
                    ('rip_church_ro_action_active','§GActive')):
    assert f'{key}:0 "{marker}' in policy_loc, (key, marker)
assert 'rip_church_icon_toggle_label:0 "Switch on / off"' in policy_loc
for policy in ('war','mercy','building','mission'):
    assert 'buttonText = "rip_church_icon_toggle_label"' in read('interface/countryreligionview.gui')
    assert f'GetChurchIcon{policy.title()}Action' in read('customizable_localization/rip_church_redesign.txt')
    cases += 1

# Execute the GUI's effect, including a stale invocation after its disabled
# state. Recount may refresh derived readouts; rejected transactions cannot pay.
for policy in ('war', 'mission'):
    action = f'rip_church_icon_{policy}_button'
    flag = f'rip_church_icon_{policy}'
    for reason in ('ready', 'fuel', 'slot', 'cooldown', 'cooldown_expired'):
        w, c, p = fixture()
        c['patriarch_authority'] = 0
        c['variables']['muscovy_fervor'] = 25
        if reason == 'fuel': c['variables']['muscovy_fervor'] = 9.99
        if reason == 'slot': c['flags']['rip_church_icon_mercy'] = w.day
        if reason.startswith('cooldown'):
            c['flags'][flag + '_used'] = w.day
            w.day += 365 if reason == 'cooldown_expired' else 364
        w.run('rip_church_ro_recount_effect', c)
        before = deepcopy(c)
        allowed = reason in ('ready', 'cooldown_expired')
        assert click(w, c, action) == allowed, (policy, reason)
        if allowed:
            assert c['variables']['muscovy_fervor'] == 15
            assert flag in c['flags'] and c['modifiers'][flag] == float('inf')
            c['variables']['muscovy_fervor'] = 0
            c['flags']['rip_church_node_novgorod'] = w.day
            assert click(w, c, action), 'an active policy can close during its cooldown at zero fuel'
            assert c['variables']['muscovy_fervor'] == 0
            assert flag not in c['flags'] and flag not in c['modifiers']
            if policy == 'mission':
                assert 'rip_church_node_novgorod' not in c['flags']
        else:
            assert c == before
            w.execute(controls['custom_button', action]['effect'], c)
            assert c == before, (policy, reason, 'stale disabled click changed state')
        cases += 1

# Historical imperial settlements must clear once before adding both markers.
# A second clear used to erase the marker immediately before it in each caller.
events = {dict(body)['id']: body
          for kind, body in parse(read('events/RussianOrthodox.txt'))
          if kind == 'country_event' and 'title' in dict(body)}


def event_option(event_id, option_name):
    return next(body for key, body in events[event_id]
                if key == 'option' and dict(body)['name'] == option_name)


imperial_option = [(key, value) for key, value in event_option(
    'russian_orthodox.11', 'russian_orthodox.11.a') if key not in ('name', 'ai_chance')]
for transaction in (imperial_option, EFFECTS['proclaim_orthodox_empire_effect']):
    assert transaction.count(('rip_ro_clear_historical_policy_effect', 'yes')) == 1
    assert transaction.count(('rip_church_historical_ro_effect', 'yes')) == 1
    w, c, p = fixture()
    c['legitimacy'] = 50
    c['variables']['muscovy_fervor'] = 0
    w.execute(transaction, c)
    assert c['variables']['muscovy_fervor'] == 20
    for marker in ('imperial_orthodox_state', 'orthodox_empire_proclaimed'):
        assert c['modifiers'][marker] == w.day + 7300
    cases += 1
suppression = event_option('russian_orthodox.6', 'russian_orthodox.6.a')
spawn = dict(dict(suppression)['random_owned_province'])['spawn_rebels']
assert dict(spawn)['type'] == 'heretic_rebels'
cases += 1

print(f'PASS: {cases} RO policy navigation, card, transaction and historical regression cases')
print('LIMIT: source contracts and bounded execution; native rendering and hit testing unverified.')
