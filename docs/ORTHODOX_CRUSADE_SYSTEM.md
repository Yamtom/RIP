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
│   └── OrthodoxCrusadeDecisions.txt         [3 рішення]
├── events/
│   └── OrthodoxCrusade.txt                  [20 подій]
├── common/
│   ├── event_modifiers/
│   │   └── russian_orthodox_modifiers.txt   [+14 модифікаторів походу]
│   ├── scripted_effects/
│   │   └── russian_orthodox_effects.txt     [+7 ефектів походу]
│   ├── scripted_triggers/
│   │   └── russian_orthodox_triggers.txt    [+8 тригерів походу]
│   ├── opinion_modifiers/
│   │   └── orthodox_crusade_opinion_modifiers.txt [4 модифікатори думки]
│   ├── casus_belli/
│   │   └── orthodox_crusade_cb.txt          [2 приводи до війни]
│   └── wargoal_types/
│       └── orthodox_crusade_wargoals.txt    [2 воєнні цілі]
└── localisation/
    ├── orthodox_crusade_l_english.yml       [повна англійська]
    └── orthodox_crusade_l_ukrainian.yml     [ЗАПЛАНОВАНО — не існує]
```

---

## Основні механіки

### 1. Оголошення хрестових походів

#### Вимоги до походу на Константинополь
- православна або російсько-православна релігія
- не бути васалом
- у мирі
- від 200 розвитку
- від 100 церковної влади
- від 50 престижу
- від 75 легітимності
- менш ніж 1 виснаження від війни
- без чинного відкату походу
- Константинополь не православний

#### Вимоги до походу на Єрусалим
- те саме, що вище, але:
- від 300 розвитку — вища вимога
- від 150 церковної влади
- від 75 престижу
- від 80 легітимності

### 2. Бонуси хрестового походу

**Провідникові походу на Константинополь:**
- +15% бойового духу
- +1 армійської традиції на рік
- −15% агресивного розширення
- −3% виснаження від війни
- +15% відновлення живої сили
- +2 престижу на рік
- +20% церковної влади

**Провідникові походу на Єрусалим:**
- +20% бойового духу
- +1.5 армійської традиції на рік
- −20% агресивного розширення
- −5% виснаження від війни
- +20% відновлення живої сили
- +3 престижу на рік
- +30% церковної влади
- +2% сили місіонерів

**Учасникам походу:**
- +8% бойового духу
- +0.5 армійської традиції на рік
- +1 престижу на рік
- +15% церковної влади
- +10% відновлення живої сили

### 3. Нагороди за перемогу

#### Визволення Константинополя
- +100 престижу
- +25 легітимності
- +100 кожної монаршої сили
- +200 церковної влади
- постійний модифікатор «Визволитель Константинополя»
- Константинополь дістає +3 до всього розвитку
- постійні бонуси провінції Константинополь
- відновлено Константинопольського патріарха (лише для російського православ'я)

#### Визволення Єрусалима
- +150 престижу
- +50 легітимності
- +150 кожної монаршої сили
- +300 церковної влади
- постійний модифікатор «Визволитель Єрусалима»
- Єрусалим дістає +4 до всього розвитку
- стаєте Захисником віри, якщо ще ні
- постійні бонуси провінції Єрусалим

### 4. Покарання за поразку

Якщо похід згасає без успіху:
- −50/−75 престижу
- −10/−15 легітимності
- −50/−100 церковної влади
- штрафний модифікатор «Невдалий похід» на 20–30 років
- 20 років відкату до наступного походу

---

## Ігровий процес

### Фаза 1: оголошення
1. Гравець виконує вимоги.
2. Ухвалює рішення оголосити похід.
3. Витрачає церковну владу: 100 або 150.
4. Дістає модифікатор походу на 50 років.
5. Дістає особливий привід до війни проти цілі.

### Фаза 2: участь
1. Інші православні держави дістають подію.
2. Можуть пристати, підтримати або відмовити.
3. Ті, хто пристав, дістають модифікатор учасника.
4. Застосовуються модифікатори думки.

### Фаза 3: війна
1. Провідник оголошує війну за приводом походу.
2. Під час походу спрацьовують події:
   - перемоги в битвах;
   - релігійне завзяття;
   - звіти про поступ.
3. Бонуси походу допомагають у бою.

### Фаза 4: завершення
1. За успіху — великі нагороди всім учасникам.
2. За поразки — кари всім причетним.
3. Починається відкат на 20 років.

---

## Довідник модифікаторів

### Постійні модифікатори перемоги

**Визволитель Константинополя:**
- +2 престижу на рік
- +1 легітимності на рік
- +3 дипломатичної репутації
- −20% агресивного розширення
- +3% сили місіонерів
- +25% церковної влади
- −15% вартості створення ядер
- +25% поліпшення стосунків

**Визволитель Єрусалима:**
- +3 престижу на рік
- +2 легітимності на рік
- +5 дипломатичної репутації
- −25% агресивного розширення
- +5% сили місіонерів
- +35% церковної влади
- −20% вартості створення ядер
- +30% поліпшення стосунків
- +3 терпимості до істинної віри

---

## Поведінка ШІ

**ШІ оголошує похід, коли:**
- має доктрину Третього Риму — удвічі вірогідніше
- це Росія, Московія або Київ — удвічі вірогідніше
- має військо від 40 полків на Константинополь або від 50 на Єрусалим
- не воювати
- має від 100 воєнної сили

**ШІ пристає до походу, коли:**
- є союзником провідника — у півтора раза вірогідніше
- не воює; якщо воює, утричі менш вірогідно
- базовий шанс 50–60% залежно від типу походу

---

## Стратегічні поради

1. **Дочекайтеся слушної миті.**
   - Оголошуйте, коли ціль слабка або відвернена.
   - Спершу збудуйте мережу союзів.
   
2. **Витрачайте церковну владу з розумом.**
   - Тримайте 100–150 на саме оголошення.
   - Не витрачайте на аспекти перед самим походом.

3. **Узгодьте дії з союзниками.**
   - Поліпшіть стосунки з православними державами до оголошення.
   - Кличте їх до війни як учасників.

4. **Готуйтеся до довгої війни.**
   - Похід триває 50 років, війна може бути коротшою.
   - Вигоди виправдовують затяжний конфлікт.

5. **Єрусалим важчий.**
   - Вищі вимоги відповідають складності.
   - Кращі нагороди виправдовують виклик.
   - Подумайте, чи не взяти спершу Константинополь.

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
