#!/usr/bin/env python3
# created: 2026-05-11T18:35:00Z
# cycle: 14
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SYNTH-1
"""Build cross-milestone synthesis tables for memory-centric agentic inference."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC = ROOT / "memory-centric-agentic" / "final_synthesis.md"


OPTION_LABELS = {
    "A_conventional_request_model_kv_serving": "A",
    "B_memory_object_aware_runtime": "B",
    "C_trajectory_dag_memory_fabric": "C",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def by_key(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, str]]:
    return {row[key]: row for row in rows}


def canonical_workload(name: str) -> str:
    aliases = {
        "RAG with retrieved-context reuse": "RAG",
        "code-agent loop with tool outputs and durable workspace": "code-agent loop",
        "multi-agent branch/merge run": "multi-agent branch/merge",
    }
    return aliases.get(name, name)


def norm_option(option: str) -> str:
    return OPTION_LABELS.get(option, option)


def build_decision_matrix() -> list[dict[str, object]]:
    runtime = by_key(read_csv(DATA / "runtime_workload_summary.csv"), "workload_class")
    queue = by_key(read_csv(DATA / "queueing_architecture_winners.csv"), "workload_class")
    compression = by_key(read_csv(DATA / "compression_workload_summary.csv"), "workload_class")
    security = by_key(read_csv(DATA / "security_workload_summary.csv"), "workload_class")
    scheduling = {
        canonical_workload(row["workload_class"]): row
        for row in read_csv(DATA / "scheduling_regime_winners.csv")
    }

    rows: list[dict[str, object]] = []
    for workload in sorted(runtime):
        rt = runtime[workload]
        q = queue[workload]
        comp = compression[workload]
        sec = security[workload]
        sched = scheduling.get(workload, {})
        base = rt["runtime_architecture_option"]
        queue_option = q["moderate_overhead_winner"]
        retained_b = float(rt["option_b_net_value"])
        retained_c = float(rt["option_c_net_value"])
        sec_adjusted = float(sec["security_adjusted_value_proxy"])
        sec_reversal = sec["security_reversal"].lower() == "true"

        if comp["ordinary_control_boundary"].lower() == "true":
            compression_gate = "conventional_keep_hot_or_lossless"
        elif comp["rag_provenance_boundary"].lower() == "true":
            compression_gate = "provenance_preserving_lossless_or_pointer"
        else:
            compression_gate = "trajectory_safe_lossless_or_summary_pointer"

        if base.startswith("A_"):
            final = base
            positive = "none; branch, durable, and cross-request reuse variables collapse"
            reversal = "none; Option A remains dominant"
            falsification = "Show non-KV retained value with valid reuse/provenance signals and positive B/C net value on this workload."
        elif base.startswith("B_"):
            final = base
            positive = "object-local retrieved-context and semantic/prefix reuse with provenance/freshness checks"
            reversal = "security validation overhead and semantic-cache correctness/invalidation cost"
            falsification = "Measure semantic-cache false-positive/invalidation and provenance overhead high enough that Option B value stays negative under normal load."
        else:
            final = base
            positive = "branch survival, verifier retention, trajectory lineage, and durable workspace reuse"
            reversal = "security validation overhead, replay authorization, verifier integrity, durable latency tails, and DAG coordination"
            falsification = "Measure low production trajectory reuse or high DAG/security overhead so Option C loses to B/A across agentic traces."

        if q["high_object_overhead_winner"].startswith("A_") and not base.startswith("A_"):
            reversal += "; high object metadata/registry overhead reverses to A in M-QUEUE-1"
        if q["high_dag_overhead_winner"].startswith("B_") and base.startswith("C_"):
            reversal += "; high DAG overhead reverses C to B in M-QUEUE-1"
        if sec_reversal:
            option_with_security = f"{base}; synthetic_security_reversal_risk"
        else:
            option_with_security = base

        if final.startswith(("B_", "C_")) and max(retained_b, retained_c) <= 0:
            raise SystemExit(f"final memory-centric option lacks positive retained value: {workload}")
        if final.startswith(("B_", "C_")) and "missing" in option_with_security.lower():
            raise SystemExit(f"final memory-centric option has missing security gate: {workload}")

        claim_type = "validated_artifact"
        if sec_reversal or "synthetic" in sec["evidence_label"]:
            claim_type = "simulated"

        rows.append(
            {
                "workload_class": workload,
                "option_without_overheads": base,
                "option_with_queueing": queue_option,
                "option_with_compression": compression_gate,
                "option_with_security": option_with_security,
                "final_option": final,
                "dominant_positive_mechanism": positive,
                "dominant_reversal_mechanism": reversal,
                "claim_type": claim_type,
                "evidence_artifacts": "; ".join(
                    [
                        "data/runtime_workload_summary.csv",
                        "data/queueing_architecture_winners.csv",
                        "data/compression_workload_summary.csv",
                        "data/security_workload_summary.csv",
                        "data/scheduling_regime_winners.csv",
                    ]
                ),
                "falsification_test": falsification,
                "option_short": norm_option(final),
                "visible_retained_value_proxy": max(retained_b, retained_c),
                "security_adjusted_value_proxy": sec_adjusted,
                "scheduling_unit": sched.get("preferred_unit", ""),
            }
        )
    return rows


def build_research_agenda() -> list[dict[str, object]]:
    return [
        {
            "rank": 1,
            "experiment_id": "EXP-TRAJ-REUSE",
            "question": "Do production agent runs reuse trajectory, verifier, branch, and durable workspace state often enough to justify Option C?",
            "prototype_or_measurement": "instrumented trace collection",
            "target_audience": "AI infra; distributed systems; agent-runtime teams",
            "required_instrumentation": "trajectory_node_id; branch_id; verifier_id; durability_horizon; replay outcome",
            "expected_signal": "reuse-distance and branch-survival distributions over long agent runs",
            "would_support": "high reuse and correctness-sensitive replay preserve Option C value",
            "would_falsify": "near-zero trajectory reuse or short lifetimes collapse agentic workloads toward Option B/A",
            "depends_on_deferred_constant": "DC-005 production agent trajectory reuse distribution",
            "priority_rationale": "highest-risk missing evidence for the trajectory/DAG memory fabric",
        },
        {
            "rank": 2,
            "experiment_id": "EXP-PROV-OVERHEAD",
            "question": "What is the end-to-end cost of provenance, source-version, cache-salt, and lineage validation?",
            "prototype_or_measurement": "runtime microbenchmark plus trace replay",
            "target_audience": "runtime; compiler; security teams",
            "required_instrumentation": "provenance_id; source_version; invalidation_signal; cache_salt; lineage checks",
            "expected_signal": "validation overhead per reused object and per trajectory replay",
            "would_support": "low overhead makes pointer-preserving reuse practical",
            "would_falsify": "validation overhead exceeds retained value for RAG and agentic workloads",
            "depends_on_deferred_constant": "DC-006 provenance-validation overhead",
            "priority_rationale": "M-SEC-1 shows security overhead can reverse B/C under synthetic scoring",
        },
        {
            "rank": 3,
            "experiment_id": "EXP-SEMANTIC-CACHE-CORRECTNESS",
            "question": "How often do semantic-cache hits become stale, poisoned, tenant-invalid, or semantically false-positive?",
            "prototype_or_measurement": "RAG cache correctness benchmark",
            "target_audience": "RAG serving; database/search; security teams",
            "required_instrumentation": "query hash; source_version; invalidation_signal; tenant_scope; correctness label",
            "expected_signal": "hit rate, false-positive rate, invalidation rate, and recovery cost",
            "would_support": "low invalid-hit rate and cheap invalidation strengthen Option B",
            "would_falsify": "frequent stale/false-positive hits make semantic reuse unsafe or uneconomic",
            "depends_on_deferred_constant": "DC-004 semantic-cache correctness and invalidation cost",
            "priority_rationale": "decides whether RAG remains a strong object-runtime case",
        },
        {
            "rank": 4,
            "experiment_id": "EXP-QUEUE-HOTPATH",
            "question": "Where do object registry, policy, migration, verifier sync, and preemption queues saturate?",
            "prototype_or_measurement": "coordinated metadata-service load test",
            "target_audience": "serving infrastructure; OS/runtime; datacenter developers",
            "required_instrumentation": "registry ops; policy ops; migration events; verifier sync events; queue wait",
            "expected_signal": "service-time thresholds that reverse B/C to A/B",
            "would_support": "low metadata and DAG queueing overhead preserves memory-centric wins",
            "would_falsify": "hot-path metadata saturation erases retained value at realistic arrival rates",
            "depends_on_deferred_constant": "DC-002 real CXL memory latency under contention",
            "priority_rationale": "M-QUEUE-1 identifies registry and DAG coordination as first-order reversal mechanisms",
        },
        {
            "rank": 5,
            "experiment_id": "EXP-DURABLE-STORE-TAILS",
            "question": "Do durable workspace and object-store latency tails make replay/checkpoint paths too expensive?",
            "prototype_or_measurement": "durable agent-state read/write/replay benchmark",
            "target_audience": "storage; distributed systems; agent-platform teams",
            "required_instrumentation": "object size; consistency mode; p50/p95/p99 latency; replay dependency path",
            "expected_signal": "tail-latency distribution for durable state under agent access patterns",
            "would_support": "bounded tails make summary-plus-pointer and durable workspace reuse practical",
            "would_falsify": "high tails dominate retained value and force recompute or local-only retention",
            "depends_on_deferred_constant": "DC-003 remote object-store latency distributions for agent state",
            "priority_rationale": "durable state is central to Option C but uncalibrated",
        },
        {
            "rank": 6,
            "experiment_id": "EXP-COMPRESSION-RECOVERY",
            "question": "Can summary-plus-pointer representations recover exact state cheaply enough for correctness-sensitive replay?",
            "prototype_or_measurement": "compression/offload recovery benchmark",
            "target_audience": "compiler; runtime; storage teams",
            "required_instrumentation": "compression_strategy; pointer validity; reconstruction latency; validation result",
            "expected_signal": "byte savings versus reconstruction/metadata/provenance overhead",
            "would_support": "exact recovery or validated pointer paths reduce capacity pressure without unsafe reuse",
            "would_falsify": "recovery failures or overhead exceed byte movement savings",
            "depends_on_deferred_constant": "DC-006 provenance-validation overhead",
            "priority_rationale": "M-COMP-1 found no current queue-help rows and many unsafe lossy cases",
        },
        {
            "rank": 7,
            "experiment_id": "EXP-TRACE-SEC-FIELDS",
            "question": "Do security-grade trace fields catch unsafe reuse end to end?",
            "prototype_or_measurement": "trace v3 schema and invalid-fixture replay",
            "target_audience": "observability; security; runtime teams",
            "required_instrumentation": "tenant_scope; cache_salt; actor_id; replay_authorization_scope; verifier_evidence_hash; retention_hold_state",
            "expected_signal": "invalid fixture rejection and downgraded architecture decisions",
            "would_support": "unsafe reuse is observable before retained value is counted",
            "would_falsify": "missing fields allow stale, cross-tenant, or unauthorized reuse to score as beneficial",
            "depends_on_deferred_constant": "DC-006 provenance-validation overhead",
            "priority_rationale": "M-SEC-1 names required fields not present in trace v2",
        },
        {
            "rank": 8,
            "experiment_id": "EXP-CXL-CONTENTION",
            "question": "When does CXL or pooled memory help warm objects rather than adding queueing delay?",
            "prototype_or_measurement": "contention benchmark with object-tier placement",
            "target_audience": "hardware; OS; datacenter teams",
            "required_instrumentation": "tier placement; access size; contention level; p50/p99 latency",
            "expected_signal": "latency-under-contention curves for warm object spill tiers",
            "would_support": "predictable contention makes CXL a useful warm tier",
            "would_falsify": "contention tails make CXL worse than recompute/offload for reusable state",
            "depends_on_deferred_constant": "DC-002 real CXL memory latency under contention",
            "priority_rationale": "public CXL evidence is capability-level, not deployment-latency evidence",
        },
        {
            "rank": 9,
            "experiment_id": "EXP-PREFIX-CACHE-ISOLATION",
            "question": "Can prefix-cache reuse preserve tenant isolation and cache-salt boundaries without losing most hits?",
            "prototype_or_measurement": "serving cache A/B test with isolation instrumentation",
            "target_audience": "LLM serving; security teams",
            "required_instrumentation": "tenant_scope; cache_salt; prefix hash; hit/miss; blocked reuse reason",
            "expected_signal": "safe cache hit rate after isolation constraints",
            "would_support": "isolation-preserving cache reuse remains high",
            "would_falsify": "safe reuse rate collapses when tenant/cache-salt checks are enforced",
            "depends_on_deferred_constant": "DC-004 semantic-cache correctness and invalidation cost",
            "priority_rationale": "tests whether production safety constraints erase object-reuse wins",
        },
        {
            "rank": 10,
            "experiment_id": "EXP-ENERGY-BYTE-MOVED",
            "question": "Do memory-placement policies reduce measured energy per useful agent step?",
            "prototype_or_measurement": "telemetry-backed energy experiment",
            "target_audience": "GPU; datacenter; sustainability teams",
            "required_instrumentation": "bytes moved by tier; GPU/CPU/storage power telemetry; useful step count",
            "expected_signal": "energy per retained/reused object and per completed agent step",
            "would_support": "memory-aware placement lowers energy versus recompute/movement baselines",
            "would_falsify": "energy differences are noise or arithmetic dominates total energy",
            "depends_on_deferred_constant": "DC-001 per-tier energy per byte moved or retained",
            "priority_rationale": "energy/economics claims remain explicitly deferred without measurement",
        },
        {
            "rank": 11,
            "experiment_id": "EXP-COMPILER-ANNOTATIONS",
            "question": "Can compiler/runtime annotations expose memory objects without developer-heavy manual labeling?",
            "prototype_or_measurement": "annotation pass over agent traces",
            "target_audience": "compiler; framework; runtime teams",
            "required_instrumentation": "object_class; lifetime boundaries; provenance pointers; branch/verifier metadata",
            "expected_signal": "coverage and false annotation rate",
            "would_support": "automatic annotations recover causal memory variables with low error",
            "would_falsify": "manual annotations are required for most correctness-sensitive objects",
            "depends_on_deferred_constant": "DC-006 provenance-validation overhead",
            "priority_rationale": "turns the architecture proposal into a usable programming model",
        },
        {
            "rank": 12,
            "experiment_id": "EXP-ABLATION-REPLAY",
            "question": "Do ablations of provenance/reuse and branch/verifier/durable fields reproduce architecture collapse on real traces?",
            "prototype_or_measurement": "runtime prototype replay over public or production traces",
            "target_audience": "AI infra; systems researchers",
            "required_instrumentation": "all trace v2 fields plus M-SEC-1 security fields",
            "expected_signal": "B to A and C to B/A collapses when causal fields are hidden",
            "would_support": "mechanism causality seen in M-PROTO-1 generalizes",
            "would_falsify": "architecture choices do not change when claimed causal fields are removed",
            "depends_on_deferred_constant": "DC-005 production agent trajectory reuse distribution",
            "priority_rationale": "directly validates the object/trajectory causal boundary",
        },
    ]


def build_claims() -> list[dict[str, object]]:
    return [
        {
            "claim_id": "CL-001",
            "claim": "Control workloads with no durable, branch, or cross-request reuse variables collapse to conventional Option A serving.",
            "claim_type": "validated_artifact",
            "supporting_artifacts": "data/runtime_workload_summary.csv; data/queueing_architecture_winners.csv; data/scheduling_regime_winners.csv",
            "assumptions": "single-turn and batch/offline controls have zero material DAG dependence",
            "falsification_condition": "A control trace shows positive non-KV retained value and valid reuse that beats Option A under overheads.",
            "risk_level": "low",
        },
        {
            "claim_id": "CL-002",
            "claim": "RAG-like workloads justify Option B when retrieved-context, semantic-cache, or prefix reuse survives provenance and freshness checks.",
            "claim_type": "simulated",
            "supporting_artifacts": "data/runtime_workload_summary.csv; data/compression_workload_summary.csv; data/security_workload_summary.csv",
            "assumptions": "semantic-cache correctness and invalidation costs are not calibrated",
            "falsification_condition": "Measured stale/false-positive or validation costs make safe object reuse consistently negative.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-003",
            "claim": "Option C is justified only when branch survival, verifier state, trajectory logs, and durable workspace state create retained value after coordination costs.",
            "claim_type": "simulated",
            "supporting_artifacts": "data/runtime_workload_summary.csv; data/queueing_architecture_winners.csv; data/security_workload_summary.csv",
            "assumptions": "production trajectory reuse distribution is deferred",
            "falsification_condition": "Production traces show low trajectory reuse or high DAG overhead so C loses to B/A.",
            "risk_level": "high",
        },
        {
            "claim_id": "CL-004",
            "claim": "High object-registry overhead can reverse both Option B and C to Option A.",
            "claim_type": "simulated",
            "supporting_artifacts": "data/queueing_architecture_winners.csv; memory-centric-agentic/queueing_model.md",
            "assumptions": "M-QUEUE-1 uses synthetic service-time multipliers",
            "falsification_condition": "Measured metadata services remain below reversal thresholds at target load.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-005",
            "claim": "High DAG/verifier/durable coordination overhead can reverse Option C to Option B.",
            "claim_type": "simulated",
            "supporting_artifacts": "data/queueing_architecture_winners.csv",
            "assumptions": "DAG synchronization, verifier sync, durable consistency, and preemption costs are synthetic",
            "falsification_condition": "Measured DAG coordination overhead is small relative to branch/verifier retained value.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-006",
            "claim": "Compression/offload must be representation-safe before byte savings are counted.",
            "claim_type": "validated_artifact",
            "supporting_artifacts": "data/compression_safety_failures.csv; data/compression_best_strategy_by_object.csv; memory-centric-agentic/compression_model.md",
            "assumptions": "correctness-sensitive lossy state requires pointer, validation, or exact recovery",
            "falsification_condition": "A lossy strategy without recovery preserves correctness across replay/merge/verification fixtures.",
            "risk_level": "low",
        },
        {
            "claim_id": "CL-007",
            "claim": "Current compression/offload settings do not preserve queue thresholds under synthetic coefficients.",
            "claim_type": "simulated",
            "supporting_artifacts": "data/compression_object_queue_interactions.csv; data/compression_queue_interactions.csv",
            "assumptions": "reconstruction and metadata overhead coefficients are synthetic",
            "falsification_condition": "Measured reconstruction/metadata costs are low enough to create positive object-level queue relief.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-008",
            "claim": "Public sources calibrate HBM capacity/bandwidth, fabric capability, PCIe capability, and some workload/cache mechanisms, but not core agentic reuse distributions.",
            "claim_type": "sourced",
            "supporting_artifacts": "REFERENCES.md; data/calibration_memory_tiers.csv; data/calibration_workload_evidence.csv; data/calibration_deferred_constants.csv",
            "assumptions": "vendor and standards data are capability evidence, not workload-achieved measurements",
            "falsification_condition": "Public or reproducible traces provide calibrated trajectory reuse, security overhead, and durable latency constants.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-009",
            "claim": "Security validation is part of architecture selection, not an add-on.",
            "claim_type": "validated_artifact",
            "supporting_artifacts": "data/security_workload_summary.csv; data/security_invalid_trace_fixtures.csv; memory-centric-agentic/security_provenance_model.md",
            "assumptions": "unsafe reuse must not receive positive retained value",
            "falsification_condition": "A design safely reuses objects without provenance, freshness, isolation, lineage, verifier, or retention checks.",
            "risk_level": "low",
        },
        {
            "claim_id": "CL-010",
            "claim": "Trace v2 is sufficient for lifetime/reuse/DAG analysis but not production-grade security.",
            "claim_type": "validated_artifact",
            "supporting_artifacts": "memory-centric-agentic/trace_schema.md; data/security_invalid_trace_fixtures.csv",
            "assumptions": "tenant scope, cache salt, replay authorization, verifier hash, and retention hold are required security fields",
            "falsification_condition": "Production security review shows trace v2 fields alone can enforce all required reuse gates.",
            "risk_level": "medium",
        },
        {
            "claim_id": "CL-011",
            "claim": "The architecture rule is to expose the coarsest state boundary that preserves causal retained-value variables.",
            "claim_type": "derived",
            "supporting_artifacts": "memory-centric-agentic/architecture_proposal.md; data/synthesis_architecture_decision_matrix.csv",
            "assumptions": "coordination, validation, and compression overheads are subtracted before choosing a richer boundary",
            "falsification_condition": "Fine-grained state visibility wins even when causal variables are zero or hidden.",
            "risk_level": "low",
        },
        {
            "claim_id": "CL-012",
            "claim": "The strongest unresolved memory-centric claim is economic and energy value, because per-tier energy and pricing are not calibrated.",
            "claim_type": "speculative",
            "supporting_artifacts": "data/calibration_deferred_constants.csv; memory-centric-agentic/cost_model.md",
            "assumptions": "DC-001 per-tier energy per byte moved or retained remains missing",
            "falsification_condition": "Telemetry shows placement/reuse energy savings are negligible relative to arithmetic and system overhead.",
            "risk_level": "high",
        },
    ]


def build_open_risks() -> list[dict[str, object]]:
    risks = [
        ("R-001", "semantic-cache correctness/invalidation", "DC-004", "Can erase Option B value for RAG-like workloads."),
        ("R-002", "production trajectory reuse", "DC-005", "Decides whether Option C is a real production architecture or synthetic artifact."),
        ("R-003", "provenance-validation overhead", "DC-006", "Can reverse both B and C even when reuse exists."),
        ("R-004", "durable object-store latency tails", "DC-003", "Can make checkpoint/replay/pointer paths too slow."),
        ("R-005", "tenant/cache salt instrumentation", "M-SEC-1 required new trace fields", "Unsafe cross-tenant reuse cannot be distinguished without it."),
        ("R-006", "replay authorization", "M-SEC-1 required new trace fields", "Trajectory replay value is invalid without actor/scope authorization."),
        ("R-007", "verifier evidence hash", "M-SEC-1 required new trace fields", "Verifier state can be tampered with unless evidence is bound to replay."),
        ("R-008", "retention hold state", "M-SEC-1 required new trace fields", "Durable deletion/audit conflicts can invalidate retained state."),
        ("R-009", "queue hot-path overhead", "M-QUEUE-1 reversal thresholds", "Registry, policy, migration, DAG, verifier, and preemption queues can dominate value."),
        ("R-010", "compression safety/recovery", "M-COMP-1 safety failures", "Lossy summaries can corrupt correctness-sensitive replay without exact recovery."),
        ("R-011", "CXL contention latency", "DC-002", "Capability-level CXL evidence is not enough for warm-tier placement decisions."),
        ("R-012", "per-tier energy per byte", "DC-001", "Energy/economics claims remain speculative without telemetry."),
    ]
    return [
        {
            "risk_id": rid,
            "risk": risk,
            "missing_measurement_or_field": missing,
            "affected_architecture_option": "B/C" if rid not in {"R-011", "R-012"} else "A/B/C",
            "why_it_matters": why,
            "current_status": "deferred_or_synthetic",
            "next_experiment": f"See synthesis_research_agenda.csv for experiments targeting {missing}.",
        }
        for rid, risk, missing, why in risks
    ]


def validate_outputs(decision_rows: list[dict[str, object]], claims: list[dict[str, object]]) -> None:
    for row in decision_rows:
        serialized = " ".join(str(v) for v in row.values()).lower()
        if "placeholder" in serialized or "replace_me" in serialized:
            raise SystemExit("placeholder text found in decision matrix")
    for claim in claims:
        for field in ["claim_type", "supporting_artifacts", "falsification_condition"]:
            if not str(claim.get(field, "")).strip():
                raise SystemExit(f"claim {claim.get('claim_id')} missing {field}")
        if claim["claim_type"] == "speculative" and "DC-" not in claim["assumptions"]:
            raise SystemExit(f"speculative claim lacks deferred constant: {claim['claim_id']}")
    if not any(str(row["final_option"]).startswith("A_") for row in decision_rows):
        raise SystemExit("missing Option A control regime")
    if not any(str(row["final_option"]).startswith("B_") for row in decision_rows):
        raise SystemExit("missing Option B regime")
    if not any(str(row["final_option"]).startswith("C_") for row in decision_rows):
        raise SystemExit("missing Option C regime")


def write_doc(decision: list[dict[str, object]], agenda: list[dict[str, object]], claims: list[dict[str, object]]) -> None:
    frontmatter = """---
created: 2026-05-11T18:35:00Z
cycle: 14
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-SYNTH-1
---
"""
    lines = [
        frontmatter,
        "# Final Synthesis: Memory-Centric Architecture for Agentic LLM Inference",
        "",
        "## Thesis",
        "",
        "`validated_artifact` The architecture should expose memory state only at the coarsest boundary that preserves causal retained-value variables. Conventional request/model/KV serving remains the right baseline for controls; object-aware runtime is justified for reusable retrieved context, semantic cache entries, and prefix state; trajectory/DAG memory fabric is justified only when branch survival, verifier state, trajectory logs, or durable workspace state survive queueing, compression, calibration, and security gates.",
        "",
        "ArchitectureChoice(w) = argmax over A/B/C of visible retained value plus movement/correctness benefit minus coordination, compression/recovery, validation, and expected security loss, subject to authorized reuse for every retained object.",
        "",
        "## Decision Rule",
        "",
        "`derived` Option A wins when branch, durable, verifier, and cross-request reuse variables are zero or when coordination/security overhead dominates. `simulated` Option B wins for RAG-like object reuse when provenance, source freshness, tenant/cache isolation, and invalidation checks pass. `simulated` Option C wins for agentic branch/verify/durable workloads only when trajectory lineage, replay authorization, verifier integrity, and retention constraints pass.",
        "",
        "## Workload Conclusions",
        "",
        "| Workload | Final option | Main positive mechanism | Main reversal risk |",
        "|---|---:|---|---|",
    ]
    for row in decision:
        lines.append(
            f"| {row['workload_class']} | {norm_option(str(row['final_option']))} | "
            f"{row['dominant_positive_mechanism']} | {row['dominant_reversal_mechanism']} |"
        )
    lines.extend(
        [
            "",
            "![Final Option A/B/C decision by workload after queueing, compression, calibration, and security gates.](../data/synthesis_architecture_matrix.png)",
            "",
            "## Robust Conclusions",
            "",
            "- `validated_artifact` Control workloads remain Option A across runtime, queueing, compression, and security outputs.",
            "- `validated_artifact` Unsafe reuse must be downgraded or rejected before retained value is counted.",
            "- `derived` The scheduling unit is an information boundary: model/request is enough for controls, memory object is enough for RAG-style reuse, and trajectory/DAG is needed only for branch/verifier/durable dependencies.",
            "- `validated_artifact` Compression is a representation-safety decision before it is a byte-saving decision.",
            "",
            "## Sensitive Conclusions",
            "",
            "- `simulated` Option B depends on semantic-cache correctness, invalidation, provenance, and tenant/cache-salt overhead.",
            "- `simulated` Option C depends on production trajectory reuse, verifier-state value, branch survival, durable-store latency tails, and DAG coordination overhead.",
            "- `simulated` Queueing can reverse richer memory-centric boundaries when registry, metadata, DAG, verifier, or preemption queues saturate.",
            "",
            "## Speculative Or Deferred Conclusions",
            "",
            "- `speculative` Energy and economics remain unresolved until per-tier energy-per-byte and cost telemetry are measured.",
            "- `speculative` Durable multi-agent trajectory reuse remains uncalibrated without production or reproducible open traces.",
            "- `speculative` CXL/pooled memory is a capability tier in the current package, not a proven low-latency warm-object tier under contention.",
            "",
            "## Top Experiments",
            "",
        ]
    )
    for row in agenda[:10]:
        lines.append(
            f"{row['rank']}. `{row['experiment_id']}` — {row['question']} "
            f"Falsifies if: {row['would_falsify']}"
        )
    lines.extend(
        [
            "",
            "![Ranked prototype/research experiments by priority and uncertainty reduction.](../data/synthesis_agenda_priority.png)",
            "",
            "## Claims and Falsification",
            "",
        ]
    )
    for claim in claims:
        lines.append(
            f"- `{claim['claim_type']}` `{claim['claim_id']}` {claim['claim']} "
            f"Falsification: {claim['falsification_condition']}"
        )
    lines.extend(
        [
            "",
            "![Robust, sensitive, and speculative claims mapped against falsification difficulty.](../data/synthesis_claim_risk_map.png)",
            "",
            "## Open Risks",
            "",
            "`validated_artifact` The unresolved risks are recorded in `data/synthesis_open_risks.csv`. The highest-priority missing measurements are production trajectory reuse, provenance-validation overhead, semantic-cache correctness/invalidation cost, durable object-store latency tails, queue hot-path overhead, CXL contention latency, and per-tier energy per byte.",
        ]
    )
    DOC.write_text("\n".join(lines) + "\n")
    print(f"wrote {DOC.relative_to(ROOT)}")


def main() -> None:
    decision = build_decision_matrix()
    agenda = build_research_agenda()
    claims = build_claims()
    risks = build_open_risks()
    validate_outputs(decision, claims)

    write_csv(
        DATA / "synthesis_architecture_decision_matrix.csv",
        [
            "workload_class",
            "option_without_overheads",
            "option_with_queueing",
            "option_with_compression",
            "option_with_security",
            "final_option",
            "dominant_positive_mechanism",
            "dominant_reversal_mechanism",
            "claim_type",
            "evidence_artifacts",
            "falsification_test",
            "option_short",
            "visible_retained_value_proxy",
            "security_adjusted_value_proxy",
            "scheduling_unit",
        ],
        decision,
    )
    write_csv(
        DATA / "synthesis_research_agenda.csv",
        [
            "rank",
            "experiment_id",
            "question",
            "prototype_or_measurement",
            "target_audience",
            "required_instrumentation",
            "expected_signal",
            "would_support",
            "would_falsify",
            "depends_on_deferred_constant",
            "priority_rationale",
        ],
        agenda,
    )
    write_csv(
        DATA / "synthesis_claims_register.csv",
        [
            "claim_id",
            "claim",
            "claim_type",
            "supporting_artifacts",
            "assumptions",
            "falsification_condition",
            "risk_level",
        ],
        claims,
    )
    write_csv(
        DATA / "synthesis_open_risks.csv",
        [
            "risk_id",
            "risk",
            "missing_measurement_or_field",
            "affected_architecture_option",
            "why_it_matters",
            "current_status",
            "next_experiment",
        ],
        risks,
    )
    write_doc(decision, agenda, claims)
    print("validation=PASS")


if __name__ == "__main__":
    main()
