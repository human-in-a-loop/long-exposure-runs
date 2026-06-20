#!/usr/bin/env python3
# created: 2026-05-12T13:00:00Z
# cycle: 34
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-UNCERT-1
"""Build statistical uncertainty fixtures for confidence-qualified threshold replay."""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = [
    DATA / "production_dc12_telemetry_schema.csv",
    DATA / "timebase_integrity_results.csv",
    DATA / "redaction_integrity_results.csv",
    DATA / "production_dc12_threshold_replay.csv",
    DATA / "final_claim_readiness_matrix.csv",
    DATA / "evidence_gatechain_replay_results.csv",
]

OUT_SCHEMA = DATA / "uncertainty_schema.csv"
OUT_VALID = DATA / "uncertainty_valid_fixture.csv"
OUT_INVALID = DATA / "uncertainty_invalid_fixtures.csv"
OUT_GRID = DATA / "uncertainty_sensitivity_grid.csv"

FIELDS = [
    "case_id",
    "case_type",
    "source_fixture_id",
    "constant_id",
    "threshold_id",
    "metric_name",
    "metric_direction",
    "point_estimate",
    "threshold_value",
    "variance",
    "sample_count",
    "confidence_level",
    "ci_lower",
    "ci_upper",
    "noise_model_id",
    "baseline_window_id",
    "control_window_id",
    "treatment_window_id",
    "drift_fraction",
    "drift_budget_fraction",
    "independent_samples",
    "p99_ci_bounded",
    "gatechain_eligible",
    "measurement_valid",
    "threshold_direction_known",
    "evidence_label",
    "expected_threshold_status",
    "expected_blocked_reason",
    "notes",
]

SCHEMA_ROWS = [
    ("metric_name", "true", "metric under confidence qualification; bytes, joules_per_byte, p99 latency, queueing delay, safe reuse, or planner value"),
    ("metric_direction", "true", "higher_is_better or lower_is_better threshold decision direction"),
    ("point_estimate", "true", "finite numeric point estimate; not sufficient for readiness"),
    ("threshold_value", "true", "finite numeric decision threshold from DC-001/DC-002 replay"),
    ("variance", "true", "non-negative per-window variance estimate; zero allowed only with valid samples"),
    ("sample_count", "true", "independent sample count used for confidence interval"),
    ("confidence_level", "true", "interval confidence level; fixture uses 0.95"),
    ("ci_lower", "true", "finite lower confidence bound"),
    ("ci_upper", "true", "finite upper confidence bound"),
    ("noise_model_id", "true", "declared measurement-noise model tied to telemetry source"),
    ("baseline_window_id", "true", "baseline window used for drift check"),
    ("control_window_id", "true", "control arm/window required to avoid workload drift promotion"),
    ("treatment_window_id", "true", "treatment arm/window for memory-centric policy"),
    ("drift_fraction", "true", "observed baseline/control/treatment drift fraction"),
    ("drift_budget_fraction", "true", "maximum allowed drift fraction"),
    ("independent_samples", "true", "true only when repeated intervals are independent enough for CI semantics"),
    ("p99_ci_bounded", "true", "true only when p99/tail latency interval is finite and bounded"),
    ("gatechain_eligible", "true", "fixture-level gatechain precondition; kept false for non-production fixtures"),
    ("measurement_valid", "true", "timing/redaction/source validity precondition"),
    ("threshold_direction_known", "true", "blocks ambiguous threshold comparisons"),
]

BASE = {
    "case_id": "valid-confidence-qualified-fixture",
    "case_type": "valid_fixture",
    "source_fixture_id": "valid-minimal-redaction-fixture",
    "constant_id": "DC-002",
    "threshold_id": "DC002-RAG-C-p99",
    "metric_name": "cxl_p99_latency_delta_ms",
    "metric_direction": "higher_is_better",
    "point_estimate": "7.4",
    "threshold_value": "5.5",
    "variance": "0.36",
    "sample_count": "64",
    "confidence_level": "0.95",
    "ci_lower": "6.2",
    "ci_upper": "8.6",
    "noise_model_id": "noise-model-dc12-tail-latency-v1",
    "baseline_window_id": "baseline-window-001",
    "control_window_id": "control-window-001",
    "treatment_window_id": "treatment-window-001",
    "drift_fraction": "0.03",
    "drift_budget_fraction": "0.10",
    "independent_samples": "true",
    "p99_ci_bounded": "true",
    "gatechain_eligible": "false",
    "measurement_valid": "true",
    "threshold_direction_known": "true",
    "evidence_label": "uncertainty_fixture",
    "expected_threshold_status": "robust_pass",
    "expected_blocked_reason": "",
    "notes": "confidence interval excludes threshold in the pass direction, but fixture evidence remains non-production",
}

ROBUST_FAIL = {
    **BASE,
    "case_id": "valid-confidence-qualified-fail-fixture",
    "point_estimate": "3.9",
    "ci_lower": "3.1",
    "ci_upper": "4.7",
    "expected_threshold_status": "robust_fail",
    "notes": "confidence interval excludes threshold in the fail direction, but fixture evidence remains non-production",
}

INVALIDS = [
    ("invalid-missing-variance-noise-model", {"variance": "", "noise_model_id": ""}, "statistical_invalid", "missing_variance"),
    ("invalid-insufficient-sample-count", {"sample_count": "3"}, "statistically_indeterminate", "insufficient_sample_count"),
    ("invalid-ci-crosses-threshold", {"point_estimate": "6.1", "ci_lower": "4.9", "ci_upper": "7.3"}, "statistically_indeterminate", "confidence_interval_crosses_threshold"),
    ("invalid-ci-touches-threshold", {"point_estimate": "6.0", "ci_lower": "5.5", "ci_upper": "6.5"}, "statistically_indeterminate", "confidence_interval_touches_threshold"),
    ("invalid-unbounded-p99-latency-ci", {"ci_upper": "inf", "p99_ci_bounded": "false"}, "statistical_invalid", "unbounded_p99_latency_ci"),
    ("invalid-drift-between-windows", {"drift_fraction": "0.18"}, "statistically_indeterminate", "control_treatment_drift_exceeds_budget"),
    ("invalid-missing-control-arm", {"control_window_id": ""}, "statistical_invalid", "missing_control_arm"),
    ("invalid-non-independent-repeated-samples", {"independent_samples": "false"}, "statistically_indeterminate", "non_independent_repeated_samples"),
    ("invalid-negative-variance", {"variance": "-0.1"}, "statistical_invalid", "negative_variance"),
    ("invalid-nan-metric", {"point_estimate": "nan"}, "statistical_invalid", "nan_metric"),
    ("invalid-missing-noise-model", {"noise_model_id": ""}, "statistical_invalid", "missing_noise_model"),
    ("invalid-zero-samples", {"sample_count": "0"}, "statistical_invalid", "nonpositive_sample_count"),
    ("invalid-unknown-source-fixture", {"source_fixture_id": "not-a-redaction-fixture"}, "statistical_invalid", "unknown_source_fixture_id"),
    ("invalid-fixture-attempted-production-calibration", {"evidence_label": "production_target"}, "statistical_invalid", "fixture_attempted_production_calibration"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def require_inputs() -> None:
    for path in INPUTS:
        read_csv(path)


def invalid_rows() -> list[dict[str, object]]:
    rows = []
    for case_id, overrides, expected_status, reason in INVALIDS:
        row = dict(BASE)
        row.update(overrides)
        row.update(
            {
                "case_id": case_id,
                "case_type": "invalid_fixture",
                "expected_threshold_status": expected_status,
                "expected_blocked_reason": reason,
                "notes": "malformed or weak uncertainty metadata must fail closed before readiness updates",
            }
        )
        rows.append(row)
    return rows


def grid_rows() -> list[dict[str, object]]:
    rows = []
    for effect_size, sigma, sample_count, drift in product([3.5, 5.5, 6.5, 8.0], [0.2, 0.8, 1.6], [4, 16, 64], [0.02, 0.12]):
        half_width = 1.96 * sigma / (sample_count ** 0.5)
        lower = effect_size - half_width
        upper = effect_size + half_width
        if sample_count < 8 or drift > 0.10 or lower <= 5.5 <= upper:
            status = "statistically_indeterminate"
        elif lower > 5.5:
            status = "robust_pass"
        else:
            status = "robust_fail"
        rows.append(
            {
                "grid_id": f"effect-{effect_size}-sigma-{sigma}-n-{sample_count}-drift-{drift}",
                "metric_direction": "higher_is_better",
                "effect_size": effect_size,
                "threshold_value": 5.5,
                "sigma": sigma,
                "sample_count": sample_count,
                "drift_fraction": drift,
                "ci_lower": f"{lower:.3f}",
                "ci_upper": f"{upper:.3f}",
                "threshold_status": status,
            }
        )
    return rows


def main() -> None:
    require_inputs()
    schema = [{"field_name": field, "required": required, "purpose": purpose} for field, required, purpose in SCHEMA_ROWS]
    write_csv(OUT_SCHEMA, schema, ["field_name", "required", "purpose"])
    write_csv(OUT_VALID, [BASE, ROBUST_FAIL], FIELDS)
    write_csv(OUT_INVALID, invalid_rows(), FIELDS)
    write_csv(OUT_GRID, grid_rows(), ["grid_id", "metric_direction", "effect_size", "threshold_value", "sigma", "sample_count", "drift_fraction", "ci_lower", "ci_upper", "threshold_status"])


if __name__ == "__main__":
    main()
