# created: 2026-05-18T14:05:00+00:00
# cycle: 20
# run_id: run-phytograph-cycle20-barrier4-closure-integration
# agent: worker
# milestone: _plan/barrier4-closure-integration

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read_tsv(path):
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_track1_sidecar_recovery_remains_below_h1_validation_threshold():
    rows = _read_tsv("tracks/track1/data/barrier4_canonical_key_recovery.tsv")
    assert len(rows) == 8

    current_recovered = [row for row in rows if row["current_accepted_key"]]
    full_wfo_recovered = [row for row in rows if row["rescued_accepted_key"]]
    event_with_synonym = [
        row for row in full_wfo_recovered if int(row["event_shaped_edges_attached"]) > 0
    ]
    exact_event = [
        row
        for row in event_with_synonym
        if row["rescue_status"] == "rescued_exact_full_wfo_taxon"
    ]

    assert len(current_recovered) == 0
    assert len(full_wfo_recovered) == 5
    assert len(event_with_synonym) == 3
    assert len(exact_event) == 2
    assert len(event_with_synonym) < 5


def test_track4_closure_has_no_climate_recommendation_support():
    summary = json.loads(
        (ROOT / "tracks/track4/data/crop_substitution_engine_summary.json").read_text(
            encoding="utf-8"
        )
    )
    candidates = _read_tsv("tracks/track4/data/crop_substitution_candidates.tsv")

    assert summary["observed_bioclim_vectors"] == 0
    assert summary["candidate_rows"] == 3
    assert summary["climate_claims_emitted"] is False
    assert {row["prediction_status"] for row in candidates} == {"pending_data_limited"}
    assert {row["validation_ready"] for row in candidates} == {"False"}
    assert {row["climate_match_status"] for row in candidates} == {
        "not_computable_no_observed_bioclim_vectors"
    }


def test_track6_closure_is_benchmark_only_without_model_error_rates():
    availability = json.loads(
        (ROOT / "tracks/track6/data/local_model_availability.json").read_text(
            encoding="utf-8"
        )
    )
    summary_rows = _read_tsv("tracks/track6/data/probe_model_summary.tsv")
    by_model = {row["model_id"]: row for row in summary_rows}

    assert availability["local_open_model_runnable"] is False
    assert availability["local_model_files"] == []
    assert availability["runtime_modules_available"] == {
        "llama_cpp": False,
        "torch": False,
        "transformers": False,
    }
    assert by_model["rubric_minimal_scoped_control"]["passed"] == "210"
    assert by_model["empty_response_control"]["passed"] == "0"
    assert by_model["forbidden_overclaim_control"]["passed"] == "0"
    assert by_model["verbatim_expected_answer_diagnostic"]["passed"] == "90"


def test_master_ledgers_remain_header_only_after_barrier4_closures():
    for path in ("prediction_ledger.tsv", "speculation_ledger.tsv"):
        lines = (ROOT / path).read_text(encoding="utf-8").splitlines()
        assert len(lines) == 1
