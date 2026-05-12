#!/usr/bin/env python3
# created: 2026-05-12T10:15:00Z
# cycle: 31
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ROOTINT-1
"""Plot production root enrollment preflight coverage and boundaries."""

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


def plot_coverage() -> None:
    schema = read_csv(DATA / "production_root_enrollment_schema.csv")
    rows = read_csv(DATA / "production_root_valid_enrollments.csv") + read_csv(DATA / "production_root_invalid_enrollments.csv")
    counts = []
    labels = []
    for field in [row["field_name"] for row in schema]:
        labels.append(field)
        counts.append(sum(1 for row in rows if row.get(field, "")))
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    ax.barh(labels, counts, color="#356f6b")
    ax.set_xlabel("fixture rows with non-empty field")
    ax.set_title("Deployment-root enrollment dimension coverage")
    ax.invert_yaxis()
    save(fig, DATA / "production_root_enrollment_coverage.png")


def plot_failures() -> None:
    rows = read_csv(DATA / "production_root_failure_modes.csv")
    labels = [row["blocked_reason"] for row in rows]
    counts = [int(row["case_count"]) for row in rows]
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    ax.bar(range(len(rows)), counts, color="#8a5f2d")
    ax.set_xticks(range(len(rows)), labels, rotation=45, ha="right")
    ax.set_ylabel("case count")
    ax.set_title("Enrollment fail-closed defects")
    save(fig, DATA / "production_root_failure_modes.png")


def plot_boundary() -> None:
    rows = read_csv(DATA / "production_root_gatechain_boundary.csv")
    counts = Counter(row["boundary_reason"] for row in rows)
    labels = list(counts)
    values = [counts[label] for label in labels]
    colors = ["#2f6f73" if label == "enrollment_precondition_only" else "#9f3a38" for label in labels]
    fig, ax = plt.subplots(figsize=(9.8, 5.2))
    ax.bar(labels, values, color=colors)
    ax.set_ylabel("case count")
    ax.set_title("Enrollment boundary before gatechain replay")
    ax.tick_params(axis="x", rotation=35)
    ax.text(0.02, 0.94, "Enrollment admissible is necessary only; claim_credit_allowed=false for all fixtures", transform=ax.transAxes, fontsize=9)
    save(fig, DATA / "production_root_gatechain_boundary.png")


def main() -> None:
    plot_coverage()
    plot_failures()
    plot_boundary()


if __name__ == "__main__":
    main()
