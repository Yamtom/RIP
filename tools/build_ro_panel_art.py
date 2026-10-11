"""Reuse unpainted native religion-panel surfaces for the RO companion panel."""
from pathlib import Path
import sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import ROOT, vanilla_root
native=Image.open(vanilla_root()/'gfx/interface/defender_of_the_faith/country_religion_view_bg.dds').convert('RGBA')
for name,box in [('header',(18,86,550,132)),('surface',(235,167,325,234))]:
    asset=native.crop(box)
    path=ROOT/f'gfx/interface/rip_ro_native_{name}.dds'
    if '--check' in sys.argv:
        assert path.exists() and Image.open(path).convert('RGBA').tobytes()==asset.tobytes()
    else: asset.save(path)
print('PASS: RO header and surface are exact crops of the installed native religion panel.')
