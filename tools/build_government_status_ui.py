"""Build read-only government explanations from native EU4 custom GUI contracts.
Uses the installed 1.37 government window; --check verifies deterministic output.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from custom_localization_layout import split_custom_localization
import argparse
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import vanilla_root
GAME = vanilla_root()
if GAME is None:
    raise SystemExit('BLOCKED: government UI generation requires the supported vanilla version; set EU4_DIR to an unpacked 1.37 installation')
LOC = {}
DYNAMIC = []
CONTROLS = []
GEOMETRY = {}   # window name -> (y, height, background sprite); the status panels keep the default

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

def row(name, y, text, tip, height=22, x=18, width=434, font='vic_18', potential='always = yes'):
    loc(name, text)
    loc(name + '_tt', tip)
    CONTROLS.append(f'custom_text_box = {{ name = {name} potential = {{ {potential} }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{ name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}" text = "{name}" maxWidth = {width} maxHeight = {height} format = left }}'''

def panel(name, potential, rows):
    CONTROLS.append(f'custom_window = {{ name = {name} potential = {{ {potential} }} }}')
    y, height, sprite = GEOMETRY.get(name, (12, 320, 'GFX_rip_government_status_bg'))
    return f'''windowType = {{ name = "{name}" scripted = yes position = {{ x=550 y={y} }} size = {{ x=470 y={height} }} moveable = 0
 iconType = {{ name = "background" spriteType = "{sprite}" position = {{ x=0 y=0 }} }}
 {chr(10).join(rows)}
}}'''

factions = [('knyazi', 'Knyazi'), ('boyary', 'Boyary'), ('starshyna', 'Starshyna')]
# The Rada (tools/build_kru_rada.py): the dominant bloc - the faction in power - stands on the RIGHT of the States General bar, the bloc that is second by
# influence on the LEFT; the third bloc is the opposition. The refresh keeps kru_rada_lead_<bloc> and kru_rada_second_<bloc> for the pair: the reform and the
# bar follow those flags, so the rows read them too.
leader = choice('RipGovRadaLeader', [(f'has_country_flag = kru_rada_lead_{f}', f'§G{n}§!') for f, n in factions], '§YSet at the next monthly review§!')
second = choice('RipGovRadaSecond', [(f'has_country_flag = kru_rada_second_{f}', f'§G{n}§!') for f, n in factions], '§YSet at the next monthly review§!')
opposition = choice('RipGovRadaOpposition', [(f'has_country_flag = kru_rada_second_{a} has_country_flag = kru_rada_lead_{b}', f'§G{n}§!')
                                              for a, b, n in (('knyazi', 'boyary', 'Starshyna'), ('boyary', 'knyazi', 'Starshyna'), ('knyazi', 'starshyna', 'Boyary'),
                                                              ('starshyna', 'knyazi', 'Boyary'), ('boyary', 'starshyna', 'Knyazi'), ('starshyna', 'boyary', 'Knyazi'))], '§YSet at the next monthly review§!')
bar = choice('RipGovRadaBar', [('kru_leader_influence_60 = yes', 'Right, three quarters (leader at 60+)'),
                               ('kru_leader_influence_55 = yes', 'Right, a half (leader at 55+)'),
                               ('kru_leader_influence_50 = yes', 'Right, a quarter (leader at 50+)')], 'Centre (leader under 50: contested)')
voice = choice('RipGovJuniorVoice', [(f'has_country_modifier = KRU_junior_{f}', n) for f, n in factions], 'None')
coalition_tip = ('The balance bar shows the two blocs that lead the rada: the bloc that is SECOND by influence stands on the LEFT, '
                 'the dominant bloc - the faction in power - on the RIGHT. The third bloc is the opposition and is not on the bar.\n'
                 'When the leading pair changes, the Rada shifts to the standing held by that pair under the Rada of Three Estates.\n'
                 'The bar is centred while the leader has under 50 influence and moves right by a quarter, a half and three quarters at 50, 55 and 60; the bloc on the side in power '
                 'gives its floor modifiers. The leader also keeps its faction-in-power standing. The runner-up keeps a junior voice from 38 influence.\n'
                 'The record refreshes every month and after every court ability. Where no Estates balance bar is active, the leading pair, the faction council and the court abilities still govern the realm.')
annual = [
 ('StabZero','stability = 0 NOT = { stability = 1 }',2,'stability = 0'),
 ('StabBad','NOT = { stability = 0 }',3,'stability < 0'),
 ('War','is_at_war = yes',1,'at war'),
 ('Loans','num_of_loans = 5',1,'at least 5 loans'),
 ('Autonomy','average_autonomy = 40',1,'average autonomy at least 40%'),
 ('Legitimacy','NOT = { legitimacy = 50 }',1,'legitimacy below 50'),
 ('StabGood','stability = 2',-3,'stability at least +2'),
 ('Peace','is_at_war = no',-2,'at peace')]
# The decadence number is a country variable that the first yearly review creates (events/RIP_KRU_RuthenianDecadence.txt, rip_decadence_initialized).
# Printing it with [Root.ruthenian_decadence.GetValue] FAILS while the variable does not exist: measured in EU4 1.37.5, the row showed nothing and the
# engine wrote "Unknown text property 'GetValue]..." once per frame (9.3 million lines, 1 GB, in five hours with the window open). A defined_text ladder
# reads a missing variable as "no", so it never errors; the colours follow the panel's own thresholds (crisis from 90, retreat below 75).
decadence_shown = choice('RipGovDecadence',
    [(f'check_variable = {{ which = ruthenian_decadence value = {i} }}', f'§{"R" if i >= 90 else "Y" if i >= 75 else "G"}{i}§!') for i in range(100, 0, -1)]
    + [('has_country_flag = rip_decadence_initialized', '§G0§!')],
    '§YNot started: it begins at 20 at the first yearly review§!')
annual_text = '\n'.join(factor('RipGov'+n,t,v,l) for n,t,v,l in annual)
annual_tip = 'Yearly change in Decadence under present conditions. Add the coloured values below. Court events may also raise or lower Decadence.\n' + annual_text + '\nAt the first yearly review, Decadence starts at 20 before the adjustments listed above. Its effects change at 40 and again at 70.'
crisis_tip = 'Court Crisis can start accumulating while the Kyivan Confederation holds this reform, faces no other disaster, and Decadence reaches at least 90. Base monthly progress at 90+: +6; frontier centralisation +1.5, frontier liberties -1, southern recovery -1. Progress recedes below 75. An active crisis ends only when Decadence is below 60 AND stability is at least +1.\nThe first time a yearly review puts Decadence at 90 or higher, the court may offer a way to reduce it. The disaster begins only when its progress is full.'
kru_potential = 'tag = KRU kru_holds_rada_reform = yes'

def share(var, name):
    return choice(name, [(f'check_variable = {{ which = {var} value = {i/100:g} }}', f'{i}%') for i in range(100,0,-1)], '0%')
minority = share('rip_cesar_minority_share', 'RipGovMinorityShare')
excluded = share('rip_cesar_excluded_share', 'RipGovExcludedShare')
eligible = choice('RipGovIntegration', [('rip_cesar_integration_eligible = yes','§GEligible§!')], '§RNot eligible§!')
breakdown = choice('RipGovBreakdown', [('has_country_flag = rip_cesar_breakdown','§RBreakdown active§!')], 'No active breakdown')
lands_tip = 'Shares use total development of ALL owned provinces, including territories; subjects are excluded. The census updates monthly. Displayed whole percentages are rounded down; thresholds use the exact share.\nNon-primary: provinces whose culture differs from the owner\'s primary culture. Unaccepted: the subset of those provinces whose culture the crown does not recognize as accepted. Accepted cultures within our cultural union follow imperial union standing.\nConquest, development, province loss, culture conversion and changes in accepted or primary culture alter these shares at the next census. Promoting a culture can reduce the unaccepted share without reducing the non-primary share.'
elig_tip = 'Integration requires ALL three: at least one owned non-primary province with an owner-accepted culture; at least one accepted culture; non-primary development at least 10%. A cultural union alone does not waive the accepted-culture requirement.\nThree accepted cultures add growth only while these requirements hold. Development matters, not the number of provinces.'
power = lambda p,v: f'has_government_power = {{ mechanic_type = {p}_mechanic power_type = {p} value = {v} }}'
concord = 'kyivan_throne_concord'; gathering = 'kyivan_peoples_gathering'
concord_factors = [('Stable','stability = 2',.1,'stability at least +2'),('Unstable','NOT = { stability = 0 }',-.2,'negative stability'),('Legit','legitimacy = 80',.2,'legitimacy at least 80'),('Illegit','NOT = { legitimacy = 40 }',-.25,'legitimacy below 40'),('Subjects','any_subject_country = { liberty_desire = 50 }',-.3,'any subject at 50% liberty desire'),('Compact',power(gathering,60)+' rip_cesar_integration_eligible = yes',.15,'Gathering at least 60 and integration eligible'),('Excluded','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.3,'unaccepted share at least 30%')]
gather_factors = [('Eligible','rip_cesar_integration_eligible = yes',.3,'integration eligible'),('Cultures','rip_cesar_integration_eligible = yes num_accepted_cultures = 3',.15,'eligible and at least 3 accepted cultures'),('Minority','rip_cesar_integration_eligible = yes check_variable = { which = rip_cesar_minority_share value = 0.3 }',.15,'eligible and non-primary share at least 30%'),('Throne','rip_cesar_integration_eligible = yes '+power(concord,60),.1,'eligible and Concord at least 60'),('Excluded15','check_variable = { which = rip_cesar_excluded_share value = 0.15 }',-.25,'unaccepted share at least 15%'),('Excluded30','check_variable = { which = rip_cesar_excluded_share value = 0.3 }',-.35,'unaccepted share at least 30% (stacks with 15%)'),('WeakThrone','NOT = { '+power(concord,30)+' }',-.2,'Concord below 30'),('Exhausted','war_exhaustion = 5',-.15,'war exhaustion at least 5'),('Ineligible','NOT = { rip_cesar_integration_eligible = yes }',-.5,'integration not eligible')]
concord_tip = 'Monthly Concord: base +0.10, plus active values below.\n'+'\n'.join(factor('CesarConcord'+n,t,v,l) for n,t,v,l in concord_factors)+'\nAt zero Concord, Throne in Disarray lasts 1825 days.'
gather_tip = 'Monthly Gathering: base 0, plus active values below.\n'+'\n'.join(factor('CesarGather'+n,t,v,l) for n,t,v,l in gather_factors)+'\nAt 100: a 3650-day compact, +10 prestige and +10 Concord; Gathering resets to 40. This reset is not a breakdown.'
recovery_tip = 'Each month, if cultures the crown has yet to accept account for at least 30% of development and Gathering is below 20, the court loses 15 Concord and suffers Throne in Disarray for 1825 days. This loss occurs once per crisis.\nThe crisis ends once unaccepted development falls below 15% and Gathering reaches 40. Throne in Disarray lasts its full term. It can also take effect when Concord falls to zero.'

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
    short = {'Confirm the Municipal Charters': 'Town charters', 'Examine the Municipal Accounts': 'Town accounts',
             'Examine the Service Rolls': 'Service rolls', 'Confirm the Local Rights': 'Local rights',
             'Fund the Full Muster': 'Full muster', 'Settle the Service Obligations': 'Service obligations'}
    head = f'{short[label]} (50 ducats + 50 {power}): '
    return choice('RipGovRes' + key, [(f'NOT = {{ {held} }}', '')] + [(trigger, head + shown + '\n') for trigger, shown in states], head + 'Check button\n')


res_name = choice('RipGovResName', [(f'has_country_modifier = {modifier}', f'§Y{name}§!') for _, _, _, _, _, modifier, name in RESOLUTIONS]
                  + [('NOT = { rip_gov_resolution_lock_over = yes }', 'None')], 'None')
res_left = choice('RipGovResLeft', [('rip_gov_resolution_lock_over = yes', 'Term complete')]
                  + [(f'had_country_flag = {{ flag = rip_gov_review_recent days = {365 * gone} }}',
                      f'Next resolution in §Y{10 - gone}§! year' + ('' if 10 - gone == 1 else 's')) for gone in range(9, 0, -1)],
                  'Next resolution in §Y10§! years')

res_title_tip = ('Institutional resolutions: the towns\' charters, the chancery\'s rolls and the Cossack register can each pass one paid resolution of ten years, '
                 'and only one resolution can stand in the whole realm.\nChoose a resolution on the left. '
                 'Hover over a resolution to see its cost, effects and requirements.')
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
hlc_slots_tip = ('Ordinance slots: the crown keeps at most three of its six ordinances in force. Each ordinance costs 50 monarch power of the kind '
                 'named, stands for ten years and cannot be enacted again before its term ends; the crown cannot take one back. '
                 'A slot opens when an ordinance runs out or the crown authority is lost.')


def ordinance_state(key, label, power, power_test, modifier):
    return choice('RipGovOrd' + key, [(f'has_country_modifier = {modifier}', '§GIn force§!'),
                                      ('NOT = { hlc_ordinance_slot_free = yes }', '§YSlots full§!'),
                                      (f'NOT = {{ {power_test} }}', f'§RNeeds 50 {power}§!')], 'Resources met')


# --- Galicia: the Boyar Council (the Polish fork of the voivodeship) ------------------------------------------------------
hlc_council = choice('RipGovHlcCouncil', [
    ('has_country_modifier = hlc_boyars_confirmed', '§GOffices Confirmed (Co-option)§!'),
    ('has_country_modifier = hlc_foreign_claimant_countered', '§GDynastic Defense§!'),
    ('has_country_modifier = hlc_boyars_made_example', '§GRepression of Defiant Boyar§!')
], 'No active course')

hlc_council_tip = 'Active Boyar Council course:\n- Confirm in Office: +10 noble loyalty immediately, concessions for 10 years\n- Counter Claimant: +3 legitimacy equivalent immediately, authority for 10 years\n- Make an Example: +3 army tradition and -5 noble loyalty immediately, coercion for 7 years\nAll three share a ten-year cooldown, including the three years after coercion expires. See each action for its cost, benefits and penalties.'
hlc_session_tip = 'Shared 10-year session lockout:\nThe Boyar Council courses share a single ten-year council session.\nChoosing any course convenes the council and locks all other courses for 10 years because co-option, dynastic defence, and repression compete rather than stack as independent tools.'

# --- Lithuania: Pany Rada (LIT) ---
lit_threshold_tip = 'Noble Loyalty Thresholds:\n- 40%: Minimum needed to seek Rada consent or muster retinues\n- 50%: Ceiling for winning over a wavering lord\nBoth major Rada actions reduce loyalty by 10%.'

# --- Volhynia: Magnate Senate (VLN) ---
vln_consent_tip = 'Senate Consent:\nSummon the Senate costs 3 months of income, grants +2 legitimacy equivalent immediately and consent for 5 years (8-year cooldown).\nConvening the Senate is required before calling up the Magnate Banners.'

# Layout is separate from the numerical contracts above. Native interaction
# buttons remain the authority for engine-owned cooldowns, including old saves.
import government_resolution_ledger as ledger
from government_status_layout import build_panels
PANELS = build_panels(globals())
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
# Drop the previous layout's unused rows and dynamic branches. Keep only the
# transitive localisation graph actually reachable from a displayed widget.
import re
used = set(re.findall(r'text = "(rip_gov_\w+)"', gui))
used |= {key + '_tt' for key in used if key + '_tt' in LOC}   # a static caption has no tooltip
definitions = {re.search(r'name = (\w+)', block)[1]: block for block in DYNAMIC}
live_dynamic = set()
while True:
    wanted = set(re.findall(r'\[Root\.(\w+)\]', '\n'.join(LOC[key] for key in used))) - live_dynamic
    if not wanted:
        break
    for name in wanted:
        used.update(re.findall(r'localisation_key = (\w+)', definitions[name]))
    live_dynamic |= wanted
LOC = {key: value for key, value in LOC.items() if key in used}
DYNAMIC = [block for name, block in definitions.items() if name in live_dynamic]
backgrounds = 'spriteTypes = {\n' + '\n'.join(
    f' corneredTileSpriteType = {{ name = {name} size = {{ x = 470 y = {height} }} texturefile = "gfx/interface/government_view/government_mechanics_bg.dds" borderSize = {{ x = 12 y = 12 }} }}'
    for name, height in [('GFX_rip_government_status_bg', 320), ('GFX_rip_government_reviews_head_bg', ledger.HEAD_H)] + [(ledger.card_sprite(h), h) for h in ledger.HEIGHTS]
) + '\n}\n'
outputs = {'interface/RIP_shared_government_status.gfx': backgrounds, 'interface/countrygovernmentview.gui': gui, 'common/custom_gui/rip_government_status.txt':'\n'.join(CONTROLS)+'\n'}
outputs.update(split_custom_localization('\n'.join(DYNAMIC)+'\n', 'government_status'))
body = '\n'.join(f' {k}:0 "{v.replace(chr(10), chr(92)+"n")}"' for k, v in LOC.items()) + '\n'
for language in ('english', 'french', 'german', 'spanish'):
    outputs[f'localisation/replace/RIP_shared_government_status_l_{language}.yml'] = 'l_' + language + ':\n' + body

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check',action='store_true'); args=parser.parse_args()
    for rel,content in outputs.items():
        newline = '\n' if rel.startswith('customizable_localization/') else '\r\n'
        data=content.replace('\r\n','\n').replace('\n',newline).encode('utf-8-sig' if rel.endswith('.yml') else 'utf-8')
        path=ROOT/rel
        if args.check:
            # core.autocrlf rewrites line endings on checkout; the engine reads both.
            unix=lambda raw: raw.replace(b'\r\n',b'\n')
            assert path.exists() and unix(path.read_bytes())==unix(data), f'Stale generated file: {rel}'
        else:
            path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    print(f'Government status UI: {len(outputs)} outputs '+('verified' if args.check else 'written'))
if __name__ == '__main__': main()
