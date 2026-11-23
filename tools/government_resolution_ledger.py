"""The institutional resolutions as a ledger: one card per institution, one medallion per resolution.

The six paid resolutions are buttons in the mechanics box on the left of the government window
(common/government_mechanics/rip_institutional_resolutions.txt). This module builds the panel on the right
that explains them. It used to be one block of text; the readout is now a head (what stands, how long the
term runs) and a card for each institution the country holds. A row repeats the button's own medallion
and says, in the order a player asks: what the order is called, what it costs, what it does for ten
years and whether it can be passed now.

EU4 windows do not move, so the position of a card depends on what stands above it. Every combination is
generated as its own window, shown by a `potential`: the head sits at the top of the column, or under the
status panel of the reform (Lithuania, Volhynia) when there is one, and each card sits under the head and
under the cards of the institutions that come before it. The text of a row is shared; only the window
differs.
"""

STATUS_Y = 336       # under the 320-high status panel (12 + 320 + 4)
TOP_Y = 12
GAP = 4
WIDTH = 470
INSET = 26           # the frame's corner ornaments reach 24 px in: text starts 26 px from the left edge ...
INSET_R = 36         # ... and right-aligned text ends 36 px from the right one
PAD = 14             # space above the first and below the last line
LINE = 18            # vic_18
HEAD_H = PAD + 2 * 20 + PAD
CARD_TOP = PAD + 20 + 4     # the card title, then the first row

# group key, title, who holds it, the two resolutions (keys of RESOLUTIONS in build_government_status_ui.py)
GROUPS = [
    ('Municipal', 'mun', "Town Charters", 'rip_gov_has_municipal_review = yes', ('MunicipalCharters', 'MunicipalAccounts')),
    ('Chancery', 'cha', "Chancery Rolls", 'rip_gov_has_chancery_review = yes', ('ChanceryService', 'ChanceryRights')),
    ('Register', 'reg', "Host Register", 'rip_gov_has_register_review = yes', ('RegisterMuster', 'RegisterSettlement')),
]

# what each order does for its ten years, in the words of the tooltip and of the modifier tests
EFFECTS = {
    'MunicipalCharters': "+5% production efficiency, +5% burghers' loyalty,\n-5 maximum absolutism",
    'MunicipalAccounts': "+5% national tax, -0.025 yearly corruption,\n-5% burghers' loyalty",
    'ChanceryService': "-5% state maintenance, -0.025 yearly corruption,\n-5% nobles' loyalty",
    'ChanceryRights': "-10% culture promotion cost, -0.5 national unrest,\n-5% national tax",
    'RegisterMuster': "+5% manpower recovery, +5% land maintenance",
    'RegisterSettlement': "-0.5 national unrest, -5% national manpower",
}
ICONS = {
    'MunicipalCharters': 'GFX_rip_resolution_municipal_charters', 'MunicipalAccounts': 'GFX_rip_resolution_municipal_accounts',
    'ChanceryService': 'GFX_rip_resolution_chancery_service', 'ChanceryRights': 'GFX_rip_resolution_chancery_rights',
    'RegisterMuster': 'GFX_rip_resolution_register_muster', 'RegisterSettlement': 'GFX_rip_resolution_register_settlement',
}


def lines(key):
    return EFFECTS[key].count(chr(10)) + 1


def row_height(key):
    """title, the effect lines, then the cost and the state on one line; a gap of 6 before the next row."""
    return LINE * (lines(key) + 2) + 6


def card_height(keys):
    return CARD_TOP + sum(row_height(k) for k in keys) - 6 + PAD


# every distinct card height needs its own background sprite
HEIGHTS = sorted({card_height(keys) for _, _, _, _, keys in GROUPS})


def card_sprite(height):
    return f'GFX_rip_government_reviews_card_{height}_bg'


def slot_gate(group_index, slot, held):
    """True when exactly `slot` of the institutions that come before this one are held."""
    earlier = [held[i] for i in range(group_index)]
    if slot == 0:
        return ' '.join(f'NOT = {{ {h} }}' for h in earlier)
    if slot == len(earlier):
        return ' '.join(earlier)
    # one of two
    a, b = earlier
    return f'OR = {{ AND = {{ {a} NOT = {{ {b} }} }} AND = {{ {b} NOT = {{ {a} }} }} }}'


def build_ledger(g, status_any):
    """Return (windows, geometry): windows are (name, gate, rows), geometry maps a window name to (y, height, sprite)."""
    loc, choice = g['loc'], g['choice']
    resolutions = {key: (held, label, power, power_test, modifier) for key, held, label, power, power_test, modifier, _ in g['RESOLUTIONS']}
    held = [group[3] for group in GROUPS]
    windows, geometry = [], {}

    def widget(name, content, x, y, width, height, scripted, fmt='left', tooltip=None):
        """A scripted box carries `content` itself (its tooltip is wired through custom_gui); a static one points at a shared key."""
        if scripted:
            loc(name, content)
            loc(name + '_tt', tooltip)
            g['CONTROLS'].append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
            return (f'instantTextBoxType = {{ name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "vic_18" '
                    f'text = "{name}" maxWidth = {width} maxHeight = {height} format = {fmt} }}')
        return (f'instantTextBoxType = {{ name = "{name}" position = {{ x={x} y={y} }} font = "vic_18" '
                f'text = "{content}" maxWidth = {width} maxHeight = {height} format = {fmt} }}')

    # shared text: what the order is called, what it costs, what it does
    for key, (_, label, power, _, _) in resolutions.items():
        loc('rip_gov_rv_name_' + key, '§Y' + label + '§!')
        loc('rip_gov_rv_cost_' + key, f'50 ducats + 50 {power}')
        loc('rip_gov_rv_fx_' + key, EFFECTS[key])
    for title_key, _, title, _, _ in GROUPS:
        loc('rip_gov_rv_group_' + title_key, '§Y' + title + '§!')
    loc('rip_gov_rv_note', 'Each order stands for ten years')

    ladders = {}
    for key, (holder, label, power, power_test, modifier) in resolutions.items():
        states = [(f'has_country_modifier = {modifier}', '§YIn force§!'),
                  ('rip_gov_resolution_in_force = yes', '§RAnother order in force§!'),
                  ('NOT = { rip_gov_resolution_lock_over = yes }', '§RLocked for ten years§!'),
                  ('is_at_war = yes', '§RAt war§!'),
                  ('NOT = { stability = 0 }', '§RStability below 0§!'),
                  ('NOT = { treasury = 50 }', '§RNeeds 50 ducats§!'),
                  (f'NOT = {{ {power_test} }}', f'§RNeeds 50 {power}§!')]
        ladders[key] = choice('RipGovResState' + key, states, '§GReady§!')

    needs = ('To pass an order you need:\n- peace\n- stability of at least 0\n- 50 ducats, which are paid\n'
             '- 50 monarch power of the kind named on the button, which is paid\n'
             '- no other order in force, and ten years since the last one.')

    def tooltip(key):
        _, label, power, _, _ = resolutions[key]
        return (f'{label}: {EFFECTS[key].replace(chr(10), " ")}, for ten years.\nCost: 50 ducats and 50 {power} power, paid when you press "{label}" in the mechanics box '
                f'on the left.\n{needs}\nThe line above says which of these holds now: gold stands, green is ready, red is not met.')

    for low in (False, True):
        tag = 'l' if low else 't'
        y0 = STATUS_Y if low else TOP_Y
        gate_status = status_any if low else f'NOT = {{ {status_any} }}'
        right = WIDTH - INSET - INSET_R
        # head: what stands, and the term (the title on the left, the term on the right)
        head = 'rip_gov_rv_head_' + tag
        rows = [
            widget(f'rip_gov_rev_title_{tag}', '§YInstitutional Resolutions§!', INSET, PAD, 200, 20, True, tooltip=g['res_title_tip']),
            widget(f'rip_gov_rev_left_{tag}', g['res_left'], INSET + 200, PAD, right - 200, 20, True, fmt='right', tooltip=g['res_now_tip']),
            widget(f'rip_gov_rev_now_{tag}', 'In force: ' + g['res_name'], INSET, PAD + 20, right, 20, True, tooltip=g['res_now_tip']),
        ]
        review_gate = ('OR = { rip_gov_has_municipal_review = yes rip_gov_has_chancery_review = yes rip_gov_has_register_review = yes '
                       'rip_gov_resolution_in_force = yes NOT = { rip_gov_resolution_lock_over = yes } }')
        windows.append((head, f'{review_gate} {gate_status}', rows))
        geometry[head] = (y0, HEAD_H, 'GFX_rip_government_reviews_head_bg')

        for index, (group, short, title, holder, keys) in enumerate(GROUPS):
            height = card_height(keys)
            for slot in range(index + 1):
                name = f'rip_gov_rv_{short}{slot}_{tag}'
                gate = f'{holder} {slot_gate(index, slot, held)} {gate_status}'
                suffix = f'{short}{slot}_{tag}'
                card = [widget(f'rip_gov_rv_group_{group}_{suffix}', 'rip_gov_rv_group_' + group, INSET, PAD, 200, 20, False),
                        widget(f'rip_gov_rv_note_{group}_{suffix}', 'rip_gov_rv_note', INSET + 200, PAD, right - 200, 20, False, fmt='right')]
                r = CARD_TOP
                for key in keys:
                    n = lines(key)
                    content = LINE * (n + 2)
                    state_name = f'rip_gov_rv_state_{key}_{suffix}'
                    card += [
                        f'iconType = {{ name = "rip_gov_rv_icon_{key}_{suffix}" spriteType = "{ICONS[key]}" position = {{ x=14 y={r + (content - 45) // 2} }} scale = 0.55 }}',
                        widget(f'rip_gov_rv_title_{key}_{suffix}', 'rip_gov_rv_name_' + key, 68, r, 372, LINE, False),
                        widget(f'rip_gov_rv_effect_{key}_{suffix}', 'rip_gov_rv_fx_' + key, 68, r + LINE, 372, LINE * n, False),
                        widget(f'rip_gov_rv_price_{key}_{suffix}', 'rip_gov_rv_cost_' + key, 68, r + LINE * (n + 1), 180, LINE, False),
                        widget(state_name, ladders[key], 252, r + LINE * (n + 1), WIDTH - INSET_R - 252, LINE, True, fmt='right', tooltip=tooltip(key)),
                    ]
                    r += row_height(key)
                    if key == keys[0]:
                        card.append(f'iconType = {{ name = "rip_gov_rv_rule_{suffix}" spriteType = "GFX_native_building_divider" position = {{ x=68 y={r - 6 - 2} }} }}')
                windows.append((name, gate, card))
                above = [card_height(GROUPS[i][4]) for i in range(index)]
                # a card of the same group at slot s sits under s earlier cards; the cards of M and C are equally high, so the order among them
                # does not matter for the offset
                geometry[name] = (y0 + HEAD_H + GAP + slot * (above[0] + GAP if above else 0), height, card_sprite(height))
    return windows, geometry
