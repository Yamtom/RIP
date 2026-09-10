---
name: eu4-culture-modding
description: EU4 1.37 culture modding - culture group and culture entry syntax in common/cultures/00_cultures.txt, name pools and inheritance, primary tag, graphical_culture, dynamic province names, accepted-culture and cultural-union mechanics, the save-compatibility rules that make a renamed culture break every history file, and how the RIP mod arranges its Ruthenian cultures across the east_slavic / slavic / carpathian groups. Load for any edit to cultures, culture groups, name lists, province culture history, or common/province_names.
---

# EU4 culture modding

Source: <https://eu4.paradoxwikis.com/Culture_modding> (thin, last verified for
1.23) plus the vanilla files and the engine's actual behaviour. Pair with
`eu4-rip-mod` for encoding and the merge gate.

## The one file

`common/cultures/00_cultures.txt`. A mod file here **replaces the entire vanilla
file** - all ~40 groups, ~189 cultures, thousands of name tokens. RIP ships a
full copy. Consequences:

- **Every vanilla diacritic must survive.** The file is **Windows-1252, no BOM,
  CRLF**. Saving it as pure ASCII once *deleted* every accented letter in 189
  cultures (`von Schöning` → `von Schning`). If it is damaged again, do **not**
  rebuild from vanilla and re-apply edits - align the two files line by line with
  `difflib` and take the vanilla line wherever the mod line is that line minus
  its non-ASCII. `tests/check_cultural_authenticity.py` and
  `tests/check_culture_key_compatibility.py` guard this.
- For the mod's *own* new text, follow vanilla's cp1252 habit: keep `š ž á`,
  drop the caron from what the codepage lacks (`č` → `c`, `ľ` → `l`) - vanilla
  writes `Cáki` and `Balaša`.

## Culture group

Top-level entries are **culture groups**. Most have **no `_group` suffix**
(`germanic`, `east_slavic`, `slavic`, `carpathian`, `byzantine`, ...); only a
handful use it (`andean_group`, `kongo_group`, `lost_cultures_group`).

```
east_slavic = {
	graphical_culture = easterngfx           # unit/building/leader art set
	second_graphical_culture = <gfx>         # 1.34+, fallback art layer

	russian = { ... }                        # a culture entry
	ruthenian = { ... }

	# group-level pools - INHERITED by every culture in the group that has none of its own
	dynasty_names = { Rurikovich Godunov "Lobanov-Rostovsky" ... }
	male_names    = { Briachislav Demid ... }
	female_names  = { Boleslava Darya ... }
}
```

**Inheritance gotcha (from the wiki):** names placed directly under the *group*
are added to the pool of every culture in that group that does not define its
own. When adding a culture to an existing group, give it its **own**
`male_names`/`female_names`/`dynasty_names` or it silently inherits the group's.

## Culture entry

Required: a unique name, `male_names`, `female_names`, `dynasty_names` (or
inherit from the group). Optional: `primary`.

```
ruthenian = {
	primary = KIE                            # this tag keeps uncontested cores forever; omit/comment if none
	male_names   = { Ivan Dmitriy "Yuriy Dolgorukiy" ... }
	female_names = { Larisa Aleksandra ... }
	dynasty_names = { Ostrogski Zaslavski "Sanguszko" ... }
}
```

- **Space = token boundary. Quote anything with a space.** `Bila Tserkva` unquoted
  is two names, "Bila" and "Tserkva"; `{ Ivanenko, Petrenko }` puts a literal
  comma in the pool (RIP once shipped the dynasty `","`).
- `male_names` / `female_names` feed **custom nations** and act as fallback.
- `dynasty_names` feed **every country of that culture** plus custom-nation
  advisor/general surnames - the widest-reach list.
- Banners (culture-specific unit flags) are enabled per culture in this file -
  copy the shape from `manchu_new`.
- There is **no** `country = { }` / `province = { }` modifier block on a culture
  (that is religions). Cultures carry names and graphics only; their gameplay
  weight is entirely in *accepted-culture* status and *unrest*.

## Save-compatibility - the rule that bites hardest

Culture ids are **written into every history file and every save**. Therefore:

- **Never rename or delete a culture that is in use.** *Move* it between groups
  instead. Deleting one turns every province/country that had it into "no
  culture" in game and in existing saves.
- RIP keeps **`severian` and `severian_new` as deliberately empty save-compat
  aliases.** `tests/check_culture_key_compatibility.py` fails the build if either
  gains a body **or if any loaded script reads `culture = severian`**. New work
  uses the vanilla keys **`ryazanian` / `ryazanian_new`**.
- Adding a culture is safe. Renaming its **localisation** is safe. Renaming the
  **key** is not.

## Where culture actually matters (mechanics)

- **Accepted cultures.** `add_accepted_culture` / `remove_accepted_culture` /
  `add_accepted_culture_class`; capacity is `num_accepted_cultures` scaled by
  governing capacity and reforms (Domination). Non-accepted provinces carry
  unrest and reduced tax/manpower.
- **Primary culture.** `change_primary_culture` (country), `change_culture`
  (province), `promote_culture`.
- **Cultural union.** Automatic at **empire rank** for the primary culture's
  whole **group** - every same-group province counts as accepted. Some
  governments/reforms grant this earlier through a `custom_attributes` key a
  scripted trigger reads.
- **Triggers:** `culture`, `culture_group`, `primary_culture`, `dominant_culture`
  (>50% of development), `accepted_culture`, `num_accepted_cultures`,
  `same_culture`, `culture_group_claim`.
- **Dynamic province names:** `common/province_names/<CULTURE>.txt` **or**
  `<TAG>.txt`, each a flat `{ 280 = "Kyiv"  281 = "Chernihiv" }`. The engine
  picks the label by the province's **culture** first, then the owner **tag**.
  `tests/check_province_names.py` checks ids, areas, encoding, and layering.

## How RIP arranges Ruthenian cultures (current - verify before editing)

Vanilla 1.37 carries **two parallel East-Slavic sets**, and RIP keeps both:

| Group | Cultures | Used by |
|---|---|---|
| `east_slavic` | `russian`, `novgorodian`, `ryazanian`, `severian`(empty), `byelorussian`, `ruthenian`, `rusyn` | **RIP's own `history/provinces/` files** (`280 - Kiev.txt` → `culture = ruthenian`) |
| `slavic` | `russian_new`, `novgorodian_new`, `ryazanian_new`, `severian_new`(empty), `byelorussian_new`, `ruthenian_new`, + all West/South Slavic `_new` | **vanilla's unmodified history** for the rest of the world |
| `carpathian` | `transylvanian`, `romanian`, `hungarian`, `rusyn_new_new` (primary UZH) | Transcarpathia |

So a RIP Kyiv (`ruthenian`, group `east_slavic`) and a vanilla Muscovy
(`russian_new`, group `slavic`) are in **different culture groups**. Whether that
divergence is deliberate (Rus' vs Great Russian as separate political-cultural
worlds) or migration debt is the central culture-design question -
`docs/CULTURAL_AUTHENTICITY_130.uk.md` and `docs/RUTHENIANEW_EXTRACTION_AUDIT.md`
carry the history. `ruthenian` (KIE) vs `rusyn` (?) vs `rusyn_new_new` (UZH) are
three separate cultures for three Ruthenian sub-identities.

`ruthenian_reform_visible` keys government access off `dominant_culture` in the
Ruthenian family - keep any culture rework and that trigger in lockstep.

## Traps checklist

- [ ] new culture added to a group, with its own name pools (not inheriting silently)?
- [ ] no space-bearing name left unquoted; no stray comma tokens?
- [ ] not renaming/deleting an in-use key; `severian`/`severian_new` untouched and unread?
- [ ] every non-ASCII vanilla name still intact (diff vs vanilla, cp1252)?
- [ ] `primary = TAG` only where that tag should hold cores forever?
- [ ] province/country history culture ids all exist in the file?
- [ ] `common/province_names` entries in the right culture/tag file, encoding clean?
- [ ] `python tests/check_cultural_authenticity.py && python tests/check_culture_key_compatibility.py && python tests/check_province_names.py` green?
