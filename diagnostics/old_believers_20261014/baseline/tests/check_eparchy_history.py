"""Contracts for the dated eparchy timeline under Catholic states.

Source of truth is tools/data/eparchy_timeline.json; tools/build_eparchy_timeline.py
writes the triggers, events and English texts from it. This check keeps the whole
chain honest:

  * the generator is current and the table is structurally sound;
  * every date window is EXACT under the engine's `>=` reading of is_year / is_month
    (a truth table over every year and month of the game, not a text match);
  * events keep the safe shape: starters hidden with MTTH, the visible event
    is_triggered_only, the answered flag set before any option, no else_if,
    no add_opinion, no scripted effect;
  * every id, flag, modifier, province and localisation key referenced exists, and
    no flag is set that nothing reads (the one deliberate record-only flag is named);
  * the numbers in the texts equal the real modifier files, and no diocesan
    modifier is applied without the rite guarantee that cancels its missionary pull;
  * historical texts name only years the row lists as supported, and cite only
    sources copied from history_research.json;
  * the Ukrainian document carries exactly the dates of the table;
  * a reachability model reads the province and country histories and says which
    rows can ever fire in default history.

Each problem-finder is a pure function of text, and PLANTED proves it by feeding a
deliberately broken copy and requiring a complaint.

LIMIT: this is a static contract. It does not run EU4; the in-game behaviour of the
starters rests on the probes recorded in tools/build_eparchy_timeline.py (F1-F7).
"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, matching_brace, read, vanilla_root

sys.path.insert(0, str(ROOT / 'tools'))
import build_eparchy_timeline as gen  # noqa: E402

DOC = 'docs/EPARCHY_TIMELINE.uk.md'
HISTORY_JSON_ENV = 'EPARCHY_RESEARCH_JSON'
# Set on purpose and read by nothing in game: a record of the refusal for the random
# Diocesan Union fallback and later content (the fallback has its own resistance-modifier
# guard). Named here so a NEW unread flag still fails the check.
RECORD_ONLY_FLAG_SUFFIXES = ('_refused',)
ALLOWED_HOSTS = ('www.encyclopediaofukraine.com', 'en.wikipedia.org', 'risu.ua', 'ugcc.ua',
                 'www.constantinesletters.ukf.sk')
BANNED_WORDS = re.compile(r'\b(?:identity|democracy|democratic|ethnic|ideology)\b', re.I)
BANNED_SPELLINGS = re.compile(r'\b(?:Przemysl|Lwow|Lemberg|Luck|Galich|Kiev|Volyn)\b')
DESC_LIMIT = 900           # characters; the longest text here is 841, the sibling rip_uzh_union.1.d about 700
LABEL_LIMIT = 7            # words; the mod's option labels average four


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def tokens_of(text: str):
    return re.findall(r'"[^"\n]*"|[{}=]|[^\s{}=]+', re.sub(r'#[^\n]*', '', text))


def parse_pairs(text: str):
    tokens, pos = tokens_of(text), 0

    def block():
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]
            if pos + 1 >= len(tokens) or tokens[pos + 1] != '=':
                raise ValueError(f'expected = after {key}')
            pos += 2
            if tokens[pos] == '{':
                pos += 1
                value = block()
                pos += 1
            else:
                value = tokens[pos].strip('"')
                pos += 1
            result.append((key, value))
        return result
    return block()


def top_level_blocks(text: str, key: str) -> list[str]:
    """Column-0 `key = {` blocks (definitions), never the indented calls inside effects."""
    found = []
    masked = re.sub(r'#[^\n]*', lambda m: ' ' * len(m.group(0)), text)
    for match in re.finditer(rf'(?m)^{re.escape(key)}\s*=\s*\{{', masked):
        opening = text.index('{', match.start())
        found.append(text[match.start():matching_brace(text, opening) + 1])
    return found


def event_blocks(events: str) -> dict[str, str]:
    result = {}
    for block in top_level_blocks(events, 'province_event'):
        result[re.search(r'\bid\s*=\s*(\S+)', block).group(1)] = block
    return result


def trigger_blocks(text: str) -> dict[str, str]:
    result = {}
    masked = re.sub(r'#[^\n]*', lambda m: ' ' * len(m.group(0)), text)
    for match in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', masked):
        opening = text.index('{', match.start())
        closing = matching_brace(text, opening)
        result[match.group(1)] = text[opening + 1:closing]
    return result


def read_loose(path: Path) -> str:
    """Whole file, tolerant of the Windows-1252 accents the mod's script files carry."""
    return path.read_text(encoding='utf-8-sig', errors='replace')


def words(text: str) -> int:
    return len(text.split())


# ---------------------------------------------------------------------------
# 1. Generator and table
# ---------------------------------------------------------------------------


def generator_problems(data: dict, actual: dict[str, bytes]) -> list[str]:
    problems = list(gen.validate(data))
    if problems:
        return problems
    for relative, content in gen.outputs(data).items():
        if relative not in actual:
            problems.append(f'{relative}: file missing')
        elif not gen.same(actual[relative], content):
            problems.append(f'{relative}: stale; run python tools/build_eparchy_timeline.py')
    for relative, raw in actual.items():
        if relative.endswith('.yml'):
            if not raw.startswith(b'\xef\xbb\xbf'):
                problems.append(f'{relative}: localisation must be UTF-8 with BOM')
        elif raw.startswith(b'\xef\xbb\xbf'):
            problems.append(f'{relative}: script must have no BOM')
        else:
            try:
                raw.decode('cp1252')
            except UnicodeDecodeError:
                problems.append(f'{relative}: not Windows-1252')
    return problems


# ---------------------------------------------------------------------------
# 2. Windows: a truth table under the engine's >= reading (fact F2)
# ---------------------------------------------------------------------------


def holds(items, year: int, month: int) -> bool:
    """Evaluate a parsed trigger list. is_year / is_month are >= tests; NOT is NOR."""
    def one(key, value):
        if key == 'is_year':
            return year >= int(value)
        if key == 'is_month':
            return month >= int(value)
        if key == 'NOT':
            return not any(one(k, v) for k, v in value)
        if key == 'OR':
            return any(one(k, v) for k, v in value)
        if key == 'AND':
            return all(one(k, v) for k, v in value)
        if key == 'always':
            return value == 'yes'
        raise ValueError(f'window uses an unsupported trigger: {key}')
    return all(one(k, v) for k, v in items)


def expected_date(row, year, month):
    if year != row['year']:
        return False
    return row['month'] is None or month == row['month']


def expected_late(row, year, month):
    if not row['year'] <= year <= row['late_until']:
        return False
    if year > row['year']:
        return True
    return row['month'] is not None and month > row['month']


def edge_window_problems(data: dict) -> list[str]:
    """January, December and year-only are the edges of the idiom; prove the generator gets them right
    for a future row even though no v1 row sits there."""
    problems = []
    for month in (0, 11, None):
        clone = copy.deepcopy(data)
        row = clone['rows'][0]
        row['month'], row['spread_months'] = month, (3 if month is None else 0)
        problems += [f'edge month {month}: {p}' for p in window_problems(clone, gen.render_triggers(clone))]
    return problems


def window_problems(data: dict, triggers: str) -> list[str]:
    problems = []
    blocks = trigger_blocks(triggers)
    for row in data['rows']:
        n = gen.names(row)
        for label, key, want in (('date', 'date_window', expected_date), ('late', 'late_window', expected_late)):
            body = blocks.get(n[key])
            if body is None:
                problems.append(f"{row['id']}: trigger {n[key]} missing")
                continue
            try:
                items = parse_pairs(body)
            except (ValueError, IndexError) as error:
                problems.append(f"{row['id']}: {n[key]} does not parse ({error})")
                continue
            wrong, error = [], None
            for year in range(1444, 1823):
                for month in range(12):
                    try:
                        got = holds(items, year, month)
                    except ValueError as exc:
                        error = str(exc)
                        break
                    if got != want(row, year, month):
                        wrong.append(f'{year}-{month + 1:02d}')
                if error:
                    break
            if error:
                problems.append(f"{row['id']}: {n[key]}: {error}")
                continue
            if wrong:
                problems.append(f"{row['id']}: {label} window is wrong at {', '.join(wrong[:4])}"
                                + (f' (+{len(wrong) - 4} more)' if len(wrong) > 4 else ''))
    return problems


# ---------------------------------------------------------------------------
# 3. Events
# ---------------------------------------------------------------------------


def flag_sets_and_reads(*texts: str):
    sets, reads = set(), set()
    for text in texts:
        sets |= set(re.findall(r'set_province_flag\s*=\s*(\w+)', text))
        reads |= set(re.findall(r'has_province_flag\s*=\s*(\w+)', text))
        reads |= set(re.findall(r'had_province_flag\s*=\s*\{\s*flag\s*=\s*(\w+)', text))
    return sets, reads


def event_problems(data: dict, events: str, triggers: str, loc_keys: set[str]) -> list[str]:
    problems = []
    blocks = event_blocks(events)
    expected_ids = set()
    code = re.sub(r'#[^\n]*', '', events)      # the generated header talks about these words
    if re.search(r'\b(?:else_if|else)\s*=\s*\{', code):
        problems.append('events use else / else_if (the engine drops events and opinions in scripted-effect else bodies; keep it out)')
    for banned in ('add_opinion', 'country_event', 'reverse_add_opinion', 'add_years_of_income', 'add_treasury',
                   'add_dip_power', 'add_adm_power', 'set_country_flag', 'add_casus_belli'):
        if banned in code:
            problems.append(f'events contain {banned}: historical rows carry no costs, patron flags or opinions')
    if 'rip_church_supports_union' in code or 'rip_du_catholic_patron' in code:
        problems.append('events touch the patron flag; the timeline must not grant free patronage')
    for row in data['rows']:
        ids = gen.event_ids(data, row)
        n, keys = gen.names(row), gen.loc_keys(data, row)
        expected_ids |= set(ids.values())
        missing = [role for role in ('dated', 'late', 'visible') if ids[role] not in blocks]
        for role in missing:
            problems.append(f"{row['id']}: event {ids[role]} ({role}) missing")
        if missing:
            continue
        dated, late, visible = blocks[ids['dated']], blocks[ids['late']], blocks[ids['visible']]
        for role, block in (('dated starter', dated), ('late starter', late)):
            if not re.search(r'(?m)^\s*hidden\s*=\s*yes', block):
                problems.append(f"{row['id']}: {role} is not hidden")
            if 'mean_time_to_happen' not in block:
                problems.append(f"{row['id']}: {role} has no mean_time_to_happen")
            if 'option = {' not in block:
                problems.append(f"{row['id']}: {role} has no option (all 210 hidden events of vanilla carry one)")
            if 'is_triggered_only' in block:
                problems.append(f"{row['id']}: {role} mixes is_triggered_only with mean_time_to_happen (load error)")
            if f"province_id = {row['province_id']}" not in block:
                problems.append(f"{row['id']}: {role} does not pin province_id = {row['province_id']}")
            if re.search(r'\bis_(?:year|month)\b', block):
                problems.append(f"{row['id']}: {role} spells a date inline; use the named window")
        if not re.search(r'(?m)^\s*fire_only_once\s*=\s*yes', dated):
            problems.append(f"{row['id']}: dated starter lacks fire_only_once (the shape the engine probes measured)")
        if n['date_window'] not in dated or n['possible'] not in dated:
            problems.append(f"{row['id']}: dated starter must test its date window and possible")
        if f"NOT = {{ has_province_flag = {n['scheduled']} }}" not in dated:
            problems.append(f"{row['id']}: dated starter does not guard itself with the scheduled flag; with MTTH 1 day it would schedule the event again")
        if f"set_province_flag = {n['scheduled']}" not in dated:
            problems.append(f"{row['id']}: dated starter never sets the scheduled flag")
        if f"province_event = {{ id = {ids['visible']} days = {data['dated_delay_days']} }}" not in dated:
            problems.append(f"{row['id']}: dated starter does not schedule the visible event {data['dated_delay_days']} days on")
        expected_mtth = f"months = {row['spread_months']}" if row['spread_months'] else 'days = 1'
        if f'mean_time_to_happen = {{ {expected_mtth} }}' not in dated:
            problems.append(f"{row['id']}: dated starter MTTH should be {expected_mtth}")
        if n['late_window'] not in late or n['possible'] not in late:
            problems.append(f"{row['id']}: late starter must test its late window and possible")
        if f"had_province_flag = {{ flag = {n['scheduled']} days = {data['late_retry_days']} }}" not in late:
            problems.append(f"{row['id']}: late starter does not wait for a stale scheduled flag")
        if f"set_province_flag = {n['late_flag']}" not in late or f"province_event = {{ id = {ids['visible']} }}" not in late:
            problems.append(f"{row['id']}: late starter must set the late flag and fire the visible event")
        if f"mean_time_to_happen = {{ months = {data['late_mtth_months']} }}" not in late:
            problems.append(f"{row['id']}: late starter MTTH months = {data['late_mtth_months']} missing")
        # Visible event.
        if not re.search(r'(?m)^\s*is_triggered_only\s*=\s*yes', visible):
            problems.append(f"{row['id']}: visible event is not is_triggered_only")
        if 'mean_time_to_happen' in visible:
            problems.append(f"{row['id']}: visible event mixes is_triggered_only with mean_time_to_happen (load error)")
        if f"{n['possible']} = yes" not in visible.split('immediate')[0]:
            problems.append(f"{row['id']}: visible event trigger must be possible")
        immediate = re.search(r'immediate\s*=\s*\{([^}]*)\}', visible)
        first_option = visible.find('option = {')
        if not immediate or f"set_province_flag = {n['answered']}" not in immediate.group(1):
            problems.append(f"{row['id']}: visible event does not set the answered flag in immediate")
        elif not 0 <= immediate.start() < first_option:
            problems.append(f"{row['id']}: answered flag must be set before the options")
        if visible.count('option = {') != 2:
            problems.append(f"{row['id']}: visible event needs exactly two options")
        options = re.split(r'(?m)^\toption = \{', visible)[1:]
        if len(options) == 2:
            a, b = options
            if keys['a'] not in a or 'ai_chance = { factor = 90 }' not in a:
                problems.append(f"{row['id']}: option a must be {keys['a']} with ai_chance 90")
            if keys['b'] not in b or 'ai_chance = { factor = 10 }' not in b:
                problems.append(f"{row['id']}: option b must be {keys['b']} with ai_chance 10")
            if f"{n['ready']} = yes" not in a.split('ai_chance')[0]:
                problems.append(f"{row['id']}: option a must be gated by ready")
            if f"limit = {{ {n['ready']} = yes }}" not in re.sub(r'\s+', ' ', a):
                problems.append(f"{row['id']}: option a must re-check ready before acting (a stale dialog)")
            if ('change_religion = greek_catholic' in a) != (row['kind'] == 'union_convert'):
                problems.append(f"{row['id']}: change_religion belongs to union_convert rows only")
            if 'change_religion' in b:
                problems.append(f"{row['id']}: the refusal must not change religion")
            if f"add_province_modifier = {{ name = {gen.refusal_modifier(data)} duration = {data['refusal_days']} }}" not in b:
                problems.append(f"{row['id']}: the refusal must add the resistance modifier for {data['refusal_days']} days")
            if f"set_province_flag = {n['refused']}" not in b:
                problems.append(f"{row['id']}: the refusal must set the refused flag")
            if ('rip_du_approached' in a) != ('rip_du_approached' in row['outcome']['flags']):
                problems.append(f"{row['id']}: rip_du_approached must follow the row's flags")
        if [k for k in re.findall(r'(?m)^\t\tdesc = (\S+)$', visible)] != [keys['d'], keys['l']]:
            problems.append(f"{row['id']}: visible event needs the two alternate descs {keys['d']} and {keys['l']}")
        if f"title = {keys['t']}" not in visible:
            problems.append(f"{row['id']}: visible event title key {keys['t']}")
        for key in keys.values():
            if key not in loc_keys:
                problems.append(f"{row['id']}: localisation key {key} missing")
    for event_id in blocks:
        if event_id not in expected_ids:
            problems.append(f'event {event_id} is not produced by any row')
    for target in re.findall(r'province_event\s*=\s*\{\s*id\s*=\s*(\S+)', events):
        if target not in blocks:
            problems.append(f'a starter fires {target}, which does not exist')
    if code.count('change_religion') != sum(r['kind'] == 'union_convert' for r in data['rows']):
        problems.append('change_religion appears a different number of times than there are union_convert rows')
    # Flags: everything read is set, everything set is read (one record-only suffix allowed).
    sets, reads = flag_sets_and_reads(code, re.sub(r'#[^\n]*', '', triggers))
    mine = {f for f in sets | reads if f.startswith('rip_eparchy_')}
    for flag in sorted(f for f in mine if f in reads and f not in sets):
        problems.append(f'flag {flag} is read but never set')
    for flag in sorted(f for f in mine if f in sets and f not in reads and not f.endswith(RECORD_ONLY_FLAG_SUFFIXES)):
        problems.append(f'flag {flag} is set but nothing reads it (declared, localised, connected to nothing)')
    if re.search(r'\bis_(?:year|month)\b', code):
        problems.append('events spell a date inline; every date lives in a named window')
    return problems


# ---------------------------------------------------------------------------
# 4. References into the rest of the mod
# ---------------------------------------------------------------------------


def modifier_definitions() -> dict[str, dict[str, float]]:
    found = {}
    for path in sorted((ROOT / 'common/event_modifiers').glob('*.txt')):
        text = path.read_text(encoding='utf-8-sig', errors='replace')
        masked = re.sub(r'#[^\n]*', lambda m: ' ' * len(m.group(0)), text)
        for match in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', masked):
            opening = text.index('{', match.start())
            body = text[opening + 1:matching_brace(text, opening)]
            found[match.group(1)] = {k: float(v) for k, v in re.findall(r'(\w+)\s*=\s*(-?\d+(?:\.\d+)?)\b', body)}
    return found


def modifier_problems(data: dict, definitions: dict[str, dict[str, float]], events: str) -> list[str]:
    problems = []
    facts = {k: v for k, v in data['modifier_facts'].items() if not k.startswith('_')}
    for name, fact in facts.items():
        real = definitions.get(name)
        if real is None:
            problems.append(f'modifier {name} is not defined in common/event_modifiers')
            continue
        for key, value in fact['values'].items():
            if abs(real.get(key, float('nan')) - value) > 1e-9:
                problems.append(f'modifier {name}: the text says {key} = {value} but the file has {real.get(key)}')
        extra = set(real) - set(fact['values'])
        if extra:
            problems.append(f'modifier {name} now also has {sorted(extra)}; the text would not mention it')
        if not all(k.startswith('local_') for k in real):
            problems.append(f'modifier {name} is not a province modifier (a non-local key): add_province_modifier would misapply it')
    used = set(re.findall(r'add_province_modifier\s*=\s*\{\s*name\s*=\s*(\w+)', events))
    used |= set(re.findall(r'has_province_modifier\s*=\s*(\w+)', events))
    for name in sorted(used - set(facts)):
        problems.append(f'events use modifier {name}, which modifier_facts does not describe')
    # Diocesan pull: every preset that adds a positive local missionary strength also adds the guarantee.
    guarantee = next((k for k, v in facts.items() if v['role'] == 'protection'), None)
    for row in data['rows']:
        groups = [row['outcome']['modifiers']] + [e['modifiers'] for e in row['outcome']['also']]
        for modifiers in groups:
            names = {m['name']: m for m in modifiers}
            pull = sum(max(facts[m]['values'].get('local_missionary_strength', 0), 0) for m in names)
            if pull:
                if guarantee not in names:
                    problems.append(f"{row['id']}: adds missionary pull {pull} without {guarantee}")
                else:
                    shield = -facts[guarantee]['values']['local_missionary_strength']
                    if shield < pull:
                        problems.append(f"{row['id']}: {guarantee} ({shield}) does not cancel the pull {pull}")
                    if names[guarantee]['days'] < max(m['days'] for m in modifiers):
                        problems.append(f"{row['id']}: {guarantee} expires before the modifier it protects")
    return problems


def province_history_path(province_id: int) -> Path | None:
    for base in (ROOT, vanilla_root()):
        if base is None:
            continue
        hits = sorted((base / 'history/provinces').glob(f'{province_id} - *.txt'))
        if hits:
            return hits[0]
    return None


def reference_problems(data: dict, events: str) -> list[str]:
    problems = []
    provinces = {r['province_id'] for r in data['rows']} | {e['province_id'] for r in data['rows'] for e in r['outcome']['also']}
    for province_id in sorted(provinces):
        path = province_history_path(province_id)
        if path is None:
            if vanilla_root() is not None:
                problems.append(f'province {province_id} has no history file in the mod or in vanilla')
    # Existing switches the rows lean on must still exist somewhere in the mod.
    triggers = read_loose(ROOT / 'common/scripted_triggers/rip_diocesan_union_triggers.txt')
    if 'has_province_flag = rip_du_approached' not in triggers:
        problems.append('rip_du_approached is no longer read by rip_du_eligible_diocese: the fallback would re-target a seat')
    corpus = ''.join(read_loose(p) for p in list((ROOT / 'decisions').glob('*.txt'))
                     + list((ROOT / 'common/scripted_effects').glob('*.txt')) + list((ROOT / 'events').glob('*.txt')))
    if 'set_country_flag = rip_church_opposes_union' not in corpus:
        problems.append('nothing sets rip_church_opposes_union any more; the ready trigger guards against a dead flag')
    return problems


def other_files_corpus() -> dict[str, str]:
    """Every script and localisation file the game loads, except the three this table generates."""
    generated = {gen.TRIGGERS, gen.EVENTS, gen.LOC}
    corpus = {}
    for folder in ('common', 'events', 'decisions', 'missions', 'customizable_localization', 'localisation', 'interface'):
        for path in sorted((ROOT / folder).rglob('*')):
            relative = path.relative_to(ROOT).as_posix()
            if path.is_file() and path.suffix in ('.txt', '.yml', '.gui') and relative not in generated:
                corpus[relative] = read_loose(path)
    return corpus


def external_reference_problems(data: dict, corpus: dict[str, str]) -> list[str]:
    """Other files may lean on the flags and triggers named here (rip_du_seat_open reads the
    answered flags). A rename in the table must not leave them reading a name that no longer exists."""
    defined = set()
    for row in data['rows']:
        defined |= set(gen.names(row).values()) | set(gen.event_ids(data, row).values())
    problems = []
    for path, text in corpus.items():
        code = re.sub(r'#[^\n]*', '', text)
        for token in sorted(set(re.findall(r'\brip_eparchy(?:_[a-z0-9_]+|\.\d+)', code))):
            if token not in defined:
                problems.append(f'{path} refers to {token}, which the eparchy table does not define')
    return problems


def loc_problems(data: dict, loc_text: str) -> list[str]:
    problems = []
    entries = dict(re.findall(r'(?m)^ (\S+):0 "(.*)"$', loc_text))
    expected = dict(gen.loc_entries(data))
    for key in expected:
        if key not in entries:
            problems.append(f'localisation key {key} missing')
    for key in entries:
        if key not in expected:
            problems.append(f'localisation key {key} is not produced by any row')
    for row in data['rows']:
        keys = gen.loc_keys(data, row)
        for suffix in ('d', 'l'):
            text = entries.get(keys[suffix], '')
            if len(text) > DESC_LIMIT:
                problems.append(f"{keys[suffix]}: {len(text)} characters, over the {DESC_LIMIT} the event window is built for")
            if 'Here' not in text:
                problems.append(f"{keys[suffix]}: no 'Here ...' sentence separating history from the game model")
            if text.count('\\n\\n') != 1:
                problems.append(f'{keys[suffix]}: expected one paragraph break between the fact and the model')
            if not text.split('\\n\\n')[0].startswith(row['text']['hist'][:40]):
                problems.append(f'{keys[suffix]}: the historical fact must come first')
        if gen.LATE_TAIL not in entries.get(keys['l'], '') or gen.LATE_TAIL in entries.get(keys['d'], ''):
            problems.append(f"{row['id']}: only the late text may say the date has passed")
        label = entries.get(keys['b'], '')
        if not label.endswith(data['refusal_label_suffix']):
            problems.append(f"{keys['b']}: the refusal option must carry the alternative-history label")
        for suffix in ('a', 'b'):
            text = entries.get(keys[suffix], '').removesuffix(data['refusal_label_suffix'])
            if words(text) > LABEL_LIMIT:
                problems.append(f"{keys[suffix]}: {words(text)} words; option labels are short imperatives")
        # The year check is per row so a text cannot smuggle in an unlisted year.
        hist_years = {int(y) for y in re.findall(r'\b(1[4-9]\d\d)s?\b', row['text']['hist'])}
        for year in sorted(hist_years - set(row['supported_years'])):
            problems.append(f"{row['id']}: hist names {year}, which supported_years does not list")
        for year in sorted(set(row['supported_years']) - hist_years - {row['year']}):
            problems.append(f"{row['id']}: supported_years lists {year} but the text does not use it")
        if row['fact_date'] not in row['text']['hist']:
            problems.append(f"{row['id']}: hist must state the fact date {row['fact_date']!r}")
        if str(row['year']) not in row['fact_date'] and not row.get('date_choice_note'):
            problems.append(f"{row['id']}: the window year differs from the fact date without a date_choice_note")
    for key, text in entries.items():
        if '!' in text:
            problems.append(f'{key}: exclamation mark')
        if BANNED_WORDS.search(text):
            problems.append(f'{key}: banned register word {BANNED_WORDS.search(text).group(0)}')
        if BANNED_SPELLINGS.search(text):
            problems.append(f'{key}: spelling {BANNED_SPELLINGS.search(text).group(0)} (glossary: Peremyshl, Lviv, Lutsk, Volhynia)')
        if re.search(r'https?://', text):
            problems.append(f'{key}: a URL in player-facing text')
    return problems


def source_problems(data: dict) -> list[str]:
    problems = []
    registry = {k: v for k, v in data['source_registry'].items() if not k.startswith('_')}
    for key, url in registry.items():
        host = re.match(r'https://([^/]+)/', url)
        if not host or host.group(1) not in ALLOWED_HOSTS:
            problems.append(f'source {key}: host of {url} is not one the research used')
    for row in data['rows']:
        for source in row['sources']:
            if source not in registry:
                problems.append(f"{row['id']}: cites {source}, which is not in source_registry (history_research.json)")
    path = os.environ.get(HISTORY_JSON_ENV)
    if path and Path(path).is_file():
        research = json.loads(Path(path).read_text(encoding='utf-8-sig'))
        allowed = {u.replace('\\\\', '\\') for e in research['eparchies'] for u in e['sources']}
        for key, url in registry.items():
            if url.replace('\\\\', '\\') not in allowed:
                problems.append(f'source {key}: {url} is not among the URLs of history_research.json')
    return problems


# ---------------------------------------------------------------------------
# 5. The Ukrainian document
# ---------------------------------------------------------------------------


def table_cells(doc: str, row_id: str) -> list[str] | None:
    for line in doc.splitlines():
        if line.startswith('|') and line.split('|')[1].strip() == f'`{row_id}`':
            return [c.strip() for c in line.strip().strip('|').split('|')]
    return None


def window_label(row: dict) -> str:
    return f"{row['year']}-{row['month'] + 1:02d}" if row['month'] is not None else str(row['year'])


def doc_problems(data: dict, doc: str, reach: list[dict]) -> list[str]:
    problems = []
    registry = {k: v for k, v in data['source_registry'].items() if not k.startswith('_')}
    for row in data['rows']:
        cells = table_cells(doc, row['id'])
        if cells is None or len(cells) < 8:
            problems.append(f"{row['id']}: no row in the document's table of rows")
            continue
        for index, label, want in ((1, 'province', str(row['province_id'])), (2, 'window', window_label(row)),
                                   (3, 'late_until', str(row['late_until'])), (4, 'kind', f"`{row['kind']}`"),
                                   (5, 'fact date', row['fact_date'])):
            if want not in cells[index]:
                problems.append(f"{row['id']}: document says {cells[index]!r} for {label}, the table says {want!r}")
        for source in row['sources']:
            if source not in cells[6]:
                problems.append(f"{row['id']}: document does not list source {source}")
        if row['requires_row'] and row['requires_row'] not in cells[7]:
            problems.append(f"{row['id']}: document does not name its prerequisite {row['requires_row']}")
    for key, url in registry.items():
        if url not in doc:
            problems.append(f'document does not print the URL of source {key}')
    for item in data['not_modelled']:
        if item['seat'] not in doc:
            problems.append(f"document does not list the seat not modelled: {item['seat']}")
    for entry in reach:
        line = next((l for l in doc.splitlines() if l.startswith('|') and l.split('|')[1].strip() == f"`{entry['id']}` (досяжність)"), None)
        if line is None:
            problems.append(f"{entry['id']}: no line in the document's reachability table")
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        got = (cells[1], cells[2], cells[3], cells[4])
        want = (entry['owner'], entry['owner_religion'], entry['province_religion'], f"`{entry['verdict']}`")
        if entry['verdict'] != 'unknown' and got != want:
            problems.append(f"{entry['id']}: reachability table says {got}, the histories give {want}")
        if entry['verdict'] == 'unreachable' and 'unlock' not in entry:
            problems.append(f"{entry['id']}: unreachable in default history without a stated unlock")
    for heading in ('Як працює один рядок', 'Як додати рядок', 'Що не змодельовано', 'Ужгородськ', 'Єпархіальн'):
        if heading not in doc:
            problems.append(f'document lacks the part about: {heading}')
    return problems


# ---------------------------------------------------------------------------
# 6. Reachability from the province and country histories
# ---------------------------------------------------------------------------


def dated_blocks(text: str):
    """(text before the first dated block, [(date, body)] sorted by date)."""
    masked = re.sub(r'#[^\n]*', lambda m: ' ' * len(m.group(0)), text)
    blocks = []
    for match in re.finditer(r'(?m)^(\d{3,4})\.(\d{1,2})\.(\d{1,2})\s*=\s*\{', masked):
        opening = text.index('{', match.start())
        body = text[opening + 1:matching_brace(text, opening)]
        blocks.append(((int(match.group(1)), int(match.group(2)), int(match.group(3))), body))
    first = re.search(r'(?m)^\d{3,4}\.\d{1,2}\.\d{1,2}\s*=', masked)
    head = text[:first.start()] if first else text
    return head, sorted(blocks, key=lambda item: item[0])


def value_at(text: str, key: str, when: tuple[int, int, int]):
    head, blocks = dated_blocks(text)
    match = re.search(rf'(?m)^{key}\s*=\s*"?([A-Za-z0-9_]+)"?', head)
    value = match.group(1) if match else None
    for date, body in blocks:
        if date <= when:
            hit = re.findall(rf'(?m)^\s*{key}\s*=\s*"?([A-Za-z0-9_]+)"?', body)
            if hit:
                value = hit[-1]
    return value


def country_history_text(tag: str) -> str | None:
    for base in (ROOT, vanilla_root()):
        if base is None:
            continue
        hits = sorted((base / 'history/countries').glob(f'{tag} - *.txt'))
        if hits:
            return hits[0].read_text(encoding='cp1252', errors='replace')
    return None


def window_dates(row: dict) -> list[tuple[int, int, int]]:
    if row['month'] is None:
        return [(row['year'], 1, 1), (row['year'], 7, 1), (row['year'], 12, 31)]
    m = row['month'] + 1
    return [(row['year'], m, 1), (row['year'], m, 15), (row['year'], m, 28)]


def reachability(data: dict) -> list[dict]:
    """One entry per row: who owns the seat in the window, what they and the province believe."""
    table = []
    direct = {}
    for row in sorted(data['rows'], key=gen.row_key):
        path = province_history_path(row['province_id'])
        entry = {'id': row['id'], 'province': row['province_id'], 'kind': row['kind'],
                 'window': window_label(row), 'requires': row['requires_row']}
        if path is None:
            entry.update(owner='?', owner_religion='?', province_religion='?', verdict='unknown')
            table.append(entry)
            continue
        text = path.read_text(encoding='cp1252', errors='replace')
        owners, provinces, faiths, unknown = [], [], [], False
        for date in window_dates(row):
            owner = value_at(text, 'owner', date)
            owners.append(owner)
            provinces.append(value_at(text, 'religion', date))
            country = country_history_text(owner) if owner else None
            if country is None:
                unknown = True
                faiths.append('?')
            else:
                faiths.append(value_at(country, 'religion', date))
        unique = lambda seq: '/'.join(dict.fromkeys(seq))  # noqa: E731
        entry.update(owner=unique(owners), owner_religion=unique(faiths), province_religion=unique(provinces))
        if unknown:
            entry['verdict'] = 'unknown'
        else:
            catholic = all(f == 'catholic' for f in faiths)
            want = {'union_convert': 'orthodox', 'union_modifier_only': 'catholic', 'development': None}[row['kind']]
            if row['kind'] == 'development':
                ok = catholic and row['requires_row'] in direct
                entry['verdict'] = 'chain' if ok else 'unreachable'
            else:
                ok = catholic and all(p == want for p in provinces)
                entry['verdict'] = 'direct' if ok else 'unreachable'
            if entry['verdict'] == 'direct':
                direct[row['id']] = entry
        if entry['verdict'] == 'unreachable' and row.get('unlock'):
            entry['unlock'] = row['unlock']
        table.append(entry)
    order = {r['id']: i for i, r in enumerate(data['rows'])}
    return sorted(table, key=lambda e: order[e['id']])


def reachability_problems(table: list[dict]) -> list[str]:
    problems = []
    for entry in table:
        if entry['verdict'] == 'unreachable' and not entry.get('unlock'):
            problems.append(f"{entry['id']}: owner {entry['owner']} ({entry['owner_religion']}) and a {entry['province_religion']} "
                            f"province at {entry['window']} can never satisfy it in default history, and the row states no unlock")
    return problems


def print_reachability(table: list[dict]):
    print('Reachability in default history (owner and faiths sampled at the start, middle and end of each window):')
    print(f"  {'row':42} {'prov':5} {'window':8} {'owner':6} {'owner faith':12} {'province faith':15} verdict")
    for e in table:
        print(f"  {e['id']:42} {e['province']:<5} {e['window']:8} {e['owner']:6} {e['owner_religion']:12} {e['province_religion']:15} {e['verdict']}"
              + (f" (needs {e['requires']} accepted)" if e['verdict'] == 'chain' else ''))


# ---------------------------------------------------------------------------
# Planted violations: every finder must complain about a deliberately broken copy
# ---------------------------------------------------------------------------


def planted(data: dict, files: dict[str, str], definitions, doc: str, loc_keys: set[str]) -> list[tuple[str, list[str]]]:
    triggers, events, loc = files['triggers'], files['events'], files['loc']
    first = data['rows'][0]
    ids = gen.event_ids(data, first)
    n = gen.names(first)
    visible_id = ids['visible']

    def mutate_data(edit):
        clone = copy.deepcopy(data)
        edit(clone)
        return clone

    def replace_once(text, old, new):
        assert old in text, old
        return text.replace(old, new, 1)

    def visible_block(text):
        return event_blocks(text)[visible_id]

    cases = []

    def case(name, problems):
        cases.append((name, list(problems)))

    # Windows.
    case('date window loses its upper month bound',
         window_problems(data, replace_once(triggers, f'\tis_month = {first["month"]}\n\tNOT = {{ is_month = {first["month"] + 1} }}',
                                            f'\tis_month = {first["month"]}')))
    case('date window loses its upper year bound',
         window_problems(data, replace_once(triggers, f'\tNOT = {{ is_year = {first["year"] + 1} }}\n\tis_month', '\tis_month')))
    case('late window reopens the month itself',
         window_problems(data, replace_once(triggers, f'AND = {{ is_year = {first["year"]} is_month = {first["month"] + 1} }}',
                                            f'AND = {{ is_year = {first["year"]} is_month = {first["month"]} }}')))
    case('late window never closes',
         window_problems(data, replace_once(triggers, f'\tNOT = {{ is_year = {first["late_until"] + 1} }}\n}}', '}')))
    case('window uses = as if it were equality (December-style off by one)',
         window_problems(data, replace_once(triggers, f'is_month = {first["month"]}\n', f'is_month = {first["month"] + 1}\n')))
    # Events.
    case('visible event gains mean_time_to_happen',
         event_problems(data, events.replace(visible_block(events), replace_once(
             visible_block(events), 'is_triggered_only = yes', 'is_triggered_only = yes\n\tmean_time_to_happen = { days = 1 }')), triggers, loc_keys))
    case('the answered flag is never set',
         event_problems(data, events.replace(visible_block(events), replace_once(
             visible_block(events), f'\timmediate = {{\n\t\tset_province_flag = {n["answered"]}\n\t}}\n', '')), triggers, loc_keys))
    case('dated starter forgets its scheduled guard',
         event_problems(data, replace_once(events, f'\t\tNOT = {{ has_province_flag = {n["scheduled"]} }}\n\t\t{n["possible"]} = yes\n\t}}\n\tmean_time_to_happen = {{ days = 1 }}',
                       f'\t\t{n["possible"]} = yes\n\t}}\n\tmean_time_to_happen = {{ days = 1 }}'), triggers, loc_keys))
    case('a hidden starter has no option',
         event_problems(data, replace_once(events, f'\t\tset_province_flag = {n["scheduled"]}\n\t\tprovince_event = {{ id = {visible_id} days = 10 }}\n\t}}\n\toption = {{ }}\n',
                       f'\t\tset_province_flag = {n["scheduled"]}\n\t\tprovince_event = {{ id = {visible_id} days = 10 }}\n\t}}\n'), triggers, loc_keys))
    case('the dated starter loses fire_only_once',
         event_problems(data, replace_once(events, f'\tid = {ids["dated"]}\n\thidden = yes\n\tfire_only_once = yes\n', f'\tid = {ids["dated"]}\n\thidden = yes\n'), triggers, loc_keys))
    case('an else_if slips into an option',
         event_problems(data, replace_once(events, '\t\tif = {\n\t\t\tlimit', '\t\telse_if = {\n\t\t\tlimit'), triggers, loc_keys))
    case('an add_opinion appears',
         event_problems(data, replace_once(events, 'set_province_flag = rip_du_approached', 'add_opinion = { who = ROOT modifier = x }\n\t\t\tset_province_flag = rip_du_approached'), triggers, loc_keys))
    case('a patron flag shortcut appears',
         event_problems(data, replace_once(events, 'set_province_flag = rip_du_approached', 'set_province_flag = rip_du_approached\n\t\t\towner = { set_country_flag = rip_church_supports_union }'), triggers, loc_keys))
    case('a flag is set that nothing reads',
         event_problems(data, replace_once(events, f'set_province_flag = {n["answered"]}', f'set_province_flag = {n["answered"]}\n\t\tset_province_flag = rip_eparchy_orphan'), triggers, loc_keys))
    case('refusal stops adding the resistance modifier',
         event_problems(data, replace_once(events, f'add_province_modifier = {{ name = {gen.refusal_modifier(data)} duration = {data["refusal_days"]} }}\n\t\tset_province_flag = {n["refused"]}',
                                           f'set_province_flag = {n["refused"]}'), triggers, loc_keys))
    case('a starter fires an event that does not exist',
         event_problems(data, replace_once(events, f'province_event = {{ id = {visible_id} days = 10 }}', 'province_event = { id = rip_eparchy.99 days = 10 }'), triggers, loc_keys))
    case('a localisation key is missing', event_problems(data, events, triggers, loc_keys - {gen.loc_keys(data, first)['l']}))
    case('a starter spells a date inline',
         event_problems(data, replace_once(events, f'\t\tprovince_id = {first["province_id"]}\n\t\t{n["date_window"]} = yes',
                                           f'\t\tprovince_id = {first["province_id"]}\n\t\tis_year = 1691\n\t\t{n["date_window"]} = yes'), triggers, loc_keys))
    # Modifiers.
    case('a modifier value drifts in the file',
         modifier_problems(data, {**definitions, 'greek_catholic_diocese': {**definitions['greek_catholic_diocese'], 'local_unrest': -2.0}}, events))
    case('a modifier gains a key the text does not mention',
         modifier_problems(data, {**definitions, 'rip_du_rite_guarantee': {**definitions['rip_du_rite_guarantee'], 'local_defensiveness': 0.1}}, events))
    case('a diocese is applied without the guarantee',
         modifier_problems(mutate_data(lambda d: d['rows'][0]['outcome']['modifiers'].__setitem__(
             slice(None), [m for m in d['rows'][0]['outcome']['modifiers'] if m['name'] != 'rip_du_rite_guarantee'])), definitions, events))
    case('the guarantee expires before the diocese',
         modifier_problems(mutate_data(lambda d: d['rows'][0]['outcome']['modifiers'][0].__setitem__('days', 365)), definitions, events))
    # Texts and sources.
    case('an exclamation mark', loc_problems(data, replace_once(loc, 'one dated act.', 'one dated act!')))
    case('an unlisted year in a historical text',
         loc_problems(mutate_data(lambda d: d['rows'][0]['text'].__setitem__('hist', d['rows'][0]['text']['hist'] + ' It happened again in 1733.')), loc))
    case('a banned spelling', loc_problems(data, replace_once(loc, 'Peremyshl see', 'Przemysl see')))
    case('the refusal loses its alternative-history label',
         loc_problems(data, replace_once(loc, f'{gen.loc_keys(data, first)["b"]}:0 "Turn the petition away{data["refusal_label_suffix"]}"',
                                         f'{gen.loc_keys(data, first)["b"]}:0 "Turn the petition away"')))
    case('the late sentence leaks into the dated text',
         loc_problems(data, replace_once(loc, gen.loc_keys(data, first)['d'] + ':0 "', gen.loc_keys(data, first)['d'] + ':0 "' + gen.LATE_TAIL + ' ')))
    case('a source outside the registry',
         source_problems(mutate_data(lambda d: d['rows'][0]['sources'].append('wiki_invented'))))
    case('a registry URL on a host the research never used',
         source_problems(mutate_data(lambda d: d['source_registry'].__setitem__('blog', 'https://example.com/eparchy'))))
    # Document.
    case('the document moves a date',
         doc_problems(data, replace_once(doc, window_label(first), '1690-06'), []))
    case('the document drops a row', doc_problems(data, '\n'.join(l for l in doc.splitlines() if f'`{data["rows"][1]["id"]}`' not in l), []))
    case('the document forgets a seat that is not modelled',
         doc_problems(data, doc.replace(data['not_modelled'][0]['seat'], 'X'), []))
    # Generator table.
    case('a row that mixes kind and outcome', gen.validate(mutate_data(lambda d: d['rows'][2]['outcome'].__setitem__('convert', True))))
    case('a development row with no prerequisite', gen.validate(mutate_data(lambda d: d['rows'][3].__setitem__('requires_row', None))))
    case('a stale generated file', generator_problems(data, {gen.TRIGGERS: triggers.encode('cp1252') + b'#x\r\n',
                                                              gen.EVENTS: events.encode('cp1252'), gen.LOC: ('﻿' + loc).encode('utf-8')}))
    # Reachability.
    fake = [{'id': 'x', 'window': '1700-06', 'owner': 'TUR', 'owner_religion': 'sunni', 'province_religion': 'orthodox',
             'verdict': 'unreachable', 'province': 1}]
    case('a row that can never fire and states no unlock', reachability_problems(fake))
    # Other files leaning on these names.
    case('another file reads a flag the table does not define',
         external_reference_problems(data, {'common/scripted_triggers/x.txt': 'NOT = { has_province_flag = rip_eparchy_lutsk_union_finished }'}))
    case('another file fires an event the table does not define',
         external_reference_problems(data, {'events/x.txt': 'province_event = { id = rip_eparchy.77 }'}))
    return cases


# ---------------------------------------------------------------------------


def main() -> int:
    data = gen.load()
    files = {'triggers': read(gen.TRIGGERS), 'events': read(gen.EVENTS), 'loc': read(gen.LOC)}
    actual = {relative: (ROOT / relative).read_bytes() for relative in (gen.TRIGGERS, gen.EVENTS, gen.LOC)}
    doc = read(DOC) if (ROOT / DOC).exists() else ''
    definitions = modifier_definitions()
    loc_keys = set(re.findall(r'(?m)^ (\S+):0 ', files['loc']))
    table = reachability(data)

    failures = {}

    def record(name, problems):
        if problems:
            failures[name] = problems

    record('generator and table', generator_problems(data, actual))
    if not failures:
        check = subprocess.run([sys.executable, '-B', 'tools/build_eparchy_timeline.py', '--check'],
                               cwd=ROOT, capture_output=True, text=True)
        if check.returncode:
            record('generator --check', [check.stdout.strip() or check.stderr.strip()])
    record('date windows', window_problems(data, files['triggers']) + edge_window_problems(data))
    record('events', event_problems(data, files['events'], files['triggers'], loc_keys))
    record('modifiers', modifier_problems(data, definitions, files['events']))
    record('references', reference_problems(data, files['events']))
    corpus = other_files_corpus()
    record('external references', external_reference_problems(data, corpus))
    record('localisation', loc_problems(data, files['loc']))
    record('sources', source_problems(data))
    record('document', doc_problems(data, doc, table) if doc else [f'{DOC} is missing'])
    record('reachability', reachability_problems(table))
    if not failures:
        results = planted(data, files, definitions, doc, loc_keys)
        missed = [name for name, found in results if not found]
        if "--show-planted" in sys.argv:
            for name, found in results:
                print(f"  planted: {name} -> {found[0][:150]}")
        record('planted violations', [f'not caught: {name}' for name in missed])
    if failures:
        print('EPARCHY TIMELINE FAIL')
        for name, problems in failures.items():
            for problem in problems:
                print(f'  {name}: {problem}')
        return 1
    print_reachability(table)
    skipped = []
    if vanilla_root() is None:
        skipped.append('vanilla country histories (EU4_DIR unset: reachability verdicts are unknown)')
    if not os.environ.get(HISTORY_JSON_ENV):
        skipped.append(f'source cross-check against history_research.json (set {HISTORY_JSON_ENV})')
    print(f"EPARCHY TIMELINE PASS: {len(data['rows'])} rows, generator current, {len(results)} planted violations caught, "
          f"windows proved over {(1822 - 1444) * 12} year-months per window.")
    if skipped:
        print('SKIP: ' + '; '.join(skipped))
    print('LIMIT: static contract; starter timing, the reconversion of a Greek Catholic seat by Latin missionaries between rows, and '
          'the engine effect of the modifiers are not certified by this check.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
