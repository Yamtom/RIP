---
name: eu4-rip-mod
description: Working knowledge of the RIP mod for Europa Universalis IV 1.37 - how EU4 silently drops content that looks correct, the measured art and balance standards, the encoding traps, the thirteen checks, and how to tie an in-game symptom back to script. Use for any edit to this repository: government reforms, decisions, events, missions, religions, cultures, great projects, localisation, graphics, or the Ukrainian documentation.
---

# RIP: Alternative Ruthenian Immersion Pack

A regional immersion mod for EU4 1.37.5. Read `docs/HANDOFF.md` first - it carries
the current state, the tooling and the decisions waiting on the author. This skill
carries what that document does not: the rules the engine enforces silently.

## First five minutes

```bash
git log --oneline -5 && git status          # expect a clean tree
python tests/run_all_tests.py | tail -3
```

**Thirteen** checks live in `tests/`, and `run_all_tests.py` runs them all - it is
wider than the eight `CLAUDE.md` lists, and `check_event_modifier_layer` and
`check_government_reforms` are the two that catch the most. The last line to read is
`ALL CRITICAL TESTS PASS: True`.

```
check_script_layer      check_glossary            check_clausewitz_braces
check_claim_pacing      check_subject_cb_limits   check_border_principalities
check_steppe_expansions check_docs_language       check_culture_key_compatibility
check_estate_layer      check_event_modifier_layer
check_government_names  check_government_reforms
```

`check_script_layer.py` is the noisy one. It now reports **0 errors, 164 warnings**.
The "10 errors" this file used to quote were real once and have since been fixed;
if you meet a number you did not cause, find out what changed before working -
that is the point of reading it first, not the specific number.

`check_border_principalities` and `check_steppe_expansions` read the Ukrainian
**documents** and fail if the prose stops matching the code. That is deliberate.

## The prime rule

**The mod inherits from vanilla more than it looks.** Every check written without
reading the vanilla install produces hundreds of false positives - this has caught
at least four authors:

| Check | Naive result | After reading vanilla |
|---|---|---|
| missing localisation | 415 errors | 0 - vanilla supplies the keys |
| event pictures | 215 | 89 |
| flags never set | 64 | 5 |
| province renames | 111 | 14 |

`check_script_layer.py` finds the install itself or takes `EU4_DIR`. On this machine
it is `D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV` - note the
misspelled "Programs".

**Second rule: test your own tool.** The orphan-event check was silent from the day it
was written because it counted every event as its own caller. When a new check returns
exactly zero or a very large number, plant a violation and confirm it is seen.

## Where EU4 silently drops correct-looking content

This is the most valuable thing in this skill. Every item below was found in this
repository, in content that parsed, passed every check, and did nothing.

**`common/` is flat. EU4 reads no subfolder under it.** Vanilla has not one
subdirectory anywhere inside `common/`, so a `common/ideas/replace/` or
`common/disasters/replace/` is dead script - the files are never loaded. The only
two replace mechanisms that exist are `localisation/replace/`, which is a real
engine feature, and `replace_path` in `descriptor.mod`, which swaps a whole vanilla
folder. Overriding one file is done by giving it a name that sorts later.

**Disaster `progress` factors are SUMMED as percent-per-month, not multiplied.**
Vanilla writes `factor = -1` in eleven places, in `castilian_civil_war` and
`court_and_country` among others, and a negative multiplier is meaningless. So a
"damper" written as `factor = 0.75` adds 0.75% a month instead of slowing anything:
a stable, allied, pacified country fills the bar faster than a collapsing one.
Dampers are negative addends. Every vanilla factor is a half-step - 0.5, 1, 1.5, 2,
3, 5, 10, and -0.5, -1, -3 - and no vanilla disaster has an unconditional base.

**A national idea that grants one government currency must grant all five.** All
149 vanilla national ideas that touch `legitimacy`, `republican_tradition`,
`devotion`, `horde_unity` or `meritocracy` list every one of the five, so the idea
pays out whatever government the holder has. Picking one silently gives nothing to
every other government - and in this mod HET and ZAZ start as republics.

**`church_power` does not exist outside four religions.** Only `anglican`,
`hussite`, `jewish` and `protestant` declare `aspects`. Orthodox has
`has_patriarchs` and nothing else, and both of this mod's faiths copy that, so
`add_church_power` on them is a no-op that charges nothing and grants nothing.
Patriarch authority is the currency they actually hold, and `legitimacy_equivalent`
is the trigger that reads whichever currency a government uses.

**`take_capital` targets the enemy's capital, not the province you meant.** To pin
a war goal to one province use `type = take_province` with an `allowed_provinces`
block, the way vanilla's `take_province_hre` does. A crusade CB granted against the
owner of Jerusalem with a `take_capital` goal points at Cairo.

**`red_ruthenia_area` is in `poland_region`, not `ruthenia_region`.** Every "the
Ruthenian lands" condition written as `region = ruthenia_region` silently drops
Halych, Belz, Peremyshl, Lviv and Drohobych - which is most of what a Galician
country owns, and the city the Khmelnytsky host besieged.

**`severian` and `severian_new` are empty save-compatibility aliases, on purpose.**
`tests/check_culture_key_compatibility.py` fails the build if either block gains a
body, and fails it again if any loaded script so much as reads `culture = severian`.
New work uses the vanilla keys `ryazanian` and `ryazanian_new`.

**A reform absent from `common/governments/00_governments.txt` is never offered.**
Whatever its `potential` and `trigger` say, it will not appear in any slot. 25 reforms
were defined, localised, iconed and unreachable - all of Podillia's tree, all of
Pereiaslav's, four Volhynian. Check `governments`, not the reform file.

**A reform with no `potential` block is shown to every country in the game.** EU4
lists it in every reform slot and merely greys it out by `trigger`. Nine Ruthenian
reforms were being offered to Castile. `potential` is the display gate; `trigger` is
the eligibility gate. Always include `has_reform = <self>` in `potential` or a country
that already holds the reform stops seeing it.

**`province_decisions` is not a table EU4 has.** All 195 vanilla decision files use
`country_decisions`. A `province_decisions` block is logged as a corrupt table entry
and thrown away - which left two scripted effects called by nothing while the
documentation said they had callers.

**`is_triggered_only` plus `mean_time_to_happen` is a load error.** A triggered event
never consults a MTTH.

**Clausewitz lists are whitespace-separated, and a comma is its own token.**
`leader_names = { Ivanenko, Petrenko }` puts a literal `,` in the name pool - that is
how a country ended up with the dynasty `","`. An unquoted two-word entry is two
entries: `Bila Tserkva` becomes "Bila" and "Tserkva". Quote anything with a space.

**A localisation key only wins if its filename sorts after the vanilla file.**
`RIP_l_english.yml` sorts before `countries_l_english.yml`, so vanilla won. Overrides
of vanilla keys belong in a `zzz_`-prefixed file; the repo keeps
`localisation/zzz_force_localisation_l_english.yml` for exactly this. `TRV` is the
only mod tag whose name vanilla also defines (Travancore); the other 18 are free.

**Never override a vanilla rank or title key by accident.** The mod had
`PRINCIPALITY:0 "The Principalities"`, renaming the rank of every vanilla Rus
principality. Mod-specific ranks need mod-specific keys.

## Encoding

| What | Encoding | Line endings |
|---|---|---|
| script (`common/`, `events/`, ...) | **Windows-1252**, no BOM | CRLF |
| localisation `.yml` | UTF-8 **with** BOM | CRLF |
| docs `.md` | UTF-8, no BOM | CRLF |

`common/cultures/00_cultures.txt` was once saved as pure ASCII, which **deleted** every
accented letter in 189 vanilla cultures - `von Schöning` became `von Schning`. If it
happens again, do not rebuild from vanilla and re-apply edits; align the two files line
by line with `difflib` and take the vanilla line wherever the mod line is that line
minus its non-ASCII. Only damage can change. See `references/eu4-gotchas.md`.

For the mod's own text, follow vanilla's Windows-1252 habit: keep what the codepage
has (`š`, `ž`, `á`), drop the caron from what it does not (`č` → `c`, `ľ` → `l`) -
vanilla writes `Cáki` for Čáky and `Balaša`.

## Diagnosing from the game

**EU4 autosaves are plain text and greppable** (`compress_saves=no` in this setup),
at `.../Europa Universalis IV/save games/`. When a symptom is described from play
rather than from code, grep the save before searching the repo - one `dynasty="..."`
grep found the single carrier of the `","` dynasty and named its culture and tag.

**`logs/error.log` triage.** Most of it is not ours. In a 25k-line log, 6038
`economic_ideas` wrong-scope errors were vanilla's, as were the GUI `Missing
InstantTextBox` lines and "province has no area". Ours were four lines: a corrupt
decision table, four events with a stray MTTH, a missing great-project sprite, and a
mission-slot overlap. Grep for the mod's own filenames and ids.

## Art standards

Both measured from the vanilla install, not guessed. Details and working code in
`references/art-standards.md`; `scripts/dds.py` reads and writes the uncompressed
32-bit DDS EU4 uses, with no image library.

**Religion icons.** `icon = N` in `common/religions` is a frame index into **three**
strips - `icon_religion.dds` and `country_icon_religion.dds` (64×64 frames) and
`icon_religion_small.dds` (32×32). Vanilla has 29 frames and declares
`noOfFrames = 29` in `interface/countryview.gfx`. The folder
`gfx/interface/religion_icons/` is source art the game does not read at runtime, so
dropping a file there does nothing. To add a religion: extend all three strips,
redeclare all three sprites with the new count, set `icon = N`. The mod ships 31
frames; 30 is Russian Orthodoxy, 31 Greek Catholicism, 32 is free.

**Great projects.** 300×150, uncompressed 32-bit BGRA, 128-byte header, no mipmaps.
Every vanilla texture bakes in a 5px gilt border and a translucent name plaque at
(8,8)-(88,29) that multiplies what is under it by 0.47 / 0.53 / 0.57. Vanilla art
averages saturation 80/255, value 125/255, luminance spread 62.

## Balance envelope for monuments

Measured across all 138 vanilla great projects. Staying inside it is what "balanced"
means here:

- upgrade cost is a **fixed ladder**: 1000 / 2500 / 5000, in 135 of 138;
- upgrade time 120 / 240 / 480 months;
- at most **6 country modifiers** per tier, median 3;
- **no monument grants a combat pip** at any price - the strongest discipline in the
  whole set is 0.1;
- `hostile_attrition` ≤ 2, `garrison_size` ≤ 0.25, `local_hostile_attrition` ≤ 1,
  `prestige` ≤ 1;
- `build_cost > 0` exists in only 3 of 138 (the Amsterdam Bourse and two canals).

## Naming

`docs/STYLE_GLOSSARY.md` is executable - `check_glossary.py` enforces it. Section 3a
records the reform-naming decisions. The rules that matter:

- **Title Case on every significant word.** Vanilla has no sentence-case names.
- **Keep the native term untranslated when it is the institution.** Vanilla writes
  `Iqta`, `Devshirme System`, `Tysyatsky Office`, `Legislative Sejm`, and already has
  `Sich Rada` and `Ruthenian Tsardom`. Do not swap such a word for a nearer English
  synonym - that is how `Kyivan Cesarstvo` briefly became `Kyivan Tsardom`.
- **Do not borrow another era or another world.** A mechanic may copy a shogunate; the
  name may not. Nothing younger than the period: no commissar, premier, people's
  republic.
- **An identical name can be deliberate.** The three `ruthenian_factional_empire_*`
  reforms share one name because they are one government swapping itself as the
  dominant faction pair changes. Check whether reforms are states of one machine
  before "fixing" duplicate names.
- Institutions, not abstractions: "the Rada elects the hetman", never "democratic
  traditions". `otaman` not `ataman`; `sotnia` not `sotnya`; `Kosh Otaman` never
  `Kish Otaman`.

## Documentation

All of `docs/` is Ukrainian, plus `README.md` and both harness READMEs.
`check_docs_language.py` reports the percentage - it does **not** fail the build.

**A Cyrillic letter in a line is not a translated line.** The mass word replacement
left `Володіє steppe provinces with Ruthenian culture` and `the design target is
25 років` counting as Ukrainian. `is_mostly_latin()` now catches that shape. Legitimate
English - image-generator prompts, province-name data, modifier effect columns, book
titles - is exempted explicitly in `is_translatable()`.

After any bulk replacement in docs, search for Latin and Cyrillic fused in one word:

```bash
python -c "import io,os,re;pat=re.compile(r'[A-Za-z][A-Za-z_]*_[Ѐ-ӿ]|[Ѐ-ӿ]+_[A-Za-z]');[print(p,i,l) for p,i,l in ((os.path.join(r,f),i,l) for r,_,fs in os.walk('docs') for f in fs if f.endswith('.md') for i,l in enumerate(io.open(os.path.join(r,f),encoding='utf-8'),1)) if pat.search(l)]"
```

That pass once turned `add_years_of_income` into `add_років_of_income` inside a code
block.

## Working habits that paid off here

- **Measure vanilla before deciding.** Every standard in this skill is a number taken
  from the install, which is why "too expensive" became "outside the only ladder
  vanilla uses in 135 of 138 cases".
- **Parallel sessions are real in this repository.** `git fetch` and check whether
  `main` moved before merging.
- **Commit only when asked**, and branch off `main` first.
- Scratch scripts belong in the session scratchpad, never in a directory the game
  loads. `tests/dev_tools/` exists for content deliberately kept out of the build.
