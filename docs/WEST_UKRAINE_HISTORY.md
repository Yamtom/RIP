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

#### Подія 1.1: Polish Cultural Influence
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
1. **Accept Polish influence** (ШІ 60%)
   - Прапорець: `polonization_started`
   - Модифікатор: `west_ukr_polish_influence` (20 років)
   - Accept Polish culture
   - -5 prestige

2. **Resist Polish culture** (ШІ 40%)
   - Модифікатор: `west_ukr_cultural_resistance` (10 років)
   - штраф до думки сюзерена

**Історичний контекст**: Polish culture gradually influenced Ruthenian nobility through education in Kraków, intermarriage, and administrative integration.

#### Подія 1.2: Polish Language at Court
**ID**: `west_ukraine_history.2`
**Тригер**:
- Has `polonization_started` flag
- Has `west_ukr_polish_influence` modifier

**Середній час**: 120 місяців

**Варіанти**:
1. **Adopt Polish at court** (ШІ default)
   - Прапорець: `polish_court_language`
   - +10 prestige
   - +5 legitimacy
   - Improve relations with overlord
   - One Ruthenian province converts to Polish culture

2. **Maintain Ruthenian language**
   - +ADM power
   - Модифікатор: `west_ukr_ruthenian_pride` (15 років)

**Історичний контекст**: By 1600s, Polish became the language of administration and high culture in most of Western Ukraine, though Ruthenian persisted among commoners.

---

### Ланцюг 2: церковна унія (1596–1650)

#### Подія 2.1: Pressure for Church Union
**ID**: `west_ukraine_history.3`
**Тригер**:
- тег: VOL, HLC або PDL
- Subject of POL/PLC
- Religion: Orthodox
- Age of Reformation

**Середній час**: 200 місяців
- ×0.5 after 1590
- ×0.3 after 1595 (historical Union of Brest)

**Варіанти**:
1. **Accept Church Union** (ШІ 40%)
   - Прапорець: `accepted_uniate_church`
   - Convert to Catholic (representing Greek Catholic)
   - Модифікатор: `west_ukr_church_union` (постійний)
   - All Orthodox provinces convert to Catholic
   - Province modifier: `west_ukr_converted_uniate` (20 років)
   - +Opinion with overlord
   - +10 prestige

2. **Refuse Church Union** (ШІ 60%)
   - Прапорець: `rejected_uniate_church`
   - Модифікатор: `west_ukr_orthodox_faithful` (25 років)
   - -Opinion with overlord
   - +15 liberty desire
   - +100 church power

**Історичний контекст**: Union of Brest (1596) created Greek Catholic Church under Polish pressure. Many Ruthenian nobles accepted it, but Orthodox faithful resisted.

#### Подія 2.2: Orthodox-Uniate Conflict
**ID**: `west_ukraine_history.4`
**Тригер**:
- Has church union flag
- Mix of Orthodox and Catholic provinces
- Province without `west_ukr_religious_peace` modifier

**Середній час**: 150 місяців

**Варіанти**:
1. **Suppress Orthodox resistance** (requires accepted union, AI 50%)
   - Province modifier: `west_ukr_forced_conversion` (10 років)
   - Convert province to Catholic
   - +10 papal influence

2. **Protect Orthodox faithful** (requires rejected union, AI 50%)
   - Province modifier: `west_ukr_orthodox_protection` (15 років)
   - +25 church power

3. **Promote tolerance** (ШІ 30%)
   - Province modifier: `west_ukr_religious_peace` (20 років)
   - +25 ADM power

**Історичний контекст**: Religious conflict between Orthodox and Uniate communities persisted for generations, with churches seized, clergy expelled, and violence common.

---

### Ланцюг 3: козацькі повстання (1590–1680)

#### Подія 3.1: Cossack Discontent
**ID**: `west_ukraine_history.5`
**Тригер**:
- тег: VOL, HLC або PDL
- Subject of POL/PLC
- Володіє steppe provinces with Ruthenian/Ukrainian culture

**Середній час**: 240 місяців
- ×0.5 after 1590
- ×0.3 after 1630 (approaching Khmelnytsky Uprising)
- ×2.0 if stability 2+

**Варіанти**:
1. **Suppress Cossack rights** (ШІ 30%)
   - Прапорець: `cossack_uprising_chain`
   - Spawn 2 regiments of Cossack rebels
   - Province modifier: `west_ukr_cossack_unrest` (15 років)
   - -1 stability

2. **Grant Cossack privileges** (ШІ 70%)
   - Прапорець: `cossack_uprising_chain` + `granted_cossack_rights`
   - Модифікатор: `west_ukr_cossack_privileges` (20 років)
   - -0.5 років income
   - штраф до думки сюзерена

**Історичний контекст**: Cossacks resisted Polish efforts to reduce them to serfdom, leading to series of uprisings culminating in Khmelnytsky Uprising (1648-1657).

#### Подія 3.2: Cossack Raid
**ID**: `west_ukraine_history.6`
**Тригер**:
- Has `granted_cossack_rights` flag
- Володіє steppe provinces
- Neighbor is CRI or TUR

**Середній час**: 180 місяців

**Варіанти**:
1. **Endorse the raid** (ШІ 60%)
   - +25 MIL power
   - +5 prestige
   - -Opinion with Crimea/Ottomans

2. **Punish the Cossacks** (ШІ 40%)
   - Модифікатор: `west_ukr_cossack_discipline` (10 років)
   - +5 unrest in steppe province

**Історичний контекст**: Cossack raids (chaiky raids via Black Sea) were constant source of tension with Ottomans and their Crimean vassals.

---

### Ланцюг 4: татарські набіги (1444–1700)

#### Подія 4.1: Tatar Raid Warning
**ID**: `west_ukraine_history.7`
**Тригер**:
- тег: VOL, HLC або PDL
- Володіє province in Ruthenia region bordering Crimean territory
- не воювати
- Before 1700

**Середній час**: 200 місяців
- ×0.7 if MIL tech < 8
- ×1.5 if MIL tech 12+
- ×2.0 after 1650

**Варіанти**:
1. **Fortify the borders** (ШІ 40%)
   - -50 MIL power
   - Province modifier: `west_ukr_border_fortifications` (15 років)

2. **Accept the risk** (ШІ 60%)
   - +10 devastation to province
   - -1 base manpower
   - Province modifier: `west_ukr_tatar_raid_damage` (10 років)
   - -5 prestige

**Історичний контекст**: Crimean Tatar raids devastated southern borderlands for centuries, carrying off up to 2 million captives into slavery (1500-1700).

#### Подія 4.2: Yasyr - Tatar Captives
**ID**: `west_ukraine_history.8`
**Тригер**:
- Has province with `west_ukr_tatar_raid_damage` modifier

**Середній час**: 60 місяців

**Варіанти**:
1. **Ransom the captives** (ШІ 60%, factor 0.1 if poor)
   - -0.3 років income
   - +1 base manpower to province
   - Remove `west_ukr_tatar_raid_damage`
   - +5 prestige

2. **Accept the loss** (ШІ 40%)
   - -1 base manpower
   - -10 prestige

**Історичний контекст**: Yasyr (ясир) - captives taken in raids and sold in Crimean slave markets. Ransom was common but expensive.

---

### Ланцюг 5: торгівля й господарство (1444–1650)

#### Подія 5.1: Lviv Trade Fair
**ID**: `west_ukraine_history.9`
**Тригер**:
- Tag HLC or володіє province 279 (Halych/Lviv)
- Province 279 has 5+ base production

**Середній час**: 300 місяців

**Варіанти**:
1. **Invest in the fair** (ШІ 60%, factor 0.1 if poor)
   - -100 ducats
   - Province modifier: `west_ukr_lviv_trade_fair` (20 років)
   - +1 base production

2. **Let it develop naturally** (ШІ 40%)
   - +1 base tax

**Історичний контекст**: Lviv was major trading center between East and West, hosting international trade fairs that attracted merchants from Venice, Genoa, Ottoman Empire, and Muscovy.

#### Подія 5.2: Magdeburg Law
**ID**: `west_ukraine_history.10`
**Тригер**:
- тег: VOL, HLC або PDL
- Володіє Halych (279) or Volhynia (280)
- Province has 15+ development
- Province lacks `west_ukr_magdeburg_law` modifier

**Середній час**: 400 місяців

**Варіанти**:
1. **Grant Magdeburg Law** (ШІ 80%)
   - Province modifier: `west_ukr_magdeburg_law` (постійний)
   - +1 base tax
   - +1 base production
   - +5 prestige
   - +10 burgher loyalty

2. **Maintain direct control** (ШІ 20%)
   - +25 ADM power
   - -5 burgher loyalty

**Історичний контекст**: Magdeburg Law (German legal code) granted cities self-government and economic freedoms. Lviv received it in 1356, becoming major commercial center.

#### Подія 5.3: Chumak Trade Route
**ID**: `west_ukraine_history.11`
**Тригер**:
- Tag: VOL or HLC
- Володіє steppe province with salt trade good

**Середній час**: 360 місяців

**Варіанти**:
1. **Support the Chumaks** (ШІ 70%)
   - Province modifier: `west_ukr_chumak_trade` (20 років)
   - +1 mercantilism

2. **Tax the Chumaks** (ШІ 30%)
   - +0.25 років income

**Історичний контекст**: Chumaks were Ukrainian salt traders who traveled in wagon caravans from Black Sea and Crimea to Polish lands, becoming iconic figures of Ukrainian economic life.

---

### Ланцюг 6: шляхетська культура (1500–1700)

#### Подія 6.1: Sarmatism Ideology
**ID**: `west_ukraine_history.12`
**Тригер**:
- тег: VOL, HLC або PDL
- Has `polonization_started` flag
- Subject of or accepted culture Polish

**Середній час**: 300 місяців

**Варіанти**:
1. **Embrace Sarmatism** (ШІ 70%)
   - Прапорець: `sarmatism_adopted`
   - Модифікатор: `west_ukr_sarmatism` (постійний)
   - +15 noble loyalty

2. **Maintain Ruthenian traditions** (ШІ 30%)
   - Модифікатор: `west_ukr_ruthenian_nobility` (25 років)
   - +10 legitimacy

**Історичний контекст**: Sarmatism - ideology claiming Polish-Lithuanian nobility descended from ancient Sarmatians, emphasizing equality among nobles, military prowess, and distinctive culture.

#### Подія 6.2: Golden Liberty vs Absolutism
**ID**: `west_ukraine_history.13`
**Тригер**:
- Tag: VOL or HLC
- Has `sarmatism_adopted` flag
- Age of Absolutism

**Середній час**: 120 місяців

**Варіанти**:
1. **Support Golden Liberty** (ШІ 50%)
   - Прапорець: `liberty_vs_absolutism_choice`
   - Модифікатор: `west_ukr_golden_liberty_support` (25 років)
   - -10 absolutism
   - +20 noble loyalty

2. **Strengthen royal power** (ШІ 50%)
   - Прапорець: `liberty_vs_absolutism_choice`
   - +10 absolutism
   - +15 legitimacy
   - -10 noble loyalty

**Історичний контекст**: Age of Absolutism challenged Polish-Lithuanian "Golden Liberty" (extensive noble privileges limiting royal power). This tension ultimately weakened the Commonwealth.

---

## Довідник модифікаторів

### Модифікатори полонізації

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_polish_influence` | -5% Idea Cost, +1 Diplomatic Reputation, -10% Advisor Cost | 20 років | Accept Polish influence |
| `west_ukr_cultural_resistance` | -10% Stability Cost, -1 Unrest, +0.5 Legitimacy | 10 років | Resist Polish culture |
| `west_ukr_ruthenian_pride` | +0.5 Prestige, +1 Legitimacy, +1 Tolerance Own | 15 років | Maintain Ruthenian language |

### Модифікатори церковної унії

| Модифікатор | Ефекти | Тривалість | Джерело |
|----------|---------|----------|--------|
| `west_ukr_church_union` | +2 Papal Influence, +2 Tolerance Own, -1 Tolerance Heretic, +2% Missionary Strength vs Heretics | Постійний | Accept Church Union |
| `west_ukr_converted_uniate` | +3 Local Unrest, +2% Local Missionary Strength | 20 років | Province converted to Uniate |
| `west_ukr_orthodox_faithful` | +15% Church Power, +2 Tolerance Own, -10% Stability Cost | 25 років | Refuse Church Union |
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
| `west_ukr_ruthenian_nobility` | +1 Legitimacy, +0.5 Prestige, -10% Stability Cost, +25% Culture Conversion Cost | 25 років | Maintain traditions |
| `west_ukr_golden_liberty_support` | -20% Liberty Desire from Development, -15% Stability Cost, +10% Governing Capacity, -0.5 Yearly Absolutism | 25 років | Support Golden Liberty |

---

## Модифікатори думки

| Modifier | Opinion | Duration | Source |
|----------|---------|----------|--------|
| `west_ukr_cultural_defiance` | -20 | 10 років | Resist Polish culture |
| `west_ukr_loyal_vassal` | +30 | 20 років | Adopt Polish at court |
| `west_ukr_church_loyalty` | +50 | 30 років | Accept Church Union |
| `west_ukr_religious_defiance` | -40 | 25 років | Refuse Church Union |
| `west_ukr_soft_on_cossacks` | -15 | 15 років | Grant Cossack privileges |
| `west_ukr_cossack_raid` | -30 | 10 років | Endorse Cossack raid |

---

## Поведінка ШІ

### Ваги ухвалення рішень

**Polonization**: 60% accept, 40% resist (balanced personality +2 to resist)
**Church Union**: 40% accept, 60% refuse (reflects historical resistance)
**Cossack Privileges**: 70% grant, 30% suppress (ШІ avoids instability)
**Cossack Raids**: 60% endorse, 40% punish
**Fortifications**: 40% build, 60% risk (cost consideration)
**Ransom Captives**: 60% pay, 40% refuse (factor 0.1 if treasury < 50)
**Lviv Fair**: 60% invest, 40% natural (factor 0.1 if treasury < 150)
**Magdeburg Law**: 80% grant, 20% refuse (strong economic benefit)
**Chumak Support**: 70% support, 30% tax
**Sarmatism**: 70% embrace, 30% resist
**Liberty vs Absolutism**: 50-50 split

---

## INTEGRATION WITH EXISTING SYSTEMS

### Сумісність
- Works alongside VOL-HLC synergy missions
- Integrates with Polish/Lithuanian mission trees
- Compatible with Cossack estate mechanics
- Works with existing Crimean/Ottoman relations

### Потрібні теги
- Primary: VOL, HLC, PDL
- Secondary: Any tag owning these provinces
- Overlord checks: POL, PLC

### Залежності від провінцій
- **Halych/Lviv** (279): Major trade events
- **Volhynia** (280): Magdeburg Law, development
- **Ruthenia region**: Tatar raids, Cossack events
- **Podolia-Volhynia area**: Border events

### Система прапорців
- `polonization_started`: Triggers cultural events
- `polish_court_language`: Language adoption
- `church_union_decision`: Church Union chosen
- `accepted_uniate_church` / `rejected_uniate_church`: Union path
- `cossack_uprising_chain`: Cossack events active
- `granted_cossack_rights`: Cossack autonomy granted
- `sarmatism_adopted`: Noble culture changed
- `liberty_vs_absolutism_choice`: Absolutism decision made

---

## Історична достовірність

### Джерела й натхнення
1. **Magocsi, Paul Robert**: "A History of Ukraine: The Land and Its Peoples"
2. **Subtelny, Orest**: "Ukraine: A History"
3. **Davies, Norman**: "God's Playground: A History of Poland"
4. **Wilson, Andrew**: "The Ukrainians: Unexpected Nation"
5. **Historical records**: Union of Brest (1596), Cossack uprisings, Tatar raids

### Deviations from History
1. **Timing**: Events spread across EU4 timeframe (1444-1821) vs. concentrated periods
2. **Choice**: Player can avoid historical outcomes (e.g., refuse Church Union)
3. **Simplification**: Complex processes condensed into single events
4. **Game Balance**: Modifiers balanced for gameplay, not perfect historical simulation

### Authentic Elements
1. **Church Union**: Based on real Union of Brest (1596)
2. **Sarmatism**: Authentic noble ideology of Polish-Lithuanian Commonwealth
3. **Cossack Culture**: Reflects actual Cossack autonomy and raiding
4. **Tatar Raids**: Based on centuries of Crimean raids
5. **Trade**: Lviv, Magdeburg Law, Chumaks all historically accurate

---

## FILES CREATED/MODIFIED

### Event Files
- **events/WestUkraineHistory.txt** (new, 1,200+ lines)
  - 13 ланцюгів історичних подій
  - Namespace: `west_ukraine_history`

### Modifier Files
- **common/event_modifiers/west_ukraine_modifiers.txt** (new)
  - 22 модифікатори країни й провінції

### Opinion Modifier Files
- **common/opinion_modifiers/RIP_opinion_modifiers.txt** (modified)
  - Added 6 opinion modifiers

### Локалізація Files
- **localisation/west_ukraine_history_l_english.yml** (new)
  - 13 event titles and descriptions
  - 39 event options
  - 22 modifier descriptions
  - 6 opinion modifier names

---

## TESTING CHECKLIST

- [ ] Events fire with correct triggers and MTTH
- [ ] AI makes reasonable decisions based on weights
- [ ] Modifiers apply correctly with specified durations
- [ ] Opinion modifiers work in diplomacy screen
- [ ] Flags prevent duplicate events
- [ ] Church Union path works correctly
- [ ] Cossack rebellion spawns properly
- [ ] Tatar raid devastation applies
- [ ] Trade modifiers boost economy
- [ ] No conflicts with existing VOL/HLC missions
- [ ] Localization displays correctly
- [ ] No syntax errors in files

---

## RECOMMENDED GAMEPLAY

### As Volhynia (VOL)
1. **Early Game (1444-1500)**: Navigate Polish/Lithuanian influence, decide on cultural identity
2. **Mid Game (1500-1600)**: Handle Church Union crisis, manage Cossacks
3. **Late Game (1600-1700)**: Choose between Golden Liberty and absolutism, deal with Tatar raids

### As Galicia (HLC)
1. **Trade Focus**: Maximize Lviv trade fair and Magdeburg Law benefits
2. **Cultural Choice**: Balance Polish influence vs. Ruthenian identity
3. **Religious Policy**: Church Union decision shapes entire playthrough

### As Poland/Lithuania
- Subject nations will face these events, requiring diplomatic management
- Loyalist vassals (accept union, grant privileges) vs. defiant ones (resist culture, reject union)

---

## FUTURE EXPANSION IDEAS

1. **Cossack Register System**: Events about official Cossack register size
2. **Haydamak Uprisings**: Peasant rebellions (1700s)
3. **Orthodox Brotherhood Movement**: Cultural resistance organizations
4. **Uniate Metropolitanate**: Church hierarchy development
5. **Armenian Merchant Community**: Lviv's Armenian trading network
6. **Jewish Shtetl Life**: Events about Jewish communities in Western Ukraine
7. **Partitions**: Events leading to Polish-Lithuanian partitions (1772-1795)

---

## TROUBLESHOOTING

### Event Not Firing
- Check tag (VOL, HLC, PDL)
- Verify trigger conditions (religion, overlord, provinces)
- Check if flag already set (preventing duplicate)
- Confirm age requirements (Reformation, Absolutism)

### Modifier Not Applying
- Check spelling in event effect and modifier file
- Verify duration syntax (-1 for постійний)
- Confirm modifier file loaded without syntax errors

### AI Behavior Issues
- AI weights in events determine choices
- Factor modifiers (treasury, personality) affect decisions
- AI generally makes historically plausible choices

---

## CREDITS & ACKNOWLEDGMENTS

**Historical Research**: Ukrainian and Polish historiography
**Paradox Interactive**: EU4 base game mechanics
**RIP Mod Team**: Existing Ukrainian/Cossack content

**Implementation**: Yamtom
**Testing**: [Pending]

---

## CHANGELOG

### Version 1.0 (January 30, 2026)
**Initial Release**
- 13 ланцюгів історичних подій implemented
- 22 modifiers created
- 6 модифікаторів думки added
- повна англійська локалізація
- Full documentation

---

**END OF DOCUMENTATION**

*"Through these storms of history, the Ruthenian spirit endures"*
