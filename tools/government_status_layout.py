"""Player-facing government dossiers; source-backed conditions, native cooldowns.

No custom buttons or gameplay flags: EU4 owns the interaction cooldown state.
Keep the native buttons, use their artwork to connect each explanatory row to
its action, and never infer availability from the lifetime of a modifier.
"""
import re
from clausewitz_testlib import named_block


def build_panels(g):
    row, choice = g['row'], g['choice']
    g['CONTROLS'].clear()
    panels = []

    def text(key, y, value, tip='', **kwargs):
        # EU4 1.37 ships vic_18, not vic_16. Use its actual metrics in the
        # layout check instead of silently falling back to an unknown font.
        kwargs['font'] = 'vic_18'
        return row('rip_gov_' + key, y, value, tip or value, **kwargs)

    def heading(key, title, purpose, tip):
        return [text(key + '_title', 12, '§Y' + title + '§!', tip),
                text(key + '_purpose', 38, purpose, tip, font='vic_16')]

    def section(key, y, title, tip=''):
        return text(key, y, '§Y' + title + '§!', tip, font='vic_16')

    def add(name, gate, rows):
        panels.append(('rip_gov_' + name + '_panel', gate, rows))

    def state(key, modifier):
        owner = 'Vln' if key == 'Senate' else 'Lit'
        return choice('RipGov' + owner + 'Dossier' + key, [(f'has_country_modifier = {modifier}', '§GIn force§!')], 'Not in force')

    def action(key, y, source, ability, title, summary, price, detail, reasons=()):
        source_text = (g['ROOT'] / 'common/government_mechanics' / source).read_text(encoding='utf-8-sig')
        block = named_block(source_text, ability)
        trigger = named_block(block, 'trigger')
        trigger = trigger[trigger.index('{') + 1:trigger.rfind('}')].strip()
        icon = re.search(r'icon\s*=\s*(\w+)', block)[1]
        years = re.search(r'cooldown_years\s*=\s*(\d+)', block)[1]
        modifier = re.search(r'add_country_modifier\s*=\s*\{\s*name\s*=\s*(\w+)', block)[1]
        active = choice('RipGov' + key[:3].title() + 'DossierActive' + key,
                        [(f'has_country_modifier = {modifier}', ' §G[Active]§!')], '')
        # The complete live trigger is the final gate, including less common
        # requirements omitted from the short, prioritised blocker messages.
        status = choice('RipGov' + key[:3].title() + 'DossierAction' + key, list(reasons) + [
            (trigger, 'Requirements met; check button timer')], '§RRequirements not met§!')
        tip = (f'{title}\n{summary}\nCost: {price}\n{detail}\n'
               f'Reuse interval: {years} years. The native action button shows the remaining cooldown and all requirements. '
               'An active effect does not mean this action can be used again.')
        return [f'iconType = {{ name = "{key}_seal" spriteType = "{icon}" position = {{ x=18 y={y + 2} }} scale = 0.35 }}',
                text(key + '_action', y, '§Y' + title + '§!' + active, tip, x=62, width=390, font='vic_16'),
                text(key + '_benefit', y + 18, summary, tip, x=62, width=390, font='vic_16'),
                text(key + '_price', y + 36, price, tip, x=62, width=390, font='vic_16'),
                text(key + '_state', y + 54, status, tip, x=62, width=390, font='vic_16')]

    # Three political actions: costs and sacrifices remain visible at all times.
    vln = heading('vln', 'Volhynia: Magnate Senate', 'Secure the lords\' consent before calling their banners.', g['vln_consent_tip'])
    vln += [text('vln_consent', 62, 'Senate consent: ' + state('Senate', 'vln_senate_convened'),
                 'Consent lasts five years and is consumed when the banners are called. The +2 legitimacy-equivalent reward is immediate.', font='vic_16')]
    vln += action('vln_summon', 86, 'rip_vln_magnate_senate.txt', 'vln_summon_the_senate', 'Summon the Senate',
                  'Consent for 5 years; +2 legitimacy equivalent now', 'Cost: 3 months of income | Repeat: 8 years',
                  'For 5 years: +15% noble influence, +10% reform progress growth, -10% stability cost.',
                  [('NOT = { years_of_income = 0.25 }', '§RNeeds 3 months of income§!')])
    vln += action('vln_banners', 162, 'rip_vln_magnate_senate.txt', 'vln_call_up_the_magnate_banners', 'Call up the Magnate Banners',
                  'Replenish manpower; +3 army tradition now', 'Consumes Senate consent | Repeat: 10 years',
                  'Adds manpower equal to 10% of maximum manpower; does not increase the maximum. For 5 years: +10% land force limit, +10% cavalry combat ability, +10% land maintenance.',
                  [('is_at_war = no', '§YOnly during war§!'), ('NOT = { has_country_modifier = vln_senate_convened }', '§RRequires Senate consent§!')])
    vln += action('vln_house', 238, 'rip_vln_magnate_senate.txt', 'vln_buy_off_a_magnate_house', 'Negotiate with a Magnate House',
                  'Choose a house and province in the event', 'Concession: 9 months of income + 30 ADM',
                  'Opening requires 6 months of income and an eligible non-capital city below 75 autonomy. A concession costs 9 months of income and 30 ADM: +20 local autonomy, -8 local unrest and a 10-year fief modifier (-15% local tax and manpower, +10% local defensiveness). Refusal costs 5 noble loyalty. The button cooldown starts even if you refuse.',
                  [('NOT = { years_of_income = 0.5 }', '§RNeeds 6 months of income to open§!'),
                   ('NOT = { adm_power = 30 years_of_income = 0.75 }', '§YConcession exceeds current resources§!')])
    add('vln', 'has_reform = vln_voivodeship_reform NOT = { has_reform = vln_cossack_host_reform }', vln)

    lit = heading('lit', 'Lithuania: Pany Rada', 'Consent and mobilisation each spend 10 noble loyalty.', g['lit_threshold_tip'])
    lit += [text('lit_consent', 62, 'Rada consent: ' + state('Rada', 'lit_rada_confirmed'),
                 'Begin with at least 50 loyalty to seek consent and immediately muster retinues at the 40-loyalty threshold. Each action still has its own native timer.', font='vic_16')]
    lit += action('lit_confirm', 86, 'rip_lit_pany_rada.txt', 'lit_seek_the_radas_confirmation', 'Seek the Rada\'s Confirmation',
                  'Consent for 5 years; +2 legitimacy equivalent now', 'Cost: 10 noble loyalty | Requires at least 40',
                  'For 5 years: +10% noble influence, -5% stability cost, -5 maximum absolutism.',
                  [('has_country_modifier = lit_rada_confirmed', '§GConsent already in force§!'),
                   ('NOT = { estate_loyalty = { estate = estate_nobles loyalty = 40 } }', '§RNeeds 40 noble loyalty§!')])
    lit += action('lit_retinues', 162, 'rip_lit_pany_rada.txt', 'lit_the_radas_own_retinues', 'Muster the Rada\'s Own Retinues',
                  '+3 army tradition; cavalry support for 5 years', 'Consumes Rada Consent and 10 noble loyalty',
                  'During war, requires consent and at least 40 noble loyalty. For 5 years: +10% land force limit, +10% cavalry combat ability, +10% land maintenance.',
                  [('is_at_war = no', '§YOnly during war§!'), ('NOT = { has_country_modifier = lit_rada_confirmed }', '§RRequires Rada consent§!'),
                   ('NOT = { estate_loyalty = { estate = estate_nobles loyalty = 40 } }', '§RNeeds 40 noble loyalty§!')])
    lit += action('lit_lord', 238, 'rip_lit_pany_rada.txt', 'lit_win_over_a_wavering_lord', 'Win Over a Wavering Lord',
                  '+15 noble loyalty now; patronage for 5 years', 'Cost: 50 DIP | Only below 50 noble loyalty',
                  'For 5 years: +0.5 diplomatic reputation, -10% advisor costs, -5% core creation cost.',
                  [('estate_loyalty = { estate = estate_nobles loyalty = 50 }', '§YRequires loyalty below 50§!'), ('NOT = { dip_power = 50 }', '§RNeeds 50 DIP§!')])
    lit_gate = 'OR = { has_reform = grand_duchy_reform has_reform = lit_union_of_two_nations_reform has_reform = lit_separate_crown_reform }'
    add('lit', lit_gate, lit)

    hlc = heading('hlc', 'Galicia: Boyar Council', 'Choose one course; all three share a ten-year term.', g['hlc_session_tip'])
    hlc += [text('hlc_council', 62, 'Current course: ' + g['hlc_council'], g['hlc_council_tip'], font='vic_16')]
    hlc += action('hlc_offices', 86, 'rip_hlc_boyar_council.txt', 'hlc_confirm_the_boyars_in_office', 'Confirm the Boyars in Office',
                  '+10 noble loyalty now; concessions for 10 years', 'Cost: 50 ADM | Nobles gain 10% influence',
                  'Requires noble loyalty below 60. For 10 years: -10% stability cost, -1 unrest, +5% morale and +10% noble influence.',
                  [('estate_loyalty = { estate = estate_nobles loyalty = 60 }', '§YRequires loyalty below 60§!'), ('NOT = { adm_power = 50 }', '§RNeeds 50 ADM§!')])
    hlc += action('hlc_claimant', 162, 'rip_hlc_boyar_council.txt', 'hlc_counter_the_foreign_claimant', 'Counter the Foreign Claimant',
                  '+3 legitimacy equivalent now; authority for 10 years', 'Cost: 50 DIP | Requires legitimacy below 60',
                  'Uses legitimacy equivalent for the government type. For 10 years: +5 maximum absolutism and +0.5 diplomatic reputation.',
                  [('legitimacy_equivalent = 60', '§YRequires legitimacy equivalent below 60§!'), ('NOT = { dip_power = 50 }', '§RNeeds 50 DIP§!')])
    hlc += action('hlc_example', 238, 'rip_hlc_boyar_council.txt', 'hlc_make_an_example_of_a_defiant_boyar', 'Make an Example of a Defiant Boyar',
                  '+3 army tradition now; coercion for 7 years', 'Cost: 60 MIL and 5 noble loyalty | +1 unrest',
                  'Requires peace and noble loyalty below 40. For 7 years: +8 maximum absolutism, +1 unrest, -5% noble influence. The shared lock lasts 10 years, including the three years after this effect expires.',
                  [('is_at_war = yes', '§RRequires peace§!'), ('estate_loyalty = { estate = estate_nobles loyalty = 40 }', '§YRequires loyalty below 40§!'), ('NOT = { mil_power = 60 }', '§RNeeds 60 MIL§!')])
    add('hlc', 'has_reform = hlc_galician_voivodeship_reform NOT = { has_reform = hlc_crown_authority_reform }', hlc)

    crown = heading('hlc_crown', 'Frontier Crown: Six Ordinances', 'Keep up to three ordinances; each lasts ten years.', g['hlc_slots_tip'])
    crown += [text('hlc_crown_slots', 62, 'Ordinances in force: ' + g['hlc_slots'], g['hlc_slots_tip'], font='vic_16')]
    for i, (key, label, power, power_test, modifier, effect) in enumerate(g['ORDINANCES']):
        y = 88 + i * 36
        status = g['ordinance_state']('Dossier' + key, label, power, power_test, modifier)
        tip = f'{label} Ordinance - for ten years: {effect}.\nCosts 50 {power}. At most three may be in force. Cannot be revoked.'
        crown += [text('hlc_crown_' + key.lower(), y, f'§Y{label}§! (50 {power}): ' + status, tip, font='vic_16'),
                  text('hlc_crown_' + key.lower() + '_effect', y + 17,
                       effect.split(';')[0].replace('tolerance of heretics and heathens', 'heretic/heathen tolerance'), tip, font='vic_16')]
    add('hlc_crown', 'has_reform = hlc_crown_authority_reform', crown)

    kru = heading('kru', 'Rada of Three Estates', 'Balance the ruling coalition and contain court decadence.', g['coalition_tip'])
    for key, y, label, value in [('leader', 66, 'Right (leads): ', g['leader']), ('second', 90, 'Left (second): ', g['second']),
                                 ('opposition', 114, 'Opposition: ', g['opposition']), ('voice', 138, 'Junior voice: ', g['voice']),
                                 ('bar', 162, 'Balance: ', g['bar'])]:
        kru += [text('kru_' + key, y, label + value, g['coalition_tip'], font='vic_16')]
    kru += [section('kru_domestic', 194, 'COURT STABILITY'), text('kru_decay', 218, 'Decadence: ' + g['decadence_shown'], g['annual_tip'], font='vic_16'),
            text('kru_annual', 244, 'Yearly change: inspect the active causes', g['annual_tip'], font='vic_16'),
            text('kru_crisis', 270, 'Risk at 90 | Recedes below 75\nEnd crisis: below 60 and stability at least +1', g['crisis_tip'], height=40, font='vic_16')]
    add('kru', g['kru_potential'], kru)

    cesar = heading('cesar', 'Cesarstvo: Lands and Settlement', 'Cultural recognition sustains the imperial settlement.', g['lands_tip'])
    for key, y, value, tip in [('minority', 66, 'Non-primary development: ~' + g['minority'], g['lands_tip']),
                              ('excluded', 90, 'Unaccepted development: ~' + g['excluded'], g['lands_tip']),
                              ('eligible', 114, 'Integration: ' + g['eligible'], g['elig_tip']),
                              ('concord', 164, 'Throne Concord: inspect monthly gains and losses', g['concord_tip']),
                              ('gather', 190, 'Gathering: inspect monthly gains and losses', g['gather_tip']),
                              ('breakdown', 240, g['breakdown'], g['recovery_tip'])]:
        cesar += [text('cesar_' + key, y, value, tip, font='vic_16')]
    cesar += [section('cesar_growth', 140, 'MONTHLY CHANGE'), section('cesar_crisis', 216, 'SETTLEMENT CRISIS'),
              text('cesar_recovery', 266, 'Recovery: unaccepted share below 15%\nand Gathering at least 40', g['recovery_tip'], height=40, font='vic_16')]
    add('cesar', 'has_reform = kyivan_cesarstvo_reform', cesar)

    # Identity reforms normally exclude one another by tier. Explicit priority
    # also prevents overlap in migrated saves that still hold a legacy pair.
    previous = []
    ordered = []
    by_name = {name: (gate, rows) for name, gate, rows in panels}
    for name in ['cesar', 'kru', 'hlc_crown', 'hlc', 'lit', 'vln']:
        full = 'rip_gov_' + name + '_panel'
        gate, rows = by_name[full]
        ordered.append((full, gate + ''.join(' NOT = { ' + earlier + ' }' for earlier in previous), rows))
        previous.append(gate)
    # The institutional resolutions are an independent block: it can coexist with any dossier, and never shows an empty
    # institution. It sits at the top of the column, or under the status panel of the reform when there is one; the ledger
    # builds one window for each position (tools/government_resolution_ledger.py).
    status_any = 'OR = { ' + ' '.join('AND = { ' + gate + ' }' for gate in previous) + ' }'
    windows, geometry = g['ledger'].build_ledger(g, status_any)
    g['GEOMETRY'].update(geometry)
    ordered.extend(windows)
    return ordered
