<!--
created: 2026-08-28T16:00:00Z
cycle: 15
run_id: run-2026-08-28T040704Z
agent: worker
milestone: _infra/ledger-schema-hardening-v3
-->

# Ledger Schema Hardening v3 — per-milestone state-transition validator

**Cycle:** 15
**Branch:** clone-0 of fork `392503ab7d47`
**Milestone:** `_infra/ledger-schema-hardening-v3`
**Status:** validated/high

## 1. The 4-cycle hardening arc

The single-source-of-truth (SSoT) ledger validator now spans four
distinct drift surfaces, each closed in its own cycle:

| Cycle | Milestone                                | Gate closed                                                                                                     |
|-------|------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| 10    | `_infra/ledger-schema-hardening`         | **Writer** — SSoT `validate_event` extracted; `append_ledger_event` validates + auto-fills UUID5 event_id; rejects cycles-7/8/9 drift (missing event_id, flat-string confidence, long-form assessor). |
| 12    | `_infra/fanout-concat-hardening`         | **Concat** — `concat_clone_ledgers` runs `validate_event` per candidate row; per-milestone ts monotonicity within candidate stream; SHA-256 content-hash tiebreak; atomic write via `os.replace`; typed `LedgerConcatError`. |
| 14    | `_infra/ledger-schema-hardening-v2`      | **Field-type + enum** — `supersedes_path` must be `str`; `_STATUS_ENUM` alias; `_lint_clone_shadow` seam surfaces drift at the clone emit boundary before concat sees it. |
| 15    | `_infra/ledger-schema-hardening-v3`      | **State transitions** — canonical `_STATE_TRANSITIONS` graph + `validate_history(rows)` reject illegal consecutive per-milestone transitions at BOTH `append_ledger_event` (writer) and `_lint_clone_shadow` (pre-concat lint); wired into `promise_check._check_lifecycle` for the check-time surface too. |

The binding invariant across all four cycles: **every ledger event,
wherever written, merged, or audited, passes the same SSoT validation
surface before it settles into the main ledger.** Cycle 10 established
the writer boundary; cycle 12 extended it to the concat boundary; cycle
14 tightened the per-event field-type surface and exposed the pre-concat
lint helper; cycle 15 elevates the validation object from "one event at
a time" to "one milestone's history at a time" — closing the class of
drift where each individual event is well-formed but the CONSECUTIVE
transition between them is illegal.

## 2. The cycle-13 line-250 root cause

Cycle 13 surfaced a `validated → in-progress` row for milestone
`M-RULES-1` on line 250 of the post-merge main ledger, with no
intervening `reopened` event. Cycle-14 clone-0 initially triaged this as
enum drift and shipped an enum check that ships a status-vocabulary
guard rail (still catches unknown values like `wobble`). That triage
was honestly re-classified in cycle-14's §2b as **wrong**: the
individual row's `status` field was in the canonical enum
(`"in-progress"`); the DRIFT was the transition FROM the prior row.

Cycle 14 explicitly hoisted this class — per-milestone state-transition
drift — to cycle-15's handoff. This cycle closes it.

## 3. Deliverables

### 3.1 `long_exposure/tools/_ledger_schema.py` — additive

Two module-top-level additions, no changes to existing symbols:

```python
_STATE_TRANSITIONS: frozenset[tuple[str, str]] = frozenset({
    # brief-specified transitions
    ("not-started", "in-progress"),
    ("in-progress", "validated"),
    ("in-progress", "invalidated"),
    ("validated", "reopened"),
    ("invalidated", "reopened"),
    ("reopened", "in-progress"),
    ("reopened", "validated"),
    ("reopened", "invalidated"),
    ("validated", "superseded"),
    ("deferred", "in-progress"),
    ("in-progress", "deferred"),
    ("action_required", "in-progress"),
    ("in-progress", "action_required"),
    # historical self-loops (observed in the 301-row sweep, legitimate)
    ("validated", "validated"),
    ("in-progress", "in-progress"),
})

def validate_history(rows: Iterable[dict]) -> list[str]:
    """Group rows by milestone_id, sort each group by ts, and return
    specific error strings for every illegal consecutive
    (prev_status, next_status) transition, using _STATE_TRANSITIONS as
    the ground-truth graph. Never raises on malformed input."""
```

The error message shape follows the brief's contract:

> `<milestone_id>: illegal transition <prev> -> <next> between event`
> `<eid_prev> (ts=<ts_prev>) and event <eid_next> (ts=<ts_next>) —`
> `not in _STATE_TRANSITIONS`

### 3.2 `workspace_bootstrap.py` — writer + lint seam wired

`append_ledger_event` — after the per-event `validate_event` pass and
the duplicate-event_id guard, reads the resolved ledger for prior rows
with the same `milestone_id`, splices the candidate onto that history,
and runs `validate_history`. Failure raises `LedgerAppendError` BEFORE
the file is opened for write — atomicity preserved.

`_lint_clone_shadow` — after the per-row `validate_event` pass, runs
`validate_history` over the whole collected shadow. Failure raises
`LedgerConcatError` naming the shadow path, the milestone, and the
(prev_status, next_status) pair.

Public API of both callables unchanged: same names, same signatures,
same return types, same raised exception types.

### 3.3 `long_exposure/tools/promise_check.py` — check-time surface

`_check_lifecycle` retains its hand-coded `validated → in-progress`
rule for backward compatibility, then defers to `validate_history`
for the full transition graph. On the clean 301-row ledger both
return empty; on a drifted ledger the hand-coded rule and
`validate_history` message the same finding via two channels — a
strict improvement in auditor triage.

## 4. Proof points

### (a) All 301 existing per-milestone histories validate

Ran `tools/_v3_sweep.py` (workspace-scoped one-shot) over the frozen
301-row main ledger:

```
total events: 301
distinct milestones: 207
First-status distribution: {'in-progress': 31, 'validated': 176}
Distinct consecutive transitions: 7
  'validated'   -> 'validated'    count=54
  'in-progress' -> 'validated'    count=29
  'in-progress' -> 'in-progress'  count=3
  'validated'   -> 'reopened'     count=3
  'reopened'    -> 'in-progress'  count=2
  'in-progress' -> 'invalidated'  count=2
  'reopened'    -> 'validated'    count=1

validate_history on 301-row ledger: 0 errors
```

The observed set is a proper subset of `_STATE_TRANSITIONS` (15 legal
pairs; 7 exercised by the historical corpus). No grandfathering was
required — the graph was drafted to cover both the brief's proposed
transitions AND the two legitimate historical self-loops
(`validated → validated` parent rollup, `in-progress → in-progress`
progress-note update), following the same "expand-when-legitimate"
escape hatch cycle 14 used for `STATUS_VALUES`.

### (b) Cycle-13 line-250 pattern rejects at BOTH writer + pre-concat lint

**Writer surface** (test_19):

```
LedgerAppendError:
ledger event history validation failed on 1 transition(s):
M-C15-1/writer: illegal transition 'validated' -> 'in-progress'
between event '<uuid_1>' (ts='2026-08-28T12:00:00Z') and event
'<uuid_2>' (ts='2026-08-28T13:00:00Z') — not in _STATE_TRANSITIONS
```

Only the first (well-formed) event lands; the file has exactly 1 line
after the rejection — atomicity confirmed.

**Pre-concat lint surface** (test_14 concat):

```
LedgerConcatError:
/tmp/concat_test_.../fork/clone-0/promise_ledger.jsonl:
per-milestone transition validation failed on 1 transition(s):
M-C15CONCAT-1: illegal transition 'validated' -> 'in-progress'
between event '...' (ts=...) and event '...' (ts=...) —
not in _STATE_TRANSITIONS
```

Reopen-bridged case (validated → reopened → in-progress) is accepted at
both surfaces (tests 20 and 15).

### (c) Existing suites remain green

| Suite                                              | Before | After  | Status |
|----------------------------------------------------|--------|--------|--------|
| `tests/test_ledger_writer_validation.py`           | 18     | 21     | 21/21 pass |
| `tests/test_fanout_concat_validation.py`           | 13     | 15     | 15/15 pass |
| `tests/test_integration_cross_branch.py` (§1–§30)  | pass   | pass   | 0 failures |
| `promise_check .` on the 301-row ledger            | 0 ERRs | 0 ERRs | unchanged |

### (d) Public API of `append_ledger_event` and `concat_clone_ledgers` unchanged

- `append_ledger_event(workspace: Path, event: dict) -> None` — same
  signature, same exception type (`LedgerAppendError`), same
  atomicity contract. Only the set of REJECTED events grew.
- `concat_clone_ledgers(workspace: Path, fork_dir: Path) -> int` —
  same signature, same return type, same exception type
  (`LedgerConcatError`). Concat itself is NOT modified in cycle 15;
  transition validation lives in `_lint_clone_shadow`, which the
  fanout conductor invokes on each shadow before calling concat.
  Direct test-time invocation of concat over an unlinted shadow with
  a transition drift will NOT raise — this preserves the cycle-14
  design that shadows lint FIRST and concat MERGES only clean
  shadows. Callers relying on `_lint_clone_shadow` → concat retain
  full transition coverage; callers bypassing lint are unchanged.
- The pre-concat lint helper `_lint_clone_shadow(shadow_path: Path)`
  had its behavior EXTENDED (adds transition sweep) but its signature
  is unchanged.

## 5. New test cases added

### `tests/test_ledger_writer_validation.py` (+3 cases, 18 → 21)

- **19** — `test_transition_validated_to_in_progress_rejected`: writes
  a `validated` event then attempts `in-progress` for the same
  milestone with no intervening `reopened`; asserts
  `LedgerAppendError` names milestone_id + both event_ids + transition
  pair, and that only the first row landed (atomicity).
- **20** — `test_transition_reopened_bridge_accepted`: writes
  `validated` → `reopened` → `in-progress` and asserts all three
  appends succeed; final ledger has 3 lines.
- **21** — `test_state_transitions_frozenset_shape`: shape invariants
  on `_STATE_TRANSITIONS` (frozenset of 2-tuples, each side in
  `STATUS_VALUES`); brief-specified core transitions all present;
  `("validated", "in-progress")` NOT in the frozenset; `validate_history`
  returns `[]` for the frozen 301-row ledger.

### `tests/test_fanout_concat_validation.py` (+2 cases, 13 → 15)

- **14** — `test_transition_within_shadow_rejected`: single clone
  shadow with `validated` then `in-progress` for the same milestone;
  asserts `_lint_clone_shadow` raises `LedgerConcatError` naming
  shadow path, milestone, transition pair, and the SSoT graph.
- **15** — `test_multi_milestone_shadow_with_reopen_bridge`: positive
  control — one milestone with a full reopen protocol
  (in-progress → validated → reopened → in-progress → validated) and
  another with a parent-rollup self-loop (validated → validated);
  lints clean, merges 7 rows, and concat is byte-idempotent across
  two runs.

Both test files carry the mandatory `_LE_PARENT` sys.path shim
(`/home/user/human-in-a-loop/long-exposure`) required for the
documented `PYTHONPATH=. /usr/bin/python3 tests/…` invocation flavor.

## 6. What cycle 15 does NOT change

- The rules ledger (`data/rules/ledger.jsonl`) and its
  `M-RULES-1/schema/*` validators are untouched — those are a
  domain-specific artifact separate from the promise ledger.
- The workspace bootstrap flow, `resolve_ledger_path` routing, and the
  clone/shadow directory layout are untouched.
- `content_hash_event_id`, `content_hash_tiebreak`, `canonical_json`,
  `validate_event`, `LedgerAppendError`, `LedgerConcatError` all
  preserve their cycle-10/12/14 contracts byte-for-byte.
- `concat_clone_ledgers` public behavior is unchanged. The transition
  check is added at the pre-concat lint boundary (`_lint_clone_shadow`),
  not inside concat itself, matching cycle-14's design principle
  that concat merges clean shadows and lint is the emit-boundary
  surface.

## 7. Handoff to cycle 16

Two follow-ups the cycle-15 clone-0 investigator surfaces but does not
attempt in scope:

1. **`concat_clone_ledgers` transition sweep**: currently rely on the
   fanout conductor to invoke `_lint_clone_shadow` on each shadow BEFORE
   calling concat. If a future caller path bypasses lint, transition
   drift could still land in the main ledger. A defense-in-depth pass
   would add `validate_history` at concat time too (over the merged
   candidate + main view). Deferred because it requires changing
   concat's public behavior surface — merits its own cycle.
2. **Drift-class enumeration index**: cycles 10 / 12 / 14 / 15 have
   each closed a distinct drift class (missing field / flat-string
   confidence / field-type-shape / illegal transition). An
   `_INFRA_DRIFT_CLASSES` frozenset naming each class with its
   representative test would make future audits' cross-cycle triage
   O(1). Deferred as pure documentation work.

## 8. Files touched

| Path                                                                                | Owner       | Change                              |
|-------------------------------------------------------------------------------------|-------------|-------------------------------------|
| `/home/user/human-in-a-loop/long-exposure/long_exposure/tools/_ledger_schema.py`    | upstream    | +`_STATE_TRANSITIONS`, +`validate_history` (additive; existing symbols byte-identical) |
| `/home/user/human-in-a-loop/long-exposure/long_exposure/workspace_bootstrap.py`     | upstream    | +`_existing_rows_for_milestone`; writer + `_lint_clone_shadow` invoke `validate_history`; public API unchanged |
| `/home/user/human-in-a-loop/long-exposure/long_exposure/tools/promise_check.py`     | upstream    | +`validate_history` import + call in `_check_lifecycle`; existing hand-coded rule retained |
| `tests/test_ledger_writer_validation.py`                                            | workspace   | +3 cases (19/20/21); 18 → 21 pass    |
| `tests/test_fanout_concat_validation.py`                                            | workspace   | +2 cases (14/15); 13 → 15 pass       |
| `docs/ledger_schema_hardening_v3.md`                                                | workspace   | this document                        |
| `tools/_v3_sweep.py`, `tools/_v3_smoke.py`, `tools/_v3_patch_*.py`                  | workspace   | one-shot scratch (archived to `tools/stale/` on integration) |
