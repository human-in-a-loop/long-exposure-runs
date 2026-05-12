#!/usr/bin/env python3
# created: 2026-05-12T19:08:00Z
# cycle: 40
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ABI-1
"""Plot memory-object ABI coverage and fail-closed boundaries."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

COVERAGE = DATA / "memory_object_abi_option_coverage.csv"
FAILURES = DATA / "memory_object_abi_failure_modes.csv"
PLANNER = DATA / "memory_object_abi_planner_boundary.csv"

OUT_COVERAGE = DATA / "memory_object_abi_coverage.png"
OUT_FAILURES = DATA / "memory_object_abi_failure_modes.png"
OUT_PLANNER = DATA / "memory_object_abi_planner_boundary.png"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def truth(value: str) -> int:
    return 1 if value == "true" else 0


def plot_coverage(rows: list[dict[str, str]]) -> None:
    columns = [
        ("option_a_supported_without_object_abi", "A opaque"),
        ("option_b_requires_planner_admissible_object", "B object ABI"),
        ("option_c_requires_resolvable_dag_or_object", "C DAG/object ABI"),
    ]
    matrix = [[truth(row[key]) for key, _label in columns] for row in rows]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    ax.imshow(matrix, cmap="Greens", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels([label for _key, label in columns], rotation=20, ha="right")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([row["object_class"] for row in rows], fontsize=8)
    ax.set_title("Memory-object ABI coverage across architecture options")
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            ax.text(x, y, "yes" if value else "no", ha="center", va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_COVERAGE, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_COVERAGE.relative_to(ROOT)}")


def plot_failures(rows: list[dict[str, str]]) -> None:
    ordered = sorted(rows, key=lambda row: int(row["count"]), reverse=True)
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.barh(range(len(ordered)), [int(row["count"]) for row in ordered], color="#d95f0e")
    ax.set_yticks(range(len(ordered)))
    ax.set_yticklabels([row["failure_mode"] for row in ordered], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("invalid examples")
    ax.set_title("ABI validation failures by contract defect")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUT_FAILURES, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_FAILURES.relative_to(ROOT)}")


def plot_planner(rows: list[dict[str, str]]) -> None:
    states = ["accepted", "rejected"]
    counts = [sum(1 for row in rows if row["planner_boundary"] == state) for state in states]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(states, counts, color=["#31a354", "#756bb1"])
    ax.set_ylabel("ABI examples")
    ax.set_title("Planner boundary: accepted contracts versus fail-closed rejection")
    ax.grid(axis="y", alpha=0.25)
    ax.text(
        0.5,
        -0.18,
        "Rejected contracts cannot reach placement, reuse, compression, or retention actions.",
        transform=ax.transAxes,
        ha="center",
        va="top",
        fontsize=8,
    )
    fig.tight_layout()
    fig.savefig(OUT_PLANNER, dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_PLANNER.relative_to(ROOT)}")


def main() -> None:
    plot_coverage(read_csv(COVERAGE))
    plot_failures(read_csv(FAILURES))
    plot_planner(read_csv(PLANNER))


if __name__ == "__main__":
    main()
