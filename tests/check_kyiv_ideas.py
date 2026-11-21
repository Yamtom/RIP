"""Check Kyiv's national ideas in the effective vanilla + mod file set."""
import re
from collections import Counter

from clausewitz_testlib import ROOT, named_block, normalized, vanilla_root


installed = vanilla_root()
directory = ROOT / "common/ideas"
files = {p.name: p for p in (installed / "common/ideas").glob("*.txt")} if installed else {}
files.update({p.name: p for p in directory.glob("*.txt")})
source = "\n".join(p.read_bytes().decode("latin-1") for p in files.values())
groups = Counter(re.findall(r"^(\w+)\s*=\s*\{", source, re.M))
for group in ("KIE_ideas", "ruthenian_ideas", "cossack_ideas"):
    assert groups[group] == 1, (group, groups[group])
for group in ("ruthenian_ideas", "cossack_ideas"):
    trigger = normalized(named_block(named_block(source, group), "trigger"))
    assert "NOT = { tag = KIE }" in trigger, group

kyiv = named_block(source, "KIE_ideas")
assert normalized(named_block(kyiv, "trigger")) == "trigger = { tag = KIE }"
slots = re.findall(r"^\t(\w+) = \{", kyiv, re.M)
ideas = [key for key in slots if key not in ("start", "trigger", "bonus")]
assert len(ideas) == len(set(ideas)) == 7
for idea in ideas:
    assert len(re.findall(rf"^\s*{idea}\s*=\s*\{{", source, re.M)) == 1, idea
print("PASS: one Kyiv group, seven unique ideas, both RIP fallback groups exclude Kyiv.")
