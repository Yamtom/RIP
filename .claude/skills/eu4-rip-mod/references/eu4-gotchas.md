# Catalogue of silent failures

Every entry was found in this repository in content that parsed cleanly, passed the
checks, and did nothing. Each carries the symptom, the cause and the fix that was
actually applied, so the next reader can recognise the shape rather than rediscover it.

---

## 1. Unreachable government reforms

**Symptom.** A reform is defined, localised, has an icon and a government-name ladder,
and never appears in game.

**Cause.** EU4 offers a reform only if it is listed under a tier in
`common/governments/00_governments.txt`. `potential` and `trigger` are irrelevant if
the reform is in no tier.

**Scale when found.** 25 of 85: the whole Podillia tree (15), all of Pereiaslav (6),
four Volhynian. `prl_ancient_principality_reform` was a country's *starting* reform
while sitting in no tier.

**Detection.**

```python
import re, glob, io
gov = io.open('common/governments/00_governments.txt', encoding='utf-8-sig', errors='replace').read()
txt = io.open('common/government_reforms/RIP_government_reforms.txt', encoding='utf-8-sig').read().replace('\r\n', '\n')
ids, d = [], 0
for l in txt.split('\n'):
    c = re.sub(r'#.*', '', l)
    if d == 0:
        m = re.match(r'^([a-zA-Z_0-9]+)\s*=\s*\{', c)
        if m: ids.append(m.group(1))
    d += c.count('{') - c.count('}')
print([i for i in ids if not re.search(r'(?<![a-z_])' + i + r'(?![a-z_])', gov)])
```

**Fix.** Place each by what it does - polity type into `feudalism_vs_autocracy`, forts
into `military_doctrines`, tax and trade into `economical_matters`, and so on. A reform
that gates itself on its own tag costs other countries nothing by sharing a tier, and
two or three alternatives in one tier is what makes a tier a choice.

A reform carrying `republic = yes` belongs in a republic tier; the route to it is
vanilla's own `become_a_republic_reform` in `monarchy/deliberative_assembly`.

---

## 2. Reforms visible to the whole world

**Symptom.** Castile is offered "Boyar Rada".

**Cause.** No `potential` block. EU4 then lists the reform in every country's slot and
only greys it out with `trigger`.

**Fix.** One scripted trigger, used by the whole family, plus a self-clause:

```
potential = {
    OR = {
        has_reform = boyar_elite_reform      # or the country loses sight of what it holds
        ruthenian_reform_visible = yes
    }
}
```

`common/scripted_triggers/ruthenian_reform_triggers.txt` holds the gate. "Majority
culture" is `dominant_culture = ruthenian`: EU4 triggers cannot express "51% of
provinces" without variables maintained by an on_action, and `dominant_culture` is the
engine's own answer to the question.

---

## 3. Tables EU4 does not have

`province_decisions` is not one. All 195 vanilla decision files use
`country_decisions`; the block was logged as `Corrupt Decision Table Entry` and
discarded, leaving `force_convert_province_effect` and `russify_province_effect`
called by nothing while the documentation claimed otherwise.

**Fix pattern.** A country decision that acts on one qualifying province per use keeps
the per-province price and the gates:

```
effect = {
    add_adm_power = -50
    random_owned_province = {
        limit = { NOT = { religion = russian_orthodox } is_city = yes NOT = { unrest = 5 } }
        force_convert_province_effect = yes
    }
}
```

Pair it with `provinces_to_highlight` so the player sees which provinces qualify.

---

## 4. Clausewitz list syntax

A list is whitespace-separated. Two consequences bite repeatedly:

**A comma becomes a token.** `leader_names = { Ivanenko, Petrenko }` puts a literal `,`
in the pool. Five country files carried 108 of them, and a rebel general appeared with
`name="Danylo ," dynasty=","`.

**An unquoted multi-word name is several names.** `Bila Tserkva` on its own line is two
ship names. Quote anything containing a space.

**Detection.** Strip quoted strings first, then look for a bare comma:

```python
code = re.sub(r'"[^"]*"', '', line.split('#')[0])
if ',' in code: ...
```

Also worth knowing: `[countrydatabase.cpp]: <TAG> has less than 10 random ship names`
in `error.log` means exactly what it says, and quoting a two-word entry reduces the
count.

---

## 5. Localisation override order

EU4 resolves a duplicated key in favour of the file loaded **last**, ordered by
filename. `RIP_l_english.yml` sorts before vanilla's `countries_l_english.yml`, so
vanilla won and Turov displayed as "Travanacore" in English while the French, German
and Spanish mirrors - which live in `zzz_`-prefixed files - showed "Turov".

**Rule.** Any override of a vanilla key goes in a `zzz_`-prefixed file. The repo keeps
`localisation/zzz_force_localisation_l_english.yml` for this.

**Audit.** `TRV` is the only mod tag whose name vanilla also defines. Check before
claiming a tag:

```python
# collect mod tags from common/country_tags/, then look for TAG / TAG_ADJ in vanilla loc
```

Related: do not override vanilla rank keys. `PRINCIPALITY:0 "The Principalities"`
renamed the rank of every vanilla Rus principality until it became
`RUTHENIAN_PRINCIPALITY`.

---

## 6. Events

`is_triggered_only = yes` with `mean_time_to_happen` logs
`Event X is triggered only, but does not have a 1 base-factor`. The MTTH is never
consulted; delete it.

`check_script_layer.py` also lists `is_triggered_only` events that nothing fires -
fourteen at last count, including `ukr_flavor.2`/`.3` and `kyiv_independence.1-3`.
Those are open questions for the author, not bugs to close blindly.

---

## 7. Mission slots

`[mission.cpp]: Non-generic mission series A overlapping with B` means two non-generic
series claim the same slot for the same country. `missions/Volhynia_Missions.txt` has
**five** series on slot 4, at least three of which can be simultaneously true for HLC.
The minimal fix is to exclude the more specific family from the shared one:

```
potential = { west_ukraine_shared_missions = yes NOT = { west_ukraine_hlc_legacy_missions = yes } }
```

This was left unapplied deliberately: mission trees are linked by `required_missions`,
and cutting a slot can strand a chain. Verify in game before changing.

---

## 8. The cultures file

`common/cultures/00_cultures.txt` overrides vanilla wholesale, so damage to it damages
every culture in the game, not only Ruthenian ones. It was once saved as pure ASCII,
which **deleted** rather than folded every accented character: `von Schöning` →
`von Schning`, `Banér` → `Banr`, `Håkon` → `Hkon`. 189 cultures, 3744 name tokens, 82
dynasty lists.

**Repair method - prefer this to rebuilding.** Rebuilding from vanilla and re-applying
the mod's edits risks losing an edit nobody remembers. Instead align the two files and
take vanilla back wherever the mod line is that line minus its non-ASCII, so only
damage can change:

```python
import difflib
drop = lambda s: ''.join(c for c in s if ord(c) < 128)
sm = difflib.SequenceMatcher(None, [drop(l) for l in van_lines], mod_lines, autojunk=False)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == 'equal':
        for k in range(i2 - i1):
            if van_lines[i1+k] != mod_lines[j1+k]:
                out[j1+k] = van_lines[i1+k]
```

That restored 1151 lines and brought 1123 of 1127 shared name lists back to byte
equality with vanilla, leaving the four genuine mod edits and all 17 added lists
untouched. Verify by counting non-ASCII: vanilla has 4501, the mod should have that
plus its own.

The mod's own lists have no vanilla to restore from and were repaired by hand.

---

## 9. Great projects

- The art must exist **and** be declared. A missing `GFX_great_project_<id>` sprite is
  317 log lines and an empty province view.
- `date` in all 138 vanilla monuments falls between -2000 and 989 - always before the
  game starts. The Sich carries 1552, which is historically right and without
  precedent; how the engine treats a monument whose date arrives mid-campaign is
  unverified.
- Empty `on_built`, `on_destroyed` and `keep_trigger` blocks are normal:
  `keep_trigger` is empty in all 141 vanilla entries.
