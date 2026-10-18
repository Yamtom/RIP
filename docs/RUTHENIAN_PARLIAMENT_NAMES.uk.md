# Назви парламентів русинських держав — 18.10.2026

Система найменування для всіх русинських держав і всіх урядових реформ, що дають
парламент. Джерело правил — таблиця `RULES` у `tools/build_parliament_names.py`;
контракт — `tests/check_parliament_names.py`.

## Що було зламано

У вікні парламенту стояло «Chernihivan [Root.GetRIPParliamentName]». Перша система
записала команду кастомної локалізації в ванільні ключі `<TAG>_parliament_name`. Гра
читає ці ключі як простий текст, коли збирає заголовок вікна («прикметник + назва»), а
команда `[Root.…]` працює лише там, де є область дії країни. Тому гравець бачив
сирий токен, а не назву.

## Як це працює тепер

1. **Заголовок вікна малює скриптовий текст.** `interface/parliament.gui` —
   ванільне вікно, у якому ванільний `title` перенесено за межі вікна (x = −2000), а на
   його місці лежить `rip_parliament_title` (`scripted = yes`, той самий шрифт `vic_29s`,
   ширина 548). Вікно `parliament_window` — підтримуваний хост `custom_gui` з ROOT =
   країна гравця, тож `[Root.GetRIPParliamentTitle]` там виконується.
2. **Одне правило визначає всю назву.** `GetRIPParliamentTitle` проходить правила зверху
   вниз; перше, чия умова справджується, дає повну назву. Тому назва залежить від реформи,
   а не лише від тегу: Чернігів із торговим віче, зі стейплом на Десні чи зі Спілкою міст
   має різні парламенти.
3. **Решта країн бачить те, що показала б ваніль:** останнє правило —
   «прикметник + `[Root.GetParliamentName]`», тож англійський чи московський парламент не
   змінився.
4. **Прості іменники лишилися.** `<TAG>_parliament_name` тепер звичайні слова без
   команд. Їх читають події й підказки з `[Root.GetParliamentName]` та ванільний заголовок,
   якщо накладку вимкнено. Для Литви лишається ванільний Seimas.

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
| Rada of Three Estates | три `ruthenian_factional_empire_*` | один уряд під трьома ідентифікаторами; назва — назва реформи |
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

### Спільні реформи й типи урядів

Ці назви з прикметником держави: «Chernihivan Boyar Rada», «Volynian Veche».

| Назва | Умова |
|---|---|
| Boyar Rada | `boyar_elite_reform`, `ruthenian_principality_reform` |
| Veche (за реформою) | `elected_assemblies_reform` |
| Burgher Assembly | `assembly_houses_reform` |
| Legislative Rada | `legislative_rada_reform` |
| Sobor | русинська держава з теократією |
| Veche | русинська республіка без власного правила |
| Rada of the Land | будь-який інший русинський уряд із парламентом |

Русинська держава — це один із тегів мода або країна з основною культурою `ruthenian`,
`rusyn`, `severian` чи їхніми новими формами: так названо й випущені чи сформовані держави.
Для будь-якої іншої країни діє останнє правило: ванільний заголовок.

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

## Що не перевірено

Вікно парламенту в запущеній грі не бачили. Статичний контракт перевіряє правила,
наявність кожного ідентифікатора реформи й тегу, відсутність команд у простих ключах,
положення накладки й ширину найдовшого заголовка за метриками `vic_29s.fnt`. Гіпотеза, що
ванільний заголовок — «прикметник + назва», узята зі скриншота автора («Chernihivan …»);
якщо рушій складає його інакше для якоїсь країни, останнє правило покаже інший текст, ніж
ваніль. Не перевірено також, чи накладка бере шрифт і розташування так само, як ванільний
рядок на різних розмірах інтерфейсу.
