"""Generate church UI localisation and fallback strings; no claim of translated fallback text."""
from pathlib import Path
import json,argparse,re
ROOT=Path(__file__).resolve().parents[1]
# The province action GUARANTEES another confessional community its rights
# (rite, clergy, local church jurisdiction). It is not that community accepting
# the Union. Player-visible name: 'Guarantee community rights'. Internal ids
# keep the older 'recognize' spelling on purpose: the province flag
# rip_church_rite_recognized lives in savegames, and modifiers, effects,
# triggers and GUI widgets are named after it.
# Numbers: common/event_modifiers/RIP_church_redesign_modifiers.txt (rip_church_rite,
# _favoured, _ecumenical, _revoked) and common/scripted_effects/rip_church_union_effects.txt
# (1 ADM per development; 3650-day revoke lock). Net on a guaranteed province:
# normal -2.5 unrest / -15% tax / -20% manpower; ecumenical -3 / -10% / -15%.
RITE_KEEPS='The province keeps its religion; it is not converted and does not enter the Union.'
RITE_MODEL=('This province-level marker is a gameplay abstraction, not an exact historical parish or canonical status, '
            'and not evidence of voluntary acceptance of the Union.')
RITE_INTERPRETATION=('The tax and manpower reductions are a game-design interpretation of the administrative compromise of '
                     'protecting local arrangements and autonomy, not a penalty for another faith and not a documented historical formula.')
RITE_TERMS=('Costs 1 ADM per development and lasts at least ten years. Unrest falls by 2, plus 0.5 from the protected local tradition; '
            'local tax falls by 15% and manpower by 20%. '+RITE_INTERPRETATION+
            ' After the ecumenical settlement: unrest -3, tax -10%, manpower -15%.')
COMMUNITIES_TT=('Communities whose rights we guarantee, Eastern and Latin. '
                'These province-level counts are a gameplay abstraction, not an exact historical parish or canonical status, '
                'and not evidence of voluntary acceptance of the Union.')
RITE_REVOKE=('No refund. The province gains +3 unrest for ten years. Revoking counts as forced integration, which invites Orthodox '
             'backlash and bars the ecumenical settlement for ten years.')
# Requirements: rip_church_can_ecumenism. Benefits: rip_church_rite_ecumenical vs
# rip_church_rite_favoured, and rip_church_opinion_gc_ecumenical (+15, mutual, no decay).
ECUMENISM_REQUIRES=('Requires twenty years of union, no forced integration in the last ten, stability +2, peace, '
                    'guaranteed community rights in an Orthodox and in a Latin province, and an Orthodox ally with opinion +100. '
                    'Muscovite Orthodox provinces and states do not count.')
ECUMENISM_BENEFITS=('In every province with guaranteed rights the extra unrest reduction rises from 0.5 to 1 and the tax and levy '
                    'penalties shrink by 5 points each (net unrest -3, tax -10%, levies -15%). '
                    'This is a limited diplomatic and local administrative settlement between Eastern and Latin communities, not a restoration of full ecclesial communion. '
                    'Its +15 is diplomatic goodwill only: Orthodox and Catholic states gain +15 mutual opinion; Russian Orthodox states are excluded. '
                    'The settlement costs nothing and is not withdrawn once concluded.')
ECUMENISM_TT='A limited diplomatic and local administrative settlement between Eastern and Latin communities.\\n'+ECUMENISM_REQUIRES+'\\n'+ECUMENISM_BENEFITS
ECUMENISM_DESC=('Conclude a limited diplomatic and local administrative settlement between the Eastern and Latin communities once community rights are guaranteed in both '
                'and the historical and diplomatic conditions are met. It deepens every guarantee. Its +15 is diplomatic goodwill only: Orthodox and Catholic states gain +15 mutual opinion; Russian Orthodox states are excluded. '
                'It is not a restoration of full ecclesial communion.')
# Province panel: rip_church_recognize_rite_button tooltip (custom_button), then the help block under the buttons.
RITE_BUTTON_TT=("Gameplay abstraction: guarantee the rights represented for this province's Orthodox or Catholic community. "
                +RITE_MODEL+' '+RITE_KEEPS+' '+RITE_TERMS)
# On-panel text (Main_14, 440 x 150 px, at most ten lines even at 7 px per character): the essentials only.
RITE_HELP=("Gameplay abstraction: not an exact parish or canonical status, or proof of voluntary Union acceptance. The province keeps its faith; no conversion is implied. "
           "Costs §Y1 ADM per development§!; lasts at least 10 years. "
           "Unrest -2 (-0.5 from protected tradition); tax -15%, manpower -20%; no religious-unity penalty. "
           "Game-design interpretation: tax and manpower reductions model the administrative compromise of protecting local arrangements and autonomy—not a penalty for another faith and not a documented historical formula. "
           "After ecumenical settlement: unrest -3, tax -10%, manpower -15%. Revoke: +3 unrest for 10 years.")
# Hover text on that block: the details.
RITE_HELP_TT=(RITE_MODEL+' '+RITE_KEEPS+' While the guarantee stands, Union backlash events and Muscovite missionary networks skip the province. '
              'The ecumenical settlement deepens it to unrest -3, tax -10% and levies -15%. '
              'It lapses if the owner leaves the Union or the province changes faith. '
              'Orthodox and Muscovite Orthodox provinces count as Eastern in the country panel, Catholic provinces as Latin. '
              'Only a Greek Catholic owner can guarantee rights.')
DATA={
  "greek_catholic_religion_desc": "A broad game category covering several distinct Ruthenian and Carpathian Eastern Catholic union traditions and jurisdictions in communion with Rome, not one church institution and not the modern Ukrainian Greek Catholic Church in its narrow sense. Brest, Uzhhorod, Peremyshl, Lviv and Lutsk have distinct local histories, chronologies and jurisdictions; these rules do not imply that every region followed the same path or belonged to one institution. Availability from 6 July 1439 uses the Florentine union as a precedent for an alternative historical path, not as the founding of the UGCC or an established separate confession. The Union of Brest in 1596 is a distinct later milestone. Their hierarchies retain internal authority, represented by Patriarch Authority. The Curia panel records diplomatic relations only.",
  "rip_church_close": "Close",
  "rip_church.2.t": "Moscow and the Third Rome",
  "rip_church.2.d": "Writers at the Muscovite court describe Moscow as a guardian of the Orthodox inheritance. This sixteenth-century political theology does not itself create a new creed or end communion with the eastern patriarchates. Universal jurisdiction would require a separate, deliberate claim.",
  "rip_church.2.a": "Cultivate the Third Rome ideal",
  "rip_church.2.b": "Emphasize our place among the Orthodox churches",
  "rip_church.3.t": "A Recognized Patriarchate",
  "rip_church.3.d": "The ecclesiastical settlement recognizes our patriarchate within the wider Orthodox communion. Moscow accepts its place after the four ancient eastern patriarchates. Our centralized church remains a distinct political institution; recognition does not abolish its internal responsibilities.",
  "rip_church.5.t": "The Florentine Legacy Reaffirmed",
  "rip_church.5.d": "Our negotiated settlement draws on the Florentine union of 1439 as a precedent; historically, it did not gain lasting general acceptance. This campaign-created alternative does not represent the founding of the UGCC in 1439 or an unbroken institutional line to Brest in 1596: the Byzantine rite and its bishops remain, while communion with Rome is accepted. Integration is represented province by province; that game abstraction does not establish a canonical parish status or local voluntary consent.",
  "rip_church.6.t": "The Institutions of Communion",
  "rip_church.6.d": "The Eastern hierarchy keeps its own institutions. A local synod may establish infrastructure or an agreement of coexistence. The Curia panel records Rome and permits a diplomatic audience; it grants no electoral rights or numerical standing.",
  "rip_church_recognition_refuse": "Claim an independent universal church — alternative history",
  "rip_church_nodes.1.t": "Fund the Missionary Network",
  "rip_church_nodes.1.d": "Register an eligible node, then select Missionary Network in its native merchant policies. Registration prepays 2 Fervor and reserves 2 Fervor each month until closed, even if a different trade policy is selected. Each node needs a merchant, 50% trade power, a controlled core parish with a temple connected to the capital's Muscovite church, and neighbouring missionary targets. One node is allowed; the schismatic branch allows two.",
  "rip_church_mission_network": "Missionary Network",
  "rip_church_mission_network_desc": "A funded network of monasteries, traders and frontier parishes. Requires a registered node, merchant, 50% trade power, connected controlled church infrastructure and an active Apostolic Mission. Conversion is gradual.",
  "rip_church_ro_heading": "THE MUSCOVITE CHURCH\\n[Root.GetChurchROStatus]",
  "rip_church_ro_resources": "Authority band: [Root.rip_church_pa_display.GetValue]%\\nIcons: [Root.rip_church_icons.GetValue] / [Root.rip_church_capacity.GetValue]   Fervor: [Root.rip_church_fervor.GetValue] / 100\\nMonthly fuel: +[Root.rip_church_fervor_income.GetValue] / -[Root.rip_church_fervor_cost.GetValue]   Missions: [Root.rip_church_nodes.GetValue]",
  "rip_church_ro_help": "Authority supplies capacity; Fervor pays for active policies. Activation: 10 Fervor. Upkeep for 1/2/3/4 icons: 2/4/8/14 monthly, plus 2 per funded node. The newest icon closes first if capacity or fuel runs out.",
  "rip_church_gc_heading": "THE UNION OF THE CHURCHES",
  "rip_church_gc_resources": "Eastern hierarchy: [Root.rip_church_pa_display.GetValue]% authority",
  "rip_church_gc_help": "Patriarchal Authority belongs to the Eastern hierarchy. Local synodal institutions are separate from diplomatic contact with Rome. Guarantee community rights from an owned province's panel.",
  "rip_church_gc_privilege_state": "Active settlement: [Root.GetChurchPrivilege]",
  "rip_church_nodes_button": "Missionary networks",
  "rip_church_reconcile_button": "Negotiate reconciliation",
  "rip_church_privileges_button": "Church privileges",
  "rip_church_ecumenism_button": "Conclude ecumenical settlement",
  "rip_church_gc_infrastructure_button": "Eastern infrastructure",
  "rip_church_gc_coexistence_button": "Agreement of coexistence",
  "rip_church_rite_heading": "COMMUNITY RIGHTS",
  "rip_church_rite_state": "[Root.GetChurchRiteStatus]",
  "rip_church_rite_help": RITE_HELP,
  "rip_church_recognize_rite_button": "Guarantee community rights",
  "rip_church_revoke_rite_button": "Revoke community rights",
  "rip_church_rite_affordable_tt": "We hold 1 ADM for every point of development in this province.",
  "rip_church_ro_unrecognized": "Unrecognized autocephaly",
  "rip_church_ro_provisional": "Patriarchate recognized; conciliar confirmation pending",
  "rip_church_ro_recognized": "Recognized patriarchate within Orthodox communion",
  "rip_church_ro_schismatic": "Independent Third Rome church — alternative history",
  "rip_church_ro_reconciling": "Reconciliation under negotiation",
  "rip_church_active": "ACTIVE",
  "rip_church_inactive": "Inactive",
  "rip_church_none": "None",
  "rip_church_rite_recognized": "Gameplay abstraction: community rights are guaranteed in this province. This is not an exact canonical status or evidence of voluntary Union acceptance; the province keeps its faith.",
  "rip_church_rite_unrecognized": "Community rights are not guaranteed in this province.",
  "rip_church_nodes_button_tt": "Register or close missionary networks. Registration prepays 2 Fervor; each registered node reserves 2 per month. Choose the native Missionary Network trade policy after funding.",
  "rip_church_reconcile_button_tt": "Costs 100 DIP and 20 Authority. Negotiations last at least five years and conclude at peace with stability 1. Universal claims are renounced; internal discontent lasts ten years.",
  "rip_church_ecumenism_button_tt": ECUMENISM_TT,
  "rip_church_recognize_rite_button_tt": RITE_BUTTON_TT,
  "rip_church_revoke_rite_button_tt": "After at least ten years, revoke the guarantee. "+RITE_REVOKE,
  "rip_church_gc_infrastructure_button_tt": "The local synod's infrastructure decision costs Patriarchal Authority and ducats and lasts ten years.",
  "rip_church_gc_coexistence_button_tt": "The local synod's agreement of coexistence costs Patriarchal Authority and ducats and lasts ten years.",
  "rip_church_request_recognition_title": "Seek recognition of our patriarchate",
  "rip_church_request_recognition_desc": "Seek recognition within the wider Orthodox communion from 1589. Delay leaves the question open; rejection is a deliberate alternative schism. Constantinople need not be an independent state.",
  "rip_church_reconcile_title": "Reconcile with the eastern patriarchates",
  "rip_church_reconcile_desc": "Costs 100 DIP and 20 Authority. Negotiations last at least five years and conclude at peace with stability 1. Universal claims are renounced; internal discontent lasts ten years.",
  "rip_church_florence_title": "Invoke the Florentine precedent — alternative history",
  "rip_church_florence_desc": "Alternative history, 1444-1501. The union of 6 July 1439 is a Florentine precedent for this alternative path, not the founding of the UGCC or an established separate confession. The Union of Brest in 1596 remains a distinct later milestone. Pay 200 ADM, 100 DIP and one year's income for five years of negotiations. Requires stability 2, peace and PAP opinion 100. The Eastern hierarchy keeps its rite while entering communion with Rome; Catholic patrons retain their state religion.",
  "rip_church_sponsor_union_title": "Sponsor an Eastern Catholic union",
  "rip_church_sponsor_union_desc": "From 1596, a Catholic crown may support an Eastern union without changing its state religion. Pay 100 ADM, 100 DIP and one year's income. The state action changes one eligible core province's religion to Greek Catholic; it is separate from a community-rights guarantee and does not report local consent.",
  "rip_church_ecumenism_title": "Conclude the ecumenical settlement",
  "rip_church_ecumenism_desc": ECUMENISM_DESC,
  "rip_church_icon_war_button": "Military Intercession",
  "rip_church_icon_war_button_tt": "+2.5% discipline; +5% manpower recovery. Activate for 10 Fervor; each icon may be reactivated only after one year. Deactivation is immediate and gives no refund.",
  "rip_church_icon_war_state": "[Root.GetChurchIconWar]",
  "rip_church_icon_mercy_button": "Mercy",
  "rip_church_icon_mercy_button_tt": "-1 unrest; -10% harsh treatment cost. Activate for 10 Fervor; each icon may be reactivated only after one year. Deactivation is immediate and gives no refund.",
  "rip_church_icon_mercy_state": "[Root.GetChurchIconMercy]",
  "rip_church_icon_building_button": "Church Building",
  "rip_church_icon_building_button_tt": "-5% development and building cost. Activate for 10 Fervor; each icon may be reactivated only after one year. Deactivation is immediate and gives no refund.",
  "rip_church_icon_building_state": "[Root.GetChurchIconBuilding]",
  "rip_church_icon_mission_button": "Apostolic Mission",
  "rip_church_icon_mission_button_tt": "+0.5 percentage points missionary strength; access to funded trade missions. Activate for 10 Fervor; each icon may be reactivated only after one year. Deactivation is immediate and gives no refund.",
  "rip_church_icon_mission_state": "[Root.GetChurchIconMission]",
  "rip_church_ro_heading_tt": "THE MUSCOVITE CHURCH\\n[Root.GetChurchROStatus]",
  "rip_church_ro_resources_tt": "Authority band: [Root.rip_church_pa_display.GetValue]%\\nIcons: [Root.rip_church_icons.GetValue] / [Root.rip_church_capacity.GetValue]   Fervor: [Root.rip_church_fervor.GetValue] / 100\\nMonthly fuel: +[Root.rip_church_fervor_income.GetValue] / -[Root.rip_church_fervor_cost.GetValue]   Missions: [Root.rip_church_nodes.GetValue]",
  "rip_church_ro_help_tt": "Authority supplies capacity; Fervor pays for active policies. Activation: 10 Fervor. Upkeep for 1/2/3/4 icons: 2/4/8/14 monthly, plus 2 per funded node. The newest icon closes first if capacity or fuel runs out.",
  "rip_church_gc_heading_tt": "THE UNION OF THE CHURCHES",
  "rip_church_gc_resources_tt": "The displayed authority belongs to the Eastern hierarchy; it is not a Curia resource.",
  "rip_church_gc_help_tt": "Local synod decisions and diplomatic contact with Rome are separate. Guarantee community rights from an owned province's panel.",
  "rip_church_gc_privilege_state_tt": "Active settlement: [Root.GetChurchPrivilege]",
  "rip_church_rite_heading_tt": "COMMUNITY RIGHTS",
  "rip_church_rite_state_tt": "[Root.GetChurchRiteStatus]",
  "rip_church_rite_help_tt": RITE_HELP_TT,
  "rip_church_icon_war_state_tt": "[Root.GetChurchIconWar]",
  "rip_church_icon_mercy_state_tt": "[Root.GetChurchIconMercy]",
  "rip_church_icon_building_state_tt": "[Root.GetChurchIconBuilding]",
  "rip_church_icon_mission_state_tt": "[Root.GetChurchIconMission]",
  "rip_church_icon_war": "icon war",
  "desc_rip_church_icon_war": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_icon_mercy": "icon mercy",
  "desc_rip_church_icon_mercy": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_icon_building": "icon building",
  "desc_rip_church_icon_building": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_icon_mission": "icon mission",
  "desc_rip_church_icon_mission": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_high": "ro high",
  "desc_rip_church_ro_high": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_max": "ro max",
  "desc_rip_church_ro_max": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_high_recognized": "ro high recognized",
  "desc_rip_church_ro_high_recognized": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_max_recognized": "ro max recognized",
  "desc_rip_church_ro_max_recognized": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_schism": "ro schism",
  "desc_rip_church_ro_schism": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_reconciliation_unrest": "reconciliation unrest",
  "desc_rip_church_reconciliation_unrest": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_infrastructure": "gc infrastructure",
  "desc_rip_church_gc_infrastructure": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_coexistence": "gc coexistence",
  "desc_rip_church_gc_coexistence": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_legate": "gc legate",
  "desc_rip_church_gc_legate": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_dynastic": "gc dynastic",
  "desc_rip_church_gc_dynastic": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_prestige": "gc prestige",
  "desc_rip_church_gc_prestige": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_rite": "rite",
  "desc_rip_church_rite": "Gameplay abstraction: our Greek Catholic government marks community rights as guaranteed in this province. This is not an exact canonical status or evidence of voluntary Union acceptance. "+RITE_KEEPS+" Lasts at least ten years. "+RITE_INTERPRETATION,
  "rip_church_rite_favoured": "rite favoured",
  "desc_rip_church_rite_favoured": "The guarantee of community rights also protects local tradition: a further -0.5 unrest. Replaced by the ecumenical accommodation once the ecumenical settlement is concluded; the two never stack.",
  "rip_church_rite_ecumenical": "rite ecumenical",
  "desc_rip_church_rite_ecumenical": "The ecumenical settlement deepens the guarantee: -1 unrest instead of -0.5, and the tax and levy penalties of the guarantee shrink by 5 points each. Replaces the protected local tradition.",
  "rip_church_rite_revoked": "rite revoked",
  "desc_rip_church_rite_revoked": "The guarantee of community rights was revoked: +3 unrest for ten years.",
  "rip_church_gc_roman_resistance": "gc roman resistance",
  "desc_rip_church_gc_roman_resistance": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_conversion_resistance": "conversion resistance",
  "desc_rip_church_conversion_resistance": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_local_see": "gc local see",
  "desc_rip_church_gc_local_see": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_conversion_pressure": "conversion pressure",
  "desc_rip_church_conversion_pressure": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_0": "ro pa country 0",
  "desc_rip_church_ro_pa_country_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_0": "gc pa country 0",
  "desc_rip_church_gc_pa_country_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_0": "ro pa local 0",
  "desc_rip_church_ro_pa_local_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_0": "gc east pa local 0",
  "desc_rip_church_gc_east_pa_local_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_0": "gc middle pa local 0",
  "desc_rip_church_gc_middle_pa_local_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_0": "gc rome pa local 0",
  "desc_rip_church_gc_rome_pa_local_0": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_1": "ro pa country 1",
  "desc_rip_church_ro_pa_country_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_1": "gc pa country 1",
  "desc_rip_church_gc_pa_country_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_1": "ro pa local 1",
  "desc_rip_church_ro_pa_local_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_1": "gc east pa local 1",
  "desc_rip_church_gc_east_pa_local_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_1": "gc middle pa local 1",
  "desc_rip_church_gc_middle_pa_local_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_1": "gc rome pa local 1",
  "desc_rip_church_gc_rome_pa_local_1": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_2": "ro pa country 2",
  "desc_rip_church_ro_pa_country_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_2": "gc pa country 2",
  "desc_rip_church_gc_pa_country_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_2": "ro pa local 2",
  "desc_rip_church_ro_pa_local_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_2": "gc east pa local 2",
  "desc_rip_church_gc_east_pa_local_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_2": "gc middle pa local 2",
  "desc_rip_church_gc_middle_pa_local_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_2": "gc rome pa local 2",
  "desc_rip_church_gc_rome_pa_local_2": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_3": "ro pa country 3",
  "desc_rip_church_ro_pa_country_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_3": "gc pa country 3",
  "desc_rip_church_gc_pa_country_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_3": "ro pa local 3",
  "desc_rip_church_ro_pa_local_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_3": "gc east pa local 3",
  "desc_rip_church_gc_east_pa_local_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_3": "gc middle pa local 3",
  "desc_rip_church_gc_middle_pa_local_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_3": "gc rome pa local 3",
  "desc_rip_church_gc_rome_pa_local_3": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_4": "ro pa country 4",
  "desc_rip_church_ro_pa_country_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_4": "gc pa country 4",
  "desc_rip_church_gc_pa_country_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_4": "ro pa local 4",
  "desc_rip_church_ro_pa_local_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_4": "gc east pa local 4",
  "desc_rip_church_gc_east_pa_local_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_4": "gc middle pa local 4",
  "desc_rip_church_gc_middle_pa_local_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_4": "gc rome pa local 4",
  "desc_rip_church_gc_rome_pa_local_4": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_5": "ro pa country 5",
  "desc_rip_church_ro_pa_country_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_5": "gc pa country 5",
  "desc_rip_church_gc_pa_country_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_5": "ro pa local 5",
  "desc_rip_church_ro_pa_local_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_5": "gc east pa local 5",
  "desc_rip_church_gc_east_pa_local_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_5": "gc middle pa local 5",
  "desc_rip_church_gc_middle_pa_local_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_5": "gc rome pa local 5",
  "desc_rip_church_gc_rome_pa_local_5": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_6": "ro pa country 6",
  "desc_rip_church_ro_pa_country_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_6": "gc pa country 6",
  "desc_rip_church_gc_pa_country_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_6": "ro pa local 6",
  "desc_rip_church_ro_pa_local_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_6": "gc east pa local 6",
  "desc_rip_church_gc_east_pa_local_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_6": "gc middle pa local 6",
  "desc_rip_church_gc_middle_pa_local_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_6": "gc rome pa local 6",
  "desc_rip_church_gc_rome_pa_local_6": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_7": "ro pa country 7",
  "desc_rip_church_ro_pa_country_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_7": "gc pa country 7",
  "desc_rip_church_gc_pa_country_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_7": "ro pa local 7",
  "desc_rip_church_ro_pa_local_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_7": "gc east pa local 7",
  "desc_rip_church_gc_east_pa_local_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_7": "gc middle pa local 7",
  "desc_rip_church_gc_middle_pa_local_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_7": "gc rome pa local 7",
  "desc_rip_church_gc_rome_pa_local_7": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_8": "ro pa country 8",
  "desc_rip_church_ro_pa_country_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_8": "gc pa country 8",
  "desc_rip_church_gc_pa_country_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_8": "ro pa local 8",
  "desc_rip_church_ro_pa_local_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_8": "gc east pa local 8",
  "desc_rip_church_gc_east_pa_local_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_8": "gc middle pa local 8",
  "desc_rip_church_gc_middle_pa_local_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_8": "gc rome pa local 8",
  "desc_rip_church_gc_rome_pa_local_8": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_9": "ro pa country 9",
  "desc_rip_church_ro_pa_country_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_9": "gc pa country 9",
  "desc_rip_church_gc_pa_country_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_9": "ro pa local 9",
  "desc_rip_church_ro_pa_local_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_9": "gc east pa local 9",
  "desc_rip_church_gc_east_pa_local_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_9": "gc middle pa local 9",
  "desc_rip_church_gc_middle_pa_local_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_9": "gc rome pa local 9",
  "desc_rip_church_gc_rome_pa_local_9": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_10": "ro pa country 10",
  "desc_rip_church_ro_pa_country_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_10": "gc pa country 10",
  "desc_rip_church_gc_pa_country_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_10": "ro pa local 10",
  "desc_rip_church_ro_pa_local_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_10": "gc east pa local 10",
  "desc_rip_church_gc_east_pa_local_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_10": "gc middle pa local 10",
  "desc_rip_church_gc_middle_pa_local_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_10": "gc rome pa local 10",
  "desc_rip_church_gc_rome_pa_local_10": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_11": "ro pa country 11",
  "desc_rip_church_ro_pa_country_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_11": "gc pa country 11",
  "desc_rip_church_gc_pa_country_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_11": "ro pa local 11",
  "desc_rip_church_ro_pa_local_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_11": "gc east pa local 11",
  "desc_rip_church_gc_east_pa_local_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_11": "gc middle pa local 11",
  "desc_rip_church_gc_middle_pa_local_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_11": "gc rome pa local 11",
  "desc_rip_church_gc_rome_pa_local_11": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_12": "ro pa country 12",
  "desc_rip_church_ro_pa_country_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_12": "gc pa country 12",
  "desc_rip_church_gc_pa_country_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_12": "ro pa local 12",
  "desc_rip_church_ro_pa_local_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_12": "gc east pa local 12",
  "desc_rip_church_gc_east_pa_local_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_12": "gc middle pa local 12",
  "desc_rip_church_gc_middle_pa_local_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_12": "gc rome pa local 12",
  "desc_rip_church_gc_rome_pa_local_12": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_13": "ro pa country 13",
  "desc_rip_church_ro_pa_country_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_13": "gc pa country 13",
  "desc_rip_church_gc_pa_country_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_13": "ro pa local 13",
  "desc_rip_church_ro_pa_local_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_13": "gc east pa local 13",
  "desc_rip_church_gc_east_pa_local_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_13": "gc middle pa local 13",
  "desc_rip_church_gc_middle_pa_local_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_13": "gc rome pa local 13",
  "desc_rip_church_gc_rome_pa_local_13": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_14": "ro pa country 14",
  "desc_rip_church_ro_pa_country_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_14": "gc pa country 14",
  "desc_rip_church_gc_pa_country_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_14": "ro pa local 14",
  "desc_rip_church_ro_pa_local_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_14": "gc east pa local 14",
  "desc_rip_church_gc_east_pa_local_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_14": "gc middle pa local 14",
  "desc_rip_church_gc_middle_pa_local_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_14": "gc rome pa local 14",
  "desc_rip_church_gc_rome_pa_local_14": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_15": "ro pa country 15",
  "desc_rip_church_ro_pa_country_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_15": "gc pa country 15",
  "desc_rip_church_gc_pa_country_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_15": "ro pa local 15",
  "desc_rip_church_ro_pa_local_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_15": "gc east pa local 15",
  "desc_rip_church_gc_east_pa_local_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_15": "gc middle pa local 15",
  "desc_rip_church_gc_middle_pa_local_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_15": "gc rome pa local 15",
  "desc_rip_church_gc_rome_pa_local_15": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_16": "ro pa country 16",
  "desc_rip_church_ro_pa_country_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_16": "gc pa country 16",
  "desc_rip_church_gc_pa_country_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_16": "ro pa local 16",
  "desc_rip_church_ro_pa_local_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_16": "gc east pa local 16",
  "desc_rip_church_gc_east_pa_local_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_16": "gc middle pa local 16",
  "desc_rip_church_gc_middle_pa_local_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_16": "gc rome pa local 16",
  "desc_rip_church_gc_rome_pa_local_16": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_17": "ro pa country 17",
  "desc_rip_church_ro_pa_country_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_17": "gc pa country 17",
  "desc_rip_church_gc_pa_country_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_17": "ro pa local 17",
  "desc_rip_church_ro_pa_local_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_17": "gc east pa local 17",
  "desc_rip_church_gc_east_pa_local_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_17": "gc middle pa local 17",
  "desc_rip_church_gc_middle_pa_local_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_17": "gc rome pa local 17",
  "desc_rip_church_gc_rome_pa_local_17": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_18": "ro pa country 18",
  "desc_rip_church_ro_pa_country_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_18": "gc pa country 18",
  "desc_rip_church_gc_pa_country_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_18": "ro pa local 18",
  "desc_rip_church_ro_pa_local_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_18": "gc east pa local 18",
  "desc_rip_church_gc_east_pa_local_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_18": "gc middle pa local 18",
  "desc_rip_church_gc_middle_pa_local_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_18": "gc rome pa local 18",
  "desc_rip_church_gc_rome_pa_local_18": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_19": "ro pa country 19",
  "desc_rip_church_ro_pa_country_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_19": "gc pa country 19",
  "desc_rip_church_gc_pa_country_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_19": "ro pa local 19",
  "desc_rip_church_ro_pa_local_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_19": "gc east pa local 19",
  "desc_rip_church_gc_east_pa_local_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_19": "gc middle pa local 19",
  "desc_rip_church_gc_middle_pa_local_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_19": "gc rome pa local 19",
  "desc_rip_church_gc_rome_pa_local_19": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_country_20": "ro pa country 20",
  "desc_rip_church_ro_pa_country_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_pa_country_20": "gc pa country 20",
  "desc_rip_church_gc_pa_country_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_ro_pa_local_20": "ro pa local 20",
  "desc_rip_church_ro_pa_local_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_east_pa_local_20": "gc east pa local 20",
  "desc_rip_church_gc_east_pa_local_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_middle_pa_local_20": "gc middle pa local 20",
  "desc_rip_church_gc_middle_pa_local_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_gc_rome_pa_local_20": "gc rome pa local 20",
  "desc_rip_church_gc_rome_pa_local_20": "An adjustment belonging to the current church settlement; its effects end or change when its conditions cease to apply.",
  "rip_church_opinion_ro_recognized": "ro recognized",
  "rip_church_opinion_ro_unrecognized": "ro unrecognized",
  "rip_church_opinion_ro_schism": "ro schism",
  "rip_church_opinion_gc_catholic_east": "gc catholic east",
  "rip_church_opinion_gc_catholic_middle": "gc catholic middle",
  "rip_church_opinion_gc_catholic_rome": "gc catholic rome",
  "rip_church_opinion_gc_orthodox_east": "gc orthodox east",
  "rip_church_opinion_gc_orthodox_middle": "gc orthodox middle",
  "rip_church_opinion_gc_orthodox_rome": "gc orthodox rome",
  "rip_church_opinion_gc_ecumenical": "gc ecumenical",
  "rip_church_opinion_gc_ro_schism": "gc ro schism",
  "rip_church_opinion_propagation_conflict": "propagation conflict"
}

DATA.update({
    'rip_church_gui_status_title': 'STATUS',
    'rip_church_gui_status_title_tt': 'Status of the Union hierarchy.',
    'rip_church_gui_parishes_title': 'COMMUNITY RIGHTS',
    'rip_church_gui_parishes_title_tt': COMMUNITIES_TT,
    'rip_church_gui_parish_counts':
        'Eastern communities: §Y[Root.rip_church_gui_eastern_parishes.GetValue]§!\\nLatin communities: §Y[Root.rip_church_gui_latin_parishes.GetValue]§!',
    'rip_church_gui_parish_counts_tt':
        'Counts only our provinces and refreshes monthly. This province-level count is a gameplay abstraction, not an exact historical parish or canonical status, and not evidence of voluntary Union acceptance. Guaranteeing rights preserves the province religion; it is not converted and does not enter the Union. Select an owned province to guarantee or revoke its rights.',
    'rip_church_gui_manage_parishes': 'Manage community rights',
    'rip_church_gui_manage_parishes_tt':
        'Open the register of guaranteed community rights. Select an owned province to guarantee or revoke its rights.',
    'rip_church_gui_institutions_title': 'SYNOD',
    'rip_church_gui_active_institution': 'Institution: §H[Root.GetChurchPrivilege]§!',
    'rip_church_gui_policy_help':
        'Church policy · Ecumenism is locked until every requirement in its tooltip is met.',
    'rip_church_gui_policy_help_tt':
        'Local Synod opens the institution choices.\\n'+ECUMENISM_TT,
    'rip_church_gui_parish_list_title': 'COMMUNITY RIGHTS',
    'rip_church_gui_parish_list_title_tt': COMMUNITIES_TT,
    'rip_church_gui_parish_empty_state': '[Root.GetChurchParishRegisterState]',
    'rip_church_gui_parish_empty_state_tt':
        'Community rights are guaranteed and revoked from the selected province panel. The summary above updates monthly.',
    'rip_church_gui_parish_register_empty':
        '§HNo community rights are guaranteed.§!\\n\\nThis province-level gameplay abstraction does not establish exact canonical status or indicate voluntary acceptance of the Union. A guarantee protects community rights without converting the province or bringing it into the Union.\\n\\nProvince · Faith · Status',
    'rip_church_gui_parish_register_active':
        '§HEastern communities§!\\nProvince · Faith · Rights\\n\\n§HLatin communities§!\\nProvince · Faith · Rights\\n\\nSelect an owned province with guaranteed rights to inspect or revoke its guarantee.',
    'rip_church_gui_parish_register_active_tt':
        'Province-level gameplay groupings, not exact canonical parish statuses and not evidence of voluntary Union acceptance.\\n\\n§HEastern communities§!\\nProvince · Faith · Rights\\n\\n§HLatin communities§!\\nProvince · Faith · Rights\\n\\nSelect an owned province with guaranteed rights to inspect or revoke its guarantee.',
    'rip_church_gui_recognize_parish': 'Guarantee community rights',
    'rip_church_gui_recognize_parish_tt':
        'Select an owned Orthodox, Muscovite Orthodox or Catholic province, then use Guarantee community rights in its province panel. '+RITE_MODEL+' '+RITE_KEEPS+' '+RITE_TERMS,
    'rip_church_gui_recognize_help': 'Requires an eligible owned province to be selected.',
    'rip_church_gui_recognize_help_tt': 'Community rights are guaranteed from the selected province panel.',
    'rip_church_gc_curia_heading': 'CURIA RELATIONS',
    'rip_church_gc_contact_title': 'PAPAL CONTACT',
    'rip_church_gc_contact_title_tt': 'A limited diplomatic audience with the Holy See.',
    'rip_church_gc_deputation_button': 'Send diplomatic mission — 50¤',
    'rip_church_gc_holy_see_gift_button': 'Send a gift to Rome — 100¤',
    'rip_church_gc_holy_see_gift_button_tt':
        'Send 100 ducats to the Holy See. The Papal State gains +25 opinion of us, decaying by 5 per year. Available once every five years. Requires the Catholic Papal State, peace and 100 ducats. This is diplomatic goodwill only: no Patriarch Authority, Curia vote, cardinal or electoral influence is gained.',
    'rip_church_gc_holy_see_gift_summary':
        'Gift: §Y100 ducats§! · §G+25 Papal opinion§! · once every five years',
    'rip_church_gc_icons_title': 'DEVOTIONAL ICON',
    'rip_church_gc_icon_liturgy_state': 'Liturgy\\n§G+1 yearly prestige; +1 diplomatic reputation; +20% improve relations§!',
    'rip_church_gc_icon_learning_state': 'Learning\\n§G-5% development cost; -5% technology cost§!',
    'rip_church_gc_icon_charity_state': 'Almsgiving\\n§G-1 national unrest; -10% stability cost§!',
 'rip_church_gc_native_privileges_button': 'Manage',
 'rip_church_gc_native_privileges_button_tt': 'Open church privileges. Opening this menu is free; only choosing a privilege spends resources.',
 'rip_church_ro_heading': 'The Muscovite Church',
 'rip_church_ro_policies_title': 'Church policies',
 'rip_church_ro_policies_title_tt': 'Use the button below an icon to activate or deactivate its policy. Active icons have a lit frame. Hover each button for its effects and payment conditions.',
 'rip_church_icon_war_button': 'Military',
 'rip_church_icon_mercy_button': 'Mercy',
 'rip_church_icon_building_button': 'Building',
 'rip_church_icon_mission_button': 'Mission',
 'rip_church_ro_status': '[Root.GetChurchROStatus]',
 'rip_church_ro_resources': 'Fervor: [Root.rip_church_fervor.GetValue] / 100   Icons: [Root.rip_church_icons.GetValue] / [Root.rip_church_capacity.GetValue]\\nMonthly Fervor: +[Root.rip_church_fervor_income.GetValue] / -[Root.rip_church_fervor_cost.GetValue]\\nFunded trade nodes: [Root.rip_church_nodes.GetValue]',
 'rip_church_ro_mission_cost': 'Each trade node: 2 Fervor now + 2 per month\\nRequires an active Apostolic Mission',
 'rip_church_nodes_button': 'Fund / close trade missions',
 'rip_church_nodes_button_tt': 'Requires a funded node to manage, or an eligible node you can afford. Each node costs 2 Fervor immediately and 2 each month, in addition to icon upkeep. No ducat fee. Opening the menu itself makes no payment. Activate Apostolic Mission first; a new node requires at least 12 Fervor, a merchant, 50% trade power, connected church infrastructure and an eligible target.',
 'rip_church_mission_network_desc': 'Muscovite Orthodox missionary network. A registered node costs 2 Fervor now and 2 per month, in addition to Apostolic Mission upkeep. No ducat fee. Requires a merchant, 50% trade power and connected controlled church infrastructure. Fund or close nodes from the church panel.',
 'rip_church_break_communion_title': 'Renounce the patriarchal settlement',
 'rip_church_break_communion_desc': 'Deliberate alternative history: abandon recognized communion and claim an independent universal church. This enables a second funded mission node, increases confessional conflict and imposes -1 diplomatic reputation. Earlier reconciliation payments are not refunded.',
 'rip_church_oppose_union_title': 'Change our policy toward the Union',
 'rip_church_oppose_union_desc': 'For 25 DIP, adopt or end state opposition to the Union. Opposition multiplies its conversion target weights in our provinces by 0.25 and adds a mutual -10 opinion with Greek Catholic countries. The policy can be changed once every five years.',
 'rip_church_withdraw_union_support_title': 'Withdraw royal support for the Union',
 'rip_church_withdraw_union_support_desc': 'End the Catholic crown\'s patronage. Any Centre of Union under our rule loses its eligible patron and ceases to operate. Earlier foundation and negotiation payments are not refunded.',
 'rip_church_opinion_union_opposition': 'State opposition to the Union',
 'rip_church_center_active': 'Our Centre of Union is active',
 'rip_church_center_suspended': 'Our Centre is suspended by occupation',
 'rip_church_center_elsewhere': 'The single Centre is held by another country',
 'rip_church_center_absent': '§RNo Centre of Union is established§!',
 'rip_church_icon_no_fuel': 'Blocked: at least 10 Fervor is required.',
 'rip_church_icon_no_slot': 'Blocked: authority currently provides no vacant icon slot.',
 'rip_church_icon_cooldown': 'Blocked: one year must pass after the previous activation of this icon.',
 'rip_church_icon_can_activate': 'Ready to activate.',
 'rip_church_icon_can_deactivate': 'Active: click to deactivate without a refund.',
 'rip_church_ro_high': 'Centralized church administration',
 'rip_church_ro_max': 'Intensive church centralization',
 'rip_church_ro_high_recognized': 'Recognized central administration',
 'rip_church_ro_max_recognized': 'Recognized intensive centralization',
 'rip_church_ro_schism': 'Universal claims in schism',
 'rip_church_reconciliation_unrest': 'Opposition to reconciliation',
 'rip_church_gc_infrastructure': 'Eastern church infrastructure',
 'rip_church_gc_coexistence': 'Agreement on coexistence',
 'rip_church_gc_legate': 'Papal legate',
 'rip_church_gc_dynastic': 'Papal support for legitimacy',
 'rip_church_gc_prestige': 'Papal recognition of standing',
 'rip_church_rite': 'Guaranteed community rights',
 'rip_church_rite_favoured': 'Protected local tradition',
 'rip_church_rite_ecumenical': 'Ecumenical accommodation',
 'rip_church_rite_revoked': 'Revoked community rights',
 'rip_church_gc_roman_resistance': 'Resistance to Roman integration',
 'rip_church_conversion_resistance': 'Resistance to jurisdictional pressure',
 'rip_church_gc_local_see': 'Local Eastern Catholic see',
 'rip_church_conversion_pressure': 'Recent missionary pressure',
 'rip_church_opinion_ro_recognized': 'Recognized Orthodox communion',
 'rip_church_opinion_ro_unrecognized': 'Shared faith, disputed jurisdiction',
 'rip_church_opinion_ro_schism': 'Rival universal claims',
 'rip_church_opinion_gc_catholic_east': 'Communion with Eastern autonomy',
 'rip_church_opinion_gc_catholic_middle': 'Balanced communion with Rome',
 'rip_church_opinion_gc_catholic_rome': 'Close Roman communion',
 'rip_church_opinion_gc_orthodox_east': 'Respect for Eastern tradition',
 'rip_church_opinion_gc_orthodox_middle': 'Balanced confessional relations',
 'rip_church_opinion_gc_orthodox_rome': 'Rivalry over Roman integration',
 'rip_church_opinion_gc_ecumenical': 'Ecumenical settlement',
 'rip_church_opinion_gc_ro_schism': 'Conflicting ecclesiastical claims',
 'rip_church_opinion_propagation_conflict': 'Missionary intervention in our parishes',
})
for key in ('heading','status','resources','mission_cost'):
 DATA['rip_church_ro_'+key+'_tt']=DATA['rip_church_ro_'+key]
for icon in ('war','mercy','building','mission'):
    DATA['rip_church_icon_'+icon]=DATA['rip_church_icon_'+icon+'_button']
    DATA['desc_rip_church_icon_'+icon]=DATA['rip_church_icon_'+icon+'_button_tt']
    DATA['rip_church_icon_'+icon+'_button_tt']+='\\n[Root.GetChurchIcon'+icon.title()+'Access]'
DATA.update({
 'rip_church_gc_heading': 'Union of the Churches',
 'rip_church_gc_orientation': '[Root.GetChurchGCOrientation]',
 'rip_church_gc_resources': 'Communion balance: [Root.GetChurchBalanceValue]\\nPapal Standing: §Y[Root.rip_church_papal_standing.GetValue] / 100§!\\nMonthly rate: [Root.GetChurchStandingRate]',
 'rip_church_gc_parishes': 'Communities with guaranteed rights: §Y[Root.rip_church_recognized_parishes.GetValue]§!',
 'rip_church_gc_parish_count': '§Y[Root.rip_church_recognized_parishes.GetValue]§!',
 'rip_church_gc_parish_count_tt': 'Communities with guaranteed rights: [Root.rip_church_recognized_parishes.GetValue]',
 'rip_church_gc_balance_negative': '§R[Root.rip_church_communion.GetValue]§!',
 'rip_church_gc_balance_positive': '§Y[Root.rip_church_communion.GetValue]§!',
 'rip_church_gc_center_state': '[Root.GetChurchCenterStatus]',
 'rip_church_gc_policy_label': 'Communion policy',
 'rip_church_gc_policy_cost': '§Y25§!   |   §Y20§! balance',
 'rip_church_gc_privilege_state': 'Active privilege\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gc_help': 'Start with Privileges. Community rights: select an owned province.\\nHover buttons for costs and conditions.',
 'rip_church_privileges_button': 'Privileges',
 'rip_church_center_button': 'Union seat',
 'rip_church_ecumenism_button': 'Ecumenism',
 'rip_church_standing_rate_zero': '§Y+0.00§!',
 'rip_church_standing_rate_east': '§G+0.10§!',
 'rip_church_standing_rate_middle': '§G+0.25§!',
 'rip_church_standing_rate_rome': '§G+0.50§!',
})
DATA.update({
 'rip_church_privileges_button': 'Synod',
 'rip_church_privileges_button_tt': 'Convene the local Greek Catholic synod. Choose Eastern infrastructure or a compact of coexistence, which needs guaranteed community rights in at least one province. These use Patriarch Authority and ducats, and occupy a separate local ten-year slot. One Curia petition may run at the same time. Opening the menu is free.\\nCurrent institution: [Root.GetChurchLocalInstitution]',
 'rip_church_gc_native_privileges_button': 'Synod',
 'rip_church_gc_native_privileges_button_tt': 'Choose an institution of the Greek Catholic hierarchy. The picture shows the active local institution; these are not Orthodox icon bonuses. Opening the synod is free.\\nCurrent institution: [Root.GetChurchLocalInstitution]',
 'rip_church.6.t': 'The Local Synod',
 'rip_church.6.d': 'Our Eastern hierarchy can organize church infrastructure or agree protections for the rites of its parishes. These local institutions spend Patriarch Authority and ducats and share a separate ten-year synod slot. One bounded Curia petition may operate at the same time; only one Curia petition can be active.\\n\\nCurrent local institution: [Root.GetChurchLocalInstitution]\\nPapal petitions are available in the Curia tab of the church panel.',
 'rip_church_gc_curia_heading': 'The Holy See and the Union',
 'rip_church_gc_curia_status': '[Root.GetChurchCuriaStatus]',
 'rip_church_gc_curia_good': 'In communion with Rome',
 'rip_church_gc_curia_cold': 'Roman support requires better relations',
 'rip_church_gc_curia_war': 'At war with the Papal State',
 'rip_church_gc_curia_absent': 'The Catholic Papal State is absent',
 'rip_church_gc_rome_resources': 'Papal opinion: [Root.GetChurchPapalOpinion]\\nStanding: §Y[Root.rip_church_papal_standing.GetValue] / 100§!\\nMonthly growth: [Root.GetChurchCuriaRate]',
 'rip_church_gc_opinion_value': '§Y[Root.rip_church_papal_opinion.GetValue]§!',
 'rip_church_gc_opinion_negative': '§R[Root.rip_church_papal_opinion.GetValue]§!',
 'rip_church_gc_opinion_absent': 'Unavailable',
 'rip_church_gc_rate_paused': 'Paused',
 'rip_church_gc_controller_label': 'Controller',
 'rip_church_gc_controller_name': '[rip_church_gc_controller.GetName]',
 'rip_church_gc_controller_none': 'No current controller',
 'rip_church_gc_pope_shield_tt': 'The Catholic Papal State. Click to open its country view. Opinion of us: [Root.GetChurchPapalOpinion]. The displayed opinion refreshes monthly and when opening the Curia tab; petition conditions always use current relations.',
 'rip_church_gc_controller_shield_tt': 'Curia controller for the current pontificate: [Root.GetChurchCuriaController]. This country won the last election; this is not a prediction of the next election. Click to open its country view.',
 'rip_church_gc_petitions_title': 'Papal petitions',
 'rip_church_gc_curia_privilege': 'Active church privilege\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gc_donate_label': 'Donate',
 'rip_church_gc_donate_button_tt': 'Donate 100 ducats: gain 10 Papal Standing and +25 Papal opinion, decaying by 5 per year. Once every five years, including after a change of religion. Requires the Catholic Papal State, peace with it and at most 90 Standing. With Emperor, 50 ducats reach the Curia Treasury and 50 the Papal State; otherwise all 100 go to the Papal State. This grants no vote or invested papal influence.',
 'rip_church_gc_donation_cost': 'Donation to the Holy See\\n§Y100 ducats§!\\n§G+10 Standing§!; §G+25 Papal opinion§!',
 'rip_church_gc_donation_state': '[Root.GetChurchDonationState]',
 'rip_church_gc_donation_ready': 'Donation available',
 'rip_church_gc_donation_wait': 'Wait five years after the last donation',
 'rip_church_gc_donation_blocked': 'Donation requirements are not met',
 'rip_church_gc_donation_opinion': 'Donation from an Eastern Catholic church',
 'rip_church_opinion_gc_deputation': 'Audience by an Eastern Catholic deputation',
 'rip_church_opinion_gc_donation': 'Donation from an Eastern Catholic church',
 'rip_church_gc_local_reserved': 'A local synod institution is already active',
 'rip_church_gc_church_tax': 'Papal licence for church revenues',
 'desc_rip_church_gc_church_tax': 'A ten-year curial privilege: +10% national tax and -5% building cost.',
 'rip_church_gc_blessing': 'Papal blessing of the Union',
 'desc_rip_church_gc_blessing': 'A ten-year curial privilege: +1 yearly prestige and +5% army morale.',
 'rip_church_gc_usury': 'Curial settlement of debts',
 'desc_rip_church_gc_usury': 'A ten-year curial privilege: -0.25 interest, +0.05 yearly inflation reduction and -0.02 yearly corruption.',
 'rip_church_gc_holy_war': 'Papal support for the war effort',
 'desc_rip_church_gc_holy_war': 'A ten-year curial privilege: +7.5% manpower recovery and -2.5% land maintenance.',
 'rip_church_gc_saint': 'Recognition of a local saint',
 'desc_rip_church_gc_saint': 'The petition granted +1 stability immediately. It reserves the Curia petition slot for ten years and gives no additional ongoing bonus.',
 'rip_church_gc_monopoly': 'Papal commercial charter',
 'desc_rip_church_gc_monopoly': 'The petition granted +1 mercantilism immediately. It reserves the Curia petition slot for ten years and gives no additional ongoing bonus.',
})
for page in ('union','curia'):
 for tab in ('union','curia'):
  key=f'rip_church_gc_{tab}_tab_{page}'
  DATA[key]=tab.title()
for key in list(DATA):
    match=re.fullmatch(r'rip_church_(ro|gc)(?:_(east|middle|rome))?_pa_(country|local)_(\d+)',key)
    if match:
        DATA[key]='Church authority adjustment: '+str(int(match[4])*5)+'%'
        DATA['desc_'+key]='Offsets the inherited Orthodox authority bonus for this confession. Recalculated in five-point authority bands; the native Orthodox faith is unchanged.'

DATA.update({
 'rip_church_gc_course_range':'East -100     |     Balanced -40 ... +40     |     Rome +100',
 'rip_church_gc_course_range_tt':'The current orientation controls access to local and Roman privileges. Monthly Standing is +0.10 / +0.25 / +0.50 only while a Catholic PAP exists, is at peace with us and has at least +50 opinion of us.',
 'rip_church_gc_privilege_state':'[Root.GetChurchSlotState]\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gc_curia_privilege':'[Root.GetChurchSlotState]\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gui_parishes_heading':'Community rights',
 'rip_church_gui_coexistence':'[Root.GetChurchCoexistenceState]',
 'rip_church_gui_coexistence_active':'§GCompact of coexistence active§!',
 'rip_church_gui_coexistence_ecumenical':'§GEcumenical settlement concluded§!',
 'rip_church_gui_coexistence_local':'Community rights stay guaranteed province by province',
 'rip_church_gui_parish_counts':'Eastern communities: §Y[Root.rip_church_gui_eastern_parishes.GetValue]§!\\nLatin communities: §Y[Root.rip_church_gui_latin_parishes.GetValue]§!',
 'rip_church_gui_parish_counts_tt':'Counts only our provinces; refreshed on opening this tab and monthly. This province-level count is a gameplay abstraction, not an exact historical parish or canonical status, and not evidence of voluntary Union acceptance. Guaranteeing community rights preserves the province religion; it is not converted and does not enter the Union. Select an owned province to guarantee or revoke its rights.',
 'rip_church_gui_network_title':'One shared Centre of Union',
 'rip_church_gui_network_scope':'[Root.GetChurchNetworkScope]',
 'rip_church_gui_network_normal':'Network access: §Yrings 0-2§!\\nLatin consent: §Yring 0 only§!',
 'rip_church_gui_network_extended':'Network access: §Yrings 0-4§!\\nLatin consent: §Yextended network§!',
 'rip_church_gui_network_none':'No active network\\nEstablish or restore the shared Union seat',
 'rip_church_gui_network_scope_tt':'Rings are connected areas, bridged by existing Greek Catholic parishes. The native centre also checks its 150 distance limit. Nearby Eastern targets have higher weights; Latin targets need explicit consent and have lower base priority. Recognized rites are excluded. Occupation suspends the centre while retaining the one world slot.',
 'rip_church_gui_found_center':'Establish Union seat',
 'rip_church_gui_found_center_tt':'Pay §Y100 ADM and one year of income§! to establish the sole Centre of Union. Requires peace, stability +1, an eligible controlled Greek Catholic core with development 10 and a temple or cathedral. An occupied centre still reserves the world slot. Founding cooldown: twenty years.',
 'rip_church_gui_slot_state':'[Root.GetChurchSlotState]',
 'rip_church_gui_slot_free':'Shared privilege: §G0 / 1§!',
 'rip_church_gui_slot_used':'Shared privilege: §Y1 / 1§!',
 'rip_church_gui_slot_patron':'Catholic patron: local GC slot unavailable',
 'rip_church_gui_slot_state_tt':'Eastern infrastructure and coexistence share one ten-year local synod slot. One Curia petition may operate at the same time, but Curia petitions share their own ten-year slot. A saint or trade charter gives an immediate reward but reserves the Curia slot. Opening menus never pays for an institution or petition.',
 'rip_church_gui_active_institution':'Active institution\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gui_synod':'Local synod',
 'rip_church_gui_ecumenism':'Ecumenism',
 'rip_church_gui_paths_heading':'Paths to the Union',
 'rip_church_gui_path_status':'[Root.GetChurchUnionPathState]',
 'rip_church_gui_path_orthodox':'Orthodox acceptance of the Union — regional alternative',
 'rip_church_gui_path_catholic':'Catholic patronage of Eastern provinces',
 'rip_church_gui_path_patron':'§GCatholic patron of the Union§!',
 'rip_church_gui_path_identity':'[Root.GetChurchUnionPathIdentity]',
 'rip_church_gui_identity_orthodox':'State acceptance changes our confession.\\nExisting communities need separate guarantees of their rights.',
 'rip_church_gui_identity_catholic':'Patronage preserves our Catholic confession.\\nThe state action changes one Eastern province\'s faith to Greek Catholic.',
 'rip_church_gui_paths_title':'Negotiations and settlement',
 'rip_church_gui_florence':'Florentine precedent',
 'rip_church_gui_florence_tt':'Invoke an alternative settlement drawing on the Florentine precedent of 1439, not the founding of the UGCC. Separate from the Brest route of 1596. Begin in 1444-1501: §Y200 ADM, 100 DIP and one year of income§!. Requires peace, stability +2, PAP opinion +100 and an eligible Orthodox core province. After five years, peace, stability and relations are checked again. Orthodox acceptance changes state faith; Catholic completion grants patronage and changes one eligible province to Greek Catholic. This is a campaign-created alternative, not a claim of an institution founded in 1439. One attempt.',
 'rip_church_gui_adopt':'Accept the Union',
 'rip_church_gui_adopt_tt':'Conclude the later Orthodox state route from 1596 — a regional alternative — paying §Y100 ADM and 100 DIP§!. Uses exactly the current national decision gates: regional state, enabled faith, peace, stability, Catholic contact or union pressure, and qualifying Orthodox provinces. Catholic countries cannot use this action.',
 'rip_church_gui_sponsor':'Sponsor the Union',
 'rip_church_gui_sponsor_tt':'From 1596, pay §Y100 ADM, 100 DIP and one year of income§! to support the Union while remaining Catholic. Requires peace, stability +1, PAP without war, and a qualifying Orthodox core province. This state action changes one eligible province\'s religion to Greek Catholic; it is separate from a community-rights guarantee and does not report local consent.',
 'rip_church_gui_path_progress':'[Root.GetChurchFlorenceProgress]',
 'rip_church_gui_florence_wait':'Florentine precedent: five-year negotiations',
 'rip_church_gui_florence_due':'Term complete: settlement conditions must hold',
 'rip_church_gui_florence_done':'§GFlorentine precedent carried forward§!',
 'rip_church_gui_florence_none':'No Florentine-precedent negotiations in progress',
 'rip_church_gui_patron_network':'Parishes and Union seat',
 'rip_church_gui_patron_network_tt':'Open the parish and centre panel. Catholic patrons can establish the centre and grant Latin consent; the Greek Catholic synod and petitions require that state confession.',
 'rip_church_gui_province_network':'Rite: [Root.GetChurchRiteFamily]\\nNetwork: [Root.GetChurchProvinceRing]\\n[Root.GetChurchProvinceUnionAccess]',
 'rip_church_gui_rite_eastern':'Eastern', 'rip_church_gui_rite_latin':'Latin',
 'rip_church_gui_ring_outside':'outside the connected rings',
 'rip_church_gui_protected':'§GCommunity rights guaranteed: spared Union backlash§!',
 'rip_church_gui_access_yes':'Network permits conversion; native range applies',
 'rip_church_gui_access_no':'§YUnion conversion conditions are not met§!',
 'rip_church_gui_province_network_tt':'Recognition keeps the local confession. Latin consent permits gradual conversion and is not recognition. Rings describe the game network, not historical jurisdiction. Native distance and conversion rules still apply. Refreshes with monthly network maintenance.',
})
DATA['rip_church_center_button_tt']='§YCentre and parishes§!\\nOpen the network panel, review recognized rites and Latin consent, or establish the sole Centre of Union.'
DATA['rip_church_gui_synod_tt']=DATA['rip_church_privileges_button_tt']
DATA['rip_church_gui_ecumenism_tt']=ECUMENISM_TT
for i in range(5): DATA['rip_church_gui_ring_'+str(i)]='ring '+str(i)
# The button is named rip_church_gc_{tab}_tab_{page}, so its label and tooltip depend on the tab alone
# (tests/check_gc_curia_window.py pins that naming). The third tab lists communities whose rights are guaranteed.
TAB_LABEL={'union':'Union','curia':'Curia','parishes':'Communities'}
TAB_TT={
 'union':'The Union of the Churches: status, local synod, ecumenism and devotional icons. Orthodox and Catholic states see their historical paths to the Union here.',
 'curia':'Rome as a diplomatic contact; no numerical standing or electoral rights.',
 'parishes':COMMUNITIES_TT}
for page in ('union','curia','parishes'):
 for tab in ('union','curia','parishes'):
  key=f'rip_church_gc_{tab}_tab_{page}'
  DATA[key]=TAB_LABEL[tab]
  DATA[key+'_tt']=TAB_TT[tab]
for key in list(DATA):
 if key.startswith('rip_church_gui_') and not key.endswith('_tt'): DATA.setdefault(key+'_tt',DATA[key])
for key in ('rip_church_gc_privilege_state_tt','rip_church_gc_curia_privilege_tt'): DATA[key]=DATA['rip_church_gui_slot_state_tt']

DATA.update({
 'rip_church.6.d':'The Eastern hierarchy may organize church infrastructure or conclude a compact of coexistence, which needs community rights guaranteed in at least one province. Both are local synodal institutions, spend Patriarch Authority and ducats, and share one ten-year synod slot.',
 'rip_church_gc_heading':'THE UNION OF THE CHURCHES',
 'rip_church_gc_resources':'Eastern hierarchy in communion with Rome\\nCommunity rights are guaranteed province by province',
 'rip_church_gc_resources_tt':'The main religion window shows Patriarch Authority. Guaranteed community rights are tracked separately for each province.',
 'rip_church_gui_parishes_title':'Community rights',
 'rip_church_gui_parish_counts':'Eastern communities: §Y[Root.rip_church_gui_eastern_parishes.GetValue]§!\\nLatin communities: §Y[Root.rip_church_gui_latin_parishes.GetValue]§!',
 'rip_church_gui_parish_counts_tt':'Counts only our provinces and refreshes monthly. This province-level count is a gameplay abstraction, not an exact historical parish or canonical status, and not evidence of voluntary Union acceptance. Guaranteeing community rights preserves the province religion; it is not converted and does not enter the Union. Select an owned province to guarantee or revoke its rights.',
 'rip_church_gui_institutions_title':'Local synodal institutions',
 'rip_church_gui_slot_state':'[Root.GetChurchSlotState]',
 'rip_church_gui_slot_free':'Synodal institution: §G0 / 1§!',
 'rip_church_gui_slot_used':'Synodal institution: §Y1 / 1§!',
 'rip_church_gui_slot_state_tt':'Infrastructure and coexistence share one ten-year local synod slot. One Curia petition can coexist, with its own one-at-a-time ten-year slot. Opening the synod is free.',
 'rip_church_gui_active_institution':'Active institution\\n§H[Root.GetChurchPrivilege]§!',
 'rip_church_gui_synod':'Local synod',
 'rip_church_gui_synod_tt':'Choose Eastern infrastructure, or a compact of coexistence once community rights are guaranteed in at least one province. These use Patriarch Authority and ducats and last ten years.',
 'rip_church_gui_ecumenism':'Ecumenism',
 'rip_church_gui_ecumenism_tt':ECUMENISM_TT,
 'rip_church_gui_local_note':'No automatic centre converts neighbouring provinces.',
 'rip_church_gui_patron_state':'[Root.GetChurchPatronState]',
 'rip_church_gui_patron_active':'§GCatholic patronage is established§!\\nThe state remains Catholic; parish changes require explicit events or decisions.',
 'rip_church_gui_patron_inactive':'Patronage has not been established',
 'rip_church_gui_sponsor_tt':'From 1596, pay §Y100 ADM, 100 DIP and one year of income§! to support the Union while remaining Catholic. Requires peace, stability +1, PAP without war, and a qualifying Orthodox core parish. One eligible parish becomes Greek Catholic.',
 'rip_church_gc_curia_heading':'The Holy See and the Union',
 'rip_church_gc_curia_status':'[Root.GetChurchCuriaStatus]',
 'rip_church_gc_curia_good':'In communion with Rome',
 'rip_church_gc_curia_cold':'Roman support requires better relations',
 'rip_church_gc_curia_war':'At war with the Papal State',
 'rip_church_gc_curia_absent':'The Catholic Papal State is absent',
 'rip_church_gc_rome_resources':'Papal opinion: [Root.GetChurchPapalOpinion]\\nStanding: §Y[Root.rip_church_papal_standing.GetValue] / 100§!\\nMonthly growth: [Root.GetChurchCuriaRate]',
 'rip_church_gc_opinion_value':'§Y[Root.rip_church_papal_opinion.GetValue]§!',
 'rip_church_gc_opinion_negative':'§R[Root.rip_church_papal_opinion.GetValue]§!',
 'rip_church_gc_opinion_absent':'Unavailable',
 'rip_church_gc_rate_paused':'Paused',
 'rip_church_gc_controller_label':'Current Curia controller',
 'rip_church_gc_controller_name':'[rip_church_gc_controller.GetName]',
 'rip_church_gc_controller_none':'No current controller',
 'rip_church_gc_petitions_title':'Papal petitions',
 'rip_church_gc_curia_privilege':'Active Curia petition\\n§H[Root.GetChurchCuriaPrivilege]§!',
 'rip_church_gc_donate_button_tt':'Donate §Y100 ducats§! for §G+10 Papal Standing§! and +25 Papal opinion, decaying by 5 per year. Once every five years; requires a Catholic Papal State at peace with us and at most 90 Standing. With Emperor, half enters the Curia Treasury and half the Papal State; otherwise all 100 ducats go to the Papal State. This grants no vote or invested papal influence.',
 'rip_church_gc_donation_cost':'§Y100 ducats§!\\n§G+10 Standing§!\\n§G+25 Papal opinion§!',
 'rip_church_gc_deputation_button':'Eastern deputation',
 'rip_church_gc_deputation_button_tt':'Send a diplomatic audience request to the Holy See. Costs §Y50 ducats§! and grants +25 opinion in both directions, decaying by 2 per year. Once every five years; no electoral rights or resource are gained.',
 'rip_church_gc_deputation_note':'§Y50¤ / 10 PA§!\\nFive-year interval; no vote',
 'rip_church_gc_icons_title':'Eastern devotional icons',
 'rip_church_gc_icon_liturgy':'Icon of the Divine Liturgy',
 'desc_rip_church_gc_icon_liturgy':'The Divine Liturgy in the Eastern rite, celebrated in communion with Rome: '+'+1 yearly prestige, +1 diplomatic reputation and +20% improve relations.',
 'rip_church_gc_icon_learning':'Icon of Eastern Learning',
 'desc_rip_church_gc_icon_learning':'Schools, scribes and printing in the Eastern tradition: -5% development cost and -5% technology cost.',
 'rip_church_gc_icon_charity':'Icon of Almsgiving',
 'desc_rip_church_gc_icon_charity':'Brotherhood alms and hospitals keep the peace in the parishes: -1 national unrest and -10% stability cost.',
 'rip_church_gc_icons_note':'One icon at a time · §Y20 PA§! · five years',
 'rip_church_gc_icon_liturgy_button':'Liturgy',
 'rip_church_gc_icon_liturgy_button_tt':'Activate the icon of the Divine Liturgy for five years. Costs §Y20 Patriarch Authority§!. +1 yearly prestige, +1 diplomatic reputation and +20% improve relations. Only one Greek Catholic icon can be active.',
 'rip_church_gc_icon_liturgy_state':'Liturgy',
 'rip_church_gc_icon_learning_button':'Learning',
 'rip_church_gc_icon_learning_button_tt':'Activate the icon of Eastern learning for five years. Costs §Y20 Patriarch Authority§!. -5% development cost and -5% technology cost. Only one Greek Catholic icon can be active.',
 'rip_church_gc_icon_learning_state':'Learning',
 'rip_church_gc_icon_charity_button':'Almsgiving',
 'rip_church_gc_icon_charity_button_tt':'Activate the icon of almsgiving for five years. Costs §Y20 Patriarch Authority§!. -1 national unrest and -10% stability cost. Only one Greek Catholic icon can be active.',
 'rip_church_gc_icon_charity_state':'Almsgiving',
 'rip_church_gc_curia_vote_disclaimer':'Greek Catholic deputations and petitions do not confer cardinalship, electoral votes or control of the Catholic Curia.',
 'rip_church_rite_help':RITE_HELP,
 'rip_church_rite_help_tt':RITE_HELP_TT,
})
DATA['rip_church_gc_curia_privilege_tt']='One Curia petition at a time; it can coexist with one local synod institution. Both slots last ten years.'
DATA['rip_church_gc_curia_vote_disclaimer_tt']=DATA['rip_church_gc_curia_vote_disclaimer']
for key in ('icons_title','icons_note','deputation_note',
            'icon_liturgy_state','icon_learning_state','icon_charity_state'):
 DATA['rip_church_gc_'+key+'_tt']=DATA['rip_church_gc_'+key]
DATA['rip_church_gc_donate_button_tt']+='\\n[Root.GetChurchDonationState]'
DATA['rip_church_gc_donation_cost_tt']=DATA['rip_church_gc_donate_button_tt']
# Retired mechanics must not leave visible labels or scripted localization.
retired_fragments=(
 'communion','standing','curia','petition','donat','center','centre','network',
 'union_ring','latin_consent','course_range','policy_cost','policy_label',
 'east_button','rome_button','papal_support','legate','dynastic','gc_prestige',
 'church_tax','indulgence','usury','holy_war','controller_shield','pope_shield',
 'province_ring','province_union_access','patron_network')
retired_prefixes=(
 'rip_church_gc_balance_', 'rip_church_gc_rome_resources',
 'rip_church_gc_local_reserved', 'rip_church_gc_privilege_state',
 'rip_church_gui_parishes_heading', 'rip_church_union_seat',
 'rip_church_gc_middle', 'rip_church_gc_east', 'rip_church_gc_rome',
 'rip_church_ecumenism_button', 'rip_church_privileges_button')
live_curia_keys={
 'rip_church_gc_curia_heading','rip_church_gc_curia_heading_tt',
 'rip_church_gc_curia_status','rip_church_gc_curia_status_tt',
 'rip_church_gc_curia_good','rip_church_gc_curia_cold',
 'rip_church_gc_curia_war','rip_church_gc_curia_absent',
 'rip_church_gc_curia_privilege','rip_church_gc_curia_privilege_tt',
 'rip_church_gc_curia_vote_disclaimer','rip_church_gc_curia_vote_disclaimer_tt','rip_church_gc_petitions_title',
 'rip_church_gc_petitions_title_tt','rip_church_gc_rome_resources',
 'rip_church_gc_rome_resources_tt','rip_church_gc_opinion_value',
 'rip_church_gc_opinion_negative','rip_church_gc_opinion_absent',
 'rip_church_gc_rate_paused','rip_church_gc_donate_label',
 'rip_church_gc_donate_button_tt','rip_church_gc_donation_cost',
 'rip_church_gc_donation_cost_tt','rip_church_gc_donation_state',
 'rip_church_gc_donation_ready','rip_church_gc_donation_wait',
 'rip_church_gc_donation_blocked','rip_church_gc_controller_label',
 'rip_church_gc_controller_label_tt','rip_church_gc_controller_name',
 'rip_church_gc_controller_none','rip_church_gc_pope_shield_tt',
 'rip_church_gc_controller_shield_tt','rip_church_opinion_gc_donation',
}
def keep_live_curia_key(key):
 if key in live_curia_keys: return True
 if re.fullmatch(r'(?:desc_)?rip_church_gc_petition_(?:church_tax|blessing|indulgence|saint|usury|holy_war|legate|monopoly)(?:_(?:label|label_tt|button_tt))?',key):
  return True
 if re.fullmatch(r'rip_church_gc_(?:union|curia|parishes)_tab_(?:union|curia|parishes)(?:_tt)?',key):
  return True
 return False
for key in list(DATA):
 if (any(fragment in key.lower() for fragment in retired_fragments) or key.startswith(retired_prefixes)) and not keep_live_curia_key(key):
  del DATA[key]
for key in list(DATA):
 if key.startswith('rip_church_gui_') and not key.endswith('_tt'): DATA.setdefault(key+'_tt',DATA[key])

# The historical unions were signed by bishops under Catholic crowns and no crown changed its own
# faith. Where the adopter has no Catholic overlord the whole state takes the union, which is the
# mod's own departure from that record and is stated where the player acts.
STATE_UNION_ALT=('Alternative history when the state has no Catholic overlord: the historical unions were concluded by bishops '
 'living under Catholic crowns, and none of those crowns changed its own faith. Here the whole state takes the union.')
# Shared mechanics abstract several local church histories, not one jurisdiction.
REGIONAL_UNION_NOTE=('Shared rules model several local Ruthenian and Carpathian Eastern Catholic union traditions under a broad game category, not one church institution. '
 'Brest, Uzhhorod, Peremyshl, Lviv and Lutsk have distinct local histories, chronologies and jurisdictions; '
 'these rules do not imply that every region followed the same path or belonged to one institution.')
DATA.update({
 'convert_to_greek_catholic_decision_title':'Accept a local church union',
 'convert_to_greek_catholic_decision_desc':STATE_UNION_ALT+' Bring our local hierarchy into communion with Rome while retaining its Byzantine rite. '+REGIONAL_UNION_NOTE,
 'rip_church_gui_paths_title':'Local routes to communion',
 'rip_church_gui_paths_title_tt':REGIONAL_UNION_NOTE,
})
DATA['rip_church_gui_adopt_tt']+=' '+STATE_UNION_ALT
for key in ('rip_church_sponsor_union_desc','rip_church_gui_adopt_tt',
            'rip_church_gui_sponsor_tt'):
 DATA[key]+=' '+REGIONAL_UNION_NOTE
for key in ('rip_church_gui_parishes_title_tt','rip_church_gui_parish_list_title_tt','rip_church_rite_help_tt'):
 DATA[key]+=' Eastern and Latin are gameplay groupings, not historical diocesan boundaries. '+REGIONAL_UNION_NOTE
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
# Generated variable/modifier definitions may add display-only compensation IDs.
for p in sorted(q for q in (ROOT/'common/event_modifiers').glob('*.txt') if q.name.lower().startswith('rip_church')):
    for key in re.findall(r'(?m)^(\w+)\s*=\s*\{',p.read_text(encoding='utf-8-sig')):
        DATA.setdefault(key,key.removeprefix('rip_church_').replace('_',' ').title())
        DATA.setdefault('desc_'+key,'Part of the current ecclesiastical settlement. Numerical adjustments follow authority and orientation.')
def defined(name,rows):
    result=f'defined_text = {{\n name = {name}\n'
    for trigger,key in rows:
        result+=f' text = {{ trigger = {{ {trigger} }} localisation_key = {key} }}\n'
    return result+'}\n'
custom=defined('GetChurchROStatus',[
 ('has_country_flag = rip_church_reconciliation_pending','rip_church_ro_reconciling'),
 ('has_country_flag = rip_church_ro_schismatic','rip_church_ro_schismatic'),
 ('rip_church_ro_recognized = yes','rip_church_ro_recognized'),
 ('has_country_flag = rip_church_ro_provisional','rip_church_ro_provisional'),
 ('always = yes','rip_church_ro_unrecognized')])
custom+=defined('GetChurchPrivilege',[(f'has_country_modifier = rip_church_gc_{key}',f'rip_church_gc_{key}') for key in ('infrastructure','coexistence')]+[('always = yes','rip_church_none')])
custom+=defined('GetChurchLocalInstitution',[
 ('has_country_modifier = rip_church_gc_infrastructure','rip_church_gc_infrastructure'),
 ('has_country_modifier = rip_church_gc_coexistence','rip_church_gc_coexistence'),
 ('always = yes','rip_church_none')])
custom+=defined('GetChurchCuriaStatus',[
 ('NOT = { rip_church_gc_rome_present = yes }','rip_church_gc_curia_absent'),
 ('war_with = PAP','rip_church_gc_curia_war'),
 ('PAP = { has_opinion = { who = ROOT value = 50 } }','rip_church_gc_curia_good'),
 ('always = yes','rip_church_gc_curia_cold')])
custom+=defined('GetChurchPapalOpinion',[
 ('rip_church_gc_rome_present = yes NOT = { check_variable = { which = rip_church_papal_opinion value = 0 } }','rip_church_gc_opinion_negative'),
 ('rip_church_gc_rome_present = yes','rip_church_gc_opinion_value'),
 ('always = yes','rip_church_gc_opinion_absent')])
custom+=defined('GetChurchCuriaController',[
 ('has_global_flag = rip_church_gc_controller_known event_target:rip_church_gc_controller = { is_papal_controller = yes }','rip_church_gc_controller_name'),
 ('always = yes','rip_church_gc_controller_none')])
custom+=defined('GetChurchRiteStatus',[
 ('has_province_flag = rip_church_rite_recognized','rip_church_rite_recognized'),
 ('always = yes','rip_church_rite_unrecognized')])
for key in ('war','mercy','building','mission'):
    custom+=defined('GetChurchIcon'+key.title(),[(f'has_country_flag = rip_church_icon_{key}','rip_church_active'),('always = yes','rip_church_inactive')])
    custom+=defined('GetChurchIcon'+key.title()+'Access',[
        (f'has_country_flag = rip_church_icon_{key}','rip_church_icon_can_deactivate'),
        ('NOT = { check_variable = { which = rip_church_fervor value = 10 } }','rip_church_icon_no_fuel'),
        ('NOT = { rip_church_ro_slot_available = yes }','rip_church_icon_no_slot'),
        (f'has_country_flag = rip_church_icon_{key}_used NOT = {{ had_country_flag = {{ flag = rip_church_icon_{key}_used days = 365 }} }}','rip_church_icon_cooldown'),
        ('always = yes','rip_church_icon_can_activate')])
custom+=defined('GetChurchSlotState',[
 ('rip_church_gc_has_privilege = yes','rip_church_gui_slot_used'),('always = yes','rip_church_gui_slot_free')])
custom+=defined('GetChurchCoexistenceState',[
 ('has_country_flag = rip_church_ecumenical','rip_church_gui_coexistence_ecumenical'),
 ('has_country_modifier = rip_church_gc_coexistence','rip_church_gui_coexistence_active'),('always = yes','rip_church_gui_coexistence_local')])
custom+=defined('GetChurchUnionPathState',[
 ('religion = orthodox','rip_church_gui_path_orthodox'),('has_country_flag = rip_church_supports_union','rip_church_gui_path_patron'),('always = yes','rip_church_gui_path_catholic')])
custom+=defined('GetChurchUnionPathIdentity',[
 ('religion = orthodox','rip_church_gui_identity_orthodox'),('always = yes','rip_church_gui_identity_catholic')])
custom+=defined('GetChurchFlorenceProgress',[
 ('has_country_flag = rip_church_florentine_union','rip_church_gui_florence_done'),
 ('has_country_flag = rip_church_florence_pending had_country_flag = { flag = rip_church_florence_pending days = 1825 }','rip_church_gui_florence_due'),
 ('has_country_flag = rip_church_florence_pending','rip_church_gui_florence_wait'),('always = yes','rip_church_gui_florence_none')])
custom+=defined('GetChurchRiteFamily',[('religion = catholic','rip_church_gui_rite_latin'),('always = yes','rip_church_gui_rite_eastern')])
custom+=defined('GetChurchPatronState',[
 ('has_country_flag = rip_church_supports_union','rip_church_gui_patron_active'),
 ('always = yes','rip_church_gui_patron_inactive')])
custom+=defined('GetChurchParishRegisterState',[
 ('OR = { check_variable = { which = rip_church_gui_eastern_parishes value = 1 } check_variable = { which = rip_church_gui_latin_parishes value = 1 } }','rip_church_gui_parish_register_active'),
 ('always = yes','rip_church_gui_parish_register_empty')])
outputs={'customizable_localization/rip_church_redesign.txt':custom}
# Retire generated strings for the removed Communion scale, paid Curia
# petition/control economy and artificial Union-centre rings. The current
# fixed-price Holy See gift is a separate diplomatic action, not that economy.
for key in list(DATA):
    if (key.startswith(('rip_church_gc_petition_', 'desc_rip_church_gc_petition_',
                        'rip_church_gc_donation_', 'rip_church_gc_donate_',
                        'rip_church_gui_ring_', 'rip_church_standing_rate_'))
            or key in {'rip_church_gc_curia_privilege', 'rip_church_gc_curia_privilege_tt',
                       'rip_church_gc_donation', 'rip_church_gc_donation_tt',
                       'rip_church_gc_orientation',
                       'rip_church_gc_orientation_tt', 'rip_church_gc_petitions_title',
                       'rip_church_gc_petitions_title_tt', 'rip_church_gc_rate_paused',
                       'rip_church_gc_rome_resources', 'rip_church_gc_rome_resources_tt',
                       'rip_church_gc_blessing', 'desc_rip_church_gc_blessing',
                       'rip_church_gc_church_tax', 'desc_rip_church_gc_church_tax',
                       'rip_church_gc_holy_war', 'desc_rip_church_gc_holy_war',
                       'rip_church_gc_saint', 'desc_rip_church_gc_saint',
                       'rip_church_gc_usury', 'desc_rip_church_gc_usury',
                       'rip_church_gc_monopoly', 'desc_rip_church_gc_monopoly',
                       'rip_church_gc_legate', 'desc_rip_church_gc_legate',
                       'rip_church_gc_dynastic', 'desc_rip_church_gc_dynastic',
                       'rip_church_gc_prestige', 'desc_rip_church_gc_prestige'}):
        del DATA[key]
# The nine retired petition modifiers survive as empty stubs so the one-time old-save cleanup
# can name them (common/event_modifiers/RIP_church_retired_modifiers.txt); they need a label.
for key in ('legate', 'dynastic', 'prestige', 'church_tax', 'blessing',
            'usury', 'holy_war', 'saint', 'monopoly'):
    DATA['rip_church_gc_' + key] = 'Retired church adjustment'
    DATA['desc_rip_church_gc_' + key] = 'This adjustment no longer exists. It has no effect and is cleared automatically.'
DATA.update({
    'rip_church_gui_slot_state_tt':
        'Eastern infrastructure and coexistence share one ten-year local synod slot. Opening the synod is free.',
    'rip_church_opinion_synod_schools': 'Synodal cooperation in education',
    'rip_church_opinion_synod_compact': 'Synodal guarantees of coexistence',
    'rip_church_gui_slot_free_tt': 'Local synod institution: §G0 / 1§!',
    'rip_church_gui_slot_used_tt': 'Local synod institution: §Y1 / 1§!',
    'rip_church_gc_infrastructure_button_tt':
        'Costs 20 Patriarch Authority and 75 ducats. For ten years: -10% state maintenance and +5% clergy loyalty equilibrium. Immediately lowers autonomy by 5 in controlled Greek Catholic core cities. Peaceful Greek Catholic neighbours gain +10 opinion of us for ten years.',
    'rip_church_gc_coexistence_button_tt':
        'Costs 20 Patriarch Authority and 100 ducats; requires a controlled Orthodox, Russian Orthodox or Catholic city with guaranteed community rights. Immediately grants +5 autonomy to each such community. For ten years: -0.5 national unrest, +10% improve relations and +15 opinion of us from peaceful Christian neighbours which do not oppose the Union.',
    'rip_church_gc_pope_shield_tt':
        'The Catholic Papal State. Click to open its country view. Opinion of us: [Root.GetChurchPapalOpinion].',
    'rip_church_gc_curia_note':
        'Rome is recorded here as a diplomatic contact. No standing, votes, or offices are conferred.',
    'rip_church_gc_curia_note_tt':
        'Rome is recorded here as a diplomatic contact. No standing, votes, or offices are conferred.',
    'rip_church_gc_curia_vote_disclaimer':
        'An Eastern deputation grants no cardinalship, Curia vote, or control of papal elections.',
    'rip_church_gc_curia_vote_disclaimer_tt':
        'An Eastern deputation grants no cardinalship, Curia vote, or control of papal elections.',
    'rip_church_gc_deputation_button_tt':
        'Send a diplomatic audience request to the Holy See. Costs §Y50 ducats§! and grants +25 opinion in both directions, decaying by 2 per year. Once every five years; no electoral rights or resource are gained.',
    'rip_church_gc_deputation_note':
        'Cooldown: §Y5 years§!\\nRequires: Catholic Papal State, peace, and §Y50 ducats§!\\nEffect: +25 opinion in both directions, decaying by 2 per year; diplomatic contact only.',
    'rip_church_gc_help':
        'Use the local synod and devotional icons. Select an owned province to guarantee its community rights.\\nHover buttons for costs and conditions.',
    'rip_church_withdraw_union_support_desc':
        "End the Catholic crown's patronage of the Union. Existing parish faiths do not change; earlier foundation and negotiation payments are not refunded.",
    'rip_church_oppose_union_desc':
        'For 25 DIP, adopt or end state opposition to the Union. Opposition imposes a mutual -10 opinion with Greek Catholic countries. The policy can be changed once every five years.',
    'rip_church_recognize_rite_button_tt': RITE_BUTTON_TT,
})
DATA.update({
 'rip_church_gui_communion_cell':'§WCommunion§!\\n§GIn communion with Rome§!',
 'rip_church_gui_rite_cell':'§WCommunity rights§!\\n§bProvince by province§!',
 'rip_church_gui_count_eastern':'Eastern communities: [Root.GetChurchEasternCount]',
 'rip_church_gui_count_latin':'Latin communities: [Root.GetChurchLatinCount]',
 'rip_church_gui_count_eastern_tt':'Open the community register. This province count is a gameplay abstraction, not an exact historical parish or canonical-status count, and not evidence of voluntary Union acceptance.',
 'rip_church_gui_count_latin_tt':'Open the community register. This province count is a gameplay abstraction, not an exact historical parish or canonical-status count, and not evidence of voluntary Union acceptance.',
 'rip_church_gui_zero_count':'§R0§!',
 'rip_church_gui_eastern_count_value':'§Y[Root.rip_church_gui_eastern_parishes.GetValue]§!',
 'rip_church_gui_latin_count_value':'§Y[Root.rip_church_gui_latin_parishes.GetValue]§!',
 'rip_church_gui_ecumenism_state':'§WEcumenism§!\\n[Root.GetChurchEcumenismAccess]',
 'rip_church_gui_policy_locked':'§RLocked§!',
 'rip_church_gui_policy_ready':'§GAvailable§!',
 'rip_church_gui_policy_done':'§GEstablished§!',
 'rip_church_gui_slot_free':'Local Synod\\n§R0§! / §Y1§!',
 'rip_church_gui_slot_used':'Local Synod\\n§G1§! / §Y1§!',
 'rip_church_gc_icons_note':'One icon · §Y20§! PA · §Y5§! years',
 'rip_church_gc_curia_heading':'§WHOLY SEE§!',
 'rip_church_gc_curia_note':'Papal opinion: [Root.GetChurchPapalOpinion]\\n§bDiplomatic contact only§!',
 'rip_church_gui_rights_title':'§WRIGHTS DENIED§!',
 'rip_church_gui_right_cardinal':'Cardinal\\n§RNot granted§!',
 'rip_church_gui_right_vote':'Curia vote\\n§RNot granted§!',
 'rip_church_gui_right_conclave':'Conclave\\n§RNot granted§!',
 'rip_church_gc_deputation_button':'Eastern deputation',
 'rip_church_gui_contact_cost':'§Y50§! ducats',
 'rip_church_gui_contact_peace':'§YPeace§!',
 'rip_church_gui_contact_rome':'§YCatholic§!\\nPapal State',
 'rip_church_gui_contact_cooldown':'§Y5§! years',
 'rip_church_gui_contact_history':'[Root.GetChurchContactHistory]',
 'rip_church_gui_contact_none':'§bNo deputation sent§!',
 'rip_church_gui_contact_recent':'§bDeputation sent · cooldown active§!',
 'rip_church_gui_contact_ready':'§GFive-year interval completed§!',
 'rip_church_gui_register_columns':'§WProvince          Rite          Status          Action§!',
 'rip_church_gui_parish_register_empty':'§bNo community rights guaranteed§!',
 'rip_church_gui_parish_register_active':'§bCommunity rights are guaranteed in some of our provinces.§!\\nSelect a province to inspect or revoke its guarantee.',
})
for family in ('eastern','latin'):
 custom+=defined('GetChurch'+family.title()+'Count',[
  (f'check_variable = {{ which = rip_church_gui_{family}_parishes value = 1 }}',f'rip_church_gui_{family}_count_value'),
  ('always = yes','rip_church_gui_zero_count')])
custom+=defined('GetChurchEcumenismAccess',[
 ('has_country_flag = rip_church_ecumenical','rip_church_gui_policy_done'),
 ('rip_church_can_ecumenism = yes','rip_church_gui_policy_ready'),
 ('always = yes','rip_church_gui_policy_locked')])
custom+=defined('GetChurchContactHistory',[
 ('NOT = { has_country_flag = rip_church_gc_deputation_sent }','rip_church_gui_contact_none'),
 ('had_country_flag = { flag = rip_church_gc_deputation_sent days = 1825 }','rip_church_gui_contact_ready'),
 ('always = yes','rip_church_gui_contact_recent')])
# Live readouts use trigger-backed localization, never dynamic button labels.
DATA.update({
 'rip_church_gui_shared_status':'§GIn communion§! · Rome: [Root.GetChurchPapalOpinion] · PA: [Root.GetChurchAuthorityReadout]',
 'rip_church_gui_count_eastern_value':'Eastern: [Root.GetChurchEasternCount]',
 'rip_church_gui_count_latin_value':'Latin: [Root.GetChurchLatinCount]',
 'rip_church_gui_rite_cell':'Rights: §Yprovince by province§!',
 'rip_church_gui_rite_cell_tt':'Each community keeps its own religion and local agreement. Guaranteeing rights does not convert nearby provinces or bring any province into the Union.',
 'rip_church_gui_slot_free':'Slots used\\n§R0§! / §Y1§!',
 'rip_church_gui_slot_used':'Slots used\\n§Y1§! / §Y1§!',
 'rip_church_gui_rights_title':'Rights',
 'rip_church_gui_ecumenism_reason':'[Root.GetChurchEcumenismReason]',
 'rip_church_gui_contact_cost':'Cost: [Root.GetChurchMissionCost]',
 'rip_church_gui_contact_peace':'Peace: [Root.GetChurchMissionPeace]',
 'rip_church_gui_contact_rome':'Rome: [Root.GetChurchMissionRome]',
 'rip_church_gui_contact_cooldown':'Cooldown: [Root.GetChurchMissionCooldown]',
 'rip_church_gui_contact_history':'[Root.GetChurchMissionReason]',
 'rip_church_gui_recognition_cost':'§Y1 ADM per development§! · lasts at least ten years\\nOwned, controlled Orthodox, Muscovite Orthodox or Catholic city. Its religion does not change.',
 'rip_church_gui_recognition_reason':'[Root.GetChurchRecognitionReason]',
 'rip_church_gui_parish_register_empty':'§WNo community rights are guaranteed.§!\\n\\nA guarantee protects a province\'s rite and clergy and removes its religious-unity penalty, at the price of lower tax and levies. It does not convert the province.',
 'rip_church_gui_register_columns':'[Root.GetChurchRegisterColumns]',
 'rip_church_gui_register_header_empty':'§WProvince          Rite          Status§!',
 'rip_church_gui_register_header_full':'§WProvince          Rite          Status          Action§!',
 'rip_church_gc_icons_note':'Cost: §Y20 PA§! · Duration: §Y5 years§! · One active; no replacement',
})
def ui_readout(name,rows):
 global custom
 pairs=[]
 for i,(gate,label) in enumerate(rows):
  key='rip_church_readout_'+name.lower()+'_'+str(i)
  DATA[key]=label
  pairs.append((gate,key))
 custom+=defined(name,pairs)
ui_readout('GetChurchAuthorityReadout',[
 (f'patriarch_authority = {i/100:.2f}',f'§Y{i}%§!') for i in range(100,-1,-1)])
ui_readout('GetChurchEcumenismReason',[
 ('has_country_flag = rip_church_ecumenical','§GSettlement established§!'),
 ('NOT = { religion = greek_catholic }','§RRequires Greek Catholic faith§!'),
 ('NOT = { had_country_flag = { flag = rip_church_union_founded days = 7300 } }','§RRequires 20 years of Union§!'),
 ('has_country_flag = rip_church_forced_integration NOT = { had_country_flag = { flag = rip_church_forced_integration days = 3650 } }','§R10 years since forced integration§!'),
 ('NOT = { stability = 2 }','§RRequires stability +2§!'),
 ('is_at_war = yes','§RRequires peace§!'),
 ('NOT = { any_owned_province = { religion = orthodox has_province_flag = rip_church_rite_recognized } }','§RGuarantee rights of an Orthodox community§!'),
 ('NOT = { any_owned_province = { religion = catholic has_province_flag = rip_church_rite_recognized } }','§RGuarantee rights of a Latin community§!'),
 ('NOT = { any_country = { religion = orthodox alliance_with = ROOT has_opinion = { who = ROOT value = 100 } } }','§ROrthodox ally: opinion +100§!'),
 ('always = yes','§GAll requirements met§!')])
ui_readout('GetChurchMissionCost',[('treasury = 50','§G50 ducats§!'),('always = yes','§R50 ducats needed§!')])
ui_readout('GetChurchMissionPeace',[('is_at_war = no','§GYes§!'),('always = yes','§RNo§!')])
ui_readout('GetChurchMissionRome',[('rip_church_gc_rome_present = yes','§GCatholic PAP§!'),('always = yes','§RUnavailable§!')])
ui_readout('GetChurchMissionCooldown',[
 ('NOT = { has_country_flag = rip_church_gc_deputation_sent }','§GReady§!'),
 ('had_country_flag = { flag = rip_church_gc_deputation_sent days = 1825 }','§GReady§!'),
 ('always = yes','§RWait 5 years§!')])
ui_readout('GetChurchMissionReason',[
 ('NOT = { religion = greek_catholic }','§RRequires Greek Catholic faith§!'),
 ('NOT = { rip_church_gc_rome_present = yes }','§RCatholic Papal State must exist§!'),
 ('is_at_war = yes','§REnd the war before sending a deputation§!'),
 ('NOT = { treasury = 50 }','§RRequires 50 ducats§!'),
 ('rip_church_gc_can_depute_to_curia = yes','§GReady to send · diplomatic contact only§!'),
 ('always = yes','§RFive-year interval has not elapsed§!')])
ui_readout('GetChurchRecognitionReason',[
 ('NOT = { religion = greek_catholic }','§RRequires Greek Catholic faith§!'),
 ('NOT = { any_owned_province = { is_city = yes controlled_by = owner OR = { religion = orthodox religion = russian_orthodox religion = catholic } NOT = { has_province_flag = rip_church_rite_recognized } } }','§RNo eligible controlled community§!'),
 ('NOT = { any_owned_province = { rip_church_can_recognize_rite = yes } }','§RInsufficient ADM for an eligible community§!'),
 ('always = yes','§YSelect a province; guarantee its community rights in the province panel§!')])
custom+=defined('GetChurchRegisterColumns',[
 ('any_owned_province = { has_province_flag = rip_church_rite_recognized }','rip_church_gui_register_header_full'),
 ('always = yes','rip_church_gui_register_header_empty')])
for key,label in (('liturgy','Liturgy'),('learning','Learning'),('charity','Almsgiving')):
 ui_readout('GetChurchDevotional'+key.title(),[
  (f'has_country_modifier = rip_church_gc_icon_{key}',label+'\\n§GActive§!'),
  ('rip_church_gc_has_active_icon = yes',label+'\\n§RAnother icon active§!'),
  ('NOT = { patriarch_authority = 0.2 }',label+'\\n§RRequires 20 PA§!'),
  ('always = yes',label+'\\n§YAvailable§!')])
 DATA['rip_church_gc_icon_'+key+'_state']='[Root.GetChurchDevotional'+key.title()+']'
 DATA['rip_church_gc_icon_'+key+'_state_tt']=DATA['rip_church_gc_icon_'+key+'_button_tt']
DATA['rip_church_gui_ecumenism_reason_tt']='[Root.GetChurchEcumenismReason]\\n'+DATA['rip_church_gui_ecumenism_tt']
for key in ('cardinal','vote','conclave'):
 DATA['rip_church_gui_right_'+key+'_tt']='Unavailable to the Greek Catholic Union. Papal opinion and deputations grant no cardinalship, Curia vote or conclave participation; there is no opinion threshold.'
# PA is reused as a local administrative resource, not universal UGCC authority.
GC_CAPACITY_HELP=('Hierarchical Capacity (HC) is the Greek Catholic label for the native Patriarch Authority bar (0–100), '
 'used here as a gameplay abstraction for the local church administration, not as papal standing or a historical measure of universal UGCC authority. '
 'Recurring gain: +7.5 HC per year (+0.625 per month) from the Greek Catholic state religion. Country-specific decisions, events and mission rewards may also change the bar; '
 'there is no free refill when loading a save. One devotional icon at a time costs 20 HC and lasts five years: Liturgy grants +1 yearly prestige, +1 diplomatic reputation '
 'and +20% improve relations; Learning grants -5% development cost and -5% technology cost; Almsgiving grants -1 global unrest and -10% stability cost. '
 'A local synod lasts ten years and costs 20 HC plus 75 ducats for Infrastructure (-10% state maintenance, +5% church loyalty and -5% local autonomy in owned Greek Catholic core cities), '
 'or 20 HC plus 100 ducats for Coexistence (-0.5 global unrest, +10% improve relations and +5% local autonomy in recognized non-Greek-Catholic communities). '
 'A parish visit costs 5 HC, 100 ducats and 25 ADM, once per ten years: choose +1% local missionary strength or -1 local unrest in one eligible province; either choice also gives -5% local tax for ten years. '
 'The bar also recalculates country and province balancing modifiers in five-point bands, so HC is not an unconditional bonus: at 100, the country has -2% global missionary strength and -10% church influence; '
 'owned Greek Catholic provinces have +2.25/+2.625/+3 local unrest by region and -33% local manpower. Other decisions show their own HC thresholds and costs.')
for key,value in list(DATA.items()):
 if (key.startswith(('rip_church_gc_', 'rip_church_readout_getchurchdevotional', 'rip_church_gui_shared_status'))
     or key in ('greek_catholic_religion_desc','rip_church.6.d','rip_church_gui_synod_tt')):
  DATA[key]=re.sub(r'\bPA\b','HC',value.replace('Patriarchal Authority','Hierarchical Capacity').replace('Patriarch Authority','Hierarchical Capacity'))
DATA['rip_church_gc_resources']='Hierarchical Capacity: [Root.GetChurchAuthorityReadout]'
DATA['rip_church_gc_controller_readout']='Curia controller\\n§Y[Root.GetChurchCuriaController]§!'
DATA['rip_church_gc_controller_readout_tt']='Country currently controlling the Catholic Curia: [Root.GetChurchCuriaController]. This is not the birthplace or nationality of the Pope. Reopening the Curia tab refreshes the current controller.'
for key in ('rip_church_gc_resources_tt','rip_church_gc_help_tt','rip_church_gui_shared_status_tt'):
 DATA[key]=GC_CAPACITY_HELP
DATA['greek_catholic_religion_desc']+=' '+GC_CAPACITY_HELP
DATA['rip_church_authority_heading']='[Root.GetChurchAuthorityHeading]'
DATA['rip_church_gc_capacity_heading']='Hierarchical Capacity'
DATA['rip_church_native_authority_heading']='$CURRENT_PATRIARCH_AUTHORITY$'
custom+=defined('GetChurchAuthorityHeading',[
 ('religion = greek_catholic','rip_church_gc_capacity_heading'),
 ('always = yes','rip_church_native_authority_heading')])
outputs['customizable_localization/rip_church_redesign.txt']=custom
DATA['rip_church_gui_ecumenism_state_tt']=DATA['rip_church_gui_ecumenism_tt']
for key in ('cost','peace','rome','cooldown','history'):
 DATA['rip_church_gui_contact_'+key+'_tt']=DATA['rip_church_gc_deputation_button_tt']
for key,value in list(DATA.items()):
 if key.startswith(('rip_church_gui_','rip_church_gc_')) and not key.endswith('_tt'):
  DATA.setdefault(key+'_tt',value)
for lang in ('english','french','german','spanish'):
    outputs[f'localisation/replace/zzzz_RIP_church_redesign_l_{lang}.yml']='\ufeffl_'+lang+':\n'+''.join(f' {k}:0 "{v.replace(chr(34),chr(39))}"\n' for k,v in sorted(DATA.items()))
# Regression guard: the province action is a guarantee of community rights, never the
# recognition of a parish or a rite. Patriarchate recognition (rip_church.3, ro_recognized)
# is a different mechanic and does not match.
old_framing=re.compile(r'\b(?:recogni[sz]e[sd]?|recognition of)\s+(?:the\s+|a\s+|an\s+)?(?:local\s+|eastern\s+|latin\s+|orthodox\s+)?(?:parish|parishes|rite|rites)\b'
                       r'|\bconfessional autonomy\b|\brecogni[sz]ed\s+(?:\w+\s+)?(?:parish|parishes|rite|rites)\b',re.I)
bad=sorted(k for k,v in DATA.items() if old_framing.search(v))
if bad: raise SystemExit('Old recognition framing of the province action in: '+', '.join(bad))
stale=[]
for path,text in outputs.items():
    p=ROOT/path
    if not p.exists() or p.read_text(encoding='utf-8')!=text:
        stale.append(path)
        if not args.check:
            p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text,encoding='utf-8',newline='\n')
print(('STALE' if args.check and stale else 'GENERATED')+f': {len(DATA)} keys; {len(stale)} files')
if args.check and stale: raise SystemExit(1)
