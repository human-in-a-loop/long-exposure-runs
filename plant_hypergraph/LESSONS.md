# Cross-Cutting Lessons

Curated findings across runs. Updated by the final auditor at run end. The DB record (record_type='lesson') is canonical; this file mirrors for human readability.

---

## Lesson: delta-final-audit-status-taxonomy
*Committed: 2026-05-18T03:18:40.955454+00:00*

## Pattern observed

A delta final audit can have real artifacts and still fail closure because the status taxonomy is not ledger-consistent. In this PhytoGraph pass, Track 2, Track 4, Track 5, and Track 6 each had useful local outputs, but the final test stage observed `promise_check` red because new Wave 4 ledger rows used IDs such as `M4.V2`, `M4.V5`, and `M4.A-track5-duke-source-ablation` while `plan_of_record.md` defined aggregate rows like `M4.V1-V6` and `M4.A1-An`. That mismatch makes public closure fragile: a final report cannot honestly summarize plan adherence if some terminal evidence is attached to IDs the plan does not recognize.

## What works

Treat plan/ledger taxonomy as a first-class audit surface, not a formatting concern. During document-stage synthesis, map every finding to one of the unified statuses and preserve narrow validated states explicitly. For example, M3.T4 can be `validated` with `low` confidence as a data-limited, non-climate Crop Substitution Engine, while M4.V5 remains `action_required` because all temporal holdouts are data-limited and the no-Duke ablation collapses. This keeps useful partial work from being erased while preventing overclaiming.

Run validators before final reporting and quote the blocking class of failure in the audit record. If `promise_check` is red for undeclared milestone IDs, do not emit auditor reconciliation events that rewrite history. Instead, report the exact plan/ledger mismatch as residual debt and require a builder-owned plan amendment or event reclassification.

## What does not work

Do not let per-track convenience IDs silently appear after the plan has committed aggregate milestones. Do not treat a local artifact as terminal just because it exists: header-only master ledgers, missing Atlas generated outputs, and data-limited validation tables all need separate status treatment. Do not convert validator-red closure into a narrative success statement; the honest outcome is `action_required` until plan taxonomy and master-ledger reconciliation are fixed.

