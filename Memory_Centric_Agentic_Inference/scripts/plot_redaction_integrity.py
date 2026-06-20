#!/usr/bin/env python3
# created: 2026-05-12T12:10:00Z
# cycle: 33
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-REDACT-1
"""Plot redaction join survival, fail-closed modes, and claim boundary."""

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


def plot_join_survival() -> None:
    rows = read_csv(DATA / "redaction_integrity_results.csv")
    labels = [row["case_id"].removeprefix("invalid-").replace("-", "\n") for row in rows]
    values = [float(row["join_survival_fraction"]) for row in rows]
    colors = ["#2f6f73" if row["redaction_admissible"] == "true" else "#9f3a38" for row in rows]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(rows)), values, color=colors)
    ax.axhline(1.0, color="#333333", linestyle="--", linewidth=1, label="all required joins preserved")
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("required join survival fraction")
    ax.set_title("Redaction policies preserve or destroy replay joins")
    ax.legend(loc="lower left", fontsize=8)
    save(fig, DATA / "redaction_join_survival.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "redaction_failure_modes.csv")
    labels = [row["blocked_reason"] for row in rows]
    values = [int(row["case_count"]) for row in rows]
    colors = ["#b85c38" if row["redaction_status"] == "privacy_leakage" else "#4f6d9f" for row in rows]
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar(range(len(rows)), values, color=colors)
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("case count")
    ax.set_title("Privacy leakage and replay loss fail closed distinctly")
    save(fig, DATA / "redaction_failure_modes.png")


def plot_claim_boundary() -> None:
    rows = read_csv(DATA / "redaction_claim_credit_boundary.csv")
    counts = Counter(row["boundary_reason"] for row in rows)
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#2f6f73" if label == "redaction_export_quality_precondition_only" else "#9f3a38" for label in labels]
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("case count")
    ax.set_title("Redaction admissibility grants zero production claim credit")
    ax.tick_params(axis="x", rotation=35)
    ax.text(0.02, 0.93, "All fixture rows keep production_calibrated=false, production_ready=false, claim_credit_allowed=false", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "redaction_claim_boundary.png")


def main() -> None:
    plot_join_survival()
    plot_failures()
    plot_claim_boundary()


if __name__ == "__main__":
    main()
