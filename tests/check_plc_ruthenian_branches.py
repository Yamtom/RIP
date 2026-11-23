"""Nine Ruthenian branches of the Commonwealth (PLC): events, decisions, disaster, modifiers, texts.

Source files
  events/RIP_shared_commonwealth_RuthenianBranches.txt   24 events in nine namespaces
  decisions/RIP_PLC_RuthenianDecisions.txt                3 decisions
  common/disasters/plc_disasters.txt                      the Confederation of Bar
  common/event_modifiers/RIP_PLC_ruthenian_modifiers.txt  15 modifiers
  common/scripted_triggers/rip_plc_ruthenian_triggers.txt the Ruthenian and Left Bank gates
  localisation/RIP_shared_commonwealth_affairs_l_english.yml and
  localisation/replace/RIP_shared_commonwealth_content_l_{french,german,spanish}.yml

What it proves, statically
  - every branch has its events, its decisions and its disaster, and nothing else in these files;
  - dated events sit in their documented windows, are gated on tag = PLC and on Ruthenian lands;
  - every triggered-only event has a caller, every flag read is set, every modifier added is
    defined and described, province modifiers carry only local_ keys and country ones none;
  - every key the script reads exists in English and in the three replace/ files;
  - no else_if, no add_opinion and no calc_true_if (three traps measured in this mod).
Nothing here runs the game; the numbers in the options are not balance-tested.
"""
from __future__ import annotations

import re
import sys

from check_vanilla_mission_sync import dump, parse
from clausewitz_testlib import read

EVENTS = "events/RIP_shared_commonwealth_RuthenianBranches.txt"
DECISIONS = "decisions/RIP_PLC_RuthenianDecisions.txt"
DISASTERS = "common/disasters/plc_disasters.txt"
MODIFIERS = "common/event_modifiers/RIP_PLC_ruthenian_modifiers.txt"
TRIGGERS = "common/scripted_triggers/rip_plc_ruthenian_triggers.txt"
LOC = {
    "english": "localisation/RIP_shared_commonwealth_affairs_l_english.yml",
    "french": "localisation/replace/RIP_shared_commonwealth_content_l_french.yml",
    "german": "localisation/replace/RIP_shared_commonwealth_content_l_german.yml",
    "spanish": "localisation/replace/RIP_shared_commonwealth_content_l_spanish.yml",
}

# branch -> (events, dated windows {event: (first year, year it stops)}, decisions, disaster)
BRANCHES = {
    "plc_hierarchy": ([1, 2, 3], {1: (1620, 1632), 2: (1632, 1641)}, [], None),
    "plc_zadnieprze": ([1, 2], {1: (1620, 1648)}, ["plc_charter_left_bank_town"], None),
    "plc_chancery": ([1, 2], {1: (1588, 1602), 2: (1690, 1710)}, ["plc_recognise_ruthenian_chancery"], None),
    "plc_princes": ([1, 2, 3], {1: (1590, 1632), 3: (1636, 1649)}, [], None),
    "plc_flight": ([1, 2, 3], {1: (1590, 1648)}, [], None),
    "plc_buchach": ([1, 2, 3], {1: (1672, 1674), 3: (1699, 1706)}, [], None),
    "plc_eternal_peace": ([1, 2], {}, ["plc_eternal_peace_with_moscow"], None),
    "plc_bar": ([1, 2, 3], {1: (1766, 1769)}, [], "plc_confederation_of_bar"),
    "plc_patrons": ([1, 2, 3], {1: (1615, 1626), 2: (1590, 1640), 3: (1632, 1651)}, [], None),
}
ANCHOR = re.compile(r"rip_plc_holds_|rip_plc_ruthenian|rip_plc_left_bank|\b280\b|\b281\b|ruthenia_region|red_ruthenia_area")
SCRIPT_FILES = (EVENTS, DECISIONS, DISASTERS)


def values(items, key):
    return [value for k, value in items if k == key]


def event_table(text):
    table = {}
    for key, body in parse(text):
        if key == "country_event":
            ident = values(body, "id")[0]
            table.setdefault(ident, []).append(body)
    return table


def loc_keys(text):
    return set(re.findall(r'(?m)^ ([A-Za-z0-9_.\-]+):\d* "', text))


def problems(src):
    out = []
    events = event_table(src[EVENTS])
    decisions = {k: v for k, v in parse(src[DECISIONS])[0][1]} if parse(src[DECISIONS]) else {}
    disasters = {k: v for k, v in parse(src[DISASTERS])}
    modifiers = {k: dump(v) for k, v in parse(src[MODIFIERS])}
    all_script = "\n".join(src[f] for f in SCRIPT_FILES)

    # --- shape and inventory
    expected_ids = {f"{ns}.{n}" for ns, (nums, *_rest) in BRANCHES.items() for n in nums}
    if set(events) != expected_ids:
        out.append(f"event ids differ: missing {sorted(expected_ids - set(events))}, extra {sorted(set(events) - expected_ids)}")
    for ident, copies in events.items():
        if len(copies) != 1:
            out.append(f"{ident}: defined {len(copies)} times")
    if set(decisions) != {d for *_a, ds, _x in BRANCHES.values() for d in ds}:
        out.append(f"decisions differ: {sorted(decisions)}")
    if set(disasters) != {x for *_a, x in BRANCHES.values() if x}:
        out.append(f"disasters differ: {sorted(disasters)}")
    if not re.search(r"Authenticity: [AB]", src[EVENTS]) or "# Sources:" not in src[EVENTS]:
        out.append("events file lost its Authenticity / Sources header")

    # --- events
    # A call is a country_event nested in an option, an immediate block or a decision effect; the
    # definitions themselves also read "country_event = { id = ...", so they must not count.
    call_text = " ".join(
        dump(block) for copies in events.values() for key in ("option", "immediate") for block in values(copies[0], key)
    ) + " ".join(dump(values(body, "effect")[0]) for body in decisions.values() if values(body, "effect"))
    calls = set(re.findall(r"country_event = \{ id = (plc_\w+\.\d+)", call_text))
    calls |= set(re.findall(r"on_(?:start|end) = (plc_\w+\.\d+)", dump(parse(src[DISASTERS]))))
    for ident, copies in events.items():
        body = copies[0]
        for key in ("title", "desc", "picture"):
            if not values(body, key):
                out.append(f"{ident}: no {key}")
        if not values(body, "option"):
            out.append(f"{ident}: no option")
        triggered = values(body, "is_triggered_only") == ["yes"]
        trigger = dump(values(body, "trigger")[0]) if values(body, "trigger") else ""
        if triggered and ident not in calls:
            out.append(f"{ident}: triggered only, but nothing calls it")
        if not triggered:
            if not values(body, "mean_time_to_happen"):
                out.append(f"{ident}: dated event without mean_time_to_happen")
            if not re.search(r"(?<!\w)tag = PLC\b", trigger):
                out.append(f"{ident}: not gated on tag = PLC")
            if not ANCHOR.search(trigger):
                out.append(f"{ident}: no Ruthenian land or culture gate")
        ns, num = ident.rsplit(".", 1)
        window = BRANCHES.get(ns, (0, {}, 0, 0))[1].get(int(num))
        if window and not triggered:
            first = re.search(r"(?<!\w)is_year = (\d+)", trigger)
            last = re.search(r"NOT = \{ is_year = (\d+) \}", trigger)
            if not first or not last or (int(first.group(1)), int(last.group(1))) != window:
                out.append(f"{ident}: window is not {window}")
        if window and triggered:
            out.append(f"{ident}: has a window but is triggered only")
        if not window and not triggered and BRANCHES.get(ns, (0, {}, 0, 0))[1]:
            if int(num) in BRANCHES[ns][0] and int(num) not in BRANCHES[ns][1]:
                out.append(f"{ident}: dated event missing from the window table")

    # --- branch-level anchors
    for ns, (nums, _windows, decision_names, disaster) in BRANCHES.items():
        pieces = [dump(events[f"{ns}.{n}"][0]) for n in nums if f"{ns}.{n}" in events]
        pieces += [dump(decisions[d]) for d in decision_names if d in decisions]
        if disaster and disaster in disasters:
            pieces.append(dump(disasters[disaster]))
        if not any(ANCHOR.search(p) for p in pieces):
            out.append(f"{ns}: nothing in the branch is tied to Ruthenian land")
    for name, body in decisions.items():
        potential = dump(values(body, "potential")[0]) if values(body, "potential") else ""
        if not re.search(r"(?<!\w)tag = PLC\b", potential):
            out.append(f"{name}: potential lacks tag = PLC")
        if not values(body, "allow") or not values(body, "effect") or not values(body, "ai_will_do"):
            out.append(f"{name}: missing allow, effect or ai_will_do")
    for name, body in disasters.items():
        for key in ("potential", "can_start", "can_end", "progress", "modifier", "on_start", "on_end"):
            if not values(body, key):
                out.append(f"{name}: no {key}")
        if not re.search(r"(?<!\w)tag = PLC\b", dump(values(body, "potential")[0]) if values(body, "potential") else ""):
            out.append(f"{name}: potential lacks tag = PLC")
        for ref in values(body, "on_start") + values(body, "on_end"):
            if ref not in events:
                out.append(f"{name}: {ref} is not an event")

    # --- flags
    set_flags = set(re.findall(r"set_country_flag = (\w+)", all_script))
    for flag in sorted(set(re.findall(r"has_country_flag = (\w+)", all_script)) - set_flags):
        out.append(f"flag {flag} is read but never set")

    # --- modifiers
    used = {"country": set(), "province": set()}
    for kind, scope in (("add_country_modifier", "country"), ("add_province_modifier", "province")):
        for found in re.findall(kind + r" = \{ name = (\w+)", dump(parse(all_script))):
            used[scope].add(found)
    for scope, names in used.items():
        for name in sorted(names):
            if name not in modifiers:
                out.append(f"{name}: used as a {scope} modifier but not defined")
                continue
            keys = re.findall(r"(\w+) = [-\d.]+", modifiers[name])
            local = [k for k in keys if k.startswith("local_")]
            if scope == "province" and len(local) != len(keys):
                out.append(f"{name}: province modifier with a country key")
            if scope == "country" and local:
                out.append(f"{name}: country modifier with a local key")
    for name in sorted(set(modifiers) - used["country"] - used["province"]):
        out.append(f"{name}: defined but never added")

    # --- traps
    for needle in ("else_if", "add_opinion", "calc_true_if"):
        if needle in all_script:
            out.append(f"{needle} is used in the Ruthenian branches")

    # --- localisation, all four languages
    wanted = set()
    for ident, copies in events.items():
        wanted |= {f"{ident}.t", f"{ident}.d"}
        wanted |= {f"{ident}.{letter}" for letter in "abcd"[: len(values(copies[0], "option"))]}
    for name in list(decisions) + list(disasters):
        wanted |= {f"{name}_title", f"{name}_desc"}
    for name in modifiers:
        wanted |= {name, f"desc_{name}"}
    for language, path in LOC.items():
        missing = wanted - loc_keys(src[path])
        for key in sorted(missing):
            out.append(f"{language}: missing {key}")
    option_names = set(re.findall(r"name = (plc_\w+\.\d+\.[a-d])\b", all_script))
    if option_names - wanted:
        out.append(f"option names without text: {sorted(option_names - wanted)}")
    return out


def self_test(src):
    """Return the planted violations the check failed to flag."""
    missed = []

    def mutate(label, path, old, new, count=1):
        text = src[path]
        assert old in text, f"mutation {label!r}: {old!r} not found in {path}"
        damaged = dict(src)
        damaged[path] = text.replace(old, new, count)
        if not problems(damaged):
            missed.append(label)

    mutate("event without a caller", EVENTS, "id = plc_hierarchy.3\n\t\t\tdays = 90", "id = plc_hierarchy.9\n\t\t\tdays = 90")
    mutate("dated window widened", EVENTS, "NOT = { is_year = 1649 }", "NOT = { is_year = 1700 }")
    mutate("event leaves PLC", EVENTS, "tag = PLC\n\t\tis_year = 1620", "tag = POL\n\t\tis_year = 1620")
    mutate("Ruthenian gate removed", EVENTS, "rip_plc_holds_orthodox_ruthenia = yes\n\t\tNOT = { has_country_flag = plc_hierarchy_settled }", "always = yes\n\t\tNOT = { has_country_flag = plc_hierarchy_settled }")
    mutate("flag renamed in the disaster", DISASTERS, "has_country_flag = plc_dissidents_refused", "has_country_flag = plc_dissidents_defied")
    mutate("modifier definition removed", MODIFIERS, "rip_plc_free_years = {", "rip_plc_free_years_x = {")
    mutate("province modifier takes a country key", MODIFIERS, "local_manpower_modifier = 0.25\n\tlocal_development_cost", "global_manpower_modifier = 0.25\n\tlocal_development_cost")
    mutate("french text missing", LOC["french"], " plc_bar.2.t:0", " plc_bar.2.t_x:0")
    mutate("german option text missing", LOC["german"], " plc_flight.1.c:0", " plc_flight.1.c_x:0")
    mutate("modifier description missing", LOC["english"], " desc_rip_plc_kyiv_collegium:0", " desc_rip_plc_kyiv_collegium_x:0")
    mutate("decision text missing", LOC["spanish"], " plc_eternal_peace_with_moscow_title:0", " plc_eternal_peace_with_moscow_title_x:0")
    mutate("else_if introduced", EVENTS, "add_stability = -1\n\t\tadd_country_modifier = {\n\t\t\tname = rip_plc_hierarchy_proscribed", "else_if = { limit = { always = yes } add_stability = -1 }\n\t\tadd_country_modifier = {\n\t\t\tname = rip_plc_hierarchy_proscribed")
    mutate("decision loses tag = PLC", DECISIONS, "tag = PLC\n\t\t\trip_plc_holds_left_bank = yes", "rip_plc_holds_left_bank = yes")
    mutate("disaster loses its end event", DISASTERS, "on_end = plc_bar.3", "on_end = plc_bar.9")
    mutate("header dropped", EVENTS, "# Authenticity:", "# Rating:")
    return missed


def main():
    paths = [EVENTS, DECISIONS, DISASTERS, MODIFIERS, TRIGGERS] + list(LOC.values())
    src = {path: read(path) for path in paths}
    failures = problems(src)
    failures += [f"self-test: planted violation not caught: {label}" for label in self_test(src)]
    for name in ("rip_plc_ruthenian_province", "rip_plc_ruthenian_orthodox_province", "rip_plc_left_bank_province",
                 "rip_plc_holds_ruthenian_lands", "rip_plc_holds_orthodox_ruthenia", "rip_plc_holds_left_bank"):
        if not re.search(rf"(?m)^{name} = \{{", src[TRIGGERS]):
            failures.append(f"scripted trigger {name} missing")
    if failures:
        print("PLC RUTHENIAN BRANCHES FAILED:")
        for item in failures:
            print(" ", item)
        return 1
    events = event_table(src[EVENTS])
    print(f"PLC RUTHENIAN BRANCHES PASS: 9 branches, {len(events)} events, 3 decisions, 1 disaster, "
          f"15 modifiers, texts in 4 languages; 15 planted violations caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
