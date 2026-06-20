#!/usr/bin/env python3
"""Track 5 coverage and source-density plots.
Outputs co-located with their source data under tracks/track5/data/.
"""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5" / "data"


def plot_top30_families() -> None:
    enr = pd.read_parquet(T5 / "track5_enrichment_edges.parquet")
    e = enr.dropna(subset=["family"])
    fam = (
        e.groupby("family")
        .agg(n_phyto=("edge_type", lambda s: int((s == "phytochemical_assertion").sum())),
             duke_share=("source_class", lambda s: float((s == "Dr. Duke").mean())))
        .sort_values("n_phyto", ascending=False)
        .head(30)
    )
    fig, ax = plt.subplots(figsize=(11, 7))
    colors = plt.cm.viridis(fam["duke_share"].values)
    ax.barh(range(len(fam)), fam["n_phyto"], color=colors)
    ax.set_yticks(range(len(fam)))
    ax.set_yticklabels(fam.index)
    ax.invert_yaxis()
    ax.set_xlabel("retained phytochemical_assertion edges (resolved-key projection)")
    ax.set_title("Track 5 — top 30 families by phytochemical_assertion count\n(bar color = Dr. Duke source share within family, 0 dark → 1 bright)")
    sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(0, 1))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label="Dr. Duke share")
    plt.tight_layout()
    plt.savefig(T5 / "family_chemistry_coverage_top30.png", dpi=150)
    plt.close()


def plot_duke_dominance_hist() -> None:
    duke = pd.read_csv(T5 / "dr_duke_dominance_audit.tsv", sep="\t")
    if duke.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(duke["duke_share"], bins=20, color="#888")
    med = duke["duke_share"].median()
    q50 = duke["duke_share"].quantile(0.50)
    q90 = duke["duke_share"].quantile(0.90)
    ax.axvline(med, color="C1", linestyle="--", label=f"median = {med:.2f}")
    ax.axvline(q50, color="C2", linestyle=":", label=f"q50 = {q50:.2f}")
    ax.axvline(q90, color="C3", linestyle=":", label=f"q90 = {q90:.2f}")
    ax.set_xlabel("Dr. Duke source share within family")
    ax.set_ylabel("families (n)")
    ax.set_title("Track 5 — Dr. Duke source share across families with >=1 retained assertion")
    ax.legend()
    plt.tight_layout()
    plt.savefig(T5 / "dr_duke_dominance_histogram.png", dpi=150)
    plt.close()


def plot_leave_one_source_out() -> None:
    loso = pd.read_csv(T5 / "leave_one_source_out_coverage.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(9, 5))
    xs = range(len(loso))
    ax.bar(xs, loso["surviving_family_cells_ge100"], color=["#444"] + ["#a33"] * (len(loso) - 1))
    ax.set_xticks(list(xs))
    ax.set_xticklabels([s if len(s) < 25 else s[:22] + "…" for s in loso["source_dropped"]], rotation=20, ha="right")
    ax.set_ylabel("surviving family-cells (>=100 assertions)")
    ax.set_title("Track 5 — surviving family-cells under leave-one-source-out (baseline first)")
    for i, v in enumerate(loso["surviving_family_cells_ge100"]):
        ax.text(i, v + 0.3, str(int(v)), ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    plt.savefig(T5 / "leave_one_source_out_coverage.png", dpi=150)
    plt.close()


def plot_family_compound_class_heatmap() -> None:
    fcc = pd.read_csv(T5 / "family_compound_class_matrix.tsv", sep="\t")
    if fcc.empty:
        return
    # top-20 compound classes by total assertions
    top_classes = (
        fcc.groupby("compound_class")["n_assertions"].sum().sort_values(ascending=False).head(20).index
    )
    # top-30 families by total compound-class assertions
    top_fams = (
        fcc[fcc["compound_class"].isin(top_classes)]
        .groupby("family")["n_assertions"].sum().sort_values(ascending=False).head(30).index
    )
    m = (
        fcc[fcc["family"].isin(top_fams) & fcc["compound_class"].isin(top_classes)]
        .pivot_table(index="family", columns="compound_class", values="n_assertions", fill_value=0)
        .reindex(index=top_fams, columns=top_classes)
    )
    fig, ax = plt.subplots(figsize=(12, 9))
    im = ax.imshow(np.log1p(m.values), cmap="magma", aspect="auto")
    ax.set_xticks(range(len(m.columns)))
    ax.set_xticklabels(m.columns, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(m.index)))
    ax.set_yticklabels(m.index, fontsize=8)
    plt.colorbar(im, ax=ax, label="log(1 + n_assertions)")
    ax.set_title("Track 5 — top-30 families × top-20 compound classes (Duke CHEMCLASS; log-scale heatmap)")
    plt.tight_layout()
    plt.savefig(T5 / "family_compound_class_heatmap.png", dpi=150)
    plt.close()


def main() -> None:
    plot_top30_families()
    plot_duke_dominance_hist()
    plot_leave_one_source_out()
    plot_family_compound_class_heatmap()
    print("plots written to", T5)


if __name__ == "__main__":
    main()
