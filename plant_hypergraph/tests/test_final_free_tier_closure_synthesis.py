#!/usr/bin/env python3
# created: 2026-05-18T23:59:59+00:00
# cycle: 33
# run_id: run-phytograph-cycle33-final-free-tier-closure-synthesis
# agent: worker
# milestone: _plan/final-free-tier-closure-synthesis

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "data/reopen/final_free_tier_track_status.tsv"
REPORT = ROOT / "reports/reopen/final_free_tier_closure_synthesis.md"
FIGURE = ROOT / "reports/reopen/figures/final_free_tier_track_status.png"
ROOT_AND_REOPEN_DOCS = [
    ROOT / "final_report.md",
    ROOT / "audit_report.md",
    ROOT / "research_contribution_ledger.md",
    ROOT / "falsification_and_ablation_report.md",
    ROOT / "artifact_index.md",
    ROOT / "reports/reopen/reopen_closure_addendum.md",
    ROOT / "reports/reopen/free_tier_recovery_integration.md",
    REPORT,
]

EXPECTED_STATUS = {
    "Track 1": "sidecar_readiness_uncontrolled",
    "Track 2": "H2_remains_not_supported_or_data_limited",
    "Track 3": "confound_limited",
    "Track 4": "still_data_limited",
    "Track 5": "H5_remains_source_biased",
    "Track 6": "environment_limited_untested",
}


def _read_tsv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_final_status_table_has_exactly_one_row_per_track():
    rows = _read_tsv(STATUS)
    assert [row["track"] for row in rows] == list(EXPECTED_STATUS)
    assert {row["track"]: row["final_free_tier_status"] for row in rows} == EXPECTED_STATUS
    assert set(rows[0]) == {
        "track",
        "final_free_tier_status",
        "validated_branch_basis",
        "key_counts",
        "blocker",
        "future_data_required",
        "master_ledger_action",
        "claim_boundary",
    }


def test_status_table_records_blockers_and_future_data_requirements():
    rows = {row["track"]: row for row in _read_tsv(STATUS)}
    assert "22 GBIF event taxa" in rows["Track 1"]["key_counts"]
    assert "2 WFO-projected taxa" in rows["Track 1"]["key_counts"]
    assert "source-density controls" in rows["Track 1"]["blocker"]
    assert "0/8 canonical held-outs pass validation contract" in rows["Track 2"]["key_counts"]
    assert "3069 accepted-key trait carrier rows" in rows["Track 3"]["key_counts"]
    assert "0 numeric BIOCLIM vectors" in rows["Track 4"]["key_counts"]
    assert "no validation-ready structured family/class stratum" in rows["Track 5"]["key_counts"]
    assert "0 executed responses" in rows["Track 6"]["key_counts"]
    for row in rows.values():
        assert row["master_ledger_action"].startswith("no_master_prediction_or_speculation_row")
        assert "No " in row["claim_boundary"]
        assert row["future_data_required"]


def test_root_and_reopen_docs_agree_on_all_final_statuses():
    for path in ROOT_AND_REOPEN_DOCS:
        text = path.read_text(encoding="utf-8")
        for status in EXPECTED_STATUS.values():
            assert status in text, f"{status!r} missing from {path}"
    for path in (ROOT / "final_report.md", ROOT / "audit_report.md", REPORT):
        text = path.read_text(encoding="utf-8")
        normalized = " ".join(text.split())
        assert "one validated prediction per track remains unmet" in normalized or (
            "validated-prediction-per-track criterion remains unmet" in normalized
        ) or ("does not currently satisfy the original research success criterion" in normalized) or (
            "original research success criterion" in normalized
            and "validated prediction per track" in normalized
        )


def test_final_synthesis_preserves_non_promotion_boundary_and_figure():
    text = REPORT.read_text(encoding="utf-8")
    forbidden = [
        "establishes a new reticulation",
        "validated anachronism",
        "validated convergence",
        "promotes a crop-substitution recommendation",
        "new phytochemical detection",
        "model error rate",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "header-only" in text
    assert FIGURE.exists()
    assert FIGURE.stat().st_size > 10_000


def test_master_ledgers_remain_header_only():
    for path in (ROOT / "prediction_ledger.tsv", ROOT / "speculation_ledger.tsv"):
        assert len(path.read_text(encoding="utf-8").splitlines()) == 1
