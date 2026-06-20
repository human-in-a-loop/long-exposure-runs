# created: 2026-05-11T22:50:00Z
# cycle: 18
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PLAN-1

"""Plot constrained memory-planner outputs."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

ACTIONS = DATA / "memory_plan_actions.csv"
SUMMARY = DATA / "memory_plan_workload_summary.csv"

OUT_ACTION_MIX = DATA / "memory_plan_action_mix.png"
OUT_CONSTRAINTS = DATA / "memory_plan_constraint_breakdown.png"
OUT_TRANSITIONS = DATA / "memory_plan_option_transitions.png"

ACTION_COLORS = {
    "keep_hot": "#2f6f4e",
    "offload_warm": "#4c78a8",
    "offload_cold": "#7f7f7f",
    "compress_or_pointer_preserve": "#d18f2f",
    "recompute_or_drop": "#b84a4a",
}
CONSTRAINT_COLORS = {
    "capacity": "#4c78a8",
    "security_gate": "#b84a4a",
    "validation_overhead": "#8f5aa8",
    "queueing_overhead": "#d18f2f",
    "contention_tail": "#6b8e23",
    "compression_unsafe": "#c05a9d",
    "control_or_zero_reuse": "#7f7f7f",
    "value_positive": "#2f6f4e",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def plot_action_mix(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        key = f"{row['workload_class']}\n{row['object_class']}"
        grouped[key][row["action"]] += 1
    labels = sorted(grouped)
    actions = [a for a in ACTION_COLORS if any(grouped[label][a] for label in labels)]
    fig, ax = plt.subplots(figsize=(14, max(6, len(labels) * 0.28)))
    left = [0] * len(labels)
    for action in actions:
        vals = [grouped[label][action] for label in labels]
        ax.barh(labels, vals, left=left, label=action, color=ACTION_COLORS[action])
        left = [a + b for a, b in zip(left, vals)]
    ax.set_xlabel("planned object/action rows")
    ax.set_title("Constrained memory planner action mix by workload and object class")
    ax.legend(loc="lower right", fontsize=8)
    save(fig, OUT_ACTION_MIX)


def plot_constraints(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[row["workload_class"]][row["constraint_binding"]] += 1
    labels = sorted(grouped)
    constraints = [c for c in CONSTRAINT_COLORS if any(grouped[label][c] for label in labels)]
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = [0] * len(labels)
    for constraint in constraints:
        vals = [grouped[label][constraint] for label in labels]
        ax.bar(labels, vals, bottom=bottom, label=constraint, color=CONSTRAINT_COLORS[constraint])
        bottom = [a + b for a, b in zip(bottom, vals)]
    ax.set_ylabel("planned object/action rows")
    ax.set_title("Binding constraint breakdown by workload")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    save(fig, OUT_CONSTRAINTS)


def plot_transitions(summary: list[dict[str, str]]) -> None:
    order = ["A", "B", "C"]
    matrix = {before: Counter() for before in order}
    labels = []
    for row in summary:
        before = row["baseline_option"][0]
        after = row["planned_option"][0]
        matrix[before][after] += 1
        labels.append(f"{row['workload_class']}: {before}->{after}")
    values = [[matrix[before][after] for after in order] for before in order]
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(values, cmap="YlGnBu", vmin=0)
    ax.set_xticks(range(3), [f"planned {x}" for x in order])
    ax.set_yticks(range(3), [f"baseline {x}" for x in order])
    for i, before in enumerate(order):
        for j, after in enumerate(order):
            ax.text(j, i, values[i][j], ha="center", va="center", color="black", fontsize=13)
    ax.set_title("Workload-level Option A/B/C transitions under planning constraints")
    caption = "\n".join(labels)
    ax.set_xlabel(caption, fontsize=8)
    fig.colorbar(im, ax=ax, label="workload count")
    save(fig, OUT_TRANSITIONS)


def main() -> None:
    actions = read_csv(ACTIONS)
    summary = read_csv(SUMMARY)
    plot_action_mix(actions)
    plot_constraints(actions)
    plot_transitions(summary)


if __name__ == "__main__":
    main()
