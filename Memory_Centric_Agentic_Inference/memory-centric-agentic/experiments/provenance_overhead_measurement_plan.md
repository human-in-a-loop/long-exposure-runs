---
created: 2026-05-11T18:55:00Z
run_id: run-2026-05-11T121649Z
fork: 523f4e7604d4
clone: 1
milestone: M-EXP-1
deferred_constant: DC-006
artifact_type: measurement_design
---

# Provenance-Validation Overhead Measurement Plan

## Scope

This branch designs the measurement path for DC-006, provenance-validation overhead. The quantity is not a single constant. It is the measured cost of the validation gates that must pass before retained memory state can contribute positive value:

```text
AuthorizedReuse(object, actor, source_version, lineage, invalidation_state) = true

SecurityAdjustedValue =
  RetainedValue
  - CoordinationOverhead
  - ValidationOverhead
  - ExpectedSecurityLoss
```

M-SEC-1 established that unsafe reuse must be rejected or downgraded. M-SYNTH-1 established that Option B and Option C remain conditional because validation overhead can erase retained value. This plan defines how to measure that overhead without treating synthetic security scores as calibrated production data.

## Mechanism Hypothesis

I think Option B/C reversals occur when the validation work required to prove safe reuse scales with reused objects, trajectory edges, verifier evidence, and retention state faster than retained-value benefit scales with reuse. This measurement rules the mechanism in if observed per-object or per-replay validation overhead exceeds the visible retained-value margin for RAG, code-agent, verification-heavy, or branch/merge workloads. It rules the mechanism out if validation overhead stays below the retained-value margin at target concurrency while invalid fixtures are still rejected.

The relevant boundary expressions are:

```text
Option B valid iff
  Benefit_object_reuse
  > Q_registry + Q_policy + Q_migration + ValidationOverhead_object + ExpectedSecurityLoss_object

Option C valid iff
  Benefit_branch_verifier_durable
  > Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption
    + ValidationOverhead_trajectory + ExpectedSecurityLoss_trajectory
```

The measurement target is the validation-overhead term. Queueing, semantic correctness, durable-store latency, and production trajectory-reuse rates remain separate axes unless a probe explicitly records them as covariates.

## Existing Evidence Used

| Source artifact | Relevant finding | How this plan uses it |
|---|---|---|
| `memory-centric-agentic/security_provenance_model.md` | Retained value is counted only after authorization, provenance, freshness, isolation, lineage, verifier, and retention checks pass. | Defines the validation gates and downgrade behavior. |
| `memory-centric-agentic/trace_schema.md` | Trace v2 has provenance, source-version, invalidation, branch, verifier, and durability fields, but lacks production security fields. | Defines baseline fields and missing trace-v3 fields. |
| `data/security_invalid_trace_fixtures.csv` | Missing tenant/cache salt, replay authorization, verifier evidence hash, and retention hold state require new instrumentation. | Defines negative-test fixtures that measurement must reject. |
| `data/security_workload_summary.csv` | Synthetic validation overhead reverses Option B/C for RAG and agentic workloads. | Defines the workload-level reversal targets. |
| `data/synthesis_architecture_decision_matrix.csv` | RAG is Option B; code-agent, verification-heavy, and branch/merge are Option C, with synthetic security reversal risk. | Defines which decisions DC-006 can update. |
| `data/runtime_ablation_results.csv` | Hiding provenance/reuse collapses RAG to A; hiding branch/verifier/durable collapses Option C to B/A. | Defines causal-field ablations to preserve in measurement. |
| `data/calibration_deferred_constants.csv` | DC-006 lacks public measured validation constants. | Keeps all results here as measurement design until production or benchmark data exists. |

## Validation Gates To Measure

| Gate ID | Gate | Objects affected | Required fields | Unit of work | Failure response |
|---|---|---|---|---|---|
| PV-01 | Provenance pointer presence and lookup | retrieved context, semantic cache entry, tool output, trajectory log, durable workspace | `provenance_id` | per reused object | block or recompute |
| PV-02 | Source-version freshness | retrieved context, semantic cache entry, tool output, durable workspace | `source_version`, `invalidation_signal` | per reused object plus source lookup | revalidate or recompute |
| PV-03 | Tenant scope and cache-salt isolation | KV cache, prefix cache, semantic cache entry, branch state | `tenant_scope`, `cache_salt` | per cache lookup or shared-state access | forbid cross-boundary reuse |
| PV-04 | Trajectory lineage validation | branch state, tool output, trajectory log, verifier state | `trajectory_node_id`, `branch_id`, `parent_object_id`, `merge_state` | per replay edge or merge edge | reject replay or downgrade to Option B |
| PV-05 | Replay actor authorization | trajectory log, branch state, tool output, durable workspace | `actor_id`, `replay_authorization_scope` | per replay attempt | reject replay |
| PV-06 | Verifier evidence binding | verifier state, branch state, trajectory log | `verifier_id`, `verifier_evidence_hash`, `merge_state` | per verifier result reused | reject replay or rerun verifier |
| PV-07 | Retention and hold-state compliance | durable workspace, trajectory log | `durability_horizon`, `retention_hold_state` | per durable read/write/replay | expire, preserve under hold, or reject |
| PV-08 | Summary-pointer recoverability | tool output, durable workspace, branch state, trajectory log, verifier state | `provenance_id`, `source_version`, recovery pointer, compression strategy | per compressed/pointer object | retain exact state or recompute |

Trace v2 already covers PV-01, PV-02, part of PV-04, and part of PV-07. Production-strength measurement requires the new M-SEC-1 fields: `tenant_scope`, `cache_salt`, `actor_id`, `replay_authorization_scope`, `verifier_evidence_hash`, and `retention_hold_state`.

## Metrics

| Metric ID | Metric | Definition | Why it matters |
|---|---|---|---|
| M-PV-LAT-OBJ | Per-object validation latency | elapsed time from validation start to allow/reject for one reused object | Direct Option B overhead term. |
| M-PV-LAT-REPLAY | Per-trajectory-replay validation latency | elapsed time for lineage, authorization, verifier, and retention validation over one replay attempt | Direct Option C overhead term. |
| M-PV-CPU | CPU time per validation gate | CPU nanoseconds or cycles grouped by gate ID | Distinguishes latency from compute load. |
| M-PV-IO | External lookup count and latency | source-version, provenance-store, authorization, verifier-evidence, and retention-policy lookups | Identifies whether validation is local metadata work or remote dependency work. |
| M-PV-QWAIT | Validation queue wait | queue delay before validation service begins | Prevents undercounting overloaded validation services. |
| M-PV-BLOCK | Blocked reuse rate | invalid or missing-field events divided by reuse attempts | Confirms safety gates are active. |
| M-PV-FN | Unsafe-pass rate | invalid fixtures or labeled unsafe reuses that pass validation | Must be zero for value to count. |
| M-PV-COLLAPSE | Architecture collapse threshold | first overhead level where Option B/C net value becomes nonpositive | Connects measurement to architecture selection. |

All metrics must be reported as distributions, not only means: p50, p90, p95, p99, max, and workload-normalized total overhead per completed agent step.

## Experiment Designs

### EXP-PROV-MICRO-001: Gate Microbenchmark

Purpose: isolate latency and CPU cost for each validation gate.

Procedure:
1. Construct valid and invalid fixtures for PV-01 through PV-08.
2. Run each gate locally with hot metadata, cold metadata, and missing metadata.
3. Record p50/p95/p99 latency, CPU time, external lookup count, and blocked-reuse rate.

Support criterion: all invalid fixtures are rejected, and p95 gate overhead stays below the retained-value margin for the relevant object class.

Falsification criterion: any invalid fixture passes, or p95 overhead for common gates PV-01/PV-02/PV-03 exceeds the RAG Option B retained-value margin.

Output rows:
- `experiment_id = EXP-PROV-MICRO-001`
- updates claims `CL-002`, `CL-006`, `CL-009`, `CL-010`
- output type `measurement_design`

### EXP-PROV-REPLAY-002: End-to-End Trace Replay Validation

Purpose: measure cumulative overhead when provenance checks run inside an object-registry replay loop.

Procedure:
1. Extend the trace replay harness with synthetic trace-v3 security fields.
2. Replay RAG, code-agent, verification-heavy, and multi-agent branch/merge traces.
3. Validate every object access, semantic-cache lookup, tool-output replay, branch merge, verifier result reuse, and durable workspace replay.
4. Compare architecture decision before and after measured validation overhead is subtracted.

Support criterion: Option B/C decisions survive when validation is enabled and invalid fixtures are still rejected.

Falsification criterion: measured validation overhead makes RAG Option B or agentic Option C net value nonpositive at target concurrency.

Output rows:
- updates claims `CL-002`, `CL-003`, `CL-009`, `CL-011`
- directly feeds `measurement_thresholds.csv`

### EXP-PROV-ISOLATION-003: Tenant and Cache-Salt Reuse A/B

Purpose: test whether isolation fields erase most useful prefix or semantic cache reuse.

Procedure:
1. Partition cache entries by `tenant_scope` and `cache_salt`.
2. Measure raw hit rate, safe hit rate, blocked hit rate, and overhead per lookup.
3. Run with shared cache, tenant-partitioned cache, and salt-partitioned cache.

Support criterion: safe hit rate remains high enough that Option B value stays positive after isolation overhead.

Falsification criterion: safe hit rate collapses or per-hit validation overhead exceeds recompute savings.

Output rows:
- updates claims `CL-002`, `CL-009`, `CL-010`
- distinguishes DC-006 from DC-004 by measuring validation overhead and safe-hit loss, not semantic false-positive correctness.

### EXP-PROV-LINEAGE-004: Trajectory Lineage and Replay Authorization

Purpose: measure Option C-specific validation cost.

Procedure:
1. Generate replay attempts across accepted, rejected, discarded, merged, and contaminated branches.
2. Validate `trajectory_node_id`, `branch_id`, `parent_object_id`, `merge_state`, `actor_id`, and `replay_authorization_scope`.
3. Record per-edge validation latency, rejected replay rate, and downgrade rate to Option B.

Support criterion: lineage and replay authorization overhead stays below branch/verifier/durable retained-value margin.

Falsification criterion: lineage checks or authorization lookups dominate retained value or fail to catch branch contamination.

Output rows:
- updates claims `CL-003`, `CL-005`, `CL-009`, `CL-011`

### EXP-PROV-VERIFIER-005: Verifier Evidence Hash Binding

Purpose: measure cost of making verifier-state reuse tamper-evident.

Procedure:
1. Bind `verifier_id`, candidate branch, verifier result, and evidence payload hash.
2. Reuse verifier state with matching hash, mismatched hash, missing hash, and stale branch lineage.
3. Measure hashing cost, metadata lookup cost, rerun/downgrade decisions, and false unsafe-pass rate.

Support criterion: verifier evidence checks reject tampering with negligible unsafe-pass rate and overhead below verifier recomputation savings.

Falsification criterion: tampered evidence passes, or hash/lookup overhead makes verifier-state retention valueless.

Output rows:
- updates claims `CL-003`, `CL-009`, `CL-010`

### EXP-PROV-RETENTION-006: Retention Hold and Durable Replay Compliance

Purpose: measure durable-state validation overhead for retention and audit/deletion conflicts.

Procedure:
1. Reuse durable workspace and trajectory log objects across valid horizon, expired horizon, legal/audit hold, and deletion-request states.
2. Validate `durability_horizon` and `retention_hold_state`.
3. Record read/write/replay validation latency, policy lookup latency, blocked replay rate, and downgrade behavior.

Support criterion: retention validation prevents overrun without making durable replay slower than recompute or local exact retention.

Falsification criterion: retention hold validation is missing, allows expired reuse, or adds tails that erase durable replay value.

Output rows:
- updates claims `CL-003`, `CL-009`, `CL-010`
- records DC-003 durable-store latency as a covariate, not as the primary axis.

### EXP-PROV-POINTER-007: Summary-Plus-Pointer Recovery Validation

Purpose: measure provenance overhead for pointer-preserving compression/offload.

Procedure:
1. For tool outputs, durable workspace state, branch state, trajectory logs, and verifier state, validate summary pointer, provenance pointer, source version, and exact recovery path.
2. Compare exact retention, lossless compression, summary-plus-pointer, and recompute-on-demand.
3. Record validation overhead, reconstruction overhead, blocked unsafe pointer rate, and net compression value after provenance checks.

Support criterion: summary-plus-pointer remains positive only when exact recovery and provenance validation both pass.

Falsification criterion: pointer validation overhead exceeds byte-movement/capacity benefit or any missing pointer is allowed.

Output rows:
- updates claims `CL-006`, `CL-007`, `CL-009`

## Threshold Computation

The worker integrating this branch should compute threshold rows with the following forms.

For RAG Option B:

```text
PV_budget_B_RAG =
  visible_retained_value_proxy_RAG
  - (Q_registry + Q_policy + Q_migration)
  - ExpectedSecurityLoss_object

Option B collapses to A if:
  measured_validation_overhead_per_reused_object * reused_object_count
  + validation_queue_wait
  > PV_budget_B_RAG
```

For Option C workloads:

```text
PV_budget_C_workload =
  visible_retained_value_proxy_workload
  - (Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption)
  - ExpectedSecurityLoss_trajectory

Option C collapses to B or A if:
  measured_lineage_authorization_verifier_retention_overhead
  + validation_queue_wait
  > PV_budget_C_workload
```

Use the current synthetic visible retained-value proxies only as placeholders for threshold wiring:

| Workload | Current option | Visible retained value proxy | Security-adjusted value proxy | Interpretation |
|---|---:|---:|---:|---|
| RAG | B | 10.8 | -30.631 | Synthetic security overhead can erase Option B. |
| code-agent loop | C | 31.8 | -45.023 | Option C is sensitive to replay authorization and lineage checks. |
| multi-agent branch/merge | C | 50.0 | -26.823 | Higher retained value gives more headroom, but replay ambiguity risk is high. |
| verification-heavy | C | 33.8 | -17.675 | Verifier evidence binding is the critical DC-006 component. |

These numbers are not calibrated production constants. They are threshold scaffolding: measured overhead replaces the synthetic validation term.

## Required Trace V3 Additions

| New field | Type | Required for | Reason |
|---|---|---|---|
| `tenant_scope` | opaque token | PV-03 | Prevent cross-tenant cache or shared-state aliasing. |
| `cache_salt` | opaque token | PV-03 | Separate cache trust domains. |
| `actor_id` | opaque token | PV-05 | Bind replay to an authorized actor or agent identity. |
| `replay_authorization_scope` | enum or capability token | PV-05 | Distinguish allowed branch replay from unauthorized trajectory reuse. |
| `verifier_evidence_hash` | digest token | PV-06 | Bind verifier result to evidence and branch state. |
| `retention_hold_state` | enum | PV-07 | Distinguish expired state from legally or audit-held state. |
| `validation_start_time` | timestamp | all gates | Measure gate latency. |
| `validation_end_time` | timestamp | all gates | Measure gate latency. |
| `validation_decision` | enum | all gates | Record allow, reject, recompute, downgrade, preserve, or expire. |
| `validation_gate_ids` | repeated enum | all gates | Attribute overhead to PV-01 through PV-08. |
| `validation_lookup_count` | integer | all gates | Distinguish local CPU from remote metadata dependency. |
| `validation_queue_wait` | duration | all gates | Capture saturation of validation service. |

## Negative Tests

The measurement harness must include negative fixtures before any overhead result is trusted:

| Fixture | Required result |
|---|---|
| missing `provenance_id` on retrieved context or tool output | block or recompute |
| `source_version` mismatch with `invalidation_signal=source_changed` | revalidate or recompute |
| cache-salt mismatch across tenant/cache domains | forbid reuse |
| actor outside `replay_authorization_scope` | reject replay or downgrade |
| missing or mismatched `verifier_evidence_hash` | reject verifier-state reuse |
| expired `durability_horizon` with no `retention_hold_state` | reject or expire |
| summary-plus-pointer with missing exact recovery pointer | retain exact state or recompute |
| branch merge with inconsistent lineage | reject replay |

Unsafe-pass rate must be zero in these fixtures. If unsafe-pass rate is nonzero, the measurement has failed before cost is relevant.

## Expected Output Contract For Parent Harness

This branch should feed the parent M-EXP-1 harness with rows equivalent to:

| Table | Rows this branch contributes |
|---|---|
| `data/measurement_experiment_specs.csv` | EXP-PROV-MICRO-001 through EXP-PROV-POINTER-007 |
| `data/measurement_required_fields.csv` | PV gate fields plus trace-v3 validation timing fields |
| `data/measurement_thresholds.csv` | Option B provenance-overhead threshold; Option C lineage/authorization/verifier/retention threshold |
| `data/measurement_claim_update_matrix.csv` | CL-002, CL-003, CL-006, CL-007, CL-009, CL-010, CL-011 update rows |
| `data/measurement_synthetic_probe_results.csv` | synthetic placeholder sensitivity runs with explicit `measurement_design` or `simulated_probe` label |

## Claim Update Map

| Claim | Measurement that can update it | Support signal | Falsification signal |
|---|---|---|---|
| CL-002 | EXP-PROV-MICRO-001, EXP-PROV-ISOLATION-003 | RAG validation overhead below retained-value margin | safe object reuse consistently negative after provenance/freshness/isolation cost |
| CL-003 | EXP-PROV-REPLAY-002, EXP-PROV-LINEAGE-004, EXP-PROV-VERIFIER-005 | Option C replay validation overhead below branch/verifier/durable retained-value margin | lineage/authorization/verifier overhead collapses C to B/A |
| CL-006 | EXP-PROV-POINTER-007 | pointer-preserving compression validates exact recovery cheaply | unsafe pointer accepted or validation overhead erases savings |
| CL-007 | EXP-PROV-POINTER-007 | measured reconstruction/metadata/provenance costs are low enough for positive queue or capacity effect | provenance overhead preserves current no-queue-help conclusion |
| CL-009 | all experiments | unsafe reuse rejected before value is counted | any missing provenance, stale, cross-tenant, unauthorized, tampered, or retention-invalid reuse passes |
| CL-010 | EXP-PROV-ISOLATION-003, EXP-PROV-LINEAGE-004, EXP-PROV-VERIFIER-005, EXP-PROV-RETENTION-006 | trace-v3 fields enforce all required security gates | trace v2 alone is insufficient, preserving current claim |
| CL-011 | EXP-PROV-REPLAY-002 | coarsest boundary remains valid after measured overheads | fine-grained state wins despite absent or invalid causal variables |

## Special-Point Checks

| Special point | Evaluation |
|---|---|
| No reuse attempts | Validation overhead should be zero except background registry maintenance; Option B/C cannot be justified by reuse. |
| Missing provenance pointer | AuthorizedReuse is false; retained value is nonpositive regardless of low overhead. |
| Stale source version | AuthorizedReuse is false until revalidated or recomputed. |
| Cache-salt mismatch | Cross-boundary reuse is forbidden even if byte savings are high. |
| Unauthorized actor | Replay value is nonpositive; Option C must downgrade or reject. |
| Missing verifier hash | Verifier-state reuse is invalid; rerun verifier or downgrade. |
| Expired retention horizon without hold | Durable replay is invalid; retaining the object is a policy violation. |
| Validation overhead equals zero | Optimistic upper bound; if Option B/C still lose, DC-006 is not the binding cause. |
| Validation overhead exceeds retained value | Option B/C collapse by definition; richer memory boundary is not justified under measured conditions. |
| Infinite validation queue wait | Safe reuse is unavailable on the critical path; recompute, exact local retention, or Option A/B downgrade dominates. |

## Pitfalls

1. Do not combine DC-006 with semantic correctness. Semantic false positives are DC-004; this branch measures the overhead of validating provenance, freshness, isolation, lineage, replay authorization, verifier evidence, and retention.
2. Do not report only average latency. p95/p99 and queue wait are required because validation can become the hot path that reverses architecture choice.
3. Do not count retained value when any required gate is missing. A fast unsafe path is not a memory-centric win.
4. Do not treat synthetic security-adjusted values as measured constants. They are scaffolding for threshold wiring.
5. Do not benchmark valid-only traces. Invalid fixtures are mandatory because correctness is a gate before economics.

## Done Criteria

This branch is sufficient when the parent harness can use it to generate:

- experiment specs for PV-01 through PV-08;
- required trace-v3 field rows for validation timing and missing M-SEC-1 security fields;
- Option B and Option C collapse-threshold rows;
- negative fixtures with zero allowed unsafe pass rate;
- claim-update rows for CL-002, CL-003, CL-006, CL-007, CL-009, CL-010, and CL-011;
- a clear distinction between `measurement_design`, `simulated_probe`, and future `measured` evidence.

