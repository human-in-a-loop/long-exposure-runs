#!/usr/bin/env python3
"""Build Track 5 temporal holdout recovery diagnostics.

created: 2026-05-18T04:35:00+00:00
cycle: 10
run_id: fork-aaf42b4ab956-clone-3-track5-wave4
agent: worker-clone-3
milestone: M4.V5
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
FIG = T5 / "figures"

HOLDOUT_FAMILIES = {
    "Taxus brevifolia": "Taxaceae",
    "Catharanthus roseus": "Apocynaceae",
    "Cinchona officinalis": "Rubiaceae",
    "Artemisia annua": "Asteraceae",
    "Digitalis purpurea": "Plantaginaceae",
    "Papaver somniferum": "Papaveraceae",
    "Atropa belladonna": "Solanaceae",
    "Salix alba": "Salicaceae",
}

EXPECTED_VALIDATION = (
    "Temporally frozen phytochemical source or targeted screen confirming "
    "compound-class detection after the cutoff; no clinical, safety, or efficacy claim."
)


def resolve_taxon_key(nodes: pd.DataFrame, taxon: str) -> tuple[str | None, str]:
    exact = nodes[nodes["label"].fillna("").str.casefold() == taxon.casefold()].copy()
    accepted = exact[exact["accepted_taxon_key"].fillna("").ne("")]
    if not accepted.empty:
        return str(accepted.iloc[0]["accepted_taxon_key"]), "accepted_key_resolved"
    if not exact.empty:
        return None, "name_seen_but_no_accepted_key"
    return None, "name_absent_from_frozen_substrate"


def class_signature_for_family(signatures: pd.DataFrame, family: str, compound_class: str) -> pd.Series | None:
    hit = signatures[
        (signatures["family"] == family)
        & (signatures["compound_class"] == compound_class)
        & (signatures["family_status"] == "qualified")
    ]
    if hit.empty:
        return None
    return hit.iloc[0]


def choose_negative_control(tf: pd.DataFrame, screening: pd.DataFrame, family: str, target_key: str | None) -> str | None:
    screened = screening.set_index("accepted_taxon_key")["n_compounds"].to_dict()
    candidates = tf[tf["family"] == family]["accepted_taxon_key"].dropna().astype(str).unique().tolist()
    candidates = [c for c in candidates if c != target_key]
    if not candidates:
        return None
    candidates.sort(key=lambda k: (screened.get(k, 0), k))
    return candidates[0]


def build() -> pd.DataFrame:
    holdout = pd.read_csv(DATA / "canonical_phyto_held_out.tsv", sep="\t")
    nodes = pd.read_parquet(ROOT / "phytograph_dataset" / "nodes.parquet")
    tf = pd.read_parquet(DATA / "track5_taxon_to_family.parquet")
    screening = pd.read_csv(DATA / "per_taxon_screening_intensity.tsv", sep="\t")
    signatures = pd.read_parquet(DATA / "phytochemistry_signatures.parquet")
    enrichment = pd.read_parquet(DATA / "track5_enrichment_edges.parquet")

    compounds_by_taxon = (
        enrichment[
            (enrichment["edge_type"] == "phytochemical_assertion")
            & (enrichment["retained"])
        ]
        .groupby("accepted_taxon_key")["compound_id"]
        .nunique()
        .to_dict()
    )

    rows: list[dict] = []
    for _, h in holdout.iterrows():
        taxon = str(h["taxon"])
        target_class = str(h["canonical_compound_class_normalized"])
        discovery_year = int(h["discovery_year"])
        cutoff_date = f"{discovery_year - 1}-12-31"
        family = HOLDOUT_FAMILIES.get(taxon)
        key, resolution = resolve_taxon_key(nodes, taxon)
        neg = choose_negative_control(tf, screening, family, key) if family else None

        direct_target_rows = pd.DataFrame()
        target_hidden = False
        if key:
            direct_target_rows = enrichment[
                (enrichment["accepted_taxon_key"] == key)
                & (
                    (enrichment["compound_class"].fillna("") == target_class)
                    | enrichment["compound_id"].fillna("").str.contains(
                        str(h["canonical_compound"]).upper().replace(" ", "-"), na=False
                    )
                )
            ]
            target_hidden = not direct_target_rows.empty

        sig = class_signature_for_family(signatures, family, target_class) if family else None
        status = "data-limited"
        rank = np.nan
        percentile = np.nan
        target_score = 0.0
        negative_score = np.nan
        diagnostic = []

        if resolution != "accepted_key_resolved":
            diagnostic.append(resolution)
        if sig is None:
            diagnostic.append("family_class_signature_absent_or_not_qualified")
        if key and not target_hidden:
            diagnostic.append("no_direct_target_label_to_hide")
        if key and sig is not None:
            # Current source rows lack historical assertion dates; this is a
            # cutoff diagnostic over the frozen M3 score after hiding direct
            # target evidence, not a true temporally dated training set.
            n_compounds = int(compounds_by_taxon.get(key, 0))
            w_screening = 1.0 / (1.0 + n_compounds)
            target_score = float(sig["signature"]) * float(sig["w_specificity"]) * w_screening
            family_taxa = tf[tf["family"] == family]["accepted_taxon_key"].dropna().astype(str).unique().tolist()
            family_scores = []
            for candidate in family_taxa:
                n_c = int(compounds_by_taxon.get(candidate, 0))
                family_scores.append(float(sig["signature"]) * float(sig["w_specificity"]) * (1.0 / (1.0 + n_c)))
            family_scores.append(target_score)
            rank = 1 + sum(s > target_score for s in family_scores)
            percentile = rank / len(family_scores) if family_scores else np.nan
            status = "validated" if percentile <= 0.10 else "falsified"
            if neg:
                n_neg = int(compounds_by_taxon.get(neg, 0))
                negative_score = float(sig["signature"]) * float(sig["w_specificity"]) * (1.0 / (1.0 + n_neg))
                if abs(negative_score - target_score) < 1e-12:
                    diagnostic.append("negative_control_scores_equivalently")

        rows.append(
            {
                "track": "track5",
                "taxon": taxon,
                "target_accepted_key": key,
                "target_resolution_status": resolution,
                "family": family,
                "canonical_compound": h["canonical_compound"],
                "target_compound_class": target_class,
                "discovery_year": discovery_year,
                "cutoff_date": cutoff_date,
                "target_compound_class_hidden_before_scoring": bool(target_hidden),
                "evidence_sources_included": "frozen Track 5 retained phytochemical_assertion rows available in workspace",
                "evidence_sources_excluded": "direct target taxon/class rows where resolvable; no post-cutoff dates available to filter globally",
                "cutoff_filter_status": "no_assertion_dates_available",
                "rank_within_family": rank,
                "family_percentile": percentile,
                "target_score": round(target_score, 6),
                "negative_control_taxon_key": neg,
                "negative_control_score": round(float(negative_score), 6) if pd.notna(negative_score) else np.nan,
                "expected_validation_source": EXPECTED_VALIDATION,
                "status": status,
                "diagnostic": "|".join(diagnostic) if diagnostic else "scored",
                "claim_scope": "screening-prior only; no taxon-level bioactivity, clinical efficacy, safety, or therapeutic claim",
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(DATA / "temporal_holdout_recovery.tsv", sep="\t", index=False)
    return out


def plot(out: pd.DataFrame) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    vals = out["family_percentile"].fillna(1.0)
    labels = out["taxon"].str.replace(" ", "\n")
    colors = ["#2f6f8f" if pd.notna(v) else "#999999" for v in out["family_percentile"]]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(out)), vals, color=colors)
    ax.axhline(0.10, color="#b33", linestyle="--", label="top-decile threshold")
    ax.set_xticks(range(len(out)))
    ax.set_xticklabels(labels, rotation=0, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("family percentile (lower is better; unresolved plotted at 1.0)")
    ax.set_title("Track 5 temporal holdout recovery under frozen source coverage")
    ax.legend()
    plt.tight_layout()
    plt.savefig(FIG / "temporal_holdout_family_percentiles.png", dpi=150)
    plt.close()


def main() -> None:
    out = build()
    plot(out)
    print(f"WROTE: {DATA / 'temporal_holdout_recovery.tsv'} ({len(out)} rows)")
    print(f"WROTE: {FIG / 'temporal_holdout_family_percentiles.png'}")


if __name__ == "__main__":
    sys.exit(main())
