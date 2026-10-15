"""Regenerate tests/dev_tools/RIP_GovernmentReformTest.txt and its loc from common/governments and common/government_reforms.

Run from anywhere: python tests/dev_tools/make_government_reform_test.py. Re-run after any change to reform tiers or triggers.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))

from clausewitz_testlib import keyed_blocks, matching_brace, named_block, _mask_comments_and_strings  # noqa: E402

NS = "rip_gov_test"
PAGE_SIZE = 7
TYPE_ORDER = ["monarchy", "republic", "theocracy", "tribal", "native"]
EVT_PATH = ROOT / "tests/dev_tools/RIP_GovernmentReformTest.txt"
LOC_PATH = ROOT / "tests/dev_tools/rip_gov_test_l_english.yml"

# ---------------------------------------------------------------- governments
gov_text = (ROOT / "common/governments/00_governments.txt").read_text(encoding="utf-8-sig")
gov = {}
for g in TYPE_ORDER:
    block = named_block(gov_text, g)
    basic = re.search(r"(?m)^\s*basic_reform\s*=\s*([A-Za-z0-9_]+)", block).group(1)
    levels = named_block(block, "reform_levels")
    tiers = []
    for m in re.finditer(r"(?m)^\t\t([A-Za-z0-9_]+)\s*=\s*\{", levels):
        opening = levels.find("{", m.start())
        closing = levels.find("}", opening)  # tier blocks hold one flat reforms = { } list
        inner = levels[m.start(): closing + 1]
        ids_match = re.search(r"reforms\s*=\s*\{([^}]*)\}", inner)
        if ids_match:
            tiers.append((m.group(1), ids_match.group(1).split()))
    exclusives = []
    for _, blk in keyed_blocks(block, "exclusive_reforms"):
        masked = _mask_comments_and_strings(blk)
        inner = masked[masked.find("{") + 1: masked.rfind("}")]
        exclusives.append(inner.split())
    gov[g] = {"basic": basic, "tiers": tiers, "exclusives": exclusives}

# ---------------------------------------------------------------- reforms
reform_dir = ROOT / "common/government_reforms"
reform_text = {}
for path in sorted(reform_dir.glob("*.txt")):
    text = path.read_text(encoding="utf-8-sig")
    masked = _mask_comments_and_strings(text)
    for m in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", masked):
        opening = text.find("{", m.start())
        closing = matching_brace(text, opening)
        reform_text[m.group(1)] = text[m.start(): closing + 1]
RIP = set(reform_text)

TOKEN = re.compile(r'#[^\n]*|"[^"\n]*"|\{|\}|=|[^\s{}=#"]+')


def parse(text):
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
            elif pos + 1 < len(toks) and toks[pos + 1] == "=":
                key, val = t, toks[pos + 2]
                if val == "{":
                    pos += 3
                    out.append((key, block()))
                    pos += 1
                else:
                    out.append((key, val))
                    pos += 3
            else:
                out.append(("__bare__", t))
                pos += 1
        return out

    return block()


def named_child(items, key):
    for k, v in items:
        if k == key and isinstance(v, list):
            return v
    return []


def analyse(items, ctx, acc):
    """ctx: root (conjunctive), NOT, OR (alternatives), AMBIG (unclear polarity)."""
    for key, val in items:
        if key in ("__bare__", "tooltip"):
            continue
        if isinstance(val, list):
            if key in ("AND", "__block__", "custom_trigger_tooltip"):
                analyse(val, ctx, acc)
            elif key == "NOT":
                analyse(val, {"root": "NOT", "NOT": "root", "OR": "AMBIG", "AMBIG": "AMBIG"}[ctx], acc)
            elif key == "OR":
                analyse(val, {"root": "OR", "OR": "OR", "NOT": "AMBIG", "AMBIG": "AMBIG"}[ctx], acc)
            else:
                acc["unmet"].add(key)
            continue
        if key == "has_reform":
            acc[{"root": "pos", "NOT": "neg", "OR": "alt", "AMBIG": "alt"}[ctx]].add(val)
        elif key == "has_country_flag":
            if ctx == "root":
                acc["flag_pos"].add(val)
            elif ctx == "NOT":
                acc["flag_neg"].add(val)
            else:
                acc["unmet"].add(key)
        else:
            acc["unmet"].add(key)


def describe(items):
    parts = []
    for k, v in items:
        if k in ("__bare__", "tooltip"):
            continue
        if isinstance(v, list):
            inner = describe(v)
            parts.append(inner if k == "custom_trigger_tooltip" else f"{k}[{inner}]")
        else:
            parts.append(f"{k} {v}")
    text = ", ".join(p for p in parts if p)
    return text if len(text) <= 180 else text[:177] + "..."


def analyse_reform(rid):
    """Acquisition path of a reform: the trigger's conjunctive items plus, for each
    top-level OR, its first arm that is not the reform itself.

    A trigger shaped like OR { has_reform = self  AND { prerequisites } } keeps the
    reform valid once held (the self arm) and lists the way to get it (the AND arm).
    Other arms are counted in alt_other and not granted.
    """
    items = parse(reform_text[rid])[0][1]  # the top-level item is the reform block itself
    trig = named_child(items, "trigger")
    acc = {"pos": set(), "neg": set(), "alt": set(), "flag_pos": set(), "flag_neg": set(),
           "unmet": set(), "path": [], "alt_other": 0}
    for key, val in trig:
        if key == "OR" and isinstance(val, list):
            arms = [(k, v) for k, v in val if k != "__bare__" and not (k == "has_reform" and v == rid)]
            if not arms:
                continue
            first_key, first_val = arms[0]
            acc["alt_other"] += len(arms) - 1
            if first_key == "has_reform":
                acc["pos"].add(first_val)
                acc["path"].append(f"has_reform {first_val}")
            else:
                analyse([(first_key, first_val)], "root", acc)
                acc["path"].append(describe([(first_key, first_val)]))
        else:
            analyse([(key, val)], "root", acc)
    acc["pos"].discard(rid)
    acc["neg"].discard(rid)
    return acc


info = {rid: analyse_reform(rid) for rid in RIP}

# ---------------------------------------------------------------- closure of positive prerequisites
def closure(rid):
    seen, stack = set(), list(info[rid]["pos"])
    while stack:
        p = stack.pop()
        if p in seen or p == rid:
            continue
        seen.add(p)
        if p in info:
            stack.extend(info[p]["pos"])
    return seen


# ---------------------------------------------------------------- variants
basic_ids = {gov[g]["basic"] for g in gov}
variants = []
for rid in sorted(RIP):
    if rid in basic_ids:
        g = next(gg for gg in gov if gov[gg]["basic"] == rid)
        variants.append({"id": rid, "g": g, "t": None, "tier_idx": -1})
        continue
    memberships = []
    for g in TYPE_ORDER:
        for idx, (tname, ids) in enumerate(gov[g]["tiers"]):
            if rid in ids:
                memberships.append((g, tname, idx))
    if not memberships:
        raise SystemExit(f"reform {rid} is in no tier and is not a basic reform")
    for g, tname, idx in memberships:
        variants.append({"id": rid, "g": g, "t": tname, "tier_idx": idx})

for v in variants:
    rid, g, t = v["id"], v["g"], v["t"]
    a = info.get(rid, {"pos": set(), "neg": set(), "alt": set(), "flag_pos": set(), "flag_neg": set(), "unmet": set()})
    prereqs = set()
    if rid in info:
        prereqs = closure(rid)
    v["prereqs"] = sorted(prereqs)
    v["neg"] = sorted(a["neg"] - prereqs)
    v["flag_pos"] = sorted(a["flag_pos"])
    v["flag_neg"] = sorted(a["flag_neg"])
    v["path"] = " + ".join(a["path"]) if a["path"] else "none (no conjunctive prerequisites)"
    v["alt_other"] = a["alt_other"]
    v["unmet"] = sorted(a["unmet"])
    tier_mates = []
    if t:
        tier_mates = [x for x in dict(gov[g]["tiers"])[t] if x in RIP and x != rid]
    excl = []
    for block in gov[g]["exclusives"]:
        if rid in block:
            excl.extend(x for x in block if x in RIP and x != rid)
    clear = (set(tier_mates) | set(excl) | set(v["neg"])) - set(prereqs) - {rid}
    v["clear"] = sorted(clear)

order = {g: i for i, g in enumerate(TYPE_ORDER)}
variants.sort(key=lambda v: (order[v["g"]], v["tier_idx"], v["id"]))

pages = [variants[i: i + PAGE_SIZE] for i in range(0, len(variants), PAGE_SIZE)]
N = len(pages)
ALL_FLAGS = sorted({f for v in variants for f in v["flag_pos"] + v["flag_neg"]})
ALL_CLEARABLE = sorted(x for x in RIP if x not in basic_ids)


def tabs(n):
    return "\t" * n


def apply_option(v, page, k):
    rid, g, t = v["id"], v["g"], v["t"]
    lines = []
    lines.append(f"{tabs(2)}option = {{")
    lines.append(f"{tabs(3)}name = {NS}.{page}.o{k}")
    lines.append(f"{tabs(3)}# {rid} | {g} | {t or 'basic'}")
    lines.append(f"{tabs(3)}# not granted by effect (fixture cannot set it): "
                 f"{', '.join(v['unmet']) if v['unmet'] else 'none'}")
    other = f"; other arms not granted: {v['alt_other']}" if v["alt_other"] else ""
    lines.append(f"{tabs(3)}# acquisition path: {v['path']}{other}")
    lines.append(f"{tabs(3)}if = {{ limit = {{ NOT = {{ government = {g} }} }} change_government = {g} }}")
    if v["id"] in basic_ids:
        lines.append(f"{tabs(3)}log = \"RIP_GOV_TEST APPLY {rid} {g} basic\"")
        lines.append(f"{tabs(3)}country_event = {{ id = {NS}.{page} }}")
        lines.append(f"{tabs(2)}}}")
        return lines
    for x in v["clear"]:
        lines.append(f"{tabs(3)}if = {{ limit = {{ has_reform = {x} }} remove_government_reform = {x} }}")
    for x in v["flag_neg"]:
        lines.append(f"{tabs(3)}clr_country_flag = {x}")
    for p in v["prereqs"]:
        lines.append(f"{tabs(3)}if = {{ limit = {{ NOT = {{ has_reform = {p} }} }} add_government_reform = {p} }}")
    for f in v["flag_pos"]:
        lines.append(f"{tabs(3)}set_country_flag = {f}")
    lines.append(f"{tabs(3)}if = {{ limit = {{ NOT = {{ has_reform = {rid} }} }} add_government_reform = {rid} }}")
    lines.append(f"{tabs(3)}log = \"RIP_GOV_TEST APPLY {rid} {g} {t}\"")
    lines.append(f"{tabs(3)}country_event = {{ id = {NS}.{page} }}")
    lines.append(f"{tabs(2)}}}")
    return lines


def page_event(p_idx):
    page = p_idx + 1
    chunk = pages[p_idx]
    out = [
        "country_event = {",
        f"\tid = {NS}.{page}",
        f"\ttitle = {NS}.{page}.t",
        f"\tdesc = {NS}.{page}.d",
        "\tpicture = ADMINISTRATIVE_REFORM_eventPicture",
        "\tis_triggered_only = yes",
        "",
    ]
    for k, v in enumerate(chunk, 1):
        # apply_option is written one level deeper than the event body; dedent by one tab
        out.extend(line[1:] for line in apply_option(v, page, k))
    if page > 1:
        out += [
            "\toption = {",
            f"\t\tname = {NS}.{page}.prev",
            f"\t\tcountry_event = {{ id = {NS}.{page - 1} }}",
            "\t}",
        ]
    if page < N:
        out += [
            "\toption = {",
            f"\t\tname = {NS}.{page}.next",
            f"\t\tcountry_event = {{ id = {NS}.{page + 1} }}",
            "\t}",
        ]
    out += [
        "\toption = {",
        f"\t\tname = {NS}.{page}.clr",
        f"\t\tcountry_event = {{ id = {NS}.99 }}",
        "\t}",
        "}",
        "",
    ]
    return out


def clear_event():
    out = [
        "country_event = {",
        f"\tid = {NS}.99",
        f"\ttitle = {NS}.99.t",
        f"\tdesc = {NS}.99.d",
        "\tpicture = ADMINISTRATIVE_REFORM_eventPicture",
        "\tis_triggered_only = yes",
        "",
        "\toption = {",
        f"\t\tname = {NS}.99.a",
    ]
    for x in ALL_CLEARABLE:
        out.append(f"\t\tif = {{ limit = {{ has_reform = {x} }} remove_government_reform = {x} }}")
    for f in ALL_FLAGS:
        out.append(f"\t\tclr_country_flag = {f}")
    out += [
        f"\t\tcountry_event = {{ id = {NS}.1 }}",
        "\t}",
        "}",
        "",
    ]
    return out


header = [
    "# Test fixture: one option per RIP government reform, plus one option per",
    "# government type for reforms listed in two types (for example",
    "# chr_grain_directorate_reform or uzh_palanok_captaincy_reform). Not loaded by",
    "# the game: it lives in tests/dev_tools/, not events/.",
    "#",
    "# To run: copy this file and rip_gov_test_l_english.yml into events/ and",
    "# localisation/ of a disposable (isolated) profile, start a game, and enter",
    f"# `event {NS}.1` in the console. Then page with the Next / Previous options.",
    "#",
    "# Each option switches government type if needed, removes the RIP reforms",
    "# in the same tier and exclusive sets (kept: its own prerequisites), grants",
    "# the positive has_reform prerequisites (closed transitively), sets the",
    "# positive has_country_flag gates, and then grants the reform itself with",
    "# add_government_reform, which ignores the reform's trigger and potential.",
    "# Tag, culture, scripted visibility and other conditions are not granted; the",
    "# comment line under each option names them. Reforms of other tiers are not",
    "# cleared, so use the Clear option (event 99) between tests.",
    "# Markers go to game.log as RIP_GOV_TEST APPLY <reform> <type> <tier>.",
    "",
    f"namespace = {NS}",
    "",
]

body = []
for p in range(N):
    body += page_event(p)
body += clear_event()

EVT_PATH.write_text("\n".join(header + body), encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- loc
loc = [f" {NS}.99.t:0 \"Clear test reforms\"",
       f" {NS}.99.d:0 \"Removes every RIP government reform and test flag, then returns to page 1.\"",
       f" {NS}.99.a:0 \"Clear and return to page 1\""]
for p_idx, chunk in enumerate(pages):
    page = p_idx + 1
    loc.append(f" {NS}.{page}.t:0 \"Government reform test: page {page} of {N}\"")
    desc_lines = [f"{v['id']} ({v['g']} / {v['t'] or 'basic'})" for v in chunk]
    loc.append(f" {NS}.{page}.d:0 \"" + "\\n".join(desc_lines) + "\"")
    for k, v in enumerate(chunk, 1):
        loc.append(f" {NS}.{page}.o{k}:0 \"${v['id']}$ / {v['g']} / {v['t'] or 'basic'}\"")
    if page > 1:
        loc.append(f" {NS}.{page}.prev:0 \"Previous page\"")
    if page < N:
        loc.append(f" {NS}.{page}.next:0 \"Next page\"")
    loc.append(f" {NS}.{page}.clr:0 \"Clear test reforms\"")

LOC_PATH.write_text("﻿" + "l_english:\n" + "\n".join(loc) + "\n", encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- report
print("variants:", len(variants), "pages:", N, "reforms:", len(RIP))
print("variants with prerequisites:", sum(1 for v in variants if v["prereqs"]))
print("variants with flags:", sum(1 for v in variants if v["flag_pos"]))
print("variants with other OR arms not granted:", sum(1 for v in variants if v["alt_other"]))
print("paths with no conjunctive prerequisites:", [(v["id"], v["g"]) for v in variants if v["path"].startswith("none")])
print("variants with negated has_reform cleared:", [(v["id"], v["neg"]) for v in variants if v["neg"]])
print("types:", {g: sum(1 for v in variants if v["g"] == g) for g in TYPE_ORDER})
print("ALL_FLAGS:", ALL_FLAGS)
print("unmet keys (count):")
from collections import Counter  # noqa: E402
cnt = Counter(k for v in variants for k in v["unmet"])
print(cnt.most_common())
