#!/usr/bin/env python3
"""Run Track 5 source and screening-intensity ablation diagnostics.

created: 2026-05-18T04:35:00+00:00
cycle: 10
run_id: fork-aaf42b4ab956-clone-3-track5-wave4
agent: worker-clone-3
milestone: M4.A-track5-duke-source-ablation
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
FIG = T5 / "figures"
sys.path.insert(0, str(T5 / "scripts"))
import track5_predictor  # noqa: E402


def empty_prediction_frame() -> pd.DataFrame:
    pred = pd.read_csv(DATA / "phytochemistry_predictions.tsv", sep="\t", nrows=0)
    return pred


def top_decile_recovery() -> int:
    path = DATA / "temporal_holdout_recovery.tsv"
    if not path.exists():
        return 0
    h = pd.read_csv(path, sep="\t")
    return int((h["family_percentile"].fillna(1.0) <= 0.10).sum())


def write_empty_predictions(path: Path) -> None:
    empty_prediction_frame().to_csv(path, sep="\t", index=False)


def run() -> pd.DataFrame:
    full = pd.read_csv(DATA / "phytochemistry_predictions.tsv", sep="\t")

    # Required no-Duke filename for Wave 4, generated from the same predictor.
    no_duke_summary = track5_predictor.run_predictor(
        enrichment_path=DATA / "track5_enrichment_edges.parquet",
        screening_path=DATA / "per_taxon_screening_intensity.tsv",
        compound_class_path=DATA / "track5_compound_class_membership.parquet",
        bioactivity_path=DATA / "track5_bioactivity_assertions.parquet",
        taxon_family_path=DATA / "track5_taxon_to_family.parquet",
        out_predictions=DATA / "phytochemistry_predictions_no_duke.tsv",
        out_signatures=DATA / "phytochemistry_signatures_no_duke.parquet",
        out_speculation=DATA / "phytochemistry_speculation_no_duke.tsv",
        loso_drop_source_class="Dr. Duke",
    )

    # With no non-Duke phytochemical source coverage, exact source-density and
    # screening-count matching have no eligible non-Duke strata to compare.
    write_empty_predictions(DATA / "phytochemistry_predictions_source_matched.tsv")
    write_empty_predictions(DATA / "phytochemistry_predictions_screening_matched.tsv")

    downweighted = full.copy()
    if not downweighted.empty:
        downweighted["score"] = (
            downweighted["score"].astype(float)
            * (1.0 - 0.90 * downweighted["duke_share_in_family"].astype(float))
        ).round(6)
        downweighted["ablation_sensitivity"] = (
            downweighted["ablation_sensitivity"].fillna("")
            + "|Duke weight set to 0.1 in score post-scaling"
        ).str.strip("|")
    downweighted.to_csv(DATA / "phytochemistry_predictions_duke_downweighted.tsv", sep="\t", index=False)

    recovery = top_decile_recovery()
    rows = [
        {
            "variant": "full",
            "duke_weight": 1.0,
            "prediction_count": len(full),
            "top_decile_holdout_recovery_count": recovery,
            "ablation_status": "baseline_source_dominated",
            "notes": "M3.T5 baseline; all prediction rows carry Dr. Duke sensitivity.",
        },
        {
            "variant": "no_duke",
            "duke_weight": 0.0,
            "prediction_count": int(no_duke_summary["n_predictions"]),
            "top_decile_holdout_recovery_count": 0,
            "ablation_status": "collapsed_to_zero",
            "notes": "Removing Dr. Duke leaves no qualifying phytochemical family/class signal.",
        },
        {
            "variant": "duke_downweighted",
            "duke_weight": 0.1,
            "prediction_count": len(downweighted),
            "top_decile_holdout_recovery_count": recovery,
            "ablation_status": "scores_scaled_not_independent",
            "notes": "Rows persist only because Duke evidence still supplies S_f[k]; not independent support.",
        },
        {
            "variant": "source_density_matched",
            "duke_weight": 0.0,
            "prediction_count": 0,
            "top_decile_holdout_recovery_count": 0,
            "ablation_status": "no_non_duke_phytochemical_stratum",
            "notes": "No matched non-Duke phytochemical source stratum exists in current frozen data.",
        },
        {
            "variant": "screening_count_matched",
            "duke_weight": 0.0,
            "prediction_count": 0,
            "top_decile_holdout_recovery_count": 0,
            "ablation_status": "no_non_duke_screening_stratum",
            "notes": "Screening-count match cannot be formed without non-Duke detection rows.",
        },
    ]
    out = pd.DataFrame(rows)
    out.to_csv(DATA / "source_ablation_results.tsv", sep="\t", index=False)
    return out


def plot_counts(out: pd.DataFrame) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(out["variant"], out["prediction_count"], color=["#555", "#b33", "#7a9", "#999", "#999"])
    ax.set_ylabel("prediction rows")
    ax.set_title("Track 5 source ablation: prediction count by variant")
    ax.tick_params(axis="x", rotation=20)
    for i, v in enumerate(out["prediction_count"]):
        ax.text(i, int(v) + 20, str(int(v)), ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG / "source_ablation_prediction_counts.png", dpi=150)
    plt.close()


def plot_duke_share() -> None:
    pred = pd.read_csv(DATA / "phytochemistry_predictions.tsv", sep="\t")
    fig, ax = plt.subplots(figsize=(8, 5))
    if not pred.empty:
        ax.scatter(pred["duke_share_in_family"], pred["score"], s=12, alpha=0.55)
    ax.set_xlabel("Dr. Duke share in family")
    ax.set_ylabel("candidate score")
    ax.set_title("Track 5 candidate score vs. Dr. Duke family share")
    plt.tight_layout()
    plt.savefig(FIG / "duke_share_vs_score.png", dpi=150)
    plt.close()


def main() -> None:
    out = run()
    plot_counts(out)
    plot_duke_share()
    print(f"WROTE: {DATA / 'source_ablation_results.tsv'} ({len(out)} variants)")
    print(f"WROTE: {DATA / 'phytochemistry_predictions_no_duke.tsv'}")
    print(f"WROTE: {DATA / 'phytochemistry_predictions_source_matched.tsv'}")
    print(f"WROTE: {FIG / 'source_ablation_prediction_counts.png'}")
    print(f"WROTE: {FIG / 'duke_share_vs_score.png'}")


if __name__ == "__main__":
    sys.exit(main())
