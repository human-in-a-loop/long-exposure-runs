#!/usr/bin/env python3
# created: 2026-05-12T11:10:00Z
# cycle: 32
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TIMEBASE-1
"""Plot timebase integrity sensitivity and fail-closed boundaries."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def save(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


def plot_sensitivity() -> None:
    rows = [r for r in read_csv(DATA / "timebase_threshold_sensitivity_cases.csv") if r["jitter_ms"] == "10" and r["collector_overhead_pct"] in {"0.0", "2.5", "4.9", "5.0", "7.5"}]
    overheads = sorted({float(r["collector_overhead_pct"]) for r in rows})
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    for overhead in overheads:
        subset = sorted([r for r in rows if float(r["collector_overhead_pct"]) == overhead], key=lambda r: float(r["skew_ms"]))
        ax.plot(
            [float(r["skew_ms"]) for r in subset],
            [1 if r["threshold_replay_status"] == "threshold_passed" else 0 for r in subset],
            marker="o",
            label=f"overhead={overhead:g}%",
        )
    ax.axvline(50, color="#444444", linestyle="--", linewidth=1, label="skew tolerance")
    ax.set_xlabel("cross-source skew (ms)")
    ax.set_ylabel("threshold replay identifiable")
    ax.set_yticks([0, 1], ["measurement_invalid", "replay valid"])
    ax.set_title("Threshold replay stability under skew and observer overhead")
    ax.legend(loc="best", fontsize=8)
    save(fig, DATA / "timebase_skew_sensitivity.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "timebase_failure_modes.csv")
    labels = [row["blocked_reason"] for row in rows]
    values = [int(row["case_count"]) for row in rows]
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.bar(range(len(rows)), values, color="#8b5a3c")
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("case count")
    ax.set_title("Timing and observer defects fail closed")
    save(fig, DATA / "timebase_failure_modes.png")


def plot_claim_boundary() -> None:
    rows = read_csv(DATA / "timebase_claim_credit_boundary.csv")
    counts = Counter(row["boundary_reason"] for row in rows)
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#2f6f73" if label == "timing_quality_precondition_only" else "#9f3a38" for label in labels]
    fig, ax = plt.subplots(figsize=(10.2, 5.2))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("case count")
    ax.set_title("Timing admissibility grants zero production claim credit")
    ax.tick_params(axis="x", rotation=35)
    ax.text(0.02, 0.93, "All fixture rows keep production_calibrated=false, production_ready=false, claim_credit_allowed=false", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "timebase_claim_boundary.png")


def main() -> None:
    plot_sensitivity()
    plot_failures()
    plot_claim_boundary()


if __name__ == "__main__":
    main()
