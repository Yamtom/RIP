"""Source contracts for Volhynian routes; not an EU4 runtime simulation."""
import re
from clausewitz_testlib import read, named_block, keyed_blocks

FILES = ["Volhynia_Common_Missions", "Volhynia_Conquest_Missions",
         "Volhynia_Missions", "Volhynia_Halych_Legacy_Missions",
         "VOL_VLN_Legacy_Transition"]
trees = {}
missions = {}
for file in FILES:
    source = read(f"missions/{file}.txt")
    for tree in re.findall(r"(?m)^(\w+) = \{", source):
        body = named_block(source, tree)
        slot = int(re.search(r"slot = (\d+)", body)[1])
        ids = re.findall(r"(?m)^\t(\w+) = \{", body)
        trees[tree] = []
        for name in ids:
            if name in {"potential"}:
                continue
            block = named_block(body, name)
            if "icon =" not in block:
                continue
            assert name not in missions, name
            pos = int(re.search(r"position = (\d+)", block)[1])
            deps = re.search(r"required_missions = \{([^}]*)\}", block)[1].split()
            missions[name] = (slot, pos, deps, block)
            trees[tree].append(name)

# Enumerate both VOL paths with both inherited legacies: even old saves with
# both ancestry flags must have unique cells and no absent prerequisites.
common = [t for t in trees if not t.startswith(("VOL_austrian", "VOL_polish"))]
for prefix in ("VOL_austrian", "VOL_polish"):
    selected = {m for t in common + [t for t in trees if t.startswith(prefix)] for m in trees[t]}
    cells = {}
    def visit(name, stack):
        assert name not in stack, f"dependency cycle: {stack + [name]}"
        for dep in missions[name][2]:
            assert dep in selected, f"{name}: missing prerequisite {dep}"
            visit(dep, stack + [name])
    for name in selected:
        slot, pos, _, _ = missions[name]
        assert (slot, pos) not in cells, (name, cells.get((slot, pos)), slot, pos)
        cells[slot, pos] = name
        visit(name, [])

common_source = read("missions/Volhynia_Common_Missions.txt")
assert "change_culture" not in common_source and "change_religion" not in common_source
assert "absolutism =" not in common_source
assert "move_capital_effect" not in common_source
assert "VOL_invest_in_west_rus_mission" not in missions["VOL_choose_development_path"][2]
assert "has_country_modifier" not in named_block(missions["VOL_religious_settlement"][3], "trigger")
assert "has_country_modifier" not in named_block(missions["VOL_education_edict"][3], "trigger")
assert "vol_multicultural_realm" in named_block(missions["VOL_manage_minorities"][3], "effect")
legacy = read("missions/VOL_VLN_Legacy_Transition.txt")
assert "galicia_area" not in legacy
assert "rip_vol_partner_holds_province" in missions["VLN_unite_galicia"][3]
assert "VLN_restore_ruthenia" not in missions["VLN_eastern_partnership_culmination"][2]
forts = missions["hlc_carpathian_bulwark"][3]
for century in (15, 16, 17, 18):
    assert f"fort_{century}th" in forts
events = read("events/RIP_VOL_VOL_path_events.txt")
choice = next(b for _, b in keyed_blocks(events, "country_event")
              if "title = vol_path_events.1.t" in b)
assert choice.count("swap_non_generic_missions = yes") == 2
response = read("events/RIP_VOL_Volhynia_Alt_History.txt")
assert "HLC = { country_event = { id = rip_vol_alt_history.9 } }" in response
assert "who = FROM" in response and "who = ROOT" in response
for lang in ("english", "french", "german", "spanish"):
    path = "localisation/RIP_VOL_realm_l_english.yml" if lang == "english" else f"localisation/replace/RIP_VOL_content_l_{lang}.yml"
    loc = read(path)
    for suffix in ("t", "d", "a", "b"):
        assert f" rip_vol_alt_history.9.{suffix}:" in loc
print(f"PASS: {len(missions)} missions; both VOL branches, combined legacies, dependency graph and political contracts")
