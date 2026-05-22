"""Focused checks for the Track 4 bioclim validation-readiness reopen package."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tracks" / "track4" / "data"
REPORT = ROOT / "tracks" / "track4" / "reports" / "track4_reopen_bioclim_validation_readiness.md"
FIGURE = ROOT / "tracks" / "track4" / "figures" / "track4_reopen_bioclim_coverage.png"


VECTOR_COLUMNS = {
    "accepted_key",
    "accepted_name",
    "role",
    "crop_anchor_key",
    "crop_anchor_name",
    "source_name",
    "occurrence_or_range_basis",
    "bioclim_variable",
    "value",
    "aggregation_method",
    "provenance_url_or_path",
    "license_or_access_note",
    "caveat",
}

PAIR_COLUMNS = {
    "crop_key",
    "crop_name",
    "candidate_key",
    "candidate_name",
    "expert_source",
    "expert_relation_type",
    "heldout_status",
    "overlaps_training_evidence",
    "same_genus",
    "validation_allowed",
    "caveat",
}

DIAG_COLUMNS = {
    "source_name",
    "candidate_rows",
    "accepted_key_rows",
    "crop_anchor_rows",
    "cwr_rows",
    "bioclim_vector_rows",
    "heldout_validation_rows",
    "rejected_rows",
    "dominant_rejection_reason",
}


def read_tsv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, sep="\t", dtype=str, keep_default_na=False)


def test_required_columns_and_vocabularies():
    vectors = read_tsv("crop_cwr_bioclim_vectors.tsv")
    pairs = read_tsv("crop_cwr_validation_pairs.tsv")
    diagnostics = read_tsv("track4_reopen_join_diagnostics.tsv")

    assert VECTOR_COLUMNS <= set(vectors.columns)
    assert PAIR_COLUMNS <= set(pairs.columns)
    assert DIAG_COLUMNS <= set(diagnostics.columns)

    assert set(vectors["role"]) <= {"crop_anchor", "cwr"}
    assert set(pairs["heldout_status"]) <= {"heldout_crop_only_no_candidate", "validation_ready"}
    assert set(pairs["validation_allowed"]) <= {"true", "false"}
    assert set(pairs["overlaps_training_evidence"]) <= {"true", "false"}
    assert set(pairs["same_genus"]) <= {"true", "false", "not_applicable"}


def test_nonqualifying_vectors_are_caveated():
    vectors = read_tsv("crop_cwr_bioclim_vectors.tsv")
    assert len(vectors) == 10
    assert (vectors["accepted_key"] != "").all()
    assert set(vectors["bioclim_variable"]) == {"none_available"}
    assert set(vectors["value"]) == {""}
    assert set(vectors["aggregation_method"]) == {"not_computed"}
    assert (vectors["caveat"].str.len() > 20).all()


def test_heldout_rows_do_not_leak_training_evidence():
    pairs = read_tsv("crop_cwr_validation_pairs.tsv")
    assert len(pairs) == 22
    assert set(pairs["overlaps_training_evidence"]) == {"false"}
    leaked_allowed = pairs[
        (pairs["validation_allowed"] == "true")
        & (pairs["overlaps_training_evidence"] == "true")
    ]
    assert leaked_allowed.empty
    assert set(pairs["validation_allowed"]) == {"false"}
    assert (pairs.loc[pairs["validation_allowed"] == "false", "caveat"] != "").all()


def test_diagnostics_support_no_reopen_determination():
    diagnostics = read_tsv("track4_reopen_join_diagnostics.tsv")
    assert diagnostics["bioclim_vector_rows"].astype(int).sum() == 0
    assert diagnostics["heldout_validation_rows"].astype(int).sum() == 0
    assert diagnostics.loc[
        diagnostics["source_name"] == "WorldClim/CHELSA climate-envelope staging",
        "accepted_key_rows",
    ].astype(int).iloc[0] == 36
    assert diagnostics.loc[
        diagnostics["source_name"] == "Track 4 crop-wild-relative pairs",
        "accepted_key_rows",
    ].astype(int).iloc[0] == 3

    text = REPORT.read_text()
    assert "determination: `no_new_qualifying_evidence`." in text
    assert "zero observed or defensibly range-derived numeric BIOCLIM values" in text
    assert FIGURE.exists() and FIGURE.stat().st_size > 1000


def test_master_ledgers_remain_header_only():
    prediction_lines = (ROOT / "prediction_ledger.tsv").read_text().strip().splitlines()
    speculation_lines = (ROOT / "speculation_ledger.tsv").read_text().strip().splitlines()
    assert len(prediction_lines) == 1
    assert len(speculation_lines) == 1
