"""Draw the arrow between the three cycle tiles of the Muscovite Church window.

Fervor -> Nodes -> Policies: one small gold chevron with a dark rim, 24x24, transparent,
drawn at 8x and reduced so the edge is smooth at native size. No vanilla art is needed;
only Pillow. Run with --check to compare without writing.
"""
from pathlib import Path
from io import BytesIO
import argparse
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()

SIZE, SCALE = 24, 8
big = SIZE * SCALE
canvas = Image.new('RGBA', (big, big), (0, 0, 0, 0))
draw = ImageDraw.Draw(canvas)
# A chevron: two bars meeting at the right, then a short shaft. Coordinates are in 24ths.
def px(*points):
    return [(x * SCALE, y * SCALE) for x, y in points]
shape = px((3, 6), (12, 6), (20, 12), (12, 18), (3, 18), (11, 12))
draw.polygon(shape, fill=(31, 22, 12, 255))                       # rim: the same shape, grown by drawing it larger below
inner = px((5, 8.2), (11, 8.2), (16.2, 12), (11, 15.8), (5, 15.8), (10, 12))
rim = ImageDraw.Draw(canvas)
rim.line(shape + [shape[0]], fill=(31, 22, 12, 255), width=int(1.6 * SCALE), joint='curve')
draw.polygon(inner, fill=(222, 176, 82, 255))
icon = canvas.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
buffer = BytesIO()
icon.save(buffer, format='DDS')
data = buffer.getvalue()
# Legacy uncompressed DDS, as every other RIP church sprite; no DX10 header.
assert data[:4] == b'DDS ' and data[84:88] != b'DX10'
target = ROOT / 'gfx/interface/rip_church/ro_cycle_arrow.dds'
stale = not target.exists() or target.read_bytes() != data
if args.check:
    assert not stale, 'ro_cycle_arrow.dds is stale: run tools/build_ro_cycle_arrow.py'
elif stale:
    target.write_bytes(data)
    icon.resize((SIZE * 4, SIZE * 4), Image.Resampling.NEAREST).save(target.with_suffix('.png'))
print(('STALE' if args.check and stale else 'GENERATED' if stale else 'CURRENT') + ': Fervor-to-nodes-to-policies arrow, 24x24')
