#!/usr/bin/env python3
# created: 2026-05-12T15:10:00Z
# cycle: 36
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODREPLAY-1
"""Plot production-target replay gate traces and claim-boundary states."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TRACE = DATA / "production_target_replay_gate_trace.csv"
BOUNDARY = DATA / "production_target_replay_claim_boundary.csv"
OUT_TRACE = DATA / "production_target_replay_gate_trace.png"
OUT_BOUNDARY = DATA / "production_target_replay_claim_boundary.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def plot_trace(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["gate_order"]))
    labels = [row["gate_name"] for row in ordered]
    values = [1 if row["gate_passed"] == "true" else 0 for row in ordered]
    colors = ["#2c7fb8" if value else "#d95f0e" for value in values]
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(range(len(labels)), values, color=colors)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("gate passed")
    ax.set_title("Production-target replay gate trace")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_TRACE, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_TRACE.relative_to(ROOT)}")


def plot_boundary(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["replay_state"] for row in rows)
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#756bb1" if "candidate" in label else "#d95f0e" if "rejected" in label else "#636363" for label in labels]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("rows")
    ax.set_title("Production-target replay claim-support boundary")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_BOUNDARY, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_BOUNDARY.relative_to(ROOT)}")


def main() -> None:
    plot_trace(read_csv(TRACE))
    plot_boundary(read_csv(BOUNDARY))


if __name__ == "__main__":
    main()
