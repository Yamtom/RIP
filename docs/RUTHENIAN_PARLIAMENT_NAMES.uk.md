# Назви парламентів русинських держав — 19.10.2026

Система найменування для всіх русинських держав і всіх урядових реформ, що дають
парламент. Джерело правил — таблиця `RULES` у `tools/build_parliament_names.py`;
контракт — `tests/check_parliament_names.py`.

## Що було зламано

Три окремі вади; кожна давала гравцеві «не те» або «ніяке» ім'я.

1. **Сирий токен (виправлено 18.10.2026).** У вікні парламенту стояло «Chernihivan
   [Root.GetRIPParliamentName]». Перша система записала команду кастомної локалізації в
   ванільні ключі `<TAG>_parliament_name`. Гра читає ці ключі як простий текст, коли збирає
   заголовок вікна («прикметник + назва»), а команда `[Root.…]` працює лише там, де є область
   дії країни. Тому гравець бачив сирий токен, а не назву.
2. **Випадковий вибір замість першого правила (виправлено 19.10.2026).** Драбину
   `GetRIPParliamentTitle` задумано як «перше правило, що спрацювало», але **EU4 бере перший
   рядок `defined_text` лише з `random = no`**; без нього рушій вибирає між усіма рядками, чия
   умова виконана. Виміряно в EU4 1.37.5: три рядки з `always = yes` — тридцять викликів поспіль
   на одну дату дали другий рядок щоразу, а з `random = no` — перший, тридцять із тридцяти.
   Наслідок у грі: уряд Ради трьох станів дістав «Rada of the Land» (рядок тегу, що стоїть
   нижче за його реформу), а останнє правило `always = yes` (ванільна назва) могло дістатися
   будь-якій русинській державі, — звідси «відсутні назви».
3. **Іменники тегів ховалися за загальними правилами (виправлено 19.10.2026).** Коли жодна
   реформа не називала парламент, русинська республіка одержувала «Veche», а монархія —
   «Rada of the Land» незалежно від тегу: Волинь не була сеймиком, Галич — сеймом, Одеса —
   купецькою радою, хоч таблиця простих іменників (нижче) каже саме так. Тепер між реформами
   й загальними правилами стоять «власні збори держави».

## Як це працює тепер

1. **Заголовок вікна малює скриптовий текст.** `interface/parliament.gui` —
   ванільне вікно, у якому ванільний `title` перенесено за межі вікна (x = −2000), а на
   його місці лежить `rip_parliament_title` (`scripted = yes`, той самий шрифт `vic_29s`,
   ширина 548). Вікно `parliament_window` — підтримуваний хост `custom_gui` з ROOT =
   країна гравця, тож `[Root.GetRIPParliamentTitle]` там виконується.
2. **Одне правило визначає всю назву, і воно перше.** `GetRIPParliamentTitle` (з `random = no`)
   проходить правила зверху вниз; перше, чия умова справджується, дає повну назву. Рівні:
   1. **реформа**, що сама називає парламент (найточніший факт про уряд; реформа може лежати в
      будь-якому ярусі, не обов'язково в тому, що дає парламент);
   2. **церковний уряд**: теократія — Sobor (Галич і Волинь — з назвою місця замість прикметника);
   3. **власні збори держави**: іменник тегу з таблиці «Прості іменники за тегами» разом з
      прикметником («Podilian Sejmik», «Kyivan Veche»), а для Галича й Волині — назва місця
      («Halych Sejm», «Volhynian Sejmik»);
   4. **загальні правила** для випущених і сформованих держав із русинською культурою, які не
      мають іменника: республіка — Veche, решта — Rada of the Land;
   5. **ванільний заголовок** для всіх інших країн.
3. **Решта країн бачить те, що показала б ваніль:** останнє правило —
   «прикметник + `[Root.GetParliamentName]`», тож англійський чи московський парламент не
   змінився.
4. **Прості іменники лишилися.** `<TAG>_parliament_name` тепер звичайні слова без
   команд. Їх читають події й підказки з `[Root.GetParliamentName]` та ванільний заголовок,
   якщо накладку вимкнено. Для Литви лишається ванільний Seimas.
5. **Парламент є не в кожної країни.** Вікно й `[Root.GetParliamentName]` існують лише тоді, коли
   якась реформа дає `has_parliament = yes` (16 реформ мода й ванільні парламентські). Для країни
   без парламенту команда повертає порожній рядок (виміряно), тож і заголовок не потрібен.

Написання: «Veche», як у назвах реформ («Veche Assemblies», «Kyivan Veche Republic»);
старе «Viche» прибрано. Установу названо прямо, рідні терміни не перекладено, кожне
значуще слово з великої (`docs/STYLE_GLOSSARY.md`). Прикметник ГЛЦ у моді написано
«Halycian», тому назви Галича цього прикметника не використовують.

## Правила за порядком

Умова — те, що перевіряє правило. «Прикметник» — `[Root.GetAdjective]`, тобто власний
прикметник держави («Chernihivan Veche»).

### Київська лінія

| Назва | Умова | Чому |
|---|---|---|
| Sobor of the Lands | `kyivan_cesarstvo_reform` | Цесарство скликає землі, не місто: собор, як зборами станів у Москві |
| Rada of Three Estates | шість `ruthenian_factional_empire_*` | один уряд під шістьма ідентифікаторами (по одному на пару «друга за впливом — домінантна фракція»); назва — назва реформи |
| Princely Snem | `kyivan_rus_reform`, `kyivan_shogunate_reform` | сеньйорат збирається як князі в Любечі 1097 року |
| Kyivan Boyar Rada | `kyivan_boyar_republic_reform` | віче твердне в раду боярських родів |
| Kyivan Veche | `kyivan_veche_reform` | міські збори, що обирають посадника |
| Synod of Kyiv | `kyivan_church_synod_reform` | уряд єпископів засідає синодом |

### Чернігів і Сіверщина

| Назва | Умова | Чому |
|---|---|---|
| Siversk Veche | `siversk_veche_reform` | Сіверське купецьке віче. Старий ланцюг перевіряв `chr_siversk_veche_reform`, якого не існує |
| Desna Staple Council | `chr_desna_staple_reform` | право складу на Десні належить купцям, що сходяться в раді |
| Assembly of the Siversk Towns | `chr_town_union_reform` | Спілка сіверських міст: кожне надсилає делегатів |
| Rada of the Lands | `chr_rada_of_lands_reform` | назва реформи |
| Siversk Boyar Rada | `chr_siversk_principality_reform` | князь править з боярською радою |
| Chancery Rada | `chr_kanceliaryst_republic_reform` | посади — за канцелярським іспитом; збирається рада канцелярії |
| Rada of Many Nations | `chr_many_nations_union_reform` | кожен народ вписує свою статтю в союз і шле своїх представників |
| Zemsky Sobor | `chr_prykaz_tsardom_reform` | цар наказів скликає земський собор: московський взірець, який цей шлях копіює |
| Council of the Magistrat | `chr_magistrat_rule_reform` | магістрат править містом через свою раду |

### Гетьманщина й козацькі громади

| Назва | Умова | Чому |
|---|---|---|
| Baturyn Rada | `het_mazepist_autocracy_reform` | батуринський двір гетьмана |
| Starshyna Rada | `het_starshyna_oligarchy_reform`, `het_hetman_for_life_reform`; також `HET` у монархії | старшина радить гетьманові |
| Regimental Rada | `het_regimental_system_reform` | полки сходяться радами полковників і сотенних |
| Collegium of Little Russia | `het_collegium_control_reform` | Малоросійська колегія: її члени й є збори |
| General Sich Rada | `zaz_general_rada_reform` | Генеральна рада Січі |
| Kosh Rada | `zaz_kosh_elections_reform` | Кіш обирає отамана на раді |
| Sich Rada | тег `ZAZ` або `rip_cossacks_reform` | ванільна козацька реформа в моді зветься Sich Rada |
| Sumy Regimental Rada, Okhtyrka Regimental Rada, Kharkiv Regimental Rada, Izium Regimental Rada | теги `SMY`, `OKH`, `KHK`, `IZM` | слобідські полки |
| General Military Rada | `HET` без монархії | республіканська Гетьманщина збирає Генеральну військову раду |

### Галич

| Назва | Умова | Чому |
|---|---|---|
| Galician Sejm | `hlc_galician_sejm_reform`, `hlc_crown_and_sejm_reform` | польська гілка воєводства: сейм землі |
| Estates of Galicia and Lodomeria | `hlc_austrian_bureaucracy_reform`, `hlc_crown_authority_reform` | австрійська гілка: коронна земля звала свій сейм Станами Галичини й Лодомерії |
| Magnate Sejm | `hlc_magnate_assembly_reform` | Estate Compact: магнати сидять у власному сеймі |
| Halych Boyar Rada | `hlc_boyar_republic_reform`, `hlc_boyar_oligarchy_reform` | Боярська республіка й Правління великих домів |
| Halych Veche | `HLC` у республіці | замість прикметника «Halycian» вжито назву міста |

### Литва

| Назва | Умова | Чому |
|---|---|---|
| Sejm of Two Nations | `lit_union_of_two_nations_reform` | Commonwealth of Two Nations |
| Diet of the Grand Duchy | `lit_grand_diet_reform` | назва реформи |
| Pany-Rada | `lit_pany_rada_reform`, `lit_ruthenian_chancery_reform` | рада панів |
| Seimas | тег `LIT` | ванільна назва литовських зборів |

### Волинь, Закарпаття, Поділля, Переяслав, Одеса

| Назва | Умова | Чому |
|---|---|---|
| Volhynian Sejmik | `vln_sejmik_republic_reform`, `vln_dietine_instructions_reform` | місцевий сеймик, з малої літери за глосарієм; інструкції дають йому мандат |
| Sejm of Grand Ruthenia | `vln_grand_ruthenia_reform` | сейм розширеної держави |
| Sejm of Ruthenia | `vln_ruthenia_reform` | сейм руської претензії на корону |
| Confessional Sejmik | `vln_confessional_reform` | Confessional Voivodeship: сеймик воєводства, де засідають конфесії |
| Cossack Host Rada | `vln_cossack_host_reform` | Cossack Host Privileges |
| Palatine Diet | `uzh_palatial_ruthenian_reform`, `uzh_palatial_rusyn_reform` | палатинський пакт збирається сеймом під палатином |
| Komitat Assembly | чотири реформи `uzh_komitat…` та `uzh_palatial_uhro…` | угорський взірець: зібрання комітату |
| Palanok Council | `uzh_palanok_captaincy_reform` | капітанство замку: рада гарнізону |
| Podilian Land Assembly | `pdl_clan_assembly_reform` | назва реформи |
| Podilian Aristocratic Assembly | `pdl_aristocratic_assembly_reform` | назва реформи |
| Pereiaslav Regimental Rada | `prl_regimental_republic_reform` | полкова республіка |
| Odesa Merchant Council | `odesa_trade_republic_reform` | вільним портом править купецтво |

### Спільні реформи, церковні уряди, власні збори й загальні правила

Назви з прикметником держави: «Chernihivan Boyar Rada», «Volynian Veche».

| Назва | Умова |
|---|---|
| Boyar Rada | `boyar_elite_reform`, `ruthenian_principality_reform` |
| Veche (за реформою) | `elected_assemblies_reform` |
| Burgher Assembly | `assembly_houses_reform` |
| Legislative Rada | `legislative_rada_reform` |
| Halych Sobor, Volhynian Sobor | теократія тегів `HLC`, `VLN` (назва місця замість прикметника) |
| Sobor | русинська держава з теократією |
| Halych Veche | `HLC` у республіці |
| Halych Sejm | `HLC` у решті форм |
| Volhynian Sejmik | `VLN` у решті форм |
| ‹прикметник› ‹іменник› | тег із власним іменником (KIE, KRU, UKR, RUT, CHR, UZH, PRL, PDL, ODS, KUY, RPS, ZLK, SRK, MSK, TRV, VTB, MSL, BLR, PLT) |
| Veche | випущена чи сформована русинська держава (власного іменника немає) у республіці |
| Rada of the Land | така держава в решті форм |

Русинська держава — це один із тегів мода або країна з основною культурою `ruthenian`,
`rusyn` чи їхніми новими формами (`ruthenian_new`, `rusyn_new`, `rusyn_new_new`): так названо й
випущені чи сформовані держави. Ключа `severian` тут більше немає — такої культури в моді нема,
і перевірка ключів культур на ньому червоніла. Для будь-якої іншої країни діє останнє правило:
ванільний заголовок.

## Назви за тегами й формою правління

Таблицю згенеровано з `RULES`: кожен тег мода (і Литва) у трьох формах правління **без** реформи, що сама називає
парламент (з будь-якою такою реформою виграє її назва з розділів вище). Прикметники й назви держав — з локалізації мода.
Тест `tests/check_parliament_names.py` вимагає, щоб блок між мітками збігався з генерованим (`--check` генератора перевіряє те саме).

<!-- MATRIX:BEGIN (written by tools/build_parliament_names.py; do not edit by hand) -->

| Тег | Держава | Монархія | Республіка | Теократія |
|---|---|---|---|---|
| `KIE` | Kyiv | Kyivan Veche | Kyivan Veche | Kyivan Sobor |
| `KRU` | Kyivan Confederation | Kyivan Rada | Kyivan Rada | Kyivan Sobor |
| `UKR` | Ukraine | Ukrainian Rada | Ukrainian Rada | Ukrainian Sobor |
| `RUT` | Ruthenian Tsardom | Ruthenian Zemsky Sobor | Ruthenian Zemsky Sobor | Ruthenian Sobor |
| `CHR` | Chernihiv | Chernihivan Veche | Chernihivan Veche | Chernihivan Sobor |
| `VLN` | Volyn | Volhynian Sejmik | Volhynian Sejmik | Volhynian Sobor |
| `HLC` | Halych | Halych Sejm | Halych Veche | Halych Sobor |
| `UZH` | Huszt March | Husztian Komitat Assembly | Husztian Komitat Assembly | Husztian Sobor |
| `PRL` | Pereiaslav | Pereiaslavlian Rada | Pereiaslavlian Rada | Pereiaslavlian Sobor |
| `PDL` | Podillia | Podilian Sejmik | Podilian Sejmik | Podilian Sobor |
| `ODS` | Odesa | Odesan Merchant Council | Odesan Merchant Council | Odesan Sobor |
| `ZAZ` | Zaporozhia | Sich Rada | Sich Rada | Sich Rada |
| `HET` | Hetmanate | Starshyna Rada | General Military Rada | General Military Rada |
| `KUY` | Kuyaba | Kuyabian Veche | Kuyabian Veche | Kuyabian Sobor |
| `RPS` | Polesia | Polesian Veche | Polesian Veche | Polesian Sobor |
| `SMY` | Sumy | Sumy Regimental Rada | Sumy Regimental Rada | Sumy Regimental Rada |
| `OKH` | Okhtyrka | Okhtyrka Regimental Rada | Okhtyrka Regimental Rada | Okhtyrka Regimental Rada |
| `IZM` | Izium | Izium Regimental Rada | Izium Regimental Rada | Izium Regimental Rada |
| `KHK` | Kharkiv | Kharkiv Regimental Rada | Kharkiv Regimental Rada | Kharkiv Regimental Rada |
| `ZLK` | Zeleny Klyn | Zeleny Klyn Rada | Zeleny Klyn Rada | Zeleny Klyn Sobor |
| `SRK` | Siryi Klyn | Siryi Klyn Rada | Siryi Klyn Rada | Siryi Klyn Sobor |
| `MSK` | Minsk | Minsk Veche | Minsk Veche | Minsk Sobor |
| `TRV` | Turov | Turov Veche | Turov Veche | Turov Sobor |
| `VTB` | Vitebsk | Vitebsk Veche | Vitebsk Veche | Vitebsk Sobor |
| `MSL` | Mstislavl | Mstislavl Veche | Mstislavl Veche | Mstislavl Sobor |
| `BLR` | Belarus | Belarusian Rada | Belarusian Rada | Belarusian Sobor |
| `PLT` | Polotsk | Polotsk Veche | Polotsk Veche | Polotsk Sobor |
| `LIT` | Lithuania | Seimas | Seimas | Seimas |

| Без тегу з іменником | Монархія | Республіка | Теократія |
|---|---|---|---|
| Випущена чи сформована русинська держава (основна культура `ruthenian`/`rusyn`, свого іменника немає) | Rada of the Land | ‹прикметник› Veche | ‹прикметник› Sobor |
| Будь-яка інша країна (ванільний заголовок) | ‹прикметник› ‹іменник› | ‹прикметник› ‹іменник› | ‹прикметник› ‹іменник› |

<!-- MATRIX:END -->

## Прості іменники за тегами

Це значення `<TAG>_parliament_name`. Ванільна гра читає їх без команд, тому вони прості.

| Тег | Іменник | Тег | Іменник |
|---|---|---|---|
| `KIE` | Veche | `KUY` | Veche |
| `KRU` | Rada | `RPS` | Veche |
| `UKR` | Rada | `SMY` | Regimental Rada |
| `RUT` | Zemsky Sobor | `OKH` | Regimental Rada |
| `CHR` | Veche | `IZM` | Regimental Rada |
| `VLN` | Sejmik | `KHK` | Regimental Rada |
| `HLC` | Sejm | `ZLK` | Rada |
| `UZH` | Komitat Assembly | `SRK` | Rada |
| `PRL` | Rada | `MSK` | Veche |
| `PDL` | Sejmik | `TRV` | Veche |
| `ODS` | Merchant Council | `VTB` | Veche |
| `ZAZ` | Sich Rada | `MSL` | Veche |
| `HET` | Starshyna Rada | `BLR` | Rada |
| | | `PLT` | Veche |

## Що перевірено в грі, а що ні

**Виміряно в EU4 1.37.5 (19.10.2026, ізольований профіль, консольні проби):**

- Без `random = no` рядок обирається не першим (див. «Що було зламано», п. 2); з `random = no` — завжди перший.
- Усі 155 варіантів реформ фікстури (`tests/dev_tools/make_government_reform_test.py`): назва, яку друкує рушій
  (`[Root.GetRIPParliamentTitle]` у `log`), збігається з тією, що передбачає генератор, — **0 розбіжностей**. Фікстура
  досягає 55 із 62 правил; не охоплено слобідські полки (`sumy`, `okhtyrka`, `kharkiv`, `izium`), `officers`
  (`HET` у монархії без реформи), `elected_assemblies_reform` і теократію Волині — їх перевіряє лише статичний тест.
- `[Root.GetParliamentName]` повертає іменник тегу («Veche», «Sejm», «Komitat Assembly», «Rada»…) **лише в країн, що
  мають парламент** (17 із 155 варіантів), у решти — порожній рядок. Вікно існує лише для перших, тож це потрібний випадок.

**Не бачено:** саме вікно парламенту із накладкою в запущеній грі (шрифт, розташування, обрізання на різних
масштабах інтерфейсу, мови поза англійською). Гіпотеза, що ванільний заголовок — «прикметник + назва», узята зі скриншота
автора («Chernihivan …»); якщо рушій складає його інакше для якоїсь країни, останнє правило покаже інший текст, ніж ваніль.
Статичний контракт перевіряє правила, наявність кожного ідентифікатора реформи й тегу, відсутність команд у простих ключах,
`random = no`, досяжність кожного правила (жодне не сховане попереднім), положення накладки й ширину найдовшого
заголовка за метриками `vic_29s.fnt`.
