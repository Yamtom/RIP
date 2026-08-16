# Steam Workshop listing

Everything needed for the store page, kept in the repository so the copy and
the content stay in step. Workshop item `2563577714`, EU4 `1.37.5`.

## 1. Thumbnail

`thumbnail.png` in the mod root, referenced by `picture=` in `descriptor.mod`.

- 512x512, PNG, 447 KB - inside the Workshop's 1 MB preview limit.
- It previously shipped as a progressive JPEG with EXIF data under a `.png`
  name. The Paradox launcher picks the loader by extension, so re-encoding it
  as an actual PNG is what makes it render. If the image is ever replaced,
  re-encode rather than rename.

## 2. Short description

One line, shown under the title in search results.

> A regional immersion pack for Ruthenia, the Cossack frontier and the
> Carpathian borderlands - nineteen playable tags, eleven mission trees and the
> Sich as a working institution.

## 3. Store description

Paste as-is; Steam Workshop accepts BBCode.

```
[h2]Alternative Ruthenian Immersion Pack[/h2]

A regional expansion for the lands between Kraków and the Don. It fills in the
part of the map EU4 leaves thin: the Ruthenian principalities, the Cossack
Host below the rapids, the Belarusian and Polesian north, and Transcarpathia.

[h3]Nations[/h3]
Nineteen new tags with their own ideas, government forms and flags - Volyn,
Halych, Uzhhorod, the Hetmanate, Kuyaba, Pereiaslav, Podolia, the Kyivan
Confederation, Odesa, the four Sloboda regiments (Sumy, Okhtyrka, Izium and
the Kharkov Host), the Polishchuks, and the northern principalities of Minsk,
Turov, Vitebsk and Mstislav, with Belarus as their union.

[h3]Missions[/h3]
Eleven mission trees and 524 missions in all, including full-length trees for
Zaporozhia (142 missions), Russia (74), Volhynia (66), Chernihiv (62),
Transcarpathia (50) and Kyiv (49), plus Podillia, Pereiaslav, the Hetmanate,
the Commonwealth rework and the Russian minors.

[h3]The Sich[/h3]
The Cossack estate rebuilt around the institutions that actually governed it -
the Rada, the bulava, the register, the palanky. The Zaporozhian Sich is a
great project. Raiding, the sea campaigns in chaiky, and the crown's habit of
cutting the register all feed the same politics.

[h3]Faith[/h3]
A Russian Orthodox religion with its own church aspects, the Union of Brest
and the Uniate church as a live confessional fault line, an Orthodox crusade
casus belli, and a Jewish estate with its own privileges.

[h3]Crisis[/h3]
Twelve disasters - the Ruina, the Khmelnytsky uprising, the Zaporozhian Sich
crisis, hetman succession, the Opryshky rising in the Carpathians, and the
confessional, Cossack and Ottoman crises in Podillia.

[h3]Depth[/h3]
608 events and 131 decisions, written to a documented style: named
institutions rather than abstractions, and no anachronism. Every event carries
an authenticity grade in its file header - A for documented, B for
extrapolated - so you can see where the mod follows the record and where it
departs from it.

[h3]Compatibility[/h3]
EU4 1.37.5. Written in English. French, German and Spanish clients will run it
without raw keys, but the text they see is still English - only a small part is
translated so far. Not compatible with other mods that rewrite the same
provinces or the Commonwealth mission tree.
```

## 4. Feature list (plain text)

For the Workshop's change notes, forum posts and the README.

- 19 new playable tags with national ideas, government reforms and flags
- 11 mission trees, 524 missions in total
- 608 events, 131 decisions
- Russian Orthodox religion with 21 church aspects
- Uniate church and the Union of Brest as a confessional fault line
- Cossack estate rebuilt on the Rada, the bulava and the register
- Jewish estate with its own privileges
- 12 disasters
- 2 great projects: the Zaporozhian Sich, Palanok Fortress
- Orthodox crusade casus belli, Kyivan princedom subject type
- 1444 bookmark: Kyiv, Volyn, Chernihiv, Zaporozhia, Halych, Uzhhorod
- English source text. FR/DE/ES ship as fallback files: about 64 keys each are
  actually translated, the remaining ~7,400 carry the English string so those
  clients see prose rather than raw keys. Do not advertise this as translation.

## 5. Screenshots

**These have to be captured in-game and are not in the repository.** Steam
shows the first five in the header strip, so shoot at least those, in order.
1920x1080, F12 in-game or Steam's own capture, no debug overlays, no console
open, and no mod list visible.

| # | Shot | Setup |
|---|---|---|
| 1 | Zaporozhia mission tree, upper third | Start as ZAZ 1444, open missions, scroll to the top of the tree. It is the largest in the mod and reads as the headline feature. |
| 2 | The 1444 bookmark | Main menu, single player, the Ruthenian bookmark - shows all six starting tags at once. |
| 3 | Political map of the region | Load 1444, zoom on Kyiv to Lviv to Smolensk, political mapmode. Shows the new tags on the map rather than in a list. |
| 4 | Cossack estate panel | As ZAZ or HET, open the estates tab with the Cossack estate expanded, privileges visible. |
| 5 | An event with its picture | Fire a border principalities or Sich event and shoot the window whole - shows the writing, which is where most of the work went. |
| 6 | Church aspects | As an Orthodox tag, open the religion tab with aspects showing. |
| 7 | The Zaporozhian Sich great project | Province view of the Sich with the project panel open. |
| 8 | A disaster in progress | The Ruina or Khmelnytsky uprising, disaster panel with progress bar. |
| 9 | Volhynia mission tree | Second-largest tree; shows the mod is not only about the Sich. |
| 10 | A formed nation | Belarus or the Hetmanate after formation, country panel with ideas visible. |

Avoid: shots of the launcher, of file listings, of the mission tree zoomed out
past legibility, or of any window with placeholder text in it.

## 6. Before publishing

Run both checks from the mod root and read the output:

```
python tests/check_script_layer.py
```

```
python tests/check_glossary.py
```

`check_script_layer.py` needs the EU4 install to give a true answer, because
the mod inherits most of its localisation from vanilla. It finds the install
automatically or takes `EU4_DIR`; without it, localisation findings drop to
warnings rather than being guessed at.

## 7. Province IDs still to settle

`check_script_layer.py` compares every `owns = N  # Name` against the province
that N actually is. These are the ones left where the right answer is a design
call rather than a lookup. Each is a trigger that currently points somewhere
the author did not mean.

| Where | Written | Actually | Comment says |
|---|---|---|---|
| `events/SteppeRaiding.txt:435` | `2410` | Theodoro | Yedisan |
| `events/SteppeRaiding.txt:436` | `2447` | Mantrega | Budjak |
| `events/SteppeRaiding.txt:437` | `2416` | Majar | Kuban |
| `events/SteppeRaiding.txt:504` | `1082` | **Kazan** | Lower Yayik |
| `common/scripted_triggers/zaz_het_triggers.txt:51` | `2410` | Theodoro | Khortytsia |
| `common/scripted_triggers/zaz_het_triggers.txt:52` | `2411` | Mansur | Samara |
| `common/scripted_triggers/zaz_het_triggers.txt:269` | `2408` | Lipetsk | Sumy |
| `missions/Podillia_Missions.txt:158` | `4749` | Stargard | "Example province in Pontic Steppe" |
| `missions/Podillia_Missions.txt:159` | `4750` | Kruje | "Add more Pontic Steppe province IDs as needed" |
| `missions/Zakarpatta_Missions.txt:761` | `2960` | Sadecki | Novi Sad |
| `missions/zzz_Hetmanate_Missions.txt:587` | `153` | Pest | Dobruja |
| `decisions/Podillia_Decisions.txt:786` | `280` | Kiev | Halych |
| `decisions/Podillia_Decisions.txt:787` | `282` | Yedisan | Lutsk |
| `decisions/Podillia_Decisions.txt:788` | `283` | Zaporozhia | Vladimir-Volynsky |

Two of these are worth doing before anything else:

- **`SteppeRaiding.txt:504`** converts `1082` to Oirat culture and Vajrayana.
  `1082` is Kazan, so the Kalmyk settlement event currently converts Kazan
  rather than the lower Yaik. There is no "Lower Yayik" province in 1.37;
  `466` Sarai or `468` Khazaria are the plausible substitutes.
- **`Podillia_Decisions.txt:786-788`** is one requirement set, so the three
  lines have to move together. It currently demands cores on Kyiv, Yedisan and
  Zaporozhia instead of Halych, Lutsk and Volodymyr. Note that 1.37 has no
  Lutsk or Volodymyr-Volynskyi province - both fall inside `279` Volhynia -
  so the set needs rethinking rather than remapping.

- **`Podillia_Missions.txt:158-159`** are placeholder IDs that shipped: they
  point at Stargard in Pomerania and Kruje in Albania.
