# Автентика й бюджет урядових реформ

Перевірено 7 вересня 2026 року для EU4 **1.37.5.0**. Встановлена гра
повернута на цю версію; джерело старого флейвору збережене окремо у
`diagnostics/vanilla_donors/eu4_1.30.3`. Значення 1.30 не використані як
норма сили для 1.37.

Переглянуто всі **109 визначень реформ і 60 блоків назв урядів**. Числові
пакети **73 реформ** зменшені; інші визначення перевірені й збережені.
Реєстрація, кількість реформ, внутрішні ідентифікатори та наявні національні
дороги збережені. Повний машинний інвентар із тирами, показниками, ознаками
механік і текстами назв — [окремий файл](data/government_authenticity_inventory.json).
Карту переходів слід читати в [наявному огляді](GOVERNMENT_REFORMS_MAP.uk.md).

## Що означає межа 105%

У EU4 немає єдиного показника «сила реформи». Знижка утримання, додатковий
купець, парламент і зміна порядку спадкування не переводяться в один відсоток
без заданої держави, господарства, війни й набору доповнень.

Тому тут розділено два результати. Для трьох повністю зіставних **базових
числових пакетів** перевірка доводить покомпонентну межу 105% від ванільного
аналога того самого тіру. Для інших реформ виконано скорочення надмірного
складання, перевірку відповідності установі та зіставлення з конкретними
ванільними альтернативами. **Загальна сила всіх 109 реформ у кампанії на
рівні не більше 105% не сертифікована.** Наявність 73 скорочень сама по собі
не є таким доказом. Особливо окремо рахуються парламент, вибори, питомі
війська, місії, привілеї, васальні дії й тимчасові постанови.

### Прямі аналоги з установленої 1.37.5

Ванільні значення прочитані з `common/government_reforms/*.txt`, тири — з
`common/governments/00_governments.txt`. У машинному інвентарі збережено
111 пакетів ванільних аналогів; 108 із них використані в повній рольовій таблиці. Це витяг для перевірки чисел, а не заміна
повних ванільних визначень.

| Реформа мода й тір | Аналог того самого тіру | Порівняння й висновок |
|---|---|---|
| `chr_prykaz_tsardom_reform`, M1 | `tsardom`, M1 | Місткість 200 проти 350; людність +10% проти +20%; автономія −0,025 проти −0,05. Додано +1 невдоволення; немає ванільних стрільців і +0,5 абсолютизму. Кожен позитивний показник пакета нижчий від аналога. |
| `rip_cossacks_reform`, R1 | `cossacks_reform`, R1 | Сила кінноти +10% проти +20%; ціна −10% проти −20%; співвідношення кінноти й частка козаків +20% проти +25%. Прибрано додаткові місткість, здобич і дешеве перенесення столиці. Платний реєстровий огляд рахується окремо. |
| `assembly_houses_reform`, M6 | `parliamentary_reform`, M6 | Обидва дають парламент і −1 невдоволення; мод додатково зменшує максимум абсолютизму на 5. Немає старих +25% поширення інституцій і −10% ціни стабільності. |
| `siversk_veche_reform`, R1 | `veche_republic`, R1 | По одному купцю. У мода +10% торговельного впливу й +5% рівноваги міщан, у ванілі +100 місткості, +10 максимуму абсолютизму та стрільці. Віче мода використовує парламент; це різні механічні пакети, не доказ єдиного відсотка. |
| `chr_desna_staple_reform`, R1 | `merchants_reform`, R1 | По одному купцю й −10 максимуму абсолютизму; у мода лишається +5% торговельної ефективності. Прибрано його додатковий парламент, знижку розвитку й невдоволення. Додатковий торговельний дохід потребує перевірки кампанією. |
| `odesa_trade_republic_reform`, R1 | `merchants_reform`, R1 | Збережено одного купця й +10% торговельної ефективності, прибрано чотири додаткові торговельно-морські надбавки. Морські зв’язки й торгова ліга лишаються окремою віссю. |
| `prl_chernozem_economy_reform`, M8 | `lockean_proviso_reform` і `bergordnung_reforms_reform`, M8 | Мод дає +10% виробничої ефективності та −5% ціни розвитку. Ванільні альтернативи дають відповідно −5% розвитку з +5% товарів або +10% виробничої ефективності. Старі одночасні товари, виробництво, податки й розвиток більше не складаються; дві залишені вигоди не оголошуються рівними одній ванільній. |
| `vln_magdeburg_rights`, M8 | `laesio_enormis_reform`, M8 | Мод: −0,025 автономії та −5% вартості управління штатами; одна платна постанова. Ваніль: −0,05 автономії, +15% виробничої ефективності, приріст добробуту й конфлікт зі шляхтою. Вартість управління й поведінка станів окремо не монетизовані. |
| `chr_grain_directorate_reform`, M8/R8 | `lockean_proviso_reform`, M8/R8 | Надбавка товарів діє лише на власні зернові провінції. Немає глобальної надбавки товарів і жодного другого шару виробничої ефективності. Частка зерна визначає фактичний ефект. |
| `vln_black_voivode_legion`, M5 | `new_order_regiments_reform`, M5 | Збережено +2,5% дисципліни й +10% моралі; вилучено традицію й дешеве утримання. Ванільний аналог натомість розвиває професіоналізм, муштру й традицію. Ці бойові моделі не прирівнюються арифметично. |
| `hlc_enlightened_monarchy_reform`, M11 | `enlightened_monarchy_reform`, M11 | Мод: −1 невдоволення й −5% ціни ідей; ваніль: −2 невдоволення та дві прийняті культури. Різні способи пізнього управління; універсального коефіцієнта немає. |

Особливі ванільні реформи не є дозволом складати їхні найкращі риси.
Зокрема, з усього власного шару прибрані безплатні додаткові бали здібностей
правителя, загальна адміністративна ефективність та знижка всіх витрат.
Це зменшує найсильніші перехресні комбінації, але не підміняє випробування
на однакових збереженнях.

## Три пов’язані цикли установ

Усі три рішення користуються **одним спільним десятирічним строком**.
Не можна одночасно мати міську, канцелярську й реєстрову постанову.

| Установа й доступ | Перша постанова | Альтернатива |
|---|---|---|
| Міські хартії: `vln_magdeburg_rights` | 50 дукатів і 50 дипломатичних балів: +5% виробничої ефективності, +5% рівноваги міщан, −5 максимуму абсолютизму | 50 дукатів і 50 адміністративних балів: +5% податків, −0,025 корупції за рік, −5% рівноваги міщан |
| Канцелярія: `lit_ruthenian_chancery_reform` або `chr_kanceliaryst_republic_reform` | 50 дукатів і 50 адміністративних балів: −5% утримання штатів, −0,025 корупції за рік, −5% рівноваги шляхти | 50 дукатів і 50 дипломатичних балів: −10% ціни прийняття культури, −0,5 невдоволення, −5% податків |
| Козацький реєстр: `het_regimental_system_reform`, `rip_cossacks_reform`, `vln_cossack_host_reform` або `prl_regimental_republic_reform` | 50 дукатів і 50 військових балів: +5% відновлення людності, +5% утримання війська | 50 дукатів і 50 дипломатичних балів: −0,5 невдоволення, −5% загальної людності |

Потрібні мир і невід’ємна стабільність. Тривалість кожної постанови —
**3650 днів**. Рішення тільки відкриває подію; оплату стягує обраний
варіант після повторної перевірки всіх умов. Відмова нічого не дає й не
забирає. Повторно відкритий старий варіант не може вдруге списати ресурси
чи накласти другу пільгу.

Втрата реформи, що утримує відповідну установу, прибирає її поточну
постанову через `removed_effect`. Дата останнього огляду зберігається:
повторний вибір реформи не повертає витрати й не скорочує очікування.
Перевірки під час завантаження, щорічного пульсу й зміни уряду прибирають
від’єднані постанови зі збережень. Вони не оновлюють строк.

Це авторські ігрові витрати й строки. Назви установ спираються на міські
суди та хартії, канцелярський облік служби й козацький реєстр. Їхня
скриптова форма повторює ванільний спосіб «рішення → подія → тимчасовий
модифікатор», а не створює новий інтерфейс. Ванільна 1.37.5 окремо має
`cossacks_registry_reform`, `royal_charters_reform` та канцелярські
реформи; це тематичні аналоги, не твердження про скопійовані тексти.
Огляд донора не підтвердив зникнення цих сюжетних родин:
[результати порівняння подій](data/flavor_130_inventory.json).

## Виправлення складання

- Сіверське віче більше не отримує ранньої козацької кнопкової механіки
  разом із парламентом і десятьма постійними надбавками.
- Деснянський склад відрізняється від міської ради торговельними
  установами; другий парламент з його пакета прибраний.
- Сіверська приказна монархія втратила +5% адміністративної ефективності
  поверх російських державних дій. Канцеляристи та корпус джур більше не
  додають безплатні адміністративні й військові здібності правителя.
- Київський сеньйорат спирається на уділи й їхні зобов’язання. З його
  монархічного визначення вилучені торгові міста та торгові пости, що
  вимагали республіканського господаря.
- Партії Паланка, князів, бояр і гетьманів зберегли вибір та недоліки, але
  втратили другорядні безплатні податкові, військові й торгові надбавки.
- Зерновий господарський пакет раніше давав +15% товарів і +15%
  виробничої ефективності на зерні: за нульових інших надбавок
  `1.15 × 1.15 = 1.3225`, тобто +32,25% виробничого доходу. Тепер
  лишено тільки +10% товарів на власному зерні, тобто `1.10`.
  Різниця — 22,25 відсоткового пункту базового виробничого доходу.
- Полкова адміністрація Гетьманщини більше не складає сім загальних
  надбавок із +20% місцевих податків: загальний пакет скорочено,
  місцевий податок зменшено до +10%, реєстрове рішення платне.
- Залишені походження, дипломатичні дії, умови місій і переходи між
  урядами. Для них статична досяжність не означає доведену вигоду ШІ.

## Назви урядів

Усі 60 блоків перевірено разом із їхніми умовами й порядком пріоритету.
Повний перелік трьох рангів і чоловічих/жіночих титулів міститься в
машинному інвентарі. Зміни стосуються назв установ і посад:

- зернова реформа більше не робить монарха «гетьманом урожаю»;
  її окремий профіль назв діє тільки в республіці, з посадником і
  маршалком ради;
- «Гетьман муштри» став гетьманом, «муштрований гетьманат» — гетьманатом,
  «держава академії» — гетьманатом;
- козацькі «кантони» у видимому тексті стали паланками; внутрішні ключі
  збережені для сумісності;
- «фракційна імперія» стала Руським цесарством; рада лишається
  механікою, а не назвою державного рангу;
- комітат Ужгорода більше не проходить у рангах через чужий «полк»:
  використані окремі ключі комітату, зборів комітатів і союзу комітатів;
- освітня або міська реформа більше не називає правителя «культурним»
  чи «бургомістром-гетьманом».

Альтернативні шляхи ордену й орди не оголошуються історичними урядами
Гетьманщини. Їхні окремі фінали збережені як попередньо закладений вибір
кампанії. Назви самі по собі не є свідченням існування установи у 1444 році.

## Перевірка

- Статично: 109 визначень, реєстрація в тирах, культурні й національні
  умови, сумісність переходів і 60 блоків назв.
- Окремий тест `check_government_reviews.py`: 36 сценаріїв оплати,
  повторного виклику, недостатніх ресурсів, війни, втрати реформи,
  очищення та межі 3649/3650 днів. Виконується малий піднабір фактичних
  скриптових умов і ефектів; це не емулятор EU4.
- Пряме зіставлення трьох базових числових пакетів із установленою 1.37.5.
- Запуск гри, виконання всіх гілок у грі, поведінка ШІ, збереження й
  завантаження та кампанійна межа 105% цим звітом **не підтверджені**.

Наступна перевірка загальної сили потребує парних збережень із однаковими
територією, станами, технологіями й військом. Окремо рахуються гроші,
вартість поповнення, людність, адміністративні витрати, автономія й темп
реформ на 10/20/50 роках. Ваги цих показників слід погоджувати до прогону,
а не підбирати під бажані 105%.

## Повне покриття визначень

Доповнено **8 вересня 2026 року**: кожне з 109 визначень має явне поле
`comparator_by_tier`. Для реформ, зареєстрованих у двох видах уряду,
аналог указано окремо для кожного тіру. Перевірено **115 пар «реформа —
тір»** проти фактичної реєстрації EU4 1.37.5. Базова республіканська
реформа зіставлена в невидимому слоті `R0`; це не додатковий вибір
гравця.

Усі посилання в таблиці нижче належать **тому самому тіру**, що й реформа
мода. Доступ до особливого ванільного аналога за тегом, релігією чи
доповненням не переноситься в мод. Два аналоги пояснюють різні частини
установи; їхні бонуси не складаються в дозволений бюджет.

Поле `base_comparator` лишене тільки для трьох зіставних числових пакетів.
Для інших визначень `quantitative_certified = false`: заповнення рольової
таблиці не сертифікує їхню загальну силу. Дев’ять часткових збігів
позначені знаком **†**. Там у потрібному тірі немає точного ванільного
двійника; причина записана в `comparator_limit` і наведена нижче.

| Визначення | Тір → ванільні аналоги 1.37.5 | Роль | Дія аудиту |
|---|---|---|---|
| `siversk_veche_reform` | `R1` → `veche_republic` | Міське віче й виборна влада | Пакет скорочено |
| `chr_grain_directorate_reform` | `M8` → `lockean_proviso_reform`, `vodka_of_the_crown_reform`; `R8` → `lockean_proviso_reform`, `vodka_of_the_crown_reform` | Господарський устрій і товарне виробництво | Пакет скорочено |
| `chr_desna_staple_reform` | `R1` → `merchants_reform` | Торгова республіка | Пакет скорочено |
| `chr_town_union_reform` | `R1` → `city_alliance_reform`, `dutch_republic` | Союз міст і розподіл виборної влади | Пакет скорочено |
| `chr_rada_of_lands_reform` | `R1` → `federal_republic`, `parliamentary_republic_reform` | Федеративна виборна рада | Пакет скорочено |
| `chr_magistrat_rule_reform` | `R1` → `oligarchy_reform`, `merchants_reform` | Міський магістрат і торгове управління | Пакет скорочено |
| `chr_siversk_principality_reform` | `M1` → `principality` | Князівський уряд | Пакет скорочено |
| `chr_prykaz_tsardom_reform` | `M1` → `tsardom` | Централізований приказний уряд | Пакет скорочено |
| `chr_kanceliaryst_republic_reform` † | `R1` → `civic_republicanism_government`, `oligarchy_reform` | Цивільна республіка й добір управлінців | Пакет скорочено |
| `chr_dzhura_corps_reform` | `M1` → `livonian_general_controlled_monarchy` | Влада служилого військового корпусу | Пакет скорочено |
| `chr_many_nations_union_reform` | `M1` → `lithuanian_grand_empire` | Управління багатокультурною монархією | Пакет скорочено |
| `het_starshyna_oligarchy_reform` | `R2` → `aristocratic_values_reform`, `republican_authoritarianism_reform` | Права старшини та розподіл республіканської влади | Збережено |
| `het_hetman_for_life_reform` | `R3` → `consolidation_of_power_reform`, `consolidate_power_in_doge_reform` | Подовження особистої влади виборного правителя | Збережено |
| `het_regimental_system_reform` | `R7` → `provincial_governments_reform`, `administrative_divisions_reform` | Провінційна адміністрація | Пакет скорочено |
| `het_academy_enlightenment_reform` † | `R6` → `attorney_general_reform`, `governing_senate_reform` | Освічена цивільна адміністрація | Збережено |
| `het_mazepist_autocracy_reform` | `R10` → `political_principle_reform`, `stability_principle_reform` | Засади особистої влади й стабільності | Пакет скорочено |
| `het_collegium_control_reform` † | `R11` → `landholders_reform`, `three_classes_reform` | Обмеження виборного уряду становим представництвом | Збережено |
| `hlc_galician_voivodeship_reform` | `M1` → `grand_duchy_reform` | Територіальна князівська адміністрація | Збережено |
| `hlc_magnate_assembly_reform` | `M2` → `maintain_nobles_status_quo_reform`, `enforce_privileges_reform` | Представництво й привілеї шляхти | Збережено |
| `hlc_centralized_voivodeship_reform` | `M2` → `quash_noble_power_reform`, `ministerialis_promotion_reform` | Центральна адміністрація замість влади магнатів | Пакет скорочено |
| `hlc_galician_sejm_reform` | `M6` → `parliamentary_reform` | Законодавчі збори | Пакет скорочено |
| `hlc_austrian_bureaucracy_reform` † | `M6` → `general_estates_reform`, `governing_senate_reform` | Співвідношення центральної влади й представництва | Пакет скорочено |
| `hlc_merchant_privileges_reform` | `M8` → `jap_gokaido_reform`, `empower_the_burghers_reform` | Купці та торгові привілеї | Пакет скорочено |
| `hlc_confessional_dualism_reform` | `M4` → `maintain_clergy_balance_of_power_reform`, `secularization_of_the_state_reform` | Співіснування конфесій та межі церковної влади | Пакет скорочено |
| `hlc_crown_authority_reform` | `M10` → `letat_cest_moi_reform`, `strengthen_bakuhan_system_reform` | Консолідація коронної влади | Пакет скорочено |
| `hlc_crown_and_sejm_reform` | `M10` → `regional_representation_reform`, `peoples_kingdom_reform` | Розподіл влади між короною й представництвом | Пакет скорочено |
| `hlc_enlightened_monarchy_reform` | `M11` → `enlightened_monarchy_reform` | Освічене пізнє управління | Пакет скорочено |
| `hlc_military_modernization_reform` | `M5` → `cavalry_warfare_reform`, `gendarmes_reform` | Реформування кінного війська | Збережено |
| `kyivan_rus_reform` | `M1` → `ruthenian_tsardom`, `tsardom` | Руська корона й державне управління | Збережено |
| `kyivan_shogunate_reform` | `M1` → `shogunate`, `feudal_france_reform` | Сеньйорат і зобов'язання молодших володарів | Пакет скорочено |
| `kyivan_cesarstvo_reform` | `M1` → `ruthenian_tsardom`, `tsardom` | Руська корона й державне управління | Збережено |
| `ruthenian_factional_empire_reform` | `M1` → `stadthalter_monarchy_reform` | Монархія з конкуруючими владними партіями | Пакет скорочено |
| `ruthenian_factional_empire_princes_hetmans_reform` | `M1` → `stadthalter_monarchy_reform` | Монархія з конкуруючими владними партіями | Пакет скорочено |
| `ruthenian_factional_empire_boyars_hetmans_reform` | `M1` → `stadthalter_monarchy_reform` | Монархія з конкуруючими владними партіями | Пакет скорочено |
| `grand_duchy_reform` | `M1` → `grand_duchy_reform`, `lithuanian_grand_kingdom` | Литовське велике князівство | Пакет скорочено |
| `lit_pany_rada_reform` | `M2` → `maintain_nobles_status_quo_reform`, `enforce_privileges_reform` | Представництво й привілеї шляхти | Збережено |
| `lit_ruthenian_chancery_reform` | `M3` → `examination_system_reform`, `regional_council_reform` | Канцелярська та місцева адміністрація | Пакет скорочено |
| `lit_confessional_guarantee_reform` | `M4` → `maintain_clergy_balance_of_power_reform`, `secularization_of_the_state_reform` | Співіснування конфесій та межі церковної влади | Пакет скорочено |
| `lit_boyar_levy_reform` | `M5` → `cavalry_warfare_reform`, `gendarmes_reform` | Реформування кінного війська | Збережено |
| `lit_grand_diet_reform` | `M6` → `parliamentary_reform` | Законодавчі збори | Збережено |
| `lit_statute_reform` | `M7` → `meritocratic_focus_reform`, `dakhni_culture_reform` | Правила державної служби й адміністративний облік | Пакет скорочено |
| `lit_union_of_two_nations_reform` | `M1` → `polish_great_sejm`, `lithuanian_grand_empire` | Союзна корона зі становим представництвом | Пакет скорочено |
| `lit_separate_crown_reform` | `M1` → `lithuanian_grand_kingdom`, `lithuanian_grand_empire` | Окрема литовська корона | Пакет скорочено |
| `odesa_trade_republic_reform` | `R1` → `merchants_reform` | Торгова республіка | Пакет скорочено |
| `pdl_clan_assembly_reform` | `M1` → `feudalism_reform`, `principality` | Князівська влада й земельне ополчення | Збережено |
| `pdl_steppe_principality_reform` | `M1` → `principality` | Прикордонна князівська влада | Збережено |
| `pdl_voivodeship_kingdom_reform` | `M1` → `grand_duchy_reform`, `livonian_administrative_monarchy` | Територіальна й станова адміністрація | Пакет скорочено |
| `pdl_palatine_court_reform` | `M2` → `maintain_nobles_status_quo_reform`, `grant_nobles_electorate_reform` | Двір і станові повноваження | Пакет скорочено |
| `pdl_aristocratic_assembly_reform` | `M2` → `maintain_nobles_status_quo_reform`, `enforce_privileges_reform` | Представництво й привілеї шляхти | Пакет скорочено |
| `pdl_magnate_republic_reform` | `M8` → `jap_gokaido_reform`, `empower_the_burghers_reform` | Купці та торгові привілеї | Збережено |
| `pdl_frontier_voivodeship_reform` | `M1` → `grand_duchy_reform`, `livonian_administrative_monarchy` | Територіальна й станова адміністрація | Пакет скорочено |
| `pdl_carpathian_bastion_reform` | `M5` → `defensive_stance_reform`, `sygnakhs_system_reform` | Прикордонні укріплення | Пакет скорочено |
| `pdl_frontier_republic_reform` | `M5` → `cavalry_warfare_reform`, `cossacks_registry_reform` | Кінна служба й козацький реєстр | Збережено |
| `pdl_magnate_dominion_reform` | `M8` → `laesio_enormis_reform`, `royal_charters_reform` | Земельні права, міські хартії й місцева адміністрація | Збережено |
| `pdl_enlightened_voivodeship_reform` | `M11` → `enlightened_monarchy_reform` | Освічене пізнє управління | Збережено |
| `pdl_absolute_dominion_reform` | `M10` → `letat_cest_moi_reform`, `strengthen_bakuhan_system_reform` | Консолідація коронної влади | Пакет скорочено |
| `pdl_revolutionary_republic_reform` | `M11` → `legislative_houses_reform`, `enlightened_monarchy_reform` | Пізній законодавчий устрій монархії | Збережено |
| `pdl_grand_podillia_reform` | `M10` → `letat_cest_moi_reform`, `strengthen_bakuhan_system_reform` | Консолідація коронної влади | Пакет скорочено |
| `pdl_religious_tolerance_reform` | `M4` → `maintain_clergy_balance_of_power_reform`, `secularization_of_the_state_reform` | Співіснування конфесій та межі церковної влади | Пакет скорочено |
| `prl_ancient_principality_reform` | `M1` → `principality` | Князівський уряд | Пакет скорочено |
| `prl_regimental_republic_reform` | `R1` → `cossacks_reform` | Козацький виборний уряд | Пакет скорочено |
| `prl_treaty_diplomacy_reform` | `M7` → `standardized_millets_reform`, `administration_of_the_parliament_reform` | Домовленості з підлеглими та зовнішні зносини | Пакет скорочено |
| `prl_chernozem_economy_reform` | `M8` → `lockean_proviso_reform`, `bergordnung_reforms_reform` | Розвиток товарного виробництва | Пакет скорочено |
| `prl_border_fortress_reform` | `M5` → `defensive_stance_reform`, `sygnakhs_system_reform` | Прикордонні укріплення | Пакет скорочено |
| `prl_episcopal_authority_reform` | `M4` → `focus_of_the_patriarchy_reform`, `strengthened_the_patriarchy_reform` | Патріарша та єпископська влада | Пакет скорочено |
| `rip_cossacks_reform` | `R1` → `cossacks_reform` | Козацький виборний уряд | Пакет скорочено |
| `rip_republic_mechanic` | `R0` → `republic_mechanic` | Базовий республіканський устрій | Збережено |
| `ruthenian_principality_reform` | `M1` → `feudalism_reform`, `austrian_archduchy_reform` | Удільні зобов'язання та контроль підлеглих | Збережено |
| `principality_appanage` | `M1` → `appanage_reform` | Удільний уряд молодшого володаря | Збережено |
| `elected_assemblies_reform` | `M2` → `grant_nobles_electorate_reform`, `maintain_nobles_status_quo_reform` | Політичне представництво земель і знаті | Збережено |
| `boyar_elite_reform` | `M2` → `grant_military_command_reform`, `enforce_privileges_reform` | Військові зобов'язання привілейованого стану | Збережено |
| `sacred_regulation_reform` | `M4` → `secure_clergy_power_reform`, `strengthen_clergy_reform` | Співпраця корони й духовенства | Збережено |
| `patriarch_engagement_reform` | `M4` → `focus_of_the_patriarchy_reform`, `strengthened_the_patriarchy_reform` | Патріарша та єпископська влада | Збережено |
| `merchant_nobility_reform` † | `M7` → `meritocratic_focus_reform` | Міщанські установи в управлінні | Пакет скорочено |
| `open_trading_ports_reform` † | `M7` → `meritocratic_focus_reform` | Міщанські установи в управлінні | Пакет скорочено |
| `assembly_houses_reform` | `M6` → `parliamentary_reform` | Законодавчі збори | Пакет скорочено |
| `considerable_bloodline_reform` | `M10` → `letat_cest_moi_reform`, `strengthen_bakuhan_system_reform` | Консолідація коронної влади | Пакет скорочено |
| `representation_monarchy_reform` | `M10` → `regional_representation_reform`, `peoples_kingdom_reform` | Розподіл влади між короною й представництвом | Пакет скорочено |
| `legislative_rada_reform` | `M11` → `legislative_houses_reform`, `enlightened_monarchy_reform` | Пізній законодавчий устрій монархії | Пакет скорочено |
| `divine_tsyisar_reform` | `M11` → `political_absolutism_reform`, `enlightened_monarchy_reform` | Коронна влада й пізній внутрішній порядок | Пакет скорочено |
| `vln_magdeburg_rights` | `M8` → `laesio_enormis_reform`, `royal_charters_reform` | Земельні права, міські хартії й місцева адміністрація | Пакет скорочено |
| `vln_ruthenian_renaissance_reform` † | `M7` → `meritocratic_focus_reform`, `strengthened_parliament_reform` | Освічене управління й розвиток земель | Пакет скорочено |
| `uzh_palanok_captaincy_reform` | `M1` → `livonian_elective_monarchy`, `stadthalter_monarchy_reform`; `R1` → `dutch_republic`, `united_cantons_reform` | Виборна прикордонна влада | Пакет скорочено |
| `uzh_komitat_system_reform` | `M1` → `grand_duchy_reform`, `livonian_administrative_monarchy` | Територіальна й станова адміністрація | Пакет скорочено |
| `uzh_republican_komitat_system_reform` | `R1` → `federal_republic`, `noble_elite_reform` | Республіканський союз територіальних станів | Пакет скорочено |
| `uzh_palatial_ruthenian_reform` | `M10` → `regional_representation_reform`, `peoples_kingdom_reform`; `R10` → `equality_principle_reform`, `enlightened_principle_reform` | Територіальне й культурне представництво | Збережено |
| `uzh_palatial_rusyn_reform` | `M10` → `regional_representation_reform`, `consulate_reform`; `R10` → `stability_principle_reform`, `equality_principle_reform` | Місцеві права та внутрішня злагода | Пакет скорочено |
| `uzh_palatial_uhro_reform` | `M10` → `military_electorate_reform`, `strengthen_bakuhan_system_reform` | Станова військова влада й коронні повноваження | Збережено |
| `uzh_palatial_uhro_republic_reform` | `R10` → `military_principle_reform` | Військова основа республіканського устрою | Збережено |
| `uzh_union_synod_reform` | `M4` → `focus_of_the_patriarchy_reform`, `maintain_clergy_balance_of_power_reform`; `R4` → `focus_of_the_patriarchy_reform`, `maintain_clergy_balance_of_power_reform` | Синод, східний обряд і конфесійне порозуміння | Пакет скорочено |
| `uzh_carpathian_border_commissariat_reform` | `M11` → `nizam_i_cedid_reform`; `R9` → `power_to_the_captains_reform`, `broaden_executive_powers_reform` | Пізня військова адміністрація | Пакет скорочено |
| `vln_voivodeship_reform` | `M1` → `grand_duchy_reform` | Територіальна князівська адміністрація | Збережено |
| `vln_confessional_reform` | `M4` → `maintain_clergy_balance_of_power_reform`, `secularization_of_the_state_reform` | Співіснування конфесій та межі церковної влади | Пакет скорочено |
| `vln_ruthenia_reform` | `M9` → `the_leviathan_reform`, `six_livres_reform` | Суверенна коронна влада | Пакет скорочено |
| `vln_cossack_host_reform` | `M2` → `grant_military_command_reform`, `enforce_privileges_reform` | Військові зобов'язання привілейованого стану | Збережено |
| `vln_confessional_academy` | `M3` → `examination_system_reform`, `court_of_art_and_culture_reform` | Освіта та добір службовців | Збережено |
| `vln_voivode_council` † | `M6` → `aristocratic_court_reform`, `royal_decree_reform` | Рада служилої знаті й коронна влада | Збережено |
| `vln_black_voivode_legion` | `M5` → `new_order_regiments_reform`, `mansure_army_reform` | Професійний полк і військова модернізація | Пакет скорочено |
| `vln_grand_ruthenia_reform` | `M10` → `letat_cest_moi_reform`, `strengthen_bakuhan_system_reform` | Консолідація коронної влади | Збережено |
| `zaz_sich_brotherhood_reform` | `R2` → `republicanism_reform`, `democratic_values_reform` | Виборне братство і спільна рада | Збережено |
| `zaz_kosh_elections_reform` | `R3` → `frequent_elections_reform`, `force_reelection_reform` | Часті вибори й переобрання | Збережено |
| `zaz_chaiky_trade_reform` | `R8` → `open_naval_services_reform`, `master_smugglers_reform` | Морська служба та прикордонна торгівля | Пакет скорочено |
| `zaz_general_rada_reform` | `R6` → `parliamentary_reform`, `estate_council_reform` | Рада й представництво станів | Пакет скорочено |
| `zaz_free_host_reform` | `R10` → `military_principle_reform` | Військова основа республіканського устрою | Пакет скорочено |
| `zaz_last_sich_reform` † | `R11` → `military_rulership_reform`, `landholders_reform` | Пізнє військове самоврядування та права землевласників | Пакет скорочено |
| `zaz_cossack_cantons_reform` | `R1` → `united_cantons_reform` | Союз військових територіальних громад | Пакет скорочено |
| `zaz_host_and_state_reform` | `R1` → `prussian_republic_reform`, `cossacks_reform` | Дисциплінований виборний військовий уряд | Пакет скорочено |
| `zaz_sacred_host_order_reform` | `Th1` → `monastic_order_reform`, `militarized_crusader_order_reform` | Духовний військовий орден | Пакет скорочено |
| `zaz_sacred_horde_reform` | `T1` → `steppe_horde`, `sacred_kingdom` | Кочовий військовий і сакральний уряд | Пакет скорочено |

### Часткові рольові відповідності

- `chr_kanceliaryst_republic_reform`: У R1 немає тотожного канцелярського пакета: зіставляються цивільний добір правителя й республіканська адміністрація, а не рівність усіх бонусів.
- `het_academy_enlightenment_reform`: У R6 академія не має окремого ванільного двійника; аналоги охоплюють освічених радників і цивільний сенат.
- `het_collegium_control_reform`: Ванільний R11 не містить такої самої залежної колегії; зіставляються становий склад і межі військового самоврядування. Залежність від сюзерена лишається окремою віссю.
- `hlc_austrian_bureaucracy_reform`: У M6 немає тотожного набору вартості радників і корупції. Порівнюються центральна рада та представництво; числовий адміністративний аналог meritocratic_focus_reform розташований у M7.
- `merchant_nobility_reform`: У M7 немає прямого ванільного бонусу купця: тут зіставлена роль міщан у державній службі; рольовий аналог додаткового купця jap_gokaido_reform належить до M8.
- `open_trading_ports_reform`: Портова реформа стоїть у M7, де немає тотожної торгово-портової альтернативи. Міщанська адміністрація зіставлена в тому самому тірі, а власне портовий аналог thalassocracy_reform — у M8.
- `vln_ruthenian_renaissance_reform`: У M7 немає окремої реформи культурного відродження з цим набором. Аналоги стосуються освіченої служби та підтримки розвитку представлених земель.
- `vln_voivode_council`: У M6 ванільна рада знаті дипломатична, а рада воєвод має військовий пакет. Тир і станова роль збігаються; бойові бонуси потребують окремої оцінки.
- `zaz_last_sich_reform`: У R11 немає аналога останньої Січі під сюзереном. Військовий устрій і права землевласників зіставлено окремо; оборона й бажання свободи не прирівнюються до ванільних показників.

Тест `check_government_reviews.py` перевіряє повноту переліку за живими
визначеннями мода, збіг кожного тіру, наявність усіх названих аналогів у
ванільній 1.37, пояснення часткових відповідностей і відсутність зайвої
числової сертифікації. Без відповідної встановленої гри він окремо
повідомляє, що перевірка живих ванільних тирів пропущена.
