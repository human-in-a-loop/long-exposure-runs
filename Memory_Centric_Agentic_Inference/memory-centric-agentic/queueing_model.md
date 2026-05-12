---
created: 2026-05-11T15:08:00Z
cycle: 8
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-QUEUE-1
---

# Queueing and Coordination-Overhead Model

## Scope

This model tests when the architecture boundary from `M-ARCH-1` reverses under coordination overhead. It uses only synthetic trace v2 as workload input and uses dimensionless queueing proxies; no measured hardware latency, bandwidth, energy, or dollar constants are introduced.

The core question is not whether object-aware or trajectory-aware scheduling can expose useful retained value. Prior milestones already established regimes where they can. The question here is whether metadata service queues, migration contention, checkpoint/preemption costs, verifier synchronization, and durable consistency queues can exceed that retained value.

## Architecture Paths

Option A, conventional request/model/KV serving, tracks model-level and aggregate KV/prefix pressure:

```text
T_A = T_base + Q_kv + Q_model
NetValue_A = -T_A
```

Option B adds memory-object visibility:

```text
T_B = T_A + Q_registry + Q_object_policy + Q_migration - Benefit_object_reuse
NetValue_B = Benefit_object_reuse - (T_A + Q_registry + Q_object_policy + Q_migration)
```

Option C adds trajectory/DAG coordination:

```text
T_C = T_B + Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption - Benefit_branch_verifier_durable
NetValue_C = Benefit_object_reuse + Benefit_branch_verifier_durable
             - (T_A + Q_registry + Q_object_policy + Q_migration
                + Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption)
```

The model intentionally shares `T_A` across all options, so reversals are driven by incremental overhead versus incremental retained value.

## Queueing Proxy

Each coordination service `s` is modeled as a simple M/M/1 proxy:

```text
rho_s = lambda_s / mu_s
Wq_s = rho_s / (mu_s - lambda_s)
Q_s = ops_s * Wq_s
```

This is not a production queueing model. It is a falsification instrument: if `lambda_s -> mu_s`, queue delay diverges, and an architecture option that still never reverses is numerically overfit or has hidden benefit assumptions.

## Trace-Derived Variables

The Python sweep reconstructs these variables from `data/agentic_trace_events_v2.csv`, `data/trace_workload_summary.csv`, and `data/trace_branch_dag_metrics.csv`:

| Variable | Trace source | Interpretation |
|---|---|---|
| `event_rate` | events per run duration | total event pressure per synthetic time step |
| `metadata_ops_per_step` | object create/place/access/update/evict/recompute/cache/tool/workspace events | registry lookup/update arrival rate |
| `migration_rate` | object migrate/place events per time step | tier-placement queue pressure |
| `migration_events_per_object_lifetime` | migrate/place events divided by object count | mobility intensity |
| `active_object_peak` | reconstructed birth/evict intervals | registry state size pressure |
| `live_bytes_peak` | reconstructed live object bytes | capacity-pressure proxy |
| `max_dag_width`, `max_dag_depth` | branch DAG metrics | trajectory coordination pressure |
| `mean_verifier_delay`, `verifier_results` | branch DAG metrics | verifier synchronization pressure |
| `durable_rate` | workspace write/compact and durable object events per time step | durable consistency pressure |

## Reversal Inequalities

Option B beats Option A iff:

```text
Benefit_object_reuse > Q_registry + Q_object_policy + Q_migration
```

Option C beats Option B iff:

```text
Benefit_branch_verifier_durable > Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption
```

Option C beats Option A iff both the object-level and trajectory-level retained values exceed their incremental queues:

```text
Benefit_object_reuse + Benefit_branch_verifier_durable
  > Q_registry + Q_object_policy + Q_migration
    + Q_dag + Q_verifier_sync + Q_durable_consistency + Q_preemption
```

These thresholds are trace-measurable once a real runtime reports event rates, object sizes, DAG width/depth, verifier delays, migration counts, and durable writes.

## Special Cases

| Special case | Expected reduction | Falsification use |
|---|---|---|
| zero metadata latency | Option B/C pay no object-registry queue | low-overhead winners should match `M-ARCH-1` |
| infinite metadata latency | Option B/C should lose unless benefits are unbounded | catches hidden object benefit constants |
| `lambda_s = 0` | `Q_s = 0` | idle services should not penalize architecture choice |
| `lambda_s -> mu_s` | `Q_s -> infinity` | saturation should produce reversals |
| zero branch width | DAG queue collapses | controls and RAG should not require Option C |
| zero verifier delay | verifier sync queue collapses | verifier-specific benefit must disappear or shrink |
| zero durable writes | durable consistency queue collapses | durable-overhead claims must not appear in controls |
| no migrations | migration queue collapses | isolates registry/policy from data movement |
| equal retained value | lower-overhead option wins | prevents architecture preference by label alone |

## Interpretation

The narrowed architecture thesis survives only if controls stay on Option A, RAG stays on Option B at low object overhead but reverses to Option A near object-service saturation, and agentic workloads select Option C only below explicit DAG/verifier/durable overhead thresholds. A result where Option C always wins, even as DAG or durable queues saturate, would rule out this mechanism.
