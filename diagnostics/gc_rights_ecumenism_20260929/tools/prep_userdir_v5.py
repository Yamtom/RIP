"""Build an isolated EU4 userdir for one v5 run (scratch tool, not part of the mod).

usage: python prep_userdir_v5.py <label> <mod worktree> <harness folder> <out root>

Creates <out root>/ud_<label>/ with mod/RIP.mod (path = the worktree), mod/rip_gcr_harness.mod (path = the
harness folder), dlc_load.json enabling both, settings.txt (monthly uncompressed autosave) and the -auto_run
commands file. Prints the userdir path.
"""
import os
import shutil
import sys

label, worktree, harness, out_root = sys.argv[1:5]
ud = os.path.join(out_root, 'ud_' + label)
if os.path.exists(ud):
    raise SystemExit('refusing to reuse an existing userdir: ' + ud)
os.makedirs(os.path.join(ud, 'mod'))


def write(path, text):
    with open(path, 'w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def posix(path):
    return os.path.abspath(path).replace('\\', '/')


write(os.path.join(ud, 'mod', 'RIP.mod'),
      'name="Alternative Ruthenian Immersion Pack"\npath="%s"\nsupported_version="v1.37.5.0"\n' % posix(worktree))
write(os.path.join(ud, 'mod', 'rip_gcr_harness.mod'),
      'name="RIP rights ecumenism harness"\npath="%s"\nsupported_version="v1.37.5.0"\n' % posix(harness))
write(os.path.join(ud, 'dlc_load.json'), '{"enabled_mods":["mod/RIP.mod","mod/rip_gcr_harness.mod"],"disabled_dlcs":[]}')
write(os.path.join(ud, 'settings.txt'), '''language="l_english"
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
shutil.copyfile(os.path.join(harness, 'commands_rip_gcr_run.txt'), os.path.join(ud, 'rip_gcr_run.txt'))
print(ud)
