# Система степових набігів

**Стан реалізації:** у скрипті завершено; власні статичні контракти проходять  
**Стан у грі:** димовий прогін запуску й розбору ще попереду  
**Версія гри:** EU4 1.37.5  
**Ревізія документа:** 17 серпня 2026

## Обсяг

Система моделює чотири пов'язані тиски навколо Понтійського степу:

- ординські набіги й захоплення ясиру проти осілих прикордонних держав;
- козацька відплата, зокрема донським і азовським маршрутом;
- кримські набіги на Черкесію й рух бранців через Кафу;
- османська відповідь, коли Крим у грі є османським васалом.

Бранців свідомо абстраговано як дохід, живу силу, спустошення, думку й
тимчасові модифікатори. Ані обліку населення, ані товару-невільника тут немає.
Наслідки подій не претендують на опис конкретного історичного набігу, якщо не
названо джерело; більшість подій — повторювані ігрові абстракції.

Тут **16 подій у семи пов'язаних ланцюгах**, а не 16 окремих ланцюгів.

## Чинні файли

| Роль | Файл |
|---|---|
| Події 1–16 | `events/SteppeRaiding.txt` |
| Спільні ефекти ринку й реакцій | `common/scripted_effects/steppe_raid_effects.txt` |
| Модифікатори подій і провінцій | `common/event_modifiers/steppe_raid_modifiers.txt` |
| Модифікатори думки | `common/opinion_modifiers/RIP_opinion_modifiers.txt` |
| Англійська локалізація | `localisation/zzz_steppe_raiding_l_english.yml` |
| Загальна інтеграція набігів | `events/RaidMechanics.txt` |
| Інтеграція Запорожжя й Гетьманщини | `events/ZaporizhiaFixes.txt`, `events/HetmanateCossackRaids.txt`, `common/scripted_effects/zaz_het_effects.txt` |
| Політика місій щодо Кафи | `missions/Zaporozhie_Missions.txt` (`ZAZ_TUR_slave_trade`) |
| Статичний регресійний контракт | `tests/check_steppe_expansions.py` |

## Ланцюги подій

### 1. Ординський набіг і цикл ясиру (`steppe_raid.1-.5`)

`steppe_raid.1` може спрацювати для CRI, NOG, KAZ, AST, GOL або країни з
реформою степової орди чи Великої Монгольської держави. Колишній запасний
варіант `government_rank = 1` прибрано: він випадково робив набігачем кожну
придатну однопровінційну державу.

Набігач має бути в мирі, мати щонайменше 30% живої сили, вийти з дворічного
відкату й мати придатного сусіда, який не є союзником. Варіант запуску коштує
воєнної сили та доходу, створює однорічну ватагу й кличе `steppe_raid.2` для
відібраного сусіда.

Ціль тоді обирає між:

- витратити воєнну силу на однорічну оборону кордону й відбити набіг;
- прийняти спустошення й дати набігачеві дійти до ясиру.

Модифікатори Глинських, Ягольдая, липків, засічної риси та звичайної оборони
кордону впливають на добір провінції й зменшують шкоду. Успішний продаж ясиру
кличе `rip_feed_kaffa_market_effect`; додатковий ринковий дохід виникає лише
тоді, коли провінція 285 має чинний ліцензований ринок.

Ціль згодом дістає вибір щодо викупу в `steppe_raid.5`. Слід думки послідовно
йде від жертви до набігача, тож `steppe_raid.6` може знайти країну, чиїх людей
справді забрали.

### 2. Козацька відплата (`steppe_raid.6-.7`)

VOL, HLC, PDL, ZAZ, країни з козацьким станом і країни з підтримуваною
козацькою реформою можуть спорядити відплатний набіг на CRI чи NOG після кривди
з ясиром. Ефекти лояльності стану захищено через `has_estate`, тож країна з
козацькою реформою, але без стану, не виконує недійсного ефекту.

Спорядник дістає дворічний відкат. Ціль зазнає обмеженої шкоди провінції, а
козацька країна — невеликий тимчасовий відплатний модифікатор.

### 3. Осідання ногайців і калмиків (`steppe_raid.8-.9`)

Контракт провінцій прив'язано до карти EU4 1.37.5:

- Єдисан (`282`), Буджак (`1756`) і Кубань (`287`) — можливі провінції
  ногайського осідання;
- Астрахань (`464`) і Яїк (`474`) потрібні для калмицької події.

Старі значення `2410`, `2447`, `2416` і `1082` вказували відповідно на Теодоро,
Мантрегу, Маджар і Казань, і ці події їх більше не вживають.

`steppe_raid.8` — одноразова подія після 1500 року для CRI чи TUR, коли NOG зникає.
`steppe_raid.9` is a one-shot 1620-1649 event for MOS/RUS; acceptance changes
the two named provinces and grants the постійний `kalmyk_cavalry` modifier.

### 4. Засічна риса (`steppe_raid.10`)

MOS/RUS at administrative technology 10 can invest in the defensive line when
an owned Russian-region province borders CRI, NOG, or AST. Acceptance grants the
постійний country modifier and applies `zasechnaya_cherta_province` to the
qualifying frontier provinces. Those province modifiers are recognized by the
raid target-selection and damage logic.

### 5. Донський і азовський козацький набіг (`steppe_raid.11-.12`)

There is no separate DON tag in EU4 1.37.5. “Don Host” is therefore represented
by a ZAZ/HET or Cossack-reform country that володіє a province in `lower_don_area`
or `azov_area`. The custom host-name text can display **Don Host** and
**Don Ataman** for a qualifying Cossack government.

The opportunity requires peace, 30% manpower, a valid neighboring CRI, no
alliance or truce, and no active five-year Cossack raid cooldown. Launching the
raid calls the Crimean response and, only if CRI is a TUR subject, requests the
Ottoman reaction.

Крим може оплатити перехоплення на кордоні або прийняти обмежену шкоду.
Захищені провінції дістають пом'якшену гілку. Якщо Крим володіє Кафою і набіг
удався, ліцензований ринок зникає, а на п'ять років настає розлад торгівлі.

### 6. Османська відповідь (`steppe_raid.13`)

Це подія країни, яку можна лише викликати. Вона дійсна тільки коли:

- ROOT — це TUR;
- CRI існує і `CRI = { is_subject_of = ROOT }`;
- FROM — наявний неосманський набігач, не союзний із TUR;
- немає п'ятирічного `ottoman_crimean_reaction_cooldown`.

Відкат накладається в `immediate`, тож жоден варіант не може оновити подію.
Порта може:

1. вимагати сатисфакції, дістаючи захищений `cb_insult` на **60 місяців**, якщо
   немає перемир'я, союзу чи вже чинної копії;
2. витратити дохід, щоб дати CRI п'ять років `ottoman_vassal_support` і живої сили;
3. знехтувати проханням ціною престижу.

Жоден варіант не оголошує війну сам. Трактування кримсько-османських стосунків
як васалітету EU4 — ігрова абстракція, а не твердження, що історично це був
простий васальний договір.

Помічник кличуть донський ланцюг і придатні запорозькі чи гетьманські шляхи
набігів на Крим або Порту. Сама лише наявність TUR його не запускає.

### 7. Черкеський набіг і політика щодо Кафи (`steppe_raid.14-.16`)

У мирі та поза відкатом CRI може вибрати власника земель у `circassia_area`,
який не є союзником, васалом і не має перемир'я. Країну обирають напряму, тож
подія цілі дістає `FROM = CRI` без двозначного стрибка через власника провінції.

Ціль може заплатити воєнною силою за оборону або прийняти обмежене спустошення
й утрату ясиру. Друге винагороджує Крим і кличе помічника постачання Кафи.

`steppe_raid.16` — подія провінції, прив'язана до Кафи (`285`). Її заблоковано,
доки є хоч один із трьох взаємовиключних модифікаторів політики:

- `crimean_yasyr_market` — постійний, доки не розладнано;
- `trade_route_disrupted` — п'ять років після вдалого набігу на ринок;
- `kaffa_ransom_exchange` — десять років від вибору в події.

Варіант постійного ринку видно лише GEN, CRI, TUR, мусульманському власникові
або власникові зі степовою ордою. Для всіх інших безпечним запасним варіантом є
впорядкований викупний обмін.

Місія `ZAZ_TUR_slave_trade` тепер націлена на Кафу (`285`), а не на Азов
(`286`). Завершення прибирає стан ринку чи розладу, встановлює двадцятирічний
викупний обмін, знімає тимчасовий дохід власника з работоргівлі та зберігає
портове й торгове поліпшення місії. Її торговий модифікатор показується як
**Black Sea Ransom Network**.

## Спільні ефекти

### `rip_feed_kaffa_market_effect`

Можна кликати з будь-якої області. Якщо Кафа має `crimean_yasyr_market`, її
власник дістає 0,05 річного доходу і два роки `slave_trade_income`.

### `rip_disrupt_kaffa_market_effect`

Можна кликати з області країни або провінції. Усередині сам визначає провінцію
`285`, прибирає ринок, накладає п'ять років `trade_route_disrupted`, знімає
`slave_trade_income` з власника й коштує йому престижу.

### `rip_request_ottoman_crimean_reaction_effect`

Кличеться в області країни-набігача. Планує `steppe_raid.13` лише тоді, коли
CRI є васалом TUR і TUR вийшов з відкату відповіді. Подія дістає набігача як
FROM.

## Чинні модифікатори

| Модифікатор | Область | Головні ефекти | Типова тривалість |
|---|---|---|---|
| `steppe_raid_party` | country | speed, maintenance, cavalry cost | 1 year |
| `steppe_raid_cooldown` | country | marker | 2 or 5 років by chain |
| `steppe_successful_raid` | country | horde unity, prestige, cavalry | 3-5 років |
| `cossack_raid_cooldown` | country | marker | 2 or 5 років by chain |
| `steppe_border_defense` | province | defense, manpower, attrition | 1-2 років |
| `steppe_raid_devastation` | province | unrest and economic penalties | 2-5 років |
| `cossack_raid_damage` | province | unrest and economic penalties | 3 років |
| `zasechnaya_cherta` | country | attrition, fort upkeep, defense | постійний |
| `zasechnaya_cherta_province` | province | defense, attrition, development | постійний |
| `nogai_settlers` | country | cavalry and manpower recovery | 20 років |
| `kalmyk_cavalry` | country | cavalry and horde unity | постійний |
| `cossack_retaliatory_raid` | country | speed and flanking | 3 років |
| `slave_trade_income` | country | trade bonus, diplomatic penalty | 2 років per feed |
| `crimean_yasyr_market` | province | Kaffa trade/production/tax, unrest | until disrupted |
| `trade_route_disrupted` | province | trade and production penalty | 5 років |
| `kaffa_ransom_exchange` | province | smaller trade/tax bonus, lower unrest | 10 or 20 років |
| `ottoman_vassal_support` | country | maintenance, cavalry, tactics | 5 років |
| `ottoman_crimean_reaction_cooldown` | country | marker | 5 років |

Unused prototype modifiers were removed rather than retained as undocumented
dead content.

## Cross-system cleanup

- `raid_mechanics.1` now treats March and May as alternatives; the former
  impossible month AND is gone.
- `raid_mechanics.2` has a live caller again.
- Chaiky target discovery uses known coastal targets rather than requiring a
  land border with TUR/CRI.
- Province raid weighting checks province modifiers in province scope.
- ZAZ/HET raid flags use a reusable contract: the decision is available when
  the flag has never existed or has aged past its 5/10-year window. The earlier
  inverted `NOT had_country_flag` form is gone.

## Verification

Run from the mod root with a real Python interpreter:

```powershell
python tests/check_steppe_expansions.py
python tests/check_border_principalities.py
python tests/check_clausewitz_braces.py
python tests/check_script_layer.py
```

Current evidence:

- [x] dedicated static expansion contract;
- [x] braces and BOM contract;
- [x] corrected Steppe province IDs;
- [x] event/option/modifier English localisation contract;
- [x] bounded Ottoman CB, cooldown, and no forced war;
- [x] protected-border integration;
- [ ] EU4 startup/parser smoke after these edits;
- [ ] targeted event firing through every option;
- [ ] observer evidence for MTTH frequency and AI choice balance;
- [ ] save/load persistence of постійний and timed modifiers.

Unchecked runtime items are not implied by the implementation-complete status.

## Compatibility and maintenance

- Province IDs and areas are verified against EU4 1.37.5. Recheck them after a
  map-version upgrade.
- `cb_insult`, subject scopes, event FROM, and scripted-effect behavior depend on
  engine semantics; the startup smoke catches parser/load failures but not every
  branch outcome.
- Do not replace the three Kaffa helpers with duplicated inline effects. Their
  explicit province-285 resolution is the scope contract used by all callers.
- Keep `tests/check_steppe_expansions.py` synchronized with any renamed event,
  modifier, mission, or helper.

## Ідеї майбутніх розширень

1. Add a player-facing target selector with cost and risk previews.
2. Add an OPM migration decision with strict anti-exploit checks.
3. Tune MTTH and AI weights from reproducible observer evidence.
4. Add a deeper captive-ransom ledger only if it remains performant and avoids
   presenting speculative population figures as measured history.

## Sources and design notes

The following sources support the broad historical frame; event costs, MTTH,
AI weights, and exact modifiers are game design:

- [“The Consequences of the Black Sea Slave Trade: Long-Run Development in Eastern Europe”](https://www.cambridge.org/core/journals/american-political-science-review/article/consequences-of-the-black-sea-slave-trade-longrun-development-in-eastern-europe/E6074298B3135E3B858CF9E64BE45F99) — Kaffa/Caffa and the Black Sea captive trade.
- [“Cossacks as Captive-Takers in the Ottoman Black Sea Region and Crimea”](https://www.nmc.utoronto.ca/research-publications/faculty-publications/cossacks-captive-takers-ottoman-black-sea-region-and) — Zaporozhian and Don Cossack captive-taking.
- [“The Ottoman Crimea in the Mid-Seventeenth Century: Some Problems and Preliminary Considerations”](https://www.husj.harvard.edu/articles/the-ottoman-crimea-in-the-mid-seventeenth-century-some-problems-and-preliminary-considerations) — damage from Cossack raids and Ottoman-Crimean context.
- [The Crimean Khanate and Ottoman relationship](https://brill.com/view/journals/thr/9/1/article-p86_86.pdf) — reason to document the EU4 subject model as an abstraction.
