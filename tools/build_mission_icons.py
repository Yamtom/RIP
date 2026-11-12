"""Build the six locked-branch mission icons of the Carpathian Captaincy (UZH) and Chernihiv (CHR).

Six missions - `uz_identity_branching_1..3` and `chr_identity_branching_1..3` - are placeholders for
the identity branch the player has not taken. They drew vanilla's `mission_unknown_mission`, the same
question mark for both countries and all six slots. They now draw a picture each, chosen from
painted vanilla mission art for what the branch is about, with vanilla's own gold padlock in the
corner so a locked slot still reads as locked:

    uzh_identity_branch_locked_1  expand_into_the_forest   a village in a forested mountain valley
    uzh_identity_branch_locked_2  claim_the_borderlands    a trail winding over a wooded cliff pass
    uzh_identity_branch_locked_3  the_law_colleges         a closed, ornate cover in an iron frame
    chr_identity_branch_locked_1  control_moldavia         a parchment map of two lands side by side
    chr_identity_branch_locked_2  early_russian_army       horsemen with lances and banners
    chr_identity_branch_locked_3  ne_palisades             a palisade line on the steppe edge

The prompts in docs/core_ruthenia_visual_prompts.md (a sealed charter on a waymarker, a forked
signpost, a codex with iron clasps, a sealed compact over a map, crossed spears bound with a ribbon,
a banner folded on a watchtower) stay the brief for a painter: none of the donors shows those
objects, so these are the nearest existing pictures, not the finished art the prompts describe.

Measured on the installed 1.37.5: 1511 of 1565 vanilla mission icons are 59x63, uncompressed 32-bit
BGRA, no mipmaps, 14996 bytes, fully opaque, with no frame of their own (the mission window draws it).

Pipeline per icon: the donor as it is, then the padlock - cut from `mission_locked_mission` by value
(the dark background goes, the keyhole stays dark, the shackle opening goes), scaled to 23 px tall,
set bottom-right over a soft dark backing and a drop shadow. Nothing else is changed; the donors
are already vanilla's own grade.

    python tools/build_mission_icons.py            # write the six DDS
    python tools/build_mission_icons.py --check    # rebuild and compare with the checked-in DDS
    python tools/build_mission_icons.py --preview out.png --scale 5

Needs Pillow, numpy and the installed game (EU4_DIR or the usual Steam path); without the game
--check says SKIP and exits 0, and writing refuses.
"""
from __future__ import annotations

import argparse
import struct
import sys
from collections import deque
from dataclasses import dataclass
from pathlib import Path

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
LOCK_DONOR = f"{MISSION_DIR}/dlc_missions/lions_of_the_north/mission_locked_mission.dds"
LOCK_BACKGROUND = (25, 31, 35)  # the flat colour behind vanilla's padlock
LOCK_EDGE = (55.0, 95.0)  # value range over which the cut-out edge fades in
LOCK_DARK = 70  # below this a pixel is background or keyhole
LOCK_HEIGHT = 23
LOCK_MARGIN = 2
CHECK_TOLERANCE = 3  # per channel; Pillow versions round Lanczos slightly differently


@dataclass(frozen=True)
class Icon:
    name: str  # the file is rip_gfx_mission_<name>_icon.dds
    source: str  # path inside the vanilla install
    why: str


ICONS = (
    Icon("uzh_identity_branch_locked_1", f"{MISSION_DIR}/dlc_missions/lions_of_the_north/mission_expand_into_the_forest.dds",
         "a village in a forested mountain valley"),
    Icon("uzh_identity_branch_locked_2", f"{MISSION_DIR}/dlc_missions/emperor/saxony/claim_the_borderlands.dds",
         "a trail winding over a wooded cliff pass"),
    Icon("uzh_identity_branch_locked_3", f"{MISSION_DIR}/dlc_missions/emperor/milan2/the_law_colleges.dds",
         "a closed, ornate cover in an iron frame"),
    Icon("chr_identity_branch_locked_1", f"{MISSION_DIR}/dlc_missions/winds_of_change/mission_control_moldavia.dds",
         "a parchment map of two lands side by side"),
    Icon("chr_identity_branch_locked_2", f"{MISSION_DIR}/dlc_missions/domination/mission_early_russian_army.dds",
         "horsemen with lances and banners"),
    Icon("chr_identity_branch_locked_3", f"{MISSION_DIR}/mission_ne_palisades.dds",
         "a palisade line on the steppe edge"),
)


def texture_path(icon: Icon) -> str:
    return f"{MISSION_DIR}/rip_gfx_mission_{icon.name}_icon.dds"


def sprite_name(icon: Icon) -> str:
    return f"rip_gfx_mission_{icon.name}_icon"


def read_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def lock_badge(game: Path) -> Image.Image:
    """Vanilla's gold padlock as an RGBA cut-out, cropped to its own box."""
    source = read_rgba(game / LOCK_DONOR)
    rgb = np.asarray(source.convert("RGB"), dtype=np.float64)
    value = np.asarray(source.convert("RGB").convert("HSV"), dtype=np.float64)[..., 2]
    height, width = value.shape
    dark = value < LOCK_DARK

    # Dark pixels reachable from the border are background. Enclosed dark pixels are the shackle
    # opening (upper half of the lock, transparent) or the keyhole (lower half, kept dark).
    outside = np.zeros_like(dark)
    queue = deque((y, x) for y in range(height) for x in range(width)
                  if dark[y, x] and (y in (0, height - 1) or x in (0, width - 1)))
    for y, x in queue:
        outside[y, x] = True
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < height and 0 <= nx < width and dark[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True
                queue.append((ny, nx))
    lit = ~dark
    rows = np.where(lit.any(axis=1))[0]
    top, bottom = rows.min(), rows.max()
    keyhole = np.zeros_like(dark)
    seen = outside.copy()
    for y in range(height):
        for x in range(width):
            if dark[y, x] and not seen[y, x]:
                component, stack = [], [(y, x)]
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    component.append((cy, cx))
                    for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                        if 0 <= ny < height and 0 <= nx < width and dark[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if np.mean([cy for cy, _ in component]) > top + 0.55 * (bottom - top):
                    for cy, cx in component:
                        keyhole[cy, cx] = True

    lo, hi = LOCK_EDGE
    alpha = np.clip((value - lo) / (hi - lo), 0.0, 1.0)
    alpha[keyhole] = 1.0
    alpha[outside] = 0.0
    # Take the background colour out of the edge pixels so the cut-out does not carry a dark halo.
    matte = np.array(LOCK_BACKGROUND, dtype=np.float64)
    safe = np.maximum(alpha, 1e-3)[..., None]
    colour = np.clip((rgb - matte * (1.0 - alpha[..., None])) / safe, 0.0, 255.0)
    colour[keyhole] = rgb[keyhole]
    out = np.dstack([colour, alpha * 255.0]).round().astype(np.uint8)
    box = np.where(alpha > 0.02)
    badge = Image.fromarray(out, "RGBA").crop((box[1].min(), box[0].min(), box[1].max() + 1, box[0].max() + 1))
    scale = LOCK_HEIGHT / badge.height
    return badge.convert("RGBa").resize((max(1, round(badge.width * scale)), LOCK_HEIGHT), Image.LANCZOS).convert("RGBA")


def add_badge(picture: Image.Image, badge: Image.Image) -> Image.Image:
    x = WIDTH - badge.width - LOCK_MARGIN
    y = HEIGHT - badge.height - LOCK_MARGIN
    canvas = picture.convert("RGBA")

    backing = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(backing).ellipse((x - 5, y - 5, x + badge.width + 4, y + badge.height + 4), fill=120)
    backing = backing.filter(ImageFilter.GaussianBlur(4))
    canvas = Image.composite(Image.new("RGBA", canvas.size, (0, 0, 0, 255)), canvas, backing)

    shadow = Image.new("L", canvas.size, 0)
    shadow.paste(badge.getchannel("A"), (x + 1, y + 1))
    shadow = shadow.filter(ImageFilter.GaussianBlur(1.1)).point(lambda v: int(v * 0.6))
    canvas = Image.composite(Image.new("RGBA", canvas.size, (0, 0, 0, 255)), canvas, shadow)

    canvas.alpha_composite(badge, (x, y))
    canvas.putalpha(255)
    return canvas


def build(icon: Icon, game: Path, badge: Image.Image) -> np.ndarray:
    donor = read_rgba(game / icon.source)
    if donor.size != (WIDTH, HEIGHT):
        raise ValueError(f"{icon.name}: donor {icon.source} is {donor.size}, mission icons are {WIDTH}x{HEIGHT}")
    if np.asarray(donor)[..., 3].min() != 255:
        raise ValueError(f"{icon.name}: donor {icon.source} is not opaque")
    return np.asarray(add_badge(donor, badge), dtype=np.uint8)


def dds_bytes(pixels: np.ndarray, header: bytes) -> bytes:
    return bytes(header) + pixels[..., [2, 1, 0, 3]].tobytes()


def build_all(game: Path) -> dict[str, np.ndarray]:
    badge = lock_badge(game)
    return {texture_path(icon): build(icon, game, badge) for icon in ICONS}


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
    parser.add_argument("--check", action="store_true", help="rebuild and compare with the checked-in DDS")
    parser.add_argument("--preview", type=Path, help="write a PNG sheet instead of the DDS")
    parser.add_argument("--scale", type=int, default=5)
    args = parser.parse_args()

    game = vanilla_root()
    if game is None:
        print("SKIP: the vanilla install is needed for the donors and the padlock (set EU4_DIR); nothing written")
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
        print("MISSION ICONS FAIL" if bad else f"MISSION ICONS PASS: {len(images)} icons rebuild from their donors")
        return 1 if bad else 0

    for path, px in images.items():
        (ROOT / path).write_bytes(dds_bytes(px, header))
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
