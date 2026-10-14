"""Builds an isolated EU4 userdir for the engine probes: RIP (path = detached HEAD worktree) + the scratch harness mod."""
import os, sys, shutil

P = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
name = sys.argv[1] if len(sys.argv) > 1 else "ud_1"
ud = os.path.join(P, name)
if os.path.exists(ud):
    shutil.rmtree(ud)
os.makedirs(os.path.join(ud, "mod"), exist_ok=True)
wtp = os.path.join(P, "wt_head").replace("\\", "/")
hp = os.path.join(P, "harness_mod3").replace("\\", "/")


def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


w(os.path.join(ud, "mod", "RIP.mod"), 'name="Alternative Ruthenian Immersion Pack"\npath="%s"\nsupported_version="v1.37.5.0"\n' % wtp)
w(os.path.join(ud, "mod", "rip_pr3_harness.mod"), 'name="RIP engine probes harness 3"\npath="%s"\nsupported_version="v1.37.5.0"\n' % hp)
w(os.path.join(ud, "dlc_load.json"), '{"enabled_mods":["mod/RIP.mod","mod/rip_pr3_harness.mod"],"disabled_dlcs":[]}')
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
events = sys.argv[2:] or ["1", "2", "90", "91", "92"]
w(os.path.join(ud, "rip_pr3_run.txt"), "\n".join(["event rip_prb." + e for e in events] + ["speed 5", ""]))
print(ud, wtp, hp)
