# created: 2026-05-18T00:32:00Z
# cycle: 8
# run_id: run-phytograph-cycle8-fork-56e44dff3ca4-clone0-track1-wave2
# agent: worker
# milestone: _plan/track1-wave2-enrichment-data-limited
"""Render Track 1 reticulation coverage figures.

Reads tracks/track1/data/reticulation_coverage_summary.tsv and the union
enrichment parquet, writes two PNGs and side-car captions under
tracks/track1/plots/.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T1_DATA = ROOT / "tracks" / "track1" / "data"
T1_PLOTS = ROOT / "tracks" / "track1" / "plots"


def out_path(default: Path) -> Path:
    override = os.environ.get("FIGURE_OUT")
    return Path(override) if override else default


def fig_coverage_by_edge_type() -> None:
    summary = pd.read_csv(T1_DATA / "reticulation_coverage_summary.tsv", sep="\t")
    edge_types = summary["edge_type"].tolist()
    staged = summary["staged_rows"].to_numpy()
    resolved = summary["resolved_rows"].to_numpy()
    pending = summary["pending_rows"].to_numpy()

    x = np.arange(len(edge_types))
    width = 0.28
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=160)
    ax.bar(x - width, staged, width, label="staged", color="#4c6ef5")
    ax.bar(x, resolved, width, label="resolved (accepted_taxon_key)", color="#2f9e44")
    ax.bar(x + width, pending, width, label="pending_crosswalk", color="#f08c00")
    for i, total in enumerate(staged):
        ax.text(i - width, total + 0.15, str(total), ha="center", fontsize=8)
    for i, total in enumerate(resolved):
        ax.text(i, total + 0.15, str(total), ha="center", fontsize=8)
    for i, total in enumerate(pending):
        ax.text(i + width, total + 0.15, str(total), ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(edge_types, rotation=15, ha="right")
    ax.set_ylabel("rows")
    ax.set_title(
        "Track 1 M1.3 reticulation enrichment: staged vs resolved vs pending\n"
        "(seed scale; 28 rows total — not a planet-scale atlas)"
    )
    ax.legend(loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    target = out_path(T1_PLOTS / "reticulation_coverage_by_edge_type.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target)
    plt.close(fig)
    caption = (
        "Track 1 M1.3 reticulation enrichment coverage by edge type. "
        "Bars show staged-row count (blue), rows that resolved to a Barrier-1 "
        "WFO accepted_taxon_key (green), and rows held pending_crosswalk=True "
        "with the raw scientific name preserved (orange). The substrate-published "
        "synonym maps are the sole resolution oracle. Most rows are pending "
        "because canonical polyploid crop binomials (e.g. Triticum aestivum, "
        "Brassica napus, Spartina anglica, Tragopogon spp.) are not in the "
        "current WFO accepted-name subset; this is the data-limited M1.3 "
        "ground truth, not a defect."
    )
    target.with_suffix(".caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(f"wrote {target}")


def fig_source_license_mix() -> None:
    union = pd.read_parquet(T1_DATA / "reticulation_enrichment_edges.parquet")
    pivot = (
        union.groupby(["source_id", "license"]).size().unstack(fill_value=0).sort_index()
    )
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=160)
    bottom = np.zeros(len(pivot))
    palette = plt.get_cmap("tab10")
    for idx, license_name in enumerate(pivot.columns):
        vals = pivot[license_name].to_numpy()
        short = (license_name[:55] + "…") if len(license_name) > 56 else license_name
        ax.bar(
            pivot.index.tolist(),
            vals,
            bottom=bottom,
            label=short,
            color=palette(idx % 10),
        )
        bottom = bottom + vals
    for i, total in enumerate(bottom):
        ax.text(i, total + 0.15, f"n={int(total)}", ha="center", fontsize=8)
    ax.set_ylabel("rows")
    ax.set_title("Track 1 reticulation enrichment: source × license mix (M1.3 seed)")
    ax.legend(fontsize=7, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    target = out_path(T1_PLOTS / "reticulation_source_license_mix.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target)
    plt.close(fig)
    caption = (
        "Track 1 reticulation enrichment source × license mix. Stacked bars "
        "show row counts by source_id (CCDB, Plant DNA C-values, Wood et al. "
        "2009 polyploid speciation synthesis), partitioned by license string. "
        "All licenses are preserved verbatim from staging; none of the M1.3 "
        "sources expose a permissive bulk-data license at probe time, so "
        "downstream cycles must continue treating these rows as citation-required "
        "seed evidence."
    )
    target.with_suffix(".caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(f"wrote {target}")


def main() -> None:
    T1_PLOTS.mkdir(parents=True, exist_ok=True)
    fig_coverage_by_edge_type()
    fig_source_license_mix()


if __name__ == "__main__":
    main()
