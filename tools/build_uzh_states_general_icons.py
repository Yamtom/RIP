"""Draw the art of the Palanok captaincy's states-general scale.

Three sprites, each the size, frame count and format of the vanilla sprite it
stands in for:

  uzh_palanok_captaincy_reform.dds  57x57, one frame   the reform card (vanilla:
        government_reform_*, a 51x51 picture inside a baked three-pixel frame)
  uzh_partia_soymu.dds              54x19, two frames  the left end of the bar
        (vanilla: GFX_statists, republic_icon_strip.dds, 27x19 per frame)
  uzh_partia_kapitaniv.dds          46x25, two frames  the right end of the bar
        (vanilla: GFX_monarchists, monarchism_icon_strip.dds, 23x25 per frame)

Frame 1 is the coloured picture and frame 2 the same picture in gold, the way
vanilla's crown and cap strips show a side that holds power.

The reform card shows Palanok above the Tysa with a salt barge at the wharf:
the castle for the captains, the barge for the Sejm. The Sejm Party is a
magnate's fur kalpak with a heron plume (Hungarian-Rusyn county dress); the
Captains' Party is a castle tower with a pennant (the frontier march). There
is no text, no flag of a later state and no imperial eagle in any of them.

The art is painted procedurally with the toolkit of
tools/build_government_ability_icons.py (polygons, gradients, a lit height
field and noise, supersampled 8x), so no image model and no external file is
involved and --check can redraw every sprite and compare it with the DDS in
the repository.

    python tools/build_uzh_states_general_icons.py            # write DDS + gfx
    python tools/build_uzh_states_general_icons.py --check    # redraw and compare
    python tools/build_uzh_states_general_icons.py --preview out.png --scale 6
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_government_ability_icons as kit  # noqa: E402  (shared painting toolkit, read-only here)
from build_government_ability_icons import (  # noqa: E402
    GOLD, SS, SIZE, FUR, BLUE_CLOTH, GREEN_CLOTH, WOOD, DARK_WOOD, STONE, CANVAS, LEATHER, VELVET_RED,
    Image, ImageChops, ImageDraw, ImageFilter, np,
    arc_points, backdrop, banner, bezier, blank_layer, blank_mask, blur, clip, ellipse, from_alpha, full_mask,
    glow, gradient, grow, hexc, inter, minus, noise, outline, over, poly, radial, ramp, roundness,
    shadow, shaded, solid, stroke, strands, union,
)

ROOT = HERE.parent
TEXTURE_DIR = 'gfx/interface/rip_government'
GFX_FILE = 'interface/RIP_UZH_government_states_general.gfx'
CHECK_TOLERANCE = 3          # per channel; float maths differs a little between machines

# name -> (texture file, sprite name, (width, height) in pixels, frames)
SPRITES = {
    'reform': ('uzh_palanok_captaincy_reform.dds',
               'government_reform_rip_gfx_reform_uzh_palanok_captaincy_icon', (57, 57), 1),
    'soymu': ('uzh_partia_soymu.dds', 'GFX_partia_soymu', (54, 19), 2),
    'kapitaniv': ('uzh_partia_kapitaniv.dds', 'GFX_partia_kapitaniv', (46, 25), 2),
}

# Warm castle stone and fired roof tile; the toolkit only ships a cold blue stone.
STONE_WARM = [(0.0, hexc('#2e2824')), (0.38, hexc('#6e6254')), (0.6, hexc('#9a8c78')),
              (0.85, hexc('#cdbfa6')), (1.0, hexc('#f4ead4'))]
TILE = [(0.0, hexc('#2a0e08')), (0.4, hexc('#6a2a14')), (0.6, hexc('#9a4a22')),
        (0.85, hexc('#c8743a')), (1.0, hexc('#f0a868'))]
GRASS = [(0.0, hexc('#0e1e0e')), (0.4, hexc('#2a4a22')), (0.6, hexc('#3e6a30')),
         (0.85, hexc('#6a9448')), (1.0, hexc('#b4cc78'))]
ROCK = [(0.0, hexc('#1c1a1a')), (0.4, hexc('#4a4642')), (0.6, hexc('#6e6860')),
        (0.85, hexc('#9a928a')), (1.0, hexc('#d0c8bc'))]
SALT = [(0.0, hexc('#7a8088')), (0.4, hexc('#c4cad0')), (0.6, hexc('#e4e8ea')),
        (0.85, hexc('#f6f8f8')), (1.0, hexc('#ffffff'))]
WATER = [(0.0, hexc('#0c2a36')), (0.5, hexc('#1c5668')), (1.0, hexc('#5aa0ae'))]
CRIMSON = [(0.0, hexc('#2a0508')), (0.4, hexc('#6a0e14')), (0.6, hexc('#9a1a22')),
           (0.85, hexc('#c4323a')), (1.0, hexc('#ee7a74'))]


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------

def to_pixels(layer, box, size):
    """Crop a box (in toolkit sprite units) from a supersampled layer and fit it to `size` pixels."""
    x0, y0, x1, y1 = [int(round(v * SS)) for v in box]
    crop = layer.crop((x0, y0, x1, y1))
    small = crop.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')
    return small


def golden(layer):
    """The same picture in gold: luminance mapped through the gold ramp, alpha kept."""
    arr = np.asarray(layer, dtype=np.float32).copy()
    lum = (arr[..., 0] * 0.30 + arr[..., 1] * 0.59 + arr[..., 2] * 0.11) / 255.0
    t = np.clip((lum - 0.04) * 1.35, 0, 1)
    arr[..., :3] = ramp(t, GOLD)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def strip(frames):
    width = sum(f.width for f in frames)
    sheet = Image.new('RGBA', (width, frames[0].height), (0, 0, 0, 0))
    x = 0
    for frame in frames:
        sheet.paste(frame, (x, 0))
        x += frame.width
    return sheet


# --------------------------------------------------------------------------
# The Sejm Party: a magnate's kalpak (27x19 px per frame, 3 sprite units a pixel)
# --------------------------------------------------------------------------

PX = 3.0                       # sprite units per target pixel for the two small icons


def P(x, y):
    return (x * PX, y * PX)


def Ps(points):
    return [P(x, y) for x, y in points]


def kalpak_layer():
    """A fur-banded cap with a cloth bag, a gold brooch and a heron plume, in profile."""
    layer = blank_layer()
    band = union(poly(Ps([(3.4, 11.0), (22.4, 10.4), (23.0, 15.6), (2.8, 16.4)])),
                 ellipse(*P(12.9, 16.2), 10.0 * PX, 2.2 * PX), ellipse(*P(12.9, 10.7), 9.6 * PX, 1.9 * PX))
    bag_pts = ([P(4.0, 11.0)] +
               [P(x, y) for x, y in bezier((4.0, 11.0), (2.6, 4.6), (9.0, 0.8), (15.0, 1.4))[1:]] +
               [P(x, y) for x, y in bezier((15.0, 1.4), (21.5, 2.0), (26.2, 5.6), (24.6, 11.2))[1:]] +
               [P(22.6, 10.8), P(12.0, 10.6)])
    bag = poly(bag_pts)
    whole = union(band, bag)
    layer = over(layer, shadow(whole, 0.8, 1.1, 0.9, 0.5), outline(whole, 0.55 * PX, (14, 10, 6), 0.95))
    layer = over(layer, shaded(bag, GREEN_CLOTH, 1.6, relief=3.2, gain=1.7, spec=0.18))
    # the gold braid down the bag
    braid = stroke(Ps([(6.0, 9.4), (10.6, 4.4), (17.4, 3.8), (22.6, 7.4)]), 0.85 * PX, caps=False)
    layer = over(layer, shaded(inter(braid, bag), GOLD, 0.8, relief=1.4, gain=1.8, spec=0.4))
    layer = over(layer, shaded(band, FUR, 1.2, relief=2.6, gain=1.6, texture=noise(11, 3.0, 3)))
    layer = over(layer, strands(band, 11, 380, 1.2 * PX, 0.16 * PX,
                                [hexc('#0e0805'), hexc('#2a180d'), hexc('#5a3a22'), hexc('#a88a60')],
                                lambda x, y: math.pi / 2, spread=0.6))
    layer = over(layer, roundness(band, 2.8 * PX, 23.0 * PX, dark=0.45, lift=0.22, peak=0.30))
    # brooch: gold boss with a red stone, and the plume rising from it
    bx, by = 9.4, 11.6
    for dx, sweep in ((0.0, -1.0), (1.4, -0.3), (-1.1, -1.7)):
        feather = stroke([P(bx, by - 1.0)] +
                         [P(x, y) for x, y in bezier((bx, by - 1.0), (bx - 3.0 + dx, 7.0), (bx - 3.4 + sweep, 3.6), (bx - 1.6 + sweep * 1.6, 0.9))[1:]],
                         1.15 * PX)
        layer = over(layer, outline(feather, 0.4 * PX, (30, 24, 20), 0.95), solid(feather, (250, 246, 236), 1.0))
    boss = ellipse(*P(bx, by), 2.3 * PX)
    layer = over(layer, outline(boss, 0.3 * PX, (40, 22, 4), 0.95), shaded(boss, GOLD, 0.6, relief=1.4, gain=1.9, spec=0.5))
    layer = over(layer, solid(ellipse(*P(bx, by), 1.1 * PX), (200, 20, 40), 1.0),
                 solid(ellipse(*P(bx - 0.3, by - 0.3), 0.35 * PX), (255, 190, 190), 0.9))
    return layer


def _emblem_frame_pair(cutout: Image.Image, fw: int, fh: int, frame: int) -> Image.Image:
    """Fit a painted cutout into (fw, fh) with a 1px dark rim and return Frame 1 (muted) or Frame 2 (gold)."""
    cw, ch = cutout.size
    target_w, target_h = fw - 4, fh - 4
    scale = min(target_w / float(cw), target_h / float(ch))
    nw = max(1, int(round(cw * scale)))
    nh = max(1, int(round(ch * scale)))
    small = cutout.convert('RGBa').resize((nw, nh), Image.LANCZOS).convert('RGBA')
    canvas = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    canvas.paste(small, ((fw - nw) // 2, (fh - nh) // 2))
    alpha = np.asarray(canvas.getchannel('A'), dtype=np.float32)
    dilated = np.asarray(canvas.getchannel('A').filter(ImageFilter.MaxFilter(3)), dtype=np.float32)
    dilated[0, 0] = 0.0
    rim_a = np.clip(dilated * 0.92, 0, 255).astype(np.uint8)
    base = Image.new('RGBA', (fw, fh), (18, 12, 8, 0))
    base.putalpha(Image.fromarray(rim_a, 'L'))
    fg = canvas.copy()
    fg.putalpha(Image.fromarray(np.clip(alpha * 1.15, 0, 255).astype(np.uint8), 'L'))
    merged = Image.alpha_composite(base, fg)
    shared_alpha = merged.getchannel('A')
    if frame == 1:
        out = kit.grade_rgba(merged, tint_rgb=(0.94, 0.92, 0.88), sat=0.68, brightness=0.78, contrast=1.05)
    else:
        out = golden(kit.grade_rgba(merged, brightness=1.12, contrast=1.10))
    out.putalpha(shared_alpha)
    return kit.clean_alpha_rgb(out)


def scene_soymu(frame):
    return _emblem_frame_pair(kit.priv_cutout('seimski_statutes'), 27, 19, frame)


def scene_kapitaniv(frame):
    return _emblem_frame_pair(kit.atlas_cutout(3, 3), 23, 25, frame)


# --------------------------------------------------------------------------
# The reform card: Palanok above the Tysa, a salt barge at the wharf
# --------------------------------------------------------------------------

def tile_cone(cx, base_y, half, height):
    return poly([(cx - half, base_y), (cx + half, base_y), (cx, base_y - height)])


def tower_scene(cx, base_y, width, height, roof, seed):
    """One round tower of the castle: lit stone shaft, crenellated gallery, conical tile roof."""
    hw = width / 2.0
    shaft = poly([(cx - hw, base_y), (cx + hw, base_y), (cx + hw * 0.92, base_y - height), (cx - hw * 0.92, base_y - height)])
    gallery = poly([(cx - hw * 1.12, base_y - height), (cx + hw * 1.12, base_y - height), (cx + hw * 1.12, base_y - height - 2.4),
                    (cx - hw * 1.12, base_y - height - 2.4)])
    cone = tile_cone(cx, base_y - height - 2.4, hw * 1.2, roof)
    layer = blank_layer()
    layer = over(layer, shadow(union(shaft, gallery, cone), 0.8, 1.0, 1.0, 0.5))
    layer = over(layer, outline(union(shaft, gallery, cone), 0.5, (24, 14, 8), 0.95))
    layer = over(layer, shaded(shaft, STONE_WARM, 1.0, relief=2.2, gain=1.6, texture=noise(seed, 1.4, 3)))
    layer = over(layer, roundness(shaft, cx - hw, cx + hw, dark=0.5, lift=0.2, peak=0.3))
    layer = over(layer, shaded(gallery, STONE_WARM, 0.5, relief=1.2, gain=1.6))
    layer = over(layer, solid(poly([(cx - hw * 1.12, base_y - height), (cx + hw * 1.12, base_y - height), (cx + hw * 1.12, base_y - height + 0.9), (cx - hw * 1.12, base_y - height + 0.9)]), (20, 14, 10), 0.55))
    layer = over(layer, shaded(cone, TILE, 1.0, relief=2.2, gain=1.6, spec=0.1, texture=noise(seed + 2, 0.8, 3)))
    layer = over(layer, roundness(cone, cx - hw * 1.2, cx + hw * 1.2, dark=0.45, lift=0.12, peak=0.3))
    slit = poly([(cx - 0.5, base_y - height * 0.62), (cx + 0.5, base_y - height * 0.62), (cx + 0.5, base_y - height * 0.36), (cx - 0.5, base_y - height * 0.36)])
    layer = over(layer, solid(slit, (12, 8, 8), 0.9))
    return layer


def curtain_wall(x0, x1, base_y, height):
    wall = poly([(x0, base_y), (x1, base_y), (x1, base_y - height), (x0, base_y - height)])
    teeth = union(*[poly([(x, base_y - height), (x + 2.2, base_y - height), (x + 2.2, base_y - height - 2.4), (x, base_y - height - 2.4)])
                    for x in np.arange(x0, x1 - 1.5, 4.0)])
    whole = union(wall, teeth)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 0.8, 1.0, 0.9, 0.5), outline(whole, 0.45, (24, 14, 8), 0.95))
    layer = over(layer, shaded(whole, STONE_WARM, 0.9, relief=2.0, gain=1.6, texture=noise(41, 1.2, 3)))
    courses = blank_mask()
    d = ImageDraw.Draw(courses)
    for k in range(1, int(height // 2.6) + 1):
        d.line(kit._px([(x0 + 0.4, base_y - k * 2.6), (x1 - 0.4, base_y - k * 2.6)]), fill=255, width=max(1, int(0.18 * SS)))
    layer = over(layer, solid(inter(courses, wall), (40, 30, 22), 0.4))
    return layer


def scene_reform():
    layer = gradient(full_mask(), [(0.0, hexc('#7f9cc4')), (0.55, hexc('#c6d2dc')), (1.0, hexc('#f4e4b8'))], (0, 0), (0, 52))
    layer = over(layer, glow(60, 24, 30, (255, 236, 190), 0.55))
    # far Carpathian ridges
    far = poly([(0, 64)] + [(x, 40 - 11 * math.sin(x / 82.0 * math.pi * 1.7 + 0.4) - 4 * math.sin(x / 7.0)) for x in range(0, 83, 3)] + [(82, 64)])
    layer = over(layer, shaded(far, [(0.0, hexc('#3a4a62')), (0.5, hexc('#6a7c96')), (1.0, hexc('#aebccc'))], 3.0, relief=3.0, gain=0.8))
    near = poly([(0, 64)] + [(x, 47 - 7 * math.sin(x / 82.0 * math.pi * 2.3 + 2.0) - 2.5 * math.sin(x / 5.0)) for x in range(0, 83, 3)] + [(82, 64)])
    layer = over(layer, shaded(near, [(0.0, hexc('#1c3a34')), (0.5, hexc('#3a6252')), (1.0, hexc('#7aa08a'))], 3.0, relief=3.0, gain=0.8))
    # the castle hill, broad enough to fill the width, with a rocky shoulder and a few firs
    hill_top = lambda x: 68 - 22 * math.exp(-((x - 41) / 40.0) ** 2) - 0.9 * math.sin(x / 4.0)
    hill = poly([(-4, 70)] + [(x, hill_top(x)) for x in range(-4, 87, 2)] + [(86, 70)])
    layer = over(layer, shadow(hill, 0.0, 1.0, 2.0, 0.4))
    layer = over(layer, shaded(hill, GRASS, 3.0, relief=5.0, gain=1.5, texture=noise(5, 3.0, 3)))
    crag = poly([(22, 58), (27, 51), (34, 47.5), (48, 47.5), (55, 51), (60, 58), (50, 61), (32, 61)])
    layer = over(layer, shaded(crag, ROCK, 1.6, relief=3.0, gain=1.4, texture=noise(6, 2.0, 3)))
    for fx, fy, fh in ((9, 60.5, 11), (16, 57.5, 13), (68, 57.5, 12), (75, 60.5, 10), (4, 63, 8)):
        fir = poly([(fx - fh * 0.32, fy), (fx + fh * 0.32, fy), (fx + fh * 0.14, fy - fh * 0.45), (fx + fh * 0.22, fy - fh * 0.45),
                    (fx, fy - fh), (fx - fh * 0.22, fy - fh * 0.45), (fx - fh * 0.14, fy - fh * 0.45)])
        layer = over(layer, shadow(fir, 0.5, 0.7, 0.6, 0.4), outline(fir, 0.35, (6, 16, 8), 0.9),
                     shaded(fir, [(0.0, hexc('#06160c')), (0.5, hexc('#16401f')), (1.0, hexc('#3f7a42'))], 0.8, relief=1.6, gain=1.4))
    # the castle: curtain wall, two round towers, the keep
    layer = over(layer, curtain_wall(25.0, 57.0, 47.5, 9.0))
    layer = over(layer, tower_scene(25.0, 48.0, 8.0, 19.0, 11.0, 3))
    layer = over(layer, tower_scene(57.0, 48.0, 8.0, 17.0, 10.0, 4))
    keep = poly([(35.0, 47.5), (47.0, 47.5), (47.0, 28.0), (35.0, 28.0)])
    keep_roof = poly([(33.0, 28.0), (49.0, 28.0), (41.0, 15.0)])
    layer = over(layer, shadow(union(keep, keep_roof), 0.8, 1.0, 1.0, 0.5), outline(union(keep, keep_roof), 0.5, (24, 14, 8), 0.95))
    layer = over(layer, shaded(keep, STONE_WARM, 1.0, relief=2.2, gain=1.6, texture=noise(8, 1.4, 3)))
    layer = over(layer, roundness(keep, 35.0, 47.0, dark=0.4, lift=0.18, peak=0.3))
    layer = over(layer, shaded(keep_roof, TILE, 1.0, relief=2.4, gain=1.6, spec=0.1, texture=noise(9, 0.8, 3)))
    layer = over(layer, roundness(keep_roof, 33.0, 49.0, dark=0.45, lift=0.12, peak=0.3))
    for wx in (38.0, 43.0):
        layer = over(layer, solid(poly([(wx, 33), (wx + 1.6, 33), (wx + 1.6, 37.5), (wx, 37.5)]), (255, 200, 110), 0.95))
    gate = poly([(38.6, 47.5), (38.6, 43.5)] + [(41.0 + 2.4 * math.cos(a), 43.5 - 2.4 * math.sin(a)) for a in np.linspace(math.pi, 0, 14)] + [(43.4, 47.5)])
    layer = over(layer, solid(gate, (14, 8, 6), 0.95))
    layer = over(layer, banner((41.0, 16.0), 0, 9.0, 10.0, 5.2, CRIMSON, charge=None, seed=2, side=1))
    # the river and the wharf
    river = poly([(0, 62), (82, 62), (82, 82), (0, 82)])
    layer = over(layer, gradient(river, WATER, (0, 62), (0, 82)))
    ripples = blank_mask()
    d = ImageDraw.Draw(ripples)
    for i, y in enumerate((66, 70, 74, 78)):
        for x0 in range(2 + (i % 2) * 9, 80, 18):
            d.line(kit._px([(x0, y), (x0 + 7, y + 0.2)]), fill=255, width=int(0.5 * SS))
    layer = over(layer, solid(inter(ripples, river), (200, 232, 236), 0.35))
    bank = poly([(0, 61), (82, 61), (82, 64), (0, 64)])
    layer = over(layer, shaded(bank, STONE_WARM, 0.6, relief=1.4, gain=1.4))
    # the salt barge: hull, a heap of white salt blocks, a steering oar
    hull = poly([(8, 70), (50, 70), (46, 77), (13, 77)])
    layer = over(layer, shadow(hull, 0.8, 1.4, 1.6, 0.5), outline(hull, 0.5, (24, 12, 6), 0.95))
    layer = over(layer, shaded(hull, DARK_WOOD, 0.9, relief=1.8, gain=1.5, texture=noise(12, 1.0, 3)))
    layer = over(layer, solid(stroke([(9.5, 71.4), (48.4, 71.4)], 0.5), (200, 160, 90), 0.6))
    heap = []
    for row, (y, count, x0) in enumerate(((70.0, 5, 12.0), (65.5, 4, 15.0), (61.0, 3, 18.0))):
        for i in range(count):
            blk = poly([(x0 + i * 7.0, y), (x0 + i * 7.0 + 6.2, y), (x0 + i * 7.0 + 5.6, y - 4.6), (x0 + i * 7.0 + 0.6, y - 4.6)])
            heap.append(blk)
    salt = union(*heap)
    layer = over(layer, shadow(salt, 0.6, 0.9, 0.8, 0.4), outline(salt, 0.4, (60, 60, 66), 0.9))
    layer = over(layer, shaded(salt, SALT, 0.6, relief=1.4, gain=1.6, texture=noise(13, 1.0, 2)))
    oar = stroke([(51, 69), (58, 76)], 0.8)
    layer = over(layer, outline(oar, 0.3, (24, 12, 6), 0.9), shaded(oar, WOOD, 0.3, relief=0.8, gain=1.5))
    # barrels on the wharf: the tolls
    for bx, by in ((66.0, 63.5), (73.5, 64.0)):
        barrel = union(ellipse(bx, by, 4.2, 5.0), poly([(bx - 4.2, by - 3.4), (bx + 4.2, by - 3.4), (bx + 4.2, by + 3.4), (bx - 4.2, by + 3.4)]))
        layer = over(layer, shadow(barrel, 0.8, 1.2, 1.0, 0.5), outline(barrel, 0.45, (24, 12, 6), 0.95))
        layer = over(layer, shaded(barrel, WOOD, 0.8, relief=1.8, gain=1.5, texture=noise(int(bx), 0.7, 2)))
        layer = over(layer, roundness(barrel, bx - 4.2, bx + 4.2, dark=0.5, lift=0.15))
        for hy in (-2.2, 2.2):
            layer = over(layer, solid(stroke([(bx - 4.0, by + hy), (bx + 4.0, by + hy)], 0.45), (40, 40, 44), 0.8))
    return layer


def _pull_into_reform_band(rgb: np.ndarray, strength: float = 0.35) -> np.ndarray:
    target_mean = (76.0, 62.0, 49.0)
    target_std = (42.0, 36.0, 30.0)
    arr = rgb.astype(np.float32).copy()
    for c in range(3):
        ch = arr[..., c]
        m = float(ch.mean())
        s = max(1.0, float(ch.std()))
        norm = (ch - m) / s * target_std[c] + target_mean[c]
        arr[..., c] = ch * (1.0 - strength) + norm * strength
    return np.clip(arr, 0, 255).astype(np.uint8)


def frame_reform(picture):
    """Fit a 51x51 picture into vanilla's authentic three-pixel reform frame ring and colour band."""
    donor = ROOT / 'gfx/interface/government_reform_icons/rip_gfx_reform_cossack_host_icon.dds'
    out = Image.open(donor).convert('RGBA')
    pic_rgba = picture.convert('RGBA').resize((51, 51), Image.LANCZOS)
    graded_rgb = _pull_into_reform_band(np.asarray(pic_rgba.convert('RGB'), dtype=np.uint8))
    inner = Image.fromarray(graded_rgb, 'RGB').convert('RGBA')
    inner.putalpha(255)
    out.paste(inner, (3, 3))
    out.putalpha(255)
    return out


def scene_reform_sprite():
    layer = kit.painted_backdrop(
        'gfx/interface/great_projects/source/palanok_fortress.png',
        focus=(0.50, 0.46), zoom=1.08, contrast=1.08,
    )
    picture = layer.resize((51, 51), Image.LANCZOS)
    picture = picture.filter(ImageFilter.UnsharpMask(radius=0.6, percent=38, threshold=3))
    return frame_reform(picture)


# --------------------------------------------------------------------------
# Rendering and output
# --------------------------------------------------------------------------

def render(key):
    """The finished sprite for `key` as an RGBA image of the target size."""
    if key == 'reform':
        return scene_reform_sprite()
    paint = {'soymu': scene_soymu, 'kapitaniv': scene_kapitaniv}[key]
    frames = [paint(1), paint(2)]
    return strip(frames)


def sprite_name(key):
    return SPRITES[key][1]


def texture_path(key):
    return f'{TEXTURE_DIR}/{SPRITES[key][0]}'


def gfx_text():
    lines = ['spriteTypes = {']
    for key, (_, name, _, frames) in SPRITES.items():
        extra = f' noOfFrames = {frames}' if frames > 1 else ''
        norefcount = ' norefcount = yes' if key == 'reform' else ''
        lines.append(f'\tspriteType = {{ name = "{name}" texturefile = "{texture_path(key)}"{extra}{norefcount} }}')
    lines.append('}')
    return '\r\n'.join(lines) + '\r\n'


def preview_sheet(scale, columns=3):
    keys = list(SPRITES)
    images = [render(k) for k in keys]
    cell_w = max(im.width for im in images) * scale + 12
    cell_h = max(im.height for im in images) * scale + 12
    sheet = Image.new('RGBA', (columns * cell_w + 12, ((len(images) + columns - 1) // columns) * cell_h + 12), (22, 40, 42, 255))
    for i, im in enumerate(images):
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
        sheet.alpha_composite(big, (12 + (i % columns) * cell_w, 12 + (i // columns) * cell_h))
    return sheet


def write_all():
    for key in SPRITES:
        path = ROOT / texture_path(key)
        kit.save_dds_atomic(render(key), path)
    (ROOT / GFX_FILE).write_bytes(gfx_text().encode('ascii'))
    print(f'wrote {len(SPRITES)} sprites and {GFX_FILE}')


def check_all():
    problems = []
    gfx = ROOT / GFX_FILE
    if not gfx.is_file() or gfx.read_bytes() != gfx_text().encode('ascii'):
        problems.append(f'{GFX_FILE} is stale')
    for key in SPRITES:
        path = ROOT / texture_path(key)
        if not path.is_file():
            problems.append(f'{texture_path(key)} is missing')
            continue
        have = np.asarray(Image.open(path).convert('RGBA'), dtype=np.int16)
        want = np.asarray(render(key), dtype=np.int16)
        worst = int(np.abs(have - want).max()) if have.shape == want.shape else 999
        if worst > CHECK_TOLERANCE:
            problems.append(f'{texture_path(key)} differs from a fresh drawing (max channel difference {worst})')
    if problems:
        print('\n'.join(problems))
        return 1
    print(f'UZH STATES GENERAL ICONS PASS: {len(SPRITES)} sprites match the generator (tolerance {CHECK_TOLERANCE}).')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='redraw and compare with the files in the repository')
    parser.add_argument('--preview', metavar='PNG', help='write a contact sheet instead of the sprites')
    parser.add_argument('--scale', type=int, default=6)
    args = parser.parse_args(argv)
    if args.preview:
        preview_sheet(args.scale).save(args.preview)
        print('preview written', args.preview)
        return 0
    if args.check:
        return check_all()
    write_all()
    return 0


if __name__ == '__main__':
    sys.exit(main())
