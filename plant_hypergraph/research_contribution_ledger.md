---
created: 2026-05-18T14:45:00+00:00
cycle: 21
run_id: run-phytograph-cycle21-wave5-final-synthesis
agent: worker
milestone: M5.1
---

# Research Contribution Ledger: PhytoGraph

| Area | Artifact(s) | Classification | New vs integrated | Claim boundary |
|---|---|---|---|---|
| Schema and source audit | `phytograph_schema.md`, `data_source_audit.md`, `risk_register.md` | new | New PhytoGraph schema/source-governance layer | Freezes typed evidence permissions; does not validate predictions. |
| Substrate | `phytograph_dataset/`, `coverage_report.md`, `tools/validate_barrier1_substrate.py` | integrated | Integrates source staging into a canonical accepted-key substrate | Supports query and track enrichment; not a biological novelty claim. |
| Barrier 1 repair | Barrier 1 canonical-member repair artifacts and validator | formal/diagnostic | New repair of canonical-member projection before deduplication | Validates substrate mechanics, not track hypotheses. |
| Track 1 | `tracks/track1/track1_reticulation_atlas.md`, `tracks/track1/data/barrier4_canonical_key_recovery.tsv`, `tracks/track1/reports/track1_barrier4_closure.md`, `tracks/track1/reports/track1_free_tier_control_strengthening.md` | sidecar-readiness/uncontrolled | New reticulation instrument and closure diagnosis | `sidecar_readiness_uncontrolled`; 22 GBIF sidecar event taxa across 11 source groups, but WFO projection is 2 taxa and source-density controls remain unresolved. |
| Track 2 | `tracks/track2/track2_ghost_hyperedges.md`, `tracks/track2/data/track2_wave4_validation_outcomes.tsv`, `tracks/track2/reports/track2_wave4_validation_closure.md`, `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md` | falsification/data-limited | New ghost-partner ranker, held-out validation scaffold, and free-tier closure controls | `H2_remains_not_supported_or_data_limited`; 0/8 canonical held-outs pass the validation contract. |
| Track 3 | `tracks/track3/track3_convergence_pressure.md`, `tracks/track3/data/track3_wave4_validation_summary.json`, `tracks/track3/reports/track3_wave4_validation_ablation.md`, `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md` | confound-limited/formal diagnostic | New convergence-pressure statistic, confound accounting, and free-tier trait matrix | `confound_limited`; 0 controlled-ready traits across 3,069 accepted-key carrier rows. |
| Track 4 | `tracks/track4/track4_domestication_hypergraph.md`, `tracks/track4/data/crop_substitution_candidates.tsv`, `tracks/track4/reports/track4_barrier4_closure.md`, `tracks/track4/reports/track4_free_tier_bioclim_recovery.md` | data-limited | New crop-substitution engine scaffold using retained pedigree/CWR evidence | `still_data_limited`; 3,358 post-filter occurrence records, 0 numeric BIOCLIM vectors, and 0 validation-allowed comparator rows. |
| Track 5 | `tracks/track5/track5_chemodiversity.md`, `tracks/track5/data/track5_wave4_validation_outcomes.tsv`, `tracks/track5/reports/track5_wave4_temporal_source_closure.md`, `tracks/track5/reports/track5_free_tier_non_duke_temporal_chemistry.md` | source-biased/falsification | New temporal validation and Duke/source ablation | `H5_remains_source_biased`; non-Duke temporal evidence is insufficient and no validation-ready structured family/class stratum exists. |
| Track 6 | `tracks/track6/track6_foundation_model_probe.md`, `tracks/track6/data/probe_results.tsv`, `tracks/track6/reports/track6_barrier4_closure.md`, `tracks/track6/reports/track6_reopen_local_model_execution.md` | environment-limited/benchmark | New static benchmark and deterministic scorer under free/open/local constraint | `environment_limited_untested`; 0 runnable local runtime-weight pairings, 0 executed responses, and 0 scored responses. |
| Atlas | `botanical_atlas_site/`, `atlas_runbook.md`, `reports/barrier3_atlas_instrument_readiness.md` | atlas/infrastructure | Integrated all track outputs into a researcher-facing surface | Displays evidence and priors; does not establish predictions. |
| Barrier 4 integration | `reports/wave4_postmerge_integration.md`, `reports/barrier4_closure_integration.md` | integrated | New master-level reconciliation of Track 1-6 closures | Keeps master ledgers header-only. |
| Post-reopen closure | `reports/reopen/reopen_closure_addendum.md`, `data/reopen/reopen_closure_status.tsv`, `reports/reopen/figures/reopen_branch_outcomes.png` | validated null/non-promotion | New final reconciliation of validated reopen branches for Tracks 1, 4, 5, and 6 | Documents exact missing predicates and keeps master ledgers header-only. |
| Free-tier recovery integration | `reports/reopen/free_tier_recovery_integration.md`, Track 1/4/5 free-tier branch reports, `tests/test_free_tier_recovery_integration.py` | integrated/reconciliation-pending | Integrates fork `5fe97ebd91d9` branch results into the closure matrix | Track 1 threshold is branch-local pending GBIF/WFO namespace reconciliation; Tracks 4/5 remain non-promotional. |
| Track 2/3 free-tier closure integration | `reports/reopen/free_tier_track2_track3_closure_integration.md`, `reports/fork_2f05eabe3800_postmerge_integration.md`, `tests/test_free_tier_track2_track3_closure_integration.py` | validated null/confound-limited non-promotion | Integrates fork `2f05eabe3800` Track 2/3 branch outcomes into master closure artifacts | Track 2 remains H2-not-supported/data-limited; Track 3 remains confound-limited; no master ledger rows. |
| Final free-tier closure synthesis | `reports/reopen/final_free_tier_closure_synthesis.md`, `data/reopen/final_free_tier_track_status.tsv`, `reports/reopen/figures/final_free_tier_track_status.png`, `tests/test_final_free_tier_closure_synthesis.py` | integrated/null-source-bias-environment closure | New six-track final free-tier status layer | All six tracks have conservative closure statuses; original validated-prediction-per-track criterion remains unmet; master ledgers remain header-only. |
| Final synthesis | `final_report.md`, `audit_report.md`, `artifact_index.md`, `falsification_and_ablation_report.md` | integrated | New PhytoGraph-specific Wave 5 closure package | Candidly records unmet success criterion and reopen conditions. |

## Per-Track Novelty Summary

- Track 1 is new as an instrument and diagnostic. Its final free-tier status is
  `sidecar_readiness_uncontrolled`: 22 GBIF sidecar event taxa across 11 source
  groups are retained, but WFO projection is 2 taxa and source-density controls
  remain unresolved.
- Track 2 is new as a ranker and validation scaffold; its headline hypothesis
  is not supported/data-limited after 0/8 canonical free-tier held-outs passed
  the validation contract.
- Track 3 is new as a statistic/confound framework; its current predictions are
  `confound_limited` after 0 controlled-ready traits across 3,069 accepted-key
  trait carrier rows.
- Track 4 is new as a queryable scaffold; `still_data_limited` means
  climate-substitution claims are blocked by 0 numeric BIOCLIM vectors and 0
  validation-allowed comparator rows.
- Track 5 is new as a source-bias falsification result more than as a predictor.
- Track 6 is new as an offline benchmark/scorer; `environment_limited_untested`
  means model execution is not yet available.

## Master Ledger Position

No major contribution is recorded as a validated master biological prediction.
The master `prediction_ledger.tsv` and `speculation_ledger.tsv` remain
header-only by design. The post-reopen and free-tier integration addenda confirm
this remains a non-promotion result: Track 1 is
`sidecar_readiness_uncontrolled`, Track 2 is
`H2_remains_not_supported_or_data_limited`, Track 3 is `confound_limited`,
Track 4 is `still_data_limited`, Track 5 is `H5_remains_source_biased`, and
Track 6 is `environment_limited_untested`.
