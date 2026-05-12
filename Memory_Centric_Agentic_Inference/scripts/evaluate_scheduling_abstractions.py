# created: 2026-05-11T13:45:00Z
# cycle: 5
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SCHED-1

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PROJECT = ROOT / "memory-centric-agentic"

EVENTS = DATA / "sim_workload_events.csv"
POLICY_RESULTS = DATA / "sim_policy_results.csv"
OBJECT_BREAKDOWN = DATA / "sim_policy_object_breakdown.csv"
SIM_SPECIAL_CASES = DATA / "sim_special_cases.csv"
MEMORY_OBJECTS = PROJECT / "memory_objects.csv"
WORKLOAD_CLASSES = PROJECT / "workload_classes.csv"

COMPARISON_OUT = DATA / "scheduling_unit_comparison.csv"
WINNERS_OUT = DATA / "scheduling_regime_winners.csv"
FAILURES_OUT = DATA / "scheduling_failure_modes.csv"
SPECIAL_OUT = DATA / "scheduling_special_cases.csv"

UNITS = [
    "request",
    "job",
    "kernel",
    "model",
    "cache_page",
    "context_segment",
    "memory_object",
    "agent_trajectory_dag",
]

UNIT_FIELDS = {
    "request": {"size_units", "workload_class"},
    "job": {"size_units", "workload_class", "durability_horizon"},
    "kernel": {"size_units"},
    "model": {"size_units", "object_class"},
    "cache_page": {"size_units", "object_class", "reuse_probability"},
    "context_segment": {"size_units", "object_class", "reuse_probability", "recompute_cost"},
    "memory_object": {
        "size_units",
        "object_class",
        "reuse_probability",
        "recompute_cost",
        "loss_cost",
        "correctness_sensitive",
        "durability_horizon",
    },
    "agent_trajectory_dag": {
        "size_units",
        "object_class",
        "reuse_probability",
        "recompute_cost",
        "loss_cost",
        "correctness_sensitive",
        "durability_horizon",
        "branch_fanout",
        "branch_survival",
        "verifier_delay",
    },
}

OVERHEAD = {
    "request": 0.03,
    "job": 0.04,
    "kernel": 0.08,
    "model": 0.05,
    "cache_page": 0.10,
    "context_segment": 0.12,
    "memory_object": 0.18,
    "agent_trajectory_dag": 0.28,
}

OBJECT_NEEDS = {
    "weights": {"size_units", "object_class"},
    "KV cache": {"size_units", "object_class", "reuse_probability"},
    "prefix cache": {"size_units", "object_class", "reuse_probability"},
    "retrieved context": {"object_class", "reuse_probability", "recompute_cost", "correctness_sensitive", "loss_cost"},
    "semantic cache entry": {"object_class", "reuse_probability", "recompute_cost", "correctness_sensitive", "loss_cost"},
    "tool output": {"object_class", "reuse_probability", "recompute_cost", "correctness_sensitive", "loss_cost", "durability_horizon"},
    "intermediate scratch": {"size_units", "object_class"},
    "branch state": {"object_class", "reuse_probability", "branch_fanout", "branch_survival", "verifier_delay", "loss_cost"},
    "verifier state": {"object_class", "reuse_probability", "verifier_delay", "correctness_sensitive", "loss_cost"},
    "trajectory log": {"object_class", "reuse_probability", "branch_survival", "verifier_delay", "durability_horizon", "correctness_sensitive", "loss_cost"},
    "durable workspace": {"object_class", "reuse_probability", "durability_horizon", "correctness_sensitive", "loss_cost"},
}

AGENTIC_OBJECTS = {"tool output", "branch state", "verifier state", "trajectory log", "durable workspace"}
CONTEXT_OBJECTS = {"KV cache", "prefix cache", "retrieved context", "semantic cache entry"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def require_columns(rows: list[dict[str, str]], path: Path, columns: set[str]) -> None:
    if not rows:
        raise SystemExit(f"empty input: {path}")
    missing = columns - set(rows[0])
    if missing:
        raise SystemExit(f"{path} missing columns: {sorted(missing)}")


def f(row: dict[str, str], key: str) -> float:
    return float(row[key])


def workload_stats(events: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    stats: dict[str, dict[str, float]] = {}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        grouped[row["workload_class"]].append(row)

    for workload, rows in grouped.items():
        total_size = sum(f(r, "size_units") for r in rows) or 1.0
        weighted = lambda key: sum(f(r, key) * f(r, "size_units") for r in rows) / total_size
        object_sizes: dict[str, float] = defaultdict(float)
        for row in rows:
            object_sizes[row["object_class"]] += f(row, "size_units")
        dominant = max(object_sizes.items(), key=lambda item: item[1])[0]
        stats[workload] = {
            "size_units": total_size,
            "reuse": weighted("reuse_probability"),
            "branch": weighted("branch_survival"),
            "verifier": weighted("verifier_delay"),
            "durability": weighted("durability_horizon"),
            "correctness": weighted("correctness_sensitive"),
            "recompute": weighted("recompute_cost"),
            "loss": weighted("loss_cost"),
            "dominant_by_size": dominant,
        }
    return stats


def winner_rows(policy_results: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for row in policy_results:
        if row["policy"] == row["winning_policy_for_workload"]:
            rows[row["workload_class"]] = row
    return rows


def positive_contributions(object_breakdown: list[dict[str, str]], winners: dict[str, dict[str, str]]) -> dict[str, dict[str, float]]:
    by_workload: dict[str, dict[str, float]] = defaultdict(dict)
    for row in object_breakdown:
        workload = row["workload_class"]
        if workload not in winners or row["policy"] != winners[workload]["winning_policy_for_workload"]:
            continue
        by_workload[workload][row["object_class"]] = float(row["total_score_contribution"])
    return by_workload


def required_fields_for_workload(events: list[dict[str, str]], workload: str, contributions: dict[str, float]) -> tuple[set[str], str]:
    rows = [row for row in events if row["workload_class"] == workload]
    positive_objects = {obj for obj, value in contributions.items() if value > 0}
    if not positive_objects:
        sizes: dict[str, float] = defaultdict(float)
        for row in rows:
            sizes[row["object_class"]] += f(row, "size_units")
        positive_objects = {max(sizes.items(), key=lambda item: item[1])[0]}
    required: set[str] = set()
    for obj in positive_objects:
        required |= OBJECT_NEEDS.get(obj, {"object_class", "size_units"})
    dominant_object = max(contributions.items(), key=lambda item: item[1])[0] if contributions else ""
    return required, dominant_object


def score_unit(unit: str, stats: dict[str, float], required: set[str], dominant_object: str) -> dict[str, float]:
    visible = UNIT_FIELDS[unit]
    alignment = len(required & visible) / len(required) if required else 1.0
    movement = 1.0 if unit in {"model", "cache_page", "context_segment", "memory_object", "agent_trajectory_dag"} else 0.45
    if dominant_object in AGENTIC_OBJECTS and unit in {"request", "job", "kernel", "model", "cache_page", "context_segment"}:
        movement *= 0.75
    reuse = stats["reuse"] if "reuse_probability" in visible else stats["reuse"] * 0.25
    branch = min(1.0, stats["branch"] * 2.5 + stats["verifier"] / 8.0) if {"branch_survival", "verifier_delay"} & visible else 0.0
    durability = min(1.0, stats["durability"] / 8.0) if "durability_horizon" in visible else 0.0
    correctness = min(1.0, stats["correctness"] + stats["loss"] / 50.0) if {"correctness_sensitive", "loss_cost"} <= visible else 0.0

    total = (
        0.30 * alignment
        + 0.15 * movement
        + 0.15 * reuse
        + 0.15 * branch
        + 0.12 * durability
        + 0.18 * correctness
        - OVERHEAD[unit]
    )
    return {
        "alignment_score": alignment,
        "movement_avoidance_score": movement,
        "reuse_capture_score": reuse,
        "branch_capture_score": branch,
        "durability_capture_score": durability,
        "correctness_capture_score": correctness,
        "coordination_overhead_score": OVERHEAD[unit],
        "total_score": total,
    }


def mechanism_label(required: set[str], dominant_object: str) -> str:
    if {"branch_survival", "verifier_delay"} & required:
        return "trajectory_branch_verifier_boundary"
    if "durability_horizon" in required:
        return "durable_object_boundary"
    if dominant_object in CONTEXT_OBJECTS and "reuse_probability" in required:
        return "context_reuse_boundary"
    return "coarse_serving_boundary"


def thesis_label(unit: str, workload: str, mechanism: str) -> str:
    if "control" in workload:
        return "weakened"
    if mechanism == "context_reuse_boundary":
        return "ambiguous"
    if unit in {"memory_object", "agent_trajectory_dag"} and mechanism != "coarse_serving_boundary":
        return "strengthened"
    return "ambiguous"


def failure_reason(unit: str, required: set[str], dominant_object: str) -> str:
    missing = sorted(required - UNIT_FIELDS[unit])
    if not missing:
        return ""
    if {"branch_survival", "verifier_delay"} & set(missing):
        return f"{unit} cannot observe branch/verifier lifetime fields for {dominant_object}"
    if "durability_horizon" in missing:
        return f"{unit} cannot observe durable-horizon retention for {dominant_object}"
    if {"correctness_sensitive", "loss_cost"} & set(missing):
        return f"{unit} cannot observe correctness-sensitive eviction loss for {dominant_object}"
    if "reuse_probability" in missing:
        return f"{unit} cannot observe reuse probability for {dominant_object}"
    return f"{unit} misses required fields {','.join(missing)} for {dominant_object}"


def special_cases(sim_cases: list[dict[str, str]]) -> list[dict[str, str]]:
    mapping = {
        "zero branch survival": ("no branch", "trajectory/DAG advantage should shrink unless verifier, durable, or correctness fields remain nonzero"),
        "zero reuse": ("no reuse", "context/object reuse advantage collapses, but correctness-sensitive verifier and durable state can still matter"),
        "equal tier costs": ("equal tier costs", "movement-driven differences collapse; extra scheduling detail is unjustified without retained-value differences"),
        "zero correctness loss": ("all state correctness-insensitive", "verifier/tool/trajectory loss advantage shrinks but recompute and branch mechanisms can persist"),
        "zero durable horizon": ("durable horizon zero", "durable-workspace scheduling advantage collapses unless branch/verifier mechanisms remain"),
        "context cap saturated but durable horizon positive": ("context cap saturated with durable horizon positive", "KV/context advantage can collapse while durable workspace and trajectory scheduling persist"),
    }
    by_case = {row["special_case"]: row for row in sim_cases}
    rows = []
    for sim_name, (name, expected) in mapping.items():
        src = by_case[sim_name]
        spread = float(src["score_spread"])
        collapse = "collapse" if spread == 0 else "persistence"
        rows.append(
            {
                "special_case": name,
                "source_sim_case": sim_name,
                "observed_policy_ranking": src["observed_policy_ranking"],
                "top_policy": src["top_policy"],
                "score_spread": f"{spread:.6f}",
                "scheduler_interpretation": expected,
                "collapse_or_persistence": collapse,
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read_csv(EVENTS)
    policy_results = read_csv(POLICY_RESULTS)
    object_breakdown = read_csv(OBJECT_BREAKDOWN)
    sim_cases = read_csv(SIM_SPECIAL_CASES)
    read_csv(MEMORY_OBJECTS)
    read_csv(WORKLOAD_CLASSES)

    require_columns(events, EVENTS, {"workload_class", "object_class", "size_units", "reuse_probability", "branch_fanout", "branch_survival", "verifier_delay", "durability_horizon", "correctness_sensitive", "recompute_cost", "loss_cost"})
    require_columns(policy_results, POLICY_RESULTS, {"policy", "workload_class", "winning_policy_for_workload", "memory_centric_thesis"})
    require_columns(object_breakdown, OBJECT_BREAKDOWN, {"policy", "workload_class", "object_class", "total_score_contribution"})

    stats_by_workload = workload_stats(events)
    winners = winner_rows(policy_results)
    contributions = positive_contributions(object_breakdown, winners)

    comparison_rows: list[dict[str, object]] = []
    failure_rows: list[dict[str, object]] = []
    winner_out: list[dict[str, object]] = []

    for workload in sorted(stats_by_workload):
        required, dominant_object = required_fields_for_workload(events, workload, contributions.get(workload, {}))
        scored = []
        for unit in UNITS:
            scores = score_unit(unit, stats_by_workload[workload], required, dominant_object)
            scored.append((unit, scores))
        scored.sort(key=lambda item: item[1]["total_score"], reverse=True)
        preferred, best_scores = scored[0]
        runner_up, runner_scores = scored[1]
        mechanism = mechanism_label(required, dominant_object)
        thesis = thesis_label(preferred, workload, mechanism)

        for unit, scores in scored:
            row = {
                "workload_class": workload,
                "scheduling_unit": unit,
                **{key: f"{value:.6f}" for key, value in scores.items()},
                "dominant_object_class": dominant_object,
                "preferred_unit_for_workload": preferred,
            }
            comparison_rows.append(row)
            reason = failure_reason(unit, required, dominant_object)
            if reason:
                failure_rows.append(
                    {
                        "workload_class": workload,
                        "scheduling_unit": unit,
                        "dominant_object_class": dominant_object,
                        "missing_fields": ";".join(sorted(required - UNIT_FIELDS[unit])),
                        "failure_mode": reason,
                        "wrong_decision_risk": "evict_or_recompute_state_without_observing_its_lifetime_boundary",
                    }
                )

        winner_out.append(
            {
                "workload_class": workload,
                "preferred_unit": preferred,
                "runner_up": runner_up,
                "margin": f"{best_scores['total_score'] - runner_scores['total_score']:.6f}",
                "mechanism_label": mechanism,
                "memory_centric_thesis": thesis,
                "dominant_object_class": dominant_object,
            }
        )

    comparison_fields = [
        "workload_class",
        "scheduling_unit",
        "alignment_score",
        "movement_avoidance_score",
        "reuse_capture_score",
        "branch_capture_score",
        "durability_capture_score",
        "correctness_capture_score",
        "coordination_overhead_score",
        "total_score",
        "dominant_object_class",
        "preferred_unit_for_workload",
    ]
    write_csv(COMPARISON_OUT, comparison_rows, comparison_fields)
    write_csv(
        WINNERS_OUT,
        winner_out,
        ["workload_class", "preferred_unit", "runner_up", "margin", "mechanism_label", "memory_centric_thesis", "dominant_object_class"],
    )
    write_csv(
        FAILURES_OUT,
        failure_rows,
        ["workload_class", "scheduling_unit", "dominant_object_class", "missing_fields", "failure_mode", "wrong_decision_risk"],
    )
    write_csv(
        SPECIAL_OUT,
        special_cases(sim_cases),
        ["special_case", "source_sim_case", "observed_policy_ranking", "top_policy", "score_spread", "scheduler_interpretation", "collapse_or_persistence"],
    )

    print(f"wrote {COMPARISON_OUT} rows={len(comparison_rows)}")
    print(f"wrote {WINNERS_OUT} rows={len(winner_out)}")
    print(f"wrote {FAILURES_OUT} rows={len(failure_rows)}")
    print(f"wrote {SPECIAL_OUT} rows=6")
    for row in winner_out:
        print(f"winner {row['workload_class']}: {row['preferred_unit']} ({row['mechanism_label']})")


if __name__ == "__main__":
    main()
