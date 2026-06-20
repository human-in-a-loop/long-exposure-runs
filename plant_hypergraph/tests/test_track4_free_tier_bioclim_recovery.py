"""Focused checks for the Track 4 free-tier BIOCLIM recovery branch."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tracks" / "track4" / "data"
REPORT = ROOT / "tracks" / "track4" / "reports" / "track4_free_tier_bioclim_recovery.md"
FIGURE = ROOT / "tracks" / "track4" / "figures" / "track4_free_tier_bioclim_recovery.png"


def read_tsv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, sep="\t", dtype=str, keep_default_na=False)


def test_report_states_readiness_predicates():
    text = REPORT.read_text()
    assert "determination: `still_data_limited`" in text
    assert "BIOCLIM readiness | failed" in text
    assert "Comparator readiness | failed" in text
    assert "no climate-substitution recommendation" in text


def test_missing_climate_is_undefined_not_numeric_zero():
    vectors = read_tsv("free_tier_bioclim_vectors.tsv")
    numeric = vectors[
        (vectors["mean"].str.strip() != "")
        | (vectors["median"].str.strip() != "")
        | (vectors["min"].str.strip() != "")
        | (vectors["max"].str.strip() != "")
    ]
    assert numeric.empty
    assert set(vectors["aggregation_method"]) == {"not_computed"}
    assert set(vectors["extraction_status"]) == {"not_computed_no_local_raster_or_runtime"}
    assert (vectors["n_coordinates_used"].astype(int).sum()) > 0


def test_validation_allowed_requires_disjoint_candidate_level_rows():
    comparators = read_tsv("free_tier_validation_comparators.tsv")
    allowed = comparators[comparators["validation_allowed"] == "true"]
    assert allowed.empty
    impossible = comparators[
        (comparators["validation_allowed"] == "true")
        & (
            (comparators["candidate_level_comparator"] != "true")
            | (comparators["overlaps_training_evidence"] != "false")
        )
    ]
    assert impossible.empty


def test_occurrence_summary_records_positive_filtered_coordinates():
    occurrence = read_tsv("free_tier_occurrence_summary.tsv")
    assert occurrence["post_filter_records"].astype(int).sum() > 0
    assert occurrence["license_compatible_records"].astype(int).sum() >= occurrence["post_filter_records"].astype(int).sum()
    assert {"Arachis hypogaea", "Avena sativa"} <= set(occurrence["queried_name"])


def test_figure_exists_and_master_ledgers_stay_header_only():
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000
    prediction_lines = (ROOT / "prediction_ledger.tsv").read_text().strip().splitlines()
    speculation_lines = (ROOT / "speculation_ledger.tsv").read_text().strip().splitlines()
    assert len(prediction_lines) == 1
    assert len(speculation_lines) == 1
