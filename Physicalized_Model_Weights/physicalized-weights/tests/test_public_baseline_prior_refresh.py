# created: 2026-05-13T21:44:00Z
# cycle: 14
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-2

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "public_baseline_prior_refresh.py"
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"


def load_probe():
    spec = importlib.util.spec_from_file_location("public_baseline_prior_refresh", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_probe() -> dict:
    module = load_probe()
    return module.main()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def test_no_energy_prior_is_updated_from_rows_lacking_power_fields() -> None:
    run_probe()
    subset = read_csv(DATA / "public_baseline_mlperf_v6_subset.csv")
    mapping = read_csv(DATA / "public_baseline_campaign_mapping.csv")
    rows_without_power = {row["source_row_id"] for row in subset if row["has_power"] == "false"}
    energy_rows = [
        row for row in mapping
        if row["campaign_dimension"] == "programmable_accelerator_energy_prior"
        and row["source_row_id"] in rows_without_power
    ]
    assert energy_rows
    assert all(row["directly_calibratable"] == "no" for row in energy_rows)
    assert all(row["recommended_use"] == "do_not_update_energy" for row in energy_rows)


def test_public_benchmark_rows_cannot_set_actual_reopen_candidate_count() -> None:
    summary = run_probe()
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["public_sources_reopen_physicalized_claim"] is False


def test_phase2_downgrade_is_preserved() -> None:
    summary = run_probe()
    assert summary["phase2_downgrade_preserved"] is True
    assert summary["refresh_decision"] in {"strengthen_programmable_null", "not_calibratable_from_public_data"}


def test_every_mapped_row_has_required_blocker_fields() -> None:
    run_probe()
    mapping = read_csv(DATA / "public_baseline_campaign_mapping.csv")
    assert mapping
    for row in mapping:
        assert row["mapping_strength"]
        assert row["directly_calibratable"]
        assert row["calibration_blocker"]


def test_vendor_secondary_rows_are_not_used_as_primary_calibration_rows() -> None:
    summary = run_probe()
    assert summary["vendor_secondary_rows_used_for_primary_calibration"] == 0
    subset = read_csv(DATA / "public_baseline_mlperf_v6_subset.csv")
    assert all("nvidia.com" not in row["source_url"].lower() for row in subset)
    assert all("raw.githubusercontent.com/mlcommons/inference_results_v6.0" in row["source_url"] for row in subset)


def test_endpoint_counters_remain_zero_or_false() -> None:
    summary = run_probe()
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False
    assert summary["energy_values_inferred_from_throughput_only"] == 0


def test_report_distinguishes_baseline_refresh_from_hybrid_reopen_evidence() -> None:
    run_probe()
    text = (DOCS / "public_baseline_prior_refresh.md").read_text()
    assert "programmable-baseline priors" in text
    assert "not the campaign safety-filter production/shadow/canary workload" in text
    assert "not measured hybrid safety-filter production/shadow/canary evidence" in text
    assert "No energy value is inferred" in text


def test_outputs_exist_and_summary_schema_is_stable() -> None:
    summary = run_probe()
    for path in [
        DATA / "public_baseline_mlperf_v6_subset.csv",
        DATA / "public_baseline_campaign_mapping.csv",
        DATA / "public_baseline_prior_refresh.csv",
        DATA / "public_baseline_prior_refresh_summary.json",
        DATA / "public_baseline_prior_refresh.png",
        DOCS / "public_baseline_prior_refresh.md",
    ]:
        assert path.exists()
        assert path.stat().st_size > 0
    persisted = json.loads((DATA / "public_baseline_prior_refresh_summary.json").read_text())
    assert persisted["schema_version"] == 1
    assert persisted["milestone_id"] == "M-PUBLICBASE-2"
    assert persisted["direct_energy_calibration_rows"] == summary["direct_energy_calibration_rows"]


if __name__ == "__main__":
    tests = [
        test_no_energy_prior_is_updated_from_rows_lacking_power_fields,
        test_public_benchmark_rows_cannot_set_actual_reopen_candidate_count,
        test_phase2_downgrade_is_preserved,
        test_every_mapped_row_has_required_blocker_fields,
        test_vendor_secondary_rows_are_not_used_as_primary_calibration_rows,
        test_endpoint_counters_remain_zero_or_false,
        test_report_distinguishes_baseline_refresh_from_hybrid_reopen_evidence,
        test_outputs_exist_and_summary_schema_is_stable,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
