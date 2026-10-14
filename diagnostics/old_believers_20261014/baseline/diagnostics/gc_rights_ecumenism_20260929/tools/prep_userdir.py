import os, sys, shutil
S = os.path.dirname(os.path.abspath(__file__))
run = sys.argv[1]  # A or B
suffix = sys.argv[2] if len(sys.argv) > 2 else ""
wt = {"A": "base", "B": "new"}[run]
ud = os.path.join(S, "ud_" + run + suffix)
os.makedirs(os.path.join(ud, "mod"), exist_ok=True)
wtp = os.path.abspath(os.path.join(S, "..", "wt", wt)).replace("\\", "/")
hp = os.path.abspath(os.path.join(S, "harness_mod")).replace("\\", "/")
def w(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
w(os.path.join(ud, "mod", "RIP.mod"), 'name="Alternative Ruthenian Immersion Pack"\npath="%s"\nsupported_version="v1.37.5.0"\n' % wtp)
w(os.path.join(ud, "mod", "rip_gcr_harness.mod"), 'name="RIP rights ecumenism harness"\npath="%s"\nsupported_version="v1.37.5.0"\n' % hp)
w(os.path.join(ud, "dlc_load.json"), '{"enabled_mods":["mod/RIP.mod","mod/rip_gcr_harness.mod"],"disabled_dlcs":[]}')
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
shutil.copyfile(os.path.join(S, "rip_gcr_run.txt"), os.path.join(ud, "rip_gcr_run.txt"))
print(ud, wtp, hp)
