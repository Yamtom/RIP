"""Compile the three painted church images into EU4-compatible RGBA DDS assets.

Artwork is generated with imagegen; this step only resizes and encodes it.
Requires Pillow, as does the church GUI source preview.
"""
from pathlib import Path
from io import BytesIO
import argparse
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
stale = []
for name in ('liturgy', 'learning', 'charity'):
    source = ROOT / f'assets/church_icons/gc_icon_{name}.png'
    target = ROOT / f'gfx/interface/rip_church/gc_icon_{name}.dds'
    with Image.open(source) as image:
        assert image.width == image.height, (source, 'square painting required')
        compiled = image.convert('RGBA').resize((64, 64), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        compiled.save(buffer, format='DDS')
    data = buffer.getvalue()
    # Legacy uncompressed DDS is supported by EU4 1.37; no DX10 header.
    assert data[:4] == b'DDS ' and data[84:88] != b'DX10', target
    if not target.exists() or target.read_bytes() != data:
        stale.append(str(target.relative_to(ROOT)))
        if not args.check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
print(('STALE' if args.check and stale else 'GENERATED') +
      f': 3 devotional icons; {len(stale)} files')
if args.check and stale:
    raise SystemExit(1)
