# СЛОБОЖАНЩИНА: ІСТОРИЧНІ ПРОЦЕСИ

## Slobozhanshchyna: Historical Processes

**Дата створення / Created**: 22 лютого 2026 / February 22, 2026  
**Версія / Version**: 1.0  
**Автор / Author**: RIP Mod Development Team  
**Регіон / Region**: Слобожанщина (Харків, Суми, Охтирка, Ізюмська лінія) / Sloboda Ukraine (Kharkiv, Sumy, Okhtyrka, Izium line)

---

## РЕЗЮМЕ / EXECUTIVE SUMMARY

**Українська:**

Ця система відтворює ключові історичні процеси Слобожанщини у 1550-1821 роках: хвилі прикордонного заселення, слобідські привілеї, формування полкового ладу, оборонну лінійну інфраструктуру, експортно-аграрний ріст та поступову інтеграцію в імперські інститути.

**Основні теми:**

- Міграції та слободи як механізм колонізації прикордоння
- Полково-сотенна організація і прикордонна служба
- Харків-Суми-Охтирка як ядро урбанізації та самоврядування
- Чорноземна аграрна спеціалізація та зернові коридори
- Напруга між місцевими вольностями та централізаторськими реформами

**English:**

This system recreates the key historical processes of Sloboda Ukraine in 1550-1821: frontier settlement waves, sloboda charters, regimental governance, fortified line infrastructure, agro-export growth, and gradual integration into imperial institutions.

**Main Themes:**

- Migration and sloboda privileges as colonization tools
- Regimental-hundred military-administrative order
- Kharkiv-Sumy-Okhtyrka as urban self-government core
- Chernozem agrarian specialization and grain corridors
- Tension between frontier liberties and centralizing reforms

---

## ГЕОГРАФІЯ ТА ОПОРНІ ТОЧКИ / GEOGRAPHY AND CORE ANCHORS

**UA (географія):**

- Ключова область: `sloboda_ukraine_area`
- Опорні міста: Харків, Суми, Охтирка
- Суміжні зв'язки: Лівобережжя, Сіверщина, Бєлгородська лінія, Донецький напрям
- Історичний темп: від раннього прикордонного заселення до пізньої бюрократичної інтеграції

**EN (geography):**

- Core area: `sloboda_ukraine_area`
- Anchor cities: Kharkiv, Sumy, Okhtyrka
- Adjacencies: Left Bank, Sivershchyna, Belgorod line, Donets axis
- Historical tempo: from frontier colonization to late bureaucratic integration

---

## ЛАНЦЮГ 1: ПРИКОРДОННЕ ЗАСЕЛЕННЯ / CHAIN 1: FRONTIER SETTLEMENT

### Подія 1.1 / Event 1.1: Хвиля переселенців на Слободи / Migrant Wave into the Slobodas

**ID (пропозиція / proposal):** `sloboda_history.1`

**Тригери / Triggers:**

- 1550-1700
- Володіння щонайменше 2 провінціями в `sloboda_ukraine_area`
- Мир
- Не встановлено прапор первинного заселення

**Опції / Options:**

1. **Відкрити слободи для переселенців / Open Slobodas to Settlers**
   - Розвиток у випадкових провінціях Слобожанщини
   - +жива сила у прикордонній провінції
   - Прапор `sloboda_settlement_wave`
2. **Заселяти через старшину / Settlement Through Starshyna Patronage**
   - Сильніший податковий/продукційний ефект
   - Менша вигода до живої сили
3. **Обмежити переселення / Restrict Inflow**
   - Короткострокова стабільність
   - Втрата довгого потенціалу колонізації

### Подія 1.2 / Event 1.2: Слобідські грамоти / Sloboda Charters Issued

**ID:** `sloboda_history.2`

**Тригери / Triggers:**

- Встановлено `sloboda_settlement_wave`
- Наявність храмів/майстерень/ринків у регіоні (синергія з місією `chr_sloboda_charters`)

**Опції / Options:**

- **Гарантувати податкові пільги / Guarantee Fiscal Privileges**
- **Визнати виборність місцевих урядників / Confirm Elective Local Offices**
- **Уніфікувати статути / Standardize Charters Under Central Chancellery**

**Історичний контекст / Historical Context:**

Слободи як формат пільгового заселення стимулювали оборону, господарський ріст і формування локального самоврядування.

---

## ЛАНЦЮГ 2: ПОЛКОВО-ОБОРОННИЙ КОРДОН / CHAIN 2: REGIMENTAL DEFENSE FRONTIER

### Подія 2.1 / Event 2.1: Полково-сотенна організація / Regimental-Hundred Order

**ID:** `sloboda_history.3`

**Тригери / Triggers:**

- Військова технологія ≥ 7
- Щонайменше 3 провінції в `sloboda_ukraine_area`
- Немає прапора `sloboda_regimental_order`

**Опції / Options:**

- **Підсилити сотенну службу / Strengthen Sotnia Service** (жива сила, професіоналізм)
- **Спиратися на міські гарнізони / Rely on Urban Garrisons** (фортифікаційний ухил)

### Подія 2.2 / Event 2.2: Лінія укріплень на сході / Eastern Fortified Line

**ID:** `sloboda_history.4`

**Тригери / Triggers:**

- Наявність форту в регіоні або місія `chr_belgorod_line`
- Прикордонний ризик (сусідні степові/ворожі держави або низька безпека)

**Опції / Options:**

- **Будувати ланцюг валів і фортець / Build Earthworks and Fort Chain**
- **Ставка на мобільні застави / Invest in Mobile Watchposts**

**Історичний контекст / Historical Context:**

Бєлгородська та Ізюмська лінії у XVII-XVIII ст. були ключовими інструментами протидії набігам і контролю прикордонної мобільності.

### Подія 2.3 / Event 2.3: Перегляд прикордонних статутів / Border Statute Review

**ID:** `sloboda_history.5`

**Тригери / Triggers:**

- Активний модифікатор оборонної лінії
- 10+ років після попереднього перегляду

**Опції / Options:**

- **Поновити вольності служилих громад / Renew Service Privileges**
- **Посилити центральний контроль / Expand Central Oversight**

---

## ЛАНЦЮГ 3: АГРАРНО-ТОРГОВИЙ КОМПЛЕКС / CHAIN 3: AGRO-TRADE COMPLEX

### Подія 3.1 / Event 3.1: Чорноземна спеціалізація / Chernozem Specialization

**ID:** `sloboda_history.6`

**Тригери / Triggers:**

- 1600+
- Щонайменше 3 зернові провінції в регіоні
- Синергія з місією `chr_black_soil_silos`

**Опції / Options:**

- **Силоси та млини / Silos and Mills** (виробництво, товарність)
- **Пасторальна диверсифікація / Pastoral Diversification** (нижчий ризик, помірні бонуси)

### Подія 3.2 / Event 3.2: Харківські ярмарки та контракти / Kharkiv Fairs and Contracting

**ID:** `sloboda_history.7`

**Тригери / Triggers:**

- Провінція Харків під контролем
- Розвинена майстернево-ринкова база

**Опції / Options:**

- **Відкрити регіональний контрактний двір / Open Regional Contract Hall**
- **Залишити роздрібну модель торгівлі / Preserve Local Retail Markets**

**Історичний контекст / Historical Context:**

Мережа ярмарків і контрактів з'єднувала Слобожанщину з Дніпровським і Чорноморським напрямами.

### Подія 3.3 / Event 3.3: Зернові коридори до Дніпра / Grain Corridors to the Dnieper

**ID:** `sloboda_history.8`

**Тригери / Triggers:**

- Прапор `chr_grain_corridors_built` або аналогічний
- Розвинені зернові провінції у `sloboda_ukraine_area`

**Опції / Options:**

- **Інвестувати в логістику / Invest in Logistics**
- **Фіскалізувати експорт / Fiscalize Exports**

---

## ЛАНЦЮГ 4: МІСЬКЕ СУСПІЛЬСТВО ТА ОСВІТА / CHAIN 4: URBAN SOCIETY AND EDUCATION

### Подія 4.1 / Event 4.1: Колегіум і канцелярська культура / Collegium and Chancellery Culture

**ID:** `sloboda_history.9`

**Тригери / Triggers:**

- Адм. тех ≥ 10
- Центр регіону має високий розвиток
- Є інституційний запит на освіту/адміністрування

**Опції / Options:**

- **Інвестувати у братські школи / Invest in Brotherhood Schools**
- **Підтримати службову канцелярію / Expand Service Chancellery**

### Подія 4.2 / Event 4.2: Поліконфесійне прикордоння / Multi-Confessional Frontier

**ID:** `sloboda_history.10`

**Тригери / Triggers:**

- Релігійна неоднорідність у регіоні
- Мир

**Опції / Options:**

- **Компроміс громадам / Community Compromise** (терпимість, нижчий ризик)
- **Уніфікація зверху / Top-Down Uniformity** (швидша централізація, короткочасна напруга)

---

## ЛАНЦЮГ 5: ІНТЕГРАЦІЯ ТА РЕФОРМИ / CHAIN 5: INTEGRATION AND REFORMS

### Подія 5.1 / Event 5.1: Кодифікація слобідської служби / Codification of Sloboda Service

**ID:** `sloboda_history.11`

**Тригери / Triggers:**

- 1700+
- Активні слобідські/полкові модифікатори

**Опції / Options:**

- **Зберегти гібридну модель / Preserve Hybrid Frontier Model**
- **Підпорядкувати загальнодержавному штату / Integrate into Central Service Tables**

### Подія 5.2 / Event 5.2: Губернська перебудова / Governorate Reorganization

**ID:** `sloboda_history.12`

**Тригери / Triggers:**

- 1760+
- Централізаторський вектор держави

**Опції / Options:**

- **Поетапна інтеграція / Gradual Integration**
- **Швидка уніфікація / Rapid Uniformization**

**Історичний контекст / Historical Context:**

У другій половині XVIII ст. регіон інтегрувався у загальноімперські інституції, що послаблювало окремі корпоративні вольності козацького прикордоння.

### Подія 5.3 / Event 5.3: Спадщина Слобідського прикордоння / Legacy of the Sloboda Frontier

**ID:** `sloboda_history.13`

**Тригери / Triggers:**

- Завершено попередні 2-3 ланцюги
- 1780+

**Опції / Options:**

- **Наголос на військовій спадщині / Emphasize Military Legacy**
- **Наголос на місько-економічній спадщині / Emphasize Urban-Economic Legacy**
- **Синтетична модель / Synthesize Frontier and Bureaucratic Traditions**

---

## ВЗАЄМОДІЯ З ПОТОЧНИМ КОНТЕНТОМ / INTEGRATION WITH CURRENT CONTENT

### Уже наявні опори / Existing Anchors

- Місія `chr_sloboda_charters`
- Місія `chr_black_soil_silos`
- Місія `chr_grain_corridors`
- Локалізаційний наратив `chr_flavor.37` (Eastern Frontier Annals)
- Тригери/ефекти з `sloboda_ukraine_area` у scripted triggers/effects

### Принцип інтеграції / Integration Principle

- Не дублювати місійну логіку, а давати подіями фазовий контекст і вибори гравця
- Ключові події мають реагувати на місійні прапори (`chr_grain_corridors_built`, `chr_black_soil_silos_flag`)
- Підсвітити стилі гри: дипломатично-урбаністичний vs мілітарно-прикордонний

---

## МАПА ІМПЛЕМЕНТАЦІЇ / IMPLEMENTATION MAP

### 1) Події / Events

- Файл: `events/SlobodaHistorical.txt`
- Namespace: `sloboda_history`
- Кількість подій: 13 (IDs 1-13)

### 2) Локалізація / Localisation

- Файл: `localisation/sloboda_history_l_english.yml`
- Ключі: `sloboda_history.X.t`, `sloboda_history.X.d`, `sloboda_history.X.a/b/c`
- Додатково: назви модифікаторів і tooltip-рядки

### 3) Модифікатори / Modifiers

- Файл: `common/event_modifiers/00_sloboda_history_modifiers.txt` (або чинний тематичний файл)
- Приклади ключів:
  - `sloboda_settlement_compacts`
  - `sloboda_regimental_chancery`
  - `sloboda_fortified_line`
  - `sloboda_grain_contract_hall`
  - `sloboda_imperial_integration`

### 4) On Actions (опційно) / On Actions (optional)

- Підключення через MTTH або точкові виклики після ключових місій
- М'яка інтеграція: мінімум hard trigger, максимум історично релевантних умов

---

## ІСТОРИЧНІ ОРІЄНТИРИ / HISTORICAL ANCHORS (КОНЦЕПТУАЛЬНО)

**UA (орієнтири):**

- Слобідські полки та вольності як інструмент ранньомодерного frontier-state building
- Хвилі переселення з Правобережжя/Лівобережжя в умовах війни та прикордонного ризику
- Формування ярмаркової і зернової економіки Харківського вузла
- Поступова бюрократизація та уніфікація у XVIII столітті

**EN (anchors):**

- Sloboda regiments and privileges as frontier state-building tools
- Settlement waves driven by war, insecurity, and land opportunities
- Fair-based and grain-export economy centered around Kharkiv
- 18th-century bureaucratization and administrative uniformization

---

## ПІДСУМОК / CONCLUSION

Система Слобожанщини має працювати як регіональний міст між козацькою автономною логікою та імперською централізацією. Її головна цінність у геймплеї — дати гравцю не просто бонуси, а історично вмотивований вибір: утримувати гнучке прикордонне суспільство чи прискорювати інституційне поглинання заради стабільного масштабування держави.
