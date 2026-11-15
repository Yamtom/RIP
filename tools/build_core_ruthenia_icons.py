"""Build and verify Core Ruthenia reform icons, Jewish privilege icons, and the Vilnius Palace monument picture.

Uses existing checked-in source artwork (gfx/interface/rip_government/source/atlas.png and source/*.png),
vanilla donor elements where available, and the procedural toolkit to replace raw vanilla placeholders
and the low-detail Vilnius Palace placeholder while enforcing EU4 DDS/alpha contracts.

    python -B tools/build_core_ruthenia_icons.py
    python -B tools/build_core_ruthenia_icons.py --check
    python -B tools/build_core_ruthenia_icons.py --privileges-only
    python -B tools/build_core_ruthenia_icons.py --privileges-only --check
    python -B tools/build_core_ruthenia_icons.py --missions-only
    python -B tools/build_core_ruthenia_icons.py --missions-only --check
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tests'))

from collections import deque
import numpy as np
from clausewitz_testlib import vanilla_root  # noqa: E402
import build_uzh_states_general_icons as uzh  # noqa: E402


def resize_clean(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    pre = image.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
    pixels = pre.load()
    width, height = pre.size
    for y in range(height):
        for x in range(width):
            if pixels[x, y][3] == 0:
                pixels[x, y] = (0, 0, 0, 0)
    return pre


def remove_atlas_background(image: Image.Image, pad_ratio: float = 0.08) -> Image.Image:
    image = image.copy()
    pixels = image.load()
    width, height = image.size
    corners = [pixels[0, 0][:3], pixels[width - 1, 0][:3],
               pixels[0, height - 1][:3], pixels[width - 1, height - 1][:3]]
    bg_r = sum(c[0] for c in corners) // 4
    bg_g = sum(c[1] for c in corners) // 4
    bg_b = sum(c[2] for c in corners) // 4
    visited = bytearray(width * height)
    pending = deque()

    def enqueue(x: int, y: int) -> None:
        index = y * width + x
        if not visited[index]:
            visited[index] = 1
            pending.append(index)

    for x in range(width):
        enqueue(x, 0)
        enqueue(x, height - 1)
    for y in range(1, height - 1):
        enqueue(0, y)
        enqueue(width - 1, y)
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            red, green, blue, _ = pixels[x, y]
            if max(abs(red - bg_r), abs(green - bg_g), abs(blue - bg_b)) <= 18:
                enqueue(x, y)

    while pending:
        index = pending.popleft()
        x, y = index % width, index // width
        red, green, blue, alpha = pixels[x, y]
        dist = max(abs(red - bg_r), abs(green - bg_g), abs(blue - bg_b))
        teal_excess = min(green - red, blue - red)
        if dist <= 32 or (teal_excess >= 16 and red < 42 and blue < 85):
            pixels[x, y] = (0, 0, 0, 0)
            if x:
                enqueue(x - 1, y)
            if x + 1 < width:
                enqueue(x + 1, y)
            if y:
                enqueue(x, y - 1)
            if y + 1 < height:
                enqueue(x, y + 1)
        elif dist < 54 or (teal_excess >= 8 and red < 55 and blue < 95):
            factor = min(1.0, max(0.0, (dist - 32) / 22.0))
            new_alpha = int(alpha * factor)
            if blue > red and green > red:
                green = (green + red) // 2
                blue = (blue + red) // 2
            pixels[x, y] = (red, green, blue, new_alpha) if new_alpha > 0 else (0, 0, 0, 0)

    for y in range(1, height - 1):
        for x in range(1, width - 1):
            if pixels[x, y][3] > 0:
                neighbors = sum(
                    1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dx or dy) and pixels[x + dx, y + dy][3] > 32
                )
                if neighbors <= 1:
                    pixels[x, y] = (0, 0, 0, 0)

    bbox = image.getbbox()
    if bbox:
        cropped = image.crop(bbox)
        cw, ch = cropped.size
        side = int(max(cw, ch) / (1.0 - 2 * pad_ratio))
        out = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        out.paste(cropped, ((side - cw) // 2, (side - ch) // 2))
        return out
    return image

CHECK_TOLERANCE = 3

REFORM_FILES = (
    'rip_gfx_reform_cossack_host_icon.dds',
    'rip_gfx_reform_zaz_sich_brotherhood_icon.dds',
    'rip_gfx_reform_het_starshyna_oligarchy_icon.dds',
    'rip_gfx_reform_het_academy_enlightenment_icon.dds',
    'rip_gfx_reform_zaz_free_host_icon.dds',
    'rip_gfx_reform_zaz_last_sich_icon.dds',
)

PRIVILEGE_FILES = (
    'rip_gfx_privilege_jewish_tax_farmers_icon.dds',
    'rip_gfx_privilege_jewish_loan_banks_icon.dds',
    'rip_gfx_privilege_jewish_kahal_autonomy_icon.dds',
    'rip_gfx_privilege_jewish_black_sea_network_icon.dds',
)

LEGACY_MISSION_ART = (
    ('mission_ukr_magdeburg_laws', 'magdeburg_charter'),
    ('petro_mohyla', 'petro_mohyla'),
)

LOCKED_BRANCH_MISSIONS = (
    ('rip_gfx_mission_uzh_identity_branch_locked_1_icon', 'uzh_identity_branch_locked_1'),
    ('rip_gfx_mission_uzh_identity_branch_locked_2_icon', 'uzh_identity_branch_locked_2'),
    ('rip_gfx_mission_uzh_identity_branch_locked_3_icon', 'uzh_identity_branch_locked_3'),
    ('rip_gfx_mission_chr_identity_branch_locked_1_icon', 'chr_identity_branch_locked_1'),
    ('rip_gfx_mission_chr_identity_branch_locked_2_icon', 'chr_identity_branch_locked_2'),
    ('rip_gfx_mission_chr_identity_branch_locked_3_icon', 'chr_identity_branch_locked_3'),
)

# Each entry is (registered sprite name, checked-in source PNG stem).
AUTHORED_MISSION_ART = (
    ('rip_gfx_mission_mazepa_patronage_icon', 'mazepa_patronage'),
    ('rip_gfx_mission_dnieper_chaika_icon', 'dnieper_chaika'),
    ('rip_gfx_mission_ruthenian_granaries_icon', 'ruthenian_granaries'),
    ('rip_gfx_mission_frontier_fortress_icon', 'frontier_fortress'),
    ('rip_gfx_mission_chumak_salt_caravan_icon', 'chumak_salt_caravan'),
    ('rip_gfx_mission_cossack_rada_icon', 'cossack_rada'),
)
MISSION_ART = LEGACY_MISSION_ART + LOCKED_BRANCH_MISSIONS + AUTHORED_MISSION_ART
MISSION_FILES = tuple(f'{sprite}.dds' for sprite, _ in MISSION_ART)

EXTENDED_PRIVILEGE_STEMS = (
    'seimski_statutes', 'left_bank_settlement', 'roman_concordat',
    'strong_appanages', 'collegium_learning', 'starshyna_council',
    'grain_charters', 'sich_rada', 'chaiky', 'magnate_supremacy',
    'brotherhood_charters', 'basilian_schools', 'parish_concord', 'synodal_courts',
)

PRIVILEGE_FILES += tuple(f'rip_gfx_privilege_{stem}_icon.dds' for stem in EXTENDED_PRIVILEGE_STEMS)

PRIVILEGE_SOURCES = (
    ('rip_gfx_privilege_jewish_tax_farmers_icon.dds', 'jewish_tax_farmers_compact'),
    ('rip_gfx_privilege_jewish_loan_banks_icon.dds', 'jewish_loan_banks_compact'),
    ('rip_gfx_privilege_jewish_kahal_autonomy_icon.dds', 'jewish_kahal_autonomy_compact'),
    ('rip_gfx_privilege_jewish_black_sea_network_icon.dds', 'jewish_black_sea_network_compact'),
) + tuple((f'rip_gfx_privilege_{stem}_icon.dds', stem) for stem in EXTENDED_PRIVILEGE_STEMS)

MAGNATE_MODIFIER_FILES = (
    ('magnates_influence_modifier.dds', 'nobles_influence_modifier.dds'),
    ('magnates_loyalty_modifier.dds', 'nobles_loyalty_modifier.dds'),
    ('magnates_loyalty_modifier_opposite.dds', 'nobles_loyalty_modifier_opposite.dds'),
    ('magnates_privilege_slots.dds', 'nobles_privilege_slots.dds'),
)

# Religion reference exports are maintained by build_religion_icon_strips.py.
OBSOLETE_RELIGION_ICONS = ()

ATLAS = Image.open(ROOT / 'gfx/interface/rip_government/source/atlas.png').convert('RGBA')
ROWS = (0, 0.25, 0.5, 0.732, 1.0)


def atlas_emblem(gx: int, gy: int, pad_ratio: float = 0.05) -> Image.Image:
    tile = ATLAS.crop((
        round(gx * ATLAS.width / 4),
        round(ROWS[gy] * ATLAS.height),
        round((gx + 1) * ATLAS.width / 4),
        round(ROWS[gy + 1] * ATLAS.height),
    ))
    return remove_atlas_background(tile, pad_ratio=pad_ratio)


def source_emblem(name: str) -> Image.Image:
    return Image.open(ROOT / f'gfx/interface/rip_government/source/{name}.png').convert('RGBA')


def build_reform_icons() -> dict[str, Image.Image]:
    """Delegate reform icon generation to build_reform_icons so both generators and tests stay in lockstep."""
    import build_reform_icons as R
    game = vanilla_root()
    if game is not None:
        return {Path(p).name: Image.fromarray(px, 'RGBA') for p, px in R.build_all(game).items()}
    return {
        name: Image.open(ROOT / 'gfx/interface/government_reform_icons' / name).convert('RGBA')
        for name in REFORM_FILES
    }


def strip_privilege_background(image: Image.Image) -> Image.Image:
    """Remove the flat dark charcoal backdrop from a painted 512x512 privilege master via border flood-fill."""
    im = image.copy()
    px = im.load()
    w, h = im.size
    corners = [px[0, 0][:3], px[w - 1, 0][:3], px[0, h - 1][:3], px[w - 1, h - 1][:3]]
    br = sum(c[0] for c in corners) // 4
    bg = sum(c[1] for c in corners) // 4
    bb = sum(c[2] for c in corners) // 4
    vis = bytearray(w * h)
    q: deque[int] = deque()

    def enq(x: int, y: int) -> None:
        idx = y * w + x
        if not vis[idx]:
            vis[idx] = 1
            q.append(idx)

    for x in range(w):
        enq(x, 0)
        enq(x, h - 1)
    for y in range(1, h - 1):
        enq(0, y)
        enq(w - 1, y)

    while q:
        idx = q.popleft()
        x, y = idx % w, idx // w
        r, g, b, a = px[x, y]
        d = max(abs(r - br), abs(g - bg), abs(b - bb))
        if d <= 20:
            px[x, y] = (0, 0, 0, 0)
            if x:
                enq(x - 1, y)
            if x + 1 < w:
                enq(x + 1, y)
            if y:
                enq(x, y - 1)
            if y + 1 < h:
                enq(x, y + 1)
        elif d <= 36:
            na = int(a * (d - 20) / 16.0)
            px[x, y] = (r, g, b, na) if na > 0 else (0, 0, 0, 0)

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if px[x, y][3] > 0:
                neighbors = sum(
                    1 for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dx or dy) and px[x + dx, y + dy][3] > 32
                )
                if neighbors <= 1:
                    px[x, y] = (0, 0, 0, 0)
    return im


def build_privilege_icons() -> dict[str, Image.Image]:
    icons: dict[str, Image.Image] = {}
    for dds_name, src_stem in PRIVILEGE_SOURCES:
        source = ROOT / f'gfx/interface/privileges/source/{src_stem}.png'
        src = Image.open(source).convert('RGBA')
        cleaned = strip_privilege_background(src)
        bbox = cleaned.getbbox()
        if not bbox:
            raise ValueError(f'No visible foreground in {source}')
        cropped = cleaned.crop(bbox)
        cw, ch = cropped.size
        # Vanilla 64px privilege textures typically center a roughly 30-35px motif.
        box_size = 30
        scale = min(box_size / cw, box_size / ch)
        nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
        obj = resize_clean(cropped, (nw, nh))
        sharp_rgb = obj.convert('RGB').filter(ImageFilter.UnsharpMask(radius=0.5, percent=30, threshold=3))
        obj = Image.merge('RGBA', (*sharp_rgb.split(), obj.getchannel('A')))
        # Offset the down-and-right shadow to keep the visible motif centered.
        ox = (64 - nw) // 2 - 1
        oy = (64 - nh) // 2 - 2

        canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        sh = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        sh_a = obj.getchannel('A').point(lambda a: int(a * 0.72))
        sh_l = Image.new('RGBA', (nw, nh), (0, 0, 0, 0))
        sh_l.putalpha(sh_a)
        sh.paste(sh_l, (ox + 1, min(64 - nh, oy + 2)))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=1.4))
        canvas = Image.alpha_composite(canvas, sh)

        fg = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        fg.paste(obj, (ox, oy))
        icons[dds_name] = resize_clean(Image.alpha_composite(canvas, fg), (64, 64))
    return icons


def build_mission_icons() -> dict[str, Image.Image]:
    icons: dict[str, Image.Image] = {}

    def make_painted_mission_icon(src_stem: str) -> Image.Image:
        src = Image.open(ROOT / f'gfx/interface/missions/source/{src_stem}.png').convert('RGB')
        w, h = src.size
        target_w = int(round(h * 59 / 63))
        if target_w <= w:
            # Preserve the reviewed crop of the original square masters.
            x0 = (w - target_w) // 2
            cropped = src.crop((x0, 0, x0 + target_w, h))
        else:
            target_h = min(h, int(round(w * 63 / 59)))
            y0 = (h - target_h) // 2
            cropped = src.crop((0, y0, w, y0 + target_h))
        small = cropped.resize((59, 63), Image.Resampling.LANCZOS)
        small = small.filter(ImageFilter.UnsharpMask(radius=0.6, percent=35, threshold=2))
        out = small.convert('RGBA')
        px = out.load()
        for y in range(63):
            for x in range(59):
                r, g, b, _ = px[x, y]
                px[x, y] = (r, g, b, 255)
        return out

    for sprite_name, src_stem in MISSION_ART:
        icons[f'{sprite_name}.dds'] = make_painted_mission_icon(src_stem)
    return icons


def mission_icons_gfx_text() -> str:
    lines = ['spriteTypes = {']
    for sprite_name, _ in LOCKED_BRANCH_MISSIONS + AUTHORED_MISSION_ART:
        lines.extend([
            '\tspriteType = {',
            f'\t\tname = "{sprite_name}"',
            f'\t\ttexturefile = "gfx/interface/missions/{sprite_name}.dds"',
            '\t}',
        ])
    lines.append('}')
    return '\n'.join(lines) + '\n'


def make_vanilla_plus_badge(size: int = 64) -> Image.Image:
    """Render a 3D bevelled emerald-green '+' sub-badge matching vanilla monthly_<power>.dds."""
    ss = 4
    s_px = size * ss
    y_g, x_g = np.mgrid[0:s_px, 0:s_px].astype(np.float32) / ss
    dv = np.maximum(np.abs(x_g - 43.5) - 2.2, np.abs(y_g - 41.9) - 8.8)
    dh = np.maximum(np.abs(x_g - 43.9) - 8.8, np.abs(y_g - 41.5) - 2.2)
    dist = np.minimum(dv, dh)

    out = np.zeros((s_px, s_px, 4), dtype=np.uint8)
    fill = dist <= 0.0
    border = (dist > 0.0) & (dist <= 1.05)

    edge_d = np.clip(-dist / 2.2, 0.0, 1.0)
    light = np.clip((-(x_g - 43.9) * 0.45 - (y_g - 41.7) * 0.75) / 9.0 + 0.55, 0.0, 1.0)
    top_left_bevel = (
        np.clip(1.0 - np.abs(edge_d - 0.35) * 2.2, 0.0, 1.0)
        * np.clip((-(x_g - 43.9) - (y_g - 41.7)) / 6.0 + 0.4, 0.0, 1.0)
    )
    shade = np.clip(0.18 + 0.55 * light * (0.45 + 0.55 * edge_d) + 0.38 * top_left_bevel, 0.0, 1.0)

    r = np.clip(18 + shade * 88, 0, 255).astype(np.uint8)
    g = np.clip(84 + shade * 148, 0, 255).astype(np.uint8)
    b = np.clip(16 + shade * 62, 0, 255).astype(np.uint8)

    out[fill, 0] = r[fill]
    out[fill, 1] = g[fill]
    out[fill, 2] = b[fill]
    out[fill, 3] = 255

    out[border, 0] = 10
    out[border, 1] = 18
    out[border, 2] = 8
    out[border, 3] = np.clip((1.05 - dist[border]) / 0.55 * 245, 0, 245).astype(np.uint8)

    im = Image.fromarray(out, 'RGBA')
    sh = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_a = im.getchannel('A').point(lambda a: int(a * 0.68))
    sh_l = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_l.putalpha(sh_a)
    sh.paste(sh_l, (int(1.0 * ss), int(1.3 * ss)))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=1.1 * ss))
    comp = Image.alpha_composite(sh, im)
    res = comp.convert('RGBa').resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    arr = np.array(res)
    arr[arr[:, :, 3] < 8] = 0
    arr[arr[:, :, 3] == 0] = 0
    return Image.fromarray(arr, 'RGBA')


def make_vanilla_arrow_badge(size: int = 64) -> Image.Image:
    """Render a 3D bevelled golden upward-arrow sub-badge matching vanilla <power>_gain_modifier.dds."""
    ss = 4
    s_px = size * ss
    pts = [
        (45.0 * ss, 32.0 * ss),
        (52.8 * ss, 40.2 * ss),
        (48.6 * ss, 40.2 * ss),
        (48.6 * ss, 50.2 * ss),
        (41.4 * ss, 50.2 * ss),
        (41.4 * ss, 40.2 * ss),
        (37.2 * ss, 40.2 * ss),
    ]
    mask_im = Image.new('L', (s_px, s_px), 0)
    ImageDraw.Draw(mask_im).polygon(pts, fill=255)
    mask = np.asarray(mask_im, dtype=np.float32) / 255.0
    dilated = np.asarray(mask_im.filter(ImageFilter.MaxFilter(int(2 * ss + 1))), dtype=np.float32) / 255.0
    bevel = np.asarray(mask_im.filter(ImageFilter.GaussianBlur(radius=1.2 * ss)), dtype=np.float32) / 255.0

    y_g, x_g = np.mgrid[0:s_px, 0:s_px].astype(np.float32) / ss
    dx = x_g - 45.0
    dy = y_g - 41.0
    left_facet = np.where(dx <= 0, np.clip(0.78 - dx * 0.04, 0.0, 1.0), np.clip(0.34 - dx * 0.04, 0.0, 1.0))
    vert_grad = np.clip(-dy * 0.035 + 0.55, 0.0, 1.0)
    ridge = np.exp(-((dx * 1.1) ** 2)) * 0.24
    shade = np.clip(0.14 + 0.58 * left_facet * vert_grad + 0.22 * bevel + ridge, 0.0, 1.0)

    r = np.clip(115 + shade * 140, 0, 255).astype(np.uint8)
    g = np.clip(74 + shade * 144, 0, 255).astype(np.uint8)
    b = np.clip(12 + shade * 78, 0, 255).astype(np.uint8)

    out = np.zeros((s_px, s_px, 4), dtype=np.uint8)
    border = (dilated > 0.15) & (mask < 0.5)
    out[border, 0] = 20
    out[border, 1] = 13
    out[border, 2] = 5
    out[border, 3] = 240

    fill = mask >= 0.5
    out[fill, 0] = r[fill]
    out[fill, 1] = g[fill]
    out[fill, 2] = b[fill]
    out[fill, 3] = 255

    im = Image.fromarray(out, 'RGBA')
    sh = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_a = im.getchannel('A').point(lambda a: int(a * 0.68))
    sh_l = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_l.putalpha(sh_a)
    sh.paste(sh_l, (int(1.0 * ss), int(1.3 * ss)))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=1.1 * ss))
    comp = Image.alpha_composite(sh, im)
    res = comp.convert('RGBa').resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    arr = np.array(res)
    arr[arr[:, :, 3] < 8] = 0
    arr[arr[:, :, 3] == 0] = 0
    return Image.fromarray(arr, 'RGBA')


_PLUS_BADGE: Image.Image | None = None
_ARROW_BADGE: Image.Image | None = None
_FACTION_INFLUENCE_BADGE: Image.Image | None = None


def make_vanilla_faction_influence_badge(size: int = 64) -> Image.Image:
    """Render a 3D bevelled steel-blue 4-directional compass ring matching vanilla <faction>_influence.dds."""
    ss = 4
    s_px = size * ss
    cx, cy = 40.0 * ss, 36.5 * ss
    y_g, x_g = np.mgrid[0:s_px, 0:s_px].astype(np.float32)
    dx = (x_g - cx) / ss
    dy = (y_g - cy) / ss
    r = np.hypot(dx, dy)

    ring_fill = (r >= 4.4) & (r <= 7.3)
    ring_border = ((r >= 3.4) & (r < 4.4)) | ((r > 7.3) & (r <= 8.3))

    tri_im = Image.new('L', (s_px, s_px), 0)
    td = ImageDraw.Draw(tri_im)
    td.polygon([(40.0 * ss, 23.3 * ss), (36.8 * ss, 27.9 * ss), (43.2 * ss, 27.9 * ss)], fill=255)
    td.polygon([(40.0 * ss, 49.7 * ss), (36.8 * ss, 45.1 * ss), (43.2 * ss, 45.1 * ss)], fill=255)
    td.polygon([(26.8 * ss, 36.5 * ss), (31.4 * ss, 33.3 * ss), (31.4 * ss, 39.7 * ss)], fill=255)
    td.polygon([(53.2 * ss, 36.5 * ss), (48.6 * ss, 33.3 * ss), (48.6 * ss, 39.7 * ss)], fill=255)
    tri_fill = np.asarray(tri_im, dtype=np.float32) / 255.0 > 0.5
    tri_dil = np.asarray(tri_im.filter(ImageFilter.MaxFilter(int(2 * ss + 1))), dtype=np.float32) / 255.0 > 0.15
    tri_border = tri_dil & (~tri_fill)

    fill_mask = ring_fill | tri_fill
    border_mask = (ring_border | tri_border) & (~fill_mask)

    fill_im = Image.fromarray((fill_mask.astype(np.uint8) * 255), 'L')
    bevel = np.asarray(fill_im.filter(ImageFilter.GaussianBlur(radius=0.9 * ss)), dtype=np.float32) / 255.0

    light = np.clip((-dx * 0.45 - dy * 0.65) / 11.5 + 0.58, 0.0, 1.0)
    ridge = np.clip(1.0 - np.abs(r - 5.85) / 1.6, 0.0, 1.0) * 0.30
    shade = np.clip(0.18 + 0.54 * light + 0.24 * bevel + ridge, 0.0, 1.0)

    red = np.clip(38 + shade * 88, 0, 255).astype(np.uint8)
    grn = np.clip(64 + shade * 108, 0, 255).astype(np.uint8)
    blu = np.clip(94 + shade * 124, 0, 255).astype(np.uint8)

    out = np.zeros((s_px, s_px, 4), dtype=np.uint8)
    out[border_mask, 0] = 12
    out[border_mask, 1] = 18
    out[border_mask, 2] = 26
    out[border_mask, 3] = 240

    out[fill_mask, 0] = red[fill_mask]
    out[fill_mask, 1] = grn[fill_mask]
    out[fill_mask, 2] = blu[fill_mask]
    out[fill_mask, 3] = 255

    im = Image.fromarray(out, 'RGBA')
    sh = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_a = im.getchannel('A').point(lambda a: int(a * 0.68))
    sh_l = Image.new('RGBA', (s_px, s_px), (0, 0, 0, 0))
    sh_l.putalpha(sh_a)
    sh.paste(sh_l, (int(1.0 * ss), int(1.3 * ss)))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=1.1 * ss))
    comp = Image.alpha_composite(sh, im)
    res = comp.convert('RGBa').resize((size, size), Image.Resampling.LANCZOS).convert('RGBA')
    arr = np.array(res)
    arr[arr[:, :, 3] < 8] = 0
    arr[arr[:, :, 3] == 0] = 0
    return Image.fromarray(arr, 'RGBA')


def make_faction_influence_icon(
    emblem_rgba: Image.Image,
    box_size: int = 42,
    center: tuple[int, int] = (27, 28),
) -> Image.Image:
    """Build a 64x64 <faction>_influence icon matching vanilla ideas_EU4 faction influence conventions."""
    global _FACTION_INFLUENCE_BADGE
    if _FACTION_INFLUENCE_BADGE is None:
        _FACTION_INFLUENCE_BADGE = make_vanilla_faction_influence_badge(64)
    base, _, _ = make_idea_modifier_triplet(emblem_rgba, box_size=box_size, center=center)
    return resize_clean(Image.alpha_composite(base, _FACTION_INFLUENCE_BADGE), (64, 64))


def rep_knyazi_emblem() -> Image.Image:
    """Composite the princely shield & charter with the Knyazi crown & sceptre for Representative Monarchy."""
    shield = atlas_emblem(0, 1).copy()
    crown = atlas_emblem(1, 2).copy()
    w, h = max(shield.width, crown.width), max(shield.height, crown.height)
    comp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sw, sh = int(w * 0.78), int(h * 0.78)
    shield_small = resize_clean(shield, (sw, sh))
    comp.paste(shield_small, ((w - sw) // 2 - 12, (h - sh) // 2 + 12))

    cw, ch = int(w * 0.84), int(h * 0.84)
    crown_small = resize_clean(crown, (cw, ch))
    ox, oy = (w - cw) // 2 + 10, (h - ch) // 2 - 8
    sh_l = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh_a = crown_small.getchannel('A').point(lambda a: int(a * 0.82))
    sh_c = Image.new('RGBA', (cw, ch), (10, 6, 12, 0))
    sh_c.putalpha(sh_a)
    sh_l.paste(sh_c, (ox + 5, oy + 7))
    sh_l = sh_l.filter(ImageFilter.GaussianBlur(radius=5.0))
    comp = Image.alpha_composite(comp, sh_l)
    fg = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    fg.paste(crown_small, (ox, oy))
    return Image.alpha_composite(comp, fg)


def rep_boyary_emblem() -> Image.Image:
    """Composite the Boyar council scroll with the treasury scales & seal for Representative Monarchy."""
    council = source_emblem('snem').copy()
    scales = atlas_emblem(2, 2).copy()
    w, h = scales.size
    cw, ch = int(w * 0.76), int(h * 0.76)
    council_small = resize_clean(council, (cw, ch))
    comp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    comp.paste(council_small, ((w - cw) // 2 - 14, (h - ch) // 2 - 10))

    sw, sh = int(w * 0.86), int(h * 0.86)
    scales_small = resize_clean(scales, (sw, sh))
    ox, oy = (w - sw) // 2 + 10, (h - sh) // 2 + 10
    sh_l = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh_a = scales_small.getchannel('A').point(lambda a: int(a * 0.82))
    sh_c = Image.new('RGBA', (sw, sh), (6, 10, 16, 0))
    sh_c.putalpha(sh_a)
    sh_l.paste(sh_c, (ox + 5, oy + 7))
    sh_l = sh_l.filter(ImageFilter.GaussianBlur(radius=5.0))
    comp = Image.alpha_composite(comp, sh_l)
    fg = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    fg.paste(scales_small, (ox, oy))
    return Image.alpha_composite(comp, fg)


def build_faction_influence_icons() -> dict[str, Image.Image]:
    return {
        'kru_knyazi_influence.dds': make_faction_influence_icon(atlas_emblem(1, 2)),
        'kru_boyary_influence.dds': make_faction_influence_icon(atlas_emblem(2, 2)),
        'kru_starshyna_influence.dds': make_faction_influence_icon(atlas_emblem(3, 2)),
        'rep_boyary_influence.dds': make_faction_influence_icon(rep_boyary_emblem()),
        'rep_knyazi_influence.dds': make_faction_influence_icon(rep_knyazi_emblem()),
    }


def het_authority_emblem() -> Image.Image:
    """Composite the painted crossed gold Hetman bulava & silver Starshyna mace over a wax-sealed charter scroll."""
    scroll = source_emblem('charter').copy()
    disaster = Image.open(ROOT / 'gfx/interface/disasters/source/hetman_succession_crisis.png').convert('RGBA')
    maces = remove_atlas_background(disaster.crop((96, 96, 628, 628)), pad_ratio=0.06)
    w, h = maces.size
    sw, sh = int(w * 0.72), int(h * 0.72)
    scroll_small = resize_clean(scroll, (sw, sh))

    comp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    comp.paste(scroll_small, ((w - sw) // 2, (h - sh) // 2 + int(h * 0.06)))

    sh_l = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh_a = maces.getchannel('A').point(lambda a: int(a * 0.84))
    sh_c = Image.new('RGBA', (w, h), (10, 6, 4, 0))
    sh_c.putalpha(sh_a)
    sh_l.paste(sh_c, (5, 7))
    sh_l = sh_l.filter(ImageFilter.GaussianBlur(radius=6.0))
    comp = Image.alpha_composite(comp, sh_l)
    return Image.alpha_composite(comp, maces)


def zaz_cossack_zeal_emblem() -> Image.Image:
    """Composite crossed swords and crimson shield with the radiant 3D golden Orthodox three-bar cross."""
    banner = Image.open(ROOT / 'assets/church_banners/ro_banner_mission.png').convert('RGBA')
    crop = banner.crop((370, 240, 885, 885))
    arr = np.asarray(crop, dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    goldness = (g - b * 0.6) + (r - b) * 0.4 - np.maximum(0, r - g * 1.45) * 1.8
    alpha = np.clip((goldness - 28.0) / 38.0 * 255.0, 0, 255).astype(np.uint8)
    cross_rgba = np.zeros_like(arr, dtype=np.uint8)
    cross_rgba[:, :, 0] = np.clip(r * 1.06, 0, 255).astype(np.uint8)
    cross_rgba[:, :, 1] = np.clip(g * 1.04, 0, 255).astype(np.uint8)
    cross_rgba[:, :, 2] = np.clip(b * 0.88, 0, 255).astype(np.uint8)
    cross_rgba[:, :, 3] = alpha
    cross_im = Image.fromarray(cross_rgba, 'RGBA')
    bbox = cross_im.getbbox()
    if bbox:
        cross_im = cross_im.crop(bbox)

    shield_swords = atlas_emblem(1, 1).copy()
    sw, sh = shield_swords.size
    cw = int(sw * 0.50)
    ch = int(cw * cross_im.height / cross_im.width)
    c_small = resize_clean(cross_im, (cw, ch))
    ox = (sw - cw) // 2
    oy = (sh - ch) // 2 - int(sh * 0.02)

    sh_l = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    sh_a = c_small.getchannel('A').point(lambda a: int(a * 0.85))
    sh_c = Image.new('RGBA', (cw, ch), (18, 6, 4, 0))
    sh_c.putalpha(sh_a)
    sh_l.paste(sh_c, (ox + 3, oy + 4))
    sh_l = sh_l.filter(ImageFilter.GaussianBlur(radius=4.0))
    out = Image.alpha_composite(shield_swords, sh_l)
    fg = Image.new('RGBA', (sw, sh), (0, 0, 0, 0))
    fg.paste(c_small, (ox, oy))
    return Image.alpha_composite(out, fg)


def make_idea_modifier_triplet(
    emblem_rgba: Image.Image,
    box_size: int = 44,
    center: tuple[int, int] = (29, 30),
) -> tuple[Image.Image, Image.Image, Image.Image]:
    """Build (<power>, monthly_<power>, <power>_gain_modifier) 64x64 icons per vanilla ideas_EU4 rules."""
    global _PLUS_BADGE, _ARROW_BADGE
    if _PLUS_BADGE is None:
        _PLUS_BADGE = make_vanilla_plus_badge(64)
    if _ARROW_BADGE is None:
        _ARROW_BADGE = make_vanilla_arrow_badge(64)

    bbox = emblem_rgba.getbbox()
    cropped = emblem_rgba.crop(bbox) if bbox else emblem_rgba
    cw, ch = cropped.size
    scale = min(box_size / cw, box_size / ch)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    emb = resize_clean(cropped, (nw, nh))
    ox = center[0] - nw // 2
    oy = center[1] - nh // 2

    canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    sh = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    sh_a = emb.getchannel('A').point(lambda a: int(a * 0.72))
    sh_l = Image.new('RGBA', (nw, nh), (0, 0, 0, 0))
    sh_l.putalpha(sh_a)
    sh.paste(sh_l, (ox + 1, oy + 2))
    sh = sh.filter(ImageFilter.GaussianBlur(radius=1.4))
    canvas = Image.alpha_composite(canvas, sh)

    fg = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    fg.paste(emb, (ox, oy))
    base = resize_clean(Image.alpha_composite(canvas, fg), (64, 64))
    monthly = resize_clean(Image.alpha_composite(base, _PLUS_BADGE), (64, 64))
    gain = resize_clean(Image.alpha_composite(base, _ARROW_BADGE), (64, 64))
    return base, monthly, gain


def build_magnate_modifier_icons() -> dict[str, Image.Image]:
    vroot = vanilla_root()
    cap = atlas_emblem(1, 2)
    bbox = cap.getbbox()
    cropped = cap.crop(bbox) if bbox else cap
    cw, ch = cropped.size
    scale = min(42 / cw, 42 / ch)
    nw, nh = max(1, int(round(cw * scale))), max(1, int(round(ch * scale)))
    cap_small = resize_clean(cropped, (nw, nh))

    donors: dict[str, np.ndarray] = {}
    for target_name, vanilla_donor in MAGNATE_MODIFIER_FILES:
        if vroot and (vroot / 'gfx/interface/ideas_EU4' / vanilla_donor).is_file():
            im = Image.open(vroot / 'gfx/interface/ideas_EU4' / vanilla_donor).convert('RGBA')
        else:
            im = Image.open(ROOT / 'gfx/interface/ideas_EU4' / target_name).convert('RGBA')
        donors[target_name] = np.asarray(resize_clean(im, (64, 64)), dtype=np.int16)

    # Mask out pixels where the base emblem (steel gauntlet or princely cap) is identical across the family
    inf_a = donors['magnates_influence_modifier.dds']
    loy_a = donors['magnates_loyalty_modifier.dds']
    prv_a = donors['magnates_privilege_slots.dds']
    shared_bg_mask = (
        (np.abs(inf_a - loy_a).max(axis=2) <= 8)
        & (np.abs(inf_a - prv_a).max(axis=2) <= 8)
        & (np.abs(loy_a - prv_a).max(axis=2) <= 8)
    )

    icons: dict[str, Image.Image] = {}
    for target_name, _ in MAGNATE_MODIFIER_FILES:
        canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        sh_c = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        sh_ca = cap_small.getchannel('A').point(lambda a: int(a * 0.72))
        sh_cl = Image.new('RGBA', cap_small.size, (0, 0, 0, 0))
        sh_cl.putalpha(sh_ca)
        sh_c.paste(sh_cl, (9, 11))
        sh_c = sh_c.filter(ImageFilter.GaussianBlur(radius=1.4))
        canvas = Image.alpha_composite(canvas, sh_c)

        fg_c = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        fg_c.paste(cap_small, (8, 9))
        canvas = Image.alpha_composite(canvas, fg_c)

        clean_arr = donors[target_name].copy()
        clean_arr[shared_bg_mask] = 0
        badge_crop = Image.fromarray(np.clip(clean_arr[28:58, 32:60], 0, 255).astype(np.uint8), 'RGBA')
        sh = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        sh_a = badge_crop.getchannel('A').point(lambda a: int(a * 0.75))
        sh_l = Image.new('RGBA', badge_crop.size, (0, 0, 0, 0))
        sh_l.putalpha(sh_a)
        sh.paste(sh_l, (32, 29))
        sh = sh.filter(ImageFilter.GaussianBlur(radius=1.2))
        canvas = Image.alpha_composite(canvas, sh)

        fg = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        fg.paste(badge_crop, (32, 28))
        canvas = Image.alpha_composite(canvas, fg)
        icons[target_name] = resize_clean(canvas, (64, 64))
    return icons


def build_vilnius_palace() -> Image.Image:
    """Export the reviewed master instead of repainting Ambras Castle."""
    from build_great_project_art import render
    return render("vilnius_palace")


def write_privilege_icons() -> None:
    for name, img in build_privilege_icons().items():
        path = ROOT / 'gfx/interface/privileges' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format='DDS')


def check_privilege_icons(problems: list[str]) -> None:
    threshold = [255 if value > CHECK_TOLERANCE else 0 for value in range(256)]
    for name, want in build_privilege_icons().items():
        path = ROOT / 'gfx/interface/privileges' / name
        if not path.is_file():
            problems.append(f'Missing privilege icon: {path}')
            continue
        have = Image.open(path).convert('RGBA')
        if have.size != (64, 64):
            problems.append(f'{name}: expected 64x64, got {have.size}')
            continue
        diff = ImageChops.difference(have, want)
        if any(diff.getchannel(band).point(threshold).getbbox() for band in 'RGBA'):
            problems.append(f'{name}: differs from generator')


def write_mission_icons() -> None:
    for name, img in build_mission_icons().items():
        path = ROOT / 'gfx/interface/missions' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format='DDS')
    (ROOT / 'interface/rip_mission_icons.gfx').write_text(
        mission_icons_gfx_text(), encoding='utf-8', newline='\n')


def check_mission_icons(problems: list[str]) -> None:
    from clausewitz_testlib import keyed_blocks

    missing_sources = [stem for _, stem in MISSION_ART
                       if not (ROOT / f'gfx/interface/missions/source/{stem}.png').is_file()]
    if missing_sources:
        problems.extend(f'Missing mission source: {stem}.png' for stem in missing_sources)
        return

    for name, want in build_mission_icons().items():
        path = ROOT / 'gfx/interface/missions' / name
        if not path.is_file():
            problems.append(f'Missing mission icon: {path}')
            continue
        with Image.open(path) as image:
            have = image.convert('RGBA')
        if have.size != (59, 63):
            problems.append(f'{name}: expected 59x63, got {have.size}')
            continue
        if have.getchannel('A').getextrema() != (255, 255):
            problems.append(f'{name}: mission artwork must be opaque')
        # RGBA getbbox() alone can miss RGB changes when alpha is unchanged.
        diff = ImageChops.difference(have, want).getextrema()
        if max(channel[1] for channel in diff) > CHECK_TOLERANCE:
            problems.append(f'{name}: differs from source master/generator')

    registrations: dict[str, list[tuple[Path, str]]] = {sprite: [] for sprite, _ in MISSION_ART}
    for path in (ROOT / 'interface').glob('*.gfx'):
        for _, block in keyed_blocks(path.read_text(encoding='utf-8-sig'), 'spriteType'):
            name_match = re.search(r'\bname\s*=\s*"([^"]+)"', block)
            if name_match and name_match[1] in registrations:
                texture_match = re.search(r'\btexturefile\s*=\s*"([^"]+)"', block)
                registrations[name_match[1]].append((path, texture_match[1] if texture_match else ''))
    mission_text = '\n'.join(path.read_text(encoding='utf-8-sig')
                             for path in (ROOT / 'missions').glob('*.txt'))
    for sprite, entries in registrations.items():
        if len(entries) != 1:
            problems.append(f'{sprite}: expected one sprite registration, got {len(entries)}')
        elif entries[0][1] != f'gfx/interface/missions/{sprite}.dds':
            problems.append(f'{sprite}: sprite texture does not point to its generated DDS')
        if not re.search(rf'(?m)^\s*icon\s*=\s*{re.escape(sprite)}\s*(?:#.*)?$', mission_text):
            problems.append(f'{sprite}: no mission uses this artwork')
    gfx_path = ROOT / 'interface/rip_mission_icons.gfx'
    if not gfx_path.is_file() or gfx_path.read_text(encoding='utf-8-sig') != mission_icons_gfx_text():
        problems.append('interface/rip_mission_icons.gfx differs from generator')


def write_all() -> int:
    import build_reform_icons as R
    game = vanilla_root()
    if game is not None:
        header = (game / R.HEADER_DONOR).read_bytes()[:R.HEADER]
        for rel_path, px in R.build_all(game).items():
            path = ROOT / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(R.dds_bytes(px, header))
    else:
        for name, img in build_reform_icons().items():
            path = ROOT / 'gfx/interface/government_reform_icons' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            img.save(path, format='DDS')

    write_privilege_icons()

    write_mission_icons()

    for name, img in build_magnate_modifier_icons().items():
        path = ROOT / 'gfx/interface/ideas_EU4' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format='DDS')

    for name, img in build_faction_influence_icons().items():
        path = ROOT / 'gfx/interface/ideas_EU4' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format='DDS')

    vp_path = ROOT / 'gfx/interface/great_projects/great_project_vilnius_palace.dds'
    build_vilnius_palace().save(vp_path, format='DDS')

    for obsolete in OBSOLETE_RELIGION_ICONS:
        p = ROOT / obsolete
        if p.exists():
            p.unlink()

    print(f'CORE RUTHENIA ICONS PASS: wrote reform/privilege icons, {len(MISSION_FILES)} mission icons, modifier icons and Vilnius Palace.')
    return 0


def check_all() -> int:
    problems: list[str] = []
    for name, want in build_reform_icons().items():
        path = ROOT / 'gfx/interface/government_reform_icons' / name
        if not path.is_file():
            problems.append(f'Missing reform icon: {path}')
            continue
        have = Image.open(path).convert('RGBA')
        if have.size != (57, 57):
            problems.append(f'{name}: expected 57x57, got {have.size}')
        diff = ImageChops.difference(have, want).getextrema()
        if max(ch[1] for ch in diff) > CHECK_TOLERANCE:
            problems.append(f'{name}: differs from generator')

    check_privilege_icons(problems)

    check_mission_icons(problems)

    for name, want in build_magnate_modifier_icons().items():
        path = ROOT / 'gfx/interface/ideas_EU4' / name
        if not path.is_file():
            problems.append(f'Missing magnate modifier icon: {path}')
            continue
        have = Image.open(path).convert('RGBA')
        if have.size != (64, 64):
            problems.append(f'{name}: expected 64x64, got {have.size}')
        diff = ImageChops.difference(have, want).getextrema()
        if max(ch[1] for ch in diff) > CHECK_TOLERANCE:
            problems.append(f'{name}: differs from generator')

    for name, want in build_faction_influence_icons().items():
        path = ROOT / 'gfx/interface/ideas_EU4' / name
        if not path.is_file():
            problems.append(f'Missing faction influence icon: {path}')
            continue
        have = Image.open(path).convert('RGBA')
        if have.size != (64, 64):
            problems.append(f'{name}: expected 64x64, got {have.size}')
        diff = ImageChops.difference(have, want).getextrema()
        if max(ch[1] for ch in diff) > CHECK_TOLERANCE:
            problems.append(f'{name}: differs from generator')

    vp_path = ROOT / 'gfx/interface/great_projects/great_project_vilnius_palace.dds'
    want_vp = build_vilnius_palace()
    if not vp_path.is_file():
        problems.append(f'Missing monument image: {vp_path}')
    else:
        have_vp = Image.open(vp_path).convert('RGBA')
        if have_vp.size != (300, 150):
            problems.append(f'great_project_vilnius_palace.dds: expected 300x150, got {have_vp.size}')
        diff = ImageChops.difference(have_vp, want_vp).getextrema()
        if max(ch[1] for ch in diff) > CHECK_TOLERANCE:
            problems.append('great_project_vilnius_palace.dds: differs from generator')

    for obsolete in OBSOLETE_RELIGION_ICONS:
        if (ROOT / obsolete).exists():
            problems.append(f'Obsolete unreferenced religion icon still present: {obsolete}')

    if problems:
        for p in problems:
            print('FAIL:', p)
        return 1
    print(f'CORE RUTHENIA ICONS PASS: reform/privilege icons, {len(MISSION_FILES)} mission icons, modifier icons and Vilnius Palace match the generator.')
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument('--privileges-only', action='store_true',
                       help='write or check only the privilege icons')
    scope.add_argument('--missions-only', action='store_true',
                       help='write or check only mission DDS icons and their sprite registrations')
    args = parser.parse_args(argv)
    if args.missions_only:
        if args.check:
            problems: list[str] = []
            check_mission_icons(problems)
            if problems:
                for problem in problems:
                    print('FAIL:', problem)
                return 1
            print(f'MISSION ICONS PASS: {len(MISSION_FILES)} icons match their masters and have live registrations/usages.')
        else:
            write_mission_icons()
            print(f'MISSION ICONS PASS: wrote {len(MISSION_FILES)} icons and sprite registrations.')
        return 0
    if args.privileges_only:
        if args.check:
            problems: list[str] = []
            check_privilege_icons(problems)
            if problems:
                for problem in problems:
                    print('FAIL:', problem)
                return 1
            print(f'PRIVILEGE ICONS PASS: {len(PRIVILEGE_FILES)} icons match the generator.')
        else:
            write_privilege_icons()
            print(f'PRIVILEGE ICONS PASS: wrote {len(PRIVILEGE_FILES)} privilege icons.')
        return 0
    return check_all() if args.check else write_all()


if __name__ == '__main__':
    raise SystemExit(main())
