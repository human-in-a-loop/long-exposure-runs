#!/usr/bin/env python3
# created: 2026-05-12T18:20:00Z
# cycle: 44
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TRACEABI-1
"""Plot legacy trace-to-ABI lift status, gaps, and option fallbacks."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
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


def as_int(value: str) -> int:
    return int(float(value or 0))


def save(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    print(f"wrote {path.relative_to(ROOT)}")


def plot_status_counts() -> None:
    rows = read_csv(DATA / "trace_to_abi_lift_results.csv")
    statuses = ["abi_admissible", "annotation_required", "fail_closed", "option_a_opaque_fallback"]
    classes = sorted({row["object_class"] for row in rows})
    counts = defaultdict(Counter)
    for row in rows:
        counts[row["object_class"]][row["lift_status"]] += 1
    colors = {
        "abi_admissible": "#54a24b",
        "annotation_required": "#f2cf5b",
        "fail_closed": "#e45756",
        "option_a_opaque_fallback": "#4c78a8",
    }
    bottom = [0] * len(classes)
    x = range(len(classes))
    plt.figure(figsize=(11, 4.8))
    for status in statuses:
        values = [counts[cls][status] for cls in classes]
        plt.bar(x, values, bottom=bottom, label=status.replace("_", " "), color=colors[status])
        bottom = [a + b for a, b in zip(bottom, values)]
    plt.xticks(list(x), [cls.replace(" ", "\n") for cls in classes], fontsize=8)
    plt.ylabel("candidate count")
    plt.title("Trace-to-ABI lift status by memory object class")
    plt.legend(fontsize=8)
    save(DATA / "trace_to_abi_status_counts.png")


def plot_missing_fields() -> None:
    rows = read_csv(DATA / "trace_to_abi_missing_fields.csv")
    classes = sorted({row["object_class"] or "opaque request" for row in rows})
    categories = ["mandatory_provenance", "mandatory_security_reuse", "mandatory_branch_dependency", "mandatory_verifier_integrity", "mandatory_retention", "advisory_default_allowed", "opaque_fallback"]
    counts = defaultdict(Counter)
    for row in rows:
        counts[row["object_class"] or "opaque request"][row["field_category"]] += 1
    x = range(len(classes))
    bottom = [0] * len(classes)
    palette = ["#e45756", "#b279a2", "#ff9da6", "#9d755d", "#f58518", "#72b7b2", "#4c78a8"]
    plt.figure(figsize=(11, 4.8))
    for category, color in zip(categories, palette):
        values = [counts[cls][category] for cls in classes]
        plt.bar(x, values, bottom=bottom, label=category.replace("_", " "), color=color)
        bottom = [a + b for a, b in zip(bottom, values)]
    plt.xticks(list(x), [cls.replace(" ", "\n") for cls in classes], fontsize=8)
    plt.ylabel("field count")
    plt.title("Missing mandatory/advisory/security fields after trace lifting")
    plt.legend(fontsize=7)
    save(DATA / "trace_to_abi_missing_fields.png")


def plot_option_fallbacks() -> None:
    rows = read_csv(DATA / "trace_to_abi_option_fallbacks.csv")
    labels = [row["case_id"].replace("legacy_", "").replace("_", "\n") for row in rows]
    action_counts = [as_int(row["downstream_memory_action_count"]) for row in rows]
    colors = ["#54a24b" if row["boundary_result"] == "admitted_object_actions" else ("#4c78a8" if row["boundary_result"] == "opaque_execute" else "#e45756") for row in rows]
    plt.figure(figsize=(12, 4.8))
    plt.bar(range(len(rows)), action_counts, color=colors)
    plt.xticks(range(len(rows)), labels, fontsize=7)
    plt.ylabel("downstream memory action count")
    plt.title("Option A/B/C route after trace lifting and ABI validation")
    for i, row in enumerate(rows):
        route = "A" if row["selected_option"].startswith("A_") else ("B" if row["selected_option"].startswith("B_") else "C")
        plt.text(i, action_counts[i] + 0.08, route, ha="center", fontsize=9)
    save(DATA / "trace_to_abi_option_fallbacks.png")


def main() -> None:
    plot_status_counts()
    plot_missing_fields()
    plot_option_fallbacks()


if __name__ == "__main__":
    main()
