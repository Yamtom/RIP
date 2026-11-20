"""Build mission icons that are put together from existing vanilla pictures.

The painted mission icons of this mod (tools/build_core_ruthenia_icons.py, masters in
gfx/interface/missions/source/) start from a painted master. Some missions need a picture that no
master and no single vanilla icon provides, but that two vanilla icons say together. Those are built
here, pixel for pixel from the installed game, and registered in their own file,
interface/RIP_shared_mission_icons_composed.gfx, so the painted generator's registration check is untouched.

    rip_gfx_mission_confessional_balance_icon   59x63
        an Orthodox domed cathedral on the left (`mission_cathedral_cities`) and a Gothic church on the
        right (`mission_european_church`), one gold seam between them: two rites kept in balance.
        It stands for religious tolerance, confessional equilibrium and the union of the rites
        (PDL_religious_tolerance, PDL_confessional_equilibrium, VLN_confessional_balance,
        VOL_religious_settlement, uz_union_dilemma, uz_union_compromise_plus).

Measured on the installed 1.37.5: 1511 of 1565 vanilla mission icons are 59x63, uncompressed 32-bit
BGRA, no mipmaps, 14996 bytes, opaque, with no frame of their own. The donors are used at their native
size, so nothing is scaled or graded; the same recipe at the reform card's size is `confessional_balance`
in tools/build_reform_icons.py.

    python tools/build_mission_composites.py            # write the DDS
    python tools/build_mission_composites.py --check    # rebuild and compare with the checked-in DDS
    python tools/build_mission_composites.py --preview out.png --scale 5

Needs Pillow, numpy and the installed game (EU4_DIR or the usual Steam path); without the game --check
says SKIP and exits 0, and writing refuses.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from clausewitz_testlib import vanilla_root  # noqa: E402

HEADER = 128
WIDTH, HEIGHT = 59, 63
FILE_BYTES = HEADER + WIDTH * HEIGHT * 4
MISSION_DIR = "gfx/interface/missions"
HEADER_DONOR = f"{MISSION_DIR}/mission_unknown_mission.dds"
GFX_FILE = "interface/RIP_shared_mission_icons_composed.gfx"
CHECK_TOLERANCE = 3  # per channel; Pillow versions round Lanczos and blurs slightly differently
SS = 4  # supersampling of the seam
LEFT_SHIFT = 14  # the cathedral is centred in its picture; half of it must not be cut by the seam


def read_rgb(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    if image.size != (WIDTH, HEIGHT) or np.asarray(image)[..., 3].min() < 200:
        raise ValueError(f"{path.name}: a donor must be an opaque {WIDTH}x{HEIGHT} mission icon, got {image.size}")
    return image.convert("RGB")


def confessional_balance(game: Path) -> Image.Image:
    """Two churches side by side, the seam leaning a little: x = 32 at the top, x = 27 at the bottom."""
    cathedral = read_rgb(game / MISSION_DIR / "dlc_missions/third_rome/novgorod/mission_cathedral_cities.dds")
    left = Image.new("RGB", (WIDTH, HEIGHT))
    left.paste(cathedral.crop((LEFT_SHIFT, 0, WIDTH, HEIGHT)), (0, 0))  # the domes, not the empty sky beside them
    right = read_rgb(game / MISSION_DIR / "mission_european_church.dds")
    top, bottom = 32.0, 27.0
    big = (WIDTH * SS, HEIGHT * SS)
    mask = Image.new("L", big, 0)
    ImageDraw.Draw(mask).polygon([(top * SS, 0), (WIDTH * SS, 0), (WIDTH * SS, HEIGHT * SS), (bottom * SS, HEIGHT * SS)], fill=255)
    mask = mask.resize((WIDTH, HEIGHT), Image.LANCZOS)
    out = Image.composite(right, left, mask).convert("RGBA")

    seam = Image.new("RGBA", big, (0, 0, 0, 0))
    ImageDraw.Draw(seam).line([(top * SS, 0), (bottom * SS, HEIGHT * SS)], fill=(238, 204, 118, 255), width=int(1.8 * SS))
    seam = seam.resize((WIDTH, HEIGHT), Image.LANCZOS)
    shadow = seam.getchannel("A").filter(ImageFilter.GaussianBlur(1.1)).point(lambda v: int(v * 0.55))
    out = Image.composite(Image.new("RGBA", out.size, (0, 0, 0, 255)), out, shadow)
    out.alpha_composite(seam)
    out.putalpha(255)
    return out


@dataclass(frozen=True)
class Composite:
    name: str  # sprite and file stem
    make: Callable[[Path], Image.Image]
    why: str


COMPOSITES = (
    Composite("rip_gfx_mission_confessional_balance_icon", confessional_balance,
              "an Orthodox cathedral and a Gothic church side by side, one gold seam"),
)


def texture_path(composite: Composite) -> str:
    return f"{MISSION_DIR}/{composite.name}.dds"


def gfx_text() -> str:
    lines = ["spriteTypes = {"]
    for composite in COMPOSITES:
        lines += ["\tspriteType = {", f'\t\tname = "{composite.name}"', f'\t\ttexturefile = "{texture_path(composite)}"', "\t}"]
    lines.append("}")
    return "\n".join(lines) + "\n"


def build_all(game: Path) -> dict[str, np.ndarray]:
    return {texture_path(c): np.asarray(c.make(game), dtype=np.uint8) for c in COMPOSITES}


def dds_bytes(pixels: np.ndarray, header: bytes) -> bytes:
    return bytes(header) + pixels[..., [2, 1, 0, 3]].tobytes()


def preview(images: dict[str, np.ndarray], scale: int, out: Path) -> None:
    pad = 8
    sheet = Image.new("RGB", (len(images) * (WIDTH * scale + pad) + pad, HEIGHT * scale + pad * 2 + 14), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for i, (path, px) in enumerate(images.items()):
        tile = Image.fromarray(px, "RGBA").resize((WIDTH * scale, HEIGHT * scale), Image.NEAREST)
        x = pad + i * (WIDTH * scale + pad)
        sheet.paste(tile, (x, pad), tile)
        draw.text((x, pad + HEIGHT * scale + 2), Path(path).stem.replace("rip_gfx_mission_", "")[:30], fill=(230, 230, 230))
    sheet.save(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="rebuild and compare with the checked-in DDS and gfx")
    parser.add_argument("--preview", type=Path, help="write a PNG sheet instead of the DDS")
    parser.add_argument("--scale", type=int, default=5)
    args = parser.parse_args()

    game = vanilla_root()
    if game is None:
        print("SKIP: the vanilla install is needed for the donors (set EU4_DIR); nothing written")
        return 0 if args.check else 1
    images = build_all(game)

    if args.preview:
        preview(images, args.scale, args.preview)
        print(f"wrote {args.preview}")
        return 0

    header = (game / HEADER_DONOR).read_bytes()[:HEADER]
    if args.check:
        bad = 0
        for path, px in images.items():
            target = ROOT / path
            if not target.exists():
                print(f"MISSING {path}")
                bad += 1
                continue
            data = target.read_bytes()
            if len(data) != FILE_BYTES or data[:HEADER] != header:
                print(f"DIFFERS {path}: size or header is not a vanilla mission icon")
                bad += 1
                continue
            have = np.frombuffer(data[HEADER:], dtype=np.uint8).reshape(HEIGHT, WIDTH, 4)[..., [2, 1, 0, 3]]
            worst = int(np.abs(have.astype(int) - px.astype(int)).max())
            if worst > CHECK_TOLERANCE:
                print(f"DIFFERS {path}: worst channel error {worst} > {CHECK_TOLERANCE}; rerun without --check")
                bad += 1
        gfx = ROOT / GFX_FILE
        if not gfx.is_file() or gfx.read_text(encoding="utf-8").replace("\r\n", "\n") != gfx_text():
            print(f"DIFFERS {GFX_FILE}: not what the generator writes")
            bad += 1
        print("MISSION COMPOSITES FAIL" if bad else f"MISSION COMPOSITES PASS: {len(images)} icon(s) rebuild from their donors")
        return 1 if bad else 0

    for path, px in images.items():
        (ROOT / path).write_bytes(dds_bytes(px, header))
        print(f"wrote {path}")
    (ROOT / GFX_FILE).write_text(gfx_text(), encoding="utf-8", newline="\n")
    print(f"wrote {GFX_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
