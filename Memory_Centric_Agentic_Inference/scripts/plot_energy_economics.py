#!/usr/bin/env python3
# created: 2026-05-11T21:50:00Z
# cycle: 16
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ENERGY-1
"""Render M-ENERGY-1 figures from energy/economics sensitivity CSVs."""

from __future__ import annotations

import csv
import os
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OPTION_COLORS = {"A": "#6b7280", "B": "#2f6f73", "C": "#8b1e3f"}
DECISION_COLORS = {
    "warm_tier_helps": "#2f6f73",
    "downgrade_warm_tier": "#8b1e3f",
}


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


def short_label(name: str) -> str:
    return (
        name.replace("DC001_", "")
        .replace("DC002_", "")
        .replace("_", "\n")
        .replace("pathological", "path")
    )


def plot_architecture_sensitivity() -> None:
    rows = read_csv(DATA / "energy_architecture_sensitivity.csv")
    workloads = sorted({r["workload_class"] for r in rows})
    settings = [
        "DC001_zero_energy|DC002_local_like_p50",
        "DC001_equal_tier_low|DC002_moderate_p95",
        "DC001_memory_gap_medium|DC002_tail_p99",
        "DC001_memory_gap_high|DC002_pathological_p99",
    ]
    by_key = {(r["workload_class"], f"{r['dc001_setting']}|{r['dc002_setting']}"): r for r in rows}
    fig, ax = plt.subplots(figsize=(12, 6))
    for y, wl in enumerate(workloads):
        for x, setting in enumerate(settings):
            row = by_key[(wl, setting)]
            option = row["option_after"]
            ax.scatter(x, y, s=640, marker="s", color=OPTION_COLORS[option], edgecolor="#111827", linewidth=0.7)
            ax.text(x, y, option, ha="center", va="center", color="white", fontweight="bold")
    ax.set_title("Option A/B/C Robustness Under Per-Byte Energy/Cost Sweeps")
    ax.set_xlabel("DC-001 energy/cost and DC-002 contention setting")
    ax.set_ylabel("Workload")
    ax.set_xticks(range(len(settings)))
    ax.set_xticklabels([short_label(s) for s in settings], fontsize=8)
    ax.set_yticks(range(len(workloads)))
    ax.set_yticklabels(workloads, fontsize=8)
    ax.grid(alpha=0.2)
    save(fig, "energy_architecture_sensitivity.png")


def plot_cxl_thresholds() -> None:
    rows = read_csv(DATA / "cxl_contention_thresholds.csv")
    selected = [r for r in rows if r["latency_percentile"] in {"p95", "p99", "p99_pathological"}]
    labels = [f"{r['workload_class']}\n{r['threshold_id'].split('-')[-2]} {r['latency_percentile']}" for r in selected]
    margins = [float(r["benefit_margin"]) for r in selected]
    settings = [min(float(r["contention_setting"]), 20.0) for r in selected]
    colors = [DECISION_COLORS[r["decision"]] for r in selected]
    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(selected))
    ax.bar(x, margins, color="#d1d5db", label="benefit margin")
    ax.scatter(x, settings, color=colors, s=40, label="contention setting, clipped at 20")
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title("CXL/Pooled-Memory Latency Thresholds Where Warm-Tier Placement Reverses")
    ax.set_ylabel("Dimensionless time-equivalent proxy")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=70, ha="right", fontsize=7)
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.25)
    save(fig, "cxl_contention_thresholds.png")


def plot_claim_update_map() -> None:
    rows = read_csv(DATA / "energy_claim_update_matrix.csv")
    decision_counts = Counter(r["decision"] for r in rows)
    evidence_counts = Counter(r["evidence_label"] for r in rows)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    ax1.bar(decision_counts.keys(), decision_counts.values(), color=["#2f6f73", "#8b1e3f", "#6b7280"][: len(decision_counts)])
    ax1.set_title("Claim Update Decisions")
    ax1.set_ylabel("Claim count")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.25)
    y = range(len(rows))
    risk_color = {"speculative": "#8b1e3f", "synthetic_sensitivity": "#b45309", "derived": "#2f6f73", "validated_artifact": "#6b7280"}
    ax2.scatter([1] * len(rows), y, s=120, color=[risk_color[r["evidence_label"]] for r in rows])
    for yi, row in zip(y, rows):
        ax2.text(1.05, yi, f"{row['claim_id']} -> {row['claim_after']}", va="center", fontsize=8)
    ax2.set_title("Synthesis Claims Updated by DC-001/DC-002 Outcomes")
    ax2.set_xlim(0.8, 2.8)
    ax2.set_yticks([])
    ax2.set_xticks([])
    subtitle = ", ".join(f"{k}={v}" for k, v in sorted(evidence_counts.items()))
    fig.suptitle(f"Energy Claim Update Map ({subtitle})", y=1.02, fontsize=10)
    save(fig, "energy_claim_update_map.png")


def main() -> None:
    target = Path(os.environ.get("FIGURE_OUT", ""))
    if target.name == "energy_architecture_sensitivity.png":
        plot_architecture_sensitivity()
    elif target.name == "cxl_contention_thresholds.png":
        plot_cxl_thresholds()
    elif target.name == "energy_claim_update_map.png":
        plot_claim_update_map()
    else:
        plot_architecture_sensitivity()
        plot_cxl_thresholds()
        plot_claim_update_map()


if __name__ == "__main__":
    main()
