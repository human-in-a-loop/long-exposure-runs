---
created: 2026-05-11T12:22:00Z
cycle: 1
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-TAX-1
---

# Agentic Inference Memory Taxonomy

This taxonomy treats an inference run as a changing set of memory objects rather than only as a stream of arithmetic kernels. The core object model for later cycles is:

`object_i = {class, size_driver, lifetime_start, lifetime_end, mutability, reuse_mode, reuse_distance_driver, placement_candidates, compression_candidates, eviction_failure_mode}`

The first-cycle claim is deliberately modest: workload names alone are too coarse. Agentic workloads differ when future reuse and lifetime are driven by branch structure, tool calls, verification loops, and durable workspace state, not only by prompt and output token counts.

## Workload Classes

| Workload class | Memory objects touched | Dominant lifetime | Expected reuse mode | Branch / merge behavior | Is arithmetic-throughput-only modeling sufficient? |
|---|---|---|---|---|---|
| Single-turn chat | weights, KV cache, prompt/prefix cache | request lifetime | little reuse beyond shared weights and possibly common system prompt | none | Often close enough for first-order latency if prompts are short and cache reuse is low; memory-centric policy has limited upside beyond batching and weight residency. |
| Multi-turn chat | weights, KV cache, prompt/prefix cache, trajectory log | session lifetime | repeated access to prior turns; growing KV or re-prefill pressure | usually linear | Not sufficient when context grows across turns, because placement and compression decisions determine whether history stays hot, is summarized, or is recomputed. |
| Batch summarization | weights, KV cache, intermediate scratch | batch/job lifetime | low cross-item reuse except common instruction prefix | none | Often a control case: throughput and batching dominate if inputs are independent and durable state is discarded after output. |
| RAG | weights, KV cache, prefix cache, retrieved context, semantic cache entry | request to corpus-update lifetime | repeated retrieval of popular chunks, reusable prefixes, possible semantic cache hits | low branch; retrieval fanout may merge into a prompt | Arithmetic-only modeling misses retrieval-object placement, duplicate chunk reuse, and stale-cache risk. |
| Code-agent loop | weights, KV cache, prefix cache, tool output, intermediate scratch, trajectory log, durable workspace | task/workspace lifetime | repeated access to files, command outputs, tests, traces, and prior patches | branch on candidate fixes; merge through selected patch or test result | Not sufficient: correctness depends on preserving workspace state and tool evidence, not just generating tokens quickly. |
| Tool-using research agent | weights, KV cache, retrieved context, tool output, trajectory log, durable workspace, semantic cache entry | project/cycle lifetime | repeated use of notes, source snippets, computations, generated data, and report drafts | moderate branch-and-merge during source selection and hypothesis testing | Not sufficient: durable artifacts and provenance become first-class state with correctness/reproducibility failure modes. |
| Verification-heavy agent | weights, KV cache, verifier state, branch state, trajectory log, tool output | verification-loop lifetime | repeated re-evaluation of candidates, counterexamples, and test traces | high fanout; merge by acceptance/rejection | Not sufficient when verifier state controls future branching and eviction can cause false confidence, duplicate work, or missed counterexamples. |
| Multi-agent branch/merge run | weights, KV cache, prefix cache, branch state, verifier state, trajectory log, durable workspace | run/team lifetime | shared prefixes, shared artifacts, divergent branch state, merged conclusions | dominant feature: many speculative branches with uncertain future reuse | Strong memory-centric case: the scheduler needs to decide which branch state remains hot, which is compressed, and what must be durable for merge/audit. |
| Offline inference | weights, KV cache, intermediate scratch | batch lifetime | little semantic state reuse; high weight reuse across many items | none or pipeline-level | Often arithmetic/bandwidth throughput dominated; memory-centric policy matters mostly for batching, weight placement, and transient KV capacity. |

## Memory Object Roles

| Object class | Role in the run | Why it needs first-class treatment |
|---|---|---|
| weights | Model parameters shared by many requests or agents | Large, read-mostly, high reuse; movement dominates cold-start and placement economics. |
| KV cache | Attention state for generated or prefetched tokens | Size grows with context and active branches; eviction can force recomputation or truncate usable context. |
| prefix cache | Reusable KV or tokenized prompt prefix | Reuse depends on common instructions, templates, system prompts, and shared task setup. |
| retrieved context | External chunks inserted into prompts | Reuse follows corpus popularity and task locality; stale retrieval can create correctness risk. |
| tool output | Results from shells, browsers, databases, tests, solvers, and APIs | Often large, semi-structured, and more durable than KV; eviction can break provenance or force expensive reruns. |
| intermediate scratch | Temporary planner, parser, compiler, or tool state | Usually short-lived but can dominate memory spikes during conversion, validation, or generation. |
| branch state | State specific to speculative paths | Future reuse is uncertain until branch selection/merge; naive eviction can erase useful alternatives. |
| verifier state | Tests, counterexamples, proofs, audit traces, and acceptance criteria | Controls whether work is trusted; eviction can affect correctness, not only latency. |
| trajectory log | Ordered record of decisions, observations, and actions | Durable enough for audit, replay, and summarization; may be compressed but should remain reconstructable. |
| durable workspace | Files, patches, datasets, plots, checkpoints, and reports | Must outlive a model context and survive process restarts; storage policy is closer to OS/database design than KV caching. |
| semantic cache entry | Cached answer, embedding, or result keyed by meaning rather than exact prefix | Reuse can cross sessions, but invalidation and correctness are workload-specific. |

## Downstream Variables Exposed

The schema exposes variables for later cycles:

- `M-LIFE-1`: lifetime boundaries, reuse distance drivers, branch probability, merge probability, fanout, durability horizon.
- `M-COST-1`: placement candidates, compression candidates, eviction failure mode, recomputation risk.
- `M-SIM-1`: workload class, dominant objects, object coverage, branch/tool/verification drivers.

## Edge Cases

- No tools: single-turn chat and batch summarization mostly reduce to weights plus KV.
- No branch: multi-turn chat still has long-lived KV/trajectory pressure but weak branch-state pressure.
- No reuse: offline independent inference weakens semantic/prefix caching arguments.
- Infinite reuse or pinned prefix: common system prefixes behave more like shared read-mostly memory.
- Zero durable state: arithmetic and transient KV become more predictive.
- Context-window saturation: KV growth forces summarization, eviction, or recomputation decisions.

## First-Cycle Falsification

The memory-centric framing is weakened for a workload class if its useful state can be accurately reduced to model weights plus linear KV growth, with no persistent non-KV state, no uncertain future reuse, no correctness-sensitive eviction risk, and no meaningful cross-request reuse.
