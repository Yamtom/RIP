"""Render generated Union tabs using installed EU4 art and bitmap font metrics.

Requires Pillow. This is a source preview, never an engine screenshot.
Nested window coordinates and all possible localized readouts are measured.
"""
from pathlib import Path
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import vanilla_root, keyed_blocks
from church_testlib import parse

GAME = vanilla_root()
OUT = ROOT / 'diagnostics/church_gui_20261001'
OUT.mkdir(parents=True, exist_ok=True)
loc = dict(re.findall(r'^\s+(\w+):0 "(.*)"$', (ROOT / 'localisation/replace/zzzz_RIP_church_redesign_l_english.yml').read_text(encoding='utf-8-sig'), re.M))
readouts = {}
for _, block in keyed_blocks((ROOT / 'customizable_localization/rip_church_redesign.txt').read_text(), 'defined_text'):
    entries = dict(parse(block))['defined_text']
    readouts[dict(entries)['name']] = [dict(v)['localisation_key'] for k, v in entries if k == 'text']
samples = {
    'GetChurchPapalOpinion': '20', 'GetChurchAuthorityReadout': '100%',
    'GetChurchEcumenismReason': 'Requires 20 years of Union',
    'GetChurchMissionCost': '50 ducats', 'GetChurchMissionPeace': 'Yes',
    'GetChurchMissionRome': 'Catholic PAP', 'GetChurchMissionCooldown': 'Ready',
    'GetChurchMissionReason': 'Ready to send · diplomatic contact only',
    'GetChurchCuriaController': 'Castile',
}

def resolve(value, overrides=None):
    def replacement(match):
        key = match[1].removeprefix('Root.')
        if overrides and key in overrides:
            return resolve(loc[overrides[key]])
        if key in samples:
            return samples[key]
        if key in readouts:
            return resolve(loc[readouts[key][-1]])
        if key.endswith('.GetValue'):
            return '999'
        if key == 'rip_church_gc_controller.GetName':
            return 'The Papal State'
        raise AssertionError(f'Unresolved readout: {key}')
    return re.sub(r'\[([^]]+)\]', replacement, value).replace('\\n', '\n')

def asset(path):
    p = GAME / path.replace('//', '/')
    if not p.exists():
        p = p.with_suffix('.dds')
    return Image.open(p).convert('RGBA')

sprites = {}
for p in [*sorted((GAME / 'interface').glob('*.gfx')), ROOT / 'interface/RIP_church_panels.gfx']:
    source = p.read_text(encoding='utf-8-sig', errors='replace')
    for kind in ('spriteType', 'textSpriteType', 'corneredTileSpriteType'):
        for _, block in keyed_blocks(source, kind):
            d = {k.lower(): v for k, v in re.findall(r'\b(name|texturefile)\s*=\s*"([^"]+)"', block, re.I)}
            frames = re.search(r'\bnoOfFrames\s*=\s*(\d+)', block, re.I)
            if frames:
                d['noofframes'] = frames[1]
            for field in ('size', 'borderSize'):
                m = re.search(r'\b'+field+r'\s*=\s*\{([^}]+)\}', block, re.I)
                if m:
                    d[field.lower()] = re.findall(r'([xy])\s*=\s*(\d+)', m[1])
            if 'name' in d and 'texturefile' in d:
                sprites[d['name']] = (kind, d)

def sprite(name, frame=1):
    kind, d = sprites[name]
    src = asset(d['texturefile'])
    if kind == 'corneredTileSpriteType':
        w, h = (int(dict(d['size'])[k]) for k in ('x', 'y'))
        bx, by = (int(dict(d['bordersize'])[k]) for k in ('x', 'y'))
        dst = Image.new('RGBA', (w, h))
        for a, b, c, e in ((0, bx, 0, bx), (bx, src.width-bx, bx, w-bx), (src.width-bx, src.width, w-bx, w)):
            for f, g, j, k in ((0, by, 0, by), (by, src.height-by, by, h-by), (src.height-by, src.height, h-by, h)):
                dst.alpha_composite(src.crop((a, f, b, g)).resize((e-c, k-j)), (c, j))
        return dst
    count = int(d.get('noofframes', 1))
    width = src.width // count
    return src.crop(((frame-1)*width, 0, frame*width, src.height))

fonts = {}
def font(name):
    if name not in fonts:
        stem = 'garamond_14' if name == 'Main_14' else name
        spec = (GAME / f'gfx/fonts/{stem}.fnt').read_text()
        chars = {}
        for line in spec.splitlines():
            if line.startswith('char '):
                char = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
                chars[char['id']] = char
        fonts[name] = (int(re.search(r'lineHeight=(\d+)', spec)[1]), chars, asset(f'gfx/fonts/{stem}.tga'))
    return fonts[name]

def text(canvas, value, x, y, w, h, name, centered, label, paint=True):
    lineheight, chars, atlas = font(name)
    plain = re.sub('§.', '', value)
    def width(s):
        return sum(chars[ord(c)]['xadvance'] for c in s)
    lines = []
    for paragraph in plain.split('\n'):
        line = ''
        for word in paragraph.split():
            candidate = (line + ' ' + word).strip()
            if width(candidate) > w and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    assert len(lines)*lineheight <= h, (label, plain, 'text height', len(lines)*lineheight, h)
    for line in lines:
        assert width(line) <= w, (label, line, 'text width', width(line), w)
        cursor = x + (w-width(line))//2 if centered else x
        if paint:
            for ch in line:
                c = chars[ord(ch)]
                glyph = atlas.crop((c['x'], c['y'], c['x']+c['width'], c['y']+c['height']))
                canvas.alpha_composite(glyph, (cursor+c['xoffset'], y+c['yoffset']))
                cursor += c['xadvance']
        y += lineheight

rects = []
def nonoverlap(x, y, w, h, label):
    for a, b, c, d, previous in rects:
        assert x+w <= a or a+c <= x or y+h <= b or b+d <= y, (label, previous, 'overlap')
    rects.append((x, y, w, h, label))

def render(entries, canvas, ox=0, oy=0, tab='union'):
    for kind, payload in entries:
        if kind not in ('windowType', 'iconType', 'guiButtonType', 'instantTextBoxType'):
            continue
        d = dict(payload)
        pos = dict(d['position'])
        x, y = ox+int(pos['x']), oy+int(pos['y'])
        if kind == 'windowType':
            render(payload, canvas, x, y, tab)
            continue
        label = d['name']
        if kind == 'instantTextBoxType':
            w, h = int(d['maxWidth']), int(d['maxHeight'])
            assert x >= 0 and y >= 0 and x+w <= canvas.width and y+h <= canvas.height, label
            if d.get('alwaystransparent') != 'yes':
                nonoverlap(x, y, w, h, label)
            value = loc[d['text']]
            for key in re.findall(r'\[Root\.(\w+)\]', value):
                for variant in readouts.get(key, []):
                    text(canvas, resolve(value, {key: variant}), x, y, w, h, d['font'], d['format']=='center', label, False)
            text(canvas, resolve(value), x, y, w, h, d['font'], d['format']=='center', label)
            continue
        if 'active_frame' in label:
            continue  # Preview fixture has no active devotional icon.
        name = d.get('spriteType', d.get('quadTextureSprite'))
        if name in ('GFX_shield_medium','GFX_shield_small'):
            small = name == 'GFX_shield_small'
            art = asset('gfx/interface/small_shield_overlay.dds' if small else 'gfx/interface/shield_medium_overlay.dds')
            mask = asset('gfx/interface/small_shield_mask.tga' if small else 'gfx/interface/shield_medium_mask.tga')
            flag = asset('gfx/flags/CAS.tga' if 'controller' in label else 'gfx/flags/PAP.tga').resize(mask.size)
            flag.putalpha(mask.getchannel('A'))
            flag.alpha_composite(art)
            art = flag
        else:
            frame = 2 if name == 'GFX_tab_small_116' and f'_{tab}_tab_' in label else 1
            art = sprite(name, frame)
        if 'scale' in d:
            scale = float(d['scale'])
            art = art.resize((round(art.width*scale), round(art.height*scale)))
        assert x >= 0 and y >= 0 and x+art.width <= canvas.width and y+art.height <= canvas.height, (label, art.size, x, y)
        canvas.alpha_composite(art, (x, y))
        if d.get('buttonText'):
            nonoverlap(x, y, art.width, art.height, label)
            text(canvas, resolve(loc[d['buttonText']]), x+7, y+(art.height-18)//2, art.width-14, 18, d['buttonFont'], True, label)

source = (ROOT / 'interface/countryreligionview.gui').read_text()
previews = []
for tab, name in [('union', 'rip_church_gc_panel'), ('curia', 'rip_church_gc_curia_panel'), ('parishes', 'rip_church_gc_parishes_panel')]:
    rects.clear()
    block = next(b for _, b in keyed_blocks(source, 'windowType') if dict(dict(parse(b))['windowType']).get('name') == name)
    entries = dict(parse(block))['windowType']
    size = dict(dict(entries)['size'])
    canvas = Image.new('RGBA', (int(size['x']), int(size['y'])), (35, 38, 42, 255))
    render(entries, canvas, tab=tab)
    canvas.save(OUT / f'{tab}.png')
    previews.append(canvas)
sheet = Image.new('RGB', (sum(p.width for p in previews)+32, max(p.height for p in previews)), (35, 38, 42))
for i, p in enumerate(previews):
    sheet.paste(p, (i*(p.width+16), 0))
sheet.save(OUT / 'tabs.png')
print(f'PASS: 3 source previews, native assets/font metrics, all direct readout variants fit. {OUT}')
print('Sample values; colors and disabled/hover state are not engine-rendered. Runtime unverified.')
