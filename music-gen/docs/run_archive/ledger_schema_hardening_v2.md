<!--
created: 2026-08-28T14:30:00Z
cycle: 14
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/ledger-schema-hardening-v2
-->

# Ledger Schema Hardening v2 — field-type + enum

**Cycle:** 14
**Branch:** clone-0 of fork `855d4c2e9945`
**Milestone:** `_infra/ledger-schema-hardening-v2`
**Status:** validated/high

## 1. The 3-cycle hardening arc

The single-source-of-truth (SSoT) ledger validator matured across three
cycles, each closing a distinct drift surface:

| Cycle | Milestone                            | Gate closed                                                                 |
|-------|--------------------------------------|-----------------------------------------------------------------------------|
| 10    | `_infra/ledger-schema-hardening`     | **Writer** — extracted required-field validator to `long_exposure.tools._ledger_schema` (SSoT); tightened `workspace_bootstrap.append_ledger_event()` to validate at write time; UUID5 event_id auto-fill; rejects cycles-7/8/9 drift (missing event_id, flat-string confidence, missing run_id + long-form assessor). |
| 12    | `_infra/fanout-concat-hardening`     | **Concat** — `workspace_bootstrap.concat_clone_ledgers` now runs `validate_event` on every candidate row; per-milestone file-order ts monotonicity within the candidate stream; content-hash tiebreak (SHA-256, not line number); atomic write via `os.replace`; `LedgerConcatError` typed subclass of `LedgerSchemaError`. |
| 14    | `_infra/ledger-schema-hardening-v2`  | **Field-type + enum** — added `supersedes_path` type check (must be `str`) and the pre-concat `_lint_clone_shadow` seam that surfaces drift at the clone emit boundary using the same SSoT invariants concat already enforces. |

The invariant that binds the three cycles: **every ledger event, wherever
written or merged, passes the same SSoT `validate_event` before it hits
the main ledger file.** Cycles 10 → 12 → 14 successively widened where
"before it hits the main ledger" is enforced.

## 2. Cycle-13 drift retrospective

Cycle 13 fork `54a6c185816e` post-merge integration surfaced two new
drift classes that the pre-cycle-14 validator did not cover:

### 2a. List-form `supersedes_path` (line 266)

A clone-1 archive event for `_archive/gap2-dawdreamer-scratch` emitted:

```json
"supersedes_path": ["tools/_dd_probe.py","tools/_dd_probe2.py","tools/_emit_gap2_v3_events.py"]
```

All other rows use string form. `promise_check._canon` calls `.lstrip("./")`
on the value and crashed:

```
AttributeError: 'list' object has no attribute 'lstrip'
```

Cycle-13 integration repaired the row in-place (rewrote `supersedes_path`
to the primary string form, kept the other two paths in `artifacts`). The
underlying validator did nothing to prevent recurrence.

### 2b. Wrong-context `in-progress` status (line 250)

Clone-2 emitted a `M-TEX-1/stage-by-stage` kickoff with `status:
"in-progress"` **after** the cycle-9 `validated/high` roll-up. The
narrative said "reopening under widening sub-scope"; the correct
keyword was `reopened`. `promise_check` surfaced this as an ERROR at
the state-transition check (a `validated → in-progress` edge requires
an intervening `reopened` event).

Cycle-13 integration rewrote the status to `reopened`. Note the enum
value `in-progress` is itself canonical — the cycle-14 hardening does
NOT reject it; the state-transition check (out of scope for this
milestone) does. What cycle-14 DOES tighten is that any status outside
the canonical enum (e.g. `wobble`, `in_progress` with an underscore,
`inProgress`) fails at emit boundary with the field name in the message.

## 3. Extended validator surface

`long_exposure/tools/_ledger_schema.py` gains two extensions and one
alias export:

### 3a. `supersedes_path` type check (new)

```python
supersedes_path = event.get("supersedes_path")
if supersedes_path is not None and not isinstance(supersedes_path, str):
    errors.append(
        f"supersedes_path must be a string, got "
        f"{type(supersedes_path).__name__} ({supersedes_path!r}) "
        f"— cycle-13 drift: list-form crashed promise_check._canon"
    )
```

The rationale is embedded in the error string so an operator who hits
this at emit boundary sees the historical context inline.

### 3b. Status enum (existing check, now aliased for external reference)

The existing `STATUS_VALUES` frozenset already rejects any status not
in `{not-started, in-progress, validated, invalidated, reopened,
deferred, action_required, superseded}`. Cycle 14 adds a module-level
alias `_STATUS_ENUM = STATUS_VALUES` so tests and the pre-concat lint
can reference the enum by the name the brief calls out. The alias is
`is`-identical to the underlying frozenset (verified in test_18).

The brief proposed a five-value enum `{in-progress, validated,
invalidated, reopened, superseded}`. That set is a proper **subset**
of the SSoT's `STATUS_VALUES` (which also holds `not-started`,
`deferred`, `action_required`). Per the falsifiability escape hatch
in the brief — "if the observed status union includes a value NOT in
the proposed enum, do NOT reject it — expand the enum" — the SSoT's
superset is retained. The observed union across the 275-row ledger is
in fact `{validated, in-progress, reopened, invalidated}` — a strict
subset of both.

### 3c. Public API unchanged

- `append_ledger_event(workspace: Path, event: dict) -> None`: unchanged
  signature, unchanged semantics on valid input; only its rejection
  surface grew.
- `concat_clone_ledgers(workspace: Path, fork_dir: Path) -> int`:
  unchanged signature, unchanged semantics on valid input.
- New symbol `_STATUS_ENUM` exported from `_ledger_schema`.
- New symbol `_lint_clone_shadow` exported from `workspace_bootstrap`
  (leading underscore signals it is a subordinate seam, not a caller-
  side integration point; `concat_clone_ledgers` remains the load-
  bearing merge entry point).

## 4. Pre-concat lint mechanism

`workspace_bootstrap._lint_clone_shadow(shadow_path)` runs
`_ledger_schema.validate_event` on every non-blank line of a shadow
ledger file. On any failure:

- `json.JSONDecodeError` → wrapped in `LedgerConcatError` with
  `<shadow_path>:<line_number>: invalid JSON: <parse error>`.
- Schema validation failure → `LedgerConcatError` with
  `<shadow_path>:<line_number> (milestone_id=<mid>): <errors>` where
  `<errors>` is the semicolon-joined list of field-named messages from
  the SSoT.

The error surface follows the `<shadow_path>:<line_number>:<field>`
contract: an operator reading the traceback can `grep <shadow_path>`
and jump directly to the offending line.

### Why not fold this into concat?

`concat_clone_ledgers` **already** invokes `validate_event` on every
candidate row and raises `LedgerConcatError` **before** the atomic
`os.replace` writes anything to the main ledger. The lint helper is
factored out so:

1. A clone can lint its own shadow at emit boundary (before the fan-out
   barrier collapses) — surfacing drift where the operator can
   attribute it to a specific clone, not at post-merge integration.
2. Tests can exercise the per-line validator without instantiating a
   full fork directory + main-ledger state machine.
3. The public API of `concat_clone_ledgers` stays unchanged.

Both gates use the SAME `validate_event` symbol from the SAME SSoT
module — `is`-identity verified by the existing test §10 in
`tests/test_fanout_concat_validation.py`.

## 5. Regression proof

### 5a. 275/275 rows pass the tightened validator

```
275-row regression fails: 0
```

Full sweep at `PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure
/usr/bin/python3 tests/test_ledger_writer_validation.py` case
`test_09_all_existing_ledger_events_pass`.

### 5b. Observed `status` union (275 rows)

| Count | Value        |
|-------|--------------|
| 237   | validated    |
| 33    | in-progress  |
|  3    | reopened     |
|  2    | invalidated  |

Strict subset of `_STATUS_ENUM`. No enum expansion needed.

### 5c. Observed `supersedes_path` shape (post cycle-13 repair)

| Count | Type |
|-------|------|
| 10    | str  |

All string. Cycle-13's list-form drift is gone; the type check is now
the only line of defense against its recurrence.

## 6. Test coverage delta

### 6a. `tests/test_ledger_writer_validation.py` (13 → 18)

- `test_14_status_in_progress_accepted` — canonical `in-progress` still
  accepted (it is a legitimate status; the cycle-13 drift was a
  state-transition mistake, not an enum violation).
- `test_15_status_wobble_rejected` — unknown status keyword rejected
  with field name `status` and the offending value in the message.
- `test_16_supersedes_path_string_accepted` — string form succeeds.
- `test_17_supersedes_path_list_rejected` — list form rejected with
  field name `supersedes_path` and "must be" in the message; ledger
  file not created on validation failure (atomicity).
- `test_18_supersedes_path_absent_accepted` — optional field absent is
  fine; asserts `_STATUS_ENUM is STATUS_VALUES` and brief-enum ⊆ enum.

Result: **18/18 pass**.

### 6b. `tests/test_fanout_concat_validation.py` (10 → 13)

- `case 11` — list-form `supersedes_path` in a clone shadow row
  rejected at BOTH the standalone `_lint_clone_shadow` helper AND the
  concat merge, with the shadow path, `:2` (line number), and
  `supersedes_path` (field name) all present in the error message.
  Main ledger not created (atomicity).
- `case 12` — invalid `status` value in a clone shadow row rejected
  at both gates with `status` + `wobble` + shadow path + `:1`.
- `case 13` — positive control: a shadow with string-form
  `supersedes_path` AND `status: "in-progress"` lints clean, then
  concat merges to a byte-identical result; idempotent on repeat.

Result: **13/13 pass**.

### 6c. `tests/test_integration_cross_branch.py` §28

Seven §28 checks covering the SSoT alias `is`-identity, `_lint_clone_shadow`
importability, `LedgerConcatError` MRO, drift-rejection message shape for
both drift classes, positive control for string form, 275-row regression,
and the report file's on-disk presence.

Result: **overall integration test PASS (0 failures)**.

### 6d. `_LE_PARENT` sys.path shim

Both writer and concat test files carry the mandatory shim:

```python
_LE_PARENT = "/home/user/human-in-a-loop/long-exposure"
if _LE_PARENT not in sys.path:
    sys.path.insert(0, _LE_PARENT)  # or .append() in the writer file
```

Cycles 10/11/12/13 all caught workers who forgot this. The cycle-14
extensions inherit the existing shims unchanged.

## 7. Migration note

**Zero caller-side changes.**

- Every prior emitter that used `append_ledger_event(workspace, event)`
  continues to work byte-identically as long as the event was
  well-formed under cycle-12 semantics. The two new checks fire only
  on `supersedes_path` being a non-string (previously silently
  accepted, subsequently crashed `promise_check._canon`) or `status`
  being outside the canonical enum (previously rejected already —
  cycle 14 just aliases the enum for external reference).
- `concat_clone_ledgers(workspace, fork_dir)` public signature and
  return type unchanged.
- Existing worker-side test suites (`test_ingest.py`, `test_score_bridge.py`,
  `test_texture_panel.py`, `test_rules_extraction.py`, `test_ear_training.py`,
  `test_egress_ready_state.py`, `test_heuristics_isolation.py`,
  `test_octave_suppression.py`, `test_sidecar_isolation.py`,
  `test_rules_schema.py`) continue to pass without modification.
- `promise_check` behavior on the 275-row ledger is unchanged (0 ERRORs,
  same WARN count as pre-cycle-14 baseline, up to the cycle-14 events
  this branch itself adopts).

## 8. What this closes and what remains

### Closed by cycles 10 + 12 + 14

| Drift class                                    | Cycle | Enforced at         |
|------------------------------------------------|-------|---------------------|
| Missing event_id                               | 10    | writer + concat     |
| Flat-string confidence                         | 10    | writer + concat     |
| Missing run_id                                 | 10    | writer + concat     |
| Long-form / decorated assessor                 | 10    | writer + concat     |
| Duplicate event_id (same file)                 | 10    | writer + concat     |
| Malformed clone JSON at merge                  | 12    | concat              |
| Per-milestone ts monotonicity violation        | 12    | concat              |
| Non-atomic merge on validation failure         | 12    | concat              |
| List-form `supersedes_path`                    | 14    | writer + pre-concat |
| Unknown `status` keyword                       | 14    | writer + pre-concat |
| Drift surfaced at fork boundary, not clone     | 14    | pre-concat helper   |

### Cycle-14 pattern lesson

Every cycle finds a new drift class the current SSoT validator does not
cover:

- Cycle 8: missing `event_id`, flat-string `confidence`.
- Cycles 10-11: writer-side hardening + concat-side gaps.
- Cycle 13: list-form `supersedes_path`, wrong-context `in-progress`.

This is not a failure of the validator — it is the healthy behavior of
a validator that improves with each retrospective. The observed pattern
is that **new drift classes tend to appear in optional or extension
fields the validator did not exercise**. A cycle-15 audit could
proactively enumerate every optional field the ledger accepts and
document its expected shape, so future drift is caught at ledger-schema
review time rather than at post-merge integration.

### Recommended cycle-15 work

1. **Full optional-field enumeration** — write an explicit shape spec
   for every extension field observed in the ledger (`supersedes`,
   `supersedes_path`, `reporter_mode`, `assessor_original`, `artifacts`,
   any others). Publish as a companion schema doc.
2. **State-transition validator** — the cycle-13 line-250 drift was a
   `validated → in-progress` edge without an intervening `reopened`.
   `promise_check` catches this at check time; hoisting it to the writer
   (with the shadow-ledger context reconstruction it requires) would
   close the gap. Non-trivial because clones don't have the main
   ledger's state graph while emitting.
3. **Drift-class enumeration doc** — a permanent record of every drift
   class caught across the campaign, indexed by cycle, so a cycle-N
   worker can grep for their own emission against the historical drift
   catalogue before shipping. This document is the seed of that record.

## Appendix A. Files changed

| File                                                                | Change                                                                    |
|---------------------------------------------------------------------|---------------------------------------------------------------------------|
| `long_exposure/tools/_ledger_schema.py`                             | Added `_STATUS_ENUM` alias; added `supersedes_path` type check.           |
| `long_exposure/workspace_bootstrap.py`                              | Added `_lint_clone_shadow(shadow_path)` importable helper.                |
| `tests/test_ledger_writer_validation.py`                            | +5 test cases (14–18); import `_STATUS_ENUM`.                             |
| `tests/test_fanout_concat_validation.py`                            | +3 test cases (11–13); import `_lint_clone_shadow`.                       |
| `tests/test_integration_cross_branch.py`                            | +§28 (7 checks) covering cycle-14 invariants.                             |
| `docs/ledger_schema_hardening_v2.md`                                | This document.                                                            |

## Appendix B. Test invocations

```
PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
    /usr/bin/python3 tests/test_ledger_writer_validation.py
    # 18/18 pass

PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
    /usr/bin/python3 tests/test_fanout_concat_validation.py
    # 13/13 pass

PYTHONPATH=. /usr/bin/python3 tests/test_integration_cross_branch.py
    # overall PASS (0 failures)

PYTHONPATH=.:/home/user/human-in-a-loop/long-exposure \
    /usr/bin/python3 -m long_exposure.tools.promise_check .
    # 0 ERRORs, WARN count matches pre-cycle-14 baseline (26)
```
