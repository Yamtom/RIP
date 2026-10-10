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
for file in ('rip_religion_settlement_triggers', 'rip_crusade_triggers', 'rus_russian_orthodox_triggers', 'rip_church_ro_history_triggers'):
    TRIGGERS.update(parse(read('common/scripted_triggers/' + file + '.txt')))
for file in ('rip_religion_settlement_effects', 'rip_crusade_effects', 'rip_parish_visit_effects', 'rip_faith_policy_effects', 'russian_orthodox_effects', 'greek_catholic_effects', 'rip_church_ro_history_effects'):
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
        if key == 'is_religion_enabled': return self.year >= (1439 if value == 'greek_catholic' else 1589)
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
            if faith == 'russian_orthodox': c['flags']['rip_church_ro_schismatic'] = w.day
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
            if faith == 'russian_orthodox': c['flags']['rip_church_ro_schismatic'] = w.day
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
    The whole effect is now flat (see relation_branch_shape_problems); this keeps
    the +15 an independent `if` with no conditional of its own inside.
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
    # common/scripted_triggers/rip_church_redesign_triggers.txt; ro_recognized_trigger_problems() pins the definition.
    if key == 'rip_church_ro_recognized':
        return ('rip_church_ro_recognized' in scope['flags'] and 'rip_church_ro_schismatic' not in scope['flags']) == (value == 'yes')
    if key == 'AND': return _holds(value, scope, root)
    if key == 'OR': return any(_trigger(k, v, scope, root) for k, v in value)
    if key == 'NOT': return not _holds(value, scope, root)
    if key == 'ROOT': return _holds(value, root, root)
    raise ValueError('trigger outside the relation model: ' + key)


def _apply(nodes, scope, root, prev, opinions, dropped=False):
    """Run one effect body over two country fixtures; opinions holds (holder, target, modifier).

    Control flow follows the script (if / else_if / else). `dropped` models the
    engine: EU4 1.37.5 stores no add_opinion made inside an else_if / else body, so
    an opinion added there never reaches `opinions`. A body nested under such a
    branch inherits that, the conservative reading of what the runs proved.
    """
    chain_done = False
    for key, value in nodes:
        if key in ('if', 'else_if', 'else'):
            if key == 'if': chain_done = False
            if chain_done: continue
            if key == 'else' or _holds(dict(value)['limit'], scope, root):
                chain_done = True
                _apply([node for node in value if node[0] != 'limit'], scope, root, prev, opinions,
                       dropped or key != 'if')
        elif key in ('add_opinion', 'remove_opinion'):
            if key == 'add_opinion' and dropped:
                continue
            fields = dict(value)
            triple = (scope['id'], {'ROOT': root, 'PREV': prev}[fields['who']]['id'], fields['modifier'])
            (opinions.add if key == 'add_opinion' else opinions.discard)(triple)
        elif key == 'ROOT':
            _apply(value, root, root, scope, opinions, dropped)
        else:
            raise ValueError('effect outside the relation model: ' + key)


RELATION_PREFIX = 'rip_church_opinion_'
SETTLED, SCHISM, RECOGNIZED = 'rip_church_ecumenical', 'rip_church_ro_schismatic', 'rip_church_ro_recognized'
# (country state, ROOT state, opinions each side must hold, opinions held before the refresh, note); a state is
# (religion, flags). The two sides always agree: every relation modifier is added in both directions.
RELATION_CASES = (
    # Greek Catholic <-> Latin: the +40 middle course, the +15 only after the Greek Catholic side has settled.
    (('catholic', ()), ('greek_catholic', (SETTLED,)), {'gc_catholic_middle', 'gc_ecumenical'}, (), 'settlement concluded'),
    (('greek_catholic', (SETTLED,)), ('catholic', ()), {'gc_catholic_middle', 'gc_ecumenical'}, (), 'settlement concluded'),
    (('catholic', ()), ('greek_catholic', ()), {'gc_catholic_middle'}, (), 'settlement not concluded'),
    (('catholic', ()), ('greek_catholic', ()), {'gc_catholic_middle'}, ('gc_ecumenical',), 'settlement lapsed, the +15 was held'),
    # Greek Catholic <-> Orthodox and Muscovite Orthodox: the neutral middle course; russian_orthodox never had the +15.
    (('orthodox', ()), ('greek_catholic', (SETTLED,)), {'gc_orthodox_middle', 'gc_ecumenical'}, (), 'settlement concluded'),
    (('greek_catholic', (SETTLED,)), ('orthodox', ()), {'gc_orthodox_middle', 'gc_ecumenical'}, (), 'settlement concluded'),
    (('orthodox', ()), ('greek_catholic', ()), {'gc_orthodox_middle'}, (), 'settlement not concluded'),
    (('orthodox', ()), ('greek_catholic', ()), {'gc_orthodox_middle'}, ('gc_ecumenical',), 'settlement lapsed, the +15 was held'),
    (('russian_orthodox', ()), ('greek_catholic', (SETTLED,)), {'gc_orthodox_middle'}, (), 'settlement concluded'),
    (('greek_catholic', (SETTLED,)), ('russian_orthodox', ()), {'gc_orthodox_middle'}, (), 'settlement concluded'),
    # Orthodox <-> Muscovite Orthodox: exactly one of unrecognized / recognized / schism, from either side.
    (('orthodox', ()), ('russian_orthodox', ()), {'ro_unrecognized'}, (), ''),
    (('russian_orthodox', ()), ('orthodox', ()), {'ro_unrecognized'}, (), ''),
    (('orthodox', ()), ('russian_orthodox', (RECOGNIZED,)), {'ro_recognized'}, (), ''),
    (('russian_orthodox', (RECOGNIZED,)), ('orthodox', ()), {'ro_recognized'}, (), ''),
    (('orthodox', ()), ('russian_orthodox', (SCHISM,)), {'ro_schism'}, (), ''),
    (('russian_orthodox', (SCHISM,)), ('orthodox', ()), {'ro_schism'}, (), ''),
    (('orthodox', ()), ('russian_orthodox', (SCHISM, RECOGNIZED)), {'ro_schism'}, (), 'schism wins over recognition'),
    (('orthodox', ()), ('russian_orthodox', (SCHISM,)), {'ro_schism'}, ('ro_recognized',), 'was recognized, now schismatic'),
    (('orthodox', ()), ('russian_orthodox', (RECOGNIZED,)), {'ro_recognized'}, ('ro_unrecognized', 'ro_schism'), 'stale opinions are removed first'),
    # Union opposition rides alongside, from either side.
    (('orthodox', ('rip_church_opposes_union',)), ('greek_catholic', ()), {'gc_orthodox_middle', 'union_opposition'}, (), ''),
    (('greek_catholic', ()), ('catholic', ('rip_church_opposes_union',)), {'gc_catholic_middle', 'union_opposition'}, (), ''),
    # Pairs that hold no church opinion.
    (('russian_orthodox', ()), ('russian_orthodox', ()), set(), (), 'two Muscovite Orthodox states'),
    (('orthodox', ()), ('orthodox', ()), set(), (), 'two Orthodox states'),
    (('catholic', ()), ('catholic', ()), set(), (), 'two Catholic states'),
    (('greek_catholic', (SETTLED,)), ('greek_catholic', (SETTLED,)), set(), (), 'two Greek Catholic states'),
    (('catholic', ()), ('orthodox', ()), set(), (), 'Latin and Orthodox states'),
    (('catholic', ()), ('russian_orthodox', ()), set(), (), 'Latin and Muscovite Orthodox states'),
    (('sunni', ()), ('greek_catholic', (SETTLED,)), set(), (), 'Greek Catholic and a Muslim state'),
    (('protestant', ()), ('russian_orthodox', (SCHISM,)), set(), (), 'Muscovite Orthodox and a Protestant state'),
)


def relation_outcome_problems(effect_text):
    """Run the country loop for every pairing and compare the opinions that result.

    The model is the script's own control flow plus the one engine fact that
    matters: an add_opinion inside an else_if / else body is not stored. So the
    effect passes only when every pair is served by an `if` (or nothing). Catholic
    states get the ecumenical +15 on top of the +40 of the middle course; Orthodox
    states keep it; russian_orthodox never had it; nobody gets it before the Greek
    Catholic side has concluded the settlement, and a bonus already held is
    withdrawn when the settlement lapses.
    """
    body = _every_country(effect_text)
    if body is None:
        return [RELATIONS_EFFECT + ' has no single every_country loop']
    body = [node for node in body if node[0] != 'limit']
    problems = []
    for (other_faith, other_flags), (root_faith, root_flags), expected, held, note in RELATION_CASES:
        other = dict(id='OTHER', religion=other_faith, flags=set(other_flags))
        root = dict(id='ROOT', religion=root_faith, flags=set(root_flags))
        opinions = {(who, whom, RELATION_PREFIX + name) for name in held
                    for who, whom in (('OTHER', 'ROOT'), ('ROOT', 'OTHER'))}
        try:
            _apply(body, other, root, None, opinions)
        except ValueError as error:
            return [str(error)]
        want = {RELATION_PREFIX + name for name in expected}
        for holder, target in (('OTHER', 'ROOT'), ('ROOT', 'OTHER')):
            got = {modifier for who, whom, modifier in opinions if (who, whom) == (holder, target)}
            if got != want:
                names = lambda group: sorted(m.replace(RELATION_PREFIX, '') for m in group)
                problems.append(f'{other_faith}{sorted(other_flags)} with ROOT {root_faith}{sorted(root_flags)}'
                                f'{" (" + note + ")" if note else ""}: {holder} holds {names(got)}, expected {names(want)}')
    return problems


CONDITIONALS = ('if', 'else_if', 'else')


def relation_branch_shape_problems(effect_text):
    """No opinion of the refresh effect may be added inside an else_if / else body.

    EU4 1.37.5 leaves no opinion in the save for an add_opinion made in an else_if
    or else body, while set_country_flag and ROOT / PREV in the same body work
    (in-game runs A to C, diagnostics/gc_rights_ecumenism_20260929). Only an
    unconditional add_opinion and one inside a top-level `if` are proven to persist,
    so the pairs are independent `if` blocks with mutually exclusive limits, and an
    add_opinion under a second nested conditional is refused too.
    """
    body = _body(effect_text, RELATIONS_EFFECT)
    if body is None:
        return [RELATIONS_EFFECT + ' is missing']
    problems = []

    def visit(nodes, conditionals):
        for key, value in nodes:
            if key == 'add_opinion':
                modifier = dict(value).get('modifier')
                if any(name != 'if' for name in conditionals):
                    problems.append(f'add_opinion of {modifier} sits inside an else_if / else body ({" > ".join(conditionals)}): '
                                    'the engine stores no opinion there')
                elif len(conditionals) > 1:
                    problems.append(f'add_opinion of {modifier} sits under {len(conditionals)} nested `if` blocks: '
                                    'only an unconditional or single top-level `if` is proven in game')
            elif isinstance(value, list):
                visit(value, conditionals + [key] if key in CONDITIONALS else conditionals)
    visit(body, [])
    return problems


def ro_recognized_trigger_problems(triggers_text):
    """The outcome model re-implements rip_church_ro_recognized; the definition must stay what it assumes."""
    expected = [('has_country_flag', 'rip_church_ro_recognized'), ('NOT', [('has_country_flag', 'rip_church_ro_schismatic')])]
    body = _body(triggers_text, 'rip_church_ro_recognized')
    return [] if body == expected else ['rip_church_ro_recognized no longer is "flag set and not schismatic"; '
                                        'update _trigger() in the relation model with it']


def else_if_copy_problems(effect_text):
    """The two relation guards must fail on a deliberately damaged copy of the effect.

    The Latin pair is turned back into an `else_if` behind the unrecognized `if`,
    the shape that lost +40 in game; both guards have to notice.
    """
    damaged, count = re.subn(r'(?<!\w)if(\s*=\s*\{\s*limit\s*=\s*\{\s*OR\s*=\s*\{\s*AND\s*=\s*\{\s*religion\s*=\s*catholic\b)',
                             r'else_if\1', effect_text, count=1)
    if count != 1:
        return ['the damaged copy could not be made: the Latin pair `if` was not found']
    missed = [name for name, guard in (('branch shape', relation_branch_shape_problems), ('outcome model', relation_outcome_problems))
              if not guard(damaged)]
    return [f'the {name} guard accepts an effect whose Latin pair is an else_if' for name in missed]


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
    # The disclaimer lives in the panel's concept tooltip, the long help, the status
    # description and the count tooltip. The action button and status tooltips state
    # effects only, so they no longer repeat it.
    model_keys = (
        'rip_church_rite_heading_tt',
        'rip_church_rite_help',
        'rip_church_rite_help_tt',
        'desc_rip_church_rite',
        'rip_church_gui_parish_list_title_tt',
        'rip_church_gui_parishes_title_tt',
        'rip_church_gui_count_value_tt',
    )
    for key in model_keys:
        values = _literals_or_whole(body, key)
        for value in values:
            lower = value.lower()
            if (not all(phrase in lower for phrase in ('gameplay', 'canonical', 'not an exact'))
                    or not re.search(r'\bvoluntary (?:acceptance|union acceptance)\b', lower)):
                problems.append(f'{key}: wording must disclaim exact status, canonical status and voluntary acceptance')
    return problems


def rite_interpretation_problems(text):
    """The tax/manpower trade-off is an explicit game-design interpretation, not faith punishment or history."""
    phrases = (
        'game-design interpretation',
        'administrative compromise',
        'protecting local arrangements and autonomy',
        'not a penalty for another faith',
        'not a documented historical formula',
    )
    keys = ['rip_church_rite_help']
    generated = 'RITE_INTERPRETATION=' not in text
    if generated:
        keys.extend(('rip_church_gui_recognize_parish_tt', 'desc_rip_church_rite'))
    problems = []
    for key in keys:
        values = _literals_or_whole(text, key)
        for value in values:
            lower = value.lower()
            problems += [f'{key}: missing {phrase!r}' for phrase in phrases if phrase not in lower]
            if key != 'desc_rip_church_rite':
                tax = 'local tax falls by 15%' if key != 'rip_church_rite_help' else 'tax -15%'
                manpower = 'manpower by 20%' if key != 'rip_church_rite_help' else 'manpower -20%'
                for phrase in (tax, manpower):
                    if phrase not in lower:
                        problems.append(f'{key}: missing unchanged modifier {phrase!r}')
    # The button tooltip states the numbers only; the interpretation lives in desc_rip_church_rite.
    for value in _literals_or_whole(text, 'rip_church_recognize_rite_button_tt'):
        lower = value.lower()
        problems += [f'rip_church_recognize_rite_button_tt: missing unchanged modifier {phrase!r}'
                     for phrase in ('local tax falls by 15%', 'manpower by 20%') if phrase not in lower]
    return problems


def rite_documentation_problems(text):
    """Ukrainian guide/atlas retain the game-design framing and historical caveat."""
    lower = re.sub(r'\s+', ' ', text.lower())
    phrases = (
        'адміністративного компромісу',
        'місцевих порядків і автономії',
        'покарання за іншу віру',
    )
    problems = [f'missing {phrase!r}' for phrase in phrases if phrase not in lower]
    if not ('історичної формули' in lower or 'історична формула' in lower):
        problems.append('does not disclaim a documented historical formula')
    if not re.search(r'добровільн\w*.{0,50}уні', lower):
        problems.append('does not disclaim proof of voluntary Union acceptance')
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
    needed = (f"+{facts['opinion']:g} mutual opinion", f"unrest {facts['unrest']:g}",
              f"tax {facts['tax']:g}%", f"levies {facts['levies']:g}%")
    return [f'the ecumenism tooltip lacks {phrase!r}'
            for value in _literals_or_whole(_without_comments(text), 'rip_church_gui_ecumenism_tt')
            for phrase in needed if phrase not in value]


def ecumenism_scope_problems(text):
    """The settlement is diplomatic/local accommodation, never restoration of full communion."""
    lower = _without_comments(text).lower()
    required = (
        'limited diplomatic and local administrative settlement',
        'not a restoration of full ecclesial communion',
        'diplomatic goodwill only',
        'orthodox and catholic states gain +15 mutual opinion',
        'russian orthodox states are excluded',
    )
    problems = [f'missing ecumenism clarification {phrase!r}'
                for phrase in required if phrase not in lower]
    # The generated localisation must carry the clarification on every active
    # tooltip path, not merely somewhere else in the file.
    output_keys = (
        'rip_church_gui_ecumenism_tt',
        'rip_church_gui_ecumenism_reason_tt',
        'rip_church_gui_ecumenism_state_tt',
        'rip_church_gui_policy_help_tt',
        'rip_church_ecumenism_desc',
    )
    if re.search(r'(?m)^\s+rip_church_gui_ecumenism_tt:0', text):
        for key in output_keys:
            values = _literals(text, key)
            if not values:
                problems.append(f'{key}: no generated localisation value')
            for value in values:
                value_lower = value.lower()
                problems += [f'{key}: missing {phrase!r}'
                             for phrase in required if phrase not in value_lower]
    return problems


def florentine_precedent_problems(text):
    """1439 is a precedent for an alternative campaign path, never the UGCC's origin."""
    requirements = {
        'greek_catholic_religion_desc': (
            'broad game category covering several distinct Ruthenian and Carpathian Eastern Catholic union traditions',
            'not the modern Ukrainian Greek Catholic Church in its narrow sense',
            'Florentine union as a precedent',
            'not as the founding of the UGCC',
        ),
        'rip_church.5.t': ('Florentine Legacy',),
        'rip_church.5.d': (
            'as a precedent',
            'campaign-created alternative',
            'does not represent the founding of the UGCC in 1439',
        ),
        'rip_church_florence_title': ('Florentine precedent',),
        'rip_church_florence_desc': (
            'Florentine precedent',
            'not the founding of the UGCC',
        ),
        'rip_church_gui_florence': ('Florentine precedent',),
        'rip_church_gui_florence_tt': (
            'Florentine precedent of 1439',
            'not the founding of the UGCC',
            'campaign-created alternative',
        ),
        'rip_church_gui_florence_wait': ('Florentine precedent',),
        'rip_church_gui_florence_done': ('Florentine precedent carried forward',),
        'rip_church_gui_florence_none': ('Florentine-precedent negotiations',),
    }
    problems = []
    for key, phrases in requirements.items():
        values = _literals(_without_comments(text), key)
        if not values:
            problems.append(f'{key}: no literal localisation value')
        for value in values:
            problems += [f'{key}: missing {phrase!r}'
                         for phrase in phrases if phrase not in value]
    body = _without_comments(text)
    for stale in ('The Florentine Alternative Endures',
                  'has sustained the Florentine union of 1439',
                  'one founding province'):
        if stale in body:
            problems.append(f'obsolete origin/continuity wording remains: {stale!r}')
    note = _literals(body, 'rip_church_gui_paths_title_tt')
    for value in note:
        if 'several local Ruthenian and Carpathian Eastern Catholic union traditions' not in value:
            problems.append('shared route note does not identify the model as several local union traditions')
    return problems


def ecumenism_documentation_problems(text):
    """Current Ukrainian references distinguish diplomatic goodwill from ecclesial communion."""
    lower = re.sub(r'\s+', ' ', text.lower())
    required = (
        'обмежене дипломатичне',
        'відновлення повного церковного спілкування',
        'russian_orthodox',
        'дипломатичн',
    )
    return [f'missing Ukrainian ecumenism clarification {phrase!r}'
            for phrase in required if phrase not in lower]
def guarantee_of_rights_contracts():
    modifiers = read('common/event_modifiers/RIP_church_redesign_modifiers.txt')
    relations = read('common/scripted_effects/rip_church_diplomacy_effects.txt')
    facts = ecumenism_facts(modifiers, read('common/opinion_modifiers/RIP_church_relations.txt'))
    generator = read('tools/build_church_localisation.py')
    english = read('localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
    fallback_localisations = {
        f'guarantee_naming_{language}': guarantee_naming_problems(
            read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml'))
        for language in ('french', 'german', 'spanish')
    }
    rite_texts = {
        'rite_interpretation_generator': generator,
        'rite_interpretation_english': english,
        **{f'rite_interpretation_{language}': read(
            f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
           for language in ('french', 'german', 'spanish')},
    }
    rite_docs = {
        'rite_documentation_guide': read('docs/GREEK_CATHOLIC_WINDOW_GUIDE.uk.md'),
        'rite_documentation_atlas': read('docs/RELIGION_MECHANICS_ATLAS.uk.md'),
    }
    ecumenism_fallbacks = {
        f'ecumenism_clarification_{language}': ecumenism_scope_problems(
            read(f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml'))
        for language in ('french', 'german', 'spanish')
    }
    ecumenism_docs = {
        f'ecumenism_documentation_{name}': ecumenism_documentation_problems(
            read(f'docs/{filename}'))
        for name, filename in (
            ('guide', 'GREEK_CATHOLIC_WINDOW_GUIDE.uk.md'),
            ('redesign', 'CHURCH_REDESIGN_20260911.uk.md'),
            ('atlas', 'RELIGION_MECHANICS_ATLAS.uk.md'),
        )
    }
    florentine_localisations = {
        f'florentine_precedent_{name}': florentine_precedent_problems(text)
        for name, text in {
            'generator': generator,
            'english': english,
            **{language: read(
                f'localisation/replace/zzzz_RIP_church_redesign_l_{language}.yml')
               for language in ('french', 'german', 'spanish')},
        }.items()
    }
    checks = {
        'ecumenical_rite_strictly_deeper': ecumenical_rite_problems(modifiers),
        'rite_modifiers_are_alternatives': alternative_rite_modifier_problems(
            read('common/scripted_effects/rip_church_union_effects.txt')),
        'ecumenical_opinion_reachable': relation_ecumenical_problems(relations),
        'relation_opinions_outside_else_branches': relation_branch_shape_problems(relations),
        'relation_opinion_outcomes': relation_outcome_problems(relations),
        'relation_guards_reject_else_if_copy': else_if_copy_problems(relations),
        'ro_recognized_trigger_matches_model': ro_recognized_trigger_problems(
            read('common/scripted_triggers/rip_church_redesign_triggers.txt')),
        'guarantee_naming_generator': guarantee_naming_problems(generator),
        'guarantee_naming_english': guarantee_naming_problems(english),
        **fallback_localisations,
        **{name: rite_interpretation_problems(text) for name, text in rite_texts.items()},
        **{name: rite_documentation_problems(text) for name, text in rite_docs.items()},
        'ecumenism_text_generator': ecumenism_text_problems(generator, facts),
        'ecumenism_text_english': ecumenism_text_problems(english, facts),
        'ecumenism_scope_generator': ecumenism_scope_problems(generator),
        'ecumenism_scope_english': ecumenism_scope_problems(english),
        **ecumenism_fallbacks,
        **ecumenism_docs,
        **florentine_localisations,
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
          f'{rights} contracts (rite modifiers, relation opinions in flat `if` blocks, English naming, Florentine precedent in EFIGS).')
    print('LIMIT: EU4 branch execution, old-save loading and 50-year effectiveness are not certified by this model.')
    # In-engine finding (EU4 1.37.5, diagnostics/gc_rights_ecumenism_20260929): add_opinion inside an else_if / else body
    # leaves no opinion in the save. The relation contracts above forbid that shape and model the engine on it; the flat
    # structure that replaced the chain is proven in game by the run recorded in that folder (run D).
    print('LIMIT: the engine rule on else_if / else is modelled from observed runs, not from EU4 source; a different EU4 build needs a new run.')
