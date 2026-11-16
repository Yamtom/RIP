# Аудит історії воєн (`history/wars`) і суміжних шарів карти та дипломатії

Перевірка виконана щодо **EU4 v1.37.5.0 Inca (491d)** без `replace_path` у `descriptor.mod` (працює пофайлове перекриття точних назв).

## 1. Розділення Трьох козацтв, позасценарні проміжки та статуси залежності

1. **Лівобережна Гетьманщина (`HET`)**: повернено реальні володіння у позасценарних проміжках `1648.6.1..1764.11.10` (`289 - Chernigov.txt`, `290 - Poltava.txt`, `1945 - Novgorod-Seversky.txt`, `2407 - Pereyaslav.txt`, `4542 - Lubnie.txt`, плюс `280 - Kiev.txt` у `1648..1667` і `1944 - Cherkasy.txt` у `1648..1667`), після чого тег `HET` скасовується до `RUS` `1764.11.10`.
2. **Правобережна Гетьманщина і Ханська Україна (`PDL`)**: тримає Правобережжя (`1942..1944`, `281`, `4247`, `4540` з `1667.1.30`, Чигирин до `1699.1.26`) та отримала османський протекторат (`TUR -> PDL`, `1669.3.1..1676.9.19` і `1677.6.29..1699.1.26`) у `ZaporizhiaHetmanate.txt`.
3. **Запорозька Січ, Олешки й Задунайська Січ (`ZAZ`)**: `283 - Zaporozhia.txt` збережено за `ZAZ` через `1648.6.1..1775.6.5` (Чортомлик, Кам'янська Січ `1709..1734` під `TUR`, Нова Січ `1734..1775` під `RUS`), оновлено перелік кошових отаманів у `ZAZ - Zaporozhie.txt` (`1657–1813`), а в `4706 - Tolcu.txt` додано **Задунайську Січ** (`1778.1.1..1821` під протекцією `TUR`).
4. **Протекторати, васали, колонії**: у `1.37.5` ванільний тип `protectorate` виведено з ужитку, тож історичні протекторати подано через `dependency = { subject_type = princedom }` (Гадяцька унія `1658.9.16..1659.10.27`), подвійні гарантії (`1667..1686`) та `vassal`. Заокеанських колоній (`colony`) козацтва не мали; слобідська й чорноморсько-кубанська колонізація відображена через культури й провінційну історію.

## 2. Деімперіалізація та виправлення Приазов'я, Дону, Криму й Кубані

- `286 - Azow.txt`: знято вигадане переведення у `russian`/`orthodox` під `1774.7.21`; корка `ZAZ` тримається до ліквідації Січі `1775.6.5`, а `trade_goods = fish` змінюється з `1783.4.8`.
- `2413 - Tyn.txt`: прибрано сфабриковану русифікацію Нижнього Дону `1593.1.1` (`culture = russian`) та згадку про битву при Молодях на Дону, лишивши `1761.9.23` (`Rostov`).
- `2410 - Theodoro.txt`: збережено `Mangup` і кримсько-готську культуру `goths` без фейкової русифікації `culture = russian` `1783.6.14` (перейменування на `Sevastopol` датоване `1784.2.21`).
- `2414 - Azaraba.txt`, `287 - Kouban.txt`, `2447 - Mantrega.txt`: анексію Кубані перенесено з помилкової `1774.7.21` на `1783.4.8`, вилучено анахронічний `1777 Yeysk` і фіктивний перехід у `culture = russian`, узгодивши колонізацію `1792–1793` Чорноморським козацьким військом (`culture = ruthenian`, `religion = orthodox`).

## 3. Узгоджені, виправлені й нові війни (`25` файлів)

- **Визвольні, козацькі та східноєвропейські кампанії**: `FirstMuscoviteLithuanianWar.txt` (`OKA` до `1494`), `SecondMuscoviteLithuanianWar.txt` (`CHR`), `ThirdMuscoviteLithuanianWar.txt` (`1507–1508`, Глинський і `CHR`, `Orsha`), `FourthMuscoviteLithuanianWar.txt` (`1534–1537`, Стародубська війна `KIE` Андрія Немировича), `PolishOttomanWar1620.txt` (`1620–1621`, Цецора й Хотин `ZAZ` Сагайдачного), `SmolenskWar.txt` (`ZAZ`), `KhmelnytskyUprising.txt` (`1648–1649`, Корсунь, Пилявці, Зборів), `PolishHetmanateWar.txt` (`1651–1654`, `HET` + `ZAZ` + `CRI`, `war_goal` `290`), `TheDeluge.txt` (Гадяч `HET`, Конотоп `1659.7.8`, Чуднів `1660.10.14`, виправлено `BOTH_SIDES`), `PolishCossackTatarWar.txt` (`PDL` + `CRI`, Підгайці `2961`), `OttomanCommonwealthWar.txt` (`war_goal` `2961`, Львів `2961`), `RussoTurkishWar.txt` (усі три козацтва `HET`, `ZAZ`, `PDL`, `war_goal` `280`, Чигирин `1944`), `WarOfTheHolyLeague.txt` (`PDL`, `HET`, `ZAZ`, `"Mustafa Koprulu"`), `GreatNordicWar.txt` (розведення `HET` Скоропадського `1709.7.9` і `ZAZ` Гордієнка до Прута `1711.7.21`, чистий ASCII `"Rehnskiold"` і `"Stromstierna"`), `SecondRussuTurkishWar.txt` (`HET` + `ZAZ`, `war_goal` `286`), `ThirdRussoTurkishWar.txt` (`ZAZ`), `FourthRussoTurkishWar.txt` та `FifthRussoTurkishWar.txt` (Задунайська Січ `ZAZ` під `TUR`).
- **Перекриті ванільні баґи європейських війн**: `CrusadeOfVarna.txt` (закрито `MOL`), `LivonianWar.txt` (`PRU` замість `TEU`, `KUR` з `1561.11.28`), `PolishMuscoviteWar.txt` (`PRU` замість `TEU`, `Stanislaw Zolkiewski` під Клушино), `SecondOttomanHungarianWar.txt.txt` (`war_goal` `153`), `WarOfThePolishSuccession.txt` (`SPI` замість `SAV`), `WarOfTheSixthCoalition.txt` (прибрано `HES`), `FrancoItalianWar.txt` (прибрано `SIL`).

## 4. Спадщина до-Leviathan (`1.29.6` / `1.30.3` → `1.37.5`)

- У Steam зараз встановлено `EU4 v1.29.6.0 Manchu`, а знімки `eu4_1.30.3` (до Leviathan `1.31`) і `eu4_1.37.5` лежать у `diagnostics/vanilla_donors/`.
- Усі 121 перевірені русинські/козацькі/східнослов'янські події `1.30.3` наявні у `1.37.5`; `Ruthenian_Missions.txt` (32 місії) уже відновлено в жовтні 2026 р., `kiev_pechersk_lavra` (монумент Leviathan `280 Київ`) перекрито у `zz_RIP_orthodox_monuments.txt`. Єдина війна ваніли, видалена після `1.30.3`, — `FrancoRussianWar.txt` (злита у `WarOfTheSixthCoalition.txt`).

## 5. Перевірка

- Генерація порівнянь: `python -B tools/audit_war_history.py --output docs/WAR_VANILLA_COMPARISON.md`
- Регресійні перевірки: `python -B tests/check_war_history.py` і [WAR_VANILLA_COMPARISON.md](WAR_VANILLA_COMPARISON.md)
