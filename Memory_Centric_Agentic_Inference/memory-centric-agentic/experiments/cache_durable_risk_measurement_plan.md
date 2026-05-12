---
created: 2026-05-11T18:55:00Z
cycle: 15
run_id: run-2026-05-11T121649Z
agent: researcher-clone-2
milestone: M-EXP-1
branch: cache-durable-risk
scope: DC-004 semantic-cache correctness and invalidation cost; DC-003 durable object-store latency distributions
claim_status: measurement_design
---

# Cache and Durable-State Risk Measurement Plan

## Purpose

This branch defines how to measure two deferred constants that can overturn the synthesized memory-centric architecture rule:

| Deferred constant | Quantity | Architecture risk |
|---|---|---|
| `DC-004` | Semantic-cache correctness and invalidation cost | Option B for RAG is valid only if approximate object reuse survives freshness, provenance, tenant/cache-salt, poisoning, false-positive, and recovery checks. |
| `DC-003` | Remote object-store latency distributions for agent state | Option C durable replay is valid only if workspace, checkpoint, summary-pointer, and trajectory replay paths avoid tail-latency costs that exceed retained value. |

The goal is not to prove that semantic caches or durable replay are useful. The goal is to make the measurement discriminating: a result should either preserve Option B/C under explicit thresholds or force a downgrade to Option A/B.

## Mechanism Hypotheses

### H1: Semantic-cache benefit is gated by valid-hit rate, not raw-hit rate

Raw semantic-cache hit rate is insufficient because a hit can be semantically false-positive, stale, poisoned, tenant-invalid, or unrecoverable. The measurable retained value of a semantic-cache entry is:

`V_semantic_safe = P_hit * P_valid_given_hit * C_recompute_avoided - C_lookup - C_validation - C_invalidation - C_recovery - E[C_wrong_reuse]`

Option B remains justified for RAG only if `V_semantic_safe > Q_registry + Q_policy + Q_migration` and all security gates pass. Option B should be downgraded to Option A if valid-hit value is nonpositive after validation and recovery costs.

Special points:

| Point | Evaluation |
|---|---|
| `P_hit = 0` | `V_semantic_safe <= 0`; semantic cache cannot justify Option B. |
| `P_valid_given_hit = 0` | All hits are unsafe; reuse must be disabled or exact provenance pointers required. |
| `C_validation = 0` | Optimistic upper bound; if Option B fails here, it cannot pass with real validation. |
| `invalidation_signal != none` | Reuse value is forced nonpositive until revalidated or recomputed. |
| `cache_salt` or `tenant_scope` mismatch | Reuse is forbidden independent of hit quality. |
| missing `provenance_id` or stale `source_version` | Reuse is blocked or must fall back to exact retrieval/recompute. |

### H2: Durable replay benefit is gated by tail latency and dependency width

Durable workspace and trajectory-state replay are useful only when replay latency does not dominate saved recomputation or coordination time. The measurable durable replay value is:

`V_durable_replay = P_replay * C_recompute_avoided - L_store_read(p) - L_consistency(p) - C_pointer_validation - C_reconstruction - E[C_replay_failure]`

where `p` must include at least p50, p95, and p99 because long agent workflows can be blocked by the slowest required replay object. Option C should be downgraded to Option B or local-only retention if `max_path_latency_p95_or_p99 >= retained_value_time_equivalent` for dependency-critical replay paths.

Special points:

| Point | Evaluation |
|---|---|
| `P_replay = 0` | Durable replay creates no retained value; durable storage remains audit/logging only. |
| `L_store_read(p99) -> infinity` | Latency-sensitive replay is invalid; local pinning, recompute, or Option B fallback is required. |
| `dependency_width = 1` | Tail amplification is minimal; p95/p99 still matter but no fan-in max effect. |
| large `dependency_width` | Effective replay latency approaches the maximum of many object reads; p99 can dominate end-to-end replay. |
| expired `durability_horizon` without `retention_hold_state` | Reuse is a retention violation, not a performance optimization. |
| missing recovery pointer | Summary-plus-pointer replay must fall back to exact retained state or recompute. |

## Required Instrumentation

### Semantic-cache events

Extend trace v2 with production-grade fields for semantic-cache and prefix-cache reuse:

| Field | Required for | Reason |
|---|---|---|
| `cache_key_hash` | lookup and insert | Joins hit, validation, invalidation, and recovery events without raw content. |
| `tenant_scope` | lookup, insert, access | Blocks cross-tenant reuse. |
| `cache_salt` | lookup, insert, access | Distinguishes trust/cache domains; required by M-SEC-1. |
| `provenance_id` | lookup, insert, access | Required for exact source recovery or validation. |
| `source_version` | lookup, insert, access | Detects stale reuse. |
| `invalidation_signal` | lookup and access | Detects TTL expiry, source change, confidence revocation, or poisoning flag. |
| `semantic_match_score` | lookup | Separates raw hit from approximate match strength. |
| `correctness_label` | offline adjudication or production shadow check | Measures semantic false positives and unsafe hits. |
| `recovery_action` | invalid hit or miss | `reuse`, `revalidate`, `retrieve_exact`, `recompute`, `block`. |
| `recovery_latency_ms` | invalid hit or recovery | Converts invalidation into cost. |
| `wrong_reuse_severity` | adjudicated unsafe hit | Converts wrong reuse into loss-cost proxy. |

### Durable-state events

Extend durable workspace, summary-pointer, and replay traces:

| Field | Required for | Reason |
|---|---|---|
| `durable_object_id` | write/read/replay | Joins durable writes to replay attempts. |
| `object_class` | all durable events | Distinguishes workspace, trajectory log, tool output, verifier state, branch state. |
| `size_bytes` | write/read/replay | Measures latency by object size. |
| `consistency_mode` | write/read/replay | Separates eventual, read-after-write, quorum, transactional, or snapshot modes. |
| `storage_tier` | write/read/replay | Distinguishes local NVMe, remote object store, pooled memory, or workspace service. |
| `dependency_path_id` | replay | Groups objects needed by the same replay path. |
| `dependency_width` | replay | Supports max-tail amplification estimates. |
| `write_latency_ms` | workspace write/checkpoint | Measures checkpoint overhead. |
| `read_latency_ms` | replay | Measures p50/p95/p99 replay tails. |
| `consistency_wait_ms` | replay | Captures waiting for freshness/visibility. |
| `reconstruction_latency_ms` | summary-pointer replay | Captures exact recovery cost. |
| `pointer_valid` | summary-pointer replay | Blocks unsafe summary-only replay. |
| `retention_hold_state` | durable objects | Required to distinguish legal/audit hold from expired retention. |
| `durability_horizon` | durable objects | Detects retention overrun. |

## Experiment Specs

| Experiment ID | Deferred constant | Workload | Measured quantity | Supports if | Falsifies/downgrades if |
|---|---|---|---|---|---|
| `CDR-SEM-001` | DC-004 | RAG | raw hit rate vs valid-hit rate | `P_valid_given_hit` remains high after source, tenant, salt, and provenance checks | raw hit rate is high but valid-hit rate is low; Option B value becomes nonpositive |
| `CDR-SEM-002` | DC-004 | RAG | semantic false-positive rate by match-score bucket | false positives are concentrated in low-score buckets that can be rejected cheaply | false positives persist in high-score buckets; semantic reuse requires exact retrieval |
| `CDR-SEM-003` | DC-004 | RAG | stale-hit rate after `source_version` and invalidation changes | invalidation catches most stale entries before reuse | stale reuse reaches correctness-sensitive paths; downgrade to exact provenance pointer |
| `CDR-SEM-004` | DC-004 | RAG / prefix-cache workloads | safe hit rate after `tenant_scope` and `cache_salt` enforcement | isolation-preserving hit rate remains positive enough to exceed metadata costs | safe reuse collapses once tenant/cache-salt checks are enforced |
| `CDR-SEM-005` | DC-004 | RAG | recovery latency and action after invalid cache hit | revalidation/retrieval/recompute cost is lower than full miss baseline often enough to preserve value | recovery cost plus lookup/validation exceeds recompute or exact retrieval |
| `CDR-SEM-006` | DC-004 | RAG | poisoning or untrusted-provenance rejection rate | untrusted entries are observable and blocked before reuse | untrusted entries can score as valid hits without new fields |
| `CDR-DUR-001` | DC-003 | code-agent loop | durable workspace write/read p50/p95/p99 by size and consistency mode | p95/p99 replay latency is below saved recomputation time | tail latency dominates replay and forces local-only retention or recompute |
| `CDR-DUR-002` | DC-003 | multi-agent branch/merge | dependency-path max replay latency | fan-in replay paths remain bounded under realistic dependency width | max path latency grows superlinearly with dependency width and blocks merge/replay |
| `CDR-DUR-003` | DC-003 | verification-heavy | verifier/tool-output summary-pointer recovery latency | pointer recovery is exact and cheaper than recompute under p95 | recovery is slow, pointer-invalid, or not exact; summary-plus-pointer must be disabled |
| `CDR-DUR-004` | DC-003 | code-agent / multi-agent | retention-horizon and hold-state violations | expired objects are blocked or held with explicit retention state | expired durable objects are reused or retained without hold state |
| `CDR-DUR-005` | DC-003 | all Option C workloads | replay success rate under object-store tail injection | Option C survives measured p95/p99 tails | Option C collapses to B/A when tails are injected into runtime replay |

### Per-experiment instrumentation map

The parent harness should populate `measurement_experiment_specs.csv.instrumentation_fields` with these minimum field sets:

| Experiment ID | Minimum instrumentation fields |
|---|---|
| `CDR-SEM-001` | `cache_key_hash; tenant_scope; cache_salt; provenance_id; source_version; invalidation_signal; semantic_match_score; correctness_label; recovery_action; recovery_latency_ms; wrong_reuse_severity` |
| `CDR-SEM-002` | `cache_key_hash; semantic_match_score; correctness_label; provenance_id; source_version; invalidation_signal; wrong_reuse_severity` |
| `CDR-SEM-003` | `cache_key_hash; provenance_id; source_version; invalidation_signal; correctness_label; recovery_action; recovery_latency_ms` |
| `CDR-SEM-004` | `cache_key_hash; tenant_scope; cache_salt; semantic_match_score; correctness_label; recovery_action; recovery_latency_ms` |
| `CDR-SEM-005` | `cache_key_hash; provenance_id; source_version; invalidation_signal; recovery_action; recovery_latency_ms; correctness_label; recompute_cost_hint` |
| `CDR-SEM-006` | `cache_key_hash; provenance_id; source_version; invalidation_signal; semantic_match_score; correctness_label; wrong_reuse_severity; recovery_action` |
| `CDR-DUR-001` | `durable_object_id; object_class; size_bytes; consistency_mode; storage_tier; write_latency_ms; read_latency_ms; consistency_wait_ms; recompute_cost_hint` |
| `CDR-DUR-002` | `durable_object_id; object_class; dependency_path_id; dependency_width; read_latency_ms; consistency_wait_ms; trajectory_node_id; branch_id; merge_state` |
| `CDR-DUR-003` | `durable_object_id; object_class; pointer_valid; provenance_id; source_version; reconstruction_latency_ms; read_latency_ms; verifier_id; recompute_cost_hint` |
| `CDR-DUR-004` | `durable_object_id; object_class; durability_horizon; retention_hold_state; read_latency_ms; write_latency_ms; recovery_action` |
| `CDR-DUR-005` | `durable_object_id; object_class; storage_tier; dependency_path_id; dependency_width; read_latency_ms; consistency_wait_ms; reconstruction_latency_ms; pointer_valid; durability_horizon; retention_hold_state` |

## Metrics and Thresholds

### Semantic-cache downgrade thresholds

| Threshold ID | Boundary expression | Decision |
|---|---|---|
| `T-SEM-VALID-001` | `P_hit * P_valid_given_hit * C_recompute_avoided <= C_lookup + C_validation + C_recovery + E[C_wrong_reuse]` | Disable semantic-cache retained-value credit; downgrade RAG Option B to exact retrieval/runtime baseline. |
| `T-SEM-STALE-002` | `stale_hit_rate * C_wrong_reuse >= C_recompute_avoided - C_validation` | Require exact provenance pointer or force revalidation before reuse. |
| `T-SEM-ISOLATION-003` | `safe_hit_rate_after_tenant_salt <= Q_registry_plus_policy / C_recompute_avoided` | Option B cannot be justified by semantic/prefix reuse after isolation gates. |
| `T-SEM-POISON-004` | `untrusted_reuse_rate > 0` for correctness-sensitive entries lacking trusted provenance | Forbid reuse; count value as nonpositive until provenance instrumentation exists. |
| `T-SEM-RECOVERY-005` | `C_lookup + C_validation + C_recovery >= C_exact_retrieval_or_recompute` | Treat cache lookup as latency overhead rather than retained value. |

### Durable-state downgrade thresholds

| Threshold ID | Boundary expression | Decision |
|---|---|---|
| `T-DUR-TAIL-001` | `L_replay_p95 >= C_recompute_avoided_time_equiv` | Do not use remote durable replay for latency-sensitive path; pin locally or recompute. |
| `T-DUR-P99-002` | `max_path_latency_p99 >= verifier_or_merge_deadline` | Downgrade Option C trajectory replay to Option B object runtime or local checkpointing. |
| `T-DUR-FANIN-003` | `E[max(L_1..L_n)] - median(L) >= retained_value_margin` | Dependency fan-in tail amplification erases durable replay benefit. |
| `T-DUR-RECOVERY-004` | `pointer_valid = false OR reconstruction_latency_p95 >= recompute_latency_p95` | Disable summary-plus-pointer for correctness-sensitive durable state. |
| `T-DUR-RETENTION-005` | `durability_horizon_expired AND retention_hold_state != active` | Reuse forbidden independent of performance; retained value is zero. |

## Synthetic Probe Design

Use existing trace v2 and runtime-prototype outputs as scaffolding only. The probe should be explicitly labeled synthetic.

1. Select RAG events with `semantic_cache_lookup`, `semantic_cache_insert`, `retrieved context`, and `semantic cache entry`.
2. Inject parameterized rates for:
   - semantic false positive
   - stale source version
   - invalidation detection
   - tenant/cache-salt block
   - recovery latency
   - wrong-reuse loss proxy
3. Recompute `V_semantic_safe` and compare it with the RAG Option B margin from the synthesis decision matrix.
4. Select Option C durable objects: `durable workspace`, `trajectory log`, `tool output`, `verifier state`, and `branch state`.
5. Inject p50/p95/p99 latency distributions by object size, consistency mode, and dependency path width.
6. Recompute replay path latency and compare it with recompute latency proxies and merge/verifier deadlines.
7. Emit one row per synthetic setting:
   `probe_id, deferred_constant, workload_class, synthetic_setting, threshold_id, decision_before, decision_after, reason`.

Expected synthetic outcomes:

| Probe setting | Expected result |
|---|---|
| low false-positive, low stale, cheap recovery | RAG remains Option B, still labeled synthetic. |
| high raw hit but low valid-hit | RAG downgrades from Option B toward exact retrieval or Option A baseline. |
| low durable p95/p99, narrow dependency path | Option C durable replay remains plausible. |
| high p99 or wide dependency fan-in | Option C downgrades to local-only retention, Option B object runtime, or recompute. |
| expired retention without hold state | Reuse is forbidden even if latency is low. |

## Claim Update Map

| Claim | Current risk | Measurement update |
|---|---|---|
| `CL-002` RAG Option B if semantic/prefix reuse survives checks | Medium; semantic correctness and invalidation uncalibrated | DC-004 measurements determine whether RAG remains Option B or downgrades to exact retrieval/Option A under real validation and recovery costs. |
| `CL-003` Option C when durable/branch/verifier state creates retained value | High; durable latency tails and trajectory reuse uncalibrated | DC-003 p95/p99 replay tails determine whether durable workspace and replay paths preserve Option C value. |
| `CL-006` Compression/offload must be representation-safe | Low conceptual risk, operationally unmeasured | Durable pointer-recovery metrics test whether summary-plus-pointer is viable for correctness-sensitive replay. |
| `CL-008` Public sources do not calibrate core agentic constants | Medium | Production/open measurements for DC-003/DC-004 convert deferred constants into calibrated rows or confirm the gap. |
| `CL-009` Security validation is architecture selection | Low conceptual risk | Cache poisoning, tenant/cache-salt, and retention-hold measurements test whether security gates are observable before value is counted. |
| `CL-010` Trace v2 is insufficient for production-grade security | Medium | If tenant/cache-salt, retention-hold, and correctness labels are required, trace v3/security-field extension is confirmed. |

## Required Output Tables for Main Harness

This branch should feed the parent `M-EXP-1` harness with rows for these tables:

### `measurement_experiment_specs.csv`

Rows to add:

- `CDR-SEM-001` through `CDR-SEM-006`
- `CDR-DUR-001` through `CDR-DUR-005`

Each row must include:

`experiment_id, deferred_constant, workload_class, measured_quantity, instrumentation_fields, metric, aggregation_window, expected_signal, supports_if, falsifies_if, updates_claim_ids, output_type`

### `measurement_required_fields.csv`

Required branch fields:

- `cache_key_hash`
- `tenant_scope`
- `cache_salt`
- `semantic_match_score`
- `correctness_label`
- `recovery_action`
- `recovery_latency_ms`
- `wrong_reuse_severity`
- `durable_object_id`
- `size_bytes`
- `consistency_mode`
- `storage_tier`
- `dependency_path_id`
- `dependency_width`
- `write_latency_ms`
- `read_latency_ms`
- `consistency_wait_ms`
- `reconstruction_latency_ms`
- `pointer_valid`
- `retention_hold_state`

Existing trace v2 fields reused:

- `object_id`
- `object_class`
- `workload_class`
- `time_step`
- `event_type`
- `provenance_id`
- `source_version`
- `invalidation_signal`
- `durability_horizon`
- `trajectory_node_id`
- `branch_id`
- `verifier_id`
- `merge_state`
- `correctness_sensitive`
- `recompute_cost_hint`
- `loss_cost_hint`

### `measurement_thresholds.csv`

Rows to add:

- `T-SEM-VALID-001`
- `T-SEM-STALE-002`
- `T-SEM-ISOLATION-003`
- `T-SEM-POISON-004`
- `T-SEM-RECOVERY-005`
- `T-DUR-TAIL-001`
- `T-DUR-P99-002`
- `T-DUR-FANIN-003`
- `T-DUR-RECOVERY-004`
- `T-DUR-RETENTION-005`

## Negative Tests

The harness should reject or downgrade these cases:

| Fixture | Expected response |
|---|---|
| Semantic-cache hit with changed `source_version` and `invalidation_signal=source_changed` | Force revalidate or recompute. |
| Semantic-cache hit with missing `provenance_id` | Block or recompute. |
| Prefix/semantic cache access with mismatched `tenant_scope` or `cache_salt` | Forbid reuse. |
| Cache entry from untrusted provenance | Block reuse and count poisoning risk. |
| Summary-plus-pointer durable replay with `pointer_valid=false` | Fall back to exact state or recompute. |
| Durable workspace replay after `durability_horizon` expired with no `retention_hold_state` | Treat as retention violation and set retained value to zero. |
| Durable replay path whose p99 exceeds verifier/merge deadline | Downgrade Option C replay path. |

## Auditor Checklist

An auditor should validate this branch by checking:

1. The plan covers both `DC-004` and `DC-003`.
2. Every experiment names a measured quantity, required instrumentation, support condition, and falsification/downgrade condition.
3. Semantic-cache experiments distinguish raw hit rate from valid-hit rate.
4. Durable-state experiments require p50, p95, and p99, not just mean latency.
5. Security gates from M-SEC-1 are treated as hard gates, not costs that can be traded away.
6. Synthetic probes are labeled as synthetic and do not claim production calibration.
7. The plan updates specific synthesis claims rather than producing isolated benchmark results.

## Open Questions for Parent Harness

1. Should `correctness_label` be produced by offline adjudication, shadow execution against exact retrieval, or production verifier feedback?
2. What unit should convert wrong semantic reuse into `C_wrong_reuse`: latency-equivalent loss, user-visible failure rate, manual remediation time, or verifier failure cost?
3. Should durable replay deadlines be workload-specific fixed thresholds or inferred from verifier/merge critical paths?
4. Can tenant/cache-salt fields be represented as opaque trust-domain identifiers without exposing tenant metadata?
5. Should semantic-cache poisoning be modeled as a security event, a correctness event, or both in the parent CSV schema?
