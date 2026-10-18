"""Build read-only government explanations from native EU4 custom GUI contracts.
Uses the installed 1.37 government window; --check verifies deterministic output.
"""
from pathlib import Path
import argparse, os
ROOT = Path(__file__).resolve().parents[1]
GAME = Path(os.environ.get('EU4_DIR', 'D:/Programs Files(x86)/Steam/steamapps/common/Europa Universalis IV'))
LOC = {}
DYNAMIC = []
CONTROLS = []

def loc(key, value):
    LOC[key] = value
    return key

def choice(name, branches, fallback='None'):
    lines = ['defined_text = {', f' name = {name}', ' random = no']
    for i, (trigger, value) in enumerate(branches + [('always = yes', fallback)]):
        key = loc(f'rip_gov_{name}_{i}', value)
        lines.append(f' text = {{ trigger = {{ {trigger} }} localisation_key = {key} }}')
    DYNAMIC.append('\n'.join(lines + ['}']))
    return f'[Root.{name}]'

def factor(name, trigger, value, label):
    active = ('§G' if value < 0 else '§R') + f'{value:+g}§!'
    # For concord and integration, increasing values are beneficial.
    if name.startswith('Cesar'):
        active = ('§G' if value > 0 else '§R') + f'{value:+g}§!'
    return choice(name, [(trigger, active)], '0') + ' ' + label

def row(name, y, text, tip, height=22):
    loc(name, text)
    loc(name + '_tt', tip)
    CONTROLS.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{ name = "{name}" scripted = yes position = {{ x=18 y={y} }} font = "vic_18" text = "{name}" maxWidth = 434 maxHeight = {height} format = left }}'''

def panel(name, potential, rows):
    CONTROLS.append(f'custom_window = {{ name = {name} potential = {{ {potential} }} }}')
    return f'''windowType = {{ name = "{name}" scripted = yes position = {{ x=550 y=72 }} size = {{ x=470 y=290 }} moveable = 0
 iconType = {{ name = "background" spriteType = "GFX_rip_government_status_bg" position = {{ x=0 y=0 }} }}
 {chr(10).join(rows)}
}}'''

factions = [('knyazi', 'Knyazi'), ('boyary', 'Boyars'), ('starshyna', 'Starshyna')]
active = 'has_country_flag = kru_factional_dominance_active'
dominant = choice('RipGovDominant', [(f'{active} has_country_flag = kru_current_dominant_{f}', n) for f,n in factions], 'No bloc at 60')
partner = choice('RipGovPartner', [(f'{active} has_country_flag = kru_previous_dominant_{f}', n) for f,n in factions], 'No coalition')
voice = choice('RipGovJuniorVoice', [(f'has_country_modifier = KRU_junior_{f}', n) for f,n in factions], 'None')
opposition = choice('RipGovOpposition', [(f'{active} NOT = {{ has_country_flag = kru_current_dominant_{f} }} NOT = {{ has_country_flag = kru_previous_dominant_{f} }}', n) for f,n in factions], 'No coalition')
coalition_tip = 'The leading faction must have at least 60 influence to dominate. Its partner is the PREVIOUS dominant faction, not the runner-up. The third faction is the opposition. The partner receives a junior-voice modifier only at 38 influence or more.\nOn the first recorded dominance, the default partner is Boyars for Knyazi, and Knyazi for Boyars or Starshyna. Below 60 there is no coalition or junior voice; the States General scale returns to centre. The remembered previous dominant faction is retained.\nThe record refreshes monthly and after courting a faction. States General requires Res Publica or Winds of Change.'
annual = [
 ('StabZero','stability = 0 NOT = { stability = 1 }',2,'stability = 0'),
 ('StabBad','NOT = { stability = 0 }',3,'stability < 0'),
 ('War','is_at_war = yes',1,'at war'),
 ('Loans','num_of_loans = 5',1,'at least 5 loans'),
 ('Autonomy','average_autonomy = 40',1,'average autonomy at least 40%'),
 ('Legitimacy','NOT = { legitimacy = 50 }',1,'legitimacy below 50'),
 ('StabGood','stability = 2',-3,'stability at least +2'),
 ('Peace','is_at_war = no',-2,'at peace')]
annual_text = '\n'.join(factor('RipGov'+n,t,v,l) for n,t,v,l in annual)
annual_tip = 'Current conditions for the next yearly pulse; coloured values are active, 0 means inactive. Add these values together. Events can change Decadence separately; this is not a forecast of intervening events.\n' + annual_text + '\nOn the first yearly update, an uninitialised zero starts at 20 before these changes. Annual modifiers: below 40 / 40-69 / at least 70.'
crisis_tip = 'Court Crisis can start accumulating for KRU with this reform, no other disaster, and Decadence at least 90. Base monthly progress at 90+: +6; frontier centralisation +1.5, frontier liberties -1, southern recovery -1. Progress recedes below 75. An active crisis ends only when Decadence is below 60 AND stability is at least +1.\nThe first annual crossing of 90 can also trigger a separate court event; its choices reduce Decadence. A threshold does not mean the disaster starts immediately.'
kru_rows = [row('rip_gov_kru_title',12,'§YRada and Decadence§!',coalition_tip), row('rip_gov_kru_leader',40,'Dominant: '+dominant,coalition_tip),row('rip_gov_kru_partner',64,'Partner: '+partner,coalition_tip),row('rip_gov_kru_opposition',88,'Opposition: '+opposition,coalition_tip),row('rip_gov_kru_voice',112,'Junior voice: '+voice,coalition_tip), row('rip_gov_kru_decay',146,'Decadence: §Y[Root.ruthenian_decadence.GetValue]§!',annual_tip),row('rip_gov_kru_annual',174,'Yearly change: hover for active factors',annual_tip),row('rip_gov_kru_crisis',202,'Crisis: 90+ | Retreat: <75 | End: <60, stability +1',crisis_tip),row('rip_gov_kru_memory',236,'Partner follows the previous dominance.',coalition_tip)]
kru_potential = 'tag = KRU OR = { has_reform = ruthenian_factional_empire_reform has_reform = ruthenian_factional_empire_princes_hetmans_reform has_reform = ruthenian_factional_empire_boyars_hetmans_reform }'

def share(var, name):
    return choice(name, [(f'check_variable = {{ which = {var} value = {i/100:g} }}', f'{i}%') for i in range(100,0,-1)], '0%')
minority = share('rip_cesar_minority_share', 'RipGovMinorityShare')
excluded = share('rip_cesar_excluded_share', 'RipGovExcludedShare')
eligible = choice('RipGovIntegration', [('rip_cesar_integration_eligible = yes','§GEligible§!')], '§RNot eligible§!')
breakdown = choice('RipGovBreakdown', [('has_country_flag = rip_cesar_breakdown','§RBreakdown active§!')], 'No active breakdown')
lands_tip = 'Shares use total development of ALL owned provinces, including territories; subjects are excluded. The census updates monthly. Displayed whole percentages are rounded down; thresholds use the exact share.\nNon-primary: provinces whose culture differs from the owner\'s primary culture. Unaccepted: the subset of those provinces for which the engine reports no owner-accepted culture. Accepted same-group cultures therefore follow the engine\'s cultural-union rules.\nConquest, development, province loss, culture conversion and changes in accepted or primary culture alter these shares at the next census. Promoting a culture can reduce the unaccepted share without reducing the non-primary share.'
elig_tip = 'Integration requires ALL three: at least one owned non-primary province with an owner-accepted culture; at least one accepted culture; non-primary development at least 10%. A cultural union alone does not waive the accepted-culture requirement.\nThree accepted cultures add growth only while these requirements hold. Development matters, not the number of provinces.'
power = lambda p,v: f'has_government_power = {{ mechanic_type = {p}_mechanic power_type = {p} value = {v} }}'
concord = 'kyivan_throne_concord'; gathering = 'kyivan_peoples_gathering'
concord_factors = [('Stable','stability = 2',.1,'stability at least +2'),('Unstable','NOT = { stability = 0 }',-.2,'negative stability'),('Legit','legitimacy = 80',.2,'legitimacy at least 80'),('Illegit','NOT = { legitimacy = 40 }',-.25,'legitimacy below 40'),('Subjects','any_subject_country = { liberty_desire = 50 }',-.3,'any subject at 50% liberty desire'),('Compact',power(gathering,60)+' rip_cesar_integration_eligible = yes',.15,'Gathering at least 60 and integration eligible'),('Excluded','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.3,'unaccepted share at least 30%')]
gather_factors = [('Eligible','rip_cesar_integration_eligible = yes',.3,'integration eligible'),('Cultures','rip_cesar_integration_eligible = yes num_accepted_cultures = 3',.15,'eligible and at least 3 accepted cultures'),('Minority','rip_cesar_integration_eligible = yes check_variable = { which = rip_cesar_minority_share value = 0.3 }',.15,'eligible and non-primary share at least 30%'),('Throne','rip_cesar_integration_eligible = yes '+power(concord,60),.1,'eligible and Concord at least 60'),('Excluded15','check_variable = { which = rip_cesar_excluded_share value = 0.15 }',-.25,'unaccepted share at least 15%'),('Excluded30','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.35,'unaccepted share at least 30% (stacks with 15%)'),('WeakThrone','NOT = { '+power(concord,30)+' }',-.2,'Concord below 30'),('Exhausted','war_exhaustion = 5',-.15,'war exhaustion at least 5'),('Ineligible','NOT = { rip_cesar_integration_eligible = yes }',-.5,'integration not eligible')]
concord_tip = 'Monthly Concord: base +0.10, plus active values below.\n'+'\n'.join(factor('CesarConcord'+n,t,v,l) for n,t,v,l in concord_factors)+'\nAt zero Concord, Throne in Disarray lasts 1825 days.'
gather_tip = 'Monthly Gathering: base 0, plus active values below.\n'+'\n'.join(factor('CesarGather'+n,t,v,l) for n,t,v,l in gather_factors)+'\nAt 100: a 3650-day compact, +10 prestige and +10 Concord; Gathering resets to 40. This reset is not a breakdown.'
recovery_tip = 'Monthly breakdown check: unaccepted development at least 30% AND Gathering below 20. Once per breakdown: -15 Concord and Throne in Disarray for 1825 days.\nRecovery requires unaccepted development strictly below 15% AND Gathering at least 40. It clears the breakdown flag; the timed Throne in Disarray modifier remains until expiry. Falling to zero Concord can also apply that modifier.'
cesar_rows = [row('rip_gov_cesar_title',12,'§YCesarstvo: Lands and Settlement§!',lands_tip),row('rip_gov_cesar_minority',44,'Non-primary development: ~'+minority,lands_tip),row('rip_gov_cesar_excluded',72,'Unaccepted development: ~'+excluded,lands_tip),row('rip_gov_cesar_eligible',104,'Integration: '+eligible,elig_tip),row('rip_gov_cesar_concord',136,'Throne Concord: monthly factors',concord_tip),row('rip_gov_cesar_gather',164,'Gathering: monthly factors',gather_tip),row('rip_gov_cesar_breakdown',198,breakdown,recovery_tip),row('rip_gov_cesar_recovery',230,'Crisis and recovery: hover for thresholds',recovery_tip)]

# --- Shared Institutional Review (Municipal, Chancery, Cossack Register) ---
rev_active = choice('RipGovActiveReview', [
    ('has_country_modifier = rip_gov_municipal_charters', '§GMunicipal Charters§!'),
    ('has_country_modifier = rip_gov_municipal_accounts', '§GMunicipal Accounts§!'),
    ('has_country_modifier = rip_gov_chancery_service', '§GChancery Service Rolls§!'),
    ('has_country_modifier = rip_gov_chancery_rights', '§GChancery Local Rights§!'),
    ('has_country_modifier = rip_gov_register_muster', '§GCossack Muster§!'),
    ('has_country_modifier = rip_gov_register_settlement', '§GCossack Settlement§!')
], 'No Active Resolution')

rev_lockout = choice('RipGovReviewLockout', [
    ('OR = { has_country_modifier = rip_gov_municipal_charters has_country_modifier = rip_gov_municipal_accounts has_country_modifier = rip_gov_chancery_service has_country_modifier = rip_gov_chancery_rights has_country_modifier = rip_gov_register_muster has_country_modifier = rip_gov_register_settlement }', '§RResolution in Force (10-Yr Lock)§!'),
    ('has_country_flag = rip_gov_review_recent NOT = { had_country_flag = { flag = rip_gov_review_recent days = 3650 } }', '§R10-Year Cooldown Active§!')
], '§GReady for Review§!')

rev_tracks = choice('RipGovReviewInstitutes', [
    ('rip_gov_has_municipal_review = yes rip_gov_has_chancery_review = yes rip_gov_has_register_review = yes', '§GMunicipal, Chancery, Register§!'),
    ('rip_gov_has_municipal_review = yes rip_gov_has_chancery_review = yes', '§GMunicipal & Chancery§!'),
    ('rip_gov_has_municipal_review = yes rip_gov_has_register_review = yes', '§GMunicipal & Register§!'),
    ('rip_gov_has_chancery_review = yes rip_gov_has_register_review = yes', '§GChancery & Register§!'),
    ('rip_gov_has_municipal_review = yes', '§GMunicipal Charters§!'),
    ('rip_gov_has_chancery_review = yes', '§GChancery Rolls§!'),
    ('rip_gov_has_register_review = yes', '§GCossack Register§!')
], 'No Tracks Available')

rev_active_tip = 'Active Institutional Resolution:\n- Municipal Charters: +5% Production Efficiency, +5% Burghers Loyalty, -5 Max Absolutism (50 DIP)\n- Municipal Accounts: +5% National Tax, -0.025 Yearly Corruption, -5% Burghers Loyalty (50 ADM)\n- Chancery Service: -5% State Maintenance, -0.025 Yearly Corruption, -5% Nobility Loyalty (50 ADM)\n- Chancery Rights: -10% Culture Acceptance Cost, -0.5 Unrest, -5% National Tax (50 DIP)\n- Cossack Muster: +5% Manpower Recovery, +5% Land Maintenance (50 MIL)\n- Cossack Settlement: -0.5 Unrest, -5% National Manpower (50 DIP)'
rev_lockout_tip = 'Why choosing one institution temporarily locks out the others:\nMunicipal, Chancery, and Cossack Register reviews form a single shared institutional system.\nEnacting any resolution sets the 10-year shared flag (rip_gov_review_recent), committing the administration to that course for 3650 days.\nDuring this term, all decisions to review other institutions are locked.\nSwitching or losing a reform clears the modifier but DOES NOT reset the 10-year lockout.'
rev_tracks_tip = 'Reforms granting access to institutional review tracks:\n- Municipal Charters: vln_magdeburg_rights\n- Chancery Rolls: lit_ruthenian_chancery_reform, chr_kanceliaryst_republic_reform\n- Cossack Register: het_regimental_system_reform, rip_cossacks_reform, vln_cossack_host_reform, prl_regimental_republic_reform'
rev_terms_tip = 'Review Requirements:\n- At peace (is_at_war = no)\n- Stability >= 0\n- At least 50 ducats in the treasury\n- At least 50 monarch power (ADM, DIP, or MIL depending on choice)\n- 10-year shared cooldown expired'
rev_why_tip = 'The crown cannot balance competing administrative, municipal, and military reorganizations at the same time.\nOnly one institutional resolution can be active at a time across the entire realm.'
rev_reform_note_tip = 'Reform changes do not allow bypassing the 10-year wait:\nLosing or replacing a reform removes the active benefit via removed_effect, but the dated review flag rip_gov_review_recent remains until the full 3650 days elapse.'

# --- Galicia: Ordinances & Council (HLC) ---
hlc_slots = choice('RipGovHlcSlots', [
    ('hlc_ordinance_over_limit = yes', '§R3 / 2 (Over limit)§!'),
    ('NOT = { hlc_ordinance_slot_free = yes }', '§Y2 / 2 (Full)§!'),
    ('OR = { has_country_flag = hlc_chancery_ordinance_active has_country_flag = hlc_settlement_ordinance_active has_country_flag = hlc_cadastral_ordinance_active }', '§G1 / 2 (1 free)§!')
], '§G0 / 2 (2 free)§!')

hlc_active = choice('RipGovHlcOrdinances', [
    ('has_country_flag = hlc_chancery_ordinance_active has_country_flag = hlc_settlement_ordinance_active has_country_flag = hlc_cadastral_ordinance_active', '§RChancery, Settlement, Cadastre§!'),
    ('has_country_flag = hlc_chancery_ordinance_active has_country_flag = hlc_settlement_ordinance_active', '§GChancery & Settlement§!'),
    ('has_country_flag = hlc_chancery_ordinance_active has_country_flag = hlc_cadastral_ordinance_active', '§GChancery & Cadastre§!'),
    ('has_country_flag = hlc_settlement_ordinance_active has_country_flag = hlc_cadastral_ordinance_active', '§GSettlement & Cadastre§!'),
    ('has_country_flag = hlc_chancery_ordinance_active', '§GChancery Ordinance§!'),
    ('has_country_flag = hlc_settlement_ordinance_active', '§GSettlement Ordinance§!'),
    ('has_country_flag = hlc_cadastral_ordinance_active', '§GCadastral Ordinance§!')
], 'None in force')

hlc_council = choice('RipGovHlcCouncil', [
    ('has_country_modifier = hlc_boyars_confirmed', '§GOffices Confirmed (Co-option)§!'),
    ('has_country_modifier = hlc_foreign_claimant_countered', '§GDynastic Defense§!'),
    ('has_country_modifier = hlc_boyars_made_example', '§GRepression of Defiant Boyar§!')
], 'No active course')

hlc_session = choice('RipGovHlcSession', [
    ('OR = { has_country_modifier = hlc_boyars_confirmed has_country_modifier = hlc_foreign_claimant_countered has_country_modifier = hlc_boyars_made_example }', '§RIn Session (10-Yr Lock)§!')
], '§GReady to Convene§!')

hlc_slots_tip = 'Ordinance Slots:\nThe crown chancery keeps at most two of its three ordinances in force simultaneously (hlc_ordinance_slot_free).\nEnacting an ordinance costs 50 DIP or ADM power and starts a 5-year cooldown token.\nRescinding an ordinance is completely free of monarch power, frees one of the two slots, and starts a 5-year cooldown on that ordinance.'
hlc_active_tip = 'Active Chancery Ordinances:\n- Chancery: +1 Diplomatic Reputation, +10% Improve Relations, +10% Advisor Costs (50 DIP)\n- Settlement: -10% Culture Conversion Cost, annual noble steadying, +1 National Unrest (50 ADM)\n- Cadastre: +5% National Tax, -5% Nobility Loyalty Equilibrium (50 ADM)'
hlc_council_tip = 'Active Boyar Council course:\n- Co-option (Confirm in Office): +10 Noble Loyalty for 10 years (available below 60% loyalty)\n- Dynastic Defense (Counter Claimant): +3 Legitimacy for 10 years (available below 60% legitimacy)\n- Repression (Make an Example): +3 Army Tradition, -5 Noble Loyalty for 7 years (at peace, loyalty < 40%)'
hlc_session_tip = 'Shared 10-year session lockout:\nThe Boyar Council courses share a single 10-year cooldown token (hlc_boyar_council_session).\nChoosing any course convenes the council and locks all other courses for 10 years because co-option, dynastic defence, and repression compete rather than stack as independent tools.'

hlc_rows = [
    row('rip_gov_hlc_title', 12, '§YGalicia: Ordinances & Council§!', hlc_slots_tip),
    row('rip_gov_hlc_slots', 38, 'Ordinance Slots: ' + hlc_slots, hlc_slots_tip),
    row('rip_gov_hlc_active', 62, 'Ordinances: ' + hlc_active, hlc_active_tip),
    row('rip_gov_hlc_council', 88, 'Council Course: ' + hlc_council, hlc_council_tip),
    row('rip_gov_hlc_session', 112, 'Council Session: ' + hlc_session, hlc_session_tip),
    row('rip_gov_hlc_reviews', 140, 'Active Resolution: ' + rev_active, rev_active_tip),
    row('rip_gov_hlc_lockout', 164, 'Shared Lockout: ' + rev_lockout, rev_lockout_tip),
    row('rip_gov_hlc_note', 190, 'Review Term: 10 Years | 50 Ducats + 50 Power', rev_terms_tip),
    row('rip_gov_hlc_footer', 220, 'One resolution binds all institutions.', rev_why_tip)
]

# --- Lithuania: Pany Rada (LIT) ---
lit_consent = choice('RipGovLitConsent', [
    ('has_country_modifier = lit_rada_confirmed', '§GConfirmed (+2 Legitimacy)§!')
], '§YNo Consent§!')
lit_retinues = choice('RipGovLitRetinues', [
    ('has_country_modifier = lit_rada_retinues_mustered', '§YRetinues Mustered§!'),
    ('is_at_war = yes has_country_modifier = lit_rada_confirmed estate_loyalty = { estate = estate_nobles loyalty = 40 }', '§GReady (Will Consume Consent)§!'),
    ('has_country_modifier = lit_rada_confirmed', '§YNeeds War & 40% Loyalty§!')
], '§RRequires Rada Consent§!')
lit_lord = choice('RipGovLitBrokerage', [
    ('has_country_modifier = lit_lord_won_over', '§GLord Won Over§!'),
    ('NOT = { estate_loyalty = { estate = estate_nobles loyalty = 50 } }', '§GAvailable (50 DIP -> +15% Loyalty)§!')
], '§YNobility Loyal (>=50%)§!')

lit_consent_tip = 'Rada Confirmation:\nGrants +2 Legitimacy for 5 years.\nRequires noble loyalty >= 40% and costs 10% noble loyalty.\nActive consent is required to muster the Rada\'s Own Retinues.'
lit_retinues_tip = 'The Rada\'s Own Retinues:\nMustering the retinues during wartime CONSUMES the active Rada Consent, costs 10% noble loyalty, and gives +3 Army Tradition and a 5-year combat modifier.\nThe Grand Duke burns his political capital with the lords to call up their private armies.'
lit_lord_tip = 'Win Over a Wavering Lord:\nCosts 50 diplomatic power to restore +15% noble loyalty when noble loyalty drops below 50%.\nEssential for recovering loyalty to reach the 40% threshold needed for consent or retinues.'
lit_threshold_tip = 'Noble Loyalty Thresholds:\n- 40%: Minimum needed to seek Rada consent or muster retinues\n- 50%: Ceiling for winning over a wavering lord\nBoth major Rada actions reduce loyalty by 10%.'

lit_rows = [
    row('rip_gov_lit_title', 12, '§YLithuania: Pany Rada§!', lit_consent_tip),
    row('rip_gov_lit_consent', 38, 'Rada Consent: ' + lit_consent, lit_consent_tip),
    row('rip_gov_lit_retinues', 64, 'Retinues: ' + lit_retinues, lit_retinues_tip),
    row('rip_gov_lit_lord', 90, 'Wavering Lord: ' + lit_lord, lit_lord_tip),
    row('rip_gov_lit_threshold', 116, 'Thresholds: 40% Consent/Muster | 50% Brokerage', lit_threshold_tip),
    row('rip_gov_lit_reviews', 144, 'Active Resolution: ' + rev_active, rev_active_tip),
    row('rip_gov_lit_lockout', 168, 'Shared Lockout: ' + rev_lockout, rev_lockout_tip),
    row('rip_gov_lit_note', 194, 'Review Term: 10 Years | 50 Ducats + 50 Power', rev_terms_tip),
    row('rip_gov_lit_footer', 224, 'One resolution binds all institutions.', rev_why_tip)
]

# --- Volhynia: Magnate Senate (VLN) ---
vln_consent = choice('RipGovVlnConsent', [
    ('has_country_modifier = vln_senate_convened', '§GConvened (+2 Legitimacy)§!')
], '§YNot Convened§!')
vln_banners = choice('RipGovVlnBanners', [
    ('has_country_modifier = vln_magnate_banners_mustered', '§YBanners Mustered§!'),
    ('is_at_war = yes has_country_modifier = vln_senate_convened', '§GReady (Will Consume Senate)§!'),
    ('has_country_modifier = vln_senate_convened', '§YNeeds War§!')
], '§RRequires Convened Senate§!')
vln_buyoff = choice('RipGovVlnBuyoff', [
    ('has_country_modifier = vln_magnate_house_bought', '§GHouse Appeased§!')
], 'Available (0.50 Income, +15 Autonomy)')

vln_consent_tip = 'Senate Consent:\nSummon the Senate costs 0.25 years of income and grants +2 Legitimacy for 5 years (8-year cooldown).\nConvening the Senate is required before calling up the Magnate Banners.'
vln_banners_tip = 'Call Up the Magnate Banners:\nDuring wartime, calling up the banners instantly CONSUMES the convened Senate, granting +10% maximum manpower, +3 Army Tradition, and a 5-year defensive boost (10-year cooldown).'
vln_buyoff_tip = 'Buy Off a Magnate House:\nCosts 0.50 years of income and adds 15 autonomy in a non-capital city to reduce local unrest by -5 and grant 5 years of stability bonus.'
vln_threshold_tip = 'Volhynian Treasury Planning:\n- Summon Senate: 0.25 years of income\n- Appease House: 0.50 years of income\nEnsure adequate reserves before war to convene the Senate in time.'

vln_rows = [
    row('rip_gov_vln_title', 12, '§YVolhynia: Magnate Senate§!', vln_consent_tip),
    row('rip_gov_vln_consent', 38, 'Senate Consent: ' + vln_consent, vln_consent_tip),
    row('rip_gov_vln_banners', 64, 'Magnate Banners: ' + vln_banners, vln_banners_tip),
    row('rip_gov_vln_buyoff', 90, 'Magnate House: ' + vln_buyoff, vln_buyoff_tip),
    row('rip_gov_vln_threshold', 116, 'Cost: 0.25 yr (Senate) | 0.50 yr (House)', vln_threshold_tip),
    row('rip_gov_vln_reviews', 144, 'Active Resolution: ' + rev_active, rev_active_tip),
    row('rip_gov_vln_lockout', 168, 'Shared Lockout: ' + rev_lockout, rev_lockout_tip),
    row('rip_gov_vln_note', 194, 'Review Term: 10 Years | 50 Ducats + 50 Power', rev_terms_tip),
    row('rip_gov_vln_footer', 224, 'One resolution binds all institutions.', rev_why_tip)
]

# --- Standalone Shared Institutional Reviews Panel ---
reviews_rows = [
    row('rip_gov_rev_title', 12, '§YInstitutional Resolutions§!', rev_why_tip),
    row('rip_gov_rev_active', 42, 'Active Policy: ' + rev_active, rev_active_tip),
    row('rip_gov_rev_lockout', 72, 'Shared Lockout: ' + rev_lockout, rev_lockout_tip),
    row('rip_gov_rev_access', 104, 'Available Tracks: ' + rev_tracks, rev_tracks_tip),
    row('rip_gov_rev_terms', 136, 'Cost: 50 Ducats + 50 Power | 10-Yr Term', rev_terms_tip),
    row('rip_gov_rev_why', 168, 'One resolution binds all three institutions.', rev_why_tip),
    row('rip_gov_rev_reform_note', 200, 'Reform loss clears policy but retains 10-yr lock.', rev_reform_note_tip)
]

hlc_potential = 'NOT = { tag = KRU } NOT = { has_reform = kyivan_cesarstvo_reform } OR = { tag = HLC has_reform = hlc_galician_voivodeship_reform has_reform = hlc_crown_authority_reform }'
lit_potential = 'NOT = { tag = KRU } NOT = { has_reform = kyivan_cesarstvo_reform } NOT = { tag = HLC } NOT = { has_reform = hlc_galician_voivodeship_reform } NOT = { has_reform = hlc_crown_authority_reform } OR = { tag = LIT has_reform = grand_duchy_reform has_reform = lit_union_of_two_nations_reform has_reform = lit_separate_crown_reform }'
vln_potential = 'NOT = { tag = KRU } NOT = { has_reform = kyivan_cesarstvo_reform } NOT = { tag = HLC } NOT = { has_reform = hlc_galician_voivodeship_reform } NOT = { has_reform = hlc_crown_authority_reform } NOT = { tag = LIT } NOT = { has_reform = grand_duchy_reform } NOT = { has_reform = lit_union_of_two_nations_reform } NOT = { has_reform = lit_separate_crown_reform } OR = { tag = VLN has_reform = vln_voivodeship_reform } NOT = { has_reform = vln_cossack_host_reform }'
reviews_potential = 'NOT = { tag = KRU } NOT = { has_reform = kyivan_cesarstvo_reform } NOT = { tag = HLC } NOT = { has_reform = hlc_galician_voivodeship_reform } NOT = { has_reform = hlc_crown_authority_reform } NOT = { tag = LIT } NOT = { has_reform = grand_duchy_reform } NOT = { has_reform = lit_union_of_two_nations_reform } NOT = { has_reform = lit_separate_crown_reform } NOT = { tag = VLN } NOT = { has_reform = vln_voivodeship_reform } OR = { rip_gov_has_municipal_review = yes rip_gov_has_chancery_review = yes rip_gov_has_register_review = yes has_country_modifier = rip_gov_municipal_charters has_country_modifier = rip_gov_municipal_accounts has_country_modifier = rip_gov_chancery_service has_country_modifier = rip_gov_chancery_rights has_country_modifier = rip_gov_register_muster has_country_modifier = rip_gov_register_settlement has_country_flag = rip_gov_review_recent }'

PANELS = [
    ('rip_gov_kru_panel', kru_potential, kru_rows),
    ('rip_gov_cesar_panel', 'has_reform = kyivan_cesarstvo_reform', cesar_rows),
    ('rip_gov_hlc_panel', hlc_potential, hlc_rows),
    ('rip_gov_lit_panel', lit_potential, lit_rows),
    ('rip_gov_vln_panel', vln_potential, vln_rows),
    ('rip_gov_reviews_panel', reviews_potential, reviews_rows)
]
PANEL_NAMES = [name for name, _, _ in PANELS]

# Insert within the native supported root window, after its existing widgets.
def close_brace(text, start):
    depth = 0
    for i in range(start,len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
    raise ValueError('Unclosed native window')

native = (GAME/'interface/countrygovernmentview.gui').read_text(encoding='utf-8-sig')
pos = native.index('name = "countrygovernmentview"')
start = native.rfind('{',0,pos)
end = close_brace(native,start)
gui = native[:end] + '\n# Generated read-only RIP government explanations.\n' + '\n'.join(panel(name, pot, rows) for name, pot, rows in PANELS) + '\n' + native[end:]
outputs = {'interface/rip_government_status.gfx': 'spriteTypes = { corneredTileSpriteType = { name = GFX_rip_government_status_bg size = { x = 470 y = 290 } texturefile = '+chr(34)+'gfx/interface/small_tiles_dialog.dds'+chr(34)+' borderSize = { x = 8 y = 8 } } }\n', 'interface/countrygovernmentview.gui': gui, 'common/custom_gui/rip_government_status.txt':'\n'.join(CONTROLS)+'\n', 'customizable_localization/rip_government_status.txt':'\n'.join(DYNAMIC)+'\n'}
for language in ('english','french','german','spanish'):
    outputs[f'localisation/replace/zzzz_RIP_government_status_l_{language}.yml'] = 'l_'+language+':\n'+'\n'.join(f' {k}:0 "{v.replace(chr(10), chr(92)+"n")}"' for k,v in LOC.items())+'\n'

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for rel,content in outputs.items():
        data=content.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8-sig' if rel.endswith('.yml') else 'utf-8')
        path=ROOT/rel
        if args.check:
            assert path.exists() and path.read_bytes()==data, f'Stale generated file: {rel}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    print(f'Government status UI: {len(outputs)} outputs '+('verified' if args.check else 'written'))
if __name__ == '__main__': main()