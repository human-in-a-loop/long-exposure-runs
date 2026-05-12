---
created: 2026-05-11T14:36:00Z
cycle: 7
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-TRACE-1
---

# Trace Calibration Plan

`M-TRACE-1` stays calibration-ready rather than calibration-claiming. The generated traces are synthetic, but the fields are chosen so a real serving or agent runtime could map measured logs into the same shape later.

## Runtime Mapping

| Runtime source | Schema fields | Status |
|---|---|---|
| Request router and model loader | `run_id`, `workload_class`, `weights`, `tier`, `source_version` | Directly observable |
| KV/prefix cache manager | `object_id`, `object_class`, `size_units`, `object_place`, `object_migrate`, `object_evict`, `reuse_distance` | Directly observable |
| Retriever/vector cache | `semantic_cache_lookup`, `semantic_cache_insert`, `retrieved context`, `provenance_id`, `invalidation_signal` | Directly observable plus policy-derived invalidation |
| Tool runner | `tool_call_start`, `tool_call_result`, `tool output`, `recompute_cost_hint`, `provenance_id` | Directly observable |
| Agent planner | `trajectory_node_id`, `branch_id`, `branch_fork`, `branch_merge`, `branch_discard` | Observable if planner emits node metadata |
| Verifier/test harness | `verifier_start`, `verifier_result`, `verifier_id`, `merge_state`, `loss_cost_hint` | Observable with inferred loss proxy |
| Workspace/version store | `workspace_write`, `workspace_compact`, `durability_horizon`, `source_version` | Directly observable plus retention-policy-derived horizon |

## Field Status

Direct fields are event times, object IDs, object classes, sizes, tiers, branch/verifier/tool/workspace events, and source versions. Inferred fields are reuse probability, recompute cost, loss cost, and durability horizon. Optional fields are parent object links and trajectory node IDs for non-agentic controls. Synthetic-only fields in this cycle are the numeric size and cost proxies used by the generator.

## Downstream Consumers

| Milestone | Consumed trace outputs |
|---|---|
| `M-QUEUE-1` | Event times, live-byte curves, DAG width, verifier delays, tier migration counts. |
| `M-COMP-1` | Object lifetimes, update frequency, object class, size, provenance, invalidation, durability horizon. |
| `M-PROTO-1` | Full event schema, validation rules, architecture option assignment from workload summaries. |
| `M-CALIB-1` | Direct/inferred/synthetic field status, source-version tokens, tier transitions, measured size distributions. |
| `M-SEC-1` | Provenance coverage, invalidation signals, correctness sensitivity, workspace durability, semantic-cache safety failures. |

## Falsification Criteria

1. If real traces cannot reconstruct object birth, active lifetime, and end state without hidden runtime state, the schema is insufficient.
2. If controls require branch, verifier, or durable trajectory fields to explain memory behavior, the narrowed architecture boundary from `M-ARCH-1` is over-broad.
3. If code-agent, verification-heavy, and branch/merge traces reduce to weights plus KV/prefix size with negligible non-KV live bytes, the memory-centric agentic thesis must narrow.
4. If semantic-cache or retrieved-context reuse cannot carry provenance and invalidation signals, reuse cannot be made calibration-safe.
5. If branch merges/discards cannot be validated from event order, trajectory/DAG scheduling is not auditable enough for downstream policy work.
6. If durable workspace growth cannot be separated from context-window saturation, trace-derived memory pressure will confound KV and project state.
7. If architecture options cannot be assigned from trace summaries without extra hidden assumptions, the trace is not a sufficient interface for policy evaluation.
