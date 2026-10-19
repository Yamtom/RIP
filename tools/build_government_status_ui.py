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

factions = [('knyazi', 'Knyazi'), ('boyary', 'Boyary'), ('starshyna', 'Starshyna')]
# The Rada (tools/build_kru_rada.py): the dominant bloc - the faction in power - stands on the RIGHT of the States General bar, the bloc that is second by
# influence on the LEFT; the third bloc is the opposition. The refresh keeps kru_rada_lead_<bloc> and kru_rada_second_<bloc> for the pair: the reform and the
# bar follow those flags, so the rows read them too.
leader = choice('RipGovRadaLeader', [(f'has_country_flag = kru_rada_lead_{f}', f'§G{n}§!') for f, n in factions], '§YNot set yet§!')
second = choice('RipGovRadaSecond', [(f'has_country_flag = kru_rada_second_{f}', f'§G{n}§!') for f, n in factions], '§YNot set yet§!')
opposition = choice('RipGovRadaOpposition', [(f'has_country_flag = kru_rada_second_{a} has_country_flag = kru_rada_lead_{b}', f'§G{n}§!')
                                              for a, b, n in (('knyazi', 'boyary', 'Starshyna'), ('boyary', 'knyazi', 'Starshyna'), ('knyazi', 'starshyna', 'Boyary'),
                                                              ('starshyna', 'knyazi', 'Boyary'), ('boyary', 'starshyna', 'Knyazi'), ('starshyna', 'boyary', 'Knyazi'))], '§YNot set yet§!')
bar = choice('RipGovRadaBar', [('kru_leader_influence_60 = yes', 'Right, three quarters (leader at 60+)'),
                               ('kru_leader_influence_55 = yes', 'Right, a half (leader at 55+)'),
                               ('kru_leader_influence_50 = yes', 'Right, a quarter (leader at 50+)')], 'Centre (leader under 50: contested)')
voice = choice('RipGovJuniorVoice', [(f'has_country_modifier = KRU_junior_{f}', n) for f, n in factions], 'None')
coalition_tip = ('The States General bar (Res Publica or Winds of Change) shows the two blocs that lead the rada: the bloc that is SECOND by influence stands on the LEFT, '
                 'the dominant bloc - the faction in power - on the RIGHT. The third bloc is the opposition and is not on the bar.\n'
                 'When the pair changes, the rada swaps to the reform that has it: six reform ids, one government called Rada of Three Estates.\n'
                 'The bar is centred while the leader has under 50 influence and moves right by a quarter, a half and three quarters at 50, 55 and 60; the bloc on the side in power '
                 'gives its floor modifiers. The leader also keeps the vanilla faction-in-power modifier. The runner-up keeps a junior voice from 38 influence.\n'
                 'The record refreshes every month and after every court ability. Without Res Publica or Winds of Change the pair, the faction panel and the abilities work, but there is no bar.')
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
kru_rows = [row('rip_gov_kru_title',12,'§YRada of Three Estates§!',coalition_tip), row('rip_gov_kru_leader',40,'Right (leads): '+leader,coalition_tip),
            row('rip_gov_kru_second',64,'Left (second): '+second,coalition_tip), row('rip_gov_kru_opposition',88,'Opposition: '+opposition,coalition_tip),
            row('rip_gov_kru_bar',112,'Bar: '+bar,coalition_tip), row('rip_gov_kru_voice',136,'Junior voice: '+voice,coalition_tip),
            row('rip_gov_kru_decay',168,'Decadence: §Y[Root.ruthenian_decadence.GetValue]§!',annual_tip), row('rip_gov_kru_annual',196,'Yearly change: hover for active factors',annual_tip),
            row('rip_gov_kru_crisis',224,'Crisis: 90+ | Retreat: <75 | End: <60, stability +1',crisis_tip)]
kru_potential = 'tag = KRU kru_holds_rada_reform = yes'

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

# --- Institutional resolutions (Municipal, Chancery, Register) -------------------------------------------------------
# The six buttons are in common/government_mechanics/rip_institutional_resolutions.txt, in the mechanics box on the left of this window. The rows
# below say what each button does right now and why it can or cannot be pressed, and are the same in every panel that carries them. A row for an
# institution the country does not hold is empty, so one block serves every combination of institutions.
RESOLUTIONS = [
    # key, who holds the institution, button text, power, power test, modifier, modifier name
    ('MunicipalCharters', 'rip_gov_has_municipal_review = yes', 'Confirm the Municipal Charters', 'DIP', 'dip_power = 50', 'rip_gov_municipal_charters', 'Confirmed Municipal Charters'),
    ('MunicipalAccounts', 'rip_gov_has_municipal_review = yes', 'Examine the Municipal Accounts', 'ADM', 'adm_power = 50', 'rip_gov_municipal_accounts', 'Examined Municipal Accounts'),
    ('ChanceryService', 'rip_gov_has_chancery_review = yes', 'Examine the Service Rolls', 'ADM', 'adm_power = 50', 'rip_gov_chancery_service', 'Examined Service Rolls'),
    ('ChanceryRights', 'rip_gov_has_chancery_review = yes', 'Confirm the Local Rights', 'DIP', 'dip_power = 50', 'rip_gov_chancery_rights', 'Confirmed Local Rights'),
    ('RegisterMuster', 'rip_gov_has_register_review = yes', 'Fund the Full Muster', 'MIL', 'mil_power = 50', 'rip_gov_register_muster', 'Funded Cossack Muster'),
    ('RegisterSettlement', 'rip_gov_has_register_review = yes', 'Settle the Service Obligations', 'DIP', 'dip_power = 50', 'rip_gov_register_settlement', 'Settled Cossack Obligations'),
]


def resolution_state(key, held, label, power, power_test, modifier):
    """One button's line: its name and price, then the first reason that applies (the same order the button's own tooltip checks)."""
    states = [(f'has_country_modifier = {modifier}', '§GIn force§!'),
              ('rip_gov_resolution_in_force = yes', '§YAnother resolution in force§!'),
              ('NOT = { rip_gov_resolution_lock_over = yes }', '§RLocked for ten years§!'),
              ('is_at_war = yes', '§RAt war§!'),
              ('NOT = { stability = 0 }', '§RStability below 0§!'),
              ('NOT = { treasury = 50 }', '§RNeeds 50 ducats§!'),
              (f'NOT = {{ {power_test} }}', f'§RNeeds 50 {power}§!')]
    head = f'{label} (50 {power}): '
    return choice('RipGovRes' + key, [(f'NOT = {{ {held} }}', '')] + [(trigger, head + shown + '\n') for trigger, shown in states], head + '§GReady§!\n')


res_lines = ''.join(resolution_state(key, held, label, power, power_test, modifier) for key, held, label, power, power_test, modifier, _ in RESOLUTIONS)
res_name = choice('RipGovResName', [(f'has_country_modifier = {modifier}', f'§G{name}§!') for _, _, _, _, _, modifier, name in RESOLUTIONS]
                  + [('NOT = { rip_gov_resolution_lock_over = yes }', '§YNone in force§!')], '§GNone in force§!')
res_left = choice('RipGovResLeft', [('rip_gov_resolution_lock_over = yes', '§GReady for a new resolution§!')]
                  + [(f'had_country_flag = {{ flag = rip_gov_review_recent days = {365 * gone} }}',
                      f'Next resolution in §Y{10 - gone}§! year' + ('' if 10 - gone == 1 else 's')) for gone in range(9, 0, -1)],
                  'Next resolution in §Y10§! years')
res_peace = choice('RipGovResPeace', [('is_at_war = yes', '§RAt war§!')], '§GAt peace§!')
res_stability = choice('RipGovResStability', [('NOT = { stability = 0 }', '§RStability below 0§!')], '§GStability 0+§!')
res_treasury = choice('RipGovResTreasury', [('NOT = { treasury = 50 }', '§RUnder 50 ducats§!')], '§G50 ducats§!')

res_title_tip = ('Institutional resolutions: the towns\' charters, the chancery\'s rolls and the Cossack register can each pass one paid resolution of ten years, '
                 'and only one resolution can stand in the whole realm.\nThe buttons are in the government mechanics box on the left of this window; '
                 'their tooltips say what each one costs, what it does and why it is refused.')
res_now_tip = ('The resolution in force, if any. A resolution ends after ten years, or at once if the reform that gave it is removed; '
               'the ten-year term still runs on and no other resolution can be passed until it is over.')
res_needs_tip = ('To pass a resolution you need:\n- peace\n- stability of at least 0\n- 50 ducats, which are paid\n- 50 monarch power of the kind named on the button, which is paid\n'
                 '- no other resolution in force, and ten years since the last one.\nGreen is met, red is not.')
res_lines_tip = ('What each button does, for ten years:\n'
                 '- Confirm the Municipal Charters (50 DIP): +5% production efficiency, +5% burghers\' loyalty, -5 maximum absolutism\n'
                 '- Examine the Municipal Accounts (50 ADM): +5% national tax, -0.025 yearly corruption, -5% burghers\' loyalty\n'
                 '- Examine the Service Rolls (50 ADM): -5% state maintenance, -0.025 yearly corruption, -5% nobles\' loyalty\n'
                 '- Confirm the Local Rights (50 DIP): -10% culture promotion cost, -0.5 national unrest, -5% national tax\n'
                 '- Fund the Full Muster (50 MIL): +5% manpower recovery, +5% land maintenance\n'
                 '- Settle the Service Obligations (50 DIP): -0.5 national unrest, -5% national manpower')
res_hint_tip = 'The two buttons are in the mechanics box on the left, under the government description. The bottom row may need the mouse wheel.'


def resolution_block(prefix, y, step):
    """Five rows: what is in force, how long the term runs, what is needed, where the buttons are, and one line per button held."""
    return [row(f'rip_gov_{prefix}_res_now', y, 'In force: ' + res_name, res_now_tip),
            row(f'rip_gov_{prefix}_res_left', y + step, res_left, res_now_tip),
            row(f'rip_gov_{prefix}_res_needs', y + 2 * step, 'Needs: ' + res_peace + ' | ' + res_stability + ' | ' + res_treasury, res_needs_tip),
            row(f'rip_gov_{prefix}_res_hint', y + 3 * step, 'Buttons: mechanics box, left.', res_hint_tip),
            row(f'rip_gov_{prefix}_res_lines', y + 4 * step, res_lines, res_lines_tip, height=132)]


# --- Galicia: the six crown ordinances (Frontier Crown Authority) -------------------------------------------------------
ORDINANCES = [
    # key, label, power, power test, modifier, what it does
    ('Chancery', 'Chancery', 'DIP', 'dip_power = 50', 'hlc_chancery_ordinance_modifier', '+1 diplomatic reputation, +10% improve relations, +10% advisor costs'),
    ('Settlement', 'Settlement', 'ADM', 'adm_power = 50', 'hlc_settlement_ordinance_modifier', '-10% culture conversion cost, +1 national unrest; the first manual conversion in a year steadies the nobles'),
    ('Cadastral', 'Cadastral', 'ADM', 'adm_power = 50', 'hlc_cadastral_ordinance_modifier', '+5% national tax, -5% nobles\' loyalty'),
    ('Urbarial', 'Urbarial', 'ADM', 'adm_power = 50', 'hlc_urbarial_ordinance_modifier', '-0.5 national unrest, +5% national manpower, -5% nobles\' loyalty'),
    ('Toleration', 'Toleration', 'DIP', 'dip_power = 50', 'hlc_toleration_ordinance_modifier', '+1 tolerance of heretics and heathens, -0.5 national unrest, -5% church loyalty'),
    ('Frontier', 'Frontier Guard', 'MIL', 'mil_power = 50', 'hlc_frontier_ordinance_modifier', '+10% defensiveness, +1 hostile attrition, +5% land maintenance'),
]
hlc_modifiers = ' '.join(f'has_country_modifier = {modifier}' for _, _, _, _, modifier, _ in ORDINANCES)
hlc_slots = choice('RipGovHlcSlots', [
    ('NOT = { hlc_ordinance_slot_free = yes }', '§Y3 / 3 (full)§!'),
    ('calc_true_if = { ' + hlc_modifiers + ' amount = 2 }', '§G2 / 3 (1 free)§!'),
    ('calc_true_if = { ' + hlc_modifiers + ' amount = 1 }', '§G1 / 3 (2 free)§!')], '§G0 / 3 (3 free)§!')
hlc_slots_tip = ('Ordinance slots: the crown keeps at most three of its six ordinances in force (hlc_ordinance_slot_free). Each ordinance costs 50 monarch power of the kind '
                 'named, stands for ten years and cannot be enacted again before its term ends; the crown cannot take one back. '
                 'A slot opens when an ordinance runs out or the crown authority is lost.')


def ordinance_state(key, label, power, power_test, modifier):
    return choice('RipGovOrd' + key, [(f'has_country_modifier = {modifier}', '§GIn force§!'),
                                      ('NOT = { hlc_ordinance_slot_free = yes }', '§YSlots full§!'),
                                      (f'NOT = {{ {power_test} }}', f'§RNeeds 50 {power}§!')], '§GReady§!')


hlc_crown_rows = [row('rip_gov_hlc_crown_title', 12, '§YFrontier Crown: Six Ordinances§!', hlc_slots_tip),
                  row('rip_gov_hlc_crown_slots', 38, 'Slots in use: ' + hlc_slots, hlc_slots_tip)]
for index, (key, label, power, power_test, modifier, effect) in enumerate(ORDINANCES):
    hlc_crown_rows.append(row(f'rip_gov_hlc_crown_{key.lower()}', 64 + 26 * index, f'{label} (50 {power}): ' + ordinance_state(key, label, power, power_test, modifier),
                              f'{label} Ordinance - for ten years: {effect}.\nCosts 50 {power} power. At most three of the six can be in force; none can be taken back.'))
hlc_crown_rows.append(row('rip_gov_hlc_crown_hint', 226, 'Buttons: mechanics box, left.', 'The six ordinance buttons are in the mechanics box on the left, two rows of three. The bottom row may need the mouse wheel.'))

# --- Galicia: the Boyar Council (the Polish fork of the voivodeship) ------------------------------------------------------
hlc_council = choice('RipGovHlcCouncil', [
    ('has_country_modifier = hlc_boyars_confirmed', '§GOffices Confirmed (Co-option)§!'),
    ('has_country_modifier = hlc_foreign_claimant_countered', '§GDynastic Defense§!'),
    ('has_country_modifier = hlc_boyars_made_example', '§GRepression of Defiant Boyar§!')
], 'No active course')

hlc_session = choice('RipGovHlcSession', [
    ('OR = { has_country_modifier = hlc_boyars_confirmed has_country_modifier = hlc_foreign_claimant_countered has_country_modifier = hlc_boyars_made_example }', '§RIn Session (10-Yr Lock)§!')
], '§GReady to Convene§!')

hlc_council_tip = 'Active Boyar Council course:\n- Co-option (Confirm in Office): +10 Noble Loyalty for 10 years (available below 60% loyalty)\n- Dynastic Defense (Counter Claimant): +3 Legitimacy for 10 years (available below 60% legitimacy)\n- Repression (Make an Example): +3 Army Tradition, -5 Noble Loyalty for 7 years (at peace, loyalty < 40%)'
hlc_session_tip = 'Shared 10-year session lockout:\nThe Boyar Council courses share a single 10-year cooldown token (hlc_boyar_council_session).\nChoosing any course convenes the council and locks all other courses for 10 years because co-option, dynastic defence, and repression compete rather than stack as independent tools.'

hlc_rows = [
    row('rip_gov_hlc_title', 12, '§YGalicia: Boyar Council§!', hlc_council_tip),
    row('rip_gov_hlc_council', 38, 'Council Course: ' + hlc_council, hlc_council_tip),
    row('rip_gov_hlc_session', 64, 'Council Session: ' + hlc_session, hlc_session_tip),
    row('rip_gov_hlc_hint', 92, 'Buttons: mechanics box, left.', 'The three council buttons are in the mechanics box on the left, under the government description.')
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
] + resolution_block('lit', 142, 24)

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
] + resolution_block('vln', 142, 24)

# --- The standalone Institutional Resolutions panel (every country that has a resolution and no panel of its own) ---
reviews_rows = [row('rip_gov_rev_title', 12, '§YInstitutional Resolutions§!', res_title_tip)] + resolution_block('rev', 40, 26)

base_excluded = 'NOT = { tag = KRU } NOT = { has_reform = kyivan_cesarstvo_reform }'
hlc_crown_potential = base_excluded + ' has_reform = hlc_crown_authority_reform'
hlc_potential = base_excluded + ' NOT = { has_reform = hlc_crown_authority_reform } OR = { tag = HLC has_reform = hlc_galician_voivodeship_reform }'
no_galicia = 'NOT = { tag = HLC } NOT = { has_reform = hlc_galician_voivodeship_reform } NOT = { has_reform = hlc_crown_authority_reform }'
lit_potential = base_excluded + ' ' + no_galicia + ' OR = { tag = LIT has_reform = grand_duchy_reform has_reform = lit_union_of_two_nations_reform has_reform = lit_separate_crown_reform }'
vln_potential = (base_excluded + ' ' + no_galicia + ' NOT = { tag = LIT } NOT = { has_reform = grand_duchy_reform } NOT = { has_reform = lit_union_of_two_nations_reform } '
                 'NOT = { has_reform = lit_separate_crown_reform } OR = { tag = VLN has_reform = vln_voivodeship_reform } NOT = { has_reform = vln_cossack_host_reform }')
reviews_potential = (base_excluded + ' ' + no_galicia + ' NOT = { tag = LIT } NOT = { has_reform = grand_duchy_reform } NOT = { has_reform = lit_union_of_two_nations_reform } '
                     'NOT = { has_reform = lit_separate_crown_reform } NOT = { tag = VLN } NOT = { has_reform = vln_voivodeship_reform } '
                     'OR = { rip_gov_has_municipal_review = yes rip_gov_has_chancery_review = yes rip_gov_has_register_review = yes rip_gov_resolution_in_force = yes has_country_flag = rip_gov_review_recent }')

PANELS = [
    ('rip_gov_kru_panel', kru_potential, kru_rows),
    ('rip_gov_cesar_panel', 'has_reform = kyivan_cesarstvo_reform', cesar_rows),
    ('rip_gov_hlc_crown_panel', hlc_crown_potential, hlc_crown_rows),
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