---
created: 2026-08-29T08:20:00Z
cycle: 36
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/fanout-namespace-convention-v2
supersedes: _infra/fanout-namespace-convention
---

# Fan-out namespace convention v2 (c36)

**Supersedes** `docs/fanout_namespace_convention.md` (c32). v1 remains
canonical for the infra-family portion of the rule; v2 EXTENDS it to
cover substantive `M-*` milestone families.

## Rule (extended)

When a clone in a fan-out emits ledger events, the `milestone_id` **MUST**
be suffixed with `-clone-<k>` for the following prefix families:

| Family                     | Suffix in fan-out?          | Notes                                                    |
|----------------------------|-----------------------------|----------------------------------------------------------|
| `_infra/` (v1)             | **yes**                     | Housekeeping, per-clone by nature.                       |
| `_run/` (v1)               | **yes**                     | Clone-scoped run boundaries.                             |
| `_archive/` (v1)           | **yes**                     | Each clone archives its own scratch.                     |
| `_plan/` (v1)              | **yes**                     | Rubric-freeze, per-clone-registration events.            |
| `_manager/` (v1)           | **yes**                     | Per-clone deferrals / conflict notes.                    |
| **`M-INGEST-1/` (v2)**     | **yes**                     | Substantive milestone shared across clones — collisions on shared probes and pipelines observed at c43. |
| **`M-SEP-1/` (v2)**        | **yes**                     | Substantive milestone.                                   |
| **`M-CLASS-1/` (v2)**      | **yes**                     | Substantive milestone.                                   |
| **`M-DAW-SPIKE-1/` (v2)**  | **yes**                     | Substantive milestone.                                   |
| **`M-TRANS-1/` (v2)**      | **yes**                     | Substantive milestone.                                   |
| **`M-SCORE-1/` (v2)**      | **yes**                     | Substantive milestone.                                   |
| **`M-HEUR-1/` (v2)**       | **yes**                     | Substantive milestone.                                   |
| **`M-EAR-1/` (v2)**        | **yes**                     | Substantive milestone.                                   |
| **`M-RULES-1/` (v2)**      | **yes**                     | Substantive milestone.                                   |
| **`M-TEX-1/` (v2)**        | **yes**                     | Substantive milestone.                                   |
| **`M-GEN-1/` (v2)**        | **yes**                     | Substantive milestone.                                   |
| **`M-RECREATE-1/` (v2)**   | **yes**                     | Substantive milestone (registered under priority-override guidance). |

Idempotence: an id already ending in `-clone-<digit>+` is not double-
suffixed.

## Why

Third recurrence of `LedgerConcatError` on a shared substantive
milestone. Previously observed on infra families:

- fork 392503ab7d47, cycle 21 — `_infra/adopt-cycleXX-tests` (fixed
  ad-hoc)
- fork cfc5009aca96, cycle 31 — `_infra/adopt-cycle31-tests` (fixed by
  v1 convention)

Now observed on a substantive family:

- fork 87da4f517029, cycle 36 — `M-INGEST-1/egress-probe` between
  clone-0 (validated, 2026-08-29T07:20:30Z) and clone-2 (reopened,
  2026-08-29T05:25:30Z).

v1's rule ("substantive `M-*` merges cleanly per-milestone by (ts,
content_hash)") was correct for non-shared work. It fails for shared
probe/utility milestones that every clone touches at top-of-cycle
(egress probe is the recurring case; any future shared harness surface
carries the same risk).

The auditor-observed trade-off: extending the suffix to `M-*` fragments
the per-milestone view of the ledger. Two clones working on the same
substantive milestone (e.g. two clones both extending
`M-EAR-1/real-label-training-v0`) will emit distinct labels. This is
accepted as the cost of structural prevention across all families the
run maintains.

## Retroactive reconciliation policy (c36)

To limit downstream WARN churn, the c36 reconciliation only renamed
milestone ids that ACTUALLY collided in a shadow-ledger concat:

    clone-0  M-INGEST-1/egress-probe  →  M-INGEST-1/egress-probe-clone-0
    clone-2  M-INGEST-1/egress-probe  →  M-INGEST-1/egress-probe-clone-2

The 3 primary substantive deliverables (`M-EAR-1/real-label-training-v0`,
`M-GEN-1/palette-driven-batch-v3`, `M-DAW-SPIKE-1/vst3-render-
nondeterminism-characterization`) each mapped to a single clone, did
not collide, and were reconciled unsuffixed against their existing
plan_of_record.md rows.

Forward-looking policy: from c37 onward, the writer guard auto-suffixes
every `M-*` id emitted from a clone, matching the extended rule above.
The plan-of-record convention will need to accept the suffixed variant
(existing WARN class already observed for c33 `_infra/anchor-manifest-v1`
and `_infra/harness-clone-namespace-guard` where the -clone-2 emission
does not match the bare plan row).

## Enforcement (writer guard)

Implementation lives at
`long_exposure/workspace_bootstrap.py::_guard_clone_namespace`:

- The `_FANOUT_INFRA_PREFIXES` constant is extended to include the 12
  substantive `M-*/` prefixes above.
- Behavior modes remain: default (silent auto-suffix) and strict
  (`MUSICGEN_LEDGER_STRICT_CLONE_NAMESPACE=1` raises
  `LedgerNamespaceViolation`).
- `_lint_clone_shadow` picks up the extended prefix set at the concat
  boundary symmetrically.

## For future fan-out scaffolding

Same rule as v1: `<bare-id>-clone-<k>`. The guard now enforces this
uniformly regardless of whether the family is a leading-underscore
infra family or a substantive `M-*` family. Callers do not need to
change — the guard is entirely internal to the writer.
