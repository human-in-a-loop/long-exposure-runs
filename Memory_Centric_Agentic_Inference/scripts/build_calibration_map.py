#!/usr/bin/env python3
# created: 2026-05-11T17:24:00Z
# cycle: 12
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CALIB-1
"""Build sourced calibration tables for M-CALIB-1.

The script is intentionally data-explicit: public product/standard facts are
kept separate from derived arithmetic and deferred unknowns.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC = ROOT / "memory-centric-agentic" / "calibration_map.md"
REFS = ROOT / "REFERENCES.md"


def refs_available() -> set[str]:
    text = REFS.read_text()
    refs = set(re.findall(r"^\[(\d+)\]", text, flags=re.M))
    numbers = sorted(int(r) for r in refs)
    if numbers != list(range(1, max(numbers) + 1)):
        raise SystemExit(f"reference numbering is not contiguous: {numbers}")
    return refs


def cite_ok(source_refs: str, refs: set[str]) -> bool:
    found = re.findall(r"\[(\d+)\]", source_refs)
    return bool(found) and all(ref in refs for ref in found)


MEMORY_TIERS = [
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA H100 SXM/NVL",
        "quantity": "per-GPU capacity",
        "range_low": "80",
        "range_high": "94",
        "unit": "GB",
        "range_basis": "H100 SXM and H100 NVL product specifications",
        "source_refs": "[1]",
        "source_quality": "vendor_product_spec",
        "claim_type": "sourced_range",
        "used_in_existing_model": "M-COST-1 memory tier; M-PROTO-1 HBM placement",
        "recommended_model_mapping": "hbm_capacity_per_gpu_gb",
        "notes": "Product-specific point range, not a universal HBM constant.",
    },
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA H100 SXM/NVL",
        "quantity": "per-GPU bandwidth",
        "range_low": "3.35",
        "range_high": "3.9",
        "unit": "TB/s",
        "range_basis": "H100 SXM and H100 NVL product specifications",
        "source_refs": "[1]",
        "source_quality": "vendor_product_spec",
        "claim_type": "sourced_range",
        "used_in_existing_model": "M-COST-1 bandwidth-delay term",
        "recommended_model_mapping": "hbm_bandwidth_tbps",
        "notes": "Peak product bandwidth; workload-achieved bandwidth remains deferred.",
    },
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA H200",
        "quantity": "per-GPU capacity",
        "range_low": "141",
        "range_high": "141",
        "unit": "GB",
        "range_basis": "DGX H200 total memory divided by eight H200 GPUs",
        "source_refs": "[2] [4]",
        "source_quality": "vendor_system_spec",
        "claim_type": "derived_from_source",
        "used_in_existing_model": "M-COST-1 memory tier; trace capacity-pressure calibration",
        "recommended_model_mapping": "hbm_capacity_per_gpu_gb",
        "notes": "Derived from 1,128 GB total DGX H200 GPU memory across eight GPUs.",
    },
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA H200",
        "quantity": "per-GPU bandwidth",
        "range_low": "4.8",
        "range_high": "4.8",
        "unit": "TB/s",
        "range_basis": "H200 product page and DGX H200 system family",
        "source_refs": "[2]",
        "source_quality": "vendor_product_spec",
        "claim_type": "sourced_range",
        "used_in_existing_model": "M-COST-1 bandwidth-delay term",
        "recommended_model_mapping": "hbm_bandwidth_tbps",
        "notes": "Single product point; no deployment utilization claim.",
    },
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA DGX B200",
        "quantity": "per-GPU capacity",
        "range_low": "180",
        "range_high": "180",
        "unit": "GB",
        "range_basis": "1,440 GB total DGX B200 GPU memory divided by eight GPUs",
        "source_refs": "[3]",
        "source_quality": "vendor_system_spec",
        "claim_type": "derived_from_source",
        "used_in_existing_model": "future calibrated capacity-pressure sweep",
        "recommended_model_mapping": "hbm_capacity_per_gpu_gb",
        "notes": "Derived from system total because the cited page reports aggregate memory.",
    },
    {
        "tier": "HBM/GPU memory",
        "subtier": "NVIDIA DGX B200",
        "quantity": "per-GPU HBM bandwidth",
        "range_low": "8",
        "range_high": "8",
        "unit": "TB/s",
        "range_basis": "64 TB/s DGX B200 aggregate HBM bandwidth divided by eight GPUs",
        "source_refs": "[3]",
        "source_quality": "vendor_system_spec",
        "claim_type": "derived_from_source",
        "used_in_existing_model": "future calibrated bandwidth-delay sweep",
        "recommended_model_mapping": "hbm_bandwidth_tbps",
        "notes": "Derived arithmetic; do not use as measured application bandwidth.",
    },
    {
        "tier": "GPU-to-GPU fabric",
        "subtier": "DGX H100/H200 NVLink/NVSwitch",
        "quantity": "GPU-to-GPU bandwidth",
        "range_low": "900",
        "range_high": "900",
        "unit": "GB/s",
        "range_basis": "DGX H100/H200 user-guide component table",
        "source_refs": "[4]",
        "source_quality": "vendor_system_spec",
        "claim_type": "sourced_range",
        "used_in_existing_model": "M-COST-1 transfer term; M-QUEUE-1 migration pressure",
        "recommended_model_mapping": "gpu_fabric_bandwidth_gbps",
        "notes": "System fabric capability; path contention and topology effects are deferred.",
    },
    {
        "tier": "GPU-to-GPU fabric",
        "subtier": "DGX B200 NVLink/NVSwitch",
        "quantity": "aggregate NVLink bandwidth",
        "range_low": "14.4",
        "range_high": "14.4",
        "unit": "TB/s",
        "range_basis": "DGX B200 system specification",
        "source_refs": "[3]",
        "source_quality": "vendor_system_spec",
        "claim_type": "sourced_range",
        "used_in_existing_model": "future multi-GPU movement sweep",
        "recommended_model_mapping": "gpu_fabric_aggregate_bandwidth_tbps",
        "notes": "Aggregate system value; not directly comparable to per-link or per-GPU values.",
    },
    {
        "tier": "host CPU DRAM",
        "subtier": "AMD EPYC 9004/9005 class",
        "quantity": "socket memory bandwidth",
        "range_low": "460.8",
        "range_high": "576",
        "unit": "GB/s",
        "range_basis": "12 channels times DDR5-4800 to DDR5-6000 effective transfers times 8 bytes/channel",
        "source_refs": "[11]",
        "source_quality": "vendor_architecture_guide",
        "claim_type": "derived_from_source",
        "used_in_existing_model": "CPU DRAM tier bandwidth in M-COST-1",
        "recommended_model_mapping": "cpu_dram_bandwidth_gbps",
        "notes": "Theoretical peak from channel count and transfer rate; achieved STREAM-like bandwidth is deferred.",
    },
    {
        "tier": "host CPU DRAM",
        "subtier": "Intel Xeon 6 MRDIMM class",
        "quantity": "DIMM transfer rate",
        "range_low": "6400",
        "range_high": "8800",
        "unit": "MT/s",
        "range_basis": "Xeon 6 DDR5-6400 support and MRDIMM up to 8800 MT/s",
        "source_refs": "[10]",
        "source_quality": "vendor_solution_brief",
        "claim_type": "sourced_range",
        "used_in_existing_model": "CPU DRAM tier bandwidth sensitivity",
        "recommended_model_mapping": "cpu_dram_transfer_rate_mts",
        "notes": "Transfer-rate capability only; channel count and application bandwidth depend on platform.",
    },
    {
        "tier": "PCIe host link",
        "subtier": "PCIe 6.0 x16",
        "quantity": "raw link capability",
        "range_low": "256",
        "range_high": "256",
        "unit": "GB/s",
        "range_basis": "PCI-SIG PCIe 6.0 feature list for x16 configuration",
        "source_refs": "[5]",
        "source_quality": "standards_body_capability",
        "claim_type": "sourced_range",
        "used_in_existing_model": "host-device transfer ceiling",
        "recommended_model_mapping": "pcie_x16_capability_gbps",
        "notes": "Protocol capability; installed systems may use PCIe 5.0 or fewer lanes.",
    },
    {
        "tier": "CXL/pooled memory",
        "subtier": "CXL 2.0+ memory pooling",
        "quantity": "feature support",
        "range_low": "",
        "range_high": "",
        "unit": "capability",
        "range_basis": "CXL 2.0 support for switching, memory pooling, persistent memory, and link integrity/encryption",
        "source_refs": "[7] [14]",
        "source_quality": "standards_body_capability",
        "claim_type": "sourced_range",
        "used_in_existing_model": "CXL_or_pooled_memory tier semantics",
        "recommended_model_mapping": "cxl_pooling_available",
        "notes": "No public deployed latency-under-contention constant is used here.",
    },
    {
        "tier": "local NVMe",
        "subtier": "DGX H100/H200 data cache SSDs",
        "quantity": "system data-cache capacity",
        "range_low": "30.72",
        "range_high": "30.72",
        "unit": "TB",
        "range_basis": "8 x 3.84 TB NVMe U.2 SSD data-cache array",
        "source_refs": "[4]",
        "source_quality": "vendor_system_spec",
        "claim_type": "derived_from_source",
        "used_in_existing_model": "NVMe_local capacity tier",
        "recommended_model_mapping": "local_nvme_capacity_tb",
        "notes": "Capacity only; SSD bandwidth, latency distribution, and write endurance are deferred.",
    },
    {
        "tier": "NVMe-over-fabrics/remote storage",
        "subtier": "NVMe-oF transport scope",
        "quantity": "remote block-storage protocol support",
        "range_low": "",
        "range_high": "",
        "unit": "capability",
        "range_basis": "NVM Express specifications cover PCIe, RDMA, TCP, and other transports; NVMe-oF enables remote storage access",
        "source_refs": "[6]",
        "source_quality": "standards_body_capability",
        "claim_type": "sourced_range",
        "used_in_existing_model": "remote_object_store / NVMe remote tier distinction",
        "recommended_model_mapping": "remote_nvme_transport_available",
        "notes": "Capability row only; no latency, bandwidth, or tail distribution is inferred.",
    },
    {
        "tier": "durable workspace/object store",
        "subtier": "agent durable state",
        "quantity": "latency and consistency distribution",
        "range_low": "",
        "range_high": "",
        "unit": "deferred",
        "range_basis": "No public source in this cycle cleanly maps object-store behavior to durable agent workspace state",
        "source_refs": "[6]",
        "source_quality": "deferred_public_evidence_missing",
        "claim_type": "deferred_public_evidence_missing",
        "used_in_existing_model": "durable_workspace_store tier in M-COST-1 and M-PROTO-1",
        "recommended_model_mapping": "durable_workspace_latency_distribution",
        "notes": "Must remain deferred until measured production traces or reproducible benchmarks exist.",
    },
    {
        "tier": "semantic/prefix cache service",
        "subtier": "prefix and semantic cache",
        "quantity": "cache-reuse mechanism evidence",
        "range_low": "",
        "range_high": "",
        "unit": "capability",
        "range_basis": "PagedAttention, vLLM prefix caching, and semantic-cache papers demonstrate cache-reuse mechanisms",
        "source_refs": "[9] [12] [13]",
        "source_quality": "peer_reviewed_or_project_documentation",
        "claim_type": "sourced_range",
        "used_in_existing_model": "semantic_cache and prefix_cache object classes",
        "recommended_model_mapping": "cache_hit_rate_distribution",
        "notes": "Mechanism evidence only; production hit-rate distributions are deferred.",
    },
]


WORKLOAD_EVIDENCE = [
    {
        "evidence_id": "WE-001",
        "workload_class": "single-turn chat control",
        "memory_object": "weights; KV cache",
        "claim_type": "sourced_range",
        "claim_summary": "MLPerf Inference datacenter includes single-stream and server scenarios that model conventional request serving without durable agent trajectory state.",
        "source_refs": "[8]",
        "source_quality": "benchmark_specification",
        "applies_to_option": "A_conventional_request_model_kv_serving",
        "limitations": "Does not measure long-running agent state, branch/merge, or durable workspace reuse.",
        "model_implication": "Supports keeping Option A as the control path.",
    },
    {
        "evidence_id": "WE-002",
        "workload_class": "batch summarization/offline inference control",
        "memory_object": "weights; KV cache; intermediate scratch",
        "claim_type": "sourced_range",
        "claim_summary": "MLPerf offline sends all queries at the start and reports throughput without a latency constraint, matching the coarse batch/offline control abstraction.",
        "source_refs": "[8]",
        "source_quality": "benchmark_specification",
        "applies_to_option": "A_conventional_request_model_kv_serving",
        "limitations": "Offline throughput framing does not expose persistent non-KV object reuse.",
        "model_implication": "Strengthens the negative/control baseline in M-SCHED-1 and M-ARCH-1.",
    },
    {
        "evidence_id": "WE-003",
        "workload_class": "multi-turn chat; LLM serving",
        "memory_object": "KV cache",
        "claim_type": "sourced_range",
        "claim_summary": "PagedAttention reports near-zero KV-cache memory waste and 2-4x throughput improvement at similar latency over compared serving baselines.",
        "source_refs": "[9]",
        "source_quality": "peer_reviewed_systems_paper",
        "applies_to_option": "A_conventional_request_model_kv_serving; B_memory_object_aware_runtime",
        "limitations": "Paper focuses on KV paging/sharing, not durable agent trajectories.",
        "model_implication": "Confirms KV-cache placement and fragmentation are first-order calibration targets.",
    },
    {
        "evidence_id": "WE-004",
        "workload_class": "multi-turn chat; prompt-reuse serving",
        "memory_object": "prefix cache",
        "claim_type": "sourced_range",
        "claim_summary": "vLLM prefix caching uses KV blocks, hashes, reference counts, and optional cache salting for trusted reuse isolation.",
        "source_refs": "[12]",
        "source_quality": "project_documentation",
        "applies_to_option": "B_memory_object_aware_runtime",
        "limitations": "Project documentation is mechanism evidence, not a production hit-rate study.",
        "model_implication": "Maps directly to prefix-cache provenance and isolation fields in M-TRACE-1/M-PROTO-1.",
    },
    {
        "evidence_id": "WE-005",
        "workload_class": "RAG with retrieved-context reuse",
        "memory_object": "semantic cache entry; retrieved context",
        "claim_type": "sourced_range",
        "claim_summary": "Semantic-cache work reports embedding-backed reuse of LLM responses and up to 68.8% API-call reduction in its evaluated query categories.",
        "source_refs": "[13]",
        "source_quality": "arxiv_systems_experiment",
        "applies_to_option": "B_memory_object_aware_runtime",
        "limitations": "Response-level semantic caching is not identical to retrieved-context correctness and invalidation in RAG.",
        "model_implication": "Supports semantic-cache mechanism but keeps correctness/invalidation cost deferred.",
    },
    {
        "evidence_id": "WE-006",
        "workload_class": "tool-using research agent; code-agent loop",
        "memory_object": "tool output; durable workspace; trajectory log",
        "claim_type": "deferred_public_evidence_missing",
        "claim_summary": "No public source in this cycle cleanly measures production durable agent trajectory reuse distributions.",
        "source_refs": "[9] [12] [13]",
        "source_quality": "deferred_public_evidence_missing",
        "applies_to_option": "C_trajectory_dag_memory_fabric",
        "limitations": "Existing serving/cache sources are adjacent but do not measure branch-conditioned durable agent state.",
        "model_implication": "Keep M-PROTO-1 trajectory-value thresholds synthetic until trace evidence exists.",
    },
]


DEFERRED_CONSTANTS = [
    ("DC-001", "per-tier energy per byte moved or retained", "M-COST-1 energy proxy", "Public product pages rarely expose comparable per-byte energy by tier and workload.", "vendor power telemetry plus workload-level bytes moved, or peer-reviewed measurement", "Strengthens memory-centric placement if HBM/host/remote movement energy gaps are large.", "Weakens energy claims; leave only latency/capacity arguments.", "high", "Do not infer from board TDP."),
    ("DC-002", "real CXL memory latency under contention", "M-QUEUE-1 coordination overhead and CXL tier", "CXL standards expose capability, not deployed p50/p99 latency under multi-tenant pressure.", "reproducible CXL memory benchmark with contention and topology details", "Can reverse Option B/C if pooled memory adds high queueing delay.", "Makes CXL a stronger spill tier for warm objects.", "high", "Capability rows are present; latency is not."),
    ("DC-003", "remote object-store latency distributions for agent state", "M-COST-1 durable tier; M-PROTO-1 durable workspace", "Public storage claims do not map cleanly to agent workspace read/write and replay patterns.", "trace-backed object-store p50/p95/p99 by object size and consistency mode", "High tails make durable replay and trajectory checkpoints expensive.", "Low tails make pointer/offload paths more attractive.", "high", "Must include consistency semantics, not just object size."),
    ("DC-004", "semantic-cache correctness and invalidation cost", "M-COMP-1 safety model; M-PROTO-1 failure cases", "Semantic cache hit rates do not determine correctness under stale, poisoned, or user-isolated contexts.", "evaluation with cache-hit, false-positive, invalidation, and recovery metrics", "High cost pushes semantic cache toward exact provenance pointers.", "Low cost strengthens Option B for RAG-like workloads.", "high", "Security analysis should revisit this in M-SEC-1."),
    ("DC-005", "production agent trajectory reuse distribution", "M-LIFE-1 branch survival; M-QUEUE-1 DAG benefit", "Public serving benchmarks do not expose durable branch/merge/tool-output reuse over long agent runs.", "instrumented production or open benchmark traces with trajectory DAG events", "High reuse strengthens Option C despite coordination overhead.", "Low reuse collapses many agentic cases toward Option B or A.", "high", "Highest-risk missing evidence for the architecture thesis."),
    ("DC-006", "provenance-validation overhead", "M-COMP-1 summary-plus-pointer; M-PROTO-1 safety checks", "No general public constant covers validating source versions, cache salts, branch lineage, and replay pointers.", "measured validation microbenchmark plus end-to-end trace replay overhead", "High overhead can erase compression/offload value.", "Low overhead makes pointer-preserving compression safer to deploy.", "medium", "Ties directly to M-SEC-1 mitigations."),
]


MODEL_MAPPING = [
    ("hbm_capacity_per_gpu_gb", "M-COST-1 capacity_pressure; M-PROTO-1 HBM placement", "HBM/GPU memory capacity rows", "medium", "Large capacity increases delay before spilling but does not remove object-lifetime logic.", "public_range_ready"),
    ("hbm_bandwidth_tbps", "M-COST-1 bandwidth_delay", "HBM/GPU memory bandwidth rows", "medium", "Higher HBM bandwidth weakens movement-delay pressure but not capacity/provenance pressure.", "public_range_ready"),
    ("gpu_fabric_bandwidth_gbps", "M-COST-1 transfer; M-QUEUE-1 migration", "GPU-to-GPU fabric rows", "medium", "Low fabric bandwidth makes branch/state movement more expensive; high bandwidth makes placement more flexible.", "public_range_ready"),
    ("cpu_dram_bandwidth_gbps", "M-COST-1 CPU DRAM tier", "host CPU DRAM rows", "medium", "Higher CPU DRAM bandwidth strengthens warm-state spill tiers.", "derived_range_ready"),
    ("pcie_x16_capability_gbps", "host-device transfer ceiling", "PCIe host link row", "medium", "Low host link capability penalizes CPU/NVMe spill and migration.", "capability_only"),
    ("cxl_latency_under_contention", "M-QUEUE-1 queueing overhead", "deferred CXL latency constant", "high", "Can reverse pooled-memory conclusions.", "deferred"),
    ("semantic_cache_false_positive_cost", "M-COMP-1 correctness loss; M-PROTO-1 invalidation", "semantic cache evidence and deferred constants", "high", "Can reverse semantic-cache retention/offload choices.", "deferred"),
    ("trajectory_reuse_distribution", "M-LIFE-1; M-QUEUE-1; M-PROTO-1 Option C value", "deferred agent trajectory evidence", "high", "Most direct falsifier for Option C.", "deferred"),
]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def validate_rows(rows: list[dict[str, str]], refs: set[str]) -> None:
    for row in rows:
        if any("placeholder" in str(value).lower() or "replace_me" in str(value).lower() for value in row.values()):
            raise SystemExit(f"placeholder row survived: {row}")
        claim_type = row.get("claim_type", "")
        source_refs = row.get("source_refs", "")
        if claim_type != "synthetic_carryover" and not cite_ok(source_refs, refs):
            raise SystemExit(f"invalid or missing source_refs in row: {row}")
        if row.get("range_low") and not row.get("source_quality"):
            raise SystemExit(f"numeric row missing source_quality: {row}")


def build_model_mapping_rows() -> list[dict[str, str]]:
    return [
        {
            "model_variable": variable,
            "existing_model_location": location,
            "calibration_source": source,
            "reversal_risk": risk,
            "sensitivity_note": note,
            "calibration_status": status,
        }
        for variable, location, source, risk, note, status in MODEL_MAPPING
    ]


def build_source_quality_summary(all_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    counts = Counter((row.get("source_quality", ""), row.get("claim_type", "")) for row in all_rows)
    return [
        {
            "source_quality": quality,
            "claim_type": claim_type,
            "row_count": str(count),
        }
        for (quality, claim_type), count in sorted(counts.items())
    ]


def write_deferred(path: Path) -> None:
    rows = [
        {
            "constant_id": cid,
            "quantity_needed": quantity,
            "model_location": location,
            "reason_deferred": reason,
            "minimum_acceptable_source": source,
            "effect_if_high": high,
            "effect_if_low": low,
            "priority": priority,
            "notes": notes,
        }
        for cid, quantity, location, reason, source, high, low, priority, notes in DEFERRED_CONSTANTS
    ]
    write_csv(
        path,
        rows,
        [
            "constant_id",
            "quantity_needed",
            "model_location",
            "reason_deferred",
            "minimum_acceptable_source",
            "effect_if_high",
            "effect_if_low",
            "priority",
            "notes",
        ],
    )


def write_doc() -> None:
    counts_by_tier = defaultdict(int)
    for row in MEMORY_TIERS:
        counts_by_tier[row["tier"]] += 1
    high_risk = [row for row in build_model_mapping_rows() if row["reversal_risk"] == "high"]
    doc = f"""---
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

The generated table `data/calibration_memory_tiers.csv` covers {len(counts_by_tier)} tier categories: {", ".join(sorted(counts_by_tier))}. HBM/GPU rows anchor current public accelerator memory ranges: H100 reports 80-94 GB and 3.35-3.9 TB/s per GPU [1], H200 is represented as 141 GB and 4.8 TB/s [2][4], and DGX B200 aggregate figures derive to 180 GB and 8 TB/s per GPU from eight-GPU totals [3].

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

High-priority reversal risks are: {", ".join(row["model_variable"] for row in high_risk)}. A later calibrated run should substitute these variables into the existing models without overwriting the validated synthetic baselines.
"""
    DOC.write_text(doc)
    print(f"wrote {DOC.relative_to(ROOT)}")


def main() -> None:
    DATA.mkdir(exist_ok=True)
    refs = refs_available()
    validate_rows(MEMORY_TIERS, refs)
    validate_rows(WORKLOAD_EVIDENCE, refs)

    write_csv(
        DATA / "calibration_memory_tiers.csv",
        MEMORY_TIERS,
        [
            "tier",
            "subtier",
            "quantity",
            "range_low",
            "range_high",
            "unit",
            "range_basis",
            "source_refs",
            "source_quality",
            "claim_type",
            "used_in_existing_model",
            "recommended_model_mapping",
            "notes",
        ],
    )
    write_csv(
        DATA / "calibration_workload_evidence.csv",
        WORKLOAD_EVIDENCE,
        [
            "evidence_id",
            "workload_class",
            "memory_object",
            "claim_type",
            "claim_summary",
            "source_refs",
            "source_quality",
            "applies_to_option",
            "limitations",
            "model_implication",
        ],
    )
    write_deferred(DATA / "calibration_deferred_constants.csv")
    mapping = build_model_mapping_rows()
    write_csv(
        DATA / "calibration_model_mapping.csv",
        mapping,
        [
            "model_variable",
            "existing_model_location",
            "calibration_source",
            "reversal_risk",
            "sensitivity_note",
            "calibration_status",
        ],
    )
    summary = build_source_quality_summary(MEMORY_TIERS + WORKLOAD_EVIDENCE)
    write_csv(
        DATA / "calibration_source_quality_summary.csv",
        summary,
        ["source_quality", "claim_type", "row_count"],
    )
    write_doc()

    tier_count = len({row["tier"] for row in MEMORY_TIERS})
    evidence_count = len(WORKLOAD_EVIDENCE)
    if tier_count < 8:
        raise SystemExit(f"too few tier categories: {tier_count}")
    if evidence_count < 5:
        raise SystemExit(f"too few workload evidence rows: {evidence_count}")
    print(f"tier_categories={tier_count}")
    print(f"workload_evidence_rows={evidence_count}")
    print("validation=PASS")


if __name__ == "__main__":
    main()
