"""Every sprite that draws a religion must slice a strip that has the religion's frame.

`icon = N` in common/religions is a frame index into FOUR textures, drawn by FIVE
sprites. The mod once extended three textures and three sprites and left the other
two sprites - so a Greek Catholic or Russian Orthodox advisor drew an empty circle
(province_view_religion.dds, GFX_province_view_religion) and every ledger icon
drifted 2 px a frame (GFX_religion_icon_strip kept noOfFrames = 29 over a 31-frame
file). Nothing flagged it; this does.

Asserted:
  - the mod declares every sprite that reads a religion strip, once each, with a
    noOfFrames at least the highest icon = N in common/religions;
  - each declared texture exists in the mod, is uncompressed 32-bit BGRA with no
    mipmaps, and is exactly 32 * frames or 64 * frames wide;
  - frames 1-29 equal vanilla, frame for frame (needs the installed game);
  - every frame a religion points at is drawn, and frames 30 and 31 are recoloured
    copies of their donors, not the donors;
  - the two 32 px strips show the same art, so an advisor row and a province view
    never disagree about a faith.

Standard library only. Does not render anything; native drawing is unverified.
"""
import re
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, vanilla_root

sys.path.insert(0, str(ROOT / "tools"))
from build_religion_icon_strips import Strip, visible  # noqa: E402

# normalised texture -> frame edge in pixels
STRIPS = {
    "gfx/interface/icon_religion.dds": 64,
    "gfx/interface/country_icon_religion.dds": 64,
    "gfx/interface/icon_religion_small.dds": 32,
    "gfx/interface/province_view_religion.dds": 32,
}
# The sprites known to read them in vanilla 1.37.5. Vanilla is searched for more.
SPRITES = {
    "GFX_icon_religion", "GFX_country_icon_religion", "GFX_icon_religion_small",
    "GFX_province_view_religion", "GFX_religion_icon_strip",
}
VANILLA_FRAMES = 29
DONORS = {30: 4, 31: 1}  # frame -> the vanilla frame it is recoloured from
errors = []


def fail(message):
    errors.append(message)


def norm(path):
    return re.sub(r"[\\/]+", "/", path).lower()


def decode(path):
    return path.read_bytes().decode("latin-1")


def sprites(text):
    """spriteType blocks as (name, texture, frames); flat blocks, comments removed."""
    text = re.sub(r"#[^\r\n]*", "", text)
    found = []
    for match in re.finditer(r"\bspriteType\s*=\s*\{", text):
        depth, i = 1, match.end()
        while depth and i < len(text):
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        body = text[match.end():i - 1]
        name = re.search(r'\bname\s*=\s*"([^"]+)"', body)
        texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', body)
        frames = re.search(r"\bnoOfFrames\s*=\s*(\d+)", body)
        found.append((name.group(1) if name else None, norm(texture.group(1)) if texture else None,
                      int(frames.group(1)) if frames else 1))
    return found


def religion_icons(text):
    """(religion, icon) for `icon = N` written directly inside a religion block."""
    text = re.sub(r"#[^\r\n]*", "", text)
    stack, found = [], []
    for match in re.finditer(r"([A-Za-z0-9_.\-]+)\s*=\s*\{|\{|\}|\bicon\s*=\s*(\d+)\b", text):
        token = match.group(0)
        if token == "}":
            if stack:
                stack.pop()
        elif token == "{":
            stack.append(None)
        elif match.group(2):
            if len(stack) == 2:  # group { religion { icon = N } }
                found.append((stack[1], int(match.group(2))))
        else:
            stack.append(match.group(1))
    return found


def declarations(root):
    out = []
    for path in sorted((root / "interface").rglob("*.gfx")):
        out.extend((name, texture, frames, path) for name, texture, frames in sprites(decode(path)))
    return out


def icons_of(root):
    found = []
    for path in sorted((root / "common" / "religions").glob("*.txt")):
        found.extend(religion_icons(decode(path)))
    return found


vanilla = vanilla_root()
mod_decl = declarations(ROOT)
mod_icons = icons_of(ROOT)
all_icons = mod_icons + (icons_of(vanilla) if vanilla else [])
if not mod_icons:
    fail("no icon = N found in the mod's common/religions; the parser is blind")
highest = max([n for _, n in all_icons] or [0])
for religion, number in mod_icons:
    clash = [r for r, n in all_icons if n == number and r != religion]
    if clash:
        fail(f"{religion} icon = {number} is also used by {', '.join(clash)}")

# Which sprites read a strip? The known five, plus anything vanilla points at one.
required = set(SPRITES)
if vanilla:
    for name, texture, _, _ in declarations(vanilla):
        if texture in STRIPS:
            required.add(name)
for name, texture, _, _ in mod_decl:
    if texture in STRIPS:
        required.add(name)

declared = {}
for name, texture, frames, path in mod_decl:
    if name in required:
        declared.setdefault(name, []).append((texture, frames, path.name))
for name in sorted(required):
    entries = declared.get(name, [])
    if not entries:
        fail(f"{name} reads a religion strip but the mod does not declare it; vanilla's 29 frames apply")
        continue
    if len(entries) > 1:
        fail(f"{name} is declared {len(entries)} times in the mod ({', '.join(e[2] for e in entries)}); the winner is ambiguous")
        continue
    texture, frames, _ = entries[0]
    if texture not in STRIPS:
        fail(f"{name} points at {texture}, which is not one of the four religion strips")
        continue
    if frames < highest:
        fail(f"{name} declares noOfFrames = {frames} but a religion uses icon = {highest}")

# Every texture the mod's sprites name, in the mod.
strips = {}
for texture, edge in STRIPS.items():
    path = ROOT / texture
    if not path.is_file():
        fail(f"{texture} is missing from the mod; vanilla's 29-frame file would be used")
        continue
    try:
        strips[texture] = Strip.read(path)
    except ValueError as problem:
        fail(str(problem))
        continue
    strip = strips[texture]
    if strip.height != edge:
        fail(f"{texture}: frame edge {strip.height}, expected {edge}")
    for name, entries in declared.items():
        for entry in entries:
            if entry[0] == texture and strip.width != strip.height * entry[1]:
                fail(f"{name} declares {entry[1]} frames but {texture} is {strip.width}x{strip.height} "
                     f"({strip.width / strip.height:g} frames)")
    if strip.frames < highest:
        fail(f"{texture} has {strip.frames} frames but a religion uses icon = {highest}")

# Frames.
referenced = sorted({n for _, n in all_icons})
for texture, strip in strips.items():
    area = strip.height * strip.height
    for number in referenced:
        if number > strip.frames:
            continue  # already reported as too few frames
        if visible(strip.frame(number)) < area // 10:
            fail(f"{texture}: frame {number} is referenced by a religion but is (nearly) empty")
    for number, donor in DONORS.items():
        if number <= strip.frames:
            if strip.frame(number) == strip.frame(donor):
                fail(f"{texture}: frame {number} is an unchanged copy of frame {donor}")
    if strip.frames >= 31 and strip.frame(30) == strip.frame(31):
        fail(f"{texture}: frames 30 and 31 are identical")

if vanilla:
    for texture, strip in strips.items():
        try:
            original = Strip.read(vanilla / texture)
        except (OSError, ValueError) as problem:
            fail(f"vanilla {texture}: {problem}")
            continue
        if original.frames != VANILLA_FRAMES:
            fail(f"vanilla {texture} has {original.frames} frames, expected {VANILLA_FRAMES}; update this check")
            continue
        bad = [n for n in range(1, VANILLA_FRAMES + 1) if n <= strip.frames and strip.frame(n) != original.frame(n)]
        if bad:
            fail(f"{texture}: frames {bad} differ from vanilla; frames 1-{VANILLA_FRAMES} must be untouched")

# The two 32 px strips share one drawing of each added faith.
small, province = (strips.get("gfx/interface/" + n) for n in ("icon_religion_small.dds", "province_view_religion.dds"))
if small and province:
    for number in range(VANILLA_FRAMES + 1, min(small.frames, province.frames) + 1):
        for y, (a, b) in enumerate(zip(small.frame(number), province.frame(number))):
            if any(a[i:i + 4] != b[i:i + 4] for i in range(0, len(a), 4) if a[i + 3] or b[i + 3]):
                fail(f"frame {number} differs between icon_religion_small.dds and province_view_religion.dds (row {y})")
                break

if errors:
    for message in errors:
        print("FAIL:", message)
    print(f"FAIL: {len(errors)} religion icon frame violation(s)")
    raise SystemExit(1)
print(f"PASS: {len(required)} sprites over {len(strips)} strips declare >= {highest} frames; "
      f"highest icon = {highest}; "
      + (f"frames 1-{VANILLA_FRAMES} equal vanilla" if vanilla else "vanilla comparison skipped (no install)")
      + "; added frames drawn; native rendering unverified")
