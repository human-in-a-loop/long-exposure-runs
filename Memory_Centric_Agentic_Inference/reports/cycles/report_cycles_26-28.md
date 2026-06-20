---
title: "Memory-Centric Agentic Inference — cycles 26-28"
date: "2026-05-12"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 26-28

## Abstract

Cycles 26-28 extended the production-readiness path for the memory-centric agentic inference package. The work did not add new synthetic architecture claims. It built and validated two operator-facing gates that sit between planned telemetry collection and production calibration: an adapter portability conformance kit in cycle 26 and a production intake bundle with chain-of-custody checks in cycle 27.

Cycle 26 produced `M-PORT-1`, the adapter conformance kit. It defines how backend-shaped telemetry adapter outputs must canonicalize logical join names, declare units, align clocks and intervals, preserve tenant and security context, and remain labeled as conformance evidence rather than production evidence. The auditor validated the kit with 9 contract rows, 7 alias rows, 9 valid backend-shaped profile rows, 11 invalid profile cases, 12 conformance results, 7 failure categories, 12 ingestion-boundary rows, and three nonblank figures.

Cycle 27 produced `M-INTAKE-1`, the production telemetry intake bundle and chain-of-custody gate. It defines the front-door bundle format for future operator telemetry drops: manifest schema, payload inventory, checksums, join window, provenance, measurement quality, security/privacy declarations, boundary labels, admission results, downstream boundary rows, and traceability links. The supplied audit report records one moderate issue found and fixed: the evaluator previously accepted any non-empty checksum field; it now hashes payload files and blocks mismatches as `checksum_mismatch`. The final validated output contains 32 manifest-schema rows, 5 valid payload rows, 11 invalid bundle cases, 9 custody requirements, 12 admission results, 8 failure categories, 12 downstream-boundary rows, 4 traceability links, and three nonblank figures.

Cycle 28 has supplied researcher, worker, and auditor session IDs, but no separate cycle-28 milestone, script, test, data file, markdown artifact, figure, or ledger event was found in the workspace record. This report treats cycle 28 as a reporting boundary and records that source gap explicitly.

The central conclusion remains conservative: adapter conformance and intake admission are necessary pre-production controls, but neither can grant `production_target` status, production calibration, production readiness, or claim credit. Real joined production telemetry is still required before DC-001/DC-002 energy/contention claims or Option B/C memory-centric architecture claims can be promoted.

## Introduction

The campaign investigates whether future AI infrastructure for long-running agentic inference should be organized around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier cycles built the base package: workload taxonomy, memory-object lifetime models, cost models, queueing models, simulations, runtime prototypes, security/provenance gates, production-shaped telemetry contracts, deployment blueprints, and trend falsification harnesses.

Cycles 26-28 focus on the operational path from “an operator has telemetry-like files” to “the existing production ingestion gates may evaluate them.” This is a narrower systems problem than the initial architecture design, but it matters because the research package depends on a hard evidence boundary. Synthetic fixtures, offline adapter rows, conformance profiles, intake manifests, planned deployments, and host-local proxies may validate protocol behavior. They cannot prove production performance or make Option B/C production-ready.

The hardware and systems context remains the same as prior reports: modern accelerator systems already expose high-bandwidth GPU memory, host DRAM, interconnect, storage, and pooled-memory tiers [1]-[7], while LLM serving systems use techniques such as paged KV-cache management, prefix caching, and semantic caching [9], [12], [13]. The campaign’s unresolved production question is whether agentic workloads add enough reusable, durable, branch-heavy state to justify memory-centric infrastructure beyond conventional throughput-oriented serving.

## Methodology

This report consolidates accepted work rather than re-auditing it. The source inventory for cycles 26-28 is:

| Cycle | Milestone | Source sessions | Main artifacts |
|---:|---|---|---|
| 26 | `M-PORT-1` | researcher `174f0fce-0d4c-4c32-bfa7-d0afb614e531`; worker `9d4abd78-822c-4b2b-b8c8-2c19825aec66`; auditor `14cdfd67-92c0-41a0-9f54-860e513ac7e4` | `adapter_conformance.md`, conformance contract, alias map, backend profile fixtures, conformance results, failure modes, ingestion boundary, three figures |
| 27 | `M-INTAKE-1` | researcher `f78f7849-a9af-4949-9ce7-2cd28fe8d13d`; worker `16c30136-fa5c-40e0-9ed4-b2ddd5d49ca3`; auditor `fee5e42f-b598-45b8-aaa5-ef2332eb8f00` | `production_intake_bundle.md`, manifest schema, valid and invalid bundle manifests, custody requirements, admission results, downstream boundary, traceability links, three figures |
| 28 | Reporting boundary | researcher `fabae07b-e4bc-418c-abcc-14cd8241d586`; worker `bb19cb73-5eb3-4bef-8a22-debce4625b92`; auditor `f4a3289f-6a64-4120-ab13-c8fa2e200797` | No separate cycle-28 workspace artifact or ledger event found |

No callable `search_sessions` or `list_session_catalog` tool was available in this environment, and no MCP session resources were exposed. The report therefore uses the supplied session IDs as traceability anchors and relies on workspace artifacts, `promise_ledger.jsonl`, `plan_of_record.md`, `REFERENCES.md`, `MANIFEST.md`, generated CSVs, generated figures, and the supplied audit report.

## Results

### Context Before Cycle 26

Cycle 25 had produced `M-ADAPTER-1`, a vendor-neutral telemetry adapter interface. It converted the deployment blueprint into offline fixture streams for required collector categories: accelerator power, host power, tier-specific byte movement, CXL or pooled-memory latency, queue depth and tenant concurrency, workload/object labels, reuse and architecture decisions, security/provenance/retention/verifier gates, and topology inventory.

Those adapter fixtures were still labeled `synthetic_adapter_fixture`. Production ingestion rejected them as `not_production_evidence_label`. Cycle 26 started from that boundary and added a portability check for backend-shaped adapter outputs.

### Cycle 26: Adapter Portability and Conformance Kit

Cycle 26 added `M-PORT-1`, the adapter conformance kit. A conformance kit is a pre-ingestion portability check: it verifies that an operator adapter’s output can be interpreted consistently before any row reaches production threshold replay.

The kit’s main design decision is that the production telemetry schema remains authoritative. Logical join names from the deployment contract are allowed only through `data/adapter_join_alias_map.csv`. The key example is `run_id`, which canonicalizes only to `measurement_run_id`. A backend profile may use `run_id` as an input alias, but the conformance runner must construct the canonical production schema field before downstream use. Unknown aliases or alias use that fails to canonicalize are fail-closed errors.

The validated conformance outputs are:

| Artifact | Rows | Role |
|---|---:|---|
| `data/adapter_conformance_contract.csv` | 9 | Required backend profile classes and conformance expectations |
| `data/adapter_join_alias_map.csv` | 7 | Logical join aliases mapped to canonical production schema fields |
| `data/adapter_backend_profile_fixtures.csv` | 9 | Valid backend-shaped profiles |
| `data/adapter_backend_profile_invalid_fixtures.csv` | 11 | Invalid profile cases |
| `data/adapter_conformance_results.csv` | 12 | Pass/fail results |
| `data/adapter_conformance_failure_modes.csv` | 7 | Failure category counts |
| `data/adapter_conformance_ingestion_boundary.csv` | 12 | Evidence-boundary rows |

The conformance runner checks stream-class coverage, canonical join-field mapping, unit declarations for power, energy, bytes, latency, and timestamps, clock-domain presence, interval alignment, schema version, tenant labels, security context, provenance freshness, and fixture evidence boundaries. Invalid profiles exercise alias, unit, clock, join, provenance, security, missing-profile, and attempted production-target failures.

![Conformance coverage by schema field, stream class, join key, and alias.](data/adapter_conformance_coverage.png)

The failure table contains 7 fail-closed categories. The largest categories are alias, unit, clock, and join, with 2 invalid profiles each; provenance, security, and boundary each account for 1 invalid profile. All categories have `fail_closed=true`.

![Fail-closed invalid profile counts by alias, unit, clock, join, provenance, and security category.](data/adapter_conformance_failures.png)

The boundary output keeps every row labeled `adapter_conformance_fixture`. Even the valid conformance profile is only a shape check. It has `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`, and production ingestion still blocks it as `not_production_evidence_label`.

![Evidence boundary from backend-shaped fixture to conformance pass/fail to production ingestion block.](data/adapter_conformance_boundary.png)

The cycle 26 auditor validated `M-PORT-1`. The accepted ledger record states that the auditor inspected the fixture builder, runner, plotter, verifier, narrative, generated CSVs, production telemetry schema, deployment join contract, plan, and ledger. The auditor regenerated the artifacts and reports that the verifier, Python compilation, independent CSV/figure probes, `promise_check`, and `org_check` passed with only known root package warnings.

### Cycle 27: Production Intake Bundle and Chain-of-Custody Gate

Cycle 27 added `M-INTAKE-1`, the production telemetry intake bundle and chain-of-custody gate. The intake bundle is the front-door format for future operator telemetry drops before adapter conformance, production ingestion, security validation, threshold replay, final readiness, or handoff artifacts may use them.

The bundle consists of a manifest plus payload inventory. It records bundle identity, telemetry file paths, stream classes, row counts, SHA-256 checksums, canonical schema targets, join-window declarations, provenance, measurement quality, security/privacy declarations, and explicit boundary labels.

The validated intake outputs are:

| Artifact | Rows | Role |
|---|---:|---|
| `data/production_intake_bundle_manifest_schema.csv` | 32 | Required manifest fields across bundle identity, payload inventory, join window, provenance, measurement quality, security/privacy, and boundary labels |
| `data/production_intake_valid_bundle_manifest.csv` | 5 | Complete fixture payload manifest rows |
| `data/production_intake_invalid_bundle_manifests.csv` | 11 | Invalid bundle cases |
| `data/production_intake_chain_of_custody_requirements.csv` | 9 | Pre-ingestion custody requirements |
| `data/production_intake_admission_results.csv` | 12 | Admission and blocked-reason results |
| `data/production_intake_failure_modes.csv` | 8 | Failure category counts |
| `data/production_intake_downstream_boundary.csv` | 12 | Downstream evidence-boundary rows |
| `data/production_intake_traceability_links.csv` | 4 | Links to adapter conformance, production ingestion, final readiness, and handoff |

The chain-of-custody requirements include complete manifest sections, checksums for every payload file, schema-version match, declared join window, alias resolution, adapter conformance report pointer, measurement-quality metadata, security/privacy declarations, and preserved boundary labels.

![Coverage of required manifest sections and telemetry stream inventory.](data/production_intake_manifest_coverage.png)

A complete fixture bundle may become `structurally_admissible`, but structural admission is deliberately weaker than production calibration. The valid intake bundle keeps `evidence_label=production_intake_fixture`, `production_target_granted=false`, `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`.

The invalid bundle cases block missing checksum, checksum mismatch, schema-version mismatch, missing adapter conformance pointer, unresolved join alias, missing noise floor, incomplete security/provenance stream, stale collection window, ambiguous redaction policy, invalid unit declaration, and fixture attempts to claim production-target evidence.

![Fail-closed invalid bundle counts by custody, schema, join, noise, security, provenance, redaction, and unit category.](data/production_intake_failure_modes.png)

The supplied cycle 27 audit report records one moderate issue found and fixed. The intake evaluator had reported `checksum_valid=true` when a checksum field was merely non-empty. That weakened the chain-of-custody gate because an incorrect SHA-256 could pass structural admission. The fix changed `scripts/evaluate_production_intake.py` to hash referenced payload files and compare the computed digest with the declared checksum. The worker also added `invalid-checksum-mismatch` to `scripts/build_production_intake_fixtures.py` and extended `tests/verify_production_intake.py` to require `checksum_valid=false` and `blocked_reason=checksum_mismatch`.

The downstream boundary remains closed after the checksum repair. All 12 boundary rows have `evidence_label=production_intake_fixture`, `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`. Downstream ingestion is blocked as `not_production_evidence_label`.

![Boundary from bundle admission to downstream ingestion, showing that intake admissibility is not production calibration.](data/production_intake_boundary.png)

The accepted audit decision was `VALIDATED`. The audit report lists the following commands as passed:

- `python3 scripts/build_production_intake_fixtures.py`
- `python3 scripts/evaluate_production_intake.py`
- `python3 scripts/plot_production_intake.py`
- `python3 tests/verify_production_intake.py`
- `python3 -m py_compile ...`
- independent CSV probe
- independent PNG probe
- `python3 -m long_exposure.tools.promise_check <workspace>`
- `python3 -m long_exposure.tools.org_check <workspace>`

The auditor ledger event is `2ffdd2d7-c566-44f8-a690-cbd69d03a90f`. The audit also notes that a temporary auditor-introduced ledger timestamp issue was corrected and `promise_check` was green with 141 events and 26 plan milestones. `org_check` still reports known root package warnings for `CURATION.yaml`, `memory_centric_agentic_inference_package_2026-05-12T0019.zip`, and `memory_centric_agentic_inference_package_latest.zip`.

### Cycle 28: Reporting Boundary and Record Gap

Cycle 28 has supplied researcher, worker, and auditor session IDs, but a workspace search found no separate cycle-28 milestone, markdown note, script, test, CSV, figure, or ledger event. This report treats cycle 28 as a record gap and reporting boundary rather than a new technical result.

This gap does not invalidate cycle 26 or cycle 27. It means only that there is no cycle-28 technical artifact to summarize from the available workspace record.

## Discussion

Cycles 26-28 complete another segment of the pre-production measurement path. The package now has a chain from deployment blueprint to adapter interface, adapter conformance, intake bundle admission, production ingestion contracts, threshold replay, readiness synthesis, and handoff traceability.

The cycle 26 conformance kit answers a portability question: can an operator’s backend-shaped adapter output be mapped into the canonical production telemetry schema without ambiguity? Its answer is fail-closed. Logical names must canonicalize, units must match, clocks and intervals must align, tenant and security context must be present, provenance must be fresh, and the evidence label must remain non-production.

The cycle 27 intake gate answers a custody question: can a telemetry drop be admitted as a structurally complete bundle before ingestion? Its answer is also fail-closed. Files must be inventoried, checksums must match actual payload bytes, schema targets must be declared, join windows must be resolvable, measurement quality must include noise metadata, security/privacy declarations must be complete, and boundary labels must remain intact.

Together, these cycles reduce the chance that a future production replay will be contaminated by malformed, ambiguous, stale, or mislabeled telemetry. They do not reduce the scientific evidence requirement. The required next step remains real joined `production_target` telemetry replayed through intake, adapter conformance, adapter normalization, production ingestion, security/provenance validation, noise-floor checks, DC-001/DC-002 threshold replay, planner updates, final readiness, and handoff traceability.

## Conclusions and Recommendations

Cycles 26-28 produced two validated additions and one explicit record gap:

1. `M-PORT-1` validates adapter portability before production ingestion. It resolves aliases only through canonical schema fields, blocks invalid units/clocks/joins/provenance/security/boundary cases, and keeps conformance evidence non-production.
2. `M-INTAKE-1` validates intake bundle structure and chain of custody. It admits complete fixture bundles only as structurally admissible, blocks invalid custody/schema/join/noise/security/provenance/redaction/unit cases, and now verifies checksums by hashing referenced payload files.
3. Cycle 28 has no separate technical artifact in the available workspace record.

The recommended next technical step is not more synthetic intake work. The audit guidance is to move on to actual trusted `production_target` telemetry replayed through the full path: intake bundle admission, adapter conformance, adapter normalization, production ingestion, security/provenance validation, noise-floor checks, DC-001/DC-002 threshold replay, planner updates, final readiness, and handoff traceability.

The architecture stance remains unchanged. Option A remains the default for controls, zero-reuse, cheap-recompute, high-overhead, or unjoinable regimes. Option B and Option C remain contract-ready pathways only when production rows prove safe object reuse or trajectory/DAG value under joined bytes, power, latency, tenant, topology, security, provenance, retention, verifier, interval, and noise-floor gates. No fixture, conformance pass, intake admission, synthetic trend, planned deployment, host-local proxy, below-noise row, unjoined row, or security-denied row should grant production-ready status or positive reuse/energy credit.

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

Cycle 26 artifacts:

| File | Purpose |
|---|---|
| `scripts/build_adapter_conformance_fixtures.py` | Builds conformance contract, join alias map, valid backend-shaped profiles, and invalid profile fixtures |
| `scripts/run_adapter_conformance.py` | Runs alias, unit, clock, join, provenance, security, and boundary checks |
| `scripts/plot_adapter_conformance.py` | Renders conformance coverage, failure, and boundary figures |
| `tests/verify_adapter_conformance.py` | Verifies canonical aliases, invalid profile blocking, ingestion boundary, and figures |
| `memory-centric-agentic/adapter_conformance.md` | Operator-facing conformance note |

Cycle 27 artifacts:

| File | Purpose |
|---|---|
| `scripts/build_production_intake_fixtures.py` | Builds manifest schema, valid bundle rows, invalid bundle rows, and custody requirements |
| `scripts/evaluate_production_intake.py` | Evaluates admission gates, hashes payload checksums, emits failure modes, downstream boundary, and traceability links |
| `scripts/plot_production_intake.py` | Renders intake coverage, failure, and boundary figures |
| `tests/verify_production_intake.py` | Verifies structural admission, checksum mismatch blocking, evidence boundary, traceability, and figures |
| `memory-centric-agentic/production_intake_bundle.md` | Operator-facing intake bundle note |

### Figure Inventory

| Figure | Dimensions | Role |
|---|---:|---|
| `data/adapter_conformance_coverage.png` | 1280 x 768 | Shows conformance coverage across required schema fields, stream classes, join keys, and aliases |
| `data/adapter_conformance_failures.png` | 1440 x 768 | Shows fail-closed invalid profile categories |
| `data/adapter_conformance_boundary.png` | 1280 x 768 | Shows conformance pass does not grant production target, calibration, readiness, or claim credit |
| `data/production_intake_manifest_coverage.png` | 1360 x 768 | Shows intake manifest sections, required fields, payload streams, and custody requirements |
| `data/production_intake_failure_modes.png` | 1440 x 768 | Shows fail-closed intake bundle failure categories |
| `data/production_intake_boundary.png` | 1360 x 768 | Shows structural admission does not grant production calibration or claim credit |

### Validation Results

Cycle 26 `M-PORT-1` was auditor-validated. The validation record reports regenerated CSVs and figures, verifier pass, Python compilation pass, independent CSV and figure probes, `promise_check` pass, and `org_check` pass with known root package warnings.

Cycle 27 `M-INTAKE-1` was auditor-validated after the checksum mismatch repair. The validation record reports regenerated CSVs and figures, verifier pass, Python compilation pass, independent CSV and PNG probes, `promise_check` pass with 141 events and 26 plan milestones, and `org_check` pass with known root package warnings.

No cycle 28 validation artifact was found.

### Source Session References

| Cycle | Role | Session ID |
|---:|---|---|
| 26 | researcher | `174f0fce-0d4c-4c32-bfa7-d0afb614e531` |
| 26 | worker | `9d4abd78-822c-4b2b-b8c8-2c19825aec66` |
| 26 | auditor | `14cdfd67-92c0-41a0-9f54-860e513ac7e4` |
| 27 | researcher | `f78f7849-a9af-4949-9ce7-2cd28fe8d13d` |
| 27 | worker | `16c30136-fa5c-40e0-9ed4-b2ddd5d49ca3` |
| 27 | auditor | `fee5e42f-b598-45b8-aaa5-ef2332eb8f00` |
| 28 | researcher | `fabae07b-e4bc-418c-abcc-14cd8241d586` |
| 28 | worker | `bb19cb73-5eb3-4bef-8a22-debce4625b92` |
| 28 | auditor | `f4a3289f-6a64-4120-ab13-c8fa2e200797` |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/production_dc12_telemetry_schema.csv` | `scripts/build_adapter_conformance_fixtures.py`, `scripts/evaluate_production_intake.py` | Production schema defines canonical fields and downstream ingestion probes |
| `data/production_telemetry_join_contract.csv` | `data/adapter_join_alias_map.csv`, `data/production_intake_chain_of_custody_requirements.csv` | Deployment join keys become adapter aliases and intake join-window requirements |
| `data/adapter_conformance_results.csv` | `data/production_intake_valid_bundle_manifest.csv` | Intake bundles cite adapter conformance as a required provenance pointer |
| `data/production_intake_admission_results.csv` | `data/production_dc12_ingestion_results.csv` | Structural admission precedes but does not satisfy production ingestion |
| `data/production_intake_downstream_boundary.csv` | `data/final_claim_readiness_matrix.csv` | Claim readiness remains blocked without trusted `production_target` telemetry |
| `data/production_intake_traceability_links.csv` | `data/handoff_claim_traceability.csv` | Handoff can cite bundle admission without treating it as calibrated evidence |

### Manifest Snapshot

`MANIFEST.md` was updated as the workspace snapshot after cycles 26-28. The current manifest records 52 Python scripts in `scripts/`, 4 Wolfram scripts, 13 test scripts, 14,545 total `scripts/` lines, 27 project markdown model/synthesis files, 131 CSV data/model files, 65 figures, and 27 completed, assessed, or designed sub-topics.
