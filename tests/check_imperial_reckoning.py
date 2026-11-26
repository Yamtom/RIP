"""Static contracts for additive Imperial Reckoning abuses, decisions, events, and disasters.

Verifies the 16 branches (5 disasters + 11 decisions, 37 events total) across:
- TUR: 2 disasters + 6 decisions = 8 branches (18 events)
- PLC: 1 disaster  + 3 decisions = 4 branches (9 events)
- RUS: 1 disaster  + 1 decision  = 2 branches (5 events)
- CRI: 1 disaster  + 1 decision  = 2 branches (5 events)

Static only: inspects Clausewitz scripts, GFX, modifiers, and EFIGS localisation;
does not run EU4.
"""
from __future__ import annotations

import re
from pathlib import Path

from clausewitz_testlib import ROOT, matching_brace, read, vanilla_has_sprite, vanilla_root
import check_glossary


BOM = b"\xef\xbb\xbf"
LANGUAGES = ("english", "french", "german", "spanish")

BRANCH_SPEC = {
    "TUR": {
        "namespace": "rip_tur_reckoning",
        "decisions": 6,
        "disasters": (
            ("rip_tur_ruina_scorched_earth", "rip_tur_reckoning.13", "rip_tur_reckoning.14", "rip_tur_reckoning.15"),
            ("rip_tur_captive_galley_revolt", "rip_tur_reckoning.16", "rip_tur_reckoning.17", "rip_tur_reckoning.18"),
        ),
        "events": 18,
    },
    "PLC": {
        "namespace": "rip_plc_reckoning",
        "decisions": 3,
        "disasters": (
            ("rip_plc_bloody_pacification", "rip_plc_reckoning.7", "rip_plc_reckoning.8", "rip_plc_reckoning.9"),
        ),
        "events": 9,
    },
    "RUS": {
        "namespace": "rip_rus_reckoning",
        "decisions": 1,
        "disasters": (
            ("rip_rus_abolition_of_hetmanate", "rip_rus_reckoning.3", "rip_rus_reckoning.4", "rip_rus_reckoning.5"),
        ),
        "events": 5,
    },
    "CRI": {
        "namespace": "rip_cri_reckoning",
        "decisions": 1,
        "disasters": (
            ("rip_cri_yasyr_depopulation_crisis", "rip_cri_reckoning.3", "rip_cri_reckoning.4", "rip_cri_reckoning.5"),
        ),
        "events": 5,
    },
}

PROVINCE_MODS = {
    "rip_tur_seized_parishes",
    "rip_tur_uprooted_quarters",
    "rip_tur_great_flight",
    "rip_plc_folwark_exhaustion",
    "rip_plc_closed_parishes",
    "rip_rus_silenced_presses",
}

COUNTRY_MODS = {
    "rip_tur_pencik_notoriety",
    "rip_tur_ransom_brokerage",
    "rip_tur_coercive_eyalet_rule",
    "rip_tur_podillian_dhimma_charter",
    "rip_tur_harsh_devshirme",
    "rip_tur_devshirme_commutation",
    "rip_tur_surgun_edicts",
    "rip_tur_voluntary_charters",
    "rip_tur_iron_pacification",
    "rip_tur_anatolian_amnesty",
    "rip_tur_danubian_exactions",
    "rip_tur_fixed_danubian_tribute",
    "rip_plc_second_serfdom",
    "rip_plc_capped_corvee",
    "rip_plc_crown_ordinance",
    "rip_plc_regimental_liberties",
    "rip_plc_confessional_coercion",
    "rip_plc_municipal_confession_peace",
    "rip_rus_imperial_uniformity",
    "rip_rus_ruthenian_charters_spared",
    "rip_cri_slave_mart_infamy",
    "rip_cri_reformed_tamga",
}


def parse_top_blocks(text: str) -> dict[str, str]:
    clean = re.sub(r"#[^\n]*", "", text)
    out: dict[str, str] = {}
    for m in re.finditer(r"(?m)^([a-z0-9_]+)\s*=\s*\{", clean):
        out[m.group(1)] = clean[m.start() : matching_brace(clean, m.end() - 1) + 1]
    return out


def parse_decisions(text: str) -> dict[str, str]:
    clean = re.sub(r"#[^\n]*", "", text)
    m = re.search(r"(?m)^country_decisions\s*=\s*\{", clean)
    assert m, "missing country_decisions block"
    body = clean[m.end() - 1 : matching_brace(clean, m.end() - 1) + 1]
    out: dict[str, str] = {}
    for dm in re.finditer(r"(?m)^\t([a-z0-9_]+)\s*=\s*\{", body):
        out[dm.group(1)] = body[dm.start() : matching_brace(body, dm.end() - 1) + 1]
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


def validate_tag_family(
    tag: str,
    spec: dict,
    dec_text: str,
    ev_text: str,
    disaster_blocks: dict[str, str],
    sprite_names: set[str],
) -> tuple[list[str], list[str], dict[str, str]]:
    errors: list[str] = []
    ns = spec["namespace"]
    decisions = parse_decisions(dec_text)
    events = parse_events(ev_text)

    if len(decisions) != spec["decisions"]:
        errors.append(f"{tag}: expected {spec['decisions']} decisions, found {len(decisions)}")
    if len(events) != spec["events"]:
        errors.append(f"{tag}: expected {spec['events']} events, found {len(events)}")

    ns_m = re.search(r"(?m)^namespace\s*=\s*([a-z0-9_]+)", ev_text)
    if not ns_m or ns_m.group(1) != ns:
        errors.append(f"{tag}: expected namespace = {ns}")

    for dec_key, dec_body in decisions.items():
        flag = f"{dec_key}_heard"
        if f"has_country_flag = {flag}" not in dec_body:
            errors.append(f"{dec_key}: missing has_country_flag = {flag}")
        if f"set_country_flag = {flag}" not in dec_body:
            errors.append(f"{dec_key}: missing set_country_flag = {flag}")
        ev_m = re.search(r"country_event\s*=\s*\{\s*id\s*=\s*([a-z0-9_.]+)", dec_body)
        if not ev_m:
            errors.append(f"{dec_key}: missing country_event call")
        elif ev_m.group(1) not in events:
            errors.append(f"{dec_key}: event {ev_m.group(1)} not defined")

    for eid, eblock in events.items():
        if "is_triggered_only = yes" not in eblock:
            errors.append(f"{eid}: missing is_triggered_only = yes")
        pic_m = re.search(r"\bpicture\s*=\s*([A-Za-z0-9_]+)", eblock)
        if not pic_m:
            errors.append(f"{eid}: missing picture")
        elif vanilla_has_sprite(pic_m.group(1)) is False:
            errors.append(f"{eid}: unknown sprite {pic_m.group(1)}")

    # Decision opening/follow-up pairs: .1/.2, .3/.4, ...
    for idx in range(spec["decisions"]):
        odd_id = f"{ns}.{idx * 2 + 1}"
        even_id = f"{ns}.{idx * 2 + 2}"
        if odd_id not in events or even_id not in events:
            errors.append(f"{tag}: missing decision pair {odd_id}/{even_id}")
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
                errors.append(f"{odd_id}: option B must not have blocking trigger")
        if len(even_opts) != 1:
            errors.append(f"{even_id}: expected 1 option, found {len(even_opts)}")

    # Disaster hooks & events: start, pulse, end
    for did, start_id, pulse_id, end_id in spec["disasters"]:
        if did not in disaster_blocks:
            errors.append(f"{tag}: missing disaster {did}")
            continue
        dblock = disaster_blocks[did]
        if f"GFX_disaster_{did}" not in sprite_names:
            errors.append(f"{did}: missing GFX_disaster_{did} sprite")
        if f"survived_{did}" not in dblock:
            errors.append(f"{did}: missing survived_{did} gate in potential")
        if f"on_start = {start_id}" not in dblock:
            errors.append(f"{did}: missing on_start = {start_id}")
        if f"on_end = {end_id}" not in dblock:
            errors.append(f"{did}: missing on_end = {end_id}")
        if pulse_id not in dblock:
            errors.append(f"{did}: missing on_monthly event {pulse_id}")
        for req_ev in (start_id, pulse_id, end_id):
            if req_ev not in events:
                errors.append(f"{did}: disaster event {req_ev} not defined")
        if start_id in events and len(extract_options(events[start_id])) != 2:
            errors.append(f"{start_id}: expected 2 options")
        if pulse_id in events and len(extract_options(events[pulse_id])) != 2:
            errors.append(f"{pulse_id}: expected 2 options")
        if end_id in events:
            eblock = events[end_id]
            if len(extract_options(eblock)) != 1:
                errors.append(f"{end_id}: expected 1 option")
            if f"set_country_flag = survived_{did}" not in eblock:
                errors.append(f"{end_id}: missing set_country_flag = survived_{did}")

    return list(decisions.keys()), errors, events


def parse_gfx_sprites(gfx_text: str) -> tuple[set[str], list[str]]:
    names = set(re.findall(r'name\s*=\s*"([^"]+)"', gfx_text))
    textures = re.findall(r'texturefile\s*=\s*"([^"]+)"', gfx_text)
    return names, textures


def check_english_glossary_and_tone(text: str) -> list[str]:
    violations: list[str] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        m = check_glossary.ENTRY.match(line)
        if not m or m.group(1) in check_glossary.SKIP_KEYS:
            continue
        key = m.group(1)
        val = check_glossary.BRACKET.sub("", m.group(3))
        for pat, want in check_glossary.BANNED_SPELLING:
            hit = re.search(pat, val)
            if hit:
                violations.append(f"L{line_no} {key}: {hit.group(0)!r} -> {want}")
        for pat, want in check_glossary.BANNED_REGISTER:
            hit = re.search(pat, val, re.I)
            if hit:
                violations.append(f"L{line_no} {key}: {hit.group(0)!r} -> {want}")
        if (key.endswith(".d") or key.endswith("_desc")) and "!" in val:
            violations.append(f"L{line_no} {key}: exclamation mark forbidden in prose")
    return violations


def expected_loc_keys(all_decisions: list[str]) -> set[str]:
    keys: set[str] = set()
    for dec in all_decisions:
        keys.add(f"{dec}_title")
        keys.add(f"{dec}_desc")
    for spec in BRANCH_SPEC.values():
        ns = spec["namespace"]
        for i in range(spec["decisions"]):
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
        for did, start_id, pulse_id, end_id in spec["disasters"]:
            keys.update({did, f"{did}_title", f"{did}_desc", f"desc_{did}"})
            for eid in (start_id, pulse_id):
                keys.update({f"{eid}.t", f"{eid}.d", f"{eid}.a", f"{eid}.b"})
            keys.update({f"{end_id}.t", f"{end_id}.d", f"{end_id}.a"})
    for mod in PROVINCE_MODS | COUNTRY_MODS:
        keys.add(mod)
        keys.add(f"desc_{mod}")
    return keys


def check_modifiers(all_event_texts: str) -> None:
    mod_text = read("common/event_modifiers/RIP_imperial_reckoning_modifiers.txt")
    defined = set(re.findall(r"(?m)^([a-z0-9_]+)\s*=\s*\{", mod_text))
    expected = PROVINCE_MODS | COUNTRY_MODS
    assert defined == expected, f"modifier mismatch: missing={expected - defined}, extra={defined - expected}"
    for m in COUNTRY_MODS:
        assert f"name = {m}" in all_event_texts, f"unused country modifier {m}"
        assert not re.search(rf"add_province_modifier\s*=\s*\{{\s*name\s*=\s*{m}\b", all_event_texts), m
    for m in PROVINCE_MODS:
        assert f"name = {m}" in all_event_texts, f"unused province modifier {m}"
        assert not re.search(rf"add_country_modifier\s*=\s*\{{\s*name\s*=\s*{m}\b", all_event_texts), m


def test_planted_regressions(
    disaster_blocks: dict[str, str],
    eng_entries: dict[str, str],
    all_decisions: list[str],
) -> None:
    # 1. Missing disaster sprite + missing survived_<id> flag in on_end
    fake_spec = {
        "namespace": "rip_fake_reckoning",
        "decisions": 0,
        "disasters": (("rip_fake_crisis", "rip_fake_reckoning.1", "rip_fake_reckoning.2", "rip_fake_reckoning.3"),),
        "events": 3,
    }
    fake_dec = "country_decisions = {\n}"
    fake_ev = """namespace = rip_fake_reckoning
country_event = {
\tid = rip_fake_reckoning.1
\ttitle = rip_fake_reckoning.1.t
\tdesc = rip_fake_reckoning.1.d
\tpicture = COURT_eventPicture
\tis_triggered_only = yes
\toption = { name = rip_fake_reckoning.1.a }
\toption = { name = rip_fake_reckoning.1.b }
}
country_event = {
\tid = rip_fake_reckoning.2
\ttitle = rip_fake_reckoning.2.t
\tdesc = rip_fake_reckoning.2.d
\tpicture = COURT_eventPicture
\tis_triggered_only = yes
\toption = { name = rip_fake_reckoning.2.a }
\toption = { name = rip_fake_reckoning.2.b }
}
country_event = {
\tid = rip_fake_reckoning.3
\ttitle = rip_fake_reckoning.3.t
\tdesc = rip_fake_reckoning.3.d
\tpicture = COURT_eventPicture
\tis_triggered_only = yes
\toption = { name = rip_fake_reckoning.3.a }
}"""
    fake_dis = {
        "rip_fake_crisis": """rip_fake_crisis = {
\tpotential = { NOT = { has_country_flag = survived_rip_fake_crisis } }
\ton_start = rip_fake_reckoning.1
\ton_end = rip_fake_reckoning.3
\ton_monthly = { random_events = { 1000 = 0 120 = rip_fake_reckoning.2 } }
}"""
    }
    _, errs, _ = validate_tag_family("TUR", fake_spec, fake_dec, fake_ev, fake_dis, set())
    assert any("missing GFX_disaster_rip_fake_crisis sprite" in e for e in errs), errs
    assert any("missing set_country_flag = survived_rip_fake_crisis" in e for e in errs), errs

    # 2. Glossary violation + exclamation mark in English prose + dropped loc key
    tone_errs = check_english_glossary_and_tone(
        ' fake.1.d:0 "Istanbul raiders struck Kiev across the Dnipro!"\n'
    )
    assert len(tone_errs) == 4, f"Expected 3 glossary hits + 1 tone hit, got {tone_errs}"
    dropped = set(expected_loc_keys(all_decisions)) - set(
        k for k in eng_entries if k != "rip_tur_reckoning.1.a"
    )
    assert "rip_tur_reckoning.1.a" in dropped, "Failed to detect dropped loc key"


def main() -> int:
    disasters_text = read("common/disasters/rip_imperial_reckoning_disasters.txt")
    disaster_blocks = parse_top_blocks(disasters_text)
    assert len(disaster_blocks) == 5, f"Expected 5 disasters, found {len(disaster_blocks)}"

    gfx_text = read("interface/RIP_shared_disaster_imperial_reckoning.gfx")
    sprite_names, textures = parse_gfx_sprites(gfx_text)
    vroot = vanilla_root()
    if vroot is not None:
        for tex in textures:
            norm = tex.replace("//", "/")
            assert (ROOT / norm).is_file() or (vroot / norm).is_file(), f"missing DDS texture {norm}"

    all_decisions: list[str] = []
    all_ev_texts: list[str] = []
    all_errors: list[str] = []

    for tag, spec in BRANCH_SPEC.items():
        dec_text = read(f"decisions/RIP_{tag}_ImperialAbuses.txt")
        ev_text = read(f"events/RIP_{tag}_ImperialAbuses.txt")
        decs, errs, _ = validate_tag_family(
            tag, spec, dec_text, ev_text, disaster_blocks, sprite_names
        )
        all_decisions.extend(decs)
        all_ev_texts.append(ev_text)
        all_errors.extend(errs)

    assert not all_errors, "Imperial reckoning errors:\n" + "\n".join(all_errors)
    check_modifiers("\n".join(all_ev_texts))

    expected_keys = expected_loc_keys(all_decisions)
    assert len(expected_keys) == 241, f"Expected 241 keys, computed {len(expected_keys)}"

    eng_entries: dict[str, str] = {}
    for lang in LANGUAGES:
        path = ROOT / "localisation" / f"RIP_shared_ruthenian_imperial_reckoning_l_{lang}.yml"
        raw = path.read_bytes()
        assert raw.startswith(BOM), f"{lang}: missing UTF-8 BOM"
        assert not raw.startswith(BOM + BOM), f"{lang}: duplicate UTF-8 BOM"
        text = raw.decode("utf-8-sig")
        entries = dict(re.findall(r'^ ([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$', text, re.M))
        missing = sorted(expected_keys - set(entries))
        extra = sorted(set(entries) - expected_keys)
        empty = sorted(k for k, v in entries.items() if not v.strip())
        assert not missing, f"{lang}: missing keys: {missing[:10]}"
        assert not extra, f"{lang}: extra keys: {extra[:10]}"
        assert not empty, f"{lang}: empty keys: {empty[:10]}"
        if lang == "english":
            eng_entries = entries
            tone_hits = check_english_glossary_and_tone(text)
            assert not tone_hits, "English glossary/tone violations:\n" + "\n".join(tone_hits)

    test_planted_regressions(disaster_blocks, eng_entries, all_decisions)
    print(
        f"PASS: 16 imperial reckoning branches ({len(disaster_blocks)} disasters, "
        f"{len(all_decisions)} decisions, 37 events), {len(PROVINCE_MODS | COUNTRY_MODS)} modifiers, "
        f"{len(expected_keys)}x4 EFIGS loc keys verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
