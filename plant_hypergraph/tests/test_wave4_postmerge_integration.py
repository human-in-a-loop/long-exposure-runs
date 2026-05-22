# created: 2026-05-18T11:00:00+00:00
# cycle: 14
# run_id: run-phytograph-cycle14-wave4-postmerge-integration
# agent: worker
# milestone: _plan/wave4-postmerge-integration

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_tsv(path):
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_track2_closure_is_null_and_track_local():
    rows = _read_tsv("tracks/track2/data/track2_wave4_validation_outcomes.tsv")
    assert len(rows) == 8
    assert {row["enters_master_prediction_ledger"] for row in rows} == {"False"}
    assert {row["inferred_anachronism_claim"] for row in rows} == {"False"}

    status_counts = {}
    for row in rows:
        status_counts[row["wave4_outcome_status"]] = status_counts.get(row["wave4_outcome_status"], 0) + 1

    assert status_counts == {
        "data_limited": 6,
        "insufficient_support": 1,
        "falsified": 1,
    }


def test_track3_child_milestone_is_explicit_and_not_promoted():
    plan = (ROOT / "plan_of_record.md").read_text(encoding="utf-8")
    assert "M4.A-track3-convergence-confounds" in plan

    rows = _read_tsv("tracks/track3/data/track3_wave4_validation_outcomes.tsv")
    assert {row["enters_master_prediction_ledger"] for row in rows} == {"False"}
    assert sorted(
        row["trait"] for row in rows if row["wave4_status"] == "pending_convergence_prior"
    ) == ["capsule", "drupe"]

    summary = json.loads(
        (ROOT / "tracks/track3/data/track3_wave4_validation_summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert summary["h3_decision"] == "data_limited"
    assert summary["master_ledgers_promoted"] is False


def test_track5_temporal_and_source_closure_counts():
    rows = _read_tsv("tracks/track5/data/track5_wave4_validation_outcomes.tsv")
    temporal = [row for row in rows if row["row_type"] == "temporal_holdout"]
    variants = {row["variant"]: row for row in rows if row["row_type"] == "source_ablation"}

    assert len(temporal) == 8
    assert {row["top_decile"] for row in temporal} == {"False"}
    assert {row["cutoff_status"] for row in temporal} == {"no_assertion_dates_available"}

    assert variants["full"]["prediction_count"] == "1405"
    assert variants["no_duke"]["prediction_count"] == "0"
    assert variants["source_density_matched"]["prediction_count"] == "0"
    assert variants["screening_count_matched"]["prediction_count"] == "0"


def test_master_prediction_and_speculation_ledgers_remain_header_only():
    for path in ("prediction_ledger.tsv", "speculation_ledger.tsv"):
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
