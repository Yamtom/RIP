# Verification playbook

Read before testing or claiming completion.

## 1. Establish a baseline

- Capture `git status --short` and relevant tests before editing.
- Record pre-existing failures. Re-run the same commands after the patch and
  compare the delta.
- If `python` is a WindowsApps stub or otherwise unusable, locate a real
  interpreter; do not report tests as passed from a lexical approximation.

## 2. Focused static contracts

Prefer small dependency-free regression tests for the exact defect. In a repo
with `tests/clausewitz_testlib.py`, reuse its brace-aware `named_block` and
`keyed_blocks` helpers.

When extracting an event, do not accept the first nested
`country_event = { id = ... }` caller. Select the full definition by ID plus a
top-level property such as `title`, or choose the complete candidate.

Useful assertions include:

- all required event IDs exist exactly once;
- response events are triggered-only and have a live caller;
- trigger and random filters are aligned;
- CB type, target, guard, duration, and exclusivity are bounded;
- no stale wrong province IDs remain in the relevant block;
- helpers resolve their intended scope internally;
- every timed/one-shot option consumes its state;
- localisation keys exist and are unique;
- documentation no longer advertises old behavior.

Also run the repo's brace/BOM, localisation, glossary, and script-layer checks.
If the global script-layer check still has unrelated failures, report the count
and show that in-scope failures went to zero.

## 3. Static review beyond tests

- Run `git diff --check`.
- Review the entire relevant diff, not only changed lines found by a test.
- Search all callers and definitions of new helpers/modifiers/flags.
- Check file encoding rules, especially localisation BOM requirements.
- Compare version-sensitive vanilla/DLC definitions from the installed game.

## 4. Isolated EU4 startup smoke

Before launching:

- check whether EU4 is already running and do not interfere with an unrelated
  process;
- use a temporary user directory and a descriptor that enables only the mod
  under test;
- keep source files immutable during the run;
- record exact executable, arguments, game/mod versions, start/end time, userdir,
  and source revision/diff state.

A startup pass requires evidence such as:

- zero new crash bundle or a clean exit;
- `setup.log` passes the relevant initialization stage;
- `game.log` reaches `Launching SINGLEPLAYER-game` and a 1444 start;
- the complete new `error.log` has no new in-scope parser/scope errors.

An empty `text.log` or a generic warning does not identify a crash cause. Use
A/B isolation only with identical source snapshots and manifests.

## 5. Higher evidence levels

Startup does not prove option effects. For branch tests, record the event fired,
chosen option, before/after state, and resulting logs/save.

Observer and manual campaign claims require dated run manifests and artifacts:

- seed/setup and mod checksum;
- start/end dates and exit status;
- checkpoints/saves;
- key balance metrics;
- crash and error logs;
- a written verdict for each run.

Old saves that predate the patch do not validate the patch. A load smoke is not
an observer run, and an observer run is not a representative manual campaign.

## 6. Documentation and final verdict

Use independent checkboxes for static, startup, targeted branches, observer,
manual campaign, and save/load results. Mark only evidenced layers complete.

The final handoff should contain:

- what is now true;
- files materially changed;
- exact test commands and outcomes;
- pre-existing failures left untouched;
- runtime artifact path, if any;
- residual risks and the next evidence-producing step.
