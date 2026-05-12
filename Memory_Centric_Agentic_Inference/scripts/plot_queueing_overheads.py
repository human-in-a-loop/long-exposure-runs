# created: 2026-05-11T15:08:00Z
# cycle: 8
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-QUEUE-1

"""Plot synthetic queueing overhead outputs."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OPTION_COLORS = {
    "A_conventional_request_model_kv_serving": "#4c78a8",
    "B_memory_object_aware_runtime": "#f58518",
    "C_trajectory_dag_memory_fabric": "#54a24b",
}
OPTION_LABELS = {
    "A_conventional_request_model_kv_serving": "A",
    "B_memory_object_aware_runtime": "B",
    "C_trajectory_dag_memory_fabric": "C",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def fnum(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def short_name(name: str) -> str:
    mapping = {
        "single-turn chat control": "single-turn\ncontrol",
        "batch summarization/offline inference control": "batch/offline\ncontrol",
        "RAG": "RAG",
        "code-agent loop": "code-agent\nloop",
        "verification-heavy": "verification\nheavy",
        "multi-agent branch/merge": "branch/merge",
    }
    return mapping.get(name, name.replace(" ", "\n"))


def plot_reversal_thresholds(out_path: Path) -> None:
    rows = read_csv(DATA / "queueing_architecture_winners.csv")
    workloads = [row["workload_class"] for row in rows]
    object_threshold = [fnum(row["first_object_reversal_metadata_service_time"]) for row in rows]
    dag_threshold = [fnum(row["first_non_C_dag_service_time"]) for row in rows]
    x = list(range(len(rows)))
    width = 0.36

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar([i - width / 2 for i in x], object_threshold, width, label="first A reversal by object overhead", color="#f58518")
    ax.bar([i + width / 2 for i in x], dag_threshold, width, label="first non-C reversal by DAG overhead", color="#54a24b")
    ax.set_xticks(x)
    ax.set_xticklabels([short_name(w) for w in workloads])
    ax.set_ylabel("synthetic service-time multiplier")
    ax.set_title("Architecture reversal thresholds by workload")
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def plot_utilization(out_path: Path) -> None:
    rates = read_csv(DATA / "queueing_trace_rates.csv")
    service_time = {
        "metadata": 0.5,
        "migration": 0.5,
        "dag": 0.5,
        "verifier": 0.35,
        "durable": 0.5,
    }
    workloads = [row["workload_class"] for row in rates]
    series = {
        "metadata": [fnum(row["metadata_ops_per_step"]) * service_time["metadata"] for row in rates],
        "migration": [fnum(row["migration_rate"]) * service_time["migration"] for row in rates],
        "DAG": [fnum(row["dag_event_rate"]) * max(1.0, fnum(row["max_dag_width"])) * service_time["dag"] for row in rates],
        "verifier": [fnum(row["verifier_event_rate"]) * max(1.0, fnum(row["mean_verifier_delay"])) * service_time["verifier"] for row in rates],
        "durable": [fnum(row["durable_rate"]) * service_time["durable"] for row in rates],
    }

    x = list(range(len(rates)))
    bottom = [0.0 for _ in rates]
    colors = ["#4c78a8", "#f58518", "#54a24b", "#b279a2", "#72b7b2"]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for (label, values), color in zip(series.items(), colors):
        ax.bar(x, values, bottom=bottom, label=label, color=color)
        bottom = [b + v for b, v in zip(bottom, values)]
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="rho = 1 saturation")
    ax.set_xticks(x)
    ax.set_xticklabels([short_name(w) for w in workloads])
    ax.set_ylabel("synthetic utilization at 0.5x service time")
    ax.set_title("Coordination-service utilization reconstructed from trace v2")
    ax.legend(ncol=3, loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def winner_for_grid(rows: list[dict[str, str]], workload: str, object_multiplier: float, dag_multiplier: float) -> str:
    candidates = [
        row
        for row in rows
        if row["workload_class"] == workload
        and fnum(row["metadata_service_time"]) == object_multiplier
        and fnum(row["migration_service_time"]) == object_multiplier
        and fnum(row["dag_coordination_service_time"]) == dag_multiplier
        and fnum(row["durable_write_service_time"]) in {0.0, 0.5, 1.0, 2.0, 4.0, 8.0}
        and fnum(row["preemption_checkpoint_service_time"]) in {0.0, 0.5, 1.0, 2.0, 4.0}
    ]
    if not candidates:
        return "A_conventional_request_model_kv_serving"
    # Keep durable/preemption at a moderate diagonal value when available.
    target_durable = min(dag_multiplier, 8.0)
    target_preempt = min(dag_multiplier, 4.0)
    best = min(
        candidates,
        key=lambda row: abs(fnum(row["durable_write_service_time"]) - target_durable)
        + abs(fnum(row["preemption_checkpoint_service_time"]) - target_preempt),
    )
    return best["winner"]


def plot_winner_map(out_path: Path) -> None:
    rows = read_csv(DATA / "queueing_overhead_sweep.csv")
    workloads = ["RAG", "code-agent loop", "verification-heavy", "multi-agent branch/merge"]
    values = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0]

    fig, axes = plt.subplots(2, 2, figsize=(10.5, 8.0), sharex=True, sharey=True)
    for ax, workload in zip(axes.ravel(), workloads):
        matrix = []
        for dag in values:
            row_values = []
            for obj in values:
                winner = winner_for_grid(rows, workload, obj, dag)
                row_values.append(["A_conventional_request_model_kv_serving", "B_memory_object_aware_runtime", "C_trajectory_dag_memory_fabric"].index(winner))
            matrix.append(row_values)
        ax.imshow(matrix, cmap=plt.matplotlib.colors.ListedColormap([OPTION_COLORS[k] for k in OPTION_COLORS]), vmin=0, vmax=2, origin="lower", aspect="auto")
        ax.set_title(short_name(workload).replace("\n", " "))
        ax.set_xticks(range(len(values)))
        ax.set_xticklabels([str(v) for v in values], rotation=45)
        ax.set_yticks(range(len(values)))
        ax.set_yticklabels([str(v) for v in values])
        for y, row_values in enumerate(matrix):
            for x, value in enumerate(row_values):
                label = ["A", "B", "C"][value]
                ax.text(x, y, label, ha="center", va="center", fontsize=8, color="white" if label == "A" else "black")
    for ax in axes[-1]:
        ax.set_xlabel("object overhead multiplier")
    for ax in axes[:, 0]:
        ax.set_ylabel("DAG/durable overhead multiplier")
    handles = [plt.Rectangle((0, 0), 1, 1, color=OPTION_COLORS[key], label=OPTION_LABELS[key]) for key in OPTION_COLORS]
    fig.legend(handles=handles, loc="upper center", ncol=3, title="winner")
    fig.suptitle("Architecture winner regions over object and DAG overheads", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", DATA / "queueing_reversal_thresholds.png"))
    plot_reversal_thresholds(out)
    plot_utilization(DATA / "queueing_utilization_by_workload.png")
    plot_winner_map(DATA / "queueing_architecture_winner_map.png")


if __name__ == "__main__":
    main()
