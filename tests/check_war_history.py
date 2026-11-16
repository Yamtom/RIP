"""Structural and historical regression checks for RIP history/wars."""
from __future__ import annotations

from pathlib import Path
import sys

TESTS_DIR = Path(__file__).resolve().parent
TOOLS_DIR = TESTS_DIR.parent / 'tools'
for p in (str(TESTS_DIR), str(TOOLS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from audit_country_history import ROOT, read
from audit_diplomacy_history import date
from audit_war_history import analyze_war_text, inspect_wars
from clausewitz_testlib import vanilla_root


def test_planted_mutations():
    timelines = {
        280: ('HET', []),
        290: ('HET', []),
        2961: ('PLC', []),
    }
    cases = [
        (
            'non-ASCII byte',
            'name = "Bad"\nwar_goal = { type = take_claim casus_belli = cb_conquest province = 280 }\n'
            '1654.1.18 = { add_attacker = RUS add_defender = HET battle = { name = "X" location = 280 attacker = { commander = "K\xf6pr\xfcl\xfc" country = RUS } defender = { commander = "A" country = HET } result = yes } }\n'
            '1667.1.30 = { rem_attacker = RUS rem_defender = HET }\n',
            dict(timelines=None, require_ascii=True),
            'non-ASCII',
        ),
        (
            'LANDLESS_DFN',
            'name = "Ghost"\nwar_goal = { type = take_claim casus_belli = cb_conquest province = 290 }\n'
            '1651.2.20 = { add_attacker = PLC add_defender = SAV }\n'
            '1654.1.17 = { rem_attacker = PLC rem_defender = SAV }\n',
            dict(timelines=timelines),
            'LANDLESS_DFN:SAV',
        ),
        (
            'BOTH_SIDES',
            'name = "Swap"\nwar_goal = { type = take_claim casus_belli = cb_conquest province = 280 }\n'
            '1654.1.18 = { add_attacker = RUS add_defender = HET }\n'
            '1659.10.27 = { add_attacker = HET rem_defender = HET }\n'
            '1667.1.30 = { rem_attacker = RUS rem_attacker = HET }\n',
            dict(timelines=None),
            'BOTH_SIDES',
        ),
        (
            'UNCLOSED',
            'name = "Open"\nwar_goal = { type = take_claim casus_belli = cb_conquest province = 280 }\n'
            '1654.1.18 = { add_attacker = RUS add_defender = HET }\n'
            '1667.1.30 = { rem_attacker = RUS }\n',
            dict(timelines=None),
            'UNCLOSED',
        ),
        (
            'WG_NOT_DEFENDER',
            'name = "BadGoal"\nwar_goal = { type = take_claim casus_belli = cb_conquest province = 2961 }\n'
            '1651.2.20 = { add_attacker = PLC add_defender = HET }\n'
            '1654.1.17 = { rem_attacker = PLC rem_defender = HET }\n',
            dict(timelines=timelines),
            'WG_NOT_DEFENDER',
        ),
    ]
    for label, sample, kwargs, expected_fragment in cases:
        res = analyze_war_text(sample, filename=f'<{label}>', **kwargs)
        assert any(expected_fragment in f for f in res['findings']), (
            f'Mutation {label!r} missed {expected_fragment!r}: {res["findings"]}'
        )


def test_local_contracts():
    war_dir = ROOT / 'history/wars'
    files = sorted(war_dir.glob('*.txt'))
    assert len(files) == 25, f'Expected 25 RIP war files, got {len(files)}'

    parsed = {}
    for p in files:
        text = read(p)
        res = analyze_war_text(text, filename=p.name, require_ascii=True)
        assert not res['findings'], f'{p.name}: {res["findings"]}'
        parsed[p.name] = (text, res)

    # KhmelnytskyUprising: ZAZ + CRI start, HET enters on 1648.6.1, Zboriv peace before 1651
    khm_txt, khm = parsed['KhmelnytskyUprising.txt']
    assert khm['war_goal']['tag'] == 'ZAZ' and {'ZAZ', 'HET', 'CRI', 'PLC'} <= khm['tags']
    assert any(ds == '1648.6.1' and ('add_attacker', 'HET') in body for ds, _, body in khm['events'])
    assert all(b in khm_txt for b in ('"Korsun"', '"Pyliavtsi"', '"Zboriv"'))

    # PolishHetmanateWar: HET + ZAZ + CRI, wargoal 290 (Poltava), closed 1654.1.17
    _, ph = parsed['PolishHetmanateWar.txt']
    assert ph['war_goal']['province'] == '290'
    assert date(khm['events'][-1][0]) < date(ph['events'][0][0])
    assert ph['events'][0][0] == '1651.2.20' and ph['events'][-1][0] == '1654.1.17'
    assert {'PLC', 'HET', 'ZAZ', 'CRI'} <= ph['tags']

    # TheDeluge: HET & ZAZ join RUS; HET switches on Hadiach & 2nd Pereyaslav; Konotop & Chudnov
    deluge_txt, td = parsed['TheDeluge.txt']
    assert td['war_goal']['province'] == '276'
    assert {'RUS', 'HET', 'ZAZ', 'PLC'} <= td['tags']
    hadiach = next(body for ds, _, body in td['events'] if ds == '1658.9.16')
    assert hadiach.index(('rem_attacker', 'HET')) < hadiach.index(('add_defender', 'HET'))
    pereyaslav2 = next(body for ds, _, body in td['events'] if ds == '1659.10.27')
    assert pereyaslav2.index(('rem_defender', 'HET')) < pereyaslav2.index(('add_attacker', 'HET'))
    assert 'name = "Konotop"' in deluge_txt and 'location = 1945' in deluge_txt
    assert 'name = "Chudnov"' in deluge_txt and 'location = 1942' in deluge_txt

    # Three Cossackdoms in RussoTurkishWar & WarOfTheHolyLeague
    _, rtw = parsed['RussoTurkishWar.txt']
    assert rtw['war_goal']['province'] == '280'
    assert {'TUR', 'CRI', 'PDL', 'RUS', 'HET', 'ZAZ'} <= rtw['tags']
    ocw_txt, ocw = parsed['OttomanCommonwealthWar.txt']
    assert ocw['war_goal']['province'] == '2961' and 'location = 2961' in ocw_txt
    assert date(rtw['events'][0][0]) > date(ocw['events'][-1][0])

    whl_txt, whl = parsed['WarOfTheHolyLeague.txt']
    assert 'Mustafa Koprulu' in whl_txt and 'Kprl' not in whl_txt
    assert {'PDL', 'HET', 'ZAZ'} <= whl['tags']

    # GreatNordicWar: HET returns after Poltava (1709.7.9); ZAZ stays with SWE/TUR till Pruth (1711.7.21)
    gnw_txt, gnw = parsed['GreatNordicWar.txt']
    assert 'Carl Gustaf Rehnskiold' in gnw_txt and 'Olof Stromstierna' in gnw_txt
    rus_join = next(ds for ds, _, body in gnw['events'] if ('add_attacker', 'RUS') in body)
    assert date(rus_join) > date(whl['events'][-1][0])
    assert any(ds == '1709.7.9' and ('rem_defender', 'HET') in body and ('add_attacker', 'HET') in body
               for ds, _, body in gnw['events'])

    # Muscovite-Lithuanian, Ottoman, Danubian Sich, and repaired European vanilla wars
    _, fml = parsed['FirstMuscoviteLithuanianWar.txt']
    assert 'OKA' in fml['tags']
    _, sml = parsed['SecondMuscoviteLithuanianWar.txt']
    assert 'CHR' in sml['tags']
    tml_txt, tml = parsed['ThirdMuscoviteLithuanianWar.txt']
    assert tml['war_goal']['province'] == '289' and 'Mykhailo Glinsky' in tml_txt
    star_txt, star = parsed['FourthMuscoviteLithuanianWar.txt']
    assert star['war_goal']['province'] == '4244' and 'Andriy Nemyrovych' in star_txt
    kho_txt, kho = parsed['PolishOttomanWar1620.txt']
    assert kho['war_goal']['province'] == '281' and 'Petro Sahaidachnyi' in kho_txt
    assert 'ZAZ' in parsed['SmolenskWar.txt'][1]['tags']
    assert {'HET', 'ZAZ'} <= parsed['SecondRussuTurkishWar.txt'][1]['tags']
    assert parsed['SecondRussuTurkishWar.txt'][1]['war_goal']['province'] == '286'
    assert 'ZAZ' in parsed['FourthRussoTurkishWar.txt'][1]['tags']
    assert 'ZAZ' in parsed['FifthRussoTurkishWar.txt'][1]['tags']
    assert 'TEU' not in parsed['LivonianWar.txt'][1]['tags'] and 'PRU' in parsed['LivonianWar.txt'][1]['tags']
    pmw_txt, pmw = parsed['PolishMuscoviteWar.txt']
    assert 'TEU' not in pmw['tags'] and 'PRU' in pmw['tags'] and 'Stanislaw Zolkiewski' in pmw_txt
    assert parsed['SecondOttomanHungarianWar.txt.txt'][1]['war_goal']['province'] == '153'
    assert 'SAV' not in parsed['WarOfThePolishSuccession.txt'][1]['tags'] and 'SPI' in parsed['WarOfThePolishSuccession.txt'][1]['tags']
    assert 'HES' not in parsed['WarOfTheSixthCoalition.txt'][1]['tags']
    assert 'SIL' not in parsed['FrancoItalianWar.txt'][1]['tags']


def test_against_vanilla():
    v = vanilla_root()
    if v is None:
        donor_137 = ROOT / 'diagnostics/vanilla_donors/eu4_1.37.5'
        v = donor_137 if donor_137.is_dir() else None
    if v is None:
        print('WAR CHECK SKIPPED (vanilla EU4 1.37.5 not detected)')
        return
    result = inspect_wars(v)
    assert not result['local_findings'], f"Local war findings: {result['local_findings']}"
    assert not result['overlaps'], f"Ruthenian/steppe war overlaps: {result['overlaps']}"

    for name in sorted(result['local_results']):
        vp = v / 'history/wars' / name
        rp = ROOT / 'history/wars' / name
        if vp.exists():
            assert read(rp) != read(vp), f'{name}: identical to vanilla (remove pointless override)'


def main():
    test_planted_mutations()
    test_local_contracts()
    test_against_vanilla()
    print('WAR HISTORY CHECK PASS')


if __name__ == '__main__':
    main()
