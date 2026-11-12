# Art standards, measured

Every number here was taken from the vanilla install with `scripts/dds.py`, not
guessed. Re-measure rather than trust this file if the game updates.

## The DDS EU4 uses for interface art

Uncompressed 32-bit, 128-byte header, no mipmaps. Pixels are stored **BGRA** (the
header declares R mask `0x00FF0000`, G `0x0000FF00`, B `0x000000FF`, A `0xFF000000`).
No image library is needed: read past the header and index the bytes.

File size is always `128 + width * height * 4`.

`scripts/dds.py` provides `read_dds`, `write_dds`, `crop`, `paste`, `to_png`. Copy the
header from a vanilla file of the same class and only rewrite width, height and pitch -
that guarantees the pixel format matches byte for byte.

Pillow decodes DXT-compressed DDS if you need to read one, but write uncompressed.

## Religion icons

`icon = N` in `common/religions/*.txt` is a **frame index**, shared by three strips:

| Sprite | Texture | Frame size |
|---|---|---|
| `GFX_icon_religion` | `gfx/interface/icon_religion.dds` | 64×64 |
| `GFX_country_icon_religion` | `gfx/interface/country_icon_religion.dds` | 64×64 |
| `GFX_icon_religion_small` | `gfx/interface/icon_religion_small.dds` | 32×32 |

Vanilla ships 29 frames in each and declares `noOfFrames = 29` in
`interface/countryview.gfx`. Frame order matches the `icon` numbers in
`common/religions/00_religion.txt`: 1 catholic, 2 protestant, 3 reformed, 4 orthodox,
5 sunni, 6 shiite … 29 dreamtime.

**`gfx/interface/religion_icons/<religion>.dds` is source art the game does not read at
runtime.** Adding a file there changes nothing. This is why the mod's two religions sat
on borrowed frames - `russian_orthodox` on 2, the Protestant cross, and `greek_catholic`
on 10, the Shinto torii.

To add a religion:

1. extend all three strips by one frame each (width += 64, 64, 32);
2. override all three sprites in a mod `.gfx` with the new `noOfFrames`;
3. set `icon = N` on the religion.

The mod ships **31** frames via `interface/rip_religion_icons.gfx`. Frame 30 is Russian
Orthodoxy - the vanilla Orthodox three-bar cross with its Byzantine purple shifted to
oak (HSV hue 26, saturation ×1.50 +0.14 capped 0.62, value ×0.90, over pixels between
hue 215 and 335). Frame 31 is Greek Catholicism - the vanilla Catholic crucifix with
its gold shifted to crimson (hue 350, saturation ×1.15 +0.10 capped 0.72, value ×0.92,
over hue 15-70). Frame 32 is free.

Recolour by hue window rather than by replacing the image: the metal rim and the
outline are near-grey and fall outside the window, so vanilla's shading survives.

## Great project art

300×150, uncompressed 32-bit, no mipmaps, 180 128 bytes.

Two things are baked into **every** vanilla monument texture and must be reproduced or
the card reads as foreign:

- **a 5px gilt border**, pixel-identical across monuments, so copy it from a donor;
- **a translucent name plaque** at `(8, 8)`-`(88, 29)`, which multiplies what is under
  it by **0.47 / 0.53 / 0.57** per channel. Measured across five monuments; reproduce
  by multiply so the new sky still shows through.

Vanilla art averages, over six monuments: **saturation 80/255, value 125/255,
luminance spread 62, edge energy 28**. A photograph arrives far busier and more
saturated.

`scripts/photo_to_great_project.py` turns a photo into a card: crop to 2:1, two median
passes so detail reads as brushwork, unsharp for painted definition, split-tone,
optional aerial haze, vignette, grade onto the three means, then frame and plaque.

Two lessons from using it:

- **Grade last.** Anything after the grading step undoes it.
- **Mean-matching fails on a sky-heavy frame.** Forcing mean value down on an image
  that is mostly sky crushes the dark subject to black. When the source already sits
  near vanilla's contrast, leave contrast alone and only nudge brightness and
  saturation. The Sich needed brightness ×0.86 and saturation ×1.10, nothing more.
- Aerial haze - blending toward a pale cool tint on a gradient toward one corner - is
  what carries a modern town in the background of a photograph into the distance the
  way the paintings do.

## Government reform icons

`gfx/interface/government_reform_icons/` plus a `.gfx` declaring
`government_reform_<name>` with `noOfFrames = 1` and `norefcount = yes`. The mod ships
six under `interface/rip_government_reform_icons.gfx`. A reform's `icon = "<name>"` selects
the sprite `government_reform_<name>`; vanilla keeps its icons in that folder and in
`dlc/<dlc>/` subfolders of it, so search both before concluding an icon is absent.

Measured over the 346 files of 1.37.5: 312 are **57x57, uncompressed 32-bit BGRA, no
mipmaps, 13124 bytes**. The rest are 27 with six mipmaps (the Winds of Change set and the
frame overlay), 5 DXT5, `retain_tribal_hierarchy` at 58x58 and `modern_economics_reform`
at 57x59 - do not copy those. Every icon carries a **3 px frame** baked into the
texture - bronze rim, crimson, dark crimson - and a **51x51 picture** inside it
(x and y 3..53), painted to the edge of that window. Picture means over 334 icons: saturation 106/255
(p10-p90 64-150), value 132/255 (89-167), luminance spread 52. The frame is not
pixel-identical between icons; the per-pixel median over all of them is the common one.

The mod's six Cossack/Hetmanate icons used to be byte copies of vanilla icons (`horde_riding`
for two different reforms, `merchant_ship` for an academy). `tools/build_reform_icons.py`
now crops each from painted art that already exists - vanilla mission icons, the
Cossacks DLC banner and startup image, vanilla's `mission_early_modern_university` and the
mod's Sich great-project art - scales it to 51x51, pulls saturation and value into the p10-p90 band above (never
past it, so a flat source is not forced) and pastes it into the median frame. Donor
missions are 59x63 and the great-project art 300x150, so the crop is a square inside them
clear of the baked name plaque. `tests/check_reform_icons.py` fails on a byte copy of a
vanilla icon, on two identical icons, and on a frame that differs from its siblings.
To make a painted one instead, follow the prompt in `docs/core_ruthenia_visual_prompts.md`
and keep the same 57x57 frame.

## Mission icons

`gfx/interface/missions/` plus a `.gfx` declaring `<sprite>` with `name` and `texturefile`;
a mission's `icon = <sprite>` uses the name directly (no `government_reform_` style prefix). Vanilla
keeps its icons there and in `dlc_missions/<dlc>/...` subfolders, so search both. Names are
not all plain: `mission_non-western_soldiers`, `mission_city_of_the_world's_desire` and
`a.e.i.o.u.` are real sprites, so a parser must not stop at `-`, `'` or `.`.

Measured over the 1565 files of 1.37.5: 1511 are **59x63, uncompressed 32-bit BGRA, no
mipmaps, 14996 bytes, fully opaque**, with no frame of their own - the mission window draws it.
The rest are 42x41 (16), 60x64 (13) and a few odd sizes; do not copy those.

The six locked-branch missions (`uz_identity_branching_*`, `chr_identity_branching_*`) used to draw
vanilla's `mission_unknown_mission`; they now draw painted pictures declared in
`interface/rip_mission_icons.gfx`. `tests/check_mission_icons.py` fails on `mission_unknown_mission`,
on an `icon =` that no sprite declares, on a mod mission texture that is not a 59x63 opaque BGRA DDS,
and on a byte copy of a vanilla icon among the six.

## Flags

`gfx/flags/<TAG>.tga`. The mod ships 24. Vanilla has no `TRV.tga`, which is why Turov
needed its own.
