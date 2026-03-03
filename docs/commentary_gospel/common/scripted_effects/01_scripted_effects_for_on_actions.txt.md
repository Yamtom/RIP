# Commentary Gospel ? 01_scripted_effects_for_on_actions.txt

- Source: `common/scripted_effects/01_scripted_effects_for_on_actions.txt`
- Extraction date: 2026-03-02
- Extracted descriptive comments: 10

## Canonical Excerpts

| Original line | Commentary |
|---:|---|
| 1 | Estate Privilege on_action effects are in 01_scripted_effects_for_estates.txt |
| 472 | Mlira and other Nature Spirits and/or ancestral cults of Central Africa |
| 1026 | country_event = { id = flavor_sax.4 days = 1 } |
| 1233 | Fire an event which checks on the current state of Burgundy to see if they are already in a normal PU or not |
| 3264 | Empty as there are no modifiers specific for this age |
| 3850 | THIS = Province, FROM = Country, ROOT = Merc Unit |
| 4159 | ALWAYS call this AFTER swap_non_generic_missions has been set or else the preview missions won't update |
| 4162 | Clear potential messes with name / map color changes |
| 4179 | Clear all flags which add the preview buttons if you do not have any mission enabling them |
| 4185 | if = {	#Commented out for now because Catholicism has received a lot of buffs already. |

## Supplemental Excerpts (2026-03-02)

| Current line | Commentary |
|---:|---|
| 322 | Setting it to 0 |
| 443 | Cwezi / Swezi / Kubandwa |
| 700 | Dharmic Cult |
| 731 | Teotl Cult |
| 765 | Norse Cult |
| 796 | Jewish Cult |
| 827 | Zoroastrian Cult |
| 1221 | Burgundian succession stuff |
| 1250 | Burgundian marriage cleaner |
| 2297 | Province effect |
| 2342 | ##removes catholic modifiers |
| 2517 | Country effect |
| 2533 | on_culture_demoted_effect_free_slot_removal = { |
| 2534 | if = { |
| 2535 | limit = { |
| 2536 | has_country_modifier = free_slot_for_$culture$ |
| 2537 | NOT = { accepted_culture = $culture$ } |
| 2538 | NOT = { primary_culture = $culture$ } |
| 2539 | } |
| 2540 | remove_country_modifier = free_slot_for_$culture$ |
| 2541 | } |
| 2542 | } |
| 2543 |  |
| 2544 | on_culture_demoted_effect_remove_all_free_slots = { |
| 2545 | on_culture_demoted_effect_free_slot_removal = { culture = armenian } |
| 2546 | on_culture_demoted_effect_free_slot_removal = { culture = georgian } |
| 2547 | on_culture_demoted_effect_free_slot_removal = { culture = turkish } |
| 2548 | on_culture_demoted_effect_free_slot_removal = { culture = al_iraqiya_arabic } |
| 2549 | on_culture_demoted_effect_free_slot_removal = { culture = al_suryah_arabic } |
| 2550 | on_culture_demoted_effect_free_slot_removal = { culture = occitain } |
| 2551 | } |
| 2553 | Country effect |
| 2555 | if = { |
| 2556 | limit = { |
| 2557 | has_country_flag = boh_czechoslovak_brotherhood_flag |
| 2558 | NOT = { |
| 2559 | accepted_culture = slovak |
| 2560 | } |
| 2561 | has_country_modifier = boh_czechoslovak_brotherhood |
| 2562 | } |
| 2563 | remove_country_modifier = boh_czechoslovak_brotherhood |
| 2564 | } |
| 2565 | if = { |
| 2566 | limit = { |
| 2567 | has_country_flag = hun_polish_culture_bonus |
| 2568 | NOT = { |
| 2569 | accepted_culture = polish |
| 2570 | } |
| 2571 | has_country_modifier = hun_polish_brotherhood |
| 2572 | } |
| 2573 | remove_country_modifier = hun_polish_brotherhood |
| 2574 | } |
| 2575 | if = { |
| 2576 | limit = { |
| 2577 | has_country_modifier = plc_polish_lithuanian_union |
| 2578 | OR = { |
| 2579 | AND = { |
| 2580 | primary_culture = polish |
| 2581 | NOT = { accepted_culture = lithuanian } |
| 2582 | } |
| 2583 | AND = { |
| 2584 | primary_culture = lithuanian |
| 2585 | NOT = { accepted_culture = polish } |
| 2586 | } |
| 2587 | AND = { |
| 2588 | OR = { |
| 2589 | NOT = { accepted_culture = lithuanian } |
| 2590 | NOT = { accepted_culture = polish } |
| 2591 | } |
| 2592 | NOT = { primary_culture = polish } |
| 2593 | NOT = { primary_culture = lithuanian } |
| 2594 | } |
| 2595 | } |
| 2596 | } |
| 2597 | remove_country_modifier = plc_polish_lithuanian_union |
| 2598 | } |
| 2599 | if = { |
| 2600 | limit = { |
| 2601 | has_country_modifier = teu_pru_integration_of_the_poles |
| 2602 | NOT = { accepted_culture = polish } |
| 2603 | NOT = { primary_culture = polish } |
| 2604 | } |
| 2605 | remove_country_modifier = teu_pru_integration_of_the_poles |
| 2606 | } |
| 2607 | if = { |
| 2608 | limit = { |
| 2609 | has_country_modifier = teu_pru_integration_of_the_ruthenians |
| 2610 | NOT = { accepted_culture = polish } |
| 2611 | NOT = { primary_culture = polish } |
| 2612 | } |
| 2613 | remove_country_modifier = teu_pru_integration_of_the_ruthenians |
| 2614 | } |
| 2772 | Country effect |
| 2827 | Province effect |
| 2916 | Country effect |
| 3008 | Country effect |
| 3255 | if = { |
| 3256 | limit = { |
| 3257 | NOT = { current_age = age_of_revolutions } |
| 3258 | } |
| 3259 | } |
| 3310 | Generic ones |
| 3519 | test if colonists outnumber natives |
| 3557 | test if colonists outnumber natives |
| 4157 | Remove tag-locked modifiers |
| 4168 | Update event targets |
| 4176 | limit = { |
| 4177 | FROM = { religion = catholic } |
| 4178 | } |
| 4179 | if = { |
| 4180 | limit = { ROOT = { government_rank = 3 } } |
| 4181 | FROM = { add_papal_influence = 20 } |
| 4182 | } |
| 4183 | else_if = { |
| 4184 | limit = { ROOT = { government_rank = 2 } } |
| 4185 | FROM = { add_papal_influence = 10 } |
| 4186 | } |
| 4187 | else = { |
| 4188 | FROM = { add_papal_influence = 5 } |
| 4189 | } |
| 4190 | } |
