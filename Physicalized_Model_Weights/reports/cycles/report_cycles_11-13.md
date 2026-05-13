---
title: "Physicalized Model Weights - cycles 11-13"
date: "2026-05-13"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Physicalized Model Weights - cycles 11-13

## Abstract

Cycles 11-13 converted the prior Phase 2 downgrade into a machine-checkable research record and then defined the only accepted path for reopening the safety/filter physicalization claim. The central conclusion did not change: under current calibrated assumptions, the tested hybrid physicalized safety/filter does not beat strong programmable baselines.

Cycle 11 (`M-SYNTH-2`) regenerated the final claim set after calibrated workload and stronger-baseline replay. The claim that a physicalized safety/filter is a performance or economic winner was marked `falsified`; the architecture and failure-mode study remained useful.

Cycle 12 (`M-MEASURE-1`) defined which production measurements would be required before the claim could be reconsidered. It also built a deterministic local proxy benchmark, but explicitly labeled local timings as proxy evidence rather than production energy or accelerator evidence.

Cycle 13 (`M-TRACE-1`) defined a production trace schema and validator. The validator prevents incomplete telemetry, proxy-only energy, privacy-risk columns, missing baselines, inconsistent policy windows, zero-volume/all-fallback controls, and failed fast-path guardrails from reopening the Phase 2 downgrade.

## Introduction

The long-exposure directive asks whether useful parts of neural-network inference can be "physicalized" into hardware instead of repeatedly executed as software kernels over programmable CPU/GPU memory hierarchies. Earlier cycles narrowed the plausible target from broad fixed frontier-model weights to a small safety/filter classifier wrapped by programmable fallback, update, audit, health, drift, and rollback controls.

Cycles 8-10 then weakened and finally downgraded that narrow claim. Calibration used public memory/energy and accelerator references [7]-[10], synthetic workload traces, and a stronger programmable-accelerator replay. The result was that the hybrid physicalized safety/filter won zero of the Phase 2 workload scenarios once it was compared against optimized software/runtime and programmable accelerator baselines under the same feature, audit, fallback, update, and utilization accounting.

Cycles 11-13 focused on making that downgrade durable. They did not broaden the hardware design. Instead, they recorded the revised claim set and created a measurement and trace-validation contract for any future production evidence.

## Approach

The work proceeded in dependency order.

Cycle 11 synthesized the validated Phase 2 evidence from `M-CAL-1`, `M-WORKLOAD-1`, and `M-SWBASE-2`. It produced a claim matrix, summary JSON, evidence-map figure, and final-synthesis addendum. Source sessions: researcher `7f0ef26d-4887-488e-98c9-a3ec5c282b3c`, worker `db71b3c9-33d7-4759-849d-6ee8a9c3a52b`, auditor `53eb984f-f98e-40b8-b50a-a735b948078e`.

Cycle 12 translated the downgrade into a production measurement contract. It listed each quantity needed to reconsider the claim and separated local proxy timing from production-required measurements. Source sessions: researcher `811248ea-aa50-4095-83df-f872b4d075c1`, worker `d2aac54a-07fb-4a32-aa44-08a5c184da99`, auditor `4fe444e7-f722-4ffb-8aa1-02450b64e34e`.

Cycle 13 translated the measurement contract into a production serving-trace schema and validator. It defined required fields, privacy boundaries, status classes, summary metrics, and reopen eligibility. Source sessions: researcher `a772f471-b07e-469a-937a-06f50dbb043d`, worker `6a5ca9ba-2380-495b-b3ab-51fd19ba6e70`, auditor `65bdd67e-6ce6-484d-aae3-da9ae0aff588`.

## Findings

### Cycle 11: Phase 2 Downgrade Became the Current Claim Set

Cycle 11 added milestone `M-SYNTH-2` and built `physicalized-weights/scripts/build_phase2_synthesis.py`. The script consumes the calibrated break-even summary, workload summary, stronger-baseline summary, and stronger-baseline comparison table. It emits:

- `physicalized-weights/data/phase2_claim_matrix.csv`
- `physicalized-weights/data/phase2_synthesis_summary.json`
- `physicalized-weights/data/phase2_evidence_map.png`
- `physicalized-weights/docs/phase2_synthesis_downgrade.md`

The key result is direct: hybrid physicalized safety/filter wins zero Phase 2 workload scenarios. The programmable accelerator wins nine of ten scenarios, and optimized software wins the zero-invocation control. The previously preserved high-volume stable moderation case flips to `programmable_accelerator`.

![Phase 1 and Phase 2 claim statuses, showing which claims were preserved, weakened, falsified, or superseded after calibrated workload and stronger-baseline replay.](physicalized-weights/data/phase2_evidence_map.png)

The claim matrix records nine claims. The safety/filter architecture and failure-mode study is preserved as useful, but the performance/economic superiority claim is `falsified`. The Phase 1 target-ranking superiority language is `superseded`, meaning the earlier target ranking no longer justifies hardware-superiority language without stronger-baseline replay or production measurements.

The auditor validated `M-SYNTH-2` without code fixes. Validation included the synthesis builder, Phase 2 tests, final synthesis tests, PNG check, `promise_check`, and `org_check`. The remaining warnings were pre-existing orphan report artifacts and root-file organization warnings.

### Cycle 12: Production Measurements Were Defined Before Any Reopen

Cycle 12 added milestone `M-MEASURE-1` and built a local proxy harness in `physicalized-weights/scripts/local_overhead_benchmark.py`. The harness uses the ten validated workload scenarios from `M-WORKLOAD-1` and measures local host/Python timing proxies for six components:

- feature extraction
- fixed classifier evaluation
- optimized software classifier evaluation
- route/fallback decision
- audit serialization
- append-only audit write

The summary reports 10 scenarios, 6 components, and `control_overhead_dominates_fixed_classifier: true`. Current generated median proxy timings in `physicalized-weights/data/local_overhead_summary.json` are:

| Component | Median ns/request |
|---|---:|
| append-only audit write proxy | 20538.441 |
| audit serialization proxy | 17367.176 |
| feature extraction proxy | 10437.758 |
| optimized software classifier proxy | 8763.939 |
| route/fallback decision proxy | 5667.545 |
| fixed classifier proxy | 5160.697 |

![Local proxy latency distributions by overhead component and workload scenario, separating measured timing proxies from production-only energy and accelerator quantities.](physicalized-weights/data/local_overhead_latency_distribution.png)

The measurement gap matrix is the important artifact. It marks feature extraction latency, audit serialization/logging latency, fallback dispatch timing, and optimized software classifier timing as local proxies. It marks feature extraction energy, audit storage cost, optimized software energy, programmable accelerator latency, programmable accelerator energy, accelerator utilization/batching, and durable hybrid margin as production-required or not measured.

The auditor validated `M-MEASURE-1` without fixes. The decision was that the cycle created the intended evidence contract while preserving the Phase 2 downgrade. Local Python timing decomposes overheads; it does not measure production accelerator energy, utilization, or durable hybrid superiority.

### Cycle 13: Production Trace Validation Closed the Reopen Loopholes

Cycle 13 added milestone `M-TRACE-1` and produced a machine-readable production trace contract. The main artifacts are:

- `physicalized-weights/docs/production_trace_schema.md`
- `physicalized-weights/data/production_trace_schema.json`
- `physicalized-weights/scripts/production_trace_validator.py`
- `physicalized-weights/tests/test_production_trace_validator.py`
- `physicalized-weights/data/example_production_trace_valid.csv`
- `physicalized-weights/data/example_production_trace_invalid.csv`
- `physicalized-weights/data/production_trace_validation_summary.json`
- `physicalized-weights/data/production_trace_validation_report.csv`
- `physicalized-weights/data/production_trace_evidence_coverage.png`

A trace can be a `valid_reopen_candidate` only if it has nonzero requests, nonzero accepted physicalized fast-path requests, measured accelerator energy, measured hybrid energy, required software and accelerator baseline latency fields, audit fields, passing health and drift gates for accepted fast-path rows, and a consistent policy window.

The current synthetic valid fixture is intentionally not a reopen candidate. It has 6 requests, 4 accepted fast-path requests, fallback frequency `0.333333`, and audit logging rate `1.0`, but it is blocked by proxy hybrid energy and synthetic environment status. The invalid fixture is rejected for privacy-risk content, missing accelerator baseline latency, negative feature-extraction latency, and inconsistent policy versions.

![Coverage of required production-trace evidence fields, separating valid measured evidence, proxy-only evidence, missing baseline evidence, and privacy/schema failures.](physicalized-weights/data/production_trace_evidence_coverage.png)

The auditor found and fixed one moderate issue. Before the fix, the validator could count physicalized fast-path rows even when `health_gate_passed=false`, `drift_gate_passed=false`, or `audit_logged=false`. The fix tightened fast-path credit so accepted fast-path evidence requires `fallback_taken=false`, `audit_logged=true`, `health_gate_passed=true`, and `drift_gate_passed=true`. A regression test, `test_fast_path_credit_requires_audit_and_passing_gates`, was added.

After the fix, all eight production trace validator tests passed, the coverage figure was confirmed as a valid 900 x 460 RGB PNG, and the auditor validated `M-TRACE-1`.

## Discussion

Cycles 11-13 change the research record from "a narrow physicalized safety/filter might win under bounded conditions" to "the current modeled case is downgraded, and only production-quality evidence can reopen it." This is a stricter result than simply saying more data is needed. The project now specifies exactly what future data must contain and how it will be rejected if it is incomplete.

The strongest preserved claim is architectural: a fixed safety/filter block can still be studied as a bounded component behind programmable controls. The rejected claim is economic or performance superiority against strong programmable baselines under the current assumptions.

The reopen pathway now has two halves. `M-MEASURE-1` says what must be measured: production feature extraction, audit cost, fallback behavior, update cadence, utilization, software baseline latency/energy, programmable accelerator latency/energy, and durable margin. `M-TRACE-1` says how future traces must encode those quantities before they can affect the claim.

No real production trace was ingested in these cycles. The valid trace is synthetic, and the local timing harness is a proxy. Those artifacts are useful as contracts and validators, not as production evidence.

## Open Questions

The main open question is whether any real production workload can satisfy the validator and show a durable positive hybrid margin against optimized software and programmable accelerator baselines.

The required missing evidence is:

- measured feature extraction latency and energy on identical request features
- measured audit serialization, storage, retention, and synchronization cost
- measured fallback dispatch latency and queueing under load
- measured optimized software classifier latency and energy
- measured programmable accelerator latency, energy, utilization, batching, and host-transfer behavior
- real policy update, rollback, drift, health alarm, fallback, and near-threshold rates
- production traces that pass the privacy, schema, baseline, gate, audit, energy, and policy consistency checks

The compiled Verilator simulation gap from earlier prototype work remains a future superseding check if build tooling becomes available. It was not reopened in cycles 11-13.

## References

[7] Mark Horowitz, "1.1 Computing's Energy Problem (and What We Can Do about It)," 2014 IEEE International Solid-State Circuits Conference Digest of Technical Papers (ISSCC), 2014. https://doi.org/10.1109/ISSCC.2014.6757323

[8] Mark Horowitz, "Computing's Energy Problem (and What We Can Do about It)," slide transcript/mirror of ISSCC 2014 energy table. https://doczz.net/doc/9135487/computing-s-energy-problem--and-what-we-can-do-about-it-

[9] NVIDIA, "NVIDIA H100 Tensor Core GPU," product specification page. https://www.nvidia.com/en-us/data-center/h100/

[10] MLCommons, "MLPerf Inference: Datacenter benchmark documentation," MLCommons. https://docs.mlcommons.org/inference/

## Appendix: Implementation Details

### Code Organization

Cycle 11 added the Phase 2 synthesis package:

- `physicalized-weights/scripts/build_phase2_synthesis.py` - 288 lines
- `physicalized-weights/tests/test_phase2_synthesis.py` - 98 lines
- `physicalized-weights/docs/phase2_synthesis_downgrade.md` - 40 lines

Cycle 12 added the production measurement package:

- `physicalized-weights/scripts/local_overhead_benchmark.py` - 449 lines
- `physicalized-weights/tests/test_local_overhead_benchmark.py` - 120 lines
- `physicalized-weights/docs/production_measurement_requirements.md` - 43 lines

Cycle 13 added the production trace package:

- `physicalized-weights/scripts/production_trace_validator.py` - 410 lines
- `physicalized-weights/tests/test_production_trace_validator.py` - 212 lines
- `physicalized-weights/docs/production_trace_schema.md` - 54 lines

The workspace manifest was updated to include the new scripts, tests, generated artifacts, cumulative counts, and cross-reference chain through `M-TRACE-1`.

### Generated Data and Figures

Cycle 11 generated:

- `physicalized-weights/data/phase2_claim_matrix.csv` - 9 claim rows
- `physicalized-weights/data/phase2_synthesis_summary.json`
- `physicalized-weights/data/phase2_evidence_map.png` - valid PNG, 900 x 460 RGB

Cycle 12 generated:

- `physicalized-weights/data/local_overhead_benchmark.csv` - 60 benchmark rows
- `physicalized-weights/data/local_overhead_summary.json`
- `physicalized-weights/data/measurement_gap_matrix.csv` - 13 measurement-gap rows
- `physicalized-weights/data/local_overhead_latency_distribution.png` - valid PNG, 900 x 460 RGB
- `physicalized-weights/data/local_overhead_benchmark_audit.jsonl`

Cycle 13 generated:

- `physicalized-weights/data/production_trace_schema.json`
- `physicalized-weights/data/example_production_trace_valid.csv` - 6 synthetic request rows
- `physicalized-weights/data/example_production_trace_invalid.csv` - 3 synthetic request rows
- `physicalized-weights/data/production_trace_validation_summary.json`
- `physicalized-weights/data/production_trace_validation_report.csv` - 2 trace report rows
- `physicalized-weights/data/production_trace_evidence_coverage.png` - valid PNG, 900 x 460 RGB

### Test Results

Reported and audited validation commands for these cycles passed:

- `python3 physicalized-weights/scripts/build_phase2_synthesis.py`
- `python3 physicalized-weights/tests/test_phase2_synthesis.py`
- `python3 physicalized-weights/tests/test_final_synthesis.py`
- `python3 physicalized-weights/scripts/local_overhead_benchmark.py`
- `python3 physicalized-weights/tests/test_local_overhead_benchmark.py`
- `python3 physicalized-weights/scripts/production_trace_validator.py physicalized-weights/data/example_production_trace_valid.csv physicalized-weights/data/example_production_trace_invalid.csv`
- `python3 physicalized-weights/tests/test_production_trace_validator.py`
- `file` checks for all three cycle figures
- `python3 -m long_exposure.tools.promise_check .`
- `python3 -m long_exposure.tools.org_check .`

Current `promise_check` reports 33 events and 13 plan milestones. Remaining warnings are pre-existing orphan report artifacts under `reports/cycles/`. Current `org_check` warnings are pre-existing root files: `physicalized_model_weights_long_exposure_prompt.md` and `physicalized_weights_long_exposure_live.log`.

### Session References

Cycle 11:

- Researcher: `7f0ef26d-4887-488e-98c9-a3ec5c282b3c`
- Worker: `db71b3c9-33d7-4759-849d-6ee8a9c3a52b`
- Auditor: `53eb984f-f98e-40b8-b50a-a735b948078e`

Cycle 12:

- Researcher: `811248ea-aa50-4095-83df-f872b4d075c1`
- Worker: `d2aac54a-07fb-4a32-aa44-08a5c184da99`
- Auditor: `4fe444e7-f722-4ffb-8aa1-02450b64e34e`

Cycle 13:

- Researcher: `a772f471-b07e-469a-937a-06f50dbb043d`
- Worker: `6a5ca9ba-2380-495b-b3ab-51fd19ba6e70`
- Auditor: `65bdd67e-6ce6-484d-aae3-da9ae0aff588`

### Cross-Reference Map

`M-SWBASE-2` produced the decisive stronger-baseline result: zero hybrid wins, nine programmable accelerator wins, and one optimized software win.

`M-SYNTH-2` consumed `M-CAL-1`, `M-WORKLOAD-1`, and `M-SWBASE-2` outputs to generate the Phase 2 claim matrix and final-synthesis addendum.

`M-MEASURE-1` consumed the validated workload scenarios and Phase 2 downgrade to define measurement requirements and local proxy timing outputs.

`M-TRACE-1` consumed the production measurement requirements to define trace fields, privacy limits, units, reopen eligibility, and validator outputs.

The final state after cycle 13 is validated and downgraded: physicalized safety/filter remains a bounded architecture and failure-mode study, but current evidence does not support it as a performance or economic winner against strong programmable baselines.
