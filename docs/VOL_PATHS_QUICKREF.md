# VOLHYNIA AUSTRIAN & POLISH PATHS - QUICK REFERENCE

## PATH SELECTION (Position 5)
**Mission**: `VOL_choose_development_path`
- Requires: Not at war, Stability 1+, 200+ dev
- Fires event with two choices:
  1. **Austrian Imperial Path** → Diplomacy & Dynasties
  2. **Polish Constitutional Path** → Sejm & Liberty

---

## AUSTRIAN IMPERIAL PATH

### Key Missions
1. **Balance Estates** → Unlock minority management
2. **Manage Minorities** → Tolerance for foreign cultures
3. **Welcome All Cultures** → Accept more cultures
4. **Develop Capitals** → Volhynia + Halych to 20 dev
5. **Balance of Power** → Alliances + subjects
6. **Dynastic Marriages** → Spread dynasty

### Victory Condition
- 600 dev, 3 countries with dynasty, 3 subjects, Great Power

### Key Modifiers
- `vol_multicultural_realm`: +1 tolerance, -15% foreign advisor cost
- `vol_dynastic_prestige`: +1 legitimacy, +50% heir chance
- `vol_imperial_triumph`: +3 diplo rep, +20% vassal income

---

## POLISH CONSTITUTIONAL PATH

### Key Missions
1. **Manage Magnates** → Balance noble power
2. **Establish Sejm** → Costs 100 ADM, permanent assembly
3. **Constitutional Compact** → Requires ADM tech 10
4. **Ruthenian Liberty** → Golden Liberty analogue
5. **University Expansion** → Education focus
6. **Renaissance Court** → Cultural flowering

### Victory Condition
- 600 dev, Golden Liberty + Stability 3 + Legitimacy 95, Great Power

### Key Modifiers
- `vol_golden_liberty`: -20% stability cost, -15% liberty desire
- `vol_center_of_learning`: -20% dev cost, +25% institution spread
- `vol_constitutional_triumph`: -33% stability cost, +10% admin efficiency

---

## SYNERGY MISSIONS (Both Paths)

1. **Prosperity** → Develop core provinces
2. **Religious Settlement** → 90% religious unity
3. **Ruthenian Hegemony** → 400 dev, promote to Empire
4. **Ruthenia Triumphant** → 600 dev, final mission

---

## FAST STRATEGY GUIDE

### Austrian Path
1. Early: Ally major power (HLC/HUN/POL)
2. Mid: Focus on royal marriages (5+)
3. Late: Spread dynasty to 3+ countries
4. Endgame: Manage multi-ethnic empire

### Polish Path
1. Early: Build noble loyalty
2. Mid: Establish Sejm (save 100 ADM!)
3. Late: Build 3+ universities
4. Endgame: Golden Liberty + high stability

---

## IMPORTANT FLAGS

- `vol_austrian_path` / `vol_constitutional_path`: Path choice (exclusive)
- `vol_sejm_established`: Sejm is active
- `vol_empire_proclaimed`: Empire rank achieved

---

## FILES REFERENCE

- **Missions**: missions/Volhynia_Missions.txt (lines 2580+)
- **Modifiers**: common/event_modifiers/VOL_mission_modifiers.txt
- **Events**: events/VOL_path_events.txt
- **Localization**: 
  - localisation/VOL_austrian_polish_missions_l_english.yml
  - localisation/VOL_path_events_l_english.yml

---

## COMMON ISSUES

**Q: Mission not appearing?**
A: Check flag is set (console: `country_event vol_path_events.1`)

**Q: Can I switch paths?**
A: No, choice is permanent (flags are exclusive)

**Q: AI path preference?**
A: Diplomats choose Austrian, Balanced choose Polish

---

**For full documentation, see**: docs/VOLHYNIA_AUSTRIAN_POLISH_PATHS.md
