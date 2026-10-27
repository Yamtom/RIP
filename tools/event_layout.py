"""Country/family event layout. Whole event bodies and ordered tokens are immutable.

Flat files follow vanilla's event loader layout. Labels describe content ownership,
not extra tag restrictions. Vanilla filename overrides must retain their names.
"""
from pathlib import Path
import re
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#"]+')


def tokens(text):
    return [m[0] for m in TOKEN.finditer(text) if not m[0].startswith('#')]


def statements(text):
    """Top-level statements, including their leading comments; quote-aware."""
    entries = [m for m in TOKEN.finditer(text) if not m[0].startswith('#')]
    i = start = 0
    while i < len(entries):
        key = entries[i][0]
        assert entries[i + 1][0] == '=', (key, entries[i + 1][0])
        j = i + 3
        if entries[i + 2][0] == '{':
            depth = 1
            while depth:
                depth += (entries[j][0] == '{') - (entries[j][0] == '}')
                j += 1
        end = entries[j - 1].end()
        yield key, text[start:end].strip()
        start, i = end, j
    if text[start:].strip():
        yield '#tail', text[start:].strip()


def event_id(body):
    code = tokens(body)
    depth = 0
    for i, token in enumerate(code):
        depth += (token == '{') - (token == '}')
        if depth == 1 and token == 'id' and code[i + 1] == '=':
            return code[i + 2].strip('"')
    raise ValueError('Event definition has no top-level id')


def format_script(text):
    """One assignment per line, tabs, preserved strings/comments and token order."""
    entries = [m[0] for m in TOKEN.finditer(text)]
    lines, i = [], 0

    def block(depth):
        nonlocal i
        while i < len(entries):
            key = entries[i]
            if key.startswith('#'):
                lines.append('\t' * depth + key.rstrip())
                i += 1
            elif key == '}':
                assert depth
                i += 1
                return
            else:
                if depth == 0 and lines:
                    lines.append('')
                if i + 1 < len(entries) and entries[i + 1] == '=':
                    value = entries[i + 2]
                    lines.append('\t' * depth + key + ' = ' + value)
                    i += 3
                    if value == '{':
                        block(depth + 1)
                        lines.append('\t' * depth + '}')
                else:
                    # Positional values (e.g. colors) are legitimate Clausewitz.
                    assert depth and key != '{', key
                    lines.append('\t' * depth + key)
                    i += 1
        assert depth == 0

    block(0)
    result = '\n'.join(lines) + '\n'
    assert tokens(result) == tokens(text)
    return result


FAMILIES = {
    'CHR': 'Chernihiv ChernihivHistorical ChernihivPaths CHR_Enterprise_Events CHR_Pantheon_Events',
    'HET': 'HetmanateCossackRaids HetmanateEnhanced HetmanateFlavor HetmanateLegacyEras HetmanateMissionRefresh HetmanateMoldovanExpansion HetmanateOrthodoxCrusade HetmanateRegimentalGovernance HetmanateSuccession RIP_HetmanAuthority RIP_HetmanElection Ruina Hadiach',
    'ZAZ': 'ZAZmission ZaporozhianSich ZaporozhianCrisis ZaporizhiaPaths ZaporizhianCrossroadsHistory ZaporizhiaFlavor ZaporizhiaFixes',
    'UZH': 'Uzh PalanokFortress RIP_UzhLocalUnion',
    'PDL': 'Podillia_Events Podillia_Disasters PodilliaDisasters PodilliaBorderPolicy',
    'PRL': 'PereiaslavFlavor', 'ODS': 'OdesaRepublic',
    'VOL': 'VOL_path_events VOLmission Volhynia_Alt_History WestUkraineMissionRefresh',
    'VLN': 'VolhynianConcessions', 'HLC': 'RIP_Galicia_AltHistory',
    'LIT': 'LithuanianConfession VilniusPalace',
    'KIE': 'KIEmission KyivShogunate KyivSuccessionHistory KyivTradeHouses',
    'KRU': 'RuthenianDecadence RuthenianFactional',
    'MOS_RUS': 'RIP_RussiaBalance TimeOfTroubles',
    'QAS': 'QasimKhanate',
    'shared_commonwealth': 'CommonwealthReformation FreeElection UnionDispute TheDeluge',
    'shared_cossack': 'CossackRevolts Haidamaky KhmelnytskyUprisings',
    'shared_ruthenian': 'KyivDnieperHistorical RuthenianEastwardExpansion RIP_RuthenianDiaspora',
    'shared_west_ruthenian': 'WestUkraineHistory svydrigaylo_independence',
    'shared_steppe': 'RaidMechanics SteppeRaiding SouthUkraineHistorical',
    'shared_frontier': 'AppanagePrincipalities BorderPrincipalities MoldavianFrontierExpansion DniesterEstuary',
    'shared_belarus': 'PolesianBelarus', 'shared_estates': 'JewishEstate',
    'shared_orthodox': 'OrthodoxCrusade RussianOrthodox RIP_RO_InstitutionalHistory RIP_OrthodoxAuthority RIP_OldBelievers RIP_OldBelieverInstitutions',
    'shared_greek_catholic': 'UniateChurch UniateCrownUnion RIP_ChurchCompact RIP_ChurchCouncils RIP_DiocesanUnion RIP_EparchyHistory RIP_GreekCatholicTest RIP_HabsburgGreekCatholic',
    'shared_church': 'RIP_ChurchNodes_generated RIP_ChurchRedesign RIP_FaithCanons RIP_FaithDisasters RIP_ParishVisit',
}
OWNERS = {stem: family for family, stems in FAMILIES.items() for stem in stems.split()}
SPLIT = {'RIP', 'NovgorodFlavorEvents', 'RIP_FaithReformEvents', 'RIP_RegionalGovernments'}


def destination(stem, eid=None, body=''):
    if stem == 'WomenInHistory':
        return 'events/WomenInHistory.txt'  # Exact-name vanilla override.
    if stem in OWNERS:
        return f'events/RIP_{OWNERS[stem]}_{stem.removeprefix("RIP_")}.txt'
    ns = eid.split('.')[0]
    if stem == 'RIP_RegionalGovernments':
        family = re.search(r'\btitle\s*=\s*rip_rg_(chr|uzh|pdl|prl|ods)_', body)
        owner = family[1].upper() if family else {'rip_rg.111': 'CHR', 'rip_rg.151': 'CHR', 'rip_rg.900': 'ODS'}[eid]
        return f'events/RIP_{owner}_RegionalGovernments.txt'
    if stem == 'RIP_FaithReformEvents':
        family = {'rip_stauropegion': 'HLC', 'rip_vetka': 'CHR', 'rip_kamianets': 'PDL', 'rip_sophia': 'PLT'}[ns]
    elif stem == 'NovgorodFlavorEvents':
        family = {'nov_flavor': 'NOV', 'mansur_flavor': 'shared_frontier', 'jagoldai_flavor': 'shared_frontier'}[ns]
    elif stem == 'RIP':
        family = {'ukr_flavor': 'shared_ruthenian', 'flavor_rus': 'MOS_RUS',
                  'zaz_flavor': 'ZAZ', 'euro_monarchy': 'shared_monarchy',
                  'princes_revolt': 'shared_ruthenian', 'kyiv_independence': 'KIE',
                  'harass_tatar': 'shared_steppe', 'ruth_instituties': 'shared_ruthenian',
                  'bs_flavor': 'shared_black_sea', 'sloboda_history': 'shared_sloboda'}[ns]
        if eid == 'ukr_flavor.2':
            family = 'NOV'
        elif eid == 'ukr_flavor.3':
            family = 'shared_frontier'  # OKA / RYA, not a Ruthenian tag gate.
    else:
        raise ValueError(f'Unclassified source: {stem}')
    return f'events/RIP_{family}_{ns}.txt'


def layout(source, text):
    stem = Path(source).stem
    if stem not in SPLIT:
        return {destination(stem): format_script(text)}
    groups = defaultdict(list)
    headers = []
    for key, body in statements(text):
        if key in ('country_event', 'province_event'):
            eid = event_id(body)
            groups[destination(stem, eid, body)].append(body)
        else:
            headers.append((key, body))
    result = {}
    for path, bodies in groups.items():
        namespaces = {event_id(b).split('.')[0] for b in bodies}
        preamble = []
        for key, body in headers:
            if key != 'namespace' or tokens(body)[2] in namespaces:
                preamble.append(body)
        result[path] = format_script('\n\n'.join(preamble + bodies))
    return result
