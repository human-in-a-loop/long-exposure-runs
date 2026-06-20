#!/usr/bin/env python3
# created: 2026-05-12T14:10:00Z
# cycle: 35
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CAUSAL-1
"""Plot causal confounder sensitivity, failure modes, and claim boundary."""

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


def plot_confounders() -> None:
    rows = read_csv(DATA / "causal_confounder_sensitivity_grid.csv")
    colors = {"causally_admissible": "#2f6f73", "causally_confounded": "#d0a33a", "causally_unidentified": "#9f3a38"}
    markers = {"true": "o", "false": "x"}
    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    for row in rows:
        ax.scatter(
            float(row["max_covariate_imbalance_smd"]),
            float(row["estimated_effect_ms"]),
            s=45 + 120 * float(row["positivity_overlap_fraction"]),
            color=colors[row["causal_status"]],
            marker=markers[row["apparent_threshold_passed"]],
            alpha=0.80,
        )
    ax.axhline(5.5, color="#333333", linestyle="--", linewidth=1, label="DC-002 threshold")
    ax.axvline(0.10, color="#555555", linestyle=":", linewidth=1, label="balance limit")
    ax.set_xlabel("max covariate imbalance, standardized mean difference")
    ax.set_ylabel("estimated effect, ms")
    ax.set_title("Confounder imbalance can create apparent robust threshold effects")
    handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=value, label=key, markersize=8)
        for key, value in colors.items()
    ]
    ax.legend(handles=handles, loc="upper left", fontsize=8)
    save(fig, DATA / "causal_confounder_sensitivity.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "causal_failure_modes.csv")
    labels = [row["blocked_reason"] for row in rows]
    values = [int(row["case_count"]) for row in rows]
    colors = ["#d0a33a" if row["causal_status"] == "causally_confounded" else "#9f3a38" for row in rows]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar(range(len(rows)), values, color=colors)
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("case count")
    ax.set_title("Invalid causal controls fail closed before claim support")
    save(fig, DATA / "causal_failure_modes.png")


def plot_claim_boundary() -> None:
    rows = read_csv(DATA / "causal_threshold_boundary.csv")
    counts = Counter((row["robust_statistical_effect"], row["causal_status"]) for row in rows)
    labels = [f"robust={robust}\n{status}" for robust, status in counts]
    values = list(counts.values())
    colors = ["#2f6f73" if status == "causally_admissible" else "#d0a33a" if status == "causally_confounded" else "#9f3a38" for _, status in counts]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.bar(range(len(labels)), values, color=colors)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("case count")
    ax.set_title("Robust statistical effect is not causal claim support")
    ax.text(0.02, 0.90, "All fixture rows keep production_calibrated=false, production_ready=false, claim_credit_allowed=false", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "causal_claim_boundary.png")


def main() -> None:
    plot_confounders()
    plot_failures()
    plot_claim_boundary()


if __name__ == "__main__":
    main()
