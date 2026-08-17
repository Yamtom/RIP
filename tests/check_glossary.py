"""Enforce docs/STYLE_GLOSSARY.md against the English localisation.

Run from the mod root:  python tests/check_glossary.py
Exit code 1 if anything drifts, so it can gate a merge.
"""
import re, glob, io, sys, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ENTRY   = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\s*(\d*)\s*"(.*)"\s*$')
BRACKET = re.compile(r'\[[^\]]*\]')

# Country display names are deliberate - see glossary section 4.
SKIP_KEYS = {"VLN", "POD", "KHK", "VOL", "ZAZ", "VLN_ADJ", "POD_ADJ", "KHK_ADJ"}

BANNED_SPELLING = [
    (r'\bKiev\b',         "Kyiv"),
    (r'\bKharkov\b',      "Kharkiv"),
    (r'\bChernigov\b',    "Chernihiv"),
    (r'\bLwow\b|\bLemberg\b', "Lviv"),
    (r'\bPodolia\b',      "Podillia"),
    (r'\bVolyn\b',        "Volhynia"),
    (r'\bBraclaw\b',      "Bratslav"),
    (r'\bZaporizhz?hia\b', "Zaporozhia"),
    (r'\bDnipro\b',       "Dnieper"),
    (r'\bsotnya\b',       "sotnia"),
    (r'\bataman\b',       "otaman"),
    (r'\bKish Otaman\b',  "Kosh Otaman"),
    # Glossary section 1 lists these too, and they were never enforced -
    # which is how "neither Moscow nor Istanbul" survived in ZAZ_HET_missions.
    (r'\bGalich\b',       "Halych"),
    (r'\bKamieniec\b|\bKamenets\b', "Kamianets"),
    (r'\bWilno\b|\bVilna\b', "Vilnius"),
    (r'\bCracow\b',       "Kraków"),
    (r'\bSublime Porte\b|\bIstanbul\b', "the Porte"),
]
BANNED_REGISTER = [
    (r'\bidentity\b',   "name a concrete thing instead"),
    (r'\bdemocratic\b', "name the institution: the Rada, election by acclamation"),
    (r'\bdemocracy\b',  "Cossack liberties, the old liberties"),
    (r'\bethnic\b',     "name the peoples"),
    (r'\bideology\b',   "creed, doctrine"),
]

def scan():
    fails = []
    files = sorted(glob.glob("localisation/*_l_english.yml")
                 + glob.glob("localisation/replace/*_l_english.yml"))
    for p in files:
        if "untranslated" in p:            # carried English, checked at source
            continue
        for i, line in enumerate(open(p, encoding="utf-8-sig", errors="replace").read().splitlines(), 1):
            m = ENTRY.match(line)
            if not m or m.group(1) in SKIP_KEYS:
                continue
            key = m.group(1)
            val = BRACKET.sub("", m.group(3))      # scripted-loc calls are not prose
            for pat, want in BANNED_SPELLING:
                if re.search(pat, val):
                    fails.append((p, i, key, "spelling", re.search(pat, val).group(0), want))
            for pat, want in BANNED_REGISTER:
                if re.search(pat, val, re.I):
                    fails.append((p, i, key, "register", re.search(pat, val, re.I).group(0), want))
    return fails

if __name__ == "__main__":
    fails = scan()
    if not fails:
        print("глосарій дотримано ✓")
        sys.exit(0)
    print("порушень глосарію: %d\n" % len(fails))
    for p, i, key, kind, found, want in fails[:40]:
        print("  %s:%d  [%s]" % (os.path.relpath(p), i, kind))
        print("     %s — «%s» -> %s" % (key, found, want))
    if len(fails) > 40:
        print("  … ще %d" % (len(fails) - 40))
    sys.exit(1)
