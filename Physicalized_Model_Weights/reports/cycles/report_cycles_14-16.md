---
title: "Physicalized Model Weights - cycles 14-16"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 14-16

## Abstract

Cycles 14-16 converted the Phase 2 downgrade into a complete evidence gate for any future attempt to reopen the safety/filter physicalization performance claim. The prior conclusion remained unchanged: current modeled, proxy, and synthetic evidence does not show that the hybrid physicalized safety/filter path beats the stronger programmable accelerator baseline.

The new work defined three linked controls. Cycle 14 (`M-REOPEN-1`) quantified how far measured production evidence would need to move before the claim could reopen. Cycle 15 (`M-INGEST-1`) ranked which evidence-ingestion paths could produce admissible traces. Cycle 16 (`M-PIPELINE-1`) composed trace validation, ingestion admissibility, provenance checks, and threshold comparison into one end-to-end decision pipeline.

The result is an auditable reopen pathway. A future trace must be privacy-safe, measured, provenance-attested, produced by a production, shadow-production, or canary dual-run path, and must cross the quantitative threshold under identical workload accounting. No current artifact satisfies those conditions.

## Introduction

The long-exposure run investigates whether useful portions of neural-network inference can be "physicalized" into hardware rather than repeatedly executed as software kernels. Earlier cycles narrowed the credible target to a bounded safety/filter submodel behind programmable fallback, audit, update, health, drift, and rollback controls. Phase 2 then compared that hybrid safety/filter path against calibrated workload traces and stronger programmable baselines. The stronger programmable accelerator erased the last modeled hybrid win.

Cycles 11-13 made that downgrade explicit and defined the evidence contract needed before the claim could reopen. Cycles 14-16 took the next step: they made the reopen contract executable. Instead of asking only "what data would be useful?", these cycles answer "what exact measured condition would count, which paths could generate it, and how is a trace-like artifact classified?"

The relevant terms are:

- A **production trace** is a privacy-safe serving telemetry table with per-request route, latency, energy, fallback, audit, policy, utilization, and gate fields.
- A **reopen candidate** is not a winning result by itself. It is a trace that passes the schema, source, provenance, measurement, and threshold gates strongly enough to challenge the current downgrade.
- **pJ-equivalent/day** is the project’s normalized daily cost unit for comparing modeled or measured energy-like terms across hybrid and programmable paths.

The public calibration context still relies on the prior Phase 2 source set for energy and accelerator baselines [7]-[10]. No new external sources were added in cycles 14-16.

## Approach

The work followed the evidence chain created in earlier cycles.

First, `M-REOPEN-1` translated the downgraded claim into a numerical inequality:

`measured_hybrid_total < measured_best_programmable_baseline`

The comparison must use identical accepted-volume, fallback, audit, update, utilization, latency, and energy accounting.

Second, `M-INGEST-1` evaluated possible ways to obtain traces that could instantiate that inequality. It separated useful production/shadow/canary dual-run designs from synthetic fixtures, vendor-only benchmarks, sampled logs without baselines, proxy replay, and privacy-risk raw logs.

Third, `M-PIPELINE-1` composed the gates into a final decision table. It demonstrated that invalid traces, insufficient traces, non-crossing measured dual-run traces, and synthetic counterfactual crossings all receive distinct statuses. Only a fully measured, attested, admissible source that crosses the threshold can become an actual reopen candidate.

The three milestones were validated by their audit sessions:

- `M-REOPEN-1`: researcher `ad4cc37f-3176-48a5-bc8c-c065ea39f99e`, worker `42fc5e9f-b924-4e96-95ff-07e82647a3e3`, auditor `231e82ae-7103-46d4-a03b-e45f88d94215`.
- `M-INGEST-1`: researcher `bf22ab01-fd7f-4918-9904-8836f8a9367d`, worker `ef3a7763-8b71-4635-ba89-b9e8f632a6d5`, auditor `85a4f146-5bc0-46e0-8ffe-1e1b420257e0`.
- `M-PIPELINE-1`: researcher `3afd1a1c-a191-4b75-b238-91a95eb1c22e`, worker `d6fbf875-307b-4534-864c-08fbf2b91ed7`, auditor `31acd650-ef84-4321-a47c-3265799c4cae`.

## Findings

### Cycle 14: Quantitative Reopen Thresholds

Cycle 14 built `M-REOPEN-1`, the quantitative threshold model. The worker added `physicalized-weights/scripts/reopen_thresholds.py`, `physicalized-weights/scripts/symbolic_reopen_thresholds.wls`, tests, documentation, and generated CSV/JSON/PNG outputs. The model reads the stronger-baseline comparison, workload viability data, trace schema, and local-overhead summary, then emits one threshold row per workload scenario.

The main result is that current hybrid wins remain zero. The threshold summary reports:

- `current_hybrid_wins`: `0`
- `scenario_count`: `10`
- `finite_threshold_count`: `8`
- `reopen_class_counts`: `finite_threshold: 8`, `unreopenable_zero_volume: 1`, `unreopenable_all_fallback: 1`
- `evidence_status`: `modeled_proxy_not_measured_production`

The formerly preserved `high_volume_stable_moderation` scenario now has a quantified gap: the hybrid path would need a `1,471,448,845.624272` pJ-equivalent/day reduction, or the programmable baseline would need the same degradation, just to tie. Its current best baseline is still `programmable_accelerator`.

![Per-scenario reduction or baseline-degradation threshold required to overturn the stronger programmable baseline, with unreopenable zero-volume/all-fallback regimes separated.](physicalized-weights/data/reopen_thresholds_by_scenario.png)

The threshold model also formalized special cases:

- Zero accepted fast-path volume cannot reopen.
- All fallback cannot reopen.
- Proxy-only energy cannot reopen.
- Missing accelerator baseline cannot reopen.
- Failed health, drift, or audit gates receive no accepted fast-path credit.

The auditor validated `M-REOPEN-1` with no code fixes. Validation included rerunning the threshold script, running six threshold tests, regenerating the Wolfram special-case proof artifact, checking the PNG, and independently confirming threshold arithmetic against `stronger_baseline_comparison.csv`.

### Cycle 15: Trace-Ingestion Path Admissibility

Cycle 15 built `M-INGEST-1`, an admissibility matrix for candidate evidence sources. The worker added `physicalized-weights/scripts/trace_ingestion_path_evaluator.py`, tests, documentation, and generated CSV/JSON/PNG artifacts.

The evaluator scored eight candidate paths across schema completeness, measured hybrid coverage, measured accelerator baseline coverage, measured energy coverage, accepted fast-path validity, fallback/audit/update accounting, policy consistency, privacy safety, workload fidelity, threshold evaluability, and counterfactual baseline validity.

The summary classified the paths as:

| Classification | Count | Paths |
|---|---:|---|
| `reopen_candidate_path` | 2 | `shadow_production_dual_run`, `canary_ab_dual_instrumented` |
| `threshold_evaluable_if_measured` | 1 | `offline_replay_redacted_features` |
| `valid_but_insufficient` | 4 | `synthetic_fixture_only`, `sampled_production_logs_without_baselines`, `accelerator_vendor_benchmark_only`, `simulated_scaled_workload` |
| `inadmissible` | 1 | `privacy_risk_raw_logs` |

No path was classified as actual reopened evidence, because no measured production trace was supplied.

![Admissibility and evidence coverage of candidate production-trace ingestion paths, separating privacy failures, missing-baseline failures, proxy-only evidence, and threshold-evaluable measured paths.](physicalized-weights/data/trace_ingestion_path_admissibility.png)

The important decision is that convenient evidence sources remain blocked. Synthetic fixtures, simulated scaled workloads, sampled logs without same-workload baselines, and vendor-only accelerator benchmarks cannot reopen the claim. Privacy-risk raw logs are rejected even if they contain useful metrics. Only privacy-safe measured dual-run production, shadow-production, or canary instrumentation can become a reopen-candidate path design.

The auditor validated `M-INGEST-1` without code fixes. The only minor note was that `threshold_evaluable_if_measured` is a slightly overloaded label for offline replay, because that path still cannot evaluate `M-REOPEN-1` until production or shadow measurement is added. The prose and blockers document this clearly.

### Cycle 16: End-to-End Reopen Pipeline

Cycle 16 built `M-PIPELINE-1`, the composed reopen gate. The worker added `physicalized-weights/scripts/reopen_pipeline_demo.py`, tests, documentation, four privacy-safe pipeline fixtures, a results table, a summary JSON file, and a decision-flow figure.

The pipeline composes:

1. `M-TRACE-1` trace validation.
2. `M-INGEST-1` ingestion-path admissibility.
3. `M-REOPEN-1` quantitative threshold comparison.
4. Pipeline-layer provenance and measured-status checks.

The final statuses are:

- `invalid_trace`
- `valid_but_insufficient`
- `threshold_evaluable_not_crossed`
- `synthetic_counterfactual_crossed`
- `actual_reopen_candidate`

The generated result table contains one fixture in each non-reopening branch:

| Fixture | Final status | Meaning |
|---|---|---|
| `pipeline_trace_invalid_privacy.csv` | `invalid_trace` | Privacy-risk trace rejected. |
| `pipeline_trace_valid_insufficient.csv` | `valid_but_insufficient` | Synthetic/proxy fixture cannot reopen. |
| `pipeline_trace_threshold_evaluable_not_crossed.csv` | `threshold_evaluable_not_crossed` | Measured-style dual-run path does not cross the threshold. |
| `pipeline_trace_synthetic_counterfactual_crossed.csv` | `synthetic_counterfactual_crossed` | Numeric threshold crossing is synthetic, so it is not actual evidence. |

The summary reports:

- `fixture_count`: `4`
- `actual_reopen_candidate_count`: `0`
- `final_status_counts`: `invalid_trace: 1`, `valid_but_insufficient: 1`, `threshold_evaluable_not_crossed: 1`, `synthetic_counterfactual_crossed: 1`
- `synthetic_or_proxy_actual_reopen_candidates`: `[]`

![End-to-end reopen gate outcomes for invalid, insufficient, threshold-evaluable, and synthetic counterfactual traces, showing that no current artifact becomes actual production reopen evidence.](physicalized-weights/data/reopen_pipeline_decision_flow.png)

The final actual-reopen condition is conjunctive. A trace must satisfy all of the following:

- `M-TRACE-1 valid_reopen_candidate`
- `M-INGEST-1 reopen_candidate_path`
- measured hybrid and programmable baseline terms
- production, shadow-production, or canary source type
- provenance attestation
- threshold crossed

The auditor validated `M-PIPELINE-1` without source fixes. The audit also ran an independent probe showing that a fully measured production control can become `actual_reopen_candidate`, while synthetic source, proxy status, missing attestation, and invalid ingestion path cannot.

## Discussion

Cycles 14-16 did not change the central technical conclusion. They made the downgrade harder to accidentally overrule.

Before these cycles, the project had a validated trace schema and a production-measurement requirement, but the reopen process still existed as separate pieces. After these cycles, the process is executable and auditable. A future evidence package must pass schema validation, source admissibility, measured-status checks, provenance checks, and threshold comparison before it can affect the claim.

This matters because several plausible-looking evidence sources are now explicitly insufficient. A vendor accelerator benchmark may contain impressive hardware numbers, but it lacks identical workload accounting against the hybrid path. A synthetic trace may test software correctly, but it cannot reopen a production performance claim. A sampled production log may reflect real traffic, but without counterfactual baselines it cannot form the measured hybrid-versus-programmable delta. Raw logs are rejected if they violate the privacy boundary.

The project now has a clear distinction between three concepts:

- **Useful rehearsal evidence**: synthetic fixtures, offline replay, and local proxy measurements can test the tooling.
- **Candidate evidence path**: privacy-safe shadow or canary dual-run instrumentation can generate admissible traces if fully measured.
- **Actual reopen evidence**: a supplied trace from an admissible path must pass every gate and cross the threshold.

The Phase 2 downgrade remains in force.

## Open Questions

No real production, shadow-production, or canary trace has been ingested.

Production accelerator energy, hybrid energy, utilization, batching effects, and same-request counterfactual baseline latencies remain unmeasured.

The current thresholds are pJ-equivalent modeled/proxy thresholds. They define the measured condition a future trace must satisfy, but they are not themselves new hardware evidence.

Offline replay remains a useful rehearsal path, but it is below the evidence standard until upgraded with production or shadow-production measured energy, utilization, and identical workload accounting.

The compiled Verilator simulation gap from earlier prototype work remains a future superseding check if local build tooling becomes available. It does not affect the cycle-14-to-16 reopen-gate validation.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

New cycle-14-to-16 scripts:

- `physicalized-weights/scripts/reopen_thresholds.py` - 431 lines - per-scenario quantitative reopen-threshold model.
- `physicalized-weights/scripts/symbolic_reopen_thresholds.wls` - 30 lines - Wolfram special-case proof artifact.
- `physicalized-weights/scripts/trace_ingestion_path_evaluator.py` - 520 lines - candidate trace-ingestion admissibility evaluator.
- `physicalized-weights/scripts/reopen_pipeline_demo.py` - 473 lines - composed reopen-gate demonstration pipeline.

New cycle-14-to-16 tests:

- `physicalized-weights/tests/test_reopen_thresholds.py` - 135 lines.
- `physicalized-weights/tests/test_trace_ingestion_path_evaluator.py` - 136 lines.
- `physicalized-weights/tests/test_reopen_pipeline_demo.py` - 173 lines.

New cycle-14-to-16 docs:

- `physicalized-weights/docs/reopen_thresholds.md` - 60 lines.
- `physicalized-weights/docs/trace_ingestion_paths.md` - 111 lines.
- `physicalized-weights/docs/end_to_end_reopen_pipeline.md` - 26 lines.

Current cumulative manifest counts after these cycles:

- Authored research scripts: 18, totaling 6,510 lines.
- Authored tests: 15, totaling 2,025 lines.
- Authored HDL/support files: 4, totaling 241 lines.
- Authored docs and diagram sources: 17, totaling 1,179 lines.
- Ledger events: 42.
- Plan milestones: 16.

`MANIFEST.md` was updated during this reporting pass to reflect the current workspace snapshot through `M-PIPELINE-1`.

### Generated Data and Figures

Cycle 14 generated:

- `physicalized-weights/data/reopen_thresholds.csv` - 10 scenario rows.
- `physicalized-weights/data/reopen_thresholds_summary.json`.
- `physicalized-weights/data/symbolic_reopen_thresholds.json`.
- `physicalized-weights/data/reopen_thresholds_by_scenario.png` - valid PNG, 900 x 460 RGB.

Cycle 15 generated:

- `physicalized-weights/data/trace_ingestion_paths.csv` - 8 path rows.
- `physicalized-weights/data/trace_ingestion_path_scores.csv` - 8 score rows.
- `physicalized-weights/data/trace_ingestion_path_summary.json`.
- `physicalized-weights/data/trace_ingestion_path_admissibility.png` - valid PNG, 900 x 460 RGB.

Cycle 16 generated:

- `physicalized-weights/data/pipeline_trace_invalid_privacy.csv`.
- `physicalized-weights/data/pipeline_trace_valid_insufficient.csv`.
- `physicalized-weights/data/pipeline_trace_threshold_evaluable_not_crossed.csv`.
- `physicalized-weights/data/pipeline_trace_synthetic_counterfactual_crossed.csv`.
- `physicalized-weights/data/reopen_pipeline_results.csv` - 4 result rows.
- `physicalized-weights/data/reopen_pipeline_summary.json`.
- `physicalized-weights/data/reopen_pipeline_decision_flow.png` - valid PNG, 900 x 460 RGB.

### Test Results

Cycle 14 validation reported:

- `python3 physicalized-weights/scripts/reopen_thresholds.py`: passed.
- `python3 physicalized-weights/tests/test_reopen_thresholds.py`: passed 6 tests.
- `wolfram-batch -script physicalized-weights/scripts/symbolic_reopen_thresholds.wls`: passed.
- PNG file check: passed.
- `promise_check`: passed with only pre-existing orphan-report warnings.
- `org_check`: passed with only pre-existing root-file warnings.

Cycle 15 validation reported:

- `python3 physicalized-weights/scripts/trace_ingestion_path_evaluator.py`: passed.
- `python3 physicalized-weights/tests/test_trace_ingestion_path_evaluator.py`: passed 7 tests.
- PNG file check: passed.
- `promise_check`: passed.
- `org_check`: passed.

Cycle 16 validation reported:

- `python3 physicalized-weights/scripts/reopen_pipeline_demo.py`: passed.
- `python3 physicalized-weights/tests/test_reopen_pipeline_demo.py`: passed 8 tests.
- PNG file check: passed.
- `promise_check`: passed after auditor event, with `events: 42` and `plan milestones: 16`.
- `org_check`: passed.
- Independent auditor probe: passed.

During this reporting pass, `promise_check` and `org_check` were run as manifest sanity checks. Both exited 0. The remaining warnings are the known orphan cycle-report artifacts and the known root files `physicalized_model_weights_long_exposure_prompt.md` and `physicalized_weights_long_exposure_live.log`.

### Session References

Cycle 14:

- Researcher: `ad4cc37f-3176-48a5-bc8c-c065ea39f99e`
- Worker: `42fc5e9f-b924-4e96-95ff-07e82647a3e3`
- Auditor: `231e82ae-7103-46d4-a03b-e45f88d94215`

Cycle 15:

- Researcher: `bf22ab01-fd7f-4918-9904-8836f8a9367d`
- Worker: `ef3a7763-8b71-4635-ba89-b9e8f632a6d5`
- Auditor: `85a4f146-5bc0-46e0-8ffe-1e1b420257e0`

Cycle 16:

- Researcher: `3afd1a1c-a191-4b75-b238-91a95eb1c22e`
- Worker: `d6fbf875-307b-4534-864c-08fbf2b91ed7`
- Auditor: `31acd650-ef84-4321-a47c-3265799c4cae`

### Cross-Reference Map

- `M-SYNTH-2`, `M-MEASURE-1`, and `M-TRACE-1` define the downgrade, measurement contract, and trace schema used by cycles 14-16.
- `stronger_baseline_comparison.csv`, `workload_viability_overlay.csv`, `production_trace_schema.json`, and `local_overhead_summary.json` feed `reopen_thresholds.py`.
- `reopen_thresholds.py` emits `reopen_thresholds.csv`, `reopen_thresholds_summary.json`, and `reopen_thresholds_by_scenario.png`.
- `symbolic_reopen_thresholds.wls` emits `symbolic_reopen_thresholds.json`.
- `production_trace_schema.json` and `reopen_thresholds_summary.json` feed `trace_ingestion_path_evaluator.py`.
- `trace_ingestion_path_evaluator.py` emits `trace_ingestion_paths.csv`, `trace_ingestion_path_scores.csv`, `trace_ingestion_path_summary.json`, and `trace_ingestion_path_admissibility.png`.
- `production_trace_schema.json`, `reopen_thresholds.csv`, and `trace_ingestion_path_scores.csv` feed `reopen_pipeline_demo.py`.
- `reopen_pipeline_demo.py` emits the four pipeline fixture traces, `reopen_pipeline_results.csv`, `reopen_pipeline_summary.json`, and `reopen_pipeline_decision_flow.png`.
- `plan_of_record.md` and `promise_ledger.jsonl` now track milestones through `M-PIPELINE-1`.
