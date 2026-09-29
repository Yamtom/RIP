"""Execute actual settlement scripts against bounded state-transition fixtures.

This deliberately small interpreter rejects unknown operations. It is a source
contract test, not the EU4 engine, a save loader or a campaign balance simulator.
"""
from copy import deepcopy
import re

from clausewitz_testlib import ROOT, read, named_block, normalized, vanilla_root, keyed_blocks


def parse(text):
    tokens = re.findall(r'"[^"\n]*"|[{}=]|[^\s{}=]+', re.sub(r'#[^\n]*', '', text))
    pos = 0

    def block():
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]
            assert tokens[pos + 1] == '=', key
            pos += 2
            if tokens[pos] == '{':
                pos += 1
                value = block()
                assert tokens[pos] == '}'
                pos += 1
            else:
                value = tokens[pos].strip('"')
                pos += 1
            result.append((key, value))
        return result
    return block()


TRIGGERS = {}
EFFECTS = {}
# Faith triggers were consolidated into the settlement trigger file.
for file in ('rip_religion_settlement_triggers', 'rip_crusade_triggers', 'rus_russian_orthodox_triggers'):
    TRIGGERS.update(parse(read('common/scripted_triggers/' + file + '.txt')))
for file in ('rip_religion_settlement_effects', 'rip_crusade_effects', 'rip_parish_visit_effects', 'rip_faith_policy_effects', 'russian_orthodox_effects', 'greek_catholic_effects'):
    EFFECTS.update(parse(read('common/scripted_effects/' + file + '.txt')))


class World:
    def __init__(self):
        self.day = 0
        self.year = 1600
        self.flags = {}
        self.countries = {}
        self.provinces = {}
        self.events = []

    def country(self, tag, religion='orthodox'):
        state = dict(kind='country', id=tag, religion=religion, flags={}, modifiers={}, variables={},
                     treasury=1000, adm_power=500, dip_power=500, mil_power=500,
                     patriarch_authority=1, papal_influence=0, prestige=60, stability=2, total_development=300,
                     is_subject=False, is_at_war=False, wars=set(), allies=set(), truces=set(),
                     cbs={}, capital=None, dlcs={'Third Rome'})
        self.countries[tag] = state
        return state

    def province(self, number, owner, religion='orthodox'):
        state = dict(kind='province', id=str(number), religion=religion, owner=owner['id'],
                     controlled_by=owner['id'], core=owner['id'], is_city=True, development=12,
                     is_reformation_center=False, is_island=False, modifiers={}, flags={}, region='ruthenia_region')
        self.provinces[str(number)] = state
        if owner['capital'] is None:
            owner['capital'] = str(number)
        return state

    def ref(self, key, scope, root, prev):
        if key == 'ROOT': return root
        if key == 'PREV': return prev
        if key == 'owner': return self.countries[scope['owner']]
        if key == 'capital_scope': return self.provinces[scope['capital']]
        return self.provinces.get(key) or self.countries.get(key)

    def collection(self, key, scope):
        if 'owned_province' in key:
            return [p for p in self.provinces.values() if p['owner'] == scope['id']]
        return list((self.provinces if 'province' in key else self.countries).values())

    def condition(self, key, value, scope, root, prev):
        if key in TRIGGERS:
            return self.gate(TRIGGERS[key], scope, root, prev) == (value == 'yes')
        if key in ('AND', 'custom_trigger_tooltip'): return self.gate(value, scope, root, prev)
        if key == 'OR': return any(self.condition(k, v, scope, root, prev) for k, v in value)
        if key == 'NOT': return not self.gate(value, scope, root, prev)
        if key == 'tooltip': return True
        if key == 'always': return value == 'yes'
        if key.startswith('any_'):
            return any(self.gate(value, item, root, scope) for item in self.collection(key, scope))
        if key == 'calc_true_if':
            fields = dict(value)
            assert set(fields) == {'all_province', 'amount'}
            return sum(self.gate(fields['all_province'], p, root, scope) for p in self.provinces.values()) >= int(fields['amount'])
        if isinstance(value, list) and (key in ('ROOT', 'PREV', 'owner', 'capital_scope') or key in self.provinces or key in self.countries):
            target = self.ref(key, scope, root, prev)
            return target is not None and self.gate(value, target, root, scope)
        if key in ('has_country_flag', 'has_global_flag'):
            return value in (self.flags if key == 'has_global_flag' else scope['flags'])
        if key == 'had_global_flag':
            fields = dict(value)
            return fields['flag'] in self.flags and self.day - self.flags[fields['flag']] >= int(fields['days'])
        if key in ('has_country_modifier', 'has_province_modifier'):
            return scope['modifiers'].get(value, -1) > self.day
        if key == 'religion':
            religion = self.ref(value, scope, root, prev)['religion'] if value in ('ROOT', 'PREV') else value
            return scope['religion'] == religion
        if key == 'uses_patriarch_authority':
            return (scope['religion'] in ('orthodox', 'russian_orthodox', 'greek_catholic')) == (value == 'yes')
        if key == 'is_religion_enabled': return self.year >= (1439 if value == 'greek_catholic' else 1448)
        if key == 'exists': return value in self.countries
        if key == 'has_owner': return (scope.get('owner') in self.countries) == (value == 'yes')
        if key == 'has_dlc': return value in scope['dlcs']
        if key in ('war_with', 'alliance_with', 'truce_with'):
            other = root['id'] if value == 'ROOT' else value
            return other in scope[{'war_with': 'wars', 'alliance_with': 'allies', 'truce_with': 'truces'}[key]]
        if key == 'owns': return self.provinces[value]['owner'] == scope['id']
        if key in ('owned_by', 'controlled_by', 'is_core', 'tag'):
            other = root['id'] if value == 'ROOT' else value
            return scope[{'owned_by': 'owner', 'controlled_by': 'controlled_by', 'is_core': 'core', 'tag': 'id'}[key]] == other
        if key == 'check_variable':
            fields = dict(value)
            return scope['variables'].get(fields['which'], 0) >= float(fields['value'])
        if key == 'has_opinion': return True  # PAP exists/war gates are tested; opinions are source-checked.
        if key == 'is_year': return self.year >= int(value)
        if key == 'region': return scope['region'] == value
        if key in scope:
            return scope[key] == (value == 'yes') if value in ('yes', 'no') else scope[key] >= float(value)
        raise AssertionError('Unsupported trigger: ' + key)

    def gate(self, items, scope, root=None, prev=None):
        return all(self.condition(k, v, scope, root or scope, prev) for k, v in items)

    def execute(self, items, scope, root=None, prev=None):
        root = root or scope
        chain_taken = False
        for key, value in items:
            if key in ('if', 'else_if', 'else'):
                fields = dict(value)
                if key == 'if': chain_taken = False
                if not chain_taken and (key == 'else' or self.gate(fields['limit'], scope, root, prev)):
                    self.execute([(k, v) for k, v in value if k != 'limit'], scope, root, prev)
                    chain_taken = True
            elif key in EFFECTS:
                body = EFFECTS[key]
                if isinstance(value, list):
                    params = dict(value)
                    def substitute(nodes):
                        return [(params.get(k.strip('$'), k) if k.startswith('$') else k,
                                 substitute(v) if isinstance(v, list) else params.get(v.strip('$'), v) if v.startswith('$') else v) for k, v in nodes]
                    body = substitute(body)
                else: assert value == 'yes'
                self.execute(body, scope, root, prev)
            elif key.startswith(('every_', 'random_')):
                fields = dict(value)
                targets = [p for p in self.collection(key, scope) if self.gate(fields.get('limit', []), p, root, scope)]
                if key.startswith('random_'): targets = targets[:1]
                for target in targets:
                    self.execute([(k, v) for k, v in value if k != 'limit'], target, root, scope)
            elif key in ('ROOT', 'PREV', 'capital_scope', 'owner') or key in self.provinces:
                self.execute(value, self.ref(key, scope, root, prev), root, scope)
            elif key == 'change_religion': scope['religion'] = value
            elif key in ('set_country_flag', 'clr_country_flag', 'set_global_flag', 'clr_global_flag'):
                flags = self.flags if 'global' in key else scope['flags']
                if key.startswith('set'): flags[value] = self.day
                else: flags.pop(value, None)
            elif key in ('add_country_modifier', 'add_province_modifier'):
                fields = dict(value)
                duration = int(fields['duration'])
                scope['modifiers'][fields['name']] = float('inf') if duration == -1 else self.day + duration
            elif key in ('remove_country_modifier', 'remove_province_modifier'): scope['modifiers'].pop(value, None)
            elif key in ('add_reform_center', 'remove_reform_center'): scope['is_reformation_center'] = key.startswith('add')
            elif key == 'set_variable':
                fields = dict(value)
                scope['variables'][fields['which']] = float(fields['value'])
            elif key in ('add_casus_belli', 'remove_casus_belli'):
                fields = dict(value)
                other = self.ref(fields['target'], scope, root, prev)
                cb = (fields['type'], other['id'])
                if key.startswith('add'): scope['cbs'][cb] = self.day + int(fields['months']) * 30
                else: scope['cbs'].pop(cb, None)
            elif key == 'country_event': self.events.append((scope['id'], dict(value)['id']))
            elif key == 'add_opinion': pass  # No resource payload; API/scope checked separately.
            elif key.startswith('add_') and key[4:] in scope: scope[key[4:]] += float(value)
            else: raise AssertionError('Unsupported effect: ' + key)

    def run(self, name, scope, **params):
        self.execute([(name, list(params.items()) if params else 'yes')], scope)


def fixture(religion='orthodox'):
    world = World()
    country = world.country('KIE', religion)
    world.province(280, country)
    world.province(281, country)
    world.country('PAP', 'catholic')
    return world, country


def run_cases():
    cases = 0
    for faith in ('orthodox', 'russian_orthodox', 'greek_catholic', 'catholic', 'sunni'):
        w, c = fixture(faith)
        c.update(patriarch_authority=0, adm_power=0)
        w.run('rip_faith_mission_resource_effect', c, PA='0.1', PI='20', ADM='25')
        expected = (.1, 0, 0) if faith in ('orthodox', 'russian_orthodox', 'greek_catholic') else (0, 20, 0) if faith == 'catholic' else (0, 0, 25)
        assert (c['patriarch_authority'], c['papal_influence'], c['adm_power']) == expected
        cases += 1
    # Adoption remains idempotent, including a change away/back and a moved capital.
    for faith, effect in (('russian_orthodox', 'rip_faith_adopt_muscovite_church_effect'), ('greek_catholic', 'rip_faith_adopt_union_effect')):
        for dlc in (True, False):
            w, c = fixture()
            if not dlc: c['dlcs'].clear()
            w.run(effect, c)
            assert c['religion'] == faith and w.provinces['280']['religion'] == faith
            assert w.provinces['281']['religion'] == 'orthodox'
            before = deepcopy(c)
            w.run(effect, c)
            assert c == before
            c['religion'] = 'catholic'
            c['capital'] = '281'
            w.run(effect, c)
            assert w.provinces['281']['religion'] == 'orthodox' and c['prestige'] == before['prestige']
            cases += 1
        for invalid in ('sunni', 'occupied', 'noncore'):
            w, c = fixture()
            p = w.provinces['280']
            p['religion' if invalid == 'sunni' else 'controlled_by' if invalid == 'occupied' else 'core'] = 'sunni' if invalid == 'sunni' else 'PAP'
            w.run(effect, c)
            assert p['religion'] != faith
            cases += 1
    # All council choices recheck payment, faith and the ten-year term.
    for faith, helper, choices in (
        ('orthodox', 'rip_kyiv_enact_council_policy_effect', ('rip_kyiv_elected_metropolitan', 'rip_kyiv_brotherhood_charters', 'rip_kyiv_church_rights')),):
        for choice in choices:
            w, c = fixture(faith)
            w.run(helper, c, POLICY=choice)
            assert c['treasury'] == 900 and c['adm_power'] == 450 and c['patriarch_authority'] == .9
            paid = deepcopy(c)
            w.run(helper, c, POLICY=choice)
            assert c == paid
            c['religion'] = 'catholic'
            w.run('rip_faith_settlement_upkeep_effect', c)
            assert choice not in c['modifiers'] and c['modifiers']
            c['religion'] = faith
            w.day = 3649
            w.run(helper, c, POLICY=choice)
            assert c['treasury'] == 900
            w.day = 3650
            w.run(helper, c, POLICY=choice)
            assert c['treasury'] == 800
            cases += 1
            for update in ({'treasury': 99}, {'adm_power': 49}, {'patriarch_authority': .09}, {'stability': 0}, {'is_at_war': True}, {'religion': 'catholic'}):
                w, c = fixture(faith)
                c.update(update)
                before = deepcopy(c)
                w.run(helper, c, POLICY=choice)
                assert c == before, update
                cases += 1
    # Moscow council fuel is covered by the focused church redesign contract.
    # A stale Brest response cannot change faith after PAP disappears or a prior signature.
    for update in ('valid', 'before_brest', 'no_pope', 'war_pope', 'signed', 'wrong_faith', 'poor'):
        w, c = fixture()
        c['flags']['pursuing_uniate_union'] = 0
        if update == 'before_brest': w.year = 1595
        if update == 'no_pope': del w.countries['PAP']
        if update == 'war_pope': c['wars'].add('PAP')
        if update == 'signed': c['flags']['union_of_brest_happened'] = 0
        if update == 'wrong_faith': c['religion'] = 'catholic'
        if update == 'poor': c['adm_power'] = 99
        assert w.gate(TRIGGERS['rip_uc_can_accept_brest_trigger'], c) == (update == 'valid')
        cases += 1
    # Old-save migration records initialization before granting any new rewards.
    for faith in ('russian_orthodox', 'greek_catholic'):
        w, c = fixture(faith)
        c['modifiers']['rip_parish_visit_recent'] = 3650
        c['modifiers']['uniate_educational_network'] = float('inf')
        c['cbs'][('cb_crusade_for_constantinople', 'PAP')] = float('inf')
        w.run('rip_faith_settlement_migration_effect', c)
        w.run('rip_faith_initialize_hierarchy_effect', c)
        assert w.provinces['280']['religion'] == 'orthodox' and c['prestige'] == 60
        assert c['modifiers']['rip_parish_visit_recent'] == 3650
        assert not c['cbs']
        assert 'rip_once_greek_catholic_education_decision' in c['flags']
        assert 'uniate_educational_network' not in c['modifiers']
        paid = deepcopy(c)
        w.run('rip_faith_settlement_migration_effect', c)
        assert c == paid
        cases += 1
    # Campaign lifecycle reads real start, join, resolution and cleanup scripts.
    for outcome in ('win', 'forfeit', 'timeout', 'faith', 'target_owner', 'target_faith', 'annexed_leader'):
        w, c = fixture()
        target = w.country('TUR', 'sunni')
        city = w.province(151, target, 'sunni')
        w.province(379, target, 'sunni')
        ally = w.country('CHR')
        c['allies'].add('CHR'); ally['allies'].add('KIE')
        w.run('rip_crusade_start_effect', c, PROVINCE='151', YEAR='1525', ACTIVE_FLAG='orthodox_crusade_constantinople_active', TARGET_FLAG='orthodox_crusade_target_constantinople', CAMPAIGN='orthodox_crusade_for_constantinople', CB='cb_crusade_for_constantinople', INVITATION='orthodox_crusade.2', ANNOUNCEMENT='orthodox_crusade.1')
        assert c['treasury'] == 800 and c['cbs'] and 'rip_crusade_active' in w.flags
        w.run('rip_crusade_join_effect', ally)
        assert ally['cbs'] and ally['patriarch_authority'] == .95
        if outcome == 'win':
            city.update(owner='KIE', controlled_by='KIE')
            assert not w.gate(TRIGGERS['rip_crusade_should_finish_trigger'], c), 'conquest must leave time for ordinary conversion'
            city['religion'] = 'orthodox'
        if outcome == 'timeout': w.day = 3650
        if outcome == 'faith': c['religion'] = 'catholic'
        if outcome == 'target_owner': city['owner'] = 'PAP'
        if outcome == 'target_faith': target['religion'] = 'orthodox'
        if outcome == 'annexed_leader': del w.countries['KIE']
        if outcome == 'forfeit': w.run('rip_crusade_resolve_effect', c)
        else: w.run('rip_crusade_maintenance_effect', ally if outcome == 'annexed_leader' else c)
        assert 'rip_crusade_active' not in w.flags and 'rip_crusade_last_ended' in w.flags, outcome
        for country in w.countries.values():
            assert not country['cbs'], (outcome, country['id'], country['cbs'])
            assert 'orthodox_crusade_leader' not in country['modifiers']
            assert 'orthodox_crusade_participant' not in country['modifiers']
        if outcome == 'win':
            assert c['adm_power'] == 525 and c['prestige'] == 70
            w.run('rip_crusade_resolve_effect', c)
            w.run('constantinople_liberation_rewards', c)
            assert c['adm_power'] == 525
        before = deepcopy(ally)
        w.run('rip_crusade_join_effect', ally)
        assert ally == before, 'stale invitation rejoined a completed campaign'
        cases += 1
    return cases


def contracts():
    # Replacing a timed policy cannot reopen one-shot historical payouts.
    for filename, repeatable in (
        ('GreekCatholicDecisions', {'convert_to_greek_catholic_decision'}),
        ('RussianOrthodoxDecisions', {'convert_to_russian_orthodox_decision', 'force_convert_province_decision', 'russify_province_decision'})):
        source = read('decisions/' + filename + '.txt')
        for name in re.findall(r'(?m)^\t(\w+) = \{', source):
            if name in repeatable: continue
            body = named_block(source, name)
            flag = 'rip_once_' + name
            assert f'NOT = {{ has_country_flag = {flag} }}' in named_block(body, 'potential')
            payout = named_block(body, 'effect')
            if name == 'greek_catholic_education_decision':
                assert 'establish_greek_catholic_education = yes' in payout
                payout = named_block(read('common/scripted_effects/greek_catholic_effects.txt'),
                                     'establish_greek_catholic_education')
                assert 'limit = { rip_uc_can_found_schools = yes }' in payout
            assert f'set_country_flag = {flag}' in payout
    # All country paths use the same idempotent bridge; province loops cannot call it.
    # The old automatic Union-centre event file is intentionally retired.
    assert not (ROOT / 'events/UniateReformationSpread.txt').exists()
    for filename in ('events/RussianOrthodox.txt', 'events/UniateChurch.txt', 'decisions/GreekCatholicDecisions.txt'):
        source = normalized(read(filename))
        assert not re.search(r'change_religion = (?:russian_orthodox|greek_catholic)', source), filename
        assert not re.search(r'add_base_(?:tax|production|manpower)\s*=', source), filename
    for filename in ('russian_orthodox', 'zz_greek_catholic'):
        assert 'rip_faith_initialize_hierarchy_effect = yes' in named_block(read('common/religions/' + filename + '.txt'), 'on_convert')
    assert 'rip_faith_adopt_union_effect = yes' in read('common/scripted_effects/rip_uniate_crown_effects.txt')
    assert 'rip_faith_adopt_muscovite_church_effect = yes' in read('common/scripted_effects/russian_orthodox_effects.txt')
    crown = named_block(read('common/scripted_effects/rip_uniate_crown_effects.txt'), 'rip_ucr_take_the_church_effect')
    assert 'set_country_flag = pursuing_uniate_union' not in crown
    assert 'set_country_flag = union_of_brest_happened' not in crown
    gc = named_block(read('common/religions/zz_greek_catholic.txt'), 'greek_catholic')
    assert re.search(r'(?m)^\s*date\s*=\s*1439\.7\.6\s*$', gc)
    assert re.search(r'(?m)^\s*has_patriarchs\s*=\s*yes\s*$', gc)
    assert re.search(r'(?m)^\s*orthodox_icons\s*=\s*\{', gc)
    assert not re.search(r'(?m)^\s*hre_heretic_religion\s*=', gc)
    # Internal hierarchy and local rite recognition remain independent systems.
    union_triggers = read('common/scripted_triggers/rip_church_union_triggers.txt')
    union_effects = read('common/scripted_effects/rip_church_union_effects.txt')
    assert 'which = rip_church_communion' not in union_effects
    assert 'which = rip_church_papal_standing' not in union_effects
    assert 'set_province_flag = rip_church_rite_recognized' in union_effects
    assert 'owner = { religion = greek_catholic }' in named_block(union_triggers, 'rip_church_can_recognize_rite')
    brest = named_block(read('decisions/GreekCatholicDecisions.txt'), 'convert_to_greek_catholic_decision')
    assert 'is_year = 1596' in named_block(brest, 'potential')
    brest_effect = named_block(brest, 'effect')
    assert 'set_country_flag = pursuing_uniate_union' in brest_effect
    assert 'set_country_flag = union_of_brest_happened' in brest_effect
    brest_event = read('events/UniateChurch.txt')
    assert brest_event.count('trigger = { rip_uc_can_accept_brest_trigger = yes }') == 2
    assert brest_event.count('set_country_flag = union_of_brest_happened') == 2
    khmelnytsky = next(block for _, block in keyed_blocks(read('events/KhmelnytskyUprisings.txt'), 'country_event')
                       if 'id = khmelnytsky_events.7' in block)
    assert 'is_year = 1596' in named_block(khmelnytsky, 'trigger')
    west_events = read('events/WestUkraineHistory.txt')
    west_union = next(block for _, block in keyed_blocks(west_events, 'country_event')
                      if 'id = west_ukraine_history.3' in block)
    assert 'is_year = 1596' in named_block(west_union, 'trigger')
    west_accept = next(block for _, block in keyed_blocks(west_union, 'option')
                       if 'name = west_ukraine_history.3.a' in block)
    assert 'rip_faith_adopt_union_effect = yes' in west_accept
    assert 'set_country_flag = union_of_brest_happened' in west_accept
    assert 'provincial_uniate_resistance' in west_accept
    assert 'change_religion = catholic' not in west_accept
    west_resistance = named_block(west_accept, 'every_owned_province')
    assert 'religion = orthodox' in named_block(west_resistance, 'limit')
    assert 'change_religion' not in west_resistance
    west_dispute = next(block for _, block in keyed_blocks(west_events, 'country_event')
                        if 'id = west_ukraine_history.4' in block)
    west_press = next(block for _, block in keyed_blocks(west_dispute, 'option')
                      if 'name = west_ukraine_history.4.a' in block)
    assert 'rip_church_historical_rome_effect = yes' in west_press
    assert 'add_papal_influence' not in west_press
    assert 'change_religion' not in west_press
    assert 'has_province_flag = rip_church_rite_recognized' in named_block(west_dispute, 'trigger')
    hierarchy_init = named_block(read('common/scripted_effects/rip_religion_settlement_effects.txt'), 'rip_faith_initialize_hierarchy_effect')
    assert 'set_country_flag = pursuing_uniate_union' not in hierarchy_init
    assert 'set_country_flag = union_of_brest_happened' not in hierarchy_init
    brest_gate = dict(parse(read('common/scripted_triggers/rip_religion_settlement_triggers.txt')))['rip_uc_can_accept_brest_trigger']
    assert ('is_year', '1596') in brest_gate
    # The Greek Catholic conversion profile belonged to the retired Union centre.
    assert not (ROOT / 'common/religious_conversions/zz_RIP_greek_catholic.txt').exists()
    events = read('events/OrthodoxCrusade.txt')
    assert not re.search(r'add_base_|change_religion\s*=', events)
    assert 'rip_faith_pilgrimage_recent duration = 3650' in events
    # Exact tier equality prevents compatibility from buffing the buildings.
    install = vanilla_root()
    if install:
        donor = (install / 'common/great_projects/01_monuments.txt').read_text(encoding='utf-8-sig')
        actual = read('common/great_projects/zz_RIP_orthodox_monuments.txt')
        for key in ('kiev_pechersk_lavra', 'rila_monasteries'):
            old, new = named_block(donor, key), named_block(actual, key)
            for tier in range(4): assert normalized(named_block(old, f'tier_{tier}')) == normalized(named_block(new, f'tier_{tier}'))
            for gate in ('build_trigger', 'can_use_modifiers_trigger', 'can_upgrade_trigger'):
                assert 'religion = russian_orthodox' in named_block(new, gate)
        rebels = (install / 'common/rebel_types/orthodox.txt').read_text(encoding='utf-8-sig')
        assert 'change_religion = orthodox' in named_block(rebels, 'demands_enforced_effect')
    # A change of jurisdiction cannot erase the evidence needed by campaign cleanup.
    history = read('common/scripted_effects/rip_faith_history_cleanup_effects.txt')
    assert 'remove_country_modifier = orthodox_crusade_participant' not in history
    for prefix in ('rip_ro_sobor_', 'rip_kyiv_'):
        assert prefix in read('common/scripted_effects/rip_religion_settlement_effects.txt')


# ---------------------------------------------------------------------------
# Guarantee of community rights (29 September 2026).
#
# The province action (internal ids still say "recognize") guarantees another
# confessional community its rights; it is not that community accepting the
# Union. The review that named it also found that the ecumenical settlement
# changed nothing in the province and never reached Catholic states.
#
# Every contract below is a PURE function of text: it takes the source of a file
# (it never reads the repository) and returns a list of problems, empty when the
# text honours the contract. That is what makes each one provable - the same
# function can be pointed at an older revision, or at a deliberately damaged
# copy, to show that it fails when it should. guarantee_of_rights_contracts()
# feeds them the live files.
# ---------------------------------------------------------------------------
RITE_FAVOURED = 'rip_church_rite_favoured'
RITE_ECUMENICAL = 'rip_church_rite_ecumenical'
RELATIONS_EFFECT = 'rip_church_refresh_relations_effect'
ECUMENICAL_OPINION = 'rip_church_opinion_gc_ecumenical'


def _subtree(key, value):
    """The node itself and every node below it, depth first."""
    yield key, value
    if isinstance(value, list):
        for child_key, child_value in value:
            yield from _subtree(child_key, child_value)


def _walk(nodes):
    for key, value in nodes:
        yield from _subtree(key, value)


def _body(text, name):
    """Children of the top-level block `name`, or None when it is absent."""
    try:
        return dict(parse(named_block(text, name)))[name]
    except KeyError:
        return None


def modifier_offsets(text, name):
    """{key: number} of one flat modifier definition, or None when it is absent."""
    body = _body(text, name)
    return None if body is None else {key: float(value) for key, value in body}


def ecumenical_rite_problems(modifiers_text):
    """The twenty-year settlement must deepen the province guarantee, not repeat it.

    rip_church_rite_favoured and rip_church_rite_ecumenical were both
    { local_unrest = -0.5 }, so concluding the settlement changed nothing here.
    """
    rite, favoured, ecumenical = (modifier_offsets(modifiers_text, name)
                                  for name in ('rip_church_rite', RITE_FAVOURED, RITE_ECUMENICAL))
    if None in (rite, favoured, ecumenical):
        return ['rip_church_rite, rip_church_rite_favoured or rip_church_rite_ecumenical is missing']
    problems = []
    if ecumenical == favoured:
        problems.append('ecumenical is identical to favoured: concluding the settlement changes nothing in the province')
    unrest, plain = ecumenical.get('local_unrest', 0), favoured.get('local_unrest', 0)
    if not unrest < plain < 0:
        problems.append(f'ecumenical local_unrest {unrest:g} is not strictly below favoured {plain:g}')
    for key in ('local_tax_modifier', 'local_manpower_modifier'):
        if not ecumenical.get(key, 0) > 0:
            problems.append(f'ecumenical has no positive {key}')
        if favoured.get(key, 0) != 0:
            problems.append(f'favoured must not carry {key}: only the settlement eases the tax and levy cost')
        # The guarantee stays a cost; the settlement only makes it smaller.
        if not rite.get(key, 0) < rite.get(key, 0) + ecumenical.get(key, 0) < 0:
            problems.append(f'net {key} with the settlement is not between the ordinary cost and zero')
    return problems


def alternative_rite_modifier_problems(union_effects_text):
    """favoured and ecumenical are alternatives, never stacked.

    The ecumenical offsets are positive and the net figures in the tooltips assume
    the province holds exactly one of them.
    """
    name = 'rip_church_gc_refresh_parishes_effect'
    body = _body(union_effects_text, name)
    if body is None:
        return [name + ' is missing']
    wanted = {RITE_FAVOURED, RITE_ECUMENICAL}

    def added(nodes):
        return sorted(dict(value)['name'] for key, value in nodes
                      if key == 'add_province_modifier' and dict(value)['name'] in wanted)

    problems = []
    if added(_walk(body)) != sorted(wanted):
        problems.append('favoured and ecumenical must each be added exactly once in ' + name)
    pairs = []

    def visit(nodes):
        for index, (key, value) in enumerate(nodes):
            if isinstance(value, list):
                if key == 'if' and index + 1 < len(nodes) and nodes[index + 1][0] == 'else':
                    pairs.append((value, nodes[index + 1][1]))
                visit(value)
    visit(body)
    if not any(added(then) == [RITE_ECUMENICAL] and added(other) == [RITE_FAVOURED]
               and ('has_country_flag', 'rip_church_ecumenical') in list(_walk(dict(then).get('limit', [])))
               for then, other in pairs):
        problems.append('ecumenical (if the owner is ecumenical) and favoured (else) are not exclusive branches of one if/else')
    return problems


def _every_country(effect_text):
    body = _body(effect_text, RELATIONS_EFFECT)
    loops = [] if body is None else [value for key, value in body if key == 'every_country']
    return loops[0] if len(loops) == 1 else None


def _scoped_values(nodes, wanted, under_root=False, found=None):
    """Values of trigger `wanted` as (country side, ROOT side) sets."""
    found = (set(), set()) if found is None else found
    for key, value in nodes:
        if key == wanted:
            found[under_root].add(value)
        elif isinstance(value, list):
            _scoped_values(value, wanted, under_root or key == 'ROOT', found)
    return found


def relation_ecumenical_problems(effect_text):
    """The ecumenical opinion must be reachable by the states it is meant for.

    It used to sit inside the else_if branch for Orthodox <-> Greek Catholic. A
    Catholic country is consumed by the earlier catholic <-> greek_catholic
    else_if, so the +15 never reached it although its condition named catholic.
    """
    body = _every_country(effect_text)
    if body is None:
        return [RELATIONS_EFFECT + ' has no single every_country loop']
    body = [node for node in body if node[0] != 'limit']

    def opinion_with(node, verb):
        return any(key == verb and ('modifier', ECUMENICAL_OPINION) in value
                   for key, value in _subtree(*node) if isinstance(value, list))

    def grants(nodes, who):
        return any(key == 'add_opinion' and dict(value) == {'who': who, 'modifier': ECUMENICAL_OPINION}
                   for key, value in nodes)

    carriers = [index for index, node in enumerate(body) if opinion_with(node, 'add_opinion')]
    if not carriers:
        return ['the ecumenical opinion is never added']
    problems = []
    for index in carriers:
        key, value = body[index]
        if key != 'if':
            problems.append(f'the ecumenical opinion is added inside a `{key}` branch of the country loop, '
                            'so an earlier branch of that chain can consume the country before it')
            continue
        if any(child_key in ('if', 'else_if', 'else') for child_key, _ in value):
            problems.append('the ecumenical opinion sits under a second conditional inside its own `if`')
        if not grants(value, 'ROOT') or not any(
                child_key == 'ROOT' and grants(child, 'PREV') for child_key, child in value):
            problems.append('the ecumenical opinion is not granted in both directions, directly inside its `if`')
        if any(later[0] in ('else_if', 'else') for later in body[index + 1:]):
            problems.append('the ecumenical `if` is not placed after the whole if / else_if chain')
        if any(opinion_with(later, 'remove_opinion') for later in body[index + 1:]):
            problems.append('the ecumenical opinion is removed after it is added')
        if not any(opinion_with(earlier, 'remove_opinion') for earlier in body[:index]):
            problems.append('the ecumenical opinion is never removed before it is re-added')
        limit = dict(value).get('limit', [])
        religions, root_religions = _scoped_values(limit, 'religion')
        for side, seen in (('country', religions), ('ROOT', root_religions)):
            for faith in ('orthodox', 'catholic', 'greek_catholic'):
                if faith not in seen:
                    problems.append(f'the ecumenical condition never tests religion = {faith} on the {side} side')
            if 'russian_orthodox' in seen:
                problems.append(f'the ecumenical condition includes russian_orthodox on the {side} side; it is excluded')
        flags = _scoped_values(limit, 'has_country_flag')
        if not all('rip_church_ecumenical' in side for side in flags):
            problems.append('the ecumenical condition must test rip_church_ecumenical on the Greek Catholic side in both directions')
    return problems


def _holds(items, scope, root):
    return all(_trigger(key, value, scope, root) for key, value in items)


def _trigger(key, value, scope, root):
    if key == 'religion': return scope['religion'] == value
    if key == 'has_country_flag': return value in scope['flags']
    if key == 'AND': return _holds(value, scope, root)
    if key == 'OR': return any(_trigger(k, v, scope, root) for k, v in value)
    if key == 'NOT': return not _holds(value, scope, root)
    if key == 'ROOT': return _holds(value, root, root)
    raise ValueError('trigger outside the relation model: ' + key)


def _apply(nodes, scope, root, prev, opinions):
    """Run one effect body over two country fixtures; opinions holds (holder, target, modifier)."""
    chain_done = False
    for key, value in nodes:
        if key in ('if', 'else_if', 'else'):
            if key == 'if': chain_done = False
            if chain_done: continue
            if key == 'else' or _holds(dict(value)['limit'], scope, root):
                chain_done = True
                _apply([node for node in value if node[0] != 'limit'], scope, root, prev, opinions)
        elif key in ('add_opinion', 'remove_opinion'):
            fields = dict(value)
            triple = (scope['id'], {'ROOT': root, 'PREV': prev}[fields['who']]['id'], fields['modifier'])
            (opinions.add if key == 'add_opinion' else opinions.discard)(triple)
        elif key == 'ROOT':
            _apply(value, root, root, scope, opinions)
        else:
            raise ValueError('effect outside the relation model: ' + key)


def relation_outcome_problems(effect_text):
    """Run the country loop for each pairing and compare the opinions that result.

    Catholic states get the ecumenical +15 on top of the +40 of the middle
    course; Orthodox states keep it; russian_orthodox never had it; nobody gets
    it before the Greek Catholic side has concluded the settlement, and a bonus
    already held is withdrawn when the settlement lapses.
    """
    body = _every_country(effect_text)
    if body is None:
        return [RELATIONS_EFFECT + ' has no single every_country loop']
    body = [node for node in body if node[0] != 'limit']
    catholic, orthodox = 'rip_church_opinion_gc_catholic_middle', 'rip_church_opinion_gc_orthodox_middle'
    cases = (
        ('catholic', 'greek_catholic', True, {catholic, ECUMENICAL_OPINION}),
        ('orthodox', 'greek_catholic', True, {orthodox, ECUMENICAL_OPINION}),
        ('russian_orthodox', 'greek_catholic', True, {orthodox}),
        ('greek_catholic', 'catholic', True, {catholic, ECUMENICAL_OPINION}),
        ('greek_catholic', 'orthodox', True, {orthodox, ECUMENICAL_OPINION}),
        ('catholic', 'greek_catholic', False, {catholic}),
        ('orthodox', 'greek_catholic', False, {orthodox}),
        ('catholic', 'greek_catholic', False, {catholic}, 'the +15 is already held'),
    )
    problems = []
    for other_faith, root_faith, settled, expected, *lapsed in cases:
        other = dict(id='OTHER', religion=other_faith, flags=set())
        root = dict(id='ROOT', religion=root_faith, flags=set())
        if settled:
            (other if other_faith == 'greek_catholic' else root)['flags'].add('rip_church_ecumenical')
        opinions = {('OTHER', 'ROOT', ECUMENICAL_OPINION), ('ROOT', 'OTHER', ECUMENICAL_OPINION)} if lapsed else set()
        try:
            _apply(body, other, root, None, opinions)
        except ValueError as error:
            return [str(error)]
        for holder, target in (('OTHER', 'ROOT'), ('ROOT', 'OTHER')):
            got = {modifier for who, whom, modifier in opinions
                   if (who, whom) == (holder, target) and modifier in {catholic, orthodox, ECUMENICAL_OPINION}}
            if got != expected:
                problems.append(f'{other_faith} state with ROOT {root_faith}, settlement {"concluded" if settled else "lapsed" if lapsed else "not concluded"}: '
                                f'{holder} holds {sorted(m.replace("rip_church_opinion_gc_", "") for m in got)}, '
                                f'expected {sorted(m.replace("rip_church_opinion_gc_", "") for m in expected)}')
    return problems


# Player-visible names of the province action. The internal ids keep the older
# "recognize" spelling because rip_church_rite_recognized lives in savegames.
STALE_RITE_NAMING = re.compile(
    r'recogni[sz]e\s+(?:the\s+|a\s+|an\s+)?(?:local\s+|eastern\s+|latin\s+|orthodox\s+)?(?:parish|rite)\b', re.I)
RITE_LABELS = {'rip_church_recognize_rite_button': 'Guarantee',
               'rip_church_gui_recognize_parish': 'Guarantee',
               'rip_church_revoke_rite_button': 'community rights'}


def _literals(text, key):
    """Quoted values bound to `key`, in the yml (key:0 "v") or in the generator ("key": "v")."""
    pattern = r'''(?<!\w)['"]?''' + re.escape(key) + r'''(?!\w)['"]?\s*:\s*\d*\s*(['"])(.*?)(?<!\\)\1'''
    return [match.group(2) for match in re.finditer(pattern, text)]


def _literals_or_whole(text, key):
    """The yml always holds a literal. The generator may build a key from named
    constants, and then its whole source stands in for the value."""
    return _literals(text, key) or [text]


def _without_comments(text):
    return re.sub(r'(?m)^\s*#.*$', '', text)


def guarantee_naming_problems(text):
    """`text` is the generated English yml or the generator that writes it."""
    body = _without_comments(text)
    problems = [f'the action is still presented as {match.group(0)!r}' for match in STALE_RITE_NAMING.finditer(body)]
    for key, word in RITE_LABELS.items():
        values = _literals(body, key)
        if not values:
            problems.append(f'{key}: no literal label')
        problems += [f'{key}: {value!r} does not say {word!r}' for value in values if word not in value]
    for value in _literals_or_whole(body, 'rip_church_recognize_rite_button_tt'):
        if 'not converted' not in value:
            problems.append('the province button tooltip does not say the province is not converted')
    return problems


def ecumenism_facts(modifiers_text, opinion_text):
    """What the ecumenical settlement really does, read from the code."""
    rite, ecumenical = (modifier_offsets(modifiers_text, name) for name in ('rip_church_rite', RITE_ECUMENICAL))
    net = lambda key: round((rite.get(key, 0) + ecumenical.get(key, 0)) * 100, 6)
    return dict(opinion=modifier_offsets(opinion_text, ECUMENICAL_OPINION)['opinion'],
                unrest=rite['local_unrest'] + ecumenical['local_unrest'],
                tax=net('local_tax_modifier'), levies=net('local_manpower_modifier'))


def ecumenism_text_problems(text, facts):
    """The ecumenism tooltip states the opinion bonus and the province effect the code gives."""
    needed = (f"+{facts['opinion']:g} opinion", f"unrest {facts['unrest']:g}",
              f"tax {facts['tax']:g}%", f"levies {facts['levies']:g}%")
    return [f'the ecumenism tooltip lacks {phrase!r}'
            for value in _literals_or_whole(_without_comments(text), 'rip_church_gui_ecumenism_tt')
            for phrase in needed if phrase not in value]


def guarantee_of_rights_contracts():
    modifiers = read('common/event_modifiers/RIP_church_redesign_modifiers.txt')
    relations = read('common/scripted_effects/rip_church_diplomacy_effects.txt')
    facts = ecumenism_facts(modifiers, read('common/opinion_modifiers/RIP_church_relations.txt'))
    generator = read('tools/build_church_localisation.py')
    english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
    checks = {
        'ecumenical_rite_strictly_deeper': ecumenical_rite_problems(modifiers),
        'rite_modifiers_are_alternatives': alternative_rite_modifier_problems(
            read('common/scripted_effects/rip_church_union_effects.txt')),
        'ecumenical_opinion_reachable': relation_ecumenical_problems(relations),
        'ecumenical_opinion_outcomes': relation_outcome_problems(relations),
        'guarantee_naming_generator': guarantee_naming_problems(generator),
        'guarantee_naming_english': guarantee_naming_problems(english),
        'ecumenism_text_generator': ecumenism_text_problems(generator, facts),
        'ecumenism_text_english': ecumenism_text_problems(english, facts),
    }
    failed = {name: problems for name, problems in checks.items() if problems}
    assert not failed, 'Guarantee-of-rights contract broken:\n' + '\n'.join(
        f'  {name}: {problem}' for name, problems in failed.items() for problem in problems)
    return len(checks)


if __name__ == '__main__':
    count = run_cases()
    contracts()
    rights = guarantee_of_rights_contracts()
    print(f'RELIGION SETTLEMENT PASS: {count} source-executed transition cases; adoption, Kyiv payments, migration, crusades, monuments; '
          f'{rights} guarantee-of-rights contracts (rite modifiers, ecumenical opinion reach, English naming).')
    print('LIMIT: EU4 branch execution, old-save loading and 50-year effectiveness are not certified by this model.')
    # In-engine finding (EU4 1.37.5, diagnostics/gc_rights_ecumenism_20260929): add_opinion inside an else_if / else body
    # leaves no opinion in the save, so the +40 / 0 / ro_* base modifiers of the refresh effect never appear and this
    # model (standard chain semantics) is stricter than the game. Only the top-level ecumenical +15 is engine-proven.
    print('LIMIT: the engine drops add_opinion inside else_if / else bodies; only the top-level ecumenical +15 is proven in game.')
