---
created: 2026-05-11T12:22:00Z
cycle: 1
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-TAX-1
---

# Assumptions for M-TAX-1

## Sourced

- No sourced production-trace, hardware-constant, or energy-per-access claims are made in this cycle.

## Derived

- The memory-object schema is derived from the directive's required objects and downstream needs: lifetime, reuse, placement, compression, and eviction risk.
- Workload classes are separated when they imply different memory-object lifetimes or reuse drivers, even if their model calls use the same base transformer.
- A workload can be a weak memory-centric case if it has short-lived state, no branch structure, low prefix/context reuse, and cheap recomputation.

## Simulated-Plan

- Later `M-LIFE-1` and `M-SIM-1` work should sample object lifetimes as intervals with branch-conditioned reuse distances rather than as a single prompt-length scalar.
- Later `M-COST-1` work should assign tier costs to HBM, GPU memory, CPU DRAM, pooled/CXL-like memory, NVMe, remote storage, and durable workspace state.
- Later simulator policies should compare at least request-level scheduling, cache-page scheduling, context-segment scheduling, and trajectory-level scheduling.

## Speculative

- Long-running code, research, verification, and multi-agent workloads are expected to create correctness-sensitive state that cannot always be discarded like transient KV cache.
- Branch/merge execution is expected to increase variance in object lifetime and reuse distance because speculative branches may become important after a verifier or merge step.
- Tool outputs and durable workspace artifacts are expected to require policies closer to storage/provenance systems than conventional LLM-serving cache eviction.
- Semantic cache entries are expected to have higher invalidation risk than exact prefix caches because reuse is approximate and workload semantics matter.

## Guardrails for Later Cycles

- Do not present hardware constants, production frequencies, compression ratios, cache hit rates, or energy numbers as facts until sourced or explicitly simulated.
- Treat negative results as useful: if batch summarization and offline inference remain throughput-dominated under plausible parameters, keep them as controls.
- Preserve object names from `memory_objects.csv` unless a later cycle has a documented reason to split or merge them.
