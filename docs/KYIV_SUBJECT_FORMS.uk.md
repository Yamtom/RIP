# Уділ, князівство, торгове місто: як влаштовані піддані київського кола

Складено 21 листопада 2026 року за скриптом на `main` (`31e807b7`) і виправлено того ж дня за поясненням автора. У грі нічого з описаного не перевірялося.

У моді кілька речей мають близькі назви й майже однакові наслідки: уділ, князівство, старший уділ, «удільне князівство», торгове місто, «апанажні князівства». Нижче — що з цього є справжнім типом підданого, що є урядом, що лише назвою події. Перелік місць, де створюються піддані цих двох типів, перевіряє `tests/check_kyiv_subject_forms.py`: додати новий шлях, не оновивши цей документ, не вийде.

## 1. Словник

| Термін | Що це насправді | Рушійна назва |
|---|---|---|
| **Уділ** | Загальне слово: земля, яку князь дому Рюриковичів тримає з наділу старшого князя. Окремого типу підданого немає, є два види тримання. | немає |
| **Князівство** (Princedom) | Спадковий уділ, «вотчина». Не анексується й не інтегрується, ранг не вищий за герцогство, платить 0,5, займає дипломатичний слот, у ліміт сил не дає нічого. | підтип `princedom` (`RIP_shared_ruthenian_subject_types.txt`) |
| **Старший уділ** (Senior Udil) | Ротаційний уділ. Не займає слота, платить 0,25 і віддає 0,5 ліміту сил; наділ спливає зі зміною старшого князя (`rip_tenure_lapsed`). | підтип `senior_udil` (`RIP_KIE_subject_types.txt`) |
| **Удільне князівство** (Appanage Principality) | **Уряд**, а не тип підданого: реформа, що лишає династію й фіксує ранг на герцогстві. Видається лише скриптом або рушієм. | реформа `principality_appanage` |
| **Торгове місто** | Механіка Mare Nostrum: реформа з `can_form_trade_league` і `trade_city_reform` дозволяє зробити провінцію торговим містом. Для `kyivan_rus_reform` таке місто дістає реформу `principality_appanage`, а `on_country_released` робить його князівством власника. Потрібен DLC Mare Nostrum. | `trade_city_reform = principality_appanage` і `on_country_released` |
| **Вільне торгове місто** | Лише модифікатор провінції `KIE_free_trade_city` (місія `KIE_free_trade_cities`, подія `kyiv_trade_houses.2`). Піддатного не створює. | модифікатор |
| **Апанажні князівства** | Назва події про Твер, Рязань, Ярославль, Верхню Оку, Смоленськ і Мстиславль: незалежні держави вибирають між Москвою і Вільнюсом. Не піддані й не уділи. | `appanage_principalities.*` |
| `appanage` (ваніль) | Російський тип підданого з гри. Мод його не створює й не перевіряє. | ваніль |

Простіше: князівство і старший уділ — це **два тримання одного уділу** (спадкове й ротаційне); «удільне князівство» — **уряд** того, хто тримає уділ; торгове місто — **шлях**, яким спадковий уділ виникає з міста; вільне торгове місто й апанажні князівства до уділів не належать.

## 2. Хто що створює

| Шлях | Файл | Тип | Модифікатор `rip_held_as_an_udil` | Реформа `principality_appanage` |
|---|---|---|---|---|
| Дипломатична дія «Grant an Udil» (реформа не шогунат) | `common/new_diplomatic_actions/RIP_KIE_diplomatic_actions.txt` | `princedom` | так | так, лише монархії |
| Та сама дія під `kyivan_shogunate_reform` | там само | `senior_udil` | так | так, лише монархії |
| Рішення `kyiv_establish_princedoms` (шогунат) | `decisions/KyivTriggers.txt` | `senior_udil` | **ні** | **ні** |
| Подія `kyiv_shogunate.1` (кілька держав за варіантами) | `events/RIP_KIE_KyivShogunate.txt` | `senior_udil` | **ні** | **ні** |
| Подія `kyiv_shogunate.2` (перехід старшинства) | там само | `senior_udil` | **ні** | так |
| Подія `kyiv_independence.3` (`KRU` робить київського володаря князівством) | `events/RIP_KIE_kyiv_independence.txt` | `princedom` | ні | ні |
| Дія «Гадяч» Речі Посполитої | `common/new_diplomatic_actions/RIP_PLC_diplomatic_actions.txt` | `princedom` | ні | ні |
| Торгове місто, зроблене під `kyivan_rus_reform` (потрібен Mare Nostrum) | `common/on_actions/RIP_KIE_on_actions.txt` | `princedom` | так | через `trade_city_reform` |

Ланцюг торгового міста складається з трьох ланок, які перевіряє `tests/check_kyiv_subject_forms.py`:

1. `kyivan_rus_reform` у двох секціях `conditional` для Mare Nostrum задає `can_form_trade_league = yes` і `trade_city_reform = principality_appanage` (`RIP_KIE_KRU_government_reforms.txt`).
2. Реформа `principality_appanage` існує й видається лише скриптом (`potential = { has_reform = principality_appanage }`), як і ванільна `trading_city` (`RIP_shared_ruthenian_government_reforms.txt`).
3. Хук `on_country_released` бачить, що випущена країна має `principality_appanage`, а випускач має `kyivan_rus_reform`, і створює `princedom` та модифікатор `rip_held_as_an_udil`.

Що діє на підданих:

- `kyivan_seniority_mechanic` (реформа `kyivan_rus_reform`) — три кнопки: з'їзд, уділ, дружина. Читає і `princedom`, і `senior_udil`.
- `kyivan_seniorate_mechanic` (реформа `kyivan_shogunate_reform`) — три накопичувані сили. Читає лише `senior_udil`.
- Дипломатичні дії «Grant the Princely Charter», «Grant an Udil», «Revoke the Udil», «Re-grant the Princely Udil» — за реформою власника.

## 3. Знайдені розбіжності й відкриті питання

1. **Гілка торгового міста задумана живою, у грі не перевірена.** Спершу тут стояло, що вона не спрацьовує, бо торгові міста робить лише республіка. Це повторювало старий коментар у `RIP_shared_ruthenian_government_reforms.txt` і було хибним: ванільні монархії `plutocratic_reform` і `livonian_trade_monarchy` мають таку саму секцію `conditional` (Mare Nostrum, `can_form_trade_league`, `trade_city_reform`). Коментар виправлено. Невідомо дві речі: чи рушій приймає `principality_appanage` як реформу торгового міста (ванільна `trading_city` має ще `is_trading_city = yes`, а в `principality_appanage` його немає) і чи для торгового міста спрацьовує `on_country_released` (ванільний коментар до нього: «this = Released country, FROM = Releasing country»). Ланцюг зникає, коли реформу `kyivan_rus_reform` замінює одна з реформ `kyiv_path_*`: шогунат і цесарство `trade_city_reform` не задають, а віче має ванільне `trading_city`.
2. **Ротація рахує не тип, а модифікатор.** `rip_recalculate_the_rota_effect` (`common/scripted_effects/rip_rota_effects.txt`) рахує піддатних із `rip_held_as_an_udil`. Старші уділи, створені рішенням `kyiv_establish_princedoms` і подіями шогунату, його не мають, тож не потрапляють у лік ротації й не дають їй ціни, хоч є справжніми `senior_udil`. Реформу `principality_appanage` дістає лише старий дім у `kyiv_shogunate.2`.
3. **Дві «регранти» з майже однаковою назвою.** Кнопка механіки `kyiv_regrant_the_udil` («Regrant the Udil», посунути князя щаблем вгору або наділити родича) і дипломатична дія `rip_regrant_the_udil` («Re-grant the Princely Udil», підтвердити конкретного князя) — різні речі.
4. **Три назви для спадкового тримання:** тип «Princedom», уряд «Appanage Principality», модифікатор «Held as an Udil».
5. **Сторонній збіг назв:** `appanage_principalities.*` (незалежні держави) і ванільний `appanage` не мають стосунку до уділів.
6. Текст `princedom_is_our` називав князівство «principality»; виправлено на «princedom».

Пункт 1 перевіряється лише в грі (потрібен Mare Nostrum). Пункти 2–4 — рішення автора, у скрипті не змінено: пункт 2 міняє ціну ротації для шогунату, пункти 3 і 4 — те, що гравець бачить у списках дій, реформ і підданих.
