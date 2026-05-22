---
created: 2026-05-18T14:45:00+00:00
cycle: 21
run_id: run-phytograph-cycle21-wave5-final-synthesis
agent: worker
milestone: M5.1
---

# Artifact Index: PhytoGraph

## Wave 0: Scope, Schema, Source Audit

- `plan_of_record.md`: PhytoGraph goals, milestones, legacy disposition, and Wave 0-5 structure.
- `phytograph_schema.md`: frozen hypergraph schema v1.0.
- `data_source_audit.md`: source audit with licenses, access mode, reliability, bias, bulk-scale support, and track use.
- `coverage_report.md`: tier coverage and source-branch status.
- `risk_register.md`: licensing, source-bias, inference, API-cost, paleobotany, and ethnobotany risks.
- `docs/prior_campaign_kernel.md`: retained kernel from the superseded plant-taxonomy campaign.

## Wave 1: Substrate Ingestion And Barrier 1

- `phytograph_dataset/`: typed substrate tables and provenance.
- `tools/validate_barrier1_substrate.py`: Barrier 1 validator.
- `data/source_branch_disposition_m1_3_m1_6.tsv`: terminal source-branch disposition for M1.3 and M1.6.
- `reports/source_branch_disposition_m1_3_m1_6.md`: source-branch lifecycle closure.
- Barrier 1 repair artifacts referenced by `promise_ledger.jsonl` under `_plan/barrier1-canonical-member-repair`.

## Wave 2: Track Enrichment And Barrier 2

- `tools/validate_barrier2_track_enrichment.py`: track enrichment conformance validator.
- `data/barrier2_track_enrichment_conformance.json`: current conformance output.
- `reports/barrier2_wave2_integration_report.md`: Wave 2 post-merge integration report.
- Track namespaces under `tracks/track1/` through `tracks/track6/`: track-local enrichment data, scripts, reports, and tests.

## Wave 3: Instruments And Atlas

- `tracks/track1/track1_reticulation_atlas.md`: Track 1 instrument report.
- `tracks/track2/track2_ghost_hyperedges.md`: Track 2 ranker report.
- `tracks/track3/track3_convergence_pressure.md`: Track 3 statistic report.
- `tracks/track4/track4_domestication_hypergraph.md`: Track 4 crop-substitution engine report.
- `tracks/track5/track5_chemodiversity.md`: Track 5 chemodiversity predictor report.
- `tracks/track6/track6_foundation_model_probe.md`: Track 6 offline probe report.
- `botanical_atlas_site/`: local Atlas site output.
- `atlas_runbook.md`: Atlas runbook.
- `reports/barrier3_atlas_instrument_readiness.md`: Barrier 3 readiness package.
- `tools/validate_barrier3_atlas_integration.py`: Barrier 3 validator.

## Wave 4: Validation, Ablation, Closure

- `reports/wave4_postmerge_integration.md`: Track 2/3/5 validation and ablation integration.
- `tests/test_wave4_postmerge_integration.py`: integration regression test.
- `reports/barrier4_closure_integration.md`: Track 1/4/6 closure integration.
- `tests/test_barrier4_closure_integration.py`: closure integration regression test.
- `reports/reopen/reopen_evidence_gate.md`: mechanical reopen predicates for Track 1/4/5/6.
- `reports/reopen/reopen_closure_addendum.md`: post-reopen closure reconciliation across all validated reopen branches.
- `reports/reopen/free_tier_recovery_integration.md`: cycle 28 integration of Track 1/4/5 free-tier recovery branches.
- `reports/reopen/free_tier_track2_track3_closure_integration.md`: fork `2f05eabe3800` Track 2/3 free-tier closure reconciliation.
- `reports/reopen/final_free_tier_closure_synthesis.md`: final six-track free-tier closure synthesis.
- `data/reopen/reopen_closure_status.tsv`: machine-readable branch outcome table.
- `data/reopen/final_free_tier_track_status.tsv`: canonical final free-tier status table with one row per track.
- `reports/reopen/figures/reopen_branch_outcomes.png`: validated reopen branch outcome figure.
- `reports/reopen/figures/final_free_tier_track_status.png`: final six-track status figure.
- `reports/reopen/scripts/build_final_free_tier_closure_synthesis.py`: generator for the final status TSV, report, and figure.
- `tests/test_reopen_closure_addendum.py`: post-reopen closure regression test.
- `tests/test_free_tier_recovery_integration.py`: cycle 28 free-tier branch integration regression test.
- `tests/test_free_tier_track2_track3_closure_integration.py`: Track 2/3 free-tier closure integration regression test.
- `tests/test_final_free_tier_closure_synthesis.py`: final six-track free-tier synthesis regression test.
- `tracks/track1/reports/track1_barrier4_closure.md`: Track 1 closure/refinement report.
- `tracks/track1/reports/track1_reopen_reticulation_evidence.md`: Track 1 accepted-key reticulation reopen branch.
- `tracks/track1/reports/track1_free_tier_reticulation_recovery.md`: Track 1 free-tier GBIF-keyed reticulation recovery branch.
- `tracks/track1/data/barrier4_canonical_key_recovery.tsv`: Track 1 accepted-key recovery diagnosis.
- `tracks/track4/reports/track4_barrier4_closure.md`: Track 4 closure/refinement report.
- `tracks/track4/reports/track4_reopen_bioclim_validation_readiness.md`: Track 4 bioclim validation reopen branch.
- `tracks/track4/reports/track4_free_tier_bioclim_recovery.md`: Track 4 free-tier occurrence/BIOCLIM recovery branch.
- `tracks/track4/data/crop_substitution_engine_summary.json`: Track 4 summary.
- `tracks/track4/data/crop_substitution_candidates.tsv`: Track 4 local candidate-prior rows.
- `tracks/track6/reports/track6_barrier4_closure.md`: Track 6 closure/refinement report.
- `tracks/track6/reports/track6_reopen_local_model_execution.md`: Track 6 local/free/open model execution reopen branch.
- `tracks/track6/data/local_model_availability.json`: Track 6 local model availability.
- `tracks/track6/data/probe_model_summary.tsv`: Track 6 deterministic scorer summary.
- `tracks/track2/reports/track2_wave4_validation_closure.md`: Track 2 validation closure.
- `tracks/track2/reports/track2_free_tier_ghost_evidence_controls.md`: Track 2 free-tier ghost evidence/control closure branch.
- `tracks/track2/data/track2_free_tier_ghost_evidence_controls.tsv`: Track 2 free-tier control matrix.
- `tracks/track2/data/track2_wave4_validation_outcomes.tsv`: Track 2 held-out outcomes.
- `tracks/track3/reports/track3_wave4_validation_ablation.md`: Track 3 validation/ablation report.
- `tracks/track3/reports/track3_free_tier_trait_confound_matrix.md`: Track 3 free-tier trait/confound matrix report.
- `tracks/track3/data/track3_free_tier_trait_taxon_matrix.tsv`: Track 3 free-tier trait carrier matrix.
- `tracks/track3/data/track3_free_tier_trait_readiness.tsv`: Track 3 free-tier controlled-readiness table.
- `tracks/track3/data/track3_wave4_validation_summary.json`: Track 3 summary.
- `tracks/track5/reports/track5_wave4_temporal_source_closure.md`: Track 5 temporal/source closure.
- `tracks/track5/reports/track5_reopen_temporal_chemistry_evidence.md`: Track 5 non-Duke temporal chemistry reopen branch.
- `tracks/track5/reports/track5_free_tier_non_duke_temporal_chemistry.md`: Track 5 free-tier non-Duke temporal chemistry recovery branch.
- `tracks/track5/data/track5_wave4_validation_outcomes.tsv`: Track 5 temporal held-out outcomes.

## Wave 5: Final Synthesis

- `final_report.md`: PhytoGraph final report.
- `audit_report.md`: PhytoGraph audit report.
- `research_contribution_ledger.md`: contribution and claim-classification ledger.
- `artifact_index.md`: this artifact index.
- `falsification_and_ablation_report.md`: cross-track falsification, ablation, and closure accounting.

## Master Ledgers

- `promise_ledger.jsonl`: append-only promise and artifact ledger.
- `prediction_ledger.tsv`: header-only master prediction ledger.
- `speculation_ledger.tsv`: header-only master speculation ledger.

## Full Wave 5 Validation

```bash
python3 -m pytest -q tests/test_wave4_postmerge_integration.py tests/test_barrier4_closure_integration.py
python3 tools/validate_barrier3_atlas_integration.py
python3 tools/validate_barrier2_track_enrichment.py
python3 tools/validate_barrier1_substrate.py
python3 -m long_exposure.tools.promise_check <run-root>
python3 -m long_exposure.tools.org_check <run-root>
```

## Known Nonblocking Process Warnings

- Historical malformed ledger line 85 is covered by an immutable validator
  exception and must not be edited.
- Some prior ledger rows reference legacy or noncanonical paths from the
  superseded plant-taxonomy campaign.
- Root files remain present because they are required final deliverables.

## Cycle 28 Free-Tier Recovery Integration

The free-tier recovery integration in
`reports/reopen/free_tier_recovery_integration.md` reconciles fork
`5fe97ebd91d9` branch outputs. Track 1 now has a branch-local
`threshold_met` result with 22 distinct GBIF accepted-key event-shaped taxa, but
master-level promotion remains blocked pending WFO-namespace or sidecar
accepted-key reconciliation. Track 4 remains `still_data_limited` after
coordinate recovery because numeric BIOCLIM vectors and validation-allowed
comparator rows are both 0. Track 5 remains source-biased because two manual
accepted-key non-Duke detections do not form a structured family/class stratum.

## Track 2/3 Free-Tier Closure Integration

The closure integration in
`reports/reopen/free_tier_track2_track3_closure_integration.md` reconciles fork
`2f05eabe3800` branch outputs. Track 2 remains
`H2_remains_not_supported_or_data_limited` because 0/8 canonical held-outs pass
the validation contract. Track 3 remains `confound_limited` because
0 controlled-ready traits are present across 3,069 accepted-key trait carrier
rows. Both remain excluded from the master prediction and speculation ledgers.

## Final Free-Tier Closure Synthesis

The synthesis in `reports/reopen/final_free_tier_closure_synthesis.md`
consolidates every free-tier branch into exactly one final status per track:
Track 1 `sidecar_readiness_uncontrolled`, Track 2
`H2_remains_not_supported_or_data_limited`, Track 3 `confound_limited`, Track 4
`still_data_limited`, Track 5 `H5_remains_source_biased`, and Track 6
`environment_limited_untested`. The canonical table is
`data/reopen/final_free_tier_track_status.tsv`, and the figure is
`reports/reopen/figures/final_free_tier_track_status.png`. The tests enforce
that `prediction_ledger.tsv` and `speculation_ledger.tsv` remain header-only.
