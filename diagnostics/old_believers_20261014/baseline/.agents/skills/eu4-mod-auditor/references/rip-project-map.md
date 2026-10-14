# RIP project map

Use this reference only inside the Ruthenian Improvement Project repository.
Treat it as routing information, not proof of current completion.

## Design sources

- `docs/GAME_DESIGN_DOCUMENT.uk.md`: project-level limits and milestones.
- `docs/STEPPE_RAIDING_SYSTEM.md`: steppe/Don/Circassian/Ottoman/Kaffa contract.
- `docs/BORDER_PRINCIPALITIES_SYSTEM.md`: Border and Qasim contract.
- `docs/RUSSIAN_ORTHODOX_IMPLEMENTATION.md` and
  `docs/RUSSIAN_ORTHODOX_QUICKREF.md`: Orthodox behavior; compare both to code.
- `docs/WORKSHOP_LISTING.md`: release notes and known triage; it can become stale.

Read only the named/relevant documents completely. Do not infer completion from
the GDD checkboxes.

## Static infrastructure

- `tests/clausewitz_testlib.py`: small brace-aware source helpers.
- `tests/check_clausewitz_braces.py`: braces and BOM.
- `tests/check_script_layer.py`: IDs, namespaces, localisation, modifier scope,
  province-comment checks, and unused-modifier warnings.
- `tests/check_glossary.py`: terminology/localisation glossary.
- `tests/check_claim_pacing.py`: KIE/KRU, Russia, and distant claim contracts.
- `tests/check_subject_cb_limits.py`: subject-CB duration/guards/exclusivity.
- `tests/check_steppe_expansions.py`: Don/Circassian/Ottoman/Kaffa contracts.
- `tests/check_border_principalities.py`: Border/Qasim contracts.

Run focused tests first, then the global layer. Preserve and report baseline
global failures rather than expanding scope to unrelated systems.

## Runtime infrastructure

- `tests/observer/run_observer.ps1`: isolated observer/smoke harness.
- `tests/observer/README.md`: supported parameters and artifact contract.
- `tests/observer/commands/`: startup and dated checkpoint commands.

Inspect the harness before running it. Use a temporary userdir and collect the
manifest plus `game.log`, `error.log`, `setup.log`, `text.log`, crash count, and
exit status.

The supported local vanilla installation has historically been under:

`D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV`

Verify that path and game version each time rather than assuming it still exists.

## High-risk RIP patterns

- KIE/KRU/UKR may inherit several mission slots after tag changes; audit the
  combined route, not one file block.
- Russia's Domination mission file and formation decisions can shadow vanilla or
  DLC content. Diff full-file overrides on every supported-version upgrade.
- `add_russian_claim` semantics can depend on country modifiers; inspect the
  inherited scripted effect before counting permanent claims.
- Subject CBs historically used invalid generic tributary/core/PU types or
  refreshed several targets. Validate vanilla prerequisites and target count.
- Raid chains historically contained scope reversal, impossible month ANDs,
  mismatched `any_*`/`random_*` filters, permanent cooldown flags, and wrong
  province IDs. Apply the semantic reference before tuning numbers.
- Localisation collisions and parser errors need A/B evidence. A warning present
  in both a passing and failing run is not automatically the crash cause.

## Completion standard

For a named system to be “fully implemented,” require:

- reachable entry and bounded target selection;
- valid scope and engine semantics;
- complete English localisation;
- focused regression coverage;
- documentation matching live behavior;
- at least an EU4 startup/parser smoke for parser-sensitive edits;
- higher runtime evidence only when the claim includes AI balance, branches,
  observer runs, manual campaigns, or save/load.
