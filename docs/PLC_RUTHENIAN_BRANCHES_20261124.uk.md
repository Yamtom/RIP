# Дев'ять русинських гілок Речі Посполитої (24 листопада 2026)

Автор просив дев'ять гілок подій, рішень чи катастроф про русинську культуру чи русинський регіон для `PLC`, з натхненням від
ванільних `flavorPOL`, `ElectiveMonarchy`, `flavorLIT`, `flavorTEU`, `libirumveto`, `estate_cossacks`, `WomenInHistory` і рішень
`Poland`, `TheCommonwealth`, `LiberumVeto`, `EstateActionsCossacks`, і без дублювання того, що в моді вже є. Спершу перелік наявного, потім
дев'ять нових гілок.

## 1. Що вже було для `PLC` (не повторювалось)

| Що | Де | Про що |
|---|---|---|
| `union_dispute.1–11`, рішення `lit_hold_the_union_on_our_terms`, `lit_take_a_separate_crown`, `pol_press_the_incorporation` | `events/RIP_shared_commonwealth_UnionDispute.txt`, `decisions/UnionDispute.txt` | суперечка Вільнюса й Кракова до й після Люблінської унії |
| `lit_guarantee_the_orthodox_lords`, `lit_confirm_the_statute` | `decisions/UnionDispute.txt` | рішення Великого князівства (тег `LIT`): гарантії православним і верховенство Статуту |
| `free_election.1–4` | `RIP_shared_commonwealth_FreeElection.txt` | безкоролів'я, pacta conventa, кандидат ззовні, рокош |
| `deluge.1–6`, `pl_reformation.1–5` | `RIP_shared_commonwealth_TheDeluge.txt`, `…CommonwealthReformation.txt` | Потоп; магнати й реформація, Варшавська конфедерація |
| `hadiach.1–6`, дипдія `rip_offer_hadiach_terms` | `events/RIP_HET_Hadiach.txt`, `common/new_diplomatic_actions/RIP_PLC_diplomatic_actions.txt` | Гадяцька унія 1658 |
| `khmelnytsky_events.1–11`, катастрофа `khmelnytsky_uprising` (`PLC` у ній теж) | `RIP_shared_cossack_KhmelnytskyUprisings.txt`, `common/disasters/shared_ruthenian_disasters.txt` | повстання 1648 року |
| `haidamaky.1–3`, `west_ukraine_history.1–13`, `uniate_church.*`, `uniate_crown.1–8`, `zaz.*` | відповідні `RIP_shared_*` | гайдамаки, звичаї руських земель, унія, козацькі ради |
| `ask_to_expand_the_register` та друга сторона реєстру | `RIP_ZAZ_diplomatic_actions.txt` | реєстр: Курукове, Переяслав, Бориспіль |
| `pol_*`: 10 місій | `missions/zzz_Poland_Commonwealth_Rework.txt` | сейм, Гадяч, військо, торгівля |
| `estate_magnates` для `PLC` | `common/estates/RIP_magnates.txt` | магнатський стан |

Нових гілок немає там, де вже є повна гілка: реєстр, Гадяч, Потоп, унія, Хмельниччина й Коліївщина лишились як були.

## 2. Дев'ять нових гілок

Усе тільки для тега `PLC`. Файли: `events/RIP_shared_commonwealth_RuthenianBranches.txt` (24 події), `decisions/RIP_PLC_RuthenianDecisions.txt`
(3 рішення), `common/disasters/plc_disasters.txt` (1 катастрофа), `common/event_modifiers/RIP_PLC_ruthenian_modifiers.txt` (15
модифікаторів), `common/scripted_triggers/rip_plc_ruthenian_triggers.txt` (брами «русинські землі», «Лівобережжя»).

| № | Гілка (простір імен) | Що в ній | Історичне підґрунтя | Натхнення з ваніли |
|---|---|---|---|---|
| 1 | Ієрархія без ліцензії, 1620–1632 (`plc_hierarchy`) | 3 події: висвячення 1620 → Статті пацифікації 1632 → «Братства пам'ятають» (якщо справу поховали) | патріарх Феофан, Йов Борецький; пацифікація 1632 | `libirumveto` (сейм як гальмо), `flavorTEU.36` «The Orthodox Faith of Ruthenia» |
| 2 | Степ за Дніпром, 1620–1648 (`plc_zadnieprze`) | 2 події і рішення `plc_charter_left_bank_town` | колонізація Лівобережжя магнатами за «слободами» | `estate_cossacks` (`cossack_estate_events.1` «Colonization of the Steppes»), `flavorTEU.45` |
| 3 | Мова Статутів, 1588 і 1696 (`plc_chancery`) | 2 події і рішення `plc_recognise_ruthenian_chancery` (прийнята культура `ruthenian`) | Третій Литовський статут; сеймова ухвала 1696 про польську в канцелярії | `flavorPOL` («Statute of Piotrkow»), `Poland.txt` (форма рішення) |
| 4 | Княжі доми, 1590–1649 (`plc_princes`) | 3 події: двір → спадкоємець у латинському обряді → «малі королі» | Острозькі, Вишневецькі, Заславські; Ярема Вишневецький | `flavorPOL.23` «Little Kings Uprising», `flavorLIT.7–9` |
| 5 | Втеча від фільварків, 1590–1648 (`plc_flight`) | 3 події: села порожніють → погоня чи слободи | Статут 1588 про біглих селян; вільні роки | `estate_cossacks` (`cossack_estate_events.12` «Unrest among the Cossacks»), `EstateActionsCossacks` |
| 6 | Кам'янець і Бучач, 1672–1699 (`plc_buchach`) | 3 події: падіння → відмова сейму й Хотин → Карловіц | облога 1672, Бучацький договір, Хотин 1673, Карловіц 1699 | `flavorPOL.3488`, `flavorPOL.3485` |
| 7 | Київ і Вічний мир, 1667–1686 (`plc_eternal_peace`) | рішення `plc_eternal_peace_with_moscow` і 2 події | Андрусів 1667, Вічний мир 1686 | `TheCommonwealth.txt` (великі рішення), `LiberumVeto.txt` |
| 8 | Дисидентське питання й Барська конфедерація, 1766–1772 (`plc_bar`) | катастрофа `plc_confederation_of_bar` і 3 події | сейм Рєпніна 1767–68, Бар 1768 | `flavorPOL.10–13` (конфедерація, Пацифікаційний сейм), `libirumveto` |
| 9 | Покровителі русинської науки, 1590–1650 (`plc_patrons`) | 3 події: дар Гальшки Гулевичівни, вдовина фундація, Київський колегіум | 1615: дар Київському братству; 1632: злиття шкіл у Київський колегіум | `WomenInHistory`, `flavorLIT.15, .18` |

### Як гілки з'єднано між собою (прапорці)

- Пацифікація (`plc_hierarchy_settled`, `plc_hierarchy_half`) відкриває Київський колегіум (`plc_patrons.3`); поховання справи
  (`plc_hierarchy_buried`) викликає «Братства пам'ятають».
- Великий дар Лівобережжя (`plc_zadnieprze_granted`) і латинське виховання спадкоємців (`plc_princes_latinised`) відкривають «малих
  королів» (`plc_princes.3`).
- Рішення й відмова у `plc_bar.1` (`plc_dissidents_settled`, `plc_dissidents_refused`) дозволяють катастрофі стартувати (рік 1768, не
  пізніше 1775); `plc_bar.2` і `plc_bar.3` відкривають і закривають її.
- Прапорці `plc_ruthenian_chancery` і `plc_eternal_peace_signed` вмикають рішення своєї гілки; `survived_bar_confederation` стримує
  повторний старт катастрофи.

## 3. Чого свідомо не робилося

- Жодна подія не змінює культуру провінцій; віру змінює лише `plc_princes.2` і лише в одній русинській провінції (на католицтво).
- Усі зміни стану лише з готових механізмів мода: `rip_estate_mood_effect` (стани `estate_magnates`, `estate_church`, `estate_cossacks`),
  `add_country_modifier`, `add_province_modifier`, `cede_province`, `create_alliance`. Без `else_if`, `add_opinion` (відомо, що
  `add_opinion` в `else_if` не зберігається), без `calc_true_if` (рахує лише прямі тригери).
- ШІ не бере рішення `plc_recognise_ruthenian_chancery` і `plc_eternal_peace_with_moscow` (`factor = 0`): обидва — вибір гравця.

## 4. Перевірка

`tests/check_plc_ruthenian_branches.py` (у гейті): набір подій, рішень і катастроф відповідає таблиці; датові вікна збігаються
з документованими; кожна датована подія має `tag = PLC`, `mean_time_to_happen` і браму русинських земель; кожна `is_triggered_only`
подія має викликача (визначення подій не рахуються викликами); кожен прочитаний прапорець десь виставляється; кожен доданий
модифікатор визначений, а провінційні мають лише ключі `local_…`; тексти є в англійській і в трьох файлах `replace/`; жодних
`else_if`, `add_opinion`, `calc_true_if`. П'ятнадцять зіпсованих варіантів (виправлена вимога викликача, розширене вікно, тег
`POL`, знята брама, перейменований прапорець, видалений модифікатор, ключ країни в провінційному модифікаторі, відсутні тексти
у французькій, німецькій, іспанській і англійській, `else_if`, рішення без `tag = PLC`, зламаний кінцевий виклик катастрофи,
знятий заголовок) ловляться. Хеші `catalogue_key_digests` у `docs/data/localisation_replace_manifest.json` перераховано.

## 5. Чого не перевірено

У грі нічого не запускалося: ні того, що події стріляють у вікнах (середній час очікування підібрано на око), ні арифметики нагород
(+0,2 річного доходу, ±10 до лояльності станів, 5–10 престижу), ні запуску катастрофи Бара (прогрес складено за зразком Хмельниччини),
ні дії `cede_province`/`create_alliance` у `plc_eternal_peace_with_moscow` та `plc_buchach.1/.3`. Відкрите питання автору: чи відмовитися від прямої
передачі Каменця (`281`) в `plc_buchach.1`, лишивши його лише подією `plc_buchach.3`. Англійські тексти копіюються у `replace/` без
перекладу.
