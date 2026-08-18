# Province Names Normalization Notes (HET/ZAZ)

---

## Стан на 16 серпня 2026 — цей документ описує минулий стан

Нижче наведено запис попереднього нормалізаційного проходу. Він більше не
описує репозиторій, і читати його як опис поточного стану не можна.

**`common/province_names/HET.txt` більше не існує.** У теці лишилися
`CHR.txt`, `UZH.txt`, `ZAZ.txt` і `ruthenian.txt`.

**`ZAZ.txt` переписано** й перегруповано за областями ванілі з коментарями
`# Ruthenia: chernigov_area` тощо. Ані «Kalnishevsky's Sich», ані інші
описові назви з таблиць нижче в ньому не лишилось.

### Чому таблиці нижче не варто відновлювати

Обидва проходи, описані в цьому файлі, спиралися на припущення, що
послідовні ID лежать поруч. У EU4 це не так, і більшість рядків указувала на
чужі провінції:

| Запис у документі | Насправді ця провінція |
|---|---|
| `281` -> «Chernihiv» | Кам'янець-Подільський |
| `282` -> «Nizhyn» | Єдисан |
| `284` -> «Turkish Ochakiv» | Крим (Qirim) |
| `286` -> «Samara Fair» | Азов |
| `287` -> «Nikopol Docks» | Кубань |
| `288` -> «Dnieper Trade» | Нижній Дон |
| `294` -> «Bila Tserkva Treaty» | Твер |
| `295` -> «Pereiaslav Articles» | Москва |
| `296` -> «Foreign Quarter» (Полтава) | Калуга |
| `297` -> «Spring Muster» (Миргород) | Брянськ |
| `298` -> «Lubny Harvest» | Курськ |
| `463` -> «Tsar's Fortress» / «Belgorod» | Черкесія |
| `466` -> «Bakhmut Salt» | Сарай |
| `1943` -> «Kamyanska Sich» | Брацлав |
| `1952` -> «Imperial Frontier» | Мараморош |
| `2404` -> «Former Glory» (Глухів) | Мергуї, Бірма |
| `2407` -> «Ottoman Border» (Берислав) | Переяслав |
| `2413` -> «Kinburn Fisheries» | Тин |
| `2448` -> «Luhansk Palanka» | Феццан, Лівія |
| `2750` -> «Konotop Victory» | Пловдив |

Той самий шаблон уразив `CHR.txt` і `UZH.txt`; обидва вичищено окремо — див.
`docs/MAP_REWORK_SUGGESTIONS.md`.

`tests/check_script_layer.py` тепер звіряє кожне перейменування з
`definition.csv`, `area.txt` і `region.txt` ванілі, тож повторити цю помилку
мовчки вже не вийде. Перед будь-яким новим проходом над `province_names`
запускайте його.

### Що з цього збережено

Один рядок консервативного блоку відновлено в поточному `ZAZ.txt` —
`282 = "Ochakiv"` — бо Очаків справді лежить у `yedisan_area` і був
найближчою османською фортецею до Січі. Правопис приведено до глосарію
(`Ochakiv`, не `Ochakov`).

---

## Обсяг
- Files normalized: `common/province_names/HET.txt`, `common/province_names/ZAZ.txt`.
- Method: dedup to `1 province ID = 1 active name` using **last-entry-wins** baseline.
- Legacy policy: no direct import from `ruthenianew/common/province_names/*`.

## Before/After Statistics
| File | Rows Before | Unique IDs Before | Duplicate IDs Before | Rows After | Unique IDs After | Duplicate IDs After | Effective Equivalent |
|---|---:|---:|---:|---:|---:|---:|---|
| `common/province_names/HET.txt` | 123 | 18 | 14 | 18 | 18 | 0 | True |
| `common/province_names/ZAZ.txt` | 80 | 37 | 18 | 37 | 37 | 0 | True |

## Legacy 3 Keys Non-Import
- Not imported into active files:
  - `2406 = "Perevizka"`
  - `2411 = "Bakhmut"`
  - `2412 = "Domakha"`
- Reason: they conflict with current effective naming model and would change active in-game outputs.

## Removed Historical Aliases (Dedup)
Each entry shows the kept effective value and the aliases removed from earlier duplicate rows.

### `common/province_names/HET.txt`
- `278` -> kept: "Land of Learning"; removed: Pechersk; Collegium District
- `280` -> kept: "Lavra Estates"; removed: Kyiv; Mother of Ruthenian Cities; Academy Quarter; Bohdan's Kyiv; Kyiv Ford; Kyiv-Pechersk Lavra; Mazepa's Kyiv; Kyiv Market; Kyiv Fortress; Imperial Kyiv; Treaty City; Little Russian Athens; Kyiv Siege; Contested Kyiv; Kochubey Holdings; Kyiv Negotiations; Winter Court; City of the Trident; Imperial Little Russia; Lost Autonomy; Kyiv Armenians
- `281` -> kept: "Church Lands"; removed: Chernihiv; Chernihiv Regiment; Siversk Chernihiv; Chernihiv Collegium; Chernihiv Hundred; Chernihiv Breadbasket; Eletsky Monastery; Chernihiv Baroque; Chernihiv Commerce; Supervised Chernihiv; Scholarly Chernihiv; Governed Chernihiv
- `282` -> kept: "Trinity Holdings"; removed: Nizhyn Regiment; Nizhyn College; Nizhyn Hundred; Nizhyn Cossacks; Holy Trinity; Nizhyn Fair; Nizhyn Registry; Hundred Court; Nizhyn Greeks
- `294` -> kept: "Bila Tserkva Treaty"; removed: Bila Tserkva; Polish Border
- `295` -> kept: "Pereiaslav Articles"; removed: Pereiaslav; Pereiaslav Regiment; Pereiaslav Settlement; Vyhovsky's Pereiaslav; Pereiaslav Crossing; Pereiaslav Compact; Berestechko Memory; Treaty Border
- `296` -> kept: "Foreign Quarter"; removed: Poltava Regiment; Poltava Estates; Poltava Colony; Poltava Hundred; Poltava Granary; Poltava Host; Poltava Cathedral; Poltava Trade; Poltava Defenses; Poltava Field; Poltava Registers; Polubotok Lands; Harvest Capital; Regimental Court
- `297` -> kept: "Spring Muster"; removed: Myrhorod Regiment; Myrhorod Ranches; Myrhorod Township; Myrhorod Hundred; Myrhorod Fields; Myrhorod Roster
- `298` -> kept: "Lubny Harvest"; removed: Lubny Regiment; Lubny Holdings
- `463` -> kept: "Tsar's Fortress"; removed: Putyvl
- `1946` -> kept: "Destroyed Capital"; removed: Baturyn; Starodub Regiment; Baturyn Court; Mazepa's Baturyn; Starodub Cossacks; Baturyn Palace; Baturyn Arsenal; Mazepa's Diplomacy; Iskra Estates; Hetman's Justice; Mace Capital
- `1952` -> kept: "Imperial Frontier"; removed: Novhorod-Siverskyi
- `2404` -> kept: "Former Glory"; removed: Hlukhiv; Hlukhiv Regiment; Hlukhiv Manors; Skoropadsky's Hlukhiv; Apostol's Capital; Rozumovsky's Court; Hlukhiv Residency; Hlukhiv Garrison; Collegium Capital; Muscovite Border; Rozumovsky Domains; Seal City; Last Hetman's Seat
- `2750` -> kept: "Konotop Victory"; removed: Hadiach Regiment; Konotop

### `common/province_names/ZAZ.txt`
- `238` -> kept: "Kodak Siege"; removed: Kodak; Gates of the Sich; Kodak Redoubt
- `283` -> kept: "Kalnishevsky's Sich"; removed: Zaporizhia; Sich of 38 Kurens; Velykyi Luh; Sich Pokrova; Land of the Free; Sich Shipyards
- `284` -> kept: "Turkish Ochakiv"; removed: Ochakiv
- `286` -> kept: "Samara Fair"; removed: Samara
- `287` -> kept: "Nikopol Docks"; removed: Nikopol; Sukhyi Kaharlyk; Nikopol Market; Dnieper Fisheries
- `288` -> kept: "Dnieper Trade"; removed: Dnipro
- `466` -> kept: "Bakhmut Salt"; removed: Bakhmut
- `1943` -> kept: "Kamyanska Sich"; removed: Kamyanka
- `1951` -> kept: "Winter Stations"; removed: Kalmius; Kalmius Palanka; Kalmius Horses
- `2406` -> kept: "Northern Redoubts"; removed: Mala Sich; Mykytyn Rih; Cossack Paradise
- `2407` -> kept: "Ottoman Border"; removed: Beryslav
- `2410` -> kept: "Sich Destruction Site"; removed: Nova Sich; Chaplynka; Pidpilnenska Sich; Oleshkivska Sich; Last Sich
- `2411` -> kept: "Mazepa's Choice"; removed: Chortomlyk; Chortomlytska Sich; Chortomlyk Waters; Chortomlyk Cathedral; Sich Fortifications; Chortomlyk Yards
- `2412` -> kept: "Bazavluk Waters"; removed: Bazavluk
- `2413` -> kept: "Kinburn Fisheries"; removed: Kinburn
- `2446` -> kept: "Summer Pastures"; removed: Melitopol; Melitopol Steppes
- `2447` -> kept: "Autumn Gathering"; removed: Tokmak; Tokmak Herds
- `2448` -> kept: "Luhansk Palanka"; removed: Luhansk

## 2026 Adjacent Frontier Expansion for `common/province_names/ZAZ.txt`
- This pass does not restore the old flavor model for ZAZ.
- Method used: `mod-semantic stand-in` for adjacent frontier territories already implied by the mod's broader Zaporozhian geography.
- Only strict toponyms were restored or added in this pass; no event-title or descriptive flavor names were reintroduced.
- The conservative core block was preserved without revision:
  - `282 = "Ochakiv"`
  - `283 = "Sich"`
  - `286 = "Azov"`
  - `2406 = "Inhul"`
  - `2409 = "Bakhmut"`
- The earlier dedup list above remains a record of the old normalization pass and no longer reflects the current active effective map for `ZAZ.txt`.

### Added Adjacent / Stand-In Toponyms
- `238 = "Kodak"`
- `287 = "Kuban"`
- `291 = "Kharkiv"`
- `463 = "Belgorod"`
- `1943 = "Kamyanka"`
- `1951 = "Kalmius"`
- `2407 = "Beryslav"`
- `2410 = "Nova Sich"`
- `2411 = "Chortomlyk"`
- `2412 = "Bazavluk"`
- `2413 = "Kinburn"`
- `2446 = "Melitopol"`
- `2447 = "Tokmak"`
- `2448 = "Luhansk"`

### Omitted In This Pass
- `2405`
- `2414`
- `1974`
- `466`
- `301`
- `2854`
- `1946`
- `1961`
- `2415`
- `2416`
- `2417`
- Reason: no sufficiently stable, strictly topological, and internally consistent stand-in mapping for the current mod state.

## Verification Checklist
- Duplicate IDs after normalization: `0` for both files.
- Baseline effective map vs normalized map: exact match for both files.
- `ruthenianew` legacy values used only as reference; no direct merge performed.
