"""Contracts for the Greek Catholic synod and eparchy gates.

Measured in EU4 1.37.5 on 2026-09-29 (diagnostics/engine_probes_20260929): a
greek_catholic country never holds papal_influence, because its religion has no
papacy block, so a decision written for that religion and gated on
papal_influence can never open. The same probes showed that add_opinion and
country/province events are silently dropped inside else_if / else bodies of
scripted effects.

What this file holds, all of it source contracts plus the bounded interpreter of
tests/church_testlib.py, not EU4 evidence and not a balance simulation:

  1. no papal_influence gate anywhere in the loaded scripts is reachable by a
     greek_catholic country (the gate must sit in a block that also says
     religion = catholic, or be an event/AI weight);
  2. the four eparchy decisions use the shared standing triggers, the Greek
     Catholic branch reads patriarch_authority, the thresholds keep the papal
     ordering and are not harder than the Orthodox gate beside them;
  3. the Synod button effects set rip_uc_synod_held, which
     preserve_eastern_rite_decision reads, and only when the button is allowed;
  4. the Volhynia and Galicia synod one-shots pay in the recipient's own
     religious currency and leave a flag behind;
  5. the Kyiv council options and the church sobor decision move estates through
     the mod helper, and the sobor spends the influence it asks for;
  6. nothing added here puts add_opinion or an event call in an else_if / else of
     a scripted effect;
  7. planted violations, made from the current text, are caught by the same
     checkers; where git can show the shipped text (git show HEAD:<path>) the
     shipped defects are run through them too.
"""
import re
import subprocess
import sys

from check_religion_settlement import parse, TRIGGERS
from church_testlib import fixture
from clausewitz_testlib import (ROOT, keyed_blocks, matching_brace, named_block, normalized,
                                _mask_comments_and_strings)


def text_of(relative):
    """Scripts are Windows-1252, localisation UTF-8; line endings are normalised."""
    raw = (ROOT / relative).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('cp1252', errors='replace')
    return text.replace('\r\n', '\n')


def head_text(relative):
    """The shipped text of a file, or None when git or the object is missing."""
    try:
        out = subprocess.run(['git', 'show', 'HEAD:' + relative], cwd=ROOT,
                             capture_output=True, check=True).stdout
    except Exception:
        return None
    return out.decode('cp1252', errors='replace').replace('\r\n', '\n')


failures = []


def require(condition, message):
    if not condition:
        failures.append(message)


# ---------------------------------------------------------------------------
# 1. papal_influence gates
# ---------------------------------------------------------------------------
GATE_ROOTS = ('decisions', 'events', 'missions', 'common/scripted_triggers',
              'common/scripted_effects', 'common/on_actions', 'common/disasters',
              'common/government_mechanics', 'common/decisions')
# A modifier inside one of these is a weight, not a gate.
WEIGHT_KEYS = {'mean_time_to_happen', 'ai_will_do', 'ai_weight', 'ai_chance', 'chance'}
PAPAL_CONDITION = re.compile(r'(?<![\w])papal_influence\s*=\s*-?\d')


def block_index(masked):
    """Every brace block: its key, span, ancestor keys and child blocks."""
    stack, done = [], []
    for match in re.finditer(r'([^\s{}=]+)\s*=\s*\{|\{|\}', masked):
        if match.group(0) == '}':
            if stack:
                block = stack.pop()
                block['end'] = match.start()
                done.append(block)
            continue
        block = {'key': match.group(1) or '', 'start': match.end(),
                 'chain': [b['key'] for b in stack], 'kids': []}
        if stack:
            stack[-1]['kids'].append(block)
        stack.append(block)
    return done


def direct_text(masked, block):
    """The block's own tokens, with nested blocks blanked out."""
    chars = list(masked[block['start']:block['end']])
    for kid in block['kids']:
        for index in range(kid['start'] - block['start'] - 1, kid['end'] - block['start'] + 1):
            if 0 <= index < len(chars):
                chars[index] = ' '
    return ''.join(chars)


def unguarded_papal_gates(text):
    """Line numbers of papal_influence conditions a greek_catholic country could face."""
    masked = _mask_comments_and_strings(text)
    blocks = block_index(masked)
    bad = []
    for match in PAPAL_CONDITION.finditer(masked):
        line = masked.count('\n', 0, match.start()) + 1
        holders = [b for b in blocks if b['start'] <= match.start() < b['end']]
        if not holders:
            bad.append(line)
            continue
        block = min(holders, key=lambda b: b['end'] - b['start'])
        if block['key'] == 'modifier' and WEIGHT_KEYS & set(block['chain']):
            continue
        if block['key'] in ('NOT', 'NOR'):
            bad.append(line)
            continue
        # The same block has to say religion = catholic. greek_catholic does not count.
        if re.search(r'\breligion\s*=\s*catholic\b', direct_text(masked, block)):
            continue
        bad.append(line)
    return bad


def script_files():
    for root in GATE_ROOTS:
        base = ROOT / root
        if base.exists():
            yield from sorted(base.rglob('*.txt'))


checked_gates = 0
for path in script_files():
    relative = path.relative_to(ROOT).as_posix()
    body = path.read_bytes().decode('cp1252', errors='replace')
    checked_gates += len(PAPAL_CONDITION.findall(_mask_comments_and_strings(body)))
    for line in unguarded_papal_gates(body):
        failures.append(f'{relative}:{line}: papal_influence gate a greek_catholic country cannot pass '
                        '(use rip_hierarchy_standing_* or put it in an AND with religion = catholic)')
require(checked_gates >= 3, f'papal gate scan found only {checked_gates} conditions; the scanner is not reading the tree')

# ---------------------------------------------------------------------------
# 2. the four eparchy decisions and the shared standing triggers
# ---------------------------------------------------------------------------
STANDING_FILE = 'common/scripted_triggers/rip_hierarchy_standing_triggers.txt'
HLC_FILE = 'decisions/HLCMetropolitanatePaths.txt'
UZH_TRIGGER_FILE = 'common/scripted_triggers/uzh_eparchy_triggers.txt'
UZH_DECISION_FILE = 'decisions/UzhEparchyPath.txt'
LOC_FILE = 'localisation/rip_synod_consequences_l_english.yml'

standing = text_of(STANDING_FILE)
hlc = text_of(HLC_FILE)
uzh_triggers = text_of(UZH_TRIGGER_FILE)
uzh_decisions = text_of(UZH_DECISION_FILE)
loc = text_of(LOC_FILE)


def standing_errors(standing_text, hlc_text, uzh_trigger_text, loc_text):
    """Static shape of the repaired gates; returns a list of messages."""
    errors = []
    thresholds = {}
    for tier in ('low', 'mid', 'high'):
        try:
            gc = normalized(named_block(standing_text, f'rip_gc_hierarchy_standing_{tier}'))
            both = normalized(named_block(standing_text, f'rip_hierarchy_standing_{tier}'))
        except KeyError as error:
            errors.append(f'missing trigger: {error}')
            continue
        found = re.search(r'patriarch_authority = ([0-9.]+)', gc)
        if not found or 'papal_influence' in gc:
            errors.append(f'rip_gc_hierarchy_standing_{tier} must read patriarch_authority and never papal_influence')
        else:
            thresholds[tier] = float(found.group(1))
        gc_branch = re.search(r'AND = \{ religion = greek_catholic (.*?) \}', both)
        cath_branch = re.search(r'AND = \{ religion = catholic papal_influence = (\d+) \}', both)
        if not gc_branch or f'rip_gc_hierarchy_standing_{tier} = yes' not in gc_branch.group(1):
            errors.append(f'rip_hierarchy_standing_{tier}: the greek_catholic branch must call rip_gc_hierarchy_standing_{tier}')
        if not cath_branch:
            errors.append(f'rip_hierarchy_standing_{tier}: the Catholic branch must keep papal_influence beside religion = catholic')
        tooltip = re.search(r'tooltip = (\w+)', gc)
        if tooltip:
            if not re.search(rf'(?m)^\s*{re.escape(tooltip.group(1))}:\d+\s+"', loc_text):
                errors.append(f'missing localisation key {tooltip.group(1)}')
        else:
            errors.append(f'rip_gc_hierarchy_standing_{tier} has no custom_trigger_tooltip')
    if len(thresholds) == 3:
        low, mid, high = thresholds['low'], thresholds['mid'], thresholds['high']
        if not low < mid < high:
            errors.append(f'Greek Catholic thresholds must keep the papal ordering 40 < 50 < 60, got {thresholds}')
        # hlc_confirm_the_metropolitan_see asks 0.5 of an Orthodox state.
        orthodox = re.search(r'religion = orthodox patriarch_authority = ([0-9.]+)', normalized(hlc_text))
        limit = float(orthodox.group(1)) if orthodox else 0.5
        if high > limit:
            errors.append(f'a Greek Catholic gate ({high}) is harder than the Orthodox one beside it ({limit})')
    # Decision wiring.
    try:
        confirm = normalized(named_block(hlc_text, 'hlc_confirm_the_metropolitan_see'))
        union = normalized(named_block(hlc_text, 'hlc_complete_the_union_of_lviv'))
        if not re.search(r'religion = greek_catholic rip_gc_hierarchy_standing_mid = yes', confirm):
            errors.append('hlc_confirm_the_metropolitan_see must gate its greek_catholic branch on rip_gc_hierarchy_standing_mid')
        if 'religion = orthodox patriarch_authority = 0.5' not in confirm:
            errors.append('hlc_confirm_the_metropolitan_see lost its Orthodox patriarch_authority branch')
        if 'rip_gc_hierarchy_standing_high = yes' not in union:
            errors.append('hlc_complete_the_union_of_lviv must gate on rip_gc_hierarchy_standing_high')
        if 'religion = greek_catholic' not in normalized(named_block(named_block(hlc_text, 'hlc_complete_the_union_of_lviv'), 'potential')):
            errors.append('hlc_complete_the_union_of_lviv lost religion = greek_catholic in potential; its allow block has no religion check')
    except KeyError as error:
        errors.append(f'missing decision: {error}')
    try:
        translate = normalized(named_block(uzh_trigger_text, 'uzh_can_translate_the_see'))
        split = normalized(named_block(uzh_trigger_text, 'uzh_can_split_presov_eparchy'))
        if 'rip_hierarchy_standing_low = yes' not in translate:
            errors.append('uzh_can_translate_the_see must use rip_hierarchy_standing_low')
        if 'rip_hierarchy_standing_high = yes' not in split:
            errors.append('uzh_can_split_presov_eparchy must use rip_hierarchy_standing_high')
    except KeyError as error:
        errors.append(f'missing trigger: {error}')
    return errors


for message in standing_errors(standing, hlc, uzh_triggers, loc):
    failures.append(message)

# The decisions still call the triggers that now carry the standing rule.
require('uzh_can_translate_the_see = yes' in uzh_decisions and 'uzh_can_split_presov_eparchy = yes' in uzh_decisions,
        'UzhEparchyPath.txt no longer calls the standing triggers')

# ---- executed: the gates by religion and by number ---------------------------
TRIGGERS.update(parse(standing))
uzh_parsed = dict(parse(uzh_triggers))
for name in ('uzh_can_translate_the_see', 'uzh_can_split_presov_eparchy'):
    TRIGGERS[name] = uzh_parsed[name]
hlc_decisions = dict(dict(parse(hlc))['country_decisions'])


def country(religion, **state):
    world, c, _ = fixture(religion)
    c.update(stability=2, is_at_war=False, is_subject=False, adm_power=500)
    c.update(state)
    return world, c


def open_gate(world, c, name):
    return world.gate([(name, 'yes')], c)


CASES = 0
# Catholic states keep papal_influence and ignore the bar.
for trigger, papal in (('rip_hierarchy_standing_low', 40), ('rip_hierarchy_standing_mid', 50),
                       ('rip_hierarchy_standing_high', 60)):
    world, c = country('catholic', papal_influence=papal, patriarch_authority=0)
    assert open_gate(world, c, trigger), (trigger, 'a Catholic state at the papal threshold')
    world, c = country('catholic', papal_influence=papal - 1, patriarch_authority=1)
    assert not open_gate(world, c, trigger), (trigger, 'one short of the threshold, bar full')
    CASES += 2
# Greek Catholic states use the bar and are not helped by a papal value they cannot hold.
for tier, needed in (('low', .30), ('mid', .35), ('high', .40)):
    for combined in (f'rip_hierarchy_standing_{tier}', f'rip_gc_hierarchy_standing_{tier}'):
        world, c = country('greek_catholic', papal_influence=0, patriarch_authority=needed)
        assert open_gate(world, c, combined), (combined, 'at the threshold')
        world, c = country('greek_catholic', papal_influence=0, patriarch_authority=needed - .01)
        assert not open_gate(world, c, combined), (combined, 'one point short')
        world, c = country('greek_catholic', papal_influence=100, patriarch_authority=needed - .01)
        assert not open_gate(world, c, combined), (combined, 'a papal value must not open it')
        CASES += 3
    world, c = country('orthodox', papal_influence=100, patriarch_authority=1)
    assert not open_gate(world, c, f'rip_hierarchy_standing_{tier}'), 'orthodox is neither Catholic nor Greek Catholic'
    CASES += 1

# Decision level: the Halych confirmation (Orthodox 0.5 unchanged) and the Lviv union.
confirm_allow = dict(hlc_decisions['hlc_confirm_the_metropolitan_see'])['allow']
union_allow = dict(hlc_decisions['hlc_complete_the_union_of_lviv'])['allow']
for religion, papal, bar, expected in (
        ('orthodox', 0, .50, True), ('orthodox', 0, .49, False),
        ('greek_catholic', 0, .35, True), ('greek_catholic', 0, .34, False),
        ('greek_catholic', 100, .34, False),      # papal 100 is not a key for a Greek Catholic state
        ('catholic', 100, 1, False)):             # a Catholic state never asks for the Halych tomos
    world, c = country(religion, papal_influence=papal, patriarch_authority=bar)
    assert world.gate(confirm_allow, c) is expected, (religion, papal, bar, 'hlc_confirm_the_metropolitan_see')
    CASES += 1
for bar, expected in ((.40, True), (.39, False)):
    world, c = country('greek_catholic', papal_influence=100, patriarch_authority=bar)
    assert world.gate(union_allow, c) is expected, (bar, 'hlc_complete_the_union_of_lviv')
    CASES += 1
# The UZH chapters: Catholic on papal influence, Greek Catholic on the bar.
for religion, papal, bar, translate_open, split_open in (
        ('greek_catholic', 0, .30, True, False),
        ('greek_catholic', 0, .29, False, False),
        ('greek_catholic', 100, .29, False, False),
        ('greek_catholic', 0, .40, True, True),
        ('catholic', 40, 0, True, False),
        ('catholic', 60, 0, True, True),
        ('catholic', 39, 1, False, False)):
    world, c = country(religion, papal_influence=papal, patriarch_authority=bar)
    assert open_gate(world, c, 'uzh_can_translate_the_see') is translate_open, (religion, papal, bar, 'translate')
    assert open_gate(world, c, 'uzh_can_split_presov_eparchy') is split_open, (religion, papal, bar, 'presov')
    CASES += 1

# ---------------------------------------------------------------------------
# 3. the Synod button sets rip_uc_synod_held
# ---------------------------------------------------------------------------
UNION_EFFECTS = 'common/scripted_effects/rip_church_union_effects.txt'
DECISIONS_GC = 'decisions/GreekCatholicDecisions.txt'


def synod_flag_errors(effects_text):
    errors = []
    for effect, guard in (('rip_church_gc_infrastructure_effect', 'rip_church_gc_can_infrastructure = yes'),
                          ('rip_church_gc_coexistence_effect', 'rip_church_gc_can_coexistence = yes')):
        try:
            body = named_block(effects_text, effect)
        except KeyError:
            errors.append(f'{effect} is missing')
            continue
        guarded = normalized(named_block(body, 'if'))
        if f'limit = {{ {guard} }}' not in guarded or 'set_country_flag = rip_uc_synod_held' not in guarded:
            errors.append(f'{effect} must set rip_uc_synod_held inside the if guarded by {guard}')
        if 'set_country_flag = rip_uc_synod_held' in normalized(body).replace(guarded, ''):
            errors.append(f'{effect} sets rip_uc_synod_held outside its guard')
    return errors


effects_now = text_of(UNION_EFFECTS)
for message in synod_flag_errors(effects_now):
    failures.append(message)
require('has_country_flag = rip_uc_synod_held' in normalized(named_block(text_of(DECISIONS_GC), 'preserve_eastern_rite_decision')),
        'preserve_eastern_rite_decision no longer reads rip_uc_synod_held; the setter contract has no reader')

# ---- executed: refusing the button sets nothing, taking it sets the flag ------
for effect, needs_rights in (('rip_church_gc_infrastructure_effect', False), ('rip_church_gc_coexistence_effect', True)):
    for bar, expected in ((.5, True), (.1, False)):
        world, c, province = fixture('greek_catholic')
        c.update(patriarch_authority=bar, treasury=500, is_at_war=False)
        if needs_rights:
            province['flags']['rip_church_rite_recognized'] = world.day
        world.run(effect, c)
        assert ('rip_uc_synod_held' in c['flags']) is expected, (effect, bar, 'synod flag')
        CASES += 1

# ---------------------------------------------------------------------------
# 4. Volhynia and Galicia synod one-shots
# ---------------------------------------------------------------------------
VOL_FILE = 'events/Volhynia_Alt_History.txt'
GAL_FILE = 'events/RIP_Galicia_AltHistory.txt'


def event_block(text, event_id):
    for _, block in keyed_blocks(text, 'country_event'):
        if f'id = {event_id}' in block:
            return block
    raise KeyError(event_id)


def option_block(event, name):
    for _, block in keyed_blocks(event, 'option'):
        if f'name = {name}' in block:
            return block
    raise KeyError(name)


def one_shot_errors(vol_text, gal_text):
    errors = []
    try:
        vol = event_block(vol_text, 'rip_vol_alt_history.3')
        for suffix in 'abc':
            option = normalized(option_block(vol, f'rip_vol_alt_history.3.{suffix}'))
            if 'set_country_flag = rip_vol_synod_held' not in option:
                errors.append(f'rip_vol_alt_history.3.{suffix} does not set rip_vol_synod_held')
            if re.search(r'(?<![\w])add_papal_influence', option):
                errors.append(f'rip_vol_alt_history.3.{suffix} pays papal influence a Greek Catholic state cannot spend')
        for suffix in 'ab':
            if 'rip_faith_mission_resource_effect' not in normalized(option_block(vol, f'rip_vol_alt_history.3.{suffix}')):
                errors.append(f'rip_vol_alt_history.3.{suffix} must pay through rip_faith_mission_resource_effect')
    except KeyError as error:
        errors.append(f'missing Volhynia event or option: {error}')
    try:
        gal = event_block(gal_text, 'rip_galicia.2')
        option = normalized(option_block(gal, 'rip_galicia.2.a'))
        if 'set_country_flag = rip_galicia_synod_held' not in option:
            errors.append('rip_galicia.2.a does not set rip_galicia_synod_held')
        if re.search(r'(?<![\w])add_papal_influence', option):
            errors.append('rip_galicia.2.a pays papal influence a Greek Catholic state cannot spend')
        if 'rip_faith_mission_resource_effect' not in option:
            errors.append('rip_galicia.2.a must pay through rip_faith_mission_resource_effect')
        if 'set_country_flag = rip_galicia_synod_held' in normalized(option_block(gal, 'rip_galicia.2.b')):
            errors.append('rip_galicia.2.b (the brotherhoods) must not claim a synod sat')
    except KeyError as error:
        errors.append(f'missing Galicia event or option: {error}')
    return errors


vol_now, gal_now = text_of(VOL_FILE), text_of(GAL_FILE)
for message in one_shot_errors(vol_now, gal_now):
    failures.append(message)

# ---------------------------------------------------------------------------
# 5. Kyiv council estates and the church sobor
# ---------------------------------------------------------------------------
COUNCIL_FILE = 'events/RIP_ChurchCouncils.txt'
KYIV_FILE = 'decisions/KyivTriggers.txt'
ESTATE_FOR_OPTION = {'a': 'estate_church', 'b': 'estate_burghers', 'c': 'estate_nobles'}
# Not part of this repair: the AI numbers stay as shipped.
COUNCIL_AI = {'a': 35, 'b': 35, 'c': 30}


def kyiv_errors(council_text, kyiv_text):
    errors = []
    try:
        event = event_block(council_text, 'rip_church_council.1')
        for suffix, estate in ESTATE_FOR_OPTION.items():
            option = normalized(option_block(event, f'rip_church_council.1.{suffix}'))
            if not re.search(rf'rip_estate_mood_effect = \{{ ESTATE = {estate} LOYALTY = \d+ \}}', option):
                errors.append(f'rip_church_council.1.{suffix} must call rip_estate_mood_effect for {estate}')
            if re.search(r'add_estate_loyalty', option):
                errors.append(f'rip_church_council.1.{suffix} bypasses the has_estate guard of rip_estate_mood_effect')
            if f'ai_chance = {{ factor = {COUNCIL_AI[suffix]} }}' not in option:
                errors.append(f'rip_church_council.1.{suffix} AI weight is no longer {COUNCIL_AI[suffix]}')
    except KeyError as error:
        errors.append(f'missing council event or option: {error}')
    try:
        sobor = named_block(kyiv_text, 'kyiv_convene_church_sobor')
        allow = normalized(named_block(sobor, 'allow'))
        effect = normalized(named_block(sobor, 'effect'))
        if 'estate_influence = { estate = estate_church influence = 60 }' not in allow:
            errors.append('kyiv_convene_church_sobor lost its estate_church influence requirement')
        if not re.search(r'any_owned_province = \{ NOT = \{ religion = ROOT \} \}', allow):
            errors.append('kyiv_convene_church_sobor must require an owned province of another faith')
        if not re.search(r'add_estate_influence_modifier = \{ estate = estate_church (?:desc = \w+ )?influence = -\d+ duration = \d+ \}', effect):
            errors.append('kyiv_convene_church_sobor must spend estate_church influence with a negative modifier')
        if 'limit = { has_estate = estate_church }' not in effect:
            errors.append('kyiv_convene_church_sobor spends influence without the has_estate guard')
        if not re.search(r'ai_will_do = \{ factor = 1 \}', normalized(sobor)):
            errors.append('kyiv_convene_church_sobor AI weight is no longer factor 1')
    except KeyError as error:
        errors.append(f'missing sobor block: {error}')
    return errors


council_now, kyiv_now = text_of(COUNCIL_FILE), text_of(KYIV_FILE)
for message in kyiv_errors(council_now, kyiv_now):
    failures.append(message)
for key in ('rip_kyiv_sobor_other_faith_tt', 'EST_VAL_RIP_KYIV_CHURCH_SOBOR'):
    require(re.search(rf'(?m)^\s*{key}:\d+\s+"', loc), f'missing localisation key {key}')
require('tooltip = rip_kyiv_sobor_other_faith_tt' in kyiv_now and 'desc = EST_VAL_RIP_KYIV_CHURCH_SOBOR' in kyiv_now,
        'KyivTriggers.txt does not use its two new localisation keys')

# ---------------------------------------------------------------------------
# 6. F1: no opinion or event call in an else_if / else of a scripted effect
# ---------------------------------------------------------------------------
F1_CALLS = re.compile(r'\b(add_opinion|reverse_add_opinion|country_event|province_event)\b')


def f1_errors(effect_text, names):
    errors = []
    for name in names:
        try:
            body = named_block(effect_text, name)
        except KeyError:
            errors.append(f'{name} is missing')
            continue
        for key in ('else_if', 'else'):
            for _, block in keyed_blocks(body, key):
                hit = F1_CALLS.search(normalized(block))
                if hit:
                    errors.append(f'{name}: {hit.group(1)} inside {key} is dropped by EU4 1.37.5')
    return errors


SYNOD_EFFECTS = ('rip_church_gc_infrastructure_effect', 'rip_church_gc_coexistence_effect')
for message in f1_errors(effects_now, SYNOD_EFFECTS):
    failures.append(message)

# ---------------------------------------------------------------------------
# 7. planted violations: every checker above must catch what it guards
# ---------------------------------------------------------------------------
PLANTED = 0


def planted(label, errors, expected_fragment=None):
    global PLANTED
    errors = [str(e) for e in errors]
    if not errors:
        failures.append(f'SELF-TEST FAILED: planting "{label}" was not caught')
    elif expected_fragment and not any(expected_fragment in e for e in errors):
        failures.append(f'SELF-TEST FAILED: planting "{label}" was caught for the wrong reason: {errors}')
    PLANTED += 1


def swap(text, old, new):
    assert old in text, f'planting anchor missing: {old!r}'
    return text.replace(old, new, 1)


# Gates: put the shipped defect back into the current text.
planted('papal_influence = 40 back in uzh_can_translate_the_see',
        unguarded_papal_gates(swap(uzh_triggers, 'rip_hierarchy_standing_low = yes', 'papal_influence = 40')))
planted('papal_influence = 60 back in uzh_can_split_presov_eparchy',
        unguarded_papal_gates(swap(uzh_triggers, 'rip_hierarchy_standing_high = yes', 'papal_influence = 60')))
planted('papal_influence = 60 back in hlc_complete_the_union_of_lviv',
        unguarded_papal_gates(swap(hlc, 'rip_gc_hierarchy_standing_high = yes', 'papal_influence = 60')))
planted('papal_influence = 50 beside religion = greek_catholic',
        unguarded_papal_gates(swap(hlc, 'rip_gc_hierarchy_standing_mid = yes', 'papal_influence = 50')))
planted('greek_catholic passed off as the Catholic guard',
        unguarded_papal_gates(swap(standing, 'religion = catholic\n\t\t\tpapal_influence = 40',
                                   'religion = greek_catholic\n\t\t\tpapal_influence = 40')))
planted('papal_influence under NOT',
        unguarded_papal_gates('x = { NOT = { religion = catholic papal_influence = 5 } }'))
planted('a bare papal_influence gate in a decision',
        unguarded_papal_gates('d = { allow = { papal_influence = 10 } }'))
assert not unguarded_papal_gates('m = { mean_time_to_happen = { months = 1 modifier = { factor = 0.7 papal_influence = 50 } } }'), \
    'an MTTH weight is not a gate'
assert not unguarded_papal_gates('e = { limit = { religion = catholic papal_influence = 5 } }'), \
    'a Catholic-guarded gate is fine'

# Standing triggers: break the shape.
planted('greek_catholic branch reading papal_influence in the standing trigger',
        standing_errors(swap(standing, 'patriarch_authority = 0.30', 'papal_influence = 30'), hlc, uzh_triggers, loc),
        'must read patriarch_authority')
planted('a threshold above the Orthodox gate',
        standing_errors(swap(standing, 'patriarch_authority = 0.40', 'patriarch_authority = 0.60'), hlc, uzh_triggers, loc),
        'harder than the Orthodox one')
planted('thresholds out of order',
        standing_errors(swap(standing, 'patriarch_authority = 0.35', 'patriarch_authority = 0.25'), hlc, uzh_triggers, loc),
        'papal ordering')
planted('decision no longer calling the standing trigger',
        standing_errors(standing, swap(hlc, 'rip_gc_hierarchy_standing_high = yes', 'always = yes'), uzh_triggers, loc),
        'hlc_complete_the_union_of_lviv')
planted('standing tooltip key deleted',
        standing_errors(standing, hlc, uzh_triggers, loc.replace('rip_gc_hierarchy_standing_low_tt:0', 'renamed_key:0')),
        'missing localisation key')
planted('uzh trigger no longer using the standing rule',
        standing_errors(standing, hlc, swap(uzh_triggers, 'rip_hierarchy_standing_low = yes', 'always = yes'), loc),
        'uzh_can_translate_the_see')

# Synod flag: take it out of the effects, or set it outside the guard.
planted('rip_uc_synod_held removed from the Synod button effects',
        synod_flag_errors(effects_now.replace('set_country_flag = rip_uc_synod_held', 'clr_country_flag = rip_church_forced_integration')),
        'must set rip_uc_synod_held')
planted('rip_uc_synod_held set outside the guard',
        synod_flag_errors(swap(effects_now, 'rip_church_gc_infrastructure_effect = {',
                               'rip_church_gc_infrastructure_effect = {\n set_country_flag = rip_uc_synod_held')),
        'outside its guard')

# One-shots: the flags and the two papal regressions.
planted('rip_vol_synod_held removed',
        one_shot_errors(vol_now.replace('set_country_flag = rip_vol_synod_held', 'set_country_flag = rip_vol_other'), gal_now),
        'rip_vol_synod_held')
planted('papal influence back in rip_vol_alt_history.3.b',
        one_shot_errors(swap(vol_now, 'rip_faith_mission_resource_effect = { PA = 0.2 PI = 50 ADM = 50 }',
                             'add_papal_influence = 50'), gal_now),
        'papal influence')
planted('papal influence back in rip_galicia.2.a',
        one_shot_errors(vol_now, swap(gal_now, 'rip_faith_mission_resource_effect = { PA = 0.25 PI = 25 ADM = 25 }',
                                      'add_papal_influence = 25')),
        'papal influence')
planted('rip_galicia_synod_held removed',
        one_shot_errors(vol_now, gal_now.replace('set_country_flag = rip_galicia_synod_held', 'set_country_flag = rip_galicia_other')),
        'rip_galicia_synod_held')

# Kyiv: helper bypassed, sobor spends nothing, weights moved.
planted('estate helper removed from a council option',
        kyiv_errors(swap(council_now, 'rip_estate_mood_effect = { ESTATE = estate_burghers LOYALTY = 10 }', ''), kyiv_now),
        'estate_burghers')
planted('unguarded add_estate_loyalty in a council option',
        kyiv_errors(swap(council_now, 'rip_estate_mood_effect = { ESTATE = estate_nobles LOYALTY = 10 }',
                         'add_estate_loyalty = { estate = estate_nobles loyalty = 10 }'), kyiv_now),
        'estate_nobles')
planted('council AI weight changed',
        kyiv_errors(swap(council_now, 'ai_chance = { factor = 30 }', 'ai_chance = { factor = 60 }'), kyiv_now),
        'AI weight')
planted('sobor spending removed',
        kyiv_errors(council_now, re.sub(r'add_estate_influence_modifier = \{[^}]*\}', '', kyiv_now, count=1)),
        'must spend estate_church influence')
planted('sobor allow without the other-faith province',
        kyiv_errors(council_now, swap(kyiv_now, 'any_owned_province = { NOT = { religion = ROOT } }', 'always = yes')),
        'another faith')

# F1: an opinion or an event in an else_if / else of a synod effect.
planted('add_opinion in an else_if of a synod effect',
        f1_errors(swap(effects_now, ' add_country_modifier = { name = rip_church_gc_coexistence duration = 3650 }',
                       ' else_if = { limit = { always = yes } add_opinion = { who = ROOT modifier = x } }\n'
                       ' add_country_modifier = { name = rip_church_gc_coexistence duration = 3650 }'),
                  ('rip_church_gc_coexistence_effect',)),
        'add_opinion')
planted('country_event in an else of a synod effect',
        f1_errors(swap(effects_now, ' add_country_modifier = { name = rip_church_gc_infrastructure duration = 3650 }',
                       ' else = { country_event = { id = x.1 } }\n'
                       ' add_country_modifier = { name = rip_church_gc_infrastructure duration = 3650 }'),
                  ('rip_church_gc_infrastructure_effect',)),
        'country_event')

# The shipped defects, from git: the same checkers must have caught them. Once the
# repair is committed, HEAD:<path> is the repaired text and is simply clean.
SHIPPED = 0
for relative, checker in (
        (UZH_TRIGGER_FILE, unguarded_papal_gates),
        (HLC_FILE, unguarded_papal_gates),
        (UNION_EFFECTS, synod_flag_errors),
        (VOL_FILE, lambda t: one_shot_errors(t, gal_now)),
        (GAL_FILE, lambda t: one_shot_errors(vol_now, t)),
        (COUNCIL_FILE, lambda t: kyiv_errors(t, kyiv_now)),
        (KYIV_FILE, lambda t: kyiv_errors(council_now, t))):
    shipped = head_text(relative)
    if shipped is not None and checker(shipped):
        SHIPPED += 1

# ---------------------------------------------------------------------------
if failures:
    print('FAIL: %d problem(s)' % len(failures))
    for item in failures:
        print(' -', item)
    sys.exit(1)
print(f'PASS: {checked_gates} papal_influence conditions, all Catholic-guarded or weights; '
      f'{CASES} executed gate and flag cases; {PLANTED} planted violations caught; '
      f'{SHIPPED} shipped-defect files flagged from git HEAD; '
      'thresholds are design values, campaign balance unverified')
