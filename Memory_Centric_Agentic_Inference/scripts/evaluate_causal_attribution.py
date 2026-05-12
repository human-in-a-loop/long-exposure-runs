#!/usr/bin/env python3
# created: 2026-05-12T14:05:00Z
# cycle: 35
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CAUSAL-1
"""Evaluate causal attribution gates for robust memory-centric effects."""

from __future__ import annotations

import csv
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

VALID = DATA / "causal_valid_fixture.csv"
INVALID = DATA / "causal_invalid_fixtures.csv"
UNCERTAINTY = DATA / "uncertainty_evaluation_results.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"
GATECHAIN = DATA / "evidence_gatechain_replay_results.csv"

OUT_RESULTS = DATA / "causal_attribution_results.csv"
OUT_FAILURES = DATA / "causal_failure_modes.csv"
OUT_THRESHOLD = DATA / "causal_threshold_boundary.csv"
OUT_CLAIM = DATA / "causal_claim_readiness_boundary.csv"

ALLOWED_SOURCE_CASES = {"valid-confidence-qualified-fixture", "valid-confidence-qualified-fail-fixture"}
ALLOWED_EVIDENCE_LABEL = "causal_fixture"
BALANCE_MAX = 0.10
SECURITY_DENY_DELTA_MAX = 0.02
DRIFT_MAX = 0.10
OVERLAP_MIN = 0.80


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
        return value, f"nonfinite_{field}"
    return value, ""


def gt(row: dict[str, str], field: str, limit: float) -> bool:
    value, reason = finite_float(row, field)
    if reason:
        return True
    return value > limit


def classify(row: dict[str, str]) -> tuple[str, str, str]:
    if row["source_uncertainty_case_id"] not in ALLOWED_SOURCE_CASES:
        return "causally_unidentified", "source_uncertainty_case_id", "unknown_uncertainty_case"
    if row["evidence_label"] == "production_target":
        return "causally_unidentified", "evidence_label", "fixture_attempted_production_calibration"
    if row["evidence_label"] != ALLOWED_EVIDENCE_LABEL:
        return "causally_unidentified", "evidence_label", "unsupported_evidence_label"
    if row["measurement_valid"] != "true":
        return "causally_unidentified", "measurement_valid", "measurement_invalid"
    if row["statistical_threshold_status"] not in {"robust_pass", "robust_fail"}:
        return "causally_unidentified", "statistical_threshold_status", "statistical_effect_not_robust"
    if row["control_arm_present"] != "true":
        return "causally_unidentified", "control_arm_present", "missing_option_a_control"
    if row["pre_treatment_covariates_declared"] != "true":
        return "causally_unidentified", "pre_treatment_covariates_declared", "missing_pre_treatment_covariate_contract"
    if row["post_treatment_covariate_used"] != "false":
        return "causally_unidentified", "post_treatment_covariate_used", "post_treatment_covariate_leakage"
    overlap, overlap_reason = finite_float(row, "positivity_overlap_fraction")
    if overlap_reason:
        return "causally_unidentified", "positivity_overlap_fraction", overlap_reason
    if overlap < OVERLAP_MIN:
        return "causally_unidentified", "positivity_overlap_fraction", "insufficient_overlap_positivity"
    if row["topology_match"] != "true":
        return "causally_confounded", "topology_match", "topology_mismatch"
    if row["model_version_match"] != "true":
        return "causally_confounded", "model_version_match", "model_version_mismatch"
    if gt(row, "workload_mix_smd", BALANCE_MAX):
        return "causally_confounded", "workload_mix_smd", "workload_mix_mismatch"
    if gt(row, "object_size_smd", BALANCE_MAX):
        return "causally_confounded", "object_size_smd", "object_size_distribution_shift"
    if gt(row, "tenant_concurrency_smd", BALANCE_MAX):
        return "causally_confounded", "tenant_concurrency_smd", "tenant_concurrency_imbalance"
    if gt(row, "cache_warmness_smd", BALANCE_MAX):
        return "causally_confounded", "cache_warmness_smd", "cache_warmness_imbalance"
    if gt(row, "scheduler_load_smd", BALANCE_MAX):
        return "causally_confounded", "scheduler_load_smd", "scheduler_load_imbalance"
    if gt(row, "security_deny_rate_delta", SECURITY_DENY_DELTA_MAX):
        return "causally_confounded", "security_deny_rate_delta", "security_deny_rate_shift"
    if gt(row, "time_window_drift_fraction", DRIFT_MAX):
        return "causally_confounded", "time_window_drift_fraction", "time_window_drift"
    return "causally_admissible", "", ""


def evaluate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    out = []
    for row in rows:
        status, field, reason = classify(row)
        robust_pass = row["statistical_threshold_status"] == "robust_pass"
        causal_support_eligible = status == "causally_admissible" and robust_pass and row["gatechain_eligible"] == "true"
        out.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "source_uncertainty_case_id": row["source_uncertainty_case_id"],
                "architecture_option": row["architecture_option"],
                "control_policy": row["control_policy"],
                "treatment_policy": row["treatment_policy"],
                "statistical_threshold_status": row["statistical_threshold_status"],
                "robust_statistical_effect": str(robust_pass).lower(),
                "causal_status": status,
                "blocked_field": field,
                "blocked_reason": reason,
                "expected_causal_status": row["expected_causal_status"],
                "expected_blocked_reason": row["expected_blocked_reason"],
                "expected_reason_matched": str((not row["expected_blocked_reason"]) or row["expected_blocked_reason"] == reason).lower(),
                "causal_support_eligible": str(causal_support_eligible).lower(),
                "readiness_update_allowed": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "causal_precondition_only": "true",
            }
        )
    return out


def failure_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter((str(row["causal_status"]), str(row["blocked_reason"])) for row in results if row["blocked_reason"])
    return [
        {"causal_status": status, "blocked_reason": reason, "case_count": count, "fail_closed": "true"}
        for (status, reason), count in sorted(counts.items())
    ]


def threshold_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "case_id": row["case_id"],
            "statistical_threshold_status": row["statistical_threshold_status"],
            "robust_statistical_effect": row["robust_statistical_effect"],
            "causal_status": row["causal_status"],
            "blocked_reason": row["blocked_reason"],
            "robust_but_confounded": str(row["robust_statistical_effect"] == "true" and row["causal_status"] != "causally_admissible").lower(),
            "causal_threshold_replay_allowed": str(row["causal_status"] == "causally_admissible").lower(),
            "robust_effect_is_sufficient": "false",
            "confounded_can_update_readiness": "false",
        }
        for row in results
    ]


def claim_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    gatechain_allowed = any(row["production_claim_credit_allowed"] == "true" for row in read_csv(GATECHAIN))
    readiness_ready = any(row["production_ready"] == "true" for row in read_csv(READINESS))
    return [
        {
            "case_id": row["case_id"],
            "statistical_threshold_status": row["statistical_threshold_status"],
            "causal_status": row["causal_status"],
            "existing_gatechain_allowed": str(gatechain_allowed).lower(),
            "existing_readiness_ready": str(readiness_ready).lower(),
            "causal_precondition_only": "true",
            "readiness_update_allowed": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "claim_credit_allowed": "false",
            "boundary_reason": "causally_admissible_but_nonproduction_fixture" if row["causal_status"] == "causally_admissible" else row["blocked_reason"],
        }
        for row in results
    ]


def main() -> None:
    uncertainty = read_csv(UNCERTAINTY)
    if not any(row["threshold_status"] == "robust_pass" for row in uncertainty):
        raise ValueError("causal harness requires an upstream robust_pass uncertainty fixture")
    if not any(row["threshold_status"] == "robust_fail" for row in uncertainty):
        raise ValueError("causal harness requires an upstream robust_fail uncertainty fixture")
    rows = read_csv(VALID) + read_csv(INVALID)
    results = evaluate(rows)
    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "case_type",
            "source_uncertainty_case_id",
            "architecture_option",
            "control_policy",
            "treatment_policy",
            "statistical_threshold_status",
            "robust_statistical_effect",
            "causal_status",
            "blocked_field",
            "blocked_reason",
            "expected_causal_status",
            "expected_blocked_reason",
            "expected_reason_matched",
            "causal_support_eligible",
            "readiness_update_allowed",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "causal_precondition_only",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows(results), ["causal_status", "blocked_reason", "case_count", "fail_closed"])
    write_csv(OUT_THRESHOLD, threshold_boundary(results), ["case_id", "statistical_threshold_status", "robust_statistical_effect", "causal_status", "blocked_reason", "robust_but_confounded", "causal_threshold_replay_allowed", "robust_effect_is_sufficient", "confounded_can_update_readiness"])
    write_csv(OUT_CLAIM, claim_boundary(results), ["case_id", "statistical_threshold_status", "causal_status", "existing_gatechain_allowed", "existing_readiness_ready", "causal_precondition_only", "readiness_update_allowed", "production_calibrated", "production_ready", "claim_credit_allowed", "boundary_reason"])


if __name__ == "__main__":
    main()
