"""Country/entity tagging layout and migration contract for localisation/replace/.

Every file in localisation/replace/ stays flat (EU4 engine contract), carries
UTF-8 with a single BOM and `_l_<language>.yml`, and follows:
    RIP_<OWNER>_<ENTITY>_l_<language>.yml
where <OWNER> is either a country tag / tag pair (e.g. CHR, HET, MOS_RUS) or
a shared domain family (e.g. shared_church, shared_ruthenian).

Generated files (build_*.py) and non-generated/legacy files intentionally target
distinct <ENTITY> names so generators can run --check without clobbering
hand-maintained or fallback entries.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REPLACE_DIR = ROOT / "localisation" / "replace"
MANIFEST_PATH = ROOT / "docs" / "data" / "localisation_replace_manifest.json"
LANGUAGES = ("english", "french", "german", "spanish")

ALLOWED_TAGS = {
    "CHR", "HET", "HLC", "KIE", "KRU", "LIT", "MOS_RUS",
    "NOV", "ODS", "PDL", "PRL", "QAS", "UZH", "VLN", "VOL", "ZAZ",
}
ALLOWED_SHARED = {
    "shared_belarus",
    "shared_church",
    "shared_commonwealth",
    "shared_cossack",
    "shared_estates",
    "shared_frontier",
    "shared_government",
    "shared_greek_catholic",
    "shared_orthodox",
    "shared_ruthenian",
    "shared_steppe",
    "shared_west_ruthenian",
}
ALLOWED_OWNERS = ALLOWED_TAGS | ALLOWED_SHARED

_OWNERS_PATTERN = "|".join(re.escape(o) for o in sorted(ALLOWED_OWNERS, key=len, reverse=True))
FILENAME_RE = re.compile(
    rf"^RIP_(?P<owner>{_OWNERS_PATTERN})_"
    r"(?P<entity>[a-z][a-z0-9_]*)_l_(?P<lang>english|french|german|spanish)\.yml$"
)
ENTRY_RE = re.compile(r'^\s*([A-Za-z0-9_.\-]+):(\d*)\s*"(.*)"\s*(?:#.*)?$')

GENERATOR_OWNED_GROUPS = {
    "RIP_HET_government_authority": "tools/build_hetman_authority.py",
    "RIP_KRU_government_rada": "tools/build_kru_rada.py",
    "RIP_shared_government_parliament_names": "tools/build_parliament_names.py",
    "RIP_shared_church_nodes": "tools/build_church_support.py",
    "RIP_shared_frontier_border_watch": "tools/build_border_mechanics_localisation.py",
    "RIP_shared_government_status": "tools/build_government_status_ui.py",
    "RIP_shared_church_redesign": "tools/build_church_localisation.py",
}

RETIRED_GENERATED_GROUPS = {
    "RIP_UZH_government_captaincy",
    "RIP_KRU_government_status",
    "RIP_KIE_government_status",
    "RIP_HLC_government_status",
    "RIP_LIT_government_status",
    "RIP_VLN_government_status",
    "RIP_MOS_RUS_church_orthodox_ui",
    "RIP_shared_greek_catholic_church_ui",
}

LEGACY_GENERATED_BASES = (
    "zzzz_RIP_het_authority",
    "zzzz_rip_kru_rada",
    "zzzz_rip_parliament_names",
    "zzzz_RIP_church_nodes",
    "zzz_RIP_untranslated_border",
    "zzzz_RIP_government_status",
    "zzzz_RIP_church_redesign",
)


def parse_replace_filename(name: str) -> tuple[str, str, str] | None:
    match = FILENAME_RE.match(name)
    if not match:
        return None
    owner, entity, lang = match.group("owner"), match.group("entity"), match.group("lang")
    if owner not in ALLOWED_OWNERS:
        return None
    return owner, entity, lang


def parse_yml_entries(path: Path) -> list[tuple[str, str, str]]:
    """Return ordered list of (key, version_digits, value_text) from a Paradox .yml."""
    entries: list[tuple[str, str, str]] = []
    text = path.read_text(encoding="utf-8-sig")
    for idx, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if idx == 0 and re.match(r"^l_[a-z]+:$", stripped):
            continue
        match = ENTRY_RE.match(line)
        if not match:
            raise ValueError(f"{path}: unmatched localisation line {idx + 1}: {line!r}")
        entries.append((match.group(1), match.group(2), match.group(3)))
    return entries


def _load_main_english_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for path in sorted((ROOT / "localisation").glob("*_l_english.yml")):
        for key, _, _ in parse_yml_entries(path):
            sources[key] = path.name
    return sources


def _load_gov_title_keys() -> set[str]:
    names_dir = ROOT / "common" / "government_names"
    if not names_dir.is_dir():
        return set()
    keys: set[str] = set()
    for path in sorted(names_dir.glob("*.txt")):
        keys.update(re.findall(r"\b([A-Z][A-Z0-9_]+)\b", path.read_text(encoding="utf-8-sig")))
    return keys


def classify_static_key(
    src_filename: str,
    key: str,
    en_source: dict[str, str],
    gov_title_keys: set[str],
) -> tuple[str, str]:
    """Deterministically route every non-generator key to consolidated (owner, 'content')."""
    # 1. Existing cohesive thematic replace files
    if src_filename.startswith("zzz_chr_paths"):
        return "CHR", "content"
    if src_filename.startswith("zzz_lit_grand_duchy"):
        return "LIT", "content"
    if src_filename.startswith("zzz_zaz_paths"):
        return "ZAZ", "content"
    if src_filename.startswith("zzz_RIP_idea_names") or re.fullmatch(
        r"rip_[A-Z]{3}_ideas(?:_start|_bonus)?", key
    ):
        return "shared_ruthenian", "content"
    if src_filename.startswith("zzz_rip_faith_mechanics"):
        return "shared_church", "content"
    if src_filename.startswith("zzz_rip_free_election"):
        return "shared_commonwealth", "content"
    if src_filename.startswith("zzz_rip_gc_privileges"):
        return "shared_greek_catholic", "content"
    if src_filename.startswith("zzz_rip_magnates"):
        return "shared_estates", "content"
    if src_filename.startswith("zzz_rip_troubles"):
        return "MOS_RUS", "content"
    if src_filename.startswith("zzz_rip_government_reviews"):
        if key.startswith("RIP_UZH_"):
            return "UZH", "content"
        return "shared_government", "content"
    if src_filename.startswith("zzz_rip_palace_diplomacy"):
        if key.startswith(("vilnius_", "lit_palace.", "rip_palace_")):
            return "LIT", "content"
        if key.startswith((
            "hadiach.", "rip_hadiach_", "rip_offer_hadiach_",
            "rip_ask_to_expand_the_register", "rip_petition_to_confirm_the_register",
            "rip_register_",
        )):
            return "HET", "content"
        return "shared_ruthenian", "content"
    if src_filename.startswith("zzzz_RIP_religion_settlement"):
        if key.startswith(("rip_ro_", "desc_rip_ro_")):
            return "MOS_RUS", "content"
        if key.startswith(("rip_kyiv_", "desc_rip_kyiv_", "rip_church_council")):
            return "KIE", "content"
        return "shared_church", "content"

    # 2. Mixed pools (000_fix_descs, zzz_RIP, zzz_RIP_untranslated) or rebalancing
    kl = key.lower()
    core = kl
    for pref in (
        "desc_", "ability_", "mechanic_", "opinion_",
        "estate_nobles_", "estate_church_", "estate_burghers_",
        "estate_cossacks_", "estate_nomadic_tribes_",
    ):
        if core.startswith(pref):
            core = core[len(pref):]
    src_en = en_source.get(key, "")

    # 2a. Exact English source-file provenance for fallback entries
    if src_en in (
        "hetmanate_content_l_english.yml",
        "hetmanate_enhanced_l_english.yml",
        "het_legacy_eras_l_english.yml",
        "khmelnytsky_events_l_english.yml",
    ):
        if core.startswith(("khmelnytsky", "cossack_revolt", "haidamak")):
            return "shared_cossack", "content"
        return "HET", "content"
    if src_en in (
        "zaz_fixes_l_english.yml",
        "ZAZ_HET_localisation_fixes_l_english.yml",
        "ZAZ_HET_missions_l_english.yml",
    ):
        if core.startswith(("het_", "hetman")):
            return "HET", "content"
        return "ZAZ", "content"
    if src_en in (
        "podillia_disasters_l_english.yml",
        "podillia_enhancements_l_english.yml",
        "podillia_events_l_english.yml",
    ):
        return "PDL", "content"
    if src_en in (
        "volhynia_government_l_english.yml",
        "VOL_austrian_polish_missions_l_english.yml",
        "VOL_path_events_l_english.yml",
    ):
        if core.startswith("vln_") or "vln_" in core:
            return "VLN", "content"
        return "VOL", "content"
    if src_en in ("rip_galicia_l_english.yml", "hlc_reforms_l_english.yml"):
        return "HLC", "content"
    if src_en in ("kyiv_dnieper_l_english.yml", "kyiv_succession_history_l_english.yml"):
        if core.startswith(("ruthenian_", "pru_", "dniester", "dnestr")):
            return "shared_ruthenian", "content"
        return "KIE", "content"
    if src_en == "qasim_khanate_l_english.yml":
        return "QAS", "content"
    if src_en == "russian_orthodox_l_english.yml":
        return "MOS_RUS", "content"
    if src_en in ("orthodox_crusade_l_english.yml", "zzz_crusade_tooltips_l_english.yml"):
        return "shared_orthodox", "content"
    if src_en == "uniate_and_raid_l_english.yml":
        if core.startswith(("zaz_", "zich_")):
            return "ZAZ", "content"
        if any(tok in core for tok in ("raid", "steppe", "tatar", "yasyr", "kaffa", "cossack_chaiky", "azov", "crimea")):
            return "shared_steppe", "content"
        return "shared_greek_catholic", "content"
    if src_en in ("rip_uniate_crown_l_english.yml", "rip_diocesan_union_l_english.yml"):
        return "shared_greek_catholic", "content"
    if src_en in (
        "rip_faith_disasters_l_english.yml",
        "rip_parish_visit_l_english.yml",
        "rip_church_aspects_l_english.yml",
        "rip_faith_reforms_l_english.yml",
    ):
        return "shared_church", "content"
    if src_en in ("deluge_l_english.yml", "pl_reformation_l_english.yml"):
        return "shared_commonwealth", "content"
    if src_en in ("border_principalities_l_english.yml", "moldavian_frontier_l_english.yml"):
        return "shared_frontier", "content"
    if src_en == "zzz_steppe_raiding_l_english.yml":
        return "shared_steppe", "content"
    if src_en in ("cossack_host_decisions_l_english.yml", "cossack_host_names_l_english.yml"):
        return "shared_cossack", "content"
    if src_en == "rip_jewish_estate_l_english.yml":
        return "shared_estates", "content"
    if src_en == "west_ukraine_history_l_english.yml":
        return "shared_west_ruthenian", "content"
    if src_en in (
        "ruthenian_eastward_l_english.yml",
        "rip_ruthenian_diaspora_l_english.yml",
        "rip_capital_loss_l_english.yml",
        "rip_state_symbols_l_english.yml",
    ):
        return "shared_ruthenian", "content"

    # 2b. Key-based rules (covers RIP_l_english, 000_fix_descs, zzz_RIP, and orphans)
    if key.endswith("_sprite_pack"):
        return "shared_ruthenian", "content"
    if key.startswith(("PROV", "PROV_ADJ")):
        return "shared_ruthenian", "content"

    if key in {
        "CHR", "CHR_ADJ", "CHR_ideas", "CHR_ideas_start", "CHR_ideas_bonus",
        "SIVERSK_COMMUNE", "MAGDEBURG_RADA", "LEFT_BANK_CONFEDERATION",
        "POSADNYK", "POSADNYTSIA", "STARSHYNA_MARSHAL", "STARSHYNA_MARSHALKA",
        "HETMAN_PROTECTOR", "HETMANKA_PROTECTOR",
        "OPINION_chr_border_compact_rupture", "OPINION_chr_border_compact_support", "OPINION_chr_border_surety",
    } or core.startswith(("chr_", "chr.", "siversk", "chernihiv_")):
        return "CHR", "content"

    if key in {
        "HET", "HET_ADJ", "HET_ideas", "HET_ideas_start", "HET_ideas_bonus",
        "LITTLE_RUSSIAN_STATE", "MAZEPIST_HETMANATE", "GRAIN_COLLEGIUM",
    } or core in {
        "regimental_headquarters", "dharynsky", "vishnevetsky", "khmelnitski",
        "teteria", "doroshenko", "mazepa", "skoropadsky", "apostol", "rozumovsky",
        "right_bank_loyalty", "pacts_and_statutes", "the_ruina",
    } or core.startswith((
        "het_", "het.", "hetman", "hetmany", "hetmans", "ruina",
        "left_bank_", "polkovo_", "mazepa_", "collegia_", "collegium_",
        "limited_hetman", "batuuryn_", "starshyna_clans", "crimean_alliance_het",
        "rus_cossack_service", "rus_hetmanate_client",
    )):
        return "HET", "content"

    if key in {
        "ZAZ", "ZAZ_ADJ", "ZAZ_ideas", "ZAZ_ideas_start", "ZAZ_ideas_bonus",
        "NEW_SICH", "LAST_FREE_SICH", "FREE_ZAPOROZHIAN_HOST",
    } or core in {
        "zich_relocated", "zaporozhian_sich_capital", "ottoman_chaiky_humiliation",
        "mobile_sich", "kaz_caravan", "ottoman_cossack_vassals",
        "ottoman_protected_sich", "ottoman_receives_cossacks", "rus_abolished_sich",
        "crimean_alliance_zaz",
    } or core.startswith((
        "zaz_", "zaz.", "zich_", "zaporozh", "sich_", "kosh_", "chaiky",
        "last_sich", "mercand_", "rip_zaz_",
    )):
        return "ZAZ", "content"

    if key in {
        "KIE", "KIE_ADJ", "KIE_ideas", "KIE_ideas_start", "KIE_ideas_bonus",
        "GRAND_KYIVAN_DUCHY", "GRAND_KYIVAN_DUCHY_desc", "KYIVAN_DUCHY",
        "like_rus_nation_title", "like_rus_nation_desc",
        "monthly_kyivan_throne_concord",
    } or core.startswith(("kie_", "kie.", "kyiv_", "kyivan_", "m_ukr_events.", "ukr_", "rip_regrant_the_udil")) and key not in {"KYIVAN_BOYAR_RADA"}:
        return "KIE", "content"

    if key in {
        "KRU", "KRU_ADJ", "KRU_ideas", "KRU_ideas_start", "KRU_ideas_bonus",
        "KYIVAN_RUS", "Absolute_hegemony_of_the_east", "Absolute_hegemony_of_the_east_desc",
        "rus_nation_title", "rus_nation_desc",
        "KYIVAN_BOYAR_RADA", "GREAT_BOYAR_RADA_OF_KYIV",
        "GRAND_BOYAR_POSADNIK", "GRAND_BOYAR_POSADNITSA",
    } or core.startswith((
        "kru_", "kru.", "boyar_", "boyars", "boyary", "knyazi",
        "princes_revolt", "disorderly_princes", "governmental_disruption",
    )):
        return "KRU", "content"

    if key in {
        "UZH", "UZH_ADJ", "METROPOLITAN_OF_MUKACHEVO", "PATRIARCH_OF_THE_CARPATHIANS",
    } or core.startswith((
        "uz_", "uzh_", "uzh.", "zakarpattia_", "palanok_", "rusyn", "nadkomit",
        "kapitan", "danubian_monarchy", "unite_the_rusin", "united_rusin",
        "unity_of_rusin", "opinion_uz_", "owns_all_pannonia", "owns_carpathia",
        "expand_into_transylvania", "found_maramures", "hungarian_integration",
        "great_hauptmann",
    )):
        return "UZH", "content"

    if key in {"PDL", "PDL_ADJ"} or core.startswith(("pdl_", "pdl.", "podil")):
        return "PDL", "content"

    if key in {"PRL", "PRL_ADJ"} or core.startswith(("prl_", "prl.", "pereiaslav")):
        return "PRL", "content"

    if key in {"HLC", "HLC_ADJ"} or core.startswith(("hlc_", "hlc.", "galic", "mechanic_hlc_")):
        return "HLC", "content"

    if key in {"VOL", "VOL_ADJ", "VOL_ideas", "VOL_ideas_start", "VOL_ideas_bonus"} or core.startswith(("vol_", "vol.", "rip_vol_", "volhyn", "volyn_", "m_vol_")):
        return "VOL", "content"

    if key in {"VLN", "VLN_ADJ"} or core.startswith(("vln_", "vln.", "rip_vln_")):
        return "VLN", "content"

    if key in {"ODS", "ODS_ADJ"} or core.startswith(("ods_", "ods.", "odesa_", "establish_hajibey", "new_port_charter")):
        return "ODS", "content"

    if key in {"KUY", "KUY_ADJ", "KUY_ideas", "KUY_ideas_start", "KUY_ideas_bonus"} or core.startswith(("kuy_", "kuyaba_")):
        return "shared_ruthenian", "content"

    if core.startswith(("nov_", "nov.")):
        return "NOV", "content"

    if key in {"vilnius_palace_renaissance_tt", "gdl_cultural_legacy", "grand_duchy_legacy", "grand_duchy_legacy_desc"} or core.startswith(("lit_", "lit.")):
        return "LIT", "content"

    if key in {
        "old_believers", "russian_backed_hetman", "russian_protection",
        "russian_protection_desc", "russian_supervision",
    } or core in {
        "rus_the_stable_empire", "rus_the_strong_motherland",
    } or core.endswith("_focus") and core.startswith("rus_") or core.startswith((
        "mos_", "muscov", "pomestie", "old_believ", "russian_",
        "service_class_militia",
    )):
        return "MOS_RUS", "content"

    if key in {
        "TRV", "TRV_ADJ", "BLR", "BLR_ADJ", "PLT", "PLT_ADJ", "MSK", "MSK_ADJ",
        "MSL", "MSL_ADJ", "VTB", "VTB_ADJ", "RPS", "RPS_ADJ",
    } or core.startswith((
        "blr_", "plt_", "msk_", "msl_", "vtb_", "rps_", "trv",
        "polesian", "belarus", "turov", "polotsk", "vitebsk", "minsk",
        "mstislavl", "sozh_", "river_", "wetland_", "children_of_the_marshes",
        "ancient_dregovichi", "battle_of_nemiga", "legacy_of_vseslav",
        "crossroads_of_rus", "eastern_frontier", "northern_border",
        "northern_crafts", "baltic_connections", "hanseatic_connections",
        "land_of_forests", "urban_fortifications", "forest_", "marsh_defenders",
    )):
        return "shared_belarus", "content"

    if key in {
        "AZO", "AZO_ADJ", "BAS", "BAS_ADJ", "KHK", "KHK_ADJ", "SMY", "SMY_ADJ",
        "OKH", "OKH_ADJ", "IZM", "IZM_ADJ", "URA", "URA_ADJ", "DON", "DON_ADJ",
        "fought_alongside_cossacks", "registered_cossacks_south", "registered_cossacks_border",
    } or core.startswith(("cossack_", "sloboda_", "free_cossack", "registered_cossack", "cos_and_het", "military_sloboda")):
        return "shared_cossack", "content"

    if core.startswith((
        "steppe_", "south_", "black_sea_", "horde_", "raid_", "nomadic_",
        "harass_tatar", "su_", "crimea", "wild_fields", "chumak_",
        "salt_fish_trade", "bs_flavor", "gen_compass",
    )):
        return "shared_steppe", "content"

    if core.startswith((
        "mansur", "jagoldai", "dniester", "dnestr", "border_", "frontier_",
        "severian_", "lipka_", "fortified_", "fortify_eastern", "kaffa", "kaz_",
    )):
        return "shared_frontier", "content"

    if key in {"RUTHENIAN_sigis_DESC", "RUTHENIAN_sigis_NAME"} or core.startswith(("svydrigaylo", "west_", "dvina")):
        return "shared_west_ruthenian", "content"

    if core.startswith("uniate") or key in {"council_of_florence", "catholic_oppression_resisted"}:
        return "shared_greek_catholic", "content"

    if key in {"orthodox_protected", "orthodox_champions", "Restore_the_Orthodoxy", "Restore_the_Orthodoxy_desc"} or core.startswith(("orthodox_", "church_", "monastery_")):
        return "shared_orthodox", "content"

    if core.startswith(("estate_", "magnate")) or key == "settled_urban_economy":
        return "shared_estates", "content"

    if core.startswith(("pol_", "polish_", "sejm", "rokosz", "commonwealth")) or key in {
        "supports_ruthenian_confederation", "gdl_cultural_legacy",
    }:
        return "shared_commonwealth", "content"

    if re.fullmatch(r"[A-Z0-9_]+", key) and (
        key in gov_title_keys
        or any(tok in key for tok in (
            "VOIVODE", "REPUBLIC", "KINGDOM", "EMPEROR", "EMPRESS", "PRINC",
            "CLAN_", "ELDER_", "MATRIARCH", "CHIEFTAIN", "OLIGARCH", "PREMIER",
            "MARCH", "GOVERNORATE", "TRIBAL_", "ASSEMB",
        ))
    ):
        return "shared_government", "content"

    if core.startswith((
        "sacred_", "elected_assemblies", "legislative_rada", "divine_tsyisar",
        "considerable_bloodline", "voluntary_houses", "assembly_houses",
        "open_trading_ports", "gatherers_tribute", "boyar_elite", "chumak_nobility",
        "merchant_nobility", "appoint_regional_governors",
    )):
        return "shared_government", "content"

    return "shared_ruthenian", "content"


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_current() -> dict:
    """Capture a complete pre-migration snapshot and baseline multiset per language."""
    sources = []
    by_lang: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for path in sorted(REPLACE_DIR.glob("*.yml")):
        m = re.search(r"_l_(english|french|german|spanish)\.yml$", path.name)
        lang = m.group(1) if m else "unknown"
        entries = parse_yml_entries(path)
        for item in entries:
            by_lang[lang].append(item)
        sources.append({
            "file": path.name,
            "lang": lang,
            "keys": len(entries),
            "sha256": _file_sha256(path),
        })
    lang_digests = {}
    for lang in LANGUAGES:
        ordered = sorted(by_lang[lang])
        payload = json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        lang_digests[lang] = {
            "count": len(ordered),
            "unique_keys": len({k for k, _, _ in ordered}),
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
    return {
        "schema": "RIP_<OWNER>_<ENTITY>_l_<language>.yml",
        "allowed_tags": sorted(ALLOWED_TAGS),
        "allowed_shared": sorted(ALLOWED_SHARED),
        "generator_groups": dict(sorted(GENERATOR_OWNED_GROUPS.items())),
        "baseline_files": sources,
        "language_digests": lang_digests,
    }


def collect_non_generated_targets(rebalance: bool = False) -> tuple[dict[tuple[str, str, str], list[tuple[str, str, str]]], list[Path]]:
    """Collect (owner, entity, lang) -> entries and list of files to rewrite/retire."""
    en_source = _load_main_english_sources()
    gov_title_keys = _load_gov_title_keys()
    targets: dict[tuple[str, str, str], list[tuple[str, str, str]]] = defaultdict(list)
    legacy_paths: list[Path] = []
    for path in sorted(REPLACE_DIR.glob("*.yml")):
        parsed = parse_replace_filename(path.name)
        if parsed is not None:
            owner_cur, entity_cur, lang = parsed
            group_name = f"RIP_{owner_cur}_{entity_cur}"
            if group_name in GENERATOR_OWNED_GROUPS:
                continue
            if rebalance and group_name in RETIRED_GENERATED_GROUPS:
                legacy_paths.append(path)
                continue
            if not rebalance:
                continue
            legacy_paths.append(path)
            for key, ver, val in parse_yml_entries(path):
                targets[(owner_cur, "content", lang)].append((key, ver, val))
            continue
        stem_base = re.sub(r"_l_(english|french|german|spanish)\.yml$", "", path.name)
        if stem_base in LEGACY_GENERATED_BASES or stem_base in RETIRED_GENERATED_GROUPS:
            legacy_paths.append(path)
            continue
        lang = re.search(r"_l_(english|french|german|spanish)\.yml$", path.name).group(1)
        legacy_paths.append(path)
        for key, ver, val in parse_yml_entries(path):
            owner, entity = classify_static_key(path.name, key, en_source, gov_title_keys)
            if f"RIP_{owner}_{entity}" in GENERATOR_OWNED_GROUPS:
                raise AssertionError(
                    f"Static key {key} from {path.name} routed into generator-owned group RIP_{owner}_{entity}"
                )
            targets[(owner, entity, lang)].append((key, ver, val))
    return targets, legacy_paths


def render_loc_file(owner: str, entity: str, lang: str, entries: list[tuple[str, str, str]]) -> bytes:
    header_comment = (
        f"# Tag-scoped replacement localisation: owner={owner}, entity={entity}.\n"
        if lang == "english"
        else f"# Tag-scoped replacement fallback ({lang}): owner={owner}, entity={entity}.\n"
    )
    lines = [f"l_{lang}:", f" {header_comment.rstrip()}"]
    for key, ver, val in sorted(entries, key=lambda item: item[0].lower()):
        lines.append(f' {key}:{ver} "{val}"')
    payload = ("\r\n".join(lines) + "\r\n").encode("utf-8")
    return b"\xef\xbb\xbf" + payload


def check_current(manifest: dict | None = None) -> list[str]:
    problems: list[str] = []
    if manifest is None and MANIFEST_PATH.is_file():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    by_lang: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    seen_keys: dict[str, dict[str, str]] = defaultdict(dict)
    for path in sorted(REPLACE_DIR.glob("*.yml")):
        parsed = parse_replace_filename(path.name)
        if parsed is None:
            problems.append(f"non-conforming replace filename: {path.name}")
            continue
        _, _, lang = parsed
        raw = path.read_bytes()
        if not raw.startswith(b"\xef\xbb\xbf") or raw[3:].startswith(b"\xef\xbb\xbf"):
            problems.append(f"{path.name}: must begin with exactly one UTF-8 BOM")
        first_line = raw.decode("utf-8-sig", errors="replace").splitlines()[0].strip()
        if first_line != f"l_{lang}:":
            problems.append(f"{path.name}: header {first_line!r} does not match language {lang}")
        for key, ver, val in parse_yml_entries(path):
            if key in seen_keys[lang]:
                problems.append(f"{lang}: duplicate key {key!r} in {seen_keys[lang][key]} and {path.name}")
            seen_keys[lang][key] = path.name
            by_lang[lang].append((key, ver, val))

    for sub in REPLACE_DIR.iterdir():
        if sub.is_dir():
            problems.append(f"nested directory forbidden in localisation/replace/: {sub.name}")

    if manifest and "language_digests" in manifest:
        for lang in LANGUAGES:
            expected = manifest["language_digests"][lang]
            ordered = sorted(by_lang[lang])
            payload = json.dumps(ordered, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            actual_sha = hashlib.sha256(payload).hexdigest()
            if len(ordered) != expected["count"]:
                problems.append(f"{lang}: key count {len(ordered)} != baseline {expected['count']}")
            if actual_sha != expected["sha256"]:
                problems.append(f"{lang}: multiset digest changed vs baseline manifest")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true", help="Write baseline snapshot manifest from current files")
    parser.add_argument("--dry-run", action="store_true", help="Report planned tag/entity targets without writing")
    parser.add_argument("--migrate", action="store_true", help="Write new static files and delete legacy source files")
    parser.add_argument("--rebalance", action="store_true", help="Re-classify already migrated non-generated files cleanly")
    parser.add_argument("--update-manifest", action="store_true", help="Record final target files into manifest")
    parser.add_argument("--check", action="store_true", help="Validate layout filenames, uniqueness, BOM and digests")
    args = parser.parse_args()

    if args.snapshot:
        snap = snapshot_current()
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote baseline snapshot: {len(snap['baseline_files'])} files -> {MANIFEST_PATH.relative_to(ROOT)}")
        return 0

    if args.dry_run or args.migrate or args.rebalance:
        targets, legacy_paths = collect_non_generated_targets(rebalance=args.rebalance)
        summary = Counter()
        for (owner, entity, lang), entries in targets.items():
            summary[f"RIP_{owner}_{entity}"] += len(entries)
        print(f"Non-generated target groups: {len(summary)}, legacy files to retire: {len(legacy_paths)}")
        for name, cnt in sorted(summary.items()):
            print(f"  {name}: {cnt} total entries across languages")
        if args.dry_run:
            return 0
        for old_path in legacy_paths:
            if old_path.exists():
                old_path.unlink()
        for (owner, entity, lang), entries in sorted(targets.items()):
            out_path = REPLACE_DIR / f"RIP_{owner}_{entity}_l_{lang}.yml"
            out_path.write_bytes(render_loc_file(owner, entity, lang, entries))
        print(f"Migrated {len(targets)} static files and removed {len(legacy_paths)} legacy/stale files.")
        return 0

    if args.update_manifest:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["allowed_tags"] = sorted(ALLOWED_TAGS)
        manifest["allowed_shared"] = sorted(ALLOWED_SHARED)
        manifest["generator_groups"] = dict(sorted(GENERATOR_OWNED_GROUPS.items()))
        manifest["migrated_files"] = [
            {
                "file": path.name,
                "owner": parsed[0],
                "entity": parsed[1],
                "lang": parsed[2],
                "keys": len(parse_yml_entries(path)),
                "sha256": _file_sha256(path),
            }
            for path in sorted(REPLACE_DIR.glob("*.yml"))
            if (parsed := parse_replace_filename(path.name)) is not None
        ]
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Updated manifest with {len(manifest['migrated_files'])} target files.")
        return 0

    if args.check:
        problems = check_current()
        if problems:
            for item in problems:
                print(f"FAIL: {item}")
            return 1
        total = len(list(REPLACE_DIR.glob("*.yml")))
        print(f"LOCALISATION REPLACE LAYOUT PASS: {total} files comply with RIP_<OWNER>_<ENTITY>_l_<lang>.yml")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
