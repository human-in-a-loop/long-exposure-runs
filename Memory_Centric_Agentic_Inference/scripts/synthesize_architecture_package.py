# created: 2026-05-11T14:05:00Z
# cycle: 6
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ARCH-1

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROJECT = ROOT / "memory-centric-agentic"


INPUTS = [
    PROJECT / "memory_objects.csv",
    PROJECT / "workload_classes.csv",
    PROJECT / "lifetime_parameters.csv",
    PROJECT / "memory_tiers.csv",
    DATA / "cost_model_scenarios.csv",
    DATA / "sim_policy_results.csv",
    DATA / "sim_policy_object_breakdown.csv",
    DATA / "scheduling_regime_winners.csv",
    DATA / "scheduling_failure_modes.csv",
    DATA / "scheduling_special_cases.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"empty input: {path}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path} rows={len(rows)}")


def require_fields(name: str, rows: list[dict[str, str]], fields: set[str]) -> None:
    missing = fields - set(rows[0])
    if missing:
        raise SystemExit(f"{name} missing required columns: {sorted(missing)}")


def join_values(values: list[str]) -> str:
    return "; ".join(dict.fromkeys(v for v in values if v))


def main() -> None:
    for path in INPUTS:
        if not path.exists():
            raise SystemExit(f"missing input: {path}")

    memory_objects = read_csv(PROJECT / "memory_objects.csv")
    workloads = read_csv(PROJECT / "workload_classes.csv")
    tiers = read_csv(PROJECT / "memory_tiers.csv")
    scenarios = read_csv(DATA / "cost_model_scenarios.csv")
    sim_results = read_csv(DATA / "sim_policy_results.csv")
    sim_breakdown = read_csv(DATA / "sim_policy_object_breakdown.csv")
    sched_winners = read_csv(DATA / "scheduling_regime_winners.csv")
    sched_failures = read_csv(DATA / "scheduling_failure_modes.csv")
    sched_special = read_csv(DATA / "scheduling_special_cases.csv")

    require_fields("memory_objects", memory_objects, {"object_class", "placement_candidates", "compression_candidates", "eviction_failure_mode"})
    require_fields("workload_classes", workloads, {"workload_class", "dominant_memory_objects", "memory_centric_hypothesis", "falsification_signal"})
    require_fields("memory_tiers", tiers, {"tier", "persistence", "sharing_scope"})
    require_fields("scheduling_regime_winners", sched_winners, {"workload_class", "preferred_unit", "memory_centric_thesis", "dominant_object_class"})
    require_fields("sim_policy_results", sim_results, {"policy", "workload_class", "winning_policy_for_workload", "memory_centric_thesis", "dominant_object_class"})
    require_fields("sim_policy_object_breakdown", sim_breakdown, {"workload_class", "object_class"})
    require_fields("scheduling_failure_modes", sched_failures, {"workload_class", "scheduling_unit"})
    require_fields("scheduling_special_cases", sched_special, {"special_case", "collapse_or_persistence"})

    workload_by_name = {row["workload_class"]: row for row in workloads}
    object_by_class = {row["object_class"]: row for row in memory_objects}
    sched_by_workload = {row["workload_class"]: row for row in sched_winners}
    winner_policy = {}
    for row in sim_results:
        if row["policy"] == row["winning_policy_for_workload"]:
            winner_policy[row["workload_class"]] = row

    option_for_workload = {}
    for workload, row in sched_by_workload.items():
        unit = row["preferred_unit"]
        thesis = row["memory_centric_thesis"]
        if thesis == "weakened" or unit in {"request", "job", "model", "kernel", "cache_page"}:
            option_for_workload[workload] = "A_conventional_request_model_kv_serving"
        elif unit in {"context_segment", "memory_object"}:
            option_for_workload[workload] = "B_memory_object_aware_runtime"
        else:
            option_for_workload[workload] = "C_trajectory_dag_memory_fabric"

    option_specs = {
        "A_conventional_request_model_kv_serving": {
            "required_scheduler_unit": "model_or_cache_page",
            "required_visible_fields": "model_id; request_size; KV/prefix page id; aggregate memory pressure",
            "supported_objects": ["weights", "KV cache", "prefix cache", "intermediate scratch"],
            "benefit_mechanism": "preserves ordinary serving path; avoids coordination overhead when agentic state variables are not causal",
            "overhead_mechanism": "optional hooks only; full object/DAG tracking is unnecessary overhead for controls",
            "evidence_label": "simulated",
        },
        "B_memory_object_aware_runtime": {
            "required_scheduler_unit": "memory_object",
            "required_visible_fields": "object_id; object_class; size_units; reuse_probability; recompute_cost; correctness_sensitive; provenance pointer",
            "supported_objects": ["retrieved context", "semantic cache entry", "tool output", "prefix cache"],
            "benefit_mechanism": "captures context, semantic-cache, retrieved-context, and tool-output reuse before full trajectory structure is needed",
            "overhead_mechanism": "object registry, metadata propagation, provenance tracking, and per-object tiering decisions",
            "evidence_label": "simulated",
        },
        "C_trajectory_dag_memory_fabric": {
            "required_scheduler_unit": "agent_trajectory_dag",
            "required_visible_fields": "object fields plus branch_fanout; branch_survival; verifier_delay; durability_horizon; graph edge; merge/discard state",
            "supported_objects": ["tool output", "branch state", "verifier state", "trajectory log", "durable workspace", "KV cache"],
            "benefit_mechanism": "retains branch, verifier, trajectory-log, and durable workspace state when future reuse depends on run graph structure",
            "overhead_mechanism": "DAG metadata, cross-object consistency, durable state coordination, and stricter correctness-sensitive retention",
            "evidence_label": "simulated",
        },
    }

    option_rows = []
    for option, spec in option_specs.items():
        target_workloads = [w for w, o in option_for_workload.items() if o == option]
        objects = [sched_by_workload[w]["dominant_object_class"] for w in target_workloads]
        objects.extend(spec["supported_objects"])
        tiers_used = []
        for obj in objects:
            if obj in object_by_class:
                tiers_used.extend([x.strip() for x in object_by_class[obj]["placement_candidates"].split(";")])
        option_rows.append(
            {
                "architecture_option": option,
                "target_workloads": join_values(target_workloads),
                "required_scheduler_unit": spec["required_scheduler_unit"],
                "required_visible_fields": spec["required_visible_fields"],
                "tiers_used": join_values(tiers_used),
                "supported_objects": join_values(objects),
                "benefit_mechanism": spec["benefit_mechanism"],
                "overhead_mechanism": spec["overhead_mechanism"],
                "evidence_label": spec["evidence_label"],
            }
        )

    hook_specs = [
        ("object_registry", "runtime", "object_id; object_class; size_units", "all nontrivial regimes", "all memory objects", "M-TAX-1; M-SCHED-1", "placement collapses to aggregate request/model heuristics"),
        ("lifetime_boundary", "runtime+compiler", "lifetime_start; lifetime_end", "RAG; code-agent; verification-heavy; branch/merge", "KV cache; retrieved context; tool output; branch state; verifier state", "M-LIFE-1", "state is evicted before reuse or retained after value expires"),
        ("reuse_probability_estimator", "runtime", "reuse_probability; reuse_distance_driver", "RAG; prefix reuse; semantic cache; tool reuse", "prefix cache; retrieved context; tool output; semantic cache entry", "M-LIFE-1; M-SIM-1", "reuse-aware tiering cannot distinguish hot objects from dead state"),
        ("retention_value_estimator", "runtime", "reuse_probability; recompute_cost; loss_cost; residency_cost", "all options with caching beyond baseline", "all memory objects", "M-COST-1", "eviction policy optimizes bytes instead of retained value"),
        ("correctness_sensitive_pin", "runtime+storage", "correctness_sensitive; loss_cost; provenance pointer", "RAG; code-agent; verification-heavy; branch/merge", "retrieved context; tool output; verifier state; trajectory log; durable workspace", "M-COST-1; M-SIM-1", "scheduler treats correctness loss as latency-only recomputation"),
        ("durability_horizon", "runtime+storage", "durability_horizon; artifact_dependency_graph", "code-agent; long-running research; branch/merge", "tool output; trajectory log; durable workspace", "M-LIFE-1; M-SCHED-1", "workspace artifacts are archived, evicted, or summarized before downstream use"),
        ("branch_state_annotation", "compiler+runtime", "branch_fanout; branch_survival; merge_probability", "branch/merge; speculative agents", "branch state; KV cache; trajectory log", "M-LIFE-1; M-SCHED-1", "branch-local state is either overpinned or lost before merge"),
        ("verifier_retention_barrier", "compiler+runtime", "verifier_delay; validation_loop_id; candidate_id", "verification-heavy; code-agent; branch/merge", "verifier state; tool output; trajectory log", "M-SCHED-1", "counterexamples and test evidence are recomputed or omitted from final audit"),
        ("trajectory_graph_edge", "runtime+storage", "trajectory_id; parent_edge; merge_or_discard_state", "code-agent; verification-heavy; branch/merge", "branch state; verifier state; trajectory log; durable workspace", "M-SCHED-1", "object-local policy misses cross-object dependencies"),
        ("tier_placement_hint", "runtime", "tier_candidates; hotness; transfer_cost_proxy", "all options", "all memory objects", "M-COST-1; M-SIM-1", "objects move through tiers without exposing value/cost tradeoff"),
        ("compression_boundary", "compiler+runtime", "compression_candidate; summary_pointer; raw_pointer", "RAG; code-agent; durable workspace", "KV cache; retrieved context; tool output; trajectory log; durable workspace", "M-TAX-1", "summaries lose required provenance or raw state remains too expensive"),
        ("provenance_pointer", "storage+runtime", "source_uri; version; invalidation_signal", "RAG; tool agents; audits", "retrieved context; tool output; semantic cache entry; durable workspace", "M-TAX-1; M-SIM-1", "cache hits become stale, unverifiable, or semantically wrong"),
    ]

    hook_rows = []
    for hook in hook_specs:
        hook_rows.append(
            {
                "hook": hook[0],
                "owner": hook[1],
                "required_fields": hook[2],
                "workload_regimes": hook[3],
                "object_classes": hook[4],
                "evidence_source": hook[5],
                "failure_if_missing": hook[6],
            }
        )

    policy_rows = []
    for obj in memory_objects:
        cls = obj["object_class"]
        if cls in {"weights", "KV cache", "prefix cache"}:
            retention = "baseline hot residency while active; optional prefix reuse cache"
            recompute = "reload or recompute prefill"
            provenance = "model/version or prefix hash"
        elif cls in {"retrieved context", "semantic cache entry"}:
            retention = "reuse-aware object retention with source invalidation"
            recompute = "repeat retrieval/embedding or materialize cached semantic result"
            provenance = "corpus version, source pointer, confidence, invalidation signal"
        elif cls in {"tool output", "verifier state", "trajectory log", "durable workspace"}:
            retention = "correctness-sensitive durable retention with hot index"
            recompute = "rerun tool/test or replay trajectory when safe"
            provenance = "artifact dependency graph and raw-output pointer"
        elif cls == "branch state":
            retention = "branch-survival-weighted checkpoint retention"
            recompute = "refork branch or regenerate candidate when acceptable"
            provenance = "trajectory branch edge and merge/discard marker"
        else:
            retention = "short-lived scratch retention until substep completes"
            recompute = "rerun local substep"
            provenance = "substep id"
        policy_rows.append(
            {
                "object_class": cls,
                "tiering_strategy": obj["placement_candidates"],
                "retention_strategy": retention,
                "compression_strategy": obj["compression_candidates"],
                "recompute_strategy": recompute,
                "provenance_strategy": provenance,
                "eviction_failure_mode": obj["eviction_failure_mode"],
                "evidence_label": "derived",
            }
        )

    failure_rows = [
        {
            "failure_mode": "trajectory fabric required for controls",
            "affected_option": "C_trajectory_dag_memory_fabric",
            "trigger_condition": "single-turn or batch/offline controls select the trajectory/DAG option",
            "observable_symptom": "coordination overhead appears without retained-value gain",
            "falsification_test": "rerun scheduling comparison and verify controls prefer model/cache-page/request-class units",
            "mitigation": "make object/DAG hooks opt-in and retain conventional serving fast path",
        },
        {
            "failure_mode": "RAG overstated as trajectory evidence",
            "affected_option": "B_memory_object_aware_runtime; C_trajectory_dag_memory_fabric",
            "trigger_condition": "retrieved-context or semantic-cache reuse is represented as branch/verifier/durable value",
            "observable_symptom": "RAG requires branch fields despite no branch survival or verifier-delay driver",
            "falsification_test": "zero branch/verifier fields and check memory-object scheduling remains sufficient",
            "mitigation": "route RAG through object/context reuse hooks unless trajectory fields are observed",
        },
        {
            "failure_mode": "benefit reduces to KV cache scaling",
            "affected_option": "B_memory_object_aware_runtime; C_trajectory_dag_memory_fabric",
            "trigger_condition": "non-KV objects do not change winning policy or scheduling unit",
            "observable_symptom": "dominant object remains KV cache across agentic workloads",
            "falsification_test": "inspect object breakdown and require non-KV dominant objects for strengthened claims",
            "mitigation": "narrow claim to KV/page-centric serving and defer trajectory fabric",
        },
        {
            "failure_mode": "synthetic weights drive conclusion",
            "affected_option": "all",
            "trigger_condition": "small perturbations of cost/loss/reuse weights flip all agentic conclusions",
            "observable_symptom": "policy winners unstable without mechanism-specific reason",
            "falsification_test": "run sensitivity sweeps over reuse, correctness loss, tier costs, and coordination overhead",
            "mitigation": "calibrate with traces/hardware constants or report only qualitative mechanism boundaries",
        },
        {
            "failure_mode": "coordination overhead dominates retained value",
            "affected_option": "B_memory_object_aware_runtime; C_trajectory_dag_memory_fabric",
            "trigger_condition": "metadata, graph tracking, and tiering decisions cost more than avoided recompute/loss",
            "observable_symptom": "net architecture value negative for non-control workloads",
            "falsification_test": "measure metadata update rate, scheduler latency, and retained-value wins under real traces",
            "mitigation": "coarsen scheduling unit or use lazy metadata materialization",
        },
        {
            "failure_mode": "stale or incorrect semantic reuse",
            "affected_option": "B_memory_object_aware_runtime",
            "trigger_condition": "semantic cache lacks provenance, versioning, or invalidation signal",
            "observable_symptom": "cache hits return unsupported, outdated, or semantically mismatched state",
            "falsification_test": "inject corpus/version changes and require cache invalidation or correctness-sensitive pinning",
            "mitigation": "attach provenance pointers and confidence/invalidation fields to reusable objects",
        },
        {
            "failure_mode": "durable workspace becomes unbounded storage",
            "affected_option": "C_trajectory_dag_memory_fabric",
            "trigger_condition": "durability horizon and archive policy are absent",
            "observable_symptom": "workspace/log state grows with run length without retirement",
            "falsification_test": "sweep durable horizon and verify policy can archive cold dependencies without breaking replay",
            "mitigation": "use dependency-aware compaction, raw-pointer summaries, and tiered archival",
        },
    ]

    agenda_rows = [
        ("1", "Trace-calibrated object lifetime study", "measured", "M-TAX-1; M-LIFE-1", "whether object lifetimes are long/branch-conditioned in real agents", "converts symbolic lifetimes into empirical distributions"),
        ("2", "Coordination-overhead benchmark for object vs DAG scheduling", "prototype", "M-SCHED-1; M-ARCH-1", "whether metadata overhead erases retained value", "sets the practical boundary between options B and C"),
        ("3", "Retention-value policy sweep with calibrated tier costs", "measured+simulated", "M-COST-1; M-SIM-1", "whether synthetic tier ratios changed conclusions", "turns current score proxies into defensible cost/latency/energy claims"),
        ("4", "RAG semantic-cache correctness and invalidation experiment", "prototype", "M-TAX-1; M-SIM-1", "whether object reuse creates stale or wrong outputs", "tests the main failure mode of option B"),
        ("5", "Verification-state pinning experiment for code agents", "prototype", "M-SIM-1; M-SCHED-1", "whether verifier traces reduce repeated validation and missed counterexamples", "tests a concrete non-KV strengthened mechanism"),
        ("6", "Durable workspace compaction and replay benchmark", "prototype", "M-LIFE-1; M-ARCH-1", "whether summaries with raw pointers preserve reproducibility", "separates useful durable memory from uncontrolled log growth"),
        ("7", "Branch/merge scheduler stress test", "simulated+prototype", "M-LIFE-1; M-SCHED-1", "whether branch survival and merge probabilities justify DAG visibility", "validates the trajectory fabric only where branch futures matter"),
        ("8", "Compiler annotation pass for memory objects", "prototype", "M-TAX-1; M-ARCH-1", "whether planners can emit reliable lifetime/reuse/provenance metadata", "defines the compiler/runtime contract for memory-centric inference"),
        ("9", "Compression boundary study for KV/tool/trajectory state", "measured", "M-COST-1; M-ARCH-1", "whether compression loses correctness-critical provenance", "maps compression to object classes instead of byte streams"),
        ("10", "Multi-tenant queueing and preemption model", "derived+simulated", "M-SCHED-1; M-ARCH-1", "whether cluster scheduling interactions change option choice", "adds the deferred systems layer after memory boundaries are explicit"),
    ]
    research_rows = [
        {
            "rank": rank,
            "question_or_experiment": question,
            "expected_evidence_type": evidence,
            "dependency": dependency,
            "risk_retired": risk,
            "why_it_matters": why,
        }
        for rank, question, evidence, dependency, risk, why in agenda_rows
    ]

    option_fields = [
        "architecture_option",
        "target_workloads",
        "required_scheduler_unit",
        "required_visible_fields",
        "tiers_used",
        "supported_objects",
        "benefit_mechanism",
        "overhead_mechanism",
        "evidence_label",
    ]
    hook_fields = ["hook", "owner", "required_fields", "workload_regimes", "object_classes", "evidence_source", "failure_if_missing"]
    policy_fields = ["object_class", "tiering_strategy", "retention_strategy", "compression_strategy", "recompute_strategy", "provenance_strategy", "eviction_failure_mode", "evidence_label"]
    failure_fields = ["failure_mode", "affected_option", "trigger_condition", "observable_symptom", "falsification_test", "mitigation"]
    research_fields = ["rank", "question_or_experiment", "expected_evidence_type", "dependency", "risk_retired", "why_it_matters"]

    write_csv(DATA / "architecture_options.csv", option_rows, option_fields)
    write_csv(DATA / "runtime_compiler_hook_matrix.csv", hook_rows, hook_fields)
    write_csv(DATA / "architecture_policy_matrix.csv", policy_rows, policy_fields)
    write_csv(DATA / "architecture_failure_modes.csv", failure_rows, failure_fields)
    write_csv(DATA / "research_agenda_ranked.csv", research_rows, research_fields)

    control_options = {option_for_workload[w] for w in option_for_workload if "control" in w}
    if "C_trajectory_dag_memory_fabric" in control_options:
        raise SystemExit("control workload incorrectly requires trajectory DAG option")
    rag_option = option_for_workload.get("RAG with retrieved-context reuse")
    if rag_option != "B_memory_object_aware_runtime":
        raise SystemExit(f"RAG expected object-aware runtime, got {rag_option}")
    for workload in ["code-agent loop with tool outputs and durable workspace", "verification-heavy agent", "multi-agent branch/merge run"]:
        if option_for_workload.get(workload) != "C_trajectory_dag_memory_fabric":
            raise SystemExit(f"{workload} expected trajectory DAG fabric")


if __name__ == "__main__":
    main()
