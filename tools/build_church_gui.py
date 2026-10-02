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
    return (button('rip_church_gc_union_tab_'+page,121,y,'OR = { religion = greek_catholic religion = catholic }',
                   'rip_church_gc_open_union_effect = yes',sprite='GFX_tab_small_116',frame=2 if page=='union' else 1)+
            button('rip_church_gc_curia_tab_'+page,237,y,'religion = greek_catholic',
                   'rip_church_gc_open_curia_effect = yes',sprite='GFX_tab_small_116',frame=2 if page=='curia' else 1))

def art(name,sprite,x,y,scale=1):
    return f'iconType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x={x} y={y} }} scale = {scale} alwaystransparent = yes }}'

def church_header(body,page):
    return (art('rip_church_window_banner_'+page,'GFX_rip_church_window_banner',18,19,0.94)+
            text('rip_church_gc_heading',28,43,w=419,h=28,font='vic_22',align='center')+
            card('rip_church_header_'+page,34,73,407,30,
                 text('rip_church_gui_shared_status',8,8,w=391,h=22,font='vic_18',align='center'))+
            # The native inactive tab ends at row 30; the rail's gold row is
            # 14px below its origin. Selected tabs cover that joined rail.
            art('rip_church_tab_rail_'+page,'GFX_macro_diplomacy_line',13,126,449/418)+gc_tabs(page))

def section(body,name,y,feature=False):
    title=(feature_text if feature else text)(name,45,y+4,w=385,h=20,font='vic_18',align='center')
    return body+art(name+'_banner','GFX_rip_church_section_banner',71,y,0.8)+title

insets=[
 'corneredTileSpriteType = { name = "GFX_rip_church_union_frame" textureFile = "gfx/interface/tiles_dialog.dds" size = { x=475 y=660 } borderSize = { x=32 y=32 } }',
 'corneredTileSpriteType = { name = "GFX_rip_church_union_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=449 y=634 } borderSize = { x=8 y=8 } }',
 'spriteType = { name = "GFX_rip_church_window_banner" textureFile = "gfx/interface/province_history_entry_banner.dds" }',
 'spriteType = { name = "GFX_rip_church_section_banner" textureFile = "gfx/interface/copts_blessing_title_banner.dds" }'
]
def panel(name,condition,body,x=540,y=8,clean=False):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    background = ('GFX_rip_church_union_frame' if clean else 'GFX_country_religion_view_bg')
    scale = '' if clean else 'scale = 0.86'
    hit_test = 'alwaystransparent = no' if clean else ''
    native_church = name in ('rip_church_rite_panel','rip_church_ro_panel','rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel')
    if native_church:
        background='GFX_rip_church_ro_frame'
        scale='scale = 0.782537'
    height=560 if native_church else 680 if clean else 550
    if name in ('rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel'):
        background='GFX_rip_church_union_frame'
        scale=''
        height=660
        body=art(name+'_surface','GFX_rip_church_union_surface',13,13)+body
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

def framed(name,sprite,x,y):
    # Both institutional cards use the same 58px slot and centered 42px art.
    return art(name+'_frame','GFX_rip_church_policy_slot',x,y)+art(name,sprite,x+8,y+8,0.65625)

def state_badge(name,x,y,ready,tooltip,scale=1):
    """Native trigger check/cross beside a read-only state, never a button."""
    result=''
    for state,gate,sprite in (
        ('ready',ready,'GFX_text_yes'),
        ('blocked','NOT = { '+ready+' }','GFX_text_no'),
    ):
        key=name+'_'+state
        defs.append(f'custom_icon = {{ name = {key} potential = {{ {gate} }} tooltip = {tooltip} }}')
        result+=f'iconType = {{ name = "{key}" scripted = yes spriteType = "{sprite}" position = {{ x={x} y={y} }} scale = {scale} }}'
    return result

gc=church_header('', 'union')
status=text('rip_church_gui_communion_cell',12,8,w=188,h=44,font='Main_14',align='center')
status+=text('rip_church_gui_rite_cell',211,8,w=184,h=44,font='Main_14',align='center')
for i,family in enumerate(('eastern','latin')):
    status+=text('rip_church_gui_count_'+family+'_value',27+i*199,56,w=145,h=20,font='Main_14',align='center').replace('format = center','format = center alwaystransparent = yes')
gc=section(gc,'rip_church_gui_status_title',92)
gc+=card('rip_church_status_card',34,126,407,84,status)
gc=section(gc,'rip_church_gui_institutions_title',216)
synod=framed('rip_church_synod_symbol','GFX_rip_church_gc_privileges',16,7)
synod+=text('rip_church_gui_slot_state',90,12,w=101,h=44,font='Main_14',align='center')
defs.append('custom_icon = { name = rip_church_synod_active_frame potential = { rip_church_gc_has_privilege = yes } tooltip = rip_church_gui_synod_active_tt }')
synod+='iconType = { name = "rip_church_synod_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = { x=16 y=7 } alwaystransparent = yes }'
# State and the sole menu entry point belong to the same card.
synod+=text('rip_church_gui_synod_active',8,68,w=208,h=40,font='vic_18',align='center')
synod+=button('rip_church_gc_native_privileges_button',0,108,'religion = greek_catholic','rip_church_gc_open_synod_effect = yes',sprite='GFX_standard_button_224')
gc+=card('rip_church_synod_card',13,250,224,140,synod)
policy=framed('rip_church_policy_symbol','GFX_rip_church_gc_ecumenism',16,7)
policy+=text('rip_church_gui_ecumenism_state',90,12,w=101,h=44,font='Main_14',align='center')
policy+=state_badge('rip_church_ecumenism_status',192,29,'OR = { has_country_flag = rip_church_ecumenical rip_church_can_ecumenism = yes }','rip_church_gui_ecumenism_reason_tt')
policy+=button('rip_church_gui_ecumenism',0,108,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes',sprite='GFX_standard_button_224')
policy+=text('rip_church_gui_ecumenism_reason',8,68,w=208,h=40,font='vic_18',align='center')
# Equal cards fill the 449px inset, and the 224px action button stays inside its card.
gc+=card('rip_church_ecumenism_card',238,250,224,140,policy)
gc=section(gc,'rip_church_gc_icons_title',396,feature=True)
icons=''
for i,(key,sprite) in enumerate((
    ('liturgy','GFX_rip_church_gc_icon_liturgy'),
    ('learning','GFX_rip_church_gc_icon_learning'),
    ('charity','GFX_rip_church_gc_icon_charity'),
)):
    x=47+i*125
    feature_defs.append(f'custom_icon = {{ name = rip_church_gc_icon_{key}_active_frame potential = {{ has_country_modifier = rip_church_gc_icon_{key} }} tooltip = rip_church_gc_icon_{key}_button_tt frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
    icons+=art(f'rip_church_gc_icon_{key}_slot','GFX_rip_church_policy_slot',x,3)
    icons+=feature_button(f'rip_church_gc_icon_{key}_button',x,3,
        f'rip_church_gc_can_activate_icon_{key} = yes',
        f'rip_church_gc_activate_icon_{key}_effect = yes',sprite='GFX_coptic_blessing_select')
    icons+=art(f'rip_church_gc_icon_{key}_art',sprite,x+8,11,0.65625)
    icons+=f'iconType = {{ name = "rip_church_gc_icon_{key}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x={x} y=3 }} alwaystransparent = yes }}'
    blocked_name=f'rip_church_gc_icon_{key}_blocked'
    feature_defs.append(f'custom_icon = {{ name = {blocked_name} potential = {{ NOT = {{ has_country_modifier = rip_church_gc_icon_{key} }} NOT = {{ rip_church_gc_can_activate_icon_{key} = yes }} }} tooltip = rip_church_gc_icon_{key}_button_tt }}')
    icons+=f'iconType = {{ name = "{blocked_name}" scripted = yes spriteType = "GFX_text_no" position = {{ x={x+39} y=42 }} scale = 0.9 }}'
    icons+=feature_text(f'rip_church_gc_icon_{key}_state',x-27,62,w=112,h=36,font='vic_18',align='center')
icons+=feature_text('rip_church_gc_icons_note',10,100,w=387,h=22,font='vic_18',align='center')
gc+=card('rip_church_devotional_card',34,428,407,128,icons)

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
see=shield('rip_church_gc_pope_shield',14,12,'rip_church_gc_rome',
              'has_global_flag = rip_church_gc_rome_known rip_church_gc_rome_present = yes','GFX_shield_small')
see+=feature_text('rip_church_gc_curia_note',66,8,w=130,h=72,font='vic_18',align='center')
see+=shield('rip_church_gc_controller_shield',213,12,'rip_church_gc_controller',
            'has_global_flag = rip_church_gc_controller_known event_target:rip_church_gc_controller = { is_papal_controller = yes }','GFX_shield_small')
see+=text('rip_church_gc_controller_readout',267,8,w=130,h=72,font='vic_18',align='center')
curia+=card('rip_church_see_card',34,126,407,81,see)
curia=section(curia,'rip_church_gc_contact_title',212)
contact=feature_button('rip_church_gc_deputation_button',91,6,
                      'rip_church_gc_can_depute_to_curia = yes',
                      'rip_church_gc_depute_to_curia_effect = yes',
                      sprite='GFX_standard_button_224',label=True)
contact+=text('rip_church_gui_contact_cost',12,42,w=383,h=30,font='Main_14',align='center')
contact+=state_badge('rip_church_deputation_status',12,79,'rip_church_gc_can_depute_to_curia = yes','rip_church_gui_contact_history_tt')
contact+=text('rip_church_gui_contact_history',42,76,w=353,h=32,font='Main_14',align='center')
contact+=feature_button('rip_church_gc_holy_see_gift_button',91,112,
                        'rip_church_gc_can_offer_gift_to_holy_see = yes',
                        'rip_church_gc_offer_gift_to_holy_see_effect = yes',
                        sprite='GFX_standard_button_224',label=True)
contact+=text('rip_church_gc_holy_see_gift_summary',12,148,w=383,h=30,font='Main_14',align='center')
contact+=state_badge('rip_church_gift_status',12,185,'rip_church_gc_can_offer_gift_to_holy_see = yes','rip_church_gc_holy_see_gift_state_tt')
contact+=text('rip_church_gc_holy_see_gift_state',42,182,w=353,h=32,font='Main_14',align='center')
curia+=card('rip_church_contact_card',34,246,407,216,contact)
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
# Catholic/Orthodox Union paths remain in their existing events and decisions.
# Do not advertise them through a permanent religion sidebar.
religion_panels=(panel('rip_church_ro_panel','religion = russian_orthodox',ro,clean=True)+'\n'+
                panel('rip_church_gc_panel','religion = greek_catholic NOT = { has_country_flag = rip_church_gc_curia_view } NOT = { has_country_flag = rip_church_gui_parishes_view }',gc,clean=True)+'\n'+
                panel('rip_church_gc_curia_panel','religion = greek_catholic has_country_flag = rip_church_gc_curia_view NOT = { has_country_flag = rip_church_gui_parishes_view }',curia,clean=True)+'\n'+
                panel('rip_church_gc_parishes_panel','OR = { religion = greek_catholic rip_church_union_supporter = yes } has_country_flag = rip_church_gui_parishes_view',parishes,clean=True))
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
 spriteType = { name = "GFX_rip_church_gc_icon_liturgy" textureFile = "gfx/interface/rip_church/gc_icon_liturgy.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_learning" textureFile = "gfx/interface/rip_church/gc_icon_learning.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_charity" textureFile = "gfx/interface/rip_church/gc_icon_charity.dds" }
 spriteType = { name = "GFX_rip_church_gc_capacity_low" textureFile = "gfx/interface/rip_church/gc_archbishop_low.dds" }
 spriteType = { name = "GFX_rip_church_gc_capacity_high" textureFile = "gfx/interface/rip_church/gc_archbishop_high.dds" }
 spriteType = { name = "GFX_rip_church_gc_capacity_hover_frame" textureFile = "gfx/interface/ideaView_progress_frame_long.dds" }
 corneredTileSpriteType = { name = "GFX_rip_church_gc_selector_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=82 y=100 } borderSize = { x=8 y=8 } }
}
'''
# Province ROOT, clicking country FROM. Never allow buttons on somebody else's land.
province=text('rip_church_rite_heading',28,40,w=419,h=26,font='vic_22',align='center')
province+=button('rip_church_rite_panel_hide_button',438,8,'owned_by = FROM',
                 'set_province_flag = rip_church_rite_panel_hidden',
                 sprite='GFX_closebutton2',label=False)
province+=text('rip_church_rite_state',28,90,w=419,h=24,align='center')
province+=text('rip_church_rite_effects',44,140,w=387,h=100)
province+=button('rip_church_recognize_rite_button',125,264,'owned_by = FROM rip_church_can_recognize_rite = yes','rip_church_recognize_rite_effect = yes',potential='NOT = { has_province_flag = rip_church_rite_recognized }')
province+=button('rip_church_revoke_rite_button',125,264,'owned_by = FROM rip_church_can_revoke_rite = yes','rip_church_revoke_rite_effect = yes',potential='has_province_flag = rip_church_rite_recognized')
province+=text('rip_church_rite_note',40,332,w=395,h=56,font='Main_14',align='center')
# Shown only where the action applies or is already in force, not on every owned province.
province_gate='owned_by = FROM FROM = { religion = greek_catholic } OR = { has_province_flag = rip_church_rite_recognized AND = { is_city = yes controlled_by = owner OR = { religion = orthodox religion = russian_orthodox religion = catholic } } }'
prov_panel=panel('rip_church_rite_panel',province_gate+' NOT = { has_province_flag = rip_church_rite_panel_hidden }',province,x=480,y=0)
# Hide state belongs to the selected province. The small reopen button is
# shown only for that same eligible province, so changing selection never
# strands the player without a way to restore the panel.
defs.append(f'custom_window = {{ name = rip_church_rite_reopen_panel potential = {{ {province_gate} has_province_flag = rip_church_rite_panel_hidden }} }}')
prov_reopen_button=button('rip_church_rite_panel_show_button',0,0,'owned_by = FROM',
                          'clr_province_flag = rip_church_rite_panel_hidden',
                          sprite='GFX_standard_button_71')
prov_reopen_panel=f'''windowType = {{
 name = "rip_church_rite_reopen_panel" scripted = yes position = {{ x=874 y=8 }} size = {{ x=80 y=32 }}
 backGround = "" moveable = 0
 {prov_reopen_button}
}}'''

# Retain native widget names and parents for the engine and old saves.
# GC retains the native HC engine widgets. The obsolete Orthodox icon selector
# is covered, while the Synod menu now opens from its institution card.
defs.append('custom_window = { name = rip_church_gc_native_controls potential = { religion = greek_catholic } }')
for level in ('low','high'):
    # Preserve the native sprite/name for Orthodox countries; only GC substitutes art.
    defs.append(f'custom_icon = {{ name = {level}_patriarch_authority potential = {{ NOT = {{ religion = greek_catholic }} }} }}')
    defs.append(f'custom_icon = {{ name = rip_church_gc_capacity_{level}_icon potential = {{ religion = greek_catholic }} tooltip = rip_church_gc_capacity_hover_tt }}')
defs.append('custom_icon = { name = rip_church_gc_capacity_bar_hover potential = { religion = greek_catholic } tooltip = rip_church_gc_capacity_hover_tt }')
defs.append('custom_icon = { name = rip_church_gc_union_symbol potential = { NOT = { has_country_modifier = rip_church_gc_infrastructure } NOT = { has_country_modifier = rip_church_gc_coexistence } } frame = { number = 31 trigger = { always = yes } } }')
for key in ('infrastructure','coexistence'):
    defs.append(f'custom_icon = {{ name = rip_church_gc_synod_{key}_symbol potential = {{ has_country_modifier = rip_church_gc_{key} }} frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
native_controls='''windowType = {
 name = "rip_church_gc_native_controls" scripted = yes
 position = { x=0 y=0 } size = { x=280 y=50 } moveable = 0
 iconType = { name = "rip_church_gc_capacity_bar_hover" scripted = yes spriteType = "GFX_rip_church_gc_capacity_hover_frame" position = { x=84 y=286 } alwaystransparent = no }
 iconType = { name = "rip_church_gc_capacity_low_icon" scripted = yes spriteType = "GFX_rip_church_gc_capacity_low" position = { x=54 y=273 } }
 iconType = { name = "rip_church_gc_capacity_high_icon" scripted = yes spriteType = "GFX_rip_church_gc_capacity_high" position = { x=260 y=273 } }
 iconType = { name = "rip_church_gc_selector_cover" spriteType = "GFX_rip_church_gc_selector_surface" position = { x=303 y=232 } alwaystransparent = no }
 iconType = { name = "rip_church_gc_union_symbol" scripted = yes spriteType = "GFX_country_icon_religion" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_infrastructure_symbol" scripted = yes spriteType = "GFX_rip_church_gc_privileges" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_coexistence_symbol" scripted = yes spriteType = "GFX_rip_church_gc_ecumenism" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
'''+'\n}\n'
def attach(file,host,body):
    s=(GAME/'interface'/file).read_text(encoding='utf-8-sig')
    if file=='countryreligionview.gui':
        for level in ('low','high'):
            s=re.sub(r'(name\s*=\s*"'+level+r'_patriarch_authority")(?!\s*scripted)',r'\1 scripted = yes',s)
        # Native text boxes do not evaluate our country-scoped custom readout.
        # Bind the replacement as scripted text, preserving the native geometry.
        s=s.replace('name = "current_patriarch_authority_text"',
                    'name = "rip_church_authority_heading" scripted = yes')
        s=re.sub(r'text = "CURRENT_PATRIARCH_AUTHORITY"[ \t]*', 'text = "rip_church_authority_heading"', s)
        defs.append('custom_text_box = { name = rip_church_authority_heading potential = { always = yes } tooltip = rip_church_authority_heading_tt }')
        native_name=re.search(r'name\s*=\s*"orthodox_specific_window"',s)
        native_start=s.rfind('windowType',0,native_name.start())
        native_end=matching_brace(s,s.index('{',native_start))
        s=s[:native_end]+'\n# RIP GC resource hover and covered native icon selector.\n'+native_controls+s[native_end:]
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
attach('provinceview.gui','province_window',prov_panel+'\n'+prov_reopen_panel)
outputs['common/custom_gui/RIP_church_controls.txt']='# ROOT/FROM contracts follow common/custom_gui/example.txt in EU4 1.37.\n'+'\n'.join(defs)+'\n'
outputs['common/custom_gui/RIP_church_gc_features.txt']='# Greek Catholic icons and non-electoral Curia diplomacy.\n'+'\n'.join(feature_defs)+'\n'
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
