"""English names for the Old Believer religion, rebels, communities and policy.

Emitted into localisation/replace/zzzz_RIP_church_redesign_l_*.yml by
tools/build_church_localisation.py, which refuses to start if a key here is
also owned by tools/ro_history_localisation.py: this file adds Old Believer
keys, it never overrides a Muscovite-history one.

The keys are read by common/religions/zzz_old_believer.txt,
common/rebel_types/old_believer.txt, events/RIP_OldBelievers.txt,
decisions/RIP_OldBelievers.txt and
common/event_modifiers/rip_old_believer_modifiers.txt. The three strings of the
console fixture live next to it, in tests/dev_tools/rip_ob_test_l_english.yml.

The Raskol disaster ends when the patriarch's authority falls below 60%, so the
policy texts say what each policy does to that pace and nothing about a timer.
"""
COPY = {
 'old_believer': 'Old Believer',
 'old_believer_religion_desc': 'Communities preserving the old Russian rites and rejecting the revised books. State institutions support visiting priests or lay elders, community assemblies, and endowed refuges. These are available through decisions. There is no common patriarchal-authority resource. The province religion represents a majority; smaller communities remain provincial modifiers.',
 'old_believer_rebels_name': '$RELIGION$ Zealots',
 'old_believer_rebels_title': 'Old Believer Zealots',
 'old_believer_rebels_desc': 'These communities defend the old books. Their success can establish Old Believer majorities. A state conversion requires their faith to be dominant.',
 'old_believer_rebels_army': 'Old Believer Host',
 'old_believer_rebels_demand': 'Freedom for the Old Rite',
 'old_believer_rebels_demand_desc': 'Protect the Old Believers; if their faith is dominant, adopt it as the state confession.',
 'rip_ob.2.t': 'The Old Rite Takes Root',
 'rip_ob.2.d': 'An Old Believer community has grown for at least a decade. Acknowledge its majority, or maintain the mixed settlement through greater autonomy. Neither choice erases the community.',
 'rip_ob.2.a': 'Acknowledge the Old Believer majority',
 'rip_ob.2.b': 'Maintain a mixed settlement with greater autonomy',
 'rip_ob.3.t': 'Families of the Old Rite',
 'rip_ob.3.d': 'Families from a neighbouring Old Believer parish have established a minority here. The province keeps its religion.',
 'rip_ob.3.a': 'Record the community',
 'rip_ob_tolerate_title': 'Guarantee the Old Rite',
 'rip_ob_tolerate_desc': "Spend 50 ADM to protect the Old Believer communities. Local unrest falls in exchange for tax concessions, tolerance of heretics rises, and the patriarch's authority drains faster, which brings the end of the Raskol nearer. The policy can change once every ten years. The communities outlast it.",
 'rip_ob_repress_title': 'Enforce the Revised Books',
 'rip_ob_repress_desc': "Spend 50 ADM to enforce uniformity. Tolerance of heretics falls and the patriarch's authority drains more slowly, so the Raskol lasts longer; the communities pay in unrest and manpower for as long as the policy stands. The policy can change once every ten years.",
 'rip_ob_adopt_old_rite_title': 'Adopt the Old Believer Confession',
 'rip_ob_adopt_old_rite_desc': 'Requires an Old Believer capital and dominant faith, peace, 1 stability and 100 ADM. Costs 100 ADM and 1 stability, and sets the policy of toleration. Changes the state confession only: the country leaves the Muscovite jurisdiction, and provincial majorities retain their faith.',
 'rip_ob_local_community': 'Old Believer Community',
 'desc_rip_ob_local_community': 'A persistent community, not necessarily a provincial majority. It survives conquest and the end of the Raskol.',
 'rip_ob_local_toleration': 'Old Rite Guaranteed',
 'desc_rip_ob_local_toleration': 'The current ruler guarantees the community in exchange for tax concessions.',
 'rip_ob_local_repression': 'Old Rite Persecuted',
 'desc_rip_ob_local_repression': 'Enforcement increases local unrest and reduces manpower.',
 'rip_ob_tolerant_policy': 'Toleration of the Old Rite',
 'desc_rip_ob_tolerant_policy': "Tolerance of heretics +1. Within the Muscovite jurisdiction, yearly patriarchal authority also falls by 0.5 percentage points; an Old Believer state has no common patriarchal-authority resource.",
 'rip_ob_repressive_policy': 'Enforcement of the Revised Books',
 'desc_rip_ob_repressive_policy': "Tolerance of heretics -1 and yearly patriarchal authority +0.5 percentage points. The communities keep their local penalties after the Raskol ends.",
}


# Three state institutions; generator-owned in all four fallback languages.
COPY.update({
 'rip_ob_choose_accord_title': 'Settle the Organization of the Old Rite',
 'rip_ob_choose_accord_desc': 'Current settlement: [Root.GetOldBelieverAccord].\\nChoose support for visiting priests or worship under lay elders. Costs 75 ADM and 100 ducats. A later change costs an additional 1 stability. Peace, at least 0 stability; change once every 20 years. Payment is made only on confirmation. This policy models patronage of diverse communities, not a single historical Old Believer church.',
 'rip_ob_hold_assembly_title': 'Convene the Community Assembly',
 'rip_ob_hold_assembly_desc': 'Current mandate: [Root.GetOldBelieverMandate].\\nFor 50 ADM and 75 ducats, choose a 10-year mandate: manuscript schools (-5% idea cost, -0.5% missionary strength), or mutual aid (-1 national unrest, -5% national tax). One mandate at a time. Peace, at least 0 stability; once every 10 years. Confirmation lists the effects.',
 'rip_ob_endow_refuge_title': 'Endow a Refuge of the Old Rite',
 'rip_ob_endow_refuge_desc': 'Propose one randomly selected eligible non-capital core with an existing Old Believer community or majority. The event names the randomly proposed site, which can be accepted or declined freely; it is not a manual map selection. Costs 50 DIP, 100 ducats and adds 10 local autonomy. Refuge: -1 local unrest, +15% local production efficiency, -15% local tax and -1% local missionary strength. One foundation per 10 years; fewer than 3 foundations must already be owned. Minority communities and provincial religion are preserved. Benefits require an Old Believer ruler or the toleration policy and are suspended by repression.',
 'rip_ob_institutions.1.t': 'Priests and Lay Elders',
 'rip_ob_institutions.1.d': 'The old books survive; the succession of clergy is harder to secure. Some communities receive priests who leave the reformed church, while others entrust prayer and teaching to lay elders. Neither policy gives us a patriarch or a new episcopal hierarchy.\\nCurrent settlement: [Root.GetOldBelieverAccord]. Confirmation costs 75 ADM and 100 ducats; changing an existing settlement also costs 1 stability. Its benefits last while we follow the Old Rite, and its 20-year lock survives conversion.',
 'rip_ob_institutions.1.a': 'Support visiting priests',
 'rip_ob_institutions.1.b': 'Entrust worship to lay elders',
 'rip_ob_institutions.2.t': 'The Community Assembly',
 'rip_ob_institutions.2.d': 'Delegates bring petitions from the settlements. The common purse can sustain the copying of old books and the teaching of readers, or support alms and mutual aid. The choice binds our expenditure for a decade.\\nCurrent mandate: [Root.GetOldBelieverMandate]. Each choice costs 50 ADM and 75 ducats and lasts 10 years. The school mandate reduces idea cost by 5% and missionary strength by 0.5%; mutual aid reduces unrest by 1 at the cost of 5% tax.',
 'rip_ob_institutions.2.a': 'Sustain manuscript schools',
 'rip_ob_institutions.2.b': 'Fund alms and mutual aid',
 'rip_ob_institutions.3.t': 'A Refuge for the Old Books',
 'rip_ob_institutions.3.d': "The proposed site is [event_target:rip_ob_refuge_site.GetName]. Its existing community asks for a prayer house, workshops and a secure endowment. The land remains under its present faith; this foundation does not convert a province.\\nConfirm for 100 ducats and 50 DIP; local autonomy rises by 10. While protected: unrest -1, production efficiency +15%, tax -15%, missionary strength -1%. The foundation survives conquest; the new ruler's faith and policy determine whether its benefits remain active.",
 'rip_ob_institutions.3.a': 'Endow the named refuge',
 'rip_ob_institutions.defer': 'Leave the matter open',
 'rip_ob_no_accord': 'No settlement chosen',
 'rip_ob_no_mandate': 'No current mandate',
 'rip_ob_priestly_accord': 'Patronage of Visiting Priests',
 'desc_rip_ob_priestly_accord': 'Communities receive clergy from outside the old-rite settlements. Missionary strength +1%, yearly prestige +0.5; tax income -5% pays for their support. This grants no patriarchate or nineteenth-century episcopal succession.',
 'rip_ob_lay_accord': 'Worship under Lay Elders',
 'desc_rip_ob_lay_accord': 'Readers and lay elders direct communal worship and preserve the old books. Tolerance of the true faith +1 and idea cost -5%, at the cost of missionary strength -1%. Communities retain their diversity.',
 'rip_ob_manuscript_mandate': 'Manuscript Schools',
 'desc_rip_ob_manuscript_mandate': 'The community assembly supports readers, scribes and the study of old books. For 10 years: idea cost -5%, missionary strength -0.5%. A game-design interpretation of community scholarship.',
 'rip_ob_mutual_aid_mandate': 'Communal Mutual Aid',
 'desc_rip_ob_mutual_aid_mandate': 'The assembly directs funds to alms and relief. For 10 years: national unrest -1, national tax -5%.',
 'rip_ob_active_refuge': 'Endowed Old Rite Refuge',
 'desc_rip_ob_active_refuge': 'An endowed prayer house and workshops sustain an existing Old Believer community. Local unrest -1, production efficiency +15%, tax -15%, missionary strength -1%. Benefits cease under repression or an unprotective conqueror; the community and foundation survive.',
 'rip_ob_inactive_refuge': 'Suspended Old Rite Endowment',
 'desc_rip_ob_inactive_refuge': 'The refuge foundation and its community survive, but its benefits are suspended. An Old Believer ruler or the toleration policy can reactivate them; repression overrides either form of protection.',
})
