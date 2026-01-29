# VOLHYNIA (VOL) - AUSTRIAN & POLISH DEVELOPMENT PATHS
## Comprehensive Mission System Documentation

**Last Updated**: January 30, 2026  
**Version**: 1.0  
**Author**: Yamtom

---

## EXECUTIVE SUMMARY

This document describes the new dual-path mission system for Volhynia (VOL), inspired by historical developments of Austria-Hungary (HAB) and the Polish-Lithuanian Commonwealth (PLC). The system allows players to choose between two distinct development paths:

1. **Austrian Imperial Path**: Emphasizes diplomatic marriages, managing diverse ethnic groups, and building a prestige-based empire
2. **Polish Constitutional Path**: Focuses on constitutional reforms, noble participation in government, and cultural flowering

---

## HISTORICAL INSPIRATION

### Austrian Habsburg Model (HAB)
The Habsburg missions in EU4 showcase:
- **Multi-ethnic Empire Management**: `emp_hab_the_hungarian_question`, `emp_hab_all_minorities_are_welcome`
- **Diplomatic Web**: `emp_hab_balance_of_power`, `emp_hab_spread_dynasties`
- **Imperial Prestige**: `emp_hab_imperial_capitals`, dynastic marriages
- **Balance of Power**: Playing great powers against each other

### Polish-Lithuanian Commonwealth Model (PLC)
The Polish missions demonstrate:
- **Constitutional Development**: `pol_great_sejm`, `plc_golden_liberty`, `plc_articles_agreement`
- **Magnate Management**: `pol_leverage_magnates`
- **Cultural Renaissance**: `plc_cultural_flowering`
- **Educational Investment**: `pol_expand_krakow_university`

---

## MISSION TREE STRUCTURE

### Path Selection (Position 5, Slot 5)
**Mission**: `VOL_choose_development_path`
- **Trigger**: 
  - Not at war
  - Stability ≥ 1
  - Total development ≥ 200
- **Effect**: Fires event `vol_path_events.1` for path selection

### Austrian Imperial Path (Slots 1-2)

#### Slot 1: Estate & Minority Management
1. **VOL_balance_estates** (Position 6)
   - Requires balanced estate loyalty (60% each)
   - Crown land ≥ 30%
   - Unlocks minority management

2. **VOL_manage_minorities** (Position 7)
   - Requires 5+ provinces of foreign culture with low unrest
   - Grants `vol_multicultural_realm` modifier
   - Applies `vol_minority_rights` to minority provinces

3. **VOL_welcome_all_cultures** (Position 8)
   - Requires accepting Polish culture + 2 accepted cultures
   - Grants permanent `vol_cultural_tolerance` modifier
   - Auto-accepts Lithuanian culture

#### Slot 2: Diplomatic & Dynastic Network
1. **VOL_develop_capitals** (Position 7)
   - Develop Volhynia (280) and Halych (279) to 20 dev
   - Grants `vol_twin_capitals` modifier
   - Adds permanent province modifiers

2. **VOL_balance_of_power** (Position 8)
   - Alliance with major power (POL/LIT/HUN/MOS/HLC)
   - 2 subjects OR 300+ subject development
   - Prestige ≥ 40

3. **VOL_dynastic_marriages** (Position 9)
   - 5 royal marriages
   - 3 countries with your dynasty OR high opinion
   - Grants `vol_dynastic_prestige` modifier

### Polish Constitutional Path (Slots 3-4)

#### Slot 3: Constitutional Development
1. **VOL_manage_magnates** (Position 6)
   - Noble estate influence ≥ 40%, loyalty ≥ 60%
   - Grants `vol_magnate_support` modifier

2. **VOL_establish_sejm** (Position 7)
   - Costs 100 ADM
   - Noble loyalty ≥ 70%
   - Grants permanent `vol_ruthenian_sejm` modifier

3. **VOL_constitutional_compact** (Position 8)
   - ADM tech ≥ 10
   - Full idea group (Aristocracy/Plutocracy/Administrative)
   - Grants `vol_constitutional_framework` modifier

4. **VOL_ruthenian_liberty** (Position 9)
   - Stability ≥ 2
   - Legitimacy ≥ 90
   - Prestige ≥ 50
   - Grants permanent `vol_golden_liberty` modifier

#### Slot 4: Cultural & Educational Development
1. **VOL_church_relations** (Position 7)
   - Church estate loyalty ≥ 60%
   - Religious unity ≥ 80%

2. **VOL_university_expansion** (Position 8)
   - University in capital (280)
   - Innovativeness ≥ 5
   - Grants `vol_center_of_learning` to capital

3. **VOL_renaissance_court** (Position 9)
   - 3 provinces with universities
   - Innovativeness ≥ 10
   - Renaissance OR Printing Press institution

4. **VOL_education_edict** (Position 10)
   - 5 provinces with 15+ dev
   - Grants permanent `vol_enlightened_realm` modifier

### Synergy Missions (Slot 5, Both Paths)

1. **VOL_prosperity** (Position 6)
   - 10 provinces in core areas with 15+ dev, no devastation
   - Path-specific bonuses: Mercantilism (Austrian) or Income (Polish)

2. **VOL_religious_settlement** (Position 7)
   - Religious unity ≥ 90%
   - Either multicultural or magnate support modifier

3. **VOL_ruthenian_hegemony** (Position 8)
   - Total development ≥ 400
   - Army size ≥ 40
   - Empire rank OR (Prestige ≥ 75 AND Legitimacy ≥ 90)
   - Promotes to Empire rank if not already

4. **VOL_ruthenia_triumphant** (Position 9)
   - Total development ≥ 600
   - Great Power status
   - Path-specific requirements:
     - **Austrian**: 3 countries with your dynasty, 3 subjects
     - **Polish**: Golden Liberty + Stability 3 + Legitimacy 95

---

## MODIFIERS REFERENCE

### Austrian Path Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `vol_balanced_estates` | -10% Stability Cost, +0.5 Yearly Absolutism | 20 years |
| `vol_multicultural_realm` | +1 Tolerance Heretic/Heathen, -15% Foreign Advisor Cost | 25 years |
| `vol_minority_rights` | -2 Local Unrest, -0.05 Local Autonomy | Permanent |
| `vol_cultural_tolerance` | +1 Accepted Culture, -25% Promote Culture Cost | Permanent |
| `vol_twin_capitals` | +1 Prestige, +1 Diplomatic Reputation, +0.5 Legitimacy | 30 years |
| `vol_diplomatic_ascendancy` | +2 Diplomatic Reputation, +20% Improve Relations | 25 years |
| `vol_dynastic_prestige` | +1 Legitimacy, +50% Heir Chance, +1 Diplomatic Slot | 30 years |

### Polish Path Modifiers

| Modifier | Effects | Duration |
|----------|---------|----------|
| `vol_magnate_support` | +10% Noble Loyalty, +5% Noble Influence, +5% Morale | 20 years |
| `vol_ruthenian_sejm` | -15% Stability Cost, +10% Governing Capacity, +10% Reform Progress | Permanent |
| `vol_constitutional_framework` | +5% Admin Efficiency, -15% State Maintenance, -0.10 Corruption | 30 years |
| `vol_golden_liberty` | -20% Stability Cost, -15% Liberty Desire, +1 Diplomat | Permanent |
| `vol_center_of_learning` | -20% Dev Cost, +25% Institution Spread, +1 Building Slot | Permanent |
| `vol_educational_reform` | -5% Idea Cost, -5% Tech Cost, +0.25 Innovativeness | 25 years |
| `vol_cultural_flowering` | +1 Prestige, -15% Advisor Cost, +25% Institution Spread | 30 years |
| `vol_enlightened_realm` | -15% Embrace Cost, -10% Tech/Idea Cost | Permanent |

### Synergy Modifiers (Both Paths)

| Modifier | Effects | Duration |
|----------|---------|----------|
| `vol_prosperous_realm` | +15% Tax, +10% Production/Trade Efficiency | 25 years |
| `vol_religious_harmony` | +15% Religious Unity, +2 Tolerance Own | 30 years |
| `vol_ruthenian_empire` | +1 Prestige/Legitimacy, +150 Gov Capacity, +5% Admin Efficiency | Permanent |
| `vol_imperial_triumph` | +3 Diplo Rep, +30% Improve Relations, +20% Vassal Income, -25% LD | Permanent |
| `vol_constitutional_triumph` | -33% Stability Cost, +25% Reform Progress, +25% Gov Capacity, +10% Admin Efficiency | Permanent |

---

## EVENT SYSTEM

### Main Path Selection Event
**ID**: `vol_path_events.1`
- **Trigger**: Mission `VOL_choose_development_path` completion
- **Options**:
  1. Austrian Path → Sets `vol_austrian_path` flag, grants `vol_diplomatic_focus` (20 years)
  2. Polish Path → Sets `vol_constitutional_path` flag, grants `vol_constitutional_focus` (20 years)

### Recurring Events

| Event ID | Title | Trigger | Mean Time to Happen |
|----------|-------|---------|---------------------|
| `vol_path_events.2` | Royal Marriage Success | Austrian path, dynastic prestige modifier, 4+ marriages | 120 months |
| `vol_path_events.3` | Sejm Deliberation | Polish path, Sejm modifier, stability 1+ | 120 months |
| `vol_path_events.4` | Cultural Flowering | Either path, cultural modifier, university in capital | 180 months |
| `vol_path_events.5` | Minority Integration | Austrian path, multicultural modifier, minority provinces | 120 months |
| `vol_path_events.6` | Constitutional Reform | Polish path, constitutional framework, 50+ reform progress | 150 months |
| `vol_path_events.7` | Empire Proclaimed | Empire flag set | 7 days |

---

## AI BEHAVIOR

### Path Selection AI Weights
**Austrian Path** favored by:
- Diplomat personality (×2)
- 2+ subjects (×2)
- Alliance with HUN/POL (×1.5)

**Polish Path** favored by:
- Balanced personality (×2)
- Elective monarchy reform (×2)
- Noble estate influence ≥ 50% (×1.5)

### Mission Priorities
- Austrian missions have AI weight 500 for conquest missions (historical accuracy)
- Constitutional missions weight administrative efficiency over expansion
- Synergy missions prioritize development over warfare

---

## INTEGRATION WITH EXISTING SYSTEMS

### Compatibility with HLC Synergy
- Both paths work with existing `rip_vol_eastern_path` and `rip_vol_baltic_path` flags
- VOL_choose_development_path mission can be taken after VOL_invest_in_west_rus_mission
- Does NOT replace HLC-VOL alliance mechanics, adds parallel development

### Province References
- **Capital**: Volhynia (280)
- **Secondary Capital**: Halych (279)
- **Core Areas**: volhynia_area, red_ruthenia_area, podolia_volhynia_area

### Flag Management
- `vol_austrian_path` / `vol_constitutional_path`: Exclusive flags set by path choice
- `vol_can_manage_minorities`: Unlocked after balancing estates (Austrian)
- `vol_magnate_alliance`: Unlocked after magnate management (Polish)
- `vol_sejm_established`: Set after establishing Sejm
- `vol_constitutional_ready`: Set after constitutional compact
- `vol_balance_master`: Set after balance of power mission
- `vol_empire_proclaimed`: Set after hegemony mission
- `vol_empire_celebration`: Prevents duplicate empire event

---

## DESIGN PHILOSOPHY

### Austrian Path Philosophy
Emulates Habsburg multi-ethnic empire management:
- **Diplomatic Over Military**: Prestige and marriages trump conquest
- **Tolerance**: Managing diversity as strength, not weakness
- **Dynastic Networks**: Spreading influence through bloodlines
- **Balance of Power**: Playing great powers against each other

### Polish Path Philosophy
Reflects PLC constitutional uniqueness:
- **Participatory Government**: Nobles as partners, not subjects
- **Legal Framework**: Constitution as source of legitimacy
- **Cultural Investment**: Education and enlightenment as power base
- **Institutional Strength**: Sejm and reforms as stability mechanism

### Key Differences from Historical Models
1. **VOL lacks HRE mechanics** → Austrian path uses dynasty spread instead of imperial authority
2. **VOL lacks elective monarchy baseline** → Polish path can unlock it but doesn't require it
3. **Both paths converge on Ruthenian Empire** → Unlike HAB/PLC separation, VOL creates unified endpoint with path-specific bonuses

---

## RECOMMENDED STRATEGIES

### Austrian Path Strategy
1. **Early Game**: Secure independence, ally with HLC or major power
2. **Mid Game**: Balance estates (mission 1), develop capitals, start marriage network
3. **Late Game**: Focus on dynastic spread, manage minorities, aim for 3+ thrones
4. **Victory Condition**: 600 dev, 3 dynasties, 3 subjects, Great Power status

### Polish Path Strategy
1. **Early Game**: Build noble loyalty, stabilize realm
2. **Mid Game**: Establish Sejm (ADM cost!), secure church support
3. **Late Game**: University chain, constitutional framework, Golden Liberty
4. **Victory Condition**: 600 dev, Golden Liberty + Stability 3 + Legitimacy 95, Great Power

### Hybrid Approach
- **Not possible**: Flags are mutually exclusive
- **Choose based on**: Starting alliances (HUN/POL favors Austrian), noble estate power (high favors Polish)
- **AI will pick**: Based on personality and diplomatic situation

---

## FILES CREATED/MODIFIED

### Mission Files
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\missions\Volhynia_Missions.txt**
  - Added 3 new mission branches (VOL_austrian_imperial_path_slot1/2, VOL_polish_constitutional_path_slot3/4, VOL_synergy_missions_slot5)
  - Total: 20 new missions

### Modifier Files
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\common\event_modifiers\VOL_mission_modifiers.txt**
  - 28 new modifiers (path-specific + synergy + event modifiers)

### Event Files
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\events\VOL_path_events.txt**
  - 7 events for path choice, recurring events, and empire proclamation

### Localization Files
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\localisation\VOL_austrian_polish_missions_l_english.yml**
  - Mission titles, descriptions, tooltips, modifier names/descriptions
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\localisation\VOL_path_events_l_english.yml**
  - Event text and options

### Opinion Modifier Files
- **d:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP\common\opinion_modifiers\RIP_opinion_modifiers.txt**
  - 3 new opinion modifiers for dynastic/constitutional relations

---

## TESTING CHECKLIST

- [ ] Path selection event fires correctly after VOL_choose_development_path
- [ ] Austrian path missions appear only with `vol_austrian_path` flag
- [ ] Polish path missions appear only with `vol_constitutional_path` flag
- [ ] Synergy missions appear with either flag set
- [ ] Modifiers apply correctly with specified durations
- [ ] Events fire with correct MTTH
- [ ] Opinion modifiers work in diplomacy screen
- [ ] Mission completion grants correct claims/modifiers
- [ ] AI selects path based on personality/situation
- [ ] Final missions (triumphant) check path-specific requirements
- [ ] No syntax errors in mission/event/modifier files
- [ ] Localization displays correctly in English

---

## FUTURE EXPANSION IDEAS

1. **Government Reforms**: Create VOL-specific reforms for each path
   - Austrian: "Multinational Administration" (+tolerance, +diplomat)
   - Polish: "Ruthenian Sejm" (+reform progress, -absolutism)

2. **Unique Units**: Path-specific unit models/pips
   - Austrian: "Imperial Hussars" (cavalry focus)
   - Polish: "Sejm Levy" (infantry focus, reduced cost)

3. **Religious Mechanics**: Path interaction with Orthodox/Uniate churches
   - Austrian: Tolerance-based
   - Polish: Synod-based (like PLC mechanics)

4. **Trade Company Integration**: Austrian path could get trade company bonuses in Black Sea
5. **Cultural Union Mechanics**: Polish path could form "West Ruthenian" cultural union

---

## TROUBLESHOOTING

### Mission Not Appearing
- Check country tag (VOL only)
- Verify flag is set (`vol_austrian_path` or `vol_constitutional_path`)
- Confirm position slot is not occupied by another mission
- Check potential triggers (DLC requirements if any added later)

### Event Not Firing
- Verify trigger conditions (modifiers, flags, etc.)
- Check event namespace (vol_path_events)
- Confirm MTTH is reasonable (120-180 months standard)

### Modifier Not Applying
- Check spelling in event/mission effect and modifier file
- Verify duration syntax (years vs. days vs. permanent with -1)
- Confirm modifier file loaded (no syntax errors blocking it)

---

## CREDITS & ACKNOWLEDGMENTS

**Paradox Interactive**: Base game mechanics and historical mission inspiration  
**EU4 Modding Community**: Tools and documentation  
**Historical Sources**: Habsburg and PLC political history research  

**Special Thanks**:
- Austrian mission tree designers for multi-ethnic management framework
- Polish mission tree designers for constitutional development mechanics
- RIP mod team for existing Volhynia/HLC synergy system

---

## CHANGELOG

### Version 1.0 (January 30, 2026)
- Initial implementation of dual-path system
- 20 new missions across 5 slots
- 28 modifiers for path progression
- 7 events for path choice and progression
- Complete English localization
- Documentation created

---

## APPENDIX: CODE SNIPPETS

### Example: Checking Path in Trigger
```
trigger = {
    has_country_flag = vol_austrian_path
    has_country_modifier = vol_dynastic_prestige
}
```

### Example: Path-Specific Reward
```
effect = {
    if = {
        limit = { has_country_flag = vol_austrian_path }
        add_mercantilism = 3
    }
    else_if = {
        limit = { has_country_flag = vol_constitutional_path }
        add_years_of_income = 1.0
    }
}
```

### Example: AI Path Selection Weighting
```
ai_chance = {
    factor = 50
    modifier = {
        factor = 2
        personality = ai_diplomat
    }
    modifier = {
        factor = 1.5
        alliance_with = HUN
    }
}
```

---

**END OF DOCUMENTATION**
