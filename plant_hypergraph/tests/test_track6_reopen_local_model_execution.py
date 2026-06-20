import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tracks" / "track6" / "scripts" / "build_reopen_local_model_execution.py"
REPORT_PATH = ROOT / "tracks" / "track6" / "reports" / "track6_reopen_local_model_execution.md"
AVAILABILITY_PATH = ROOT / "tracks" / "track6" / "data" / "local_model_availability_reopen.tsv"
RESPONSES_PATH = ROOT / "tracks" / "track6" / "data" / "local_model_probe_responses.tsv"
DIAGNOSTICS_PATH = ROOT / "tracks" / "track6" / "data" / "local_model_probe_scoring_diagnostics.tsv"
FIGURE_PATH = ROOT / "tracks" / "track6" / "figures" / "track6_reopen_execution_coverage.png"


def load_builder():
    spec = importlib.util.spec_from_file_location("track6_reopen_builder", BUILDER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_reopen_tables_obey_schema_and_null_execution_status():
    builder = load_builder()
    availability = pd.read_csv(AVAILABILITY_PATH, sep="\t", dtype=str).fillna("")
    responses = pd.read_csv(RESPONSES_PATH, sep="\t", dtype=str).fillna("")
    diagnostics = pd.read_csv(DIAGNOSTICS_PATH, sep="\t", dtype=str).fillna("")

    assert list(availability.columns) == builder.AVAILABILITY_COLUMNS
    assert list(responses.columns) == builder.RESPONSE_COLUMNS
    assert list(diagnostics.columns) == builder.DIAGNOSTIC_COLUMNS
    assert set(availability["runnable_flag"]) <= {"false", "true"}
    assert (availability["runnable_flag"] == "true").sum() == 0
    assert set(responses["execution_status"]) == {"not_run_no_local_model"}
    assert responses["response_text_digest"].eq("").all()
    assert diagnostics["runnable_response_count"].astype(int).sum() == 0
    assert diagnostics["scored_response_count"].astype(int).sum() == 0
    assert set(diagnostics["error_rate_claim_allowed"]) == {"false"}


def test_no_remote_or_keyed_provider_calls_are_configured():
    text = BUILDER_PATH.read_text().lower()
    forbidden = [
        "requests",
        "httpx",
        "socket",
        "anthropic",
        "openai",
        "google.generativeai",
        "gemini",
        "pl@ntnet",
        "inaturalist",
        "huggingface",
        "api_key",
    ]
    assert all(term not in text for term in forbidden)


def test_report_suppresses_model_claims_when_no_scored_responses():
    report = REPORT_PATH.read_text().lower()
    assert "determination: `no_new_qualifying_evidence`" in report
    assert "h6 therefore remains `environment_limited_untested`" in report
    assert "no model-performance, leaderboard, vendor-comparison, toxicity-safety, or failure-rate claim is promoted" in report
    assert "scored model responses: 0" in report
    assert "undefined here" in report


def test_static_benchmark_coverage_and_master_ledgers_remain_unpromoted():
    responses = pd.read_csv(RESPONSES_PATH, sep="\t")
    diagnostics = pd.read_csv(DIAGNOSTICS_PATH, sep="\t")
    prediction_lines = (ROOT / "prediction_ledger.tsv").read_text().splitlines()
    speculation_lines = (ROOT / "speculation_ledger.tsv").read_text().splitlines()

    assert len(responses) == 210
    assert diagnostics["static_benchmark_questions"].sum() == 210
    assert diagnostics["category"].nunique() == 7
    assert len(prediction_lines) == 1
    assert len(speculation_lines) == 1
    assert FIGURE_PATH.exists()
    assert FIGURE_PATH.stat().st_size > 1000
