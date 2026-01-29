# PODILLIA SYSTEM - QUICK REFERENCE MAP

**Purpose:** Quick lookup guide for Podillia implementation files and their relationships

---

## File Structure Overview

```
RIP Mod/
├── common/
│   ├── government_reforms/
│   │   └── RIP_government_reforms.txt     [5 Podillia reforms + 10 Volhynia reforms added]
│   │       └── Lines 2075-2370: PODILLIA GOVERNMENT SYSTEM
│   │
│   └── government_names/
│       └── 000_RIP_names.txt              [15 Podillia titles + 30 Volhynia titles added]
│           └── Podillia name blocks (5) linked to reforms
│
├── missions/
│   └── Podillia_Missions.txt               [27 missions, 1088 lines, NEW FILE]
│       ├── Slot 1: Carpathian Bastion (5 missions)
│       ├── Slot 2: Frontier Republic (4 missions)
│       ├── Slot 3: Magnate Dominion (5 missions)
│       ├── Slot 4: Universal Expansion (4 missions)
│       ├── Slot 5: Religious & Cultural (4 missions)
│       ├── Synergy Missions (Galicia/Volhynia)
│       └── Historical Milestone (Khotyn Siege)
│
├── localisation/
│   └── [l_english.yml]                    [47 keys to be added - SEE SECTION 11]
│
└── [Documentation Files]
    ├── PODILLIA_TECHNICAL_INTEGRATION.md  [600 lines - technical reference]
    ├── PODILLIA_DEVELOPMENT.md            [1,200+ lines - historical/design context]
    ├── PODILLIA_SUMMARY.md                [500+ lines - executive summary]
    └── PODILLIA_COMPLETION_REPORT.md      [This report]
```

---

## Cross-Reference Matrix

### Government Reforms ↔ Government Names

| Reform | Reform File | Lines | Government Names File | Names Block | Lines |
|--------|-------------|-------|----------------------|------------|-------|
| pdl_frontier_voivodeship_reform | RIP_govt_reforms | 2105-2130 | 000_RIP_names | pdl_frontier_voivodeship | [TBD] |
| pdl_carpathian_bastion_reform | RIP_govt_reforms | 2147-2181 | 000_RIP_names | pdl_carpathian_bastion | [TBD] |
| pdl_frontier_republic_reform | RIP_govt_reforms | 2189-2219 | 000_RIP_names | pdl_frontier_republic | [TBD] |
| pdl_magnate_dominion_reform | RIP_govt_reforms | 2235-2268 | 000_RIP_names | pdl_magnate_dominion | [TBD] |
| pdl_grand_podillia_reform | RIP_govt_reforms | 2280-2310 | 000_RIP_names | pdl_grand_podillia | [TBD] |
| pdl_religious_tolerance_reform | RIP_govt_reforms | 2323-2367 | 000_RIP_names | [overlay] | [TBD] |

### Missions ↔ Government Reforms

| Mission Path | Mission File | Lines | Unlocks Reform | Reform Lines |
|---------|----------|-------|--------|------|
| Carpathian Bastion (Slot 1, Pos 1-5) | Podillia | 149-310 | pdl_carpathian_bastion | 2147-2181 |
| Frontier Republic (Slot 2, Pos 1-4) | Podillia | 333-470 | pdl_frontier_republic | 2189-2219 |
| Magnate Dominion (Slot 3, Pos 1-5) | Podillia | 492-640 | pdl_magnate_dominion | 2235-2268 |
| Universal Expansion (Slot 4, Pos 1-4) | Podillia | 657-760 | pdl_grand_podillia | 2280-2310 |
| Religious & Cultural (Slot 5, Pos 1-4) | Podillia | 805-900 | pdl_religious_tolerance | 2323-2367 |

---

## Trigger Chain Architecture

```
Mission Completion
    ↓
Set Country Flag
    ↓
Trigger Government Reform Adoption
    ↓
Government_names Block Activated
    ↓
Ruler Title Changed (Rank 1-3)
```

### Example: Carpathian Bastion Path

```
Mission: PDL_fortify_khotyn (Slot 1, Position 2)
    Effect: set_country_flag = pdl_carpathian_path
             add_prestige = 10
    ↓
Player Adopts Government Reform
    Trigger: has_country_flag = pdl_carpathian_path (from mission)
    ↓
PDL_carpathian_bastion_reform Becomes Available
    Name Block: pdl_carpathian_bastion
    ↓
Government Titles Display
    Rank 1: FORT_CAPTAIN
    Rank 2: GARRISON_COMMANDER
    Rank 3: BASTION_VOIVODE
```

---

## Dependency Graph

```
PDL Independence
    ↓
PDL_declare_independence (Slot 1, Pos 1)
    ↓ (Split into 5 paths)
    ├─→ Carpathian Bastion Path (Slot 1, Pos 2-5)
    │   └─→ pdl_carpathian_bastion_reform
    │       └─→ pdl_carpathian_bastion government names
    │
    ├─→ Frontier Republic Path (Slot 2, Pos 1-4)
    │   └─→ pdl_frontier_republic_reform
    │       └─→ pdl_frontier_republic government names
    │
    ├─→ Magnate Dominion Path (Slot 3, Pos 1-5)
    │   └─→ pdl_magnate_dominion_reform
    │       └─→ pdl_magnate_dominion government names
    │
    ├─→ Universal Expansion (Slot 4, Pos 1-4)
    │   └─→ pdl_grand_podillia_reform
    │       └─→ pdl_grand_podillia government names
    │
    └─→ Religious & Cultural Path (Slot 5, Pos 1-4)
        └─→ pdl_religious_tolerance_reform
            └─→ [overlay - no dedicated names]
```

---

## Government Reform Modifier Effects Summary

### pdl_frontier_voivodeship_reform (Base)
```
+ governing_capacity_modifier: 0.15
+ reform_progress_growth: 0.15
- state_maintenance_modifier: -0.10
+ diplomatic_reputation: 0.5
- global_unrest: -1
```

### pdl_carpathian_bastion_reform (Defense Path)
```
- fort_maintenance_modifier: -0.20
+ defensiveness: 0.25
+ garrison_size: 0.20
- army_tradition_decay: -0.01
+ hostile_attrition: 1.5
```

### pdl_frontier_republic_reform (Cavalry Path)
```
- cavalry_cost: -0.15
+ cavalry_flanking: 0.25
+ land_forcelimit: 0.15
- mil_tech_cost_modifier: -0.05
+ army_tradition: 0.25
Ability: cossacks_mechanic
```

### pdl_magnate_dominion_reform (Economic Path)
```
+ global_tax_modifier: 0.15
+ trade_efficiency: 0.15
+ governing_capacity_modifier: 0.20
+ merchants: 1
+ burghers_influence_modifier: 0.15
+ nobles_influence_modifier: 0.10
+ max_absolutism: 15
Estate Allocation: 25%
```

### pdl_grand_podillia_reform (Final Tier)
```
+ prestige: 2
- stability_cost_modifier: -0.15
+ diplomatic_reputation: 1
+ max_absolutism: 20
+ reform_progress_growth: 0.10
+ global_manpower_modifier: 0.10
```

### pdl_religious_tolerance_reform (Optional Overlay)
```
+ tolerance_heretic: 2
+ tolerance_heathen: 1
+ religious_unity: 0.25
- stability_cost_modifier: -0.15
- missionary_maintenance_cost: -0.25
+ global_missionary_strength: 0.02
```

---

## Mission Statistics by Slot

| Slot | Path | # Missions | Primary Mechanic | Reform Unlocked | DLC Requirement |
|------|------|-----------|-----------------|-----------------|-----------------|
| 1 | Carpathian Bastion | 5 | Garrison/Fort | pdl_carpathian | None |
| 2 | Frontier Republic | 4 | Cavalry/Cossack | pdl_frontier_republic | Cossacks |
| 3 | Magnate Dominion | 5 | Trade/Noble | pdl_magnate_dominion | Common Sense |
| 4 | Universal Expansion | 4 | Conquest | pdl_grand_podillia | None |
| 5 | Religious & Cultural | 4 | Tolerance/Culture | pdl_religious_tolerance | Humanism |
| Synergy | Galicia Integration | 2 | Diplomacy | N/A | None |
| Synergy | Volhynia Trade | 1 | Trade | N/A | None |
| Special | Khotyn Siege | 1 | Military | N/A | None |

---

## Historical Model Mapping

```
Carpathian Bastion (Slot 1)
    Historical Model: Croatian Fortifications
    Game System: Fort maintenance + garrison culture
    Key Mechanic: defensiveness, fort_maintenance_modifier
    Government Reform: pdl_carpathian_bastion_reform

Frontier Republic (Slot 2)
    Historical Model: Cossack Host / Lithuanian Cavalry
    Game System: Estate cossacks + cavalry mechanics
    Key Mechanic: cavalry_flanking, cossacks_mechanic
    Government Reform: pdl_frontier_republic_reform

Magnate Dominion (Slot 3)
    Historical Model: Mazovian Noble Autonomy
    Game System: Estate autonomy + trade power
    Key Mechanic: trade_efficiency, noble influence
    Government Reform: pdl_magnate_dominion_reform

Universal Expansion (Slot 4)
    Historical Model: Regional Hegemony (Ruthenian Dominance)
    Game System: Territorial conquest + administrative control
    Key Mechanic: prestige, max_absolutism
    Government Reform: pdl_grand_podillia_reform

Religious Tolerance (Slot 5)
    Historical Model: Confessional Balance (Ruthenian Uniqueness)
    Game System: Religious tolerance + diversity mechanics
    Key Mechanic: tolerance mechanics, religious_unity
    Government Reform: pdl_religious_tolerance_reform
```

---

## Synergy Missions

### Galicia (HLC) Integration
```
PDL_galician_compact (Slot 1, Pos 3)
    Trigger: HLC exists, is independent
    Effect: Prestige, flag set
    ↓
PDL_trade_corridor (Slot 1, Pos 4)
    Trigger: PDL_galician_compact completed
    Effect: Trade efficiency with Galicia
```

### Volhynia (VLN) Integration
- pdl_trade_corridor mission references VLN trade synergy
- Cavalry path (Slot 2) synergizes with vln_cossack_host_reform
- Government path (Slot 3) synergizes with hlc_crown_and_sejm_reform

---

## AI Weight Priority System

```
pdl_frontier_voivodeship_reform:  10 (always adopt as base)
PDL_declare_independence mission: 150+ (highest priority)

Path Priorities:
├─ Carpathian Bastion:  150-200 (high for threatened AI)
├─ Frontier Republic:   150-200 (high for cavalry-focused AI)
├─ Magnate Dominion:    100-150 (medium-high for economic AI)
└─ Religious Tolerance: 50-100 (conditional on religion)

Final Tier:
└─ pdl_grand_podillia: 10 (highest priority late-game)
```

---

## Localization Keys Inventory

### Government Reform Names (6 keys)
```
pdl_frontier_voivodeship_reform
pdl_carpathian_bastion_reform
pdl_frontier_republic_reform
pdl_magnate_dominion_reform
pdl_grand_podillia_reform
pdl_religious_tolerance_reform
```

### Government Titles (15 keys)
```
FRONTIER_VOIVODE, FRONTIER_VOIVODE_MALE, FRONTIER_VOIVODE_FEMALE
FORT_CAPTAIN, GARRISON_COMMANDER, BASTION_VOIVODE
HOST_VOIVODE, HETMAN_VOIVODE, HOST_COMMANDER
MAGNATE_DUKE, MAGNATE_KING, AUTONOMOUS_VOIVODE
GRAND_VOIVODE, GRAND_KING, PODILLIAN_EMPEROR
```

### Mission Titles (27 keys)
```
PDL_declare_independence_title
PDL_fortify_khotyn_title
[... 25 more mission titles]
```

### Mission Descriptions (27 keys)
```
PDL_declare_independence_desc
PDL_fortify_khotyn_desc
[... 25 more mission descriptions]
```

### Modifier Names (varies)
```
pdl_khotyn_fortress
pdl_garrison_tradition
pdl_ottoman_resistance
pdl_steppe_masters
[... etc]
```

---

## Related Files & Systems

### Volhynia Integration
- **File:** `missions/Volhynia_Missions.txt`
- **Cross-References:** 5 government names blocks for vln_* reforms
- **Synergies:** PDL trade corridors, shared military traditions

### Galicia Integration
- **File:** `missions/Galician_Missions.txt` (if exists)
- **Cross-References:** hlc_crown_and_sejm_reform compatibility
- **Synergies:** Red Ruthenia conquest, magnate cooperation

### Estate System
- **Cossacks Estate:** Active in pdl_frontier_republic_reform
- **Nobility Estate:** Active in pdl_magnate_dominion_reform
- **Reference:** Common Sense DLC mechanics

### Area System
- **podolia_volhynia_area:** Primary claim target
- **red_ruthenia_area:** Secondary expansion target
- **crimea_area:** Cavalry raid targets
- **west_dniepr_area:** Eastern expansion target

---

## Common Issues & Solutions

### Issue: Government Names Not Displaying
**Cause:** Government reform triggers not matching mission flags  
**Solution:** Verify `has_reform = [reform_name]` matches reform definition name  
**Reference:** PODILLIA_TECHNICAL_INTEGRATION.md Section 2

### Issue: Missions Not Appearing
**Cause:** potential = { tag = PDL } condition not met  
**Solution:** Play as PDL, check NOT = { map_setup = map_setup_random }  
**Reference:** Podillia_Missions.txt header

### Issue: Modifiers Not Applied
**Cause:** Modifier names don't match declaration  
**Solution:** Check modifier spelling in missions vs. static modifiers file  
**Reference:** PODILLIA_TECHNICAL_INTEGRATION.md Section 5

### Issue: Localization Errors
**Cause:** Missing l_english.yml keys  
**Solution:** Add all 47 keys from PODILLIA_TECHNICAL_INTEGRATION.md Section 11  
**Reference:** Section 11 has complete key list

---

## Testing Checklist

```
□ Launch game as PDL
□ Verify PDL_declare_independence appears
□ Complete mission → check if reforms available
□ Select government reform → verify titles change
□ Check AI adoption of different paths
□ Test Volhynia/Galicia synergies
□ Verify modifier stacking
□ Test all 5 mission paths to completion
□ Check cross-regional trade effects
□ Verify no conflicts with existing systems
```

---

## Version Control References

- **Main Implementation:** January 3, 2026
- **Files Modified:** 3 (reforms, names, missions)
- **Files Created:** 4 (missions + 3 documentation)
- **Total Lines Added:** ~4,540
- **Status:** Production-ready (pending localization)

---

## Quick Links

1. **Technical Details:** PODILLIA_TECHNICAL_INTEGRATION.md
2. **Historical Context:** PODILLIA_DEVELOPMENT.md
3. **Executive Summary:** PODILLIA_SUMMARY.md
4. **This Completion Report:** PODILLIA_COMPLETION_REPORT.md
5. **Mission Code:** missions/Podillia_Missions.txt
6. **Reforms:** common/government_reforms/RIP_government_reforms.txt (Lines 2075-2370)
7. **Names:** common/government_names/000_RIP_names.txt

---

**Last Updated:** January 3, 2026  
**Next Step:** Add 47 localization keys to l_english.yml  
**Estimated Time:** 30-45 minutes for full localization
