# HLC Sejm Reform Addition

## Summary
Added a fourth Galician government reform to the HLC (Halychyna) government archetype, expanding its reform suite to cover more government mechanics.

## Changes Made

### 1. Government Reform Definition
**File:** `common/government_reforms/RIP_government_reforms.txt`

Added new reform in the Deliberative Assembly tier:
```
hlc_galician_sejm_reform = {
    monarchy = yes
    duration = 20
    icon = 24
    has_patriarchs = yes
    is_part_of_assembly = yes
    legacy_government_mechanic = {
        name = "sejm"
        bonus = 0.1
    }
    
    modifier = {
        free_adm_policy = 1
        estates_loyalty_equilibrium = 0.05
        envoy_travel_time = -0.15
    }
    
    conditional = {
        allow = { tag = HLC }
        effect = {
            add_country_modifier = {
                name = galician_sejm_assembly
                duration = -1
            }
        }
    }
    
    ai_will_do = { factor = 0.8 }
}
```

### 2. Localization
**File:** `localisation/hlc_reforms_l_english.yml`

Added localization strings:
```yaml
hlc_galician_sejm_reform:0 "Galician Sejm Assembly"
hlc_galician_sejm_reform_desc:0 "Galician nobility convene in regional sejm, blending Polish deliberative traditions with Austrian administrative oversight."
```

### 3. Government Reform Tree Integration
**File:** `common/governments/00_governments.txt`

Added reform to the deliberative_assembly tier, allowing Galician rulers to adopt this reform alongside other deliberative assembly reforms.

## Reform Tiers Overview

The HLC government now covers reforms in these tiers:

1. **Religious Integration** (Tier 9 equivalent): `hlc_galician_voivodeship_reform`
2. **Confessional Affairs** (Tier 9 equivalent): `hlc_confessional_dualism_reform`
3. **Executive-Legislative Balance** (Tier 8 equivalent): `hlc_crown_and_sejm_reform`
4. **Deliberative Assembly** (Tier 5): `hlc_galician_sejm_reform`

## Reform Mechanics

The new Galician Sejm Assembly reform provides:
- +1 free administrative policy (enables Polish sejm-style governance)
- +0.05 estates loyalty equilibrium (better estate relations through assembly)
- -15% envoy travel time (enhanced diplomatic reach)

It also grants:
- Legacy sejm mechanic with 0.1 bonus
- A permanent country modifier for Galician sejm assembly

## Compatibility

This reform integrates seamlessly with:
- Existing HLC government reforms
- Polish sejm mechanics
- Austrian administrative systems
- Estate privileges and deliberative assembly systems
- Galician nationality and culture groups

The reform maintains historical authenticity by representing how Galician nobility adapted Polish sejm institutions within the Austrian administrative framework.
