"""Source-layout preview with vanilla textures/fonts; not an EU4 screenshot.
Checks text overflow while rendering the generated GC pane at native pixel size.
"""
from pathlib import Path
import argparse, re, sys
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from clausewitz_testlib import ROOT, vanilla_root, keyed_blocks
from church_testlib import parse
GAME=vanilla_root()
ap=argparse.ArgumentParser(); group=ap.add_mutually_exclusive_group()
for option in ('ro','paths','province'): group.add_argument('--'+option,action='store_true')
args=ap.parse_args()
branch='ro' if args.ro else 'union_paths' if args.paths else 'rite' if args.province else 'gc'
loc=dict(re.findall(r'^\s+(\w+):0 "(.*)"$',(ROOT/'localisation/replace/zzzz_RIP_church_redesign_l_english.yml').read_text(encoding='utf-8-sig'),re.M))
sample={'Root.GetChurchPrivilege':'Agreement on coexistence'}
sample.update({'Root.GetChurchROStatus':'Reconciliation in progress',
 'Root.rip_church_fervor.GetValue':'100','Root.rip_church_icons.GetValue':'4',
 'Root.rip_church_capacity.GetValue':'4','Root.rip_church_fervor_income.GetValue':'5',
 'Root.rip_church_fervor_cost.GetValue':'18','Root.rip_church_nodes.GetValue':'2'})
for key in ('War','Mercy','Building','Mission'): sample['Root.GetChurchIcon'+key]='Active'
sample.update({'Root.GetChurchCuriaStatus':'Rome is present; diplomatic audience available',
 'Root.GetChurchLocalInstitution':'Agreement on coexistence'})
sample.update({'Root.GetChurchSlotState':'Synodal institution: §Y1 / 1§!',
 'Root.GetChurchCoexistenceState':'§GCompact of coexistence active§!',
 'Root.rip_church_gui_eastern_parishes.GetValue':'999',
 'Root.rip_church_gui_latin_parishes.GetValue':'999',
 'Root.GetChurchUnionPathState':'Catholic patronage of Eastern parishes',
 'Root.GetChurchUnionPathIdentity':'Patronage preserves our Catholic confession.\\nAn Eastern founding parish enters the Union.',
 'Root.GetChurchFlorenceProgress':'Term complete: settlement conditions must hold',
 'Root.GetChurchPatronState':'Catholic patronage is established',
 'Root.GetChurchRiteStatus':'The Latin parish has consented to gradual Byzantine integration.',
 'Root.GetChurchRiteFamily':'Latin'})
def resolve(key):
    return re.sub(r'\[([^]]+)\]',lambda m:sample[m[1]],loc[key]).replace('\\n','\n')
def asset(path):
    p=GAME/path
    if not p.exists(): p=p.with_suffix('.dds')
    return Image.open(p).convert('RGBA')
def tile(path,w,h,b):
    src=asset(path); sw,sh=src.size; dst=Image.new('RGBA',(w,h))
    for sx,ex,dx,tx in [(0,b,0,b),(b,sw-b,b,w-b),(sw-b,sw,w-b,w)]:
        for sy,ey,dy,ty in [(0,b,0,b),(b,sh-b,b,h-b),(sh-b,sh,h-b,h)]:
            patch=src.crop((sx,sy,ex,ey)).resize((tx-dx,ty-dy))
            dst.alpha_composite(patch,(dx,dy))
    return dst
fonts={}
def font(name):
    if name not in fonts:
        stem='garamond_14' if name=='Main_14' else name
        spec=(GAME/f'gfx/fonts/{stem}.fnt').read_text()
        chars={}
        for line in spec.splitlines():
            if line.startswith('char '):
                c={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}; chars[c['id']]=c
        fonts[name]=(int(re.search(r'lineHeight=(\d+)',spec)[1]),chars,asset(f'gfx/fonts/{stem}.tga'))
    return fonts[name]
def draw_text(canvas,s,x,y,w,h,name,center=False):
    line_height,chars,atlas=font(name)
    def width(t): return sum(chars[ord(c)]['xadvance'] for c in re.sub('§.','',t))
    palette={'Y':(255,215,80),'G':(100,220,95),'R':(235,90,80),'H':(240,175,80)}
    color=None
    lines=[]
    for paragraph in s.split('\n'):
        line=''
        for word in paragraph.split():
            candidate=(line+' '+word).strip()
            if width(candidate)>w and line: lines.append(line); line=word
            else: line=candidate
        lines.append(line)
    assert len(lines)*line_height<=h,(s,len(lines)*line_height,h)
    for line in lines:
        assert width(line)<=w,(line,width(line),w)
        cursor=x+(w-width(line))//2 if center else x
        tokens=re.findall('§.|[^§]',line)
        for ch in tokens:
            if ch.startswith('§'):
                color=palette.get(ch[1]); continue
            c=chars[ord(ch)]; glyph=atlas.crop((c['x'],c['y'],c['x']+c['width'],c['y']+c['height']))
            if color and c['width'] and c['height']:
                tint=Image.new('RGBA',glyph.size,color); tint.putalpha(glyph.getchannel('A')); glyph=tint
            if c['width'] and c['height']: canvas.alpha_composite(glyph,(cursor+c['xoffset'],y+c['yoffset']))
            cursor+=c['xadvance']
        y+=line_height
source=(ROOT/('interface/provinceview.gui' if args.province else 'interface/countryreligionview.gui')).read_text()
panel=next(block for _,block in keyed_blocks(source,'windowType') if re.search(r'\bname\s*=\s*"([^"]+)"',block)[1]=='rip_church_'+branch+'_panel')
entries=dict(parse(panel))['windowType']
dimensions=dict(dict(entries)['size']); panel_w,panel_h=int(dimensions['x']),int(dimensions['y'])
canvas=Image.new('RGBA',(panel_w,panel_h),(22,30,33,255))
sprite_paths={'GFX_country_religion_view_bg':'gfx/interface/defender_of_the_faith/country_religion_view_bg.dds'}
tiles={}
for _,block in keyed_blocks((ROOT/'interface/RIP_church_panels.gfx').read_text(),'corneredTileSpriteType'):
    d=dict(dict(parse(block))['corneredTileSpriteType']); dims=dict(d['size'])
    tiles[d['name']]=tile(d['textureFile'],int(dims['x']),int(dims['y']),int(dict(d['borderSize'])['x']))
for _,block in keyed_blocks((ROOT/'interface/RIP_church_panels.gfx').read_text(),'spriteType'):
    d=dict(dict(parse(block))['spriteType']); sprite_paths[d['name']]=d['textureFile']
rects=[]
bindings={dict(dict(parse(b))['custom_button'])['name']:dict(dict(parse(b))['custom_button']) for _,b in keyed_blocks((ROOT/'common/custom_gui/RIP_church_controls.txt').read_text(),'custom_button')}
for kind,payload in entries:
    if kind not in ('iconType','instantTextBoxType','guiButtonType'): continue
    d=dict(payload); pos=dict(d['position']); x,y=int(pos['x']),int(pos['y'])
    if kind=='iconType':
        if d['spriteType'] in sprite_paths or d['spriteType'] in tiles or d['spriteType']=='GFX_icon_powers_administrative':
            art=tiles[d['spriteType']] if d['spriteType'] in tiles else asset('gfx/interface/icon_powers_administrative.tga' if d['spriteType']=='GFX_icon_powers_administrative' else sprite_paths[d['spriteType']])
            if 'scale' in d:
                factor=float(d['scale']); art=art.resize((round(art.width*factor),round(art.height*factor)))
            canvas.alpha_composite(art,(x,y))
            continue
        if d['spriteType']=='GFX_message_band':
            banner=asset('gfx/interface/message_band.tga')
            banner=banner.resize((round(banner.width*float(d['scale'])),round(banner.height*float(d['scale']))))
            canvas.alpha_composite(banner,(x,y))
            continue
        outer=d['spriteType']=='GFX_rip_church_union_frame'
        canvas.alpha_composite(tile('gfx/interface/'+('tiles_dialog.dds' if outer else 'small_tiles_dialog.dds'),475 if outer else 419,680 if outer else 106,32 if outer else 8),(x,y))
        continue
    if kind=='guiButtonType':
        small=d['quadTextureSprite']=='GFX_standard_button_142_34_button'
        native=d['quadTextureSprite']
        if native in tiles: sprite=tiles[native]
        elif native in sprite_paths: sprite=asset(sprite_paths[native])
        elif native=='button_type_1': sprite=asset('gfx/interface/button_type_1.tga')
        elif native=='GFX_tab_small_116':
            sprite=asset('gfx/interface/tab_small_116.dds')
            n=int(dict(bindings[d['name']]['frame'])['number'])-1
            sprite=sprite.crop((n*116,0,(n+1)*116,36))
        elif native in ('GFX_shield_medium','GFX_shield_small'):
            mini=native=='GFX_shield_small'
            sprite=asset('gfx/interface/small_shield_overlay.dds' if mini else 'gfx/interface/shield_medium_overlay.dds')
            mask=asset('gfx/interface/small_shield_mask.tga' if mini else 'gfx/interface/shield_medium_mask.tga')
            flag=asset('gfx/flags/FRA.tga' if mini else 'gfx/flags/PAP.tga').resize(mask.size)
            flag.putalpha(mask.getchannel('A')); flag.alpha_composite(sprite); sprite=flag
        elif native=='GFX_papacy_action_strip':
            sprite=asset('gfx/interface/papacy_action_strip.dds'); w=sprite.width//9
            n=int(dict(bindings[d['name']]['frame'])['number'])-1
            sprite=sprite.crop((n*w,0,(n+1)*w,sprite.height))
        elif native=='GFX_buy_indulgence_button': sprite=asset('gfx/interface/buy_indulgence_button.dds')
        else:
            assert native in ('GFX_standard_button_142_34_button','GFX_standard_button_105','GFX_standard_button_224'),native
            sprite=asset('gfx/interface/buttons/button_142_animated.dds' if small else 'gfx/interface/standard_button_105.dds' if native=='GFX_standard_button_105' else 'gfx/interface/standard_button_224.dds')
        if small: sprite=sprite.crop((0,0,sprite.width//3,sprite.height))
        w,h=sprite.size
        canvas.alpha_composite(sprite,(x,y))
        if d.get('buttonText'): draw_text(canvas,resolve(d['buttonText']),x+8,y+(h-18)//2,w-16,18,'vic_18',True)
    else:
        w,h=int(d['maxWidth']),int(d['maxHeight'])
        draw_text(canvas,resolve(d['text']),x,y,w,h,d['font'],d['format']=='center')
    assert x>=0 and y>=0 and x+w<=panel_w and y+h<=panel_h,d['name']
    for a,b,c,e,label in rects:
        assert x+w<=a or a+c<=x or y+h<=b or b+e<=y,(d['name'],label)
    rects.append((x,y,w,h,d['name']))
output=ROOT/f'diagnostics/church_redesign_20260911/{branch}_layout_preview.png'
canvas.save(output)
print(f'SOURCE LAYOUT PASS: {len(rects)} non-overlapping controls; native font metrics; {output}')
print('Preview uses sample values and is not an engine render or click test.')
