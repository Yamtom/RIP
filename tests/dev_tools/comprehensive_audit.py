import os, glob, re
from collections import defaultdict

vanilla_path = r'D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV'
mod_path = r'd:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV\mod\RIP'

# Extract all triggers recognized in vanilla
vanilla_triggers = set()
for vf in glob.glob(os.path.join(vanilla_path, 'common', 'scripted_triggers', '*.txt')):
    with open(vf, 'r', encoding='utf-8-sig', errors='ignore') as f:
        t = f.read()
    for m in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', t):
        vanilla_triggers.add(m.group(1))

# Also mod scripted triggers
mod_triggers = set()
for mf in glob.glob(os.path.join(mod_path, 'common', 'scripted_triggers', '*.txt')):
    with open(mf, 'r', encoding='utf-8-sig') as f:
        t = f.read()
    for m in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', t):
        mod_triggers.add(m.group(1))

engine_triggers = {
    'tag', 'culture', 'primary_culture', 'culture_group', 'religion', 'religion_group', 'is_year',
    'has_reform', 'have_had_reform', 'is_playing_custom_nation', 'map_setup', 'government',
    'is_revolutionary', 'has_dlc', 'is_subject', 'num_of_cities', 'total_development',
    'has_country_flag', 'has_global_flag', 'has_ruler_flag', 'owns', 'owns_core_of', 'owns_or_subject_of',
    'capital_scope', 'region', 'area', 'superregion', 'continent', 'num_of_owned_provinces_with',
    'any_owned_province', 'all_owned_province', 'development', 'current_age', 'adm_tech', 'dip_tech', 'mil_tech',
    'technology_group', 'is_monarchy', 'is_republic', 'is_theocracy', 'is_tribal', 'is_nomad',
    'has_estate', 'estate_loyalty', 'estate_influence', 'mercantilism', 'stability', 'prestige',
    'legitimacy', 'republican_tradition', 'devotion', 'horde_unity', 'meritocracy', 'imperial_mandate',
    'is_emperor', 'is_part_of_hre', 'num_of_subjects', 'any_subject_country', 'all_subject_country',
    'army_size', 'army_size_percentage', 'manpower_percentage', 'treasury', 'inflation', 'war_exhaustion',
    'is_at_war', 'diplomatic_reputation', 'legitimacy_equivalent', 'has_country_modifier',
    'has_ruler_modifier', 'has_institution', 'is_great_power', 'calc_true_if', 'check_variable',
    'is_cossack_polity', 'is_city', 'is_free_city', 'has_seat_in_parliament', 'is_capital',
    'custom_trigger_tooltip', 'tooltip', 'has_terrain', 'overlord', 'trade_goods', 'mission_completed',
    'AND', 'OR', 'NOT'
}

all_known_triggers = vanilla_triggers | mod_triggers | engine_triggers

unknown_in_pot_trig = []
for mf in sorted(glob.glob(os.path.join(mod_path, 'common', 'government_reforms', '*.txt'))):
    fname = os.path.basename(mf)
    with open(mf, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    matches = list(re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', text))
    for m in matches:
        ref_id = m.group(1)
        start = m.end()
        depth = 1
        pos = start
        while pos < len(text) and depth > 0:
            if text[pos] == '{': depth += 1
            elif text[pos] == '}': depth -= 1
            pos += 1
        body = text[start:pos-1]
        for blk_name in ['potential', 'trigger']:
            p_start = body.find(blk_name + ' = {')
            if p_start != -1:
                b_start = p_start + len(blk_name) + 3
                b_depth = 1
                b_pos = b_start
                while b_pos < len(body) and b_depth > 0:
                    if body[b_pos] == '{': b_depth += 1
                    elif body[b_pos] == '}': b_depth -= 1
                    b_pos += 1
                blk_content = body[b_start:b_pos-1]
                for line in blk_content.splitlines():
                    line = line.split('#')[0].strip()
                    if '=' in line:
                        k = line.split('=')[0].strip()
                        if ' ' not in k and '{' not in k and k not in all_known_triggers:
                            unknown_in_pot_trig.append((fname, ref_id, blk_name, k, line))

print(f'Total unknown keys in potential/trigger: {len(unknown_in_pot_trig)}')
for u in sorted(set(unknown_in_pot_trig)):
    print(' ', u)
