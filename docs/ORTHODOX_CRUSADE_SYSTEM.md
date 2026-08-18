# Система православного хрестового походу

> **Звірено з кодом 2026-08-17.** Документ точний: усі перелічені файли на
> місці, крім українського перекладу (див. нижче), а числа в довіднику
> модифікаторів збігаються з `russian_orthodox_modifiers.txt` - Константинополь
> дає +2 престижу, +1 легітимності, +3 дипрепутації та -20% AE, Єрусалим
> +3 престижу. Вікна 1525/1600 і `orthodox_crusade_cooldown` теж на місці;
> звідки взялися саме ці числа, описано в `EVENT_CHAINS_AUDIT_2026-02-28.md`.


## Огляд

The Orthodox Crusade system allows Orthodox and Russian Orthodox nations to declare holy wars to reclaim Constantinople (Byzantium) and Jerusalem from non-Christian rulers. This mechanic provides historical flavor and strategic gameplay options for Orthodox powers.

Система православного хрестового походу дозволяє православним і російським православним державам оголошувати священні війни для відвоювання Константинополя (Візантії) та Єрусалима від нехристиянських правителів. Ця механіка надає історичний колорит та стратегічні ігрові можливості для православних держав.

---

## Структура файлів

```
RIP Mod/
├── decisions/
│   └── OrthodoxCrusadeDecisions.txt         [3 Decisions]
├── events/
│   └── OrthodoxCrusade.txt                  [20 Events]
├── common/
│   ├── event_modifiers/
│   │   └── russian_orthodox_modifiers.txt   [Added 14 Crusade Modifiers]
│   ├── scripted_effects/
│   │   └── russian_orthodox_effects.txt     [Added 7 Crusade Effects]
│   ├── scripted_triggers/
│   │   └── russian_orthodox_triggers.txt    [Added 8 Crusade Triggers]
│   ├── opinion_modifiers/
│   │   └── orthodox_crusade_opinion_modifiers.txt [4 Opinion Modifiers]
│   ├── casus_belli/
│   │   └── orthodox_crusade_cb.txt          [2 Casus Belli]
│   └── wargoal_types/
│       └── orthodox_crusade_wargoals.txt    [2 War Goals]
└── localisation/
    ├── orthodox_crusade_l_english.yml       [Complete English]
    └── orthodox_crusade_l_ukrainian.yml     [PLANNED - does not exist]
```

---

## Основні механіки

### 1. Оголошення хрестових походів

#### Constantinople Crusade Requirements:
- Orthodox or Russian Orthodox religion
- Not a subject nation
- у мирі
- 200+ development
- 100+ church power
- 50+ prestige
- 75+ legitimacy
- Less than 1 war exhaustion
- No active crusade cooldown
- Constantinople not Orthodox

#### Jerusalem Crusade Requirements:
- Same as above, BUT:
- 300+ development (higher requirement)
- 150+ church power
- 75+ prestige
- 80+ legitimacy

### 2. Бонуси хрестового походу

**For Constantinople Crusade Leader:**
- +15% Land Morale
- +1 Army Tradition/year
- -15% Aggressive Expansion
- -3% War Exhaustion
- +15% Manpower Recovery
- +2 Prestige/year
- +20% Church Power

**For Jerusalem Crusade Leader:**
- +20% Land Morale
- +1.5 Army Tradition/year
- -20% Aggressive Expansion
- -5% War Exhaustion
- +20% Manpower Recovery
- +3 Prestige/year
- +30% Church Power
- +2% Missionary Strength

**For Crusade Participants:**
- +8% Land Morale
- +0.5 Army Tradition/year
- +1 Prestige/year
- +15% Church Power
- +10% Manpower Recovery

### 3. Нагороди за перемогу

#### Constantinople Liberation:
- +100 Prestige
- +25 Legitimacy
- +100 of each monarch power
- +200 Church Power
- Постійний "Liberator of Constantinople" modifier
- Constantinople gets +3 to all development
- Постійний bonuses to Constantinople province
- Patriarch of Constantinople restored (Russian Orthodox only)

#### Jerusalem Liberation:
- +150 Prestige
- +50 Legitimacy
- +150 of each monarch power
- +300 Church Power
- Постійний "Liberator of Jerusalem" modifier
- Jerusalem gets +4 to all development
- Becomes Defender of the Faith (if not already)
- Постійний bonuses to Jerusalem province

### 4. Покарання за поразку

If crusade expires without success:
- -50/-75 Prestige
- -10/-15 Legitimacy
- -50/-100 Church Power
- 20-30 year "Failed Crusade" penalty modifier
- 20 year cooldown before another crusade

---

## Ігровий процес

### Фаза 1: оголошення
1. Player meets requirements
2. Makes decision to declare crusade
3. Spends church power (100/150)
4. Receives crusade modifier (50 year duration)
5. Gets special CB on target

### Фаза 2: участь
1. Other Orthodox nations receive event
2. Can choose to join, support, or refuse
3. Joining nations get participant modifier
4. Opinion modifiers apply

### Фаза 3: війна
1. Leader declares war using crusade CB
2. Various events fire during crusade:
   - Battle victories
   - Religious fervor
   - Progress updates
3. Crusade bonuses help in combat

### Фаза 4: завершення
1. If successful: Massive rewards for all participants
2. If failed: Penalties for all involved
3. Cooldown period begins (20 років)

---

## Довідник модифікаторів

### Постійні модифікатори перемоги

**Визволитель Константинополя:**
- +2 Prestige/year
- +1 Legitimacy/year
- +3 Diplomatic Reputation
- -20% AE Impact
- +3% Missionary Strength
- +25% Church Power
- -15% Core Creation Cost
- +25% Improve Relations

**Визволитель Єрусалима:**
- +3 Prestige/year
- +2 Legitimacy/year
- +5 Diplomatic Reputation
- -25% AE Impact
- +5% Missionary Strength
- +35% Church Power
- -20% Core Creation Cost
- +30% Improve Relations
- +3 Tolerance of True Faith

---

## Поведінка ШІ

**AI will declare crusades when:**
- Has Third Rome ideology (2x more likely)
- Is Russia/Muscovy/Kiev (2x more likely)
- Has 40+ (Constantinople) or 50+ (Jerusalem) army size
- не воювати
- Has 100+ military power

**AI will join crusades when:**
- Allied to leader (1.5x more likely)
- не воювати (3x more likely if at war)
- 60-50% base chance depending on crusade type

---

## Стратегічні поради

1. **Wait for the Right Moment:**
   - Declare when target is weak or distracted
   - Build up alliance network first
   
2. **Use Church Power Wisely:**
   - Save 100-150 church power for declaration
   - Don't spend on aspects right before crusade

3. **Coordinate with Allies:**
   - Improve relations with Orthodox nations before declaring
   - Call them into war as participants

4. **Plan for Long War:**
   - Crusade lasts 50 років but war may be shorter
   - Benefits are worth extended conflict

5. **Jerusalem is Harder:**
   - Higher requirements reflect difficulty
   - Better rewards justify the challenge
   - Consider conquering Constantinople first

---

## Інтеграція з наявними системами

**Works with:**
- Russian Orthodox mechanics
- Third Rome ideology
- Church power system
- Patriarch mechanics
- Holy sites system

**Compatible with:**
- Missions (can be crusade objectives)
- Events (triggers special crusade events)
- Modifiers (stacks with other religious bonuses)

---

## Відомі обмеження

1. Custom CBs may need wargoal types properly configured
2. AI evaluation might need balancing after testing
3. Only one crusade can be active at a time
4. Cooldown prevents rapid crusade spam
5. Requires proper province IDs (151=Constantinople, 379=Jerusalem)

---

## 📝 Historical Context / Історичний контекст

The Orthodox Crusade concept reflects several historical ideas:

1. **Reconquest aspirations** - Byzantine Greeks and Orthodox Slavs long desired to reclaim Constantinople after 1453

2. **Third Rome ideology** - Moscow saw itself as the successor to Rome and Constantinople

3. **Holy Land pilgrimage** - Jerusalem remained spiritually important to Orthodox Christianity

4. **Pan-Orthodox unity** - Crusades could unite Orthodox nations against common enemies

5. **Religious motivation** - Orthodox powers often justified expansion through religious duty

---

## 🎨 Future Expansion Ideas

Potential additions:
- Antioch crusade (third holy site)
- Alexandria crusade (fourth holy site) 
- Mount Athos protection events
- Crusader orders for Orthodox
- Relic recovery mechanics
- Multiple crusades simultaneously (if balanced)
- Excommunication for refusing crusade
- Crusade tax collection
- Papal response events for Catholic nations

---

## 📞 Testing Checklist

Before playing:
- [ ] All files copied to correct folders
- [ ] Localization files use UTF-8 with BOM encoding
- [ ] Province IDs verified (151, 379)
- [ ] Test with Orthodox nation
- [ ] Test with Russian Orthodox nation
- [ ] Verify CB grants properly
- [ ] Check event chain triggers
- [ ] Confirm AI declares crusades
- [ ] Test success path
- [ ] Test failure path
- [ ] Verify cooldown works

---

## 🏆 Achievement Ideas (If Making Full Conversion Mod)

- **Deus Vult!** - Win any Orthodox crusade
- **Second Rome Restored** - Successfully complete Constantinople crusade
- **Kingdom of Heaven** - Successfully complete Jerusalem crusade
- **Crusader King** - Complete both crusades
- **The True Faith** - Form Byzantium through crusade conquest
- **Pilgrims' Path** - Control all Orthodox holy sites after crusade

---

Made with ❤️ for the RIP EU4 Mod
Created: 2026-02-05
