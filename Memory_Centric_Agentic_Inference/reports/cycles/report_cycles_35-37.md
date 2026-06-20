---
title: "Memory-Centric Agentic Inference — cycles 35-37"
date: "2026-05-12"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 35-37

## Abstract

Cycles 35-37 continued the production-evidence hardening path for the memory-centric agentic inference project. The campaign had already built a memory-centric architecture package and a long chain of synthetic, proxy, fixture, and preflight gates. The remaining question was not whether those fixtures could produce an architectural recommendation, but what would be required before a real production deployment could support one.

Cycle 35 added `M-CAUSAL-1`, a causal attribution and control-arm validity gate. This gate prevents robust-looking threshold results from becoming readiness evidence when the comparison against the Option A control is confounded or unidentified. Cycle 36 added `M-PRODREPLAY-1`, an executable replay surface for real `production_target` telemetry. The audit found and fixed a critical over-credit path in which a future manifest could self-assert every gate boolean without linking to validated evidence artifacts. After the fix, a production-target claim-support candidate requires both `evidence_label=production_target` and an existing evidence artifact path for every passed gate. Cycle 37 supplied session IDs, but the available workspace record contains no separate technical artifact, script, data file, figure, or ledger event for that cycle.

The current result is conservative: causal validity and production-target replay are now represented explicitly, but no production architecture endorsement has been made. The workspace still contains zero real production-target manifests, zero claim-support candidates, and zero current rows with `production_calibrated=true`, `production_ready=true`, or `claim_credit_allowed=true`.

## Introduction

The overall research program asks whether future AI infrastructure should be organized around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier cycles produced a taxonomy of agentic workloads, lifetime and cost models, simulation harnesses, architecture options, trace schemas, runtime prototypes, security gates, calibration maps, production telemetry schemas, and operator-facing preflight tools. Public accelerator, interconnect, storage, benchmark, prefix-cache, semantic-cache, CPU, and CXL references remain the external context for that broader package [1]-[14].

By cycles 35-37, the work had moved from architecture modeling into evidentiary control. Previous gates had already established that fixture, proxy, adapter, conformance, intake, attestation, trust-policy, gatechain, deployment-root, timebase, redaction, and uncertainty artifacts are useful only as preconditions. They cannot by themselves upgrade Option B or Option C from contract-ready architecture options into production-ready claims.

Cycle 35 addressed one remaining scientific gap: a threshold result can be statistically robust and still causally invalid if the treatment and control arms are not comparable. Cycle 36 addressed the operational replay gap: even if a future operator supplies a `production_target` bundle, the replay surface must distinguish absence, rejection, and claim-support candidacy without allowing manifest-only self-attestation. Cycle 37 is recorded here as a reporting boundary because no separate technical workspace artifact was found.

Source traceability is by supplied session ID. The reporter did not have callable `search_sessions` or `list_session_catalog` tools in this runtime, so the report uses the supplied session IDs as anchors and relies on workspace artifacts, ledger records, validation outputs, and the supplied audit report for technical content.

## Approach

The cycle range was consolidated chronologically.

Cycle 35 sources were the supplied researcher, worker, and auditor session IDs; ledger entries for `M-CAUSAL-1`; `memory-centric-agentic/causal_attribution.md`; the causal fixture builder, evaluator, plotter, verifier, CSV outputs, and figures; and the current manifest snapshot. The relevant session IDs are:

| Role | Session ID |
|---|---|
| Cycle 35 researcher | `88c633b4-3363-4a7a-92d5-eade5dbdca02` |
| Cycle 35 worker | `e784f362-2075-485d-8c6c-3734c55a613f` |
| Cycle 35 auditor | `3274c023-4fe2-4930-ac45-6c0e014218bb` |

Cycle 36 sources were the supplied researcher, worker, and auditor session IDs; ledger entries for `M-PRODREPLAY-1`; `memory-centric-agentic/production_target_replay.md`; replay, plotting, and verifier scripts; generated replay CSVs and figures; and the supplied audit report. The relevant session IDs are:

| Role | Session ID |
|---|---|
| Cycle 36 researcher | `5d165de9-4dfd-4f37-a33c-e9174ae00e9c` |
| Cycle 36 worker | `ecafd12e-5b5b-4c29-945b-123b22bdc8b2` |
| Cycle 36 auditor | `a6480a34-0633-4f07-bcec-6285f6a384dc` |

Cycle 37 sources were the supplied session IDs plus a workspace search across the ledger, plan, manifest, reports, project notes, scripts, tests, and data. No cycle-37 technical artifact was found in the available workspace record.

| Role | Session ID |
|---|---|
| Cycle 37 researcher | `691b573c-292d-467b-b706-5e0a0374a5ae` |
| Cycle 37 worker | `3ba0f71b-84af-417f-b565-aed06825efb0` |
| Cycle 37 auditor | `b59e643d-811a-4dfd-99a2-1f0d0f0f6ac9` |

## Findings

### Context Before Cycle 35

Before cycle 35, the project had already built a production-evidence chain around the architecture package. The chain included deployment-root enrollment, attestation, operator trust policy, intake custody, adapter conformance, production-shaped telemetry ingestion, gatechain replay, timebase integrity, redaction integrity, and statistical uncertainty propagation.

The immediate predecessor, `M-UNCERT-1`, established that confidence-qualified threshold replay is required before readiness updates. Its evaluated outcomes include `robust_pass`, `robust_fail`, `statistically_indeterminate`, and `statistical_invalid`. That mattered for cycle 35 because statistical robustness alone was still insufficient: a threshold result could be statistically strong but causally confounded.

### Cycle 35: Causal Attribution and Control-Arm Validity

Cycle 35 added `M-CAUSAL-1`, a causal validity gate after statistical uncertainty and before any claim-support boundary.

The gate treats the memory-centric intervention, usually Option B or Option C placement and reuse, as the treatment. Outcomes are latency, byte-movement, energy, or planner-value deltas. The required pre-treatment confounders include workload mix, object size, tenant concurrency, hardware topology, model/runtime version, cache warmness, security-deny rate, time-window load, and scheduler pressure.

The minimum control-arm contract is an Option A control with declared pre-treatment covariates. Matching or blocking is required on workload, model, topology, and time windows. Standardized mean differences must stay at or below 0.10 for workload, object, tenant, cache, and scheduler fields. Security-deny-rate delta must stay at or below 0.02. Time drift must stay at or below 0.10. Positivity overlap must be at least 0.80.

The gate explicitly forbids post-treatment adjustment using cache hits, reuse counts, or scheduler outcomes. Those can be mechanisms of the memory-centric treatment rather than independent controls.

The evaluator separates robust statistical effects into three causal classes:

| Causal class | Meaning |
|---|---|
| `causally_admissible` | The control-arm contract is satisfied. |
| `causally_confounded` | A robust-looking effect is blocked because treatment and control are imbalanced. |
| `causally_unidentified` | The result lacks required controls, covariate contracts, positivity, or valid adjustment structure. |

The generated outputs were:

| Artifact | Rows |
|---|---:|
| `data/causal_attribution_schema.csv` | 16 |
| `data/causal_valid_fixture.csv` | 2 |
| `data/causal_invalid_fixtures.csv` | 14 |
| `data/causal_confounder_sensitivity_grid.csv` | 48 |
| `data/causal_required_covariates.csv` | 10 |
| `data/causal_attribution_results.csv` | 16 |
| `data/causal_failure_modes.csv` | 14 |
| `data/causal_threshold_boundary.csv` | 16 |
| `data/causal_claim_readiness_boundary.csv` | 16 |

The auditor validated `M-CAUSAL-1` without requiring a code patch. The audit record states that robust-but-confounded effects are blocked from readiness updates; missing controls, positivity failure, missing covariate contracts, and post-treatment adjustment fail closed as unidentified; and every fixture row keeps `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`.

![Causal confounder sensitivity grid showing where robust statistical effects remain causally admissible or become blocked.](data/causal_confounder_sensitivity.png)

![Fail-closed causal attribution failure modes for confounded and unidentified cases.](data/causal_failure_modes.png)

![Causal admissibility remains a scientific precondition and grants no current production claim credit.](data/causal_claim_boundary.png)

### Cycle 36: Real Production-Target Replay and Claim-Support Boundary

Cycle 36 added `M-PRODREPLAY-1`, the executable boundary between real production telemetry, rejected non-production evidence, and possible future claim-support candidacy.

The replay scans `data/production_target_bundle/` for `manifest.json` or `manifest.csv`. If no production-target manifest exists, it emits `no_real_telemetry_available`. In the current workspace, the absence report shows:

| Field | Value |
|---|---|
| Search root | `data/production_target_bundle` |
| Manifest count | 0 |
| Production-target manifest count | 0 |
| Absence state | `no_real_telemetry_available` |
| Blocked reason | `no_production_target_bundle_found` |

The replay order is fixed:

1. Root enrollment.
2. Attestation envelope.
3. Trust policy.
4. Intake custody.
5. Adapter/conformance normalization.
6. Timebase and observer-overhead integrity.
7. Redaction and join preservation.
8. Evidence gatechain replay.
9. Uncertainty qualification.
10. Causal attribution.
11. DC-001/DC-002 threshold replay.
12. Planner/readiness boundary.
13. Final handoff traceability.

The worker implementation initially built the replay coordinator, plotter, verifier, operator note, absence report, gate trace, claim boundary, and negative-control handling. Non-production labels are rejected at `evidence_label`; rejected and absent paths get no threshold attempt, no readiness update, no production calibration, no production readiness, and no claim credit.

The audit found one critical defect. A future `production_target` manifest could self-assert all gate booleans and become a claim-support candidate without linking to evidence artifacts from the validated gates. That would have over-credited manifest-only evidence.

The fix changed `scripts/run_production_target_replay.py` so each passed production gate must also name an existing `<gate_field>_evidence_path`. The verifier now injects a forged all-true `production_target` manifest with no evidence paths and confirms that it rejects at `root_enrollment` with `missing_root_enrollment_evidence` and zero credit. The operator note was updated to document the evidence-artifact requirement.

Current outputs after the audit patch are:

| Artifact | Rows |
|---|---:|
| `data/production_target_replay_results.csv` | 17 |
| `data/production_target_replay_gate_trace.csv` | 1 |
| `data/production_target_replay_claim_boundary.csv` | 17 |
| `data/production_target_replay_absence_report.csv` | 1 |

The supplied audit report states that there are zero claim-support candidates and that all current rows have `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`.

![Production-target replay gate trace showing current absence rather than a passed production chain.](data/production_target_replay_gate_trace.png)

![Production-target replay claim boundary showing zero current production calibration, readiness, claim credit, or automatic architecture endorsement.](data/production_target_replay_claim_boundary.png)

### Cycle 37: Reporting Boundary and Source-Record Gap

Cycle 37 supplied researcher, worker, and auditor session IDs, but the available workspace record contains no separate cycle-37 milestone, markdown note, script, test, CSV, figure, or ledger event.

This is reported as a source-record gap, not as a technical defect in the cycle-35 or cycle-36 artifacts. The searched materials included `promise_ledger.jsonl`, `plan_of_record.md`, `MANIFEST.md`, `reports/cycles/`, `memory-centric-agentic/`, `scripts/`, `tests/`, and `data/`.

## Discussion

The main technical movement in cycles 35-37 was a shift from “does the architecture option look good under modeled or fixture evidence?” to “what would make a real production claim admissible?”

Cycle 35 closed the causal validity gap. The project already had statistical uncertainty handling, but confidence intervals do not prove that the memory-centric intervention caused the observed improvement. `M-CAUSAL-1` makes the Option A control explicit and blocks robust-looking results when workload mix, model version, topology, tenant concurrency, object-size distribution, cache warmness, scheduler load, security-deny rate, or time windows make the comparison invalid.

Cycle 36 closed the replay-surface gap. The project already had individual gates, but a future production manifest needed a single executable path through those gates. `M-PRODREPLAY-1` now provides that path while preserving a hard distinction between three states: no real telemetry, rejected evidence, and possible future claim-support candidacy. The audit patch is central to that distinction because it prevents a manifest from replacing the evidence chain with self-reported booleans.

The architecture stance remains unchanged. Option A remains the validated conventional baseline and control path. Option B and Option C remain contract-ready memory-centric options for object-aware runtime management and trajectory/DAG-aware memory fabrics, but they are not production recommendations yet. A production upgrade still requires real joined telemetry that passes every root, custody, measurement-quality, privacy, statistical, causal, threshold, planner, and handoff gate.

## Open Questions

The next non-redundant advancement requires actual trusted `production_target` telemetry or an operator integration task that produces real gate evidence artifacts.

The required production evidence includes deployment-root enrollment, attestation, trust policy, intake custody, adapter conformance, timebase validity, redaction admissibility, gatechain replay, uncertainty qualification, causal admissibility, DC-001/DC-002 threshold replay, planner/readiness boundary, and final handoff traceability.

The core open question is no longer whether more synthetic gates can be added. The current record already says additional synthetic gates are likely diminishing returns unless they test a new fail-closed boundary. The open research question is whether real production rows, under target accelerator and memory hierarchy conditions, show that memory-centric placement or trajectory/DAG management improves latency, energy, bytes moved, capacity pressure, or planner value enough to justify Option B or Option C.

## References

[1] NVIDIA, "NVIDIA H100 Tensor Core GPU," NVIDIA Data Center, accessed 2026-05-11. https://www.nvidia.com/en-us/data-center/h100/

[2] NVIDIA, "NVIDIA H200 Tensor Core GPU," NVIDIA Data Center, accessed 2026-05-11. https://www.nvidia.com/en-us/data-center/h200/

[3] NVIDIA, "NVIDIA DGX B200: The Foundation for Your AI Factory," NVIDIA Data Center, accessed 2026-05-11. https://www.nvidia.com/en-gb/data-center/dgx-b200/

[4] NVIDIA, "Introduction to NVIDIA DGX H100/H200 Systems," NVIDIA DGX H100/H200 User Guide, accessed 2026-05-11. https://docs.nvidia.com/dgx/dgxh100-user-guide/introduction-to-dgxh100.html

[5] PCI-SIG, "PCI Express 6.0 Specification," PCI-SIG, accessed 2026-05-11. https://pcisig.com/pci-express-6.0-specification

[6] NVM Express, "Specifications," NVM Express, accessed 2026-05-11. https://nvmexpress.org/specifications/

[7] Compute Express Link Consortium, "CXL Specification," Compute Express Link, accessed 2026-05-11. https://computeexpresslink.org/cxl-specification/

[8] MLCommons, "MLPerf Inference: Datacenter Benchmark," MLCommons, accessed 2026-05-11. https://mlperf.pw/benchmarks/inference-datacenter/index.html

[9] Woosuk Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention," arXiv, 2023. https://arxiv.org/abs/2309.06180

[10] Intel, "Intel Xeon 6 Processors with MRDIMM — Solution Brief," Intel, accessed 2026-05-11. https://www.intel.com/content/www/us/en/content-details/919018/intel-xeon-6-processors-with-mrdimm-solution-brief.html

[11] AMD, "AMD EPYC 9005 Processor Architecture Overview," AMD, accessed 2026-05-11. https://www.amd.com/content/dam/amd/en/documents/epyc-technical-docs/user-guides/58462_amd-epyc-9005-tg-architecture-overview.pdf

[12] vLLM Project, "Automatic Prefix Caching," vLLM Documentation, accessed 2026-05-11. https://docs.vllm.ai/en/latest/design/prefix_caching/

[13] Sajal Regmi and Chetan Phakami Pun, "GPT Semantic Cache: Reducing LLM Costs and Latency via Semantic Embedding Caching," arXiv, 2024. https://arxiv.org/abs/2411.05276

[14] CXL Consortium, "CXL Consortium Releases Compute Express Link 2.0 Specification," Business Wire, 2020. https://www.businesswire.com/news/home/20201110005037/en/CXL-Consortium-Releases-Compute-Express-Link-2.0-Specification

## Appendix: Implementation Details

### Code Organization

Cycle 35 added or used the following causal attribution files:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_causal_attribution_fixtures.py` | 250 | Builds causal schema, fixtures, confounder grid, and required covariates. |
| `scripts/evaluate_causal_attribution.py` | 239 | Evaluates admissible, confounded, and unidentified cases. |
| `scripts/plot_causal_attribution.py` | 99 | Renders causal sensitivity, failure-mode, and claim-boundary figures. |
| `tests/verify_causal_attribution.py` | 122 | Verifies causal outputs, failure cases, boundaries, and figures. |
| `memory-centric-agentic/causal_attribution.md` | 17 | Documents the causal gate and non-production boundary. |

Cycle 36 added or used the following production replay files:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/run_production_target_replay.py` | 352 | Replays production-target manifests through the full evidence chain. |
| `scripts/plot_production_target_replay.py` | 76 | Renders replay gate-trace and claim-boundary figures. |
| `tests/verify_production_target_replay.py` | 145 | Verifies absence handling, negative controls, manifest-only rejection, and figures. |
| `memory-centric-agentic/production_target_replay.md` | 27 | Documents replay order, manifest contract, and evidence-artifact requirements. |

### Figure Inventory

| Figure | Dimensions |
|---|---:|
| `data/causal_confounder_sensitivity.png` | 1520 x 928 |
| `data/causal_failure_modes.png` | 1760 x 928 |
| `data/causal_claim_boundary.png` | 1520 x 832 |
| `data/production_target_replay_gate_trace.png` | 1760 x 768 |
| `data/production_target_replay_claim_boundary.png` | 1280 x 768 |

All five figures were present and nonblank in the workspace record used for this report.

### Validation Results

Cycle 35 validation passed for `M-CAUSAL-1`. The auditor required no code patch. Reported checks included the causal verifier, Python bytecode compilation, independent CSV/figure checks, `promise_check`, and `org_check` with only known root warnings.

Cycle 36 validation passed for `M-PRODREPLAY-1` after a critical audit patch. Reported checks included:

```bash
python3 scripts/run_production_target_replay.py
python3 scripts/plot_production_target_replay.py
python3 tests/verify_production_target_replay.py
python3 -m py_compile ...
```

The supplied audit report also records an independent CSV/figure probe, green `promise_check` with 185 events and 35 plan milestones, and `org_check` exit 0 with only known root warnings for `CURATION.yaml` and two package zip files.

### Source Session References

| Cycle | Researcher | Worker | Auditor |
|---:|---|---|---|
| 35 | `88c633b4-3363-4a7a-92d5-eade5dbdca02` | `e784f362-2075-485d-8c6c-3734c55a613f` | `3274c023-4fe2-4930-ac45-6c0e014218bb` |
| 36 | `5d165de9-4dfd-4f37-a33c-e9174ae00e9c` | `ecafd12e-5b5b-4c29-945b-123b22bdc8b2` | `a6480a34-0633-4f07-bcec-6285f6a384dc` |
| 37 | `691b573c-292d-467b-b706-5e0a0374a5ae` | `3ba0f71b-84af-417f-b565-aed06825efb0` | `b59e643d-811a-4dfd-99a2-1f0d0f0f6ac9` |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/uncertainty_evaluation_results.csv` | `data/causal_valid_fixture.csv`, `data/causal_attribution_results.csv` | Confidence-qualified threshold outcomes become causal-attribution inputs. |
| `data/causal_attribution_results.csv` | `data/production_target_replay_results.csv`, `data/production_target_replay_claim_boundary.csv` | Robust but causally invalid rows remain blocked before claim-support candidacy. |
| `data/production_target_replay_absence_report.csv` | `data/production_target_replay_results.csv`, `data/production_target_replay_claim_boundary.csv` | Absence of real production-target manifests becomes explicit zero-credit replay output. |
| `memory-centric-agentic/production_target_replay.md` | `scripts/run_production_target_replay.py`, `tests/verify_production_target_replay.py` | The documented manifest contract is enforced by the replay and negative test. |

### Manifest Snapshot

`MANIFEST.md` was updated during this reporter pass. The snapshot now records cycle-35 and cycle-36 additions, refreshed cumulative counts, and new cross-references. Current manifest-level counts are:

| Category | Count |
|---|---:|
| Python scripts in `scripts/` | 78 |
| Wolfram scripts in `scripts/` | 4 |
| Test scripts | 22 |
| Total `scripts/` lines | 20,044 |
| Markdown model/synthesis files under `memory-centric-agentic/` | 36 |
| Experiment-plan and verification markdown files | 4 |
| CSV data/model files under `data/` | 203 |
| Figures under `data/` | 91 |
| Sub-topics completed, assessed, or designed | 34 |
