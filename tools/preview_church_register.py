"""Layout preview of the Holy Cities Register and the Muscovite Church window.

Not an EU4 screenshot. It draws the generated panel from interface/countryreligionview.gui with the real
vanilla and mod textures and the real vic_18 glyph atlas, so overflow, overlap and alignment can be judged
without starting the game. Sample provinces and sample variables stand in for the live ones; every frame and
every visibility test is taken by executing the actual common/custom_gui bindings in the bounded church
interpreter used by the tests, so a binding that picks the wrong frame shows up here as a wrong picture.
Tooltips are not drawn; the five progress tooltips are printed instead, fully expanded.

    python tools/preview_church_register.py --panel register --state mid --out register_mid.png
    python tools/preview_church_register.py --panel church --state schism --out church_schism.png
    python tools/preview_church_register.py --panel all --out diagnostics/church_ui_20261018 --zoom 1

States: fresh (no variable set yet, as in a new game), mid (myths part-way), matured (all five complete).
For the church panel, schism adds the Reconcile button that appears during the Raskol.
"""
from pathlib import Path
import argparse
import re
import sys

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tests'))
from church_testlib import World, parse                     # noqa: E402
from clausewitz_testlib import ROOT, vanilla_root                   # noqa: E402

GAME = vanilla_root()
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--panel', choices=('register', 'church', 'all'), default='register',
                help='all renders the five standard views into the --out directory')
ap.add_argument('--state', choices=('fresh', 'mid', 'matured', 'schism'), default='mid')
ap.add_argument('--out', type=Path, default=Path('register_preview.png'), help='a PNG file, or a directory with --panel all')
ap.add_argument('--zoom', type=int, default=2, help='integer upscale of the saved image (1 = native pixels)')
ap.add_argument('--quiet', action='store_true', help='do not print the expanded tooltips')
args = ap.parse_args()
if GAME is None:
    raise SystemExit('SKIP: the vanilla install is needed for textures and fonts (set EU4_DIR)')

# ---- Sprites -----------------------------------------------------------------------------------------
SPRITES = {}
BLOCK = re.compile(r'(?i)\b(\w*SpriteType)\s*=\s*\{')                 # spriteType, textSpriteType, corneredTileSpriteType


def scan(folder):
    for path in sorted(folder.rglob('*.gfx')):
        text = re.sub(r'#[^\n]*', '', path.read_text(encoding='utf-8-sig', errors='replace'))        # braces in comments
        marks = list(BLOCK.finditer(text))
        for index, m in enumerate(marks):
            # A sprite block never contains another one, so it runs to the next sprite keyword: no brace matching,
            # which is what made scanning all of vanilla's interface folder take ten seconds.
            block = text[m.end():marks[index + 1].start() if index + 1 < len(marks) else len(text)]
            name = re.search(r'\bname\s*=\s*"([^"]+)"', block)
            texture = re.search(r'(?i)\btexturefile\s*=\s*"([^"]+)"', block)
            if not name or not texture:
                continue
            frames = re.search(r'(?i)\bnoOfFrames\s*=\s*(\d+)', block)
            size = re.search(r'\bsize\s*=\s*\{\s*x\s*=\s*(\d+)\s*y\s*=\s*(\d+)', block)
            border = re.search(r'(?i)\bborderSize\s*=\s*\{\s*x\s*=\s*(\d+)', block)
            SPRITES[name[1]] = dict(texture=texture[1].replace('\\', '/').replace('//', '/'),
                                    frames=int(frames[1]) if frames else 1,
                                    cornered=m[1].lower().startswith('cornered'),
                                    size=(int(size[1]), int(size[2])) if size else None,
                                    border=int(border[1]) if border else 0)


scan(GAME / 'interface')
scan(ROOT / 'interface')                                  # the mod wins, as in the engine
_textures = {}


def texture(path):
    if path not in _textures:
        for base in (ROOT, GAME):
            for candidate in (base / path, (base / path).with_suffix('.dds'), (base / path).with_suffix('.tga')):
                if candidate.exists():
                    _textures[path] = Image.open(candidate).convert('RGBA')
                    break
            if path in _textures:
                break
        else:
            raise FileNotFoundError(path)
    return _textures[path]


def nine_slice(source, width, height, border):
    sw, sh = source.size
    out = Image.new('RGBA', (width, height))
    for sx, ex, dx, tx in ((0, border, 0, border), (border, sw - border, border, width - border), (sw - border, sw, width - border, width)):
        for sy, ey, dy, ty in ((0, border, 0, border), (border, sh - border, border, height - border), (sh - border, sh, height - border, height)):
            out.alpha_composite(source.crop((sx, sy, ex, ey)).resize((tx - dx, ty - dy)), (dx, dy))
    return out


def sprite_image(name, frame=1, scale=1.0):
    meta = SPRITES[name]
    art = texture(meta['texture'])
    if meta['cornered']:
        art = nine_slice(art, *meta['size'], meta['border'])
    elif meta['frames'] > 1:
        width = art.width // meta['frames']
        index = min(max(frame, 1), meta['frames']) - 1
        art = art.crop((index * width, 0, (index + 1) * width, art.height))
    if scale != 1.0:
        art = art.resize((max(1, round(art.width * scale)), max(1, round(art.height * scale))), Image.LANCZOS)
    return art


# ---- Fonts and text ----------------------------------------------------------------------------------
GLOBAL_COLORS = {'W': (255, 255, 255), 'G': (0, 255, 0), 'R': (255, 50, 50), 'g': (176, 176, 176), 'Y': (255, 189, 0),
                 'O': (255, 160, 0), 'M': (35, 206, 255), 'T': (0, 255, 239), 'b': (0, 0, 0)}
VIC18 = {'G': (44, 171, 50), 'R': (181, 61, 61), 'Y': (219, 203, 71)}       # vic_18's own colour table
FONT_FILES = {'vic_18': 'vic_18', 'vic_22': 'vic_22', 'Main_14': 'garamond_14', 'Main_14_bold': 'garamond_14_bold'}
_fonts = {}
problems = []


def font(name):
    stem = FONT_FILES.get(name)
    if stem is None:                                         # an undeclared font such as the mod's vic_14 falls back to vic_18
        problems.append(f'font {name} is not declared by the game; drawn as vic_18')
        stem, name = 'vic_18', 'vic_18'
    if stem not in _fonts:
        spec = (GAME / f'gfx/fonts/{stem}.fnt').read_text(encoding='latin-1')
        chars = {}
        for line in spec.splitlines():
            if line.startswith('char '):
                c = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
                chars[c['id']] = c
        _fonts[stem] = (int(re.search(r'lineHeight=(\d+)', spec)[1]), chars, Image.open(GAME / f'gfx/fonts/{stem}.tga').convert('RGBA'), name)
    return _fonts[stem]


def draw_text(canvas, source, x, y, width, height, font_name, center, label):
    line_height, chars, atlas, resolved = font(font_name)
    table = dict(GLOBAL_COLORS)
    if resolved == 'vic_18':
        table.update(VIC18)

    def measure(tokens):
        return sum(chars[ord(t)]['xadvance'] for t in tokens if not t.startswith('§'))

    # Split into lines on explicit breaks, then wrap on spaces. Colour codes cost no width.
    wrapped = []
    for paragraph in source.replace('\\n', '\n').split('\n'):
        current = []
        for word in paragraph.split(' '):
            candidate = current + ([' '] if current else []) + re.findall('§.|[^§]', word)
            if measure(candidate) > width and current:
                wrapped.append(current)
                current = re.findall('§.|[^§]', word)
            else:
                current = candidate
        wrapped.append(current)
    if len(wrapped) > 1 and len(wrapped) * line_height > height:           # one line is always drawn, as in the game
        problems.append(f'{label}: {len(wrapped)} lines of {line_height}px do not fit a {height}px box: {source!r}')
    color, cursor_y = None, y
    for tokens in wrapped:
        cursor = x + (width - measure(tokens)) // 2 if center else x
        for token in tokens:
            if token.startswith('§'):
                color = None if token[1] == '!' else table.get(token[1])
                continue
            c = chars[ord(token)]
            if c['width'] and c['height']:
                glyph = atlas.crop((c['x'], c['y'], c['x'] + c['width'], c['y'] + c['height']))
                if color:
                    tint = Image.new('RGBA', glyph.size, color + (255,))
                    tint.putalpha(glyph.getchannel('A'))
                    glyph = tint
                canvas.alpha_composite(glyph, (cursor + c['xoffset'], cursor_y + c['yoffset']))
            cursor += c['xadvance']
        cursor_y += line_height


# ---- Localisation, bindings and the window tree ------------------------------------------------------
def read_loc(path):
    return dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', path.read_text(encoding='utf-8-sig'), re.M))


LOC = read_loc(ROOT / 'localisation/replace/zzzz_RIP_church_redesign_l_english.yml')
LOC.update(read_loc(ROOT / 'localisation/rip_ro_blessing_window_l_english.yml'))
LADDERS = {}
for kind, body in parse((ROOT / 'customizable_localization/rip_church_redesign.txt').read_text(encoding='utf-8-sig')):
    if kind == 'defined_text':
        LADDERS[dict(body)['name']] = [(dict(row)['trigger'], dict(row)['localisation_key']) for k, row in body if k == 'text']
for kind, body in parse((ROOT / 'customizable_localization/rip_ro_holy_cities_custom_loc.txt').read_text(encoding='utf-8-sig')):
    if kind == 'defined_text':
        LADDERS[dict(body)['name']] = [(dict(row).get('trigger', [('always', 'yes')]), dict(row)['localisation_key']) for k, row in body if k == 'text']
BINDINGS = {}
for kind, body in parse((ROOT / 'common/custom_gui/RIP_church_controls.txt').read_text(encoding='utf-8-sig')):
    if kind.startswith('custom_'):
        BINDINGS[kind, dict(body)['name']] = body
GUI = parse((ROOT / 'interface/countryreligionview.gui').read_text(encoding='utf-8-sig'))


def find(entries, kind, name):
    for key, body in entries:
        if isinstance(body, list):
            if key == kind and dict(body).get('name') == name:
                return body
            hit = find(body, kind, name)
            if hit:
                return hit


CITIES = (('novgorod', 310, 'Novgorod', 'NOV', 'Novgorod', 'orthodox'),
          ('moscow', 295, 'Moskva', 'MOS', 'Muscovy', 'russian_orthodox'),
          ('kyiv', 280, 'Kyiv', 'KIE', 'Kyiv', 'orthodox'),
          ('constantinople', 151, 'Constantinople', 'BYZ', 'Byzantium', 'orthodox'),
          ('jerusalem', 379, 'al-Quds', 'MAM', 'Mamluks', 'sunni'))
RELIGION_NAMES = {'orthodox': 'Orthodox', 'russian_orthodox': 'Muscovite Orthodox', 'sunni': 'Sunni'}
MID = {'novgorod': 3, 'moscow': 12, 'kyiv': 21, 'constantinople': 27, 'jerusalem': 0}
YEARS = {'fresh': {}, 'mid': MID, 'matured': {key: 30 for key, *_ in CITIES}, 'schism': MID}
SAMPLE = {'GetChurchROStatus': 'Muscovite confession in Eastern communion · RD 0%', 'GetChurchROFervor': '§R0§!', 'GetChurchRONet': '§Y0§!',
          'GetChurchRONodes': '§Y0§!', 'GetChurchRONodeLimit': '1', 'GetChurchRONodeIncome': '§g0§!', 'GetChurchROBase': '§g0§!',
          'GetChurchROUpkeep': '§g0§!', 'GetChurchROPolicies': '§Y0§!', 'GetChurchROCapacity': '§Y1§!'}


class Scene:
    """One panel in one state: a sample world, the bindings run against it, and the drawn canvas."""

    def __init__(self, panel, state):
        del problems[:]
        self.world = World()
        self.player = self.world.country('MOS', 'russian_orthodox')
        owners = {tag: self.world.country(tag, 'orthodox') for tag in ('NOV', 'KIE', 'BYZ', 'MAM')}
        owners['MOS'] = self.player
        self.province_info = {}
        for key, number, name, tag, owner_name, religion in CITIES:
            self.world.province(number, owners[tag], religion)
            self.province_info[number] = (name, owner_name, RELIGION_NAMES[religion])
        for key, years in YEARS[state].items():
            self.player['variables'][f'rip_ro_myth_years_{key}'] = years
            if years >= 30:
                self.player['flags'][f'rip_ro_myth_complete_{key}'] = 0
        if state == 'schism':
            self.player['flags']['rip_church_ro_schismatic'] = 0
        if panel == 'register':
            self.player['flags']['rip_ro_holy_city_register_open'] = 0       # the register is open: its Close button shows
        self.panel, self.state = panel, state
        window = find(GUI, 'windowType', 'rip_ro_holy_cities_panel' if panel == 'register' else 'rip_church_ro_panel')
        size = dict(dict(window)['size'])
        self.canvas = Image.new('RGBA', (int(size['x']), int(size['y'])), (0, 0, 0, 0))
        self.drawn = []
        self.draw(window, 0, 0)
        for name, x, y, w, h in self.drawn:
            if x < 0 or y < 0 or x + w > self.canvas.width or y + h > self.canvas.height:
                problems.append(f'{name} leaves the window: {(x, y, w, h)}')
        self.problems = sorted(set(problems))

    def resolve(self, text, depth=0):
        def command(m):
            body = m[1]
            ladder = re.fullmatch(r'(?i:root)\.(\w+)', body)
            if ladder and ladder[1] in LADDERS:
                key = next(k for gate, k in LADDERS[ladder[1]] if self.world.gate(gate, self.player))
                return self.resolve(LOC[key], depth + 1)
            if ladder and ladder[1] in SAMPLE:
                return SAMPLE[ladder[1]]
            province = re.fullmatch(r'(\d+)\.(Owner\.GetName|Religion\.GetName|GetName)', body)
            if province:
                name, owner, religion = self.province_info[int(province[1])]
                return {'GetName': name, 'Owner.GetName': owner, 'Religion.GetName': religion}[province[2]]
            problems.append(f'unresolved [{body}]')
            return ''
        return re.sub(r'\[([^\]]+)\]', command, text)

    def visible(self, kind, name):
        binding = BINDINGS.get((kind, name))
        if binding is None:
            return None
        potential = dict(binding).get('potential')
        return self.world.gate(potential, self.player) if potential else True

    def frame_of(self, name):
        for key, value in BINDINGS.get(('custom_icon', name)) or []:
            if key == 'frame' and self.world.gate(dict(value)['trigger'], self.player):
                return int(dict(value)['number'])
        return 1

    def draw(self, entries, ox, oy):
        for kind, body in entries:
            if not isinstance(body, list) or 'name' not in dict(body):
                continue
            f = dict(body)
            pos = dict(f['position']) if 'position' in f else {'x': '0', 'y': '0'}
            x, y = ox + int(pos['x']), oy + int(pos['y'])
            name, scripted = f['name'], f.get('scripted') == 'yes'
            if kind == 'windowType':
                if scripted and self.visible('custom_window', name) is False:
                    continue
                self.draw(body, x, y)
            elif kind == 'iconType':
                if scripted and self.visible('custom_icon', name) is False:
                    continue
                art = sprite_image(f['spriteType'], self.frame_of(name) if scripted else 1, float(f.get('scale', 1)))
                self.canvas.alpha_composite(art, (x, y))
                self.drawn.append((name, x, y, art.width, art.height))
            elif kind == 'guiButtonType':
                if scripted and self.visible('custom_button', name) is False:
                    continue
                art = sprite_image(f['quadTextureSprite'], 1, float(f.get('scale', 1)))
                self.canvas.alpha_composite(art, (x, y))
                self.drawn.append((name, x, y, art.width, art.height))
                label = f.get('buttonText')
                if label:
                    draw_text(self.canvas, self.resolve(LOC.get(label, label)), x + 8, y + (art.height - 18) // 2, art.width - 16, 18,
                              f.get('buttonFont', 'vic_18'), True, name)
            elif kind == 'instantTextBoxType':
                if scripted and self.visible('custom_text_box', name) is False:
                    continue
                key = f['text']
                if key not in LOC:
                    problems.append(f'{name}: localisation key {key} is missing')
                draw_text(self.canvas, self.resolve(LOC.get(key, key)), x, y, int(f['maxWidth']), int(f['maxHeight']),
                          f.get('font', 'vic_18'), f.get('format') in ('center', 'centre'), name)
                self.drawn.append((name, x, y, int(f['maxWidth']), int(f['maxHeight'])))

    def save(self, path, zoom):
        path.parent.mkdir(parents=True, exist_ok=True)
        sheet = Image.new('RGBA', self.canvas.size, (30, 38, 42, 255))
        sheet.alpha_composite(self.canvas)
        if zoom > 1:
            sheet = sheet.resize((sheet.width * zoom, sheet.height * zoom), Image.LANCZOS)
        sheet.convert('RGB').save(path)

    def tooltips(self):
        return {key: re.sub(r'§.', '', self.resolve(LOC[f'rip_ro_holy_city_{key}_myth_progress_tt'])).replace('\\n', ' | ')
                for key, *_ in CITIES}


ALL = (('register', 'fresh'), ('register', 'mid'), ('register', 'matured'), ('church', 'fresh'), ('church', 'schism'))
jobs = ALL if args.panel == 'all' else ((args.panel, args.state),)
failed = False
for panel, state in jobs:
    scene = Scene(panel, state)
    target = args.out / f'{panel}_{state}.png' if args.panel == 'all' else args.out
    scene.save(target, args.zoom)
    print(f'PREVIEW: {panel} / {state}: {len(scene.drawn)} drawn widgets -> {target}')
    if panel == 'register' and not args.quiet:
        for key, text in scene.tooltips().items():
            print(f'  tooltip {key}: {text}')
    for problem in scene.problems:
        print('PROBLEM:', problem)
    failed |= any(not p.startswith('font ') for p in scene.problems)
print('Source-layout preview with sample values: not an engine render, hover or click test.')
sys.exit(1 if failed else 0)
