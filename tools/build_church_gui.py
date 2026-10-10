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
NO_TIP=set()
# Derive the GUI transaction from the live decision, including regional and
# historical gates. Do not maintain a weaker parallel path to state conversion.
adoption=named_block((ROOT/'decisions/GreekCatholicDecisions.txt').read_text(encoding='utf-8-sig'),'convert_to_greek_catholic_decision')
def decision_field(key):
    match=re.search(r'\b'+key+r'\s*=\s*\{',adoption)
    opening=adoption.index('{',match.start())
    return adoption[opening+1:matching_brace(adoption,opening)]
outputs['common/scripted_triggers/rip_church_gui_generated.txt']='# Generated from convert_to_greek_catholic_decision.\nrip_church_gui_can_adopt_union = {\n'+decision_field('potential')+decision_field('allow')+'\n}\n'
outputs['common/scripted_effects/rip_church_gui_generated.txt']='# Generated guarded GUI transaction; the decision remains authoritative.\nrip_church_gui_adopt_union_effect = {\n if = { limit = { rip_church_gui_can_adopt_union = yes }\n'+decision_field('effect')+'\n }\n}\n'
def text(name,x,y,w=440,h=42,font='vic_18',align='left',tip=True):
    if name not in text_bindings:
        tip_clause=f' tooltip = {name}_tt' if tip else ''
        defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }}{tip_clause} }}')
        text_bindings.add(name)
        if not tip: NO_TIP.add(name)
    return f'''instantTextBoxType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }} font = "{font}"
 text = "{name}" maxWidth = {w} maxHeight = {h} format = {align}
}}'''
def button(name,x,y,trigger,effect,potential='always = yes',sprite='GFX_standard_button_224',frame=None,label=True,tooltip=None,scale=None):
    frame_clause='' if frame is None else f' frame = {{ number = {frame} trigger = {{ always = yes }} }}'
    tooltip_key=tooltip or name+'_tt'
    scale_clause='' if scale is None else f' scale = {scale}'
    defs.append(f'''custom_button = {{
 name = {name} potential = {{ {potential} }} trigger = {{ {trigger} }}
 effect = {{ {effect} }} tooltip = {tooltip_key}{frame_clause}
}}''')
    return f'''guiButtonType = {{
 name = "{name}" scripted = yes position = {{ x={x} y={y} }}
 quadTextureSprite = "{sprite}" buttonText = "{name if label else ''}" buttonFont = "vic_18"{scale_clause}
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

def feature_text(name,x,y,w=440,h=42,font='vic_18',align='left',tip=True):
    tip_clause=f' tooltip = {name}_tt' if tip else ''
    if not tip: NO_TIP.add(name)
    feature_defs.append(f'custom_text_box = {{ name = {name} potential = {{ always = yes }}{tip_clause} }}')
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
            # Banner band is rows 28..61; vic_22 capitals span +5..+16 of the box, so y=35 centres them (was 43: 2px above the band's lower edge).
            text('rip_church_gc_heading',28,35,w=419,h=24,font='vic_22',align='center',tip=False)+
            card('rip_church_header_'+page,34,73,407,30,
                 text('rip_church_gui_shared_status',8,8,w=391,h=22,font='vic_18',align='center'))+
            # The native inactive tab ends at row 30; the rail's gold row is
            # 14px below its origin. Selected tabs cover that joined rail.
            art('rip_church_tab_rail_'+page,'GFX_macro_diplomacy_line',13,126,449/418)+gc_tabs(page))

def section(body,name,y,feature=False,tip=False):
    # Section titles repeat their banner, so they carry no tooltip unless asked.
    title=(feature_text if feature else text)(name,45,y+4,w=385,h=20,font='vic_18',align='center',tip=tip)
    return body+art(name+'_banner','GFX_rip_church_section_banner',71,y,0.8)+title


insets=[
 'corneredTileSpriteType = { name = "GFX_rip_church_union_frame" textureFile = "gfx/interface/tiles_dialog.dds" size = { x=475 y=660 } borderSize = { x=32 y=32 } }',
 'corneredTileSpriteType = { name = "GFX_rip_church_union_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=449 y=634 } borderSize = { x=8 y=8 } }',
 'corneredTileSpriteType = { name = "GFX_rip_church_rite_frame" textureFile = "gfx/interface/tiles_dialog.dds" size = { x=475 y=327 } borderSize = { x=32 y=32 } }',
 'corneredTileSpriteType = { name = "GFX_rip_church_rite_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=449 y=301 } borderSize = { x=8 y=8 } }',
 'spriteType = { name = "GFX_rip_church_window_banner" textureFile = "gfx/interface/province_history_entry_banner.dds" }',
 'spriteType = { name = "GFX_rip_church_section_banner" textureFile = "gfx/interface/copts_blessing_title_banner.dds" }'
]
def panel(name,condition,body,x=540,y=8,clean=False):
    defs.append(f'custom_window = {{ name = {name} potential = {{ {condition} }} }}')
    background = ('GFX_rip_church_union_frame' if clean else 'GFX_country_religion_view_bg')
    scale = '' if clean else 'scale = 0.86'
    hit_test = 'alwaystransparent = no' if clean else ''
    native_church = name in ('rip_church_ro_panel','rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel')
    if native_church:
        background='GFX_rip_church_ro_frame'
        scale='scale = 0.782537'
    height=560 if native_church else 680 if clean else 550
    if name == 'rip_church_rite_panel':
        # Same window language as the Union/Curia pages, but sized to its content.
        background='GFX_rip_church_rite_frame'
        scale=''
        height=327
        body=art(name+'_surface','GFX_rip_church_rite_surface',13,13)+body
    if name in ('rip_church_ro_panel','rip_church_gc_panel','rip_church_gc_curia_panel','rip_church_gc_parishes_panel'):
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
# Each card is a real parent: children use local UPPER_LEFT coordinates.
def card(name,x,y,w,h,body):
    # Layout groups have no texture: the native dialog is the single surface.
    return f'windowType = {{ name = "{name}" position = {{ x={x} y={y} }} size = {{ x={w} y={h} }} Orientation = "UPPER_LEFT" moveable = 0 '+body+' }'

def framed(name,sprite,x,y):
    # Both institutional cards use the same 58px slot and centered 42px art.
    return art(name+'_frame','GFX_rip_church_policy_slot',x,y)+art(name,sprite,x+8,y+8,0.65625)

def state_badge(name,x,y,ready,tooltip,scale=1,click_through=False):
    """Native trigger check/cross beside a read-only state, never a button."""
    result=''
    for state,gate,sprite in (
        ('ready',ready,'GFX_text_yes'),
        ('blocked','NOT = { '+ready+' }','GFX_text_no'),
    ):
        key=name+'_'+state
        defs.append(f'custom_icon = {{ name = {key} potential = {{ {gate} }} tooltip = {tooltip} }}')
        transparent=' alwaystransparent = yes' if click_through else ''
        result+=f'iconType = {{ name = "{key}" scripted = yes spriteType = "{sprite}" position = {{ x={x} y={y} }} scale = {scale}{transparent} }}'
    return result

# Same native font, parent geometry and slot hit area as the Union window.
# Policies are our real transactions; retired native Orthodox icons stay inert.
ro=art('rip_church_window_banner_ro','GFX_rip_church_window_banner',18,19,0.94)
ro+=text('rip_church_ro_heading',28,35,w=419,h=24,font='vic_22',align='center',tip=False)
ro+=card('rip_church_ro_status_card',34,73,407,30,
         text('rip_church_ro_status',8,8,w=391,h=22,align='center'))
for key,y,sprite in (
    ('fuel',119,'GFX_rip_church_ro_fervor'),
    ('slots',146,'GFX_rip_church_ro_authority'),
    ('network',173,'GFX_rip_church_ro_network'),
):
    ro+=art('rip_church_ro_'+key+'_symbol',sprite,43,y-2,0.375)
    ro+=text('rip_church_ro_'+key,76,y,w=355,h=18)
ro=section(ro,'rip_church_ro_policies_title',207,tip=True)
for i,k in enumerate(('war','mercy','building','mission')):
    x,y=34+(i%2)*209,248+(i//2)*136
    policy=art('rip_church_'+k+'_slot','GFX_rip_church_policy_slot',8,0)
    policy+=button(f'rip_church_icon_{k}_button',8,0,
                   f'religion = russian_orthodox OR = {{ has_country_flag = rip_church_icon_{k} rip_church_can_activate_{k} = yes }}',
                   f'rip_church_toggle_{k}_effect = yes',sprite='GFX_rip_church_policy_select',label=False)
    policy+=art('rip_church_'+k+'_art','GFX_rip_church_policy_'+k,16,8,0.65625)
    defs.append(f'custom_icon = {{ name = rip_church_{k}_active_frame potential = {{ has_country_flag = rip_church_icon_{k} }} }}')
    policy+=f'iconType = {{ name = "rip_church_{k}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x=8 y=0 }} alwaystransparent = yes }}'
    policy+=state_badge('rip_church_ro_'+k+'_access',47,39,
                       f'OR = {{ has_country_flag = rip_church_icon_{k} rip_church_can_activate_{k} = yes }}',
                       f'rip_church_icon_{k}_button_tt',scale=0.9,click_through=True)
    policy+=text(f'rip_church_icon_{k}_label',76,2,w=114,h=18,tip=False)
    policy+=text(f'rip_church_icon_{k}_state',76,25,w=114,h=18,tip=False)
    policy+=text(f'rip_church_icon_{k}_action',76,48,w=114,h=36)
    policy+=text(f'rip_church_icon_{k}_benefit',8,88,w=182,h=36)
    ro+=card('rip_church_ro_'+k+'_card',x,y,198,124,policy)
ro+=button('rip_church_nodes_button',125,535,'rip_church_ro_can_open_network_menu = yes',
           'country_event = { id = rip_church_nodes.1 }')
ro+=text('rip_church_ro_mission_cost',34,576,w=407,h=36,align='center')
ro+=button('rip_church_reconcile_button',125,613,'rip_church_can_reconcile = yes',
           'rip_church_ro_begin_reconciliation_effect = yes',
           'has_country_flag = rip_church_ro_schismatic')

# ---------------------------------------------------------------------------
# Layout grid for the three Union pages. Window-local pixels; the inner surface
# is x13..462 / y13..647 and every symmetric element mirrors about x=237.5.
#   content box   x34..441 (CW=407): a 21px gutter to the surface on both sides
#   two columns   x34..232 and x243..441 (COL_W=198, 11px gutter, centres 133/342);
#                 the right column is the left one translated by COL_DX=209
#   text rows     12px inset inside the content box: 383px wide, centred on 237.5
#   Even-width sprites (tabs, 58px slots, the 224px row button) centre on 237, half a
#   pixel left of the 475px window's axis: unavoidable with integer positions.
CX,CW=34,407
COL_W,COL_DX=198,209
PAD=12
BODY_TOP=154          # first section banner, identical on every page: gold rail line (y=140) + 14, the same gap as between sections
BODY_DY=41            # banner top -> first row: 29 visible banner rows + 12
SEC_GAP=14            # last row -> next banner
# Two button widths, chosen by the container, never by the label:
#   column action  button_type_8 189x31, inside a 198px column (x+4); clear text area ~155px
#   row action     GFX_standard_button_224 224x32, centred in the 407px content box (x+91 = abs 125, centre 237); clear text area ~190px
BTN='button_type_8'
BTN_W=189
BTN_COL_X=(COL_W-BTN_W)//2     # 4
BTN_ROW='GFX_standard_button_224'
BTN_ROW_W=224
BTN_ROW_X=(CW-BTN_ROW_W)//2     # 91

# ---- Union -----------------------------------------------------------------
gc=church_header('', 'union')
y=BODY_TOP
gc=section(gc,'rip_church_gui_status_title',y,tip=False); y+=BODY_DY
status=text('rip_church_gui_communion_cell',0,0,w=COL_W,h=36,align='center')
status+=text('rip_church_gui_rite_cell',COL_DX,0,w=COL_W,h=36,align='center')
# One row on the window axis: the two counts are one fact (guarantees by faith) and the
# row carries its own tooltip, so it must stay hit-testable.
status+=text('rip_church_gui_count_value',PAD,46,w=383,h=18,align='center')
gc+=card('rip_church_status_card',CX,y,CW,64,status); y+=64+SEC_GAP

gc=section(gc,'rip_church_gui_institutions_title',y,tip=False); y+=BODY_DY
# One cell template for both institutions: the 58px slot and its 72px label form a
# group centred in the 198px column; button and state line share the column centre.
SLOT_X,LABEL_X,LABEL_W=29,97,72
synod=framed('rip_church_synod_symbol','GFX_rip_church_gc_privileges',SLOT_X,0)
synod+=text('rip_church_gui_slot_state',LABEL_X,11,w=LABEL_W,h=36,align='left')
defs.append('custom_icon = { name = rip_church_synod_active_frame potential = { rip_church_gc_has_privilege = yes } tooltip = rip_church_gui_synod_active_tt }')
synod+='iconType = { name = "rip_church_synod_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = { x='+str(SLOT_X)+' y=0 } alwaystransparent = yes }'
synod+=button('rip_church_gc_native_privileges_button',BTN_COL_X,66,'religion = greek_catholic','rip_church_gc_open_synod_effect = yes',sprite=BTN)
synod+=text('rip_church_gui_synod_active',0,103,w=COL_W,h=36,align='center')
gc+=card('rip_church_synod_card',CX,y,COL_W,139,synod)
policy=framed('rip_church_policy_symbol','GFX_rip_church_gc_ecumenism',SLOT_X,0)
policy+=text('rip_church_gui_ecumenism_state',LABEL_X,11,w=LABEL_W,h=36,align='left')
# The check/cross sits on the slot's bottom-right corner, as on the devotional icons.
policy+=state_badge('rip_church_ecumenism_status',SLOT_X+39,39,'OR = { has_country_flag = rip_church_ecumenical rip_church_can_ecumenism = yes }','rip_church_gui_ecumenism_reason_tt',scale=0.9)
policy+=button('rip_church_gui_ecumenism',BTN_COL_X,66,'rip_church_can_ecumenism = yes','rip_church_achieve_ecumenism_effect = yes',sprite=BTN)
policy+=text('rip_church_gui_ecumenism_reason',0,103,w=COL_W,h=36,align='center')
gc+=card('rip_church_ecumenism_card',CX+COL_DX,y,COL_W,139,policy); y+=139+SEC_GAP

gc=section(gc,'rip_church_gc_icons_title',y,feature=True,tip=False); y+=BODY_DY
icons=''
for i,(key,sprite) in enumerate((
    ('liturgy','GFX_rip_church_gc_icon_liturgy'),
    ('learning','GFX_rip_church_gc_icon_learning'),
    ('charity','GFX_rip_church_gc_icon_charity'),
)):
    x=48+i*126                    # abs 82 / 208 / 334: centres 111 / 237 / 363, 68px gaps
    feature_defs.append(f'custom_icon = {{ name = rip_church_gc_icon_{key}_active_frame potential = {{ has_country_modifier = rip_church_gc_icon_{key} }} tooltip = rip_church_gc_icon_{key}_button_tt frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
    icons+=art(f'rip_church_gc_icon_{key}_slot','GFX_rip_church_policy_slot',x,0)
    icons+=feature_button(f'rip_church_gc_icon_{key}_button',x,0,
        f'rip_church_gc_can_activate_icon_{key} = yes',
        f'rip_church_gc_activate_icon_{key}_effect = yes',sprite='GFX_coptic_blessing_select')
    icons+=art(f'rip_church_gc_icon_{key}_art',sprite,x+8,8,0.65625)
    icons+=f'iconType = {{ name = "rip_church_gc_icon_{key}_active_frame" scripted = yes spriteType = "GFX_rip_church_policy_active" position = {{ x={x} y=0 }} alwaystransparent = yes }}'
    blocked_name=f'rip_church_gc_icon_{key}_blocked'
    feature_defs.append(f'custom_icon = {{ name = {blocked_name} potential = {{ NOT = {{ has_country_modifier = rip_church_gc_icon_{key} }} NOT = {{ rip_church_gc_can_activate_icon_{key} = yes }} }} tooltip = rip_church_gc_icon_{key}_button_tt }}')
    icons+=f'iconType = {{ name = "{blocked_name}" scripted = yes spriteType = "GFX_text_no" position = {{ x={x+39} y=39 }} scale = 0.9 }}'
    icons+=feature_text(f'rip_church_gc_icon_{key}_state',x-31,59,w=120,h=40,font='vic_18',align='center')
icons+=feature_text('rip_church_gc_icons_note',PAD,103,w=383,h=18,font='vic_18',align='center')
gc+=card('rip_church_devotional_card',CX,y,CW,121,icons)

# ---- Community rights register (legacy route, third page of the same window) --
parishes=church_header('', 'parishes')
y=BODY_TOP
parishes=section(parishes,'rip_church_gui_parish_list_title',y); y+=BODY_DY
register=text('rip_church_gui_register_columns',PAD,0,w=383,h=20,font='vic_18',tip=False)
register+=text('rip_church_gui_parish_empty_state',PAD,28,w=383,h=108,font='vic_18',align='center')
register+=text('rip_church_gui_recognition_cost',PAD,144,w=383,h=72,font='vic_18',align='center',tip=False)
register+=text('rip_church_gui_recognition_reason',PAD,224,w=383,h=36,font='vic_18',align='center',tip=False)
register+=button('rip_church_gui_recognize_parish',BTN_ROW_X,268,'always = no','rip_church_gui_open_parishes_effect = yes',sprite=BTN_ROW)
parishes+=card('rip_church_register_card',CX,y,CW,300,register)

# ---- Curia -------------------------------------------------------------------
curia=church_header('', 'curia')
y=BODY_TOP
curia=section(curia,'rip_church_gc_curia_heading',y,tip=False); y+=BODY_DY
# Same cell template as the Union institutions: icon, then a left-aligned label
# whose left edge never moves; the 32px shield group is centred in its 198px column.
SH_X,SH_LABEL_X,SH_LABEL_W=22,64,112
see=shield('rip_church_gc_pope_shield',SH_X,0,'rip_church_gc_rome',
              'has_global_flag = rip_church_gc_rome_known rip_church_gc_rome_present = yes','GFX_shield_small')
see+=feature_text('rip_church_gc_curia_note',SH_LABEL_X,0,w=SH_LABEL_W,h=54,font='vic_18',align='left')
see+=shield('rip_church_gc_controller_shield',COL_DX+SH_X,0,'rip_church_gc_controller',
            'has_global_flag = rip_church_gc_controller_known event_target:rip_church_gc_controller = { is_papal_controller = yes }','GFX_shield_small')
see+=text('rip_church_gc_controller_readout',COL_DX+SH_LABEL_X,0,w=SH_LABEL_W,h=54,font='vic_18',align='left')
curia+=card('rip_church_see_card',CX,y,CW,54,see); y+=54+SEC_GAP

curia=section(curia,'rip_church_gc_contact_title',y); y+=BODY_DY
# Action group: button, one price/effect line, one state line, all on the axis.
# The check/cross sits 8px right of the button, so it never depends on text width.
BADGE_X=BTN_ROW_X+BTN_ROW_W+8
contact=feature_button('rip_church_gc_deputation_button',BTN_ROW_X,0,
                      'rip_church_gc_can_depute_to_curia = yes',
                      'rip_church_gc_depute_to_curia_effect = yes',
                      sprite=BTN_ROW,label=True)
contact+=state_badge('rip_church_deputation_status',BADGE_X,6,'rip_church_gc_can_depute_to_curia = yes','rip_church_gui_contact_history_tt')
contact+=text('rip_church_gui_contact_cost',PAD,37,w=383,h=20,font='vic_18',align='center')
contact+=text('rip_church_gui_contact_history',PAD,61,w=383,h=36,font='vic_18',align='center')
contact+=feature_button('rip_church_gc_holy_see_gift_button',BTN_ROW_X,105,
                        'rip_church_gc_can_offer_gift_to_holy_see = yes',
                        'rip_church_gc_offer_gift_to_holy_see_effect = yes',
                        sprite=BTN_ROW,label=True)
contact+=state_badge('rip_church_gift_status',BADGE_X,111,'rip_church_gc_can_offer_gift_to_holy_see = yes','rip_church_gc_holy_see_gift_state_tt')
contact+=text('rip_church_gc_holy_see_gift_summary',PAD,142,w=383,h=20,font='vic_18',align='center')
contact+=text('rip_church_gc_holy_see_gift_state',PAD,166,w=383,h=36,font='vic_18',align='center')
curia+=card('rip_church_contact_card',CX,y,CW,202,contact)

# Catholic/Orthodox Union paths remain in their existing events and decisions.
# Do not advertise them through a permanent religion sidebar.
religion_panels=(panel('rip_church_ro_panel','religion = russian_orthodox NOT = { has_country_flag = rip_church_ro_window_hidden }',ro,clean=True)+'\n'+
                panel('rip_church_gc_panel','religion = greek_catholic NOT = { has_country_flag = rip_church_gc_window_hidden } NOT = { has_country_flag = rip_church_gc_curia_view } NOT = { has_country_flag = rip_church_gui_parishes_view }',gc,clean=True)+'\n'+
                panel('rip_church_gc_curia_panel','religion = greek_catholic NOT = { has_country_flag = rip_church_gc_window_hidden } has_country_flag = rip_church_gc_curia_view NOT = { has_country_flag = rip_church_gui_parishes_view }',curia,clean=True)+'\n'+
                panel('rip_church_gc_parishes_panel','OR = { religion = greek_catholic rip_church_union_supporter = yes } NOT = { has_country_flag = rip_church_gc_window_hidden } has_country_flag = rip_church_gui_parishes_view',parishes,clean=True))
# Keep the window control beside Defender of the Faith and outside the pages it
# toggles, so it remains available while the Greek Catholic window is hidden.
gc_window_toggle=button(
    'rip_church_gc_window_toggle',372,238,'religion = greek_catholic',
    'if = { limit = { has_country_flag = rip_church_gc_window_hidden } clr_country_flag = rip_church_gc_window_hidden } else = { set_country_flag = rip_church_gc_window_hidden }',
    potential='religion = greek_catholic',sprite='GFX_closebutton2',label=False,
    scale=0.7)
religion_panels += '\n' + gc_window_toggle
outputs['interface/RIP_church_panels.gfx']='spriteTypes = {\n'+'\n'.join(insets)+'''
 spriteType = {
  name = "GFX_rip_church_ro_frame"
  textureFile = "gfx/interface/copts_bg.dds"
 }
 spriteType = { name = "GFX_rip_church_policy_slot" textureFile = "gfx/interface/copts_blessing_slot.dds" }
 spriteType = { name = "GFX_rip_church_policy_select" textureFile = "gfx/interface/copts_blessing_slot.dds" effectFile = "gfx/FX/buttonstate.lua" }
 spriteType = { name = "GFX_rip_church_policy_active" textureFile = "gfx/interface/copts_blessing_select_glow.dds" }
 spriteType = { name = "GFX_rip_church_policy_war" textureFile = "gfx/interface/ideas_EU4/land_morale.dds" }
 spriteType = { name = "GFX_rip_church_policy_mercy" textureFile = "gfx/interface/ideas_EU4/global_unrest.dds" }
 spriteType = { name = "GFX_rip_church_policy_building" textureFile = "gfx/interface/ideas_EU4/development_cost.dds" }
 spriteType = { name = "GFX_rip_church_policy_mission" textureFile = "gfx/interface/ideas_EU4/global_missionary_strength.dds" }
 spriteType = { name = "GFX_rip_church_ro_fervor" textureFile = "gfx/interface/ideas_EU4/monthly_fervor_increase.dds" }
 spriteType = { name = "GFX_rip_church_ro_authority" textureFile = "gfx/interface/ideas_EU4/church_privilege_slots.dds" }
 spriteType = { name = "GFX_rip_church_ro_network" textureFile = "gfx/interface/ideas_EU4/global_trade_power.dds" }
 spriteType = { name = "GFX_rip_church_gc_privileges" textureFile = "gfx/interface/ideas_EU4/church_privilege_slots.dds" }
 spriteType = { name = "GFX_rip_church_gc_ecumenism" textureFile = "gfx/interface/ideas_EU4/improve_relation_modifier.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_liturgy" textureFile = "gfx/interface/rip_church/gc_icon_liturgy.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_learning" textureFile = "gfx/interface/rip_church/gc_icon_learning.dds" }
 spriteType = { name = "GFX_rip_church_gc_icon_charity" textureFile = "gfx/interface/rip_church/gc_icon_charity.dds" }
 spriteType = { name = "GFX_rip_church_gc_capacity_low" textureFile = "gfx/interface/rip_church/gc_archbishop_low.dds" }
 spriteType = { name = "GFX_rip_church_gc_capacity_high" textureFile = "gfx/interface/rip_church/gc_archbishop_high.dds" }
 corneredTileSpriteType = { name = "GFX_rip_church_gc_selector_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=82 y=100 } borderSize = { x=8 y=8 } }
 corneredTileSpriteType = { name = "GFX_rip_church_gc_state_surface" textureFile = "gfx/interface/copts_blessing_slot.dds" size = { x=464 y=50 } borderSize = { x=8 y=8 } }
}
'''
# Province ROOT, clicking country FROM. Never allow buttons on somebody else's land.
province=art('rip_church_rite_window_banner','GFX_rip_church_window_banner',18,19,0.94)
province+=text('rip_church_rite_heading',58,35,w=359,h=24,font='vic_22',align='center')
province+=button('rip_church_rite_panel_hide_button',436,2,'owned_by = FROM',
                 'set_province_flag = rip_church_rite_panel_hidden',
                 sprite='GFX_closebutton2',label=False)
province+=card('rip_church_rite_header',34,73,407,30,
               text('rip_church_rite_state',8,8,w=391,h=22,font='vic_18',align='center'))
province=section(province,'rip_church_rite_effects_title',112)
province+=text('rip_church_rite_effects',34,154,w=407,h=54,font='vic_18',align='center')
province+=button('rip_church_recognize_rite_button',125,223,'owned_by = FROM rip_church_can_recognize_rite = yes','rip_church_recognize_rite_effect = yes',potential='NOT = { has_province_flag = rip_church_rite_recognized }')
province+=button('rip_church_revoke_rite_button',125,223,'owned_by = FROM rip_church_can_revoke_rite = yes','rip_church_revoke_rite_effect = yes',potential='has_province_flag = rip_church_rite_recognized')
province+=text('rip_church_rite_note',58,267,w=359,h=18,font='vic_18',align='center')
# Shown only where the action applies or is already in force, not on every owned province.
province_gate='owned_by = FROM FROM = { religion = greek_catholic } OR = { has_province_flag = rip_church_rite_recognized AND = { is_city = yes controlled_by = owner OR = { religion = orthodox religion = russian_orthodox religion = catholic } } }'
prov_panel=panel('rip_church_rite_panel',province_gate+' NOT = { has_province_flag = rip_church_rite_panel_hidden }',province,x=480,y=0)
# Hide state belongs to the selected province. The reopen button sits in the
# state window at the native metropolitan action's position.
defs.append(f'custom_window = {{ name = rip_church_rite_reopen_panel potential = {{ {province_gate} has_province_flag = rip_church_rite_panel_hidden }} }}')
defs.append('custom_window = { name = rip_church_gc_state_cover potential = { FROM = { religion = greek_catholic } } }')
prov_state_cover='''windowType = {
 name = "rip_church_gc_state_cover" scripted = yes position = { x=19 y=414 } size = { x=464 y=50 }
 moveable = 0
 iconType = { name = "rip_church_gc_state_surface" spriteType = "GFX_rip_church_gc_state_surface" position = { x=0 y=0 } alwaystransparent = no }
}'''
prov_reopen_button=button('rip_church_rite_panel_show_button',0,0,'owned_by = FROM',
                          'clr_province_flag = rip_church_rite_panel_hidden',
                          sprite='button_type_8')
prov_reopen_panel=f'''windowType = {{
 name = "rip_church_rite_reopen_panel" scripted = yes position = {{ x=156 y=423 }} size = {{ x=189 y=31 }}
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
defs.append('custom_icon = { name = current_patriarch_authority_progress_frame potential = { always = yes } tooltip = rip_church_authority_heading_tt }')
# The native percentage rides the moving marker for both faiths. Only the heading needs a
# Greek Catholic copy: the shared one sits 3px left of the bar centre.
defs.append('custom_text_box = { name = rip_church_gc_capacity_heading potential = { religion = greek_catholic } tooltip = rip_church_authority_heading_tt }')
defs.append('custom_icon = { name = rip_church_gc_union_symbol potential = { NOT = { has_country_modifier = rip_church_gc_infrastructure } NOT = { has_country_modifier = rip_church_gc_coexistence } } frame = { number = 31 trigger = { always = yes } } }')
for key in ('infrastructure','coexistence'):
    defs.append(f'custom_icon = {{ name = rip_church_gc_synod_{key}_symbol potential = {{ has_country_modifier = rip_church_gc_{key} }} frame = {{ number = 1 trigger = {{ always = yes }} }} }}')
native_controls='''windowType = {
 name = "rip_church_gc_native_controls" scripted = yes
 position = { x=0 y=0 } size = { x=280 y=50 } moveable = 0
 instantTextBoxType = { name = "rip_church_gc_capacity_heading" scripted = yes position = { x=53 y=255 } font = "vic_18" text = "rip_church_gc_capacity_heading" maxWidth = 256 maxHeight = 24 format = center }
 iconType = { name = "rip_church_gc_capacity_low_icon" scripted = yes spriteType = "GFX_rip_church_gc_capacity_low" position = { x=54 y=274 } }
 iconType = { name = "rip_church_gc_capacity_high_icon" scripted = yes spriteType = "GFX_rip_church_gc_capacity_high" position = { x=270 y=275 } }
 iconType = { name = "rip_church_gc_selector_cover" spriteType = "GFX_rip_church_gc_selector_surface" position = { x=303 y=232 } alwaystransparent = no }
 iconType = { name = "rip_church_gc_union_symbol" scripted = yes spriteType = "GFX_country_icon_religion" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_infrastructure_symbol" scripted = yes spriteType = "GFX_rip_church_gc_privileges" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
 iconType = { name = "rip_church_gc_synod_coexistence_symbol" scripted = yes spriteType = "GFX_rip_church_gc_ecumenism" position = { x=319 y=244 } scale = 0.8 alwaystransparent = yes }
'''+'\n}\n'

# Replace the empty native selector with a working route to the policy pane.
# Keep the engine-owned controls underneath, just as for the Union selector.
defs.append('custom_window = { name = rip_church_ro_native_controls potential = { religion = russian_orthodox } }')
ro_native_controls='''windowType = {
 name = "rip_church_ro_native_controls" scripted = yes
 position = { x=0 y=0 } size = { x=280 y=50 } moveable = 0
 iconType = { name = "rip_church_ro_selector_cover" spriteType = "GFX_rip_church_gc_selector_surface" position = { x=303 y=232 } alwaystransparent = no }
 iconType = { name = "rip_church_ro_selector_symbol" spriteType = "GFX_rip_church_policy_mission" position = { x=322 y=244 } scale = 0.65625 alwaystransparent = yes }
'''+button('rip_church_ro_window_toggle',304,300,'religion = russian_orthodox',
           'if = { limit = { has_country_flag = rip_church_ro_window_hidden } clr_country_flag = rip_church_ro_window_hidden } else = { set_country_flag = rip_church_ro_window_hidden }',
           sprite='GFX_standard_button_71')+'\n}\n'
def attach(file,host,body):
    s=(GAME/'interface'/file).read_text(encoding='utf-8-sig')
    if file=='provinceview.gui':
        # State is a documented province-scoped host. Cover the native row only
        # for GC, preserving the engine-managed Orthodox button and callback.
        state_name=re.search(r'name\s*=\s*"state_window"',s)
        state_start=s.rfind('windowType',0,state_name.start())
        state_end=matching_brace(s,s.index('{',state_start))
        s=s[:state_end].rstrip()+'\n'+prov_state_cover+'\n'+prov_reopen_panel+'\n\t\t'+s[state_end:]
    if file=='countryreligionview.gui':
        for widget in ('current_patriarch_authority_progress_frame',):
            s=re.sub(r'(name\s*=\s*"'+widget+r'")',r'\1 scripted = yes',s)
        for level in ('low','high'):
            s=re.sub(r'(name\s*=\s*"'+level+r'_patriarch_authority")(?!\s*scripted)',r'\1 scripted = yes',s)
        # Native text boxes do not evaluate our country-scoped custom readout.
        # Bind the replacement as scripted text, preserving the native geometry.
        s=s.replace('name = "current_patriarch_authority_text"',
                    'name = "rip_church_authority_heading" scripted = yes')
        s=re.sub(r'text = "CURRENT_PATRIARCH_AUTHORITY"[ \t]*', 'text = "rip_church_authority_heading"', s)
        defs.append('custom_text_box = { name = rip_church_authority_heading potential = { NOT = { religion = greek_catholic } } tooltip = rip_church_authority_heading_tt }')
        native_name=re.search(r'name\s*=\s*"orthodox_specific_window"',s)
        native_start=s.rfind('windowType',0,native_name.start())
        native_end=matching_brace(s,s.index('{',native_start))
        s=s[:native_end]+'\n# RIP resource hover and functional replacements for retired native selectors.\n'+native_controls+native_anchors(ro_native_controls)+s[native_end:]
    name=re.search(r'name\s*=\s*"'+re.escape(host)+r'"',s)
    assert name, host
    start=s.rfind('windowType',0,name.start())
    opening=s.index('{',start); end=matching_brace(s,opening)
    outputs['interface/'+file]=s[:end]+'\n# RIP church custom controls, descendants of the supported host.\n'+body+'\n'+s[end:]
# Explicit local anchors; scripted tooltip remains the authoritative dynamic
# binding. pdx_tooltip also covers the native GUI hover path.
def native_anchors(source):
    def anchor(m):
        name=m[2]
        tip='' if name in NO_TIP or name.endswith('_panel') else ' pdx_tooltip = "'+name+'_tt"'
        # This replacement shares the native Select button's host and offsets.
        orientation='LEFT' if name=='rip_church_ro_window_toggle' else 'UPPER_LEFT'
        return m[1]+' Orientation = "'+orientation+'"'+tip
    source=re.sub(r'(name = "([^"]+)" scripted = yes position = \{[^}]+\})',anchor,source)
    source=re.sub(r'(position = \{[^}]+\})( scale =)',r'\1 Orientation = "UPPER_LEFT"\2',source)
    return source
attach('countryreligionview.gui','countryreligionview',native_anchors(religion_panels))
attach('provinceview.gui','province_window',prov_panel)
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
