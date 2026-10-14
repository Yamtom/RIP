"""Render generated Union tabs using installed EU4 art and bitmap font metrics.

Requires Pillow. This is a source preview, never an engine screenshot.
Nested window coordinates and all possible localized readouts are measured.
"""
from pathlib import Path
import argparse
import json
import re
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import vanilla_root, keyed_blocks
from church_testlib import parse, fixture

GAME = vanilla_root()
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--out', type=Path, default=ROOT / 'diagnostics/church_gui_20261002')
args = ap.parse_args()
OUT = args.out
OUT.mkdir(parents=True, exist_ok=True)
loc = dict(re.findall(r'^\s+(\w+):0 "(.*)"$', (ROOT / 'localisation/replace/zzzz_RIP_church_redesign_l_english.yml').read_text(encoding='utf-8-sig'), re.M))
readouts = {}
for _, block in keyed_blocks((ROOT / 'customizable_localization/rip_church_redesign.txt').read_text(), 'defined_text'):
    entries = dict(parse(block))['defined_text']
    name = dict(entries)['name']
    leaves = [dict(v)['localisation_key'] for k, v in entries if k == 'text']
    # Engine probes rejected GetValue in defined_text results in scripted
    # church widgets, including the quoted form used by other native hosts.
    for leaf in leaves:
        assert not re.search(r'\[Root\.\w+\.GetValue\]', loc.get(leaf, leaf)), (name, leaf, 'runtime-invalid nested variable readout')
    readouts[name] = leaves
samples = {
    'GetChurchPapalOpinion': '20', 'GetChurchAuthorityReadout': '100%',
    'GetChurchEcumenismReason': 'Requires 20 years of Union',
    'GetChurchMissionCost': '50 ducats', 'GetChurchMissionPeace': 'Yes',
    'GetChurchMissionRome': 'Catholic PAP', 'GetChurchMissionCooldown': 'Ready',
    'GetChurchMissionReason': 'Deputation available', 'GetChurchGiftReason': 'Gift available',
    'GetChurchCuriaController': 'Castile',
}
numeric_samples = {
    'rip_church_gui_eastern_parishes.GetValue': '12',
    'rip_church_gui_latin_parishes.GetValue': '7',
}
numeric_extremes = {
    'rip_church_gui_eastern_parishes.GetValue': ('1', '9999'),
    'rip_church_gui_latin_parishes.GetValue': ('1', '9999'),
}
# New visual badges use the live scripted gates. This bounded source fixture
# is not engine evidence, but it prevents painting both mutually exclusive
# badges on top of each other in the preview.
fixture_world, fixture_country, _ = fixture('greek_catholic')
fixture_country.update(treasury=150, patriarch_authority=1, is_at_war=False, stability=2)
icon_gates = {}
for path in ('common/custom_gui/RIP_church_controls.txt', 'common/custom_gui/RIP_church_gc_features.txt'):
    for kind, payload in parse((ROOT / path).read_text(encoding='utf-8-sig')):
        if kind == 'custom_icon':
            fields = dict(payload)
            icon_gates[fields['name']] = fields.get('potential', [])

def resolve_leaf(leaf, overrides=None, trail=(), values=None):
    # The parser removes quotes. Native defined_text may return a quoted raw
    # property expression, rather than the name of a localisation entry.
    if re.fullmatch(r'\[[^]\r\n]+\]', leaf):
        return resolve(leaf, overrides, trail, values)
    assert leaf in loc, f'Unresolved readout localisation: {leaf}'
    return resolve(loc[leaf], overrides, trail, values)


def resolve(value, overrides=None, trail=(), values=None):
    # EU4 substitutes both $LOCALISATION_KEY$ and [Root.ScriptedReadout].
    # Measure the resulting text, not the shorter unresolved key spelling.
    def localised(match):
        key = match[1]
        assert key in loc, f'Unresolved localisation: {key}'
        assert key not in trail, f'Circular localisation: {trail + (key,)}'
        return resolve(loc[key], overrides, trail + (key,), values)

    def replacement(match):
        key = match[1].removeprefix('Root.')
        if overrides and key in overrides:
            return resolve_leaf(overrides[key], overrides, trail, values)
        if key in samples:
            return samples[key]
        if key in readouts:
            leaf = readouts[key][-1]
            return resolve_leaf(leaf, overrides, trail, values)
        if key.endswith('.GetValue'):
            return (values or {}).get(key, numeric_samples.get(key, '9999'))
        if key == 'rip_church_gc_controller.GetName':
            return 'The Papal State'
        raise AssertionError(f'Unresolved readout: {key}')
    value = re.sub(r'\$([^$]+)\$', localised, value)
    return re.sub(r'\[([^]]+)\]', replacement, value).replace('\\n', '\n')


def expand_keys(value, trail=()):
    def replacement(match):
        key = match[1]
        assert key in loc and key not in trail, (key, 'missing/circular localisation')
        return expand_keys(loc[key], trail + (key,))
    return re.sub(r'\$([^$]+)\$', replacement, value)

def asset(path):
    path = path.replace('//', '/')
    p = ROOT / path
    if not p.exists():
        p = GAME / path
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

def sprite(name, frame=1, target=None):
    kind, d = sprites[name]
    src = asset(d['texturefile'])
    if kind == 'corneredTileSpriteType':
        # Vanilla uses default destination sizes unlike its source DDS sizes
        # (e.g. tiles_dialog.dds). A GUI icon's explicit size overrides that
        # default. This is a source model, not proof of engine UV sampling.
        w, h = target or tuple(int(dict(d['size'])[k]) for k in ('x', 'y'))
        bx, by = (int(dict(d['bordersize'])[k]) for k in ('x', 'y'))
        assert 2*bx <= min(src.width, w) and 2*by <= min(src.height, h), (name, 'corner border exceeds source/target')
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
measurements = []
geometry = {}
def nonoverlap(x, y, w, h, label):
    for a, b, c, d, previous in rects:
        assert x+w <= a or a+c <= x or y+h <= b or b+d <= y, (label, previous, 'overlap')
    rects.append((x, y, w, h, label))

def render(entries, canvas, ox=0, oy=0, tab='union', bounds=None):
    bounds = bounds or (ox, oy, canvas.width, canvas.height)

    def contained(x, y, w, h, label):
        px, py, pw, ph = bounds
        assert x >= px and y >= py and x+w <= px+pw and y+h <= py+ph, (label, 'outside parent', (x, y, w, h), bounds)
        assert x >= 0 and y >= 0 and x+w <= canvas.width and y+h <= canvas.height, (label, 'outside page')

    for kind, payload in entries:
        if kind not in ('windowType', 'iconType', 'guiButtonType', 'instantTextBoxType'):
            continue
        d = dict(payload)
        pos = dict(d['position'])
        x, y = ox+int(pos['x']), oy+int(pos['y'])
        if kind == 'windowType':
            size = dict(d['size'])
            w, h = int(size['x']), int(size['y'])
            contained(x, y, w, h, d['name'])
            render(payload, canvas, x, y, tab, (x, y, w, h))
            continue
        label = d['name']
        if kind == 'iconType' and label.endswith(('_ready', '_blocked')):
            assert label in icon_gates, (label, 'unbound status badge')
            if not fixture_world.gate(icon_gates[label], fixture_country):
                continue
        if kind == 'instantTextBoxType':
            w, h = int(d['maxWidth']), int(d['maxHeight'])
            contained(x, y, w, h, label)
            geometry[label] = (x, y, w, h)
            nonoverlap(x, y, w, h, label)
            value = loc[d['text']]
            variants = 0
            # Expand $KEY$ first so nested scripted fields are also validated.
            expanded = expand_keys(value)
            for key in re.findall(r'\[Root\.(\w+)\]', expanded):
                for variant in readouts.get(key, []):
                    text(canvas, resolve(value, {key: variant}), x, y, w, h, d['font'], d['format']=='center', label, False)
                    variants += 1
            # Positive parish counts are direct outer properties. Measure
            # their nonzero and wide values even without defined_text rows.
            for variable in re.findall(r'\[Root\.(\w+\.GetValue)\]', expanded):
                for numeric in numeric_extremes.get(variable, ('1', '9999')):
                    text(canvas, resolve(value, values={variable: numeric}), x, y, w, h, d['font'], d['format']=='center', label, False)
                    variants += 1
            sample = resolve(value)
            text(canvas, sample, x, y, w, h, d['font'], d['format']=='center', label)
            measurements.append({'page': tab, 'widget': label, 'bounds': [x,y,w,h], 'readout_variants': variants, 'sample_text': sample})
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
            target = tuple(int(dict(d['size'])[k]) for k in ('x', 'y')) if 'size' in d else None
            art = sprite(name, frame, target)
        if 'scale' in d:
            scale = float(d['scale'])
            art = art.resize((round(art.width*scale), round(art.height*scale)))
        contained(x, y, art.width, art.height, label)
        geometry[label] = (x, y, art.width, art.height)
        canvas.alpha_composite(art, (x, y))
        if kind == 'guiButtonType':
            # Include clickable icons and shields, not just captioned buttons.
            nonoverlap(x, y, art.width, art.height, label)
        if d.get('buttonText'):
            text(canvas, resolve(loc[d['buttonText']]), x+7, y+(art.height-18)//2, art.width-14, 18, d['buttonFont'], True, label)


def check_navigation_alignment(tab):
    # Match opaque native art, rather than the tab's transparent 36px canvas.
    # This is the join that looked disconnected in the player's screenshot.
    rail = geometry[f'rip_church_tab_rail_{tab}']
    rail_art = sprite('GFX_macro_diplomacy_line').resize(rail[2:])
    gold_row = next(y for y in range(rail_art.height)
                    if rail_art.getpixel((40, y))[3] == 255)
    inactive_art = sprite('GFX_tab_small_116', frame=1)
    inactive_bottom = inactive_art.getbbox()[3] - 1
    for family in ('union', 'curia'):
        control = geometry[f'rip_church_gc_{family}_tab_{tab}']
        assert control[1] + inactive_bottom == rail[1] + gold_row, (
            tab, family, 'inactive tab silhouette must meet the native gold rail')


def check_icon_alignment(tab):
    if tab != 'union':
        return
    pairs = [(f'rip_church_{key}_symbol_frame', f'rip_church_{key}_symbol') for key in ('synod', 'policy')]
    pairs += [(f'rip_church_gc_icon_{key}_slot', f'rip_church_gc_icon_{key}_art')
              for key in ('liturgy', 'learning', 'charity')]
    frames, arts = [], []
    for frame_label, art_label in pairs:
        frame, art = geometry[frame_label], geometry[art_label]
        frames.append(frame)
        arts.append(art)
        assert 2*frame[0]+frame[2] == 2*art[0]+art[2], (art_label, 'not horizontally centered in slot')
        assert 2*frame[1]+frame[3] == 2*art[1]+art[3], (art_label, 'not vertically centered in slot')
    assert len({r[2:] for r in frames}) == 1, 'institution/devotional slot sizes differ'
    assert len({r[2:] for r in arts}) == 1, 'institution/devotional art sizes differ'
    assert frames[0][1] == frames[1][1], 'institution slots do not share a row'
    assert len({r[1] for r in frames[2:]}) == 1, 'devotional slots do not share a row'
    for key in ('liturgy', 'learning', 'charity'):
        slot = geometry[f'rip_church_gc_icon_{key}_slot']
        assert geometry[f'rip_church_gc_icon_{key}_button'] == slot, (key, 'click target differs from visible slot')
        caption = geometry[f'rip_church_gc_icon_{key}_state']
        assert 2*slot[0]+slot[2] == 2*caption[0]+caption[2], (key, 'caption not centered under icon')

source = (ROOT / 'interface/countryreligionview.gui').read_text()
previews = []
for tab, name in [('union', 'rip_church_gc_panel'), ('curia', 'rip_church_gc_curia_panel'), ('parishes', 'rip_church_gc_parishes_panel')]:
    rects.clear()
    geometry.clear()
    block = next(b for _, b in keyed_blocks(source, 'windowType') if dict(dict(parse(b))['windowType']).get('name') == name)
    entries = dict(parse(block))['windowType']
    size = dict(dict(entries)['size'])
    canvas = Image.new('RGBA', (int(size['x']), int(size['y'])), (35, 38, 42, 255))
    render(entries, canvas, tab=tab)
    check_navigation_alignment(tab)
    check_icon_alignment(tab)
    canvas.save(OUT / f'{tab}.png')
    previews.append(canvas)
visible = previews[:2]  # The parish register is a legacy route, not a third tab.
sheet = Image.new('RGB', (sum(p.width for p in visible)+16, max(p.height for p in visible)), (35, 38, 42))
for i, p in enumerate(visible):
    sheet.paste(p, (i*(p.width+16), 0))
sheet.save(OUT / 'tabs.png')
(OUT / 'layout.json').write_text(json.dumps({'evidence': 'source preview; engine rendering not verified', 'Papal_opinion_sample': samples['GetChurchPapalOpinion'], 'numeric_samples': numeric_samples, 'numeric_extremes': numeric_extremes, 'text_widgets': measurements}, indent=2), encoding='utf-8')
print(f'PASS: 2 visible tabs and 1 legacy register; parent bounds, nonoverlapping text/controls, native bitmap fonts and all direct readout variants. {OUT}')
print('Source fixture: 100 HC, 150 ducats, no active institution, fresh contact cooldowns. Colors, hover and cornered UV sampling are not engine-rendered.')
