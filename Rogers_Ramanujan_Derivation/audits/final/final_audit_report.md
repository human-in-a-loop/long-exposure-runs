---
title: "Final Audit Report"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Final Audit Report

Run id: run-2026-05-14T232311Z
Document generated: 2026-05-15T13:26:26.155533+00:00

This final audit checked the run's structured commitments, ledger states, cited evidence files, closure artifacts, and validator outputs. It did not re-prove the mathematics independently; it verified that the public record supports the run's stated milestone outcomes and that computational checks are not presented as substitutes for proof.

## Status distribution

- validated: 5

## Plan adherence

| Milestone | Terminal status | Confidence | Evidence count | Latest evidence pointer |
|---|---:|---:|---:|---|
| M0 | validated | high | 2 | `docs/lemmas/lemma_catalogue.md` |
| M1 | validated | high | 6 | `scripts/rr/finite_rr_experiments.wls` |
| M2 | validated | high | 12 | `docs/proof/bailey_matrix_transform.md` |
| M3 | validated | high | 6 | `docs/proof/product_side.md` |
| M4 | validated | high | 8 | `docs/proof/final_proof.md` |

All five plan milestones M0-M4 are latest-state `validated/high`. Stage verification confirmed that the cited evidence files exist and support the corresponding record: formal setup and validation separation for M0, finite experiment harness for M1, derived Bailey-style transfer mechanism for M2, product-side formalization for M3, and final proof synthesis plus validation separation for M4.

Key proof and validation documents present:
- `docs/lemmas/lemma_catalogue.md`: present
- `docs/proof/bailey_matrix_transform.md`: present
- `docs/proof/product_side.md`: present
- `docs/proof/final_proof.md`: present
- `docs/validation.md`: present

## Confidence calibration

- validated/high: 5
- validated/medium: 0
- validated/low: 0
- validated/provisional: 0
- Low-confidence terminal states: none

The high-confidence terminal states are supported by the ledger artifacts and by two adversarial test passes. The validation record keeps coefficient and residual checks in a discovery/regression role rather than using them as proof.

## Residual debt

- `_run/start` (nonterminal-ledger-state): Latest ledger state is in-progress/high. This is bookkeeping debt rather than a proof defect for plan milestones M0-M4.

No residual debt affects the validated status of M0-M4. The remaining item is a run-state bookkeeping marker.

## Findings by severity

- CRITICAL: 0
- MODERATE: 0
- MINOR: 0

No final-audit findings remain. Earlier verifier false positives were removed before this document stage because they came from audit-script parsing and evidence-classification mistakes, not from run defects.

## Future work

- Anchored to `_run/start`: Close or supersede the run-start bookkeeping entry when the final audit artifacts are committed, so terminal reports do not retain an in-progress run marker.

## Reconciliation log

- None. No `_plan/`, `_archive/`, or correction events are proposed by the final audit.

## Validator and coverage notes

- promise_check: green
- org_check: green
- Stage files present: 5 / 5
- Figure coverage: 9 figure files present, 9 referenced by ledger, 0 missing, 0 orphaned.
