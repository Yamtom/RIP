"""Static regression gate for selective donor-mission ports across all 5 country groups.

Verifies (static inspection only — does not launch EU4):
1. All 33 ported missions exist in their expected files, slots 1..5, and declared rows < 24.
2. EU4 sequential per-slot stacking has zero collisions and strictly downward newly added arrows
   for KUY, KIE, UKR/KRU, CHR (diplomatic & militarized), PRL, HET standalone, HET from PRL,
   and HET from ZAZ (all 5 diplomatic branches).
3. KIE_missions_5 no longer has a duplicate position = 4 collision.
4. Do-not-copy donor defects stay excluded (no Kryvbas iron on 283, no "Korsun" on 2410,
   no change_trade_goods = unknown in chr_tmutarakan_inheritance, EU4 spelling `manuever`,
   explicit Rivne 2962 map-abstraction note for Ostroh).
5. All ported English localisation keys fit <= 2 lines in vanilla vic_18.fnt (when installed),
   match French/German/Spanish replace fallbacks, and never overlap RIP_shared_ruthenian_legacy_missions.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

from clausewitz_testlib import ROOT, named_block, read, vanilla_root

EXPECTED_PORTS: dict[str, tuple[str, ...]] = {
    "missions/Zakarpatta_Missions.txt": (
        "uzh_beskid_vistula_passes",
        "uzh_carpathian_magdeburg_charters",
    ),
    "missions/Volhynia_Heritage_Missions.txt": ("hlc_lviv_magdeburg_charters",),
    "missions/zzz_VOL_VLN_Legacy_Transition.txt": ("VLN_ostrozkyi_patrons",),
    "missions/Volhynia_Missions.txt": ("VOL_vistula_marches",),
    "missions/Podillia_Missions.txt": (
        "PDL_dniester_granaries",
        "PDL_kamianets_magdeburg_charters",
    ),
    "missions/Kyiv_Successors_Missions.txt": (
        "UKR_lithuanian_inheritance",
        "UKR_swedish_question",
        "UKR_ruthenian_empire",
        "UKR_breadbasket_of_europe",
        "KIE_mohyla_academy",
        "KIE_ruthenian_baroque",
        "KIE_second_jerusalem",
    ),
    "missions/Kuyaba_Missions.txt": (
        "KUY_magdeburg_guilds",
        "KUY_granary_of_steppe",
        "KUY_dnieper_crossings",
        "KUY_steppe_caravans",
        "KUY_restore_kuyaba",
        "KUY_crimean_gates",
        "KUY_sultanate_of_rus",
        "KUY_black_sea_fleet",
        "KUY_bosporus_straits",
    ),
    "missions/Chernihiv_Missions.txt": (
        "chr_siversk_sloboda_frontier",
        "chr_tmutarakan_inheritance",
    ),
    "missions/Pereiaslav_Missions.txt": (
        "prl_magdeburg_charter",
        "prl_dnieper_baroque",
        "prl_sloboda_regiments",
    ),
    "missions/Zaporozhie_Missions.txt": (
        "ZAZ_sahaidachnyi_reforms",
        "ZAZ_heroic_campaigns",
    ),
    "missions/zzz_Hetmanate_Missions.txt": (
        "het_sahaidachnyi_host",
        "het_age_of_heroic_campaigns",
        "het_black_sea_armada",
    ),
}

PORTED_LOC_FILES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "UZH": (
        "localisation/RIP_UZH_realm_l_english.yml",
        "localisation/replace/RIP_UZH_content_l_{lang}.yml",
        (
            "uzh_beskid_vistula_passes_title",
            "uzh_beskid_vistula_passes_desc",
            "uzh_carpathian_magdeburg_charters_title",
            "uzh_carpathian_magdeburg_charters_desc",
            "uz_beskid_vistula_corridor",
            "desc_uz_beskid_vistula_corridor",
            "uz_carpathian_town_charters",
            "desc_uz_carpathian_town_charters",
        ),
    ),
    "HLC": (
        "localisation/RIP_HLC_realm_l_english.yml",
        "localisation/replace/RIP_HLC_content_l_{lang}.yml",
        (
            "hlc_lviv_magdeburg_charters_title",
            "hlc_lviv_magdeburg_charters_desc",
            "rip_galicia_lviv_magdeburg_hall",
            "desc_rip_galicia_lviv_magdeburg_hall",
            "rip_galicia_magdeburg_charters",
            "desc_rip_galicia_magdeburg_charters",
        ),
    ),
    "VLN": (
        "localisation/RIP_VLN_realm_l_english.yml",
        "localisation/replace/RIP_VLN_content_l_{lang}.yml",
        (
            "VLN_ostrozkyi_patrons_title",
            "VLN_ostrozkyi_patrons_desc",
            "vln_ostrozkyi_patronage",
            "desc_vln_ostrozkyi_patronage",
        ),
    ),
    "VOL": (
        "localisation/RIP_VOL_realm_l_english.yml",
        "localisation/replace/RIP_VOL_content_l_{lang}.yml",
        (
            "VOL_vistula_marches_title",
            "VOL_vistula_marches_desc",
            "vol_vistula_carpathian_march",
            "desc_vol_vistula_carpathian_march",
        ),
    ),
    "PDL": (
        "localisation/RIP_PDL_realm_l_english.yml",
        "localisation/replace/RIP_PDL_content_l_{lang}.yml",
        (
            "PDL_dniester_granaries_title",
            "PDL_dniester_granaries_desc",
            "PDL_kamianets_magdeburg_charters_title",
            "PDL_kamianets_magdeburg_charters_desc",
            "pdl_dniester_granary_network",
            "desc_pdl_dniester_granary_network",
            "pdl_magdeburg_charters",
            "desc_pdl_magdeburg_charters",
        ),
    ),
    "KIE": (
        "localisation/RIP_KIE_realm_l_english.yml",
        "localisation/replace/RIP_KIE_content_l_{lang}.yml",
        (
            "KIE_mohyla_academy_title",
            "KIE_mohyla_academy_desc",
            "KIE_ruthenian_baroque_title",
            "KIE_ruthenian_baroque_desc",
            "KIE_second_jerusalem_title",
            "KIE_second_jerusalem_desc",
            "UKR_lithuanian_inheritance_title",
            "UKR_lithuanian_inheritance_desc",
            "UKR_swedish_question_title",
            "UKR_swedish_question_desc",
            "UKR_breadbasket_of_europe_title",
            "UKR_breadbasket_of_europe_desc",
            "UKR_ruthenian_empire_title",
            "UKR_ruthenian_empire_desc",
            "KIE_lavra_printing_press",
            "desc_KIE_lavra_printing_press",
            "KIE_second_jerusalem_modifier",
            "desc_KIE_second_jerusalem_modifier",
            "UKR_grand_duchy_heritage",
            "desc_UKR_grand_duchy_heritage",
            "UKR_breadbasket_granary",
            "desc_UKR_breadbasket_granary",
            "UKR_ruthenian_empire_modifier",
            "desc_UKR_ruthenian_empire_modifier",
            "UKR_every_grain_province_tt",
            "UKR_ruthenian_grain",
        ),
    ),
    "KUY": (
        "localisation/RIP_KUY_realm_l_english.yml",
        "localisation/replace/RIP_shared_ruthenian_content_l_{lang}.yml",
        (
            "KUY_magdeburg_guilds_title",
            "KUY_magdeburg_guilds_desc",
            "KUY_granary_of_steppe_title",
            "KUY_granary_of_steppe_desc",
            "KUY_dnieper_crossings_title",
            "KUY_dnieper_crossings_desc",
            "KUY_steppe_caravans_title",
            "KUY_steppe_caravans_desc",
            "KUY_restore_kuyaba_title",
            "KUY_restore_kuyaba_desc",
            "KUY_crimean_gates_title",
            "KUY_crimean_gates_desc",
            "KUY_sultanate_of_rus_title",
            "KUY_sultanate_of_rus_desc",
            "KUY_black_sea_fleet_title",
            "KUY_black_sea_fleet_desc",
            "KUY_bosporus_straits_title",
            "KUY_bosporus_straits_desc",
            "kuy_magdeburg_guilds_modifier",
            "desc_kuy_magdeburg_guilds_modifier",
            "kuy_steppe_granary",
            "desc_kuy_steppe_granary",
            "kuy_steppe_caravans_modifier",
            "desc_kuy_steppe_caravans_modifier",
            "kuy_black_sea_fleet_modifier",
            "desc_kuy_black_sea_fleet_modifier",
            "kuy_sultanate_of_rus_modifier",
            "desc_kuy_sultanate_of_rus_modifier",
            "KUY_every_grain_province_tt",
            "kuy_steppe_grain",
        ),
    ),
    "CHR": (
        "localisation/RIP_CHR_realm_l_english.yml",
        "localisation/replace/RIP_CHR_content_l_{lang}.yml",
        (
            "chr_siversk_sloboda_frontier_title",
            "chr_siversk_sloboda_frontier_desc",
            "chr_tmutarakan_inheritance_title",
            "chr_tmutarakan_inheritance_desc",
            "chr_tmutarakan_principality",
            "desc_chr_tmutarakan_principality",
        ),
    ),
    "PRL": (
        "localisation/RIP_PRL_realm_l_english.yml",
        "localisation/replace/RIP_PRL_content_l_{lang}.yml",
        (
            "prl_magdeburg_charter_title",
            "prl_magdeburg_charter_desc",
            "prl_dnieper_baroque_title",
            "prl_dnieper_baroque_desc",
            "prl_sloboda_regiments_title",
            "prl_sloboda_regiments_desc",
            "prl_magdeburg_charter_modifier",
            "desc_prl_magdeburg_charter_modifier",
            "prl_pereiaslav_baroque_collegium",
            "desc_prl_pereiaslav_baroque_collegium",
            "prl_sloboda_regimental_frontier",
            "desc_prl_sloboda_regimental_frontier",
        ),
    ),
    "ZAZ": (
        "localisation/RIP_ZAZ_realm_l_english.yml",
        "localisation/replace/RIP_ZAZ_content_l_{lang}.yml",
        (
            "ZAZ_sahaidachnyi_reforms_title",
            "ZAZ_sahaidachnyi_reforms_desc",
            "ZAZ_heroic_campaigns_title",
            "ZAZ_heroic_campaigns_desc",
            "zaz_sahaidachnyi_reforms_modifier",
            "desc_zaz_sahaidachnyi_reforms_modifier",
            "zaz_heroic_campaigns_modifier",
            "desc_zaz_heroic_campaigns_modifier",
            "zaz_black_sea_campaigns_tt",
        ),
    ),
    "HET": (
        "localisation/RIP_HET_realm_l_english.yml",
        "localisation/replace/RIP_HET_content_l_{lang}.yml",
        (
            "het_sahaidachnyi_host_title",
            "het_sahaidachnyi_host_desc",
            "het_age_of_heroic_campaigns_title",
            "het_age_of_heroic_campaigns_desc",
            "het_black_sea_armada_title",
            "het_black_sea_armada_desc",
            "het_sahaidachnyi_regiments",
            "desc_het_sahaidachnyi_regiments",
            "het_heroic_sea_campaigns",
            "desc_het_heroic_sea_campaigns",
            "het_black_sea_armada_modifier",
            "desc_het_black_sea_armada_modifier",
            "het_black_sea_campaigns_tt",
        ),
    ),
}


def parse_series_in_file(rel_path: str) -> list[tuple[str, int, str, list[tuple[str, int, list[str]]]]]:
    raw = re.sub(r"#[^\n]*", "", read(rel_path))
    series_list = []
    for m in re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", raw):
        sname = m.group(1)
        body = named_block(raw, sname)
        slot = int(re.search(r"\bslot\s*=\s*(\d+)", body).group(1))
        pot = re.sub(r"\s+", " ", named_block(body, "potential")).strip()
        missions = []
        for mm in re.finditer(r"(?m)^\t([A-Za-z0-9_]+)\s*=\s*\{", body):
            mname = mm.group(1)
            if mname in ("potential", "potential_on_load", "ai_weight"):
                continue
            mbody = named_block(body, mname)
            pos = int(re.search(r"\bposition\s*=\s*(\d+)", mbody).group(1))
            reqs = re.search(r"\brequired_missions\s*=\s*\{([^}]*)\}", mbody, re.S)
            missions.append((mname, pos, reqs.group(1).split() if reqs else []))
        series_list.append((sname, slot, pot, missions))
    return series_list


def simulate_stacking(label: str, files: list[str], pred, ported_set: set[str]) -> dict[str, tuple[int, int]]:
    series = []
    for fn in sorted(files, key=str.lower):
        for item in parse_series_in_file(f"missions/{fn}"):
            if pred(item[0], item[2]):
                series.append(item)
    cursors: dict[int, int] = defaultdict(int)
    placed: dict[str, tuple[int, int, list[str]]] = {}
    grid: dict[tuple[int, int], str] = {}
    for sname, slot, _, missions in series:
        assert 1 <= slot <= 5, (label, sname, slot)
        prev = 0
        for mname, pos, reqs in missions:
            if mname in ported_set:
                assert pos > prev, (label, sname, mname, pos, prev)
            prev = pos
            row = max(cursors[slot] + 1, pos)
            assert (slot, row) not in grid, (label, (slot, row), grid[(slot, row)], mname)
            cursors[slot] = row
            grid[(slot, row)] = mname
            placed[mname] = (slot, row, reqs)
    for mname, (s, p, reqs) in placed.items():
        if mname in ported_set:
            for dep in reqs:
                assert dep in placed, (label, mname, "missing req", dep)
                ds, dp, _ = placed[dep]
                assert p > dp, (label, f"{dep}(s{ds}p{dp}) -> {mname}(s{s}p{p}) non-downward")
                if ds == s and p - dp > 1:
                    blockers = [grid[(s, y)] for y in range(dp + 1, p) if (s, y) in grid]
                    assert not blockers, (label, mname, dep, blockers)
    return {k: (v[0], v[1]) for k, v in placed.items()}


def loc_map(path: Path) -> dict[str, str]:
    return dict(
        re.findall(
            r'^ ([A-Za-z0-9_.\-]+):\d+\s+"(.*)"$',
            path.read_text(encoding="utf-8-sig"),
            re.M,
        )
    )


def main() -> int:
    # 1. Verify all 33 ported missions exist with slot 1..5 and position < 24.
    all_ported: set[str] = set()
    for rel_path, expected in EXPECTED_PORTS.items():
        text = read(rel_path)
        series = parse_series_in_file(rel_path)
        found = {mname: (slot, pos) for _, slot, _, ms in series for mname, pos, _ in ms}
        for mname in expected:
            assert mname in found, (rel_path, mname, "missing")
            slot, pos = found[mname]
            assert 1 <= slot <= 5, (mname, slot)
            assert 1 <= pos < 24, (mname, pos)
            all_ported.add(mname)
        assert not (ROOT / rel_path).read_bytes().startswith(b"\xef\xbb\xbf"), rel_path
    assert len(all_ported) == 33, len(all_ported)

    # 2. Verify EU4 slot-stacking zero collisions & downward ported arrows.
    simulate_stacking("KUY", ["Kuyaba_Missions.txt"], lambda s, p: True, all_ported)
    simulate_stacking(
        "KIE",
        ["Kyiv_Missions.txt", "Kyiv_Shared_Missions.txt", "Kyiv_Successors_Missions.txt"],
        lambda s, p: "tag = KIE" in p,
        all_ported,
    )
    ukr_grid = simulate_stacking(
        "UKR_KRU",
        ["Kyiv_Missions.txt", "Kyiv_Shared_Missions.txt", "Kyiv_Successors_Missions.txt"],
        lambda s, p: "tag = UKR" in p,
        all_ported,
    )
    assert ukr_grid["UKR_ruthenian_empire"] == (3, 12)
    assert ukr_grid["KIE_second_jerusalem"] == (1, 11)
    assert ukr_grid["UKR_swedish_question"] == (2, 11)

    for br, excl in (("diplomatic", "militarized"), ("militarized", "diplomatic")):
        simulate_stacking(
            f"CHR_{br}",
            ["Chernihiv_Missions.txt"],
            lambda s, p, ex=excl: ex not in p and "chr_identity_branching" not in s and "placeholder" not in s,
            all_ported,
        )
    simulate_stacking("PRL", ["Pereiaslav_Missions.txt"], lambda s, p: True, all_ported)
    simulate_stacking("HET_standalone", ["zzz_Hetmanate_Missions.txt"], lambda s, p: True, all_ported)
    simulate_stacking(
        "HET_from_PRL",
        ["Pereiaslav_Missions.txt", "zzz_Hetmanate_Missions.txt"],
        lambda s, p: True,
        all_ported,
    )
    for bflag in ("zaz_only_zaz", "zaz_allied_tur", "zaz_allied_rus", "zaz_allied_gol", "zaz_allied_cri", "zaz_allied_pol"):
        simulate_stacking(
            f"HET_from_ZAZ_{bflag}",
            ["Zaporozhie_Missions.txt", "zzz_Hetmanate_Missions.txt"],
            lambda s, p, bf=bflag: (
                "ZAZ_missions_" not in s or ("NOT = { OR = {" not in p)
            ) and ("zaz_allied_" not in p and "zaz_only_zaz" not in p or bf in p)
            and (s not in ("ZAZ_missions_1", "ZAZ_missions_2", "ZAZ_missions_3", "ZAZ_missions_4", "ZAZ_missions_5") or "zaz_has_legacy_missions" in p),
            all_ported,
        )

    # 3. KIE_missions_5 duplicate row 4 fix.
    kie_shared = read("missions/Kyiv_Shared_Missions.txt")
    assert "position = 5" in named_block(kie_shared, "KIE_cossack")
    assert "position = 6" in named_block(kie_shared, "KIE_dnieper_settlement")

    # 4. Donor caveat enforcement across active mission files.
    for rel_path in EXPECTED_PORTS:
        txt = read(rel_path)
        assert "kryvbas" not in txt.lower(), rel_path
        assert 'rename_capital = "Korsun"' not in txt, rel_path
    kuy_txt = read("missions/Kuyaba_Missions.txt")
    assert "change_trade_goods = iron" not in kuy_txt
    chr_inherit = named_block(read("missions/Chernihiv_Missions.txt"), "chr_tmutarakan_inheritance")
    assert "change_trade_goods = unknown" not in chr_inherit and "change_trade_goods = grain" in chr_inherit
    zaz_sah = named_block(read("missions/Zaporozhie_Missions.txt"), "ZAZ_sahaidachnyi_reforms")
    assert "manuever = 4" in zaz_sah and "maneuver =" not in zaz_sah

    # 5. Localisation mirror, Ostroh caveat, legacy non-overlap, and 2-line vic_18 width check.
    legacy_keys = set(loc_map(ROOT / "localisation/RIP_shared_ruthenian_legacy_missions_l_english.yml"))
    all_titles: list[tuple[str, str]] = []
    for owner, (en_rel, rep_tmpl, keys) in PORTED_LOC_FILES.items():
        en = loc_map(ROOT / en_rel)
        assert not (set(keys) & legacy_keys), (owner, set(keys) & legacy_keys)
        for k in keys:
            assert k in en and en[k].strip(), (owner, k)
            if k.endswith("_title"):
                all_titles.append((k, en[k]))
        for lang in ("french", "german", "spanish"):
            fb = loc_map(ROOT / rep_tmpl.format(lang=lang))
            for k in keys:
                assert fb.get(k) == en[k], (owner, lang, k)

    vln_desc = loc_map(ROOT / "localisation/RIP_VLN_realm_l_english.yml")["VLN_ostrozkyi_patrons_desc"]
    assert "Ostroh" in vln_desc and "Rivne (2962)" in vln_desc

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

        for k, title in all_titles:
            n84, w84 = wrap_metrics(title, 84)
            n90, w90 = wrap_metrics(title, 90)
            assert n84 <= 2 and n90 <= 2 and w84 <= 84 and w90 <= 90, (k, title, n84, w84, n90, w90)

    print(
        f"DONOR MISSION PORTS PASS: {len(all_ported)} ported missions across 5 country groups, "
        "0 stacking collisions, caveats and 4-language EFIGS fallbacks verified (static only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
