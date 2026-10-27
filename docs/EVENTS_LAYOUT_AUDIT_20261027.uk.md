# Аудит і структура подій RIP — 2026-10-27

Згенеровано `python -B tools/audit_event_links.py`. Повна карта зв’язків: `outputs/events_links.json` (виклики, місця використання, символи common, прапорці/змінні/цілі та англійська локалізація).

## Результат

- 96 початкових файлів → 116 файлів; 881 унікальних ID, порядок значущих токенів кожної події збережено.
- Країнний контент: `RIP_<TAG>_<тема>.txt`; міждержавний, регіональний і релігійний: `RIP_shared_<родина>_<тема>.txt`. Назва означає належність контенту, а не додаткове обмеження доступності тегом.
- Табуляція, пробіли навколо `=`, розгорнуті блоки, UTF-8 без BOM. Коментарі та рядки збережено; баланс, ID й порядок опцій не змінено.
- Нерозв’язаних прямих викликів із подій: 0; з усіх перевірених каталогів: 0; невідповідностей country_event/province_event: 0.

Параметризованих місць виклику: 2 (`$INVITATION$`, `$ANNOUNCEMENT$` у rip_crusade_effects). Вони винесені окремо від нерозв’язаних буквальних ID; значення передаються викликачем.

## Порівняння з ваніллю

Джерело: `D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV`, версія 1.37.5.0; 6366 подій. Використано локальні файли гри, а не припущення про формат.

Збережено пласку структуру events, namespace, country_event/province_event, trigger, MTTH або is_triggered_only, immediate й option. Ваніль поєднує країнові та тематичні файли й допускає однорядкові блоки; стиль RIP навмисно суворіше уніфіковано. Це відповідність структури, а не твердження про тотожність усіх механік або коректність кожного scope.

Повна файлова заміна ванілі: `WomenInHistory.txt`. Її назву не змінено, щоб ванільні події не завантажилися вдруге.

Генератори church_support, hetman_authority, regional_governments і eparchy_timeline використовують `tools/event_layout.py`. Старі імена в їхніх шаблонах є вхідними ключами класифікації, а не вихідними файлами. Маніфест `tools/data/event_layout_manifest.json` зберігає початкові хеші.

## Події без іншого буквального використання

40 triggered-only подій потребують окремого рішення про підключення або архівування. `rip_gc_test.1` і `.10` належать ручній консольній лабораторії; відсутність автоматичного виклику для них очікувана. Для інших записів автоматичний шлях не підтверджено. Сам trigger не запускає is_triggered_only подію. Під час реорганізації їхню логіку не змінено.

| ID | Файл |
|---|---|
| `chr_flavor.1` | `events/RIP_CHR_Chernihiv.txt` |
| `chr_flavor.2` | `events/RIP_CHR_Chernihiv.txt` |
| `chr_flavor.3` | `events/RIP_CHR_Chernihiv.txt` |
| `het_cossack_raids.7` | `events/RIP_HET_HetmanateCossackRaids.txt` |
| `kyiv_independence.1` | `events/RIP_KIE_kyiv_independence.txt` |
| `kyiv_independence.2` | `events/RIP_KIE_kyiv_independence.txt` |
| `ruthenian_factions.1` | `events/RIP_KRU_RuthenianFactional.txt` |
| `ruthenian_factions.2` | `events/RIP_KRU_RuthenianFactional.txt` |
| `ukr_flavor.2` | `events/RIP_NOV_ukr_flavor.txt` |
| `podillia_events.11` | `events/RIP_PDL_Podillia_Events.txt` |
| `polesian_belarus.20` | `events/RIP_shared_belarus_PolesianBelarus.txt` |
| `bs_flavor.1` | `events/RIP_shared_black_sea_bs_flavor.txt` |
| `rip_faith.3` | `events/RIP_shared_church_FaithCanons.txt` |
| `zaz.17` | `events/RIP_shared_cossack_CossackRevolts.txt` |
| `ukr_flavor.3` | `events/RIP_shared_frontier_ukr_flavor.txt` |
| `rip_gc_test.10` | `events/RIP_shared_greek_catholic_GreekCatholicTest.txt` |
| `rip_gc_test.1` | `events/RIP_shared_greek_catholic_GreekCatholicTest.txt` |
| `rip_ro_authority.1` | `events/RIP_shared_orthodox_OrthodoxAuthority.txt` |
| `orthodox_crusade.3` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.6` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.7` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.8` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.13` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.16` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.17` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `orthodox_crusade.18` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `princes_revolt.3` | `events/RIP_shared_ruthenian_princes_revolt.txt` |
| `ruth_instituties.1` | `events/RIP_shared_ruthenian_ruth_instituties.txt` |
| `ruth_instituties.2` | `events/RIP_shared_ruthenian_ruth_instituties.txt` |
| `harass_tatar.1` | `events/RIP_shared_steppe_harass_tatar.txt` |
| `svydrigaylo.001` | `events/RIP_shared_west_ruthenian_svydrigaylo_independence.txt` |
| `uzh.1` | `events/RIP_UZH_Uzh.txt` |
| `uzh.9` | `events/RIP_UZH_Uzh.txt` |
| `uzh.10` | `events/RIP_UZH_Uzh.txt` |
| `rip_vol_alt_history.5` | `events/RIP_VOL_Volhynia_Alt_History.txt` |
| `rip_vol_alt_history.6` | `events/RIP_VOL_Volhynia_Alt_History.txt` |
| `rip_vol_alt_history.7` | `events/RIP_VOL_Volhynia_Alt_History.txt` |
| `rip_vol_alt_history.8` | `events/RIP_VOL_Volhynia_Alt_History.txt` |
| `zaz_flavor_m_1.1` | `events/RIP_ZAZ_ZAZmission.txt` |
| `zaz_flavor_m_5.2` | `events/RIP_ZAZ_ZAZmission.txt` |

## Карта перенесення

| Старий файл | Поточні файли |
|---|---|
| `events/AppanagePrincipalities.txt` | `events/RIP_shared_frontier_AppanagePrincipalities.txt` |
| `events/BorderPrincipalities.txt` | `events/RIP_shared_frontier_BorderPrincipalities.txt` |
| `events/Chernihiv.txt` | `events/RIP_CHR_Chernihiv.txt` |
| `events/ChernihivHistorical.txt` | `events/RIP_CHR_ChernihivHistorical.txt` |
| `events/ChernihivPaths.txt` | `events/RIP_CHR_ChernihivPaths.txt` |
| `events/CHR_Enterprise_Events.txt` | `events/RIP_CHR_CHR_Enterprise_Events.txt` |
| `events/CHR_Pantheon_Events.txt` | `events/RIP_CHR_CHR_Pantheon_Events.txt` |
| `events/CommonwealthReformation.txt` | `events/RIP_shared_commonwealth_CommonwealthReformation.txt` |
| `events/CossackRevolts.txt` | `events/RIP_shared_cossack_CossackRevolts.txt` |
| `events/DniesterEstuary.txt` | `events/RIP_shared_frontier_DniesterEstuary.txt` |
| `events/FreeElection.txt` | `events/RIP_shared_commonwealth_FreeElection.txt` |
| `events/Hadiach.txt` | `events/RIP_HET_Hadiach.txt` |
| `events/Haidamaky.txt` | `events/RIP_shared_cossack_Haidamaky.txt` |
| `events/HetmanateCossackRaids.txt` | `events/RIP_HET_HetmanateCossackRaids.txt` |
| `events/HetmanateEnhanced.txt` | `events/RIP_HET_HetmanateEnhanced.txt` |
| `events/HetmanateFlavor.txt` | `events/RIP_HET_HetmanateFlavor.txt` |
| `events/HetmanateLegacyEras.txt` | `events/RIP_HET_HetmanateLegacyEras.txt` |
| `events/HetmanateMissionRefresh.txt` | `events/RIP_HET_HetmanateMissionRefresh.txt` |
| `events/HetmanateMoldovanExpansion.txt` | `events/RIP_HET_HetmanateMoldovanExpansion.txt` |
| `events/HetmanateOrthodoxCrusade.txt` | `events/RIP_HET_HetmanateOrthodoxCrusade.txt` |
| `events/HetmanateRegimentalGovernance.txt` | `events/RIP_HET_HetmanateRegimentalGovernance.txt` |
| `events/HetmanateSuccession.txt` | `events/RIP_HET_HetmanateSuccession.txt` |
| `events/JewishEstate.txt` | `events/RIP_shared_estates_JewishEstate.txt` |
| `events/KhmelnytskyUprisings.txt` | `events/RIP_shared_cossack_KhmelnytskyUprisings.txt` |
| `events/KIEmission.txt` | `events/RIP_KIE_KIEmission.txt` |
| `events/KyivDnieperHistorical.txt` | `events/RIP_shared_ruthenian_KyivDnieperHistorical.txt` |
| `events/KyivShogunate.txt` | `events/RIP_KIE_KyivShogunate.txt` |
| `events/KyivSuccessionHistory.txt` | `events/RIP_KIE_KyivSuccessionHistory.txt` |
| `events/KyivTradeHouses.txt` | `events/RIP_KIE_KyivTradeHouses.txt` |
| `events/LithuanianConfession.txt` | `events/RIP_LIT_LithuanianConfession.txt` |
| `events/MoldavianFrontierExpansion.txt` | `events/RIP_shared_frontier_MoldavianFrontierExpansion.txt` |
| `events/NovgorodFlavorEvents.txt` | `events/RIP_NOV_nov_flavor.txt`<br>`events/RIP_shared_frontier_mansur_flavor.txt`<br>`events/RIP_shared_frontier_jagoldai_flavor.txt` |
| `events/OdesaRepublic.txt` | `events/RIP_ODS_OdesaRepublic.txt` |
| `events/OrthodoxCrusade.txt` | `events/RIP_shared_orthodox_OrthodoxCrusade.txt` |
| `events/PalanokFortress.txt` | `events/RIP_UZH_PalanokFortress.txt` |
| `events/PereiaslavFlavor.txt` | `events/RIP_PRL_PereiaslavFlavor.txt` |
| `events/Podillia_Disasters.txt` | `events/RIP_PDL_Podillia_Disasters.txt` |
| `events/Podillia_Events.txt` | `events/RIP_PDL_Podillia_Events.txt` |
| `events/PodilliaBorderPolicy.txt` | `events/RIP_PDL_PodilliaBorderPolicy.txt` |
| `events/PodilliaDisasters.txt` | `events/RIP_PDL_PodilliaDisasters.txt` |
| `events/PolesianBelarus.txt` | `events/RIP_shared_belarus_PolesianBelarus.txt` |
| `events/QasimKhanate.txt` | `events/RIP_QAS_QasimKhanate.txt` |
| `events/RaidMechanics.txt` | `events/RIP_shared_steppe_RaidMechanics.txt` |
| `events/RIP.txt` | `events/RIP_shared_ruthenian_ukr_flavor.txt`<br>`events/RIP_NOV_ukr_flavor.txt`<br>`events/RIP_MOS_RUS_flavor_rus.txt`<br>`events/RIP_ZAZ_zaz_flavor.txt`<br>`events/RIP_shared_monarchy_euro_monarchy.txt`<br>`events/RIP_shared_steppe_harass_tatar.txt`<br>`events/RIP_shared_ruthenian_princes_revolt.txt`<br>`events/RIP_KIE_kyiv_independence.txt`<br>`events/RIP_shared_ruthenian_ruth_instituties.txt`<br>`events/RIP_shared_black_sea_bs_flavor.txt`<br>`events/RIP_shared_sloboda_sloboda_history.txt`<br>`events/RIP_shared_frontier_ukr_flavor.txt` |
| `events/RIP_ChurchCompact.txt` | `events/RIP_shared_greek_catholic_ChurchCompact.txt` |
| `events/RIP_ChurchCouncils.txt` | `events/RIP_shared_greek_catholic_ChurchCouncils.txt` |
| `events/RIP_ChurchNodes_generated.txt` | `events/RIP_shared_church_ChurchNodes_generated.txt` |
| `events/RIP_ChurchRedesign.txt` | `events/RIP_shared_church_ChurchRedesign.txt` |
| `events/RIP_DiocesanUnion.txt` | `events/RIP_shared_greek_catholic_DiocesanUnion.txt` |
| `events/RIP_EparchyHistory.txt` | `events/RIP_shared_greek_catholic_EparchyHistory.txt` |
| `events/RIP_FaithCanons.txt` | `events/RIP_shared_church_FaithCanons.txt` |
| `events/RIP_FaithDisasters.txt` | `events/RIP_shared_church_FaithDisasters.txt` |
| `events/RIP_FaithReformEvents.txt` | `events/RIP_HLC_rip_stauropegion.txt`<br>`events/RIP_CHR_rip_vetka.txt`<br>`events/RIP_PDL_rip_kamianets.txt`<br>`events/RIP_PLT_rip_sophia.txt` |
| `events/RIP_Galicia_AltHistory.txt` | `events/RIP_HLC_Galicia_AltHistory.txt` |
| `events/RIP_GreekCatholicTest.txt` | `events/RIP_shared_greek_catholic_GreekCatholicTest.txt` |
| `events/RIP_HabsburgGreekCatholic.txt` | `events/RIP_shared_greek_catholic_HabsburgGreekCatholic.txt` |
| `events/RIP_HetmanAuthority.txt` | `events/RIP_HET_HetmanAuthority.txt` |
| `events/RIP_HetmanElection.txt` | `events/RIP_HET_HetmanElection.txt` |
| `events/RIP_OldBelieverInstitutions.txt` | `events/RIP_shared_orthodox_OldBelieverInstitutions.txt` |
| `events/RIP_OldBelievers.txt` | `events/RIP_shared_orthodox_OldBelievers.txt` |
| `events/RIP_OrthodoxAuthority.txt` | `events/RIP_shared_orthodox_OrthodoxAuthority.txt` |
| `events/RIP_ParishVisit.txt` | `events/RIP_shared_church_ParishVisit.txt` |
| `events/RIP_RegionalGovernments.txt` | `events/RIP_CHR_RegionalGovernments.txt`<br>`events/RIP_UZH_RegionalGovernments.txt`<br>`events/RIP_PDL_RegionalGovernments.txt`<br>`events/RIP_PRL_RegionalGovernments.txt`<br>`events/RIP_ODS_RegionalGovernments.txt` |
| `events/RIP_RO_InstitutionalHistory.txt` | `events/RIP_shared_orthodox_RO_InstitutionalHistory.txt` |
| `events/RIP_RussiaBalance.txt` | `events/RIP_MOS_RUS_RussiaBalance.txt` |
| `events/RIP_RuthenianDiaspora.txt` | `events/RIP_shared_ruthenian_RuthenianDiaspora.txt` |
| `events/RIP_UzhLocalUnion.txt` | `events/RIP_UZH_UzhLocalUnion.txt` |
| `events/Ruina.txt` | `events/RIP_HET_Ruina.txt` |
| `events/RussianOrthodox.txt` | `events/RIP_shared_orthodox_RussianOrthodox.txt` |
| `events/RuthenianDecadence.txt` | `events/RIP_KRU_RuthenianDecadence.txt` |
| `events/RuthenianEastwardExpansion.txt` | `events/RIP_shared_ruthenian_RuthenianEastwardExpansion.txt` |
| `events/RuthenianFactional.txt` | `events/RIP_KRU_RuthenianFactional.txt` |
| `events/SouthUkraineHistorical.txt` | `events/RIP_shared_steppe_SouthUkraineHistorical.txt` |
| `events/SteppeRaiding.txt` | `events/RIP_shared_steppe_SteppeRaiding.txt` |
| `events/svydrigaylo_independence.txt` | `events/RIP_shared_west_ruthenian_svydrigaylo_independence.txt` |
| `events/TheDeluge.txt` | `events/RIP_shared_commonwealth_TheDeluge.txt` |
| `events/TimeOfTroubles.txt` | `events/RIP_MOS_RUS_TimeOfTroubles.txt` |
| `events/UniateChurch.txt` | `events/RIP_shared_greek_catholic_UniateChurch.txt` |
| `events/UniateCrownUnion.txt` | `events/RIP_shared_greek_catholic_UniateCrownUnion.txt` |
| `events/UnionDispute.txt` | `events/RIP_shared_commonwealth_UnionDispute.txt` |
| `events/Uzh.txt` | `events/RIP_UZH_Uzh.txt` |
| `events/VilniusPalace.txt` | `events/RIP_LIT_VilniusPalace.txt` |
| `events/VOL_path_events.txt` | `events/RIP_VOL_VOL_path_events.txt` |
| `events/Volhynia_Alt_History.txt` | `events/RIP_VOL_Volhynia_Alt_History.txt` |
| `events/VolhynianConcessions.txt` | `events/RIP_VLN_VolhynianConcessions.txt` |
| `events/VOLmission.txt` | `events/RIP_VOL_VOLmission.txt` |
| `events/WestUkraineHistory.txt` | `events/RIP_shared_west_ruthenian_WestUkraineHistory.txt` |
| `events/WestUkraineMissionRefresh.txt` | `events/RIP_VOL_WestUkraineMissionRefresh.txt` |
| `events/WomenInHistory.txt` | `events/WomenInHistory.txt` |
| `events/ZaporizhiaFixes.txt` | `events/RIP_ZAZ_ZaporizhiaFixes.txt` |
| `events/ZaporizhiaFlavor.txt` | `events/RIP_ZAZ_ZaporizhiaFlavor.txt` |
| `events/ZaporizhianCrossroadsHistory.txt` | `events/RIP_ZAZ_ZaporizhianCrossroadsHistory.txt` |
| `events/ZaporizhiaPaths.txt` | `events/RIP_ZAZ_ZaporizhiaPaths.txt` |
| `events/ZaporozhianCrisis.txt` | `events/RIP_ZAZ_ZaporozhianCrisis.txt` |
| `events/ZaporozhianSich.txt` | `events/RIP_ZAZ_ZaporozhianSich.txt` |
| `events/ZAZmission.txt` | `events/RIP_ZAZ_ZAZmission.txt` |

## Межі перевірки

Це статичний граф точних символів. Наявність посилання не доводить досяжність гілки; дані не симулюють ROOT/FROM/PREV, чергу подій чи AI. Динамічні посилання та завантаження інших модів потребують окремої перевірки. EU4, кампанію та старі збереження в межах цього аудиту не запускали.

Перевірено encoding, braces, hidden-event shape, синхронність генераторів і script layer (0 помилок, 317 попереджень). Із пакета 92 тестів після ремонту eparchy_history проходять 90. Залишаються попередні помилки check_diocesan_union (очікує стару форму AI-умови в рішенні) та check_precommit_recovery (автопошук Python без RIP_PYTHON). Вони не спричинені перенесенням подій. Статичні перевірки не доводять runtime.
