---
created: 2026-08-29T04:00:00Z
cycle: 32
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/fanout-namespace-convention
---

# Fan-out namespace convention (c32)

## Rule

When a clone in a fan-out emits ledger events for its own bookkeeping —
`_infra/*`, `_run/*`, `_plan/*`, `_archive/*`, `_manager/*` — the
`milestone_id` **MUST** be suffixed with `-clone-<k>`, where `<k>` is the
clone index reported by the harness (0, 1, 2, …).

    ✅  _infra/adopt-cycle31-tests-clone-1
    ✅  _run/cycle_31_launched-clone-2
    ✅  _archive/cycle-31-scratch-clone-0
    ❌  _infra/adopt-cycle31-tests            # bare — collides across clones
    ❌  _run/cycle_31_launched_branch_B       # non-uniform suffix

Substantive milestone ids — the `M-*` families and their sub-milestones
— are the shared work product and are **not** suffixed. Two clones
appending distinct events under the same `M-*` id is expected and
merges cleanly per-milestone by `(ts, content_hash)`.

## Why

Concat-conflict recurrence. Two forks in a row hit `LedgerConcatError`
on a bare `_infra/adopt-cycle<N>-tests` id emitted by more than one
clone:

- fork 392503ab7d47, cycle 21 — `_infra/adopt-cycleXX-tests`
- fork cfc5009aca96, cycle 31 — `_infra/adopt-cycle31-tests`
  between clone-1 (ts=2026-08-29T02:50:00Z) and clone-2 (ts=2026-08-29T00:42:00Z)

The concat validator requires monotonic per-milestone timestamps in
file order; different clones write in independent time orders, so
sharing a milestone id on independent operations is structurally
race-prone. Namespacing per clone eliminates the shared id and makes
the collision impossible.

## What to suffix (the leading-underscore infra families)

| Family      | Suffix in fan-out?         | Rationale                                                  |
|-------------|----------------------------|------------------------------------------------------------|
| `_infra/`   | **yes**                    | Housekeeping, per-clone by nature.                         |
| `_run/`     | **yes** (per-clone launch/close) | Clone-scoped run boundaries.                          |
| `_archive/` | **yes**                    | Each clone archives its own scratch.                       |
| `_plan/`    | **yes** (when clone-emitted) | Rubric-freeze, per-clone-registration events.            |
| `_manager/` | **yes**                    | Per-clone deferrals / conflict notes.                      |
| `M-*/…`     | **no**                     | Shared substantive milestone; multiple events expected.    |

Root-level events (conductor emits, single-clone default path) do not
need the suffix — the collision surface is only pluralized clones.

## Applied historical reconciliations

The c32 reconciliation of fork cfc5009aca96 shadow ledgers renamed
these ids on merge (see `tools/stale/_reconcile_fork_cfc5009aca96.py`):

    clone-1  _run/cycle_31_launched_branch_B                           → _run/cycle_31_launched-clone-1
    clone-1  _run/cycle_31_closed_branch_B                             → _run/cycle_31_closed-clone-1
    clone-1  _infra/adopt-cycle31-tests                                → _infra/adopt-cycle31-tests-clone-1
    clone-1  _archive/cycle-31-branch-B-scratch                        → _archive/cycle-31-scratch-clone-1
    clone-1  _archive/cycle-31-branch-B-reinvocation-scratch           → _archive/cycle-31-reinvocation-scratch-clone-1
    clone-1  _infra/egress-probe-cycle-31-branch-B-reinvocation        → _infra/egress-probe-cycle-31-reinvocation-clone-1
    clone-1  _infra/adopt-fanout-artifacts-M-DAW-SPIKE-1-...           → …-clone-1
    clone-1  _plan/palette_schema_rubric_frozen                        → _plan/palette_schema_rubric_frozen-clone-1
    clone-2  _run/cycle_31_launched                                    → _run/cycle_31_launched-clone-2
    clone-2  _run/cycle_31_closed                                      → _run/cycle_31_closed-clone-2
    clone-2  _infra/adopt-cycle31-tests                                → _infra/adopt-cycle31-tests-clone-2
    clone-2  _archive/cycle-31-branch-C-scratch                        → _archive/cycle-31-scratch-clone-2
    clone-2  _infra/sb-dry-run-script                                  → _infra/sb-dry-run-script-clone-2
    clone-2  _plan/verdict_rubric_frozen_armed_harness_fixture         → …-clone-2

Branch A (clone-0) had already merged to main with its own scratch-suffixed
ids; those are grandfathered — no rename needed.

## For future fan-out scaffolding

The harness auto-writer (`long_exposure.exploration._append_report_artifact_event`)
already namespaces reports as `_run/report_cycles_<lo>-<hi>_clone-<k>` — that
pattern is the template. Any clone-emitted infra-family id should follow
the same shape: `<bare-id>-clone-<k>`.

New cycles: before emitting an infra event from inside a clone, check
`_is_clone()`; if true, append `-clone-<k>` to the id.
