# Чернігів, Переяслав, Куяба: правки за переглядом місій від 21 листопада 2026 року

Два перегляди місій `missions/Chernihiv_Missions.txt`, `missions/Pereiaslav_Missions.txt`
і `missions/Kuyaba_Missions.txt`. Правки зроблені на `main` 53a4d19c, після
коміту 4c7418c5, який уже закрив частину зауважень (див. нижче).

## Перший перегляд

| Зауваження | Правка |
|---|---|
| Колонка 4 мала `generic = yes` без `ai = yes`, тож ШІ-Чернігів не отримував її | `generic = no` і `ai = yes`, як у решти колонок файла |
| `chr_build_manufactories` вимагав 20 провінцій із мануфактурами (копія ванільного generic) і замикав весь зерновий стовп | поріг `6`: сусідні кроки колонки вимагають 5 зернових провінцій і 4 фермерські маєтки |
| `chr_defeated_rya`: +24% торгової потужності провінцій і +24% керування торгівлею на 80 років | `0.1` і `0.15` на 50 років (як `chr_defeated_oka`); опис переписано під торговельну дію. Автор у 4c7418c5 теж переписав опис, але на військовий; лишено версію, що збігається з ефектом |
| `prl_princely_legacy_desc` називав Святослава Хороброго князем Переяслава | його «Переяславець» дунайський; замість нього Володимир Глібович, переяславський князь 1169–1187 |
| `prl_great_power_alliance_desc` згадував Богдана Хмельницького, хоча місія доступна з 1444 року | вже виправлено автором у 4c7418c5 (текст про сусідів із більшими арміями); взято його формулювання |
| 10 модифікаторів CHR визначені й ніде не використані | `chr_dominate_home_trade_reward` додано до нагороди `chr_dominate_home_trade_node` (його опис і є описом цієї місії); дев'ять решти (шість `_mod` і три `chr_ruthenian_*registers*`/`civil_registers`) вилучені разом з локалізацією на чотирьох мовах — вони дублювали вже підключені `chr_*_guardianship`, `chr_commonwealth_joint_diets`, `chr_black_sea_consortia` і належали вилученій гілці реєстрів |
| `chr_flavor.1` і `chr_flavor.3` осиротілі | `ruina_events.1` для CHR через 3 дні викликає `chr_flavor.1` (її варіанти дають `chr_baturyn_fortifications` і `chr_starshyna_compromise`, які блок `progress` катастрофи `chernihiv_ruina` уже враховує, але які ніде не видавалися); `chr_flavor.1` через 540 днів викликає `chr_flavor.3`, що перевіряє, чи Руїна ще триває |

## Другий перегляд

| Зауваження | Стан |
|---|---|
| Залежність від покровителя Руїни | Уточнення від 22 листопада. Прикордонна рада (`chr_flavor.38`) визначає дипломатичну або військову лінію слота 2. Обидві кримські місії слота 4 доступні за будь-якої доктрини. Для цих місій можна уникнути Руїни або вибрати будь-якого покровителя після неї. Перегляд діючого пакту змінює відносини з партнером і тимчасові бонуси. |
| Фінал `chr_imperial_ambition_mission` («The State's Conquest», «imperial destiny») суперечить конфедеративному тону колонки | назва «The Rus' Concord», текст про хартії, сейми й спільні податки; нагорода — власний `chr_rus_concord` (`years_of_nationalism = -5`, той самий ефект, що в ванільного `imperial_ambition`), щоб підказка не казала «Imperial Ambition» |
| KUY: дві місії слоту 1 нікуди не ведуть | `KUY_granary_of_steppe` тепер умова `KUY_steppe_caravans`; ланцюг `KUY_magdeburg_guilds` → `KUY_granary_of_steppe` → `KUY_steppe_caravans` → `KUY_sultanate_of_rus` замкнений |
| KUY: перша місія вимагає 5 провінцій із торговими будівлями й розвитком 15 | 3 провінції; вимога до Києва (280: торгова будівля, розвиток 15) незмінна, бо її фіксує `check_chr_prl_kuy_mission_fixes.py` |
| Ретроспективні місії проходяться за століття до події | `prl_magdeburg_charter` (текст датує грамоту 1585 роком) тепер вимагає `is_year = 1585` або інституцію `printing_press`. Вознесенського захищено автором (1695 або `manufactories`). `chr_tmutarakan_inheritance` мовить про минуле й дати не потребує |
| Додати по одному реальному факту з роком до кожної місії | не робилось: близько сотні місій у трьох файлах, кожен факт потребує перевірки. Пропозиція: робити партіями по дереву, починаючи з KUY (дев'ять місій) |

## Про вісім червоних перевірок

Гіпотеза про CRLF перевірена на чистому checkout HEAD із `core.autocrlf=false`
(усі файли LF). Підтвердилася частково:

- `check_colonial_names` на LF проходить, на CRLF падає;
- `check_ruthenian_legacy` на CRLF падає на першому байтовому порівнянні
  `RIP_shared_ruthenian_legacy_missions_l_english.yml`, а на LF — далі, на
  збігу `position` у `zzzz_RuthenianDiaspora_Missions.txt`, тож вада справжня;
- решта (`check_church_gui_routes`, `check_ruthenian_government_ui`,
  `check_interface_naming`, `check_kyiv_subject_forms`) падає однаково на LF:
  це зміст, не закінчення рядків.

`check_event_modifier_layer` і `check_regional_governments` виправлено
комітами основної гілки. Зараз червоних сім; на чистому 53a4d19c ті самі сім,
і з правками цього документа їх не більше. `check_parliament_names` стала
червоною після 53a4d19c: таблиця в `docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md` не
збігається з виходом генератора (`python tools/build_parliament_names.py`).

## Лишається рішенням автора

`chr_flavor.2` («Order Returns to Chernihiv») осиротіла. Нотатка
`docs/EVENT_CHAIN_FIXES_20261027.uk.md` свідомо не видає її нагород, а
`ruina_events.2` сам викликає `chr_flavor.18`. Підключення дало б подвійний
виклик `chr_flavor.18` і повернуло б `chr_collegium_reform`. Вилучення потребує
чистки `chr_collegium_reform`, чотирьох ключів на чотирьох мовах і запису в
`docs/EVENTS_LAYOUT_AUDIT_20261027.uk.md`.

## Перевірено й не перевірено

Статичні перевірки: `check_clausewitz_braces.py`,
`check_localisation_replace_layout.py`, `check_chr_prl_kuy_mission_fixes.py`,
`check_donor_mission_ports.py`, `check_script_layer.py`. Маніфест
`docs/data/localisation_replace_manifest.json` оновлено під вилучені й змінені
ключі. EU4 не запускався: нові виклики `chr_flavor.1` і `chr_flavor.3`, новий
модифікатор фіналу, нове ребро KUY і дата Магдебурга в грі не випробувані. Таймінг
`chr_flavor.3` (540 днів) і числа `chr_defeated_rya` — припущення, не виміри.
