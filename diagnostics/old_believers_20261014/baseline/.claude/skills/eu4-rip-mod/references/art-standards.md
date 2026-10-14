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
six under `interface/rip_government_reform_icons.gfx`.

## Flags

`gfx/flags/<TAG>.tga`. The mod ships 24. Vanilla has no `TRV.tga`, which is why Turov
needed its own.
