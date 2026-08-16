# Balance and playtest report

## Status

As of 2026-08-16, execution against the current worktree is **pending**:

- valid AI observer runs to 1650: **0 / 10**;
- completed manual representative campaigns: **0 / 3**.

The harness is present under `tests/observer/`, but its startup automation still
requires a one-run GUI smoke test. Old November 2025 observer saves and January
2026 logs predate the current August 2026 code and are not counted.

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
| Git revision | Clean commit, recorded in every manifest | Pending |
| EU4 version | `v1.37.5.0` | Pending run manifest |
| Enabled mods | Exactly `mod/RIP.mod` | Pending run manifest |
| Start date | `1444.11.11` | Pending checkpoint verification |
| End date | `>= 1650.1.1` | Pending endpoint save |
| Saves | Uncompressed EU4 text saves | Pending |
| Logs | Archived before the next launch | Pending |

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
| — | — | — | — | — | — | Pending |

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

