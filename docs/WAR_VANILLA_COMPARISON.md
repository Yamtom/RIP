# War history comparison

Installed baseline: **EU4 v1.37.5.0 Inca (491d)**

Merged files use exact-name overrides without `replace_path`.
Evaluation simulates merged `RIP + vanilla` province ownership on every dated war event.

| File | War | Mode | Span | War goal | Local findings |
|---|---|---|---|---|---|
| `CrusadeOfVarna.txt` | Crusade of Varna | override | `1443.1.1..1444.11.11` | superiority_crusade (cb_crusade) | 0 |
| `FifthRussoTurkishWar.txt` | Fifth Russo-Turkish War | override | `1806.1.1..1812.5.28` | take_capital_liberation (cb_liberation) | 0 |
| `FirstMuscoviteLithuanianWar.txt` | First Muscovite-Lithuanian War | override | `1486.1.1..1495.1.1` | take_province_nationalist (cb_nationalist) @ 272 Lithuania | 0 |
| `FourthMuscoviteLithuanianWar.txt` | Starodub War | addition | `1534.2.15..1537.2.18` | take_core (cb_core) @ 4244 Starodub | 0 |
| `FourthRussoTurkishWar.txt` | Fourth Russo-Turkish War | override | `1787.8.24..1792.1.9` | take_core (cb_core) @ 287 Kouban | 0 |
| `FrancoItalianWar.txt` | Franco-Italian War | override | `1542.1.1..1546.8.1` | take_core (cb_core) @ 104 Milan | 0 |
| `GreatNordicWar.txt` | Great Nordic War | override | `1699.12.10..1721.8.30` | superiority_punitive (cb_super_badboy) @ 1 Uppland | 0 |
| `KhmelnytskyUprising.txt` | Khmelnytsky Uprising | addition | `1648.4.19..1649.8.18` | defend_capital_independence (cb_independence_war) | 0 |
| `LivonianWar.txt` | Livonian War | override | `1558.1.22..1583.8.10` | take_claim (cb_conquest) @ 1834 Dorpat | 0 |
| `OttomanCommonwealthWar.txt` | Ottoman-Commonwealth War | override | `1672.6.4..1676.10.17` | take_border (cb_border_war) @ 2961 Lwow | 0 |
| `PolishCossackTatarWar.txt` | Polish-Cossack-Tatar War | addition | `1667.1.30..1667.10.19` | take_capital_vassalize (cb_vassalize_mission) @ 1944 Cherkasy | 0 |
| `PolishHetmanateWar.txt` | Polish-Cossack War | addition | `1651.2.20..1654.1.17` | take_capital_vassalize (cb_vassalize_mission) @ 290 Poltava | 0 |
| `PolishMuscoviteWar.txt` | Russo-Commonwealth War | override | `1605.1.1..1618.12.11` | take_capital_throne (cb_claim_throne) | 0 |
| `PolishOttomanWar1620.txt` | Polish-Ottoman War (Khotyn) | addition | `1620.9.1..1621.10.9` | take_claim (cb_conquest) @ 281 Kamienec | 0 |
| `RussoTurkishWar.txt` | Russo-Turkish War | override | `1676.11.1..1681.1.3` | take_claim (cb_conquest) @ 280 Kiev | 0 |
| `SecondMuscoviteLithuanianWar.txt` | Second Muscovite-Lithuanian War | override | `1500.5.1..1503.3.21` | take_province_nationalist (cb_nationalist) @ 293 Smolensk | 0 |
| `SecondOttomanHungarianWar.txt.txt` | Second Ottoman-Hungarian War | override | `1521.5.18..1526.8.30` | take_claim (cb_conquest) @ 153 Pest | 0 |
| `SecondRussuTurkishWar.txt` | Second Russo-Turkish War | override | `1735.7.1..1739.10.3` | take_claim (cb_conquest) @ 286 Azow | 0 |
| `SmolenskWar.txt` | Smolensk War | override | `1632.6.1..1634.6.14` | take_core (cb_core) @ 293 Smolensk | 0 |
| `TheDeluge.txt` | Russo-Polish War | override | `1654.1.18..1667.1.30` | take_claim (cb_conquest) @ 276 Minsk | 0 |
| `ThirdMuscoviteLithuanianWar.txt` | Third Muscovite-Lithuanian War | addition | `1507.2.2..1508.10.18` | take_core (cb_core) @ 289 Chernigov | 0 |
| `ThirdRussoTurkishWar.txt` | Third Russo-Turkish War | override | `1768.9.25..1774.7.21` | take_claim (cb_conquest) @ 291 Kharkov | 0 |
| `WarOfTheHolyLeague.txt` | War of the Holy League | override | `1683.3.1..1700.6.13` | take_claim (cb_conquest) @ 265 Brno | 0 |
| `WarOfThePolishSuccession.txt` | War of the Polish Succession | override | `1733.8.14..1735.10.3` | take_capital_throne (cb_claim_throne) | 0 |
| `WarOfTheSixthCoalition.txt` | War of the Sixth Coalition | override | `1812.6.21..1814.4.11` | superiority_revolution (cb_spread_the_revolution) | 0 |

## Local RIP findings

- None (`0` errors across all local war files).

## Multi-war overlaps for Ruthenian / steppe tags

- None across merged RIP + vanilla wars for `ZAZ`, `PDL`, `HET`, `CHR`, `KIE`, `HLC`, `VLN`, `OKA`, `CRI`.

## Inherited vanilla Eastern European findings (unoverridden files)

- OttomanMamlukWar.txt: WG_NOT_DEFENDER:378(Tripoli,owner=SYR,dfn=['MAM'])
- OttomanSaudiWar.txt: WG_NOT_DEFENDER:405(Tadmor,owner=TUR,dfn=['NAJ'])
- RussoPersianWar.txt: WG_NOT_DEFENDER:425(Dagestan,owner=GAZ,dfn=['PER'])
- SecondRussoPersianWar.txt: 1796.11.1: REM_MISSING_DFN:ARM
- SecondRussoPersianWar.txt: WG_NOT_DEFENDER:421(Shirvan,owner=SRV,dfn=['ARM', 'PER', 'TBR'])
- ThirdRussoPersianWar.txt: WG_NOT_DEFENDER:416(Tabriz,owner=TBR,dfn=['ARD', 'ARM', 'MGR', 'MLK', 'PER'])

## Override diffs and SHA256 hashes

### CrusadeOfVarna.txt

RIP SHA256: `7f892e7d4b81cf31862696a8c048f0544ba41be5fc4290b087b3e12984e5a8f0`

Vanilla SHA256: `a50006d821e3422a5ab6f9b14364b6549f0614b4e857197bf5d8846af294bbea`

```diff
--- vanilla/CrusadeOfVarna.txt
+++ RIP/CrusadeOfVarna.txt
@@ -51,6 +51,7 @@
 	rem_attacker = LIT
 	rem_attacker = BOS
 	rem_attacker = WAL
+	rem_attacker = MOL
 	rem_attacker = VEN
 	rem_attacker = PAP
 	rem_defender = TUR
```

### FifthRussoTurkishWar.txt

RIP SHA256: `3621cee86928832f7d47fed8a937db53082491358f179a591883d2eee57b32de`

Vanilla SHA256: `c3972ad92a10a21176c8441b4c34faed7f739f1278c18bece2bc57015c0d31ef`

```diff
--- vanilla/FifthRussoTurkishWar.txt
+++ RIP/FifthRussoTurkishWar.txt
@@ -10,6 +10,7 @@
 	add_defender = TUR
 	add_defender = WAL
 	add_defender = MOL
+	add_defender = ZAZ
 }
 
 # Treaty of Bucharest
@@ -18,4 +19,5 @@
 	rem_defender = TUR
 	rem_defender = WAL
 	rem_defender = MOL
+	rem_defender = ZAZ
 }
```

### FirstMuscoviteLithuanianWar.txt

RIP SHA256: `2f344d3207a61ed6b24e0fa15b0d3360f61925f7322166bc301caa05b38f1db0`

Vanilla SHA256: `90958ef084be2d5eee68b776da50d3bbb6eda7592b0f83ad1686cff7fc31bfe3`

```diff
--- vanilla/FirstMuscoviteLithuanianWar.txt
+++ RIP/FirstMuscoviteLithuanianWar.txt
@@ -2,7 +2,7 @@
 war_goal = {
 	type = take_province_nationalist
 	casus_belli = cb_nationalist
-	province = 272 #Vilna
+	province = 272 # Vilna
 }
 
 1486.1.1 = {
@@ -17,11 +17,14 @@
 	add_defender = TEU
 	add_defender = MAZ
 	add_defender = MOL
+	add_defender = OKA
 }
 
-#1492.1.1 = {
-#	add_attacker = CRI
-#}
+# Upper Oka principalities pass to Moscow under the Treaty of 1494
+1494.1.1 = {
+	rem_defender = OKA
+}
+
 # Marriage between Helena and Alexander
 1495.1.1 = {
 	rem_attacker = MOS
@@ -30,11 +33,9 @@
 	rem_attacker = QAS
 	rem_attacker = KAZ
 	rem_attacker = PRM
-#	rem_attacker = CRI
 	rem_defender = LIT
 	rem_defender = POL
 	rem_defender = TEU
 	rem_defender = MAZ
 	rem_defender = MOL
 }
-
```

### FourthMuscoviteLithuanianWar.txt

RIP SHA256: `e5f071a5154e1e30f67de2907ba3d4fb22b870fa53f86d35503220b6d545d61c`

New RIP war file (`addition`).

### FourthRussoTurkishWar.txt

RIP SHA256: `b0e50133365aa97fb0a24dadeb3cd4b349259b7a9a09bb0c529131e4b004d26e`

Vanilla SHA256: `33a7af153a9df13cd49036e8973492b601e4fb82df2360a6bb31d9617447a870`

```diff
--- vanilla/FourthRussoTurkishWar.txt
+++ RIP/FourthRussoTurkishWar.txt
@@ -11,6 +11,7 @@
 	add_attacker = ABB
 	add_attacker = WAL
 	add_attacker = MOL
+	add_attacker = ZAZ
 	add_defender = RUS
 	add_defender = KZH
 	add_defender = GEO
@@ -33,6 +34,7 @@
 	rem_attacker = ABB
 	rem_attacker = WAL
 	rem_attacker = MOL
+	rem_attacker = ZAZ
 	rem_defender = RUS
 	rem_defender = KZH
 	rem_defender = GEO
```

### FrancoItalianWar.txt

RIP SHA256: `1acacc4e7d6a816dd88c056e43f2c06b29294987955902aa50a0012262dcd3eb`

Vanilla SHA256: `c41218c2f7402d2f68cd4420b84f9cedd021caaa37a1f4bc6f0d33fbe000b9e8`

```diff
--- vanilla/FrancoItalianWar.txt
+++ RIP/FrancoItalianWar.txt
@@ -21,7 +21,6 @@
 	add_attacker = GEL
 	add_defender = SPA
 	add_defender = HAB
-	add_defender = SIL
 	add_defender = ENG
 }
 
@@ -60,7 +59,7 @@
 		location = 1272
 		attacker = {
 			commander = "Claude d'Annebault"	# Claude d'Annebault
-			heavy_ship = 80 
+			heavy_ship = 80
 			light_ship = 60
 			losses = 10	# percent
 			country = FRA
@@ -86,7 +85,6 @@
 	rem_attacker = TUN
 	rem_defender = SPA
 	rem_defender = HAB
-	rem_defender = SIL
 }
 
 # End of the war
```

### GreatNordicWar.txt

RIP SHA256: `4f793be54ef56313f9b1bf64f83d018ab737deed28d92564491149b94762d382`

Vanilla SHA256: `905bae3a7e0f9daa170c8cd02d7b7626cbc082eb2c7751dee1ee95eaf0ed9a56`

```diff
--- vanilla/GreatNordicWar.txt
+++ RIP/GreatNordicWar.txt
@@ -7,8 +7,6 @@
 
 1699.12.10 = {
 	add_attacker = DAN
-	add_attacker = RUS
-	add_attacker = ZAZ
 	add_attacker = PLC
 	add_attacker = KUR
 	add_attacker = SAX
@@ -18,6 +16,13 @@
 # Treaty of Travendal
 1700.8.18 = {
 	rem_attacker = DAN
+}
+
+# Russia, Left-Bank Hetmanate, and Zaporizhia enter after the Treaty of Constantinople
+1700.8.19 = {
+	add_attacker = RUS
+	add_attacker = HET
+	add_attacker = ZAZ
 }
 
 1700.11.20 = {
@@ -75,7 +80,7 @@
 			country = SAX
 		}
 		defender = {
-			commander = "Carl Gustaf Rehnskiöld"	# Carl Gustaf Rehnskiöld
+			commander = "Carl Gustaf Rehnskiold"	# Carl Gustaf Rehnskiold
 			infantry = 6500
 			cavalry = 4000
 			losses = 4	#percent
@@ -85,7 +90,6 @@
 	}
 }
 
-# Treaty of Altranstadt
 1706.9.24 = {
 	rem_attacker = SAX
 	rem_attacker = PLC
@@ -134,6 +138,14 @@
 		result = yes
 	}
 }
+# Ivan Mazepa and Kost Hordiyenko align with Sweden
+1708.11.1 = {
+	rem_attacker = HET
+	rem_attacker = ZAZ
+	add_defender = HET
+	add_defender = ZAZ
+}
+
 
 1709.6.28 = {
 	battle = {
@@ -158,13 +170,18 @@
 	}
 }
 
+# After Poltava, Skoropadsky's Left-Bank Hetmanate returns to Russian vassalage while ZAZ goes to Bender
+1709.7.9 = {
+	rem_defender = HET
+	add_attacker = HET
+}
+
 # Saxony and Poland reenter the war
 1709.8.8 = {
 	add_attacker = SAX
 	add_attacker = PLC
 }
 
-# Denmark reenters the war
 1709.10.28 = {
 	add_attacker = DAN
 }
@@ -174,13 +191,14 @@
 	add_defender = MOL
 }
 
+# Treaty of Pruth
 1711.7.21 = {
 	rem_defender = TUR
 	rem_defender = MOL
-}
-
-
-# Hannover and the Netherlands joins the attackers..
+	rem_defender = ZAZ
+}
+
+
 1712.4.1 = {
 	add_attacker = HAN
 	add_attacker = NED
@@ -246,7 +264,7 @@
 			country = DAN
 		}
 		defender = {
-			commander = "Olof Strömstierna"	#
+			commander = "Olof Stromstierna"	# Olof Stromstierna
 			galley = 8
 			light_ship = 4
 			losses = 7	#percent
@@ -290,6 +308,6 @@
 # Peace and end of war.
 1721.8.30 = {
 	rem_attacker = RUS
-	rem_attacker = ZAZ
+	rem_attacker = HET
 	rem_defender = SWE
 }
```

### KhmelnytskyUprising.txt

RIP SHA256: `07bbe36cb5bb67e0a51230752f0e4802b84e9344a9bd4bb58b87ff67e389e45e`

New RIP war file (`addition`).

### LivonianWar.txt

RIP SHA256: `e783a7097d408c9e6294b54e6a494def89f1c45be921dc2e34857796585b3c46`

Vanilla SHA256: `31c303f9051c8dc53e321e7c1765e0b7a867e20a47b1c4c6977bda5c24604368`

```diff
--- vanilla/LivonianWar.txt
+++ RIP/LivonianWar.txt
@@ -2,7 +2,7 @@
 war_goal = {
 	type = take_claim
 	casus_belli = cb_conquest
-	province = 1834 #Dorpat
+	province = 1834 # Dorpat
 }
 
 1558.1.22 = {
@@ -12,13 +12,17 @@
 	add_defender = LIV
 	add_defender = POL
 	add_defender = LIT
-	add_defender = TEU
-	add_defender = KUR
+	add_defender = PRU
 	add_defender = ZAZ
 }
 
 1561.1.1 = {
 	rem_defender = LIV
+}
+
+# Union of Vilnius creates Duchy of Courland under Polish protection
+1561.11.28 = {
+	add_defender = KUR
 }
 
 1569.7.1 = {
@@ -56,7 +60,7 @@
 # Peace of Jam Zapolski
 1582.1.15 = {
 	rem_defender = PLC
-	rem_defender = TEU
+	rem_defender = PRU
 	rem_defender = KUR
 	rem_defender = ZAZ
 }
```

### OttomanCommonwealthWar.txt

RIP SHA256: `d7e6a42ca12133c8920c4ee2342d9dc7935dcd9da82a12a74353149170458e0c`

Vanilla SHA256: `d796b142153462f79b0c55900587f25c5c858b374cc953efe53de16b5b5c465b`

```diff
--- vanilla/OttomanCommonwealthWar.txt
+++ RIP/OttomanCommonwealthWar.txt
@@ -2,23 +2,25 @@
 war_goal = {
 	type = take_border
 	casus_belli = cb_border_war
-	province = 1943
+	province = 2961 # Lwow
 }
 
-1672.8.1 = {
+# Ottoman declaration of war on the Commonwealth
+1672.6.4 = {
 	add_attacker = TUR
 	add_attacker = MOL
 	add_attacker = WAL
 	add_attacker = CRI
 	add_attacker = RAG
 	add_attacker = TRA
+	add_attacker = PDL
 	add_defender = PLC
 }
 
 1675.8.24 = {
 	battle = {
 		name = "Lwow"
-		location = 260
+		location = 2961
 		attacker = {
 			commander = "Ibrahim Shyshman"	# Ibrahim Shyshman
 			infantry = 8500
@@ -37,7 +39,13 @@
 	}
 }
 
-1676.1.1 = {
+# Capitulation of Petro Doroshenko at Chyhyryn
+1676.9.19 = {
+	rem_attacker = PDL
+}
+
+# Treaty of Zurawno
+1676.10.17 = {
 	rem_attacker = TUR
 	rem_attacker = MOL
 	rem_attacker = WAL
```

### PolishCossackTatarWar.txt

RIP SHA256: `50c3d4aacb9604a3dcdada23b9a1adae712d74bf03515cc72a025dddbb1fe729`

New RIP war file (`addition`).

### PolishHetmanateWar.txt

RIP SHA256: `e15da182a2b792eb106c2bbc48a00dfe5cfd2bcd554db2bf3c4190eb52203200`

New RIP war file (`addition`).

### PolishMuscoviteWar.txt

RIP SHA256: `4730b98b174c942fa34725f106b647241f973980fbd317e516a8ddf539e50387`

Vanilla SHA256: `2e4c075727f2cd84e3db74f29819a903d7b34f5d3c3fe64d3f13bdf139ab7dbd`

```diff
--- vanilla/PolishMuscoviteWar.txt
+++ RIP/PolishMuscoviteWar.txt
@@ -7,7 +7,7 @@
 
 1605.1.1 = {
 	add_attacker = PLC
-	add_attacker = TEU
+	add_attacker = PRU
 	add_attacker = KUR
 	add_attacker = ZAZ
 	add_defender = RUS
@@ -42,7 +42,7 @@
 		name = "Klushino"
 		location = 293
 		attacker = {
-			commander = "Fyodor Mstislavsky"	# Stanislaw Zolkiewski
+			commander = "Stanislaw Zolkiewski"	# Stanislaw Zolkiewski
 			infantry = 1000
 			cavalry = 6000
 			artillery = 30
@@ -83,10 +83,14 @@
 	}
 }
 
+# Prussia passes to Brandenburg personal union
+1618.8.28 = {
+	rem_attacker = PRU
+}
+
 # Treaty of Dywilino
 1618.12.11 = {
 	rem_attacker = PLC
-	rem_attacker = TEU
 	rem_attacker = KUR
 	rem_attacker = ZAZ
 	rem_defender = RUS
```

### PolishOttomanWar1620.txt

RIP SHA256: `f6428a4f6ffb56fb4aa0632edbf542ce84df2e135eb9c4a7d6dd2988acaffbda`

New RIP war file (`addition`).

### RussoTurkishWar.txt

RIP SHA256: `d801b0345d5cb86d211a3f5e7e6e68e32e250601d911974647eb2f55a77e8e4e`

Vanilla SHA256: `5862de4ce686048ca35d04b8bb831e4b3aacf1d8132b5a4e8f82fb8d88de9d96`

```diff
--- vanilla/RussoTurkishWar.txt
+++ RIP/RussoTurkishWar.txt
@@ -2,17 +2,53 @@
 war_goal = {
 	type = take_claim
 	casus_belli = cb_conquest
-	province = 466 # Sarai
+	province = 280 # Kiev
 }
 
-1676.1.1 = {
+# Escalation after Zurawno; Left-Bank Hetmanate and Zaporizhia defend against the Porte
+1676.11.1 = {
 	add_attacker = TUR
 	add_attacker = CRI
 	add_defender = RUS
+	add_defender = HET
+	add_defender = ZAZ
 }
 
+# Yuriy Khmelnytsky marches with the Ottoman Chyhyryn expedition
+1677.6.29 = {
+	add_attacker = PDL
+}
+
+1678.7.21 = {
+	battle = {
+		name = "Chyhyryn"
+		location = 1944
+		attacker = {
+			commander = "Kara Mustafa"	# Kara Mustafa
+			infantry = 70000
+			cavalry = 30000
+			artillery = 60
+			losses = 20	# percent
+			country = TUR
+		}
+		defender = {
+			commander = "Grigory Romodanovsky"	# Grigory Romodanovsky
+			infantry = 50000
+			cavalry = 20000
+			artillery = 40
+			losses = 15	# percent
+			country = RUS
+		}
+		result = yes
+	}
+}
+
+# Treaty of Bakhchisarai
 1681.1.3 = {
 	rem_attacker = TUR
 	rem_attacker = CRI
+	rem_attacker = PDL
 	rem_defender = RUS
+	rem_defender = HET
+	rem_defender = ZAZ
 }
```

### SecondMuscoviteLithuanianWar.txt

RIP SHA256: `f80b4991a779dfc3df10be83d5c3e3620ade3217df7f00e081fb24143774d392`

Vanilla SHA256: `ad7bf4ad317a585bb8c26bbd9ee0bde112419923cabc5e57394798ee8cf60392`

```diff
--- vanilla/SecondMuscoviteLithuanianWar.txt
+++ RIP/SecondMuscoviteLithuanianWar.txt
@@ -5,8 +5,10 @@
 	province = 293 # Smolensk
 }
 
+# Severian princes defect to Moscow against Lithuania
 1500.5.1 = {
 	add_attacker = MOS
+	add_attacker = CHR
 	add_defender = LIT
 	add_defender = POL
 }
@@ -33,9 +35,10 @@
 	}
 }
 
-# Truce
+# Truce of the Annunciation
 1503.3.21 = {
 	rem_attacker = MOS
+	rem_attacker = CHR
 	rem_defender = LIT
 	rem_defender = POL
 }
```

### SecondOttomanHungarianWar.txt.txt

RIP SHA256: `991e749ac363112e3ff1c2d46ae3deb83656ed35e3390bde1bbeb665895c22e1`

Vanilla SHA256: `ce4ceb74aecb29c2afdbacaba75cbeaed46db51da377da2bd0b00f1fdb3b1002`

```diff
--- vanilla/SecondOttomanHungarianWar.txt.txt
+++ RIP/SecondOttomanHungarianWar.txt.txt
@@ -2,7 +2,7 @@
 war_goal = {
 	type = take_claim
 	casus_belli = cb_conquest
-	province = 152 # Belovar
+	province = 153 # Pest / Buda
 }
 
 1521.5.18 = {
@@ -10,7 +10,7 @@
 	add_attacker = MOL
 	add_attacker = WAL
 	add_attacker = CRI
-	add_defender = HUN	
+	add_defender = HUN
 }
 
 1526.8.30 = {
```

### SecondRussuTurkishWar.txt

RIP SHA256: `d834ee8d2850d70e22b8d7cc49ec9e85eb2c04117c00a856a03d51e0925ca5f4`

Vanilla SHA256: `dd0935f2899686806b5d6cbcd064f273c96ba81bc232821fe5d34d3c01f9f9db`

```diff
--- vanilla/SecondRussuTurkishWar.txt
+++ RIP/SecondRussuTurkishWar.txt
@@ -2,11 +2,14 @@
 war_goal = {
 	type = take_claim
 	casus_belli = cb_conquest
-	province = 422 # Imereti
+	province = 286 # Azov
 }
 
+# Left-Bank Hetmanate and Zaporozhian Nova Sich fight alongside Russia
 1735.7.1 = {
 	add_attacker = RUS
+	add_attacker = HET
+	add_attacker = ZAZ
 	add_defender = TUR
 	add_defender = MOL
 	add_defender = CRI
@@ -16,12 +19,16 @@
 	add_attacker = HAB
 }
 
+# Treaty of Belgrade (Habsburgs)
 1739.9.18 = {
 	rem_attacker = HAB
 }
 
+# Treaty of Nis
 1739.10.3 = {
 	rem_attacker = RUS
+	rem_attacker = HET
+	rem_attacker = ZAZ
 	rem_defender = TUR
 	rem_defender = MOL
 	rem_defender = CRI
```

### SmolenskWar.txt

RIP SHA256: `702dff250e882094baff027464dfdfde7d280593096552b33dfbdc954bfc28f6`

Vanilla SHA256: `53a8118c2f6b7bdf778ddeaf8becb1f30c6c321dfbe863b2197c20bb258aaefd`

```diff
--- vanilla/SmolenskWar.txt
+++ RIP/SmolenskWar.txt
@@ -6,13 +6,16 @@
 	province = 293 # Smolensk
 }
 
+# Zaporozhian Cossacks serve alongside the Commonwealth relief army
 1632.6.1 = {
 	add_attacker = RUS
 	add_defender = PLC
+	add_defender = ZAZ
 }
 
-# Treaty of Polanów
+# Treaty of Polanow
 1634.6.14 = {
 	rem_attacker = RUS
 	rem_defender = PLC
+	rem_defender = ZAZ
 }
```

### TheDeluge.txt

RIP SHA256: `8064bec9201c853f2b99b10ef9fbd1347a6b23619db06d3ccd3be9d394e12789`

Vanilla SHA256: `32333285758654a15180912d51e556a1fefd6f2ebdb398efa8cbbaf64f0e9b5b`

```diff
--- vanilla/TheDeluge.txt
+++ RIP/TheDeluge.txt
@@ -6,9 +6,11 @@
 	province = 276 # Minsk
 }
 
-# Russo-Polish War
-1654.1.1 = {
+# Pereyaslav Agreement and Russo-Polish War
+1654.1.18 = {
 	add_attacker = RUS
+	add_attacker = HET
+	add_attacker = ZAZ
 	add_defender = PLC
 }
 
@@ -29,13 +31,75 @@
 	rem_defender = DAN
 }
 
+# Treaty of Hadiach (Vyhovsky's Hetmanate aligns with the Commonwealth; ZAZ stays opposed)
+1658.9.16 = {
+	rem_attacker = HET
+	add_defender = HET
+}
+
+1659.7.8 = {
+	battle = {
+		name = "Konotop"
+		location = 1945
+		attacker = {
+			commander = "Aleksey Trubetskoy"	# Aleksey Trubetskoy
+			infantry = 35000
+			cavalry = 15000
+			artillery = 40
+			losses = 60	# percent
+			country = RUS
+		}
+		defender = {
+			commander = "Ivan Vyhovsky"	# Ivan Vyhovsky
+			infantry = 16000
+			cavalry = 20000
+			artillery = 20
+			losses = 15	# percent
+			country = HET
+		}
+		result = no
+	}
+}
+
+# Second Pereyaslav Articles
+1659.10.27 = {
+	rem_defender = HET
+	add_attacker = HET
+}
+
 # Peace treaty of Oliwa
 1660.3.5 = {
 	rem_defender = BRA
 }
 
-1667.1.1 = {
+1660.10.14 = {
+	battle = {
+		name = "Chudnov"
+		location = 1942
+		attacker = {
+			commander = "Vasiliy Sheremetev"	# Vasiliy Sheremetev
+			infantry = 20000
+			cavalry = 15000
+			artillery = 30
+			losses = 75	# percent
+			country = RUS
+		}
+		defender = {
+			commander = "Jerzy Lubomirski"	# Jerzy Lubomirski
+			infantry = 14000
+			cavalry = 18000
+			artillery = 30
+			losses = 15	# percent
+			country = PLC
+		}
+		result = no
+	}
+}
+
+# Truce of Andrusovo
+1667.1.30 = {
 	rem_defender = PLC
 	rem_attacker = RUS
+	rem_attacker = HET
+	rem_attacker = ZAZ
 }
-
```

### ThirdMuscoviteLithuanianWar.txt

RIP SHA256: `b0d76e2aec45715cf0f15996a0be7d2a1e4df93969f0f57d1aa3b416e182f59f`

New RIP war file (`addition`).

### ThirdRussoTurkishWar.txt

RIP SHA256: `4c93e10301fdaf39b06ad76bac8fd08a5093dff438a7177afc9303b29670a84d`

Vanilla SHA256: `460f1ce736020ad1faef53a75510ff06864755d481ea5a3b80a0e076adab66e7`

```diff
--- vanilla/ThirdRussoTurkishWar.txt
+++ RIP/ThirdRussoTurkishWar.txt
@@ -12,12 +12,15 @@
 	add_attacker = MOL
 	add_attacker = RAG
 	add_defender = RUS
+	add_defender = ZAZ
 }
 
+# Treaty of Kucuk Kaynarca
 1774.7.21 = {
 	rem_attacker = TUR
 	rem_attacker = CRI
 	rem_attacker = MOL
 	rem_attacker = RAG
 	rem_defender = RUS
+	rem_defender = ZAZ
 }
```

### WarOfTheHolyLeague.txt

RIP SHA256: `99233d8c2be57b0f1c105737575197d8569b8b825b2a1426c3db051c2b7330fe`

Vanilla SHA256: `42ea37f978f9c6fb5388182db75bfd3fe0954cf71401463b4d87af5238cb9848`

```diff
--- vanilla/WarOfTheHolyLeague.txt
+++ RIP/WarOfTheHolyLeague.txt
@@ -12,6 +12,7 @@
 	add_attacker = TRA
 	add_attacker = WAL
 	add_attacker = MOL
+	add_attacker = PDL
 	add_defender = HAB
 	add_defender = PLC
 	add_defender = VEN
@@ -44,6 +45,8 @@
 # Russia joins the alliance
 1686.1.1 = {
 	add_defender = RUS
+	add_defender = HET
+	add_defender = ZAZ
 }
 
 1687.8.12 = {
@@ -75,7 +78,7 @@
 		name = "Slankamen" 
 		location = 141
 		attacker = { 
-			commander = "Mustafa Köprülü"		# Mustafa Köprülü
+			commander = "Mustafa Koprulu"		# Mustafa Koprulu
 			infantry = 26000
 			cavalry = 12000
 			losses = 25		# percent 
@@ -121,9 +124,9 @@
 	rem_defender = HAB
 	rem_defender = PLC
 	rem_defender = VEN
+	rem_attacker = PDL
 }
 
-#Treaty of of Constantinople
 
 1700.6.13 = {
 	rem_attacker = TUR
@@ -132,4 +135,6 @@
 	rem_attacker = WAL
 	rem_attacker = MOL
 	rem_defender = RUS
+	rem_defender = HET
+	rem_defender = ZAZ
 }
```

### WarOfThePolishSuccession.txt

RIP SHA256: `270aa7eb14d0ee6073c695c9cc43bd27944cfe0016f83a076af9936ac415b31b`

Vanilla SHA256: `203ea8f9710229bb3679820da29ebd0867ec227ca8f476b66d90301ee22bdba5`

```diff
--- vanilla/WarOfThePolishSuccession.txt
+++ RIP/WarOfThePolishSuccession.txt
@@ -15,7 +15,7 @@
 
 1733.10.10 = {
 	add_defender = FRA
-	add_defender = SAV
+	add_defender = SPI
 }
 
 1733.11.7 = {
@@ -25,7 +25,7 @@
 # Peace of Vienna
 1735.10.3 = {
 	rem_defender = FRA
-	rem_defender = SAV
+	rem_defender = SPI
 	rem_defender = SPA
 	rem_defender = PLC
 	rem_attacker = RUS
```

### WarOfTheSixthCoalition.txt

RIP SHA256: `be1d448940de319811f5cc6f7d53c98ce56e54639484d7e54463ed5152f716fd`

Vanilla SHA256: `70654047c059e82de5c910241d8473022053a84f1c732932f93fb13f422fb496`

```diff
--- vanilla/WarOfTheSixthCoalition.txt
+++ RIP/WarOfTheSixthCoalition.txt
@@ -14,7 +14,6 @@
 	add_attacker = BAV
 	add_attacker = SAX
 	add_attacker = BAD
-	add_attacker = HES
 	add_attacker = ANH
 	add_attacker = WUR
 	add_attacker = WBG
@@ -70,7 +69,7 @@
 		name = "Smolensk"
 		location = 293
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 175000
 			losses = 5	# percent
 			country = FRA
@@ -132,7 +131,7 @@
 		name = "Borodino"
 		location = 276
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 82500
 			cavalry = 27000
 			artillery = 590
@@ -196,7 +195,7 @@
 		name = "Maloyaroslavets"
 		location = 296
 		attacker = {
-			commander = "Eugène de Beauharnais"	# Eugène de Beauharnais
+			commander = "Eugene de Beauharnais"	# Eugene de Beauharnais
 			infantry = 20000
 			losses = 25	# percent
 			country = FRA
@@ -278,7 +277,7 @@
 		name = "Krasnoi"
 		location = 293
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 81000
 			losses = 12	# percent
 			country = FRA
@@ -298,7 +297,7 @@
 		name = "Berezina"
 		location = 276
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 75000
 			losses = 47	# percent
 			country = FRA
@@ -313,7 +312,7 @@
 	}
 }
 
-# Treaty of Örebro, Sweden joins the sixth coalition
+# Treaty of Orebro, Sweden joins the sixth coalition
 1813.3.3 = {
 	add_defender = SWE
 }
@@ -327,13 +326,13 @@
 		name = "Bautzen"
 		location = 61
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 115000
 			losses = 17	# percent
 			country = FRA
 		}
 		defender = {
-			commander = "Gebhard von Blücher"	# Gebhard von Blücher
+			commander = "Gebhard von Blucher"	# Gebhard von Blucher
 			infantry = 96000
 			losses = 21	# percent
 			country = PRU
@@ -351,13 +350,13 @@
 		name = "Katzbach"
 		location = 264
 		attacker = {
-			commander = "Étienne MacDonald"	# Étienne MacDonald
+			commander = "Etienne MacDonald"	# Etienne MacDonald
 			infantry = 102000
 			losses = 15	# percent
 			country = FRA
 		}
 		defender = {
-			commander = "Gebhard von Blücher"	# Gebhard von Blücher
+			commander = "Gebhard von Blucher"	# Gebhard von Blucher
 			infantry = 114000
 			losses = 4	# percent
 			country = PRU
@@ -371,7 +370,7 @@
 		name = "Dresden"
 		location = 61
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 135000
 			losses = 7	# percent
 			country = FRA
@@ -397,7 +396,7 @@
 			country = FRA
 		}
 		defender = {
-			commander = "Gebhard von Blücher"	# Gebhard von Blücher
+			commander = "Gebhard von Blucher"	# Gebhard von Blucher
 			infantry = 54000
 			losses = 20	# percent
 			country = PRU
@@ -421,7 +420,7 @@
 		name = "Leipzig"
 		location = 62
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 191000
 			losses = 20	# percent
 			country = FRA
@@ -444,12 +443,10 @@
 	add_defender = ANH
 }
 
-# Baden and Hesse switch side
+# Baden switches side (Hesse was dissolved into Westphalia)
 1813.10.20 = {
 	rem_attacker = BAD
 	add_defender = BAD
-	rem_attacker = HES
-	add_defender = HES
 }
 
 # Wurzburg switches side
@@ -463,7 +460,7 @@
 		name = "Hanau"
 		location = 81
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 17000
 			losses = 26	# percent
 			country = FRA
@@ -478,7 +475,7 @@
 	}
 }
 
-# Württemberg switches side
+# Wurttemberg switches side
 1813.11.2 = {
 	rem_attacker = WUR
 	add_defender = WUR
@@ -496,16 +493,16 @@
 
 1814.2.1 = {
 	battle = {
-		name = "La Rothière"
+		name = "La Rothiere"
 		location = 187
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 40000
 			losses = 15	# percent
 			country = FRA
 		}
 		defender = {
-			commander = "Gebhard von Blücher"	# Gebhard von Blücher
+			commander = "Gebhard von Blucher"	# Gebhard von Blucher
 			infantry = 110000
 			losses = 5	# percent
 			country = PRU
@@ -519,7 +516,7 @@
 		name = "Arcis-sur-Aube"
 		location = 186
 		attacker = {
-			commander = "Napoléon Bonaparte"	# Napoléon Bonaparte
+			commander = "Napoleon Bonaparte"	# Napoleon Bonaparte
 			infantry = 25000
 			losses = 12	# percent
 			country = FRA
@@ -564,7 +561,6 @@
 	rem_defender = SWE
 	rem_defender = RUS
 	rem_defender = HAB
-	rem_defender = HES
 	rem_defender = WUR
 	rem_defender = BAD
 	rem_defender = PRU
```

