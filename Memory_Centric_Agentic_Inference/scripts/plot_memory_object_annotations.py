#!/usr/bin/env python3
# created: 2026-05-12T22:10:00Z
# cycle: 45
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ANNOT-1
"""Plot annotation merge outcomes."""

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


def status_plot() -> None:
    lift = read_csv(DATA / "trace_to_abi_lift_results.csv")
    merge = read_csv(DATA / "annotation_merge_results.csv")
    before = Counter(row["lift_status"] for row in lift)
    after = Counter(row["merge_status"] for row in merge)
    labels = sorted(set(before) | set(after))
    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar([i - 0.18 for i in x], [before[label] for label in labels], width=0.36, label="trace lift")
    ax.bar([i + 0.18 for i in x], [after[label] for label in labels], width=0.36, label="after annotation merge")
    ax.set_xticks(list(x), labels, rotation=25, ha="right")
    ax.set_ylabel("candidate or scenario count")
    ax.set_title("Annotation-required candidates before/after merge")
    ax.legend()
    save(fig, DATA / "memory_object_annotation_status.png")


def conflict_plot() -> None:
    rows = read_csv(DATA / "annotation_conflict_failures.csv")
    counts = Counter(f"{row['annotation_class']}\n{row['conflict_reason']}" for row in rows)
    labels, values = zip(*counts.items())
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh(range(len(labels)), values)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("fail-closed scenario count")
    ax.set_title("Annotation conflicts by class and reason")
    save(fig, DATA / "memory_object_annotation_conflicts.png")


def boundary_plot() -> None:
    rows = read_csv(DATA / "annotation_option_boundary.csv")
    counts = Counter(row["selected_option"] for row in rows)
    labels, values = zip(*sorted(counts.items()))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar(labels, values)
    ax.set_ylabel("annotation scenarios")
    ax.set_title("Option route after annotation validation and ABI replay")
    ax.tick_params(axis="x", labelrotation=20)
    save(fig, DATA / "memory_object_annotation_option_boundary.png")


def main() -> None:
    status_plot()
    conflict_plot()
    boundary_plot()


if __name__ == "__main__":
    main()
