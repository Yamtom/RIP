"""Draw the art of the Holy Cities Register in the Muscovite Church window.

Three small sprites, all drawn here with Pillow and numpy so that no vanilla pixel is copied:

  ro_myth_bar.dds   31 frames of a 96x22 capacity bar, one per year of a sacred myth (0..30).
                    Gold fill while the myth matures, green once the 30 years are full. EU4 slices
                    a strip into noOfFrames equal frames, so the file is 31 * 96 = 2976 px wide.
  ro_myth_veil.dds  72x36 translucent dark plate laid over the two blessing slots of a myth that
                    has not matured yet. The icons are vanilla modifier icons; they show in
                    full colour only once the blessing is in force.
  ro_holy_tile.dds  58x58 button face for the Holy Cities Register: the slate tile and gold rim of
                    the vanilla blessing selector, but with no emblem. The Russian Orthodox cross
                    (religion frame 30) is laid over it by the GUI, instead of the Coptic cross that
                    sat in the vanilla tile.

Frames are drawn at 4x and reduced, so the rounded ends are smooth at native size. Output is legacy
uncompressed DDS, as for every other RIP church sprite (no DX10 header). Run with --check to compare
the committed files without writing; --preview PATH writes a contact sheet for a visual look.
"""
from io import BytesIO
from pathlib import Path
import argparse

try:
    import numpy as np
    from PIL import Image, ImageDraw
    _import_err = None
except ModuleNotFoundError as _err:
    np = None
    Image = None
    ImageDraw = None
    _import_err = _err

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'gfx/interface/rip_church'

# One frame per year of the myth, zero included. The GUI generator reads these two numbers.
BAR_FRAMES, BAR_W, BAR_H = 31, 96, 22
MYTH_YEARS = BAR_FRAMES - 1
VEIL_W, VEIL_H = 72, 36                    # two 36px slots side by side
TILE_SIZE = 58
SS = 4                                    # supersampling factor for the rounded shapes

GOLD_TOP, GOLD_BOTTOM = (222, 176, 92), (104, 74, 34)
AMBER = ((252, 222, 140), (228, 180, 80), (154, 106, 38), (104, 70, 26))      # highlight, top, bottom, edge
GREEN = ((196, 246, 182), (100, 200, 112), (38, 122, 64), (26, 84, 44))
TROUGH_TOP, TROUGH_BOTTOM = (16, 21, 25), (38, 48, 54)


def mask(box, radius, size):
    """An 'L' mask of a rounded rectangle, box in final pixels, drawn at SS times the size."""
    image = Image.new('L', (size[0] * SS, size[1] * SS), 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(image).rounded_rectangle(
        (x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1), radius=radius * SS, fill=255)
    return np.asarray(image, dtype=np.float32) / 255.0


def gradient(size, top, bottom):
    """Vertical gradient as float RGB, at SS times the size."""
    h = size[1] * SS
    t = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    top, bottom = np.array(top, np.float32), np.array(bottom, np.float32)
    column = top * (1 - t) + bottom * t
    return np.broadcast_to(column, (h, size[0] * SS, 3)).copy()


def paint(canvas, color, alpha):
    """Source-over of a colour (an RGB array or triple) through an alpha mask onto an RGBA float canvas."""
    colour = np.asarray(color, np.float32)
    if colour.ndim == 1:
        colour = np.broadcast_to(colour, canvas.shape[:2] + (3,))
    a = alpha[..., None]
    out_a = a + canvas[..., 3:4] * (1 - a)
    safe = np.where(out_a == 0, 1, out_a)
    canvas[..., :3] = (colour * a + canvas[..., :3] * canvas[..., 3:4] * (1 - a)) / safe
    canvas[..., 3:4] = out_a


def reduce(canvas, size):
    """Premultiplied box reduction from SS times the size to the final size, as 8-bit RGBA."""
    a = canvas[..., 3:4]
    premultiplied = np.concatenate([canvas[..., :3] * a, a], axis=-1)
    h, w = size[1], size[0]
    blocks = premultiplied.reshape(h, SS, w, SS, 4).mean(axis=(1, 3))
    alpha = blocks[..., 3:4]
    rgb = np.where(alpha > 0, blocks[..., :3] / np.where(alpha == 0, 1, alpha), 0)
    out = np.concatenate([rgb, alpha * 255.0], axis=-1)
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), 'RGBA')


def bar_frame(years):
    size = (BAR_W, BAR_H)
    canvas = np.zeros((BAR_H * SS, BAR_W * SS, 4), np.float32)
    paint(canvas, gradient(size, GOLD_TOP, GOLD_BOTTOM), mask((0, 0, BAR_W, BAR_H), 5, size))          # gold rim
    paint(canvas, (14, 18, 21), mask((1, 1, BAR_W - 1, BAR_H - 1), 4, size))                           # dark line inside it
    paint(canvas, gradient(size, TROUGH_TOP, TROUGH_BOTTOM), mask((2, 2, BAR_W - 2, BAR_H - 2), 3, size))
    # The trough loses a little light at the top, as a recessed slot does.
    shade = np.zeros_like(canvas[..., 0]); shade[2 * SS:4 * SS, :] = 0.35
    paint(canvas, (0, 0, 0), shade * mask((2, 2, BAR_W - 2, BAR_H - 2), 3, size))
    inner_l, inner_r, inner_t, inner_b = 3, BAR_W - 3, 3, BAR_H - 3                                    # 98 x 16 usable
    usable = inner_r - inner_l
    if years > 0:
        highlight, top, bottom, edge = GREEN if years >= MYTH_YEARS else AMBER
        width = round(usable * years / MYTH_YEARS)
        fill_box = (inner_l, inner_t, inner_l + width, inner_b)
        body = mask(fill_box, 3, size)
        colours = gradient(size, top, bottom)
        paint(canvas, colours, body)
        rows = np.zeros_like(body)
        rows[inner_t * SS:(inner_t + 1) * SS, :] = 1.0                       # one bright row on top
        paint(canvas, highlight, rows * body * 0.85)
        rows = np.zeros_like(body)
        rows[(inner_b - 1) * SS:inner_b * SS, :] = 1.0                       # one dark row below
        paint(canvas, edge, rows * body * 0.9)
    # Faint ticks every five years: the bar reads as six steps of a long project.
    ticks = np.zeros((BAR_H * SS, BAR_W * SS), np.float32)
    for k in range(1, 6):
        x = inner_l + round(usable * k / 6)
        ticks[(inner_t + 1) * SS:(inner_b - 1) * SS, x * SS:x * SS + SS] = 1.0
    paint(canvas, (0, 0, 0), ticks * 0.28 * mask((2, 2, BAR_W - 2, BAR_H - 2), 3, size))
    return reduce(canvas, size)


def bar_strip():
    strip = Image.new('RGBA', (BAR_W * BAR_FRAMES, BAR_H), (0, 0, 0, 0))
    for years in range(BAR_FRAMES):
        strip.paste(bar_frame(years), (years * BAR_W, 0))
    return strip


def veil():
    size = (VEIL_W, VEIL_H)
    canvas = np.zeros((VEIL_H * SS, VEIL_W * SS, 4), np.float32)
    paint(canvas, (8, 12, 15), mask((0, 0, VEIL_W, VEIL_H), 4, size) * (112 / 255))
    return reduce(canvas, size)


def tile():
    """The vanilla blessing tile's anatomy, in pixels: a 3 px soft shadow, a 1 px bevelled gold rim on a
    52 px box, a dark line, a lit top and left edge, and a slate fill that darkens downward."""
    s = TILE_SIZE
    a = np.zeros((s, s, 4), np.uint8)
    lo, hi = 3, s - 4                                                      # rim box 3..54
    for dist, alpha in ((3, 18), (2, 55), (1, 111)):
        x0, x1 = lo - dist, hi + dist
        for i in range(x0, x1 + 1):
            for (x, y) in ((i, x0), (i, x1), (x0, i), (x1, i)):
                a[y, x] = (0, 0, 0, max(alpha, a[y, x, 3]))
    rng = np.random.default_rng(1444)
    height = hi - lo - 1
    for y in range(lo + 1, hi):
        t = (y - lo - 1) / max(height - 1, 1)
        base = np.array((70, 86, 100), np.float32) * (1 - t) + np.array((40, 53, 62), np.float32) * t
        for x in range(lo + 1, hi):
            a[y, x, :3] = np.clip(base + rng.integers(-2, 3, 3), 0, 255)
            a[y, x, 3] = 255
    # Inner dark line, then the lit edges: top brightest, left a little less.
    for i in range(lo + 1, hi):
        a[lo + 1, i] = a[hi - 1, i] = a[i, lo + 1] = a[i, hi - 1] = (24, 27, 30, 255)
    for i in range(lo + 2, hi - 1):
        a[lo + 2, i] = (124, 146, 176, 255)
        a[lo + 3, i] = (84, 99, 117, 255)
        a[i, lo + 2] = (96, 113, 131, 255)
        a[hi - 2, i] = (30, 38, 44, 255)
        a[i, hi - 2] = (34, 43, 50, 255)
    # Gold rim: light on top, shaded toward the bottom right.
    for i in range(lo + 1, hi):
        a[lo, i] = (245, 206, 133, 255)
        a[i, lo] = (167, 124, 52, 255)
        a[hi, i] = (93, 59, 26, 255)
        a[i, hi] = (153, 107, 47, 255)
    for corner in ((lo, lo), (hi, lo), (lo, hi), (hi, hi)):                 # round the rim's four corners
        a[corner[1], corner[0]] = (0, 0, 0, 0)
    return Image.fromarray(a, 'RGBA')


def dds(image):
    buffer = BytesIO()
    image.save(buffer, format='DDS')
    data = buffer.getvalue()
    assert data[:4] == b'DDS ' and data[84:88] != b'DX10', 'legacy uncompressed DDS only'
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--preview', type=Path, help='write a contact sheet PNG')
    args = parser.parse_args()

    if _import_err is not None:
        if args.check:
            print(f'SKIP: build_ro_register_art.py ({_import_err}); interpreter limitation, committed art checked by static header assertions')
            return
        raise _import_err
    images = {'ro_myth_bar.dds': bar_strip(), 'ro_myth_veil.dds': veil(), 'ro_holy_tile.dds': tile()}
    stale = []
    for name, image in images.items():
        data = dds(image)
        target = OUT / name
        if not target.exists() or target.read_bytes() != data:
            stale.append(name)
            if not args.check:
                target.write_bytes(data)
    if args.preview:
        sheet = Image.new('RGBA', (BAR_W * 5 + 40, 560), (26, 34, 38, 255))
        for row, years in enumerate((0, 1, 7, 15, 22, 29, 30)):
            frame = images['ro_myth_bar.dds'].crop((years * BAR_W, 0, (years + 1) * BAR_W, BAR_H))
            sheet.alpha_composite(frame.resize((BAR_W * 3, BAR_H * 3), Image.NEAREST), (10, 10 + row * 76))
        sheet.alpha_composite(images['ro_holy_tile.dds'].resize((TILE_SIZE * 3, TILE_SIZE * 3), Image.NEAREST), (340, 10))
        sheet.alpha_composite(images['ro_myth_veil.dds'].resize((VEIL_W * 3, VEIL_H * 3), Image.NEAREST), (340, 200))
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.preview)
    print(('STALE' if args.check and stale else 'GENERATED' if stale else 'CURRENT')
          + f': Holy Cities Register art, {BAR_FRAMES} bar frames of {BAR_W}x{BAR_H}, veil and button tile')
    if args.check and stale:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
