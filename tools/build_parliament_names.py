"""Build the naming system for the parliaments of the Ruthenian states.

Why it exists. The first system put `[Root.GetRIPParliamentName]` into the vanilla keys `<TAG>_parliament_name`.
The game reads those keys as plain text when it builds the parliament window title ("<adjective> <name>"), so the
player saw "Chernihivan [Root.GetRIPParliamentName]". A custom-localisation command only works where the engine
has a scope to run it in, and a scripted GUI text box has one: the host window `parliament_window` is a documented
custom_gui host with ROOT = the player's country (common/custom_gui/example.txt).

So the title is now drawn by a scripted text box laid over the native one, and the native `title` is moved out
of the window. The text box asks one defined_text, GetRIPParliamentTitle, which walks the rules below and returns
the whole title, so a name can depend on the government reform and not only on the tag. A country that matches no
Ruthenian rule gets exactly what vanilla would have shown: "<adjective> <parliament name>".

The plain keys `<TAG>_parliament_name` remain, now as plain nouns, for everything that does not run through the
window: events and tooltips that say `[Root.GetParliamentName]`, and the native title if the overlay is ever off.

Outputs (all written, or compared with --check):
  customizable_localization/rip_parliament_names.txt       GetRIPParliamentTitle, first matching rule wins
  common/custom_gui/rip_parliament_title.txt                the text-box binding
  interface/parliament.gui                                  vanilla window with the overlay and the native title moved
  localisation/replace/zzzz_rip_parliament_names_l_*.yml    titles and plain nouns (English text in all four languages)
Names follow docs/STYLE_GLOSSARY.md: the institution is named, native terms stay untranslated, every significant
word is capitalised, "Veche" is spelled as in the reform names. docs/RUTHENIAN_PARLIAMENT_NAMES.uk.md explains each rule.
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tests'))
from clausewitz_testlib import matching_brace, vanilla_root  # noqa: E402

GAME = vanilla_root()
LANGUAGES = ('english', 'french', 'german', 'spanish')

# The Ruthenian tags of the mod. Each gets a plain noun in <TAG>_parliament_name (LIT keeps vanilla's Seimas).
NOUNS = {
    'KIE': 'Veche', 'KRU': 'Rada', 'UKR': 'Rada', 'RUT': 'Zemsky Sobor', 'CHR': 'Veche', 'VLN': 'Sejmik',
    'HLC': 'Sejm', 'UZH': 'Komitat Assembly', 'PRL': 'Rada', 'PDL': 'Sejmik', 'ODS': 'Merchant Council',
    'ZAZ': 'Sich Rada', 'HET': 'Starshyna Rada', 'KUY': 'Veche', 'RPS': 'Veche', 'SMY': 'Regimental Rada',
    'OKH': 'Regimental Rada', 'IZM': 'Regimental Rada', 'KHK': 'Regimental Rada', 'ZLK': 'Rada', 'SRK': 'Rada',
    'MSK': 'Veche', 'TRV': 'Veche', 'VTB': 'Veche', 'MSL': 'Veche', 'BLR': 'Rada', 'PLT': 'Veche',
}
TAGS = list(NOUNS) + ['LIT']
CULTURES = ('ruthenian', 'ruthenian_new', 'rusyn', 'rusyn_new', 'rusyn_new_new', 'severian', 'severian_new')
RUTHENIAN = ('OR = { ' + ' '.join(f'tag = {t}' for t in TAGS) + ' '
             + ' '.join(f'primary_culture = {c}' for c in CULTURES) + ' }')
ADJ = '[Root.GetAdjective]'


def reforms(*names):
    return 'OR = { ' + ' '.join(f'has_reform = {n}' for n in names) + ' }' if len(names) > 1 else f'has_reform = {names[0]}'


# (id, title, trigger, why). The first rule whose trigger holds names the parliament. Reform rules come first because
# a reform is the most specific fact about a government; tags and government types follow; the last rule is vanilla's.
RULES = [
    # --- the Kyivan line
    ('cesarstvo', 'Sobor of the Lands', reforms('kyivan_cesarstvo_reform'),
     'The Cesarstvo calls the lands, not a town: a sobor, as the Russian estates assembly was called.'),
    ('three_estates', 'Rada of Three Estates', reforms('ruthenian_factional_empire_reform', 'ruthenian_factional_empire_princes_hetmans_reform', 'ruthenian_factional_empire_boyars_hetmans_reform'),
     'One government under three reform ids; the name is the reform name.'),
    ('snem', 'Princely Snem', reforms('kyivan_rus_reform', 'kyivan_shogunate_reform'),
     'The seniorate meets as the princes met at Liubech in 1097: a snem of princes.'),
    ('kyivan_boyar', 'Kyivan Boyar Rada', reforms('kyivan_boyar_republic_reform'),
     'The veche hardens into a council of boyar lineages: the reform name.'),
    ('kyivan_veche', 'Kyivan Veche', reforms('kyivan_veche_reform'),
     'The town assembly that elects a posadnik.'),
    ('kyivan_synod', 'Synod of Kyiv', reforms('kyivan_church_synod_reform'),
     'A government of bishops sits as a synod.'),
    # --- Chernihiv and the Siverian land
    ('siversk_veche', 'Siversk Veche', reforms('siversk_veche_reform'),
     'Siversk Merchant Veche. The old ladder tested chr_siversk_veche_reform, an id that does not exist.'),
    ('desna_staple', 'Desna Staple Council', reforms('chr_desna_staple_reform'),
     'The staple right on the Desna is held by the merchants who meet in this council.'),
    ('siversk_towns', 'Assembly of the Siversk Towns', reforms('chr_town_union_reform'),
     'Union of the Siversk Towns: each town sends its delegates.'),
    ('rada_of_lands', 'Rada of the Lands', reforms('chr_rada_of_lands_reform'),
     'The reform name.'),
    ('siversk_boyar', 'Siversk Boyar Rada', reforms('chr_siversk_principality_reform'),
     'The Siversk prince governs with a boyar council.'),
    ('chancery_rada', 'Chancery Rada', reforms('chr_kanceliaryst_republic_reform'),
     'Office goes by chancery examination; the body that sits is the rada of the chancery.'),
    ('many_nations', 'Rada of Many Nations', reforms('chr_many_nations_union_reform'),
     'Every people brought in writes its clause into the union and sends its delegates.'),
    ('prykaz_sobor', 'Zemsky Sobor', reforms('chr_prykaz_tsardom_reform'),
     'The tsardom of the prykazy meets as a zemsky sobor: the Muscovite pattern this path copies.'),
    ('magistrat', 'Council of the Magistrat', reforms('chr_magistrat_rule_reform'),
     'The magistrat rules the town through its council.'),
    # --- the Hetmanate and the Cossack hosts
    ('baturyn', 'Baturyn Rada', reforms('het_mazepist_autocracy_reform'),
     'The Baturyn court of the hetman.'),
    ('starshyna', 'Starshyna Rada', reforms('het_starshyna_oligarchy_reform', 'het_hetman_for_life_reform'),
     'The officers advise the hetman.'),
    ('regimental', 'Regimental Rada', reforms('het_regimental_system_reform'),
     'The regiments meet as radas of their colonels and sotnia officers.'),
    ('collegium', 'Collegium of Little Russia', reforms('het_collegium_control_reform'),
     'The Little Russian Collegium; its members are the assembly.'),
    ('general_sich', 'General Sich Rada', reforms('zaz_general_rada_reform'),
     'The General Rada of the Sich.'),
    ('kosh', 'Kosh Rada', reforms('zaz_kosh_elections_reform'),
     'The Kosh elects its otaman in the rada.'),
    ('sich', 'Sich Rada', 'OR = { tag = ZAZ has_reform = rip_cossacks_reform }',
     'The vanilla cossack reform is called Sich Rada in the mod; every Zaporozhian state keeps the name.'),
    ('sumy', 'Sumy Regimental Rada', 'tag = SMY', 'Sloboda regiment.'),
    ('okhtyrka', 'Okhtyrka Regimental Rada', 'tag = OKH', 'Sloboda regiment.'),
    ('kharkiv', 'Kharkiv Regimental Rada', 'tag = KHK', 'Sloboda regiment.'),
    ('izium', 'Izium Regimental Rada', 'tag = IZM', 'Sloboda regiment.'),
    ('officers', 'Starshyna Rada', 'tag = HET government = monarchy',
     'A hetman ruling for life sits with his starshyna.'),
    ('general_rada', 'General Military Rada', 'tag = HET',
     'A republican Hetmanate meets as the General Military Rada.'),
    # --- Halych
    ('galician_sejm', 'Galician Sejm', reforms('hlc_galician_sejm_reform', 'hlc_crown_and_sejm_reform'),
     'The Polish fork of the voivodeship: the sejm of the land.'),
    ('galician_estates', 'Estates of Galicia and Lodomeria', reforms('hlc_austrian_bureaucracy_reform', 'hlc_crown_authority_reform'),
     'The Austrian fork: the Habsburg crown land called its diet the Estates of Galicia and Lodomeria.'),
    ('magnate_sejm', 'Magnate Sejm', reforms('hlc_magnate_assembly_reform'),
     'Estate Compact: the magnates sit in their own sejm.'),
    ('halych_boyar', 'Halych Boyar Rada', reforms('hlc_boyar_republic_reform', 'hlc_boyar_oligarchy_reform'),
     'Boyar Republic and Rule of the Great Houses.'),
    # --- Lithuania
    ('commonwealth_sejm', 'Sejm of Two Nations', reforms('lit_union_of_two_nations_reform'),
     'Commonwealth of Two Nations.'),
    ('grand_diet', 'Diet of the Grand Duchy', reforms('lit_grand_diet_reform'),
     'The reform name.'),
    ('pany', 'Pany-Rada', reforms('lit_pany_rada_reform', 'lit_ruthenian_chancery_reform'),
     'The council of lords.'),
    ('seimas', 'Seimas', 'tag = LIT', 'Vanilla name of the Lithuanian assembly.'),
    # --- Volhynia
    ('sejmik', 'Volhynian Sejmik', reforms('vln_sejmik_republic_reform', 'vln_dietine_instructions_reform'),
     'The local sejmik, with a small s as the glossary asks; the instructions reform gives it its mandate.'),
    ('grand_ruthenia', 'Sejm of Grand Ruthenia', reforms('vln_grand_ruthenia_reform'),
     'The sejm of the enlarged realm.'),
    ('ruthenia', 'Sejm of Ruthenia', reforms('vln_ruthenia_reform'),
     'The sejm of the Ruthenian crown claim.'),
    ('confessional_sejmik', 'Confessional Sejmik', reforms('vln_confessional_reform'),
     'Confessional Voivodeship: the voivodeship\'s sejmik, where the confessions sit.'),
    ('host_rada', 'Cossack Host Rada', reforms('vln_cossack_host_reform'),
     'Cossack Host Privileges.'),
    # --- Uzhhorod
    ('palatine_diet', 'Palatine Diet', reforms('uzh_palatial_ruthenian_reform', 'uzh_palatial_rusyn_reform'),
     'The palatine compact meets as a diet under the palatine.'),
    ('komitat', 'Komitat Assembly', reforms('uzh_komitat_system_reform', 'uzh_republican_komitat_system_reform', 'uzh_palatial_uhro_reform', 'uzh_palatial_uhro_republic_reform'),
     'The Hungarian pattern: the county assembly.'),
    ('palanok', 'Palanok Council', reforms('uzh_palanok_captaincy_reform'),
     'The captaincy of the castle: its garrison council.'),
    # --- Podillia, Pereiaslav, Odesa
    ('podilian_land', 'Podilian Land Assembly', reforms('pdl_clan_assembly_reform'), 'The reform name.'),
    ('podilian_aristocrats', 'Podilian Aristocratic Assembly', reforms('pdl_aristocratic_assembly_reform'), 'The reform name.'),
    ('pereiaslav_regimental', 'Pereiaslav Regimental Rada', reforms('prl_regimental_republic_reform'), 'Regimental republic.'),
    ('odesa_merchants', 'Odesa Merchant Council', reforms('odesa_trade_republic_reform'), 'The free port is governed by its merchants.'),
    # --- reforms shared by every Ruthenian state
    ('boyar_rada', f'{ADJ} Boyar Rada', reforms('boyar_elite_reform', 'ruthenian_principality_reform'),
     'Boyar Rada (renamed from boyar elite): the prince is advised by a council, not by Moscow\'s duma.'),
    ('veche_assemblies', f'{ADJ} Veche', reforms('elected_assemblies_reform'), 'Veche Assemblies.'),
    ('burghers', f'{ADJ} Burgher Assembly', reforms('assembly_houses_reform'), 'Burgher Assemblies.'),
    ('legislative_rada', f'{ADJ} Legislative Rada', reforms('legislative_rada_reform'), 'The reform name.'),
    # --- government types, Ruthenian states only
    ('sobor', f'{ADJ} Sobor', f'{RUTHENIAN} government = theocracy',
     'A church government sits as a sobor.'),
    ('halych_veche', 'Halych Veche', 'tag = HLC government = republic',
     'The adjective of HLC is spelled Halycian in the mod; the place name is used instead.'),
    ('veche', f'{ADJ} Veche', f'{RUTHENIAN} government = republic',
     'Every other Ruthenian republic: the town assembly under the state\'s own adjective.'),
    ('land', 'Rada of the Land', RUTHENIAN,
     'Every other Ruthenian government with a parliament: the assembly of the land.'),
    # --- everyone else: what the game shows without this file
    ('vanilla', f'{ADJ} [Root.GetParliamentName]', 'always = yes',
     'Exactly the vanilla title: the adjective and the plain parliament name.'),
]


def validate():
    """Every reform id and tag a rule names must exist; ids and titles must be unique; no leaf may be empty."""
    errors = []
    ids = [rule[0] for rule in RULES]
    if len(ids) != len(set(ids)):
        errors.append('duplicate rule ids')
    folders = [ROOT / 'common/government_reforms'] + ([GAME / 'common/government_reforms'] if GAME else [])
    known = set()
    for folder in folders:
        for path in folder.glob('*.txt'):
            known.update(re.findall(r'(?m)^([A-Za-z0-9_]+)\s*=\s*\{', path.read_text(encoding='utf-8-sig', errors='replace')))
    tag_files = [ROOT / 'common/country_tags'] + ([GAME / 'common/country_tags'] if GAME else [])
    tags = set()
    for folder in tag_files:
        for path in folder.glob('*.txt'):
            tags.update(re.findall(r'(?m)^([A-Z0-9]{3})\s*=', path.read_text(encoding='utf-8-sig', errors='replace')))
    for rule_id, title, trigger, why in RULES:
        for reform in re.findall(r'has_reform = (\w+)', trigger):
            if reform not in known:
                errors.append(f'{rule_id}: reform {reform} is not defined')
        for tag in re.findall(r'\btag = ([A-Z0-9]{3})', trigger):
            if tags and tag not in tags:
                errors.append(f'{rule_id}: tag {tag} is not defined')
        if not title or '"' in title or '\n' in title:
            errors.append(f'{rule_id}: bad title')
    for tag in TAGS:
        if tags and tag not in tags:
            errors.append(f'tag {tag} is not defined')
    if errors:
        raise SystemExit('Parliament naming rules are inconsistent:\n  ' + '\n  '.join(errors))


def leaf_key(rule_id):
    return 'rip_parliament_title_' + rule_id


def custom_loc():
    lines = ['# Generated by tools/build_parliament_names.py - edit the RULES table there.',
             '# The title of the parliament window. The first rule whose trigger holds names the parliament; the',
             '# last rule is vanilla\'s own title. Read only by the scripted text box rip_parliament_title.',
             'defined_text = {', '\tname = GetRIPParliamentTitle']
    for rule_id, title, trigger, why in RULES:
        lines.append('\ttext = {')
        lines.append('\t\ttrigger = { ' + trigger + ' }')
        lines.append(f'\t\tlocalisation_key = {leaf_key(rule_id)}')
        lines.append('\t}')
    lines.append('}')
    return '\n'.join(lines) + '\n'


def localisation(language):
    rows = ['rip_parliament_title:0 "[Root.GetRIPParliamentTitle]"']
    rows += [f'{leaf_key(rule_id)}:0 "{title}"' for rule_id, title, trigger, why in RULES]
    rows += [f'{tag}_parliament_name:0 "{noun}"' for tag, noun in NOUNS.items()]
    return (f'l_{language}:\n # Generated by tools/build_parliament_names.py; English text in every language until a translator takes it.\n'
            + ''.join(f' {row}\n' for row in rows))


GUI_BINDING = 'custom_text_box = { name = rip_parliament_title potential = { always = yes } }\n'
OVERLAY = (' instantTextBoxType = {\n'
           '  name = "rip_parliament_title" scripted = yes position = { x=0 y=45 } Orientation = "UPPER_LEFT"\n'
           '  font = "vic_29s" borderSize = { x=0 y=0 } text = "rip_parliament_title" maxWidth = 548 maxHeight = 24 format = center\n'
           ' }\n')
NATIVE_PARKED = 'position = { x=-2000 y=45 }'


def gui(source):
    """The vanilla window with the scripted title laid where the native one was, and the native one moved away."""
    window = source.index('name = "parliament_window"')
    title = source.index('name = "title"', window)
    start = source.rfind('instantTextBoxType', 0, title)
    end = matching_brace(source, source.index('{', start)) + 1
    block = source[start:end]
    parked, count = re.subn(r'position\s*=\s*\{\s*x\s*=\s*0\s+y\s*=\s*45\s*\}', NATIVE_PARKED, block, count=1)
    assert count == 1, 'the native parliament title moved; review the overlay before regenerating'
    assert source.index('name = "start_issue"', window) > end, 'the first title is not the window title'
    # The overlay goes after the native block, so it is drawn on top of the window background.
    line_end = source.index('\n', end) + 1
    return source[:start] + parked + source[end:line_end] + OVERLAY + source[line_end:]


def outputs():
    result = {
        'customizable_localization/rip_parliament_names.txt': custom_loc(),
        'common/custom_gui/rip_parliament_title.txt': GUI_BINDING,
    }
    for language in LANGUAGES:
        result[f'localisation/replace/zzzz_rip_parliament_names_l_{language}.yml'] = '﻿' + localisation(language)
    if GAME is not None:
        result['interface/parliament.gui'] = gui((GAME / 'interface/parliament.gui').read_text(encoding='utf-8-sig'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    validate()
    stale = []
    for relative, text in outputs().items():
        path = ROOT / relative
        data = text.replace('\r\n', '\n')
        bom = data.startswith('﻿')
        payload = data.lstrip('﻿').replace('\n', '\r\n').encode('utf-8')
        if bom:
            payload = b'\xef\xbb\xbf' + payload
        current = path.read_bytes().replace(b'\r\n', b'\n') if path.exists() else None
        if current != payload.replace(b'\r\n', b'\n'):
            stale.append(relative)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
    if GAME is None:
        print('SKIP: interface/parliament.gui needs the vanilla install (EU4_DIR); the committed file is unchanged')
    print(('STALE' if args.check and stale else 'GENERATED' if stale else 'CURRENT')
          + f': parliament naming, {len(RULES)} rules, {len(NOUNS)} plain nouns, {len(stale)} files')
    if args.check and stale:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
