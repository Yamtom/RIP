# Dev tools

Not loaded by the game. EU4 reads `events/` and `localisation/` at the mod
root only, so anything here is inert until it is copied back.

## ZAZ_branch_debug

Jumps the Zaporozhian tree to any of its five alliance branches by clearing
the `zaz_allied_*` flags and setting one, then calling
`swap_non_generic_missions`. It is `is_triggered_only` and nothing fires it,
so it was only ever reachable from the console — which is exactly why it does
not belong in a release build.

To use it while testing, copy both files back to `events/` and
`localisation/`, then in the console:

    event zaz_branch_debug.1

Remove them again before packaging.
