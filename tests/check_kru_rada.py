"""Contracts of the Rada of Three Estates (tools/build_kru_rada.py): six reforms, the pair logic, the bar and the court buttons.

The author's rule: on the native States General bar the faction that is SECOND by influence stands on the LEFT, the DOMINANT faction on the
RIGHT. The bar's ends are fixed by the reform that is held (first block of `states_general_mechanic` = left end, second block = right end),
so the Rada has one reform for every ordered pair (second, dominant): six. This test pins:

  * the six reform blocks: ids, the order of their two side blocks, the side modifiers, the visibility gates, one shared name;
  * the generated triggers and effects, EXECUTED over a grid of influence triples and a long random walk by a small interpreter of the
    script subset they use: the held reform always has (second, dominant) as its (left, right) ends, the bar stands where the leader's
    grip puts it, a refresh is idempotent, a tie keeps the old runner-up, and the reform never flaps while the order does not change;
  * every place that used to list three ids now asks the holder trigger, the court buttons refresh the pair right after they add influence,
    and the monthly and yearly events exist;
  * the three side sprites (46x25, two frames) and the side texts in four languages.

planted_violations() breaks the sources in memory and requires every break to be reported. It cannot show the bar in EU4:
docs/RUTHENIAN_GOVERNMENT_UI.uk.md says what was and was not seen in the game.
"""
import importlib.util
import itertools
import random
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read  # noqa: E402

spec = importlib.util.spec_from_file_location('build_kru_rada', ROOT / 'tools/build_kru_rada.py')
rada = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rada)
KEYS, PAIRS, REFORM_IDS, BY_KEY = rada.KEYS, rada.PAIRS, rada.REFORM_IDS, rada.BY_KEY
LANGUAGES = rada.LANGUAGES


# --------------------------------------------------------------------------------- a small interpreter -----------------------------

def parse(text):
    text = re.sub(r'#[^\n]*', '', text)
    tokens = re.findall(r'"[^"\n]*"|[{}=]|[^\s{}=]+', text)
    position = 0

    def block():
        nonlocal position
        result = []
        while position < len(tokens) and tokens[position] != '}':
            key = tokens[position]
            assert tokens[position + 1] == '=', (key, tokens[position:position + 3])
            position += 2
            if tokens[position] == '{':
                position += 1
                value = block()
                assert tokens[position] == '}'
                position += 1
            else:
                value = tokens[position]
                position += 1
            result.append((key, value))
        return result

    return dict(block())


def load_logic(triggers_text, effects_text, kru_effects_text):
    triggers = parse(triggers_text)
    effects = {**parse(effects_text), **parse(kru_effects_text)}
    return triggers, effects


class Interpreter:
    def __init__(self, triggers, effects):
        self.triggers, self.effects = triggers, effects

    def holds(self, items, state):
        return all(self.condition(key, value, state) for key, value in items)

    def condition(self, key, value, state):
        if key in self.triggers:
            return self.holds(self.triggers[key], state) == (value == 'yes')
        if key == 'AND':
            return self.holds(value, state)
        if key == 'OR':
            return any(self.condition(k, v, state) for k, v in value)
        if key == 'NOT':
            return not any(self.condition(k, v, state) for k, v in value)
        if key == 'always':
            return value == 'yes'
        if key == 'faction_in_power':
            return state['leader'] == value
        if key == 'faction_influence':
            fields = dict(value)
            return state['influence'][fields['faction']] >= float(fields['influence'])
        if key == 'has_country_flag':
            return value in state['flags']
        if key == 'has_reform':
            return value in state['reforms']
        if key == 'has_states_general_mechanic':
            return value == 'yes'
        if key == 'has_country_modifier':
            return value in state['modifiers']
        raise AssertionError(f'unsupported trigger {key}')

    def run(self, items, state):
        for key, value in items:
            if key in self.effects:
                assert value == 'yes', key
                self.run(self.effects[key], state)
            elif key == 'if':
                fields = dict(value)
                if self.holds(fields['limit'], state):
                    self.run([(k, v) for k, v in value if k != 'limit'], state)
            elif key == 'hidden_effect':
                self.run(value, state)          # a hidden_effect only hides the tooltip text; the effects inside run as usual
            elif key == 'set_country_flag':
                state['flags'].add(value)
            elif key == 'clr_country_flag':
                state['flags'].discard(value)
            elif key == 'remove_government_reform':
                state['reforms'].discard(value)
                if value in REFORM_IDS and not state['reforms'] & set(REFORM_IDS):
                    # Measured in EU4 1.37.5 (swap probe, 2026-10-19): the factions leave with the reform that founded them.
                    state['influence'] = {faction: 0.0 for faction in state['influence']}
                    state['leader'] = None
            elif key == 'add_government_reform':
                held = state['reforms'] & set(REFORM_IDS)
                state['reforms'] -= set(REFORM_IDS)          # one tier: adding a sibling replaces the held one, factions untouched (measured)
                state['reforms'].add(value)
                if value in REFORM_IDS and not held:
                    # A Rada founded from nothing starts at 55 / 15 / 30 with the knyazi in power (measured).
                    state['influence'] = {'kru_knyazi': 55.0, 'kru_boyary': 15.0, 'kru_starshyna': 30.0}
                    state['leader'] = 'kru_knyazi'
            elif key == 'change_statists_vs_orangists':
                state['bar'] = max(-1.0, min(1.0, state['bar'] + float(value)))
            elif key == 'add_country_modifier':
                state['modifiers'].add(dict(value)['name'])
            elif key == 'remove_country_modifier':
                state['modifiers'].discard(value)
            else:
                raise AssertionError(f'unsupported effect {key}')


def fresh(influence=(34, 33, 33), reform='ruthenian_factional_empire_reform'):
    state = dict(influence=dict(zip(('kru_knyazi', 'kru_boyary', 'kru_starshyna'), map(float, influence))), leader=None, flags=set(),
                 reforms={reform}, bar=0.0, modifiers=set())
    set_leader(state)
    return state


def set_leader(state, prefer=None):
    best = max(state['influence'].values())
    top = [f for f, v in state['influence'].items() if v == best]
    state['leader'] = prefer if prefer in top else top[0]


def pair_of(reform):
    return next(pair for pair in PAIRS if rada.reform_id(*pair) == reform)


def expected_second(state):
    """The runner-up the Rada should have: higher influence among the two others, a gap under two points being a tie."""
    lead = state['leader'][4:]
    others = [k for k in KEYS if k != lead]
    a, b = others
    ia, ib = state['influence']['kru_' + a], state['influence']['kru_' + b]
    # two-point steps: ahead means reaching a step the other does not
    step = lambda v: int(v // 2)
    if step(ia) > step(ib):
        return {a}
    if step(ib) > step(ia):
        return {b}
    return {a, b}                                      # a tie: either is acceptable, the old runner-up wins


def expected_bar(state):
    lead_value = state['influence'][state['leader']]
    return 0.75 if lead_value >= 60 else 0.5 if lead_value >= 55 else 0.25 if lead_value >= 50 else 0.0


# ------------------------------------------------------------------------------------------------ checks ---------------------------

def block_or_empty(text, name):
    try:
        return named_block(text, name)
    except KeyError:
        return ''


def check_reforms(reform_text):
    problems = []
    found = re.findall(r'(?m)^(ruthenian_factional_empire\w*_reform) = \{', reform_text)
    if found != REFORM_IDS:
        problems.append(f'the reform file defines {found}, expected {REFORM_IDS}')
    for (second, lead), reform in zip(PAIRS, REFORM_IDS):
        try:
            block = named_block(reform_text, reform)
        except KeyError:
            problems.append(f'{reform} is missing')
            continue
        sides = block_or_empty(block, 'states_general_mechanic')
        names = re.findall(r'(?m)^\s*(kru_rada_\w+) = \{', sides)
        if names != [f'kru_rada_{second}', f'kru_rada_{lead}']:
            problems.append(f'{reform}: sides {names}, expected left kru_rada_{second} (second) then right kru_rada_{lead} (dominant)')
        for key in (second, lead):
            body = normalized(block_or_empty(sides, f'kru_rada_{key}'))
            want = ' '.join(f'{name} = {rada.fmt(value)}' for name, value in BY_KEY[key][4])
            if body != f'kru_rada_{key} = {{ {want} }}':
                problems.append(f'{reform}: the {key} side is not its floor modifiers {want}')
        allow = block_or_empty(block_or_empty(block, 'conditional'), 'allow')
        if 'has_dlc = "Res Publica"' not in allow or 'has_dlc = "Winds of Change"' not in allow:
            problems.append(f'{reform}: the bar is not gated by Res Publica or Winds of Change')
        potential = normalized(block_or_empty(block, 'potential'))
        if reform == 'ruthenian_factional_empire_reform':
            if 'tag = KRU' not in potential or any(f'NOT = {{ has_reform = {o} }}' not in potential for o in REFORM_IDS if o != reform):
                problems.append(f'{reform}: the default reform must be offered to KRU only while it holds no sibling')
        elif potential != f'potential = {{ has_reform = {reform} }}':
            problems.append(f'{reform}: a reform the script swaps in must show only to its holder, found {potential}')
        for needle in ('factions = { kru_knyazi kru_boyary kru_starshyna }', 'ruthenian_factional_court_mechanic', 'locked_government_type = yes',
                       'lock_level_when_selected = yes', 'governing_capacity_modifier = 0.1', 'vassal_income = 0.15'):
            if needle not in normalized(block):
                problems.append(f'{reform} lacks {needle}')
    return problems



def check_logic(triggers_text, effects_text, kru_effects_text, runs=3000, seed=1444):
    problems = []
    interpreter = Interpreter(*load_logic(triggers_text, effects_text, kru_effects_text))

    def refresh(state):
        interpreter.run([('kru_refresh_factional_court_effect', 'yes')], state)

    # 1. a grid of influence triples
    grid = 0
    for a in range(0, 101, 5):
        for b in range(0, 101 - a, 5):
            c = 100 - a - b
            state = fresh((a, b, c))
            kept = dict(state['influence'])
            refresh(state)
            grid += 1
            if state['influence'] != kept:
                problems.append(f'{(a, b, c)}: the refresh changed the influence to {state["influence"]}; a swap must leave the rada\'s influence alone')
                break
            second, lead = pair_of(next(iter(state['reforms'])))
            if state['leader'][4:] != lead:
                problems.append(f'{(a, b, c)}: the Rada holds the reform of leader {lead}, the faction in power is {state["leader"]}')
            if second not in expected_second(state):
                problems.append(f'{(a, b, c)}: the Rada holds second {second}, expected {expected_second(state)}')
            if abs(state['bar'] - expected_bar(state)) > 1e-9:
                problems.append(f'{(a, b, c)}: the bar stands at {state["bar"]}, the leader\'s grip puts it at {expected_bar(state)}')
            before = (set(state['reforms']), state['bar'], set(state['flags']), set(state['modifiers']))
            refresh(state)
            if before != (state['reforms'], state['bar'], state['flags'], state['modifiers']):
                problems.append(f'{(a, b, c)}: a second refresh changed the state')
    # 2. a long walk: one point at a time, the faction in power changes only when another overtakes
    rng = random.Random(seed)
    state = fresh((34, 33, 33))
    refresh(state)
    swaps = 0
    last = None
    for step in range(runs):
        giver, taker = rng.sample(sorted(state['influence']), 2)
        if state['influence'][giver] >= 1:
            state['influence'][giver] -= 1
            state['influence'][taker] += 1
        set_leader(state, prefer=state['leader'])
        kept = dict(state['influence'])
        refresh(state)
        if state['influence'] != kept:
            problems.append(f'step {step}: the refresh changed the influence {kept} to {state["influence"]}')
            break
        if len(state['reforms']) != 1 or not state['reforms'] <= set(REFORM_IDS):
            problems.append(f'step {step}: the Rada holds {state["reforms"]}')
            break
        second, lead = pair_of(next(iter(state['reforms'])))
        if state['leader'][4:] != lead:
            problems.append(f'step {step}: leader {state["leader"]} but reform leader {lead}')
            break
        if second not in expected_second(state):
            problems.append(f'step {step}: second {second}, expected one of {expected_second(state)}')
            break
        if abs(state['bar'] - expected_bar(state)) > 1e-9:
            problems.append(f'step {step}: bar {state["bar"]} against grip {expected_bar(state)}')
            break
        if last is not None and (second, lead) != last:
            swaps += 1
        if last is not None and last[1] == lead and last[0] in expected_second(state) and second != last[0]:
            problems.append(f'step {step}: the runner-up changed from {last[0]} to {second} although {last[0]} is still a valid second (a tie keeps the old one)')
            break
        last = (second, lead)
    if swaps == 0:
        problems.append('the walk never changed the pair: the test would not notice a Rada that cannot swap')
    # 3. a tie keeps the old runner-up, and without one the order knyazi, boyary, starshyna decides
    for lead, old, other in itertools.permutations(KEYS):
        values = {f'kru_{lead}': 40.0, f'kru_{old}': 30.0, f'kru_{other}': 30.0}
        state = fresh((0, 0, 0))
        state['influence'] = values
        state['leader'] = f'kru_{lead}'
        state['flags'] = {f'kru_rada_second_{old}'}
        state['reforms'] = {rada.reform_id(old, lead)}
        refresh(state)
        if pair_of(next(iter(state['reforms']))) != (old, lead):
            problems.append(f'a tie between {old} and {other} under {lead} did not keep the old runner-up {old}')
        order = [k for k in KEYS if k in (old, other)]
        state['influence'] = dict(values)
        state['flags'] = set()
        state['reforms'] = {rada.reform_id(order[1], lead)}         # start from the WRONG pair, so a pair that is never found shows
        refresh(state)
        if pair_of(next(iter(state['reforms']))) != (order[0], lead):
            problems.append(f'a tie with no old runner-up under {lead} did not go to {order[0]} by the order knyazi, boyary, starshyna')
    # 4. the old flags are forgotten, nothing else keeps them
    state = fresh((55, 25, 20))
    state['flags'] |= {'kru_factional_dominance_active', 'kru_current_dominant_knyazi', 'kru_previous_dominant_boyary'}
    refresh(state)
    if state['flags'] & {'kru_factional_dominance_active', 'kru_current_dominant_knyazi', 'kru_previous_dominant_boyary'}:
        problems.append('a refresh leaves the flags of the previous-dominant version in a save')
    # 5. the junior voice: only the runner-up, only from 38
    state = fresh((50, 40, 10))
    refresh(state)
    if state['modifiers'] != {'KRU_junior_boyary'}:
        problems.append(f'knyazi lead, boyary at 40 is the runner-up: expected KRU_junior_boyary, got {state["modifiers"]}')
    state = fresh((50, 35, 15))
    refresh(state)
    if state['modifiers']:
        problems.append(f'a runner-up with 35 influence must not get a junior voice, got {state["modifiers"]}')
    return problems


def check_sources(files):
    problems = []
    for relative in ('events/RuthenianDecadence.txt', 'common/disasters/kru_disasters.txt',
                     'common/scripted_triggers/su_south_ukraine_triggers.txt'):
        text = files[relative]
        if 'has_reform = ruthenian_factional_empire' in text:
            problems.append(f'{relative} still names a Rada reform id instead of asking kru_holds_rada_reform')
        if 'kru_holds_rada_reform = yes' not in text:
            problems.append(f'{relative} does not ask kru_holds_rada_reform')
    if re.search(r'\bruthenian_convene_court\s*=\s*\{', files['decisions/KyivTriggers.txt']):
        problems.append('the retired free court decision has returned')
    court = files['common/government_mechanics/rip_ruthenian_factional_court.txt']
    # `available` is parsed before the scripted triggers exist (measured in the game): it names the six ids itself.
    available = normalized(named_block(court, 'available'))
    for reform in REFORM_IDS:
        if f'has_reform = {reform}' not in available:
            problems.append(f'the court mechanic is not available to the holder of {reform}')
    if 'kru_holds_rada_reform' in available:
        problems.append('the court mechanic asks a scripted trigger in `available`, which the engine parses too early')
    for action, faction in (('kru_court_the_knyazi', 'kru_knyazi'), ('kru_court_the_boyary', 'kru_boyary'), ('kru_court_the_starshyna', 'kru_starshyna')):
        effect = normalized(named_block(named_block(court, 'interactions'), action))
        if f'add_faction_influence = {{ faction = {faction} influence = 25 }}' not in effect:
            problems.append(f'{action} does not add 25 influence to {faction}')
        if effect.index('kru_refresh_factional_court_effect = yes') < effect.index('add_faction_influence'):
            problems.append(f'{action} refreshes the pair before it has changed the influence')
    governments = files['common/governments/00_governments.txt']
    for reform in REFORM_IDS:
        if governments.count(reform) < 3:
            problems.append(f'{reform} is not in all three tier lists of 00_governments.txt (tier 1 and two exclusive sets)')
    names = named_block(files['common/government_names/000_RIP_names.txt'], 'ruthenian_factional_empire_reform')
    for reform in REFORM_IDS:
        if f'has_reform = {reform}' not in names:
            problems.append(f'the government names block does not name {reform}')
    actions = normalized(files['common/on_actions/RIP_KRU_on_actions.txt'])
    if 'on_monthly_pulse = { events = { ruthenian_factions.21 } }' not in actions or 'ruthenian_factions.20' not in actions:
        problems.append('RIP_KRU_on_actions.txt does not run the monthly refresh (ruthenian_factions.21) and the yearly one (.20)')
    events = files['events/RuthenianFactional.txt']
    monthly = events[events.index('id = ruthenian_factions.21'):].split('id = ruthenian_factions.20')[0]
    if 'kru_refresh_factional_court_effect = yes' not in monthly or 'hidden = yes' not in monthly:
        problems.append('ruthenian_factions.21 is not a hidden event that refreshes the Rada')
    if 'kru_update_dominant_pair_effect = yes' not in events:
        problems.append('the yearly event no longer runs kru_update_dominant_pair_effect')
    # Seen in EU4 1.37.5: a refresh that is not hidden prints the bar moves ("Strengthen Starshyna by 1000.00%") in every court button's tooltip.
    refresh = normalized(named_block(files['common/scripted_effects/kru_effects.txt'], 'kru_refresh_factional_court_effect'))
    if 'hidden_effect = {' not in refresh or 'kru_rada_bar_effect = yes' not in refresh.split('hidden_effect = {', 1)[-1]:
        problems.append('kru_refresh_factional_court_effect is not a hidden_effect: its tooltip lines ("Strengthen X by 1000.00%") reach every court button')
    for relative in ('common/scripted_effects/kru_effects.txt',):
        for retired in ('kru_current_dominant', 'kru_previous_dominant', 'kru_factional_dominance_active', 'KRU_pair_', 'KRU_courting_'):
            if retired in files[relative].replace('kru_rada_forget_old_state_effect', ''):
                problems.append(f'{relative} still mentions {retired}')
    return problems


def check_sprites_and_text(loc):
    problems = []
    gfx = read('interface/rip_kru_rada.gfx')
    for key in KEYS:
        if f'name = "GFX_kru_rada_{key}" texturefile = "gfx/interface/rip_government/kru_rada_{key}.dds" noOfFrames = 2' not in gfx:
            problems.append(f'GFX_kru_rada_{key} is not declared with two frames')
        data = (ROOT / f'gfx/interface/rip_government/kru_rada_{key}.dds').read_bytes()
        height, width = struct.unpack('<2I', data[12:20])
        if data[:4] != b'DDS ' or (width, height) != (46, 25):
            problems.append(f'kru_rada_{key}.dds is not a 46x25 DDS (two frames of 23x25)')
        else:
            pixels = data[128:]
            frames = [pixels[(row * 46 + col) * 4: (row * 46 + col) * 4 + 4] for col in range(46) for row in range(25)]
            if sum(1 for p in frames[:25 * 23] if p[3] > 127) < 40 or sum(1 for p in frames[25 * 23:] if p[3] > 127) < 40:
                problems.append(f'kru_rada_{key}.dds has an empty frame')
        for suffix in ('', '_desc', '_MECHANIC_TOOLTIP'):
            for language in LANGUAGES:
                if f'kru_rada_{key}{suffix}' not in loc[language]:
                    problems.append(f'{language}: kru_rada_{key}{suffix} is missing')
    for path in (ROOT / 'localisation').rglob('*.yml'):
        body = path.read_text(encoding='utf-8-sig')
        if 'kru_rada_coalition' in body or 'kru_rada_opposition' in body:
            problems.append(f'{path.name} still localises the retired coalition/opposition sides')
    # The two vanilla texts the Rada corrects (English only): the left end's election sentence and the "reform abolished" window of every swap.
    for key, _, _ in rada.VANILLA_OVERRIDES:
        if key not in loc['english']:
            problems.append(f'english: the corrected vanilla key {key} is missing')
        for language in LANGUAGES[1:]:
            if key in loc[language]:
                problems.append(f'{language}: {key} must stay the vanilla translation, not an English fallback')
    if 'elected every 4 years' in loc['english'].get('STATISTS_DRO', ''):
        problems.append('STATISTS_DRO still promises elected rulers on the left end of the Rada bar')
    if 'abolished' in loc['english'].get('REFORM_DESELECTED_DESC', '') or 'abolished' in loc['english'].get('REFORM_DESELECTED_TITLE', ''):
        problems.append('the window that follows every Rada swap still says the reform was abolished')
    ui = loc['ui']
    for reform in REFORM_IDS:
        if ui.get(reform) != 'Rada of Three Estates':
            problems.append(f'{reform} is not named "Rada of Three Estates"')
        if 'second by influence on the left' not in ui.get(reform + '_desc', ''):
            problems.append(f'{reform}_desc does not tell the player which bloc is on which end of the bar')
    return problems


def load_loc():
    loc = {}
    for language in LANGUAGES:
        text = read(f'localisation/replace/zzzz_rip_kru_rada_l_{language}.yml')
        loc[language] = dict(re.findall(r'(?m)^ (\w+):\d+ "(.*)"$', text))
    loc['ui'] = dict(re.findall(r'(?m)^ (\w+):\d+ "(.*)"$', read('localisation/zzzz_rip_government_ui_l_english.yml')))
    return loc


def sources():
    names = ('events/RuthenianDecadence.txt', 'decisions/KyivTriggers.txt', 'common/disasters/kru_disasters.txt',
             'common/scripted_triggers/su_south_ukraine_triggers.txt', 'common/government_mechanics/rip_ruthenian_factional_court.txt',
             'common/governments/00_governments.txt', 'common/government_names/000_RIP_names.txt', 'common/on_actions/RIP_KRU_on_actions.txt',
             'events/RuthenianFactional.txt', 'common/scripted_effects/kru_effects.txt')
    return {name: read(name) for name in names}


def planted(reform_text, triggers_text, effects_text, kru_effects_text, files, loc):
    def swap(text, old, new, count=1):
        assert old in text, old
        return text.replace(old, new, count)

    first = REFORM_IDS[1]
    cases = {
        'sides swapped in a reform': check_reforms(swap(reform_text, 'kru_rada_knyazi = {', 'kru_rada_X = {', 1)),
        'a reform with a third side': check_reforms(swap(reform_text, 'states_general_mechanic = {', 'states_general_mechanic = {\n\t\t\tkru_rada_boyary = { discipline = 1 }', 1)),
        'a side with another modifier': check_reforms(swap(reform_text, 'discipline = 0.01', 'discipline = 0.02', 1)),
        'a swapped-in reform visible to everyone': check_reforms(swap(reform_text, f'potential = {{\n\t\thas_reform = {first}\n\t}}', 'potential = {\n\t\talways = yes\n\t}', 1)),
        'the bar without its DLC gate': check_reforms(swap(reform_text, 'has_dlc = "Res Publica"', 'always = yes', 1)),
        'a reform missing from the file': check_reforms(reform_text[:reform_text.rindex('ruthenian_factional_empire_hetmans_boyars_reform = {')]),
        'the tie rule dropped': check_logic(triggers_text.replace('has_country_flag = kru_rada_second_boyary', 'always = no'), effects_text, kru_effects_text, runs=300),
        'the priority order reversed': check_logic(swap(triggers_text, 'always = yes', 'always = no', 1), effects_text, kru_effects_text, runs=300),
        'a ladder with the wrong comparison': check_logic(swap(triggers_text, 'kru_ahead_knyazi_boyary = {\n\tOR = {', 'kru_ahead_knyazi_boyary = {\n\tOR = {\n\t\talways = yes', 1), effects_text, kru_effects_text, runs=300),
        'a bar that is not recentred': check_logic(triggers_text, swap(effects_text, '\t\tchange_statists_vs_orangists = -10\n', '', 1), kru_effects_text, runs=300),
        'a bar that follows the wrong grip': check_logic(triggers_text, swap(effects_text, 'change_statists_vs_orangists = 0.5 }', 'change_statists_vs_orangists = 0.25 }', 1), kru_effects_text, runs=300),
        'a swap that removes the held reform first': check_logic(triggers_text, swap(effects_text, '\t\tadd_government_reform = ruthenian_factional_empire_hetmans_princes_reform\n', '\t\tif = { limit = { has_reform = ruthenian_factional_empire_reform } remove_government_reform = ruthenian_factional_empire_reform }\n\t\tadd_government_reform = ruthenian_factional_empire_hetmans_princes_reform\n', 1), kru_effects_text, runs=300),
        'a refresh that skips the reform swap': check_logic(triggers_text, effects_text, swap(kru_effects_text, '\tkru_rada_select_reform_effect = yes\n', '', 1), runs=300),
        'a refresh that skips the pair': check_logic(triggers_text, effects_text, swap(kru_effects_text, '\tkru_rada_rank_effect = yes\n', '', 1), runs=300),
        'a junior voice for any runner-up': check_logic(triggers_text, effects_text, kru_effects_text.replace('influence = 38', 'influence = 20'), runs=300),
        'old flags that survive a refresh': check_logic(triggers_text, swap(effects_text, '\tclr_country_flag = kru_previous_dominant_boyary\n', '', 1), kru_effects_text, runs=300),
        'a file that names a Rada id again': check_sources({**files, 'events/RuthenianDecadence.txt': files['events/RuthenianDecadence.txt'] + '\nhas_reform = ruthenian_factional_empire_reform\n'}),
        'a court mechanic that asks the scripted trigger': check_sources({**files, 'common/government_mechanics/rip_ruthenian_factional_court.txt': swap(files['common/government_mechanics/rip_ruthenian_factional_court.txt'], '\t\t\thas_reform = ruthenian_factional_empire_reform\n', '\t\t\tkru_holds_rada_reform = yes\n', 1)}),
        'a court button that refreshes before it adds': check_sources({**files, 'common/government_mechanics/rip_ruthenian_factional_court.txt': swap(files['common/government_mechanics/rip_ruthenian_factional_court.txt'], 'add_faction_influence = {\n\t\t\t\t\tfaction = kru_boyary\n\t\t\t\t\tinfluence = 25\n\t\t\t\t}', 'kru_refresh_factional_court_effect = yes\n\t\t\t\tadd_faction_influence = {\n\t\t\t\t\tfaction = kru_boyary\n\t\t\t\t\tinfluence = 25\n\t\t\t\t}', 1).replace('add_treasury = 50\n\t\t\t\tkru_refresh_factional_court_effect = yes', 'add_treasury = 50', 1)}),
        'a reform id missing from the tier lists': check_sources({**files, 'common/governments/00_governments.txt': files['common/governments/00_governments.txt'].replace('ruthenian_factional_empire_hetmans_boyars_reform', 'x')}),
        'no monthly refresh': check_sources({**files, 'common/on_actions/RIP_KRU_on_actions.txt': files['common/on_actions/RIP_KRU_on_actions.txt'].replace('ruthenian_factions.21', 'x')}),
        'a refresh that is not hidden': check_sources({**files, 'common/scripted_effects/kru_effects.txt': swap(files['common/scripted_effects/kru_effects.txt'], 'hidden_effect = {', 'if = { limit = { always = yes }', 1)}),
        'a retired flag back in kru_effects': check_sources({**files, 'common/scripted_effects/kru_effects.txt': files['common/scripted_effects/kru_effects.txt'] + '\n# kru_current_dominant_knyazi\n'}),
        'a side text missing': check_sprites_and_text({**loc, 'french': {k: v for k, v in loc['french'].items() if k != 'kru_rada_boyary_desc'}}),
        'a reform with its own name': check_sprites_and_text({**loc, 'ui': {**loc['ui'], REFORM_IDS[3]: 'Rada of Two Estates'}}),
    }
    return [name for name, found in cases.items() if not found], len(cases)


def main():
    result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/build_kru_rada.py'), '--check'], capture_output=True, text=True)
    if result.returncode != 0:
        print('KRU RADA CHECK: FAIL\n  - the generator output is stale:\n' + result.stdout + result.stderr)
        return 1
    reform_text = read('common/government_reforms/RIP_KRU_rada_reforms.txt')
    triggers_text = read('common/scripted_triggers/kru_rada_triggers.txt')
    effects_text = read('common/scripted_effects/kru_rada_effects.txt')
    kru_effects_text = read('common/scripted_effects/kru_effects.txt')
    files, loc = sources(), load_loc()
    problems = check_reforms(reform_text) + check_logic(triggers_text, effects_text, kru_effects_text) + check_sources(files) + check_sprites_and_text(loc)
    unseen, count = planted(reform_text, triggers_text, effects_text, kru_effects_text, files, loc)
    problems += [f'planted violation not caught: {name}' for name in unseen]
    if problems:
        print('KRU RADA CHECK: FAIL')
        for problem in problems[:60]:
            print('  - ' + problem)
        if len(problems) > 60:
            print(f'  ... and {len(problems) - 60} more')
        return 1
    print(f'KRU RADA CHECK: PASS (6 reforms with the second bloc on the left and the dominant bloc on the right; pair logic executed over a grid of influence '
          f'triples and a random walk; bar, junior voice, tie rule, court buttons, events and sprites; {count} planted violations caught)')
    print('LIMIT: static contracts over an interpreter of the script subset the Rada uses. The bar, its sprites, the reform swap and the buttons were not seen in EU4 by this test.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
