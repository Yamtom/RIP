"""Synthetic arithmetic tests, never campaign observations."""
from copy import deepcopy
import importlib.util
import math
from clausewitz_testlib import ROOT

spec=importlib.util.spec_from_file_location('church_balance_protocol',ROOT/'tools/church_balance_protocol.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
zeros={k:0 for k in module.METRICS}
assert set(module.metric_scores(zeros,zeros,'homogeneous_peace').values())=={100}
for bad in (None,float('nan'),float('inf'),True):
    invalid=dict(zeros); invalid['net_monarch_points']=bad
    try: module.metric_scores(invalid,zeros,'homogeneous_peace')
    except ValueError: pass
    else: raise AssertionError('Unobserved/nonfinite input was accepted.')
rows=[dict(branch='gc_historical',route='brest_1600',control_environment='RIP',dlc_profile='all_owned_enabled',seed=1001,
           scenario=s,treatment=dict(zeros),control=dict(zeros)) for s in module.SCENARIOS]
assert module.score_stratum(rows)['index']==100
# A 12% improvement in one of six dimensions contributes exactly two index points.
rows[0]['treatment']['net_financial_position_delta']=240
assert module.score_stratum(rows)['index']==100.5
assert module.metric_scores(dict(zeros,recovery_days_total=180),zeros,'homogeneous_peace')['recovery_days_total']==90
assert module.metric_scores(dict(zeros,net_financial_position_delta=-2100),dict(zeros,net_financial_position_delta=-2000),'homogeneous_peace')['net_financial_position_delta']==95
try: module.score_stratum(rows[:3])
except ValueError: pass
else: raise AssertionError('Partial four-scenario bundle accepted.')
mixed=deepcopy(rows); mixed[0]['dlc_profile']='other'
try: module.score_stratum(mixed)
except ValueError: pass
else: raise AssertionError('Mixed strata accepted.')
print('CHURCH BALANCE PROTOCOL PASS: frozen weights, zero/negative controls, direction, invalid inputs and scenario coverage; synthetic data only.')
