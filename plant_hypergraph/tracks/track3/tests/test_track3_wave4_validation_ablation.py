from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd


WORKSPACE = Path(__file__).resolve().parents[3]
TRACK3 = WORKSPACE / "tracks" / "track3"
DATA = TRACK3 / "data"
FIGURES = TRACK3 / "figures"
REPORTS = TRACK3 / "reports"
SCRIPT = TRACK3 / "scripts" / "validate_wave4_convergence.py"


def regenerate() -> pd.DataFrame:
    subprocess.run(["python3", str(SCRIPT)], cwd=WORKSPACE, check=True)
    return pd.read_csv(DATA / "track3_wave4_validation_outcomes.tsv", sep="\t")


def test_wave4_outputs_are_regenerated():
    outcomes = regenerate()
    assert len(outcomes) == 16
    for path in [
        DATA / "track3_wave4_validation_outcomes.tsv",
        DATA / "track3_wave4_validation_summary.json",
        FIGURES / "track3_wave4_null_model_comparison.png",
        REPORTS / "track3_wave4_validation_ablation.md",
    ]:
        assert path.exists(), f"missing Wave 4 artifact: {path}"
        assert path.stat().st_size > 0, f"empty Wave 4 artifact: {path}"


def test_only_drupe_and_capsule_are_pending_hypotheses():
    outcomes = regenerate()
    pending = outcomes[outcomes["wave4_status"] == "pending_convergence_prior"]
    assert set(pending["trait"]) == {"drupe", "capsule"}

    summary = json.loads((DATA / "track3_wave4_validation_summary.json").read_text())
    assert summary["pending_traits"] == ["capsule", "drupe"]
    assert summary["h3_decision"] in {"data_limited", "not_validated_pending"}


def test_other_bucket_is_diagnostic_not_prediction():
    outcomes = regenerate()
    other = outcomes[outcomes["trait"] == "_other"].iloc[0]
    assert other["wave4_status"] == "diagnostic_not_prediction"
    assert other["enters_master_prediction_ledger"] in [False, "False"]
    assert "excluded_bucket" in other["special_handling"]


def test_zero_carrier_canonical_traits_are_data_limited():
    outcomes = regenerate()
    zero = outcomes[outcomes["trait"].isin(["ant_domatia", "carnivory", "parasitism"])]
    assert set(zero["wave4_status"]) == {"data_limited_not_prediction"}
    assert zero["special_handling"].str.contains("zero_carrier_trait", regex=False).all()


def test_null_degeneracy_cannot_produce_validated_status():
    outcomes = regenerate()
    degenerate = outcomes[
        outcomes["n1_null_std"].isna()
        | outcomes["n2_null_std"].isna()
        | outcomes["n1_null_std"].eq(0)
        | outcomes["n2_null_std"].eq(0)
    ]
    assert len(degenerate) >= 1
    assert not degenerate["wave4_status"].str.contains("validated", case=False, regex=False).any()


def test_no_rows_enter_master_prediction_ledger():
    outcomes = regenerate()
    assert not outcomes["enters_master_prediction_ledger"].astype(bool).any()

    prediction_lines = (WORKSPACE / "prediction_ledger.tsv").read_text().splitlines()
    speculation_lines = (WORKSPACE / "speculation_ledger.tsv").read_text().splitlines()
    assert len(prediction_lines) == 1
    assert len(speculation_lines) == 1
