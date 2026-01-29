# Border Principalities System - Technical Documentation

## Historical Context

Between 1444 and 1520, the border region between the Grand Duchy of Lithuania and Muscovy was characterized by numerous small semi-autonomous principalities that could switch allegiance between the two powers. This instability was a key factor in the Muscovite-Lithuanian Wars of 1500-1503 and 1507-1508, which resulted in significant territorial gains for Moscow.

### Key Historical Principalities

1. **Rylsk Principality (Рыльское княжество)**
   - **Rulers**: Descendants of Dmitri Shemyaka, a Rurikid prince who contested the throne of Moscow
   - **Status**: Lithuanian vassal with considerable autonomy
   - **Historical Fate**: Switched to Muscovy during 1500-1503 war
   - **Significance**: Shemyaka's descendants had legitimate claims to Russian lands, making them valuable diplomatic assets

2. **Hlinsk/Glinski Lands (Глинские земли)**
   - **Rulers**: Glinski family, claiming descent from Mamai (Mongol general)
   - **Military**: Commanded Tatar cavalry loyal to the family
   - **Rebellion**: 1507-1508 Glinski rebellion, switched to Muscovy
   - **Legacy**: Elena Glinskaya (from this family) became mother of Ivan IV (the Terrible)
   - **Importance**: Provided crucial border defense against steppe raids using Tatar troops

3. **Jagoldai Settlement (Ягольдаева волость)**
   - **Ruler**: Jagoldai, Golden Horde pretender
   - **Status**: Tatar military settlement under Lithuanian protection
   - **Location**: South of Kursk, modern Belgorod region
   - **Historical Fate**: Passed to Muscovy in 1492-1494 border war
   - **Function**: Buffer zone against Nogai and Crimean raids

4. **Severian Principalities (Северские княжества)**
   - **Main Cities**: Starodub, Chernigov, Novgorod-Seversky
   - **Defection**: 1500-1503, major territorial loss for Lithuania
   - **Reason**: Orthodox Rus' princes preferred Muscovite rule
   - **Impact**: Shifted balance of power significantly toward Moscow

### The Qasim Khanate (Касимовское ханство)

**Foundation**: 1452  
**Founder**: Qasim, son of Kazan Khan  
**Purpose**: Muscovite puppet state to control Tatar vassals and justify claims on Kazan  
**Duration**: 1452-1681  
**Capital**: Qasim (Gorodets-Meshchersky)

**Historical Functions**:
- Provided loyal Tatar cavalry for Muscovite campaigns
- Served as rival claimant to Kazan throne, justifying interventions
- Demonstrated Muscovite tolerance and ability to rule Muslim subjects
- After Kazan's conquest (1552), became ceremonial but prestigious title

**Key Moments**:
- 1467-1469: Qasim Khan attacks Kazan with Muscovite support
- 1487: Qasim pretender installed as Khan of Kazan (puppet rule)
- 1552: After Ivan IV conquers Kazan, Qasim loses relevance
- 1681: Formally annexed into Russian state

### Lipka Tatars (Липки)

**Origins**: Tatars who settled in Grand Duchy of Lithuania/Polish-Lithuanian Commonwealth  
**Timeline**: 14th-17th centuries  
**Religion**: Sunni Islam  
**Language**: Turkic languages, later Polish/Belarusian  

**Military Service**:
- Elite light cavalry in Lithuanian/Polish armies
- Fought against Teutonic Knights, Muscovy, Ottoman Empire
- Renowned for speed, reconnaissance, and skirmishing
- Maintained steppe warfare traditions in European context

**Settlements**:
- Concentrated in modern Belarus and Lithuania
- Given land grants in exchange for military service
- Maintained mosques and Islamic culture
- Integrated into nobility (szlachta) while keeping Muslim faith

**Legal Status**:
- Religious freedom guaranteed by Warsaw Confederation (1573)
- Noble privileges (szlachta rights)
- Autonomy in internal affairs
- Military service obligations to Crown

## Event System Structure

### Border Principalities Events (border_principalities namespace)

#### Event 1: Shemyaka Heirs in Rylsk
**Trigger**: Lithuania owns Rylsk, 1444-1500  
**MTTH**: 12 months  
**Choice A** (AI 80%): Grant vassal autonomy → modifier `shemyaka_rurikid_rule` on province, `border_vassal_buffer` country modifier  
**Choice B** (AI 20%): Direct control → stability or adm power, +3 unrest in Rylsk

#### Event 2: Glinski Family and Mamai's Descendants
**Trigger**: Lithuania owns Bryansk or Severia area, 1444-1500  
**MTTH**: 18 months  
**Choice A** (AI 70%): Grant lands to Glinski → `glinski_tatar_settlement` modifier on random Severia/Bryansk province, +1 base manpower, `tatar_border_defense` country modifier (25 years)  
**Choice B** (AI 30%): Refuse petition → +5 prestige, `refused_powerful_family` negative modifier (10 years)

#### Event 3: Jagoldai Khanate Settlement
**Trigger**: Lithuania owns Kursk, 1444-1480  
**MTTH**: 24 months  
**Choice A** (AI 75%): Accept Jagoldai → `jagoldai_horde_settlement` modifier on Kursk, +2 base cavalry, `horde_vassal_buffer` country modifier (25 years)  
**Choice B** (AI 25%): Refuse → +10 legitimacy, +2 unrest in Kursk

#### Event 4: Rylsk Defects to Muscovy
**Trigger**: Lithuania owns Rylsk with `shemyaka_rurikid_rule`, 1500-1510, Muscovy exists and neighbors Lithuania  
**MTTH**: 36 months (faster if low legitimacy or at war)  
**Choice A** (AI 60%): Keep loyal → -10 prestige, +10 loyalty, 30% defects anyway triggering Event 5, 70% loyalty maintained  
**Choice B** (AI 10%): Peaceful transfer → Rylsk cedes to Muscovy, -15 prestige, truce  
**Choice C** (AI 30%): War → Declares restoration war on Muscovy

#### Event 5: Muscovy Receives Rylsk (triggered by Event 4)
**Result**: Muscovy gains Rylsk, +10 prestige, +5 legitimacy, core CB on Lithuania (10 years)

#### Event 6: Glinski Rebellion Brewing
**Trigger**: Lithuania has Glinski province, 1507-1515, Muscovy exists  
**MTTH**: 24 months (faster if low legitimacy or revolts present)  
**Choice A** (AI 40%): Negotiate → -10 prestige, -0.3 years income, 60% Glinski stays loyal (`glinski_appeasement`), 40% triggers Event 7  
**Choice B** (AI 30%): Suppress → -50 mil power, 2 noble rebel stacks spawn (friendly to Muscovy)  
**Choice C** (AI 30%): Exile Glinski → triggers Event 8, removes modifier, +20 devastation on province

#### Event 7: Glinski Full Rebellion (triggered by Event 6)
**Result**: 3 noble rebel stacks spawn, Muscovy gets support rebels CB (5 years)

#### Event 8: Muscovy Receives Glinski Defectors (triggered by Event 6.c)
**Result**: +15 prestige, +10 legitimacy, +50 adm power, `glinski_advisors_muscovy` modifier (20 years), core CB on Lithuania (10 years)

#### Event 9: Jagoldai Switches Allegiance
**Trigger**: Lithuania owns Kursk with `jagoldai_horde_settlement`, 1492-1505, Muscovy exists  
**MTTH**: 48 months (faster if Muscovy stronger or Lithuania at war)  
**Choice A** (AI 50%): Retain loyalty → -0.25 years income, 40% stays loyal, 60% triggers Event 10  
**Choice B** (AI 20%): Let go → Kursk cedes to Muscovy, -10 prestige  
**Choice C** (AI 30%): War → Declares annexation war on Muscovy

#### Event 10: Muscovy Receives Jagoldai (triggered by Event 9)
**Result**: Kursk cedes to Muscovy, removes old modifier, applies `jagoldai_muscovite_service`, +10 prestige, +50 mil power

#### Event 11: Starodub Switching Allegiance
**Trigger**: Lithuania owns Severia/Bryansk, 1500-1510, Muscovy neighbor  
**MTTH**: 30 months (faster if at war or Muscovy militarily stronger)  
**Choice A** (AI 70%): Fight → Muscovy gets core CB (10 years), triggers Event 12  
**Choice B** (AI 30%): Let go → -20 prestige, random Severia/Bryansk province cedes to Muscovy, truce

#### Event 12: Muscovy Receives Starodub Offer (triggered by Event 11)
**Result**: +15 prestige, +10 legitimacy, core CB on Lithuania (10 years)

### Qasim Khanate Events (qasim_khanate namespace)

#### Event 1: Foundation of Qasim Khanate
**Trigger**: Muscovy owns Qasim province, 1450-1460, Kazan exists and not allied  
**MTTH**: 24 months (faster if rival to Kazan or at war with Kazan)  
**Choice A** (AI 80%): Create khanate → `qasim_khanate_capital` on province, `qasim_khanate_vassal` country modifier (permanent), release and vassalize QAS, QAS gets `kazan_pretender_claims`, Kazan gets negative opinion  
**Choice B** (AI 20%): Direct control → +50 adm power, +1 base tax on Qasim

#### Event 2: Qasim Attacks Kazan
**Trigger**: Muscovy has QAS vassal with claims, 1467-1550, Kazan exists, not at war/allied with Kazan  
**MTTH**: 120 months (faster if rival to Kazan or Kazan weak)  
**Choice A** (AI 60%): Military support → Declares restoration PU war on Kazan, QAS -20 liberty desire  
**Choice B** (AI 30%): Diplomatic pressure → Kazan gets threatened opinion, -5 prestige  
**Choice C** (AI 10%): Restrain vassal → QAS +10 liberty desire, +25 dip power

#### Event 3: Fate of Conquered Kazan
**Trigger**: Muscovy owns Kazan capital, 1467-1552, QAS exists as vassal, Kazan doesn't exist  
**MTTH**: 6 months  
**Choice A** (AI 40%): Install Qasim Khan → Kazan area gets QAS core, release and vassalize QAS (now ruling Kazan), QAS gets `muscovite_puppet_khan`, QAS -30 liberty desire  
**Choice B** (AI 60%): Annex directly → Kazan area gets `conquered_khanate` modifier (20 years), QAS +20 liberty desire

#### Event 4: Qasim Khanate Integration
**Trigger**: Muscovy has QAS vassal, 1550-1700  
**MTTH**: 240 months (faster if Kazan conquered or high ADM)  
**Choice A** (AI 70%): Integrate → Inherit QAS, Qasim province gets `former_qasim_khanate`, country gets `tatar_nobility_integrated` (permanent)  
**Choice B** (AI 30%): Keep vassal → QAS -20 liberty desire, QAS gets `loyal_tatar_vassal`

#### Event 5: Lipka Tatars Seek Settlement
**Trigger**: Lithuania, 1440-1500, owns provinces in White Ruthenia/Minsk/Pripyat areas  
**MTTH**: 60 months  
**Choice A** (AI 80%): Welcome Lipka → Random qualifying province gets `lipka_tatar_settlement`, +1 base manpower, country gets `lipka_tatar_cavalry_tradition` (permanent)  
**Choice B** (AI 20%): Refuse → +5 prestige, +25 adm power

#### Event 6: Lipka Tatars' Loyalty
**Trigger**: Commonwealth (tag PLC), 1569-1700, has province with `lipka_tatar_settlement`  
**MTTH**: 120 months  
**Choice A** (AI 70%): Reward loyalty → -0.2 years income, all Lipka provinces get `lipka_tatar_privileges` (20 years), country gets `tatar_nobility_service` (25 years)  
**Choice B** (AI 30%): Status quo → +25 mil power

## Modifier Reference

### Province Modifiers

| Modifier | Effects | Duration | Applied By |
|----------|---------|----------|------------|
| `shemyaka_rurikid_rule` | -1 unrest, +15% defensiveness, +10% garrison | Permanent | border_principalities.1 |
| `glinski_tatar_settlement` | +20% manpower, +1 hostile attrition, +10% cavalry power | Permanent | border_principalities.2 |
| `jagoldai_horde_settlement` | +25% manpower, +15% cavalry power, +1.5 hostile attrition | Permanent | border_principalities.3 |
| `glinski_appeasement` | -2 unrest, -15% local tax | 10 years | border_principalities.6.a |
| `jagoldai_muscovite_service` | +15% manpower, +10% garrison, +1 hostile attrition | Permanent | border_principalities.10 |
| `qasim_khanate_capital` | +20% manpower, +15% cavalry power, +10% garrison | Permanent | qasim_khanate.1 |
| `conquered_khanate` | +5 unrest, +10% local autonomy | 20 years | qasim_khanate.3.b |
| `former_qasim_khanate` | +10% manpower, -10% cavalry cost | Permanent | qasim_khanate.4.a |
| `lipka_tatar_settlement` | +20% manpower, +15% garrison, +10% cavalry power | Permanent | qasim_khanate.5 |
| `lipka_tatar_privileges` | -2 unrest, +15% manpower, +20% garrison | 20 years | qasim_khanate.6.a |

### Country Modifiers

| Modifier | Effects | Duration | Applied By |
|----------|---------|----------|------------|
| `border_vassal_buffer` | +0.5 hostile attrition, -10% fort maintenance, +1 diplomat | 20 years | border_principalities.1 |
| `tatar_border_defense` | +5% cavalry power, +25% flanking, -15% fort maint, +0.75 hostile attrition | 25 years | border_principalities.2 |
| `refused_powerful_family` | -0.25 legitimacy, -5% all estate loyalty | 10 years | border_principalities.2.b |
| `horde_vassal_buffer` | -10% cavalry cost, +10% cavalry power, +1 hostile attrition | 25 years | border_principalities.3 |
| `strengthened_border_vassals` | +15% vassal income, +1 diplomatic reputation, -10% fort maintenance | 10 years | border_principalities.4.a success |
| `glinski_loyalty` | +0.5 legitimacy, +10% cavalry power, +1 diplomatic reputation | 20 years | border_principalities.6.a success |
| `jagoldai_loyalty` | +10% cavalry power, -10% cavalry cost, +0.5 hostile attrition | 15 years | border_principalities.9.a success |
| `glinski_advisors_muscovy` | +2 diplomatic reputation, +0.5 legitimacy, -15% advisor cost, +5% cav power | 20 years | border_principalities.8 |
| `lipka_tatar_cavalry_tradition` | +15% cavalry power, +25% flanking, -10% cavalry cost | Permanent | qasim_khanate.5 |
| `tatar_nobility_service` | +10% cavalry power, +1 diplomatic reputation, +2 tolerance heathen | 25 years | qasim_khanate.6.a |
| `severian_princes_defection` | -1.0 prestige, -1 diplomatic reputation, -0.5 legitimacy | Event-applied | border_principalities.11/12 |
| `muscovite_expansion_momentum` | +1.0 prestige, +1.0 legitimacy, +1 dipl rep, -10% core creation | Event-applied | border_principalities.11/12 |
| `border_war_preparation` | +5% morale, +10% manpower recovery, -15% fort maintenance | Event-applied | Multiple events |
| `qasim_khanate_vassal` | +10% cavalry power, +1 diplomatic reputation, +20% vassal income | Permanent | qasim_khanate.1 |
| `kazan_pretender_claims` | -10% AE impact, -15% unjustified demands | Permanent | qasim_khanate.1 |
| `muscovite_puppet_khan` | -20 liberty desire, -1 diplomatic reputation | Permanent | qasim_khanate.3.a |
| `tatar_nobility_integrated` | +10% cavalry power, +2 tolerance heathen, +1 diplomatic reputation | Permanent | qasim_khanate.4.a |
| `loyal_tatar_vassal` | +15% cavalry power, -30 liberty desire | Permanent | qasim_khanate.4.b |

## Integration with Existing Systems

### Steppe Raiding System
The border principalities system integrates with the steppe raiding mechanics:
- Tatar settlements (Glinski, Jagoldai, Lipka) provide `local_hostile_attrition` bonuses
- These settlements reduce raid damage from `steppe_raid.1-7` events
- `tatar_border_defense` country modifier stacks with `zasechnaya_cherta`
- Provinces with Tatar modifiers are less likely to be targeted by raids

### Cossack Estate System
Border principalities affect Cossack estate interactions:
- Glinski Tatar cavalry compete with Cossack hosts for influence
- Severian princes' defection can trigger Cossack loyalty shifts
- Orthodox principalities switching to Muscovy strengthen Cossack integration
- Lipka Tatars in PLC provide alternative cavalry, reducing Cossack monopoly

### Muscovite Expansion
The system provides historical justification for Muscovite westward expansion:
- Shemyaka heirs give claims to Lithuanian border regions
- Glinski defection provides military intelligence and commanders
- Severian princes' switch simulates "gathering of Russian lands"
- Qasim Khanate demonstrates ability to rule non-Russian subjects

### Lithuanian Internal Dynamics
For Lithuania/Commonwealth, the system creates internal challenges:
- Border vassals drain resources (tribute payments)
- Risk of defection forces military spending
- Tatar settlements create multi-faith issues
- Orthodox principalities resist integration

## AI Behavior

### Lithuania AI Weights
- **Grant vassal autonomy**: 70-80% (border security valued)
- **Accept Tatar settlements**: 70-80% (pragmatic military need)
- **Fight to keep vassals**: 60-70% (prestige matters)
- **Negotiate with rebels**: 40% (cost-averse)

### Muscovy AI Weights
- **Create Qasim Khanate**: 80% (strategic value high)
- **Support Qasim claims**: 60% (expansionist but cautious)
- **Accept defectors**: 100% (free territory)
- **Annex vs puppet Kazan**: 60% annex / 40% puppet (direct control preferred)

### Modifier Impact on AI
- Low legitimacy: Faster vassal defection (x0.7-0.8 MTTH)
- At war: Increased defection risk (x0.6-0.8 MTTH)
- Strong military: Slower defection (x1.2-1.5 MTTH)
- Alliance with rival: Blocks some events

## Historical Accuracy vs Gameplay

### Authentic Elements
✅ Shemyaka descendants' role in Rylsk  
✅ Glinski rebellion and defection (1508)  
✅ Jagoldai settlement as buffer state  
✅ Severian princes' switch (1500-1503)  
✅ Qasim Khanate as Muscovite tool  
✅ Lipka Tatars in Polish-Lithuanian service  
✅ Religious tensions Orthodox vs Catholic  

### Simplified for Gameplay
⚠️ Timeline compression: Events can fire within narrower windows  
⚠️ Player agency: Historical outcomes can be avoided  
⚠️ Mechanical effects: Some modifiers more powerful than historical impact  
⚠️ Vassal mechanics: EU4 system doesn't perfectly capture period's feudal complexity  
⚠️ Qasim tag: May need creation via event (not in base game)  

### Balance Considerations
- Tatar cavalry bonuses strong but historically justified
- Defection risks force player investment in legitimacy/military
- Muscovy gains significant but require player action
- Lithuania can maintain control with proper management
- Rewards historical play style (tolerant Lithuania, expansionist Muscovy)

## Testing Checklist

### Event Triggers
- [ ] Shemyaka event fires for Lithuania 1444-1500
- [ ] Glinski event fires for Lithuania with Severia/Bryansk
- [ ] Jagoldai event fires for Lithuania with Kursk
- [ ] Rylsk defection event fires 1500-1510
- [ ] Glinski rebellion fires 1507-1515
- [ ] Starodub defection fires 1500-1510
- [ ] Qasim foundation fires 1450-1460 for Muscovy
- [ ] Qasim attacks Kazan fires after 1467
- [ ] Lipka settlement fires 1440-1500 for Lithuania

### Event Chains
- [ ] Rylsk defection triggers Muscovy reception event
- [ ] Glinski rebellion leads to full uprising if negotiation fails
- [ ] Glinski exile triggers Muscovy reception
- [ ] Jagoldai defection triggers Muscovy reception
- [ ] Starodub switch triggers Muscovy reception

### Modifiers Application
- [ ] Province modifiers apply correctly
- [ ] Country modifiers stack appropriately
- [ ] Duration timers work as intended
- [ ] Permanent modifiers remain after save/load
- [ ] Negative modifiers (conquest, refusal) apply penalties

### AI Behavior
- [ ] AI Lithuania accepts vassal arrangements >70%
- [ ] AI Muscovy creates Qasim Khanate >80%
- [ ] AI Lithuania fights for important vassals
- [ ] AI accepts peaceful transfers occasionally
- [ ] AI Muscovy supports Qasim claims

### Integration
- [ ] Tatar settlements reduce steppe raid damage
- [ ] Defections provide CBs and claims
- [ ] Qasim provides Kazan intervention justification
- [ ] Lipka Tatars provide cavalry bonuses
- [ ] Border wars trigger correctly

### Balance
- [ ] Muscovy doesn't blob too fast
- [ ] Lithuania isn't crippled by defections
- [ ] Tatar bonuses aren't overpowered
- [ ] Player has meaningful choices
- [ ] Historical outcomes achievable but not guaranteed

## Files Created/Modified

### New Files
1. **events/BorderPrincipalities.txt** - 12 events for vassal switching
2. **events/QasimKhanate.txt** - 6 events for Qasim and Lipka Tatars
3. **common/event_modifiers/border_principalities_modifiers.txt** - 30+ modifiers
4. **localisation/border_principalities_l_english.yml** - Event and modifier localization
5. **localisation/qasim_khanate_l_english.yml** - Qasim event localization
6. **docs/BORDER_PRINCIPALITIES_SYSTEM.md** - This documentation

### Modified Files
None (all new content in separate files)

## Future Expansion Ideas

1. **Appanage System**: Expand to other regions (Tver, Ryazan, Yaroslavl principalities)
2. **Dynastic Claims**: Implement Rurikid family tree for claim mechanics
3. **Tatar Integration**: Deeper mechanics for Tatar nobility in Russian service
4. **Lithuanian Reforms**: Counter-measures to prevent defections
5. **Qasim Succession**: Events for changing Qasim khans, internal conflicts
6. **Lipka Culture**: Create Lipka Tatar culture group with unique traits
7. **Religious Conversion**: Mechanics for converting Tatar vassals to Orthodoxy
8. **Estate Interactions**: Integrate with nobility/clergy estates for conflicts
9. **Map Changes**: Add more provinces for Severia, split Bryansk area
10. **PLC Formation**: Special events when Lithuania forms Commonwealth affecting vassals
