"""Build and verify the 31-frame religion strips (Russian Orthodoxy 30, Greek Catholicism 31).

EU4 draws a religion from a strip of equal square frames indexed by `icon = N`
in common/religions. Vanilla ships FOUR such textures, not three:

    icon_religion.dds            64x64  x29   GFX_icon_religion
    country_icon_religion.dds    64x64  x29   GFX_country_icon_religion
    icon_religion_small.dds      32x32  x29   GFX_icon_religion_small, GFX_religion_icon_strip
    province_view_religion.dds   32x32  x29   GFX_province_view_religion

The first three were extended to 31 frames by hand (commit 38ec5210) and are
never rewritten by this tool. The fourth - the one the advisor rows, the HRE
window, holy-site blessings, the colonisation panel and the map conversion icon
draw - was left at 29, so a Greek Catholic or Russian Orthodox subject drew an
empty circle. This tool generates it:

    frames 1..29  the vanilla file, byte for byte
    frame 30      vanilla frame 4 (Orthodox cross), purple shifted to oak
    frame 31      vanilla frame 1 (Catholic crucifix), gold shifted to crimson

with the SAME recolour documented in interface/rip_religion_icons.gfx. Pixels
with alpha 0 keep the donor's bytes, so bilinear sampling under a scale factor
(advisor icons draw at 0.9) bleeds the same colour vanilla's own frames do.

The recolour was recovered by reproducing the shipped frames of the other three
strips: every one of them is rebuilt bit-exactly from vanilla by `extend()`
below, which is also how the legacy strips are verified without being touched.
The one parameter the .gfx comment does not state is the grey floor - pixels
with saturation under 0.08 are left alone, which is what keeps the metal rim and
the outline at vanilla's shading.

Needs the installed game (EU4_DIR or the usual Steam path); without it --check
falls back to structural checks and says so. Standard library only.
"""
from __future__ import annotations

import argparse
import colorsys
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from clausewitz_testlib import vanilla_root  # noqa: E402

HEADER = 128
VANILLA_FRAMES = 29
MOD_FRAMES = 31
MIN_SATURATION = 0.08  # below this a pixel is metal or outline, not coloured paint

# frame -> (donor frame in the vanilla strip, recolour). Hues are degrees.
RECOLOURS = {
    30: dict(donor=4, window=(215, 335), hue=26, sat_mul=1.50, sat_add=0.14, sat_cap=0.62, val_mul=0.90),
    31: dict(donor=1, window=(15, 70), hue=350, sat_mul=1.15, sat_add=0.10, sat_cap=0.72, val_mul=0.92),
}

# (file under gfx/interface, frame edge in pixels, generated here?)
STRIPS = (
    ("icon_religion.dds", 64, False),
    ("country_icon_religion.dds", 64, False),
    ("icon_religion_small.dds", 32, False),
    ("province_view_religion.dds", 32, True),
)


class Strip:
    """An uncompressed 32-bit BGRA DDS strip of square frames, no mipmaps."""

    def __init__(self, data: bytes, label: str):
        if data[:4] != b"DDS " or len(data) < HEADER:
            raise ValueError(f"{label}: not a DDS file")
        fields = struct.unpack("<4s31I", data[:HEADER])
        self.header = bytearray(data[:HEADER])
        self.height, self.width = fields[3], fields[4]
        pixel_format = fields[19:27]  # size, flags, fourcc, bits, R, G, B, A masks
        if pixel_format[3] != 32 or pixel_format[2] != 0 or pixel_format[4:] != (0xFF0000, 0xFF00, 0xFF, 0xFF000000):
            raise ValueError(f"{label}: not uncompressed 32-bit BGRA")
        if fields[7] > 1:
            raise ValueError(f"{label}: has mipmaps")
        self.pixels = data[HEADER:]
        if len(self.pixels) != self.width * self.height * 4:
            raise ValueError(f"{label}: {len(self.pixels)} pixel bytes, expected {self.width * self.height * 4}")
        self.label = label

    @classmethod
    def read(cls, path: Path) -> "Strip":
        return cls(path.read_bytes(), str(path))

    @property
    def frames(self) -> int:
        return self.width // self.height

    def row(self, y: int, x0: int, width: int) -> bytes:
        start = (y * self.width + x0) * 4
        return bytes(self.pixels[start:start + width * 4])

    def frame(self, number: int) -> list[bytes]:
        """Rows of 1-based frame `number`."""
        size = self.height
        return [self.row(y, (number - 1) * size, size) for y in range(size)]


def to_byte(value: float) -> int:
    return max(0, min(255, int(math.floor(value * 255 + 0.5))))  # half up, not banker's


def recolour(rows: list[bytes], spec: dict) -> list[bytes]:
    lo, hi = spec["window"]
    out = []
    for row in rows:
        pixels = bytearray(row)
        for i in range(0, len(pixels), 4):
            b, g, r, a = pixels[i:i + 4]
            if a == 0:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if not (lo <= h * 360 <= hi and s >= MIN_SATURATION):
                continue
            nr, ng, nb = colorsys.hsv_to_rgb(
                spec["hue"] / 360, min(spec["sat_cap"], s * spec["sat_mul"] + spec["sat_add"]), v * spec["val_mul"])
            pixels[i:i + 3] = bytes((to_byte(nb), to_byte(ng), to_byte(nr)))
        out.append(bytes(pixels))
    return out


def extend(vanilla: Strip) -> bytes:
    """The vanilla strip plus frames 30 and 31, as a complete DDS file."""
    if vanilla.frames != VANILLA_FRAMES or vanilla.width != VANILLA_FRAMES * vanilla.height:
        raise ValueError(f"{vanilla.label}: expected {VANILLA_FRAMES} square frames, found {vanilla.width}x{vanilla.height}")
    added = [recolour(vanilla.frame(RECOLOURS[n]["donor"]), RECOLOURS[n]) for n in (30, 31)]
    header = bytearray(vanilla.header)
    width = MOD_FRAMES * vanilla.height
    struct.pack_into("<I", header, 16, width)
    struct.pack_into("<I", header, 20, width * 4)  # pitch
    body = bytearray()
    for y in range(vanilla.height):
        body += vanilla.row(y, 0, vanilla.width) + added[0][y] + added[1][y]
    return bytes(header) + bytes(body)


def visible(rows: list[bytes]) -> int:
    return sum(1 for row in rows for i in range(3, len(row), 4) if row[i])


def structural(strip: Strip) -> list[str]:
    """What must hold of a mod strip with or without a vanilla install."""
    problems = []
    if strip.frames != MOD_FRAMES or strip.width != MOD_FRAMES * strip.height:
        problems.append(f"{strip.width}x{strip.height}, expected {MOD_FRAMES} square frames")
        return problems
    area = strip.height * strip.height
    for number in (30, 31):
        count = visible(strip.frame(number))
        if count < area // 20:
            problems.append(f"frame {number} has only {count} visible pixels")
    if strip.frame(30) == strip.frame(31):
        problems.append("frames 30 and 31 are identical")
    return problems


def vanilla_equal(mod: Strip, vanilla: Strip) -> list[str]:
    return [f"frame {n} differs from vanilla" for n in range(1, VANILLA_FRAMES + 1)
            if mod.frame(n) != vanilla.frame(n)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="write nothing; exit 1 if the generated strip is stale or a shipped strip is wrong")
    args = parser.parse_args()
    root = vanilla_root()
    bad: list[str] = []
    stale: list[str] = []
    wrote: list[str] = []
    for name, size, generated in STRIPS:
        target = ROOT / "gfx" / "interface" / name
        rel = target.relative_to(ROOT).as_posix()
        if root is None:
            # Nothing to rebuild from: judge only the shape of what is on disk.
            if not target.exists():
                (stale if generated else bad).append(rel)
                print(f"MISSING {rel}")
                continue
            problems = structural(Strip.read(target))
            print(("BAD   " if problems else "SKIP  ") + f"{rel}: no vanilla to compare; structural only" +
                  ("".join("; " + p for p in problems)))
            bad.extend([rel] if problems else [])
            continue
        donor = Strip.read(root / "gfx" / "interface" / name)
        if donor.height != size:
            raise SystemExit(f"{name}: vanilla frame edge {donor.height}, tool expects {size}")
        expected = extend(donor)
        shipped = target.read_bytes() if target.exists() else None
        if shipped == expected:
            print(f"OK    {rel}: {MOD_FRAMES} frames, rebuilt bit-exactly from vanilla ({len(expected)} bytes)")
            continue
        if generated:
            stale.append(rel)
            if args.check:
                print(f"STALE {rel}: " + ("missing" if shipped is None else "differs from the vanilla-derived strip"))
            else:
                target.write_bytes(expected)
                wrote.append(rel)
                print(f"WROTE {rel}: {MOD_FRAMES} frames ({len(expected)} bytes)")
            continue
        # A shipped strip this tool never rewrites. If it is no longer reproducible,
        # insist only on the contract: vanilla frames untouched, ours present.
        if shipped is None:
            bad.append(rel)
            print(f"BAD   {rel}: missing")
            continue
        mod = Strip(shipped, rel)
        problems = structural(mod) + vanilla_equal(mod, donor)
        if problems:
            bad.append(rel)
            print(f"BAD   {rel}: " + "; ".join(problems))
        else:
            print(f"OK    {rel}: not bit-exact to the recolour, but frames 1-29 equal vanilla and 30-31 are present")
    state = "BAD" if bad else "STALE" if args.check and stale else "GENERATED" if wrote else "OK"
    print(f"{state}: religion strips; {len(stale)} stale, {len(wrote)} written, {len(bad)} bad"
          + ("" if root is not None else "; vanilla install not found, comparison skipped"))
    return 1 if (bad or (args.check and stale)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
