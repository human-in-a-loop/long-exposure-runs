#!/usr/bin/env python3
# created: 2026-05-18T21:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-track1-free-tier-reticulation-recovery
# agent: worker
# milestone: _plan/track1-free-tier-reticulation-recovery
"""Plot accepted-key/event recovery by taxon and source group."""
from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import colormaps
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PANEL = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_panel.tsv"
DIAG = ROOT / "tracks" / "track1" / "data" / "free_tier_reticulation_join_diagnostics.tsv"
OUT = Path(os.environ.get("FIGURE_OUT", ROOT / "tracks" / "track1" / "figures" / "free_tier_reticulation_recovery_matrix.png"))


def main() -> None:
    panel = pd.read_csv(PANEL, sep="\t").fillna("")
    diag = pd.read_csv(DIAG, sep="\t").fillna("")
    source_order = ["gbif_species_api", "crossref_metadata", "openalex_metadata", "curated_open_literature"]
    taxa = panel["input_name"].tolist()
    matrix = []
    for taxon in taxa:
        row = []
        for source in source_order:
            record = diag[(diag["input_name"] == taxon) & (diag["source_group"] == source)].iloc[0]
            if source == "gbif_species_api":
                row.append(1 if str(record["accepted_key_match"]).lower() == "true" else 0)
            elif source == "curated_open_literature":
                row.append(2 if int(record["usable_event_shaped_hit_count"]) > 0 else 0)
            else:
                row.append(1 if int(record["source_hit_count"]) > 0 else 0)
        matrix.append(row)

    fig_height = max(7, len(taxa) * 0.22)
    fig, ax = plt.subplots(figsize=(8, fig_height))
    im = ax.imshow(matrix, aspect="auto", cmap=colormaps["YlGnBu"].resampled(3), vmin=0, vmax=2)
    ax.set_xticks(range(len(source_order)))
    ax.set_xticklabels(["GBIF key", "Crossref hits", "OpenAlex hits", "Event evidence"], rotation=30, ha="right")
    ax.set_yticks(range(len(taxa)))
    labels = [
        f"{name} ({'+' if role == 'canonical_positive' else 'C'})"
        for name, role in zip(panel["input_name"], panel["panel_role"])
    ]
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_title("Track 1 free-tier reticulation recovery matrix")
    ax.set_xlabel("No-auth source group")
    ax.set_ylabel("Panel taxon")
    for idx, role in enumerate(panel["panel_role"]):
        if role == "matched_control":
            ax.get_yticklabels()[idx].set_color("#555555")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02, ticks=[0, 1, 2])
    cbar.ax.set_yticklabels(["none", "join/hit", "event"])
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=180)


if __name__ == "__main__":
    main()
