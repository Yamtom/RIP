"""Static contracts for the Kyiv mission rework of 21 November 2026.

The reviewer's six points, each as a script contract:
1. UKR_dniepr / UKR_sloboda_frontier (covered in check_kyiv_successor_progression.py).
2. UKR_baltic offers three campaigns and the whole shore is a separate summit;
   UKR_tsyisar no longer converts Constantinople by decree.
3. KIE_brotherhood_schools admits a realm of another faith; KIE_magdeburg_law
   asks the player how far the magistrate's powers reach.
4. KIE_byzantine_relations has a public declaration instead of an insult.
5. Diaspora: the southern branches do not wait for the circumnavigation, the
   Wedge branches tolerate local peoples, the final does not count Saratov.
6. KIE_mohyla_academy follows the Brotherhood schools with a focused reward.

Static only: nothing here proves the events fire in the game.
"""
import re
from clausewitz_testlib import matching_brace, named_block, read

shared = read('missions/Kyiv_Shared_Missions.txt')
successors = read('missions/Kyiv_Successors_Missions.txt')
kyiv = read('missions/Kyiv_Missions.txt')
diaspora = read('missions/zzzz_RuthenianDiaspora_Missions.txt')
events = read('events/RIP_KIE_KyivChoices.txt')
decisions = read('decisions/RIP_KIE_ByzantinePrimacy.txt')
kie_modifiers = read('common/event_modifiers/RIP_KIE_modifiers.txt')
kie_opinions = read('common/opinion_modifiers/RIP_KIE_opinion_modifiers.txt')


def loc_entries(path):
    return dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(path), re.M))


def check_baltic_and_tsarhorod():
    baltic = named_block(successors, 'UKR_baltic')
    trigger = named_block(baltic, 'trigger')
    assert 'type = all' not in trigger, 'UKR_baltic must not demand the whole shore'
    for tooltip in ('UKR_baltic_port_tt', 'UKR_baltic_trade_tt', 'UKR_baltic_alliance_tt'):
        assert f'tooltip = {tooltip}' in trigger, tooltip
    assert trigger.count('custom_trigger_tooltip') == 3
    assert 'region = baltic_region' in trigger
    assert 'has_port = yes' in trigger and 'has_building = dock' in trigger
    assert 'trade_share' in trigger and 'any_ally' in trigger
    assert 'required_missions = { KIE_magdeburg_law }' in baltic

    trade = named_block(successors, 'UKR_merchant_commonwealth')
    assert 'required_missions = { UKR_baltic }' in trade
    assert 'trade_share' in named_block(trade, '1926')
    assert 'trade_share' in named_block(trade, '280')

    compact = named_block(successors, 'UKR_princely_compact')
    assert 'required_missions = { KIE_consolidate }' in compact
    for seat in ('279', '289', '2961'):
        assert 'rip_kyivan_compact_seat = yes' in named_block(compact, seat)
    empire = named_block(successors, 'UKR_ruthenian_empire')
    assert named_block(empire, 'required_missions').split() == [
        'required_missions', '=', '{', 'UKR_greece', 'KIE_second_jerusalem', '}',
    ]

    summit = named_block(successors, 'UKR_baltic_dominion')
    assert 'required_missions = { UKR_swedish_question }' in summit
    summit_trigger = named_block(summit, 'trigger')
    area = named_block(summit_trigger, 'baltic_region')
    assert 'type = all' in area and 'country_or_non_sovereign_subject_holds = ROOT' in area
    assert 'name = UKR_baltic_dominion' in named_block(summit, 'effect')
    named_block(kie_modifiers, 'UKR_baltic_dominion')
    assert 'required_missions = { UKR_princes }' in named_block(successors, 'UKR_poland')

    tsyisar = named_block(successors, 'UKR_tsyisar')
    effect = named_block(tsyisar, 'effect')
    assert 'change_culture' not in effect and 'change_religion' not in effect, \
        'Constantinople must not change culture and faith in one click'
    assert 'id = kyiv_choices.1' in effect
    assert 'add_base_tax = 2' not in effect


def top_level_events():
    """Events at column 0. A delayed `country_event = { id = ... days = ... }` call
    inside an option is indented and is not a definition."""
    bodies = []
    for match in re.finditer(r'(?m)^country_event = \{', events):
        bodies.append(events[match.start(): matching_brace(events, match.end() - 1) + 1])
    return bodies


def check_events():
    bodies = top_level_events()
    ids = [re.search(r'\bid = (kyiv_choices\.\d+)', body)[1] for body in bodies]
    assert ids == ['kyiv_choices.1', 'kyiv_choices.2', 'kyiv_choices.3', 'kyiv_choices.4'], ids
    for index, body in enumerate(bodies, 1):
        for field in ('title', 'desc', 'picture'):
            assert re.search(rf'\b{field} = ', body), (index, field)
        assert 'is_triggered_only = yes' in body
        assert 'mean_time_to_happen' not in body
        assert re.search(r'\boption = \{', body), index
    first, second, third, fourth = bodies
    options = [named_block(first, 'option', n) for n in (1, 2)]
    assert 'change_culture = greek' in options[0] and 'change_religion = orthodox' in options[0]
    assert 'name = UKR_tsarhorod_greek_privileges' in options[0]
    assert 'id = kyiv_choices.2' in options[1] and 'days = 5475' in options[1]
    assert 'change_culture' not in options[1], 'the long integration converts only after fifteen years'
    assert 'change_culture = ROOT' in second and 'change_religion = ROOT' in second
    assert 'has_country_flag = ukr_tsarhorod_integrating' in named_block(second, 'trigger')

    magistrate = [named_block(third, 'option', n) for n in (1, 2)]
    assert 'name = KIE_kyiv_magistrate' in magistrate[0] and 'add_base_production = 1' in magistrate[0]
    assert 'name = KIE_kyiv_voivode_oversight' in magistrate[1] and 'add_adm_power = 50' in magistrate[1]

    claims = [named_block(fourth, 'option', n) for n in (1, 2, 3)]
    assert 'modifier = kie_church_primacy_declared' in claims[0]
    assert 'modifier = kie_dynastic_primacy_declared' in claims[1]
    for claim in claims[:2]:
        assert 'set_country_flag = rip_kie_byz_primacy_declared' in claim
    assert 'set_country_flag' not in claims[2], 'keeping silent must leave the decision available'

    for name in ('UKR_tsarhorod_greek_privileges', 'UKR_tsarhorod_court_integration',
                 'KIE_kyiv_magistrate', 'KIE_kyiv_voivode_oversight'):
        named_block(kie_modifiers, name)
    for name in ('kie_church_primacy_declared', 'kie_dynastic_primacy_declared'):
        assert re.search(rf'{name} = \{{\s*opinion = -\d+', kie_opinions), name


def check_shared_missions():
    brotherhood = named_block(shared, 'KIE_brotherhood_schools')
    trigger = named_block(brotherhood, 'trigger')
    # Not a bare religion gate: the historical brotherhood was founded by an
    # Orthodox community under a Catholic king.
    assert not re.search(r'(?m)^\t\t\t(?:religion|NOT = \{ religion)', trigger), \
        'the brotherhood trigger must not demand the state religion at the top level'
    assert 'tooltip = KIE_brotherhood_parish_network_tt' in trigger
    assert 'tooltip = KIE_brotherhood_patronage_tt' in trigger
    patronage = named_block(trigger, 'custom_trigger_tooltip', 2)
    assert 'NOT = { religion = orthodox }' in patronage
    assert 'religion = orthodox' in named_block(patronage, '280')
    assert 'estate_burghers' in patronage and 'mission_completed = KIE_cossack' in patronage
    network = named_block(trigger, 'custom_trigger_tooltip', 1)
    assert 'value = 3' in network and 'religion = russian_orthodox' in network
    assert 'adm_tech = 10' in trigger

    magdeburg = named_block(shared, 'KIE_magdeburg_law')
    effect = named_block(magdeburg, 'effect')
    assert 'id = kyiv_choices.3' in effect
    assert 'add_adm_power' not in effect and 'add_base_production' not in effect
    assert 'name = magdeburg_law_expansion' in effect


def check_byzantine_and_mohyla():
    byz = named_block(kyiv, 'KIE_byzantine_relations')
    assert 'insulted' not in named_block(byz, 'trigger')
    assert 'tooltip = KIE_byzantine_primacy_declared_tt' in byz

    decision = named_block(decisions, 'rip_kie_declare_primacy')
    assert 'exists = BYZ' in decision and 'id = kyiv_choices.4' in named_block(decision, 'effect')
    assert 'NOT = { has_country_flag = rip_kie_byz_primacy_declared }' in decision

    mohyla = named_block(successors, 'KIE_mohyla_academy')
    trigger = named_block(mohyla, 'trigger')
    effect = named_block(mohyla, 'effect')
    assert 'mission_completed = KIE_brotherhood_schools' in trigger
    assert 'required_missions = { }' in mohyla, 'a cross-column arrow would draw through other cells'
    for blurred in ('define_advisor', 'change_heir', 'change_government_reform_progress',
                    'change_innovativeness', 'add_prestige_or_monarch_power'):
        assert blurred not in effect, f'the Collegium reward must stay focused: {blurred}'
    assert 'name = kyiv_mohyla_academy' in effect and 'add_building = university' in effect
    assert 'remove_province_modifier = kyiv_brotherhood_collegium' in effect


def check_diaspora():
    # The tree exists twice (rows 24-32 and, with the suffix _kyiv, rows 15-23);
    # every contract holds for both copies.
    for suffix in ('', '_kyiv'):
        for mission in ('rip_diaspora_south_america', 'rip_diaspora_australia',
                        'rip_diaspora_south_america_settlers', 'rip_diaspora_australia_settlers'):
            mission += suffix
            trigger = named_block(named_block(diaspora, mission), 'trigger')
            assert 'rip_lysianskyi_circumnavigation_flag' not in trigger, \
                f'{mission} must not wait for the circumnavigation'
        assert 'rip_lysianskyi_circumnavigation_flag' in named_block(diaspora, 'rip_diaspora_of_rus' + suffix)
        named_block(diaspora, 'rip_lysianskyi_circumnavigation' + suffix)

        for mission, region in (('rip_green_wedge', 'manchuria_region'), ('rip_grey_wedge', 'central_asia_region')):
            mission += suffix
            trigger = named_block(named_block(diaspora, mission), 'trigger')
            assert 'NOT = {' not in trigger.replace('is_subject = no', ''), \
                f'{mission} must tolerate provinces with a local population'
            counters = [named_block(trigger, 'num_of_owned_provinces_with', n) for n in (1, 2)]
            assert f'region = {region}' in counters[0] and 'value = 3' in counters[0]
            assert 'rip_diaspora_eligible_culture_province = yes' in counters[1] and 'value = 2' in counters[1]

        final = named_block(named_block(diaspora, 'rip_diaspora_of_rus' + suffix), 'trigger')
        assert 'saratov_area' not in final, 'the Volga is not the Grey Wedge'
        for area in ('yrtesh_area', 'ishim_area', 'aqmola_area', 'kazakhstan_area'):
            assert 'rip_diaspora_established_community = yes' in named_block(final, area), area


def check_localisation():
    kie = loc_entries('localisation/RIP_KIE_realm_l_english.yml')
    expeditions = loc_entries('localisation/RIP_shared_ruthenian_expeditions_l_english.yml')
    kie_keys = [
        'UKR_sloboda_frontier_title', 'UKR_sloboda_frontier_desc',
        'UKR_baltic_dominion_title', 'UKR_baltic_dominion_desc',
        'UKR_baltic_port_tt', 'UKR_baltic_trade_tt', 'UKR_baltic_alliance_tt',
        'UKR_princely_compact_title', 'UKR_princely_compact_desc',
        'UKR_merchant_commonwealth_title', 'UKR_merchant_commonwealth_desc',
        'KIE_brotherhood_parish_network_tt', 'KIE_brotherhood_patronage_tt',
        'KIE_byzantine_primacy_declared_tt',
        'UKR_baltic_dominion', 'desc_UKR_baltic_dominion',
        'UKR_tsarhorod_greek_privileges', 'desc_UKR_tsarhorod_greek_privileges',
        'UKR_tsarhorod_court_integration', 'desc_UKR_tsarhorod_court_integration',
        'KIE_kyiv_magistrate', 'desc_KIE_kyiv_magistrate',
        'KIE_kyiv_voivode_oversight', 'desc_KIE_kyiv_voivode_oversight',
        'kie_church_primacy_declared', 'kie_dynastic_primacy_declared',
        'rip_kie_declare_primacy_title', 'rip_kie_declare_primacy_desc',
        'kyiv_choices.1.t', 'kyiv_choices.1.d', 'kyiv_choices.1.a', 'kyiv_choices.1.b',
        'kyiv_choices.2.t', 'kyiv_choices.2.d', 'kyiv_choices.2.a',
        'kyiv_choices.3.t', 'kyiv_choices.3.d', 'kyiv_choices.3.a', 'kyiv_choices.3.b',
        'kyiv_choices.4.t', 'kyiv_choices.4.d', 'kyiv_choices.4.a', 'kyiv_choices.4.b',
        'kyiv_choices.4.c',
        'UKR_dniepr_desc', 'UKR_tsyisar_desc', 'UKR_baltic_title', 'UKR_baltic_desc',
        'KIE_magdeburg_law_desc', 'KIE_brotherhood_schools_desc',
        'KIE_mohyla_academy_title', 'KIE_mohyla_academy_desc', 'KIE_byzantine_relations_desc',
    ]
    for key in kie_keys:
        assert kie.get(key), key
    for lang in ('french', 'german', 'spanish'):
        fallback = loc_entries(f'localisation/replace/RIP_KIE_content_l_{lang}.yml')
        for key in kie_keys:
            assert fallback.get(key) == kie[key], (lang, key)
    # The mission texts name what the trigger really asks for.
    assert 'Pereiaslav' in kie['UKR_dniepr_desc'] and 'fort' in kie['UKR_dniepr_desc']
    assert '1620' in kie['KIE_brotherhood_schools_desc'] and 'Sahaidachnyi' in kie['KIE_brotherhood_schools_desc']
    assert 'Collegium' in kie['KIE_mohyla_academy_title']
    assert 'insult' not in kie['KIE_byzantine_relations_desc']

    for key in ('rip_green_wedge_desc', 'rip_grey_wedge_desc', 'rip_diaspora_of_rus_desc',
                'rip_lysianskyi_circumnavigation_desc'):
        for lang in ('french', 'german', 'spanish'):
            fallback = loc_entries(f'localisation/replace/RIP_shared_ruthenian_content_l_{lang}.yml')
            assert fallback[key] == expeditions[key], (lang, key)
    assert 'Saratov' not in expeditions['rip_diaspora_of_rus_desc']
    assert 'Yellow Wedge' not in expeditions['rip_diaspora_of_rus_desc']


def planted(label, mutate, check):
    """The check must fail on a deliberately broken script."""
    global successors, shared, kyiv, diaspora, events
    saved = (successors, shared, kyiv, diaspora, events)
    try:
        mutate()
        check()
    except AssertionError:
        return
    finally:
        successors, shared, kyiv, diaspora, events = saved
    raise SystemExit(f'planted regression not caught: {label}')


check_baltic_and_tsarhorod()
check_events()
check_shared_missions()
check_byzantine_and_mohyla()
check_diaspora()
check_localisation()

def break_dniepr_baltic():
    global successors
    marker = 'tooltip = UKR_baltic_trade_tt'
    assert marker in successors
    successors = successors.replace(marker, 'type = all ' + marker, 1)


def break_tsarhorod():
    global successors
    marker = re.search(r'country_event = \{\s+id = kyiv_choices\.1\s+\}', successors)
    assert marker
    successors = successors.replace(marker[0], '151 = { change_culture = ROOT }', 1)


def break_diaspora():
    global diaspora
    diaspora, hits = re.subn(r'(rip_diaspora_australia = \{.*?trigger = \{)',
                             r'\1 has_country_flag = rip_lysianskyi_circumnavigation_flag',
                             diaspora, count=1, flags=re.S)
    assert hits == 1


planted('Baltic demands type = all again', break_dniepr_baltic, check_baltic_and_tsarhorod)
planted('Tsarhorod converts by decree again', break_tsarhorod, check_baltic_and_tsarhorod)
planted('Australia waits for the circumnavigation again', break_diaspora, check_diaspora)
print('PASS: Kyiv mission choices (Baltic routes, Tsarhorod, brotherhood, Magdeburg, Byzantine declaration, Collegium, diaspora) - static only')
