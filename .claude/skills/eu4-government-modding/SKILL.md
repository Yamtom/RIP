---
name: eu4-government-modding
description: EU4 1.37 government modding - the three layers (government types & reform tiers in common/governments, reform cards in common/government_reforms, scriptable powers/interactions in common/government_mechanics), their exact syntax, the traps that make a correct-looking reform never appear, and how the RIP mod wires its 100+ Ruthenian reforms. Load for any edit to government reforms, tiers, government mechanics, legacy governments, or the ruthenian_reform_visible gate.
---

# EU4 government modding

Source: <https://eu4.paradoxwikis.com/Government_mechanic_modding>, plus
<https://eu4.paradoxwikis.com/Government> and the vanilla files. Pair this with the
`eu4-rip-mod` skill for the merge gate and the encoding rules.

Government is **three layers**, and a mistake in the top layer silently kills work
in the lower two:

| Layer | File(s) | What it is |
|---|---|---|
| **Types & tiers** | `common/governments/00_governments.txt` | the 5 government types, and the **reform tier list** that decides which reforms are *offered at all* |
| **Reforms** | `common/government_reforms/*.txt` | the pickable cards - modifiers, flags, `government_abilities`, `conditional` blocks |
| **Mechanics** (1.35+) | `common/government_mechanics/*.txt` | scriptable **powers** (bars) and **interactions** (buttons), enabled by a reform's `government_abilities` |

RIP uses layers 1 and 2 heavily (100+ reforms) and **layer 3 not at all** - every
"mechanic" it has is faked with reform modifiers, `states_general_mechanic`
blocks, estates, and scripted pulses.

---

## Layer 1: types and tiers - the gate

`00_governments.txt` in a mod **overrides the whole vanilla file**. RIP ships a
full copy with its reforms spliced in.

```
monarchy = {
	reform_levels = {
		feudalism_vs_autocracy = {          # tier 1 (T1)
			reforms = { feudalism_reform autocracy_reform ... kyivan_rus_reform }
		}
		hereditary_vs_nobility  = { reforms = { ... boyar_elite_reform } }   # T2
		bureaucracy             = { reforms = { ... } }                      # T3
		state_and_religion      = { reforms = { ... sacred_regulation_reform } }
		military_doctrines      = { reforms = { ... } }
		deliberative_assembly   = { reforms = { ... assembly_houses_reform } }
		growth_of_administration= { reforms = { ... } }
		economical_matters      = { reforms = { ... vln_magdeburg_rights } }
		legitimation_of_power   = { reforms = { ... } }
		absolute_rule_vs_constitutional = { reforms = { ... representation_monarchy_reform } }
		separation_of_power     = { reforms = { ... divine_tsyisar_reform } }
	}
	basic_reform = monarchy_mechanic       # the always-on T0 reform for the type
	legacy_government = { despotic_monarchy feudal_monarchy ... tsardom_legacy }
	exclusive_reforms = { tsardom ruthenian_tsardom ... }   # at most one of these at a time
	color = { 179 25 25 }
}
```

- **A reform absent from every `reforms = { }` list is never offered.** Not greyed
  - absent. RIP lost 25 reforms this way (all of Podillia's tree, all of
  Pereiaslav's). The symptom is "the reform is in the file but nowhere in game";
  the cause is always the tier list, never the reform file.
- `basic_reform` is the T0 card every country of that type holds. RIP replaces
  `republic`'s with `rip_republic_mechanic`.
- `legacy_government` lists the pre-1.30 "restore government" targets; a reform's
  `legacy_equivalent = X` maps it to one.
- `exclusive_reforms = { A B C }` - a country may hold at most one of the set.
  Repeated blocks, each its own set. Use for "you picked the Tsardom path, the
  veche path is closed".
- `pre_dharma_mapping` at the bottom maps old save government ids; add an entry
  for any new T1 reform that sets a distinct government (RIP added
  `siversk_veche_reform`).

Tier count is fixed by the type. You cannot add a 12th monarchy tier; you place a
reform in one of the existing eleven.

---

## Layer 2: the reform card

```
<reform_id> = {
	icon = "nobleman"                       # frame in GFX_reforms_icons_set strips
	legacy_equivalent = principality_legacy
	potential = { ... }                     # DISPLAY gate
	trigger   = { ... }                     # ELIGIBILITY gate (shows but greyed)
	valid_for_nation_designer = no
	valid_for_new_country = yes             # can a fresh Nation-Designer/released country start with it
	allow_normal_conversion = no            # yes = picking it can flip government type
	lock_level_when_selected = yes          # this tier can't be re-picked later
	fixed_rank = 1                          # locks duchy(1)/kingdom(2)/empire(3)
	queen = yes  heir = yes  royal_marriage = yes  rulers_can_be_generals = yes
	maintain_dynasty = yes  heirs_can_be_generals = yes
	has_term_election = yes  duration = 6  republic = yes  republican_name = yes
	nation_designer_trigger = { }  nation_designer_cost = 10
	modifiers = { land_forcelimit_modifier = 0.15  max_absolutism = -20 }
	custom_attributes = {
		locked_government_type = yes
		enables_aristocratic_idea_group = yes
		enables_plutocratic_idea_group = no
	}
	government_abilities = { cossacks_mechanic }     # enables a layer-3 mechanic
	factions = { ... }                               # old faction system, common/factions/
	states_general_mechanic = {                      # Dutch "scales" - each key needs loc
		knyazi  = { legitimacy = 0.5 }
		boyary  = { nobles_influence_modifier = 0.1 }
	}
	conditional = {
		allow = { has_dlc = "Res Publica" }
		has_parliament = yes                         # any reform key, applied only if allowed
	}
	replacement_on_independence_war = feudalism_reform
	different_religion_acceptance = 25
	effect = { }  removed_effect = { }  post_removed_effect = { }
	ai = { factor = 10 }
}
```

### The two gates - get this wrong and Castile sees your boyar duma

- **`potential`** = should the card be *drawn* in its slot. **Must resolve true
  only for intended holders.** A reform with **no `potential` block is shown to
  every country on earth** and merely greyed by `trigger`. Nine RIP reforms were
  being offered to Castile before this was fixed.
- **`potential` must include `has_reform = <self>`** (usually as one arm of an
  `OR`), or a country that already holds the reform stops seeing it in the slot.
- **`trigger`** = may the shown card be *clicked*. This is where you put the
  expensive checks (development, institutions, province counts).
- RIP's shared visibility gate is the scripted trigger **`ruthenian_reform_visible`**
  (`common/scripted_triggers/kru_ruthenian_reform_triggers.txt`), with
  `ruthenian_reform_eligible` as the trigger-side partner. "51%" in those
  triggers means `dominant_culture` is in the Ruthenian family. Do not inline
  culture checks into individual reforms - route through the gate.

### `custom_attributes` are read elsewhere

They do nothing on their own. A `scripted_trigger` reads them with
`has_reform_property` / `check_reform_property` or the engine keys them
(`enables_aristocratic_idea_group`, `locked_government_type`,
`nation_designer_...`). Adding a `custom_attributes` key with no reader is inert.

### `conditional` blocks

`conditional = { allow = { <triggers> } <keys> }` applies `<keys>` only when
`allow` is met - the standard pattern for "this reform grants a parliament **only
if the player owns Common Sense**". `allow` is almost always `has_dlc`. Do not
nest a bare `has_dlc` line loose inside `allow` after the block already closed -
that is exactly the malformed shape that broke RIP's `siversk_veche_reform`.

---

## Layer 3: scriptable government mechanics (1.35+)

`common/government_mechanics/<name>.txt`. Vanilla ships 27 (cossacks, russian,
russian_modernization, system_of_councils, parliament_vs_monarchy,
cultural_disunity, blood_gathering, prussian_militarization, ...). A mechanic
does nothing until a **reform** turns it on with
`government_abilities = { <ability_name> }`.

```
<mechanic_name> = {
	alert_icon_gfx   = GFX_alerticons_government_mechanics
	alert_icon_index = 10
	available = {                # ONLY checked when a reform is picked; the reform
		tag = PRU               # tooltip claims the ability even if this fails
	}
	powers = {
		<power_name> = {
			min = 0  max = 100  default = 0
			reset_on_new_ruler = no
			base_monthly_growth = 0.1
			development_scaled_monthly_growth = 0.05   # x (dev / 600)
			monarch_power = mil                        # gain from ruler stat
			show_before_interactions = no
			is_good = yes
			scaled_modifier = {          # modifier x (distance to end_value)/100
				start_value = 0  end_value = 100  extend_beyond_value = yes
				trigger = { }
				modifier = { discipline = 0.05  land_maintenance_modifier = -0.2 }
			}
			reverse_scaled_modifier = { ... }         # scales from the other end
			range_modifier = { start_value = 80  end_value = 100  modifier = { } }  # flat, no scaling
			on_max_reached = { }  on_min_reached = { }
		}
	}
	interactions = {
		<interaction_name> = {
			gui = <windowType name>
			center = no
			cost_type = <power_name>  cost = 10
			potential = { }          # visibility (still occupies UI space if hidden)
			trigger   = { }          # clickability
			effect    = { add_government_power = { mechanic_type = <m> power_type = <p> value = 10 } }
			cooldown_years = 5  cooldown_token = shared_cd  cooldown_desc = LOC_KEY
			ai_chance = { factor = 0  modifier = { factor = 10  mil_power = 500 } }
		}
	}
}
```

**Auto-generated per power** (you must localise + icon both, icons in
`gfx/interface/ideas_EU4/`):
`monthly_<power>` (additive modifier) and `<power>_gain_modifier` (multiplicative).

**Triggers:** `has_government_power = { mechanic_type power_type value }`,
`government_power_frozen = { mechanic_type power_type }`.
**Effects:** `add_government_power`, `set_government_power`,
`add_government_power_scaled_to_seats`, `freeze_government_power`,
`unfreeze_government_power` - all take `{ mechanic_type power_type value }`.

**Loc:** `ability_<mechanic_name>: "Name"` (tooltip: *Enables [Name] Ability*),
`<power_name>:` / `<power_name>_desc:`, `<interaction_name>:` /
`<interaction_name>_desc:`.

### GUI - the real cost

Every mechanic with a bar or a button needs a `windowType` in an
`interface/*.gui` (subfolder `interface/government_mechanics/` is conventional)
with these **hardcoded** element names:

- `iconType name = "government_power_bar"` (+ a `progressbartype` sprite)
- `iconType name = "government_power_bar_frame"`
- `guiButtonType name = "government_interaction_button"`

A power gets its own gui **only if**: no interactions exist, **or** no interaction
uses it as `cost_type`, **or** ≥2 interactions use it as `cost_type`. Otherwise
the interaction's gui carries the bar. Always **3 buttons per row** - the engine
will not start a row at 1, 2, or 4. `size = { x y }` on the windowType sets both
the clip box and the offset to the next element.

Unlike the religion panel (see `eu4-religion-modding`), the government mechanics
strip has its **own** UI region and does not fight the province list, so adding
one bar is far less punishing than adding a faith mechanic. The cost is the DDS
art (`progress_bar.dds` + `_empty.dds`), the frame, the button quad, and the
alert-icon strip.

---

## Government rank, cultural union, reform progress

- Rank (duchy/kingdom/empire) upgrades at **300 / 1000 dev** (+ 50 / 75 prestige).
  `fixed_rank = N` in a T1 reform locks it (Tsardom, Ruthenian Tsardom = empire).
- **Empire rank auto-grants cultural union** for the primary culture's group.
  Some reforms grant same-group-accepted earlier via `custom_attributes` a
  scripted trigger reads.
- Reform progress: **+10/yr base**, scaled by autonomy, `republican_tradition`,
  crownland, `devotion`; +20% from `Ruthenian Tsardom` for Orthodox Ruthenia
  (vanilla already codes this). T2 costs 100, each tier +40; re-pick costs 50.

---

## How RIP does government (current)

- **~109 reforms** across ~14 files (`RIP_<TAG>_government_reforms.txt` +
  `RIP_shared_ruthenian_`, `RIP_shared_cossack_`, `RIP_shared_global_`).
- Polity trees: **KIE/KRU** (Kyivan Rus → Cesarstvo / Shogunate / factional
  empire), **CHR** (Siversk Veche → principality / prykaz-tsardom / dzhura /
  union), **HET** (Starshyna oligarchy, Hetman-for-life, Mazepist autocracy),
  **ZAZ** (Kosh elections, Sich brotherhood, sacred host/horde, last Sich),
  **HLC** (Galician voivodeship, magnate assembly, Austrian bureaucracy, crown &
  sejm), **VLN** (voivodeship, cossack host, grand Ruthenia), **UZH** (Palanok
  captaincy, komitat, palatial Ruthenian/Rusyn/Uhro, union synod), **PDL** /
  **PRL** (reachable trees), **LIT** (Grand Duchy reworked - union of two
  nations, pany-rada, Ruthenian chancery, statute).
- Faked mechanics: `states_general_mechanic` for the KRU "factional empire"
  (faction keys **must be consistent** and each needs loc - RIP currently mixes
  `boyars/princes` with `knyazi/boyary/hetmany`), estates
  (`common/estates/RIP_magnates.txt`), scripted pulses for the Sich.
- No `common/government_mechanics/` file exists.

### Merge-gate checks that touch government

`check_government_reforms.py` (VFS, tier membership, gates, lifecycle),
`check_government_reviews.py` (the ≤105%-of-1.37 "government review" envelope,
tier rows verified against installed vanilla), `check_government_names.py`
(name priority, reachability, title contracts), `check_clausewitz_braces.py`,
`check_glossary.py` (naming), `check_script_layer.py`. Several are coupled to
`docs/GOVERNMENT_REFORMS_MAP.uk.md` / `docs/GOVERNMENT_AUTHENTICITY_105.uk.md` -
change prose and code together.

## Traps checklist

- [ ] reform listed in a `reforms = { }` tier in `00_governments.txt`?
- [ ] `potential` present and containing `has_reform = <self>`?
- [ ] not shown to unintended tags (test: does a Castile save see it)?
- [ ] `government_abilities` name matches a real `common/government_mechanics/` entry, and its `available` can actually be met by the holder?
- [ ] `states_general_mechanic` / faction keys localised and consistent?
- [ ] `conditional { allow { } }` brace-balanced, no loose `has_dlc` after the close?
- [ ] new T1-with-government added to `pre_dharma_mapping` and `exclusive_reforms` where needed?
- [ ] icon frame index real; loc keys `<id>:0` and `<id>_desc:0` present, not overriding a vanilla key?
- [ ] `python tests/check_government_reforms.py && python tests/check_government_reviews.py && python tests/check_clausewitz_braces.py` green?
