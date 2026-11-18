"""Static UZH AI parity, permanent rewards and player-visible effects."""
import re
from clausewitz_testlib import ROOT, keyed_blocks, named_block, read


def event(text, eid):
    return next(b for _, b in keyed_blocks(text, 'country_event')
                if re.search(r'\bid\s*=\s*' + re.escape(eid) + r'\b', b)
                and re.search(r'\btitle\s*=', b))


missions = read('missions/Zakarpatta_Missions.txt')
events = read('events/RIP_UZH_Uzh.txt')
choice = named_block(named_block(missions, 'uz_identity_question'), 'effect')
assert 'id = uzh_identity.1' in choice
assert not re.search(r'\bai\s*=|\brandom_list\s*=|set_country_flag\s*=\s*chose_', choice)
options = [b for _, b in keyed_blocks(event(events, 'uzh_identity.1'), 'option')]
assert len(options) == 3
for option, weight in zip(options, (33, 33, 34)):
    assert re.search(r'factor\s*=\s*' + str(weight) + r'\b', named_block(option, 'ai_chance'))
    assert 'change_primary_culture' in option and 'every_owned_province' in option
    assert 'change_culture' in option and 'swap_non_generic_missions = yes' in option
    assert len(re.findall(r'set_country_flag\s*=\s*chose_', option)) == 1
    assert len(re.findall(r'clr_country_flag\s*=\s*chose_', option)) == 2

for modifier, expected in [('uz_pan_ruthenian_union', 2), ('uz_statute_codification', 3)]:
    grants = [b for _, b in keyed_blocks(missions + '\n' + events, 'add_country_modifier')
              if re.search(r'\bname\s*=\s*"?' + modifier + r'\b', b)]
    assert len(grants) == expected, modifier
    assert all(re.search(r'duration\s*=\s*-1\b', b) for b in grants), modifier

palatial = named_block(named_block(missions, 'uzh_palatial_reform'), 'effect')
assert 'custom_tooltip = UZH_palatial_reform_reward_tt' in palatial
assert len(re.findall(r'add_government_reform\s*=', palatial)) == 4
assert all('add_government_reform' not in b for _, b in keyed_blocks(palatial, 'hidden_effect'))
reforms = read('common/government_reforms/RIP_UZH_government_reforms.txt')
for key in ('uzh_palatial_uhro_reform', 'uzh_palatial_uhro_republic_reform'):
    block = named_block(reforms, key)
    assert 'governing_capacity_modifier = -0.10' in block
    assert 'technology_cost = 0.05' in block

english = dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read('localisation/RIP_UZH_realm_l_english.yml'), re.M))
border = named_block(named_block(missions, 'uzh_congress_subject_hegemony'), 'effect')
border = named_block(border, 'else_if')
text = english['UZH_congress_subject_hegemony_border_tt'].replace('§Y', '').replace('§G', '').replace('§!', '')
for effect, scale, rendered in [('add_manpower', 1000, '8,000'), ('add_mil_power', 1, '150'),
                                 ('add_army_professionalism', 100, '+5%'), ('add_army_tradition', 1, '+15')]:
    value = float(re.search(r'\b' + effect + r'\s*=\s*([\d.]+)', border)[1]) * scale
    assert value == float(rendered.replace(',', '').replace('%', ''))
    assert rendered in text
keys = ['UZH_palatial_reform_reward_tt', 'UZH_congress_subject_hegemony_border_tt',
        'UZH_constitutional_monarchy_tt', 'UZH_congress_border_bastion_subject_tt']
for key in keys[2:]:
    assert 'permanently' in english[key].lower()
assert all(s in english[keys[0]] for s in ('Tier 10', '-10%', '+5%', 'Ugro-Rusyn'))
for path in (ROOT / 'localisation/replace').glob('RIP_UZH_content_l_*.yml'):
    fallback = dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', path.read_text(encoding='utf-8-sig'), re.M))
    assert all(fallback[key] == english[key] for key in keys), path
print('PASS: shared AI/player identity event, permanent rewards, visible reforms and matching reward tooltips')
