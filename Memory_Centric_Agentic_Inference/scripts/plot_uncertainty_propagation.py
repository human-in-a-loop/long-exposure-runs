#!/usr/bin/env python3
# created: 2026-05-12T13:10:00Z
# cycle: 34
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-UNCERT-1
"""Plot uncertainty sensitivity, fail-closed modes, and claim boundary."""

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


def plot_threshold_sensitivity() -> None:
    rows = read_csv(DATA / "uncertainty_sensitivity_grid.csv")
    color = {"robust_pass": "#2f6f73", "robust_fail": "#9f3a38", "statistically_indeterminate": "#d0a33a"}
    marker = {4: "x", 16: "o", 64: "s"}
    fig, ax = plt.subplots(figsize=(9, 5.8))
    for row in rows:
        ax.scatter(
            float(row["effect_size"]),
            float(row["sigma"]),
            s=50 + int(row["sample_count"]),
            marker=marker[int(row["sample_count"])],
            color=color[row["threshold_status"]],
            alpha=0.82 if float(row["drift_fraction"]) <= 0.10 else 0.35,
        )
    ax.axvline(5.5, color="#333333", linestyle="--", linewidth=1, label="decision threshold")
    ax.set_xlabel("effect size / metric delta")
    ax.set_ylabel("noise sigma")
    ax.set_title("Confidence gate separates robust pass/fail from indeterminate regions")
    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=value, label=key, markersize=8)
        for key, value in color.items()
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=8)
    save(fig, DATA / "uncertainty_threshold_sensitivity.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "uncertainty_failure_modes.csv")
    labels = [row["blocked_reason"] for row in rows]
    values = [int(row["case_count"]) for row in rows]
    colors = ["#9f3a38" if row["threshold_status"] == "statistical_invalid" else "#d0a33a" for row in rows]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar(range(len(rows)), values, color=colors)
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("case count")
    ax.set_title("Malformed or weak uncertainty metadata fails closed")
    save(fig, DATA / "uncertainty_failure_modes.png")


def plot_claim_boundary() -> None:
    rows = read_csv(DATA / "uncertainty_threshold_boundary.csv")
    counts = Counter((row["point_estimate_passed"], row["threshold_status"]) for row in rows)
    labels = [f"point={point}\n{status}" for point, status in counts]
    values = list(counts.values())
    colors = ["#2f6f73" if status == "robust_pass" else "#d0a33a" if status == "statistically_indeterminate" else "#9f3a38" for _, status in counts]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.bar(range(len(labels)), values, color=colors)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("case count")
    ax.set_title("Point-estimate threshold pass is not claim readiness")
    ax.text(0.02, 0.92, "All fixture rows keep production_calibrated=false, production_ready=false, claim_credit_allowed=false", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "uncertainty_claim_boundary.png")


def main() -> None:
    plot_threshold_sensitivity()
    plot_failures()
    plot_claim_boundary()


if __name__ == "__main__":
    main()
