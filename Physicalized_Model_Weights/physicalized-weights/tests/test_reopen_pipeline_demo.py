# created: 2026-05-13T10:24:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PIPELINE-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "reopen_pipeline_demo.py"
spec = importlib.util.spec_from_file_location("reopen_pipeline_demo", SCRIPT_PATH)
pipeline = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["reopen_pipeline_demo"] = pipeline
spec.loader.exec_module(pipeline)


def load_results() -> dict[str, dict[str, str]]:
    with pipeline.RESULTS_CSV.open(newline="") as f:
        return {Path(row["trace_file"]).name: row for row in csv.DictReader(f)}


def load_summary() -> dict[str, object]:
    return json.loads(pipeline.SUMMARY_JSON.read_text())


def test_invalid_privacy_fixture_ends_as_invalid_trace() -> None:
    row = load_results()["pipeline_trace_invalid_privacy.csv"]
    assert row["trace_validation_status"] == "invalid_privacy_risk"
    assert row["final_status"] == "invalid_trace"
    assert row["actual_reopen_candidate"] == "False"


def test_valid_insufficient_fixture_ends_as_valid_but_insufficient() -> None:
    row = load_results()["pipeline_trace_valid_insufficient.csv"]
    assert row["trace_validation_status"] == "valid_but_insufficient"
    assert row["ingestion_class"] == "valid_but_insufficient"
    assert row["measurement_status"] == "proxy"
    assert row["final_status"] == "valid_but_insufficient"


def test_threshold_evaluable_not_crossed_fixture() -> None:
    row = load_results()["pipeline_trace_threshold_evaluable_not_crossed.csv"]
    assert row["trace_validation_status"] == "valid_reopen_candidate"
    assert row["ingestion_class"] == "reopen_candidate_path"
    assert row["threshold_crossed"] == "False"
    assert row["final_status"] == "threshold_evaluable_not_crossed"


def test_synthetic_counterfactual_crosses_without_actual_reopen() -> None:
    row = load_results()["pipeline_trace_synthetic_counterfactual_crossed.csv"]
    assert row["threshold_crossed"] == "True"
    assert row["evidence_source_type"] == "synthetic"
    assert row["final_status"] == "synthetic_counterfactual_crossed"
    assert row["actual_reopen_candidate"] == "False"


def test_no_synthetic_or_proxy_fixture_can_be_actual_reopen_candidate() -> None:
    for row in load_results().values():
        if row["evidence_source_type"] == "synthetic" or row["measurement_status"] == "proxy":
            assert row["actual_reopen_candidate"] == "False"


def test_actual_reopen_candidate_requires_all_conjuncts() -> None:
    schema = pipeline.load_schema()
    ingestion_scores = pipeline.load_ingestion_scores()
    thresholds = pipeline.load_thresholds()
    path = temp_path("actual_candidate")
    pipeline.write_trace(
        path,
        [
            pipeline.base_row(
                1000,
                evidence_source_type="production",
                measurement_environment="production",
                ingestion_path_id="shadow_production_dual_run",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
            pipeline.base_row(
                2000,
                evidence_source_type="production",
                measurement_environment="production",
                ingestion_path_id="shadow_production_dual_run",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
        ],
    )
    result = pipeline.evaluate_trace(path, schema, ingestion_scores, thresholds)
    assert result["m_trace_1_valid_reopen_candidate"] == "True"
    assert result["m_ingest_1_reopen_candidate_path"] == "True"
    assert result["measured_terms_sufficient"] == "True"
    assert result["evidence_source_type"] == "production"
    assert result["provenance_attestation"] == "True"
    assert result["threshold_crossed"] == "True"
    assert result["final_status"] == "actual_reopen_candidate"

    no_provenance = temp_path("actual_candidate_no_provenance")
    pipeline.write_trace(
        no_provenance,
        [
            pipeline.base_row(
                1000,
                evidence_source_type="production",
                measurement_environment="production",
                ingestion_path_id="shadow_production_dual_run",
                provenance_attestation="false",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            )
        ],
    )
    blocked = pipeline.evaluate_trace(no_provenance, schema, ingestion_scores, thresholds)
    assert blocked["final_status"] != "actual_reopen_candidate"
    assert "provenance_attestation=false" in blocked["primary_blockers"]


def test_current_summary_has_zero_actual_reopen_candidates() -> None:
    summary = load_summary()
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["synthetic_or_proxy_actual_reopen_candidates"] == []


def test_output_schemas_are_stable_and_figure_exists() -> None:
    with pipeline.RESULTS_CSV.open(newline="") as f:
        assert csv.DictReader(f).fieldnames == [
            "trace_file",
            "scenario_id",
            "trace_validation_status",
            "ingestion_path_id",
            "ingestion_class",
            "evidence_source_type",
            "measurement_status",
            "provenance_attestation",
            "measured_terms_sufficient",
            "m_trace_1_valid_reopen_candidate",
            "m_ingest_1_reopen_candidate_path",
            "requests",
            "accepted_fast_path_requests",
            "accelerator_energy_sum_pj",
            "hybrid_energy_sum_pj",
            "required_reduction_to_tie_pj_equivalent",
            "threshold_margin_pj_equivalent",
            "threshold_crossed",
            "final_status",
            "actual_reopen_candidate",
            "primary_blockers",
        ]
    assert pipeline.OUTPUT_PNG.exists()
    assert pipeline.OUTPUT_PNG.stat().st_size > 100


def temp_path(name: str) -> Path:
    directory = Path(tempfile.gettempdir()) / "physicalized_reopen_pipeline_tests"
    directory.mkdir(exist_ok=True)
    return directory / f"{name}.csv"


if __name__ == "__main__":
    pipeline.main()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
