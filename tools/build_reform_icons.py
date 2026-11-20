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
    zaz_last_sich            great_project_zaporozhian_sich (this mod)   the timber watchtower and palisade of the Sich

The Sich donor is a picture of this mod that other work may repaint, so its md5 is pinned: if it
changes the icon is not rebuilt or verified, `STALE DONOR` says so, and the crop needs choosing again.

The prompts in docs/core_ruthenia_visual_prompts.md stay the brief for a painter: none of the donors holds a mace,
a seal ring or an astrolabe, so these are the closest existing pictures, not the finished art the prompts describe.
The Kyiv-Mohyla academy icon is not built here any more: 14431995 replaced it with the painted master.

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
import hashlib
import struct
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
SIZE = 57
FRAME = 3
ART = SIZE - 2 * FRAME  # 51
FILE_BYTES = HEADER + SIZE * SIZE * 4
ICON_DIR = "gfx/interface/government_reform_icons"
HEADER_DONOR = f"{ICON_DIR}/horde_riding.dds"
MIS = "gfx/interface/missions/"

# Vanilla picture statistics (HSV, 0-255) the grade pulls into, never beyond.
SAT_BAND = (75.0, 140.0)
VAL_BAND = (100.0, 165.0)
MIN_SPREAD = 42.0
MAX_SAT_GAIN = 1.5
MAX_STRETCH = 1.2
MIN_ALPHA = 200  # a donor crop must be opaque to this much
CHECK_TOLERANCE = 3  # per channel; Pillow versions round Lanczos and HSV slightly differently


@dataclass(frozen=True)
class Icon:
    name: str  # the file is rip_gfx_reform_<name>_icon.dds
    source: str  # path inside the donor root
    vanilla: bool  # True: under the installed game; False: under this mod
    crop: tuple[int, int, int, int]  # left, top, right, bottom of a SQUARE in the donor
    why: str
    md5: str | None = None  # pin for a donor inside this mod, which other work may repaint; vanilla's is pinned by the install version


ICONS = (
    Icon("cossack_host", "gfx/interface/missions/dlc_missions/third_rome/russian_minors/mission_recruit_the_cossacks.dds",
         True, (3, 9, 57, 63), "a Cossack rider with a lance and a pennant on the open steppe"),
    Icon("zaz_free_host", "gfx/interface/missions/mission_cossack_cavalry.dds",
         True, (0, 4, 59, 63), "an elite rider charging under a storm sky"),
    Icon("zaz_sich_brotherhood", "gfx/interface/sub/startup/subscription_startup_image_7_cossacks.dds",
         True, (205, 75, 545, 415), "the circle round the rada table: the quill, the paper, the oath"),
    Icon("het_starshyna_oligarchy", "gfx/dlc_pictures/dlc046_the_cossacks_banner.dds",
         True, (398, 52, 538, 192), "a grey-capped elder beside a crested officer: the senior ranks"),
    Icon("zaz_last_sich", "gfx/interface/great_projects/great_project_zaporozhian_sich.dds",
         False, (176, 31, 290, 145), "the log watchtower and palisade of the Sich, below the monument plaque",
         md5="1d0ee7952fbdf6137b5beda7ca10f013"),
    # Ruthenian reforms that drew a Japanese shogun, a British monarch, a revolutionary fist, a tribal
    # council or a Chinese examiner. Each donor is a vanilla mission picture of Rus', Novgorod,
    # Hungary or the Orthodox church, which is what the reform is about.
    Icon("kyivan_rus", MIS + "dlc_missions/third_rome/russian_minors/mission_restore_kiev.dds",
         True, (0, 2, 59, 61), "a Rus' prince on his throne with the book of law"),
    Icon("princes_council", MIS + "dlc_missions/third_rome/russian_minors/mission_unite_the_princes.dds",
         True, (0, 2, 59, 61), "princes and boyars in council under an arch"),
    Icon("kyivan_cathedral", MIS + "dlc_missions/lions_of_the_north/mission_develop_kiev.dds",
         True, (0, 2, 59, 61), "the golden domes of the Kyivan cathedral complex"),
    Icon("orthodox_synod", MIS + "dlc_missions/third_rome/novgorod/mission_autocephalous_archbishopric.dds",
         True, (0, 2, 59, 61), "the Orthodox cross between two icon banners"),
    Icon("prikaz_chancery", MIS + "dlc_missions/third_rome/muscovy_russia/mission_establish_the_prikazy.dds",
         True, (0, 4, 59, 63), "a chancery clerk writing with a quill"),
    Icon("rus_host", MIS + "dlc_missions/third_rome/russian_minors/mission_consolidate_the_state.dds",
         True, (0, 4, 59, 63), "a mounted captain and foot soldiers with red shields before a white fortress"),
    Icon("ruthenian_banner", MIS + "dlc_missions/third_rome/russian_minors/mission_rule_ruthenia.dds",
         True, (0, 2, 59, 61), "the blue banner with the golden trident of Ruthenia"),
    Icon("veche", MIS + "dlc_missions/third_rome/novgorod/mission_novgorod_the_great.dds",
         True, (0, 4, 59, 63), "the walls and towers of Novgorod, seat of the veche"),
    Icon("statute", MIS + "dlc_missions/emperor/serbia/reissue_the_mining_code.dds",
         True, (0, 2, 59, 61), "an illuminated law code read to a gathering"),
    Icon("sacred_law", MIS + "dlc_missions/emperor/serbia/law_of_the_pious.dds",
         True, (0, 2, 59, 61), "an open illuminated manuscript of church law"),
    Icon("palatine_compact", MIS + "dlc_missions/emperor/bohemia/hungarian_union.dds",
         True, (0, 2, 59, 61), "two parties settling a compact over a table"),
    Icon("palatine_parliament", MIS + "dlc_missions/emperor/hungary/a_strong_government.dds",
         True, (0, 4, 59, 63), "the seat of a Hungarian assembly"),
    Icon("monastic_lands", MIS + "dlc_missions/third_rome/muscovy_russia/mission_land_of_churches.dds",
         True, (0, 4, 59, 63), "white monastery churches in open country"),
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


class StaleDonor(Exception):
    """A donor inside this mod no longer is the picture the crop was chosen on."""


def make_picture(icon: Icon, root: Path) -> Image.Image:
    if icon.md5 and hashlib.md5((root / icon.source).read_bytes()).hexdigest() != icon.md5:
        raise StaleDonor(f"{icon.name}: {icon.source} is not the picture the crop {icon.crop} was chosen on "
                         f"(pinned md5 {icon.md5}); choose a new crop and update the pin")
    source = read_rgba(root / icon.source)
    left, top, right, bottom = icon.crop
    if right - left != bottom - top:
        raise ValueError(f"{icon.name}: crop {icon.crop} is not square")
    piece = source.crop(icon.crop)
    if np.asarray(piece)[..., 3].min() < MIN_ALPHA:  # some vanilla mission icons are 229-255 at their edges
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


# --------------------------------------------------------------------------------------------
# Composites: pictures put together from several existing ones
# --------------------------------------------------------------------------------------------

def donor_picture(path: Path, crop: tuple[int, int, int, int]) -> Image.Image:
    """A square piece of an opaque donor, scaled to the picture window and graded like any donor."""
    piece = read_rgba(path).crop(crop)
    picture = piece.convert("RGB").resize((ART, ART), Image.LANCZOS)
    return pull_into_band(picture.filter(ImageFilter.UnsharpMask(radius=0.7, percent=45, threshold=3)))


def confessional_balance(game: Path) -> Image.Image:
    """Orthodox domes on the left, a Gothic spire on the right, one gold seam between: two rites kept in balance."""
    left = donor_picture(game / MIS / "dlc_missions/third_rome/novgorod/mission_cathedral_cities.dds", (0, 2, 59, 61))
    right = donor_picture(game / MIS / "mission_european_church.dds", (0, 2, 59, 61))
    mask = Image.new("L", (ART * 4, ART * 4), 0)
    # the seam leans a little: from x = 28 at the top to x = 22 at the bottom
    ImageDraw.Draw(mask).polygon([(28 * 4, 0), (ART * 4, 0), (ART * 4, ART * 4), (22 * 4, ART * 4)], fill=255)
    mask = mask.resize((ART, ART), Image.LANCZOS)
    out = Image.composite(right, left, mask)
    seam = Image.new("RGBA", (ART * 4, ART * 4), (0, 0, 0, 0))
    ImageDraw.Draw(seam).line([(28 * 4, 0), (22 * 4, ART * 4)], fill=(236, 200, 110, 255), width=8)
    seam = seam.resize((ART, ART), Image.LANCZOS)
    shadow = seam.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: int(v * 0.5))
    out = out.convert("RGBA")
    dark = Image.new("RGBA", out.size, (0, 0, 0, 255))
    out = Image.composite(dark, out, shadow.getchannel("A"))
    out.alpha_composite(seam)
    return out.convert("RGB")


# The Rada of Three Estates (tools/build_kru_rada.py): one government, six reform ids, one for each ordered pair
# (second by influence, dominant). The icon shows the two emblems of the faction emblems, the dominant one large.
RADA_EMBLEMS = {  # faction -> (md5 of gfx/interface/rip_government/faction_<key>.dds, background of the card when it leads)
    "knyazi": ("3d34efd0e7e66c102262b6b990e060db", (96, 30, 38)),
    "boyary": ("5524d83042f61c86b2edc0674d793037", (30, 58, 62)),
    "starshyna": ("7f94ac517aa0947f83540f39449e6fd9", (74, 38, 30)),
}
RADA_PAIRS = (  # (second, dominant): the order of build_kru_rada.PAIRS
    ("boyary", "knyazi"), ("starshyna", "knyazi"), ("knyazi", "boyary"),
    ("starshyna", "boyary"), ("knyazi", "starshyna"), ("boyary", "starshyna"),
)


def rada_icon_name(second: str, lead: str) -> str:
    return f"kru_rada_{second}_{lead}"


def emblem(key: str) -> Image.Image:
    path = ROOT / "gfx/interface/rip_government" / f"faction_{key}.dds"
    if hashlib.md5(path.read_bytes()).hexdigest() != RADA_EMBLEMS[key][0]:
        raise StaleDonor(f"kru_rada: {path.relative_to(ROOT).as_posix()} is not the emblem the Rada icons were composed "
                         f"from (pinned md5 {RADA_EMBLEMS[key][0]}); compose them again and update the pin")
    image = read_rgba(path)
    box = np.asarray(image)[..., 3] > 24
    rows, cols = np.where(box)
    return image.crop((cols.min(), rows.min(), cols.max() + 1, rows.max() + 1))


def place(canvas: Image.Image, image: Image.Image, centre: tuple[float, float], longest: int, dim: float = 1.0) -> None:
    """Scale `image` so its longer side is `longest`, centre it, drop a soft shadow under it."""
    scale = longest / max(image.size)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    small = image.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")
    if dim != 1.0:
        r, g, b, a = small.split()
        small = Image.merge("RGBA", [c.point(lambda v: int(v * dim)) for c in (r, g, b)] + [a])
    x, y = round(centre[0] - size[0] / 2), round(centre[1] - size[1] / 2)
    shadow = Image.new("L", canvas.size, 0)
    shadow.paste(small.getchannel("A"), (x + 1, y + 2))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.6)).point(lambda v: int(v * 0.65))
    canvas.paste(Image.new("RGBA", canvas.size, (0, 0, 0, 255)), (0, 0), shadow)
    canvas.alpha_composite(small, (x, y))


def rada_picture(second: str, lead: str) -> Image.Image:
    """The two blocs that lead the Rada: the dominant emblem large and lit, the second smaller behind it."""
    cx, cy = ART * 0.58, ART * 0.44
    bg = np.zeros((ART, ART, 3), dtype=np.float64)
    yy, xx = np.mgrid[0:ART, 0:ART]
    radius = np.clip(np.hypot(xx - cx, yy - cy) / (ART * 0.78), 0.0, 1.0)
    centre = np.array(RADA_EMBLEMS[lead][1], dtype=np.float64)
    bg[:] = centre * (1.0 - 0.72 * radius[..., None] ** 1.4)
    canvas = Image.fromarray(bg.round().astype(np.uint8), "RGB").convert("RGBA")

    glow = np.clip(1.0 - np.hypot(xx - cx, yy - cy) / (ART * 0.42), 0.0, 1.0) ** 2 * 0.42
    light = Image.new("RGBA", canvas.size, (255, 214, 150, 0))
    light.putalpha(Image.fromarray((glow * 255).round().astype(np.uint8), "L"))
    canvas.alpha_composite(light)

    place(canvas, emblem(second), (ART * 0.27, ART * 0.72), 25, dim=0.82)
    place(canvas, emblem(lead), (cx, cy), 37)
    return canvas.convert("RGB")


@dataclass(frozen=True)
class Composite:
    name: str
    why: str
    make: Callable[[Path], Image.Image]  # the RGB picture of ART x ART


COMPOSITES = (
    Composite("confessional_balance", "an Orthodox cathedral and a Gothic church side by side, one gold seam",
              confessional_balance),
) + tuple(
    Composite(rada_icon_name(s, l), f"the Rada: {s} second, {l} dominant",
              (lambda game, s=s, l=l: rada_picture(s, l)))
    for s, l in RADA_PAIRS
)


def dds_bytes(pixels: np.ndarray, header: bytes) -> bytes:
    """Header of a vanilla icon (same pixel format, masks, flags) and BGRA pixels."""
    return bytes(header) + pixels[..., [2, 1, 0, 3]].tobytes()


def build_all_checked(game: Path) -> tuple[dict[str, np.ndarray], list[str]]:
    """The rebuilt icons, and a message for each icon whose pinned donor has changed (not rebuilt)."""
    ring = frame_ring(game)
    built, stale = {}, []
    for icon in ICONS:
        try:
            built[texture_path(icon)] = build(icon, game, ring)
        except StaleDonor as problem:
            stale.append(str(problem))
    for composite in COMPOSITES:
        try:
            out = ring.copy()
            out[FRAME:SIZE - FRAME, FRAME:SIZE - FRAME, :3] = np.asarray(composite.make(game), dtype=np.uint8)
            out[FRAME:SIZE - FRAME, FRAME:SIZE - FRAME, 3] = 255
            built[texture_path(Icon(composite.name, "", True, (0, 0, 0, 0), composite.why))] = out
        except StaleDonor as problem:
            stale.append(str(problem))
    return built, stale


def build_all(game: Path) -> dict[str, np.ndarray]:
    """Every icon, as {texture path: RGBA pixels}; raises StaleDonor rather than skip one (other tools call this)."""
    built, stale = build_all_checked(game)
    if stale:
        raise StaleDonor("; ".join(stale))
    return built


def preview(images: dict[str, np.ndarray], scale: int, out: Path, columns: int = 8) -> None:
    pad = 8
    cell = SIZE * scale
    rows = -(-len(images) // columns)
    sheet = Image.new("RGB", (min(len(images), columns) * (cell + pad) + pad, rows * (cell + pad + 14) + pad), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    for i, (path, px) in enumerate(images.items()):
        tile = Image.fromarray(px, "RGBA").resize((cell, cell), Image.NEAREST)
        x = pad + (i % columns) * (cell + pad)
        y = pad + (i // columns) * (cell + pad + 14)
        sheet.paste(tile, (x, y), tile)
        draw.text((x, y + cell + 2), Path(path).stem.replace("rip_gfx_reform_", "")[:30], fill=(230, 230, 230))
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
    images, stale = build_all_checked(game)
    for message in stale:
        print(f"STALE DONOR {message}")
    if stale and not args.check:
        print("nothing written: a donor changed, so the picture would not be the one that was chosen")
        return 1

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
        note = f"; {len(stale)} not re-verified (STALE DONOR above)" if stale else ""
        print("REFORM ICONS FAIL" if bad else f"REFORM ICONS PASS: {len(images)} icons rebuild from their donors{note}")
        return 1 if bad else 0

    for path, px in images.items():
        (ROOT / path).write_bytes(dds_bytes(px, header))
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())