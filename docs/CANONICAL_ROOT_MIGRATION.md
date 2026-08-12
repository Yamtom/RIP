# Canonical-root migration record

## Decision

`RIP/` is the single source of truth and the only Europa Universalis IV mod
root. The former nested `RIP-fresh2` tree must not reappear in a release or in
the Git index.

## Preserved history

- `archive/pre-flatten-root` preserves the outer tree before integration.
- `archive/rip-fresh2` preserves the former nested repository at commit
  `07cf176d953f90a2e827939e96f79b0df8f934a2`.
- merge commit `1b51af9b5c24551781e6a8ae95f960766b0c8bb1`
  connects both histories with a real two-parent merge.
- commit `2691c70a` removes the obsolete mode-`160000` gitlink from the
  canonical tree after the history has been preserved.

No reset, force-push, or mechanical copy-over was used. The merge restores
nested-only content at the canonical root while retaining non-conflicting
outer changes. Content conflicts were resolved in favour of the nested line
only at the conflicting hunks, then reviewed as normal source files.

## Loader normalization

The canonical tree uses only supported engine locations:

- decisions live in `/decisions`, not `/common/decisions`;
- modifiers live in the appropriate `/common/event_modifiers` or other
  supported subsystem, not `/common/modifiers`;
- church aspects and blessings live in `/common/church_aspects`;
- country flags are runtime state and do not require declarations under
  `/common/country_flags`;
- placeholder files directly under `/common` are not loader input.

`restored_ruthenia` required a semantic migration rather than a file move.
Vanilla EU4 already owns that ID as a province modifier. The mod therefore
uses the namespaced IDs `rip_vol_restored_ruthenia_province` and
`rip_vol_restored_ruthenia_country`, with mission references split by scope.

## Rules for future changes

1. Never copy a complete historical tree over the repository root.
2. Recover historical files from `archive/*` in subsystem-sized branches.
3. Give every new tag a country definition, history, flag, colour, and
   localisation before merging.
4. Record every intentional vanilla filename or semantic-ID override in the
   PR description and the collision allowlist.
5. Build release archives from an allowlist of EU4 loader directories; never
   package `.git`, tooling caches, `docs`, tests, `.bak`, or diagnostic ZIPs.
6. Never enable the local and Workshop copies of remote item `2563577714` at
   the same time.
