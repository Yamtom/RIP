# Volhynia (VOL) - Quick Start Guide

## What Was Created?

### For Players
1. **Two alternative history paths for Volhynia:**
   - 🏔️ **Eastern Partnership** → Carpathian Federation (allies with Galicia)
   - 🏛️ **Baltic Path** → Grand Ruthenia (expands north to become great power)

2. **13 new missions** organized in 4 mission columns
3. **8 new events** with meaningful choices that unlock government reforms
4. **3 new government reforms** (Tiers 1, 4, 9 of monarchy system)
5. **40+ modifiers** providing bonuses for each path choice

### For Modders
1. **Complete mission architecture** showing path-gating via flags
2. **Event-driven progression system** for government reform unlocks
3. **HLC-VOL synergy mechanics** demonstrating multi-nation cooperation
4. **Balanced flag system** preventing overpowered combinations

---

## Files Created/Modified

### New Files
| File | Purpose | Size |
|------|---------|------|
| `events/Volhynia_Alt_History.txt` | 8 events for paths | ~400 lines |
| `missions/Volhynia_Alt_History.txt` | 13 missions in 4 columns | Already exists |
| `common/modifiers/RIP_VOL_modifiers.txt` | 40+ modifiers | ~300 lines |
| `VOLHYNIA_IMPLEMENTATION_SUMMARY.md` | Technical documentation | ~500 lines |
| `VOL_HLC_SYNERGY_SYSTEM.md` | Design & mechanics docs | ~700 lines |
| `VOL_TESTING_GUIDE.md` | Testing & troubleshooting | ~600 lines |

### Modified Files
| File | Changes | Lines |
|------|---------|-------|
| `common/government_reforms/RIP_government_reforms.txt` | Added 3 VOL reforms | 787-859 |
| `localisation/000_fixes_l_english.yml` | Added 70+ loc keys | 1-300 |

---

## Quick Game Flow

### Path 1: Eastern Partnership (Carpathian Federation)
```
1. VOL_declare_independence 
   ↓ (independence achieved)
2. VOL_unite_galicia 
   ↓ (Galicia united under VOL)
3. VOL_galician_alliance 
   ↓ (alliance with HLC required)
   🚩 Sets: rip_vol_eastern_path flag
   ⚙️ Adds: vol_galician_brotherhood modifier
4. VOL_carpathian_federation_eastern
   ↓ (HLC must have rip_galicia_path_austria flag)
   📢 Event: rip_vol_alt_history.1
   ↓ (Choose: Form Carpathian Federation)
5. VOL_confessional_balance (optional, synergy)
   ↓ (HLC's confessional choice matters)
   📢 Event: rip_vol_alt_history.3
6. VOL_constitutional_assembly
   ↓ (choose: Crown & Sejmik / Voivodeship / Cossack)
   📢 Event: rip_vol_alt_history.4
   🚩 Sets: rip_vol_constitution_done flag
7. Unlock vol_ruthenia_reform (Tier 9)

RESULT: Carpathian Federation (VOL junior to HLC)
```

### Path 2: Baltic Expansion (Grand Ruthenia)
```
1. VOL_declare_independence
   ↓ (independence achieved)
2. VOL_unite_galicia
   ↓ (Galicia united)
3. VOL_integrate_north
   ↓ (conquer Minsk, White Rutheria)
4. VOL_baltic_aspirations
   ↓ (conquer Lithuania/Samogitia)
   🚩 Sets: rip_vol_baltic_path flag
   ⚙️ Adds: vol_baltic_ambitions modifier
5. VOL_grand_ruthenia_baltic
   ↓ (all Ruthenia + Lithuania owned)
   📢 Event: rip_vol_alt_history.2
   ↓ (Choose: Accept Grand Ruthenia)
6. VOL_confessional_balance (optional, independent)
   ↓ (can choose freely, no HLC dependency)
   📢 Event: rip_vol_alt_history.3
7. VOL_constitutional_assembly
   ↓ (choose government type)
   📢 Event: rip_vol_alt_history.4
8. Unlock vol_ruthenia_reform (Tier 9)

RESULT: Grand Ruthenia (VOL independent great power)
```

---

## Government Reforms Unlocked

### Tier 1: Power Structure
**vol_voivodeship_reform**
- No prerequisites, available immediately
- **Bonus:** +10% governing capacity, +10% reform progress
- **Flavor:** Voivodes become formal governing body

### Tier 4: State & Religion
**vol_confessional_reform**
- Requires: `rip_vol_confessional_allied` flag (from event)
- **Bonus:** +2 tolerance heretic, +20% religious unity
- **Flavor:** Religious balance between Orthodox/Uniate/Catholic

### Tier 9: Legitimation of Power
**vol_ruthenia_reform**
- Requires: `rip_vol_constitution_done` flag (from event)
- **Bonus:** +10 max absolutism, +10% tax modifier
- **Flavor:** Constitutional framework for Grand Ruthenia

---

## Key Mechanics

### 🚩 Flags (Mutually Exclusive)
```
rip_vol_eastern_path  ⊕  rip_vol_baltic_path
    ↓                           ↓
Cannot use both!        Choose ONE path
```

### ⚙️ Modifiers (Stackable)
- 40+ distinct modifiers tied to missions
- Each path has unique modifiers
- Can stack modifiers (e.g., confessional + constitutional)

### 🌐 HLC Dependency
| HLC Flag | VOL Effect |
|----------|-----------|
| `rip_galicia_path_austria` | Unlocks Carpathian federation path |
| `rip_galicia_confessional_set` | Enables confessional balance mission |
| `rip_galicia_constitution_done` | Opens government reform options |

### 👥 Opinion System
- **vol_galician_brotherhood**: +1 diplomatic rep, +1 opinion
- **vol_eternal_union**: +5 opinion, -25% alliance negotiation time
- **vol_carpathian_brother**: HLC gets +3 opinion bonus

---

## Event Choices Matter

### Event 1: Eastern Partnership Formed
**Option A: Form Carpathian Federation**
- ✅ VOL joins HLC as personal union
- ✅ Unified government policy
- ✅ Shared territory benefits
- ❌ VOL is junior (depends on HLC)

**Option B: Remain Sovereign Allies**
- ✅ Independence preserved
- ❌ Loses federation bonuses
- ❌ Must pursue Baltic path instead

### Event 3: Confessional Choice
**3 independent choices:**
1. **Orthodox Foundation** (if HLC Orthodox)
2. **Uniate Synthesis** (if HLC Uniate)
3. **Pluralist Balance** (any HLC choice)

### Event 4: Constitutional Framework
**3 governance models:**
1. **Crown & Sejmik** (Polish model) → +diplomacy
2. **Voivodeship Assembly** (Hungarian model) → +administration
3. **Cossack Democracy** (radical model) → +military power

---

## Balance Notes

### Why Mutually Exclusive Paths?
- Prevents "dominant megastate" (VOL + full HLC control)
- Creates distinct playstyles
- Encourages replayability

### Why HLC Dependencies?
- Rewards VOL-HLC interaction
- Simulates geopolitical constraints
- Makes VOL development logical (not isolated)

### Why Multiple Confessional/Constitutional Options?
- Different historical traditions
- Player choice matters (not forced outcome)
- Replayable with different builds

---

## Localisation Status

✅ **Fully localized** in English:
- 8 events (18 keys: titles + descriptions)
- 13 missions (26 keys: titles + descriptions)
- 3 government reforms (6 keys)
- 40+ modifiers (with descriptions)
- 68+ total localisation keys added

🌍 **Ready for translation** to other languages

---

## Console Commands for Testing

### Give flags for Eastern path:
```
set_country_flag rip_vol_eastern_path
set_country_flag rip_vol_confessional_allied
set_country_flag rip_vol_constitution_done
```

### Give flags for Baltic path:
```
set_country_flag rip_vol_baltic_path
set_country_flag rip_vol_grand_ruthenia
set_country_flag rip_vol_constitution_done
```

### Force trigger events:
```
country_event { id = rip_vol_alt_history.1 days = 1 }
country_event { id = rip_vol_alt_history.3 days = 1 }
country_event { id = rip_vol_alt_history.4 days = 1 }
```

### Add modifiers:
```
add_country_modifier { name = vol_carpathian_federation_modifier duration = -1 }
add_country_modifier { name = vol_grand_ruthenia_modifier duration = -1 }
```

---

## Known Limitations

1. **Events are triggered manually** via missions (not automatic)
   - Solution: Always complete missions to progress
   
2. **No AI behavior** for path choices
   - Solution: AI VOL may not utilize paths effectively
   - Future: Add AI priority weights in event options
   
3. **Union formation requires careful timing**
   - Solution: Test union in console first
   - Future: Add fail-safe alternative path

4. **No integration with other mods**
   - Solution: RIP mod is self-contained
   - Future: Ensure compatibility with major overhauls

---

## Troubleshooting

### Mission doesn't appear?
- Check mutual exclusivity flag
- Verify prerequisite mission complete
- Ensure tag is VOL (not HLC or other)

### Event doesn't fire?
- Complete the triggering mission
- Use console: `country_event { id = rip_vol_alt_history.X days = 1 }`

### Reform doesn't unlock?
- Verify flag set (console: `has_country_flag rip_vol_*`)
- Check government type is monarchy
- Reload government screen (switch reform, switch back)

### HLC dependency not working?
- Tag HLC: verify their flags set
- Verify HLC completed their missions
- Force HLC events if needed

---

## What's Next? (Future Work)

### Short Term
- [ ] Add AI weights for event options
- [ ] Create fail-safe union alternatives
- [ ] Add Lviv/Kyiv regional modifiers

### Medium Term
- [ ] Create VOL-HLC joint great projects
- [ ] Add Voivode rebellion events (crisis system)
- [ ] Integrate Black Sea trade mechanics

### Long Term
- [ ] Expand to other Eastern European nations (Ryazan, Tver, etc.)
- [ ] Create Commonwealth alternative (Ruthenia-centric PLC)
- [ ] Add custom music/sound events for major decisions

---

## Credits & References

### Historical Inspirations
- **Carpathian Federation:** Austria-Hungary dual monarchy structure
- **Grand Ruthenia:** Grand Duchy of Lithuania expansion model
- **Confessional Balance:** 17th century Uniate-Orthodox compromise
- **Constitutional Frameworks:** Polish Sejm, Hungarian Voivode Assembly, Cossack Rada

### EU4 Mechanics Used
- Government reform system (11-tier monarchy)
- Event-triggered flag system
- Mission tree architecture (4-column format)
- Modifier stacking system
- Opinion cascading

---

## Summary Table

| Aspect | Eastern Path | Baltic Path |
|--------|--------------|------------|
| Primary Goal | Carpathian Federation | Grand Ruthenia |
| Geographic Focus | Galicia + Carpathians | Lithuania + Ruthenia |
| HLC Dependency | HIGH (requires Austria choice) | NONE (independent) |
| Final Rank | Rank 2-3 (depends on HLC) | Rank 3 (always great power) |
| Government Type | Federation hybrid | Independent monarchy |
| Confessional | Synced with HLC | Free choice |
| Constitutional | Synced with HLC | Free choice |
| Modifier Count | 15-20 | 15-20 |
| Replayability | High (HLC variations) | High (independence paths) |
| Difficulty | Medium (HLC bottleneck) | Medium-High (expansion needed) |

---

## How to Use This Package

1. **For Playing:** Start as VOL, follow "Quick Game Flow" above
2. **For Testing:** Use "VOL_TESTING_GUIDE.md" for comprehensive tests
3. **For Understanding:** Read "VOLHYNIA_IMPLEMENTATION_SUMMARY.md" for technical details
4. **For Design:** Review "VOL_HLC_SYNERGY_SYSTEM.md" for mechanics & examples

---

**Version:** 1.0
**Release Date:** 2025
**Mod:** RIP (Ruthenia: Impossible Possibilities)
**Status:** ✅ COMPLETE & READY FOR TESTING
