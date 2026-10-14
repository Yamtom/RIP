"""Prepare an isolated, non-historical 20-year church pacing experiment."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
if len(sys.argv)>1:
    assert sys.argv[1] in ('run2','run3')
    OUT=OUT/sys.argv[1]
SNAP=OUT/'snapshot'
HARNESS=OUT/'harness'
UD=OUT/'userdir'
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8',newline='\n')
assert not (OUT/'manifest.json').exists(), 'Use a fresh experiment directory'
inventory={}
for folder in ('common','events','decisions','missions','history','map','interface','gfx','localisation','customizable_localization','music','sound'):
    source=(OUT.parent/'snapshot'/folder) if len(sys.argv)>1 else ROOT/folder
    if source.exists():
        shutil.copytree(source,SNAP/folder)
        for p in (SNAP/folder).rglob('*'):
            if p.is_file(): inventory[p.relative_to(SNAP).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
write(OUT/'source_inventory.json',json.dumps(inventory,indent=2))
setup=[]
for tag,icon,mixed in [('MOS','liturgy',False),('LIT','charity',True),('POL','learning',False)]:
    setup.append(f'''{tag} = {{
 enable_religion = greek_catholic
 change_religion = greek_catholic
 rip_church_v3_initialize_effect = yes
 every_owned_province = {{ change_religion = {'orthodox' if mixed else 'greek_catholic'} }}
 capital_scope = {{ change_religion = greek_catholic }}
 add_patriarch_authority = -1
 add_patriarch_authority = 0.6
 add_treasury = 300
 add_stability = 3
 set_country_flag = rip_gcpace_cohort
''')
    if mixed:
        setup.append('random_owned_province = { limit = { religion = orthodox } set_province_flag = rip_church_rite_recognized }\nrip_church_gc_refresh_parishes_effect = yes\n')
    setup.append(f'rip_church_gc_activate_icon_{icon}_effect = yes\n')
    setup.append('rip_church_gc_coexistence_effect = yes\n' if mixed else 'rip_church_gc_infrastructure_effect = yes\n')
    setup.append('country_event = { id = rip_gcpace.2 days = 30 }\n}\n')
categories={
 'icon_locked':'rip_church_gc_has_active_icon = yes',
 'icon_ready':'rip_church_gc_can_activate_icons = yes',
 'icon_low':'NOT = { rip_church_gc_has_active_icon = yes } NOT = { patriarch_authority = 0.2 }',
 'synod_locked':'rip_church_gc_has_privilege = yes',
 'synod_ready':'OR = { rip_church_gc_can_infrastructure = yes rip_church_gc_can_coexistence = yes }',
 'synod_low':'NOT = { rip_church_gc_has_privilege = yes } NOT = { patriarch_authority = 0.2 }',
 'synod_other':'NOT = { rip_church_gc_has_privilege = yes } patriarch_authority = 0.2 NOT = { OR = { rip_church_gc_can_infrastructure = yes rip_church_gc_can_coexistence = yes } }',
 'both_locked':'rip_church_gc_has_active_icon = yes rip_church_gc_has_privilege = yes',
 'liturgy':'has_country_modifier = rip_church_gc_icon_liturgy',
 'learning':'has_country_modifier = rip_church_gc_icon_learning',
 'charity':'has_country_modifier = rip_church_gc_icon_charity',
}
sample='change_variable = { which = rip_gcpace_n value = 1 }\n'
for key,trigger in categories.items():
    sample+=f'if = {{ limit = {{ {trigger} }} change_variable = {{ which = rip_gcpace_{key} value = 1 }} }}\n'
sample+='export_to_variable = { which = rip_gcpace_hc value = trigger_value:patriarch_authority }\n'
fields=['n','hc']
for offset in range(0,len(fields),4):
    sample+='log = "GC_PACE [Root.GetName] '+ ' '.join(k+'=[Root.rip_gcpace_'+k+'.GetValue]' for k in fields[offset:offset+4])+'"\n'
sample+='if = { limit = { NOT = { is_year = 1465 } } country_event = { id = rip_gcpace.2 days = 30 } }\n'
metadata=' title = rip_gcpace_title desc = rip_gcpace_desc picture = RELIGION_eventPicture hidden = yes is_triggered_only = yes '
write(HARNESS/'events/rip_gcpace.txt','namespace = rip_gcpace\ncountry_event = { id = rip_gcpace.1'+metadata+'immediate = {\n'+''.join(setup)+'log = "GC_PACE_SETUP_COMPLETE"\n} option = { name = rip_gcpace_ok } }\ncountry_event = { id = rip_gcpace.2'+metadata+'trigger = { religion = greek_catholic } immediate = {\n'+sample+'} option = { name = rip_gcpace_ok } }\n')
write(HARNESS/'localisation/rip_gcpace_l_english.yml','\ufeffl_english:\n rip_gcpace_title:0 "Pacing probe"\n rip_gcpace_desc:0 "Isolated instrumentation."\n rip_gcpace_ok:0 "Continue"\n')
for name,path in [('RIP',SNAP),('rip_gcpace',HARNESS)]:
    write(UD/f'mod/{name}.mod',f'name="{name} pacing experiment"\npath="{path.as_posix()}"\nsupported_version="v1.37.5.0"\n')
write(UD/'dlc_load.json',json.dumps({'enabled_mods':['mod/RIP.mod','mod/rip_gcpace.mod'],'disabled_dlcs':[]}))
write(UD/'settings.txt','''language="l_english"
graphics={ adapter=0 size={ x=1280 y=720 } min_gui={ x=1280 y=720 } refreshRate=60 fullScreen=no borderless=no shadows=no multi_sampling=0 maxanisotropy=0 vsync=no }
master_volume=0
music_volume=0
autosave="YEARLY"
autosave_tocloud=no
compress_autosave=no
compress_saves=no
graceful_exit=yes
''')
write(UD/'gcpace_start.txt','event rip_gcpace.1\nrunyear 1465 gcpace_end.txt\nspeed 5\nobserve\n')
write(UD/'gcpace_end.txt','echo GC_PACE_TARGET_1465\nsave gcpace_final\npause\n')
write(OUT/'manifest.json',json.dumps({'status':'prepared','seed':1001,'start':'1444.11.11','target':'1465.1.1','kind':'engineered observer campaign; not historical adoption or human playtest','head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'git_status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'initial_hc':60,'initial_treasury_grant':300,'initial_stability_grant':3,'seeded_slots':'one icon and one synod purchased through live effects; 40 HC total','cohorts':{'MOS':'homogeneous; liturgy/infrastructure','LIT':'mixed; charity/coexistence','POL':'homogeneous; learning/infrastructure'},'sampling':'every 30 days, after initial purchases; cumulative sample counts','inventory_files':len(inventory)},indent=2))
print(str(UD))
