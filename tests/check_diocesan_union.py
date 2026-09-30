"""Source contracts for the Catholic patron's bounded provincial union path.

Static only: none of this runs the engine. Three groups of contracts:

* the Eparchial Union decision and its events (targeting, cost, cooldowns,
  guards, labelling of the fallback, refusal cost stated in the text);
* the sponsor gate: a Habsburg crown holding Galicia after 1772 must be able to
  become patron, proven with a small model of the trigger over the province
  history files (it failed before rip_church_sponsor_parish existed);
* khmelnytsky_events.7, the uncoupled second Brest path, is now coupled to the
  same patron flags and cannot double-convert a province another path settled.
"""
import json
import re
from clausewitz_testlib import (read, named_block, keyed_blocks, normalized, ROOT,
                                vanilla_read, vanilla_root)

triggers = read('common/scripted_triggers/rip_diocesan_union_triggers.txt')
decisions = read('decisions/RIP_DiocesanUnion.txt')
events = read('events/RIP_DiocesanUnion.txt')

patron = normalized(named_block(triggers, 'rip_du_catholic_patron'))
assert 'religion = catholic' in patron
assert 'has_country_flag = rip_church_supports_union' in patron
assert 'any_owned_province = { religion = greek_catholic }' in patron

# One predicate closes an eparchy to every random path.
seat_open = normalized(named_block(triggers, 'rip_du_seat_open'))
for guard in ('NOT = { has_province_modifier = resistance_to_greek_catholic_spread }',
              'had_province_flag = { flag = rip_du_approached days = 3650 }',
              'NOT = { has_province_flag = rip_du_approached }'):
    assert guard in seat_open, guard
assert 'ROOT' not in seat_open

candidate = normalized(named_block(triggers, 'rip_du_eligible_diocese'))
for guard in ('religion = orthodox', 'is_core = owner', 'controlled_by = owner',
              'NOT = { has_missionary = yes }', 'rip_du_seat_open = yes'):
    assert guard in candidate, guard
assert 'ROOT' not in candidate  # Must work in both country and province ROOT.
can = normalized(named_block(triggers, 'rip_du_can_negotiate'))
assert 'had_country_flag = { flag = rip_du_negotiated days = 1825 }' in can
assert 'any_owned_province = { rip_du_eligible_diocese = yes }' in can
selection = named_block(decisions, 'random_owned_province')
assert normalized(named_block(selection, 'limit')) == 'limit = { rip_du_eligible_diocese = yes }'
assert decisions.index('set_country_flag = rip_du_negotiated') < decisions.index('random_owned_province')
assert 'id = rip_diocesan_union.1' in selection

definitions = {re.search(r'id\s*=\s*(\S+)', b)[1]: b
               for _, b in keyed_blocks(events, 'province_event') if 'title =' in b}
assert set(definitions) == {f'rip_diocesan_union.{i}' for i in (1, 2, 3)}
assert all('is_triggered_only = yes' in b for b in definitions.values())
offer = definitions['rip_diocesan_union.1']
options = [b for _, b in keyed_blocks(offer, 'option')]
assert len(options) == 2
guard = normalized(named_block(options[0], 'trigger')).split('= ', 1)[1]
execution_guard = normalized(named_block(options[0], 'limit')).split('= ', 1)[1]
assert guard == execution_guard
assert 'owned_by = FROM' in guard and 'rip_du_catholic_patron = yes' in guard
assert 'dip_power = 50 years_of_income = 0.25' in guard
assert 'trigger =' not in options[1]  # Always possible to dismiss a stale offer.
assert 'add_dip_power = -50 add_years_of_income = -0.25' in options[0]
assert options[0].index('add_dip_power') < options[0].index('random_list')
accepted = named_block(options[0], '60')
refused = named_block(options[0], '40')
assert 'change_religion = greek_catholic' in accepted
assert 'add_local_autonomy = 10' in accepted and 'duration = 7300' in accepted
assert 'change_religion' not in refused and 'duration = 3650' in refused
assert events.count('change_religion =') == 1
assert 'country_event' not in events and 'save_event_target_as' not in events
assert 'create_center_of_reformation' not in events
for outcome in (2, 3):
    assert f'id = rip_diocesan_union.{outcome}' in options[0]
    assert 'change_religion' not in definitions[f'rip_diocesan_union.{outcome}']
# A province the union already took would answer the next offer from the flag.
assert 'set_province_flag = rip_du_approached' in options[0]
assert options[0].index('set_province_flag = rip_du_approached') < options[0].index('random_list')

loc_path = ROOT / 'localisation/rip_diocesan_union_l_english.yml'
assert loc_path.read_bytes().startswith(b'\xef\xbb\xbf')
loc = loc_path.read_text(encoding='utf-8-sig')
for key in re.findall(r'(?:title|desc|name)\s*=\s*(rip_diocesan_union\.\d+\.[a-z])', events):
    assert f' {key}:0 ' in loc, key
assert 'local_missionary_strength = -1' in read('common/event_modifiers/rip_diocesan_union_modifiers.txt')


def entries(text):
    """key -> raw value of every localisation line."""
    return dict(re.findall(r'(?m)^ ([\w.\-]+):\d*\s*"(.*)"\s*$', text))


texts = entries(loc)

# The random union is the labelled fallback, alternative history, and it says so
# in the decision and in the offer; both state what a refusal costs and that the
# ten-year lock belongs to one eparchy, not to the crown.
desc = texts['rip_du_negotiate_desc']
offer_text = texts['rip_diocesan_union.1.d']
assert desc.startswith('Alternative history.'), desc[:40]
assert offer_text.startswith('Alternative history.'), offer_text[:40]
for text in (desc, offer_text, texts['rip_diocesan_union.3.d']):
    assert '+3 unrest' in text and '+15% autonomy' in text and 'ten years' in text, text[:60]
assert 'cannot be approached again' in desc and 'others can' in desc
assert 'cannot be approached again' in offer_text and 'Other eparchies are not affected' in offer_text
assert 'the other eparchies stay open' in texts['rip_diocesan_union.3.d']
assert 'dated event' in desc  # the dated seat events take precedence historically
# The numbers in the text are the numbers of the modifier and the timers.
resistance = named_block(read('common/event_modifiers/uniate_church_modifiers.txt'),
                         'resistance_to_greek_catholic_spread')
assert re.search(r'local_unrest\s*=\s*3\b', resistance)
assert re.search(r'local_autonomy\s*=\s*0\.15\b', resistance)
assert 'name = resistance_to_greek_catholic_spread duration = 3650' in normalized(refused)
assert 'add_local_autonomy = 10' in accepted
# One name for one object: an Eastern see is an eparchy, never a diocese.
for key, value in texts.items():
    if key.startswith(('rip_du_', 'rip_diocesan_union.', 'desc_rip_du_')):
        assert not re.search(r'(?i)dioces', value), (key, value[:60])
assert texts['rip_du_negotiate_title'] == 'Negotiate an Eparchial Union'
assert texts['rip_du_rite_guarantee'] == 'Eastern Rite Protected'

# --------------------------------------------------------------------------
# THE SPONSOR GATE
# --------------------------------------------------------------------------
sponsor_triggers = read('common/scripted_triggers/rip_church_sponsor_triggers.txt')
union_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
sponsor_effects = read('common/scripted_effects/rip_church_sponsor_effects.txt')
church_decisions = read('decisions/RIP_ChurchRedesign.txt')

can_sponsor = normalized(named_block(sponsor_triggers, 'rip_church_can_sponsor_union'))
assert 'any_owned_province = { rip_church_sponsor_parish = yes }' in can_sponsor
assert 'rip_church_florence_parish' not in can_sponsor
sponsor_effect = normalized(named_block(sponsor_effects, 'rip_church_sponsor_union_effect'))
assert 'random_owned_province = { limit = { rip_church_sponsor_parish = yes } change_religion = greek_catholic }' in sponsor_effect
assert 'rip_church_florence_parish' not in sponsor_effect
# The decision hides itself unless the country holds a parish it could convert,
# as the Florentine decision does; the AI weight is unchanged.
sponsor_decision = named_block(church_decisions, 'rip_church_sponsor_union')
assert 'any_owned_province = { rip_church_sponsor_parish = yes }' in normalized(named_block(sponsor_decision, 'potential'))
assert 'ai_will_do = { factor = 1 modifier = { factor = 0 num_of_loans = 1 } }' in normalized(sponsor_decision)
assert 'rip_church_can_sponsor_union = yes' in normalized(named_block(sponsor_decision, 'allow'))
# The Florentine path keeps its own, narrower test, untouched.
florence_parish = normalized(named_block(union_triggers, 'rip_church_florence_parish'))
assert florence_parish == ('rip_church_florence_parish = { is_city = yes religion = orthodox '
                           'is_core = ROOT controlled_by = ROOT '
                           'OR = { region = ruthenia_region culture_group = byzantine } }'), florence_parish
florence_decision = normalized(named_block(church_decisions, 'rip_church_florence'))
assert 'rip_church_florence_parish = yes' in florence_decision
assert 'rip_church_sponsor_parish' not in florence_decision
assert 'rip_church_sponsor_parish' not in normalized(named_block(union_triggers, 'rip_church_can_begin_florence'))


# --- a small model of the trigger over the province history files -----------
def tree(text):
    """Tolerant Clausewitz reader: [(key, value)], value a str, a list, or None
    for a bare word (area and region files list bare province ids and names)."""
    tokens = re.findall(r'"[^"\n]*"|[{}=]|[^\s{}=]+', re.sub(r'#[^\n]*', '', text))
    pos = 0

    def block():
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]
            pos += 1
            if pos < len(tokens) and tokens[pos] == '=':
                pos += 1
                if tokens[pos] == '{':
                    pos += 1
                    value = block()
                    pos += 1
                else:
                    value = tokens[pos].strip('"')
                    pos += 1
                result.append((key, value))
            else:
                result.append((key.strip('"'), None))
        return result
    return block()


_HISTORY_INDEX = {}


def history_file(kind, number):
    """The mod's own history file wins, as in the engine; vanilla is the fallback."""
    if kind not in _HISTORY_INDEX:
        index = {}
        root = vanilla_root()
        for base in ([root] if root else []) + [ROOT]:  # the mod is read last, so it wins
            folder = base / 'history' / kind
            if folder.is_dir():
                for path in folder.glob('*.txt'):
                    index[path.name.split(' - ')[0].strip()] = path
        _HISTORY_INDEX[kind] = index
    path = _HISTORY_INDEX[kind].get(str(number))
    return path.read_text(encoding='cp1252', errors='replace') if path else None


_PROVINCES = {}


def province_at(number, date):
    """Owner, controller, cores, religion, culture and is_city on `date` (y, m, d)."""
    if (number, date) not in _PROVINCES:
        _PROVINCES[(number, date)] = _province_at(number, date)
    return dict(_PROVINCES[(number, date)], cores=set(_PROVINCES[(number, date)]['cores']))


def _province_at(number, date):
    text = history_file('provinces', number)
    assert text is not None, f'no history file for province {number}'
    state = dict(id=int(number), owner=None, controller=None, cores=set(),
                 religion=None, culture=None, is_city=False)
    dated = []

    def apply(items):
        for key, value in items:
            if key == 'owner': state['owner'] = value
            elif key == 'controller': state['controller'] = value
            elif key == 'religion': state['religion'] = value
            elif key == 'culture': state['culture'] = value
            elif key == 'is_city': state['is_city'] = value == 'yes'
            elif key == 'add_core': state['cores'].add(value)
            elif key == 'remove_core': state['cores'].discard(value)
    top = []
    for key, value in tree(text):
        if re.fullmatch(r'\d+\.\d+\.\d+', key) and isinstance(value, list):
            dated.append((tuple(int(x) for x in key.split('.')), value))
        elif not isinstance(value, list):
            top.append((key, value))
    apply(top)
    for when, items in sorted(dated, key=lambda pair: pair[0]):
        if when <= date:
            apply([(k, v) for k, v in items if not isinstance(v, list)])
    return state


def geography():
    """area -> province ids and area -> region from vanilla, else the two facts
    this check needs (verified against the 1.37.5 install)."""
    areas, regions = {}, {}
    area_text = vanilla_read('map/area.txt')
    region_text = vanilla_read('map/region.txt')
    if area_text and region_text:
        for name, body in tree(area_text):
            if isinstance(body, list):
                ids = [int(k) for k, v in body if v is None and k.isdigit()]
                if ids:
                    areas[name] = ids
        for name, body in tree(region_text):
            if isinstance(body, list):
                for key, value in body:
                    if key == 'areas' and isinstance(value, list):
                        for area, _ in value:
                            regions[area] = name
        return areas, regions, True
    return ({'red_ruthenia_area': [261, 1940, 2424, 2961, 4541],
             'transylvania_area': [1952]},
            {'red_ruthenia_area': 'poland_region', 'transylvania_area': 'carpathia_region'}, False)


AREAS, REGIONS, FROM_VANILLA = geography()
assert not (ROOT / 'map').exists(), 'the mod ships map/: the vanilla area table no longer applies'
assert sorted(AREAS['red_ruthenia_area']) == [261, 1940, 2424, 2961, 4541], AREAS['red_ruthenia_area']
assert REGIONS['red_ruthenia_area'] == 'poland_region'  # not ruthenia_region: the D1 cause
AREA_OF = {p: a for a, ids in AREAS.items() for p in ids}


def culture_groups():
    groups = {}
    for group, body in tree((ROOT / 'common/cultures/00_cultures.txt').read_text(encoding='cp1252')):
        if isinstance(body, list):
            for culture, sub in body:
                if isinstance(sub, list):
                    groups.setdefault(culture, group)
    return groups


GROUP_OF = culture_groups()
REGISTRY = {}
for source in (union_triggers, sponsor_triggers):
    for name, body in tree(source):
        if isinstance(body, list):
            REGISTRY[name] = body


def holds(items, province, root_tag):
    """Evaluate a trigger body on one province. Unknown atoms fail loudly."""
    for key, value in items:
        if key == 'OR':
            ok = any(holds([item], province, root_tag) for item in value)
        elif key == 'AND':
            ok = holds(value, province, root_tag)
        elif key == 'NOT':
            ok = not holds(value, province, root_tag)
        elif key in REGISTRY:
            ok = holds(REGISTRY[key], province, root_tag) == (value == 'yes')
        elif key == 'is_city':
            ok = province['is_city'] == (value == 'yes')
        elif key == 'religion':
            ok = province['religion'] == value
        elif key == 'is_core':
            assert value == 'ROOT', value
            ok = root_tag in province['cores']
        elif key == 'controlled_by':
            assert value == 'ROOT', value
            ok = province['controller'] == root_tag
        elif key == 'culture_group':
            ok = GROUP_OF.get(province['culture']) == value
        elif key == 'area':
            ok = AREA_OF.get(province['id']) == value
        elif key == 'region':
            ok = REGIONS.get(AREA_OF.get(province['id'])) == value
        elif key == 'province_id':
            ok = province['id'] == int(value)
        else:
            raise AssertionError('unmodelled trigger atom: ' + key)
        if not ok:
            return False
    return True


def parishes(trigger, tag, date, candidates):
    return sorted(p for p in candidates
                  if holds(REGISTRY[trigger], province_at(p, date), tag))


SEAT_LAND = sorted(set(AREAS['red_ruthenia_area']) | {1952})

# Habsburg Galicia: from 1772.8.5 the crown holds Lviv, Peremyshl, Halych and
# Drohobych as cores. The Florentine test cannot see them (poland_region, and a
# Ruthenian culture is not of the byzantine group); the sponsor test can.
galicia = parishes('rip_church_sponsor_parish', 'HAB', (1775, 1, 1), SEAT_LAND)
florentine = parishes('rip_church_florence_parish', 'HAB', (1775, 1, 1), SEAT_LAND)
assert florentine == [], f'D1 regression model broken: the Florentine test now sees {florentine}'
assert {261, 2424, 2961, 4541} <= set(galicia), galicia
assert 1940 not in galicia  # Belz is Catholic by province history since 1570
# Before the partition nothing qualifies: the crown holds no such core.
assert parishes('rip_church_sponsor_parish', 'HAB', (1771, 1, 1), SEAT_LAND) == []
# Maramaros is reachable by province id alone, for a crown that owns it.
maramaros = dict(province_at(1952, (1700, 1, 1)), cores={'HAB'}, controller='HAB')
assert holds(REGISTRY['rip_church_sponsor_parish'], maramaros, 'HAB')
assert not holds(REGISTRY['rip_church_florence_parish'], maramaros, 'HAB')
# A crown must hold the core and the control: a foreign province does not qualify.
assert not holds(REGISTRY['rip_church_sponsor_parish'], province_at(2424, (1775, 1, 1)), 'PLC')
# Nothing Florence and the old sponsor path could reach was lost.
if FROM_VANILLA:
    ruthenia_areas = {a for a, r in REGIONS.items() if r == 'ruthenia_region'}
    ruthenian = sorted(p for a in ruthenia_areas for p in AREAS.get(a, []))
    for tag, date in (('PLC', (1600, 1, 1)), ('LIT', (1500, 1, 1))):
        before = parishes('rip_church_florence_parish', tag, date, ruthenian)
        after = parishes('rip_church_sponsor_parish', tag, date, ruthenian)
        assert set(before) <= set(after), (tag, before, after)
    plc = parishes('rip_church_sponsor_parish', 'PLC', (1600, 1, 1), ruthenian)
    assert plc, 'the Commonwealth must still hold sponsor parishes in 1600'
# HAB is Catholic in history, so religion = catholic in the gate is not what blocks it.
hab = history_file('countries', 'HAB')
if hab is not None:
    assert re.search(r'(?m)^religion\s*=\s*catholic', hab)

# --------------------------------------------------------------------------
# khmelnytsky_events.7: the Catholic crown's second Brest path
# --------------------------------------------------------------------------
khmelnytsky_text = read('events/KhmelnytskyUprisings.txt')
k7 = next(block for _, block in keyed_blocks(khmelnytsky_text, 'country_event')
          if 'id = khmelnytsky_events.7' in block)
k7_trigger = normalized(named_block(k7, 'trigger'))
for guard in ('religion = catholic', 'has_country_flag = rip_church_supports_union',
              'NOT = { has_country_flag = rip_church_opposes_union }',
              'any_owned_province = { rip_du_crown_union_province = yes }',
              'is_year = 1596', 'NOT = { is_year = 1626 }',
              'NOT = { has_country_flag = union_of_brest_happened }'):
    assert guard in k7_trigger, guard
assert 'is_triggered_only' not in k7 and 'mean_time_to_happen' in k7
k7_options = [b for _, b in keyed_blocks(k7, 'option')]
assert len(k7_options) == 2
k7_a, k7_b = k7_options
assert 'any_owned_province = { rip_du_crown_union_province = yes }' in normalized(named_block(k7_a, 'trigger'))
k7_pick = named_block(k7_a, 'random_owned_province')
assert normalized(named_block(k7_pick, 'limit')) == 'limit = { rip_du_crown_union_province = yes }'
assert 'change_religion = greek_catholic' in k7_pick and 'add_unrest = 3' in k7_pick
assert re.search(r'add_local_autonomy\s*=\s*5\b', k7_pick), 'autonomy takes points, not fractions'
assert 'change_religion' not in k7_b
crown_province = normalized(named_block(triggers, 'rip_du_crown_union_province'))
for guard in ('religion = orthodox', 'region = ruthenia_region', 'rip_du_seat_open = yes',
              'is_city = yes', 'controlled_by = owner'):
    assert guard in crown_province, guard
assert 'ROOT' not in crown_province
# The dated seat events answer for themselves. Their answered flags close a seat
# here; the same events set rip_du_approached when they convert one.
for flag in ('rip_eparchy_przemysl_union_answered', 'rip_eparchy_lviv_union_answered',
             'rip_eparchy_lutsk_union_answered'):
    assert f'NOT = {{ has_province_flag = {flag} }}' in seat_open, flag
timeline_data = ROOT / 'tools/data/eparchy_timeline.json'
development_flags = set()  # rows that need a Greek Catholic province: never a random target
if timeline_data.exists():
    # The dated timeline is the source of truth for which seats answer for themselves.
    for row in json.loads(timeline_data.read_text(encoding='utf-8'))['rows']:
        flag = f"rip_eparchy_{row['id']}_answered"
        if row['kind'] in ('union_convert', 'union_modifier_only'):
            assert f'NOT = {{ has_province_flag = {flag} }}' in seat_open, (
                'rip_du_seat_open must list the answered flag of dated seat ' + row['id'])
        else:
            development_flags.add(flag)
timeline = ROOT / 'events/RIP_EparchyHistory.txt'
if timeline.exists():
    timeline_text = timeline.read_text(encoding='cp1252')
    answered = set(re.findall(r'set_province_flag\s*=\s*(rip_eparchy_\w+_answered)', timeline_text))
    uncovered = sorted(f for f in answered if f not in seat_open and f not in development_flags)
    assert 'rip_du_approached' in timeline_text or not uncovered, (
        'dated seat events neither set rip_du_approached nor appear in rip_du_seat_open: '
        + ', '.join(uncovered))
    if uncovered:
        print('NOTE: answered flags not listed in rip_du_seat_open (the seat is closed '
              'through rip_du_approached instead): ' + ', '.join(uncovered))
else:
    print('NOTE: events/RIP_EparchyHistory.txt absent; the seat-lock interface is checked from this side only')

# Real text, defined once: no placeholder from zzz_missing may load later and win.
khmelnytsky_loc = (ROOT / 'localisation/khmelnytsky_events_l_english.yml').read_text(encoding='utf-8-sig')
k7_texts = entries(khmelnytsky_loc)
wanted = ['khmelnytsky_events.7.t', 'khmelnytsky_events.7.d', 'khmelnytsky_events.7.a',
          'khmelnytsky_events.7.b', 'union_of_brest_enforced', 'desc_union_of_brest_enforced',
          'union_of_brest_compromise', 'desc_union_of_brest_compromise']
for key in wanted:
    assert key in k7_texts, key
    holders = [p.name for p in (ROOT / 'localisation').rglob('*_l_english.yml')
               if re.search(r'(?m)^ ' + re.escape(key) + r':\d', p.read_text(encoding='utf-8-sig'))]
    assert holders == ['khmelnytsky_events_l_english.yml'], (key, holders)
body = k7_texts['khmelnytsky_events.7.d']
assert body.startswith('Game model.')
assert 'changes rite' in body and '+3 unrest' in body and '+5% autonomy' in body
assert 'patronage' in body and 'Brest' in body and 'twenty years' in body
modifiers = read('common/event_modifiers/PRL_modifiers.txt')
enforced = named_block(modifiers, 'union_of_brest_enforced')
compromise = named_block(modifiers, 'union_of_brest_compromise')
assert re.search(r'global_unrest\s*=\s*1\b', enforced) and re.search(r'tolerance_heretic\s*=\s*-1\b', enforced)
assert re.search(r'global_unrest\s*=\s*-1\b', compromise) and re.search(r'tolerance_heretic\s*=\s*1\b', compromise)
assert '+1 unrest and -1 tolerance of heretics' in body
assert 'prestige falls by 5' in body and 'add_prestige = -5' in k7_b
assert 'duration = 7300' in k7_a and 'duration = 7300' in k7_b  # twenty years, as the text says
for text in (body, *(k7_texts[k] for k in wanted)):
    assert '!' not in text

print('PASS: Catholic patron, symmetric targeting, cooldowns, stale-owner/resource guards, paid '
      'acceptance/refusal, labelled fallback and its stated refusal cost, sponsor reach '
      f'(HAB Galicia 1775: {galicia}), coupled Brest path and localisation')
