# Тегова система найменування файлів у `localisation/replace/`

Міграцію виконано з повною перевіркою еквівалентності даних через [localisation_replace_layout.py](../tools/localisation_replace_layout.py) та еталонний маніфест [localisation_replace_manifest.json](data/localisation_replace_manifest.json).

## 1. Правило іменування файлів

Усі файли в `localisation/replace/` залишаються в **плоскому** каталозі (без підтек, відповідно до вимог завантажувача EU4) і мають уніфікований формат назви:

```text
RIP_<OWNER>_<ENTITY>_l_<language>.yml
```

Де:
- `<language>` ∈ `{english, french, german, spanish}`;
- `<OWNER>` — власник контенту (за країною або спільним сутнісним сімейством):
  - **Країнні теги та пари тегів (`16`)**: `CHR`, `HET`, `HLC`, `KIE`, `KRU`, `LIT`, `MOS_RUS`, `NOV`, `ODS`, `PDL`, `PRL`, `QAS`, `UZH`, `VLN`, `VOL`, `ZAZ`;
  - **Спільні сімейства (`shared_*`, `12`)**: `shared_belarus`, `shared_church`, `shared_commonwealth`, `shared_cossack`, `shared_estates`, `shared_frontier`, `shared_government`, `shared_greek_catholic`, `shared_orthodox`, `shared_ruthenian` (сюди ж об'єднано `KUY` та перекриття назв ванільних наборів), `shared_steppe`, `shared_west_ruthenian`.
- `<ENTITY>` — функціональна сутність у нижньому регістрі:
  - `content` для консолідованих статичних/fallback-ключів кожного власника;
  - виділені сутності для генераторів (`government_authority`, `government_rada`, `government_parliament_names`, `government_status`, `church_nodes`, `church_redesign`, `border_watch`).

## 2. Гарантії збереження роботоздатності

1. **Контракти рушія EU4 1.37.5**:
   - Плоска структура `localisation/replace/*.yml`, суфікси `_l_<language>.yml`, перший рядок `l_<language>:`, кодування UTF-8 із **рівно одним BOM**.
   - У ванільній `EU4 1.37.5` директорія `localisation/replace/` порожня, усередині `RIP/localisation/replace/` існує `0` дублікатів ключів на кожну мову, а перетин із кореневою `localisation/*.yml` дорівнює `0`. Через це перехід зі старих префіксів `000_`, `zzz_`, `zzzz_` на єдиний `RIP_<OWNER>_<ENTITY>_l_<language>.yml` повністю інваріантний для завантаження гри та перекриття ванільних ключів.
2. **Розмежування генераторних та негенерованих файлів (`35` груп → `127` файлів)**:
   - Сім генераторів мають рівно по одній власній групі (загалом `27` генерованих файлів), що виключає мікрофрагментацію й не затирає статичні файли `content`:
     - [build_hetman_authority.py](../tools/build_hetman_authority.py) → `RIP_HET_government_authority` (`4` файли)
     - [build_kru_rada.py](../tools/build_kru_rada.py) → `RIP_KRU_government_rada` (`4` файли)
     - [build_parliament_names.py](../tools/build_parliament_names.py) → `RIP_shared_government_parliament_names` (`4` файли)
     - [build_church_support.py](../tools/build_church_support.py) → `RIP_shared_church_nodes` (`4` файли)
     - [build_border_mechanics_localisation.py](../tools/build_border_mechanics_localisation.py) → `RIP_shared_frontier_border_watch` (`3` файли)
     - [build_government_status_ui.py](../tools/build_government_status_ui.py) → `RIP_shared_government_status` (`4` файли)
     - [build_church_localisation.py](../tools/build_church_localisation.py) → `RIP_shared_church_redesign` (`4` файли)
   - Статичні та fallback-записи кожного власника консолідовано в один файл `RIP_<OWNER>_content_l_<language>.yml` (`28` груп, `100` файлів).
3. **100% збереження ключів і значень**:
   - З `70` попередніх файлів (`12 374` ключів у кожній із мов `french`/`german`/`spanish` і `3 637` в `english`) після оптимізації проміжної розбивки (`224` файли / `64` групи) залишено **`127` файлів** у `35` групах (`100` статичних + `27` генерованих) зі `100%` збігом контрольних сум мультимножин `(key, version, value)`.
   - Регресійний контракт закріплено в [check_localisation_replace_layout.py](../tests/check_localisation_replace_layout.py).
