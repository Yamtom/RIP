"""Check that every number and instruction on the Muscovite Church window reaches the screen, and that it fits.

Why this exists: the window used to read its numbers with a direct [Root.<variable>.GetValue]. In the
scripted church GUI that prints nothing while the variable has never been set, and the window is opened
before the first monthly refresh, so players saw "Fervor: / 100" and "Active policies: /". Every number
now comes from a literal defined_text ladder. This test executes those ladders against the real recount
effect, so a ladder and the mechanic cannot drift apart. It also holds the new reading order to the
rules the player asked for: the order of actions is a numbered step on the screen, not a hint in a
tooltip, and the numbers printed in text match the numbers in the modifiers.

It does not prove EU4 rendering, hit testing or real font metrics: widths use the average advance measured
on an in-game screenshot (vic_18 about 6.3 px per character, vic_22 about 7.5 px).
"""
from math import floor
import re

from church_testlib import TRIGGERS, World, parse
from clausewitz_testlib import ROOT, named_block, read

cases = 0
loc = {key: value.replace('\\n', '\n') for key, value in re.findall(
    r'^ ([\w.]+):\d+ "(.*)"$',
    (ROOT / 'localisation/replace/zzzz_RIP_church_redesign_l_english.yml').read_text(encoding='utf-8-sig'),
    re.M)}
node_loc = {key: value for key, value in re.findall(
    r'^ ([\w.]+):\d+ "(.*)"$',
    (ROOT / 'localisation/replace/zzzz_RIP_church_nodes_l_english.yml').read_text(encoding='utf-8-sig'),
    re.M)}
readouts = {}
for kind, body in parse(read('customizable_localization/rip_church_redesign.txt')):
    if kind == 'defined_text':
        readouts[dict(body)['name']] = [(dict(rows)['trigger'], dict(rows)['localisation_key'])
                                        for key, rows in body if key == 'text']
controls = parse(read('common/custom_gui/RIP_church_controls.txt'))
text_bindings = {dict(body)['name']: dict(body) for kind, body in controls if kind == 'custom_text_box'}
modifiers = {name: dict(body) for name, body in parse(read('common/event_modifiers/RIP_church_redesign_modifiers.txt'))}


def visible(text):
    return re.sub(r'§.', '', text)


def find(entries, kind, name):
    for key, body in entries:
        if isinstance(body, list):
            if key == kind and dict(body).get('name') == name:
                return body
            hit = find(body, kind, name)
            if hit:
                return hit


def widgets(body, ox=0, oy=0):
    """Every named widget below a window, with window-local absolute coordinates."""
    for kind, inner in body:
        if not isinstance(inner, list) or 'name' not in dict(inner):
            continue
        fields = dict(inner)
        pos = dict(fields['position']) if 'position' in fields else {'x': '0', 'y': '0'}
        x, y = ox + int(pos['x']), oy + int(pos['y'])
        yield kind, fields, x, y, ox, oy
        if kind == 'windowType':
            yield from widgets(inner, x, y)


panel = find(parse(read('interface/countryreligionview.gui')), 'windowType', 'rip_church_ro_panel')
assert panel, 'the Muscovite Church panel is missing from countryreligionview.gui'
everything = list(widgets(panel))
texts = {f['name']: f for kind, f, *_ in everything if kind == 'instantTextBoxType'}
buttons = {f['name']: f for kind, f, *_ in everything if kind == 'guiButtonType'}


def render(name, w, c):
    """The first defined_text row whose trigger holds, as the player would read it."""
    assert name in readouts, f'[Root.{name}] is not a defined_text'
    for gate, key in readouts[name]:
        if w.gate(gate, c):
            return visible(loc[key])
    raise AssertionError((name, 'no row matched'))


def screen(key, w, c):
    """An outer panel string with every [Root.GetX] resolved like the engine would."""
    return visible(re.sub(r'\[Root\.(\w+)\]', lambda m: render(m[1], w, c), loc[key]))


def ro_country():
    w = World()
    c = w.country('MOS', 'russian_orthodox')
    w.province(295, c, 'russian_orthodox')
    c['dlcs'] = {'Cradle of Civilization'}
    return w, c


# ---- 1. Nothing on the panel reads a variable directly ---------------------------------
panel_keys = set()
for f in list(texts.values()) + list(buttons.values()):
    for field in ('text', 'buttonText', 'pdx_tooltip'):
        if f.get(field):
            panel_keys.add(f[field])
for key in sorted(panel_keys):
    assert key in loc, f'panel localisation missing: {key}'
    assert '.GetValue' not in loc[key], f'{key}: a variable read directly prints nothing until it is set'
    for name in re.findall(r'\[Root\.(\w+)\]', loc[key]):
        assert name in readouts, f'{key}: [Root.{name}] is not a defined_text'
    cases += 1
for key, value in loc.items():
    if key.startswith(('rip_church_ro_', 'rip_church_icon_', 'rip_church_nodes')):
        assert '.GetValue' not in value, f'{key}: a variable read directly prints nothing until it is set'
        for name in re.findall(r'\[Root\.(\w+)\]', value):
            assert name in readouts, f'{key}: [Root.{name}] is not a defined_text'
for name, rows in readouts.items():
    for _, key in rows:
        assert '[' not in loc[key] or not name.startswith('GetChurchRO'), (
            name, key, 'a ladder leaf must be literal; nested returns are reparsed by the custom GUI')
        assert '.GetValue' not in loc[key], (name, key)
cases += 1

# ---- 2. Every ladder reads like the variable, and an unset variable reads like zero -----
def signed(value):
    n = floor(value)
    return '+15' if n >= 15 else f'+{n}' if n >= 1 else '0' if n == 0 else f'{n}' if n > -30 else '-30'


LADDERS = {
    'GetChurchROFervor': ('rip_church_fervor', lambda v: str(min(100, max(0, floor(v)))), '0'),
    'GetChurchROBase': ('rip_church_fervor_base', lambda v: '0' if v < 1 else f'+{min(9, floor(v))}', '0'),
    'GetChurchRONodeIncome': ('rip_church_node_income', lambda v: '0' if v < 1 else f'+{min(9, floor(v))}', '0'),
    'GetChurchROUpkeep': ('rip_church_fervor_cost', lambda v: '0' if v < 1 else f'-{min(30, floor(v))}', '0'),
    'GetChurchROPolicies': ('rip_church_icons', lambda v: str(min(9, max(0, floor(v)))), '0'),
    'GetChurchROCapacity': ('rip_church_capacity', lambda v: str(max(1, min(9, floor(v)))), '1'),
    'GetChurchRONodes': ('rip_church_nodes', lambda v: str(min(9, max(0, floor(v)))), '0'),
    'GetChurchRONet': ('rip_church_fervor_net', signed, '0'),
}
for name, (variable, expected, unset) in LADDERS.items():
    w, c = ro_country()
    assert render(name, w, c) == unset, (name, 'an unset variable must read as a number, never as nothing')
    samples = [n / 2 for n in range(-90, 241)] + [9.99, -0.5, 0.5]
    for value in samples:
        c['variables'][variable] = value
        assert render(name, w, c) == expected(value), (name, value, render(name, w, c), expected(value))
    cases += 1

# ---- 3. The tiles follow the mechanic: recount, then read what the player reads ---------
BASE = {0: 2, 0.3: 3, 0.65: 4, 0.9: 5}
CAPACITY = {0: 1, 0.3: 2, 0.65: 3, 0.9: 4}
POLICIES = ('war', 'mercy', 'building', 'mission')

w, c = ro_country()
assert screen('rip_church_ro_fervor_value', w, c) == '0 / 100'
assert screen('rip_church_ro_fervor_sub', w, c) == 'Net 0 / month'
assert screen('rip_church_ro_nodes_value', w, c) == '0 / 1'
assert screen('rip_church_ro_nodes_sub', w, c) == '0 Fervor / mo'
assert screen('rip_church_ro_policies_value', w, c) == '0 / 1'
assert screen('rip_church_ro_policies_sub', w, c) == '0 Fervor / mo'
cases += 1                                                  # a country that never ran the refresh

for authority, base in BASE.items():
    for active in range(0, 5):
        for nodes in (0, 1, 2):
            for fervor in (0, 9, 10, 57, 100):
                w, c = ro_country()
                c['patriarch_authority'] = authority
                c['variables']['rip_church_fervor'] = fervor
                c['variables']['rip_church_nodes'] = nodes
                for policy in POLICIES[:active]:
                    c['flags'][f'rip_church_icon_{policy}'] = w.day
                w.run('rip_church_ro_recount_effect', c)
                net = base + 3 * nodes - 3 * active
                assert screen('rip_church_ro_fervor_value', w, c) == f'{fervor} / 100'
                assert screen('rip_church_ro_fervor_sub', w, c) == f'Net {signed(net)} / month', (authority, active, nodes)
                assert screen('rip_church_ro_nodes_value', w, c) == f'{nodes} / 1'
                assert screen('rip_church_ro_nodes_sub', w, c) == f'{signed(3 * nodes)} Fervor / mo'
                assert screen('rip_church_ro_policies_value', w, c) == f'{active} / {CAPACITY[authority]}'
                assert screen('rip_church_ro_policies_sub', w, c) == f'{-3 * active if active else 0} Fervor / mo'
                cases += 1
w, c = ro_country()
c['flags']['rip_church_ro_schismatic'] = w.day
assert screen('rip_church_ro_nodes_value', w, c) == '0 / 2'
cases += 1

# The tooltips print the same breakdown the tile does.
w, c = ro_country()
c['patriarch_authority'] = 0.65
c['flags']['rip_church_icon_mission'] = w.day
c['variables']['rip_church_nodes'] = 1
w.run('rip_church_ro_recount_effect', c)
tip = screen('rip_church_ro_fervor_value_tt', w, c)
assert 'authority +4, nodes +3, policies -3, net +4' in tip, tip
cases += 1

# ---- 4. The lock reason names the gate that is actually shut -------------------------
def hint(mission=True, dlc=True, nodes=0, fervor=50, schism=False):
    w, c = ro_country()
    if mission:
        c['flags']['rip_church_icon_mission'] = w.day
    if not dlc:
        c['dlcs'].clear()
    if schism:
        c['flags']['rip_church_ro_schismatic'] = w.day
    c['variables'].update(rip_church_nodes=nodes, rip_church_fervor=fervor)
    return render('GetChurchRONodeHint', w, c)


assert 'Mission policy' in hint(mission=False)
assert 'Mission policy' in hint(mission=False, dlc=False), 'the policy comes before the DLC'
assert 'Cradle of Civilization' in hint(dlc=False)
assert 'Node limit reached' in hint(nodes=1)
assert 'Node limit reached' not in hint(nodes=1, schism=True), 'renouncing communion permits a second node'
assert 'Node limit reached' in hint(nodes=2, schism=True)
assert 'costs 10 Fervor' in hint(fervor=9) and 'costs 10 Fervor' not in hint(fervor=10)
assert 'No trade node qualifies' in hint(fervor=10), 'no eligible province is modelled in this fixture'
assert hint(nodes=1, schism=True).startswith('A node can be funded')
stub = TRIGGERS['rip_church_ro_can_open_network_menu']
try:
    TRIGGERS['rip_church_ro_can_open_network_menu'] = [('always', 'yes')]
    assert hint().startswith('A node can be funded')
finally:
    TRIGGERS['rip_church_ro_can_open_network_menu'] = stub
cases += 1

# The hint repeats the generated rules; if those change, the words must change with them.
nodes_source = read('common/scripted_triggers/rip_church_nodes_generated.txt')
openers = re.findall(r'^(rip_church_node_\w+_can_open) = \{', nodes_source, re.M)
assert len(openers) >= 60, len(openers)
for name in openers:
    block = named_block(nodes_source, name)
    assert 'check_variable = { which = rip_church_fervor value = 10 }' in block, name
    assert 'NOT = { check_variable = { which = rip_church_nodes value = 1 } }' in block, name
    assert 'has_country_flag = rip_church_ro_schismatic NOT = { check_variable = { which = rip_church_nodes value = 2 } }' in block, name
    eligible = named_block(nodes_source, name.replace('_can_open', '_eligible'))
    assert 'has_country_flag = rip_church_icon_mission' in eligible and 'has_dlc = "Cradle of Civilization"' in eligible, name
cases += 1

# ---- 5. The three steps: the order of actions is on the screen -----------------------------
def step(n, **kw):
    w, c = ro_country()
    c['patriarch_authority'] = 0.9
    c['variables']['rip_church_fervor'] = kw.get('fervor', 50)
    c['variables']['rip_church_nodes'] = kw.get('nodes', 0)
    w.run('rip_church_ro_recount_effect', c)
    if kw.get('mission'):
        c['flags']['rip_church_icon_mission'] = w.day
    if kw.get('slot') is False:
        for policy in ('war', 'mercy', 'building', 'mission')[:4]:
            c['flags'][f'rip_church_icon_{policy}'] = w.day
        c['flags'].pop('rip_church_icon_mission') if not kw.get('mission') else None
        c['patriarch_authority'] = 0
        w.run('rip_church_ro_recount_effect', c)
    if kw.get('schism'):
        c['flags']['rip_church_ro_schismatic'] = w.day
    if kw.get('can_open') is not None:
        TRIGGERS['rip_church_ro_can_open_network_menu'] = [('always', 'yes' if kw['can_open'] else 'no')]
    try:
        return render(f'GetChurchROStep{n}', w, c)
    finally:
        TRIGGERS['rip_church_ro_can_open_network_menu'] = stub


assert step(1, mission=True).startswith('1. Mission policy is on')
assert step(1, fervor=19).startswith('1. Mission needs 20 Fervor')
assert step(1, fervor=20).startswith('1. Switch on the Mission policy')
assert step(1, slot=False).startswith('1. Mission needs a free policy slot')
assert step(1).startswith('1. Switch on the Mission policy')
assert step(2).startswith('2. Fund a node, after Mission'), 'step 2 waits for step 1'
assert step(2, mission=True, fervor=9).startswith('2. A node costs 10 Fervor')
assert step(2, mission=True, can_open=False).startswith('2. No trade node qualifies')
assert step(2, mission=True, can_open=True).startswith('2. Fund a trade node: 10 Fervor')
assert step(2, mission=True, nodes=1).startswith('2. Node funded: +3 Fervor/month')
assert step(2, mission=True, nodes=2, schism=True).startswith('2. Two nodes: +6 Fervor/month')
assert step(2, mission=True, nodes=1, schism=True).startswith('2. 1 node funded, 1 more allowed')
assert step(3).startswith('3. Then choose Missionary Network')
assert step(3, nodes=1).startswith('3. In the funded node, choose Missionary Network')
cases += 1

# ---- 6. What the text promises is what the modifiers deliver --------------------------------
def pct(value):
    return f'{abs(value) * 100:g}%'


def signed_pct(value):
    return ('+' if value > 0 else '-') + pct(value)


war = loc['rip_church_icon_war_button_tt']
frontier, wartime = modifiers['rip_church_frontier_watch'], modifiers['rip_church_icon_war_steppe']
assert f"{signed_pct(float(frontier['local_defensiveness']))} defensiveness" in war
assert f"+{float(frontier['local_hostile_attrition']):g} attrition" in war
assert f"{signed_pct(float(wartime['discipline']))} discipline" in war
assert f"{signed_pct(float(wartime['manpower_recovery_speed']))} manpower recovery" in war
clemency = modifiers['rip_church_eastern_clemency']
assert f"{signed_pct(float(clemency['local_autonomy']))} local autonomy" in loc['rip_church_icon_mercy_button_tt']
assert f"{float(clemency['local_unrest']):g} local unrest" in loc['rip_church_icon_mercy_button_tt']
drive = modifiers['rip_church_cathedral_drive']
assert f"{signed_pct(float(drive['local_build_cost']))} construction cost" in loc['rip_church_icon_building_button_tt']
preaching = modifiers['rip_church_preaching']
assert f"{signed_pct(float(preaching['local_missionary_strength']))} local missionary strength" in loc['rip_church_icon_mission_button_tt']
courtyards = modifiers['rip_church_node_courtyards']
for text in (loc['rip_church_nodes.1.d'], loc['rip_church_ro_nodes_value_tt'], next(iter(node_loc.values()))):
    assert f"{signed_pct(float(courtyards['province_trade_power_modifier']))} trade power" in text, text
for text in (loc['rip_church_nodes.1.d'], loc['rip_church_ro_nodes_value_tt']):
    assert f"{signed_pct(float(courtyards['local_missionary_strength']))} missionary strength" in text, text
# Card teasers: the same numbers, shortened.
assert 'Defence +20%' in loc['rip_church_icon_war_benefit'] and 'vs nomads +5%' in loc['rip_church_icon_war_benefit']
assert 'Autonomy -10%' in loc['rip_church_icon_mercy_benefit'] and 'Unrest -1' in loc['rip_church_icon_mercy_benefit']
assert 'Build cost -25%' in loc['rip_church_icon_building_benefit']
assert 'Missionary +2%' in loc['rip_church_icon_mission_benefit']
# The price and the return are the ones the scripts charge and pay.
for key in ('rip_church_ro_fervor_value_tt', 'rip_church_ro_nodes_value_tt',
            'rip_church_ro_steps_title_tt', 'rip_church_ro_step2_tt', 'rip_church_nodes.1.d'):
    assert re.search(r'10 Fervor|§Y10§!', loc[key]), key
assert '§R3 Fervor§! a month' in loc['rip_church_ro_policies_value_tt']
assert 'costs §Y10 Fervor§! once' in loc['rip_church_nodes.1.d'] and '+3 Fervor§! a month' in loc['rip_church_nodes.1.d']
assert 'rip_church_ro_action_ready' in loc and '10 now, 3/mo' in loc['rip_church_ro_action_ready']
assert 'Costs §Y10 Fervor§! to start and §R3 Fervor§! a month' in loc['rip_church_icon_war_button_tt']
cases += 1

# The node menu: a pair of lines for every node, each with its price and return, and the keys exist.
event = dict(parse(read('events/RIP_ChurchNodes_generated.txt'))[1][1])
assert event['title'] == 'rip_church_nodes.1.t' and event['desc'] == 'rip_church_nodes.1.d'
options = [dict(body) for key, body in parse(read('events/RIP_ChurchNodes_generated.txt'))[1][1] if key == 'option']
funds = [o for o in options if o['name'].endswith('_fund')]
closes = [o for o in options if o['name'].endswith('_close') and o['name'] != 'rip_church_close']
assert len(funds) == len(closes) >= 60
for option in funds + closes:
    assert option['name'] in node_loc, option['name']
    assert re.search(r'\$\w+\$', node_loc[option['name']]), 'the node name comes from the trade-node key'
for option in funds:
    assert '-10 Fervor' in node_loc[option['name']] and '+3 Fervor' in node_loc[option['name']], option['name']
for option in closes:
    assert '-3 Fervor' in node_loc[option['name']] and 'not refunded' in node_loc[option['name']], option['name']
assert 'rip_church_close' in loc
cases += 1

# ---- 7. Bindings, widgets and tooltips agree --------------------------------------------
panel_text_bindings = {name for name in text_bindings if name.startswith(('rip_church_ro_', 'rip_church_icon_'))}
assert panel_text_bindings == set(texts), (
    'orphan bindings', sorted(panel_text_bindings - set(texts)), 'unbound widgets', sorted(set(texts) - panel_text_bindings))
for name, binding in text_bindings.items():
    if name in texts and 'tooltip' in binding:
        assert binding['tooltip'] in loc, (name, binding['tooltip'])
        assert texts[name].get('pdx_tooltip') == binding['tooltip'] or texts[name].get('pdx_tooltip') is None, name
for name in ('rip_church_ro_fervor', 'rip_church_ro_nodes', 'rip_church_ro_policies'):
    assert name + '_tile' in {f['name'] for kind, f, *_ in everything if kind == 'windowType'}
    for part in ('label', 'value', 'sub'):
        assert text_bindings[f'{name}_{part}']['tooltip'] == f'{name}_{part}_tt'
for n in (1, 2, 3):
    assert text_bindings[f'rip_church_ro_step{n}']['tooltip'] == f'rip_church_ro_step{n}_tt'
cases += 1

# ---- 8. Geometry: inside the frame, no two readable boxes overlap, text fits ----------------
SURFACE = (13, 13, 462, 533)                     # inner surface of the 475x560 Coptic frame
ADVANCE = {'vic_18': 6.33, 'vic_22': 7.5}        # px per character, estimated from an in-game screenshot
LINE = {'vic_18': 18, 'vic_22': 24}
BUTTON = {'GFX_standard_button_224': (224, 32), 'GFX_rip_church_policy_select': (58, 58), 'button_type_8': (189, 31)}


def longest(text):
    """The widest rendering of a loc value: every [Root.GetX] becomes its longest leaf."""
    def widest(value):
        return max(len(visible(line)) for line in value.split('\n'))
    return re.sub(r'\[Root\.(\w+)\]',
                  lambda m: max((longest(loc[key]) for _, key in readouts[m[1]]), key=widest), text)


boxes = {}
for kind, f, x, y, ox, oy in everything:
    if kind == 'instantTextBoxType':
        w_, h_ = int(f['maxWidth']), int(f['maxHeight'])
        shown = longest(loc[f['text']])
        lines = visible(shown).split('\n')
        font = f['font']
        assert max(len(line) for line in lines) * ADVANCE[font] <= w_, (f['name'], 'text may wrap', lines, w_)
        assert len(lines) * LINE[font] <= h_, (f['name'], 'text needs more lines than the box has', lines, h_)
        boxes[f['name']] = (x, y, x + w_, y + h_)
    elif kind == 'guiButtonType':
        bw, bh = BUTTON[f['quadTextureSprite']]
        boxes[f['name']] = (x, y, x + bw, y + bh)
        if f.get('buttonText'):
            shown = visible(loc[f['buttonText']])
            assert len(shown) * ADVANCE['vic_18'] <= bw - 30, (f['name'], 'button label too long', shown)
for name, (x0, y0, x1, y1) in boxes.items():
    assert SURFACE[0] <= x0 and x1 <= SURFACE[2] and SURFACE[1] <= y0 and y1 <= SURFACE[3], (name, boxes[name])
names = sorted(boxes)
for i, a in enumerate(names):
    for b in names[i + 1:]:
        ax0, ay0, ax1, ay1 = boxes[a]
        bx0, by0, bx1, by1 = boxes[b]
        assert ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0, ('overlap', a, boxes[a], b, boxes[b])
cases += 1

# Reading order is the question order: resources, policies, the three steps, the schism action last.
y_of = {name: boxes[name][1] for name in boxes}
tile_bottom = max(boxes[f'rip_church_ro_{k}_sub'][3] for k in ('fervor', 'nodes', 'policies'))
tile_x = [min(boxes[f'rip_church_ro_{k}_{p}'][0] for p in ('label', 'value', 'sub')) for k in ('fervor', 'nodes', 'policies')]
assert tile_x == sorted(tile_x), 'the cycle reads left to right: Fervor, nodes, policies'
arrows = sorted((x, y) for kind, f, x, y, *_ in everything if kind == 'iconType' and f['name'].startswith('rip_church_ro_cycle_arrow'))
assert len(arrows) == 2 and tile_x[0] < arrows[0][0] < tile_x[1] < arrows[1][0] < tile_x[2], 'an arrow sits between each pair of tiles'
cards = {f['name']: (x, y) for kind, f, x, y, *_ in everything if kind == 'windowType' and f['name'].endswith('_card')}
policy_cards = [cards[f'rip_church_ro_{p}_card'] for p in POLICIES]
cards_top = min(y for _, y in policy_cards)
cards_bottom = max(y for _, y in policy_cards) + 172
assert tile_bottom <= y_of['rip_church_ro_policies_title'], 'tiles must end above the policies ribbon'
assert y_of['rip_church_ro_policies_title'] + 20 <= cards_top, 'the ribbon title sits above the first card'
assert cards_bottom <= y_of['rip_church_ro_steps_title'], 'policies must end above the steps'
assert y_of['rip_church_ro_steps_title'] + 20 <= y_of['rip_church_ro_step1'] < y_of['rip_church_ro_step2'] < y_of['rip_church_ro_step3'], \
    'the steps are numbered in the order they are read'
assert boxes['rip_church_nodes_button'][1] <= boxes['rip_church_ro_step2'][1] + 10 and \
       boxes['rip_church_ro_step2'][3] > boxes['rip_church_nodes_button'][1], 'the button of step 2 shares its row'
assert boxes['rip_church_nodes_button'][3] <= boxes['rip_church_ro_step3'][1] + 4, 'the third step is below the button'
assert boxes['rip_church_ro_step3'][3] <= boxes['rip_church_reconcile_button'][1], 'the schism action comes last'
# The instruction is part of the window's main reading line, never a small caption under the last button.
assert max(boxes[n][3] for n in boxes if n.startswith('rip_church_ro_step')) < boxes['rip_church_reconcile_button'][1]
cases += 1

print(f'PASS: {cases} Muscovite Church window readout, tile, step, lock-reason, number-parity, binding and geometry cases')
print('LIMIT: executes source contracts with an estimated glyph advance; native rendering, hit testing and font metrics unverified.')
