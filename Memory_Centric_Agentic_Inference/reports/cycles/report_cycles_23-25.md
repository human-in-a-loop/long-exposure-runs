---
title: "Memory-Centric Agentic Inference — cycles 23-25"
date: "2026-05-12"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 23-25

## Abstract

Cycles 23-25 moved the memory-centric agentic inference package from calibrated internal artifacts toward operator-facing production measurement and forward-looking falsification. The technical focus was no longer to add another synthetic policy model, but to make the existing architecture claims measurable, reject invalid measurements fail-closed, and identify the hardware or workload trends that would make the memory-centric thesis stronger or weaker.

Cycle 23 produced `M-PRODDEPLOY-1`, a production telemetry deployment blueprint. It maps the previously validated DC-001/DC-002 telemetry contract into concrete collector categories, required join keys, preflight checks, and a minimal pilot plan. The result is not measured production evidence. It is an operator-facing plan for collecting future `production_target` rows without accidentally promoting planned, synthetic, or host-local evidence into production-ready claims.

Cycle 24 produced `M-TRENDS-1`, a synthetic future hardware and workload trend falsification harness. It evaluates future scenarios across HBM capacity and bandwidth, CXL or pooled-memory tail latency, durable-state latency, energy per byte, recompute cost, validation/security overhead, reuse probability, branch fanout, durable-state lifetime, and verification-loop count. The audit accepted the harness after a repair that made validated upstream context explicit in the output rows. It produced 54 scenario rows, 30 phase-grid rows, 6 falsification thresholds, 7 measurement priorities, and three nonblank figures.

Cycle 25 has supplied researcher, worker, and auditor session IDs, but no separate milestone, script, test, data file, figure, markdown artifact, or ledger event was found in the workspace records. This report treats cycle 25 as a reporting boundary and records that gap explicitly.

The main conclusion remains unchanged: Option B and Option C memory-centric mechanisms are contract-ready and synthetically compelling in high-reuse, branch-heavy, durable, verification-heavy regimes, but no Option B/C claim and no `CL-012` energy/economics claim is production-ready until real joined `production_target` telemetry passes all gates.

## Introduction

The campaign investigates whether future AI infrastructure should be organized around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier cycles built the core ingredients: workload taxonomy, memory-object models, cost and queueing models, security/provenance gates, synthetic traces, runtime prototypes, planning passes, host-local proxy calibration, and a production-shaped telemetry ingestion contract.

Cycles 23-25 sit after that technical base. Their question is operational: what must a production operator actually collect, join, and validate to test the memory-centric architecture claims, and which future hardware or workload trends would falsify or strengthen those claims?

The hardware context remains the same as prior reports. Current accelerator systems expose high-bandwidth GPU memory and increasingly heterogeneous host, interconnect, and storage tiers [1]-[7], while LLM serving systems already exploit memory-management techniques such as paged KV-cache handling, prefix caching, and semantic caching [9], [12], [13]. The campaign’s distinction is that long-running agentic inference may add persistent tool outputs, branch state, verifier state, durable workspace state, and multi-agent trajectory state to the memory-management problem.

## Methodology

The report consolidates accepted source material rather than re-auditing it. The source inventory for cycles 23-25 is:

| Cycle | Milestone | Source sessions | Main artifacts |
|---:|---|---|---|
| 23 | `M-PRODDEPLOY-1` | researcher `968f2186-0734-49cc-9b7a-64217c35851f`; worker `ad240682-a7ae-4cc1-ac05-356105593275`; auditor `5652bd89-eb95-4f20-aac3-0c5bee9aa197` | `production_telemetry_deployment.md`, collector spec, join contract, preflight checks, pilot design, three figures |
| 24 | `M-TRENDS-1` | researcher `e6526405-0009-45b6-9f82-d639e22de8d4`; worker `63488762-32ff-4055-b3e2-4618ebd0984d`; auditor `c677c4e3-b359-4df2-990b-656d95c06370` | `future_trend_falsification.md`, scenario table, phase grid, thresholds, measurement priorities, three figures |
| 25 | Reporting boundary | researcher `facbac6c-76a9-4a9b-b0b0-8060c6fd2085`; worker `405af2bd-283f-4d02-ad88-a8418903e6c1`; auditor `67b351f5-262c-4928-aa51-8fee37a6db01` | No separate cycle-25 workspace artifact or ledger event found |

No callable session-search or session-catalog tool was available in this environment. The report therefore uses the supplied session IDs as traceability anchors and relies on workspace artifacts, `promise_ledger.jsonl`, `plan_of_record.md`, `REFERENCES.md`, `MANIFEST.md`, generated CSVs, generated figures, and the supplied audit report for technical content.

## Results

### Context Before Cycle 23

Before cycle 23, the package already had a validated production-shaped DC-001/DC-002 telemetry contract. DC-001 covers per-tier energy or dollar cost per byte moved or retained. DC-002 covers CXL or pooled-memory latency under contention. Prior work also established that synthetic fixtures and host-local proxy measurements could exercise the machinery, but could not calibrate production claims.

The production acceptance rule inherited by cycle 23 was:

`ProductionCalibrated = evidence_label=production_target AND required fields present AND join keys valid AND power/byte intervals aligned AND delta above noise AND security/provenance/retention/verifier gates pass AND threshold is comparable`

Cycle 23 turned that rule into a deployment blueprint.

### Cycle 23: Production Telemetry Deployment Blueprint

Cycle 23 added `M-PRODDEPLOY-1`, an operator-facing kit for collecting future `production_target` telemetry. The deployment note defines a usable run as a joined replay row satisfying:

`RequiredCollectorsPresent AND SharedRunID AND SharedIntervalID AND ClockAligned AND WorkloadObjectJoinValid AND TopologyTenantJoinValid AND SecurityJoinValid AND NoiseFloorKnown AND EvidenceLabel=production_target`

If any term is false, the row remains diagnostic and `production_calibrated=false`.

The generated collector spec contains 9 deployment-specific collector categories. The auditor records that these cover all 27 required `M-PRODTELEM-1` production schema fields. The categories include accelerator power counters, host power counters, tier-specific byte counters, CXL or pooled-memory p50/p95/p99 latency, queue depth and tenant concurrency, workload/object classification, reuse decision and architecture option logs, security/provenance/retention/verifier gates, and interval/noise-floor metadata.

The join contract contains 7 required join domains: `run_id`, `interval_id`, `workload_id`, `object_id`, `topology_id`, `tenant_id`, and `security_context_id`. These keys prevent mixed evidence classes, mismatched intervals, unjoinable object labels, topology ambiguity, tenant-context loss, and security/provenance gaps.

![Production telemetry join keys connecting power, bytes, latency, workload/object, topology, tenant, and security logs.](data/production_telemetry_join_graph.png)

The preflight matrix contains 10 checks. Every row has `blocks_calibration=true`. The point of preflight is to fail before misleading rows can enter the calibration path. Missing power counters, tier-specific bytes, CXL/pool tail latency, workload/object labels, tenant concurrency, security/provenance gates, noise floors, production evidence labels, or clock alignment all block production calibration.

![Fail-closed production telemetry preflight checks by collector category and claim impact.](data/production_telemetry_preflight_matrix.png)

The minimal pilot contains 5 steps: preflight-only dry run, Option A control replay, Option B object-reuse candidate, Option C trajectory/DAG candidate, and fail-closed audit replay. The pilot is intentionally narrow. It can prove whether instrumentation is joinable and whether negative controls stay negative. It cannot endorse Option B or Option C deployment by itself.

![Minimal pilot scope for testing Option A controls, Option B object reuse, Option C trajectory/DAG candidates, and fail-closed audit replay.](data/production_telemetry_pilot_scope.png)

The auditor validated `M-PRODDEPLOY-1` without code changes. The accepted validation record states that the verifier, Python compilation, `promise_check`, and `org_check` passed, with only known root package warnings. The cycle also preserved the evidence boundary: planned telemetry is not measured evidence, and no current claim became production-ready.

### Cycle 24: Future Trend Falsification Harness

Cycle 24 added `M-TRENDS-1`, a synthetic future-trend harness. Its purpose was to ask which future hardware or workload changes would make memory-centric architecture compelling, unnecessary, or falsified under stated assumptions.

The scoring rule is inherited from the planner and energy/contention models:

`MemoryCentricAdvantage = RetainedStateValue - MovementCost - ContentionPenalty - RecomputeAlternative - ValidationSecurityOverhead`

Retained value rises with reuse probability, branch fanout, durable-state lifetime, verification-loop count, and recompute cost. Movement and contention costs fall when memory tiers improve. Validation and security costs are charged after retained value, so high provenance or safety overhead can still downgrade Option B/C.

The harness produced 54 scenario rows. Option choices were:

| Option | Scenario rows |
|---|---:|
| A | 35 |
| B | 8 |
| C | 11 |

The 30-row phase grid produced 10 Option A rows, 9 Option B rows, and 11 Option C rows. All rows have `production_ready=false`.

![Option A/B/C preferred regions under synthetic future hardware and workload trend axes.](data/future_trend_phase_diagram.png)

The harness records six falsification thresholds:

| Threshold | Value | Meaning |
|---|---:|---|
| Minimum reuse probability for B | 0.2 | Below this, object reuse is likely transient or workload-specific |
| Minimum branch fanout for C | 2 | Trajectory/DAG machinery requires real branching structure |
| Validation/security overhead collapse | 32x | Safety/provenance cost can collapse B/C back to A |
| CXL p99 latency collapse | 480x | Warm-tier tail latency can erase retained value |
| Recompute-cost threshold | 0.5x | Cheap recompute weakens memory-centric placement |
| Durable lifetime threshold for C | 6 | Durable workspace state must live long enough to amortize costs |

![Synthetic thresholds where memory-centric mechanisms become compelling or collapse.](data/future_trend_falsification_thresholds.png)

The supplied audit report records one moderate finding and one minor log. The moderate issue was fixed: `scripts/evaluate_future_trends.py` had declared validated upstream artifacts as inputs but mostly existence-checked them. The repair made those inputs propagate into explicit scoring context columns: planner net value, security safe-hit rate, CXL p99 collapse threshold, energy-sensitivity collapse rate, and pilot option scope. A repair side effect was that the old CXL synthetic probe grid no longer crossed the collapse threshold; the auditor widened only the CXL probe grid, and the crossing now occurs at `480x`.

The harness also produced 7 ranked measurement priorities:

| Rank | Measurement | Primary axis |
|---:|---|---|
| 1 | Joined production reuse probability by object class | reuse probability |
| 2 | CXL/pooled-memory p99 under tenant concurrency | CXL p99 latency |
| 3 | Validation/security/provenance overhead per safe reuse | validation/security overhead |
| 4 | Branch fanout and merge/discard rates | branch fanout |
| 5 | Durable workspace lifetime and replay frequency | durable-state lifetime |
| 6 | Target accelerator energy per tier byte moved | energy per byte |
| 7 | Recompute cost for verifier and tool-output regeneration | recompute cost |

![Ranked future production measurements by expected ability to change architecture conclusions.](data/future_trend_measurement_priorities.png)

The audit decision was `VALIDATED`. The accepted validation commands were:

- `python3 scripts/evaluate_future_trends.py`
- `python3 scripts/plot_future_trends.py`
- `python3 tests/verify_future_trends.py`
- `python3 -m py_compile ...`
- independent Pillow figure probe
- `python3 -m long_exposure.tools.promise_check <workspace>`
- `python3 -m long_exposure.tools.org_check <workspace>`

The final audit counts were 54 scenario rows, 30 phase-grid rows, 6 threshold rows, 7 measurement-priority rows, and three nonblank figures. `promise_check` was green with 128 events and 23 plan milestones. `org_check` exited 0 with known root package warnings.

### Cycle 25: Reporting Boundary and Record Gap

Cycle 25 has supplied researcher, worker, and auditor session IDs. A workspace search across ledger records, plan records, project markdown, scripts, tests, data, figures, reports, and manifest content found no separate cycle-25 milestone or technical artifact.

This report therefore treats cycle 25 as a reporting boundary rather than as a new technical result. The gap does not alter the cycle 23 or cycle 24 validation records. It only means there is no cycle-25 artifact to summarize beyond the supplied traceability IDs.

## Discussion

Cycles 23-25 sharpen the package’s evidence boundary. The work does not claim that memory-centric infrastructure is production-endorsed. It defines what would be required to make such a claim.

The cycle 23 deployment kit makes the production evidence requirement operational. A power counter alone is insufficient. A latency histogram alone is insufficient. A reuse decision alone is insufficient. The row must join energy, byte movement, latency, workload/object identity, topology, tenant context, architecture option, reuse decision, security/provenance/retention/verifier gates, interval alignment, and noise-floor metadata. If any part is missing or mismatched, the system fails closed.

The cycle 24 trend harness makes the architecture thesis more falsifiable. It identifies regimes where Option A remains enough: zero-reuse controls, cheap recompute, low-reuse workloads on large/fast local memory, low CXL latency without reuse, pathological CXL tail latency, and high validation/security overhead. It also identifies synthetic regimes where Option B or C can become compelling: Option B when object reuse amortizes movement and validation, and Option C when branch fanout, durable state, and verification loops combine.

The most important continuity with prior cycles is that `CL-012` remains blocked. Energy/economics claims cannot be upgraded by synthetic future rows, deployment blueprints, or host-local proxy runs. They require real target measurements with aligned power and byte intervals above noise.

## Conclusions and Recommendations

Cycles 23-25 produced two validated additions to the research package:

1. `M-PRODDEPLOY-1` converts the production telemetry contract into a deployment blueprint with collector mappings, join keys, fail-closed preflight checks, and a minimal pilot.
2. `M-TRENDS-1` defines synthetic future-trend scenarios, phase grids, falsification thresholds, and ranked production measurements while preserving non-production-ready semantics.

The recommended next technical step is real joined `production_target` telemetry replay through the existing production ingestion, energy/contention, planner, readiness, deployment, and trend paths. The first measurements should follow the ranked list from cycle 24: reuse probability by object class, CXL/pool p99 under tenant concurrency, validation/security overhead per safe reuse, branch fanout and merge/discard rates, durable workspace lifetime, target energy per tier byte moved, and recompute cost for verifier/tool-output regeneration.

Until those measurements exist, the architecture stance remains conservative:

- Option A remains the default for controls, zero-reuse workloads, cheap-recompute regimes, and regimes where validation/security or CXL tail costs dominate.
- Option B remains a contract-ready object-reuse pathway when safe retained object value can be joined to bytes, energy, latency, and security/provenance gates.
- Option C remains a contract-ready trajectory/DAG pathway only when branch fanout, durable-state lifetime, verifier loops, queueing, contention, security, and compression constraints all remain favorable.
- No synthetic, planned, host-local, below-noise, unjoined, or security-denied row should grant production-ready status or positive reuse/energy credit.

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

Cycle 23 artifacts:

| File | Purpose |
|---|---|
| `scripts/build_production_telemetry_deployment_kit.py` | Builds collector spec, join contract, preflight checks, and pilot design |
| `scripts/plot_production_telemetry_deployment.py` | Renders deployment join, preflight, and pilot figures |
| `tests/verify_production_telemetry_deployment.py` | Verifies collector coverage, join keys, preflight blockers, pilot scope, and evidence boundaries |
| `memory-centric-agentic/production_telemetry_deployment.md` | Operator-facing deployment blueprint |
| `data/production_telemetry_collector_spec.csv` | 9 collector rows |
| `data/production_telemetry_join_contract.csv` | 7 join rows |
| `data/production_telemetry_preflight_checks.csv` | 10 fail-closed preflight rows |
| `data/production_telemetry_pilot_design.csv` | 5 pilot rows |

Cycle 24 artifacts:

| File | Purpose |
|---|---|
| `scripts/evaluate_future_trends.py` | Builds synthetic future trend scenarios, phase grid, thresholds, and measurement priorities |
| `scripts/plot_future_trends.py` | Renders trend phase, threshold, and measurement-priority figures |
| `tests/verify_future_trends.py` | Verifies required axes, thresholds, context propagation, and non-production-ready boundaries |
| `memory-centric-agentic/future_trend_falsification.md` | Narrative trend-falsification note |
| `data/future_trend_scenarios.csv` | 54 scenario rows |
| `data/future_trend_architecture_phase_diagram.csv` | 30 phase-grid rows |
| `data/future_trend_falsification_thresholds.csv` | 6 threshold rows |
| `data/future_trend_measurement_priorities.csv` | 7 measurement-priority rows |

### Figure Inventory

| Figure | Dimensions |
|---|---:|
| `data/production_telemetry_join_graph.png` | 1440 x 960 |
| `data/production_telemetry_preflight_matrix.png` | 1600 x 880 |
| `data/production_telemetry_pilot_scope.png` | 1600 x 864 |
| `data/future_trend_phase_diagram.png` | 1360 x 768 |
| `data/future_trend_falsification_thresholds.png` | 1600 x 832 |
| `data/future_trend_measurement_priorities.png` | 1600 x 896 |

### Validation Results

`M-PRODDEPLOY-1` was auditor-validated without code changes. The final ledger event records 9 collector rows, 7 join rows, 10 preflight rows, 5 pilot rows, and three nonblank figures. It also records passing verifier, Python compilation, `promise_check`, and `org_check`, with only known root package warnings.

`M-TRENDS-1` was auditor-validated after one moderate fix. The evaluator now threads validated upstream inputs into scoring context columns, and the CXL synthetic probe grid was widened so the p99 collapse threshold crosses at `480x`. The final audit records 54 scenario rows, 30 phase-grid rows, 6 threshold rows, 7 measurement-priority rows, three nonblank figures, passing verifier, Python compilation, independent Pillow figure probe, green `promise_check`, and `org_check` exit 0 with known root package warnings.

`MANIFEST.md` was updated as a current workspace snapshot. It now records 43 Python scripts in `scripts/`, 4 Wolfram scripts, 10 test scripts, 12,570 script lines, 24 model/synthesis markdown files, 4 experiment-plan markdown files, 114 CSV data/model files, 57 figures, and 24 completed, assessed, or designed sub-topics.

### Source Session References

| Cycle | Role | Session ID |
|---:|---|---|
| 23 | researcher | `968f2186-0734-49cc-9b7a-64217c35851f` |
| 23 | worker | `ad240682-a7ae-4cc1-ac05-356105593275` |
| 23 | auditor | `5652bd89-eb95-4f20-aac3-0c5bee9aa197` |
| 24 | researcher | `e6526405-0009-45b6-9f82-d639e22de8d4` |
| 24 | worker | `63488762-32ff-4055-b3e2-4618ebd0984d` |
| 24 | auditor | `c677c4e3-b359-4df2-990b-656d95c06370` |
| 25 | researcher | `facbac6c-76a9-4a9b-b0b0-8060c6fd2085` |
| 25 | worker | `405af2bd-283f-4d02-ad88-a8418903e6c1` |
| 25 | auditor | `67b351f5-262c-4928-aa51-8fee37a6db01` |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/production_dc12_telemetry_schema.csv` | `scripts/build_production_telemetry_deployment_kit.py` | Required production fields become deployment collector requirements and preflight blockers |
| `data/production_telemetry_collector_spec.csv` | `data/production_telemetry_join_contract.csv` | Collector categories are tied to replay join keys |
| `data/production_telemetry_preflight_checks.csv` | `data/production_telemetry_pilot_design.csv` | Pilot steps inherit fail-closed calibration blockers |
| `data/final_claim_readiness_matrix.csv` | `scripts/evaluate_future_trends.py` | Final claim-readiness boundaries become synthetic scoring context |
| `data/final_architecture_option_readiness.csv` | `scripts/evaluate_future_trends.py` | Option A/B/C readiness labels inform trend scenario context |
| `data/cxl_contention_thresholds.csv` | `scripts/evaluate_future_trends.py` | CXL p99 collapse context is propagated into trend outputs |
| `data/energy_architecture_sensitivity.csv` | `scripts/evaluate_future_trends.py` | Energy-sensitivity collapse context is propagated into trend outputs |
| `data/memory_plan_constraint_sensitivity.csv` | `scripts/evaluate_future_trends.py` | Planner net-value context is propagated into scenarios and thresholds |
| `data/production_telemetry_pilot_design.csv` | `scripts/evaluate_future_trends.py` | Pilot option scope is recorded in trend context columns |
| `data/future_trend_falsification_thresholds.csv` | future production measurements | Thresholds define what future measurements should try to confirm or falsify |
