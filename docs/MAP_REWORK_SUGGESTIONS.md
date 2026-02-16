# Map Rework Suggestions for RIP Mod
## Based on Paradox Forum Proposals by fr-rein

**Source Threads:**
- [Ruthenia & Cossack Immersion Pack](https://forum.paradoxplaza.com/forum/threads/ruthenia-cossack-immersion-pack.1121263/page-2#post-24736853)
- [Update to Ukrainian Region, Cossacks Content](https://forum.paradoxplaza.com/forum/threads/update-to-ukrainian-region-cossacks-content.1140129/)

---

## Overview

This document outlines comprehensive map rework proposals for the Ukrainian/Ruthenian region based on extensive historical research and EU4 mapping best practices. The proposals range from minimal border corrections to moderate province additions, designed to better represent the historical geography and political dynamics of 1444-1821.

---

## Core Issues Addressed

### 1. **Historical Border Inaccuracies**
- **Cherkasy**: Current southern border is ~50-100km too far south, crossing historical territorial boundaries
- **Starodub vs Trubchevsk**: Province labeled "Trubchevsk" actually contains Starodub; real Trubchevsk is in Severia
- **Dniester River**: Misaligned, affecting Moldova/Ruthenia border accuracy
- **Desna River**: River course doesn't match historical geography

### 2. **Missing Historical Cities**
- **Odesa/Khajibey**: Genoa colony "Ginestra", major Black Sea port, strategic trade hub
- **Ochakov (Özü)**: Ottoman fortress, key to Black Sea naval supremacy
- **Belgorod**: Jagoldai Tatar settlement, strategic border fortress
- **Dnipro (Kodak)**: Kodak fortress location (currently misplaced in Poltava!)

### 3. **Gameplay Issues**
- **Wild Field**: Only 1-2 provinces make Tatar raids impossible to simulate (single fort blocks everything)
- **Cossack Force Limits**: Current 15 provinces with ~80 development = ~20k force limit vs historical 40-100k Hetmanate armies
- **Religious Conversion**: Too easy to paint-convert without representing historical Uniate Church complexity
- **Hetmanate**: No representation of this century-long state that shaped Eastern European history

---

## Proposal Tiers

### **Tier 0: Minimal (Border Fixes Only, 0 New Provinces)**

**Primary Goal:** Fix glaring historical errors without adding provinces

#### Changes:
1. **Cherkasy Border**: Move southern border ~50km north to historical line
   - Rationale: Current border crosses into territory that was part of Wild Field/Ottoman sphere
   - Historical maps show clear demarcation along river systems

2. **Starodub/Trubchevsk**: Split or rename
   - Province labeled "Trubchevsk" → rename to "Starodub"
   - Add actual Trubchevsk in Severia region as separate province (or merge with Sevsk)

3. **Dniester River**: Realign to match historical course
   - Affects Moldova-Ruthenia border
   - Critical for Dniester Estuary mechanics

4. **Severia Area Border**: Adjust to exclude Rylsk, include historical Severian lands
   - Rylsk historically part of Kursk area
   - Severia = Chernigov, Novgorod-Seversky, Starodub core

**Map Illustration:** Zero Proposal
```
- Cherkasy: Southern border moves north to Ingulets River
- Starodub: Rename current "Trubchevsk" province
- Trubchevsk: Add as small province north of Sevsk OR merge with Sevsk
- Dniester: Realign river course through Moldova
```

---

### **Tier 1: Moderate (5 New Provinces)**

**Primary Goal:** Add most critical strategic locations while respecting development density concerns

#### New Provinces:

**1. Belgorod (Province ID TBD)**
- **Location:** Between Kursk and Voronezh
- **Historical Context:** 
  - Jagoldai Tatar settlement (Golden Horde remnant vassal to Lithuania, later Muscovy)
  - Strategic fortress on Zasechnaya Cherta defensive line
  - Border buffer between Lithuania/Muscovy (1444-1494)
- **Gameplay:** Integrates with Border Principalities system (already implemented in mod)
- **Development:** 5-7 (frontier fortress, low population)

**2. Dnipro/Kodak (Province ID TBD)**
- **Location:** East bank of Dnieper, north of current Zaporozhia
- **Historical Context:**
  - Kodak Fortress (1635) built to suppress Cossacks
  - Future site of Yekaterinoslav (Dnipropetrovsk/Dnipro city)
  - Strategic Dnieper crossing
- **Gameplay:** Correctly places Kodak event target (currently wrongly in Poltava!)
- **Development:** 4-6 (fortress, later grows)

**3. Bila Tserkva (Province ID TBD)**
- **Location:** Between Kiev and Cherkasy
- **Historical Context:**
  - Ancient Yuriev, renamed after "White Church" ruins
  - Major Right Bank Ukraine city (as large as Kiev in 1444)
  - Key Cossack regiment center
  - On Tatar raid path to Poland
- **Gameplay:** Critical for Khmelnytsky Uprising events, Right Bank Hetmanate mechanics
- **Development:** 8-10 (major city)

**4. Ochakov/Özü (Province ID TBD)**
- **Location:** Black Sea coast, Dnieper estuary
- **Historical Context:**
  - Ottoman fortress controlling Dnieper-Bug estuary
  - Key naval base for Black Sea dominance
  - Frequently contested (Ottoman-Russian wars, Crimean raids)
- **Gameplay:** Strategic chokepoint for naval/steppe warfare
- **Development:** 6-8 (fortress, small port)

**5. Odesa/Khajibey (Province ID TBD)**
- **Location:** Black Sea coast, Dniester estuary
- **Historical Context:**
  - Genoa colony "Ginestra" (1440s)
  - Multiple Genoese Black Sea colonies in region
  - Future site of Odesa (major port city)
  - Trade route: Istanbul-Odesa-Krakow-Kiev
- **Gameplay:** Adds historical Center of Trade potential, Genoese colonization flavor
- **Development:** 7-9 (trade colony, grows significantly)

#### Additional Changes:
- **Cherkasy**: Border moved north (from Tier 0)
- **Mansur**: Rename to "Bakhmut", adjust borders
- **Yedisan**: Split development with Ochakov/Odesa (currently has unnatural 10-11 dev for empty steppe)

**Map Illustration:** Moderate Proposal (5 New Provinces)
```
Added:
1. Belgorod (Kursk area)
2. Kodak/Dnipro (Wild Field area)
3. Bila Tserkva (Kiev area)
4. Ochakov (Yedisan area)
5. Odesa/Khajibey (Yedisan area)

Total increase: +5 provinces (from ~15 to ~20 in Ukrainian region)
```

---

### **Tier 2: Expanded (7 New Provinces)**

**Primary Goal:** Full Right Bank Ukraine + Wild Field representation

**Adds to Tier 1:**

**6. Chyhyryn (Province ID TBD)**
- **Location:** Right Bank Ukraine, south of Cherkasy
- **Historical Context:**
  - Hetmanate capital under Khmelnytsky and successors (1648-1676)
  - Site of major Cossack uprising spark
  - Utterly destroyed after Right Bank collapse
- **Gameplay:** Essential for Hetmanate mechanics, capital of Cossack state
- **Development:** 6-8 (grows to 10+ as capital, devastated in 1670s-1680s)

**7. Kremenchuk (Province ID TBD)**
- **Location:** Left Bank Ukraine, Dnieper region
- **Historical Context:**
  - Important Left Bank city
  - Cossack regiment center
  - Near-Dnieper economic zone
- **Gameplay:** Fills gap in Left Bank representation
- **Development:** 6-8

**Map Illustration:** Expanded Proposal (7 New Provinces)
```
Tier 1 + Tier 2 additions:
6. Chyhyryn (Right Bank Ukraine area)
7. Kremenchuk (Left Bank Ukraine area)

Total increase: +7 provinces
```

---

### **Tier 3: Comprehensive (13 New Provinces) - For Reference**

**Note:** This tier is from original forum proposals but may be too dense for implementation. Included for historical completeness.

**Additional provinces beyond Tier 2:**
- Korsun (Right Bank Ukraine)
- Myrhorod (Left Bank Ukraine)
- Trubchevsk (Severia - as separate province)
- Sumy (Sloboda Ukraine)
- Izium (Sloboda Ukraine)
- Oril/Pavlograd (Wild Field)
- Zhovti Vody (Wild Field)
- Syni Vody (Wild Field)

**Rationale:** Full historical administrative division representation, optimal for comprehensive Cossack/Tatar raid mechanics

**Concerns:** May be too province-dense compared to surrounding regions

---

## Moldova Region Rework

### Current Issues:
- Only 5 provinces for entire historical Moldovan Principality
- Khotyn (major fortress, site of 1621 battle) not represented
- No Bessarabia split (Russian annexation 1812)
- No Bukovina split (Austrian annexation)

### Moderate Proposal (Moldova: +2-3 provinces):

**1. Khotyn/Hotin**
- Strategic fortress on Dniester
- Site of Battle of Khotyn 1621 (Polish-Lithuanian-Cossack victory over Ottomans)
- Frequently switched hands (Moldova-Poland-Ottoman-Russia)

**2. Cernauti/Chernivtsi**
- Northern Bukovina capital
- Became Austrian after partitions
- Important cultural center

**3. Optional: Tighina**
- Dniester crossing fortress
- Importance due to Dniester Estuary (impassable terrain)
- Ottoman strategic holding

### Expanded Proposal (Moldova: +5-7 provinces):
- Above + Orhei, Soroca, Suceava, Bacau, Birlad
- Creates historically accurate 3-region division:
  - **Moldova core** (Iasi, Suceava, Cernauti)
  - **Bessarabia** (Tighina, Orhei, Soroca) - for Russian annexation
  - **Southern Moldova** (Khotyn area) - for Ottoman/Polish contests

**Justification:** Moldova was powerful in 1444, but fragmented by Ottoman (south), Russian (Bessarabia), and Austrian (Bukovina) partitions. Current 5-province model doesn't allow this historical trajectory.

---

## Wild Field Area Rework

### Historical Context:
**Wild Field (Дике Поле)** = Pontic Steppe region between settled Ruthenia and Crimean/Nogai territories
- Largely unpopulated due to constant Tatar raids (yasyr slave trade)
- Home to Zaporozhian Cossack Sich (nomadic war camps)
- Key transit zone for:
  - Crimean raids into Poland-Lithuania
  - Cossack counter-raids into Crimea
  - Ottoman campaigns northward

### Current Problem:
- Only 1-2 provinces represent entire Wild Field
- Single fort completely blocks all raid mechanics
- No space for army maneuvering or historical raid paths
- Zaporozhia Cossacks = 1-province OPM joke instead of major regional power

### Proposal:

**Minimum (Tier 1):** Add Kodak/Dnipro province
- Allows basic fort bypassing
- Creates 2-province Wild Field

**Moderate (Tier 2):** Add Kodak + Chyhyryn
- 3-province Wild Field with Right Bank buffer
- Functional raid mechanics possible

**Expanded (Tier 3):** 5-province Wild Field
- Full raid path implementation:
  1. **Zaporozhia**: Sich heartland (existing)
  2. **Kodak**: Dnieper fort zone
  3. **Chyhyryn**: Right Bank transition
  4. **Chornyi Lis**: Black Forest, start of steppe (New Serbia settlement later)
  5. **Syni Vody/Zhovti Vody**: Central steppe, Tatar raid paths

**Development Balance:**
- Wild Field provinces: 3-6 development (empty steppe)
- With Tatar Raid mechanics (implemented in mod), low dev justified by constant devastation
- Later colonization events convert to 8-12 dev (Sloboda Ukraine, Donbass settlement)

---

## Historical Justifications

### Why More Provinces?

**1. Force Limit Issue:**
Current Hetmanate territory = 15 provinces, ~80 development = ~20k force limit

Historical Hetmanate armies:
- Minimum estimate (Polish treaties): 40,000 regulars
- Battle evidence: 60,000 regulars
- Maximum estimates: 100,000+ (including militia)

**Solution:** More provinces = more development = realistic force limits without breaking ideas/buildings

**2. Religious Conversion:**
- Current: Poland easily converts all Ruthenia to Catholic in 50 years
- Historical: 200 years of Uniate Church compromise, persistent Orthodoxy, religious revolts
- Solution: More provinces = more missionaries needed, slower conversion

**3. Cossack Estate Mechanics:**
- Current: Cossacks only spawn in Steppe terrain (2-3 provinces)
- Historical: Cossacks dominated 20+ provinces in Right Bank, Left Bank, Wild Field
- Solution: More provinces with Cossack estate = historically accurate influence

**4. Tatar Raid Mechanics:**
- Current: Single fort blocks all raids
- Historical: Raids bypassed forts, devastated wide areas, multiple simultaneous paths
- Solution: Multiple provinces with varied terrain = functional raid system (already implemented in mod!)

**5. Hetmanate State Formation:**
- Current: No Hetmanate tag, Khmelnytsky Uprising = generic rebellion
- Historical: Century-long independent Cossack state (1648-1764)
- Solution: Province density supports forming unique Hetmanate with proper borders

---

## Integration with Existing Mod Systems

### 1. **Steppe Raiding System** (Already Implemented)
- 10 events for yasyr trade, Crimean raids, Nogai/Kalmyk migrations
- **Map Requirements:** 
  - Multiple Wild Field provinces for raid paths
  - Province modifiers for hostile attrition (Tatar settlements)
  - Zasechnaya Cherta defensive line provinces

**Optimal:** Tier 2-3 Wild Field (5+ provinces)

### 2. **Border Principalities System** (Already Implemented)
- 18 events for Rylsk (Shemyaka), Glinski lands, Jagoldai, Qasim Khanate
- **Map Requirements:**
  - Belgorod province (Jagoldai settlement)
  - Rylsk province (Shemyaka descendants)
  - Kursk area adjustments

**Optimal:** Tier 1+ (Belgorod province essential)

### 3. **Cossack Hetmanate Mechanics** (Planned)
- Khmelnytsky Uprising disaster
- Right Bank vs Left Bank Hetmanate split
- Cossack regiment administration
- **Map Requirements:**
  - Bila Tserkva, Cherkasy, Chyhyryn (Right Bank centers)
  - Kremenchuk, Poltava, Pereyaslav (Left Bank centers)
  - Zaporozhia, Wild Field (Sich territory)

**Optimal:** Tier 2+ (Chyhyryn capital province essential)

### 4. **Greek Catholic/Uniate Church** (Planned)
- Church Union of Brest (1596) intermediate religion
- Gradual conversion mechanics vs forced conversion
- **Map Requirements:**
  - More provinces = slower conversion
  - Western Ukraine vs Eastern Ukraine distinction

**Optimal:** Any tier (more provinces = better)

---

## Recommended Implementation Path

### **Phase 1: Critical Fixes (Tier 0)**
**Effort:** Low (border adjustments only)
**Impact:** High (fixes glaring errors)

- Fix Cherkasy border
- Fix Starodub/Trubchevsk naming
- Realign Dniester River
- Adjust Severia area borders

**Time Estimate:** 1-2 hours (definition.csv edits)

---

### **Phase 2: Strategic Additions (Tier 1 Partial - 3 provinces)**
**Effort:** Medium (3 new provinces)
**Impact:** High (enables Border Principalities + Steppe Raids)

Priority provinces:
1. **Belgorod** - Essential for Jagoldai/Border Principalities events (already implemented!)
2. **Kodak/Dnipro** - Fixes Kodak fortress misplacement, enables Wild Field raids
3. **Bila Tserkva** - Major city, enables Right Bank Hetmanate events

**Time Estimate:** 4-6 hours (province creation, history files, localization)

---

### **Phase 3: Full Moderate (Tier 1 Complete - 5 provinces)**
**Effort:** Medium-High (2 additional provinces)
**Impact:** Medium (trade/strategic depth)

Additional provinces:
4. **Ochakov** - Ottoman fortress, Black Sea control
5. **Odesa** - Genoa colony, trade hub, future major port

**Time Estimate:** 3-4 hours

---

### **Phase 4: Hetmanate Support (Tier 2 - 7 provinces)**
**Effort:** High (2 more provinces + Hetmanate mechanics)
**Impact:** Very High (enables full Hetmanate simulation)

Additional provinces:
6. **Chyhyryn** - Hetmanate capital
7. **Kremenchuk** - Left Bank city

**Time Estimate:** 6-8 hours (includes Hetmanate government reform, disaster, missions)

---

### **Phase 5: Moldova Rework (Optional)**
**Effort:** Medium (2-3 provinces)
**Impact:** Medium (historical partitions)

Priority:
1. **Khotyn** - Major fortress, battle site
2. **Cernauti** - Bukovina, Austrian partition
3. Optional: **Tighina** - Dniester crossing

**Time Estimate:** 3-5 hours

---

## Technical Implementation Notes

### Province Creation Checklist:
- [ ] `definition.csv` - Add province ID, RGB color, province name
- [ ] `default.map` - Update max_provinces, province ranges
- [ ] `area.txt` - Assign provinces to areas
- [ ] `region.txt` - Verify area-to-region assignments
- [ ] `history/provinces/XXXX - Name.txt` - Create province history
  - [ ] Base tax, production, manpower
  - [ ] Culture, religion
  - [ ] Owner, controller
  - [ ] Core, HRE status
  - [ ] Buildings
  - [ ] Trade node
  - [ ] Native size/ferocity/hostileness (if applicable)
- [ ] `localisation/*_l_english.yml` - Add province name, adjective
- [ ] `positions.txt` - Set unit position, text position, port position
- [ ] `climate.txt` - Assign climate (if applicable)
- [ ] `terrain.txt` - Assign terrain type
- [ ] `map/adjacencies.csv` - Add sea connections (if coastal)
- [ ] Graphical map files (if creating actual map mod):
  - [ ] `provinces.bmp` - Paint province with exact RGB
  - [ ] `rivers.bmp` - Add river connections
  - [ ] `terrain.bmp` - Set terrain texture

### Development Guidelines:
- **Wild Field provinces:** 3-6 base development (devastated by raids)
- **Frontier fortresses:** 5-8 base development (military focus, low population)
- **Major cities:** 8-12 base development (Bila Tserkva, Odesa)
- **Trade colonies:** 7-10 base development (Genoese holdings)

### Culture/Religion Guidelines:
- **Right Bank Ukraine:** Ruthenian culture, Orthodox religion
  - After 1596: Some provinces convert to Uniate (when implemented)
- **Wild Field:** Ruthenian culture (Cossack settlers), Orthodox
  - Alternative: "Nomadic" or "Cossack" culture variant
- **Genoa colonies:** Italian culture initially, converts to Ruthenian/Turkish
- **Tatar settlements:** Crimean culture, Sunni Islam
- **Frontier zones:** Mixed cultures (represent border dynamics)

---

## Historical Sources Referenced

**Maps:**
- [Hetmanate administrative divisions](https://commons.wikimedia.org/wiki/File:Getmanshchyna.jpg)
- [Oryol Namestnichestvo 1792 with Trubchevsk](https://commons.wikimedia.org/wiki/File:Map_of_Oryol_Namestnichestvo_1792_(small_atlas).jpg)
- [Poland after Truce of Deulino 1618-1619](https://pl.wikipedia.org/wiki/Plik:Truce_of_Deulino_1618-1619.PNG)
- [Poland in 1635](https://upload.wikimedia.org/wikipedia/commons/7/7c/Polish-Lithuanian_Commonwealth_1635.svg)
- [Desna River course](https://commons.wikimedia.org/wiki/File:Desna.png)
- [Sloboda Ukraine development](https://commons.wikimedia.org/wiki/File:Slob_uk_dev.png)
- [Hetmanate in 1648 post-Uprising](https://uk.wikipedia.org/wiki/Файл:Гетьманщина-полки_(за_Кривошеєм).png)

**Books/Articles:**
- Krivosheev's works on Hetmanate administrative structure
- Studies on Cossack regiments and their territories
- Ottoman-Crimean fortification systems
- Genoa Black Sea colonies documentation

---

## Alternative Minimal Approach (If Province Addition Undesirable)

If adding provinces is not feasible, alternative solutions:

### 1. **Development Rebalancing**
- Increase development in existing Ruthenian provinces
- Current ~80 total → Target 120-150 total
- Redistributes from over-developed steppe (Yedisan 10+ dev → 5-6 dev)

### 2. **Special Buildings**
- "Cossack Registry" building: +15% force limit, +10% manpower
- "Sich Camp" building: +20% cavalry combat ability
- Available only in specific provinces (Zaporozhia, Cherkasy, Kiev area)

### 3. **Government Reform Bonuses**
- Hetmanate government: +25% force limit, +0.5 yearly army tradition
- Balances force limit without map changes

### 4. **Area Terrain Changes**
- Change some "plains" to "steppe" or "grasslands" in Wild Field
- Enables Cossack estate expansion without province additions

### 5. **Event-driven Colonization**
- Events that add development over time (1500-1700)
- Simulates Sloboda Ukraine settlement, New Serbia, Novorossiya colonization
- Transforms Wild Field from 4 dev → 10-12 dev provinces

**Note:** These are inferior to proper province additions but provide some historical accuracy if map changes impossible.

---

## Conclusion

The map rework proposals range from minimal border corrections (Tier 0) to comprehensive historical representation (Tier 3). **Recommended implementation: Tier 1-2** (5-7 new provinces), focusing on:

**Essential:**
- Belgorod (Border Principalities integration)
- Kodak/Dnipro (Wild Field raids, Kodak fortress fix)
- Bila Tserkva (Hetmanate mechanics)

**Highly Recommended:**
- Ochakov (Ottoman fortress)
- Odesa (Genoa colony, trade)
- Chyhyryn (Hetmanate capital)

**Optional:**
- Kremenchuk (Left Bank depth)
- Moldova additions (Khotyn, Cernauti)

**Integration:** All proposals designed to work with already-implemented mod systems (Steppe Raids, Border Principalities) and planned systems (Hetmanate, Uniate Church).

**Historical Accuracy:** All province additions based on:
- Period maps (1444-1821)
- Administrative divisions (Hetmanate regiments, Polish voivodeships, Russian guberniyas)
- Strategic importance (fortresses, battles, capitals)
- Economic significance (trade colonies, river crossings)

**Next Steps:**
1. Review proposals with mod team
2. Select implementation tier (recommend Tier 1 minimum)
3. Create province history files
4. Update localization
5. Test integration with existing events
6. Gather playtest feedback on balance

---

**Document Version:** 1.0  
**Date:** January 30, 2026  
**Author:** Based on fr-rein forum proposals, compiled for RIP mod  
**Status:** Proposal for implementation
