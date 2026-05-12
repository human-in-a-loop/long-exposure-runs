#!/usr/bin/env python3
# created: 2026-05-12T11:15:00Z
# cycle: 32
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TIMEBASE-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_FIELDS = {
    "clock_domain_id",
    "clock_sync_source",
    "clock_sync_status",
    "interval_id",
    "interval_start_ms",
    "interval_end_ms",
    "byte_interval_start_ms",
    "byte_interval_end_ms",
    "power_interval_start_ms",
    "power_interval_end_ms",
    "latency_interval_start_ms",
    "latency_interval_end_ms",
    "queue_interval_start_ms",
    "queue_interval_end_ms",
    "security_interval_start_ms",
    "security_interval_end_ms",
    "sampling_period_ms",
    "sampling_jitter_ms",
    "max_cross_source_skew_ms",
    "skew_tolerance_ms",
    "jitter_tolerance_ms",
    "workload_label_sampled_at_ms",
    "workload_label_max_age_ms",
    "collector_overhead_pct",
    "observer_perturbation_budget_pct",
    "counter_sequence_start",
    "counter_sequence_end",
    "counter_reset_observed",
    "clock_drift_ppm",
    "clock_drift_tolerance_ppm",
}

EXPECTED_INVALID = {
    "invalid-unknown-source-fixture": "unknown_source_fixture_id",
    "invalid-measurement-run-id-mismatch": "measurement_run_id_mismatch",
    "invalid-bundle-id-mismatch": "bundle_id_mismatch",
    "invalid-collector-id-mismatch": "collector_id_mismatch",
    "invalid-schema-version-mismatch": "schema_version_mismatch",
    "invalid-missing-clock-domain": "missing_clock_domain",
    "invalid-cross-source-skew": "cross_source_skew_above_tolerance",
    "invalid-negative-skew": "negative_cross_source_skew",
    "invalid-interval-overlap-mismatch": "interval_overlap_mismatch",
    "invalid-interval-gap": "interval_gap",
    "invalid-inconsistent-sampling-period": "inconsistent_sampling_period",
    "invalid-zero-sampling-period": "non_positive_sampling_period",
    "invalid-negative-jitter": "negative_sampling_jitter",
    "invalid-stale-workload-label": "stale_workload_label",
    "invalid-missing-overhead-estimate": "missing_collector_overhead_estimate",
    "invalid-overhead-above-budget": "observer_overhead_above_budget",
    "invalid-negative-overhead": "negative_collector_overhead",
    "invalid-counter-reset-inside-interval": "counter_reset_inside_interval",
    "invalid-clock-drift-across-bundle": "clock_drift_across_bundle",
    "invalid-negative-clock-drift": "negative_clock_drift",
    "invalid-fixture-attempted-production-calibration": "fixture_attempted_production_calibration",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def by_case(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["case_id"]: row for row in rows}


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "timebase_integrity_schema.csv")
    valid = read_csv(DATA / "timebase_valid_fixture.csv")
    invalid = read_csv(DATA / "timebase_invalid_fixtures.csv")
    sensitivity = read_csv(DATA / "timebase_threshold_sensitivity_cases.csv")
    results = read_csv(DATA / "timebase_integrity_results.csv")
    failures = read_csv(DATA / "timebase_failure_modes.csv")
    replay_boundary = read_csv(DATA / "timebase_threshold_replay_boundary.csv")
    claim_boundary = read_csv(DATA / "timebase_claim_credit_boundary.csv")

    schema_fields = {row["field_name"] for row in schema if row["required"] == "true"}
    assert REQUIRED_FIELDS <= schema_fields
    assert len(valid) == 1
    assert len(invalid) == len(EXPECTED_INVALID)

    result = by_case(results)
    complete = result["valid-timebase-complete-fixture"]
    assert complete["timing_admissible"] == "true"
    assert complete["threshold_replay_status"] == "threshold_passed"
    assert complete["threshold_crossed_if_valid"] == "true"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    for case_id, reason in EXPECTED_INVALID.items():
        assert result[case_id]["timing_admissible"] == "false"
        assert result[case_id]["blocked_reason"] == reason
        assert result[case_id]["expected_reason_matched"] == "true"
        assert result[case_id]["threshold_replay_status"] == "measurement_invalid"

    assert all(row["fail_closed"] == "true" and row["replay_status"] == "measurement_invalid" for row in failures)
    assert all(row["invalid_timing_is_threshold_miss"] == "false" for row in replay_boundary)
    assert all(row["threshold_replay_status"] != "threshold_failed" for row in replay_boundary if row["timing_admissible"] == "false")
    assert result["invalid-unknown-source-fixture"]["blocked_field"] == "source_fixture_id"
    assert result["invalid-measurement-run-id-mismatch"]["blocked_field"] == "measurement_run_id"
    assert result["invalid-bundle-id-mismatch"]["blocked_field"] == "bundle_id"
    assert result["invalid-collector-id-mismatch"]["blocked_field"] == "collector_id"
    assert result["invalid-schema-version-mismatch"]["blocked_field"] == "schema_version"
    assert result["invalid-overhead-above-budget"]["blocked_field"] == "collector_overhead_pct"
    assert result["invalid-zero-sampling-period"]["blocked_field"] == "sampling_period_ms"
    assert result["invalid-negative-skew"]["blocked_field"] == "max_cross_source_skew_ms"
    assert result["invalid-negative-jitter"]["blocked_field"] == "sampling_jitter_ms"
    assert result["invalid-negative-overhead"]["blocked_field"] == "collector_overhead_pct"
    assert result["invalid-negative-clock-drift"]["blocked_field"] == "clock_drift_ppm"
    assert all(row["production_calibrated"] == "false" for row in claim_boundary)
    assert all(row["production_ready"] == "false" for row in claim_boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in claim_boundary)
    assert any(row["skew_ms"] == "0" and row["threshold_replay_status"] == "threshold_passed" for row in sensitivity)
    assert any(row["skew_ms"] == "75" and row["threshold_replay_status"] == "measurement_invalid" for row in sensitivity)
    assert any(row["collector_overhead_pct"] == "5.0" and row["threshold_replay_status"] == "measurement_invalid" for row in sensitivity)

    for fig in [
        DATA / "timebase_skew_sensitivity.png",
        DATA / "timebase_failure_modes.png",
        DATA / "timebase_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: timebase integrity verified.")


if __name__ == "__main__":
    main()
