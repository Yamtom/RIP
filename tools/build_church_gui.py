"""Build scripted church panes and province rite controls for EU4 1.37.
Exact vanilla host overrides are necessary: EU4 attaches scripted children to named hosts.
"""
from pathlib import Path
import argparse,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import matching_brace,vanilla_root,named_block
ROOT=Path(__file__).resolve().parents[1]; GAME=vanilla_root()
ap=argparse.ArgumentParser(); ap.add_argument('--check',action='store_true'); args=ap.parse_args()
defs=[]; feature_defs=[]; outputs={}; text_bindings=set()
# Derive the GUI transaction from the live decision, including regional and
# historical gates. Do not maintain a weaker parallel path to state conversion.
adoption=named_block((ROOT/'decisions/GreekCatholicDecisions.txt').read_text(encoding='utf-8-sig'),'convert_to_greek_catholic_decision')
def decision_field(key):
    match=re.search(r'\b'+key+r'\s*=\s*\{',adoption)
    opening=adoption.index('{',match.start())
    return adoption[opening+1:matching_brace(adoption,opening)]
outputs['common/scripted_triggers/rip_church_gui_generated.txt']='# Generated from convert_to_greek_catholic_decision.\nrip_church_gui_can_adopt_union = {\n'+decision_field('potential')+decision_field('allow')+'\n}\n'
outputs['common/scripted_effects/rip_church_gui_generated.txt']='# Generated guarded GUI transaction; the decision remains authoritative.\nrip_church_gui_adopt_union_effect = {\n if = { limit = { rip_church_gui_can_adopt_union = yes }\n'+decision_field('effect')+'\n }\n}\n'
def text(name,x,y,w=440,h=42,font='vic_18',align='left'):
    if name not in text_bindings:
        defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
        text_bindings.add(name)
    return f'''instantTextBoxType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}"
 text = "{name}" maxWidth = {w} maxHeight = {h} format = {align}
}}'''
def button(name,x,y,trigger,effect,potential='always = yes',sprite='GFX_standard_button_224',frame=None,label=True):
    frame_clause='' if frame is None else f' frame = {{ number = {frame} trigger = {{ always = yes }} }}'
    defs.append(f'''custom_button = {{
 name = {name} potential = {{ {potential} }} trigger = {{ {trigger} }}
 effect = {{ {effect} }} tooltip = {name}_tt{frame_clause}
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }}
 quadTextureSprite = "{sprite}" buttonText = "{name if label else ''}" buttonFont = "vic_18"
}}'''

def feature_button(name,trigger,effect,sprite='GFX_standard_button_71',frame=None):
    frame_clause='' if frame is None else f' frame = {{ number = {frame} trigger = {{ always = yes }} }}'
    feature_defs.append(f'''custom_button = {{
 name = {name} potential = {{ always = yes }} trigger = {{ {trigger} }}
 effect = {{ {effect} }} tooltip = {name}_tt{frame_clause}
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x=0 y=0 }}
 quadTextureSprite = "{sprite}" buttonText = "{name}" buttonFont = "vic_18"
}}'''

def shield(name,x,y,target,potential,sprite):
    defs.append(f'''custom_shield = {{
 name = {name} potential = {{ {potential} }} trigger = {{ always = yes }}
 global_event_target = {target} open_country = yes tooltip = {name}_tt
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }}
 quadTextureSprite = "{sprite}" buttonFont = "vic_18"
}}'''

def art(name,sprite,x,y,scale=1):
    return f'iconType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x={x} y={y} }} scale = {scale} alwaystransparent = yes }}'

def inset(name,x,y,w,h):
    sprite='GFX_rip_church_inset_'+name
    insets.append(f'corneredTileSpriteType = {{ name = "{sprite}" textureFile = "gfx/interface/copts_blessing_slot.dds" size = {{ x={w} y={h} }} borderSize = {{ x=8 y=8 }} }}')
    return art('rip_church_inset_'+name,sprite,x,y)

insets=['corneredTileSpriteType = { name = "GFX_rip_church_action_slot" textureFile = "gfx/interface/small_tiles_dialog.dds" size = { x=58 y=58 } borderSize = { x=8 y=8 } }']
def panel(name,condition,body,x=540,y=8,clean=False):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    background = ('GFX_rip_church_union_frame' if clean else 'GFX_country_religion_view_bg')
    scale = '' if clean else 'scale = 0.86'
    hit_test = 'alwaystransparent = no' if clean else ''
    native_church = name in ('rip_church_ro_panel','rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_union_paths_panel')
    if native_church:
        background='GFX_rip_church_ro_frame'
        scale='scale = 0.782537'
    height=680 if name=='rip_church_gc_panel' else 560 if native_church else 680 if clean else 550
    return f'''windowType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} size = {{ x=475 y={height} }}
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
gc=inset('union_status',34,98,407,72)+inset('parishes',34,205,407,92)+inset('institutions',34,332,407,178)
gc+=text('rip_church_gc_heading',28,28,w=419,h=26,font='vic_22',align='center')
gc+=text('rip_church_gui_coexistence',28,76,w=419,h=20,align='center')
gc+=text('rip_church_gc_resources',44,108,w=387,h=50,align='center')
gc+=text('rip_church_gui_parishes_title',28,176,w=419,h=22,align='center')
gc+=text('rip_church_gui_parish_counts',44,216,w=387,h=54)
gc+=text('rip_church_gui_institutions_title',28,303,w=419,h=22,align='center')
gc+=text('rip_church_gui_slot_state',44,344,w=387,h=24,align='center')
gc+=text('rip_church_gui_active_institution',44,379,w=387,h=42,align='center')
gc+=button('rip_church_gui_synod',54,446,'religion = greek_catholic','rip_church_gc_open_synod_effect = yes',sprite='button_type_1')
gc+=button('rip_church_gui_ecumenism',272,446,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes',sprite='button_type_1')
gc+=text('rip_church_gui_local_note',44,486,w=387,h=18,font='Main_14',align='center')
gc+=text('rip_church_gc_icons_title',28,523,w=419,h=22,align='center')
for i,(key,sprite) in enumerate((
    ('liturgy','GFX_rip_church_gc_icon_liturgy'),
    ('learning','GFX_rip_church_gc_icon_learning'),
    ('charity','GFX_rip_church_gc_icon_charity'),
)):
    x=64+i*120
    gc+=f'iconType = {{ name = "rip_church_gc_icon_{key}_art" spriteType = "{sprite}" position = {{ x={x+19} y=552 }} alwaystransparent = yes }}'
    gc+=feature_button(f'rip_church_gc_icon_{key}_button',
        f'rip_church_gc_can_activate_icon_{key} = yes',
        f'rip_church_gc_activate_icon_{key}_effect = yes')
    gc+=f'guiButtonType = {{ name = "rip_church_gc_icon_{key}_button" scripted = yes position = {{ x={x} y=548 }} quadTextureSprite = "GFX_standard_button_71" buttonText = "" buttonFont = "vic_18" }}'
    gc+=text(f'rip_church_gc_icon_{key}_state',x-6,594,w=100,h=24,align='center')
gc+=text('rip_church_gc_icons_note',38,628,w=399,h=30,font='Main_14',align='center')

retired_curia_source = r"""
curia=''
curia+=text('rip_church_gc_curia_heading',28,20,w=419,h=26,font='vic_22',align='center')
curia+=text('rip_church_gc_curia_status',28,54,w=419,h=20,align='center')
curia+=text('rip_church_gc_rome_resources',44,82,w=387,h=48,align='center')
curia+='''guiButtonType = { name = "rip_church_gc_pope_shield" scripted = yes position = { x=112 y=136 } buttonFont = "vic_18" }
guiButtonType = { name = "rip_church_gc_controller_shield" scripted = yes position = { x=336 y=136 } buttonFont = "vic_18" }
'''
curia+=text('rip_church_gc_controller_label',286,137,w=150,h=24,align='center')
curia+=inset('petitions',34,174,407,151)
curia+=text('rip_church_gc_petitions_title',28,179,w=419,h=22,align='center')
for i,key in enumerate(('church_tax','blessing','indulgence','saint','usury','holy_war','legate','monopoly')):
    x=42+(i%4)*99
    y=210+(i//4)*50
    name=f'rip_church_gc_petition_{key}_button'
    curia+=f'guiButtonType = {{ name = "{name}" scripted = yes position = {{ x={x} y={y} }} quadTextureSprite = "GFX_standard_button_71" buttonText = "" buttonFont = "vic_18" }}'
curia+=inset('curia_privilege',34,338,407,60)
curia+=text('rip_church_gc_curia_privilege',44,347,w=387,h=45,align='center')
curia+=inset('donation',34,412,407,84)
curia+=text('rip_church_gc_donation_cost',44,420,w=220,h=64)
curia+=button('rip_church_gc_donate_button',286,435,'rip_church_gc_can_donate = yes','rip_church_gc_donate_effect = yes',sprite='GFX_standard_button_105')
curia+=f'''guiButtonType = {{ name = "rip_church_gc_deputation_button" scripted = yes position = {{ x=82 y=535 }} quadTextureSprite = "GFX_standard_button_224" buttonText = "rip_church_gc_deputation_button" buttonFont = "vic_18" }}'''
curia+=art('rip_church_gc_deputation_art','GFX_shield_small',102,541,0.7)
curia+=text('rip_church_gc_deputation_note',50,575,w=375,h=56,font='Main_14',align='center')
curia+=inset('gc_icons',34,520,407,105) # Adjusted position to fit after deputation
curia+=feature_text('rip_church_gc_icons_title',28,522,w=419,h=20,align='center') # Adjusted position
for i,(key,sprite) in enumerate((
    ('liturgy','GFX_rip_church_gc_icon_liturgy'),
    ('learning','GFX_rip_church_gc_icon_learning'),
    ('charity','GFX_rip_church_gc_icon_charity'),
)):
    x=76+i*124
    feature_defs.append(f'custom_icon = {{ name = rip_church_gc_icon_{key}_active_frame potential = {{ has_country_modifier = rip_church_gc_icon_{key} }} frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
    curia+=art(f'rip_church_gc_icon_{key}_art',sprite,x+20,552)
    curia+=f'iconType = {{ name = "rip_church_gc_icon_{key}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x={x+20} y=552 }} alwaystransparent = yes }}'
    curia+=feature_button(f'rip_church_gc_icon_{key}_button',x,548,
        f'rip_church_gc_can_activate_icon_{key} = yes',
        f'rip_church_gc_activate_icon_{key}_effect = yes')
    curia+=feature_text(f'rip_church_gc_icon_{key}_state',x-8,588,w=100,h=22,align='center')
curia+=feature_text('rip_church_gc_icons_note',44,608,w=387,h=20,font='Main_14',align='center')
curia+=gc_tabs('curia')
curia_panel=f'''windowType = {{
 name = "rip_church_gc_curia_panel" scripted = yes position = {{ x=540 y=8 }} size = {{ x=475 y=680 }}
 moveable = 0
 iconType = {{ name = "rip_church_gc_curia_panel_bg" spriteType = "GFX_rip_church_ro_frame" position = {{ x=0 y=0 }} scale = 0.782537 }}
 {curia}
}}'''
"""
paths=inset('paths_status',34,98,407,64)+inset('paths_actions',34,195,407,195)+inset('paths_patron',34,402,407,108)
paths+=text('rip_church_gui_paths_heading',28,28,w=419,h=26,font='vic_22',align='center')
paths+=text('rip_church_gui_path_status',28,76,w=419,h=20,align='center')
paths+=text('rip_church_gui_path_identity',44,104,w=387,h=54)
paths+=text('rip_church_gui_paths_title',28,166,w=419,h=22,align='center')
paths+=button('rip_church_gui_florence',125,204,'rip_church_can_begin_florence = yes','rip_church_begin_florence_effect = yes')
paths+=button('rip_church_gui_adopt',125,253,'rip_church_gui_can_adopt_union = yes','rip_church_gui_adopt_union_effect = yes')
paths+=button('rip_church_gui_sponsor',125,302,'rip_church_can_sponsor_union = yes','rip_church_sponsor_union_effect = yes')
paths+=text('rip_church_gui_path_progress',44,350,w=387,h=36,align='center')
paths+=text('rip_church_gui_patron_state',44,420,w=387,h=70,align='center')
religion_panels=(panel('rip_church_ro_panel','religion = russian_orthodox',ro,clean=True)+'\n'+
                panel('rip_church_gc_panel','religion = greek_catholic',gc,clean=True)+'\n'+
                panel('rip_church_union_paths_panel','OR = { religion = orthodox religion = catholic }',paths,clean=True))
outputs['common/custom_gui/RIP_church_gc_features.txt']='# Greek Catholic icon actions.\n'+'\n'.join(feature_defs)+'\n'
outputs['interface/RIP_church_panels.gfx']='spriteTypes = {\n'+'\n'.join(insets)+'''
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
 spriteType = { name = "GFX_rip_church_gc_privileges" textureFile = "gfx/interface/ideas_EU4/church_privilege_slots.dds" }
 spriteType = { name = "GFX_rip_church_gc_center" textureFile = "gfx/interface/ideas_EU4/global_missionary_strength.dds" }
 spriteType = { name = "GFX_rip_church_gc_ecumenism" textureFile = "gfx/interface/ideas_EU4/improve_relation_modifier.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_liturgy" textureFile = "gfx/interface/ideas_EU4/global_missionary_strength.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_learning" textureFile = "gfx/interface/ideas_EU4/development_cost.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_charity" textureFile = "gfx/interface/ideas_EU4/global_unrest.dds" }
}
'''
# Province ROOT, clicking country FROM. Never allow buttons on somebody else's land.
province=text('rip_church_rite_heading',18,12,w=440,h=40)
province+=text('rip_church_rite_state',18,52,w=440,h=66)
province+=button('rip_church_recognize_rite_button',18,126,'owned_by = FROM rip_church_can_recognize_rite = yes','rip_church_recognize_rite_effect = yes')
province+=button('rip_church_revoke_rite_button',18,168,'owned_by = FROM rip_church_can_revoke_rite = yes','rip_church_revoke_rite_effect = yes')
province+=text('rip_church_rite_help',18,224,w=440,h=150,font='Main_14')
prov_panel=panel('rip_church_rite_panel','owned_by = FROM FROM = { religion = greek_catholic } OR = { religion = orthodox religion = russian_orthodox religion = catholic }',province,x=480,y=0)

# Retain native widget names and parents for the engine and old saves.
# A GC-only local synod occupies the native empty icon-selector area, drawn last.
defs.append('custom_window = { name = rip_church_gc_native_controls potential = { religion = greek_catholic } }')
defs.append('custom_icon = { name = rip_church_gc_union_symbol potential = { NOT = { has_country_modifier = rip_church_gc_infrastructure } NOT = { has_country_modifier = rip_church_gc_coexistence } } frame = { number = 31 trigger = { always = yes } } }')
for key in ('infrastructure','coexistence'):
    defs.append(f'custom_icon = {{ name = rip_church_gc_synod_{key}_symbol potential = {{ has_country_modifier = rip_church_gc_{key} }} frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
native_controls='''windowType = {
 name = "rip_church_gc_native_controls" scripted = yes
 position = { x=0 y=0 } size = { x=280 y=50 } moveable = 0
 iconType = { name = "rip_church_gc_selector_cover" spriteType = "GFX_rip_church_policy_slot" position = { x=310 y=235 } scale = 1.2 alwaystransparent = no }
 iconType = { name = "rip_church_gc_union_symbol" scripted = yes spriteType = "GFX_country_icon_religion" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_infrastructure_symbol" scripted = yes spriteType = "GFX_rip_church_gc_privileges" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_coexistence_symbol" scripted = yes spriteType = "GFX_rip_church_gc_ecumenism" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
'''+button('rip_church_gc_native_privileges_button',304,300,'religion = greek_catholic','rip_church_gc_open_synod_effect = yes',sprite='GFX_standard_button_71').replace('buttonFont = "vic_18"','buttonFont = "vic_18" Orientation = "LEFT"')+'\n}\n'
def attach(file,host,body):
    s=(GAME/'interface'/file).read_text(encoding='utf-8-sig')
    if file=='countryreligionview.gui':
        native_name=re.search(r'name\s*=\s*"orthodox_specific_window"',s)
        native_start=s.rfind('windowType',0,native_name.start())
        native_end=matching_brace(s,s.index('{',native_start))
        s=s[:native_end]+'\n# RIP GC privilege shortcut over the empty native icon selector.\n'+native_controls+s[native_end:]
    name=re.search(r'name\s*=\s*"'+re.escape(host)+r'"',s)
    assert name, host
    start=s.rfind('windowType',0,name.start())
    opening=s.index('{',start); end=matching_brace(s,opening)
    outputs['interface/'+file]=s[:end]+'\n# RIP church custom controls, descendants of the supported host.\n'+body+'\n'+s[end:]
attach('countryreligionview.gui','countryreligionview',religion_panels)
attach('provinceview.gui','province_window',prov_panel)
outputs['common/custom_gui/RIP_church_controls.txt']='# ROOT/FROM contracts follow common/custom_gui/example.txt in EU4 1.37.\n'+'\n'.join(defs)+'\n'
outputs['common/custom_gui/RIP_church_gc_features.txt']='# Greek Catholic icons and a non-electoral Curia deputation.\n'+'\n'.join(feature_defs)+'\n'
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
