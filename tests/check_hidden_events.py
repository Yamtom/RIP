"""Every event the game loads has a title, a desc, a picture and an option - hidden ones too.

EU4 1.37.5 checks each loaded event in eventmanager.cpp and writes error.log lines
"... is missing a title", "... is missing a desc", "... is missing picture" and
"... has no options" for the keys it does not find. `hidden = yes` does NOT switch these
checks off. The vanilla shape of an event nobody sees is `title = none`, `desc = none`,
`picture = none` and at least one `option` (an empty `option = { }` is enough):
all 68 hidden events of vanilla 1.37.5 carry the four keys, and so does every one of its
6366 events (the run re-measures this when the game is installed; a vanilla surprise only warns).

Measured 2026-10-19 in the real game: twelve RIP events without the shape wrote 37 lines at
every start (rip_eparchy.101-105 and .201-205 were generated, rip_uzh_union.10, rip_rg.900);
`rip_ro_authority.1` wrote four more. Adding the keys removed exactly those lines.
See docs/HIDDEN_EVENT_SHAPE.uk.md.

What this reads: every `*_event = { ... }` block at the top level of events/**/*.txt, with a
small scanner that understands comments, quoted strings and nested blocks, so a `title` that
sits inside an `option`, a commented-out `# title = none` or a `hidden = yes` inside
`define_heir` is not mistaken for an event-level key. Only the keys DIRECTLY inside the
event count. The rule covers visible events as well (they all comply today), because the
engine checks them the same way.

Usage:
    python tests/check_hidden_events.py                 scan the mod and re-measure the rule on the installed game
    python tests/check_hidden_events.py --root DIR      scan DIR/events instead (an extracted commit: A/B)
    python tests/check_hidden_events.py --no-vanilla    skip the re-measurement on the installed game

Exit 1 when an event lacks a key or a self-test is blind; 2 when the events folder is missing.

LIMIT: a static contract on the script text. It cannot see an event the engine builds in
another way, and it does not run EU4; the error.log result rests on the A/B runs recorded in
diagnostics/hidden_event_shape_20261019/.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from clausewitz_testlib import ROOT, vanilla_root

REQUIRED = ('title', 'desc', 'picture', 'option')
# Keys whose value must be a block to count (`option = yes` is not an option).
BLOCK_KEYS = ('option',)

TOKEN = re.compile(r'#[^\n]*|"(?:[^"\\\n]|\\.)*"?|[=<>]=?|!=|\?=|[{}]|[^\s={}<>"#]+')
OPERATORS = frozenset(('=', '==', '<', '>', '<=', '>=', '!=', '?='))

FIX_HINT = ('Fix: give the event the vanilla hidden-event shape - `title = none`, `desc = none`, `picture = none` '
            'right after `id`, and an `option = { }` (a model: events/RIP_OrthodoxAuthority.txt). EU4 writes "is missing a '
            'title / desc / picture" and "has no options" to error.log for every event without these keys, hidden or not.')


class ScriptError(ValueError):
    """The text cannot be split into balanced blocks."""


@dataclass
class Event:
    kind: str
    id: str | None
    hidden: bool
    keys: set[str]                       # keys directly inside the event
    block_keys: set[str]                 # those among them whose value is a { block }
    start: int                           # offset of the `*_event` word
    end: int                             # offset just after the closing brace
    spans: dict[str, list[tuple[int, int]]] = field(default_factory=dict)   # only with spans=True

    def missing(self) -> list[str]:
        return [key for key in REQUIRED
                if key not in (self.block_keys if key in BLOCK_KEYS else self.keys)]


def scan_text(text: str, spans: bool = False) -> list[Event]:
    """The top-level `*_event = { }` blocks of one file and the keys directly inside each.

    A single pass over the tokens. Only two levels matter: depth 0 (a word, `=`, then `{` opens an
    event when the word ends in `_event`) and depth 1 inside an event (the event's own keys). Everything
    deeper, and every other top-level block, is skipped by counting braces. Raises ScriptError on
    unbalanced braces.
    """
    events: list[Event] = []
    depth = 0
    event: Event | None = None
    pending: str | None = None            # last word/string seen at a level that matters
    pending_at = 0
    operator_seen = False
    open_key: str | None = None            # key whose block is open at depth 2 (for spans)
    open_start = 0
    last_event_open = 0

    def note_key(key: str, is_block: bool, begin: int, end: int, value: str | None) -> None:
        assert event is not None
        key = key.strip('"')
        event.keys.add(key)
        if is_block:
            event.block_keys.add(key)
        if key == 'hidden' and value is not None and value.strip('"') == 'yes':
            event.hidden = True
        elif key == 'id' and value is not None and event.id is None:
            event.id = value.strip('"')
        if spans and end >= 0:
            event.spans.setdefault(key, []).append((begin, end))

    for match in TOKEN.finditer(text):
        token = match.group()
        first = token[0]
        if first == '#':
            continue
        if first == '{':
            depth += 1
            if depth == 1:
                if pending is not None and operator_seen and pending.endswith('_event'):
                    event = Event(kind=pending, id=None, hidden=False, keys=set(), block_keys=set(),
                                  start=pending_at, end=-1)
                    last_event_open = pending_at
            elif depth == 2 and event is not None and pending is not None and operator_seen:
                note_key(pending, True, pending_at, -1, None)
                open_key, open_start = pending.strip('"'), pending_at
            pending, operator_seen = None, False
            continue
        if first == '}':
            depth -= 1
            if depth < 0:
                raise ScriptError(f'unexpected closing brace at offset {match.start()}')
            if depth == 1 and event is not None and open_key is not None:
                if spans:
                    event.spans.setdefault(open_key, []).append((open_start, match.end()))
                open_key = None
            if depth == 0 and event is not None:
                event.end = match.end()
                events.append(event)
                event = None
            pending, operator_seen = None, False
            continue
        if token in OPERATORS:
            if pending is not None:
                operator_seen = True
            continue
        # a word or a quoted string
        if depth == 0 or (depth == 1 and event is not None):
            if pending is not None and operator_seen:
                if depth == 1:
                    note_key(pending, False, pending_at, match.end(), token)
                pending, operator_seen = None, False
            else:
                pending, pending_at, operator_seen = token, match.start(), False
    if depth:
        where = f' (the last event opened at offset {last_event_open})' if event is not None else ''
        raise ScriptError(f'{depth} unclosed block(s) at the end of the text{where}')
    return events


def read_script(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252', errors='replace')


def line_of(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


@dataclass
class Problem:
    path: str
    line: int
    event: Event

    def render(self, generators: dict[str, str]) -> str:
        shape = f"{self.event.kind}{', hidden' if self.event.hidden else ''}"
        gen = generators.get(self.path)
        return (f"  {self.path}:{self.line} {self.event.id or '<no id>'} ({shape}): missing "
                + ', '.join(self.event.missing()) + (f'  [generated by {gen}: fix the generator]' if gen else ''))


def scan_folder(folder: Path, label_root: Path) -> tuple[list[Problem], dict[str, int], list[str]]:
    """(problems, counts, parse errors) for every .txt file under `folder`."""
    problems: list[Problem] = []
    errors: list[str] = []
    counts = {'files': 0, 'events': 0, 'hidden': 0}
    for path in sorted(folder.rglob('*.txt')):
        label = path.relative_to(label_root).as_posix()
        text = read_script(path)
        counts['files'] += 1
        try:
            events = scan_text(text)
        except ScriptError as error:
            errors.append(f'  {label}: {error}')
            continue
        counts['events'] += len(events)
        for event in events:
            counts['hidden'] += event.hidden
            if event.missing():
                problems.append(Problem(label, line_of(text, event.start), event))
    return problems, counts, errors


def generators_of(paths: set[str], root: Path) -> dict[str, str]:
    """For each path, the tools/*.py script that names it (a generated file is fixed in its generator)."""
    found: dict[str, str] = {}
    scripts = sorted((root / 'tools').glob('*.py')) if (root / 'tools').is_dir() else []
    corpus = {script.name: read_script(script) for script in scripts} if paths else {}
    for path in paths:
        for name, text in corpus.items():
            if path in text:
                found[path] = f'tools/{name}'
                break
    return found


# ---------------------------------------------------------------------------
# Self-tests: the scanner must see what the engine sees
# ---------------------------------------------------------------------------

SHAPE = '\ttitle = none\n\tdesc = none\n\tpicture = none\n'
GOOD = ('country_event = {\n\tid = t.1\n' + SHAPE
        + '\thidden = yes\n\tis_triggered_only = yes\n\timmediate = { clr_country_flag = x }\n\toption = { }\n}\n')
# The shape of each RIP event that wrote error.log lines: no title/desc/picture, an option or not.
PROVINCE_STARTER = ('province_event = {\n\tid = t.2\n\thidden = yes\n\tfire_only_once = yes\n\ttrigger = { province_id = 1 }\n'
                    '\tmean_time_to_happen = { days = 1 }\n\timmediate = { set_province_flag = x }\n\toption = { }\n}\n')
BARE_TRIGGERED = ('country_event = {\n\tid = t.3\n\thidden = yes\n\tis_triggered_only = yes\n'
                  '\timmediate = { rip_rg_grain_refresh_effect = yes }\n}\n')
VISIBLE_OK = ('country_event = {\n\tid = t.4\n\ttitle = t.4.t\n\tdesc = t.4.d\n\tpicture = RELIGION_eventPicture\n'
              '\tis_triggered_only = yes\n\toption = { name = t.4.a }\n}\n')
VISIBLE_NO_PICTURE = VISIBLE_OK.replace('\tpicture = RELIGION_eventPicture\n', '').replace('t.4', 't.5')

PITFALLS = [
    # (name, text, {event id: expected missing keys})
    ('vanilla hidden shape passes', GOOD, {'t.1': []}),
    ('a visible event with all four passes', VISIBLE_OK, {'t.4': []}),
    ('hidden province starter without title, desc, picture (rip_uzh_union.10, rip_eparchy.*)', PROVINCE_STARTER,
     {'t.2': ['title', 'desc', 'picture']}),
    ('hidden event with nothing but immediate (rip_rg.900)', BARE_TRIGGERED,
     {'t.3': ['title', 'desc', 'picture', 'option']}),
    ('a visible event without a picture is caught too', VISIBLE_NO_PICTURE, {'t.5': ['picture']}),
    ('no title', GOOD.replace('\ttitle = none\n', ''), {'t.1': ['title']}),
    ('no desc', GOOD.replace('\tdesc = none\n', ''), {'t.1': ['desc']}),
    ('no picture', GOOD.replace('\tpicture = none\n', ''), {'t.1': ['picture']}),
    ('no option', GOOD.replace('\toption = { }\n', ''), {'t.1': ['option']}),
    ('option = yes is not an option', GOOD.replace('\toption = { }\n', '\toption = yes\n'), {'t.1': ['option']}),
    ('one of several options is enough', GOOD.replace('\toption = { }\n', '\toption = { name = a }\n\toption = { name = b }\n'),
     {'t.1': []}),
    ('a commented-out title does not count', GOOD.replace('\ttitle = none\n', '\t# title = none\n'), {'t.1': ['title']}),
    ('a trailing comment does not hide a key', GOOD.replace('\ttitle = none\n', '\ttitle = none # kept\n'), {'t.1': []}),
    ('keys inside nested blocks do not count',
     GOOD.replace(SHAPE, '').replace('\toption = { }\n',
                                     '\toption = { name = a title = none desc = none picture = none }\n'
                                     '\timmediate2 = { hidden_effect = { title = none desc = none picture = none option = { } } }\n'),
     {'t.1': ['title', 'desc', 'picture']}),
    ('braces and equals inside a quoted string do not unbalance the scan',
     GOOD.replace('desc = none', 'desc = "a { b = c } # d"'), {'t.1': []}),
    ('a desc made of trigger blocks counts as a desc',
     GOOD.replace('\tdesc = none\n', '\tdesc = { trigger = { always = yes } desc = x.d }\n\tdesc = { trigger = { always = no } desc = x.e }\n'),
     {'t.1': []}),
    ('a hidden = yes nested in an effect does not make a visible event hidden',
     VISIBLE_OK.replace('option = { name = t.4.a }', 'option = { name = t.4.a define_heir = { hidden = yes } }'), {'t.4': []}),
    ('two events in one file are judged one by one',
     'namespace = t\n' + GOOD + '# a comment between events\n' + BARE_TRIGGERED, {'t.1': [], 't.3': ['title', 'desc', 'picture', 'option']}),
    ('top-level blocks that are not events are ignored',
     'namespace = t\nsomething = { title = none }\n' + VISIBLE_OK, {'t.4': []}),
    ('the file may start with the event', GOOD, {'t.1': []}),
    ('compact spacing', 'country_event={id=t.6 title=none desc=none picture=none hidden=yes option={}}', {'t.6': []}),
    ('compact spacing, keys missing', 'country_event={id=t.7 hidden=yes option={}}', {'t.7': ['title', 'desc', 'picture']}),
]

HIDDEN_FLAG_CASES = [
    ('hidden = yes is read', GOOD, {'t.1': True}),
    ('hidden = no is not hidden', GOOD.replace('hidden = yes', 'hidden = no'), {'t.1': False}),
    ('nested hidden = yes is not event-level',
     VISIBLE_OK.replace('option = { name = t.4.a }', 'option = { name = t.4.a define_heir = { hidden = yes } }'), {'t.4': False}),
    ('a province_event is an event too', PROVINCE_STARTER, {'t.2': True}),
]

BROKEN = [
    ('an unclosed event', GOOD[:-2]),
    ('an unclosed nested block', GOOD.replace('immediate = { clr_country_flag = x }', 'immediate = { clr_country_flag = x')),
    ('a stray closing brace', GOOD + '}\n'),
]


def self_test_problems() -> list[str]:
    problems: list[str] = []
    for name, text, expected in PITFALLS:
        try:
            found = {event.id: event.missing() for event in scan_text(text)}
        except ScriptError as error:
            problems.append(f'self-test {name!r}: scanner error {error}')
            continue
        if found != expected:
            problems.append(f'self-test {name!r}: got {found}, expected {expected}')
    for name, text, expected in HIDDEN_FLAG_CASES:
        found = {event.id: event.hidden for event in scan_text(text)}
        if found != expected:
            problems.append(f'self-test {name!r}: got {found}, expected {expected}')
    for name, text in BROKEN:
        try:
            scan_text(text)
        except ScriptError:
            continue
        problems.append(f'self-test {name!r}: unbalanced text was accepted')
    return problems


def planted_problems(folder: Path) -> tuple[list[str], int]:
    """Delete each required key from every compliant HIDDEN event of the real files, one key at a time,
    and require the scanner to name exactly that key. Proves the scan sees the real syntax of the mod."""
    problems: list[str] = []
    planted = 0
    for path in sorted(folder.rglob('*.txt')):
        text = read_script(path)
        try:
            events = scan_text(text)
        except ScriptError:
            continue
        for event in events:
            if not event.hidden or event.missing():
                continue
            snippet = text[event.start:event.end]
            whole = scan_text(snippet, spans=True)
            label = f'{path.name}: {event.id}'
            if len(whole) != 1 or whole[0].missing():
                problems.append(f'planted {label}: the event does not scan alone')
                continue
            for key in REQUIRED:
                mutated = snippet
                for begin, end in sorted(whole[0].spans.get(key, []), reverse=True):
                    mutated = mutated[:begin] + mutated[end:]
                result = scan_text(mutated)
                planted += 1
                if len(result) != 1 or result[0].missing() != [key]:
                    problems.append(f'planted {label} without {key}: '
                                    f'{result[0].missing() if len(result) == 1 else "no single event"} reported')
    return problems, planted


# ---------------------------------------------------------------------------


def vanilla_measure() -> str:
    """Re-measure the rule on the installed game. One line; never fatal (the engine log is the ground truth)."""
    root = vanilla_root()
    if root is None:
        return ('SKIP vanilla: no installed EU4 matching the mod (set EU4_DIR); the rule was measured on 1.37.5 '
                '(6366 events, 68 hidden, none without the four keys)')
    problems, counts, errors = scan_folder(root / 'events', root)
    if errors:
        return 'WARN vanilla: ' + '; '.join(errors)
    if problems:
        sample = ', '.join(f"{p.event.id}:{'/'.join(p.event.missing())}" for p in problems[:5])
        return (f"WARN vanilla: {len(problems)} of {counts['events']} vanilla events lack a key ({sample}); "
                'the premise changed - re-measure error.log before trusting this rule')
    return (f"VANILLA: {counts['events']} events in {counts['files']} files, {counts['hidden']} hidden, "
            'every one has title, desc, picture and an option')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='tree whose events/ folder is scanned (default: this mod)')
    parser.add_argument('--no-vanilla', action='store_true', help='skip the re-measurement of the rule on the installed game')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    folder = root / 'events'
    if not folder.is_dir():
        print(f'HIDDEN EVENT SHAPE ERROR: {folder} is not a folder')
        return 2

    # The scanner must be right before its verdict on the mod means anything.
    blind = self_test_problems()
    planted_failures, planted = planted_problems(folder)
    blind += planted_failures
    if blind:
        print('HIDDEN EVENT SHAPE FAIL: the scanner itself is wrong')
        for failure in blind:
            print('  ' + failure)
        return 1

    problems, counts, errors = scan_folder(folder, root)
    if errors:
        print('HIDDEN EVENT SHAPE FAIL: events do not parse')
        for error in errors:
            print(error)
        return 1
    if problems:
        generators = generators_of({p.path for p in problems}, root)
        print(f"HIDDEN EVENT SHAPE FAIL: {len(problems)} of {counts['events']} events lack a key EU4 checks "
              f"({sum(p.event.hidden for p in problems)} hidden)")
        for problem in problems:
            print(problem.render(generators))
        print(FIX_HINT)
        return 1

    n_self = len(PITFALLS) + len(HIDDEN_FLAG_CASES) + len(BROKEN)
    print(f"HIDDEN EVENT SHAPE PASS: {counts['events']} events in {counts['files']} files "
          f"({counts['hidden']} hidden), each has title, desc, picture and an option; "
          f'{n_self} scanner self-tests and {planted} planted deletions caught.')
    if not args.no_vanilla:
        print(vanilla_measure())
    fixtures = ROOT / 'tests' / 'dev_tools'
    if fixtures.is_dir():
        advice, fixture_counts, fixture_errors = scan_folder(fixtures, ROOT)
        if advice or fixture_errors:
            print(f"NOTE tests/dev_tools: {len(advice)} of {fixture_counts['events']} fixture events lack a key; they are not "
                  'shipped, but copied into a harness mod they add error.log lines:')
            for problem in advice:
                print(problem.render({}))
            for error in fixture_errors:
                print(error)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except OSError as error:
        # e.g. a --root deeper than the 260 characters Windows opens by default
        print(f'HIDDEN EVENT SHAPE ERROR: cannot read {error.filename} ({error.strerror}); '
              'on Windows a path over 260 characters needs a shorter --root')
        sys.exit(2)
