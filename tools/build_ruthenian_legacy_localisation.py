"""Localisation for the restored legacy missions; non-English files are fallbacks."""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
MISSIONS = {
    'ukr_kyiv_mohyla_academy': ('Kyiv Mohyla Academy', 'Bring the printing press to our realm and establish a flourishing centre of learning in Kyiv.'),
    'ukr_magdeburg_laws': ('Magdeburg Law', 'Support prosperous towns and secure the confidence of their burghers.'),
    'ukr_barocco': ('Ruthenian Baroque', 'Develop Kyiv and Chernihiv and build churches throughout the Dnieper towns.'),
    'ukr_kyiv_patriarchate': ('The Church of Kyiv', 'Strengthen the religious institutions of Kyiv and secure the support of the clergy.'),
    'ukr_second_jerusalem': ('A Second Jerusalem', 'Defend our faith and establish a cathedral and university in Kyiv.'),
    'ukr_restore_kyiv': ('Restore Kyiv', 'Unite the western Dnieper lands and restore the prosperity of Kyiv.'),
    'ukr_dnipro': ('Across the Dnieper', 'Secure and develop the lands along the eastern Dnieper.'),
    'ukr_chernihiv': ('The Chernihiv Lands', 'Unite Chernihiv, Novhorod-Siverskyi and Starodub under our rule.'),
    'ukr_ostrozkyi_princes': ('The Ostrozkyi Patrons', 'Support learning in the Volhynian lands around Ostroh and Rivne.'),
    'ukr_sweden_alliance': ('The Swedish Question', 'Resolve our relations with Sweden through alliance, rivalry or the disappearance of its crown.'),
    'ukr_take_smolensk': ('Secure Smolensk', 'Bring the Smolensk lands under our rule or that of our subjects.'),
    'ukr_defeat_muscowy': ('Break Muscovite Power', 'Control Moscow and the Oka lands, and end Muscovite or Russian rule over Novgorod.'),
    'ukr_podillya': ('The Podillian Lands', 'Secure the Podillian lands on our western frontier.'),
    'ukr_volyn': ('Unite Volhynia', 'Bring the Volhynian lands under our rule.'),
    'ukr_lviv': ('The City of Lviv', 'Secure Lviv and the lands of Red Ruthenia.'),
    'ukr_kingdom_of_ruthenia': ('The Ruthenian Crown', 'Gather the Ruthenian lands beneath a common crown.'),
    'ukr_visla': ('The Western Borderlands', 'Secure our claims towards the Vistula and across the Carpathian frontier.'),
    'ukr_crown_of_lithuania': ('The Lithuanian Inheritance', 'Bring the Lithuanian and Belarusian lands under our authority.'),
    'ukr_ruthenian_empire': ('A Ruthenian Empire', 'Complete our great enterprises and establish a stable and prestigious imperial state.'),
    'ukr_cossacks': ('The Cossack Frontier', 'Secure Zaporizhzhia and Ingil and organize the forces of the frontier.'),
    'ukr_age_of_heroic_campaigns': ('The Black Sea Campaigns', 'Establish our power along the Black Sea coast through conquest, occupation or raids.'),
    'ukr_sahaydachnyi_reforms': ('Reform the Cossack Host', 'Build an experienced army and establish capable military leadership.'),
    'ukr_crimea': ('Secure Crimea', 'Bring Crimea and the adjoining steppe lands under our rule.'),
    'ukr_dyke_pole': ('Settle the Wild Fields', 'Secure and settle Yedisan, Yedishkul and Kyzyl-Yar.'),
    'ukr_breadbasket_europe': ('The Granary of Europe', 'Develop grain production and become a major supplier to European markets.'),
    'ukr_moldavia': ('The Moldavian Connection', 'Bring Moldavia into our political and commercial sphere.'),
    'ukr_wallachia': ('Beyond the Danube', 'Extend our authority over Wallachia and the lower Danube.'),
    'ukr_sloboda_ukraine': ('Sloboda Ukraine', 'Secure the northeastern frontier and the lands around Rylsk.'),
    'ukr_legacy_of_chernihiv_princes': ('The Southern Inheritance', 'Extend our authority to the lower Don and the lands of Tmutorokan.'),
    'ukr_korsun': ('The Port of Korsun', 'Build docks and shipyards in the province of Theodoro.'),
    'ukr_black_sea_fleet': ('A Black Sea Fleet', 'Build a fleet capable of asserting our interests across the Black Sea.'),
    'ukr_take_tsarhorod': ('The Road to Tsarhorod', 'Secure Constantinople and its European approaches.'),
}

TEXT = {
    'ukr_magdeburg_laws_modifier': 'Magdeburg Law',
    'kyiv_patriarchate': 'The Church of Kyiv',
    'kyiv_second_jerusalem': 'Kyiv, a Second Jerusalem',
    'ukr_vkl': 'The Lithuanian Inheritance',
    'ruthenian_empire': 'Ruthenian Imperial Institutions',
    'ukr_age_of_heroic_campaigns_modifier': 'Black Sea Campaigns',
    'ukr_reformed_zaporozhian_cossacks_modifier': 'Reformed Cossack Host',
    'ukr_end_of_the_tatar_invasions': 'A Secure Steppe Frontier',
    'kryvbas': 'The Ironworks of Kryvbas',
    'ukr_moldavian_principality': 'Moldavian Trade',
    'korsun_port': 'The Port of Korsun',
    'ruthenian_swedish_alliance': 'Ruthenian-Swedish Cooperation',
    'ukrainian_grain': 'Ruthenian Grain Exports',
    'ukr_black_sea_cossack_raids': 'Black Sea ports held, occupied or raided',
    'flavor_ukr_legacy_of_rus.1.t': 'Our Banners at Tsarhorod',
    'flavor_ukr_legacy_of_rus.1.d': 'Our victory at Constantinople has transformed our standing among the powers of Europe. The city offers new opportunities for trade and diplomacy, alongside the burden of defending the straits.',
    'flavor_ukr_legacy_of_rus.1.a': 'Let our envoys announce the victory.',
    'flavor_ukr_legacy_of_rus.2.t': 'Muscovite Power Broken',
    'flavor_ukr_legacy_of_rus.2.d': 'With Moscow under our authority and Novgorod beyond Muscovite rule, the balance of power has shifted. Our court can now press its own claims to leadership among the lands of Rus.',
    'flavor_ukr_legacy_of_rus.2.a': 'A new settlement begins.',
    'flavor_ukr_legacy_of_rus.3.t': 'Kyiv Restored',
    'flavor_ukr_legacy_of_rus.3.d': 'The towns of the western Dnieper once again answer to a common authority. Rebuilding Kyiv has given our administrators a firm centre from which to govern these lands.',
    'flavor_ukr_legacy_of_rus.3.a': 'Put the new administration to work.',
    'flavor_ukr_legacy_of_rus.4.t': 'Learning in Volhynia',
    'flavor_ukr_legacy_of_rus.4.d': 'Patrons in the lands around Ostroh and Rivne have gathered scholars, teachers and printers. State support can turn their work into a lasting institution of learning.',
    'flavor_ukr_legacy_of_rus.4.a': 'Endow the school.',
}


def render(language):
    entries = dict(TEXT)
    for key, (title, description) in MISSIONS.items():
        entries[key + '_title'] = title
        entries[key + '_desc'] = description
    lines = [f'l_{language}:', ' # Generated by tools/build_ruthenian_legacy_localisation.py.']
    if language != 'english':
        lines.append(' # English fallback; translation has not yet been authored.')
    lines += [f' {key}:0 "{value}"' for key, value in sorted(entries.items())]
    return ('\ufeff' + '\n'.join(lines) + '\n').encode('utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for language in ('english', 'french', 'german', 'spanish'):
        path = ROOT / 'localisation' / f'Legacy_of_Rus_l_{language}.yml'
        expected = render(language)
        if not path.exists() or path.read_bytes() != expected:
            if args.check:
                stale.append(str(path.relative_to(ROOT)))
            else:
                path.write_bytes(expected)
    if stale:
        raise SystemExit('STALE: ' + ', '.join(stale))
    print('PASS: legacy mission localisation is current')


if __name__ == '__main__':
    main()
