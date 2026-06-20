"""Validation checks for the Track 4 Crop Substitution Engine."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "tracks" / "track4" / "data"


def test_crop_substitution_outputs_exist():
    required = [
        ROOT / "scripts" / "track4_crop_substitution_engine.py",
        DATA / "crop_substitution_candidates.tsv",
        DATA / "crop_substitution_data_availability.tsv",
        DATA / "crop_substitution_engine_summary.json",
        DATA / "crop_substitution_data_availability.png",
        ROOT / "tracks" / "track4" / "track4_domestication_hypergraph.md",
    ]
    missing = [str(path) for path in required if not path.exists()]
    assert not missing


def test_candidates_are_data_limited_and_keyed():
    candidates = pd.read_csv(DATA / "crop_substitution_candidates.tsv", sep="\t", dtype=str, keep_default_na=False)
    assert len(candidates) == 3
    assert (candidates["crop_accepted_taxon_key"] != "").all()
    assert (candidates["candidate_wild_relative_key"] != "").all()
    assert set(candidates["prediction_status"]) == {"pending_data_limited"}
    assert set(candidates["validation_ready"].astype(str)) <= {"False", "false"}
    assert set(candidates["climate_match_status"]) == {"not_computable_no_observed_bioclim_vectors"}
    assert set(candidates["climate_component"]) == {""}
    assert set(candidates["score_basis"]) == {"pedigree_cwr_selection_vavilov_only"}


def test_climate_is_not_used_as_zero_score():
    candidates = pd.read_csv(DATA / "crop_substitution_candidates.tsv", sep="\t", dtype=str, keep_default_na=False)
    assert "climate_component" in candidates.columns
    assert (candidates["substitution_score_non_climate"].astype(float) > 0).all()
    assert (candidates["climate_component"] == "").all()
    assert candidates["climate_shortfall_reason"].str.contains("observed bioclim vectors absent", regex=False).all()


def test_availability_records_zero_observed_bioclim_vectors():
    availability = pd.read_csv(DATA / "crop_substitution_data_availability.tsv", sep="\t", dtype=str, keep_default_na=False)
    assert len(availability) >= 2
    assert not availability["bioclim_values_present"].astype(str).str.lower().eq("true").any()
    assert set(availability["instrument_status"]) <= {
        "candidate_scored_pedigree_only",
        "data_limited_no_scored_candidate",
    }


def test_summary_and_report_preserve_claim_boundary():
    summary = json.loads((DATA / "crop_substitution_engine_summary.json").read_text())
    assert summary["candidate_rows"] == 3
    assert summary["observed_bioclim_vectors"] == 0
    assert summary["climate_claims_emitted"] is False

    report = (ROOT / "tracks" / "track4" / "track4_domestication_hypergraph.md").read_text()
    assert "not a validated crop-substitution recommendation" in report
    assert "Climate is not assigned a zero score" in report
    assert "observed bioclim vectors equal zero" in report
