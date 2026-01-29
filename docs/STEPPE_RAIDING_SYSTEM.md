# STEPPE RAIDING & NOMADIC MECHANICS SYSTEM
## Comprehensive Documentation

**Date**: January 30, 2026  
**Version**: 1.0  
**Author**: Yamtom  
**Regions**: Crimean Khanate, Nogai Horde, Great Steppe, Black Sea, Muscovy/Russia border

---

## EXECUTIVE SUMMARY

This system recreates the devastating steppe raiding culture that plagued Eastern Europe from the 14th-18th centuries. Crimean Tatars, Nogai, and other nomadic peoples conducted regular raids into Muscovy, Poland-Lithuania, and Ukraine to capture **yasyr** (ясир - captives for the slave trade). The system also includes:

- **Raiding mechanics** for steppe hordes
- **Yasyr (slave) system** with ransom opportunities
- **Cossack counter-raids** including chaiky boat raids
- **Kalmyk and Nogai migrations** (historical 1500s-1600s)
- **Zasechnaya Cherta** - Russian defensive line system
- **Kaffa slave markets** economic simulation

**Total Implementation**:
- 10 event chains
- 25+ modifiers (country and province)
- 6 opinion modifiers
- Complete English localization
- Period coverage: 1444-1821

---

## HISTORICAL CONTEXT

### The Yasyr Trade (1444-1783)

**Yasyr** (Russian: ясир, from Turkic *esir* = captive/prisoner) was the term for captives taken in steppe raids and sold into slavery. This was the economic backbone of the Crimean Khanate.

#### Scale of the Trade:
- **1500-1700**: Estimated 2-2.5 million captives taken from Russia, Poland, Ukraine
- **Peak Years**: 1570s-1630s (before Zasechnaya Cherta effectiveness)
- **Major Markets**: Kaffa (Crimea), Constantinople, Cairo, Baghdad
- **Price Range**: 30-100 ducats per slave depending on age/gender/skills

#### Typical Raid Pattern:
1. **Spring/Summer**: Small parties (100-1,000 riders) strike border regions
2. **Major Raids**: Every 2-5 years, forces of 10,000-30,000 riders penetrate deep
3. **Lightning Speed**: 100+ km/day movement, avoiding fortified positions
4. **Captive Taking**: Primary goal - yasyr more valuable than loot
5. **Return Route**: Escape before main armies mobilize

### Geographic Targets

#### Most Raided Regions:
- **Muscovy**: Tula, Ryazan, Kaluga regions (pre-Zasechnaya Cherta)
- **Ukraine**: Podolia, Volhynia, Kiev region
- **Poland**: Eastern borderlands (kresy wschodnie)
- **Circassia**: North Caucasus (internal Crimean raids)

#### Safe Zones:
- Behind major river lines (Oka River, Dnieper)
- Fortified cities (kremlin strongholds)
- Post-1600s Zasechnaya Cherta zones

### Zasechnaya Cherta (Засечная черта)

**Great Abatis Line** - Russian defensive system 1520s-1700s:

#### Structure:
- **Zaseki** (засеки): Zones of felled trees creating impassable barriers for cavalry
- **Fortified Towns**: Garrison posts every 20-40km
- **Watchtowers**: Early warning system (fire/smoke signals)
- **Service Cavalry**: Rapid response forces (служилые люди)
- **Length**: Eventually ~1,000 km from Bryansk to Volga

#### Effectiveness:
- **Pre-1600**: Limited, easily bypassed
- **1600-1650**: Reduced major raids by ~60%
- **Post-1650**: Crimean raids mostly limited to small-scale border incidents
- **1680s+**: Pushed southward to protect expanding Russian territory

### Cossack Chaiky Raids

**Chaiky** (чайки) - light boats used by Zaporozhian Cossacks:

#### Characteristics:
- **Size**: 15-20m long, 3-4m wide
- **Crew**: 50-70 Cossacks per boat
- **Armament**: Muskets, small cannons, boarding weapons
- **Speed**: Very fast under oars, could outrun galleys

#### Raid Targets:
- **1590s-1620s**: Peaked during Ottoman wars
- **Targets**: Crimean coast, Kaffa, Sinop, even Constantinople suburbs
- **Goal**: Revenge for yasyr taking, liberation of captives, loot
- **Impact**: Severely disrupted Crimean economy, freed thousands of slaves

---

## EVENT CHAINS DOCUMENTATION

### CHAIN 1: Steppe Raiding Cycle

#### Event 1.1: Organize Raiding Party
**ID**: `steppe_raid.1`  
**Trigger**:
- Government: Steppe Horde OR Crimea/Nogai/Kazakh/Astrakhan
- Not at war
- 30%+ manpower
- No recent raid cooldown
- Neighbor is Muscovy/Russia/Poland/Lithuania/Ukraine tags

**MTTH**: 120 months
- ×0.7 if horde unity 70+
- ×0.8 if 100+ MIL power
- ×1.5 if at war

**Options**:
1. **Launch raid** (AI 70%)
   - Cost: 25 MIL power, 0.15 years income
   - Gain: Modifier `steppe_raid_party` (1 year)
   - Gain: +5 horde unity
   - Cooldown: 2 years
   - Triggers event 2 for random neighbor (30 days)

2. **Don't raid** (AI 30%)
   - Cost: -5 prestige, -3 horde unity

**Historical Context**: Raids typically organized in spring when horses recovered from winter and grass was plentiful for long journeys.

#### Event 1.2: Raid Arrives (Target)
**ID**: `steppe_raid.2`  
**Triggered Only**: By event 1

**Options**:
1. **Defend borders** (AI 60%)
   - Cost: 25 MIL power
   - Province gets `steppe_border_defense` modifier (1 year)
   - Triggers event 3 (raid repelled) for raider

2. **Accept devastation** (AI 40%)
   - Province gets +15 devastation
   - Province gets `steppe_raid_devastation` modifier (5 years)
   - Triggers event 4 (successful raid) for raider

**Historical Context**: Sedentary states often couldn't mobilize fast enough to intercept raids, forcing choice between costly defense or accepting damage.

#### Event 1.3: Raid Repelled
**ID**: `steppe_raid.3`  
**Triggered Only**: By event 2 (defense option)

**Effects**:
- Raider loses: -10 prestige, -5 horde unity, -2 manpower
- Removes `steppe_raid_party` modifier
- Opinion modifier: `steppe_raid_repelled` (-15 opinion, 10 years)

**Historical Context**: Well-prepared defenses (Zasechnaya Cherta, strong garrisons) could repel raids, as in 1572 Battle of Molodi.

#### Event 1.4: Successful Raid - Yasyr Taken
**ID**: `steppe_raid.4`  
**Triggered Only**: By event 2 (accept devastation)

**Options**:
1. **Sell yasyr in slave markets** (AI 80%)
   - Gain: +0.5 years income, +10 prestige, +10 horde unity
   - Gain: `steppe_successful_raid` modifier (5 years)
   - Cost: -1 manpower (casualties)
   - Opinion: `steppe_raid_successful` (-30) and `steppe_yasyr_taken` (-50) with target
   - Triggers event 5 (ransom) for target (6 months later)

2. **Hold for ransom** (AI 20%)
   - Gain: +0.25 years income, +5 prestige, +5 horde unity
   - Opinion: `steppe_raid_tribute` (+10) with target

**Historical Context**: Crimean economy depended heavily on slave trade. Kaffa market alone processed 10,000-20,000 slaves annually at peak.

#### Event 1.5: Ransom the Yasyr
**ID**: `steppe_raid.5`  
**Triggered Only**: By event 4 (180 days later)  
**Condition**: Not at war with raider

**Options**:
1. **Pay ransom** (AI 60%, factor 0.1 if poor)
   - Cost: 0.5 years income
   - Province regains +1 base manpower
   - Gain: +5 prestige
   - Raider gains: +0.3 years income
   - Opinion: `steppe_yasyr_ransomed` (+20 opinion, 15 years)

2. **Refuse ransom** (AI 40%)
   - Province loses: -1 base manpower, +5 devastation
   - Lose: -10 prestige
   - Opinion: `steppe_yasyr_refused` (-20 opinion, 10 years)

**Historical Context**: Ransom was common practice. Noble families often bankrupted themselves to recover relatives. Common folk had no such recourse.

---

### CHAIN 2: Cossack Counter-Raids

#### Event 2.1: Cossacks Demand Vengeance
**ID**: `steppe_raid.6`  
**Trigger**:
- Tag: VOL/HLC/PDL/ZAZ OR has Cossack estate
- Has Cossack self-governance privilege
- No Cossack raid cooldown
- Neighbor is Crimea/Nogai/steppe horde
- That neighbor has opinion modifier `steppe_yasyr_taken` on ROOT

**MTTH**: 80 months
- ×0.7 if Cossack loyalty 60+

**Options**:
1. **Support Cossack raid** (AI 70%)
   - Cost: 15 MIL power
   - Cooldown: 2 years
   - Triggers event 7 for target horde (45 days)

2. **Forbid raid** (AI 30%)
   - Cost: -10 Cossack loyalty
   - Gain: +5 prestige

**Historical Context**: Cossacks organized revenge raids especially after major yasyr incidents. Famous raids: 1606, 1614, 1616 chaiky attacks on Constantinople suburbs.

#### Event 2.2: Cossack Raid Strikes
**ID**: `steppe_raid.7`  
**Triggered Only**: By event 6

**Effects**:
- Random border province: +10 devastation
- Province gets `cossack_raid_damage` modifier (3 years)
- Horde loses: -5 prestige, -5 horde unity
- Cossacks gain: +0.3 years income, +10 Cossack loyalty

**Historical Context**: Cossack raids disrupted Crimean economy and slave trade. 1616 raid captured Turkish ambassador's ship, causing diplomatic crisis.

---

### CHAIN 3: Migrations

#### Event 3.1: Nogai Migration
**ID**: `steppe_raid.8`  
**Trigger**:
- Tag: Crimea OR Ottomans
- Owns Yedisan/Budjak/Kuban provinces
- Nogai Horde doesn't exist
- After 1500

**MTTH**: 240 months

**Options**:
1. **Settle Nogai** (AI 80%)
   - Selected province: Culture → nogaybak, +2 manpower, +1 production
   - Gain: `nogai_settlers` modifier (20 years)

2. **Refuse** (AI 20%)
   - Lose: -5 prestige

**Historical Context**: After collapse of Nogai Horde (1550s-1630s), surviving clans settled in Crimean territory. Formed autonomous Nogai Horde under Crimean suzerainty in Budjak/Kuban.

#### Event 3.2: Kalmyk Migration
**ID**: `steppe_raid.9`  
**Trigger**:
- Tag: Muscovy OR Russia
- Owns Astrakhan + Lower Yayik
- Years 1620-1650

**MTTH**: 120 months

**Options**:
1. **Accept Kalmyks** (AI 70%)
   - Astrakhan & Lower Yayik: Culture → oirats, Religion → vajrayana
   - Astrakhan: +3 manpower; Yayik: +2 manpower
   - Gain: `kalmyk_cavalry` modifier (permanent)

2. **Refuse** (AI 30%)
   - Astrakhan spawns: 3 regiments nomad raiders

**Historical Context**: Kalmyk migration (1609-1632) brought ~200,000 Oirat Mongols from Dzungaria to Caspian region. Became Russian subjects in 1640s.

---

### CHAIN 4: Zasechnaya Cherta

#### Event 4.1: Build Defensive Line
**ID**: `steppe_raid.10`  
**Trigger**:
- Tag: Muscovy OR Russia
- ADM tech 10+
- Owns Russia region province bordering Crimea
- No `zasechnaya_cherta` modifier

**MTTH**: 200 months
- ×0.7 if 100+ ADM power

**Options**:
1. **Build Zasechnaya Cherta** (AI 80%)
   - Cost: 50 ADM power, 0.5 years income
   - Gain: `zasechnaya_cherta` modifier (permanent)
   - All border provinces: `zasechnaya_cherta_province` modifier (permanent)

2. **Too expensive** (AI 20%)
   - Lose: -5 prestige

**Historical Context**: Zasechnaya Cherta construction began under Ivan III (1480s) and reached full effectiveness by 1650s. Fundamentally changed balance of power between Russia and Crimea.

---

## MODIFIERS REFERENCE

### Raiding Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `steppe_raid_party` | +25% Movement Speed, -20% Land Maintenance, -15% Cavalry Cost | 1 year |
| `steppe_successful_raid` | +1 Horde Unity, +0.25 Prestige, +5% Cavalry Power | 5 years |
| `steppe_raid_devastation` | +5 Unrest, -35% Tax, -25% Manpower, -20% Production | 5 years |

### Defense Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `steppe_border_defense` | +25% Defensiveness, +10% Manpower, +1 Hostile Attrition | 1 year |
| `zasechnaya_cherta` | +1 Hostile Attrition, -15% Fort Maintenance, +10% Defensiveness | Permanent |
| `zasechnaya_cherta_province` | +30% Local Defensiveness, +2 Local Hostile Attrition, -10% Development Cost | Permanent |

### Migration Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `nogai_settlers` | +10% Cavalry Power, -10% Cavalry Cost, +15% Manpower Recovery | 20 years |
| `kalmyk_cavalry` | +15% Cavalry Power, +25% Cavalry Flanking, -15% Cavalry Cost, +1 Horde Unity | Permanent |

### Economic Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `slave_trade_income` | +10% Trade Efficiency, +5% Global Trade Power, -1 Diplomatic Reputation | Varies |
| `crimean_yasyr_market` | +15% Trade Efficiency, +10% Global Trade Power, -2 Diplomatic Reputation, +2 Horde Unity | Event-based |

---

## OPINION MODIFIERS

| Modifier | Opinion | Duration | Source |
|----------|---------|----------|--------|
| `steppe_raid_repelled` | -15 | 10 years | Successfully defended against raid |
| `steppe_raid_successful` | -30 | 15 years | Lost territory to raid |
| `steppe_yasyr_taken` | -50 | 20 years | Population captured as slaves |
| `steppe_raid_tribute` | +10 | 10 years | Offered tribute instead of raid |
| `steppe_yasyr_ransomed` | +20 | 15 years | Paid ransom for captives |
| `steppe_yasyr_refused` | -20 | 10 years | Refused to ransom captives |

---

## AI BEHAVIOR

### Raiding Decisions
**Launch Raid**: 70% yes, 30% no  
**Defense**: 60% defend, 40% accept damage  
**Yasyr Sale**: 80% sell, 20% ransom  
**Pay Ransom**: 60% yes (0.1× if treasury < 50), 40% no

### Migration Acceptance
**Nogai**: 80% accept, 20% refuse  
**Kalmyk**: 70% accept, 30% refuse (rebel spawn)

### Zasechnaya Cherta
**Build**: 80% yes, 20% no

---

## INTEGRATION WITH EXISTING SYSTEMS

### Compatibility
- Works with existing Cossack estate mechanics
- Integrates with Crimean Khanate flavor
- Compatible with Ottoman vassal systems
- Works alongside Western Ukraine historical events

### Tag Requirements
**Raiders**: Steppe hordes, CRI, NOG, KAZ, AST  
**Targets**: MOS, RUS, POL, PLC, LIT, VOL, HLC, PDL, Eastern tech group  
**Cossacks**: VOL, HLC, PDL, ZAZ, any with Cossack estate

### Province Dependencies
- **Border provinces**: Determines raid targets
- **Yedisan (2410), Budjak (2447), Kuban (2416)**: Nogai settlement
- **Astrakhan (464), Lower Yayik (1082)**: Kalmyk settlement
- **Russia region**: Zasechnaya Cherta construction

---

## HISTORICAL ACCURACY

### Authentic Elements
1. **Yasyr System**: Based on actual slave trade (2+ million captives 1500-1700)
2. **Kaffa Market**: Real economic center of Crimean Khanate
3. **Zasechnaya Cherta**: Actual defensive line (1520s-1700s)
4. **Kalmyk Migration**: Historical migration 1609-1632
5. **Nogai Settlement**: Real refugee crisis 1550s-1630s
6. **Cossack Chaiky**: Famous boat raids 1590s-1620s

### Simplified Elements
1. **Raid Frequency**: Game raids less frequent than historical (every 2-3 years vs. annually)
2. **Captive Numbers**: Abstracted to manpower/income rather than tracking individuals
3. **Ransom Process**: Simplified from complex diplomatic negotiations
4. **Zasechnaya Cherta**: Instant effect vs. gradual construction (1520s-1680s)

---

## GAMEPLAY IMPACT

### As Crimean Khanate
- **Early Game**: Use raids to generate income and horde unity
- **Mid Game**: Balance Ottoman vassalage with raiding autonomy
- **Late Game**: Face Zasechnaya Cherta effectiveness, shift to diplomacy

### As Muscovy/Russia
- **Early Game**: Suffer raids, prioritize border defense
- **Mid Game**: Build Zasechnaya Cherta (after ADM 10)
- **Late Game**: Turn tables, push into Crimean territory

### As Poland-Lithuania/Ukraine
- **Strategy**: Use Registered Cossacks for defense, permit counter-raids for Cossack loyalty
- **Dilemma**: Support Cossacks (loyalty) vs. maintain relations with Ottomans/Crimea

---

## TESTING CHECKLIST

- [ ] Raid events fire with correct MTTH
- [ ] Yasyr system generates appropriate income
- [ ] AI makes reasonable raiding decisions
- [ ] Zasechnaya Cherta reduces raid frequency
- [ ] Kalmyk/Nogai migrations trigger in correct date ranges
- [ ] Cossack revenge raids work correctly
- [ ] Opinion modifiers apply properly
- [ ] Province modifiers stack correctly
- [ ] No conflicts with existing steppe horde mechanics
- [ ] Localization displays properly

---

## FILES CREATED/MODIFIED

### Event Files
- **events/SteppeRaiding.txt** (new, 500+ lines)
  - 10 event chains with historical context

### Modifier Files
- **common/event_modifiers/steppe_raid_modifiers.txt** (new)
  - 25+ country and province modifiers

### Opinion Files
- **common/opinion_modifiers/RIP_opinion_modifiers.txt** (modified)
  - Added 6 raiding-related opinion modifiers

### Localization Files
- **localisation/steppe_raiding_l_english.yml** (new)
  - Complete English localization for all events/modifiers

---

## FUTURE EXPANSION IDEAS

1. **Decision to Form Raiding Party**: Player-controlled raids instead of only events
2. **Yasyr Liberation Missions**: Special missions for Ukraine/Russia to free captives
3. **Kaffa Slave Market Building**: Special building in Crimea increasing trade income
4. **Steppe Migration OPM Mechanic**: Allow one-province hordes to migrate
5. **Don Cossack Raids**: Extend system to Don Cossack Host
6. **Circassian Slave Trade**: Expand to North Caucasus region
7. **Ottoman Intervention**: Events where Ottomans defend Crimean vassals

---

## CREDITS & ACKNOWLEDGMENTS

**Historical Sources**:
- Kivelson, Valerie: "Cartographies of Tsardom"
- Fisher, Alan: "Crimean Tatars"
- Khodarkovsky, Michael: "Russia's Steppe Frontier"

**Inspiration**: Paradox forums threads on steppe mechanics (2015-2017)

**Implementation**: Yamtom

---

**END OF DOCUMENTATION**

*"The steppe remembers, and the steppe takes what is owed."*
