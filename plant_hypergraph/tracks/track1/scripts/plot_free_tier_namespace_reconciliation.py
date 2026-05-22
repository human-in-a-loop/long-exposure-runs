#!/usr/bin/env python3
# created: 2026-05-18T22:20:00+00:00
# cycle: 29
# run_id: run-phytograph-cycle29-track1-free-tier-namespace-reconciliation
# agent: worker
# milestone: _plan/track1-free-tier-namespace-reconciliation
"""Plot retained/rejected Track 1 namespace reconciliation counts."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_reconciled_evidence.tsv"
OUT = Path(
    os.environ.get(
        "FIGURE_OUT",
        ROOT / "tracks" / "track1" / "figures" / "track1_free_tier_namespace_reconciliation.png",
    )
)


def main() -> None:
    evidence = pd.read_csv(EVIDENCE, sep="\t").fillna("")
    counts = evidence["accepted_key_basis"].value_counts().reindex(
        ["wfo_projected", "gbif_sidecar", "rejected"], fill_value=0
    )
    colors = ["#2f7d62", "#6f4ba3", "#8a8f98"]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    bars = ax.bar(counts.index, counts.values, color=colors)
    ax.set_title("Track 1 namespace reconciliation")
    ax.set_ylabel("Evidence rows")
    ax.set_xlabel("Accepted-key basis after reconciliation")
    ax.set_xticks(range(len(counts.index)))
    ax.set_xticklabels(["WFO projected", "GBIF sidecar", "Rejected"])
    ax.set_ylim(0, max(counts.values) + 4)
    for bar in bars:
        value = int(bar.get_height())
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.4, str(value), ha="center", va="bottom")
    ax.text(
        0.02,
        0.95,
        "No master prediction/speculation row; sidecar rows are readiness diagnostics only.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="#333333",
    )
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180)


if __name__ == "__main__":
    main()
