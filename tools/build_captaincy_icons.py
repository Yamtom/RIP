"""Draw the button icons of the Carpathian Captaincy and the Border Watch.

Seven sprites for two button-only government mechanics (and one reform card):

  uzh_carpathian_captaincy_mechanic   3 buttons  82x82  hexagonal gold frame, forest-green enamel
      captaincy_posts      Man the Border Posts      a blockhouse and a striped customs barrier in the pass
      captaincy_salt       Pledge the Salt Chambers  salt blocks, a sealed pledge and a miner's pick
      captaincy_opryshky   Enlist the Opryshky       a highlander's felt hat, a bartka axe and a camp fire
  rip_border_watch_mechanic           3 buttons  82x82  crenellated gold frame, slate-blue enamel
      watch_towers         Post the Watchtowers      a timber tower with a beacon fire on the steppe line
      watch_patrols        Send Out the Patrols      a mounted patrol under a pennant
      watch_settlers       Settle the Watch          a cottage, a plough field and a watchtower
  uzh_carpathian_captaincy_reform     57x57  the reform card (vanilla: government_reform_*)
      captaincy_reform     Carpathian Captaincy      the Verecke pass with a blockhouse, a barrier and salt carts

The art is painted procedurally with the toolkit of tools/build_government_ability_icons.py
(polygons, gradients, a lit height field and noise, supersampled 8x), as the sprites of
the sibling mechanics are, so no image model and no external file is involved and --check
can redraw every sprite and compare it with the checked-in DDS. The toolkit is imported
read-only: this file adds its own frames and scenes and changes nothing there.

    python tools/build_captaincy_icons.py            # write DDS + gfx
    python tools/build_captaincy_icons.py --check    # redraw and compare
    python tools/build_captaincy_icons.py --preview out.png --scale 4
    python tools/build_captaincy_icons.py --preview out.png --only captaincy_posts --only watch_towers
"""
from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_government_ability_icons as kit  # noqa: E402  (shared painting toolkit, read-only here)
import build_uzh_states_general_icons as uzh  # noqa: E402  (palettes and the reform-card frame, read-only here)
from build_government_ability_icons import (  # noqa: E402
    CHECK_TOLERANCE, DARK_WOOD, FUR, GOLD, LEATHER, SIZE, SS, STEEL, THATCH, VELVET_RED, WAX, WOOD,
    Image, ImageChops, ImageDraw, ImageFilter, np,
    arc_points, backdrop, bezier, blank_layer, blank_mask, blur, clip, contact, desaturate, ellipse,
    erode, from_alpha, full_mask, glow, gradient, hexc, inter, minus, noise, outline, over, poly,
    radial, roundness, shadow, shaded, solid, stroke, strands, tint, union,
)

ROOT = HERE.parent
TEXTURE_DIR = 'gfx/interface/rip_government'
GFX_FILE = 'interface/rip_captaincy_icons.gfx'

# --------------------------------------------------------------------------
# Palettes (dark -> lit) that the toolkit does not ship
# --------------------------------------------------------------------------

FOREST_ENAMEL = [(0.0, hexc('#04140a')), (0.5, hexc('#0f3a1c')), (1.0, hexc('#2a7a3e'))]
SLATE_ENAMEL = [(0.0, hexc('#0a1220')), (0.5, hexc('#1e3350')), (1.0, hexc('#46688e'))]
SALT_WHITE = uzh.SALT
STONE_WARM = uzh.STONE_WARM
ROCK = uzh.ROCK
GRASS = uzh.GRASS
TILE = uzh.TILE
CRIMSON = uzh.CRIMSON
SHINGLE = [(0.0, hexc('#241608')), (0.4, hexc('#4e3216')), (0.6, hexc('#6e4a22')), (0.85, hexc('#9a7038')), (1.0, hexc('#c8a066'))]
FELT = [(0.0, hexc('#0a0806')), (0.4, hexc('#1e1a16')), (0.6, hexc('#302a24')), (0.85, hexc('#4c443a')), (1.0, hexc('#78705f'))]
FLAME = [(0.0, hexc('#8a1a04')), (0.4, hexc('#e0480a')), (0.7, hexc('#ff9a1c')), (1.0, hexc('#fff0a0'))]
STEPPE = [(0.0, hexc('#2e2a12')), (0.4, hexc('#6a5e24')), (0.6, hexc('#8c8030')), (0.85, hexc('#b4aa50')), (1.0, hexc('#e0d890'))]
CHESTNUT = [(0.0, hexc('#180a04')), (0.4, hexc('#3e1e0c')), (0.62, hexc('#5e3216')), (0.85, hexc('#86502a')), (1.0, hexc('#b88a58'))]
LIGHT_WOOD = [(0.0, hexc('#5a3818')), (0.4, hexc('#8a5a2a')), (0.62, hexc('#b07a3c')), (0.85, hexc('#d6a45c')), (1.0, hexc('#f4d296'))]
STRIPE_WHITE = [(0.0, hexc('#9a9a94')), (0.5, hexc('#e4e2d8')), (1.0, hexc('#ffffff'))]


# --------------------------------------------------------------------------
# Frames: a hexagon (the Captaincy) and a crenellated keep (the Watch)
# --------------------------------------------------------------------------

def hex_points(cx, cy, radius, rot=0.0):
    return [(cx + radius * math.cos(math.radians(rot + 60 * i)), cy + radius * math.sin(math.radians(rot + 60 * i)))
            for i in range(6)]


def keep_poly():
    body = poly([(4.0, 12.0), (78.0, 12.0), (78.0, 79.0), (4.0, 79.0)])
    teeth = union(*[poly([(x, 3.6), (x + 11.0, 3.6), (x + 11.0, 12.5), (x, 12.5)]) for x in (4.0, 25.0, 46.0, 67.0)])
    return union(body, teeth)


def frame_masks(kind):
    """Outer silhouette, inner edge of the gold band, of the enamel, and the picture area."""
    c = SIZE / 2.0
    if kind == 'hex':
        return (poly(hex_points(c, c, 40.8)), poly(hex_points(c, c, 36.2)),
                poly(hex_points(c, c, 33.8)), poly(hex_points(c, c, 32.8)))
    if kind == 'keep':
        outer = keep_poly()
        return outer, erode(outer, 3.9), erode(outer, 5.6), erode(outer, 6.4)
    raise ValueError(kind)


def draw_frame(kind, enamel_stops, scene_layer):
    """A finished sprite: drop shadow, picture, enamel, gold band with its bevel (as the toolkit's draw_frame)."""
    outer, gold_in, enamel_in, scene = frame_masks(kind)
    band = minus(outer, gold_in)
    enamel = minus(gold_in, enamel_in)
    inner_line = minus(enamel_in, scene)
    sprite = blank_layer()
    sprite = over(sprite, shadow(outer, 0.6, 1.0, 0.9, 0.6))
    picture = clip(scene_layer, scene)
    rim_depth = np.asarray(ImageChops.invert(blur(scene, 2.6)), dtype=np.float32) / 255.0
    sprite = over(sprite, picture, from_alpha((0, 0, 0), rim_depth * (np.asarray(scene, dtype=np.float32) / 255.0) * 0.38))
    sprite = over(sprite, shaded(enamel, enamel_stops, 0.5, relief=1.3, gain=1.5))
    sprite = over(sprite, shaded(inner_line, GOLD, 0.3, relief=0.7, gain=1.6))
    sprite = over(sprite, shaded(band, GOLD, 1.3, relief=3.0, gain=1.9, spec=0.25, texture=noise(7, 1.6, 2)))
    sprite = over(sprite, outline(outer, 0.45, (24, 12, 4), 0.95))
    return sprite


# --------------------------------------------------------------------------
# Props
# --------------------------------------------------------------------------

def fir(fx, fy, fh, seed=1):
    """A spruce of the Carpathian slopes: a stack of dark boughs."""
    pts = [(fx - fh * 0.34, fy), (fx + fh * 0.34, fy), (fx + fh * 0.14, fy - fh * 0.40), (fx + fh * 0.26, fy - fh * 0.40),
           (fx + fh * 0.08, fy - fh * 0.72), (fx + fh * 0.16, fy - fh * 0.72), (fx, fy - fh),
           (fx - fh * 0.16, fy - fh * 0.72), (fx - fh * 0.08, fy - fh * 0.72), (fx - fh * 0.26, fy - fh * 0.40),
           (fx - fh * 0.14, fy - fh * 0.40)]
    tree = poly(pts)
    layer = blank_layer()
    layer = over(layer, shadow(tree, 0.5, 0.7, 0.6, 0.4), outline(tree, 0.35, (6, 16, 8), 0.9))
    layer = over(layer, shaded(tree, [(0.0, hexc('#06160c')), (0.5, hexc('#16401f')), (1.0, hexc('#3f7a42'))], 0.8,
                               relief=1.6, gain=1.4, texture=noise(seed + 40, 0.9, 2)))
    return layer


def ridge(points, bottom, stops, softness=3.0, relief=3.0, gain=0.8, seed=1):
    shape = poly([(points[0][0], bottom)] + points + [(points[-1][0], bottom)])
    return shaded(shape, stops, softness, relief=relief, gain=gain, texture=noise(seed, 3.0, 2))


def wave(x0, x1, base, amp, freq, phase, step=3):
    return [(x, base - amp * math.sin(x / 82.0 * math.pi * freq + phase) - amp * 0.35 * math.sin(x / 6.0 + phase)) for x in range(x0, x1 + 1, step)]


def pennant(base, length, height, field=CRIMSON, side=1):
    """A swallow-tailed pennant streaming from the top of a pole at `base`."""
    x, y = base
    flag = poly([(x, y), (x + side * length, y + height * 0.12), (x + side * length * 0.72, y + height * 0.5),
                 (x + side * length, y + height * 0.88), (x, y + height)])
    layer = blank_layer()
    layer = over(layer, outline(flag, 0.3, (30, 4, 6), 0.95), shaded(flag, field, 0.6, relief=1.2, gain=1.6, spec=0.2))
    return layer


def timber(mask, seed, planks=True):
    """Weathered wood with plank lines."""
    layer = shaded(mask, SHINGLE, 0.7, relief=1.6, gain=1.5, texture=noise(seed, 0.8, 3))
    if planks:
        box = mask.getbbox()
        if box:
            x0, y0, x1, y1 = [v / SS for v in box]
            lines = blank_mask()
            d = ImageDraw.Draw(lines)
            x = x0 + 1.6
            while x < x1:
                d.line(kit._px([(x, y0), (x, y1)]), fill=255, width=max(1, int(0.2 * SS)))
                x += 2.4
            layer = over(layer, solid(inter(lines, mask), (20, 12, 6), 0.45))
    return layer


# --------------------------------------------------------------------------
# Scenes
# --------------------------------------------------------------------------

def scene_posts():
    """Man the Border Posts: a blockhouse above the pass, a striped customs barrier across the road."""
    layer = gradient(full_mask(), [(0.0, hexc('#46688e')), (0.40, hexc('#c8a27e')), (0.62, hexc('#f4d490')), (1.0, hexc('#f4d490'))],
                     (0, 4), (0, 56))
    layer = over(layer, glow(64, 33, 28, (255, 236, 170), 0.6))
    layer = over(layer, ridge(wave(0, 82, 40, 9, 1.6, 0.5), 70, [(0.0, hexc('#3a4a62')), (0.5, hexc('#6a7c96')), (1.0, hexc('#b8c4d4'))], seed=3))
    layer = over(layer, ridge(wave(0, 82, 48, 6, 2.2, 2.0), 72, [(0.0, hexc('#14302a')), (0.5, hexc('#2e5a48')), (1.0, hexc('#6a9a80'))], seed=5))
    ground = poly([(0, 58)] + [(x, 58 - 2.0 * math.sin(x / 9.0)) for x in range(0, 83, 3)] + [(82, 82), (0, 82)])
    layer = over(layer, shaded(ground, GRASS, 2.5, relief=3.4, gain=1.1, texture=noise(8, 3.0, 3)))
    road = poly([(36, 58), (48, 58), (60, 82), (20, 82)])
    layer = over(layer, gradient(road, [(0.0, hexc('#8c7a58')), (1.0, hexc('#5a4a30'))], (0, 58), (0, 82)))
    # the rocky knoll under the blockhouse
    knoll = poly([(6, 60), (12, 50), (22, 45), (38, 45), (46, 50), (50, 60)])
    layer = over(layer, shaded(knoll, ROCK, 1.6, relief=3.0, gain=1.4, texture=noise(6, 2.0, 3)))
    # the blockhouse: stone footing, timber storey, shingle roof, glowing window, pennant
    foot = poly([(14, 46), (36, 46), (36, 38), (14, 38)])
    upper = poly([(12, 38), (38, 38), (36, 25), (14, 25)])
    roof = poly([(10, 25), (40, 25), (25, 13)])
    whole = union(foot, upper, roof)
    layer = over(layer, shadow(whole, 0.9, 1.2, 1.0, 0.5), outline(whole, 0.5, (20, 12, 6), 0.95))
    layer = over(layer, shaded(foot, STONE_WARM, 0.8, relief=1.8, gain=1.5, texture=noise(11, 1.4, 3)))
    layer = over(layer, timber(upper, 12))
    layer = over(layer, shaded(roof, SHINGLE, 0.9, relief=2.0, gain=1.5, texture=noise(13, 0.7, 3)))
    layer = over(layer, roundness(union(foot, upper), 12, 38, dark=0.45, lift=0.15, peak=0.3))
    layer = over(layer, solid(poly([(22, 36), (28, 36), (28, 30), (22, 30)]), (255, 206, 110), 0.95),
                 solid(minus(poly([(21.4, 36.6), (28.6, 36.6), (28.6, 29.4), (21.4, 29.4)]), poly([(22, 36), (28, 36), (28, 30), (22, 30)])), (30, 18, 8), 0.95))
    layer = over(layer, solid(poly([(19, 46), (19, 41), (23, 41), (23, 46)]), (14, 8, 6), 0.9))
    pole = stroke([(25, 13), (25, 4)], 0.6, caps=False)
    layer = over(layer, outline(pole, 0.25, (20, 14, 8), 0.9), solid(pole, (190, 160, 100), 1.0))
    layer = over(layer, pennant((25.3, 4.2), 9.0, 5.2))
    # the customs barrier: a striped pole on a post, counterweight behind
    post = poly([(46, 60), (50, 60), (50, 52), (46, 52)])
    layer = over(layer, shadow(post, 0.6, 0.9, 0.6, 0.4), outline(post, 0.35, (20, 12, 6), 0.95), shaded(post, DARK_WOOD, 0.4, relief=1.0, gain=1.4))
    beam = stroke([(36, 56.6), (66, 52.4)], 2.0, caps=False)
    stripes = blank_mask()
    sd = ImageDraw.Draw(stripes)
    for i in range(10):
        x0 = 36 + i * 3.1
        sd.line(kit._px([(x0, 56.6 - (x0 - 36) * 0.14 + 1.5), (x0 + 1.0, 56.6 - (x0 + 1 - 36) * 0.14 - 1.5)]), fill=255, width=int(1.4 * SS))
    layer = over(layer, shadow(beam, 0.6, 0.9, 0.6, 0.4), outline(beam, 0.35, (30, 8, 8), 0.95))
    layer = over(layer, shaded(beam, STRIPE_WHITE, 0.4, relief=1.0, gain=1.4))
    layer = over(layer, solid(inter(stripes, beam), (186, 28, 32), 0.95))
    counter = ellipse(37.6, 57.2, 2.0)
    layer = over(layer, outline(counter, 0.3, (20, 12, 6), 0.9), shaded(counter, STONE_WARM, 0.5, relief=1.0, gain=1.4))
    # firs
    for fx, fy, fh in ((5, 64, 14), (12, 62, 11), (72, 62, 15), (78, 66, 12)):
        layer = over(layer, fir(fx, fy, fh, seed=int(fx)))
    return layer


def salt_block(x, y, w, h, tilt=0.0, seed=1):
    """A block of rock salt: pale, faceted, bluish in the shade."""
    pts = [(x, y), (x + w, y - tilt), (x + w + w * 0.18, y - h * 0.22 - tilt), (x + w * 0.14, y - h * 0.22), (x, y)]
    front = poly([(x, y), (x + w, y - tilt), (x + w, y - h - tilt), (x, y - h)])
    top = poly([(x, y - h), (x + w, y - h - tilt), (x + w + w * 0.2, y - h - tilt - h * 0.24), (x + w * 0.2, y - h - h * 0.24)])
    side = poly([(x + w, y - tilt), (x + w + w * 0.2, y - tilt - h * 0.24), (x + w + w * 0.2, y - h - tilt - h * 0.24), (x + w, y - h - tilt)])
    whole = union(front, top, side)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 0.8, 1.1, 0.9, 0.5), outline(whole, 0.4, (60, 66, 76), 0.9))
    layer = over(layer, shaded(front, SALT_WHITE, 0.5, relief=1.2, gain=1.5, texture=noise(seed, 0.8, 2)))
    layer = over(layer, shaded(top, SALT_WHITE, 0.4, relief=1.0, gain=1.2))
    layer = over(layer, solid(side, (110, 128, 160), 0.35), solid(front, (96, 118, 150), 0.12))
    layer = over(layer, solid(stroke([(x + w * 0.2, y - h * 0.8), (x + w * 0.5, y - h * 0.5)], 0.25), (255, 255, 255), 0.7))
    return layer


def pickaxe(base, degrees, length):
    """A miner's pick stuck head-down: haft up, a curved double-pointed head."""
    pts = lambda p: kit.place(p, degrees, base)
    haft = poly(pts([(-1.0, 0), (1.0, 0), (0.85, -length), (-0.85, -length)]))
    head = poly(pts([(-9.0, -length + 3.6), (-4.0, -length - 0.6), (0.0, -length - 1.4), (4.0, -length - 0.6), (9.0, -length + 3.6),
                     (4.0, -length + 1.2), (0.0, -length + 1.8), (-4.0, -length + 1.2)]))
    layer = blank_layer()
    layer = over(layer, shadow(union(haft, head), 0.9, 1.2, 0.9, 0.5), outline(union(haft, head), 0.5, (16, 14, 14), 0.95))
    layer = over(layer, shaded(haft, WOOD, 0.4, relief=0.9, gain=1.6, texture=noise(21, 0.7, 2)))
    layer = over(layer, shaded(head, STEEL, 1.0, relief=2.0, gain=1.3, spec=0.2))
    return layer


def scene_salt():
    """Pledge the Salt Chambers: salt blocks, a miner's pick, a sealed deed of pledge."""
    layer = gradient(full_mask(), [(0.0, hexc('#16343c')), (0.55, hexc('#0c1e26')), (1.0, hexc('#050e12'))], (0, 0), (0, 82))
    layer = over(layer, glow(34, 34, 30, (150, 210, 220), 0.30))
    floor = poly([(0, 60), (82, 60), (82, 82), (0, 82)])
    layer = over(layer, shaded(floor, DARK_WOOD, 1.0, relief=1.6, gain=1.1, texture=noise(31, 1.4, 2)))
    layer = over(layer, solid(stroke([(0, 60.4), (82, 60.4)], 0.7), (210, 170, 90), 0.5))
    # a stack of salt blocks
    rows = ((60.0, 3, 12.0), (51.0, 2, 17.5), (42.0, 1, 23.0))
    k = 0
    for y, count, x0 in rows:
        for i in range(count):
            layer = over(layer, salt_block(x0 + i * 11.2, y, 10.4, 8.6, tilt=0.0, seed=k + 1))
            k += 1
    layer = over(layer, pickaxe((58.5, 61), 17, 30))
    # the deed of pledge, with its wax seal, lying in front
    layer = over(layer, kit.charter(31, 62.5, 22, 12, seed=33, degrees=-5, lines=3, seal_r=3.4))
    # coins
    for cx, cy in ((46.0, 65.0), (50.5, 63.5), (48.5, 67.5)):
        layer = over(layer, kit.coin(cx, cy, 2.6, flat=0.55, seed=int(cx)))
    return layer


def bartka(base, degrees, length):
    """The highlander's bartka: a long haft with a narrow-bladed axe head and a hammer at the back."""
    pts = lambda p: kit.place(p, degrees, base)
    haft = poly(pts([(-0.95, 0), (0.95, 0), (0.8, -length), (-0.8, -length)]))
    top = -length + 4.0
    blade = poly(pts([(0.8, top - 7.0), (2.4, top - 7.4), (9.4, top - 1.0), (9.0, top + 1.0), (2.4, top + 7.0), (0.8, top + 6.8)]))
    hammer = poly(pts([(-0.8, top - 2.6), (-4.6, top - 2.0), (-4.6, top + 1.6), (-0.8, top + 2.2)]))
    head = union(blade, hammer)
    layer = blank_layer()
    layer = over(layer, shadow(union(haft, head), 1.0, 1.4, 1.0, 0.5), outline(union(haft, head), 0.6, (226, 188, 128), 0.55))
    layer = over(layer, shaded(haft, LIGHT_WOOD, 0.4, relief=0.9, gain=1.6, texture=noise(24, 0.7, 2)))
    layer = over(layer, shaded(head, STEEL, 1.0, relief=2.0, gain=1.3, spec=0.2))
    edge = stroke(pts([(9.2, top - 1.0), (8.8, top + 1.0)]), 0.6)
    layer = over(layer, solid(edge, (250, 252, 255), 0.92))
    # a pair of brass rings on the haft, as the highlanders wear it
    for ry in (-length * 0.4, -length * 0.62):
        ring = stroke(pts([(-1.3, ry), (1.3, ry)]), 0.9, caps=False)
        layer = over(layer, shaded(ring, GOLD, 0.2, relief=0.6, gain=1.7, spec=0.3))
    return layer


def highland_hat(cx, cy, scale=1.0):
    """A round felt hat with a low crown, a red band and a long feather."""
    def P(x, y):
        return (cx + x * scale, cy + y * scale)
    brim = ellipse(*P(0, 4), 15 * scale, 4.0 * scale)
    crown = poly([P(-9, 4)] + [P(-9 + 18 * t, 4 - 11 * math.sin(math.pi * t) ** 0.7) for t in np.linspace(0, 1, 24)] + [P(9, 4)])
    band = poly([P(-9.2, 2.2), P(9.2, 2.2), P(9.4, 4.6), P(-9.4, 4.6)])
    whole = union(brim, crown)
    layer = blank_layer()
    layer = over(layer, shadow(whole, 1.0, 1.4, 1.2, 0.55), outline(whole, 0.55, (10, 8, 6), 0.95))
    layer = over(layer, shaded(brim, FELT, 0.8, relief=1.4, gain=1.4, texture=noise(41, 0.8, 2)))
    layer = over(layer, shaded(crown, FELT, 1.4, relief=2.8, gain=1.5, spec=0.08, texture=noise(42, 0.8, 3)))
    layer = over(layer, roundness(crown, cx - 9 * scale, cx + 9 * scale, dark=0.5, lift=0.18, peak=0.3))
    layer = over(layer, shaded(band, VELVET_RED, 0.4, relief=1.0, gain=1.6, spec=0.2))
    feather = stroke([P(6, 2)] + [P(x, y) for x, y in bezier((6, 2), (12, -6), (18, -12), (20, -20))[1:]], 1.5 * scale)
    layer = over(layer, outline(feather, 0.35, (30, 24, 20), 0.95), solid(feather, (240, 236, 224), 1.0))
    quill_line = stroke([P(6, 2)] + [P(x, y) for x, y in bezier((6, 2), (12, -6), (18, -12), (20, -20))[1:]], 0.3 * scale)
    layer = over(layer, solid(quill_line, (120, 110, 96), 0.8))
    return layer


def campfire(cx, base_y, scale=1.0):
    def P(x, y):
        return (cx + x * scale, base_y + y * scale)
    layer = blank_layer()
    layer = over(layer, glow(cx, base_y - 6 * scale, 22 * scale, (255, 160, 60), 0.55))
    logs = union(stroke([P(-9, 0), P(8, -4)], 2.6 * scale), stroke([P(9, 0), P(-8, -4)], 2.6 * scale))
    flame = poly([P(-6, -3)] + [P(x, y) for x, y in bezier((-6, -3), (-8, -12), (-1, -14), (0, -26))[1:]] +
                 [P(x, y) for x, y in bezier((0, -26), (2, -14), (8, -12), (6, -3))[1:]])
    core = poly([P(-3, -3)] + [P(x, y) for x, y in bezier((-3, -3), (-4, -9), (0, -10), (0, -17))[1:]] +
                [P(x, y) for x, y in bezier((0, -17), (1, -10), (4, -9), (3, -3))[1:]])
    layer = over(layer, outline(logs, 0.4, (16, 8, 4), 0.95), shaded(logs, DARK_WOOD, 0.5, relief=1.2, gain=1.4))
    layer = over(layer, shaded(flame, FLAME, 1.0, relief=2.4, gain=1.3))
    layer = over(layer, shaded(core, FLAME, 0.6, relief=1.6, gain=1.5, spec=0.3))
    return layer


def scene_opryshky():
    """Enlist the Opryshky: a highlander's hat, a bartka and a camp fire under the firs."""
    layer = gradient(full_mask(), [(0.0, hexc('#0a1c16')), (0.55, hexc('#14382a')), (1.0, hexc('#05120c'))], (0, 0), (0, 82))
    layer = over(layer, glow(41, 66, 46, (255, 150, 60), 0.50))
    for fx, fy, fh, s in ((6, 68, 30, 1), (15, 66, 24, 2), (68, 66, 26, 3), (77, 70, 32, 4), (25, 64, 16, 5), (58, 64, 18, 6)):
        layer = over(layer, tint(fir(fx, fy, fh, seed=s), (0.55, 0.62, 0.6)))
    ground = poly([(0, 66), (82, 66), (82, 82), (0, 82)])
    layer = over(layer, shaded(ground, DARK_WOOD, 1.0, relief=1.4, gain=1.0, texture=noise(51, 1.4, 2)))
    layer = over(layer, campfire(46, 67, 0.85))
    layer = over(layer, bartka((27, 67), 14, 44))
    layer = over(layer, highland_hat(47, 37, 0.95))
    return layer


def watch_tower(cx, base_y, width, height, beacon=True, seed=1):
    """A timber watchtower on four posts with a railed platform and, optionally, a beacon fire."""
    hw = width / 2.0
    legs = union(stroke([(cx - hw, base_y), (cx - hw * 0.6, base_y - height)], 1.5, caps=False),
                 stroke([(cx + hw, base_y), (cx + hw * 0.6, base_y - height)], 1.5, caps=False))
    brace = union(stroke([(cx - hw * 0.92, base_y - height * 0.12), (cx + hw * 0.64, base_y - height * 0.56)], 0.9, caps=False),
                  stroke([(cx + hw * 0.92, base_y - height * 0.12), (cx - hw * 0.64, base_y - height * 0.56)], 0.9, caps=False))
    platform = poly([(cx - hw * 0.84, base_y - height), (cx + hw * 0.84, base_y - height), (cx + hw * 0.84, base_y - height - 1.8),
                     (cx - hw * 0.84, base_y - height - 1.8)])
    hut_h = height * 0.30
    hut = poly([(cx - hw * 0.6, base_y - height - 1.8), (cx + hw * 0.6, base_y - height - 1.8), (cx + hw * 0.6, base_y - height - 1.8 - hut_h),
                (cx - hw * 0.6, base_y - height - 1.8 - hut_h)])
    roof = poly([(cx - hw * 0.8, base_y - height - 1.8 - hut_h), (cx + hw * 0.8, base_y - height - 1.8 - hut_h),
                 (cx, base_y - height - 1.8 - hut_h - hw * 0.8)])
    whole = union(legs, brace, platform, hut, roof)
    layer = blank_layer()
    layer = over(layer, contact(cx, base_y + 0.5, width * 0.8, 1.6, 0.5))
    layer = over(layer, shadow(whole, 0.9, 1.2, 1.0, 0.5), outline(whole, 0.45, (16, 10, 6), 0.95))
    layer = over(layer, shaded(legs, DARK_WOOD, 0.4, relief=1.0, gain=1.5))
    layer = over(layer, shaded(brace, WOOD, 0.3, relief=0.8, gain=1.5))
    layer = over(layer, shaded(platform, WOOD, 0.4, relief=1.0, gain=1.4))
    layer = over(layer, timber(hut, seed))
    layer = over(layer, shaded(roof, SHINGLE, 0.7, relief=1.6, gain=1.5, texture=noise(seed + 3, 0.7, 3)))
    if beacon:
        fire_cx = cx
        fire_base = base_y - height - 1.8 - hut_h - hw * 0.8
        layer = over(layer, campfire(fire_cx, fire_base + 1.0, 0.62))
    return layer


def scene_towers():
    """Post the Watchtowers: a tower line on the steppe, a beacon fire on the near one."""
    layer = gradient(full_mask(), [(0.0, hexc('#243452')), (0.34, hexc('#7a5a6a')), (0.56, hexc('#e8a860')), (1.0, hexc('#e8a860'))], (0, 0), (0, 58))
    layer = over(layer, glow(26, 54, 36, (255, 226, 150), 0.60))
    ground = poly([(0, 56)] + [(x, 56 - 1.4 * math.sin(x / 8.0) - 0.8 * math.sin(x / 3.0)) for x in range(0, 83, 3)] + [(82, 82), (0, 82)])
    layer = over(layer, gradient(ground, [(0.0, hexc('#7a6a34')), (0.45, hexc('#4a4018')), (1.0, hexc('#1e1a0a'))], (0, 54), (0, 82)))
    grass = strands(ground, 7, 380, 2.4, 0.16, [hexc('#a89c48'), hexc('#6a6226'), hexc('#d8cc78'), hexc('#3a3414')],
                    lambda x, y: -math.pi / 2, spread=0.28)
    layer = over(layer, grass)
    # far towers, small and dark against the glow
    for fx, fy, fh, w in ((64, 56, 14, 5.0), (74, 56, 10, 3.6), (52, 56, 8, 3.0)):
        layer = over(layer, tint(watch_tower(fx, fy, w, fh, beacon=False, seed=int(fx)), (0.55, 0.52, 0.6)))
    layer = over(layer, watch_tower(32, 74, 17, 34, beacon=True, seed=3))
    return layer


def scene_patrols():
    """Send Out the Patrols: two riders with a pennant, riding the line against the sunset."""
    layer = gradient(full_mask(), [(0.0, hexc('#243452')), (0.34, hexc('#7a5a6a')), (0.56, hexc('#e8a860')), (1.0, hexc('#e8a860'))], (0, 0), (0, 58))
    layer = over(layer, glow(60, 52, 34, (255, 226, 150), 0.60))
    ground = poly([(0, 54)] + [(x, 54 - 1.6 * math.sin(x / 9.0 + 1.0)) for x in range(0, 83, 3)] + [(82, 82), (0, 82)])
    layer = over(layer, gradient(ground, [(0.0, hexc('#7a6a34')), (0.45, hexc('#4a4018')), (1.0, hexc('#1e1a0a'))], (0, 52), (0, 82)))
    layer = over(layer, strands(ground, 8, 320, 2.4, 0.16, [hexc('#a89c48'), hexc('#6a6226'), hexc('#d8cc78'), hexc('#3a3414')],
                                lambda x, y: -math.pi / 2, spread=0.28))
    layer = over(layer, tint(watch_tower(14, 56, 6.0, 16, beacon=False, seed=5), (0.55, 0.52, 0.6)))
    far, _ = kit.boyar_rider(24, 60, 0.30, horse=CHESTNUT, coat=kit.SKY_BLUE_COAT, flip=False, seed=2)
    layer = over(layer, tint(far, (0.8, 0.8, 0.86)))
    rider, F = kit.boyar_rider(54, 66, 0.52, horse=kit.DUN, coat=kit.RED_COAT, flip=False, seed=1)
    layer = over(layer, rider)
    layer = over(layer, kit.lance_standard(F(58, 20), -2, 38, 17, 11, [(0.0, hexc('#6a0c12')), (0.6, hexc('#a81620')), (1.0, hexc('#d84c44'))],
                                           emblem=None, seed=1, side=-1))
    layer = over(layer, solid(blur(ellipse(48, 74, 28, 4.0), 2.2), (232, 200, 150), 0.30))
    return layer


def scene_settlers():
    """Settle the Watch: a cottage on a ploughed strip, a watchtower on the rise behind."""
    layer = gradient(full_mask(), [(0.0, hexc('#3a2a5a')), (0.45, hexc('#c8783c')), (0.8, hexc('#f0b860')), (1.0, hexc('#f0b860'))], (0, 4), (0, 56))
    layer = over(layer, glow(62, 48, 26, (255, 220, 140), 0.55))
    hills = poly([(0, 50)] + bezier((0, 50), (14, 40), (30, 44), (46, 49), n=20)[1:] + bezier((46, 49), (60, 52), (70, 42), (82, 46), n=20)[1:] + [(82, 82), (0, 82)])
    layer = over(layer, shaded(hills, [(0.0, hexc('#12261a')), (0.5, hexc('#24462a')), (1.0, hexc('#4a7a3c'))], 2.0, relief=3.0, gain=1.0))
    layer = over(layer, tint(watch_tower(66, 47, 7.0, 20, beacon=False, seed=6), (0.62, 0.6, 0.66)))
    layer = over(layer, kit.furrows(54, 30, 0, 82, 82))
    layer = over(layer, kit.cottage(36, 66, 1.0))
    # a palisade of pointed stakes in front
    for i in range(11):
        x = 6 + i * 3.4
        stake = poly([(x - 1.2, 80), (x + 1.2, 80), (x + 1.2, 72.5), (x, 70.4), (x - 1.2, 72.5)])
        layer = over(layer, shadow(stake, 0.5, 0.8, 0.5, 0.4), outline(stake, 0.3, (16, 10, 6), 0.95), shaded(stake, WOOD, 0.3, relief=0.8, gain=1.5))
    # a haystack
    stack = poly([(60, 70), (74, 70), (72, 62), (67, 57), (62, 62)])
    layer = over(layer, shadow(stack, 0.8, 1.0, 0.8, 0.45), outline(stack, 0.4, (40, 28, 8), 0.95),
                 shaded(stack, THATCH, 1.0, relief=2.0, gain=1.3, texture=noise(61, 0.6, 3)))
    return layer


def scene_reform():
    """The reform card: the Verecke pass with a blockhouse, the customs barrier and two salt carts."""
    layer = scene_posts()
    # a pair of salt carts crossing the foreground, white loads under canvas
    for cx, sc in ((20, 0.5), (47, 0.46)):
        layer = over(layer, kit.wagon(cx, 79, sc))
    return layer


# --------------------------------------------------------------------------
# Sprite table, rendering and output
# --------------------------------------------------------------------------

# key -> (frame kind, enamel, scene)
BUTTONS = {
    'captaincy_posts': ('hex', FOREST_ENAMEL, scene_posts),
    'captaincy_salt': ('hex', FOREST_ENAMEL, scene_salt),
    'captaincy_opryshky': ('hex', FOREST_ENAMEL, scene_opryshky),
    'watch_towers': ('keep', SLATE_ENAMEL, scene_towers),
    'watch_patrols': ('keep', SLATE_ENAMEL, scene_patrols),
    'watch_settlers': ('keep', SLATE_ENAMEL, scene_settlers),
}
REFORM_KEY = 'captaincy_reform'
REFORM_SPRITE = 'government_reform_rip_gfx_reform_uzh_carpathian_captaincy_icon'
KEYS = list(BUTTONS) + [REFORM_KEY]


def render(key):
    if key == REFORM_KEY:
        picture = uzh.to_pixels(scene_reform(), (0, 0, 82, 82), (51, 51))
        picture = picture.filter(ImageFilter.UnsharpMask(radius=0.6, percent=28, threshold=6))
        return uzh.frame_reform(picture)
    kind, enamel, scene = BUTTONS[key]
    sprite = draw_frame(kind, enamel, scene())
    small = sprite.convert('RGBa').resize((SIZE, SIZE), Image.LANCZOS).convert('RGBA')
    return small.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2))


def sprite_name(key):
    return REFORM_SPRITE if key == REFORM_KEY else f'GFX_rip_{key}'


def texture_path(key):
    return f'{TEXTURE_DIR}/{key}.dds'


def gfx_text():
    lines = ['spriteTypes = {']
    for key in KEYS:
        extra = ' norefcount = yes' if key == REFORM_KEY else ''
        lines.append(f'\tspriteType = {{ name = "{sprite_name(key)}" texturefile = "{texture_path(key)}"{extra} }}')
    lines.append('}')
    return '\r\n'.join(lines) + '\r\n'


def preview_sheet(names, scale, columns=4):
    columns = max(1, min(columns, len(names)))
    images = [render(n) for n in names]
    cell_w = max(im.width for im in images) * scale + 8
    cell_h = max(im.height for im in images) * scale + 8
    rows = (len(images) + columns - 1) // columns
    sheet = Image.new('RGBA', (columns * cell_w + 8, rows * cell_h + 8), (22, 40, 42, 255))
    for i, im in enumerate(images):
        big = im.resize((im.width * scale, im.height * scale), Image.NEAREST if scale >= 3 else Image.LANCZOS)
        sheet.alpha_composite(big, (8 + (i % columns) * cell_w, 8 + (i // columns) * cell_h))
    return sheet


def write_all():
    for key in KEYS:
        path = ROOT / texture_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        render(key).save(path, format='DDS')
    (ROOT / GFX_FILE).write_bytes(gfx_text().encode('ascii'))
    sheet = ROOT / TEXTURE_DIR / 'source' / 'captaincy_preview.png'
    sheet.parent.mkdir(parents=True, exist_ok=True)
    preview_sheet(KEYS, 4).save(sheet)
    print(f'wrote {len(KEYS)} sprites, {GFX_FILE} and {sheet.relative_to(ROOT).as_posix()}')


def check_all():
    problems = []
    gfx = ROOT / GFX_FILE
    if not gfx.is_file() or gfx.read_bytes() != gfx_text().encode('ascii'):
        problems.append(f'{GFX_FILE} is stale')
    for key in KEYS:
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
    print(f'CAPTAINCY ICONS PASS: {len(KEYS)} sprites match the generator (tolerance {CHECK_TOLERANCE}).')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='redraw and compare with the files in the repository')
    parser.add_argument('--preview', metavar='PNG', help='write a contact sheet instead of the sprites')
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--columns', type=int, default=4)
    parser.add_argument('--only', action='append', help='limit --preview to these sprites')
    args = parser.parse_args(argv)
    if args.preview:
        preview_sheet(args.only or KEYS, args.scale, args.columns).save(args.preview)
        print('preview written', args.preview)
        return 0
    if args.check:
        return check_all()
    write_all()
    return 0


if __name__ == '__main__':
    sys.exit(main())
