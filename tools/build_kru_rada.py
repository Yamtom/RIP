"""Build the Rada of Three Estates of the Kyivan Confederation: six reforms, the pair logic and the States General sides.

The Rada is the vanilla FACTION mechanic (common/factions/RIP_kru_factions.txt: knyazi, boyary, starshyna) plus, with Res Publica or Winds
of Change, the native States General bar. The author's rule for that bar, 18 October 2026:

    the faction that is SECOND by influence stands on the LEFT of the bar, the DOMINANT faction on the RIGHT.

The bar's two ends are fixed by the reform that is held: the first block of `states_general_mechanic` is the left end, the second the
right end, whatever they are called (the UZH Palanok bar works that way, observed in the game). A bar whose ends follow the factions
therefore needs one reform for every ordered pair (second, dominant): 3 x 2 = 6. The three older reform ids are kept, so a save keeps
loading, and three are added. All six are one government under one name, "Rada of Three Estates": the script swaps between them as the
pair changes, exactly as the three-id version did.

    reform id                                                     left (second)   right (dominant)
    ruthenian_factional_empire_reform                             boyary          knyazi        (the id of a new Confederation)
    ruthenian_factional_empire_princes_hetmans_reform             knyazi          starshyna
    ruthenian_factional_empire_boyars_hetmans_reform              boyary          starshyna
    ruthenian_factional_empire_princes_boyars_reform              knyazi          boyary
    ruthenian_factional_empire_hetmans_princes_reform             starshyna       knyazi
    ruthenian_factional_empire_hetmans_boyars_reform              starshyna       boyary

What this writes (all of it generated, compare with --check):
  common/government_reforms/RIP_KRU_rada_reforms.txt        the six reforms
  common/scripted_triggers/kru_rada_triggers.txt            the holder test, "A is ahead of B" ladders, the six pair tests, the leader's grip
  common/scripted_effects/kru_rada_effects.txt              the rank, reform swap and bar effects
  interface/rip_kru_rada.gfx                                the three side sprites (GFX_kru_rada_<faction>, two frames: out of power / in power)
  gfx/interface/rip_government/kru_rada_<faction>.dds       their textures, made from the faction emblems
  localisation/replace/zzzz_rip_kru_rada_l_<language>.yml   side names, descriptions and tooltips (English text in all four languages)

How a bar position is chosen (kru_rada_bar_effect): the bar is centred and then moved to the right by the leader's grip: influence 50 gives a
quarter, 55 a half, 60 three quarters, less than 50 nothing - the Rada is contested and nobody holds the floor. Side modifiers apply to the
side that is in power, so the leader's bloc gets its floor modifiers from 50 influence and the runner-up's bloc gets none until it overtakes.
The vanilla faction mechanic still gives the faction in power its own modifier, and the runner-up keeps its junior voice from 38 influence.

Comparing two factions' influence has no trigger of its own. "A is ahead of B" is the ladder  OR over N = 2, 4 .. 100 of
(influence of A >= N and not influence of B >= N)  - the two-point steps make a gap of one point a tie, and a tie keeps the runner-up the
Rada already had (flag kru_rada_second_<faction>), or else the order knyazi, boyary, starshyna, so the pair does not flap.
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('english', 'french', 'german', 'spanish')

# key, faction id, name, word in reform ids, floor modifiers (what the bloc gives while it holds the floor), what the bloc stands for
FACTIONS = (
    ('knyazi', 'kru_knyazi', 'Knyazi', 'princes',
     (('legitimacy', 0.5), ('diplomatic_reputation', 0.5), ('vassal_forcelimit_bonus', 0.05)),
     'dynastic standing, diplomacy and the service of dependent princes'),
    ('boyary', 'kru_boyary', 'Boyary', 'boyars',
     (('global_tax_modifier', 0.05), ('stability_cost_modifier', -0.05), ('advisor_cost', -0.05)),
     'office, landed rights and the treasury'),
    ('starshyna', 'kru_starshyna', 'Starshyna', 'hetmans',
     (('discipline', 0.01), ('land_morale', 0.05), ('manpower_recovery_speed', 0.1)),
     'regimental appointments, the register and the rights of the host'),
)
KEYS = [f[0] for f in FACTIONS]
BY_KEY = {f[0]: f for f in FACTIONS}
LEGACY_DEFAULT = ('boyary', 'knyazi')       # (second, leader) of the id that a new Confederation starts with


def reform_id(second, lead):
    if (second, lead) == LEGACY_DEFAULT:
        return 'ruthenian_factional_empire_reform'
    return f'ruthenian_factional_empire_{BY_KEY[second][3]}_{BY_KEY[lead][3]}_reform'


PAIRS = [(second, lead) for lead in KEYS for second in KEYS if second != lead]
REFORM_IDS = [reform_id(second, lead) for second, lead in PAIRS]
THIRD = {(second, lead): next(k for k in KEYS if k not in (second, lead)) for second, lead in PAIRS}
STEPS = range(2, 101, 2)
GRIP = ((60, 0.75), (55, 0.5), (50, 0.25))      # leader's influence -> how far the bar moves to the right


def fmt(value):
    return repr(float(value)).rstrip('0').rstrip('.') if float(value) != int(value) else str(int(value))


# ------------------------------------------------------------------------------------------------ reforms --------------------

def side_block(key, indent='\t\t\t'):
    lines = [f'{indent}kru_rada_{key} = {{']
    for name, value in BY_KEY[key][4]:
        lines.append(f'{indent}\t{name} = {fmt(value)}')
    lines.append(f'{indent}}}')
    return '\n'.join(lines)


def reform_text(second, lead):
    rid = reform_id(second, lead)
    others = [r for r in REFORM_IDS if r != rid]
    if rid == 'ruthenian_factional_empire_reform':
        potential = ('\tpotential = {\n\t\tOR = {\n\t\t\thas_reform = ' + rid + '\n\t\t\tAND = {\n\t\t\t\ttag = KRU\n'
                     + ''.join(f'\t\t\t\tNOT = {{ has_reform = {o} }}\n' for o in others) + '\t\t\t}\n\t\t}\n\t}\n')
    else:
        potential = f'\tpotential = {{\n\t\thas_reform = {rid}\n\t}}\n'
    return f'''{rid} = {{
	icon = "imperial_nobility_reform"
	legacy_equivalent = principality_legacy
{potential}	allow_normal_conversion = no
	valid_for_nation_designer = no
	valid_for_new_country = yes
	lock_level_when_selected = yes
	queen = yes
	heir = yes
	royal_marriage = yes
	allow_convert = no
	trigger = {{
		OR = {{
			has_reform = {rid}
			tag = KRU
		}}
	}}
	modifiers = {{
		governing_capacity_modifier = 0.1
		vassal_income = 0.15
	}}
	custom_attributes = {{
		locked_government_type = yes
	}}
	# Left end of the States General bar: {BY_KEY[second][2]}, second by influence. Right end: {BY_KEY[lead][2]}, dominant.
	factions = {{
		kru_knyazi
		kru_boyary
		kru_starshyna
	}}
	government_abilities = {{
		ruthenian_factional_court_mechanic
	}}
	conditional = {{
		allow = {{
			OR = {{
				has_dlc = "Res Publica"
				has_dlc = "Winds of Change"
			}}
		}}
		states_general_mechanic = {{
{side_block(second)}
{side_block(lead)}
		}}
	}}
}}
'''


def reforms_file():
    head = f'''# Generated by tools/build_kru_rada.py - edit the tables there, not this file.
#
# The Rada of Three Estates: ONE government under SIX reform ids, one for every ordered pair (second by influence, dominant). The first
# block of states_general_mechanic is the LEFT end of the native States General bar, the second the RIGHT end: the faction that is second
# by influence stands on the left, the dominant faction on the right, and the script (common/scripted_effects/kru_rada_effects.txt) swaps
# between the six ids as the pair changes. All six carry the same name, "Rada of Three Estates"; the three older ids are kept so that a
# save keeps loading.
#
#   id                                                              left (second)   right (dominant)
''' + ''.join(f'#   {reform_id(s, l):<62}{BY_KEY[s][2]:<16}{BY_KEY[l][2]}\n' for s, l in PAIRS) + '\n'
    return head + '\n'.join(reform_text(s, l) for s, l in PAIRS)


# ----------------------------------------------------------------------------------------------- triggers ---------------------

def triggers_file():
    out = ['# Generated by tools/build_kru_rada.py - edit the tables there, not this file.',
           '# The Rada of Three Estates (see common/government_reforms/RIP_KRU_rada_reforms.txt): who holds the reform, who is ahead of whom by',
           '# influence, which pair (second, dominant) the Rada is in, and how firm the leader\'s grip is.', '']
    out.append('# Any of the six reform ids.\nkru_holds_rada_reform = {\n\tOR = {')
    out += [f'\t\thas_reform = {r}' for r in REFORM_IDS]
    out.append('\t}\n}\n')
    out.append('# The reform and the KRU tag together: the gate of the court events, decisions and abilities.\n'
               'kru_has_factional_empire_reform = {\n\ttag = KRU\n\tkru_holds_rada_reform = yes\n}\n')
    out.append('# A is ahead of B: A reaches a two-point step that B does not. A gap of less than two points is a tie.')
    for a in KEYS:
        for b in KEYS:
            if a == b:
                continue
            out.append(f'kru_ahead_{a}_{b} = {{\n\tOR = {{')
            for n in STEPS:
                out.append(f'\t\tAND = {{ faction_influence = {{ faction = kru_{a} influence = {n} }} NOT = {{ faction_influence = {{ faction = kru_{b} influence = {n} }} }} }}')
            out.append('\t}\n}\n')
    out.append('# The pair the Rada is in: D leads (the faction in power) and X is second. A tie between the two others keeps the old runner-up\n'
               '# (kru_rada_second_<faction>), and with no old runner-up the order knyazi, boyary, starshyna decides.')
    for second, lead in PAIRS:
        z = THIRD[(second, lead)]
        priority = 'always = yes' if KEYS.index(second) < KEYS.index(z) else 'always = no'
        out.append(f'''kru_pair_{second}_{lead} = {{
	faction_in_power = kru_{lead}
	OR = {{
		kru_ahead_{second}_{z} = yes
		AND = {{
			NOT = {{ kru_ahead_{z}_{second} = yes }}
			OR = {{
				has_country_flag = kru_rada_second_{second}
				AND = {{
					NOT = {{ has_country_flag = kru_rada_second_{z} }}
					{priority}
				}}
			}}
		}}
	}}
}}
''')
    out.append('# How firm the leader\'s grip is: the faction in power with at least this much influence. The bar moves right by a quarter, a half or\n'
               '# three quarters at 50, 55 and 60; below 50 the Rada is contested and the bar stays in the centre.')
    for n, _ in GRIP:
        out.append(f'kru_leader_influence_{n} = {{\n\tOR = {{')
        for k in KEYS:
            out.append(f'\t\tAND = {{ faction_in_power = kru_{k} faction_influence = {{ faction = kru_{k} influence = {n} }} }}')
        out.append('\t}\n}\n')
    return '\n'.join(out)


# ------------------------------------------------------------------------------------------------ effects ---------------------

def effects_file():
    flags = [f'kru_rada_second_{k}' for k in KEYS] + [f'kru_rada_lead_{k}' for k in KEYS]
    tmp = [f'kru_rada_tmp_{s}_{l}' for s, l in PAIRS]
    out = ['# Generated by tools/build_kru_rada.py - edit the tables there, not this file.',
           '# The Rada of Three Estates: find the pair, swap to the reform that has it, and set the States General bar. Only if-blocks are used:',
           '# inside an else_if/else body of a scripted effect the engine drops some effects without an error.',
           '#',
           '# Called by kru_refresh_factional_court_effect (common/scripted_effects/kru_effects.txt) from the court buttons, the monthly pulse',
           '# (ruthenian_factions.21) and the yearly one (ruthenian_factions.20).', '']
    out.append('''# Flags and modifiers of the earlier, previous-dominant version of the Rada. Cleared on every refresh; nothing reads them now.
kru_rada_forget_old_state_effect = {
	clr_country_flag = kru_factional_dominance_active
	clr_country_flag = kru_current_dominant_knyazi
	clr_country_flag = kru_current_dominant_boyary
	clr_country_flag = kru_current_dominant_starshyna
	clr_country_flag = kru_previous_dominant_knyazi
	clr_country_flag = kru_previous_dominant_boyary
	clr_country_flag = kru_previous_dominant_starshyna
}
''')
    out.append('# The pair into flags. Every limit below reads the OLD flags (the tie rule needs them), so the new pair goes into temporary flags first\n'
               '# and replaces the old ones only when a pair was found.\nkru_rada_rank_effect = {')
    for second, lead in PAIRS:
        out.append(f'\tif = {{ limit = {{ kru_pair_{second}_{lead} = yes }} set_country_flag = kru_rada_tmp_{second}_{lead} }}')
    out.append('\tif = {\n\t\tlimit = {\n\t\t\tOR = {')
    out += [f'\t\t\t\thas_country_flag = {t}' for t in tmp]
    out.append('\t\t\t}\n\t\t}')
    out += [f'\t\tclr_country_flag = {f}' for f in flags]
    for second, lead in PAIRS:
        out.append(f'\t\tif = {{ limit = {{ has_country_flag = kru_rada_tmp_{second}_{lead} }} set_country_flag = kru_rada_second_{second} set_country_flag = kru_rada_lead_{lead} }}')
    out += [f'\t\tclr_country_flag = {t}' for t in tmp]
    out.append('\t}\n}\n')
    out.append('# The reform that has the pair: left end second, right end dominant. add_government_reform replaces the reform of the same tier, and that\n'
               '# is ALL it may do: remove_government_reform deletes the factions with the reform, and the next add_government_reform founds them again at\n'
               '# 55 / 15 / 30 (measured in EU4 1.37.5), so a removal would wipe the rada\'s influence at every swap. A new reform is only added when it is\n'
               '# not held already.\nkru_rada_select_reform_effect = {')
    for second, lead in PAIRS:
        rid = reform_id(second, lead)
        out.append('\tif = {\n\t\tlimit = {\n\t\t\thas_country_flag = kru_rada_second_%s\n\t\t\thas_country_flag = kru_rada_lead_%s\n\t\t\tNOT = { has_reform = %s }\n\t\t}' % (second, lead, rid))
        out.append(f'\t\tadd_government_reform = {rid}\n\t}}')
    out.append('}\n')
    out.append('# The bar: centred, then moved right by the leader\'s grip (50 influence a quarter, 55 a half, 60 three quarters). -10 then +1 is the\n'
               '# vanilla centring (common/scripted_effects/01_scripted_effects_for_on_actions.txt).\nkru_rada_bar_effect = {\n\tif = {\n\t\tlimit = { has_states_general_mechanic = yes }\n'
               '\t\tchange_statists_vs_orangists = -10\n\t\tchange_statists_vs_orangists = 1')
    steps = list(GRIP)
    for index, (n, move) in enumerate(steps):
        if index == 0:
            out.append(f'\t\tif = {{ limit = {{ kru_leader_influence_{n} = yes }} change_statists_vs_orangists = {fmt(move)} }}')
        else:
            out.append(f'\t\tif = {{ limit = {{ kru_leader_influence_{n} = yes NOT = {{ kru_leader_influence_{steps[index - 1][0]} = yes }} }} change_statists_vs_orangists = {fmt(move)} }}')
    out.append('\t}\n}\n')
    return '\n'.join(out)


# -------------------------------------------------------------------------------------------- sprites and text ---------------

def sprite_strip(key):
    """Two 23x25 frames: the faction's emblem muted (out of power), and bright with a gold rim (in power)."""
    from PIL import Image, ImageFilter
    emblem = Image.open(ROOT / f'gfx/interface/rip_government/faction_{key}.dds').convert('RGBA')
    emblem = emblem.crop(emblem.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox())
    scale = min(21.0 / emblem.width, 23.0 / emblem.height)
    emblem = emblem.resize((max(1, round(emblem.width * scale)), max(1, round(emblem.height * scale))), Image.LANCZOS)
    strip = Image.new('RGBA', (46, 25), (0, 0, 0, 0))
    for frame in range(2):
        cell = Image.new('RGBA', (23, 25), (0, 0, 0, 0))
        x, y = (23 - emblem.width) // 2, (25 - emblem.height) // 2
        picture = emblem.copy()
        if frame == 0:
            r, g, b, a = picture.split()
            grey = Image.merge('RGB', (r, g, b)).convert('L')
            muted = Image.merge('RGB', tuple(Image.blend(grey, ch, 0.55) for ch in (r, g, b))).point(lambda v: int(v * 0.78))
            picture = Image.merge('RGBA', (*muted.split(), a))
        else:
            held = Image.new('L', (23, 25), 0)
            held.paste(picture.getchannel('A'), (x, y))
            rim = held.filter(ImageFilter.MaxFilter(3)).point(lambda v: 255 if v > 0 else 0)
            glow = Image.new('RGBA', (23, 25), (255, 205, 70, 0))
            glow.putalpha(rim.point(lambda v: 170 if v else 0))
            cell.alpha_composite(glow)
            r, g, b, a = picture.split()
            picture = Image.merge('RGBA', (r.point(lambda v: min(255, int(v * 1.12) + 6)), g.point(lambda v: min(255, int(v * 1.10) + 5)), b.point(lambda v: min(255, int(v * 1.04))), a))
        cell.alpha_composite(picture, (x, y))
        strip.alpha_composite(cell, (23 * frame, 0))
    return strip


SIDE_TEXT = {
    'knyazi': ('The princely houses hold the floor of the Rada. Their agenda - {stands} - prevails while they lead it with at least 50 influence.'),
    'boyary': ('The boyar houses hold the floor of the Rada. Their agenda - {stands} - prevails while they lead it with at least 50 influence.'),
    'starshyna': ('The Cossack officers hold the floor of the Rada. Their agenda - {stands} - prevails while they lead it with at least 50 influence.'),
}


def localisation(language):
    rows = []
    for key, _, name, _, _, stands in FACTIONS:
        rows.append(f'kru_rada_{key}:0 "{name}"')
        rows.append(f'kru_rada_{key}_desc:0 "{SIDE_TEXT[key].format(stands=stands)} The faction that is second by influence stands on the left of the bar and the dominant faction on the right; the bar moves right with the leader\'s influence."')
        rows.append(f'kru_rada_{key}_MECHANIC_TOOLTIP:0 "{name}"')
    return f'l_{language}:\n # Generated by tools/build_kru_rada.py; English text in every language until a translator takes it.\n' + ''.join(f' {row}\n' for row in rows)


def gfx_text():
    lines = ['spriteTypes = {']
    for key in KEYS:
        lines.append(f'\tspriteType = {{ name = "GFX_kru_rada_{key}" texturefile = "gfx/interface/rip_government/kru_rada_{key}.dds" noOfFrames = 2 norefcount = yes }}')
    lines.append('}')
    return '\n'.join(lines) + '\n'


def text_outputs():
    result = {
        'common/government_reforms/RIP_KRU_rada_reforms.txt': reforms_file(),
        'common/scripted_triggers/kru_rada_triggers.txt': triggers_file(),
        'common/scripted_effects/kru_rada_effects.txt': effects_file(),
        'interface/rip_kru_rada.gfx': gfx_text(),
    }
    for language in LANGUAGES:
        result[f'localisation/replace/zzzz_rip_kru_rada_l_{language}.yml'] = '﻿' + localisation(language)
    return result


def write_bytes(relative, text):
    data = text.replace('\r\n', '\n')
    bom = data.startswith('﻿')
    payload = data.lstrip('﻿').replace('\n', '\r\n').encode('utf-8')
    return (b'\xef\xbb\xbf' if bom else b'') + payload


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for relative, text in text_outputs().items():
        path = ROOT / relative
        payload = write_bytes(relative, text)
        current = path.read_bytes() if path.exists() else None
        if current is None or current.replace(b'\r\n', b'\n') != payload.replace(b'\r\n', b'\n'):
            stale.append(relative)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
    for key in KEYS:
        relative = f'gfx/interface/rip_government/kru_rada_{key}.dds'
        path = ROOT / relative
        fresh = sprite_strip(key)
        if not path.exists():
            stale.append(relative)
            if not args.check:
                fresh.save(path, format='DDS')
            continue
        from PIL import Image
        import numpy as np
        have = np.asarray(Image.open(path).convert('RGBA'), dtype=np.int16)
        want = np.asarray(fresh, dtype=np.int16)
        if have.shape != want.shape or int(np.abs(have - want).max()) > 3:
            stale.append(relative)
            if not args.check:
                fresh.save(path, format='DDS')
    print(('STALE' if args.check and stale else 'GENERATED' if stale else 'CURRENT')
          + f': Rada of Three Estates, {len(REFORM_IDS)} reforms, {len(KEYS)} side sprites, {len(stale)} files')
    for relative in stale:
        print('  ' + relative)
    if args.check and stale:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
