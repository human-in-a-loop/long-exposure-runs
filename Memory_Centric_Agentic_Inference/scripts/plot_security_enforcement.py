# created: 2026-05-11T22:13:00Z
# cycle: 17
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SECOPS-1

"""Render production-security enforcement replay figures."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str | None) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return ordered[idx]


def save(fig, name: str) -> None:
    out = Path(os.environ.get("FIGURE_OUT", DATA / name))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def plot_safe_reuse_waterfall() -> None:
    rows = read_csv(DATA / "security_enforcement_decisions.csv")
    grouped: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        raw = as_float(row["raw_reuse_credit"])
        if raw <= 0:
            continue
        wl = row["workload_class"]
        grouped[wl]["raw"] += raw
        if row["validation_decision"] == "safe_reuse":
            grouped[wl]["safe"] += as_float(row["safe_reuse_credit"])
        elif row["validation_decision"] == "denied_reuse":
            grouped[wl]["denied"] += raw
        elif row["validation_decision"] == "downgraded_reuse":
            grouped[wl]["downgraded"] += raw
        else:
            grouped[wl]["overhead"] += raw
    labels = sorted(grouped)
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(12, 6))
    raw = [grouped[w]["raw"] for w in labels]
    safe = [grouped[w]["safe"] for w in labels]
    denied = [grouped[w]["denied"] for w in labels]
    downgraded = [grouped[w]["downgraded"] for w in labels]
    overhead = [grouped[w]["overhead"] for w in labels]
    ax.bar(x, raw, color="#9ca3af", label="raw reuse credit")
    ax.bar(x, safe, color="#2563eb", label="safe reuse credit")
    ax.bar(x, denied, bottom=safe, color="#991b1b", label="denied")
    bottom = [safe[i] + denied[i] for i in x]
    ax.bar(x, downgraded, bottom=bottom, color="#b45309", label="downgraded")
    bottom = [bottom[i] + downgraded[i] for i in x]
    ax.bar(x, overhead, bottom=bottom, color="#6b7280", label="overhead dominated")
    ax.set_title("Raw Reuse Credit vs Security-Adjusted Safe Reuse")
    ax.set_ylabel("Synthetic retained-value credit")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncols=3, fontsize=8)
    save(fig, "security_safe_reuse_waterfall.png")


def plot_gate_latency_distribution() -> None:
    rows = read_csv(DATA / "security_trace_v3_events.csv")
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        gates = [g for g in row["validation_gate_ids"].split("; ") if g]
        if not gates:
            continue
        latency = as_float(row["validation_queue_wait"])
        if row["validation_start_time"] and row["validation_end_time"]:
            latency += as_float(row["validation_end_time"]) - as_float(row["validation_start_time"])
        for gate in gates:
            grouped[(row["workload_class"], gate)].append(latency)
    gate_order = sorted({gate for _, gate in grouped})
    p95 = []
    p99 = []
    maxes = []
    for gate in gate_order:
        values = [v for (workload, g), vals in grouped.items() if g == gate for v in vals]
        p95.append(percentile(values, 0.95))
        p99.append(percentile(values, 0.99))
        maxes.append(max(values) if values else 0.0)
    x = range(len(gate_order))
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(x, p95, marker="o", color="#2563eb", label="p95")
    ax.plot(x, p99, marker="s", color="#7c2d12", label="p99")
    ax.scatter(x, maxes, color="#111827", s=18, label="max")
    ax.set_title("Validation Gate Latency Tails")
    ax.set_ylabel("Synthetic latency units")
    ax.set_xticks(list(x))
    ax.set_xticklabels(gate_order, rotation=30, ha="right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    save(fig, "security_gate_latency_distribution.png")


def plot_option_update_matrix() -> None:
    rows = read_csv(DATA / "security_architecture_decision_updates.csv")
    option_code = {
        "A_conventional_request_model_kv_serving": 0,
        "B_memory_object_aware_runtime": 1,
        "C_trajectory_dag_memory_fabric": 2,
    }
    labels = [r["workload_class"] for r in rows]
    matrix = [[option_code[r["option_before"]], option_code[r["option_after_security"]]] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, aspect="auto", cmap=plt.get_cmap("viridis", 3), vmin=0, vmax=2)
    ax.set_title("Architecture Option Before vs After Security Enforcement")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["before", "after"])
    ax.set_yticks(list(range(len(labels))))
    ax.set_yticklabels(labels, fontsize=8)
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, "ABC"[value], ha="center", va="center", color="white", fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(["A", "B", "C"])
    save(fig, "security_option_update_matrix.png")


def main() -> None:
    target = Path(os.environ.get("FIGURE_OUT", ""))
    if target.name == "security_safe_reuse_waterfall.png":
        plot_safe_reuse_waterfall()
    elif target.name == "security_gate_latency_distribution.png":
        plot_gate_latency_distribution()
    elif target.name == "security_option_update_matrix.png":
        plot_option_update_matrix()
    else:
        plot_safe_reuse_waterfall()
        plot_gate_latency_distribution()
        plot_option_update_matrix()


if __name__ == "__main__":
    main()
