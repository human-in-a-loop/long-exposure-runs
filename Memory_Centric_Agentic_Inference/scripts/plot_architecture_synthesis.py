# created: 2026-05-11T14:05:00Z
# cycle: 6
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ARCH-1

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


OPTION_ORDER = [
    "A_conventional_request_model_kv_serving",
    "B_memory_object_aware_runtime",
    "C_trajectory_dag_memory_fabric",
]

HOOKS = [
    "object_registry",
    "lifetime_boundary",
    "reuse_probability_estimator",
    "retention_value_estimator",
    "correctness_sensitive_pin",
    "durability_horizon",
    "branch_state_annotation",
    "verifier_retention_barrier",
    "trajectory_graph_edge",
    "tier_placement_hint",
    "compression_boundary",
    "provenance_pointer",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def short_workload(name: str) -> str:
    mapping = {
        "single-turn chat control": "single-turn\ncontrol",
        "batch summarization/offline inference control": "batch/offline\ncontrol",
        "RAG with retrieved-context reuse": "RAG\nreuse",
        "code-agent loop with tool outputs and durable workspace": "code-agent\ndurable",
        "verification-heavy agent": "verification\nheavy",
        "multi-agent branch/merge run": "branch/merge\nmulti-agent",
    }
    return mapping.get(name, name.replace(" ", "\n"))


def option_for_unit(unit: str, thesis: str) -> str:
    if thesis == "weakened" or unit in {"request", "job", "kernel", "model", "cache_page"}:
        return "A_conventional_request_model_kv_serving"
    if unit in {"context_segment", "memory_object"}:
        return "B_memory_object_aware_runtime"
    return "C_trajectory_dag_memory_fabric"


def plot_option_matrix(out_path: Path) -> None:
    winners = read_csv(DATA / "scheduling_regime_winners.csv")
    workloads = [row["workload_class"] for row in winners]
    values = []
    labels = []
    for row in winners:
        selected = option_for_unit(row["preferred_unit"], row["memory_centric_thesis"])
        values.append([1 if option == selected else 0 for option in OPTION_ORDER])
        labels.append(row["dominant_object_class"])

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.imshow(values, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(OPTION_ORDER)))
    ax.set_xticklabels(["A: conventional\nmodel/KV", "B: memory\nobject runtime", "C: trajectory\nDAG fabric"])
    ax.set_yticks(range(len(workloads)))
    ax.set_yticklabels([short_workload(w) for w in workloads])
    ax.set_title("Architecture option selected by workload regime")
    for y, row in enumerate(values):
        for x, selected in enumerate(row):
            text = "fit" if selected else ""
            ax.text(x, y, text, ha="center", va="center", color="black", fontsize=10, fontweight="bold" if selected else "normal")
        ax.text(len(OPTION_ORDER) - 0.02, y, f"  dominant: {labels[y]}", va="center", ha="left", fontsize=8)
    ax.set_xlim(-0.5, len(OPTION_ORDER) + 1.7)
    ax.set_xlabel("Architecture option")
    ax.set_ylabel("Workload regime")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def hook_required(hook: str, option: str, workload: str) -> bool:
    is_control = "control" in workload
    is_rag = workload.startswith("RAG")
    is_trajectory = any(token in workload for token in ["code-agent", "verification-heavy", "branch/merge"])

    baseline_hooks = {"tier_placement_hint", "compression_boundary"}
    object_hooks = {
        "object_registry",
        "lifetime_boundary",
        "reuse_probability_estimator",
        "retention_value_estimator",
        "correctness_sensitive_pin",
        "tier_placement_hint",
        "compression_boundary",
        "provenance_pointer",
    }
    dag_hooks = object_hooks | {"durability_horizon", "branch_state_annotation", "verifier_retention_barrier", "trajectory_graph_edge"}

    if option == "A_conventional_request_model_kv_serving":
        return is_control and hook in baseline_hooks
    if option == "B_memory_object_aware_runtime":
        return is_rag and hook in object_hooks
    if option == "C_trajectory_dag_memory_fabric":
        return is_trajectory and hook in dag_hooks
    return False


def plot_hook_coverage(out_path: Path) -> None:
    winners = read_csv(DATA / "scheduling_regime_winners.csv")
    workloads = [row["workload_class"] for row in winners]
    selected_options = {
        row["workload_class"]: option_for_unit(row["preferred_unit"], row["memory_centric_thesis"])
        for row in winners
    }
    columns = [f"{short_workload(w)}\n{selected_options[w].split('_')[0]}" for w in workloads]
    matrix = [
        [1 if hook_required(hook, selected_options[w], w) else 0 for w in workloads]
        for hook in HOOKS
    ]

    fig, ax = plt.subplots(figsize=(11, 7.5))
    ax.imshow(matrix, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=0, fontsize=8)
    ax.set_yticks(range(len(HOOKS)))
    ax.set_yticklabels([h.replace("_", "\n") for h in HOOKS], fontsize=8)
    ax.set_title("Runtime/compiler hook coverage by selected architecture option")
    for y, row in enumerate(matrix):
        for x, selected in enumerate(row):
            if selected:
                ax.text(x, y, "req", ha="center", va="center", fontsize=8, fontweight="bold")
    ax.set_xlabel("Workload and selected option")
    ax.set_ylabel("Hook")
    fig.tight_layout()
    fig.savefig(out_path, dpi=180)
    plt.close(fig)
    print(f"wrote {out_path}")


def main() -> None:
    option_out = Path(os.environ.get("FIGURE_OUT", DATA / "architecture_option_matrix.png"))
    plot_option_matrix(option_out)
    plot_hook_coverage(DATA / "runtime_hook_coverage.png")


if __name__ == "__main__":
    main()
