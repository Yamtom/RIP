# Урядові реформи RIP: пропозиція перебудови

Статус: пропозиція від 10 вересня 2026. Не виконуваний документ. Спирається на
довідник [eu4-government-modding](../.claude/skills/eu4-government-modding/SKILL.md)
(вікі `Government_mechanic_modding` + `Government`), на
[карту реформ](GOVERNMENT_REFORMS_MAP.uk.md),
[аудит автентичності](GOVERNMENT_AUTHENTICITY_105.uk.md) і пілари
[GDD](GAME_DESIGN_DOCUMENT.uk.md) (§3.4, §3.8).

> **Координація.** `.claude/worktrees/` містить кілька гілок, що правлять
> `common/government_reforms/`. Ця область активно редагується поза цією
> сесією. Будь-яку правку тут узгоджувати перед злиттям (`git fetch`, звірка
> `main`).

Мета — щоб урядова гілка кожної руської політії була **справжнім вибором машини
правління**, а не паралельними стат-палицями, і щоб механіка виражала пілар
**«Інституції замість пласких бонусів»**: сильна нагорода як наслідок рішення й
opportunity cost, а не постійний стек модифікаторів.

---

## 1. Поточний стан

**≈109 реформ** у 15 файлах (`RIP_<TAG>_government_reforms.txt` +
`RIP_shared_ruthenian_`, `_cossack_`, `_global_`), усі вписані в тіри
`common/governments/00_governments.txt` (повне перекриття ванільного файла).
Гейт видимості — скриптовий тригер `ruthenian_reform_eligible`
(`primary/accepted/dominant` руська культура або наявність руської урядової
форми).

**Механік рушія RIP не використовує взагалі.** Немає теки
`common/government_mechanics/`. Усі «механіки» — це:

- `states_general_mechanic`-блоки в `conditional { allow { has_dlc = "Res
  Publica" } }` (KRU «факційна імперія», `representation_monarchy_reform`);
- станові файли (`common/estates/RIP_magnates.txt`);
- скриптові пульси (`on_bi_yearly_pulse`) для січі;
- `custom_attributes`-прапорці, що їх читають скриптові тригери.

Полкові дерева: **KIE/KRU** (Київська Русь → Цесарство / Сеніорат / факційна
імперія), **CHR** (Сіверське віче → князівство / наказне царство / джури /
унія), **HET** (старшинська олігархія, довічне гетьманство, мазепинська
автократія, колегія), **ZAZ** (кошові вибори, січове братство, священні
орден/орда, остання Січ), **HLC** (галицьке воєводство, магнатський сейм,
австрійська бюрократія, корона й сейм), **VLN** (воєводство, козацький кіш,
велика Русь), **UZH** (паланкова капітанія, комітат, палацові
руська/русинська/угро-руська, унійний синод), **PDL/PRL** (досяжні дерева),
**LIT** (перероблене Велике князівство).

---

## 2. Оцінка як геймдизайн

### Що працює

- **T1-вибір справді форкає кампанію** для KIE (шість національних форм на M1),
  CHR (три дороги віча), HLC (польська проти австрійської), ZAZ (чотири бази),
  PDL (три M1). Це не косметика — форми несуть різні `government_abilities`,
  ранги (`fixed_rank`), типи (`monarchy`/`republic`/`monastic_order`).
- **`exclusive_reforms` вжиті** — вибір Tsardom-шляху закриває вічовий.
- **Життєвий цикл почищено** — `removed_effect` знімає провінційні модифікатори
  (`rip_gov_clear_*_effect`), `check_government_reviews` стежить за 7 такими.
- **Автентичність задокументована** — `government_authenticity_inventory.json`
  дає кожній реформі ванільний компаратор по тіру й оцінку відповідності;
  `check_government_reviews` тримає ≤105% для порівнюваних числових пакетів.

### Проблеми

1. **Багато реформ — паралельні стат-палиці.** `M2–M11` спільної руської
   драбини (`merchant_nobility_reform`, `open_trading_ports_reform`,
   `assembly_houses_reform`, `considerable_bloodline_reform`, …) — це переважно
   пари «трохи торгівлі / трохи впливу станів / трохи абсолютизму», між якими
   вибір рідко змінює те, як грається держава.
2. **`boost_income = yes` розсипано** по CHR-реформах (`siversk_veche`,
   `chr_town_union`, `chr_rada_of_lands`, `chr_desna_staple`) — це вмикач
   республіканського доходу від торгівлі, але наліплений так широко, що
   перестає бути ознакою конкретної форми.
3. **`claim_states = yes` на `kyivan_rus_reform`** (з полагодженого WIP, за
   зразком `ruthenian_tsardom`) — сильна здатність (постійні претензії на цілі
   штати). GDD §3.7 прямо позначає «Kyiv/KRU expansion» на ревізію. Проходить
   джерельний контракт, але варто окремо просимулювати темп.
4. **Неузгоджені ключі факцій `states_general_mechanic`.**
   `representation_monarchy_reform` вживає `boyars`/`princes`;
   `ruthenian_factional_empire_*` — `knyazi`/`boyary`/`hetmany`. П'ять різних
   ключів, кожен потребує локалізації, і немає єдиного словника. Гравець
   бачить то «Boyars», то «Boyary».
5. **`government_abilities`, що не активуються.** `uzh_castles_line_reform`
   (у знятому WIP) давала `hessian_militarization_mechanic` — вона доступна за
   `has_dlc = "Domination"`, тобто активувалася б, але тематично це «здача
   полків у найм», а не карпатська застава. `russian_mechanic` на київських
   формах активний (Third Rome/Domination), але це московський тулкіт царя.
6. **Немає механіки рушія там, де вона напрошується.** Січ, Гетьманщина,
   магнатські сеймики, київська сеніорат-рота — усе це прямо просить бар або
   шкалу, а RIP їх симулює вручну або зводить до модифікаторів реформи.

---

## 3. Оцінка як лудонаратив

- **Дерево здебільшого розказує руську історію** через назви за глосарієм:
  `Sich Rada`, `Ruthenian Tsardom`, `Kosh Otaman`, `Starshyna`, `Hetman for
  Life`, `Magnate Assembly`, `Divine Tsisar`. Спекулятивні гілки (Kyivan
  Seniorate, Cesarstvo) позначені як Speculative Alternate History.
- **Механіка іноді суперечить фікції.** Республіканські форми
  (`siversk_veche`, козацькі) часто грають як автократія (низький
  `max_absolutism`, але `governing_capacity`, `boost_income`, звичайні
  модифікатори — немає відчуття, що «Рада обирає», крім `has_term_election`).
  GDD §1.3: «називати установу, а не абстракцію».
- **Захоплення Гетьманщини старшиною** — центральна драма козацької держави —
  розказане трьома окремими реформами (`het_starshyna_oligarchy`,
  `het_hetman_for_life`, `het_mazepist_autocracy`), а не одним рухомим
  протистоянням «Старшина ↔ Гетьман», яке гравець бачить і на яке впливає.
- **Рота / сеніорат** (київський порядок престолонаслідування) згадана лише
  назвою `kyivan_shogunate_reform` = «Kyivan Seniorate». Механічно це звичайна
  монархія з `vassal_forcelimit_bonus`.

---

## 4. Пропозиції

### R1. Скриптована механіка рушія для ключових політій

Вікі `Government_mechanic_modding` (1.35+): `common/government_mechanics/` — це
`powers` (бари) + `interactions` (кнопки), вмикаються `government_abilities =
{ <ability> }` у реформі. **Смуга механік має власну UI-область** — на відміну
від релігійної панелі, вона не б'ється зі списком провінцій, тож ризик значно
нижчий.

**Найдешевший, безризиковий шаблон — `devshirme_mechanic`:** без блоку
`powers`, без власного `.gui`, лише `interactions`, кожна списує очки монарха
у власному `effect` (`add_adm_power = -50` тощо), рендериться дефолтним
списком урядових взаємодій. Іконки можна взяти з наявних ванільних спрайтів
(`GFX_cossacks_ability_ADM/DIP/MIL`), тобто **нуль нового DDS-арту**. Механіка з
баром (`powers` + `scaled_modifier`) потребує `.gui` з `windowType`,
`progressbartype` і текстур — тут DDS вже неминучий.

**Зроблено в цій сесії — три механіки, усі за шаблоном devshirme:**

| Реформа | Замінила | Механіка | Взаємодії |
|---|---|---|---|
| `kyivan_rus_reform`, `kyivan_cesarstvo_reform` | `russian_mechanic` (московський цар) | `kyivan_seniority_mechanic` | снем · переуділення · збір дружин |
| `kyivan_shogunate_reform` | `shogunate_mechanic` (японський даймьо) | `kyivan_seniorate_mechanic` + новий тип суб'єктів `senior_udil` | княжий збір · пересадка столів · переконфірмація надань |
| `ruthenian_factional_empire_reform` ×3 | `states_general_mechanic` (голландський) | `ruthenian_factional_court_mechanic` | залицяння до Князів / Бояр / Старшини |

Решта кандидатів за спаданням цінності:

| Механіка | Клонувати з | `powers` / `interactions` |
|---|---|---|
| **Січ: Кошова скарбниця й козацька воля** | `00_cossacks` + `16_prussian_militarization` (бар+кнопки) | бар `cossack_liberty` (0–100): високий — `republican_tradition`, `land_morale`, менше `governing_capacity`; кнопки «Розписати похід» (−воля, +дохід/претензія), «Скликати Раду» (скинути на нового кошового) |
| **Гетьманщина: Старшина ↔ Гетьман** | `18_parliament_vs_monarchy` (шкала −100…+100) | шкала: бік старшини — `nobles_influence`, `advisor_cost`, дешевша стабільність; бік гетьмана — `max_absolutism`, `reform_progress`, `army_tradition`. Замінює три окремі HET-реформи одним рухомим протистоянням |
| **Магнатські сеймики (HLC/VLN)** | `23_cultural_disunity` (бар) | бар `magnate_concord`: низький — `global_unrest`, повільніші реформи; кнопка «Сеймик» (адмін-очки → підняти) |

Січ і Гетьманщина — найбільша віддача з решти; обидві лягають на той самий
безповий шаблон (Гетьманщина краще на шкалу `18_parliament_vs_monarchy`, а це
вже вимагає `.gui` й DDS).

### R2. Уніфікувати ключі факцій

**Частково зроблено.** `states_general_mechanic` прибрано з усіх трьох
`ruthenian_factional_empire_*` (заміна — `ruthenian_factional_court_mechanic`);
взаємодії й модифікатори нового механізму вживають **`starshyna`** у назвах і
локалізації. Збережена змінна `kru_hetmany_influence` (save-сумісність) із
приміткою — рушій пише змінні у збереження, тож перейменування ключа їх ламає.
**Лишилось:** `representation_monarchy_reform` усе ще має
`states_general_mechanic { boyars = {} princes = {} }` (Res Publica) — його теж
слід звести до `boyary`/`knyazi` або перевести на власний механізм.

### R3. Згорнути паралельні стат-палиці M2–M11 у менше, різкіших виборів

Приклад: замість `merchant_nobility_reform` ≈ `open_trading_ports_reform` ≈
`assembly_houses_reform` — одна тіра з трьома реально різними машинами:
«Магдебурзькі міста» (`burghers_influence`, автономія міст, але
`max_absolutism` вниз), «Боярська дума» (`nobles_influence`, дешевші радники,
повільніший абсолютизм), «Приказна канцелярія» (`governing_capacity`,
`yearly_corruption` вниз, але `global_unrest` угору). Кожна вимикає ідейну
групу, кожна має `removed_effect`.

### R4. Дати республіканським формам республіканську механіку

`siversk_veche`, козацькі форми: додати `has_term_election` скрізь (де немає),
`republican_name = yes`, і — якщо береться R1 — бар козацької волі. Прибрати
`boost_income` там, де він не характеризує форму (лишити для торгових
республік `chr_desna_staple`, `chr_town_union`, `odesa_trade_republic`).

### R5. Повернути п'ять реформ зі знятого WIP — свідомо, з повним пакетом

У цій сесії їх зняли, бо вони ламали гейт (немає записів автентичності;
`zaz_sich_cossack_republic_reform` містив неіснуючі `cossack_privilege` та
`enables_cossack_idea_group`). Специфікації для правильного впровадження:

| Реформа | Тір | Модифікатори (перевірити проти компаратора тіру) | Пакет для злиття |
|---|---|---|---|
| `kru_all_rus_autocracy_reform` | M1 (`feudalism_vs_autocracy`), тільки KRU, `locked_government_type` | `governing_capacity_modifier 0.1`, `vassal_income 0.15`; `conditional` Third Rome → `claim_states` + (Third Rome/Domination) `russian_mechanic` | запис у `government_authenticity_inventory.json` (компаратор `autocracy_reform`/`tsardom`, роль «часткова», `comparator_limit`); loc `kru_all_rus_autocracy_reform:0`/`_desc:0`; рядок у `GOVERNMENT_REFORMS_MAP.uk.md`; `EXPECTED_REFORM_COUNT` + хеш у `check_government_reforms.py`; `== 109` → `== 114` у `check_government_reviews.py:233` |
| `kie_metropolitan_seat_reform` | M4 (`state_and_religion`), тільки KIE | `tolerance_own 1`, `church_loyalty_modifier 0.05`, `yearly_patriarch_authority 0.005` (діє лише коли KIE на `russian_orthodox`/`greek_catholic` — це задум: катедра важить, коли є власна ієрархія) | компаратор `focus_of_the_patriarchy_reform`/`holy_synod_reform`; решта пакета як вище |
| `uzh_castles_line_reform` | M5 (`military_doctrines`), тільки UZH | `fort_maintenance_modifier -0.10`, `land_forcelimit_modifier 0.1`, `defensiveness 0.15`; **замінити** `hessian_militarization_mechanic` на `militarization_mechanic` (тематичніше — «мілітаризоване прикордоння», не найм полків) або на скриптовий бар «граничарська застава» | компаратор `military_engineering_reform`/`defensive_stance_reform` |
| `vln_magnate_senate_reform` | M6 (`deliberative_assembly`), VLN-origin | `nobles_influence_modifier 0.15`, `reform_progress_growth 0.1`, `stability_cost_modifier -0.1` | компаратор `aristocratic_court_reform`/`royal_decree_reform` (як `vln_voivode_council`) |
| `zaz_sich_cossack_republic_reform` | R1 (`oligarchy_merchant_class_noble_elite`) | **переписати:** прибрати вигадані `cossack_privilege`, `enables_cossack_idea_group`; дати `land_morale 0.1`, `manpower_recovery_speed 0.1`, `global_unrest -2`, `enables_plutocratic_idea_group = yes` (як інші ZAZ-республіки). Але спершу вирішити, чи потрібен **четвертий** R1-козацький варіант поряд із `zaz_cossack_cantons` ≈ `zaz_host_and_state` ≈ `zaz_sich_brotherhood` — чи це дублювання | компаратор `civic_republicanism_government`/`noble_elite_reform` |

### R6. Не повертати два відкати ребалансу

Знятий WIP також повертав `government_abilities = { cossacks_mechanic }` у
`siversk_veche_reform` і `trade_city_reform = principality_appanage` у
`kyivan_shogunate_reform` — обидва свідомо прибрали в `1512b9da`
(«перебалансовані урядові реформи») і стережуть assert-и в
`check_government_reviews`. **Не повертати без явного рішення переглянути той
ребаланс** — і тоді разом зі зняттям assert-ів та коментарем-обґрунтуванням.

---

## 5. Що стереже гейт злиття

- `check_government_reforms.py` — `EXPECTED_REFORM_COUNT = 109` +
  `EXPECTED_REFORM_ID_SHA256` (хеш відсортованого списку ID); кожна реформа має
  бути в `docs/GOVERNMENT_REFORMS_MAP.uk.md` як `` `id` `` і в рядку
  «109 унікальних definition-ID»; кожна вписана в тір `00_governments.txt`;
  без BOM; заборонені stale-токени (`max_states`, `monarch_mil_power`, …).
- `check_government_reviews.py` — `data["reforms"]` у
  `government_authenticity_inventory.json` рівно 109, `set(rows) == live_ids`;
  для кожної реформи `set(tiers) == set(comparator_by_tier) == тіри з
  00_governments`; `comparator_role_match ∈ {відповідна, часткова}`;
  `часткова` вимагає `comparator_limit`; сім `rip_gov_clear_*_effect` у
  `removed_effect`; заборонені `monarch_admin_power`, `monarch_military_power`,
  `administrative_efficiency`, `all_power_cost`; `cossacks_mechanic` НЕ в
  `siversk_veche_reform`; `trade_city_reform` НЕ в `kyivan_shogunate_reform`;
  числові пакети `chr_prykaz_tsardom`/`rip_cossacks`/`assembly_houses` ≤105%
  ванільних компараторів.
- `check_government_names.py` — 60 блоків назв; пріоритет, досяжність,
  життєвий цикл, контракти титулів.
- `check_glossary.py` — Title Case; native institutional terms; `otaman` не
  `ataman`; `Kosh Otaman` ніколи `Kish Otaman`; жодного анахронізму.
- `check_clausewitz_braces.py` — без BOM, дужки, `conditional { allow { } }`
  без вільного `has_dlc` після закриття.
- Правило движка: реформа поза тіром `00_governments.txt` не з'являється ніколи;
  `potential` без `has_reform = <self>` показує реформу всьому світу;
  `government_abilities` активується лише коли `available` механіки виконано.
- **Жодна перевірка не рахує ігрову арифметику.** Темп претензій, силу
  `claim_states`, бар козацької волі — симулювати в
  `tests/dev_tools/balance_sim/` до злиття.

---

## 6. Зроблено в цій сесії (гілка `feat/rip-subsystems-redesign`, гейт зелений)

Коміт `fix(government): Полагодити незавершену правку урядових реформ`:

- `RIP_CHR` `siversk_veche_reform` — переписано розбалансовані `conditional`
  (валили `check_clausewitz_braces` зайвою дужкою на рядку 92); прибрано
  `government_abilities = { cossacks_mechanic }` (assert-контракт).
- `RIP_HET` — прибрано `factions = { ... }` (літеральний плейсхолдер).
- `RIP_KIE_KRU` — прибрано задубльовані `allow_vassal_*`; `allow` для
  `russian_mechanic`/`shogunate_mechanic` виправлено на
  `OR { Third Rome, Domination }` за зразком ванільного `ruthenian_tsardom`;
  прибрано повернений `trade_city_reform` у shogunate.
- `RIP_UZH`/`RIP_VLN`/`RIP_ZAZ` — фінальний CRLF.
- Знято п'ять незавершених реформ + їхню реєстрацію в тірах (див. R5).
- Збережено решту WIP: DLC-conditional торгівля, `min_autonomy` →
  `global_autonomy` на `kyivan_rus_reform`, `principality_appanage`
  `maintain_dynasty`/`replacement_on_independence_war`, кращі тексти опису.

Коміт `feat(government): Механіка Kyivan Seniority замість russian_mechanic`:

- **`common/government_mechanics/rip_kyivan_seniority.txt`** — перша скриптована
  механіка рушія в моді. `kyivan_seniority_mechanic`, шаблон `devshirme` (лише
  interactions, без powers, без `.gui`), моделює лествичне право:
  - `kyiv_call_the_snem` (ADM 50, кулдаун 15 р.) — княжий з'їзд: підданим −20
    liberty desire + `kyiv_snem_convened` (менше LD від розвитку підданих,
    +vassal FL, дипутримання; ціна — +2,5% автономії, як Любеч 1097).
  - `kyiv_regrant_the_udil` (DIP 50, кулдаун 10 р.) — пересадити князя драбиною
    тронів: випадковому підданому з LD ≥35 знімає 35 LD + думка
    `kyivan_confirmed_in_the_udil` (+25, decay 2/р.), собі +легітимність.
  - `kyiv_summon_the_druzhyny` (MIL 50, кулдаун 10 р.) — старший князь кличе
    дружини молодших: `kyiv_druzhyna_muster` (рекрути +20%, кіннота +10%,
    forcelimit +10%, наймана людність +25%; ціна — +10% утримання армій).
    ШІ активніше під час війни й проти степового (tribal) сусіда.
- Іконки — ванільні `GFX_cossacks_ability_ADM/DIP/MIL` (нуль нового арту;
  бесповий київський арт — follow-up).
- `kyivan_rus_reform`: `government_abilities = { russian_mechanic }` →
  `{ kyivan_seniority_mechanic }`. `kyivan_cesarstvo_reform`: додано те саме.
  Той самий гейт Third Rome / Domination, тож регресії для гравця без DLC
  немає. CHR «наказне царство» лишає `russian_mechanic` навмисно (емуляція
  Москви).
- Нові модифікатори в `RIP_KRU_modifiers.txt` / `kie_opinion_modifiers.txt`
  (ключ думки — `kyivan_` префікс, вимога `check_opinion_modifier_layer`);
  локалізація EN + FR/DE/ES-фолбек.

Коміт `feat(government): Механіки для сеніорату та факційної імперії KRU`:

- **`kyivan_seniorate_mechanic`** (`kyivan_shogunate_reform`, замінила
  `shogunate_mechanic`):
  - Новий тип суб'єктів **`senior_udil`** (`common/subject_types/rip_senior_udil.txt`)
    — ротаційний стіл проти вотчинного `princedom`: `forcelimit_to_overlord 0.5`
    (левій замість ренти), `pays_overlord 0.25`, `place_relative_on_throne` і
    `send_officers` увімкнені, `base_liberty_desire 40`,
    `liberty_desire_same_dynasty -12`. `rip_grant_the_udil` розгалужується за
    реформою — Сеніорат робить `senior_udil`, решта Київських урядів `princedom`.
  - Взаємодії: `kyiv_call_the_princely_levy` (MIL 60, кулдаун 10 р. —
    `rip_kyiv_princely_levy`: forcelimit +15%, vassal FL +20%, рекрути +15%,
    ціна +10% утримання); `kyiv_rotate_the_seats` (DIP 60, кулдаун 12 р. —
    випадковому senior_udil з LD ≥30 знімає 40 LD + думка); `kyiv_reconfirm_the_grants`
    (ADM 40, кулдаун 5 р. — знімає `rip_tenure_lapsed`, +довіра).
  - `on_monarch_death` (`kie_on_actions.txt`): смерть старшого князя гасить усі
    надання — senior_udil'и отримують `rip_tenure_lapsed` (LD +20) до
    переконфірмації. Це і є рота: успадкування = драбина крутиться.
- **`ruthenian_factional_court_mechanic`** (усі три `ruthenian_factional_empire_*`,
  замінила `states_general_mechanic`, **БЕЗ DLC-гейта**):
  - `kru_court_the_knyazi` / `_boyary` / `_starshyna` (по 50 очок відповідного
    типу, кулдаун 6 р.) — `KRU_courting_*` на 10 років: +20 до відповідної
    шкали впливу в `kru_recalculate_faction_influence_effect` + тематичний
    дивіденд (легітимність / податок / традиція армії). Це прямий важіль
    гравця на автоматичний доти зсув пари.
  - `kru_has_factional_empire_reform` більше не вимагає Res Publica — симуляція
    впливу (`ruthenian_factions.20`) працює base-game. Пакети `KRU_pair_*`
    збагачено (єдине джерело парних бонусів). `ruthenian_factions.2` вимкнено.

Урядові / субʼєктні / модифікаторні / brace / glossary перевірки зелені.
`run_all_tests` наразі червоний **лише через паралельну сесію релігії**
(`check_faith_content_balance`, `check_opinion_modifier_layer`,
`check_script_layer` — файли `zzzz_RIP_religion_settlement_*`); жодна з 17
помилок не стосується урядових комітів, жоден релігійний файл не в staged.

Що НЕ засвідчено (потребує запуску EU4): чи панель урядових механік рендериться
без Domination; вигляд/розміщення кнопок; чи `place_relative_on_throne` /
`send_officers` на кастомному типі суб'єктів працюють як гадалось; чи
`on_monarch_death` спрацьовує до того, як рушій розв'яже спадкування; ігрова
арифметика — симулювати в `tests/dev_tools/balance_sim/`.

---

## 7. Відкриті питання

1. Три київські/KRU механіки зроблено (сеніорат, сеніорат-левій із новим типом
   суб'єктів, факційний двір) — розширити підхід на Січ і Гетьманщину
   (рекомендація: так)? Чи потрібен бесповий арт замість позичених козацьких
   спрайтів? Чи лишається `icon = "shogunate"` / `legacy_equivalent =
   shogunate_legacy` на реформі-сеніораті, чи їх теж міняти?
2. Скільки паралельних стат-палиць M2–M11 згорнути (R3), і за яким принципом?
3. Повертати п'ять знятих реформ (R5)? Якщо так — чи потрібен четвертий
   R1-козацький варіант (`zaz_sich_cossack_republic_reform`), чи це дублювання
   `zaz_cossack_cantons` / `zaz_host_and_state` / `zaz_sich_brotherhood`?
4. `claim_states` на `kyivan_rus_reform` — лишається (як `ruthenian_tsardom`),
   чи темп претензій KIE/KRU вимагає слабшого варіанта?
5. Переглядати ребаланс `1512b9da` (cossacks_mechanic у siversk_veche,
   trade_city_reform у shogunate) — чи ці асерти лишаються?
6. `hessian_militarization_mechanic` на карпатській заставі — замінити на
   `militarization_mechanic`, на скриптовий бар, чи лишити?
7. Ключі факцій — `starshyna` чи `hetmany`? (Рекомендація: `starshyna`.)
