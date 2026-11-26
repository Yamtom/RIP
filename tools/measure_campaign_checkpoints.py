"""Read the state of the RIP region from uncompressed EU4 1.37.5 observer saves."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from clausewitz_testlib import _mask_comments_and_strings, matching_brace

TAG = rb"[A-Z0-9]{3}"
DEFAULT_TAGS = "KIE KRU UKR ZAZ HET POL LIT PLC MOS RUS HLC VLN PDL PRL CHR UZH MOL"
START_LINE = re.compile(rb'(?m)^date=(\d+\.\d+\.\d+)\r?$')
FORT_MAINTENANCE_INDEX = 8  # rakaly/eu4save, Query.expense_ledger_breakdown
PAID_PROJECTS = {
    "dniester_estuary_developed": "dniester_trade_network",
    "dniester_estuary_fortified": "dniester_defensive_network",
    "rip_dniester_accord_signed": "rip_dniester_accord_reward",
    "rip_hadiach_accord_signed": "rip_hadiach_accord_reward",
    "rip_kyiv_accord_signed": "rip_kyiv_accord_reward",
}
INDEPENDENT_DEPENDENCIES = {"tributary_state", "trade_protectorate"}


def records(data, key, depth):
    """Yield the body and key of blocks written at this EU4 save indentation."""
    indent = b"\t" * depth
    opening = re.compile(rb"(?m)^" + indent + rb"(" + key + rb")=\{\r?\n")
    closing = re.compile(rb"(?m)^" + indent + rb"}\r?$")
    for match in opening.finditer(data):
        end = closing.search(data, match.end())
        if end is None:
            raise ValueError(f"Incomplete {match[1].decode()} block")
        yield match[1].decode(), data[match.end():end.start()]


def provinces(data):
    # Unlike all other sections, the province header and its closing brace
    # can have different indentation. The next numbered header ends a row.
    boundary = re.compile(rb"(?m)^-(\d+)=\{\r?\n")
    first = None
    for match in boundary.finditer(data):
        if first:
            yield int(first[1]), data[first.end():match.start()]
        first = match
    if first:
        yield int(first[1]), data[first.end():]


def section(data, name, depth):
    return next((body for _, body in records(data, name.encode(), depth)), b"")


def field(data, name, depth, default=None):
    pattern = rb"(?m)^" + b"\t" * depth + name.encode() + rb'="?([^"\r\n]+)"?\r?$'
    match = re.search(pattern, data)
    return match[1].decode("cp1252").strip() if match else default


def date_tuple(value):
    return tuple(map(int, value.split(".")))


def nation_modifiers(country):
    result = {}
    for _, mod in records(country, b"modifier", 2):
        name = field(mod, "modifier", 3)
        if name:
            result[name] = field(mod, "date", 3)
    return result


def efficiency_sources(vanilla, mod):
    """Index unconditional administrative efficiency from engine definitions."""
    value_pattern = re.compile(r"\badministrative_efficiency\s*=\s*(-?\d+(?:\.\d+)?)")
    result = {}
    definition = re.compile(r"(?m)^([a-zA-Z0-9_]+)\s*=\s*\{")
    end_definition = re.compile(r"(?m)^}")
    for family in ("event_modifiers", "government_reforms"):
        files = {file.name: file for root in (vanilla, mod) for file in sorted((root / "common" / family).glob("*.txt"))}
        for file in files.values():
            data = file.read_text(encoding="utf-8-sig", errors="replace")
            if "administrative_efficiency" not in data:
                continue
            masked = _mask_comments_and_strings(data)
            for match in definition.finditer(masked):
                opening = match.end() - 1
                end = end_definition.search(masked, opening + 1)
                if not end:
                    continue
                body = masked[opening + 1:end.start()]
                if family == "event_modifiers":
                    modifier = body
                else:
                    block = re.search(r"(?m)^[\t ]modifiers\s*=\s*\{", body)
                    if not block:
                        continue
                    opening = block.end() - 1
                    modifier = body[opening + 1:matching_brace(body, opening)]
                amount = value_pattern.search(modifier)
                if amount:
                    result[match[1]] = float(amount[1])
    return result


def measure(path, tags, sources):
    data = path.read_bytes()
    if not data.startswith(b"EU4txt"):
        raise ValueError(f"{path}: expected an uncompressed EU4txt save")
    match = START_LINE.search(data[:8192])
    if not match:
        raise ValueError(f"{path}: no checkpoint date")
    date = match[1].decode()
    province_data = section(data, "provinces", 0)
    countries = section(data, "countries", 0)
    diplomacy = section(data, "diplomacy", 0)
    if not all((province_data, countries, diplomacy)):
        raise ValueError(f"{path}: missing campaign sections")
    development = defaultdict(float)
    province_owners = {}
    for pid, province in provinces(province_data):
        owner = field(province, "owner", 2)
        if owner:
            province_owners[pid] = owner
            development[owner] += sum(
                float(field(province, f"base_{kind}", 2, "0"))
                for kind in ("tax", "production", "manpower")
            )

    subjects = defaultdict(set)
    alliances = defaultdict(dict)
    for kind, relation in records(diplomacy, b"dependency|alliance", 1):
        first = field(relation, "first", 2)
        second = field(relation, "second", 2)
        formed = date_tuple(field(relation, "start_date", 2, "1.1.1"))
        ended = date_tuple(field(relation, "end_date", 2, "9999.1.1"))
        if not (first in development and second in development and formed <= date_tuple(date) < ended):
            continue
        if kind == "dependency":
            if field(relation, "subject_type", 2) not in INDEPENDENT_DEPENDENCIES:
                subjects[first].add(second)
        else:
            alliances[first][second] = formed
            alliances[second][first] = formed

    country_tags = b"|".join(tag.encode() for tag in tags)
    country_data = dict(records(countries, country_tags, 1))
    dependents = set().union(*subjects.values())
    metrics = []
    for tag in tags:
        country = country_data.get(tag, b"")
        alive = tag in development
        subject_tags = sorted(subjects[tag])
        modifiers = nation_modifiers(country)
        flags = section(country, "flags", 2)
        claimed = {int(pid) for pid in section(country, "claim_provinces", 2).split()}
        budget = section(country, "lastmonthexpensetable", 3).split()
        reforms = re.findall(rb'"([^"]+)"', section(country, "reforms", 4))
        efficiency = None
        if alive and sources is not None:
            permanent = {name for name, expires in modifiers.items() if expires == "-1.1.1"}
            permanent.update(reform.decode() for reform in reforms)
            efficiency = round(100 * sum(sources.get(name, 0.0) for name in permanent), 4)
        metrics.append({
            "tag": tag,
            "survives": alive,
            "sovereign": alive and tag not in dependents,
            "direct_development": round(development.get(tag, 0), 3),
            "subject_development": round(sum(development[subject] for subject in subject_tags), 3),
            "direct_subjects": subject_tags,
            "foreign_owned_claims": sum(pid in province_owners and province_owners[pid] != tag for pid in claimed) if alive else 0,
            "permanent_modifier_and_reform_efficiency_pp": efficiency,
            "monthly_fort_upkeep_ducats": float(budget[FORT_MAINTENANCE_INDEX]) if alive and len(budget) > FORT_MAINTENANCE_INDEX else None,
            "alliances": sorted(alliances[tag]),
            "sovereign_alliances_at_least_five_calendar_years": [
                partner for partner, formed in sorted(alliances[tag].items())
                if tag not in dependents and partner not in dependents
                and date_tuple(date) >= (formed[0] + 5, *formed[1:])
            ],
            "paid_projects": {
                flag: {"paid_since": since, "benefit_active": modifier in modifiers}
                for flag, modifier in PAID_PROJECTS.items()
                if (since := field(flags, flag, 3))
            },
            "last_regional_government_order": field(flags, "rip_rg_used", 3),
            "last_border_watch_order": field(flags, "rip_border_watch_laid", 3),
        })
    return {"date": date, "save": str(path.resolve()), "countries": metrics, "repeat_event_counts": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("saves", nargs="+", type=Path)
    parser.add_argument("--tags", nargs="+", default=DEFAULT_TAGS.split())
    parser.add_argument("--vanilla", type=Path)
    parser.add_argument("--mod", type=Path)
    args = parser.parse_args()
    if any(not re.fullmatch(TAG, tag.encode()) for tag in args.tags):
        parser.error("country tags must be three uppercase characters or digits")
    if (args.vanilla is None) != (args.mod is None):
        parser.error("--vanilla and --mod must be supplied together")
    sources = efficiency_sources(args.vanilla, args.mod) if args.vanilla else None
    print(json.dumps([measure(path, args.tags, sources) for path in args.saves], indent=2))


if __name__ == "__main__":
    main()
