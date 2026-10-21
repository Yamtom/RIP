"""Country/family layout and formatting for RIP defined_text generators.

Each defined_text stays intact: its name, random setting and ordered text
branches are engine contracts. Only whole definitions move between files.
"""
import re
from collections import defaultdict

TOKEN = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')


def code_tokens(text):
    return [m[0] for m in TOKEN.finditer(text) if not m[0].startswith("#")]


def definitions(text):
    """Yield (name, source including leading comments) in original order."""
    entries = list(TOKEN.finditer(text))
    start = 0
    i = 0
    while i < len(entries):
        if entries[i][0].startswith("#"):
            i += 1
            continue
        assert [m[0] for m in entries[i:i + 3]] == ["defined_text", "=", "{"]
        depth = 1
        j = i + 3
        while depth:
            token = entries[j][0]
            depth += (token == "{") - (token == "}")
            j += 1
        end = entries[j - 1].end()
        body = text[start:end]
        name = re.search(r"\bname\s*=\s*(\w+)", body)[1]
        yield name, body
        start = end
        i = j
    assert not code_tokens(text[start:]), "Unexpected trailing code"


def format_script(text):
    entries = [m[0] for m in TOKEN.finditer(text)]
    lines = []
    pos = 0

    def block(depth):
        nonlocal pos
        while pos < len(entries):
            key = entries[pos]
            if key.startswith("#"):
                lines.append("\t" * depth + key.rstrip())
                pos += 1
                continue
            if key == "}":
                assert depth > 0
                pos += 1
                return
            assert entries[pos + 1] == "=", (key, entries[pos:pos + 4])
            value = entries[pos + 2]
            pos += 3
            if depth == 0 and lines:
                lines.append("")
            lines.append("\t" * depth + key + " = " + value)
            if value == "{":
                block(depth + 1)
                lines.append("\t" * depth + "}")
        assert depth == 0

    block(0)
    result = "\n".join(lines) + "\n"
    assert code_tokens(text) == code_tokens(result)
    return result


def owner(family, name):
    if family == "identity":
        for tag in ("UZH", "CHR", "ZAZ", "HET"):
            if name.startswith("Get" + tag):
                return tag
    elif family == "government_status":
        if name.startswith(("RipGovRada", "RipGovJunior", "RipGovDecadence")) or name in {
            "RipGovStabZero", "RipGovStabBad", "RipGovWar", "RipGovLoans",
            "RipGovAutonomy", "RipGovLegitimacy", "RipGovStabGood", "RipGovPeace",
        }:
            return "KRU"
        if name.startswith("Cesar") or name in {
            "RipGovMinorityShare", "RipGovExcludedShare", "RipGovIntegration", "RipGovBreakdown",
        }:
            return "KIE"
        if name.startswith(("RipGovHlc", "RipGovOrd")):
            return "HLC"
        if name.startswith("RipGovLit"):
            return "LIT"
        if name.startswith("RipGovVln"):
            return "VLN"
        if name.startswith("RipGovRes"):
            return "shared"
    elif family == "church":
        if name in {"GetChurchAuthorityReadout", "GetChurchAuthorityTooltip", "GetChurchAuthorityHeading"}:
            return "shared"
        if name.startswith(("GetChurchRO", "GetRipRo", "GetChurchIcon")):
            return "MOS_RUS"
        if name.startswith("GetChurch"):
            return "shared_greek_catholic"
    elif family in {"cossack_host_names", "cossack_host_dynamic_names", "parliament_names"}:
        return "shared"
    elif family in {"old_believer_institutions", "holy_cities"}:
        return "MOS_RUS"
    raise ValueError(f"Classify new custom-localisation definition: {family}/{name}")


def split_custom_localization(text, family):
    groups = defaultdict(list)
    seen = set()
    for name, body in definitions(text):
        assert name not in seen, name
        seen.add(name)
        groups[owner(family, name)].append(body.strip())
    result = {}
    for country, bodies in groups.items():
        header = (
            f"# RIP - {country}; {family}.\n"
            "# Country labels identify the content family, not additional eligibility gates.\n"
            "# Whole definitions are grouped here; keep each text-branch order and random setting.\n"
        )
        result[f"customizable_localization/RIP_{country}_{family}.txt"] = (
            header + format_script("\n\n".join(bodies))
        )
    return result
