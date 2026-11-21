"""Every mission of the mod must draw a picture that exists, and no slot may fall back to the "?".

Six missions - `uz_identity_branching_1..3` and `chr_identity_branching_1..3` - shipped with
vanilla's `mission_unknown_mission`, a question mark, for the identity branch the player has not
taken. The audit (docs/core_ruthenia_visual_audit.md) listed them as missing; nothing failed.

Asserted:
  - no mission file of the mod writes `icon = mission_unknown_mission`;
  - every `icon = X` of the mod's missions/*.txt names a sprite that the mod or the installed
    game declares (the installed game is needed for the vanilla half; without it only the mod's
    own names are verified, and the rest is listed as unverified);
  - every sprite the mod declares for a mission picture sits in gfx/interface/missions/, exists,
    is an uncompressed 32-bit BGRA 59x63 DDS (14996 bytes) with no mipmaps, fully opaque, and is
    declared once;
  - the six locked-branch sprites exist, are the ones those six missions use, show six different
    pictures, and none is a byte copy of a vanilla icon;
  - every sprite of interface/RIP_shared_mission_icons_composed.gfx is used by a mission and, when Pillow,
    numpy and the game are present, rebuilds from its donors
    (`tools/build_mission_composites.py --check`).

Standard library only for the contracts above. Does not render anything; native drawing is unverified.
"""
import importlib.util
import re
import struct
import subprocess
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, vanilla_root

MISSION_DIR = "gfx/interface/missions"
HEADER = 128
WIDTH, HEIGHT = 59, 63
FILE_BYTES = HEADER + WIDTH * HEIGHT * 4
# (mission, sprite) - the audit's ids; the missions must use exactly these.
LOCKED = {
    "uz_identity_branching_1": "rip_gfx_mission_uzh_identity_branch_locked_1_icon",
    "uz_identity_branching_2": "rip_gfx_mission_uzh_identity_branch_locked_2_icon",
    "uz_identity_branching_3": "rip_gfx_mission_uzh_identity_branch_locked_3_icon",
    "chr_identity_branching_1": "rip_gfx_mission_chr_identity_branch_locked_1_icon",
    "chr_identity_branching_2": "rip_gfx_mission_chr_identity_branch_locked_2_icon",
    "chr_identity_branching_3": "rip_gfx_mission_chr_identity_branch_locked_3_icon",
}
errors = []


def fail(message):
    errors.append(message)


def read_text(path):
    return Path(path).read_bytes().decode("utf-8-sig", errors="replace")


def strip_comments(text):
    return re.sub(r"#[^\r\n]*", "", text)


def sprites(text):
    """(name, texture) of every spriteType block; flat blocks, comments removed."""
    text = strip_comments(text)
    found = []
    for match in re.finditer(r"\bspriteType\s*=\s*\{", text):
        depth, i = 1, match.end()
        while depth and i < len(text):
            depth += (text[i] == "{") - (text[i] == "}")
            i += 1
        body = text[match.end():i - 1]
        name = re.search(r'\bname\s*=\s*"([^"]+)"', body)
        texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', body)
        found.append((name.group(1) if name else None,
                      re.sub(r"[\\/]+", "/", texture.group(1)) if texture else None))
    return found


def declared(root):
    out = []
    for path in sorted((root / "interface").rglob("*.gfx")):
        out.extend((name, texture, path.name) for name, texture in sprites(read_text(path)))
    return out


def mission_icons():
    """{mission_or_None: [(icon, file)]} - the icon of each mission block, by name where it has one."""
    found = {}
    for path in sorted((ROOT / "missions").glob("*.txt")):
        text = strip_comments(read_text(path))
        owner = None
        for token in re.finditer(r"(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{|\bicon\s*=\s*\"?([^\s\"}]+)\"?", text):
            if token.group(1):
                owner = token.group(1)
            else:
                found.setdefault(owner, []).append((token.group(2), path.name))
    return found


def check_dds(data, label):
    if len(data) != FILE_BYTES or data[:4] != b"DDS ":
        fail(f"{label}: {len(data)} bytes, expected a {FILE_BYTES}-byte DDS")
        return False
    fields = struct.unpack("<4s31I", data[:HEADER])
    height, width, mips = fields[3], fields[4], fields[7]
    fourcc, bits, masks = fields[21], fields[22], fields[23:27]
    if (width, height) != (WIDTH, HEIGHT):
        fail(f"{label}: {width}x{height}, mission icons are {WIDTH}x{HEIGHT}")
    if mips not in (0, 1):
        fail(f"{label}: {mips} mipmaps, vanilla mission icons have none")
    if fourcc != 0 or bits != 32 or masks != (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
        fail(f"{label}: not uncompressed 32-bit BGRA")
    if min(data[HEADER + 3::4]) != 255:
        fail(f"{label}: has transparent pixels; vanilla mission icons are opaque")
    return True


mod_sprites = declared(ROOT)
by_name = {}
for name, texture, source in mod_sprites:
    by_name.setdefault(name, []).append((texture, source))
vanilla = vanilla_root()
vanilla_names = {name for name, _, _ in declared(vanilla)} if vanilla else set()

# ---- what the missions use ---------------------------------------------------------------------
icons = mission_icons()
all_used = {icon for entries in icons.values() for icon, _ in entries}
if len(all_used) < 50:
    fail(f"only {len(all_used)} distinct mission icons found in missions/*.txt; the parser is blind")
if "mission_unknown_mission" in all_used:
    users = sorted({owner for owner, entries in icons.items() for icon, _ in entries
                    if icon == "mission_unknown_mission"})
    fail("mission_unknown_mission (the vanilla question mark) is still used by: " + ", ".join(map(str, users)))
unverified = []
for icon in sorted(all_used):
    if icon in by_name:
        continue
    if not vanilla:
        unverified.append(icon)
    elif icon not in vanilla_names:
        files = sorted({f for entries in icons.values() for i, f in entries if i == icon})
        fail(f"icon {icon} ({', '.join(files)}) is declared neither by the mod nor by the installed game")

# ---- the mod's mission sprites ---------------------------------------------------------------
textures = {}
for name, entries in sorted(by_name.items()):
    mission_entries = [(t, s) for t, s in entries if t and t.startswith(MISSION_DIR + "/")]
    if not mission_entries:
        continue
    if len(entries) > 1:
        fail(f"sprite {name} is declared {len(entries)} times: {', '.join(s for _, s in entries)}")
    texture = mission_entries[0][0]
    path = ROOT / texture
    if not path.is_file():
        fail(f"sprite {name} points at a missing texture: {texture}")
        continue
    data = path.read_bytes()
    if check_dds(data, texture):
        textures[name] = data

# ---- the six locked-branch icons -------------------------------------------------------------
for mission, sprite in sorted(LOCKED.items()):
    used = [icon for icon, _ in icons.get(mission, [])]
    if used != [sprite]:
        fail(f"{mission} uses {used or 'no icon'}, expected {sprite}")
    if sprite not in textures:
        fail(f"{sprite} is not a declared, valid texture")
sixes = {sprite: textures[sprite] for sprite in LOCKED.values() if sprite in textures}
for first in sorted(sixes):
    for second in sorted(sixes):
        if first < second and sixes[first] == sixes[second]:
            fail(f"{first} and {second} are the same picture")

# ---- icons composed from vanilla pictures (tools/build_mission_composites.py) -------------
composed_gfx = ROOT / "interface" / "RIP_shared_mission_icons_composed.gfx"
composed = [name for name, _ in sprites(read_text(composed_gfx))] if composed_gfx.is_file() else []
for sprite in composed:
    if sprite not in textures:
        fail(f"{sprite} is not a declared, valid texture")
    if sprite not in all_used:
        fail(f"{sprite} is composed but no mission uses it")

notes = []
if vanilla:
    twins = {}
    for path in (vanilla / MISSION_DIR).rglob("*.dds"):
        twins.setdefault(path.read_bytes(), path)
    for sprite, data in sixes.items():
        twin = twins.get(data)
        if twin is not None:
            fail(f"{sprite} is a byte copy of vanilla {twin.relative_to(vanilla).as_posix()}")
    if all(importlib.util.find_spec(m) for m in ("PIL", "numpy")):
        run = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "build_mission_composites.py"), "--check"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if run.returncode != 0:
            fail("tools/build_mission_composites.py --check: " + (run.stdout + run.stderr).strip().replace("\n", " | "))
    else:
        notes.append("rebuild of the composed icons (Pillow or numpy missing)")
else:
    notes.append(f"{len(unverified)} vanilla icon names, byte copies of vanilla icons and the rebuild of the composed "
                 "icons (no installed EU4)")

if errors:
    print("MISSION ICONS FAIL")
    for message in errors:
        print(" -", message)
    sys.exit(1)
print(f"MISSION ICONS PASS: {len(all_used)} distinct mission icons resolve, {len(textures)} mod textures "
      f"{WIDTH}x{HEIGHT}, the six locked-branch missions each draw their own picture")
if notes:
    print("SKIP: " + "; ".join(notes))
