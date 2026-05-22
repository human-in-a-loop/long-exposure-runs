---
created: 2026-05-18T11:00:00+00:00
cycle: 14
run_id: run-phytograph-cycle14-wave4-postmerge-integration
agent: worker
milestone: _plan/wave4-postmerge-integration
---

# Wave 4 Post-Merge Integration

## Scope

This integration cycle reconciles fork `cc044bf40be3` clone outputs for Track 2 validation closure, Track 3 convergence/confound handling, and Track 5 temporal/source closure. It does not start new research, refit instruments, fetch sources, perform audit-level validation, or promote rows into `prediction_ledger.tsv` or `speculation_ledger.tsv`.

## Integrated Outcomes

| Branch | Integrated artifact | Decision carried forward |
|---|---|---|
| Track 2 | `tracks/track2/reports/track2_wave4_validation_closure.md` | H2 is not supported at the 30% canonical recovery threshold under current accepted-key/source/living-megafauna controls: 0 validated, 1 falsified under ablation, 6 data-limited, 1 insufficient-support. |
| Track 3 | `tracks/track3/reports/track3_wave4_validation_ablation.md` | H3 remains data-limited; `drupe` and `capsule` are track-local pending convergence-prior rows only, with no master-ledger promotion. |
| Track 5 | `tracks/track5/reports/track5_wave4_temporal_source_closure.md` | H5 is not validated under frozen inputs; temporal holdouts have 0 top-decile recoveries, and the Duke/source ablation is a validated source-bias null result. |

## Reconciliation

The only integration mismatch was namespace drift for Track 3: the branch ledger used `_plan/wave4-track3-validation-ablation-branch` because `M4.A-track3-convergence-confounds` was not explicit in `plan_of_record.md`. This cycle adds that exact child milestone to the Wave 4 table and keeps the branch as track-local ablation evidence pending Barrier 4 reconciliation.

The Track 2, Track 3, and Track 5 packages agree on the important shared boundary: every branch records local validation or ablation outcomes, and none writes a validated biological prediction to the master ledgers. `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.

## Integration Checks

The focused integration test `tests/test_wave4_postmerge_integration.py` verifies branch outcome counts, Track 3 child milestone registration, non-promotion flags, Track 5 ablation counts, and header-only master ledgers. Barrier validators should be rerun after this report and ledger event are registered.
