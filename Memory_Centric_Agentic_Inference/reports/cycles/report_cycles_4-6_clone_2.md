---
title: "Memory-Centric Agentic Inference — cycles 4-6 clone 2"
date: "2026-05-11"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 4-6 clone 2

## Abstract

Cycles 4-6 did not produce a new clone-2 artifact. They confirmed that the existing clone-2 deliverable, `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`, remains stable, validated, and ready for parent `M-EXP-1` integration.

The branch objective was to design the semantic-cache and durable-state risk measurement branch for two deferred constants:

- `DC-004`: semantic-cache correctness, invalidation, recovery, poisoning, and safe reuse risk.
- `DC-003`: durable object-store replay latency, tail behavior, pointer validity, retention, and replay-failure risk.

Across all three cycles, researchers, workers, and auditors converged on the same decision: clone 2 should not be reopened unless parent integration exposes a concrete contradiction. The remaining issue is not in the clone-2 plan. It is parent-scope registration and ingestion work: the parent measurement CSVs must ingest the clone-2 `CDR-*` experiment rows and `T-*` threshold rows, and `promise_check` orphan warnings must be resolved or explicitly documented before full parent `M-EXP-1` validation.

## Introduction

The root project investigates whether agentic LLM infrastructure should be designed around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier synthesis work defined architecture options in which memory reuse becomes progressively more central:

- **Option A**: conventional request/model/KV-centric serving.
- **Option B**: a memory-object-aware runtime that tracks reusable objects such as retrieved context, semantic cache entries, prefix cache entries, tool outputs, provenance pointers, and invalidation state.
- **Option C**: a trajectory/DAG-aware memory fabric that treats branch state, verifier state, durable workspace state, replay dependencies, and multi-agent state as first-class scheduling and placement inputs.

Clone 2 addresses a specific risk in that architecture decision. Semantic caches and prefix caches can reduce recomputation, but raw hit rate is not enough evidence for Option B because hits can be stale, poisoned, tenant-invalid, false-positive, or too expensive to validate and recover. Public prefix-cache and semantic-cache mechanisms provide background for why reuse can matter, but clone 2 keeps correctness and invalidation cost as a measured deferred constant rather than assuming a benefit [12], [13].

Durable state can also reduce recomputation by preserving workspaces, checkpoints, trajectory logs, verifier state, and tool outputs. For Option C, however, durable replay is useful only if replay tails, dependency fan-in, pointer reconstruction, consistency waits, and retention rules do not erase retained value. Storage references such as NVMe specifications provide context for durable tiers, but the relevant agentic quantity is the p50/p95/p99 replay distribution on dependency-critical paths, not generic storage capability [6].

## Methodology

This report consolidates clone-2 cycles 4-6. It reports completed work and accepted audit outcomes; it does not re-audit the artifact.

The source material used for this report was:

| Cycle | Role | Session ID | Date | What it contains |
|---:|---|---|---|---|
| 4 | researcher | `627afafc-b87d-40e0-9f29-9d0acdebc724` | 2026-05-11 | States clone 2 is complete and stable; directs parent `M-EXP-1` ingestion. |
| 4 | worker | `5a80dec7-6ab4-4a5b-bf3f-12bd2fa6e82c` | 2026-05-11 | Performs no edits; confirms clone 2 is stable input to parent integration. |
| 4 | auditor | `da403b2f-f8a0-4fce-90f6-0e2524efa436` | 2026-05-11 | Validates the 308-line artifact; records parent-scope orphan warnings. |
| 5 | researcher | `7ddc59f7-954d-4736-af18-301c7939c048` | 2026-05-11 | Repeats that clone 2 should not be reopened; identifies CSV ingestion as next work. |
| 5 | worker | `86c209c0-8de5-4519-8066-12578818bc2c` | 2026-05-11 | Performs no edits; restates required experiments, thresholds, and boundaries. |
| 5 | auditor | `a796fdaa-9e26-4160-9c8a-f77bd4d10259` | 2026-05-11 | Validates artifact content; keeps only parent/root artifact registration as warning. |
| 6 | researcher | `d6a27062-9da0-4343-86d5-147fbe8f6af6` | 2026-05-11 | Defines parent integration sufficiency criteria for clone-2 coverage. |
| 6 | worker | `4ce98b80-0dd8-4892-b579-4102f4761967` | 2026-05-11 | Performs no edits; confirms branch is exhausted as a standalone clone. |
| 6 | auditor | `ff3820ab-d9ab-4431-8207-c6c23adf1f04` | 2026-05-11 | Final supplied validation: clone 2 sufficient; parent integration incomplete. |

The reporting pass also used the current artifact, `REFERENCES.md`, `MANIFEST.md`, the prior cycles 1-3 clone-2 report, and current validation command outputs.

## Results

### Cycle 4: Stable Handoff to Parent Integration

Cycle 4 established that clone 2 had moved from design work into handoff status. The researcher session `627afafc-b87d-40e0-9f29-9d0acdebc724` stated that the validated artifact remained `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` at 308 lines and that no further clone-2 design work was needed.

The worker session `5a80dec7-6ab4-4a5b-bf3f-12bd2fa6e82c` made no file changes and ran no commands. This was reported as intentional because the branch had already been validated. The worker preserved the required handoff set:

- 11 CDR experiments: `CDR-SEM-001` through `CDR-SEM-006`, and `CDR-DUR-001` through `CDR-DUR-005`.
- 10 downgrade thresholds: `T-SEM-VALID-001` through `T-SEM-RECOVERY-005`, and `T-DUR-TAIL-001` through `T-DUR-RETENTION-005`.
- `DC-004` as semantic-cache correctness, stale/poisoned hit, invalidation, recovery, tenant/cache-salt, and valid-hit retained-value risk.
- `DC-003` as durable object-store p50/p95/p99 replay-tail, dependency fan-in, pointer validity, retention, and replay-failure risk.

The auditor session `da403b2f-f8a0-4fce-90f6-0e2524efa436` validated the artifact and recorded no clone-scoped defect. It identified one moderate parent-scope warning: `promise_check` exits successfully but reports orphan artifacts, including parent measurement CSVs and sibling/report artifacts. The audit decision was **VALIDATED**.

### Cycle 5: No Reopen, Preserve Mechanism Boundary

Cycle 5 repeated the same branch state with sharper integration guidance. The researcher session `7ddc59f7-954d-4736-af18-301c7939c048` said the next useful work was parent `M-EXP-1` CSV ingestion plus ledger/orphan-warning handling. It emphasized that parent ingestion must preserve the mechanism distinction:

- Option B evidence is safe valid semantic retained value, not raw semantic hit rate.
- Option C evidence is tail-safe durable replay value, not median durable latency.

The worker session `86c209c0-8de5-4519-8066-12578818bc2c` again made no changes and ran no commands. It concluded that clone 2 was exhausted as a standalone branch and should be consumed by the parent harness.

The auditor session `a796fdaa-9e26-4160-9c8a-f77bd4d10259` validated the artifact again. It confirmed that the plan still preserved:

- all 11 experiment IDs,
- all 10 threshold IDs,
- per-experiment `instrumentation_fields`,
- required safety fields such as `tenant_scope`, `cache_salt`, `pointer_valid`, and `retention_hold_state`,
- p50/p95/p99 durable replay-tail measurement,
- Option B and Option C downgrade semantics.

The only warning remained parent/root artifact registration. The audit again instructed not to rely on the absent ledger event `523f4e76-04d4-4002-8000-000000000002`.

### Cycle 6: Final Stability Confirmation

Cycle 6 treated clone 2 as converged. The researcher session `d6a27062-9da0-4343-86d5-147fbe8f6af6` stated that the active sub-topic had moved to parent `M-EXP-1` integration. It listed the parent tables that must ingest clone-2 rows:

- `data/measurement_experiment_specs.csv`,
- `data/measurement_required_fields.csv`,
- `data/measurement_thresholds.csv`,
- `data/measurement_claim_update_matrix.csv`,
- `data/measurement_synthetic_probe_results.csv`.

The worker session `4ce98b80-0dd8-4892-b579-4102f4761967` made no edits. It restated the row identities and concluded that remaining work was parent-scope: CSV ingestion, ledger registration, orphan-warning resolution or documentation, and an integrated `M-EXP-1` audit.

The auditor session `ff3820ab-d9ab-4431-8207-c6c23adf1f04`, also supplied directly as the audit report input, validated clone 2. It reported:

- critical findings: none,
- moderate findings: parent-scope orphan artifact warnings remain,
- minor findings: none,
- artifact line count: 308,
- `org_check`: green,
- decision: **VALIDATED**.

The audit concluded that reopening or editing `cache_durable_risk_measurement_plan.md` would not address the remaining issue class. The required next step is parent integration.

## Measurement Design Status

The measurement design itself did not change during cycles 4-6. The stable content is summarized here because it is the object being handed off.

### DC-004: Semantic-Cache Risk

The `DC-004` design treats semantic-cache benefit as a valid-hit retained-value problem, not a raw-hit-rate problem. A semantic-cache hit only counts as useful if it survives correctness, freshness, provenance, tenant/cache-salt, poisoning, validation, recovery, and wrong-reuse gates.

The plan’s safe semantic retained-value expression is:

```text
V_semantic_safe =
  P_hit * P_valid_given_hit * C_recompute_avoided
  - C_lookup
  - C_validation
  - C_invalidation
  - C_recovery
  - E[C_wrong_reuse]
```

Option B remains justified for retrieval-augmented generation only if this value remains positive after runtime metadata and policy overheads. Unsafe reuse is blocked or downgraded, not merely assigned a lower score.

The six semantic experiments are:

| Experiment ID | Measurement |
|---|---|
| `CDR-SEM-001` | Raw hit rate versus valid-hit rate. |
| `CDR-SEM-002` | Semantic false-positive rate by match-score bucket. |
| `CDR-SEM-003` | Stale-hit rate after `source_version` and invalidation changes. |
| `CDR-SEM-004` | Safe hit rate after `tenant_scope` and `cache_salt` enforcement. |
| `CDR-SEM-005` | Recovery latency and action after invalid cache hit. |
| `CDR-SEM-006` | Poisoning or untrusted-provenance rejection rate. |

The semantic downgrade thresholds are:

| Threshold ID | Decision |
|---|---|
| `T-SEM-VALID-001` | Disable semantic-cache retained-value credit when valid-hit value cannot pay lookup, validation, recovery, and wrong-reuse costs. |
| `T-SEM-STALE-002` | Require exact provenance or revalidation when stale-hit loss erases recompute savings. |
| `T-SEM-ISOLATION-003` | Downgrade Option B if safe hit rate collapses after tenant/cache-salt gates. |
| `T-SEM-POISON-004` | Forbid correctness-sensitive reuse when untrusted reuse rate is nonzero without trusted provenance. |
| `T-SEM-RECOVERY-005` | Treat lookup as overhead when lookup, validation, and recovery exceed exact retrieval or recompute. |

### DC-003: Durable-State Replay Risk

The `DC-003` design treats durable-state benefit as a replay-tail and dependency-path problem. Durable state supports Option C only when p50/p95/p99 replay latency, consistency wait, fan-in amplification, pointer reconstruction, retention validity, and replay-failure risk remain below retained-value margins.

The plan’s durable replay expression is:

```text
V_durable_replay =
  P_replay * C_recompute_avoided
  - L_store_read(p)
  - L_consistency(p)
  - C_pointer_validation
  - C_reconstruction
  - E[C_replay_failure]
```

The percentile `p` must include p50, p95, and p99 because long agentic workflows may block on the slowest object in a replay dependency path.

The five durable experiments are:

| Experiment ID | Measurement |
|---|---|
| `CDR-DUR-001` | Durable workspace write/read p50/p95/p99 by size and consistency mode. |
| `CDR-DUR-002` | Dependency-path max replay latency. |
| `CDR-DUR-003` | Verifier/tool-output summary-pointer recovery latency. |
| `CDR-DUR-004` | Retention-horizon and hold-state violations. |
| `CDR-DUR-005` | Replay success rate under object-store tail injection. |

The durable downgrade thresholds are:

| Threshold ID | Decision |
|---|---|
| `T-DUR-TAIL-001` | Avoid remote durable replay when p95 replay latency exceeds saved recomputation time. |
| `T-DUR-P99-002` | Downgrade Option C when max-path p99 exceeds verifier or merge deadline. |
| `T-DUR-FANIN-003` | Downgrade when fan-in tail amplification erases retained-value margin. |
| `T-DUR-RECOVERY-004` | Disable summary-plus-pointer when pointer is invalid or reconstruction is slower than recompute. |
| `T-DUR-RETENTION-005` | Forbid reuse when durability horizon has expired and no retention hold is active. |

## Integration Status

Clone 2 is complete as a branch artifact but not yet integrated into the parent `M-EXP-1` measurement harness.

The parent harness must ingest clone-2 rows into:

| Parent table | Required clone-2 contribution |
|---|---|
| `measurement_experiment_specs.csv` | Add `CDR-SEM-001` through `CDR-SEM-006` and `CDR-DUR-001` through `CDR-DUR-005`, each with nonempty per-experiment `instrumentation_fields`. |
| `measurement_required_fields.csv` | Add semantic-cache and durable-state fields such as `cache_key_hash`, `tenant_scope`, `cache_salt`, `correctness_label`, `durable_object_id`, `dependency_width`, `read_latency_ms`, `pointer_valid`, and `retention_hold_state`. |
| `measurement_thresholds.csv` | Add all `T-SEM-*` and `T-DUR-*` downgrade thresholds. |
| `measurement_claim_update_matrix.csv` | Preserve updates to claims including `CL-002`, `CL-003`, `CL-006`, `CL-008`, `CL-009`, and `CL-010`. |
| `measurement_synthetic_probe_results.csv` | Add synthetic probe rows for false positives, stale hits, recovery cost, durable tails, fan-in, pointer validity, and retention expiry. |

The current parent measurement CSVs in the workspace are populated for `DC-005` trajectory reuse. Clone-2 `CDR-*` rows remain parent integration input.

The parent integration must preserve deferred-constant separation:

- `DC-003`: durable replay p95/p99, fan-in, pointer, consistency, retention, and replay-failure risk.
- `DC-004`: semantic-cache correctness, stale/poisoned hits, invalidation, recovery, isolation, provenance, and valid-hit retained value.
- `DC-005`: trajectory reuse distribution, a sibling scope.
- `DC-006`: provenance-validation overhead, a sibling scope.

## Discussion

Cycles 4-6 are important because they show convergence rather than construction. The branch stopped producing edits because the artifact already satisfied the scoped objective. Each worker no-op was accepted by audit as the correct behavior: further clone-local edits would not resolve the only remaining issue, which is parent-level registration and ingestion.

The repeated audit result also clarifies the architecture signal. Clone 2 does not say that semantic caches or durable replay are always good. It defines the measurements that decide when they stop being good enough.

For Option B, semantic reuse is credited only when it remains safe and positive after validation. A high raw semantic hit rate can still force downgrade if valid-hit rate collapses, if stale or poisoned entries reach correctness-sensitive paths, if tenant/cache-salt enforcement removes most reusable entries, or if recovery cost exceeds exact retrieval.

For Option C, durable replay is credited only when replay paths remain tail-safe. Median durable latency is not enough. Wide dependency paths, high p99 reads, consistency waits, invalid pointers, slow reconstruction, expired retention, or replay failure can all erase durable retained value and force fallback to local retention, Option B object runtime, recompute, or forbidden reuse.

The main unresolved work is operational: parent `M-EXP-1` must encode this branch into the CSV harness and ledger state without flattening the mechanisms into generic cache-hit or storage-latency metrics.

## Conclusions and Recommendations

1. Clone 2 is validated and complete for cycles 4-6. The required artifact remains `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`.

2. No new clone-2 build work occurred in cycles 4-6. That was intentional and accepted by audit because the branch had converged.

3. Option B should only receive semantic-cache reuse credit when safe valid-hit retained value remains positive after correctness, freshness, provenance, tenant/cache-salt, poisoning, validation, recovery, and wrong-reuse costs.

4. Option C should only receive durable replay credit when p50/p95/p99 tails, dependency fan-in, consistency wait, pointer validity, reconstruction latency, retention state, and replay-failure risk remain below retained-value margins.

5. Unsafe reuse remains a hard downgrade or forbid condition. It is not merely a lower-quality successful reuse case.

6. Parent `M-EXP-1` should ingest all clone-2 experiments, thresholds, fields, claim updates, and synthetic probes into the measurement CSVs.

7. Parent validation should not rely on the absent ledger event `523f4e76-04d4-4002-8000-000000000002`.

8. Full parent `M-EXP-1` validation should wait until `promise_check` orphan warnings are resolved or explicitly documented with ledger evidence.

## References

[6] NVM Express, "Specifications," NVM Express, accessed 2026-05-11. https://nvmexpress.org/specifications/

[12] vLLM Project, "Automatic Prefix Caching," vLLM Documentation, accessed 2026-05-11. https://docs.vllm.ai/en/latest/design/prefix_caching/

[13] Sajal Regmi and Chetan Phakami Pun, "GPT Semantic Cache: Reducing LLM Costs and Latency via Semantic Embedding Caching," arXiv, 2024. https://arxiv.org/abs/2411.05276

## Appendix: Implementation Details

### Code and Artifact Organization

The primary clone-2 artifact is:

| File | Lines | Purpose |
|---|---:|---|
| `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` | 308 | Validated measurement design for `DC-004` semantic-cache correctness/invalidation risk and `DC-003` durable replay-tail risk. |

Sibling experiment-plan artifacts in the workspace are:

| File | Lines | Purpose |
|---|---:|---|
| `memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md` | 298 | `DC-005` trajectory-reuse measurement design. |
| `memory-centric-agentic/experiments/provenance_overhead_measurement_plan.md` | 344 | `DC-006` provenance-validation overhead measurement design. |

The parent measurement CSVs currently observed in the workspace are:

| File | Lines | Current status |
|---|---:|---|
| `data/measurement_experiment_specs.csv` | 8 | Populated for `DC-005`; clone-2 `CDR-*` rows remain integration input. |
| `data/measurement_required_fields.csv` | 14 | Populated for `DC-005`; clone-2 fields remain integration input. |
| `data/measurement_thresholds.csv` | 5 | Populated for `DC-005`; clone-2 `T-*` thresholds remain integration input. |
| `data/measurement_claim_update_matrix.csv` | 12 | Populated for `DC-005`; clone-2 claim updates remain integration input. |
| `data/measurement_synthetic_probe_results.csv` | 7 | Populated for `DC-005`; clone-2 probe rows remain integration input. |

No new figures were produced by clone 2 during cycles 4-6. Existing workspace figures are not specific to this stability pass, so none are embedded in this report.

### Workspace Snapshot

`MANIFEST.md` was updated as a current snapshot after the clone-2 stability pass. The snapshot records:

| Category | Count |
|---|---:|
| Python scripts | 23 |
| Wolfram scripts | 4 |
| Total script lines | 7,108 |
| Markdown model/synthesis files | 16 |
| Experiment-plan markdown files | 3 |
| CSV data/model files | 65 |
| Figures | 29 |
| Sub-topics completed, assessed, or designed | 15 |

The manifest cross-reference map records that `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md` should feed parent `M-EXP-1` measurement CSVs with `CDR-SEM-*`, `CDR-DUR-*`, `T-SEM-*`, and `T-DUR-*` rows while resolving or documenting parent CSV orphan warnings.

### Validation Commands

The reporter pass ran the current workspace checks after updating `MANIFEST.md`.

`org_check` passed:

```text
OK: org_check green.
```

`promise_check` exited successfully and reported 62 events and 14 plan milestones. It also reported orphan warnings for managed artifacts, including:

- `data/dc005_merge_verification_results.csv`,
- `data/measurement_claim_update_matrix.csv`,
- `data/measurement_experiment_specs.csv`,
- `data/measurement_required_fields.csv`,
- `data/measurement_synthetic_probe_results.csv`,
- `data/measurement_thresholds.csv`,
- `reports/cycles/report_cycles_1-3_clone_0.md`,
- `reports/cycles/report_cycles_1-3_clone_0.pdf`,
- `reports/cycles/report_cycles_1-3_clone_2.md`,
- `reports/cycles/report_cycles_1-3_clone_2.pdf`,
- `tests/verify_dc005_merge_ready.py`.

These warnings match the cycle 4-6 audit record: they are parent/root registration issues, not clone-2 artifact defects.

### Session Cross-Reference Map

| Report section | Source sessions |
|---|---|
| Abstract and Conclusions | `da403b2f-f8a0-4fce-90f6-0e2524efa436`, `a796fdaa-9e26-4160-9c8a-f77bd4d10259`, `ff3820ab-d9ab-4431-8207-c6c23adf1f04` |
| Cycle 4 results | `627afafc-b87d-40e0-9f29-9d0acdebc724`, `5a80dec7-6ab4-4a5b-bf3f-12bd2fa6e82c`, `da403b2f-f8a0-4fce-90f6-0e2524efa436` |
| Cycle 5 results | `7ddc59f7-954d-4736-af18-301c7939c048`, `86c209c0-8de5-4519-8066-12578818bc2c`, `a796fdaa-9e26-4160-9c8a-f77bd4d10259` |
| Cycle 6 results | `d6a27062-9da0-4343-86d5-147fbe8f6af6`, `4ce98b80-0dd8-4892-b579-4102f4761967`, `ff3820ab-d9ab-4431-8207-c6c23adf1f04` |
| Measurement design status | `memory-centric-agentic/experiments/cache_durable_risk_measurement_plan.md`; all cycle 4-6 audit sessions |
| Integration status | all cycle 4-6 researcher sessions; all cycle 4-6 auditor sessions |
| Implementation details | current workspace files, `MANIFEST.md`, `REFERENCES.md`, `org_check`, `promise_check` |

### Record Gaps

No clone-2 build records are missing for cycles 4-6. The absence of new artifact edits is itself recorded in all three worker sessions.

The only open gap is parent-scope: the parent `M-EXP-1` CSV ingestion and ledger/orphan-warning cleanup were repeatedly identified as next work, but they were not performed by clone 2 during cycles 4-6.
