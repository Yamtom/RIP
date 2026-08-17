# RIP observer-run harness

This directory contains a reproducible, opt-in harness for the balance runs
required by Milestone 3. It does **not** claim that any run has happened. The
authoritative status and result tables live in
[`docs/BALANCE_PLAYTEST_REPORT.md`](../../docs/BALANCE_PLAYTEST_REPORT.md).

## Safety model

- `run_observer.ps1` is a dry run unless `-Launch` is supplied.
- Output is accepted only below `diagnostics/observer_runs/` (or another
  explicitly supplied directory inside the repository).
- Existing saves and logs are copied, never moved or deleted.
- A dirty worktree is rejected for launched runs unless `-AllowDirty` is
  supplied. Official results should always use a committed, clean tree.
- The game is never force-stopped unless `-ForceStopAfterCompletion` is
  supplied. Even then, stopping is allowed only after the target-year EU4 text
  autosave has been copied and revalidated as an immutable checkpoint.

## Local prerequisites

The harness validates these before launch:

1. EU4 `v1.37.5.0` and this mod's `supported_version` agree.
2. `dlc_load.json` enables exactly `mod/RIP.mod`.
3. the external `RIP.mod` descriptor points at this repository root.
4. normal and yearly autosaves are uncompressed (`compress_saves=no`,
   `compress_autosave=no`, `autosave="YEARLY"`), so their headers can be
   checked and milestone autosaves copied before rotation.
5. all command/checkpoint files exist.

The validated user-data path is passed explicitly through EU4's `-userdir`
startup option. This keeps a clean observer fixture isolated from unrelated
launcher descriptors in the normal Documents directory.

The defaults match the currently discovered Windows installation, but every
path can be overridden:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 `
  -GameExe 'D:\Programs Files(x86)\Steam\steamapps\common\Europa Universalis IV\eu4.exe' `
  -UserDataRoot 'D:\Users\Yamtom\Documents\Paradox Interactive\Europa Universalis IV'
```

## First: dry run

Run this from the mod root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1
```

It performs preflight checks and prints the ten planned seeds (`1001` through
`1010`) and launch arguments. It does not create directories or start EU4.

## Short automation smoke test

The installed EU4 binary exposes the startup options `start_tag`, `seed`, and
`auto_run`, and the console commands `run_commands`, `runyear`, `observe`,
and `speed`. EU4 prefixes the `auto_run` value with
`run_commands`. The command only resolves files placed directly in the EU4
user-data root. On launch the harness therefore stages a uniquely prefixed,
BOM-free command bundle there, rewrites nested checkpoint references to those
generated filenames, and passes the setup filename (without a path). First
validate this with a short 1444 to 1446 run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 -Launch -Smoke -Seeds 1001 -AllowDirty
```

Expected behavior:

1. EU4 starts directly at 1444 as KIE with RIP as the only enabled mod.
2. `commands/smoke_setup.txt` schedules the 1446 checkpoint, selects speed 5, and
   enters observer mode before the first daily tick.
3. when the yearly autosave reaches 1446, the harness copies it to
   `checkpoint_1446.eu4` and re-reads the archived date.
4. at 1446 the game pauses and the harness reports the detected endpoint.
5. without `-ForceStopAfterCompletion`, close EU4 normally when prompted in
   the terminal; the harness then archives the flushed logs.

If `auto_run` does not execute on this build, use the explicit fallback:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 -Launch -Smoke -Seeds 1001 -AllowDirty -BootstrapMode ManualConsole
```

After the map loads, open the EU4 console and enter:

```text
run_commands <generated_setup_filename_printed_by_the_harness>
```

Do not begin the ten-run batch until the short smoke has produced its 1446 save
and a manifest with `"status": "completed"`. Then run one full seed and verify
all four checkpoints before starting the remaining nine seeds.

## Full ten-run batch

After committing the exact code being tested and confirming the smoke test:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 -Launch
```

This runs the ten seeds sequentially. At each 1650 endpoint, close EU4 normally
so the next seed can begin. For an explicitly unattended batch, the following
option force-stops EU4 only after the verified endpoint save has been copied:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 -Launch -ForceStopAfterCompletion
```

Force-stop mode trades graceful log flushing for unattended execution. The
endpoint save is archived first; logs are copied after the process exits.
For faster headless simulation, add `-NoGui`; the harness requires it to be
paired with `-ForceStopAfterCompletion` because the hidden UI cannot be closed
interactively:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tests\observer\run_observer.ps1 -Launch -ForceStopAfterCompletion -NoGui
```

## Generated evidence

Each invocation creates a timestamped batch below
`diagnostics/observer_runs/`. Every run directory contains:

- `manifest.json`, conforming to `run-manifest.schema.json`;
- immutable `checkpoint_<year>.eu4` copies captured from the uncompressed
  yearly autosaves before EU4 rotates them;
- fresh `.log`, `.csv`, and `.xml` files from the EU4 logs directory;
- copies of `dlc_load.json`, `settings.txt`, `RIP.mod`, and the mod descriptor.

The batch root also contains `source_snapshot/` plus
`source-inventory.json`. The harness hashes every engine-loaded source file
before and after each run and fails the batch if that fingerprint changes.
This preserves the exact dirty-worktree content used by non-release smoke or
overnight runs instead of recording only the Git commit name.

The harness also writes `batch-summary.json`. Results are not complete merely
because files exist: transfer the measured claim/CB/country metrics into the
balance report and review every error-log delta.

## What counts as a valid observer run

A row may be changed from `Pending` to `Pass`/`Fail` only when all of these are
present:

- seed and exact Git commit/worktree state;
- game version, launch arguments, and enabled-mod configuration;
- a readable archived endpoint checkpoint dated 1650 or later;
- checkpoint saves for 1500, 1550, 1600, and 1650;
- logs archived before the next EU4 launch;
- explicit review of KIE/KRU, MOS/RUS, long-range claims, and subject CBs.

Observer runs do not satisfy the three manual representative campaigns. Those
need human decisions, milestone saves/screenshots, and written play notes.
