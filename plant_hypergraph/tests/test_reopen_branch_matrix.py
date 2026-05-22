# created: 2026-05-18T15:20:00+00:00
# cycle: 22
# run_id: run-phytograph-cycle22-reopen-evidence-gate
# agent: worker
# milestone: _plan/reopen-evidence-gate

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/reopen/reopen_branch_matrix.tsv"

REQUIRED_COLUMNS = [
    "track",
    "closed_status",
    "missing_evidence",
    "candidate_source",
    "access_mode",
    "minimum_rows_or_coverage",
    "required_join_key",
    "first_validation_test",
    "promotion_risk",
    "recommended_priority",
]

ALLOWED_STATUSES = {
    "H1_data_limited",
    "H4_data_limited",
    "H5_not_validated_source_biased",
    "H6_environment_limited_untested",
}

ALLOWED_PRIORITIES = {"high", "medium-high", "medium", "low", "no-reopen"}

CLAIM_LIKE_TERMS = {
    "recommendation",
    "recommendations",
    "validated",
    "error-rate",
    "bioactivity",
    "climate-substitution",
}


def _rows():
    with MATRIX.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_reopen_matrix_has_required_columns_and_tracks():
    rows = _rows()
    assert rows
    assert list(rows[0]) == REQUIRED_COLUMNS
    assert {row["track"] for row in rows} == {"Track 1", "Track 4", "Track 5", "Track 6"}


def test_reopen_matrix_uses_allowed_statuses_and_priorities():
    for row in _rows():
        assert row["closed_status"] in ALLOWED_STATUSES
        assert row["recommended_priority"] in ALLOWED_PRIORITIES


def test_every_branch_names_evidence_join_key_coverage_and_validation():
    for row in _rows():
        assert row["missing_evidence"].strip()
        assert row["candidate_source"].strip()
        assert row["minimum_rows_or_coverage"].strip()
        assert row["required_join_key"].strip()
        assert row["first_validation_test"].strip()
        assert "test" in row["first_validation_test"].lower() or "control" in row["first_validation_test"].lower()


def test_claim_like_language_has_validation_test_and_promotion_risk():
    for row in _rows():
        text = "\t".join(row.values()).lower()
        if any(term in text for term in CLAIM_LIKE_TERMS):
            assert row["first_validation_test"].strip()
            assert row["promotion_risk"].strip()


def test_master_ledgers_remain_header_only():
    for path in ("prediction_ledger.tsv", "speculation_ledger.tsv"):
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
