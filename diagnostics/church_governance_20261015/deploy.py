"""Apply this reviewed church patch only, with byte-for-byte backup and manifest.
No process termination, save mutation, directory replacement or deletion.
"""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[2]
ACTIVE = Path('D:/Users/Yamtom/Documents/Paradox Interactive/Europa Universalis IV/mod/RIP').resolve()
REPORT = Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def paths(args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().splitlines()
selected = sorted(set(paths(['diff','--name-only']) + paths(['ls-files','--others','--exclude-standard'])))
allowed = {'common','decisions','events','tools','tests','interface','gfx','localisation','docs'}
rows=[]
for rel in selected:
    if Path(rel).parts[0] not in allowed: continue
    src=(ROOT/rel).resolve(); dst=(ACTIVE/rel).resolve()
    if not src.is_relative_to(ROOT) or not dst.is_relative_to(ACTIVE):
        raise SystemExit('Unsafe path: '+rel)
    desired=src.read_bytes(); old=dst.read_bytes() if dst.exists() else None
    if old == desired: continue
    backup=REPORT/'backup'/rel
    if backup.exists(): raise SystemExit('Backup already exists; refusing to overwrite: '+rel)
    rows.append((rel,src,dst,backup,old,desired))
manifest=[{'path':r,'before':sha(old) if old is not None else None,'after':sha(new)}
          for r,s,d,b,old,new in rows]
(REPORT/'deployment_manifest.json').write_text(json.dumps({'source':str(ROOT),'target':str(ACTIVE),
    'files':manifest},indent=2),encoding='utf-8')
for rel,src,dst,backup,old,new in rows:
    # Recheck immediately before writing, in case another task updated the mod.
    if (dst.read_bytes() if dst.exists() else None) != old:
        raise SystemExit('Active file changed during deployment: '+rel)
    if old is not None:
        backup.parent.mkdir(parents=True,exist_ok=True); backup.write_bytes(old)
    dst.parent.mkdir(parents=True,exist_ok=True); dst.write_bytes(new)
    if sha(dst.read_bytes()) != sha(new): raise SystemExit('Verification failed: '+rel)
print('DEPLOYED AND HASH-VERIFIED:',len(rows),'files; original bytes in',REPORT/'backup')
