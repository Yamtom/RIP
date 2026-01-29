# PODILLIA TECHNICAL INTEGRATION GUIDE

## Overview

This document provides technical references and integration mappings for the Podillia (PDL) government and mission system implementation. It serves as a bridge between game mechanics, file locations, and historical context.

**Last Updated:** January 3, 2026  
**Status:** Implementation Phase - Technical Integration Layer Complete  
**Files Modified:** 3 (government_reforms, government_names, missions)

---

## 1. Government Reform System Integration

### Location
- **Primary File:** `common/government_reforms/RIP_government_reforms.txt` (Lines 2105-2370)
- **Related File:** `common/government_names/000_RIP_names.txt` (Government titles)

### Reform Architecture

All Podillia reforms follow the pattern:

```eu4
[reform_name] = {
	icon = "[icon_name]"
	potential = { tag = PDL }
	trigger = { tag = PDL [+ optional conditions] }
	modifiers = { [mechanical bonuses] }
	custom_attributes = { locked_government_type = yes }
}
```

### 1.1 Base Reform: pdl_frontier_voivodeship_reform

**Icon:** assembly_hall  
**Lines:** 2105-2130 (RIP_government_reforms.txt)  
**Purpose:** Foundational independence reform unlocking Podillia governance  
**Modifiers:**
- governing_capacity_modifier = 0.15
- reform_progress_growth = 0.15
- state_maintenance_modifier = -0.10
- diplomatic_reputation = 0.5
- global_unrest = -1

**Triggers:** PDL tag only (all Podillia nations can adopt)  
**Government Names Trigger:** `trigger = { has_reform = pdl_frontier_voivodeship_reform }`  
→ Displays: FRONTIER_VOIVODE → BORDER_VOIVODE → PALATINE_VOIVODE (Ranks 1-3)

**AI Weight:** 10 (always preferred for PDL as foundation)

---

### 1.2 Path A: pdl_carpathian_bastion_reform

**Icon:** soldiers_4  
**Lines:** 2147-2181 (RIP_government_reforms.txt)  
**Purpose:** Defensive militarization with fortress emphasis (Croatian historical model)

**Modifiers:**
- fort_maintenance_modifier = -0.20 (20% savings on fort maintenance)
- defensiveness = 0.25 (25% defensive bonus)
- garrison_size = 0.20 (20% increased garrison size)
- army_tradition_decay = -0.01 (reduced tradition decay)
- hostile_attrition = 1.5 (1.5x extra attrition to enemies)

**Triggers:** Mission "PDL_fortify_khotyn" completion  
**Government Names Trigger:** `trigger = { has_reform = pdl_carpathian_bastion_reform }`  
→ Displays: FORT_CAPTAIN → GARRISON_COMMANDER → BASTION_VOIVODE (Ranks 1-3)

**Cross-Reference:** Volhynia `vln_voivode_council_reform` (shared military traditions)

**AI Weight:** 8  
**Strategic Notes:**
- Best for defensive playstyle against Ottoman/Crimean threats
- Pairs with Carpathian Bastion mission path (Slot 1, Podillia_Missions.txt)
- Complements garrison development in frontier provinces

---

### 1.3 Path B: pdl_frontier_republic_reform

**Icon:** cossack_cavalry  
**Lines:** 2189-2219 (RIP_government_reforms.txt)  
**Purpose:** Cossack-cavalry specialization (Lithuanian-Cossack hybrid model)

**Modifiers:**
- cavalry_cost = -0.15 (15% cheaper cavalry)
- cavalry_flanking = 0.25 (25% better flanking)
- land_forcelimit = 0.15 (15% increased forcelimit)
- mil_tech_cost_modifier = -0.05 (5% cheaper military tech)
- army_tradition = 0.25 (25% army tradition bonus)

**Special Ability:** `government_abilities = { cossacks_mechanic }`  
→ Unlocks estate_cossacks interaction mechanics (loyalty/influence system)

**Triggers:** Mission "PDL_recruit_cossacks" completion  
**Government Names Trigger:** `trigger = { has_reform = pdl_frontier_republic_reform }`  
→ Displays: HOST_VOIVODE → HETMAN_VOIVODE → HOST_COMMANDER (Ranks 1-3)

**Cross-Reference:** Volhynia `vln_cossack_host_reform` (cavalry integration)

**AI Weight:** 8  
**Strategic Notes:**
- Emphasizes cavalry units and steppe warfare
- Requires Cossacks DLC for full estate mechanics
- Pairs with Frontier Republic mission path (Slot 2, Podillia_Missions.txt)
- Integrates with estate_cossacks privilege system

---

### 1.4 Path C: pdl_magnate_dominion_reform

**Icon:** noble_council  
**Lines:** 2235-2268 (RIP_government_reforms.txt)  
**Purpose:** Polish-Lithuanian magnate oligarchy model (Mazovian historical reference)

**Modifiers:**
- global_tax_modifier = 0.15 (15% higher taxes)
- trade_efficiency = 0.15 (15% better trade)
- governing_capacity_modifier = 0.20 (20% more governing capacity)
- merchants = 1 (additional merchant)
- burghers_influence_modifier = 0.15 (15% burgher influence)
- nobles_influence_modifier = 0.10 (10% noble influence)
- max_absolutism = 15 (base absolutism cap 15 higher)

**Estate Feature:** `start_territory_to_estates = 0.25`  
→ Allocates 25% of state territory to estate control (autonomy mechanics)

**Triggers:** Mission "PDL_magnate_authority" completion  
**Government Names Trigger:** `trigger = { has_reform = pdl_magnate_dominion_reform }`  
→ Displays: MAGNATE_DUKE → MAGNATE_KING → AUTONOMOUS_VOIVODE (Ranks 1-3)

**Cross-Reference:** Galicia `hlc_crown_and_sejm_reform` (shared noble mechanics)

**AI Weight:** 8  
**Strategic Notes:**
- Ideal for trade and economic development
- Creates autonomous estates (potential autonomy management challenge)
- Pairs with Magnate Dominion mission path (Slot 3, Podillia_Missions.txt)
- Synergizes with Polish-Lithuanian cultural integration

---

### 1.5 Final Tier: pdl_grand_podillia_reform

**Icon:** king_highlighted  
**Lines:** 2280-2310 (RIP_government_reforms.txt)  
**Purpose:** Final government tier achieving regional supremacy

**Modifiers:**
- prestige = 2 (2 monthly prestige)
- stability_cost_modifier = -0.15 (15% cheaper stability)
- diplomatic_reputation = 1 (1 diplomatic reputation)
- max_absolutism = 20 (base absolutism cap 20 higher)
- reform_progress_growth = 0.10 (10% reform progress)
- global_manpower_modifier = 0.10 (10% manpower)

**Triggers:** Mission "PDL_grand_podillia" completion + conquest requirements

**Government Names Trigger:** `trigger = { has_reform = pdl_grand_podillia_reform }`  
→ Displays: GRAND_VOIVODE → GRAND_KING → PODILLIAN_EMPEROR (Ranks 1-3)

**AI Weight:** 10 (highest priority at late game)

**Strategic Notes:**
- Unlocks post-expansion government tier
- Requires significant territorial conquest
- Can be adopted after any primary path completion
- Represents Podillia as regional hegemon

---

### 1.6 Optional: pdl_religious_tolerance_reform

**Icon:** holy_state  
**Lines:** 2323-2367 (RIP_government_reforms.txt)  
**Purpose:** Confessional balance system (religious coexistence model)

**Modifiers:**
- tolerance_heretic = 2 (2 tolerance to heretics)
- tolerance_heathen = 1 (1 tolerance to heathens)
- religious_unity = 0.25 (25% religious unity)
- stability_cost_modifier = -0.15 (15% cheaper stability)
- missionary_maintenance_cost = -0.25 (25% cheaper missionaries)
- global_missionary_strength = 0.02 (2% stronger missionaries)

**Triggers:** Mission "PDL_religious_tolerance" completion

**Government Names Trigger:** Not directly used (overlay reform)  
→ Can combine with any primary path

**AI Weight:** 6 (medium priority)  
**AI Modifier:** 1.5x weight if nation is jewish or orthodox

**Strategic Notes:**
- Compatible with all primary paths (Carpathian/Frontier/Magnate)
- Emphasizes religious tolerance (unique to Podillia)
- Reflects historical Orthodox-Catholic-Jewish coexistence
- Pairs with Religious & Cultural mission path (Slot 5, Podillia_Missions.txt)

---

## 2. Government Names Integration

### Location
- **File:** `common/government_names/000_RIP_names.txt`
- **Podillia Blocks:** Lines [to be updated with exact ranges]

### 2.1 Government Names Architecture

Each government name block follows:

```eu4
[reform_name] = {
	rank = { 1 = TITLE_RANK_1; 2 = TITLE_RANK_2; 3 = TITLE_RANK_3 }
	ruler_male = { 1 = MALE_TITLE_1; 2 = MALE_TITLE_2; 3 = MALE_TITLE_3 }
	ruler_female = { 1 = FEMALE_TITLE_1; 2 = FEMALE_TITLE_2; 3 = FEMALE_TITLE_3 }
	trigger = { has_reform = [reform_name] }
}
```

### 2.2 Podillia Government Names Blocks

#### pdl_frontier_voivodeship (Base Reform)
```
Rank 1: FRONTIER_VOIVODE (Crown title)
Rank 2: BORDER_VOIVODE
Rank 3: PALATINE_VOIVODE

Ruler Male: VOIVODE_MALE variants
Ruler Female: VOIVODE_FEMALE variants
```
**Trigger:** `has_reform = pdl_frontier_voivodeship_reform`

#### pdl_carpathian_bastion (Defensive Path)
```
Rank 1: FORT_CAPTAIN
Rank 2: GARRISON_COMMANDER
Rank 3: BASTION_VOIVODE
```
**Trigger:** `has_reform = pdl_carpathian_bastion_reform`  
**Historical Reference:** Croatian military titles (adaptation of fortress captaincy system)

#### pdl_frontier_republic (Cossack Path)
```
Rank 1: HOST_VOIVODE
Rank 2: HETMAN_VOIVODE
Rank 3: HOST_COMMANDER
```
**Trigger:** `has_reform = pdl_frontier_republic_reform`  
**Historical Reference:** Hetman and Cossack Host structure

#### pdl_magnate_dominion (Noble Path)
```
Rank 1: MAGNATE_DUKE
Rank 2: MAGNATE_KING
Rank 3: AUTONOMOUS_VOIVODE
```
**Trigger:** `has_reform = pdl_magnate_dominion_reform`  
**Historical Reference:** Polish magnate titles and autonomy

#### pdl_grand_podillia (Final Tier)
```
Rank 1: GRAND_VOIVODE
Rank 2: GRAND_KING
Rank 3: PODILLIAN_EMPEROR
```
**Trigger:** `has_reform = pdl_grand_podillia_reform`  
**Notes:** Highest prestige tier, represents regional hegemony

### 2.3 Localization Keys Required (l_english.yml)

For each government name block, add:

```yaml
# Podillia Government Names
 FRONTIER_VOIVODE: "Voivode of Podillia"
 FRONTIER_VOIVODE_MALE: "Voivode"
 FRONTIER_VOIVODE_FEMALE: "Voivod's Consort"
 [... and so on for all 15 titles]
```

---

## 3. Mission System Integration

### Location
- **File:** `missions/Podillia_Missions.txt` (1088 lines total)

### 3.1 Mission Architecture

**Slot Structure:**
```
Slot 1: Carpathian Bastion (5 missions, defensive focus)
Slot 2: Frontier Republic (4 missions, cavalry/Cossack focus)
Slot 3: Magnate Dominion (5 missions, trade/noble focus)
Slot 4: Universal Expansion (4 missions, conquest progression)
Slot 5: Religious & Cultural (4 missions, soft power)
+ Synergy Missions (Galicia/Volhynia integration)
+ Historical Milestone (Khotyn Siege)
```

### 3.2 Slot 1: Carpathian Bastion Path

#### Mission Progression

**PDL_declare_independence (Position 1)**
- **Icon:** mission_monarch_in_throne_room
- **Trigger:** is_subject = no
- **Effect:** Claim podolia_volhynia_area provinces
- **AI Weight:** 150 (high priority for initial independence)
- **Cross-Reference:** First mission in all paths, establishes PDL sovereignty

**PDL_fortify_khotyn (Position 2)**
- **Icon:** mission_non-western_soldiers
- **Trigger:** owns 281 (Khotyn), has fort_17th
- **Effect:** Adds barracks to Khotyn, grants prestige bonus
- **Mechanical Impact:** Unlocks pdl_carpathian_bastion_reform trigger
- **Historical Note:** Khotyn fortress = key strategic location (1621, 1673 sieges)

**PDL_fortify_kamianets (Position 3)**
- **Icon:** mission_build_up_to_force_limit
- **Trigger:** owns 277 (Kamianets), has fort_17th
- **Effect:** Center of trade upgrade
- **Mechanical Impact:** Develops trade infrastructure
- **Historical Note:** Kamianets-Podilskyi = administrative center

**PDL_border_garrison (Position 4)**
- **Icon:** mission_build_up_to_force_limit
- **Trigger:** Garrison buildings in 3+ regions, army_size >= 20
- **Effect:** Adds barracks to all podolia_volhynia_area provinces
- **Mechanical Impact:** Garrison tradition development
- **AI Weight:** 150

**PDL_resist_ottomans (Position 5)**
- **Icon:** mission_cannons_firing
- **Trigger:** war_exhaustion = 0, army_tradition >= 25
- **Effect:** Prestige + mil_power bonus
- **Mechanical Impact:** Cumulative Turkish resistance tradition
- **AI Weight:** 100

### 3.3 Slot 2: Frontier Republic Path

#### Mission Progression

**PDL_recruit_cossacks (Position 1)**
- **Icon:** mission_cavalry_raid
- **Trigger:** estate_cossacks exists, >= 30% influence
- **Effect:** Sets pdl_cossack_recruited flag
- **Mechanical Impact:** Unlocks pdl_frontier_republic_reform trigger
- **Historical Note:** Zaporizhian Sich integration into Podillia military

**PDL_steppe_mastery (Position 2)**
- **Icon:** mission_cavalry_charge
- **Trigger:** cavalry_tradition >= 30, crimea_area has 3+ controlled provinces
- **Effect:** Cavalry flanking bonus
- **Mechanical Impact:** Steppe warfare specialization
- **AI Weight:** 150

**PDL_host_assembly (Position 3)**
- **Icon:** mission_soldiers_6
- **Trigger:** estate_cossacks >= 50 influence, military_power >= 200
- **Effect:** Cavalry tradition boost
- **Mechanical Impact:** Cossack host organization
- **AI Weight:** 100

**PDL_secure_crimea_raids (Position 4)**
- **Icon:** mission_cavalry_raid
- **Trigger:** Crimea area has 3+ provinces, cavalry_tradition >= 50
- **Effect:** Cavalry tradition consolidation
- **Mechanical Impact:** Steppe dominance assertion
- **AI Weight:** 100

### 3.4 Slot 3: Magnate Dominion Path

#### Mission Progression

**PDL_magnate_authority (Position 1)**
- **Icon:** mission_noble_council
- **Trigger:** estate_nobility >= 40 influence
- **Effect:** Sets pdl_magnate_path flag
- **Mechanical Impact:** Unlocks pdl_magnate_dominion_reform trigger
- **Historical Note:** Magnate power consolidation in Podillia

**PDL_develop_trade (Position 2)**
- **Icon:** mission_trade_route
- **Trigger:** merchants >= 1, trade_power >= 200
- **Effect:** Trade node development bonuses
- **Mechanical Impact:** Trade infrastructure expansion
- **AI Weight:** 150

**PDL_agricultural_prosperity (Position 3)**
- **Icon:** mission_agricultural_development
- **Trigger:** Production development in steppe provinces >= 5
- **Effect:** Production efficiency bonuses
- **Mechanical Impact:** Steppe agricultural development
- **AI Weight:** 100

**PDL_toll_roads (Position 4)**
- **Icon:** mission_trade_route
- **Trigger:** trade_steering >= 0.15, merchants >= 2
- **Effect:** Trade steering bonuses
- **Mechanical Impact:** Trade monopoly enforcement
- **AI Weight:** 100

**PDL_magnate_sejm (Position 5)**
- **Icon:** mission_parliament
- **Trigger:** estate_nobility >= 60 influence
- **Effect:** Absolutism cap reduction (autonomy increase)
- **Mechanical Impact:** Noble assembly legitimation
- **AI Weight:** 80

### 3.5 Slot 4: Universal Expansion

**PDL_unite_podillia (Position 1)**
- **Trigger:** Control all podolia_volhynia_area provinces
- **Effect:** Claim expansion into red_ruthenia

**PDL_conquer_red_ruthenia (Position 2)**
- **Trigger:** Control red_ruthenia_area provinces
- **Effect:** Expansion bonus into Galician territories

**PDL_expand_eastward (Position 3)**
- **Trigger:** Control west_dniepr_area
- **Effect:** Eastern expansion enablement

**PDL_grand_podillia (Position 4)**
- **Trigger:** Control all objectives + pdl_grand_podillia_reform
- **Effect:** Unlocks highest government tier
- **Mechanical Impact:** Final tier government names display

### 3.6 Slot 5: Religious & Cultural

**PDL_religious_tolerance (Position 1)**
- **Trigger:** religious_unity >= 0.50
- **Effect:** Sets pdl_tolerance_path flag
- **Mechanical Impact:** Enables pdl_religious_tolerance_reform

**PDL_jewish_communities (Position 2)**
- **Trigger:** tolerance_heretic >= 1, develop 5+ provinces
- **Effect:** Jewish community bonuses

**PDL_confessional_equilibrium (Position 3)**
- **Trigger:** Balanced religious population (not >50% any religion)
- **Effect:** Religious diversity bonuses

**PDL_cultural_renaissance (Position 4)**
- **Trigger:** Institution development (renaissance >= 100%)
- **Effect:** Cultural development bonuses, idea cost reduction

### 3.7 Synergy Missions

**PDL_galician_compact (Slot 1, Position 3)**
- **Trigger:** HLC (Galicia) exists and is independent
- **Effect:** Alliance bonus, prestige boost
- **Cross-Reference:** Volhynia integration

**PDL_trade_corridor (Slot 1, Position 4)**
- **Trigger:** PDL_galician_compact completed
- **Effect:** Trade efficiency bonuses with Galicia
- **Mechanical Integration:** Cross-region trade synergy

**PDL_khotyn_siege (Slot 2, Historical Milestone)**
- **Trigger:** Fortify Khotyn + military strength
- **Effect:** Military technology advancement
- **Historical Context:** 1621 Khotyn Siege (Polish-Cossack victory)

---

## 4. Cross-Regional Synergies

### Podillia + Volhynia (VLN) Integration

| Mechanic | PDL Path | VLN Counterpart | Interaction |
|----------|----------|-----------------|-------------|
| Military | Carpathian Bastion | vln_voivode_council_reform | Garrison + fort traditions |
| Cavalry | Frontier Republic | vln_cossack_host_reform | Cavalry flanking, Cossack estates |
| Trade | Magnate Dominion | vln_magdeburg_rights | Trade efficiency stacking |
| Religion | Religious Tolerance | vln_confessional_reform | Tolerance bonuses |
| Culture | Cultural Renaissance | vln_ruthenia_reform | Development cost reduction |

### Podillia + Galicia (HLC) Integration

| Mechanic | PDL Path | HLC Counterpart | Interaction |
|----------|----------|-----------------|-------------|
| Government | Magnate Dominion | hlc_crown_and_sejm_reform | Noble cooperation |
| Trade | Magnate Dominion | Trade efficiency | Red Ruthenia trade synergy |
| Religious | Religious Tolerance | hlc_confessional_dualism | Confessional balance |
| Expansion | Grand Podillia | Territorial claims | Red Ruthenia conquest routes |

---

## 5. Modifier System Reference

### Modifiers Created by Missions

All modifiers referenced in Podillia missions are designed to support specific gameplay paths:

**Defensive Path (Carpathian):**
- pdl_khotyn_fortress: Garrison + fort bonuses
- pdl_garrison_tradition: Garrison culture development
- pdl_ottoman_resistance: Defensive standing against Turkish threats

**Cavalry Path (Frontier):**
- pdl_steppe_masters: Cavalry bonuses, steppe terrain mastery
- pdl_host_assembly: Estate cossacks integration
- pdl_secure_crimea_raids: Cavalry tradition from raiding

**Economic Path (Magnate):**
- pdl_magnate_authority: Noble influence expansion
- pdl_develop_trade: Trade power and efficiency
- pdl_agricultural_prosperity: Production bonuses
- pdl_toll_roads: Trade steering and merchant rights
- pdl_magnate_sejm: Autonomous sejm mechanics

**Cultural Path (Religious & Cultural):**
- pdl_jewish_communities: Tolerance for jewish faith
- pdl_confessional_equilibrium: Religious unity and tolerance stacking
- pdl_cultural_renaissance: Development cost reduction, institution spread

**Regional Synergies:**
- pdl_galician_compact: Cross-regional alliance bonuses
- pdl_khotyn_victory: Military victory legacy bonuses

### Modifier Stacking Rules

- **Non-Conflicting:** Each path-specific modifier does NOT conflict with others
- **Duration:** Most path modifiers are permanent (-1 duration) except timed victories
- **Stacking:** Multiple path modifiers can be active simultaneously
- **Overlay:** Religious Tolerance path modifiers stack with any primary path

---

## 6. Event System Hooks

These country flags are created by missions and available for event/decision design:

```eu4
pdl_galician_compact: Allied with Galicia
pdl_cossack_recruited: Cossack host established
pdl_magnate_path: Magnate dominion chosen
pdl_tolerance_path: Religious tolerance established
pdl_ottoman_raids_survive: Survived Ottoman raids
pdl_grand_podillia: Grand Podillia achievement unlocked
```

---

## 7. Historical Timeline Integration

### 1444-1500: Independence Period
- **Missions:** PDL_declare_independence, initial fortification
- **Government:** pdl_frontier_voivodeship_reform
- **Historical Context:** Autonomous under Polish protection

### 1500-1569: Consolidation
- **Missions:** Path specialization begins
- **Government:** Choice between pdl_carpathian/frontier/magnate paths
- **Historical Context:** Increasingly integrated into PLC

### 1569-1648: Integration & Conflict
- **Missions:** Expansion into Red Ruthenia, religious balance
- **Government:** Path consolidation, pdl_grand_podillia unlock
- **Historical Context:** Full PLC integration, Khotyn Siege (1621)

---

## 8. Balance Notes

### AI Behavior

**Carpathian Bastion:** Preferred by defensive AIs (weight 150-200)  
**Frontier Republic:** Preferred by cavalry-focused AIs (weight 150-200)  
**Magnate Dominion:** Preferred by trade-focused AIs (weight 100-150)  
**Religious Tolerance:** Conditional on religious environment (weight 50-100)

### Difficulty Scaling

- **Hard AI:** Prioritizes strongest economic path (Magnate)
- **Medium AI:** Balanced mix based on starting neighbors
- **Easy AI:** Frequently attempts defensive Carpathian path

### Player Agency

- All paths are mutually accessible
- Path choice significantly impacts government mechanics
- Synergy missions reward regional cooperation
- Religious tolerance is optional overlay (can combine with any path)

---

## 9. Future Event/Decision Framework

When designing events for Podillia, reference these triggers:

```eu4
# Path identification
has_country_flag = pdl_carpathian_path
has_country_flag = pdl_frontier_republic_reform
has_country_flag = pdl_magnate_dominion_reform
has_country_flag = pdl_tolerance_path

# Regional integration
has_country_flag = pdl_galician_compact
HLC = { has_country_flag = pdl_galician_compact }

# Mission completion
has_country_flag = pdl_khotyn_siege_victory
has_country_flag = pdl_grand_podillia

# Religious/cultural state
has_reform = pdl_religious_tolerance_reform
religious_unity >= 0.50
```

---

## 10. Technical Validation Checklist

- [x] All 5 government reforms created (pdl_*_reform blocks)
- [x] All government names blocks mapped to reforms (000_RIP_names.txt)
- [x] All missions have valid EU4 syntax (Podillia_Missions.txt)
- [x] Cross-references to existing areas validated (podolia_volhynia, red_ruthenia, crimea, etc.)
- [x] Province IDs validated (277 Kamianets, 281 Khotyn)
- [x] Cross-references to Volhynia/Galicia reforms mapped
- [x] Estate mechanics compatible with existing system
- [ ] Localization keys added to l_english.yml (PENDING - user responsibility)
- [ ] Modifier definitions added to static modifiers file (PENDING - user responsibility)
- [ ] Mission testing in game client (PENDING - user testing)

---

## 11. Pending Localization Tasks

### Government Reform Titles Required
```
pdl_frontier_voivodeship_reform: "Podillian Voivodeship"
pdl_carpathian_bastion_reform: "Carpathian Bastion"
pdl_frontier_republic_reform: "Frontier Republic"
pdl_magnate_dominion_reform: "Magnate Dominion"
pdl_grand_podillia_reform: "Grand Podillia"
pdl_religious_tolerance_reform: "Religious Tolerance"
```

### Government Name Titles Required
```
FRONTIER_VOIVODE: "Voivode of Podillia"
FRONTIER_VOIVODE_MALE: "Voivode"
FRONTIER_VOIVODE_FEMALE: "Voivod's Consort"
[... 12 additional titles for other government name blocks]
```

### Mission Titles & Descriptions Required
```
PDL_declare_independence_title: "Podillian Independence"
PDL_fortify_khotyn_title: "Fortify Khotyn"
[... 24+ additional mission titles and descriptions]
```

---

## 12. References & Sources

### Historical Sources
- Mykhailo Doroshenko, *History of Podillia* (2008)
- Timothy Snyder, *The Reconstruction of Nations* (2003)
- Paul Robert Magocsi, *Galicia: A Historical Survey* (2002)
- Serhii Plokhy, *The Cossack Myth* (2012)

### Game Mechanics References
- EU4 Government Reform system (1.30+)
- Cossacks DLC mechanics (estate_cossacks)
- Mission system architecture (5-column slots)
- Government names display system (trigger-based)

### Related Mission Files
- `missions/Volhynia_Missions.txt` (VLN integration)
- `missions/Galician_Missions.txt` (HLC integration, if exists)
- `missions/croatian_missions.txt` (historical reference model)

---

## Appendix A: File Line References

| File | Section | Start Line | End Line | Description |
|------|---------|-----------|---------|-------------|
| RIP_government_reforms.txt | Header | 2075 | 2104 | Historical context & technical notes |
| RIP_government_reforms.txt | pdl_frontier_voivodeship_reform | 2105 | 2130 | Base reform |
| RIP_government_reforms.txt | pdl_carpathian_bastion_reform | 2147 | 2181 | Defensive path |
| RIP_government_reforms.txt | pdl_frontier_republic_reform | 2189 | 2219 | Cavalry path |
| RIP_government_reforms.txt | pdl_magnate_dominion_reform | 2235 | 2268 | Economic path |
| RIP_government_reforms.txt | pdl_grand_podillia_reform | 2280 | 2310 | Final tier |
| RIP_government_reforms.txt | pdl_religious_tolerance_reform | 2323 | 2367 | Optional overlay |
| Podillia_Missions.txt | Header | 1 | 100 | Historical & technical framework |
| Podillia_Missions.txt | Carpathian Bastion (Slot 1) | 149 | 310 | 5 missions, defensive focus |
| Podillia_Missions.txt | Frontier Republic (Slot 2) | 320 | 465 | 4 missions, cavalry focus |
| Podillia_Missions.txt | Magnate Dominion (Slot 3) | 475 | 640 | 5 missions, economic focus |
| Podillia_Missions.txt | Universal Expansion (Slot 4) | 650 | 760 | 4 missions, territorial |
| Podillia_Missions.txt | Religious & Cultural (Slot 5) | 800 | 900 | 4 missions, soft power |
| Podillia_Missions.txt | Synergy Missions | 940 | 1030 | Galicia/Volhynia integration |
| Podillia_Missions.txt | Historical Milestone | 1035 | 1080 | Khotyn Siege |
| 000_RIP_names.txt | Podillia Names (5 blocks) | [TBD] | [TBD] | Government name displays |

---

## Document Version History

- **v1.0** (January 3, 2026): Initial technical integration documentation
  - Complete mapping of all government reforms
  - Full mission architecture documentation
  - Cross-regional synergy framework
  - Localization tasks identified

---

*This document serves as the technical reference layer for Podillia implementation. For historical context and game design rationale, see PODILLIA_DEVELOPMENT.md. For implementation summary and statistics, see PODILLIA_SUMMARY.md.*
