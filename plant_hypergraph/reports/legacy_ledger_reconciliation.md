---
created: 2026-05-17T17:55:36.737311+00:00
cycle: 2
run_id: fork-e34b5b2c1c6c-clone-5
agent: worker
milestone: _manager/ledger-integrity
---

# Legacy Ledger Reconciliation

This reconciliation classifies the current `promise_check` output after the PhytoGraph pivot. It does not rewrite, delete, or alter historical `promise_ledger.jsonl` lines.

## Summary

- `promise_check` exit code: `0`
- Parsed validator rows: 123
- Severity counts: {'warning': 123}
- Classification counts: {'legacy_prior_campaign': 63, 'active_phytograph': 42, 'manager_artifact': 18}
- M1.1 ledger status: `validated`
- M1.7 ledger status: `validated`
- M1.7 warning/error mentions: 0
- M1.1 warning/error mentions: 0

## Classification Rule

Pre-pivot bare milestone IDs `M1` through `M8` are classified as `legacy_prior_campaign` because the active PhytoGraph plan uses IDs such as `M0.1`, `M1.1`, and `M1.7`. Prior-cycle report/final artifacts and the old public-taxonomy sample are also legacy. Manager assessment paths and validator bookkeeping rows are `manager_artifact`. Current or pending PhytoGraph milestone/path rows are `active_phytograph`; these are warnings about unfinished sibling work or future waves unless they name a validated M1.1/M1.7 artifact.

## Findings

The current `promise_check` run has no hard errors. Former hard-error noise from bare `M1`-`M8` prior-campaign entries has been reduced to classified warning-level legacy and manager bookkeeping rows.

No current `promise_check` warning or error names an M1.7 chemodiversity/handoff artifact. M1.1 and M1.7 remain validated in the ledger, so Barrier 1 can treat future M1.1/M1.7 warnings as new defects rather than inherited ledger noise.

The remaining active-PhytoGraph warnings are pending/future milestones with no events yet, plus sibling-clone artifacts outside clone 5 ownership. The reconciliation does not mark those complete.

## Outputs

- TSV: `reports/legacy_ledger_reconciliation.tsv`
- Validator capture: `reports/legacy_promise_check_after.txt`

## Unknown Rows

No rows were left unclassified.
