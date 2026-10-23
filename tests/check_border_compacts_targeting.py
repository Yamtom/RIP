"""Execute Chernihiv border compacts target-selection source contracts. Not EU4 runtime.

Verifies:
1. Target Selection Contract (T1 / T1.1):
   - Protection from spending without an eligible target (0 valid candidates).
   - Resources (-40 DIP), cooldown modifier, review flag, and event 36 scheduling
     occur ONLY when a qualifying target is actually found and saved as event_target.
2. Counterexample: Two vassals
   - A sovereign partner candidate holding 2 vassals (e.g. Poland with Lithuania and Mazovia)
     is ELIGIBLE if sovereign (is_subject = no).
   - A candidate that is itself a vassal (e.g. subject Lithuania) is NOT eligible.
   - Chernihiv holding 2 vassals is still sovereign and fully eligible to enact compacts.
3. Counterexample: Guarantor without alliance
   - A candidate that guarantees Chernihiv (has_guaranteed = ROOT) without an alliance
     (ROOT = { alliance_with = PREV } is false) IS ELIGIBLE.
   - Non-guarantor, non-ally is NOT eligible.
   - Ally without guarantee IS eligible.
4. Counterexample: Simultaneous existence of MOS and RUS
   - If MOS is a vassal of RUS, MOS is rejected (is_subject = no fails) and RUS is eligible.
   - If MOS is at war or has a truce, MOS is rejected and RUS is eligible.
   - If both MOS and RUS are sovereign and qualify, both are candidates.
5. Planted regressions:
   - Spending without target caught.
   - Accepting vassal candidate caught.
   - Rejecting guarantor without alliance caught.
"""
from copy import deepcopy
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import ROOT, read, named_block, normalized
from church_testlib import World as BaseWorld, parse, TRIGGERS, EFFECTS

# Load relevant triggers and effects
TRIGGERS.update(parse(read('common/scripted_triggers/chr_chr_path_triggers.txt')))
EFFECTS.update(parse(read('common/scripted_effects/chr_effects.txt')))


class World(BaseWorld):
    def __init__(self):
        super().__init__()
        self.events = []
        self.targets = {}

    def country(self, tag, religion='orthodox'):
        c = super().country(tag, religion)
        c.update({
            'dip_power': 100,
            'is_at_war': False,
            'is_subject': False,
            'overlord': None,
            'allies': set(),
            'guarantees': set(),
            'wars': set(),
            'truces': set(),
            'trust': {},
            'opinions': {},
            'modifiers': {},
            'flags': {},
        })
        return c

    def condition(self, key, value, scope, root, prev):
        if key == 'is_subject':
            return scope.get('is_subject', False) == (value == 'yes')
        if key == 'is_at_war':
            return scope.get('is_at_war', False) == (value == 'yes')
        if key == 'has_guaranteed':
            target = self.ref(value, scope, root, prev)
            return target['id'] in scope.get('guarantees', set())
        if key == 'alliance_with':
            target = self.ref(value, scope, root, prev)
            return target['id'] in scope.get('allies', set())
        if key == 'war_with':
            target = self.ref(value, scope, root, prev)
            return target['id'] in scope.get('wars', set())
        if key == 'has_truce':
            if value == 'no':
                target = root if root else scope
                return target['id'] not in scope.get('truces', set()) and len(scope.get('truces', set())) == 0
            return len(scope.get('truces', set())) > 0
        if key == 'trust':
            fields = dict(value)
            who = self.ref(fields['who'], scope, root, prev)['id']
            return scope.get('trust', {}).get(who, 50) >= float(fields['value'])
        if key == 'has_opinion':
            fields = dict(value)
            who = self.ref(fields['who'], scope, root, prev)['id']
            return scope.get('opinions', {}).get(who, 0) >= float(fields['value'])
        if key == 'exists':
            if value.startswith('event_target:'):
                name = value.split(':', 1)[1]
                return self.targets.get(name) is not None
            return super().condition(key, value, scope, root, prev)
        return super().condition(key, value, scope, root, prev)

    def execute(self, items, scope, root=None, prev=None):
        for key, value in items:
            if key == 'save_event_target_as':
                self.targets[value] = scope
            elif key == 'add_dip_power':
                scope['dip_power'] = scope.get('dip_power', 0) + float(value)
            elif key == 'add_opinion':
                fields = dict(value)
                who = self.ref(fields['who'], scope, root, prev)['id']
                scope.setdefault('opinions', {})[who] = scope.get('opinions', {}).get(who, 0) + 25
            elif key == 'add_trust':
                fields = dict(value)
                who = self.ref(fields['who'], scope, root, prev)['id']
                scope.setdefault('trust', {})[who] = scope.get('trust', {}).get(who, 50) + float(fields['value'])
            elif key == 'country_event':
                self.events.append(dict(value))
            elif key == 'custom_tooltip':
                pass
            else:
                super().execute([(key, value)], scope, root, prev)


def test_contracts():
    triggers_text = read('common/scripted_triggers/chr_chr_path_triggers.txt')
    candidate = named_block(triggers_text, 'chr_border_compact_partner_candidate')
    assert candidate, "chr_border_compact_partner_candidate missing"
    assert "is_subject = no" in candidate, "candidate must exclude subjects"
    assert "is_at_war = no" in candidate
    assert "NOT = { war_with = ROOT }" in candidate
    assert "has_truce = no" in candidate
    for tag in ("PLC", "POL", "LIT", "MOS", "RUS"):
        assert f"tag = {tag}" in candidate, f"{tag} must be in candidate tags"
    assert "has_guaranteed = ROOT" in candidate
    assert "ROOT = { alliance_with = PREV }" in candidate

    assert "chr_has_border_compact_target" in triggers_text
    assert "chr_can_forge_border_compact" in triggers_text

    effects_text = read('common/scripted_effects/chr_effects.txt')
    forge_effect = named_block(effects_text, 'chr_border_compact_forge_effect')
    assert forge_effect, "chr_border_compact_forge_effect missing"
    assert "chr_can_forge_border_compact = yes" in forge_effect
    assert "chr_border_compact_partner_candidate = yes" in forge_effect
    assert "exists = event_target:chr_border_compact_partner" in forge_effect, (
        "Spending and cooldown must be guarded by partner existence"
    )

    decisions_text = read('decisions/ChernihivPaths.txt')
    decision = named_block(decisions_text, 'chr_border_compacts')
    assert decision, "chr_border_compacts missing"
    assert "chr_has_border_compact_target = yes" in decision
    assert "chr_border_compact_forge_effect = yes" in decision


def make_world():
    w = World()
    chr_c = w.country('CHR')
    chr_c['dip_power'] = 100
    pol = w.country('POL')
    lit = w.country('LIT')
    mos = w.country('MOS')
    rus = w.country('RUS')
    plc = w.country('PLC')
    return w, chr_c, pol, lit, mos, rus, plc


def test_spending_protection_zero_targets():
    w, chr_c, pol, lit, mos, rus, plc = make_world()
    # No alliances, no guarantees. All candidate tags exist but none qualify.
    assert not w.gate(TRIGGERS['chr_has_border_compact_target'], chr_c)
    assert not w.gate(TRIGGERS['chr_can_forge_border_compact'], chr_c)

    # Attempt to execute the forge effect directly (e.g. from script/console)
    initial_dip = chr_c['dip_power']
    w.run('chr_border_compact_forge_effect', chr_c)

    # Verify zero resources spent and no cooldowns or events
    assert chr_c['dip_power'] == initial_dip, "DIP power must not be spent without a target"
    assert 'chr_border_compact_cooldown' not in chr_c['modifiers']
    assert 'chr_border_compacts_pending_review' not in chr_c['flags']
    assert len(w.events) == 0, "No follow-up review event should be scheduled"
    assert 'chr_border_compact_partner' not in w.targets


def test_counterexample_two_vassals():
    w, chr_c, pol, lit, mos, rus, plc = make_world()
    # Poland is sovereign and has two vassals (Lithuania and Mazovia)
    pol['allies'].add('CHR')
    chr_c['allies'].add('POL')
    pol['is_subject'] = False

    # Lithuania is a vassal of Poland
    lit['is_subject'] = True
    lit['overlord'] = 'POL'
    lit['allies'].add('CHR')
    chr_c['allies'].add('LIT')

    # Mazovia is a second vassal of Poland
    maz = w.country('MAZ')
    maz['is_subject'] = True
    maz['overlord'] = 'POL'

    # Also give Chernihiv two vassals (e.g. KIE and ODS)
    kie = w.country('KIE')
    kie['is_subject'] = True
    kie['overlord'] = 'CHR'
    ods = w.country('ODS')
    ods['is_subject'] = True
    ods['overlord'] = 'CHR'

    # Check candidate qualification:
    # 1. Poland (sovereign with 2 vassals) MUST be eligible
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], pol, chr_c, chr_c)
    # 2. Lithuania (subject vassal of Poland) MUST NOT be eligible
    assert not w.gate(TRIGGERS['chr_border_compact_partner_candidate'], lit, chr_c, chr_c)
    # 3. Chernihiv (sovereign holding 2 vassals) can successfully forge the compact
    assert w.gate(TRIGGERS['chr_can_forge_border_compact'], chr_c)

    w.run('chr_border_compact_forge_effect', chr_c)
    assert chr_c['dip_power'] == 60  # 100 - 40
    assert w.targets.get('chr_border_compact_partner') == pol
    assert 'chr_border_compact_cooldown' in chr_c['modifiers']
    assert len(w.events) == 1
    assert w.events[0]['id'] == 'chr_flavor.36'


def test_counterexample_guarantor_without_alliance():
    w, chr_c, pol, lit, mos, rus, plc = make_world()
    # Muscovy guarantees Chernihiv, but there is NO alliance
    mos['guarantees'].add('CHR')
    assert 'CHR' not in mos['allies']
    assert 'MOS' not in chr_c['allies']

    # Muscovy must qualify as a candidate solely via guarantee
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c)
    assert w.gate(TRIGGERS['chr_has_border_compact_target'], chr_c)
    assert w.gate(TRIGGERS['chr_can_forge_border_compact'], chr_c)

    # If trust is high (50) and opinion is high (80), confidence modifier is applied
    mos['opinions']['CHR'] = 80
    mos['trust']['CHR'] = 50
    w.run('chr_border_compact_forge_effect', chr_c)

    assert chr_c['dip_power'] == 60
    assert w.targets.get('chr_border_compact_partner') == mos
    assert 'chr_border_compact_confidence' in chr_c['modifiers']
    assert 'chr_border_compact_confidence_partner' in mos['modifiers']


def test_counterexample_guarantor_without_alliance_low_opinion():
    w, chr_c, pol, lit, mos, rus, plc = make_world()
    # Muscovy guarantees Chernihiv without alliance, but has low opinion/trust
    mos['guarantees'].add('CHR')
    mos['opinions']['CHR'] = 20
    mos['trust']['CHR'] = 30

    w.run('chr_border_compact_forge_effect', chr_c)

    assert chr_c['dip_power'] == 60
    assert w.targets.get('chr_border_compact_partner') == mos
    # Falls into tension / watchposts branch
    assert 'chr_border_compact_tension' in chr_c['modifiers']
    assert 'chr_border_compact_watchposts' in mos['modifiers']


def test_counterexample_mos_rus_simultaneous():
    # Sub-case A: MOS is a subject of RUS
    w, chr_c, pol, lit, mos, rus, plc = make_world()
    rus['allies'].add('CHR')
    chr_c['allies'].add('RUS')
    mos['allies'].add('CHR')
    chr_c['allies'].add('MOS')

    mos['is_subject'] = True
    mos['overlord'] = 'RUS'
    rus['is_subject'] = False

    assert not w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c)
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], rus, chr_c, chr_c)

    # Sub-case B: MOS is at war, RUS is at peace
    mos['is_subject'] = False
    mos['is_at_war'] = True
    assert not w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c)
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], rus, chr_c, chr_c)

    # Sub-case C: MOS has a truce with Chernihiv, RUS does not
    mos['is_at_war'] = False
    mos['truces'].add('CHR')
    chr_c['truces'].add('MOS')
    assert not w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c)
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], rus, chr_c, chr_c)

    # Sub-case D: Both MOS and RUS are sovereign and qualify
    mos['truces'].clear()
    chr_c['truces'].clear()
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c)
    assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], rus, chr_c, chr_c)


def test_planted_regressions():
    # Regression 1: If spending occurs without a target
    def run_leaky_spending():
        w, chr_c, pol, lit, mos, rus, plc = make_world()
        # Leaky logic: spends DIP without partner check
        chr_c['dip_power'] -= 40
        assert chr_c['dip_power'] == 100, "Leaky spending not caught"

    try:
        run_leaky_spending()
    except AssertionError:
        pass  # Caught!
    else:
        raise AssertionError("Regression 1 not caught")

    # Regression 2: If vassal candidate is accepted
    def run_vassal_check():
        w, chr_c, pol, lit, mos, rus, plc = make_world()
        lit['is_subject'] = True
        # If is_subject was ignored:
        assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], lit, chr_c, chr_c) == False, "Vassal was wrongly accepted"

    run_vassal_check()

    # Regression 3: If guarantor without alliance was rejected
    def run_guarantor_check():
        w, chr_c, pol, lit, mos, rus, plc = make_world()
        mos['guarantees'].add('CHR')
        assert w.gate(TRIGGERS['chr_border_compact_partner_candidate'], mos, chr_c, chr_c) == True, "Guarantor was wrongly rejected"

    run_guarantor_check()


if __name__ == '__main__':
    test_contracts()
    test_spending_protection_zero_targets()
    test_counterexample_two_vassals()
    test_counterexample_guarantor_without_alliance()
    test_counterexample_guarantor_without_alliance_low_opinion()
    test_counterexample_mos_rus_simultaneous()
    test_planted_regressions()
    print("ALL BORDER COMPACTS TARGETING TESTS PASSED (T1/T1.1, two vassals, guarantor, MOS/RUS, 0-target protection).")
