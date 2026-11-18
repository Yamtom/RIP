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
GFX_FILE = 'interface/RIP_shared_government_captaincy_icons.gfx'

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


def bastion_points(cx, cy, half, cut):
    return [
        (cx - half + cut, cy - half),
        (cx + half - cut, cy - half),
        (cx + half, cy - half + cut),
        (cx + half, cy + half - cut),
        (cx + half - cut, cy + half),
        (cx - half + cut, cy + half),
        (cx - half, cy + half - cut),
        (cx - half, cy - half + cut),
    ]


def keep_poly():
    c = SIZE / 2.0
    return poly(bastion_points(c, c, 36.2, 8.2))


def frame_masks(kind):
    """Outer silhouette, inner edge of the gold band, of the enamel, and the picture area."""
    c = SIZE / 2.0
    if kind == 'hex':
        return (poly(hex_points(c, c, 39.2)), poly(hex_points(c, c, 34.8)),
                poly(hex_points(c, c, 32.5)), poly(hex_points(c, c, 31.5)))
    if kind == 'keep':
        return (poly(bastion_points(c, c, 36.2, 8.2)),
                poly(bastion_points(c, c, 32.2, 6.6)),
                poly(bastion_points(c, c, 30.0, 5.8)),
                poly(bastion_points(c, c, 29.0, 5.4)))
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
    """Man the Border Posts: pure painted Palanok fortress commanding the Carpathian pass."""
    return kit.painted_backdrop(
        'gfx/interface/great_projects/source/palanok_fortress.png',
        focus=(0.45, 0.45), zoom=1.22, tint_rgb=(0.98, 1.02, 0.96), brightness=0.92, contrast=1.08,
    )


def scene_salt():
    """Pledge the Salt Chambers: oak salt chest brimming with rock-salt crystals and royal wax seal."""
    return kit.emblem_scene(
        kit.extra_cutout(1, 0),
        top_rgb=(18, 56, 32), bot_rgb=(6, 20, 12), glow_rgb=(186, 244, 198),
        box=50, cy=42,
    )


def scene_opryshky():
    """Enlist the Opryshky: crossed Carpathian brass bartka axes bound with a crimson cord."""
    return kit.emblem_scene(
        kit.extra_cutout(0, 0),
        top_rgb=(26, 48, 24), bot_rgb=(10, 18, 8), glow_rgb=(255, 214, 138),
        box=50, cy=42,
    )


def scene_towers():
    """Post the Watchtowers: pure painted timber watchtower and palisade of the Sich on the steppe line."""
    return kit.painted_backdrop(
        'gfx/interface/great_projects/source/zaporozhian_sich.png',
        focus=(0.74, 0.44), zoom=1.35, tint_rgb=(0.98, 1.00, 1.04), brightness=0.92, contrast=1.08,
    )


def scene_patrols():
    """Send Out the Patrols: brass frontier signal horn crossed with a steel cavalry sabre."""
    return kit.emblem_scene(
        kit.extra_cutout(1, 1),
        top_rgb=(24, 42, 68), bot_rgb=(10, 16, 28), glow_rgb=(255, 218, 146),
        box=50, cy=42,
    )


def scene_settlers():
    """Settle the Watch: frontier heraldic shield with golden wheat ears and crossed spears."""
    return kit.emblem_scene(
        kit.gov_cutout('prosperity'),
        top_rgb=(28, 48, 66), bot_rgb=(10, 18, 26), glow_rgb=(255, 224, 148),
        box=50, cy=42,
    )


def scene_reform():
    """The reform card: painted Carpathian pass with timber watchtower and waymarker shield."""
    return kit.painted_backdrop(
        'gfx/interface/missions/source/uzh_identity_branch_locked_2.png',
        focus=(0.50, 0.46), zoom=1.08, contrast=1.08,
    )


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
        picture = scene_reform().resize((51, 51), Image.LANCZOS)
        picture = picture.filter(ImageFilter.UnsharpMask(radius=0.6, percent=38, threshold=3))
        return uzh.frame_reform(picture)
    kind, enamel, scene = BUTTONS[key]
    sprite = draw_frame(kind, enamel, scene())
    small = sprite.convert('RGBa').resize((SIZE, SIZE), Image.LANCZOS).convert('RGBA')
    return kit.clean_alpha_rgb(small.filter(ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2)))


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
        kit.save_dds_atomic(render(key), path)
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
