# Матриця аудиту вилучення з RutheniaNew (для RIP)

> **Історичний запис. Джерела більше немає.** Теки `ruthenianew/` у
> репозиторії не існує, тож матрицю нижче не можна ані перевірити проти неї,
> ані повторити. Вона лишається з двох причин: фіксує правило `POD -> PDL`
> для будь-якої майбутньої міграції зі старих файлів, і пояснює, **чому карту
> не імпортували** - конвеєр 1.28 несумісний з поточним.
>
> Перевірено 2026-08-17: результат міграції на місці
> (`decisions/HetmanateLegacyErasDecisions.txt`, `events/HetmanateLegacyEras.txt`,
> `localisation/het_legacy_eras_l_english.yml`), а `history/wars/` справді вже
> вживає `PDL` і жодного `POD`. Один рядок матриці застарів - див. поправку.

## Обсяг і правила
- Джерело: `ruthenianew/`
- Режим: лише аудит, без прямого імпорту карти, торгових вузлів чи історичних блобів зі старих файлів.
- Ціль: корисні доповнення до чинного руського й гетьманського вмісту RIP з мінімальним ризиком конфлікту.

## Матриця класифікації

| Блок джерела | Категорія | Класифікація | Шлях у RIP | Стан | Примітки |
|---|---|---|---|---|---|
| `ruthenianew/common/countries/*.txt` | countries | obsolete/renamed | n/a (reference-only) | deferred | Legacy definitions overlap current country setup; no direct merge needed. |
| `ruthenianew/common/country_tags/00_countries.txt` | tags | obsolete/renamed | `common/country_tags/01_countries.txt` | deferred | Legacy uses `POD`; active war/history flows in RIP use `PDL` for Podillia timeline. |
| `ruthenianew/common/province_names/east_slavic.txt` | province_names | already integrated | `common/province_names/*` + localization layers | done | Most useful naming has already been incorporated earlier. |
| `ruthenianew/common/province_names/HET.txt` | province_names | safe candidate | ~~`common/province_names/HET.txt`~~ | **застаріло** | Файл згодом видалено з репозиторію - у `common/province_names/` лишилися `CHR`, `UZH`, `ZAZ` і `ruthenian`. Див. `PROVINCE_NAMES_NORMALIZATION_NOTES.md`. |
| `ruthenianew/common/province_names/ZAZ.txt` | province_names | safe candidate | `common/province_names/ZAZ.txt` | done | Safe-candidate verified via normalization pass; direct legacy import not performed due to naming-model conflict. |
| `ruthenianew/history/countries/HET - Hetmanate.txt` | history | already integrated | `history/countries/HET - Hetmanate.txt` | done | Chronology and flavor were already reused via current Hetmanate systems. |
| `ruthenianew/history/wars/*.txt` | wars | already integrated | `history/wars/*.txt` | done | Same war set exists in RIP; active files already use normalized tags (notably `PDL`). |
| `ruthenianew/history/provinces/*.txt` | history | incompatible (1.28 map pipeline) | n/a | deferred | Direct province-history import can desync with current map/province ownership balance. |
| `ruthenianew/history/provinces.rar` | history | incompatible (1.28 map pipeline) | n/a | deferred | Archived blob is not diff-friendly and unsuitable for direct integration workflow. |
| `ruthenianew/common/tradenodes/00_tradenodes.txt` | trade/map | incompatible (1.28 map pipeline) | n/a | deferred | Trade graph changes require coordinated map update and global balance pass. |
| `ruthenianew/map/*` | map | incompatible (1.28 map pipeline) | n/a | deferred | `default.map`, `definition.csv`, `area/region/continent`, and bitmaps require full map rebuild pipeline. |
| `ruthenianew/localisation/Ruthenia_mod_l_english.yml` | localisation | already integrated | `localisation/ruthenian_eastward_l_english.yml` and other RIP loc files | done | Core names/strings are already represented in current localization layers. |
| `ruthenianew/gfx/flags/*.tga` | assets | safe candidate | `gfx/flags/*.tga` | deferred | Optional visual backlog; can be imported per-tag if custom flag direction is approved. |

## Нормалізація старих тегів
- Обов'язкове відображення для будь-якого майбутнього вилучення: `POD -> PDL`.
- Наслідок: старі уривки воєн та історії, що й досі згадують `POD`, треба перемапити перед повторним ужитком.
- Підтвердження в RIP: `history/wars/*.txt` уже вживає `PDL` в активних скриптах воєн.

## Результат вилучення в цій ітерації
- Збережено позицію «лише аудит» щодо старих сирих даних.
- Розширено наявну архітектуру гетьманських ланцюгів подій замість додавання нового дерева місій:
  - `decisions/HetmanateLegacyErasDecisions.txt`
  - `events/HetmanateLegacyEras.txt`
  - `localisation/het_legacy_eras_l_english.yml`

## Кандидати в беклог
- Необов'язкове перенесення графіки прапорів із `ruthenianew/gfx/flags/*.tga` після узгодження арт-напрямку.
- Необов'язковий вибірковий прохід по різниці назв провінцій лише для `HET` і `ZAZ`.
