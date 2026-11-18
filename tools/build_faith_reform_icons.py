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
GFX_FILE = 'interface/RIP_shared_church_reform_icons.gfx'
hexc = G.hexc

GREEN_ENAMEL = [(0.0, hexc('#06180c')), (0.5, hexc('#12482a')), (1.0, hexc('#2c8a52'))]
DUSK = [(0.0, hexc('#3a4a7a')), (0.5, hexc('#1c2850')), (1.0, hexc('#080c20'))]
EMBER = [(0.0, hexc('#8a3a1a')), (0.5, hexc('#3a1408')), (1.0, hexc('#100604'))]
HALL = [(0.0, hexc('#3f6a52')), (0.5, hexc('#1c4030')), (1.0, hexc('#08180f'))]


def ground(layer, top, stops):
    strip = G.poly([(0, top), (82, top), (82, 82), (0, 82)])
    return G.over(layer, G.gradient(strip, stops, (0, top), (0, 82)))


def hierarch_cutout() -> Image.Image:
    key = ('hierarch', 'gc_archbishop')
    if key not in G._PAINTED_CACHE:
        im = G._raw_image('gfx/interface/rip_church/gc_archbishop_source.png')
        right_half = im.crop((im.width // 2, 0, im.width, im.height))
        bbox = right_half.getbbox()
        G._PAINTED_CACHE[key] = right_half.crop(bbox) if bbox else right_half
    return G._PAINTED_CACHE[key]


def scene_zaz_monastery():
    """Endow a Military Monastery: rolled monastery endowment charter with Orthodox cross and red wax seal."""
    return G.emblem_scene(
        G.priv_cutout('brotherhood_charters'),
        top_rgb=(20, 42, 76), bot_rgb=(8, 16, 32), glow_rgb=(255, 218, 142),
        box=51, cy=43,
    )


def scene_zaz_escort():
    """Escort the Hierarchy: painted Orthodox metropolitan hierarch with cross and staff on a sapphire medallion."""
    return G.emblem_scene(
        hierarch_cutout(),
        top_rgb=(24, 48, 82), bot_rgb=(10, 18, 36), glow_rgb=(255, 224, 152),
        box=52, cy=44,
    )


def scene_zaz_faithful():
    """Raise the Faithful: crimson-and-gold Archangel Michael war gonfalon on a dark sapphire-ember medallion."""
    return G.emblem_scene(
        G.banner_cutout('ro_banner_war_v2'),
        top_rgb=(42, 26, 62), bot_rgb=(14, 10, 26), glow_rgb=(255, 206, 132),
        box=52, cy=43,
    )


def scene_zaz_zeal():
    """The Cossack Zeal emblem: golden three-bar Orthodox cross on a deep navy-blue medallion."""
    return G.emblem_scene(
        G.religion_cutout('russian_orthodox'),
        top_rgb=(18, 38, 72), bot_rgb=(6, 14, 30), glow_rgb=(255, 216, 134),
        box=50, cy=42,
    )


def scene_plt_seal():
    """Seal the Nomocanon: leather-bound Nomocanon codex embossed with a golden Orthodox cross and quill."""
    return G.emblem_scene(
        G.priv_cutout('basilian_schools'),
        top_rgb=(16, 54, 34), bot_rgb=(6, 20, 12), glow_rgb=(255, 222, 148),
        box=51, cy=44,
    )


def scene_plt_guild():
    """Patronage of the Guild Parishes: brotherhood guild printing press beneath a golden Orthodox cross."""
    return G.emblem_scene(
        G.disaster_cutout('rip_uc_brotherhoods', 0),
        top_rgb=(20, 58, 38), bot_rgb=(8, 22, 14), glow_rgb=(255, 224, 150),
        box=50, cy=43,
    )


def scene_plt_veto():
    """Call the City Assembly (the veto): golden scales of justice over the assembly law book."""
    return G.emblem_scene(
        G.priv_cutout('synodal_courts'),
        top_rgb=(18, 52, 42), bot_rgb=(6, 18, 16), glow_rgb=(255, 222, 146),
        box=50, cy=44,
    )


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
    return G.clean_alpha_rgb(small.filter(G.ImageFilter.UnsharpMask(radius=0.6, percent=55, threshold=2)))


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
# filename convention; build a freestanding Cossack Zeal emblem triplet.
POWER_ICONS = ('zaz_cossack_zeal', 'monthly_zaz_cossack_zeal', 'zaz_cossack_zeal_gain_modifier')
_POWER_TRIPLET: dict[str, Image.Image] | None = None


def power_icon(key: str = 'zaz_cossack_zeal') -> Image.Image:
    global _POWER_TRIPLET
    if _POWER_TRIPLET is None:
        from build_core_ruthenia_icons import make_idea_modifier_triplet, zaz_cossack_zeal_emblem
        base_ic, monthly_ic, gain_ic = make_idea_modifier_triplet(zaz_cossack_zeal_emblem())
        _POWER_TRIPLET = {
            'zaz_cossack_zeal': base_ic,
            'monthly_zaz_cossack_zeal': monthly_ic,
            'zaz_cossack_zeal_gain_modifier': gain_ic,
        }
    return _POWER_TRIPLET[key]


def write_all():
    for key in POWER_ICONS:
        path = ROOT / 'gfx/interface/ideas_EU4' / f'{key}.dds'
        G.save_dds_atomic(power_icon(key), path)
    for key in SCENES:
        path = ROOT / texture_path(key)
        G.save_dds_atomic(render(key), path)
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
                        - np.asarray(power_icon(key), dtype=np.int16)).max()) > G.CHECK_TOLERANCE:
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
