"""Manifest of the mod files the game loads: compares the NEW snapshot with the live worktree and with the HEAD snapshot.

Usage: python manifest.py <scratch ee dir> <worktree dir>
Writes <ee>/manifest.json and prints whether the snapshot still equals the live worktree.
"""
import hashlib
import json
import os
import sys

LOADED = "common customizable_localization decisions events gfx history interface localisation missions sound".split()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()


def tree(root, dirs):
    out = {}
    for d in dirs:
        for dd, _, fs in os.walk(os.path.join(root, d)):
            for f in fs:
                p = os.path.join(dd, f)
                out[os.path.relpath(p, root).replace("\\", "/")] = sha(p)
    return out


ee = sys.argv[1]
wt = sys.argv[2]
snap = tree(os.path.join(ee, "wt_new"), LOADED)
live = tree(wt, LOADED)
head = tree(os.path.join(ee, "wt_head"), LOADED)
print("loaded files: snapshot %d, live worktree %d, HEAD %d" % (len(snap), len(live), len(head)))
print("snapshot identical to live worktree:", snap == live)
diff = sorted(k for k in set(head) | set(snap) if head.get(k) != snap.get(k))
print("files that differ HEAD vs NEW: %d" % len(diff))
for k in diff:
    print("  ", ("added " if k not in head else "removed" if k not in snap else "changed"), k)
with open(os.path.join(ee, "manifest.json"), "w") as f:
    json.dump({"new": snap, "head": head}, f, indent=0)
