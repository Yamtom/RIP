"""Static regression contract for RIP estates, privileges, and agendas."""

from __future__ import annotations

from collections import Counter
import re
import sys

from clausewitz_testlib import ROOT, keyed_blocks, named_block, normalized, read


COUNTRY_PRIVILEGES = {
    "common/estate_privileges/RIP_CHR_privileges.txt": {
        "tag": "CHR",
        "keys": {
            "estate_nobles_chr_seimski_statuty",
            "estate_church_chr_chernihiv_collegium",
            "estate_cossacks_chr_starshyna_collegium",
            "estate_burghers_chr_grain_cartels",
        },
    },
    "common/estate_privileges/RIP_HET_privileges.txt": {
        "tag": "HET",
        "keys": {
            "estate_cossacks_het_registered_host",
            "estate_nobles_het_starshyna_class",
            "estate_nobles_het_hetman_power",
            "estate_burghers_het_left_bank",
            "estate_church_het_academy",
        },
    },
    "common/estate_privileges/RIP_ZAZ_privileges.txt": {
        "tag": "ZAZ",
        "keys": {
            "estate_cossacks_zaz_sich_rada",
            "estate_cossacks_zaz_chaiky_raids",
            "estate_cossacks_zaz_free_steppe",
            "estate_cossacks_zaz_wild_field",
        },
    },
}

SHARED_JEWISH = {
    "estate_jewish_tax_farmers",
    "estate_jewish_loan_banks",
    "estate_jewish_kahal_autonomy",
    "estate_jewish_black_sea_network",
}
JEWISH_TAGS = {"POL", "LIT", "PLC", "HLC", "VOL", "VLN", "KRU", "HET", "PRL", "PDL", "KUY", "UKR"}

MAGNATE_PRIVILEGES = {
    "estate_magnates_land_rights",
    "estate_magnates_folwarks",
    "estate_magnates_private_banners",
    "estate_magnates_supremacy_over_szlachta",
    "estate_magnates_anti_absolutism",
    "estate_magnates_curtail_cossacks",
}
ORTHODOX_PRIVILEGES = {
    "rip_privilege_josephite_discipline",
    "rip_privilege_nonpossessor_rule",
}
MAGNATE_AGENDAS = {
    "estate_magnates_agenda_develop_latifundium",
    "estate_magnates_agenda_hire_advisor",
}

ESTATE_REGISTRATIONS = {
    "common/estates/01_church.txt": ORTHODOX_PRIVILEGES | {
        "estate_church_chr_chernihiv_collegium",
        "estate_church_het_academy",
    },
    "common/estates/02_nobility.txt": {
        "estate_nobles_chr_seimski_statuty",
        "estate_nobles_het_starshyna_class",
        "estate_nobles_het_hetman_power",
    },
    "common/estates/03_burghers.txt": SHARED_JEWISH | {
        "estate_burghers_chr_grain_cartels",
        "estate_burghers_het_left_bank",
    },
    "common/estates/04_cossacks.txt": {
        "estate_cossacks_chr_starshyna_collegium",
        "estate_cossacks_het_registered_host",
        "estate_cossacks_zaz_sich_rada",
        "estate_cossacks_zaz_chaiky_raids",
        "estate_cossacks_zaz_free_steppe",
        "estate_cossacks_zaz_wild_field",
    },
    "common/estates/RIP_magnates.txt": MAGNATE_PRIVILEGES,
}

CUSTOM_SCRIPT_FILES = (
    "common/estate_agendas/RIP_magnate_agendas.txt",
    "common/estate_privileges/RIP_CHR_privileges.txt",
    "common/estate_privileges/RIP_HET_privileges.txt",
    "common/estate_privileges/RIP_ZAZ_privileges.txt",
    "common/estate_privileges/RIP_magnate_privileges.txt",
    "common/estate_privileges/RIP_orthodox_zeal_privileges.txt",
    "common/estate_privileges/RIP_shared_jewish_privileges.txt",
    "common/estates/RIP_magnates.txt",
    "common/estates_preload/RIP_magnates_modifiers.txt",
)


def require(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def top_level_keys(text: str) -> set[str]:
    return set(re.findall(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text))


def exact_tokens(text: str) -> list[str]:
    return re.findall(r"(?m)^\s*((?:estate_|rip_privilege_)[A-Za-z0-9_]+)\s*$", text)


def event_block(text: str, event_id: str) -> str:
    for _, block in keyed_blocks(text, "country_event"):
        if re.search(rf"(?m)^\s*id\s*=\s*{re.escape(event_id)}\s*$", block):
            return block
    raise KeyError(f"country_event id {event_id!r} not found")


def check_country_files(failures: list[str]) -> set[str]:
    all_keys: set[str] = set()
    for relative, contract in COUNTRY_PRIVILEGES.items():
        text = read(relative)
        keys = top_level_keys(text)
        require(failures, keys == contract["keys"],
                f"{relative}: expected {sorted(contract['keys'])}, found {sorted(keys)}")
        all_keys |= keys
        for key in contract["keys"]:
            block = named_block(text, key)
            for gate in ("is_valid", "can_select"):
                gate_block = named_block(block, gate)
                require(failures, f"tag = {contract['tag']}" in normalized(gate_block),
                        f"{relative}::{key}: {gate} is not gated to {contract['tag']}")
    return all_keys


def check_shared_jewish(failures: list[str]) -> None:
    relative = "common/estate_privileges/RIP_shared_jewish_privileges.txt"
    text = read(relative)
    require(failures, top_level_keys(text) == SHARED_JEWISH,
            f"{relative}: Jewish privilege ownership drifted")
    for key in SHARED_JEWISH:
        block = named_block(text, key)
        for gate in ("is_valid", "can_select"):
            tags = re.findall(r"\btag\s*=\s*([A-Z0-9]{3})\b", named_block(block, gate))
            require(failures, Counter(tags) == Counter(JEWISH_TAGS),
                    f"{relative}::{key}: {gate} tag set differs from the shared contract")

    trigger = named_block(event_block(read("events/JewishEstate.txt"), "rip_jewish.1"), "trigger")
    event_tags = re.findall(r"\btag\s*=\s*([A-Z0-9]{3})\b", trigger)
    require(failures, Counter(event_tags) == Counter(JEWISH_TAGS),
            "events/JewishEstate.txt::rip_jewish.1: tag gate differs from its privileges")


def check_registrations(failures: list[str], custom_privileges: set[str]) -> None:
    registrations: Counter[str] = Counter()
    for relative, expected in ESTATE_REGISTRATIONS.items():
        text = read(relative)
        listed = set(exact_tokens(named_block(text, "privileges")))
        for key in custom_privileges:
            if key in listed:
                registrations[key] += 1
        require(failures, expected <= listed,
                f"{relative}: missing RIP privileges {sorted(expected - listed)}")

    for key in custom_privileges:
        require(failures, registrations[key] == 1,
                f"{key}: expected one estate registration, found {registrations[key]}")

    definitions: Counter[str] = Counter()
    for path in (ROOT / "common/estate_privileges").glob("*.txt"):
        definitions.update(top_level_keys(path.read_text(encoding="utf-8-sig", errors="replace")))
    for key in custom_privileges:
        require(failures, definitions[key] == 1,
                f"{key}: expected one privilege definition, found {definitions[key]}")

    magnates = read("common/estates/RIP_magnates.txt")
    agendas = set(exact_tokens(named_block(magnates, "agendas")))
    require(failures, MAGNATE_AGENDAS <= agendas,
            f"common/estates/RIP_magnates.txt: missing agendas {sorted(MAGNATE_AGENDAS - agendas)}")


def check_magnates(failures: list[str]) -> None:
    privileges = read("common/estate_privileges/RIP_magnate_privileges.txt")
    require(failures, top_level_keys(privileges) == MAGNATE_PRIVILEGES,
            "RIP_magnate_privileges.txt: Magnates privilege ownership drifted")

    supremacy = named_block(privileges, "estate_magnates_supremacy_over_szlachta")
    for gate in ("is_valid", "can_select"):
        require(failures, "has_estate = estate_nobles" in normalized(named_block(supremacy, gate)),
                f"Magnates supremacy: {gate} does not require the Nobles estate")

    curtail = named_block(privileges, "estate_magnates_curtail_cossacks")
    for gate in ("is_valid", "can_select"):
        require(failures, "has_estate = estate_cossacks" in normalized(named_block(curtail, gate)),
                f"Curtail Cossacks: {gate} does not require the Cossacks estate")
    require(failures, "factor = 0" not in normalized(named_block(curtail, "ai_will_do")),
            "Curtail Cossacks: AI is still disabled")

    agendas = read("common/estate_agendas/RIP_magnate_agendas.txt")
    require(failures, top_level_keys(agendas) == MAGNATE_AGENDAS,
            "RIP_magnate_agendas.txt: Magnates agenda ownership drifted")
    require(failures, "task_failed_effect" not in agendas,
            "RIP_magnate_agendas.txt: non-vanilla task_failed_effect remains")
    for key in MAGNATE_AGENDAS:
        failure = named_block(named_block(agendas, key), "failing_effect")
        norm = normalized(failure)
        require(failures, all(token in norm for token in (
            "on_failed_agenda_effect = yes", "clr_auto_complete_flag = yes",
            "add_estate_loyalty_modifier", "desc = EST_VAL_AGENDA_DENIED",
        )), f"{key}: failure path does not follow the vanilla agenda pattern")


def check_burgher_name(failures: list[str]) -> None:
    burghers = named_block(read("common/estates/03_burghers.txt"), "estate_burghers")
    candidates = [block for _, block in keyed_blocks(burghers, "custom_name")
                  if "desc = estate_mecenates" in normalized(block)]
    require(failures, len(candidates) == 1,
            "03_burghers.txt: expected one estate_mecenates custom_name block")
    if candidates:
        expected = {"ruthenian", "ruthenian_new", "rusyn", "rusyn_new", "rusyn_new_new",
                    "byelorussian", "byelorussian_new"}
        found = set(re.findall(r"\bculture\s*=\s*([A-Za-z0-9_]+)", candidates[0]))
        require(failures, found == expected,
                f"03_burghers.txt: estate_mecenates cultures differ: {sorted(found)}")


def check_style_and_dependencies(failures: list[str]) -> None:
    for relative in CUSTOM_SCRIPT_FILES:
        text = read(relative)
        for number, line in enumerate(text.splitlines(), 1):
            require(failures, not re.match(r"^ +\S", line),
                    f"{relative}:{number}: indentation must use tabs")
        require(failures, not re.search(r"(?<![0-9])-?\d+\.[0-9]*[1-9]0\b", text),
                f"{relative}: decimal literal has a redundant trailing zero")

    ordered_files = tuple(COUNTRY_PRIVILEGES) + (
        "common/estate_privileges/RIP_shared_jewish_privileges.txt",
    )
    for relative in ordered_files:
        text = read(relative)
        for key in top_level_keys(text):
            block = named_block(text, key)
            header = block[:block.find("is_valid")]
            positions = []
            for field in ("icon", "land_share", "max_absolutism", "loyalty", "influence"):
                match = re.search(rf"(?m)^\s*{field}\s*=", header)
                if match:
                    positions.append(match.start())
            require(failures, positions == sorted(positions),
                    f"{relative}::{key}: top fields do not follow vanilla order")

    reforms = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                         for path in (ROOT / "common/government_reforms").glob("*.txt"))
    for reform in ("hlc_magnate_assembly_reform", "pdl_magnate_republic_reform",
                   "pdl_magnate_dominion_reform", "vln_voivode_council"):
        require(failures, len(re.findall(rf"(?m)^{re.escape(reform)}\s*=\s*\{{", reforms)) == 1,
                f"Magnates trigger reform is not defined exactly once: {reform}")

    effects = read("common/scripted_effects/rip_estate_effects.txt")
    require(failures, len(re.findall(r"(?m)^rip_estate_mood_effect\s*=\s*\{", effects)) == 1,
            "rip_estate_mood_effect is not defined exactly once")

    preload = read("common/estates_preload/RIP_magnates_modifiers.txt")
    require(failures, top_level_keys(preload) == {"estate_magnates"},
            "Magnates estates_preload ownership drifted")
    preload_block = named_block(preload, "estate_magnates")
    definitions = [normalized(block) for _, block in keyed_blocks(preload_block, "modifier_definition")]
    for modifier_type, key in (
        ("loyalty", "magnates_loyalty_modifier"),
        ("influence", "magnates_influence_modifier"),
        ("privileges", "magnates_privilege_slots"),
    ):
        matches = [block for block in definitions
                   if f"type = {modifier_type}" in block and f"key = {key}" in block]
        require(failures, len(matches) == 1 and "has_estate = estate_magnates" in matches[0],
                f"Magnates estates_preload registration is invalid: {key}")

    magnates = named_block(read("common/estates/RIP_magnates.txt"), "estate_magnates")
    land_modifier = named_block(magnates, "land_ownership_modifier")
    require(failures, "magnates_loyalty_modifier = 0.2" in normalized(land_modifier),
            "Magnates land ownership does not use its registered loyalty modifier")

    gfx = read("interface/rip_privilege_icons.gfx")
    for key in ("tax_farmers", "loan_banks", "kahal_autonomy", "black_sea_network"):
        sprite = f"rip_gfx_privilege_jewish_{key}_icon"
        require(failures, gfx.count(f'name = "{sprite}"') == 1,
                f"Jewish privilege sprite is not defined exactly once: {sprite}")
        require(failures, (ROOT / f"gfx/interface/privileges/{sprite}.dds").is_file(),
                f"Jewish privilege DDS is missing: {sprite}.dds")


def check_localisation(failures: list[str], keys: set[str]) -> None:
    english = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                          for path in (ROOT / "localisation").rglob("*_l_english.yml"))
    loc_keys = set(re.findall(r"(?m)^\s*([A-Za-z0-9_.-]+):\d+\s", english))
    for key in keys:
        for suffix in ("", "_desc"):
            require(failures, key + suffix in loc_keys,
                    f"English localisation missing: {key + suffix}")
    for key in ("magnates_loyalty_modifier", "magnates_influence_modifier",
                "magnates_privilege_slots", "desc_lit_offices_closed"):
        require(failures, key in loc_keys, f"English localisation missing: {key}")


def main() -> int:
    failures: list[str] = []
    for stale in ("common/estate_privileges/chr_privileges.txt",
                  "common/estate_privileges/jewish_privileges.txt"):
        require(failures, not (ROOT / stale).exists(), f"stale mixed-content file remains: {stale}")

    country = check_country_files(failures)
    check_shared_jewish(failures)
    check_magnates(failures)
    check_burgher_name(failures)
    check_style_and_dependencies(failures)

    custom_privileges = country | SHARED_JEWISH | MAGNATE_PRIVILEGES | ORTHODOX_PRIVILEGES
    check_registrations(failures, custom_privileges)
    check_localisation(failures, custom_privileges | MAGNATE_AGENDAS | {"estate_magnates"})

    loaded_text = "\n".join(path.read_text(encoding="utf-8-sig", errors="replace")
                             for directory in ("common", "events", "missions", "decisions")
                             for path in (ROOT / directory).rglob("*.txt"))
    require(failures, "estate_jewish_merchants" not in loaded_text,
            "dead standalone estate_jewish_merchants reference remains in loaded script")

    if failures:
        print("Estate-layer contract failures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("Estate files are separated by country and all RIP links are registered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
