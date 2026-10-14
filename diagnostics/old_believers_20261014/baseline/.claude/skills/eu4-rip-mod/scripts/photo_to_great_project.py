"""Turn a photograph into an EU4 great-project image.

    python photo_to_great_project.py <photo> <out.dds> [--crop L,T,R,B] [--preview p.png]

EU4 ships great-project art as 300x150 uncompressed 32-bit DDS, painted rather
than photographic. Measured over six vanilla monuments, that art sits at mean
saturation 80/255, mean value 125/255, luminance spread 62 and edge energy 28.
A photo comes in far busier and more saturated, so the pipeline is:

  crop to 2:1  ->  median filter to break detail into paint-like patches  ->
  grade saturation, brightness and contrast onto the vanilla means  ->
  unsharp to give the flattened image painted definition  ->  warm the
  highlights and cool the shadows a touch  ->  vignette  ->  300x150.
"""
import io, os, sys

from PIL import Image, ImageEnhance, ImageFilter, ImageStat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dds

TARGET_W, TARGET_H = 300, 150
VANILLA_SAT, VANILLA_VAL, VANILLA_CONTRAST = 79.9, 125.2, 62.0


def crop_2to1(im, box=None):
    if box:
        return im.crop(box)
    w, h = im.size
    want_h = w // 2
    if want_h <= h:                      # portrait or tall: take the upper-middle band
        top = int((h - want_h) * 0.34)   # the subject usually sits above centre
        return im.crop((0, top, w, top + want_h))
    want_w = h * 2
    left = (w - want_w) // 2
    return im.crop((left, 0, left + want_w, h))


def measure(im):
    hsv = im.convert("HSV")
    st = ImageStat.Stat(hsv)
    return st.mean[1], st.mean[2], ImageStat.Stat(im.convert("L")).stddev[0]


def grade(im):
    """Bring saturation, brightness and contrast onto the vanilla means."""
    for _ in range(6):                   # iterate: the three controls interact
        sat, val, con = measure(im)
        im = ImageEnhance.Color(im).enhance(1 + 0.8 * (VANILLA_SAT / max(sat, 1) - 1))
        im = ImageEnhance.Brightness(im).enhance(1 + 0.8 * (VANILLA_VAL / max(val, 1) - 1))
        im = ImageEnhance.Contrast(im).enhance(1 + 0.8 * (VANILLA_CONTRAST / max(con, 1) - 1))
    return im


def painterly(im):
    big = im.resize((im.width, im.height), Image.LANCZOS)
    big = big.filter(ImageFilter.MedianFilter(size=5))     # flatten photo grain
    big = big.filter(ImageFilter.MedianFilter(size=3))
    big = big.filter(ImageFilter.GaussianBlur(radius=0.8))
    return big


def split_tone(im, warm=6, cool=6):
    """Warm the light, cool the dark - the habit of the vanilla paintings."""
    r, g, b = im.split()
    lum = im.convert("L")
    out_r, out_g, out_b = r.load(), g.load(), b.load()
    lm = lum.load()
    for y in range(im.height):
        for x in range(im.width):
            t = (lm[x, y] - 128) / 128.0
            out_r[x, y] = max(0, min(255, int(out_r[x, y] + warm * t)))
            out_b[x, y] = max(0, min(255, int(out_b[x, y] - cool * t)))
    return Image.merge("RGB", (r, g, b))


def vignette(im, strength=0.22):
    w, h = im.size
    px = im.load()
    cx, cy = w / 2.0, h / 2.0
    maxd = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(h):
        for x in range(w):
            d = (((x - cx) ** 2 + (y - cy) ** 2) ** 0.5) / maxd
            f = 1.0 - strength * (d ** 2.2)
            r, g, b = px[x, y]
            px[x, y] = (int(r * f), int(g * f), int(b * f))
    return im


DONOR = (r"D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV"
         r"/gfx/interface/great_projects/great_project_bran_castle.dds")

# Vanilla bakes two things into every monument texture: a 5px gilt border, and
# a translucent name plaque at the top left. Measured over five monuments, the
# plaque multiplies what is under it by roughly these factors.
FRAME = 5
PLAQUE = (8, 8, 88, 29)
PLAQUE_MUL = (0.467, 0.525, 0.568)


def add_frame_and_plaque(im):
    x0, y0, x1, y1 = PLAQUE
    px = im.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            # feather one pixel so the panel edge is not a hard cut
            fx = 1.0 if x0 + 1 < x < x1 - 2 else 0.6
            fy = 1.0 if y0 + 1 < y < y1 - 2 else 0.6
            f = fx * fy
            r, g, b = px[x, y]
            px[x, y] = (int(r * (PLAQUE_MUL[0] * f + (1 - f))),
                        int(g * (PLAQUE_MUL[1] * f + (1 - f))),
                        int(b * (PLAQUE_MUL[2] * f + (1 - f))))

    w, h, dp, _ = dds.read_dds(DONOR)
    donor = Image.frombytes("RGBA", (w, h), bytes(dp))
    bb, gg, rr, _ = donor.split()
    donor = Image.merge("RGB", (rr, gg, bb))
    out = donor.copy()                       # keeps the gilt border exactly
    out.paste(im.crop((FRAME, FRAME, TARGET_W - FRAME, TARGET_H - FRAME)), (FRAME, FRAME))
    return out


def convert(src, out_dds, box=None, preview=None, haze=0.55, haze_x=1.0, haze_y=1.0):
    im = Image.open(src).convert("RGB")
    im = crop_2to1(im, box)
    im = painterly(im)
    im = im.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=95, threshold=2))
    im = aerial_haze(im, hx=haze_x, hy=haze_y, strength=haze)
    im = split_tone(im)
    im = vignette(im)
    im = grade(im)                       # last, so nothing after it undoes the match
    im = add_frame_and_plaque(im)

    sat, val, con = measure(im)
    print("  result: saturation %.1f  value %.1f  contrast %.1f   (vanilla %.1f / %.1f / %.1f)"
          % (sat, val, con, VANILLA_SAT, VANILLA_VAL, VANILLA_CONTRAST))

    if preview:
        im.save(preview)

    # vanilla header, so the pixel format matches exactly
    V = (r"D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV"
         r"/gfx/interface/great_projects/great_project_bran_castle.dds")
    _, _, _, hdr = dds.read_dds(V)
    buf = bytearray()
    px = im.load()
    for y in range(TARGET_H):
        for x in range(TARGET_W):
            r, g, b = px[x, y]
            buf += bytes((b, g, r, 255))
    dds.write_dds(out_dds, TARGET_W, TARGET_H, buf, hdr)
    print("  written", out_dds, os.path.getsize(out_dds), "bytes")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    box = None
    preview = None
    for a in sys.argv[1:]:
        if a.startswith("--crop"):
            box = tuple(int(v) for v in a.split("=", 1)[1].split(","))
        if a.startswith("--preview"):
            preview = a.split("=", 1)[1]
    convert(args[0], args[1], box, preview)


def aerial_haze(im, hx=1.0, hy=1.0, strength=0.55, tint=(196, 208, 222)):
    """Push the far ground back the way the vanilla paintings do.

    An aerial photograph gives every distance the same clarity. The paintings
    do not: distant ground goes pale, cool and soft. The mask rises toward the
    corner given by (hx, hy) - 1,0 is top right - so the town behind the castle
    recedes while the walls in front stay sharp.
    """
    from PIL import ImageFilter
    soft = im.filter(ImageFilter.GaussianBlur(radius=1.4))
    w, h = im.size
    px, sp = im.load(), soft.load()
    for y in range(h):
        fy = 1.0 - abs(y / (h - 1.0) - (1.0 - hy))
        for x in range(w):
            fx = 1.0 - abs(x / (w - 1.0) - hx)
            t = max(0.0, min(1.0, (fx * fy) ** 2.2)) * strength
            r, g, b = sp[x, y] if t > 0.25 else px[x, y]
            px[x, y] = (int(r + (tint[0] - r) * t),
                        int(g + (tint[1] - g) * t),
                        int(b + (tint[2] - b) * t))
    return im
