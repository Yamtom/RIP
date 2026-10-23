"""Source-executed ownership, occupation, queued-option and dated-rada contracts.

This bounded model is not EU4 runtime, save migration or AI scheduling evidence.
"""
from copy import deepcopy
import re
from clausewitz_testlib import ROOT, read, named_block
from church_testlib import World as BaseWorld, parse, TRIGGERS, EFFECTS

TRIGGERS.update(parse(read('common/scripted_triggers/rip_dniester_triggers.txt')))
EFFECTS.update(parse(read('common/scripted_effects/rip_dniester_effects.txt')))
DECISIONS = dict(dict(parse(read('decisions/DniesterEstuaryDecisions.txt')))['country_decisions'])
EVENTS = {dict(body)['id']: body for key, body in parse(read('events/DniesterEstuary.txt')) if key == 'country_event'}


class World(BaseWorld):
    def condition(self, key, value, scope, root, prev):
        if key == 'owns_or_non_sovereign_subject_of':
            owner = self.countries[self.provinces[value]['owner']]
            return owner is scope or (owner.get('overlord') == scope['id'] and owner.get('non_sovereign', False))
        return super().condition(key, value, scope, root, prev)

    def execute(self, items, scope, root=None, prev=None):
        i = 0
        while i < len(items):
            key, value = items[i]
            i += 1
            if key == 'if':
                group = [(key, value)]
                while i < len(items) and items[i][0] in ('else_if', 'else'):
                    group.append(items[i]); i += 1
                super().execute(group, scope, root, prev)
            elif key == 'center_of_trade': scope[key] = int(value)
            elif key == 'add_building':
                scope['buildings'].add(value)
                if value == 'fort_15th': scope['fort_level'] = 2
            else: super().execute([(key, value)], scope, root, prev)


def fixture():
    w = World()
    c = w.country('MOL')
    c.update(adm_tech=20, dip_tech=20, mil_tech=20, war_exhaustion=0, army_tradition=0)
    for tag in ('SUB', 'TUR'): w.country(tag)
    p = w.province(1756, c)
    p.update(base_tax=5, base_production=4, base_manpower=2, center_of_trade=3,
             fort_level=4, buildings={'fort_16th'}, has_port=True, unrest=0)
    w.province(282, c)
    return w, c, p


def networks():
    count = 0
    for state, active in (('direct', True), ('dependent', True), ('occupied', False),
                          ('subject_occupied', False), ('released', False), ('foreign', False), ('sovereign_subject', False)):
        w, c, p = fixture()
        c['flags'].update(dniester_estuary_developed=0, dniester_estuary_fortified=0)
        c['modifiers'].update(dniester_trade_network=float('inf'), dniester_defensive_network=float('inf'))
        if state in ('dependent', 'subject_occupied', 'released', 'sovereign_subject'):
            p.update(owner='SUB', controlled_by='SUB')
            w.countries['SUB'].update(overlord='MOL', non_sovereign=state != 'sovereign_subject')
        if state in ('occupied', 'subject_occupied'): p['controlled_by'] = 'TUR'
        if state == 'released': w.countries['SUB']['overlord'] = None
        if state == 'foreign': p.update(owner='TUR', controlled_by='TUR')
        w.run('rip_dniester_network_upkeep_effect', c)
        assert ('dniester_trade_network' in c['modifiers']) == active, state
        assert ('dniester_defensive_network' in c['modifiers']) == active, state
        flags = deepcopy(c['flags'])
        money, adm, prestige = c['treasury'], c['adm_power'], c['prestige']
        p.update(owner='MOL', controlled_by='MOL')
        w.run('rip_dniester_network_upkeep_effect', c)
        before = deepcopy(c)
        w.run('rip_dniester_network_upkeep_effect', c)
        assert c == before and c['flags'] == flags
        assert (c['treasury'], c['adm_power'], c['prestige']) == (money, adm, prestige)
        assert len(c['modifiers']) == 2
        count += 1
    w, c, p = fixture()
    c['modifiers']['dniester_trade_network'] = float('inf')
    w.run('rip_dniester_network_upkeep_effect', c)
    assert not c['modifiers']  # owning a port does not create a paid project
    return count + 1


def investments_and_queue():
    count = 0
    for owner in ('MOL', 'SUB'):
        w, c, p = fixture()
        p.update(owner=owner, controlled_by=owner)
        w.countries['SUB'].update(overlord='MOL', non_sovereign=True)
        untouched = deepcopy(w.provinces['282'])
        for name in ('develop_dniester_estuary_trade', 'fortify_dniester_estuary'):
            fields = dict(DECISIONS[name])
            assert w.gate(fields['allow'], c)
            w.execute(fields['effect'], c)
            count += 1
        assert (c['treasury'], c['adm_power'], c['dip_power'], c['mil_power']) == (300, 425, 450, 425)
        assert (p['base_tax'], p['base_production'], p['base_manpower']) == (7, 6, 5)
        assert p['center_of_trade'] == 3 and p['buildings'] == {'fort_16th'}
        assert 'dniester_fortress_akkerman' in p['modifiers']
        assert w.provinces['282'] == untouched
    for identifier, body in EVENTS.items():
        if identifier.endswith(('.11', '.30')): continue  # foreign response / Ottoman claimant
        for key, option in body:
            if key != 'option': continue
            w, c, p = fixture()
            p.update(owner='TUR', controlled_by='TUR')
            before = deepcopy((w.countries, w.provinces, w.events))
            w.execute([(k, v) for k, v in option if k not in ('name', 'trigger', 'ai_chance')], c)
            assert (w.countries, w.provinces, w.events) == before, identifier
            count += 1
    w, c, p = fixture()
    tax = [v for k, v in EVENTS['dniester_estuary.1'] if k == 'option'][1]
    w.execute([(k, v) for k, v in tax if k not in ('name', 'ai_chance')], c)
    assert c['treasury'] == 1150 and p['unrest'] == 2 and p['local_autonomy'] == 10
    return count + 1


def dated_councils():
    count = 0
    for path, name, flag in (
        ('HetmanateDecisions', 'het_strengthen_hetman', 'hetman_strengthened_recent'),
        ('HetmanateDecisions', 'het_empower_starshyna', 'starshyna_empowered_recent'),
        ('ZaporizhiaDecisions', 'zaz_host_great_rada', 'great_rada_recent'),
    ):
        fields = dict(dict(parse(read('decisions/' + path + '.txt')))['country_decisions'])
        decision = dict(fields[name])
        terms = [(k, v) for k, v in decision['potential'] if k == 'OR' and flag in repr(v)]
        assert len(terms) == 1
        for age in (None, 0, 3649, 3650, 3651, 36500):
            w, c, _ = fixture()
            if age is not None: c['flags'][flag] = 0; w.day = age
            assert w.gate(terms, c) == (age is None or age >= 3650), (name, age)
            if age is None or age >= 3650:
                w.execute([(k, v) for k, v in decision['effect'] if k == 'set_country_flag'], c)
                assert not w.gate(terms, c)
            count += 1
    return count


def static_contracts():
    for filename in ('decisions/DniesterEstuaryDecisions.txt', 'events/DniesterEstuary.txt'):
        assert not re.search(r'\b(?:282|2410)\b', read(filename))
    assert len(DECISIONS) == 6
    for name, body in DECISIONS.items():
        fields = dict(body)
        assert fields['provinces_to_highlight'] == [('province_id', '1756')]
        if name != 'contest_ottoman_dniester_control':
            assert ('rip_dniester_port_access', 'yes') in fields['allow']
    hooks = read('common/on_actions/RIP_Dniester_on_actions.txt')
    for name in ('on_startup', 'on_monthly_pulse'):
        assert 'rip_dniester_network_upkeep_effect = yes' in named_block(hooks, name)
    assert 'ruthenian_convene_court = {' not in read('decisions/KyivTriggers.txt')
    for lang in ('english', 'french', 'german', 'spanish'):
        files = [p for p in (ROOT/'localisation').rglob('*.yml') if p.name.endswith('_l_' + lang + '.yml')]
        alltext = '\n'.join(p.read_text(encoding='utf-8-sig') for p in files)
        for key in ('chr_organize_sloboda_desc', 'chr_establish_enterprise_desc', 'chr_grant_sloboda_to_old_believers_desc',
                    'force_convert_province_decision_desc', 'russify_province_decision_desc', 'het_deep_penetration_raid_desc',
                    'rip_church_restore_compact_desc', 'rip_ob_endow_refuge_desc',
                    'rip_church_sponsor_union_desc', 'rip_church_florence_desc'):
            matches = re.findall(r'(?m)^\s*'+key+r':\d*\s+"([^"]+)"', alltext)
            assert matches and all('random' in text.lower() for text in matches), (lang, key)


if __name__ == '__main__':
    static_contracts()
    count = networks() + investments_and_queue() + dated_councils()
    original = EFFECTS['rip_dniester_network_upkeep_effect']
    EFFECTS['rip_dniester_network_upkeep_effect'] = []
    try:
        try: networks()
        except AssertionError: pass
        else: raise AssertionError('Missing cleanup regression escaped')
    finally: EFFECTS['rip_dniester_network_upkeep_effect'] = original
    print(f'DNIESTER/DECISION LIFECYCLE PASS: {count} source-model cases; missing-cleanup mutation caught.')
    print('LIMIT: no EU4 runtime, AI scheduling or old-save asset migration demonstrated.')
