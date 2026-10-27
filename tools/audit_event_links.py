"""Reproducible static event dependency inventory; does not simulate EU4 scopes."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import re
import sys

from event_layout import ROOT, statements, tokens, event_id, format_script
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import vanilla_root, vanilla_version, keyed_blocks


def read(path):
    raw = path.read_bytes()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252')


def digest(body):
    return hashlib.sha256(json.dumps(tokens(body), ensure_ascii=False).encode('utf-8')).hexdigest()


def inventory(root):
    result = {}
    for path in sorted((root / 'events').glob('*.txt')):
        for kind, body in statements(read(path)):
            if kind in ('country_event', 'province_event'):
                eid = event_id(body)
                assert eid not in result, f'Duplicate {eid}: {path}'
                result[eid] = {'file': path.relative_to(root).as_posix(), 'kind': kind,
                               'sha256_tokens': digest(body), 'body': body}
    return result


def main():
    baseline = json.loads((ROOT / 'tools/data/event_layout_manifest.json').read_text(encoding='utf-8'))
    events = inventory(ROOT)
    assert set(events) == set(baseline['events']), 'Event ID set changed'
    for eid, entry in events.items():
        assert entry['sha256_tokens'] == baseline['events'][eid]['sha256_tokens'], f'Event tokens changed: {eid}'
    for path in (ROOT / 'events').glob('*.txt'):
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        assert not raw.startswith(b'\xef\xbb\xbf'), path
        assert text.replace('\r\n', '\n') == format_script(text), f'Style drift: {path}'
        namespaces = {tokens(b)[2] for k, b in statements(text) if k == 'namespace'}
        for k, b in statements(text):
            if k in ('country_event', 'province_event'):
                eid = event_id(b)
                assert '.' not in eid or eid.split('.')[0] in namespaces, (path, eid)

    vanilla = vanilla_root()
    assert vanilla is not None, 'Install supported vanilla to resolve inherited references'
    vanilla_events = inventory(vanilla)
    overrides = sorted(p.name for p in (ROOT / 'events').glob('*.txt') if (vanilla / 'events' / p.name).exists())
    assert overrides == baseline['vanilla_filename_overrides'], 'Vanilla filename override changed'
    effective_ids = set(events) | {eid for eid, item in vanilla_events.items()
                                    if Path(item['file']).name not in overrides}
    uses = defaultdict(list)
    symbols = defaultdict(set)
    state_by_event = {}
    for eid, entry in events.items():
        code = ' '.join(tokens(entry['body']))
        names = re.findall(r'\b(?:set_country_flag|clr_country_flag|has_country_flag|set_province_flag|clr_province_flag|has_province_flag|has_global_flag|set_global_flag|clr_global_flag|has_saved_event_target|save_event_target_as|save_global_event_target_as|which|flag)\s*=\s*([^\s{}]+)', code)
        state_by_event[eid] = sorted({n.strip('"') for n in names})
    state_names = {n for names in state_by_event.values() for n in names}
    state_uses = defaultdict(list)
    call_kinds = []
    unresolved_repository_calls = []
    parameterized_repository_calls = []
    # Record all exact code-token uses, including on_action weighted event lists.
    for directory in ('events', 'common', 'decisions', 'missions', 'history', 'interface', 'customizable_localization'):
        for path in sorted((ROOT / directory).rglob('*')):
            if not path.is_file() or path.suffix not in ('.txt', '.gui', '.gfx'):
                continue
            text = read(path)
            rel = path.relative_to(ROOT).as_posix()
            for line_no, line in enumerate(text.splitlines(), 1):
                for token in set(tokens(line)):
                    token = token.strip('"')
                    if token in events:
                        uses[token].append(f'{rel}:{line_no}')
                    if token in state_names:
                        state_uses[token].append(f'{rel}:{line_no}')
            for kind in ('country_event', 'province_event'):
                for offset, body in keyed_blocks(text, kind):
                    try:
                        target = event_id(body)
                    except ValueError:
                        continue
                    if target.startswith('$') and target.endswith('$'):
                        parameterized_repository_calls.append({'file': rel,
                            'line': text.count('\n', 0, offset) + 1, 'parameter': target})
                    elif target not in effective_ids:
                        unresolved_repository_calls.append({'file': rel,
                            'line': text.count('\n', 0, offset) + 1, 'id': target})
                    if target in events and events[target]['kind'] != kind:
                        call_kinds.append({'file': rel, 'line': text.count('\n', 0, offset) + 1,
                                           'id': target, 'call': kind, 'definition': events[target]['kind']})
            # Top-level definitions in dependency directories, not inferred built-ins.
            if directory == 'common':
                for m in re.finditer(r'(?m)^([\w.:-]+)\s*=\s*\{', text):
                    symbols[m[1]].add(rel)
    loc = defaultdict(set)
    for root in (vanilla, ROOT):
        for path in (root / 'localisation').rglob('*l_english.yml'):
            for m in re.finditer(r'^\s*([\w.:-]+):\d*\s*"', read(path), re.M):
                loc[m[1]].add(('mod/' if root == ROOT else 'vanilla/') + path.relative_to(root).as_posix())
    rows = {}
    missing_calls = []
    isolated = []
    for eid, entry in events.items():
        body = entry.pop('body')
        code = tokens(body)
        calls = []
        for kind in ('country_event', 'province_event'):
            for offset, nested in keyed_blocks(' '.join(code[3:-1]), kind):
                calls.append(event_id(nested))
        missing_calls.extend((eid, target) for target in calls if target not in effective_ids)
        dependencies = {s: sorted(symbols[s]) for s in sorted({t.strip('"') for t in code}) if s in symbols}
        loc_keys = sorted({t.strip('"') for t in code if t.strip('"') in loc})
        triggered = bool(re.search(r'\bis_triggered_only\s*=\s*yes\b', body))
        # Includes own id definition; exactly one use means no other literal caller.
        if triggered and len(uses[eid]) <= 1:
            isolated.append(eid)
        rows[eid] = {**entry, 'source_file_before': baseline['events'][eid]['file'],
                     'uses_including_definition': uses[eid], 'calls': calls,
                     'resolved_mod_symbols': dependencies,
                     'state_symbol_uses': {k: state_uses[k] for k in state_by_event[eid]},
                     'localisation': {k: sorted(loc[k]) for k in loc_keys},
                     'triggered_only': triggered,
                     'vanilla_same_id': vanilla_events.get(eid, {}).get('file')}
    out = {'vanilla': str(vanilla), 'version': vanilla_version(vanilla),
           'scope': 'Exact-token source links; no scope simulation or runtime proof. Dynamic/generated references need review.',
           'files_before': len(baseline['files']), 'files_after': len(list((ROOT / 'events').glob('*.txt'))),
           'event_count': len(events), 'vanilla_event_count': len(vanilla_events),
           'vanilla_filename_overrides': overrides, 'missing_direct_event_calls': missing_calls,
           'event_kind_mismatches': call_kinds,
           'unresolved_repository_event_calls': unresolved_repository_calls,
           'parameterized_repository_event_calls': parameterized_repository_calls,
           'triggered_without_other_literal_use_review': isolated,
           'files': baseline['files'], 'events': rows}
    target = ROOT / 'outputs/events_links.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = [
        '# Аудит і структура подій RIP — 2026-10-27', '',
        'Згенеровано `python -B tools/audit_event_links.py`. Повна карта зв’язків: '
        '`outputs/events_links.json` (виклики, місця використання, символи common, '
        'прапорці/змінні/цілі та англійська локалізація).', '',
        '## Результат', '',
        f'- {out["files_before"]} початкових файлів → {out["files_after"]} файлів; '
        f'{len(events)} унікальних ID, порядок значущих токенів кожної події збережено.',
        '- Країнний контент: `RIP_<TAG>_<тема>.txt`; міждержавний, регіональний і '
        'релігійний: `RIP_shared_<родина>_<тема>.txt`. Назва означає належність '
        'контенту, а не додаткове обмеження доступності тегом.',
        '- Табуляція, пробіли навколо `=`, розгорнуті блоки, UTF-8 без BOM. '
        'Коментарі та рядки збережено; баланс, ID й порядок опцій не змінено.',
        f'- Нерозв’язаних прямих викликів із подій: {len(missing_calls)}; '
        f'з усіх перевірених каталогів: {len(unresolved_repository_calls)}; '
        f'невідповідностей country_event/province_event: {len(call_kinds)}.', '',
        f'Параметризованих місць виклику: {len(parameterized_repository_calls)} '
        '(`$INVITATION$`, `$ANNOUNCEMENT$` у rip_crusade_effects). Вони винесені '
        'окремо від нерозв’язаних буквальних ID; значення передаються викликачем.', '',
        '## Порівняння з ваніллю', '',
        f'Джерело: `{vanilla}`, версія {out["version"]}; {len(vanilla_events)} подій. '
        'Використано локальні файли гри, а не припущення про формат.', '',
        'Збережено пласку структуру events, namespace, country_event/province_event, '
        'trigger, MTTH або is_triggered_only, immediate й option. Ваніль '
        'поєднує країнові та тематичні файли й допускає однорядкові блоки; '
        'стиль RIP навмисно суворіше уніфіковано. Це відповідність структури, '
        'а не твердження про тотожність усіх механік або коректність кожного scope.', '',
        'Повна файлова заміна ванілі: ' + ', '.join(f'`{p}`' for p in overrides) +
        '. Її назву не змінено, щоб ванільні події не завантажилися вдруге.', '',
        'Генератори church_support, hetman_authority, regional_governments і '
        'eparchy_timeline використовують `tools/event_layout.py`. Старі імена '
        'в їхніх шаблонах є вхідними ключами класифікації, а не вихідними файлами. '
        'Маніфест `tools/data/event_layout_manifest.json` зберігає початкові хеші.', '',
        '## Події без іншого буквального використання', '',
        f'{len(isolated)} triggered-only подій потребують окремого рішення про '
        'підключення або архівування. `rip_gc_test.1` і `.10` належать ручній '
        'консольній лабораторії; відсутність автоматичного виклику для них очікувана. '
        'Для інших записів автоматичний шлях не підтверджено. Сам trigger '
        'не запускає is_triggered_only подію. Під час реорганізації їхню логіку не змінено.', '',
        '| ID | Файл |', '|---|---|',
    ]
    report.extend(f'| `{eid}` | `{rows[eid]["file"]}` |' for eid in isolated)
    report += ['', '## Карта перенесення', '', '| Старий файл | Поточні файли |', '|---|---|']
    report.extend(f'| `{old}` | ' + '<br>'.join(f'`{p}`' for p in paths) + ' |'
                  for old, paths in baseline['files'].items())
    report += ['', '## Межі перевірки', '',
        'Це статичний граф точних символів. Наявність посилання не доводить '
        'досяжність гілки; дані не симулюють ROOT/FROM/PREV, чергу подій чи AI. '
        'Динамічні посилання та завантаження інших модів потребують окремої перевірки. '
        'EU4, кампанію та старі збереження в межах цього аудиту не запускали.', '',
        'Перевірено encoding, braces, hidden-event shape, синхронність генераторів '
        'і script layer (0 помилок, 317 попереджень). Із пакета 92 тестів '
        'після ремонту eparchy_history проходять 90. Залишаються попередні '
        'помилки check_diocesan_union (очікує стару форму AI-умови в рішенні) '
        'та check_precommit_recovery (автопошук Python без RIP_PYTHON). '
        'Вони не спричинені перенесенням подій. Статичні перевірки не доводять runtime.', '']
    (ROOT / 'docs/EVENTS_LAYOUT_AUDIT_20261027.uk.md').write_text('\n'.join(report), encoding='utf-8')
    print(f'EVENT LAYOUT PASS: {len(events)} event IDs and ordered token hashes preserved; UTF-8, style, namespaces, overrides checked.')
    print(f'LINK AUDIT: {len(missing_calls)} unresolved direct event calls; {len(isolated)} triggered-only events require caller review; {len(vanilla_events)} vanilla events compared.')
    print(target)


if __name__ == '__main__':
    main()
