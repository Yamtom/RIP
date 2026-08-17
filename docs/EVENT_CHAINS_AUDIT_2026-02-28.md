# Event Chains Audit (2026-02-28)

> **Історичний запис.** Це звіт про завершений прохід, а не живий трекер.
> Перевірено проти коду 2026-08-17: пункти 2, 3 і 4 нижче досі відповідають
> репозиторію - вікна хрестових походів 1525/1600, `orthodox_crusade_cooldown`
> і розведення сповіщень на 45/60 днів на місці. Документ вартий збереження
> саме тому: він пояснює, **звідки взялися ці числа**, щоб їх випадково не
> «оптимізували» назад.
>
> Пункт 1 не відповідає дійсності - див. поправку нижче.

## Scope

- ZAZ-related events
- Religious events (Orthodox Crusade, Russian Orthodox, Uniate)
- Cossack raid/revolt events
- Timing burst risk and pacing

## Event Inventory

### ZAZ-related

- `events/ZaporizhiaFlavor.txt` (`zaz_flavor.*`)
- `events/ZaporizhiaFixes.txt` (`zaz_fixes.*`)
- `events/ZAZmission.txt` (`zaz_flavor_m_*`)
- `events/CossackRevolts.txt` (`zaz.*`)

### Religious

- `events/OrthodoxCrusade.txt` (`orthodox_crusade.*`)
- `events/HetmanateOrthodoxCrusade.txt`
- `events/RussianOrthodox.txt`
- `events/UniateChurch.txt`

### Cossack-focused

- `events/HetmanateCossackRaids.txt` (`het_cossack_raids.*`)
- `events/SteppeRaiding.txt`
- `events/CossackRevolts.txt`

## Balance and Coherence Assessment

### Strong points

- Core crusade chain has clear declare -> target reaction -> participant outcomes.
- ZAZ and Hetmanate content has good thematic separation (Sich, raids, frontier, religious legitimacy).
- Most chains are already internally gated by tags, tech/year, and flags.

### Issues observed before this pass

- Notification and reaction bursts clustered in short windows (2-15-30 days), causing event spam.
- Some formation decisions had duplicated province checks in `potential` and `allow`.
- One vanilla-like idea key (`MSK_ideas`) was outside the replace idea bundle.
- Orthodox crusade visibility was available earlier than intended campaign pacing.

## Implemented Improvements in this pass

### 1) Idea override hygiene

- ~~Moved `MSK_ideas` from `common/ideas/01_ideas.txt` to `common/ideas/replace/01_country_ideas.txt`.~~
- ~~Result: vanilla-like override keys are consolidated in replace ideas file (hybrid policy).~~

> **Поправка (2026-08-17).** Цього не сталося, і правильно, що не сталося.
> `MSK` - тег самого мода (Мінськ); ані `MSK`, ані `MSK_ideas` у ванілі не
> існують, тож це не «vanilla-like override key» і в `replace/` йому не місце.
> Теки `common/ideas/replace/` у репозиторії взагалі немає. `MSK_ideas`
> лишається в `common/ideas/01_ideas.txt`, і це коректно.

### 2) Formation decision density (2x province rule)

- Removed duplicated `num_of_owned_provinces_with` blocks from `potential` where `calc_true_if` already exists:
  - `decisions/RuthenianNation.txt`
  - `decisions/KuyabaNation.txt`
  - `decisions/PolesianBelarusianNations.txt`
  - `decisions/VHKNation.txt`
  - `decisions/KyivTriggers.txt` (Kyiv former paths)
- Result: cleaner visibility logic and lower province-check inflation.

### 3) Orthodox crusade appropriateness and pacing

- Delayed availability windows:
  - Constantinople crusade: `is_year = 1525` (was 1500)
  - Jerusalem crusade: `is_year = 1600` (was 1550)
- Added potential-level cooldown hiding (`NOT = { has_country_modifier = orthodox_crusade_cooldown }`).
- Staggered call-to-arms fanout in decisions to `30/45/60` days.

### 4) Event timing anti-burst changes

- `events/OrthodoxCrusade.txt`:
  - Direct target alerts changed from `15` to `45` days.
  - Participant win/fail distribution switched from `15/30/45` to `30/45/60`.
- `events/HetmanateCossackRaids.txt`:
  - Follow-up responses changed from `30` to `45` days.
  - Deep raid consequence changed from `15` to `45` days.
- `events/CossackRevolts.txt`:
  - Early diplomatic escalations changed from `30` to `45` days.
- `events/ZAZmission.txt`:
  - Ultra-short dispatches changed `10 -> 45` and `2 -> 60` days.

## Remaining Recommendations (next pass)

- Add bridge events between `UniateChurch` and `RussianOrthodox` outcomes so confessional state transitions feel less siloed.
- Standardize long-chain cooldown patterns (`country_modifier` vs `country_flag`) across all raid systems.
- Add explicit player-facing tooltips for major flag-gated decisions where ambiguity remains.

## Practical Outcome

- Fewer short-interval event clusters.
- More consistent mid-game entry for crusade content.
- Cleaner formable visibility gating without over-constraining province checks.
- Better override hygiene for vanilla-adjacent idea keys.
