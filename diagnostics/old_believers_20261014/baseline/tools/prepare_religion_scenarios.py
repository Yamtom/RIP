"""Prepare paired 1600-1650 measurement manifests; never invent observations."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'diagnostics/religion_settlement_20260911/scenarios.json'
SCENARIOS = {
    'homogeneous_peace': {
        'description_uk': 'Однорідна держава в мирі; однакові будівництво, торгівля й витрати на установи.',
        'state_faith_development_share': 1.0,
        'war_schedule': [],
        'stress': [],
    },
    'mixed_frontier': {
        'description_uk': 'Змішане прикордоння; половина розвитку іншої віри; звичайні місіонери й центри обліковуються окремо.',
        'state_faith_development_share': 0.5,
        'war_schedule': [],
        'stress': ['same_missionary_budget', 'record_exact_minority_faiths'],
    },
    'military_expansion': {
        'description_uk': 'Однакові противники, початкові армії й мирні угоди; облік втрат і відновлення.',
        'state_faith_development_share': 0.8,
        'war_schedule': [1605, 1620, 1635],
        'stress': ['same_newly_conquered_development', 'record_cb_availability_and_cost'],
    },
    'church_crisis': {
        'description_uk': 'Криза єдності й духовенства; однаковий зовнішній тиск, власні церковні наслідки кожної віри.',
        'state_faith_development_share': 0.5,
        'war_schedule': [],
        'stress': ['stability_zero_1610', 'papal_relations_broken_1610_1620', 'see_lost_1620', 'record_rebels_and_concessions'],
    },
}
METRICS = (
    'gross_income_ducats', 'recurring_expenses_ducats', 'church_payments_ducats',
    'net_income_ducats', 'loans_received_ducats', 'principal_repaid_ducats',
    'manpower_gained', 'manpower_spent', 'army_losses', 'recovery_months',
    'adm_spent', 'dip_spent', 'mil_spent', 'adm_granted', 'dip_granted', 'mil_granted',
    'religious_resource_spent', 'converted_development_missionaries',
    'converted_development_centers', 'initial_hierarchy_development',
    'missionary_months', 'rebel_regiments', 'rebel_occupied_months',
    'rebellions', 'diplomatic_opportunities', 'religion_specific_events',
)


def main():
    if DEST.exists():
        existing = json.loads(DEST.read_text(encoding='utf-8'))
        if any(arm.get('observed') for pair in existing['pairs'] for arm in pair['arms']):
            raise SystemExit('Refusing to overwrite recorded observations.')
    hashes = {}
    for folder in ('common', 'events', 'decisions', 'missions', 'localisation'):
        for path in sorted((ROOT / folder).rglob('*')):
            if path.is_file() and path.suffix in ('.txt', '.yml', '.lua'):
                hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    pairs = []
    for new, baseline, target in (('russian_orthodox', 'orthodox', '<=95%'), ('greek_catholic', 'catholic', '~105%')):
        for scenario, recipe in SCENARIOS.items():
            for environment in ('RIP', 'vanilla_1.37.5'):
                for third_rome in (True, False):
                    pair_id = f'{new}_{scenario}_{environment}_third_rome_{int(third_rome)}'
                    arms = []
                    for faith, mod in ((new, 'RIP'), (baseline, environment)):
                        arms.append(dict(religion=faith, environment=mod, observed=False,
                                         initial_save=None, final_save=None, logs=None,
                                         setup_province_ids=None, setup_faith_by_province=None,
                                         setup_country_tag=None, checkpoints=[],
                                         measurements={key: None for key in METRICS}))
                    pairs.append(dict(id=pair_id, scenario=scenario, recipe=recipe,
                                      third_rome=third_rome, seed=1001,
                                      start_date='1600.01.01', end_date='1650.01.01',
                                      checkpoint_years=[1600, 1610, 1620, 1630, 1640, 1650],
                                      common_setup=dict(development=200, treasury=1000,
                                          adm_power=500, dip_power=500, mil_power=500,
                                          stability=1, prestige=25,
                                          institutions='identical', technologies='identical',
                                          ruler='identical', armies='identical',
                                          national_missions_and_privileges='identical_within_RIP'),
                                      balancing_target=target, total_effectiveness=None,
                                      status='not_run', arms=arms))
    manifest = dict(created_utc=datetime.now(timezone.utc).isoformat(), game_version='1.37.5',
                    git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    source_sha256=hashes, pairs=pairs,
                    limitation='Preparation only. Null is unobserved, not zero. No effectiveness score is computed without measured campaigns and agreed metric weights.')
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared {len(pairs)} paired protocols ({len(pairs) * 2} arms), zero observed campaigns: {DEST}')


if __name__ == '__main__':
    main()
