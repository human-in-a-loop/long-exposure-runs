from __future__ import annotations

from pathlib import Path

import pandas as pd

WORKSPACE = Path(__file__).resolve().parents[3]
TRACK3 = WORKSPACE / "tracks" / "track3"
DATA = TRACK3 / "data"


def test_convergence_pressure_outputs_exist():
    for name in [
        "convergence_pressure_scores.tsv",
        "convergence_pressure_nulls.tsv",
        "convergence_pressure_confound_regression.tsv",
        "convergence_pressure_canonical_recovery.tsv",
        "convergence_predictions.tsv",
        "convergence_pressure_run_summary.json",
        "convergence_pressure_figure.png",
    ]:
        path = DATA / name
        assert path.exists(), f"missing Track 3 instrument artifact: {path}"
        assert path.stat().st_size > 0, f"empty Track 3 instrument artifact: {path}"


def test_canonical_scoring_excludes_other_bucket():
    scores = pd.read_csv(DATA / "convergence_pressure_scores.tsv", sep="\t")
    other = scores[scores["trait"] == "_other"]
    assert len(other) == 1
    assert bool(other["excluded_from_canonical"].iloc[0]) is True
    assert other["clears_bar"].iloc[0] in [False, "False"]
    assert pd.isna(other["CP_min"].iloc[0])

    canonical = scores[~scores["excluded_from_canonical"].astype(bool)]
    assert "_other" not in set(canonical["trait"])
    assert {"CP_N1", "CP_N2", "CP_min", "clears_bar"}.issubset(scores.columns)


def test_prediction_tsv_separates_hypotheses_from_evidence():
    pred = pd.read_csv(DATA / "convergence_predictions.tsv", sep="\t")
    assert len(pred) >= 16
    assert "pending_convergent_trait_hypothesis" in set(pred["row_class"])
    assert "observed_trait_evidence_summary" in set(pred["row_class"])
    assert "data_limited_canonical_trait" in set(pred["row_class"])
    assert "diagnostic_bucket_excluded" in set(pred["row_class"])

    hypotheses = pred[pred["row_class"] == "pending_convergent_trait_hypothesis"]
    assert len(hypotheses) > 0
    assert set(hypotheses["status"]) == {"pending"}
    assert hypotheses["validation_ready"].astype(bool).all()
    assert not hypotheses["prediction_statement"].str.contains(
        "validated|established", case=False, regex=True
    ).any()
    assert hypotheses["expected_validation_source"].str.contains(
        "Wave 4 held-out convergence validation", regex=False
    ).all()

    non_predictions = pred[pred["row_class"] != "pending_convergent_trait_hypothesis"]
    assert not non_predictions["status"].eq("pending").any()
    assert not non_predictions["validation_ready"].astype(bool).any()
    assert not pred["enters_master_prediction_ledger"].astype(bool).any()


def test_confound_falsifier_recorded_and_not_hard_falsified():
    reg = pd.read_csv(DATA / "convergence_pressure_confound_regression.tsv", sep="\t")
    values = dict(zip(reg["name"], reg["coef"]))
    assert "R2_observed_H_family" in values
    assert "spearman_rho_residOBS_vs_CPmin" in values
    assert "verdict" in values
    assert values["verdict"] == "PASS"


def test_script_has_no_paid_provider_imports_or_substrate_writes():
    script = TRACK3 / "scripts" / "convergence_pressure.py"
    text = script.read_text()
    forbidden_tokens = [
        "imp" + "ort " + "anthropic",
        "imp" + "ort " + "openai",
        "fr" + "om " + "anthropic",
        "fr" + "om " + "openai",
        "go" + "ogle.genai",
        "go" + "ogle.generativeai",
    ]
    for token in forbidden_tokens:
        assert token not in text

    for line in text.splitlines():
        if "phytograph_dataset" in line:
            assert "to_parquet" not in line
            assert "to_csv" not in line
            assert "write_text" not in line
