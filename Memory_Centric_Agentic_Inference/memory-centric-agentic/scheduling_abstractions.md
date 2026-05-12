---
created: 2026-05-11T13:45:00Z
cycle: 5
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-SCHED-1
---

# Scheduling Abstractions for Memory-Centric Agentic Inference

This cycle treats a scheduling unit as an information boundary. A request,
job, kernel, model, cache page, context segment, memory object, or
agent-trajectory DAG can only make good placement and retention decisions if
the fields it observes include the variables that determine the dominant
memory object's lifetime, reuse, and correctness risk.

The comparison is synthetic and derived from the validated simulator outputs.
It does not model production arrivals, queueing, multi-tenant contention,
vendor hardware constants, or measured datacenter prices. Those are deferred
until the abstraction boundary is explicit enough to say what a real scheduler
would need to measure.

## Candidate Units

| scheduling_unit | Typical boundary | Observable state | Main blind spot |
|---|---|---|---|
| request | single prompt/response or run slice | workload label, aggregate size | object class, reuse, branch survival, durable horizon, correctness loss |
| job | batch/offline job or agent task | workload label, aggregate size, coarse durability | object-local reuse and verifier/correctness state |
| kernel | accelerator operation | local tensor size and timing | semantic lifetime, durable state, branch future |
| model | model/adaptor residency group | model identity, weights, aggregate demand | non-weight objects and trajectory dependencies |
| cache_page | KV/prefix/cache page | object class for KV/prefix-like pages, size, local reuse | tool/verifier/durable semantics |
| context_segment | prompt/KV/retrieved-context segment | object class, size, reuse probability, recompute cost | branch survival, verifier delay, durable workspace horizon |
| memory_object | taxonomy memory object | object class, size, reuse, recompute/loss cost, correctness sensitivity | cross-object branch/merge trajectory structure |
| agent_trajectory_dag | branch/merge run graph | object fields plus branch fanout/survival, verifier delay, durability horizon, correctness sensitivity | coordination overhead and excess detail for controls |

## Scoring Model

For each workload and scheduling unit, the evaluator computes:

`Benefit(unit, workload) = observed retained value + movement avoidance + reuse capture + branch capture + durability capture + correctness capture - coordination overhead`

The terms are normalized synthetic scores, not measured performance. The
important output is the preferred unit and the failure-mode explanation, not
the absolute score. A unit should win only when its visibility set contains
the fields that drive the positive object contributions in
`data/sim_policy_object_breakdown.csv` and the workload-level winner in
`data/sim_policy_results.csv`.

## Expected Collapses

- Controls with weights, KV cache, prefix cache, and transient scratch should
  prefer request, model, cache-page, or context-segment scheduling because
  finer units add coordination overhead without exposing useful agentic state.
- RAG should prefer context-segment or memory-object scheduling because
  retrieved context and semantic cache entries depend on reuse and
  correctness/staleness fields, but not branch or durable trajectory fields.
- Code-agent, verification-heavy, and multi-agent branch/merge runs should
  prefer memory-object or trajectory-DAG scheduling when tool output, branch
  state, verifier state, trajectory log, or durable workspace dominate.
- Equal tier costs should collapse movement-driven differences.
- Context-window saturation should not collapse durable workspace or
  trajectory-log value when the durable horizon remains positive.

## Deferred Work

Queueing, arrival processes, preemption, multi-tenant contention, cache-page
packing, interconnect topology, compression ratios, and exact tier capacities
are deferred. They are real scheduling concerns, but introducing them before
the abstraction boundary is explicit would mix policy visibility with cluster
mechanics.
