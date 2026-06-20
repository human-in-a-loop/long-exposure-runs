#!/usr/bin/env python3
"""Regression tests for the Track 5 chemodiversity predictor."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
PRED = DATA / "phytochemistry_predictions.tsv"


def load_predictor_module():
    spec = importlib.util.spec_from_file_location(
        "track5_predictor", str(T5 / "scripts" / "track5_predictor.py")
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_prediction_file_is_pending_and_validation_addressable():
    pred = pd.read_csv(PRED, sep="\t")
    assert len(pred) > 0
    assert (pred["track"] == "track5").all()
    assert (pred["status"] == "pending").all()
    assert pred["expected_validation_source"].fillna("").str.len().gt(0).all()
    assert pred["prediction_statement"].str.contains("clinical", case=False, na=False).sum() == 0


def test_prediction_firewall_separates_detection_bioactivity_and_clinical_claims():
    pred = pd.read_csv(PRED, sep="\t")
    bio_rows = pred["predicted_bioactivity_via_compound_indirection"].fillna("").ne("")
    assert bio_rows.any()
    assert pred.loc[bio_rows, "bioactivity_chain_supporting_compound_ids"].fillna("").str.len().gt(0).all()
    assert pred.loc[bio_rows, "evidence_scope"].str.contains("compound indirection").all()
    assert pred.loc[bio_rows, "evidence_scope"].str.contains("does not support detection").all()
    assert pred["evidence_scope"].str.contains("clinical efficacy", case=False, na=False).all()


def test_all_predictions_carry_duke_ablation_sensitivity():
    pred = pd.read_csv(PRED, sep="\t")
    assert (pred["duke_share_in_family"] >= 0.5).all()
    assert pred["ablation_sensitivity"].fillna("").str.contains("Dr. Duke").all()


def test_duke_loso_zero_evidence_state_does_not_crash(tmp_path):
    mod = load_predictor_module()
    summary = mod.run_predictor(
        enrichment_path=DATA / "track5_enrichment_edges.parquet",
        screening_path=DATA / "per_taxon_screening_intensity.tsv",
        compound_class_path=DATA / "track5_compound_class_membership.parquet",
        bioactivity_path=DATA / "track5_bioactivity_assertions.parquet",
        taxon_family_path=DATA / "track5_taxon_to_family.parquet",
        out_predictions=tmp_path / "pred.tsv",
        out_signatures=tmp_path / "sig.parquet",
        out_speculation=tmp_path / "spec.tsv",
        loso_drop_source_class="Dr. Duke",
    )
    assert summary["n_predictions"] == 0
    pred = pd.read_csv(tmp_path / "pred.tsv", sep="\t")
    assert list(pred.columns)
    assert pred.empty
