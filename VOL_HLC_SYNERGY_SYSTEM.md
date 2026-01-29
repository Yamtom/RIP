# VOL-HLC Galician Union System

## Core Concept
Volhynia and Galicia form **complementary alternative history paths** where VOL's development is tightly linked to HLC's choices. This system allows:
- **Junior partnership** (VOL as subject of HLC)
- **Sibling federation** (both equal partners in Carpathian Federation)
- **Independent parallel development** (separate grand powers)

---

## Flag Interaction Matrix

### HLC → VOL Dependencies

| HLC Flag | Effect on VOL | Result |
|----------|---------------|--------|
| `rip_galicia_path_austria` | Unlocks `VOL_carpathian_federation_eastern` mission | Eastern partnership becomes viable |
| `rip_galicia_path_poland` | Blocks Eastern path (incompatible with Poland's system) | VOL must pursue Baltic path |
| `rip_galicia_confessional_set` | Unlocks `VOL_confessional_balance` mission | VOL can synchronize religion |
| `rip_galicia_constitution_done` | Enables advanced government reform decisions | VOL can finalize constitutional framework |

### VOL → HLC Opinion Effects

| VOL Flag | Opinion Modifier | Value |
|----------|-----------------|-------|
| `rip_vol_eastern_path` | `vol_galician_brotherhood` | +1 diplomatic reputation |
| `rip_vol_carpathian_partner` | `vol_carpathian_brother` | +3 opinion |
| `rip_vol_carpathian_union_formed` | `vol_eternal_union` | +5 opinion, -25% alliance negotiation |

---

## Three Scenarios

### Scenario A: Carpathian Federation (Mutual Peers)

**Prerequisites:**
- VOL independent (rip_vol_eastern_path)
- HLC chose Austria path (rip_galicia_path_austria)
- Both allied

**Progression:**
```
VOL_galician_alliance mission completed
    ↓ (alliance = HLC requirement met)
VOL_carpathian_federation_eastern mission completed
    ↓ (event rip_vol_alt_history.1)
rip_vol_alt_history.1 event fires
    ↓ (player chooses "Form Carpathian Federation")
create_union = HLC  (VOL becomes junior partner)
    ↓
Both countries share:
  - Carpathian Federation government modifier
  - Unified confessional policy
  - Constitutional framework
```

**Result:**
- VOL in personal union with HLC
- VOL can elect Carpathian Federation government reforms (3-tier system)
- HLC gets +5 opinion from eternal union modifier
- Combined realm spans Carpathians to Dniepr

---

### Scenario B: Independent Grand Ruthenia (VOL Dominant)

**Prerequisites:**
- VOL pursues Baltic path (rip_vol_baltic_path)
- Conquer Lithuania, Samogitia, White Ruthenia
- HLC becomes supporting power (not dominant)

**Progression:**
```
VOL_baltic_aspirations mission completed
    ↓ (conquer Lithuania/Samogitia)
VOL_grand_ruthenia_baltic mission completed
    ↓ (event rip_vol_alt_history.2)
rip_vol_alt_history.2 event fires
    ↓ (player accepts Grand Ruthenia title)
set_country_rank = 3
add_country_modifier = vol_grand_ruthenia_hegemony
    ↓
VOL controls:
  - Entire Ruthenia (west + east Dniepr)
  - Lithuania proper
  - White Rutheria
  - Potential HLC as ally/vassal
```

**Result:**
- VOL becomes **independent great power** (rank 3)
- HLC can be junior partner or excluded from power structure
- VOL elects unique Grand Ruthenia reforms
- Alternative to historical PLC (Polish-dominated Commonwealth)

---

### Scenario C: Dynastic Union (HLC Dominant)

**Prerequisites:**
- VOL united with Galicia provinces
- HLC already independent/powerful
- VOL_unite_galicia mission completed

**Progression:**
```
VOL_unite_galicia mission completed
    ↓ (event trigger for HLC: rip_galicia.1)
HLC forms union with VOL
    ↓ (HLC becomes senior partner)
VOL remains junior partner
HLC can impose:
  - Confessional policy (event rip_vol_alt_history.3)
  - Constitutional framework (event rip_vol_alt_history.4)
  - Government reforms tier progression
```

**Result:**
- VOL develops government reforms as HLC's junior partner
- Confessional and constitutional choices sync with HLC's path
- VOL can achieve independence through rebel support or war

---

## Government Reform Unlocks via Events

### Eastern Path Event Chain
```
VOL_eastern_partnership_culmination mission
    ↓ (trigger)
rip_vol_alt_history.1: Eastern Partnership Formed
    ↓ (choose "Form Carpathian Federation")
set_country_flag = rip_vol_carpathian_partner
    ↓
VOL_confessional_balance mission available
    ↓ (if HLC has rip_galicia_confessional_set)
rip_vol_alt_history.3: Synod of Confessional Balance
    ↓ (choose Orthodox/Uniate/Pluralist)
set_country_flag = rip_vol_confessional_allied
    ↓
vol_confessional_reform becomes eligible
```

### Baltic Path Event Chain
```
VOL_grand_ruthenia_baltic mission
    ↓ (trigger)
rip_vol_alt_history.2: Grand Ruthenia Proclaimed
    ↓ (choose "Accept Grand Ruthenia's mantle")
set_country_flag = rip_vol_grand_ruthenia_confirmed
    ↓
VOL_constitutional_assembly mission available
    ↓ (requires federation OR grand ruthenia modifier + 45 absolutism)
rip_vol_alt_history.4: Constitutional Assembly
    ↓ (choose Crown&Sejmik / Voivodeship / Cossack)
set_country_flag = rip_vol_constitution_done
    ↓
vol_ruthenia_reform becomes eligible
```

---

## Confessional Synergy System

### How Confessional Balance Works

1. **HLC makes confessional choice** (event rip_galicia.2)
   - Sets `rip_galicia_confessional_set` flag
   - Applies one modifier: `uniate_synod` OR `orthodox_bastion`

2. **VOL_confessional_balance mission available**
   - Trigger: `has_country_flag = rip_galicia_confessional_set` on HLC
   - Fires: event rip_vol_alt_history.3

3. **VOL chooses confessional approach**
   - Orthodox Foundation (if HLC chose Orthodox)
   - Uniate Synthesis (if HLC chose Uniate)
   - Pluralist Balance (neutral choice)

4. **Results**
   - Sets `rip_vol_confessional_allied` flag
   - Applies complementary modifier
   - Unlocks `vol_confessional_reform` (Tier 4)

### Confessional Modifier Benefits

**Orthodox Foundation + Orthodox Bastion (HLC)**
- Combined: +2 tolerance own, +1 church power modifier
- Strategy: Unified Orthodox bloc resisting Polish/Catholic pressure

**Uniate Synthesis + Uniate Synod (HLC)**
- Combined: +2 religious unity, balance between Rome and Kyiv
- Strategy: Diplomatic middle ground maintaining Catholic and Orthodox traditions

**Pluralist Balance + Any HLC Path**
- Combined: +2-4 total tolerance modifiers
- Strategy: Multi-faith realm with cultural diversity

---

## Constitutional Framework System

### Mission: VOL_constitutional_assembly

**Availability:**
- Requires: Federation OR Grand Ruthenia modifier (path-dependent)
- Requires: 45+ absolutism
- Event: rip_vol_alt_history.4 fires

**Three Constitutional Choices**

#### Option 1: Crown and Sejmik (Polish Model)
```
Effect:
  + add_country_modifier = vol_crown_and_sejmik_reform (duration -1)
  + 50 adm power
  + 50 dip power
  + max_absolutism = 5

Interpretation:
  - Nobility retains significant privileges
  - Sejmik (local assembly) shares power with crown
  - Diplomatic engagement increased
  - More limited absolutism (~5-15 range)
```

#### Option 2: Voivodeship Assembly (Hungarian Model)
```
Effect:
  + add_country_modifier = vol_voivodeship_assembly_reform (duration -1)
  + 75 adm power
  + max_absolutism = 10

Interpretation:
  - Voivodes organize formal assembly with crown authority
  - Stronger monarchical control than Sejmik
  - Better administrative efficiency
  - Absolutism cap raised to 10 (moderate)
```

#### Option 3: Cossack Democracy (Radical Model)
```
Effect:
  + add_country_modifier = vol_cossack_democratic_reform (duration -1)
  + 75 mil power
  + 25 legitimacy

Interpretation:
  - Cossack egalitarian principles dominate
  - Rada (council) checks monarchical power
  - Strong military tradition
  - Republican legitimacy replaces noble privileges
```

---

## Historical References & Mechanics

### Carpathian Federation Model
**Historical Inspiration:** Austria-Hungary dual monarchy structure

**Mechanical Implementation:**
- Personal union (one ruler, two crowns)
- Shared confesional policy forced by HLC-VOL alliance
- Equal administrative capacity growth
- Mutual opinion bonuses (+5 eternal union)
- Both realms can elect distinct government reforms

**Advantage Over Historical PLC:**
- Doesn't require Polish dominance
- Ruthenian culture/religion remains primary
- VOL can achieve equality or dominance through conquest

---

### Grand Ruthenia Model
**Historical Inspiration:** Grand Duchy of Lithuania expansion

**Mechanical Implementation:**
- VOL becomes rank 3 great power (not junior)
- Controls entire Ruthenia core region
- Extends into Baltic territories
- Can accept other nations as vassals (including HLC)

**Advantage Over Historical Lithuania:**
- Centered on Ruthenian identity (not Baltic)
- Avoids Polish-Lithuanian political structures
- Allows cossack/orthodox culture focus

---

### Constitutional Models

**Polish Crown & Sejmik:**
- Real historical model: Polish-Lithuanian Commonwealth
- VOL version: NON-SUBSERVIENT to Polish crown
- Mechanics: Nobility power checked by monarchy

**Hungarian Voivodeship:**
- Real historical model: Hungarian nobility with voivodes
- VOL version: Ruthenian voivode assembly
- Mechanics: Organized aristocracy with formal structure

**Cossack Democracy:**
- Real historical model: Zaporozhian Sich Rada
- VOL version: Expanded to realm-wide governance
- Mechanics: Republican legitimacy with military focus

---

## Integration Points

### With HLC System
- VOL confessional missions **require** HLC confessional flag
- VOL constitutional missions **require** federation OR grand ruthenia (path-dependent)
- VOL-HLC opinion cascades trigger joint events

### With Existing VOL Missions
- Core missions (independence, unite galicia) are universal
- Path missions (eastern vs baltic) are mutually exclusive
- Synergy missions (confessional, constitutional) bridge both paths

### With Government Reforms
- **Tier 1 (Power Structure):** vol_voivodeship_reform
  - Available immediately after independence
  - No flag requirements
  
- **Tier 4 (State & Religion):** vol_confessional_reform
  - Requires `rip_vol_confessional_allied` flag
  - Syncs with HLC's confessional path
  
- **Tier 9 (Legitimation):** vol_ruthenia_reform
  - Requires `rip_vol_constitution_done` flag
  - Final tier unlocked by constitutional choice

---

## Example Playthroughs

### Playthrough 1: Carpathian Federation Path

**Turn 1444:** Start as VOL
**Years 1-20:** Build up, core territories, ally HLC
**Year ~1470:** HLC chooses Austria path (gets rip_galicia_path_austria)
**Year ~1480:** VOL_galician_alliance mission completes → rip_vol_eastern_path flag
**Year ~1490:** VOL_carpathian_federation_eastern completes → event rip_vol_alt_history.1
**Decision:** Form Carpathian Federation (create_union HLC)
**Year ~1500:** HLC's confessional choice fires rip_vol_alt_history.2
**Year ~1510:** VOL_confessional_balance completes → rip_vol_alt_history.3
**Choose:** Orthodox Foundation (matches HLC's Orthodox Bastion)
**Year ~1520:** vol_confessional_reform becomes available
**Year ~1530:** VOL_constitutional_assembly completes → rip_vol_alt_history.4
**Choose:** Voivodeship Assembly (blend of Hungarian and local traditions)
**Year ~1540:** vol_ruthenia_reform becomes available
**Result:** Carpathian Federation rules eastern Europe with unified Ruthenian identity

---

### Playthrough 2: Independent Grand Ruthenia Path

**Turn 1444:** Start as VOL
**Years 1-50:** Expand northward, conquer Lithuania pieces
**Year ~1500:** VOL_baltic_aspirations completes → rip_vol_baltic_path flag
**Year ~1510:** Conquer all Lithuania + Samogitia
**Year ~1520:** VOL_grand_ruthenia_baltic completes → event rip_vol_alt_history.2
**Decision:** Accept Grand Ruthenia mantle → rank 3, huge prestige
**Year ~1530:** Can pursue confessional and constitutional missions independently
**Choose:** Pluralist Balance (accepts all faiths)
**Year ~1540:** Choose Cossack Democracy (radical egalitarian system)
**Result:** Grand Ruthenia becomes great power rivaling Poland, centered on Cossack principles

---

## Balance Notes

### Why Mutual Exclusivity?
- Prevents "dominant megastate" (VOL + HLC both at full strength)
- Forces meaningful choices (Eastern partnership vs Nordic expansion)
- Creates distinct alt-history outcomes

### Why HLC Flag Requirements?
- Encourages VOL-HLC alliance and interaction
- Makes VOL development partially dependent on HLC choices
- Prevents VOL from ignoring HLC entirely
- Simulates realistic geopolitical constraints

### Why Government Reform Gating?
- Ensures missions must be completed for reform access
- Creates logical progression (confessional → constitutional)
- Prevents "optimal path" min-maxing
- Rewards engaged roleplay

---

## Future Expansion Ideas

### Additional Voivode Options
- Chernihiv voivode assembly
- Kyiv voivode assembly
- Lithuanian-Ruthenian hybrid council

### Crisis Events
- Voivode rebellion (if assembly too powerful)
- Hetman coup (if cossack democracy chosen)
- Religious reformation pressure (Age of Reformation)

### Cultural Mashup Events
- Polish-Ruthenian cultural fusion (if PLC forms)
- Lithuanian-Ruthenian dynastic marriage
- Cossack-noble conflict resolution

### Integration with Greater Mod
- Ties to:Crimean Khanate, Ottoman pressure
- Black Sea trade competition
- Magdeburg rights in cities
- Brethren of the Common Life religious movements
