"""Generate the harness replicas of rip_church_refresh_relations_effect (scratchpad tool)."""
import re, subprocess, sys
S = sys.argv[1]
base = open(S + "/../wt/base/common/scripted_effects/rip_church_diplomacy_effects.txt", encoding="utf-8").read().replace("\r", "")
new = open(S + "/../wt/new/common/scripted_effects/rip_church_diplomacy_effects.txt", encoding="utf-8").read().replace("\r", "")
mods = set()
def make(text, pfx, name):
    out = text.replace("rip_church_refresh_relations_effect", name)
    def rn(m):
        mods.add(m.group(1))
        return "rip_gcr_probe_%s_%s" % (pfx, m.group(1))
    out = re.sub(r"rip_church_opinion_(\w+)", rn, out)
    def addflag(m):
        return m.group(0) + " set_country_flag = rip_gcr_%s_%s" % (pfx, m.group(2))
    out = re.sub(r"add_opinion = \{ who = ROOT modifier = rip_gcr_probe_(\w)_(\w+) \}", lambda m: "add_opinion = { who = ROOT modifier = rip_gcr_probe_%s_%s } set_country_flag = rip_gcr_%s_%s" % (m.group(1), m.group(2), m.group(1), m.group(2)), out)
    return out
n = make(base, "n", "rip_gcr_replica_nested_effect")
s = make(new, "s", "rip_gcr_replica_sibling_effect")
open(S + "/harness_mod/common/scripted_effects/rip_gcr_replicas.txt", "w", encoding="utf-8", newline="\n").write(
    "# Test harness only. Exact copies of rip_church_refresh_relations_effect with the modifiers renamed to probes\n"
    "# and a country flag set next to every add_opinion. n = pre-fix (nested) text, s = fixed (sibling) text.\n" + n + "\n" + s)
defs = ["# Test harness only: probe copies of the church opinion modifiers.\n"]
orig = open(S + "/../wt/new/common/opinion_modifiers/RIP_church_relations.txt", encoding="utf-8").read().replace("\r", "")
for line in orig.split("\n"):
    m = re.match(r"^\s*rip_church_opinion_(\w+) = (\{.*\})\s*$", line)
    if m:
        for pfx in ("n", "s"):
            defs.append("rip_gcr_probe_%s_%s = %s\n" % (pfx, m.group(1), m.group(2)))
open(S + "/harness_mod/common/opinion_modifiers/rip_gcr_probe_church_opinions.txt", "w", encoding="utf-8", newline="\n").write("".join(defs))
print(len(mods), "modifier names;", len(defs) - 1, "probe definitions")
