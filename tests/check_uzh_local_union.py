"""Local Uzhhorod union: dated April 1646 timing, patronage, one-shot outcome,
the reachable UZH sequel, and the texts that describe them.

Every contract raises AssertionError with a short code. After the real files
pass, the same contracts are run over planted violations, one per contract
family, and each must fail with exactly the code it was planted for - so a
contract that quietly stops firing is itself caught.
"""
import re
from clausewitz_testlib import ROOT, named_block, keyed_blocks, normalized

SOURCES = {
    'triggers': 'common/scripted_triggers/rip_uzh_union_triggers.txt',
    'effects': 'common/scripted_effects/rip_uzh_union_effects.txt',
    'events': 'events/RIP_UzhLocalUnion.txt',
    'uzh': 'events/Uzh.txt',
    'missions': 'missions/Zakarpatta_Missions.txt',
    'loc': 'localisation/rip_uzh_local_union_l_english.yml',
    'country': 'history/countries/UZH - Huszt.txt',
    'province': 'history/provinces/1952 - Maramaros.txt',
    'doc': 'docs/UZHHOROD_LOCAL_UNION.uk.md',
}


def read(path):
    """Script is Windows-1252; the docs and localisation are UTF-8."""
    raw = (ROOT / path).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252', errors='replace')
    return text.replace(chr(13) + chr(10), chr(10))


def req(condition, code):
    if not condition:
        raise AssertionError(code)


# --- a small Clausewitz reader, enough for triggers and effect bodies --------

TOKEN = re.compile(r'[{}=]|[^\s{}=]+')


def parse(text):
    """Block body -> list of (key, value); value is a str, a list, or None."""
    tokens = TOKEN.findall(re.sub(r'#[^\n]*', '', text).replace('"', ' '))
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(tokens):
            key = tokens[pos]
            pos += 1
            if key == '}':
                return items
            if pos < len(tokens) and tokens[pos] == '=':
                pos += 1
                if tokens[pos] == '{':
                    pos += 1
                    items.append((key, block()))
                else:
                    items.append((key, tokens[pos]))
                    pos += 1
            else:
                items.append((key, None))
        return items

    return block()


def body(text, name):
    return parse(named_block(text, name))[0][1]


def get(items, key):
    return [v for k, v in items if k == key]


def walk(items):
    for key, value in items:
        yield key, value
        if isinstance(value, list):
            yield from walk(value)


def window_true(items, year, month):
    """is_year / is_month as measured in EU4 1.37.5: both mean 'from then on'."""
    for key, value in items:
        if key == 'is_year':
            ok = year >= int(value)
        elif key == 'is_month':
            ok = month >= int(value)
        elif key == 'NOT':
            ok = not any(window_true([kv], year, month) for kv in value)
        elif key == 'OR':
            ok = any(window_true([kv], year, month) for kv in value)
        elif key == 'AND':
            ok = window_true(value, year, month)
        else:
            raise AssertionError('window-atom')
        if not ok:
            return False
    return True


def state_true(items, flags, modifiers):
    """Country flags and modifiers are read from the state; every other atom is
    assumed true, so this answers only 'can these flags alone close the gate'."""
    for key, value in items:
        if key == 'has_country_flag':
            ok = value in flags
        elif key == 'has_country_modifier':
            ok = value in modifiers
        elif key == 'NOT':
            ok = not any(state_true([kv], flags, modifiers) for kv in value)
        elif key == 'OR':
            ok = any(state_true([kv], flags, modifiers) for kv in value)
        elif key == 'AND':
            ok = state_true(value, flags, modifiers)
        else:
            ok = True
        if not ok:
            return False
    return True


def weight(option, religion):
    """AI weight of an option for an owner of the given religion."""
    ai = get(option, 'ai_chance')
    req(ai, 'ai-missing')
    total = float(get(ai[0], 'factor')[0])
    for modifier in get(ai[0], 'modifier'):
        applies = True
        for key, value in modifier:
            if key == 'factor':
                continue
            if key == 'owner':
                value = get(value, 'religion')[0]
            elif key != 'religion':
                raise AssertionError('ai-atom')
            applies = applies and value == religion
        if applies:
            total *= float(get(modifier, 'factor')[0])
    return total


def accept_share(options, religion):
    a, b = weight(options[0], religion), weight(options[1], religion)
    return a / (a + b)


def events_by_id(text):
    out = {}
    for _, block in keyed_blocks(text, 'province_event'):
        out[re.search(r'\bid\s*=\s*(\S+)', block)[1]] = block
    return out


# --- the contracts -----------------------------------------------------------

def contract_possible(t):
    n = normalized(t)
    for guard in ('province_id = 1952', 'is_year = 1646', 'controlled_by = owner',
                  'NOT = { has_missionary = yes }', 'religion = orthodox',
                  'overlord = { religion = catholic }',
                  'any_known_country = { religion = catholic alliance_with = PREV }'):
        req(guard in n, 'possible-guard')
    possible = normalized(named_block(t, 'rip_uzh_local_union_possible'))
    req('tag = UZH' not in possible and 'is_core' not in possible, 'possible-tag')


def contract_windows(t):
    date = body(t, 'rip_uzh_union_date_window')
    late = body(t, 'rip_uzh_union_late_window')
    text = normalized(named_block(t, 'rip_uzh_union_date_window'))
    req('is_year = 1646 NOT = { is_year = 1647 }' in text, 'window-year')
    req('is_month = 3 NOT = { is_month = 4 }' in text, 'window-month')
    for year in range(1444, 1801):
        for month in range(12):
            req(not (window_true(date, year, month) and window_true(late, year, month)),
                'window-overlap')
            inside = (year, month) == (1646, 3)
            req(window_true(date, year, month) == inside, 'window-month')
            after = (year, month) > (1646, 3)
            req(window_true(late, year, month) == after, 'window-late')
    fresh = normalized(named_block(t, 'rip_uzh_union_scheduled_fresh'))
    req('has_province_flag = rip_uzh_union_scheduled' in fresh, 'fresh-flag')
    req('NOT = { had_province_flag = { flag = rip_uzh_union_scheduled days = 45 } }' in fresh,
        'fresh-flag')


def contract_accept_effect(effects):
    used = {k for k, _ in walk(parse(effects))}
    req('else' not in used and 'else_if' not in used, 'effect-else')
    req(not {'add_opinion', 'country_event', 'province_event'} & used, 'effect-event')
    n = normalized(effects)
    req('limit = { rip_uzh_local_union_possible = yes }' in n, 'effect-limit')
    for literal in ('set_province_flag = rip_uzh_union_accepted',
                    'enable_religion = greek_catholic',
                    'set_country_flag = rip_church_supports_union',
                    'limit = { NOT = { has_country_flag = rip_church_union_founded } } '
                    'set_country_flag = rip_church_union_founded',
                    'add_local_autonomy = 10',
                    'add_province_modifier = { name = rip_du_rite_guarantee duration = 7300 }'):
        req(literal in n, 'effect-outcome')
    accept = body(effects, 'rip_uzh_union_accept_effect')
    limit_if = get(accept, 'if')[0]
    req(get(limit_if, 'change_religion') == ['greek_catholic'], 'effect-outcome')
    owner = get(limit_if, 'owner')[0]
    req('change_religion' not in {k for k, _ in walk(owner)}, 'effect-owner-religion')
    patron_if = get(owner, 'if')[0]
    keys = [k for k, _ in patron_if]
    req('custom_tooltip' in keys and 'hidden_effect' in keys
        and keys.index('custom_tooltip') < keys.index('hidden_effect'), 'effect-tooltip')
    req(get(patron_if, 'custom_tooltip') == ['rip_uzh_union_patron_tt'], 'effect-tooltip')


def contract_events(events):
    defs = events_by_id(events)
    req(set(defs) == {'rip_uzh_union.1', 'rip_uzh_union.2', 'rip_uzh_union.10'}, 'events-set')
    for eid, block in defs.items():
        n = normalized(block)
        req(not ('is_triggered_only = yes' in n and 'mean_time_to_happen' in n), 'event-f7')
    starter = normalized(defs['rip_uzh_union.10'])
    for literal in ('hidden = yes', 'fire_only_once = yes', 'province_id = 1952',
                    'rip_uzh_union_date_window = yes',
                    'rip_uzh_local_union_possible = yes',
                    'NOT = { has_province_flag = rip_uzh_union_answered }',
                    'NOT = { has_province_flag = rip_uzh_union_scheduled }',
                    'mean_time_to_happen = { days = 1 }',
                    'set_province_flag = rip_uzh_union_scheduled',
                    'province_event = { id = rip_uzh_union.1 days = 20 }'):
        req(literal in starter, 'starter')
    req('title =' not in starter and 'is_triggered_only' not in starter, 'starter')
    popup = normalized(defs['rip_uzh_union.1'])
    req('is_triggered_only = yes' in popup, 'popup-triggered')
    req('mean_time_to_happen' not in popup, 'popup-triggered')
    late = normalized(defs['rip_uzh_union.2'])
    for literal in ('mean_time_to_happen = { months = 6 }', 'province_id = 1952',
                    'rip_uzh_union_late_window = yes',
                    'rip_uzh_local_union_possible = yes',
                    'NOT = { has_province_flag = rip_uzh_union_answered }'):
        req(literal in late, 'late')
    req('NOT = { rip_uzh_union_scheduled_fresh = yes }' in late, 'late-fresh')
    req('is_triggered_only' not in late, 'late')
    # the scheduled flag is set once only: setting it again refreshes its date
    req(events.count('set_province_flag = rip_uzh_union_scheduled') == 1, 'scheduled-once')
    for eid in ('rip_uzh_union.1', 'rip_uzh_union.2'):
        n = normalized(defs[eid])
        req('immediate = { set_province_flag = rip_uzh_union_answered }' in n, 'answered')
        req('NOT = { has_province_flag = rip_uzh_union_answered }' in n, 'answered')
        options = [b for _, b in keyed_blocks(defs[eid], 'option')]
        req(len(options) == 2, 'options')
        first, second = normalized(options[0]), normalized(options[1])
        req('trigger = { rip_uzh_local_union_possible = yes }' in first, 'options')
        req('rip_uzh_union_accept_effect = yes' in first, 'options')
        req('trigger =' not in second and 'rip_uzh_union_accept_effect' not in second
            and 'change_religion' not in second, 'options')
        parsed = [parse(o)[0][1] for o in options]
        c = accept_share(parsed, 'catholic')
        g = accept_share(parsed, 'greek_catholic')
        o = accept_share(parsed, 'orthodox')
        req(0.6 <= c <= 0.95 and 0.6 <= g <= 0.95 and 0.2 <= o <= 0.6, 'ai-shares')
        req(c < g and o < c, 'ai-order')
    req(events.count('change_religion') == 0, 'events-religion')
    for banned in ('add_opinion', 'add_government_reform', 'add_country_modifier',
                   'else_if', 'else ='):
        req(banned not in events, 'events-banned')
    req(events.lstrip().startswith('#') and '# Authenticity: B' in events, 'header')


def contract_sequel(uzh):
    sequel = next(b for _, b in keyed_blocks(uzh, 'country_event')
                  if re.search(r'id\s*=\s*uzh\.51\b', b))
    gate = normalized(named_block(sequel, 'trigger'))
    for guard in ('tag = UZH', 'is_subject = no', 'owns = 1952',
                  'controlled_by = ROOT', 'has_province_flag = rip_uzh_union_accepted',
                  'NOT = { has_country_flag = uzh_union_synod_established }'):
        req(guard in gate, 'sequel-guard')
    req('fire_only_once = yes' in normalized(sequel), 'sequel-once')
    # the mission sets these two for any Orthodox UZH with no year gate
    req('uzh_union_old_rite_confirmed' not in gate
        and 'uz_old_rite_resilience' not in gate, 'sequel-blocked')
    trigger = parse(named_block(sequel, 'trigger'))[0][1]
    req(state_true(trigger, {'uzh_union_old_rite_confirmed'}, {'uz_old_rite_resilience'}),
        'sequel-blocked')
    req(not state_true(trigger, {'uzh_union_synod_established'}, set()), 'sequel-guard')
    req(not state_true(trigger, set(), {'uz_greek_catholic_concord'}), 'sequel-guard')
    n = normalized(sequel)
    req(not ('is_triggered_only' in n and 'mean_time_to_happen' in n), 'event-f7')
    months = int(re.search(r'mean_time_to_happen = \{ months = (\d+) \}', n)[1])
    req(months <= 36, 'sequel-timing')
    req('add_government_reform = uzh_union_synod_reform' in n, 'sequel-reform')
    options = [b for _, b in keyed_blocks(sequel, 'option')]
    req(len(options) == 2, 'sequel-options')
    parsed = [parse(o)[0][1] for o in options]
    o = accept_share(parsed, 'orthodox')
    c = accept_share(parsed, 'catholic')
    req(o < 0.5 < c, 'sequel-ai')
    first, second = normalized(options[0]), normalized(options[1])
    req(first.index('remove_country_modifier = uz_old_rite_resilience')
        < first.index('add_country_modifier'), 'sequel-modifiers')
    req('custom_tooltip = rip_uzh_synod_closed_tt' in second, 'sequel-tooltip')
    req('set_country_flag = uzh_union_old_rite_confirmed' in second, 'sequel-flags')


def contract_mission(missions):
    mission = parse(named_block(missions, 'uz_union_dilemma'))[0][1]
    effect = get(mission, 'effect')[0]
    keys = [k for k, _ in effect]
    req(keys == ['if', 'add_prestige', 'hidden_effect'], 'mission-shape')
    guard = effect[0][1]
    req(get(guard, 'limit')[0] == [('NOT', [('has_country_flag',
                                            'uzh_union_synod_established')])], 'mission-guard')
    inside = [k for k, _ in walk(guard)]
    total = [k for k, _ in walk(effect)]
    req(total.count('add_country_modifier') == 2 == inside.count('add_country_modifier'),
        'mission-guard')
    req(inside.count('set_country_flag') == 2 and 'add_government_reform' in inside,
        'mission-guard')
    req(get(get(effect, 'hidden_effect')[0], 'set_country_flag') == ['uzh_union_debated'],
        'mission-debated')


def contract_texts(loc, doc, province, country):
    def text(key):
        m = re.search(rf'^ {re.escape(key)}:0 "(.*)"$', loc, re.M)
        req(m, 'loc-missing')
        return m[1]
    for eid in (1, 2):
        for suffix in ('t', 'd', 'a', 'b'):
            text(f'rip_uzh_union.{eid}.{suffix}')
    popup, late = text('rip_uzh_union.1.d'), text('rip_uzh_union.2.d')
    req('63 priests' in popup and '24 April 1646' in popup, 'loc-history')
    req('Jakusics' in popup, 'loc-jakusics')
    for d in (popup, late):
        req('no province for Uzhhorod' in d and '[Root.GetName]' in d, 'loc-standin')
        req('!' not in d.replace('§!', ''), 'loc-shout')
    # the popup states the record's date, never its own
    req('24 April' not in late and not re.search(r'\b[Tt]oday\b', popup + late), 'loc-day')
    req(re.search(r'Historically, 63 priests .* on 24 April 1646\.', popup), 'loc-day')
    req('lternative history' in text('rip_uzh_union.2.t')
        and 'lternative history' in late and 'came late' in late, 'loc-marked')
    req('lternative history' not in text('rip_uzh_union.1.t'), 'loc-marked')
    for eid in (1, 2):
        req(text(f'rip_uzh_union.{eid}.a') == 'Guarantee their rite.', 'loc-options')
        req(text(f'rip_uzh_union.{eid}.b') == 'Leave the parishes as they are.', 'loc-options')
    req('patron of local unions' in text('rip_uzh_union_patron_tt'), 'loc-tooltip')
    req('eparchy needs one' in text('rip_uzh_synod_closed_tt'), 'loc-tooltip')
    req('Concord of Huszt' not in province and 'rip_uzh_union.1' in province, 'history-comment')
    req(not re.search(r'religion\s*=\s*catholic', province), 'history-comment')
    req('capital = 1952' in country, 'capital')
    for literal in ('rip_uzh_union.10', 'rip_uzh_union.2', 'rip_uzh_union_date_window',
                    'rip_uzh_union_late_window', 'rip_uzh_union_scheduled', 'uzh.51'):
        req(literal in doc, 'doc-ids')
    req('MTTH 12 місяців' not in doc, 'doc-stale')


def contracts(src):
    contract_possible(src['triggers'])
    contract_windows(src['triggers'])
    contract_accept_effect(src['effects'])
    contract_events(src['events'])
    contract_sequel(src['uzh'])
    contract_mission(src['missions'])
    contract_texts(src['loc'], src['doc'], src['province'], src['country'])


# (description, source, old text, new text, code the contract must fail with)
PLANTED = [
    ('year window without its closing bound', 'triggers',
     'is_year = 1646 NOT = { is_year = 1647 }', 'is_year = 1646', 'window-year'),
    ('month window without its closing bound', 'triggers',
     'is_month = 3 NOT = { is_month = 4 }', 'is_month = 3', 'window-month'),
    ('late window that overlaps April', 'triggers',
     '  is_year = 1647\n  is_month = 4\n', '  is_year = 1647\n  is_month = 3\n',
     'window-overlap'),
    ('late window that starts a year late', 'triggers',
     '  is_year = 1647\n  is_month = 4\n', '  is_year = 1648\n  is_month = 4\n',
     'window-late'),
    ('popup mixes is_triggered_only with MTTH', 'events',
     ' id = rip_uzh_union.1\n', ' id = rip_uzh_union.1\n mean_time_to_happen = { months = 12 }\n',
     'event-f7'),
    ('popup loses is_triggered_only', 'events',
     ' picture = RELIGION_eventPicture\n is_triggered_only = yes\n',
     ' picture = RELIGION_eventPicture\n', 'popup-triggered'),
    ('starter waits longer than a day', 'events',
     'mean_time_to_happen = { days = 1 }', 'mean_time_to_happen = { days = 30 }', 'starter'),
    ('starter stops scheduling the popup', 'events',
     '  province_event = { id = rip_uzh_union.1 days = 20 }\n', '', 'starter'),
    ('late fallback ignores a fresh schedule', 'events',
     '  NOT = { rip_uzh_union_scheduled_fresh = yes }\n', '', 'late-fresh'),
    ('late fallback sets the scheduled flag again', 'events',
     ' province_id = 1952\n  rip_uzh_union_late_window = yes\n',
     ' province_id = 1952\n  rip_uzh_union_late_window = yes\n'
     '  set_province_flag = rip_uzh_union_scheduled\n', 'scheduled-once'),
    ('flat AI weights for an Orthodox owner', 'events',
     'modifier = { factor = 0.25 owner = { religion = orthodox } }',
     'modifier = { factor = 1 owner = { religion = orthodox } }', 'ai-shares'),
    ('option conversion moves back into the event', 'events',
     '  rip_uzh_union_accept_effect = yes\n', '  change_religion = greek_catholic\n',
     'options'),
    ('accept effect gains an else_if', 'effects',
     '  add_local_autonomy = 10\n',
     '  add_local_autonomy = 10\n'
     '  else_if = { limit = { always = yes } add_local_autonomy = 1 }\n', 'effect-else'),
    ('accept effect calls an opinion', 'effects',
     '  add_local_autonomy = 10\n',
     '  add_local_autonomy = 10\n  owner = { add_opinion = { who = ROOT modifier = x } }\n',
     'effect-event'),
    ('patron flags lose their tooltip line', 'effects',
     '    custom_tooltip = rip_uzh_union_patron_tt\n', '', 'effect-tooltip'),
    ('sequel regains the old-rite flag gate', 'uzh',
     '        NOT = { has_country_modifier = uz_greek_catholic_concord }\n    }\n',
     '        NOT = { has_country_modifier = uz_greek_catholic_concord }\n'
     '        NOT = { has_country_flag = uzh_union_old_rite_confirmed }\n    }\n',
     'sequel-blocked'),
    ('sequel regains the old-rite modifier gate', 'uzh',
     '        NOT = { has_country_modifier = uz_greek_catholic_concord }\n    }\n',
     '        NOT = { has_country_modifier = uz_greek_catholic_concord }\n'
     '        NOT = { has_country_modifier = uz_old_rite_resilience }\n    }\n',
     'sequel-blocked'),
    ('sequel waits ten years again', 'uzh', 'months = 24', 'months = 120', 'sequel-timing'),
    ('sequel option b loses its tooltip', 'uzh',
     '        custom_tooltip = rip_uzh_synod_closed_tt\n', '', 'sequel-tooltip'),
    ('mission gives its outcome twice', 'missions',
     'limit = { NOT = { has_country_flag = uzh_union_synod_established } }\n'
     '                if = {\n                    limit = { rip_faith_is_eastern_orthodox = yes }',
     'limit = { always = yes }\n'
     '                if = {\n                    limit = { rip_faith_is_eastern_orthodox = yes }',
     'mission-guard'),
    ('popup loses the record date', 'loc', '24 April 1646', '24 April', 'loc-history'),
    ('popup forgets the bishop', 'loc', 'Bishop Jakusics of Eger', 'the Bishop of Eger',
     'loc-jakusics'),
    ('popup forgets the stand-in', 'loc', 'no province for Uzhhorod', 'no province',
     'loc-standin'),
    ('late text loses its label', 'loc', '§YAlternative history.§! ', '', 'loc-marked'),
    ('concord comment returns', 'province',
     'Vanilla converts the province here', 'Concord of Huszt affirms Orthodox rites',
     'history-comment'),
    ('doc loses the starter', 'doc', 'rip_uzh_union.10', 'rip_uzh_union.X', 'doc-ids'),
]


def main():
    sources = {key: read(path) for key, path in SOURCES.items()}
    contracts(sources)
    for name, key, old, new, code in PLANTED:
        assert old in sources[key], f'planted {name!r}: pattern not found in {SOURCES[key]}'
        mutated = dict(sources)
        mutated[key] = sources[key].replace(old, new)
        try:
            contracts(mutated)
        except AssertionError as failure:
            assert str(failure) == code, (
                f'planted {name!r} failed as {failure!s}, expected {code}')
        else:
            raise SystemExit(f'SELF-TEST FAILED: planted violation {name!r} was not caught')
    print('PASS: April 1646 dated window (month-exact, disjoint late window), one-shot '
          'scheduling, no triggered-only plus MTTH, reachable UZH sequel, mission guard, '
          f'AI weights by religion, texts and doc ({len(PLANTED)} planted violations caught)')


main()
