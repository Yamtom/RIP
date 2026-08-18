# Інтеграція зі старого мода Ruthenia

**Джерело:** тека `ruthenianew` — мод оновлення українського регіону  
**Дата:** лютий 2026  
**Стан інтеграції:** завершено й перевірено

---

## 1. Вилучена локалізація

### Теги й назви країн
- **HET:** Hetmanate
- **HAL:** Halych
- **HVL:** Halych-Volhynia
- **POD:** Podolia
- **VOL:** Volyn
- **ZAZ:** Zaporozhie

### Historical Province Names (East Slavic)

> **Знято у серпні 2026.** Цей блок був перенесений із legacy-моду разом із
> припущенням, що 4651-4655 - вільні ID під українські провінції. Це не так:
> 4651 - Цусіма, 4652 - Хайчен у Ляоніні, 4653 - Маолян, 4654 - Фуерхе,
> 4655 - Шілімянь. Ключі `PROVnnnn` глобальні, тож маньчжурські й японські
> провінції отримували українські назви для всіх гравців. `2405` - це
> Бендери, а не Оргіїв; `2407` вже Переяслав у ванілі, а `4542` - Лубни,
> тож обидва перейменування суперечили `common/province_names/` самого мода.
>
> Усі вісім рядків видалено з англійської та трьох інших мов.
> `tests/check_script_layer.py` тепер звіряє кожне перейменування з
> `definition.csv` і `region.txt` ванілі.

- ~~**2407:** Nizhyn~~ — 2407 це Переяслав
- ~~**4542:** Pereyaslav (also Lubnie)~~ — 4542 це Лубни
- ~~**4651:** Chornobyl~~ — 4651 це Цусіма
- ~~**4652:** Bila Tserkva~~ — 4652 це Хайчен
- ~~**4653:** Kodak (formerly Oril)~~ — 4653 це Маолян
- ~~**4654:** Kremenchuk~~ — 4654 це Фуерхе
- ~~**4655:** Wild Field (Dikore Pole)~~ — 4655 це Шілімянь
- ~~**2405:** Orhei (Moldavian region)~~ — 2405 це Бендери

---

## 2. Історичні гетьмани та епохи

Внесено до `history/countries/HET - Hetmanate.txt`:

### Раннє козацьке проводирство (1506–1577)
- Lyantskoronsky (1506)
- Kishka (1534)
- Vishnevetsky-Bayda (1550)
- Ivan Svirgovsky (1573)

### Доба Хмельницького (1648)
- **1648.1.25:** Khmelnytsky Uprising  
  - націоналістичні повстанці беруть гору, починається війна
- **1649.8.18:** Treaty of Zboriv  
  - Гетьманщина здобуває формальне визнання
- Доданий модифікатор: **khmelnitsky_uprising**

### Доба Руїни й Дорошенко (1663–1668)
- Pavlo Teteria (1663)
- Petro Doroshenko (1665)
- Доданий модифікатор: **het_divided_state** (Polish-Russian split)

### Золота доба Мазепи (1687–1708)
- **Ivan Mazepa** (1687–1708)  
  - культурне й військове відродження
- Доданий модифікатор: **mazepa_golden_age** (+legitimacy, -idea cost, +global manpower)
- **1708.11.1:** Great Northern War independence attempt

### Після Мазепи: російські репресії (1709–1722)
- Ivan Skoropadsky (1709)
- Доданий модифікатор: **het_russian_repression** (-legitimacy, -diplomatic reputation)
- **1722–1727:** Abolished; Little Russian Collegium installed
  - Доданий модифікатор: **het_little_russian_collegium**

### Пізнє відновлення Гетьманщини (1727–1764)
- Danylo Apostol (1727)
- Kyrylo Rozumovsky (1750, last elected Hetman)
- Доданий модифікатор: **het_reformed_election_system**
- **1764.11.10:** Final abolition of Hetmanate
  - Доданий модифікатор: **het_abolished** (-diplomatic reputation, -legitimacy, +local autonomy)

---

## 3. Бібліотека історичних модифікаторів

Створено у `common/event_modifiers/ruthenian_eastward_modifiers.txt`:

| Модифікатор | Ефекти | Контекст |
|----------|---------|---------|
| **khmelnitsky_uprising** | +ліміт сухопутних військ, +шкода бойовому духу | повстання 1648 |
| **mazepa_golden_age** | +legitimacy, -idea cost, +global manpower | 1687 renaissance |
| **het_ruina_period** | +war exhaustion, +development cost, +global unrest | Civil conflict era |
| **het_divided_state** | -legitimacy, -diplomatic reputation | Poland-Russia split |
| **het_independence_struggle** | +army tradition, +siege ability | Great Northern War |
| **het_russian_repression** | -legitimacy, -diplomatic reputation | Post-1709 subjugation |
| **het_little_russian_collegium** | -administrative efficiency, -diplomatic reputation | Imperial administration |
| **het_reformed_election_system** | +legitimacy, -idea cost, +diplomatic reputation | Late restoration |
| **het_abolished** | -legitimacy, -diplomatic reputation, +local autonomy | 1764 abolition |

---

## 4. Шаблон дипломатичних відносин

Структуру взято з `history/diplomacy/Russian_alliances.txt`:
- Vassal relationships (MOS → PSK, RUS, regional principalities, etc.)
- Royal marriage patterns
- Alliance period dating

**Integration Примітка:** Can be extended for Hetmanate's diplomatic relationships with Poland-Lithuania, Ottoman Empire, and Crimean Khanate.

---

## 5. Руські династичні прізвища

Додано до локалізації:
- Dharynsky
- Vishnevetsky-Bayda
- Khmelnytski
- Teteria
- Doroshenko
- Mazepa
- Skoropadsky
- Apostol
- Rozumovsky

---

## 6. Географічна інтеграція

### Згадані регіони й області
- **Moldavia Area** (moldavia_area) – for Moldova expansion path
- **Black Ruthenia** (black_ruthenia_area) – Podolia and Volyn heartland

### Стратегічні провінції
- Kyiv (280) – capital of religious and cultural gravity
- Poltava (290) – Hetmanate power center
- Chernihiv (289) – northern Rus stronghold
- Lviv (2961) – western Ruthenia
- Zaporozhia (283) – Cossack homeland

---

## 7. Чому цей вміст перевикористано

### Чому саме ці елементи
1. **Localization:** Provides consistent translation and naming conventions across the mod
2. **Historical Accuracy:** Hetmanate eras align with documented succession and treaties
3. **Modifier Framework:** Encodes historical turning points as gameplay consequences
4. **Dynasty Authenticity:** Enables historical ruler flavor and decision chains

### Що виключено
- Full map region/area redefinition (already integrated in V2+)
- Duplicate country file definitions (HET already exists in main RIP mod)
- Overlapping war history (managed separately in mission trees)

---

## 8. Точки інтеграції

### Змінені активні файли
- `localisation/ruthenian_eastward_l_english.yml` – Added all tags, provinces, dynasties
- `common/event_modifiers/ruthenian_eastward_modifiers.txt` – Hetmanate historical modifiers
- `decisions/RuthenianEastwardExpansion.txt` – MOL tag support
- `localisation/replace/zzz_RIP_l_english.yml` – Dynasty names

### Стан перевірки

Перевірено проти коду 2026-08-17, і твердження тримаються:

- усі дев'ять модифікаторів із таблиці вище існують у
  `common/event_modifiers/ruthenian_eastward_modifiers.txt`;
- гетьманські ери справді в `history/countries/HET - Hetmanate.txt`;
- прізвища Дорошенка, Мазепи, Скоропадського й Розумовського є в локалізації.

Єдине, що не витримало перевірки, - блок історичних назв провінцій вище;
він виправлений окремо й позначений закресленням.

✅ **No syntax errors**  
✅ **All modifier keys EU4-valid**  
✅ **All localization keys in place**  

---

## 9. Наступні кроки

**Рекомендовані розширення:**
1. Hetmanate-specific mission tree with Khmelnytsky → Mazepa → Rozumovsky arcs
2. Cossack raid decisions branching from Hetmanate government reform
3. Orthodox crusade integration (Khmelnytsky vs Catholic Poland context)
4. Moldovan expansion via hetmanic support or vassalization

