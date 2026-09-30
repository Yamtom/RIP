"""Moves the overridden RIP files of a generated harness (everything except the rip_ee_* harness files) into a snapshot copy of
the RIP tree, replacing the same-named files there.

    python overlay.py <harness dir> <snapshot dir>

Why: EU4 1.37.5 did not let a later mod replace RIP's scripted-trigger file by giving its own file the same name (the window
triggers still read 'no' in the first run), so each profile runs on its own snapshot copy of the tree under test, with the window
triggers and the hidden starters edited in the copy. The harness mod then only holds the setup and probe events (rip_ee_*).
"""
import os
import shutil
import sys

h, snap = sys.argv[1:3]
moved = []
for dd, _, fs in os.walk(h):
    for f in fs:
        if f.startswith("rip_ee") or f == "descriptor.mod":
            continue
        src = os.path.join(dd, f)
        rel = os.path.relpath(src, h)
        dst = os.path.join(snap, rel)
        if not os.path.exists(dst):
            raise SystemExit("snapshot has no %s: refusing to add files" % rel)
        shutil.move(src, dst)
        moved.append(rel.replace(os.sep, "/"))
print("overlay: %d files replaced in %s" % (len(moved), snap))
for m in moved:
    print("  ", m)
