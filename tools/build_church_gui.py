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
def text(name,x,y,w=440,h=42,font='vic_18',align='left'):
    defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}"
 text = "{name}" maxWidth = {w} maxHeight = {h} format = {align}
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
def panel(name,condition,body,x=540,y=8,clean=False):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    background = ('GFX_rip_church_union_frame' if clean else 'GFX_country_religion_view_bg')
    scale = '' if clean else 'scale = 0.86'
    hit_test = 'alwaystransparent = no' if clean else ''
    native_church = name in ('rip_church_ro_panel','rip_church_gc_panel')
    if native_church:
        background='GFX_rip_church_ro_frame'
        scale='scale = 0.782537'
    return f'''windowType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} size = {{ x=475 y={560 if native_church else 680 if clean else 550} }}
 moveable = 0
 iconType = {{ name = "{name}_bg" spriteType = "{background}" position = {{ x=0 y=0 }} {scale} {hit_test} }}
 {body}
}}'''
ro=text('rip_church_ro_heading',28,28,w=419,h=26,font='vic_22',align='center')
ro+=text('rip_church_ro_status',28,76,w=419,h=20,align='center')
ro+=text('rip_church_ro_resources',44,100,w=387,h=54)
ro+=text('rip_church_ro_policies_title',28,166,w=419,h=22,align='center')
for i,k in enumerate(('war','mercy','building','mission')):
    x=26+i*106
    ro+=f'iconType = {{ name = "rip_church_{k}_slot" spriteType = "GFX_rip_church_policy_slot" position = {{ x={x+23} y=208 }} alwaystransparent = yes }}'
    ro+=f'iconType = {{ name = "rip_church_{k}_art" spriteType = "GFX_rip_church_policy_{k}" position = {{ x={x+20} y=205 }} alwaystransparent = yes }}'
    defs.append(f'custom_icon = {{ name = rip_church_{k}_active_frame potential = {{ has_country_flag = rip_church_icon_{k} }} frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
    ro+=f'iconType = {{ name = "rip_church_{k}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x={x+23} y=208 }} alwaystransparent = yes }}'
    ro+=button(f'rip_church_icon_{k}_button',x,278,
               f'religion = russian_orthodox OR = {{ has_country_flag = rip_church_icon_{k} rip_church_can_activate_{k} = yes }}',
               f'rip_church_toggle_{k}_effect = yes',sprite='GFX_standard_button_105')
    ro+=text(f'rip_church_icon_{k}_state',x,317,w=105,h=18,align='center')
ro+=text('rip_church_ro_mission_cost',28,346,w=419,h=40,align='center')
ro+=button('rip_church_nodes_button',125,394,'rip_church_ro_can_open_network_menu = yes',
           'country_event = { id = rip_church_nodes.1 }')
ro+=button('rip_church_reconcile_button',125,438,'rip_church_can_reconcile = yes',
           'rip_church_ro_begin_reconciliation_effect = yes',
           'has_country_flag = rip_church_ro_schismatic')
ro+=text('rip_church_ro_help',40,481,w=395,h=54,font='Main_14')
gc=text('rip_church_gc_heading',28,28,w=419,h=26,font='vic_22',align='center')
gc+=text('rip_church_gc_orientation',28,76,w=419,h=20,align='center')
gc+=text('rip_church_gc_resources',44,100,w=387,h=54)
gc+=text('rip_church_gc_policy_label',28,166,w=419,h=22,align='center')
gc+=text('rip_church_gc_parishes',44,199,w=387,h=18)
gc+=text('rip_church_gc_center_state',44,221,w=387,h=36)
gc+=button('rip_church_east_button',44,260,
           'rip_church_can_shift_communion = yes check_variable = { which = rip_church_communion value = -99.999 }',
           'rip_church_gc_shift_east_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=button('rip_church_rome_button',265,260,
           'rip_church_can_shift_communion = yes NOT = { check_variable = { which = rip_church_communion value = 100 } }',
           'rip_church_gc_shift_rome_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=text('rip_church_gc_policy_cost',28,324,w=419,h=18,align='center')
gc+=text('rip_church_gc_privilege_state',28,348,w=419,h=36,align='center')
gc+=button('rip_church_privileges_button',125,392,'religion = greek_catholic',
           'country_event = { id = rip_church.6 }')
gc+=button('rip_church_center_button',125,432,'rip_church_can_found_center = yes','rip_church_found_center_effect = yes')
gc+=button('rip_church_ecumenism_button',125,472,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes')
gc+=button('rip_church_gc_guide_button',185,512,'religion = greek_catholic','country_event = { id = rip_church_help.1 }',sprite='GFX_standard_button_105')
religion_panels=panel('rip_church_ro_panel','religion = russian_orthodox',ro,clean=True)+'\n'+panel('rip_church_gc_panel','religion = greek_catholic',gc,clean=True)
outputs['interface/RIP_church_panels.gfx']='''spriteTypes = {
 spriteType = {
  name = "GFX_rip_church_ro_frame"
  textureFile = "gfx/interface/copts_bg.dds"
 }
 spriteType = { name = "GFX_rip_church_policy_slot" textureFile = "gfx/interface/copts_blessing_slot.dds" }
 spriteType = { name = "GFX_rip_church_policy_active" textureFile = "gfx/interface/copts_blessing_select_glow.dds" }
 spriteType = { name = "GFX_rip_church_policy_war" textureFile = "gfx/interface/ideas_EU4/land_morale.dds" }
 spriteType = { name = "GFX_rip_church_policy_mercy" textureFile = "gfx/interface/ideas_EU4/global_unrest.dds" }
 spriteType = { name = "GFX_rip_church_policy_building" textureFile = "gfx/interface/ideas_EU4/development_cost.dds" }
 spriteType = { name = "GFX_rip_church_policy_mission" textureFile = "gfx/interface/ideas_EU4/global_missionary_strength.dds" }
}
'''
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

# Retain native widget names and parents for the engine and old saves.
# A GC-only guide occupies the native empty icon-selector area, drawn last.
defs.append('custom_window = { name = rip_church_gc_native_guide potential = { religion = greek_catholic } }')
defs.append('custom_icon = { name = rip_church_gc_guide_symbol potential = { always = yes } frame = { number = 31 trigger = { always = yes } } }')
native_guide='''windowType = {
 name = "rip_church_gc_native_guide" scripted = yes
 position = { x=0 y=0 } size = { x=280 y=50 } moveable = 0
 iconType = { name = "rip_church_gc_guide_cover" spriteType = "GFX_rip_church_policy_slot" position = { x=310 y=235 } scale = 1.2 alwaystransparent = no }
 iconType = { name = "rip_church_gc_guide_symbol" scripted = yes spriteType = "GFX_country_icon_religion" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
'''+button('rip_church_gc_native_guide_button',304,300,'religion = greek_catholic','country_event = { id = rip_church_help.1 }',sprite='GFX_standard_button_71').replace('buttonFont = "vic_18"','buttonFont = "vic_18" Orientation = "LEFT"')+'\n}\n'
def attach(file,host,body):
    s=(GAME/'interface'/file).read_text(encoding='utf-8-sig')
    if file=='countryreligionview.gui':
        native_name=re.search(r'name\s*=\s*"orthodox_specific_window"',s)
        native_start=s.rfind('windowType',0,native_name.start())
        native_end=matching_brace(s,s.index('{',native_start))
        s=s[:native_end]+'\n# RIP GC guide over the empty native icon selector.\n'+native_guide+s[native_end:]
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
