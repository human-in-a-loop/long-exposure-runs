#!/usr/bin/env python3
# created: 2026-05-12T16:10:00Z
# cycle: 37
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-EVIDART-1
"""Plot gate evidence artifact dependencies, failures, and replay boundary."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

GRAPH = DATA / "gate_evidence_dependency_graph.csv"
FAILURES = DATA / "gate_evidence_failure_modes.csv"
BOUNDARY = DATA / "gate_evidence_replay_readiness_boundary.csv"

OUT_GRAPH = DATA / "gate_evidence_dependency_graph.png"
OUT_FAILURES = DATA / "gate_evidence_failure_modes.png"
OUT_BOUNDARY = DATA / "gate_evidence_replay_readiness_boundary.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def plot_dependency(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["gate_order"]))
    labels = [row["gate_name"] for row in ordered]
    y = list(reversed(range(len(labels))))
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.scatter([0] * len(labels), y, s=180, color="#2c7fb8", zorder=3)
    for idx, row in enumerate(ordered):
        yy = y[idx]
        ax.text(0.08, yy, f"{row['gate_order']}. {row['gate_name']}", va="center", fontsize=9)
        if idx < len(ordered) - 1:
            ax.annotate("", xy=(0, y[idx + 1] + 0.18), xytext=(0, yy - 0.18), arrowprops={"arrowstyle": "->", "color": "#636363"})
    ax.set_xlim(-0.2, 2.8)
    ax.set_ylim(-0.7, len(labels) - 0.3)
    ax.set_title("Gate evidence dependency order and required upstream links")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT_GRAPH, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_GRAPH.relative_to(ROOT)}")


def plot_failures(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["count"]), reverse=True)
    labels = [row["failure_mode"] for row in ordered]
    values = [int(row["count"]) for row in ordered]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(range(len(labels)), values, color="#d95f0e")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("fail-closed probe count")
    ax.set_title("Offline gate-evidence artifact validation failures")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_FAILURES, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_FAILURES.relative_to(ROOT)}")


def plot_boundary(rows: list[dict[str, str]]) -> None:
    counts = Counter(
        "artifact complete, replay prerequisite only" if row["evidence_artifact_complete"] == "true" else "artifact incomplete/rejected"
        for row in rows
    )
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#31a354" if "complete" in label else "#d95f0e" for label in labels]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("bundle/probe rows")
    ax.set_title("Evidence artifact completeness versus replay and claim-credit boundary")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", alpha=0.25)
    note = "All bars preserve production_calibrated=false, production_ready=false, claim_credit_allowed=false"
    ax.text(0.5, -0.22, note, ha="center", va="top", transform=ax.transAxes, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_BOUNDARY, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_BOUNDARY.relative_to(ROOT)}")


def main() -> None:
    plot_dependency(read_csv(GRAPH))
    plot_failures(read_csv(FAILURES))
    plot_boundary(read_csv(BOUNDARY))


if __name__ == "__main__":
    main()
