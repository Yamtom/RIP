"""Build 32-frame EU4 religion strips and standalone DDS reference exports.

Frames 1-29 preserve installed vanilla pixels byte for byte. Frames 30-32
use transparent PNG masters from gfx/interface/religion_icons/source.
Four BGRA strips serve five sprites at native 64px and 32px sizes.
Masters are fitted with premultiplied-alpha resampling and transparent margins.
Requires Pillow and installed EU4; --check verifies reproducibility.
Without vanilla only structural checks are possible, explicitly reported.
The legacy recolour helpers remain available to compare previous artwork.
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
MOD_FRAMES = 32
MIN_SATURATION = 0.08  # below this a pixel is metal or outline, not coloured paint

# frame -> (donor frame in the vanilla strip, recolour). Hues are degrees.
RECOLOURS = {
    30: dict(donor=4, window=(215, 335), hue=26, sat_mul=1.50, sat_add=0.14, sat_cap=0.62, val_mul=0.90),
    31: dict(donor=4, window=(215, 335), hue=350, sat_mul=1.15, sat_add=0.10, sat_cap=0.72, val_mul=0.92),
    32: dict(donor=4, window=(215, 335), hue=150, sat_mul=1.20, sat_add=0.10, sat_cap=0.65, val_mul=0.85),
}

# (file under gfx/interface, frame edge in pixels, generated here?)
STRIPS = (
    ("icon_religion.dds", 64, True),
    ("country_icon_religion.dds", 64, True),
    ("icon_religion_small.dds", 32, True),
    ("province_view_religion.dds", 32, True),
)

STANDALONE_FRAMES = {'russian_orthodox': 30, 'greek_catholic': 31, 'old_believers': 32}


def artwork_frame(number: int, size: int) -> list[bytes]:
    """Export transparent masters at native UI size using premultiplied alpha."""
    from PIL import Image
    faith = next(name for name, frame in STANDALONE_FRAMES.items() if frame == number)
    path = ROOT / f'gfx/interface/religion_icons/source/{faith}_v2.png'
    with Image.open(path) as source:
        image = source.convert('RGBA')
    alpha = image.getchannel('A')
    if alpha.getextrema()[0] != 0:
        raise ValueError(f'{path}: master must have transparent background')
    bbox = alpha.point(lambda a: 255 if a >= 16 else 0).getbbox()
    if bbox is None:
        raise ValueError(f'{path}: empty master')
    image = image.crop(bbox)
    scale = min(round(size * 0.60) / image.width, round(size * 0.84) / image.height)
    dims = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    image = image.convert('RGBa').resize(dims, Image.Resampling.LANCZOS).convert('RGBA')
    canvas = Image.new('RGBA', (size, size))
    canvas.paste(image, ((size - dims[0]) // 2, (size - dims[1]) // 2))
    data = canvas.tobytes('raw', 'BGRA')
    return [data[y * size * 4:(y + 1) * size * 4] for y in range(size)]


def standalone(strip: 'Strip', number: int) -> bytes:
    """Export a preview/source-reference DDS with the same native BGRA layout."""
    header = bytearray(strip.header)
    struct.pack_into('<I', header, 16, strip.height)
    struct.pack_into('<I', header, 20, strip.height * 4)
    return bytes(header) + b''.join(strip.frame(number))


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
    """The vanilla strip plus frames 30 through 32, as a complete DDS file."""
    if vanilla.frames != VANILLA_FRAMES or vanilla.width != VANILLA_FRAMES * vanilla.height:
        raise ValueError(f"{vanilla.label}: expected {VANILLA_FRAMES} square frames, found {vanilla.width}x{vanilla.height}")
    added = [artwork_frame(n, vanilla.height) for n in sorted(RECOLOURS)]
    header = bytearray(vanilla.header)
    width = MOD_FRAMES * vanilla.height
    struct.pack_into("<I", header, 16, width)
    struct.pack_into("<I", header, 20, width * 4)  # pitch
    body = bytearray()
    for y in range(vanilla.height):
        body += vanilla.row(y, 0, vanilla.width) + b''.join(frame[y] for frame in added)
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
    for number in sorted(RECOLOURS):
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
    # These individual files are reference exports; EU4 reads the strips above.
    icon_strip = ROOT / 'gfx/interface/icon_religion.dds'
    if icon_strip.exists():
        strip = Strip.read(icon_strip)
        for faith, number in STANDALONE_FRAMES.items():
            target = ROOT / f'gfx/interface/religion_icons/{faith}.dds'
            expected = standalone(strip, number)
            if not target.exists() or target.read_bytes() != expected:
                stale.append(target.relative_to(ROOT).as_posix())
                if not args.check:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(expected)
                    wrote.append(target.relative_to(ROOT).as_posix())
                else:
                    print(f'STALE {target.relative_to(ROOT)}: standalone export differs from live frame')
    state = "BAD" if bad else "STALE" if args.check and stale else "GENERATED" if wrote else "OK"
    print(f"{state}: religion strips; {len(stale)} stale, {len(wrote)} written, {len(bad)} bad"
          + ("" if root is not None else "; vanilla install not found, comparison skipped"))
    return 1 if (bad or (args.check and stale)) else 0


if __name__ == "__main__":
    raise SystemExit(main())
