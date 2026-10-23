"""Execute repaired court/election/autonomy source contracts. Not EU4 runtime."""
from copy import deepcopy
import re

from clausewitz_testlib import ROOT, read, named_block, keyed_blocks, normalized
from church_testlib import World as BaseWorld, parse, TRIGGERS, EFFECTS

TRIGGERS.update(parse(read('common/scripted_triggers/zaz_mechanics_triggers.txt')))
for filename in ('zaz_mechanics_effects', 'het_autonomy_effects'):
    EFFECTS.update(parse(read('common/scripted_effects/' + filename + '.txt')))


def event(path, identifier):
    candidates = []
    for _, text in keyed_blocks(read(path), 'country_event'):
        fields = dict(dict(parse(text))['country_event'])
        if fields.get('id') == identifier and 'title' in fields:
            candidates.append(fields)
    assert len(candidates) == 1, (identifier, len(candidates))
    return candidates[0]


class World(BaseWorld):
    def ref(self, key, scope, root, prev):
        if key == 'overlord': return self.countries.get(scope.get('overlord'))
        return super().ref(key, scope, root, prev)

    def collection(self, key, scope):
        if key == 'any_ally': return [self.countries[tag] for tag in sorted(scope['allies'])]
        return super().collection(key, scope)

    def condition(self, key, value, scope, root, prev):
        if key == 'overlord' and isinstance(value, list):
            target = self.ref(key, scope, root, prev)
            return target is not None and self.gate(value, target, root, scope)
        if key == 'is_subject_of': return scope.get('overlord') == value and scope['is_subject']
        if key == 'has_institution': return value in scope.get('institutions', set())
        if key == 'current_age': return scope.get('current_age') == value
        if key == 'army_size':
            target = self.ref(value, scope, root, prev)
            return scope['army_size'] >= (target['army_size'] if target else float(value))
        if key == 'has_opinion_modifier':
            fields = dict(value)
            return (self.ref(fields['who'], scope, root, prev)['id'], fields['modifier']) in scope.get('opinion_modifiers', set())
        return super().condition(key, value, scope, root, prev)

    def execute(self, items, scope, root=None, prev=None):
        for key, value in items:
            if key == 'add_legitimacy_equivalent':
                fields = dict(value)
                keyname = 'republican_tradition' if scope['government'] == 'republic' else 'legitimacy_equivalent'
                scope[keyname] += float(fields.get('republican_tradition', fields['amount']) if keyname == 'republican_tradition' else fields['amount'])
            elif key == 'define_ruler':
                scope['ruler_request'] = dict(value)
            elif key == 'add_army_tradition':
                scope['army_tradition'] = scope.get('army_tradition', 0) + float(value)
            else:
                super().execute([(key, value)], scope, root, prev)


def fixture(tag='HET'):
    w = World()
    w.year = 1766
    c = w.country(tag)
    c.update(government='republic', legitimacy_equivalent=90, republican_tradition=49,
             liberty_desire=80, army_size=20, manpower_percentage=0.6, num_of_rebel_armies=0,
             is_subject=True, overlord='RUS', institutions={'printing_press'})
    w.province(280, c)
    patron = w.country('RUS')
    patron['opinions'][tag] = -50
    patron['opinion_modifiers'] = set()
    ally = w.country('SWE')
    ally['army_size'] = 30
    c['allies'].add('SWE')
    w.country('POL')
    return w, c


def gate(w, c, name):
    return w.gate(TRIGGERS[name], c)


def check_tombstones():
    decisions = read('decisions/KyivTriggers.txt')
    assert not re.search(r'\bruthenian_convene_court\s*=\s*\{', decisions)
    retired = ('KRU_factional_court_cooldown', 'KRU_princes_court', 'KRU_boyar_duma', 'KRU_hetman_council')
    for folder in ('decisions', 'events', 'common'):
        for path in (ROOT / folder).rglob('*.txt'):
            # Legacy vanilla overrides can be cp1252; this scan checks ASCII IDs only.
            text = re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig', errors='replace'))
            assert not any(name in text for name in retired), path
    for dlcs in (set(), {'Res Publica'}, {'Winds of Change'}):
        w, c = fixture('KRU')
        c['dlcs'] = dlcs
        for identifier in ('ruthenian_factions.1', 'ruthenian_factions.2'):
            fields = event('events/RuthenianFactional.txt', identifier)
            assert fields['hidden'] == fields['is_triggered_only'] == 'yes'
            before = deepcopy(c)
            w.execute(fields.get('immediate', []), c)
            for key, option in dict(parse(named_block(read('events/RuthenianFactional.txt'), 'country_event', 1 if identifier.endswith('.1') else 2)))['country_event']:
                if key == 'option': w.execute([(k, v) for k, v in option if k != 'name'], c)
            assert c == before and not w.events
    court = read('common/government_mechanics/rip_ruthenian_factional_court.txt')
    assert 'has_dlc' not in named_block(court, 'available')
    for action, resource in (('kru_court_the_knyazi', 'dip'), ('kru_court_the_boyary', 'adm'), ('kru_court_the_starshyna', 'mil')):
        body = named_block(court, action)
        assert f'add_{resource}_power = -50' in named_block(body, 'effect')
        assert 'cooldown_years = 6' in body


def check_elections():
    cases = 0
    for flag, helper, days in (
        ('zaz_recent_hetman_election', 'zaz_hetman_recent_election_expired', 730),
        ('zaz_election_event_cooldown', 'zaz_manual_election_term_expired', 365),
        ('zaz_election_event_cooldown', 'zaz_election_event_term_expired', 1460),
    ):
        for age in (None, 0, days - 1, days, days + 1, 7300, 36500):
            w, c = fixture()
            if age is not None:
                c['flags'][flag] = 0
                w.day = age
            assert gate(w, c, helper) == (age is None or age >= days), (helper, age)
            cases += 1
    w, c = fixture()
    c['legitimacy_equivalent'] = 39
    assert gate(w, c, 'can_hold_hetman_election')  # first election, no dated flags
    c['legitimacy_equivalent'] = 40
    assert not gate(w, c, 'can_hold_hetman_election')
    c['flags'] = dict(last_hetman_election=0, zaz_recent_hetman_election=0, zaz_election_event_cooldown=0)
    for age in (0, 364, 365, 729, 730, 1459, 1460, 7299, 7300, 7301, 36500):
        w.day = age
        assert gate(w, c, 'can_hold_hetman_election') == (age >= 7300), age
        cases += 1
    # Exceptional early election: still bound by the shared two-year term.
    w.countries['RUS']['opinion_modifiers'].add(('HET', 'demanded_sich_relocation'))
    for age in (729, 730, 731):
        w.day = age
        assert gate(w, c, 'can_hold_hetman_election') == (age >= 730)
        cases += 1
    # The real effect pays once, records dates before calling the candidate event.
    w.day = 7300
    w.run('zaz_hold_hetman_election', c)
    assert c['adm_power'] == 400 and c['stability'] == 1
    assert all(c['flags'][flag] == 7300 for flag in ('last_hetman_election', 'zaz_recent_hetman_election', 'zaz_election_event_cooldown'))
    assert w.events == [('HET', 'rip_het_election.1')]
    before = deepcopy(c)
    w.run('zaz_hold_hetman_election', c)
    assert c == before and len(w.events) == 1
    candidate = event('events/RIP_HetmanElection.txt', 'rip_het_election.1')
    assert candidate['is_triggered_only'] == 'yes' and w.gate(candidate['trigger'], c)
    assert 'tag = ZAZ' not in normalized(named_block(read('events/RIP_HetmanElection.txt'), 'trigger'))
    decision = named_block(read('decisions/ZaporizhiaDecisions.txt'), 'zaz_hold_hetman_election')
    assert 'add_adm_power' not in named_block(decision, 'effect')
    # Execute each paid candidate branch for both government resource types.
    options = [body for _, body in keyed_blocks(read('events/RIP_HetmanElection.txt'), 'option')]
    assert len(options) == 3
    for government in ('monarchy', 'republic'):
        for index, body in enumerate(options):
            w, c = fixture()
            c.update(government=government, legitimacy_equivalent=39)
            w.run('zaz_hold_hetman_election', c)
            fields = dict(parse(body))['option']
            w.execute([(key, value) for key, value in fields if key != 'name'], c)
            assert c['adm_power'] == 400 and c['stability'] == 1
            assert c['ruler_request'] == (
                {'change_mil': '3', 'change_adm': '-1'},
                {'change_dip': '3', 'change_mil': '-1'},
                {'change_adm': '2', 'change_dip': '1', 'change_mil': '1'},
            )[index]
            bonus = 10 if index == 2 else 5
            assert c.get('army_tradition', 0) == (5 if index == 0 else 0)
            assert c['dip_power'] == (525 if index == 1 else 500)
            assert c['legitimacy_equivalent'] == (39 if government == 'republic' else 49 + bonus)
            assert c['republican_tradition'] == (54 + bonus if government == 'republic' else 49)
            before = deepcopy(c)
            w.run('zaz_hold_hetman_election', c)
            assert c == before and len(w.events) == 1
            cases += 1
    for resource, value in (('adm_power', 99), ('stability', -1), ('is_at_war', True), ('num_of_rebel_armies', 1)):
        w, c = fixture()
        c['legitimacy_equivalent'] = 39
        c[resource] = value
        before = deepcopy(c)
        w.run('zaz_hold_hetman_election', c)
        assert c == before and not w.events, resource
        cases += 1
    # All three autonomous ZAZ events use the same ready/mark contract.
    w, c = fixture('ZAZ')
    c['reforms'].add('zaz_kosh_elections_reform')
    for n in (5, 14, 15):
        fields = event('events/ZaporizhiaFlavor.txt', f'zaz_flavor.{n}')
        assert ('zaz_election_event_term_expired', 'yes') in fields['trigger']
        assert ('zaz_hetman_recent_election_expired', 'yes') in fields['trigger']
        for age in (0, 729, 730, 1459, 1460, 7300):
            c['flags'] = dict(last_hetman_election=0, zaz_recent_hetman_election=0, zaz_election_event_cooldown=0)
            w.day = age
            assert w.gate(fields['trigger'], c) == (age >= 1460), (n, age)
            cases += 1
        w.execute(fields['immediate'], c)
        assert c['flags']['last_hetman_election'] == w.day
        assert not w.gate(fields['trigger'], c)
    return cases


def check_autonomy():
    cases = 0
    for key, value in (('mil_power', 199), ('stability', -1), ('legitimacy_equivalent', 74),
                       ('army_size', 14), ('manpower_percentage', 0.49), ('is_at_war', True), ('allies', set())):
        w, c = fixture()
        c[key] = value
        before = deepcopy(c)
        w.run('het_resist_abolition_effect', c)
        assert c == before, key
        cases += 1
    w, c = fixture()
    c['modifiers']['het_abolished'] = float('inf')
    assert gate(w, c, 'can_resist_abolition')
    w.run('het_resist_abolition_effect', c)
    assert c['mil_power'] == 300 and c['stability'] == 0
    assert 'het_abolished' not in c['modifiers']
    assert c['modifiers']['rip_het_autonomy_defended'] == 3650
    assert c['flags']['rip_het_abolition_deferred'] == 0
    assert not w.events and not c['wars']  # the action never forces a war
    before = deepcopy(c)
    w.run('het_resist_abolition_effect', c)
    assert c == before
    abolition = event('events/HetmanateEnhanced.txt', 'het_enhanced.7')
    for age in (0, 3649):
        w.day = age
        assert not gate(w, c, 'can_resist_abolition')
        assert not w.gate(abolition['trigger'], c)
        cases += 1
    w.day = 3650
    w.year = 1776  # the paid reprieve must not silently escape the old date window
    assert gate(w, c, 'can_resist_abolition') and w.gate(abolition['trigger'], c)
    w.execute(abolition['immediate'], c)
    assert 'abolition_threatened' in c['flags'] and 'rip_het_abolition_deferred' not in c['flags']
    assert not w.gate(abolition['trigger'], c)
    cases += 1
    for transition in ('independence', 'successor', 'new_patron', 'reconciliation'):
        w, c = fixture()
        w.run('het_resist_abolition_effect', c)
        if transition == 'independence': c.update(is_subject=False, overlord=None)
        elif transition == 'successor':
            c['id'] = 'KRU'
            w.countries['KRU'] = w.countries.pop('HET')
        elif transition == 'new_patron': c['overlord'] = 'POL'
        else:
            w.day = 3650
            w.countries['RUS']['opinions']['HET'] = 50
        w.run('het_autonomy_upkeep_effect', c)
        assert 'rip_het_abolition_deferred' not in c['flags'], transition
        assert 'rip_het_resisted_abolition' in c['flags'], transition
        if transition in ('independence', 'successor'):
            assert 'rip_het_autonomy_defended' not in c['modifiers']
            c.update(id='HET', is_subject=True, overlord='RUS')
            if transition == 'successor': w.countries['HET'] = w.countries.pop('KRU')
            assert not gate(w, c, 'can_resist_abolition')  # no term refund
        cases += 1
    # Native modifier + startup/monthly cleanup and four-language text are real definitions.
    modifier = dict(dict(parse(read('common/event_modifiers/RIP_HET_modifiers.txt')))['rip_het_autonomy_defended'])
    assert modifier == {'defensiveness': '0.15', 'global_unrest': '-1'}
    hooks = read('common/on_actions/RIP_HET_autonomy_on_actions.txt')
    for hook in ('on_startup', 'on_monthly_pulse'):
        assert 'het_autonomy_upkeep_effect = yes' in named_block(hooks, hook)
    for lang in ('english', 'french', 'german', 'spanish'):
        path = ROOT / f'localisation/rip_het_autonomy_l_{lang}.yml'
        assert path.read_bytes().startswith(b'\xef\xbb\xbf')
        text = path.read_text(encoding='utf-8-sig')
        assert 'rip_het_autonomy_defended:0' in text and 'desc_rip_het_autonomy_defended:0' in text
    return cases


def planted_violations():
    # Prove the boundary test rejects the exact old inverted-flag regression.
    name = 'zaz_hetman_recent_election_expired'
    original = TRIGGERS[name]
    TRIGGERS[name] = parse('NOT = { had_country_flag = { flag = zaz_recent_hetman_election days = 730 } }')
    try:
        try: check_elections()
        except AssertionError: pass
        else: raise AssertionError('inverted flag mutation was not caught')
    finally: TRIGGERS[name] = original
    # A missing result or missing guard must fail real transaction execution.
    name = 'het_resist_abolition_effect'
    original = EFFECTS[name]
    for broken in (parse('add_mil_power = -200 add_stability = -2'),
                   [(k, v) for k, v in dict(original)['if'] if k != 'limit']):
        EFFECTS[name] = broken
        try:
            try: check_autonomy()
            except AssertionError: pass
            else: raise AssertionError('abolition result/guard mutation was not caught')
        finally: EFFECTS[name] = original


if __name__ == '__main__':
    check_tombstones()
    count = check_elections() + check_autonomy()
    planted_violations()
    print(f'KRU/HET DECISION REPAIRS PASS: {count} source-executed cases; retired court, paid reprieve, elections, three planted regressions caught.')
    print('LIMIT: source model; native UI, queued-save delivery, AI scheduling and EU4 campaign execution unverified.')
