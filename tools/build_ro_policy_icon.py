"""Build the RO trade-policy sprite from its existing religion frame.
The user requested a scripted replacement; no generated religious artwork.
"""
from pathlib import Path
import argparse, sys
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import ROOT, vanilla_root
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
source=Image.open(ROOT/'gfx/interface/country_icon_religion.dds').convert('RGBA')
assert source.size==(31*64,64)
cross=source.crop((29*64,0,30*64,64)).resize((42,42),Image.Resampling.LANCZOS)
coins=Image.open(vanilla_root()/'gfx/interface/icon_gold.dds').convert('RGBA')
coins=coins.crop(coins.getbbox()).resize((26,26),Image.Resampling.LANCZOS)
native=Image.open(vanilla_root()/'gfx/interface/trading_policy_propagate_religion.dds').convert('RGBA')
assert native.size==(112,56)
result=Image.new('RGBA',native.size)
for i in range(2):
    frame=Image.new('RGBA',(56,56))
    ImageDraw.Draw(frame).rounded_rectangle((5,5,50,50),radius=8,fill=(26,45,49,255))
    # Enlarged symbols, moved slightly inward while retaining their diagonal.
    # Cross centre (23,23); coin centre (38,38).
    frame.alpha_composite(cross,(2,2))
    frame.alpha_composite(coins,(25,25))
    border=native.crop((i*56,0,(i+1)*56,56))
    # Retain only the native outer frame; the old crescent is never copied.
    for box in ((0,0,56,6),(0,50,56,56),(0,6,6,50),(50,6,56,50)):
        frame.alpha_composite(border.crop(box),(box[0],box[1]))
    result.alpha_composite(frame,(i*56,0))
output=ROOT/'gfx/interface/rip_ro_mission_policy.dds'
same=output.exists() and Image.open(output).convert('RGBA').tobytes()==result.tobytes()
if args.check:
    assert same,'RO policy icon is stale'
else:
    result.save(output)
    result.save(ROOT/'diagnostics/church_redesign_20260911/ro_policy_icon.png')
print('RO POLICY ICON PASS: religion frame 30, two 56px frames, isolated sprite.')
