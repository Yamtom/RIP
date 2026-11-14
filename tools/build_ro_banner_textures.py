"""Compile the four v2 church banners to reproducible 64px legacy DDS."""
from pathlib import Path
from io import BytesIO
import argparse
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
stale = []
for key in ('war', 'mercy', 'building', 'mission'):
    source = ROOT / f'assets/church_banners/ro_banner_{key}_v2.png'
    with Image.open(source) as raw:
        image = raw.convert('RGBA')
    assert image.getchannel('A').getextrema() == (0, 255), source
    image = image.convert('RGBa').resize((64, 64), Image.Resampling.LANCZOS).convert('RGBA')
    output = ROOT / f'gfx/interface/rip_church/ro_banner_{key}.dds'
    buffer = BytesIO()
    image.save(buffer, format='DDS')
    data = buffer.getvalue()
    assert len(data) == 128 + 64 * 64 * 4 and data[84:88] != b'DX10'
    if not output.exists() or output.read_bytes() != data:
        stale.append(key)
        if not args.check:
            output.write_bytes(data)
            image.save(ROOT / f'assets/church_banners/ro_banner_{key}_64.png')
if args.check and stale:
    raise SystemExit('STALE: ' + ', '.join(stale))
print(f'PASS: four 64px RGBA banners; {len(stale)} rebuilt' if not args.check else 'PASS: four banners match their sources')
