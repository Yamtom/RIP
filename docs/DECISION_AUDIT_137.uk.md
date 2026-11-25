# Рішення кампанії з RIP у EU4 1.37.5

У каталозі 258 рішень із 48 файлів мода та 502 з 192 незаміщених файлів базової гри. Однакові імена файлів розв’язано на користь RIP. Серед прочитаних архівних каталогів DLC додаткових файлів рішень не виявлено. У двох неповних місцевих архівах (`dlc126.zip`, `dlc131.zip`) вдалося прочитати лише доступні локальні заголовки.

## Що побачить гравець

| Рішення | Що визначає видимість і доступність |
| --- | --- |
| Проголосити козацьке військо | Рішення доступне козацькій державі відповідної руської культури. Потрібні 6 піхотних і 3 кінні полки. До військової технології 7 — щонайменше 10 полків загалом, від технології 7 — щонайменше один артилерійський полк. |
| Проголосити Гетьманат | Рішення видно Переяславу й республіканському Запорожжю ще до прийняття Ренесансу. На карті підсвічуються відсутні національні провінції та землі, які зараховуються до спільного порогу. |
| Переяславська угода та виступ Мазепи | Підказка показує пороги чинного для кампанії періоду. У ранньому сценарії потрібен більший запас очок. Фактична ціна угоди становить 100 дипломатичних очок, виступу — 150 військових. |
| Православні походи | Ініціатор має виставити 30 полків і зберегти половину резерву рекрутів. Підказки окремо пояснюють власника міста, інтервал між походами та роль Гетьманату. |
| Регіональні уряди та переселенці | У рішеннях урядів гравець бачить зміст розпорядження. У рішеннях переселенців залишаються видимими ціна й період очікування, а вибір технічного прапорця місця призначення приховано. |
| Інтеграція Війська до російської системи | Рішення з’являється у підданого Росії. Сам союз із Росією раніше показував дію, яку союзник не міг виконати. |

## Покажчик перевірки

Для кожного рішення перша колонка умов стисло характеризує `potential`, друга — `allow`. Позначено категорії безпосередніх перевірок. Спеціальні умови можуть розгортатися у спільні скрипти. Довжина файла або кількість умов сама по собі не визначає, скільки рядків покаже рушій. Це покажчик для пошуку й повторної перевірки, а не протокол проходження кампаній.

### RIP

<details><summary>chernihivpaths.txt · 17</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Take the Road of the Towns (`chr_road_of_the_towns`) | прогрес кампанії | спеціальна умова |
| Bind the Towns into a Union (`chr_union_of_the_towns`) | державність, прогрес кампанії | спеціальна умова |
| Seat the Rada of the Lands (`chr_rada_of_all_the_lands`) | державність, прогрес кампанії | спеціальна умова |
| Take the Road of the Houses (`chr_road_of_the_houses`) | прогрес кампанії | спеціальна умова |
| Call a Prince to Siversk (`chr_call_a_prince`) | державність, прогрес кампанії | спеціальна умова |
| Raise the Tsardom of the Prykazy (`chr_crown_the_prykaz_tsardom`) | державність, прогрес кампанії | спеціальна умова |
| Take the Road of the Chancery (`chr_road_of_the_chancery`) | прогрес кампанії | спеціальна умова |
| Raise the Corps of the Dzhury (`chr_raise_the_dzhury`) | державність, прогрес кампанії | спеціальна умова |
| Proclaim the Union of Many Nations (`chr_union_of_many_nations`) | державність, прогрес кампанії | спеціальна умова |
| Proclaim Great Chernihiv (`chr_proclaim_great_chernihiv`) | державність, прогрес кампанії | спеціальна умова |
| Forge Border Compacts (`chr_border_compacts`) | державність | прогрес кампанії, ресурси, дипломатія й війна |
| Organise a Sloboda (`chr_organize_sloboda`) | державність | землі, ресурси |
| Establish an Enterprise (`chr_establish_enterprise`) | державність | час і технології, землі, ресурси |
| Commission Monastic Bastions (`chr_commission_monastic_bastions`) | державність, прогрес кампанії, землі | землі, ресурси |
| Expand Sloboda Farmsteads (`chr_expand_sloboda_farmlands`) | державність, прогрес кампанії, землі | землі, ресурси |
| Integrate Grain Fair Guilds (`chr_integrate_grain_exchange_guilds`) | державність, прогрес кампанії, землі | ресурси |
| Grant a Sloboda to the Old Believers (`chr_grant_sloboda_to_old_believers`) | державність | прогрес кампанії, землі, ресурси |

</details>

<details><summary>cossackhostdecisions.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Proclaim Cossack Host (`form_cossack_host`) | державність, походження, прогрес кампанії | час і технології, землі, ресурси, військо |
| Establish Host Military Organization (`establish_host_organization`) | прогрес кампанії | ресурси, військо |
| Formalize Liberties of the Host (`formalize_host_democracy`) | державність, прогрес кампанії | ресурси |
| Integrate into Russian Host System (`integrate_russian_host_system`) | державність, прогрес кампанії, час і технології | державність, дипломатія й війна |
| Raise the Don Host (`found_the_don_host`) | прогрес кампанії, землі | ресурси |
| Raise the Danube Host (`found_the_danube_sich`) | прогрес кампанії, землі | ресурси |
| Raise the Eastern Host (`found_the_eastern_host`) | прогрес кампанії, землі | ресурси, військо |
| Raise the Sloboda Host (`found_the_sloboda_host`) | прогрес кампанії, землі | ресурси |

</details>

<details><summary>dniesterestuarydecisions.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Develop Dniester Estuary Trade (`develop_dniester_estuary_trade`) | державність, прогрес кампанії, землі | час і технології, ресурси, дипломатія й війна |
| Fortify Dniester Estuary (`fortify_dniester_estuary`) | прогрес кампанії | час і технології, ресурси, дипломатія й війна |
| Establish Estuary Fishing Industry (`establish_dniester_fishing`) | прогрес кампанії | час і технології, ресурси |
| Develop Wine Trade (`establish_dniester_wine_trade`) | прогрес кампанії | час і технології, ресурси |
| Establish Salt Production (`establish_dniester_salt_works`) | прогрес кампанії | час і технології, ресурси |
| Contest Ottoman Control of Dniester (`contest_ottoman_dniester_control`) | державність, прогрес кампанії, землі | час і технології, військо, дипломатія й війна |

</details>

<details><summary>estates.txt · 12</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Curtail the Nobility (`curtail_estate_noble`) | прогрес кампанії | землі, ресурси |
| Curtail the Clergy (`curtail_estate_church`) | прогрес кампанії | землі, ресурси |
| Curtail the Brahmins (`curtail_estate_brahmins`) | прогрес кампанії | землі, ресурси |
| Curtail the Burghers (`curtail_estate_burghers`) | прогрес кампанії | землі, ресурси |
| Curtail the Vaishyas (`curtail_estate_vaisyas`) | прогрес кампанії | землі, ресурси |
| Curtail the Tribes (`curtail_estate_nomadic_tribes`) | прогрес кампанії | землі, ресурси |
| Curtail the Jains (`curtail_estate_jains`) | прогрес кампанії | землі, ресурси |
| Call of the Steppes (`cossack_nation`) | державність | державність, ресурси |
| Establish the Dhimmi Estate (`gain_access_to_estate_dhimmi`) | державність, походження, прогрес кампанії | походження, прогрес кампанії, землі, ресурси |
| Curtail the Eunuchs (`curtail_eunuch_estate_decision`) | прогрес кампанії | землі, ресурси |
| Curtail the [Root.GetQizilbashOrFallbackName] (`curtail_estate_qizilbash`) | прогрес кампанії | землі, ресурси |
| Breed a New War Steed (`horse_breeding_decision`) | прогрес кампанії | землі, військо |

</details>

<details><summary>greekcatholicdecisions.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Accept a local church union (`convert_to_greek_catholic_decision`) | походження, час і технології | державність, походження, прогрес кампанії, землі, ресурси, дипломатія й війна |
| Establish Greek Catholic Educational Network (`greek_catholic_education_decision`) | походження, прогрес кампанії, землі | спеціальна умова |
| Patronize Greek Catholic Culture (`patronize_greek_catholic_culture_decision`) | походження, прогрес кампанії | ресурси |
| Seek Orthodox Reconciliation (`seek_orthodox_reconciliation_decision`) | походження, прогрес кампанії | походження, ресурси, дипломатія й війна |
| Strengthen Papal Ties (`strengthen_papal_ties_decision`) | державність, походження, прогрес кампанії | ресурси |
| Preserve Eastern Rite Traditions (`preserve_eastern_rite_decision`) | походження, прогрес кампанії | ресурси |

</details>

<details><summary>hetmanatecossackraids.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Organize Major Raid (`het_organize_major_raid`) | державність, прогрес кампанії | ресурси, військо, дипломатія й війна |
| Deep Penetration Raid (`het_deep_penetration_raid`) | державність, прогрес кампанії | ресурси, військо, дипломатія й війна |
| Launch Punitive Expedition (`het_punitive_expedition`) | державність | прогрес кампанії, військо, дипломатія й війна |
| Steppe Domination (`het_steppe_domination`) | державність | прогрес кампанії, землі, військо, дипломатія й війна |
| Drill the Regular Regiments (`het_modernize_host`) | державність, час і технології | прогрес кампанії, час і технології, ресурси |

</details>

<details><summary>hetmanatedecisions.txt · 16</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Strengthen Hetman Authority (`het_strengthen_hetman`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Empower the Starshyna Council (`het_empower_starshyna`) | державність, прогрес кампанії | ресурси |
| Establish Regimental System (`het_establish_regiments`) | державність, прогрес кампанії, землі | землі, ресурси |
| Establish the Kyiv Brotherhood Collegium (`het_found_brotherhood_collegium`) | державність, прогрес кампанії, час і технології, землі | ресурси |
| Charter the Kyiv-Mohyla Academy (`het_expand_academy`) | державність, прогрес кампанії, час і технології, землі | прогрес кампанії, час і технології, ресурси |
| Sign Treaty with Russia (`het_pereiaslav_treaty`) | державність, прогрес кампанії, час і технології, дипломатія й війна | державність, час і технології, ресурси, дипломатія й війна |
| Break with Overlord (`het_mazepa_independence`) | державність, прогрес кампанії, час і технології, дипломатія й війна | час і технології, ресурси, військо, дипломатія й війна |
| Establish Left Bank Administration (`het_left_bank_admin`) | державність, прогрес кампанії, землі | ресурси |
| Establish Sloboda Ukraine Settlements (`het_sloboda_settlements`) | державність, прогрес кампанії, час і технології, землі | землі, ресурси |
| Defend the Orthodox Faith (`het_defend_orthodox`) | державність, походження, прогрес кампанії | ресурси |
| Establish Black Sea Trade (`het_black_sea_trade`) | державність, прогрес кампанії, землі | землі, ресурси |
| Reform Hetman Election Process (`het_reform_elections`) | державність, прогрес кампанії | ресурси |
| Review Regimental Territorial Governance (`het_regimental_territorial_governance_decision`) | державність, землі | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Establish Printing Press (`het_establish_printing_press`) | прогрес кампанії | ресурси |
| Resist Abolition of Autonomy (`het_resist_abolition`) | спеціальна умова | спеціальна умова |
| Compile the Legacy Chronicles (`het_compile_legacy_chronicles`) | державність | прогрес кампанії, час і технології, ресурси, дипломатія й війна |

</details>

<details><summary>hetmanatemoldovanexpansion.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Offer Moldavian Protection (`het_moldovan_protection`) | державність, прогрес кампанії | землі, ресурси, військо, дипломатія й війна |
| Integrate Moldavia (`het_integrate_moldova`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Call Moldavian Levies (`het_moldovan_military_access`) | державність, прогрес кампанії | державність, ресурси, дипломатія й війна |
| Danube Trade Charter (`het_danube_trade_charter`) | державність, прогрес кампанії, землі | час і технології, землі, ресурси |
| Support Orthodox Missionaries (`het_orthodox_missionary_support`) | державність, прогрес кампанії | ресурси |

</details>

<details><summary>hetmanatenation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Proclaim the Hetmanate (`hetmanate_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>hlcmetropolitanatepaths.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Confirm the Metropolitan See (`hlc_confirm_the_metropolitan_see`) | державність, прогрес кампанії | державність, походження, ресурси |
| Complete the Union of Lviv (`hlc_complete_the_union_of_lviv`) | державність, походження, прогрес кампанії | державність, ресурси |

</details>

<details><summary>hlcrepublicpaths.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Boyars Take Power (`hlc_the_boyars_take_power`) | державність, ресурси | державність, ресурси |
| Seat the Metropolitan of Halych (`hlc_elevate_the_metropolitan`) | державність, ресурси | державність, ресурси |

</details>

<details><summary>kuyabanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Slavic Homeland Under Allah's Protection (`kuyaba_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>kyivtriggers.txt · 12</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Centralize Kyivan Rus (`rus_nation`) | державність, прогрес кампанії, час і технології | час і технології, землі, ресурси |
| The Days of Kyivan Rus Are Over. (`like_rus_nation`) | державність, прогрес кампанії, землі | час і технології, землі, ресурси |
| The Kyivan Seniorate (`kyiv_shogunate_path`) | державність, прогрес кампанії | час і технології, землі, ресурси |
| Proclaim the Kyivan Cesarstvo (`kyiv_cesarstvo_path`) | державність, прогрес кампанії | час і технології, землі, ресурси, дипломатія й війна |
| Convene the Three Estates of Rus' (`kyiv_factional_ruthenia`) | державність, прогрес кампанії, землі | час і технології, землі, ресурси |
| Proclaim the Kyivan Veche (`kyiv_veche_republic`) | державність, прогрес кампанії, землі | час і технології, землі, ресурси |
| Proclaim the Kyivan Metropolitanate (`kyiv_metropolitan_theocracy`) | державність, походження, прогрес кампанії, землі | час і технології, землі, ресурси |
| Establish Kyivan Princedoms (`kyiv_establish_princedoms`) | державність, прогрес кампанії | спеціальна умова |
| Summon the Kyivan Princes (`kyiv_summon_princes`) | державність, землі | ресурси, дипломатія й війна |
| Charter a Free Trade City (`kyiv_charter_free_city`) | державність, прогрес кампанії | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Convene the Boyar Council (`kyiv_convene_boyar_council`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |
| Convene the Church Sobor (`kyiv_convene_church_sobor`) | державність, прогрес кампанії | походження, землі, ресурси, дипломатія й війна |

</details>

<details><summary>moldavianfrontierexpansion.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Moldavian Frontier Mandate (`moldavian_frontier_mandate`) | державність | прогрес кампанії, час і технології, землі, дипломатія й війна |
| Form the Steppe Host Doctrine (`moldavian_steppe_host_doctrine`) | державність, прогрес кампанії | прогрес кампанії, час і технології, землі, дипломатія й війна |
| Corridors and Customs (`moldavian_corridor_and_customs`) | державність, прогрес кампанії | прогрес кампанії, час і технології, землі, дипломатія й війна |
| Statute of the Fortress Belt (`moldavian_fortress_belt_statute`) | державність, прогрес кампанії | прогрес кампанії, час і технології, землі, дипломатія й війна |
| Set the Frontier Legacy (`moldavian_frontier_legacy`) | державність, прогрес кампанії | прогрес кампанії, час і технології, дипломатія й війна |

</details>

<details><summary>novgorodzalesyedecisions.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Enact Birch Bark Literacy & Veche Law (`nov_birch_bark_tradition`) | державність, походження, прогрес кампанії, землі | час і технології, землі, ресурси, дипломатія й війна |
| Consolidate the Northern Slavic Union (`nov_north_slavic_consolidation`) | державність, походження, прогрес кампанії | землі, ресурси, дипломатія й війна |
| Address the Volga-Finnic Substrate of Zalesye (`mos_volga_finnic_heritage`) | державність, походження, прогрес кампанії, землі | час і технології, землі, ресурси, дипломатія й війна |
| Acknowledge the Legacy of Mansur's Principality (`mansur_principality_legacy`) | державність, прогрес кампанії, землі | землі, ресурси, дипломатія й війна |
| Affirm the Autonomy of Jagoldai's Host (`jagoldai_darkness_autonomy`) | державність, прогрес кампанії, землі | землі, ресурси, дипломатія й війна |

</details>

<details><summary>odesagovernmentdecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Establish the Free Port of Hajibey (`establish_hajibey_free_port`) | державність, землі | час і технології, ресурси, дипломатія й війна |

</details>

<details><summary>orthodoxcrusadedecisions.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Declare Crusade for Constantinople (`orthodox_crusade_constantinople`) | час і технології | спеціальна умова |
| Declare Crusade for Jerusalem (`orthodox_crusade_jerusalem`) | час і технології | спеціальна умова |
| End the Orthodox Crusade (`orthodox_crusade_end`) | прогрес кампанії | завжди |
| Join the Orthodox Crusade (`orthodox_crusade_join`) | прогрес кампанії | спеціальна умова |

</details>

<details><summary>pereiaslavgovernmentdecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Establish the Regimental Republic (`prl_establish_regimental_republic`) | державність, прогрес кампанії | землі, ресурси, військо, дипломатія й війна |

</details>

<details><summary>podillia_decisions.txt · 18</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Organize the Dniester Defense (`pdl_adopt_carpathian_doctrine`) | прогрес кампанії | землі, ресурси |
| Embrace Cossack Frontier Traditions (`pdl_adopt_cossack_traditions`) | прогрес кампанії | ресурси, військо |
| Embrace Magnate Governance (`pdl_adopt_magnate_governance`) | прогрес кампанії | ресурси |
| Grant Lands to Cossack Settlers (`pdl_grant_cossack_lands`) | державність, прогрес кампанії | землі, ресурси |
| Establish Magnate Council (`pdl_establish_magnate_council`) | державність, прогрес кампанії | ресурси |
| Proclaim Religious Tolerance (`pdl_proclaim_tolerance`) | державність, прогрес кампанії | походження, землі, ресурси |
| Protect Jewish Communities (`pdl_protect_jewish_communities`) | державність, прогрес кампанії | ресурси |
| Develop Kamianets as Capital (`pdl_develop_kamianets`) | державність, прогрес кампанії, землі | ресурси |
| Fortify Khotyn (`pdl_fortify_khotyn_decision`) | державність, прогрес кампанії, землі | ресурси |
| Establish Trade Route to Lviv (`pdl_establish_lviv_trade`) | державність, прогрес кампанії, землі | ресурси |
| Grant Magnate Titles (`pdl_grant_magnate_titles`) | державність, прогрес кампанії | прогрес кампанії, ресурси, дипломатія й війна |
| Integrate a Magnate Vassal (`pdl_integrate_magnate_vassal`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |
| Establish a Trade Company (`pdl_establish_trade_company`) | державність, прогрес кампанії, землі | час і технології, землі, ресурси |
| Expand Trade Network (`pdl_expand_trade_network`) | державність, прогрес кампанії | час і технології, землі, ресурси |
| Unite with Galicia (`pdl_unite_with_galicia_diplo`) | державність, прогрес кампанії | державність, ресурси, дипломатія й війна |
| Integrate Volhynia (`pdl_unite_with_volhynia`) | державність, прогрес кампанії | державність, ресурси, дипломатія й війна |
| Review Podillian Border Policy (`pdl_border_policy_decision`) | прогрес кампанії | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Charter of the Four Communities (`pdl_charter_of_four_communities`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |

</details>

<details><summary>polesianbelarusiannations.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Polesia (`polesian_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Restore Polotsk (`polotsk_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Form Belarus (`belarus_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>rip_capitalloss.txt · 12</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Take the Name of [HLC.GetName] (`rip_seat_become_hlc`) | державність, землі | завжди |
| Take the Name of [VLN.GetName] (`rip_seat_become_vln`) | державність, землі | завжди |
| Take the Name of [KIE.GetName] (`rip_seat_become_kie`) | державність, землі | завжди |
| Take the Name of [CHR.GetName] (`rip_seat_become_chr`) | державність, землі | завжди |
| Take the Name of [ZAZ.GetName] (`rip_seat_become_zaz`) | державність, землі | завжди |
| Take the Name of [PRL.GetName] (`rip_seat_become_prl`) | державність, землі | завжди |
| Take the Name of [PDL.GetName] (`rip_seat_become_pdl`) | державність, землі | завжди |
| Take the Name of [UZH.GetName] (`rip_seat_become_uzh`) | державність, землі | завжди |
| Take the Name of [VTB.GetName] (`rip_seat_become_vtb`) | державність, землі | завжди |
| Take the Name of [MSK.GetName] (`rip_seat_become_msk`) | державність, землі | завжди |
| Take the Name of [MSL.GetName] (`rip_seat_become_msl`) | державність, землі | завжди |
| Take the Name of [PLT.GetName] (`rip_seat_become_plt`) | державність, землі | завжди |

</details>

<details><summary>rip_churchcouncils.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Convene the Sobor (`rip_ro_convene_the_sobor`) | спеціальна умова | спеціальна умова |
| Convene the Kyivan Church Council (`rip_kyiv_convene_the_council`) | державність, походження, землі | спеціальна умова |
| Fund a Parish Mission (`rip_fund_a_parish_mission`) | походження, землі | спеціальна умова |

</details>

<details><summary>rip_churchgovernance.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore a Broken Church Charter (`rip_church_restore_compact`) | землі | походження, землі, ресурси, дипломатія й війна |
| Reserve Episcopal Appointments to the Crown (`rip_church_crown_appointments`) | державність, прогрес кампанії | спеціальна умова |
| Restore Ecclesiastical Elections (`rip_church_restore_elections`) | прогрес кампанії | спеціальна умова |
| Require Crown Approval of Theology (`rip_church_censor_theology`) | державність, прогрес кампанії | прогрес кампанії, ресурси |
| End Theological Censorship (`rip_church_end_censorship`) | прогрес кампанії | завжди |
| Appoint a Lay Supervisor of the Synod (`rip_church_appoint_supervisor`) | державність, прогрес кампанії, час і технології | прогрес кампанії |
| Mobilize through the State Church (`rip_church_mobilize_confession`) | державність, дипломатія й війна | прогрес кампанії, ресурси |
| Negotiate an Eastern Church Charter (`rip_church_negotiate_compact`) | землі | спеціальна умова |

</details>

<details><summary>rip_churchredesign.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Renounce the patriarchal settlement (`rip_church_break_communion`) | походження, прогрес кампанії, час і технології | спеціальна умова |
| Change our policy toward the Union (`rip_church_oppose_union`) | походження, прогрес кампанії | прогрес кампанії, ресурси |
| Seek recognition of our patriarchate (`rip_church_request_recognition`) | походження, прогрес кампанії, час і технології | прогрес кампанії, ресурси, дипломатія й війна |
| Reconcile with the eastern patriarchates (`rip_church_reconcile`) | походження, прогрес кампанії | спеціальна умова |
| Invoke the Florentine Precedent (`rip_church_florence`) | походження, прогрес кампанії, час і технології, землі | спеціальна умова |
| Sponsor an Eastern Catholic union (`rip_church_sponsor_union`) | походження, прогрес кампанії, час і технології, землі | спеціальна умова |
| Withdraw royal support for the Union (`rip_church_withdraw_union_support`) | походження, прогрес кампанії | ресурси, дипломатія й війна |
| Conclude the ecumenical settlement (`rip_church_ecumenism`) | походження, прогрес кампанії | спеціальна умова |

</details>

<details><summary>rip_diocesanunion.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Negotiate an Eparchial Union (`rip_du_negotiate`) | походження, прогрес кампанії, час і технології | спеціальна умова |

</details>

<details><summary>rip_kie_byzantineprimacy.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Declare Kyiv's Primacy (`rip_kie_declare_primacy`) | державність, прогрес кампанії | дипломатія й війна |

</details>

<details><summary>rip_oldbelieverinstitutions.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Settle the Organization of the Old Rite (`rip_ob_choose_accord`) | спеціальна умова | прогрес кампанії |
| Convene the Community Assembly (`rip_ob_hold_assembly`) | спеціальна умова | прогрес кампанії |
| Endow a Refuge of the Old Rite (`rip_ob_endow_refuge`) | спеціальна умова | прогрес кампанії, землі |

</details>

<details><summary>rip_oldbelievers.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Guarantee the Old Rite (`rip_ob_tolerate`) | прогрес кампанії | спеціальна умова |
| Enforce the Revised Books (`rip_ob_repress`) | прогрес кампанії | спеціальна умова |
| Adopt the Old Believer Confession (`rip_ob_adopt_old_rite`) | походження, землі | походження, ресурси, дипломатія й війна |

</details>

<details><summary>rip_orthodoxicons.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Take the First Rome (`rip_ro_the_first_rome`) | прогрес кампанії | походження, землі, ресурси, дипломатія й війна |

</details>

<details><summary>rip_parishvisit.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Visit the Parishes (`rip_visit_the_parishes`) | походження, землі | спеціальна умова |

</details>

<details><summary>rip_regionalgovernments.txt · 14</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Ring the Veche Bell (`rip_rg_chr_bell_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Grant the Desna Staple Right (`rip_rg_chr_staple_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Muster the Guild Militia (`rip_rg_chr_militia_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Exercise the Salt Regalia (`rip_rg_uzh_salt_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Contract the Highland Guides (`rip_rg_uzh_guides_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Fortify the Carpathian Pass (`rip_rg_uzh_pass_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Send the Watch Patrols (`rip_rg_pdl_patrol_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Grant the Kamianets Town Statute (`rip_rg_pdl_charter_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Muster the Mobile Defense (`rip_rg_pdl_mobile_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Send the Watch Patrols (`rip_rg_prl_patrol_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Charter the Frontier Towns (`rip_rg_prl_charter_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Muster the Mobile Defense (`rip_rg_prl_mobile_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |
| Charter Mediterranean Freight (`rip_rg_ods_freight_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Outfit Black Sea Corsairs (`rip_rg_ods_corsairs_decision`) | спеціальна умова | прогрес кампанії, землі, ресурси |

</details>

<details><summary>rip_ro_communion.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Renounce Eastern Orthodox Communion (`rip_ro_renounce_communion`) | прогрес кампанії, час і технології | прогрес кампанії, ресурси, дипломатія й війна |

</details>

<details><summary>rip_rutheniandiaspora.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Offer Settlers to a Colony (`rip_diaspora_colonial_settlers`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |
| Offer Settlers and the Faith (`rip_diaspora_colonial_settlers_faith`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |
| Offer Settlers Across the Border (`rip_diaspora_mainland_settlers`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |
| Offer Settlers and the Faith Across the Border (`rip_diaspora_mainland_settlers_faith`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |

</details>

<details><summary>rip_statesymbolsdecisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Adopt the Trident (`adopt_the_trident`) | державність | державність, дипломатія й війна |
| Proclaim the Ruthenian Empire (`proclaim_ruthenian_empire`) | державність, прогрес кампанії | державність, прогрес кампанії |

</details>

<details><summary>russiannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Russian Nation (`russian_nation`) | державність, походження, прогрес кампанії, землі | державність, прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>russianorthodoxdecisions.txt · 9</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Elect an Independent Metropolitan (`convert_to_russian_orthodox_decision`) | походження, прогрес кампанії, час і технології | землі, ресурси, дипломатія й війна |
| Establish Moscow Patriarchate (`establish_moscow_patriarchate_decision`) | державність, прогрес кампанії, час і технології | ресурси, дипломатія й війна |
| Impose Administrative Assimilation (`russification_campaign_decision`) | походження, прогрес кампанії, час і технології, землі | ресурси |
| Authorize Confessional Courts (`establish_orthodox_inquisition_decision`) | прогрес кампанії, час і технології | ресурси |
| Gathering of Russian Lands (`gathering_russian_lands_decision`) | походження, прогрес кампанії | ресурси |
| Establish Symphonia of Powers (`establish_symphonia_decision`) | державність, прогрес кампанії | ресурси |
| Proclaim Orthodox Empire (`proclaim_orthodox_empire_decision`) | державність, прогрес кампанії | походження, землі, ресурси |
| Protect a Provincial Mission (`force_convert_province_decision`) | походження, прогрес кампанії, землі | походження, землі, ресурси |
| Endow a Settlement Office (`russify_province_decision`) | походження, прогрес кампанії, землі | походження, землі, ресурси |

</details>

<details><summary>ruthenianeastwardexpansion.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Commission an Eastern Frontier Expedition (`ruthenian_eastward_frontier_policy`) | державність | час і технології, землі, ресурси, дипломатія й війна |
| Commission a Ural Frontier Expedition (`ruthenian_open_ural_gate`) | державність, прогрес кампанії | час і технології, землі, ресурси, дипломатія й війна |
| Adopt Steppe Raid Doctrine (`ruthenian_steppe_raid_doctrine`) | державність, прогрес кампанії | прогрес кампанії, час і технології, землі, ресурси, дипломатія й війна |
| Frontier Mobility Network (`ruthenian_frontier_mobility_network`) | державність, прогрес кампанії | прогрес кампанії, час і технології, землі, ресурси, дипломатія й війна |
| Commission a Manchurian Frontier Expedition (`ruthenian_manchurian_horizon`) | державність, прогрес кампанії | час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>rutheniannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reclaim Ruthenian Legacy (`ruthenian_nation`) | державність, походження, прогрес кампанії, час і технології, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>southukrainedecisions.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Enable Moldavian Southern Process (`south_ukraine_enable_process_mol`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Charter the Khan's Frontier Settlements (`south_ukraine_enable_process_cri`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Codify the Steppe Frontier (`south_ukraine_codify_frontier`) | прогрес кампанії, час і технології, землі, ресурси, військо | час і технології, землі, ресурси, військо, дипломатія й війна |
| Establish a Black Sea Grain Exchange (`south_ukraine_grain_exchange`) | прогрес кампанії, час і технології, ресурси | час і технології, ресурси |

</details>

<details><summary>svydrigaylo_independence.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Send Confederation Invitations (`svydrigaylo_confederation_invitation`) | державність, прогрес кампанії | дипломатія й війна |
| Proclaim the Ruthenian Independence War (`svydrigaylo_ruthenian_independence_war`) | державність | військо, дипломатія й війна |

</details>

<details><summary>uniatecrownunion.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Treat with Rome (`rip_ucr_treat_with_rome`) | походження, прогрес кампанії | державність, походження, ресурси, дипломатія й війна |

</details>

<details><summary>uniondispute.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Hold the Union on Our Terms (`lit_hold_the_union_on_our_terms`) | прогрес кампанії | спеціальна умова |
| Take a Crown of Our Own (`lit_take_a_separate_crown`) | прогрес кампанії | спеціальна умова |
| Press for the Palatinates (`pol_press_the_incorporation`) | державність, прогрес кампанії | спеціальна умова |
| Guarantee the Orthodox Lords (`lit_guarantee_the_orthodox_lords`) | прогрес кампанії | походження, землі, ресурси, дипломатія й війна |
| Confirm the Statute (`lit_confirm_the_statute`) | державність, прогрес кампанії | ресурси, дипломатія й війна |

</details>

<details><summary>uzheparchypath.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Raise the Eparchial See (`uzh_road_of_the_eparchy`) | державність, походження, прогрес кампанії, час і технології | спеціальна умова |
| Translate the Episcopal Seat (`uzh_translate_the_episcopal_seat`) | державність, прогрес кампанії | державність |
| Establish the Presov Eparchy (`uzh_establish_the_presov_eparchy`) | державність, прогрес кампанії, час і технології | державність |
| Launch Rusyn Colonization (`uzh_launch_colonization_wave`) | державність | прогрес кампанії, ресурси, дипломатія й війна |
| Raise the Hajduk Host (`uzh_raise_serdyuk_host`) | державність | прогрес кампанії, ресурси |

</details>

<details><summary>vhknation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restoration of Halycia-Volhynia (`volyn_halich_nation`) | державність, землі | державність, час і технології, дипломатія й війна |

</details>

<details><summary>vlnrepublicpaths.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Sejmik Asserts Itself (`vln_the_sejmik_asserts_itself`) | державність, час і технології | державність, прогрес кампанії, ресурси, дипломатія й війна |
| Territorial Concessions to the Magnates (`vln_magnate_territorial_concession_decision`) | державність, землі | прогрес кампанії, землі, ресурси, дипломатія й війна |

</details>

<details><summary>westruthenianmaneuverdecisions.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Charter the Vernacular Chanceries (`wr_charter_distinctiveness_decision`) | спеціальна умова | ресурси |
| Send Envoys with the Chancery Charter (`wr_rally_branch_a_congress_decision`) | спеціальна умова | ресурси |
| Put the Ruthenian Statutes to the Diet (`wr_codify_west_ruthenian_group_decision`) | спеціальна умова | ресурси |
| Offer a Compact to the Western Towns (`wr_proclaim_west_slavic_affinity_decision`) | спеціальна умова | ресурси |
| Invite the Guilds to the Western Compact (`wr_rally_branch_b_congress_decision`) | спеціальна умова | ресурси |
| Ratify the Western Charter (`wr_attempt_west_slavic_transition_decision`) | спеціальна умова | ресурси |

</details>

<details><summary>zaporizhiadecisions.txt · 24</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Relocate the Sich (`zaz_relocate_sich`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |
| Launch a Great Raid (`zaz_great_raid`) | державність, прогрес кампанії, час і технології | ресурси, дипломатія й війна |
| Send the Chaiky (`zaz_chaiky_raid`) | державність, прогрес кампанії, час і технології | державність, ресурси, дипломатія й війна |
| Liberate the Slaves (`zaz_liberate_slaves`) | державність, прогрес кампанії, час і технології | державність, походження, ресурси |
| Settle the Wild Fields (`zaz_settle_wild_fields`) | державність, прогрес кампанії, землі | ресурси |
| Forge the Steppe Alliance (`zaz_steppe_alliance`) | державність, походження, прогрес кампанії | походження, ресурси, дипломатія й війна |
| Monopolize Black Sea Trade (`zaz_black_sea_trade`) | державність, прогрес кампанії, землі | землі, ресурси |
| Host a Great Rada (`zaz_host_great_rada`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Fortify the Frontier (`zaz_fortify_frontier`) | державність, прогрес кампанії, землі | землі, ресурси |
| Defend the Orthodox (`zaz_defend_orthodox`) | державність, походження, прогрес кампанії | ресурси |
| Take the Road of the Cantons (`zaz_road_of_the_cantons`) | прогрес кампанії | спеціальна умова |
| Take the Road of Host and State (`zaz_road_of_host_and_state`) | прогрес кампанії | спеціальна умова |
| Take the Road of the Sacred Order (`zaz_road_of_the_sacred_order`) | прогрес кампанії | спеціальна умова |
| Take the Road of the Sacred Horde (`zaz_road_of_the_sacred_horde`) | прогрес кампанії | спеціальна умова |
| Carry the Host Away (`cossack_carry_the_host`) | землі | ресурси, дипломатія й війна |
| Convene the Great Rada (`zaz_convene_great_rada`) | спеціальна умова | ресурси |
| Launch Chaiky Raid (`zaz_launch_chaiky_raid`) | спеціальна умова | ресурси |
| Expand the Cossack Register (`zaz_expand_register`) | спеціальна умова | ресурси |
| Abolish the Cossack Register (`zaz_abolish_register`) | спеціальна умова | ресурси |
| Recruit Steppe Cavalry (`zaz_recruit_steppe_cavalry`) | спеціальна умова | ресурси |
| Establish Sloboda Settlement (`zaz_establish_sloboda`) | спеціальна умова | спеціальна умова |
| Fortify Sloboda (`zaz_fortify_sloboda`) | спеціальна умова | спеціальна умова |
| Protect Orthodox Monasteries (`zaz_protect_orthodox`) | спеціальна умова | ресурси |
| Hold Hetman Election (`zaz_hold_hetman_election`) | спеціальна умова | спеціальна умова |

</details>

### Базова гра

<details><summary>abolishtheelectivemonarchy.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Abolish the Elective Monarchy (`boh_abolish_the_elective_monarchy`) | державність, прогрес кампанії | ресурси, дипломатія й війна |

</details>

<details><summary>africandecisions.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Colonize [1127.GetName] (`colonize_tuat_decision`) | прогрес кампанії | землі, дипломатія й війна |
| Colonize the Corridor (`colonize_djado_and_tajarhi_decision`) | прогрес кампанії | землі, дипломатія й війна |
| Focus on a professional Army (`set_focus_on_professional_army`) | прогрес кампанії | спеціальна умова |
| Send the Shaman to foreign Cults (`send_the_shaman_to_a_foreign_country`) | походження, прогрес кампанії | спеціальна умова |
| Switch Primary Cult (`swap_primary_cult`) | прогрес кампанії | прогрес кампанії, ресурси |
| Choose a new Cult (`switch_active_cult_decision`) | походження, прогрес кампанії | державність, походження, прогрес кампанії, ресурси |
| Replace Resident Scholar (`switch_permanent_scholar`) | походження, прогрес кампанії | прогрес кампанії |
| Invest into the Seven Cities (`invest_into_the_seven_cities`) | прогрес кампанії | прогрес кампанії |

</details>

<details><summary>aksumitenation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Aksum (`aksumite_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>alaskanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Alaska (`alaska_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>andalusiannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Al-Andalus (`andalusian_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>arabnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Arabia (`arab_nation`) | державність, походження, прогрес кампанії | походження, прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>armenianation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Kingdom of Armenia (`armenia_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, дипломатія й війна |
| Move the Capital to Tigranakert (`armenia_tigranakert`) | державність, прогрес кампанії | землі, дипломатія й війна |

</details>

<details><summary>australianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Australian Nation (`australia_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>austriahungarydecisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Compromise with the Hungarians (`compromise_with_hungarians`) | спеціальна умова | землі, дипломатія й війна |
| Compromise with the Austrians (`compromise_with_austrians`) | спеціальна умова | землі |

</details>

<details><summary>austriandecisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Habsburg Lands (`unite_habsburg_lands`) | спеціальна умова | землі |
| Unite with the Iberian Crown (`iberian_union_decision`) | державність, прогрес кампанії | державність, прогрес кампанії, дипломатія й війна |

</details>

<details><summary>ayyubiddecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Move the Capital to Damascus (`hsn_move_capital_to_damascus`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |

</details>

<details><summary>aztec_decisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Grant Generalship to Montezuma (`grant_generalship_to_montezuma`) | державність | дипломатія й війна |

</details>

<details><summary>bharatnation.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Bharat (`bharat_nation_dravidian`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Bharat (`bharat_nation_western_aryan`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Bharat (`bharat_nation_hindusthani`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Bharat (`bharat_nation_eastern_aryan`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Bharat (`bharat_nation_central_indic`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>brazilnation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Brazilian Nation (`brazil_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |
| Flee to Brazil (`por_flee_to_brazil`) | державність, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>britishnation.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form British Nation (`british_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Form British Nation Diplomatically (`british_nation_diplomatically`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |
| [Root.GetActsOfUnionDecisionTitle] (`force_british_union_debate`) | державність, прогрес кампанії | державність, час і технології, землі, дипломатія й війна |
| [Root.GetActsOfUnionDecisionTitle] (`force_french_union_debate`) | державність, прогрес кампанії | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>bukharanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Bukhara (`bukharan_nation`) | державність, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>bulgarianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Bulgaria (`bulgaria_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>byzantine_decisions.txt · 11</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Justinian's Empire (`BYZ_justinians_empire_decision`) | прогрес кампанії | прогрес кампанії, землі |
| Rebuild the Hexamilion Wall (`BYZ_build_hexamilion_wall_decision`) | прогрес кампанії | прогрес кампанії, землі, ресурси |
| Repair the Theodosian Walls (`BYZ_build_theodosian_wall_decision`) | прогрес кампанії | прогрес кампанії, землі, ресурси |
| Expand the Bosphorus Tolls (`BYZ_bosphorus_toll_decision`) | прогрес кампанії | спеціальна умова |
| Export Byzantine Mosaicists (`BYZ_mosaicists_decision`) | прогрес кампанії | прогрес кампанії, ресурси |
| Hold an Ecumenical Council (`BYZ_ecumenical_decision`) | прогрес кампанії | прогрес кампанії |
| End Latin Favoritism (`BYZ_revoke_exkousseiai`) | спеціальна умова | спеціальна умова |
| Repair the Army (`BYZ_revoke_deteriorating_army`) | спеціальна умова | прогрес кампанії, землі, військо |
| End the Union of the Churches (`BYZ_revoke_union_of_the_churches`) | походження | державність, походження, землі |
| Return to Orthodoxy (`BYZ_become_orthodox_again`) | походження | державність, походження, землі |
| Integrate Galata (`BYZ_integrate_galata`) | землі | спеціальна умова |

</details>

<details><summary>californianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Californian Nation (`california_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>canadanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Canadian Nation (`canada_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>cascadianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Cascadia (`cascadia_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>chilenation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Chilean Nation (`chile_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>china.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Repair of the Great Wall (`reparations_of_the_great_wall`) | державність, прогрес кампанії, землі | спеціальна умова |
| Construct the Forbidden City (`build_the_forbidden_city`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Government Reform (`no_more_celestial_empire`) | державність | час і технології |

</details>

<details><summary>civic.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Declare Statute in Restraint of Appeals (`statue_in_restraint_of_appeals`) | державність, походження, прогрес кампанії | дипломатія й війна |
| Pass Abolition of Slavery Act (`abolish_slavery_act`) | прогрес кампанії, час і технології | спеціальна умова |
| Revoke Restraint of Appeals (`revoke_restraint_of_appeals`) | державність, походження, прогрес кампанії | дипломатія й війна |

</details>

<details><summary>colombianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Colombian Nation (`colombia_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>colonialnations.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Colonial Assembly (`form_colonial_assembly`) | державність, прогрес кампанії, час і технології | ресурси, дипломатія й війна |

</details>

<details><summary>constructions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Improve Fort Defense (`eng_corps_boost`) | прогрес кампанії | дипломатія й війна |

</details>

<details><summary>courlandnation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reform into Kurland (`couronian_nation`) | державність, прогрес кампанії | походження, час і технології, землі, дипломатія й війна |
| Embrace Kurlander Identity (`couronian_nation_baltic_german`) | державність, походження, прогрес кампанії | походження, час і технології, землі, дипломатія й війна |

</details>

<details><summary>croatiannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Croatia (`croatian_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>cubanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Cuban Nation (`cuba_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>dalmatiannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reunite the Kingdom of Dalmatia (`dalmatian_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>danishdecisions.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Provoke Hanseatic Trade Conflict (`dan_provoke_trade_conflict_war`) | прогрес кампанії | спеціальна умова |
| Proclaim Title of Arch-[Root.Monarch.GetTitle] (`dan_proclaim_archking_title_decision`) | державність | спеціальна умова |
| Take the Aristocrats' Focus (`got_choose_aristocratic_gutnish_imperial_focus`) | прогрес кампанії | ресурси |
| Take the Traders' Focus (`got_choose_traders_gutnish_imperial_focus`) | прогрес кампанії | ресурси |
| Take the Guilds' Focus (`got_choose_guilds_gutnish_imperial_focus`) | прогрес кампанії | ресурси |
| Choose the Buccaneers' Focus of Piracy (`got_choose_the_buccaneers_focus`) | прогрес кампанії | ресурси |
| Choose the Smugglers' Focus of Piracy (`got_choose_the_smugglers_focus`) | прогрес кампанії | ресурси |
| Choose the Captains' Focus of Piracy (`got_choose_the_captains_focus`) | прогрес кампанії | ресурси |

</details>

<details><summary>deccannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Sultan of the Deccan (`deccan_nation`) | державність, походження, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>delhination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Sultan of Delhi (`sultan_of_delhi`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>dutch.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Found Oost-Indische Compagnie (`found_voc`) | державність, прогрес кампанії | час і технології, землі |
| Land Reclamation in Holland (`development_of_amsterdam`) | державність | час і технології, землі, ресурси |
| United the Two Crowns (`ned_unite_two_crowns`) | державність, прогрес кампанії | державність, час і технології, ресурси, дипломатія й війна |
| Overthrow Statist Stadholder (`overthrow_statist_stadholder`) | прогрес кампанії | спеціальна умова |

</details>

<details><summary>egyptiannation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Egypt (`egyptian_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Adopt Mamluk Government (`adopt_mamluk_government`) | державність, прогрес кампанії, землі | державність, землі |

</details>

<details><summary>electoratedecisions.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Purchase the Electorate (`purchase_the_electorate`) | спеціальна умова | походження, прогрес кампанії, ресурси, дипломатія й війна |
| Request the Electorate (`request_the_electorate`) | спеціальна умова | походження, прогрес кампанії, дипломатія й війна |
| Usurp the Electorate (`usurp_the_electorate`) | спеціальна умова | ресурси |

</details>

<details><summary>empireofchina.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reform the Administration (`reform_the_administration_of_china_decision`) | прогрес кампанії | ресурси |

</details>

<details><summary>england.txt · 7</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Designate Calais as The Staple Port (`designate_the_staple_port`) | державність, прогрес кампанії, землі | ресурси, дипломатія й війна |
| Offer a Purchase of [369.GetName] (`eng_make_orkney_offer`) | прогрес кампанії | ресурси, дипломатія й війна |
| Repeal Law Adjustments (`eng_abolish_adjustments_of_laws`) | прогрес кампанії | прогрес кампанії, ресурси, дипломатія й війна |
| End the Law Adjustments (`eng_end_the_law_discussions`) | прогрес кампанії | завжди |
| Resume the Law Adjustments (`eng_start_the_law_discussions`) | прогрес кампанії | спеціальна умова |
| Grant Autonomy to Colonial Enterprises (`eng_disable_colonial_ventures`) | прогрес кампанії | завжди |
| Revoke Autonomy from Colonial Enterprises (`eng_enable_colonial_ventures`) | прогрес кампанії | спеціальна умова |

</details>

<details><summary>englishnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form English Nation (`english_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>estateactionsbrahmins.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetBrahminsName]: Make Generous Donation (`estate_brahmins_make_generous_donation`) | спеціальна умова | спеціальна умова |
| [Root.GetBrahminsName]: Seek Brahmin Approval (`estate_brahmins_make_support_of_brahmins`) | спеціальна умова | спеціальна умова |
| [Root.GetBrahminsName]: Recruit Minister (`estate_brahmins_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetBrahminsName]: Recruit Inquisitor (`estate_brahmins_recruit_inquisitor`) | спеціальна умова | спеціальна умова |
| [Root.GetBrahminsName]: Demand Administrative Support (`estate_brahmins_demand_support_brahmin`) | спеціальна умова | спеціальна умова |
| [Root.GetBrahminsName]: Seek Legitimacy (`estate_brahmins_seek_brahmin_legitimacy`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsburghers.txt · 7</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetBurghersName]: Ask for Contribution (`estate_burghers_ask_for_contribution`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Demand Diplomatic Support (`estate_burghers_demand_support`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Grant Monopoly Charters (`estate_burghers_grant_monopoly_charter`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Recruit Minister (`estate_burghers_recruit_ministers`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Grant Admiralship (`estate_burghers_grant_admiralship`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Grant New World Charter (`estate_burghers_grant_new_world_charter`) | спеціальна умова | спеціальна умова |
| [Root.GetBurghersName]: Draft Ships for War (`estate_burghers_comission_merchant_ships_for_war`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionschuch.txt · 7</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetClergyName]: Make Generous Donation (`estate_church_make_generous_donation`) | спеціальна умова | спеціальна умова |
| [Root.GetClergyName]: Recruit Minister (`estate_church_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetClergyName]: Recruit Inquisitor (`estate_church_recruit_inquisitor`) | спеціальна умова | спеціальна умова |
| [Root.GetClergyName]: Religious Delegation (`estate_church_religious_delegation_action`) | державність | спеціальна умова |
| [Root.GetClergyName]: Demand Administrative Support (`estate_church_demand_support`) | спеціальна умова | спеціальна умова |
| [Root.GetClergyName]: Seek Support of the Clergy (`estate_church_seek_support_of_clergy`) | спеціальна умова | спеціальна умова |
| [Root.GetClergyName]: New World Missions (`estate_church_new_world_mission_action`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionscossacks.txt · 7</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetCossacksName]: Expand Cossack Register (`estate_cossacks_expand_cossack_registry`) | спеціальна умова | землі |
| [Root.GetCossacksName]: Raise Cossack Host (`estate_cossacks_raise_cossack_host`) | спеціальна умова | землі, військо |
| [Root.GetCossacksName]: Cossack Exploration Expedition (`estate_cossacks_cossack_conquistador`) | спеціальна умова | спеціальна умова |
| [Root.GetCossacksName]: Recruit Minister (`estate_cossacks_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetCossacksName]: Conscript Elite Cossacks (`estate_cossacks_conscript_cossack_elite`) | спеціальна умова | землі |
| [Root.GetCossacksName]: Supply Arms (`estate_cossacks_supply_arms_cossacks`) | спеціальна умова | спеціальна умова |
| [Root.GetCossacksName]: Permit Self Governance (`estate_cossacks_permit_self_governance`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsdhimmi.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetDhimmiName]: Recruit Minister (`estate_dhimmi_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetDhimmiName]: Lighten Dhimmi Tax Burden (`estate_dhimmi_lighten_dhimmi_tax_burden`) | спеціальна умова | спеціальна умова |
| [Root.GetDhimmiName]: Promote Dhimmi Nobles (`estate_dhimmi_promote_dhimmi_nobles`) | спеціальна умова | спеціальна умова |
| [Root.GetDhimmiName]: Recruit from the Dhimmi (`estate_dhimmi_recruit_from_the_dhimmi`) | спеціальна умова | спеціальна умова |
| [Root.GetDhimmiName]: Impose New Religious Tax (`estate_dhimmi_demand_contribution`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsghulams.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetGhilmanName]: Promote Caucasian Troops (`estate_ghulams_promote_caucasian_troops`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsjains.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetJainsName]: Procure a Loan (`estate_jains_procure_loans`) | спеціальна умова | спеціальна умова |
| [Root.GetJainsName]: Investigate Corruption (`estate_jains_investigate_corruption`) | спеціальна умова | ресурси |
| [Root.GetJainsName]: Patronize Jain Families (`estate_jains_patronize_jain_families`) | спеціальна умова | спеціальна умова |
| [Root.GetJainsName]: Commission Jain Scriptures (`estate_jains_commision_jain_scriptures`) | спеціальна умова | спеціальна умова |
| [Root.GetJainsName]: Demand Diplomatic Support (`estate_jains_demand_support`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsmaratha.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetMarathasName]: Promote Maratha Nobility (`estate_maratha_promote_maratha_nobility`) | спеціальна умова | спеціальна умова |
| [Root.GetMarathasName]: Recruit Minister (`estate_maratha_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetMarathasName]: Recruit from the Marathi (`estate_maratha_recruit_marathi_troops`) | спеціальна умова | спеціальна умова |
| [Root.GetMarathasName]: Demand Military Support (`estate_maratha_demand_support`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsnobles.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetNobilityName]: Call Diet (`estate_nobles_call_diet`) | спеціальна умова | спеціальна умова |
| [Root.GetNobilityName]: Grant Generalship (`estate_nobles_grant_generalship`) | спеціальна умова | спеціальна умова |
| [Root.GetNobilityName]: Recruit Conquistador (`estate_nobles_recruit_conquistador_estates`) | спеціальна умова | спеціальна умова |
| [Root.GetNobilityName]: Demand Military Support (`estate_nobles_demand_support`) | спеціальна умова | спеціальна умова |
| [Root.GetNobilityName]: Recruit Minister (`estate_nobles_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetNobilityName]: Raise Additional Levies (`estate_nobles_demand_more_troops`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsnomadictribes.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetTribesName]: Support Tribes (`estate_nomadic_tribes_support_tribes`) | спеціальна умова | спеціальна умова |
| [Root.GetTribesName]: Contribute Warriors (`estate_nomadic_tribes_contribute_warriors`) | спеціальна умова | ресурси |
| [Root.GetTribesName]: Raise Host (`estate_nomadic_tribes_raise_host`) | спеціальна умова | спеціальна умова |
| [Root.GetTribesName]: Recruit Minister (`estate_nomadic_tribes_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetTribesName]: Strengthen Tribal Autonomy (`estate_nomadic_tribes_strengthen_tribal_autonomy`) | спеціальна умова | спеціальна умова |
| [Root.GetTribesName]: Redistribute Horde Authority (`estate_nomadic_tribes_redistribute_horde_authority_tribes`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsqizilbash.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetQizilbashName]: Grant Qizilbash Horses (`estate_qizilbash_grant_qizilbash_horses`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsrajputs.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetRajputsName]: Recruit Rajput General (`estate_rajput_recruit_rajput_general`) | спеціальна умова | спеціальна умова |
| [Root.GetRajputsName]: Enlist Purbias (`estate_rajput_look_up_purbias_action`) | спеціальна умова | спеціальна умова |
| [Root.GetRajputsName]: Demand Military Support (`estate_rajput_demand_support`) | спеціальна умова | спеціальна умова |
| [Root.GetRajputsName]: Exempt From Jizya (`estate_rajput_exempt_from_jizya`) | походження | спеціальна умова |
| [Root.GetRajputsName]: Promote Rajput Nobility (`estate_rajput_promote_rajput_nobility`) | спеціальна умова | спеціальна умова |
| [Root.GetRajputsName]: Rajput Levies (`estate_rajput_recruit_rajput_troops`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>estateactionsvaisyas.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetVaishyasName]: Ask for Contribution (`estate_vaisyas_ask_for_contribution`) | спеціальна умова | спеціальна умова |
| [Root.GetVaishyasName]: Demand Diplomatic Support (`estate_vaisyas_demand_support`) | спеціальна умова | спеціальна умова |
| [Root.GetVaishyasName]: Seek Guild Support (`estate_vaisyas_seek_guild_support`) | спеціальна умова | спеціальна умова |
| [Root.GetVaishyasName]: Recruit (`estate_vaisyas_recruit_minister`) | спеціальна умова | спеціальна умова |
| [Root.GetVaishyasName]: Draft Ships for War (`estate_vaisyas_commision_merchant_ships_for_war`) | спеціальна умова | спеціальна умова |

</details>

<details><summary>ethiopianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Solomonid's Legacy (`ethiopia_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>fijination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Fiji (`unite_fiji`) | державність, походження, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>floridanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Floridian Nation (`florida_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>formaustriahungary.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form the Austro-Hungarian Empire (`form_austria_hungary`) | державність, походження, прогрес кампанії | державність, прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>formgreatmoravia.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Great Moravia (`great_moravia`) | державність, прогрес кампанії | державність, прогрес кампанії, час і технології, дипломатія й війна |
| Rebuild Veligrad (`restore_veligrad`) | державність, прогрес кампанії | землі, ресурси, дипломатія й війна |

</details>

<details><summary>france.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Move Court to Versailles (`move_the_court_to_versailles`) | державність, прогрес кампанії | час і технології |
| 'L'État c'est moi' (`say_the_state_is_me`) | державність, прогрес кампанії | час і технології |
| Enact Edict de Nantes (`enact_edict_de_nantes`) | державність, прогрес кампанії | походження, прогрес кампанії |
| Revoke Edict de Nantes (`revoke_edict_de_nantes`) | прогрес кампанії | походження |
| The Fate of Joan of Arc (`retrial_of_joan_of_arc`) | походження, прогрес кампанії, час і технології | дипломатія й війна |

</details>

<details><summary>frenchnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form French Nation (`french_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>georgianation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Georgia (`georgia_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |
| Move the Capital to Constantinople (`georgia_constantinople`) | державність, прогрес кампанії | землі, дипломатія й війна |

</details>

<details><summary>germandecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Choose Culture to Integrate (`GER_pick_culture_to_integrate`) | державність | спеціальна умова |

</details>

<details><summary>germannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form German Nation (`german_nation`) | державність, походження, прогрес кампанії, час і технології, землі | державність, прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>gondnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Kingdom of Nagpur (`gond_nation`) | державність, походження, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>governments.txt · 9</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Formalize Separation of Powers (`formalize_separation_of_powers`) | державність, прогрес кампанії | ресурси, дипломатія й війна |
| Cult of Reason (`go_cult_of_reason`) | прогрес кампанії | ресурси |
| Elevate Bishopric to an Archbishopric (`elevate_bishopric`) | державність | державність, походження |
| Force Re-election (`force_reelection`) | прогрес кампанії | прогрес кампанії, ресурси |
| Force Issue Through (`force_issue_through`) | прогрес кампанії | прогрес кампанії, ресурси |
| Promote Art (`promote_art`) | прогрес кампанії | спеціальна умова |
| Stop Promoting Art (`stop_promoting_art`) | прогрес кампанії | завжди |
| State of Conquerors (`state_of_conquerors`) | прогрес кампанії | прогрес кампанії |
| Select Grand Vizier (`grand_vizier_selection`) | спеціальна умова | прогрес кампанії |

</details>

<details><summary>greatzimbabwenation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Zimbabwe (`great_zimbabwe_nation`) | державність, прогрес кампанії, землі | державність, дипломатія й війна |

</details>

<details><summary>greeknation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Constantinople (`greek_orthodox_constantinople`) | походження, прогрес кампанії | землі, дипломатія й війна |

</details>

<details><summary>habsburgnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reclaim the Archduchy of Austria (`habsburg_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>haitination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Haitian Nation (`haiti_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>hanseaticleague.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Declare the Hanseatic League (`declare_hanseatic_league`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>hausanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Hausa (`hausa_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>hawaiination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Hawaii (`unite_hawaii`) | державність, походження, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>hindudeitydecision.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Choose Personal Deity Again (`brahmin_hindu_deity_decision`) | походження | прогрес кампанії |

</details>

<details><summary>hindustannation.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Hindustan (`hindustan_nation_dravidian`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Hindustan (`hindustan_nation_western_aryan`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Hindustan (`hindustan_nation_hindusthani`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Hindustan (`hindustan_nation_eastern_aryan`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |
| Form Hindustan (`hindustan_nation_central_indic`) | державність, походження, прогрес кампанії, землі | походження, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>hre_formablenations.txt · 7</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Bavaria (`bavaria_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Form Pomerania (`pomerania_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Form Franconia (`franconia_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Form Swabia (`swabia_nation`) | державність, походження, прогрес кампанії | землі, дипломатія й війна |
| Form Saxony (`saxony_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Form Hanover (`hannoverian_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Form Westphalia (`westfalian_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>hungariannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Hungarian Nation (`hungarian_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>hungary.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Abolish the Black Army (`abolish_black_army`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |

</details>

<details><summary>hussitefaith.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Adopt Hussitism (`become_hussite`) | державність, походження, землі | ресурси |

</details>

<details><summary>illinoisnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Illinoisan Nation (`illinois_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>incandecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Venture into Tribal Lands (`INC_colonize_surroundings`) | спеціальна умова | ресурси |

</details>

<details><summary>incannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Tawantinsuyu, the Empire of the Incas (`incan_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>incidentdecisions.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Rein in Italy (`shadow_kingdom_decision`) | прогрес кампанії, час і технології | державність, прогрес кампанії, землі |
| End the Great Peasants' War (`great_peasants_war_emperor_decision`) | прогрес кампанії | спеціальна умова |
| Enforce Peasant Demands (`great_peasants_war_peasant_decision`) | прогрес кампанії | спеціальна умова |

</details>

<details><summary>indiantradecompany.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Found Indian Trade Company (`indian_trade_company`) | державність, прогрес кампанії, час і технології, землі | час і технології, землі |
| Expel Foreign Traders (`expel_foreign_traders`) | землі | час і технології, ресурси, дипломатія й війна |

</details>

<details><summary>irishnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Irish Nation (`irish_nation`) | державність, походження, прогрес кампанії, землі | час і технології, дипломатія й війна |

</details>

<details><summary>israelnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Re-Establish Israel (`israel_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>italiannation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Italian Nation (`italian_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Declare the Kingdom of God (`gods_kingdom`) | державність, прогрес кампанії, землі | землі, дипломатія й війна |

</details>

<details><summary>japanesenation.txt · 6</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Japan! (`unite_japan`) | державність, прогрес кампанії | державність, землі, дипломатія й війна |
| Japan is united (`united_japan`) | державність, прогрес кампанії | державність, землі, дипломатія й війна |
| Japan is united (`united_japan_daimyo`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Enforce Sakoku Law (`enforce_sakoku_law`) | прогрес кампанії | ресурси |
| Western Embassy (`send_western_embassy_mission`) | державність, прогрес кампанії, час і технології | ресурси |
| Restore the Ise Shrines (`restore_the_shrine_of_ise`) | походження | землі, ресурси |

</details>

<details><summary>jerusalem.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reestablish The Kingdom of Jerusalem (`kingdom_of_jerusalem`) | державність, походження, прогрес кампанії, час і технології, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>kitaranation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Claim the Empire of Kitara Title (`kitara_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>knights.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Rhodians and other Greeks in the Order (`accept_rhodians_and_other_greeks`) | державність, прогрес кампанії | ресурси |

</details>

<details><summary>kok_arabian_decisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Cradle of Gold (`ARB_restore_cradle_of_gold`) | землі | спеціальна умова |
| Close the Cradle of Gold (`ARB_close_the_cradle_of_gold`) | землі | ресурси |

</details>

<details><summary>kongonation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Kongo Kingdom (`kongo_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>koreandecisions.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Found Hall of Worthies (`found_hall_of_worthies`) | спеціальна умова | спеціальна умова |
| The Sinmun Office (`establish_sinmun_office`) | державність, прогрес кампанії | спеціальна умова |
| Introduce the Hopae System (`hopae_system_decision`) | державність, прогрес кампанії | ресурси |
| Promote Sojunghwa (`promote_sojunghwa_decision`) | державність, прогрес кампанії | державність, походження, землі |
| Enforce the Hangul Alphabet (`enforce_hangeul_alphabet_decision`) | прогрес кампанії | прогрес кампанії |
| Revoke the Hangul Alphabet (`revoke_hangeul_alphabet_decision`) | прогрес кампанії | спеціальна умова |
| Reinforce the Tripitaka Koreana (`reinforce_tripitaka_koreana_decision`) | землі | землі |
| Evacuate the Tripitaka Koreana (`evacuate_tripitaka_koreana_decision`) | землі | землі |

</details>

<details><summary>lanfang_decisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Invite Kongsi Federations (`lanfang_decision`) | державність, землі | землі |
| Invite Kongsi Federations (`lanfang_decision_formation`) | державність, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>laplatanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form La Platan Nation (`la_plata_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>liberumveto.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Institute Liberum Veto (`liberum_veto`) | державність, походження, прогрес кампанії | землі, дипломатія й війна |

</details>

<details><summary>livoniandecisions.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Dissolve Bishopric (`liv_dissolve_bishopric`) | спеціальна умова | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Purchase Bishopric (`liv_purchase_bishopric`) | спеціальна умова | прогрес кампанії, землі, ресурси, дипломатія й війна |
| Dissolve Livonian Bishopric (`rig_dissolve_bishopric`) | державність, прогрес кампанії | державність, прогрес кампанії, землі, ресурси, дипломатія й війна |
| Purchase Livonian Bishopric (`rig_purchase_bishopric`) | державність, прогрес кампанії | державність, прогрес кампанії, ресурси, дипломатія й війна |
| Re-establish the Livonian Order (`rig_reestablish_livonian_order`) | державність, час і технології, землі | державність, час і технології |

</details>

<details><summary>livoniannation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reform into Livonia (`livonian_nation`) | державність, прогрес кампанії | походження, час і технології, землі, дипломатія й війна |
| Form Livonia (`livonian_nation_batlic_german`) | державність, походження, прогрес кампанії | походження, час і технології, землі, дипломатія й війна |

</details>

<details><summary>lotharingianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Kingdom of Lotharingia (`lotharingia_nation`) | державність, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>louisiananation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Louisianan Nation (`louisiana_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>macinanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Macina (`macina_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>maghrebicountryformations.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Moroccan Kingdom (`moroccan_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |
| Form Algerian Nation (`algiers_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |
| Form Tunisian Nation (`tunisian_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |
| Form Tripolitania (`tripoli_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>malayannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Malaya (`malayan_nation`) | державність, походження, прогрес кампанії, землі | походження, землі, дипломатія й війна |

</details>

<details><summary>malidecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Purchase Trade Colony (`mal_purchase_trade_colony`) | прогрес кампанії | ресурси, дипломатія й війна |

</details>

<details><summary>malination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Take the Mantle of Mali (`mali_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, дипломатія й війна |

</details>

<details><summary>manchudecisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Adopt Manchu Identity (`manchu_nation_1`) | державність, походження, прогрес кампанії | землі, дипломатія й війна |
| Qing Dynasty (`form_manchu_dynasty`) | державність, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>marathanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Maratha Confederation (`maratha_nation`) | державність, походження, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>mayanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reunite the League of Mayapan (`maya_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |

</details>

<details><summary>mexiconation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Mexican Nation (`mexico_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>military.txt · 8</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Enlist Privateers (`enlist_privateers`) | прогрес кампанії, час і технології | спеціальна умова |
| State Firearm Regiments (`state_firearm_regiments`) | прогрес кампанії, час і технології | час і технології |
| Abolish our Armed Elite Regiments (`abolish_state_firearm_regiments`) | прогрес кампанії | прогрес кампанії |
| Standardized Uniforms (`standardized_uniforms`) | прогрес кампанії, час і технології | спеціальна умова |
| Abolish Standardized Uniforms (`abolish_standardized_uniforms`) | прогрес кампанії | прогрес кампанії |
| The Righteous Army (`kor_righteous_army`) | прогрес кампанії | державність, прогрес кампанії, землі, дипломатія й війна |
| Raise the Ordenanças (`por_raise_the_ordenancas`) | прогрес кампанії | прогрес кампанії, дипломатія й війна |
| Rally the Volunteers (`gra_rally_the_volunteers`) | прогрес кампанії | походження, прогрес кампанії, дипломатія й війна |

</details>

<details><summary>misccountryformations.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Greece (`greek_nation`) | державність, походження, прогрес кампанії, землі | час і технології, землі, дипломатія й війна |
| Embrace Icelandic Identity (`icelandic_nation`) | державність, прогрес кампанії, землі | землі, дипломатія й війна |

</details>

<details><summary>mongolempire.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Mongol Empire (`restore_mongol_empire`) | державність, походження, прогрес кампанії | державність, прогрес кампанії, дипломатія й війна |
| Restore the Ilkhanate (`restore_ilkhanate_decision_march`) | державність, прогрес кампанії, землі | дипломатія й війна |
| Re-form the Ilkhanate (`restore_ilkhanate_decision`) | державність, походження, прогрес кампанії, землі | державність, дипломатія й війна |

</details>

<details><summary>mossidecisions.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Confederal Kingdoms: Gather the Armies (`federal_kingdoms_gather_the_armies`) | прогрес кампанії, землі | прогрес кампанії, ресурси, дипломатія й війна |
| Confederal Kingdoms: Arrange Marriage (`federal_kingdoms_internal_royal_marriage`) | прогрес кампанії, землі | прогрес кампанії, ресурси |
| Confederal Kingdoms: Celebrate Rituals (`federal_celebrate_rituals_together`) | прогрес кампанії, землі | прогрес кампанії, дипломатія й війна |
| Confederal Kingdoms: Gain Tribal Allegiance (`federal_gain_tribal_allegiance`) | прогрес кампанії, землі | прогрес кампанії, дипломатія й війна |

</details>

<details><summary>mossination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Mossi Kingdoms (`mossi_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>mughalnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Mughal Empire (`mughal_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>muslim.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unify Islam (`unify_islam`) | державність, походження, прогрес кампанії, землі | походження, прогрес кампанії, землі |
| Change Religion to Sunni (`change_religion_sunni`) | походження | походження |
| Change Religion to Shiite (`change_religion_shiite`) | походження | походження |
| Abandon Legalism (`abandon_the_legal_ways`) | прогрес кампанії | ресурси |
| Embrace Legalism (`return_to_the_legal_ways`) | прогрес кампанії | ресурси |

</details>

<details><summary>nativeamericans.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Shame Pole Debt (`pay_debt_shame_pole`) | державність, походження, прогрес кампанії | ресурси |
| An Honor Pole for an Ally (`erect_honour_pole_ally`) | державність, походження, прогрес кампанії | ресурси |
| An Honor Pole for our Tribe (`erect_honour_pole`) | державність, походження, прогрес кампанії | ресурси |
| Commission Some Rock Art (`commission_some_rock_art`) | державність, походження, прогрес кампанії | ресурси |

</details>

<details><summary>nepalnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unification of Nepal (`nepal_nation`) | походження, прогрес кампанії, час і технології, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>netherlandsnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Dutch Nation (`netherlands_nation`) | державність, походження, прогрес кампанії | державність, прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>new_decisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Establish American Frontier (`establish_american_frontier`) | прогрес кампанії | землі |
| Adopt Aztec Traditions (`adopt_aztec_traditions`) | державність, походження, прогрес кампанії, землі | державність |

</details>

<details><summary>nubiannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Nubians (`nubian_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, дипломатія й війна |

</details>

<details><summary>old_missions_decisions.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Become King of Gonder (`become_king_of_gonder`) | державність, прогрес кампанії, дипломатія й війна | землі |
| Defeat Saruhan (`defeat_saruhan`) | державність, прогрес кампанії, землі, дипломатія й війна | державність |
| Recover our Cultural Heritage (`recover_manga`) | державність, походження, землі, дипломатія й війна | землі |

</details>

<details><summary>orissanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Orissa (`orissa_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>ottoman.txt · 9</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Make Constantinople Capital (`make_constantinople_capital`) | державність, прогрес кампанії, землі | походження, землі, дипломатія й війна |
| Expand the Devshirme System (`devshirme_system`) | державність, прогрес кампанії | ресурси |
| Restore the Devshirme System (`restore_devshirme_system`) | державність, прогрес кампанії | ресурси |
| Force Janissaries to Undergo Yoklama (`disband_the_janissaries`) | спеціальна умова | спеціальна умова |
| Second Islamic Golden Age (`second_islamic_golden_era_descision`) | походження, прогрес кампанії | спеціальна умова |
| Face the Janissaries in the Balkans (`face_the_janissaries_1`) | прогрес кампанії | землі, ресурси |
| Face the Janissaries in Anatolia (`face_the_janissaries_2`) | прогрес кампанії | землі, ресурси |
| Face the Janissaries in [Root.Capital.GetName] (`face_the_janissaries_3`) | прогрес кампанії | ресурси |
| Negotiate with the Janissaries (`negotiate_with_the_janissaries`) | прогрес кампанії | ресурси |

</details>

<details><summary>paraguaynation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Paraguayan Nation (`paraguay_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>parliamentactions.txt · 17</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| [Root.GetParliamentOrFallbackName]: Acts of High Admiralty (`debate_acts_of_high_admiralty_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Maritime Courage Acts (`debate_acts_of_maritime_courage_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Acts of Maritime Professionalism (`debate_acts_of_maritime_professionalism_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Act of Naval Professionalism (`debate_acts_of_naval_professionalism_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Colonial Venture (`debate_colonial_venture_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Act of the Spanish Crown (`debate_crown_of_iberia_act_issue`) | прогрес кампанії | державність, землі |
| [Root.GetParliamentOrFallbackName]: Acts of Impressment (`debate_acts_of_impressment_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Taxation Acts (`debate_acts_of_taxation_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Acts of Representation (`debate_act_of_representation_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Act of the Italian Crown (`debate_crown_of_italy_act_issue`) | прогрес кампанії | державність, землі |
| [Root.GetParliamentOrFallbackName]: Crown of Ireland Act (`debate_crown_of_ireland_act_issue`) | прогрес кампанії | державність |
| [Root.GetParliamentOrFallbackName]: Crown of the Empire (`debate_crown_of_the_empire_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Gold Act (`debate_the_gold_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Spice Act (`debate_the_spice_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: The Sugar Act (`debate_the_sugar_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: Establish the Imperial Diet (`debate_establish_the_imperial_diet_act_issue`) | прогрес кампанії | спеціальна умова |
| [Root.GetParliamentOrFallbackName]: French-English Reconciliation Act (`debate_french_english_reconciliation_act_issue`) | прогрес кампанії | державність, походження |

</details>

<details><summary>persiannation.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Persian Nation (`persian_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |
| Establish the Iranian Name (`rename_to_iran`) | державність, прогрес кампанії | дипломатія й війна |
| Establish the Iranian Name (`rename_to_iran_non_rev`) | державність, прогрес кампанії | дипломатія й війна |

</details>

<details><summary>perunation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Peruvian Nation (`peru_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>pirategovernment.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Hoist the Black Flag (`become_pirates_decision`) | державність, прогрес кампанії, землі | державність, прогрес кампанії, землі, ресурси, дипломатія й війна |
| Enthrone a Pirate King (`pirate_king_decision`) | державність | прогрес кампанії, час і технології, ресурси |
| Establish a Black Market Consortium (`black_market_consortium_decision`) | державність | прогрес кампанії, час і технології, ресурси |
| Enact War Against the World Doctrine (`war_against_the_world_decision`) | державність | прогрес кампанії, час і технології, ресурси |
| Lower the Black Flag (`lower_black_flag_decision`) | державність | прогрес кампанії, ресурси |

</details>

<details><summary>poland.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Move Capital to Warsaw (`move_capital_to_warsawa`) | державність, прогрес кампанії, землі | дипломатія й війна |
| Revoke the Pacta Conventa (`revoke_the_pacta_conventa`) | державність, прогрес кампанії, землі | ресурси, дипломатія й війна |

</details>

<details><summary>polishnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Polish Nation (`polish_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>pragmaticsanction.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Pragmatic Sanction (`pragmatic_sanction_decision`) | прогрес кампанії | ресурси |

</details>

<details><summary>prussianconfederation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Curtail the Prussian Confederation (`curtail_prussian_confederation`) | прогрес кампанії | землі, ресурси |

</details>

<details><summary>prussiannation.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Kingdom of Prussia (`form_kingdom_of_prussia`) | державність, прогрес кампанії | державність, походження, час і технології, землі, дипломатія й війна |
| Reform into Prussia (`prussian_nation`) | державність, прогрес кампанії | державність, походження, прогрес кампанії, час і технології, землі, дипломатія й війна |
| Reform into Prussia (`prussian_nation_general`) | державність, походження, прогрес кампанії | державність, походження, час і технології, землі, дипломатія й війна |

</details>

<details><summary>punjabnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Kingdom of Punjab (`punjab_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, час і технології, землі, дипломатія й війна |

</details>

<details><summary>purple_phoenix_decisions.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Triumph for Greece (`triumph_greece`) | державність, прогрес кампанії | спеціальна умова |
| Triumph for the Balkans (`triumph_balkans`) | державність, прогрес кампанії | спеціальна умова |
| Triumph for the Asia minor coast (`triumph_asia`) | державність, прогрес кампанії | спеціальна умова |
| Triumph for Anatolia (`triumph_anatolia`) | державність, прогрес кампанії | спеціальна умова |
| Triumph for Italy (`triumph_italy`) | державність, прогрес кампанії | спеціальна умова |

</details>

<details><summary>quebecnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Quebecian Nation (`quebec_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>rajputnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Rajputs (`rajput_nation`) | державність, походження, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>releaseprussia.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Release Prussia (`boh_release_prussia`) | державність, прогрес кампанії | державність, дипломатія й війна |

</details>

<details><summary>religion.txt · 64</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Institute the Societas Jesu (`institute_the_societas_jesu`) | державність, походження, прогрес кампанії | час і технології |
| Pass De Heretico Comburendo Act (`de_heretico_comburendo_act`) | походження, прогрес кампанії | час і технології |
| Pass Advancement of Religion Act (`advancement_of_true_religion_act`) | походження, прогрес кампанії | спеціальна умова |
| Pass Blasphemy Act (`blasphemy_act`) | походження, прогрес кампанії, час і технології | спеціальна умова |
| Pass Declaration of Indulgence Act (`declaration_of_indulgence`) | походження, прогрес кампанії | прогрес кампанії, час і технології |
| Pass Act of Uniformity (`act_of_uniformity`) | походження, прогрес кампанії | час і технології |
| Establish Sunday Schools (`sunday_school`) | походження, прогрес кампанії, час і технології | ресурси |
| Pass Conventicle Act (`conventicle_act`) | походження, прогрес кампанії | час і технології |
| Pass Test Act (`test_act`) | походження, прогрес кампанії | прогрес кампанії, час і технології |
| Pass Dissolution of the Monasteries Act (`dissolution_of_the_monasteries`) | походження, прогрес кампанії | спеціальна умова |
| Pass Popery Act (`popery_act`) | походження, прогрес кампанії, час і технології | спеціальна умова |
| Enforce Religious Unity (`enforce_religion_muslim`) | походження | спеціальна умова |
| Adopt the Title of Khalifa (`the_khalifah`) | державність, походження | спеціальна умова |
| Denouncement of Sect Practices (`denouncement_of_sect_practices`) | походження | спеціальна умова |
| Islamic center of Scholarly Learning (`islamic_centre_of_scholarly`) | походження, час і технології | спеціальна умова |
| Monastic Education (`monastic_education`) | походження, прогрес кампанії | спеціальна умова |
| Embrace Wahabism (`adopt_wahabism`) | державність, походження, прогрес кампанії | спеціальна умова |
| Adopt Islam as the State Religion (`trade_propagation_convert_to_islam`) | походження | державність |
| Adopt Zoroastrianism as the State Religion (`trade_propagation_convert_to_zoroastrianism`) | походження | державність |
| Regulate the Monasteries (`regulate_the_monastaries`) | походження, прогрес кампанії, час і технології | спеціальна умова |
| Adopt Vajrayana Buddhism (`adopt_vajrayana`) | походження, час і технології, землі | ресурси, дипломатія й війна |
| Invite a Lama to Settle in Our Country (`invite_lama`) | походження, прогрес кампанії | ресурси, дипломатія й війна |
| Anti-Christian Edict (`anti_christian_edict`) | походження, прогрес кампанії | походження, дипломатія й війна |
| Establish an Ibadat Khana (`ibadat_khana`) | походження, прогрес кампанії | спеціальна умова |
| Introduce Din-i Illahi (`din_i_illahi`) | державність, походження, прогрес кампанії, землі | спеціальна умова |
| Anti-Muslim edict (`anti_muslim_edict`) | походження, прогрес кампанії, землі | ресурси |
| Accept Religious Sects (`acceptance_of_religious_sects`) | походження, прогрес кампанії | ресурси, дипломатія й війна |
| Support the Haridasa Movement (`haridasa_movement`) | походження, прогрес кампанії | прогрес кампанії, ресурси |
| Support the Advaita Movement (`advaita_movement`) | походження, прогрес кампанії | прогрес кампанії, ресурси |
| Encourage Divination (`divination`) | походження, прогрес кампанії | ресурси, дипломатія й війна |
| Religious Sacrifices (`religious_sacrifice`) | походження, прогрес кампанії | ресурси |
| Introduce Vision Quest (`vision_quest`) | походження, прогрес кампанії | спеціальна умова |
| Save the Burning World (`save_the_burning_world`) | походження, прогрес кампанії | спеціальна умова |
| Enforce our Heritage (`enforce_heritage`) | походження, прогрес кампанії | походження, ресурси |
| Encourage Conversion to Judaism (`restrict_government_offices`) | походження, прогрес кампанії | спеціальна умова |
| Spreading of Norse Rituals (`spreading_of_norse_rituals`) | походження, прогрес кампанії | спеціальна умова |
| Choose Personal Deity Again (`norse_flexible_deity_decision`) | походження, прогрес кампанії | прогрес кампанії |
| Restore the Temple of Uppsala (`norse_restore_the_uppsala_temple`) | державність, походження | походження, ресурси |
| The Religious Path of [Root.GetName] (`norse_gain_norse_missions`) | державність, походження, прогрес кампанії | походження |
| Yellow Shamanism (`tengri_yellow_shamanism`) | походження, прогрес кампанії | спеціальна умова |
| Black Shamanism (`tengri_black_shamanism`) | походження, прогрес кампанії | прогрес кампанії |
| Expel the Khojas (`tengri_expel_the_khojas`) | походження, прогрес кампанії, землі | спеціальна умова |
| Rites of Admission (`zoroastrian_rites_of_admission`) | походження, прогрес кампанії | ресурси |
| Rekindling the Royal Fires (`zoroastrian_royal_fires`) | походження, прогрес кампанії | державність, землі |
| Zoroastrian Diaspora (`zoroastrian_diaspora`) | походження, прогрес кампанії | походження, землі |
| Ritual Education (`animism_ritual_education`) | походження, прогрес кампанії, землі | час і технології, ресурси |
| Wandering Shamans (`shamanism_wondering_shamans`) | походження, прогрес кампанії, землі | час і технології, ресурси |
| Purification Movement (`totemism_purification_movement`) | походження, прогрес кампанії, землі | ресурси |
| Codification of the Faith (`mesoamerican_codification_of_the_faith`) | походження, прогрес кампанії, землі | час і технології, ресурси |
| Nahuatl Proselytization (`nahuatl_conversion_ceremonies`) | походження, прогрес кампанії, землі | час і технології, ресурси |
| Inti Proselytization (`inti_obligatory_religious_festivals`) | походження, прогрес кампанії, землі | час і технології, ресурси |
| Convert to Christianity (`pagan_conversion_to_christianity`) | походження, землі | державність, ресурси |
| Convert to Islam (`pagan_conversion_to_islam`) | походження, землі | державність, ресурси |
| Convert to Buddhism (`pagan_conversion_to_buddhism`) | походження, землі | державність, ресурси |
| Convert to an Indic Faith (`pagan_conversion_to_dharmic`) | походження, землі | державність, ресурси |
| Convert To Zoroastrianism (`pagan_conversion_to_zoroastrian`) | походження, землі | державність, ресурси |
| Convert To Judaism (`pagan_conversion_to_judaism`) | походження, землі | державність, ресурси |
| Convert to Sikhism (`muslim_conversion_to_sikhism`) | походження, землі | ресурси |
| Baptize Ruler (`shinto_christian_decision`) | походження, прогрес кампанії | ресурси |
| Time for a [Root.Religion.GetName] [Root.Monarch.GetTitle]? (`conversion_of_convenience`) | спеціальна умова | ресурси |
| Renovate the Emerald Buddha Shrine (§YKarma +§!) (`renovate_emerald_buddha_shrine`) | походження, землі | спеціальна умова |
| Renovate the Emerald Buddha Shrine (§YKarma -§!) (`renovate_emerald_buddha_shrine_alternate`) | походження, землі | спеціальна умова |
| Consultate the Monasteries (`buddhism_consulate_monasteries`) | прогрес кампанії | прогрес кампанії |
| Build the Third Temple (`build_the_third_temple`) | походження, прогрес кампанії | походження |

</details>

<details><summary>religiousconversion.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Embrace the Counter-Reformation (`join_the_counter_reformation`) | походження, прогрес кампанії | державність, прогрес кампанії, дипломатія й війна |
| Kirishitan Conversion (`christian_daimyo`) | державність, походження, землі | ресурси |
| Embrace Islam (`malay_islam_decision`) | походження | ресурси |

</details>

<details><summary>restorebyzantineempire.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Byzantine Empire (`restore_byzantine_empire`) | державність, походження, прогрес кампанії | землі, дипломатія й війна |

</details>

<details><summary>restorecolororname.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Our Name (`restore_name_decision`) | прогрес кампанії | державність, дипломатія й війна |
| Restore our Color (`restore_color_decision`) | прогрес кампанії | державність, дипломатія й війна |

</details>

<details><summary>restoreromanempire.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Roman Empire (`restore_roman_empire`) | державність, походження, прогрес кампанії, землі | землі, дипломатія й війна |

</details>

<details><summary>revolutionaryguard.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Elite Revolutionary Guard Training (`elite_revolutionary_guard`) | прогрес кампанії | спеціальна умова |
| Professional Revolutionary Guard Training (`professional_revolutionary_guard`) | прогрес кампанії | спеціальна умова |
| Mass Revolutionary Guard Training (`mass_revolutionary_guard`) | прогрес кампанії | спеціальна умова |
| Vanguard Revolutionary Guard Training (`vanguard_revolutionary_guard`) | прогрес кампанії | спеціальна умова |

</details>

<details><summary>romaniannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Romanian Nation (`romanian_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>rozwination.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Establish Rozwi (`rozwi_nation`) | державність, прогрес кампанії, землі | державність, дипломатія й війна |

</details>

<details><summary>russia.txt · 5</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Make St. Petersburg the Capital (`make_st_petersburg_capital`) | державність, прогрес кампанії, землі | дипломатія й війна |
| Establish Russian Patriarchate (`establish_russian_patriarchate`) | державність, походження, прогрес кампанії | ресурси, дипломатія й війна |
| Promote Vodka Sales (`rus_sell_vodka_to_the_people`) | прогрес кампанії | прогрес кампанії |
| Abolish the Serfdom (`rus_abolish_the_serfdom`) | прогрес кампанії | ресурси |
| Proclaim the Emperor Title (`rus_claim_emperor_title`) | державність, прогрес кампанії | землі |

</details>

<details><summary>sardinapiedmontnation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Sardinia-Piedmont (`sardinia_piedmont_nation`) | державність, походження, прогрес кампанії | державність, походження, час і технології, землі, дипломатія й війна |
| Form Sardinia-Piedmont Diplomatically (`sardinia_piedmont_nation_inherit`) | державність, прогрес кампанії | державність, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>scandinaviannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Scandinavian Nation (`scandinavian_nation`) | державність, походження, прогрес кампанії, час і технології, землі | прогрес кампанії, час і технології, землі, дипломатія й війна |

</details>

<details><summary>scottishnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Scottish Nation (`scottish_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>sea_decisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Grow Cloves in Zanzibar (`grow_cloves_in_zanzibar`) | землі | землі |

</details>

<details><summary>sea_reformables.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore Dai Viet (`restore_dai_viet`) | державність, походження, прогрес кампанії, землі | державність, дипломатія й війна |
| Restore Lan Xang (`restore_lan_xang`) | державність, походження, прогрес кампанії, землі | державність, дипломатія й війна |

</details>

<details><summary>serbia.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Move Capital to Belgrade (`capital_in_belgrade`) | державність, прогрес кампанії | походження, землі, ресурси |

</details>

<details><summary>shadowkingdom.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Rein in Northern Italy (`stop_shadow_kingdom`) | прогрес кампанії | державність, час і технології |

</details>

<details><summary>shannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Confederate the Shan States (`shan_nation`) | державність, походження, прогрес кампанії, землі | землі, дипломатія й війна |

</details>

<details><summary>shintoconversion.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Kirishitan Question (`become_kirishitan_daimyo`) | походження, прогрес кампанії | походження |
| The Divine Wind (`become_ikko_ikki_daimyo`) | походження, прогрес кампанії | походження |
| Adopt Confucian Administration (`become_confucian_daimyo`) | походження, прогрес кампанії | походження |

</details>

<details><summary>siamesenation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Siamese Nation (`siamese_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>siamrevolutiondecisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Arrest Phetracha (`arrest_phetracha_decision`) | прогрес кампанії | ресурси |
| Support Phetracha (`phetracha_coup_decision`) | прогрес кампанії | ресурси |

</details>

<details><summary>silesian_nation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Silesian Nation (`silesia_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>sinicize.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Sinicize our Culture (`sinicize_culture`) | походження | походження |

</details>

<details><summary>sokotonation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Create the Sokoto Caliphate (`sokoto_nation`) | державність, походження, прогрес кампанії | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>somalianation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Somalian Clans (`somalia_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>sonoranation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Sonora Nation (`sonora_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>spanishnation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Spanish Nation Militarily (`spanish_nation`) | державність, походження, прогрес кампанії, землі | державність, походження, час і технології, землі, дипломатія й війна |
| Form Spanish Nation Diplomatically (`spanish_nation_diplomatically`) | державність, прогрес кампанії, землі | державність, походження, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>swedishdecisions.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Repay Debt to the [Root.GetChurchOrFallbackName] (`swe_repay_estate_church`) | прогрес кампанії | державність, походження, ресурси, дипломатія й війна |
| Repay Debt to the [Root.GetBurghersOrFallbackName] (`swe_repay_estate_burghers`) | прогрес кампанії | державність, дипломатія й війна |
| Repay Debt to the [Root.GetNobilityOrFallbackName] (`swe_repay_estate_nobles`) | прогрес кампанії | державність, військо, дипломатія й війна |
| Proclaim Protection for the Protestants (`swe_provoke_religious_leagues_forming_decision`) | прогрес кампанії | походження, час і технології, дипломатія й війна |

</details>

<details><summary>swissnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Swiss Confederacy (`switzerland_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>tatarnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Re-form the Golden Horde (`tatar_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>texasnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Texan Nation (`texas_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>thecommonwealth.txt · 3</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Polish-Lithuanian Commonwealth (`pol_commonwealth`) | державність, прогрес кампанії, землі | державність, прогрес кампанії, час і технології, землі, ресурси, дипломатія й війна |
| Form Lithuanian-Polish Commonwealth (`lit_commonwealth`) | державність, прогрес кампанії, землі, дипломатія й війна | державність, час і технології, землі, ресурси, дипломатія й війна |
| Enforce a Commonwealth (`commonwealth_enforced`) | державність, прогрес кампанії | державність, час і технології, землі, ресурси, дипломатія й війна |

</details>

<details><summary>thehansa.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| The Lübeck Krantor (`build_lubeck_krantor`) | державність, прогрес кампанії, землі | ресурси |
| The 'Adler von Lübeck' (`commission_adler_von_lubeck`) | державність, прогрес кампанії, землі | ресурси, дипломатія й війна |

</details>

<details><summary>tibetannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Tibetan Nation (`tibetan_nation`) | державність, походження, прогрес кампанії, землі | походження, землі, дипломатія й війна |

</details>

<details><summary>timurid_decisions.txt · 4</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Treasury (`TIM_bring_taxation_under_control`) | спеціальна умова | прогрес кампанії, землі, дипломатія й війна |
| Supremacy of the Sharia (`TIM_supremacy_of_the_sharia`) | спеціальна умова | прогрес кампанії, землі |
| Commission the Peacock Throne (`MUG_commission_the_peacock_throne`) | прогрес кампанії | прогрес кампанії, землі |
| Viceroyalty of Deccan (`MUG_viceroyalty_of_deccan`) | прогрес кампанії | державність, землі |

</details>

<details><summary>timuridnation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Enthrone Timurid Prince (`enthrone_timurid_prince`) | державність, походження, час і технології | державність, час і технології, землі |
| Claim Timur's Legacy (`timurid_nation`) | державність, походження, прогрес кампанії | державність, землі, дипломатія й війна |

</details>

<details><summary>trade.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Close Foreign Trade (`close_foreign_trade`) | прогрес кампанії | дипломатія й війна |
| Stop Foreign Slave Trade (`stop_foreign_slave_trade`) | прогрес кампанії | державність, час і технології, ресурси |

</details>

<details><summary>transfernitra.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Transfer the Ownership of Nitra (`boh_transfer_nitra`) | державність, прогрес кампанії | державність, дипломатія й війна |

</details>

<details><summary>turkishnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Restore the Sultanate of Rûm (`turkish_nation`) | державність, походження, прогрес кампанії | державність, походження, землі, дипломатія й війна |

</details>

<details><summary>tuscannation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Tuscany (`tuscan_nation`) | державність, походження, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>tutorial.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Spanish Nation Diplomatically (`spanish_nation_diplomatically_tutorial`) | державність, землі | державність, дипломатія й війна |

</details>

<details><summary>twosiciliesnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite the Two Sicilies (`two_sicilies_nation`) | державність, походження, прогрес кампанії | час і технології, землі, дипломатія й війна |

</details>

<details><summary>upcanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Central American Nation (`upca_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>usanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form American Nation (`usa_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>venezuelanation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Venezuelan Nation (`venezuela_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>venice.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Confirm Thalassocracy (`confirm_thalassocracy`) | прогрес кампанії | спеціальна умова |
| Replenish Mercenary Ranks (`replenish_mercenary_ranks`) | прогрес кампанії, землі | прогрес кампанії |

</details>

<details><summary>vermontnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Vermonter Nation (`vermont_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>voc_decisions.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Establish the VOC (`establish_voc`) | державність, прогрес кампанії | землі |
| Expand the VOC (`expand_voc`) | спеціальна умова | землі |

</details>

<details><summary>westindiesnation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Caribbean Nation (`west_indies_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |

</details>

<details><summary>yemennation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Unite Yemen (`yemen_nation`) | державність, походження, прогрес кампанії, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>yuandecisions.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Hold Naadam Festival (`yua_hold_naadam_festival`) | прогрес кампанії | прогрес кампанії |

</details>

<details><summary>yuannation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Reform Great Yuan (`form_great_yuan`) | державність, походження, прогрес кампанії, землі | державність, походження, землі, ресурси, дипломатія й війна |
| Restore Great Yuan (`hordes_restore_yuan`) | державність, прогрес кампанії | державність, землі |

</details>

<details><summary>zealandianation.txt · 2</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Form Zealandia (`zealandia_nation`) | державність, прогрес кампанії, землі | державність, час і технології, землі, дипломатія й війна |
| Form Aotearoa (`aotearoa_nation`) | державність, походження, землі | державність, землі, дипломатія й війна |

</details>

<details><summary>zulunation.txt · 1</summary>

| Рішення | Видимість | Виконання |
| --- | --- | --- |
| Militarize the Nguni (`zulu_nation`) | державність, походження, прогрес кампанії | державність, час і технології, землі, дипломатія й війна |

</details>
