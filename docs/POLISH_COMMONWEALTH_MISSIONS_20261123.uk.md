# Польща й Річ Посполита: місії за рецензією 23 листопада 2026

Файл `missions/zzz_Poland_Commonwealth_Rework.txt` (раніше `Poland_Commonwealth_Rework.txt`) додає
`POL` і `PLC` Сейм, Гадяч, військову реформу й торгівлю зерном у колонки 1 і 2. Твердження про ваніль
звірено з `Polish_Missions.txt` і `SCA_Polish_Missions.txt` встановленої 1.37.5. У самій грі нічого не запускали.

Рецензію паралельно виправляла лінія роботи в `main` (коміти `f04e1b66`, `7fb3e6c9`, `c7d93e5f`). Ця гілка
спершу робила те саме, тож після rebase на `main` лишилося тільки те, чого там не було; решту взято з `main`.

## 1. Що зробили обидві лінії однаково (стоїть версія `main`)

- Перейменування на `zzz_Poland_Commonwealth_Rework.txt`. За абеткою `Poland_` стоїть перед `Polish_` і
  `SCA_`; серії колонки складаються одна під одною, місія стає на `max(попередній рядок + 1, position)`.
  Файл із `position = 11..18`, завантажений першим, відсуває курсор на рядок 18, і ванільне дерево осідає під нього.
- `generic = no` в обох серіях. Коментар у ванільному `00_Generic_missions.txt` каже, що негенерична серія
  перекриває загальну в тій самій колонці, а `POL` і `PLC` мають такі серії в колонках 1 і 2 в обох ванільних
  файлах. Це висновок із коментаря, не з гри.
- `pol_codify_hadiach_privileges`: `calc_true_if = { amount = 3 any_owned_province = {...} }` ніколи не стає
  істинним, бо `any_*` це один тригер і дає щонайбільше 1. Замість нього `num_of_owned_provinces_with`
  з `value = 3`, `region = ruthenia_region` і `has_seat_in_parliament = yes`.
- Дублі умов у `pol_hadiach_commission`, `pol_codify_hadiach_privileges` і `pol_triatomic_commonwealth`
  (прихована копія в `custom_trigger_tooltip` + відкрита) замінено однією `custom_trigger_tooltip` з тригером усередині.
- `mos_rus_russian_patriarchate` у `DOM_Russia_Missions.txt` дає нагороду й `russian_orthodox`
  (`rip_faith_is_eastern_orthodox = yes`); `main` виправив і дві умови для провінції 295.

## 2. Що додає ця гілка

| Зміна | Чому |
|---|---|
| `NOT = { map_setup = map_setup_random }` у `potential` обох серій | Як у ванільних серіях. У `main` цієї умови не було. |
| `pol_triatomic_compact`: `promote_culture_cost = -0.25` замість `culture_conversion_cost = -0.15` | Дешева асиміляція суперечить рівноправній федерації; дешеве прийняття культури їй відповідає (у ванілі так працює ідея «Cultural Melting Pot»). Значення −0,25 береться з ванільних подієвих модифікаторів. |
| Пояснення порядку завантаження й `calc_true_if` у заголовку й біля місії | Щоб префікс `zzz_` не прибрали за зайвий. |
| `tests/check_poland_commonwealth_missions.py` | Тримає ім'я файла (сортується після обох ванільних), `generic = no`, `map_setup`, один рядок підказки на умову, модифікатор і Патріархат. Заодно шукає нездійсненні `calc_true_if` в усіх скриптах (пропускає блоки з `all_*`, `custom_trigger_tooltip` і ванільною формою `desc =`). |

## 3. Чого не перевірено

- Розкладку колонок 1–2 для `POL` і `PLC` у самій грі, з DLC «Lions of the North» і без нього. У першому
  випадку ванільні серії колонок беруться з `SCA_Polish_Missions.txt`, у другому з `Polish_Missions.txt`.
  Модель складання взято з вимірів в інших деревах (`docs/HANDOFF.md`), а цього дерева не виміряно.
- Що `generic = yes` справді ховало серію: висновок із коментаря ванільного файла.
- Що `custom_trigger_tooltip` із тригером усередині справді перевіряє цей тригер, а не лише малює рядок.
  Так пишуть у ванілі, але на цих трьох місіях це не вимірювали.
