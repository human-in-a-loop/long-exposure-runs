---
created: 2026-05-13T04:46:00Z
cycle: 1
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-FINAL-1
---

# Reproducibility

Run commands from `<workspace>`. The current environment has `wolfram-batch`, Verilator, Yosys, and Graphviz `dot`, but does not have `pytest`, `make`, or a C++ compiler. Tests therefore use stdlib harnesses, and compiled Verilator simulation is recorded as blocked rather than passed.

## Regenerate Core Artifacts

```bash
python3 physicalized-weights/scripts/breakeven_model.py
wolfram-batch -script physicalized-weights/scripts/symbolic_breakeven.wls
python3 physicalized-weights/scripts/target_scoring.py
dot -Tpng physicalized-weights/docs/hybrid_safety_filter_arch.dot -o physicalized-weights/docs/hybrid_safety_filter_arch.png
python3 physicalized-weights/scripts/fallback_policy_sim.py
python3 physicalized-weights/scripts/prototype_safety_filter.py
python3 physicalized-weights/hdl/run_yosys_eval.py
yosys -s physicalized-weights/hdl/safety_filter_core.ys > physicalized-weights/data/yosys_safety_filter.log 2>&1
dot -Tpng physicalized-weights/data/safety_filter_core_netlist.dot -o physicalized-weights/data/safety_filter_core_netlist.png
python3 physicalized-weights/scripts/verify_prototype_closure.py
python3 physicalized-weights/scripts/build_final_synthesis.py
```

## Run Tests

```bash
python3 physicalized-weights/tests/test_breakeven_model.py
python3 physicalized-weights/tests/test_target_scoring.py
python3 physicalized-weights/tests/test_fallback_policy_sim.py
python3 physicalized-weights/tests/test_prototype_safety_filter.py
python3 physicalized-weights/tests/test_prototype_verification_closure.py
python3 physicalized-weights/tests/test_final_synthesis.py
python3 -m long_exposure.tools.promise_check .
```

## Tool Limitations To Preserve

Verilator lint is usable, but compiled Verilator simulation requires `make` and a C++ compiler that are not present in this environment. If those tools become available, rerun the compiled simulator and compare it against `physicalized-weights/data/hdl_sim_results.csv`; a disagreement reopens `M-PROTO-1`.

## Phase 3 Reopen Pathway Replay

The Phase 3 closure package is replayed in dependency order so a reader can reproduce the non-reopen conclusion from one command block:

```bash
python3 physicalized-weights/scripts/local_overhead_benchmark.py
python3 physicalized-weights/scripts/production_trace_validator.py physicalized-weights/data/example_production_trace_valid.csv physicalized-weights/data/example_production_trace_invalid.csv
python3 physicalized-weights/scripts/reopen_thresholds.py
wolfram-batch -script physicalized-weights/scripts/symbolic_reopen_thresholds.wls
python3 physicalized-weights/scripts/trace_ingestion_path_evaluator.py
python3 physicalized-weights/scripts/reopen_pipeline_demo.py
python3 physicalized-weights/scripts/evidence_pack_replay.py
python3 physicalized-weights/scripts/build_phase3_reopen_synthesis.py
```

Expected non-reopen outcomes:

- `physicalized-weights/data/reopen_pipeline_summary.json` keeps `actual_reopen_candidate_count` at `0`.
- `physicalized-weights/data/evidence_pack_replay_summary.json` keeps `actual_reopen_candidate_count` at `0`.
- `physicalized-weights/data/phase3_reopen_summary.json` reports `current_artifacts_reopen: false`.
- `physicalized-weights/data/phase3_reopen_claim_matrix.csv` includes blocked classes for synthetic, proxy/local, vendor-only, privacy-risk, stale-hash, unknown-threshold, and non-crossing measured packages.

Validation:

```bash
python3 physicalized-weights/tests/test_local_overhead_benchmark.py
python3 physicalized-weights/tests/test_production_trace_validator.py
python3 physicalized-weights/tests/test_reopen_thresholds.py
python3 physicalized-weights/tests/test_trace_ingestion_path_evaluator.py
python3 physicalized-weights/tests/test_reopen_pipeline_demo.py
python3 physicalized-weights/tests/test_evidence_pack_replay.py
python3 physicalized-weights/tests/test_phase3_reopen_synthesis.py
file physicalized-weights/data/phase3_reopen_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

## Phase 4 Reopen Lifecycle Replay

Replay the post-Phase-3 operational layers and final synthesis refresh in dependency order:

```bash
python3 physicalized-weights/scripts/evidence_acquisition_readiness.py
python3 physicalized-weights/scripts/evidence_pack_template_dryrun.py
python3 physicalized-weights/scripts/evidence_pack_intake_rehearsal.py
python3 physicalized-weights/scripts/reopen_uncertainty_protocol.py
python3 physicalized-weights/scripts/evidence_package_lifecycle.py
python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py
```

Expected non-reopen outcomes:

- `physicalized-weights/data/evidence_acquisition_readiness_summary.json` reports readiness is not evidence.
- `physicalized-weights/data/evidence_pack_dryrun_summary.json` reports dry-run artifacts are not evidence.
- `physicalized-weights/data/evidence_pack_intake_rehearsal_summary.json` reports `actual_reopen_candidate_count: 0`.
- `physicalized-weights/data/reopen_uncertainty_summary.json` requires `UCB_alpha(H - B) < 0`.
- `physicalized-weights/data/evidence_package_lifecycle_summary.json` reports `actual_reopen_candidate_count: 0` and `hypothetical_actual_candidate_control_count: 1`.
- `physicalized-weights/data/phase4_reopen_summary.json` reports `current_artifacts_reopen: false`.

Validation:

```bash
python3 physicalized-weights/tests/test_evidence_acquisition_readiness.py
python3 physicalized-weights/tests/test_evidence_pack_template_dryrun.py
python3 physicalized-weights/tests/test_evidence_pack_intake_rehearsal.py
python3 physicalized-weights/tests/test_reopen_uncertainty_protocol.py
python3 physicalized-weights/tests/test_evidence_package_lifecycle.py
python3 physicalized-weights/tests/test_phase4_reopen_synthesis.py
file physicalized-weights/data/phase4_reopen_lifecycle_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

## Campaign Closure Replay

Replay the campaign closure reporting layer:

```bash
python3 physicalized-weights/scripts/build_campaign_closure_report.py
python3 physicalized-weights/tests/test_campaign_closure_report.py
file physicalized-weights/data/campaign_closure_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

Expected invariant outputs:

- `physicalized-weights/data/campaign_closure_summary.json` reports `current_superiority_claim_count: 0`.
- `physicalized-weights/data/campaign_closure_summary.json` reports `actual_reopen_candidate_count: 0`.
- `physicalized-weights/data/campaign_closure_summary.json` reports `new_reopen_gate_count: 0`.
- `physicalized-weights/docs/campaign_executive_summary.md` keeps synthetic, proxy, template, rehearsal, vendor-only, and dry-run artifacts out of measured-evidence status.

## Public Baseline Refresh Replay

Replay the public programmable-baseline recency probe, conservative prior refresh, and synthesis addendum:

```bash
python3 physicalized-weights/scripts/public_baseline_recency_probe.py
python3 physicalized-weights/scripts/public_baseline_prior_refresh.py
python3 physicalized-weights/scripts/build_public_baseline_synthesis.py
```

Expected outcomes:

- `physicalized-weights/data/public_baseline_recency_summary.json` records MLPerf Inference v6.0 as the latest public MLPerf Inference release observed by this campaign.
- `physicalized-weights/data/public_baseline_prior_refresh_summary.json` records 12 primary MLCommons rows ingested from 520 available rows, zero direct energy calibration rows, zero direct safety-filter workload rows, and `programmable_null_effect: strengthened_or_preserved`.
- `physicalized-weights/data/public_baseline_synthesis_summary.json` records `phase2_downgrade_preserved: true`, `phase4_reopen_condition_unchanged: true`, and endpoint counters at zero or false.

Validation:

```bash
python3 physicalized-weights/tests/test_public_baseline_recency_probe.py
python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py
python3 physicalized-weights/tests/test_public_baseline_synthesis.py
file physicalized-weights/data/public_baseline_synthesis_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```
