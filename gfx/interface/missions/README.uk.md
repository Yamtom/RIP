# Іконки місій RIP

Тека містить 14 власних іконок і PNG-майстри у `source/`. Шість нових
ілюстрацій доповнюють Петра Могилу, Магдебурзьке право та шість закритих
слотів гілок Чернігова й Закарпаття.

## Теми та підключення

Для наведених нижче майстрів ідентифікатор спрайта має вигляд
`rip_gfx_mission_<назва майстра>_icon`.

| Майстер PNG | Сюжет | Місії |
| --- | --- | --- |
| `mazepa_patronage` | Книга, перо та українське бароко; меценатство Мазепи | `het_mazepa_renaissance` |
| `dnieper_chaika` | Козацька чайка на Дніпрі | `prl_river_flotilla`, `prl_trade_dominance`, `het_dnieper_control`, `ZAZ_chaiky_raids` |
| `ruthenian_granaries` | Сніп, збіжжя та дерев'яна комора на чорноземі | `prl_chernozem_development`, `PDL_podillian_granaries`, `chr_grain_corridors` |
| `frontier_fortress` | Кам'яна прикордонна фортеця на невисокій скелі | `PDL_fortify_podillia`, `uz_resist_habsburgs`, `uz_huszt_rename`, `uzh_congress_border_bastion` |
| `chumak_salt_caravan` | Воловий віз із сіллю | `uzh_salt_corridors`, `uzh_solotvynska_camera`, `VOL_conquer_moldavia`, `VOL_expand_Chumatsky_Way_mission` |
| `cossack_rada` | Козацька рада, булава та грамота | `het_zaporizhian_liberty`, `PDL_host_assembly` |

Разом нові ілюстрації використовують 18 місій у семи деревах. Для
`het_cossack_host`, яка вимагає кавалерійське військо, використано наявну
`mission_cossack_cavalry`. Умови, нагороди та розташування місій не змінено.

## Стиль і походження

Нові PNG створено через imagegen для цього моду: живописна історична мініатюра,
теплі охристі й коричневі кольори, приглушені зелений і синій, великі впізнавані
силуети, без написів та інтерфейсної рамки. Сюжети є художніми інтерпретаціями.
Фортеця не відтворює точний вигляд Паланка чи Кам'янця, а сцени не є доказом
історичності альтернативних держав і місій. Військова чайка також умовно
позначає контроль річкових шляхів у торгових місіях.

## Відтворення DDS

З кореня репозиторію, Python 3.10+ з Pillow та NumPy:

```text
python -B tools/build_core_ruthenia_icons.py --missions-only
python -B tools/build_core_ruthenia_icons.py --missions-only --check
python -B tests/check_mission_icons.py
python -B tests/check_file_encoding.py
python -B tests/check_clausewitz_braces.py
```

Маніфест джерел — `MISSION_ART` у генераторі. Він виконує центральне обрізання
без спотворення пропорцій і без чорних полів, зменшує зображення до 59×63 та
створює непрозорий нестиснений BGRA DDS без mipmaps (14 996 байтів).
Нові спрайти реєструються в `interface/rip_mission_icons.gfx`; дві старі
іконки залишаються в `interface/rip_ruthenian_legacy_missions.gfx`.

Режим `--missions-only` перебудовує лише іконки місій та їхню реєстрацію.
Перевірка порівнює всі канали DDS з майстрами, розмір і непрозорість,
єдиність реєстрації та фактичне використання у місіях.

Статичні перевірки й перегляд зменшених зображень виконані. Відображення
безпосередньо в EU4 не перевірене.
