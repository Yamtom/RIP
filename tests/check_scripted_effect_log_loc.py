"""A `log = "..."` string inside common/scripted_effects must not contain `[`.

EU4 1.37.5 works on the scripted loc of a `log` string (`[Root.GetName]`, `[This.GetName]`, ...) while it
loads the scripted effects, and does not survive it: eu4.exe dies with EXCEPTION_STACK_OVERFLOW (C00000FD) in the
"Loading Databases" stage, a few seconds after the last `common/event_modifiers` line of error.log - or the
window sits on "Loading Databases..." for minutes, or the process exits with code 1. The game never reaches
the main menu, and no other check of this repository can see it: the text is valid script. (Why: most likely
a scripted effect has no scope when it is loaded and the evaluation recurses without end - an inference, the
crash itself is what was measured.)

Measured 2026-10-22 on EU4 1.37.5 (isolated userdir, game started from the session, paused load):
- origin/main 439e67b4 did not load. The only `log = "...[...]"` strings in common/ were six lines in
  common/scripted_effects/rip_frontier_expedition_effects.txt (generator tools/build_frontier_design.py);
  the same tree with only those tokens removed loaded in 66 s.
- A probe mod holding one scripted-effects file with `log = "RIP_PROBE SE begin [Root.GetTag]"` crashed the
  same way, even though nothing called the effect; the same file with plain text loaded.
- The same string in the `log` of an event, a decision or a government-mechanic effect loads fine (a scope
  exists there), which is why only scripted effects are guarded.
The exact trigger inside the class is not pinned down: the author's earlier A/B of the frontier file
(docs/DESIGN_DECISIONS_AND_RUNTIME_QA_20261021.uk.md) reached the game screen with the first two blocks - the
second one logs from inside a `random_province` block - and overflowed once `rip_frontier_crimea_purchase_effect`
(log in the country scope) was added. So the guard bans the whole class, not only the country-scope form.

What this reads: every `log = "..."` pair in common/scripted_effects/**/*.txt, with a small scanner that
understands comments and quoted strings (a comment may carry a bracket, a string may carry `#`, `{`, `=` or an
escaped quote, and a string may run over lines). Only the key `log` counts.

Usage:
    python tests/check_scripted_effect_log_loc.py               scan this mod
    python tests/check_scripted_effect_log_loc.py --root DIR    scan DIR/common/scripted_effects instead (an extracted commit: A/B)

Exit 1 when a log string carries `[`, a file does not scan, or a self-test is blind; 2 when the folder is missing.

LIMIT: a static contract on the script text. It does not run EU4 and does not look at other folders of common/
(on_actions, government_reforms, disasters, ... are unmeasured), at other string-valued effects, or at text
that reaches a log through a `$PARAM$` of a scripted effect. The crash itself rests on the A/B runs above.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from clausewitz_testlib import ROOT

# comment | quoted string (a string may run over lines; `close` is missing when it never ends) | = { } | any other word
TOKEN = re.compile(r'(?P<comment>#[^\n]*)|"(?P<body>(?:[^"\\]|\\.)*)(?P<close>")?|(?P<op>[={}])|(?P<word>[^\s={}"#]+)',
                   re.DOTALL)

FIX_HINT = ('Fix: write plain text in the log (no [Root.X] / [This.X]), or move the marker into the event, decision or '
            'mechanic effect that calls the scripted effect - there the same string is safe. With scripted loc in the '
            'log of a scripted effect eu4.exe dies with EXCEPTION_STACK_OVERFLOW during "Loading Databases" (measured '
            '2026-10-22 on 1.37.5: origin/main 439e67b4 did not load). A generated file is fixed in its generator.')

PLANT_BLOCK = 'rip_planted_log_loc_effect = {\n\tlog = "PLANTED [Root.GetName]"\n}\n'


class ScriptError(ValueError):
    """The text cannot be scanned (a string that never ends)."""


@dataclass(frozen=True)
class LogString:
    offset: int          # of the opening quote
    body: str

    @property
    def bracketed(self) -> bool:
        return '[' in self.body


def log_strings(text: str) -> list[LogString]:
    """Every `log = "..."` value in the text, with or without a bracket, in file order."""
    found: list[LogString] = []
    last: list[tuple[str, str]] = []            # the two previous tokens that are not comments
    for match in TOKEN.finditer(text):
        if match.group('comment') is not None:
            continue
        if match.group('body') is not None:
            if match.group('close') is None:
                raise ScriptError(f'a string opened at offset {match.start()} never ends')
            if len(last) == 2 and last[1] == ('op', '=') and last[0][0] in ('word', 'string') and last[0][1] == 'log':
                found.append(LogString(match.start(), match.group('body')))
            token = ('string', match.group('body'))
        elif match.group('op') is not None:
            token = ('op', match.group('op'))
        else:
            token = ('word', match.group('word'))
        last = (last + [token])[-2:]
    return found


def bracketed_lines(text: str) -> list[int]:
    return [line_of(text, entry.offset) for entry in log_strings(text) if entry.bracketed]


def line_of(text: str, offset: int) -> int:
    return text.count('\n', 0, offset) + 1


def read_script(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252', errors='replace')


@dataclass
class Problem:
    path: str
    line: int
    source: str

    def render(self, generators: dict[str, str]) -> str:
        gen = generators.get(self.path)
        return f'  {self.path}:{self.line}  {self.source}' + (f'  [generated by {gen}: fix the generator]' if gen else '')


def scan_folder(folder: Path, label_root: Path) -> tuple[list[Problem], dict[str, int], list[str]]:
    """(problems, counts, parse errors) for every .txt file under `folder`."""
    problems: list[Problem] = []
    errors: list[str] = []
    counts = {'files': 0, 'logs': 0}
    for path in sorted(folder.rglob('*.txt')):
        label = path.relative_to(label_root).as_posix()
        text = read_script(path)
        counts['files'] += 1
        try:
            entries = log_strings(text)
        except ScriptError as error:
            errors.append(f'  {label}: {error}')
            continue
        counts['logs'] += len(entries)
        lines = text.splitlines()
        for entry in entries:
            if entry.bracketed:
                line = line_of(text, entry.offset)
                source = lines[line - 1].strip()
                problems.append(Problem(label, line, source if len(source) <= 160 else source[:157] + '...'))
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

CASES = [
    # (name, text, line of each bracketed log string)
    ('plain text passes', 'x = {\n\tlog = "RIP plain text"\n}\n', []),
    ('scripted loc is caught', 'x = {\n\tlog = "A [Root.GetName]"\n}\n', [2]),
    ('the shape that stopped origin/main 439e67b4 from loading',
     'rip_frontier_crimea_one_effect = {\n add_claim = ROOT\n log = "RIP_FRONTIER CLAIM crimea [Root.GetName] [This.GetName]"\n}\n', [3]),
    ('a single Root token is enough (the probe that crashed the load)', 'x = { log = "RIP_PROBE SE begin [Root.GetTag]" }', [1]),
    ('no spaces around the equals sign', 'x = { log="A [Root.GetTag]" }', [1]),
    ('the key, the sign and the string on three lines', 'x = {\n log\n\t=\n\t"A [Root.GetTag]"\n}', [4]),
    ('a bracket after an escaped quote is still inside the string', 'x = { log = "say \\"hi\\" [Root.GetName]" }', [1]),
    ('a commented-out log does not count', 'x = {\n\t# log = "A [Root.GetName]"\n\tlog = "B"\n}\n', []),
    ('a bracket in a trailing comment does not count', 'x = {\n\tlog = "B" # [This.GetName]\n}\n', []),
    ('a quote inside a comment does not open a string', "x = { # it's \"quoted\n log = \"ok\" }\n", []),
    ('# { = inside a string do not confuse the scan', 'x = { log = "a { b = c # d" }\ny = { log = "[Root.GetName]" }\n', [2]),
    ('a string that runs over lines', 'x = {\n\tlog = "first\n second [Root.GetName]"\n}\n', [2]),
    ('every bad string is found, in order', 'x = {\n log = "A [Root.GetName]"\n log = "ok"\n log = "[This.GetName]"\n}\n', [2, 4]),
    ('an empty string passes', 'x = { log = "" }', []),
    ('only the key log counts', 'x = { blog = "A [Root.GetName]" log_text = "[x]" mylog = "[y]" }', []),
    ('a variable named log is not the effect',
     'x = { set_variable = { which = log value = 1 } check_variable = { which = log value = 1 } }', []),
    ('a quoted key still counts', 'x = { "log" = "A [Root.GetName]" }', [1]),
    ('a log string is found inside nested blocks',
     'x = { if = { limit = { tag = RUS } hidden_effect = { log = "[Root.GetName]" } } }', [1]),
    ('the file may start with the log', 'log = "[Root.GetName]"\n', [1]),
]

BROKEN = [
    ('a string that never ends', 'x = { log = "A [Root.GetName] }\n'),
    ('a string ending in an escaped quote', 'x = { log = "A \\" }\n'),
]


def self_test_problems() -> list[str]:
    problems: list[str] = []
    for name, text, expected in CASES:
        try:
            found = bracketed_lines(text)
        except ScriptError as error:
            problems.append(f'self-test {name!r}: scanner error {error}')
            continue
        if found != expected:
            problems.append(f'self-test {name!r}: got lines {found}, expected {expected}')
    for name, text in BROKEN:
        try:
            log_strings(text)
        except ScriptError:
            continue
        problems.append(f'self-test {name!r}: a string that never ends was accepted')
    return problems


def planted_problems(folder: Path) -> tuple[list[str], int]:
    """Plant a bracket into the real files and require the scanner to find exactly that one.

    1. Append a new effect with a bracketed log to the end of every file: it must be the one new hit, on the
       appended line. A scanner that lost sync earlier in the file (a stray quote, an odd escape) would swallow
       the appended text and go blind to the rest of that file - this names the file instead of passing.
    2. Put a bracket into each log string of the file that has none: one new hit per string, on that string's line.
    """
    problems: list[str] = []
    planted = 0
    for path in sorted(folder.rglob('*.txt')):
        text = read_script(path)
        try:
            entries = log_strings(text)
        except ScriptError:
            continue                                   # reported by the scan itself
        before = bracketed_lines(text)
        appended = text.rstrip('\r\n') + '\n' + PLANT_BLOCK
        expected_line = appended.count('\n', 0, appended.rindex('log = "PLANTED')) + 1
        after = bracketed_lines(appended)
        planted += 1
        if after != before + [expected_line]:
            problems.append(f'planted at the end of {path.name}: got lines {after}, expected {before + [expected_line]}')
        for entry in entries:
            if entry.bracketed:
                continue
            mutated = text[:entry.offset + 1] + '[Root.GetName] ' + text[entry.offset + 1:]
            result = bracketed_lines(mutated)
            planted += 1
            if result != sorted(before + [line_of(text, entry.offset)]):
                problems.append(f'planted in {path.name}:{line_of(text, entry.offset)}: got lines {result}')
    return problems, planted


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path, default=ROOT, help='tree whose common/scripted_effects folder is scanned (default: this mod)')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    folder = root / 'common' / 'scripted_effects'
    if not folder.is_dir():
        print(f'SCRIPTED EFFECT LOG LOC ERROR: {folder} is not a folder')
        return 2

    # The scanner must be right before its verdict on the mod means anything.
    blind = self_test_problems()
    planted_failures, planted = planted_problems(folder)
    blind += planted_failures
    if blind:
        print('SCRIPTED EFFECT LOG LOC FAIL: the scanner itself is wrong')
        for failure in blind:
            print('  ' + failure)
        return 1

    problems, counts, errors = scan_folder(folder, root)
    if errors:
        print('SCRIPTED EFFECT LOG LOC FAIL: scripted effects do not scan')
        for error in errors:
            print(error)
        return 1
    if problems:
        generators = generators_of({p.path for p in problems}, root)
        print(f"SCRIPTED EFFECT LOG LOC FAIL: {len(problems)} log string(s) in scripted effects carry scripted loc "
              f"(EU4 1.37.5 does not finish loading)")
        for problem in problems:
            print(problem.render(generators))
        print(FIX_HINT)
        return 1

    print(f"SCRIPTED EFFECT LOG LOC PASS: {counts['logs']} log string(s) in {counts['files']} scripted-effect files, "
          f"none carries a '['; {len(CASES) + len(BROKEN)} scanner self-tests and {planted} planted brackets caught.")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except OSError as error:
        # e.g. a --root deeper than the 260 characters Windows opens by default
        print(f'SCRIPTED EFFECT LOG LOC ERROR: cannot read {error.filename} ({error.strerror}); '
              'on Windows a path over 260 characters needs a shorter --root')
        sys.exit(2)
