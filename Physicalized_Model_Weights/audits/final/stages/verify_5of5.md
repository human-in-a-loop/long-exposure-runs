# Final Audit Stage 6 - Verify 5/5

Generated: 2026-05-13T23:10:00Z
Run id: run-2026-05-13T015136Z
Stage: 6 of 12 (verify 5/5)

## Slice

- `M-ARCHIVE-1`
- `M-TOOLCHAIN-1`
- `M-INVARIANT-1`
- `M-PUBLICBASE-1`
- `M-PUBLICBASE-2`
- `M-PUBLICBASE-SYNTH-1`

## Ledger And Artifact Existence

| Milestone | Latest event | Status | Confidence | Artifacts | Missing |
|---|---|---|---|---:|---:|
| `M-ARCHIVE-1` | `5728e047-7d2f-4a02-8d42-3dca21a8ea69` | `validated` | `high` | 8 | 0 |
| `M-TOOLCHAIN-1` | `f6181068-1f23-4812-905d-d73d636711f6` | `validated` | `high` | 11 | 0 |
| `M-INVARIANT-1` | `8a7c8ed1-c2ab-4f5d-985f-47566aa9bc46` | `validated` | `high` | 6 | 0 |
| `M-PUBLICBASE-1` | `22d69644-f3ce-4059-8ad1-2542c33b7ac6` | `validated` | `high` | 7 | 0 |
| `M-PUBLICBASE-2` | `8fd4e2f6-f00c-4ad2-9c9f-7f24483590b0` | `validated` | `high` | 9 | 0 |
| `M-PUBLICBASE-SYNTH-1` | `95e2cd5d-5bfc-4c0a-9659-7a7c60b24bc1` | `validated` | `high` | 10 | 0 |

No low, provisional, medium, or non-validated terminal events exist in this slice. `M-INVARIANT-1`, `M-PUBLICBASE-1`, `M-PUBLICBASE-2`, and `M-PUBLICBASE-SYNTH-1` have earlier high-confidence worker validations followed by high-confidence auditor validations; the latest auditor events are the terminal records used here.

## Evidence Support

### `M-ARCHIVE-1`

Supported. `physicalized-weights/data/closure_archive_summary.json` reports:

- `canonical_artifact_count`: 54
- `missing_canonical_artifact_count`: 0
- `zero_size_canonical_artifact_count`: 0
- `closure_claim_support_count`: 16
- `current_superiority_claim_count`: 0
- `actual_reopen_candidate_count`: 0
- `new_reopen_gate_count`: 0
- `current_artifacts_reopen`: false

`physicalized-weights/docs/closure_archive_index.md` maps canonical endpoint artifacts to milestone owner, artifact class, size, SHA-256 hash, and regeneration command where available. The report explicitly states that the archive adds no model, reopen gate, synthetic evidence path, or current superiority claim.

### `M-TOOLCHAIN-1`

Supported. `physicalized-weights/data/toolchain_condition_summary.json` reports:

- Verilator lint passed.
- Yosys eval passed.
- Yosys synthesis passed.
- Graphviz artifact checked.
- `compiled_verilator_status`: `blocked_environment`
- Missing compiled-simulation tools: `make`, `cxx_compiler`
- `current_superiority_claim_count`: 0
- `actual_reopen_candidate_count`: 0
- `new_reopen_gate_count`: 0

`physicalized-weights/docs/toolchain_condition_report.md` correctly treats compiled Verilator simulation as an environment-blocked strengthening path, not a prototype failure and not a performance/economic reopen path.

### `M-INVARIANT-1`

Supported. `physicalized-weights/data/campaign_invariant_summary.json` reports:

- `artifact_count_checked`: 17
- `json_artifact_count_checked`: 8
- `markdown_artifact_count_checked`: 9
- `contradiction_count`: 0
- `ambiguous_text_warning_count`: 7
- `missing_required_endpoint_field_count`: 0
- `current_superiority_claim_count`: 0
- `actual_reopen_candidate_count`: 0
- `new_reopen_gate_count`: 0
- `current_artifacts_reopen`: false
- `introduced_new_gate`: false

`physicalized-weights/docs/campaign_invariant_report.md` classifies ambiguous prose as warning-level only and records no machine-readable endpoint contradictions.

### `M-PUBLICBASE-1`

Supported. `physicalized-weights/data/public_baseline_recency_summary.json` reports:

- `latest_mlperf_inference_release`: `MLPerf Inference v6.0`
- `latest_mlperf_inference_publication_date`: `2026-04-01`
- `primary_source_count`: 4
- `machine_readable_primary_source_count`: 3
- `material_public_baseline_update_count`: 3
- `model_refresh_recommended`: true
- `refresh_scope`: future programmable-baseline prior refresh only
- `public_sources_reopen_physicalized_claim`: false
- `phase2_conclusion_preserved`: true
- `phase4_reopen_path_satisfied`: false
- endpoint counters remain zero/false

`physicalized-weights/docs/public_baseline_recency_report.md` distinguishes official MLCommons sources from vendor context and explicitly states that public benchmark updates are not measured hybrid production, shadow, or canary evidence.

### `M-PUBLICBASE-2`

Supported. `physicalized-weights/data/public_baseline_prior_refresh_summary.json` reports:

- `raw_primary_rows_available`: 520
- `primary_mlcommons_rows_ingested`: 12
- `throughput_prior_rows`: 12
- `direct_energy_calibration_rows`: 0
- `safety_filter_direct_workload_rows`: 0
- `energy_values_inferred_from_throughput_only`: 0
- `vendor_secondary_rows_used_for_primary_calibration`: 0
- `refresh_decision`: `strengthen_programmable_null`
- `programmable_null_effect`: `strengthened_or_preserved`
- `phase2_downgrade_preserved`: true
- endpoint counters remain zero/false

`physicalized-weights/docs/public_baseline_prior_refresh.md` preserves the required non-mapping boundary: MLPerf throughput rows are bounded public programmable-baseline priors only, not identical safety-filter workload accounting, direct energy calibration, or lifecycle-valid hybrid evidence.

### `M-PUBLICBASE-SYNTH-1`

Supported. `physicalized-weights/data/public_baseline_synthesis_summary.json` reports:

- integrated milestones: `M-PUBLICBASE-1`, `M-PUBLICBASE-2`, `M-CLOSURE-1`
- `public_baseline_refresh_integrated`: true
- `latest_mlperf_inference_release`: `MLPerf Inference v6.0`
- `primary_mlcommons_rows_ingested`: 12
- `throughput_prior_rows`: 12
- `direct_energy_calibration_rows`: 0
- `safety_filter_direct_workload_rows`: 0
- `programmable_null_effect`: `strengthened_or_preserved`
- `phase2_downgrade_preserved`: true
- `phase4_reopen_condition_unchanged`: true
- `public_sources_reopen_physicalized_claim`: false
- endpoint counters remain zero/false

`physicalized-weights/docs/public_baseline_refresh_synthesis.md` integrates the public-baseline recency and prior-refresh work into the canonical record while preserving the unchanged Phase 4 future reopen condition.

## Tests Run

Focused tests for this slice:

- `python3 physicalized-weights/tests/test_closure_archive_index.py` passed.
- `python3 physicalized-weights/tests/test_toolchain_condition_probe.py` passed.
- `python3 physicalized-weights/tests/test_campaign_invariant_checker.py` passed.
- `python3 physicalized-weights/tests/test_public_baseline_recency_probe.py` passed.
- `python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py` passed.
- `python3 physicalized-weights/tests/test_public_baseline_synthesis.py` passed.

These tests regenerated their normal CSV, JSON, PNG, and documentation artifacts as part of verification. No source or artifact repair was intentionally made by the final auditor.

Adjacent check:

- `python3 physicalized-weights/tests/test_final_synthesis.py` still exits 1 in `test_artifact_hashes_are_current`.
- Direct recomputation of `physicalized-weights/data/evidence_manifest.csv` found the same four stale `M-FINAL-1` rows already recorded in the Stage 2 MODERATE finding:
  - row 3, `REFERENCES.md`
  - row 4, `physicalized-weights/docs/final_synthesis.md`
  - row 21, duplicate `physicalized-weights/docs/final_synthesis.md`
  - row 24, `physicalized-weights/docs/reproducibility.md`
- No stale evidence-manifest row is labeled with a Stage 6 milestone, so this stage appends no duplicate finding.

## Findings

- CRITICAL: 0
- MODERATE: 0 new
- MINOR: 0 new

The existing MODERATE `M-FINAL-1` stale evidence-manifest finding remains carried forward as residual debt.

