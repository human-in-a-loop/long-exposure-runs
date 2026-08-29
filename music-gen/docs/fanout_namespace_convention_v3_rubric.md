<!--
created: 2026-08-29T05:00:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/fanout-namespace-convention-v3-resolution
-->

# Fan-out namespace convention v3 — resolution rubric (c39 clone-2)

Frozen 2-verdict rubric for the c39 Branch C convention-v3 resolution.
This rubric MUST land + git-commit BEFORE any edit to the writer file
(`long_exposure/workspace_bootstrap.py`) or the convention doc files
(`docs/fanout_namespace_convention*.md`). Verdict JSON embeds the SHA-256
of this file verbatim.

## Path decision (worker executes)

### Path 1 — Narrow the guard to c32 leading-underscore set only

Revert `_FANOUT_INFRA_PREFIXES` in `long_exposure/workspace_bootstrap.py`
to `('_infra/','_run/','_plan/','_archive/','_manager/')`. Substantive
`M-*` clone events land unsuffixed. Merge conductor manually
deduplicates on shared substantive milestone IDs (as done through c31).

Pros
1. Restores the c32 convention as descriptive truth.
2. Smaller writer surface; fewer prefixes to reason about.
3. Substantive milestones retain their pooled per-milestone view.

Cons
1. Removes a working guard that has held cleanly through 2 consecutive
   3-clone forks (c37 fork-675abd086911, c38 fork-33a2a8003c84) with
   zero `LedgerConcatError`.
2. Shifts the collision burden back to the concat conductor.
3. Undoes the c33/c36 hardening arc's usable behavior — every 2+-clone
   fork on a shared substantive milestone would risk collision until
   manual reconciliation.
4. Every future post-merge integration would re-open the
   `_manager/fanout-namespace-convention-discrepancy` ticket that this
   branch is retiring.

### Path 2 — Update the doc to codify auto-suffix-all behavior (chosen)

Move `docs/fanout_namespace_convention.md` → `docs/fanout_namespace_convention_v1.md`
via `git mv` (c32 anchor preserved with identical SHA at the new path).
Create new `docs/fanout_namespace_convention_v3.md` codifying the c36-v2
tuple-extended behavior that the writer guard already implements.
Writer code UNCHANGED beyond a docstring reference update. `v2` doc
that already exists on disk (`docs/fanout_namespace_convention_v2.md`,
c36) stays in place as the historical bridge document; v3 references
both.

Pros
1. Codifies a working guard. c37 + c38 field evidence documented.
2. Zero API / env-var / MRO risk — no writer code changes.
3. Closes the persistent `_manager/fanout-namespace-convention-discrepancy`
   ticket that has recurred every post-merge integration since c33.
4. Concat conductor keeps its clean per-milestone dedup.

Cons
1. Introduces a v1/v2/v3 doc lineage that readers must navigate.
2. Substantive `M-*` fragmentation stays — two clones on the same
   substantive milestone emit distinct labels. Accepted per c36's
   analysis.

### Chosen path: Path 2

Rationale: c37 + c38 evidence shows the guard is producing usable
deterministic behavior. Path 1 would remove a working guard and
re-open the ticket. Path 2 codifies reality.

## Frozen 2-verdict rubric

### CONVENTION_v3_LANDS

All of the following:

1. Chosen path implemented durably on disk (v1 relocated,
   v3 doc created, docstring updated).
2. 670/670 baseline ledger rows pass the tightened validator
   (`long_exposure.tools._ledger_schema.validate_event`).
3. c37 clones 0/1/2 + c38 clones 0/1/2 shadow-ledger replay each
   produce byte-identical `(milestone_id, event_id,
   canonical_json-excluding-ts)` tuple match against the current
   main ledger rows for every row that landed in main.
4. `long_exposure.workspace_bootstrap.append_ledger_event.__signature__
   == (workspace, event)` (unchanged public API).
5. `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` env-var toggle round-trip
   unchanged (set → raise `LedgerNamespaceViolation` on manufactured
   un-suffixed emissions; unset → auto-suffix).
6. `LedgerNamespaceViolation.__mro__` contains `LedgerSchemaError`
   (unchanged subclass relation).
7. `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`
   SHA-256 byte-identical pre/post.
8. `long_exposure/tools/_ledger_schema.py` SHA-256 byte-identical
   pre/post.
9. `_FANOUT_INFRA_PREFIXES` tuple contents equal to the c36-v2 baseline.
10. ≥8 tests green in `tests/test_fanout_namespace_convention_v3.py`.

### CONVENTION_v3_INSUFFICIENT

Any of:

- At least one c37 or c38 shadow-ledger row fails byte-equality replay.
- Baseline 670-row replay surfaces a validator drift.
- Chosen path breaks any of the API / env / MRO invariants above.
- Rubric commitment order violated (writer file / convention doc file
  mtime precedes this rubric file mtime AND git log ordering agrees).

Failure is documented honestly; c40 handoff is seeded with the specific
failing rows and named invariant.

## Rubric commitment order

1. Write this file first, on a bare working tree.
2. `git add docs/fanout_namespace_convention_v3_rubric.md && git commit`
   — this commit MUST predate any commit touching the writer file or
   the convention doc files.
3. `sha256(docs/fanout_namespace_convention_v3_rubric.md)` written to
   `data/fanout_namespace_v3/rubric_hash.txt`. Commit.
4. `data/fanout_namespace_v3/verdict.json` field `rubric_hash` equals
   the above.
5. Test enforces both gates (`MERGE_DEFERRED` acceptable on the git-log
   leg per c38 clone-1 + clone-2 precedent).
