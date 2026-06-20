# created: 2026-05-11T18:10:00Z
# cycle: 13
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SEC-1

"""Render security/provenance figures from generated CSV artifacts."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


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


def plot_risk_by_object() -> None:
    rows = read_csv(DATA / "security_risk_scores.csv")
    by_object = defaultdict(float)
    for row in rows:
        by_object[row["object_class"]] += float(row["synthetic_risk_score"])
    items = sorted(by_object.items(), key=lambda x: x[1], reverse=True)
    labels = [x[0] for x in items]
    values = [x[1] for x in items]
    fig, ax = plt.subplots(figsize=(11, 6))
    colors = ["#8b1e3f" if v >= 30 else "#2f6f73" if v >= 15 else "#6b7280" for v in values]
    ax.bar(labels, values, color=colors)
    ax.set_title("Security Risk by Memory-Object Class")
    ax.set_ylabel("Synthetic risk score, summed across observed workloads")
    ax.set_xlabel("Memory-object class")
    ax.tick_params(axis="x", rotation=35, labelsize=9)
    ax.grid(axis="y", alpha=0.25)
    save(fig, "security_risk_by_object.png")


def plot_mitigation_coverage() -> None:
    rows = read_csv(DATA / "security_mitigation_matrix.csv")
    labels = [r["risk_class"] for r in rows]
    counts = [len([x for x in r["covered_object_classes"].split("; ") if x]) for r in rows]
    colors = ["#335c67" if r["coverage_status"] == "covered" else "#9f1239" for r in rows]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(labels, counts, color=colors)
    ax.set_title("Mitigation-Hook Coverage by Risk Class")
    ax.set_xlabel("Covered memory-object classes")
    ax.set_ylabel("Risk class")
    ax.grid(axis="x", alpha=0.25)
    save(fig, "security_mitigation_coverage.png")


def plot_architecture_tradeoff() -> None:
    rows = read_csv(DATA / "security_workload_summary.csv")
    labels = [r["workload_class"] for r in rows]
    retained = [float(r["retained_value_proxy"]) for r in rows]
    overhead = [float(r["mitigation_overhead_proxy_sum"]) for r in rows]
    adjusted = [float(r["security_adjusted_value_proxy"]) for r in rows]
    x = range(len(rows))
    width = 0.26
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar([i - width for i in x], retained, width=width, label="retained value", color="#2f6f73")
    ax.bar(x, [-v for v in overhead], width=width, label="validation overhead", color="#b45309")
    ax.bar([i + width for i in x], adjusted, width=width, label="security-adjusted value", color="#8b1e3f")
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title("Architecture Tradeoff: Retained Value vs Security Validation Overhead")
    ax.set_ylabel("Dimensionless synthetic proxy")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=28, ha="right", fontsize=8)
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save(fig, "security_architecture_tradeoff.png")


def main() -> None:
    target = Path(os.environ.get("FIGURE_OUT", ""))
    if target.name == "security_mitigation_coverage.png":
        plot_mitigation_coverage()
    elif target.name == "security_architecture_tradeoff.png":
        plot_architecture_tradeoff()
    else:
        plot_risk_by_object()


if __name__ == "__main__":
    main()
