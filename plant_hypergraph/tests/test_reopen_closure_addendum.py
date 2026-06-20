# created: 2026-05-18T20:05:00+00:00
# cycle: 28
# run_id: run-phytograph-cycle28-free-tier-recovery-integration
# agent: worker
# milestone: _plan/free-tier-recovery-integration

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/reopen/reopen_closure_status.tsv"
ADDENDUM = ROOT / "reports/reopen/reopen_closure_addendum.md"


def test_all_reopen_branch_statuses_are_represented():
    df = pd.read_csv(STATUS, sep="\t", dtype=str)
    assert set(df["track"]) == {"Track 1", "Track 2", "Track 3", "Track 4", "Track 5", "Track 6"}
    assert dict(zip(df["track"], df["result"])) == {
        "Track 1": "branch_local_threshold_met_reconciliation_pending",
        "Track 2": "H2_remains_not_supported_or_data_limited",
        "Track 3": "confound_limited",
        "Track 4": "still_data_limited",
        "Track 5": "insufficient_non_duke_temporal_evidence_h5_remains_source_biased",
        "Track 6": "no_new_qualifying_evidence",
    }
    assert all(df["master_ledger_action"].str.contains("non_promotion"))


def test_master_ledgers_remain_header_only():
    for name in ["prediction_ledger.tsv", "speculation_ledger.tsv"]:
        lines = (ROOT / name).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1, name


def test_closure_text_avoids_unsupported_claim_language():
    text = ADDENDUM.read_text(encoding="utf-8").lower()
    forbidden_phrases = [
        "new hybridization discovered",
        "new bioactivity",
        "climate recommendation",
        "recommended substitute",
        "model error rate",
        "toxicity safety claim",
        "validated prediction",
        "established novelty",
    ]
    for phrase in forbidden_phrases:
        assert phrase not in text
    assert "error rates are undefined" in text
    assert "no master prediction or speculation row" in text
    assert "header-only by design" in text
    assert "reconciliation-pending at master level" in text


def test_future_data_recipes_are_predicates_not_recommendations():
    df = pd.read_csv(STATUS, sep="\t", dtype=str)
    assert all(value.startswith("Predicate:") for value in df["allowed_future_reopen_evidence"])
    combined = "\n".join(df["allowed_future_reopen_evidence"]).lower()
    assert "recommend " not in combined
    assert "recommended" not in combined
    assert "should use" not in combined
    assert "must" in combined


def test_reopen_figure_exists():
    figure = ROOT / "reports/reopen/figures/reopen_branch_outcomes.png"
    assert figure.exists()
    assert figure.stat().st_size > 1000
