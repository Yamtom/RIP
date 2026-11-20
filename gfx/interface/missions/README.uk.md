# Іконки місій RIP

Тека містить 14 власних іконок з PNG-майстрів у `source/` і одну іконку, складену
з ванільних (див. нижче). Шість нових
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

## Перепризначення та складена іконка (листопад 2026)

Аудит іконок 539 місій показав, що більшість місій мода слушно вживає загальні
ванільні іконки, але чотири групи мали чужу чи випадкову картинку: «релігійна
рівновага» — університет або молитовні руки, православні місії — «молитовні руки»,
колонізація Банату — Карибська карта, «Західний Дніпро» — рисове поле. **40 місій**
отримали іншу іконку; умови, нагороди й розташування не змінено.

| Тема | Місії | Іконка |
| --- | --- | --- |
| Дві віри в рівновазі | `PDL_religious_tolerance`, `PDL_confessional_equilibrium`, `VLN_confessional_balance`, `VOL_religious_settlement`, `uz_union_dilemma`, `uz_union_compromise_plus` | `rip_gfx_mission_confessional_balance_icon` (нова, складена) |
| Магдебурзьке право | `KIE_magdeburg_law` | `mission_ukr_magdeburg_laws` |
| Київська академія та братські школи | `KIE_brotherhood_schools`, `prl_brotherhood_schools`, `chr_left_bank_collegium_mission` | `petro_mohyla` |
| Православна ієрархія | `prl_episcopal_authority`, `uzh_srem_metropolis` | `mission_most_holy_synod` |
| | `prl_orthodox_leadership` | `mission_develop_kiev` |
| | `VOL_church_relations` | `promote_the_patriarchate` |
| | `ZAZ_orthodox_protectors`, `het_orthodox_defender` | `mission_autocephalous_archbishopric` |
| Карпатський обряд | `uz_preserve_orthodox_faith`, `uz_orthodox_unity` | `mission_catholic_heddal_church` |
| Переселення | `uzh_banat_colonization`, `uzh_backa_settlements` | `mission_serfdom` |
| | `uz_great_migration` | `mission_cope_with_refugees` |
| Зерно, сіль, торгівля | `pol_secure_grain_trade`, `uzh_agriculture`, `chr_agro_hypercorporation` | `rip_gfx_mission_ruthenian_granaries_icon` |
| | `uzh_tisza_customs_convention`, `KIE_dniestr_trade_route` | `rip_gfx_mission_chumak_salt_caravan_icon` |
| Чайки | `UKR_fleet` | `rip_gfx_mission_dnieper_chaika_icon` |
| Фортеці та рубежі | `PDL_khotyn_siege`, `VOL_full_army`, `het_bulwark_christendom`, `uz_mukachevo_autonomy`, `chr_Smolensk`, `VOL_conquer_smolensk` | `rip_gfx_mission_frontier_fortress_icon` |
| Рада | `ZAZ_POL_politics` | `rip_gfx_mission_cossack_rada_icon` |
| Інше | `KIE_friend_or_foe` | `mission_friends_or_enemies` |
| | `ZAZ_GOL_west_dniepr` | `mission_advance_to_the_dnieper` |
| | `UKR_baltic` | `mission_conquer_riga` |
| | `ZAZ_RUS_end_crimea` | `mission_break_the_tatar_yoke` |
| | `VOL_renaissance_court` | `law_of_the_pious` |
| | `ZAZ_UKR_podolia_volhynia` | `mission_unite_home_region` |

Мальовані спрайти цієї теки тепер обслуговують більше місій, ніж було намальовано:
`petro_mohyla` і `mission_ukr_magdeburg_laws` через закоментований
`Ruthenian_Missions.txt` не використовував жодну активну місію, і перевірка
`tools/build_core_ruthenia_icons.py --missions-only --check` через це падала.

Ванільні спрайти місій мають різні імена: частина з префіксом `mission_`
(`mission_most_holy_synod`), частина без нього (`promote_the_patriarchate`,
`law_of_the_pious`), тож перед підстановкою назву треба звіряти з
`interface/*.gfx` встановленої гри; цю звірку робить `tests/check_mission_icons.py`.

**Складена іконка.** `rip_gfx_mission_confessional_balance_icon` — православний собор
із золотою банею (`mission_cathedral_cities`) ліворуч, готична церква
(`mission_european_church`) праворуч і золотий шов між ними. Її будує
`tools/build_mission_composites.py` (`--check`, `--preview`) з ванільних донорів у
рідному розмірі, без масштабування й тонування; DDS лежить поруч з іншими, а
реєстрація — в окремому `interface/RIP_shared_mission_icons_composed.gfx`, щоб не міняти
текст `RIP_shared_mission_icons.gfx`, який порівнює генератор мальованих іконок.
Це найближча готова картина, а не мальований майстер; промпт для живописного
варіанта: дві віри, що стоять поруч, — православна церква з банями й готична
церква зі шпилем, золотий розділ між ними, живописна історична мініатюра, без
написів.

