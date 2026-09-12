"""Build the two scripted church panes and province rite controls for EU4 1.37.
Exact vanilla host overrides are necessary: EU4 attaches scripted children to named hosts.
"""
from pathlib import Path
import argparse,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import matching_brace,vanilla_root
ROOT=Path(__file__).resolve().parents[1]; GAME=vanilla_root()
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
defs=[]; outputs={}
def text(name,x,y,w=440,h=42,font='vic_18'):
    defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}"
 text = "{name}" maxWidth = {w} maxHeight = {h} format = left
}}'''
def button(name,x,y,trigger,effect,potential='always = yes',sprite='GFX_standard_button_224'):
    defs.append(f'''custom_button = {{
 name = {name} potential = {{ {potential} }} trigger = {{ {trigger} }}
 effect = {{ {effect} }} tooltip = {name}_tt
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }}
 quadTextureSprite = "{sprite}" buttonText = "{name}" buttonFont = "vic_18"
}}'''
def panel(name,condition,body,x=540,y=8):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    return f'''windowType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} size = {{ x=475 y=550 }}
 moveable = 0
 iconType = {{ name = "{name}_bg" spriteType = "GFX_country_religion_view_bg" position = {{ x=0 y=0 }} scale = 0.86 }}
 {body}
}}'''
ro=text('rip_church_ro_heading',18,12)
ro+=text('rip_church_ro_resources',18,52,h=76)
for i,k in enumerate(('war','mercy','building','mission')):
    ro+=button(f'rip_church_icon_{k}_button',18,140+i*42,
               f'religion = russian_orthodox OR = {{ has_country_flag = rip_church_icon_{k} rip_church_can_activate_{k} = yes }}',
               f'rip_church_toggle_{k}_effect = yes')
    ro+=text(f'rip_church_icon_{k}_state',250,143+i*42,w=185,h=30)
ro+=button('rip_church_nodes_button',18,324,'religion = russian_orthodox',
           'country_event = { id = rip_church_nodes.1 }')
ro+=button('rip_church_reconcile_button',18,366,'rip_church_can_reconcile = yes',
           'rip_church_ro_begin_reconciliation_effect = yes',
           'has_country_flag = rip_church_ro_schismatic')
ro+=text('rip_church_ro_help',18,414,h=100,font='Main_14')
gc=text('rip_church_gc_heading',18,12)
gc+=text('rip_church_gc_resources',18,52,h=102,font='Main_14')
gc+=button('rip_church_east_button',18,158,
           'rip_church_can_shift_communion = yes check_variable = { which = rip_church_communion value = -99.999 }',
           'rip_church_gc_shift_east_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=button('rip_church_rome_button',238,158,
           'rip_church_can_shift_communion = yes NOT = { check_variable = { which = rip_church_communion value = 100 } }',
           'rip_church_gc_shift_rome_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=text('rip_church_gc_privilege_state',18,204,h=42)
gc+=button('rip_church_privileges_button',18,256,'religion = greek_catholic',
           'country_event = { id = rip_church.6 }')
gc+=button('rip_church_center_button',18,298,'rip_church_can_found_center = yes','rip_church_found_center_effect = yes')
gc+=button('rip_church_ecumenism_button',18,340,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes')
gc+=text('rip_church_gc_help',18,388,h=135,font='Main_14')
religion_panels=panel('rip_church_ro_panel','religion = russian_orthodox',ro)+'\n'+panel('rip_church_gc_panel','religion = greek_catholic',gc)
# Province ROOT, clicking country FROM. Never allow buttons on somebody else's land.
province=text('rip_church_rite_heading',18,12,w=440,h=40)
province+=text('rip_church_rite_state',18,52,w=440,h=66)
province+=button('rip_church_recognize_rite_button',18,126,'owned_by = FROM rip_church_can_recognize_rite = yes','rip_church_recognize_rite_effect = yes')
province+=button('rip_church_revoke_rite_button',18,168,'owned_by = FROM rip_church_can_revoke_rite = yes','rip_church_revoke_rite_effect = yes')
province+=button('rip_church_latin_consent_button',18,210,
                 'owned_by = FROM religion = catholic controlled_by = owner NOT = { has_province_flag = rip_church_rite_recognized } NOT = { has_province_flag = rip_church_latin_consent } owner = { rip_church_union_supporter = yes adm_power = 25 }',
                 'rip_church_latin_consent_effect = yes')
province+=text('rip_church_rite_help',18,262,w=440,h=120,font='Main_14')
prov_panel=panel('rip_church_rite_panel','owned_by = FROM FROM = { rip_church_union_supporter = yes } OR = { religion = orthodox religion = russian_orthodox religion = catholic }',province,x=480,y=0)
def attach(file,host,body):
    s=(GAME/'interface'/file).read_text(encoding='utf-8-sig')
    name=re.search(r'name\s*=\s*"'+re.escape(host)+r'"',s)
    assert name, host
    start=s.rfind('windowType',0,name.start())
    opening=s.index('{',start); end=matching_brace(s,opening)
    outputs['interface/'+file]=s[:end]+'\n# RIP church custom controls, descendants of the supported host.\n'+body+'\n'+s[end:]
attach('countryreligionview.gui','countryreligionview',religion_panels)
attach('provinceview.gui','province_window',prov_panel)
outputs['common/custom_gui/RIP_church_controls.txt']='# ROOT/FROM contracts follow common/custom_gui/example.txt in EU4 1.37.\n'+'\n'.join(defs)+'\n'
stale=[]
for path,s in outputs.items():
    target=ROOT/path
    if not target.exists() or target.read_text(encoding='utf-8')!=s:
        stale.append(path)
        if not args.check:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(s,encoding='utf-8',newline='\n')
print(('STALE' if args.check and stale else 'GENERATED')+f': {len(defs)} scripted UI bindings, {len(stale)} files')
if args.check and stale: sys.exit(1)
