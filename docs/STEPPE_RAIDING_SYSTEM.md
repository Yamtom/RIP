# Steppe Raiding System

**Implementation status:** complete in script; dedicated static contract passing  
**Runtime status:** startup/parser smoke pending  
**Game version:** EU4 1.37.5  
**Document revision:** 2026-08-17

## Scope

The system models four connected pressures around the Pontic steppe:

- horde raids and yasyr-taking against sedentary border states;
- Cossack retaliation, including a Don/Azov route;
- Crimean raids into Circassia and the movement of captives through Kaffa;
- an Ottoman response when Crimea is represented in-game as an Ottoman subject.

Captives are deliberately abstracted as income, manpower, devastation, opinion,
and temporary modifiers. There is no population ledger or slave commodity. The
system does not treat its event outcomes as claims about a particular historical
raid unless a source is named; most events are repeatable gameplay abstractions.

There are **16 events in seven connected chains**, not 16 independent chains.

## Live files

| Role | File |
|---|---|
| Events 1-16 | `events/SteppeRaiding.txt` |
| Shared market/reaction effects | `common/scripted_effects/steppe_raid_effects.txt` |
| Event and province modifiers | `common/event_modifiers/steppe_raid_modifiers.txt` |
| Opinion modifiers | `common/opinion_modifiers/RIP_opinion_modifiers.txt` |
| English localisation | `localisation/zzz_steppe_raiding_l_english.yml` |
| General raid integration | `events/RaidMechanics.txt` |
| Zaporozhian/HET integration | `events/ZaporizhiaFixes.txt`, `events/HetmanateCossackRaids.txt`, `common/scripted_effects/zaz_het_effects.txt` |
| Kaffa mission policy | `missions/Zaporozhie_Missions.txt` (`ZAZ_TUR_slave_trade`) |
| Static regression contract | `tests/check_steppe_expansions.py` |

## Event chains

### 1. Horde raid and yasyr cycle (`steppe_raid.1-.5`)

`steppe_raid.1` may fire for CRI, NOG, KAZ, AST, GOL, or a country with the
steppe-horde/Great Mongol State reform. The earlier `government_rank = 1`
fallback was removed because it accidentally made every eligible OPM a horde
raider.

The raider must be at peace, have at least 30% manpower, be off the two-year
raid cooldown, and have a valid non-allied neighboring target. The launch option
costs military power and income, creates a one-year raid party, and calls
`steppe_raid.2` for a filtered neighbor.

The target then chooses between:

- spending military power on a one-year border defense and repelling the raid;
- taking devastation and allowing the raider to reach the yasyr reward.

Glinski, Jagoldai, Lipka, Zasechnaya Cherta, and ordinary border-defense
modifiers affect province selection and/or reduce damage. A successful yasyr
sale calls `rip_feed_kaffa_market_effect`; this produces extra market income only
when province 285 currently has the licensed market.

The target receives a later ransom choice in `steppe_raid.5`. The opinion trail
uses the victim-to-raider direction consistently, so `steppe_raid.6` can find a
country whose people were actually taken.

### 2. Cossack retaliation (`steppe_raid.6-.7`)

VOL, HLC, PDL, ZAZ, countries with the Cossack estate, and countries with a
supported Cossack reform can sponsor a counter-raid against CRI or NOG after a
yasyr grievance. Estate loyalty effects are guarded by `has_estate`, so a
Cossack-reform country without the estate does not execute an invalid estate
effect.

The sponsor receives a two-year cooldown. The target suffers bounded province
damage; the Cossack country receives a small temporary retaliatory modifier.

### 3. Nogai and Kalmyk settlement (`steppe_raid.8-.9`)

The province contract is fixed to the EU4 1.37.5 map:

- Yedisan (`282`), Budjak (`1756`), and Kouban (`287`) are the possible Nogai
  settlement provinces;
- Astrakhan (`464`) and Yaik (`474`) are required for the Kalmyk event.

The old values `2410`, `2447`, `2416`, and `1082` pointed to Theodoro, Mantrega,
Majar, and Kazan respectively and are no longer used by these events.

`steppe_raid.8` is a one-shot post-1500 event for CRI/TUR after NOG disappears.
`steppe_raid.9` is a one-shot 1620-1649 event for MOS/RUS; acceptance changes
the two named provinces and grants the permanent `kalmyk_cavalry` modifier.

### 4. Zasechnaya Cherta (`steppe_raid.10`)

MOS/RUS at administrative technology 10 can invest in the defensive line when
an owned Russian-region province borders CRI, NOG, or AST. Acceptance grants the
permanent country modifier and applies `zasechnaya_cherta_province` to the
qualifying frontier provinces. Those province modifiers are recognized by the
raid target-selection and damage logic.

### 5. Don/Azov Cossack raid (`steppe_raid.11-.12`)

There is no separate DON tag in EU4 1.37.5. “Don Host” is therefore represented
by a ZAZ/HET or Cossack-reform country that owns a province in `lower_don_area`
or `azov_area`. The custom host-name text can display **Don Host** and
**Don Ataman** for a qualifying Cossack government.

The opportunity requires peace, 30% manpower, a valid neighboring CRI, no
alliance or truce, and no active five-year Cossack raid cooldown. Launching the
raid calls the Crimean response and, only if CRI is a TUR subject, requests the
Ottoman reaction.

Crimea may fund a border interception or accept bounded damage. Protected
provinces receive the reduced branch. If Crimea owns Kaffa and the raid succeeds,
the licensed market is removed and replaced with five years of disrupted trade.

### 6. Ottoman reaction (`steppe_raid.13`)

This is a triggered-only country event. It is valid only when:

- ROOT is TUR;
- CRI exists and `CRI = { is_subject_of = ROOT }`;
- FROM is an existing non-Ottoman raider and is not allied to TUR;
- the five-year `ottoman_crimean_reaction_cooldown` is absent.

The cooldown is applied in `immediate`, so no option can refresh the event. The
Porte may:

1. demand satisfaction, receiving a guarded `cb_insult` for **60 months** when
   there is no truce, alliance, or already-active copy;
2. spend income to give CRI five years of `ottoman_vassal_support` and manpower;
3. ignore the appeal at a prestige cost.

No option automatically declares war. Treating the Crimean-Ottoman relationship
as EU4 subject status is a gameplay abstraction, not a claim that the historical
relationship was equivalent to a simple vassal contract.

The helper is called by the Don chain and by the valid Zaporozhian/Hetmanate
Crimean or Ottoman raid paths. It does not fire merely because TUR exists.

### 7. Circassian raid and Kaffa policy (`steppe_raid.14-.16`)

At peace and off cooldown, CRI can select a non-allied, non-subject, non-truce
owner of land in `circassia_area`. The country is selected directly so the target
event receives `FROM = CRI` without an ambiguous province-owner scope hop.

The target can pay military power to defend or accept bounded devastation and a
yasyr loss. The latter rewards Crimea and calls the Kaffa feed helper.

`steppe_raid.16` is a province event fixed to Kaffa (`285`). It is blocked while
any of the three mutually exclusive policy modifiers is present:

- `crimean_yasyr_market` — permanent until disrupted;
- `trade_route_disrupted` — five years after a successful anti-market raid;
- `kaffa_ransom_exchange` — ten years from the event choice.

The permanent market option is visible only to GEN, CRI, TUR, a Muslim owner,
or a steppe-horde owner. Every other owner has the regulated ransom exchange as
the safe fallback.

The mission `ZAZ_TUR_slave_trade` now targets Kaffa (`285`), not Azov (`286`).
Completion removes the market/disruption state, establishes a twenty-year
ransom exchange, removes the owner's temporary slave-trade income, and preserves
the mission's port/trade upgrade. Its trade modifier is displayed as **Black Sea
Ransom Network**.

## Shared effects

### `rip_feed_kaffa_market_effect`

May be called from any scope. If Kaffa has `crimean_yasyr_market`, its owner
receives 0.05 years of income and two years of `slave_trade_income`.

### `rip_disrupt_kaffa_market_effect`

May be called from country or province scope. It resolves province `285`
internally, removes the market, applies five years of `trade_route_disrupted`,
removes `slave_trade_income` from the owner, and costs the owner prestige.

### `rip_request_ottoman_crimean_reaction_effect`

Called in the raider's country scope. It schedules `steppe_raid.13` only when
CRI is a TUR subject and TUR is off the reaction cooldown. The event receives
the raider as FROM.

## Active modifiers

| Modifier | Scope | Main effects | Typical duration |
|---|---|---|---|
| `steppe_raid_party` | country | speed, maintenance, cavalry cost | 1 year |
| `steppe_raid_cooldown` | country | marker | 2 or 5 years by chain |
| `steppe_successful_raid` | country | horde unity, prestige, cavalry | 3-5 years |
| `cossack_raid_cooldown` | country | marker | 2 or 5 years by chain |
| `steppe_border_defense` | province | defense, manpower, attrition | 1-2 years |
| `steppe_raid_devastation` | province | unrest and economic penalties | 2-5 years |
| `cossack_raid_damage` | province | unrest and economic penalties | 3 years |
| `zasechnaya_cherta` | country | attrition, fort upkeep, defense | permanent |
| `zasechnaya_cherta_province` | province | defense, attrition, development | permanent |
| `nogai_settlers` | country | cavalry and manpower recovery | 20 years |
| `kalmyk_cavalry` | country | cavalry and horde unity | permanent |
| `cossack_retaliatory_raid` | country | speed and flanking | 3 years |
| `slave_trade_income` | country | trade bonus, diplomatic penalty | 2 years per feed |
| `crimean_yasyr_market` | province | Kaffa trade/production/tax, unrest | until disrupted |
| `trade_route_disrupted` | province | trade and production penalty | 5 years |
| `kaffa_ransom_exchange` | province | smaller trade/tax bonus, lower unrest | 10 or 20 years |
| `ottoman_vassal_support` | country | maintenance, cavalry, tactics | 5 years |
| `ottoman_crimean_reaction_cooldown` | country | marker | 5 years |

Unused prototype modifiers were removed rather than retained as undocumented
dead content.

## Cross-system cleanup

- `raid_mechanics.1` now treats March and May as alternatives; the former
  impossible month AND is gone.
- `raid_mechanics.2` has a live caller again.
- Chaiky target discovery uses known coastal targets rather than requiring a
  land border with TUR/CRI.
- Province raid weighting checks province modifiers in province scope.
- ZAZ/HET raid flags use a reusable contract: the decision is available when
  the flag has never existed or has aged past its 5/10-year window. The earlier
  inverted `NOT had_country_flag` form is gone.

## Verification

Run from the mod root with a real Python interpreter:

```powershell
python tests/check_steppe_expansions.py
python tests/check_border_principalities.py
python tests/check_clausewitz_braces.py
python tests/check_script_layer.py
```

Current evidence:

- [x] dedicated static expansion contract;
- [x] braces and BOM contract;
- [x] corrected Steppe province IDs;
- [x] event/option/modifier English localisation contract;
- [x] bounded Ottoman CB, cooldown, and no forced war;
- [x] protected-border integration;
- [ ] EU4 startup/parser smoke after these edits;
- [ ] targeted event firing through every option;
- [ ] observer evidence for MTTH frequency and AI choice balance;
- [ ] save/load persistence of permanent and timed modifiers.

Unchecked runtime items are not implied by the implementation-complete status.

## Compatibility and maintenance

- Province IDs and areas are verified against EU4 1.37.5. Recheck them after a
  map-version upgrade.
- `cb_insult`, subject scopes, event FROM, and scripted-effect behavior depend on
  engine semantics; the startup smoke catches parser/load failures but not every
  branch outcome.
- Do not replace the three Kaffa helpers with duplicated inline effects. Their
  explicit province-285 resolution is the scope contract used by all callers.
- Keep `tests/check_steppe_expansions.py` synchronized with any renamed event,
  modifier, mission, or helper.

## Future Expansion Ideas

1. Add a player-facing target selector with cost and risk previews.
2. Add an OPM migration decision with strict anti-exploit checks.
3. Tune MTTH and AI weights from reproducible observer evidence.
4. Add a deeper captive-ransom ledger only if it remains performant and avoids
   presenting speculative population figures as measured history.

## Sources and design notes

The following sources support the broad historical frame; event costs, MTTH,
AI weights, and exact modifiers are game design:

- [“The Consequences of the Black Sea Slave Trade: Long-Run Development in Eastern Europe”](https://www.cambridge.org/core/journals/american-political-science-review/article/consequences-of-the-black-sea-slave-trade-longrun-development-in-eastern-europe/E6074298B3135E3B858CF9E64BE45F99) — Kaffa/Caffa and the Black Sea captive trade.
- [“Cossacks as Captive-Takers in the Ottoman Black Sea Region and Crimea”](https://www.nmc.utoronto.ca/research-publications/faculty-publications/cossacks-captive-takers-ottoman-black-sea-region-and) — Zaporozhian and Don Cossack captive-taking.
- [“The Ottoman Crimea in the Mid-Seventeenth Century: Some Problems and Preliminary Considerations”](https://www.husj.harvard.edu/articles/the-ottoman-crimea-in-the-mid-seventeenth-century-some-problems-and-preliminary-considerations) — damage from Cossack raids and Ottoman-Crimean context.
- [The Crimean Khanate and Ottoman relationship](https://brill.com/view/journals/thr/9/1/article-p86_86.pdf) — reason to document the EU4 subject model as an abstraction.
