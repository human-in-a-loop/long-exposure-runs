#!/usr/bin/env python3
# created: 2026-05-11T23:58:00Z
# cycle: 19
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-DC12-1
"""Plot M-DC12-1 host-local proxy calibration outputs."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

BYTE = DATA / "dc12_byte_movement_measurements.csv"
CONTENTION = DATA / "dc12_contention_measurements.csv"
OVERLAY = DATA / "dc12_proxy_threshold_overlay.csv"

OUT_BYTE = DATA / "dc12_byte_movement_proxy.png"
OUT_CONTENTION = DATA / "dc12_contention_latency_proxy.png"
OUT_OVERLAY = DATA / "dc12_threshold_overlay.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} is empty")
    return rows


def fnum(row: dict[str, str], key: str) -> float:
    return float(row.get(key, "") or 0.0)


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def plot_byte(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["access_pattern"]].append(row)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    colors = {
        "sequential_copy": "#4c78a8",
        "sequential_read": "#2f6f4e",
        "sequential_write": "#d18f2f",
        "random_read_byte": "#8f5aa8",
    }
    for pattern, items in sorted(grouped.items()):
        items = sorted(items, key=lambda r: fnum(r, "working_set_bytes"))
        x = [fnum(r, "working_set_bytes") / (1 << 20) for r in items]
        y = [fnum(r, "throughput_mb_s") for r in items]
        ax1.plot(x, y, marker="o", color=colors.get(pattern, "#555555"), label=f"{pattern} throughput")
        lat = [fnum(r, "latency_p95_us") for r in items]
        ax2.plot(x, lat, marker="x", linestyle="--", color=colors.get(pattern, "#555555"), alpha=0.7)
    ax1.set_xscale("log", base=2)
    ax1.set_xlabel("working-set size (MiB)")
    ax1.set_ylabel("throughput (MiB/s)")
    ax2.set_ylabel("p95 operation/phase latency (us)")
    ax1.set_title("DC-001 host-local byte movement proxy")
    ax1.legend(loc="upper left", fontsize=8)
    save(fig, OUT_BYTE)


def plot_contention(rows: list[dict[str, str]]) -> None:
    items = sorted(rows, key=lambda r: int(r["worker_count"]))
    x = [int(r["worker_count"]) for r in items]
    fig, ax = plt.subplots(figsize=(9, 6))
    for pct, color in [("latency_p50_us", "#4c78a8"), ("latency_p95_us", "#d18f2f"), ("latency_p99_us", "#b84a4a")]:
        ax.plot(x, [fnum(r, pct) for r in items], marker="o", label=pct.replace("latency_", "").replace("_us", ""), color=color)
    ax.set_xlabel("local worker count")
    ax.set_ylabel("per-operation latency (us)")
    ax.set_title("DC-002 local contention latency proxy")
    ax.legend()
    save(fig, OUT_CONTENTION)


def plot_overlay(rows: list[dict[str, str]]) -> None:
    dc002 = [r for r in rows if r["constant_id"] == "DC-002"]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dc002:
        grouped[row["workload_class"]].append(row)
    labels = sorted(grouped)
    measured = [max(fnum(r, "measured_penalty_units") for r in grouped[label]) for label in labels]
    thresholds = [max(fnum(r, "collapse_threshold") for r in grouped[label]) for label in labels]
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(labels))
    ax.bar([i - 0.18 for i in x], measured, width=0.36, label="max measured local contention proxy", color="#4c78a8")
    ax.bar([i + 0.18 for i in x], thresholds, width=0.36, label="max existing reversal threshold", color="#b84a4a", alpha=0.8)
    ax.set_xticks(list(x), labels, rotation=25, ha="right")
    ax.set_ylabel("dimensionless proxy penalty / threshold units")
    ax.set_title("DC-001/DC-002 proxy overlay on existing Option A/B/C reversal thresholds")
    ax.legend()
    save(fig, OUT_OVERLAY)


def main() -> None:
    plot_byte(read_csv(BYTE))
    plot_contention(read_csv(CONTENTION))
    plot_overlay(read_csv(OVERLAY))


if __name__ == "__main__":
    main()
