---
name: eu4-religion-modding
description: EU4 1.37 religion modding - religion group and religion entry syntax in common/religions, the country/province/secondary modifier blocks, heretics and conversion, every vanilla mechanic switch (papacy, has_patriarchs, fervor, blessings, church power, personal deities, holy sites, centres of reformation), the icon strips, and the hard engine limits that make a scripted faith panel overlap the province list. Explains how the RIP mod runs its two custom faiths (Russian Orthodox, Greek Catholic) on one native panel with no GUI override. Load for any edit to religions, faith mechanics, icons, church aspects, or personal deities.
---

# EU4 religion modding

Source: <https://eu4.paradoxwikis.com/Religion_modding> (full, but last verified
1.23 in places) plus the vanilla files and RIP's hard-won constraints. Pair with
`eu4-rip-mod`.

## Files

| Path | Holds |
|---|---|
| `common/religions/00_religion.txt` | vanilla groups - copy to edit, **keep the filename** |
| `common/religions/<anything>.txt` | new religion groups |
| `common/church_aspects/00_church_aspects.txt` | aspects for `uses_church_power` / `uses_anglican_power` faiths |
| `common/personal_deities/*.txt` | deities for `personal_deity = yes` faiths |
| `common/religious_conversions/00_religious_conversions.txt` | Centre-of-Reformation conversion targets + `base_conversion_speed` |
| `common/static_modifiers/` | `karma_just_right` etc (global, all `uses_karma` faiths) |
| `interface/countryview.gfx`, `provinceview.gfx`, `ledger.gfx` | religion-icon frame counts |
| `interface/countryreligionview.gui` | the faith panel (aspect item windows) |
| `gfx/interface/*religion*.dds` | the three icon strips |

## Religion group

```
jewish_group = {
	defender_of_faith = yes
	can_form_personal_unions = yes
	center_of_religion = 118                  # province id; CoRs limited to that continent pre-1.35
	crusade_name = CRUSADE
	flags_with_emblem_percentage = 33         # custom-nation / client-state flag generation
	flag_emblem_index_range = { 28 28 }
	harmonized_modifier = harmonized_jewish_group

	jewish = { ... }                          # the religion entry/entries
}
```

## Religion entry

Required: `color = { r g b }` (0-255 since 1.21), `icon = N` (frame index),
`heretic = { TYPE ... }` (≥1).

```
jewish = {
	icon = 20
	color = { 153 26 102 }
	country          = { tolerance_own = 2  advisor_pool = 1 }        # holder of this faith
	province         = { local_missionary_strength = -0.02 }          # provinces of this faith
	country_as_secondary = { idea_cost = -0.1 }                       # syncretic adopter
	heretic = { SAMARITAN KARAITE }

	allowed_conversion = { hinduism }
	on_convert = {                                                    # any country-scope effect
		change_religion = hinduism
		add_prestige = -100
	}
	allowed_center_conversion = { orthodox catholic }                 # CoR spread targets
	misguided_heretic = yes            # better base relations within group (Orthodox, Coptic)
	declare_war_in_regency = yes       # only Nahuatl in vanilla
	can_have_secondary_religion = yes  # syncretic; may pair with ONE other mechanic
	date = 1450.1.1                    # is_religion_enabled gate; games started earlier ignore it
}
```

## Mechanic switches - **do not mix**

One faith, one mechanic (the wiki: mixing "may require advanced interface modding
to work correctly" - in practice it overlaps or crashes).

| Switch | Mechanic | Moddability |
|---|---|---|
| `papacy = {}` | Catholic curia | global only; needs a papal tag or it does nothing |
| `hre_religion = yes` / `hre_heretic_religion = yes` | HRE official / primary-heresy slot | - |
| `fervor = yes` | Reformed fervor | gain modifier + focus cost/effect, global |
| `has_patriarchs = yes` | Orthodox patriarch **authority** | icons well-moddable; authority coefficients global only |
| `uses_piety = yes` | Muslim piety | scaled modifiers global |
| `personal_deity = yes` | deity pick (Norse, Hindu) | **well-moddable**, add deities per faith |
| `blessings = { }` | Coptic blessings | needs entries here + in `church_aspects/` |
| `will_get_center` (trigger in entry) | Centre of Reformation | needs `can_have_center_of_reformation_trigger` + a `religious_conversions` entry |
| holy sites (Coptic style) | up to **5** holy sites | **well-moddable, needs NO `countryreligionview.gui` entry** |
| `uses_church_power` / `uses_anglican_power` | aspects | well-moddable **but crashes without a per-religion `countryreligionview_aspectitem_<religion>` window** |
| `uses_karma`, `uses_harmony`, `authority`, `doom`, `religious_reforms`, `ancestors`, `gurus={}`, `fetishist_cult`, `uses_isolationism`, `uses_judaism_power` | as named | mostly global-only |

### Traps that already cost this repo time

- **`church_power` / `add_church_power` is a no-op outside `anglican`, `hussite`,
  `jewish`, `protestant`.** `has_patriarchs` faiths hold **patriarch authority**
  (`yearly_patriarch_authority`, `add_patriarch_authority`,
  `legitimacy_equivalent` to read whatever currency a government uses).
- **`aspects` and `blessings` are different fields** with different panels. A file
  in `common/church_aspects/` that nothing declares is dead weight.
- **`orthodox_icons` holds AT MOST ONE icon**, costs
  `ORTHODOX_ICON_AUTHORITY_COST = 0.1` PA, **lapses after
  `ORTHODOX_ICON_DURATION_MONTHS = 240`**, and every icon event carries
  `has_dlc = "Third Rome"`. Commissioning a second replaces the first.
- **`current_icon` is a trigger with no effect form** (added 1.22, never given a
  setter). Script cannot take a standing icon down - so an icon that grants a
  payload can never be revoked, and an emptied icon block must also zero its
  payloads. Vanilla's own `BYZ_double_current_icon` fakes a second icon with an
  `add_country_modifier` chain.
- **`religious_unity` is not an `export_to_variable` value** - it is a threshold
  trigger; multiply by it with an `else_if` ladder.

## Icons

Three strips in `gfx/interface`: `icon_religion.dds` +
`country_icon_religion.dds` (64x64 frames), `icon_religion_small.dds` /
`province_view_religion.dds` (32x32). To add a faith: **extend all three strips**,
bump `noOfFrames` in `GFX_icon_religion`, `GFX_country_icon_religion`,
`GFX_icon_religion_small` (`interface/countryview.gfx`),
`GFX_province_view_religion` (`provinceview.gfx`), `GFX_religion_icon_strip`
(`ledger.gfx`), then set `icon = N`. `gfx/interface/religion_icons/` is source
art the game does **not** read. RIP ships **31 frames** (30 = Russian Orthodoxy,
31 = Greek Catholicism, 32 free) - see `scripts/dds.py` in `eu4-rip-mod`.

## The panel is one rectangle - the design lesson

`has_patriarchs`, `holy_sites`, `fervor`, aspects, blessings each claim the
**same band** of `countryreligionview.gui`. Two mechanics on one faith = two
overlapping panels. Moving one is not the fix: `province_listbox` sits at
`y = 402`, 530x450, so an override that relocates a panel draws on top of the
province list. **RIP tried a GUI override and reverted it. It ships no
`countryreligionview.gui`.**

**The design that worked is the opposite:** one native panel, no GUI override,
and payloads set to a fixed fraction of vanilla's -
`tests/check_ro_blessing_window.py` enforces **95%** of vanilla Orthodox intrinsic
bonuses for Russian Orthodoxy, `tests/check_uc_curia.py` enforces **105%** of the
matching Catholic numbers for Greek Catholicism. Reach for that before reaching
for a scripted imitation with a custom bar.

## Personal deities (the one genuinely well-moddable extra)

```
# common/personal_deities/rip_deities.txt
saint_volodymyr = {
	prestige = 1
	missionary_strength = 0.01
	sprite = 56                              # frame in gfx/interface/hindu_deities_strip.dds; too-high = no icon (valid)
	potential = { religion = russian_orthodox }
	trigger = { }                            # visible-but-unpickable if false, shown in tooltip
	effect = { }  removed_effect = { }
	ai_will_do = { factor = 1  modifier = { factor = 2  personality = ai_religious_zealot } }
}
```
Needs `personal_deity = yes` on the faith, a frame in the strip + the count in
`GFX_hindu_deities_strip` (`interface/countryreligionview.gfx`), and
`<key>:` / `<key>_desc:` loc. No per-religion gui window required.

## Localisation

`<group>:`, `<religion>:`, `<religion>_religion_desc:1`, each `<heretic>:`,
`<religion>_rebels_demand:` / `_title:` / `_name:` / `_desc:` / `_army:`.
Overrides of vanilla keys go in a `zzz_`-named file.

## How RIP runs its two faiths (current)

- `common/religions/russian_orthodox.txt` (icon 30): `has_patriarchs`,
  `misguided_heretic`, `date = 1448.12.15`, an `orthodox_icons` block, `on_convert`
  → `third_rome_ideology`. Ladder of flags
  `rip_ro_stage_autocephaly → …_patriarchate → …_raskol` (1448/1589/1653).
- `common/religions/zz_greek_catholic.txt` (icon 31): `has_patriarchs`,
  `hre_heretic_religion = yes`, `allowed_center_conversion = { orthodox
  russian_orthodox catholic }`, `date = 1596.10.6`, `heretic = { BOGOMILIST }`.
- Custom machinery, all on `on_bi_yearly_pulse`:
  `common/scripted_effects/rip_faith_spread_effects.txt` (conversion budget =
  `total_dev x religious_unity / 10 x stage`, stages 0.75/0.50/0.25),
  `rip_ro_icon_effects.txt` (decision-driven iconostas: patriarch authority →
  slots → icons → per-pulse upkeep → what is left for the Sobor focus),
  `rip_uc_curia_effects.txt` (Greek Catholic standing in Rome + petitions, laid
  on patriarch authority because `has_patriarchs` already draws that bar),
  `common/disasters/rip_faith_disasters.txt` (`rip_ro_raskol` breaks on
  *success*, `rip_uc_brotherhoods` on *failure*),
  `rip_faith_zeal_effects.txt` (rebel spawns).
- Balance proven by C++ simulation in `tests/dev_tools/balance_sim/`, not by any
  check. `check_faith_content_balance.py` / `check_scripted_faith_links.py` /
  `check_ro_blessing_window.py` / `check_uc_curia.py` gate the source contracts.

## Traps checklist

- [ ] religion in a group; `color`/`icon`/`heretic` present; `icon = N` inside the declared frame count?
- [ ] one mechanic switch only; `has_patriarchs` faiths use patriarch authority, not church power?
- [ ] `orthodox_icons` block ≤1 live icon, or fully inert with zeroed payloads if the mod uses a scripted iconostas instead?
- [ ] no `countryreligionview.gui` override (or you have measured it against the `y=402` province list)?
- [ ] payloads inside the 95% (Orthodox) / 105% (Greek Catholic) envelope the checks enforce?
- [ ] all three icon strips + five `.gfx`/`.gui` frame counts bumped together?
- [ ] heretic types real and localised; `date` gate correct; `on_convert` scoped to country?
- [ ] `python tests/check_ro_blessing_window.py && python tests/check_uc_curia.py && python tests/check_faith_content_balance.py && python tests/check_scripted_faith_links.py` green?
