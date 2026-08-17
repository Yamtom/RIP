# Balance and playtest report

## Status

As of 2026-08-16, execution against the current worktree is **pending**:

- valid AI observer runs to 1650: **0 / 10**;
- completed manual representative campaigns: **0 / 3**.

The automated startup gate now passes. The latest snapshot-backed smoke entered
observer mode, archived an uncompressed save dated `1446.1.1`, and completed
without a crash. It is evidence that the harness works, but it is intentionally
not counted as one of the ten runs to 1650. Old November 2025 observer saves and
January 2026 logs predate the current August 2026 code and are not counted.

Latest smoke evidence:
[`smoke_20260816_190251Z/run_01/manifest.json`](../diagnostics/observer_runs/smoke_20260816_190251Z/run_01/manifest.json).

Do not convert any row below to Pass or Fail without linking the run manifest,
endpoint save, archived logs, and measured results. A launch attempt or a save
file by itself is not completion evidence.

## Test target

The tested revision must satisfy all of the following:

1. KIE/KRU expansion remains regionally paced rather than issuing uncontrolled
   long-range claim bursts.
2. MOS/RUS mission rewards and expansion stay within the same pacing envelope.
3. A full regional minor route normally grants about 50–120 permanent-claim
   provinces; broad region rewards follow control of roughly 40–60% of that
   region.
4. Early or distant claims are temporary (the design target is 25 years) or
   replaced by a bounded CB.
5. PU, vassalization, and tributary CBs have an explicit finite duration,
   geographically valid targets, and mutually exclusive choices where a reward
   offers alternatives.
6. No actor accumulates unintended simultaneous subject-CB targets.

These are review criteria, not claimed outcomes.

## Environment record

| Field | Required value/evidence | Actual |
|---|---|---|
| Source identity | Git revision plus immutable source snapshot and SHA-256 inventory | Smoke: HEAD `0ec6e4fc`, 425 files, SHA-256 `28E915AB…D57` |
| EU4 version | `v1.37.5.0` | Confirmed by smoke manifest |
| Enabled mods | Exactly `mod/RIP.mod` | Confirmed by archived `dlc_load.json` |
| Start date | `1444.11.11` | Confirmed by archived `game.log` |
| End date | `>= 1650.1.1` | Pending endpoint save |
| Saves | Uncompressed EU4 text saves | Smoke checkpoint `1446.1.1` validated; full checkpoints pending |
| Logs | Archived before the next launch | 29 fresh smoke logs archived; full-run logs pending |

## Static implementation verification

Runtime playtesting is still pending, but the static checks now cover more
than they did, and their results are worth recording here because they are
the only evidence that exists until the ten runs happen.

Run from the mod root; `check_script_layer.py` needs the EU4 install and
finds it automatically or takes `EU4_DIR`.

| Check | Covers | State as of 2026-08-17 |
|---|---|---|
| `check_clausewitz_braces.py` | BOM and brace balance | pass |
| `check_claim_pacing.py` | KIE/KRU, Russia, long-range claims | pass |
| `check_subject_cb_limits.py` | subject-CB duration and exclusivity | pass |
| `check_glossary.py` | toponyms and register | pass |
| `check_script_layer.py` | structure, localisation, reachability | 10 errors, all listed below |

What `check_script_layer.py` gained since this report was written:

- **merge conflict markers.** `events/QasimKhanate.txt` reached `origin/main`
  with `<<<<<<<` / `=======` / `>>>>>>>` still in it. Braces balanced around
  them, so every other check passed while the file could not be parsed at all.
- **event pictures and opinion modifiers**, both of which fail silently - a
  bad picture renders an empty frame, a bad opinion modifier does nothing.
- **flags tested but never set**, which makes whatever they gate unreachable.
- **orphan `is_triggered_only` events**. This check existed but never worked;
  it counted each event as its own caller.

The ten remaining errors are province references whose right answer is a
design call rather than a lookup - see section 7 of `docs/WORKSHOP_LISTING.md`.

The current source passes the targeted contracts in
`tests/check_claim_pacing.py`, `tests/check_subject_cb_limits.py`,
`tests/check_clausewitz_braces.py`, and `tests/check_glossary.py`.

- KIE/KRU formation claims require 20 Ruthenia provinces; Russia requires 23
  provinces before the broad follow-up reward.
- Russia formation no longer grants the former Crimea/Ural permanent burst.
  Baltic, Scandinavian, Siberian, and other distant rewards use temporary or
  staged claims.
- The Asian trade reward is mutually exclusive and grants only Shanshan+Tarim
  (7 provinces) or Lahore (5), replacing whole Mongolia/Hindusthan rewards.
- Mission-granted PU, vassalization, and tributary CBs use bounded 60–120 month
  windows, eligibility/no-refresh guards, and one-target cleanup where a chain
  could otherwise accumulate simultaneous targets.

These checks prove source contracts, not 1650 AI behavior; the observer and
manual matrices remain required.

## AI observer matrix

Default seeds are fixed by the harness for reproducibility.

| Run | Seed | Status | 1500 | 1550 | 1600 | 1650 | Manifest/evidence | Notes |
|---:|---:|---|---|---|---|---|---|---|
| 01 | 1001 | Pending | — | — | — | — | — | — |
| 02 | 1002 | Pending | — | — | — | — | — | — |
| 03 | 1003 | Pending | — | — | — | — | — | — |
| 04 | 1004 | Pending | — | — | — | — | — | — |
| 05 | 1005 | Pending | — | — | — | — | — | — |
| 06 | 1006 | Pending | — | — | — | — | — | — |
| 07 | 1007 | Pending | — | — | — | — | — | — |
| 08 | 1008 | Pending | — | — | — | — | — | — |
| 09 | 1009 | Pending | — | — | — | — | — | — |
| 10 | 1010 | Pending | — | — | — | — | — | — |

### Per-checkpoint country metrics

Add one row per observed tag and checkpoint. Preserve extinct tags as explicit
`exists=no` rows rather than omitting them.

| Run | Date | Tag | Exists | Formed from | Provinces | Development | Subjects | Active wars | Notes |
|---|---|---|---|---|---:|---:|---:|---:|---|
| — | — | KIE/KRU/MOS/RUS | — | — | — | — | — | — | Pending |

### Claims review

Count normal and permanent claims from the checkpoint saves and compare each
checkpoint with the preceding one. Record the mission/event source when known.

| Run | Date | Actor | Source | New normal claims | New permanent claims | Region | Long-range anomaly | Verdict |
|---|---|---|---|---:|---:|---|---|---|
| — | — | — | — | — | — | — | — | Pending |

For every suspected burst, attach the province list and explain why it is or is
not contiguous with the actor's owned/core/claimed frontier.

### Subject-CB review

| Run | Date | Actor | CB type | Target | Start | End | Duration | Concurrent subject-CB count | Geography valid | Exclusive choice respected | Verdict |
|---|---|---|---|---|---|---|---|---:|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — | Pending |

Immediate failures include a subject CB without `end_date`, a duration beyond
the implemented design cap, a target outside the stated geographic scope, or
multiple alternative rewards active at once.

## Manual representative campaigns

Observer behavior cannot replace human validation of mission readability,
choice pressure, reward timing, or save/load continuity.

| Campaign | Route | Required coverage | Status | Evidence | Findings |
|---:|---|---|---|---|---|
| 1 | KIE → KRU | Full Kyiv/KRU expansion route; claim growth and mission gates through 1650 | Pending | — | — |
| 2 | MOS → RUS | Russia mission rewards, pacing, and distant claims through 1650 | Pending | — | — |
| 3 | Subject-CB stress route | Route containing the densest PU/vassal/tributary reward choices identified by the static audit | Pending | — | — |

Each campaign requires milestone saves and screenshots at 1500, 1550, 1600,
and 1650, plus notes for:

- mission completion date and prerequisite friction;
- claim/CB state immediately before and after each relevant reward;
- alternative-choice exclusivity;
- whether the reward was useful without being compulsory;
- save/load success at least once after a relevant CB was granted.

## Runtime and error-log review

| Run/campaign | CTD/hang | New parser error | New missing localisation | Repeating event/decision | Save/load result | Verdict |
|---|---|---|---|---|---|---|
| Smoke 20260816_190251Z | No | No new claim/CB parser error | No | No | Checkpoint read as `1446.1.1` | Harness gate Pass |

Classify errors against a clean pre-run baseline. Existing unrelated vanilla
warnings must be listed separately; absence of a crash is not proof that the
mod produced no engine errors.

## Completion gate

This report is complete only after:

- all ten observer rows have endpoint evidence and reviewed metrics;
- all three manual campaigns have saves, screenshots, and notes;
- every KIE/KRU, MOS/RUS, claim-burst, and subject-CB anomaly has a disposition;
- the final run uses the same committed code that is proposed for release;
- no unresolved mod-caused runtime error remains.

Until then, the status remains **Pending**.

