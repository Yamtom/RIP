# Commentary Gospel ? uzh_opryshky_uprising.txt

- Source: `common/disasters/uzh_opryshky_uprising.txt`
- Extraction date: 2026-03-02
- Extracted descriptive comments: 56

## Canonical Excerpts

| Original line | Commentary |
|---:|---|
| 1 | ========================================================================= |
| 3 | ========================================================================= |
| 6 | The Opryshky (Опришки) were Carpathian mountain outlaws active in the |
| 7 | 17th-18th centuries across Zakarpattia, Galicia, Bukovyna, and Maramureș. |
| 8 | Born from the valach (Wallachian) legal tradition granting pastoral autonomy, |
| 9 | these brotherhoods evolved into resistance movements against feudal |
| 10 | exploitation, Habsburg centralization, and salt monopoly abuses. |
| 13 | - Oleksa Dovbush (Олекса Довбуш, 1700-1745): Most famous opryshky leader, |
| 14 | operated from the Carpathian forests, raiding noble estates and |
| 15 | redistributing wealth. Became a folk hero celebrated in Hutsul songs. |
| 16 | - Vasyl Bailiuk (Василь Байлюк, early 1700s): Led bands in Maramureș |
| 17 | - Ivan Boichuk (Іван Бойчук): Active in Zakarpattia borderlands |
| 18 | - Hryts Pyntya (Гриць Пинтя, 1670s): Earlier opryshky captain |
| 21 | - Valach Law (Волоське право): Medieval charters granting mountain shepherds |
| 22 | tax exemptions and self-governance in exchange for border guard duties |
| 23 | - Salt Monopoly: Habsburg and Polish crown monopolies on Carpathian salt |
| 24 | mines (Solotvyno, Kosiv) created smuggling economies and brutal enforcement |
| 25 | - Serfdom Pressures: 17th-18th century re-imposition of corvée labor |
| 26 | (robota/панщина) drove free peasants into outlaw bands |
| 27 | - Counter-Reformation: Religious pressure on Orthodox/Uniate communities |
| 31 | This disaster simulates the Opryshky phenomenon through a multi-stage |
| 32 | escalation system that mirrors historical patterns of peasant unrest, |
| 36 | - Historical Era: Age of Absolutism/Revolutions (post-1650) |
| 37 | Reflects the intensification of state centralization vs. traditional rights |
| 38 | - Low Stability (<1): Represents weak governance allowing banditry to flourish |
| 39 | - Economic/Military Stress: War exhaustion, rebel provinces, or manpower |
| 40 | depletion simulate the conditions that drove peasants to opryshky bands |
| 43 | - +3 Global Unrest: Mountain parishes and lowland estates both suffer raids |
| 44 | - -15% Manpower Recovery: Young men join opryshky bands instead of levies |
| 45 | - -10% Production: Salt roads are unsafe, caravans are ambushed, trade disrupted |
| 49 | - High War Exhaustion (+50% at 5+): Returning veterans swell bandit ranks |
| 50 | - Rebel Provinces (+25%): Demonstrates state weakness, emboldens opryshky |
| 51 | - Manpower Depletion (+20% under 30%): Desperation drives recruitment |
| 54 | - uz_mountain_gendarmerie (-15%): Palanok watch patrols suppress bands |
| 55 | - uz_amnesty_rollout (-25%): Pardons and salt tax reductions buy calm |
| 58 | - on_start = uzh.54: "Opryshky Stir the Mountains" |
| 59 | Player chooses: raise gendarmerie (harsh) or parley (conciliatory) |
| 60 | - on_monthly = uzh.55 (2% chance): "Ambush in the Salt Pass" |
| 62 | - on_end = uzh.56: "A Quiet Carpathian Dawn" |
| 63 | Resolution: institutionalize mountain guard or celebrate folk heroes |
| 67 | - War Exhaustion <3: Peace allows focus on internal order |
| 68 | - No Rebel Provinces: State authority re-established |
| 71 | - The disaster cannot recur once uz_opryshky_pacified modifier is gained |
| 72 | - Province 1952 (Maramureș/Mukachevo) must be owned (historical epicenter) |
| 73 | - Balanced to allow player agency: harsh crackdown vs. compromise both viable |
| 74 | - Ties into mission tree: uz_union_dilemma and border control missions |
| 75 | provide tools to prevent or mitigate the disaster |
| 79 | - UZH_opryshky_uprising_title, UZH_opryshky_uprising_desc (UI text) |
| 80 | - uzh.54.t/d/a/b, uzh.55.t/d/a/b, uzh.56.t/d/a/b (event chain) |
| 81 | - uz_mountain_gendarmerie, uz_amnesty_rollout, uz_opryshky_pacified (modifiers) |
| 82 | - uz_rebel_legends, uz_opryshky_raids (flavor modifiers from events) |
| 85 | - Іван Франко, "Добрий Добуш" (collected folk ballads, 1896) |
| 86 | - Ярослав Дашкевич, "Опришківство на Україні" (academic study, 1976) |
| 87 | - Roman Drozd, "Oleksa Dovbush: Between History and Legend" (2008) |
| 88 | - Habsburg military reports on Carpathian banditry (Kriegsarchiv Wien) |
| 89 | ========================================================================= |

## Supplemental Excerpts (2026-03-02)

| Current line | Commentary |
|---:|---|
| 1 | OPRYSHKY UPRISING DISASTER |
| 2 |  |
| 3 | HISTORICAL BACKGROUND: |
| 4 |  |
| 5 | Key Historical Figures: |
| 6 |  |
| 7 | Historical Context: |
| 8 | added ideological fuel to economic grievances |
| 9 |  |
| 10 | GAME MECHANICS: |
| 11 | banditry, and eventual state response. |
| 12 |  |
| 13 | TRIGGERING CONDITIONS (can_start): |
| 14 |  |
| 15 | DISASTER EFFECTS (modifier): |
| 16 |  |
| 17 | PROGRESSION SYSTEM (progress): |
| 18 | Base progression speed increases with: |
| 19 |  |
| 20 | Mitigation modifiers: |
| 21 |  |
| 22 | EVENT CHAIN: |
| 23 | Random raid event showing ongoing banditry |
| 24 |  |
| 25 | ENDING CONDITIONS (can_end): |
| 26 | - Stability 1+: Governance restored |
| 27 |  |
| 28 | DESIGN NOTES: |
| 29 |  |
| 30 | LOCALIZATION KEYS: |
| 31 | - UZH_opryshky_uprising (disaster name) |
| 32 |  |
| 33 | HISTORICAL SOURCES: |
