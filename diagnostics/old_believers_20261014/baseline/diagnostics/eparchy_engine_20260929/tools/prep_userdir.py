"""Builds an isolated EU4 userdir: RIP (path = a snapshot of the tree under test) + the scratch harness mod loaded after it.

    python prep_userdir.py <userdir> <rip tree> <harness dir> <mod-name-suffix>

The commands file rip_ee_run.txt (userdir root, passed to -auto_run) fires the setup event and sets speed 5.
"""
import os
import shutil
import sys

ud, rip, harness, tag = sys.argv[1:5]
if os.path.exists(ud):
    shutil.rmtree(ud)
os.makedirs(os.path.join(ud, "mod"), exist_ok=True)


def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


rip = rip.replace("\\", "/")
harness = harness.replace("\\", "/")
w(os.path.join(ud, "mod", "RIP.mod"), 'name="Alternative Ruthenian Immersion Pack"\npath="%s"\nsupported_version="v1.37.5.0"\n' % rip)
w(os.path.join(ud, "mod", "rip_ee_harness.mod"), 'name="RIP eparchy engine harness %s"\npath="%s"\nsupported_version="v1.37.5.0"\n' % (tag, harness))
w(os.path.join(ud, "dlc_load.json"), '{"enabled_mods":["mod/RIP.mod","mod/rip_ee_harness.mod"],"disabled_dlcs":[]}')
w(os.path.join(ud, "settings.txt"), '''language="l_english"
graphics={
 adapter=0
 size={ x=1280 y=720 }
 min_gui={ x=1280 y=720 }
 refreshRate=60
 fullScreen=no
 borderless=no
 shadows=no
 multi_sampling=0
 maxanisotropy=0
 vsync=no
}
master_volume=0
music_volume=0
autosave="MONTHLY"
autosave_tocloud=no
compress_autosave=no
compress_saves=no
graceful_exit=yes
''')
w(os.path.join(ud, "rip_ee_run.txt"), "event rip_ee.1\nspeed 5\n")
print(ud, rip, harness)
