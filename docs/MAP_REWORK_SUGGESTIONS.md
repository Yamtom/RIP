# Пропозиції з переробки карти для мода RIP
## За пропозиціями fr-rein на форумі Paradox

---

## Стан на 16 серпня 2026 — прочитайте перед плануванням

**Мод не має теки `map/`.** Він не змінює карту взагалі. Усе, що нижче
описано як «додати провінцію», потребує повного шару карти, якого зараз
немає, і зокрема перемальовування `map/provinces.bmp` — растру, де кожна
провінція має унікальний RGB. Це ручна графічна робота; жоден скрипт її не
зробить. Додати рядок у `definition.csv`, не намалювавши пікселі, гірше, ніж
не робити нічого: гра лається на провінцію без пікселів.

`max_provinces` у 1.37.5 дорівнює **4942**, і діапазон зайнятий щільно.
Вільних ID під нові українські провінції в діапазоні 4600–4700 **немає** —
4651–4655 це Цусіма та чотири маньчжурські провінції.

### Що з цього вже намагалися зробити — і що воно поламало

Спроба «зарезервувати» ID під Білу Церкву, Кодак, Кременчук і Дике Поле
пройшла повз карту й лишилася в локалізації, де ключ `PROVnnnn` глобальний:

| Ключ | Мав бути | Насправді перейменовував |
|---|---|---|
| `PROV4651` | Чорнобиль | Цусіма (Японія) |
| `PROV4652` | Біла Церква | Хайчен (Ляонін) |
| `PROV4653` | Кодак | Маолян (Маньчжурія) |
| `PROV4654` | Кременчук | Фуерхе (Маньчжурія) |
| `PROV4655` | Дике Поле | Шілімянь (Маньчжурія) |
| `PROV2405` | Оргіїв | Бендери |
| `PROV2407` | Ніжин | Переяслав — суперечило `province_names` самого мода |
| `PROV4542` | Переяслав | Лубни — те саме |

Це бачив кожен гравець, не лише той, хто грає за Русь. Рядки знято.

Той самий шаблон «послідовні ID лежать поруч» вразив і тегові
`common/province_names/`:

- `UZH.txt` давав закарпатські назви Богемії, Моравії, Пльзеню, Литві,
  Пскову, Мінську, Підляшшю, Бессарабії, двом повітам Китаю, Васіту в Іраку
  та восьми іспанським провінціям. Ужгород, узявши Луго, звав його
  «Воловець». Лишилося два коректні рядки.
- `CHR.txt` звав Твер «Білою Церквою», Москву «Переяславлем», Калугу
  «Миргородом», Брянськ «Гадячем», Пловдив «Конотопом», Черкесію
  «Путивлем», а Мергуї в Бірмі — «Глухівом». Знято дев'ять рядків.

`common/province_names/ruthenian.txt` навмисно перейменовує півсвіту — це
файл за культурою, і ваніль робить так само для російської. Він коректний.

`tests/check_script_layer.py` тепер це стереже: тегові файли перейменувань і
глобальні ключі `PROV` звіряються з `definition.csv`, `area.txt` і
`region.txt` ванілі.

### Три пріоритетні пункти Фази 2 без карти

| Пункт | Що зроблено замість нової провінції |
|---|---|
| **Бєлгород** | Уже представлений: `291` має `capital = "Belgorod"` до 1657 і `"Kharkiv"` після переходу до Росії. Це історично правильна пара — Бєлгород засновано 1596, Харків 1654 — і міняти її не треба. |
| **Кодак / Дніпро** | Форт 1635 року стояв у `290` Полтава, тобто на лівому березі за півтори сотні верст від порогів. Перенесено до `1944` Черкаси: правий берег, Придніпров'я, під Річчю Посполитою з 1569. Це наближення, а не Кодак. |
| **Біла Церква** | Власної провінції немає; вона лежить усередині `280` Київ і `1944` Черкаси. Обидва хибні перейменування знято. Топонім лишається без провінції. |

### Ще три пункти Tier 1–2 без карти

| Пункт | Що зроблено замість нової провінції |
|---|---|
| **Очаків** | `282` Єдисан з 1792 має `capital = "Ochakiv"` — Ясський мир віддає Росії саме Очаківський степ. Для тегу ZAZ провінція зветься «Ochakiv» постійно: це була найближча османська фортеця до Січі. Правопис скрізь приведено до глосарію. |
| **Одеса / Хаджибей** | `282` починає гру як `capital = "Hajibey"`, османський з 1475. Перейменування на Одесу тепер стоїть під **1794**, роком заснування, а не під 1792 — і сходиться з подією `odesa_republic.1`, яка випускає тег ODS у вікні 1794–1806. |
| **Чигирин** | `1944` Черкаси беруть `capital = "Chyhyryn"` у 1648, коли гетьманська столиця переїжджає до маєтків Хмельницького, і повертаються до Черкас **1678.8.12**, коли Чигирин зруйновано остаточно. |

Раніше `282` перейменовувалася на «Ochakov» у 1792 і на цьому спинялася —
тобто Хаджибей ставав Очаковом, хоча Хаджибей став Одесою, а Очаків — це
інше місто за сотню верст. Обидва тепер мають своє місце в хронології однієї
провінції; на окремі провінції вони й далі чекають.

### Кременчук і молдовський пакет

Обидва в цьому документі позначені як бажані, і обидва впираються в те саме.

**Кременчук** власної провінції в 1.37 не має й лежить усередині `290`
Полтави та `1944` Черкас. `PROV4654`, який мав його нести, перейменовував
Фуерхе в Маньчжурії й знято. Без розширення карти зробити з ним нічого не
можна: на відміну від Очакова, Хаджибея й Чигирина, він не має власного
періоду в хронології жодної провінції, який можна було б підписати.

**Молдовський пакет** менший, ніж здається на перший погляд. `moldavia_area`
справді має лише п'ять провінцій - `268` Бессарабія, `1756` Буджак, `2405`
Бендери, `4529` Ясси, `4530` Бирлад - але з трьох запропонованих пунктів
один уже існує: **Тігіна це і є Бендери**, `2405`, просто під турецькою
назвою. Лишаються Хотин і Чернівці, яких у 1.37 немає взагалі, і Сучава -
столиця Молдавського князівства - теж відсутня.

Тобто без карти молдовський пакет зводиться до перейменування `2405` на
Тігіну, і навіть це нікому робити: мод не має молдовського тегу, а
`province_names` працює по тегах і культурах.

Топоніми, що чекають на розширення карти: Біла Церква, Кременчук, Кодак,
Остер, Ніжин, Глухів, Конотоп, Путивль, Миргород, Гадяч, Мукачево, Берегове,
Тячів, Виноградів, Перечин, Рахів, Сколе, Свалява, Ясіня. Очаків, Хаджибей,
Одеса й Чигирин з цього переліку вийшли — вони тепер живуть у хронології
`282` та `1944`, хоча власних провінцій так само не мають.

**Гілки-джерела:**
- [Ruthenia & Cossack Immersion Pack](https://forum.paradoxplaza.com/forum/threads/ruthenia-cossack-immersion-pack.1121263/page-2#post-24736853)
- [Update to Ukrainian Region, Cossacks Content](https://forum.paradoxplaza.com/forum/threads/update-to-ukrainian-region-cossacks-content.1140129/)

---

## Огляд

Документ окреслює пропозиції з переробки карти українського й руського
регіону, спираючись на історичні дослідження та усталені практики картування
в EU4. Пропозиції простягаються від мінімальних правок кордонів до помірного
додавання провінцій і мають краще передати історичну географію й політичну
динаміку 1444–1821 років.

---

## Які проблеми розв'язуються

### 1. **Неточності історичних кордонів**
- **Черкаси**: південний кордон зараз на 50–100 км південніше, ніж має бути, і перетинає історичні межі
- **Стародуб і Трубчевськ**: провінція з підписом «Трубчевськ» насправді містить Стародуб, а справжній Трубчевськ — у Сіверщині
- **Дністер**: русло зміщене, що псує точність молдовсько-руського кордону
- **Десна**: русло не відповідає історичній географії

### 2. **Відсутні історичні міста**
- **Одеса й Хаджибей**: генуезька колонія «Джінестра», великий чорноморський порт, вузол торгівлі
- **Очаків (Özü)**: османська фортеця, ключ до панування на Чорному морі
- **Бєлгород**: татарське поселення Ягольдая, стратегічна прикордонна фортеця
- **Дніпро (Кодак)**: місце Кодацької фортеці — зараз помилково в Полтаві

### 3. **Ігрові проблеми**
- **Дике Поле**: лише одна-дві провінції роблять симуляцію татарських набігів неможливою — один форт блокує все
- **Ліміт козацьких військ**: нинішні 15 провінцій із розвитком близько 80 дають ліміт близько 20 тисяч, тоді як історичні війська Гетьманщини сягали 40–100 тисяч
- **Релігійне навернення**: надто легко перефарбувати карту, не показавши складності унійної Церкви
- **Гетьманщина**: столітня держава, щоформувала історію Східної Європи, ніяк не представлена

---

## Рівні пропозицій

### **Рівень 0: мінімальний — лише правки кордонів, без нових провінцій**

**Головна ціль:** Fix glaring historical errors without adding provinces

#### Зміни:
1. **Cherkasy Border**: Move southern border ~50km north to historical line
   - Rationale: Current border crosses into territory that was part of Wild Field/Ottoman sphere
   - Historical maps show clear demarcation along river systems

2. **Starodub/Trubchevsk**: Split or rename
   - Province labeled "Trubchevsk" → rename to "Starodub"
   - Add actual Trubchevsk in Severia region as separate province (or merge with Sevsk)

3. **Dniester River**: Realign to match historical course
   - Affects Moldova-Ruthenia border
   - Critical for Dniester Estuary mechanics

4. **Severia Area Border**: Adjust to exclude Rylsk, include historical Severian lands
   - Rylsk historically part of Kursk area
   - Severia = Chernigov, Novgorod-Seversky, Starodub core

**Ілюстрація карти:** нульова пропозиція
```
- Cherkasy: Southern border moves north to Ingulets River
- Starodub: Rename current "Trubchevsk" province
- Trubchevsk: Add as small province north of Sevsk OR merge with Sevsk
- Dniester: Realign river course through Moldova
```

---

### **Рівень 1: помірний — 5 нових провінцій**

**Головна ціль:** Add most critical strategic locations while respecting development density concerns

#### Нові провінції:

**1. Belgorod (Province ID TBD)**
- **Розташування:** Between Kursk and Voronezh
- **Історичний контекст:**
  - Jagoldai Tatar settlement (Golden Horde remnant vassal to Lithuania, later Muscovy)
  - Strategic fortress on Zasechnaya Cherta defensive line
  - Border buffer between Lithuania/Muscovy (1444-1494)
- **Геймплей:** Integrates with Border Principalities system (already implemented in mod)
- **Розвиток:** 5-7 (frontier fortress, low population)

**2. Dnipro/Kodak (Province ID TBD)**
- **Розташування:** East bank of Dnieper, north of current Zaporozhia
- **Історичний контекст:**
  - Kodak Fortress (1635) built to suppress Cossacks
  - Future site of Yekaterinoslav (Dnipropetrovsk/Dnipro city)
  - Strategic Dnieper crossing
- **Геймплей:** Correctly places Kodak event target (currently wrongly in Poltava!)
- **Розвиток:** 4-6 (fortress, later grows)

**3. Bila Tserkva (Province ID TBD)**
- **Розташування:** Between Kiev and Cherkasy
- **Історичний контекст:**
  - Ancient Yuriev, renamed after "White Church" ruins
  - Major Right Bank Ukraine city (as large as Kiev in 1444)
  - Key Cossack regiment center
  - On Tatar raid path to Poland
- **Геймплей:** Critical for Khmelnytsky Uprising events, Right Bank Hetmanate mechanics
- **Розвиток:** 8-10 (major city)

**4. Ochakov/Özü (Province ID TBD)**
- **Розташування:** Black Sea coast, Dnieper estuary
- **Історичний контекст:**
  - Ottoman fortress controlling Dnieper-Bug estuary
  - Key naval base for Black Sea dominance
  - Frequently contested (Ottoman-Russian wars, Crimean raids)
- **Геймплей:** Strategic chokepoint for naval/steppe warfare
- **Розвиток:** 6-8 (fortress, small port)

**5. Odesa/Khajibey (Province ID TBD)**
- **Розташування:** Black Sea coast, Dniester estuary
- **Історичний контекст:**
  - Genoa colony "Ginestra" (1440s)
  - Multiple Genoese Black Sea colonies in region
  - Future site of Odessa (major port city)
  - Trade route: Istanbul-Odessa-Krakow-Kiev
- **Геймплей:** Adds historical Center of Trade potential, Genoese colonization flavor
- **Розвиток:** 7-9 (trade colony, grows significantly)

#### Додаткові зміни:
- **Cherkasy**: Border moved north (from Tier 0)
- **Mansur**: Rename to "Bakhmut", adjust borders
- **Yedisan**: Split development with Ochakov/Odesa (currently has unnatural 10-11 dev for empty steppe)

**Map Illustration:** Moderate Proposal (5 New Provinces)
```
Added:
1. Belgorod (Kursk area)
2. Kodak/Dnipro (Wild Field area)
3. Bila Tserkva (Kiev area)
4. Ochakov (Yedisan area)
5. Odesa/Khajibey (Yedisan area)

Total increase: +5 provinces (from ~15 to ~20 in Ukrainian region)
```

---

### **Рівень 2: розширений — 7 нових провінцій**

**Головна ціль:** Full Right Bank Ukraine + Wild Field representation

**Adds to Tier 1:**

**6. Chyhyryn (Province ID TBD)**
- **Розташування:** Right Bank Ukraine, south of Cherkasy
- **Історичний контекст:**
  - Hetmanate capital under Khmelnytsky and successors (1648-1676)
  - Site of major Cossack uprising spark
  - Utterly destroyed after Right Bank collapse
- **Геймплей:** Essential for Hetmanate mechanics, capital of Cossack state
- **Розвиток:** 6-8 (grows to 10+ as capital, devastated in 1670s-1680s)

**7. Kremenchuk (Province ID TBD)**
- **Розташування:** Left Bank Ukraine, Dnieper region
- **Історичний контекст:**
  - Important Left Bank city
  - Cossack regiment center
  - Near-Dnieper economic zone
- **Геймплей:** Fills gap in Left Bank representation
- **Розвиток:** 6-8

**Map Illustration:** Expanded Proposal (7 New Provinces)
```
Tier 1 + Tier 2 additions:
6. Chyhyryn (Right Bank Ukraine area)
7. Kremenchuk (Left Bank Ukraine area)

Total increase: +7 provinces
```

---

### **Рівень 3: повний — 13 нових провінцій, для довідки**

**Примітка:** This tier is from original forum proposals but may be too dense for implementation. Included for historical completeness.

**Additional provinces beyond Tier 2:**
- Korsun (Right Bank Ukraine)
- Myrhorod (Left Bank Ukraine)
- Trubchevsk (Severia - as separate province)
- Sumy (Sloboda Ukraine)
- Izium (Sloboda Ukraine)
- Oril/Pavlograd (Wild Field)
- Zhovti Vody (Wild Field)
- Syni Vody (Wild Field)

**Обґрунтування:** Full historical administrative division representation, optimal for comprehensive Cossack/Tatar raid mechanics

**Concerns:** May be too province-dense compared to surrounding regions

---

## Переробка молдовського регіону

### Поточні проблеми:
- Only 5 provinces for entire historical Moldovan Principality
- Khotyn (major fortress, site of 1621 battle) not represented
- No Bessarabia split (Russian annexation 1812)
- No Bukovina split (Austrian annexation)

### Moderate Proposal (Moldova: +2-3 provinces):

**1. Khotyn/Hotin**
- Strategic fortress on Dniester
- Site of Battle of Khotyn 1621 (Polish-Lithuanian-Cossack victory over Ottomans)
- Frequently switched hands (Moldova-Poland-Ottoman-Russia)

**2. Cernauti/Chernivtsi**
- Northern Bukovina capital
- Became Austrian after partitions
- Important cultural center

**3. Optional: Tighina**
- Dniester crossing fortress
- Importance due to Dniester Estuary (impassable terrain)
- Ottoman strategic holding

### Expanded Proposal (Moldova: +5-7 provinces):
- Above + Orhei, Soroca, Suceava, Bacau, Birlad
- Creates historically accurate 3-region division:
  - **Moldova core** (Iasi, Suceava, Cernauti)
  - **Bessarabia** (Tighina, Orhei, Soroca) - for Russian annexation
  - **Southern Moldova** (Khotyn area) - for Ottoman/Polish contests

**Обґрунтування:** Moldova was powerful in 1444, but fragmented by Ottoman (south), Russian (Bessarabia), and Austrian (Bukovina) partitions. Current 5-province model doesn't allow this historical trajectory.

---

## Переробка Дикого Поля

### Історичний контекст:
**Wild Field (Дике Поле)** = Pontic Steppe region between settled Ruthenia and Crimean/Nogai territories
- Largely unpopulated due to constant Tatar raids (yasyr slave trade)
- Home to Zaporozhian Cossack Sich (nomadic war camps)
- Key transit zone for:
  - Crimean raids into Poland-Lithuania
  - Cossack counter-raids into Crimea
  - Ottoman campaigns northward

### Поточна проблема:
- Only 1-2 provinces represent entire Wild Field
- Single fort completely blocks all raid mechanics
- No space for army maneuvering or historical raid paths
- Zaporozhia Cossacks = 1-province OPM joke instead of major regional power

### Пропозиція:

**Minimum (Tier 1):** Add Kodak/Dnipro province
- Allows basic fort bypassing
- Creates 2-province Wild Field

**Moderate (Tier 2):** Add Kodak + Chyhyryn
- 3-province Wild Field with Right Bank buffer
- Functional raid mechanics possible

**Expanded (Tier 3):** 5-province Wild Field
- Full raid path implementation:
  1. **Zaporozhia**: Sich heartland (existing)
  2. **Kodak**: Dnieper fort zone
  3. **Chyhyryn**: Right Bank transition
  4. **Chornyi Lis**: Black Forest, start of steppe (New Serbia settlement later)
  5. **Syni Vody/Zhovti Vody**: Central steppe, Tatar raid paths

**Development Balance:**
- Wild Field provinces: 3-6 development (empty steppe)
- With Tatar Raid mechanics (implemented in mod), low dev justified by constant devastation
- Later colonization events convert to 8-12 dev (Sloboda Ukraine, Donbass settlement)

---

## Історичні обґрунтування

### Навіщо більше провінцій?

**1. Force Limit Issue:**
Current Hetmanate territory = 15 provinces, ~80 development = ~20k force limit

Historical Hetmanate armies:
- Minimum estimate (Polish treaties): 40,000 regulars
- Battle evidence: 60,000 regulars
- Maximum estimates: 100,000+ (including militia)

**Розв'язання:** More provinces = more development = realistic force limits without breaking ideas/buildings

**2. Religious Conversion:**
- Current: Poland easily converts all Ruthenia to Catholic in 50 років
- Historical: 200 років of Uniate Church compromise, persistent Orthodoxy, religious revolts
- Solution: More provinces = more missionaries needed, slower conversion

**3. Cossack Estate Mechanics:**
- Current: Cossacks only spawn in Steppe terrain (2-3 provinces)
- Historical: Cossacks dominated 20+ provinces in Right Bank, Left Bank, Wild Field
- Solution: More provinces with Cossack estate = historically accurate influence

**4. Tatar Raid Mechanics:**
- Current: Single fort blocks all raids
- Historical: Raids bypassed forts, devastated wide areas, multiple simultaneous paths
- Solution: Multiple provinces with varied terrain = functional raid system (already implemented in mod!)

**5. Hetmanate State Formation:**
- Current: No Hetmanate tag, Khmelnytsky Uprising = generic rebellion
- Historical: Century-long independent Cossack state (1648-1764)
- Solution: Province density supports forming unique Hetmanate with proper borders

---

## Інтеграція з наявними системами мода

### 1. **Steppe Raiding System** (Already Implemented)
- 10 events for yasyr trade, Crimean raids, Nogai/Kalmyk migrations
- **Потрібно від карти:**
  - Multiple Wild Field provinces for raid paths
  - Province modifiers for hostile attrition (Tatar settlements)
  - Zasechnaya Cherta defensive line provinces

**Optimal:** Tier 2-3 Wild Field (5+ provinces)

### 2. **Border Principalities System** (Already Implemented)
- 18 events for Rylsk (Shemyaka), Glinski lands, Jagoldai, Qasim Khanate
- **Потрібно від карти:**
  - Belgorod province (Jagoldai settlement)
  - Rylsk province (Shemyaka descendants)
  - Kursk area adjustments

**Optimal:** Tier 1+ (Belgorod province essential)

### 3. **Cossack Hetmanate Mechanics** (Planned)
- Khmelnytsky Uprising disaster
- Right Bank vs Left Bank Hetmanate split
- Cossack regiment administration
- **Потрібно від карти:**
  - Bila Tserkva, Cherkasy, Chyhyryn (Right Bank centers)
  - Kremenchuk, Poltava, Pereyaslav (Left Bank centers)
  - Zaporozhia, Wild Field (Sich territory)

**Optimal:** Tier 2+ (Chyhyryn capital province essential)

### 4. **Greek Catholic/Uniate Church** (Planned)
- Church Union of Brest (1596) intermediate religion
- Gradual conversion mechanics vs forced conversion
- **Потрібно від карти:**
  - More provinces = slower conversion
  - Western Ukraine vs Eastern Ukraine distinction

**Optimal:** Any tier (more provinces = better)

---

## Рекомендований шлях реалізації

### **Phase 1: Critical Fixes (Tier 0)**
**Зусилля:** Low (border adjustments only)
**Вплив:** High (fixes glaring errors)

- Fix Cherkasy border
- Fix Starodub/Trubchevsk naming
- Realign Dniester River
- Adjust Severia area borders

**Оцінка часу:** 1-2 hours (definition.csv edits)

---

### **Phase 2: Strategic Additions (Tier 1 Partial - 3 provinces)**
**Зусилля:** Medium (3 new provinces)
**Вплив:** High (enables Border Principalities + Steppe Raids)

Priority provinces:
1. **Belgorod** - Essential for Jagoldai/Border Principalities events (already implemented!)
2. **Kodak/Dnipro** - Fixes Kodak fortress misplacement, enables Wild Field raids
3. **Bila Tserkva** - Major city, enables Right Bank Hetmanate events

**Оцінка часу:** 4-6 hours (province creation, history files, localization)

---

### **Phase 3: Full Moderate (Tier 1 Complete - 5 provinces)**
**Зусилля:** Medium-High (2 additional provinces)
**Вплив:** Medium (trade/strategic depth)

Additional provinces:
4. **Ochakov** - Ottoman fortress, Black Sea control
5. **Odesa** - Genoa colony, trade hub, future major port

**Оцінка часу:** 3-4 hours

---

### **Phase 4: Hetmanate Support (Tier 2 - 7 provinces)**
**Зусилля:** High (2 more provinces + Hetmanate mechanics)
**Вплив:** Very High (enables full Hetmanate simulation)

Additional provinces:
6. **Chyhyryn** - Hetmanate capital
7. **Kremenchuk** - Left Bank city

**Оцінка часу:** 6-8 hours (includes Hetmanate government reform, disaster, missions)

---

### **Phase 5: Moldova Rework (Optional)**
**Зусилля:** Medium (2-3 provinces)
**Вплив:** Medium (historical partitions)

Priority:
1. **Khotyn** - Major fortress, battle site
2. **Cernauti** - Bukovina, Austrian partition
3. Optional: **Tighina** - Dniester crossing

**Оцінка часу:** 3-5 hours

---

## Technical Implementation Notes

### Перелік для створення провінції:
- [ ] `definition.csv` - Add province ID, RGB color, province name
- [ ] `default.map` - Update max_provinces, province ranges
- [ ] `area.txt` - Assign provinces to areas
- [ ] `region.txt` - Verify area-to-region assignments
- [ ] `history/provinces/XXXX - Name.txt` - Create province history
  - [ ] Base tax, production, manpower
  - [ ] Culture, religion
  - [ ] Owner, controller
  - [ ] Core, HRE status
  - [ ] Buildings
  - [ ] Trade node
  - [ ] Native size/ferocity/hostileness (if applicable)
- [ ] `localisation/*_l_english.yml` - Add province name, adjective
- [ ] `positions.txt` - Set unit position, text position, port position
- [ ] `climate.txt` - Assign climate (if applicable)
- [ ] `terrain.txt` - Assign terrain type
- [ ] `map/adjacencies.csv` - Add sea connections (if coastal)
- [ ] Graphical map files (if creating actual map mod):
  - [ ] `provinces.bmp` - Paint province with exact RGB
  - [ ] `rivers.bmp` - Add river connections
  - [ ] `terrain.bmp` - Set terrain texture

### Настанови щодо розвитку:
- **Wild Field provinces:** 3-6 base development (devastated by raids)
- **Frontier fortresses:** 5-8 base development (military focus, low population)
- **Major cities:** 8-12 base development (Bila Tserkva, Odesa)
- **Trade colonies:** 7-10 base development (Genoese holdings)

### Настанови щодо культури й релігії:
- **Right Bank Ukraine:** Ruthenian culture, Orthodox religion
  - After 1596: Some provinces convert to Uniate (when implemented)
- **Wild Field:** Ruthenian culture (Cossack settlers), Orthodox
  - Alternative: "Nomadic" or "Cossack" culture variant
- **Genoa colonies:** Italian culture initially, converts to Ruthenian/Turkish
- **Tatar settlements:** Crimean culture, Sunni Islam
- **Frontier zones:** Mixed cultures (represent border dynamics)

---

## Використані історичні джерела

**Мапи:**
- [Hetmanate administrative divisions](https://commons.wikimedia.org/wiki/File:Getmanshchyna.jpg)
- [Oryol Namestnichestvo 1792 with Trubchevsk](https://commons.wikimedia.org/wiki/File:Map_of_Oryol_Namestnichestvo_1792_(small_atlas).jpg)
- [Poland after Truce of Deulino 1618-1619](https://pl.wikipedia.org/wiki/Plik:Truce_of_Deulino_1618-1619.PNG)
- [Poland in 1635](https://upload.wikimedia.org/wikipedia/commons/7/7c/Polish-Lithuanian_Commonwealth_1635.svg)
- [Desna River course](https://commons.wikimedia.org/wiki/File:Desna.png)
- [Sloboda Ukraine development](https://commons.wikimedia.org/wiki/File:Slob_uk_dev.png)
- [Hetmanate in 1648 post-Uprising](https://uk.wikipedia.org/wiki/Файл:Гетьманщина-полки_(за_Кривошеєм).png)

**Книги й статті:**
- Krivosheev's works on Hetmanate administrative structure
- Studies on Cossack regiments and their territories
- Ottoman-Crimean fortification systems
- Genoa Black Sea colonies documentation

---

## Мінімальна альтернатива, якщо додавати провінції небажано

If adding provinces is not feasible, alternative solutions:

### 1. **Development Rebalancing**
- Increase development in existing Ruthenian provinces
- Current ~80 total → Target 120-150 total
- Redistributes from over-developed steppe (Yedisan 10+ dev → 5-6 dev)

### 2. **Special Buildings**
- "Cossack Registry" building: +15% force limit, +10% manpower
- "Sich Camp" building: +20% cavalry combat ability
- Available only in specific provinces (Zaporozhia, Cherkasy, Kiev area)

### 3. **Government Reform Bonuses**
- Hetmanate government: +25% force limit, +0.5 yearly army tradition
- Balances force limit without map changes

### 4. **Area Terrain Changes**
- Change some "plains" to "steppe" or "grasslands" in Wild Field
- Enables Cossack estate expansion without province additions

### 5. **Event-driven Colonization**
- Events that add development over time (1500-1700)
- Simulates Sloboda Ukraine settlement, New Serbia, Novorossiya colonization
- Transforms Wild Field from 4 dev → 10-12 dev provinces

**Примітка:** These are inferior to proper province additions but provide some historical accuracy if map changes impossible.

---

## Висновок

The map rework proposals range from minimal border corrections (Tier 0) to comprehensive historical representation (Tier 3). **Recommended implementation: Tier 1-2** (5-7 new provinces), focusing on:

**Essential:**
- Belgorod (Border Principalities integration)
- Kodak/Dnipro (Wild Field raids, Kodak fortress fix)
- Bila Tserkva (Hetmanate mechanics)

**Highly Recommended:**
- Ochakov (Ottoman fortress)
- Odesa (Genoa colony, trade)
- Chyhyryn (Hetmanate capital)

**Optional:**
- Kremenchuk (Left Bank depth)
- Moldova additions (Khotyn, Cernauti)

**Integration:** All proposals designed to work with already-implemented mod systems (Steppe Raids, Border Principalities) and planned systems (Hetmanate, Uniate Church).

**Historical Accuracy:** All province additions based on:
- Period maps (1444-1821)
- Administrative divisions (Hetmanate regiments, Polish voivodeships, Russian guberniyas)
- Strategic importance (fortresses, battles, capitals)
- Economic significance (trade colonies, river crossings)

**Наступні кроки:**
1. Review proposals with mod team
2. Select implementation tier (recommend Tier 1 minimum)
3. Create province history files
4. Update localization
5. Test integration with existing events
6. Gather playtest feedback on balance

---

**Версія документа:** 1.0
**Дата:** 30 січня 2026
**Author:** Based on fr-rein forum proposals, compiled for RIP mod
**Стан:** пропозиція до впровадження
