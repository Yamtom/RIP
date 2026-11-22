"""Static contracts for the 22 November 2026 ZAZ and HET mission repairs, as merged with the Rada redesign.

ZAZ: every ambush event belongs to its own city and the Free State has its own event;
the choice of protectors opens without the raid on Constantinople; the Lithuanian
ambush is wired and no longer punishes ROOT; the Turkish "other ally" mission rejects
both Ottoman tags; the Polish branch reaches its conversion event. HET: the Moldavian
line can be won beside a free ally. (The alliance partners, the Polish claims and
Mazepa's course were redesigned on main in the same hours; check_zaz_rada.py and
check_zaz_het_mission_redesign.py hold those.)

Source-contract checks only - this does not launch EU4.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "tests"))

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read  # noqa: E402


def mission(path: str, name: str) -> str:
    return named_block(read(path), name)


def events(path: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for _, block in keyed_blocks(read(path), "country_event"):
        match = re.search(r"\bid\s*=\s*([A-Za-z0-9_.]+)", block)
        if match:
            out[match[1]] = block
    return out


def english_loc() -> dict[str, str]:
    values: dict[str, str] = {}
    for folder in ("localisation", "localisation/replace"):
        for path in sorted((ROOT / folder).glob("*_l_english.yml")):
            for key, value in re.findall(
                r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', path.read_text(encoding="utf-8-sig"), re.M
            ):
                values[key] = value
    return values


def replace_keys(lang: str) -> set[str]:
    keys: set[str] = set()
    for path in sorted((ROOT / "localisation/replace").glob(f"*_l_{lang}.yml")):
        keys |= set(re.findall(r"^ ([A-Za-z0-9_.\-]+):\d*\s+\"", path.read_text(encoding="utf-8-sig"), re.M))
    return keys


def called_events(text: str) -> list[str]:
    return re.findall(r"country_event\s*=\s*\{[^}]*?\bid\s*=\s*([A-Za-z0-9_.]+)", text)


def required(block: str) -> list[str]:
    match = re.search(r"required_missions\s*=\s*\{([^}]*)\}", block)
    return match[1].split() if match else []


ZAZ = "missions/Zaporozhie_Missions.txt"
HET = "missions/zzz_Hetmanate_Missions.txt"


def check_zaz_events_belong_to_their_city() -> None:
    zaz_events = events("events/RIP_ZAZ_ZAZmission.txt")
    loc = english_loc()
    text = read(ZAZ)
    # mission -> (event, province ids the event takes, word its title and text must carry)
    pairs = {
        "ZAZ_lit": ("zaz_flavor_m_1.1", {272, 275, 1936}, "Lithuania"),
        "ZAZ_krakow": ("zaz_flavor_m_2.1", {262}, "Krak"),
        "ZAZ_moskva": ("zaz_flavor_m_2.2", {295}, "Moskva"),
        "ZAZ_saratov": ("zaz_flavor_m_3.2", {303}, "Saratov"),
        "ZAZ_istanbul": ("zaz_flavor_m_3.3", {151}, "Bosporus"),
    }
    for name, (event_id, provinces, word) in pairs.items():
        effect = normalized(named_block(mission(ZAZ, name), "effect"))
        assert called_events(effect) == [event_id], (name, called_events(effect))
        guard = r"(\d+) = \{ if = \{ limit = \{ owner = \{ war_with = ROOT \} \} change_controller = ROOT"
        taken = {int(p) for p in re.findall(guard, normalized(zaz_events[event_id]))}
        assert taken == provinces, (event_id, taken)
        # an ambush occupies a province only while its owner is at war with ROOT
        assert normalized(zaz_events[event_id]).count("change_controller") == len(re.findall(guard, normalized(zaz_events[event_id])))
        assert word in loc[f"{event_id}.t"], (event_id, loc[f"{event_id}.t"])
        assert word in loc[f"{event_id}.d"] or (word == "Bosporus" and "Constantinople" in loc[f"{event_id}.d"]), event_id
        target = re.search(r"province_id = (\d+)", normalized(named_block(mission(ZAZ, name), "provinces_to_highlight")))
        assert target and int(target[1]) in provinces, (name, target and target[1])
    for event_id in (pair[0] for pair in pairs.values()):
        assert len(re.findall(rf"\bid\s*=\s*{re.escape(event_id)}\b", text)) == 1, event_id
    # the Lithuanian ambush may not punish ROOT for provinces ROOT already owns
    lit = normalized(zaz_events["zaz_flavor_m_1.1"])
    # penalties to the owner sit inside the war guard, so ROOT never pays for a province it owns
    assert lit.count("owner = { add_") == 9 and "NOT = { owned_by = ROOT }" not in lit, lit.count("owner = { add_")
    assert "add_years_of_income = 5" not in lit and "add_years_of_income = 2" in lit

    finally_effect = normalized(named_block(mission(ZAZ, "ZAZ_finally"), "effect"))
    assert called_events(finally_effect) == ["zaz_flavor_m_3.1"], finally_effect
    assert "change_controller" not in normalized(zaz_events["zaz_flavor_m_3.1"])
    assert loc["zaz_flavor_m_3.1.t"] == "The Free Zaporozhian State"
    for lang in ("french", "german", "spanish"):
        keys = replace_keys(lang)
        for key in ("zaz_flavor_m_3.1.t", "zaz_flavor_m_3.2.t", "zaz_flavor_m_3.3.t", "zaz_flavor_m_3.3.d"):
            assert key in keys, (lang, key)


def check_zaz_council_without_the_bosphorus() -> None:
    assert required(mission(ZAZ, "ZAZ_finally")) == ["ZAZ_proper"]
    holders = [
        name for name in re.findall(r"(?m)^\t(ZAZ_[A-Za-z0-9_]+) = \{", read(ZAZ))
        if "ZAZ_istanbul" in required(mission(ZAZ, name))
    ]
    assert holders == ["ZAZ_heroic_campaigns"], holders


def check_zaz_turkish_other_ally_and_polish_conversion() -> None:
    different = normalized(named_block(mission(ZAZ, "ZAZ_TUR_different_ally"), "trigger"))
    assert different == "trigger = { any_ally = { NOT = { tag = TUR } NOT = { tag = RUM } } }", different

    second = mission(ZAZ, "ZAZ_POL_politics_2")
    assert "OR = { alliance_with = PLC alliance_with = POL }" in normalized(named_block(second, "trigger"))
    assert called_events(normalized(named_block(second, "effect"))) == ["zaz_flavor_m_5.2"]
    assert "NOT = { religion = catholic }" in normalized(named_block(second, "effect"))

    conversion = events("events/RIP_ZAZ_ZAZmission.txt")["zaz_flavor_m_5.2"]
    options = [normalized(block) for _, block in keyed_blocks(conversion, "option")]
    assert len(options) == 2
    convert, stay = options
    assert "change_religion = catholic" in convert and "factor = 0.1" in convert
    assert "factor = 0.9" in stay


def check_het_moldavian_line() -> None:
    alliance = mission(HET, "het_moldovan_alliance")
    effect = normalized(named_block(alliance, "effect"))
    assert (
        "if = { limit = { NOT = { alliance_with = MOL } NOT = { MOL = { is_subject_of = ROOT } } } "
        "moldavia_area = {" in effect
    ), effect
    assert effect.count("moldavia_area = {") == 1
    assert "wallachia_area = {" in effect

    union = mission(HET, "het_absorb_moldova")
    assert required(union) == ["het_moldovan_alliance"]
    trigger = normalized(named_block(union, "trigger"))
    assert "MOL = { is_subject_of = ROOT }" in trigger
    assert "country_or_non_sovereign_subject_holds = ROOT" in trigger
    free = "AND = { alliance_with = MOL MOL = { is_subject = no } OR = { has_country_flag = het_defended_moldavia has_country_flag = het_moldavia_pressure_held } }"
    assert free in trigger, trigger
    union_effect = normalized(named_block(union, "effect"))
    assert "else_if = { limit = { alliance_with = MOL MOL = { is_subject = no } } add_country_modifier = { name = het_moldovan_sworn_alliance" in union_effect
    assert "het_moldovan_vassalization" in union_effect and "het_moldovan_conquest" in union_effect
    assert "add_claim = ROOT" in union_effect  # Danube expansion stays a full alternative
    assert required(mission(HET, "het_danube_frontier")) == ["het_absorb_moldova"]

    modifiers = read("common/event_modifiers/ruthenian_eastward_modifiers.txt")
    assert len(re.findall(r"(?m)^het_moldovan_sworn_alliance\s*=", modifiers)) == 1
    body = normalized(named_block(modifiers, "het_moldovan_sworn_alliance"))
    for token in ("diplomatic_reputation = 2", "ae_impact = -0.1", "improve_relation_modifier = 0.25", "prestige = 0.25"):
        assert token in body, token

    moldova = events("events/RIP_HET_HetmanateMoldovanExpansion.txt")
    defence = normalized(moldova["het_moldova.7"])
    assert "has_country_flag = het_unlocked_moldovan_path" in defence
    assert "alliance_with = MOL" in defence and "is_in_war = { defenders = MOL }" in defence
    assert "set_country_flag = het_defended_moldavia" in defence
    assert "is_triggered_only" not in defence and "mean_time_to_happen" in defence
    pressure = normalized(moldova["het_moldova.8"])
    assert "alliance_with = MOL" in pressure and "is_great_power = yes" in pressure
    assert "had_country_flag = { flag = het_unlocked_moldovan_path days = 1825 }" in pressure
    assert "set_country_flag = het_moldavia_pressure_held" in pressure
    assert "is_triggered_only" not in pressure and "mean_time_to_happen" in pressure

    loc = english_loc()
    for key in (
        "het_moldova.7.t", "het_moldova.7.d", "het_moldova.7.a", "het_moldova.7.b",
        "het_moldova.8.t", "het_moldova.8.d", "het_moldova.8.a", "het_moldova.8.b",
        "het_moldovan_sworn_alliance", "desc_het_moldovan_sworn_alliance",
        "het_absorb_moldova_title", "het_absorb_moldova_desc", "het_moldovan_alliance_tt",
    ):
        assert key in loc, key
        for lang in ("french", "german", "spanish"):
            assert key in replace_keys(lang), (lang, key)
    assert "free" in loc["het_absorb_moldova_desc"] and "ally" in loc["het_absorb_moldova_desc"]
    assert "!" not in " ".join(v for k, v in loc.items() if k.startswith(("het_moldova.7", "het_moldova.8")))


def modifier_stats(text: str, name: str) -> dict[str, float]:
    body = named_block(text, name)
    return {k: float(v) for k, v in re.findall(r"(?m)^\s*([a-z_]+) = (-?[0-9.]+)\s*$", body)}


def check_reward_ladder() -> None:
    zaz = read("common/event_modifiers/RIP_ZAZ_modifiers.txt")
    east = read("common/event_modifiers/ruthenian_eastward_modifiers.txt")
    assert modifier_stats(zaz, "zaz_army") == {"land_forcelimit_modifier": 0.15}
    assert modifier_stats(zaz, "zaz_turkish_help") == {"discipline": 0.05}
    assert modifier_stats(east, "khmelnitsky_uprising")["war_exhaustion"] == -0.03
    # no reward the missions hand out may still sit at the old 0.66 donor constant
    used = set(re.findall(r"name = \"?([a-z_0-9]+)\"?", read(ZAZ)))
    for name in sorted(used):
        if re.search(rf"(?m)^{re.escape(name)} = \{{", zaz):
            assert 0.66 not in modifier_stats(zaz, name).values(), name
    # the Turkish help lasts 25 years wherever it is paid
    assert not re.search(r"name = zaz_turkish_help\s+duration = 18250", read(ZAZ))
    # capstones: three effects, above the single-stat mid-tier rewards of their trees, permanent
    mission_text = read(ZAZ)
    for modifier, missions in (
        ("zaz_tur_buff", ("ZAZ_GOL_tur_5", "ZAZ_UKR_5", "ZAZ_POL_5")),
        ("zaz_plc_buff", ("ZAZ_GOL_poland", "ZAZ_UKR_poland")),
        ("zaz_russia_buff", ("ZAZ_GOL_russia_3", "ZAZ_UKR_russia_3", "ZAZ_POL_russia_3")),
    ):
        stats = modifier_stats(zaz, modifier)
        assert len(stats) >= 3 and max(stats.values()) >= 0.15, (modifier, stats)
        for mission_name in missions:
            effect = normalized(named_block(mission(ZAZ, mission_name), "effect"))
            assert f"name = {modifier} duration = -1" in effect, (mission_name, modifier)
    assert modifier_stats(zaz, "zaz_tur_buff")["trade_efficiency"] >= modifier_stats(zaz, "zaz_trade_eff")["trade_efficiency"]
    assert mission_text


def check_zaz_copies_are_not_shown_twice() -> None:
    text = read(ZAZ)
    for series, name, twin in (
        ("ZAZ_missions_4_host", "ZAZ_sahaidachnyi_reforms", "het_sahaidachnyi_host"),
        ("ZAZ_missions_5_campaigns", "ZAZ_heroic_campaigns", "het_age_of_heroic_campaigns"),
    ):
        block = named_block(text, series)
        assert normalized(named_block(block, "potential")) == "potential = { tag = ZAZ }", series
        assert name in block and block.count(" = {\n\t\ticon") == 1, series
        assert twin in read(HET)
    # the Hetmanate twins never stack a second permanent buff on a Host that earned the first
    for twin, other, own in (
        ("het_sahaidachnyi_host", "zaz_sahaidachnyi_reforms_modifier", "het_sahaidachnyi_regiments"),
        ("het_age_of_heroic_campaigns", "zaz_heroic_campaigns_modifier", "het_heroic_sea_campaigns"),
    ):
        raw = named_block(mission(HET, twin), "effect")
        # strings are masked by normalized(), so test the guard on the masked text and the name on the raw one
        assert f"limit = {{ NOT = {{ has_country_modifier = {other} }} }} add_country_modifier = {{" in normalized(raw), twin
        guard_at = raw.index(other)
        assert raw.index(own) > guard_at and raw.count(own) == 1, twin
    # no title is shared by a ZAZ mission and a Hetmanate mission
    loc = english_loc()
    zaz_titles = {loc[f"{m}_title"].lower() for m in re.findall(r"(?m)^\t(ZAZ_[A-Za-z0-9_]+) = \{\n\t\ticon", text)}
    het_titles = {loc[f"{m}_title"].lower() for m in re.findall(r"(?m)^\t(het_[A-Za-z0-9_]+) = \{\n\t\ticon", read(HET))}
    # a title may repeat only for the ported pair, whose ZAZ copy is ZAZ-only and so never shown beside it
    zaz_only = {loc[f"{m}_title"].lower() for m in ("ZAZ_sahaidachnyi_reforms", "ZAZ_heroic_campaigns")}
    assert (zaz_titles & het_titles) <= zaz_only, (zaz_titles & het_titles) - zaz_only
    assert loc["ZAZ_lit_title"] == "Lithuanian Campaign"
    for lang in ("french", "german", "spanish"):
        assert "ZAZ_lit_title" in replace_keys(lang)


def check_insult_steps_have_a_fallback() -> None:
    text = read(ZAZ)
    names = re.findall(r"(?m)^\t(ZAZ_[A-Za-z0-9_]+) = \{\n\t\ticon", text)
    checked = 0
    for name in names:
        trigger = normalized(named_block(mission(ZAZ, name), "trigger")) if "trigger" in mission(ZAZ, name) else ""
        tags = re.findall(r"who = ([A-Z]{3}) modifier = insulted", trigger)
        if not tags:
            continue
        checked += 1
        # the target may be gone: a mission gated on an insult must also complete when it is
        if len(tags) == 1:
            assert f"NOT = {{ exists = {tags[0]} }}" in trigger, (name, tags)
        else:
            assert len(tags) == 2, (name, tags)
            assert f"NOT = {{ OR = {{ exists = {tags[0]} exists = {tags[1]} }} }}" in trigger, (name, tags)
    assert checked >= 10, checked
    for name, tag in (("ZAZ_GOL_insult_feo", "FEO"), ("ZAZ_GOL_insult_lit", "LIT"), ("ZAZ_TUR_expand_border", "LIT")):
        trigger = normalized(named_block(mission(ZAZ, name), "trigger"))
        assert f"NOT = {{ exists = {tag} }}" in trigger, name


def check_het_neutral_course_and_legitimacy() -> None:
    gambit = mission(HET, "het_swedish_alliance")
    trigger = normalized(named_block(gambit, "trigger"))
    assert "tooltip = het_mazepa_neutral_course_tt is_subject = no is_at_war = no" in trigger, trigger
    effect = normalized(named_block(gambit, "effect"))
    assert "else_if = { limit = { OR = { has_country_flag = mazepa_remained_loyal is_subject = yes } } set_country_flag = het_loyal_course_completed" in effect
    assert "else = { set_country_flag = het_neutral_course_completed add_country_modifier = { name = het_armed_neutrality" in effect, effect
    modifiers = read("common/event_modifiers/hetmanate_enhanced_modifiers.txt")
    assert len(re.findall(r"(?m)^het_armed_neutrality\s*=", modifiers)) == 1
    loc = english_loc()
    for key in ("het_mazepa_neutral_course_tt", "het_armed_neutrality", "desc_het_armed_neutrality"):
        assert key in loc, key
        for lang in ("french", "german", "spanish"):
            assert key in replace_keys(lang), (lang, key)
    assert "independent" in loc["het_swedish_alliance_desc"]
    # a republic reads its tradition through legitimacy_equivalent, not legitimacy
    het = re.sub(r"legitimacy_equivalent", "", read(HET))
    assert not re.search(r"(?m)^\s*legitimacy = \d", het)
    for mission_name, value in (("het_zaporizhian_liberty", 90), ("het_rozumovsky_reforms", 80)):
        assert f"legitimacy_equivalent = {value}" in normalized(named_block(mission(HET, mission_name), "trigger")), mission_name


CLAIM_ONLY_BLOCKERS = re.compile(
    r"add_(country_modifier|prestige|adm_power|dip_power|mil_power|army_tradition|navy_tradition|years_of_income|"
    r"manpower|base_|building|casus_belli|trade_modifier|province_modifier)|country_event|create_|define_|"
    r"set_country_flag|hidden_effect|change_"
)


def claim_ladders() -> list[list[str]]:
    """Longest chains of missions whose effect does nothing but hand out claims."""
    text = read(ZAZ)
    names = re.findall(r"(?m)^\t(ZAZ_[A-Za-z0-9_]+) = \{\n\t\ticon", text)
    claim_only, children = set(), {}
    for name in names:
        block = mission(ZAZ, name)
        effect = normalized(named_block(block, "effect")) if re.search(r"\n\t\teffect = \{", block) else ""
        if re.search(r"add_(permanent_)?claim", effect) and not CLAIM_ONLY_BLOCKERS.search(effect):
            claim_only.add(name)
        for dep in required(block):
            children.setdefault(dep, []).append(name)
    memo: dict[str, list[str]] = {}

    def longest(name: str) -> list[str]:
        if name not in memo:
            best = [name]
            for child in children.get(name, []):
                if child in claim_only:
                    cand = [name] + longest(child)
                    best = cand if len(cand) > len(best) else best
            memo[name] = best
        return memo[name]

    starts = [n for n in claim_only if not any(d in claim_only for d in required(mission(ZAZ, n)))]
    return sorted((longest(n) for n in starts), key=len, reverse=True)


def check_claim_ladders_are_short() -> None:
    ladders = claim_ladders()
    assert len(ladders[0]) <= 6, ladders[0]
    removed = (
        "ZAZ_UKR_2", "ZAZ_UKR_3", "ZAZ_GOL_tur_2", "ZAZ_GOL_tur_3", "ZAZ_POL_2", "ZAZ_POL_3",
        "ZAZ_POL_west_dniepr", "ZAZ_GOL_west_dniepr", "ZAZ_GOL_malopolska",
    )
    text = read(ZAZ)
    loc = english_loc()
    for name in removed:
        assert not re.search(rf"(?m)^\t{name} = \{{", text), name
        assert not re.search(rf"\b{name}\b", text), name
        assert f"{name}_title" not in loc and f"{name}_desc" not in loc, name
        for lang in ("french", "german", "spanish"):
            assert f"{name}_title" not in replace_keys(lang), (lang, name)
    # the Balkan ladder: Moldavia claims the three Danube areas, they in turn claim Thrace and Tsargrad
    for first, last, capstone in (
        ("ZAZ_UKR", "ZAZ_UKR_4", "ZAZ_UKR_5"),
        ("ZAZ_GOL_tur_1", "ZAZ_GOL_tur_4", "ZAZ_GOL_tur_5"),
        ("ZAZ_POL", "ZAZ_POL_4", "ZAZ_POL_5"),
    ):
        gate = normalized(named_block(mission(ZAZ, first), "effect"))
        for area in ("wallachia_area", "bulgaria_area", "silistria_area"):
            assert f"{area} = {{" in gate and "add_claim = ROOT" in gate, (first, area)
        thrace = mission(ZAZ, last)
        assert required(thrace) == [first], last
        trig = normalized(named_block(thrace, "trigger"))
        for area in ("wallachia_area", "bulgaria_area", "silistria_area"):
            assert f"{area} = {{ type = all owned_by = ROOT }}" in trig, (last, area)
        eff = normalized(named_block(thrace, "effect"))
        assert "149 = {" in eff and "1764 = {" in eff and "151 = {" in eff and "add_permanent_claim = ROOT" in eff, last
        assert required(mission(ZAZ, capstone)) == [last], capstone
    pol_gate = mission(ZAZ, "ZAZ_POL")
    assert required(pol_gate) == ["ZAZ_POL_settle_north", "ZAZ_POL_cordon"]
    assert "west_dniepr_area = { type = all owned_by = ROOT }" in normalized(named_block(pol_gate, "trigger"))
    assert "minsk_area" in normalized(named_block(pol_gate, "effect"))
    weste = mission(ZAZ, "ZAZ_GOL_weste")
    assert required(weste) == ["ZAZ_GOL_cordon", "ZAZ_GOL_east_dniepr"]
    assert "west_dniepr_area = { type = all owned_by = ROOT }" in normalized(named_block(weste, "trigger"))
    assert "minsk_area" in normalized(named_block(weste, "effect"))
    assert "wielkopolska_area" in normalized(named_block(mission(ZAZ, "ZAZ_GOL_red_ruthenia"), "effect"))
    assert required(mission(ZAZ, "ZAZ_GOL_poland")) == ["ZAZ_GOL_red_ruthenia"]
    for key in ("ZAZ_UKR_desc", "ZAZ_UKR_4_desc", "ZAZ_GOL_weste_desc", "ZAZ_POL_desc"):
        assert "Silistria" in loc[key] or "Minsk" in loc[key], key


CAPSTONES = (
    "ZAZ_GOL_tur_5", "ZAZ_UKR_5", "ZAZ_POL_5", "ZAZ_GOL_poland", "ZAZ_UKR_poland",
    "ZAZ_GOL_russia_3", "ZAZ_UKR_russia_3", "ZAZ_POL_russia_3", "ZAZ_GOL_tribes_4",
)


def check_capstones_pay_the_full_package() -> None:
    zaz = read("common/event_modifiers/RIP_ZAZ_modifiers.txt")
    for name in CAPSTONES:
        effect = normalized(named_block(mission(ZAZ, name), "effect"))
        for token in ("add_prestige = 50", "add_adm_power = 100", "add_dip_power = 100", "add_mil_power = 100", "duration = -1"):
            assert token in effect, (name, token)
    caucasus = normalized(named_block(mission(ZAZ, "ZAZ_GOL_tribes_4"), "effect"))
    assert "name = zaz_caucasus_buff" in caucasus and "add_dip_power = 200" not in caucasus
    stats = modifier_stats(zaz, "zaz_caucasus_buff")
    assert len(stats) == 3 and stats["manpower_recovery_speed"] == 0.15, stats
    loc = english_loc()
    for key in ("zaz_caucasus_buff", "desc_zaz_caucasus_buff"):
        assert key in loc, key
        for lang in ("french", "german", "spanish"):
            assert key in replace_keys(lang), (lang, key)


def main() -> int:
    check_zaz_events_belong_to_their_city()
    check_zaz_council_without_the_bosphorus()
    check_zaz_turkish_other_ally_and_polish_conversion()
    check_het_moldavian_line()
    check_reward_ladder()
    check_zaz_copies_are_not_shown_twice()
    check_insult_steps_have_a_fallback()
    check_het_neutral_course_and_legitimacy()
    check_claim_ladders_are_short()
    check_capstones_pay_the_full_package()
    print(
        "HET/ZAZ MISSION FIXES PASS: five ambush events fire from their own city and only occupy while at "
        "war, the council needs ZAZ_proper only, the Turkish other-ally mission rejects TUR and RUM, the "
        "Polish branch reaches its conversion event, the Moldavian Union accepts a defended or pressured "
        "free ally, rewards sit on one ladder with permanent three-effect capstones, the ZAZ copies of the "
        "two ported missions are ZAZ-only, every insult-gated step has a 'target is gone' fallback, and "
        "an independent Hetmanate has an armed-neutrality course, the longest pure claim ladder is six missions "
        "and the three Balkan ladders are two, and all nine capstones pay one full package (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
