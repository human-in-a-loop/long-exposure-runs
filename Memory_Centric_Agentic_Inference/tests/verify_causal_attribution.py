#!/usr/bin/env python3
# created: 2026-05-12T14:15:00Z
# cycle: 35
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CAUSAL-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

EXPECTED_INVALID = {
    "invalid-missing-option-a-control": ("causally_unidentified", "missing_option_a_control"),
    "invalid-workload-mix-mismatch": ("causally_confounded", "workload_mix_mismatch"),
    "invalid-model-version-mismatch": ("causally_confounded", "model_version_mismatch"),
    "invalid-topology-mismatch": ("causally_confounded", "topology_mismatch"),
    "invalid-tenant-concurrency-imbalance": ("causally_confounded", "tenant_concurrency_imbalance"),
    "invalid-object-size-distribution-shift": ("causally_confounded", "object_size_distribution_shift"),
    "invalid-cache-warmness-imbalance": ("causally_confounded", "cache_warmness_imbalance"),
    "invalid-security-deny-rate-shift": ("causally_confounded", "security_deny_rate_shift"),
    "invalid-time-window-drift": ("causally_confounded", "time_window_drift"),
    "invalid-post-treatment-covariate-leakage": ("causally_unidentified", "post_treatment_covariate_leakage"),
    "invalid-insufficient-overlap-positivity": ("causally_unidentified", "insufficient_overlap_positivity"),
    "invalid-missing-covariate-contract": ("causally_unidentified", "missing_pre_treatment_covariate_contract"),
    "invalid-scheduler-load-imbalance": ("causally_confounded", "scheduler_load_imbalance"),
    "invalid-fixture-attempted-production-calibration": ("causally_unidentified", "fixture_attempted_production_calibration"),
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
    schema = read_csv(DATA / "causal_attribution_schema.csv")
    valid = read_csv(DATA / "causal_valid_fixture.csv")
    invalid = read_csv(DATA / "causal_invalid_fixtures.csv")
    grid = read_csv(DATA / "causal_confounder_sensitivity_grid.csv")
    covariates = read_csv(DATA / "causal_required_covariates.csv")
    results = read_csv(DATA / "causal_attribution_results.csv")
    failures = read_csv(DATA / "causal_failure_modes.csv")
    threshold = read_csv(DATA / "causal_threshold_boundary.csv")
    claim = read_csv(DATA / "causal_claim_readiness_boundary.csv")

    schema_fields = {row["field_name"] for row in schema}
    for required in {"control_arm_present", "workload_mix_smd", "topology_match", "model_version_match", "positivity_overlap_fraction", "post_treatment_covariate_used"}:
        assert required in schema_fields
    assert len(valid) == 2
    assert len(invalid) == len(EXPECTED_INVALID)
    assert {"causally_admissible", "causally_confounded", "causally_unidentified"} <= {row["causal_status"] for row in grid}
    assert len(covariates) >= 10
    assert any(row["temporal_role"] == "post_treatment" and row["required_handling"] == "forbidden_adjustment" for row in covariates)

    result = by_case(results)
    complete = result["valid-causally-admissible-fixture"]
    assert complete["statistical_threshold_status"] == "robust_pass"
    assert complete["robust_statistical_effect"] == "true"
    assert complete["causal_status"] == "causally_admissible"
    assert complete["causal_support_eligible"] == "false"
    assert complete["production_calibrated"] == "false"
    assert complete["production_ready"] == "false"
    assert complete["claim_credit_allowed"] == "false"

    robust_fail = result["valid-causally-admissible-robust-fail-fixture"]
    assert robust_fail["statistical_threshold_status"] == "robust_fail"
    assert robust_fail["robust_statistical_effect"] == "false"
    assert robust_fail["causal_status"] == "causally_admissible"
    assert robust_fail["readiness_update_allowed"] == "false"

    for case_id, (status, reason) in EXPECTED_INVALID.items():
        row = result[case_id]
        assert row["causal_status"] == status
        assert row["blocked_reason"] == reason
        assert row["expected_reason_matched"] == "true"
        assert row["readiness_update_allowed"] == "false"

    assert result["invalid-workload-mix-mismatch"]["robust_statistical_effect"] == "true"
    assert result["invalid-workload-mix-mismatch"]["causal_status"] == "causally_confounded"
    assert result["invalid-insufficient-overlap-positivity"]["causal_status"] == "causally_unidentified"
    assert result["invalid-post-treatment-covariate-leakage"]["blocked_reason"] == "post_treatment_covariate_leakage"
    assert result["invalid-missing-option-a-control"]["blocked_reason"] == "missing_option_a_control"

    assert all(row["fail_closed"] == "true" for row in failures)
    assert any(row["causal_status"] == "causally_confounded" for row in failures)
    assert any(row["causal_status"] == "causally_unidentified" for row in failures)
    assert all(row["robust_effect_is_sufficient"] == "false" for row in threshold)
    assert all(row["confounded_can_update_readiness"] == "false" for row in threshold)
    assert any(row["robust_but_confounded"] == "true" for row in threshold)
    assert all(row["production_calibrated"] == "false" for row in claim)
    assert all(row["production_ready"] == "false" for row in claim)
    assert all(row["claim_credit_allowed"] == "false" for row in claim)

    for fig in [
        DATA / "causal_confounder_sensitivity.png",
        DATA / "causal_failure_modes.png",
        DATA / "causal_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: causal attribution verified.")


if __name__ == "__main__":
    main()
