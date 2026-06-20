#!/usr/bin/env python3
# created: 2026-05-12T13:05:00Z
# cycle: 34
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-UNCERT-1
"""Evaluate statistical confidence gates for threshold and readiness propagation."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

VALID = DATA / "uncertainty_valid_fixture.csv"
INVALID = DATA / "uncertainty_invalid_fixtures.csv"
REDACTION = DATA / "redaction_integrity_results.csv"
THRESHOLD = DATA / "production_dc12_threshold_replay.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"
GATECHAIN = DATA / "evidence_gatechain_replay_results.csv"

OUT_RESULTS = DATA / "uncertainty_evaluation_results.csv"
OUT_FAILURES = DATA / "uncertainty_failure_modes.csv"
OUT_THRESHOLD = DATA / "uncertainty_threshold_boundary.csv"
OUT_CLAIM = DATA / "uncertainty_claim_readiness_boundary.csv"

ALLOWED_SOURCE_FIXTURES = {"valid-minimal-redaction-fixture"}
ALLOWED_EVIDENCE_LABEL = "uncertainty_fixture"
N_MIN = 8


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


def finite_float(row: dict[str, str], field: str) -> tuple[float, str]:
    raw = row.get(field, "")
    if raw == "":
        return 0.0, f"missing_{field}"
    try:
        value = float(raw)
    except ValueError:
        return 0.0, f"invalid_{field}"
    if not math.isfinite(value):
        if math.isnan(value):
            return value, "nan_metric" if field == "point_estimate" else f"nan_{field}"
        return value, "unbounded_p99_latency_ci" if field in {"ci_lower", "ci_upper"} and row.get("metric_name", "").startswith("cxl_p99") else f"nonfinite_{field}"
    return value, ""


def finite_int(row: dict[str, str], field: str) -> tuple[int, str]:
    raw = row.get(field, "")
    if raw == "":
        return 0, f"missing_{field}"
    try:
        value = int(raw)
    except ValueError:
        return 0, f"invalid_{field}"
    return value, ""


def classify(row: dict[str, str]) -> tuple[str, str, str]:
    if not row["source_fixture_id"]:
        return "statistical_invalid", "source_fixture_id", "missing_source_fixture_id"
    if row["source_fixture_id"] not in ALLOWED_SOURCE_FIXTURES:
        return "statistical_invalid", "source_fixture_id", "unknown_source_fixture_id"
    if row["evidence_label"] == "production_target":
        return "statistical_invalid", "evidence_label", "fixture_attempted_production_calibration"
    if row["evidence_label"] != ALLOWED_EVIDENCE_LABEL:
        return "statistical_invalid", "evidence_label", "unsupported_evidence_label"
    if row["measurement_valid"] != "true":
        return "statistical_invalid", "measurement_valid", "measurement_invalid"
    if row["threshold_direction_known"] != "true":
        return "statistical_invalid", "threshold_direction_known", "threshold_direction_unknown"
    if not row["control_window_id"]:
        return "statistical_invalid", "control_window_id", "missing_control_arm"
    for field in ["point_estimate", "threshold_value", "variance", "confidence_level", "ci_lower", "ci_upper", "drift_fraction", "drift_budget_fraction"]:
        _, reason = finite_float(row, field)
        if reason:
            return "statistical_invalid", field, "missing_variance" if field == "variance" and reason == "missing_variance" else reason
    if not row["noise_model_id"]:
        return "statistical_invalid", "noise_model_id", "missing_noise_model"
    variance = float(row["variance"])
    if variance < 0:
        return "statistical_invalid", "variance", "negative_variance"
    sample_count, sample_reason = finite_int(row, "sample_count")
    if sample_reason:
        return "statistical_invalid", "sample_count", sample_reason
    if sample_count <= 0:
        return "statistical_invalid", "sample_count", "nonpositive_sample_count"
    if row["p99_ci_bounded"] != "true":
        return "statistical_invalid", "p99_ci_bounded", "unbounded_p99_latency_ci"
    if sample_count < N_MIN:
        return "statistically_indeterminate", "sample_count", "insufficient_sample_count"
    if row["independent_samples"] != "true":
        return "statistically_indeterminate", "independent_samples", "non_independent_repeated_samples"
    if float(row["drift_fraction"]) > float(row["drift_budget_fraction"]):
        return "statistically_indeterminate", "drift_fraction", "control_treatment_drift_exceeds_budget"
    lower = float(row["ci_lower"])
    upper = float(row["ci_upper"])
    threshold = float(row["threshold_value"])
    if lower > upper:
        return "statistical_invalid", "ci_lower", "invalid_confidence_interval_order"
    if lower == threshold or upper == threshold:
        return "statistically_indeterminate", "confidence_interval", "confidence_interval_touches_threshold"
    if lower < threshold < upper:
        return "statistically_indeterminate", "confidence_interval", "confidence_interval_crosses_threshold"
    if row["metric_direction"] == "higher_is_better":
        return ("robust_pass", "", "") if lower > threshold else ("robust_fail", "", "")
    if row["metric_direction"] == "lower_is_better":
        return ("robust_pass", "", "") if upper < threshold else ("robust_fail", "", "")
    return "statistical_invalid", "metric_direction", "unknown_metric_direction"


def evaluate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        status, field, reason = classify(row)
        point_pass = False
        try:
            point = float(row["point_estimate"])
            threshold = float(row["threshold_value"])
            point_pass = point > threshold if row["metric_direction"] == "higher_is_better" else point < threshold
        except (ValueError, KeyError):
            point_pass = False
        readiness_update_allowed = status == "robust_pass" and row["gatechain_eligible"] == "true"
        out.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "source_fixture_id": row["source_fixture_id"],
                "metric_name": row["metric_name"],
                "point_estimate": row["point_estimate"],
                "threshold_value": row["threshold_value"],
                "ci_lower": row["ci_lower"],
                "ci_upper": row["ci_upper"],
                "point_estimate_passed": str(point_pass).lower(),
                "threshold_status": status,
                "blocked_field": field,
                "blocked_reason": reason,
                "expected_threshold_status": row["expected_threshold_status"],
                "expected_blocked_reason": row["expected_blocked_reason"],
                "expected_reason_matched": str((not row["expected_blocked_reason"]) or row["expected_blocked_reason"] == reason).lower(),
                "readiness_update_allowed": str(readiness_update_allowed).lower(),
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "confidence_precondition_only": "true",
            }
        )
    return out


def failure_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter((str(row["threshold_status"]), str(row["blocked_reason"])) for row in results if row["blocked_reason"])
    return [
        {"threshold_status": status, "blocked_reason": reason, "case_count": count, "fail_closed": "true"}
        for (status, reason), count in sorted(counts.items())
    ]


def threshold_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "case_id": row["case_id"],
            "point_estimate_passed": row["point_estimate_passed"],
            "threshold_status": row["threshold_status"],
            "blocked_reason": row["blocked_reason"],
            "robust_threshold_replay_allowed": str(row["threshold_status"] == "robust_pass").lower(),
            "point_estimate_pass_is_sufficient": "false",
            "indeterminate_can_update_readiness": "false",
        }
        for row in results
    ]


def claim_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    gatechain_allowed = any(row["production_claim_credit_allowed"] == "true" for row in read_csv(GATECHAIN))
    readiness_ready = any(row["production_ready"] == "true" for row in read_csv(READINESS))
    return [
        {
            "case_id": row["case_id"],
            "threshold_status": row["threshold_status"],
            "existing_gatechain_allowed": str(gatechain_allowed).lower(),
            "existing_readiness_ready": str(readiness_ready).lower(),
            "confidence_precondition_only": "true",
            "readiness_update_allowed": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "claim_credit_allowed": "false",
            "boundary_reason": "confidence_qualified_but_nonproduction_fixture" if row["threshold_status"] == "robust_pass" else row["blocked_reason"],
        }
        for row in results
    ]


def main() -> None:
    if not any(row["redaction_admissible"] == "true" for row in read_csv(REDACTION)):
        raise ValueError("uncertainty harness requires at least one redaction-admissible fixture")
    if not any(row["threshold_crossed"] == "true" for row in read_csv(THRESHOLD)):
        raise ValueError("uncertainty harness requires at least one upstream point-estimate threshold pass")
    rows = read_csv(VALID) + read_csv(INVALID)
    results = evaluate(rows)
    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "case_type",
            "source_fixture_id",
            "metric_name",
            "point_estimate",
            "threshold_value",
            "ci_lower",
            "ci_upper",
            "point_estimate_passed",
            "threshold_status",
            "blocked_field",
            "blocked_reason",
            "expected_threshold_status",
            "expected_blocked_reason",
            "expected_reason_matched",
            "readiness_update_allowed",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "confidence_precondition_only",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows(results), ["threshold_status", "blocked_reason", "case_count", "fail_closed"])
    write_csv(OUT_THRESHOLD, threshold_boundary(results), ["case_id", "point_estimate_passed", "threshold_status", "blocked_reason", "robust_threshold_replay_allowed", "point_estimate_pass_is_sufficient", "indeterminate_can_update_readiness"])
    write_csv(OUT_CLAIM, claim_boundary(results), ["case_id", "threshold_status", "existing_gatechain_allowed", "existing_readiness_ready", "confidence_precondition_only", "readiness_update_allowed", "production_calibrated", "production_ready", "claim_credit_allowed", "boundary_reason"])


if __name__ == "__main__":
    main()
