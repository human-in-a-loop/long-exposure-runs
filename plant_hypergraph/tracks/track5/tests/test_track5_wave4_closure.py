#!/usr/bin/env python3
"""Regression tests for Track 5 Wave 4 closure artifacts."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
T5 = ROOT / "tracks" / "track5"
DATA = T5 / "data"
FIG = T5 / "figures"
REPORT = T5 / "reports" / "track5_wave4_temporal_source_closure.md"


def test_closure_outcomes_cover_holdouts_and_ablations():
    out = pd.read_csv(DATA / "track5_wave4_validation_outcomes.tsv", sep="\t")
    holdouts = out[out["row_type"] == "temporal_holdout"]
    ablations = out[out["row_type"] == "source_ablation"]
    assert len(holdouts) == len(pd.read_csv(DATA / "temporal_holdout_recovery.tsv", sep="\t"))
    assert len(ablations) == len(pd.read_csv(DATA / "source_ablation_results.tsv", sep="\t"))
    assert {"Taxus brevifolia", "Catharanthus roseus", "Cinchona officinalis", "Artemisia annua"}.issubset(
        set(holdouts["target_taxon"])
    )


def test_temporal_rows_cannot_validate_without_top_decile_evidence():
    out = pd.read_csv(DATA / "track5_wave4_validation_outcomes.tsv", sep="\t")
    holdouts = out[out["row_type"] == "temporal_holdout"]
    invalid = holdouts[(holdouts["outcome"] == "validated_temporal_recovery") & (~holdouts["top_decile"].astype(bool))]
    assert invalid.empty
    assert (holdouts["outcome"] != "validated_temporal_recovery").all()


def test_source_ablation_nulls_are_represented():
    out = pd.read_csv(DATA / "track5_wave4_validation_outcomes.tsv", sep="\t")
    ab = out[out["row_type"] == "source_ablation"].set_index("variant")
    assert int(ab.loc["full", "prediction_count"]) == 1405
    assert int(ab.loc["no_duke", "prediction_count"]) == 0
    assert int(ab.loc["source_density_matched", "prediction_count"]) == 0
    assert int(ab.loc["screening_count_matched", "prediction_count"]) == 0
    assert ab.loc["duke_downweighted", "outcome"] == "not_independent_duke_still_present"


def test_report_preserves_evidence_firewall_and_ledgers_are_header_only():
    text = REPORT.read_text(encoding="utf-8").lower()
    assert "h5 is not validated" in text
    assert "not evidence about real-world compound absence" in text
    forbidden_positive = [
        "treats ",
        "cures ",
        "safe to",
        "recommended dose",
        "clinical efficacy claim",
        "validated taxon-level detection",
    ]
    assert not any(term in text for term in forbidden_positive)
    assert len((ROOT / "prediction_ledger.tsv").read_text(encoding="utf-8").splitlines()) == 1
    assert len((ROOT / "speculation_ledger.tsv").read_text(encoding="utf-8").splitlines()) == 1


def test_summary_figure_exists_and_is_nonblank():
    path = FIG / "track5_wave4_temporal_source_summary.png"
    assert path.exists()
    assert path.stat().st_size > 1000
