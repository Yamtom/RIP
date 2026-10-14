# Clausewitz / EU4 semantic invariants

Read only for script-facing work.

## Scope and event chains

- Write down ROOT, FROM, PREV, and the current scope at every nested effect.
- Prefer explicit tag/province scopes inside reusable effects when callers may
  invoke them from different scopes.
- When country A calls an event for country B, verify what the recipient sees as
  FROM. Avoid ambiguous `random_province -> owner -> country_event` hops when a
  direct `random_country` selection can express the contract.
- Named event targets are global state. Do not save one in an event and consume
  it after a delayed follow-up where another country can overwrite it. Reselect
  locally in the delayed event or persist identity with an appropriate flag.
- `is_triggered_only = yes` is necessary for response events that must not fire
  autonomously. MTTH events need a reachable trigger and a valid selectable
  target.

## Trigger/selection symmetry

For every pair such as:

```text
any_neighbor_country -> random_neighbor_country
any_known_country    -> random_known_country
any_owned_province   -> random_owned_province
```

compare the complete filters: alliance, truce, subject relation, active CB,
ownership, geography, and protective modifiers. Ensure the random block cannot
be empty after the trigger passed.

## CB and claim semantics

- Inspect the supported vanilla `common/cb_types` definition before granting a
  CB by effect.
- Some CBs are prerequisite-driven rather than triggered grants. A `months`
  field cannot shorten a CB that naturally exists because of a core or claim.
- `cb_core` requires an actual core; `cb_support_rebels` requires the supported
  rebel relationship; PU CBs require valid union participants; generic tributary
  CBs may require Emperor-of-China conditions.
- A normal `add_claim` naturally enables the conquest CB for the claim lifetime.
  Use an exact claim when the disputed province matters more than an open-ended
  border-war target.
- Guard effect-granted CBs against an active copy, alliances, truces, invalid
  subjects, and missing/dead targets. Do not auto-declare war from flavour events
  unless the design explicitly requires and validates it.
- Subject-style CB rewards should have an explicit duration and mutually
  exclusive target selection. Clear the previous chain target when only one
  campaign CB should remain active.

## Cooldowns and one-shot state

A permanent flag with `NOT = { has_country_flag = recent }` never expires.
This reusable cooldown contract is valid:

```text
OR = {
  NOT = { has_country_flag = recent_action }
  had_country_flag = { flag = recent_action days = 1825 }
}
```

Setting the flag again refreshes its age. Do not invert the second branch with
`NOT had_country_flag`; that opens the action during the cooldown and closes it
after the window.

For one-shot events, consume every option with `fire_only_once`, a resolved
flag, or both when defensive compatibility with old saves matters.

## Province IDs and map data

- Resolve numeric IDs against the supported installation's
  `history/provinces`, `map/area.txt`, `map/region.txt`, and localisation.
- Comments and old documentation are not authoritative. A syntactically valid
  ID can still target another continent or a similarly named province.
- Check trigger, highlight, effect, mission, and documentation occurrences as a
  group. Fixing only the comment is not a gameplay fix.
- Record the supported game version and retest after map upgrades.

## Claims and pacing

- Count provinces affected by region/area scopes, including both branches of a
  reward.
- Distinguish normal claims, permanent claims, and helpers whose semantics vary
  by country state.
- Gate broad permanent rewards behind meaningful control of the target region.
- Make distant theatres temporary and mutually exclusive where simultaneous
  completion would create a burst.
- Inspect formation decisions and inherited mission slots together; tag changes
  can expose more than one tree.

## Modifiers, localisation, and overrides

- Confirm whether each modifier is country- or province-scoped at definition and
  every caller.
- Search globally before removing an apparently unused modifier, localisation
  key, helper, event, or flag.
- Check event title, description, every option, modifiers, custom localisation,
  and fallback/carry localisation.
- Identify exact-filename or full-file vanilla/DLC overrides. Diff them against
  the supported game version and document upgrade risk.
