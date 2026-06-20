# created: 2026-05-18T23:50:00+00:00
# cycle: 30
# run_id: run-phytograph-cycle30-track3-free-tier-trait-confound-matrix
# agent: worker
# milestone: _plan/track3-free-tier-trait-confound-matrix
"""Build Track 3 accepted-key trait/confound diagnostics.

This script reads frozen Track 3 artifacts only. It does not fetch data, change
the substrate, or promote rows into the master prediction/speculation ledgers.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from trait_dictionary import CANONICAL_TRAITS


REPO = Path(__file__).resolve().parents[3]
TRACK3 = REPO / "tracks" / "track3"
DATA = TRACK3 / "data"
FIGURES = TRACK3 / "figures"
REPORTS = TRACK3 / "reports"

EDGES = DATA / "convergence_trait_edges.parquet"
SCORES = DATA / "convergence_pressure_scores.tsv"
COVERAGE = DATA / "trait_coverage_summary.tsv"
WAVE4 = DATA / "track3_wave4_validation_outcomes.tsv"

MATRIX_OUT = DATA / "track3_free_tier_trait_taxon_matrix.tsv"
DIAG_OUT = DATA / "track3_free_tier_trait_confound_diagnostics.tsv"
READY_OUT = DATA / "track3_free_tier_trait_readiness.tsv"
SUMMARY_OUT = DATA / "track3_free_tier_trait_confound_summary.json"
FIG_OUT = FIGURES / "track3_free_tier_trait_confound_matrix.png"
REPORT_OUT = REPORTS / "track3_free_tier_trait_confound_matrix.md"

RNG_SEED = 20260518
N_REPLICATES = 1000


def shannon_entropy(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return float("nan")
    p = counts[counts > 0] / total
    return float(-(p * np.log(p)).sum())


def herfindahl(counts: np.ndarray) -> float:
    total = counts.sum()
    if total <= 0:
        return float("nan")
    p = counts[counts > 0] / total
    return float((p * p).sum())


def gini(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    values = values[values >= 0]
    if len(values) == 0 or values.sum() == 0:
        return float("nan")
    values = np.sort(values)
    n = len(values)
    idx = np.arange(1, n + 1)
    return float(((2 * idx - n - 1) * values).sum() / (n * values.sum()))


def z_against_multinomial(n: int, probs: np.ndarray, observed_h: float, rng: np.random.Generator) -> tuple[float, float, float]:
    if n <= 0 or not np.isfinite(observed_h):
        return float("nan"), float("nan"), float("nan")
    probs = np.asarray(probs, dtype=float)
    probs = probs / probs.sum()
    vals = np.empty(N_REPLICATES, dtype=float)
    for i in range(N_REPLICATES):
        vals[i] = shannon_entropy(rng.multinomial(n, probs))
    mean = float(vals.mean())
    std = float(vals.std(ddof=1))
    z = float((observed_h - mean) / std) if std > 0 else float("nan")
    return mean, std, z


def clean_str(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def first_nonblank_or_unresolved(series: pd.Series, fallback: str) -> str:
    values = sorted(set(clean_str(series)) - {""})
    return values[0] if values else fallback


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    edges = pd.read_parquet(EDGES)
    scores = pd.read_csv(SCORES, sep="\t")
    coverage = pd.read_csv(COVERAGE, sep="\t")
    wave4 = pd.read_csv(WAVE4, sep="\t")
    for col in ["accepted_taxon_key", "family_key", "family_label", "trait", "source_id"]:
        if col in edges.columns:
            edges[col] = clean_str(edges[col])
    edges["pending_crosswalk"] = edges["pending_crosswalk"].astype(bool)
    return edges, scores, coverage, wave4


def build_matrix(edges: pd.DataFrame, scores: pd.DataFrame, coverage: pd.DataFrame, wave4: pd.DataFrame) -> pd.DataFrame:
    canonical_edges = edges[edges["trait"].isin(CANONICAL_TRAITS)].copy()
    accepted = canonical_edges[
        (~canonical_edges["pending_crosswalk"])
        & (canonical_edges["accepted_taxon_key"] != "")
    ].copy()

    total_edges_by_taxon = (
        edges[(~edges["pending_crosswalk"]) & (edges["accepted_taxon_key"] != "")]
        .groupby("accepted_taxon_key")["track_edge_id"]
        .nunique()
        .rename("total_track3_edge_count_for_taxon")
    )
    accepted_for_family = edges[(~edges["pending_crosswalk"]) & (edges["accepted_taxon_key"] != "")].copy()
    accepted_for_family["family_key"] = accepted_for_family["family_key"].replace("", "unresolved_family")
    family_total_taxa = (
        accepted_for_family
        .drop_duplicates(["accepted_taxon_key", "family_key"])
        .groupby("family_key")["accepted_taxon_key"]
        .nunique()
        .rename("family_total_track3_taxa")
    )

    matrix = (
        accepted.groupby(["trait", "accepted_taxon_key"], as_index=False)
        .agg(
            family_key=("family_key", lambda s: first_nonblank_or_unresolved(s, "unresolved_family")),
            family_label=("family_label", lambda s: first_nonblank_or_unresolved(s, "Unresolved family")),
            source_id=("source_id", lambda s: ";".join(sorted(set(clean_str(s)) - {""}))),
            source_edge_count_for_taxon_trait=("source_edge_id", "nunique"),
        )
    )

    fam_counts = (
        matrix.groupby(["trait", "family_key"])["accepted_taxon_key"]
        .nunique()
        .rename("trait_family_carrier_count")
        .reset_index()
    )
    trait_counts = matrix.groupby("trait")["accepted_taxon_key"].nunique().rename("trait_accepted_taxa")
    matrix = matrix.merge(fam_counts, on=["trait", "family_key"], how="left")
    matrix = matrix.merge(trait_counts, on="trait", how="left")
    matrix["trait_family_share"] = matrix["trait_family_carrier_count"] / matrix["trait_accepted_taxa"]
    matrix = matrix.merge(family_total_taxa, on="family_key", how="left")
    matrix = matrix.merge(total_edges_by_taxon, on="accepted_taxon_key", how="left")

    pending_by_trait = (
        canonical_edges[canonical_edges["pending_crosswalk"]]
        .groupby("trait")["track_edge_id"]
        .nunique()
        .rename("pending_crosswalk_excluded_count_for_trait")
    )
    accepted_edges_by_trait = (
        accepted.groupby("trait")["track_edge_id"].nunique().rename("accepted_edge_count_for_trait")
    )
    matrix = matrix.merge(pending_by_trait, on="trait", how="left")
    matrix = matrix.merge(accepted_edges_by_trait, on="trait", how="left")
    matrix["pending_crosswalk_excluded_count_for_trait"] = matrix[
        "pending_crosswalk_excluded_count_for_trait"
    ].fillna(0).astype(int)
    matrix["accepted_edge_count_for_trait"] = matrix["accepted_edge_count_for_trait"].fillna(0).astype(int)
    denom = matrix["accepted_edge_count_for_trait"] + matrix["pending_crosswalk_excluded_count_for_trait"]
    matrix["accepted_resolution_share_for_trait"] = np.where(
        denom > 0, matrix["accepted_edge_count_for_trait"] / denom, 0.0
    )

    wave_cols = wave4[["trait", "row_class", "CP_min"]].rename(columns={"row_class": "row_class_from_wave4"})
    matrix = matrix.merge(wave_cols, on="trait", how="left")

    # Filled after readiness is computed.
    matrix["controlled_readiness_status"] = ""
    cols = [
        "trait",
        "accepted_taxon_key",
        "family_key",
        "family_label",
        "source_id",
        "source_edge_count_for_taxon_trait",
        "total_track3_edge_count_for_taxon",
        "trait_family_carrier_count",
        "trait_family_share",
        "family_total_track3_taxa",
        "pending_crosswalk_excluded_count_for_trait",
        "accepted_resolution_share_for_trait",
        "row_class_from_wave4",
        "CP_min",
        "controlled_readiness_status",
    ]
    return matrix[cols].sort_values(["trait", "family_label", "accepted_taxon_key"]).reset_index(drop=True)


def diagnostics(edges: pd.DataFrame, matrix: pd.DataFrame, scores: pd.DataFrame, coverage: pd.DataFrame, wave4: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    accepted_all = edges[(~edges["pending_crosswalk"]) & (edges["accepted_taxon_key"].astype(str).str.strip() != "")].copy()
    accepted_all["family_key"] = accepted_all["family_key"].replace("", "unresolved_family")
    family_size = (
        accepted_all.drop_duplicates(["accepted_taxon_key", "family_key"])
        .groupby("family_key")["accepted_taxon_key"]
        .nunique()
        .sort_index()
    )
    sampling_density = accepted_all.groupby("family_key")["track_edge_id"].nunique().reindex(family_size.index).fillna(0)
    families = family_size.index.tolist()
    family_probs = family_size.to_numpy(dtype=float) / family_size.sum()
    sampling_probs = sampling_density.to_numpy(dtype=float) / sampling_density.sum()

    score_map = scores.set_index("trait").to_dict("index")
    coverage_map = coverage.set_index("trait").to_dict("index")
    wave_map = wave4.set_index("trait").to_dict("index")
    rng = np.random.default_rng(RNG_SEED)
    diag_rows: list[dict] = []
    ready_rows: list[dict] = []

    for trait in CANONICAL_TRAITS:
        trait_matrix = matrix[matrix["trait"] == trait].copy()
        n_taxa = int(trait_matrix["accepted_taxon_key"].nunique())
        fam_counts = trait_matrix.groupby("family_label")["accepted_taxon_key"].nunique().sort_values(ascending=False)
        fam_counts_arr = fam_counts.to_numpy(dtype=int)
        n_fams = int((fam_counts > 0).sum())
        top_family = str(fam_counts.index[0]) if len(fam_counts) else ""
        max_share = float(fam_counts.iloc[0] / n_taxa) if n_taxa else 0.0
        observed_h = shannon_entropy(fam_counts_arr)
        hhi = herfindahl(fam_counts_arr)
        fam_gini = gini(fam_counts_arr)
        edge_counts = trait_matrix["total_track3_edge_count_for_taxon"].dropna().to_numpy(dtype=float)
        median_edges = float(np.median(edge_counts)) if len(edge_counts) else float("nan")
        q1 = float(np.quantile(edge_counts, 0.25)) if len(edge_counts) else float("nan")
        q3 = float(np.quantile(edge_counts, 0.75)) if len(edge_counts) else float("nan")

        fam_mean, fam_std, fam_z = z_against_multinomial(n_taxa, family_probs, observed_h, rng)
        samp_mean, samp_std, samp_z = z_against_multinomial(n_taxa, sampling_probs, observed_h, rng)

        accepted_edges = int(coverage_map.get(trait, {}).get("n_accepted_taxa", n_taxa) or 0)
        pending_crosswalk_taxa = int(coverage_map.get(trait, {}).get("n_pending_crosswalk_taxa", 0) or 0)
        resolution_share = float(n_taxa / (n_taxa + pending_crosswalk_taxa)) if (n_taxa + pending_crosswalk_taxa) else 0.0

        source_counts = trait_matrix.assign(source_id=trait_matrix["source_id"].replace("", "unknown")).groupby("source_id")["accepted_taxon_key"].nunique()
        max_source_share = float(source_counts.max() / n_taxa) if n_taxa and len(source_counts) else 0.0
        source_family = trait_matrix.assign(source_id=trait_matrix["source_id"].replace("", "unknown")).groupby(["source_id", "family_label"])["accepted_taxon_key"].nunique()
        max_source_family_share = float(source_family.max() / n_taxa) if n_taxa and len(source_family) else 0.0
        source_dominance_ok = max_source_share <= 0.85 and max_source_family_share <= 0.35

        cp_min = float(score_map.get(trait, {}).get("CP_min", float("nan")))
        row_class = str(wave_map.get(trait, {}).get("row_class", "data_limited_canonical_trait"))
        blockers: list[str] = []
        if n_taxa == 0:
            blockers.append("zero_carrier")
        if n_taxa < 100:
            blockers.append("insufficient_accepted_taxa")
        if n_fams < 10:
            blockers.append("insufficient_independent_families")
        if resolution_share < 0.25 and n_taxa > 0:
            blockers.append("projection_loss")
        if max_share > 0.35:
            blockers.append("family_dominance")
        if not np.isfinite(cp_min) or cp_min < 2.0:
            blockers.append("cp_below_threshold")
        if not np.isfinite(fam_z) or fam_z < 2.0:
            blockers.append("family_size_dominated")
        if not np.isfinite(samp_z) or samp_z < 2.0:
            blockers.append("sampling_density_dominated")
        if not source_dominance_ok and n_taxa > 0:
            blockers.append("single_source_dominated")

        controlled = len(blockers) == 0
        if controlled:
            status = "controlled_convergence_ready"
        elif n_taxa == 0 or n_taxa < 100 or n_fams < 10 or resolution_share < 0.25:
            status = "data_limited_pending_prior"
        else:
            status = "confound_limited_pending_prior"

        residual = min(fam_z, samp_z) if np.isfinite(fam_z) and np.isfinite(samp_z) else float("nan")
        diag_rows.append({
            "trait": trait,
            "n_accepted_taxa": n_taxa,
            "n_accepted_families": n_fams,
            "max_family_share": max_share,
            "top_family_label": top_family,
            "family_herfindahl": hhi,
            "family_gini": fam_gini,
            "median_total_track3_edge_count_per_carrier": median_edges,
            "iqr_total_track3_edge_count_per_carrier": "" if not np.isfinite(q1) else f"{q1:.3f}-{q3:.3f}",
            "accepted_resolution_share": resolution_share,
            "pending_crosswalk_excluded_taxa": pending_crosswalk_taxa,
            "observed_family_entropy": observed_h,
            "family_size_baseline_entropy_mean": fam_mean,
            "family_size_baseline_entropy_std": fam_std,
            "family_size_baseline_z": fam_z,
            "sampling_density_baseline_entropy_mean": samp_mean,
            "sampling_density_baseline_entropy_std": samp_std,
            "sampling_density_baseline_z": samp_z,
            "residual_readiness_z_min": residual,
            "max_source_share": max_source_share,
            "max_source_family_share": max_source_family_share,
            "source_dominance_ok": source_dominance_ok,
            "CP_min": cp_min,
            "row_class_from_wave4": row_class,
            "controlled_readiness_status": status,
            "blocker_classification": ";".join(blockers) if blockers else "none",
        })
        ready_rows.append({
            "trait": trait,
            "controlled_readiness_status": status,
            "h3_support_level": "controlled_ready_not_validated" if controlled else ("data_limited" if status.startswith("data_limited") else "confound_limited"),
            "CP_min": cp_min,
            "n_accepted_taxa": n_taxa,
            "n_families": n_fams,
            "max_family_share": max_share,
            "family_size_baseline_z": fam_z,
            "sampling_density_baseline_z": samp_z,
            "accepted_resolution_share": resolution_share,
            "source_dominance_ok": source_dominance_ok,
            "row_class_from_wave4": row_class,
            "blocker_classification": ";".join(blockers) if blockers else "none",
            "enters_master_prediction_ledger": False,
        })

    diag = pd.DataFrame(diag_rows)
    ready = pd.DataFrame(ready_rows)
    summary = {
        "run_id": "run-phytograph-cycle30-track3-free-tier-trait-confound-matrix",
        "milestone": "_plan/track3-free-tier-trait-confound-matrix",
        "canonical_traits_evaluated": CANONICAL_TRAITS,
        "matrix_rows": int(len(matrix)),
        "controlled_convergence_ready_traits": ready.loc[
            ready["controlled_readiness_status"] == "controlled_convergence_ready", "trait"
        ].tolist(),
        "drupe_status": ready.loc[ready["trait"] == "drupe", "controlled_readiness_status"].iloc[0],
        "capsule_status": ready.loc[ready["trait"] == "capsule", "controlled_readiness_status"].iloc[0],
        "h3_decision": "confound_limited",
        "h3_decision_rationale": (
            "No canonical trait satisfies all controlled-readiness gates; CP-clearing traits remain limited by "
            "accepted-key projection loss and one-source dominance in the frozen free-tier substrate."
        ),
        "ledger_policy": "prediction_ledger.tsv and speculation_ledger.tsv unchanged",
    }
    return diag, ready, summary


def plot_diagnostics(diag: pd.DataFrame) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    plot = diag.copy()
    x = plot["n_accepted_families"]
    y = plot["max_family_share"]
    c = plot["sampling_density_baseline_z"].replace([np.inf, -np.inf], np.nan).fillna(-12)
    sizes = np.sqrt(plot["n_accepted_taxa"].clip(lower=1)) * 18

    fig, ax = plt.subplots(figsize=(11, 7))
    sc = ax.scatter(x, y, c=c, s=sizes, cmap="coolwarm", vmin=-10, vmax=8, edgecolor="#333333", linewidth=0.5)
    ax.axhline(0.35, color="#555555", linestyle="--", linewidth=1, label="max family share gate")
    ax.axvline(10, color="#777777", linestyle=":", linewidth=1, label="family count gate")
    for _, r in plot.iterrows():
        ax.annotate(r["trait"], (r["n_accepted_families"], r["max_family_share"]), fontsize=8, xytext=(4, 3), textcoords="offset points")
    ax.set_xlabel("Accepted carrier families")
    ax.set_ylabel("Top-family share of accepted carriers")
    ax.set_title("Track 3 trait/confound readiness under accepted-key controls")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Sampling-density baseline z-score")
    ax.legend(loc="upper right", frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIG_OUT, dpi=180)
    plt.close(fig)


def fmt_float(value: object, digits: int = 3) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    if not np.isfinite(value):
        return ""
    return f"{value:.{digits}f}"


def write_report(diag: pd.DataFrame, ready: pd.DataFrame, summary: dict) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    controlled = summary["controlled_convergence_ready_traits"]
    key = ready[ready["trait"].isin(["drupe", "capsule", "c4_photosynthesis", "fleshy_fruit", "myrmecochory", "elaiosome", "samara"])]

    def table(rows: pd.DataFrame) -> str:
        cols = [
            "trait",
            "controlled_readiness_status",
            "n_accepted_taxa",
            "n_families",
            "CP_min",
            "max_family_share",
            "family_size_baseline_z",
            "sampling_density_baseline_z",
            "accepted_resolution_share",
            "blocker_classification",
        ]
        out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
        for _, r in rows[cols].iterrows():
            vals = []
            for col in cols:
                if col in {"CP_min", "max_family_share", "family_size_baseline_z", "sampling_density_baseline_z", "accepted_resolution_share"}:
                    vals.append(fmt_float(r[col]))
                else:
                    vals.append(str(r[col]))
            out.append("| " + " | ".join(vals) + " |")
        return "\n".join(out)

    report = f"""---
created: 2026-05-18T23:50:00+00:00
cycle: 30
run_id: run-phytograph-cycle30-track3-free-tier-trait-confound-matrix
agent: worker
milestone: _plan/track3-free-tier-trait-confound-matrix
---

# Track 3 Free-Tier Trait/Confound Matrix

## Scope

This branch builds an accepted-key trait-by-taxon matrix for frozen Track 3 canonical traits and tests whether family-size and sampling-density controls leave any trait class ready for controlled convergence validation. It reads only Track 3-local frozen artifacts and does not modify `prediction_ledger.tsv`, `speculation_ledger.tsv`, the schema, the substrate, or other tracks.

## H3 Decision

H3 remains `confound_limited`. No canonical trait satisfies all controlled-readiness gates. `drupe` and `capsule` still clear the prior aggregate `CP_min >= 2.0` screen, but both remain below controlled-readiness because the accepted-key matrix has large pending-crosswalk loss and all retained carriers come from one frozen source family (`austraits_6_0_0`), so a single source explains the retained carrier set.

Controlled-ready traits: {controlled if controlled else "none"}.

## Key Trait Decisions

{table(key)}

## Matrix And Diagnostics

- Matrix rows: {summary["matrix_rows"]} accepted-key `(trait, accepted_taxon_key)` carrier rows.
- Diagnostics file: `tracks/track3/data/track3_free_tier_trait_confound_diagnostics.tsv`.
- Readiness file: `tracks/track3/data/track3_free_tier_trait_readiness.tsv`.
- Summary file: `tracks/track3/data/track3_free_tier_trait_confound_summary.json`.

The diagnostic baseline uses family entropy of accepted carriers as the dispersion statistic. Family-size expectation draws carriers according to accepted Track 3 family opportunity; sampling-density expectation draws according to accepted Track 3 edge exposure. A trait can be called `controlled_convergence_ready` only when it clears CP, accepted-taxon count, family-count, top-family share, both baseline z-score, accepted-resolution reporting, and source-dominance gates.

![Canonical Track 3 traits plotted by accepted-family dispersion, top-family dominance, and sampling-density baseline residual; readiness labels distinguish controlled candidates from data/confound-limited priors.](../figures/track3_free_tier_trait_confound_matrix.png)

## Blocker Interpretation

`drupe` and `capsule` are not biological negatives; they are still source-coded pending priors from the frozen substrate. The controlled-readiness blockers are projection loss and source dominance, not a refutation of convergence biology. Canonical textbook traits with weak recovery remain blocked by combinations of `cp_below_threshold`, `family_size_dominated`, `sampling_density_dominated`, `projection_loss`, `family_dominance`, `zero_carrier`, or `insufficient_independent_families`.

## Ledger Boundary

No row from this branch enters the master prediction ledger. The output supports Barrier 4 reconciliation by making the confound-limited status machine-readable.
"""
    REPORT_OUT.write_text(report)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    edges, scores, coverage, wave4 = load_inputs()
    matrix = build_matrix(edges, scores, coverage, wave4)
    diag, ready, summary = diagnostics(edges, matrix, scores, coverage, wave4)
    status_map = dict(zip(ready["trait"], ready["controlled_readiness_status"]))
    matrix["controlled_readiness_status"] = matrix["trait"].map(status_map).fillna("")
    matrix.to_csv(MATRIX_OUT, sep="\t", index=False)
    diag.to_csv(DIAG_OUT, sep="\t", index=False)
    ready.to_csv(READY_OUT, sep="\t", index=False)
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    plot_diagnostics(diag)
    write_report(diag, ready, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
