"""Harness province report (scratchpad tool): the two test provinces of the harness in one save."""
import re, sys
path = sys.argv[1]
lines = open(path, encoding="latin-1").read().split("\n")
print("save:", path.replace("\\", "/").split("/")[-1], lines[1])
for i, l in enumerate(lines):
    if re.match(r"^-\d+=\{$", l):
        # peek at the flags block only (cheap): province flags come first
        j = i + 1
        if lines[j] == "\t\tflags={":
            k = j + 1
            fl = []
            while lines[k] != "\t\t}":
                fl.append(lines[k].strip())
                k += 1
            if any(f.startswith("rip_gcr_test_") for f in fl):
                e = i + 1
                while lines[e] != "\t}":
                    e += 1
                blk = lines[i:e + 1]
                pid = l[1:-2]
                get = lambda key: next((x.strip() for x in blk if x.startswith("\t\t" + key + "=")), key + "=?")
                mods = []
                for q, x in enumerate(blk):
                    if x.strip().startswith('modifier="'):
                        mods.append(x.strip().split('"')[1])
                print("province %s  %s  %s  %s" % (pid, get("name"), get("owner"), get("religion")))
                print("   flags   :", ", ".join(fl))
                print("   modifiers:", ", ".join(mods) or "-")
                print("   has rip_church_rite: %s | has favoured: %s | has ecumenical: %s" % (
                    "rip_church_rite" in mods, "rip_church_rite_favoured" in mods, "rip_church_rite_ecumenical" in mods))
