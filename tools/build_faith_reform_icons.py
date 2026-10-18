"""Draw the icons of the two faith mechanics added in October 2026.

Seven 82x82 sprites, built from the toolkit of build_government_ability_icons.py:

  zaz_holy_patronage    4 sprites   round blue-enamel frame
      zaz_monastery   endow a military monastery
      zaz_escort      escort the hierarchy
      zaz_faithful    raise the faithful
      zaz_zeal        the emblem of the Zeal bar (drawn at half size)
  plt_nomocanon         3 sprites   arched green-enamel frame
      plt_seal        seal the Nomocanon
      plt_guild       patronage of the guild parishes
      plt_veto        call the city assembly (the veto)

    python tools/build_faith_reform_icons.py            # write DDS + gfx
    python tools/build_faith_reform_icons.py --check    # redraw and compare
    python tools/build_faith_reform_icons.py --preview out.png --scale 4
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_government_ability_icons as G  # noqa: E402

ROOT = G.ROOT
TEXTURE_DIR = G.TEXTURE_DIR
GFX_FILE = 'interface/rip_faith_reform_icons.gfx'
hexc = G.hexc

GREEN_ENAMEL = [(0.0, hexc('#06180c')), (0.5, hexc('#12482a')), (1.0, hexc('#2c8a52'))]
DUSK = [(0.0, hexc('#3a4a7a')), (0.5, hexc('#1c2850')), (1.0, hexc('#080c20'))]
EMBER = [(0.0, hexc('#8a3a1a')), (0.5, hexc('#3a1408')), (1.0, hexc('#100604'))]
HALL = [(0.0, hexc('#3f6a52')), (0.5, hexc('#1c4030')), (1.0, hexc('#08180f'))]


def ground(layer, top, stops):
    strip = G.poly([(0, top), (82, top), (82, 82), (0, 82)])
    return G.over(layer, G.gradient(strip, stops, (0, top), (0, 82)))


def scene_zaz_monastery():
    """A whitewashed chapel of the order with two candles lit before it."""
    layer = G.backdrop(DUSK, (41, 30), 52)
    layer = G.over(layer, G.glow(41, 36, 26, (255, 200, 120), 0.30))
    layer = ground(layer, 62, [(0.0, hexc('#1c3a2a')), (1.0, hexc('#08140e'))])
    layer = G.over(layer, G.cottage(41, 63, 1.55))
    layer = G.over(layer, G.candle(14, 72, 9))
    layer = G.over(layer, G.candle(68, 72, 9))
    return layer


def scene_zaz_escort():
    """A bishop's banner carried between crossed swords."""
    layer = G.backdrop(DUSK, (41, 30), 52)
    layer = G.over(layer, G.glow(41, 30, 26, (190, 214, 255), 0.30))
    layer = ground(layer, 66, [(0.0, hexc('#1c3a2a')), (1.0, hexc('#08140e'))])
    layer = G.over(layer, G.sword((16, 72), -58, 48, blade_w=3.6, grip=5.0))
    layer = G.over(layer, G.sword((66, 72), -122, 48, blade_w=3.6, grip=5.0))
    layer = G.over(layer, G.banner((41, 72), 0, 52, 21, 16, G.VELVET_RED, charge='cross', seed=2, side=1))
    return layer


def scene_zaz_faithful():
    """The faithful in a burning town: a banner and a raised sword against the fire."""
    layer = G.backdrop(EMBER, (41, 66), 56)
    layer = G.over(layer, G.glow(41, 58, 32, (255, 140, 50), 0.55))
    layer = G.over(layer, G.glow(18, 62, 14, (255, 190, 80), 0.45))
    layer = G.over(layer, G.glow(66, 60, 14, (255, 190, 80), 0.45))
    layer = ground(layer, 66, [(0.0, hexc('#2a1208')), (1.0, hexc('#0a0402'))])
    layer = G.over(layer, G.cottage(17, 67, 0.8))
    layer = G.over(layer, G.cottage(66, 67, 0.8))
    layer = G.over(layer, G.sword((41, 72), -90, 34, blade_w=4.0, grip=5.5))
    layer = G.over(layer, G.banner((27, 72), -10, 46, 17, 14, G.BLUE_CLOTH, charge='cross', seed=3, side=1))
    return layer


def scene_zaz_zeal():
    """The Zeal emblem: one great flame over the cross of the order."""
    layer = G.backdrop(DUSK, (41, 41), 56)
    layer = G.over(layer, G.glow(41, 48, 30, (255, 190, 90), 0.55))
    layer = G.over(layer, G.candle(41, 66, 16))
    cross_v = G.poly([(39.2, 10), (42.8, 10), (42.8, 32), (39.2, 32)])
    cross_h = G.poly([(33, 15), (49, 15), (49, 18.6), (33, 18.6)])
    cross = G.union(cross_v, cross_h)
    layer = G.over(layer, G.outline(cross, 0.4, (40, 22, 4), 0.95), G.shaded(cross, G.GOLD, 0.4, relief=1.0, gain=1.8, spec=0.5))
    return layer


def scene_plt_seal():
    """The Nomocanon rolled and sealed in wax, a candle at its side."""
    layer = G.backdrop(HALL, (41, 36), 52)
    layer = G.over(layer, G.glow(41, 36, 26, (255, 214, 140), 0.28))
    layer = ground(layer, 64, [(0.0, hexc('#2a1a0c')), (1.0, hexc('#0a0604'))])
    layer = G.over(layer, G.rolled_scroll(40, 46, 40, 12, degrees=-6))
    layer = G.over(layer, G.wax_seal(50, 43, 6.5, seed=4))
    layer = G.over(layer, G.candle(14, 62, 10))
    return layer


def scene_plt_guild():
    """A guild's purse and coins before the parish church of the quarter."""
    layer = G.backdrop(HALL, (41, 36), 52)
    layer = G.over(layer, G.glow(41, 32, 26, (255, 214, 140), 0.25))
    layer = ground(layer, 62, [(0.0, hexc('#2a1a0c')), (1.0, hexc('#0a0604'))])
    layer = G.over(layer, G.cottage(54, 62, 1.15))
    layer = G.over(layer, G.purse(24, 56, 11))
    for i, (x, y) in enumerate([(14, 70), (22, 72), (31, 70), (38, 73)]):
        layer = G.over(layer, G.coin(x, y, 3.3, flat=0.55, seed=i))
    return layer


def scene_plt_veto():
    """The city assembly refuses: a charter torn across, its seal broken."""
    layer = G.backdrop(HALL, (41, 36), 52)
    layer = G.over(layer, G.glow(41, 36, 26, (255, 214, 140), 0.25))
    paper = G.charter(41, 38, 40, 46, seed=8, degrees=-4, lines=6, seal_r=5.5, broken=True, torn=True)
    layer = G.over(layer, paper)
    return layer


SCENES = {
    'zaz_monastery': ('round', G.BLUE_ENAMEL, scene_zaz_monastery),
    'zaz_escort': ('round', G.BLUE_ENAMEL, scene_zaz_escort),
    'zaz_faithful': ('round', G.BLUE_ENAMEL, scene_zaz_faithful),
    'zaz_zeal': ('round', G.BLUE_ENAMEL, scene_zaz_zeal),
    'plt_seal': ('arch', GREEN_ENAMEL, scene_plt_seal),
    'plt_guild': ('arch', GREEN_ENAMEL, scene_plt_guild),
    'plt_veto': ('arch', GREEN_ENAMEL, scene_plt_veto),
}


def render(name):
    kind, enamel, scene = SCENES[name]
    sprite = G.draw_frame(kind, enamel, scene())
    small = sprite.convert('RGBa').resize((G.SIZE, G.SIZE), Image.LANCZOS).convert('RGBA')
    return small.filter(G.ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2))


def preview_sheet(names, scale, columns=4):
    columns = max(1, min(columns, len(names)))
    cell = G.SIZE * scale
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


# EU4 builds the sprites of a power's generated modifiers from the ideas_EU4
# filename convention; the Zeal emblem stands in for all three.
POWER_ICONS = ('zaz_cossack_zeal', 'monthly_zaz_cossack_zeal', 'zaz_cossack_zeal_gain_modifier')


def power_icon():
    return render('zaz_zeal').resize((64, 64), Image.LANCZOS)


def write_all():
    for key in POWER_ICONS:
        path = ROOT / 'gfx/interface/ideas_EU4' / f'{key}.dds'
        path.parent.mkdir(parents=True, exist_ok=True)
        power_icon().save(path, format='DDS')
    for key in SCENES:
        path = ROOT / texture_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        render(key).save(path, format='DDS')
    (ROOT / GFX_FILE).write_bytes(gfx_text().encode('ascii'))
    sheet = ROOT / TEXTURE_DIR / 'source' / 'faith_reform_preview.png'
    sheet.parent.mkdir(parents=True, exist_ok=True)
    preview_sheet(list(SCENES), 4).save(sheet)
    print(f'wrote {len(SCENES)} sprites, {GFX_FILE} and {sheet.relative_to(ROOT).as_posix()}')


def check_all():
    problems = []
    gfx = ROOT / GFX_FILE
    if not gfx.is_file() or gfx.read_bytes() != gfx_text().encode('ascii'):
        problems.append(f'{GFX_FILE} is stale')
    for key in POWER_ICONS:
        path = ROOT / 'gfx/interface/ideas_EU4' / f'{key}.dds'
        if not path.is_file():
            problems.append(f'gfx/interface/ideas_EU4/{key}.dds is missing')
        elif int(np.abs(np.asarray(Image.open(path).convert('RGBA'), dtype=np.int16)
                        - np.asarray(power_icon(), dtype=np.int16)).max()) > G.CHECK_TOLERANCE:
            problems.append(f'gfx/interface/ideas_EU4/{key}.dds differs from a fresh drawing')
    for key in SCENES:
        path = ROOT / texture_path(key)
        if not path.is_file():
            problems.append(f'{texture_path(key)} is missing')
            continue
        have = np.asarray(Image.open(path).convert('RGBA'), dtype=np.int16)
        want = np.asarray(render(key), dtype=np.int16)
        worst = int(np.abs(have - want).max()) if have.shape == want.shape else 999
        if worst > G.CHECK_TOLERANCE:
            problems.append(f'{texture_path(key)} differs from a fresh drawing (max channel difference {worst})')
    if problems:
        print('\n'.join(problems))
        return 1
    print(f'FAITH REFORM ICONS PASS: {len(SCENES)} sprites match the generator.')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--preview', metavar='PNG')
    parser.add_argument('--scale', type=int, default=4)
    parser.add_argument('--columns', type=int, default=4)
    parser.add_argument('--only', action='append')
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
