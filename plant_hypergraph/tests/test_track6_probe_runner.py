import importlib.util
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tracks" / "track6" / "scripts" / "run_offline_probe.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("track6_runner", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_offline_runner_controls_discriminate_pass_and_fail(tmp_path):
    runner = load_runner()
    outputs = runner.run(
        results_path=tmp_path / "probe_results.tsv",
        model_summary_path=tmp_path / "probe_model_summary.tsv",
        category_summary_path=tmp_path / "probe_category_summary.tsv",
        availability_path=tmp_path / "local_model_availability.json",
        figure_path=tmp_path / "offline_probe_error_by_category.png",
        report_path=tmp_path / "track6_foundation_model_probe.md",
        make_plot=False,
    )
    results = pd.read_csv(outputs["results"], sep="\t")
    summary = pd.read_csv(outputs["model_summary"], sep="\t")

    assert len(results) == 210 * 4
    pass_rates = dict(zip(summary["model_id"], summary["pass_rate"]))
    assert pass_rates["rubric_minimal_scoped_control"] == 1.0
    assert pass_rates["empty_response_control"] == 0.0
    assert pass_rates["forbidden_overclaim_control"] == 0.0
    assert 0.0 < pass_rates["verbatim_expected_answer_diagnostic"] < 1.0


def test_offline_runner_outputs_required_report_and_no_provider_execution(tmp_path):
    runner = load_runner()
    outputs = runner.run(
        results_path=tmp_path / "probe_results.tsv",
        model_summary_path=tmp_path / "probe_model_summary.tsv",
        category_summary_path=tmp_path / "probe_category_summary.tsv",
        availability_path=tmp_path / "local_model_availability.json",
        figure_path=tmp_path / "offline_probe_error_by_category.png",
        report_path=tmp_path / "track6_foundation_model_probe.md",
        make_plot=False,
    )
    results = pd.read_csv(outputs["results"], sep="\t")
    assert set(results["provider_execution"]) == {"none"}
    assert results["offline_only"].all()
    report = outputs["report"].read_text()
    assert "benchmark-only / data-limited for model execution" in report
    assert "not model performance measurements" in report


def test_runner_source_uses_no_network_or_provider_client_imports():
    text = RUNNER_PATH.read_text()
    forbidden = [
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "anthropic",
        "openai",
        "google.generativeai",
        "pl@ntnet",
        "inaturalist",
    ]
    assert all(term not in text.lower() for term in forbidden)
