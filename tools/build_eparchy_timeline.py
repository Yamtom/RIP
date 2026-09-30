"""Generate the dated eparchy timeline under Catholic states from one table.

Source of truth: tools/data/eparchy_timeline.json (one row per dated development).
Generated files (never edit by hand; each carries a header saying so):

    common/scripted_triggers/rip_eparchy_triggers.txt   date windows, readiness gates
    events/RIP_EparchyHistory.txt                        two hidden starters + one visible event per row
    localisation/rip_eparchy_l_english.yml               event texts (fr/de/es inherit from English)

Usage:
    python tools/build_eparchy_timeline.py            rewrite the three files
    python tools/build_eparchy_timeline.py --check    exit 1 when one of them is stale
    python tools/build_eparchy_timeline.py --harness DIR
        write a copy of the trigger file with every date window forced to
        `always = yes` (late windows to `always = no`) for an in-game probe;
        nothing the game loads is touched.

Engine facts the shape rests on (EU4 1.37.5, measured 2026-09-29):
  F2  is_month = N is true when the month is >= N (January = 0) and is_year = Y
      when the year is >= Y, so an EXACT month is `is_month = N NOT = { is_month = N+1 }`
      and an exact year `is_year = Y NOT = { is_year = Y+1 }`.
  F3  a hidden province_event starter with province_id, is_year / is_month and
      mean_time_to_happen = { days = 1 } fires by itself within about 1-7 days of the
      window opening; a delayed province_event lands within a day of its delay.
      Month-level precision is all this promises.
  F4  re-setting a flag refreshes its date, so had_province_flag = { days = N }
      reads "last set at least N days ago".
  F1  add_opinion and event calls are dropped inside else_if / else of a SCRIPTED
      effect. This file writes no scripted effect and no else_if at all.
  F7  is_triggered_only and mean_time_to_happen never share an event.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'tools/data/eparchy_timeline.json'
TRIGGERS = 'common/scripted_triggers/rip_eparchy_triggers.txt'
EVENTS = 'events/RIP_EparchyHistory.txt'
LOC = 'localisation/rip_eparchy_l_english.yml'
GENERATOR = 'tools/build_eparchy_timeline.py'
KINDS = ('union_convert', 'union_modifier_only', 'development')
ROLES = ('protection', 'diocese', 'metropolitan', 'resistance')
IDENT = re.compile(r'^[a-z][a-z0-9_]*$')
LATE_TAIL = 'Here that date has passed without a settlement, and the question is still open.'

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


def load(path: Path = DATA) -> dict:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def row_key(row) -> tuple:
    """Sort key of a row's own date: (year, month); a year-only row counts from January."""
    return (row['year'], row['month'] if row['month'] is not None else 0)


def validate(data: dict) -> list[str]:
    """Structural problems that would make the generator emit nonsense. [] when sound."""
    problems: list[str] = []

    def bad(message):
        problems.append(message)

    for key in ('namespace', 'visible_event_offset', 'dated_starter_offset', 'late_starter_offset',
                'dated_delay_days', 'late_retry_days', 'late_mtth_months', 'refusal_days', 'refusal_label_suffix',
                'modifier_facts', 'source_registry', 'rows', 'not_modelled'):
        if key not in data:
            bad(f'missing top-level key {key}')
    if problems:
        return problems
    if not IDENT.match(data['namespace']):
        bad('namespace is not an identifier')
    facts = {k: v for k, v in data['modifier_facts'].items() if not k.startswith('_')}
    for name, fact in facts.items():
        if fact.get('role') not in ROLES:
            bad(f'modifier_facts.{name}: role must be one of {ROLES}')
        if not isinstance(fact.get('values'), dict) or not fact['values']:
            bad(f'modifier_facts.{name}: values missing')
    registry = {k: v for k, v in data['source_registry'].items() if not k.startswith('_')}
    if not any(f.get('role') == 'resistance' for f in facts.values()):
        bad('modifier_facts needs one resistance modifier for the refusal option')
    rows = data['rows']
    if not rows:
        bad('no rows')
    ids, numbers = set(), set()
    by_id = {r.get('id'): r for r in rows}
    for row in rows:
        rid = row.get('id', '?')
        where = f'row {rid}'
        if not IDENT.match(str(rid)):
            bad(f'{where}: id is not an identifier')
        if rid in ids:
            bad(f'{where}: duplicate id')
        ids.add(rid)
        number = row.get('number')
        if not isinstance(number, int) or not 1 <= number <= 99:
            bad(f'{where}: number must be an integer 1..99')
        elif number in numbers:
            bad(f'{where}: duplicate number {number}')
        numbers.add(number)
        if not isinstance(row.get('province_id'), int) or row['province_id'] <= 0:
            bad(f'{where}: province_id')
        if row.get('kind') not in KINDS:
            bad(f'{where}: kind must be one of {KINDS}')
        year, month = row.get('year'), row.get('month')
        if not isinstance(year, int) or not 1444 <= year <= 1821:
            bad(f'{where}: year must be an integer within the game (1444-1821)')
            continue
        if month is not None and (not isinstance(month, int) or not 0 <= month <= 11):
            bad(f'{where}: month is 0-based (0..11) or null')
        spread = row.get('spread_months')
        if not isinstance(spread, int) or spread < 0:
            bad(f'{where}: spread_months must be an integer >= 0')
        elif month is not None and spread:
            bad(f'{where}: a month row cannot spread over months')
        late = row.get('late_until')
        if not isinstance(late, int) or late < year or late > 1821:
            bad(f'{where}: late_until must be an integer from year to 1821')
        prerequisite = row.get('requires_row')
        if row.get('kind') == 'development':
            other = by_id.get(prerequisite)
            if other is None:
                bad(f'{where}: a development row needs requires_row naming a union_convert row')
            else:
                if other.get('kind') != 'union_convert' or other.get('province_id') != row.get('province_id'):
                    bad(f'{where}: requires_row must be a union_convert row on the same province')
                if isinstance(other.get('year'), int) and row_key(other) >= row_key(row):
                    bad(f'{where}: requires_row must come earlier in time')
        elif prerequisite is not None:
            bad(f'{where}: only a development row may have requires_row')
        outcome = row.get('outcome', {})
        if bool(outcome.get('convert')) != (row.get('kind') == 'union_convert'):
            bad(f'{where}: outcome.convert must be true exactly for union_convert')
        autonomy = outcome.get('autonomy')
        if not isinstance(autonomy, int) or autonomy < 0 or (autonomy and not outcome.get('convert')):
            bad(f'{where}: outcome.autonomy is an integer, non-zero only with convert')
        for flag in outcome.get('flags', []):
            if not IDENT.match(flag):
                bad(f'{where}: flag {flag!r}')
        groups = [('outcome', outcome.get('modifiers', []))]
        for extra in outcome.get('also', []):
            if not isinstance(extra.get('province_id'), int) or not extra.get('seat') or not extra.get('require_religion'):
                bad(f'{where}: an outcome.also entry needs province_id, seat and require_religion')
            groups.append(('also', extra.get('modifiers', [])))
        if not outcome.get('modifiers'):
            bad(f'{where}: outcome.modifiers is empty')
        for label, modifiers in groups:
            days = {m.get('days') for m in modifiers}
            if len(days) > 1:
                bad(f'{where}: {label} modifiers must share one duration (the text says it once)')
            for modifier in modifiers:
                if modifier.get('name') not in facts:
                    bad(f'{where}: modifier {modifier.get("name")!r} is not in modifier_facts')
                elif facts[modifier['name']].get('role') == 'resistance':
                    bad(f'{where}: the resistance modifier belongs to the refusal, not to acceptance')
                if not isinstance(modifier.get('days'), int) or modifier['days'] <= 0:
                    bad(f'{where}: modifier days')
                if not isinstance(modifier.get('if_absent'), bool):
                    bad(f'{where}: modifier {modifier.get("name")} needs if_absent true or false')
        text = row.get('text', {})
        for key in ('title', 'hist', 'here', 'caveat', 'option_a', 'option_b'):
            value = text.get(key)
            if not isinstance(value, str) or not value.strip():
                bad(f'{where}: text.{key} missing')
                continue
            if '"' in value or '\n' in value or '!' in value:
                bad(f'{where}: text.{key} holds a quote, a newline or an exclamation mark')
            if not value.isascii():
                bad(f'{where}: text.{key} must be ASCII (the label suffix adds the only dash)')
        if not str(row.get('fact_date', '')).strip():
            bad(f'{where}: fact_date missing')
        if not row.get('sources') or any(s not in registry for s in row['sources']):
            bad(f'{where}: sources must be non-empty ids of source_registry')
        if not str(row.get('dispute', '')).strip():
            bad(f'{where}: dispute note missing (write "none" when the sources agree)')
        if not isinstance(row.get('supported_years'), list) or year not in row.get('supported_years', []):
            bad(f'{where}: supported_years must list every year the text names, including the row year')
    return problems


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------


def names(row: dict) -> dict:
    i = row['id']
    return {
        'date_window': f'rip_eparchy_{i}_date_window',
        'late_window': f'rip_eparchy_{i}_late_window',
        'ready': f'rip_eparchy_{i}_ready',
        'possible': f'rip_eparchy_{i}_possible',
        'answered': f'rip_eparchy_{i}_answered',
        'scheduled': f'rip_eparchy_{i}_scheduled',
        'refused': f'rip_eparchy_{i}_refused',
        'late_flag': f'rip_eparchy_late_{i}',
    }


def event_ids(data: dict, row: dict) -> dict:
    ns = data['namespace']
    return {
        'visible': f"{ns}.{row['number'] + data['visible_event_offset']}",
        'dated': f"{ns}.{row['number'] + data['dated_starter_offset']}",
        'late': f"{ns}.{row['number'] + data['late_starter_offset']}",
    }


def loc_keys(data: dict, row: dict) -> dict:
    base = event_ids(data, row)['visible']
    return {k: f'{base}.{k}' for k in ('t', 'd', 'l', 'a', 'b')}


# ---------------------------------------------------------------------------
# Windows (fact F2)
# ---------------------------------------------------------------------------


def date_window_lines(row: dict) -> list[str]:
    year, month = row['year'], row['month']
    lines = [f'is_year = {year}', f'NOT = {{ is_year = {year + 1} }}']
    if month is not None:
        lines.append(f'is_month = {month}')
        if month < 11:
            lines.append(f'NOT = {{ is_month = {month + 1} }}')
    return lines


def late_window_lines(row: dict) -> list[str]:
    year, month, last = row['year'], row['month'], row['late_until']
    if month is None or month == 11:
        lines = [f'is_year = {year + 1}']
    else:
        lines = ['OR = {', f'\tAND = {{ is_year = {year} is_month = {month + 1} }}', f'\tis_year = {year + 1}', '}']
    lines.append(f'NOT = {{ is_year = {last + 1} }}')
    return lines


MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
          'September', 'October', 'November', 'December')


def when(row: dict) -> str:
    return f"{MONTHS[row['month']]} {row['year']}" if row['month'] is not None else f"{row['year']} (year only)"


# ---------------------------------------------------------------------------
# Rendering: scripts
# ---------------------------------------------------------------------------

HEADER = [
    '# GENERATED FILE - do not edit by hand.',
    f'# Source: tools/data/eparchy_timeline.json   Generator: {GENERATOR}',
    f'# Regenerate with: python {GENERATOR}   (add --check to fail when this file is stale)',
]


def indent(lines: list[str], depth: int) -> list[str]:
    return ['\t' * depth + line if line else line for line in lines]


def render_triggers(data: dict, harness: bool = False) -> str:
    out = list(HEADER)
    out += [
        '#',
        '# Province scope. One block of four triggers per row of the table:',
        '#   _date_window  exactly the month (or year) of the historical fact, fact F2 idiom',
        '#   _late_window  from the following month until the row\'s late_until year',
        '#   _ready        the seat can take the outcome right now',
        '#   _possible     _ready and the seat has not been answered yet',
    ]
    if harness:
        out += ['#', '# HARNESS COPY: date windows are always = yes and late windows always = no.',
                '# Never install this file in the mod; it exists to probe the chain in game.']
    for row in data['rows']:
        n = names(row)
        out += ['', f"# --- {row['id']}: {row['seat']} ({row['province_id']}), {when(row)}, {row['kind']}"]
        out.append(f"{n['date_window']} = {{")
        out += indent(['always = yes'] if harness else date_window_lines(row), 1)
        out.append('}')
        out.append(f"{n['late_window']} = {{")
        out += indent(['always = no'] if harness else late_window_lines(row), 1)
        out.append('}')
        religion = {'union_convert': 'orthodox', 'union_modifier_only': 'catholic', 'development': 'greek_catholic'}[row['kind']]
        out.append(f"{n['ready']} = {{")
        out += indent([
            f"province_id = {row['province_id']}",
            'is_city = yes',
            'controlled_by = owner',
            f'religion = {religion}',
            'owner = {',
            '\treligion = catholic',
            '\tNOT = { has_country_flag = rip_church_opposes_union }',
            '}',
        ], 1)
        out.append('}')
        out.append(f"{n['possible']} = {{")
        out += indent([f"{n['ready']} = yes", f"NOT = {{ has_province_flag = {n['answered']} }}"], 1)
        out.append('}')
    return '\n'.join(out) + '\n'


def modifier_lines(modifiers: list[dict]) -> list[str]:
    lines = []
    for m in modifiers:
        add = f"add_province_modifier = {{ name = {m['name']} duration = {m['days']} }}"
        if m['if_absent']:
            lines += ['if = {', f"\tlimit = {{ NOT = {{ has_province_modifier = {m['name']} }} }}", f'\t{add}', '}']
        else:
            lines.append(add)
    return lines


def outcome_lines(row: dict) -> list[str]:
    o = row['outcome']
    lines = [f'set_province_flag = {f}' for f in o['flags']]
    if o['convert']:
        lines.append('change_religion = greek_catholic')
        if o['autonomy']:
            lines.append(f"add_local_autonomy = {o['autonomy']}")
    lines += modifier_lines(o['modifiers'])
    for extra in o['also']:
        lines += [f"{extra['province_id']} = {{", '\tif = {', '\t\tlimit = {',
                  f"\t\t\treligion = {extra['require_religion']}",
                  '\t\t\towner = { religion = catholic }', '\t\t}']
        lines += indent(modifier_lines(extra['modifiers']), 2)
        lines += ['\t}', '}']
    return lines


def render_events(data: dict) -> str:
    ns = data['namespace']
    refusal_name = refusal_modifier(data)
    refusal_days = data['refusal_days']
    out = list(HEADER)
    out += [
        '#',
        '# Three events per row. Numbers: visible = row number, dated starter = +100, late starter = +200.',
        '#   dated starter  hidden; opens in the exact month, schedules the visible event ten days on.',
        '#                  fire_only_once and the scheduled-flag guard both stop a daily MTTH from scheduling twice.',
        '#                  The empty option copies all 210 hidden events of vanilla, none of which lacks one.',
        '#   late starter   hidden; from the following month, retries every ~6 months until late_until',
        '#   visible event  is_triggered_only; sets the answered flag first, so each seat is asked once',
        '# No scripted effect, no else_if, no add_opinion: the engine drops those in else_if bodies (F1).',
        f'namespace = {ns}',
    ]
    for row in data['rows']:
        n, ids, keys = names(row), event_ids(data, row), loc_keys(data, row)
        province = row['province_id']
        out += ['', f"# === {row['id']}: {row['seat']} ({province}), {when(row)}, {row['kind']}"]
        # Dated starter.
        out += [
            'province_event = {',
            f"\tid = {ids['dated']}",
            '\thidden = yes',
            '\tfire_only_once = yes',
            '\ttrigger = {',
            f'\t\tprovince_id = {province}',
            f"\t\t{n['date_window']} = yes",
            f"\t\tNOT = {{ has_province_flag = {n['scheduled']} }}",
            f"\t\t{n['possible']} = yes",
            '\t}',
            '\tmean_time_to_happen = { ' + (f"months = {row['spread_months']}" if row['spread_months'] else 'days = 1') + ' }',
            '\timmediate = {',
            f"\t\tset_province_flag = {n['scheduled']}",
            f"\t\tprovince_event = {{ id = {ids['visible']} days = {data['dated_delay_days']} }}",
            '\t}',
            '\toption = { }',
            '}',
        ]
        # Late starter.
        out += [
            'province_event = {',
            f"\tid = {ids['late']}",
            '\thidden = yes',
            '\ttrigger = {',
            f'\t\tprovince_id = {province}',
            f"\t\t{n['late_window']} = yes",
            f"\t\t{n['possible']} = yes",
            '\t\tOR = {',
            f"\t\t\tNOT = {{ has_province_flag = {n['scheduled']} }}",
            f"\t\t\thad_province_flag = {{ flag = {n['scheduled']} days = {data['late_retry_days']} }}",
            '\t\t}',
            '\t}',
            f"\tmean_time_to_happen = {{ months = {data['late_mtth_months']} }}",
            '\timmediate = {',
            f"\t\tset_province_flag = {n['late_flag']}",
            f"\t\tprovince_event = {{ id = {ids['visible']} }}",
            '\t}',
            '\toption = { }',
            '}',
        ]
        # Visible event.
        out += [
            'province_event = {',
            f"\tid = {ids['visible']}",
            f"\ttitle = {keys['t']}",
            '\tdesc = {',
            f"\t\ttrigger = {{ NOT = {{ has_province_flag = {n['late_flag']} }} }}",
            f"\t\tdesc = {keys['d']}",
            '\t}',
            '\tdesc = {',
            f"\t\ttrigger = {{ has_province_flag = {n['late_flag']} }}",
            f"\t\tdesc = {keys['l']}",
            '\t}',
            '\tpicture = RELIGION_eventPicture',
            '\tis_triggered_only = yes',
            '\ttrigger = {',
            f"\t\t{n['possible']} = yes",
            '\t}',
            '\timmediate = {',
            f"\t\tset_province_flag = {n['answered']}",
            '\t}',
            '\toption = {',
            f"\t\tname = {keys['a']}",
            '\t\ttrigger = {',
            f"\t\t\t{n['ready']} = yes",
            '\t\t}',
            '\t\tai_chance = { factor = 90 }',
            '\t\tif = {',
            '\t\t\tlimit = {',
            f"\t\t\t\t{n['ready']} = yes",
            '\t\t\t}',
        ]
        out += indent(outcome_lines(row), 3)
        out += [
            '\t\t}',
            '\t}',
            '\toption = {',
            f"\t\tname = {keys['b']}",
            '\t\tai_chance = { factor = 10 }',
            f'\t\tadd_province_modifier = {{ name = {refusal_name} duration = {refusal_days} }}',
            f"\t\tset_province_flag = {n['refused']}",
            '\t}',
            '}',
        ]
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------------------
# Rendering: texts. Every number printed comes from modifier_facts.
# ---------------------------------------------------------------------------

STAT_LABEL = {
    'local_tax_modifier': 'local tax',
    'local_autonomy': 'local autonomy',
    'local_development_cost': 'local development cost',
    'local_state_maintenance_modifier': 'local state maintenance',
    'local_institution_spread': 'local institution spread',
}


def stat(key: str, value) -> str:
    if key == 'local_unrest':
        return f'{value:+g} local unrest'
    return f'{round(value * 100):+d}% {STAT_LABEL[key]}'


def shown_stats(fact: dict) -> list[str]:
    """Everything the text names; missionary strength is described by the protection role instead."""
    return [stat(k, v) for k, v in fact['values'].items() if k != 'local_missionary_strength']


def join_and(items: list[str]) -> str:
    if len(items) <= 2:
        return ' and '.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def years_words(days: int) -> str:
    return {3650: 'ten years', 7300: 'twenty years'}.get(days, f'{days // 365} years')


def clause(name: str, facts: dict, seat: str) -> str:
    fact = facts[name]
    role, stats = fact['role'], ', '.join(shown_stats(fact))
    if role == 'protection':
        return 'protects the rite from missionary conversion'
    if role == 'diocese':
        return f'grants a diocese ({stats})'
    if role == 'metropolitan':
        return f'makes {seat} a metropolitan see ({stats})'
    raise ValueError(role)


def accept_sentence(row: dict, facts: dict) -> str:
    o = row['outcome']
    verbs = [clause(m['name'], facts, row['seat']) for m in o['modifiers']]
    days = years_words(o['modifiers'][0]['days'])
    if o['convert']:
        text = f"Acceptance makes the province Greek Catholic at the cost of {o['autonomy']} local autonomy; it also {join_and(verbs)} for {days}."
    else:
        text = f'Acceptance {join_and(verbs)} for {days}.'
    for extra in o['also']:
        nouns = {'protection': 'the protection', 'diocese': 'the diocese', 'metropolitan': 'the metropolitan see'}
        items = [nouns[facts[m['name']]['role']] for m in extra['modifiers']]
        # The diocese reads better before the protection it comes with.
        items.sort(key=lambda s: s == 'the protection')
        text += f" A {extra['require_religion'].replace('_', ' ').title()} {extra['seat']} receives {join_and(items)} as well."
    return text


def refusal_modifier(data: dict) -> str:
    return next(k for k, v in data['modifier_facts'].items() if isinstance(v, dict) and v.get('role') == 'resistance')


def refusal_sentence(data: dict) -> str:
    fact = data['modifier_facts'][refusal_modifier(data)]
    return (f"Refusal is alternative history: the province keeps its faith and gains "
            f"{join_and(shown_stats(fact))} for {years_words(data['refusal_days'])}.")


def desc_text(data: dict, row: dict, late: bool) -> str:
    facts = {k: v for k, v in data['modifier_facts'].items() if not k.startswith('_')}
    t = row['text']
    first = t['hist'] + (' ' + LATE_TAIL if late else '')
    second = ' '.join([t['here'], accept_sentence(row, facts), refusal_sentence(data), t['caveat']])
    return first + '\\n\\n' + second


def loc_entries(data: dict) -> list[tuple[str, str]]:
    entries = []
    for row in data['rows']:
        keys = loc_keys(data, row)
        entries += [
            (keys['t'], row['text']['title']),
            (keys['d'], desc_text(data, row, late=False)),
            (keys['l'], desc_text(data, row, late=True)),
            (keys['a'], row['text']['option_a']),
            (keys['b'], row['text']['option_b'] + data['refusal_label_suffix']),
        ]
    return entries


def render_loc(data: dict) -> str:
    out = ['l_english:'] + [f' {line}' for line in HEADER]
    out += [' # Texts: a sourced historical fact first, then what the game model does ("Here ..."),',
            ' # then the outcomes and a dry caveat. Refusal options carry the alternative-history label.']
    out += [f' {key}:0 "{value}"' for key, value in loc_entries(data)]
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------


def encode_script(text: str) -> bytes:
    return text.replace('\n', '\r\n').encode('cp1252')


def encode_loc(text: str) -> bytes:
    return ('﻿' + text).replace('\n', '\r\n').encode('utf-8')


def outputs(data: dict) -> dict[str, bytes]:
    return {
        TRIGGERS: encode_script(render_triggers(data)),
        EVENTS: encode_script(render_events(data)),
        LOC: encode_loc(render_loc(data)),
    }


def same(a: bytes, b: bytes) -> bool:
    """Compare ignoring the checkout's line-ending style (core.autocrlf)."""
    return a.replace(b'\r\n', b'\n') == b.replace(b'\r\n', b'\n')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='exit 1 when a generated file is stale')
    parser.add_argument('--harness', type=Path, help='write a probe copy of the triggers with forced windows')
    args = parser.parse_args(argv)
    data = load()
    problems = validate(data)
    if problems:
        print('eparchy timeline table is invalid:')
        for problem in problems:
            print('  ' + problem)
        return 1
    if args.harness:
        args.harness.mkdir(parents=True, exist_ok=True)
        target = args.harness / Path(TRIGGERS).name
        target.write_bytes(encode_script(render_triggers(data, harness=True)))
        print(f'HARNESS copy written to {target} (not loaded by the game)')
        return 0
    stale = []
    for relative, content in outputs(data).items():
        path = ROOT / relative
        if not path.exists() or not same(path.read_bytes(), content):
            stale.append(relative)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
    count = len(data['rows'])
    if args.check:
        if stale:
            print(f'STALE: {", ".join(stale)}; run python {GENERATOR}')
            return 1
        print(f'CURRENT: {count} rows, 3 generated files match tools/data/eparchy_timeline.json')
        return 0
    print(f'GENERATED: {count} rows; rewrote {len(stale)} of 3 files' + (f' ({", ".join(stale)})' if stale else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())
