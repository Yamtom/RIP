"""Static regression contract for RIP opinion modifiers after their split."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re
import sys

from clausewitz_testlib import ROOT, _mask_comments_and_strings, line_number, matching_brace


MODIFIER_DIR = ROOT / "common" / "opinion_modifiers"
COUNTRY_FILES = {
    "chr_opinion_modifiers.txt": (re.compile(r"^chr_"), set()),
    "cri_opinion_modifiers.txt": (re.compile(r"^(?:crimean_|crimea_)"), set()),
    "het_opinion_modifiers.txt": (
        re.compile(r"^(?:het_|hetmanate_)"),
        {"accepted_russian_candidate", "rejected_russian_candidate", "accepted_collegium", "resisted_collegium", "negotiated_autonomy"},
    ),
    "kie_opinion_modifiers.txt": (re.compile(r"^(?:kie_|kyivan_|svydrigaylo_|ruthenian_independence_|supports_ruthenian_)"), set()),
    "lit_opinion_modifiers.txt": (re.compile(r"^(?:lit_|lithuania_)"), set()),
    "mos_opinion_modifiers.txt": (re.compile(r"^(?:rip_tot_|muscovy_)"), set()),
    "pdl_opinion_modifiers.txt": (re.compile(r"^pdl_"), set()),
    "plc_opinion_modifiers.txt": (re.compile(r"^(?:plc_|poland_)"), set()),
    "tur_opinion_modifiers.txt": (re.compile(r"^ottoman_"), set()),
    "uzh_opinion_modifiers.txt": (re.compile(r"^opinion_uz_"), set()),
    "vol_opinion_modifiers.txt": (re.compile(r"^vol_"), set()),
    "west_ukr_opinion_modifiers.txt": (re.compile(r"^west_ukr_"), set()),
    "zaz_opinion_modifiers.txt": (
        re.compile(r"^zaz_"),
        {"demanded_sich_relocation", "expanded_register", "abolished_register", "demanded_hetman_change", "integrated_host_system", "orthodox_cossack_defenders"},
    ),
}
SCRIPT_DIRS = ("common", "decisions", "events", "missions", "history")
OPINION_APIS = re.compile(
    r"\b(?:add_opinion|reverse_add_opinion|remove_opinion|reverse_remove_opinion|"
    r"has_opinion_modifier|reverse_has_opinion_modifier)\s*=\s*\{"
)
MODIFIER_VALUE = re.compile(r"\bmodifier\s*=\s*\"?([A-Za-z0-9_]+)\"?")
TOP_LEVEL_DEFINITION = re.compile(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{")
NEGATIVE_MAX = re.compile(r"(?m)^\s*max\s*=\s*-\d+(?:\.\d+)?\s*$")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def definitions_from_text(text: str) -> list[tuple[str, int, str]]:
    """Return only top-level modifier blocks, excluding comments and strings."""
    result: list[tuple[str, int, str]] = []
    masked = _mask_comments_and_strings(text)
    cursor = 0
    while cursor < len(masked):
        match = TOP_LEVEL_DEFINITION.search(masked, cursor)
        if not match:
            break
        depth = masked.count("{", cursor, match.start()) - masked.count("}", cursor, match.start())
        if depth == 0:
            opening = masked.find("{", match.start(), match.end())
            closing = matching_brace(text, opening)
            result.append((match.group(1), match.start(), text[match.start():closing + 1]))
            cursor = closing + 1
        else:
            cursor = match.end()
    return result


def mask_comments(text: str) -> str:
    """Mask comments without hiding quoted modifier keys."""
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
        elif in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == "#":
            in_comment = True
            chars[index] = " "
        elif char == '"':
            in_string = True
    return "".join(chars)


def opinion_uses_from_text(text: str) -> list[tuple[str, int]]:
    """Find literal modifier values inside brace-matched opinion API blocks."""
    uses: list[tuple[str, int]] = []
    masked = _mask_comments_and_strings(text)
    for match in OPINION_APIS.finditer(masked):
        opening = masked.find("{", match.start(), match.end())
        closing = matching_brace(text, opening)
        block = mask_comments(text[opening:closing + 1])
        for value in MODIFIER_VALUE.finditer(block):
            uses.append((value.group(1), opening + value.start(1)))
    return uses


def self_test() -> int:
    definitions = definitions_from_text(
        "# chr_wrong = { max = -50 }\n"
        "het_real = {\n\tmax = 0\n}\n"
        "het_bad_max = {\n\tmax = -50\n}\n"
    )
    assert [key for key, _, _ in definitions] == ["het_real", "het_bad_max"]
    assert not NEGATIVE_MAX.search(_mask_comments_and_strings(definitions[0][2]))
    assert NEGATIVE_MAX.search(_mask_comments_and_strings(definitions[1][2]))

    uses = opinion_uses_from_text(
        "# add_opinion = { modifier = ignored }\n"
        "if = { limit = { always = yes } reverse_add_opinion = {\n"
        "\t# modifier = ignored\n\tmodifier = \"het_real\"\n}\n}\n"
    )
    assert [key for key, _ in uses] == ["het_real"]
    print("OPINION MODIFIER LAYER SELF-TEST: PASS")
    return 0


def main() -> int:
    failures: list[str] = []
    definitions: dict[str, list[str]] = defaultdict(list)

    if (MODIFIER_DIR / "RIP_opinion_modifiers.txt").exists():
        failures.append("RIP_opinion_modifiers.txt monolith must stay removed")

    for filename in COUNTRY_FILES:
        if not (MODIFIER_DIR / filename).is_file():
            failures.append(f"missing country ownership file: {filename}")

    for path in sorted(MODIFIER_DIR.glob("*.txt")):
        text = read(path)
        for key, offset, block in definitions_from_text(text):
            location = f"{path.name}:{line_number(text, offset)}"
            definitions[key].append(location)
            if path.name in COUNTRY_FILES:
                prefix, exceptions = COUNTRY_FILES[path.name]
                if not prefix.match(key) and key not in exceptions:
                    failures.append(f"{location}: {key} violates {path.name} ownership")
            if NEGATIVE_MAX.search(_mask_comments_and_strings(block)):
                failures.append(f"{location}: {key} has a negative max")

    for filename in COUNTRY_FILES:
        if not any(location.startswith(f"{filename}:") for locations in definitions.values() for location in locations):
            failures.append(f"empty country ownership file: {filename}")

    for key, locations in definitions.items():
        if len(locations) > 1:
            failures.append(f"duplicate opinion modifier {key}: {', '.join(locations)}")

    external_uses: dict[str, list[str]] = defaultdict(list)
    for dirname in SCRIPT_DIRS:
        for path in (ROOT / dirname).rglob("*.txt"):
            if path.parent == MODIFIER_DIR:
                continue
            text = read(path)
            for key, offset in opinion_uses_from_text(text):
                if key in definitions:
                    external_uses[key].append(f"{path.relative_to(ROOT)}:{line_number(text, offset)}")

    for key in sorted(definitions):
        if not external_uses[key]:
            failures.append(f"orphaned opinion modifier {key}: no external opinion API use")

    if failures:
        print("OPINION MODIFIER LAYER CHECK: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("OPINION MODIFIER LAYER CHECK: PASS " f"({len(definitions)} unique definitions; all externally used)")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    raise SystemExit(main())