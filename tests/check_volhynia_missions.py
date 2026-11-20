"""Source and EU4 layout contracts for Volhynian/Halych/VLN routes; not an EU4 runtime simulation."""
from collections import defaultdict
import re
from clausewitz_testlib import read, named_block, keyed_blocks, vanilla_root

# Exact EU4 alphabetical load order for this mission cluster.
FILES = [
    "Volhynia_Common_Missions",
    "Volhynia_Conquest_Missions",
    "Volhynia_Missions",
    "zzz_VOL_VLN_Legacy_Transition",
    "zzz_Volhynia_Halych_Legacy_Missions",
]
assert FILES == sorted(FILES, key=str.lower), "FILES must reflect EU4 alphabetical load order"

trees = {}
tree_meta = {}
missions = {}
ordered_trees = []
for file in FILES:
    source = read(f"missions/{file}.txt")
    for tree in re.findall(r"(?m)^(\w+) = \{", source):
        body = named_block(source, tree)
        slot = int(re.search(r"slot = (\d+)", body)[1])
        pot = re.sub(r"\s+", " ", named_block(body, "potential")).strip()
        ids = re.findall(r"(?m)^\t(\w+) = \{", body)
        trees[tree] = []
        tree_meta[tree] = (file, slot, pot, body)
        ordered_trees.append(tree)
        for name in ids:
            if name in {"potential"}:
                continue
            block = named_block(body, name)
            if "icon =" not in block:
                continue
            assert name not in missions, name
            pos = int(re.search(r"position = (\d+)", block)[1])
            deps = re.search(r"required_missions = \{([^}]*)\}", block)[1].split()
            missions[name] = (slot, pos, deps, block, tree)
            trees[tree].append(name)


def check_eu4_layout(label, active_trees, *, allow_legacy_shift=False, max_allowed_row=None):
    """Simulate EU4 sequential per-slot series stacking and validate arrows and compactness."""
    active_set = set(active_trees)
    slot_cursor = defaultdict(int)
    placed = {}
    grid = {}
    for tree in ordered_trees:
        if tree not in active_set:
            continue
        file, slot, _, _ = tree_meta[tree]
        prev_in_series = 0
        for name in trees[tree]:
            _, declared_pos, deps, _, _ = missions[name]
            assert declared_pos > prev_in_series, f"{label}: {tree} non-ascending {name} p{declared_pos}"
            prev_in_series = declared_pos
            cur = slot_cursor[slot] + 1
            actual = max(cur, declared_pos)
            if not allow_legacy_shift or not file.startswith("zzz_"):
                assert actual == declared_pos, (
                    f"{label}: {file}::{tree}::{name} declared p{declared_pos} shifted to p{actual}"
                )
            slot_cursor[slot] = actual
            assert (slot, actual) not in grid, f"{label}: collision at s{slot}p{actual}"
            grid[(slot, actual)] = name
            placed[name] = (slot, actual, deps)

    max_row = max(p for _, p in grid)
    if max_allowed_row is not None:
        assert max_row <= max_allowed_row, f"{label}: max_row {max_row} > {max_allowed_row}"
    for row in range(1, max_row + 1):
        assert any((s, row) in grid for s in range(1, 6)), f"{label}: empty row p{row}"

    def visit(name, stack):
        assert name not in stack, f"{label}: dependency cycle {stack + [name]}"
        for dep in placed[name][2]:
            assert dep in placed, f"{label}: {name} missing prerequisite {dep}"
            visit(dep, stack + [name])

    for name, (s, p, deps) in placed.items():
        visit(name, [])
        for dep in deps:
            rs, rp, _ = placed[dep]
            assert p > rp, f"{label}: non-downward arrow {dep}(s{rs}p{rp}) -> {name}(s{s}p{p})"
            if rs != s:
                assert p - rp == 1, (
                    f"{label}: dangling cross-column arrow {dep}(s{rs}p{rp}) -> {name}(s{s}p{p})"
                )
            elif p - rp > 1:
                blockers = [grid[(s, y)] for y in range(rp + 1, p) if (s, y) in grid]
                assert not blockers, f"{label}: blocked vertical {dep} -> {name} by {blockers}"


def select(pred):
    return [t for t in ordered_trees if pred(*tree_meta[t][:3])]


# 1. HLC standalone (must have zero empty rows, compact height, and both Halych shields).
check_eu4_layout(
    "HLC",
    select(lambda f, s, p: any(k in p for k in (
        "west_ukraine_shared_starter", "west_ukraine_hlc_vol_starter", "west_ukraine_hlc_legacy_missions"
    ))),
    max_allowed_row=8,
)
assert "has_country_shield = yes" in tree_meta["VOL_missions_HLC"][3]
assert "has_country_shield = yes" in tree_meta["VOL_missions_4_HLC"][3]

# 2. VLN standalone (both with HLC alive and with HLC gone).
check_eu4_layout(
    "VLN_with_HLC",
    select(lambda f, s, p: any(k in p for k in ("west_ukraine_vln_alt_paths", "west_ukraine_vln_legacy_missions"))),
    max_allowed_row=4,
)
check_eu4_layout(
    "VLN_no_HLC",
    select(lambda f, s, p: any(k in p for k in (
        "west_ukraine_shared_starter", "west_ukraine_vln_alt_paths", "west_ukraine_vln_legacy_missions"
    ))),
    allow_legacy_shift=True,
    max_allowed_row=8,
)

# 3. VOL plain, from HLC, from VLN, and combined old-save legacies on both branches.
for branch, excl in (("austrian", "constitutional"), ("constitutional", "austrian")):
    vol_core = lambda f, s, p, ex=excl: (
        any(k in p for k in ("west_ukraine_shared_starter", "west_ukraine_hlc_vol_starter"))
        or ("tag = VOL" in p and ex not in p)
    )
    check_eu4_layout(f"VOL_plain_{branch}", select(vol_core), max_allowed_row=14)
    check_eu4_layout(
        f"VOL_from_HLC_{branch}",
        select(lambda f, s, p: vol_core(f, s, p) or "west_ukraine_hlc_legacy_missions" in p),
        allow_legacy_shift=True,
        max_allowed_row=17,
    )
    check_eu4_layout(
        f"VOL_from_VLN_{branch}",
        select(lambda f, s, p: vol_core(f, s, p) or "west_ukraine_vln_" in p),
        allow_legacy_shift=True,
        max_allowed_row=18,
    )
    check_eu4_layout(
        f"VOL_both_legacies_{branch}",
        select(lambda f, s, p: vol_core(f, s, p) or "west_ukraine_hlc_legacy_missions" in p or "west_ukraine_vln_" in p),
        allow_legacy_shift=True,
        max_allowed_row=22,
    )

# 4. UKR inheritance: retained Halych/VLN missions must not depend on absent VOL_unite_galicia.
assert missions["hlc_halych_sejm_mission"][2] == []
assert missions["hlc_carpathian_bulwark"][2] == []

# 5. Political and historical contracts.
common_source = read("missions/Volhynia_Common_Missions.txt")
assert "change_culture" not in common_source and "change_religion" not in common_source
assert "absolutism =" not in common_source
assert "move_capital_effect" not in common_source
assert "VOL_invest_in_west_rus_mission" not in missions["VOL_choose_development_path"][2]
assert "mission_completed = VOL_renaissance_mission" in named_block(missions["VOL_choose_development_path"][3], "trigger")
assert "has_country_modifier" not in named_block(missions["VOL_religious_settlement"][3], "trigger")
assert "has_country_modifier" not in named_block(missions["VOL_education_edict"][3], "trigger")
assert "vol_multicultural_realm" in named_block(missions["VOL_manage_minorities"][3], "effect")
legacy = read("missions/zzz_VOL_VLN_Legacy_Transition.txt")
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

# 6. Mission titles must fit EU4's 2-line mission scroll banner (vic_18, maxWidth 90).
vanilla = vanilla_root()
if vanilla and (vanilla / "gfx/fonts/vic_18.fnt").is_file():
    fnt = (vanilla / "gfx/fonts/vic_18.fnt").read_text(encoding="latin-1")
    adv = {int(m.group(1)): int(m.group(2)) for m in re.finditer(r"char\s+id=(\d+).*?xadvance=(-?\d+)", fnt)}
    sp = adv.get(32, 4)

    def wrap_metrics(title: str, max_w: int) -> tuple[int, int]:
        lines_w: list[int] = []
        cur_w = 0
        for word in title.split(" "):
            ww = sum(adv.get(ord(ch), 7) for ch in word)
            if cur_w == 0:
                cur_w = ww
            elif cur_w + sp + ww <= max_w:
                cur_w += sp + ww
            else:
                lines_w.append(cur_w)
                cur_w = ww
        if cur_w:
            lines_w.append(cur_w)
        return len(lines_w), max(lines_w or [0])

    en_titles: dict[str, str] = {}
    for loc_file in ("RIP_VOL_realm_l_english.yml", "RIP_VLN_realm_l_english.yml", "RIP_HLC_realm_l_english.yml"):
        for k, v in re.findall(r'^ ([A-Za-z0-9_.\-]+_title):\d+\s+"(.*)"\s*$', read(f"localisation/{loc_file}"), re.M):
            en_titles[k] = v
    for mname in missions:
        title = en_titles[f"{mname}_title"]
        assert title == title.strip() and "\\n" not in title, (mname, title)
        n84, w84 = wrap_metrics(title, 84)
        n90, w90 = wrap_metrics(title, 90)
        assert n84 <= 2 and n90 <= 2 and w84 <= 84 and w90 <= 90, (mname, title, n84, w84, n90, w90)

print(f"PASS: {len(missions)} missions; HLC, VLN, both VOL branches, combined legacies, EU4 slot stacking, arrow geometry, 2-line titles and political contracts")
