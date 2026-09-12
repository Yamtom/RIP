"""Frozen church benchmark protocol and evidence-gated score calculation.

Preparation is not observation. No score is printed for unrun campaigns.
Each branch/entry-route/DLC/control-environment stratum needs all four scenarios.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, json, math, subprocess

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'diagnostics/church_redesign_20260911/campaign_protocol.json'
METRICS={
 'net_financial_position_delta': {'direction':1,'unit':'ducats'},
 'recovery_days_total': {'direction':-1,'unit':'days'},
 'net_monarch_points': {'direction':1,'unit':'ADM+DIP+MIL'},
 'integrated_development_years': {'direction':1,'unit':'development-years'},
 'rebel_occupied_development_months': {'direction':-1,'unit':'development-months'},
 'diplomatic_objectives_met': {'direction':1,'unit':'objectives out of 10'},
}
SCENARIOS={
 'homogeneous_peace': dict(scales=[2000,1800,1500,10000,12000,10], own_faith_share=1.0, war_offsets=[]),
 'mixed_frontier': dict(scales=[2500,1800,1500,10000,12000,10], own_faith_share=.5, war_offsets=[]),
 'military_expansion': dict(scales=[3000,3600,1500,10000,24000,10], own_faith_share=.8, war_offsets=[5,20,35]),
 'church_crisis': dict(scales=[2500,1800,1500,10000,24000,10], own_faith_share=.5, war_offsets=[]),
}
BRANCHES={
 'ro_recognized': dict(religion='russian_orthodox',control='orthodox',routes=['recognition_1600'],target='at_most_95'),
 'ro_schismatic': dict(religion='russian_orthodox',control='orthodox',routes=['refusal_1600'],target='at_most_95'),
 'gc_historical': dict(religion='greek_catholic',control='catholic',routes=['brest_1600','florence_1444'],target='102_to_108'),
 'gc_ecumenical': dict(religion='greek_catholic',control='catholic',routes=['brest_1600','florence_1444'],target='102_to_108'),
}
RULES={
 'version':'church-20260911-v1',
 'metric_weight':'1/6', 'scenario_weight':'1/4',
 'formula':'100 * (1 + mean(direction * (treatment - control) / max(abs(control), scenario_scale)))',
 'clipping':False,
 'no_universal_scenario_dominance':'at least one scenario index <= 100',
 'metrics':METRICS,'scenarios':SCENARIOS,'branches':BRANCHES,
 'treatment_costs':'All negotiation, entry, policy, privilege, conversion and crisis costs from the first day are included. No pre-granted recognition or ecumenism.',
 'religious_resources':'PA, Fervor, Communion and Standing are recorded separately; never counted as monarch points or cash.',
 'development_integration':'Daily sum of owned controlled full-core development in the state faith or a currently recognized rite, divided by 365.25. Orthodox/RO jurisdiction offsets alone do not count as provincial integration.',
 'finance':'Change in treasury minus outstanding principal debt; book all church payments and interest, and do not count new loans as income.',
 'points':'Cumulative ADM+DIP+MIL earned minus spent after identical frozen non-religious purchases; include unrecoverable entry and policy costs. Track each point type and cap wastage separately.',
 'stability':'Monthly sum of development occupied by rebels; negative direction. Keep rebellion count, fighting losses, unrest and suppression spending as supplementary raw measures.',
 'recovery':'At years +10,+25,+40 remove 10000 manpower in both arms after the monthly tick. Sum days to restore the pre-shock reserve, capped at 3650 per shock. Do not overlap the next shock. Combat, war and casualties follow the frozen scenario schedule.',
 'diplomacy':'Ten frozen partner-date objectives, two at each +10,+20,+30,+40,+50 checkpoint. One point requires alliance, opinion >=100 and neither side a subject or at war with the other. Freeze the five Orthodox and five Catholic partner-date entries before either arm runs.',
 'crisis':'At +10 set stability to 0 and break PAP relations until +20; at +20 occupy the union seat for two years, or the designated comparison parish if absent. Do not erase accumulated church fuel or pre-grant solutions.',
 'baseline_environments':'Report RIP-native and unmodified EU4 controls separately; do not pool them or DLC strata.',
 'source_limit':'This protocol is an agreed decision aid, not a universal measure of a religion.',
}

def protocol_hash():
    return hashlib.sha256(json.dumps(RULES,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def metric_scores(treatment,control,scenario):
    if set(treatment)!=set(METRICS) or set(control)!=set(METRICS): raise ValueError('Exactly six measurements are required.')
    output={}
    for (key,spec),scale in zip(METRICS.items(),SCENARIOS[scenario]['scales']):
        a,b=treatment[key],control[key]
        if isinstance(a,bool) or isinstance(b,bool) or not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or not math.isfinite(a) or not math.isfinite(b):
            raise ValueError('Unobserved or non-finite measurement: '+key)
        output[key]=100*(1+spec['direction']*(a-b)/max(abs(b),scale))
    return output

def score_stratum(rows):
    if len(rows)!=4 or {r['scenario'] for r in rows}!=set(SCENARIOS): raise ValueError('Four distinct scenarios are required.')
    first=rows[0]
    identity=lambda r:tuple(r[k] for k in ('branch','route','control_environment','dlc_profile','seed'))
    if any(identity(r)!=identity(first) for r in rows): raise ValueError('Mixed benchmark strata.')
    outcomes={}
    for row in rows:
        dimensions=metric_scores(row['treatment'],row['control'],row['scenario'])
        outcomes[row['scenario']]=dict(index=sum(dimensions.values())/6, dimensions=dimensions,
                                      treatment=row['treatment'],control=row['control'])
    score=sum(v['index'] for v in outcomes.values())/4
    numeric=score<=95 if first['branch'].startswith('ro_') else 102<=score<=108
    specialization=any(v['index']<=100+1e-9 for v in outcomes.values())
    return dict(branch=first['branch'],route=first['route'],control_environment=first['control_environment'],
                dlc_profile=first['dlc_profile'],index=score,scenarios=outcomes,
                numeric_target_met=numeric,no_universal_scenario_dominance=specialization,
                acceptance=numeric and specialization)

def source_manifest():
    hashes={}
    for folder in ('common','events','decisions','missions','interface','customizable_localization','localisation'):
        for path in sorted((ROOT/folder).rglob('*')):
            if path.is_file() and path.suffix in ('.txt','.gui','.gfx','.yml','.lua'):
                hashes[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    hashes['descriptor.mod']=hashlib.sha256((ROOT/'descriptor.mod').read_bytes()).hexdigest()
    return hashes

def prepare(destination=DEST):
    if destination.exists():
        old=json.loads(destination.read_text(encoding='utf-8'))
        if any(arm.get('observed') or any(v is not None for v in arm['measurements'].values()) for p in old['pairs'] for arm in p['arms']):
            raise ValueError('Refusing to overwrite recorded observations.')
    pairs=[]
    for branch,spec in BRANCHES.items():
        for route in spec['routes']:
            for scenario,setup in SCENARIOS.items():
                for environment in ('RIP','vanilla_1.37.5'):
                    for dlc in ('all_owned_enabled','Third_Rome_and_Cradle_disabled'):
                        start=1444 if route.startswith('florence') else 1600
                        key='_'.join((branch,route,scenario,environment,dlc))
                        arms=[dict(role=role,religion=faith,environment=env,observed=False,
                                   measurements={k:None for k in METRICS},supplementary_measurements={},
                                   artifacts=dict(initial_save=None,final_save=None,logs=None,monthly_ledger=None),
                                   branch_achieved=None,source_sha256=None)
                              for role,faith,env in [('treatment',spec['religion'],'RIP'),('control',spec['control'],environment)]]
                        pairs.append(dict(id=key,branch=branch,route=route,scenario=scenario,control_environment=environment,
                                          dlc_profile=dlc,seed=1001,start_date=f'{start}.01.01',end_date=f'{start+50}.01.01',
                                          checkpoint_years=[start+v for v in (0,10,20,30,40,50)],status='not_run',
                                          setup=dict(development=200,treasury=1000,adm=500,dip=500,mil=500,stability=2,
                                                     initial_religious_resources='zero in each arm; no free achieved branch or centre',
                                                     initial_state_faith_share=setup['own_faith_share'],
                                                     country_tag=None,province_ids=None,faith_by_province=None,
                                                     diplomacy_objectives=None,war_opponents=None,
                                                     frozen_nonreligious_purchases=None,
                                                     note='Freeze actual IDs, partners, saves and schedules before either arm. Florence treatment begins Orthodox and negotiates entry; do not start with a free union.'),
                                          arms=arms))
    record=dict(created_utc=datetime.now(timezone.utc).isoformat(),game_version='1.37.5',protocol_sha256=protocol_hash(),
                rules=RULES,git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_sha256=source_manifest(),pairs=pairs,
                observed_campaigns=0,limitation='Prepared protocols only. Null is unknown; no balance verdict exists until dated campaigns and raw ledgers are attached.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Prepared {len(pairs)} pairs, {len(pairs)*2} unobserved arms; no balance scores. {destination}')

def evaluate(path):
    data=json.loads(path.read_text(encoding='utf-8'))
    if data['protocol_sha256']!=protocol_hash() or data['rules']!=RULES: raise ValueError('The frozen protocol was changed.')
    expected={(branch,route,scenario,env,dlc,1001) for branch,spec in BRANCHES.items() for route in spec['routes']
              for scenario in SCENARIOS for env in ('RIP','vanilla_1.37.5')
              for dlc in ('all_owned_enabled','Third_Rome_and_Cradle_disabled')}
    actual=[tuple(p[k] for k in ('branch','route','scenario','control_environment','dlc_profile','seed')) for p in data['pairs']]
    if set(actual)!=expected or len(actual)!=len(expected): raise ValueError('Incomplete or duplicated branch/route/DLC/control coverage.')
    groups={}
    for pair in data['pairs']:
        if pair['status']!='completed': raise ValueError('Campaign not completed: '+pair['id'])
        setup=pair['setup']
        if not all(setup.get(k) is not None for k in ('country_tag','province_ids','faith_by_province','diplomacy_objectives','war_opponents','frozen_nonreligious_purchases')):
            raise ValueError('Initial setup is not frozen: '+pair['id'])
        if len(setup['diplomacy_objectives'])!=10: raise ValueError('Ten frozen diplomacy objectives are required.')
        row={k:pair[k] for k in ('branch','route','scenario','control_environment','dlc_profile','seed')}
        if len(pair['arms'])!=2 or {a['role'] for a in pair['arms']}!={'treatment','control'}: raise ValueError('A paired treatment and control are required.')
        for arm in pair['arms']:
            if not arm['observed'] or arm['source_sha256'] is None: raise ValueError('Missing observation or source identity.')
            if arm['role']=='treatment' and arm.get('branch_achieved') is not True: raise ValueError('The requested branch was not achieved within the measured window.')
            for artifact in arm['artifacts'].values():
                if not artifact or not (path.parent/artifact).is_file(): raise ValueError('Missing campaign artifact: '+str(artifact))
            row[arm['role']]=arm['measurements']
        key=tuple(row[k] for k in ('branch','route','control_environment','dlc_profile','seed'))
        groups.setdefault(key,[]).append(row)
    return [score_stratum(rows) for rows in groups.values()]

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare',action='store_true'); mode.add_argument('--evaluate',type=Path)
    args=ap.parse_args()
    try:
        if args.prepare: prepare()
        else: print(json.dumps(evaluate(args.evaluate),ensure_ascii=False,indent=2))
    except ValueError as error: raise SystemExit(str(error))
