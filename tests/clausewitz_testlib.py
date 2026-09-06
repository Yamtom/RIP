"""Small dependency-free helpers for static Clausewitz regression checks.

These helpers deliberately do not try to be a full EU4 parser.  They only
handle comments, quoted strings, and balanced brace blocks well enough for
targeted source-contract tests.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8-sig")


def _mask_comments_and_strings(text: str) -> str:
    """Keep newlines/braces positions stable while masking inert content."""
    chars = list(text)
    in_string = False
    escaped = False
    in_comment = False

    for index, char in enumerate(text):
        if in_comment:
            if char in "\r\n":
                in_comment = False
            else:
                chars[index] = " "
            continue

        if in_string:
            if escaped:
                escaped = False
                chars[index] = " "
            elif char == "\\":
                escaped = True
                chars[index] = " "
            elif char == '"':
                in_string = False
                chars[index] = " "
            elif char not in "\r\n":
                chars[index] = " "
            continue

        if char == "#":
            in_comment = True
            chars[index] = " "
        elif char == '"':
            in_string = True
            chars[index] = " "

    return "".join(chars)


def matching_brace(text: str, opening: int) -> int:
    masked = _mask_comments_and_strings(text)
    depth = 0
    for index in range(opening, len(masked)):
        if masked[index] == "{":
            depth += 1
        elif masked[index] == "}":
            depth -= 1
            if depth == 0:
                return index
            if depth < 0:
                break
    raise ValueError(f"unmatched opening brace at offset {opening}")


def named_block(text: str, name: str, occurrence: int = 1) -> str:
    pattern = re.compile(rf"(?m)^\s*{re.escape(name)}\s*=\s*\{{")
    matches = list(pattern.finditer(_mask_comments_and_strings(text)))
    if len(matches) < occurrence:
        raise KeyError(f"block {name!r} occurrence {occurrence} not found")
    match = matches[occurrence - 1]
    opening = text.find("{", match.start(), match.end())
    closing = matching_brace(text, opening)
    return text[match.start(): closing + 1]


def keyed_blocks(text: str, key: str):
    pattern = re.compile(rf"(?m)^\s*{re.escape(key)}\s*=\s*\{{")
    masked = _mask_comments_and_strings(text)
    for match in pattern.finditer(masked):
        opening = text.find("{", match.start(), match.end())
        closing = matching_brace(text, opening)
        yield match.start(), text[match.start(): closing + 1]


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", _mask_comments_and_strings(text)).strip()


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def brace_error(text: str) -> str | None:
    masked = _mask_comments_and_strings(text)
    depth = 0
    for index, char in enumerate(masked):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return f"unexpected closing brace on line {line_number(text, index)}"
    if depth:
        return f"{depth} unmatched opening brace(s)"
    return None


# ==========================================================================
# THE VANILLA INSTALL
#
# The single most repeated operation in this project is asking whether
# something exists in VANILLA before trusting it: is this a real modifier or a
# typo the engine will drop, does this event picture name a real spriteType,
# what does this define actually say, does vanilla already own this
# localisation key. Every check that needed this grew its own ad-hoc
# discovery, and they did not agree - five read EU4_DIR,
# check_ro_blessing_window.py read EU4_GAME_DIR, and CLAUDE.md documents only
# the first.
#
# THE FAILURE MODE THESE HELPERS EXIST TO AVOID
#
# Vanilla may be absent. A helper that answers "no" when it means "I could not
# look" turns a missing install into a wall of false failures - which is the
# prime rule of this repository restated as a bug. So every lookup below is
# TRI-STATE and returns None for unknown. Callers must test explicitly:
#
#     if vanilla_has_sprite(name) is False:   # known absent -> a real error
#         fail(...)
#     # None means unknown: say so, or skip. Never fail on it.
# ==========================================================================

import os
import json

_UNSET = object()
_vanilla_root = _UNSET
_vanilla_cache = {}

# The stray "s" in "Programs Files(x86)" is not a typo here - it is the real
# directory name on the author's machine, and it is why bare auto-detection
# misses the install.
_VANILLA_CANDIDATES = (
    r"D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV",
    r"C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV",
    r"D:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV",
    r"C:/Program Files/Steam/steamapps/common/Europa Universalis IV",
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV",
)


def vanilla_version(path):
    """Read game version from launcher metadata, never from the generic EXE 1.0."""
    try:
        data = json.loads((Path(path) / "launcher-settings.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None
    for key in ("rawVersion", "version"):
        match = re.search(r"\b(?:v)?(\d+\.\d+(?:\.\d+)*)", str(data.get(key, "")))
        if match:
            return match.group(1)
    return None


def target_vanilla_series():
    """Version family declared by the mod, e.g. 1.37; donor installs stay separate."""
    match = re.search(r'supported_version\s*=\s*"v?(\d+\.\d+)', read("descriptor.mod"))
    return match.group(1) if match else None


def vanilla_matches_target(path, target=None):
    version = vanilla_version(path)
    target = target or target_vanilla_series()
    return bool(version and target and (version == target or version.startswith(target + ".")))


def _installed_candidates():
    seen = set()
    values = [v for v in (os.environ.get("EU4_DIR"), os.environ.get("EU4_GAME_DIR")) if v]
    for value in values + list(_VANILLA_CANDIDATES):
        path = Path(value)
        key = str(path).lower()
        if key not in seen and (path / "common" / "religions").is_dir():
            seen.add(key)
            yield path


def vanilla_installation_root():
    """First installed game of ANY version. Use only for explicitly labelled donor audits."""
    return next(_installed_candidates(), None)


def vanilla_root():
    """A target-compatible install, or None. Old donors cannot certify new content."""
    global _vanilla_root
    if _vanilla_root is not _UNSET:
        return _vanilla_root

    _vanilla_root = None
    rejected = []
    for path in _installed_candidates():
        if vanilla_matches_target(path):
            _vanilla_root = path
            break
        rejected.append(f"{vanilla_version(path) or 'unknown version'} at {path}")
    if _vanilla_root is None and rejected:
        print("SKIP: target EU4 " + str(target_vanilla_series()) +
              " data unavailable; donor install excluded: " + "; ".join(rejected))
    return _vanilla_root


def vanilla_available():
    """True when lookups can answer. Use it to word a skip message once."""
    return vanilla_root() is not None


def vanilla_read(relative_path):
    """Text of one vanilla file, or None if vanilla or the file is absent."""
    root = vanilla_root()
    if root is None:
        return None
    key = ("file", relative_path)
    if key not in _vanilla_cache:
        try:
            _vanilla_cache[key] = (root / relative_path).read_text(
                encoding="utf-8-sig", errors="replace")
        except OSError:
            _vanilla_cache[key] = None
    return _vanilla_cache[key]


def _vanilla_glob_text(subdir, pattern):
    """Concatenated text of a vanilla directory, or None. Cached."""
    root = vanilla_root()
    if root is None:
        return None
    key = ("glob", subdir, pattern)
    if key not in _vanilla_cache:
        chunks = []
        base = root / subdir
        if base.is_dir():
            for path in sorted(base.rglob(pattern)):
                try:
                    chunks.append(path.read_text(encoding="utf-8-sig", errors="replace"))
                except OSError:
                    continue
        _vanilla_cache[key] = "\n".join(chunks)
    return _vanilla_cache[key]


def vanilla_defines():
    """Every NAME = value in common/defines.lua as strings, or None.

    Values stay strings deliberately: MAX_FERVOR is "100.0" and
    ORTHODOX_ICON_DURATION_MONTHS is "240", and a check that wants a number
    should say which kind it wants.
    """
    text = vanilla_read("common/defines.lua")
    if text is None:
        return None
    key = ("defines",)
    if key not in _vanilla_cache:
        _vanilla_cache[key] = {
            name: value.strip()
            for name, value in re.findall(
                r"(?m)^\s*([A-Z][A-Z0-9_]*)\s*=\s*([^,\n]+)", text)
        }
    return _vanilla_cache[key]


def vanilla_define(name):
    """One define as a string, or None.

    Ambiguous by design - call vanilla_available() first when the difference
    between "no install" and "no such define" matters.
    """
    defines = vanilla_defines()
    return None if defines is None else defines.get(name)


def vanilla_sprite_names():
    """Every spriteType name declared in vanilla interface/*.gfx, or None.

    This is what an event `picture = X` is resolved against. Naming one that
    does not exist fails silently in game. Returns vanilla only - union the
    mod's own interface/*.gfx in at the call site.
    """
    text = _vanilla_glob_text("interface", "*.gfx")
    if text is None:
        return None
    key = ("sprites",)
    if key not in _vanilla_cache:
        _vanilla_cache[key] = frozenset(re.findall(r'\bname\s*=\s*"([^"]+)"', text))
    return _vanilla_cache[key]


def vanilla_has_sprite(name):
    """True / False / None(unknown). Test `is False` before failing a check."""
    names = vanilla_sprite_names()
    return None if names is None else name in names


def vanilla_localisation_keys(language="english"):
    """Every localisation key vanilla defines for a language, or None.

    This is why the localisation checks went from 415 reported errors to 0:
    most keys a mod appears to be missing are inherited.
    """
    root = vanilla_root()
    if root is None:
        return None
    key = ("loc", language)
    if key not in _vanilla_cache:
        found = set()
        base = root / "localisation"
        if base.is_dir():
            for path in sorted(base.rglob("*_l_%s.yml" % language)):
                try:
                    text = path.read_text(encoding="utf-8-sig", errors="replace")
                except OSError:
                    continue
                found.update(re.findall(
                    r"(?m)^\s*([A-Za-z_][\w.\-]*)\s*:\s*\d*\s*\"", text))
        _vanilla_cache[key] = frozenset(found)
    return _vanilla_cache[key]


def vanilla_defines_localisation(key_name, language="english"):
    """True / False / None(unknown) for one localisation key."""
    keys = vanilla_localisation_keys(language)
    return None if keys is None else key_name in keys


def vanilla_grep(pattern, subdir="common", glob="*.txt"):
    """Regex findall across a vanilla directory, or None if vanilla is absent.

    The escape hatch for the one-off questions these helpers do not name -
    "is this effect real", "in which scope is it used". Use it to count and to
    locate, not to parse.
    """
    text = _vanilla_glob_text(subdir, glob)
    if text is None:
        return None
    return re.findall(pattern, text)
