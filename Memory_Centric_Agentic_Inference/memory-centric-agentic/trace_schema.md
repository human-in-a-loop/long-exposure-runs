---
created: 2026-05-11T14:36:00Z
cycle: 7
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-TRACE-1
---

# Trace Schema for Agentic Memory Objects

This schema is a calibration-ready event interface, not a production log format. It is designed to reconstruct memory-object lifetime, reuse, placement, branch survival, verifier delay, durable workspace growth, provenance coverage, and correctness-sensitive retention without storing raw prompts, tool outputs, or user data.

## Required Columns

| Field | Meaning | Requirement |
|---|---|---|
| `trace_id` | Stable trace identifier. | Required for every event. |
| `run_id` | Stable workload run identifier. | Required for every event. |
| `workload_class` | Workload label joinable to taxonomy/scheduling artifacts. | Required for every event. |
| `time_step` | Monotone synthetic or measured event time. | Required for every event. |
| `event_type` | Event verb from the schema table. | Required for every event. |
| `object_id` | Opaque memory object ID. | Required for object events; blank for run-level events. |
| `object_class` | Taxonomy object class. | Required when `object_id` is present. |
| `size_units` | Synthetic or measured size proxy. | Required for object create/update/write events. |
| `tier` | Placement tier or blank if not placed. | Required for place/migrate/evict events. |
| `parent_object_id` | Opaque parent object pointer. | Optional except derived/split objects. |
| `trajectory_node_id` | Opaque node in the run trajectory DAG. | Required for branch/verifier/tool/workspace events in agentic runs. |
| `branch_id` | Opaque branch identifier. | Required for branch events and branch-local objects. |
| `provenance_id` | Opaque source or artifact pointer. | Required for retrieved context, tool output, durable workspace, and semantic cache reuse. |
| `reuse_distance` | Time since previous access to the object or blank. | Required for repeated accesses. |
| `reuse_probability_hint` | Synthetic or inferred policy hint in `[0,1]`. | Optional policy input. |
| `correctness_sensitive` | Whether eviction/reuse can affect correctness or auditability. | Required for object events. |
| `recompute_cost_hint` | Synthetic or inferred recomputation-cost proxy. | Optional policy input. |
| `loss_cost_hint` | Synthetic or inferred correctness-loss proxy. | Optional policy input. |
| `durability_horizon` | Synthetic or measured expected persistence horizon. | Required for workspace and durable trajectory objects. |
| `verifier_id` | Opaque verifier attempt ID. | Required for verifier start/result events. |
| `merge_state` | `forked`, `merged`, `discarded`, `accepted`, `rejected`, or blank. | Required for branch merge/discard and verifier result events. |
| `source_version` | Opaque source/corpus/workspace version. | Required for provenance-sensitive events. |
| `invalidation_signal` | `none`, `ttl_expired`, `source_changed`, `confidence_revoked`, or blank. | Required for semantic-cache lookup/insert events. |

## Event Types

| Event type | Purpose | Minimum object fields |
|---|---|---|
| `run_start` | Begin a trace. | none |
| `object_create` | Materialize a memory object. | `object_id`, `object_class`, `size_units` |
| `object_access` | Read/use an existing object. | `object_id`, `object_class`, `reuse_distance` on repeated access |
| `object_update` | Mutate or append to an object. | `object_id`, `object_class`, `size_units` |
| `object_place` | Initial tier placement. | `object_id`, `tier` |
| `object_migrate` | Move object between tiers. | `object_id`, `tier` |
| `object_evict` | End residency without recompute. | `object_id`, `tier` |
| `object_recompute` | Recreate a previously needed object. | `object_id`, `recompute_cost_hint` |
| `branch_fork` | Create a trajectory branch. | `branch_id`, `trajectory_node_id` |
| `branch_discard` | Drop a branch. | `branch_id`, `merge_state` |
| `branch_merge` | Merge branch evidence. | `branch_id`, `merge_state` |
| `verifier_start` | Start a validation pass. | `verifier_id`, `trajectory_node_id` |
| `verifier_result` | Complete validation. | `verifier_id`, `merge_state` |
| `tool_call_start` | Start a tool call. | `trajectory_node_id` |
| `tool_call_result` | Materialize tool output. | `object_id`, `provenance_id` |
| `workspace_write` | Write durable workspace state. | `object_id`, `durability_horizon`, `provenance_id` |
| `workspace_compact` | Compact durable workspace state. | `object_id`, `durability_horizon` |
| `semantic_cache_lookup` | Query approximate reuse. | `object_id`, `provenance_id`, `invalidation_signal` |
| `semantic_cache_insert` | Insert approximate reusable state. | `object_id`, `provenance_id`, `source_version` |
| `run_end` | End a trace. | none |

## Derived Metrics

| Metric | Definition from event history |
|---|---|
| Object lifetime | `t_last(object_evict or run_end) - t_first(object_create)`. |
| Live bytes | `sum(size_units for objects with create <= t < evict and class = c)`. |
| Retained-value proxy inputs | Reuse probability, recompute cost, correctness sensitivity, loss cost, residency time, and tier transitions per object. |
| Reuse distance | Difference between consecutive `object_access` times for the same object. |
| DAG width/depth | Active branches over time and maximum trajectory-node depth. |
| Verifier delay | `time_step(verifier_result) - time_step(verifier_start)`. |
| Durable growth slope | Change in live durable workspace bytes over run duration. |
| Provenance coverage | Provenance-required events with nonblank `provenance_id` divided by all provenance-required events. |
| Trace validity rate | Valid events divided by all events after schema and order checks. |

## Privacy and Observability

The schema intentionally uses opaque IDs, version tokens, size proxies, and cost/loss hints. It does not require raw prompts, completions, retrieved documents, shell output, database rows, filesystem contents, or user data. A real runtime can hash or redact object IDs and provenance IDs while still preserving the memory-centric variables needed by downstream models.

## Boundary Conditions

Controls should collapse to weights, KV cache, prefix cache, and transient scratch with zero or inert branch/DAG fields. RAG traces should expose retrieved-context and semantic-cache reuse with provenance but without full trajectory dependence. Code-agent, verification-heavy, and multi-agent branch/merge traces should expose tool output, verifier state, branch state, trajectory log, and durable workspace as non-KV memory objects.
