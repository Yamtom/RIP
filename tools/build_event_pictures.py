"""Compile the original event illustrations into 512x132 legacy DDS textures.

Requires Pillow. Use --check to compare the generated textures with the files
already in the mod.
"""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import struct

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "event_pictures"
TARGET_DIR = ROOT / "gfx" / "event_pictures" / "event_pictures_rip"
SIZE = (512, 132)

# Each original has a different lower edge to its illustrated band.
ART = {
    "south_ukraine_zaporozhian_autonomy_charter": (0.785, 0.4),
    "south_ukraine_imperial_frontier_reform": (0.785, 0.25),
    "hetmanate_little_russian_collegium": (0.815, 0.5),
    "kyiv_orthodox_printing_press": (0.845, 0.5),
    "jewish_estate_invite_merchants": (0.775, 0.5),
}


def compile_art(source: Path, bottom: float, horizontal_center: float) -> bytes:
    with Image.open(source) as image:
        if image.format != "PNG" or image.width < SIZE[0] or image.height < SIZE[1]:
            raise ValueError(f"{source}: expected a PNG at least {SIZE[0]}x{SIZE[1]}")
        crop = image.convert("RGB").crop(
            (0, round(image.height * 0.14), image.width, round(image.height * bottom))
        )
        framed = ImageOps.fit(
            crop, SIZE, method=Image.Resampling.LANCZOS, centering=(horizontal_center, 0.5)
        )
        output = BytesIO()
        framed.convert("RGBA").save(output, format="DDS")

    data = output.getvalue()
    if (
        len(data) != 128 + SIZE[0] * SIZE[1] * 4
        or data[:4] != b"DDS "
        or data[84:88] != b"\0\0\0\0"
        or struct.unpack_from("<I", data, 88)[0] != 32
    ):
        raise ValueError(f"{source}: DDS encoder did not produce legacy 32-bit RGBA")
    with Image.open(BytesIO(data)) as decoded:
        if decoded.size != SIZE or decoded.convert("RGBA").getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"{source}: generated DDS failed size or opacity validation")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report stale output without writing it")
    args = parser.parse_args()
    stale = []
    for stem, (bottom, horizontal_center) in ART.items():
        source = SOURCE_DIR / f"{stem}.png"
        target = TARGET_DIR / f"rip_gfx_event_{stem}_art_eventPicture.dds"
        data = compile_art(source, bottom, horizontal_center)
        if not target.is_file() or target.read_bytes() != data:
            stale.append(target.relative_to(ROOT))
            if not args.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
    if args.check and stale:
        for path in stale:
            print(f"STALE: {path}")
        return 1
    print(f"{'CHECKED' if args.check else 'GENERATED'}: {len(ART)} event pictures; {len(stale)} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
