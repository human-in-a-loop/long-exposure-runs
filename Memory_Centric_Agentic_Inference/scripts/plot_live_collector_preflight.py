#!/usr/bin/env python3
# created: 2026-05-12T17:15:00Z
# cycle: 38
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-LIVECOLLECT-1
"""Plot live collector capability, failure modes, and claim boundary."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CAPABILITY = DATA / "live_collector_capability_matrix.csv"
FAILURES = DATA / "live_collector_failure_modes.csv"
BOUNDARY = DATA / "live_collector_claim_boundary.csv"

OUT_CAPABILITY = DATA / "live_collector_capability_matrix.png"
OUT_FAILURES = DATA / "live_collector_failure_modes.png"
OUT_BOUNDARY = DATA / "live_collector_claim_boundary.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def plot_capability(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["collection_source_class"] for row in rows)
    labels = ["collector_observed", "operator_supplied", "external_attestation", "derived_from_prior_gate"]
    values = [counts[label] for label in labels]
    colors = ["#2c7fb8", "#41ab5d", "#756bb1", "#fdae6b"]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("gate artifacts")
    ax.set_title("Live collector source class by gate artifact")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_CAPABILITY, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_CAPABILITY.relative_to(ROOT)}")


def plot_failures(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["count"]), reverse=True)
    labels = [row["failure_mode"] for row in ordered]
    values = [int(row["count"]) for row in ordered]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.barh(range(len(labels)), values, color="#d95f0e")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("preflight probe count")
    ax.set_title("Live collector fail-closed states")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_FAILURES, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_FAILURES.relative_to(ROOT)}")


def plot_boundary(rows: list[dict[str, str]]) -> None:
    counts = Counter(
        "non-production artifacts emitted" if row["candidate_artifacts_emitted"] == "true" else "production emission blocked"
        for row in rows
    )
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#31a354" if "non-production" in label else "#d95f0e" for label in labels]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("probe cases")
    ax.set_title("Collector emission status versus production claim boundary")
    ax.tick_params(axis="x", rotation=10)
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.5,
        -0.20,
        "All cases preserve production_calibrated=false, production_ready=false, claim_credit_allowed=false",
        ha="center",
        va="top",
        transform=ax.transAxes,
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(OUT_BOUNDARY, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_BOUNDARY.relative_to(ROOT)}")


def main() -> None:
    plot_capability(read_csv(CAPABILITY))
    plot_failures(read_csv(FAILURES))
    plot_boundary(read_csv(BOUNDARY))


if __name__ == "__main__":
    main()
