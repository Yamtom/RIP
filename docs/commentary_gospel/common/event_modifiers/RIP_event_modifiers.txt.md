# Commentary Gospel ? RIP_event_modifiers.txt

- Source: `common/event_modifiers/RIP_event_modifiers.txt`
- Extraction date: 2026-03-02
- Extracted descriptive comments: 152

## Canonical Excerpts

| Original line | Commentary |
|---:|---|
| 340 | ========================================================================= |
| 341 | ZAPORIZHIAN SICH MILITARY & DIPLOMATIC MODIFIERS (XVI-XVIII ст.) |
| 342 | ========================================================================= |
| 344 | These modifiers represent the Zaporozhian Sich's peak military and |
| 345 | diplomatic capabilities (XVI-XVIII centuries) before Russian suppression (1775). |
| 347 | The Sich was a cossack military democracy characterized by: |
| 348 | - Rapid defensive fortification & relocation against superior forces |
| 349 | - Cavalry raids (chaiky) across Black Sea & Danube steppes |
| 350 | - Diplomatic juggling with Ottoman, Polish, Russian powers |
| 354 | - 200% bonus scaling reflects Sich's specialized military economy |
| 356 | - Trade bonuses reflect Black Sea commerce networks |
| 360 | - Serhii Plokhy, *The Cossacks and Religion in Early Modern Ukraine* (2001) |
| 361 | - Frank Sysyn, *Between Poland and the Ukraine* (1985) |
| 362 | - Timothy Snyder, *Bloodlands* (2010), chapters 1-2 |
| 363 | - Orest Subtelny, *Ukraine: A History* (2009), chapters 5-7 |
| 364 | ========================================================================= |
| 367 | ZAPORIZHIA MODIFIERS - Enhanced to 200% (doubled from baseline) |
| 550 | Mechanics: Diplomatic reputation, improved relations, and tax bump with finite duration to reflect Polish-Lithuanian backing. |
| 551 | Narrative: Models Warsaw and Vilnius underwriting Chernihiv defenses during the Ruina. |
| 552 | References: Zenon Kohut, *Russian Centralism and Ukrainian Autonomy* (1988); Serhii Plokhy, *The Cossack Myth* (2012). |
| 615 | Mechanics: Raises manpower recovery, trims maintenance, and adds defensiveness to show Russian military aid. |
| 616 | Narrative: Echoes the Andrusovo-era agreements where Moscow supplied troops in exchange for influence. |
| 617 | References: Frank Sysyn, *Between Poland and the Ukraine* (1985); Orest Subtelny, *Ukraine: A History* (2009). |
| 631 | Mechanics: Trade efficiency, heathen tolerance, and naval force limit bonus simulating Crimean escorts on grain convoys. |
| 632 | Narrative: Represents the Khanate safeguarding caravans to secure grain and peace along the steppe frontier. |
| 633 | References: Alan Fisher, *The Crimean Tatars* (1978); Victor Ostapchuk, studies on Ottoman-Cossack diplomacy. |
| 1224 | ========================================================================= |
| 1226 | ========================================================================= |
| 1228 | - Mission Integration: Every uz_* modifier below is awarded by the |
| 1229 | Zakarpatta_Missions tree or its supporting events (namespaced uzh.*). |
| 1230 | Numbers mirror specific mission tasks: e.g. uz_ambitious_expansion_modifier |
| 1231 | ("National Revival" finale) reduces diplo-annex cost, while |
| 1232 | uz_protected_frontier and uz_border_guard_union are tied to frontier |
| 1233 | fortification branches. Disaster follow-ups (uz_mountain_gendarmerie, |
| 1234 | uz_amnesty_rollout, uz_opryshky_pacified) are called from the |
| 1237 | * Salt Economy: uz_solotvyno_chambers, uz_salt_chamber_overwatch, |
| 1238 | uz_private_salt_leases improve tax/trade as events 50-55 resolve. |
| 1239 | * Ecclesiastical Balancing: uz_greek_catholic_concord, uz_old_rite_resilience, |
| 1241 | dilemmata (missions/events 51, 201) giving opposing faith bonuses. |
| 1242 | * Identity Paths: uz_slavo_rusyn_identity, uz_ukraino_rusyn_identity, |
| 1244 | outcome branches of mission "Question of Identity" and its follow-ups. |
| 1245 | * Governance Reforms: uz_statute_codification, uz_federal_structure, |
| 1247 | federalization missions, stacking governing cap and reform progress. |
| 1248 | * Pannonian Expansion: uz_pannonian_settlement, uz_backa_colonial_network, |
| 1250 | uz_danubian_monarchy_influence reward conquering the Danubian basin. |
| 1251 | - Gameplay Hooks: Modifiers often add autonomy, loyalty, or culture effects |
| 1252 | that plug into custom triggers (e.g. chose_ruthenian_identity flag). Check |
| 1253 | for synergies in decisions like HetmanateNation and Uzh missions to avoid |
| 1257 | - Border March Legacy: Frontier pieces (uz_protected_frontier, |
| 1258 | uz_carpathian_hegemony) echo Palanok Castle and the Habsburg Military |
| 1259 | Frontier. Identity-focused bonuses evoke Rusyn/Hungarian duality. |
| 1260 | - Salt & Trade Corridors: Solotvyno salt domes, Tysa caravans, and Danube |
| 1261 | exchanges appear through salt modifiers and uz_danube_* suite, portraying |
| 1262 | Huszt as logistics hub between Vienna and the Balkans. |
| 1263 | - Religious Concord: Dual Orthodox/Greek Catholic modifiers dramatise the |
| 1264 | 1646 Union of Uzhhorod and later Karlovac synod compromises. |
| 1265 | - Popular Resistance: Opryshky-related modifiers chart the arc from raids |
| 1266 | (uz_opryshky_raids) to state co-option (uz_rebel_legends, |
| 1267 | uz_opryshky_pacified), reflecting mountain outlaw folklore. |
| 1270 | - "Union of Uzhhorod" (1646) primary accounts compiled by Mykhailo Лучкай |
| 1271 | and František Dvorník's studies on the Greek Catholic Church. |
| 1272 | - Habsburg Military Frontier records on Palanok Fortress (Kriegsarchiv Wien). |
| 1273 | - Roman Drozd, *Oleksa Dovbush: Between History and Legend* (2008) for |
| 1274 | opryshky material; Jaroslav Dashkevych's research on Rusyn uprisings. |
| 1275 | - Economic notes from Austro-Hungarian salt monopoly archives (Solotvyno, |
| 1276 | Maramureș) documenting tax farming vs. state oversight. |
| 1277 | ========================================================================= |
| 1564 | NOTE: dnestr_estuary_modifier already exists in base game (00_event_modifiers.txt) |
| 1565 | with province_trade_power_value = 10. We add additional modifiers below. |
| 1952 | Add any other effects you want for this modifier |
| 2124 | ========================================================================= |
| 2126 | ========================================================================= |
| 2734 | === НОВІ МОДИФІКАТОРИ: ЗАПОРОЗЬКА СІЧ XVII–XVIII ст. === |
| 2736 | Registered Cossacks (XVI–XVII ст.: формалізація козацтва за польськими статтями) |
| 2737 | Історія: Річ Посполита встановила "реєстр" офіційних козаків — платні, дисциплінаційовані, |
| 2738 | але менш вільні. Вільні козаки опиралися цьому як порушенню традицій демократії Січі. |
| 2748 | Free Cossacks Spirit (XVII–XVIII ст.: захист демократичної традиції Січі) |
| 2749 | Історія: Козаки, що відстоюють вільність від польської/російської контролю, |
| 2750 | зберігають демократичні традиції та резистентність до централізації. |
| 2760 | Sich Fortified Against Ottoman Attack (XVII–XVIII ст.: підготовка до знищувального удару) |
| 2761 | Історія: 1656–1657 р. та 1709–1775 — Османська імперія та Крим організовували велики рейди. |
| 2762 | Укріплення Січі були символом опору й надії на вияток від знищення. |
| 2771 | Seeking a Patron Power (XVII–XVIII ст.: дипломатичний пошук союзника) |
| 2772 | Історія: Січь часто шукала покровництво від Польщі, Московії або Туреччини для захисту. |
| 2780 | Sich Relocated (XVI–XVIII ст.: переміщення з одної локації до іншої) |
| 2781 | Історія: Томаківська → Базавлуцька → Микитинська → Чортомлицька → Олешківська. |
| 2782 | Кожне переміщення давало нові можливості, але й знов начиналася адаптація. |
| 2791 | Sich in Ottoman Lands (1709–1775: Олешківська Січ під Османською протекцією) |
| 2792 | Історія: Після поразки Мазепи при Полтаві (1709) частина козаків переміщувалась до |
| 2793 | Олешківської Січі під Кримською залежністю й Османським контролем. |
| 2803 | Cossack Settlement (XVI–XIX ст.: утворення козацьких слобід на кордонах) |
| 2804 | Історія: Слободи як полукочевие поселення вільних людей, організовані козацькими общинами, |
| 2814 | Steppe Brotherhood (XVI–XVIII ст.: союз козаків з іншими степовими народами) |
| 2815 | Історія: Інколи козаки союзувалися з кримськими татарами, ногайцями чи іншими степовимі |
| 2816 | воєнизованими громадами проти спільного ворога (Осман, РП). |
| 2824 | Steppe Alliance (XVI–XVIII ст.: формальний союз з степовими кочівниками) |
| 2830 | Rebellious Cossacks (XVIII ст.: козацька резистентність російському панству) |
| 2831 | Історія: После 1709 р. козаки все более розглядалися як російські васали, але опір |
| 2832 | російській централізації залишився. Бунти, втечі, союзи з Пугачевим. |
| 2841 | Ottoman-Protected Sich (1709–1775: Січь як інструмент Османської політики) |
| 2842 | Історія: Кримські хани й Туреччина використовували уламки Січі як буфер проти Російської експансії. |
| 2851 | Sich Diaspora (1775–XIX ст.:散散的 козацькі громади в екзилі) |
| 2852 | Історія: Після знищення Січі 1775 р. уламки козаків розсіялися: на Кубань (Чорноморське Козацтво), |
| 2853 | на Дунай (Дунайське Козацтво), на Дон, в Туреччину. |
| 2862 | Registered Cossacks (Гетьманщина XVII–XVIII ст.: інтеграція козаків в офіційну структуру) |
| 2863 | Історія: За гетьманства Мазепи й його наступників козацькі полки були переведені на |
| 2864 | постійну службу й включені в военно-адміністративну структуру. |
| 2873 | Hetman Faction Conflict (XVII–XVIII ст.: боротьба старшинських кланів за гетьманство) |
| 2874 | Історія: Вибори гетьмана були часто буремні: старшина розділялась, іноземні держави |
| 2875 | втручалися, нові гетмани мали низьку легітимність. |
| 2884 | Russian-Backed Hetman (XVIII ст.: гетьман, призначений Московією) |
| 2885 | Історія: Після 1709 р. Московія почала прямо призначати гетманів, замість дозволяти їхній вибір. |
| 2894 | ========================================================================= |
| 2895 | SVYDRIGAYLO INDEPENDENCE PATH MODIFIERS (XIV-XV century alternate history) |
| 2896 | ========================================================================= |
| 2898 | XIV-XV century path where Svydrigaylo of Lithuania (сын Ольгерда) successfully |
| 2899 | establishes an independent Ruthenian state, breaking from Grand Duchy of Lithuania. |
| 2900 | This alternate timeline sees Ruthenian confederation maintained through 16th-18th centuries. |
| 2903 | Starshyna Council → Preparation Phase → Independence Declaration → Confederation Formation |
| 2904 | Each phase unlocks additional buffs, prestige, diplomatic benefits. |
| 2907 | - 1399-1432: Svydrigaylo (Свидригайло) claims Ruthenian lands vs Vytautas |
| 2908 | - 1648-1654: Bohdan Khmelnytsky Uprising revives confederation model |
| 2909 | - 1667 onwards: Alternate history maintains multi-power balance vs Russian absorption |
| 2910 | ========================================================================= |
| 2912 | Starshyna Council Formation (XIV-XV ст.: перша формальна організація старшини) |
| 2913 | Механіка: Дозволяє розпочати процес незалежності; стабілізує внутрішні конфлікти. |
| 2914 | Історія: Перша офіціальна структура, в якій козацькі офіцери й литовська аристократія |
| 2915 | обговорюють спільні інтереси незалежної Рутенської держави. |
| 2923 | Preparing for Independence (XV ст.: дипломатична підготовка до розриву) |
| 2924 | Механіка: Підтримка союзників, укріплення армії, набір анти-литовського настрою. |
| 2925 | Історія: За часи підготовки до розриву договорів з Литвою здійснюються переговори |
| 2926 | з Крименьким Ханством, Польщею, і локальними козацькими громадами. |
| 2935 | Independent Ruthenian State (XV ст.: новоутворена вільна держава) |
| 2936 | Механіка: Видаляє модификатори васалізму, додає престиж й дипломатичну репутацію. |
| 2937 | Історія: Рутенська держава визнається як суверенний актор, пропонує альтернативу |
| 2938 | як русинському, так і польському, й литовському домінуванню. |
| 2948 | Kyivan Confederation Established (XV-XVI ст.: об'єднання Рутенських земель) |
| 2949 | Механіка: Максимальні бонуси за об'єднання; додає принципи республіканської традиції |
| 2950 | + легітимності, символізуючи компромісну систему управління (демократія + аристократія). |
| 2951 | Історія: КРУ конфедерація об'єднує Київ (релігійний центр), Гетьманщину (військовий), |
| 2952 | Запоріжжя (демократичне), Чернігів (административне). |
| 2966 | ========================================================================= |
| 2968 | ========================================================================= |
| 2983 | ========================================================================= |
| 2985 | ========================================================================= |
| 3005 | Svydrigaylo's Legacy (XIV-XV ст.: історична реберенція до Свидригайла) |
| 3006 | Механіка: Престиж i легітимність від історичної фігури, яка встановила традицію независимості. |
| 3007 | Історія: Упрочнення ідеї про Рутенське право на самовизначення й опір чужому панству. |
| 3015 | Balance between Rada and Hetmanate (republican tradition converted to legitimacy) |
| 3120 | Optional: Icon for the modifier (uses icons from GFX) |
| 3143 | ========================================================================= |
| 3145 | ========================================================================= |

## Supplemental Excerpts (2026-03-02)

| Current line | Commentary |
|---:|---|
| 1 | council of florenc |
| 20 | Missions of Halicia-Volhynia |
| 90 | Misiioms of kyiv |
| 340 | HISTORICAL CONTEXT: |
| 341 |  |
| 342 | - Democratic militia governance with elected otamans |
| 343 |  |
| 344 | GAME MECHANICS: |
| 345 | - Cavalry modifiers show steppe combat specialization |
| 346 | - Unrest penalties reflect internal democratic conflicts |
| 347 |  |
| 348 | HISTORICAL REFERENCES: |
| 350 | Mission of Zaporizhzhzia |
| 420 | alligned with russia |
| 532 | "Commonwealth Guardianship" modifier |
| 594 | "Muscovite Auxiliaries" modifier |
| 607 | "Crimean Compact" modifier |
| 747 | Mission of Chernihiv |
| 941 | Eastern Sivershchyna provincial history |
| 1167 | Zaz revolt |
| 1198 | UZHHOROD / ZAKARPATTIA MODIFIER CATALOGUE |
| 1199 | TECHNICAL OVERVIEW: |
| 1200 | uzh_opryshky_uprising disaster script. |
| 1201 | - Thematic Clusters: |
| 1202 | uz_karloca_synod_blessing and uz_cathedral_guild_college stem from union |
| 1203 | uz_uhro_rusyn_identity, uz_pan_ruthenian_union represent the three |
| 1204 | uz_dual_monarchy_administration correspond to Palanok -> Komitat -> |
| 1205 | uz_banat_colonists, uz_danube_trade_league, uz_crown_of_saint_stephen, |
| 1206 | stacking conflicts. |
| 1207 |  |
| 1208 | NARRATIVE PILLARS: |
| 1209 |  |
| 1210 | HISTORICAL REFERENCES: |
| 1212 | Zakarpatta_modifiers = { |
| 1246 | Custom modifiers for Zakarpattia missions |
| 1406 | Frontier and expansion modifiers |
| 1496 | === DNIESTER ESTUARY EXPANSION MODIFIERS === |
| 1659 | Cultural and national identity modifiers |
| 1722 | Political development modifiers |
| 1763 | Economic development modifiers |
| 1889 | Add other effects as needed |
| 1938 | THE RUINA MODIFIERS |
| 1975 | ZAPORIZHIA SICH CRISIS MODIFIERS |
| 2006 | HETMANATE SUCCESSION MODIFIERS |
| 2054 | MISSING MODIFIERS - ZAPORIZHIA & HETMANATE DECISIONS/EVENTS |
| 2056 | HETMANATE PROVINCE MODIFIERS |
| 2098 | HETMANATE COUNTRY MODIFIERS |
| 2189 | ZAPORIZHIA PROVINCE MODIFIERS |
| 2219 | ZAPORIZHIA COUNTRY MODIFIERS |
| 2323 | NEW MISSION MODIFIERS |
| 2410 | === NEW ZAPORIZHIA & HETMANATE UNIQUE MODIFIERS === |
| 2412 | Rada modifiers |
| 2422 | Hidden cooldown |
| 2432 | Sich relocation modifiers |
| 2440 | Hidden cooldown |
| 2443 | Chaiky raid modifiers |
| 2465 | Hidden cooldown |
| 2468 | Cossack register modifiers |
| 2501 | Steppe alliance modifiers |
| 2515 | Sloboda modifiers |
| 2537 | Orthodox protector modifiers |
| 2558 | Hetman election modifiers |
| 2591 | Hetmanate cultural modifiers |
| 2615 | Hetmanate autonomy struggle modifiers |
| 2635 | Poltava crisis modifiers |
| 2713 | забезпечували буфер проти татарських рейдів. |
| 2782 | Historical Context: |
| 2783 |  |
| 2784 | Mechanical Basis: |
| 2785 |  |
| 2786 | Narrative Inspiration: |
| 2825 | JEWISH MERCHANT ESTATE MODIFIERS |
| 2840 | COSSACK RAID & KHMElnytsky TIE-INS |
| 2875 | Polesian and Belarusian Event Modifiers |
| 2971 | picture = "fort_icon" |
| 2993 | SLOBOZHANSHCHYNA HISTORICAL PROCESS MODIFIERS |
