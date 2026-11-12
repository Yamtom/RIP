"""Build the six Cossack/Hetmanate government-reform icons from existing painted art.

EU4 draws a government reform from a 57x57 uncompressed 32-bit DDS in
gfx/interface/government_reform_icons/, declared by a `government_reform_<icon>` sprite.
Measured on the installed 1.37.5 (346 files; 312 are exactly this, the rest are mipmapped,
DXT5 or a pixel off and are not used as a model):

    57x57, no mipmaps, 128-byte header, BGRA, 13124 bytes
    a 3 px frame on every side (bronze rim, crimson, dark crimson) and a 51x51 picture
    inside it, x and y 3..53; the picture is painted to the edge of that window
    picture means over 334 icons (inside the frame): saturation 106/255 (p10-p90 64-150),
    value 132/255 (89-167), luminance spread 52

The six icons were once byte copies of vanilla icons that the visual audit itself had
marked as misreads (`horde_riding` twice, `merchant_ship`, `soldiers_6`, `fist_in_air`,
`dlc/domination/mountain_fort`), so a Cossack Host and a Free Host drew the same picture and
an academy drew a trading ship. Each is now cropped from painted art that already ships in
EU4 or in this mod and says what the reform is:

    cossack_host             mission_recruit_the_cossacks   a Cossack rider with a lance and pennant on the steppe
    zaz_free_host            mission_cossack_cavalry        a rider charging under a storm sky
    zaz_sich_brotherhood     startup image of the Cossacks  the circle at the rada table, the quill and the paper
    het_starshyna_oligarchy  DLC banner "The Cossacks"      a grey-capped elder beside a crested officer
    het_academy_enlightenment petro_mohyla (this mod)       the Kyiv academy courtyard and its dome
    zaz_last_sich            great_project_zaporozhian_sich (this mod)   the timber watchtower and palisade of the Sich

The prompts in docs/core_ruthenia_visual_prompts.md stay the brief for a painter: none of
the donors holds a mace, a seal ring or an astrolabe, so these are the closest existing
pictures, not the finished art the prompts describe.

Pipeline for one icon (all numbers below are constants, nothing is tuned by eye per icon):

    crop the donor to a square -> resize to 51x51 (Lanczos) -> light unsharp mask (45%, radius 0.7)
    -> pull picture saturation and value into vanilla's p10-p90 band, stretch contrast
       only when the luminance spread is under 42 -> paste into the vanilla frame

The frame is the per-pixel median of every uncompressed vanilla reform icon, so it is the
common frame and carries no one icon's art. Pixels of the ring keep their alpha.

    python tools/build_reform_icons.py            # write the six DDS
    python tools/build_reform_icons.py --check    # rebuild and compare with the checked-in DDS
    python tools/build_reform_icons.py --preview out.png --scale 5

Needs Pillow, numpy and the installed game (EU4_DIR or the usual Steam path); without the
game --check says SKIP and exits 0, and writing refuses.
"""
from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from clausewitz_testlib import vanilla_root  # noqa: E402

HEADER = 128
SIZE = 57
FRAME = 3
ART = SIZE - 2 * FRAME  # 51
FILE_BYTES = HEADER + SIZE * SIZE * 4
ICON_DIR = "gfx/interface/government_reform_icons"
HEADER_DONOR = f"{ICON_DIR}/horde_riding.dds"

# Vanilla picture statistics (HSV, 0-255) the grade pulls into, never beyond.
SAT_BAND = (75.0, 140.0)
VAL_BAND = (100.0, 165.0)
MIN_SPREAD = 42.0
MAX_SAT_GAIN = 1.5
MAX_STRETCH = 1.2
CHECK_TOLERANCE = 3  # per channel; Pillow versions round Lanczos and HSV slightly differently


@dataclass(frozen=True)
class Icon:
    name: str  # the file is rip_gfx_reform_<name>_icon.dds
    source: str  # path inside the donor root
    vanilla: bool  # True: under the installed game; False: under this mod
    crop: tuple[int, int, int, int]  # left, top, right, bottom of a SQUARE in the donor
    why: str


ICONS = (
    Icon("cossack_host", "gfx/interface/missions/dlc_missions/third_rome/russian_minors/mission_recruit_the_cossacks.dds",
         True, (3, 9, 57, 63), "a Cossack rider with a lance and a pennant on the open steppe"),
    Icon("zaz_free_host", "gfx/interface/missions/mission_cossack_cavalry.dds",
         True, (0, 4, 59, 63), "an elite rider charging under a storm sky"),
    Icon("zaz_sich_brotherhood", "gfx/interface/sub/startup/subscription_startup_image_7_cossacks.dds",
         True, (205, 75, 545, 415), "the circle round the rada table: the quill, the paper, the oath"),
    Icon("het_starshyna_oligarchy", "gfx/dlc_pictures/dlc046_the_cossacks_banner.dds",
         True, (398, 52, 538, 192), "a grey-capped elder beside a crested officer: the senior ranks"),
    Icon("het_academy_enlightenment", "gfx/interface/missions/petro_mohyla.dds",
         False, (0, 4, 59, 63), "the Kyiv academy courtyard and its dome"),
    Icon("zaz_last_sich", "gfx/interface/great_projects/great_project_zaporozhian_sich.dds",
         False, (165, 15, 295, 145), "the timber watchtower and palisade of the Sich"),
)


def texture_path(icon: Icon) -> str:
    return f"{ICON_DIR}/rip_gfx_reform_{icon.name}_icon.dds"


def uncompressed_vanilla_icons(game: Path) -> list[Path]:
    """Every 57x57 uncompressed reform icon of the install, frames included, overlays and highlights not."""
    found = []
    for path in sorted((game / ICON_DIR).rglob("*.dds")):
        if "overlay" in path.name or "highlight" in path.name:
            continue
        head = path.read_bytes()[:HEADER]
        height, width = struct.unpack("<2I", head[12:20])
        if (width, height) == (SIZE, SIZE) and head[84:88] == b"\0\0\0\0" and path.stat().st_size == FILE_BYTES:
            found.append(path)
    return found


def read_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def frame_ring(game: Path) -> np.ndarray:
    """The common frame: the per-pixel median over all vanilla reform icons, uint8 SIZE x SIZE x 4."""
    stack = np.stack([np.asarray(read_rgba(p), dtype=np.uint8) for p in uncompressed_vanilla_icons(game)])
    return np.median(stack, axis=0).round().astype(np.uint8)


def luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def pull_into_band(picture: Image.Image) -> Image.Image:
    """Saturation and value into vanilla's p10-p90 band (never past it), contrast up only if flat."""
    hsv = np.asarray(picture.convert("HSV"), dtype=np.float64)
    sat, val = hsv[..., 1] / 255.0, hsv[..., 2] / 255.0

    mean_sat = sat.mean() * 255.0
    if mean_sat < SAT_BAND[0]:
        sat = np.clip(sat * min(SAT_BAND[0] / max(mean_sat, 1.0), MAX_SAT_GAIN), 0.0, 1.0)
    elif mean_sat > SAT_BAND[1]:
        sat = sat * (SAT_BAND[1] / mean_sat)

    mean_val = val.mean() * 255.0
    target = min(max(mean_val, VAL_BAND[0]), VAL_BAND[1])
    if abs(target - mean_val) > 0.5:  # bisect a gamma: val ** g has the target mean
        lo, hi = 0.2, 3.0
        for _ in range(40):
            mid = (lo + hi) / 2.0
            if (val ** mid).mean() * 255.0 > target:
                lo = mid
            else:
                hi = mid
        val = val ** ((lo + hi) / 2.0)

    out = np.stack([hsv[..., 0], sat * 255.0, val * 255.0], axis=-1)
    rgb = np.asarray(Image.fromarray(np.clip(out.round(), 0, 255).astype(np.uint8), "HSV").convert("RGB"), dtype=np.float64)

    spread = luminance(rgb).std()
    if spread < MIN_SPREAD:
        stretch = min(MIN_SPREAD / max(spread, 1.0), MAX_STRETCH)
        centre = luminance(rgb).mean()
        rgb = np.clip((rgb - centre) * stretch + centre, 0.0, 255.0)
    return Image.fromarray(np.clip(rgb.round(), 0, 255).astype(np.uint8), "RGB")


def make_picture(icon: Icon, root: Path) -> Image.Image:
    source = read_rgba(root / icon.source)
    left, top, right, bottom = icon.crop
    if right - left != bottom - top:
        raise ValueError(f"{icon.name}: crop {icon.crop} is not square")
    piece = source.crop(icon.crop)
    if np.asarray(piece)[..., 3].min() != 255:
        raise ValueError(f"{icon.name}: crop {icon.crop} reaches transparent pixels of {icon.source}")
    picture = piece.convert("RGB").resize((ART, ART), Image.LANCZOS)
    picture = picture.filter(ImageFilter.UnsharpMask(radius=0.7, percent=45, threshold=3))
    return pull_into_band(picture)


def build(icon: Icon, game: Path, ring: np.ndarray) -> np.ndarray:
    """SIZE x SIZE x 4 uint8, RGBA, the frame ring with the picture inside."""
    out = ring.copy()
    picture = np.asarray(make_picture(icon, game if icon.vanilla else ROOT), dtype=np.uint8)
    out[FRAME:SIZE - FRAME, FRAME:SIZE - FRAME, :3] = picture
    out[FRAME:SIZE - FRAME, FRAME:SIZE - FRAME, 3] = 255
    return out


def dds_bytes(pixels: np.ndarray, header: bytes) -> bytes:
    """Header of a vanilla icon (same pixel format, masks, flags) and BGRA pixels."""
    return bytes(header) + pixels[..., [2, 1, 0, 3]].tobytes()


def build_all(game: Path) -> dict[str, np.ndarray]:
    ring = frame_ring(game)
    return {texture_path(icon): build(icon, game, ring) for icon in ICONS}


def preview(images: dict[str, np.ndarray], scale: int, out: Path) -> None:
    pad = 8
    cell = SIZE * scale
    sheet = Image.new("RGB", (len(images) * (cell + pad) + pad, cell + pad * 2 + 14), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for i, (path, px) in enumerate(images.items()):
        tile = Image.fromarray(px, "RGBA").resize((cell, cell), Image.NEAREST)
        x = pad + i * (cell + pad)
        sheet.paste(tile, (x, pad), tile)
        draw.text((x, pad + cell + 2), Path(path).stem.replace("rip_gfx_reform_", "")[:28], fill=(230, 230, 230))
    sheet.save(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="rebuild and compare with the checked-in DDS")
    parser.add_argument("--preview", type=Path, help="write a PNG sheet instead of the DDS")
    parser.add_argument("--scale", type=int, default=5)
    args = parser.parse_args()

    game = vanilla_root()
    if game is None:
        print("SKIP: the vanilla install is needed for the donors and the frame (set EU4_DIR); nothing written")
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
                print(f"DIFFERS {path}: size or header is not a vanilla reform icon")
                bad += 1
                continue
            have = np.frombuffer(data[HEADER:], dtype=np.uint8).reshape(SIZE, SIZE, 4)[..., [2, 1, 0, 3]]
            worst = int(np.abs(have.astype(int) - px.astype(int)).max())
            if worst > CHECK_TOLERANCE:
                print(f"DIFFERS {path}: worst channel error {worst} > {CHECK_TOLERANCE}; rerun without --check")
                bad += 1
        print("REFORM ICONS FAIL" if bad else f"REFORM ICONS PASS: {len(images)} icons rebuild from their donors")
        return 1 if bad else 0

    for path, px in images.items():
        (ROOT / path).write_bytes(dds_bytes(px, header))
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
