#!/usr/bin/env python3
# created: 2026-05-18T16:05:00+00:00
# cycle: 23
# run_id: run-phytograph-cycle23-track1-reopen-reticulation-evidence
# agent: worker
# milestone: _plan/track1-reticulation-reopen-evidence
"""Render Track 1 reopen accepted-key/event-shaped recovery diagnostics."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DIAGNOSTICS = ROOT / "tracks" / "track1" / "data" / "reticulation_reopen_join_diagnostics.tsv"


def main() -> None:
    out = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks/track1/figures/reticulation_reopen_join_recovery.png"))
    df = pd.read_csv(DIAGNOSTICS, sep="\t")
    labels = [
        name.replace("Barrier 4 frozen accepted-subset baseline", "Barrier 4\nbaseline")
        .replace("Wood et al. 2009 polyploid speciation synthesis", "Wood 2009\nlocal rows")
        .replace("CCDB chromosome-count seed rows", "CCDB\ncontext rows")
        for name in df["source_name"]
    ]
    x = range(len(df))
    fig, ax = plt.subplots(figsize=(8, 4.8))
    width = 0.26
    ax.bar([i - width for i in x], df["candidate_rows"], width=width, label="candidate rows", color="#6c757d")
    ax.bar(x, df["accepted_key_rows"], width=width, label="accepted-key rows", color="#2a9d8f")
    ax.bar([i + width for i in x], df["event_shaped_rows"], width=width, label="accepted-key event-shaped rows", color="#d62828")
    ax.axhline(5, color="#222222", linestyle="--", linewidth=1, label="minimum canonical-event threshold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=0, ha="center")
    ax.set_ylabel("rows")
    ax.set_title("Track 1 Reopen Join Recovery")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)


if __name__ == "__main__":
    main()
