"""Regression test for decision localization and end event integrity across all supported languages.

Verifies:
1. Standard Decision Title and Description Contracts:
   - Every decision in decisions/*.txt must have standard `<decision>_title` and `<decision>_desc`.
   - Bare decision names (`<decision>`) are NOT accepted as substitutes for `<decision>_title`.
   - Key lookup is exact (dictionary membership), NOT fuzzy substring search.
   - Covers English, French, German, and Spanish.
2. Decision-Triggered End Event Completeness:
   - Every event triggered by decisions (and downstream event chains) must have defined
     title, desc, and option keys across all 4 languages.
   - Values must be non-empty strings.
3. Duplicate Localization Key Prevention:
   - No localization key may be defined more than once within any language (across all .yml files).
4. Planted Regressions:
   - Catching missing standard `<decision>_title` (e.g. only bare key defined).
   - Catching missing `<decision>_desc`.
   - Catching missing event option localization.
   - Catching duplicate key definitions.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import ROOT, read, keyed_blocks, matching_brace, _mask_comments_and_strings, vanilla_available, vanilla_localisation_keys

LANGUAGES = ("english", "french", "german", "spanish")
LOC_ENTRY = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*\d*\s*"([^"]*)"', re.M)

# Cache vanilla localization keys once
_VANILLA_KEYS: dict[str, set[str]] = {}
if vanilla_available():
    for lang in LANGUAGES:
        try:
            _VANILLA_KEYS[lang] = vanilla_localisation_keys(lang)
        except Exception:
            _VANILLA_KEYS[lang] = set()
else:
    for lang in LANGUAGES:
        _VANILLA_KEYS[lang] = set()


def load_localization(language: str) -> tuple[dict[str, tuple[str, str]], dict[str, list[str]]]:
    """Load all localization keys for a given language.
    Returns (key_dict: key -> (value, filename), duplicates: key -> list of filenames).
    """
    key_dict: dict[str, tuple[str, str]] = {}
    duplicates: dict[str, list[str]] = defaultdict(list)
    
    loc_files = sorted((ROOT / "localisation").glob(f"**/*_{language}.yml"))
    for p in loc_files:
        text = p.read_text(encoding="utf-8-sig", errors="ignore")
        for m in LOC_ENTRY.finditer(text):
            k = m.group(1)
            v = m.group(2)
            if k == f"l_{language}":
                continue
            if k in key_dict:
                duplicates[k].append(p.name)
            else:
                key_dict[k] = (v, p.name)
                duplicates[k].append(p.name)
                
    actual_duplicates = {k: files for k, files in duplicates.items() if len(files) > 1}
    return key_dict, actual_duplicates


def parse_all_decisions() -> list[tuple[str, str, list[str]]]:
    """Parse all decisions from decisions/*.txt.
    Returns list of (filename, decision_name, triggered_events).
    """
    decisions = []
    for p in sorted((ROOT / "decisions").glob("*.txt")):
        text = p.read_text(encoding="utf-8-sig", errors="ignore")
        for wrapper in ("country_decisions", "religion_decisions"):
            for _, block in keyed_blocks(text, wrapper):
                inner = block[block.find("{") + 1 : block.rfind("}")]
                masked = _mask_comments_and_strings(inner)
                depth = 0
                key = None
                i = 0
                while i < len(masked):
                    c = masked[i]
                    if depth == 0 and c == "=":
                        pre = masked[:i].rstrip()
                        m = re.search(r"([a-zA-Z0-9_]+)\s*$", pre)
                        if m:
                            key = m.group(1)
                    elif c == "{":
                        if depth == 0:
                            opening = i
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0 and key:
                            closing = i
                            dec_body = inner[opening : closing + 1]
                            events = re.findall(
                                r"(?:country_event|province_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)",
                                dec_body,
                            )
                            decisions.append((p.name, key, events))
                            key = None
                    i += 1
    return decisions


def parse_all_events() -> dict[str, dict]:
    """Parse all events from events/*.txt."""
    event_defs = {}
    for p in sorted((ROOT / "events").glob("*.txt")):
        text = p.read_text(encoding="utf-8-sig", errors="ignore")
        for m in re.finditer(r"^\s*(country_event|province_event)\s*=\s*\{", text, re.MULTILINE):
            start = m.start()
            opening = text.find("{", start)
            closing = matching_brace(text, opening)
            block = text[start : closing + 1]
            idm = re.search(r'^\s*id\s*=\s*"?([A-Za-z0-9_.\-]+)"?', block, re.M)
            if idm:
                eid = idm.group(1)
                tm = re.search(r'^\s*title\s*=\s*"?([A-Za-z0-9_.\-]+)"?', block, re.M)
                descs = re.findall(r'^\s*desc\s*=\s*"?([A-Za-z0-9_.\-]+)"?', block, re.M)
                opt_names = []
                for opt_match in re.finditer(r"^\s*option\s*=\s*\{", block, re.M):
                    opt_open = block.find("{", opt_match.start())
                    opt_close = matching_brace(block, opt_open)
                    opt_body = block[opt_open : opt_close + 1]
                    nm = re.search(r'^\s*name\s*=\s*"?([A-Za-z0-9_.\-]+)"?', opt_body, re.M)
                    if nm:
                        opt_names.append(nm.group(1))
                downstream = re.findall(
                    r"(?:country_event|province_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)",
                    block,
                )
                event_defs[eid] = {
                    "file": p.name,
                    "title": tm.group(1) if tm else None,
                    "descs": descs,
                    "options": opt_names,
                    "downstream": downstream,
                }
    return event_defs


def collect_reachable_events(
    decisions: list[tuple[str, str, list[str]]], event_defs: dict[str, dict]
) -> set[str]:
    """Recursively collect all events reachable from decisions."""
    reachable = set()
    queue = []
    for _, _, evs in decisions:
        for e in evs:
            if e not in reachable:
                reachable.add(e)
                queue.append(e)
    while queue:
        curr = queue.pop(0)
        if curr in event_defs:
            for nxt in event_defs[curr]["downstream"]:
                if nxt not in reachable:
                    reachable.add(nxt)
                    queue.append(nxt)
    return reachable


def verify_decision_keys(
    decisions: list[tuple[str, str, list[str]]],
    loc_by_lang: dict[str, dict[str, tuple[str, str]]],
) -> list[str]:
    """Verify standard _title and _desc for all decisions."""
    errors = []
    for fname, dname, _ in decisions:
        title_key = f"{dname}_title"
        desc_key = f"{dname}_desc"
        for lang in LANGUAGES:
            mod_keys = loc_by_lang[lang]
            vanilla_k = _VANILLA_KEYS.get(lang, set())
            
            # Strict title check: must be exactly `<decision>_title`, NOT bare `<decision>`
            has_title = title_key in mod_keys or title_key in vanilla_k
            if not has_title:
                has_bare = dname in mod_keys or dname in vanilla_k
                if has_bare:
                    errors.append(
                        f"[{lang}] Decision '{dname}' ({fname}) uses bare key '{dname}' instead of standard '{title_key}'"
                    )
                else:
                    errors.append(
                        f"[{lang}] Decision '{dname}' ({fname}) missing standard title '{title_key}'"
                    )
            
            # Strict desc check: must be exactly `<decision>_desc`
            has_desc = desc_key in mod_keys or desc_key in vanilla_k
            if not has_desc:
                errors.append(
                    f"[{lang}] Decision '{dname}' ({fname}) missing standard desc '{desc_key}'"
                )
    return errors


def verify_reachable_events(
    reachable_events: set[str],
    event_defs: dict[str, dict],
    loc_by_lang: dict[str, dict[str, tuple[str, str]]],
) -> list[str]:
    """Verify localization for all events reachable from decisions."""
    errors = []
    for eid in sorted(reachable_events):
        if eid not in event_defs:
            # Vanilla event (e.g. ideagroups.1)
            continue
        ed = event_defs[eid]
        keys = []
        if ed["title"]:
            keys.append(("title", ed["title"]))
        for d in ed["descs"]:
            keys.append(("desc", d))
        for o in ed["options"]:
            keys.append(("option", o))
            
        for lang in LANGUAGES:
            mod_keys = loc_by_lang[lang]
            vanilla_k = _VANILLA_KEYS.get(lang, set())
            for ktype, k in keys:
                has_key = k in mod_keys or k in vanilla_k
                if not has_key:
                    errors.append(
                        f"[{lang}] Event '{eid}' ({ed['file']}) missing {ktype} localization key '{k}'"
                    )
                elif k in mod_keys and not mod_keys[k][0].strip():
                    errors.append(
                        f"[{lang}] Event '{eid}' ({ed['file']}) {ktype} key '{k}' has empty text"
                    )
    return errors


def verify_no_duplicates(
    duplicates_by_lang: dict[str, dict[str, list[str]]]
) -> list[str]:
    """Verify that no language has duplicated localization keys."""
    errors = []
    for lang in LANGUAGES:
        dups = duplicates_by_lang[lang]
        for k, files in sorted(dups.items()):
            errors.append(f"[{lang}] Duplicate key '{k}' defined in: {files}")
    return errors


def test_planted_regressions(
    decisions: list[tuple[str, str, list[str]]],
    reachable_events: set[str],
    event_defs: dict[str, dict],
    loc_by_lang: dict[str, dict[str, tuple[str, str]]],
):
    """Ensure that the audit catches planted errors (decision bare title, missing desc, event missing option, duplicates)."""
    # 1. Bare title mutation
    fake_decisions = [("test.txt", "planted_decision_bare", [])]
    fake_loc = {
        lang: {"planted_decision_bare": ("Some Title", "fake.yml")}
        for lang in LANGUAGES
    }
    errs = verify_decision_keys(fake_decisions, fake_loc)
    assert any("uses bare key" in e for e in errs), "Failed to catch bare title mutation"

    # 2. Missing desc mutation
    fake_loc_no_desc = {
        lang: {"planted_decision_bare_title": ("Some Title", "fake.yml")}
        for lang in LANGUAGES
    }
    errs = verify_decision_keys(fake_decisions, fake_loc_no_desc)
    assert any("missing standard desc" in e for e in errs), "Failed to catch missing desc mutation"

    # 3. Missing event option mutation
    fake_events = {"fake_event.1"}
    fake_event_defs = {
        "fake_event.1": {
            "file": "test.txt",
            "title": "fake.1.t",
            "descs": ["fake.1.d"],
            "options": ["fake.1.a", "fake.1.missing_option"],
            "downstream": [],
        }
    }
    fake_loc_event = {
        lang: {
            "fake.1.t": ("Title", "fake.yml"),
            "fake.1.d": ("Desc", "fake.yml"),
            "fake.1.a": ("Option A", "fake.yml"),
        }
        for lang in LANGUAGES
    }
    errs = verify_reachable_events(fake_events, fake_event_defs, fake_loc_event)
    assert any("fake.1.missing_option" in e for e in errs), "Failed to catch missing event option mutation"

    # 4. Duplicate key mutation
    fake_dups = {
        lang: {"duplicate_key": ["file1.yml", "file2.yml"]} if lang == "french" else {}
        for lang in LANGUAGES
    }
    errs = verify_no_duplicates(fake_dups)
    assert any("duplicate_key" in e for e in errs), "Failed to catch duplicate key mutation"


def main():
    # 1. Load localizations
    loc_by_lang = {}
    duplicates_by_lang = {}
    for lang in LANGUAGES:
        loc_map, dups = load_localization(lang)
        loc_by_lang[lang] = loc_map
        duplicates_by_lang[lang] = dups

    # 2. Parse decisions and events
    decisions = parse_all_decisions()
    assert len(decisions) == 251, f"Expected 251 decisions, found {len(decisions)}"
    event_defs = parse_all_events()
    reachable_events = collect_reachable_events(decisions, event_defs)

    # 3. Verify no duplicates
    dup_errors = verify_no_duplicates(duplicates_by_lang)
    assert not dup_errors, f"Duplicate localization keys found:\n" + "\n".join(dup_errors)

    # 4. Verify standard _title and _desc for all decisions
    dec_errors = verify_decision_keys(decisions, loc_by_lang)
    assert not dec_errors, f"Decision localization errors found:\n" + "\n".join(dec_errors)

    # 5. Verify reachable end events
    ev_errors = verify_reachable_events(reachable_events, event_defs, loc_by_lang)
    assert not ev_errors, f"End event localization errors found:\n" + "\n".join(ev_errors)

    # 6. Planted regression verification
    test_planted_regressions(decisions, reachable_events, event_defs, loc_by_lang)

    print(
        f"DECISION LOCALE INTEGRITY PASS: All {len(decisions)} decisions verified for standard _title and _desc; "
        f"{len(reachable_events)} reachable end events verified across all 4 languages; "
        f"0 duplicate keys detected across EFIGS. 4 planted mutations caught."
    )


if __name__ == "__main__":
    main()
