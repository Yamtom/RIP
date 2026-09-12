"""Bounded source interpreter for church state tests; never an EU4 emulator.

Unknown instructions fail. Native rendering, AI scheduling and conversion speed
are outside this model. Network fixtures supply explicit adjacency and trade nodes.
"""
from copy import deepcopy
import re
from check_religion_settlement import World as SettlementWorld, parse, TRIGGERS, EFFECTS
from clausewitz_testlib import ROOT, read

for directory, registry in [('scripted_triggers', TRIGGERS), ('scripted_effects', EFFECTS)]:
    for path in (ROOT / 'common' / directory).glob('rip_church_*.txt'):
        registry.update(parse(path.read_text(encoding='utf-8-sig')))
for name in ['rip_uc_curia_effects', 'rip_faith_effects', 'rip_ro_icon_effects']:
    EFFECTS.update(parse(read('common/scripted_effects/' + name + '.txt')))


class World(SettlementWorld):
    def __init__(self):
        super().__init__()
        self.targets = {}
        self.from_scope = None

    def country(self, tag, religion='orthodox'):
        c = super().country(tag, religion)
        c.update(annual_income=120, opinions={}, government='monarchy', ai=False)
        return c

    def province(self, number, owner, religion='orthodox'):
        p = super().province(number, owner, religion)
        p.update(variables={}, area='a', neighbors=set(), buildings={'temple'},
                 culture='ruthenian', culture_group='east_slavic', has_missionary=False,
                 node='node', traders=set(), shares={})
        return p

    def ref(self, key, scope, root, prev):
        if key.startswith('event_target:'): return self.targets.get(key.split(':', 1)[1])
        if key == 'FROM': return self.from_scope
        return super().ref(key, scope, root, prev)

    def flag(self, value, scope, root, prev):
        if '@' not in value: return value
        name, reference = value.split('@', 1)
        return name + '@' + self.ref(reference, scope, root, prev)['id']

    def collection(self, key, scope):
        if 'neighbor_province' in key:
            return [self.provinces[n] for n in sorted(scope['neighbors'])]
        if 'trade_node_member_province' in key:
            return [p for p in self.provinces.values() if p['node'] == scope['node']]
        if key == 'area': return [p for p in self.provinces.values() if p['area'] == scope['area']]
        return super().collection(key, scope)

    def variable_operands(self, value, scope):
        keys = [v for k, v in value if k == 'which']
        if len(keys) == 2: return keys[0], scope['variables'].get(keys[1], 0)
        raw = dict(value)['value']
        assert re.fullmatch(r'-?\d+(?:\.\d+)?', raw), 'Variable operands require two which fields: ' + str(value)
        return keys[0], float(raw)

    def gate(self, items, scope, root=None, prev=None):
        root = root or scope
        chain = False
        for key, value in items:
            if key in ('if', 'else_if', 'else'):
                if key == 'if': chain = False
                if not chain and (key == 'else' or self.gate(dict(value)['limit'], scope, root, prev)):
                    chain = True
                    if not self.gate([(k,v) for k,v in value if k != 'limit'], scope, root, prev): return False
            elif not self.condition(key, value, scope, root, prev): return False
        return True

    def condition(self, key, value, scope, root, prev):
        if key == 'check_variable':
            name, operand = self.variable_operands(value, scope)
            return scope['variables'].get(name, 0) + 1e-9 >= operand
        if key in ('has_country_flag', 'has_province_flag'):
            return self.flag(value, scope, root, prev) in scope['flags']
        if key in ('had_country_flag', 'had_province_flag'):
            fields = dict(value); flag = self.flag(fields['flag'], scope, root, prev)
            return flag in scope['flags'] and self.day - scope['flags'][flag] >= int(fields['days'])
        if key == 'variable_arithmetic_trigger':
            saved = deepcopy(scope['variables'])
            result = True
            for k,v in value:
                if k == 'export_to_variable': self.execute([(k,v)], scope, root, prev)
                elif k != 'custom_tooltip': result &= self.condition(k,v,scope,root,prev)
            scope['variables'] = saved
            return result
        if isinstance(value, list) and (key.isdigit() or key in ('FROM',) or key.startswith('event_target:')):
            ref = self.ref(key, scope, root, prev)
            return ref is not None and self.gate(value, ref, root, scope)
        if key in ('owned_by', 'controlled_by', 'is_core', 'tag'):
            field = {'owned_by':'owner','controlled_by':'controlled_by','is_core':'core','tag':'id'}[key]
            ref = self.ref(value, scope, root, prev)
            return scope[field] == (ref['id'] if ref else value)
        if key in ('area', 'culture', 'culture_group'):
            ref = self.ref(value, scope, root, prev)
            return scope[key] == (ref[key] if ref else value)
        if key == 'has_building': return value in scope['buildings']
        if key == 'has_trader': return self.ref(value,scope,root,prev)['id'] in scope['traders']
        if key == 'trade_share':
            fields=dict(value)
            return scope['shares'].get(self.ref(fields['country'],scope,root,prev)['id'],0) >= float(fields['share'])
        if key == 'has_opinion':
            fields=dict(value); ref=self.ref(fields['who'],scope,root,prev)
            return scope['opinions'].get(ref['id'] if ref else fields['who'],0) >= float(fields['value'])
        if key == 'years_of_income': return scope['treasury'] >= scope['annual_income'] * float(value)
        if key == 'government': return scope['government'] == value
        if key == 'province_id': return scope['id'] == value
        if key == 'num_of_owned_provinces_with':
            fields=dict(value)
            return sum(self.gate([(k,v) for k,v in value if k!='value'],p,root,scope) for p in self.collection('any_owned_province',scope)) >= float(fields['value'])
        if key == 'is_religion_enabled': return self.year >= 1596 or value in getattr(self,'enabled',set())
        return super().condition(key,value,scope,root,prev)

    def execute(self, items, scope, root=None, prev=None):
        root = root or scope
        i=0
        while i < len(items):
            key,value=items[i]; i+=1
            if key == 'if':
                group=[(key,value)]
                while i < len(items) and items[i][0] in ('else_if','else'):
                    group.append(items[i]); i+=1
                super().execute(group,scope,root,prev)
            elif key in EFFECTS and isinstance(value,list):
                params=dict(value)
                def substitute(nodes):
                    def sub(s): return re.sub(r'\$(\w+)\$',lambda m:params[m[1]],s)
                    return [(sub(k),substitute(v) if isinstance(v,list) else sub(v)) for k,v in nodes]
                self.execute(substitute(EFFECTS[key]),scope,root,prev)
            elif key in ('set_variable','change_variable','subtract_variable','multiply_variable','divide_variable'):
                name,number=self.variable_operands(value,scope); old=scope['variables'].get(name,0)
                scope['variables'][name] = number if key=='set_variable' else old+number if key=='change_variable' else old-number if key=='subtract_variable' else old*number if key=='multiply_variable' else old/number
            elif key == 'export_to_variable':
                fields=dict(value); source=self.ref(fields['who'],scope,root,prev) if 'who' in fields else scope
                scope['variables'][fields['which']]=source[fields['value'].removeprefix('trigger_value:')]
            elif key == 'while':
                fields=dict(value); count=0
                while self.gate(fields['limit'],scope,root,prev):
                    self.execute([(k,v) for k,v in value if k!='limit'],scope,root,prev)
                    count+=1
                    assert count < 10000, 'Nonterminating source loop'
            elif key in ('set_country_flag','clr_country_flag','set_province_flag','clr_province_flag'):
                flag=self.flag(value,scope,root,prev)
                if key.startswith('set'): scope['flags'][flag]=self.day
                else: scope['flags'].pop(flag,None)
            elif key in ('save_global_event_target_as','save_event_target_as'): self.targets[value]=scope
            elif key == 'clear_global_event_target': self.targets.pop(value,None)
            elif key == 'area':
                fields=dict(value)
                for p in self.collection(key,scope):
                    if self.gate(fields.get('limit',[]),p,root,scope): self.execute([(k,v) for k,v in value if k!='limit'],p,root,scope)
            elif key.isdigit() or key in ('FROM',) or key.startswith('event_target:'):
                ref=self.ref(key,scope,root,prev)
                if ref: self.execute(value,ref,root,scope)
            elif key == 'add_years_of_income': scope['treasury'] += float(value) * scope['annual_income']
            elif key in ('add_opinion','remove_opinion'):
                fields=dict(value); ref=self.ref(fields['who'],scope,root,prev)
                pair=(ref['id'],fields['modifier'])
                if key=='add_opinion': scope.setdefault('opinion_modifiers',set()).add(pair)
                else: scope.setdefault('opinion_modifiers',set()).discard(pair)
            elif key == 'enable_religion': self.enabled=getattr(self,'enabled',set())|{value}
            elif key in ('hidden_effect','custom_tooltip'):
                if isinstance(value,list): self.execute(value,scope,root,prev)
            elif key == 'add_patriarch_authority': scope[key[4:]]=min(1,max(0,scope[key[4:]]+float(value)))
            else: super().execute([(key,value)],scope,root,prev)

    def run(self,name,scope,from_scope=None,**params):
        self.from_scope=from_scope
        super().run(name,scope,**params)


def fixture(religion='russian_orthodox'):
    w=World(); c=w.country('MOS',religion); p=w.province(295,c,religion)
    pope=w.country('PAP','catholic'); pope['opinions']['MOS']=100
    return w,c,p
