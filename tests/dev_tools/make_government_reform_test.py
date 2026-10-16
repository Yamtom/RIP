"""Generate the government-reform test fixture from the live script.

The fixture is a pair of files in tests/dev_tools/ that the game does not load:

    RIP_GovernmentReformTest.txt     country events (namespace rip_gov_test)
    rip_gov_test_l_english.yml       their English localisation

Choosing a reform in the menu gives the country everything the reform asks for
and then the reform itself: government type, tag, religion, primary culture,
path flags, prerequisite reforms and the numeric stats that can be raised. Before the
reform is added the fixture evaluates the reform's own `potential` and `trigger`
(copied verbatim from common/government_reforms) and writes the result to game.log,
so a reform whose conditions the fixture failed to grant shows up as a marker,
not as a silent gap. Conditions that script cannot grant (the date, an
institution that is not enabled yet, an age) are listed in the result window and
expected to fail.

Usage (from anywhere):

    python tests/dev_tools/make_government_reform_test.py            regenerate both files
    python tests/dev_tools/make_government_reform_test.py --check    exit 1 when they are stale
    python tests/dev_tools/make_government_reform_test.py --install  copy them into events/ and localisation/
    python tests/dev_tools/make_government_reform_test.py --remove   delete those copies
    python tests/dev_tools/make_government_reform_test.py --report [game.log]
                                                                     read the RIP_GOV_TEST markers
    python tests/dev_tools/make_government_reform_test.py --trace DIR
                                                                     write a copy with extra TRACE lines
                                                                     (tag, government, province counts) to DIR

Re-run after any change to reform tiers, reform conditions or the scripted triggers
they use.

How the conditions are found: each reform's `potential` and `trigger` become one boolean
formula, scripted triggers inlined. A small solver walks the OR arms and keeps the cheapest
consistent set of facts (a tag, a flag, a reform, a religion, a number); each fact has a grant
in grant_lines(). A fact no effect can give (the date, an age, an institution that is not
enabled yet, being a subject) is recorded as "cannot be given" and the check marks the option
with `*`. The in-game self-check is what proves the plan: it evaluates the reform's real
`potential` and `trigger` after the grants.

Measured in EU4 1.37.5 (see tests/dev_tools/README.md): a country event fired from an effect
runs at once and nested; after change_tag the scope an event was fired for is a dead country,
so everything that follows a tag change is addressed to the human country afresh
(fire_human); change_government to the same type keeps the reforms, to another type drops
them; add_government_reform validates the reform's conditions after adding it.
"""

from __future__ import annotations

import argparse
import copy
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))

from clausewitz_testlib import keyed_blocks, matching_brace, named_block, _mask_comments_and_strings  # noqa: E402

NS = "rip_gov_test"
PAGE_SIZE = 7
TYPE_ORDER = ["monarchy", "republic", "theocracy", "tribal", "native"]
EVT_PATH = ROOT / "tests/dev_tools/RIP_GovernmentReformTest.txt"
LOC_PATH = ROOT / "tests/dev_tools/rip_gov_test_l_english.yml"
INSTALLED = [ROOT / "events/RIP_GovernmentReformTest.txt", ROOT / "localisation/rip_gov_test_l_english.yml"]

REFORMS = BASIC = FORMULAS = None  # set by generate() and build()
TRACE = False  # --trace: extra log lines around the grants, for debugging the fixture itself

ID_INDEX = 1  # event ids: 1-2 group index, 3 battery summary, 10+ group pages
ID_INDEX2 = 2
ID_BATTERY_DONE = 3
ID_PAGE0 = 10
ID_RESET = 90
ID_BATTERY = 91
ID_CLEAR = 99
ID_APPLY0 = 1000  # + variant number
ID_POPUP0 = 2000

# Groups of the menu, in order: (key, title, source files). A reform file that is not
# listed here gets a group of its own at the end, so a new file is never dropped.
GROUPS = [
    ("CHR", "CHR - Siversk Veche", ["RIP_CHR_government_reforms.txt"]),
    ("HET", "HET - Hetmanate", ["RIP_HET_government_reforms.txt"]),
    ("ZAZ", "ZAZ - Zaporozhia", ["RIP_ZAZ_government_reforms.txt", "RIP_ZAZ_HET_path_reforms.txt"]),
    ("KIE", "KIE and KRU - Kyivan Rus", ["RIP_KIE_KRU_government_reforms.txt"]),
    ("HLC", "HLC - Halych", ["RIP_HLC_government_reforms.txt"]),
    ("VLN", "VLN - Volhynia", ["RIP_VLN_government_reforms.txt"]),
    ("PDL", "PDL - Podillia", ["RIP_PDL_government_reforms.txt"]),
    ("PRL", "PRL - Pereiaslav", ["RIP_PRL_government_reforms.txt"]),
    ("UZH", "UZH - Uzhhorod", ["RIP_UZH_government_reforms.txt"]),
    ("LIT", "LIT - Grand Duchy", ["RIP_LIT_government_reforms.txt"]),
    ("ODS", "ODS - Odesa", ["RIP_ODS_government_reforms.txt"]),
    ("SHR", "Shared - Ruthenian", ["RIP_shared_ruthenian_government_reforms.txt"]),
    ("SHC", "Shared - Cossack and republic",
     ["RIP_shared_cossack_government_reforms.txt", "RIP_shared_global_government_reforms.txt"]),
]

# Cost of making one condition true; the solver keeps the cheapest consistent set. A prerequisite
# reform costs more than a tag plus its path flag, so the entry arm of an OR (the one a decision opens)
# wins over "hold any other reform of the family".
COST_TAG, COST_REFORM, COST_CHANGE, COST_FLAG, COST_STAT, COST_BAD = 10, 12, 3, 1, 3, 1000

# ---------------------------------------------------------------- tokens and tree

TOKEN = re.compile(r'#[^\n]*|"[^"\n]*"|\{|\}|<=|>=|=|<|>|[^\s{}=<>#"]+')
COMPARE = ("=", "<", ">", "<=", ">=")


def parse(text):
    """Clausewitz text -> list of (key, value) where value is a string or a nested list."""
    toks = [t for t in TOKEN.findall(text) if not t.startswith("#")]
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks) and toks[pos] != "}":
            t = toks[pos]
            if t == "{":
                pos += 1
                out.append(("__block__", block()))
                pos += 1
            elif pos + 2 < len(toks) and toks[pos + 1] in COMPARE:
                key, op, val = t, toks[pos + 1], toks[pos + 2]
                if op == "=" and val == "{":
                    pos += 3
                    out.append((key, block()))
                    pos += 1
                else:
                    out.append((key, val if op == "=" else op + val))
                    pos += 3
            else:
                out.append(("__bare__", t))
                pos += 1
        return out

    return block()


def child_inner_text(block_text, key):
    """Raw text between the braces of `key = { ... }` sitting at depth 1 of `block_text`."""
    masked = _mask_comments_and_strings(block_text)
    for m in re.finditer(r"\b" + re.escape(key) + r"\s*=\s*\{", masked):
        depth = masked.count("{", 0, m.start()) - masked.count("}", 0, m.start())
        if depth == 1:
            opening = m.end() - 1
            return block_text[opening + 1: matching_brace(block_text, opening)]
    return None


def strip_comments(text):
    """Drop `#` comments, leaving quoted strings alone."""
    out = []
    for raw in text.split("\n"):
        in_string, cut = False, len(raw)
        for i, ch in enumerate(raw):
            if ch == '"':
                in_string = not in_string
            elif ch == "#" and not in_string:
                cut = i
                break
        out.append(raw[:cut].rstrip())
    return "\n".join(out)


# ---------------------------------------------------------------- governments and reforms

def load_governments():
    gov_text = (ROOT / "common/governments/00_governments.txt").read_text(encoding="utf-8-sig")
    gov = {}
    for g in TYPE_ORDER:
        try:
            block = named_block(gov_text, g)
        except KeyError:
            continue
        basic = re.search(r"(?m)^\s*basic_reform\s*=\s*([A-Za-z0-9_]+)", block).group(1)
        levels = named_block(block, "reform_levels")
        tiers = []
        for m in re.finditer(r"(?m)^\t\t([A-Za-z0-9_]+)\s*=\s*\{", levels):
            closing = levels.find("}", levels.find("{", m.start()))  # a tier holds one flat reforms list
            ids_match = re.search(r"reforms\s*=\s*\{([^}]*)\}", levels[m.start(): closing + 1])
            if ids_match:
                tiers.append((m.group(1), ids_match.group(1).split()))
        exclusives = []
        for _, blk in keyed_blocks(block, "exclusive_reforms"):
            masked = _mask_comments_and_strings(blk)
            exclusives.append(masked[masked.find("{") + 1: masked.rfind("}")].split())
        gov[g] = {"basic": basic, "tiers": tiers, "exclusives": exclusives}
    return gov


def top_blocks(text):
    masked = _mask_comments_and_strings(text)
    for m in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", masked):
        opening = text.find("{", m.start())
        yield m.group(1), text[m.start(): matching_brace(text, opening) + 1]


def load_reforms():
    reforms = {}
    for path in sorted((ROOT / "common/government_reforms").glob("*.txt")):
        for name, block in top_blocks(path.read_text(encoding="utf-8-sig")):
            reforms[name] = {
                "file": path.name,
                "potential": child_inner_text(block, "potential"),
                "trigger": child_inner_text(block, "trigger"),
            }
    return reforms


def load_scripted_triggers():
    out = {}
    for path in sorted((ROOT / "common/scripted_triggers").glob("*.txt")):
        for name, block in top_blocks(path.read_text(encoding="utf-8-sig")):
            if name in ("AND", "OR", "NOT"):
                continue
            out[name] = parse(block)[0][1]  # a later definition of the same name wins, as in the engine
    return out


# ---------------------------------------------------------------- conditions as formulas

TRUE, FALSE = ("true",), ("false",)


def mk_and(xs):
    out = []
    for x in xs:
        if x == FALSE:
            return FALSE
        if x != TRUE:
            out.append(x)
    return TRUE if not out else out[0] if len(out) == 1 else ("and", out)


def mk_or(xs):
    out = []
    for x in xs:
        if x == TRUE:
            return TRUE
        if x != FALSE:
            out.append(x)
    return FALSE if not out else out[0] if len(out) == 1 else ("or", out)


def negate(f):
    kind = f[0]
    if kind == "true":
        return FALSE
    if kind == "false":
        return TRUE
    if kind == "lit":
        return ("lit", f[1], f[2], not f[3])
    if kind == "and":
        return mk_or([negate(x) for x in f[1]])
    return mk_and([negate(x) for x in f[1]])


def serialize(items):
    parts = []
    for k, v in items:
        if k == "__bare__":
            parts.append(v)
        elif isinstance(v, list):
            parts.append(f"{k} = {{ {serialize(v)} }}")
        else:
            parts.append(f"{k} = {v}")
    return " ".join(parts)


class Formulas:
    """Builds boolean formulas out of potential/trigger blocks, inlining scripted triggers."""

    def __init__(self, reforms, strig):
        self.reforms = reforms
        self.strig = strig
        self.cache = {}

    def of_reform(self, rid):
        if rid not in self.cache:
            r = self.reforms[rid]
            parts = [self.of_text(r[k]) for k in ("potential", "trigger") if r[k] is not None]
            self.cache[rid] = mk_and(parts)
        return self.cache[rid]

    def of_text(self, text):
        return self.of_items(parse(text), ())

    def of_items(self, items, seen):
        out, i = [], 0
        while i < len(items):
            key, val = items[i]
            i += 1
            if key in ("__bare__", "tooltip", "limit"):
                continue
            if key == "if" and isinstance(val, list):
                branches = [(val, None)]
                while i < len(items) and items[i][0] in ("else_if", "else") and isinstance(items[i][1], list):
                    branches.append((items[i][1], items[i][0]))
                    i += 1
                out.append(self.ite(branches, seen))
                continue
            out.append(self.node(key, val, seen))
        return mk_and(out)

    def ite(self, branches, seen):
        arms, earlier = [], []
        for body, kind in branches:
            if kind == "else":
                arms.append(mk_and(earlier + [self.of_items(body, seen)]))
                return mk_or(arms)
            limit = next((v for k, v in body if k == "limit" and isinstance(v, list)), [])
            cond = self.of_items(limit, seen)
            arms.append(mk_and(earlier + [cond, self.of_items(body, seen)]))
            earlier = earlier + [negate(cond)]
        arms.append(mk_and(earlier))
        return mk_or(arms)

    def node(self, key, val, seen):
        if isinstance(val, list):
            if key in ("AND", "__block__", "custom_trigger_tooltip"):
                return self.of_items(val, seen)
            if key == "OR":
                return mk_or([self.of_items([it], seen) for it in val if it[0] != "__bare__"])
            if key in ("NOT", "NOR"):  # NOT = { a b } is "neither a nor b"
                return mk_and([negate(self.of_items([it], seen)) for it in val if it[0] != "__bare__"])
            return ("lit", key, serialize(val), True)  # a scoped or counting block is one opaque atom
        if key == "always":
            return TRUE if val == "yes" else FALSE
        if key in self.strig and val in ("yes", "no") and key not in seen and len(seen) < 8:
            body = self.of_items(self.strig[key], seen + (key,))
            return body if val == "yes" else negate(body)
        return ("lit", key, val, True)


def flags_in(f, acc):
    if f[0] == "lit":
        if f[1] == "has_country_flag":
            acc.add(f[2])
    elif f[0] in ("and", "or"):
        for x in f[1]:
            flags_in(x, acc)


# ---------------------------------------------------------------- solver

class State:
    """One consistent way to make a formula true."""

    def __init__(self):
        self.tag = None
        self.tag_not = frozenset()
        self.religion = None
        self.religion_not = frozenset()
        self.culture = None
        self.culture_not = frozenset()
        self.reforms = ()
        self.reforms_not = frozenset()
        self.flags = frozenset()
        self.flags_not = frozenset()
        self.stats = {}
        self.bad = ()
        self.assumed = ()
        self.attempts = ()
        self.cost = 0

    def clone(self):
        c = copy.copy(self)
        c.stats = dict(self.stats)
        return c

    def key(self):
        return (self.tag, self.religion, self.culture, tuple(sorted(self.reforms)), self.flags,
                tuple(sorted(self.stats.items())), self.bad)


class Env:
    def __init__(self, g, rid, gov, forbid=()):
        self.g, self.rid, self.gov = g, rid, gov
        self.forbid = {rid, *forbid}  # reforms the plan must not hold while the check runs
        tiers = gov[g]["tiers"]
        self.tier_of = {r: i for i, (_, ids) in enumerate(tiers) for r in ids}
        self.tier_of[gov[g]["basic"]] = -1
        self.exclusives = gov[g]["exclusives"]


STAT_KEYS = {"adm_tech", "mil_tech", "dip_tech", "army_tradition", "army_professionalism", "manpower_percentage"}
BAD_POSITIVE = {
    "is_year": "the year must be {v} or later; script cannot set the date",
    "current_age": "the current age must be {v}; script cannot set the age",
    "has_institution": "institution {v} is not enabled at the 1444 start (embracement is tried once it is)",
    "army_size_percentage": "army size must be {v} of the force limit (needs a force-limit modifier)",
    "is_subject": "the country must be a subject",
    "liberty_desire": "liberty desire must reach {v} (needs to be a subject)",
    "mission_completed": "mission {v} must be completed",
    "is_playing_custom_nation": "must be a custom nation",
    "have_had_reform": "must once have held reform {v}",
    "is_revolutionary": "must be a revolutionary country",
    "map_setup": "map_setup must be {v}",
    "was_tag": "must once have been tag {v}",
    "exists": "country {v} must exist",
    "development": "development condition {v}",
}


def owned_dev_key(text):
    """`value = N development = D` (nothing else) -> a stats key, else None."""
    items = dict((k, v) for k, v in parse(text) if not isinstance(v, list))
    if len(items) == len(parse(text)) and set(items) == {"value", "development"}:
        return f"owned_dev_{int(float(items['value']))}_{int(float(items['development']))}"
    return None


def add(st, field, value):
    setattr(st, field, getattr(st, field) | {value})


def bad(st, key, val, text):
    note = text.format(v=val)
    if note not in st.bad:
        st.bad = st.bad + (note,)
        st.cost += COST_BAD
    return st


def apply_lit(st, key, val, pos, env):
    """Make the literal (key = val, pos) true on a copy of `st`; None when it contradicts `st`."""
    s = st.clone()
    if key == "tag":
        if pos:
            if val in s.tag_not or (s.tag not in (None, val)):
                return None
            if s.tag is None:
                s.tag = val
                s.cost += COST_TAG
        else:
            if s.tag == val:
                return None
            add(s, "tag_not", val)
        return s
    if key == "has_reform":
        if pos:
            if val in env.forbid or val in s.reforms_not or val not in env.tier_of:
                return None
            if val in s.reforms:
                return s
            tier = env.tier_of[val]
            for other in s.reforms:
                if env.tier_of.get(other) == tier and tier != -1:
                    return None
                if any(val in blk and other in blk for blk in env.exclusives):
                    return None
            s.reforms = s.reforms + (val,)
            s.cost += COST_REFORM
        else:
            if val in s.reforms:
                return None
            add(s, "reforms_not", val)
        return s
    if key == "has_country_flag":
        if pos:
            if val in s.flags_not:
                return None
            if val not in s.flags:
                add(s, "flags", val)
                s.cost += COST_FLAG
        else:
            if val in s.flags:
                return None
            add(s, "flags_not", val)
        return s
    if key in ("religion", "primary_culture"):
        fld, fld_not = ("religion", "religion_not") if key == "religion" else ("culture", "culture_not")
        if pos:
            if val in getattr(s, fld_not) or getattr(s, fld) not in (None, val):
                return None
            if getattr(s, fld) is None:
                setattr(s, fld, val)
                s.cost += COST_CHANGE
        else:
            if getattr(s, fld) == val:
                return None
            add(s, fld_not, val)
        return s
    if key in STAT_KEYS:
        if pos:
            try:
                num = float(val)
            except ValueError:
                return None
            if num > s.stats.get(key, -1):
                s.stats[key] = num
                s.cost += COST_STAT
        return s  # a negative stat condition holds at the start values
    if key == "republican_tradition":
        if pos:
            if env.g == "republic":
                s.stats[key] = max(s.stats.get(key, 0), float(val))
                s.cost += COST_STAT
                return s
            return bad(s, key, val, "republican tradition exists only in a republic")
        return s
    if key == "num_of_owned_provinces_with" and pos:
        want = owned_dev_key(val)
        if want:
            s.stats[want] = 1.0
            s.cost += COST_STAT
            return s
        return bad(s, key, val, "an owned-province count condition that script cannot give (see the reform)")
    if key == "has_institution" and pos:
        s.attempts = s.attempts + (val,)
        return bad(s, key, val, BAD_POSITIVE[key])
    if key == "has_dlc":
        if pos:
            s.assumed = s.assumed + (f"DLC {val} is installed",)
            return s
        return bad(s, key, val, "the DLC {v} must be missing")
    if key in BAD_POSITIVE:
        if pos:
            return bad(s, key, val, BAD_POSITIVE[key])
        return s  # the negative of a date, age, institution or status holds at the 1444 start
    if key == "is_not_blocked_by_estate_privilege":
        return s
    # unknown atom: a positive one is a gap the check will show, a negative one is left alone
    return bad(s, key, val, "no grant is known for " + key + " = {v}") if pos else s


def prune(states, beam=48):
    seen, out = set(), []
    for st in sorted(states, key=lambda x: x.cost):  # stable: arm order breaks ties
        k = st.key()
        if k not in seen:
            seen.add(k)
            out.append(st)
    return out[:beam]


def solve(f, states, env):
    kind = f[0]
    if kind == "true":
        return states
    if kind == "false":
        return []
    if kind == "lit":
        return [n for n in (apply_lit(s, f[1], f[2], f[3], env) for s in states) if n is not None]
    if kind == "and":
        cur = states
        for x in f[1]:
            cur = prune(solve(x, cur, env))
            if not cur:
                return []
        return cur
    out = []
    for x in f[1]:
        out.extend(solve(x, states, env))
    return prune(out)


def evaluate(f, st, held=()):
    """Closed-world check of a formula against the planned state (used to test the solver).

    `held` names reforms counted as held on top of the planned ones.
    """
    kind = f[0]
    if kind == "true":
        return True
    if kind == "false":
        return False
    if kind == "and":
        return all(evaluate(x, st, held) for x in f[1])
    if kind == "or":
        return any(evaluate(x, st, held) for x in f[1])
    _, key, val, pos = f
    if key == "tag":
        truth = st.tag == val
    elif key == "has_reform":
        truth = val in st.reforms or val in held
    elif key == "has_country_flag":
        truth = val in st.flags
    elif key == "religion":
        truth = st.religion == val
    elif key == "primary_culture":
        truth = st.culture == val
    elif key in STAT_KEYS or key == "republican_tradition":
        truth = key in st.stats and st.stats[key] >= float(val)
    elif key == "num_of_owned_provinces_with":
        truth = owned_dev_key(val) in st.stats
    elif key == "has_dlc":
        truth = True
    elif key == "is_not_blocked_by_estate_privilege":
        truth = True
    else:
        truth = False
    return truth if pos else not truth


# ---------------------------------------------------------------- variants and plans

class Variant:
    pass


def build_variants(gov, reforms, formulas):
    rip = set(reforms)
    basic_of = {gov[g]["basic"]: g for g in gov}
    out = []
    for rid in sorted(rip):
        if rid in basic_of:
            out.append((rid, basic_of[rid], None, -1))
            continue
        found = [(g, name, idx) for g in TYPE_ORDER if g in gov
                 for idx, (name, ids) in enumerate(gov[g]["tiers"]) if rid in ids]
        if not found:
            raise SystemExit(f"reform {rid} is in no tier and is not a basic reform")
        out.extend((rid, g, name, idx) for g, name, idx in found)

    group_of_file = {f: (k, t) for k, t, files in GROUPS for f in files}
    variants = []
    for rid, g, tier, idx in out:
        v = Variant()
        v.id, v.g, v.tier, v.tier_idx = rid, g, tier, idx
        gk, gt = group_of_file.get(reforms[rid]["file"], (reforms[rid]["file"], "Other - " + reforms[rid]["file"]))
        v.group_key, v.group_title = gk, gt
        v.plan = plan_for(v, gov, reforms, formulas)
        variants.append(v)
    group_rank = {k: i for i, (k, _, _) in enumerate(GROUPS)}
    order = {g: i for i, g in enumerate(TYPE_ORDER)}
    variants.sort(key=lambda v: (group_rank.get(v.group_key, 99), v.group_key, order[v.g], v.tier_idx, v.id))
    for n, v in enumerate(variants, 1):
        v.n = n
    return variants


class Plan:
    pass


def plan_for(v, gov, reforms, formulas):
    env = Env(v.g, v.id, gov)
    p = Plan()
    p.script_only = False
    p.skipped = []
    p.has_potential = reforms[v.id]["potential"] is not None
    p.has_trigger = reforms[v.id]["trigger"] is not None
    cands = solve(formulas.of_reform(v.id), [State()], env)
    if not cands:  # every arm needs the reform itself (or a reform of another type): only script can give it
        p.script_only = True
        p.names_itself = bool(solve(formulas.of_reform(v.id), [State()], Env(v.g, None, gov)))
        st = State()
    else:
        st = cands[0]
        if not evaluate(formulas.of_reform(v.id), st) and not st.bad:
            raise SystemExit(f"solver bug: the plan for {v.id} does not satisfy its own formula")
    # prerequisite reforms bring the conditions of their own path (tag, flags, ...) as far as they agree
    done, queue = {v.id}, list(st.reforms)
    while queue:
        pre = queue.pop(0)
        if pre in done:
            continue
        done.add(pre)
        if pre not in reforms:
            continue
        got = [c for c in solve(formulas.of_reform(pre), [st], Env(v.g, pre, gov, forbid=(v.id,))) if len(c.bad) == len(st.bad)]
        if got:
            queue.extend(r for r in got[0].reforms if r not in st.reforms)
            st = got[0]
        else:
            p.skipped.append(pre)
    tier_of = Env(v.g, v.id, gov).tier_of
    p.state = st
    p.reforms = sorted(set(st.reforms), key=lambda r: (tier_of.get(r, 99), r))
    p.bad = list(st.bad)
    p.assumed = sorted(set(st.assumed))
    if p.script_only:
        p.bad = ["only a script can give this reform: its conditions name the reform itself" if p.names_itself else
                 "its conditions need a reform of another government type"]
    p.expect_fail = bool(p.bad)
    # The engine adds a reform and then validates its trigger, so a trigger that does not name the
    # reform itself stops add_government_reform while any of its conditions is out of reach.
    p.may_refuse = p.expect_fail and not evaluate(formulas.of_reform(v.id), st, held={v.id})
    return p


# ---------------------------------------------------------------- text builders

def tabs(n):
    return "\t" * n


def indent_block(text, depth):
    lines = [l for l in strip_comments(text).split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    base = min((len(l) - len(l.lstrip("\t ")) for l in lines if l.strip()), default=0)
    return [tabs(depth) + l[base:].replace("    ", "\t").rstrip() for l in lines]


def stat_effect(key, val):
    if key.startswith("owned_dev_"):
        _, _, count, dev = key.split("_")
        return [f"random_owned_province = {{ limit = {{ NOT = {{ development = {dev} }} }} add_base_tax = {dev} }}"
                for _ in range(int(count))]
    num = float(val)
    shown = str(int(num)) if num == int(num) else str(num)
    if key in ("adm_tech", "mil_tech", "dip_tech"):
        return [f"if = {{ limit = {{ NOT = {{ {key} = {shown} }} }} add_{key} = {shown} }}"]
    if key == "army_tradition":
        return [f"if = {{ limit = {{ NOT = {{ army_tradition = {shown} }} }} add_army_tradition = 100 }}"]
    if key == "republican_tradition":
        return [f"if = {{ limit = {{ NOT = {{ republican_tradition = {shown} }} }} add_republican_tradition = 100 }}"]
    if key == "army_professionalism":
        return [f"if = {{ limit = {{ NOT = {{ army_professionalism = {shown} }} }} add_army_professionalism = 1 }}"]
    if key == "manpower_percentage":
        return [f"if = {{ limit = {{ NOT = {{ manpower_percentage = {shown} }} }} add_manpower = 9999 }}"]
    raise SystemExit(f"no grant for stat {key}")


def trace_yes_no(v, cond, name):
    """With --trace: log whether `cond` holds; otherwise nothing."""
    if not TRACE:
        return []
    mark = f"RIP_GOV_TEST TRACE {v.id} {v.g} {name}"
    return [f'if = {{ limit = {{ {cond} }} log = "{mark} YES" }}',
            f'if = {{ limit = {{ NOT = {{ {cond} }} }} log = "{mark} NO" }}']


def grant_lines(v):
    """Effects that give the country what the reform asks for, one per line."""
    st = v.plan.state
    out = []
    if st.tag:
        t = st.tag
        out += [f"if = {{ limit = {{ NOT = {{ tag = {t} }} }}"]
        out += ["\t" + l for l in trace_yes_no(v, f"exists = {t}", f"exists {t} before")]
        out += [f"\tif = {{ limit = {{ exists = {t} }} inherit = {t} }}"]
        out += ["\t" + l for l in trace_yes_no(v, f"exists = {t}", f"exists {t} after inherit")]
        out += [f"\tchange_tag = {t}"]
        out += ["\t" + l for l in trace_yes_no(v, f"tag = {t}", f"tag {t} after change_tag")]
        out += ["\ton_change_tag_effect = yes"]
        out += ["\t" + l for l in trace_yes_no(v, f"tag = {t}", f"tag {t} after on_change_tag_effect")]
        out += ["}"]
    if st.religion:
        out.append(f"if = {{ limit = {{ NOT = {{ religion = {st.religion} }} }} change_religion = {st.religion} }}")
    if st.culture:
        out.append(f"if = {{ limit = {{ NOT = {{ primary_culture = {st.culture} }} }} "
                   f"change_primary_culture = {st.culture} }}")
    for key in sorted(st.stats):
        if key.startswith("owned_dev_"):
            _, _, count, dev = key.split("_")
            out += trace_yes_no(v, f"num_of_owned_provinces_with = {{ value = {count} }}", f"owns {count} provinces before")
            out += trace_yes_no(v, f"num_of_owned_provinces_with = {{ value = 1 development = {dev} }}",
                                f"owns a province of development {dev} before")
        out += stat_effect(key, st.stats[key])
        if key.startswith("owned_dev_"):
            out += trace_yes_no(v, f"num_of_owned_provinces_with = {{ value = 1 development = {dev} }}",
                                f"owns a province of development {dev} after")
    for inst in sorted(set(st.attempts)):  # best effort: only works once the institution is enabled
        out.append(f"if = {{ limit = {{ is_institution_enabled = {inst} }} "
                   f"capital_scope = {{ add_institution_embracement = {{ which = {inst} value = 100 }} }} }}")
    out += [f"set_country_flag = {f}" for f in sorted(st.flags)]
    out += [f"clr_country_flag = {f}" for f in sorted(st.flags_not)]
    out += [f"add_government_reform = {r}" for r in v.plan.reforms]
    return out


def verify_lines(v):
    """After the grants: one GRANT_FAIL marker per planned item that is not in place."""
    st = v.plan.state
    wanted = []
    if st.tag:
        wanted.append((f"tag = {st.tag}", f"tag:{st.tag}"))
    if st.religion:
        wanted.append((f"religion = {st.religion}", f"religion:{st.religion}"))
    if st.culture:
        wanted.append((f"primary_culture = {st.culture}", f"culture:{st.culture}"))
    for key in sorted(st.stats):
        if key.startswith("owned_dev_"):
            _, _, count, dev = key.split("_")
            wanted.append((f"num_of_owned_provinces_with = {{ value = {count} development = {dev} }}", f"provinces:{count}x{dev}"))
        else:
            num = st.stats[key]
            wanted.append((f"{key} = {int(num) if num == int(num) else num}", f"stat:{key}"))
    wanted += [(f"has_country_flag = {f}", f"flag:{f}") for f in sorted(st.flags)]
    wanted += [(f"has_reform = {r}", f"reform:{r}") for r in v.plan.reforms]
    return [f"if = {{ limit = {{ NOT = {{ {cond} }} }} set_country_flag = rip_gov_test_fail "
            f'log = "RIP_GOV_TEST GRANT_FAIL {v.id} {v.g} {what}" }}' for cond, what in wanted]


def summary_lines(v):
    """Plain-text account of what the option gives and what it cannot give."""
    p, st = v.plan, v.plan.state
    lines = [f"Reform: {v.id}", f"Government: {v.g}, " + (f"tier {v.tier_idx + 1} ({v.tier})" if v.tier else "basic reform")]
    given = []
    if st.tag:
        given.append(f"tag {st.tag} (another country holding it is annexed first)")
    if st.religion:
        given.append(f"religion {st.religion}")
    if st.culture:
        given.append(f"primary culture {st.culture}")
    if st.stats:
        given.append("stats " + ", ".join(
            (f"{k[10:].split('_')[0]} provinces of development {k[10:].split('_')[1]}" if k.startswith("owned_dev_")
             else f"{k} {int(x) if x == int(x) else x}") for k, x in sorted(st.stats.items())))
    if st.flags:
        given.append("flags " + ", ".join(sorted(st.flags)))
    if p.reforms:
        given.append("reforms " + ", ".join(p.reforms))
    lines.append("Given: " + ("; ".join(given) if given else "nothing besides the reform"))
    if p.assumed:
        lines.append("Assumed: " + "; ".join(p.assumed))
    if p.skipped:
        lines.append("Prerequisite reforms held without their own path: " + ", ".join(p.skipped))
    lines.append("Cannot be given: " + ("; ".join(p.bad) if p.bad else "none"))
    if p.may_refuse:
        lines.append("The game checks a reform's trigger when it is added, so this reform may not stay while those conditions fail.")
    return lines


def loc_text(lines):
    text = "\\n".join(lines).replace('"', "'")
    return text


def check_lines(v, which, depth):
    """Evaluate the reform's own block before the reform is added; writes POT_/TRG_ markers."""
    block = {"POT": ("potential", v.plan.has_potential), "TRG": ("trigger", v.plan.has_trigger)}[which]
    name, present = block
    mark = f"RIP_GOV_TEST {{}} {v.id} {v.g}"
    out = []
    if not present:
        out.append(f'log = "{mark.format(which + "_NONE")}"')
        return [tabs(depth) + l for l in out]
    text = REFORMS[v.id][name]
    flag = f"rip_gov_test_chk_{which.lower()}"
    out.append(f"set_country_flag = {flag}")
    out.append("if = {")
    out.append("\tlimit = {")
    out += indent_block(text, 2)
    out.append("\t}")
    out.append(f"\tclr_country_flag = {flag}")
    out.append(f'\tlog = "{mark.format(which + "_OK")}"')
    out.append("}")
    out.append(f"if = {{ limit = {{ has_country_flag = {flag} }} clr_country_flag = {flag} "
               f'set_country_flag = rip_gov_test_fail log = "{mark.format(which + "_FAIL")}" }}')
    return [tabs(depth) + l for l in out]


def apply_event(v):
    alt = "republic" if v.g == "monarchy" else "monarchy"
    mark = f"RIP_GOV_TEST {{}} {v.id} {v.g}"
    L = [
        "country_event = {",
        f"\tid = {NS}.{ID_APPLY0 + v.n}",
        f"\ttitle = {NS}.t",
        f"\tdesc = {NS}.d",
        "\tpicture = ADMINISTRATIVE_REFORM_eventPicture",
        "\thidden = yes",
        "\tis_triggered_only = yes",
        f"\toption = {{ name = {NS}.a }}",
        "\timmediate = {",
        f"\t\t# {v.id} | {v.g} | {v.tier or 'basic'}",
        f'\t\tlog = "{mark.format("BEGIN")}"',
        f"\t\tcountry_event = {{ id = {NS}.{ID_RESET} }}",
        "\t\t# a switch to another type drops every reform; the switch back leaves the basic one",
        f"\t\tchange_government = {alt}",
        f"\t\tchange_government = {v.g}",
    ]
    L += [tabs(2) + l for l in trace_yes_no(v, f"government = {v.g}", f"government {v.g} after the switches")]
    L += [tabs(2) + l for l in grant_lines(v)]
    L += [tabs(2) + l for l in verify_lines(v)]
    L += check_lines(v, "POT", 2)
    L += check_lines(v, "TRG", 2)
    if v.id not in BASIC:
        L.append(f"\t\tadd_government_reform = {v.id}")
    L.append(f"\t\tif = {{ limit = {{ has_reform = {v.id} }} log = \"{mark.format('HELD_OK')}\" }}")
    L.append(f"\t\tif = {{ limit = {{ NOT = {{ has_reform = {v.id} }} }} set_country_flag = rip_gov_test_fail "
             f"log = \"{mark.format('HELD_FAIL')}\" }}")
    L += ["\t}", "}", ""]
    return L


def popup_event(v, back_page, nxt, prev):
    n = ID_POPUP0 + v.n
    L = [
        "country_event = {",
        f"\tid = {NS}.{n}",
        f"\ttitle = {NS}.{n}.t",
        f"\tdesc = {NS}.{n}.d",
        "\tpicture = ADMINISTRATIVE_REFORM_eventPicture",
        "\tis_triggered_only = yes",
        "",
        "\toption = {",
        f"\t\tname = {NS}.back_ok",
        "\t\ttrigger = { NOT = { has_country_flag = rip_gov_test_fail } }",
        f"\t\tcountry_event = {{ id = {NS}.{back_page} }}",
        "\t}",
        "\toption = {",
        f"\t\tname = {NS}.back_fail",
        "\t\ttrigger = { has_country_flag = rip_gov_test_fail }",
        f"\t\tcountry_event = {{ id = {NS}.{back_page} }}",
        "\t}",
    ]
    if nxt:
        L += ["\toption = {", f"\t\tname = {NS}.next_reform",
              fire_human(ID_APPLY0 + nxt.n), fire_human(ID_POPUP0 + nxt.n), "\t}"]
    if prev:
        L += ["\toption = {", f"\t\tname = {NS}.prev_reform",
              fire_human(ID_APPLY0 + prev.n), fire_human(ID_POPUP0 + prev.n), "\t}"]
    L += ["}", ""]
    return L


def fire_human(eid, depth=2):
    """Fire an event for the human country as it is now.

    A tag change moves the country to a new object; the scope an event was fired for goes stale and
    every effect after the change lands on the dead one (government switches and tag changes do
    nothing, flags and reforms land on a country nobody plays). So whatever may follow a tag change
    is addressed to the human country afresh instead of to ROOT.
    """
    return f"{tabs(depth)}every_country = {{ limit = {{ ai = no }} country_event = {{ id = {NS}.{eid} }} }}"


def run_option(v, name):
    return [
        "\toption = {",
        f"\t\tname = {name}",
        fire_human(ID_APPLY0 + v.n),
        fire_human(ID_POPUP0 + v.n),
        "\t}",
    ]


def goto_option(name, target):
    return ["\toption = {", f"\t\tname = {name}", f"\t\tcountry_event = {{ id = {NS}.{target} }}", "\t}"]


def visible_event(eid):
    return ["country_event = {", f"\tid = {NS}.{eid}", f"\ttitle = {NS}.{eid}.t", f"\tdesc = {NS}.{eid}.d",
            "\tpicture = ADMINISTRATIVE_REFORM_eventPicture", "\tis_triggered_only = yes", ""]


def build(gov, reforms, variants):
    global REFORMS, BASIC
    REFORMS, BASIC = reforms, {gov[g]["basic"] for g in gov}
    N = len(variants)

    # pages: consecutive variants of one group, PAGE_SIZE per page
    groups = []
    for v in variants:
        if not groups or groups[-1]["key"] != v.group_key:
            groups.append({"key": v.group_key, "title": v.group_title, "variants": []})
        groups[-1]["variants"].append(v)
    pages = []
    for gi, grp in enumerate(groups):
        chunks = [grp["variants"][i: i + PAGE_SIZE] for i in range(0, len(grp["variants"]), PAGE_SIZE)]
        for ci, chunk in enumerate(chunks):
            pages.append({"id": ID_PAGE0 + len(pages), "group": gi, "chunk": chunk, "part": ci + 1, "parts": len(chunks)})
        grp["first_page"] = pages[-len(chunks)]["id"]
    if ID_PAGE0 + len(pages) >= ID_RESET:
        raise SystemExit("too many menu pages for the reserved event ids")
    split = 7
    index_pages = {ID_INDEX: groups[:split], ID_INDEX2: groups[split:]}
    index_of_group = {g["key"]: (ID_INDEX if i < split else ID_INDEX2) for i, g in enumerate(groups)}

    ev, loc = [], []
    L = loc.append

    def lk(key, text):
        L(f' {NS}.{key}:0 "{text}"')

    # shared strings of the hidden events
    lk("t", "Government reform test")
    lk("d", "Console-only fixture for a disposable game.")
    lk("a", "Continue")

    # ---- index pages
    for eid, grs in index_pages.items():
        if not grs:
            continue
        ev += visible_event(eid)
        other = ID_INDEX2 if eid == ID_INDEX else ID_INDEX
        for gi, grp in enumerate(grs):
            ev += goto_option(f"{NS}.{eid}.g{gi + 1}", grp["first_page"])
            lk(f"{eid}.g{gi + 1}", f"{grp['title']} ({len(grp['variants'])})")
        if eid == ID_INDEX:
            if index_pages[ID_INDEX2]:
                ev += goto_option(f"{NS}.{eid}.more", ID_INDEX2)
                lk(f"{eid}.more", "More polities")
            ev += ["\toption = {", f"\t\tname = {NS}.{eid}.battery", fire_human(ID_BATTERY),
                   fire_human(ID_BATTERY_DONE), "\t}"]
            lk(f"{eid}.battery", f"Run all {N} reforms and log the result")
            ev += goto_option(f"{NS}.{eid}.clear", ID_CLEAR)
            lk(f"{eid}.clear", "Reset government and test flags")
        else:
            ev += goto_option(f"{NS}.{eid}.back", ID_INDEX)
            lk(f"{eid}.back", "Back to the first list")
        ev += ["}", ""]
        lk(f"{eid}.t", "Government reform test: polities" + (" (1 of 2)" if eid == ID_INDEX else " (2 of 2)"))
        lk(f"{eid}.d", loc_text([
            "Pick a polity, then a reform. The country gets its tag, religion, culture, flags and prerequisite "
            "reforms, and then the reform; the result window says what was given and what could not be.",
            "Console: event rip_gov_test.1",
            f"The battery applies all {N} reform variants one after another and writes RIP_GOV_TEST lines to game.log."]))

    # ---- battery summary
    ev += visible_event(ID_BATTERY_DONE)
    ev += goto_option(f"{NS}.{ID_BATTERY_DONE}.a", ID_INDEX) + ["}", ""]
    lk(f"{ID_BATTERY_DONE}.t", "Government reform battery finished")
    lk(f"{ID_BATTERY_DONE}.d", loc_text([
        f"All {N} variants were applied. Read the RIP_GOV_TEST lines in game.log (logs folder of the user directory):",
        "BEGIN, POT_, TRG_ and HELD_ markers per reform. Run: python tests/dev_tools/make_government_reform_test.py --report <game.log>"]))
    lk(f"{ID_BATTERY_DONE}.a", "Back to the list")

    # ---- group pages
    for pi, page in enumerate(pages):
        grp = groups[page["group"]]
        pid = page["id"]
        ev += visible_event(pid)
        for k, v in enumerate(page["chunk"], 1):
            ev += run_option(v, f"{NS}.{pid}.o{k}")
            lk(f"{pid}.o{k}", f"${v.id}$ - {v.g} {('T' + str(v.tier_idx + 1)) if v.tier else 'basic'}"
                              + (" *" if v.plan.expect_fail else ""))
        if pi > 0:
            ev += goto_option(f"{NS}.{pid}.prev", pages[pi - 1]["id"])
            lk(f"{pid}.prev", "Previous page")
        if pi < len(pages) - 1:
            ev += goto_option(f"{NS}.{pid}.next", pages[pi + 1]["id"])
            lk(f"{pid}.next", "Next page")
        ev += goto_option(f"{NS}.{pid}.idx", index_of_group[grp["key"]])
        lk(f"{pid}.idx", "Polities")
        ev += ["}", ""]
        part = f" ({page['part']} of {page['parts']})" if page["parts"] > 1 else ""
        lk(f"{pid}.t", f"Government reform test: {grp['title']}{part}")
        lk(f"{pid}.d", loc_text(
            [f"{v.id} ({v.g}, " + (f"tier {v.tier_idx + 1}" if v.tier else "basic") + ")"
             + (" *" if v.plan.expect_fail else "") for v in page["chunk"]]
            + ["* some conditions cannot be given by script; the result window says which."]))

    # ---- result windows
    page_of = {v.n: p["id"] for p in pages for v in p["chunk"]}
    for i, v in enumerate(variants):
        ev += popup_event(v, page_of[v.n], variants[i + 1] if i + 1 < N else None, variants[i - 1] if i else None)
        n = ID_POPUP0 + v.n
        lk(f"{n}.t", f"Applied: ${v.id}$")
        lk(f"{n}.d", loc_text(summary_lines(v)))
    for v in variants:
        ev += apply_event(v)
    lk("back_ok", "Back to the list - conditions met, reform held")
    lk("back_fail", "Back to the list - some conditions are not met, see the text")
    lk("next_reform", "Next reform")
    lk("prev_reform", "Previous reform")

    # ---- reset, battery, clear
    all_flags = set()
    for v in variants:
        flags_in(FORMULAS.of_reform(v.id), all_flags)
        all_flags |= v.plan.state.flags | v.plan.state.flags_not
    ev += ["country_event = {", f"\tid = {NS}.{ID_RESET}", f"\ttitle = {NS}.t", f"\tdesc = {NS}.d",
           "\tpicture = ADMINISTRATIVE_REFORM_eventPicture", "\thidden = yes", "\tis_triggered_only = yes",
           f"\toption = {{ name = {NS}.a }}", "\timmediate = {",
           "\t\t# every flag any reform condition reads, so no leftover satisfies or blocks the next test"]
    ev += [f"\t\tclr_country_flag = {f}" for f in sorted(all_flags)]
    ev += ["\t\tclr_country_flag = rip_gov_test_fail", "\t\tclr_country_flag = rip_gov_test_chk_pot",
           "\t\tclr_country_flag = rip_gov_test_chk_trg", "\t}", "}", ""]

    ev += ["country_event = {", f"\tid = {NS}.{ID_BATTERY}", f"\ttitle = {NS}.t", f"\tdesc = {NS}.d",
           "\tpicture = ADMINISTRATIVE_REFORM_eventPicture", "\thidden = yes", "\tis_triggered_only = yes",
           f"\toption = {{ name = {NS}.a }}", "\timmediate = {",
           f'\t\tlog = "RIP_GOV_TEST BATTERY_BEGIN {N}"']
    ev += [fire_human(ID_APPLY0 + v.n) for v in variants]
    ev += [f'\t\tlog = "RIP_GOV_TEST BATTERY_END {N}"', "\t}", "}", ""]

    ev += visible_event(ID_CLEAR)
    ev += ["\toption = {", f"\t\tname = {NS}.{ID_CLEAR}.a", f"\t\tcountry_event = {{ id = {NS}.{ID_RESET} }}",
           "\t\tchange_government = republic", "\t\tchange_government = monarchy",
           f"\t\tcountry_event = {{ id = {NS}.{ID_INDEX} }}", "\t}", "}", ""]
    lk(f"{ID_CLEAR}.t", "Reset government and test flags")
    lk(f"{ID_CLEAR}.d", loc_text(["Clears every flag the reform conditions read and returns to a monarchy with only its basic reform.",
                                  "The tag, religion and culture stay as the last test left them."]))
    lk(f"{ID_CLEAR}.a", "Reset and return to the list")

    header = [
        "# Test fixture: every RIP government reform, one option each, with the conditions it asks for.",
        "# Generated by tests/dev_tools/make_government_reform_test.py; do not edit by hand.",
        "# Not loaded by the game: it lives in tests/dev_tools/, not events/.",
        "#",
        "# To run: python tests/dev_tools/make_government_reform_test.py --install, start a disposable",
        "# non-Ironman game, enter `event rip_gov_test.1` in the console, and pick a polity and a reform.",
        "# Afterwards run --remove. The fixture annexes countries and changes tag, religion and culture.",
        "#",
        "# Each option fires, in order, a hidden apply event (rip_gov_test.1000 + n) and a result window",
        "# (rip_gov_test.2000 + n). The apply event resets the government by switching to another type and",
        "# back, grants the conditions, evaluates the reform's own potential and trigger before adding the",
        "# reform and writes RIP_GOV_TEST markers to game.log:",
        "#   BEGIN / GRANT_FAIL (a planned item is missing; last word says which) / POT_OK|POT_FAIL|POT_NONE /",
        "#   TRG_OK|TRG_FAIL|TRG_NONE / HELD_OK|HELD_FAIL, each followed by <reform> <type>",
        "# `*` in a button marks a reform with a condition script cannot give (the date, an institution",
        "# that is not enabled yet, an age); its POT_FAIL or TRG_FAIL is expected.",
        "# The battery option applies all variants in one go; --report reads the markers.",
        "",
        f"namespace = {NS}",
        "",
    ]
    return "\n".join(header + ev), "﻿" + "l_english:\n" + "\n".join(loc) + "\n", pages, groups


# ---------------------------------------------------------------- report

MARK = re.compile(r"RIP_GOV_TEST (BEGIN|POT_OK|POT_FAIL|POT_NONE|TRG_OK|TRG_FAIL|TRG_NONE|HELD_OK|HELD_FAIL) (\S+) (\S+)")
GRANT = re.compile(r"RIP_GOV_TEST GRANT_FAIL (\S+) (\S+) (\S+)")


def report(variants, log_path):
    text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    got = {}
    for kind, rid, g in MARK.findall(text):
        got.setdefault((rid, g), {})[kind[:3] if kind != "BEGIN" else "BEGIN"] = kind
    missing = {}
    for rid, g, what in GRANT.findall(text):
        missing.setdefault((rid, g), []).append(what)
    rows, problems = [], []
    for v in variants:
        r = got.get((v.id, v.g), {})
        pot, trg, held = r.get("POT", "-"), r.get("TRG", "-"), r.get("HEL", "-")
        verdict = "ok"
        if "BEGIN" not in r:
            verdict = "NOT RUN"
        elif held != "HELD_OK":
            verdict = "expected gap" if v.plan.may_refuse else "REFORM NOT HELD"
        elif (v.id, v.g) in missing:
            verdict = "GRANT FAILED"
        elif pot == "POT_FAIL" or trg == "TRG_FAIL":
            verdict = "expected gap" if v.plan.expect_fail else "UNEXPECTED FAIL"
        if verdict in ("NOT RUN", "REFORM NOT HELD", "GRANT FAILED", "UNEXPECTED FAIL"):
            problems.append(v)
        rows.append((v, pot, trg, held, verdict))
    width = max(len(v.id) for v in variants)
    print(f"{'#':>3} {'reform':<{width}} {'type':<9} {'POT':<9} {'TRG':<9} {'HELD':<9} verdict")
    for v, pot, trg, held, verdict in rows:
        print(f"{v.n:>3} {v.id:<{width}} {v.g:<9} {pot[4:] if pot != '-' else '-':<9} "
              f"{trg[4:] if trg != '-' else '-':<9} {held[5:] if held != '-' else '-':<9} {verdict}")
    counts = Counter(r[4] for r in rows)
    print("\n" + ", ".join(f"{k}: {n}" for k, n in sorted(counts.items())))
    for v in problems:
        why = "; ".join(v.plan.bad) if v.plan.bad else "no known ungrantable condition"
        lost = missing.get((v.id, v.g))
        print(f"PROBLEM {v.id} ({v.g}): " + (f"not in place after the grants: {', '.join(lost)}" if lost else why))
    return 1 if problems else 0


# ---------------------------------------------------------------- main

def generate():
    global FORMULAS
    gov = load_governments()
    reforms = load_reforms()
    FORMULAS = Formulas(reforms, load_scripted_triggers())
    variants = build_variants(gov, reforms, FORMULAS)
    events, loc, pages, groups = build(gov, reforms, variants)
    return gov, reforms, variants, events, loc, pages, groups


def norm(text):
    return text.replace("\r\n", "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 when the committed files are stale")
    ap.add_argument("--install", action="store_true", help="copy the fixture into events/ and localisation/")
    ap.add_argument("--trace", metavar="DIR", help="write a copy with extra TRACE log lines into DIR (the repo files stay as they are)")
    ap.add_argument("--remove", action="store_true", help="delete the installed copies")
    ap.add_argument("--report", metavar="GAME_LOG", nargs="?", const="",
                    help="read RIP_GOV_TEST markers from a game.log (default: the user directory of this mod)")
    args = ap.parse_args()

    if args.remove:
        for path in INSTALLED:
            if path.exists():
                path.unlink()
                print("removed", path.relative_to(ROOT))
        return 0

    if args.trace:
        global TRACE
        TRACE = True
        out_dir = Path(args.trace)
        (out_dir / "events").mkdir(parents=True, exist_ok=True)
        (out_dir / "localisation").mkdir(parents=True, exist_ok=True)
        _, _, _, events, loc, _, _ = generate()
        (out_dir / "events" / EVT_PATH.name).write_text(events, encoding="utf-8", newline="\n")
        (out_dir / "localisation" / LOC_PATH.name).write_text(loc, encoding="utf-8", newline="\n")
        print("traced copy written to", out_dir)
        return 0

    gov, reforms, variants, events, loc, pages, groups = generate()

    if args.report is not None:
        log = Path(args.report) if args.report else ROOT.parents[1] / "logs" / "game.log"
        if not log.exists():
            print(f"no game.log at {log}; pass its path to --report")
            return 1
        return report(variants, log)
    if args.check:
        stale = [p.name for p, text in ((EVT_PATH, events), (LOC_PATH, loc))
                 if not p.exists() or norm(p.read_text(encoding="utf-8")) != norm(text)]
        if stale:
            print("STALE:", ", ".join(stale), "- run python tests/dev_tools/make_government_reform_test.py")
            return 1
        print(f"fresh: {len(variants)} variants")
        return 0

    EVT_PATH.write_text(events, encoding="utf-8", newline="\n")
    LOC_PATH.write_text(loc, encoding="utf-8", newline="\n")
    if args.install:
        INSTALLED[0].write_text(events, encoding="utf-8", newline="\n")
        INSTALLED[1].write_text(loc, encoding="utf-8", newline="\n")
        print("installed into events/ and localisation/; run --remove before packing or committing")

    n_bad = sum(1 for v in variants if v.plan.expect_fail)
    print(f"reforms: {len(reforms)}  variants: {len(variants)}  pages: {len(pages)}  groups: {len(groups)}")
    print(f"types: {dict(Counter(v.g for v in variants))}")
    print(f"variants with a condition script cannot give: {n_bad}")
    for v in variants:
        if v.plan.expect_fail:
            print(f"  {v.id} ({v.g}): " + "; ".join(v.plan.bad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
