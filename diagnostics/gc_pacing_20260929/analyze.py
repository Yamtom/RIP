"""Extract actual engine counters; never infer an unobserved final year."""
from pathlib import Path
<<<<<<< HEAD
import hashlib,json,re,sys
=======
import json,re,sys
>>>>>>> bdb75509 (feat(gc_church): Уточнити ігрові абстракції та впровадити діагностичний сценарій темпу ікон/синоду)
OUT=Path(__file__).resolve().parent
if len(sys.argv)>1: OUT=OUT/sys.argv[1]
save=OUT/'userdir/save games/gcpace_final.eu4'
if not save.exists(): save=OUT/'userdir/save games/autosave.eu4'
if not save.exists(): raise SystemExit('No engine save available')
<<<<<<< HEAD
raw=save.read_bytes()
lines=raw.decode('latin-1').splitlines()
=======
lines=save.read_text(encoding='latin-1').splitlines()
>>>>>>> bdb75509 (feat(gc_church): Уточнити ігрові абстракції та впровадити діагностичний сценарій темпу ікон/синоду)
date=next(x[5:] for x in lines[:10] if x.startswith('date='))
i=lines.index('countries={')+1
cohorts={};tag=None;body=[]
while i<len(lines) and lines[i]!='}':
    line=lines[i]
    m=re.match(r'^\t([A-Z0-9]{3})=\{$',line)
    if m: tag=m[1];body=[]
    elif line=='\t}' and tag:
        text='\n'.join(body)
        if 'rip_gcpace_cohort=' in text:
            counters={k:float(v) for k,v in re.findall(r'^\t\t\trip_gcpace_(\w+)=(-?\d+(?:\.\d+)?)$',text,re.M)}
            native={k:v for k,v in re.findall(r'^\t\t(religion|patriarch_authority|treasury|stability|prestige)=(.*)$',text,re.M)}
            mods=re.findall(r'modifier="(rip_church_gc_[^"]+)"\n\t\t\tdate=([^\n]+)',text)
            cohorts[tag]={'native':native,'counters':counters,'active_modifiers':mods}
        tag=None
    elif tag: body.append(line)
    i+=1
game=(OUT/'userdir/logs/game.log').read_text(encoding='utf-8',errors='replace')
dates=re.findall(r'EVENT \[([\d.]+)\]',game)
errors=(OUT/'userdir/logs/error.log').read_text(encoding='utf-8',errors='replace')
<<<<<<< HEAD
result={'save':save.name,'save_sha256':hashlib.sha256(raw).hexdigest(),'save_date':date,'last_logged_event_date':dates[-1] if dates else None,'target_reached':int(date.split('.')[0])>=1465,'cohorts':cohorts,'harness_error_lines':sorted(set(line for line in errors.splitlines() if 'gcpace' in line or 'Quoted string longer' in line))}
(OUT/'observations.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
(OUT/f'observations_{date}.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
=======
result={'save':save.name,'save_date':date,'last_logged_event_date':dates[-1] if dates else None,'target_reached':int(date.split('.')[0])>=1465,'cohorts':cohorts,'harness_error_lines':sorted(set(line for line in errors.splitlines() if 'gcpace' in line or 'Quoted string longer' in line))}
(OUT/'observations.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
>>>>>>> bdb75509 (feat(gc_church): Уточнити ігрові абстракції та впровадити діагностичний сценарій темпу ікон/синоду)
print(json.dumps(result,indent=2))
