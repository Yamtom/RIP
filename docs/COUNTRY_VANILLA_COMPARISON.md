# Country history comparison

Installed baseline: **EU4 v1.37.5.0 Inca (491d)**

Path: `D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV`

Counts: {'addition': 22, 'override': 7, 'identical': 3}

Only the 32 RIP country histories are reviewed; inherited vanilla countries are not a global historical audit.
Definition checks establish identifier presence, not reform eligibility or runtime behavior. Province labels are file names, not geographic proof.

| Tag | Comparison | Capital (effective province file) | Government / reform | Distinct dated blocks |
|---|---|---|---|---|
| BLR | addition | 276: Minsk | monarchy / principality | 1 |
| CHR | override | 289: Chernigov | republic / siversk_veche_reform | 4 |
| HET | addition | 290: Poltava | republic / rip_cossacks_reform | 67 |
| HLC | addition | 2961: Lwow | monarchy / hlc_galician_voivodeship_reform | 1 |
| IZM | addition | 2408: Lipetsk | republic / rip_cossacks_reform | 1 |
| KHK | addition | 291: Kharkov | republic / rip_cossacks_reform | 1 |
| KIE | override | 280: Kiev | monarchy / ruthenian_principality_reform | 5 |
| KRU | addition | 280: Kiev | monarchy / kyivan_rus_reform | 0 |
| KUY | addition | 280: Kiev | monarchy / ruthenian_tsardom | 1 |
| MSK | addition | 276: Minsk | monarchy / principality | 1 |
| MSL | addition | 4246: Mstislav | monarchy / principality | 1 |
| NOV | override | 310: Novgorod | republic / veche_republic | 6 |
| ODS | addition | 282: Yedisan | republic / odesa_trade_republic_reform | 0 |
| OKA | override | 4116: Upper Oka | monarchy / principality | 3 |
| OKH | addition | 298: Kursk | republic / rip_cossacks_reform | 1 |
| PDL | addition | 281: Kamienec | monarchy / pdl_frontier_voivodeship_reform | 9 |
| PLT | identical | 275: Polotsk | monarchy / principality | 0 |
| PRL | addition | 2407: Pereyaslav | monarchy / prl_ancient_principality_reform | 0 |
| RPS | addition | 278: Pinsk | monarchy / principality | 1 |
| RUT | addition | 280: Kiev | monarchy / ruthenian_tsardom | 0 |
| RYA | identical | 301: Ryazan | monarchy / principality | 4 |
| SMO | override | 293: Smolensk | monarchy / principality | 1 |
| SMY | addition | 299: Voronezh | republic / rip_cossacks_reform | 1 |
| SRK | addition | 456: Turkestan | monarchy / feudalism_reform | 0 |
| TRV | addition | 1941: Turov | monarchy / principality | 1 |
| UKR | identical | 280: Kiev | monarchy / feudalism_reform | 0 |
| UZH | addition | 1952: Maramaros | monarchy / uzh_palanok_captaincy_reform | 1 |
| VLN | addition | 279: Volhynia | monarchy / vln_voivodeship_reform | 0 |
| VOL | override | 279: Volhynia | monarchy / feudalism_reform | 1 |
| VTB | addition | 771: Vitebsk | monarchy / principality | 1 |
| ZAZ | override | 283: Zaporozhia | republic / rip_cossacks_reform | 66 |
| ZLK | addition | 2107: Ningguta | monarchy / feudalism_reform | 0 |

## Review findings

- ZAZ: 1639.1.1: 2 competing monarch records

## Complete override diffs

### BLR - Belarus.txt

RIP SHA256: `c86161a0b1e35979dd35c4fd58562efb25c9b1be553a1a9f23942e32c8f5c37f`

No vanilla counterpart; historical validation needs external sources.

### CHR - Chernigov.txt

RIP SHA256: `ee0965ea1c8119e31d7c203e6c02f1627710211386429502835861c77a1952d3`

Vanilla SHA256: `24c7846bef0694146f3e04a3e9f46fabb68933c0f5b6c2813090c978627e0cec`

```diff
--- vanilla/CHR - Chernigov.txt
+++ RIP/CHR - Chernigov.txt
@@ -1,8 +1,66 @@
-government = monarchy
-add_government_reform = principality
-government_rank = 1
-technology_group = eastern
-religion = orthodox
-primary_culture = ryazanian
-capital = 289	# Chernigov
-fixed_capital = 289 # Cannot move capital away from this province & no power cost to move to it+government = republic
+add_government_reform = siversk_veche_reform
+government_rank = 1
+technology_group = eastern
+religion = orthodox
+primary_culture = ruthenian
+capital = 289	# Chernihiv
+fixed_capital = 289	# Chernihiv
+historical_friend = GOL
+historical_friend = MOL
+
+1444.1.1 = {	
+	monarch = {		
+		name = "Semyon"
+		dynasty = Mozhaisky
+		culture = ruthenian
+		adm = 3		
+		dip = 6		
+		mil = 6	
+	}
+	leader = {
+		name = "Semyon Mozhaisky"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 3
+		siege = 1
+		death_date = 1505.1.1
+	}
+}
+
+1480.1.1 = {
+	leader = {
+		name = "Ivan Shemyachich"
+		type = general
+		fire = 3
+		shock = 3
+		manuever = 3
+		siege = 1
+		death_date = 1508.1.1
+	}
+}
+
+1500.1.1 = {
+	leader = {
+		name = "Vasyl Shemyachich"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 3
+		siege = 2
+		death_date = 1529.1.1
+	}
+}
+
+1505.1.1 = {
+	leader = {
+		name = "Mykhailo Glinsky"
+		type = general
+		fire = 3
+		shock = 4
+		manuever = 4
+		siege = 2
+		death_date = 1534.9.1
+	}
+}
```

### HET - Hetmanate.txt

RIP SHA256: `7d3bb7b77acf08503a77c2f7abc2a18eef0a8cc3c1fdf5edcb3154c809b92d78`

No vanilla counterpart; historical validation needs external sources.

### HLC - Halich.txt

RIP SHA256: `9016dd32c93664d92839a4fe18113b59689054138108f42cb8080b2c06f27d5c`

No vanilla counterpart; historical validation needs external sources.

### IZM - Izium Regiment.txt

RIP SHA256: `f4e3f9fedfe9f82ac3601069e9a613a82e9330114579615cd22041c7ebf7fa01`

No vanilla counterpart; historical validation needs external sources.

### KHK - Kharkov Host.txt

RIP SHA256: `4c639a77cc0007eb4098b9c57b954442045c188d315f6b11dfd68f1fd8730c33`

No vanilla counterpart; historical validation needs external sources.

### KIE - Kiev.txt

RIP SHA256: `f082849ac2331993db569e5827f0ea487e632ceefdc0e5545e7368eb6b2bc48b`

Vanilla SHA256: `4a82835d99110572464106a0209d0e705783e3f35d62b186a3d1635db37729c5`

```diff
--- vanilla/KIE - Kiev.txt
+++ RIP/KIE - Kiev.txt
@@ -1,8 +1,51 @@
-government = monarchy
-add_government_reform = principality
-government_rank = 1
-technology_group = eastern
-religion = orthodox
-primary_culture = ruthenian
-capital = 280	# Kiev
-fixed_capital = 280 # Cannot move capital away from this province & no power cost to move to it+government = monarchy
+add_government_reform = ruthenian_principality_reform 
+government_rank = 2
+technology_group = eastern
+religion = orthodox
+primary_culture = ruthenian
+historical_friend = LIT	# the Olelkovichi held Kyiv under Vilnius
+historical_friend = NOV
+capital = 280	# Kyiv
+fixed_capital = 280 # Cannot move capital away from this province & no power cost to move to it
+
+1442.1.1 = {
+	monarch = {
+		name = "Olel'ko"
+		dynasty = Gedyminovich
+		birth_date = 1380.1.1
+		death_date = 1454.12.31
+		adm = 3
+		dip = 6
+		mil = 2
+	}
+
+}
+
+1442.1.1 = {
+	heir = {
+		name = "Semen"
+		dynasty = Gedyminovich
+		birth_date = 1418.1.1
+		death_date = 1470.12.31
+		claim = 95
+		adm = 3
+		dip = 3
+		mil = 2
+	}
+
+}
+
+
+# Marks the Kyivan lineage for events/KyivSuccessionHistory.txt and the two
+# decisions it gates (decisions/KyivTriggers.txt: kyiv_shogunate_path,
+# kyiv_cesarstvo_path). The flag survives change_tag, so a KIE that later
+# becomes UKR through decisions/RuthenianNation.txt keeps the eligibility a
+# UKR formed from HLC/VLN/PDL never had.
+1444.1.1 = { set_country_flag = rip_kyivan_lineage_flag }
+
+1497.9.12 = { leader = { name = "Kostyantyn Ostrozs'kiy"	type = general	fire = 3	shock = 4	manuever = 3	siege = 1	death_date = 1530.8.10 } }
+
+1536.1.1 = { leader = {	name = "Andriy Nemyrovych"     	type = general	fire = 1	shock = 2	manuever = 3	siege = 0	death_date = 1541.1.1 } }
+
+1553.1.1 = { leader = {	name = "Mykola Radzyvil"        	type = general	fire = 2	shock = 4	manuever = 3	siege = 0	death_date = 1616.2.28 } }
```

### KRU - Rus.txt

RIP SHA256: `f84ce08aa9067c0f8dc5124f77a206fc49862004b77d5d7a19defbf065af0168`

No vanilla counterpart; historical validation needs external sources.

### KUY - Kuyaba.txt

RIP SHA256: `39c7205cd11db2be11d38eb07423635edac7eee6947605f98d2d6519b4c35c5f`

No vanilla counterpart; historical validation needs external sources.

### MSK - Minsk.txt

RIP SHA256: `d10081c5123c0e83fe02703a9fd5f78eba34a43a39eca2788de47696a9f2e00e`

No vanilla counterpart; historical validation needs external sources.

### MSL - Mstislavl.txt

RIP SHA256: `5a7017826cfb7783c55467759f474940378a986eb5110f10b5e7de45f2637dc7`

No vanilla counterpart; historical validation needs external sources.

### NOV - Novgorod.txt

RIP SHA256: `813e49674bdd1dda393da364420cb30b78d3734d65147bd605636f78c574dfa8`

Vanilla SHA256: `9abb05e903add7f1d4182de0549780abfa11f2218de2cf69e359180396b42e5b`

```diff
--- vanilla/NOV - Novgorod.txt
+++ RIP/NOV - Novgorod.txt
@@ -10,12 +10,25 @@
 fixed_capital = 310 # Cannot move capital away from this province & no power cost to move to it
 
 add_accepted_culture = karelian
+
 1429.1.1 = {
 	monarch = {
 		name = "Evfimy II"
 		adm = 3
 		dip = 4
 		mil = 2
+	}
+}
+
+1444.1.1 = {
+	leader = {
+		name = "Dmitry Shemyaka"
+		type = general
+		fire = 2
+		shock = 3
+		manuever = 3
+		siege = 1
+		death_date = 1453.7.17
 	}
 }
 
@@ -32,6 +45,27 @@
 	}
 }
 
+1470.1.1 = {
+	leader = {
+		name = "Dmitry Boretsky"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 3
+		siege = 1
+		death_date = 1471.7.24
+	}
+	leader = {
+		name = "Vasily Kazimir"
+		type = general
+		fire = 2
+		shock = 3
+		manuever = 3
+		siege = 0
+		death_date = 1480.1.1
+	}
+}
+
 1470.11.1 = {
 	monarch = {
 		name = "Feofil"
```

### ODS - Odessa.txt

RIP SHA256: `833f3c9f988d7f2103083b324791c1e68992ec48e30ae7a3b7258ff63a189828`

No vanilla counterpart; historical validation needs external sources.

### OKA - Oka.txt

RIP SHA256: `0b46b60a167f9dc16dcd408270662d2de695345912c244ded86eeea8a2641611`

Vanilla SHA256: `3f7a0e4e2626ee8fb540506208b9f20d753298be160865e389b392a3057df888`

```diff
--- vanilla/OKA - Oka.txt
+++ RIP/OKA - Oka.txt
@@ -1,81 +1,80 @@
-#Represents the various small Upper Oka Principalities
-government_rank = 1
-government = monarchy
-add_government_reform = principality
-primary_culture = ryazanian
-religion = orthodox
-technology_group = eastern
-capital = 4116	# Upper Oka
-fixed_capital = 4116 # Cannot move capital away from this province & no power cost to move to it
-
-1427.1.1 = {
-	monarch = {
-		name = "Ivan"
-		dynasty = "Rurikovich"
-		adm = 2
-		dip = 3
-		mil = 2
-	}
-}
-
-1427.1.1 = {
-	heir = {
-		name = "Semen"
-		monarch_name = "Semen"
-		dynasty = "Rurikovich"
-		birth_date = 1427.1.1
-		death_date = 1473.1.1
-		claim = 95
-		adm = 1
-		dip = 1
-		mil = 2
-	}
-}
-
-1459.1.1 = {
-	monarch = {
-		name = "Semen"
-		dynasty = "Rurikovich"
-		adm = 1
-		dip = 1
-		mil = 2
-	}
-}
-
-1459.1.1 = {
-	heir = {
-		name = "Ivan"
-		monarch_name = "Ivan"
-		dynasty = "Rurikovich"
-		birth_date = 1459.1.1
-		death_date = 1508.1.1
-		claim = 95
-		adm = 2
-		dip = 1
-		mil = 2
-	}
-}
-
-1470.1.1 = {
-	monarch = {
-		name = "Ivan"
-		dynasty = "Rurikovich"
-		adm = 2
-		dip = 1
-		mil = 2
-	}
-}
-
-1470.1.1 = {
-	heir = {
-		name = "Roman"
-		monarch_name = "Roman"
-		dynasty = "Rurikovich"
-		birth_date = 1470.1.1
-		death_date = 1550.1.1
-		claim = 95
-		adm = 2
-		dip = 2
-		mil = 2
-	}
-}+government_rank = 1
+government = monarchy
+add_government_reform = principality
+primary_culture = ruthenian
+religion = orthodox
+technology_group = eastern
+capital = 4116	# Upper Oka
+fixed_capital = 4116 # Cannot move capital away from this province & no power cost to move to it
+
+1427.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = "Rurikovich"
+		adm = 2
+		dip = 3
+		mil = 2
+	}
+}
+
+1427.1.1 = {
+	heir = {
+		name = "Semen"
+		monarch_name = "Semen"
+		dynasty = "Rurikovich"
+		birth_date = 1427.1.1
+		death_date = 1473.1.1
+		claim = 95
+		adm = 1
+		dip = 1
+		mil = 2
+	}
+}
+
+1459.1.1 = {
+	monarch = {
+		name = "Semen"
+		dynasty = "Rurikovich"
+		adm = 1
+		dip = 1
+		mil = 2
+	}
+}
+
+1459.1.1 = {
+	heir = {
+		name = "Ivan"
+		monarch_name = "Ivan"
+		dynasty = "Rurikovich"
+		birth_date = 1459.1.1
+		death_date = 1508.1.1
+		claim = 95
+		adm = 2
+		dip = 1
+		mil = 2
+	}
+}
+
+1470.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = "Rurikovich"
+		adm = 2
+		dip = 1
+		mil = 2
+	}
+}
+
+1470.1.1 = {
+	heir = {
+		name = "Roman"
+		monarch_name = "Roman"
+		dynasty = "Rurikovich"
+		birth_date = 1470.1.1
+		death_date = 1550.1.1
+		claim = 95
+		adm = 2
+		dip = 2
+		mil = 2
+	}
+}
```

### OKH - Okhtyrka Regiment.txt

RIP SHA256: `fbe3beedae358483b37f027857fb6f6bd8cce84e7c50cc03458669363a19b947`

No vanilla counterpart; historical validation needs external sources.

### PDL - Podillia.txt

RIP SHA256: `0849d2ccdddfe95a887fa0dadc3a2b187b110947961c94691047d270e5ca72b7`

No vanilla counterpart; historical validation needs external sources.

### PLT - Polotsk.txt

RIP SHA256: `caab1f96990da5b3c9c29b9d77b1450c41c3a8036462e941e9aa577ca536b115`

Vanilla SHA256: `5049804eeac11379f72f1e8f2a43c29477a314f428d76bfdbe7aeb6b5b6c3ede`

```diff
--- vanilla/PLT - Polotsk.txt
+++ RIP/PLT - Polotsk.txt
@@ -1,8 +1,14 @@
+# RIP Polotsk: vanilla 1.37.5 fallback for a released/restored principality.
+# This does not assert an independent Polotsk ruler in 1444.
+# decisions/PolesianBelarusianNations.txt handles the formation path and rank.
+# Sophian autonomy is a conditional gameplay reform, not a default historical
+# entitlement; preserve principality until its own eligibility rules are met.
+# No invented dynasty or backdated religious privileges are assigned here.
 government = monarchy
 add_government_reform = principality
 government_rank = 1
 primary_culture = byelorussian
 religion = orthodox
 technology_group = eastern
-capital = 275	# Polotsk
-fixed_capital = 275 # Cannot move capital away from this province & no power cost to move to it+capital = 275 # Polotsk
+fixed_capital = 275
```

### PRL - Pereiaslav.txt

RIP SHA256: `fc90408d13edc799f1611950214197d6bf5808fa6ffc6f104946fb3f7bcb00b0`

No vanilla counterpart; historical validation needs external sources.

### RPS - Polishchuks.txt

RIP SHA256: `e0ed4904b97170868157ff6eb1e10c2547204d3c26a2a4dd7fb72c306056dfd3`

No vanilla counterpart; historical validation needs external sources.

### RUT - Ruthenian Tsardom.txt

RIP SHA256: `e311396c75fb6dd116bf711d4c1a5c3db95549148a65bb4f09f9a02c3f6dc229`

No vanilla counterpart; historical validation needs external sources.

### RYA - Ryazan.txt

RIP SHA256: `c0c8273487dfce1f988aa94d074d51cf6d914b8f6ae1875b5f90bd4d8696532e`

Vanilla SHA256: `9261155f2191a723f4935e1761da47465360866f4d0aeab77dbf06e428cf58b9`

```diff
--- vanilla/RYA - Ryazan.txt
+++ RIP/RYA - Ryazan.txt
@@ -1,75 +1,75 @@
-government = monarchy
-add_government_reform = principality
-government_rank = 1
-primary_culture = ryazanian
-religion = orthodox
-technology_group = eastern
-capital = 301	# Ryazan
-fixed_capital = 301 # Cannot move capital away from this province & no power cost to move to it
-
-1372.1.1 = {
-	monarch = {
-		name = "Oleg Ivanovich"
-		dynasty = "Rurikovich"
-		adm = 1
-		dip = 3
-		mil = 1
-	}
-}
-
-1372.1.1 = {
-	heir = {
-		name = "Fyodor Olegovich"
-		monarch_name = "Fyodor Olegovich"
-		dynasty = "Rurikovich"
-		birth_date = 1372.1.1
-		death_date = 1427.1.1
-		claim = 95
-		adm = 2
-		dip = 3
-		mil = 2
-	}
-}
-
-1402.1.1 = {
-	monarch = {
-		name = "Fyodor Olegovich"
-		dynasty = "Rurikovich"
-		birth_date = 1372.1.1
-		adm = 2
-		dip = 3
-		mil = 2
-	}
-}
-
-1402.1.1 = {
-	heir = {
-		name = "Ivan Fyodorovich"
-		monarch_name = "Ivan Fyodorovich"
-		dynasty = "Rurikovich"
-		birth_date = 1402.1.1
-		death_date = 1456.1.1
-		claim = 95
-		adm = 3
-		dip = 3
-		mil = 1
-	}
-}
-
-1427.1.1 = {
-	monarch = {
-		name = "Ivan Fyodorovich"
-		dynasty = "Rurikovich"
-		birth_date = 1402.1.1
-		adm = 3
-		dip = 3
-		mil = 1
-	}
-	clear_scripted_personalities = yes
-	add_ruler_personality = zealot_personality
-	add_ruler_personality = craven_personality
-}
-
-1454.1.1 = {
-	government_rank = 1
-}
+government = monarchy
+add_government_reform = principality
+government_rank = 1
+primary_culture = ryazanian
+religion = orthodox
+technology_group = eastern
+capital = 301	# Ryazan
+fixed_capital = 301 # Cannot move capital away from this province & no power cost to move to it
+
+1372.1.1 = {
+	monarch = {
+		name = "Oleg Ivanovich"
+		dynasty = "Rurikovich"
+		adm = 1
+		dip = 3
+		mil = 1
+	}
+}
+
+1372.1.1 = {
+	heir = {
+		name = "Fyodor Olegovich"
+		monarch_name = "Fyodor Olegovich"
+		dynasty = "Rurikovich"
+		birth_date = 1372.1.1
+		death_date = 1427.1.1
+		claim = 95
+		adm = 2
+		dip = 3
+		mil = 2
+	}
+}
+
+1402.1.1 = {
+	monarch = {
+		name = "Fyodor Olegovich"
+		dynasty = "Rurikovich"
+		birth_date = 1372.1.1
+		adm = 2
+		dip = 3
+		mil = 2
+	}
+}
+
+1402.1.1 = {
+	heir = {
+		name = "Ivan Fyodorovich"
+		monarch_name = "Ivan Fyodorovich"
+		dynasty = "Rurikovich"
+		birth_date = 1402.1.1
+		death_date = 1456.1.1
+		claim = 95
+		adm = 3
+		dip = 3
+		mil = 1
+	}
+}
+
+1427.1.1 = {
+	monarch = {
+		name = "Ivan Fyodorovich"
+		dynasty = "Rurikovich"
+		birth_date = 1402.1.1
+		adm = 3
+		dip = 3
+		mil = 1
+	}
+	clear_scripted_personalities = yes
+	add_ruler_personality = zealot_personality
+	add_ruler_personality = craven_personality
+}
+
+1454.1.1 = {
+	government_rank = 1
+}
```

### SMO - Smolensk.txt

RIP SHA256: `406aa2437b23ea0b7e6f6a178162d0f751b3744256063dc4544111865b713f94`

Vanilla SHA256: `16199b9a6df19d70b0aa490d7a77dc8731b79ec8a51f14f96473cd62957ea1fc`

```diff
--- vanilla/SMO - Smolensk.txt
+++ RIP/SMO - Smolensk.txt
@@ -1,18 +1,18 @@
-government = monarchy
-add_government_reform = principality
-government_rank = 1
-primary_culture = ryazanian
-religion = orthodox
-technology_group = eastern
-capital = 293	# Smolensk
-fixed_capital = 293 # Cannot move capital away from this province & no power cost to move to it
-
-1386.1.1 = {
-	monarch = {
-		name = "Yury I"
-		dynasty = "Rostaslavichi"
-		adm = 0
-		dip = 0
-		mil = 3
-	}
-}
+government = monarchy
+add_government_reform = principality
+government_rank = 1
+primary_culture = byelorussian
+religion = orthodox
+technology_group = eastern
+capital = 293	# Smolensk
+fixed_capital = 293 # Cannot move capital away from this province & no power cost to move to it
+
+1386.1.1 = {
+	monarch = {
+		name = "Yury I"
+		dynasty = "Rostaslavichi"
+		adm = 0
+		dip = 0
+		mil = 3
+	}
+}
```

### SMY - Sumy Regiment.txt

RIP SHA256: `1184064b9233dc6a30c75ec47253e2157334ecdadb990cfb9f59ee77c4e11238`

No vanilla counterpart; historical validation needs external sources.

### SRK - Siryi Klyn.txt

RIP SHA256: `c30797d40a5104cb845d4afac567809d5301043f1c0b28c865517591d3ac0250`

No vanilla counterpart; historical validation needs external sources.

### TRV - Turov.txt

RIP SHA256: `97663a8abb93516224ecef4f14983356df44c288c2485cd5caed99de70e5036d`

No vanilla counterpart; historical validation needs external sources.

### UKR - Ukraine.txt

RIP SHA256: `f5215448051f92377960f8e48b13e5fe07e4bef6f9c0226998e53913dedcf11e`

Vanilla SHA256: `210c3f27a932cbf80a21ca02e9e147822c90ff0e801f0a65fe95e638f84d09ee`

```diff
--- vanilla/UKR - Ukraine.txt
+++ RIP/UKR - Ukraine.txt
@@ -1,6 +1,12 @@
+# RIP Ruthenia/Ukraine: vanilla 1.37.5 fallback for the formable tag.
+# This is an alternative state-building outcome, not a claim that a united
+# independent state with this government existed in Kyiv in 1444.
+# decisions/RuthenianNation.txt controls formation, rank and conditional reforms.
+# Keep the Kyivan lineage flag exclusive to its KIE origin; do not grant it here.
+# No invented monarch or fixed capital: preserve the vanilla fallback settings.
 government = monarchy
 add_government_reform = feudalism_reform
 technology_group = eastern
 religion = orthodox
 primary_culture = ruthenian
-capital = 280	# Kiev
+capital = 280 # Kyiv
```

### UZH - Huszt.txt

RIP SHA256: `63fe4209330ccb525c7275edef79ca1447a625dc473bd9d1cd8f73f1cf41d0b3`

No vanilla counterpart; historical validation needs external sources.

### VLN - Voln.txt

RIP SHA256: `9cc70a69576bdf5fc798392a3304989ba90d4f201a45b77a148e2a03a6242203`

No vanilla counterpart; historical validation needs external sources.

### VOL - Volyn.txt

RIP SHA256: `ace99ae99346f3506fa73ca12cd4ff88532bd83fb1ca184ad35aa629d2eeba65`

Vanilla SHA256: `207887a26f78135485bcc8e77ed9be57510a251ee541cd2d42cd77572f9e1532`

```diff
--- vanilla/VOL - Volyn.txt
+++ RIP/VOL - Volyn.txt
@@ -1,6 +1,21 @@
-government = monarchy
-add_government_reform = feudalism_reform
-technology_group = eastern
-religion = catholic
-primary_culture = ruthenian
-capital = 279	# Volhynia
+government = monarchy
+add_government_reform = feudalism_reform
+government_rank = 2
+technology_group = eastern
+religion = orthodox
+primary_culture = ruthenian
+historical_friend = LIT
+historical_friend = POL
+capital = 279	# Volhynia
+
+1440.1.1 = {
+	monarch = {
+		name = "Lew"
+		dynasty = Gedyminovich
+		birth_date = 1433.1.1
+		death_date = 1495.10.2
+		adm = 3
+		dip = 4
+		mil = 2
+	}
+}
```

### VTB - Vitebsk.txt

RIP SHA256: `e80b0aa1b4c292e1e5f1543dc2f4507bd49eb82214793a4b16f8326819113fee`

No vanilla counterpart; historical validation needs external sources.

### ZAZ - Zaporozhie.txt

RIP SHA256: `af474b6376691dc1eea62d7e4dd93768c46fa2f0d6c36aa8d23705f61946cf31`

Vanilla SHA256: `644700595c8d47147fa281817a9ee081a907b474f61612fb190a58c5baa2d33b`

```diff
--- vanilla/ZAZ - Zaporozhie.txt
+++ RIP/ZAZ - Zaporozhie.txt
@@ -1,483 +1,780 @@
-government = republic
-add_government_reform = cossacks_reform
-technology_group = eastern
-religion = orthodox
-primary_culture = ruthenian
-capital = 283	# Zaporozhia
-
-
-1506.1.1 = {	
-	monarch = {		
-		name = "Lyantskoronsky"			
-		adm = 3		
-		dip = 4		
-		mil = 4	
-	}
-}
-
-1534.1.1 = {	
-	monarch = {		
-		name = "Kishka"				
-		adm = 3		
-		dip = 4		
-		mil = 4	
-	}
-}
-
-1550.1.1 = {
-	monarch = {		
-		name = "Vishnevetsky-Bayda"		
-		adm = 3		
-		dip = 3		
-		mil = 3  
-	}
-}
-
-1555.1.1 = {
-	government_rank = 1
-}
-
-1563.1.1 = {	
-	monarch = {		
-		name = "M. Vishnevetsky"	
-		adm = 2		
-		dip = 2		
-		mil = 2 
-	}
-}
-
-1573.1.1 = {	
-	monarch = {		
-		name = "Ivan Svirgovsky"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1575.1.1 = {	
-	monarch = {		
-		name = "Bogdan Ruzhinsky"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1576.1.1 = {	
-	monarch = {		
-		name = "Ivan II Pidkova"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1577.1.1 = {	
-	monarch = {		
-		name = "Yakiv I Shakh"			
-		adm = 1		
-		dip = 1		
-		mil = 1
-	}
-}
-
-1578.1.1 = {	
-	monarch = {		
-		name = "Lukyan Chornynsky"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1580.1.1 = {	
-	monarch = {		
-		name = "Samiylo II"			
-		adm = 1		
-		dip = 1		
-		mil = 1
-	}
-}
-
-1585.1.1 = {	
-	monarch = {		
-		name = "Zakhar Kulaga"			
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1586.1.1 = {	
-	monarch = {		
-		name = "Lukyan Chornsky"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1588.1.1 = {	
-	monarch = {		
-		name = "Semen I Skalozub"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1589.1.1 = {	
-	monarch = {		
-		name = "V Chanovytsky"			
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1590.1.1 = {	
-	monarch = {		
-		name = "K. Kosynsky"			
-		adm = 1		
-		dip = 1		
-		mil = 1
-	}
-}
-
-1593.1.1 = {	
-	monarch = {		
-		name = "G. Loboda"			
-		adm = 2		
-		dip = 2		
-		mil = 1
-	}
-}
-
-1596.2.2 = {	
-	monarch = {		
-		name = "Shaula, Krempsky & Nech"
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1596.11.3 = {	
-	monarch = {		
-		name = "Gnat Vassylevsky"		
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1598.1.1 = {	
-	monarch = {		
-		name = "Baybuza & Polous"		
-		adm = 1		
-		dip = 1		
-		mil = 1 
-	}
-}
-
-1600.1.1 = {	
-	monarch = {		
-		name = "Gavrylo Kortnevych"		
-		adm = 1		
-		dip = 1		
-		mil = 1 
-	}
-}
-
-1601.1.1 = {	
-	monarch = {		
-		name = "Samiylo III Kishka"		
-		adm = 1		
-		dip = 1		
-		mil = 1 
-	}
-}
-
-1602.1.1 = {	
-	monarch = {		
-		name = "Kortnevych & Kutskovych"	
-		adm = 1		
-		dip = 2		
-		mil = 2	
-	}
-}
-
-1606.1.1 = {	
-	monarch = {		
-		name = "Zborovsky"			
-		adm = 3		
-		dip = 3		
-		mil = 3	
-	}
-}
-
-1609.1.1 = {	
-	monarch = {		
-		name = "Andriyevch"			
-		adm = 2		
-		dip = 1		
-		mil = 2	
-	}
-}
-
-1610.1.1 = {	
-	monarch = {		
-		name = "Tyskinevych"			
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1614.1.1 = {	
-	monarch = {		
-		name = "P. Sagaydachny"			
-		adm = 3		
-		dip = 4		
-		mil = 5 
-	}
-}
-
-1622.1.1 = {	
-	monarch = {		
-		name = "Olifer Golub"			
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1623.1.1 = {
-	monarch = {		
-		name = "M. Doroshenko"			
-		adm = 2		
-		dip = 2		
-		mil = 4	
-	}
-}
-
-1625.1.1 = {
-	monarch = {		
-		name = "M. Doroshenko"			
-		adm = 2		
-		dip = 2		
-		mil = 4	
-	}
-}
-
-1626.1.1 = {	
-	monarch = {		
-		name = "K. Vovk"			
-		adm = 1		
-		dip = 1		
-		mil = 1	
-	}
-}
-
-1628.1.1 = {	
-	monarch = {		
-		name = "Ivan V Sulyma"			
-		adm = 2		
-		dip = 2		
-		mil = 2	
-	}
-}
-
-1629.1.1 = {	
-	monarch = {	
-		name = "G. Chorny"			
-		adm = 1		
-		dip = 1		
-		mil = 1
-	}
-}
-
-1630.1.1 = {	
-	monarch = {		
-		name = "Orendarenko"
-		adm = 1	
-		dip = 1	
-		mil = 1
-	}
-}
-
-1631.1.1 = {
-	monarch = {
-		name = "Ivan VI Kulaga"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1632.1.1 = {
-	monarch = {
-		name = "Gavrylovych"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1633.1.1 = {
-	monarch = {
-		name = "Samiylo IV Sulyma"
-		adm = 1
-		dip = 1
-		mil = 2
-	}
-}
-
-1635.1.1 = {
-	monarch = {
-		name = "Ivan V Sylyma"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1636.1.1 = {
-	monarch = {
-		name = "Vassyl Tomylenko"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1637.1.1 = {
-	monarch = {
-		name = "Sava, Pavlyuk & Gunya"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1638.1.1 = {
-	monarch = {
-		name = "Gunya"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1640.1.1 = { leader = {	name = "Chmielnicki"           	type = general	fire = 1	shock = 3	manuever = 5	siege = 0 death_date = 1657.8.6 }}
-
-1641.1.1 = {
-	monarch = {
-		name = "Karpo P."
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1644.1.1 = {
-	monarch = {
-		name = "Gulak-Bulyuk"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1648.1.1 = {
-	monarch = {
-		name = "Bogdan IV Khmelnitsky"
-		adm = 4
-		dip = 6
-		mil = 5
-	}
-	government_rank = 2
-}
-
-1654.1.8 = {
-	government_rank = 1
-}
-
-1657.1.1 = {
-	monarch = {
-		name = "Ivan I Vygovskyy"
-		adm = 1
-		dip = 1
-		mil = 1
-	}
-}
-
-1659.1.1 = {
-	monarch = {
-		name = "Yuriy Khmelnitsky"
-		adm = 3
-		dip = 4
-		mil = 4
-	}
-}
-
-1663.1.1 = {
-	monarch = {
-		name = "Divisional Hetmans"
-		adm = 0
-		dip = 0
-		mil = 1
-	}
-}
-
-1687.1.1 = {
-	monarch = {
-		name = "Ivan IV Mazep"
-		adm = 1
-		dip = 3
-		mil = 5
-	}
-}
-
-1695.1.1 = { leader = {	name = "Mazeppa"               	type = general	fire = 2	shock = 4	manuever = 5	siege = 0 death_date = 1710.1.1 }}
-
-1710.1.1 = {
-	monarch = {
-		name = "Ivan V Skoropadsky"
-		adm = 1
-		dip = 5
-		mil = 5
-	}
-}
-
-1722.1.1 = {
-	monarch = {
-		name = "Pavlo II Polubotok"
-		adm = 1
-		dip = 1
-		mil = 2
-	}
-}
-
-1727.1.1 = {
-	monarch = {
-		name = "Danylo Apostol"
-		adm = 0
-		dip = 3
-		mil = 3
-	}
-}
-
-1750.1.1 = {
-	monarch = {
-		name = "Rozumovsky"
-		adm = 0
-		dip = 1
-		mil = 3
-	}
-}
-
-1775.8.3 = {
-	government_rank = 2
-}+government = republic
+add_government_reform = rip_cossacks_reform
+government_rank = 1
+technology_group = eastern
+religion = orthodox
+primary_culture = ruthenian
+capital = 283	# Zaporozhia
+add_country_modifier = {
+	name = "frontier_military_culture"
+	duration = -1
+}
+set_estate_privilege = estate_cossacks_cossack_self_governance
+
+1444.1.1 = {	
+	monarch = {		
+		name = "Ostap"
+		dynasty = Osa			
+		adm = 5		
+		dip = 4		
+		mil = 4	
+	}
+}
+
+1486.1.1 = {	
+	monarch = {		
+		name = "Mykhailo"	
+		dynasty = Vishnevetsky
+		adm = 2		
+		dip = 2		
+		mil = 2 
+	}
+}
+
+1488.1.1 = {	
+	monarch = {		
+		name = "Bohdan Mamaj"	
+		dynasty = Glins'kij
+		adm = 3		
+		dip = 3		
+		mil = 5 
+	}
+}
+
+1492.1.1 = {	
+	monarch = {		
+		name = "Dmytro"	
+		dynasty = Putiatych
+		adm = 4		
+		dip = 5		
+		mil = 0 
+	}
+}
+
+1510.1.1 = {	
+	monarch = {		
+		name = "Semen"	
+		dynasty = Poloz
+		adm = 5		
+		dip = 5		
+		mil = 5 
+	}
+}
+
+1514.1.1 = {	
+	monarch = {		
+		name = "Ostafii"	
+		dynasty = Dashkevych
+		adm = 4		
+		dip = 1		
+		mil = 4
+	}
+}
+
+1516.1.1 = {	
+	monarch = {		
+		name = "Predslav"	
+		dynasty = Liantskoronskyi
+		adm = 5		
+		dip = 2		
+		mil = 1 
+	}
+}
+
+1550.1.1 = {	
+	monarch = {		
+		name = "Dmytro"	
+		dynasty = Vishnevetsky
+		adm = 1		
+		dip = 5		
+		mil = 6 
+	}
+}
+
+
+1555.1.1 = {
+	government_rank = 1
+}
+
+1568.1.1 = {	
+	monarch = {		
+		name = "Andrii"	
+		dynasty = Liakh
+		adm = 2		
+		dip = 2		
+		mil = 5 
+	}
+}
+
+1577.1.1 = {	
+	monarch = {		
+		name = "Ivan"	
+		dynasty = Pidkova
+		adm = 1		
+		dip = 1		
+		mil = 1 
+	}
+}
+
+1578.1.1 = {	
+	monarch = {		
+		name = "Lukian"	
+		dynasty = Chornynskyi
+		adm = 1	
+		dip = 1		
+		mil = 1 
+	}
+}
+
+1581.1.1 = {	
+	monarch = {		
+		name = "Samiilo"	
+		dynasty = Zborovskyi
+		adm = 3		
+		dip = 3		
+		mil = 3 
+	}
+}
+
+1584.1.1 = {	
+	monarch = {		
+		name = "Bohdan"	
+		dynasty = Mykoshynskyi
+		adm = 4		
+		dip = 4		
+		mil = 1 
+	}
+}
+
+1585.1.1 = {	
+	monarch = {		
+		name = "Mykhailo"	
+		dynasty = Ruzhynskyi
+		adm = 5		
+		dip = 4		
+		mil = 1 
+	}
+}
+
+1586.1.1 = {	
+	monarch = {		
+		name = "Lukian"	
+		dynasty = Chornynskyi
+		adm = 1		
+		dip = 1	
+		mil = 1 
+	}
+}
+
+1588.1.1 = {	
+	monarch = {		
+		name = "Ivan"	
+		dynasty = Potrebatskyi
+		adm = 3		
+		dip = 2		
+		mil = 1 
+	}
+}
+
+1589.1.1 = {	
+	monarch = {		
+		name = "Zakhar"	
+		dynasty = Kulaha
+		adm = 5		
+		dip = 2		
+		mil = 1 
+	}
+}
+
+1594.1.1 = {	
+	monarch = {		
+		name = "Gryhorii"	
+		dynasty = Loboda
+		adm = 2	
+		dip = 2
+		mil = 1
+	}
+}
+
+
+1596.1.1 = {	
+	monarch = {		
+		name = "Hnat"	
+		dynasty = Vasylevych
+		adm = 5	
+		dip = 2		
+		mil = 2 
+	}
+}
+
+1597.1.1 = {	
+	monarch = {		
+		name = "Tykhin"	
+		dynasty = Baibuza
+		adm = 4		
+		dip = 4	
+		mil = 1 
+	}
+}
+
+1598.1.1 = {	
+	monarch = {		
+		name = "Florian"	
+		dynasty = Hedroits
+		adm = 1		
+		dip = 2		
+		mil = 4 
+	}
+}
+
+1602.1.1 = {	
+	monarch = {		
+		name = "Ivan"	
+		dynasty = Kutskovych
+		adm = 1	
+		dip = 2		
+		mil = 2
+	}
+}
+
+1603.1.1 = {	
+	monarch = {		
+		name = "Ivan"	
+		dynasty = Kosyi
+		adm = 1	
+		dip = 1
+		mil = 1
+	}
+}
+
+1606.1.1 = {	
+	monarch = {		
+		name = "Samiilo"	
+		dynasty = Zborovskyi
+		adm = 3		
+		dip = 3		
+		mil = 3 
+	}
+}
+
+1617.1.1 = {	
+	monarch = {		
+		name = "Dmytro"	
+		dynasty = Barabash
+		adm = 4		
+		dip = 4		
+		mil = 1 
+	}
+}
+
+1618.1.1 = {	
+	monarch = {		
+		name = "Mykhailo"	
+		dynasty = Skyba
+		adm = 1		
+		dip = 3		
+		mil = 3 
+	}
+}
+
+1619.1.1 = {	
+	monarch = {		
+		name = "Yakiv"	
+		dynasty = Borodavka-Neroda
+		adm = 5		
+		dip = 4		
+		mil = 2 
+	}
+}
+
+1620.1.1 = {	
+	monarch = {		
+		name = "Petro"	
+		dynasty = Odynets
+		adm = 3		
+		dip = 3		
+		mil = 5 
+	}
+}
+
+1624.1.1 = {	
+	monarch = {		
+		name = "Hrytsko"	
+		dynasty =  Chornyi
+		adm = 1	
+		dip = 1		
+		mil = 1 
+	}
+}
+
+1625.1.1 = {	
+	monarch = {		
+		name = "Fedir"	
+		dynasty = Pyrskyi
+		adm = 4	
+		dip = 3		
+		mil = 2
+	}
+}
+
+1628.1.1 = {	
+	monarch = {		
+		name = "Hrytsko"	
+		dynasty =  Chornyi
+		adm = 1	
+		dip = 1	
+		mil = 1
+	}
+}
+
+1629.1.1 = {	
+	monarch = {		
+		name = "Hrytsko"	
+		dynasty =  Chornyi
+		adm = 1	
+		dip = 1	
+		mil = 1
+	}
+}
+
+1630.1.1 = {	
+	monarch = {		
+		name = "Taras"	
+		dynasty = Fedorovych
+		adm = 4		
+		dip = 3		
+		mil = 2 
+	}
+}
+
+1632.1.1 = {	
+	monarch = {		
+		name = "Andrii"	
+		dynasty = Didenko
+		adm = 5		
+		dip = 1		
+		mil = 3 
+	}
+}
+
+1633.1.1 = {	
+	monarch = {		
+		name = "Ivan"	
+		dynasty = Sulyma
+		adm = 1	
+		dip = 1		
+		mil = 2 
+	}
+}
+
+1636.1.1 = {	
+	monarch = {		
+		name = "Vasyl"	
+		dynasty = Tomylenko
+		adm = 1	
+		dip = 1	
+		mil = 1
+	}
+}
+
+1637.1.1 = {	
+	monarch = {		
+		name = "Pavlo"	
+		dynasty = But
+		adm = 5		
+		dip = 4		
+		mil = 1 
+	}
+}
+
+1638.1.1 = {	
+	monarch = {		
+		name = "Yakiv"	
+		dynasty = Iskra-Ostrianyn
+		adm = 4
+		dip = 4		
+		mil = 1 
+	}
+}
+
+1639.1.1 = {	
+	monarch = {		
+		name = "Karpo"	
+		dynasty = Pivtora-Kozhukha
+		adm = 3		
+		dip = 4		
+		mil = 4 
+	}
+}
+
+
+
+1639.1.1 = {	
+	monarch = {		
+		name = "Maxym"	
+		dynasty = Hulak
+		adm = 2		
+		dip = 3		
+		mil = 3 
+	}
+}
+
+1506.1.1 = {
+	leader = {
+		name = "Ostafiy Dashkevych"
+		type = general
+		fire = 2
+		shock = 3
+		manuever = 3
+		siege = 1
+		death_date = 1535.1.1
+	}
+}
+
+1550.1.1 = {
+	leader = {
+		name = "Dmytro Vyshnevetsky"
+		type = general
+		fire = 3
+		shock = 4
+		manuever = 4
+		siege = 1
+		death_date = 1563.10.1
+	}
+}
+
+1574.1.1 = {
+	leader = {
+		name = "Samiylo Kishka"
+		type = admiral
+		fire = 2
+		shock = 4
+		manuever = 5
+		siege = 1
+		death_date = 1602.1.1
+	}
+	leader = {
+		name = "Samiylo Kishka"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 4
+		siege = 1
+		death_date = 1602.1.1
+	}
+}
+
+1594.1.1 = {
+	leader = {
+		name = "Severyn Nalyvaiko"
+		type = general
+		fire = 3
+		shock = 4
+		manuever = 3
+		siege = 1
+		death_date = 1597.4.21
+	}
+}
+
+1614.1.1 = {
+	leader = {
+		name = "Petro Sahaidachny"
+		type = general
+		fire = 4
+		shock = 5
+		manuever = 5
+		siege = 2
+		death_date = 1622.4.20
+	}
+}
+
+1628.1.1 = {
+	leader = {
+		name = "Ivan Sulyma"
+		type = general
+		fire = 3
+		shock = 3
+		manuever = 4
+		siege = 2
+		death_date = 1635.12.12
+	}
+}
+
+1630.1.1 = {
+	leader = {
+		name = "Taras Fedorovych"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 3
+		siege = 0
+		death_date = 1639.1.1
+	}
+}
+
+1640.1.1 = {
+	leader = {
+		name = "Bohdan Khmelnytsky"
+		type = general
+		fire = 4
+		shock = 5
+		manuever = 5
+		siege = 2
+		death_date = 1657.8.6
+	}
+	leader = {
+		name = "Ivan Bohun"
+		type = general
+		fire = 3
+		shock = 5
+		manuever = 5
+		siege = 3
+		death_date = 1664.2.27
+	}
+	leader = {
+		name = "Maksym Kryvonis"
+		type = general
+		fire = 1
+		shock = 5
+		manuever = 3
+		siege = 1
+		death_date = 1648.11.15
+	}
+}
+
+1659.1.1 = {
+	leader = {
+		name = "Ivan Sirko"
+		type = general
+		fire = 3
+		shock = 6
+		manuever = 5
+		siege = 1
+		death_date = 1680.8.11
+	}
+}
+
+1665.1.1 = {
+	leader = {
+		name = "Petro Doroshenko"
+		type = general
+		fire = 3
+		shock = 4
+		manuever = 4
+		siege = 1
+		death_date = 1698.11.19
+	}
+}
+
+1684.1.1 = {
+	leader = {
+		name = "Semen Paliy"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 4
+		siege = 1
+		death_date = 1710.1.1
+	}
+}
+
+1702.1.1 = {
+	leader = {
+		name = "Kost Hordiyenko"
+		type = general
+		fire = 2
+		shock = 4
+		manuever = 4
+		siege = 1
+		death_date = 1733.5.15
+	}
+}
+
+1762.1.1 = {
+	leader = {
+		name = "Petro Kalnyshevsky"
+		type = general
+		fire = 1
+		shock = 3
+		manuever = 3
+		siege = 0
+		death_date = 1803.10.31
+	}
+}
+
+1648.1.1 = {
+	monarch = {
+		name = "Bohdan"
+		dynasty = Khmelnitsky
+		adm = 4
+		dip = 6
+		mil = 5
+	}
+	government_rank = 3
+}	
+
+1654.1.8 = {
+	government_rank = 2
+}
+
+1657.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = Vygovskyy
+		adm = 1
+		dip = 1
+		mil = 1
+	}
+}
+
+1659.1.1 = {
+	monarch = {
+		name = "Yuriy"
+		dynasty = Khmelnitsky
+		adm = 3
+		dip = 4
+		mil = 4
+	}
+}
+
+1660.1.1 = {
+	government_rank = 1
+}
+1660.1.1 = {
+	monarch = {
+		name = "Yuriy"
+		dynasty = Khmelnitsky
+		adm = 3
+		dip = 4
+		mil = 4
+	}
+}
+
+1663.1.1 = {
+	monarch = {
+		name = "Pavlo"
+		dynasty = Teteria
+		adm = 2
+		dip = 4
+		mil = 3
+	}
+}
+
+1665.1.1 = {
+	monarch = {
+		name = "Petro"
+		dynasty = Doroshenko
+		adm = 2
+		dip = 2
+		mil = 4
+	}
+}
+
+
+1668.1.1 = {
+	monarch = {
+		name = "Petro"
+		dynasty = Doroshenko
+		adm = 2
+		dip = 2
+		mil = 4
+	}
+	government_rank = 2
+}
+
+1669.1.1 = {
+	monarch = {
+		name = "Petro"
+		dynasty = Doroshenko
+		adm = 2
+		dip = 2
+		mil = 4
+	}
+}
+
+1678.1.1 = {
+	monarch = {
+		name = "Yuriy"
+		dynasty = Khmelnitsky
+		adm = 3
+		dip = 3
+		mil = 4
+	}
+}
+
+1681.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = Samoilovych
+		adm = 3
+		dip = 4
+		mil = 4
+	}
+}
+
+1685.1.1 = {
+	monarch = {
+		name = "Yuriy"
+		dynasty = Khmelnitsky
+		adm = 3
+		dip = 3
+		mil = 4
+	}
+}
+
+
+1687.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = Mazepa-Kaledynskyi
+		adm = 1
+		dip = 3
+		mil = 5
+	}
+}
+
+1695.1.1 = { leader = {	name = "Mazepa"               	type = general fire = 2	shock = 4	manuever = 5	siege = 0 death_date = 1710.1.1 }}
+
+1708.1.1 = {
+	monarch = {
+		name = "Ivan"
+		dynasty = Skoropadskyi
+		adm = 1
+		dip = 5
+		mil = 5
+	}
+}
+
+1718.1.1 = {
+	monarch = {
+		name = "Pylyp"
+		dynasty = Orlyk
+		adm = 6
+		dip = 1
+		mil = 1
+	}
+}
+
+1727.1.1 = {
+	monarch = {
+		name = "Danylo"
+		dynasty = Apostol
+		adm = 0
+		dip = 3
+		mil = 3
+	}
+}
+
+1750.1.1 = {
+	monarch = {
+		name = "Kyrylo"
+		dynasty = Rozumovskyi
+		adm = 0
+		dip = 1
+		mil = 3
+	}
+}
+
+1775.8.3 = {
+	government_rank = 2
+}
```

### ZLK - Zeleny Klyn.txt

RIP SHA256: `89ad449c643cf5ff337e130f58c55674b0188ab44594b2f1a42e629324a27971`

No vanilla counterpart; historical validation needs external sources.

