"""Static contracts for additive Ruthenian-culture / Ruthenia-region neighbor branches.

Verifies the 15 decision/event branches (30 events total) for TUR (6), CRI (3),
POL/PLC (3), and HAB/AUH (3) plus their 12 modifiers and 4-language EFIGS
localisation, without overriding vanilla event/decision files.

Static only: inspects Clausewitz scripts and localisation; does not run EU4.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from clausewitz_testlib import ROOT, matching_brace, read, vanilla_has_sprite
import check_glossary


BOM = b"\xef\xbb\xbf"
LANGUAGES = ("english", "french", "german", "spanish")

VANILLA_EVENT_NO_OVERRIDE = (
    "FlavorTUR.txt",
    "HaremEvents.txt",
    "Decadence.txt",
    "estate_janissaries.txt",
    "disaster_TUR_JanissaryDecadence.txt",
    "disaster_ottoman_power_struggle.txt",
    "SalonikaEvents.txt",
    "flavorBYZ.txt",
    "disaster_Revolution.txt",
    "flavorCRI.txt",
    "horde_mission_events.txt",
    "steppe_flavor.txt",
    "TribalSuccession.txt",
    "estate_tribes.txt",
    "flavorPOL.txt",
    "ElectiveMonarchy.txt",
    "flavorMOL.txt",
    "flavorTEU.txt",
    "flavorHSA.txt",
    "libirumveto.txt",
    "estate_cossacks.txt",
    "FlavorHAB.txt",
    "PragmaticSanction.txt",
    "Incident_UniversalEmpire.txt",
    "Hungarian_Revolution_Disaster_Events.txt",
    "flavorHUN.txt",
    "flavorBAV.txt",
)

VANILLA_DECISION_NO_OVERRIDE = (
    "Ottoman.txt",
    "Muslim.txt",
    "TatarNation.txt",
    "MongolEmpire.txt",
    "EstateActionsNomadicTribes.txt",
    "Poland.txt",
    "PolishNation.txt",
    "TheCommonwealth.txt",
    "LiberumVeto.txt",
    "EstateActionsCossacks.txt",
    "AustrianDecisions.txt",
    "AustriaHungaryDecisions.txt",
    "FormAustriaHungary.txt",
    "HabsburgNation.txt",
    "PragmaticSanction.txt",
)

TAG_FAMILIES = {
    "TUR": ("rip_tur_ruthenian", 6),
    "CRI": ("rip_cri_ruthenian", 3),
    "POL": ("rip_pol_ruthenian", 3),
    "HAB": ("rip_hab_ruthenian", 3),
}

COUNTRY_MODS = {
    "rip_tur_ruthenian_palace_waqf",
    "rip_tur_salonika_ruthenian_factors",
    "rip_tur_phanar_kyiv_mediation",
    "rip_cri_dnieper_salt_truce",
    "rip_cri_ruthenian_yarlyk_chancery",
    "rip_pol_ruthenian_sejmik_accord",
    "rip_pol_ruthenian_border_register",
    "rip_hab_galicia_cadastre_mod",
    "rip_hab_carpathian_communes",
    "rip_hab_carpathian_post_road",
}

PROVINCE_MODS = {
    "rip_tur_kamianets_defter",
    "rip_pol_lviv_staple_corridor",
}


def parse_decisions(text: str) -> dict[str, str]:
    clean = re.sub(r"#[^\n]*", "", text)
    m = re.search(r"(?m)^country_decisions\s*=\s*\{", clean)
    assert m, "missing country_decisions block"
    body = clean[m.end() - 1 : matching_brace(clean, m.end() - 1) + 1]
    out: dict[str, str] = {}
    for dm in re.finditer(r"(?m)^\t([a-z0-9_]+)\s*=\s*\{", body):
        key = dm.group(1)
        out[key] = body[dm.start() : matching_brace(body, dm.end() - 1) + 1]
    return out


def parse_events(text: str) -> dict[str, str]:
    clean = re.sub(r"#[^\n]*", "", text)
    out: dict[str, str] = {}
    for em in re.finditer(r"(?m)^country_event\s*=\s*\{", clean):
        block = clean[em.start() : matching_brace(clean, em.end() - 1) + 1]
        idm = re.search(r"\bid\s*=\s*([a-z0-9_.]+)", block)
        assert idm, "country_event without id"
        out[idm.group(1)] = block
    return out


def extract_options(event_block: str) -> list[str]:
    return [
        event_block[om.start() : matching_brace(event_block, om.end() - 1) + 1]
        for om in re.finditer(r"(?m)^\toption\s*=\s*\{", event_block)
    ]


def validate_family(
    tag: str,
    namespace: str,
    expected_branches: int,
    dec_text: str,
    ev_text: str,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    decisions = parse_decisions(dec_text)
    events = parse_events(ev_text)

    if len(decisions) != expected_branches:
        errors.append(
            f"{tag}: expected {expected_branches} decisions, found {len(decisions)}"
        )
    if len(events) != expected_branches * 2:
        errors.append(
            f"{tag}: expected {expected_branches * 2} events, found {len(events)}"
        )

    ns_m = re.search(r"(?m)^namespace\s*=\s*([a-z0-9_]+)", ev_text)
    if not ns_m or ns_m.group(1) != namespace:
        errors.append(f"{tag}: expected namespace={namespace}")

    fired_events: list[str] = []
    for dec_key, dec_body in decisions.items():
        flag = f"{dec_key}_heard"
        if f"has_country_flag = {flag}" not in dec_body:
            errors.append(f"{dec_key}: missing has_country_flag = {flag}")
        if f"set_country_flag = {flag}" not in dec_body:
            errors.append(f"{dec_key}: missing set_country_flag = {flag}")
        ev_m = re.search(r"country_event\s*=\s*\{\s*id\s*=\s*([a-z0-9_.]+)", dec_body)
        if not ev_m:
            errors.append(f"{dec_key}: does not fire any country_event")
        else:
            fired_events.append(ev_m.group(1))
            if ev_m.group(1) not in events:
                errors.append(f"{dec_key}: fired event {ev_m.group(1)} not defined")

    for eid, eblock in events.items():
        if "is_triggered_only = yes" not in eblock:
            errors.append(f"{eid}: missing is_triggered_only = yes")
        pic_m = re.search(r"\bpicture\s*=\s*([A-Za-z0-9_]+)", eblock)
        if not pic_m:
            errors.append(f"{eid}: missing picture")
        elif vanilla_has_sprite(pic_m.group(1)) is False:
            errors.append(f"{eid}: unknown sprite {pic_m.group(1)}")

    for idx in range(expected_branches):
        odd_id = f"{namespace}.{idx * 2 + 1}"
        even_id = f"{namespace}.{idx * 2 + 2}"
        if odd_id not in events or even_id not in events:
            errors.append(f"{tag}: missing pair {odd_id}/{even_id}")
            continue
        odd_opts = extract_options(events[odd_id])
        even_opts = extract_options(events[even_id])
        if len(odd_opts) != 2:
            errors.append(f"{odd_id}: expected 2 options, found {len(odd_opts)}")
        else:
            if f"id = {even_id}" not in odd_opts[0] or "days =" not in odd_opts[0]:
                errors.append(f"{odd_id}: option A must queue delayed {even_id}")
            if f"custom_tooltip = {odd_id}.result_tt" not in odd_opts[0]:
                errors.append(f"{odd_id}: option A missing result_tt")
            if re.search(r"(?m)^\t\ttrigger\s*=", odd_opts[1]):
                errors.append(f"{odd_id}: option B fallback must not have blocking trigger")
        if len(even_opts) != 1:
            errors.append(f"{even_id}: expected 1 option, found {len(even_opts)}")

    if "government_power" in ev_text:
        for bm in re.finditer(r"(?:add|has)_government_power\s*=\s*\{", ev_text):
            sub = ev_text[bm.start() : matching_brace(ev_text, bm.end() - 1) + 1]
            if (
                "mechanic_type = ottoman_decadence_mechanic" not in sub
                or "power_type = ottoman_decadence" not in sub
            ):
                errors.append(f"{tag}: malformed ottoman_decadence block: {sub}")

    return list(decisions.keys()), errors


def parse_loc_file(lang: str) -> tuple[bytes, dict[str, str]]:
    path = ROOT / "localisation" / f"RIP_shared_ruthenian_neighbor_events_l_{lang}.yml"
    raw = path.read_bytes()
    text = raw.decode("utf-8-sig")
    entries = dict(re.findall(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', text, re.M))
    return raw, entries


def check_english_glossary_text(text: str) -> list[str]:
    violations: list[str] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        m = check_glossary.ENTRY.match(line)
        if not m or m.group(1) in check_glossary.SKIP_KEYS:
            continue
        val = check_glossary.BRACKET.sub("", m.group(3))
        for pat, want in check_glossary.BANNED_SPELLING:
            hit = re.search(pat, val)
            if hit:
                violations.append(f"L{line_no} {m.group(1)}: {hit.group(0)!r} -> {want}")
        for pat, want in check_glossary.BANNED_REGISTER:
            hit = re.search(pat, val, re.I)
            if hit:
                violations.append(f"L{line_no} {m.group(1)}: {hit.group(0)!r} -> {want}")
    return violations


def expected_loc_keys(all_decisions: list[str]) -> set[str]:
    keys: set[str] = set()
    for dec in all_decisions:
        keys.add(f"{dec}_title")
        keys.add(f"{dec}_desc")
    for ns, count in TAG_FAMILIES.values():
        for i in range(count):
            odd = i * 2 + 1
            even = i * 2 + 2
            keys.update(
                {
                    f"{ns}.{odd}.t",
                    f"{ns}.{odd}.d",
                    f"{ns}.{odd}.a",
                    f"{ns}.{odd}.result_tt",
                    f"{ns}.{odd}.b",
                    f"{ns}.{even}.t",
                    f"{ns}.{even}.d",
                    f"{ns}.{even}.a",
                }
            )
    for mod in COUNTRY_MODS | PROVINCE_MODS:
        keys.add(mod)
        keys.add(f"desc_{mod}")
    return keys


def check_no_vanilla_overrides() -> None:
    for fn in VANILLA_EVENT_NO_OVERRIDE:
        assert not (ROOT / "events" / fn).exists(), f"unexpected override events/{fn}"
    for fn in VANILLA_DECISION_NO_OVERRIDE:
        assert not (ROOT / "decisions" / fn).exists(), f"unexpected override decisions/{fn}"
    if (ROOT / ".git").exists():
        res = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--", "events/WomenInHistory.txt"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert not res.stdout.strip(), f"events/WomenInHistory.txt should remain unmodified: {res.stdout}"


def check_modifiers(all_event_texts: str) -> None:
    mod_text = read("common/event_modifiers/RIP_neighbor_ruthenian_events_modifiers.txt")
    defined = set(re.findall(r"(?m)^([a-z0-9_]+)\s*=\s*\{", mod_text))
    expected = COUNTRY_MODS | PROVINCE_MODS
    assert defined == expected, f"modifier mismatch: missing={expected - defined}, extra={defined - expected}"
    for m in COUNTRY_MODS:
        assert f"name = {m}" in all_event_texts, f"unused country modifier {m}"
        assert not re.search(rf"add_province_modifier\s*=\s*\{{\s*name\s*=\s*{m}\b", all_event_texts), m
    for m in PROVINCE_MODS:
        assert f"name = {m}" in all_event_texts, f"unused province modifier {m}"
        assert not re.search(rf"add_country_modifier\s*=\s*\{{\s*name\s*=\s*{m}\b", all_event_texts), m


def test_planted_regressions(eng_entries: dict[str, str], all_decisions: list[str]) -> None:
    # 1. Missing follow-up event + blocking fallback Option B trigger
    broken_dec = """country_decisions = {
\trip_fake_branch = {
\t\tpotential = { tag = TUR NOT = { has_country_flag = rip_fake_branch_heard } }
\t\tallow = { always = yes }
\t\teffect = { set_country_flag = rip_fake_branch_heard country_event = { id = rip_fake.1 } }
\t}
}"""
    broken_ev = """namespace = rip_fake
country_event = {
\tid = rip_fake.1
\ttitle = rip_fake.1.t
\tdesc = rip_fake.1.d
\tpicture = COURT_eventPicture
\tis_triggered_only = yes
\toption = {
\t\tname = rip_fake.1.a
\t\tcustom_tooltip = rip_fake.1.result_tt
\t\tcountry_event = { id = rip_fake.2 days = 180 }
\t}
\toption = {
\t\tname = rip_fake.1.b
\t\ttrigger = { adm_power = 50 }
\t}
}"""
    _, errs = validate_family("TUR", "rip_fake", 1, broken_dec, broken_ev)
    assert any("missing pair rip_fake.1/rip_fake.2" in e for e in errs), (
        f"Failed to catch missing follow-up event: {errs}"
    )
    broken_ev_with_2 = broken_ev + """
country_event = {
\tid = rip_fake.2
\ttitle = rip_fake.2.t
\tdesc = rip_fake.2.d
\tpicture = COURT_eventPicture
\tis_triggered_only = yes
\toption = { name = rip_fake.2.a }
}"""
    _, errs2 = validate_family("TUR", "rip_fake", 1, broken_dec, broken_ev_with_2)
    assert any("blocking trigger" in e for e in errs2), (
        f"Failed to catch Option B blocking trigger: {errs2}"
    )

    # 2. Planted glossary regression + missing loc key
    glossary_errs = check_english_glossary_text(' fake_key:0 "Envoys from Istanbul crossed the Dnipro."\n')
    assert len(glossary_errs) == 2, f"Failed to catch planted glossary terms: {glossary_errs}"
    dropped = set(expected_loc_keys(all_decisions)) - set(
        k for k in eng_entries if k != "rip_tur_ruthenian.1.a"
    )
    assert "rip_tur_ruthenian.1.a" in dropped, "Failed to detect dropped loc key"


def main() -> int:
    check_no_vanilla_overrides()
    all_decisions: list[str] = []
    all_ev_texts: list[str] = []
    all_errors: list[str] = []

    for tag, (ns, count) in TAG_FAMILIES.items():
        dec_text = read(f"decisions/RIP_{tag}_RuthenianPetitions.txt")
        ev_text = read(f"events/RIP_{tag}_RuthenianPetitions.txt")
        decs, errs = validate_family(tag, ns, count, dec_text, ev_text)
        all_decisions.extend(decs)
        all_ev_texts.append(ev_text)
        all_errors.extend(errs)

    assert not all_errors, "Branch validation errors:\n" + "\n".join(all_errors)
    check_modifiers("\n".join(all_ev_texts))

    expected_keys = expected_loc_keys(all_decisions)
    eng_entries: dict[str, str] = {}
    for lang in LANGUAGES:
        raw, entries = parse_loc_file(lang)
        assert raw.startswith(BOM), f"{lang}: missing UTF-8 BOM"
        assert not raw.startswith(BOM + BOM), f"{lang}: duplicate UTF-8 BOM"
        missing = sorted(expected_keys - set(entries))
        extra = sorted(set(entries) - expected_keys)
        empty = sorted(k for k, v in entries.items() if not v.strip())
        assert not missing, f"{lang}: missing keys: {missing[:10]}"
        assert not extra, f"{lang}: unexpected extra keys: {extra[:10]}"
        assert not empty, f"{lang}: empty keys: {empty[:10]}"
        if lang == "english":
            eng_entries = entries

    eng_text = (ROOT / "localisation" / "RIP_shared_ruthenian_neighbor_events_l_english.yml").read_text(
        encoding="utf-8-sig"
    )
    glossary_hits = check_english_glossary_text(eng_text)
    assert not glossary_hits, "Glossary violations:\n" + "\n".join(glossary_hits)

    test_planted_regressions(eng_entries, all_decisions)
    print(
        f"PASS: 15 neighbor Ruthenian branches ({len(all_decisions)} decisions, "
        f"{len(all_decisions) * 2} events), {len(COUNTRY_MODS | PROVINCE_MODS)} modifiers, "
        f"{len(expected_keys)}x4 EFIGS loc keys verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
