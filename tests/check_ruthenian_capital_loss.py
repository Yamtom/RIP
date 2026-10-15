"""Execute the namesake-seat decisions against the live source.

A Ruthenian realm that has gone more than 25 years without its namesake seat is
offered, one decision per seat it now holds, the name of another principality.
This checks the table, the clock behind the 25 years, who sees which decision, and
what taking one does. It is a bounded source model, not evidence of the engine's
own behaviour: change_tag, the capital move and the mission swap are recorded, not
simulated, and nothing here runs the game.
"""
import re

from church_testlib import World, EFFECTS, TRIGGERS, parse
from clausewitz_testlib import ROOT, read, vanilla_root

TRIGGERS.update(parse(read('common/scripted_triggers/rip_capital_loss_triggers.txt')))
EFFECTS.update(parse(read('common/scripted_effects/rip_capital_loss_effects.txt')))

DAYS = 25 * 365


class Realm(World):
    """Church world that records the tag change instead of performing it."""

    def __init__(self):
        super().__init__()
        self.done = []

    def execute(self, items, scope, root=None, prev=None):
        rest = []
        for key, value in items:
            if key == 'set_capital':
                scope['capital'] = str(value)
                self.done.append((key, value))
            elif key in ('change_tag', 'swap_non_generic_missions', 'on_change_tag_effect'):
                self.done.append((key, value))
            else:
                rest.append((key, value))
        super().execute(rest, scope, root, prev)


def block(pairs, name):
    found = [v for k, v in pairs if k == name]
    assert len(found) == 1, (name, len(found))
    return found[0]


# --- 1. the table -----------------------------------------------------------
table = {}
for key, row in block(TRIGGERS['rip_namesake_seat_missing'], 'OR'):
    assert key == 'AND'
    tag = block(row, 'tag')
    seat = block(block(row, 'NOT'), 'owns')
    assert tag not in table, 'a tag has one row'
    table[tag] = int(seat)
assert len(table) == 12 and len(set(table.values())) == 12, 'one seat per realm, one realm per seat'

# The mod inherits most country and province history from vanilla, so a tag or a
# province is real if either the mod or the installed game defines it.
game = vanilla_root()
roots = [ROOT] + ([game] if game is not None else [])
if game is None:
    print('NOTE: vanilla EU4 not found; tag and province existence is checked in the mod only')


def defined(directory, pattern):
    return any(re.match(pattern, p.name) for r in roots for p in (r / directory).glob('*.txt'))


tag_files = ''.join((r / 'common/country_tags' / name).read_text(encoding='latin-1')
                    for r in roots for name in ('01_countries.txt', '00_countries.txt') if (r / 'common/country_tags' / name).exists())
for tag, seat in table.items():
    if game is not None:
        assert re.search(rf'^{tag}\s*=', tag_files, re.M), tag + ' is not a known tag'
        assert defined('history/countries', rf'{tag} - '), tag + ' has no country history'
        assert defined('history/provinces', rf'{seat}[ -]'), f'{tag}: province {seat} has no history file'
assert 'TRV' not in table, 'TRV is also vanilla Travancore; the table must not offer it'
cases = 1

# --- 2. one decision per row, each reading the same table --------------------
decisions = dict(parse(read('decisions/RIP_CapitalLoss.txt'))[0][1])
assert set(decisions) == {'rip_seat_become_' + t.lower() for t in table}, 'one decision per row of the table'
for tag, seat in table.items():
    body = decisions['rip_seat_become_' + tag.lower()]
    potential, effect = block(body, 'potential'), block(body, 'effect')
    assert ('rip_namesake_seat_lost_long', 'yes') in potential, tag
    assert ('NOT', [('tag', tag)]) in potential, tag + ': a realm is not offered its own name'
    assert ('NOT', [('exists', tag)]) in potential, tag + ': a name already in use is not offered'
    assert ('owns', str(seat)) in potential, f'{tag}: the seat {seat} must be held to take the name'
    assert block(block(body, 'provinces_to_highlight'), 'province_id') == str(seat)
    assert ('change_tag', tag) in effect and ('set_capital', str(seat)) in effect, tag
    # EU4 1.37.5 logged "Unknown effect type. Key: capital" for a decision effect; the effect is set_capital.
    assert 'capital' not in [k for k, _ in effect], tag + ': capital = N is a trigger, not an effect'
    assert ('clr_country_flag', 'rip_namesake_seat_lost') in effect, tag + ': the clock must reset'
    assert ('swap_non_generic_missions', 'yes') in effect and ('on_change_tag_effect', 'yes') in effect, tag
    assert block(block(body, 'ai_will_do'), 'factor') == '0', tag + ': the AI never takes it'
    assert ('set_country_flag', 'formed_polotsk_nation_flag') in effect if tag == 'PLT' else True
cases += 1

# --- 3. text -----------------------------------------------------------------
loc = read('localisation/rip_capital_loss_l_english.yml')
for tag in table:
    key = 'rip_seat_become_' + tag.lower()
    assert re.search(rf'^ {key}_title:\d+ "[^"]+"', loc, re.M) and re.search(rf'^ {key}_desc:\d+ "[^"]+"', loc, re.M), key
    assert f'[{tag}.GetName]' in loc, key + ': the text names the realm through its tag'
assert len(re.findall(r'^ \w+:\d+ ', loc, re.M)) == 2 * len(table), 'only the decisions\' own keys'
cases += 1


# --- 4. the clock ------------------------------------------------------------
def world(tag, owns):
    """A realm `tag` holding the provinces `owns`; every other seat belongs to a neutral."""
    w = Realm()
    realm = w.country(tag, 'orthodox')
    neutral = w.country('NEU', 'orthodox')
    for seat in table.values():
        w.province(seat, neutral)
    for seat in owns:
        w.provinces[str(seat)]['owner'] = realm['id']
    return w, realm


def offered(w, c):
    return sorted(tag for tag in table
                  if w.gate(block(decisions['rip_seat_become_' + tag.lower()], 'potential'), c))


# Halych without Halych, holding Chernihiv and Kyiv.
w, c = world('HLC', [table['CHR'], table['KIE']])
w.run('rip_namesake_seat_upkeep_effect', c)
assert 'rip_namesake_seat_lost' in c['flags'], 'the clock starts the first time the seat is found missing'
for day, expected in ((1, []), (DAYS - 1, []), (DAYS, ['CHR', 'KIE']), (DAYS + 4000, ['CHR', 'KIE'])):
    w.day = day
    assert offered(w, c) == expected, (day, offered(w, c))
assert 'HLC' not in offered(w, c) and 'ZAZ' not in offered(w, c), 'only the seats it holds, never its own name'

# A name already in use is not offered.
w.country('CHR', 'orthodox')
assert offered(w, c) == ['KIE']

# Regaining the seat stops the clock; losing it again starts a new one.
w.provinces[str(table['HLC'])]['owner'] = 'HLC'
w.run('rip_namesake_seat_upkeep_effect', c)
assert 'rip_namesake_seat_lost' not in c['flags'] and offered(w, c) == []
w.day = 20000
w.provinces[str(table['HLC'])]['owner'] = 'NEU'
w.run('rip_namesake_seat_upkeep_effect', c)
w.day = 20000 + DAYS - 1
assert offered(w, c) == [], 'the 25 years are one unbroken stretch'
w.day = 20000 + DAYS
assert offered(w, c) == ['KIE']
cases += 1

# A realm that holds its seat never starts a clock; a country outside the table never does.
for tag in table:
    w, c = world(tag, [table[tag]])
    w.run('rip_namesake_seat_upkeep_effect', c)
    assert 'rip_namesake_seat_lost' not in c['flags'], tag
w, c = world('KRU', [])
w.run('rip_namesake_seat_upkeep_effect', c)
assert 'rip_namesake_seat_lost' not in c['flags'], 'a formed nation is outside the table'
cases += 1

# --- 5. taking a name ---------------------------------------------------------
for tag in ('CHR', 'PLT'):
    w, c = world('HLC', [table[tag]])
    c['flags']['rip_namesake_seat_lost'] = 0
    w.day = DAYS
    assert offered(w, c) == [tag]
    w.execute(block(decisions['rip_seat_become_' + tag.lower()], 'effect'), c)
    assert ('change_tag', tag) in w.done and ('set_capital', str(table[tag])) in w.done
    assert 'rip_namesake_seat_lost' not in c['flags']
    assert c['capital'] == str(table[tag]), 'the new name\'s seat becomes the capital'
    assert ('formed_polotsk_nation_flag' in c['flags']) == (tag == 'PLT')
cases += 1

# --- 6. wiring ----------------------------------------------------------------
hooks = read('common/on_actions/rip_capital_loss_on_actions.txt')
for hook in ('on_startup', 'on_yearly_pulse'):
    assert re.search(hook + r'\s*=\s*\{\s*rip_namesake_seat_upkeep_effect = yes\s*\}', hooks), hook
lost = read('common/scripted_triggers/rip_capital_loss_triggers.txt')
assert f'days = {DAYS}' in lost, '25 years are 9125 days'
for path in ('common/scripted_triggers/rip_capital_loss_triggers.txt', 'common/scripted_effects/rip_capital_loss_effects.txt',
             'decisions/RIP_CapitalLoss.txt'):
    text = read(path)
    assert not re.search(r'\belse(_if)?\s*=', text), path + ': else/else_if is the trap the engine measured; use exclusive ifs'
    assert 'add_opinion' not in text, path
cases += 1

print(f'CAPITAL LOSS PASS: {cases} source-executed cases; {len(table)} realms, one decision per seat held, '
      f'offered only after {DAYS} days without the namesake seat, the AI never takes it; source model, not engine evidence.')
