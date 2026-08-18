# Нотатки про нормалізацію назв провінцій (HET/ZAZ)

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
- Нормалізовані файли: `common/province_names/HET.txt`, `common/province_names/ZAZ.txt`.
- Метод: усунення дублікатів до правила «один ID = одна активна назва» за базою «виграє останній запис».
- Політика щодо старого: жодного прямого імпорту з `ruthenianew/common/province_names/*`.

## Статистика до і після
| Файл | Рядків до | Унікальних ID до | Дублікатів до | Рядків після | Унікальних ID після | Дублікатів після | Еквівалентно |
|---|---:|---:|---:|---:|---:|---:|---|
| `common/province_names/HET.txt` | 123 | 18 | 14 | 18 | 18 | 0 | True |
| `common/province_names/ZAZ.txt` | 80 | 37 | 18 | 37 | 37 | 0 | True |

## Три старі ключі, які не імпортували
- Не внесено до активних файлів:
  - `2406 = "Perevizka"`
  - `2411 = "Bakhmut"`
  - `2412 = "Domakha"`
- Причина: вони суперечать чинній моделі назв і змінили б те, що бачить гравець.

## Прибрані історичні синоніми
У кожному записі — збережене чинне значення й синоніми, прибрані з попередніх дублікатів.

### `common/province_names/HET.txt`
- `278` -> збережено: "Land of Learning"; прибрано: Pechersk; Collegium District
- `280` -> збережено: "Lavra Estates"; прибрано: Kyiv; Mother of Ruthenian Cities; Academy Quarter; Bohdan's Kyiv; Kyiv Ford; Kyiv-Pechersk Lavra; Mazepa's Kyiv; Kyiv Market; Kyiv Fortress; Imperial Kyiv; Treaty City; Little Russian Athens; Kyiv Siege; Contested Kyiv; Kochubey Holdings; Kyiv Negotiations; Winter Court; City of the Trident; Imperial Little Russia; Lost Autonomy; Kyiv Armenians
- `281` -> збережено: "Church Lands"; прибрано: Chernihiv; Chernihiv Regiment; Siversk Chernihiv; Chernihiv Collegium; Chernihiv Hundred; Chernihiv Breadbasket; Eletsky Monastery; Chernihiv Baroque; Chernihiv Commerce; Supervised Chernihiv; Scholarly Chernihiv; Governed Chernihiv
- `282` -> збережено: "Trinity Holdings"; прибрано: Nizhyn Regiment; Nizhyn College; Nizhyn Hundred; Nizhyn Cossacks; Holy Trinity; Nizhyn Fair; Nizhyn Registry; Hundred Court; Nizhyn Greeks
- `294` -> збережено: "Bila Tserkva Treaty"; прибрано: Bila Tserkva; Polish Border
- `295` -> збережено: "Pereiaslav Articles"; прибрано: Pereiaslav; Pereiaslav Regiment; Pereiaslav Settlement; Vyhovsky's Pereiaslav; Pereiaslav Crossing; Pereiaslav Compact; Berestechko Memory; Treaty Border
- `296` -> збережено: "Foreign Quarter"; прибрано: Poltava Regiment; Poltava Estates; Poltava Colony; Poltava Hundred; Poltava Granary; Poltava Host; Poltava Cathedral; Poltava Trade; Poltava Defenses; Poltava Field; Poltava Registers; Polubotok Lands; Harvest Capital; Regimental Court
- `297` -> збережено: "Spring Muster"; прибрано: Myrhorod Regiment; Myrhorod Ranches; Myrhorod Township; Myrhorod Hundred; Myrhorod Fields; Myrhorod Roster
- `298` -> збережено: "Lubny Harvest"; прибрано: Lubny Regiment; Lubny Holdings
- `463` -> збережено: "Tsar's Fortress"; прибрано: Putyvl
- `1946` -> збережено: "Destroyed Capital"; прибрано: Baturyn; Starodub Regiment; Baturyn Court; Mazepa's Baturyn; Starodub Cossacks; Baturyn Palace; Baturyn Arsenal; Mazepa's Diplomacy; Iskra Estates; Hetman's Justice; Mace Capital
- `1952` -> збережено: "Imperial Frontier"; прибрано: Novhorod-Siverskyi
- `2404` -> збережено: "Former Glory"; прибрано: Hlukhiv; Hlukhiv Regiment; Hlukhiv Manors; Skoropadsky's Hlukhiv; Apostol's Capital; Rozumovsky's Court; Hlukhiv Residency; Hlukhiv Garrison; Collegium Capital; Muscovite Border; Rozumovsky Domains; Seal City; Last Hetman's Seat
- `2750` -> збережено: "Konotop Victory"; прибрано: Hadiach Regiment; Konotop

### `common/province_names/ZAZ.txt`
- `238` -> збережено: "Kodak Siege"; прибрано: Kodak; Gates of the Sich; Kodak Redoubt
- `283` -> збережено: "Kalnishevsky's Sich"; прибрано: Zaporizhia; Sich of 38 Kurens; Velykyi Luh; Sich Pokrova; Land of the Free; Sich Shipyards
- `284` -> збережено: "Turkish Ochakiv"; прибрано: Ochakiv
- `286` -> збережено: "Samara Fair"; прибрано: Samara
- `287` -> збережено: "Nikopol Docks"; прибрано: Nikopol; Sukhyi Kaharlyk; Nikopol Market; Dnieper Fisheries
- `288` -> збережено: "Dnieper Trade"; прибрано: Dnipro
- `466` -> збережено: "Bakhmut Salt"; прибрано: Bakhmut
- `1943` -> збережено: "Kamyanska Sich"; прибрано: Kamyanka
- `1951` -> збережено: "Winter Stations"; прибрано: Kalmius; Kalmius Palanka; Kalmius Horses
- `2406` -> збережено: "Northern Redoubts"; прибрано: Mala Sich; Mykytyn Rih; Cossack Paradise
- `2407` -> збережено: "Ottoman Border"; прибрано: Beryslav
- `2410` -> збережено: "Sich Destruction Site"; прибрано: Nova Sich; Chaplynka; Pidpilnenska Sich; Oleshkivska Sich; Last Sich
- `2411` -> збережено: "Mazepa's Choice"; прибрано: Chortomlyk; Chortomlytska Sich; Chortomlyk Waters; Chortomlyk Cathedral; Sich Fortifications; Chortomlyk Yards
- `2412` -> збережено: "Bazavluk Waters"; прибрано: Bazavluk
- `2413` -> збережено: "Kinburn Fisheries"; прибрано: Kinburn
- `2446` -> збережено: "Summer Pastures"; прибрано: Melitopol; Melitopol Steppes
- `2447` -> збережено: "Autumn Gathering"; прибрано: Tokmak; Tokmak Herds
- `2448` -> збережено: "Luhansk Palanka"; прибрано: Luhansk

## Прохід 2026 року: суміжне порубіжжя для `common/province_names/ZAZ.txt`
- Цей прохід не повертає старої описової моделі для ZAZ.
- Спосіб: підставні назви за змістом мода для суміжних порубіжних земель, які вже випливають із запорозької географії мода.
- Повернуто й додано лише строгі топоніми; назв із заголовків подій і описових назв не вертали.
- Обережне ядро лишилося без змін:
  - `282 = "Ochakiv"`
  - `283 = "Sich"`
  - `286 = "Azov"`
  - `2406 = "Inhul"`
  - `2409 = "Bakhmut"`
- Перелік дублікатів вище — це запис старого нормалізаційного проходу; чинного стану `ZAZ.txt` він більше не описує.

### Додані суміжні та підставні топоніми
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

### Пропущено в цьому проході
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
- Причина: для поточного стану мода немає досить стійкого, строго топологічного й внутрішньо несуперечливого відображення.

## Перелік перевірки
- Дублікатів ID після нормалізації: `0` в обох файлах.
- Базова чинна мапа проти нормалізованої: повний збіг в обох файлах.
- Старі значення `ruthenianew` вжито лише як довідку; прямого злиття не було.
