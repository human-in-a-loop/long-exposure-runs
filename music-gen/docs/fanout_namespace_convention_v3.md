<!--
created: 2026-08-29T05:15:00Z
cycle: 39
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _manager/fanout-namespace-convention-v3-resolution
supersedes: _infra/fanout-namespace-convention-v2
-->

# Fan-out namespace convention v3 (c39)

**Supersedes** `docs/fanout_namespace_convention_v1.md` (c32) and
`docs/fanout_namespace_convention_v2.md` (c36). This document is the
current canonical description of the writer-boundary clone-namespace
guard implemented by
`long_exposure/workspace_bootstrap.py::_guard_clone_namespace`.

The rule below is **descriptive**, not aspirational: it codifies the
behavior the c36-v2 writer guard already implements and that c37 +
c38 field evidence proved works cleanly across two consecutive
3-clone forks.

## §1 History

| Version | Cycle | Scope                                | Status          |
|---------|-------|--------------------------------------|-----------------|
| v1      | c32   | Leading-underscore infra families only. Substantive `M-*` merges cleanly per-milestone by `(ts, content_hash)`. | Historical (`docs/fanout_namespace_convention_v1.md`). |
| v2      | c36   | Extended to enumerated `M-*` families after `M-INGEST-1/egress-probe` collision on fork 87da4f517029. | Historical bridge (`docs/fanout_namespace_convention_v2.md`). |
| **v3**  | **c39** | **Codifies the c36-v2 behavior after two consecutive clean 3-clone forks (c37, c38) with zero `LedgerConcatError`. Doc-only change.** | **Canonical (this document).** |

Field evidence supporting the v3 codification:

- Fork 675abd086911 (c37): 3 clones × M-RECREATE-1/first-real-audio,
  M-EAR-1/real-label-training-v0, M-GEN-1/palette-driven-batch-v4.
  Concat merge clean; auto-suffix produced deterministic
  `-clone-<k>` variants for every substantive `M-*` and infra event
  a clone emitted.
- Fork 33a2a8003c84 (c38): 3 clones × M-EAR-1/real-label-training-v1,
  M-SCORE-1/bridge-api-real-audio-quantization,
  M-RECREATE-1/second-real-audio-batch. Same behavior; 24 sub-leaf
  milestone rows landed under the auto-suffix guard without concat
  friction.
- c38 post-merge integration cycle noted the persistent
  `_manager/fanout-namespace-convention-discrepancy` ticket that
  this document retires (c38 handoff item #8).

## §2 Rule

When a clone in a fan-out emits ledger events, the `milestone_id` **MUST**
be suffixed with `-clone-<k>` for the following prefix families:

| Family                     | Suffix in fan-out?          | Notes                                                    |
|----------------------------|-----------------------------|----------------------------------------------------------|
| `_infra/` (v1)             | **yes**                     | Housekeeping, per-clone by nature.                       |
| `_run/` (v1)               | **yes**                     | Clone-scoped run boundaries.                             |
| `_archive/` (v1)           | **yes**                     | Each clone archives its own scratch.                     |
| `_plan/` (v1)              | **yes**                     | Rubric-freeze, per-clone-registration events.            |
| `_manager/` (v1)           | **yes**                     | Per-clone deferrals / conflict notes.                    |
| `M-INGEST-1/` (v2)         | **yes**                     | Shared substantive milestone.                            |
| `M-SEP-1/` (v2)            | **yes**                     | Substantive milestone.                                   |
| `M-CLASS-1/` (v2)          | **yes**                     | Substantive milestone.                                   |
| `M-DAW-SPIKE-1/` (v2)      | **yes**                     | Substantive milestone.                                   |
| `M-TRANS-1/` (v2)          | **yes**                     | Substantive milestone.                                   |
| `M-SCORE-1/` (v2)          | **yes**                     | Substantive milestone.                                   |
| `M-HEUR-1/` (v2)           | **yes**                     | Substantive milestone.                                   |
| `M-EAR-1/` (v2)            | **yes**                     | Substantive milestone.                                   |
| `M-RULES-1/` (v2)          | **yes**                     | Substantive milestone.                                   |
| `M-TEX-1/` (v2)            | **yes**                     | Substantive milestone.                                   |
| `M-GEN-1/` (v2)            | **yes**                     | Substantive milestone.                                   |
| `M-RECREATE-1/` (v2)       | **yes**                     | Substantive milestone.                                   |

Detection: `_is_clone_context(workspace)` returns `(True, k)` when
`AGENT_FORK_ID` is set and `AGENT_FORK_CLONE_K` parses to a
non-negative integer. Root-only conductor writes fall through
unchanged.

Idempotence: an id already ending in `-clone-<digit>+` is not
double-suffixed (`_CLONE_SUFFIX_RE` guard).

Root-only conductor writes retain their bare labels — the guard only
fires under clone context.

## §3 Environment variable

`MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` switches the guard into
strict mode: a manufactured un-suffixed emission from clone context
raises `LedgerNamespaceViolation` (subclass of `LedgerSchemaError`)
instead of silently auto-suffixing. Unset (default) the guard
silently rewrites `milestone_id` in place. The same detection runs
symmetrically at the concat boundary via `_lint_clone_shadow`.

Round-trip contract:

- set → manufactured `_infra/foo` from clone raises `LedgerNamespaceViolation`.
- unset → same identifier auto-suffixes to `_infra/foo-clone-<k>`.

Contract test: `tests/test_fanout_namespace_convention_v3.py::test_11`.

## §4 Replay evidence (this cycle)

Machine-readable results live at
`data/fanout_namespace_v3/replay_c37_clones.json` and
`data/fanout_namespace_v3/replay_c38_clones.json`; baseline result at
`data/fanout_namespace_v3/replay_baseline.json`.

### Baseline (main ledger)

- 670/670 rows pass `long_exposure.tools._ledger_schema.validate_event`.
- Byte-determinism × 2 on the assertion pass (two independent
  `python3 scripts/fanout_namespace_v3/replay.py` invocations return
  identical result JSON).

### c37 shadow-ledger replay (fork 675abd086911)

| Clone | Rows in shadow | Rows found in main | Byte-identical (mid,eid,canon-ts) |
|-------|----------------|--------------------|-----------------------------------|
| 0     | 8              | 8                  | 8                                 |
| 1     | 8              | 8                  | 8                                 |
| 2     | 8              | 8                  | 8                                 |

### c38 shadow-ledger replay (fork 33a2a8003c84)

| Clone | Rows in shadow | Rows found in main | Byte-identical (mid,eid,canon-ts) |
|-------|----------------|--------------------|-----------------------------------|
| 0     | 9              | 9                  | 9                                 |
| 1     | 20             | 20                 | 20                                |
| 2     | 10             | 10                 | 10                                |

Every row that landed in main is byte-identical on the
`(milestone_id, event_id, canonical_json-excluding-ts)` tuple against
the corresponding row in the clone shadow.

## §5 Migration note

- `_infra/fanout-namespace-convention-v2` inline references in c33 +
  c36 ledger events remain as-is (append-only ledger contract). v3
  is descriptive-only: no ledger event is rewritten.
- The c36 `docs/fanout_namespace_convention_v2.md` file stays on
  disk as a historical bridge document. It described the tuple
  extension when it landed; v3 codifies the field-tested behavior
  that resulted.
- The c32 `docs/fanout_namespace_convention.md` has moved to
  `docs/fanout_namespace_convention_v1.md` with an unchanged content
  SHA. Any prior link to the c32 path now resolves via git history
  or the v1 archival name.
- Writer code UNCHANGED. Only the docstring reference in
  `long_exposure/workspace_bootstrap.py::_guard_clone_namespace`
  moves from `docs/fanout_namespace_convention.md` to
  `docs/fanout_namespace_convention_v3.md`.

With this document landing, the persistent
`_manager/fanout-namespace-convention-discrepancy` ticket that
recurred through c33, c36, c37, and c38 post-merge integrations is
closed.
