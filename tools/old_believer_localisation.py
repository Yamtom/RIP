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
 'old_believer_religion_desc': 'Communities preserving the pre-reform Russian rites and rejecting the reformed hierarchy. The province religion represents a majority; smaller communities remain provincial modifiers.',
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
 'desc_rip_ob_tolerant_policy': "Tolerance of heretics +1 and yearly patriarchal authority -0.5 percentage points. The communities are protected without dissolving the confessional distinction.",
 'rip_ob_repressive_policy': 'Enforcement of the Revised Books',
 'desc_rip_ob_repressive_policy': "Tolerance of heretics -1 and yearly patriarchal authority +0.5 percentage points. The communities keep their local penalties after the Raskol ends.",
}
