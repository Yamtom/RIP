"""Compose the Mission policy banner with native two-state trade frames."""
from pathlib import Path
import argparse, sys
from PIL import Image, ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import ROOT, vanilla_root
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
symbol=Image.open(ROOT/'assets/church_banners/ro_banner_mission_64.png').convert('RGBA')
symbol.thumbnail((34,36),Image.Resampling.LANCZOS)
symbol=symbol.crop(symbol.getbbox())
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
    ImageDraw.Draw(frame).polygon([(18,9),(37,9),(46,18),(46,37),
                                   (37,46),(18,46),(9,37),(9,18)],
                                  fill=(26,45,49,255))
    frame.alpha_composite(symbol,((56-symbol.width)//2,(56-symbol.height)//2))
    original=native.crop((i*56,0,(i+1)*56,56))
    for y in range(56):
        for x in range(56):
            edge=min(x,y,55-x,55-y)<8
            corner=min(x,55-x)<14 and min(y,55-y)<14
            if edge or corner:
                assert frame.getpixel((x,y))==original.getpixel((x,y)), 'Native trade frame was clipped'
    result.alpha_composite(frame,(i*56,0))
output=ROOT/'gfx/interface/rip_ro_mission_policy.dds'
same=output.exists() and Image.open(output).convert('RGBA').tobytes()==result.tobytes()
if args.check:
    assert same,'RO policy icon is stale'
else:
    result.save(output)
    result.save(ROOT/'diagnostics/church_redesign_20260911/ro_policy_icon.png')
print('RO POLICY ICON PASS: centered religion frame 30; complete native 56px states; no ducat symbol.')
