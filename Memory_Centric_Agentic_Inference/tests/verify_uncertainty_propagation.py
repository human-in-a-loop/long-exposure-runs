#!/usr/bin/env python3
# created: 2026-05-12T13:15:00Z
# cycle: 34
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-UNCERT-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED_INVALID = {
    "invalid-missing-variance-noise-model": ("statistical_invalid", "missing_variance"),
    "invalid-insufficient-sample-count": ("statistically_indeterminate", "insufficient_sample_count"),
    "invalid-ci-crosses-threshold": ("statistically_indeterminate", "confidence_interval_crosses_threshold"),
    "invalid-ci-touches-threshold": ("statistically_indeterminate", "confidence_interval_touches_threshold"),
    "invalid-unbounded-p99-latency-ci": ("statistical_invalid", "unbounded_p99_latency_ci"),
    "invalid-drift-between-windows": ("statistically_indeterminate", "control_treatment_drift_exceeds_budget"),
    "invalid-missing-control-arm": ("statistical_invalid", "missing_control_arm"),
    "invalid-non-independent-repeated-samples": ("statistically_indeterminate", "non_independent_repeated_samples"),
    "invalid-negative-variance": ("statistical_invalid", "negative_variance"),
    "invalid-nan-metric": ("statistical_invalid", "nan_metric"),
    "invalid-missing-noise-model": ("statistical_invalid", "missing_noise_model"),
    "invalid-zero-samples": ("statistical_invalid", "nonpositive_sample_count"),
    "invalid-unknown-source-fixture": ("statistical_invalid", "unknown_source_fixture_id"),
    "invalid-fixture-attempted-production-calibration": ("statistical_invalid", "fixture_attempted_production_calibration"),
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
    schema = read_csv(DATA / "uncertainty_schema.csv")
    valid = read_csv(DATA / "uncertainty_valid_fixture.csv")
    invalid = read_csv(DATA / "uncertainty_invalid_fixtures.csv")
    grid = read_csv(DATA / "uncertainty_sensitivity_grid.csv")
    results = read_csv(DATA / "uncertainty_evaluation_results.csv")
    failures = read_csv(DATA / "uncertainty_failure_modes.csv")
    threshold = read_csv(DATA / "uncertainty_threshold_boundary.csv")
    claim = read_csv(DATA / "uncertainty_claim_readiness_boundary.csv")

    schema_fields = {row["field_name"] for row in schema}
    for required in {"variance", "sample_count", "ci_lower", "ci_upper", "noise_model_id", "control_window_id", "drift_fraction", "independent_samples"}:
        assert required in schema_fields
    assert len(valid) == 2
    assert len(invalid) == len(EXPECTED_INVALID)
    assert {"robust_pass", "robust_fail", "statistically_indeterminate"} <= {row["threshold_status"] for row in grid}

    result = by_case(results)
    complete = result["valid-confidence-qualified-fixture"]
    assert complete["threshold_status"] == "robust_pass"
    assert complete["point_estimate_passed"] == "true"
    assert complete["readiness_update_allowed"] == "false"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    robust_fail = result["valid-confidence-qualified-fail-fixture"]
    assert robust_fail["threshold_status"] == "robust_fail"
    assert robust_fail["point_estimate_passed"] == "false"
    assert robust_fail["readiness_update_allowed"] == "false"
    assert robust_fail["production_calibrated"] == "false"
    assert robust_fail["production_ready"] == "false"
    assert robust_fail["claim_credit_allowed"] == "false"
    assert {"robust_pass", "robust_fail", "statistically_indeterminate"} <= {row["threshold_status"] for row in results}

    for case_id, (status, reason) in EXPECTED_INVALID.items():
        row = result[case_id]
        assert row["threshold_status"] == status
        assert row["blocked_reason"] == reason
        assert row["expected_reason_matched"] == "true"
        assert row["readiness_update_allowed"] == "false"

    assert result["invalid-ci-crosses-threshold"]["point_estimate_passed"] == "true"
    assert result["invalid-ci-crosses-threshold"]["threshold_status"] == "statistically_indeterminate"
    assert result["invalid-ci-touches-threshold"]["threshold_status"] == "statistically_indeterminate"
    assert result["invalid-drift-between-windows"]["threshold_status"] == "statistically_indeterminate"
    assert result["invalid-missing-control-arm"]["threshold_status"] == "statistical_invalid"
    assert result["invalid-negative-variance"]["blocked_reason"] == "negative_variance"
    assert result["invalid-nan-metric"]["blocked_reason"] == "nan_metric"

    assert all(row["fail_closed"] == "true" for row in failures)
    assert any(row["threshold_status"] == "statistical_invalid" for row in failures)
    assert any(row["threshold_status"] == "statistically_indeterminate" for row in failures)
    assert all(row["point_estimate_pass_is_sufficient"] == "false" for row in threshold)
    assert all(row["indeterminate_can_update_readiness"] == "false" for row in threshold)
    assert all(row["production_calibrated"] == "false" for row in claim)
    assert all(row["production_ready"] == "false" for row in claim)
    assert all(row["claim_credit_allowed"] == "false" for row in claim)

    for fig in [
        DATA / "uncertainty_threshold_sensitivity.png",
        DATA / "uncertainty_failure_modes.png",
        DATA / "uncertainty_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: uncertainty propagation verified.")


if __name__ == "__main__":
    main()
