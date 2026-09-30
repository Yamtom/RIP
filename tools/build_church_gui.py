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

def feature_button(name,x,y,trigger,effect,sprite='GFX_standard_button_71',frame=None,label=False):
    frame_clause='' if frame is None else f' frame = {{ number = {frame} trigger = {{ always = yes }} }}'
    feature_defs.append(f'''custom_button = {{
 name = {name} potential = {{ always = yes }} trigger = {{ {trigger} }}
 effect = {{ {effect} }} tooltip = {name}_tt{frame_clause}
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }}
 quadTextureSprite = "{sprite}" buttonText = "{name if label else ''}" buttonFont = "vic_18"
}}'''

def feature_text(name,x,y,w=440,h=42,font='vic_18',align='left'):
    feature_defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }} tooltip = {name}_tt }}')
    return f'''instantTextBoxType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}"
 text = "{name}" maxWidth = {w} maxHeight = {h} format = {align}
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

def gc_tabs(page):
    # Fixed navigation rail shared by all three Union pages.
    y=110
    return (button('rip_church_gc_union_tab_'+page,63,y,'OR = { religion = greek_catholic religion = catholic }',
                   'rip_church_gc_open_union_effect = yes',sprite='GFX_tab_small_116',frame=2 if page=='union' else 1)+
            button('rip_church_gc_curia_tab_'+page,179,y,'religion = greek_catholic',
                   'rip_church_gc_open_curia_effect = yes',sprite='GFX_tab_small_116',frame=2 if page=='curia' else 1)+
            button('rip_church_gc_parishes_tab_'+page,295,y,'rip_church_union_supporter = yes',
                   'rip_church_gui_open_parishes_effect = yes',sprite='GFX_tab_small_116',frame=2 if page=='parishes' else 1))

def art(name,sprite,x,y,scale=1):
    return f'iconType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x={x} y={y} }} scale = {scale} alwaystransparent = yes }}'

def inset(name,x,y,w,h):
    sprite='GFX_rip_church_inset_'+name
    insets.append(f'corneredTileSpriteType = {{ name = "{sprite}" textureFile = "gfx/interface/copts_blessing_slot.dds" size = {{ x={w} y={h} }} borderSize = {{ x=8 y=8 }} }}')
    return art('rip_church_inset_'+name,sprite,x,y)

def church_header(body,page):
    return (text('rip_church_gc_heading',28,43,w=419,h=28,font='vic_22',align='center')+
            card('rip_church_header_'+page,34,73,407,30,
                 text('rip_church_gui_shared_status',8,10,w=391,h=22,font='vic_18',align='center'))+
            gc_tabs(page))

def section(body,name,y,feature=False):
    title=(feature_text if feature else text)(name,45,y+4,w=385,h=20,font='vic_18',align='center')
    return body+art(name+'_banner','GFX_rip_church_section_banner',71,y,0.8)+title

insets=[
 'corneredTileSpriteType = { name = "GFX_rip_church_union_frame" textureFile = "gfx/interface/choose_idea_bg.dds" size = { x=475 y=660 } borderSize = { x=32 y=64 } }',
 'spriteType = { name = "GFX_rip_church_section_banner" textureFile = "gfx/interface/copts_blessing_title_banner.dds" }'
]
def panel(name,condition,body,x=540,y=8,clean=False):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    background = ('GFX_rip_church_union_frame' if clean else 'GFX_country_religion_view_bg')
    scale = '' if clean else 'scale = 0.86'
    hit_test = 'alwaystransparent = no' if clean else ''
    native_church = name in ('rip_church_ro_panel','rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel','rip_church_union_paths_panel')
    if native_church:
        background='GFX_rip_church_ro_frame'
        scale='scale = 0.782537'
    height=560 if native_church else 680 if clean else 550
    if name in ('rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel'):
        background='GFX_rip_church_union_frame'
        scale=''
        height=660
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
# Each card is a real parent: children use local UPPER_LEFT coordinates.
def card(name,x,y,w,h,body):
    # Layout groups have no texture: the native dialog is the single surface.
    return f'windowType = {{ name = "{name}" position = {{ x={x} y={y} }} size = {{ x={w} y={h} }} Orientation = "UPPER_LEFT" moveable = 0 '+body+' }'

def framed(name,sprite,x,y,scale=1):
    return art(name+'_frame','GFX_rip_church_policy_slot',x,y,scale)+art(name,sprite,x+round(9*scale),y+round(9*scale),0.65*scale)

gc=church_header('', 'union')
status=text('rip_church_gui_communion_cell',12,10,w=188,h=48,font='Main_14')
status+=text('rip_church_gui_rite_cell',211,10,w=184,h=48,font='Main_14')
for i,family in enumerate(('eastern','latin')):
    status+=button('rip_church_gui_count_'+family,27+i*199,63,'rip_church_union_supporter = yes',
                   'rip_church_gui_open_parishes_effect = yes',sprite='button_type_1',label=False)
    status+=text('rip_church_gui_count_'+family+'_value',27+i*199,68,w=145,h=20,font='Main_14',align='center').replace('format = center','format = center alwaystransparent = yes')
gc=section(gc,'rip_church_gui_status_title',92)
gc+=card('rip_church_status_card',34,126,407,108,status)
gc=section(gc,'rip_church_gui_institutions_title',239)
synod=framed('rip_church_synod_symbol','GFX_rip_church_gc_privileges',12,7,0.72)
synod+=text('rip_church_gui_slot_state',76,12,w=111,h=36,font='Main_14')
synod+=button('rip_church_gui_synod',27,85,'religion = greek_catholic','rip_church_gc_open_synod_effect = yes',sprite='button_type_1')
gc+=card('rip_church_synod_card',34,273,199,118,synod)
policy=framed('rip_church_policy_symbol','GFX_rip_church_gc_ecumenism',12,7,0.72)
policy+=text('rip_church_gui_ecumenism_state',76,12,w=111,h=36,font='Main_14')
policy+=button('rip_church_gui_ecumenism',27,85,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes',sprite='button_type_1')
policy+=text('rip_church_gui_ecumenism_reason',8,49,w=183,h=36,font='vic_18',align='center')
defs.append('custom_icon = { name = rip_church_ecumenism_lock potential = { NOT = { rip_church_can_ecumenism = yes } NOT = { has_country_flag = rip_church_ecumenical } } tooltip = rip_church_gui_ecumenism_tt }')
policy+=art('rip_church_ecumenism_lock','GFX_idea_not_yet_unlocked',44,37,0.65).replace('spriteType =','scripted = yes spriteType =',1)
gc+=card('rip_church_ecumenism_card',242,273,199,118,policy)
gc=section(gc,'rip_church_gc_icons_title',397,feature=True)
icons=''
for i,(key,sprite) in enumerate((
    ('liturgy','GFX_rip_church_gc_icon_liturgy'),
    ('learning','GFX_rip_church_gc_icon_learning'),
    ('charity','GFX_rip_church_gc_icon_charity'),
)):
    x=47+i*125
    feature_defs.append(f'custom_icon = {{ name = rip_church_gc_icon_{key}_active_frame potential = {{ has_country_modifier = rip_church_gc_icon_{key} }} tooltip = rip_church_gc_icon_{key}_button_tt frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
    icons+=art(f'rip_church_gc_icon_{key}_slot','GFX_rip_church_policy_slot',x,5)
    icons+=feature_button(f'rip_church_gc_icon_{key}_button',x,5,
        f'rip_church_gc_can_activate_icon_{key} = yes',
        f'rip_church_gc_activate_icon_{key}_effect = yes',sprite='GFX_coptic_blessing_select')
    icons+=art(f'rip_church_gc_icon_{key}_art',sprite,x+9,14,0.65)
    icons+=f'iconType = {{ name = "rip_church_gc_icon_{key}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x={x} y=5 }} alwaystransparent = yes }}'
    icons+=feature_text(f'rip_church_gc_icon_{key}_state',x-27,65,w=112,h=36,font='vic_18',align='center')
icons+=feature_text('rip_church_gc_icons_note',10,104,w=387,h=40,font='vic_18',align='center')
gc+=card('rip_church_devotional_card',34,431,407,148,icons)

parishes=church_header('', 'parishes')
parishes=section(parishes,'rip_church_gui_parish_list_title',92)
register=text('rip_church_gui_register_columns',12,12,w=383,h=22,font='Main_14')
register+=text('rip_church_gui_parish_empty_state',12,53,w=383,h=130,font='Main_14',align='center')
register+=text('rip_church_gui_recognition_cost',12,196,w=383,h=90,font='Main_14',align='center')
register+=text('rip_church_gui_recognition_reason',12,320,w=383,h=36,font='Main_14',align='center')
register+=button('rip_church_gui_recognize_parish',91,362,'always = no','rip_church_gui_open_parishes_effect = yes')
parishes+=card('rip_church_register_card',34,126,407,418,register)

curia=church_header('', 'curia')
curia=section(curia,'rip_church_gc_curia_heading',92)
see=shield('rip_church_gc_pope_shield',14,8,'rip_church_gc_rome',
              'has_global_flag = rip_church_gc_rome_known rip_church_gc_rome_present = yes','GFX_shield_medium')
see+=feature_text('rip_church_gc_curia_note',91,12,w=300,h=54,font='Main_14')
curia+=card('rip_church_see_card',34,126,407,81,see)
curia=section(curia,'rip_church_gui_rights_title',212)
rights=''
for i,key in enumerate(('cardinal','vote','conclave')):
    x=44+i*125
    rights+=framed('rip_church_right_'+key,('GFX_rip_church_gc_privileges','GFX_rip_church_gc_ecumenism','GFX_rip_church_policy_mission')[i],x,7)
    rights+=art('rip_church_right_'+key+'_lock','GFX_idea_not_yet_unlocked',x+32,37,0.65)
    rights+=text('rip_church_gui_right_'+key,x-27,70,w=112,h=36,font='Main_14',align='center')
curia+=card('rip_church_rights_card',34,246,407,115,rights)
curia=section(curia,'rip_church_gc_contact_title',366)
contact=feature_button('rip_church_gc_deputation_button',91,12,
                      'rip_church_gc_can_depute_to_curia = yes',
                      'rip_church_gc_depute_to_curia_effect = yes',
                      sprite='GFX_standard_button_224',label=True)
for i,key in enumerate(('cost','peace','rome','cooldown')):
    contact+=text('rip_church_gui_contact_'+key,14+(i%2)*194,51+(i//2)*27,w=188,h=26,font='Main_14')
contact+=text('rip_church_gui_contact_history',12,110,w=383,h=40,font='vic_18',align='center')
curia+=card('rip_church_contact_card',34,400,407,151,contact)
# Apply the shift to whole card windows and standalone section strips using a
# brace-aware walk, so nested text and buttons retain their parent offsets.
def shift_page(source):
    result=''; pos=0
    while pos<len(source):
        opening=source.find('{',pos)
        if opening<0: return result+source[pos:]
        end=matching_brace(source,opening)+1
        block=source[pos:end]
        name=re.search(r'name = "([^"]+)"',block)
        if name and not any(k in name[1] for k in ('surface_','window_banner','gc_heading','header_','tab_')):
            block=re.sub(r'(position = \{ x=\d+ y=)(\d+)',lambda m:m[1]+str(int(m[2])+60),block,count=1)
        result+=block; pos=end
    return result
gc,curia,parishes=map(shift_page,(gc,curia,parishes))
# Match the native religion view's body font, including feature text.
gc,curia,parishes=(page.replace('font = "Main_14"','font = "vic_18"') for page in (gc,curia,parishes))
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
                panel('rip_church_gc_panel','religion = greek_catholic NOT = { has_country_flag = rip_church_gc_curia_view } NOT = { has_country_flag = rip_church_gui_parishes_view }',gc,clean=True)+'\n'+
                panel('rip_church_gc_curia_panel','religion = greek_catholic has_country_flag = rip_church_gc_curia_view NOT = { has_country_flag = rip_church_gui_parishes_view }',curia,clean=True)+'\n'+
                panel('rip_church_gc_parishes_panel','OR = { religion = greek_catholic rip_church_union_supporter = yes } has_country_flag = rip_church_gui_parishes_view',parishes,clean=True)+'\n'+
                panel('rip_church_union_paths_panel','OR = { religion = orthodox religion = catholic } NOT = { has_country_flag = rip_church_gui_parishes_view }',paths,clean=True))
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
        # Native text boxes do not evaluate our country-scoped custom readout.
        # Bind the replacement as scripted text, preserving the native geometry.
        s=s.replace('name = "current_patriarch_authority_text"',
                    'name = "rip_church_authority_heading" scripted = yes')
        s=re.sub(r'text = "CURRENT_PATRIARCH_AUTHORITY"[ \t]*', 'text = "rip_church_authority_heading"', s)
        defs.append('custom_text_box = { name = rip_church_authority_heading potential = { always = yes } tooltip = rip_church_authority_heading }')
        native_name=re.search(r'name\s*=\s*"orthodox_specific_window"',s)
        native_start=s.rfind('windowType',0,native_name.start())
        native_end=matching_brace(s,s.index('{',native_start))
        s=s[:native_end]+'\n# RIP GC privilege shortcut over the empty native icon selector.\n'+native_controls+s[native_end:]
    name=re.search(r'name\s*=\s*"'+re.escape(host)+r'"',s)
    assert name, host
    start=s.rfind('windowType',0,name.start())
    opening=s.index('{',start); end=matching_brace(s,opening)
    outputs['interface/'+file]=s[:end]+'\n# RIP church custom controls, descendants of the supported host.\n'+body+'\n'+s[end:]
# Explicit local anchors; scripted tooltip remains the authoritative dynamic
# binding. pdx_tooltip also covers the native GUI hover path.
def native_anchors(source):
    source=re.sub(r'(name = "([^"]+)" scripted = yes position = \{[^}]+\})',
                  lambda m:m[1]+' Orientation = "UPPER_LEFT" pdx_tooltip = "'+m[2]+'_tt"',source)
    source=re.sub(r'(position = \{[^}]+\})( scale =)',r'\1 Orientation = "UPPER_LEFT"\2',source)
    return source
attach('countryreligionview.gui','countryreligionview',native_anchors(religion_panels))
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
