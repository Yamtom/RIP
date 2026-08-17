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
