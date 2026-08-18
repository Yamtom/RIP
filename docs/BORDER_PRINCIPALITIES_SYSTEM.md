# Порубіжні князівства — технічний опис

## Стан

Обидва ланцюги підключені й мають спрацьовувати. Спершу довелося усунути три
окремі вади: всі ID провінцій у `border_principalities.1-12` указували не туди,
кожен тригер вимагав тег, який на початку партії тими землями не володіє, а
`qasim_khanate.1` не міг створити свого васала. Заблокованих місць у жодному з
ланцюгів більше не видно.

Одне залишається на розсуд автора: **Бєлгород**. Документ
`MAP_REWORK_SUGGESTIONS.md` пропонує окрему провінцію під Ягольдаєву
волость, і тоді подія 3 мала б націлюватися на неї, а не на Курськ. Поки
провінції немає, Ягольдай осідає в `298` Курськ - історично це північний
край волості, тож наближення прийнятне.

## Хто насправді тримає ці землі

Ланцюг писався під Литву: кожен тригер починався з `tag = LIT`. Але мод
власною історією провінцій передає Сіверщину Чернігову **1444.11.1**, за
десять днів до старту гри:

| Провінція | Власник у файлі | Власник на 1444.11.11 |
|---|---|---|
| `4543` Рильськ | LIT | **CHR** |
| `298` Курськ | LIT | **CHR** |
| `1945` Новгород-Сіверський | LIT | **CHR** |
| `4244` Стародуб | LIT | **CHR** |
| `297` Брянськ | LIT | LIT |

CHR — незалежна республіка Сіверського віча зі столицею в Чернігові, не
васал Вільна. Тому з семи подій, що вимагали `tag = LIT`, реально могла
спрацювати лише друга — та, якій вистачало Брянська. Події про Шемячичів у
Рильську, про Ягольдая в Курську та про Стародуб не мали шансів, доки Литва
не відвоює Сіверщину назад.

Тригери тепер приймають `LIT` або `CHR`, а події, які отримує Москва,
беруть сюзерена через `FROM` замість жорсткого тегу — отже ланцюг працює
для того, хто справді тримає землю. Описи подій 5, 8, 10 і 12 називають
сюзерена через `[From.GetName]`, а не «Литву».

## ID провінцій

Ланцюг початково мав ID провінцій, які не збігалися з коментарями поруч; кожен
тригер указував не туди, і найгірше — `295`, це Москва, а не Рильськ. Нижче
наведено ті ID, які справді відповідають описові в
own `history/provinces/` files define. On who володіє them at game start, see the
розділі вище.

| Провінція | ID | Було (хибно) | Де вживається |
|---|---|---|---|
| Рильськ | `4543` | `295` — Москва | події 1, 4, 5 |
| Курськ | `298` | `2408` — Липецьк | події 3, 9, 10 |
| Брянськ | `297` | `296` — Миргород | подія 2 |
| Новгород-Сіверський | `1945` | `1960` — такої провінції немає | події 2, 11 |
| Стародуб | `4244` | `1960` — такої провінції немає | подія 11 |

## Касимовський ланцюг

`QAS` — тег із ванілі: `common/country_tags/00_countries.txt` відсилає до
`countries/QasimKhanate.txt`, а ваніль дає йому осердя на `1778` Касимові.
It is dormant rather than absent: Muscovy володіє Kasimov in 1444 and no vanilla
жодна подія ванілі QAS не звільняє, тож мод може це зробити сам. ID провінцій
у ланцюгу правильні: `1778` — Касимов, `1082` — Казань.

Єдина вада була в `qasim_khanate.1`: він кликав `create_subject` для країни,
якої ще не існувало. Тепер спершу виконується `release = QAS` — так, як це вже
було в `qasim_khanate.3`.

Відтоді ланцюг переробили далі: `qasim_khanate.2` і `.3` тепер захищають себе
прапорцями `qasim_kazan_intervention_resolved` і `qasim_kazan_fate_resolved`, а
`.3` враховує, що Казань може вціліти як васал, а не лише бути завойованою.
Обидві мають `fire_only_once` — для `.3` це було конче потрібно, бо її тригер
лишається істинним після будь-якого варіанта, і подія
was returning every six місяців.

Ця переробка потрапила в `origin/main` із нерозв'язаними маркерами конфлікту
злиття, тобто EU4 узагалі не могла розібрати `QasimKhanate.txt`. Маркери
прибрано, а `tests/check_script_layer.py` тепер падає на них, тож тихо це вже
не повториться.

Ще два коментарі в репозиторії називають ці самі провінції неправильно, і
довіряти їм не варто: `events/SteppeRaiding.txt` зве `1082` Нижнім Яїком, а це
не так. Розбір див. у `docs/WORKSHOP_LISTING.md`.

## Історичний контекст

Між 1444 і 1520 роками порубіжжя Великого князівства Литовського й Московії складалося з багатьох дрібних напівсамостійних князівств, які могли переходити від однієї держави до іншої. Ця хиткість стала однією з головних причин московсько-литовських воєн 1500-1503 і 1507-1508 років, які принесли Москві значні здобутки.

### Ключові історичні князівства

1. **Rylsk Principality (Рыльское княжество)**
   - **Правителі**: Descendants of Dmitri Shemyaka, a Rurikid prince who contested the throne of Moscow
   - **Стан**: Lithuanian vassal with considerable autonomy
   - **Історична доля**: Switched to Muscovy during 1500-1503 war
   - **Значення**: Shemyaka's descendants had legitimate claims to Russian lands, making them valuable diplomatic assets

2. **Hlinsk/Glinski Lands (Глинские земли)**
   - **Правителі**: Glinski family, claiming descent from Mamai (Mongol general)
   - **Військо**: Commanded Tatar cavalry loyal to the family
   - **Повстання**: 1507-1508 Glinski rebellion, switched to Muscovy
   - **Спадок**: Elena Glinskaya (from this family) became mother of Ivan IV (the Terrible)
   - **Значення**: Provided crucial border defense against steppe raids using Tatar troops

3. **Jagoldai Settlement (Ягольдаева волость)**
   - **Правитель**: Jagoldai, Golden Horde pretender
   - **Стан**: Tatar military settlement under Lithuanian protection
   - **Розташування**: South of Kursk, modern Belgorod region
   - **Історична доля**: Passed to Muscovy in 1492-1494 border war
   - **Роль**: Buffer zone against Nogai and Crimean raids

4. **Severian Principalities (Северские княжества)**
   - **Головні міста**: Starodub, Chernigov, Novgorod-Seversky
   - **Перехід**: 1500-1503, major territorial loss for Lithuania
   - **Причина**: Orthodox Rus' princes preferred Muscovite rule
   - **Наслідок**: рівновага сил помітно схилилася до Москви

### The Qasim Khanate (Касимовское ханство)

**Заснування**: 1452
**Засновник**: Qasim, son of Kazan Khan
**Призначення**: Muscovite puppet state to control Tatar vassals and justify claims on Kazan
**Тривалість**: 1452-1681
**Столиця**: Qasim (Gorodets-Meshchersky)

**Історична роль**:
- Давало Москві вірну татарську кінноту
- Тримало суперника на казанський престол, чим виправдовувало втручання
- Показувало, що Москва вміє врядувати мусульманськими підданими
- Після взяття Казані (1552) лишилося почесним титулом

**Головні віхи**:
- 1467-1469: Касим-хан б'є на Казань за московської підтримки
- 1487: касимовського претендента саджають на казанський престол як ляльку
- 1552: після взяття Казані Іваном IV Касимов утрачає вагу
- 1681: остаточно прилучено до Московської держави

### Lipka Tatars (Липки)

**Походження**: Tatars who settled in Grand Duchy of Lithuania/Polish-Lithuanian Commonwealth
**Хронологія**: 14th-17th centuries
**Релігія**: Sunni Islam
**Мова**: Turkic languages, later Polish/Belarusian

**Військова служба**:
- Добірна легка кіннота литовського й польського війська
- Билися з тевтонцями, Москвою, Портою
- Славилися прудкістю, розвідкою та сутичками
- Тримали степовий спосіб воювання посеред Європи

**Оселі**:
- Осідали здебільшого на теренах теперішніх Білорусі й Литви
- Діставали землю за військову службу
- Тримали мечеті й мусульманський звичай
- Увійшли до шляхти, не зрікшись віри

**Правове становище**:
- Свободу віри забезпечила Варшавська конфедерація 1573 року
- Шляхетські привілеї
- Самоуправа у внутрішніх справах
- Обов'язок військової служби короні

## Будова системи подій

### Події порубіжних князівств (простір імен border_principalities)

#### Подія 1: Шемячичі в Рильську
**Тригер**: Lithuania or Chernihiv володіє Rylsk (`4543`), 1444-1500
**Середній час**: 12 місяців
**Вибір A** (AI 80%): Grant vassal autonomy → modifier `shemyaka_rurikid_rule` on province, `border_vassal_buffer` country modifier
**Вибір B** (AI 20%): Direct control → stability or adm power, +3 unrest in Rylsk

#### Подія 2: Глинські, нащадки Мамая
**Тригер**: Lithuania or Chernihiv володіє Bryansk (`297`) or Novgorod-Seversky (`1945`), 1444-1500
**Середній час**: 18 місяців
**Вибір A** (AI 70%): Grant lands to Glinski → `glinski_tatar_settlement` modifier on random Severia/Bryansk province, +1 base manpower, `tatar_border_defense` country modifier (25 років)
**Вибір B** (AI 30%): Refuse petition → +5 prestige, `refused_powerful_family` negative modifier (10 років)

#### Подія 3: Ягольдаєве осадження
**Тригер**: Lithuania or Chernihiv володіє Kursk (`298`), 1444-1480
**Середній час**: 24 місяців
**Вибір A** (AI 75%): Accept Jagoldai → `jagoldai_horde_settlement` modifier on Kursk, +50 mil power, `horde_vassal_buffer` country modifier (25 років)
**Вибір B** (AI 25%): Refuse → +10 legitimacy, +2 unrest in Kursk

#### Подія 4: Рильськ відходить до Москви
**Тригер**: Lithuania or Chernihiv володіє Rylsk with `shemyaka_rurikid_rule`, 1500-1510, Muscovy exists and neighbors Lithuania
**Середній час**: 36 місяців (faster if low legitimacy or at war)
**Вибір A** (AI 60%): Keep loyal → -10 prestige, +10 legitimacy, 30% defects anyway triggering Event 5, 70% keeps `strengthened_border_vassals`
**Вибір B** (AI 10%): Peaceful transfer → Rylsk cedes to Muscovy, -15 prestige, truce
**Вибір C** (AI 30%): War → Declares restoration war on Muscovy

#### Подія 5: Москва приймає Рильськ (кличе подія 4)
**Результат**: Muscovy gains Rylsk, +10 prestige, +5 legitimacy, core CB on Lithuania (10 років)

#### Подія 6: Глинські готують повстання
**Тригер**: Lithuania or Chernihiv has Glinski province, 1507-1515, Muscovy exists
**Середній час**: 24 місяців (faster if low legitimacy or revolts present)
**Вибір A** (AI 40%): Negotiate → -10 prestige, -0.3 років income, 60% Glinski stays loyal (`glinski_appeasement`), 40% triggers Event 7
**Вибір B** (AI 30%): Suppress → -50 mil power, 2 noble rebel stacks spawn (friendly to Muscovy)
**Вибір C** (AI 30%): Exile Glinski → triggers Event 8, removes modifier, +20 devastation on province

#### Подія 7: повстання Глинських (кличе подія 6)
**Результат**: 3 noble rebel stacks spawn, Muscovy gets support rebels CB (5 років)

#### Подія 8: Москва приймає Глинських (кличе варіант 6.c)
**Результат**: +15 prestige, +10 legitimacy, +50 adm power, `glinski_advisors_muscovy` modifier (20 років), core CB on Lithuania (10 років)

#### Подія 9: Ягольдаєвичі міняють зверхника
**Тригер**: Lithuania or Chernihiv володіє Kursk with `jagoldai_horde_settlement`, 1492-1505, Muscovy exists
**Середній час**: 48 місяців (faster if Muscovy stronger or Lithuania at war)
**Вибір A** (AI 50%): Retain loyalty → -0.25 років income, 40% stays loyal, 60% triggers Event 10
**Вибір B** (AI 20%): Let go → Kursk cedes to Muscovy, -10 prestige
**Вибір C** (AI 30%): War → Declares annexation war on Muscovy

#### Подія 10: Москва приймає Ягольдаєвичів (кличе подія 9)
**Результат**: Kursk cedes to Muscovy, removes old modifier, applies `jagoldai_muscovite_service`, +10 prestige, +50 mil power

#### Подія 11: Стародуб міняє зверхника
**Тригер**: Lithuania or Chernihiv володіє Starodub (`4244`) or Novgorod-Seversky (`1945`), 1500-1510, Muscovy neighbor
**Середній час**: 30 місяців (faster if at war or Muscovy militarily stronger)
**Вибір A** (AI 70%): Fight → Muscovy gets core CB (10 років), triggers Event 12
**Вибір B** (AI 30%): Let go → -20 prestige, random Severia/Bryansk province cedes to Muscovy, truce

#### Подія 12: Москва дістає стародубську пропозицію (кличе подія 11)
**Результат**: +15 prestige, +10 legitimacy, core CB on Lithuania (10 років)

### Події Касимовського ханства (простір імен qasim_khanate)

#### Подія 1: заснування Касимовського ханства
**Тригер**: Muscovy володіє Qasim province, 1450-1460, Kazan exists and not allied
**Середній час**: 24 місяців (faster if rival to Kazan or at war with Kazan)
**Вибір A** (AI 80%): Create khanate → `qasim_khanate_capital` on province, `qasim_khanate_vassal` country modifier (постійний), release and vassalize QAS, QAS gets `kazan_pretender_claims`, Kazan gets negative opinion
**Вибір B** (AI 20%): Direct control → +50 adm power, +1 base tax on Qasim

#### Подія 2: Касимов б'є на Казань
**Тригер**: Muscovy has QAS vassal with claims, 1467-1550, Kazan exists, not at war/allied with Kazan
**Середній час**: 120 місяців (faster if rival to Kazan or Kazan weak)
**Вибір A** (AI 60%): Military support → Declares restoration PU war on Kazan, QAS -20 liberty desire
**Вибір B** (AI 30%): Diplomatic pressure → Kazan gets threatened opinion, -5 prestige
**Вибір C** (AI 10%): Restrain vassal → QAS +10 liberty desire, +25 dip power

#### Подія 3: доля завойованої Казані
**Тригер**: Muscovy володіє Kazan capital, 1467-1552, QAS exists as vassal, Kazan doesn't exist
**Середній час**: 6 місяців
**Вибір A** (AI 40%): Install Qasim Khan → Kazan area gets QAS core, release and vassalize QAS (now ruling Kazan), QAS gets `muscovite_puppet_khan`, QAS -30 liberty desire
**Вибір B** (AI 60%): Annex directly → Kazan area gets `conquered_khanate` modifier (20 років), QAS +20 liberty desire

#### Подія 4: прилучення Касимовського ханства
**Тригер**: Muscovy has QAS vassal, 1550-1700
**Середній час**: 240 місяців (faster if Kazan conquered or high ADM)
**Вибір A** (AI 70%): Integrate → Inherit QAS, Qasim province gets `former_qasim_khanate`, country gets `tatar_nobility_integrated` (постійний)
**Вибір B** (AI 30%): Keep vassal → QAS -20 liberty desire, QAS gets `loyal_tatar_vassal`

#### Подія 5: липки просяться на осідок
**Тригер**: Lithuania, 1440-1500, володіє provinces in White Ruthenia/Minsk/Pripyat areas
**Середній час**: 60 місяців
**Вибір A** (AI 80%): Welcome Lipka → Random qualifying province gets `lipka_tatar_settlement`, +1 base manpower, country gets `lipka_tatar_cavalry_tradition` (постійний)
**Вибір B** (AI 20%): Refuse → +5 prestige, +25 adm power

#### Подія 6: вірність липків
**Тригер**: Commonwealth (tag PLC), 1569-1700, has province with `lipka_tatar_settlement`
**Середній час**: 120 місяців
**Вибір A** (AI 70%): Reward loyalty → -0.2 років income, all Lipka provinces get `lipka_tatar_privileges` (20 років), country gets `tatar_nobility_service` (25 років)
**Вибір B** (AI 30%): Status quo → +25 mil power

## Довідник модифікаторів

### Модифікатори провінцій

| Модифікатор | Дія | Тривалість | Хто накладає |
|----------|---------|----------|------------|
| `shemyaka_rurikid_rule` | -1 unrest, +15% defensiveness, +10% garrison | Постійний | border_principalities.1 |
| `glinski_tatar_settlement` | +20% local manpower, +1 local hostile attrition | Постійний | border_principalities.2 |
| `jagoldai_horde_settlement` | +25% local manpower, +1.5 local hostile attrition | Постійний | border_principalities.3 |
| `glinski_appeasement` | -2 unrest, -15% local tax | 10 років | border_principalities.6.a |
| `jagoldai_muscovite_service` | +15% manpower, +10% garrison, +1 hostile attrition | Постійний | border_principalities.10 |
| `qasim_khanate_capital` | +20% local manpower, +10% garrison | Постійний | qasim_khanate.1 |
| `conquered_khanate` | +5 unrest, +10% local autonomy | 20 років | qasim_khanate.3.b |
| `former_qasim_khanate` | +10% local manpower | Постійний | qasim_khanate.4.a |
| `lipka_tatar_settlement` | +20% local manpower, +15% garrison | Постійний | qasim_khanate.5 |
| `lipka_tatar_privileges` | -2 unrest, +15% manpower, +20% garrison | 20 років | qasim_khanate.6.a |

### Модифікатори країни

| Модифікатор | Дія | Тривалість | Хто накладає |
|----------|---------|----------|------------|
| `border_vassal_buffer` | +0.5 hostile attrition, -10% fort maintenance, +1 diplomat | 20 років | border_principalities.1 |
| `tatar_border_defense` | +5% cavalry power, +25% flanking, -15% fort maint, +0.75 hostile attrition | 25 років | border_principalities.2 |
| `refused_powerful_family` | -0.25 legitimacy | 10 років | border_principalities.2.b |
| `horde_vassal_buffer` | -10% cavalry cost, +10% cavalry power, +1 hostile attrition | 25 років | border_principalities.3 |
| `strengthened_border_vassals` | +15% vassal income, +1 diplomatic reputation, -10% fort maintenance | 10 років | border_principalities.4.a success |
| `glinski_loyalty` | +0.5 legitimacy, +10% cavalry power, +1 diplomatic reputation | 20 років | border_principalities.6.a success |
| `jagoldai_loyalty` | +10% cavalry power, -10% cavalry cost, +0.5 hostile attrition | 15 років | border_principalities.9.a success |
| `glinski_advisors_muscovy` | +2 diplomatic reputation, +0.5 legitimacy, -15% advisor cost, +5% cav power | 20 років | border_principalities.8 |
| `lipka_tatar_cavalry_tradition` | +15% cavalry power, +25% flanking, -10% cavalry cost | Постійний | qasim_khanate.5 |
| `tatar_nobility_service` | +10% cavalry power, +1 diplomatic reputation, +2 tolerance heathen | 25 років | qasim_khanate.6.a |
| `severian_princes_defection` | -1,0 престижу, -1 дипломатичної поваги, -0,5 легітимності | **описаний, ніде не накладається** | — |
| `muscovite_expansion_momentum` | +1,0 престижу, +1,0 легітимності, +1 дипломатичної поваги, -10% ціни осердь | **описаний, ніде не накладається** | — |
| `border_war_preparation` | +5% бойового духу, +10% відновлення живої сили, -15% утримання фортець | **описаний, ніде не накладається** | — |
| `qasim_khanate_vassal` | +10% cavalry power, +1 diplomatic reputation, +20% vassal income | Постійний | qasim_khanate.1 |
| `kazan_pretender_claims` | -10% AE impact, -15% unjustified demands | Постійний | qasim_khanate.1 |
| `muscovite_puppet_khan` | -20 liberty desire, -1 diplomatic reputation | Постійний | qasim_khanate.3.a |
| `tatar_nobility_integrated` | +10% cavalry power, +2 tolerance heathen, +1 diplomatic reputation | Постійний | qasim_khanate.4.a |
| `loyal_tatar_vassal` | +15% cavalry power, -30 liberty desire | Постійний | qasim_khanate.4.b |

## Інтеграція з наявними системами

### Степові набіги
Порубіжні князівства стикуються з механікою степових набігів:
- Татарські осади (Глинські, Ягольдаєві, липківські) дають `local_hostile_attrition`
- Вони зменшують шкоду від подій `steppe_raid.1-7`
- Модифікатор країни `tatar_border_defense` складається із `zasechnaya_cherta`
- Провінції з татарськими модифікаторами рідше стають ціллю набігів

### Козацький стан
Порубіжні князівства впливають на козацький стан:
- Татарська кіннота Глинських змагається з козацтвом за вплив
- Відхід сіверських князів може хитнути вірність козацтва
- Перехід православних князівств до Москви скріплює козацьке прилучення
- Липки в Речі Посполитій дають іншу кінноту, розбиваючи козацьку однину

### Московське розширення
Система дає історичне підґрунтя московському рухові на захід:
- Шемячичі дають претензії на литовське порубіжжя
- Відхід Глинських приносить відомості й воєвод
- Перехід сіверських князів відтворює «збирання руських земель»
- Касимовське ханство показує вміння врядувати неруськими підданими

### Внутрішнє життя Литви
Литві та Речі Посполитій система дає внутрішні клопоти:
- Порубіжні васали тягнуть кошти (данина)
- Загроза відходу змушує тримати військо
- Татарські осади породжують багатовірʼя
- Православні князівства опираються прилученню

## Поведінка ШІ

### Ваги для литовського ШІ
- **Дати васалові самоуправу**: 70-80% (безпека кордону цінна)
- **Прийняти татарські осади**: 70-80% (військова потреба)
- **Боротися за васалів**: 60-70% (престиж важить)
- **Домовлятися з бунтівниками**: 40% (шкода витрат)

### Ваги для московського ШІ
- **Створити Касимовське ханство**: 80% (велика стратегічна вага)
- **Підтримати касимовські претензії**: 60% (хижо, але обачно)
- **Прийняти перебіжчиків**: 100% (дармова земля)
- **Прилучити чи посадити ляльку в Казані**: 60% прилучити / 40% лялька

### Як модифікатори змінюють ШІ
- Мала легітимність: васали відходять швидше (×0,7-0,8 MTTH)
- Під час війни: більший ризик відходу (×0,6-0,8 MTTH)
- Сильне військо: відхід повільніший (×1,2-1,5 MTTH)
- Союз із суперником: частину подій замикає

## Історичність проти гри

### Що взято з історії
✅ Роль Шемячичів у Рильську
✅ Повстання й відхід Глинських (1508)
✅ Ягольдаєве осадження як прокладка
✅ Перехід сіверських князів (1500-1503)
✅ Касимовське ханство як московське знаряддя
✅ Липки на польсько-литовській службі
✅ Напруга між православними й католиками

### Що спрощено заради гри
⚠️ Стиснення часу: події настають у вужчих вікнах
⚠️ Воля гравця: історичного кінця можна уникнути
⚠️ Механіка: окремі модифікатори сильніші за історичну вагу події
⚠️ Васалітет: система EU4 не передає всієї плутанини тодішніх залежностей
⚠️ Тег Касимова: у грі він є, але звільняти його доводиться подією

### Баланс Considerations
- Вигоди татарської кінноти сильні, але історично виправдані
- Загроза відходу змушує гравця вкладатися в легітимність і військо
- Здобутки Москви вагомі, але вимагають дій гравця
- Литва може все втримати, якщо врядує вправно
- Винагороджує історичний спосіб гри: терпима Литва, хижа Москва

## Перелік для перевірки

### Тригери подій
- [ ] Подія про Шемячичів настає в Литви 1444-1500
- [ ] Подія про Глинських настає в Литви із Сіверщиною чи Брянськом
- [ ] Подія про Ягольдая настає в Литви з Курськом
- [ ] Подія про відхід Рильська настає 1500-1510
- [ ] Повстання Глинських настає 1507-1515
- [ ] Відхід Стародуба настає 1500-1510
- [ ] Заснування Касимова настає в Москви 1450-1460
- [ ] Похід Касимова на Казань настає після 1467
- [ ] Осадження липків настає в Литви 1440-1500

### Ланцюги подій
- [ ] Відхід Рильська кличе подію прийняття в Москви
- [ ] Якщо перемовини провалились, бунт Глинських переростає в повстання
- [ ] Вигнання Глинських кличе подію прийняття в Москви
- [ ] Відхід Ягольдаєвичів кличе подію прийняття в Москви
- [ ] Перехід Стародуба кличе подію прийняття в Москви

### Модифікатори Application
- [ ] Модифікатори провінцій накладаються правильно
- [ ] Модифікатори країни складаються як слід
- [ ] Строки відлічуються правильно
- [ ] Постійний modifiers remain after save/load
- [ ] Збиткові модифікатори (завоювання, відмова) накладають кари

### Поведінка ШІ
- [ ] Литва під ШІ пристає на васальні угоди понад 70% разів
- [ ] Москва під ШІ створює Касимовське ханство понад 80% разів
- [ ] Литва під ШІ б'ється за важливих васалів
- [ ] ШІ час від часу пристає на мирну передачу
- [ ] Москва під ШІ підтримує касимовські претензії

### Стик із рештою
- [ ] Татарські осади зменшують шкоду від набігів
- [ ] Відходи дають приводи до війни й претензії
- [ ] Касимов виправдовує втручання в Казань
- [ ] Липки дають вигоди кінноті
- [ ] Порубіжні війни починаються правильно

### Баланс
- [ ] Москва не розповзається надто швидко
- [ ] Відходи не ламають Литву
- [ ] Татарські вигоди не завеликі
- [ ] Вибір гравця важить
- [ ] Історичний кінець досяжний, але не гарантований

## Створені файли/Modified

### Нові файли
1. **events/BorderPrincipalities.txt** — 12 подій про зміну зверхника
2. **events/QasimKhanate.txt** — 6 подій про Касимов і липків
3. **common/event_modifiers/border_principalities_modifiers.txt** — понад 30 модифікаторів
4. **localisation/border_principalities_l_english.yml** — локалізація подій і модифікаторів
5. **localisation/qasim_khanate_l_english.yml** — локалізація касимовських подій
6. **docs/BORDER_PRINCIPALITIES_SYSTEM.md** — цей опис

### Змінені файли
Жодного: усе нове лежить в окремих файлах

### Перевірки

`python tests/check_script_layer.py` покриває цю систему: ловить розбіжні
дужки й хибне кодування, повторені ID подій, необ'явлені простори імен, текст
подій без локалізації, модифікатори без локалізації та записи модифікаторів у
хибній області. ID провінцій він не знає — їх треба звіряти з
`history/provinces/`, саме так і знайшлися помилки вище.

## Ідеї майбутніх розширень

1. **Уділи**: поширити на інші краї (Твер, Рязань, Ярославль)
2. **Династичні претензії**: родовід Рюриковичів як підстава для претензій
3. **Татари на службі**: глибша механіка татарської знаті в московському війську
4. **Литовські реформи**: засоби проти відходів
5. **Спадкоємство в Касимові**: події про зміну ханів і внутрішні чвари
6. **Культура липків**: окрема культурна група з власними рисами
7. **Навернення**: механіка переходу татарських васалів у православ'я
8. **Стани**: стик зі шляхтою й духівництвом задля чвар
9. **Зміни на карті**: більше провінцій на Сіверщині, поділ Брянської області
10. **Постання Речі Посполитої**: окремі події про долю васалів після унії
