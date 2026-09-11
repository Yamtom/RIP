"""Execute actual settlement scripts against bounded state-transition fixtures.

This deliberately small interpreter rejects unknown operations. It is a source
contract test, not the EU4 engine, a save loader or a campaign balance simulator.
"""
from copy import deepcopy
import re

from clausewitz_testlib import ROOT, read, named_block, normalized, vanilla_root


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
for file in ('rip_religion_settlement_triggers', 'rip_crusade_triggers', 'rus_russian_orthodox_triggers', 'rip_faith_triggers'):
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
        if key == 'is_religion_enabled': return self.year >= (1596 if value == 'greek_catholic' else 1448)
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
        ('russian_orthodox', 'rip_ro_enact_council_policy_effect', ('rip_ro_sobor_lands', 'rip_ro_sobor_books', 'rip_ro_sobor_courts')),
        ('orthodox', 'rip_kyiv_enact_council_policy_effect', ('rip_kyiv_elected_metropolitan', 'rip_kyiv_brotherhood_charters', 'rip_kyiv_church_rights'))):
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
    # See creation, global cap, lost building, conquest and replacement term.
    w, c = fixture('greek_catholic')
    w.run('rip_faith_initialize_hierarchy_effect', c)
    w.run('rip_uc_raise_see_effect', c)
    assert c['adm_power'] == 400 and w.provinces['280']['is_reformation_center']
    w.provinces['280']['religion'] = 'orthodox'
    w.run('rip_faith_maintain_local_property_effect', c)
    assert not w.provinces['280']['is_reformation_center'], 'changed province faith retained its old centre'
    # Independent conquest fixture for the same formerly funded building.
    w.provinces['280'].update(religion='greek_catholic', is_reformation_center=True)
    w.provinces['280']['modifiers']['rip_uc_see_of_the_union'] = float('inf')
    w.provinces['280']['owner'] = 'PAP'
    w.run('rip_faith_maintain_local_property_effect', w.countries['PAP'])
    assert not w.provinces['280']['is_reformation_center']
    assert 'rip_uc_see_of_the_union' not in w.provinces['280']['modifiers']
    w.provinces['281']['religion'] = 'greek_catholic'
    w.day = 7299
    w.run('rip_uc_raise_see_effect', c)
    assert c['adm_power'] == 400
    w.day = 7300
    w.run('rip_uc_raise_see_effect', c)
    assert c['adm_power'] == 300 and w.provinces['281']['is_reformation_center']
    assert 'rip_uc_see_raised' in c['flags']
    cases += 1
    successor = w.country('HLC', 'greek_catholic')
    w.provinces['281']['owner'] = 'HLC'
    w.run('rip_faith_maintain_local_property_effect', successor)
    assert 'rip_uc_see_raised' in successor['flags'] and w.provinces['281']['is_reformation_center']
    w.provinces['281']['owner'] = 'KIE'
    cases += 1
    for number in range(3):
        other = w.country('X' + str(number), 'greek_catholic')
        w.province(300 + number, other, 'greek_catholic')['is_reformation_center'] = True
    c['modifiers'].clear()
    w.provinces['281']['is_reformation_center'] = False
    assert not w.gate(TRIGGERS['rip_uc_can_raise_see_trigger'], c)
    cases += 1
    # A stale Brest response cannot change faith after PAP disappears or a prior signature.
    for update in ('valid', 'no_pope', 'war_pope', 'signed', 'wrong_faith', 'poor'):
        w, c = fixture()
        c['flags']['pursuing_uniate_union'] = 0
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
            assert f'set_country_flag = {flag}' in named_block(body, 'effect')
    # All country paths use the same idempotent bridge; province loops cannot call it.
    for filename in ('events/RussianOrthodox.txt', 'events/UniateChurch.txt', 'events/UniateReformationSpread.txt', 'decisions/GreekCatholicDecisions.txt'):
        source = normalized(read(filename))
        assert not re.search(r'change_religion = (?:russian_orthodox|greek_catholic)', source), filename
        assert not re.search(r'add_base_(?:tax|production|manpower)\s*=', source), filename
    for filename in ('russian_orthodox', 'zz_greek_catholic'):
        assert 'rip_faith_initialize_hierarchy_effect = yes' in named_block(read('common/religions/' + filename + '.txt'), 'on_convert')
    assert 'rip_faith_adopt_union_effect = yes' in read('common/scripted_effects/rip_uniate_crown_effects.txt')
    assert 'rip_faith_adopt_muscovite_church_effect = yes' in read('common/scripted_effects/russian_orthodox_effects.txt')
    whitelist = named_block(read('common/religions/zz_greek_catholic.txt'), 'allowed_center_conversion')
    assert 'catholic' not in whitelist and 'orthodox' in whitelist and 'russian_orthodox' in whitelist
    profile = normalized(read('common/religious_conversions/zz_RIP_greek_catholic.txt'))
    assert 'area = PREV is_reformation_center = yes religion = greek_catholic' in profile
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


if __name__ == '__main__':
    count = run_cases()
    contracts()
    print(f'RELIGION SETTLEMENT PASS: {count} source-executed transition cases; adoption, payments, See, migration, crusades, monuments.')
    print('LIMIT: EU4 branch execution, old-save loading and 50-year effectiveness are not certified by this model.')
