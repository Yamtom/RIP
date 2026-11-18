"""Render every RIP window from source, using an explicitly labelled asset donor.

Not an engine renderer: no trigger execution, hover, shaders or live numeric data.
Creates normal/long-text samples, geometry findings and an HTML contact sheet.
"""
from pathlib import Path
import argparse
import html
import json
import re
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from audit_diplomacy_history import province_tree
from audit_country_history import ROOT, read


def clean(value):
    return value.strip('"') if isinstance(value, str) else value


def fields(items):
    return {k.lower(): clean(v) for k, v in items}


def walk(items, parents=()):
    for kind, value in items:
        if not isinstance(value, list):
            continue
        d = fields(value)
        if kind.lower() == 'windowtype':
            name = d.get('name', '?')
            yield name, value, parents
            yield from walk(value, parents + (name,))
        else:
            yield from walk(value, parents)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--donor', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=ROOT / 'outputs/interface-review')
    args = ap.parse_args()
    game, out = args.donor, args.out
    out.mkdir(parents=True, exist_ok=True)
    version = json.loads(read(game / 'launcher-settings.json')).get('version', '?')
    loc = {}
    for directory in (game / 'localisation', ROOT / 'localisation'):
        paths = sorted(directory.rglob('*_l_english.yml'), key=lambda p: ('replace' in p.parts, str(p)))
        for p in paths:
            loc.update(re.findall(r'^\s*([^\s:]+):\d*\s*"(.*)"', read(p), re.M))
    dynamic = {}
    for p in (ROOT / 'customizable_localization').glob('*.txt'):
        for kind, val in province_tree(read(p)):
            if kind == 'defined_text':
                d = fields(val)
                dynamic[d['name']] = [fields(x).get('localisation_key', '') for k, x in val if k == 'text']
    sprites = {}
    for directory in (game / 'interface', ROOT / 'interface'):
        for p in sorted(directory.glob('*.gfx')):
            for _, entries in province_tree(read(p)):
                if not isinstance(entries, list):
                    continue
                for kind, val in entries:
                    if isinstance(val, list):
                        d = fields(val)
                        if 'name' in d:
                            sprites[d['name']] = (kind.lower(), d)
    issues = []
    current = ''

    def issue(kind, name, detail):
        entry = dict(panel=current, kind=kind, name=name, detail=detail)
        if entry not in issues:
            issues.append(entry)

    def resolve(value, stress=False, depth=0):
        if depth > 7:
            return '…'
        value = loc.get(value, value)
        def expression(m):
            key = m[1].split('.', 1)[-1]
            if key in dynamic:
                choices = [resolve(x, stress, depth+1) for x in dynamic[key]]
                return max(choices, key=len) if stress else choices[-1]
            if key.endswith('GetValue'):
                return '9999' if stress else '50'
            if key.endswith('GetName'):
                return 'Commonwealth of Ruthenia' if stress else 'Kyiv'
            issue('sample_expression', key, 'Rendered as sample state; no runtime evaluation')
            return 'State'
        value = re.sub(r'\[([^]]+)\]', expression, value)
        value = re.sub(r'\$([^$]+)\$', lambda m: resolve(m[1], stress, depth+1) if m[1] in loc else '50', value)
        return re.sub('[\x15§].', '', value).replace('\\n', '\n').replace('\\"', '"')

    @lru_cache(None)
    def asset(name):
        name = name.replace('//', '/')
        for base in (ROOT, game):
            p = base / name
            for candidate in (p, p.with_suffix('.dds')):
                if candidate.is_file():
                    return Image.open(candidate).convert('RGBA')
        raise FileNotFoundError(name)

    def dimensions(d, key, default=(0, 0)):
        if key not in d:
            return default
        f = fields(d[key])
        return tuple(int(float(f.get(k, default[i]))) for i, k in enumerate(('x', 'y')))

    def sprite(name, target=None):
        if name not in sprites:
            raise FileNotFoundError(name)
        kind, d = sprites[name]
        im = asset(d['texturefile'])
        frames = int(d.get('noofframes', 1))
        if frames > 1:
            im = im.crop((0, 0, im.width // frames, im.height))
        if kind == 'corneredtilespritetype':
            w, h = target or dimensions(d, 'size', im.size)
            bx, by = dimensions(d, 'bordersize', (8, 8))
            bx, by = min(bx, im.width//2, w//2), min(by, im.height//2, h//2)
            canvas = Image.new('RGBA', (w, h))
            for a,b,c,e in ((0,bx,0,bx),(bx,im.width-bx,bx,w-bx),(im.width-bx,im.width,w-bx,w)):
                for f,g,j,k in ((0,by,0,by),(by,im.height-by,by,h-by),(im.height-by,im.height,h-by,h)):
                    if e>c and k>j and b>a and g>f:
                        canvas.alpha_composite(im.crop((a,f,b,g)).resize((e-c,k-j)), (c,j))
            im = canvas
        elif target:
            im = im.resize(target)
        return im.copy()

    @lru_cache(None)
    def bitmap(name):
        stem = 'garamond_14' if name == 'Main_14' else name
        p = game / f'gfx/fonts/{stem}.fnt'
        spec = read(p)
        chars = {}
        for line in spec.splitlines():
            if line.startswith('char '):
                c = {k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',line)}
                chars[c['id']] = c
        return int(re.search(r'lineHeight=(\d+)',spec)[1]), chars, asset(f'gfx/fonts/{stem}.tga')

    def text(canvas, label, s, box, font, center, mode):
        x,y,w,h = box
        try:
            lh, chars, atlas = bitmap(font)
        except (OSError, TypeError):
            issue('font_fallback', label, font)
            ImageDraw.Draw(canvas).text((x,y),s,fill='#f5ead0',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14))
            return
        def width(t):
            return sum(chars.get(ord(ch),chars.get(63,{'xadvance':8}))['xadvance'] for ch in t)
        lines = []
        for p in s.split('\n'):
            line = ''
            for word in p.split():
                test = (line+' '+word).strip()
                if line and width(test) > w:
                    lines.append(line); line=word
                else:
                    line=test
            lines.append(line)
        if len(lines)*lh > h or any(width(line)>w for line in lines):
            issue('text_overflow',label,dict(mode=mode,required_height=len(lines)*lh,available_height=h,text=s))
        for line in lines:
            cursor = x+(w-width(line))//2 if center else x
            for ch in line:
                c = chars.get(ord(ch),chars.get(63))
                if not c:
                    continue
                glyph=atlas.crop((c['x'],c['y'],c['x']+c['width'],c['y']+c['height']))
                if c['width'] and c['height']:
                    canvas.alpha_composite(glyph,(cursor+c['xoffset'],y+c['yoffset']))
                cursor+=c['xadvance']
            y+=lh

    def render(entries, canvas, mode, offset=(0,0)):
        for kind, value in entries:
            if not isinstance(value,list):
                continue
            d=fields(value); label=d.get('name',kind)
            px,py=dimensions(d,'position');x,y=offset[0]+px,offset[1]+py
            k=kind.lower()
            if k=='windowtype':
                render(value,canvas,mode,(x,y));continue
            if k not in ('icontype','guibuttontype','instanttextboxtype','textboxtype'):
                continue
            if k in ('instanttextboxtype','textboxtype'):
                w,h=int(d.get('maxwidth',200)),int(d.get('maxheight',30))
                s=resolve(d.get('text',''),mode=='long')
                if d.get('text','').startswith('rip_') and d.get('text') not in loc:
                    issue('missing_localization',label,d.get('text'))
                text(canvas,label,s,(x,y,w,h),d.get('font','vic_18'),d.get('format')=='center',mode)
            else:
                name=d.get('spritetype',d.get('quadtexturesprite',''))
                try:
                    art=sprite(name,dimensions(d,'size') if 'size' in d else None)
                except (OSError,KeyError,ValueError):
                    issue('missing_sprite_or_texture',label,name)
                    art=Image.new('RGBA',(32,32),'#713f61')
                    ImageDraw.Draw(art).text((8,8),'?',fill='white')
                scale=float(d.get('scale',1));w,h=max(1,round(art.width*scale)),max(1,round(art.height*scale))
                if art.size!=(w,h): art=art.resize((w,h))
                canvas.alpha_composite(art,(x,y))
                if d.get('buttontext'):
                    text(canvas,label,resolve(d['buttontext'],mode=='long'),(x+6,y+(h-18)//2,w-12,18),d.get('buttonfont','vic_18'),True,mode)
            if not (x>=0 and y>=0 and x+w<=canvas.width and y+h<=canvas.height):
                issue('canvas_bounds',label,dict(box=[x,y,w,h],canvas=canvas.size))

    pages=[]
    for p in sorted((ROOT/'interface').glob('*.gui')):
        for name, entries, parents in walk(province_tree(read(p))):
            if not name.startswith('rip_'):
                continue
            current=name;size=dimensions(fields(entries),'size',(300,100))
            if min(size)<=0: continue
            # These are anchor containers inside orthodox_specific_window.
            # Their nominal size does not bound their positioned children.
            if name in ('rip_church_gc_native_controls','rip_church_ro_native_controls'):
                size=(400,340)
            for mode in ('normal','long'):
                canvas=Image.new('RGBA',size,(29,35,39,255));render(entries,canvas,mode)
                canvas.convert('RGB').save(out/f'{name}_{mode}.png')
            pages.append(dict(name=name,file=p.name,parents=parents,size=size))
    # The parliament title is a new overlay inside a native window, not a new window.
    p=ROOT/'interface/parliament.gui'
    for name, entries, parents in walk(province_tree(read(p))):
        if name=='parliament_window':
            current='rip_parliament_title_overlay'
            selected=[(k,v) for k,v in entries if isinstance(v,list) and fields(v).get('name') in ('parliament_bg','rip_parliament_title')]
            canvas=Image.new('RGBA',(548,110),(29,35,39,255));render(selected,canvas,'normal')
            canvas.convert('RGB').save(out/f'{current}_normal.png')
            canvas.convert('RGB').save(out/f'{current}_long.png')
            pages.append(dict(name=current,file=p.name,parents=(),size=canvas.size))
    summary=dict(evidence='SOURCE PREVIEW ONLY; donor textures/fonts, no engine execution; all source children visible; conditional alternatives may superimpose; first sprite frame; shaders and orientation transforms not emulated',donor=str(game),donor_version=version,pages=pages,issues=issues)
    (out/'review.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    cards=''.join(f'<article><h2>{html.escape(p["name"])}</h2><p>{html.escape(p["file"])} · {p["size"]}</p><a href="{p["name"]}_normal.png"><img src="{p["name"]}_normal.png"></a><p><a href="{p["name"]}_long.png">Long-text sample (windows)</a></p></article>' for p in pages)
    (out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>RIP interface review</title><style>body{background:#182026;color:#eee;font:15px Arial;margin:24px}main{display:flex;flex-wrap:wrap;gap:20px}article{background:#253039;padding:16px;max-width:560px}h2{font-size:16px}img{max-width:100%}a{color:#ddc382}</style><h1>RIP: source-layout review</h1><p>'+html.escape(summary['evidence'])+'</p><p>Donor: '+html.escape(version)+'</p><main>'+cards+'</main>',encoding='utf-8')
    print(f'Rendered {len(pages)} panels/overlays; {len(issues)} review findings; {out}')


if __name__=='__main__':
    main()
