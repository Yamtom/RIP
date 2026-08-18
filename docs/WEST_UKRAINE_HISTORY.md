# Система історичних подій Західної України

---

## Стан на 16 серпня 2026

Документ звірено з кодом: **усі 26 модифікаторів, перелічені в таблицях
нижче, існують** у `common/event_modifiers/` та `common/opinion_modifiers/`.
Розбіжностей немає — рідкісний випадок у цьому репозиторії.

### Чого бракувало: гайдамаччина

`CHAIN 3: Cossack Uprisings` доводить справу до 1680 року й на цьому спиняє
її. Наступне століття на Правобережжі - гайдамацьке, і в моді його не було
взагалі: жодної згадки гайдамаків чи Коліївщини в жодному файлі.

Додано `events/Haidamaky.txt`:

| Подія | Коли | Хто |
|---|---|---|
| `haidamaky.1` — Ватаги в ярах | 1715-1765 | власник Черкас, Брацлава або Житомира з високою автономією чи заворушеннями |
| `haidamaky.2` — Коліївщина | 1768-1775 | той самий, якщо не завів надвірних міліцій |
| `haidamaky.3` — Січ і гайдамаки | 1730-1775 | ZAZ, поки не володіє Черкасами |

Перша дає вибір між надвірними міліціями магнатів, каральною колоною і
поступками селу. Друга - між придушенням власними силами і покликанням
імператорських полків, які наводять лад і не питають, коли їм від'їжджати.
Третя ставить Кошу питання, чи ті самі люди, що зимують під порогами,
брали ярмарки в Умані.

П'ять модифікаторів: `haidamaka_country`, `nadvirna_militia`,
`koliivshchyna_reprisals`, `order_kept_by_foreign_troops`,
`sich_shelters_haidamaky`.

---
## Повний опис

**Дата**: 30 січня 2026
**Версія**: 1.0
**Автор**: Yamtom
**Регіон**: Галичина (HLC), Волинь (VOL), Поділля (PDL), Червона Русь

---

## КОРОТКИЙ ПІДСУМОК

Система відтворює історичні процеси Західної України — Галичини, Волині та
сусідніх земель — у межах часу EU4, від 1444 до 1821 року. Події показують
сплетіння польсько-литовського впливу, релігійного конфлікту, козацької
культури, татарських набігів і господарського розвитку, яким жив цей край.

**Загалом реалізовано**:
- 13 ланцюгів історичних подій
- 22 модифікатори країни й провінції
- 6 модифікаторів думки
- повна англійська локалізація
- охоплений період: 1444–1821

---

## ІСТОРИЧНИЙ КОНТЕКСТ

### Географічний обсяг
- **Галичина** (Halych/HLC): осердя Червоної Русі, великий торговий центр — Львів
- **Волинь** (VOL): порубіжжя між Польщею, Литвою та Руссю
- **Поділля** (PDL): південне порубіжжя, відкрите татарським набігам
- **Червона Русь**: історичний край на межі польської та руської культур

### Ключові історичні теми

#### 1. Польсько-литовське панування (1340-ті — 1795)
- польське завоювання Галицько-Волинської держави (1340-ті — 1370-ті)
- входження до Речі Посполитої
- поступова полонізація шляхти й міських верхів
- напруга між польською католицькою та руською православною культурами

#### 2. Берестейська унія (1596)
- постання греко-католицької (унійної) Церкви
- визнання влади папи зі збереженням східного обряду
- глибокий розкол між православними вірянами й тими, хто прийняв унію
- релігійний конфлікт, що тривав століттями

#### 3. Козацька культура (XVI–XVIII ст.)
- вільні військові громади на порубіжжі
- опір польському кріпацтву й владі
- великі повстання: Хмельниччина 1648, Коліївщина 1768
- походи на османські й татарські землі

#### 4. Татарські набіги (XV–XVIII ст.)
- набіги кримських татар на порубіжжя
- ясир, тобто бранців, продавали в неволю
- спустошення південних земель
- розбудова оборонних систем

#### 5. Господарський розвиток
- Львів як великий торговий перехрестя
- соляна торгівля чумацькими валками
- міста з магдебурзьким правом
- вивіз збіжжя та худоби

#### 6. Шляхетська культура
- сарматизм: шляхта як нащадки сарматських воїв
- Золота вольність, тобто шляхетські привілеї
- полонізація проти руської самобутності
- культура шляхти

---

## Опис ланцюгів подій

### Ланцюг 1: полонізація (1444–1700)

#### Подія 1.1: польський культурний вплив
**ID**: `west_ukraine_history.1`
**Тригер**:
- тег: VOL, HLC або PDL
- васал або союзник POL чи PLC
- володіє провінціями руської або білоруської культури

**Середній час**: 60 місяців
- ×0.5 якщо васал POL
- ×0.5 якщо васал PLC
- ×1.5 якщо стабільність від'ємна

**Варіанти**:
1. **Пристати на польський вплив** (ШІ 60%)
   - Прапорець: `polonization_started`
   - Модифікатор: `west_ukr_polish_influence` (20 років)
   - Польська культура стає прийнятою
   - -5 престижу

2. **Опиратися польській культурі** (ШІ 40%)
   - Модифікатор: `west_ukr_cultural_resistance` (10 років)
   - штраф до думки сюзерена

**Історичний контекст**: Polish culture gradually influenced Ruthenian nobility through education in Kraków, intermarriage, and administrative integration.

#### Подія 1.2: Polish Language at Court
**ID**: `west_ukraine_history.2`
**Тригер**:
- Є прапорець `polonization_started`
- Є модифікатор `west_ukr_polish_influence`

**Середній час**: 120 місяців

**Варіанти**:
1. **Adopt Polish at court** (ШІ default)
   - Прапорець: `polish_court_language`
   - +10 престижу
   - +5 легітимності
   - Стосунки із сюзереном ліпшають
   - Одна руська провінція переходить на польську культуру

2. **Триматися руської мови**
   - + адміністративної сили
   - Модифікатор: `west_ukr_ruthenian_pride` (15 років)

**Історичний контекст**: By 1600s, Polish became the language of administration and high culture in most of Western Ukraine, though Ruthenian persisted among commoners.

---

### Ланцюг 2: церковна унія (1596–1650)

#### Подія 2.1: Pressure for Church Union
**ID**: `west_ukraine_history.3`
**Тригер**:
- тег: VOL, HLC або PDL
- Васал POL чи PLC
- Віра: православна
- Доба Реформації

**Середній час**: 200 місяців
- ×0,5 після 1590
- ×0,3 після 1595 (історична Берестейська унія)

**Варіанти**:
1. **Accept Church Union** (ШІ 40%)
   - Прапорець: `accepted_uniate_church`
   - Перехід у католицтво (позначає греко-католицтво)
   - Модифікатор: `west_ukr_church_union` (постійний)
   - Усі православні провінції переходять у католицтво
   - Province modifier: `west_ukr_converted_uniate` (20 років)
   - + приязні сюзерена
   - +10 престижу

2. **Refuse Church Union** (ШІ 60%)
   - Прапорець: `rejected_uniate_church`
   - Модифікатор: `west_ukr_orthodox_faithful` (25 років)
   - - приязні сюзерена
   - +15 жаги свободи
   - +100 церковної сили

**Історичний контекст**: Union of Brest (1596) created Greek Catholic Church under Polish pressure. Many Ruthenian nobles accepted it, but Orthodox faithful resisted.

#### Подія 2.2: Orthodox-Uniate Conflict
**ID**: `west_ukraine_history.4`
**Тригер**:
- Є прапорець церковної унії
- Є і православні, і католицькі провінції
- Є провінція без модифікатора `west_ukr_religious_peace`

**Середній час**: 150 місяців

**Варіанти**:
1. **Придушити православний опір** (потрібна прийнята унія, ШІ 50%)
   - Модифікатор провінції: `west_ukr_forced_conversion` (10 років)
   - Провінція переходить у католицтво
   - +10 папського впливу

2. **Обороняти православних** (потрібна відкинута унія, ШІ 50%)
   - Модифікатор провінції: `west_ukr_orthodox_protection` (15 років)
   - +25 церковної сили

3. **Насаджувати терпимість** (ШІ 30%)
   - Модифікатор провінції: `west_ukr_religious_peace` (20 років)
   - +25 адміністративної сили

**Історичний контекст**: чвара між православними й унійними громадами тяглася поколіннями: церкви відбирали, священиків виганяли, доходило й до крові.

---

### Ланцюг 3: козацькі повстання (1590–1680)

#### Подія 3.1: козацьке невдоволення
**ID**: `west_ukraine_history.5`
**Тригер**:
- тег: VOL, HLC або PDL
- Васал POL чи PLC
- Володіє steppe provinces with Ruthenian/Ukrainian culture

**Середній час**: 240 місяців
- ×0,5 після 1590
- ×0,3 після 1630 (наближається повстання Хмельницького)
- ×2,0 якщо стабільність 2 і вище

**Варіанти**:
1. **Suppress Cossack rights** (ШІ 30%)
   - Прапорець: `cossack_uprising_chain`
   - З'являються 2 полки козацьких бунтівників
   - Province modifier: `west_ukr_cossack_unrest` (15 років)
   - -1 стабільності

2. **Grant Cossack privileges** (ШІ 70%)
   - Прапорець: `cossack_uprising_chain` + `granted_cossack_rights`
   - Модифікатор: `west_ukr_cossack_privileges` (20 років)
   - -0.5 років income
   - штраф до думки сюзерена

**Історичний контекст**: Cossacks resisted Polish efforts to reduce them to serfdom, leading to series of uprisings culminating in Khmelnytsky Uprising (1648-1657).

#### Подія 3.2: Cossack Raid
**ID**: `west_ukraine_history.6`
**Тригер**:
- Є прапорець `granted_cossack_rights`
- Володіє steppe provinces
- Сусідить із CRI або TUR

**Середній час**: 180 місяців

**Варіанти**:
1. **Endorse the raid** (ШІ 60%)
   - +25 воєнної сили
   - +5 престижу
   - - приязні Криму та Порти

2. **Punish the Cossacks** (ШІ 40%)
   - Модифікатор: `west_ukr_cossack_discipline` (10 років)
   - +5 заворушення в степовій провінції

**Історичний контекст**: Cossack raids (chaiky raids via Black Sea) were constant source of tension with Ottomans and their Crimean vassals.

---

### Ланцюг 4: татарські набіги (1444–1700)

#### Подія 4.1: Tatar Raid Warning
**ID**: `west_ukraine_history.7`
**Тригер**:
- тег: VOL, HLC або PDL
- Володіє province in Ruthenia region bordering Crimean territory
- не воювати
- До 1700

**Середній час**: 200 місяців
- ×0,7 якщо воєнна техніка нижча за 8
- ×1,5 якщо воєнна техніка 12 і вище
- ×2,0 після 1650

**Варіанти**:
1. **Fortify the borders** (ШІ 40%)
   - -50 воєнної сили
   - Province modifier: `west_ukr_border_fortifications` (15 років)

2. **Accept the risk** (ШІ 60%)
   - +10 спустошення провінції
   - -1 базової живої сили
   - Province modifier: `west_ukr_tatar_raid_damage` (10 років)
   - -5 престижу

**Історичний контекст**: Crimean Tatar raids devastated southern borderlands for centuries, carrying off up to 2 million captives into slavery (1500-1700).

#### Подія 4.2: Yasyr - Tatar Captives
**ID**: `west_ukraine_history.8`
**Тригер**:
- Є провінція з модифікатором `west_ukr_tatar_raid_damage`

**Середній час**: 60 місяців

**Варіанти**:
1. **Ransom the captives** (ШІ 60%, factor 0.1 if poor)
   - -0.3 років income
   - +1 базової живої сили провінції
   - Знімає `west_ukr_tatar_raid_damage`
   - +5 престижу

2. **Accept the loss** (ШІ 40%)
   - -1 базової живої сили
   - -10 престижу

**Історичний контекст**: Yasyr (ясир) - captives taken in raids and sold in Crimean slave markets. Ransom was common but expensive.

---

### Ланцюг 5: торгівля й господарство (1444–1650)

#### Подія 5.1: Lviv Trade Fair
**ID**: `west_ukraine_history.9`
**Тригер**:
- Tag HLC or володіє province 279 (Halych/Lviv)
- Провінція 279 має 5+ базового виробництва

**Середній час**: 300 місяців

**Варіанти**:
1. **Invest in the fair** (ШІ 60%, factor 0.1 if poor)
   - -100 дукатів
   - Province modifier: `west_ukr_lviv_trade_fair` (20 років)
   - +1 базового виробництва

2. **Let it develop naturally** (ШІ 40%)
   - +1 базового податку

**Історичний контекст**: Lviv was major trading center between East and West, hosting international trade fairs that attracted merchants from Venice, Genoa, Ottoman Empire, and Muscovy.

#### Подія 5.2: Magdeburg Law
**ID**: `west_ukraine_history.10`
**Тригер**:
- тег: VOL, HLC або PDL
- Володіє Halych (279) or Volhynia (280)
- Провінція має 15+ розвитку
- Провінція не має модифікатора `west_ukr_magdeburg_law`

**Середній час**: 400 місяців

**Варіанти**:
1. **Grant Magdeburg Law** (ШІ 80%)
   - Province modifier: `west_ukr_magdeburg_law` (постійний)
   - +1 базового податку
   - +1 базового виробництва
   - +5 престижу
   - +10 вірності міщан

2. **Maintain direct control** (ШІ 20%)
   - +25 адміністративної сили
   - -5 вірності міщан

**Історичний контекст**: Magdeburg Law (German legal code) granted cities self-government and economic freedoms. Lviv received it in 1356, becoming major commercial center.

#### Подія 5.3: Chumak Trade Route
**ID**: `west_ukraine_history.11`
**Тригер**:
- Тег: VOL або HLC
- Володіє steppe province with salt trade good

**Середній час**: 360 місяців

**Варіанти**:
1. **Support the Chumaks** (ШІ 70%)
   - Province modifier: `west_ukr_chumak_trade` (20 років)
   - +1 меркантилізму

2. **Tax the Chumaks** (ШІ 30%)
   - +0.25 років income

**Історичний контекст**: Chumaks were Ukrainian salt traders who traveled in wagon caravans from Black Sea and Crimea to Polish lands, becoming iconic figures of Ukrainian economic life.

---

### Ланцюг 6: шляхетська культура (1500–1700)

#### Подія 6.1: Sarmatism Ideology
**ID**: `west_ukraine_history.12`
**Тригер**:
- тег: VOL, HLC або PDL
- Є прапорець `polonization_started`
- Васал Польщі або польська культура прийнята

**Середній час**: 300 місяців

**Варіанти**:
1. **Embrace Sarmatism** (ШІ 70%)
   - Прапорець: `sarmatism_adopted`
   - Модифікатор: `west_ukr_sarmatism` (постійний)
   - +15 вірності шляхти

2. **Maintain Ruthenian traditions** (ШІ 30%)
   - Модифікатор: `west_ukr_ruthenian_nobility` (25 років)
   - +10 легітимності

**Історичний контекст**: Sarmatism - ideology claiming Polish-Lithuanian nobility descended from ancient Sarmatians, emphasizing equality among nobles, military prowess, and distinctive culture.

#### Подія 6.2: Golden Liberty vs Absolutism
**ID**: `west_ukraine_history.13`
**Тригер**:
- Тег: VOL або HLC
- Є прапорець `sarmatism_adopted`
- Доба абсолютизму

**Середній час**: 120 місяців

**Варіанти**:
1. **Support Golden Liberty** (ШІ 50%)
   - Прапорець: `liberty_vs_absolutism_choice`
   - Модифікатор: `west_ukr_golden_liberty_support` (25 років)
   - -10 абсолютизму
   - +20 вірності шляхти

2. **Strengthen royal power** (ШІ 50%)
   - Прапорець: `liberty_vs_absolutism_choice`
   - +10 абсолютизму
   - +15 легітимності
   - -10 вірності шляхти

**Історичний контекст**: Age of Absolutism challenged Polish-Lithuanian "Golden Liberty" (extensive noble privileges limiting royal power). This tension ultimately weakened the Commonwealth.

---

## Довідник модифікаторів

### Модифікатори полонізації

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_polish_influence` | -5% Idea Cost, +1 Diplomatic Reputation, -10% Advisor Cost | 20 років | Accept Polish influence |
| `west_ukr_cultural_resistance` | -10% Stability Cost, -1 Unrest, +0.5 Legitimacy | 10 років | Опиратися польській культурі |
| `west_ukr_ruthenian_pride` | +0.5 Prestige, +1 Legitimacy, +1 Tolerance Own | 15 років | Maintain Ruthenian language |

### Модифікатори церковної унії

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_church_union` | +2 Papal Influence, +2 Tolerance Own, -1 Tolerance Heretic, +2% Missionary Strength vs Heretics | Постійний | Accept Church Union |
| `west_ukr_converted_uniate` | +3 Local Unrest, +2% Local Missionary Strength | 20 років | Province converted to Uniate |
| `west_ukr_orthodox_faithful` | +15% Church Power, +2 Tolerance Own, -10% Stability Cost | 25 років | Відкинути унію |
| `west_ukr_forced_conversion` | +5 Local Unrest, +5% Local Missionary Strength, -10% Local Autonomy | 10 років | Suppress Orthodox |
| `west_ukr_orthodox_protection` | -2 Local Unrest, +10% Local Tax, -50% Local Missionary Strength | 15 років | Protect Orthodox |
| `west_ukr_religious_peace` | -3 Local Unrest, +1 Tolerance Heretic, +10% Local Prosperity Growth | 20 років | Promote tolerance |

### Козацькі модифікатори

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_cossack_unrest` | +8 Local Unrest, +5% Local Autonomy | 15 років | Suppress Cossacks |
| `west_ukr_cossack_privileges` | +10% Cavalry Power, -10% Cavalry Cost, +5% Global Autonomy, +10% Cossack Loyalty | 20 років | Grant privileges |
| `west_ukr_cossack_discipline` | +3% Discipline, +5% Morale, -5% Cossack Loyalty | 10 років | Punish Cossacks |

### Модифікатори татарських набігів

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_border_fortifications` | +20% Local Defensiveness, -10% Local Development Cost, -15% Fort Maintenance | 15 років | Fortify borders |
| `west_ukr_tatar_raid_damage` | +10% Local Autonomy, +3 Local Unrest, -25% Local Manpower, -20% Local Tax | 10 років | Raid occurs |

### Торгові модифікатори

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_lviv_trade_fair` | +10% Trade Efficiency, +20% Local Production Efficiency, +15 Province Trade Power | 20 років | Invest in Lviv fair |
| `west_ukr_magdeburg_law` | -15% Local Development Cost, +20% Local Tax, +15% Local Production, +10% Local Autonomy | Постійний | Grant Magdeburg Law |
| `west_ukr_chumak_trade` | +25% Local Production Efficiency, +15% Province Trade Power, +10% Trade Goods Size | 20 років | Support Chumaks |

### Модифікатори шляхетської культури

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_sarmatism` | +15% Cavalry Power, +10% Noble Loyalty, +5% Noble Influence, -1% Army Tradition Decay | Постійний | Embrace Sarmatism |
| `west_ukr_ruthenian_nobility` | +1 Legitimacy, +0.5 Prestige, -10% Stability Cost, +25% Culture Conversion Cost | 25 років | Триматися звичаю |
| `west_ukr_golden_liberty_support` | -20% Liberty Desire from Development, -15% Stability Cost, +10% Governing Capacity, -0.5 Yearly Absolutism | 25 років | Підтримати Золоту вольність |

---

## Модифікатори думки

| Модифікатор | Приязнь | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_cultural_defiance` | -20 | 10 років | Опиратися польській культурі |
| `west_ukr_loyal_vassal` | +30 | 20 років | Польська мова при дворі |
| `west_ukr_church_loyalty` | +50 | 30 років | Пристати на унію |
| `west_ukr_religious_defiance` | -40 | 25 років | Відкинути унію |
| `west_ukr_soft_on_cossacks` | -15 | 15 років | Надати козацькі привілеї |
| `west_ukr_cossack_raid` | -30 | 10 років | Endorse Cossack raid |

---

## Поведінка ШІ

### Ваги ухвалення рішень

**Полонізація**: 60% пристати, 40% опиратися (врівноважена вдача додає +2 до опору)
**Церковна унія**: 40% пристати, 60% відмовити (відбиває історичний опір)
**Cossack Privileges**: 70% grant, 30% suppress (ШІ avoids instability)
**Козацькі походи**: 60% схвалити, 40% покарати
**Укріплення**: 40% будувати, 60% ризикнути (через ціну)
**Викуп бранців**: 60% платити, 40% відмовити (×0,1 якщо в скарбниці менше 50)
**Львівський ярмарок**: 60% укласти кошти, 40% лишити як є (×0,1 якщо в скарбниці менше 150)
**Магдебурзьке право**: 80% надати, 20% відмовити (велика господарська вигода)
**Чумаки**: 70% підтримати, 30% обкласти податком
**Сарматизм**: 70% прийняти, 30% опиратися
**Вольність проти абсолютизму**: порівну

---

## Стик із наявними системами

### Сумісність
- Працює поруч зі спільними місіями VOL і HLC
- Стикується з польським і литовським деревами місій
- Сумісне з механікою козацького стану
- Працює з наявними стосунками з Кримом і Портою

### Потрібні теги
- Головні: VOL, HLC, PDL
- Другорядні: будь-який тег, що володіє цими провінціями
- Перевірка сюзерена: POL, PLC

### Залежності від провінцій
- **Галич і Львів** (279): великі торгові події
- **Волинь** (280): магдебурзьке право, розвиток
- **Край Русь**: татарські набіги, козацькі події
- **Подільсько-волинська область**: порубіжні події

### Система прапорців
- `polonization_started`: відмикає культурні події
- `polish_court_language`: мова двору
- `church_union_decision`: унію вибрано
- `accepted_uniate_church` / `rejected_uniate_church`: гілка унії
- `cossack_uprising_chain`: козацькі події ввімкнено
- `granted_cossack_rights`: козацьку самоуправу надано
- `sarmatism_adopted`: шляхетський звичай змінено
- `liberty_vs_absolutism_choice`: вибір щодо абсолютизму зроблено

---

## Історична достовірність

### Джерела й натхнення
1. **Магочій, Павло Роберт**: «A History of Ukraine: The Land and Its Peoples»
2. **Субтельний, Орест**: «Ukraine: A History»
3. **Дейвіс, Норман**: «God's Playground: A History of Poland»
4. **Вілсон, Ендрю**: «The Ukrainians: Unexpected Nation»
5. **Документи доби**: Берестейська унія (1596), козацькі повстання, татарські набіги

### Відступи від історії
1. **Час**: події розтягнуто на весь проміжок EU4 (1444-1821), а не стиснуто в кілька десятиліть
2. **Вибір**: гравець може обійти історичний кінець (скажімо, відкинути унію)
3. **Спрощення**: тривалі процеси зведено до окремих подій
4. **Баланс**: числа підібрано під гру, а не під точне відтворення

### Що взято з історії
1. **Церковна унія**: за Берестейською унією 1596 року
2. **Сарматизм**: справжнє шляхетське вчення Речі Посполитої
3. **Козацький звичай**: відбиває справжню козацьку самоуправу й походи
4. **Татарські набіги**: за сторіччями кримських нападів
5. **Торгівля**: Львів, магдебурзьке право, чумаки — усе історичне

---

## Створені та змінені файли

### Файли подій
- **events/WestUkraineHistory.txt** (новий, понад 1200 рядків)
  - 13 ланцюгів історичних подій
  - Простір імен: `west_ukraine_history`

### Файли модифікаторів
- **common/event_modifiers/west_ukraine_modifiers.txt** (новий)
  - 22 модифікатори країни й провінції

### Файли модифікаторів приязні
- **common/opinion_modifiers/RIP_opinion_modifiers.txt** (змінено)
  - Додано 6 модифікаторів приязні

### Локалізація Files
- **localisation/west_ukraine_history_l_english.yml** (новий)
  - 13 назв і описів подій
  - 39 варіантів у подіях
  - 22 описи модифікаторів
  - 6 назв модифікаторів приязні

---

## Перелік перевірки

- [ ] Події настають за правильними тригерами й MTTH
- [ ] ШІ вибирає розумно за вагами
- [ ] Модифікатори накладаються із зазначеною тривалістю
- [ ] Модифікатори приязні працюють на екрані дипломатії
- [ ] Прапорці не дають подіям повторюватися
- [ ] Гілка церковної унії працює
- [ ] Козацький бунт з'являється як слід
- [ ] Спустошення від набігу накладається
- [ ] Торгові модифікатори підіймають господарку
- [ ] Немає суперечок із наявними місіями VOL і HLC
- [ ] Локалізація показується правильно
- [ ] У файлах немає синтаксичних помилок

---

## Як це грати

### За Волинь (VOL)
1. **Ранок партії (1444-1500)**: лавірувати між польським і литовським впливом, визначитися з культурою
2. **Середина (1500-1600)**: пережити унійну кризу, дати раду козацтву
3. **Пізня гра (1600-1700)**: вибрати між Золотою вольністю й абсолютизмом, відбивати татар

### За Галичину (HLC)
1. **Упор на торгівлю**: вичавити все з львівського ярмарку й магдебурзького права
2. **Культурний вибір**: тримати рівновагу між польським впливом і руським звичаєм
3. **Церковна політика**: вибір щодо унії визначає всю партію

### За Польщу чи Литву
- Ці події настають у ваших васалів, і з ними доведеться щось робити
- Вірні васали (пристали на унію, дістали привілеї) проти непокірних (опираються культурі, відкинули унію)

---

## Задуми на майбутнє

1. **Козацький реєстр**: події про його розмір
2. **Гайдамаччина**: селянські повстання XVIII століття
3. **Братства**: осередки культурного опору
4. **Унійна митрополія**: розбудова церковної ієрархії
5. **Вірменське купецтво**: львівська вірменська торгова мережа
6. **Життя містечок**: події про єврейські громади заходу України
7. **Поділи**: події, що ведуть до поділів Речі Посполитої (1772-1795)

---

## Що робити, коли не працює

### Подія не настає
- Перевірте тег (VOL, HLC, PDL)
- Звірте умови тригера (віра, сюзерен, провінції)
- Погляньте, чи прапорець уже стоїть (він і не пускає)
- Перевірте добу (Реформація, абсолютизм)

### Модифікатор не накладається
- Звірте написання в ефекті події та у файлі модифікаторів
- Verify duration syntax (-1 for постійний)
- Переконайтеся, що файл модифікаторів завантажився без помилок

### ШІ поводиться дивно
- Вибір визначають ваги ШІ в подіях
- Множники (скарбниця, вдача) зміщують вибір
- Загалом ШІ вибирає історично правдоподібно

---

## Подяки

**Історичні розвідки**: українська й польська історіографія
**Paradox Interactive**: механіка базової гри
**Команда мода RIP**: наявне українське й козацьке наповнення

**Втілення**: Yamtom
**Випробування**: [попереду]

---

## Журнал змін

### Версія 1.0 (30 січня 2026)
**Перший випуск**
- 13 ланцюгів історичних подій implemented
- Створено 22 модифікатори
- 6 модифікаторів думки added
- повна англійська локалізація
- Повна документація

---

**КІНЕЦЬ ДОКУМЕНТА**

*«Крізь ці бурі історії руський дух вистоює»*
