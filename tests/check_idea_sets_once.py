"""Every idea set is defined once in the effective vanilla + mod file set.

RIP's common/ideas/00_country_ideas.txt and zz_group_ideas.txt replace the
vanilla files of the same path, so a set that is also defined in an 01_/zzz_ RIP
file appears twice. The generator tools/build_kyiv_idea_overrides.py cuts such sets
out of the copy; this check fails when one slips back in. It also fails when a set
lists the same idea twice.
"""
import re
import sys
from collections import Counter

from clausewitz_testlib import ROOT, vanilla_root

installed = vanilla_root()
directory = ROOT / "common/ideas"
files = {p.name: p for p in (installed / "common/ideas").glob("*.txt")} if installed else {}
files.update({p.name: p for p in directory.glob("*.txt")})

problems = []
where: dict[str, list[str]] = {}
for name, path in sorted(files.items()):
    text = path.read_bytes().decode("latin-1").replace("\r\n", "\n")
    depth = 0
    current = None
    ideas: Counter = Counter()
    for line in text.split("\n"):
        code = re.sub(r"#.*", "", line)
        if depth == 0:
            match = re.match(r"^\s*([A-Za-z_0-9]+)\s*=\s*\{", code)
            if match:
                current = match.group(1)
                where.setdefault(current, []).append(name)
                ideas = Counter()
        elif depth == 1 and current:
            match = re.match(r"^\s*([A-Za-z_0-9]+)\s*=\s*\{", code)
            if match and match.group(1) not in ("start", "bonus", "trigger", "ai_will_do"):
                ideas[match.group(1)] += 1
                if ideas[match.group(1)] == 2:
                    problems.append(f"{name}: {current} lists idea {match.group(1)} twice")
        depth += code.count("{") - code.count("}")

for group, names in sorted(where.items()):
    if len(names) > 1:
        problems.append(f"{group} is defined in {', '.join(names)}")

if problems:
    print("IDEA SET CHECK: FAIL")
    for item in problems:
        print("  -", item)
    sys.exit(1)
print(f"IDEA SET CHECK: PASS ({len(where)} idea sets, each defined once, no idea listed twice in a set)")
