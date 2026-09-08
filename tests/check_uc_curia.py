"""Greek Catholic transaction, migration and vanilla-balance source contracts.

These checks do not execute EU4 or establish overall campaign strength.
"""
from decimal import Decimal
import re
from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized, vanilla_root


PETS = {
    'church_tax': ('papal_sanction_for_church_taxes', 200),
    'blessing': ('papal_blessing', 150),
    'indulgence': ('papal_indulgence', 150),
    'usury': ('usury_forgiven', 100),
    'legate': ('papal_legate', 250),
    'holy_war': ('papal_sanction_for_holy_war', 200),
}
SYNOD = dict(zip('abcefghi', (
    'embrace_eastern_rite', 'accept_papal_supremacy', 'basilian_monasteries',
    'uniate_educational_network_aspect', 'defender_of_union',
    'blessing_of_basilian_order', 'blessing_of_papal_protection',
    'blessing_of_uniate_missionaries',
)))


def payload(text):
    text = re.sub(r'#[^\n]*', '', text)
    return {k: Decimal(v) for k, v in re.findall(
        r'(?m)^\s*(\w+)\s*=\s*(-?\d+(?:\.\d+)?)\s*$', text)}


# zz_ prefix is load-bearing: EU4 parses common/religions/ alphabetically and
# allowed_center_conversion cannot forward-reference a religion declared in a
# later file. greek_catholic.txt sorted BEFORE russian_orthodox.txt, so the
# engine rejected the russian_orthodox entry outright -
#   error.log: [religion.cpp:900] Unknown religion russian_orthodox defined
#              for center of reformation conversion
# and the See silently stopped converting the mod's own main faith. Vanilla has
# zero forward references across its 160 religions.
faith = read('common/religions/zz_greek_catholic.txt')
triggers = read('common/scripted_triggers/rip_faith_triggers.txt')
effects = read('common/scripted_effects/rip_uc_curia_effects.txt')
resource = read('common/scripted_effects/greek_catholic_effects.txt')
decisions = read('decisions/RIP_UniateCuria.txt')
modifiers = read('common/event_modifiers/RIP_UniateCuria_modifiers.txt')
shared = read('common/event_modifiers/RIP_faith_modifiers.txt')
hooks = read('common/on_actions/greek_catholic_on_actions.txt')

# Snapshot from EU4 1.37.5; absence of an install is unknown, not a mod error.
BASELINE = {
    'church_tax': {'global_tax_modifier': '.15', 'build_cost': '-.1'},
    'blessing': {'prestige': '1', 'land_morale': '.1'},
    'indulgence': {'legitimacy': '1', 'horde_unity': '1', 'meritocracy': '1',
                   'devotion': '1', 'republican_tradition': '.2', 'improve_relation_modifier': '.1'},
    'usury': {'interest': '-.25', 'inflation_reduction': '.1', 'yearly_corruption': '-.04'},
    'legate': {'diplomatic_reputation': '1', 'diplomatic_annexation_cost': '-.1'},
    'holy_war': {'manpower_recovery_speed': '.15', 'land_maintenance_modifier': '-.05'},
}
COUNTRY = {'tolerance_own': Decimal('1'), 'global_heathen_missionary_strength': Decimal('.01')}
install = vanilla_root()
if install is not None:
    vanilla_mods = (install / 'common/event_modifiers/00_event_modifiers.txt').read_text(encoding='cp1252')
    vanilla_faith = named_block((install / 'common/religions/00_religion.txt').read_text(encoding='utf-8-sig'), 'catholic')
    assert payload(named_block(vanilla_faith, 'country')) == COUNTRY
    for name, (vanilla, _) in PETS.items():
        assert payload(named_block(vanilla_mods, vanilla)) == {k: Decimal(v) for k, v in BASELINE[name].items()}
    print('PASS: all baselines match the installed vanilla')
else:
    print('SKIP: installed vanilla unavailable; only the versioned 1.37.5 snapshot is checked')
assert payload(named_block(faith, 'country')) == {
    k: v * Decimal('1.05') for k, v in COUNTRY.items()
}
assert 'has_patriarchs = yes' in normalized(faith)
assert not re.search(r'\b(?:papacy|fervor|holy_sites|blessings|uses_church_power)\s*=', normalized(faith))
for icon in ('michael', 'eleusa', 'pancreator', 'nicholas', 'climacus'):
    old = named_block(faith, 'rip_gc_icon_' + icon)
    assert all(v == 0 for v in payload(old).values())
    assert 'always = no' in named_block(old, 'allow')
    assert 'always = no' in named_block(old, 'visible')
for gui in ('countryreligionview.gui', 'papacy.gui', 'blessings.gui'):
    assert not (ROOT / 'interface' / gui).exists(), gui

slot = named_block(triggers, 'rip_uc_has_church_benefit')
expected_benefits = {'rip_uc_curia_' + n for n in PETS} | set(SYNOD.values())
assert set(re.findall(r'has_country_modifier\s*=\s*(\w+)', slot)) == expected_benefits
common_gate = normalized(named_block(triggers, 'rip_uc_can_petition_the_curia'))
for clause in ('religion = greek_catholic', 'has_country_flag = rip_uc_see_raised',
               'patriarch_authority = 0.25', 'exists = PAP', 'NOT = { war_with = PAP }',
               'stability = 0', 'who = ROOT value = 25',
               'NOT = { rip_uc_has_church_benefit = yes }'):
    assert clause in common_gate, clause
for name, (vanilla, ducats) in PETS.items():
    actual = named_block(modifiers, 'rip_uc_curia_' + name)
    assert payload(actual) == {k: Decimal(v) * Decimal('1.05') for k, v in BASELINE[name].items()}, name
    assert 'religion = yes' in actual
    gate = 'rip_uc_can_petition_' + name
    decision = named_block(decisions, 'rip_uc_petition_' + name)
    assert gate + ' = yes' in named_block(decision, 'allow')
    transaction = named_block(effects, 'rip_uc_petition_' + name + '_effect')
    guarded = named_block(transaction, 'if')
    assert gate + ' = yes' in named_block(guarded, 'limit')
    assert f'add_treasury = -{ducats}' in guarded
    assert f'treasury = {ducats}' in named_block(triggers, gate)
    assert guarded.count('rip_uc_spend_the_standing_effect = yes') == 1
    assert guarded.count('rip_uc_petition_cost_effect = yes') == 1
    assert f'name = rip_uc_curia_{name}' in guarded and 'duration = 7300' in guarded
    assert 'add_country_modifier' not in named_block(decision, 'effect')
    print('PASS: 105% vanilla payload and guarded payment:', name)
assert 'prestige = 25' in named_block(triggers, 'rip_uc_can_petition_legate')
assert 'is_at_war = yes' in named_block(triggers, 'rip_uc_can_petition_holy_war')
assert 'add_patriarch_authority = -0.25' in named_block(resource, 'rip_uc_spend_the_standing_effect')

# No free diplomatic slot, loyalty or monarch points hidden behind UI/cooldowns.
cost = named_block(read('common/scripted_effects/rip_faith_effects.txt'), 'rip_uc_petition_cost_effect')
assert 'add_prestige = -2' in cost and 'add_estate_loyalty' not in cost
for timer in ('rip_uc_petition_cooldown', 'rip_uc_synod_recently_sat'):
    assert payload(named_block(shared, timer)) == {}
synod = next(b for _, b in keyed_blocks(read('events/RIP_FaithCanons.txt'), 'country_event')
             if re.search(r'id\s*=\s*rip_faith\.2\b', b) and 'title =' in b)
assert 'duration = -1' not in synod and 'add_dip_power' not in synod
assert 'add_adm_power' not in named_block(decisions, 'rip_uc_hold_a_synod')
assert 'NOT = { rip_uc_has_church_benefit = yes }' in normalized(named_block(triggers, 'rip_uc_can_hold_synod'))
for letter, modifier in SYNOD.items():
    option = next(b for _, b in keyed_blocks(synod, 'option') if f'name = rip_faith.2.{letter}' in b)
    assert 'rip_uc_can_hold_synod = yes' in named_block(option, 'trigger')
    body = named_block(effects, 'rip_uc_synod_' + letter + '_effect')
    assert 'rip_uc_can_hold_synod = yes' in named_block(body, 'limit')
    assert body.count('rip_uc_synod_cost_effect = yes') == 1
    assert 'name = ' + modifier in body and 'duration = 7300' in body
    assert 'papal_influence' not in named_block(shared, modifier)
synod_cost = named_block(effects, 'rip_uc_synod_cost_effect')
assert 'add_adm_power = -100' in synod_cost
assert 'rip_uc_spend_the_standing_effect = yes' in synod_cost

# Retired free conversion loops cannot grant province-scoped authority.
assert 'rip_uc_gain_standing_effect =' not in resource
spread = read('common/scripted_effects/rip_faith_spread_effects.txt')
assert 'rip_gc_unity_spread_effect =' not in spread
assert 'rip_gc_unity_spread_effect = yes' not in hooks
tick = named_block(resource, 'rip_uc_standing_tick_effect')
assert 'papal_legate' not in tick
assert 'add_patriarch_authority = 0.02' in tick and 'add_patriarch_authority = -0.02' in tick
donation = named_block(resource, 'rip_uc_donation_effect')
assert 'rip_uc_can_donate = yes' in named_block(donation, 'limit')
assert 'add_treasury = -150' in donation and 'add_patriarch_authority = 0.10' in donation
assert 'duration = 1825' in donation

# Reopening a save keeps its new benefit; leaving the faith removes the benefit
# but retains zero-payload payment timers and the one-time migration flag.
migration = named_block(effects, 'rip_uc_curia_migration_effect')
greek = named_block(migration, 'if')
assert 'religion = greek_catholic' in named_block(greek, 'limit')
for original, _ in PETS.values():
    assert f'remove_country_modifier = {original}' in greek
    assert migration.count(f'remove_country_modifier = {original}') == 1
once = named_block(greek, 'if', occurrence=2)
assert 'NOT = { has_country_flag = rip_uc_curia_v2_migrated }' in named_block(once, 'limit')
assert 'rip_uc_clear_church_benefits_effect = yes' in once
assert 'clr_country_flag = rip_uc_curia_v2_migrated' not in effects
assert 'remove_country_modifier = rip_uc_donation_recently_sent' not in effects
for hook in ('on_startup', 'on_religion_change', 'on_bi_yearly_pulse'):
    assert 'rip_uc_curia_migration_effect = yes' in named_block(hooks, hook)
assert 'rip_uc_standing_tick_effect = yes' in named_block(hooks, 'on_bi_yearly_pulse')

info = read('events/RIP_UniateCuria.txt')
assert 'rip_uc_curia.1' in decisions and 'is_triggered_only = yes' in info
assert not re.search(r'\badd_\w+\s*=', info)
loc_path = ROOT / 'localisation/rip_uc_curia_l_english.yml'
assert loc_path.read_bytes().startswith(b'\xef\xbb\xbf')
loc = loc_path.read_text(encoding='utf-8-sig')
for key in expected_benefits - set(SYNOD.values()):
    assert f' {key}:0 ' in loc
print('PASS: one benefit, no free cancel, retired conversion rewards, migration, native GUI isolation')
print('LIMIT: 105% compares matching numeric bonuses, not total religion/campaign effectiveness')
