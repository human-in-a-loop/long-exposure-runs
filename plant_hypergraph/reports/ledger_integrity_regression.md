---
created: 2026-05-17T22:10:00Z
cycle: 5
run_id: run-phytograph-cycle5-ledger-reconciliation
agent: worker
milestone: _manager/ledger-integrity-regression
---

# Ledger Integrity Regression

## Scope

This cycle reconciles ledger lifecycle integrity only. Barrier 1 substrate outputs, staged Wave 1 source artifacts, source evidence rows, and Wave 2 track work were held constant.

## Current Hard Errors

The required pre-check was run with:

```bash
python3 -m long_exposure.tools.promise_check <run-root> > reports/ledger_integrity_regression_promise_check_before.txt 2>&1
```

It exited 1 with two hard errors:

| Line | Finding | Classification | Disposition |
|---:|---|---|---|
| 85 | `event_id` is `auditor-closure-m18-clone6`, not a UUID. | Historical immutable data defect. | Cannot be repaired append-only because the validator checks every historical row's `event_id`; filed `reports/ledger_validator_exception_line85.md` and ledger-referenced it. |
| 99 | `M1.3` transitioned `validated -> in-progress` without `reopened`. | Active append-only lifecycle defect. | Repaired append-only by adding a `reopened` bridge event for `M1.3` with timestamp `2026-05-17T18:19:59Z`, immediately before the side-wave `in-progress` event at line 99 in validator sort order. |

## Prior Closure Failure

The previous `_manager/ledger-integrity` closure was insufficient because it addressed the earlier legacy milestone namespace problem, then marked the manager blocker `validated` while two newer deterministic hard errors remained in the root ledger state. It did not include an invariant requiring a fresh `promise_check` result after all root-ledger fan-out rows were merged. The corrective invariant is: `_manager/ledger-integrity*` may be marked `validated` only when the current root-workspace `promise_check` has zero hard errors, or when every remaining hard error is listed by exact line number in a validator exception artifact and a manager event remains `action_required` until the validator policy is updated.

## Current Manager / Action-Required State

Latest `_manager/ledger-integrity` before this cycle was `validated` at line 100, but that closure is superseded by this regression assessment because `reports/ledger_integrity_regression_promise_check_before.txt` still has hard errors.

Remaining latest `action_required` milestones before corrective appends:

| Milestone | Line | Reason |
|---|---:|---|
| `M1.9` | 109 | Wikidata/Commons dump-based recovery remains a late-arrival source-recovery branch. |
| `_plan/data-limited-status-vocabulary` | 102 | Ledger status vocabulary lacks an explicit `data-limited` state, forcing an `in-progress` plus rationale workaround. |

## Track 6 Scope Correction

The existing M1.8 paid-provider foundation-model harness is preserved only as a noncompliant cycle-2 artifact. Anthropic, OpenAI, Gemini, Pl@ntNet, iNaturalist paid or key-gated API execution, live smoke tests, key export, and `$500` cap planning are out of scope for this PhytoGraph run. Future Track 6 work must use static benchmark design, deterministic scoring, public/offline datasets, and local/open-weight models only when available without paid calls.

## After-Check Interpretation

The after-check is saved at `reports/ledger_integrity_regression_promise_check_after.txt`. It exits 1 with one remaining hard error:

```text
ledger:line 85: event_id is not a valid UUID
```

The line 99 lifecycle error is gone after the `M1.3` `reopened` bridge. Line 85 is covered by `reports/ledger_validator_exception_line85.md`; because that is an immutable historical data defect rather than a validator false positive, `_manager/ledger-integrity-regression` remains `action_required` until validator policy supports explicit historical exceptions.

During the after-check, `promise_check` also exposed a validator robustness defect: it crashed on list-valued `supersedes`, even though the append helper had accepted the event. The checker was minimally patched to normalize scalar and list `supersedes` values before membership checks, allowing the after-check to complete and report the remaining real hard error.
