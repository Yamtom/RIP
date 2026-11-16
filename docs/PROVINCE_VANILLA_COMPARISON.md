# Province history comparison

Installed baseline: **EU4 v1.37.5.0 Inca (491d)**

Path: `D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV`

Reviewed `65` RIP province history files: {'override': 62, 'identical': 3}.
Total 1444.11.11 development across reviewed provinces: vanilla **428** -> RIP **592** (**+164**).
1444.11.11 ownership breakdown: {'LIT': 21, 'CHR': 9, 'KIE': 7, 'POL': 5, 'HLC': 5, 'VLN': 5, 'RYA': 4, 'ZAZ': 3, 'HUN': 1, 'MOS': 1, 'GOL': 1, 'MAZ': 1, 'UZH': 1, 'OKA': 1}.

Only RIP overrides in `history/provinces/` are compared; unoverridden vanilla provinces inherit vanilla history verbatim.
Identical fixture provinces (`300`, `301`, `4255`) are intentionally retained for `tests/check_culture_key_compatibility.py`.

| ID | File | Comparison | 1444 Owner (V->RIP) | 1444 Culture (V->RIP) | 1444 Religion | 1444 Dev (V->RIP) | Trade Good | CoT | 1444 Cores | Dated Blocks |
|---|---|---|---|---|---|---|---|---|---|---|
| 153 | 153 - Pest.txt | override | HUN -> HUN | hungarian -> hungarian | catholic | 11 -> 12 (+1) | grain | 2 | HUN | 14 |
| 259 | 259 - Sandomierz.txt | override | POL -> POL | polish -> polish | catholic | 9 -> 12 (+3) | cloth | — | POL | 14 |
| 260 | 260 - Lublin.txt | override | POL -> POL | polish -> polish | catholic | 13 -> 16 (+3) | cloth | 2 | POL,VLN | 18 |
| 261 | 261 - Halicz.txt | override | POL -> HLC | ruthenian -> ruthenian | orthodox | 8 -> 12 (+4) | grain | — | HLC,POL | 15 |
| 269 | 269 - Podlasia.txt | override | LIT -> LIT | polish -> ruthenian | catholic | 13 -> 19 (+6) | livestock | — | LIT,VLN | 12 |
| 270 | 270 - Troki.txt | override | LIT -> LIT | lithuanian -> lithuanian | catholic | 8 -> 11 (+3) | livestock | — | LIT | 4 |
| 271 | 271 - Samogitia.txt | override | LIT -> LIT | lithuanian -> lithuanian | catholic | 6 -> 9 (+3) | livestock | — | LIT | 9 |
| 272 | 272 - Lithuania.txt | override | LIT -> LIT | lithuanian -> lithuanian | catholic | 13 -> 16 (+3) | grain | 1 | LIT | 9 |
| 276 | 276 - Minsk.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 7 -> 10 (+3) | naval_supplies | — | LIT,MSK | 8 |
| 277 | 277 - Brest.txt | override | LIT -> VLN | byelorussian -> ruthenian | orthodox | 6 -> 6 (+0) | wool | — | LIT,VLN | 9 |
| 278 | 278 - Pinsk.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 6 -> 9 (+3) | wool | — | LIT | 8 |
| 279 | 279 - Volhynia.txt | override | LIT -> VLN | ruthenian -> ruthenian | orthodox | 10 -> 16 (+6) | livestock | — | VLN | 14 |
| 280 | 280 - Kiev.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 10 -> 16 (+6) | grain | 2 | KIE | 23 |
| 281 | 281 - Kamienec.txt | override | POL -> HLC | ruthenian -> ruthenian | orthodox | 6 -> 8 (+2) | livestock | — | HLC,PDL | 12 |
| 282 | 282 - Yedisan.txt | override | LIT -> ZAZ | ruthenian -> ruthenian | orthodox | 5 -> 8 (+3) | livestock | — | ZAZ | 10 |
| 283 | 283 - Zaporozhia.txt | override | LIT -> ZAZ | ruthenian -> ruthenian | orthodox | 4 -> 7 (+3) | livestock | — | ZAZ | 36 |
| 289 | 289 - Chernigov.txt | override | LIT -> CHR | ryazanian -> ruthenian | orthodox | 5 -> 5 (+0) | iron | — | CHR,KHK | 12 |
| 290 | 290 - Poltava.txt | override | LIT -> CHR | ruthenian -> ruthenian | orthodox | 5 -> 8 (+3) | grain | — | CHR,PRL | 5 |
| 291 | 291 - Kharkov.txt | override | LIT -> CHR | ruthenian -> ruthenian | orthodox | 5 -> 5 (+0) | iron | — | CHR,KHK | 4 |
| 292 | 292 - Mogilyov.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 5 -> 8 (+3) | wool | — | LIT,PLT | 8 |
| 293 | 293 - Smolensk.txt | override | LIT -> LIT | ryazanian -> byelorussian | orthodox | 9 -> 12 (+3) | grain | 2 | LIT,SMO | 17 |
| 295 | 295 - Moskva.txt | override | MOS -> MOS | russian -> russian | orthodox | 17 -> 14 (-3) | iron | 2->1 | MOS | 15 |
| 297 | 297 - Bryansk.txt | override | LIT -> LIT | ryazanian -> ruthenian | orthodox | 5 -> 8 (+3) | grain | — | LIT,SMO | 9 |
| 298 | 298 - Kursk.txt | override | LIT -> CHR | ryazanian -> ruthenian | orthodox | 4 -> 4 (+0) | grain | — | CHR,KHK,OKH | 7 |
| 299 | 299 - Voronezh.txt | override | GOL -> GOL | mishary -> mishary | sunni | 8 -> 8 (+0) | livestock | — | GOL,KHK,SMY | 3 |
| 300 | 300 - Tula.txt | identical | RYA -> RYA | ryazanian -> ryazanian | orthodox | 8 -> 8 (+0) | iron | — | RYA | 8 |
| 301 | 301 - Ryazan.txt | identical | RYA -> RYA | ryazanian -> ryazanian | orthodox | 13 -> 13 (+0) | wool | — | RYA | 9 |
| 771 | 771 - Vitebsk.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 5 -> 8 (+3) | grain | — | LIT,PLT,VTB | 10 |
| 1936 | 1936 - Kovno.txt | override | LIT -> LIT | lithuanian -> lithuanian | catholic | 7 -> 10 (+3) | livestock | — | LIT | 11 |
| 1937 | 1937 - Grodno.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 5 -> 11 (+6) | livestock | — | LIT,VLN | 6 |
| 1940 | 1940 - Belz.txt | override | MAZ -> MAZ | ruthenian -> ruthenian | orthodox | 9 -> 13 (+4) | livestock | — | HLC,MAZ,VOL | 11 |
| 1941 | 1941 - Turov.txt | override | LIT -> KIE | byelorussian -> ruthenian | orthodox | 3 -> 3 (+0) | wool | — | KIE,TRV | 9 |
| 1942 | 1942 - Zhytomyr.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 4 -> 7 (+3) | grain | — | KIE | 10 |
| 1943 | 1943 - Bratslav.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 7 -> 13 (+6) | livestock | — | KIE,PDL | 12 |
| 1944 | 1944 - Cherkasy.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 3 -> 6 (+3) | livestock | — | KIE | 11 |
| 1945 | 1945 - Novgorod-Seversky.txt | override | LIT -> CHR | ryazanian -> ruthenian | orthodox | 4 -> 7 (+3) | iron | —->1 | CHR,KHK | 21 |
| 1952 | 1952 - Maramaros.txt | override | HUN -> UZH | ruthenian -> rusyn | orthodox | 5 -> 11 (+6) | salt | —->1 | HUN,UZH | 7 |
| 2406 | 2406 - Ingil.txt | override | LIT -> ZAZ | ruthenian -> ruthenian | orthodox | 3 -> 6 (+3) | wine | — | ZAZ | 3 |
| 2407 | 2407 - Pereyaslav.txt | override | LIT -> CHR | ruthenian -> ruthenian | orthodox | 5 -> 8 (+3) | grain | — | CHR,PRL | 6 |
| 2408 | 2408 - Lipetsk.txt | override | RYA -> RYA | mishary -> mishary | sunni | 7 -> 7 (+0) | livestock | — | IZM,KHK,RYA | 4 |
| 2424 | 2424 - Peremyshl.txt | override | POL -> HLC | ruthenian -> ruthenian | orthodox | 7 -> 12 (+5) | livestock | — | HLC,POL | 15 |
| 2959 | 2959 - Tarnow.txt | override | POL -> POL | polish -> polish | catholic | 8 -> 8 (+0) | grain | — | HLC,POL | 13 |
| 2960 | 2960 - Sadecki.txt | override | POL -> POL | polish -> polish | catholic | 14 -> 20 (+6) | iron | — | HLC,POL | 9 |
| 2961 | 2961 - Lwow.txt | override | POL -> HLC | ruthenian -> ruthenian | orthodox | 12 -> 13 (+1) | dyes | 1 | HLC,POL | 14 |
| 2962 | 2962 - Rowne.txt | override | LIT -> VLN | ruthenian -> ruthenian | orthodox | 3 -> 6 (+3) | livestock | — | VLN | 14 |
| 4115 | 4115 - Mazyr.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 6 -> 9 (+3) | grain | — | LIT,TRV | 8 |
| 4116 | 4116 - Upper Oka.txt | override | OKA -> OKA | ryazanian -> ruthenian | orthodox | 9 -> 9 (+0) | grain | — | OKA | 6 |
| 4242 | 4242 - Ula.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 5 -> 8 (+3) | iron | — | LIT,PLT,VTB | 6 |
| 4243 | 4243 - Toropets.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 5 -> 8 (+3) | grain | — | LIT,PLT | 11 |
| 4244 | 4244 - Starodub.txt | override | LIT -> CHR | ryazanian -> ruthenian | orthodox | 5 -> 7 (+2) | grain | —->1 | CHR,SMO | 16 |
| 4245 | 4245 - Vyazma.txt | override | LIT -> LIT | ryazanian -> byelorussian | orthodox | 5 -> 8 (+3) | cloth | — | LIT,SMO | 17 |
| 4246 | 4246 - Mstislav.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 3 -> 6 (+3) | wool | — | LIT,MSL,PLT | 8 |
| 4247 | 4247 - Owrucz.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 4 -> 7 (+3) | grain | — | KIE | 10 |
| 4255 | 4255 - Pronsk.txt | identical | RYA -> RYA | ryazanian -> ryazanian | orthodox | 6 -> 6 (+0) | iron | — | RYA | 8 |
| 4527 | 4527 - Checiny.txt | override | POL -> POL | polish -> polish | catholic | 7 -> 10 (+3) | cloth | — | POL | 14 |
| 4536 | 4536 - Lida.txt | override | LIT -> LIT | lithuanian -> lithuanian | catholic | 6 -> 9 (+3) | livestock | — | LIT | 4 |
| 4537 | 4537 - Nowogrodek.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 4 -> 7 (+3) | wool | — | LIT | 8 |
| 4538 | 4538 - Chelm.txt | override | POL -> VLN | ruthenian -> ruthenian | orthodox | 5 -> 5 (+0) | wool | — | POL,VLN | 9 |
| 4539 | 4539 - Kremenets.txt | override | LIT -> VLN | ruthenian -> ruthenian | orthodox | 3 -> 6 (+3) | livestock | — | VLN | 14 |
| 4540 | 4540 - Winnica.txt | override | LIT -> KIE | ruthenian -> ruthenian | orthodox | 3 -> 6 (+3) | livestock | — | KIE,PDL | 11 |
| 4541 | 4541 - Drohobycz.txt | override | POL -> HLC | ruthenian -> ruthenian | orthodox | 5 -> 6 (+1) | livestock | — | HLC,POL | 14 |
| 4542 | 4542 - Lubnie.txt | override | LIT -> CHR | ruthenian -> ruthenian | orthodox | 5 -> 8 (+3) | grain | — | CHR,PRL | 5 |
| 4543 | 4543 - Rylsk.txt | override | LIT -> CHR | ryazanian -> ruthenian | orthodox | 3 -> 3 (+0) | grain | — | CHR,KHK | 7 |
| 4544 | 4544 - Bobrujsk.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 3 -> 6 (+3) | grain | — | LIT | 8 |
| 4545 | 4545 - Sluck.txt | override | LIT -> LIT | byelorussian -> byelorussian | orthodox | 6 -> 9 (+3) | cloth | — | LIT,MSK | 8 |

## Development delta summary (51 provinces changed; net +164)

| ID | Province | Vanilla Tax/Prod/Man (Total) | RIP Tax/Prod/Man (Total) | Delta |
|---|---|---|---|---|
| 153 | Pest | 5/4/2 (11) | 6/4/2 (12) | +1 |
| 259 | Sandomierz | 4/4/1 (9) | 5/5/2 (12) | +3 |
| 260 | Lublin | 5/5/3 (13) | 6/6/4 (16) | +3 |
| 261 | Halicz | 3/3/2 (8) | 4/4/4 (12) | +4 |
| 269 | Podlasia | 5/5/3 (13) | 7/7/5 (19) | +6 |
| 270 | Troki | 3/3/2 (8) | 4/4/3 (11) | +3 |
| 271 | Samogitia | 2/2/2 (6) | 3/3/3 (9) | +3 |
| 272 | Lithuania | 5/5/3 (13) | 6/6/4 (16) | +3 |
| 276 | Minsk | 3/3/1 (7) | 4/4/2 (10) | +3 |
| 278 | Pinsk | 3/2/1 (6) | 4/3/2 (9) | +3 |
| 279 | Volhynia | 4/4/2 (10) | 6/6/4 (16) | +6 |
| 280 | Kiev | 4/4/2 (10) | 6/6/4 (16) | +6 |
| 281 | Kamienec | 2/2/2 (6) | 3/3/2 (8) | +2 |
| 282 | Yedisan | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 283 | Zaporozhia | 1/1/2 (4) | 2/2/3 (7) | +3 |
| 290 | Poltava | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 292 | Mogilyov | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 293 | Smolensk | 4/4/1 (9) | 5/5/2 (12) | +3 |
| 295 | Moskva | 6/6/5 (17) | 5/5/4 (14) | -3 |
| 297 | Bryansk | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 771 | Vitebsk | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 1936 | Kovno | 3/3/1 (7) | 4/4/2 (10) | +3 |
| 1937 | Grodno | 2/2/1 (5) | 4/4/3 (11) | +6 |
| 1940 | Belz | 4/3/2 (9) | 5/4/4 (13) | +4 |
| 1942 | Zhytomyr | 1/2/1 (4) | 2/3/2 (7) | +3 |
| 1943 | Bratslav | 2/3/2 (7) | 4/5/4 (13) | +6 |
| 1944 | Cherkasy | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 1945 | Novgorod-Seversky | 1/2/1 (4) | 2/3/2 (7) | +3 |
| 1952 | Maramaros | 2/2/1 (5) | 4/4/3 (11) | +6 |
| 2406 | Ingil | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 2407 | Pereyaslav | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 2424 | Peremyshl | 3/3/1 (7) | 5/5/2 (12) | +5 |
| 2960 | Sadecki | 6/6/2 (14) | 8/8/4 (20) | +6 |
| 2961 | Lwow | 5/5/2 (12) | 5/5/3 (13) | +1 |
| 2962 | Rowne | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 4115 | Mazyr | 2/2/2 (6) | 3/3/3 (9) | +3 |
| 4242 | Ula | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 4243 | Toropets | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 4244 | Starodub | 2/2/1 (5) | 2/3/2 (7) | +2 |
| 4245 | Vyazma | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 4246 | Mstislav | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 4247 | Owrucz | 1/2/1 (4) | 2/3/2 (7) | +3 |
| 4527 | Checiny | 3/2/2 (7) | 4/3/3 (10) | +3 |
| 4536 | Lida | 2/2/2 (6) | 3/3/3 (9) | +3 |
| 4537 | Nowogrodek | 2/1/1 (4) | 3/2/2 (7) | +3 |
| 4539 | Kremenets | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 4540 | Winnica | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 4541 | Drohobycz | 2/2/1 (5) | 2/3/1 (6) | +1 |
| 4542 | Lubnie | 2/2/1 (5) | 3/3/2 (8) | +3 |
| 4544 | Bobrujsk | 1/1/1 (3) | 2/2/2 (6) | +3 |
| 4545 | Sluck | 2/3/1 (6) | 3/4/2 (9) | +3 |

## Structural and timeline errors

No structural errors.

## Warnings and retained vanilla quirks

- 281 (Kamienec)@1672.8.18: owner TUR lacks core (inherited vanilla quirk)
- 293 (Smolensk)@1395.1.1: owner LIT lacks core (inherited vanilla quirk)
- 293 (Smolensk)@1399.1.1: owner LIT lacks core (inherited vanilla quirk)
- 1943 (Bratslav)@1672.8.18: owner TUR lacks core (inherited vanilla quirk)
- 1943 (Bratslav)@1685.1.1: owner TUR lacks core (inherited vanilla quirk)
- 4242 (Ula)@1569.7.1: owner changed to PLC during inherited wartime occupation by RUS
- 4245 (Vyazma)@1395.1.1: owner LIT lacks core (inherited vanilla quirk)
- 4245 (Vyazma)@1399.1.1: owner LIT lacks core (inherited vanilla quirk)
- 4540 (Winnica)@1672.8.18: owner TUR lacks core (inherited vanilla quirk)
- 4540 (Winnica)@1685.1.1: owner TUR lacks core (inherited vanilla quirk)

## Complete override diffs

### 153 - Pest.txt

RIP SHA256: `13658b35b19b2475ff043c18f508c8fb5aa9f4454c0d59986f8632fe252db23e`

Vanilla SHA256: `6abba11a4e7e1f9f5264ca5df53b8094a974e4f6edacf49df1f1f06080db5ed6`

```diff
--- vanilla/153 - Pest.txt
+++ RIP/153 - Pest.txt
@@ -1,4 +1,3 @@
-#153 - Pest (Pest + Pilis + Esztergom + Kalocsa + most of Kiskunság + Parts of Nógrád )
 
 owner = HUN
 controller = HUN 
@@ -7,7 +6,7 @@
 capital = "Buda"
 trade_goods = grain
 hre = no
-base_tax = 5
+base_tax = 6
 base_production = 4
 base_manpower = 2
 is_city = yes
```

### 259 - Sandomierz.txt

RIP SHA256: `cc32fbc6e30d0c118ae9cad35dd111cbcb8a48515e86078589d62564b2a40b07`

Vanilla SHA256: `37604cc5a380bef9350308ce8fe992ae32fb17c10b1526fa80baad46b02cff91`

```diff
--- vanilla/259 - Sandomierz.txt
+++ RIP/259 - Sandomierz.txt
@@ -1,4 +1,3 @@
-#259 - Sandomierz
 
 owner = POL
 controller = POL
@@ -7,9 +6,9 @@
 religion = catholic
 trade_goods = cloth
 hre = no
-base_tax = 4
-base_production = 4
-base_manpower = 1
+base_tax = 5
+base_production = 5
+base_manpower = 2
 is_city = yes
 add_core = POL
```

### 260 - Lublin.txt

RIP SHA256: `343de70a7313a7f010bbc16d2b3c411799723fa390376037a80386fa63b9f72d`

Vanilla SHA256: `573586e429375ffbbd053964dbcb847096ebc761a328bac7243afe6b99f17883`

```diff
--- vanilla/260 - Lublin.txt
+++ RIP/260 - Lublin.txt
@@ -1,4 +1,3 @@
-#260 - Lublin
 
 latent_trade_goods = {
 	coal
@@ -11,9 +10,9 @@
 religion = catholic
 trade_goods = cloth
 hre = no
-base_tax = 5
-base_production = 5
-base_manpower = 3
+base_tax = 6
+base_production = 6
+base_manpower = 4
 is_city = yes
 add_core = POL
 discovered_by = KAZ
@@ -29,6 +28,7 @@
 center_of_trade = 2
 
 
+1444.11.1 = { owner = POL controller = POL add_core = VLN }
 1490.1.1 = { unrest = 6 } # Uprising led by Mukha
 1492.1.1 = { unrest = 0 } 
 1550.1.1 = { religion = reformed }
@@ -42,11 +42,9 @@
 1589.1.1 = { revolt = {} controller = PLC } # Coronation of Sigismund III
 1596.1.1 = { unrest = 4 } # Religious struggles, union of Brest
 1597.1.1 = { unrest = 0 }
-# The Deluge
 1733.1.1 = { revolt = { type = revolutionary_rebels size = 0 } controller = REB } # The war of Polish succession
 1735.1.1 = { revolt = {} controller = PLC }
 1781.1.1 = { unrest = 4 } # Struggle against serfdom
- # Second settlement patent
 1794.3.24 = { unrest = 8 } # Kosciuszko uprising
 1794.11.16 = { unrest = 0 } # The end of the uprising
 1795.10.24 = {
```

### 261 - Halicz.txt

RIP SHA256: `9ddb05c2455c85b7df32a67e1e3d8fbe9cc159b243f44d1c71f5e238e176909f`

Vanilla SHA256: `ebb1019de6de9a6fbdd4374d3bb4674a44e29476969df9d8d32374279949c4c3`

```diff
--- vanilla/261 - Halicz.txt
+++ RIP/261 - Halicz.txt
@@ -1,4 +1,3 @@
-#261 - Halicz
 
 owner = POL
 controller = POL
@@ -7,12 +6,12 @@
 religion = orthodox
 trade_goods = grain
 hre = no
-base_tax = 3
-base_production = 3
-base_manpower = 2
+base_tax = 4
+base_production = 4
+base_manpower = 4
 is_city = yes
 add_core = POL
-add_core = VOL
+add_core = HLC
 discovered_by = KAZ
 discovered_by = CRI
 discovered_by = GOL
@@ -24,6 +23,7 @@
 discovered_by = ottoman
 
 
+1439.11.1 = { owner = HLC controller = HLC }
 1492.1.1 = { unrest = 0 } 
 1569.7.1 = {
 	owner = PLC
```

### 269 - Podlasia.txt

RIP SHA256: `d187f87babcde14422cb64b237a2fc706c778a1d999c670454ff4afae5aea6c9`

Vanilla SHA256: `5c975bc4ca565e11beeffb1c9afe12a8ed3d49aed96dd3cd9441f3a520a8b93a`

```diff
--- vanilla/269 - Podlasia.txt
+++ RIP/269 - Podlasia.txt
@@ -1,18 +1,16 @@
-#269 - Podlasia
 
 owner = LIT
-controller = LIT
-culture = polish
+controller = LIT  
+culture = ruthenian
 religion = catholic
 hre = no
 trade_goods = livestock
-base_tax = 5
-base_production = 5
-base_manpower = 3
-capital = "Drohiczyn"
+base_tax = 7
+base_production = 7
+base_manpower = 5
+capital = "Bialystok"
 is_city = yes
 add_core = LIT
-#fort_15th = yes
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
@@ -20,6 +18,7 @@
 discovered_by = nomad_group
 
 
+1444.11.1 = { owner = LIT controller = LIT add_core = VLN }
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
```

### 270 - Troki.txt

RIP SHA256: `ec9c7864a9c3d53136c44ad3fdca416715a729b1b732f0b62e98222108f25b3f`

Vanilla SHA256: `0e6ae79f640e8c0081b630542c59266de35fecd9ee85a602a4768d46c1026ba2`

```diff
--- vanilla/270 - Troki.txt
+++ RIP/270 - Troki.txt
@@ -1,4 +1,3 @@
-#270 Troki
 
 owner = LIT
 controller = LIT
@@ -7,11 +6,10 @@
 capital = "Trakai"
 trade_goods = livestock
 hre = no
-base_tax = 3
-base_production = 3
-base_manpower = 2 
+base_tax = 4
+base_production = 4
+base_manpower = 3 
 is_city = yes
-#fort_15th = yes #Trakai Castles "Little Marienburg"
 add_core = LIT
 discovered_by = western
 discovered_by = eastern
```

### 271 - Samogitia.txt

RIP SHA256: `8116d42870427d4a3d72f114d955cfd4fd4d01c0172655f43b6d7471c0353416`

Vanilla SHA256: `7e4fca21ae0f11d56115e69d098956abcbaf0e0f5d35d7e04dc957123195297f`

```diff
--- vanilla/271 - Samogitia.txt
+++ RIP/271 - Samogitia.txt
@@ -1,4 +1,3 @@
-#271 - Samogitia
 
 owner = LIT
 controller = LIT
@@ -7,9 +6,9 @@
 capital = "Varniai"
 trade_goods = livestock
 hre = no
-base_tax = 2
-base_production = 2
-base_manpower = 2
+base_tax = 3
+base_production = 3
+base_manpower = 3
 is_city = yes
 add_core = LIT
 discovered_by = KAZ
@@ -31,7 +30,6 @@
 } # Union of Lublin
 1701.1.1 = { controller = SWE } # Swedish occupation
 1706.9.24 = { controller = PLC } # Treaty of Altranstadt
- # Great plague, lost almost two thirds of its population
 1794.3.24 = { unrest = 6 } # Kosciuszko uprising
 1794.11.16 = { unrest = 0 }
 1795.10.24 = { owner = RUS controller = RUS add_core = RUS } # Annexed by Russia, third partition
```

### 272 - Lithuania.txt

RIP SHA256: `cc9c847db7d0dc171736191c72eb2bc232e12360609e519df133f5c5d905b5f6`

Vanilla SHA256: `b6e6028958341823b30c755f239ddd0a96de67dccada0a5815122b65d73b7a60`

```diff
--- vanilla/272 - Lithuania.txt
+++ RIP/272 - Lithuania.txt
@@ -1,4 +1,3 @@
-#272 Lithuania
 
 owner = LIT
 controller = LIT
@@ -8,9 +7,9 @@
 religion = catholic
 trade_goods = grain
 hre = no
-base_tax = 5
-base_production = 5
-base_manpower = 3
+base_tax = 6
+base_production = 6
+base_manpower = 4
 fort_15th = yes #Vilnius Castle Complex
 add_core = LIT
 discovered_by = western
```

### 276 - Minsk.txt

RIP SHA256: `17a9d960573f2cbabe79b0fc6a6567f1434f354c9679daca22ca445b16258e94`

Vanilla SHA256: `90cd8682b071df4a9b6c9b856ef5d78887a64f74436b5d2f18dfc8d1ed3b0f42`

```diff
--- vanilla/276 - Minsk.txt
+++ RIP/276 - Minsk.txt
@@ -1,18 +1,17 @@
-#276 - Minsk
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 3
-base_production = 3
+base_tax = 4
+base_production = 4
 trade_goods = naval_supplies 
-base_manpower = 1
+base_manpower = 2
 capital = "Minsk"
 is_city = yes
 add_core = LIT
-#fort_15th = yes
+add_core = MSK
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
```

### 277 - Brest.txt

RIP SHA256: `3159f4006800fab7452a84b04302bcc05a66c57202a8ccfd975adf1081ba4645`

Vanilla SHA256: `b2cf35c48d5ef123ebda6bec3593e30377f755ff2b6c9ec84a9beb7811ee091c`

```diff
--- vanilla/277 - Brest.txt
+++ RIP/277 - Brest.txt
@@ -2,7 +2,7 @@
 
 owner = LIT
 controller = LIT  
-culture = byelorussian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 2
@@ -12,6 +12,7 @@
 capital = "Brest-Litovsk"
 is_city = yes 
 add_core = LIT
+add_core = VLN
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
@@ -19,6 +20,7 @@
 discovered_by = nomad_group
 
 
+1439.11.1 = { owner = VLN controller = VLN }
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
```

### 278 - Pinsk.txt

RIP SHA256: `08fd86f6de393dbf0759f73f3d44d24aed66a7141f99f4dfadd7ab9e990c87e9`

Vanilla SHA256: `1d4bd5cd5723ea090e94d9b65ab9361e6d55ccec8cc3e55f71a7c4a0a9d1cd30`

```diff
--- vanilla/278 - Pinsk.txt
+++ RIP/278 - Pinsk.txt
@@ -1,14 +1,13 @@
-#278 - Pinsk
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 3
-base_production = 2
+base_tax = 4
+base_production = 3
 trade_goods = wool  
-base_manpower = 1
+base_manpower = 2
 capital = "Pinsk"
 is_city = yes
 add_core = LIT
@@ -36,7 +35,6 @@
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
 1655.10.5 = { controller = RUS } # Occupied, Pinsk and castle completely destroyed 
 1656.1.1 = { controller = PLC }
- # Destroyed again, this time by the Swedish army, Karl XII
 1793.1.23 = {
 	owner = RUS
 	controller = RUS
```

### 279 - Volhynia.txt

RIP SHA256: `6a563cf0752305f5a0fca2b0aa60c3959f991bbb562b92273a9e56a09583b519`

Vanilla SHA256: `10bb193e2be80305d26d248af95a48b409a1c8af37f2b58eb75bb53a2eb4a3ba`

```diff
--- vanilla/279 - Volhynia.txt
+++ RIP/279 - Volhynia.txt
@@ -1,17 +1,17 @@
-#279 - Volhynia
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 4
-base_production = 4
+base_tax = 6
+base_production = 6
 trade_goods = livestock  
-base_manpower = 2
+base_manpower = 4
 capital = "Volodymyr"
 is_city = yes
-add_core = VOL
+fort_15th = yes
+add_core = VLN
 add_core = LIT
 discovered_by = western
 discovered_by = eastern
@@ -20,9 +20,9 @@
 discovered_by = nomad_group
 
 
+1439.11.1 = { owner = VLN controller = VLN remove_core = LIT }
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = {
-	remove_core = LIT	# Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	religion = catholic
 	owner = PLC
 	controller = PLC
```

### 280 - Kiev.txt

RIP SHA256: `d856e20b4544cfcb44eaf4e7709be5d3ccee24e37a8b51ef1685bf81ce07f83c`

Vanilla SHA256: `7f976b31208bc3c74d8d2ada24a3bdbca5e3d26fa2120b67aa4b9d6e2995f3f3`

```diff
--- vanilla/280 - Kiev.txt
+++ RIP/280 - Kiev.txt
@@ -1,15 +1,14 @@
-#280 - Kiev
 
 owner = LIT
 controller = LIT  
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 4
-base_production = 4
+base_tax = 6
+base_production = 6
 trade_goods = grain 
-base_manpower = 2
-capital = "Kiev"
+base_manpower = 4
+capital = "Kyiv"
 is_city = yes
 add_core = KIE
 add_core = LIT
@@ -21,24 +20,115 @@
 extra_cost = 16
 center_of_trade = 2
 
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
+
 1550.1.1 = { fort_15th = yes }
+
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
 	add_core = PLC
-}# Union of Lublin
-1595.1.1 = { unrest = 4 } # Union of Brest, religious struggles
-1596.1.1 = { unrest = 0 } 
-1648.1.1 = {	revolt = { type = nationalist_rebels size = 0 }
+	base_tax = 7
+	base_production = 7
+}
+
+1595.1.1 = { unrest = 5 }
+1596.1.1 = { unrest = 8 } # Union proclaimed
+1620.1.1 = { unrest = 4 } # Battle of Cecora
+
+1632.1.1 = { 
+	unrest = 2
+	add_permanent_province_modifier = {
+		name = "kyiv_mohyla_academy"
+		duration = -1
+	}
+}
+
+1648.1.1 = {
+	revolt = { type = nationalist_rebels size = 3 }
 	controller = REB
 	add_core = ZAZ
-}# Chmielnicki uprising, civil war
-1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+	add_core = HET
+	unrest = 15
+}
+
+1648.6.1 = { 
+	revolt = {} 
+	controller = ZAZ
+	owner = ZAZ
+	unrest = 0
+}
+
+1649.8.8 = {
+	add_permanent_province_modifier = {
+		name = "hetmanate_capital"
+		duration = -1
+	}
+}
+
+1654.1.8 = { 
+	add_permanent_province_modifier = {
+		name = "het_kyiv_russian_protection"
+		duration = -1
+	}
+}
+
+1658.9.16 = {
+	owner = PLC
+	controller = PLC
+	remove_core = ZAZ
+}
+
+1659.6.17 = {
+	owner = ZAZ
+	controller = ZAZ
+	add_core = ZAZ
+}
+
+1663.1.1 = {
+	unrest = 8
+}
+
 1667.1.30 = {
 	owner = RUS
 	controller = RUS
 	add_core = RUS
 	remove_core = PLC
-}# Treaty of Andrusovo
-1768.1.1 = { unrest = 8 } # Kolivshchyna rebellion, peasant uprising
-1769.1.1 = { unrest = 0 } # Suppressed by Polish and Russian troops
+}
+
+1687.1.1 = {
+	base_tax = 8
+	base_production = 8
+	add_province_modifier = {
+		name = "het_kyiv_mazepa_golden_age"
+		duration = 8030
+	}
+}
+
+1709.7.8 = { 
+	unrest = 6
+	remove_province_modifier = hetmanate_capital
+}
+
+1722.1.1 = {
+	remove_province_modifier = "het_kyiv_russian_protection"
+}
+
+1750.1.1 = {
+	add_province_modifier = {
+		name = "kyiv_autonomy_guaranteed"
+		duration = 5475
+	}
+}
+
+1764.11.10 = {
+	remove_province_modifier = kyiv_autonomy_guaranteed
+	remove_province_modifier = kyiv_mohyla_academy
+	remove_core = HET
+	remove_core = ZAZ
+	unrest = 4
+}
+
+1768.1.1 = { unrest = 12 }
+1769.1.1 = { unrest = 3 }
+1770.1.1 = { unrest = 0 }
```

### 281 - Kamienec.txt

RIP SHA256: `3c80f95b6c31621ce76b5f0bd0f9bf12761af89187a4fa9f9acc49b9c5947270`

Vanilla SHA256: `a002be36af7d43ef1f917cf2140ac64a203cb6ba69710f160703f8260d6f4b7e`

```diff
--- vanilla/281 - Kamienec.txt
+++ RIP/281 - Kamienec.txt
@@ -1,29 +1,30 @@
-#281 - Podolia
 
 owner = POL
 controller = POL
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = livestock 
 base_manpower = 2
-capital = "Kamieniec"
+capital = "Kamianec"
 is_city = yes
 fort_15th = yes
-add_core = VOL
+add_core = HLC
 add_core = POL
+add_core = PDL
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1439.11.1 = { owner = HLC controller = HLC remove_core = POL add_claim = KIE }
+
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
-	remove_core = POL
 	add_core = PLC
 } # Union of Lublin
 1648.1.1 = {
@@ -32,6 +33,11 @@
 	add_core = ZAZ
 } # Chmielnicki uprising, civil war
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+	add_core = PDL
+} # Andrusovo truce, but goes war with Doroshenko
 1672.8.18 = {	owner = TUR controller = TUR } # Treaty of Buchach
 1699.1.26 = { owner = PLC controller = PLC } # Treaty of Karlowitz
 1768.1.1 = { unrest = 8 } # Kolivshchyna rebellion, peasant uprising
@@ -39,4 +45,3 @@
 1793.1.23 = { owner = RUS controller = RUS add_core = RUS }
 1794.3.24 = { unrest = 5 } # Kosciuszko uprising, minimize the Russian influence
 1794.11.16 = { unrest = 0 }
-
```

### 282 - Yedisan.txt

RIP SHA256: `c3309672093b1cce94f74ecbd0b599977e94aa0ea4facf3be8650ef880b35296`

Vanilla SHA256: `321fdcacad3739fd35021e9f944222c8bc5c6f0cd288bd674b794750e9c5ce24`

```diff
--- vanilla/282 - Yedisan.txt
+++ RIP/282 - Yedisan.txt
@@ -1,14 +1,13 @@
-#282 - Yedisan
 
 owner = CRI
 controller = CRI
 culture = crimean
 religion = sunni
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = livestock
-base_manpower = 1
+base_manpower = 2
 capital = "Hajibey"
 is_city = yes
 add_local_autonomy = 25
@@ -28,13 +27,15 @@
 }
 
 1444.1.1 = { owner = LIT controller = LIT add_core = LIT culture = ruthenian religion = orthodox }
+
+1444.11.1 = { owner = ZAZ controller = ZAZ remove_core = CRI remove_core = LIT add_claim = CRI }
+
 1475.6.1 = { owner = TUR controller = TUR add_core = TUR } # Ottomans take Hajibey
- # Ochakov/Kara-kermen fortress built
 1737.7.2 = { controller = RUS } # Occupied by Russia
 1739.9.29 = { controller = TUR } # Treaty of Nish
 1770.9.30 = { controller = RUS } # Occupied by Russia
 1774.7.21 = { controller = TUR } # Treaty of Kuchuk-Kainarji
-1783.4.8 = { remove_core = CRI } # Crimean khanate abolished
 1788.12.17 = { controller = RUS } # Occupied by Russia
-1792.1.9 = { owner = RUS controller = RUS add_core = RUS remove_core = TUR capital = "Ochakov" } # Treaty of Jassy
+1792.1.9 = { owner = RUS controller = RUS add_core = RUS remove_core = TUR capital = "Ochakiv" } # Treaty of Jassy cedes the Ochakiv steppe
+1794.1.1 = { capital = "Odesa" } # Hajibey refounded as Odesa; see odesa_republic.1
```

### 283 - Zaporozhia.txt

RIP SHA256: `7970b8ead7b7c1b01a6befa215350a34ba7086c5be1209850bad6dc5f8321e46`

Vanilla SHA256: `e7dd3c41edf5cc99e5caccc41faa8ed5e21c77093442495a107c0a5229a4abd8`

```diff
--- vanilla/283 - Zaporozhia.txt
+++ RIP/283 - Zaporozhia.txt
@@ -1,14 +1,13 @@
-#283 - Zaporozhia
 
 owner = CRI
 controller = CRI
 culture = crimean
 religion = sunni
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = livestock
-base_manpower = 2
+base_manpower = 3
 capital = "Sich"
 is_city = yes
 add_core = CRI
@@ -20,10 +19,161 @@
 discovered_by = nomad_group
 
 1444.1.1 = { owner = LIT controller = LIT add_core = LIT culture = ruthenian religion = orthodox }
-1555.1.1 = { owner = ZAZ controller = ZAZ remove_core = CRI culture = ruthenian religion = orthodox base_manpower = 4 } # Fortified military camp, independent state
-1709.7.8 = { unrest = 6 } # Persecuted by the Russians after Zaporizhia became an ally of Hetman
-1734.1.1 = { unrest = 0 }
-1764.1.1 = { owner = RUS controller = RUS add_core = RUS } # Sich liquidated
-1768.1.1 = { unrest = 8 } # Kolivshchyna rebellion, peasant uprising
-1769.1.1 = { unrest = 0 } # Suppressed by Polish and Russian troops
-1775.5.7 = { remove_core = ZAZ } # Zaporozhian host abolished
+
+1444.11.1 = { owner = ZAZ controller = ZAZ remove_core = CRI remove_core = LIT }
+
+1552.1.1 = { 
+	base_manpower = 4
+	add_permanent_province_modifier = {
+		name = "zaporozhian_sich_capital"
+		duration = -1
+	}
+}
+
+1556.1.1 = { fort_15th = yes }
+
+1569.7.1 = {
+	owner = PLC
+	controller = PLC
+	add_core = PLC
+}
+
+1590.1.1 = { unrest = 3 }
+1591.1.1 = { unrest = 5 } # Kosinsky uprising
+1593.1.1 = {
+	unrest = 0
+	remove_province_modifier = "zaporozhian_sich_capital"
+	add_permanent_province_modifier = {
+		name = "sich_outpost"
+		duration = -1
+	}
+}
+
+1594.1.1 = { unrest = 8 } # Nalyvaiko uprising begins
+1596.1.1 = { unrest = 10 }
+1597.5.1 = { unrest = 0 } # Uprising suppressed
+
+1628.1.1 = { capital = "Mykytyn Sich" }
+1638.8.1 = { unrest = 10 } # Pawluk and Ostryanyn uprisings
+1639.1.1 = { unrest = 0 }
+
+1648.1.1 = {
+	revolt = { type = nationalist_rebels size = 2 }
+	controller = REB
+	unrest = 15
+}
+
+1648.6.1 = { 
+	revolt = {} 
+	controller = ZAZ 
+	owner = ZAZ
+	remove_core = PLC
+	unrest = 0
+	base_manpower = 5
+}
+
+1654.1.8 = { 
+	add_permanent_province_modifier = {
+		name = "russian_protection"
+		duration = -1
+	}
+}
+
+1657.1.1 = { unrest = 5 }
+1663.1.1 = { unrest = 8 } # Peak of Ruin
+1667.1.30 = { unrest = 6 } # Treaty of Andrusovo
+
+1669.1.1 = {
+	owner = TUR
+	controller = TUR
+	add_core = TUR
+	remove_province_modifier = "russian_protection"
+}
+
+1676.10.27 = {
+	owner = RUS
+	controller = RUS
+	add_core = RUS
+	remove_core = TUR
+	unrest = 3
+}
+
+1687.1.1 = { 
+	unrest = 0
+	base_tax = 3
+	base_production = 3
+	capital = "Chortomlyk Sich"
+	add_permanent_province_modifier = {
+		name = "zaporozhian_sich_capital"
+		duration = -1
+	}
+}
+
+1709.7.8 = { 
+	unrest = 8
+	remove_province_modifier = "zaporozhian_sich_capital"
+}
+
+1711.1.1 = {
+	owner = CRI
+	controller = CRI
+	add_core = CRI
+}
+
+1728.1.1 = {
+	owner = TUR
+	controller = TUR
+	add_core = TUR
+	remove_core = RUS
+}
+
+1734.1.1 = { 
+	owner = RUS 
+	controller = RUS 
+	add_core = RUS
+	remove_core = TUR
+	remove_core = CRI
+	unrest = 0
+	capital = "Nova Sich"
+	add_permanent_province_modifier = {
+		name = "zaporozhian_sich_capital"
+		duration = -1
+	}
+}
+
+1750.1.1 = { unrest = 4 }
+
+1762.1.1 = { 
+	base_manpower = 6
+	add_permanent_province_modifier = {
+		name = "frontier_fortress"
+		duration = -1
+	}
+}
+
+1764.1.1 = { unrest = 3 } # Hetmanate abolished
+
+1768.1.1 = {
+	unrest = 10
+}
+1769.1.1 = {
+	unrest = 5
+}
+1775.6.5 = {
+	unrest = 15
+	remove_core = ZAZ
+	add_province_modifier = {
+		name = "sich_destroyed"
+		duration = 3650
+	}
+}
+
+1776.1.1 = {
+	base_tax = 4
+	base_production = 4
+	base_manpower = 4
+	unrest = 8
+}
+
+1780.1.1 = { unrest = 3 }
+1785.1.1 = { unrest = 0 }
```

### 289 - Chernigov.txt

RIP SHA256: `813674d5dc9ac11c8070c1294693150b51bdcc962e0cf1a28fad01efc7413277`

Vanilla SHA256: `edd91ae76f9bca819241c67acdbe04d4e22030443791e3322ede9e28992ffef1`

```diff
--- vanilla/289 - Chernigov.txt
+++ RIP/289 - Chernigov.txt
@@ -1,24 +1,25 @@
-#289 - Chernigov
 
 owner = LIT
 controller = LIT  
-culture = ryazanian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 2
 base_production = 2
 trade_goods = iron 
 base_manpower = 1
-capital = "Chernigov"
+capital = "Chernihiv"
 is_city = yes
 add_core = CHR
 add_core = LIT
-add_local_autonomy = 10
+add_core = KHK
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
+
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT }
 
 1503.1.1 = { controller = MOS }
 1503.3.21 = { owner = MOS add_core = MOS }
@@ -41,7 +42,6 @@
 	controller = REB
 	add_core = ZAZ
 } # Chmielnicki Rebellion
- # Military and territorial unit at the time
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
 1657.1.1 = {
 	owner = RUS
```

### 290 - Poltava.txt

RIP SHA256: `07420ec2a902a40621f7105b3bbdd1eec4b30b9cab77ec0e7e71b4f89eaabddb`

Vanilla SHA256: `dc03625549387e5515e296e1fb486844f09e87aa7ee7a8399fee3d5bede9225c`

```diff
--- vanilla/290 - Poltava.txt
+++ RIP/290 - Poltava.txt
@@ -1,38 +1,38 @@
-#290 - Poltava
 
 owner = LIT
 controller = LIT 
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain
-base_manpower = 1
+base_manpower = 2
 capital = "Poltava"
 is_city = yes
-#add_local_autonomy = 10
 add_core = CHR
 add_core = LIT
+add_core = PRL
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT  add_claim = ZAZ }
+
 1569.7.1 = {	owner = PLC
 	controller = PLC
 	add_core = PLC
 } # Union of Lublin, Polish administration
-1635.1.1 = { fort_16th = yes } #Kodak Fortress
 1648.1.1 = {	revolt = { type = nationalist_rebels size = 0 }
 	controller = REB
 	add_core = ZAZ
 } # Chmielnicki uprising
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
-1667.1.1 = {
+1667.1.30 = {
 	owner = RUS
 	controller = RUS
 	add_core = RUS
 	remove_core = PLC
-} # Part of the Russian empire
+} # Treaty of Andrusovo
```

### 291 - Kharkov.txt

RIP SHA256: `16094ebb45684e7b4e9348700573fc1c2af4f86c7faf76cdbdd2617dafd24fcb`

Vanilla SHA256: `267b54d4774310b3754106b3c594f57a68a4e86972710529326fada7b99cf4fe`

```diff
--- vanilla/291 - Kharkov.txt
+++ RIP/291 - Kharkov.txt
@@ -1,4 +1,3 @@
-#291 - Kharkov
 
 latent_trade_goods = {
 	coal
@@ -6,7 +5,7 @@
 
 owner = CRI
 controller = CRI
-culture = ryazanian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 2
@@ -15,8 +14,8 @@
 base_manpower = 1
 capital = "Belgorod"
 is_city = yes
-#add_core = CHR
 add_core = CRI
+add_core = KHK
 
 
 discovered_by = western
@@ -27,11 +26,13 @@
 
 1444.1.1 = { owner = LIT controller = LIT add_core = LIT remove_core = CRI culture = ruthenian religion = orthodox }
 
-1555.1.1 = { owner = ZAZ controller = ZAZ add_core = ZAZ remove_core = LIT culture = ruthenian religion = orthodox } # Fortified military camp, independent state
+1444.11.1 = { owner = CHR controller = CHR add_core = CHR remove_core = LIT }
+
+1555.1.1 = { owner = ZAZ controller = ZAZ add_core = ZAZ culture = ruthenian religion = orthodox } # Fortified military camp, independent state
 1657.1.1 = {
 	owner = RUS
 	controller = RUS
 	add_core = RUS
 	remove_core = ZAZ
-	capital = "Kharkov" 
+	capital = "Kharkiv" 
 }
```

### 292 - Mogilyov.txt

RIP SHA256: `c4697af90231319ac96f0b5d03825834f2ce8525ff7373d68ea573d1c558ec4d`

Vanilla SHA256: `fd6c70673d93c7afaf280b97b1af8063f64d55700c9848e43e682e4d615b13c7`

```diff
--- vanilla/292 - Mogilyov.txt
+++ RIP/292 - Mogilyov.txt
@@ -1,14 +1,13 @@
-#292 - Mogilyov / Mahilyow
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox 
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = wool 
-base_manpower = 1
+base_manpower = 2
 capital = "Mahilyow"
 is_city = yes
 add_core = LIT
```

### 293 - Smolensk.txt

RIP SHA256: `6a12b29a6744d8f49eabdcd056facc511e6c72dca14595927a9a97491752ecfa`

Vanilla SHA256: `18856172e11ba162ad2517baab4121623c94522f92ffd4837d729887517f5a43`

```diff
--- vanilla/293 - Smolensk.txt
+++ RIP/293 - Smolensk.txt
@@ -1,14 +1,13 @@
-#293 - Smolensk
 
 owner = SMO
-controller = SMO
-culture = ryazanian
+controller = SMO  
+culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 4
-base_production = 4
+base_tax = 5
+base_production = 5
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Smolensk"
 is_city = yes
```

### 295 - Moskva.txt

RIP SHA256: `26c7263d416ab727fb440d21934a278f8ff51de2215f3f46ab5c9021ef88072f`

Vanilla SHA256: `82c6a8f90d728dbc25917e590781071ec429fc588d9f33c7ab1d91349a3d68ef`

```diff
--- vanilla/295 - Moskva.txt
+++ RIP/295 - Moskva.txt
@@ -1,14 +1,13 @@
-#295 - Moskva
 
 owner = MOS 
 controller = MOS 
 culture = russian
 religion = orthodox
 hre = no
-base_tax = 6
-base_production = 6
+base_tax = 5
+base_production = 5
 trade_goods = iron 
-base_manpower = 5
+base_manpower = 4
 capital = "Moskva"
 is_city = yes
 add_core = MOS
@@ -18,7 +17,7 @@
 discovered_by = nomad_group
 fort_15th = yes
 extra_cost = 16
-center_of_trade = 2
+center_of_trade = 1
 
 
 1450.1.1 = { discovered_by = SIB }
```

### 297 - Bryansk.txt

RIP SHA256: `3e79d16666280c639aa142e22bb8e1610230057575fce11dc505a1d1489f7fe3`

Vanilla SHA256: `45d30046c738cc30d2ae02c80e9a809b2767e72a7068dbe485bf4eebd9b2e3a9`

```diff
--- vanilla/297 - Bryansk.txt
+++ RIP/297 - Bryansk.txt
@@ -1,14 +1,13 @@
-#297 - Bryansk
 
 owner = LIT
 controller = LIT
-culture = ryazanian
+culture = ruthenian
 religion = orthodox 
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Bryansk"
 is_city = yes
```

### 298 - Kursk.txt

RIP SHA256: `bca4b5c83e239891cfeeea3da8a455f2cfe59478ca171f2964bd57a7f98d345d`

Vanilla SHA256: `ca11b1395cb3f20312ae4ec499f80ced751b4a578fb2f84274027edfc77dabfb`

```diff
--- vanilla/298 - Kursk.txt
+++ RIP/298 - Kursk.txt
@@ -1,8 +1,7 @@
-#298 - Kursk
 
 owner = LIT
 controller = LIT 
-culture = ryazanian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 2
@@ -13,6 +12,8 @@
 is_city = yes
 add_core = CHR
 add_core = LIT
+add_core = KHK
+add_core = OKH
 add_local_autonomy = 25
 discovered_by = western
 discovered_by = eastern
@@ -20,7 +21,9 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
-1508.10.18 = { owner = RUS controller = RUS add_core = RUS remove_core = LIT } # Treaty of 1508
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT }
+
+1508.10.18 = { owner = RUS controller = RUS add_core = RUS } # Treaty of 1508
 1596.1.1 = { fort_16th = yes } # Rebuilt as a Muscovite fortress
 1598.1.1 = { unrest = 8 } # "Time of troubles"
 1613.1.1 = { unrest = 0 } # Order returned, Romanov dynasty
```

### 299 - Voronezh.txt

RIP SHA256: `1f3bb735458375161f9e36dbebb9f8e8e4f9371e509a5ed3a928368bebe803a7`

Vanilla SHA256: `3747a0b46b175b84491acaf102a378557a6c5efa44a8675df63baba01f9fbcab`

```diff
--- vanilla/299 - Voronezh.txt
+++ RIP/299 - Voronezh.txt
@@ -1,4 +1,3 @@
-#299 - Voronezh
 
 owner = GOL
 controller = GOL
@@ -12,6 +11,8 @@
 capital = "Voronezh"
 is_city = yes
 add_core = GOL
+add_core = KHK
+add_core = SMY
 discovered_by = eastern
 discovered_by = western
 discovered_by = muslim
```

### 300 - Tula.txt

RIP SHA256: `89e241be7b3b010f902f32c95e20e13532e6c3b205f572ff147efa28ca487d31`

Vanilla SHA256: `df7f8783e6d969e088e9c1fd98d47ef4cc53d6b06751dfcb94e657892b00e92d`

```diff
--- vanilla/300 - Tula.txt
+++ RIP/300 - Tula.txt
@@ -1,4 +1,3 @@
-#300 - Tula
 
 owner = RYA
 controller = RYA
```

### 301 - Ryazan.txt

RIP SHA256: `9e7273e7ca1bb429d54e4b140b7c12e2c94dcfc242c9e2ca50a49e196cf448c7`

Vanilla SHA256: `5d700d5373f3dc0546997e10d8a3a3319cd584c09f98d6434ae0416a4cc8e713`

```diff
--- vanilla/301 - Ryazan.txt
+++ RIP/301 - Ryazan.txt
@@ -1,4 +1,3 @@
-#301 - Ryazan
 
 owner = RYA
 controller = RYA
```

### 771 - Vitebsk.txt

RIP SHA256: `846f350f60a3b7d8ce019881ff09cae4894f61fbfb63e9d07bf35449ce2b007b`

Vanilla SHA256: `663108ebcb792edaf8ae75aaf13e3cd0214894b876f5caba28468ec2567d8c04`

```diff
--- vanilla/771 - Vitebsk.txt
+++ RIP/771 - Vitebsk.txt
@@ -1,19 +1,19 @@
-#771 - Vitebsk
 
 owner = LIT
 controller = LIT
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Vitebsk"
 is_city = yes	 
 add_core = LIT
 add_core = PLT
+add_core = VTB
 discovered_by = western
 discovered_by = eastern
 discovered_by = nomad_group
```

### 1936 - Kovno.txt

RIP SHA256: `0e910590545378461d94ff11e4694de2d2d6c34053185fb3945f70e130f407a6`

Vanilla SHA256: `ffba6b241952368b191798dfa5548e9570d901a0ef4b9ce22a4691fcf1a4705c`

```diff
--- vanilla/1936 - Kovno.txt
+++ RIP/1936 - Kovno.txt
@@ -7,9 +7,9 @@
 capital = "Kovno"
 trade_goods = livestock
 hre = no
-base_tax = 3
-base_production = 3
-base_manpower = 1
+base_tax = 4
+base_production = 4
+base_manpower = 2
 is_city = yes
 fort_15th = yes
 add_core = LIT
```

### 1937 - Grodno.txt

RIP SHA256: `cb2d76177bd19abe047df05bfb36f0d87cc978f75cd90b52c66f95392ad29e76`

Vanilla SHA256: `e5a6f5dcfcdc4cd050ad2b964f5cfaeeeb03f0c7a1b636fabc97c6aeacfe7cef`

```diff
--- vanilla/1937 - Grodno.txt
+++ RIP/1937 - Grodno.txt
@@ -1,14 +1,13 @@
-#277 - Grodno
 
 owner = LIT
 controller = LIT 
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 4 
+base_production = 4
 trade_goods = livestock
-base_manpower = 1
+base_manpower = 3
 capital = "Grodno"
 is_city = yes 
 add_core = LIT
@@ -18,6 +17,7 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = LIT controller = LIT add_core = VLN }
 
 1569.7.1 = {
 	owner = PLC
```

### 1940 - Belz.txt

RIP SHA256: `2ec88065dfc1fa75ba4c446dad2f63b7bb30275544b12d02983771690053884d`

Vanilla SHA256: `9869d67ed8e6eb1603361e2c6cb1bead3fe78b8446283f583159547299493eb1`

```diff
--- vanilla/1940 - Belz.txt
+++ RIP/1940 - Belz.txt
@@ -7,9 +7,9 @@
 religion = orthodox
 trade_goods = livestock
 hre = no
-base_tax = 4 
-base_production = 3
-base_manpower = 2
+base_tax = 5
+base_production = 4
+base_manpower = 4
 is_city = yes
 add_core = MAZ
 add_core = VOL
@@ -25,7 +25,7 @@
 discovered_by = muslim
 discovered_by = ottoman
 
-
+1444.11.1 = { owner = MAZ controller = MAZ add_core = HLC }
 1462.7.1 = { owner = POL controller = POL add_core = POL remove_core = MAZ } # Belz incorporated into Poland
 1569.7.1 = {
 	owner = PLC
```

### 1941 - Turov.txt

RIP SHA256: `7901ab95ca0bb12afba56eb925dad06e55bdf819528763a7f564d209fd2f9c10`

Vanilla SHA256: `10232eb4d840075aa2ea9dd7d10daeb6dda3440ff5247bfbbbcf22405731e541`

```diff
--- vanilla/1941 - Turov.txt
+++ RIP/1941 - Turov.txt
@@ -1,8 +1,8 @@
 #Turov
 
 owner = LIT
-controller = LIT 
-culture = byelorussian
+controller = LIT  
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 1 
@@ -12,6 +12,8 @@
 capital = "Turov"
 is_city = yes
 add_core = LIT
+add_core = KIE
+add_core = TRV
 
 
 
@@ -22,6 +24,7 @@
 discovered_by = nomad_group
 
 
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
 1569.7.1 = {
 	owner = PLC
  	controller = PLC
```

### 1942 - Zhytomyr.txt

RIP SHA256: `df337f4af3660334648c4a0e0cd6745d705f54076f13c8b3ef075394a9845955`

Vanilla SHA256: `807937956647828d2e8cbbe7b4a81e1c38d67032eb145881dbe0e9579a5d91c1`

```diff
--- vanilla/1942 - Zhytomyr.txt
+++ RIP/1942 - Zhytomyr.txt
@@ -1,14 +1,14 @@
-#1942 - Zhytomyr
+#Zhytomyr
 
 owner = LIT
 controller = LIT  
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 2
+base_tax = 2
+base_production = 3
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2	
 capital = "Zhytomyr"
 is_city = yes
 add_core = KIE
@@ -19,9 +19,10 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
+
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = {
-	remove_core = LIT # Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	owner = PLC
 	controller = PLC
 	remove_core = POL
@@ -35,6 +36,15 @@
 	add_core = ZAZ
 } # Chmielnicki uprising, civil war
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+	add_core = PDL
+} # Andrusovo truce, but goes war with Doroshenko
+1676.10.16 = {
+	owner = PLC
+	controller = PLC
+} # Zhuravno treaty
 1793.1.23 = {
 	owner = RUS
 	controller = RUS
```

### 1943 - Bratslav.txt

RIP SHA256: `0469e1a34ec7cd268a04980c938cd7d51f6a8c4f6984f8cedce074ede9b025ef`

Vanilla SHA256: `6569316ff51d635c3b3521f14fd0eb6357ca98cc649e5c5b808a990875a39bd2`

```diff
--- vanilla/1943 - Bratslav.txt
+++ RIP/1943 - Bratslav.txt
@@ -1,25 +1,27 @@
-#Bratslav/East Podolia
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 3
+base_tax = 4
+base_production = 5
 trade_goods = livestock 
-base_manpower = 2
+base_manpower = 4
 capital = "Bratslav"
-is_city = yes
-#fort_15th = yes #Bratslav Castle
+is_city = yes 
+fort_15th = yes #Bratslav Castle
 add_local_autonomy = 25
 add_core = KIE
 add_core = LIT
+add_core = PDL
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
+
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
 
 1551.1.1 = { fort_15th = no }
 1569.7.1 = {
@@ -33,10 +35,17 @@
 	add_core = ZAZ
 } # Chmielnicki uprising, civil war
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+} # Andrusovo truce, but goes war with Doroshenko
 1672.8.18 = {
 	owner = TUR
 	controller = TUR
 } # Treaty of Buchach
+1685.1.1 = {
+	controller = PLC
+} # Right bank Hetmanate effectively defeated
 1699.1.26 = { owner = PLC controller = PLC } # Treaty of Karlowitz
 1768.1.1 = { unrest = 8 } # Kolivshchyna rebellion, peasant uprising
 1769.1.1 = { unrest = 0 } # Suppressed by Polish and Russian troops
```

### 1944 - Cherkasy.txt

RIP SHA256: `eaaf6461be0291e4e8bb9da7146f61b55a81ab59e3f130eecf4da0929214337c`

Vanilla SHA256: `049797486b2403dbd00bd1bffab0b455fb37f6e5ab39fe9c7920325dd2063f37`

```diff
--- vanilla/1944 - Cherkasy.txt
+++ RIP/1944 - Cherkasy.txt
@@ -5,10 +5,10 @@
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = livestock
-base_manpower = 1
+base_manpower = 2
 capital = "Cherkasy"
 is_city = yes
 add_local_autonomy = 25
@@ -20,19 +20,42 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT add_claim = ZAZ add_claim = CHR }
+
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = {
-	remove_core = LIT	# Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	owner = PLC
 	controller = PLC
 	add_core = PLC
 } # Union of Lublin
+1635.1.1 = { fort_16th = yes }
+# Kodak, raised by the Commonwealth above the first cataract to sit on the
+# Sich. The fort belongs on the right bank of the Dnieper; it stood here
+# rather than in Poltava, which is the left bank and nowhere near the
+# cataracts. Kodak has no province of its own in 1.37 - see
+# docs/MAP_REWORK_SUGGESTIONS.md - so Cherkasy carries it.
+
 1648.1.1 = {
 	revolt = { type = nationalist_rebels size = 0 }
 	controller = REB
 	add_core = ZAZ
-} # Chmielnicki uprising
+	capital = "Chyhyryn"
+} # Chmielnicki uprising; the hetman's seat moves to his own estates
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+	add_core = PDL
+} # Andrusovo truce, but goes war with Doroshenko
+1678.8.12 = { capital = "Cherkasy" }
+# Chyhyryn razed at the end of the second campaign against it, and never
+# recovered as a seat of government. Like Kodak above, it has no province of
+# its own in 1.37 - see docs/MAP_REWORK_SUGGESTIONS.md.
+
+1685.1.1 = {
+	controller = PLC
+} # Right bank Hetmanate effectively defeated
+1699.1.26 = { owner = PLC controller = PLC } # Treaty of Karlowitz
 1793.1.23 = {
 	owner = RUS
 	controller = RUS
```

### 1945 - Novgorod-Seversky.txt

RIP SHA256: `b98e82a92cbdba968fc73d043710107110d6839ae16b49456beebe507427567c`

Vanilla SHA256: `8f9737c886bcabb744714c4868b0235d9f61c94afac2d856caa0e0c94ef37183`

```diff
--- vanilla/1945 - Novgorod-Seversky.txt
+++ RIP/1945 - Novgorod-Seversky.txt
@@ -1,26 +1,32 @@
-#Severia
+#Siveria
 
 owner = LIT
-controller = LIT 
-culture = ryazanian
+controller = LIT  
+culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 2
-trade_goods = iron 
-base_manpower = 1
-capital = "Novgorod-Seversky"
+base_tax = 2
+base_production = 3
+trade_goods = iron
+base_manpower = 2
+center_of_trade = 1
+capital = "Novgorod-Siversky"
 is_city = yes
 add_core = CHR
 add_core = LIT
+add_core = KHK
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT }
 
-1503.4.1 = { owner = RUS controller = RUS add_core = RUS remove_core = LIT } # Treaty of the Annunciation
+1503.4.1 = { owner = RUS controller = RUS add_core = RUS } # Treaty of the Annunciation
+1523.1.1 = { add_local_autonomy = 10 } # Lithuanian border fortifications raise local autonomy
+1537.6.1 = { add_local_autonomy = -5 } # Ostrogski reforms restore princely oversight
+1596.1.9 = { add_permanent_province_modifier = { name = chr_bratslav_brotherhood duration = -1 } } # Printing brotherhood influence spreads east
 1598.1.1 = { unrest = 5 } # "Time of troubles"
 1611.1.1 = { controller = PLC } # Polish occupation
 1613.1.1 = { unrest = 0 } # Order returned, Romanov dynasty
@@ -35,8 +41,14 @@
 	controller = REB
 	add_core = ZAZ
 } # Chmielnicki Rebellion
+1648.7.11 = { base_tax = 3 } # Cossack host rallying swells the local markets
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
 1654.1.18 = { owner = RUS controller = RUS add_core = RUS } # Treaty of Pereyaslav
+1660.5.1 = { add_local_autonomy = 15 } # Seim regimental autonomy restored
 1667.2.9 = { remove_core = PLC } # Treaty of Andrusovo
+1708.11.2 = { unrest = 4 } # Mazepa's defection unsettles Siversk towns
+1709.7.1 = { unrest = 0 } # Poltava battle quells unrest
+1736.4.1 = { add_building = weapons } # Hetmanate commissions new ironworks
+1767.3.1 = { add_permanent_province_modifier = { name = chr_siversk_statute duration = -1 } } # Siversk Statute codifies urban rights
 1794.3.24 = { unrest = 5 } # Kosciuszko uprising, minimize the Russian influence
 1794.11.16 = { unrest = 0 }
```

### 1952 - Maramaros.txt

RIP SHA256: `3ecc9b38c921391a8493592fb668e36851b3202110d27ad2582385bfb5a1e587`

Vanilla SHA256: `dde2a95839904677f67e44a174f0d7fa3be597d6799ad20f2bc3ff17e66c70ad`

```diff
--- vanilla/1952 - Maramaros.txt
+++ RIP/1952 - Maramaros.txt
@@ -1,18 +1,19 @@
-#1952 - Máramaros
 
-owner = HUN
-controller = HUN 
-culture = ruthenian
+owner = UZH
+controller = UZH 
+culture = rusyn
 religion = orthodox
 capital = "Huszt"
-trade_goods = naval_supplies
+trade_goods = salt
 hre = no
-base_tax = 2 
-base_production = 2
-base_manpower = 1
+base_tax = 4 
+base_production = 4
+base_manpower = 3
 is_city = yes
+center_of_trade = 1
+add_local_autonomy = 35
 add_core = HUN
-
+add_core = UZH
 
 discovered_by = KAZ
 discovered_by = CRI
@@ -25,42 +26,28 @@
 discovered_by = ottoman
 
 
-1444.1.1 = { add_core = TRA }
+1465.6.1 = {
+	add_core = TRA
+} # Transylvanian estates maintain claims but autonomy charter holds
 1526.8.30 = {
-	owner = TRA
-	controller = TRA
-} # Battle of Mohács, the end of the independent Kingdom of Hungary
-1551.7.19 = {
-	owner = HAB
-	controller = HAB
 	add_core = HAB
-} # Ferdinand gains Transylvania from Treaty of Weissenburg
-1556.10.1 = { owner = TRA controller = TRA } # Isabella Jagiello is restored as queen of Transylvania
-1570.1.1 = {
-	remove_core = TRA
-	owner = HAB
-	controller = HAB
-} #Treaty of Speyer
-1604.1.1 = { revolt = { type = nationalist_rebels size = 1 } controller = REB } # The nobility in Royal Hungary rebelled against Habsburg & Jesuit repression
-1606.1.1 = { revolt = {} controller = HAB } # Peace treaty
-1619.1.1 = { revolt = { type = nationalist_rebels size = 1 } controller = REB } # Occupied by Gabriel Bethlen
-1620.1.1 = { revolt = {} }
-1626.1.1 = { controller = HAB } # The 3rd Peace of Pressburg
-1646.1.1 = { religion = catholic } # Ungvar union
-1648.1.1 = {
-	owner = TRA
-	controller = TRA
-	add_core = TRA
-	remove_core = HAB
-} # Uzgorod is united with Transylvania
-1682.1.1 = { revolt = { type = nationalist_rebels size = 1 } controller = REB } # Occupied by Imrich Tokoli
+	add_local_autonomy = 5
+} # After Mohács the Palanok charter is renewed as a loyal Rusyn march under both crowns
+1604.1.1 = {
+	unrest = 2
+} # Estates of Upper Hungary demand broader Rusyn privileges amid Bocskai's rising
+# 1646.1.1: Vanilla converts the province here (the Ungvar union); RIP leaves it Orthodox and moves the union to the scripted event rip_uzh_union.1
 1685.10.15 = {
-	revolt = {}
-	owner = HAB
-	controller = HAB
-	add_core = HAB
-	remove_core = TRA
-} # Imrich Tokoli surrendered to the emperor's soldiers
-1703.1.1 = { unrest = 6 } # Kuruc rebellion, lead by Francisc Rakoczy
- # Great plague
-1711.1.1 = { unrest = 0 } # Treaty of Szatmar, the House of Habsburg recognized as the new ruler
+	unrest = 0
+	add_local_autonomy = -15
+} # Habsburg court confirms the march as a barrier against Thököly
+1703.6.20 = {
+	unrest = 5
+} # Rákóczi's rebels test the frontier, but the march stays loyal for salt exemptions
+1711.5.1 = {
+	unrest = 0
+	add_local_autonomy = -5
+} # Treaty of Szatmár codifies Rusyn self-rule inside Royal Hungary
+1772.9.22 = {
+	add_core = GAL
+} # Galician administrators eye the salt road yet respect Huszt's statutes
```

### 2406 - Ingil.txt

RIP SHA256: `21d70de30b03cb7f6cff3a37ad4d13f7d33442c2b48cec830bb5faa3e496f339`

Vanilla SHA256: `409ba26a3171d54606fa06438461a23e1a01fb663ccace8ade999b593d4e3309`

```diff
--- vanilla/2406 - Ingil.txt
+++ RIP/2406 - Ingil.txt
@@ -1,14 +1,13 @@
-#2406 - Ingil
 
 owner = CRI
 controller = CRI
 culture = crimean
 religion = sunni
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = wine
-base_manpower = 1
+base_manpower = 2
 capital = "Kyzy-Kermen"
 is_city = yes
 add_local_autonomy = 25
@@ -31,11 +30,7 @@
 	culture = ruthenian
 	religion = orthodox 
 }
-1569.7.1 = {
-	owner = PLC
-	controller = PLC
-	remove_core = LIT
-	add_core = PLC
-} # Union of Lublin
-1570.1.1 = { owner = ZAZ controller = ZAZ add_core = ZAZ remove_core = CRI culture = ruthenian religion = orthodox } # Don Cossacks settle in the area, build fortified capital
-1764.1.1 = { owner = RUS controller = RUS add_core = RUS } # Sich liquidated
+
+1444.11.1 = { owner = ZAZ controller = ZAZ remove_core = CRI remove_core = LIT }
+
+1775.6.5 = { owner = RUS controller = RUS add_core = RUS remove_core = ZAZ } # Sich liquidated
```

### 2407 - Pereyaslav.txt

RIP SHA256: `378d740611c4533fe99a3321927fe7e2aa08b1ce844edd3a416ac44c7af4bd27`

Vanilla SHA256: `20124dbbc6197715f8daefcf81be3eefbe625871dd2297bc8447858297ba5353`

```diff
--- vanilla/2407 - Pereyaslav.txt
+++ RIP/2407 - Pereyaslav.txt
@@ -1,34 +1,42 @@
-#2407 - Pereyaslav
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain
-base_manpower = 1
-capital = "Pereyaslav"
+base_manpower = 2
+capital = "Pereiaslav"
 is_city = yes
-#add_local_autonomy = 10
 add_core = LIT
 add_core = CHR
+add_core = PRL
 discovered_by = eastern
 discovered_by = western
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT add_claim = KIE }
+
+1550.1.1 = { fort_15th = yes }
+
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
 	add_core = PLC
 } # Union of Lublin
-1648.1.1 = { revolt = { type = anti_tax_rebels size = 2 } controller = REB } # Antifeudal insurrection
-1654.1.1 = { revolt = {} controller = RUS } 
-1667.1.1 = {
+1648.1.1 = {
+	revolt = { type = nationalist_rebels size = 2 }
+	controller = REB
+	add_core = ZAZ
+} # Khmelnytsky Uprising
+1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
 	owner = RUS
+	controller = RUS
 	add_core = RUS
 	remove_core = PLC
-} # Part of the Russian empire
+} # Treaty of Andrusovo
```

### 2408 - Lipetsk.txt

RIP SHA256: `c94c7378e4102b9f562d8709314a62619d43c4f25ff11d57e4d41a451ace14c9`

Vanilla SHA256: `6ab0d5ef2e2f3834992d35c30343e19e723f581eeda6b10285dd829966dc326b`

```diff
--- vanilla/2408 - Lipetsk.txt
+++ RIP/2408 - Lipetsk.txt
@@ -1,4 +1,3 @@
-#2408 - Yelets
 
 owner = RYA
 controller = RYA
@@ -12,6 +11,8 @@
 capital = "Yelets"
 is_city = yes
 add_core = RYA
+add_core = KHK
+add_core = IZM
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
@@ -32,4 +33,4 @@
 	remove_core = CRI 
 } # Battle of Molodi
 1600.1.1 = { culture = ryazanian religion = orthodox }
-1703.1.1 = { capital = "Lipetsk" }+1703.1.1 = { capital = "Lipetsk" }
```

### 2424 - Peremyshl.txt

RIP SHA256: `077c07e29cbe9c44ea43aa674960a5aa9586fc320db292161998339d93adab31`

Vanilla SHA256: `c29ca800b86d8fa1c53c693bf4c6dafe5c8e6c00c3f18cc0490b2a6057a6c536`

```diff
--- vanilla/2424 - Peremyshl.txt
+++ RIP/2424 - Peremyshl.txt
@@ -1,18 +1,17 @@
-#2424 - Przemysl
 
 owner = POL
 controller = POL
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 3
-base_production = 3
+base_tax = 5
+base_production = 5
 trade_goods = livestock
-base_manpower = 1
+base_manpower = 2
 capital = "Przemysl"
 is_city = yes
 add_core = POL
-add_core = VOL
+add_core = HLC
 
 
 discovered_by = KAZ
@@ -25,6 +24,7 @@
 discovered_by = ottoman
 discovered_by = muslim
 
+1439.11.1 = { owner = HLC controller = HLC }
 1492.1.1 = { unrest = 0 } 
 
 1569.7.1 = {
```

### 2959 - Tarnow.txt

RIP SHA256: `7f70a8fd5d6fe15f8e74c6cb7d0719fe719ffac691a8b72cad810f18042a1df3`

Vanilla SHA256: `56d2a5840049a4b19b387753fe2b5fe3f9a7690881ab53e87f040deafcc4172e`

```diff
--- vanilla/2959 - Tarnow.txt
+++ RIP/2959 - Tarnow.txt
@@ -1,4 +1,3 @@
-#2959 - Tarnow
 
 owner = POL
 controller = POL
@@ -24,7 +23,7 @@
 discovered_by = muslim
 discovered_by = ottoman
 
-
+1444.11.1 = { owner = POL controller = POL add_core = HLC }
 1550.1.1 = { religion = reformed }
 1569.7.1 = {
 	owner = PLC
```

### 2960 - Sadecki.txt

RIP SHA256: `2f36a70c9be7492d0f85c0ace769bc53833fa192f73812bc0bc970c599ea1c43`

Vanilla SHA256: `ea0d51ea1b83cedd1652e708b1aedaf4956cf80d08bcbbdc9ae8f4e716c7acdb`

```diff
--- vanilla/2960 - Sadecki.txt
+++ RIP/2960 - Sadecki.txt
@@ -1,4 +1,3 @@
-#262 - Sadecki
 
 owner = POL
 controller = POL
@@ -6,10 +5,10 @@
 religion = catholic
 capital = "Nowy Sacz"
 hre = no
-base_tax = 6
-base_production = 6
+base_tax = 8
+base_production = 8
 trade_goods = iron
-base_manpower = 2
+base_manpower = 4
 is_city = yes
 add_core = POL
 discovered_by = KAZ
@@ -22,6 +21,8 @@
 discovered_by = muslim
 discovered_by = ottoman
 
+
+1444.11.1 = { owner = POL controller = POL add_core = HLC }
 1558.1.1 = { religion = protestant }
 1569.7.1 = {
 	owner = PLC
```

### 2961 - Lwow.txt

RIP SHA256: `bbdf9bfc0782913b55e62925623e0948998a151df396038106a7f80a3077c642`

Vanilla SHA256: `785fb25f668872df9d77e1ed86c833aefbcebd48c3c0bd4f28b2200cfa8fceaa`

```diff
--- vanilla/2961 - Lwow.txt
+++ RIP/2961 - Lwow.txt
@@ -1,4 +1,3 @@
-#2961 - Lwow
 
 latent_trade_goods = {
 	coal
@@ -6,17 +5,17 @@
 
 owner = POL
 controller = POL
-capital= "Lwów"
+capital= "Lviv"
 culture = ruthenian
 religion = orthodox
 trade_goods = dyes #Polish cochineal
 hre = no
 base_tax = 5
 base_production = 5
-base_manpower = 2
+base_manpower = 3
 is_city = yes
 add_core = POL
-add_core = VOL
+add_core = HLC
 discovered_by = KAZ
 discovered_by = CRI
 discovered_by = GOL
@@ -28,6 +27,8 @@
 discovered_by = ottoman
 extra_cost = 8
 center_of_trade = 1
+
+1439.11.1 = { owner = HLC controller = HLC }
 
 1569.7.1 = {
 	owner = PLC
```

### 2962 - Rowne.txt

RIP SHA256: `c75715b7c20640254d89526634ae25b954ebc46d96fa6259e220b6ce91b9de80`

Vanilla SHA256: `6ba4aed20035e82295dfbe9526932c5780975c6ba290b4ef76597008da89d37c`

```diff
--- vanilla/2962 - Rowne.txt
+++ RIP/2962 - Rowne.txt
@@ -1,17 +1,16 @@
-#279 - Rowne
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = livestock 
-base_manpower = 1
-capital = "Rowne"
+base_manpower = 2
+capital = "Rivne"
 is_city = yes
-add_core = VOL
+add_core = VLN
 add_core = LIT
 
 
@@ -23,9 +22,9 @@
 discovered_by = nomad_group
 
 
+1439.11.1 = { owner = VLN controller = VLN remove_core = LIT }
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = { 
-	remove_core = LIT	# Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	religion = catholic
 	owner = PLC
 	controller = PLC
```

### 4115 - Mazyr.txt

RIP SHA256: `ebdf8b961837636dc0f8aa6c1419e20ef7fdc1e30404b68d1fc31e0e883d2f3c`

Vanilla SHA256: `58ee9ba85011724036bc2366f639455b7b72356ed13f92d18d4a637d62f51852`

```diff
--- vanilla/4115 - Mazyr.txt
+++ RIP/4115 - Mazyr.txt
@@ -1,17 +1,17 @@
-# - Mazyr
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain 
-base_manpower = 2
+base_manpower = 3
 capital = "Mazyr"
 is_city = yes
 add_core = LIT
+add_core = TRV
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
```

### 4116 - Upper Oka.txt

RIP SHA256: `cef6e17b78b42a91c70f1c79228d23d431aedf1f458ac459dcf822963543f532`

Vanilla SHA256: `a39934e4539fdcdc12060b283f8b43906e0394bff4956d7a11ebb3391aa3b49a`

```diff
--- vanilla/4116 - Upper Oka.txt
+++ RIP/4116 - Upper Oka.txt
@@ -1,8 +1,7 @@
-#Upper Oka Basin
 
 owner = OKA #Controlled by various small Principalities shifting allegience between Muscovy and Lithuania
 controller = OKA 
-culture = ryazanian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 3
```

### 4242 - Ula.txt

RIP SHA256: `62e2206aa3953589d1f8879686cef559dad2208bc55e2487c19db95e61771204`

Vanilla SHA256: `898486a387713092a4477f5bb9cc4545661d963a958ed8ea16dba27c0a200731`

```diff
--- vanilla/4242 - Ula.txt
+++ RIP/4242 - Ula.txt
@@ -1,19 +1,19 @@
-#4242 - Ula
 
 owner = LIT 
 controller = LIT 
 culture = byelorussian
 religion = orthodox 
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = iron
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Ula"
 is_city = yes 
 add_core = PLT
 add_core = LIT
+add_core = VTB
 discovered_by = western
 discovered_by = eastern
 discovered_by = nomad_group
```

### 4243 - Toropets.txt

RIP SHA256: `dd901968bca55321fe01de3325ca2d1bc27e53144f578a14bd5ac84c47978d26`

Vanilla SHA256: `162d3c44b7ca3e0e56aa427c22cec1dbfcfbfd40a436a6caae90ffa1abb17810`

```diff
--- vanilla/4243 - Toropets.txt
+++ RIP/4243 - Toropets.txt
@@ -1,14 +1,13 @@
-#4243 - Toropets
 
 owner = LIT
 controller = LIT
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Toropets"
 is_city = yes
```

### 4244 - Starodub.txt

RIP SHA256: `e3b9a563899b3703856dd7d61779fde9cc55a53d0cd2b43e2a4fcc63bdc7b8b2`

Vanilla SHA256: `96c77dabfd818372cfb17ad967c887f2a5e6535acbedba6ac501b7835b9e1f44`

```diff
--- vanilla/4244 - Starodub.txt
+++ RIP/4244 - Starodub.txt
@@ -1,30 +1,38 @@
-#4244 - Trubchevsk (Trubchevsk+Starodub+Pochep)
 
 owner = LIT
-controller = LIT
-culture = ryazanian
-religion = orthodox 
+controller = LIT  
+culture = ruthenian
+religion = orthodox
 hre = no
 base_tax = 2
-base_production = 2
+base_production = 3
 trade_goods = grain
-base_manpower = 1
-add_local_autonomy = 50
+base_manpower = 2
+center_of_trade = 1
+add_local_autonomy = 40
 capital = "Trubchevsk"
 is_city = yes
 add_core = LIT
+add_core = CHR
 add_core = SMO
 discovered_by = western
 discovered_by = eastern
 discovered_by = nomad_group
 
 
-1503.4.1 = { owner = RUS controller = RUS add_core = RUS remove_core = LIT add_local_autonomy = -50 } # Treaty of the Annunciation
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT }
+1494.1.1 = { add_permanent_province_modifier = { name = chr_desna_watch duration = -1 } } # Muscovite border watchtowers across the Desna
+1503.4.1 = { owner = RUS controller = RUS add_core = RUS add_local_autonomy = -40 } # Treaty of the Annunciation
 1598.1.1 = { unrest = 5 } # "Time of troubles"
 1611.1.1 = { controller = PLC } # Polish occupation
 1613.1.1 = { unrest = 0 } # Order returned, Romanov dynasty
 1618.12.11 = { controller = RUS } # Truce of Deulino
+1648.5.1 = { add_local_autonomy = 10 } # Starodub sotnias win expanded privileges
+1667.2.9 = { add_permanent_province_modifier = { name = chr_starodub_statute duration = -1 } } # Andrusovo confirms starshyna courts
 1670.1.1 = { unrest = 8 } # Stepan Razin
 1671.1.1 = { unrest = 0 } # Razin is captured
+1708.10.30 = { unrest = 6 } # Mazepa's forces briefly occupy Starodub
+1709.9.1 = { unrest = 0 } # Poltava reasserts tsarist control
+1764.1.1 = { base_production = 4 } # Sloboda colonists expand Starodub hemp markets
 1773.1.1 = { unrest = 5 } # Emelian Pugachev, Cossack insurrection.
 1774.9.14 = { unrest = 0 } # Pugachev is captured.
```

### 4245 - Vyazma.txt

RIP SHA256: `7ec2499f531744a2f31001ad4cf8e22bd6e93b2f31c4d9bab014ec8fba1f8cb6`

Vanilla SHA256: `3f122c08d07c384aafe85fb786844ee84c4d26ba5ff15de465e39624917a21c5`

```diff
--- vanilla/4245 - Vyazma.txt
+++ RIP/4245 - Vyazma.txt
@@ -1,14 +1,13 @@
-#4245 - Vyazma
 
 owner = SMO
 controller = SMO
-culture = ryazanian
+culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = cloth 
-base_manpower = 1
+base_manpower = 2
 add_local_autonomy = 50
 capital = "Vyazma"
 is_city = yes
@@ -26,7 +25,7 @@
 1514.1.1 = { controller = RUS } # Captured by Vasili III
 1522.1.1 = { owner = RUS add_local_autonomy = -50 }
 1569.7.4 = { add_core = PLC } # Polish-Lithuanian Commonwealth
-1602.1.1 = { fort_15th = no fort_16th = yes } # Heavily fortified
+1602.1.1 = { fort_16th = yes } # Heavily fortified
 1611.1.1 = { controller = PLC }
 1618.12.11 = { owner = PLC } # Truce of Deulino
 1654.9.23 = { owner = RUS controller = RUS } # Reqonquered
```

### 4246 - Mstislav.txt

RIP SHA256: `906f99a712b512f3c3ec30a46a68e2b0529e1b26868517eaed321efcd5ce0668`

Vanilla SHA256: `52df170119b16f5b65a283562093a277377d770ff19340680d1c4447d627657f`

```diff
--- vanilla/4246 - Mstislav.txt
+++ RIP/4246 - Mstislav.txt
@@ -1,18 +1,18 @@
-#4246 - Mstislav
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox 
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = wool 
-base_manpower = 1
+base_manpower = 2
 capital = "Mstsislaw"
 is_city = yes
 add_core = LIT
 add_core = PLT
+add_core = MSL
 discovered_by = western
 discovered_by = eastern
 discovered_by = nomad_group
```

### 4247 - Owrucz.txt

RIP SHA256: `1ce4b6cca48e78ebc05cafb6eec965a15f2ee11354dafeac91326281a71bd120`

Vanilla SHA256: `d95e0dc122fa1cc099a5d62fd28c4756e9b273293d0d06c3dbfb64a5ca262a09`

```diff
--- vanilla/4247 - Owrucz.txt
+++ RIP/4247 - Owrucz.txt
@@ -1,14 +1,13 @@
-#4247 - Owrucz, Chernobyl, etc.
 
 owner = LIT
 controller = LIT  
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 2
+base_tax = 2
+base_production = 3
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2
 capital = "Ovruch"
 is_city = yes
 add_core = KIE
@@ -19,9 +18,9 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = {
-	remove_core = LIT # Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	owner = PLC
 	controller = PLC
 	remove_core = POL
@@ -35,6 +34,15 @@
 	add_core = ZAZ
 } # Chmielnicki uprising, civil war
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+	add_core = PDL
+} # Andrusovo truce, but goes war with Doroshenko
+1676.10.16 = {
+	owner = PLC
+	controller = PLC
+} # Zhuravno treaty
 1793.1.23 = {
 	owner = RUS
 	controller = RUS
```

### 4255 - Pronsk.txt

RIP SHA256: `0d34ec156f3dfa6042238d74d69655ba4ae68f51266e1991e883937528fc7f11`

Vanilla SHA256: `fc4935482d1135e091305ba28de09723e4510d11a9e0e3b29809c6e8d037b0fb`

```diff
--- vanilla/4255 - Pronsk.txt
+++ RIP/4255 - Pronsk.txt
@@ -1,4 +1,3 @@
-#4255 - Pronsk
 
 owner = RYA
 controller = RYA
@@ -31,4 +30,4 @@
 1657.1.1 = { unrest = 0 }
 1711.1.1 = { base_tax = 7 base_production = 7 } # Governmental reforms and the absolutism
 1767.1.1 = { base_tax = 8 base_production = 8 } # Legislative reform
-1778.1.1 = { capital = "Ryazan" } # Ryazan governorate formed, city renamed+1778.1.1 = { capital = "Ryazan" } # Ryazan governorate formed, city renamed
```

### 4527 - Checiny.txt

RIP SHA256: `cbb0f6fc2c6d9c27dd51df6dc97483082fcc05710a00bf4b24178e60d4034edd`

Vanilla SHA256: `37cbf4b0ee02a912591c983e2f5a11b41435e4a1001396d606da19b289ce8d4e`

```diff
--- vanilla/4527 - Checiny.txt
+++ RIP/4527 - Checiny.txt
@@ -1,4 +1,3 @@
-#4527 - Checiny
 
 owner = POL
 controller = POL
@@ -7,9 +6,9 @@
 religion = catholic
 trade_goods = cloth
 hre = no
-base_tax = 3
-base_production = 2
-base_manpower = 2
+base_tax = 4
+base_production = 3
+base_manpower = 3
 is_city = yes
 add_core = POL
```

### 4536 - Lida.txt

RIP SHA256: `0829632f3dbc462d186a156fcaa21f95f82617e4c1789ebb0442ad9105faca2c`

Vanilla SHA256: `957b5a0def6cbfaf4cf1c13715ad551ca890343b3983aa50ed11070ebe6df861`

```diff
--- vanilla/4536 - Lida.txt
+++ RIP/4536 - Lida.txt
@@ -1,4 +1,3 @@
-#4536 - Lida
 
 owner = LIT
 controller = LIT
@@ -7,11 +6,10 @@
 capital = "Lyda"
 trade_goods = livestock
 hre = no
-base_tax = 2
-base_production = 2
-base_manpower = 2 
+base_tax = 3
+base_production = 3
+base_manpower = 3 
 is_city = yes
-#fort_15th = yes #Trakai Castles "Little Marienburg"
 add_core = LIT
 discovered_by = western
 discovered_by = eastern
```

### 4537 - Nowogrodek.txt

RIP SHA256: `19049f3e94060aeb0e151da1aa3c5875ee90892d8c134334773e643d4f1fc4ad`

Vanilla SHA256: `0afea0ac1a2c71b82f68fd3c7ee7e17f14af9a43ed02a1374cf274995b70e47b`

```diff
--- vanilla/4537 - Nowogrodek.txt
+++ RIP/4537 - Nowogrodek.txt
@@ -1,14 +1,13 @@
-#4537 - Nowogrodek
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2 
-base_production = 1
+base_tax = 3 
+base_production = 2
 trade_goods = wool  
-base_manpower = 1
+base_manpower = 2
 capital = "Navahrudak"
 is_city = yes
 add_core = LIT
@@ -36,7 +35,6 @@
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
 1655.10.5 = { controller = RUS } # Occupied, Pinsk and castle completely destroyed 
 1656.1.1 = { controller = PLC }
- # Destroyed again, this time by the Swedish army, Karl XII
 1793.1.23 = {
 	owner = RUS
 	controller = RUS
```

### 4538 - Chelm.txt

RIP SHA256: `77e62ac052a9a691e5f82e69b2d4fbdfbb7d57dbe3f4a3c5f11e1fff956a146b`

Vanilla SHA256: `f40629c2e34f24e50ee517e2b99191f9b2b943d2f62621fb51bf9c8871124967`

```diff
--- vanilla/4538 - Chelm.txt
+++ RIP/4538 - Chelm.txt
@@ -1,7 +1,7 @@
 #Chelm
 
-owner = POL
-controller = POL  
+owner = VLN
+controller = VLN  
 culture = ruthenian
 religion = orthodox
 hre = no
@@ -12,6 +12,7 @@
 capital = "Chelm"
 is_city = yes 
 add_core = POL
+add_core = VLN
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
@@ -19,6 +20,7 @@
 discovered_by = nomad_group
 
 
+1439.11.1 = { owner = VLN controller = VLN }
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
```

### 4539 - Kremenets.txt

RIP SHA256: `b688fdf209ebc29fca2070a50042f3d47356072b4566121e719ce2e1958bdc99`

Vanilla SHA256: `4b056b9cd62ab995081f8819ff6bc9a555bac8a0a07a67d1b1e733daa5b8445d`

```diff
--- vanilla/4539 - Kremenets.txt
+++ RIP/4539 - Kremenets.txt
@@ -1,17 +1,16 @@
-#4539 - Kremenets
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = livestock 
-base_manpower = 1
+base_manpower = 2
 capital = "Kremenets"
 is_city = yes
-add_core = VOL
+add_core = VLN
 add_core = LIT
 
 
@@ -23,9 +22,9 @@
 discovered_by = nomad_group
 
 
+1439.11.1 = { owner = VLN controller = VLN remove_core = LIT }
 1569.3.26 = { owner = POL controller = POL add_core = POL } # annexed by Poland
 1569.7.1 = { 
-	remove_core = LIT	# Union of Lublin, western part ceded to Poland & southern part still belonged to Lithuania
 	religion = catholic
 	owner = PLC
 	controller = PLC
```

### 4540 - Winnica.txt

RIP SHA256: `df762a66ffe379911218ebef6d837c27f5dd3a3682afbd5db2a4f325108939b6`

Vanilla SHA256: `c29c3dbf93ca67f68b156ca3323b70b58cc23c4f180f2b28893f9a7949648faa`

```diff
--- vanilla/4540 - Winnica.txt
+++ RIP/4540 - Winnica.txt
@@ -1,27 +1,26 @@
-# Winnica / Vinnystia
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = livestock 
-base_manpower = 1
+base_manpower = 2
 capital = "Vinnytsia"
 is_city = yes
-#fort_15th = yes #Bratslav Castle
 add_local_autonomy = 25
 add_core = KIE
 add_core = LIT
+add_core = PDL
 discovered_by = western
 discovered_by = eastern
 discovered_by = muslim
 discovered_by = ottoman
 discovered_by = nomad_group
 
-1551.1.1 = { fort_15th = no }
+1444.11.1 = { owner = KIE controller = KIE remove_core = LIT }
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
@@ -33,10 +32,17 @@
 	add_core = ZAZ
 } # Chmielnicki uprising, civil war
 1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
+	owner = PDL
+	controller = PDL
+} # Andrusovo truce, but goes war with Doroshenko
 1672.8.18 = {
 	owner = TUR
 	controller = TUR
 } # Treaty of Buchach
+1685.1.1 = {
+	controller = PLC
+} # Right bank Hetmanate effectively defeated
 1699.1.26 = { owner = PLC controller = PLC } # Treaty of Karlowitz
 1768.1.1 = { unrest = 8 } # Kolivshchyna rebellion, peasant uprising
 1769.1.1 = { unrest = 0 } # Suppressed by Polish and Russian troops
```

### 4541 - Drohobycz.txt

RIP SHA256: `e25d088246a40fd19fa852750aabe359ee76ec5d81cdcb0e3e89012fc77bf14b`

Vanilla SHA256: `619ecb677cf382e22c6a0d513b7d7bfc4e0a0fb5812a6610ccce65fd008eef91`

```diff
--- vanilla/4541 - Drohobycz.txt
+++ RIP/4541 - Drohobycz.txt
@@ -1,18 +1,17 @@
-#4541 - Drohobycz
 
-owner = POL
-controller = POL
+owner = HLC
+controller = HLC
 culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 2
-base_production = 2
+base_production = 3
 trade_goods = livestock
 base_manpower = 1
 capital = "Drohobycz"
 is_city = yes
 add_core = POL
-add_core = VOL
+add_core = HLC
 
 
 discovered_by = KAZ
```

### 4542 - Lubnie.txt

RIP SHA256: `fc704e7074c6d2cbe637693bb533b571698c457d8227c1abff40715f9c014797`

Vanilla SHA256: `7dd3b04c4086cfcb378042578edbee3216e47266d363c790d23a32d4a73ba41a`

```diff
--- vanilla/4542 - Lubnie.txt
+++ RIP/4542 - Lubnie.txt
@@ -1,19 +1,18 @@
-#4542 - Lubnie
 
 owner = LIT
 controller = LIT
 culture = ruthenian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 2
+base_tax = 3
+base_production = 3
 trade_goods = grain
-base_manpower = 1
+base_manpower = 2
 capital = "Lubnie"
 is_city = yes
-#add_local_autonomy = 10
 add_core = LIT
 add_core = CHR
+add_core = PRL
 fort_15th = yes
 discovered_by = eastern
 discovered_by = western
@@ -21,15 +20,21 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT }
 1569.7.1 = {
 	owner = PLC
 	controller = PLC
 	add_core = PLC
 } # Union of Lublin
-1648.1.1 = { revolt = { type = anti_tax_rebels size = 2 } controller = REB } # Antifeudal insurrection
-1654.1.1 = { revolt = {} controller = RUS } 
-1667.1.1 = {
+1648.1.1 = {
+	revolt = { type = nationalist_rebels size = 2 }
+	controller = REB
+	add_core = ZAZ
+} # Khmelnytsky Uprising
+1654.1.1 = { revolt = {} controller = PLC remove_core = ZAZ }
+1667.1.30 = {
 	owner = RUS
+	controller = RUS
 	add_core = RUS
 	remove_core = PLC
-} # Part of the Russian empire
+} # Treaty of Andrusovo
```

### 4543 - Rylsk.txt

RIP SHA256: `c8f6a6af8168abd0662bd60fb0c58f2db33ebf55d86e50b7cb63cdee2c069347`

Vanilla SHA256: `565480e0d9206765d2cd436d89a5331f708bdd74d2468615d1f80c14ba988fba`

```diff
--- vanilla/4543 - Rylsk.txt
+++ RIP/4543 - Rylsk.txt
@@ -1,7 +1,6 @@
-#4543 - Rylsk
 owner = LIT
 controller = LIT 
-culture = ryazanian
+culture = ruthenian
 religion = orthodox
 hre = no
 base_tax = 1
@@ -12,6 +11,7 @@
 is_city = yes
 add_core = CHR
 add_core = LIT
+add_core = KHK
 add_local_autonomy = 25
 discovered_by = western
 discovered_by = eastern
@@ -19,7 +19,8 @@
 discovered_by = ottoman
 discovered_by = nomad_group
 
-1508.10.18 = { owner = RUS controller = RUS add_core = RUS remove_core = LIT } # Treaty of 1508
+1444.11.1 = { owner = CHR controller = CHR remove_core = LIT  add_claim = ZAZ }
+1508.10.18 = { owner = RUS controller = RUS add_core = RUS } # Treaty of 1508
 1596.1.1 = { fort_16th = yes } # Rebuilt as a Muscovite fortress
 1598.1.1 = { unrest = 8 } # "Time of troubles"
 1613.1.1 = { unrest = 0 } # Order returned, Romanov dynasty
```

### 4544 - Bobrujsk.txt

RIP SHA256: `215f2a6846b5064a679e211196d285cb76f6c005c889f4c346ea10007b2f2a89`

Vanilla SHA256: `92fa45037c2ec16a86b9e92facafc4ffb2c69eb9669dcad35dbb7d744998ed63`

```diff
--- vanilla/4544 - Bobrujsk.txt
+++ RIP/4544 - Bobrujsk.txt
@@ -1,14 +1,13 @@
-# - Bobrujsk
 
 owner = LIT
 controller = LIT  
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 1
-base_production = 1
+base_tax = 2
+base_production = 2
 trade_goods = grain 
-base_manpower = 1
+base_manpower = 2
 capital = "Bobrujsk"
 is_city = yes
 add_core = LIT
```

### 4545 - Sluck.txt

RIP SHA256: `24d7c4fefb7faf706e12a011249fc877bbfa16c6ec8d8deeb68aa3a5eea6e5d0`

Vanilla SHA256: `3ce85e4d574498d3b3a809df65b07a5b346fd00b1e3856cb43649005fd732f05`

```diff
--- vanilla/4545 - Sluck.txt
+++ RIP/4545 - Sluck.txt
@@ -5,13 +5,14 @@
 culture = byelorussian
 religion = orthodox
 hre = no
-base_tax = 2
-base_production = 3
+base_tax = 3
+base_production = 4
 trade_goods = cloth 
-base_manpower = 1
+base_manpower = 2
 capital = "Sluck"
 is_city = yes
 add_core = LIT
+add_core = MSK
```
