"""Contract of the Ruthenian parliament naming system (tools/build_parliament_names.py).

The first system wrote [Root.GetRIPParliamentName] into the vanilla keys <TAG>_parliament_name, which the game reads
as plain text: the window said "Chernihivan [Root.GetRIPParliamentName]". The title is now drawn by a scripted text
box in the parliament window, which has a country scope, and the plain keys hold plain nouns. This test pins:
  - no plain key and no vanilla-read key contains a [command];
  - every parliament a RIP reform grants, and every Ruthenian government type, resolves to a specific title,
    a country that is not Ruthenian resolves to vanilla's own title, and no reform id in the rules is invented
    (the old ladder tested chr_siversk_veche_reform, which does not exist);
  - the window carries the overlay, the native title is parked outside it, the binding exists;
  - every title fits the 548 px title line at vic_29s;
  - the Ukrainian guide lists every title.
It cannot show the window in EU4; docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md says what is and is not verified.
"""
import re
import subprocess
import sys

from clausewitz_testlib import ROOT, keyed_blocks, matching_brace, named_block, read, vanilla_root

LANGUAGES = ('english', 'french', 'german', 'spanish')
loc = {lang: dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(f'localisation/replace/zzzz_rip_parliament_names_l_{lang}.yml'), re.M))
       for lang in LANGUAGES}
english = loc['english']
ladder = read('customizable_localization/rip_parliament_names.txt')
choices = [(named_block(block, 'trigger'), re.search(r'localisation_key = (\w+)', block)[1]) for _, block in keyed_blocks(ladder, 'text')]
assert 'name = GetRIPParliamentTitle' in ladder and 'GetRIPParliamentName' not in ladder


def evaluate(text, country):
    """First-match evaluation of one trigger over the few triggers the rules use."""
    tokens = re.findall(r'[{}=]|[^\s{}=]+', text)
    pos = 0

    def parse(mode='AND'):
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos]
            assert tokens[pos + 1] == '=', (key, tokens[pos:pos + 3])
            pos += 2
            value = tokens[pos]
            pos += 1
            if value == '{':
                result.append(parse(key))
                assert tokens[pos] == '}'
                pos += 1
            elif key == 'has_reform':
                result.append(value in country['reforms'])
            elif key == 'tag':
                result.append(value == country['tag'])
            elif key == 'government':
                result.append(value == country['government'])
            elif key == 'primary_culture':
                result.append(value == country['culture'])
            elif key == 'always':
                result.append(value == 'yes')
            else:
                raise AssertionError('unsupported trigger ' + key)
        return any(result) if mode == 'OR' else not any(result) if mode == 'NOT' else all(result)
    return parse()


def title(tag, government='monarchy', culture='ruthenian', reforms=()):
    country = dict(tag=tag, government=government, culture=culture, reforms=set(reforms))
    key = next(key for trigger, key in choices if evaluate(trigger, country))
    return english[key]


ADJ = '[Root.GetAdjective]'
# ---- Parliaments that RIP reforms grant, and what each is called -----------------------------------------
expected = [
    ('KRU', 'monarchy', 'ruthenian', ['ruthenian_factional_empire_reform'], 'Rada of Three Estates'),
    ('KRU', 'monarchy', 'ruthenian', ['ruthenian_factional_empire_princes_hetmans_reform'], 'Rada of Three Estates'),
    ('KRU', 'monarchy', 'ruthenian', ['ruthenian_factional_empire_boyars_hetmans_reform'], 'Rada of Three Estates'),
    ('KIE', 'monarchy', 'ruthenian', ['kyivan_cesarstvo_reform'], 'Sobor of the Lands'),
    ('KIE', 'monarchy', 'ruthenian', ['kyivan_shogunate_reform'], 'Princely Snem'),
    ('KIE', 'republic', 'ruthenian', ['kyivan_veche_reform'], 'Kyivan Veche'),
    ('KIE', 'republic', 'ruthenian', ['kyivan_boyar_republic_reform'], 'Kyivan Boyar Rada'),
    ('CHR', 'republic', 'ruthenian', ['siversk_veche_reform'], 'Siversk Veche'),
    ('CHR', 'republic', 'ruthenian', ['chr_desna_staple_reform'], 'Desna Staple Council'),
    ('CHR', 'republic', 'ruthenian', ['chr_town_union_reform'], 'Assembly of the Siversk Towns'),
    ('CHR', 'republic', 'ruthenian', ['chr_rada_of_lands_reform'], 'Rada of the Lands'),
    ('CHR', 'republic', 'ruthenian', ['chr_kanceliaryst_republic_reform'], 'Chancery Rada'),
    ('CHR', 'monarchy', 'ruthenian', ['chr_siversk_principality_reform'], 'Siversk Boyar Rada'),
    ('HET', 'monarchy', 'ruthenian', ['het_mazepist_autocracy_reform'], 'Baturyn Rada'),
    ('HET', 'monarchy', 'ruthenian', ['het_starshyna_oligarchy_reform'], 'Starshyna Rada'),
    ('HET', 'republic', 'ruthenian', ['het_regimental_system_reform'], 'Regimental Rada'),
    ('HLC', 'monarchy', 'ruthenian', ['hlc_galician_sejm_reform'], 'Galician Sejm'),
    ('HLC', 'monarchy', 'ruthenian', ['hlc_austrian_bureaucracy_reform'], 'Estates of Galicia and Lodomeria'),
    ('HLC', 'monarchy', 'ruthenian', ['hlc_crown_authority_reform'], 'Estates of Galicia and Lodomeria'),
    ('HLC', 'republic', 'ruthenian', ['hlc_boyar_republic_reform'], 'Halych Boyar Rada'),
    ('LIT', 'monarchy', 'lithuanian', ['lit_grand_diet_reform'], 'Diet of the Grand Duchy'),
    ('LIT', 'monarchy', 'lithuanian', ['lit_union_of_two_nations_reform'], 'Sejm of Two Nations'),
    ('LIT', 'monarchy', 'lithuanian', ['lit_pany_rada_reform'], 'Pany-Rada'),
    ('LIT', 'monarchy', 'lithuanian', [], 'Seimas'),
    ('VLN', 'republic', 'ruthenian', ['vln_sejmik_republic_reform'], 'Volhynian Sejmik'),
    ('VLN', 'monarchy', 'ruthenian', ['vln_ruthenia_reform'], 'Sejm of Ruthenia'),
    ('VLN', 'monarchy', 'ruthenian', ['vln_grand_ruthenia_reform'], 'Sejm of Grand Ruthenia'),
    ('UZH', 'monarchy', 'ruthenian', ['uzh_palatial_ruthenian_reform'], 'Palatine Diet'),
    ('UZH', 'monarchy', 'ruthenian', ['uzh_komitat_system_reform'], 'Komitat Assembly'),
    ('UZH', 'monarchy', 'ruthenian', ['uzh_palanok_captaincy_reform'], 'Palanok Council'),
    ('PDL', 'monarchy', 'ruthenian', ['pdl_clan_assembly_reform'], 'Podilian Land Assembly'),
    ('PRL', 'republic', 'ruthenian', ['prl_regimental_republic_reform'], 'Pereiaslav Regimental Rada'),
    ('ODS', 'republic', 'ruthenian', ['odesa_trade_republic_reform'], 'Odesa Merchant Council'),
    ('ZAZ', 'republic', 'ruthenian', ['zaz_general_rada_reform'], 'General Sich Rada'),
    ('ZAZ', 'republic', 'ruthenian', [], 'Sich Rada'),
    ('SMY', 'monarchy', 'ruthenian', [], 'Sumy Regimental Rada'),
    ('CHR', 'monarchy', 'ruthenian', ['assembly_houses_reform'], f'{ADJ} Burgher Assembly'),
    ('CHR', 'monarchy', 'ruthenian', ['legislative_rada_reform'], f'{ADJ} Legislative Rada'),
    ('CHR', 'monarchy', 'ruthenian', ['boyar_elite_reform'], f'{ADJ} Boyar Rada'),
]
for tag, government, culture, held, want in expected:
    assert title(tag, government, culture, held) == want, (tag, government, held, title(tag, government, culture, held), want)

# Every parliament a RIP reform grants has a title of its own; the three Rada ids are one government on purpose.
granting = []
for path in sorted((ROOT / 'common/government_reforms').glob('*.txt')):
    source = path.read_text(encoding='utf-8-sig', errors='replace')
    for match in re.finditer(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', source):
        block = source[match.start():matching_brace(source, source.index('{', match.start())) + 1]
        if re.search(r'has_parliament\s*=\s*yes', block):
            granting.append(match[1])
assert len(granting) >= 16, granting
generic = {f'{ADJ} [Root.GetParliamentName]', 'Rada of the Land', f'{ADJ} Veche', f'{ADJ} Sobor'}
fallthrough = [reform for reform in granting if title('CHR', 'republic', 'ruthenian', [reform]) in generic]
assert not fallthrough, f'these parliament-granting reforms have no rule of their own: {fallthrough}'

# ---- Countries that are not Ruthenian get exactly vanilla's title ----------------------------------------
for tag, culture in (('FRA', 'french'), ('ENG', 'english'), ('POL', 'polish'), ('MOS', 'russian'), ('TUR', 'turkish')):
    for government in ('monarchy', 'republic', 'theocracy'):
        assert title(tag, government, culture) == f'{ADJ} [Root.GetParliamentName]', (tag, government)
for government, want in (('theocracy', f'{ADJ} Sobor'), ('republic', f'{ADJ} Veche'), ('monarchy', 'Rada of the Land')):
    assert title('KUY', government) == want, (government, title('KUY', government))
assert title('HLC', 'republic') == 'Halych Veche', 'the HLC adjective is misspelled in the mod; the title uses the place'
for culture in ('ruthenian', 'rusyn', 'severian', 'ruthenian_new'):
    assert title('XXX', 'monarchy', culture) == 'Rada of the Land', culture      # a released or formed state with a Ruthenian primary culture

# ---- Plain keys ------------------------------------------------------------------------------------------
generator = read('tools/build_parliament_names.py')
nouns = dict(re.findall(r"'([A-Z]{3})': '([^']+)'", generator.split('NOUNS = {')[1].split('}')[0]))
assert len(nouns) >= 27 and 'LIT' not in nouns
for lang in LANGUAGES:
    for tag, noun in nouns.items():
        assert loc[lang][f'{tag}_parliament_name'] == noun, (lang, tag)
    for key, value in loc[lang].items():
        if key.endswith('_parliament_name'):
            assert '[' not in value, f'{lang}: {key} would print as a raw command'
    assert set(loc[lang]) == set(english)
# Nothing else in the mod may define a <TAG>_parliament_name or call the retired command.
for path in sorted((ROOT / 'localisation').rglob('*.yml')):
    if path.name.startswith('zzzz_rip_parliament_names_'):
        continue
    text = path.read_text(encoding='utf-8-sig')
    assert 'GetRIPParliamentName' not in text and '_parliament_name:' not in text, path.name
for stale in ('GetRIPParliamentName',):
    assert stale not in read('tools/build_ruthenian_government_ui.py')

# ---- The window --------------------------------------------------------------------------------------------
gui = read('interface/parliament.gui')
window = named_block(gui, 'windowType')
assert 'name = "parliament_window"' in window
overlay_at = gui.index('name = "rip_parliament_title"')
overlay_start = gui.rfind('instantTextBoxType', 0, overlay_at)
overlay = gui[overlay_start:matching_brace(gui, gui.index('{', overlay_start)) + 1]
assert 'scripted = yes' in overlay and 'text = "rip_parliament_title"' in overlay and 'font = "vic_29s"' in overlay
assert window.index('rip_parliament_title') < window.rindex('select_new_issue_window'), 'the overlay belongs to the window, not the issue list'
parked = re.search(r'position = \{ x=(-?\d+) y=45 \}', gui)
assert parked and int(parked[1]) <= -1000, 'the native title must be parked outside the window'
assert re.search(r'custom_text_box = \{ name = rip_parliament_title potential = \{ always = yes \} \}', read('common/custom_gui/rip_parliament_title.txt'))
assert english['rip_parliament_title'] == '[Root.GetRIPParliamentTitle]'
assert not (ROOT / 'interface/parliament.gui').read_bytes().startswith(b'\xef\xbb\xbf'), 'a BOM breaks a .gui file'

install = vanilla_root()
if install:
    vanilla = (install / 'interface/parliament.gui').read_text(encoding='utf-8-sig')
    cleaned = gui.replace(overlay, '').replace(parked[0], 'position = { x=0 y =45}')
    assert re.sub(r'\s+', '', cleaned) == re.sub(r'\s+', '', vanilla), 'only the title is changed in the vanilla window'
    # Width: the longest title, with the widest adjective and parliament name the game could substitute.
    advance = {}
    for line in (install / 'gfx/fonts/vic_29s.fnt').read_text(encoding='latin-1').splitlines():
        if line.startswith('char '):
            fields = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', line)}
            advance[fields['id']] = fields['xadvance']
    widest = {'[Root.GetAdjective]': "Pereiaslavlian", '[Root.GetParliamentName]': 'Staten-Generaal'}
    for key, value in english.items():
        if key.startswith('rip_parliament_title_'):
            shown = value
            for command, text in widest.items():
                shown = shown.replace(command, text)
            assert sum(advance[ord(c)] for c in shown) <= 548 - 40, (key, shown)

# ---- The generator is current, and the guide lists every title ----------------------------------------
result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/build_parliament_names.py'), '--check'], capture_output=True, text=True)
assert result.returncode == 0, result.stdout + result.stderr
guide = read('docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md')
for key, value in english.items():
    if key.startswith('rip_parliament_title_') and not value.startswith(ADJ):
        assert value in guide, f'the guide does not list "{value}"'
for tag in nouns:
    assert f'`{tag}`' in guide, f'the guide does not list the plain noun of {tag}'
print(f'PASS: {len(choices)} parliament naming rules, {len(expected)} country and reform cases, plain nouns in four languages, '
      'title overlay in the parliament window')
