"""Lithuania's two reckonings: the Kyiv appanage (1470-1481) and the Volok survey (1557-1588).

Wiring contract for events/RIP_LIT_Reckoning.txt, decisions/RIP_LIT_Reckoning.txt,
common/disasters/rip_lit_reckoning_disasters.txt, common/event_modifiers/RIP_LIT_reckoning_modifiers.txt,
interface/RIP_shared_disaster_lit_reckoning.gfx, localisation/RIP_LIT_reckoning_l_*.yml and the two missions
rip_lit_kyiv_succession / rip_lit_volok_survey (both DLC variants) in zzzzz_Neighbor_Ruthenian_Missions.txt.

Pins: every event id is wired (a mission, an option, or a disaster calls it), every flag that is read is set
somewhere, every modifier is defined and has text, each disaster starts only after the harsher choice and has its
icon, both decisions need the disaster to be over, all text exists in four languages and keeps the house rules.
Static only; nothing here runs EU4. Historical claims and sources: docs/LIT_RECKONING_20261124.uk.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz_testlib import ROOT, read, vanilla_root  # noqa: E402

EVENTS = "events/RIP_LIT_Reckoning.txt"
DECISIONS = "decisions/RIP_LIT_Reckoning.txt"
DISASTERS = "common/disasters/rip_lit_reckoning_disasters.txt"
MODIFIERS = "common/event_modifiers/RIP_LIT_reckoning_modifiers.txt"
GFX = "interface/RIP_shared_disaster_lit_reckoning.gfx"
MISSIONS = "missions/zzzzz_Neighbor_Ruthenian_Missions.txt"
LANGUAGES = ("english", "french", "german", "spanish")
EVENT_IDS = [1, 2, 3, 4, 5, 11, 12, 13, 14, 15]
DISASTER_IDS = ("rip_lit_ruthenian_princes_revolt", "rip_lit_peasant_flight")
DECISION_IDS = ("rip_lit_rehabilitate_olelkovych", "rip_lit_open_frontier_register")
MISSION_IDS = {"rip_lit_kyiv_succession": 1, "rip_lit_volok_survey": 11}
PICTURES = {"COURT_eventPicture", "CORRUPTION_eventPicture", "DIPLOMACY_eventPicture", "BATTLE_eventPicture",
            "FARMING_eventPicture", "ANGRY_MOB_eventPicture"}
FORBIDDEN = ("identity", "democracy", "democratic", "ethnic", "ideology", "!")


def loc(language: str) -> dict[str, str]:
    return dict(re.findall(r'(?m)^ ([A-Za-z0-9_.]+):\d* "(.*)"\s*$', read(f"localisation/RIP_LIT_reckoning_l_{language}.yml")))


def events_of(text: str) -> dict[int, str]:
    out = {}
    for match in re.finditer(r"(?m)^country_event = \{\n(.*?)^\}\n", text, re.S):
        body = match.group(1)
        out[int(re.search(r"id = rip_lit_reckoning\.(\d+)", body)[1])] = body
    return out


def problems_of(events: str, decisions: str, disasters: str, modifiers: str, gfx: str, missions: str) -> list[str]:
    problems = []
    by_id = events_of(events)
    if sorted(by_id) != EVENT_IDS:
        problems.append(f"events {sorted(by_id)}, expected {EVENT_IDS}")
    keys_needed = set()
    called = set()
    for event_id, body in by_id.items():
        base = f"rip_lit_reckoning.{event_id}"
        for part, key in (("title", f"{base}.t"), ("desc", f"{base}.d")):
            if f"{part} = {key}\n" not in body:
                problems.append(f"{base}: {part} must be {key}")
            keys_needed.add(key)
        if "is_triggered_only = yes" not in body:
            problems.append(f"{base}: not is_triggered_only")
        picture = re.search(r"picture = (\w+)", body)
        if not picture or picture[1] not in PICTURES:
            problems.append(f"{base}: picture {picture and picture[1]}")
        options = re.findall(r"name = (rip_lit_reckoning\.\d+\.\w)", body)
        if not options:
            problems.append(f"{base}: no option")
        keys_needed.update(options)
        called.update(int(n) for n in re.findall(r"id = rip_lit_reckoning\.(\d+)", body) if int(n) != event_id)
    # who opens each event: a mission, an option of another event, or a disaster
    openers = missions + disasters
    called.update(int(n) for n in re.findall(r"rip_lit_reckoning\.(\d+)", openers))
    for event_id in by_id:
        if event_id not in called:
            problems.append(f"rip_lit_reckoning.{event_id}: nothing opens it")
    # flags
    read_flags = set(re.findall(r"has_country_flag = (\w+)", events + decisions + disasters))
    set_flags = set(re.findall(r"set_country_flag = (\w+)", events + decisions))
    for flag in sorted(read_flags - set_flags):
        problems.append(f"flag {flag} is read but never set")
    # modifiers
    used = set(re.findall(r"name = (rip_lit_\w+)\n", events + decisions)) | set(
        re.findall(r"(?:remove_country_modifier|remove_province_modifier|has_country_modifier) = (rip_lit_\w+)", events + decisions + disasters))
    defined = set(re.findall(r"(?m)^(rip_lit_\w+) = \{", modifiers))
    for name in sorted(used - defined):
        problems.append(f"modifier {name} used but not defined")
    for name in sorted(defined - used):
        problems.append(f"modifier {name} defined but never used")
    for name in defined:
        keys_needed.update((name, f"desc_{name}"))
    # disasters
    for disaster in DISASTER_IDS:
        block = re.search(rf"(?ms)^{disaster} = \{{\n(.*?)^\}}\n", disasters)
        if not block:
            problems.append(f"disaster {disaster} missing")
            continue
        body = block.group(1)
        if "tag = LIT" not in body or "has_country_flag" not in body.split("can_start")[0]:
            problems.append(f"{disaster}: must be gated by tag = LIT and by the flag of its harsher choice")
        for hook in ("on_start", "on_end"):
            if not re.search(rf"{hook} = rip_lit_reckoning\.\d+", body):
                problems.append(f"{disaster}: no {hook} event")
        if "on_monthly" not in body:
            problems.append(f"{disaster}: no monthly event")
        if f'name = "GFX_disaster_{disaster}"' not in gfx:
            problems.append(f"{disaster}: no icon sprite")
        keys_needed.update((disaster, f"{disaster}_title", f"{disaster}_desc", f"desc_{disaster}"))
    # decisions
    for decision in DECISION_IDS:
        block = re.search(rf"(?ms)^\t{decision} = \{{\n(.*?)^\t\}}\n", decisions)
        if not block:
            problems.append(f"decision {decision} missing")
            continue
        if "tag = LIT" not in block.group(1) or "NOT = { has_disaster =" not in block.group(1):
            problems.append(f"{decision}: needs tag = LIT and the disaster to be over")
        keys_needed.update((f"{decision}_title", f"{decision}_desc"))
    # missions: both variants open the same event
    for mission, event_id in MISSION_IDS.items():
        for key in (mission, mission + "_classic"):
            block = re.search(rf"(?ms)^\t{key} = \{{\n(.*?)^\t\}}\n", missions)
            if not block:
                problems.append(f"mission {key} missing")
            elif f"country_event = {{ id = rip_lit_reckoning.{event_id} }}" not in block.group(1):
                problems.append(f"{key}: must open rip_lit_reckoning.{event_id}")
        keys_needed.update((f"{mission}_title", f"{mission}_desc"))
    # text
    for language in LANGUAGES:
        entries = loc(language)
        for key in sorted(keys_needed):
            if not entries.get(key):
                problems.append(f"{language}: missing text {key}")
        for key, value in entries.items():
            if any(word in value.lower() for word in FORBIDDEN):
                problems.append(f"{language}: {key} breaks the house style")
    return problems


def texture_problems(gfx: str) -> list[str]:
    root = vanilla_root()
    if root is None:
        return []
    return [f"texture {name} missing in the install" for name in re.findall(r'texturefile = "(.*?)"', gfx)
            if not (root / name.replace("//", "/")).exists()]


def main() -> int:
    inputs = [read(p) for p in (EVENTS, DECISIONS, DISASTERS, MODIFIERS, GFX, MISSIONS)]
    problems = problems_of(*inputs) + texture_problems(inputs[4])

    def planted(label: str, index: int, old: str, new: str) -> None:
        damaged = list(inputs)
        if old not in damaged[index]:
            problems.append(f"self-test setup: {old!r} not found for {label}")
            return
        damaged[index] = damaged[index].replace(old, new, 1)
        if not problems_of(*damaged):
            problems.append(f"self-test: not caught: {label}")

    planted("a flag that is read and never set", 0, "set_country_flag = rip_lit_princes_executed", "set_country_flag = rip_lit_other")
    planted("an event nothing opens", 2, "on_end = rip_lit_reckoning.15", "on_end = rip_lit_reckoning.14")
    planted("a disaster without its icon", 4, "GFX_disaster_rip_lit_peasant_flight", "GFX_disaster_other")
    planted("a modifier that is not defined", 3, "rip_lit_capped_dues = {", "rip_lit_capped_dues_x = {")
    planted("a mission that opens the wrong event", 5, "id = rip_lit_reckoning.11", "id = rip_lit_reckoning.12")
    planted("a decision open during the disaster", 1, "NOT = { has_disaster = rip_lit_peasant_flight }", "always = yes")
    if problems:
        print("LIT RECKONING FAILED:")
        for item in problems:
            print(" ", item)
        return 1
    print(f"LIT RECKONING PASS: {len(EVENT_IDS)} events, {len(DISASTER_IDS)} disasters, {len(DECISION_IDS)} decisions, "
          f"{len(MISSION_IDS)} missions in both DLC variants, modifiers and text in four languages; 6 planted breaks caught")
    return 0


if __name__ == "__main__":
    sys.exit(main())
