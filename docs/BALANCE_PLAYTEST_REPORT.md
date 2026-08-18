# Звіт про баланс і ігрові випробування

## Стан

Станом на 16 серпня 2026 прогони проти поточного дерева **ще не виконано**:

- дійсних прогонів ШІ-спостерігача до 1650 року: **0 / 10**;
- завершених ручних показових кампаній: **0 / 3**.

Автоматичний бар'єр запуску тепер проходить. Останній димовий прогін зі
знімком джерела ввійшов у режим спостерігача, зберіг нестиснене збереження з
датою `1446.1.1` і завершився без падіння. Це доказ, що оснастка працює, але
його свідомо не зараховують як один із десяти прогонів до 1650 року. Старі
збереження спостерігача з листопада 2025 і логи з січня 2026 давніші за
поточний код серпня 2026 і не зараховуються.

Доказ останнього димового прогону:
[`smoke_20260816_190251Z/run_01/manifest.json`](../diagnostics/observer_runs/smoke_20260816_190251Z/run_01/manifest.json).

Не переводьте жоден рядок нижче в «пройдено» чи «провалено» без посилання на
маніфест прогону, кінцеве збереження, заархівовані логи та виміряні
результати. Сама лише спроба запуску чи файл збереження доказом завершення не є.

## Ціль випробування

Перевірювана ревізія має задовольняти все наведене нижче:

1. Розширення KIE та KRU лишається в регіональному темпі, без неконтрольованих
   сплесків далеких претензій.
2. Нагороди місій та розширення MOS і RUS лишаються в тому самому темпі.
3. A full regional minor route normally grants about 50–120 постійний-claim
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
| End date | `>= 1650.1.1` | чекає кінцевого збереження |
| Saves | Uncompressed EU4 text saves | Smoke checkpoint `1446.1.1` validated; full checkpoints pending |
| Logs | Archived before the next launch | 29 fresh smoke logs archived; full-run logs pending |

## Статична перевірка реалізації

Ігрові випробування ще попереду, але статичні перевірки тепер охоплюють
більше, ніж раніше, і їхні результати варто записати тут — бо іншого доказу
до тих десяти прогонів не існує.

Запускати з кореня мода; `check_script_layer.py` потребує встановленої EU4 —
знаходить її сам або бере шлях із `EU4_DIR`.

| Перевірка | Що охоплює | Стан на 17 серпня 2026 |
|---|---|---|
| `check_clausewitz_braces.py` | BOM і баланс дужок | пройдено |
| `check_claim_pacing.py` | KIE/KRU, Росія, далекі претензії | пройдено |
| `check_subject_cb_limits.py` | тривалість і винятковість CB на васалів | пройдено |
| `check_glossary.py` | топоніми й регістр | пройдено |
| `check_script_layer.py` | структура, локалізація, досяжність | 10 помилок, перелічені нижче |

Що додалося в `check_script_layer.py` після написання цього звіту:

- **маркери конфлікту злиття.** `events/QasimKhanate.txt` дійшов до
  `origin/main` із `<<<<<<<` / `=======` / `>>>>>>>` усередині. Дужки навколо
  них балансували, тож усі інші перевірки проходили, поки файл узагалі не
  розбирався.
- **картинки подій і модифікатори думки** — обидва відмовляють мовчки: хибна
  картинка дає порожню рамку, хибний модифікатор думки не робить нічого.
- **прапорці, які перевіряють, але ніде не ставлять** — усе, що вони стережуть, стає недосяжним.
- **осиротілі події `is_triggered_only`.** Перевірка існувала, але не
  працювала: кожну подію вона зараховувала як власного викликача.

Десять помилок, що лишилися, — це посилання на провінції, де правильна
відповідь є рішенням дизайну, а не пошуком; див. розділ 7 у
`docs/WORKSHOP_LISTING.md`.

The current source passes the targeted contracts in
`tests/check_claim_pacing.py`, `tests/check_subject_cb_limits.py`,
`tests/check_clausewitz_braces.py`, and `tests/check_glossary.py`.

- KIE/KRU formation claims require 20 Ruthenia provinces; Russia requires 23
  provinces before the broad follow-up reward.
- Russia formation no longer grants the former Crimea/Ural постійний burst.
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
| 01 | 1001 | очікує | — | — | — | — | — | — |
| 02 | 1002 | очікує | — | — | — | — | — | — |
| 03 | 1003 | очікує | — | — | — | — | — | — |
| 04 | 1004 | очікує | — | — | — | — | — | — |
| 05 | 1005 | очікує | — | — | — | — | — | — |
| 06 | 1006 | очікує | — | — | — | — | — | — |
| 07 | 1007 | очікує | — | — | — | — | — | — |
| 08 | 1008 | очікує | — | — | — | — | — | — |
| 09 | 1009 | очікує | — | — | — | — | — | — |
| 10 | 1010 | очікує | — | — | — | — | — | — |

### Per-checkpoint country metrics

Add one row per observed tag and checkpoint. Preserve extinct tags as explicit
`exists=no` rows rather than omitting them.

| Run | Date | Tag | Exists | Formed from | Provinces | Development | Subjects | Active wars | Notes |
|---|---|---|---|---|---:|---:|---:|---:|---|
| — | — | KIE/KRU/MOS/RUS | — | — | — | — | — | — | очікує |

### Claims review

Count normal and постійний claims from the checkpoint saves and compare each
checkpoint with the preceding one. Record the mission/event source when known.

| Run | Date | Actor | Source | New normal claims | New постійний claims | Region | Long-range anomaly | Verdict |
|---|---|---|---|---:|---:|---|---|---|
| — | — | — | — | — | — | — | — | очікує |

For every suspected burst, attach the province list and explain why it is or is
not contiguous with the actor's owned/core/claimed frontier.

### Subject-CB review

| Run | Date | Actor | CB type | Target | Start | End | Duration | Concurrent subject-CB count | Geography valid | Exclusive choice respected | Verdict |
|---|---|---|---|---|---|---|---|---:|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — | очікує |

Immediate failures include a subject CB without `end_date`, a duration beyond
the implemented design cap, a target outside the stated geographic scope, or
multiple alternative rewards active at once.

## Manual representative campaigns

Observer behavior cannot replace human validation of mission readability,
choice pressure, reward timing, or save/load continuity.

| Campaign | Route | Required coverage | Status | Evidence | Findings |
|---:|---|---|---|---|---|
| 1 | KIE → KRU | Full Kyiv/KRU expansion route; claim growth and mission gates through 1650 | очікує | — | — |
| 2 | MOS → RUS | Russia mission rewards, pacing, and distant claims through 1650 | очікує | — | — |
| 3 | Subject-CB stress route | Route containing the densest PU/vassal/tributary reward choices identified by the static audit | очікує | — | — |

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

