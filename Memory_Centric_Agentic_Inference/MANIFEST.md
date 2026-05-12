# Workspace Manifest

Snapshot for the memory-centric agentic inference workspace after cycles 44-45: legacy trace-to-memory-object ABI migration, constrained developer/runtime annotation completion, and continued fail-closed non-production claim boundaries. The `## Key Files` section below is preserved verbatim from the final reporter close-out material.

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `scripts/lifetime_model.wls` — Lifetime equations and regime outputs cited in the Validated Mechanism Stack section.
- `scripts/cost_model.wls` — Heterogeneous memory cost scenarios and retained-value inequality support cited in the Validated Mechanism Stack section.
- `scripts/simulate_memory_policies.py` — Synthetic policy comparisons for Option A/B/C workload decisions cited in the Validated Mechanism Stack section.
- `scripts/evaluate_scheduling_abstractions.py` — Scheduling-boundary comparison results cited in the Validated Mechanism Stack section.
- `scripts/generate_agentic_trace_v2.py` — Trace v2 event and workload-summary results cited in the Validated Mechanism Stack section.
- `scripts/queueing_model.wls` — Symbolic queueing reductions and reversal thresholds cited in the Validated Mechanism Stack section.
- `scripts/simulate_queueing_overheads.py` — Coordination-overhead sweeps and architecture reversals cited in the Validated Mechanism Stack section.
- `scripts/compression_model.wls` — Compression/offload boundary inequalities cited in the Energy, Economics, Security, and Compression Boundaries section.
- `scripts/evaluate_compression_strategies.py` — Compression safety and queue-attribution results cited in the Energy, Economics, Security, and Compression Boundaries section.
- `scripts/runtime_prototype.py` — Object-registry replay and ablation results cited in the Validated Mechanism Stack section.
- `scripts/build_calibration_map.py` — Calibration map and deferred-constant outputs cited in the Measurement Designs and Deferred Constants section.
- `scripts/evaluate_security_provenance.py` — Security/provenance reuse scoring cited in the Energy, Economics, Security, and Compression Boundaries section.
- `scripts/synthesize_research_agenda.py` — Integrated synthesis rule, risk, and agenda tables cited in the Conclusions and future-work discussion.
- `scripts/evaluate_energy_economics.py` — DC-001/DC-002 energy, economics, and CXL contention sweeps cited in the Energy, Economics, Security, and Compression Boundaries section.
- `scripts/security_enforcement_replay.py` — Trace-v3 security enforcement replay cited in the Energy, Economics, Security, and Compression Boundaries section.
- `scripts/constrained_memory_planner.py` — Compiler/runtime planning results cited in the Runtime, Compiler, and Control Plane Implications section.
- `scripts/build_memory_object_abi.py` — Memory-object ABI contract artifacts cited in the Runtime, Compiler, and Control Plane Implications section.
- `scripts/integrate_memory_object_abi.py` — ABI integration artifacts cited in the Runtime, Compiler, and Control Plane Implications section.
- `scripts/build_architecture_control_plane_progression.py` — Control-plane progression data cited in the Runtime, Compiler, and Control Plane Implications section.
- `scripts/plot_architecture_control_plane_progression.py` — Control-plane progression figure cited in final_report.md.
- `scripts/local_dc12_proxy_bench.py` — Host-local DC-001/DC-002 proxy outputs cited in the Production Evidence Chain section.
- `scripts/ingest_production_dc12_telemetry.py` — Production-shaped telemetry admission and fail-closed replay cited in the Production Evidence Chain section.
- `scripts/build_production_telemetry_deployment_kit.py` — Production telemetry deployment contract cited in the Production Evidence Chain section.
- `scripts/evaluate_future_trends.py` — Future hardware/workload falsification thresholds cited in Falsification Criteria.
- `scripts/run_adapter_conformance.py` — Adapter conformance outputs cited in the Production Evidence Chain section.
- `scripts/evaluate_production_intake.py` — Intake custody and checksum-admission outputs cited in the Production Evidence Chain section.
- `scripts/evaluate_operator_trust_policy.py` — Operator trust-policy gate results cited in the Production Evidence Chain section.
- `scripts/replay_evidence_gatechain.py` — Gatechain replay and zero claim-credit results cited in the Production Evidence Chain and Falsification Criteria sections.
- `scripts/evaluate_timebase_integrity.py` — Timebase and observer-overhead integrity results cited in the Production Evidence Chain section.
- `scripts/evaluate_redaction_integrity.py` — Redaction and replay-identifiability results cited in the Production Evidence Chain section.
- `scripts/evaluate_causal_attribution.py` — Causal attribution and Option A control-validity results cited in Falsification Criteria.
- `scripts/run_production_target_replay.py` — Real production-target replay absence and claim-boundary outputs cited in Falsification Criteria.
- `scripts/validate_gate_evidence_artifacts.py` — Evidence artifact validation outputs cited in the Production Evidence Chain section.
- `scripts/evaluate_live_collector_preflight.py` — Live collector preflight and dry-run boundary results cited in the Production Evidence Chain section.
- `tools/production_evidence_collector.py` — Collector CLI behavior cited in the Production Evidence Chain section.
- `scripts/evaluate_claim_expiry.py` — Claim expiry and lifecycle revalidation outputs cited in Falsification Criteria.
- `scripts/build_final_architecture_package.py` — Final option-readiness and blocked-claim tables cited in the Architecture Package and Reproduction Surface section.
- `scripts/plot_final_architecture_package.py` — Final claim-readiness and option-readiness figures cited in the Architecture Package and Reproduction Surface section.
- `scripts/build_campaign_handoff.py` — Handoff artifact index, claim traceability, reproduction manifest, and experiment-upgrade data cited in the Architecture Package and Reproduction Surface section.
- `scripts/plot_campaign_handoff.py` — Handoff dependency, claim traceability, and experiment-upgrade figures cited in final_report.md.
- `tests/verify_memory_object_abi.py` — ABI verifier cited in the reproduction entry points.
- `tests/verify_memory_object_abi_integration.py` — ABI integration verifier cited in the reproduction entry points.
- `tests/verify_final_architecture_package.py` — Final package verifier cited in the reproduction entry points.
- `tests/verify_campaign_handoff.py` — Handoff verifier cited in the reproduction entry points.
- `tests/verify_architecture_control_plane_progression.py` — Control-plane progression verifier cited in the reproduction entry points.
- `tests/verify_future_trends.py` — Future-trend threshold verifier cited in Falsification Criteria.
- `tests/verify_production_target_replay.py` — Production-target replay verifier cited in Falsification Criteria.
- `tests/verify_live_collector_preflight.py` — Live collector preflight verifier cited in the Production Evidence Chain section.
- `tests/verify_claim_expiry.py` — Claim-expiry verifier cited in Falsification Criteria.

## Script Inventory

### memory-centric-agentic/data

| File | Lines | Purpose |
|---|---:|---|
| `plot_taxonomy_coverage.py` | 56 | Regenerates the workload-by-memory-object taxonomy coverage heatmap. |

### scripts

| File | Lines | Purpose |
|---|---:|---|
| `apply_dc12_proxy_calibration.py` | 326 | Maps host-local DC-001/DC-002 proxy measurements onto existing synthetic threshold and claim-update machinery. |
| `build_adapter_conformance_fixtures.py` | 203 | Builds backend-shaped adapter conformance fixtures and invalid portability cases. |
| `build_architecture_control_plane_progression.py` | 208 | Builds control-plane progression artifacts for memory-object contract validation, runtime/planner checks, and production-credit boundaries. |
| `build_calibration_map.py` | 601 | Builds cited calibration tables, deferred constants, and source-quality summaries. |
| `build_campaign_handoff.py` | 345 | Builds the reproducible campaign hand-off artifact index, claim traceability, reproduction manifest, and open questions. |
| `build_causal_attribution_fixtures.py` | 250 | Builds causal attribution schema, valid and invalid control-arm fixtures, confounder sensitivity grid, and required covariate contract. |
| `build_claim_expiry_fixtures.py` | 180 | Builds production claim lifecycle schema, TTL policy profiles, valid/invalid expiry fixtures, and drift-event cases. |
| `build_evidence_gatechain_fixtures.py` | 281 | Builds end-to-end production evidence gatechain states, transitions, and replay fixture paths. |
| `build_gate_evidence_artifact_contract.py` | 268 | Builds per-gate evidence artifact schema, required fields, dependency graph, and operator checklist. |
| `build_final_architecture_package.py` | 289 | Builds final claim-readiness, architecture-option readiness, blocked-claim, and production-experiment backlog tables. |
| `build_live_collector_contract.py` | 218 | Builds production-side collector capability, operator-input, artifact-mapping, and preflight schema contracts. |
| `build_memory_object_annotations.py` | 215 | Builds memory-object annotation schema, valid and invalid examples, and annotation-requirement fixtures. |
| `build_memory_object_abi.py` | 217 | Builds memory-object ABI contract artifacts and compatibility fixtures. |
| `build_operator_trust_policy_fixtures.py` | 246 | Builds operator trust-policy schema, profiles, key lifecycle controls, and replacement-map fixtures. |
| `build_production_attestation_fixtures.py` | 251 | Builds production attestation envelope schema, valid and invalid envelopes, key registry, and replay registry. |
| `build_production_dc12_fixtures.py` | 284 | Emits valid and invalid production-shaped DC-001/DC-002 telemetry fixtures. |
| `build_production_intake_fixtures.py` | 251 | Builds production intake bundle manifest schema, valid bundle rows, invalid bundle cases, and custody requirements. |
| `build_production_root_enrollment_fixtures.py` | 225 | Builds deployment-root enrollment schema, valid and invalid enrollment fixtures, and counter-binding requirements. |
| `build_production_telemetry_deployment_kit.py` | 437 | Builds the production telemetry deployment collector map, join contract, preflight checks, and pilot design. |
| `build_redaction_integrity_fixtures.py` | 207 | Builds redaction integrity schema, policy profiles, valid and invalid fixtures, and required join-field maps. |
| `build_telemetry_adapter_fixtures.py` | 308 | Builds vendor-neutral telemetry adapter interface fixtures and invalid stream cases. |
| `build_timebase_integrity_fixtures.py` | 289 | Builds timing schema, valid and invalid timing fixtures, and threshold sensitivity cases. |
| `compression_model.wls` | 65 | Exports symbolic compression/offload boundary inequalities and special cases. |
| `constrained_memory_planner.py` | 567 | Plans per-object placement, retention, compression, and recompute actions under security, capacity, queueing, contention, and compression constraints. |
| `cost_model.wls` | 146 | Generates symbolic/synthetic heterogeneous memory cost scenarios and sensitivity data. |
| `evaluate_compression_strategies.py` | 460 | Scores compression/offload strategies by workload and object class, including safety gates and object-level queue interactions. |
| `evaluate_causal_attribution.py` | 239 | Evaluates causal admissibility, confounding, unidentified controls, threshold boundaries, and claim-readiness boundaries. |
| `evaluate_claim_expiry.py` | 142 | Evaluates claim lifecycle status, TTL expiry, deployment drift, revalidation requirements, and zero-credit claim boundaries. |
| `evaluate_energy_economics.py` | 530 | Sweeps DC-001 per-byte energy/cost settings and DC-002 CXL/pooled-memory contention settings over existing architecture decisions. |
| `evaluate_future_trends.py` | 379 | Evaluates synthetic future hardware/workload trend scenarios and falsification thresholds against validated upstream context. |
| `evaluate_live_collector_preflight.py` | 257 | Evaluates production-side collector preflight states, source-material blockers, dry-run labels, and claim-credit boundaries. |
| `evaluate_operator_trust_policy.py` | 300 | Evaluates operator trust-policy admissibility, fail-closed failures, boundary outputs, and traceability links. |
| `evaluate_production_attestation.py` | 322 | Evaluates attestation envelope mechanics, failure modes, replay registry, and intake boundary outputs. |
| `evaluate_production_intake.py` | 341 | Evaluates production intake bundle admission, checksum validity, downstream boundaries, and traceability links. |
| `evaluate_production_root_enrollment.py` | 277 | Evaluates deployment-root enrollment admissibility, failure modes, gatechain boundary rows, and traceability links. |
| `evaluate_redaction_integrity.py` | 248 | Evaluates privacy leakage, replay identifiability, redaction admissibility, and claim-credit boundaries. |
| `evaluate_scheduling_abstractions.py` | 388 | Scores request, job, kernel, model, cache-page, context-segment, memory-object, and trajectory-DAG scheduling units. |
| `evaluate_security_provenance.py` | 576 | Scores security, provenance, isolation, and retention risks by workload and memory object. |
| `evaluate_timebase_integrity.py` | 322 | Evaluates clock-domain, interval, skew, jitter, observer-overhead, counter, and drift integrity. |
| `generate_agentic_trace_v2.py` | 471 | Generates synthetic calibration-ready trace events and derived lifetime/reuse/DAG summaries. |
| `ingest_production_dc12_telemetry.py` | 347 | Validates production-shaped telemetry rows, enforces fail-closed credit accounting, and replays DC-001/DC-002 thresholds. |
| `integrate_memory_object_abi.py` | 448 | Integrates the memory-object ABI with runtime, planner, and verification artifacts. |
| `lifetime_model.wls` | 78 | Generates symbolic lifetime-model special cases and the lifetime regime grid. |
| `lift_trace_to_memory_object_abi.py` | 373 | Lifts conventional trace/runtime/planner records into memory-object ABI candidates and migration-status outputs. |
| `local_dc12_proxy_bench.py` | 315 | Runs host-local byte-movement and process-level shared-memory contention proxy measurements. |
| `merge_trace_annotations_to_abi.py` | 238 | Merges constrained annotations into trace-derived ABI candidates, reruns ABI validation, and emits action-gating outputs. |
| `normalize_telemetry_adapter_streams.py` | 453 | Normalizes offline adapter fixture streams into production-shaped candidate rows and boundary outputs. |
| `plot_adapter_conformance.py` | 83 | Renders adapter conformance coverage, failure, and boundary figures. |
| `plot_agentic_trace_v2.py` | 126 | Renders trace lifetime, live-byte, and branch/DAG figures. |
| `plot_architecture_control_plane_progression.py` | 98 | Renders control-plane progression and production-credit boundary figures. |
| `plot_architecture_synthesis.py` | 164 | Renders architecture option and runtime/compiler hook coverage figures. |
| `plot_calibration_map.py` | 124 | Renders calibration tier ranges, source quality, and model sensitivity targets. |
| `plot_campaign_handoff.py` | 99 | Renders hand-off artifact dependency, traceability coverage, and experiment upgrade-path figures. |
| `plot_causal_attribution.py` | 99 | Renders causal confounder sensitivity, failure-mode, and claim-boundary figures. |
| `plot_claim_expiry.py` | 113 | Renders claim expiry timeline, failure-mode, and revalidation-boundary figures. |
| `plot_compression_strategies.py` | 190 | Renders compression strategy, safety, and object-selective queue-relief figures. |
| `plot_constrained_memory_planner.py` | 130 | Renders planner action mix, binding-constraint, and option-transition figures. |
| `plot_cost_sensitivity.py` | 75 | Regenerates the cost-model sensitivity heatmap. |
| `plot_dc12_proxy_calibration.py` | 116 | Renders host-local proxy byte-movement, contention, and threshold-overlay figures. |
| `plot_energy_economics.py` | 140 | Renders energy/economics sensitivity, CXL-contention threshold, and claim-update figures. |
| `plot_evidence_gatechain.py` | 89 | Renders evidence gatechain state coverage, quarantine reasons, and claim boundary figures. |
| `plot_final_architecture_package.py` | 96 | Renders final claim-readiness, architecture-option readiness, and production-experiment priority figures. |
| `plot_future_trends.py` | 96 | Renders future-trend phase diagram, falsification thresholds, and measurement-priority figures. |
| `plot_gate_evidence_artifacts.py` | 106 | Renders gate-evidence dependency, failure-mode, and replay-readiness boundary figures. |
| `plot_lifetime_regimes.py` | 91 | Regenerates the lifetime regime dominance heatmap. |
| `plot_live_collector_preflight.py` | 109 | Renders live collector capability, failure-mode, and claim-boundary figures. |
| `plot_memory_object_annotations.py` | 84 | Renders annotation merge status, conflict, and option-boundary figures. |
| `plot_operator_trust_policy.py` | 99 | Renders operator trust-policy coverage, failure, and boundary figures. |
| `plot_production_attestation.py` | 96 | Renders attestation envelope coverage, failure mode, and boundary figures. |
| `plot_production_dc12_telemetry.py` | 123 | Renders production telemetry coverage, threshold replay, and claim-gate figures. |
| `plot_production_intake.py` | 83 | Renders production intake manifest coverage, fail-closed failures, and boundary figures. |
| `plot_production_root_enrollment.py` | 89 | Renders deployment-root enrollment coverage, failure modes, and gatechain boundary figures. |
| `plot_production_target_replay.py` | 76 | Renders production-target replay gate-trace and claim-boundary figures. |
| `plot_production_telemetry_deployment.py` | 113 | Renders production telemetry join graph, preflight matrix, and pilot scope figures. |
| `plot_queueing_overheads.py` | 186 | Renders queueing reversal threshold, utilization, and architecture-winner figures. |
| `plot_redaction_integrity.py` | 88 | Renders redaction join-survival, failure-mode, and claim-boundary figures. |
| `plot_runtime_prototype.py` | 135 | Renders runtime architecture boundary, residency, and ablation figures. |
| `plot_scheduling_abstractions.py` | 121 | Renders scheduling abstraction winner and failure-mode figures. |
| `plot_security_enforcement.py` | 166 | Renders safe-reuse waterfall, validation-gate latency, and security-updated architecture figures. |
| `plot_security_provenance.py` | 103 | Renders security risk and mitigation coverage figures. |
| `plot_sim_policy_results.py` | 148 | Renders simulator policy comparison and object-breakdown figures. |
| `plot_timebase_integrity.py` | 92 | Renders timebase skew/overhead sensitivity, failure-mode, and claim-boundary figures. |
| `plot_synthesis.py` | 126 | Renders synthesis architecture, claim-risk, and agenda-priority figures. |
| `plot_telemetry_adapter_results.py` | 125 | Renders adapter stream coverage, join/preflight failure, and claim-boundary figures. |
| `plot_trace_to_abi_lift.py` | 113 | Renders trace-to-ABI lift status, missing-field, and option-fallback figures. |
| `queueing_model.wls` | 70 | Exports symbolic M/M/1 queueing reductions, reversal thresholds, and special cases. |
| `replay_evidence_gatechain.py` | 282 | Replays end-to-end promotion states, quarantines failed gates, and emits claim-credit boundaries. |
| `run_adapter_conformance.py` | 309 | Runs backend profile conformance checks, alias canonicalization, and ingestion-boundary probes. |
| `run_production_target_replay.py` | 352 | Replays real production-target manifests through the validated gate chain and emits absence, rejection, trace, and claim-boundary outputs. |
| `runtime_prototype.py` | 666 | Replays trace v2 into an object registry and emits placement, compression, eviction, and ablation decisions. |
| `security_enforcement_replay.py` | 564 | Extends trace v2 into trace v3 security telemetry, runs enforcement decisions, invalid fixtures, ablations, and architecture updates. |
| `simulate_memory_policies.py` | 470 | Generates synthetic workload events and compares memory placement policies. |
| `simulate_queueing_overheads.py` | 350 | Reconstructs trace rates and sweeps coordination-overhead regimes for architecture reversals. |
| `synthesize_architecture_package.py` | 337 | Synthesizes architecture option, hook, policy, failure-mode, and agenda tables. |
| `synthesize_research_agenda.py` | 646 | Builds final synthesis claim, open-risk, and ranked-agenda tables. |
| `validate_agentic_trace_v2.py` | 195 | Validates positive traces and negative fixtures for schema/order consistency. |
| `validate_gate_evidence_artifacts.py` | 438 | Validates evidence artifact paths, digests, required payload fields, identity continuity, time windows, dependencies, and replay-readiness boundaries. |

### tools

| File | Lines | Purpose |
|---|---:|---|
| `production_evidence_collector.py` | 316 | Conservative production-side collector CLI for preflight, dry-run fixture emission, and production artifact emission guarded by root/operator/source-material requirements. |

### tests

| File | Lines | Purpose |
|---|---:|---|
| `verify_adapter_conformance.py` | 151 | Verifies adapter conformance aliases, invalid profiles, ingestion boundaries, and figures. |
| `verify_architecture_control_plane_progression.py` | 172 | Verifies control-plane progression artifacts, claim boundaries, and figures. |
| `verify_campaign_handoff.py` | 110 | Verifies hand-off artifact traceability, reproduction ordering, open questions, and non-production-ready boundaries. |
| `verify_causal_attribution.py` | 122 | Verifies causal attribution statuses, fail-closed invalid controls, boundary rows, and figures. |
| `verify_claim_expiry.py` | 99 | Verifies claim lifecycle states, TTL boundary, drift/revalidation cases, copied-old-replay rejection, zero-credit boundaries, and figures. |
| `verify_constrained_memory_planner.py` | 153 | Verifies planner outputs, constraint behavior, hook ablations, sensitivity rows, and nonblank figures. |
| `verify_dc005_merge_ready.py` | 212 | Verifies DC-005 merge readiness across the parent M-EXP-1 measurement CSVs. |
| `verify_dc12_proxy_calibration.py` | 150 | Verifies host-local DC-001/DC-002 proxy artifacts, external-validity labels, negative controls, and figures. |
| `verify_evidence_gatechain.py` | 133 | Verifies gatechain states, skipped/out-of-order failures, failed gates, boundaries, traceability, and figures. |
| `verify_final_architecture_package.py` | 116 | Verifies final package readiness boundaries, claim linkage, blocked claims, and figures. |
| `verify_future_trends.py` | 109 | Verifies future-trend axes, falsification thresholds, measurement priorities, context propagation, and non-production-ready labels. |
| `verify_gate_evidence_artifacts.py` | 174 | Verifies artifact contract coverage, fail-closed defect probes, replay-readiness-only semantics, and figures. |
| `verify_live_collector_preflight.py` | 122 | Verifies collector preflight blockers, dry-run labels, missing source-material rejection, zero-credit boundaries, and figures. |
| `verify_memory_object_annotations.py` | 162 | Verifies annotation schema/examples, merge constraints, ABI validation reuse, action gating, and figures. |
| `verify_memory_object_abi.py` | 131 | Verifies memory-object ABI contract artifacts and invalid fixture boundaries. |
| `verify_memory_object_abi_integration.py` | 113 | Verifies memory-object ABI integration with runtime, planner, and control-plane artifacts. |
| `verify_mexp1_integration.py` | 95 | Verifies DC-003 through DC-006 parent measurement-harness integration and absence of placeholder rows. |
| `verify_operator_trust_policy.py` | 124 | Verifies trust-policy schema, invalid profiles, production-trust boundaries, traceability, and figures. |
| `verify_production_attestation.py` | 130 | Verifies attestation envelope schema, invalid envelopes, boundary rows, traceability, and figures. |
| `verify_production_dc12_telemetry.py` | 159 | Verifies production telemetry schema coverage, fail-closed fixture handling, candidate-only rows, claim gates, and figures. |
| `verify_production_intake.py` | 123 | Verifies intake manifest coverage, checksum mismatch blocking, structural-admission boundary, traceability, and figures. |
| `verify_production_root_enrollment.py` | 136 | Verifies root enrollment schema, invalid enrollments, boundary rows, traceability, and figures. |
| `verify_production_target_replay.py` | 145 | Verifies production-target replay absence, negative controls, manifest-only rejection, boundaries, and figures. |
| `verify_production_telemetry_deployment.py` | 114 | Verifies production deployment collector coverage, join keys, preflight blockers, pilot scope, and claim boundaries. |
| `verify_redaction_integrity.py` | 141 | Verifies redaction schema, privacy/replay failures, join preservation, claim boundary, and figures. |
| `verify_security_enforcement_replay.py` | 117 | Verifies trace-v3 security fields, invalid fixture denial/downgrade behavior, ablations, architecture updates, and nonblank figures. |
| `verify_telemetry_adapters.py` | 132 | Verifies telemetry adapter interface coverage, fixture fail-closed behavior, ingestion boundary, and figures. |
| `verify_timebase_integrity.py` | 154 | Verifies timebase schema, timing failures, sensitivity cases, claim boundary, and figures. |

## Model and Data Artifacts

### memory-centric-agentic

| File | Lines | Purpose |
|---|---:|---|
| `adapter_conformance.md` | 39 | Documents the production telemetry adapter portability and conformance kit. |
| `architecture_proposal.md` | 165 | Defines conventional, memory-object-aware, and trajectory/DAG-aware architecture options. |
| `assumptions.md` | 38 | Labels cycle 1 taxonomy assumptions as sourced, derived, simulated-plan, or speculative. |
| `calibration_map.md` | 55 | Maps synthetic model variables to cited public hardware, interconnect, storage, and workload evidence. |
| `causal_attribution.md` | 17 | Documents causal attribution, control-arm validity, confounder checks, and non-production claim boundaries. |
| `claim_expiry_revalidation.md` | 25 | Documents claim TTL, deployment drift, revalidation requirements, copied-old-replay rejection, and lifecycle-status-only semantics. |
| `compression_model.md` | 78 | Defines compression/offload strategies, safety rules, selective queue attribution, and falsification criteria. |
| `constrained_memory_planning.md` | 91 | Documents the synthetic per-object compiler/runtime planning pass and its binding constraints. |
| `cost_assumptions.md` | 53 | Documents symbolic variables, synthetic tier ratios, proxy-score status, and deferred assumptions. |
| `cost_model.md` | 91 | Defines the composable heterogeneous memory cost model. |
| `dc12_local_proxy_calibration.md` | 60 | Documents host-local DC-001/DC-002 proxy measurements and external-validity limits. |
| `energy_economics_contention.md` | 51 | Defines the DC-001/DC-002 energy, dollar, and contention falsification harness. |
| `evidence_gatechain.md` | 25 | Documents end-to-end production evidence gatechain replay and promotion-state boundaries. |
| `final_architecture_package.md` | 47 | Summarizes final claim-readiness, option-readiness, production blockers, and experiment agenda. |
| `final_synthesis.md` | 87 | Consolidates architecture decisions, claims, open risks, and the ranked research agenda. |
| `future_trend_falsification.md` | 56 | Documents synthetic future hardware/workload trend scenarios, thresholds, measurement priorities, and evidence limits. |
| `gate_evidence_artifacts.md` | 28 | Documents concrete evidence artifact requirements for every production replay gate and structural replay-readiness boundaries. |
| `lifetime_model.md` | 75 | Defines object lifetime, reuse, branch, verifier, durable workspace, and collapse equations. |
| `live_collector_preflight.md` | 81 | Documents production-side collector assumptions, source classes, CLI modes, preflight blockers, and claim boundary. |
| `memory_object_annotation_contract.md` | 31 | Documents constrained developer/runtime annotations for non-inferable memory-object ABI fields. |
| `memory_object_abi.md` | 52 | Documents the memory-object ABI and planner-admission boundary. |
| `memory_object_abi_integration.md` | 57 | Documents ABI-to-runtime and constrained-planner integration replay. |
| `operator_trust_policy.md` | 25 | Documents the operator trust-policy gate required before replacing fixture signing with production roots. |
| `production_attestation_envelope.md` | 46 | Documents attestation envelope mechanics and why fixture signatures are not production trust. |
| `production_dc12_telemetry.md` | 58 | Defines production-target telemetry schema, fixture semantics, ingestion gates, and claim-update boundaries. |
| `production_intake_bundle.md` | 27 | Defines production intake bundle manifest, chain-of-custody gate, structural admission, and evidence boundary. |
| `production_root_enrollment.md` | 26 | Documents deployment-root enrollment and collector-root preflight replay boundaries. |
| `production_target_replay.md` | 27 | Documents real production-target manifest replay, evidence-artifact requirements, absence handling, and claim-support boundaries. |
| `production_telemetry_deployment.md` | 60 | Defines the operator-facing collector, join, preflight, and pilot blueprint for future production_target telemetry. |
| `queueing_model.md` | 112 | Defines queueing/coordination-overhead model and architecture reversal inequalities. |
| `redaction_integrity.md` | 24 | Documents telemetry minimization, privacy leakage blocks, replay identifiability, and redaction claim boundaries. |
| `runtime_prototype.md` | 94 | Documents the trace-replay object registry and policy loop prototype. |
| `scheduling_abstractions.md` | 70 | Defines scheduling units as information boundaries. |
| `security_provenance_model.md` | 85 | Defines security, provenance, isolation, and retention gates for memory reuse. |
| `security_telemetry_enforcement.md` | 68 | Documents trace-v3 security telemetry, executable enforcement replay, fixture results, and architecture updates. |
| `simulator_design.md` | 64 | Defines simulator scope, event schema, policies, metrics, and special cases. |
| `taxonomy.md` | 66 | Defines workload classes and memory-object roles. |
| `telemetry_adapter_interface.md` | 51 | Defines vendor-neutral production telemetry adapter streams and offline fixture boundaries. |
| `timebase_integrity.md` | 26 | Documents production telemetry timebase, observer overhead, and measurement-validity preconditions. |
| `trace_calibration_plan.md` | 47 | Maps trace fields to runtime sources and downstream milestones. |
| `trace_to_abi_migration.md` | 32 | Documents legacy trace-to-memory-object ABI lifting and annotation-required boundaries. |
| `trace_schema.md` | 86 | Defines calibration-ready trace events for object lifetime, reuse, branch, verifier, provenance, and durability. |

### memory-centric-agentic/experiments

| File | Lines | Purpose |
|---|---:|---|
| `cache_durable_risk_measurement_plan.md` | 308 | Measurement design for DC-004 semantic-cache correctness/invalidation risk and DC-003 durable replay-tail risk. |
| `dc005_merge_verification.md` | 54 | Documents conductor-facing DC-005 merge verification and reopen conditions. |
| `provenance_overhead_measurement_plan.md` | 344 | Measurement design for DC-006 provenance-validation overhead. |
| `trajectory_reuse_measurement_plan.md` | 298 | Measurement design for DC-005 production trajectory reuse distribution. |

### Key CSV Outputs Added Or Updated By Production Evidence Gate Work

| File | Rows | Purpose |
|---|---:|---|
| `data/operator_trust_policy_schema.csv` | 23 | Required operator trust-policy fields across trust root, key custody, collector binding, replay, audit, and tenant/security dimensions. |
| `data/operator_trust_policy_profiles.csv` | 1 | Complete fixture policy profile that reaches only policy admissibility. |
| `data/operator_trust_policy_invalid_profiles.csv` | 11 | Invalid trust-policy profiles. |
| `data/operator_key_lifecycle_matrix.csv` | 5 | Required key lifecycle phases and fail-closed reasons. |
| `data/operator_attestation_replacement_map.csv` | 10 | Mapping from fixture signing fields to future production KMS/HSM/hardware-attestation replacements. |
| `data/operator_trust_policy_results.csv` | 12 | Policy admissibility, blocked-reason, and production-trust boundary results. |
| `data/operator_trust_policy_failure_modes.csv` | 8 | Fail-closed trust-policy failure categories. |
| `data/operator_trust_policy_boundary.csv` | 12 | Boundary rows showing policy admissibility does not grant production trust or claim credit. |
| `data/operator_trust_policy_traceability_links.csv` | 4 | Links from policy admission to attestation, intake custody, deployment preflight, final readiness, and handoff. |
| `data/evidence_gatechain_state_schema.csv` | 14 | Required promotion states from raw bundle through production claim credit. |
| `data/evidence_gatechain_transition_rules.csv` | 14 | Linear transition rules and identifier-continuity requirements. |
| `data/evidence_gatechain_valid_fixture_paths.csv` | 26 | Validly ordered fixture paths that still quarantine before production claim credit. |
| `data/evidence_gatechain_invalid_fixture_paths.csv` | 202 | Invalid path rows for skipped gates, out-of-order states, identifier mismatches, failed gates, evidence-label violations, and downstream bypass attempts. |
| `data/evidence_gatechain_replay_results.csv` | 19 | Replay summaries; all keep `production_claim_credit_allowed=false`. |
| `data/evidence_gatechain_quarantine_reasons.csv` | 17 | Fail-closed quarantine reasons. |
| `data/evidence_gatechain_claim_credit_boundary.csv` | 19 | Claim-credit boundary rows; Option B/C remain `contract_ready_only`. |
| `data/evidence_gatechain_traceability_matrix.csv` | 5 | Links gatechain states to attestation, intake, adapter conformance, production ingestion, final readiness, and handoff artifacts. |
| `data/production_root_enrollment_schema.csv` | 22 | Required deployment-root enrollment fields across root, collector, firmware, topology, schema, counter, tenant, and security bindings. |
| `data/production_root_valid_enrollments.csv` | 1 | Complete fixture enrollment that reaches only enrollment admissibility. |
| `data/production_root_invalid_enrollments.csv` | 16 | Invalid root-enrollment fixtures. |
| `data/production_root_counter_binding_requirements.csv` | 4 | Counter-source binding requirements. |
| `data/production_root_enrollment_results.csv` | 17 | Enrollment admissibility, blocked-reason, and production-boundary results. |
| `data/production_root_failure_modes.csv` | 16 | Fail-closed root-enrollment failure categories. |
| `data/production_root_gatechain_boundary.csv` | 17 | Boundary rows showing enrollment admissibility does not grant production target status or claim credit. |
| `data/production_root_traceability_links.csv` | 5 | Links root enrollment to trust policy, attestation, intake, adapter/deployment, and gatechain artifacts. |
| `data/timebase_integrity_schema.csv` | 36 | Required timing and observer-overhead integrity fields. |
| `data/timebase_valid_fixture.csv` | 1 | Complete timing fixture that reaches only timing admissibility. |
| `data/timebase_invalid_fixtures.csv` | 21 | Invalid timing fixtures. |
| `data/timebase_threshold_sensitivity_cases.csv` | 120 | Skew, jitter, overhead, and drift sensitivity cases. |
| `data/timebase_integrity_results.csv` | 22 | Timing admissibility, measurement-invalid reasons, and threshold replay status. |
| `data/timebase_failure_modes.csv` | 21 | Fail-closed timing and observer-overhead failure categories. |
| `data/timebase_threshold_replay_boundary.csv` | 22 | Boundary rows showing invalid timing blocks threshold replay as measurement-invalid. |
| `data/timebase_claim_credit_boundary.csv` | 22 | Claim-credit boundary rows; all keep claim credit blocked. |
| `data/redaction_integrity_schema.csv` | 23 | Required redaction and replay-identifiability fields. |
| `data/redaction_policy_profiles.csv` | 7 | Redaction policy profiles used to compare privacy leakage and join survival. |
| `data/redaction_valid_fixture.csv` | 1 | Complete redaction fixture that reaches only redaction admissibility. |
| `data/redaction_invalid_fixtures.csv` | 20 | Invalid redaction fixtures. |
| `data/redaction_required_join_fields.csv` | 11 | Required replay join fields and pseudonym/coarsening rules. |
| `data/redaction_integrity_results.csv` | 21 | Redaction admissibility, privacy leakage, replay identifiability, and blocked reasons. |
| `data/redaction_failure_modes.csv` | 16 | Fail-closed redaction failure categories. |
| `data/redaction_join_replay_boundary.csv` | 21 | Boundary rows showing whether redacted exports remain replay-identifiable. |
| `data/redaction_claim_credit_boundary.csv` | 21 | Claim-credit boundary rows; all keep production claim credit blocked. |
| `data/causal_attribution_schema.csv` | 16 | Required causal attribution and control-arm validity fields. |
| `data/causal_valid_fixture.csv` | 2 | Causally admissible fixtures, including robust pass and robust fail cases. |
| `data/causal_invalid_fixtures.csv` | 14 | Invalid causal fixtures for missing controls, imbalance, positivity failure, post-treatment adjustment, and fixture production-calibration attempts. |
| `data/causal_confounder_sensitivity_grid.csv` | 48 | Confounder sensitivity grid used to expose causal-admissibility boundaries. |
| `data/causal_required_covariates.csv` | 10 | Required pre-treatment covariates for Option A control comparison. |
| `data/causal_attribution_results.csv` | 16 | Causal evaluation results separating admissible, confounded, and unidentified cases. |
| `data/causal_failure_modes.csv` | 14 | Fail-closed causal attribution failure categories. |
| `data/causal_threshold_boundary.csv` | 16 | Threshold-boundary rows after causal screening. |
| `data/causal_claim_readiness_boundary.csv` | 16 | Claim-readiness boundary rows; all keep production claim credit blocked. |
| `data/production_target_replay_results.csv` | 17 | Real production-target replay results covering absence and non-production negative controls. |
| `data/production_target_replay_gate_trace.csv` | 1 | Gate trace for the current no-production-target replay state. |
| `data/production_target_replay_claim_boundary.csv` | 17 | Claim-boundary rows proving no current replay row earns production calibration, readiness, claim credit, or architecture endorsement. |
| `data/production_target_replay_absence_report.csv` | 1 | Absence report showing zero manifests and zero production-target manifests under `data/production_target_bundle`. |
| `data/gate_evidence_artifact_schema.csv` | 13 | Per-gate evidence artifact contract rows for the production replay gates. |
| `data/gate_evidence_required_fields.csv` | 221 | Required payload, identity, digest, and linkage fields for concrete evidence artifacts. |
| `data/gate_evidence_dependency_graph.csv` | 13 | Dependency ordering among production replay evidence gates. |
| `data/gate_evidence_operator_checklist.csv` | 78 | Operator-facing checklist for producing gate evidence artifacts. |
| `data/gate_evidence_artifact_validation_results.csv` | 44 | Offline structural validation results for complete and defect-probe evidence bundles. |
| `data/gate_evidence_failure_modes.csv` | 10 | Fail-closed artifact validation categories. |
| `data/gate_evidence_replay_readiness_boundary.csv` | 12 | Boundary rows proving artifact completeness is only replay readiness and grants no claim credit. |
| `data/live_collector_capability_matrix.csv` | 13 | Collector source-class mapping for each gate evidence artifact. |
| `data/live_collector_required_operator_inputs.csv` | 5 | Operator-supplied or external trust-bearing inputs required before production artifact emission. |
| `data/live_collector_artifact_mapping.csv` | 13 | Mapping from collector inputs to downstream M-EVIDART artifact fields. |
| `data/live_collector_preflight_schema.csv` | 22 | Preflight fields and checks for production-side evidence collection. |
| `data/live_collector_preflight_results.csv` | 12 | Preflight/dry-run probe results covering blocked production and dry-run fixture paths. |
| `data/live_collector_failure_modes.csv` | 3 | Aggregated fail-closed live collector failure categories. |
| `data/live_collector_claim_boundary.csv` | 12 | Claim-boundary rows proving collector preflight and dry-run artifacts grant no production claim credit. |
| `data/claim_expiry_schema.csv` | 18 | Claim lifecycle input fields for TTL, identity, drift, and evidence label checks. |
| `data/claim_expiry_policy_profiles.csv` | 2 | Default and short-pilot lifecycle policy profiles. |
| `data/claim_expiry_valid_fixture.csv` | 1 | Hypothetical fresh prior production replay lifecycle fixture. |
| `data/claim_expiry_invalid_fixtures.csv` | 17 | Stale, drifted, invalidated, copied-old-replay, and non-production lifecycle fixtures. |
| `data/claim_expiry_drift_events.csv` | 14 | Drift and invalidation events mapped to revalidation or invalidation outcomes. |
| `data/claim_expiry_results.csv` | 18 | Claim lifecycle evaluation results across currently supportable, expired, invalidated, revalidation-required, and unsupported cases. |
| `data/claim_expiry_failure_modes.csv` | 13 | Fail-closed lifecycle failure categories. |
| `data/claim_expiry_revalidation_boundary.csv` | 18 | Boundary rows proving stale or changed deployment support requires fresh production material. |
| `data/claim_expiry_claim_boundary.csv` | 18 | Claim-boundary rows separating lifecycle support from production calibration/readiness/claim credit. |
| `data/trace_to_abi_lift_results.csv` | 9 | Legacy trace-to-ABI lift outcomes: ABI-admissible, annotation-required, fail-closed, or Option A opaque fallback. |
| `data/trace_to_abi_missing_fields.csv` | 7 | Missing or ambiguous ABI fields that block or qualify legacy trace lifting. |
| `data/trace_to_abi_option_fallbacks.csv` | 9 | Option routing and fallback behavior for lifted legacy trace candidates. |
| `data/trace_to_abi_annotation_requirements.csv` | 3 | Annotation classes required for non-inferable fields surfaced by trace lifting. |
| `data/memory_object_annotation_schema.csv` | 8 | Annotation classes and the ABI fields each class is allowed to complete. |
| `data/memory_object_annotation_requirements.csv` | 5 | Required annotation-completion cases for trace-derived ABI candidates. |
| `data/annotation_merge_results.csv` | 17 | Deterministic trace-plus-annotation merge outcomes and action-count boundaries. |
| `data/annotation_conflict_failures.csv` | 10 | Fail-closed conflict cases for unsafe or incomplete annotations. |
| `data/annotation_integration_results.csv` | 17 | Annotation merge results replayed through ABI validation and integration accounting. |
| `data/annotation_option_boundary.csv` | 17 | Option-routing and claim-credit boundary rows for annotation outputs. |

## Cumulative Stats

| Category | Count |
|---|---:|
| Python scripts in `scripts/` | 99 |
| Wolfram scripts in `scripts/` | 4 |
| Test scripts | 30 |
| Tools scripts | 1 |
| Total `scripts/` lines | 24,344 |
| Markdown model/synthesis files under `memory-centric-agentic/` | 44 |
| Experiment-plan and verification markdown files | 4 |
| CSV data/model files under `data/` | 250 |
| Figures under `data/` | 113 |
| Sub-topics completed, assessed, or designed | 39 |

Completed, assessed, or designed sub-topics now include `M-ROOTINT-1`, `M-TIMEBASE-1`, `M-REDACT-1`, `M-UNCERT-1`, `M-CAUSAL-1`, `M-PRODREPLAY-1`, `M-EVIDART-1`, `M-LIVECOLLECT-1`, `M-CLAIMEXP-1`, `M-ABI-1`, `M-ABIINT-1`, `M-ARCHPKG-1`, `M-TRACEABI-1`, and `M-ANNOT-1` in addition to prior taxonomy, lifetime, cost, simulation, scheduling, architecture, trace, queueing, compression, runtime, calibration, security, synthesis, measurement, energy, security-operations, planning, proxy-calibration, production-telemetry, final-package, handoff, deployment, trend, adapter, conformance, intake, attestation, trust-policy, and gatechain milestones.

## Cross-References

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/production_attestation_results.csv` | `data/operator_attestation_replacement_map.csv`, `data/evidence_gatechain_state_schema.csv` | Mechanical test attestation remains upstream evidence and must be replaced by real operator trust roots before production trust. |
| `data/operator_trust_policy_results.csv` | `data/evidence_gatechain_valid_fixture_paths.csv`, `data/evidence_gatechain_transition_rules.csv` | Policy admissibility becomes a required gatechain state but cannot by itself grant production trust. |
| `data/production_intake_admission_results.csv` | `data/evidence_gatechain_valid_fixture_paths.csv`, `data/evidence_gatechain_traceability_matrix.csv` | Intake admission is required before adapter conformance and production ingestion states. |
| `data/adapter_conformance_results.csv` | `data/evidence_gatechain_valid_fixture_paths.csv` | Adapter conformance is required before adapter normalization and production ingestion. |
| `data/production_dc12_ingestion_results.csv` | `data/evidence_gatechain_replay_results.csv`, `data/evidence_gatechain_claim_credit_boundary.csv` | Production ingestion, security/provenance, noise-floor, and threshold gates are replayed before any claim-credit attempt. |
| `data/final_claim_readiness_matrix.csv` and `data/handoff_claim_traceability.csv` | `data/evidence_gatechain_traceability_matrix.csv` | Final readiness and handoff traceability are required downstream gates before claim credit. |
| `data/production_root_enrollment_results.csv` | `data/timebase_valid_fixture.csv`, `data/timebase_integrity_results.csv` | Deployment-root enrollment is upstream identity/root continuity for timing-admissible telemetry. |
| `data/timebase_integrity_results.csv` | `data/redaction_valid_fixture.csv`, `data/redaction_integrity_results.csv` | Timebase-admissible telemetry is the source fixture class that redaction must preserve for replay. |
| `data/redaction_required_join_fields.csv` | `data/redaction_join_replay_boundary.csv`, `data/redaction_claim_credit_boundary.csv` | Stable pseudonym and coarsening rules define whether redacted telemetry remains replay-identifiable without leaking raw tenant/tool-output identifiers. |
| `data/uncertainty_evaluation_results.csv` | `data/causal_valid_fixture.csv`, `data/causal_attribution_results.csv` | Confidence-qualified threshold outcomes become the input class for causal attribution and control-arm validity. |
| `data/causal_attribution_results.csv` | `data/production_target_replay_results.csv`, `data/production_target_replay_claim_boundary.csv` | Robust but causally invalid controls remain blocked before production-target claim-support candidacy. |
| `data/production_target_replay_absence_report.csv` | `data/production_target_replay_results.csv`, `data/production_target_replay_claim_boundary.csv` | Absence of real production-target manifests materializes as no telemetry available and zero claim credit. |
| `data/gate_evidence_required_fields.csv` | `data/gate_evidence_artifact_validation_results.csv`, `data/gate_evidence_replay_readiness_boundary.csv` | Concrete payload, digest, identity, time-window, and dependency fields are required before a production-target replay can consume a manifest. |
| `data/gate_evidence_operator_checklist.csv` | `data/live_collector_capability_matrix.csv`, `data/live_collector_artifact_mapping.csv` | Operator-facing artifact requirements become collector source-class and artifact-field mappings. |
| `data/live_collector_preflight_results.csv` | `data/claim_expiry_results.csv`, `data/claim_expiry_revalidation_boundary.csv` | Collector preflight and dry-run boundaries define the current production-material absence that lifecycle revalidation must not bypass. |
| `data/production_target_replay_claim_boundary.csv` | `data/claim_expiry_claim_boundary.csv` | A prior production replay can only become lifecycle-supportable within TTL and unchanged deployment assumptions; the current workspace still grants no production claim credit. |
| `data/runtime_policy_decisions.csv` and `data/memory_plan_actions.csv` | `data/trace_to_abi_lift_results.csv`, `data/trace_to_abi_option_fallbacks.csv` | Existing runtime/planner decisions provide the migration source context for trace-derived ABI candidates. |
| `data/trace_to_abi_lift_results.csv` | `data/trace_to_abi_annotation_requirements.csv`, `data/annotation_merge_results.csv` | Trace lifting identifies which candidates are already ABI-admissible, which fail closed, and which require constrained annotations. |
| `data/memory_object_annotation_examples.jsonl` | `data/annotation_merge_results.csv`, `data/annotation_conflict_failures.csv` | Annotation examples are merged into trace-derived candidates and either complete ABI contracts or fail closed. |
| `data/annotation_merge_results.csv` | `data/annotation_integration_results.csv`, `data/annotation_option_boundary.csv` | Completed annotation candidates are rerun through ABI validation and integration action gating before any Option B/C routing. |
| `REFERENCES.md` | reports and calibration artifacts | Public sources provide global numbered references for hardware, interconnect, storage, prefix caching, semantic caching, and benchmark context. |

## Validation Snapshot

- `M-TRUSTPOL-1`: auditor-validated in cycle 29 after enforcing collector firmware identity binding and normalizing replacement-map booleans; regenerated 23 schema rows, 1 complete profile, 11 invalid profiles, 5 key-lifecycle rows, 10 replacement-map rows, 12 policy results, 8 failure categories, 12 boundary rows, 4 traceability links, and three nonblank figures. Verifier, py_compile, independent CSV/figure probe, promise_check, and org_check passed with only known root package warnings.
- `M-GATECHAIN-1`: auditor-validated in cycle 30 after enforcing `state_passed == true`; regenerated 14 state rows, 14 transition rules, 26 valid fixture rows, 202 invalid fixture rows, 19 replay summaries, 17 quarantine reasons, 19 claim-credit boundary rows, 5 traceability rows, and three nonblank figures. Verifier, py_compile, independent failed-gate probe, independent CSV/figure probe, promise_check, and org_check passed with only known root package warnings.
- `M-ROOTINT-1`: auditor-validated in cycle 31 after enforcing root and identifier continuity; regenerated 22 schema rows, 1 valid enrollment, 16 invalid enrollments, 4 counter-binding requirements, 17 evaluation rows, 16 failure modes, 17 gatechain-boundary rows, 5 traceability links, and three nonblank figures. Verifier, py_compile, independent mismatch probes, independent CSV/figure checks, promise_check, and org_check passed with only known root package warnings.
- `M-TIMEBASE-1`: auditor-validated in cycle 32 after enforcing source join, identifier continuity, and numeric-domain fail-closed checks; regenerated 36 schema rows, 1 valid fixture, 21 invalid fixtures, 120 sensitivity cases, 22 evaluation rows, 21 failure modes, 22 replay-boundary rows, 22 claim-boundary rows, and three nonblank figures. Verifier, py_compile, independent fail-closed probes, CSV/figure checks, promise_check, and org_check passed with only known root package warnings.
- `M-REDACT-1`: auditor-validated in cycle 33 after enforcing source-fixture, evidence-label, and collision-count fail-closed checks; regenerated 23 schema rows, 1 valid fixture, 20 invalid fixtures, 11 required join fields, 21 evaluation rows, 16 failure modes, 21 replay-boundary rows, 21 claim-boundary rows, and three nonblank figures. Verifier, py_compile, independent fail-closed probes, CSV/figure checks, promise_check, and org_check passed with only known root package warnings.
- `M-CAUSAL-1`: auditor-validated in cycle 35 without code changes; regenerated 16 schema rows, 2 valid fixtures, 14 invalid fixtures, 48 sensitivity rows, 10 required covariate rows, 16 evaluation rows, 14 failure modes, 16 threshold-boundary rows, 16 claim-boundary rows, and three nonblank figures. Causal verifier, py_compile, independent CSV/figure checks, promise_check, and org_check passed with only known root warnings.
- `M-PRODREPLAY-1`: auditor-validated in cycle 36 after closing a critical manifest-only self-attestation path; regenerated 17 replay result rows, 1 gate-trace row, 17 claim-boundary rows, 1 absence row, and two nonblank figures. Replay, plot, verifier, py_compile, independent CSV/figure probes, promise_check, and org_check passed with only known root warnings.
- `M-EVIDART-1`: auditor-validated in cycle 37 after closing a critical missing-required-payload-field bypass; regenerated 13 artifact schema rows, 221 required-field rows, 13 dependency rows, 78 checklist rows, 44 validation rows, 10 failure modes, 12 replay-readiness boundary rows, and three nonblank figures. Gate evidence verifier, adjacent production-target replay verifier, py_compile, independent CSV/figure probes, promise_check, and org_check passed with only known root warnings.
- `M-LIVECOLLECT-1`: auditor-validated in cycle 38 after closing a critical missing gate-source-material production emission bypass; regenerated 13 capability rows, 5 operator-input rows, 13 artifact-mapping rows, 22 preflight schema rows, 12 preflight results, 3 failure modes, 12 claim-boundary rows, and three nonblank figures. Live collector verifier, M-EVIDART verifier, adjacent production-target replay verifier, py_compile, independent CSV/figure probes, promise_check, and org_check passed with only known root warnings.
- `M-CLAIMEXP-1`: auditor-validated in cycle 39 after closing a critical lifecycle-status-to-production-credit overclaim; regenerated 18 schema rows, 2 policy profiles, 1 valid fixture, 17 invalid fixtures, 14 drift-event rows, 18 evaluation rows, 13 failure modes, 18 revalidation-boundary rows, 18 claim-boundary rows, and three nonblank figures. Claim expiry verifier, adjacent live collector/evidence/replay verifiers, py_compile, direct CSV/figure probes, promise_check, and org_check passed with only known root warnings.
- `M-TRACEABI-1`: auditor-validated in cycle 44 after tightening candidate-specific integration-boundary accounting; regenerated 9 lift-result rows, 7 missing-field rows, 9 option-fallback rows, 3 annotation-requirement rows, and three nonblank figures. Trace-lift verifier, adjacent ABI/integration/control-plane regressions, promise_check, and org_check passed with only known root warnings.
- `M-ANNOT-1`: auditor-validated in cycle 45 without implementation patch; regenerated 8 annotation-schema rows, 17 annotation examples, 5 annotation-requirement rows, 17 merge-result rows, 10 conflict-failure rows, 17 integration-result rows, 17 option-boundary rows, and three nonblank figures. Annotation verifier, syntax compile, adjacent trace/ABI/integration/control-plane regressions, promise_check, and org_check passed with only known root warnings.
- Current production boundary: fixture signatures, trust-policy profiles, adapter fixtures, conformance fixtures, intake fixtures, deployment-root fixtures, timebase fixtures, redaction fixtures, uncertainty fixtures, causal fixtures, gate evidence fixtures, dry-run collector artifacts, lifecycle fixtures, synthetic trends, planned deployments, host-local proxies, trace-lift fixtures, and annotation fixtures remain non-production evidence. Real `production_target` telemetry with linked gate evidence artifacts, complete production-side source material, real deployment-root integration, fresh lifecycle revalidation, and production-grade annotation provenance is still required before any DC-001/DC-002 or Option B/C claim can become production-ready.
