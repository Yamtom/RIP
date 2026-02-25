# Province Names Normalization Notes (HET/ZAZ)

## Scope
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

## Verification Checklist
- Duplicate IDs after normalization: `0` for both files.
- Baseline effective map vs normalized map: exact match for both files.
- `ruthenianew` legacy values used only as reference; no direct merge performed.
