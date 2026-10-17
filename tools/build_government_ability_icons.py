"""Draw the button icons of the Galician and Volhynian government abilities.

Fifteen 82x82 sprites for four button-only mechanics:

  rip_hlc_boyar_council           3 buttons   round gold frame, crimson enamel
  rip_hlc_austrian_reorganization 6 buttons   black-and-gold octagon
  rip_vln_magnate_senate          3 buttons   arched gold frame, blue enamel
  rip_lit_pany_rada               3 buttons   shield frame, scarlet enamel, silver inner line

They replace the vanilla Cossack ability sprites these mechanics used to
borrow. The art is painted procedurally - polygons, gradients, a lit height
field and noise, supersampled 8x - so no image model and no external file is
involved, and --check can redraw every sprite and compare it with the
checked-in DDS. The edge length follows vanilla's own mechanic buttons
(devshirme, iqta, council of ten: 82x82); the frames follow its habit of one
frame shape per mechanic with a different picture inside.

    python tools/build_government_ability_icons.py            # write DDS + gfx
    python tools/build_government_ability_icons.py --check    # redraw and compare
    python tools/build_government_ability_icons.py --preview out.png --scale 4
    python tools/build_government_ability_icons.py --only boyar_office --preview x.png
    python tools/build_government_ability_icons.py --only rada_confirm --only rada_lord --only rada_retinues --preview x.png --columns 3
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from functools import reduce
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SIZE = 82            # final sprite edge: vanilla's mechanic buttons are 82x82
SS = 8               # supersampling factor
S = SIZE * SS
LIGHT = (-0.55, -0.70, 0.62)          # light comes from the upper left
TEXTURE_DIR = 'gfx/interface/rip_government'
GFX_FILE = 'interface/rip_ability_icons.gfx'
CHECK_TOLERANCE = 3                    # per channel; float maths differs a little between machines


# --------------------------------------------------------------------------
# Toolkit. Coordinates are sprite units (0..82); a mask is an 'L' image at
# supersampled size, a layer an 'RGBA' image of the same size.
# --------------------------------------------------------------------------

def _px(points):
    return [(x * SS, y * SS) for x, y in points]


def hexc(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def blank_mask():
    return Image.new('L', (S, S), 0)


def full_mask():
    return Image.new('L', (S, S), 255)


def blank_layer():
    return Image.new('RGBA', (S, S), (0, 0, 0, 0))


def poly(points):
    mask = blank_mask()
    ImageDraw.Draw(mask).polygon(_px(points), fill=255)
    return mask


def rotate_points(points, angle, origin=(0, 0), shift=(0, 0)):
    ca, sa = math.cos(angle), math.sin(angle)
    ox, oy = origin
    return [(ox + (x - ox) * ca - (y - oy) * sa + shift[0],
             oy + (x - ox) * sa + (y - oy) * ca + shift[1]) for x, y in points]


def place(points, degrees, at):
    """Rotate local points (y down, positive degrees turn clockwise on screen) and move them to `at`."""
    return rotate_points(points, math.radians(degrees), shift=at)


def ellipse(cx, cy, rx, ry=None, degrees=0.0):
    ry = rx if ry is None else ry
    if not degrees:
        mask = blank_mask()
        ImageDraw.Draw(mask).ellipse(
            [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=255)
        return mask
    points = [(rx * math.cos(t), ry * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 120, endpoint=False)]
    return poly(place(points, degrees, (cx, cy)))


def stroke(points, width, caps=True):
    mask = blank_mask()
    draw = ImageDraw.Draw(mask)
    pixels = _px(points)
    w = max(1, int(round(width * SS)))
    draw.line(pixels, fill=255, width=w, joint='curve')
    if caps:
        r = w / 2.0
        for x, y in (pixels[0], pixels[-1]):
            draw.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return mask


def bezier(p0, p1, p2, p3, n=28):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def arc_points(cx, cy, rx, ry, a0, a1, n=32):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


def union(*masks):
    return reduce(ImageChops.lighter, masks)


def minus(a, b):
    return ImageChops.subtract(a, b)


def inter(a, b):
    return ImageChops.multiply(a, b)


def blur(mask, radius):
    return mask.filter(ImageFilter.GaussianBlur(radius * SS))


def move(mask, dx, dy):
    return mask.transform(mask.size, Image.AFFINE, (1, 0, -dx * SS, 0, 1, -dy * SS), Image.BILINEAR)


def grow(mask, radius):
    """Dilate by `radius` units (a soft threshold on a blurred copy)."""
    sigma = max(0.5, radius * SS / 1.28)
    blurred = np.asarray(mask.filter(ImageFilter.GaussianBlur(sigma)), dtype=np.float32) / 255.0
    return Image.fromarray((np.clip((blurred - 0.1) * 10.0, 0, 1) * 255).astype(np.uint8), 'L')


def scaled(mask, factor):
    return mask.point(lambda v: int(v * factor))


def solid(mask, color, alpha=1.0):
    layer = Image.new('RGBA', (S, S), tuple(color) + (0,))
    layer.putalpha(scaled(mask, alpha) if alpha != 1.0 else mask)
    return layer


def from_alpha(color, alpha):
    """A flat colour layer whose alpha is a float array in 0..1."""
    rgba = np.zeros((S, S, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def over(base, *tops):
    for top in tops:
        base = Image.alpha_composite(base, top)
    return base


def clip(layer, mask):
    layer = layer.copy()
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))
    return layer


def turn(layer, degrees, cx, cy):
    """Turn a whole layer about a point; positive degrees turn clockwise on screen."""
    return layer.rotate(-degrees, resample=Image.BICUBIC, center=(cx * SS, cy * SS))


def ramp(values, stops):
    """Map an array in 0..1 through colour stops [(pos, (r, g, b)), ...]."""
    values = np.clip(values, 0.0, 1.0)
    positions = [p for p, _ in stops]
    out = np.zeros(values.shape + (3,), dtype=np.float32)
    for channel in range(3):
        out[..., channel] = np.interp(values, positions, [c[channel] for _, c in stops])
    return out


def _to_layer(rgb, mask):
    rgba = np.dstack([np.clip(rgb, 0, 255), np.asarray(mask, dtype=np.float32)]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


_GRID = np.mgrid[0:S, 0:S].astype(np.float32)


def gradient(mask, stops, p0, p1):
    """Linear gradient between two sprite-unit points, clipped to the mask."""
    yy, xx = _GRID
    dx, dy = (p1[0] - p0[0]) * SS, (p1[1] - p0[1]) * SS
    t = ((xx - p0[0] * SS) * dx + (yy - p0[1] * SS) * dy) / max(1.0, dx * dx + dy * dy)
    return _to_layer(ramp(t, stops), mask)


def radial(mask, stops, center, radius):
    yy, xx = _GRID
    t = np.hypot(xx - center[0] * SS, yy - center[1] * SS) / (radius * SS)
    return _to_layer(ramp(t, stops), mask)


def shaded(mask, stops, softness=1.0, relief=None, light=LIGHT, gain=1.7, spec=0.0, texture=None):
    """Colour a silhouette by lighting its blurred height field (a bevel for any shape).

    The flat interior takes the middle of the colour ramp, edges that face the
    light go brighter, edges that face away go darker; `spec` adds a pale glint.
    """
    relief = 2.2 * softness if relief is None else relief
    height = np.asarray(blur(mask, softness), dtype=np.float32) / 255.0 * relief * SS
    gy, gx = np.gradient(height)
    norm = np.sqrt(gx * gx + gy * gy + 1.0)
    lx, ly, lz = light
    ln = math.sqrt(lx * lx + ly * ly + lz * lz)
    flat = lz / ln
    diffuse = np.clip((-gx * lx - gy * ly + lz) / (norm * ln), 0, 1)
    t = 0.5 + (diffuse - flat) * gain
    if texture is not None:
        t = t + (texture - 0.5) * 0.35
    rgb = ramp(t, stops)
    if spec:
        glint = np.clip((t - 0.72) / 0.28, 0, 1) ** 2 * spec * 255.0
        rgb = rgb + glint[..., None]
    return _to_layer(rgb, mask)


def roundness(mask, x0, x1, dark=0.55, lift=0.22, peak=0.30):
    """Cylinder lighting across x: bright near `peak`, dark toward the far edge."""
    xx = _GRID[1]
    t = np.clip((xx / SS - x0) / (x1 - x0), 0, 1)
    shade_a = (t ** 1.7) * dark
    lift_a = np.exp(-(((t - peak) / 0.17) ** 2)) * lift
    m = np.asarray(mask, dtype=np.float32) / 255.0
    return over(from_alpha((0, 0, 0), shade_a * m), from_alpha((255, 244, 214), lift_a * m))


def glow(cx, cy, radius, color, alpha=0.5):
    yy, xx = _GRID
    t = np.hypot(xx - cx * SS, yy - cy * SS) / (radius * SS)
    return from_alpha(color, np.clip(1 - t, 0, 1) ** 2 * alpha)


def shadow(mask, dx=0.9, dy=1.3, softness=1.3, alpha=0.55, color=(0, 0, 0)):
    return solid(blur(move(mask, dx, dy), softness), color, alpha)


def outline(mask, width=0.7, color=(20, 10, 6), alpha=0.9):
    return solid(minus(grow(mask, width), mask), color, alpha)


def noise(seed, cell, octaves=2):
    """Smooth value noise in 0..1 (cell in sprite units)."""
    rng = np.random.RandomState(seed)
    total = np.zeros((S, S), dtype=np.float32)
    weight, amp = 0.0, 1.0
    for octave in range(octaves):
        size = max(2, int(S / (cell * SS / (2 ** octave))) + 2)
        grid = rng.rand(size, size).astype(np.float32)
        img = Image.fromarray((grid * 255).astype(np.uint8), 'L').resize((S, S), Image.BICUBIC)
        total += np.asarray(img, dtype=np.float32) / 255.0 * amp
        weight += amp
        amp *= 0.5
    return total / weight


def tint(layer, factor):
    arr = np.asarray(layer, dtype=np.float32).copy()
    f = np.array(factor if isinstance(factor, tuple) else (factor,) * 3, dtype=np.float32)
    arr[..., :3] = np.clip(arr[..., :3] * f, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')


def desaturate(layer, amount):
    arr = np.asarray(layer, dtype=np.float32).copy()
    grey = arr[..., :3] @ np.array([0.30, 0.59, 0.11], dtype=np.float32)
    arr[..., :3] = arr[..., :3] * (1 - amount) + grey[..., None] * amount
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')


def strands(mask, seed, count, length, width, colors, direction, spread=0.5):
    """Short hair-like strokes inside a mask (fur, thatch, grain)."""
    rng = random.Random(seed)
    layer = blank_layer()
    draw = ImageDraw.Draw(layer)
    box = mask.getbbox()
    if not box:
        return layer
    x0, y0, x1, y1 = [v / SS for v in box]
    produced = attempts = 0
    probe = mask.load()
    while produced < count and attempts < count * 14:
        attempts += 1
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        if probe[min(S - 1, int(x * SS)), min(S - 1, int(y * SS))] < 128:
            continue
        angle = direction(x, y) + rng.uniform(-spread, spread)
        ln = length * rng.uniform(0.6, 1.3)
        color = colors[rng.randrange(len(colors))]
        draw.line([(x * SS, y * SS), ((x + math.cos(angle) * ln) * SS, (y + math.sin(angle) * ln) * SS)],
                  fill=color + (rng.randint(150, 235),), width=max(1, int(width * SS)))
        produced += 1
    return clip(layer, mask)


# --------------------------------------------------------------------------
# Palettes (dark -> lit)
# --------------------------------------------------------------------------

GOLD = [(0.0, hexc('#3a2208')), (0.30, hexc('#8a5a14')), (0.5, hexc('#d6a22a')),
        (0.72, hexc('#f3d36a')), (1.0, hexc('#fff3b8'))]
STEEL = [(0.0, hexc('#1e262e')), (0.35, hexc('#5a6a78')), (0.5, hexc('#9aa8b4')),
         (0.75, hexc('#d6e0e8')), (1.0, hexc('#ffffff'))]
PARCHMENT = [(0.0, hexc('#8a6a3a')), (0.35, hexc('#c8a96a')), (0.5, hexc('#e8d9a8')),
             (0.8, hexc('#f6ecc8')), (1.0, hexc('#fffbe8'))]
WOOD = [(0.0, hexc('#2a160a')), (0.4, hexc('#5a3418')), (0.6, hexc('#7d4e26')),
        (0.85, hexc('#a8703a')), (1.0, hexc('#d0a066'))]
DARK_WOOD = [(0.0, hexc('#120904')), (0.4, hexc('#2e1a0c')), (0.6, hexc('#472a14')),
             (0.85, hexc('#6a4424')), (1.0, hexc('#a07a4a'))]
LEATHER = [(0.0, hexc('#1e0f06')), (0.4, hexc('#4a2a12')), (0.6, hexc('#6a3e1c')),
           (0.85, hexc('#8c5a2c')), (1.0, hexc('#c08a50'))]
FUR = [(0.0, hexc('#120a06')), (0.4, hexc('#2e1c10')), (0.6, hexc('#4a2e1a')),
       (0.85, hexc('#6e4c2e')), (1.0, hexc('#9a7a54'))]
VELVET_RED = [(0.0, hexc('#2a0508')), (0.4, hexc('#6a0e14')), (0.6, hexc('#9a1a22')),
              (0.85, hexc('#c4323a')), (1.0, hexc('#ee7a74'))]
WAX = [(0.0, hexc('#2e0606')), (0.4, hexc('#7a1010')), (0.6, hexc('#a81818')),
       (0.85, hexc('#d03a30')), (1.0, hexc('#ff9a88'))]
SKIN = [(0.0, hexc('#6a3a22')), (0.4, hexc('#c8885a')), (0.6, hexc('#e0aa80')),
        (0.85, hexc('#f2cba4')), (1.0, hexc('#fff2de'))]
BLUE_CLOTH = [(0.0, hexc('#08183a')), (0.4, hexc('#143a78')), (0.6, hexc('#2058a0')),
              (0.85, hexc('#4a86cc')), (1.0, hexc('#a8c8f0'))]
GREEN_CLOTH = [(0.0, hexc('#08240e')), (0.4, hexc('#145a24')), (0.6, hexc('#24803a')),
               (0.85, hexc('#4aac5e')), (1.0, hexc('#a8e0b0'))]
CANVAS = [(0.0, hexc('#8a7a5a')), (0.4, hexc('#cfc09a')), (0.6, hexc('#ece0bc')),
          (0.85, hexc('#fbf3d8')), (1.0, hexc('#ffffff'))]
THATCH = [(0.0, hexc('#4a3512')), (0.4, hexc('#8a6a28')), (0.6, hexc('#b8903a')),
          (0.85, hexc('#dcb858')), (1.0, hexc('#f8e090'))]
STONE = [(0.0, hexc('#22262e')), (0.4, hexc('#4c5668')), (0.6, hexc('#6e7a90')),
         (0.85, hexc('#98a6bc')), (1.0, hexc('#d4deee'))]
BLACK_ENAMEL = [(0.0, hexc('#050505')), (0.5, hexc('#161616')), (1.0, hexc('#46464a'))]
CRIMSON_ENAMEL = [(0.0, hexc('#2a0608')), (0.5, hexc('#6a1414')), (1.0, hexc('#b03028'))]
BLUE_ENAMEL = [(0.0, hexc('#08142e')), (0.5, hexc('#16336a')), (1.0, hexc('#3a68b0'))]

# Pany Rada: the Grand Duchy's red field, the Pahonia's silver, horses, coats and wax
SCARLET_ENAMEL = [(0.0, hexc('#38060a')), (0.5, hexc('#9a1218')), (1.0, hexc('#e04030'))]
SCARLET_FIELD = [(0.0, hexc('#3a060a')), (0.4, hexc('#8a1016')), (0.6, hexc('#b8161e')), (0.85, hexc('#e0302c')), (1.0, hexc('#ff7a66'))]
SILVER_LINE = [(0.0, hexc('#4a5460')), (0.45, hexc('#a8b4c0')), (0.75, hexc('#e8eef4')), (1.0, hexc('#ffffff'))]
SILVER_WHITE = [(0.0, hexc('#7c889c')), (0.40, hexc('#c4ccd9')), (0.62, hexc('#e6ebf2')), (0.85, hexc('#fafcff')), (1.0, hexc('#ffffff'))]
SILVER_PLATE = [(0.0, hexc('#46525f')), (0.40, hexc('#8d9aa8')), (0.62, hexc('#c2ccd6')), (0.85, hexc('#e8eef4')), (1.0, hexc('#ffffff'))]
BAY = [(0.0, hexc('#1a0c06')), (0.40, hexc('#42220f')), (0.62, hexc('#64371a')), (0.85, hexc('#8a5428')), (1.0, hexc('#b8854e'))]
DUN = [(0.0, hexc('#2a1c0e')), (0.40, hexc('#6a4a24')), (0.62, hexc('#8c6a38')), (0.85, hexc('#b8925a')), (1.0, hexc('#e2c48a'))]
GREY_HORSE = [(0.0, hexc('#2e3640')), (0.40, hexc('#6a7684')), (0.62, hexc('#8e9aa8')), (0.85, hexc('#c0cad4')), (1.0, hexc('#eef2f6'))]
BLACK_HORSE = [(0.0, hexc('#050608')), (0.40, hexc('#16181c')), (0.62, hexc('#262a30')), (0.85, hexc('#40464e')), (1.0, hexc('#6a727c'))]
MAIL = [(0.0, hexc('#20262e')), (0.40, hexc('#4c5866')), (0.62, hexc('#76828f')), (0.85, hexc('#aab6c2')), (1.0, hexc('#e4ecf2'))]
RED_COAT = [(0.0, hexc('#2a0508')), (0.4, hexc('#7a1018')), (0.62, hexc('#a81c24')), (0.85, hexc('#d04040')), (1.0, hexc('#f08a80'))]
SKY_BLUE_COAT = [(0.0, hexc('#0a1830')), (0.4, hexc('#1c4478')), (0.62, hexc('#2c64a8')), (0.85, hexc('#5a92d0')), (1.0, hexc('#b0d0f4'))]
YELLOW_COAT = [(0.0, hexc('#3a2a06')), (0.4, hexc('#8a6a14')), (0.62, hexc('#c49a22')), (0.85, hexc('#e8c448')), (1.0, hexc('#fff0a0'))]
BEARD_GREY = [(0.0, hexc('#585c60')), (0.5, hexc('#a8acb0')), (1.0, hexc('#f0f2f4'))]
BEARD_BROWN = [(0.0, hexc('#1a0e08')), (0.5, hexc('#4a2c18')), (1.0, hexc('#8a6444'))]
SABLE = [(0.0, hexc('#0c0604')), (0.4, hexc('#241408')), (0.62, hexc('#3a2410')), (0.85, hexc('#5c3e20')), (1.0, hexc('#8a6a40'))]
WAX_GREEN = [(0.0, hexc('#08240e')), (0.4, hexc('#1c5a2a')), (0.6, hexc('#2c7c3c')), (0.85, hexc('#52a862')), (1.0, hexc('#b0e8b8'))]
WAX_YELLOW = [(0.0, hexc('#3a2a06')), (0.4, hexc('#8a6a14')), (0.6, hexc('#c49a22')), (0.85, hexc('#e8c448')), (1.0, hexc('#fff0a0'))]


# --------------------------------------------------------------------------
# Frames
# --------------------------------------------------------------------------

def octagon_points(cx, cy, radius):
    return [(cx + radius * math.cos(math.pi / 8 + i * math.pi / 4) / math.cos(math.pi / 8),
             cy + radius * math.sin(math.pi / 8 + i * math.pi / 4) / math.cos(math.pi / 8)) for i in range(8)]


def arch_poly(cx, width, top, bottom):
    half = width / 2.0
    pts = [(cx - half, bottom), (cx - half, top + half)]
    pts += arc_points(cx, top + half, half, half, math.pi, 2 * math.pi, 40)
    pts += [(cx + half, top + half), (cx + half, bottom)]
    return poly(pts)


def erode(mask, radius):
    """Shrink by `radius` units (the dual of grow)."""
    return ImageChops.invert(grow(ImageChops.invert(mask), radius))


def shield_poly(cx, hw, top, bottom, shoulder=0.44):
    """A heater shield silhouette: flat top, straight flanks, a rounded point."""
    h = bottom - top
    ys = top + h * shoulder
    pts = [(cx - hw, top + 1.2), (cx - hw + 1.2, top), (cx + hw - 1.2, top), (cx + hw, top + 1.2), (cx + hw, ys)]
    pts += bezier((cx + hw, ys), (cx + hw, ys + h * 0.30), (cx + hw * 0.42, bottom - h * 0.10), (cx, bottom), 32)[1:]
    pts += bezier((cx, bottom), (cx - hw * 0.42, bottom - h * 0.10), (cx - hw, ys + h * 0.30), (cx - hw, ys), 32)[1:]
    return poly(pts)


def frame_masks(kind):
    """Outer silhouette, inner edge of the gold band, of the enamel, and the picture area."""
    c = SIZE / 2.0
    if kind == 'round':
        return ellipse(c, c, 40.0), ellipse(c, c, 35.2), ellipse(c, c, 33.4), ellipse(c, c, 32.6)
    if kind == 'octagon':
        return (poly(octagon_points(c, c, 40.4)), poly(octagon_points(c, c, 35.8)),
                poly(octagon_points(c, c, 33.2)), poly(octagon_points(c, c, 32.2)))
    if kind == 'arch':
        return (arch_poly(c, 70, 2.4, 79.6), arch_poly(c, 61.6, 6.8, 75.2),
                arch_poly(c, 58.0, 8.6, 73.4), arch_poly(c, 56.4, 9.4, 72.6))
    if kind == 'shield':
        outer = shield_poly(c, 36.0, 3.0, 79.4)
        return outer, erode(outer, 4.3), erode(outer, 6.1), erode(outer, 6.9)
    raise ValueError(kind)


INNER_LINE = {'shield': SILVER_LINE}      # every other frame keeps a gold inner line


def draw_frame(kind, enamel_stops, scene_layer):
    """A finished sprite: drop shadow, picture, enamel, gold band with its bevel."""
    outer, gold_in, enamel_in, scene = frame_masks(kind)
    band = minus(outer, gold_in)
    enamel = minus(gold_in, enamel_in)
    inner_line = minus(enamel_in, scene)
    sprite = blank_layer()
    sprite = over(sprite, shadow(outer, 0.6, 1.0, 0.9, 0.6))
    picture = clip(scene_layer, scene)
    # the picture sinks a little into the enamel: darken a thin rim inside it
    rim_depth = np.asarray(ImageChops.invert(blur(scene, 2.6)), dtype=np.float32) / 255.0
    sprite = over(sprite, picture, from_alpha((0, 0, 0), rim_depth * (np.asarray(scene, dtype=np.float32) / 255.0) * 0.38))
    sprite = over(sprite, shaded(enamel, enamel_stops, 0.5, relief=1.3, gain=1.5))
    sprite = over(sprite, shaded(inner_line, INNER_LINE.get(kind, GOLD), 0.3, relief=0.7, gain=1.6))
    sprite = over(sprite, shaded(band, GOLD, 1.3, relief=3.0, gain=1.9, spec=0.25, texture=noise(7, 1.6, 2)))
    sprite = over(sprite, outline(outer, 0.45, (24, 12, 4), 0.95))
    return sprite


# --------------------------------------------------------------------------
# Props
# --------------------------------------------------------------------------

def backdrop(stops, center, radius):
    return radial(full_mask(), stops, center, radius)


def contact(cx, cy, rx, ry, alpha=0.5):
    return solid(blur(ellipse(cx, cy, rx, ry), 1.1), (0, 0, 0), alpha)


def fur_hat(cx, base_y, width, height, seed=1, degrees=0.0):
    """A boyar's tall fur hat (gorlatna shapka): fur drum, crimson velvet top with gold braid."""
    top_y = base_y - height
    wt = width * 1.42
    left = bezier((cx - width / 2, base_y), (cx - width * 0.46, base_y - height * 0.34),
                  (cx - wt * 0.47, base_y - height * 0.70), (cx - wt / 2, top_y))
    right = bezier((cx + wt / 2, top_y), (cx + wt * 0.47, base_y - height * 0.70),
                   (cx + width * 0.46, base_y - height * 0.34), (cx + width / 2, base_y))
    ry_base = width * 0.13
    bottom = arc_points(cx, base_y, width / 2, ry_base, 0, math.pi, 28)
    body = poly(left + right + bottom)
    top_rim = ellipse(cx, top_y, wt / 2, wt * 0.17)
    drum = union(body, top_rim)
    layer = blank_layer()
    layer = over(layer, shadow(drum, 1.0, 1.4, 1.4, 0.5))
    layer = over(layer, outline(drum, 0.7))
    layer = over(layer, shaded(drum, FUR, 1.6, relief=2.6, gain=1.5, texture=noise(seed, 0.9, 3)))
    layer = over(layer, strands(drum, seed, int(width * height * 5.5), width * 0.22, 0.17,
                                [hexc('#0e0805'), hexc('#2a180d'), hexc('#4a2e1a'), hexc('#6e4c2e'), hexc('#a88a60')],
                                lambda x, y: math.pi / 2 + (x - cx) * 0.05, spread=0.45))
    layer = over(layer, roundness(drum, cx - wt / 2, cx + wt / 2, dark=0.55, lift=0.20, peak=0.28))
    foot = np.clip((np.mgrid[0:S, 0:S][0] / SS - (base_y - height * 0.35)) / (height * 0.35 + ry_base), 0, 1)
    layer = over(layer, from_alpha((0, 0, 0), foot * 0.5 * (np.asarray(drum, dtype=np.float32) / 255.0)))
    velvet = ellipse(cx, top_y, wt * 0.44, wt * 0.135)
    layer = over(layer, outline(velvet, 0.35, (20, 4, 6), 0.9))
    layer = over(layer, shaded(velvet, VELVET_RED, 0.8, relief=1.3, gain=1.5, spec=0.2))
    braid = union(stroke([(cx - wt * 0.38, top_y), (cx + wt * 0.38, top_y)], 0.5),
                  stroke([(cx, top_y - wt * 0.11), (cx, top_y + wt * 0.11)], 0.5))
    layer = over(layer, shaded(inter(braid, velvet), GOLD, 0.2, relief=0.5, gain=1.8))
    layer = over(layer, shaded(ellipse(cx, top_y, wt * 0.06), GOLD, 0.3, relief=0.8, gain=1.8, spec=0.5))
    return turn(layer, degrees, cx, base_y) if degrees else layer


def charter(cx, cy, w, h, seed=3, degrees=0.0, lines=5, seal_r=5.0, broken=False, torn=False,
            cords=((150, 24, 28), (214, 164, 44))):
    """An unrolled charter with its script, rolled ends and a hanging wax seal."""
    x, y = cx - w / 2, cy - h / 2
    curl = max(2.0, h * 0.075)
    sheet_pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    if torn:
        zig = [(x + w, y + h * 0.38)]
        n = 9
        for i in range(1, n):
            zig.append((x + w - w * i / n, y + h * (0.55 - 0.1 * (i % 2) + 0.05 * math.sin(i))))
        zig.append((x, y + h * 0.62))
        sheet_pts = [(x, y), (x + w, y), *zig, (x, y + h * 0.62)]
    sheet = poly(sheet_pts)
    layer = blank_layer()
    layer = over(layer, shadow(sheet, 0.9, 1.3, 1.1, 0.5))
    layer = over(layer, outline(sheet, 0.55, (46, 28, 10), 0.9))
    paper = gradient(sheet, PARCHMENT, (x, y), (x + w * 0.9, y + h))
    layer = over(layer, paper)
    grain = np.asarray(sheet, dtype=np.float32) / 255.0 * (noise(seed, 0.7, 3) - 0.5) * 0.32
    layer = over(layer, from_alpha((60, 36, 12), np.clip(grain, 0, 1)), from_alpha((255, 250, 225), np.clip(-grain, 0, 1)))
    ink = blank_mask()
    rng = random.Random(seed)
    top = y + curl + 1.6
    gap = (h * (0.62 if torn else 1.0) - 2 * curl - 3.4) / max(1, lines)
    for i in range(lines):
        yy = top + gap * (i + 0.5)
        x0 = x + 2.3 + (3.4 if i == 0 else 0.0)
        x1 = x + w - 2.3 - (rng.uniform(0.0, w * 0.35) if i == lines - 1 else rng.uniform(0.0, 1.0))
        ImageDraw.Draw(ink).line(_px([(x0, yy), (x1, yy + rng.uniform(-0.12, 0.12))]), fill=255, width=max(1, int(0.55 * SS)))
    layer = over(layer, solid(inter(ink, sheet), (74, 46, 22), 0.66))
    initial = poly([(x + 2.3, top + gap * 0.1), (x + 5.4, top + gap * 0.1), (x + 5.4, top + gap * 1.0), (x + 2.3, top + gap * 1.0)])
    layer = over(layer, solid(initial, (150, 24, 28), 0.85))
    for ry in (y, y + (h * 0.62 if torn else h) - curl):
        roll = poly([(x - 0.9, ry), (x + w + 0.9, ry), (x + w + 0.9, ry + curl), (x - 0.9, ry + curl)])
        layer = over(layer, outline(roll, 0.45, (46, 28, 10), 0.9))
        layer = over(layer, shaded(roll, PARCHMENT, 0.5, relief=1.5, gain=1.7))
        for ex in (x - 0.9, x + w + 0.9):
            end = ellipse(ex, ry + curl / 2, curl * 0.42, curl * 0.5)
            layer = over(layer, solid(end, (96, 66, 30), 0.85), solid(ellipse(ex, ry + curl / 2, curl * 0.2, curl * 0.26), (230, 208, 150), 0.9))
    if seal_r:
        base_y = y + (h * 0.62 if torn else h)
        sx, sy = cx + w * 0.12, base_y + seal_r * 0.8
        for dx, color in zip((-0.7, 0.9), cords):
            cord = stroke([(sx + dx * 0.4, base_y - 1.0), (sx + dx * 0.8, base_y + seal_r * 0.4), (sx + dx * 1.2, sy - seal_r * 0.4)], 0.6)
            layer = over(layer, solid(cord, color, 0.95))
        layer = over(layer, wax_seal(sx, sy, seal_r, seed=seed + 1, broken=broken))
    return turn(layer, degrees, cx, cy) if degrees else layer


def tear_apart(layer, y_left, y_right, seed=4, gap=(1.0, 1.9), turn_lower=3.5):
    """Split a layer along a ragged diagonal and pull the halves apart: a torn document."""
    rng = random.Random(seed)
    steps = 14
    line = [(82.0 * i / steps, y_left + (y_right - y_left) * i / steps + (rng.uniform(-1.1, 1.1) if 0 < i < steps else 0.0))
            for i in range(steps + 1)]
    upper = poly([(0, 0), (82, 0)] + line[::-1])
    lower = ImageChops.invert(upper)
    top, bottom = clip(layer, upper), clip(layer, lower)
    edge = stroke(line, 0.5)
    top = over(top, clip(solid(edge, (70, 44, 20), 0.85), upper))
    bottom = over(bottom, clip(solid(edge, (70, 44, 20), 0.85), lower))
    bottom = turn(bottom, turn_lower, 41, 60)
    bx, by = gap
    bottom = bottom.transform(bottom.size, Image.AFFINE, (1, 0, -bx * SS, 0, 1, -by * SS), Image.BILINEAR)
    top = top.transform(top.size, Image.AFFINE, (1, 0, 0.4 * SS, 0, 1, 0.7 * SS), Image.BILINEAR)
    return over(blank_layer(), shadow(ImageChops.lighter(top.getchannel('A'), bottom.getchannel('A')), 0.7, 1.0, 0.8, 0.35), bottom, top)


def wax_seal(cx, cy, r, seed=5, broken=False):
    rng = random.Random(seed)
    pts = []
    for i in range(36):
        a = 2 * math.pi * i / 36
        rr = r + rng.uniform(-0.1, 0.1) * r + 0.1 * r * math.sin(5 * a)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    blob = poly(pts)
    layer = blank_layer()
    layer = over(layer, shadow(blob, 0.7, 1.0, 0.9, 0.5))
    layer = over(layer, outline(blob, 0.4, (30, 4, 4), 0.9))
    layer = over(layer, shaded(blob, WAX, 0.9, relief=2.0, gain=1.7, spec=0.35))
    ring = minus(ellipse(cx, cy, r * 0.66), ellipse(cx, cy, r * 0.5))
    layer = over(layer, shaded(ring, WAX, 0.3, relief=0.9, gain=2.2, spec=0.25))
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r * (0.36 if i % 2 == 0 else 0.16)
        star.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    layer = over(layer, shaded(poly(star), WAX, 0.28, relief=0.8, gain=2.4, spec=0.2))
    if broken:
        crack = stroke([(cx - r * 0.25, cy - r * 1.1), (cx + r * 0.05, cy - r * 0.3), (cx - r * 0.15, cy + r * 0.25),
                        (cx + r * 0.25, cy + r * 1.1)], 0.4)
        layer = over(layer, solid(minus(inter(crack, blob), blank_mask()), (14, 2, 2), 1.0))
    return layer


def crown(cx, base_y, width, height, degrees=0.0):
    """A foreign royal crown: gold band, fleurons, arches under an orb and cross, red cap."""
    layer = blank_layer()
    hw = width / 2.0
    band_h = height * 0.30
    cap = poly([(cx - hw * 0.86, base_y - band_h)] + bezier((cx - hw * 0.86, base_y - band_h), (cx - hw * 0.9, base_y - height * 0.8),
                (cx - hw * 0.3, base_y - height * 0.95), (cx, base_y - height * 0.95)) +
               bezier((cx, base_y - height * 0.95), (cx + hw * 0.3, base_y - height * 0.95), (cx + hw * 0.9, base_y - height * 0.8),
                      (cx + hw * 0.86, base_y - band_h)))
    layer = over(layer, shadow(cap, 1.0, 1.4, 1.2, 0.5))
    layer = over(layer, outline(cap, 0.5, (30, 4, 6), 0.9))
    layer = over(layer, shaded(cap, VELVET_RED, 1.4, relief=3.0, gain=1.5, spec=0.15))
    band = poly([(cx - hw, base_y), (cx + hw, base_y), (cx + hw * 0.93, base_y - band_h), (cx - hw * 0.93, base_y - band_h)])
    fleurons = []
    for i in range(5):
        fx = cx - hw * 0.93 + (hw * 1.86) * i / 4.0
        fh = height * (0.62 if i in (0, 4) else (0.5 if i in (1, 3) else 0.56))
        fleurons.append(poly([(fx - hw * 0.14, base_y - band_h + 0.4), (fx, base_y - fh), (fx + hw * 0.14, base_y - band_h + 0.4)]))
    ring_arch = [stroke(bezier((cx - hw * 0.9, base_y - band_h), (cx - hw * 0.8, base_y - height * 1.0),
                               (cx - hw * 0.2, base_y - height * 1.04), (cx, base_y - height * 0.97)), height * 0.085),
                 stroke(bezier((cx + hw * 0.9, base_y - band_h), (cx + hw * 0.8, base_y - height * 1.0),
                               (cx + hw * 0.2, base_y - height * 1.04), (cx, base_y - height * 0.97)), height * 0.085)]
    gold = union(band, *fleurons, *ring_arch)
    layer = over(layer, outline(gold, 0.55, (40, 22, 4), 0.95))
    layer = over(layer, shaded(gold, GOLD, 0.7, relief=1.8, gain=1.9, spec=0.35))
    orb = ellipse(cx, base_y - height * 1.0, height * 0.075)
    cross = union(poly([(cx - 0.35, base_y - height * 1.2), (cx + 0.35, base_y - height * 1.2), (cx + 0.35, base_y - height * 1.0), (cx - 0.35, base_y - height * 1.0)]),
                  poly([(cx - 1.1, base_y - height * 1.12), (cx + 1.1, base_y - height * 1.12), (cx + 1.1, base_y - height * 1.07), (cx - 1.1, base_y - height * 1.07)]))
    layer = over(layer, outline(union(orb, cross), 0.35, (40, 22, 4), 0.95), shaded(union(orb, cross), GOLD, 0.35, relief=1.0, gain=1.8, spec=0.5))
    gems = [((-0.62, 'r'), (-0.31, 'w'), (0.0, 'b'), (0.31, 'w'), (0.62, 'r'))][0]
    for off, kind in gems:
        gx, gy = cx + hw * off, base_y - band_h * 0.5
        color = {'r': [(0.0, (60, 0, 8)), (0.6, (200, 20, 40)), (1.0, (255, 150, 150))],
                 'b': [(0.0, (6, 20, 70)), (0.6, (30, 90, 200)), (1.0, (170, 210, 255))],
                 'w': [(0.0, (130, 120, 110)), (0.6, (240, 236, 226)), (1.0, (255, 255, 255))]}[kind]
        layer = over(layer, shaded(ellipse(gx, gy, band_h * 0.2 if kind != 'b' else band_h * 0.27), color, 0.3, relief=0.9, gain=2.0, spec=0.6))
    return turn(layer, degrees, cx, base_y) if degrees else layer


def sword(hilt, degrees, length, blade_w=4.4, grip=7.0):
    """A straight sword drawn along +x from the hilt, then turned and placed at `hilt`."""
    pts = lambda p: place(p, degrees, hilt)
    layer = blank_layer()
    blade = poly(pts([(grip + 2.6, -blade_w / 2), (grip + 2.6 + length * 0.78, -blade_w / 2 + 0.25),
                      (grip + 2.6 + length, 0.0), (grip + 2.6 + length * 0.78, blade_w / 2 - 0.25), (grip + 2.6, blade_w / 2)]))
    fuller = stroke(pts([(grip + 5.0, 0), (grip + 2.6 + length * 0.7, 0)]), 0.7)
    guard = poly(pts([(grip, -6.0), (grip + 2.6, -6.0), (grip + 2.6, 6.0), (grip, 6.0)]))
    guard_tips = union(ellipse(*pts([(grip + 1.3, -6.0)])[0], 1.6), ellipse(*pts([(grip + 1.3, 6.0)])[0], 1.6))
    handle = poly(pts([(0.0, -1.3), (grip, -1.3), (grip, 1.3), (0.0, 1.3)]))
    pommel = ellipse(*pts([(-1.4, 0)])[0], 2.3)
    allm = union(blade, guard, guard_tips, handle, pommel)
    layer = over(layer, shadow(allm, 1.0, 1.4, 1.0, 0.5), outline(allm, 0.55, (14, 16, 20), 0.95))
    layer = over(layer, shaded(blade, STEEL, 0.8, relief=1.7, gain=1.7, spec=0.35))
    layer = over(layer, solid(fuller, (60, 74, 88), 0.55))
    layer = over(layer, shaded(handle, LEATHER, 0.35, relief=0.8, gain=1.6))
    layer = over(layer, shaded(union(guard, guard_tips, pommel), GOLD, 0.6, relief=1.5, gain=1.9, spec=0.4))
    return layer


def axe(base, degrees, length):
    """A broad Rus' axe standing on `base`, haft up, cutting edge facing right."""
    pts = lambda p: place(p, degrees, base)
    haft = poly(pts([(-1.15, 0), (1.15, 0), (0.95, -length), (-0.95, -length)]))
    top = -length + 5.0                       # the head sits just below the haft's end
    eye = poly(pts([(-1.9, top - 4.2), (1.9, top - 4.2), (1.9, top + 5.6), (-1.9, top + 5.6)]))
    edge = bezier((11.4, top - 7.2), (14.2, top - 2.0), (13.6, top + 3.0), (10.6, top + 7.4))
    blade = poly(pts([(1.9, top - 3.6), (6.4, top - 6.0)] + edge + [(6.8, top + 8.0), (1.9, top + 5.6)]))
    poll = poly(pts([(-1.9, top - 2.6), (-4.6, top - 0.6), (-1.9, top + 2.0)]))
    head = union(blade, eye, poll)
    layer = blank_layer()
    layer = over(layer, shadow(union(haft, head), 1.0, 1.4, 1.0, 0.5), outline(union(haft, head), 0.55, (16, 14, 14), 0.95))
    layer = over(layer, shaded(haft, WOOD, 0.4, relief=0.9, gain=1.6, texture=noise(21, 0.7, 2)))
    layer = over(layer, roundness(haft, base[0] - 1.2, base[0] + 1.2, dark=0.4, lift=0.15))
    layer = over(layer, shaded(head, STEEL, 1.2, relief=2.4, gain=1.25, spec=0.18))
    sharp = stroke(pts(edge), 0.5)
    layer = over(layer, solid(sharp, (250, 252, 255), 0.92))
    layer = over(layer, solid(stroke(pts([(4.6, top - 3.4), (4.2, top + 5.4)]), 0.45), (70, 84, 98), 0.5))
    return layer


def log_block(cx, base_y, width, height, seed=9):
    """A chopping block: bark drum with a ringed top."""
    ry = width * 0.17
    body = poly([(cx - width / 2, base_y - height), (cx + width / 2, base_y - height)] +
                arc_points(cx, base_y, width / 2, ry, 0, math.pi, 28)[::-1][::-1] + [(cx - width / 2, base_y)])
    body = union(body, poly([(cx - width / 2, base_y - height), (cx + width / 2, base_y - height), (cx + width / 2, base_y), (cx - width / 2, base_y)]))
    foot = ellipse(cx, base_y, width / 2, ry)
    top = ellipse(cx, base_y - height, width / 2, ry)
    solid_shape = union(body, foot, top)
    layer = blank_layer()
    layer = over(layer, contact(cx, base_y + ry * 0.6, width * 0.62, ry * 1.25, 0.55))
    layer = over(layer, outline(solid_shape, 0.7))
    layer = over(layer, shaded(minus(solid_shape, top), DARK_WOOD, 0.9, relief=2.0, gain=1.5, texture=noise(seed, 0.7, 3)))
    bark = strands(minus(solid_shape, top), seed, 260, height * 0.5, 0.2, [hexc('#0c0603'), hexc('#2a170a'), hexc('#5a3a1c')],
                   lambda x, y: math.pi / 2, spread=0.12)
    layer = over(layer, bark, roundness(minus(solid_shape, top), cx - width / 2, cx + width / 2, dark=0.5, lift=0.15))
    layer = over(layer, shaded(top, WOOD, 0.8, relief=1.2, gain=1.4, texture=noise(seed + 1, 0.6, 2)))
    for k in (0.8, 0.58, 0.36, 0.16):
        ring = minus(ellipse(cx, base_y - height, width / 2 * k, ry * k), ellipse(cx, base_y - height, width / 2 * k - 0.35, ry * k - 0.18))
        layer = over(layer, solid(ring, (60, 34, 14), 0.7))
    return layer


def purse(cx, cy, r, seed=4):
    """A heavy leather purse tied with a gold cord."""
    body = ellipse(cx, cy + r * 0.12, r, r * 0.92)
    neck = poly([(cx - r * 0.34, cy - r * 0.6), (cx + r * 0.34, cy - r * 0.6), (cx + r * 0.5, cy - r * 1.18), (cx - r * 0.5, cy - r * 1.18)])
    frill = ellipse(cx, cy - r * 1.18, r * 0.66, r * 0.24)
    whole = union(body, neck, frill)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 1.1, 1.5, 1.4, 0.55), outline(whole, 0.7))
    layer = over(layer, shaded(whole, LEATHER, 1.8, relief=4.0, gain=1.6, spec=0.2, texture=noise(seed, 0.8, 3)))
    layer = over(layer, roundness(whole, cx - r, cx + r, dark=0.45, lift=0.18))
    layer = over(layer, solid(ellipse(cx, cy - r * 1.18, r * 0.5, r * 0.15), (14, 6, 2), 0.9))
    cord = stroke([(cx - r * 0.42, cy - r * 0.62), (cx, cy - r * 0.5), (cx + r * 0.42, cy - r * 0.62)], 0.9)
    layer = over(layer, outline(cord, 0.3, (30, 18, 2), 0.9), shaded(cord, GOLD, 0.25, relief=0.7, gain=1.8, spec=0.4))
    tassel = union(stroke([(cx + r * 0.38, cy - r * 0.6), (cx + r * 0.62, cy - r * 0.1)], 0.7), poly([(cx + r * 0.52, cy - r * 0.1), (cx + r * 0.74, cy - r * 0.1), (cx + r * 0.7, cy + r * 0.22), (cx + r * 0.56, cy + r * 0.22)]))
    layer = over(layer, shaded(tassel, GOLD, 0.2, relief=0.6, gain=1.8))
    emblem = union(poly([(cx - 0.6, cy - r * 0.05), (cx + 0.6, cy - r * 0.05), (cx + 0.6, cy + r * 0.62), (cx - 0.6, cy + r * 0.62)]),
                   poly([(cx - r * 0.3, cy + r * 0.2), (cx + r * 0.3, cy + r * 0.2), (cx + r * 0.3, cy + r * 0.2 + 1.2), (cx - r * 0.3, cy + r * 0.2 + 1.2)]))
    layer = over(layer, shaded(emblem, GOLD, 0.2, relief=0.6, gain=1.8, spec=0.3))
    return layer


def coin(cx, cy, r, flat=1.0, seed=0):
    face = ellipse(cx, cy, r, r * flat)
    layer = blank_layer()
    layer = over(layer, shadow(face, 0.5, 0.7, 0.5, 0.5), outline(face, 0.3, (40, 22, 4), 0.95))
    layer = over(layer, shaded(face, GOLD, 0.5, relief=1.2, gain=1.9, spec=0.5))
    rim = minus(ellipse(cx, cy, r * 0.76, r * 0.76 * flat), ellipse(cx, cy, r * 0.6, r * 0.6 * flat))
    layer = over(layer, solid(rim, (110, 70, 14), 0.7))
    layer = over(layer, solid(ellipse(cx, cy, r * 0.22, r * 0.22 * flat), (255, 240, 170), 0.55))
    return layer


def heater_shield(cx, top, width, height, field_stops, degrees=0.0, device=None):
    """A heater shield with a gold border; `device` is 'bend', 'fess' or 'chevron'."""
    hw = width / 2.0
    outline_pts = [(cx - hw, top), (cx + hw, top)] + bezier((cx + hw, top), (cx + hw, top + height * 0.62), (cx + hw * 0.3, top + height * 0.9), (cx, top + height))[1:] + \
        bezier((cx, top + height), (cx - hw * 0.3, top + height * 0.9), (cx - hw, top + height * 0.62), (cx - hw, top))[1:]
    shield = poly(outline_pts)
    inset = poly([(cx + (x - cx) * 0.82, top + height * 0.5 + (y - top - height * 0.5) * 0.86 + height * 0.015) for x, y in outline_pts])
    layer = blank_layer()
    layer = over(layer, shadow(shield, 1.0, 1.4, 1.2, 0.55), outline(shield, 0.55, (30, 18, 4), 0.95))
    layer = over(layer, shaded(minus(shield, inset), GOLD, 0.6, relief=1.6, gain=1.9, spec=0.35))
    layer = over(layer, shaded(inset, field_stops, 1.4, relief=2.4, gain=1.4, spec=0.1))
    if device == 'bend':
        band = poly([(cx - hw, top + height * 0.18), (cx - hw, top + height * 0.02), (cx + hw, top + height * 0.7), (cx + hw, top + height * 0.86)])
        layer = over(layer, shaded(inter(band, inset), GOLD, 0.35, relief=0.9, gain=1.8, spec=0.3))
    elif device == 'chevron':
        band = stroke([(cx - hw * 0.7, top + height * 0.5), (cx, top + height * 0.28), (cx + hw * 0.7, top + height * 0.5)], height * 0.12)
        layer = over(layer, shaded(inter(band, inset), GOLD, 0.35, relief=0.9, gain=1.8, spec=0.3))
    return turn(layer, degrees, cx, top + height / 2) if degrees else layer


def banner(base, degrees, length, flag_len, flag_h, field_stops, charge='cross', seed=1, side=1):
    """A lance with a swallow-tailed banner; `side` picks which way the flag streams."""
    pts = lambda p: place(p, degrees, base)
    pole = poly(pts([(-0.55, 0), (0.55, 0), (0.5, -length), (-0.5, -length)]))
    head = poly(pts([(-1.3, -length), (1.3, -length), (0, -length - 5.0)]))
    top = -length + 2.0
    waves = 1.0 + 0.4 * (seed % 2)
    upper = [(side * (flag_len * i / 20.0), top + math.sin(i / 20.0 * math.pi * 1.4 * waves + seed) * 1.1) for i in range(21)]
    lower = [(side * (flag_len * i / 20.0), top + flag_h + math.sin(i / 20.0 * math.pi * 1.4 * waves + seed) * 1.1) for i in range(20, -1, -1)]
    notch = (side * flag_len * 0.74, top + flag_h / 2 + 0.6)
    flag_pts = upper + [notch] + lower
    flag = poly(pts(flag_pts))
    layer = blank_layer()
    layer = over(layer, shadow(union(flag, pole, head), 1.0, 1.4, 1.0, 0.45), outline(union(flag, pole, head), 0.5, (20, 12, 8), 0.95))
    layer = over(layer, shaded(pole, WOOD, 0.3, relief=0.7, gain=1.6))
    layer = over(layer, shaded(flag, field_stops, 1.2, relief=2.0, gain=1.5, spec=0.12, texture=noise(seed + 30, 1.4, 2)))
    fold = np.asarray(flag, dtype=np.float32) / 255.0
    yy, xx = _GRID
    cloth = (np.sin((xx / SS * 0.9 + yy / SS * 0.25) * 1.1 + seed) * 0.5 + 0.5)
    layer = over(layer, from_alpha((0, 0, 0), fold * cloth * 0.22), from_alpha((255, 240, 220), fold * (1 - cloth) * 0.10))
    if charge == 'cross':
        a = stroke(pts([(side * flag_len * 0.18, top + flag_h * 0.5), (side * flag_len * 0.58, top + flag_h * 0.5)]), flag_h * 0.2, caps=False)
        b = stroke(pts([(side * flag_len * 0.38, top + flag_h * 0.18), (side * flag_len * 0.38, top + flag_h * 0.82)]), flag_h * 0.2, caps=False)
        layer = over(layer, shaded(inter(union(a, b), flag), GOLD, 0.3, relief=0.7, gain=1.8, spec=0.3))
    elif charge == 'stripe':
        a = stroke(pts([(side * flag_len * 0.05, top + flag_h * 0.5), (side * flag_len * 0.72, top + flag_h * 0.5)]), flag_h * 0.26, caps=False)
        layer = over(layer, shaded(inter(a, flag), GOLD, 0.3, relief=0.7, gain=1.8, spec=0.3))
    layer = over(layer, shaded(head, GOLD, 0.35, relief=1.0, gain=1.9, spec=0.5))
    return layer


def magnate(cx, cy, s, coat, cap_cloth, seed=1):
    """A bust of a magnate: fur-banded cap with a feather, moustache, braided kontusz."""
    layer = blank_layer()
    shoulders = ([(cx - 10.5 * s, cy + 19 * s), (cx - 10 * s, cy + 9.5 * s)] +
                 bezier((cx - 10 * s, cy + 9.5 * s), (cx - 9 * s, cy + 6.5 * s), (cx - 5 * s, cy + 5.6 * s), (cx - 2.6 * s, cy + 5.0 * s))[1:] +
                 [(cx + 2.6 * s, cy + 5.0 * s)] +
                 bezier((cx + 2.6 * s, cy + 5.0 * s), (cx + 5 * s, cy + 5.6 * s), (cx + 9 * s, cy + 6.5 * s), (cx + 10 * s, cy + 9.5 * s))[1:] +
                 [(cx + 10.5 * s, cy + 19 * s)])
    body = poly(shoulders)
    neck = poly([(cx - 2.2 * s, cy + 3.0 * s), (cx + 2.2 * s, cy + 3.0 * s), (cx + 2.8 * s, cy + 6.2 * s), (cx - 2.8 * s, cy + 6.2 * s)])
    head = ellipse(cx, cy, 4.3 * s, 4.9 * s)
    band = union(poly([(cx - 4.9 * s, cy - 1.9 * s), (cx + 4.9 * s, cy - 1.9 * s), (cx + 4.6 * s, cy - 5.6 * s), (cx - 4.6 * s, cy - 5.6 * s)]),
                 ellipse(cx, cy - 5.6 * s, 4.6 * s, 1.2 * s), ellipse(cx, cy - 1.9 * s, 4.9 * s, 1.1 * s))
    crown_pts = ([(cx - 4.4 * s, cy - 5.2 * s)] +
                 bezier((cx - 4.4 * s, cy - 5.2 * s), (cx - 4.8 * s, cy - 9.4 * s), (cx - 0.5 * s, cy - 12.6 * s), (cx + 3.6 * s, cy - 11.4 * s))[1:] +
                 bezier((cx + 3.6 * s, cy - 11.4 * s), (cx + 6.6 * s, cy - 10.2 * s), (cx + 7.4 * s, cy - 7.4 * s), (cx + 4.4 * s, cy - 5.2 * s))[1:])
    crown_c = poly(crown_pts)
    everything = union(body, head, band, crown_c)
    layer = over(layer, shadow(everything, 0.9, 1.2, 1.0, 0.5), outline(everything, 0.5, (14, 8, 6), 0.95))
    layer = over(layer, shaded(neck, SKIN, 0.4, relief=0.8, gain=1.4))
    layer = over(layer, shaded(body, coat, 1.2 * s, relief=2.4 * s, gain=1.4, texture=noise(seed, 0.9, 2)))
    layer = over(layer, roundness(body, cx - 10.5 * s, cx + 10.5 * s, dark=0.35, lift=0.10, peak=0.35))
    layer = over(layer, solid(stroke([(cx, cy + 6.0 * s), (cx, cy + 19 * s)], 0.45 * s), (10, 6, 4), 0.45))
    for i in range(3):
        yy = cy + (10.0 + 2.5 * i) * s
        for sign in (-1, 1):
            braid = stroke([(cx + sign * 0.9 * s, yy), (cx + sign * 4.6 * s, yy + 0.35 * s)], 0.7 * s)
            layer = over(layer, solid(grow(braid, 0.18 * s), (40, 22, 6), 0.8), solid(braid, (244, 206, 96), 1.0))
    layer = over(layer, shaded(head, SKIN, 0.9 * s, relief=1.8 * s, gain=1.4, spec=0.10))
    # cap
    layer = over(layer, shaded(crown_c, cap_cloth, 0.8 * s, relief=1.6 * s, gain=1.5, spec=0.15))
    layer = over(layer, shaded(band, FUR, 0.6 * s, relief=1.2 * s, gain=1.4, texture=noise(seed + 3, 0.5, 2)))
    layer = over(layer, strands(band, seed, int(60 * s * s), 1.1 * s, 0.14, [hexc('#0e0805'), hexc('#2a180d'), hexc('#5a3a22'), hexc('#8a6a44')],
                                lambda x, y: math.pi / 2, spread=0.5))
    layer = over(layer, shaded(ellipse(cx - 1.0 * s, cy - 3.7 * s, 0.95 * s), GOLD, 0.2, relief=0.6, gain=1.9, spec=0.5))
    layer = over(layer, solid(ellipse(cx - 1.0 * s, cy - 3.7 * s, 0.38 * s), (200, 20, 40), 0.95))
    for dx, spread in ((0.0, 0.0), (0.7, 0.7), (-0.5, -0.6)):
        plume = stroke(bezier((cx - 1.0 * s, cy - 4.4 * s), (cx - 3.4 * s + dx * s, cy - 9 * s), (cx - 2.8 * s + spread * 2 * s, cy - 13 * s),
                              (cx - 0.2 * s + spread * 3 * s, cy - 16.2 * s)), 0.5 * s)
        layer = over(layer, solid(plume, (250, 246, 232), 0.95))
    # face
    layer = over(layer, solid(ellipse(cx - 1.7 * s, cy - 0.4 * s, 0.5 * s, 0.4 * s), (20, 10, 6), 0.95),
                 solid(ellipse(cx + 1.7 * s, cy - 0.4 * s, 0.5 * s, 0.4 * s), (20, 10, 6), 0.95))
    layer = over(layer, solid(ellipse(cx, cy + 1.2 * s, 0.75 * s, 0.9 * s), (150, 90, 60), 0.5))
    for sign in (-1, 1):
        wisp = stroke(bezier((cx + sign * 0.4 * s, cy + 2.0 * s), (cx + sign * 2.6 * s, cy + 1.9 * s), (cx + sign * 4.2 * s, cy + 3.4 * s),
                             (cx + sign * 4.8 * s, cy + 5.4 * s)), 1.0 * s)
        layer = over(layer, solid(wisp, (46, 26, 12), 0.95))
    return layer


def candle(cx, base_y, height):
    layer = blank_layer()
    layer = over(layer, glow(cx, base_y - height - 1.4, 7.5, (255, 190, 90), 0.55))
    stem = poly([(cx - 1.2, base_y), (cx + 1.2, base_y), (cx + 1.2, base_y - height), (cx - 1.2, base_y - height)])
    layer = over(layer, shadow(stem, 0.5, 0.7, 0.5, 0.4), outline(stem, 0.3, (30, 20, 8), 0.9), shaded(stem, CANVAS, 0.4, relief=0.8, gain=1.4))
    flame = ellipse(cx, base_y - height - 1.5, 0.95, 1.8)
    layer = over(layer, solid(grow(flame, 0.5), (255, 140, 40), 0.8), solid(flame, (255, 230, 120), 1.0),
                 solid(ellipse(cx, base_y - height - 1.0, 0.4, 0.9), (255, 255, 235), 1.0))
    return layer


def long_table(y_top, y_front, x0=2.0, x1=80.0, seed=12):
    top = poly([(x0 + 7, y_top), (x1 - 7, y_top), (x1, y_front), (x0, y_front)])
    front = poly([(x0, y_front), (x1, y_front), (x1, y_front + 12), (x0, y_front + 12)])
    layer = blank_layer()
    layer = over(layer, shadow(top, 0.0, -1.0, 1.2, 0.4))
    layer = over(layer, shaded(front, DARK_WOOD, 0.8, relief=1.2, gain=1.3, texture=noise(seed, 1.2, 2)))
    layer = over(layer, shaded(top, WOOD, 1.0, relief=1.4, gain=1.3, texture=noise(seed + 1, 1.0, 3)))
    layer = over(layer, strands(top, seed, 160, 5.0, 0.16, [hexc('#4a2a12'), hexc('#6a4020'), hexc('#8a5a2c'), hexc('#2e1a0c')], lambda x, y: 0.0, spread=0.04))
    trim = stroke([(x0 + 0.5, y_front + 0.6), (x1 - 0.5, y_front + 0.6)], 0.9)
    layer = over(layer, outline(top, 0.5, (20, 10, 4), 0.9), shaded(trim, GOLD, 0.3, relief=0.7, gain=1.8, spec=0.3))
    return layer


def rolled_scroll(cx, cy, length, thick, degrees=0.0):
    body = poly([(cx - length / 2, cy - thick / 2), (cx + length / 2, cy - thick / 2), (cx + length / 2, cy + thick / 2), (cx - length / 2, cy + thick / 2)])
    caps = union(ellipse(cx - length / 2, cy, thick * 0.32, thick / 2), ellipse(cx + length / 2, cy, thick * 0.32, thick / 2))
    whole = union(body, caps)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 0.7, 1.0, 0.8, 0.5), outline(whole, 0.45, (46, 28, 10), 0.9))
    layer = over(layer, shaded(whole, PARCHMENT, 0.7, relief=1.8, gain=1.6))
    ribbon = poly([(cx - 1.0, cy - thick / 2 - 0.3), (cx + 1.0, cy - thick / 2 - 0.3), (cx + 1.0, cy + thick / 2 + 0.3), (cx - 1.0, cy + thick / 2 + 0.3)])
    layer = over(layer, shaded(ribbon, VELVET_RED, 0.3, relief=0.6, gain=1.6))
    layer = over(layer, solid(ellipse(cx, cy, thick * 0.3, thick * 0.3), (150, 24, 28), 0.95))
    return turn(layer, degrees, cx, cy) if degrees else layer


def inkwell(cx, base_y, w, h):
    body = union(ellipse(cx, base_y - h * 0.38, w / 2, h * 0.4),
                 poly([(cx - w * 0.22, base_y - h * 0.82), (cx + w * 0.22, base_y - h * 0.82), (cx + w * 0.3, base_y - h * 0.5), (cx - w * 0.3, base_y - h * 0.5)]),
                 ellipse(cx, base_y - h * 0.84, w * 0.27, h * 0.1))
    layer = blank_layer()
    layer = over(layer, contact(cx, base_y, w * 0.55, h * 0.12, 0.5), outline(body, 0.5, (10, 12, 16), 0.95))
    layer = over(layer, shaded(body, STEEL, 0.9, relief=2.0, gain=1.2, spec=0.2))
    layer = over(layer, roundness(body, cx - w / 2, cx + w / 2, dark=0.45, lift=0.0))
    layer = over(layer, solid(ellipse(cx, base_y - h * 0.84, w * 0.2, h * 0.06), (8, 8, 14), 0.95))
    return layer


def quill(base, degrees, length):
    """A goose quill standing in the inkwell, vane to the left of the shaft."""
    pts = lambda p: place(p, degrees, base)
    shaft = stroke(pts([(0, 0), (0.3, -length * 0.5), (0.9, -length)]), 0.55)
    left = bezier((0, -length * 0.18), (-3.6, -length * 0.40), (-4.2, -length * 0.78), (0.9, -length))
    right = bezier((0.9, -length), (3.2, -length * 0.78), (3.0, -length * 0.42), (0.1, -length * 0.20))
    vane = poly(pts(left + right))
    layer = blank_layer()
    layer = over(layer, shadow(vane, 0.8, 1.0, 0.7, 0.4), outline(vane, 0.45, (60, 48, 36), 0.9))
    layer = over(layer, shaded(vane, CANVAS, 0.8, relief=1.4, gain=1.4))
    barbs = blank_mask()
    d = ImageDraw.Draw(barbs)
    for i in range(14):
        t = 0.22 + 0.7 * i / 13.0
        sx, sy = 0.3 + 0.6 * t, -length * t
        for sign, reach in ((-1, 3.6), (1, 2.8)):
            ex, ey = sx + sign * reach * math.sin(math.pi * min(1.0, t * 1.05)), sy + 2.0
            d.line(_px(pts([(sx, sy), (ex, ey)])), fill=255, width=max(1, int(0.12 * SS)))
    layer = over(layer, solid(inter(barbs, vane), (120, 100, 78), 0.55))
    layer = over(layer, solid(shaft, (200, 190, 168), 1.0))
    return layer


def file_stack(cx, base_y, w):
    layer = blank_layer()
    colors = [LEATHER, BLUE_CLOTH, GREEN_CLOTH]
    for i, stops in enumerate(colors):
        y1 = base_y - i * 3.6
        slab = poly([(cx - w / 2 + i * 0.7, y1 - 3.3), (cx + w / 2 - i * 0.5, y1 - 3.3), (cx + w / 2 - i * 0.5, y1), (cx - w / 2 + i * 0.7, y1)])
        layer = over(layer, shadow(slab, 0.6, 0.9, 0.6, 0.45), outline(slab, 0.4, (14, 10, 6), 0.95), shaded(slab, stops, 0.5, relief=1.0, gain=1.4))
        tape = poly([(cx - 0.8, y1 - 3.3), (cx + 0.8, y1 - 3.3), (cx + 0.8, y1), (cx - 0.8, y1)])
        layer = over(layer, solid(tape, (180, 28, 32), 0.95))
        page = stroke([(cx - w / 2 + 1.4 + i * 0.7, y1 - 0.9), (cx + w / 2 - 1.4 - i * 0.5, y1 - 0.9)], 0.35)
        layer = over(layer, solid(page, (240, 228, 190), 0.55))
    return layer


def wagon(cx, ground_y, sc=1.0):
    """A covered settlers' wagon seen from the side."""
    def P(x, y):
        return (cx + x * sc, ground_y + y * sc)
    layer = blank_layer()
    bed = poly([P(-15, -10), P(15, -10), P(13.5, -4), P(-13.5, -4)])
    dome = poly([P(-14, -10)] + [P(14 * math.cos(math.pi - a), -10 - 13.5 * math.sin(a)) for a in np.linspace(0, math.pi, 30)] + [P(14, -10)])
    tongue = stroke([P(14, -6), P(26, -2.5)], 1.5 * sc)
    wheels = [(P(wx, -6.5), 6.6 * sc) for wx in (-8.5, 9)]
    layer = over(layer, contact(cx + 2 * sc, ground_y, 18 * sc, 2.2 * sc, 0.5))
    layer = over(layer, shadow(union(bed, dome), 1.0, 1.3, 1.1, 0.5))
    layer = over(layer, outline(union(bed, dome, tongue), 0.6, (24, 14, 6), 0.95))
    layer = over(layer, shaded(tongue, WOOD, 0.3, relief=0.7, gain=1.5))
    layer = over(layer, shaded(dome, CANVAS, 1.6, relief=3.0, gain=1.4))
    ribs = blank_mask()
    d = ImageDraw.Draw(ribs)
    for k in (-0.62, -0.2, 0.22, 0.64):
        d.line(_px([P(14 * k, -10), P(14 * k * 0.98, -10 - 13.3 * math.sqrt(max(0.0, 1 - k * k)))]), fill=255, width=max(1, int(0.34 * SS * sc)))
    layer = over(layer, solid(inter(ribs, dome), (110, 88, 56), 0.6))
    layer = over(layer, shaded(bed, WOOD, 0.8, relief=1.6, gain=1.4, texture=noise(31, 0.8, 2)))
    layer = over(layer, solid(stroke([P(-14, -7.2), P(14, -7.2)], 0.3 * sc), (24, 12, 4), 0.55))
    for (wx, wy), r in wheels:
        disc = ellipse(wx, wy, r)
        ring = minus(disc, ellipse(wx, wy, r * 0.78))
        layer = over(layer, shadow(disc, 0.6, 0.8, 0.5, 0.4), outline(disc, 0.45, (14, 8, 4), 0.95))
        layer = over(layer, solid(ellipse(wx, wy, r * 0.78), (24, 14, 8), 0.55))
        spokes = blank_mask()
        sd = ImageDraw.Draw(spokes)
        for i in range(8):
            a = i * math.pi / 4 + 0.2
            sd.line(_px([(wx, wy), (wx + math.cos(a) * r * 0.8, wy + math.sin(a) * r * 0.8)]), fill=255, width=max(1, int(0.55 * SS * sc)))
        layer = over(layer, shaded(spokes, WOOD, 0.2, relief=0.5, gain=1.4))
        layer = over(layer, shaded(ring, DARK_WOOD, 0.4, relief=1.2, gain=1.5))
        layer = over(layer, shaded(ellipse(wx, wy, r * 0.2), GOLD, 0.2, relief=0.6, gain=1.7, spec=0.3))
    return layer


def cottage(cx, ground_y, sc=1.0):
    def P(x, y):
        return (cx + x * sc, ground_y + y * sc)
    layer = blank_layer()
    wall = poly([P(-9, -10), P(9, -10), P(9, 0), P(-9, 0)])
    roof = poly([P(-12.5, -9), P(12.5, -9), P(5, -21), P(-5, -21)])
    chimney = poly([P(4.5, -19), P(8, -19), P(8, -12), P(4.5, -12)])
    layer = over(layer, contact(cx, ground_y, 13 * sc, 1.6 * sc, 0.45))
    layer = over(layer, outline(union(wall, roof, chimney), 0.5, (24, 14, 6), 0.95))
    layer = over(layer, shaded(chimney, STONE, 0.4, relief=0.8, gain=1.3))
    layer = over(layer, shaded(wall, CANVAS, 0.9, relief=1.4, gain=1.3))
    layer = over(layer, solid(poly([P(-9, -10), P(9, -10), P(9, -8.4), P(-9, -8.4)]), (60, 40, 20), 0.35))
    layer = over(layer, shaded(roof, THATCH, 1.0, relief=1.8, gain=1.3, texture=noise(41, 0.6, 3)))
    layer = over(layer, strands(roof, 41, 220, 3.0 * sc, 0.16, [hexc('#7a5a1a'), hexc('#c8a040'), hexc('#f0d078'), hexc('#5a3e10')], lambda x, y: math.pi / 2, spread=0.18))
    door = poly([P(-2.4, -6.6), P(0.6, -6.6), P(0.6, 0), P(-2.4, 0)])
    window = poly([P(3.0, -7.4), P(6.4, -7.4), P(6.4, -4.2), P(3.0, -4.2)])
    layer = over(layer, shaded(door, DARK_WOOD, 0.3, relief=0.6, gain=1.3))
    layer = over(layer, solid(window, (255, 214, 120), 1.0), solid(minus(grow(window, 0.3), window), (40, 24, 8), 0.95))
    for i, (sx, sy, sr) in enumerate([(6.2, -23.5, 1.6), (7.6, -27.0, 2.2), (9.6, -30.4, 2.8)]):
        layer = over(layer, solid(blur(ellipse(*P(sx, sy), sr * sc), 0.7), (214, 206, 198), 0.55 - 0.1 * i))
    return layer


def furrows(horizon_y, vanish_x, x_left, x_right, bottom_y):
    ground = poly([(x_left, horizon_y), (x_right, horizon_y), (x_right, bottom_y), (x_left, bottom_y)])
    layer = gradient(ground, [(0.0, hexc('#5a4a22')), (0.5, hexc('#4a3418')), (1.0, hexc('#2a1c0c'))], (0, horizon_y), (0, bottom_y))
    lines = blank_mask()
    d = ImageDraw.Draw(lines)
    for i in range(-6, 7):
        d.line(_px([(vanish_x + i * 1.2, horizon_y), (vanish_x + i * 9.0, bottom_y)]), fill=255, width=int(0.8 * SS))
    return over(layer, solid(inter(lines, ground), (190, 150, 80), 0.40))


def survey_map(seed=5):
    """A survey sheet: tinted parcels, boundary ink, a river, a compass rose."""
    region = poly([(6, 6), (76, 6), (76, 76), (6, 76)])
    layer = gradient(region, PARCHMENT, (6, 6), (76, 76))
    parcels = [
        ([(9, 9), (34, 9), (30, 27), (9, 30)], (150, 176, 110)),
        ([(34, 9), (58, 9), (55, 24), (30, 27)], (214, 180, 100)),
        ([(58, 9), (73, 9), (73, 26), (55, 24)], (192, 140, 108)),
        ([(9, 30), (30, 27), (33, 46), (9, 50)], (206, 176, 112)),
        ([(30, 27), (55, 24), (52, 44), (33, 46)], (140, 170, 108)),
        ([(55, 24), (73, 26), (73, 48), (52, 44)], (176, 160, 120)),
        ([(9, 50), (33, 46), (30, 73), (9, 73)], (190, 150, 106)),
        ([(33, 46), (52, 44), (54, 73), (30, 73)], (156, 180, 116)),
        ([(52, 44), (73, 48), (73, 73), (54, 73)], (214, 184, 106)),
    ]
    ink = blank_mask()
    for pts_, color in parcels:
        layer = over(layer, solid(poly(pts_), color, 0.62))
        ImageDraw.Draw(ink).line(_px(pts_ + [pts_[0]]), fill=255, width=int(0.6 * SS))
    layer = over(layer, solid(ink, (92, 56, 24), 0.9))
    course = bezier((9, 20), (30, 8), (36, 48), (73, 40), n=40)
    river = stroke(course, 3.0)
    layer = over(layer, solid(grow(river, 0.35), (60, 90, 120), 0.5), solid(river, (92, 140, 190), 0.95), solid(stroke(course, 1.0), (170, 206, 236), 0.7))
    dots = blank_mask()
    dd = ImageDraw.Draw(dots)
    for (x, y) in [(14, 36), (20, 42), (42, 33), (60, 56), (40, 62), (18, 64), (66, 14), (46, 15)]:
        dd.ellipse([(x - 0.9) * SS, (y - 0.9) * SS, (x + 0.9) * SS, (y + 0.9) * SS], fill=255)
    layer = over(layer, solid(dots, (60, 100, 50), 0.75))
    grain = np.asarray(region, dtype=np.float32) / 255.0 * (noise(seed, 0.8, 3) - 0.5) * 0.28
    layer = over(layer, from_alpha((70, 44, 16), np.clip(grain, 0, 1)), from_alpha((255, 250, 230), np.clip(-grain, 0, 1)))
    rose = []
    for i in range(8):
        a = -math.pi / 2 + i * math.pi / 4
        rr = 5.2 if i % 2 == 0 else 2.2
        rose.append((67 + rr * math.cos(a), 17 + rr * math.sin(a)))
    layer = over(layer, outline(poly(rose), 0.35, (50, 30, 10), 0.95), shaded(poly(rose), GOLD, 0.3, relief=0.7, gain=1.8, spec=0.3))
    layer = over(layer, solid(ellipse(67, 17, 1.0), (150, 24, 28), 0.95))
    return layer


def survey_chain(points, gap_at=None):
    """A Gunter's chain of brass links along a curve; `gap_at` leaves links out (a broken chain)."""
    layer = blank_layer()
    for i in range(len(points) - 1):
        if gap_at is not None and i in gap_at:
            continue
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        flat = (i % 2 == 0)
        link = ellipse(mx, my, 3.1, 1.85 if flat else 1.15, degrees=ang)
        hole = ellipse(mx, my, 2.1, 0.95 if flat else 0.45, degrees=ang)
        layer = over(layer, shadow(link, 0.6, 0.9, 0.5, 0.5), outline(link, 0.3, (30, 18, 4), 0.95),
                     shaded(minus(link, hole), GOLD, 0.35, relief=0.9, gain=1.9, spec=0.4))
    return layer


def dividers(hinge, degrees, spread, length):
    """Brass-and-steel dividers hanging from their hinge."""
    pts = lambda p: place(p, degrees, hinge)
    legs = []
    for sign in (-1, 1):
        tip = (sign * spread, length)
        legs.append(poly(pts([(sign * 0.2 - 1.0, 0), (sign * 0.2 + 1.0, 0), (tip[0] + 0.25, tip[1]), (tip[0] - 0.25, tip[1])])))
    hinge_ball = ellipse(*pts([(0, 0)])[0], 2.2)
    arm = stroke(pts([(-spread * 0.55, length * 0.55), (spread * 0.55, length * 0.55)]), 0.7)
    layer = blank_layer()
    both = union(*legs, hinge_ball, arm)
    layer = over(layer, shadow(both, 0.9, 1.2, 0.8, 0.5), outline(both, 0.45, (20, 22, 26), 0.95))
    for leg in legs:
        layer = over(layer, shaded(leg, STEEL, 0.4, relief=1.0, gain=1.4, spec=0.3))
    layer = over(layer, shaded(arm, GOLD, 0.2, relief=0.5, gain=1.7))
    layer = over(layer, shaded(hinge_ball, GOLD, 0.5, relief=1.4, gain=1.9, spec=0.5))
    return layer


def return_arrow(cx, cy, radius, width):
    """A gold arrow that turns back on itself: undo, recall, revert."""
    a0, a1 = math.radians(-40), math.radians(-300)
    pts_ = [(cx + radius * math.cos(a0 + (a1 - a0) * i / 40), cy + radius * math.sin(a0 + (a1 - a0) * i / 40)) for i in range(41)]
    body = stroke(pts_[:-3], width)
    (x0, y0), (x1, y1) = pts_[-4], pts_[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    tip = (x1 + math.cos(ang) * width * 0.9, y1 + math.sin(ang) * width * 0.9)
    base_l = (x0 + math.cos(ang + math.pi / 2) * width * 1.15, y0 + math.sin(ang + math.pi / 2) * width * 1.15)
    base_r = (x0 + math.cos(ang - math.pi / 2) * width * 1.15, y0 + math.sin(ang - math.pi / 2) * width * 1.15)
    arrow = union(body, poly([base_l, tip, base_r]))
    layer = blank_layer()
    layer = over(layer, shadow(arrow, 1.0, 1.4, 1.0, 0.65), outline(arrow, 0.6, (24, 12, 4), 0.98))
    layer = over(layer, shaded(arrow, GOLD, 0.7, relief=1.8, gain=1.9, spec=0.35))
    return layer


# --------------------------------------------------------------------------
# Pany Rada props: horse and rider figures, the Pahonia, lords, charters, a castle
# --------------------------------------------------------------------------

def taper(points, widths):
    """A limb: trapezoids between joints, a disc on every joint; widths are full widths in sprite units."""
    parts = []
    for (x0, y0), (x1, y1), w0, w1 in zip(points, points[1:], widths, widths[1:]):
        a = math.atan2(y1 - y0, x1 - x0) + math.pi / 2
        dx0, dy0 = math.cos(a) * w0 / 2, math.sin(a) * w0 / 2
        dx1, dy1 = math.cos(a) * w1 / 2, math.sin(a) * w1 / 2
        parts.append(poly([(x0 + dx0, y0 + dy0), (x1 + dx1, y1 + dy1), (x1 - dx1, y1 - dy1), (x0 - dx0, y0 - dy0)]))
    for (x, y), w in zip(points, widths):
        parts.append(ellipse(x, y, w / 2))
    return union(*parts)


class DesignGrid:
    """Design-grid (0..100) to sprite mapping."""
    def __init__(self, cx, cy, scale, flip=False, degrees=0.0):
        self.cx, self.cy, self.k, self.flip, self.deg = cx, cy, scale, flip, degrees

    def __call__(self, x, y):
        x = (x - 50.0) * self.k
        y = (y - 50.0) * self.k
        if self.flip:
            x = -x
        if self.deg:
            c, s = math.cos(math.radians(self.deg)), math.sin(math.radians(self.deg))
            x, y = x * c - y * s, x * s + y * c
        return (self.cx + x, self.cy + y)

    def pts(self, points):
        return [self(x, y) for x, y in points]

    def w(self, widths):
        return [v * self.k for v in widths]


def vytis_parts(F):
    """Rearing horse facing left (the Pahonia gallops to the dexter), armoured rider, sword up, shield on the arm."""
    P = {}
    body = ellipse(*F(58, 58), 26 * F.k, 13 * F.k, degrees=(-40 if F.flip else 40))
    neck = taper(F.pts([(41, 48), (31, 24), (28, 20)]), F.w([15, 9, 8.2]))
    head = taper(F.pts([(29, 20), (22, 27), (13, 35)]), F.w([8.0, 7.0, 4.4]))
    muzzle = taper(F.pts([(16, 33), (11.5, 37.5)]), F.w([4.8, 4.6]))
    ear = poly(F.pts([(27.5, 17), (29.5, 9.5), (32.5, 17)]))
    tail = poly(F.pts(bezier((78, 58), (96, 58), (104, 78), (92, 98), 24) + bezier((92, 98), (96, 80), (90, 68), (76, 66), 24)))
    P['horse'] = union(body, neck, head, muzzle, ear, tail)
    P['far_legs'] = union(
        taper(F.pts([(44, 47), (34, 52), (25, 43), (17, 48)]), F.w([8, 5.6, 4.2, 3.2])),
        taper(F.pts([(78, 72), (89, 84), (85, 93), (89, 99)]), F.w([11, 6, 4.2, 3.6])))
    P['near_legs'] = union(
        taper(F.pts([(39, 53), (29, 62), (19, 57), (13, 65)]), F.w([9, 6, 4.6, 3.4])),
        taper(F.pts([(72, 66), (76, 81), (68, 91), (71, 99)]), F.w([13, 7, 4.8, 4.0])))
    P['torso'] = taper(F.pts([(63, 51), (59, 26)]), F.w([11, 12.5]))
    P['rider_leg'] = taper(F.pts([(62, 52), (51, 57), (53, 69)]), F.w([7.5, 5.2, 4.2]))
    P['head_r'] = ellipse(*F(57, 16), 5.2 * F.k)
    P['helmet'] = poly(F.pts([(51, 17), (51.6, 11), (54.5, 6.5), (57, 5), (59.5, 6.5), (62.6, 11), (63, 17), (60, 15), (54, 15)]))
    P['arm'] = taper(F.pts([(60, 27), (68, 24), (72, 12)]), F.w([5.2, 4.2, 3.6]))
    P['sword'] = taper(F.pts([(72, 11), (92, -16)]), F.w([2.8, 1.5]))
    P['guard'] = taper(F.pts([(68, 12), (76.5, 8.5)]), F.w([2.0, 2.0]))
    sh = [(41, 24), (55, 24), (55, 38)] + bezier((55, 38), (55, 46), (48, 50), (48, 51), 12)[1:] + bezier((48, 51), (48, 50), (41, 46), (41, 38), 12)[1:]
    P['shield'] = poly(F.pts(sh))
    return P


def paint_part(layer, mask, stops, softness=0.8, relief=1.6, gain=1.5, spec=0.0, texture=None, edge=(20, 12, 10), edge_w=0.4, edge_a=0.95):
    layer = over(layer, outline(mask, edge_w, edge, edge_a))
    return over(layer, shaded(mask, stops, softness, relief=relief, gain=gain, spec=spec, texture=texture))


def vytis(cx, cy, scale, flip=False, degrees=0.0):
    """The Pahonia: a white armoured rider on a rearing white horse, sword raised, cross-bearing shield on the arm."""
    F = DesignGrid(cx, cy, scale, flip=flip, degrees=degrees)
    P = vytis_parts(F)
    layer = blank_layer()
    k = scale
    ew = max(0.3, 0.55 * k * 1.6)
    layer = over(layer, shadow(union(P['horse'], P['near_legs'], P['far_legs'], P['torso'], P['sword']), 0.5, 0.7, 0.5, 0.35))
    layer = paint_part(layer, P['far_legs'], GREY_HORSE, 0.5, 1.2, 1.3, edge=(46, 6, 8), edge_w=ew)
    layer = paint_part(layer, P['horse'], SILVER_WHITE, 1.4 * k * 2, 2.0, 1.3, edge=(46, 6, 8), edge_w=ew)
    layer = paint_part(layer, P['near_legs'], SILVER_WHITE, 0.6, 1.4, 1.4, edge=(60, 70, 88), edge_w=ew * 0.8)
    layer = paint_part(layer, P['rider_leg'], SILVER_PLATE, 0.5, 1.2, 1.4, edge=(40, 48, 62), edge_w=ew * 0.8)
    layer = paint_part(layer, P['torso'], SILVER_PLATE, 1.0, 1.8, 1.4, spec=0.1, edge=(40, 48, 62), edge_w=ew * 0.8)
    layer = paint_part(layer, P['arm'], SILVER_PLATE, 0.5, 1.2, 1.4, edge=(40, 48, 62), edge_w=ew * 0.8)
    layer = paint_part(layer, P['head_r'], SKIN, 0.5, 1.0, 1.3, edge=(40, 30, 24), edge_w=ew * 0.7)
    layer = paint_part(layer, P['helmet'], SILVER_PLATE, 0.5, 1.4, 1.5, spec=0.2, edge=(40, 48, 62), edge_w=ew * 0.8)
    layer = over(layer, paint_part(blank_layer(), P['sword'], STEEL, 0.3, 0.6, 1.4, spec=0.3, edge=(40, 48, 62), edge_w=ew * 0.8))
    layer = over(layer, shaded(P['guard'], GOLD, 0.2, relief=0.5, gain=1.8))
    # the shield: a blue field with the Jagiellonian double cross in gold
    layer = paint_part(layer, P['shield'], BLUE_CLOTH, 0.6, 1.4, 1.4, edge=(220, 190, 80), edge_w=ew * 1.1)
    stem = stroke([F(48, 29), F(48, 46)], 1.6 * k * 1.7, caps=False)
    bar1 = stroke([F(43.5, 33), F(52.5, 33)], 1.5 * k * 1.7, caps=False)
    bar2 = stroke([F(44.5, 39), F(51.5, 39)], 1.5 * k * 1.7, caps=False)
    layer = over(layer, shaded(inter(union(stem, bar1, bar2), P['shield']), GOLD, 0.2, relief=0.5, gain=1.8, spec=0.3))
    return layer


def walker_parts(F):
    """A horse at a walk facing right, with an upright rider in the saddle: coat, mail coif, steel cap, round shield."""
    P = {}
    body = ellipse(*F(45, 31), 24 * F.k, 11.5 * F.k)
    chest = ellipse(*F(58, 30), 10 * F.k, 11 * F.k)
    neck = taper(F.pts([(59, 28), (66, 16), (72, 9.5)]), F.w([18, 13, 9.5]))
    head = taper(F.pts([(72, 11), (79, 18), (86, 25)]), F.w([9.5, 8.0, 5.0]))
    cheek = ellipse(*F(76, 17), 5.4 * F.k, 5.0 * F.k)
    muzzle = taper(F.pts([(83, 22.5), (88.5, 27.5)]), F.w([5.0, 5.2]))
    ear = poly(F.pts([(69.5, 8), (71.5, -1.5), (75.5, 8.5)]))
    tail = poly(F.pts(bezier((24, 24), (12, 26), (8, 40), (12, 54), 20) + bezier((12, 54), (16, 43), (20, 36), (26, 33), 20)))
    mane = poly(F.pts(bezier((60, 19), (65, 7), (69, 4), (72, 2), 12) + bezier((72, 2), (70, 10), (66, 17), (62, 25), 12)))
    P['horse'] = union(body, chest, neck, head, cheek, muzzle, ear, tail)
    P['mane'] = mane
    P['cloth'] = poly(F.pts([(34, 18), (56, 18), (58, 36), (32, 36)]))
    P['near_legs'] = union(
        taper(F.pts([(61, 38), (63, 50), (62, 60), (63.5, 67)]), F.w([9, 5.4, 4.0, 4.6])),
        taper(F.pts([(31, 38), (26, 50), (27, 60), (25.5, 67)]), F.w([11, 6.2, 4.0, 4.6])))
    P['far_legs'] = union(
        taper(F.pts([(56, 37), (65, 47), (70, 55), (71.5, 61)]), F.w([8, 5.2, 3.8, 4.2])),
        taper(F.pts([(36, 37), (40, 49), (38, 60), (40, 67)]), F.w([10, 5.8, 3.8, 4.4])))
    P['torso'] = taper(F.pts([(47, 22), (48, 2)]), F.w([12, 13.5]))
    P['rider_leg'] = taper(F.pts([(47, 23), (51, 32), (49.5, 42)]), F.w([9, 6.2, 4.6]))
    P['head_r'] = ellipse(*F(49, -5.5), 5.4 * F.k)
    P['helmet'] = poly(F.pts([(43.2, -4.6), (43.4, -10), (46, -13.4), (48.4, -16.5), (50.4, -13.4), (53, -10), (55, -4.6), (52.4, -7.6), (46, -7.6)]))
    P['arm'] = taper(F.pts([(50, 4), (57, 9), (62, 4)]), F.w([5.6, 4.6, 4.0]))
    P['shield'] = ellipse(*F(41, 15), 8.6 * F.k)
    return P


def boyar_rider(cx, cy, scale, horse=BAY, coat=RED_COAT, flip=False, seed=1):
    """A boyar of a magnate's household on horseback (the design faces right; `flip` turns him left). Returns the layer and its grid."""
    F = DesignGrid(cx, cy, scale, flip=flip)
    P = walker_parts(F)
    k = scale
    ew = max(0.3, 0.55 * k * 1.7)
    dark = (12, 6, 4)
    layer = blank_layer()
    layer = over(layer, contact(*F(46, 69), 26 * k, 3.0 * k, 0.45))
    layer = paint_part(layer, P['far_legs'], horse, 0.4, 1.0, 1.3, edge=dark, edge_w=ew)
    layer = paint_part(layer, P['horse'], horse, 1.2, 2.2, 1.4, texture=noise(seed, 0.9, 2), edge=dark, edge_w=ew)
    layer = over(layer, roundness(P['horse'], F(23, 0)[0], F(70, 0)[0], dark=0.35, lift=0.12, peak=0.3))
    layer = over(layer, shaded(inter(P['cloth'], P['horse']), coat, 0.6, relief=1.2, gain=1.3),
                 solid(stroke(F.pts([(34, 18.5), (56, 18.5)]), 0.5 * k * 2), (244, 206, 96), 0.9))
    layer = paint_part(layer, P['near_legs'], horse, 0.5, 1.2, 1.4, edge=dark, edge_w=ew * 0.9)
    layer = over(layer, shaded(P['mane'], BLACK_HORSE, 0.4, relief=0.8, gain=1.2))
    layer = paint_part(layer, P['rider_leg'], MAIL, 0.4, 0.9, 1.4, edge=(16, 18, 24), edge_w=ew * 0.8)
    layer = paint_part(layer, P['torso'], coat, 0.9, 1.6, 1.4, spec=0.1, edge=(24, 8, 10), edge_w=ew * 0.8)
    layer = over(layer, solid(stroke(F.pts([(47, 6), (47.4, 22)]), 0.9 * k * 2), (244, 206, 96), 0.9))
    layer = paint_part(layer, P['arm'], MAIL, 0.4, 0.9, 1.4, edge=(16, 18, 24), edge_w=ew * 0.8)
    layer = paint_part(layer, P['head_r'], SKIN, 0.4, 0.8, 1.3, edge=(40, 30, 24), edge_w=ew * 0.7)
    coif = minus(ellipse(*F(49, -4.2), 6.2 * k, 6.4 * k), ellipse(*F(50.4 if not flip else 47.6, -5.0), 3.6 * k, 3.4 * k))
    layer = over(layer, shaded(coif, MAIL, 0.3, relief=0.8, gain=1.4))
    layer = paint_part(layer, P['helmet'], STEEL, 0.4, 1.2, 1.5, spec=0.2, edge=(16, 18, 24), edge_w=ew * 0.8)
    layer = paint_part(layer, P['shield'], VELVET_RED, 0.8, 1.6, 1.4, edge=(220, 190, 80), edge_w=ew * 1.1)
    layer = over(layer, shaded(ellipse(*F(41, 15), 2.2 * k), GOLD, 0.2, relief=0.6, gain=1.8, spec=0.4))
    return layer, F


def spline(points, closed=True, n=8):
    """Catmull-Rom curve through the points (a smooth outline from a handful of corners)."""
    pts = list(points)
    m = len(pts)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        p0 = pts[(i - 1) % m] if closed or i > 0 else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if closed or i + 2 < m else pts[(i + 1) % m]
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    return out


def rada_lord(cx, cy, s, facing, coat, cap_top, beard=BEARD_GREY, fur=SABLE, seed=1):
    """A lord of the Rada in profile: sable-banded cap, beard, coat with a fur collar and gold braid. (cx, cy) is the head centre."""
    f = facing
    X = lambda x: cx + f * x * s
    Y = lambda y: cy + y * s
    pt = lambda x, y: (X(x), Y(y))
    P = lambda seq: [pt(*q) for q in seq]
    layer = blank_layer()
    body = poly(P([(-11.5, 32), (-11, 13)] + bezier((-11, 13), (-10, 8.4), (-5, 6.6), (-1, 6.2), 10)[1:] + bezier((-1, 6.2), (5, 6.2), (10.5, 8.4), (12, 14), 10)[1:] + [(12.5, 32)]))
    neck = poly(P([(-2.6, 3), (3.0, 3), (3.4, 8.0), (-3.2, 8.0)]))
    face = poly(P(spline([(-0.4, -5.6), (3.0, -4.6), (4.6, -2.6), (4.2, -1.0), (6.9, 1.5), (5.0, 2.6), (5.1, 3.6), (4.5, 4.4), (4.3, 6.2), (1.2, 6.8),
                           (-2.6, 4.8), (-4.9, 0.6), (-4.2, -4.4)], True, 6)))
    beard_m = poly(P(spline([(-2.8, 1.0), (1.8, 3.0), (4.8, 3.6), (5.4, 5.6), (4.6, 8.6), (3.0, 12.0), (0.2, 9.6), (-2.2, 6.0)], True, 6)))
    must = poly(P(spline([(3.6, 2.7), (7.0, 2.9), (6.6, 4.1), (4.4, 4.4)], True, 5)))
    band = poly(P([(-5.6, -2.6), (4.8, -3.0), (5.1, -6.6), (-5.6, -6.9)]))
    top = poly(P(spline([(-5.5, -6.5), (-5.8, -10.5), (-2.2, -13.6), (2.6, -12.6), (5.2, -9.6), (5.0, -6.5)], True, 6)))
    everything = union(body, face, band, top, beard_m, neck)
    layer = over(layer, shadow(everything, 0.7 * s, 1.0 * s, 0.8, 0.5), outline(everything, 0.45, (14, 8, 6), 0.95))
    layer = over(layer, shaded(body, coat, 1.0 * s, relief=2.0 * s, gain=1.4, texture=noise(seed, 0.9, 2)))
    layer = over(layer, roundness(body, X(-10.5) if f > 0 else X(12), X(12) if f > 0 else X(-10.5), dark=0.35, lift=0.10, peak=0.35))
    collar = poly(P(spline([(-11, 13.5), (-9, 8.6), (-2, 6.4), (4, 6.4), (10, 8.6), (12, 14), (8.8, 12.6), (3.5, 10.6), (-3, 11.0), (-8, 13.8)], True, 6)))
    layer = over(layer, shaded(collar, fur, 0.6 * s, relief=1.2 * s, gain=1.3, texture=noise(seed + 2, 0.5, 2)))
    for i in range(3):
        yy = 17 + 3.2 * i
        layer = over(layer, solid(stroke([pt(1.0, yy), pt(6.4, yy + 0.3)], 0.65 * s), (244, 206, 96), 0.95))
    layer = over(layer, shaded(neck, SKIN, 0.4, relief=0.8, gain=1.4))
    layer = over(layer, shaded(face, SKIN, 0.9 * s, relief=1.8 * s, gain=1.4, spec=0.08))
    layer = over(layer, solid(ellipse(X(-1.6), Y(0.9), 1.0 * s, 1.7 * s), (150, 90, 62), 0.55))
    layer = over(layer, shaded(beard_m, beard, 0.5 * s, relief=1.2, gain=1.3, texture=noise(seed + 5, 0.5, 2)))
    layer = over(layer, strands(beard_m, seed, int(36 * s * s), 1.6 * s, 0.13, [hexc('#0e0805'), hexc('#3a2a1a'), hexc('#a8a8a8'), hexc('#e8e8e8')], lambda x, y: math.pi / 2, spread=0.4))
    layer = over(layer, shaded(must, beard, 0.2, relief=0.5, gain=1.3))
    layer = over(layer, solid(ellipse(X(2.7), Y(-0.9), 0.62 * s, 0.46 * s), (20, 10, 6), 0.97))
    layer = over(layer, solid(stroke([pt(1.2, -2.5), pt(4.3, -2.3)], 0.55 * s), (50, 28, 12), 0.85))
    layer = over(layer, shaded(top, cap_top, 0.8 * s, relief=1.6 * s, gain=1.5, spec=0.15))
    layer = over(layer, shaded(band, fur, 0.6 * s, relief=1.2 * s, gain=1.4, texture=noise(seed + 3, 0.5, 2)))
    layer = over(layer, strands(band, seed, int(70 * s * s), 1.0 * s, 0.14, [hexc('#0e0805'), hexc('#2a180d'), hexc('#5a3a22'), hexc('#9a7a54')], lambda x, y: math.pi / 2, spread=0.5))
    layer = over(layer, shaded(ellipse(X(2.0), Y(-9.0), 1.0 * s), GOLD, 0.2, relief=0.6, gain=1.9, spec=0.5))
    return layer


def hanging_seals(x_left, base_y, w, radii=(4.4, 4.0, 4.4), colors=(WAX, WAX_GREEN, WAX_YELLOW), drops=(2.5, 5.0, 3.0), seed=1):
    """Pendant seals on cords from the foot of a charter, spaced across its width."""
    layer = blank_layer()
    n = len(radii)
    for i in range(n):
        sx = x_left + w * (i + 0.5) / n
        sy = base_y + drops[i] + radii[i]
        cord = stroke([(sx, base_y - 0.6), (sx + 0.3, base_y + drops[i] * 0.5), (sx + 0.1, sy - radii[i] * 0.6)], 0.5)
        layer = over(layer, solid(cord, (220, 190, 120) if i != 1 else (170, 30, 34), 0.95))
        r = radii[i]
        rng = random.Random(seed + i)
        pts = [(sx + (r + rng.uniform(-0.08, 0.08) * r + 0.08 * r * math.sin(5 * (2 * math.pi * j / 32))) * math.cos(2 * math.pi * j / 32),
                sy + (r + rng.uniform(-0.08, 0.08) * r + 0.08 * r * math.sin(5 * (2 * math.pi * j / 32))) * math.sin(2 * math.pi * j / 32)) for j in range(32)]
        blob = poly(pts)
        layer = over(layer, shadow(blob, 0.6, 0.9, 0.7, 0.5), outline(blob, 0.35, (24, 6, 6), 0.9))
        layer = over(layer, shaded(blob, colors[i], 0.8, relief=1.8, gain=1.7, spec=0.35))
        ring = minus(ellipse(sx, sy, r * 0.64), ellipse(sx, sy, r * 0.46))
        layer = over(layer, shaded(ring, colors[i], 0.25, relief=0.8, gain=2.2, spec=0.25))
        layer = over(layer, shaded(ellipse(sx, sy, r * 0.28), colors[i], 0.25, relief=0.7, gain=2.2, spec=0.25))
    return layer


def privilege_charter(cx, cy, w, h, seed=5, degrees=0.0, lines=6, seals=3):
    """An unrolled privilege (a 1492 or 1506 charter): ruled script, a red initial, wax seals hanging from its foot on cords."""
    x, y = cx - w / 2, cy - h / 2
    curl = max(2.0, h * 0.075)
    sheet_m = poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])
    layer = blank_layer()
    layer = over(layer, shadow(sheet_m, 0.9, 1.3, 1.1, 0.5), outline(sheet_m, 0.55, (46, 28, 10), 0.9))
    layer = over(layer, gradient(sheet_m, PARCHMENT, (x, y), (x + w * 0.9, y + h)))
    grain = np.asarray(sheet_m, dtype=np.float32) / 255.0 * (noise(seed, 0.7, 3) - 0.5) * 0.32
    layer = over(layer, from_alpha((60, 36, 12), np.clip(grain, 0, 1)), from_alpha((255, 250, 225), np.clip(-grain, 0, 1)))
    ink = blank_mask()
    rng = random.Random(seed)
    top = y + curl + 1.4
    gap = (h - 2 * curl - 6.0) / max(1, lines)
    for i in range(lines):
        yy = top + gap * (i + 0.5)
        x0 = x + 2.3 + (3.2 if i == 0 else 0.0)
        x1 = x + w - 2.3 - (rng.uniform(0.0, w * 0.3) if i == lines - 1 else rng.uniform(0.0, 1.0))
        ImageDraw.Draw(ink).line(_px([(x0, yy), (x1, yy + rng.uniform(-0.1, 0.1))]), fill=255, width=max(1, int(0.55 * SS)))
    layer = over(layer, solid(inter(ink, sheet_m), (74, 46, 22), 0.66))
    initial = poly([(x + 2.3, top + gap * 0.1), (x + 5.2, top + gap * 0.1), (x + 5.2, top + gap * 0.95), (x + 2.3, top + gap * 0.95)])
    layer = over(layer, solid(initial, (150, 24, 28), 0.85))
    for ry in (y, y + h - curl):
        roll = poly([(x - 0.9, ry), (x + w + 0.9, ry), (x + w + 0.9, ry + curl), (x - 0.9, ry + curl)])
        layer = over(layer, outline(roll, 0.45, (46, 28, 10), 0.9), shaded(roll, PARCHMENT, 0.5, relief=1.5, gain=1.7))
        for ex in (x - 0.9, x + w + 0.9):
            layer = over(layer, solid(ellipse(ex, ry + curl / 2, curl * 0.42, curl * 0.5), (96, 66, 30), 0.85),
                         solid(ellipse(ex, ry + curl / 2, curl * 0.2, curl * 0.26), (230, 208, 150), 0.9))
    # the foot of the sheet is folded up and the seals hang on tags
    layer = over(layer, hanging_seals(x + 1.5, y + h - 0.4, w - 3.0, radii=(4.0, 3.6, 4.0)[:seals], colors=(WAX, WAX_GREEN, WAX_YELLOW)[:seals],
                                      drops=(1.8, 4.4, 2.4)[:seals], seed=seed + 1))
    return turn(layer, degrees, cx, cy) if degrees else layer


def gediminas_mask(cx, cy, h):
    """The Columns of Gediminas, simplified: a base bar, two side prongs, a square pedestal and a centre stem (a 'trident')."""
    t = 0.085 * h
    pts = lambda l: [(cx + x * h, cy + y * h) for x, y in l]
    left = stroke(pts(bezier((-0.37, 0.40), (-0.40, 0.05), (-0.38, -0.30), (-0.31, -0.50), 14)), t, caps=False)
    right = stroke(pts(bezier((0.37, 0.40), (0.40, 0.05), (0.38, -0.30), (0.31, -0.50), 14)), t, caps=False)
    base = poly(pts([(-0.42, 0.40), (0.42, 0.40), (0.42, 0.50), (-0.42, 0.50)]))
    square = poly(pts([(-0.13, 0.04), (0.13, 0.04), (0.13, 0.40), (-0.13, 0.40)]))
    stem = poly(pts([(-0.045, -0.52), (0.045, -0.52), (0.045, 0.06), (-0.045, 0.06)]))
    return union(left, right, base, square, stem)


def gediminas_columns(cx, cy, h):
    mask = gediminas_mask(cx, cy, h)
    layer = over(blank_layer(), outline(mask, 0.35, (60, 30, 4), 0.9), shaded(mask, GOLD, 0.3, relief=0.8, gain=1.8, spec=0.3))
    return layer


def lance_standard(base, degrees, length, flag_len, flag_h, field, emblem=None, seed=1, side=1, tail=True, border=True):
    """A lance with a swallow-tailed standard streaming to one side; `emblem(centre)` returns the charge, drawn in sprite coordinates."""
    pts = lambda p: place(p, degrees, base)
    pole = poly(pts([(-0.55, 0), (0.55, 0), (0.5, -length), (-0.5, -length)]))
    head = poly(pts([(-1.3, -length), (1.3, -length), (0, -length - 5.0)]))
    top = -length + 2.0
    waves = 1.0 + 0.4 * (seed % 2)
    upper = [(side * (flag_len * i / 20.0), top + math.sin(i / 20.0 * math.pi * 1.4 * waves + seed) * 1.0) for i in range(21)]
    lower = [(side * (flag_len * i / 20.0), top + flag_h + math.sin(i / 20.0 * math.pi * 1.4 * waves + seed) * 1.0) for i in range(20, -1, -1)]
    notch = (side * flag_len * 0.78, top + flag_h / 2 + 0.6)
    flag_pts = upper + ([notch] if tail else []) + lower
    flag = poly(pts(flag_pts))
    layer = blank_layer()
    layer = over(layer, shadow(union(flag, pole, head), 0.8, 1.1, 0.8, 0.45), outline(union(flag, pole, head), 0.45, (20, 12, 8), 0.95))
    layer = over(layer, shaded(pole, WOOD, 0.3, relief=0.7, gain=1.6))
    layer = over(layer, shaded(flag, field, 1.1, relief=1.8, gain=1.5, spec=0.12, texture=noise(seed + 30, 1.4, 2)))
    if border:
        rim = minus(flag, erode(flag, 0.9))
        layer = over(layer, shaded(rim, GOLD, 0.2, relief=0.5, gain=1.7, spec=0.2))
    if emblem is not None:
        centre = pts([(side * flag_len * (0.40 if tail else 0.5), top + flag_h / 2)])[0]
        layer = over(layer, clip(emblem(centre), flag))
    fold = np.asarray(flag, dtype=np.float32) / 255.0
    yy, xx = _GRID
    cloth = (np.sin((xx / SS * 0.9 + yy / SS * 0.25) * 1.1 + seed) * 0.5 + 0.5)
    layer = over(layer, from_alpha((0, 0, 0), fold * cloth * 0.20), from_alpha((255, 240, 220), fold * (1 - cloth) * 0.08))
    layer = over(layer, shaded(head, GOLD, 0.35, relief=1.0, gain=1.9, spec=0.5))
    return layer


def gold_key(cx, cy, length, degrees=0.0, bow_r=None):
    """A gold key drawn along +x: ring bow on the left, shaft, a two-toothed bit on the right; placed at its middle."""
    bow_r = bow_r or length * 0.17
    L = length
    pts = lambda p: place(p, degrees, (cx, cy))
    x0 = -L / 2
    bow_c = (x0 + bow_r, 0)
    bow = ellipse(*pts([bow_c])[0], bow_r)
    hole = ellipse(*pts([bow_c])[0], bow_r * 0.5)
    shaft = poly(pts([(x0 + bow_r * 1.6, -bow_r * 0.26), (L / 2, -bow_r * 0.26), (L / 2, bow_r * 0.26), (x0 + bow_r * 1.6, bow_r * 0.26)]))
    collar = poly(pts([(x0 + bow_r * 2.0, -bow_r * 0.55), (x0 + bow_r * 2.6, -bow_r * 0.55), (x0 + bow_r * 2.6, bow_r * 0.55), (x0 + bow_r * 2.0, bow_r * 0.55)]))
    tooth1 = poly(pts([(L / 2 - bow_r * 1.5, bow_r * 0.2), (L / 2, bow_r * 0.2), (L / 2, bow_r * 1.25), (L / 2 - bow_r * 0.8, bow_r * 1.25), (L / 2 - bow_r * 0.8, bow_r * 0.8), (L / 2 - bow_r * 1.5, bow_r * 0.8)]))
    tooth2 = poly(pts([(L / 2 - bow_r * 2.8, bow_r * 0.2), (L / 2 - bow_r * 2.0, bow_r * 0.2), (L / 2 - bow_r * 2.0, bow_r * 1.0), (L / 2 - bow_r * 2.8, bow_r * 1.0)]))
    whole = union(minus(bow, hole), shaft, collar, tooth1, tooth2)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 0.9, 1.2, 0.9, 0.55), outline(whole, 0.5, (30, 16, 2), 0.97))
    layer = over(layer, shaded(whole, GOLD, 0.6, relief=1.8, gain=1.9, spec=0.45))
    return layer


def open_hand(cx, cy, s, degrees=0.0, cuff=(VELVET_RED, SABLE)):
    """An open hand, palm up, from a sleeve with a fur cuff: coordinates are for a hand reaching to the right."""
    pts = lambda p: place(p, degrees, (cx, cy))
    sleeve = poly(pts([(-22 * s, -7 * s), (-4 * s, -5.2 * s), (-4 * s, 5.2 * s), (-22 * s, 8.5 * s)]))
    cuff_m = poly(pts([(-6.5 * s, -5.8 * s), (-1.5 * s, -5.0 * s), (-1.5 * s, 5.0 * s), (-6.5 * s, 6.0 * s)]))
    palm = ellipse(*pts([(3.5 * s, 0)])[0], 5.2 * s, 4.4 * s, degrees)
    fingers = [taper(pts([(6.0 * s, (-3.4 + 2.3 * i) * s), (10.8 * s, (-3.9 + 2.5 * i) * s)]), [2.5 * s, 2.0 * s]) for i in range(4)]
    thumb = taper(pts([(1.5 * s, -3.6 * s), (4.5 * s, -7.0 * s), (8.0 * s, -7.8 * s)]), [3.0 * s, 2.4 * s, 2.0 * s])
    whole = union(palm, thumb, *fingers)
    layer = blank_layer()
    layer = over(layer, shadow(union(whole, sleeve), 0.9, 1.2, 0.9, 0.5))
    layer = over(layer, outline(union(sleeve, whole), 0.45, (30, 14, 8), 0.95))
    layer = over(layer, shaded(sleeve, cuff[0], 1.0, relief=2.0, gain=1.4, texture=noise(4, 0.9, 2)))
    layer = over(layer, shaded(whole, SKIN, 0.5, relief=1.2, gain=1.4))
    layer = over(layer, shaded(cuff_m, cuff[1], 0.5, relief=1.0, gain=1.3, texture=noise(5, 0.5, 2)))
    layer = over(layer, strands(cuff_m, 3, 40, 1.1, 0.14, [hexc('#0e0805'), hexc('#2a180d'), hexc('#5a3a22'), hexc('#9a7a54')], lambda x, y: math.pi / 2, spread=0.5))
    return layer


def castle_tower(cx, base_y, w, h, roof_h, wall=STONE, roof=VELVET_RED, seed=1):
    """A round-topped castle tower: stone drum, red conical roof, an arrow slit."""
    body = poly([(cx - w / 2, base_y), (cx - w / 2, base_y - h), (cx + w / 2, base_y - h), (cx + w / 2, base_y)])
    cone = poly([(cx - w / 2 - 0.9, base_y - h), (cx, base_y - h - roof_h), (cx + w / 2 + 0.9, base_y - h)])
    layer = blank_layer()
    layer = over(layer, outline(union(body, cone), 0.4, (10, 14, 24), 0.9))
    layer = over(layer, shaded(body, wall, 0.7, relief=1.4, gain=1.3, texture=noise(seed, 0.7, 2)))
    layer = over(layer, roundness(body, cx - w / 2, cx + w / 2, dark=0.4, lift=0.1))
    layer = over(layer, shaded(cone, roof, 0.7, relief=1.4, gain=1.4))
    slit = poly([(cx - 0.5, base_y - h * 0.7), (cx + 0.5, base_y - h * 0.7), (cx + 0.5, base_y - h * 0.45), (cx - 0.5, base_y - h * 0.45)])
    layer = over(layer, solid(slit, (10, 12, 20), 0.85))
    return layer


def castle(cx, base_y, sc=1.0, seed=1):
    """A hill castle seen from the front: a curtain wall with battlements, a gate tower and two corner towers with red roofs."""
    layer = blank_layer()
    wall = poly([(cx - 17 * sc, base_y), (cx - 17 * sc, base_y - 9 * sc), (cx + 17 * sc, base_y - 9 * sc), (cx + 17 * sc, base_y)])
    merlons = union(*[poly([(cx + (-17 + 3.4 * i) * sc, base_y - 9 * sc), (cx + (-17 + 3.4 * i + 2.0) * sc, base_y - 9 * sc),
                            (cx + (-17 + 3.4 * i + 2.0) * sc, base_y - 11.2 * sc), (cx + (-17 + 3.4 * i) * sc, base_y - 11.2 * sc)]) for i in range(10)])
    gate = poly([(cx - 2.2 * sc, base_y), (cx - 2.2 * sc, base_y - 4.2 * sc)] + arc_points(cx, base_y - 4.2 * sc, 2.2 * sc, 2.2 * sc, math.pi, 2 * math.pi, 12) + [(cx + 2.2 * sc, base_y)])
    layer = over(layer, outline(union(wall, merlons), 0.4, (10, 14, 24), 0.9))
    layer = over(layer, shaded(union(wall, merlons), STONE, 0.7, relief=1.4, gain=1.3, texture=noise(seed, 0.7, 2)))
    layer = over(layer, solid(gate, (12, 14, 22), 0.92))
    layer = over(layer, castle_tower(cx - 15 * sc, base_y, 7 * sc, 17 * sc, 8 * sc, seed=seed + 1))
    layer = over(layer, castle_tower(cx + 15 * sc, base_y, 7 * sc, 17 * sc, 8 * sc, seed=seed + 2))
    layer = over(layer, castle_tower(cx, base_y - 6 * sc, 9 * sc, 17 * sc, 9 * sc, seed=seed + 3))
    return layer


# --------------------------------------------------------------------------
# Scenes
# --------------------------------------------------------------------------

def scene_boyar_office():
    """Confirm the Boyars in Office: a charter with its seal, a boyar's fur hat beside it."""
    layer = backdrop([(0.0, hexc('#8a4426')), (0.5, hexc('#4e2016')), (1.0, hexc('#1e0b08'))], (46, 26), 54)
    layer = over(layer, glow(54, 30, 22, (255, 190, 100), 0.35))
    for x in range(8, 78, 9):
        layer = over(layer, solid(poly([(x, 0), (x + 1.3, 0), (x + 1.3, 82), (x, 82)]), (20, 6, 4), 0.22))
    layer = over(layer, fur_hat(54, 52, 16, 27, seed=4, degrees=4))
    layer = over(layer, charter(31, 42, 24, 30, seed=11, degrees=-8, lines=5, seal_r=4.8))
    return layer


def scene_boyar_claimant():
    """Counter the Foreign Claimant: a foreign crown with the prince's sword laid across it."""
    layer = backdrop([(0.0, hexc('#7a3a2a')), (0.5, hexc('#3e1812')), (1.0, hexc('#180806'))], (41, 36), 52)
    layer = over(layer, glow(41, 36, 22, (255, 200, 120), 0.30))
    layer = over(layer, contact(42, 58, 18, 3.2, 0.55))
    layer = over(layer, crown(42, 56, 30, 27, degrees=-6))
    layer = over(layer, sword((16, 64), -38, 42, blade_w=5.6))
    return layer


def scene_boyar_example():
    """Make an Example of a Defiant Boyar: his fur hat on the block, the axe in the wood."""
    layer = backdrop([(0.0, hexc('#5a1c14')), (0.55, hexc('#341210')), (1.0, hexc('#140606'))], (41, 30), 54)
    layer = over(layer, glow(41, 40, 24, (255, 150, 80), 0.22))
    layer = over(layer, log_block(36, 67, 28, 12, seed=9))
    layer = over(layer, fur_hat(35, 57, 14, 23, seed=6, degrees=-8))
    layer = over(layer, axe((59, 69), -5, 33))
    return layer


def senate_hall():
    """Blue hall behind the Volhynian magnates: a lit window arch between two stone pillars."""
    layer = backdrop([(0.0, hexc('#34548f')), (0.5, hexc('#18305e')), (1.0, hexc('#070f24'))], (41, 26), 52)
    arch = poly([(30, 40), (30, 22)] + arc_points(41, 22, 11, 11, math.pi, 2 * math.pi, 24) + [(52, 22), (52, 40)])
    layer = over(layer, glow(41, 26, 24, (190, 215, 255), 0.40))
    layer = over(layer, solid(arch, (176, 204, 250), 0.50), solid(stroke([(41, 11), (41, 40)], 0.7), (24, 40, 80), 0.55),
                 solid(stroke([(30, 27), (52, 27)], 0.7), (24, 40, 80), 0.55), outline(arch, 0.6, (14, 24, 52), 0.8))
    for x0 in (12.0, 64.0):
        pillar = poly([(x0, 8), (x0 + 6, 8), (x0 + 6, 74), (x0, 74)])
        layer = over(layer, shadow(pillar, 0.8, 0.0, 1.0, 0.45), outline(pillar, 0.5, (10, 14, 26), 0.9), shaded(pillar, STONE, 1.0, relief=2.0, gain=1.3))
        layer = over(layer, roundness(pillar, x0, x0 + 6, dark=0.5, lift=0.12))
    return layer


def scene_senate_summon():
    """Summon the Senate: three magnates seated behind the council table, candles lit."""
    layer = senate_hall()
    layer = over(layer, magnate(24.5, 38, 0.78, GREEN_CLOTH, VELVET_RED, seed=2))
    layer = over(layer, magnate(57.5, 38, 0.78, BLUE_CLOTH, GREEN_CLOTH, seed=3))
    layer = over(layer, magnate(41, 35, 0.98, VELVET_RED, GREEN_CLOTH, seed=1))
    layer = over(layer, long_table(55, 62, 4.0, 78.0))
    layer = over(layer, candle(17, 56, 7))
    layer = over(layer, candle(65, 56, 7))
    layer = over(layer, rolled_scroll(41, 59, 17, 4.4, degrees=-4))
    return layer


def scene_senate_buyoff():
    """Buy Off a Magnate House: a house shield, a heavy purse, ducats spilling across the floor."""
    layer = backdrop([(0.0, hexc('#34548f')), (0.5, hexc('#18305e')), (1.0, hexc('#070f24'))], (41, 30), 50)
    layer = over(layer, glow(41, 40, 24, (200, 220, 255), 0.25))
    floor = poly([(0, 58), (82, 58), (82, 82), (0, 82)])
    layer = over(layer, gradient(floor, [(0.0, hexc('#1b2a4a')), (1.0, hexc('#080e1e'))], (0, 58), (0, 82)))
    layer = over(layer, heater_shield(33, 20, 24, 32, VELVET_RED, degrees=-9, device='bend'))
    layer = over(layer, purse(50, 50, 12.5))
    for i, (x, y, flat) in enumerate([(24, 66, 0.55), (31, 69, 0.55), (38, 67, 0.55), (45, 70, 0.55), (53, 68, 0.55), (60, 66, 0.55), (31, 63, 0.55)]):
        layer = over(layer, coin(x, y, 3.3, flat=flat, seed=i))
    layer = over(layer, coin(42, 62, 3.6, flat=1.0))
    return layer


def scene_senate_banners():
    """Call Up the Magnate Banners: three swallow-tailed banners on lances, one for each great house."""
    layer = backdrop([(0.0, hexc('#34548f')), (0.5, hexc('#18305e')), (1.0, hexc('#070f24'))], (41, 30), 50)
    layer = over(layer, glow(41, 30, 26, (190, 214, 255), 0.30))
    ground = poly([(0, 66), (82, 66), (82, 82), (0, 82)])
    layer = over(layer, gradient(ground, [(0.0, hexc('#1c3a2a')), (1.0, hexc('#08140e'))], (0, 66), (0, 82)))
    layer = over(layer, heater_shield(24, 56, 13, 17, VELVET_RED, degrees=-14, device='chevron'))
    layer = over(layer, sword((66, 71), -118, 15, blade_w=3.4, grip=4.5))
    layer = over(layer, banner((41, 71), -15, 46, 14, 13, BLUE_CLOTH, charge='cross', seed=2, side=-1))
    layer = over(layer, banner((41, 71), 15, 46, 14, 13, VELVET_RED, charge='stripe', seed=3, side=1))
    layer = over(layer, banner((41, 72), 0, 54, 20, 15, [(0.0, hexc('#5a4410')), (0.5, hexc('#c89a24')), (1.0, hexc('#f6dc7a'))],
                               charge='cross', seed=1, side=1))
    return layer


def chancery_room():
    layer = backdrop([(0.0, hexc('#2c5260')), (0.5, hexc('#17303a')), (1.0, hexc('#08141a'))], (30, 24), 54)
    layer = over(layer, glow(26, 22, 26, (190, 230, 240), 0.22))
    desk = poly([(0, 58), (82, 58), (82, 82), (0, 82)])
    layer = over(layer, shaded(desk, DARK_WOOD, 1.0, relief=1.6, gain=1.2, texture=noise(51, 1.4, 2)))
    layer = over(layer, solid(stroke([(0, 58.4), (82, 58.4)], 0.7), (210, 170, 90), 0.55))
    return layer


def finish_rescind(layer, rescind, arrow_at=(57, 55)):
    if not rescind:
        return layer
    layer = tint(desaturate(layer, 0.5), (0.9, 0.93, 1.0))
    return over(layer, return_arrow(arrow_at[0], arrow_at[1], 7.2, 3.0))


def scene_chancery(rescind=False):
    """The Chancery Ordinance: a sealed ordinance, pen and ink, the files tied up in red tape."""
    layer = chancery_room()
    layer = over(layer, file_stack(31, 69, 14))
    paper = charter(39, 34, 26, 32, seed=21, degrees=-5, lines=6, seal_r=4.8, broken=rescind,
                    cords=((24, 24, 28), (214, 164, 44)))
    layer = over(layer, tear_apart(paper, 40.0, 29.0, seed=7) if rescind else paper)
    layer = over(layer, quill((62, 64), 14, 32))
    layer = over(layer, inkwell(62, 68, 10, 8))
    return finish_rescind(layer, rescind, (60, 27))


def scene_settlement(rescind=False):
    """The Settlement Ordinance: a settlers' wagon and a new cottage on the ploughed marches."""
    layer = backdrop([(0.0, hexc('#3a2a5a')), (0.45, hexc('#c8783c')), (1.0, hexc('#f2c36a'))], (41, 48), 60)
    layer = gradient(full_mask(), [(0.0, hexc('#25305a')), (0.55, hexc('#b86a44')), (0.82, hexc('#f0b860')), (1.0, hexc('#f0b860'))], (0, 8), (0, 56))
    layer = over(layer, glow(60, 50, 26, (255, 220, 140), 0.55))
    hills = poly([(0, 50)] + bezier((0, 50), (14, 40), (30, 44), (46, 49), n=20)[1:] + bezier((46, 49), (60, 52), (70, 42), (82, 46), n=20)[1:] + [(82, 82), (0, 82)])
    layer = over(layer, shaded(hills, [(0.0, hexc('#12261a')), (0.5, hexc('#24462a')), (1.0, hexc('#4a7a3c'))], 2.0, relief=3.0, gain=1.0))
    layer = over(layer, furrows(54, 41, 0, 82, 82))
    layer = over(layer, cottage(62, 58, 0.9))
    layer = over(layer, wagon(30, 71, 1.15))
    return finish_rescind(layer, rescind, (58, 28))


def scene_cadastre(rescind=False):
    """The Cadastral Ordinance: a survey sheet of parcels, the surveyor's chain and dividers."""
    layer = backdrop([(0.0, hexc('#46341c')), (1.0, hexc('#1a1208'))], (41, 41), 56)
    layer = over(layer, survey_map())
    chain_pts = bezier((9, 64), (26, 46), (46, 76), (73, 54), n=24)
    gap = {11, 12} if rescind else None
    layer = over(layer, survey_chain(chain_pts, gap_at=gap))
    layer = over(layer, dividers((56, 20), 16, 7.5, 27))
    return finish_rescind(layer, rescind)


def vytis_at(cx, cy, height, **kw):
    """The Pahonia with its bounding box centred on (cx, cy): the design is 90 wide and 115 tall."""
    k = height / 115.0
    return vytis(cx - 5 * k, cy + 9 * k, k, **kw)


def pahonia_shield(cx, top, width, height):
    """A gold-bordered heater shield, red field, the Pahonia on it."""
    layer = heater_shield(cx, top, width, height, SCARLET_FIELD)
    inner_h = height * 0.86 * 0.80
    layer = over(layer, vytis_at(cx, top + height * 0.46, inner_h))
    return layer


def pahonia_emblem(centre, height):
    """The Pahonia as a banner charge."""
    return vytis_at(centre[0], centre[1], height)


def gediminas_emblem(centre, height):
    """The Columns of Gediminas as a banner charge."""
    return gediminas_columns(centre[0], centre[1], height)


def scene_rada_confirm():
    """Seek the Rada's Confirmation: two lords face each other across the council table, the privilege between them with its
    seals hanging over the edge, the Pahonia on the wall behind."""
    layer = backdrop([(0.0, hexc('#8c7442')), (0.5, hexc('#4c3a20')), (1.0, hexc('#1a1208'))], (41, 26), 56)
    for x in range(10, 74, 10):
        layer = over(layer, solid(poly([(x, 0), (x + 1.2, 0), (x + 1.2, 82), (x, 82)]), (16, 10, 4), 0.20))
    layer = over(layer, glow(41, 24, 26, (255, 214, 140), 0.40))
    layer = over(layer, pahonia_shield(41, 5, 26, 33))
    layer = over(layer, rada_lord(21, 35, 0.95, 1, RED_COAT, YELLOW_COAT, seed=2))
    layer = over(layer, rada_lord(61, 35, 0.95, -1, GREEN_CLOTH, SKY_BLUE_COAT, beard=BEARD_BROWN, seed=3))
    layer = over(layer, long_table(52, 58, 4.0, 78.0))
    layer = over(layer, privilege_charter(41, 44, 23, 15, seed=5, degrees=-2, lines=4))
    return layer


def scene_rada_lord():
    """Win Over a Wavering Lord: a hand offers the key of a starostwo under a sealed charter; a hesitating lord looks at it, his castle behind."""
    layer = gradient(full_mask(), [(0.0, hexc('#34566a')), (0.45, hexc('#b8825a')), (0.7, hexc('#f0c070')), (1.0, hexc('#f0c070'))], (0, 4), (0, 62))
    layer = over(layer, glow(26, 36, 30, (255, 224, 150), 0.45))
    hills = poly([(0, 46)] + bezier((0, 46), (14, 38), (30, 42), (44, 45), n=20)[1:] + bezier((44, 45), (60, 48), (72, 40), (82, 43), n=20)[1:] + [(82, 82), (0, 82)])
    layer = over(layer, shaded(hills, [(0.0, hexc('#10241a')), (0.5, hexc('#24462a')), (1.0, hexc('#4a7a3c'))], 2.0, relief=3.0, gain=1.0))
    layer = over(layer, castle(33, 46, 0.9))
    layer = over(layer, rada_lord(57, 30, 1.5, -1, RED_COAT, YELLOW_COAT, seed=2))
    layer = over(layer, privilege_charter(23, 33, 16, 19, seed=7, degrees=-5, lines=5, seals=1))
    layer = over(layer, open_hand(27, 59, 1.2, degrees=-8))
    layer = over(layer, gold_key(34, 50, 26, degrees=-20))
    return layer


def distant_lances(xs, base_y, top_y, seed=1):
    """A rank of lances and pennons far behind the riders: the rest of the household."""
    rng = random.Random(seed)
    layer = blank_layer()
    for x in xs:
        ty = top_y + rng.uniform(-3, 3)
        pole = stroke([(x, base_y), (x - 0.5, ty)], 0.45, caps=False)
        pen = poly([(x - 0.5, ty), (x + 4.2, ty + 1.0), (x + 3.0, ty + 2.0), (x + 4.2, ty + 3.0), (x - 0.5, ty + 3.0)])
        layer = over(layer, solid(pole, (36, 24, 28), 0.85), solid(pen, (130, 24, 30), 0.9))
    return layer


def scene_rada_retinues():
    """The Rada's Own Retinues: boyar household cavalry under two magnate standards, the Pahonia and the Columns of Gediminas."""
    layer = gradient(full_mask(), [(0.0, hexc('#243452')), (0.40, hexc('#7a5a6a')), (0.62, hexc('#e8a860')), (1.0, hexc('#e8a860'))], (0, 4), (0, 60))
    layer = over(layer, glow(41, 50, 34, (255, 226, 150), 0.55))
    ground = poly([(0, 56)] + bezier((0, 56), (20, 52), (60, 54), (82, 55), n=20)[1:] + [(82, 82), (0, 82)])
    layer = over(layer, gradient(ground, [(0.0, hexc('#6a5430')), (1.0, hexc('#241a0c'))], (0, 54), (0, 82)))
    layer = over(layer, distant_lances([14, 19, 52, 57, 62, 67], 52, 34, seed=3))
    rc, _ = boyar_rider(62, 51, 0.31, horse=DUN, coat=GREEN_CLOTH, flip=True, seed=5)
    layer = over(layer, rc)
    ra, Fa = boyar_rider(27, 54, 0.38, horse=GREY_HORSE, coat=SKY_BLUE_COAT, flip=True, seed=3)
    layer = over(layer, ra)
    layer = over(layer, lance_standard(Fa(58, 20), -2, 28, 17, 14, [(0.0, hexc('#6a0c12')), (0.6, hexc('#a81620')), (1.0, hexc('#d84c44'))],
                                 emblem=lambda c: gediminas_emblem(c, 8.0), seed=2, side=1))
    rb, Fb = boyar_rider(46, 57, 0.46, horse=BAY, coat=RED_COAT, flip=True, seed=1)
    layer = over(layer, rb)
    layer = over(layer, lance_standard(Fb(58, 20), -2, 36, 20, 16, SCARLET_FIELD,
                                 emblem=lambda c: pahonia_emblem(c, 13), seed=1, side=1))
    layer = over(layer, solid(blur(ellipse(41, 66, 30, 4.5), 2.2), (232, 200, 150), 0.40))
    return layer


SCENES = {
    'boyar_office': ('round', CRIMSON_ENAMEL, scene_boyar_office),
    'boyar_claimant': ('round', CRIMSON_ENAMEL, scene_boyar_claimant),
    'boyar_example': ('round', CRIMSON_ENAMEL, scene_boyar_example),
    'chancery_enact': ('octagon', BLACK_ENAMEL, lambda: scene_chancery(False)),
    'settlement_enact': ('octagon', BLACK_ENAMEL, lambda: scene_settlement(False)),
    'cadastre_enact': ('octagon', BLACK_ENAMEL, lambda: scene_cadastre(False)),
    'chancery_rescind': ('octagon', BLACK_ENAMEL, lambda: scene_chancery(True)),
    'settlement_rescind': ('octagon', BLACK_ENAMEL, lambda: scene_settlement(True)),
    'cadastre_rescind': ('octagon', BLACK_ENAMEL, lambda: scene_cadastre(True)),
    'senate_summon': ('arch', BLUE_ENAMEL, scene_senate_summon),
    'senate_buyoff': ('arch', BLUE_ENAMEL, scene_senate_buyoff),
    'senate_banners': ('arch', BLUE_ENAMEL, scene_senate_banners),
    'rada_confirm': ('shield', SCARLET_ENAMEL, scene_rada_confirm),
    'rada_lord': ('shield', SCARLET_ENAMEL, scene_rada_lord),
    'rada_retinues': ('shield', SCARLET_ENAMEL, scene_rada_retinues),
}


# --------------------------------------------------------------------------
# Rendering and output
# --------------------------------------------------------------------------

def render(name):
    kind, enamel, scene = SCENES[name]
    sprite = draw_frame(kind, enamel, scene())
    small = sprite.convert('RGBa').resize((SIZE, SIZE), Image.LANCZOS).convert('RGBA')
    return small.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2))


def preview_sheet(names, scale, columns=6):
    columns = max(1, min(columns, len(names)))
    cell = SIZE * scale
    rows = (len(names) + columns - 1) // columns
    sheet = Image.new('RGBA', (columns * (cell + 8) + 8, rows * (cell + 8) + 8), (22, 40, 42, 255))
    for i, name in enumerate(names):
        icon = render(name).resize((cell, cell), Image.NEAREST if scale >= 3 else Image.LANCZOS)
        sheet.alpha_composite(icon, (8 + (i % columns) * (cell + 8), 8 + (i // columns) * (cell + 8)))
    return sheet


def sprite_name(key):
    return f'GFX_rip_{key}'


def texture_path(key):
    return f'{TEXTURE_DIR}/{key}.dds'


def gfx_text():
    lines = ['spriteTypes = {']
    for key in SCENES:
        lines.append(f'\tspriteType = {{ name = "{sprite_name(key)}" texturefile = "{texture_path(key)}" }}')
    lines.append('}')
    return '\r\n'.join(lines) + '\r\n'


def write_all():
    for key in SCENES:
        path = ROOT / texture_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        render(key).save(path, format='DDS')
    (ROOT / GFX_FILE).write_bytes(gfx_text().encode('ascii'))
    sheet = ROOT / TEXTURE_DIR / 'source' / 'abilities_preview.png'
    sheet.parent.mkdir(parents=True, exist_ok=True)
    preview_sheet(list(SCENES), 4).save(sheet)
    print(f'wrote {len(SCENES)} sprites, {GFX_FILE} and {sheet.relative_to(ROOT).as_posix()}')


def check_all():
    problems = []
    gfx = ROOT / GFX_FILE
    if not gfx.is_file() or gfx.read_bytes() != gfx_text().encode('ascii'):
        problems.append(f'{GFX_FILE} is stale')
    for key in SCENES:
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
    print(f'ABILITY ICONS PASS: {len(SCENES)} sprites match the generator (tolerance {CHECK_TOLERANCE}).')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='redraw and compare with the files in the repository')
    parser.add_argument('--preview', metavar='PNG', help='write a contact sheet instead of the sprites')
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--columns', type=int, default=6)
    parser.add_argument('--only', action='append', help='limit --preview to these sprites')
    args = parser.parse_args(argv)
    if args.preview:
        names = args.only or list(SCENES)
        preview_sheet(names, args.scale, args.columns).save(args.preview)
        print('preview written', args.preview)
        return 0
    if args.check:
        return check_all()
    write_all()
    return 0


if __name__ == '__main__':
    sys.exit(main())
