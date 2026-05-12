# created: 2026-05-11T13:45:00Z
# cycle: 5
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SCHED-1

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
COMPARISON = DATA / "scheduling_unit_comparison.csv"
FAILURES = DATA / "scheduling_failure_modes.csv"
PLOT_OUT = Path(os.environ.get("FIGURE_OUT", DATA / "scheduling_abstraction_plot.png"))
FAILURE_OUT = DATA / "scheduling_failure_modes.png"

UNIT_ORDER = [
    "request",
    "job",
    "kernel",
    "model",
    "cache_page",
    "context_segment",
    "memory_object",
    "agent_trajectory_dag",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing input: {path}")
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def short_workload(name: str) -> str:
    return {
        "single-turn chat control": "single-turn",
        "batch summarization/offline inference control": "batch/offline",
        "RAG with retrieved-context reuse": "RAG",
        "code-agent loop with tool outputs and durable workspace": "code-agent",
        "verification-heavy agent": "verification",
        "multi-agent branch/merge run": "branch/merge",
    }.get(name, name[:18])


def plot_scores(rows: list[dict[str, str]]) -> None:
    workloads = sorted({row["workload_class"] for row in rows})
    by_pair = {(row["workload_class"], row["scheduling_unit"]): float(row["total_score"]) for row in rows}
    preferred = {row["workload_class"]: row["preferred_unit_for_workload"] for row in rows}

    fig, ax = plt.subplots(figsize=(13, 6.5))
    x_positions = list(range(len(workloads)))
    width = 0.095
    colors = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#72b7b2", "#b279a2", "#ff9da6", "#9d755d"]

    for idx, unit in enumerate(UNIT_ORDER):
        offset = (idx - (len(UNIT_ORDER) - 1) / 2) * width
        values = [by_pair.get((workload, unit), 0.0) for workload in workloads]
        bars = ax.bar([x + offset for x in x_positions], values, width=width, label=unit, color=colors[idx])
        for bar, workload in zip(bars, workloads):
            if preferred[workload] == unit:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015, "*", ha="center", va="bottom", fontsize=12)

    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([short_workload(w) for w in workloads], rotation=20, ha="right")
    ax.set_ylabel("synthetic scheduler-unit score")
    ax.set_title("Scheduling abstraction preference changes by workload regime")
    ax.legend(ncols=4, fontsize=8, frameon=False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(PLOT_OUT, dpi=160)
    plt.close(fig)


def plot_failures(rows: list[dict[str, str]]) -> None:
    workloads = sorted({row["workload_class"] for row in rows})
    counts = {(row["workload_class"], row["scheduling_unit"]): 0 for row in rows}
    for row in rows:
        counts[(row["workload_class"], row["scheduling_unit"])] += len([x for x in row["missing_fields"].split(";") if x])

    matrix = [[counts.get((workload, unit), 0) for unit in UNIT_ORDER] for workload in workloads]
    fig, ax = plt.subplots(figsize=(12, 5.8))
    image = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(UNIT_ORDER)))
    ax.set_xticklabels(UNIT_ORDER, rotation=35, ha="right")
    ax.set_yticks(range(len(workloads)))
    ax.set_yticklabels([short_workload(w) for w in workloads])
    ax.set_title("Blind-spot count by scheduling unit and workload")
    ax.set_xlabel("scheduling unit")
    ax.set_ylabel("workload")

    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, str(value), ha="center", va="center", color="#222222", fontsize=8)

    fig.colorbar(image, ax=ax, label="missing required fields")
    fig.tight_layout()
    fig.savefig(FAILURE_OUT, dpi=160)
    plt.close(fig)


def main() -> None:
    comparison = read_csv(COMPARISON)
    failures = read_csv(FAILURES)
    plot_scores(comparison)
    plot_failures(failures)
    print(f"wrote {PLOT_OUT}")
    print(f"wrote {FAILURE_OUT}")


if __name__ == "__main__":
    main()
