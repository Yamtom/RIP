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
  - the ladder says `random = no`: EU4 does NOT take the first row that holds unless it is told to (measured 2026-10-19: with three
    rows holding, thirty evaluations on one date gave the second row every time), so a ladder without it names a parliament at random
    among the rows that hold - the Rada of Three Estates came out as "Rada of the Land", the vanilla fallback came up for any country;
  - every tag by form of government resolves to a name of its own (never to vanilla's fallback), every rule is the first match of at
    least one country (no rule is hidden by an earlier one), and the table in the guide is the generated one;
  - the Ukrainian guide lists every title.
It cannot show the window in EU4; docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md says what is and is not verified.
"""
import importlib.util
import re
import subprocess
import sys

from clausewitz_testlib import ROOT, keyed_blocks, matching_brace, named_block, read, vanilla_root

spec = importlib.util.spec_from_file_location('build_kru_rada', ROOT / 'tools/build_kru_rada.py')
rada = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rada)

LANGUAGES = ('english', 'french', 'german', 'spanish')
loc = {lang: dict(re.findall(r'^ ([\w.]+):\d+ "(.*)"$', read(f'localisation/replace/zzzz_rip_parliament_names_l_{lang}.yml'), re.M))
       for lang in LANGUAGES}
english = loc['english']
ladder = read('customizable_localization/RIP_shared_parliament_names.txt')
choices = [(named_block(block, 'trigger'), re.search(r'localisation_key = (\w+)', block)[1]) for _, block in keyed_blocks(ladder, 'text')]
assert 'name = GetRIPParliamentTitle' in ladder and 'GetRIPParliamentName' not in ladder
assert re.search(r'name = GetRIPParliamentTitle\s+random = no\b', ladder), 'the ladder must say `random = no`, or the engine draws among the rows that hold'


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
    *[('KRU', 'monarchy', 'ruthenian', [reform], 'Rada of Three Estates') for reform in rada.REFORM_IDS],
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
    # the state's own assembly, once no reform names the parliament
    ('VLN', 'monarchy', 'ruthenian', [], 'Volhynian Sejmik'),
    ('VLN', 'republic', 'ruthenian', [], 'Volhynian Sejmik'),
    ('VLN', 'theocracy', 'ruthenian', [], 'Volhynian Sobor'),
    ('HLC', 'monarchy', 'ruthenian', [], 'Halych Sejm'),
    ('HLC', 'republic', 'ruthenian', [], 'Halych Veche'),
    ('HLC', 'theocracy', 'ruthenian', [], 'Halych Sobor'),
    ('KRU', 'monarchy', 'ruthenian', [], f'{ADJ} [Root.GetParliamentName]'),
    ('RUT', 'monarchy', 'ruthenian', [], f'{ADJ} [Root.GetParliamentName]'),
    ('UZH', 'republic', 'ruthenian', [], f'{ADJ} [Root.GetParliamentName]'),
    ('ODS', 'monarchy', 'ruthenian', [], f'{ADJ} [Root.GetParliamentName]'),
    ('KIE', 'theocracy', 'ruthenian', [], f'{ADJ} Sobor'),
    ('HET', 'monarchy', 'ruthenian', [], 'Starshyna Rada'),
    ('HET', 'republic', 'ruthenian', [], 'General Military Rada'),
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
    assert title('XXX', government) == want, (government, title('XXX', government))          # a released or formed state: no noun of its own
assert title('HLC', 'republic') == 'Halych Veche', 'the HLC adjective is misspelled in the mod; the title uses the place'
for culture in ('ruthenian', 'rusyn', 'ruthenian_new', 'rusyn_new', 'rusyn_new_new'):
    assert title('XXX', 'monarchy', culture) == 'Rada of the Land', culture      # a released or formed state with a Ruthenian primary culture

# ---- Every tag by form of government, every rule reachable, the guide's table is the generated one ----------------
spec = importlib.util.spec_from_file_location('build_parliament_names', ROOT / 'tools/build_parliament_names.py')
generator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator_module)


def first_of(rules, tag, form, culture, held=()):
    country = dict(tag=tag, government=form, culture=culture, reforms=set(held))
    return next(rule for rule in rules if generator_module.evaluate(rule[2], country))


def ladder_problems(ladder_text, rules):
    """What the ladder file and the rules must satisfy; the planted violations below break each of them in memory."""
    found = []
    if not re.search(r'name = GetRIPParliamentTitle\s+random = no\b', ladder_text):
        found.append('the ladder does not say `random = no`: EU4 draws among the rows that hold instead of taking the first')
    for tag in generator_module.TAGS:
        culture = 'lithuanian' if tag == 'LIT' else 'ruthenian'
        for form in generator_module.FORMS:
            if first_of(rules, tag, form, culture)[0] == 'vanilla':
                found.append(f"{tag} in a {form} falls to vanilla's own title")
    reform_ids = sorted({r for rule in rules for r in re.findall(r'has_reform = (\w+)', rule[2])})
    reached = set()
    for tag in generator_module.TAGS + ['XXX', 'FRA']:
        for form in generator_module.FORMS:
            for culture in ('ruthenian', 'french'):
                for held in [()] + [(r,) for r in reform_ids]:
                    reached.add(first_of(rules, tag, form, culture, held)[0])
    hidden = [rule[0] for rule in rules if rule[0] not in reached]
    if hidden:
        found.append(f'these rules are the first match of no country - an earlier rule hides them: {hidden}')
    return found


def planted_violations():
    rules = generator_module.RULES
    by_id = {rule[0]: rule for rule in rules}
    cases = {
        'a ladder without random = no': ladder_problems(ladder.replace('\trandom = no\n', ''), rules),
        'the generic Rada of the Land ahead of everything': ladder_problems(ladder, [by_id['land']] + [r for r in rules if r[0] != 'land']),
        'the generic Veche ahead of everything': ladder_problems(ladder, [by_id['veche']] + [r for r in rules if r[0] != 'veche']),
        'no rule for a Ruthenian tag but vanilla': ladder_problems(ladder, [r for r in rules if r[0] not in ('home_assembly', 'land', 'veche', 'sobor')]),
        'the Rada reform rule behind the tag rows': ladder_problems(ladder, [r for r in rules if r[0] != 'three_estates'] + [by_id['three_estates']]),
    }
    return [name for name, found in cases.items() if not found], len(cases)


for tag in generator_module.TAGS:
    culture = 'lithuanian' if tag == 'LIT' else 'ruthenian'
    for form in generator_module.FORMS:
        rule_id = generator_module.first_rule(tag, form, culture)[0]
        assert title(tag, form, culture) == english['rip_parliament_title_' + rule_id], (tag, form, rule_id)
problems = ladder_problems(ladder, generator_module.RULES)
assert not problems, problems
missed, planted_count = planted_violations()
assert not missed, f'planted violations not caught: {missed}'
guide_text = read('docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md').replace('\r\n', '\n')
assert generator_module.doc_block() in guide_text, 'the table in the guide is not the generated one: run python tools/build_parliament_names.py'

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
print(f'PASS: {len(choices)} parliament naming rules, {len(expected)} country and reform cases, {len(generator_module.TAGS)} tags by three forms of government, '
      f'every rule reachable, `random = no`, plain nouns in four languages, title overlay in the parliament window; {planted_count} planted violations caught')
