---
created: 2026-05-11T15:38:00Z
cycle: 9
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-COMP-1
---

# Compression and Offload Boundary Model

This milestone tests compression as a correctness-preserving representation choice, not only a byte-reduction trick. The model is synthetic and mechanism-facing: no calibrated compression ratios, hardware latencies, bandwidths, prices, or energy constants are introduced. It consumes the validated trace v2 lifetime/reuse/provenance fields and the M-QUEUE-1 reversal model.

For memory object `i` in workload `w` under strategy `s`:

```text
NetCompressionValue(i,s) =
  BytesSaved(i,s) * CapacityPressure(w)
  + TransferAvoided(i,s)
  + QueueRelief(i,s)
  - ReconstructionCost(i,s)
  - MetadataCost(i,s)
  - ProvenanceRisk(i,s)
  - CorrectnessLossRisk(i,s)
```

Compression is allowed only when the representation preserves the semantics needed by the object. Lossy information removal is invalid if `correctness_sensitive = true` and there is no provenance-preserving pointer, validation path, or full-state recovery path. The invalidity gate is applied before score ranking; unsafe lossy strategies do not merely receive a low score.

## Strategy Set

| strategy | representation | intended use | primary risk |
|---|---|---|---|
| `keep_hot` | full object remains in hot tier | active KV, weights, correctness-sensitive state on the critical path | consumes hot capacity |
| `lossless_compress` | reversible compressed object | capacity/movement relief for exact state | reconstruction latency and metadata |
| `lossy_summarize` | irreversible semantic or numeric summary | low-risk scratch or non-authoritative context | lost evidence, replay breakage, verifier error |
| `summary_plus_pointer` | hot summary plus pointer to full source | RAG, tool output, trajectory, durable workspace | pointer chasing, provenance validation |
| `offload_full` | full object moved to colder tier | long-lived or low-reuse state needing exact recovery | offload/reload delay |
| `recompute_on_demand` | discard and rebuild from source | cheap deterministic intermediates | recompute latency and source drift |

## Object Safety Rules

| object class | safe low-risk strategies | lossy boundary |
|---|---|---|
| weights | `keep_hot`, `lossless_compress`, `offload_full` | lossy weight compression is deferred to calibration, not claimed here |
| KV cache | `keep_hot`, `lossless_compress`, `offload_full`, `recompute_on_demand` | lossy summarization changes continuation semantics unless the boundary is explicit |
| prefix cache | `lossless_compress`, `offload_full`, `recompute_on_demand` | lossy summaries are only safe for non-authoritative prompts |
| retrieved context | `summary_plus_pointer`, `offload_full`, `lossless_compress` | lossy summaries require source pointer and invalidation state |
| semantic cache entry | `summary_plus_pointer`, `offload_full` | lossy reuse is unsafe without provenance and invalidation |
| tool output | `summary_plus_pointer`, `offload_full`, `lossless_compress` | lossy summaries are unsafe when replay/audit or downstream verification depends on exact output |
| verifier state | `keep_hot`, `lossless_compress`, `summary_plus_pointer` | lossy summaries are invalid for correctness-sensitive verification evidence |
| branch state | `keep_hot`, `lossless_compress`, `summary_plus_pointer` | lossy summaries are invalid when merge/discard correctness depends on full state |
| trajectory log | `summary_plus_pointer`, `offload_full`, `lossless_compress` | lossy summaries are invalid for audit/replay without full log recovery |
| durable workspace | `summary_plus_pointer`, `offload_full`, `lossless_compress` | lossy summaries are invalid when future tool calls or merges depend on exact files |
| intermediate scratch | `lossy_summarize`, `recompute_on_demand`, `lossless_compress` | lossy is acceptable only when scratch is not correctness-sensitive |

## Queueing Link

Compression can help Option B/C remain viable when it reduces the object movement and coordination terms from M-QUEUE-1:

```text
B beats A if Benefit_object_reuse > Q_registry + Q_object_policy + Q_migration
C beats B if Benefit_branch_verifier_durable > Q_dag + Q_verifier_sync + Q_durable + Q_preemption
```

Compression helps when it lowers `Q_migration`, `Q_registry`, `Q_durable`, or `Q_preemption` enough to stay below those thresholds. It hurts when reconstruction, pointer chasing, validator work, or provenance checks add enough metadata or synchronization work to cross the same thresholds. Therefore `summary_plus_pointer` is plausible for agentic state only when its queue relief exceeds pointer/provenance overhead.

## Selective Queue Attribution

The queue-help claim is evaluated at object granularity before workload aggregation. A workload-level strategy is not labeled as helping an M-QUEUE-1 reversal unless at least one valid `(workload, object_class, strategy)` row satisfies:

```text
QueueRelief(i,s) > ReconstructionCost(i,s) + MetadataCost(i,s)
```

and the affected workload participates in a high-object or high-DAG reversal threshold. Under the current synthetic coefficients, no valid object-level row has positive net queue effect, so this milestone narrows the compression conclusion: compression/offload remains useful as capacity, movement, local-storage, provenance, and safety machinery, but it is not claimed to preserve queue thresholds for this trace/coefficient setup. The regenerated workload-level interaction table keeps queue-harm warnings for offload/recompute/pointer-heavy strategies and records zero positive object evidence for `helps_*` labels.

## Falsification Criteria

The compression boundary model is weakened if lossy summaries win for correctness-sensitive verifier, branch, trajectory, tool, semantic-cache, or durable workspace objects without a full recovery pointer. It is also weakened if compression remains beneficial when capacity pressure, transfer pressure, queue relief, and reuse are all zero. The model is strengthened if controls reduce to conventional KV/prefix/weights/scratch compression, RAG requires provenance-preserving context representations, and agentic workloads prefer exact or pointer-preserving representations for replay-sensitive state.
