#!/usr/bin/env python3
# created: 2026-05-11T17:24:00Z
# cycle: 12
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CALIB-1
"""Plot M-CALIB-1 calibration tables."""

from __future__ import annotations

import csv
import os
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open() as fh:
        return list(csv.DictReader(fh))


def numeric(value: str) -> float | None:
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def plot_bandwidth_capacity(out: Path) -> None:
    rows = read_csv("calibration_memory_tiers.csv")
    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    capacity = [
        row for row in rows
        if row["unit"] in {"GB", "TB"} and "capacity" in row["quantity"].lower()
    ]
    labels = [f'{row["tier"]}\n{row["subtier"]}' for row in capacity]
    highs = [numeric(row["range_high"]) or 0 for row in capacity]
    colors = ["#4c78a8" if row["claim_type"] != "deferred_public_evidence_missing" else "#bab0ac" for row in capacity]
    axes[0].barh(range(len(labels)), highs, color=colors)
    axes[0].set_yticks(range(len(labels)), labels, fontsize=8)
    axes[0].invert_yaxis()
    axes[0].set_xlabel("High end of sourced/derived capacity range")
    axes[0].set_title("Capacity Anchors")

    bandwidth = [
        row for row in rows
        if row["unit"] in {"GB/s", "TB/s"} and ("bandwidth" in row["quantity"].lower() or "link" in row["quantity"].lower())
    ]
    labels = [f'{row["tier"]}\n{row["subtier"]}' for row in bandwidth]
    highs = [numeric(row["range_high"]) or 0 for row in bandwidth]
    display = [value * 1000 if row["unit"] == "TB/s" else value for row, value in zip(bandwidth, highs)]
    colors = ["#59a14f" if row["claim_type"] == "sourced_range" else "#f28e2b" for row in bandwidth]
    axes[1].barh(range(len(labels)), display, color=colors)
    axes[1].set_yticks(range(len(labels)), labels, fontsize=8)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("High end, normalized to GB/s")
    axes[1].set_title("Bandwidth / Link Capability Anchors")

    fig.suptitle("Sourced or derived memory-tier capacity/bandwidth ranges; deferred tiers are omitted from numeric bars")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out.relative_to(ROOT)}")


def plot_source_quality(out: Path) -> None:
    rows = read_csv("calibration_source_quality_summary.csv")
    labels = [f'{row["source_quality"]}\n{row["claim_type"]}' for row in rows]
    counts = [int(row["row_count"]) for row in rows]
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(range(len(labels)), counts, color="#4c78a8")
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Rows")
    ax.set_title("Source quality and claim-type distribution across calibration entries")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out.relative_to(ROOT)}")


def plot_sensitivity_targets(out: Path) -> None:
    rows = read_csv("calibration_model_mapping.csv")
    priority = {"high": 3, "medium": 2, "low": 1}
    status_bonus = {"deferred": 1.0, "capability_only": 0.6, "derived_range_ready": 0.3, "public_range_ready": 0.2}
    rows = sorted(rows, key=lambda row: priority[row["reversal_risk"]] + status_bonus[row["calibration_status"]])
    labels = [row["model_variable"] for row in rows]
    scores = [priority[row["reversal_risk"]] + status_bonus[row["calibration_status"]] for row in rows]
    colors = ["#e15759" if row["reversal_risk"] == "high" else "#f28e2b" for row in rows]
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.barh(range(len(labels)), scores, color=colors)
    ax.set_yticks(range(len(labels)), labels, fontsize=8)
    ax.set_xlabel("Calibration priority score")
    ax.set_title("Existing model variables ranked by calibration priority and reversal risk")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"wrote {out.relative_to(ROOT)}")


def main() -> None:
    target = Path(os.environ.get("FIGURE_OUT", ""))
    if str(target) and not target.is_absolute():
        target = ROOT / target
    if target.name == "calibration_tier_bandwidth_capacity.png":
        plot_bandwidth_capacity(target)
    elif target.name == "calibration_source_quality.png":
        plot_source_quality(target)
    elif target.name == "calibration_model_sensitivity_targets.png":
        plot_sensitivity_targets(target)
    else:
        plot_bandwidth_capacity(DATA / "calibration_tier_bandwidth_capacity.png")
        plot_source_quality(DATA / "calibration_source_quality.png")
        plot_sensitivity_targets(DATA / "calibration_model_sensitivity_targets.png")


if __name__ == "__main__":
    main()
