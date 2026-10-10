"""Check Muscovite policy navigation, click targets and guarded transactions.

The bounded church interpreter executes source effects; it does not prove EU4
rendering, mouse hit testing, AI behaviour or save/load persistence.
"""
from copy import deepcopy
import struct

from church_testlib import EFFECTS, fixture, parse
from clausewitz_testlib import read, vanilla_root


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
assert native['scripted'] == route['scripted'] == 'yes'
assert cover['alwaystransparent'] == 'no', 'cover must intercept the retired selector'
assert cover['spriteType'] == 'GFX_rip_church_gc_selector_surface'
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
    for kind, name in (('guiButtonType', 'pick_icon_button'),
                       ('iconType', 'no_current_icon'), ('iconType', 'current_icon')):
        assert widget(kind, name, host_children)[0] == widget(kind, name, vanilla_gui)[0], name
    for asset in ('copts_blessing_select', 'copts_blessing_slot'):
        image = (install / f'gfx/interface/{asset}.dds').read_bytes()
        assert image[:4] == b'DDS ' and struct.unpack_from('<II', image, 12) == (58, 58)

cases = 0
for faith in ('russian_orthodox', 'orthodox', 'greek_catholic', 'catholic'):
    w, c, p = fixture(faith)
    before = deepcopy(c)
    eligible = faith == 'russian_orthodox'
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

# All four cards use local coordinates and the actual 58px policy click sprite.
# Readouts stay outside that target and describe the same activation transaction.
for policy in ('war', 'mercy', 'building', 'mission'):
    card, body = widget('windowType', f'rip_church_ro_{policy}_card')
    assert dict(card['size']) == {'x': '198', 'y': '124'}
    children = list(descendants(body))
    action = f'rip_church_icon_{policy}_button'
    hit, _ = widget('guiButtonType', action, children)
    slot, _ = widget('iconType', f'rip_church_{policy}_slot', children)
    assert position(hit) == position(slot) == {'x': 8, 'y': 0}
    assert hit['quadTextureSprite'] == 'GFX_rip_church_policy_select'
    assert hit.get('scale', '1') == '1' and hit['buttonText'] == ''
    assert slot['spriteType'] == 'GFX_rip_church_policy_slot'
    control = controls['custom_button', action]
    gate = ('OR', [('has_country_flag', f'rip_church_icon_{policy}'),
                   (f'rip_church_can_activate_{policy}', 'yes')])
    assert control['trigger'] == [('religion', 'russian_orthodox'), gate]
    assert control['effect'] == [(f'rip_church_toggle_{policy}_effect', 'yes')]
    # One state signal per policy: the lit frame and the Active/Inactive line. A check/cross badge
    # on the slot repeated both (a red cross beside "Inactive"), so neither widget may return.
    for state in ('ready', 'blocked'):
        assert ('custom_icon', f'rip_church_ro_{policy}_access_{state}') not in controls
        assert not [1 for _, fields, _ in children if fields['name'] == f'rip_church_ro_{policy}_access_{state}']
    frame, _ = widget('iconType', f'rip_church_{policy}_active_frame', children)
    assert frame['alwaystransparent'] == 'yes', 'the lit frame must not steal a click from the policy'
    for suffix in ('label', 'state', 'action', 'benefit'):
        label, _ = widget('instantTextBoxType', f'rip_church_icon_{policy}_{suffix}', children)
        assert label['font'] == 'vic_18' and label['scripted'] == 'yes'
    cases += 1

# Execute the GUI's effect, including a stale invocation after its disabled
# state. Recount may refresh derived readouts; rejected transactions cannot pay.
for policy in ('war', 'mission'):
    action = f'rip_church_icon_{policy}_button'
    flag = f'rip_church_icon_{policy}'
    for reason in ('ready', 'fuel', 'slot', 'cooldown', 'cooldown_expired'):
        w, c, p = fixture()
        c['patriarch_authority'] = 0
        c['variables']['rip_church_fervor'] = 25
        if reason == 'fuel': c['variables']['rip_church_fervor'] = 9.99
        if reason == 'slot': c['flags']['rip_church_icon_mercy'] = w.day
        if reason.startswith('cooldown'):
            c['flags'][flag + '_used'] = w.day
            w.day += 365 if reason == 'cooldown_expired' else 364
        w.run('rip_church_ro_recount_effect', c)
        before = deepcopy(c)
        allowed = reason in ('ready', 'cooldown_expired')
        assert click(w, c, action) == allowed, (policy, reason)
        if allowed:
            assert c['variables']['rip_church_fervor'] == 15
            assert flag in c['flags'] and c['modifiers'][flag] == float('inf')
            c['variables']['rip_church_fervor'] = 0
            c['flags']['rip_church_node_novgorod'] = w.day
            assert click(w, c, action), 'an active policy can close during its cooldown at zero fuel'
            assert c['variables']['rip_church_fervor'] == 0
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
    c['variables']['rip_church_fervor'] = 0
    w.execute(transaction, c)
    assert c['variables']['rip_church_fervor'] == 20
    for marker in ('imperial_orthodox_state', 'orthodox_empire_proclaimed'):
        assert c['modifiers'][marker] == w.day + 7300
    cases += 1
suppression = event_option('russian_orthodox.6', 'russian_orthodox.6.a')
spawn = dict(dict(suppression)['random_owned_province'])['spawn_rebels']
assert dict(spawn)['type'] == 'heretic_rebels'
cases += 1

print(f'PASS: {cases} RO policy navigation, card, transaction and historical regression cases')
print('LIMIT: source contracts and bounded execution; native rendering and hit testing unverified.')
