"""Write the French, German and Spanish copies of localisation/rip_border_mechanics_l_english.yml.

The mod's source language is English. French, German and Spanish carry the English text
under localisation/replace/ so that nothing renders as a raw key while a translation is
outstanding (docs/STYLE_GLOSSARY.md). This tool derives those copies from the English
file, so the four languages cannot drift:

    python tools/build_border_mechanics_localisation.py            # write the three files
    python tools/build_border_mechanics_localisation.py --check    # exit 1 when one is stale

When a real translation of a line exists, put it into the copy by hand and delete the
key from the English-derived output: this tool then needs a skip list, which it does not
have yet. Until then the copies are plain English.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "localisation" / "rip_border_mechanics_l_english.yml"
LANGUAGES = {
    "french": "Traduction partielle",
    "german": "Teilweise ubersetzt",
    "spanish": "Traduccion parcial",
}
ENTRY = re.compile(r'^ ([A-Za-z0-9_.\-]+):\d+ ".*"$')
OWNER = "shared_frontier"
ENTITY = "border_watch"


def target(language: str) -> Path:
    return ROOT / "localisation" / "replace" / f"RIP_{OWNER}_{ENTITY}_l_{language}.yml"


def entry_lines() -> list[str]:
    text = SOURCE.read_text(encoding="utf-8-sig")
    return [line for line in text.splitlines() if ENTRY.match(line)]


def render(language: str, lines_out: list[str]) -> bytes:
    lines = [
        f"l_{language}:",
        "",
        f" # {LANGUAGES[language]} (owner={OWNER}, entity={ENTITY}). The mod's source language is English;",
        " # the entries below are copied from localisation/rip_border_mechanics_l_english.yml so nothing",
        " # renders as a raw key while the translation is outstanding. Written by",
        " # tools/build_border_mechanics_localisation.py: change the English file, not this one.",
        "",
        *lines_out,
        "",
    ]
    return b"\xef\xbb\xbf" + "\r\n".join(lines).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="exit 1 when a copy is missing or stale")
    args = parser.parse_args()
    lines_out = entry_lines()
    stale = []
    for language in LANGUAGES:
        path = target(language)
        want = render(language, lines_out)
        if args.check:
            if not path.is_file() or path.read_bytes() != want:
                stale.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_bytes(want)
            print(f"wrote {path.relative_to(ROOT).as_posix()} ({len(lines_out)} keys)")
    if stale:
        print("STALE: " + ", ".join(stale))
        return 1
    if args.check:
        print(f"BORDER MECHANICS LOCALISATION PASS: {len(lines_out)} keys in {len(LANGUAGES)} tag-scoped fallback files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
