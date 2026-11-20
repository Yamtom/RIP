"""Source and EU4 layout contracts for Volhynian/Halych/VLN routes; not an EU4 runtime simulation."""
from collections import defaultdict
import re
from clausewitz_testlib import read, named_block, keyed_blocks, normalized, vanilla_root

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
old_capital_trigger = normalized(named_block(missions["VOL_old_capital"][3], "trigger"))
assert "280 = { owned_by = ROOT is_capital = yes }" in old_capital_trigger
assert "country_or_non_sovereign_subject_holds" not in old_capital_trigger
army = named_block(common_source, "VOL_full_army")
assert "add_building = fort_16th" not in army
assert "add_building = fort_15th" in army
assert "name = fortress_modifier" in army
assert "cossack_cavalry" not in named_block(common_source, "VOL_king_power")
minorities = missions["VOL_manage_minorities"][3]
assert "embraced_minority_religion" not in minorities
assert "name = vol_minority_rights" in minorities
assert "1952" not in missions["VOL_land_collector"][3]
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
fort_counter = named_block(named_block(forts, "trigger"), "num_of_owned_provinces_with")
fort_highlight = named_block(forts, "provinces_to_highlight")
frontier = {"261", "2424", "4541"}
assert set(re.findall(r"province_id\s*=\s*(\d+)", fort_counter)) == frontier
assert set(re.findall(r"province_id\s*=\s*(\d+)", fort_highlight)) == frontier
assert "value = 3" in fort_counter and "controlled_by = ROOT" in fort_counter
assert "area =" not in fort_counter, "Inland forts must not satisfy the Carpathian frontier"
assert "VOL_conquer_malopolska" not in missions["hlc_halych_sejm_mission"][3]
assert missions["hlc_confessional_compact"][2] == ["hlc_carpathian_bulwark"]
assert missions["hlc_constitutional_settlement"][2] == ["hlc_confessional_compact"]
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

# 5b. Volhynian restoration country modifier, sane global autonomy, and marketplace pacing.
vln_restore_eff = normalized(named_block(missions["VLN_restore_ruthenia"][3], "effect"))
assert "name = rip_vol_restored_ruthenia_country" in vln_restore_eff
assert "name = restored_ruthenia" not in vln_restore_eff

vol_unity_mod = normalized(named_block(read("common/event_modifiers/RIP_VOL_modifiers.txt"), "VOL_unity"))
assert "global_autonomy = -0.05" in vol_unity_mod
assert "global_autonomy = -1" not in vol_unity_mod

chumak_trig = normalized(named_block(missions["VOL_expand_Chumatsky_Way_mission"][3], "trigger"))
assert "has_building = marketplace" in chumak_trig
west_rus_trig = normalized(named_block(missions["VOL_invest_in_west_rus_mission"][3], "trigger"))
assert west_rus_trig.count("has_building = marketplace") == 4

# 5c. VOL claim chain completeness, VOL_old_capital heir/highlight guards, and early VOL_border_control balance.
unite_eff = normalized(named_block(missions["VOL_unite_galicia"][3], "effect"))
assert "malopolska_area" in unite_eff and "sandomierz_area" in unite_eff

malopolska_eff = normalized(named_block(missions["VOL_conquer_malopolska"][3], "effect"))
assert "white_ruthenia_area" in malopolska_eff and "podlasie_area" in malopolska_eff

west_dniepr_eff = normalized(named_block(missions["VOL_conquer_west_dniepr"][3], "effect"))
assert "east_dniepr_area" in west_dniepr_eff and "zaporizhia_area" in west_dniepr_eff
assert "yedisan_area" not in west_dniepr_eff

moldavia_eff = normalized(named_block(missions["VOL_conquer_moldavia"][3], "effect"))
assert "yedisan_area" in moldavia_eff

east_dniepr_eff = normalized(named_block(missions["VOL_conquer_east_dniepr"][3], "effect"))
assert "chernigov_area" in east_dniepr_eff and "sloboda_ukraine_area" in east_dniepr_eff

chernihiv_eff = normalized(named_block(missions["volhynia_conquer_chernihiv"][3], "effect"))
assert "smolensk_area" in chernihiv_eff and "sloboda_ukraine_area" not in chernihiv_eff

sloboda_eff = normalized(named_block(missions["VOL_conquer_sloboda"][3], "effect"))
assert "2409" not in sloboda_eff

demolish_mos_eff = normalized(named_block(missions["VOL_demolish_MOS"][3], "effect"))
for area in ("pskov_area", "novgorod_area", "tver_area"):
    assert area in demolish_mos_eff

old_cap_eff = normalized(named_block(missions["VOL_old_capital"][3], "effect"))
assert "has_heir = yes" in old_cap_eff and "change_heir_adm = 2" in old_cap_eff
assert "else = { add_adm_power = 75 add_dip_power = 75 add_mil_power = 75 }" in old_cap_eff

vol_stab_eff = normalized(named_block(missions["VOL_stability"][3], "effect"))
assert "duration = 3650" in vol_stab_eff and "duration = 3654" not in vol_stab_eff

border_mod = normalized(named_block(read("common/event_modifiers/RIP_VOL_modifiers.txt"), "VOL_border_control"))
assert "land_morale = 0.1" in border_mod
assert "land_morale = 0.2" not in border_mod

# 5d. Symmetric HLC/VLN partner hold in VOL_unite_galicia, VOL_full_army barracks, shared Ostroh slot 4, and imperial path balance.
unite_gal_trig = normalized(named_block(missions["VOL_unite_galicia"][3], "trigger"))
assert unite_gal_trig.count("rip_vol_partner_holds_province = yes") == 3
partner_trig = normalized(read("common/scripted_triggers/rip_vol_mission_triggers.txt"))
assert "tag = HLC" in partner_trig and "alliance_with = VLN" in partner_trig

full_army_eff = normalized(named_block(missions["VOL_full_army"][3], "effect"))
assert "NOT = { has_building = barracks } NOT = { has_building = training_fields }" in full_army_eff
assert "add_building = barracks" in full_army_eff

assert "tag = VOL" in tree_meta["VOL_ostroh_learning_slot4"][2]
assert "west_ukraine_constitutional_path" not in tree_meta["VOL_ostroh_learning_slot4"][2]
assert (
    missions["VOL_church_relations"][1],
    missions["VOL_university_expansion"][1],
    missions["VOL_renaissance_court"][1],
    missions["VOL_education_edict"][1],
) == (10, 11, 12, 13)

vol_mods = read("common/event_modifiers/VOL_mission_modifiers.txt")
imp_triumph = normalized(named_block(vol_mods, "vol_imperial_triumph"))
assert "diplomatic_annexation_cost = -0.2" in imp_triumph and "ae_impact = -0.15" in imp_triumph and "discipline = 0.05" in imp_triumph
cult_tol = normalized(named_block(vol_mods, "vol_cultural_tolerance"))
assert "governing_capacity_modifier = 0.15" in cult_tol
diplo_asc = normalized(named_block(vol_mods, "vol_diplomatic_ascendancy"))
assert "ae_impact = -0.1" in diplo_asc and "diplomatic_annexation_cost = -0.15" in diplo_asc

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
