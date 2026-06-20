# Manifest


## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `physicalized-weights/scripts/breakeven_model.py` — Normalized break-even sweep and default winner counts used in Section 1.
- `physicalized-weights/scripts/symbolic_breakeven.wls` — Wolfram break-even special-case derivation used in Section 1.
- `physicalized-weights/scripts/target_scoring.py` — Target and anti-target ranking used in Section 2.
- `physicalized-weights/scripts/fallback_policy_sim.py` — Hybrid safety/filter routing and fallback simulation used in Section 2.
- `physicalized-weights/scripts/prototype_safety_filter.py` — Prototype classifier vectors, routing distribution, and baseline comparison used in Section 3.
- `physicalized-weights/scripts/verify_prototype_closure.py` — Prototype closure evidence tying Python, HDL, Yosys, Verilator lint, Graphviz, and hash freshness in Section 3.
- `physicalized-weights/scripts/build_final_synthesis.py` — Initial evidence-labeled synthesis and evidence map summarized in Section 3.
- `physicalized-weights/hdl/safety_filter_core.sv` — Combinational safety/filter HDL core described in Section 3.
- `physicalized-weights/hdl/run_yosys_eval.py` — Yosys evaluation of the HDL core against Python golden vectors in Sections 3 and 9.
- `physicalized-weights/hdl/safety_filter_core.ys` — Yosys synthesis and DOT-export flow supporting Sections 3 and 9.
- `physicalized-weights/hdl/safety_filter_core_tb.cpp` — Retained compiled-simulation testbench whose environment blocker is discussed in Sections 3 and 10.
- `physicalized-weights/scripts/calibrated_breakeven.py` — Explicit-unit calibrated model and scenario counts used in Section 4.
- `physicalized-weights/scripts/workload_trace_generator.py` — Synthetic workload regimes and fast-path viability overlay used in Section 4.
- `physicalized-weights/scripts/stronger_baseline_model.py` — Equal-workload stronger-baseline replay and Phase 2 falsification result used in Section 4.
- `physicalized-weights/scripts/build_phase2_synthesis.py` — Phase 2 claim matrix and downgrade synthesis used in Section 4.
- `physicalized-weights/scripts/local_overhead_benchmark.py` — Local proxy timing medians and production-measurement gap evidence used in Section 5.
- `physicalized-weights/scripts/production_trace_validator.py` — Production trace schema and validator rules used in Section 5.
- `physicalized-weights/scripts/reopen_thresholds.py` — Quantitative reopen thresholds and current zero-hybrid-win accounting used in Section 6.
- `physicalized-weights/scripts/symbolic_reopen_thresholds.wls` — Wolfram reopen-threshold special cases used in Section 6.
- `physicalized-weights/scripts/trace_ingestion_path_evaluator.py` — Admissible ingestion-path classification used in Section 6.
- `physicalized-weights/scripts/reopen_pipeline_demo.py` — End-to-end validation, ingestion, provenance, and threshold pipeline used in Section 6.
- `physicalized-weights/scripts/evidence_pack_replay.py` — Replayable evidence-pack manifest harness used in Section 6.
- `physicalized-weights/scripts/build_phase3_reopen_synthesis.py` — Phase 3 reopen-pathway synthesis summarized in Section 6.
- `physicalized-weights/scripts/evidence_acquisition_readiness.py` — Pre-collection readiness classification used in Section 6.
- `physicalized-weights/scripts/evidence_pack_template_dryrun.py` — Operator evidence-pack dry-run templates and blocking checks used in Section 6.
- `physicalized-weights/scripts/evidence_pack_intake_rehearsal.py` — Synthetic-safe intake handoff rehearsal used in Section 6.
- `physicalized-weights/scripts/reopen_uncertainty_protocol.py` — Uncertainty-aware UCB reopen rule used in Section 6.
- `physicalized-weights/scripts/evidence_package_lifecycle.py` — Lifecycle state machine and terminal-state accounting used in Section 7.
- `physicalized-weights/scripts/build_phase4_reopen_synthesis.py` — Canonical Phase 4 reopen conjunction and claim matrix used in Section 7.
- `physicalized-weights/scripts/target_robustness_stress.py` — Target-class robustness stress test used in Section 8.
- `physicalized-weights/scripts/build_campaign_deferral_watchlist.py` — Deferral watchlist and trigger governance used in Sections 8 and 10.
- `physicalized-weights/scripts/build_campaign_closure_report.py` — Closure claim dispositions and endpoint counters used in Section 8.
- `physicalized-weights/scripts/build_closure_archive_index.py` — Canonical archive index and artifact coverage evidence used in Section 8.
- `physicalized-weights/scripts/toolchain_condition_probe.py` — Post-closure toolchain condition probe used in Section 9.
- `physicalized-weights/scripts/campaign_invariant_checker.py` — Cross-artifact invariant checker used in Section 9.
- `physicalized-weights/scripts/public_baseline_recency_probe.py` — MLPerf recency and source materiality screen used in Section 9.
- `physicalized-weights/scripts/public_baseline_prior_refresh.py` — MLCommons v6.0 public-baseline prior refresh used in Section 9.
- `physicalized-weights/scripts/build_public_baseline_synthesis.py` — Public-baseline synthesis addendum and endpoint preservation used in Section 9.

## Script Inventory

### physicalized-weights/scripts

- `breakeven_model.py` - 384 lines - normalized break-even sweep for programmable, software-optimized, accelerator, fixed-digital, analog, and hybrid strategies.
- `target_scoring.py` - 283 lines - deterministic ranking model for physicalization candidates and anti-targets.
- `fallback_policy_sim.py` - 342 lines - fallback and fail-safe policy simulator for the hybrid safety-filter architecture.
- `prototype_safety_filter.py` - 392 lines - deterministic fixed safety/filter classifier prototype with route/fallback outputs.
- `verify_prototype_closure.py` - 377 lines - closure checker tying Python, HDL, Yosys, Verilator-lint, Graphviz, and freshness evidence.
- `build_final_synthesis.py` - 451 lines - final evidence manifest, summary JSON, and evidence map builder.
- `calibrated_breakeven.py` - 428 lines - explicit-unit calibrated companion to the Phase 1 break-even model.
- `local_overhead_probe.py` - 121 lines - local host/Python proxy measurements for dot product, dispatch, and dot-plus-dispatch overheads.
- `workload_trace_generator.py` - 593 lines - deterministic workload generator and viability overlay for safety/filter traffic.
- `stronger_baseline_model.py` - 510 lines - equal-workload replay comparing optimized software/runtime, programmable accelerator, and hybrid paths.
- `build_phase2_synthesis.py` - 288 lines - Phase 2 claim-matrix and downgrade synthesis builder.
- `local_overhead_benchmark.py` - 449 lines - local proxy timing harness for feature extraction, fixed classifier, software classifier, routing, and audit overheads.
- `production_trace_validator.py` - 410 lines - production serving-trace validator for reopen eligibility and privacy constraints.
- `reopen_thresholds.py` - 431 lines - per-scenario quantitative reopen-threshold model.
- `symbolic_reopen_thresholds.wls` - 30 lines - Wolfram special-case proof artifact for reopen controls.
- `trace_ingestion_path_evaluator.py` - 520 lines - admissibility matrix for trace-ingestion paths.
- `reopen_pipeline_demo.py` - 473 lines - end-to-end reopen gate composing validation, ingestion, provenance, and threshold checks.
- `evidence_pack_replay.py` - 482 lines - replayable evidence-pack manifest harness for future trace packages.
- `build_phase3_reopen_synthesis.py` - 630 lines - Phase 3 reopen-pathway synthesis builder.
- `evidence_acquisition_readiness.py` - 298 lines - pre-collection readiness evaluator for proposed production/shadow/canary acquisition designs.
- `evidence_pack_template_dryrun.py` - 704 lines - operator-facing evidence-pack template generator and dry-run acceptance checker.
- `evidence_pack_intake_rehearsal.py` - 599 lines - synthetic-safe handoff rehearsal from dry-run templates into evidence-pack replay.
- `reopen_uncertainty_protocol.py` - 669 lines - uncertainty-aware measured reopen decision-margin classifier.
- `evidence_package_lifecycle.py` - 830 lines - deterministic lifecycle state machine composing acquisition, dry-run, intake, replay, threshold, and uncertainty gates.
- `build_phase4_reopen_synthesis.py` - 566 lines - Phase 4 canonical reopen-path synthesis, claim matrix, manifest, and flow-figure builder.
- `target_robustness_stress.py` - 485 lines - target-class robustness stress test against stronger programmable baselines.
- `build_campaign_deferral_watchlist.py` - 444 lines - campaign deferral and future-evidence trigger watchlist builder.
- `build_campaign_closure_report.py` - 518 lines - reader-facing closure report, executive summary, claim disposition, manifest, and evidence-flow builder.
- `build_closure_archive_index.py` - 442 lines - closure archive index, hash manifest, summary, and coverage-figure builder.
- `toolchain_condition_probe.py` - 382 lines - local HDL/toolchain capability probe and conditional compiled-Verilator status checker.
- `campaign_invariant_checker.py` - 427 lines - cross-artifact endpoint-invariant consistency checker for canonical summaries and reports.
- `public_baseline_recency_probe.py` - 399 lines - public programmable-baseline recency and materiality screen using official MLCommons sources.
- `public_baseline_prior_refresh.py` - 527 lines - primary MLCommons v6.0 subset ingestion and conservative programmable-baseline prior refresh mapper.
- `build_public_baseline_synthesis.py` - 399 lines - public-baseline refresh synthesis addendum builder for canonical final synthesis and reproducibility records.
- `symbolic_breakeven.wls` - 28 lines - Wolfram derivation of break-even threshold special cases.

### physicalized-weights/tests

- 30 stdlib test files, 4,164 total lines.
- Cycle 20-22 additions:
  - `test_evidence_pack_template_dryrun.py` - 161 lines - operator dry-run statuses, manifest allow-list, ingestion path, privacy, provenance, hash, and non-reopen tests.
  - `test_evidence_pack_intake_rehearsal.py` - 124 lines - dry-run-to-replay handoff preservation and mutation-blocking tests.
  - `test_reopen_uncertainty_protocol.py` - 130 lines - confidence-bound, missing-uncertainty, high-correlation, source, volume, fallback, and zero-reopen tests.
- Cycle 23-25 additions:
  - `test_evidence_package_lifecycle.py` - 155 lines - lifecycle terminal-state, ordering, non-reopen, and hypothetical-control accounting tests.
  - `test_phase4_reopen_synthesis.py` - 162 lines - canonical synthesis, uncertainty/lifecycle rule, claim matrix, manifest coverage, and replayability tests.
  - `test_target_robustness_stress.py` - 119 lines - zero-volume, all-fallback, high-update, software-savings, anti-target, counterfactual-label, and frontier tests.
- Cycle 26-28 additions:
  - `test_campaign_deferral_watchlist.py` - 116 lines - current-disposition, insufficient-substitute, measured-trigger, prototype-trigger, and no-new-gate tests.
  - `test_campaign_closure_report.py` - 142 lines - closure-counter, claim-coverage, artifact-support, final-synthesis-linkage, and non-evidence labeling tests.
  - `test_closure_archive_index.py` - 133 lines - archive-counter, canonical-artifact hash, claim-support coverage, fixture-label, and figure-embedding tests.
- Cycle 29-31 additions:
  - `test_toolchain_condition_probe.py` - 125 lines - tool availability, blocked compiled-Verilator status, refreshed HDL checks, endpoint-counter, and PNG tests.
  - `test_campaign_invariant_checker.py` - 141 lines - zero-contradiction, endpoint-counter, synthetic contradiction, warning, no-new-gate, and ownership-regression tests.
  - `test_public_baseline_recency_probe.py` - 143 lines - MLPerf recency, source traceability, model-refresh, non-reopen, endpoint-counter, and PNG tests.
- Cycle 32-34 additions:
  - `test_public_baseline_prior_refresh.py` - 133 lines - MLCommons subset ingestion, no energy inference, endpoint-counter, vendor-secondary, and mapping-field tests.
  - `test_public_baseline_synthesis.py` - 142 lines - public-baseline synthesis, claim-row, endpoint-counter, absent energy/workload support, and Phase 4 boundary tests.

### physicalized-weights/hdl

- `run_yosys_eval.py` - 113 lines - Yosys-based HDL evaluator against Python golden vectors.
- `safety_filter_core.sv` - 45 lines - pure combinational signed-int8 safety/filter dot-product core.
- `safety_filter_core.ys` - 11 lines - Yosys synthesis/check and DOT-export script.
- `safety_filter_core_tb.cpp` - 72 lines - Verilator C++ testbench retained for future compiled simulation.

### physicalized-weights/docs

- 33 authored research docs and diagram sources, 2,061 total lines.
- Cycle 20-22 additions:
  - `operator_evidence_pack_template.md` - 38 lines - future-operator manifest, trace, attestation, privacy, threshold, and dry-run package instructions.
  - `evidence_pack_intake_rehearsal.md` - 33 lines - handoff rehearsal between dry-run templates and evidence-pack replay.
  - `measured_reopen_uncertainty_protocol.md` - 42 lines - UCB-based future reopen uncertainty rule and blockers.
- Cycle 23-25 additions:
  - `evidence_package_lifecycle_state_machine.md` - 41 lines - terminal lifecycle states, owning gates, ordering, and current non-reopen accounting.
  - `phase4_reopen_lifecycle_synthesis.md` - 71 lines - canonical Phase 4 reopen-path synthesis and future reopen conjunction.
  - `target_robustness_stress_test.md` - 35 lines - robustness stress-test purpose, target classes, blockers, and replay instructions.
- Cycle 26-28 additions:
  - `campaign_deferral_watchlist.md` - 58 lines - current claim dispositions, future triggers, insufficient substitutes, and trigger ownership.
  - `campaign_closure_report.md` - 71 lines - reader-facing final campaign disposition and Phase 4 restart condition.
  - `campaign_executive_summary.md` - 29 lines - concise closure summary for non-cycle readers.
  - `closure_archive_index.md` - 109 lines - canonical endpoint artifact index with hashes, owners, regeneration commands, warnings, and invariants.
- Cycle 29-31 additions:
  - `toolchain_condition_report.md` - 58 lines - local tool availability, refreshed HDL check, compiled-Verilator blocker, and prototype-only interpretation report.
  - `campaign_invariant_report.md` - 54 lines - cross-artifact invariant coverage, contradiction count, ambiguity warnings, and no-new-gate statement.
  - `public_baseline_recency_report.md` - 48 lines - official MLPerf recency, source table, baseline materiality, and future-refresh boundary report.
- Cycle 32-34 additions:
  - `public_baseline_prior_refresh.md` - 66 lines - primary MLCommons source subset, campaign-term mapping, non-mappings, and conservative refresh decision.
  - `public_baseline_refresh_synthesis.md` - 36 lines - synthesis addendum integrating public-baseline recency and prior-refresh results into the canonical endpoint record.

## Generated Data and Figures

- Evidence-package lifecycle: `physicalized-weights/data/evidence_package_lifecycle_cases.csv`, `evidence_package_lifecycle_results.csv`, `evidence_package_lifecycle_summary.json`, `evidence_package_lifecycle_flow.png`.
- Phase 4 reopen synthesis: `physicalized-weights/data/phase4_reopen_claim_matrix.csv`, `phase4_reopen_manifest.csv`, `phase4_reopen_summary.json`, `phase4_reopen_lifecycle_flow.png`.
- Target robustness stress test: `physicalized-weights/data/target_robustness_cases.csv`, `target_robustness_results.csv`, `target_robustness_summary.json`, `target_robustness_frontier.png`.
- Campaign deferral watchlist: `physicalized-weights/data/campaign_deferral_watchlist.csv`, `campaign_deferral_watchlist_results.csv`, `campaign_deferral_watchlist_summary.json`, `campaign_deferral_watchlist.png`.
- Campaign closure package: `physicalized-weights/data/campaign_closure_claim_disposition.csv`, `campaign_closure_manifest.csv`, `campaign_closure_summary.json`, `campaign_closure_evidence_flow.png`.
- Closure archive index: `physicalized-weights/data/closure_archive_manifest.csv`, `closure_archive_manifest.json`, `closure_archive_summary.json`, `closure_archive_coverage.png`.
- Toolchain condition probe: `physicalized-weights/data/toolchain_condition_matrix.csv`, `toolchain_condition_summary.json`, `toolchain_condition_matrix.png`, `toolchain_verilator_lint.log`, `toolchain_yosys_eval.log`, `toolchain_yosys_synthesis.log`, `toolchain_graphviz.log`.
- Campaign invariant checker: `physicalized-weights/data/campaign_invariant_matrix.csv`, `campaign_invariant_summary.json`, `campaign_invariant_matrix.png`.
- Public baseline recency probe: `physicalized-weights/data/public_baseline_sources.csv`, `public_baseline_delta_matrix.csv`, `public_baseline_recency_summary.json`, `public_baseline_delta_matrix.png`.
- Public baseline prior refresh: `physicalized-weights/data/public_baseline_mlperf_v6_subset.csv`, `public_baseline_campaign_mapping.csv`, `public_baseline_prior_refresh.csv`, `public_baseline_prior_refresh_summary.json`, `public_baseline_prior_refresh.png`.
- Public baseline synthesis addendum: `physicalized-weights/data/public_baseline_synthesis_claim_matrix.csv`, `public_baseline_synthesis_manifest.csv`, `public_baseline_synthesis_summary.json`, `public_baseline_synthesis_flow.png`.
- Operator evidence-pack dry-run: `physicalized-weights/data/operator_evidence_pack_manifest_template.json`, `operator_trace_template.csv`, `operator_provenance_attestation_template.md`, `evidence_pack_dryrun_cases.csv`, `evidence_pack_dryrun_results.csv`, `evidence_pack_dryrun_summary.json`, `evidence_pack_dryrun_status_matrix.png`.
- Intake rehearsal: `physicalized-weights/data/evidence_pack_intake_cases.csv`, `physicalized-weights/data/intake_rehearsal_packages/`, `evidence_pack_intake_rehearsal_results.csv`, `evidence_pack_intake_rehearsal_summary.json`, `evidence_pack_intake_rehearsal_flow.png`.
- Reopen uncertainty protocol: `physicalized-weights/data/reopen_uncertainty_cases.csv`, `reopen_uncertainty_results.csv`, `reopen_uncertainty_summary.json`, `reopen_uncertainty_margin_plot.png`.
- Earlier generated families remain: break-even model, target ranking, hybrid architecture, prototype classifier, HDL/closure evidence, final synthesis, Phase 2 calibration, workload traces, stronger baselines, Phase 2 downgrade, production measurement contract, production trace validator, reopen thresholds, trace-ingestion admissibility, end-to-end reopen pipeline, evidence-pack replay, Phase 3 reopen synthesis, and evidence-acquisition readiness.

## Cumulative Stats

- Total authored research scripts: 35
- Total authored research script lines: 15,311
- Total authored tests: 32
- Total authored test lines: 4,439
- Total authored HDL/support files: 4
- Total authored HDL/support lines: 241
- Total authored research docs and diagram sources: 34
- Total authored doc/source lines: 2,150
- Campaign deferral watchlist rows/results rows: 10 each
- Campaign closure claim rows: 7
- Campaign closure manifest rows: 31
- Closure archive canonical artifact rows: 54
- Closure archive missing canonical artifacts: 0
- Closure archive zero-size canonical artifacts: 0
- Toolchain condition matrix rows: 10
- Campaign invariant matrix rows: 49
- Campaign invariant contradictions: 0
- Public baseline source rows: 5
- Public baseline delta rows: 6
- Latest public MLPerf Inference release recorded: v6.0, 2026-04-01
- Public baseline prior-refresh MLCommons subset rows: 12
- Public baseline prior-refresh raw primary rows available: 520
- Public baseline prior-refresh mapping rows: 72
- Public baseline direct energy calibration rows: 0
- Public baseline direct safety-filter workload rows: 0
- Public baseline synthesis claim rows: 7
- Public baseline synthesis manifest rows: 11
- Evidence-package lifecycle cases/results rows: 15 each
- Phase 4 reopen claim rows: 10
- Phase 4 reopen manifest rows: 38
- Target robustness cases/results rows: 28 each
- Evidence-pack dry-run cases/results rows: 12 each
- Evidence-pack intake cases/results rows: 9 each
- Reopen uncertainty cases/results rows: 11 each
- Evidence-pack replay rows: 5
- Phase 3 reopen claim rows: 14
- Phase 3 reopen manifest rows: 29
- Evidence-acquisition criteria rows: 20
- Evidence-acquisition design rows: 10
- Evidence-acquisition result rows: 10
- Reopen-threshold rows: 10
- Trace-ingestion path rows: 8
- Reopen-pipeline result rows: 4
- Evidence manifest rows: 29
- Ledger events: 89
- Plan milestones: 33
- Active sub-topics: taxonomy and null hypothesis, break-even modeling, target ranking, hybrid safety-filter architecture, prototype safety-filter fast path, prototype verification closure, final evidence synthesis, Phase 2 calibration, workload/update traces, stronger baseline replay, Phase 2 synthesis downgrade, production measurement requirements, production trace schema and validator, reopen-threshold modeling, trace-ingestion path admissibility, end-to-end reopen pipeline, evidence-pack replay, Phase 3 reopen synthesis, evidence-acquisition readiness, operator evidence-pack dry-run, intake rehearsal, measured reopen uncertainty protocol, evidence-package lifecycle state machine, Phase 4 reopen synthesis, target robustness stress testing, campaign deferral watchlist, campaign closure package, closure archive index, toolchain condition probe, campaign invariant checker, public baseline recency probe, public baseline prior refresh, public baseline synthesis addendum, trigger-gated admission control/no-cycle state.

## Cross-References

- `physicalized_model_weights_long_exposure_prompt.md` -> `plan_of_record.md`: directive converted into goals, milestones, and out-of-scope constraints.
- `plan_of_record.md` -> `promise_ledger.jsonl`: milestone definitions mirrored by ledger events through `M-ARCHIVE-1` validation.
- `REFERENCES.md` -> `physicalized-weights/data/calibration_assumptions.csv`: references [7]-[10] provide public calibration bounds for Phase 2 and downstream reopen thresholds.
- `stronger_baseline_comparison.csv`, `workload_viability_overlay.csv`, `production_trace_schema.json`, and `local_overhead_summary.json` -> `reopen_thresholds.py`: current modeled margins become per-scenario reopen thresholds.
- `production_trace_schema.json` and `reopen_thresholds_summary.json` -> `trace_ingestion_path_evaluator.py`: schema and threshold contracts become admissibility scoring for candidate evidence sources.
- `production_trace_schema.json`, `reopen_thresholds.csv`, and `trace_ingestion_path_scores.csv` -> `reopen_pipeline_demo.py`: validation, threshold, and ingestion gates compose into the end-to-end reopen decision table.
- `reopen_pipeline_demo.py` -> `evidence_pack_replay.py`: package manifests add trace hashes, schema compatibility, provenance, privacy, source, ingestion path, and threshold-scenario declarations before downstream replay.
- `evidence_pack_replay.py` -> `evidence_pack_replay_harness.md`: replay outputs document valid-but-insufficient, threshold-evaluable, synthetic-crossing, missing-attestation, and bad-hash outcomes.
- `local_overhead_summary.json`, `production_trace_validation_summary.json`, `reopen_thresholds_summary.json`, `trace_ingestion_path_summary.json`, `reopen_pipeline_summary.json`, and `evidence_pack_replay_summary.json` -> `build_phase3_reopen_synthesis.py`: Phase 3 summaries are consolidated into the reopen-pathway claim matrix and report.
- `build_phase3_reopen_synthesis.py` -> `phase3_reopen_pathway_summary.md`, `final_synthesis.md`, and `reproducibility.md`: synthesis preserves zero current actual reopen candidates and records the full future reopen conjunction.
- `phase3_reopen_summary.json` -> `evidence_acquisition_readiness.py`: validated Phase 3 gates become pre-collection readiness criteria for proposed trace-acquisition designs.
- `evidence_acquisition_readiness.py` -> `evidence_acquisition_readiness.md`: readiness classifications separate collection-ready plans from repair-required, inadmissible, and diagnostic-only designs without treating plans as evidence.
- `evidence_acquisition_readiness.py` and `evidence_pack_replay.py` -> `evidence_pack_template_dryrun.py`: acquisition and replay requirements become operator-facing templates and dry-run blocking statuses.
- `evidence_pack_template_dryrun.py` -> `evidence_pack_intake_rehearsal.py`: template outputs become synthetic-safe package-local traces and manifests for handoff rehearsal.
- `evidence_pack_intake_rehearsal.py` -> `evidence_pack_replay.py`: preserved intake packages are delegated to replay, while handoff mutations are blocked before replay.
- `reopen_thresholds.py`, `evidence_pack_replay.py`, and `evidence_pack_intake_rehearsal.py` -> `reopen_uncertainty_protocol.py`: point threshold crossings are refined into an uncertainty-aware UCB rule while retaining all evidence-package gates.
- `evidence_acquisition_readiness.py`, `evidence_pack_template_dryrun.py`, `evidence_pack_intake_rehearsal.py`, `evidence_pack_replay.py`, `reopen_thresholds.py`, and `reopen_uncertainty_protocol.py` -> `evidence_package_lifecycle.py`: validated layer outputs become a deterministic package-state machine with terminal states and owning gates.
- `evidence_package_lifecycle.py` -> `build_phase4_reopen_synthesis.py`: lifecycle states, candidate accounting, and the hypothetical positive branch are folded into the canonical Phase 4 claim matrix and final synthesis.
- `target_scoring.py`, `stronger_baseline_model.py`, and `build_phase4_reopen_synthesis.py` -> `target_robustness_stress.py`: target classes and stronger-baseline framing are stress-tested across calibrated, favorable-plausible, extreme-counterfactual, and special-control regimes.
- `build_phase4_reopen_synthesis.py` and `target_robustness_stress.py` -> `build_campaign_deferral_watchlist.py`: validated no-current-superiority and no-current-reopen outcomes become trigger governance for future measured evidence, baseline refreshes, prototype-only checks, and insufficient substitutes.
- `build_campaign_deferral_watchlist.py`, `build_phase4_reopen_synthesis.py`, and `target_robustness_stress.py` -> `build_campaign_closure_report.py`: deferral state, Phase 4 reopen conditions, and robustness results are consolidated into the reader-facing campaign closure package.
- `build_campaign_closure_report.py`, `build_campaign_deferral_watchlist.py`, and upstream canonical summaries -> `build_closure_archive_index.py`: closure claim supports and endpoint artifacts are indexed by milestone, artifact class, file size, SHA-256 hash, and regeneration command while preserving zero current superiority claims and zero actual reopen candidates.
- `verify_prototype_closure.py`, `safety_filter_core.sv`, `run_yosys_eval.py`, `safety_filter_core.ys`, and `safety_filter_core_tb.cpp` -> `toolchain_condition_probe.py`: prototype evidence is refreshed against current Verilator/Yosys/Graphviz availability while compiled simulation remains blocked by missing `make` and C++ compiler support.
- Canonical Phase 2, Phase 3, Phase 4, robustness, deferral, closure, archive, and toolchain summaries -> `campaign_invariant_checker.py`: endpoint counters and report wording are checked for contradictions without creating a new scientific criterion.
- `REFERENCES.md`, `stronger_baseline_summary.json`, `stronger_baseline_comparison.csv`, and `phase2_synthesis_summary.json` -> `public_baseline_recency_probe.py`: newer official MLCommons benchmark sources are screened for programmable-baseline drift while preserving no measured hybrid reopen.
- `public_baseline_sources.csv`, `REFERENCES.md`, and MLCommons v6.0 `summary_results.json` -> `public_baseline_prior_refresh.py`: primary public benchmark rows become bounded throughput-prior context while direct energy calibration, safety-filter workload comparability, and measured hybrid reopen credit remain blocked.
- `public_baseline_recency_summary.json`, `public_baseline_prior_refresh_summary.json`, `public_baseline_campaign_mapping.csv`, and `phase2_synthesis_summary.json` -> `build_public_baseline_synthesis.py`: validated public-baseline drift and prior-refresh outputs are integrated into the canonical synthesis as programmable-baseline prior context, with the Phase 2 downgrade preserved and the Phase 4 reopen condition unchanged.
