import sys
sys.path.append('tests')
import os, glob, re
from collections import defaultdict
from clausewitz_testlib import read, named_block, matching_brace, normalized, ROOT

vanilla_root = r'D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV'
vanilla_reforms_path = os.path.join(vanilla_root, 'common', 'government_reforms')

# 1. Parse all mod reforms
reforms_dir = ROOT / "common/government_reforms"
mod_reforms = {}
for path in sorted(reforms_dir.glob("*.txt")):
    text = path.read_text(encoding="utf-8-sig")
    matches = re.finditer(r"(?m)^([A-Za-z0-9_]+)\s*=\s*\{", text)
    for m in matches:
        ref_id = m.group(1)
        block = named_block(text, ref_id)
        mod_reforms[ref_id] = {
            'file': path.name,
            'block': block,
            'path': path
        }

print(f"Total mod reforms loaded: {len(mod_reforms)}")

# 2. Parse 00_governments.txt to get tier and government form for each reform
gov_text = read("common/governments/00_governments.txt")
reform_tier_info = defaultdict(list)

for gov_type in ["monarchy", "republic", "theocracy", "tribal", "native"]:
    try:
        gov_block = named_block(gov_text, gov_type)
    except KeyError:
        continue
    
    basic_m = re.search(r"(?m)^\s*basic_reform\s*=\s*([A-Za-z0-9_]+)", gov_block)
    if basic_m:
        reform_tier_info[basic_m.group(1)].append((gov_type, "Tier 0 (Basic)"))
        
    try:
        levels_block = named_block(gov_block, "reform_levels")
    except KeyError:
        continue
    
    # Parse levels
    for level_match in re.finditer(r"(?m)^\s*([A-Za-z0-9_]+)\s*=\s*\{", levels_block):
        lvl_name = level_match.group(1)
        try:
            lvl_blk = named_block(levels_block, lvl_name)
            refs_m = re.search(r"reforms\s*=\s*\{([^}]+)\}", lvl_blk)
            if refs_m:
                for r in refs_m.group(1).split():
                    reform_tier_info[r].append((gov_type, lvl_name))
        except Exception:
            pass

# 3. Analyze saturation across tags and tiers
tag_tier_matrix = defaultdict(lambda: defaultdict(list))
regional_matrix = defaultdict(list)

for ref_id, data in mod_reforms.items():
    blk = data['block']
    f = data['file']
    tiers = reform_tier_info.get(ref_id, [("unknown", "unknown")])
    
    # Determine tag or scope
    pot = ""
    try:
        pot = named_block(blk, "potential")
    except KeyError:
        pass
    
    tags = re.findall(r"\btag\s*=\s*([A-Z0-9_]+)", pot)
    if not tags:
        # Check if it has specific origin triggers
        if "west_ukraine_hlc_origin_country" in pot or "hlc_has_poland_path" in pot or "hlc_has_austria_path" in pot:
            tags = ["HLC"]
        elif "west_ukraine_vln_origin_country" in pot or "vln_has_grand_ruthenia" in pot:
            tags = ["VLN"]
        elif "west_ukraine_pdl_origin_country" in pot or "pdl_frontier_reform_visible" in pot or "pdl_magnate_reforms_visible" in pot or "pdl_grand_reform_visible" in pot:
            tags = ["PDL"]
        elif "lit_ladder_visible" in pot or "lit_separate_crown_visible" in pot or "lit_union_of_two_nations_visible" in pot:
            tags = ["LIT"]
        elif "chr_siversk_principality_visible" in pot or "chr_desna_staple_visible" in pot or "chr_town_union_visible" in pot or "chr_rada_of_lands_visible" in pot or "chr_magistrat_rule_visible" in pot or "chr_prykaz_tsardom_visible" in pot or "chr_kanceliaryst_republic_visible" in pot or "chr_dzhura_corps_visible" in pot or "chr_many_nations_union_visible" in pot:
            tags = ["CHR"]
        elif "zaz_path_cantons_visible" in pot or "zaz_path_host_state_visible" in pot or "zaz_path_sacred_order_visible" in pot or "zaz_path_sacred_horde_visible" in pot or "zaz_lineage_country" in pot:
            tags = ["ZAZ"]
        elif "uzh_identity" in pot:
            tags = ["UZH"]
        elif "ruthenian_reform_visible" in pot or "ruthenian_principality_reform" in pot:
            tags = ["Ruthenian (Regional)"]
        else:
            tags = ["Global / Cossack"]
            
    for t in tags:
        for gov_type, lvl in tiers:
            tag_tier_matrix[t][f"{gov_type}:{lvl}"].append(ref_id)

print("\n=== REFORM SATURATION BY TAG AND TIER ===")
for t, lvl_map in sorted(tag_tier_matrix.items()):
    print(f"\n--- TAG / SCOPE: {t} (Total tiers with unique reforms: {len(lvl_map)}) ---")
    for lvl, refs in sorted(lvl_map.items()):
        print(f"  {lvl} ({len(refs)} reforms): {refs}")

# 4. Check for availability / potential issues
print("\n=== DETAILED ANALYSIS OF REFORM GATES & CONDITIONS ===")
issues = []
for ref_id, data in mod_reforms.items():
    blk = data['block']
    f = data['file']
    
    # Check potential vs trigger
    has_pot = "potential = {" in blk
    has_trig = "trigger = {" in blk
    
    if not has_pot:
        issues.append(f"{ref_id} ({f}): MISSING potential block!")
    
    # Check allow_normal_conversion
    allow_conv = re.search(r"allow_normal_conversion\s*=\s*([a-z]+)", blk)
    lock_lvl = re.search(r"lock_level_when_selected\s*=\s*([a-z]+)", blk)
    
    # Check if lock_level_when_selected is used with allow_normal_conversion = yes
    if lock_lvl and lock_lvl.group(1) == "yes" and allow_conv and allow_conv.group(1) == "yes":
        issues.append(f"{ref_id} ({f}): CONFLICT - lock_level_when_selected = yes but allow_normal_conversion = yes")
        
    # Check mechanics inside blk
    if "states_general_mechanic" in blk:
        sgm = named_block(blk, "states_general_mechanic")
        # check sub-keys
        sub_keys = re.findall(r"([A-Za-z0-9_]+)\s*=\s*\{", sgm)
        print(f"INFO: {ref_id} has states_general_mechanic with factions: {sub_keys}")

print(f"\nPotential/Trigger logic issues found: {len(issues)}")
for iss in issues:
    print("  *", iss)
