---
title: "Memory-Centric Agentic Inference — cycles 1-3 clone 2"
date: "2026-05-11"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 1-3 clone 2

## Abstract

Clone 2 designed and validated the semantic-cache and durable-state risk measurement branch for `M-EXP-1`, the deferred-constant measurement harness. Its required artifact is `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`.

The branch covers two deferred constants from the parent synthesis:

- `DC-004`: semantic-cache correctness and invalidation cost.
- `DC-003`: remote durable object-store latency distributions for agent state.

The main result is a measurement design that can downgrade architecture choices instead of only reporting cache or storage performance. Option B, the memory-object-aware runtime, is preserved for retrieval-augmented generation only when semantic-cache hits remain valid after freshness, provenance, tenant/cache-salt, poisoning, validation, and recovery checks. Option C, the trajectory/DAG-aware memory fabric, is preserved only when durable replay p50/p95/p99 tails, dependency fan-in, pointer validity, consistency waits, retention state, and replay recovery remain below retained-value margins.

The branch was validated by audit. The remaining issue is explicitly parent-scope: the parent measurement CSVs exist as managed artifacts but are not yet registered cleanly in the promise ledger, and the clone-2 CDR rows still need parent `M-EXP-1` integration.

## Introduction

The root project asks whether future agentic LLM inference systems should be designed around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier parent work produced three architecture options:

- **Option A**: conventional request/model/KV-centric serving.
- **Option B**: a memory-object-aware runtime that tracks reusable objects such as retrieved context, prefix cache entries, semantic cache entries, tool outputs, provenance pointers, and invalidation state.
- **Option C**: a trajectory/DAG-aware memory fabric that treats branch state, verifier state, durable workspace state, and replay dependencies as first-class scheduling and placement inputs.

The final synthesis identified several deferred constants: quantities that could reverse architecture conclusions if measured values are unfavorable. Clone 2 focused on two of them.

`DC-004` asks whether semantic caches and related approximate reuse mechanisms actually provide safe retained value. A semantic cache stores or retrieves prior responses or objects by similarity rather than exact identity; this creates risk from false positives, stale source versions, poisoned entries, tenant isolation failures, and expensive recovery. Public work exists on prefix caching and semantic caching mechanisms, but the parent synthesis kept correctness and invalidation cost deferred rather than treating raw hit rate as sufficient evidence [12], [13].

`DC-003` asks whether durable object-store replay is fast and reliable enough for agentic state. Durable replay means reading prior workspace objects, checkpoints, tool outputs, summary-pointer state, verifier evidence, or trajectory logs so an agent can resume or merge work. The relevant quantity is not average storage bandwidth. The risk is tail latency: p95 and p99 replay delays can dominate verifier or merge paths, especially when a replay path depends on many objects. NVMe and storage-interface sources provide capability context, but the agentic replay distribution remains a deferred measurement [6].

## Methodology

This report consolidates clone-2 cycles 1-3. It reports completed work and audit outcomes; it does not re-audit the artifact.

The source sessions supplied for this report were:

| Cycle | Role | Session ID | Source content |
|---:|---|---|---|
| 1 | researcher | `9b8a5162-0640-43a8-a6b4-84b3314ff60d` | Source anomaly: this session describes sibling clone 0 trajectory-reuse output, not clone 2. It is useful only as fanout context. |
| 1 | worker | `11dd4699-c391-40a6-95cd-856c35ff8cf8` | Verified and finalized the clone-2 cache/durable risk plan, reported 291 lines, and wrote a merge report. |
| 1 | auditor | `6ec8418d-8aa6-4db0-bd58-ad4d8deb07a3` | Found and fixed one moderate integration ambiguity: missing per-experiment instrumentation mappings. Validated the patched 308-line artifact. |
| 2 | researcher | `c4395aeb-ac9e-4823-8672-1e9171033372` | Reframed clone 2 as validated parent-integration input and specified how parent CSVs should consume it. |
| 2 | worker | `7363fc26-9023-45a6-8d13-136f88480448` | Revalidated the artifact and reported a ledger event UUID later found absent. |
| 2 | auditor | `eb0ead1b-2df3-4f64-8118-881903303395` | Validated the artifact and noted the claimed ledger event was not present in `promise_ledger.jsonl`. |
| 3 | researcher | `23078c5d-affe-4b80-8b96-152cd86ecb38` | Directed that clone 2 should not be reopened; parent integration is the next action. |
| 3 | worker | `83b41bdd-a464-4283-971e-adb529fe1abd` | Performed no new build work and preserved the validated branch as parent-integration input. |
| 3 | auditor | `04dd614a-8fdf-4b00-8ed3-1aa6c89e7026` | Validated that all experiment IDs, thresholds, and required markers remain present; documented parent CSV orphan warnings. |

The reporting pass also used the branch artifact, the supplied audit report, `REFERENCES.md`, `MANIFEST.md`, `promise_ledger.jsonl`, and the current parent measurement CSVs.

## Results

### Cycle 1: Measurement Plan and Audit Patch

Cycle 1 produced the required clone-2 artifact:

`memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`

The worker session `11dd4699-c391-40a6-95cd-856c35ff8cf8` reported that the plan covered:

- semantic false positives,
- stale or poisoned semantic-cache hits,
- invalidation and recovery cost,
- durable object-store replay tails,
- p50/p95/p99 durable latency,
- Option B downgrade logic,
- Option C downgrade logic,
- experiment IDs and threshold IDs.

The cycle 1 audit session `6ec8418d-8aa6-4db0-bd58-ad4d8deb07a3` found one moderate defect and fixed it. The defect was not a missing concept; it was an integration ambiguity. The plan listed branch-level instrumentation fields, but it did not map required `instrumentation_fields` per experiment row even though the parent harness schema requires that field in `measurement_experiment_specs.csv`.

The auditor added a per-experiment instrumentation map for all eleven experiments:

- `CDR-SEM-001` through `CDR-SEM-006`,
- `CDR-DUR-001` through `CDR-DUR-005`.

After the patch, the artifact was 308 lines. The audit reported:

- critical issues: none,
- moderate issues: one found and fixed,
- minor issues: none,
- `promise_check`: green,
- `org_check`: green,
- decision: validated.

### Cycle 2: Parent Integration Framing and Ledger Warning

Cycle 2 shifted the branch from design work to parent integration readiness. The researcher session `c4395aeb-ac9e-4823-8672-1e9171033372` stated that the clone-2 plan should feed five parent harness tables:

- `data/measurement_experiment_specs.csv`,
- `data/measurement_required_fields.csv`,
- `data/measurement_thresholds.csv`,
- `data/measurement_claim_update_matrix.csv`,
- `data/measurement_synthetic_probe_results.csv`.

The worker session `7363fc26-9023-45a6-8d13-136f88480448` revalidated the artifact and reported a ledger event UUID:

`523f4e76-04d4-4002-8000-000000000002`

The cycle 2 audit session `eb0ead1b-2df3-4f64-8118-881903303395` found that this UUID was absent from `promise_ledger.jsonl`. The auditor did not append a replacement event because clone 2 validates a branch design, not the full parent `M-EXP-1` milestone. The audit classified the issue as moderate audit-trail inconsistency, not an artifact defect.

The audit validated the branch content and confirmed:

- all 11 expected experiment IDs are present,
- all 10 expected threshold IDs are present,
- semantic correctness and durable replay risks remain separate,
- parent integration readiness is met for this branch,
- the absent ledger event should not be relied on downstream.

### Cycle 3: Stability Check and Parent-Scope Warning

Cycle 3 made no new design changes. The researcher session `23078c5d-affe-4b80-8b96-152cd86ecb38` explicitly instructed that clone 2 should be treated as validated parent-integration input, not reopened.

The worker session `83b41bdd-a464-4283-971e-adb529fe1abd` therefore performed no additional build work. It preserved the existing artifact and restated the validated contents:

- 11 experiment specs,
- 10 downgrade thresholds,
- DC-004 coverage for semantic false positives, stale/poisoned hits, invalidation, recovery, tenant/cache-salt safety, and valid-hit retained value,
- DC-003 coverage for durable replay p50/p95/p99 tails, dependency fan-in, pointer validity, retention gates, and replay-failure risk.

The final audit session `04dd614a-8fdf-4b00-8ed3-1aa6c89e7026` validated the stable artifact. It also reported a parent-scope warning: `promise_check` exits successfully but reports orphan managed artifacts for the parent measurement CSVs. The warning covers:

- `data/measurement_claim_update_matrix.csv`,
- `data/measurement_experiment_specs.csv`,
- `data/measurement_required_fields.csv`,
- `data/measurement_synthetic_probe_results.csv`,
- `data/measurement_thresholds.csv`.

The audit decision remained validated because this warning is not a clone-2 artifact defect. It must be resolved or explicitly documented during parent `M-EXP-1` integration.

## Measurement Design

### DC-004: Semantic-Cache Risk

The plan’s first mechanism hypothesis is that semantic-cache benefit is gated by valid-hit rate, not raw-hit rate. A raw hit means the cache returned something similar. A valid hit means the returned object is also fresh, trusted, tenant-safe, provenance-valid, and recoverable.

The plan defines safe semantic retained value as:

```text
V_semantic_safe =
  P_hit * P_valid_given_hit * C_recompute_avoided
  - C_lookup
  - C_validation
  - C_invalidation
  - C_recovery
  - E[C_wrong_reuse]
```

Option B remains justified for RAG only if this value is positive after registry, policy, and migration overheads. The plan makes several hard-gate cases explicit:

| Condition | Decision |
|---|---|
| `P_hit = 0` | Semantic cache cannot justify Option B. |
| `P_valid_given_hit = 0` | Reuse must be disabled or exact provenance pointers required. |
| `invalidation_signal != none` | Reuse value is forced nonpositive until revalidated or recomputed. |
| `tenant_scope` or `cache_salt` mismatch | Reuse is forbidden independent of hit quality. |
| Missing `provenance_id` or stale `source_version` | Reuse is blocked or falls back to exact retrieval/recompute. |

The six semantic-cache experiments are:

| Experiment ID | Measurement |
|---|---|
| `CDR-SEM-001` | raw hit rate versus valid-hit rate |
| `CDR-SEM-002` | semantic false-positive rate by match-score bucket |
| `CDR-SEM-003` | stale-hit rate after source-version and invalidation changes |
| `CDR-SEM-004` | safe hit rate after tenant-scope and cache-salt enforcement |
| `CDR-SEM-005` | recovery latency and recovery action after invalid cache hit |
| `CDR-SEM-006` | poisoning or untrusted-provenance rejection rate |

The semantic-cache downgrade thresholds are:

| Threshold ID | Decision |
|---|---|
| `T-SEM-VALID-001` | Disable semantic-cache retained-value credit when valid-hit value cannot pay lookup, validation, recovery, and wrong-reuse costs. |
| `T-SEM-STALE-002` | Require exact provenance or revalidation when stale-hit loss erases recompute savings. |
| `T-SEM-ISOLATION-003` | Downgrade Option B if safe hit rate collapses after tenant/cache-salt gates. |
| `T-SEM-POISON-004` | Forbid correctness-sensitive reuse when untrusted reuse rate is nonzero without trusted provenance. |
| `T-SEM-RECOVERY-005` | Treat cache lookup as overhead when lookup, validation, and recovery cost exceed exact retrieval or recompute. |

### DC-003: Durable-State Replay Risk

The plan’s second mechanism hypothesis is that durable replay benefit is gated by tail latency and dependency width. Durable storage can preserve workspace, trajectory, checkpoint, tool-output, verifier, and branch state. That preservation only supports Option C if replay does not dominate the saved recomputation or coordination time.

The plan defines durable replay value as:

```text
V_durable_replay =
  P_replay * C_recompute_avoided
  - L_store_read(p)
  - L_consistency(p)
  - C_pointer_validation
  - C_reconstruction
  - E[C_replay_failure]
```

The latency percentile `p` must include at least p50, p95, and p99. This is required because agentic replay can block on the slowest object in a dependency path.

The plan makes these special cases explicit:

| Condition | Decision |
|---|---|
| `P_replay = 0` | Durable storage remains audit/logging only; it creates no retained execution value. |
| `L_store_read(p99)` is unbounded or too high | Latency-sensitive replay is invalid; use local pinning, recompute, or Option B fallback. |
| `dependency_width = 1` | Tail amplification is minimal, but p95/p99 still matter. |
| Large `dependency_width` | End-to-end replay approaches the maximum of many object reads; p99 can dominate. |
| Expired `durability_horizon` without active `retention_hold_state` | Reuse is a retention violation, not a performance optimization. |
| Missing recovery pointer | Summary-plus-pointer replay must fall back to exact retained state or recompute. |

The five durable-state experiments are:

| Experiment ID | Measurement |
|---|---|
| `CDR-DUR-001` | durable workspace write/read p50/p95/p99 by size and consistency mode |
| `CDR-DUR-002` | dependency-path max replay latency |
| `CDR-DUR-003` | verifier/tool-output summary-pointer recovery latency |
| `CDR-DUR-004` | retention-horizon and hold-state violations |
| `CDR-DUR-005` | replay success rate under object-store tail injection |

The durable-state downgrade thresholds are:

| Threshold ID | Decision |
|---|---|
| `T-DUR-TAIL-001` | Avoid remote durable replay when p95 replay latency exceeds saved recomputation time. |
| `T-DUR-P99-002` | Downgrade Option C when p99 max-path latency exceeds verifier or merge deadline. |
| `T-DUR-FANIN-003` | Downgrade when dependency fan-in tail amplification erases retained-value margin. |
| `T-DUR-RECOVERY-004` | Disable summary-plus-pointer when pointer is invalid or reconstruction is slower than recompute. |
| `T-DUR-RETENTION-005` | Forbid reuse when durability horizon has expired and no retention hold is active. |

## Integration Status

The clone-2 plan is complete as a branch artifact. It is not yet complete as parent `M-EXP-1` CSV integration.

The plan tells the parent harness to add:

- 11 experiment rows: `CDR-SEM-001` through `CDR-SEM-006`, and `CDR-DUR-001` through `CDR-DUR-005`;
- 10 threshold rows: `T-SEM-VALID-001` through `T-SEM-RECOVERY-005`, and `T-DUR-TAIL-001` through `T-DUR-RETENTION-005`;
- required fields such as `cache_key_hash`, `tenant_scope`, `cache_salt`, `semantic_match_score`, `correctness_label`, `recovery_latency_ms`, `durable_object_id`, `dependency_path_id`, `dependency_width`, `read_latency_ms`, `consistency_wait_ms`, `pointer_valid`, and `retention_hold_state`;
- claim-update mappings for `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`;
- synthetic probe rows for low/high false-positive, stale-hit, recovery-cost, durable-tail, fan-in, pointer-validity, and retention-expiry settings.

The current parent measurement CSVs in the workspace are populated for `DC-005` trajectory reuse, not yet for clone-2 `CDR-*` rows. This matches the audit guidance: clone 2 is a validated input, while parent integration remains the next meaningful target.

## Discussion

Clone 2 narrows the meaning of “reuse” in the memory-centric architecture. Reuse is not counted just because a cache lookup hits or a durable object can be read. Reuse counts only when it survives correctness, freshness, provenance, isolation, recovery, latency, and retention gates.

For Option B, this prevents semantic cache hit rate from becoming a misleading metric. A high raw hit rate can still downgrade to Option A if valid-hit rate is low, if false positives persist in high-score buckets, if stale entries reach correctness-sensitive paths, if tenant/cache-salt enforcement collapses safe reuse, or if recovery cost exceeds exact retrieval.

For Option C, this prevents durable storage from being treated as automatically useful. Durable state can support branch/merge replay, verifier reuse, and workspace continuation only when p95/p99 replay tails and fan-in amplification stay below retained-value margins. If pointer recovery is invalid, retention state is expired, or max-path p99 exceeds verifier or merge deadlines, durable replay should downgrade to local retention, Option B object runtime, recompute, or forbidden reuse.

The plan also keeps sibling scopes separate. `DC-003` is durable replay-tail risk. `DC-004` is semantic-cache correctness, invalidation, and recovery risk. `DC-005` trajectory reuse distribution and `DC-006` provenance-validation overhead are related, but they should not be collapsed into the same benchmark. The auditors repeatedly emphasized this boundary because collapsing the deferred constants would turn a discriminating measurement plan into a generic cache/storage test.

## Conclusions and Recommendations

Clone 2 completed its scoped objective. The validated artifact `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` gives the parent `M-EXP-1` harness a concrete design for measuring `DC-004` and `DC-003`.

The central conclusions are:

1. Option B RAG should be credited for semantic-cache reuse only when valid semantic retained value remains positive after correctness, freshness, provenance, tenant/cache-salt, poisoning, validation, recovery, and wrong-reuse costs.
2. Option C durable replay should be credited only when durable p50/p95/p99 replay tails, dependency fan-in, consistency waits, pointer reconstruction, retention validity, and replay-failure risk remain below retained-value margins.
3. Unsafe reuse is a hard block, not a cost tradeoff, for tenant/cache-salt mismatch, missing provenance in correctness-sensitive paths, stale source versions, untrusted provenance, invalid pointers, and expired retention without active hold.
4. Clone 2 should now be integrated into the parent measurement CSVs rather than reopened for further design.

The next parent action is to ingest the plan into the `M-EXP-1` CSVs while preserving the distinction between `DC-004`, `DC-003`, `DC-005`, and `DC-006`, then resolve or explicitly document the parent CSV orphan warnings before full `M-EXP-1` validation.

## References

[6] NVM Express, "Specifications," NVM Express, accessed 2026-05-11. https://nvmexpress.org/specifications/

[12] vLLM Project, "Automatic Prefix Caching," vLLM Documentation, accessed 2026-05-11. https://docs.vllm.ai/en/latest/design/prefix_caching/

[13] Sajal Regmi and Chetan Phakami Pun, "GPT Semantic Cache: Reducing LLM Costs and Latency via Semantic Embedding Caching," arXiv, 2024. https://arxiv.org/abs/2411.05276

## Appendix: Implementation Details

### Code Organization

The required clone-2 artifact is:

| File | Lines | Purpose |
|---|---:|---|
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | 308 | Measurement design for `DC-004` semantic-cache correctness/invalidation risk and `DC-003` durable replay-tail risk. |

Related sibling experiment plans are:

| File | Lines | Purpose |
|---|---:|---|
| `memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md` | 298 | Measurement design for `DC-005` trajectory reuse. |
| `memory-centric-agentic/experiments/provenance_overhead_measurement_plan.md` | 344 | Measurement design for `DC-006` provenance-validation overhead. |

The parent measurement CSVs currently present in the workspace are:

| File | Lines | Current status |
|---|---:|---|
| `data/measurement_experiment_specs.csv` | 8 | Contains `DC-005` rows; clone-2 CDR rows remain parent integration input. |
| `data/measurement_required_fields.csv` | 14 | Contains `DC-005` fields; clone-2 fields remain parent integration input. |
| `data/measurement_thresholds.csv` | 5 | Contains `DC-005` thresholds; clone-2 thresholds remain parent integration input. |
| `data/measurement_claim_update_matrix.csv` | 12 | Contains `DC-005` claim updates; clone-2 claim updates remain parent integration input. |
| `data/measurement_synthetic_probe_results.csv` | 7 | Contains `DC-005` synthetic probe rows; clone-2 probe rows remain parent integration input. |

No figures were created by clone 2. The deliverable is a markdown measurement plan.

### Test Results

The supplied audit report and session audits recorded these validation results:

| Check | Result |
|---|---|
| Required artifact exists and is nonempty | passed |
| Artifact line count | 308 |
| `CDR-SEM-001` through `CDR-SEM-006` present | passed |
| `CDR-DUR-001` through `CDR-DUR-005` present | passed |
| `T-SEM-VALID-001` through `T-SEM-RECOVERY-005` present | passed |
| `T-DUR-TAIL-001` through `T-DUR-RETENTION-005` present | passed |
| DC-003/DC-004 markers present | passed |
| valid-hit gating present | passed |
| p50/p95/p99 durable tails present | passed |
| tenant/cache-salt, pointer validity, retention state, negative tests, and claim update map present | passed |
| `org_check` | green |
| `promise_check` | exits 0 with parent-scope orphan warnings |

During this reporting pass, `MANIFEST.md` was updated to include the clone-2 experiment plan and the current parent integration status. `python3 -m long_exposure.tools.org_check <workspace>` was green. `python3 -m long_exposure.tools.promise_check <workspace>` exited successfully and reported the parent measurement CSV orphan warnings already noted by audit, plus clone-0 rendered report artifacts.

### Session References

| Cycle | Researcher | Worker | Auditor |
|---:|---|---|---|
| 1 | `9b8a5162-0640-43a8-a6b4-84b3314ff60d` | `11dd4699-c391-40a6-95cd-856c35ff8cf8` | `6ec8418d-8aa6-4db0-bd58-ad4d8deb07a3` |
| 2 | `c4395aeb-ac9e-4823-8672-1e9171033372` | `7363fc26-9023-45a6-8d13-136f88480448` | `eb0ead1b-2df3-4f64-8118-881903303395` |
| 3 | `23078c5d-affe-4b80-8b96-152cd86ecb38` | `83b41bdd-a464-4283-971e-adb529fe1abd` | `04dd614a-8fdf-4b00-8ed3-1aa6c89e7026` |

### Cross-Reference Map

| Origin | Consuming artifact | Flow |
|---|---|---|
| `data/runtime_ablation_results.csv` | `cache_durable_risk_measurement_plan.md` | Defines the Option B and Option C collapse mechanisms that the plan measures. |
| `data/security_invalid_trace_fixtures.csv` | `cache_durable_risk_measurement_plan.md` | Supplies negative-test patterns for missing provenance, tenant/cache-salt mismatch, invalid pointer, and retention failures. |
| `data/calibration_deferred_constants.csv` | `cache_durable_risk_measurement_plan.md` | Provides `DC-003` and `DC-004` as deferred constants to turn into measurement designs. |
| `cache_durable_risk_measurement_plan.md` | parent `measurement_experiment_specs.csv` | Should add `CDR-SEM-*` and `CDR-DUR-*` experiment rows with per-experiment `instrumentation_fields`. |
| `cache_durable_risk_measurement_plan.md` | parent `measurement_required_fields.csv` | Should add semantic-cache and durable-state required fields. |
| `cache_durable_risk_measurement_plan.md` | parent `measurement_thresholds.csv` | Should add `T-SEM-*` and `T-DUR-*` downgrade thresholds. |
| `cache_durable_risk_measurement_plan.md` | parent `measurement_claim_update_matrix.csv` | Should update claims `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`. |
| `cache_durable_risk_measurement_plan.md` | parent `measurement_synthetic_probe_results.csv` | Should add synthetic probes for valid-hit collapse, stale/poisoned hits, recovery cost, durable tails, fan-in, pointer validity, and retention expiry. |
