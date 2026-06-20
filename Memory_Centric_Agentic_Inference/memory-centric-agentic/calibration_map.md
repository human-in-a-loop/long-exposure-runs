---
created: 2026-05-11T17:24:00Z
cycle: 12
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-CALIB-1
---

# Calibration Map for Memory-Centric Agentic Inference

## Scope

This map connects the validated symbolic and synthetic artifacts to public calibration evidence. It does not rerun M-COST-1, M-QUEUE-1, M-COMP-1, or M-PROTO-1, and it does not mutate any prior synthetic outputs.

Rows are labeled as `sourced_range`, `derived_from_source`, `measured_in_prior_artifact`, `synthetic_carryover`, or `deferred_public_evidence_missing`. Numeric calibrated rows are limited to vendor product specifications, standards-body capability claims, benchmark specifications, paper results, or transparent arithmetic from those sources.

## Source-Quality Rubric

- `vendor_product_spec` and `vendor_system_spec`: usable for product-specific capacity, bandwidth, storage, and fabric points, but not universal deployed constants.
- `standards_body_capability`: usable for protocol capability and feature scope, not for measured latency, contention, energy, price, or production deployment behavior.
- `benchmark_specification`: usable for scenario/load framing, not for agentic state reuse unless the benchmark exposes it.
- `peer_reviewed_systems_paper`, `arxiv_systems_experiment`, and `project_documentation`: usable for mechanism evidence and reported experimental outcomes with stated limitations.
- `deferred_public_evidence_missing`: first-class output when public evidence is missing or too indirect.

## Memory-Tier Ranges

The generated table `data/calibration_memory_tiers.csv` covers 9 tier categories: CXL/pooled memory, GPU-to-GPU fabric, HBM/GPU memory, NVMe-over-fabrics/remote storage, PCIe host link, durable workspace/object store, host CPU DRAM, local NVMe, semantic/prefix cache service. HBM/GPU rows anchor current public accelerator memory ranges: H100 reports 80-94 GB and 3.35-3.9 TB/s per GPU [1], H200 is represented as 141 GB and 4.8 TB/s [2][4], and DGX B200 aggregate figures derive to 180 GB and 8 TB/s per GPU from eight-GPU totals [3].

Host DRAM and host links are separated from accelerator memory. AMD EPYC 9005-class rows derive a 460.8-576 GB/s socket range from twelve DDR5 channels and 4800-6000 MT/s transfer rates [11], while Intel Xeon 6 MRDIMM evidence is retained as a 6400-8800 MT/s transfer-rate capability rather than converted without platform channel assumptions [10]. PCIe 6.0 x16 is represented as a 256 GB/s capability row from PCI-SIG [5].

Capability rows are deliberately not deployment constants. CXL/pooled memory is represented as support for switching, memory pooling, persistent memory, and link protection [7][14], while NVMe and NVMe-oF are represented as protocol/transport scope across PCIe, RDMA, TCP, and related transports [6]. Durable object-store latency and consistency distributions remain deferred.

## Workload Evidence

`data/calibration_workload_evidence.csv` maps public evidence to existing workload classes and architecture options. MLPerf Inference datacenter supports the conventional single-stream/server/offline controls [8]. PagedAttention supports KV-cache memory management and sharing as an LLM serving mechanism [9]. vLLM prefix caching supports hash-addressed KV-block reuse and trust-group cache isolation [12]. Semantic-cache evidence supports response/query reuse mechanisms but does not settle RAG correctness or invalidation cost [13].

No public source used in this cycle cleanly measures production durable agent trajectory reuse, branch survival, verifier-state retention value, or tool-output replay distributions. Those rows are deferred rather than stretched from adjacent KV/prefix/semantic-cache literature.

## Deferred Constants

The required deferred constants are explicit in `data/calibration_deferred_constants.csv`: per-tier energy per byte, CXL latency under contention, remote object-store latency distributions, semantic-cache correctness/invalidation cost, production agent trajectory reuse distributions, and provenance-validation overhead.

## Implications for Existing Models

The architecture decision form remains unchanged: retained value minus coordination overhead. Public ranges mainly calibrate capacity and movement ceilings; they do not directly replace synthetic reuse probabilities, correctness-loss costs, or queueing coefficients.

Robust conclusions: Option A remains necessary for MLPerf-style controls; KV/prefix-cache memory management is publicly supported as a real serving mechanism; CXL/NVMe rows should be treated as capability tiers unless measured deployment data is available.

Sensitive conclusions: Option B is sensitive to semantic/prefix cache hit rates, false-positive costs, provenance overhead, and host-device movement costs. Option C is most sensitive to production trajectory reuse distributions, verifier-state retention value, branch survival, durable-store latency tails, and CXL/remote-memory contention.

Speculative conclusions: durable multi-agent state reuse and trajectory-DAG memory fabric value remain synthetic until trace-backed public or reproducible workload evidence exists.

## Falsification Targets

High-priority reversal risks are: cxl_latency_under_contention, semantic_cache_false_positive_cost, trajectory_reuse_distribution. A later calibrated run should substitute these variables into the existing models without overwriting the validated synthetic baselines.
