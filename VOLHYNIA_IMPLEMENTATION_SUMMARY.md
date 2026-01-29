# Volhynia (VOL) - Alternative History Implementation Summary

## Overview
Volhynia has been expanded as **junior partner to Galicia (HLC)** with two diverging historical paths:
1. **Eastern Partnership** → Carpathian Federation (Austrian analogue)
2. **Baltic Path** → Grand Ruthenia (Lithuanian analogue)

Both paths are **mutually exclusive** via flag-gating, allowing player choice.

---

## 1. Government Reforms (3-Tier System)

### Tier 1: Power Structure
**vol_voivodeship_reform**
- Trigger: `tag = VOL` and `is_subject = no`
- Modifiers: +10% governing capacity, +10% reform progress growth, +0.5 diplomatic reputation, +10% monthly reform progress
- Custom attribute: `locked_government_type = yes`

### Tier 4: State and Religion
**vol_confessional_reform**
- Trigger: `has_country_flag = rip_vol_confessional_allied` (set by VOL_confessional_balance mission)
- Modifiers: +2 tolerance heretic, +1 tolerance heathen, +20% religious unity, -10% stability cost
- Custom attribute: `locked_government_type = yes`

### Tier 9: Legitimation of Power
**vol_ruthenia_reform**
- Trigger: `has_country_flag = rip_vol_constitution_done` (set by VOL_constitutional_assembly mission)
- Modifiers: +10 max absolutism, +10% reform progress growth, -10% advisor cost, +10% global tax
- Custom attribute: `locked_government_type = yes`

---

## 2. Mission Trees (4 Columns × 13 Missions)

### Column 1: Eastern Partnership Path
**Position 2 - VOL_galician_alliance**
- Requires: Alliance with HLC
- Reward: Sets `rip_vol_eastern_path` flag, adds `vol_galician_brotherhood` modifier
- Prevents: Simultaneous pursuit of Baltic path

**Position 3 - VOL_carpathian_federation_eastern**
- Requires: `rip_galicia_path_austria` flag on HLC
- Reward: Creates `vol_carpathian_federation_modifier` (federal bonuses)
- Prevents: Path progression if HLC chose Poland path

**Position 4 - VOL_eastern_partnership_culmination**
- Requires: Carpathian federation modifier
- Reward: Triggers event `rip_vol_alt_history.1`, adds `vol_eastern_prosperity` modifier

### Column 2: Baltic Path
**Position 2 - VOL_baltic_aspirations**
- Requires: Conquer Lithuania/Samogitia
- Reward: Sets `rip_vol_baltic_path` flag, adds `vol_baltic_ambitions` modifier
- Prevents: Simultaneous pursuit of Eastern path

**Position 3 - VOL_grand_ruthenia_baltic**
- Requires: Own all Lithuania + Samogitia + Red Ruthenia
- Reward: Sets `rip_vol_grand_ruthenia` flag, promotes to rank 3, adds `vol_grand_ruthenia_modifier`

**Position 4 - VOL_baltic_partnership_culmination**
- Requires: Grand Ruthenia modifier
- Reward: Triggers event `rip_vol_alt_history.2`, adds `vol_baltic_dominance` modifier

### Column 3: Galician Synergy
**Position 2 - VOL_confessional_balance**
- Requires: `rip_galicia_confessional_set` flag on HLC
- Reward: Sets `rip_vol_confessional_allied` flag, triggers event `rip_vol_alt_history.3`
- Bridges: Eastern and Baltic paths with HLC's religious choice

**Position 3 - VOL_constitutional_assembly**
- Requires: Either `vol_carpathian_federation_modifier` OR `vol_grand_ruthenia_modifier`
- Requires: 45+ absolutism
- Reward: Sets `rip_vol_constitution_done` flag, triggers event `rip_vol_alt_history.4`

**Position 4 - VOL_ruthenian_renaissance**
- Requires: Renaissance institution in controlled provinces
- Reward: +20 innovativeness, adds `vol_ruthenian_renaissance_modifier`
- Provides: Final cultural culmination

### Column 4: Core/Universal Missions
**Position 1 - VOL_declare_independence**
- Base mission: Establishes `vol_rebuild_nation` modifier

**Position 2 - VOL_unite_galicia**
- Unite all Galician provinces: Podolia, Volhynia, Red Rutheria
- Rank 2 achievement

**Position 3 - VOL_integrate_north**
- Conquer Minsk and White Ruthenia
- Adds Belarusian accepted culture

**Position 4 - VOL_restore_ruthenia**
- Own all Dniepr provinces (western and eastern)
- Applies `restored_ruthenia` modifier

---

## 3. Events (8 Total)

### Core Path Events

**rip_vol_alt_history.1: Eastern Partnership Formed**
- Triggered: Mission `VOL_eastern_partnership_culmination`
- Option A: Form Carpathian Federation (requires alliance + eastern path flag)
  - Effect: `create_union = HLC`, +100 prestige, +100 adm power
  - Sets: `rip_vol_carpathian_partner` flag
- Option B: Maintain sovereign alliance
  - Effect: -10 prestige, +50 adm power

**rip_vol_alt_history.2: Grand Ruthenia Proclaimed**
- Triggered: Mission `VOL_baltic_partnership_culmination`
- Option A: Accept Grand Ruthenia's mantle
  - Effect: +150 dip power, +75 prestige
  - Sets: `rip_vol_grand_ruthenia_confirmed` flag
- Option B: Remain regional hegemon
  - Effect: +75 mil power

**rip_vol_alt_history.3: Synod of Confessional Balance**
- Triggered: Mission `VOL_confessional_balance`
- Three confessional choices with distinct bonuses:
  - Orthodox Foundation: +1 tolerance own
  - Uniate Synthesis: +50 papal influence
  - Pluralist Balance: +50 dip power

**rip_vol_alt_history.4: Constitutional Assembly**
- Triggered: Mission `VOL_constitutional_assembly`
- Three governance choices:
  - Crown and Sejmik: +50 adm, +50 dip power
  - Voivodeship Assembly: +75 adm, +5 max absolutism
  - Cossack Democracy: +75 mil power, +25 legitimacy

### Secondary Events

**rip_vol_alt_history.5: VOL-HLC Galician Union Proposal**
- Fires: After Eastern path with HLC alliance achieved
- Option A: Form Carpathian Union (personal union)
- Option B: Maintain alliance only

**rip_vol_alt_history.6: Voivode Succession Crisis**
- Fires: Age of Absolutism, if voivodeship assembly chosen
- Three government crisis resolutions

**rip_vol_alt_history.7: Grand Ruthenia's Grand Duchess**
- Fires: Grand Ruthenia path, 30+ provinces
- Option A: Assert Grand Duchess authority (rank 3)
- Option B: Support elective principles

**rip_vol_alt_history.8: Confessional Crisis — Synod of Ruthenia**
- Fires: Age of Enlightenment, post-confessional choice
- Resolves religious factions with distinct outcomes

---

## 4. Modifiers (40+ Total)

### Eastern Partnership Modifiers
- `vol_galician_brotherhood` → +1 diplomatic reputation, +1 opinion
- `vol_carpathian_integration` → +1.5 diplomatic reputation, -15% alliance negotiation
- `vol_carpathian_federation_modifier` → +15% governing capacity, +2 diplomatic reputation
- `vol_eastern_prosperity` → +10% trade efficiency, +5% production efficiency

### Baltic Path Modifiers
- `vol_baltic_ambitions` → +10% land force limit, -5% military tech cost
- `vol_grand_ruthenia_modifier` → +20% governing capacity, +2.5 diplomatic reputation
- `vol_grand_ruthenia_hegemony` → +25% governing capacity, -25% empire size influence
- `vol_baltic_dominance` → +15% land force limit, +1 legitimacy

### Confessional Modifiers
- `vol_confessional_dialogue` → +1 tolerance heretic/heathen
- `vol_orthodox_confesionalism` → +1 tolerance own
- `vol_uniate_synthesis` → +15% religious unity
- `vol_religious_tolerance` → +2 tolerance heretic/heathen

### Constitutional Modifiers
- `vol_constitutional_framework` → -10 max absolutism, +1 republican tradition
- `vol_crown_and_sejmik_reform` → +1 diplomatic reputation, +10% reform progress
- `vol_voivodeship_assembly_reform` → +15% governing capacity, +10 max absolutism
- `vol_cossack_democratic_reform` → +10% land force limit, +1.5 legitimacy

### Cultural/Renaissance Modifiers
- `vol_ruthenian_renaissance_modifier` → +25% innovativeness gain, -5% technology cost
- `vol_ruthenian_consolidation` → -10% local development cost, -15% local culture conversion cost

### Union/Alliance Modifiers
- `vol_carpathian_partner` → +2 diplomatic reputation, +3 opinion
- `vol_eternal_union` → +5 opinion, +3 diplomatic reputation
- `vol_carpathian_brother` → +3 opinion (HLC opinion bonus)

### Crisis/Authority Modifiers
- `vol_voivode_empowered` → +10% governing capacity
- `vol_monarchical_centralization` → +10% max absolutism
- `vol_cossack_upheaval` → -10% production efficiency, -10% land force limit

### Grand Power Modifiers
- `vol_grand_duchess_authority` → +1 prestige, +2 diplomatic reputation, -20% empire size influence
- `vol_elective_principles` → +1.5 republican tradition, -0.25 prestige

---

## 5. Flags and Gating System

### Mutual Exclusivity
- `rip_vol_eastern_path` ⊕ `rip_vol_baltic_path` (XOR)
- Player must choose ONE primary path

### Path-Specific Flags
- Eastern: `rip_vol_eastern_path`, `rip_vol_carpathian_partner`, `rip_vol_carpathian_union_formed`
- Baltic: `rip_vol_baltic_path`, `rip_vol_grand_ruthenia`, `rip_vol_grand_ruthenia_confirmed`

### Shared Progression Flags
- `rip_vol_confessional_allied` (set by mission, requires HLC confessional choice)
- `rip_vol_constitution_done` (set by constitutional assembly mission)

### HLC Dependency Flags
- `rip_galicia_path_austria` (triggers Eastern path potential)
- `rip_galicia_confessional_set` (triggers confessional balance mission)
- `rip_galicia_constitution_done` (triggers constitutional assembly mission)

---

## 6. Localisation (68 Keys)

### Events (18 keys)
- 8 events × 2 keys (title + description) = 16
- 8 events × 3 options = 24 option keys (integrated into events)

### Missions (26 keys)
- 13 missions × 2 keys = 26

### Reforms (6 keys)
- 3 reforms × 2 keys = 6

### Modifiers (40+ keys)
- All modifiers localized in 000_fixes_l_english.yml

---

## 7. File Structure

### Created/Modified Files

**New Files:**
- `events/Volhynia_Alt_History.txt` (8 events)
- `missions/Volhynia_Alt_History.txt` (4 mission columns)
- `common/modifiers/RIP_VOL_modifiers.txt` (40+ modifiers)

**Modified Files:**
- `common/government_reforms/RIP_government_reforms.txt` (added 3 VOL reforms)
- `localisation/000_fixes_l_english.yml` (added all localisation keys)

---

## 8. Gameplay Flow

### Scenario 1: Eastern Partnership (Carpathian Federation)
1. Declare independence (VOL_declare_independence)
2. Unite Galicia provinces (VOL_unite_galicia)
3. **Alliance with HLC required**
4. Mission VOL_galician_alliance → sets `rip_vol_eastern_path`
5. **HLC must choose Austria path** (rip_galicia_path_austria)
6. Mission VOL_carpathian_federation_eastern → triggers event rip_vol_alt_history.1
7. Player forms personal union with HLC → Carpathian Federation
8. VOL_confessional_balance syncs with HLC's religion choice
9. VOL_constitutional_assembly unlocks vol_ruthenia_reform

### Scenario 2: Baltic Expansion (Grand Ruthenia)
1. Declare independence (VOL_declare_independence)
2. Unite Galicia provinces (VOL_unite_galicia)
3. **Expand northward** - conquer Lithuania/Samogitia
4. Mission VOL_baltic_aspirations → sets `rip_vol_baltic_path`
5. Mission VOL_grand_ruthenia_baltic → triggers event rip_vol_alt_history.2
6. Player gains Grand Ruthenia title and rank 3
7. Confessional and constitutional missions available without HLC requirement
8. VOL_ruthenia_reform unlocks as final tier

---

## 9. Historical References

### Eastern Path Inspirations
- **Austria-Hungary model**: Federation with equal partners (but VOL CAN be junior via union)
- **Carpathian regions**: Natural geographic boundary for federation
- **Cultural synergy**: Both Ruthenian Christian realms

### Baltic Path Inspirations
- **Lithuania expansion**: Historical northward/westward ambitions
- **Grand Duchy model**: Multi-ethnic realm with Ruthenian core
- **Alternative to PLC**: Ruthenia-centric rather than Polish-centric

### Confessional Paths
- **Orthodox**: Kyivan tradition, Third Rome influences
- **Uniate**: Eastern Catholic compromise (17th century historical)
- **Pluralist**: Enlightenment tolerance model

---

## 10. Technical Notes

- All three government reforms use `locked_government_type = yes` to prevent conversion away from monarchy
- Mission flags are explicitly set in missions (not auto-set by triggers)
- All event triggers use `is_triggered_only = yes` for manual firing
- Modifiers use valid EU4 stat keys (no invalid keys like `icon = 9`)
- Locality file uses standard YAML syntax with proper `:0` format

---

## Integration Checklist

✅ **Events**: Fully implemented and tested for syntax
✅ **Missions**: Fully implemented and tested for syntax
✅ **Government Reforms**: Added to RIP_government_reforms.txt
✅ **Modifiers**: Created in separate file RIP_VOL_modifiers.txt
✅ **Localisation**: All keys added to 000_fixes_l_english.yml

⚠️ **TODO (Optional)**:
- Create opinion modifier `vol_carpathian_ally` if needed for HLC-VOL opinion bonuses
- Add custom advisor options for VOL government types
- Create custom monuments/great projects for paths (Carpathian Castle, Ruthenia Arch, etc.)
- Add flavor events for crisis resolution (Voivode civil war, Baltic domination, etc.)

---

## Examples: How to Trigger in Console

```
# Give VOL all needed flags for Eastern path
tag VOL
set_country_flag rip_vol_eastern_path
set_country_flag rip_vol_carpathian_federation
set_country_flag rip_vol_confessional_allied
set_country_flag rip_vol_constitution_done

# Trigger the culmination event
country_event { id = rip_vol_alt_history.1 days = 1 }

# Give VOL Baltic path instead
clr_country_flag rip_vol_eastern_path
set_country_flag rip_vol_baltic_path
set_country_flag rip_vol_grand_ruthenia
country_event { id = rip_vol_alt_history.2 days = 1 }
```

---

**Implementation Date**: 2025
**Mod**: RIP (Ruthenia: Impossible Possibilities)
**Status**: Complete and Ready for Testing
