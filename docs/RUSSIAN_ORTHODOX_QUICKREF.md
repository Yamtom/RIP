# Російська православна церква — коротка довідка

> **Звірено з кодом 2026-08-17.** Числа нижче були застарілі й тепер
> виправлені: подій **17** (не 15 - додано `.16` і `.17` про Розкол),
> аспектів **7**, благословень **7** (не 6 і 5), модифікаторів **55**,
> рішень **7 country + 2 province**.
>
> Province decisions, які всі три документи перелічували як пункти 8 і 9,
> досі не існували: `force_convert_province_effect` і
> `russify_province_effect` були написані, локалізація для них теж, а самих
> рішень не було - ефекти не викликалися нізвідки. Тепер викликаються.


## Швидкий старт

**Що це таке?**
Наступальний варіант православ'я, що поєднує протестантські й мусульманські механіки поширення з православною традицією. Ставка на розширення, завоювання, русифікацію та доктрину Третього Риму.

**Як навернутися:**
1. бути православною державою
2. тримати Москву або дочекатися події
3. ухвалити рішення «Прийняти православ'я Третього Риму»
4. ШІ за Росію чи Московію навертається сам

---

## Основні механіки

### Церковна влада
- накопичується так само, як у звичайному православ'ї
- витрачається на аспекти (по 100) і благословення (по 50)
- додатковий приріст від завоювань і навернень

### Механіка поширення
**Розширення мусульманського типу:**
- бонуси за завоювання неправославних земель
- можливість примусового навернення провінцій
- бонуси до сили місіонерів
- переваги при наверненні культури

**Головна відмінність від греко-католицтва:**
- греко-католицтво поширюється дипломатично, як протестантські центри
- російське православ'я поширюється завоюванням

---

## Сім аспектів — вибирайте зважено

| Аспект | Ціна | Головні бонуси | Коли брати |
|--------|------|--------------|--------------|
| **Third Rome Mission** | 100 CP | +10% Morale, +1 Diplomat | перший вибір, основа |
| **Patriarch Authority** | 100 CP | +10% Tax, +5% Admin Efficiency | після заснування патріархату |
| **Orthodox Inquisition** | 100 CP | +2% Missionary Strength | коли маєте справу з єрессю |
| **Forced Russification** | 100 CP | -25% Culture Conversion Cost | розширення в середній грі |
| **Imperial Orthodox Church** | 100 CP | +10% Production, +1 Absolutism | пізня гра, після реформ |
| **Subjugation of Heretics** | 100 CP | +15% Fort Defense, +0.5 Army Tradition | постійна війна |

**Рекомендований порядок від ранньої до пізньої гри:**
1. Місія Третього Риму — основа
2. Влада патріарха — економіка
3. Православна інквізиція — релігійна єдність
4. Упокорення єретиків — військо
5. Примусова русифікація — культура
6. Імперська православна церква — фінал

---

## 🙏 7 Blessings (Temporary Buffs - 20 Years)

| Благословення | Ціна | Ефект | Коли найкраще |
|----------|------|--------|---------------|
| Третій Рим | 50 | +10% бойового духу, +10% дисципліни | перед великими війнами |
| Патріарх Московський | 50 | +10% податків, +10% виробництва | відновлення економіки |
| Православне завоювання | 50 | −10% вартості ядер, −20% агресивного розширення | під час розширення |
| Культурне панування | 50 | −25% вартості навернення культури | культурні кампанії |
| Релігійна єдність | 50 | +3% місіонерів, −2 заворушень | після завоювань |

**Порада.** Тримайте «Православне завоювання» ввімкненим, коли робите ядра на нових землях: зниження агресивного розширення тут дуже відчутне.

---

## Рішення гравця

### Рішення країни

1. **Прийняти православ'я Третього Риму**
   - навертає вас у російське православ'я
   - потребує: бути православним, тримати Москву або мати російську культуру
   - робіть якнайраніше заради бонусів

2. **Заснувати Московський патріархат** ⭐
   - відкриває аспект «Влада патріарха»
   - потребує: тримати Москву, бути російсько-православним і ще не мати патріархату
   - великий приріст престижу (+100)

3. **Розпочати кампанію русифікації**
   - на 20 років: −25% вартості навернення культури
   - потребує: мати неросійські культури в державі
   - увага: підвищує заворушення в зачеплених провінціях

4. **Заснувати православну інквізицію**
   - на 20 років: +2% сили місіонерів, +1 нетерпимості
   - потребує: мати єретичні чи іновірні провінції
   - увага: суворі штрафи до стабільності

5. **Збирання руських земель** ⭐
   - постійні претензії на всі провінції російської культури
   - привід до війни проти держав, що тримають руські землі
   - потребує: бути російсько-православним, російської культури й не володіти всіма руськими землями
   - історичний відіграш: «Москва збирає руські землі»

6. **Встановити симфонію влад**
   - постійно: +1 абсолютизму, +5% адмін-ефективності
   - потребує: мати патріархат і абсолютизм понад 50
   - втілює єдність церкви й держави за візантійським ідеалом

7. **Проголосити православну імперію**
   - величезний модифікатор престижу
   - потребує: ранг імперії й контроль щонайменше трьох православних святинь
   - фінальне рішення для відіграшу

### Рішення провінції

8. **Примусово навернути провінцію**
   - миттєво навертає провінцію в російське православ'я
   - увага: +10 заворушень на 10 років і спустошення
   - вживайте ощадливо, лише для стратегічних провінцій

9. **Русифікувати провінцію**
   - миттєво навертає культуру на російську
   - увага: +8 заворушень на 8 років
   - швидше за звичайне навернення культури

---

## Ключові події, за якими варто стежити

### Історичні події (з датами)

| Подія | Дата | Що стається |
|-------|------|--------------|
| Fall of Constantinople | 1453 | Choose to embrace Third Rome ideology or stay traditional |
| Moscow Patriarchate | 1589 | Establish independent patriarchate (massive prestige) |
| Conquest of Kazan | 1552 | Policy towards Muslim subjects (force convert vs tolerance) |
| Old Believer Schism | 1650s | Church reforms cause split - suppress or tolerate? |

### Випадкові події (можуть спрацювати будь-коли)

- **Newly Conquered Province** (when you take land)
  - Choose: Force conversion / Establish missions / Allow freedom

- **Russification Campaign** (random)
  - Choose: Aggressive Russification / Gradual integration / Respect cultures

- **Conquest of Constantinople!** (IF you take Constantinople)
  - Fulfill Third Rome destiny!
  - Massive bonuses and prestige

- **Cultural Resistance Movement**
  - Local peoples resist Russification
  - Choose: Suppress harshly / Grant concessions

---

## Військова стратегія

### Армійські бонуси
- Third Rome Mission: +10% Morale
- Third Rome Blessing: +10% Morale, +10% Discipline
- Subjugation of Heretics: +0.5 Yearly Army Tradition, +15% Fort Defense

**Recommended Military Build:**
1. Take "Third Rome Mission" aspect first
2. Stack with "Third Rome" blessing before wars
3. Use "Subjugation of Heretics" for constant warfare
4. Combine with Russian/Slavic national ideas for military dominance

---

## Стратегія розширення

### Рання гра (1444–1550)
1. Convert to Russian Orthodox ASAP (if Muscovy/Russia)
2. Take "Third Rome Mission" aspect
3. Use "Gathering Russian Lands" decision for claims
4. Expand into Orthodox lands first (less AE)

### Середня гра (1550–1650)
1. Establish Moscow Patriarchate (decision)
2. Take "Orthodox Inquisition" aspect
3. Use "Orthodox Conquest" blessing during wars
4. Start Russification of non-Russian cores

### Пізня гра (1650–1821)
1. Take "Imperial Orthodox Church" aspect
2. Establish Symphonia (if high Absolutism)
3. Proclaim Orthodox Empire (if Empire rank)
4. Culture convert strategic provinces

---

## Поради досвідченим

### Керування церковною владою
- Don't spend all CP immediately
- Save 50 CP for "Orthodox Conquest" blessing before big wars
- Prioritize aspects over blessings (постійний vs temporary)

### Culture Conversion
- Use "Russification Campaign" decision before manual conversions
- Take "Forced Russification" aspect
- Use "Cultural Dominance" blessing
- **Stack all three for -50% culture conversion cost!**

### Керування агресивним розширенням
- Always use "Orthodox Conquest" blessing when expanding
- -20% AE is huge for large conquests
- Combine with Improve Relations advisors and diplomats

### Religious Unity
- Force convert strategic provinces only
- Use missionaries for regular conversion
- Take "Orthodox Inquisition" aspect
- Use "Religious Unity" blessing to reduce unrest

---

## 🎭 Roleplay Flavor

### Third Rome Ideology
*"Two Romes have fallen, but the third stands, and a fourth there shall not be."*

Play as successor to Rome and Byzantium. Your mission: unite all Orthodox lands under Russian rule and protect true faith from heresy.

### Historical Nations for Russian Orthodox

**Primary:**
- Muscovy → Russia
- Novgorod (if survives)
- Pskov (if survives)

**Alternative History:**
- Kiev → Ruthenia (Third Rome from Kiev instead of Moscow)
- Beloozero (minor Orthodox nation)
- Any Orthodox nation pursuing Third Rome ideology

---

## ⚖️ Balance Comparison

| Category | Russian Orthodox | Greek Catholic | Regular Orthodox |
|----------|------------------|----------------|------------------|
| **Military** | 🟢🟢🟢 Very Strong | 🟡 Moderate | 🟡 Moderate |
| **Economy** | 🟡 Moderate | 🟢🟢 Strong | 🟡 Moderate |
| **Diplomacy** | 🔴 Weak | 🟢🟢🟢 Very Strong | 🟡 Moderate |
| **Missionary** | 🟢🟢🟢 Very Strong | 🟢🟢 Strong | 🟡 Moderate |
| **Culture Convert** | 🟢🟢🟢 Very Strong | 🟢 Moderate | 🔴 Weak |
| **AE Impact** | 🔴 High (but reducible) | 🟢🟢 Low | 🟡 Moderate |
| **Stability** | 🔴 Low (high unrest) | 🟢🟢 High | 🟢 Moderate |

**Best For:**
- **Russian Orthodox**: Aggressive military expansion, conquest, Russification
- **Greek Catholic**: Diplomatic expansion, cultural synthesis, peaceful growth
- **Regular Orthodox**: Balanced gameplay, traditional approach

---

## 🔧 Troubleshooting

**Q: How do I convert to Russian Orthodox?**
A: Use the "Embrace Third Rome Orthodoxy" decision (in Decisions menu, Religion tab)

**Q: I don't see the decision to convert**
A: You need to be Orthodox AND either (1) control Moscow, OR (2) be Russian culture, OR (3) have the "Third Rome" event fire

**Q: My provinces have massive unrest after forced conversion**
A: Expected. Use "Religious Unity" blessing or wait it out. Don't force convert too many provinces at once.

**Q: Should I take "Forced Russification" aspect?**
A: Only if you're actively culture converting. Otherwise, skip it for military/economic aspects.

**Q: When should I establish the Inquisition?**
A: When you have many heretic/heathen provinces causing religious unity problems. Not needed early game.

**Q: Can I switch back to regular Orthodox?**
A: No, conversion is постійний (like Protestant/Reformed split)

---

## 📈 Optimization Checklist

### Early Priorities
- [ ] Convert to Russian Orthodox
- [ ] Take "Third Rome Mission" aspect
- [ ] Establish Moscow Patriarchate (decision)
- [ ] Use "Gathering Russian Lands" for claims

### Mid Game Goals
- [ ] Take "Orthodox Inquisition" aspect
- [ ] Launch Russification Campaign (if non-Russian cultures)
- [ ] Stack culture conversion modifiers
- [ ] Maintain "Orthodox Conquest" blessing during wars

### Late Game Achievements
- [ ] Take all 7 aspects
- [ ] Establish Symphonia of Powers
- [ ] Proclaim Orthodox Empire
- [ ] Convert Constantinople (if conquered)
- [ ] Achieve religious and cultural unity

---

## 🎯 Achievement Ideas (Unofficial)

**"Third Rome"**
- As Russian Orthodox nation, control Rome, Constantinople, and Moscow

**"Gathering of Lands"**
- As Russia, unite all Russian culture provinces using "Gathering Russian Lands" decision

**"Orthodox Inquisition"**
- Convert 100 provinces using forced conversion

**"Russified"**
- Have 80% of your provinces be Russian culture

**"Symphonia"**
- Establish Symphonia of Powers with 90+ Absolutism

---

## 📞 See Also

- **Full Documentation**: `RUSSIAN_ORTHODOX_README.md`
- **Implementation Details**: `RUSSIAN_ORTHODOX_IMPLEMENTATION.md`
- **Related System**: Greek Catholic Church (diplomatic alternative)

---

**Version**: 1.0.0
**Last Updated**: 2025
**Author**: RIP Mod Team

*Glory to the Third Rome!*
