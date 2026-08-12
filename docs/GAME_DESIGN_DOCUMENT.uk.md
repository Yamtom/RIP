# Alternative Ruthenian Immersion Pack

## Game Design Document

| Поле | Значення |
|---|---|
| Проєкт | Alternative Ruthenian Immersion Pack (RIP) |
| Гра | Europa Universalis IV |
| Цільова версія | 1.37.5.0 |
| Жанр | Регіональний historical/alternate-history immersion expansion |
| Географічний фокус | Русь, українське пограниччя, Полісся, Карпати, басейни Дніпра й Дністра |
| Стан документа | Production GDD, створений за фактичним inventory репозиторію |
| Canonical root | Корінь репозиторію `RIP/` |

Цей документ описує цільовий ігровий досвід і водночас фіксує різницю між
**реалізованим**, **інтегрованим, але таким, що потребує QA**, та
**запланованим**. Кількості нижче означають визначення у вихідних файлах, а не
обсяг контенту, гарантовано доступний в одному проходженні.

---

# 1. Core vision, історична достовірність та занурення

## 1.1. High concept

RIP — це регіональний immersion expansion, який перетворює Русь із периферії
між Польщею-Литвою, Московією, Кримом, Османською імперією та Габсбургами на
самостійний політичний театр. Гравець не просто фарбує карту: він визначає,
**якою інституційною, конфесійною та культурною моделлю стане Русь у ранньому
Новому часі**.

Основна player fantasy: почати регіональною державою або прикордонною
спільнотою, пережити тиск великих держав і збудувати власний порядок —
князівську федерацію, централізоване царство, козацьку республіку,
старшинську олігархію, конституційну монархію чи багатоконфесійний торговий
простір.

## 1.2. Дизайн-пілари

### Плюральна Русь

Київ, Чернігів, Волинь, Галичина, Поділля, Закарпаття, Полісся, Переяслав і
Запорожжя мають власні державотворчі логіки. Об'єднання не повинно мати одного
«канонічного» московського або польсько-литовського фіналу.

### Пограниччя як система

Степ, Дніпро, Дністер, Карпати та сіверське порубіжжя мають впливати на
демографію, торгівлю, дипломатію й війну. Набіги, ясир, чайки, слободи,
фортеці, міграції, засічні лінії та буферні князівства мають бути пов'язаними
механіками, а не ізольованими подіями.

### Інституції замість пласких бонусів

Ідентичність держави розкривається через місії, реформи, стани, релігії,
disasters, типи підданих і дипломатичні контракти. Сильна нагорода має бути
наслідком рішення та opportunity cost, а не постійним стеком модифікаторів.

### Правдоподібна альтернативна історія

Історичний результат має бути можливим, але не примусовим. Кожний
альтернативний шлях повинен мати реальну вихідну передумову: місцеву
інституцію, претензію, династичний зв'язок, конфесійний конфлікт, торговий
інтерес або геополітичну кризу.

## 1.3. Тон і принципи занурення

- Політичні тексти подають інтереси станів і сусідів, а не сучасну
  національну телеологію.
- Назви, титули та топоніми дотримуються єдиного language style guide:
  `Kyiv`, `Chernihiv`, `Zaporizhia`, `Odesa` в англійській локалізації, з
  окремим правилом для vanilla filename compatibility.
- Спекулятивні гілки на кшталт Kyivan Shogunate або Cesarstvo позначаються в
  tooltip як **Speculative Alternate History**.
- Великі події подають не лише «правильний» вибір, а щонайменше два
  легітимні інституційні інтереси.
- Унікальні механіки повинні бути читабельними без зовнішнього wiki:
  передумова, ціна, тривалість і наслідок показуються у UI.

## 1.4. Framework історичної достовірності

Для кожного великого ланцюга встановлюється один рівень:

1. **Historical** — документовані особа, дата, інституція або війна.
2. **Plausible** — альтернативний результат, що прямо виростає з реальних
   сил та інституцій епохи.
3. **Speculative** — навмисна фантазія для replayability; ніколи не
   маскується під доведений факт.

Definition of done для історичного пакета:

- 2–4 джерела або примітка про джерельну невизначеність;
- допустиме date window;
- географічна перевірка province IDs;
- пояснення абстракцій EU4;
- відсутність анахронічних правителів і династій.

Наявні тематичні джерела проєкту: [прикордонні князівства](BORDER_PRINCIPALITIES_SYSTEM.md),
[степові набіги](STEPPE_RAIDING_SYSTEM.md), [Західну Україну](WEST_UKRAINE_HISTORY.md),
[Російську православну систему](RUSSIAN_ORTHODOX_IMPLEMENTATION.md) і
[пропозиції карти](MAP_REWORK_SUGGESTIONS.md). Їх слід доповнити бібліографією
та відділити джерела від дизайнерських інтерпретацій.

## 1.5. Гравець, кампанія й темп

- **Цільовий гравець:** досвідчений гравець EU4, якому потрібна щільна
  регіональна наративна кампанія.
- **Початок:** локальне виживання, легітимація та відбудова інституцій.
- **Середина:** вибір політичного й конфесійного шляху, боротьба за регіональну
  гегемонію.
- **Пізня гра:** федерація/імперія, модернізація, конституційний або
  автократичний settlement, інтеграція прикордоння.
- **Балансна ціль:** сила держави виникає через послідовний розвиток; один
  ранній reward не повинен одразу давати claims на пів континенту або кілька
  повноцінних idea bonuses.

---

# 2. Новий контент

## 2.1. Зареєстровані нові держави

У canonical root зареєстровано 18 нових тегів:

| Тег | Робоча назва | Фокус кампанії |
|---|---|---|
| VLN | Volyn | волинська регіональна держава |
| HLC | Halych | галицько-карпатська політика |
| UZH | Huszt March / Uzhhorod | русинська ідентичність і угорське пограниччя |
| HET | Hetmanate | козацька держава та еволюція гетьманської влади |
| KUY | Kuyaba | альтернативна київська державність |
| PRL | Pereiaslav | полкова адміністрація й Дніпро |
| PDL | Podillia | прикордонна фортеця, республіка або magnate dominion |
| KRU | Kyivan Confederation | федеративне об'єднання Русі |
| ODS | Odesa | чорноморська торгова держава |
| SMY | Sumy Regiment | слобідський полковий устрій |
| OKH | Okhtyrka Regiment | слобідське прикордоння |
| IZM | Izium Regiment | військова колонізація степу |
| RPS | Polishchuks / Polesia | Полісся та Прип'ятські болота |
| MSK | Minsk | мінський торгово-князівський центр |
| TRV | Turov | давня Турівська земля |
| VTB | Vitebsk | двинська торгівля й північна Русь |
| MSL | Mstislavl | східне білоруське прикордоння |
| BLR | Belarus | об'єднання білоруських земель |

Vanilla-теги `KIE`, `CHR`, `VOL`, `ZAZ`, `UKR`, `PLT`, `MOS/RUS` та російські
князівства отримують розширення або overrides. `KHA` не є новим тегом: у
vanilla він належить Mongol Khanate, тому Харківський полк повинен отримати
інший вільний тег до релізу.

## 2.2. Місійні дерева

У моді 11 mission files, 133 series і 524 визначення місій. Гілки часто
взаємовиключні, тому сума не дорівнює кількості місій одного проходження.

| Файл / напрям | Місій | Дизайнерська роль |
|---|---:|---|
| Chernihiv | 62 | Сіверщина, Ока, grain economy, Крим, Київ, відновлення Русі |
| DOM Russia | 74 | повний тематичний override російського дерева |
| Kyiv | 49 | київська реставрація та KIE/UKR/KRU маршрути |
| Pereiaslav | 20 | полкова адміністрація, Дніпро, зерно, дипломатична спадщина |
| Podillia | 25 | Carpathian Bastion, Frontier Republic, Magnate Dominion |
| Poland/Commonwealth | 10 | польсько-руський і козацький шар PLC |
| Russian Minors | 10 | тематичний override vanilla minors |
| Volhynia/Halych/Volyn | 66 | карпатський, балтійський, австрійський і польський paths |
| Zakarpatta | 50 | Ruthenian, Rusyn та Uhro-Rusyn identities |
| Zaporozhie | 142 | Ottoman, Russian, Horde, Ukrainian та Polish branches |
| Hetmanate | 16 | Khmelnytsky, Mazepa й Rozumovsky arcs |

Окрема 1444 bookmark додає рекомендовані старти, не замінюючи vanilla
bookmarks.

## 2.3. Події та рішення

Поточний inventory:

- 53 event files і 598 top-level events;
- 27 active decision files і 131 decisions;
- 26 country histories, 67 province histories, 4 diplomacy histories,
  8 historical wars та 1 advisor history.

Основні event families:

- Чернігів, підприємництво, pantheon і Ruina;
- Cossack Revolts, Steppe Raiding, chaiky й Zaporizhian Crisis;
- Гетьманщина, succession, Legacy Eras, Moldova та Khmelnytsky;
- Greek Catholic, Russian Orthodox, Raskol, Union of Brest і Crusades;
- Uzhhorod, Volhynia, Galicia, Podillia, Polesia/Belarus;
- Border Principalities, Qasim Khanate, Dniester й Moldavian frontier;
- Kyiv–Dnieper та South/West Ukraine historical packages;
- Women in History — навмисний exact-filename override vanilla, який потребує
  окремого regression review.

Основні decision packages: формування Ruthenia, Hetmanate, Kuyaba,
Volyn–Halych, Polesia та Belarus; київські імперські моделі; Great Rada,
register, chaiky, Sloboda; Podillia paths; Greek Catholic/Russian Orthodox;
Orthodox Crusade; Dniester, Moldova, South Ukraine та eastward expansion.

## 2.4. Системний контент і assets

| Категорія | Поточний обсяг |
|---|---:|
| Government reforms | 85 |
| National idea groups | 18 |
| Disasters | 12 |
| Religions | 2 |
| Church aspect / blessing definitions | 21 |
| Estates | 4 active vanilla-estate overrides |
| Custom estate privileges | 17, з них 4 Jewish/Burgher |
| Great projects | 2 |
| Subject types | 1 (`princedom`) |
| CB / wargoal types | 2 / 2 |
| Event modifier definitions | 1,054 (1,028 unique IDs) |
| Localisation | 42 files, 8,728 key lines; 8,486 use standard indentation |
| Visuals | 23 TGA, 18 DDS, 6 interface GFX, thumbnail |

Усі 18 зареєстрованих нових тегів уже мають прапори. У release assets не
враховуються чотири `.tga.bak`; це резервні копії, а не ігровий контент.

---

# 3. Системи, механіки та зміни

## 3.1. State formation та identity state machine

Country flags, scripted triggers, decisions і mission-refresh events формують
взаємовиключні державні шляхи: Kyivan Rus, федеративна Русь, Cesarstvo,
Sich/Hetmanate, три закарпатські ідентичності, волинські Austrian/Polish paths
і подільські political models. Кожний path повинен мати:

- один canonical activation flag;
- один exit/refresh effect;
- взаємовиключність у potential;
- визначений спосіб переходу тега;
- save/load test і AI fallback.

## 3.2. Степ, набіги та прикордонна колонізація

Цільовий loop: **загроза набігу → оборонна інвестиція → військова відповідь →
демографічний/торговий наслідок**. До нього входять ясир, devastation,
chaiky, register, Great Rada, Sloboda settlement, засічні лінії, калмицькі й
ногайські міграції. Грошова нагорода raids має масштабуватися від доходу та
ризику, а не бути фіксованим раннім джерелом сотень дукатів.

## 3.3. Релігійні моделі

Greek Catholic моделює східний обряд у сопричасті з Римом, Russian Orthodox —
інституціоналізацію патріархату, Third Rome, Symphonia та внутрішній розкол.
Orthodox Crusade розширює конфесійну дипломатію.

У коді існують і `aspects`, і `blessings`, але їхня activation contract ще не
завершена: релігії повинні обрати сумісну з EU4 модель і явно підключити список
механік. Не слід одночасно змішувати Protestant-style aspects і Coptic-style
blessings без підтвердженої підтримки engine.

## 3.4. Уряд, стани та внутрішня політика

Реформи охоплюють князівські assemblies, appanages, Cossack Host, Kosh
elections, Sich brotherhood, Hetman for Life, Starshyna oligarchy, Collegium
control, Podillian, Galician, Volhynian, Pereiaslav і Uzhhorod models.

Jewish economic content інтегровано через чотири Burgher privileges — tax
farming, credit, kahal autonomy й Black Sea networks — а не через окремий
п'ятий estate. Цей підхід зменшує UI-конкуренцію між станами й краще
узгоджується з механіками EU4.

## 3.5. Diplomacy, subjects і прикордонні князівства

`princedom` — автономний неанексований тип підданого для федеративної моделі.
Border Principalities моделюють зміну лояльності Рильська, Глинських,
Яголдая й Сіверщини між Литвою та Московією. Додаткові контури: Qasim Khanate,
Lipka Tatars, Moldavian protectorates і Orthodox coalitions.

## 3.6. Економіка й регіональний розвиток

Ключові economic identities: Dnieper grain exchange, чорнозем, Sloboda,
Dniester estuary, Lviv fairs, Magdeburg Law, Black Sea trade та Jewish credit
networks. Palanok Fortress і Zaporozhian Sich є physical progression anchors.
Monument tiers мають давати 3–6 сфокусованих ефектів, а не окреме друге
національне idea set.

## 3.7. Claims, CB та pacing

Регіональні minor paths мають орієнтир 50–120 permanent-claim provinces за
повний маршрут. Великі `region` rewards дозволені після контролю 40–60%
регіону; ранні або віддалені claims краще робити 25-річними чи замінювати CB.
Особливої ревізії потребують Kyiv/KRU expansion, повні Russia rewards та
далекі Baltic/Scandinavian rewards. PU/vassalization/tributary CB мають бути
обмежені duration, географією та взаємовиключними виборами.

## 3.8. Балансна матриця

Для першого стабільного релізу:

- discipline з одного джерела: здебільшого 2.5–5%;
- administrative efficiency: не більше 5% за один рідкісний late reward;
- yearly patriarch authority: звіряти з vanilla scale (`0.005`, а не `0.5`);
- estate loyalty equilibrium/influence: decimal scale (`0.10`, не `10`);
- permanent global autonomy: обережно, типово не нижче `-0.05` за один source;
- mission reward: стандартно 50–200 mana, 1,200+ лише для унікального
  endgame-моменту з великим opportunity cost;
- попередній tier modifier видаляється перед додаванням наступного.

---

# 4. Технічна імплементація, структура файлів і GitHub workflow

## 4.1. Canonical root і loader contract

Єдиний активний корінь — `RIP/`. Engine-facing файли допускаються лише у
підтримуваних каталогах:

```text
RIP/
├── common/<EU4 subsystem>/
├── customizable_localization/
├── decisions/
├── events/
├── gfx/
├── history/
├── interface/
├── localisation/
├── missions/
├── descriptor.mod
└── thumbnail.png
```

`docs`, tests і tooling не входять до Workshop ZIP. Поточний canonical
release inventory: 415 tracked engine-layer files — `common` 123, `events` 53,
`missions` 11, `decisions` 27, `history` 106, `localisation` 42, `gfx` 45,
`interface` 6 і `customizable_localization` 2. У локальному worktree можуть
залишатися чотири ignored `.tga.bak`, але Git і release archive їх не містять.

## 4.2. Міграція RIP-fresh2

Колишній `RIP-fresh2` був другою повною копією моду в активному корені. EU4
не шукає рекурсивно новий mod root, тому 134 nested-only paths не
завантажувалися, а 240 розбіжних дублікатів не можна було безпечно копіювати
нагору.

Міграцію виконано як Git integration, а не як видалення історії:

```text
archive/pre-flatten-root ───────┐
                               ├─ 1b51af9b (real two-parent merge)
archive/rip-fresh2 @ 07cf176d ─┘
                                      └─ 2691c70a (remove gitlink)
```

Результат:

- nested-only game content інтегрований у canonical root;
- non-conflicting outer fixes збережені three-way merge;
- mode-`160000` gitlink і порожній `RIP-fresh2` прибрані;
- commit вкладеної історії захищений archive-гілкою і merge ancestry;
- reset, force-push і масове перетирання дерева не застосовувалися.

Повний технічний запис: [CANONICAL_ROOT_MIGRATION.md](CANONICAL_ROOT_MIGRATION.md).

## 4.3. Нормалізовані нестандартні каталоги

- `common/blessings` консолідовано в `common/church_aspects`;
- placeholder `common/RIP.txt` відсутній;
- `common/decisions/RussianNation.txt` переміщено до `/decisions` і тепер
  навмисно shadow-ить vanilla filename;
- інертний `common/country_flags/rip_flags.txt` видалено — country flags не
  потребують декларацій;
- `common/modifiers/RIP_VOL_modifiers.txt` видалено після reference audit;
- `restored_ruthenia` розділено на namespaced province/country modifiers у
  `common/event_modifiers`, тому він не конфліктує з vanilla ID і не змішує
  scopes.

## 4.4. Country integrity contract

Кожний новий тег проходить ланцюг:

```text
country_tags mapping
  → common/countries definition
  → history/countries setup
  → gfx/flags/<TAG>.tga
  → country_colors entry
  → TAG / TAG_ADJ localisation
```

CI має відхиляти PR, якщо бракує хоча б одного обов'язкового елемента.
Filename може зберігати vanilla spelling для VFS override, тоді як UI
localisation використовує style guide.

## 4.5. Vanilla override policy

Є два типи зміни:

- **additive content** — унікальний файл/ID, що завантажується поруч із vanilla;
- **override** — той самий virtual filename або semantic ID, який змінює
  vanilla поведінку.

Усі overrides вносяться до allowlist із причиною. Відомі великі кандидати:
`DOM_Russia_Missions`, `TR_Russian_Minors_Missions`, `WomenInHistory`,
`RuthenianNation`, base cultures/governments/estates, province та war history.
`replace_path` використовується лише коли справді треба приховати весь vanilla
каталог; bookmarks залишаються additive.

## 4.6. Branching і pull requests

- `main` — лише release-ready commits;
- `integration/*` — великі міграції та multi-subsystem stabilization;
- `feat/<system>` — новий content;
- `fix/<loader-or-id>` — технічна корекція;
- `balance/<tag-or-system>` — лише числовий баланс;
- `archive/*` — read-only історичні refs, ніколи не джерело release ZIP.

Один PR вирішує одну subsystem-проблему. PR template повинен містити:

- player-facing impact;
- перелік файлів і vanilla overrides;
- migration notes для IDs/flags;
- test matrix і error-log delta;
- screenshots для місій/UI;
- historical sources для нового наративного контенту.

## 4.7. CI та release pipeline

Мінімальні checks:

1. `git diff --check`, відсутність conflict markers.
2. Clausewitz/CWTools parse validation.
3. Duplicate ID і unresolved-reference scans.
4. Tag-integrity check.
5. Localisation: UTF-8 BOM, `l_english:` header, indentation, duplicate keys.
6. Vanilla collision allowlist.
7. Заборона nested `.git`, mode `160000`, nested `descriptor.mod`, невідомих
   loader directories і `.bak` у release.
8. Smoke load, новий `error.log`, save/load і AI observer run.

Release створюється з loader allowlist, має SemVer tag, changelog і ZIP без
`.git`, `.claude`, `.cpatch`, `.venv`, `.pytest_cache`, `.vscode`, `docs`,
tests, diagnostics і backups. Steam item `2563577714` оновлюється тільки з
tagged release. Локальну й Workshop-копію моду не можна активувати одночасно.

---

# 5. Roadmap

## Milestone 0 — Canonical Root Recovery

**Стан: виконано в integration branch.**

- [x] Захистити outer і nested історії archive refs.
- [x] Виконати real two-parent three-way merge.
- [x] Інтегрувати nested-only content у canonical root.
- [x] Прибрати gitlink `RIP-fresh2` без reset/force-push.
- [x] Відновити canonical design docs із pre-flatten history.
- [x] Нормалізувати `common/decisions`, `common/modifiers`,
  `common/country_flags`, `common/blessings` і placeholder `common/RIP.txt`.
- [x] Розділити `restored_ruthenia` за scope та namespace.
- [ ] Пройти smoke-load і regression review перед merge у `main`.

## Milestone 1 — Engine Correctness

**Release blocker.**

- [ ] Призначити Харківському полку вільний тег замість vanilla `KHA`.
- [ ] Виправити mappings або filenames `Chernihiv`, `Kyiv`, `Zaporizhia`,
  `Kharkov_Host`, `Rus`.
- [x] Додати flags для RPS, MSK, TRV, VTB, MSL, BLR.
- [x] Додати RPS/VTB name й adjective localisation та ODS country colour.
- [ ] Консолідувати 26 duplicate event-modifier IDs, 10 opinion IDs і
  duplicate scripted triggers.
- [ ] Завершити aspects/blessings wiring.
- [ ] Виправити mission series/slot collisions і case typo `NOt`.
- [ ] Перевірити всі province IDs та same-ID/different-filename histories.
- [ ] Винести `ZAZ_branch_debug` із release.

Exit criteria: CWTools без parse errors; tag/reference checks зелені; новий
EU4 `error.log` не містить mod-caused engine errors; нова гра та save/load
проходять успішно.

## Milestone 2 — Localisation and Historical QA

- [ ] Уніфікувати BOM/header/indentation за vanilla 1.37.5.
- [ ] Додати стандартний відступ до 242 zero-indented English keys.
- [ ] Консолідувати 706 duplicate English keys і 1,213 redundant occurrences,
  починаючи з тих, що мають різні значення.
- [ ] Виправити malformed localisation і неправильні POL/VIT keys.
- [ ] Завершити EN як source language; позначити FR/DE/ES як partial, доки не
  буде повного покриття.
- [ ] Запровадити topographic/style glossary.
- [ ] Прибрати анахронічні династії та сучасні політичні прізвища.
- [ ] Додати source note й authenticity tier до ключових event chains.

## Milestone 3 — Balance and Pacing Alpha

- [ ] Виправити scale errors loyalty, autonomy, patriarch authority та інші
  значення, що відрізняються від vanilla приблизно у 10–100 разів.
- [ ] Прибрати накопичення permanent tier modifiers.
- [ ] Нормалізувати надсильні ideas, reforms, privileges і Sich monument.
- [ ] Скоротити надмірні mana rewards і income-independent raid payouts.
- [ ] Переглянути KIE/KRU, Russia та long-range claim bursts.
- [ ] Обмежити PU/vassal/tributary CB duration і кількість одночасних цілей.
- [ ] Провести 10 AI observer runs до 1650 та 3 ручні representative campaigns.

## Milestone 4 — Visual and UI Beta

- [ ] Замінити placeholder icons для CHR/UZH missions.
- [ ] Завершити bespoke reform, privilege й event-picture assets.
- [x] Додати відсутні прапори; видалити `.bak` із source/release.
- [ ] Перевірити readability місійних ліній і tooltip completeness.
- [ ] Підготувати Workshop thumbnail, screenshots і feature list.

## Milestone 5 — Map and Late-game Expansion

Після стабілізації script layer: border fixes; Belgorod; Kodak/Dnipro; Bila
Tserkva; Ochakov; Odesa/Khajibey; Chyhyryn; опційно Kremenchuk і Moldova
package. Далі: Old Believers, expanded appanages, Don/Circassian raids,
Ottoman reaction, Kaffa slave market, Haidamaky, Orthodox brotherhoods,
Armenian/Jewish urban networks, partitions і late-game Galicia/Volhynia.

## Release definition of done

Версія готова до публікації, коли advertised systems не просто присутні у
файлах, а **reachable, локалізовані, збалансовані, сумісні із save/load,
працюють для AI та не створюють незадокументованих vanilla overrides**.
