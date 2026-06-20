#!/usr/bin/env python3
# created: 2026-05-11T18:42:00Z
# cycle: 14
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SYNTH-1
"""Render M-SYNTH-1 figures from generated synthesis CSVs."""

from __future__ import annotations

import csv
import os
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


OPTION_COLORS = {
    "A": "#6b7280",
    "B": "#2f6f73",
    "C": "#8b1e3f",
}
RISK_SCORE = {"low": 1, "medium": 2, "high": 3}
CLAIM_SCORE = {
    "sourced": 1,
    "derived": 1.3,
    "validated_artifact": 1.6,
    "simulated": 2.3,
    "speculative": 3.0,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def save(fig, default_name: str) -> None:
    out = Path(os.environ.get("FIGURE_OUT", DATA / default_name))
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"wrote {out}")


def plot_architecture_matrix() -> None:
    rows = read_csv(DATA / "synthesis_architecture_decision_matrix.csv")
    labels = [r["workload_class"] for r in rows]
    final = [r["option_short"] for r in rows]
    retained = [float(r["visible_retained_value_proxy"]) for r in rows]
    adjusted = [float(r["security_adjusted_value_proxy"]) for r in rows]
    colors = [OPTION_COLORS[o] for o in final]
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(rows))
    ax.bar(x, retained, color=colors, label="visible retained value")
    ax.scatter(x, adjusted, color="#111827", marker="D", s=45, label="security-adjusted proxy")
    for i, opt in enumerate(final):
        ax.text(i, retained[i] + 1.2, opt, ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title("Final Architecture Boundary by Workload")
    ax.set_ylabel("Dimensionless proxy")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=28, ha="right", fontsize=8)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save(fig, "synthesis_architecture_matrix.png")


def plot_agenda_priority() -> None:
    rows = read_csv(DATA / "synthesis_research_agenda.csv")
    labels = [r["experiment_id"] for r in rows]
    ranks = [int(r["rank"]) for r in rows]
    scores = [len(rows) + 1 - rank for rank in ranks]
    colors = ["#8b1e3f" if rank <= 4 else "#2f6f73" if rank <= 8 else "#6b7280" for rank in ranks]
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(labels[::-1], scores[::-1], color=colors[::-1])
    ax.set_title("Research Agenda Priority")
    ax.set_xlabel("Priority score, derived from rank")
    ax.set_ylabel("Experiment")
    ax.grid(axis="x", alpha=0.25)
    save(fig, "synthesis_agenda_priority.png")


def plot_claim_risk_map() -> None:
    rows = read_csv(DATA / "synthesis_claims_register.csv")
    fig, ax = plt.subplots(figsize=(10, 6))
    for row in rows:
        x = CLAIM_SCORE[row["claim_type"]]
        y = RISK_SCORE[row["risk_level"]]
        ax.scatter(x, y, s=95, color="#2f6f73" if y == 1 else "#b45309" if y == 2 else "#8b1e3f", alpha=0.85)
        ax.text(x + 0.03, y + 0.03, row["claim_id"], fontsize=8)
    counts = Counter(r["claim_type"] for r in rows)
    subtitle = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    ax.set_title(f"Claim Risk and Evidence Map ({subtitle})")
    ax.set_xlabel("Falsification difficulty / evidence maturity proxy")
    ax.set_ylabel("Risk level")
    ax.set_xticks([1, 1.3, 1.6, 2.3, 3.0])
    ax.set_xticklabels(["sourced", "derived", "validated", "simulated", "speculative"], rotation=20, ha="right")
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels(["low", "medium", "high"])
    ax.grid(alpha=0.25)
    save(fig, "synthesis_claim_risk_map.png")


def main() -> None:
    target = Path(os.environ.get("FIGURE_OUT", ""))
    if target.name == "synthesis_agenda_priority.png":
        plot_agenda_priority()
    elif target.name == "synthesis_claim_risk_map.png":
        plot_claim_risk_map()
    elif target.name == "synthesis_architecture_matrix.png":
        plot_architecture_matrix()
    else:
        plot_architecture_matrix()
        plot_agenda_priority()
        plot_claim_risk_map()


if __name__ == "__main__":
    main()
