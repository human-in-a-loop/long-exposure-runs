---
created: 2026-05-11T18:55:00Z
run_id: run-2026-05-11T121649Z
fork: 523f4e7604d4
clone: 0
milestone: M-EXP-1
deferred_constant: DC-005
evidence_status: measurement_design
---

# Production Trajectory Reuse Measurement Plan

## Scope

This branch designs the measurement plan for `DC-005`: production agent trajectory reuse distribution. It focuses only on trajectory/DAG reuse: branch survival, verifier-state reuse, tool-output replay, trajectory-log replay, durable workspace reuse, and the ablation thresholds that collapse Option C (`trajectory/DAG memory fabric`) to Option B or Option A.

The plan does not claim that production reuse is already measured. Existing numeric examples are synthetic and are used only to define measurement fields, threshold equations, and falsification criteria.

## Mechanism Under Test

Option C is justified only when trajectory-level retained value remains positive after incremental trajectory-fabric costs:

```text
Benefit_branch_verifier_durable
  > Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption
```

With security/provenance gates included, the production measurement should evaluate:

```text
NetTrajectoryValue =
    V_branch
  + V_verifier
  + V_tool_replay
  + V_trajectory_log
  + V_durable_workspace
  - Q_dag
  - Q_verifier_sync
  - Q_durable_consistency
  - Q_preemption
  - ValidationOverhead_trajectory
  - ExpectedSecurityLoss_trajectory
```

Option C remains justified iff:

```text
NetTrajectoryValue > max(0, NetObjectOnlyValueDelta)
```

For the narrower C-versus-B boundary, the measurement should use:

```text
C_beats_B iff NetTrajectoryValue > 0
```

For the C-versus-A boundary, combine object and trajectory value:

```text
C_beats_A iff NetObjectReuseValue + NetTrajectoryValue > 0
```

This branch measures the `Benefit_*` side of the inequality and the trajectory event rates needed for the queue terms. Provenance-validation overhead is owned by the DC-006 branch, but this branch must record whether trajectory reuse was authorized; unauthorized reuse contributes zero positive retained value.

## Special-Point Checks

| Point or limit | Evaluation | Interpretation |
|---|---|---|
| `p_survive = 0` for all branches | `V_branch = 0` and branch-retention value vanishes | Option C cannot be justified by branch state. |
| `reuse_count = 0` for verifier/tool/durable objects | reuse benefit is zero except audit-retention value explicitly measured separately | Downgrade to Option B/A unless queue costs are also zero and another trajectory object contributes value. |
| `max_dag_width = 0` | `Q_dag = 0` and trajectory DAG scheduling has no object to schedule | Controls and RAG should not select Option C. |
| `verifier_results = 0` | `V_verifier = 0`, `Q_verifier_sync = 0` | Verification-heavy claims should disappear. |
| `durability_horizon = 0` | durable retained value and durable consistency cost collapse | Durable workspace cannot support Option C. |
| missing `trajectory_node_id`, `branch_id`, `verifier_id`, or replay edge | denominator may exist but reuse is not attributable | Mark measurement invalid for DC-005 rather than imputing reuse. |
| `AuthorizedReuse = false` | positive retained value is forced to zero | Reuse cannot count even if the object was accessed. |
| `Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption -> infinity` | `NetTrajectoryValue -> -infinity` | Option C must collapse to B/A. |

## Required Production Trace Fields

Trace v2 already defines most DC-005 fields. Production measurement needs the following subset with stable semantics:

| Field | Required for | Notes |
|---|---|---|
| `trace_id`, `run_id`, `workload_class`, `time_step`, `event_type` | all metrics | `time_step` may be monotonic logical time or timestamp. |
| `object_id`, `object_class`, `size_units` | all retained objects | Required for branch state, verifier state, tool output, trajectory log, durable workspace. |
| `trajectory_node_id` | DAG attribution | Required for tool, branch, verifier, workspace, replay, and merge events. |
| `parent_object_id` | replay/source dependency edge | Required to distinguish reuse from unrelated access. |
| `branch_id`, `merge_state` | branch survival and merge/discard rates | Required for `branch_fork`, `branch_merge`, `branch_discard`, branch-local objects. |
| `verifier_id` | verifier reuse and verifier delay | Required for `verifier_start`, `verifier_result`, verifier-state objects. |
| `durability_horizon` | durable workspace retained value | Required for workspace and trajectory objects. |
| `reuse_distance` | reuse interval distribution | Required on repeated object access. |
| `correctness_sensitive`, `recompute_cost_hint`, `loss_cost_hint` | retained-value proxy | May be measured, estimated from rerun cost, or omitted from benefit until calibrated. |
| `provenance_id`, `source_version`, `invalidation_signal` | authorized replay preconditions | Needed to avoid counting stale trajectory reuse. |
| `actor_id`, `replay_authorization_scope` | production security extension | Required for trajectory replay authorization; absent in trace v2 and owned jointly with DC-006. |
| `verifier_evidence_hash` | production security extension | Required to trust verifier-state replay; absent in trace v2. |
| `retention_hold_state` | production retention extension | Required for durable workspace retention/deletion conflicts; absent in trace v2. |

Privacy constraint: object IDs, provenance IDs, actor IDs, and verifier hashes may be opaque or salted. The measurement requires stable joins and equality checks, not raw prompts, tool outputs, files, or user data.

## Event Extensions

Trace v2 can infer reuse from repeated `object_access`, but production DC-005 should add explicit replay intent and outcome events:

| Event | Purpose | Minimum fields |
|---|---|---|
| `trajectory_replay_start` | Begin replay/resume from prior trajectory state | `trajectory_node_id`, `parent_object_id`, `actor_id`, `replay_authorization_scope` |
| `trajectory_replay_result` | Record success, failure, or fallback recompute | `trajectory_node_id`, `object_id`, `merge_state`, `recompute_cost_hint` |
| `branch_promote` | Mark branch selected as future state | `branch_id`, `trajectory_node_id`, `merge_state=accepted` |
| `branch_evidence_access` | Access discarded or merged branch evidence | `branch_id`, `object_id`, `reuse_distance` |
| `verifier_evidence_access` | Reuse test, proof, audit, or counterexample state | `verifier_id`, `object_id`, `verifier_evidence_hash` |
| `workspace_dependency_access` | Use durable artifact as dependency for later step | `object_id`, `parent_object_id`, `durability_horizon` |
| `tool_output_replay` | Reuse prior tool output instead of rerunning tool | `object_id`, `provenance_id`, `recompute_cost_hint` |

If production teams cannot add new event types, equivalent records may be encoded as `object_access` with a `replay_outcome` extension. The measurement is invalid if replay and ordinary read access cannot be separated.

## Metrics

| Metric ID | Definition | Supports Option C if | Falsifies Option C if |
|---|---|---|---|
| `traj_reuse_rate` | reused trajectory-scoped objects / created trajectory-scoped objects | materially above zero for agentic workloads and absent in controls | near zero for code-agent, verification-heavy, and branch/merge workloads |
| `weighted_traj_reuse_rate` | sum reused `size_units * correctness_weight` / created trajectory-scoped weighted size | high-weight correctness-sensitive state is reused | reuse is concentrated in low-value or non-correctness-sensitive objects |
| `branch_survival_rate` | accepted or merged branches / forked branches | enough branches survive or inform merges to justify retention | branches are almost always discarded without later evidence access |
| `post_merge_evidence_reuse` | accesses to merged/discarded branch evidence after merge/discard / branch evidence objects | branch evidence affects later steps, audits, or regressions | merged/discarded evidence is never read again |
| `verifier_state_reuse_rate` | verifier-state objects reused across candidates, retries, regressions, or final audit / verifier-state objects created | verifier traces prevent repeated validation or missed regressions | verifier state is single-use and can be discarded |
| `tool_output_replay_rate` | tool outputs replayed or cited after original step / tool outputs created | tool outputs avoid reruns or preserve auditability | tool outputs are never reused and are cheap to recompute |
| `durable_dependency_reuse_rate` | durable workspace artifacts read as dependencies after creation session / durable artifacts created | durable workspace carries cross-session state | durable artifacts do not affect future execution |
| `trajectory_reuse_distance_p50_p95` | reuse-distance distribution for trajectory-scoped objects | reuse distances exceed request/session scope | reuse is only immediate and request-local |
| `trajectory_value_proxy` | sum over reused trajectory objects of `P_reuse * (C_recompute + correctness_sensitive * C_loss)` | exceeds trajectory coordination and validation overheads | less than overheads or unavailable because cost/loss hints absent |
| `field_observability_rate` | required DC-005 fields present / required fields | high enough to compute all prior metrics | missing fields make reuse unattribitable |

Trajectory-scoped object classes are `branch state`, `verifier state`, `tool output`, `trajectory log`, and `durable workspace`. KV cache may be counted only when it is branch-local and joined to a `branch_id`; otherwise it belongs to conventional serving analysis.

## Experiment Specs

| Experiment ID | Workload target | Measurement | Required instrumentation | Expected signal | Would support | Would falsify | Claim updates |
|---|---|---|---|---|---|---|---|
| `TRJ-001-branch-survival` | code-agent loop; verification-heavy; multi-agent branch/merge | branch fork, merge, discard, promote, and later evidence access rates | `branch_id`, `trajectory_node_id`, `merge_state`, `branch_evidence_access` | survival and post-merge reuse distribution | Option C branch-retention value is positive | branches die without later evidence access | `CL-003`, `CL-005`, Option C rows |
| `TRJ-002-verifier-reuse` | verification-heavy; code-agent loop; multi-agent branch/merge | verifier-state access across candidates, retries, regressions, and audits | `verifier_id`, `verifier_start`, `verifier_result`, `verifier_evidence_access`, `verifier_evidence_hash` | verifier reuse and avoided repeated validation | verifier state is a reusable correctness-sensitive object | verifier state is single-use or not replay-authorized | `CL-003`, `CL-009` |
| `TRJ-003-tool-output-replay` | code-agent loop; research/tool agents; branch/merge | replay/citation of previous tool outputs versus rerun | `tool_call_result`, `tool_output_replay`, `provenance_id`, `recompute_cost_hint` | replay avoids tool reruns or preserves evidence | tool outputs carry retained value beyond current prompt | tool outputs are never reused or cheap to rerun | `CL-003`, `CL-011` |
| `TRJ-004-durable-dependency` | code-agent loop; multi-agent branch/merge | workspace artifacts used as future dependencies | `workspace_write`, `workspace_dependency_access`, `durability_horizon`, `parent_object_id` | cross-session durable dependency graph | durable workspace supports Option C | durable artifacts are archival only and not execution inputs | `CL-003`, `CL-012` |
| `TRJ-005-trajectory-reuse-distance` | all agentic workloads plus controls | reuse-distance distribution for trajectory-scoped objects | `object_access`, `reuse_distance`, `object_class`, `trajectory_node_id` | long-tail reuse beyond request-local scope | agentic memory exceeds token/KV lifetime | reuse distances are short and KV-like | `CL-003`, `CL-008` |
| `TRJ-006-field-ablation-replay` | production/open traces replayed through runtime prototype | architecture decision with fields hidden | all DC-005 fields plus runtime option computation | hiding branch/verifier/durable fields collapses C to B/A | M-PROTO-1 causal boundary generalizes | architecture choice unchanged by hiding fields | `CL-003`, `CL-011` |
| `TRJ-007-control-negative` | single-turn chat; batch/offline controls; RAG | false-positive trajectory reuse check | same trace parser as agentic workloads | zero/inert DAG fields and no Option C recommendation | measurement discriminates controls | controls show spurious Option C from logging artifacts | `CL-001`, `CL-010` |

## Threshold Equations

Use measured distributions to compute a lower-bound retained value. Let object `i` range over trajectory-scoped objects that pass authorization checks:

```text
V_i =
  I_authorized(i)
  * I_reused(i)
  * (C_recompute_i + I_correctness_sensitive(i) * C_loss_i)
```

Branch value:

```text
V_branch =
  sum_i in branch_state V_i
  + sum_b I_survived_or_informed_merge(b) * C_branch_evidence_b
```

Verifier value:

```text
V_verifier =
  sum_i in verifier_state V_i
  + sum_v I_reused(v) * C_validation_rerun_v
```

Tool replay value:

```text
V_tool_replay =
  sum_i in tool_output I_tool_replayed(i)
    * I_authorized(i)
    * (C_tool_rerun_i + I_correctness_sensitive(i) * C_audit_loss_i)
```

Durable workspace value:

```text
V_durable_workspace =
  sum_i in durable_workspace I_dependency_reused(i)
    * I_authorized(i)
    * (C_recompute_i + C_dependency_loss_i)
```

Trajectory-log value:

```text
V_trajectory_log =
  sum_i in trajectory_log I_replayed_or_audited(i)
    * I_authorized(i)
    * C_audit_or_resume_loss_i
```

Total trajectory benefit:

```text
Benefit_branch_verifier_durable =
  V_branch + V_verifier + V_tool_replay + V_durable_workspace + V_trajectory_log
```

Queue threshold imported from M-QUEUE-1:

```text
TrajectoryQueueCost =
    (DAGWidth * lambdaDag * Odag) / (muDag * (muDag - lambdaDag))
  + (lambdaVerifier * Overifier * VerifierDelay) / (muVerifier * (muVerifier - lambdaVerifier))
  + (lambdaDurable * Odurable) / (muDurable * (muDurable - lambdaDurable))
  + (lambdaPreempt * Opreempt) / (muPreempt * (muPreempt - lambdaPreempt))
```

Collapse thresholds:

```text
C_to_B collapse when
  Benefit_branch_verifier_durable <= TrajectoryQueueCost
                                     + ValidationOverhead_trajectory
                                     + ExpectedSecurityLoss_trajectory

C_to_A collapse when
  Benefit_object_reuse + Benefit_branch_verifier_durable
    <= ObjectQueueCost + TrajectoryQueueCost
       + ValidationOverhead_total
       + ExpectedSecurityLoss_total
```

Minimum branch survival threshold, holding per-branch state value constant:

```text
p_survive_min =
  (TrajectoryQueueCost + ValidationOverhead_trajectory + ExpectedSecurityLoss_trajectory
   - V_verifier - V_tool_replay - V_durable_workspace - V_trajectory_log)
  / (f * s_b * (C_branch_recompute + C_branch_loss))
```

If the numerator is negative, non-branch trajectory value alone can justify Option C. If the denominator is zero, branch survival cannot justify Option C.

Minimum verifier reuse threshold, holding other terms constant:

```text
p_verifier_reuse_min =
  (TrajectoryQueueCost + ValidationOverhead_trajectory + ExpectedSecurityLoss_trajectory
   - V_branch - V_tool_replay - V_durable_workspace - V_trajectory_log)
  / (n_verifier_states * (C_validation_rerun + C_verifier_loss))
```

These thresholds should be emitted as distributions, not just means: p50/p95 queue costs and p50/p95 retained values can produce different architecture choices.

## Synthetic Baseline From Existing Artifacts

Existing synthetic artifacts provide only a mechanism baseline:

| Workload | Synthetic DAG signal | Synthetic ablation result | Measurement implication |
|---|---|---|---|
| single-turn chat control | `max_dag_width=0`, `verifier_results=0` | remains Option A under all branch/verifier/durable ablations | Production controls should remain Option A. |
| batch/offline control | `max_dag_width=0`, `verifier_results=0` | remains Option A | Production batch traces should not create spurious trajectory value. |
| RAG | `max_dag_width=0`, `verifier_results=0` | hiding branch/verifier/durable fields does not change Option B | RAG is not a DC-005 support case unless it has real trajectory dependencies. |
| code-agent loop | `max_dag_width=2`, `verifier_results=2` | hiding branch/verifier/durable fields collapses C to B | Production code-agent traces should reproduce or falsify this collapse. |
| verification-heavy | `max_dag_width=3`, `verifier_results=4` | hiding branch/verifier/durable fields collapses C to B | Verifier reuse is the critical measured variable. |
| multi-agent branch/merge | `max_dag_width=4`, `verifier_results=3` | hiding branch/verifier/durable fields collapses C to B | Branch survival and durable dependency reuse should be strongest here. |

The existing synthetic results support the shape of the measurement, not the production magnitude.

## Data Products For Parent Harness

This branch should contribute the following rows to the parent M-EXP-1 harness:

| Output table | Rows contributed by this branch |
|---|---|
| `data/measurement_experiment_specs.csv` | `TRJ-001` through `TRJ-007` |
| `data/measurement_required_fields.csv` | all fields in Required Production Trace Fields with `deferred_constant=DC-005` |
| `data/measurement_thresholds.csv` | `C_to_B_trajectory_reuse`, `C_to_A_trajectory_reuse`, `p_survive_min`, `p_verifier_reuse_min` |
| `data/measurement_claim_update_matrix.csv` | updates to `CL-001`, `CL-003`, `CL-005`, `CL-008`, `CL-009`, `CL-010`, `CL-011` |
| `data/measurement_synthetic_probe_results.csv` | optional synthetic replay rows showing known C-to-B/A collapse under hidden trajectory fields |

## Acceptance Criteria

The trajectory reuse measurement branch is complete when a worker can implement parsers and dashboards from this plan without inventing semantics:

- Every DC-005 metric has required fields and an explicit denominator.
- Controls have a negative test that should keep Option A.
- At least one threshold collapses Option C to Option B when trajectory benefit is below trajectory queue and validation costs.
- At least one threshold collapses Option C to Option A when combined object plus trajectory retained value is below all incremental overheads.
- Missing trajectory fields make the measurement invalid rather than silently imputing no reuse.
- Unauthorized, stale, tampered, or retention-invalid replay contributes zero positive value.
- Synthetic examples are labeled as mechanism probes, not calibration.

## Open Risks

- Production systems may not have stable trajectory node IDs across resumes, compactions, or multi-agent handoffs; without them, reuse cannot be attributed to a DAG.
- Reuse and audit value can be confounded: a trajectory log may be accessed for compliance rather than execution. The metric must separate execution reuse, audit reuse, and archival reads.
- Tool-output replay may be hidden behind application caches; instrumentation must distinguish replayed prior output from rerun tool calls with identical results.
- Branch evidence can inform a merge without later explicit access. If the runtime does not log merge evidence inputs, branch survival will be underestimated.
- Correctness-loss costs may be unavailable in production. In that case, report lower-bound recompute-only value and mark correctness-sensitive value as uncalibrated.
