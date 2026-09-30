"""SHA-1 manifest of the mod files the game loads from a tree, and a comparison of two manifests.

    python manifest2.py write <tree> <out.json>
    python manifest2.py compare <a.json> <b.json>

Used to prove that the worktree (the RIP mod root of every run) was not modified while the game ran.
"""
import hashlib
import json
import os
import sys

LOADED = "common customizable_localization decisions events gfx history interface localisation missions sound".split()


def tree(root):
    out = {}
    for d in LOADED:
        for dd, _, fs in os.walk(os.path.join(root, d)):
            for f in fs:
                p = os.path.join(dd, f)
                with open(p, "rb") as fh:
                    out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha1(fh.read()).hexdigest()
    return out


if sys.argv[1] == "write":
    m = tree(sys.argv[2])
    with open(sys.argv[3], "w") as f:
        json.dump(m, f)
    print("files:", len(m))
else:
    a = json.load(open(sys.argv[2]))
    b = json.load(open(sys.argv[3]))
    diff = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    print("identical" if not diff else "DIFFERENT: %d files" % len(diff))
    for k in diff:
        print("  ", k)
    sys.exit(1 if diff else 0)
