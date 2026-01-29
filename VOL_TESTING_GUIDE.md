# VOL-HLC Synergy System - Testing Guide

## Pre-Game Setup

### Load Mod
1. Enable "RIP" mod in EU4 launcher
2. Start new game with patch 1.36+ (government reforms require modern EU4)

### Initial Conditions
- VOL exists as subject of HLC or independent in 1444
- Verify both tags present in save game (console: `tag VOL`, then `tag HLC`)

---

## Test 1: Eastern Partnership Path

### Test 1A: VOL Independence & Galician Alliance

**Steps:**
1. Start as VOL
2. Use console: `add_liberty_desire -1000` (reduce HLC control if subject)
3. Wait for independence OR declare on HLC with ally support
4. Ally HLC (send alliance offer)
5. Complete VOL_declare_independence mission (baseline position 1)
6. Complete VOL_unite_galicia mission (unite Galicia provinces)

**Verify:**
- [ ] VOL_galician_alliance mission appears in mission tree (position 2)
- [ ] Mission allows if alliance with HLC exists
- [ ] Mission completes on alliance maintenance

**Expected Output:**
```
rip_vol_eastern_path flag SET
vol_galician_brotherhood modifier APPLIED
Mission: VOL_carpathian_federation_eastern UNLOCKED
```

---

### Test 1B: HLC Austria Path Requirements

**Steps:**
1. Control HLC (console: `tag HLC`)
2. Complete VOL_unite_galicia for HLC (triggered from VOL)
3. Trigger event: `country_event { id = rip_galicia.1 days = 1 }`
4. Choose option A: "Raise the Carpathian Shield"

**Verify:**
- [ ] Event appears correctly
- [ ] rip_galicia_path_austria flag SET
- [ ] carpathian_shield modifier applied

**Expected Output:**
```
rip_galicia_path_austria flag SET
HLC gains carpathian_shield modifier
VOL_carpathian_federation_eastern mission BECOMES COMPLETABLE
```

---

### Test 1C: Carpathian Federation Culmination

**Steps:**
1. Tag VOL
2. Complete VOL_carpathian_federation_eastern mission
3. Trigger event: `country_event { id = rip_vol_alt_history.1 days = 1 }`
4. Choose option A: "Form Carpathian Federation"

**Verify:**
- [ ] Event fires and displays correctly
- [ ] Create union command executes
- [ ] rip_vol_carpathian_partner flag SET
- [ ] vol_carpathian_integration modifier applied
- [ ] VOL becomes junior partner of HLC

**Expected Output:**
```
Personal union formed: VOL ← HLC
rip_vol_carpathian_partner flag SET
vol_carpathian_integration modifier: +1.5 diplomatic reputation, -15% alliance negotiation time
HLC opinion: +vol_carpathian_brother modifier (+3)
```

---

## Test 2: Baltic Path (Grand Ruthenia)

### Test 2A: Northward Expansion

**Steps:**
1. Start as VOL
2. Complete independence chain (VOL_declare_independence, VOL_unite_galicia)
3. Expand northward: conquer Minsk (White Ruthenia)
4. Complete VOL_integrate_north mission
5. Expand further: conquer Lithuania proper

**Verify:**
- [ ] VOL_baltic_aspirations mission becomes available (position 2)
- [ ] Mission requires Lithuania/Samogitia in possession
- [ ] Mission triggers on completion

**Expected Output:**
```
rip_vol_baltic_path flag SET
vol_baltic_ambitions modifier: +10% land force limit, -5% military tech cost
Mission: VOL_grand_ruthenia_baltic UNLOCKED
```

---

### Test 2B: Grand Ruthenia Proclamation

**Steps:**
1. Tag VOL, possess: Lithuania, Samogitia, Red Ruthenia, Podolia, Volhynia, Minsk
2. Complete VOL_grand_ruthenia_baltic mission
3. Trigger event: `country_event { id = rip_vol_alt_history.2 days = 1 }`
4. Choose option A: "Accept Grand Ruthenia's mantle"

**Verify:**
- [ ] Event fires correctly
- [ ] rip_vol_grand_ruthenia_confirmed flag SET
- [ ] VOL rank promoted to 3
- [ ] vol_grand_ruthenia_hegemony modifier applied
- [ ] Prestige +75, dip power +150

**Expected Output:**
```
rip_vol_grand_ruthenia_confirmed flag SET
VOL rank: 3 (Great Power)
vol_grand_ruthenia_hegemony modifier: +25% governing capacity, -25% empire size influence
Prestige +75, Dip Power +150
```

---

## Test 3: Confessional Synergy

### Test 3A: HLC Confessional Choice

**Steps:**
1. Tag HLC
2. Establish HLC: complete independence chain with VOL-HLC synergy
3. Wait 24 months MTTH (mean time to happen)
4. Event should fire: `rip_galicia.2`
5. OR force trigger: `country_event { id = rip_galicia.2 days = 1 }`
6. Choose option A: "Hold a Uniate Synod"

**Verify:**
- [ ] rip_galicia_confessional_set flag SET
- [ ] uniate_synod modifier applied (tolerance 2, religious unity +20%)
- [ ] Papal influence affected

**Expected Output:**
```
rip_galicia_confessional_set flag SET
uniate_synod modifier APPLIED
HLC religion effects: tolerance_heretic +2, religious_unity +0.20
```

---

### Test 3B: VOL Confessional Balance Mission

**Steps:**
1. Tag VOL
2. Ensure HLC has: rip_galicia_confessional_set flag + uniate_synod modifier
3. Complete either Eastern path (rip_vol_eastern_path) OR Baltic path (rip_vol_baltic_path)
4. Check mission tree: VOL_confessional_balance (mission column 3, position 2)

**Verify:**
- [ ] Mission appears in tree
- [ ] Trigger: `tag = VOL` + `has_country_flag = rip_galicia_confessional_set`
- [ ] Trigger satisfied with HLC confessional flag

**Expected Output:**
```
Mission available: VOL_confessional_balance
Potential triggers: HLC has rip_galicia_confessional_set flag
Progress: Yes, trigger satisfied
```

---

### Test 3C: Confessional Synod Event

**Steps:**
1. Complete VOL_confessional_balance mission
2. Trigger event: `country_event { id = rip_vol_alt_history.3 days = 1 }`
3. Choose option B: "Uniate Synthesis"

**Verify:**
- [ ] Event fires with all three options
- [ ] Option selected correctly
- [ ] rip_vol_confessional_allied flag SET
- [ ] vol_uniate_synthesis modifier applied

**Expected Output:**
```
rip_vol_alt_history.3 event FIRES
rip_vol_confessional_allied flag SET
vol_uniate_synthesis modifier: +15% religious unity, -5% stability cost
Papal Influence +50
```

---

## Test 4: Constitutional Assembly

### Test 4A: Constitutional Assembly Mission

**Steps:**
1. Tag VOL
2. Complete one of:
   - Eastern path: have vol_carpathian_federation_modifier
   - Baltic path: have vol_grand_ruthenia_modifier
3. Have 45+ absolutism
4. Check mission tree: VOL_constitutional_assembly (position 3, column 3)

**Verify:**
- [ ] Mission available
- [ ] Trigger requirements: `vol_carpathian_federation_modifier OR vol_grand_ruthenia_modifier` AND `absolutism >= 45`
- [ ] Mission can complete

**Expected Output:**
```
Mission available: VOL_constitutional_assembly
Completable: Yes (45 absolutism satisfied, federation/ruthenia modifier present)
Progress bar: Increases daily
```

---

### Test 4B: Constitutional Assembly Event

**Steps:**
1. Complete VOL_constitutional_assembly mission
2. Trigger event: `country_event { id = rip_vol_alt_history.4 days = 1 }`
3. Choose option C: "Cossack Democracy"

**Verify:**
- [ ] Event fires with three options
- [ ] Option selected correctly
- [ ] rip_vol_constitution_done flag SET
- [ ] vol_cossack_democratic_reform modifier applied

**Expected Output:**
```
rip_vol_alt_history.4 event FIRES
rip_vol_constitution_done flag SET
vol_cossack_democratic_reform modifier: +10% land force limit, +1.5 legitimacy, +2 republican tradition
Military Power +75
```

---

## Test 5: Government Reforms Progression

### Test 5A: Tier 1 - VOL Voivodeship Reform

**Steps:**
1. Tag VOL
2. Ensure: independent (is_subject = no), tag = VOL
3. Open government tab
4. Navigate to tier 1 (Power Structure)

**Verify:**
- [ ] vol_voivodeship_reform appears in list
- [ ] Can be selected (no prerequisites beyond government type)
- [ ] Modifiers apply: +10% governing capacity, +10% reform progress growth

**Expected Output:**
```
Government Reform: VOL Voivodeship Reform SELECTABLE
Icon: assembly_hall
Modifiers:
  + 10% governing_capacity
  + 10% reform_progress_growth
  + 0.5 diplomatic_reputation
  + 10% monthly_reform_progress
```

---

### Test 5B: Tier 4 - Confessional Reform

**Steps:**
1. Tag VOL
2. Set flag via console: `set_country_flag rip_vol_confessional_allied`
3. Go to government → tier 4 (State and Religion)

**Verify:**
- [ ] vol_confessional_reform appears in list
- [ ] Trigger satisfied: rip_vol_confessional_allied flag present
- [ ] Can be selected

**Expected Output:**
```
Government Reform: VOL Confessional Compact SELECTABLE
Trigger: has_country_flag = rip_vol_confessional_allied ✓
Icon: holy_state
Modifiers:
  + 2 tolerance_heretic
  + 1 tolerance_heathen
  + 20% religious_unity
  - 10% stability_cost_modifier
```

---

### Test 5C: Tier 9 - Ruthenia Reform (Final)

**Steps:**
1. Tag VOL
2. Set flag: `set_country_flag rip_vol_constitution_done`
3. Go to government → tier 9 (Legitimation of Power)

**Verify:**
- [ ] vol_ruthenia_reform appears in list
- [ ] Trigger satisfied: rip_vol_constitution_done flag present
- [ ] Can be selected

**Expected Output:**
```
Government Reform: VOL Grand Ruthenia's Constitution SELECTABLE
Trigger: has_country_flag = rip_vol_constitution_done ✓
Icon: bureaucracy
Modifiers:
  + 10 max_absolutism
  + 10% reform_progress_growth
  - 10% advisor_cost
  + 10% global_tax_modifier
```

---

## Test 6: Flag Mutual Exclusivity

### Test 6A: Eastern Path Flag Exclusivity

**Steps:**
1. Tag VOL
2. Set flag: `set_country_flag rip_vol_eastern_path`
3. Try to complete VOL_baltic_aspirations mission (position 2, column 2)

**Verify:**
- [ ] Mission is LOCKED or BLOCKED
- [ ] VOL_baltic_aspirations trigger includes: `NOT = { has_country_flag = rip_vol_eastern_path }`
- [ ] Cannot complete both paths simultaneously

**Expected Output:**
```
Mission VOL_baltic_aspirations: BLOCKED
Reason: Has flag rip_vol_eastern_path (mutually exclusive)
Player must complete CLEAR flag operation to switch paths
```

---

### Test 6B: Baltic Path Flag Exclusivity

**Steps:**
1. Tag VOL
2. Set flag: `set_country_flag rip_vol_baltic_path`
3. Try to access VOL_carpathian_federation_eastern mission (position 3, column 1)

**Verify:**
- [ ] Mission is LOCKED or BLOCKED
- [ ] Mission trigger checks: `NOT = { has_country_flag = rip_vol_baltic_path }`
- [ ] Cannot progress Eastern path while Baltic flag set

**Expected Output:**
```
Mission VOL_carpathian_federation_eastern: BLOCKED
Reason: Has flag rip_vol_baltic_path (mutually exclusive)
Player must clear baltic path flag to pursue eastern partnership
```

---

## Test 7: HLC Dependencies

### Test 7A: Austria Path Dependency (Eastern)

**Steps:**
1. Tag HLC
2. Set flag: `set_country_flag rip_galicia_path_poland` (Poland path)
3. Tag VOL
4. Try to complete VOL_carpathian_federation_eastern mission

**Verify:**
- [ ] Mission BLOCKED because HLC chose Poland (not Austria)
- [ ] Mission trigger: `HLC = { has_country_flag = rip_galicia_path_austria }`
- [ ] Mission becomes available only if HLC switches to Austria path

**Expected Output:**
```
Mission VOL_carpathian_federation_eastern: BLOCKED
Reason: HLC does not have rip_galicia_path_austria flag
Requirement: HLC must choose Austria path in rip_galicia.1 event
```

---

### Test 7B: Confessional Flag Dependency

**Steps:**
1. Tag VOL
2. Try to access VOL_confessional_balance mission without HLC confessional flag set

**Verify:**
- [ ] Mission available but trigger NOT satisfied
- [ ] Trigger: `HLC = { has_country_flag = rip_galicia_confessional_set }`
- [ ] Mission shows as "blocked" or "unavailable" in UI

**Expected Output:**
```
Mission VOL_confessional_balance: BLOCKED
Reason: HLC does not have rip_galicia_confessional_set flag
Requirement: HLC must complete confessional choice event (rip_galicia.2)
```

---

## Test 8: Modifier Application & Opinion Effects

### Test 8A: Galician Brotherhood Opinion

**Steps:**
1. Tag VOL
2. Tag HLC
3. Complete VOL_galician_alliance mission
4. Open diplomacy view

**Verify:**
- [ ] vol_galician_brotherhood modifier visible in VOL modifiers tab
- [ ] Opinion change shows: +1 diplomatic reputation
- [ ] HLC's opinion of VOL improves (if using dynamic opinion system)

**Expected Output:**
```
VOL Modifiers: vol_galician_brotherhood (Galician Brotherhood)
  + 1 diplomatic_reputation
  + 1 opinion
HLC Opinion of VOL: Baseline + 1 point
```

---

### Test 8B: Eternal Union Opinion (Post-Federation)

**Steps:**
1. Tag VOL
2. Form Carpathian Federation (complete path through event 1)
3. Set modifier: `add_country_modifier { name = vol_eternal_union duration = -1 }`
4. Check diplomacy: HLC opinion of VOL

**Verify:**
- [ ] vol_eternal_union modifier visible
- [ ] Opinion bonus: +5 opinion (static), +3 diplomatic reputation
- [ ] Alliance negotiation: -25% time
- [ ] Marriage options should improve (if applicable)

**Expected Output:**
```
VOL Modifiers: vol_eternal_union (Eternal Union)
  + 5 opinion
  + 3 diplomatic_reputation
  - 25% alliance_negotiation_time
HLC Opinion: +5 points permanent (as long as modifier active)
```

---

## Test 9: Modifier Conflicts & Layering

### Test 9A: Confessional Modifier Layering

**Steps:**
1. Set VOL: `add_country_modifier { name = vol_orthodox_confesionalism duration = -1 }`
2. Set VOL: `add_country_modifier { name = vol_uniate_synthesis duration = -1 }`

**Verify:**
- [ ] Both modifiers stack (no replacement)
- [ ] Combined effects: tolerance_own +1 + religious_unity +15%
- [ ] No stability cost overlaps

**Expected Output:**
```
VOL Modifiers:
  1. vol_orthodox_confesionalism: tolerance_own +1
  2. vol_uniate_synthesis: religious_unity +15%
Combined: tolerance_own +1, religious_unity +15%
```

---

### Test 9B: Constitutional Modifier Isolation

**Steps:**
1. Set VOL: `add_country_modifier { name = vol_crown_and_sejmik_reform duration = -1 }`
2. Try to set VOL: `add_country_modifier { name = vol_cossack_democratic_reform duration = -1 }`

**Verify:**
- [ ] Both modifiers apply (no mutual exclusion)
- [ ] Effects stack: adm +50, dip +50, mil +75
- [ ] max_absolutism +5 from first, legitimacy +1.5 + republican +2 from second

**Expected Output:**
```
VOL Modifiers:
  1. vol_crown_and_sejmik_reform
  2. vol_cossack_democratic_reform
Combined Bonuses (stacked):
  Administrative Power generation (mod 1)
  Diplomatic Power generation (mod 1)
  Military Power generation (mod 2)
  Legitimacy +1.5 (mod 2)
  Republican Tradition +2 (mod 2)
```

---

## Test 10: Event Triggers & Conditions

### Test 10A: Event Trigger Verification

**Steps for rip_vol_alt_history.1:**
1. Verify event exists: grep for `id = rip_vol_alt_history.1`
2. Check trigger: `is_triggered_only = yes`
3. Check options count: 2 options (Form Federation, Maintain Alliance)

**Steps for rip_vol_alt_history.3:**
1. Verify event trigger conditions
2. Check option conditions: Each option has distinct triggers/effects
3. Verify localisation keys exist

**Verify:**
- [ ] All 8 events (rip_vol_alt_history.1-8) exist
- [ ] All events have `is_triggered_only = yes`
- [ ] All events have minimum 2 options
- [ ] All localisation keys defined

**Expected Output:**
```
Events verified:
  rip_vol_alt_history.1: 2 options (Federation, Alliance)
  rip_vol_alt_history.2: 2 options (Accept, Remain regional)
  rip_vol_alt_history.3: 3 options (Orthodox, Uniate, Pluralist)
  rip_vol_alt_history.4: 3 options (Crown, Voivodeship, Cossack)
  rip_vol_alt_history.5: 2 options (Union, Alliance)
  rip_vol_alt_history.6: 3 options (Empower, Centralize, Uprising)
  rip_vol_alt_history.7: 2 options (Duchess, Elective)
  rip_vol_alt_history.8: 3 options (Orthodox, Uniate, Tolerance)
All localisation keys DEFINED
```

---

## Integration Tests

### Test 11A: Mod Loads Without Errors

**Steps:**
1. Enable RIP mod in launcher
2. Load mod in EU4
3. Start new game
4. Console: `errors`
5. Filter for VOL or Volhynia errors

**Verify:**
- [ ] No syntax errors in VOL files
- [ ] No missing localisation keys for VOL items
- [ ] No missing modifier references

**Expected Output:**
```
VOL-related errors: 0
Missions load: ✓
Events load: ✓
Reforms load: ✓
Modifiers load: ✓
Localisation load: ✓
```

---

### Test 11B: Mission Tree Visualization

**Steps:**
1. Start as VOL or load VOL
2. Open mission tree (F1)
3. Select "VOL Missions" filter (if available)
4. Inspect all 4 columns

**Verify:**
- [ ] All 13 missions visible
- [ ] Column 1 (Eastern): 3 missions visible
- [ ] Column 2 (Baltic): 3 missions visible
- [ ] Column 3 (Synergy): 3 missions visible
- [ ] Column 4 (Core): 4 missions visible
- [ ] Connections/arrows between missions show correctly
- [ ] Mission positions (1-4) match expected layout

**Expected Output:**
```
Mission Tree Visualization:
Column 1 (Eastern Partnership): VOL_galician_alliance → VOL_carpathian_federation_eastern → VOL_eastern_partnership_culmination
Column 2 (Baltic Path): VOL_baltic_aspirations → VOL_grand_ruthenia_baltic → VOL_baltic_partnership_culmination
Column 3 (Synergy): VOL_confessional_balance → VOL_constitutional_assembly → VOL_ruthenian_renaissance
Column 4 (Core): VOL_declare_independence → VOL_unite_galicia → VOL_integrate_north → VOL_restore_ruthenia
```

---

## Performance Tests

### Test 12A: Flag Operations Performance

**Steps:**
1. Create save at 1444
2. Set 50 VOL flags simultaneously: `set_country_flag rip_vol_test_flag_1..50`
3. Measure save/load time
4. Check for lag spike

**Verify:**
- [ ] No lag spike
- [ ] Save game loads successfully
- [ ] Flag operations execute without delay

**Expected Output:**
```
50 flags set in <1 second
Save game loads: <2 seconds additional (normal)
No game lag observed
```

---

### Test 12B: Modifier Calculation Performance

**Steps:**
1. Apply all 40+ VOL modifiers simultaneously
2. Check government reform screen (re-calculates bonuses)
3. Measure UI responsiveness

**Verify:**
- [ ] UI remains responsive
- [ ] Tooltips load quickly (<1 second)
- [ ] No graphical glitches

**Expected Output:**
```
40+ modifiers applied: No lag
UI response time: <500ms
Tooltips load instantly
```

---

## Balance Validation Tests

### Test 13A: Modifier Power Levels

**Steps:**
1. Compare VOL modifiers to HLC modifiers
2. Check if bonuses are proportional/balanced
3. Compare to vanilla EU4 standard modifiers

**Verify:**
- [ ] No single modifier provides >20% bonus to any stat (except niche ones)
- [ ] Stacking limitations prevent "degenerate" builds
- [ ] Total bonuses align with great power standards

**Expected Output:**
```
VOL Modifiers Balance:
  Individual cap: <20% most bonuses
  Combined cap: <50% (for any single stat)
  Comparable to: HLC modifiers, vanilla great power reformations
  Balance: ✓ ACCEPTABLE
```

---

### Test 13B: Path Viability Comparison

**Steps:**
1. Test Eastern path playthrough (Carpathian Federation)
2. Test Baltic path playthrough (Grand Ruthenia)
3. Compare final power levels at 1700

**Verify:**
- [ ] Eastern path achieves rank 2-3 power level
- [ ] Baltic path achieves rank 3 power level
- [ ] Neither path is clearly dominant
- [ ] Both paths offer distinct advantages

**Expected Output:**
```
Eastern Path (Carpathian Federation):
  Final Rank: 2-3 (depends on HLC growth)
  Territory: Carpathians + Dniepr + Eastern Europe
  Strategy: Defensive federation, diplomatic bonuses

Baltic Path (Grand Ruthenia):
  Final Rank: 3 (independent)
  Territory: Ruthenia + Lithuania + White Rutheria
  Strategy: Offensive expansion, cultural dominance

Viability: EQUAL (both paths viable)
```

---

## Troubleshooting Guide

### Issue: Event Doesn't Fire
**Diagnosis:**
- Check flag prerequisites: `set_country_flag` for all required flags
- Check trigger conditions: Ensure alliance, territory, government type met
- Force trigger: `country_event { id = rip_vol_alt_history.1 days = 1 }`

### Issue: Mission Doesn't Appear
**Diagnosis:**
- Check mutual exclusivity flags blocking it
- Verify prerequisite mission completed
- Check government type (must be monarchy)
- Force mission: Reload government reforms (switch to different reform, switch back)

### Issue: Modifier Not Applying
**Diagnosis:**
- Check modifier name spelling (case-sensitive)
- Verify modifier file loads (check errors)
- Check duration: -1 means permanent, positive number = days
- Force apply: `add_country_modifier { name = vol_* duration = -1 }`

### Issue: Union Not Forming
**Diagnosis:**
- Check HLC existence: `exists = HLC`
- Check diplomatic relationship: Verify alliance active
- Check personal union limit: VOL might already be in union
- Force union: `create_union = HLC`

---

## Regression Testing Checklist

Before each mod update:
- [ ] All 13 missions load without syntax errors
- [ ] All 8 events fire correctly when triggered
- [ ] All 3 government reforms selectable with proper triggers
- [ ] All 40+ modifiers apply without conflicts
- [ ] No missing localisation keys
- [ ] HLC integration unbroken (test VOL-HLC dependency chains)
- [ ] Flag mutual exclusivity working
- [ ] Opinion modifiers stacking correctly
- [ ] Performance acceptable (<500ms UI response)
- [ ] Balance unbroken (no path clearly overpowered)

---

**Testing Checklist Version:** 1.0
**Last Updated:** 2025
**Mod:** RIP (Ruthenia: Impossible Possibilities)
