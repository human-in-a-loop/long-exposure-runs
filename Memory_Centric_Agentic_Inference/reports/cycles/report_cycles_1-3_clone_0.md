---
title: "Memory-Centric Agentic Inference — cycles 1-3 clone 0"
date: "2026-05-11"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Memory-Centric Agentic Inference — cycles 1-3 clone 0

## Abstract

This fanout clone designed and closed the `DC-005` production trajectory reuse measurement branch for `M-EXP-1`, the measurement harness for deferred agentic memory constants. The branch did not attempt to measure production reuse directly. Its purpose was to specify how production systems should measure trajectory-level retained value for branch state, verifier state, tool outputs, trajectory logs, and durable workspace dependencies.

Across cycles 1-3, the clone produced the required artifact, `memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md`; converted the plan into parent harness CSV rows; and then stopped further branch-local work after audit confirmed that the design was sufficient. The final audit decision was `PIVOT`, not because the DC-005 artifacts failed, but because the branch was complete and another null validation cycle would add no substantive research.

The validated result is a measurement contract for testing when Option C, a trajectory/DAG-aware memory fabric, remains justified over Option B, a memory-object-aware runtime, or Option A, conventional request/model/KV-centric serving. The contract defines required trace fields, replay events, trajectory reuse metrics, experiment specs `TRJ-001` through `TRJ-007`, and collapse thresholds from Option C to Option B or A.

## Introduction

The root research program asks whether future AI infrastructure should be designed around memory movement, placement, reuse, compression, and lifetime management rather than arithmetic throughput alone. Earlier cycles produced three architecture options:

- **Option A**: conventional serving organized around requests, models, and KV cache.
- **Option B**: a memory-object-aware runtime that tracks reusable objects such as retrieved context, tool outputs, semantic or prefix cache entries, and durable artifacts.
- **Option C**: a trajectory/DAG-aware memory fabric that also treats branch state, verifier state, trajectory logs, and durable workspace dependencies as first-class schedulable memory objects.

`DC-005` is the deferred constant for production agent trajectory reuse distributions. It matters because Option C is only justified if retained trajectory state has enough measured value to pay for the extra coordination, validation, security, and consistency costs of managing a trajectory DAG.

This clone’s scoped objective was narrow: design the production trajectory reuse measurement branch for DC-005. It focused on trajectory DAG events, branch survival, verifier-state reuse, tool-output replay, durable workspace reuse, and ablation thresholds that collapse Option C to Option B or A. It did not measure provenance-validation overhead magnitude; that remains `DC-006`.

## Methodology

The branch used the validated prior package as context rather than reopening earlier results. The key upstream context was:

- `M-CALIB-1` identified production trajectory reuse distributions as a high-priority deferred constant.
- `M-PROTO-1` showed that hiding branch, verifier, and durable fields collapses agentic workloads from Option C toward Option B in the synthetic runtime prototype.
- `M-SYNTH-1` framed Option C as sensitive to branch survival, verifier-state value, trajectory logs, durable workspace state, and DAG coordination overhead.
- `M-EXP-1` was added to the plan of record as a measurement harness for deferred constants, including DC-005.

The clone then followed a three-step sequence.

Cycle 1 created the DC-005 measurement plan and validated it. Cycle 2 integrated the validated plan into parent harness tables. Cycle 3 confirmed that no further branch-local work was justified and pivoted the research loop away from the closed clone.

## Results

### Cycle 1: Trajectory Reuse Measurement Plan

Cycle 1 produced the required artifact:

`memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md`

The plan is 298 lines and is explicitly labeled as `measurement_design`, not production evidence. It defines the mechanism under test as:

```text
Benefit_branch_verifier_durable
  > Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption
```

With security and provenance gates included, the plan defines total trajectory value as retained value from branch state, verifier state, tool replay, trajectory logs, and durable workspace dependencies, minus trajectory coordination, validation, security, preemption, and consistency costs.

The plan’s central decision rule is:

```text
Option C remains justified iff
NetTrajectoryValue > max(0, NetObjectOnlyValueDelta)
```

For narrower architecture boundaries, the plan defines:

```text
C_beats_B iff NetTrajectoryValue > 0
```

and:

```text
C_beats_A iff NetObjectReuseValue + NetTrajectoryValue > 0
```

Cycle 1 also specified special-point checks. Examples include `p_survive = 0`, `reuse_count = 0`, `max_dag_width = 0`, missing trajectory identifiers, zero durability horizon, unauthorized replay, and infinite trajectory queue cost. The important measurement rule is that missing fields make the measurement invalid, while unauthorized, stale, tampered, or retention-invalid replay contributes zero positive retained value.

The cycle 1 auditor validated the artifact with no critical, moderate, or action-requiring minor issues. The audit confirmed that the plan covered trajectory DAG events, branch survival, verifier-state reuse, tool-output replay, durable workspace reuse, production fields, event extensions, Option C collapse thresholds, and the DC-006 scope boundary.

Source sessions: researcher `cf8385c6-18b3-4900-a1ac-b5f63ec629cb`, worker `c618e995-f1b8-458d-af77-469dd98813f6`, auditor `b6a19029-4705-4dad-ac9f-1ade66f0d13d`.

### Cycle 2: Parent Harness Integration

Cycle 2 converted the validated prose plan into parent `M-EXP-1` harness rows under `data/`.

The integration produced five measurement tables:

| Artifact | DC-005 content |
|---|---|
| `data/measurement_experiment_specs.csv` | Seven experiment specs, `TRJ-001` through `TRJ-007`. |
| `data/measurement_required_fields.csv` | Thirteen required production field rows. |
| `data/measurement_thresholds.csv` | Four threshold rows. |
| `data/measurement_claim_update_matrix.csv` | Eleven claim-update routing rows. |
| `data/measurement_synthetic_probe_results.csv` | Six synthetic mechanism-probe rows. |

The seven experiment specs are:

| ID | Purpose |
|---|---|
| `TRJ-001-branch-survival` | Measure branch fork, merge, discard, promote, and later evidence-access rates. |
| `TRJ-002-verifier-reuse` | Measure verifier-state reuse across candidates, retries, regressions, and audits. |
| `TRJ-003-tool-output-replay` | Measure replay or citation of previous tool outputs versus rerunning tools. |
| `TRJ-004-durable-dependency` | Measure durable workspace artifacts used as later execution dependencies. |
| `TRJ-005-trajectory-reuse-distance` | Measure reuse-distance distributions for trajectory-scoped objects. |
| `TRJ-006-field-ablation-replay` | Replay production or open traces through the runtime with DC-005 fields hidden. |
| `TRJ-007-control-negative` | Confirm controls do not create false-positive Option C trajectory reuse. |

The required fields include trajectory identity and ordering, object accounting, DAG attribution, replay/source edges, branch and merge state, verifier IDs, durability horizons, reuse distances, correctness and recompute hints, provenance and invalidation fields, actor authorization scope, verifier evidence hashes, and retention hold state.

The threshold table includes:

- `C_to_B_trajectory_reuse`
- `C_to_A_trajectory_reuse`
- `p_survive_min`
- `p_verifier_reuse_min`

The cycle 2 audit validated the integration. It confirmed that the CSV rows preserved trajectory-only semantics, kept authorization and provenance as validity gates, left provenance-overhead magnitude to DC-006, and represented missing or unauthorized replay as invalid or zero positive retained value. The only caveat was a fanout ledger-isolation warning: root `promise_check` reported the five measurement CSVs as orphan artifacts until clone shadow-ledger events are merged.

Source sessions: researcher `585db8a8-8f49-4e57-947d-dd507e22a057`, worker `c95f11da-48b1-4349-8e59-ac60186d830a`, auditor `3a63ae55-2b86-475c-9222-ff8800cf6109`.

### Cycle 3: Closure and Pivot

Cycle 3 did not build new artifacts. The researcher determined that DC-005 was complete for this clone and should not be reopened unless conductor merge revealed a concrete schema conflict.

The worker issued a no-build closure memo. The final auditor confirmed that:

- `memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md` still existed and was 298 lines.
- The clone merge report existed.
- `data/measurement_experiment_specs.csv` contained exactly seven specs, `TRJ-001` through `TRJ-007`.
- `data/measurement_thresholds.csv` contained the four required collapse and minimum-reuse thresholds.
- Required fields included `trajectory_node_id`, `replay_authorization_scope`, `verifier_evidence_hash`, and `retention_hold_state`.
- Invalid or unauthorized replay still contributed zero positive retained value.
- `DC-006` appeared only as ownership context for provenance/authorization overhead, not as a DC-005 measurement row.

The final decision was `PIVOT`. The rationale was that the DC-005 branch artifacts remained sufficient, but the cycle produced only a closure memo rather than new substantive research. Under the no-null-cycle rule, the correct action was to preserve the validated DC-005 results and move to conductor merge or sibling/parent `M-EXP-1` work.

Source sessions: researcher `1787ae9e-0f95-4c15-841d-24c927eaa959`, worker `09a25362-0bdb-4dc6-82a7-375f26fec1ff`, auditor `2015a875-fdee-4dad-b50c-dc2b8ea891e3`.

## Findings

The main finding is that DC-005 now has a concrete measurement design rather than a vague deferred-risk label. A production trace can test Option C by measuring whether branch, verifier, tool-output, trajectory-log, and durable-workspace reuse create retained value above trajectory-specific overheads.

The second finding is that the measurement must distinguish replay from ordinary access. The plan requires explicit replay events or equivalent `object_access` extensions with replay outcomes. If a production system cannot distinguish trajectory replay from ordinary reads, the measurement is invalid for DC-005.

The third finding is that authorization, provenance, verifier integrity, and retention state are gates in this branch. They decide whether reuse may count as positive retained value. Their overhead magnitude remains outside DC-005 and belongs to DC-006.

The fourth finding is that controls are part of the measurement design. Single-turn chat, batch/offline control, and ordinary RAG should not produce Option C support unless real trajectory dependencies exist. This prevents logging artifacts from being misread as trajectory reuse.

The fifth finding is that synthetic baseline rows are mechanism probes only. They preserve the observed shape from earlier runtime ablations: hiding branch, verifier, and durable fields collapses code-agent, verification-heavy, and multi-agent branch/merge workloads from Option C toward Option B, while controls remain Option A and RAG remains Option B unless real trajectory dependencies are present.

## Discussion

The DC-005 branch narrows the Option C claim. Option C is not supported by the mere existence of agent logs or durable state. It is supported only when measured trajectory reuse survives attribution, authorization, integrity, and retention gates, and when retained value exceeds incremental coordination and validation costs.

This is important for the memory-centric architecture thesis because it turns a speculative claim into an executable measurement path. The branch identifies what a production or reproducible trace must record before the system can claim that trajectory/DAG memory fabric is necessary.

The scope boundary with DC-006 is also part of the result. DC-005 records whether reuse is authorized and valid. DC-006 measures the cost of proving that authorization and validity. Keeping those separate prevents the trajectory reuse branch from absorbing all security and provenance work into one constant.

The only unresolved process issue is fanout ledger isolation. Root `promise_check` continued to report the five DC-005 parent-harness CSVs as orphan artifacts. The audits treated this as expected clone-ledger behavior, not a content defect. The conductor should rerun root `promise_check` after shadow-ledger reconciliation.

## Conclusions and Recommendations

The DC-005 fanout branch completed its scoped objective. It produced a validated production trajectory reuse measurement plan and integrated that plan into parent `M-EXP-1` harness tables.

The branch should remain closed unless conductor merge reveals one of the concrete schema conflicts named by the auditor: missing `TRJ-*` rows, missing collapse thresholds, broken field semantics, or accidental absorption of DC-006 overhead measurement into DC-005.

Recommended next work is outside this clone:

- `DC-006`: provenance-validation overhead.
- Semantic-cache correctness and invalidation cost.
- Durable-store latency tails.
- Parent conductor merge verification, including root `promise_check` after clone ledger reconciliation.

## References

No external references were newly cited by this DC-005 clone report. The branch used prior project artifacts and session records as its source material.

## Appendix: Implementation Details

### Source Inventory

| Source | Date | Contents | Timeline role |
|---|---|---|---|
| `cf8385c6-18b3-4900-a1ac-b5f63ec629cb` | 2026-05-11 | Research result for the DC-005 trajectory reuse plan. | Cycle 1 plan creation. |
| `c618e995-f1b8-458d-af77-469dd98813f6` | 2026-05-11 | Worker verification of the required artifact and clone merge report. | Cycle 1 build/verification. |
| `b6a19029-4705-4dad-ac9f-1ade66f0d13d` | 2026-05-11 | Audit validating the DC-005 plan. | Cycle 1 validation. |
| `585db8a8-8f49-4e57-947d-dd507e22a057` | 2026-05-11 | Research brief to integrate DC-005 into parent M-EXP-1 CSV tables. | Cycle 2 integration plan. |
| `c95f11da-48b1-4349-8e59-ac60186d830a` | 2026-05-11 | Worker output creating the parent harness rows. | Cycle 2 integration build. |
| `3a63ae55-2b86-475c-9222-ff8800cf6109` | 2026-05-11 | Audit validating CSV integration and noting fanout ledger caveat. | Cycle 2 validation. |
| `1787ae9e-0f95-4c15-841d-24c927eaa959` | 2026-05-11 | Research brief closing the clone pending conductor merge. | Cycle 3 closure decision. |
| `09a25362-0bdb-4dc6-82a7-375f26fec1ff` | 2026-05-11 | Worker no-build closure memo. | Cycle 3 no-build confirmation. |
| `2015a875-fdee-4dad-b50c-dc2b8ea891e3` | 2026-05-11 | Final audit report with `PIVOT` decision. | Cycle 3 final decision. |

### Artifact Inventory

| File | Rows or lines | Role |
|---|---:|---|
| `memory-centric-agentic/experiments/trajectory_reuse_measurement_plan.md` | 298 lines | Required DC-005 measurement-plan artifact. |
| `data/measurement_experiment_specs.csv` | 7 data rows | `TRJ-001` through `TRJ-007` experiment specs. |
| `data/measurement_required_fields.csv` | 13 data rows | Required production fields for trajectory reuse measurement. |
| `data/measurement_thresholds.csv` | 4 data rows | Collapse and minimum-reuse thresholds. |
| `data/measurement_claim_update_matrix.csv` | 11 data rows | Routes DC-005 outcomes to synthesis claims. |
| `data/measurement_synthetic_probe_results.csv` | 6 data rows | Synthetic mechanism probes, not production calibration. |
| `MANIFEST.md` | updated during reporting | Workspace snapshot refreshed to include M-EXP-1 measurement artifacts. |

### Validation Summary

The audits reported no critical or moderate defects across the branch.

Cycle 1 validation confirmed that the plan existed, contained required markers, and passed `promise_check` and `org_check`.

Cycle 2 validation confirmed that the parent harness CSVs contained seven experiment rows, thirteen required-field rows, four threshold rows, eleven claim-update rows, and six synthetic probe rows. It also confirmed no DC-006 rows were added under DC-005.

Cycle 3 validation confirmed that the artifacts remained sufficient and issued `PIVOT` because the branch was closed and additional no-build validation would not add substantive output.

### Cross-Reference Map

| DC-005 output | Consuming context | Meaning |
|---|---|---|
| `trajectory_reuse_measurement_plan.md` | `measurement_experiment_specs.csv` | Converts prose experiment specs into machine-readable parent harness rows. |
| `trajectory_reuse_measurement_plan.md` | `measurement_required_fields.csv` | Converts required production trace fields into schema rows. |
| `trajectory_reuse_measurement_plan.md` | `measurement_thresholds.csv` | Converts Option C collapse equations into parent harness thresholds. |
| `measurement_claim_update_matrix.csv` | Parent synthesis claims | Routes future DC-005 measurements to claims `CL-001`, `CL-003`, `CL-005`, `CL-008`, `CL-009`, `CL-010`, and `CL-011`. |
| `measurement_synthetic_probe_results.csv` | Parent M-EXP-1 harness | Preserves synthetic mechanism probes while labeling them as non-production calibration. |
