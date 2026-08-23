---
name: eu4-mod-auditor
description: Audit, repair, and verify Europa Universalis IV Clausewitz mods: events, missions, decisions, CBs, claims, scopes, province IDs, localisation, documentation, and runtime evidence. Use for EU4 mod completeness, balance, regression, or implementation work; do not use for ordinary gameplay advice.
metadata:
  short-description: Audit and harden EU4 mods
---

# EU4 Mod Auditor

Produce an evidence-backed result: a read-only diagnosis when asked to audit,
or a minimal verified patch when asked to finish, repair, or clean a system.

## Start from evidence

1. Locate the mod root, supported EU4 version, vanilla/DLC install, and any
   repository instructions.
2. Read each user-named specification completely. Treat a checked box or prose
   claim as a requirement, not proof.
3. Inspect `git status --short` and the relevant diff before editing. Preserve
   user changes and unrelated work.
4. Build a compact requirement matrix: requirement, live entry point, evidence,
   defect, intended patch, static test, and runtime evidence.

For this RIP repository, read [references/rip-project-map.md](references/rip-project-map.md)
only when its named files or systems are in scope.

## Audit Clausewitz semantics before balance

Read [references/clausewitz-semantics.md](references/clausewitz-semantics.md)
when the task touches events, effects, scopes, CBs, flags, claims, province IDs,
or modifiers. Confirm static trigger/scope reachability before judging numbers
or flavour, and reserve runtime claims for observed evidence.

Trace every system as a graph:

```text
entry trigger -> target selection -> event/effect scope -> option -> cooldown
              -> follow-up event -> localisation -> documented outcome
```

Check trigger and random-selection filters for symmetry. A valid `any_*` trigger
does not make an unfiltered `random_*` effect safe.

## Implement within the requested authority

- For an audit or diagnosis, report findings without changing gameplay files.
- For a strict read-only audit, prefer commands that cannot create artifacts;
  invoke Python checks with `python -B` and compare final `git status --short`
  with the baseline.
- For a requested fix, patch the smallest coherent unit, including callers,
  localisation, focused regression tests, and documentation that would otherwise
  become false.
- Reuse a namespaced scripted trigger/effect when several callers need the same
  scope contract. Do not copy a fragile inline effect across event files.
- Prefer exact normal claims or a valid bounded CB over prerequisite-driven or
  semantically invalid CB grants. Never force a war merely to preserve old text.
- Keep simultaneous subject-CB targets and long-range claim bursts bounded.
- Remove confirmed dead scaffolding only after a repository-wide usage search.

Use `apply_patch` for text edits. Do not rewrite unrelated dirty files.

## Verify in layers

Read [references/verification-playbook.md](references/verification-playbook.md)
before writing tests, launching EU4, or declaring completion.

Always distinguish these evidence levels:

1. source contract and diff review;
2. static parser/regression tests;
3. EU4 startup/parser smoke;
4. targeted branch execution;
5. observer/manual campaign evidence.

Passing a lower layer does not prove a higher one. Label trigger/scope analysis
as **statically reachable** or **source-reachable**. Claim **runtime-observed
reachability**, observer runs, manual campaigns, AI balance, or save/load
persistence only when dated artifacts demonstrate it.

## Keep documentation honest

- Describe live IDs, durations, scopes, files, and gameplay abstractions.
- Separate historical source claims from designer-created costs, MTTH, AI
  weights, and modifiers.
- Move implemented features out of future-work lists.
- Mark static, startup, branch, observer, and save/load checks independently.
- Note full-file vanilla/DLC overrides and version-sensitive map assumptions.

## Handoff

Lead with the outcome, then list material changes, tests and their exact status,
known pre-existing failures, runtime evidence, and remaining risk. A global test
suite with unrelated baseline failures is not "green"; report the focused pass
and the baseline delta precisely.
