# Fan-out launched-event convention (Cycle 35 codification)

## Rule (literal)

**A `_run/cycle_<N>_launched(-clone-<k>)?` ledger event MUST be emitted
with `status: "validated"` at emission time.**

Rationale: a launched event marks the *start-of-cycle* — the run began,
the plan is in the ledger, the worker/researcher has committed to the
scope. It is **not** an open piece of work whose truth conditions are
pending. Writing it as `status: "in-progress"` invites the ledger's
state machine (c29 lemma: no `validated → in_progress` transitions) to
treat the cycle itself as an in-flight promise, which it is not: the
cycle's substantive work lives in `M-*` and `_infra/*` milestones that
carry their own status transitions.

## Scope of the rule

- Applies to every `_run/cycle_<N>_launched` root-scope event and every
  per-clone `_run/cycle_<N>_launched-clone-<k>` fanout event.
- Does not apply to any other `_run/*` family label (e.g.
  `_run/cycle_<N>_closed`, `_run/report_cycles_<lo>-<hi>_*`,
  `_run/start`, `_run/post-merge-integration-*`); those carry their
  own semantics.
- Applies from cycle 35 onward. Pre-existing offender events (see
  below) are documented, not rewritten.

## Pre-existing offender list (pinned)

Six pre-c35 launched-event ledger rows carry `status: "in-progress"`.
They are documented at
`tests/fixtures/launched_event_offender_list_v1.txt` and the
`test_launched_event_convention.py` test asserts the offender set
does not grow after cycle 35. Rewriting historic ledger rows would
break the append-only invariant and is explicitly prohibited.

| Cycle | milestone_id                     | agent  | note                              |
|-------|----------------------------------|--------|-----------------------------------|
| 29    | `_run/cycle_29_launched`         | worker | pre-convention                    |
| 30    | `_run/cycle_30_launched`         | worker | pre-convention                    |
| 31    | `_run/cycle_31_launched`         | worker | pre-convention (root)             |
| 31    | `_run/cycle_31_launched-clone-1` | worker | pre-convention (fanout)           |
| 31    | `_run/cycle_31_launched-clone-2` | worker | pre-convention (fanout)           |
| 32    | `_run/cycle_32_launched`         | worker | pre-convention                    |
| 34    | `_run/cycle_34_launched-clone-0` | worker | asymmetric with clone-1, clone-2  |

The brief called out only the c34 clone-0 asymmetry; the actual
historical set is broader. The test pins the current set verbatim so
any future re-emission that drifts a c35+ event to `in-progress` is
caught as a growing offender list.

## Interaction with the c32/c33 fanout-namespace convention

The c32 convention (writer-enforced by c33's
`_infra/harness-clone-namespace-guard`) requires
`_run/*` labels a clone touches to be suffixed with `-clone-<k>`. That
convention is orthogonal to this one: the c32/c33 rule governs the
identifier suffix; this rule governs the `status` field. Both must
hold for a compliant launched-event emission.

## Enforcement

- `tests/test_launched_event_convention.py` (≥6 cases) enforces the
  rule at test time by scanning `promise_ledger.jsonl` for launched
  rows and cross-checking against the offender fixture.
- No writer-boundary enforcement is added in c35 — the c33 clone-guard
  chain already covers namespace suffixing; adding `status` gating at
  the writer would risk turning a documentation bug into a hard emit
  failure. Test-boundary enforcement is sufficient at this stage.

## Future work (deferred, not blocking)

- If a subsequent cycle observes an offender growth, the follow-up is a
  writer-boundary lint (analogous to c33's `_lint_clone_shadow`) rather
  than a ledger rewrite.
- If the campaign later chooses to normalize the historical offenders,
  that requires a dedicated `_manager/` triage cycle to weigh
  append-only preservation against schema uniformity; the c35 branch
  makes no such recommendation.
