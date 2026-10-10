"""Check that every number on the Muscovite Church panel reaches the screen, and that the panel fits.

Why this exists: the panel used to read its numbers with a direct [Root.<variable>.GetValue].
In the scripted church GUI that prints nothing while the variable has never been set, and the
window is opened before the first monthly refresh, so players saw "Fervor: / 100" and
"Active policies: /". The numbers now come from literal defined_text ladders. This test executes
those ladders against the real recount effect, so a ladder and the mechanic cannot drift apart,
and it checks the layout against an estimated glyph advance.

It does not prove EU4 rendering, hit testing or real font metrics: widths use the average advance
measured on an in-game screenshot (vic_18 about 6.3 px per character, vic_22 about 7.5 px).
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
readouts = {}
for kind, body in parse(read('customizable_localization/rip_church_redesign.txt')):
    if kind == 'defined_text':
        readouts[dict(body)['name']] = [(dict(rows)['trigger'], dict(rows)['localisation_key'])
                                        for key, rows in body if key == 'text']
controls = parse(read('common/custom_gui/RIP_church_controls.txt'))
text_bindings = {dict(body)['name']: dict(body) for kind, body in controls if kind == 'custom_text_box'}


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
for name, rows in readouts.items():
    for _, key in rows:
        assert '[' not in loc[key] or not name.startswith('GetChurchRO'), (
            name, key, 'a ladder leaf must be literal; nested returns are reparsed by the custom GUI')
        assert '.GetValue' not in loc[key], (name, key)
cases += 1

# ---- 2. Every ladder reads like the variable, and an unset variable reads like zero -----
def signed(value):
    n = floor(value)
    return '+9' if n >= 9 else f'+{n}' if n >= 1 else '0' if n == 0 else f'{n}' if n > -30 else '-30'


LADDERS = {
    'GetChurchROFervor': ('rip_church_fervor', lambda v: str(min(100, max(0, floor(v)))), '0'),
    'GetChurchROIncome': ('rip_church_fervor_income', lambda v: '0' if v < 1 else f'+{min(9, floor(v))}', '0'),
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
INCOME = {0: 2, 0.3: 3, 0.65: 4, 0.9: 5}
CAPACITY = {0: 1, 0.3: 2, 0.65: 3, 0.9: 4}
UPKEEP = {0: 0, 1: 2, 2: 4, 3: 8, 4: 14}
POLICIES = ('war', 'mercy', 'building', 'mission')

w, c = ro_country()
assert screen('rip_church_ro_fervor_value', w, c) == '0 / 100'
assert screen('rip_church_ro_policies_value', w, c) == '0 / 1'
assert screen('rip_church_ro_monthly_value', w, c) == '0'
assert screen('rip_church_ro_monthly_sub', w, c) == '0 income · 0 upkeep'
assert screen('rip_church_ro_network', w, c) == 'Funded nodes: 0 / 1'
cases += 1                                                  # a country that never ran the refresh

for authority in INCOME:
    for active in range(0, 5):
        for nodes in (0, 1):
            for fervor in (0, 9, 10, 57, 100):
                w, c = ro_country()
                c['patriarch_authority'] = authority
                c['variables']['rip_church_fervor'] = fervor
                c['variables']['rip_church_nodes'] = nodes
                for policy in POLICIES[:active]:
                    c['flags'][f'rip_church_icon_{policy}'] = w.day
                w.run('rip_church_ro_recount_effect', c)
                upkeep = UPKEEP[active] + 2 * nodes
                net = INCOME[authority] - upkeep
                assert screen('rip_church_ro_fervor_value', w, c) == f'{fervor} / 100'
                assert screen('rip_church_ro_policies_value', w, c) == f'{active} / {CAPACITY[authority]}'
                assert screen('rip_church_ro_monthly_value', w, c) == signed(net), (authority, active, nodes)
                assert screen('rip_church_ro_monthly_sub', w, c) == (
                    f'+{INCOME[authority]} income · ' + (f'-{upkeep}' if upkeep else '0') + ' upkeep')
                assert screen('rip_church_ro_network', w, c) == f'Funded nodes: {nodes} / 1'
                cases += 1
w, c = ro_country()
c['flags']['rip_church_ro_schismatic'] = w.day
assert screen('rip_church_ro_network', w, c) == 'Funded nodes: 0 / 2'
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


assert 'Activate the Mission policy' in hint(mission=False)
assert 'Activate the Mission policy' in hint(mission=False, dlc=False), 'the policy comes before the DLC'
assert 'Cradle of Civilization' in hint(dlc=False)
assert 'Node limit reached' in hint(nodes=1)
assert 'Node limit reached' not in hint(nodes=1, schism=True), 'renouncing communion permits a second node'
assert 'Node limit reached' in hint(nodes=2, schism=True)
assert 'needs 12 Fervor' in hint(fervor=11) and 'needs 12 Fervor' not in hint(fervor=12)
assert 'No trade node meets' in hint(fervor=12), 'no eligible province is modelled in this fixture'
assert hint(nodes=1, schism=True).startswith('Ready')
stub = TRIGGERS['rip_church_ro_can_open_network_menu']
try:
    TRIGGERS['rip_church_ro_can_open_network_menu'] = [('always', 'yes')]
    assert hint().startswith('Ready: open the menu')
finally:
    TRIGGERS['rip_church_ro_can_open_network_menu'] = stub
cases += 1

# The hint repeats the generated rules; if those change, the words must change with them.
nodes_source = read('common/scripted_triggers/rip_church_nodes_generated.txt')
openers = re.findall(r'^(rip_church_node_\w+_can_open) = \{', nodes_source, re.M)
assert len(openers) >= 60, len(openers)
for name in openers:
    block = named_block(nodes_source, name)
    assert 'check_variable = { which = rip_church_fervor value = 12 }' in block, name
    assert 'NOT = { check_variable = { which = rip_church_nodes value = 1 } }' in block, name
    assert 'has_country_flag = rip_church_ro_schismatic NOT = { check_variable = { which = rip_church_nodes value = 2 } }' in block, name
    eligible = named_block(nodes_source, name.replace('_can_open', '_eligible'))
    assert 'has_country_flag = rip_church_icon_mission' in eligible and 'has_dlc = "Cradle of Civilization"' in eligible, name
cases += 1

# ---- 5. Bindings, widgets and tooltips agree --------------------------------------------
panel_text_bindings = {name for name in text_bindings if name.startswith(('rip_church_ro_', 'rip_church_icon_'))}
assert panel_text_bindings == set(texts), (
    'orphan bindings', sorted(panel_text_bindings - set(texts)), 'unbound widgets', sorted(set(texts) - panel_text_bindings))
for name, binding in text_bindings.items():
    if name in texts and 'tooltip' in binding:
        assert binding['tooltip'] in loc, (name, binding['tooltip'])
        assert texts[name].get('pdx_tooltip') == binding['tooltip'] or texts[name].get('pdx_tooltip') is None, name
for name in ('rip_church_ro_fervor', 'rip_church_ro_monthly', 'rip_church_ro_policies'):
    assert name + '_tile' in {f['name'] for kind, f, *_ in everything if kind == 'windowType'}
cases += 1

# ---- 6. Geometry: inside the dialog surface, no two readable boxes overlap, text fits ----
SURFACE = (13, 13, 462, 647)                     # inner surface of the 475x660 frame
ADVANCE = {'vic_18': 6.33, 'vic_22': 7.5}        # px per character, estimated from an in-game screenshot
LINE = {'vic_18': 18, 'vic_22': 24}
BUTTON = {'GFX_standard_button_224': (224, 32), 'GFX_rip_church_policy_select': (58, 58)}


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

# Reading order is the question order: resources, policies, funding, and the schism action last.
y_of = {name: boxes[name][1] for name in boxes}
sections = {f['name']: y for kind, f, _, y, *_ in everything if kind == 'iconType' and f['name'].endswith('_title_banner')}
tile_bottom = max(boxes[f'rip_church_ro_{k}_sub'][3] for k in ('fervor', 'monthly', 'policies'))
cards = {f['name']: (x, y) for kind, f, x, y, *_ in everything if kind == 'windowType' and f['name'].endswith('_card')}
policy_cards = [cards[f'rip_church_ro_{p}_card'] for p in POLICIES]
cards_bottom = max(y for _, y in policy_cards) + 124
assert tile_bottom <= sections['rip_church_ro_policies_title_banner'], 'tiles must end above the policies banner'
assert min(y for _, y in policy_cards) - sections['rip_church_ro_policies_title_banner'] >= 35, 'banner is 29 rows tall'
assert cards_bottom <= sections['rip_church_ro_funding_title_banner'], 'policies must end above the funding banner'
assert sections['rip_church_ro_funding_title_banner'] + 35 <= y_of['rip_church_ro_network'] < y_of['rip_church_ro_mission_cost'] \
    < y_of['rip_church_nodes_button'] < y_of['rip_church_reconcile_button']
assert boxes['rip_church_nodes_button'][3] < boxes['rip_church_reconcile_button'][1], 'two action buttons must not touch'
cases += 1

print(f'PASS: {cases} Muscovite Church panel readout, tile, lock-reason, binding and geometry cases')
print('LIMIT: executes source contracts with an estimated glyph advance; native rendering, hit testing and font metrics unverified.')
