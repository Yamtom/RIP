"""Harness probe report (scratchpad tool): count opinion modifiers by name and by owner religion in one save."""
import re, sys, collections
path = sys.argv[1]
prefixes = sys.argv[2:]
lines = open(path, encoding="latin-1").read().split("\n")
print("save:", path.replace("\\", "/").split("/")[-1], lines[1])
start = next(i for i, l in enumerate(lines) if l == "countries={")
i = start + 1; cur = None; blocks = {}
while lines[i] != "}":
    m = re.match(r"^\t([A-Z0-9]{3})=\{$", lines[i])
    if m: cur = m.group(1); a = i
    elif lines[i] == "\t}" and cur: blocks[cur] = (a, i); cur = None
    i += 1
rel = {}
cnt = collections.defaultdict(lambda: collections.Counter())
who = collections.defaultdict(set)
flags = collections.defaultdict(list)
for t, (a, b) in blocks.items():
    r = None; k = a; inf = False
    while k < b:
        l = lines[k]
        if l.startswith("\t\treligion=") and r is None: r = l.split("=")[1]
        if l == "\t\tflags={": inf = True
        elif inf:
            if l == "\t\t}": inf = False
            else:
                f = l.strip().split("=")[0]
                if any(f.startswith(p.replace("rip_gcr_probe_", "rip_gcr_")) for p in prefixes) or f.startswith("rip_gcr_shape") or f.startswith("rip_gcr_f_"):
                    flags[f].append(t)
        k += 1
    rel[t] = r
    k = a
    while k < b and lines[k] != "\t\tactive_relations={": k += 1
    partner = None
    while k < b and lines[k] != "\t\t}":
        m = re.match(r"^\t\t\t([A-Z0-9]{3})=\{$", lines[k])
        if m: partner = m.group(1)
        m = re.match(r'^\t\t\t\t\tmodifier="(.+)"$', lines[k])
        if m and any(m.group(1).startswith(p) for p in prefixes):
            cnt[m.group(1)][str(r)] += 1
            who[m.group(1)].add(t)
        k += 1
for mod in sorted(cnt):
    print("  %-42s entries by owner religion: %s" % (mod, dict(cnt[mod])))
print("flags set by the harness effects (country count by religion):")
for f in sorted(flags):
    print("  %-34s %s" % (f, dict(collections.Counter(str(rel[t]) for t in flags[f]))))
