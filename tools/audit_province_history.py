"""Compare every RIP province history with vanilla and audit timelines/references.

Read-only unless --output is supplied; never edits engine files.
Parses the full header + dated timeline of all provinces in RIP/history/provinces/
and verifies references, chronological order, cores, controller integrity,
deprecated history syntax, and 1444.11.11 / 1821 states against vanilla.
"""
from __future__ import annotations

import argparse
from collections import Counter
import datetime as dt
import difflib
import hashlib
import json
from pathlib import Path
import re

from audit_country_history import DATE, ROOT, merged, parse, read
from audit_diplomacy_history import date, province_tree

VANILLA_DEFAULT = Path(r"D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV")
EU4_START = dt.date(1444, 11, 11)
EU4_END = dt.date(1821, 1, 2)
EXPECTED_IDENTICAL_FIXTURES = {"300", "301", "4255"}
KNOWN_VANILLA_QUIRKS = {
    # Inherited vanilla quirks outside 1444.11.11 that are deliberately left intact
    "270": {"quoted_religion"},
    "281": {"owner_lacks_core:TUR"},
    "293": {"owner_lacks_core:LIT"},
    "1943": {"owner_lacks_core:TUR"},
    "2959": {"empty_block:1580.1.1"},
    "4242": {"wartime_occupation:1569.7.1:RUS"},
    "4245": {"owner_lacks_core:LIT"},
    "4536": {"quoted_religion"},
    "4540": {"owner_lacks_core:TUR"},
}

CULTURE_META = {
    "graphical_culture", "second_graphical_culture",
    "country", "province", "male_names", "female_names", "dynasty_names",
}
RELIGION_META = {
    "center_of_religion", "flags_with_emblem_percentage",
    "flag_emblem_index_range", "religious_schools",
    "harmonized_modifier", "crusade_name", "defender_of_faith",
    "ai_will_do", "papacy",
}
FORT_KEYS = {"fort_15th", "fort_16th", "fort_17th", "fort_18th"}


def strip_quotes(value: str) -> str:
    """Remove surrounding quotes from a scalar token."""
    return value.strip('"')


def load_definitions(vanilla: Path) -> dict[str, set[str]]:
    """Collect valid tags, cultures, religions, goods, modifiers, buildings, and rebels."""
    tags: set[str] = set()
    for p in merged(vanilla, "common/country_tags"):
        tags.update(k for k, _ in parse(read(p)))

    cultures: set[str] = set()
    for p in merged(vanilla, "common/cultures"):
        for _, gv in province_tree(read(p)):
            if isinstance(gv, list):
                for ck, cv in gv:
                    if ck not in CULTURE_META and isinstance(cv, list):
                        cultures.add(ck)

    religions: set[str] = set()
    for p in merged(vanilla, "common/religions"):
        for _, gv in province_tree(read(p)):
            if isinstance(gv, list):
                for rk, rv in gv:
                    if rk not in RELIGION_META and isinstance(rv, list):
                        religions.add(rk)

    goods = {
        k
        for p in merged(vanilla, "common/tradegoods")
        for k, v in province_tree(read(p))
        if isinstance(v, list)
    }
    buildings = {
        k
        for p in merged(vanilla, "common/buildings")
        for k, v in province_tree(read(p))
        if isinstance(v, list)
    }
    rebels = {
        k
        for p in merged(vanilla, "common/rebel_types")
        for k, v in province_tree(read(p))
        if isinstance(v, list)
    }
    modifiers: set[str] = set()
    for folder in ("common/event_modifiers", "common/triggered_modifiers", "common/province_triggered_modifiers"):
        if (vanilla / folder).is_dir() or (ROOT / folder).is_dir():
            for p in merged(vanilla, folder):
                modifiers.update(k for k, v in province_tree(read(p)) if isinstance(v, list))

    return {
        "tags": tags,
        "cultures": cultures,
        "religions": religions,
        "trade_goods": goods,
        "buildings": buildings,
        "rebels": rebels,
        "modifiers": modifiers,
    }


def parse_prov_filename(path: Path) -> tuple[str, str]:
    """Extract numeric province ID and name suffix from a history filename."""
    m = re.match(r"(\d+)\s*-\s*(.*)", path.stem)
    if not m:
        raise ValueError(f"Unrecognized province filename format: {path.name}")
    return m[1], m[2]


def simulate_province(tree: list, when: dt.date | None = None) -> dict:
    """Evaluate province history sequentially up to `when` (or entire timeline if None)."""
    state = {
        "owner": None,
        "controller": None,
        "culture": None,
        "religion": None,
        "capital": None,
        "trade_goods": None,
        "base_tax": 0,
        "base_production": 0,
        "base_manpower": 0,
        "center_of_trade": 0,
        "hre": "no",
        "is_city": "no",
        "cores": set(),
        "claims": set(),
        "perma_claims": set(),
        "forts": set(),
        "revolt": False,
        "modifiers": set(),
    }

    def apply_items(items: list) -> None:
        for k, v in items:
            if k in ("owner", "controller", "culture", "religion", "trade_goods", "hre", "is_city"):
                state[k] = strip_quotes(v) if isinstance(v, str) else state[k]
            elif k == "capital" and isinstance(v, str):
                state["capital"] = strip_quotes(v)
            elif k in ("base_tax", "base_production", "base_manpower", "center_of_trade") and isinstance(v, str):
                state[k] = int(float(v))
            elif k == "add_core" and isinstance(v, str):
                state["cores"].add(v)
            elif k == "remove_core" and isinstance(v, str):
                state["cores"].discard(v)
            elif k == "add_claim" and isinstance(v, str):
                state["claims"].add(v)
            elif k == "remove_claim" and isinstance(v, str):
                state["claims"].discard(v)
            elif k == "add_permanent_claim" and isinstance(v, str):
                state["perma_claims"].add(v)
            elif k == "remove_permanent_claim" and isinstance(v, str):
                state["perma_claims"].discard(v)
            elif k in FORT_KEYS and isinstance(v, str):
                if v == "yes":
                    state["forts"].add(k)
                elif v == "no":
                    state["forts"].discard(k)
            elif k == "revolt" and isinstance(v, list):
                state["revolt"] = len(v) > 0
            elif k in ("add_permanent_province_modifier", "add_province_modifier") and isinstance(v, list):
                mname = dict((ik, iv) for ik, iv in v if isinstance(iv, str)).get("name")
                if mname:
                    state["modifiers"].add(strip_quotes(mname))
            elif k == "remove_province_modifier" and isinstance(v, str):
                state["modifiers"].discard(strip_quotes(v))

    header_items = [(k, v) for k, v in tree if not DATE.fullmatch(k)]
    apply_items(header_items)

    for k, v in tree:
        if not DATE.fullmatch(k) or not isinstance(v, list):
            continue
        d = date(k)
        if when is not None and d > when:
            break
        apply_items(v)

    state["dev"] = state["base_tax"] + state["base_production"] + state["base_manpower"]
    return state


def audit_province(pid: str, name: str, rip_path: Path, van_path: Path | None, defs: dict[str, set[str]]) -> dict:
    """Run all comparison and structural/timeline checks on one RIP province file."""
    rip_text = read(rip_path)
    rip_tree = province_tree(rip_text)
    van_text = read(van_path) if van_path and van_path.exists() else ""
    van_tree = province_tree(van_text) if van_path and van_path.exists() else None

    if van_tree is None:
        status = "addition"
    elif rip_tree == van_tree:
        status = "identical"
    else:
        status = "override"

    van_only_syntax: set[str] = set()
    if van_tree is not None:
        for k, v in van_tree:
            if k == "religion" and isinstance(v, str) and v.startswith('"'):
                van_only_syntax.add("quoted_religion")
            if DATE.fullmatch(k) and isinstance(v, list) and len(v) == 0:
                van_only_syntax.add(f"empty_block:{k}")

    errors: list[str] = []
    warnings: list[str] = []

    if van_path is None:
        errors.append(f"{pid} ({rip_path.name}): no matching vanilla province file")
    elif van_path.name != rip_path.name:
        errors.append(f"{pid} ({rip_path.name}): filename differs from vanilla {van_path.name}")

    # Walk header + timeline tracking exact chronology & core state
    prev_date: dt.date | None = None
    seen_dates: set[str] = set()
    cores: set[str] = set()
    forts: set[str] = set()
    owner: str | None = None
    controller: str | None = None
    revolt_active = False

    def validate_items(items: list, ctx: str, in_date: dt.date | None) -> None:
        nonlocal owner, controller, revolt_active
        for k, v in items:
            if k == "estate":
                errors.append(f"{pid} ({name})@{ctx}: deprecated 'estate = {v}'")
            elif k == "set_local_autonomy":
                errors.append(f"{pid} ({name})@{ctx}: non-vanilla 'set_local_autonomy = {v}' (use add_local_autonomy)")
            elif k == "add_province_modifier" and isinstance(v, list):
                kv = dict((ik, iv) for ik, iv in v if isinstance(iv, str))
                if kv.get("duration") == "-1":
                    errors.append(
                        f"{pid} ({name})@{ctx}: permanent modifier '{kv.get('name')}' uses add_province_modifier instead of add_permanent_province_modifier"
                    )
            elif k == "latent_trade_goods" and isinstance(v, list):
                for gk, gv in v:
                    g = strip_quotes(gk) if gv is None else strip_quotes(gv)
                    if g not in defs["trade_goods"]:
                        errors.append(f"{pid} ({name})@{ctx}: unknown latent trade good '{g}'")

            if isinstance(v, list):
                if k in ("add_permanent_province_modifier", "add_province_modifier"):
                    mname = dict((ik, iv) for ik, iv in v if isinstance(iv, str)).get("name", "")
                    mname = strip_quotes(mname)
                    if not mname or mname not in defs["modifiers"]:
                        errors.append(f"{pid} ({name})@{ctx}: unknown modifier '{mname}'")
                elif k == "revolt":
                    revolt_active = len(v) > 0
                    rtype = dict((ik, iv) for ik, iv in v if isinstance(iv, str)).get("type")
                    if rtype and rtype not in defs["rebels"]:
                        errors.append(f"{pid} ({name})@{ctx}: unknown rebel type '{rtype}'")
                continue

            if not isinstance(v, str):
                continue
            val = strip_quotes(v)
            if k in ("owner", "controller", "add_core", "remove_core", "add_claim", "remove_claim", "add_permanent_claim", "remove_permanent_claim"):
                if not (k == "controller" and val == "REB") and val not in defs["tags"]:
                    errors.append(f"{pid} ({name})@{ctx}: unknown tag {k} = {val}")
            elif k == "culture":
                if val not in defs["cultures"]:
                    errors.append(f"{pid} ({name})@{ctx}: unknown culture '{val}'")
            elif k == "religion":
                if val not in defs["religions"]:
                    errors.append(f"{pid} ({name})@{ctx}: unknown religion '{val}'")
                if v.startswith('"') and "quoted_religion" not in van_only_syntax:
                    warnings.append(f"{pid} ({name})@{ctx}: quoted religion {v}")
            elif k == "trade_goods":
                if val not in defs["trade_goods"]:
                    errors.append(f"{pid} ({name})@{ctx}: unknown trade good '{val}'")
            elif k == "remove_province_modifier":
                if val not in defs["modifiers"]:
                    errors.append(f"{pid} ({name})@{ctx}: unknown modifier in remove_province_modifier '{val}'")
            elif v == "yes" and k not in FORT_KEYS and k not in {"hre", "is_city", "revolt", "discovered_by"}:
                if k not in defs["buildings"] and not k.endswith("_triggered_modifier"):
                    warnings.append(f"{pid} ({name})@{ctx}: non-building flag {k} = yes")

            # Timeline state invariants
            if k == "add_core":
                cores.add(val)
            elif k == "remove_core":
                if val not in cores:
                    errors.append(f"{pid} ({name})@{ctx}: remove_core = {val} when core not active")
                cores.discard(val)
            elif k == "owner":
                prev_owner = owner
                owner = val
                # Transfer of ownership leaving previous third-party occupier in control without new controller assignment
                if prev_owner and prev_owner != owner and controller and controller not in (owner, "REB") and not any(ik == "controller" for ik, _ in items):
                    if not revolt_active:
                        note = f"wartime_occupation:{ctx}:{controller}"
                        if note in KNOWN_VANILLA_QUIRKS.get(pid, set()):
                            warnings.append(f"{pid} ({name})@{ctx}: owner changed to {owner} during inherited wartime occupation by {controller}")
                        else:
                            errors.append(f"{pid} ({name})@{ctx}: owner changed to {owner} while lingering controller stays {controller}")
            elif k == "controller":
                controller = val
            elif k in FORT_KEYS:
                if val == "yes":
                    forts.add(k)
                elif val == "no":
                    if k not in forts and in_date is not None:
                        errors.append(f"{pid} ({name})@{ctx}: {k} = no when fort not present")
                    forts.discard(k)

        if in_date is not None and owner and owner not in cores:
            issue = f"{pid} ({name})@{ctx}: owner {owner} lacks core"
            if f"owner_lacks_core:{owner}" in KNOWN_VANILLA_QUIRKS.get(pid, set()) and in_date != EU4_START:
                warnings.append(f"{issue} (inherited vanilla quirk)")
            else:
                errors.append(issue)

    header_items = [(k, v) for k, v in rip_tree if not DATE.fullmatch(k)]
    validate_items(header_items, "header", None)
    if owner and owner not in cores:
        errors.append(f"{pid} ({name})@header: owner {owner} lacks core")

    for k, v in rip_tree:
        if not DATE.fullmatch(k):
            continue
        if not isinstance(v, list):
            errors.append(f"{pid} ({name})@{k}: dated entry is not a block")
            continue
        try:
            cur_date = date(k)
        except ValueError as exc:
            errors.append(f"{pid} ({name})@{k}: invalid date ({exc})")
            continue
        if cur_date > EU4_END:
            errors.append(f"{pid} ({name})@{k}: post-1821 date beyond EU4 timeline")
        if k in seen_dates:
            errors.append(f"{pid} ({name})@{k}: duplicate dated block")
        seen_dates.add(k)
        if prev_date and cur_date < prev_date:
            errors.append(f"{pid} ({name})@{k}: out-of-order date after {prev_date.isoformat()}")
        prev_date = cur_date
        if len(v) == 0 and f"empty_block:{k}" not in KNOWN_VANILLA_QUIRKS.get(pid, set()):
            errors.append(f"{pid} ({name})@{k}: empty dated block {{}}")
        validate_items(v, k, cur_date)

    # Check 1444.11.11 & 1821 end states
    s1444 = simulate_province(rip_tree, EU4_START)
    s1821 = simulate_province(rip_tree, EU4_END)
    v1444 = simulate_province(van_tree, EU4_START) if van_tree is not None else None

    if s1444["owner"] not in s1444["cores"]:
        errors.append(f"{pid} ({name})@1444.11.11: owner {s1444['owner']} lacks core")
    if s1444["controller"] != s1444["owner"]:
        errors.append(f"{pid} ({name})@1444.11.11: controller {s1444['controller']} != owner {s1444['owner']}")
    if s1821["controller"] != s1821["owner"]:
        errors.append(f"{pid} ({name})@1821: controller {s1821['controller']} != owner {s1821['owner']} (lingering occupation/revolt)")

    if status == "identical" and pid not in EXPECTED_IDENTICAL_FIXTURES:
        errors.append(f"{pid} ({rip_path.name}): zero-diff override identical to vanilla")

    return {
        "pid": pid,
        "name": name,
        "filename": rip_path.name,
        "rip_path": rip_path,
        "van_path": van_path,
        "rip_text": rip_text,
        "van_text": van_text,
        "status": status,
        "rip_1444": s1444,
        "van_1444": v1444,
        "rip_1821": s1821,
        "dated_blocks": sum(1 for k, v in rip_tree if DATE.fullmatch(k) and isinstance(v, list)),
        "errors": errors,
        "warnings": warnings,
    }


def collect_audit(vanilla: Path) -> tuple[str, list[dict], list[str], list[str]]:
    """Audit all RIP province histories against `vanilla` and return version, rows, errors, warnings."""
    v = vanilla.resolve()
    if re.search(r'replace_path\s*=\s*"history(?:/provinces)?"', read(ROOT / "descriptor.mod")):
        raise RuntimeError("replace_path changes history/provinces merging; update auditor first")
    if not (v / "history/provinces").is_dir():
        raise FileNotFoundError(f"Missing vanilla history/provinces in {v}")

    version = json.loads((v / "launcher-settings.json").read_text(encoding="utf-8-sig"))["version"]
    defs = load_definitions(v)

    vanilla_by_id: dict[str, Path] = {}
    for vp in (v / "history/provinces").glob("*.txt"):
        m = re.match(r"(\d+)\s*-\s*", vp.name)
        if m:
            vanilla_by_id[m[1]] = vp

    results = []
    all_errors: list[str] = []
    all_warnings: list[str] = []

    rip_files = sorted(
        (ROOT / "history/provinces").glob("*.txt"),
        key=lambda p: (int(parse_prov_filename(p)[0]), p.name),
    )
    for p in rip_files:
        pid, name = parse_prov_filename(p)
        res = audit_province(pid, name, p, vanilla_by_id.get(pid), defs)
        results.append(res)
        all_errors.extend(res["errors"])
        all_warnings.extend(res["warnings"])

    return version, results, all_errors, all_warnings


def format_report(version: str, vanilla: Path, results: list[dict], errors: list[str], warnings: list[str]) -> str:
    """Render docs/PROVINCE_VANILLA_COMPARISON.md."""
    counts = Counter(r["status"] for r in results)
    rip_dev_total = sum(r["rip_1444"]["dev"] for r in results)
    van_dev_total = sum(r["van_1444"]["dev"] for r in results if r["van_1444"])
    dev_delta = rip_dev_total - van_dev_total

    owner_counts_1444 = Counter(r["rip_1444"]["owner"] for r in results)
    table_rows = []
    details = []
    dev_rows = []

    for r in results:
        s = r["rip_1444"]
        vs = r["van_1444"]
        v_own = vs["owner"] if vs else "—"
        v_cul = vs["culture"] if vs else "—"
        v_dev = str(vs["dev"]) if vs else "—"
        delta = f"{s['dev'] - vs['dev']:+d}" if vs else "—"
        cot = f"{s['center_of_trade']}" if s["center_of_trade"] else "—"
        v_cot = f"{vs['center_of_trade']}" if (vs and vs["center_of_trade"]) else "—"
        cot_str = cot if cot == v_cot else f"{v_cot}->{cot}"
        cores_str = ",".join(sorted(s["cores"]))
        table_rows.append(
            f"| {r['pid']} | {r['filename']} | {r['status']} | {v_own} -> {s['owner']} | "
            f"{v_cul} -> {s['culture']} | {s['religion']} | {v_dev} -> {s['dev']} ({delta}) | "
            f"{s['trade_goods']} | {cot_str} | {cores_str} | {r['dated_blocks']} |"
        )
        if vs and s["dev"] != vs["dev"]:
            dev_rows.append(
                f"| {r['pid']} | {r['name']} | "
                f"{vs['base_tax']}/{vs['base_production']}/{vs['base_manpower']} ({vs['dev']}) | "
                f"{s['base_tax']}/{s['base_production']}/{s['base_manpower']} ({s['dev']}) | {delta} |"
            )

        details.append(f"### {r['filename']}\n")
        details.append(f"RIP SHA256: `{hashlib.sha256(r['rip_path'].read_bytes()).hexdigest()}`\n")
        if r["van_path"]:
            details.append(f"Vanilla SHA256: `{hashlib.sha256(r['van_path'].read_bytes()).hexdigest()}`\n")
            diff_lines = "".join(
                difflib.unified_diff(
                    r["van_text"].replace("\r\n", "\n").replace("\r", "\n").splitlines(True),
                    r["rip_text"].replace("\r\n", "\n").replace("\r", "\n").splitlines(True),
                    fromfile="vanilla/" + r["van_path"].name,
                    tofile="RIP/" + r["filename"],
                )
            ).rstrip()
            if diff_lines:
                details.append("```diff\n" + diff_lines + "\n```\n")
            else:
                details.append("_No semantic diff from vanilla (retained fixture/override)._\n")

    lines = [
        "# Province history comparison",
        "",
        f"Installed baseline: **{version}**",
        "",
        f"Path: `{vanilla.resolve()}`",
        "",
        f"Reviewed `{len(results)}` RIP province history files: {dict(counts)}.",
        f"Total 1444.11.11 development across reviewed provinces: vanilla **{van_dev_total}** -> RIP **{rip_dev_total}** (**{dev_delta:+d}**).",
        f"1444.11.11 ownership breakdown: {dict(owner_counts_1444.most_common())}.",
        "",
        "Only RIP overrides in `history/provinces/` are compared; unoverridden vanilla provinces inherit vanilla history verbatim.",
        "Identical fixture provinces (`300`, `301`, `4255`) are intentionally retained for `tests/check_culture_key_compatibility.py`.",
        "",
        "| ID | File | Comparison | 1444 Owner (V->RIP) | 1444 Culture (V->RIP) | 1444 Religion | 1444 Dev (V->RIP) | Trade Good | CoT | 1444 Cores | Dated Blocks |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
        *table_rows,
        "",
        f"## Development delta summary ({len(dev_rows)} provinces changed; net {dev_delta:+d})",
        "",
        "| ID | Province | Vanilla Tax/Prod/Man (Total) | RIP Tax/Prod/Man (Total) | Delta |",
        "|---|---|---|---|---|",
        *dev_rows,
        "",
        "## Structural and timeline errors",
        "",
        *(["- " + e for e in errors] or ["No structural errors."]),
        "",
        "## Warnings and retained vanilla quirks",
        "",
        *(["- " + w for w in warnings] or ["No warnings."]),
        "",
        "## Complete override diffs",
        "",
        *details,
    ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    """CLI entrypoint."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vanilla", type=Path, default=VANILLA_DEFAULT)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    version, results, errors, warnings = collect_audit(args.vanilla)
    report = format_report(version, args.vanilla, results, errors, warnings)
    if args.output:
        args.output.write_text(report, encoding="utf-8", newline="\n")
    else:
        print(report)
    counts = Counter(r["status"] for r in results)
    print(f"Reviewed {len(results)} files: {dict(counts)}; {len(errors)} error(s); {len(warnings)} warning(s).")
    for e in errors:
        print("ERROR:", e)
    for w in warnings:
        print("WARN:", w)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
