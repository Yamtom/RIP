"""Every mission title in missions/*.txt fits EU4's two-line mission banner.

Same measure as check_kyiv_mission_layout.py (vic_18 advance widths, banner width
84 and 90 px, two lines at most, no single word wider than the banner), applied to
all mission files instead of the Kyiv, Podillia, Volhynia and UZH trees alone.
A `[X.GetName]` placeholder is measured as a nine-letter name. Mission titles that
come from vanilla keys (DOM_Russia, TR_Russian_Minors) have no RIP entry and are
skipped. Needs the installed game for the font; without it the check says so and
passes.
"""
import re
import sys

from clausewitz_testlib import ROOT, vanilla_root

installed = vanilla_root()
font = installed / "gfx/fonts/vic_18.fnt" if installed else None
if not font or not font.is_file():
    print("MISSION TITLE WIDTH: SKIPPED (installed EU4 not found, no font metrics)")
    sys.exit(0)

adv = {int(m.group(1)): int(m.group(2))
       for m in re.finditer(r"char\s+id=(\d+).*?xadvance=(-?\d+)", font.read_text(encoding="latin-1"))}
space = adv.get(32, 4)


def wrap(title, max_w):
    lines, cur = [], 0
    for word in title.split(" "):
        w = sum(adv.get(ord(c), 7) for c in word)
        if cur == 0:
            cur = w
        elif cur + space + w <= max_w:
            cur += space + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return len(lines), max(lines or [0])


loc = {}
loc_files = sorted((ROOT / "localisation").glob("*_l_english.yml")) + sorted(
    (ROOT / "localisation/replace").glob("*_l_english.yml"))
for path in loc_files:
    for key, value in re.findall(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', path.read_text(encoding="utf-8-sig"), re.M):
        loc[key] = value


def resolve(value):
    seen = set()
    while re.fullmatch(r"\$[A-Za-z0-9_.\-]+\$", value) and value not in seen:
        seen.add(value)
        value = loc.get(value[1:-1], value)
    return re.sub(r"\[[^\]]*\]", "Lithuania", value)


def mission_names(text):
    depth, out, cur, body = 0, [], None, []
    for line in text.split("\n"):
        code = re.sub(r"#.*", "", line)
        match = re.match(r"^\s*([A-Za-z_0-9]+)\s*=\s*\{", code)
        if depth == 1 and match:
            cur, body = match.group(1), []
        if cur is not None:
            body.append(code)
        depth += code.count("{") - code.count("}")
        if depth == 1 and cur is not None:
            if any(re.match(r"^\s*position\s*=", b) for b in body):
                out.append(cur)
            cur = None
    return out


problems, checked = [], 0
for path in sorted((ROOT / "missions").glob("*.txt")):
    text = "\n".join(path.read_text(encoding="utf-8-sig").splitlines())
    for name in mission_names(text):
        key = f"{name}_title"
        if key not in loc:
            continue
        checked += 1
        title = resolve(loc[key])
        n84, w84 = wrap(title, 84)
        n90, w90 = wrap(title, 90)
        if n84 > 2 or n90 > 2 or w84 > 84 or w90 > 90:
            problems.append(f"{path.name}::{name}: {title!r} (lines {n84}/{n90}, widest {w84}/{w90})")

if problems:
    print("MISSION TITLE WIDTH: FAIL")
    for item in problems:
        print("  -", item)
    sys.exit(1)
print(f"MISSION TITLE WIDTH: PASS ({checked} mission titles fit two lines at 84 and 90 px)")
