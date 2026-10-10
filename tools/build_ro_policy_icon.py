"""Compose the RO policy's centered cross with native two-state button frames.

The action spends Fervor, so its art deliberately contains no ducat symbol.
Only RIP's own sprite is written; Muslim propagation keeps its native art.
"""
from pathlib import Path
import argparse, sys
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import ROOT, vanilla_root
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
source=Image.open(ROOT/'gfx/interface/country_icon_religion.dds').convert('RGBA')
assert source.size==(31*64,64)
cross=source.crop((29*64,0,30*64,64))
cross=cross.crop(cross.getbbox())
cross.thumbnail((30,38),Image.Resampling.LANCZOS)
game=vanilla_root()
if game is None:
    raise SystemExit('Cannot build the policy icon without target-compatible EU4 native frames.')
native=Image.open(game/'gfx/interface/trading_policy_propagate_religion.dds').convert('RGBA')
assert native.size==(112,56)
result=Image.new('RGBA',native.size)
for i in range(2):
    frame=native.crop((i*56,0,(i+1)*56,56))
    # Cover the complete old crescent/coins, keeping the native ornamental frame.
    # Preserve the inward ornamental corners too: a rectangle clipped them.
    ImageDraw.Draw(frame).polygon([(14,8),(41,8),(47,14),(47,41),
                                   (41,47),(14,47),(8,41),(8,14)],
                                  fill=(26,45,49,255))
    frame.alpha_composite(cross,((56-cross.width)//2,(56-cross.height)//2))
    result.alpha_composite(frame,(i*56,0))
output=ROOT/'gfx/interface/rip_ro_mission_policy.dds'
same=output.exists() and Image.open(output).convert('RGBA').tobytes()==result.tobytes()
if args.check:
    assert same,'RO policy icon is stale'
else:
    result.save(output)
    result.save(ROOT/'diagnostics/church_redesign_20260911/ro_policy_icon.png')
print('RO POLICY ICON PASS: centered religion frame 30; complete native 56px states; no ducat symbol.')
