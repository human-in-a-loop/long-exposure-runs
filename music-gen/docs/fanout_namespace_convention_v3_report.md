<!--
created: 2026-08-29T05:50:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/fanout-namespace-convention-v3-resolution
-->

# Fan-out namespace convention v3 — resolution report (c39 clone-2, Branch C)

## §1 Verdict

**`CONVENTION_v3_LANDS`**

- `rubric_hash` = `4cd79e4fdba5431e25ec10b6af5c56e69bf77170dcac2e469c11727af2cf628e`
  (embedded verbatim in `data/fanout_namespace_v3/verdict.json`
  and pinned in `data/fanout_namespace_v3/rubric_hash.txt`).
- All 11 rubric gates satisfied (see §7).
- 19/19 tests green in `tests/test_fanout_namespace_convention_v3.py`.
- Persistent `_manager/fanout-namespace-convention-discrepancy` ticket
  (open since c33) is declared **closed** by this cycle (see §10).

## §2 Path chosen

**Path 2** — codify the c36-v2 auto-suffix-all behavior in a new v3
convention doc. Writer code UNCHANGED beyond a docstring reference
bump from `docs/fanout_namespace_convention.md` to
`docs/fanout_namespace_convention_v3.md`.

| Path                                             | Chosen | Pros (numbered)                                                                                                                                                                                                                                                                                                                                                     | Cons (numbered)                                                                                                                                                                                                                                                                                                                                    |
|--------------------------------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Path 1**: narrow guard to c32 leading-underscore set only | No | 1. Restores c32 convention as descriptive truth. 2. Smaller writer surface. 3. Substantive milestones retain pooled per-milestone view.                                                                                                                                                                                                                              | 1. Removes a guard that has held cleanly through 2 consecutive 3-clone forks (c37, c38) with zero `LedgerConcatError`. 2. Shifts collision burden back to concat conductor. 3. Undoes c33/c36 hardening arc's usable behavior. 4. Re-opens the persistent ticket at every future post-merge integration.                                              |
| **Path 2**: update doc to codify auto-suffix-all | **Yes** | 1. Codifies a working guard. c37 + c38 field evidence documented. 2. Zero API / env-var / MRO risk (no writer code changes). 3. Closes the persistent `_manager/fanout-namespace-convention-discrepancy` ticket. 4. Concat conductor keeps its clean per-milestone dedup.                                                                                            | 1. Introduces a v1/v2/v3 doc lineage that readers must navigate. 2. Substantive `M-*` fragmentation stays — two clones on the same substantive milestone emit distinct labels. Accepted per c36's analysis.                                                                                                                                          |

Rationale: c37 (fork 675abd086911) and c38 (fork 33a2a8003c84)
provided field evidence that the writer guard is producing usable
deterministic behavior. Path 1 would REMOVE that working guard and
re-open the ticket. Path 2 codifies reality.

## §3 What changed on disk

| Change                                                                                                     | Before                                          | After                                                                                              |
|------------------------------------------------------------------------------------------------------------|-------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Rubric committed first                                                                                     | absent                                          | `docs/fanout_namespace_convention_v3_rubric.md` (SHA `4cd79e4f…`, pinned in `rubric_hash.txt`)     |
| c32 doc relocated                                                                                          | `docs/fanout_namespace_convention.md`           | `docs/fanout_namespace_convention_v1.md` (content SHA `de45eb4e…` unchanged; mtime touched to reflect the rename)  |
| v3 doc created                                                                                             | absent                                          | `docs/fanout_namespace_convention_v3.md` (SHA `7883557f…`)                                        |
| c36 v2 doc                                                                                                 | `docs/fanout_namespace_convention_v2.md` (`a67bf101…`) | unchanged (historical bridge; SHA byte-identical)                                                  |
| Writer docstring reference bumped (3 occurrences: guard header comment, `_guard_clone_namespace` raise message, `_lint_clone_shadow` raise message) | `long_exposure/workspace_bootstrap.py` SHA `462e3d30…` | SHA `af0e1e87…` (docstring-only delta; no code-behavior change)                                    |
| Replay tooling                                                                                             | absent                                          | `scripts/fanout_namespace_v3/{snapshot_anchors,replay,emit_verdict}.py`                            |
| Test suite                                                                                                 | absent                                          | `tests/test_fanout_namespace_convention_v3.py` (19 named cases, all green)                        |
| Ledger events                                                                                              | 670 rows in main                                | +10 rows in `clone-2` shadow (6 substantive `_manager/…/…-clone-2` + 4 housekeeping `-clone-2`)   |

## §4 Baseline replay

`scripts/fanout_namespace_v3/replay.py baseline` streams every row of
`promise_ledger.jsonl` through
`long_exposure.tools._ledger_schema.validate_event`.

| Metric      | Value    |
|-------------|----------|
| Total rows  | 670      |
| Passed      | 670      |
| Failed      | 0        |

Byte-determinism × 2 verified: two independent invocations produce
`replay_baseline.json` with SHA `c20a6d354ba0c2c5…` byte-identical.

## §5 c37 shadow-ledger replay (fork 675abd086911)

For every row in each clone's shadow ledger, we look up the matching
`(milestone_id, event_id)` row in main and compare the
`canonical_json` with `ts` stripped.

| Clone | Rows in shadow | Byte-identical in main | Missing | Mismatched |
|-------|----------------|------------------------|---------|------------|
| 0     | 8              | 8                      | 0       | 0          |
| 1     | 8              | 8                      | 0       | 0          |
| 2     | 8              | 8                      | 0       | 0          |
| **Total** | **24**     | **24**                 | **0**   | **0**      |

## §6 c38 shadow-ledger replay (fork 33a2a8003c84)

| Clone | Rows in shadow | Byte-identical in main | Missing | Mismatched |
|-------|----------------|------------------------|---------|------------|
| 0     | 9              | 9                      | 0       | 0          |
| 1     | 20             | 20                     | 0       | 0          |
| 2     | 10             | 10                     | 0       | 0          |
| **Total** | **39**     | **39**                 | **0**   | **0**      |

The c38 clone-1 20 rows include the concat-merged normalizer-v2
self-continuation captured by the c38 post-merge integration cycle.
All 20 remain byte-identical.

## §7 Invariant preservation

| Invariant                                                                                | Status |
|------------------------------------------------------------------------------------------|--------|
| `append_ledger_event.__signature__ == (workspace: Path, event: dict) -> None`            | UNCHANGED |
| `MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` round-trip: set → raise; unset → auto-suffix | UNCHANGED (test 11 green) |
| `LedgerNamespaceViolation.__mro__ ⊇ {LedgerSchemaError, ValueError, …}`                  | UNCHANGED |
| `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt` SHA-256                    | UNCHANGED (`12e14f8a…`) |
| `long_exposure/tools/_ledger_schema.py` SHA-256                                          | UNCHANGED (`566fad69…`) |
| `_FANOUT_INFRA_PREFIXES` tuple == c36-v2 baseline (17 entries)                            | UNCHANGED |

## §8 Anchor preservation manifest

Snapshot pre/post via `scripts/fanout_namespace_v3/snapshot_anchors.py`;
recorded verbatim at `data/fanout_namespace_v3/anchor_preservation.json`.

| Anchor                                                                          | Pre SHA-256       | Post SHA-256      | Note                                                            |
|---------------------------------------------------------------------------------|-------------------|-------------------|-----------------------------------------------------------------|
| c14 `long_exposure/tools/_ledger_schema.py` (SSoT)                              | `566fad6977e00…` | `566fad6977e00…` | byte-identical                                                  |
| c33 `tests/fixtures/harness_clone_namespace_guard_rubric_hash.txt`              | `12e14f8a4d780…` | `12e14f8a4d780…` | byte-identical                                                  |
| c32 `docs/fanout_namespace_convention.md` (old path)                             | `de45eb4eac330…` | `null` (moved)   | content preserved at new path                                    |
| `docs/fanout_namespace_convention_v1.md` (new path)                              | `null`           | `de45eb4eac330…` | SHA byte-identical to c32 original                              |
| c36 `docs/fanout_namespace_convention_v2.md`                                     | `a67bf101be6ca…` | `a67bf101be6ca…` | byte-identical (historical bridge, unedited)                    |
| c39 `docs/fanout_namespace_convention_v3.md`                                     | `null`           | `7883557f372f4…` | new                                                              |
| c39 `docs/fanout_namespace_convention_v3_rubric.md`                              | `4cd79e4fdba54…` | `4cd79e4fdba54…` | committed first; unchanged                                       |
| `long_exposure/workspace_bootstrap.py`                                          | `462e3d30a4f11…` | `af0e1e87f7ca0…` | docstring-only delta (3 refs bumped from `.md` → `_v3.md`)     |

## §9 c40 handoff

**None from this branch.** This branch closes the persistent
`_manager/fanout-namespace-convention-discrepancy` ticket (see §10).

The c38 handoff items #1–#7 and #9 (SB corpus expansion, score-bridge
normalizer-v2 promotion, stage-06 migration, quantize tuning, corpus
extension, VST3 activation) remain valid and untouched by this branch.

Merge conductor note: on integration, `docs/fanout_namespace_convention_v1.md`
should be recorded as a rename of `docs/fanout_namespace_convention.md`
via `git mv` (this sandbox lacked git-commit approval; the on-disk
move preserves content SHA byte-identically, so `git mv` on the merge
side produces the same delta).

## §10 Namespace convention discrepancy — declared closed

The `_manager/fanout-namespace-convention-discrepancy` ticket has
recurred in every post-merge integration since c33:

- c33: writer guard extended to substantive `M-*` families;
  `_infra/fanout-namespace-convention-v2` inline label introduced;
  c32 doc not updated.
- c36: v2 doc landed as `docs/fanout_namespace_convention_v2.md`
  after `M-INGEST-1/egress-probe` collision on fork 87da4f517029;
  c32 doc still on disk, still saying "substantive `M-*` unsuffixed".
- c37, c38 post-merge cycles: 2 more successful 3-clone forks under
  the c36-v2 guard; discrepancy ticket carried forward at each cycle
  close.

c39 clone-2 (Branch C) resolves the discrepancy by moving the c32 doc
to its `_v1.md` archival name and publishing the c39
`docs/fanout_namespace_convention_v3.md` document that codifies the
c36-v2 behavior on evidence of two consecutive clean 3-clone forks.

Writer code unchanged beyond a docstring reference bump.
`_FANOUT_INFRA_PREFIXES` unchanged.
`append_ledger_event` public signature unchanged.
`MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` round-trip unchanged.
`LedgerNamespaceViolation` MRO unchanged.
c14 SSoT + c33 guard fixture SHAs byte-identical pre/post.
c37 + c38 shadow-ledger replay 63/63 byte-identical.
Baseline 670/670 pass tightened validator.

**Ticket status: closed.**
