#!/usr/bin/env python3
"""Regression tests for Track 5 Wave 4 validation and ablation outputs."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track5" / "data"
FIG = ROOT / "tracks" / "track5" / "figures"


def test_temporal_holdout_rows_are_explicit_and_firewalled():
    out = pd.read_csv(DATA / "temporal_holdout_recovery.tsv", sep="\t")
    required = {
        "Taxus brevifolia",
        "Catharanthus roseus",
        "Cinchona officinalis",
        "Artemisia annua",
    }
    assert required.issubset(set(out["taxon"]))
    assert out["cutoff_date"].fillna("").str.match(r"\d{4}-12-31").all()
    assert {"rank_within_family", "family_percentile", "target_compound_class_hidden_before_scoring"}.issubset(out.columns)
    assert out["expected_validation_source"].fillna("").str.len().gt(0).all()
    assert out["claim_scope"].str.contains("no taxon-level bioactivity", case=False, na=False).all()
    assert out["claim_scope"].str.contains("clinical efficacy", case=False, na=False).all()
    assert set(out["status"]).issubset({"validated", "falsified", "data-limited"})


def test_source_ablation_matrix_reports_required_zero_signal_variants():
    ab = pd.read_csv(DATA / "source_ablation_results.tsv", sep="\t")
    required = {
        "full",
        "no_duke",
        "duke_downweighted",
        "source_density_matched",
        "screening_count_matched",
    }
    assert required == set(ab["variant"])
    counts = ab.set_index("variant")["prediction_count"].to_dict()
    assert counts["full"] == 1405
    assert counts["no_duke"] == 0
    assert counts["source_density_matched"] == 0
    assert counts["screening_count_matched"] == 0


def test_ablation_prediction_files_have_stable_firewalled_columns():
    base_cols = list(pd.read_csv(DATA / "phytochemistry_predictions.tsv", sep="\t", nrows=0).columns)
    for name in [
        "phytochemistry_predictions_no_duke.tsv",
        "phytochemistry_predictions_source_matched.tsv",
        "phytochemistry_predictions_screening_matched.tsv",
    ]:
        df = pd.read_csv(DATA / name, sep="\t")
        assert list(df.columns) == base_cols
        assert df.empty


def test_non_duke_harmonization_is_explicit_null_result():
    h = pd.read_csv(DATA / "non_duke_class_harmonization.tsv", sep="\t")
    assert len(h) == 1
    assert h.loc[0, "harmonization_status"] == "no_local_non_duke_detection_class_rows"
    assert "does not support taxon-level bioactivity" in h.loc[0, "evidence_scope"]


def test_wave4_figures_exist_and_are_nonempty():
    for name in [
        "temporal_holdout_family_percentiles.png",
        "source_ablation_prediction_counts.png",
        "duke_share_vs_score.png",
    ]:
        path = FIG / name
        assert path.exists()
        assert path.stat().st_size > 1000
