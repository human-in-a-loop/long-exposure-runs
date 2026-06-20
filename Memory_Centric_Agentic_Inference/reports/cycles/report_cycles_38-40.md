---
title: "Memory-Centric Agentic Inference — cycles 38-40"
date: "2026-05-12"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 38-40

## Abstract

Cycles 38-40 extended the memory-centric agentic inference package from production replay contracts into production-side evidence collection and claim lifecycle control. The work did not create production evidence for Option B or Option C memory-centric architecture claims. Instead, it added two validated fail-closed boundaries around any future production claim.

Cycle 38 produced `M-LIVECOLLECT-1`, a production-side gate-evidence collector scaffold and preflight. It maps each required replay gate to concrete source material, blocks production artifact emission when operator, root, attestation, time, counter, or per-gate source evidence is missing, and permits only dry-run fixture artifacts in the current workspace.

Cycle 39 produced `M-CLAIMEXP-1`, a production claim expiry and longitudinal revalidation harness. It states that even a future successful production replay is not evergreen: support expires at a declared time-to-live (TTL), is invalidated by identity-breaking deployment changes, and requires fresh production material when workload, scheduler, memory tier, security, uncertainty, or causal-control conditions drift.

Cycle 40 has supplied researcher, worker, and auditor session IDs, but the available workspace record contains no separate cycle-40 milestone, artifact, ledger event, script, test, data file, figure, or audit decision. This report treats cycle 40 as a source-record gap rather than a technical result.

## Introduction

The long-exposure run investigates whether future AI infrastructure should be designed around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier cycles built the main research package: workload taxonomy, lifetime and cost models, simulations, scheduling comparisons, architecture options, runtime prototypes, security analysis, calibration maps, energy/economics sensitivity, and production-evidence gates. Public background sources include GPU systems and accelerator memory context [1]-[4], PCIe/NVMe/CXL interconnect and storage specifications [5]-[7], MLPerf inference benchmarking context [8], PagedAttention [9], CPU/DRAM platform context [10]-[11], prefix caching [12], semantic caching [13], and CXL 2.0 context [14].

By cycles 35-37, the package had already established that synthetic, fixture, proxy, and non-production evidence cannot justify production-ready Option B/C claims. Cycle 35 added causal attribution and control-arm validity. Cycle 36 added real `production_target` replay semantics. Cycle 37 added the operator gate-evidence artifact contract, `M-EVIDART-1`, which requires concrete evidence paths, digests, payload fields, identity bindings, measurement windows, and upstream dependency links before replay readiness.

Cycles 38-40 continued that production-evidence hardening path. The focus shifted from "can a manifest be replayed?" to "can production-side material be collected without self-attestation?" and "if production support ever exists, how long does it remain valid?"

## Approach

The reporting sources were the supplied audit report, supplied cycle session IDs, `promise_ledger.jsonl`, `plan_of_record.md`, milestone markdown files, generated CSV and figure outputs, `REFERENCES.md`, and `MANIFEST.md`. No callable `search_sessions` or `list_session_catalog` tool was available in this environment, so session IDs are used as traceability anchors rather than fetched session transcripts.

The direct cycle session IDs supplied for this report are:

| Cycle | Researcher | Worker | Auditor |
|---|---|---|---|
| 38 | `683ea2ab-b287-4426-8f12-1eb01d909281` | `90dac0d5-849f-40dc-87d6-e298414571fc` | `13f1320c-3802-4535-bee9-aeb790cf8aaf` |
| 39 | `1ffcbcfc-5a1c-4e15-be54-01307d326436` | `e073ee3b-901b-72f-85aa-e891b72f1242` | `518ebeda-2aab-4086-a43e-0313e29d6857` |
| 40 | `878de3f2-6369-4911-ab0d-3cad9cff873e` | `4c7128a0-e24b-4341-9cea-0844420c1873` | `7976335f-0fdc-41d0-a735-f50dc1a54468` |

The cycle-39 worker ID above is reported exactly as supplied in the input stream.

## Findings

### Context Before Cycle 38: Concrete Gate Evidence Became a Replay Prerequisite

Cycle 37, immediately before this report range, produced `M-EVIDART-1`: the operator gate-evidence artifact production and validation kit. Its purpose was to prevent `production_target` replay from trusting manifest booleans alone.

The kit defines required artifacts for the full replay chain: root enrollment, attestation envelope, trust policy, intake custody, adapter conformance, timebase integrity, redaction integrity, evidence gatechain, uncertainty qualification, causal attribution, DC-001/DC-002 threshold replay, planner readiness boundary, and final handoff traceability.

The auditor for cycle 37 found and fixed a critical defect: artifacts missing required payload and identity-binding fields could still be marked complete and ready for replay. After the patch, the validator enforces required payload fields and preserves the distinction between structural replay readiness and production claim credit. The complete linked-artifact probe can reach `ready_for_production_target_replay=true`, but `production_calibrated`, `production_ready`, `threshold_success`, `causal_validity_granted`, and `claim_credit_allowed` remain `false`.

![Gate evidence dependency graph tying each production replay gate to required upstream artifacts.](data/gate_evidence_dependency_graph.png)

### Cycle 38: Production-Side Evidence Collector Scaffold

Cycle 38 added `M-LIVECOLLECT-1`, the production-side gate-evidence collection scaffold and preflight. The plan event was `b7d6d573-f4d9-4e13-b1a5-5ad8c6ad8441`; worker progress and validation were recorded in `74d3dd1c-b6fc-4d9c-b14e-84a55c9eb2fc` and `ee4d5b7e-5875-4c54-9a37-fd598cf2fb33`; auditor validation was recorded in `562dd54d-4baf-4ae8-b3c8-569d806e24f4`.

The collector does not decide claim readiness. It checks whether a deployment has enough independent material to emit candidate evidence artifacts for later `M-EVIDART-1` validation and `M-PRODREPLAY-1` replay.

The generated capability model maps each gate to one of four source classes:

- `collector_observed`: reports or counter-derived material the collector can bind.
- `operator_supplied`: deployment, policy, causal-control, or handoff material supplied by the operator.
- `external_attestation`: hardware, KMS, HSM, or external-attester material.
- `derived_from_prior_gate`: artifacts derived from earlier validated evidence links.

![Collector capability matrix showing which source class feeds each gate artifact.](data/live_collector_capability_matrix.png)

Production artifact emission requires a production-root marker, deployment-root identity, collector identity, operator trust policy, external attestation, telemetry counter source, fresh time source, writable output custody path, and per-gate source material. In the current workspace, no real production root exists, so production emission remains blocked or dry-run only.

The auditor found and fixed a critical production-emission defect. Before the patch, `emit-artifacts` could write 13 `production_target` artifacts when only top-level root, identity, policy, attestation, time, and counter files existed, silently substituting fixture digests for missing per-gate source material. The fix requires every mapped gate source input before production artifact emission and adds a non-fixture digest guard.

The validated output has 12 preflight result rows and 12 claim-boundary rows. Dry-run rows can emit 13 structurally complete artifacts labeled `collector_dry_run_fixture`, but all current rows keep production calibration, production readiness, threshold success, causal validity, and claim credit set to `false`.

![Live collector preflight failure modes showing missing production-side material failing closed.](data/live_collector_failure_modes.png)

![Collector preflight and dry-run artifact emission remain separated from production claim credit.](data/live_collector_claim_boundary.png)

### Cycle 39: Production Claim Expiry and Revalidation

Cycle 39 added `M-CLAIMEXP-1`, a lifecycle boundary for any future successful `production_target` replay. The plan event was `0f5a66ab-383e-44f7-9738-391c70641b75`; worker progress and validation were recorded in `cc88f1fa-d356-4884-a7a4-0828f255c0da` and `65a7ef3e-e8cd-4922-9b2d-28cd66205be7`; auditor validation was recorded in `70f1be25-e77f-4f6f-9932-ff7a7132988c`.

The harness defines five lifecycle statuses:

| Status | Meaning |
|---|---|
| `currently_supportable` | A hypothetical prior production replay is still inside TTL and deployment assumptions have not drifted. |
| `revalidation_required` | The deployment or workload changed enough that fresh production material and replay are required. |
| `expired` | Evidence age is at or beyond the TTL boundary. |
| `invalidated_by_change` | Identity, topology, collector/root, trust, model, or redaction changes break support. |
| `not_production_supported` | Upstream material or evidence labels are not production-supported. |

The default policy uses a 168-hour TTL and a closed expiry boundary: `age_hours >= ttl_hours` is `expired`. Identity-breaking changes such as model version changes, topology changes, collector/root rotation without re-enrollment, trust-policy rotation, or redaction-policy changes are `invalidated_by_change`. Workload, scheduler, memory-tier, security-deny-rate, uncertainty, and causal-control drift require revalidation unless an operator policy makes them outright invalidating.

![Claim-support lifecycle state over age and invalidation events.](data/claim_expiry_timeline.png)

The auditor found and fixed a critical claim-boundary defect. The original `data/claim_expiry_claim_boundary.csv` marked the hypothetical `fresh_prior_production_replay` row as production calibrated, production ready, threshold successful, causally valid, and claim-credit allowed. That treated a lifecycle fixture as current production claim credit. The patch separates `currently_supportable_lifecycle_state` from production-credit fields, and all production calibration/readiness/threshold/causal/claim-credit fields are now `false` for every current workspace fixture row.

The validated output has 18 lifecycle result rows, 18 revalidation-boundary rows, and 18 claim-boundary rows. The `fresh_prior_production_replay` case is `currently_supportable` only as a lifecycle status. It does not create production calibration, production readiness, threshold success, causal validity, or claim credit.

![Claim expiry and revalidation failure modes, including stale, drifted, invalidated, copied, and non-production cases.](data/claim_expiry_failure_modes.png)

![Fresh replay requirements show stale or changed deployment support cannot be satisfied by old replay copies.](data/claim_expiry_revalidation_boundary.png)

### Cycle 40: Source-Record Gap

Cycle 40 has supplied researcher, worker, and auditor session IDs, but workspace search found no separate cycle-40 milestone, plan row, ledger event, markdown artifact, script, test, CSV, or figure. The report therefore has no independent technical result to attribute to cycle 40.

This is a reporting gap, not a finding that work failed. The available record simply does not contain a cycle-40 technical artifact.

## Discussion

Cycles 38-40 tightened the production evidence chain without upgrading any architecture claim. That is the main result.

The chain now has three additional safeguards around future production evidence:

1. `M-EVIDART-1` says every replay gate needs concrete evidence artifacts, not just manifest booleans.
2. `M-LIVECOLLECT-1` says a collector may emit production artifacts only when real production-side source material exists for every mapped gate.
3. `M-CLAIMEXP-1` says even a successful future production replay is time-bounded and deployment-bounded.

Together, these milestones prevent three overclaim paths:

- A manifest cannot self-attest its way through production replay.
- A collector cannot replace missing per-gate source material with fixture digests.
- A lifecycle fixture cannot become current production claim credit.

The architecture stance remains conservative. Option A remains the validated baseline and control path. Option B and Option C remain contract-ready pathways, not production recommendations. Real `production_target` telemetry is still required before any DC-001/DC-002 or Option B/C production claim can be made.

## Open Questions

The next non-redundant advancement requires real trusted `production_target` material. The required material includes a production root, enrolled collector identity, operator trust policy, external attestation, fresh time and counter sources, complete per-gate evidence artifacts, and a full replay through live collection, evidence artifact validation, production-target replay, uncertainty, causal, planner, and handoff gates.

The remaining open questions are operational rather than synthetic:

- Can an operator produce complete production-side source material for every gate without weakening privacy, trust, or custody constraints?
- Can production telemetry preserve the joins needed for workload, object, topology, tenant, security, timebase, uncertainty, and causal replay?
- How often would real production claims expire under normal model, topology, scheduler, collector, or workload changes?
- Are the TTL and drift policies too strict for production usefulness, or too loose for scientific validity?
- What production experiment can provide the first non-fixture evidence for DC-001/DC-002 thresholds and Option B/C architecture selection?

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

Cycle 38 / `M-LIVECOLLECT-1` artifacts:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_live_collector_contract.py` | 218 | Builds collector capability, operator-input, artifact-mapping, and preflight schemas. |
| `tools/production_evidence_collector.py` | 316 | Provides preflight, dry-run, and guarded production artifact emission CLI modes. |
| `scripts/evaluate_live_collector_preflight.py` | 257 | Evaluates preflight blockers, dry-run labels, source-material requirements, and claim boundaries. |
| `scripts/plot_live_collector_preflight.py` | 109 | Renders collector capability, failure-mode, and claim-boundary figures. |
| `tests/verify_live_collector_preflight.py` | 122 | Verifies fail-closed collector behavior and zero-credit boundaries. |
| `memory-centric-agentic/live_collector_preflight.md` | 81 | Documents deployment assumptions, source classes, CLI usage, failure modes, and claim boundary. |

Cycle 39 / `M-CLAIMEXP-1` artifacts:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_claim_expiry_fixtures.py` | 180 | Builds lifecycle schema, TTL policies, expiry fixtures, and drift events. |
| `scripts/evaluate_claim_expiry.py` | 142 | Evaluates lifecycle status, expiry, invalidation, revalidation, and claim boundary. |
| `scripts/plot_claim_expiry.py` | 113 | Renders lifecycle timeline, failure-mode, and revalidation-boundary figures. |
| `tests/verify_claim_expiry.py` | 99 | Verifies lifecycle statuses, TTL edge cases, drift handling, copied replay rejection, and zero-credit fields. |
| `memory-centric-agentic/claim_expiry_revalidation.md` | 25 | Documents TTL, drift, revalidation, and lifecycle-status-only semantics. |

Immediate dependency / `M-EVIDART-1` artifacts used as context:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/build_gate_evidence_artifact_contract.py` | 268 | Builds per-gate evidence artifact contract and operator checklist. |
| `scripts/validate_gate_evidence_artifacts.py` | 438 | Validates artifact paths, digests, payload fields, identity bindings, time windows, and dependencies. |
| `scripts/plot_gate_evidence_artifacts.py` | 106 | Renders artifact dependency and replay-readiness figures. |
| `tests/verify_gate_evidence_artifacts.py` | 174 | Verifies artifact validation fail-closed behavior. |
| `memory-centric-agentic/gate_evidence_artifacts.md` | 28 | Documents evidence artifact requirements and replay-readiness boundary. |

### Data Outputs

`M-LIVECOLLECT-1` generated 13 capability rows, 5 operator-input rows, 13 artifact-mapping rows, 22 preflight schema rows, 12 preflight results, 3 failure-mode rows, and 12 claim-boundary rows.

`M-CLAIMEXP-1` generated 18 schema rows, 2 policy profiles, 1 valid fixture, 17 invalid fixtures, 14 drift-event rows, 18 evaluation rows, 13 failure-mode rows, 18 revalidation-boundary rows, and 18 claim-boundary rows.

`M-EVIDART-1`, used as the upstream artifact contract, generated 13 artifact schema rows, 221 required-field rows, 13 dependency rows, 78 operator checklist rows, 44 validation rows, 10 failure-mode rows, and 12 replay-readiness boundary rows.

### Figure Inventory

| Figure | Dimensions | Report role |
|---|---:|---|
| `data/gate_evidence_dependency_graph.png` | 1760 x 1040 | Shows upstream evidence dependencies for replay gates. |
| `data/live_collector_capability_matrix.png` | 1440 x 768 | Shows source classes by collector capability. |
| `data/live_collector_failure_modes.png` | 1360 x 768 | Shows fail-closed live collector blockers. |
| `data/live_collector_claim_boundary.png` | 1360 x 768 | Shows collector outputs remain separated from claim credit. |
| `data/claim_expiry_timeline.png` | 1600 x 992 | Shows lifecycle status across age and invalidation events. |
| `data/claim_expiry_failure_modes.png` | 1440 x 864 | Shows expiry, invalidation, revalidation, copied-replay, and non-production failures. |
| `data/claim_expiry_revalidation_boundary.png` | 1360 x 768 | Shows fresh production material requirements for revalidation. |

### Validation Results

The supplied audit report states that `M-CLAIMEXP-1` was validated after one critical patch. The patch separated `currently_supportable_lifecycle_state` from production-credit fields, so every current workspace fixture row keeps `production_calibrated=false`, `production_ready=false`, `threshold_success=false`, `causal_validity_granted=false`, and `claim_credit_allowed=false`.

The validation run passed:

- `python3 tests/verify_claim_expiry.py`
- `python3 tests/verify_live_collector_preflight.py`
- `python3 tests/verify_gate_evidence_artifacts.py`
- `python3 tests/verify_production_target_replay.py`
- claim-expiry `py_compile`
- direct CSV probe for `fresh_prior_production_replay`
- figure nonblank checks for the three claim-expiry figures
- `promise_check`: green, 200 events, 38 plan milestones
- `org_check`: exit 0 with known root package warnings only

The cycle-38 ledger records auditor validation for `M-LIVECOLLECT-1` after a critical patch that required every mapped gate source input before production artifact emission and added a non-fixture digest guard.

The cycle-37 ledger records auditor validation for `M-EVIDART-1` after a critical patch that required contract-required payload fields before replay readiness.

### Source Session References

Cycle 38 sources: researcher `683ea2ab-b287-4426-8f12-1eb01d909281`, worker `90dac0d5-849f-40dc-87d6-e298414571fc`, auditor `13f1320c-3802-4535-bee9-aeb790cf8aaf`.

Cycle 39 sources: researcher `1ffcbcfc-5a1c-4e15-be54-01307d326436`, worker `e073ee3b-901b-4b97-85aa-e891b72f1242`, auditor `518ebeda-2aab-4086-a43e-0313e29d6857`.

Cycle 40 sources: researcher `878de3f2-6369-4911-ab0d-3cad9cff873e`, worker `4c7128a0-e24b-4341-9cea-0844420c1873`, auditor `7976335f-0fdc-41d0-a735-f50dc1a54468`. No separate cycle-40 artifact was present in the available workspace record.

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/gate_evidence_required_fields.csv` | `data/gate_evidence_artifact_validation_results.csv`, `data/gate_evidence_replay_readiness_boundary.csv` | Required payload, digest, identity, time-window, and dependency fields become replay-readiness checks. |
| `data/gate_evidence_operator_checklist.csv` | `data/live_collector_capability_matrix.csv`, `data/live_collector_artifact_mapping.csv` | Operator evidence requirements become collector source-class and artifact-field mappings. |
| `data/live_collector_preflight_results.csv` | `data/claim_expiry_results.csv`, `data/claim_expiry_revalidation_boundary.csv` | Current collector preflight/dry-run limits define why lifecycle revalidation cannot be satisfied without fresh production material. |
| `data/production_target_replay_claim_boundary.csv` | `data/claim_expiry_claim_boundary.csv` | A future successful replay can become lifecycle-supportable only inside TTL and unchanged deployment assumptions; current rows still grant no claim credit. |
| `REFERENCES.md` | reports and calibration artifacts | Global numbered references provide public hardware, interconnect, storage, benchmark, prefix-cache, semantic-cache, CPU/DRAM, and CXL context. |

### Manifest Snapshot

`MANIFEST.md` was updated for cycles 38-40. The current snapshot records 87 Python scripts in `scripts/`, 4 Wolfram scripts, 25 test scripts, 1 tool script, 21,875 total script lines, 39 markdown model/synthesis files under `memory-centric-agentic/`, 226 CSV data/model files, 100 figures, and 37 completed, assessed, or designed sub-topics.

The manifest now includes `M-EVIDART-1`, `M-LIVECOLLECT-1`, and `M-CLAIMEXP-1` in the cumulative production-evidence chain and states the current production boundary: real `production_target` telemetry with linked gate evidence artifacts, complete production-side source material, real deployment-root integration, and fresh lifecycle revalidation is still required before any DC-001/DC-002 or Option B/C claim can become production-ready.
