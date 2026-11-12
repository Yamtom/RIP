"""Every government-reform icon of the mod must be a real 57x57 reform icon of its own.

The six Cossack/Hetmanate reform icons once shipped as byte copies of vanilla icons that
the visual audit had marked as misreads: `horde_riding` stood for both the Cossack Host and
the Free Host, an academy drew `merchant_ship`, a starshyna council drew `soldiers_6`.
Nothing failed, the game drew them. This does.

Asserted:
  - each `icon = "rip_gfx_reform_*"` that a reform writes has a `government_reform_<icon>`
    sprite, declared once, whose texture exists in the mod; no texture in
    gfx/interface/government_reform_icons/ is left without a sprite;
  - every such texture is an uncompressed 32-bit BGRA DDS, 57x57, no mipmaps, 13124 bytes,
    with the same size, pitch, pixel-format masks and caps as its siblings;
  - the 3 px frame of the six icons built by tools/build_reform_icons.py is identical across
    them, and the 51x51 picture is not (nothing painted over the frame, nothing copied);
  - no two mod reform icons are the same picture, and none is a byte copy of a vanilla one
    (needs the installed game);
  - when Pillow, numpy and the game are present, the six icons rebuild from their donors
    (`tools/build_reform_icons.py --check`).

Standard library only for the contracts above. Does not render anything; native drawing is
unverified.
"""
import importlib.util
import re
import struct
import subprocess
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, vanilla_root

ICON_DIR = "gfx/interface/government_reform_icons"
HEADER = 128
SIZE = 57
FRAME = 3
FILE_BYTES = HEADER + SIZE * SIZE * 4
# The icons built from donors by tools/build_reform_icons.py (the frame is shared by these).
BUILT = (
    "rip_gfx_reform_cossack_host_icon",
    "rip_gfx_reform_zaz_free_host_icon",
    "rip_gfx_reform_zaz_sich_brotherhood_icon",
    "rip_gfx_reform_het_starshyna_oligarchy_icon",
    "rip_gfx_reform_het_academy_enlightenment_icon",
    "rip_gfx_reform_zaz_last_sich_icon",
)
errors = []


def fail(message):
    errors.append(message)


def norm(path):
    return re.sub(r"[\\/]+", "/", path)


def read_text(path):
    return Path(path).read_bytes().decode("utf-8-sig", errors="replace")


def sprite_blocks(text):
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
        found.append((name.group(1) if name else None, norm(texture.group(1)) if texture else None))
    return found


def parse_header(data, label):
    """Fields of an uncompressed 32-bit BGRA DDS header, or None after recording why not."""
    if len(data) < HEADER or data[:4] != b"DDS ":
        fail(f"{label}: not a DDS file")
        return None
    fields = struct.unpack("<4s31I", data[:HEADER])
    height, width, mips = fields[3], fields[4], fields[7]
    fourcc, bits, r, g, b, a = fields[21], fields[22], fields[23], fields[24], fields[25], fields[26]
    if (width, height) != (SIZE, SIZE):
        fail(f"{label}: {width}x{height}, reform icons are {SIZE}x{SIZE}")
    if mips not in (0, 1):
        fail(f"{label}: {mips} mipmaps, vanilla reform icons have none")
    if fourcc != 0 or bits != 32 or (r, g, b, a) != (0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000):
        fail(f"{label}: not uncompressed 32-bit BGRA (fourcc {fourcc:#x}, {bits} bits)")
    if len(data) != FILE_BYTES:
        fail(f"{label}: {len(data)} bytes, expected {FILE_BYTES}")
    return fields


def ring_and_picture(data):
    """(frame ring bytes, picture bytes) of the pixel block, row by row."""
    pixels = data[HEADER:]
    ring, picture = bytearray(), bytearray()
    for y in range(SIZE):
        row = pixels[y * SIZE * 4:(y + 1) * SIZE * 4]
        if FRAME <= y < SIZE - FRAME:
            ring += row[:FRAME * 4] + row[(SIZE - FRAME) * 4:]
            picture += row[FRAME * 4:(SIZE - FRAME) * 4]
        else:
            ring += row
    return bytes(ring), bytes(picture)


# ---- the reforms' icons and their sprites --------------------------------------------------
used = {}
for path in sorted((ROOT / "common" / "government_reforms").glob("*.txt")):
    text = re.sub(r"#[^\r\n]*", "", read_text(path))
    for icon in re.findall(r'\bicon\s*=\s*"(rip_gfx_reform_[A-Za-z0-9_]+)"', text):
        used.setdefault(icon, []).append(path.name)

declared = {}
for path in sorted((ROOT / "interface").rglob("*.gfx")):
    for name, texture in sprite_blocks(read_text(path)):
        if name and name.startswith("government_reform_rip_gfx_reform_"):
            declared.setdefault(name, []).append((texture, path.name))

if not used:
    fail("no icon = \"rip_gfx_reform_*\" found in common/government_reforms; the parser is blind")
for icon, files in sorted(used.items()):
    sprite = f"government_reform_{icon}"
    entries = declared.get(sprite, [])
    if not entries:
        fail(f"{icon} (used in {', '.join(sorted(set(files)))}) has no {sprite} sprite in interface/*.gfx")
    elif len(entries) > 1:
        fail(f"{sprite} is declared {len(entries)} times: {', '.join(f for _, f in entries)}")
    else:
        texture = entries[0][0]
        if texture is None or not (ROOT / texture).is_file():
            fail(f"{sprite} points at a missing texture: {texture}")

declared_textures = {texture for entries in declared.values() for texture, _ in entries}
folder = sorted((ROOT / ICON_DIR).glob("*.dds"))
for path in folder:
    relative = f"{ICON_DIR}/{path.name}"
    if relative not in declared_textures:
        fail(f"{relative} has no government_reform_* sprite; the file is dead weight")
for name in BUILT:
    if not (ROOT / ICON_DIR / f"{name}.dds").is_file():
        fail(f"{ICON_DIR}/{name}.dds is missing")

# ---- the textures ----------------------------------------------------------------------------
textures = {}
for texture in sorted(declared_textures):
    path = ROOT / texture
    if path.is_file():
        data = path.read_bytes()
        if parse_header(data, texture):
            textures[texture] = data
# Bytes 32-75 are reserved (vanilla's carry an NVTT signature, the procedural tools write zeros);
# everything that changes how pixels are read - size, pitch, masks, caps - must agree.
headers = {data[:32] + data[76:HEADER] for data in textures.values()}
if len(headers) > 1:
    fail(f"{len(headers)} different DDS headers among the mod's reform icons; size, pitch, pixel format and caps should agree")

built = {name: textures.get(f"{ICON_DIR}/{name}.dds") for name in BUILT}
rings, pictures = {}, {}
for name, data in built.items():
    if data is not None and len(data) == FILE_BYTES:
        rings[name], pictures[name] = ring_and_picture(data)
if len({ring for ring in rings.values()}) > 1:
    odd = sorted(name for name, ring in rings.items() if ring != next(iter(rings.values())))
    fail("the frame ring differs between the built icons (a picture painted over it, or a different frame): "
         + ", ".join(odd))
for first in sorted(pictures):
    for second in sorted(pictures):
        if first < second and pictures[first] == pictures[second]:
            fail(f"{first} and {second} are the same picture")
for first in sorted(textures):
    for second in sorted(textures):
        if first < second and textures[first] == textures[second]:
            fail(f"{first} and {second} are byte-identical")

# ---- against the installed game --------------------------------------------------------------
vanilla = vanilla_root()
notes = []
if vanilla:
    vanilla_files = {}
    for path in (vanilla / ICON_DIR).rglob("*.dds"):
        vanilla_files.setdefault(path.read_bytes(), path)
    for texture, data in textures.items():
        twin = vanilla_files.get(data)
        if twin is not None:
            fail(f"{texture} is a byte copy of vanilla {twin.relative_to(vanilla).as_posix()}")
    if all(importlib.util.find_spec(m) for m in ("PIL", "numpy")):
        run = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / "build_reform_icons.py"), "--check"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if run.returncode != 0:
            fail("tools/build_reform_icons.py --check: " + (run.stdout + run.stderr).strip().replace("\n", " | "))
    else:
        notes.append("rebuild from donors (Pillow or numpy missing)")
else:
    notes.append("byte copies of vanilla icons and the rebuild from donors (no installed EU4)")

if errors:
    print("REFORM ICONS FAIL")
    for message in errors:
        print(" -", message)
    sys.exit(1)
print(f"REFORM ICONS PASS: {len(used)} reform icons declared and present, {len(textures)} textures "
      f"57x57, {len(BUILT)} built icons share one frame and show six different pictures")
if notes:
    print("SKIP: " + "; ".join(notes))
