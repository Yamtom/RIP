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
    background_binding = f'backGround = "{name}_bg"' if clean else ''
    hit_test = 'alwaystransparent = no' if clean else ''
    return f'''windowType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} size = {{ x=475 y={680 if clean else 550} }}
 moveable = 0
{background_binding}
 iconType = {{ name = "{name}_bg" spriteType = "{background}" position = {{ x=0 y=0 }} {scale} {hit_test} }}
 {body}
}}'''
ro='iconType = { name = "rip_church_ro_title_band" spriteType = "GFX_message_band" position = { x=28 y=14 } scale = 0.79 alwaystransparent = yes }'
ro+=text('rip_church_ro_heading',28,28,w=419,h=30,font='vic_22',align='center')
ro+=text('rip_church_ro_status',28,66,w=419,h=26,align='center')
ro+='iconType = { name = "rip_church_ro_resources_frame" spriteType = "GFX_rip_church_union_section" position = { x=28 y=102 } alwaystransparent = yes }'
ro+=text('rip_church_ro_resources',44,120,w=387,h=76)
for i,k in enumerate(('war','mercy','building','mission')):
    ro+=button(f'rip_church_icon_{k}_button',44,236+i*44,
               f'religion = russian_orthodox OR = {{ has_country_flag = rip_church_icon_{k} rip_church_can_activate_{k} = yes }}',
               f'rip_church_toggle_{k}_effect = yes')
    ro+=text(f'rip_church_icon_{k}_state',294,243+i*44,w=145,h=24)
ro+=text('rip_church_ro_mission_cost',28,414,w=419,h=42,align='center')
ro+=button('rip_church_nodes_button',125,468,'rip_church_ro_can_open_network_menu = yes',
           'country_event = { id = rip_church_nodes.1 }')
ro+=button('rip_church_reconcile_button',125,516,'rip_church_can_reconcile = yes',
           'rip_church_ro_begin_reconciliation_effect = yes',
           'has_country_flag = rip_church_ro_schismatic')
ro+=text('rip_church_ro_help',28,566,w=419,h=86,font='Main_14')
gc='iconType = { name = "rip_church_gc_title_band" spriteType = "GFX_message_band" position = { x=28 y=14 } scale = 0.79 alwaystransparent = yes }'
gc+=text('rip_church_gc_heading',28,28,w=419,h=30,font='vic_22',align='center')
gc+=text('rip_church_gc_orientation',28,66,w=419,h=26,align='center')
for key,y in [('resources',102),('parishes',220)]:
    gc+=f'iconType = {{ name = "rip_church_gc_{key}_frame" spriteType = "GFX_rip_church_union_section" position = {{ x=28 y={y} }} alwaystransparent = yes }}'
gc+=text('rip_church_gc_resources',44,120,w=387,h=76)
gc+=text('rip_church_gc_parishes',44,238,w=387,h=26)
gc+=text('rip_church_gc_center_state',44,274,w=387,h=40)
gc+=text('rip_church_gc_policy_label',28,330,w=419,h=18,align='center')
gc+=button('rip_church_east_button',44,354,
           'rip_church_can_shift_communion = yes check_variable = { which = rip_church_communion value = -99.999 }',
           'rip_church_gc_shift_east_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=button('rip_church_rome_button',265,354,
           'rip_church_can_shift_communion = yes NOT = { check_variable = { which = rip_church_communion value = 100 } }',
           'rip_church_gc_shift_rome_effect = yes',sprite='GFX_standard_button_142_34_button')
gc+=text('rip_church_gc_policy_cost',28,420,w=419,h=20,align='center')
gc+=text('rip_church_gc_privilege_state',28,450,w=419,h=42,align='center')
gc+=button('rip_church_privileges_button',125,504,'religion = greek_catholic',
           'country_event = { id = rip_church.6 }')
gc+=button('rip_church_center_button',125,548,'rip_church_can_found_center = yes','rip_church_found_center_effect = yes')
gc+=button('rip_church_ecumenism_button',125,592,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes')
gc+=text('rip_church_gc_help',28,636,w=419,h=24,font='Main_14',align='center')
religion_panels=panel('rip_church_ro_panel','religion = russian_orthodox',ro,clean=True)+'\n'+panel('rip_church_gc_panel','religion = greek_catholic',gc,clean=True)
outputs['interface/RIP_church_panels.gfx']='''spriteTypes = {
 corneredTileSpriteType = {
  name = "GFX_rip_church_union_frame"
  textureFile = "gfx/interface/tiles_dialog.dds"
  size = { x=475 y=680 } borderSize = { x=32 y=32 }
 }
 corneredTileSpriteType = {
  name = "GFX_rip_church_union_section"
  textureFile = "gfx/interface/small_tiles_dialog.dds"
  size = { x=419 y=106 } borderSize = { x=8 y=8 }
 }
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
