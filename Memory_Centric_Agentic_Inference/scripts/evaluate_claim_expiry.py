#!/usr/bin/env python3
# created: 2026-05-12T18:05:00Z
# cycle: 39
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CLAIMEXP-1
"""Evaluate production claim expiry and revalidation boundaries."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

IN_VALID = DATA / "claim_expiry_valid_fixture.csv"
IN_INVALID = DATA / "claim_expiry_invalid_fixtures.csv"
OUT_RESULTS = DATA / "claim_expiry_results.csv"
OUT_FAILURES = DATA / "claim_expiry_failure_modes.csv"
OUT_REVALIDATION = DATA / "claim_expiry_revalidation_boundary.csv"
OUT_CLAIM = DATA / "claim_expiry_claim_boundary.csv"


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


def flag(row: dict[str, str], key: str) -> bool:
    return row[key].lower() == "true"


def classify(row: dict[str, str]) -> tuple[str, str]:
    if row["upstream_replay_state"] != "production_supported" or row["evidence_label"] != "production_target":
        return "not_production_supported", "upstream_or_label_not_production_supported"
    if float(row["age_hours"]) >= float(row["ttl_hours"]):
        return "expired", "evidence_age_exceeds_or_equals_ttl"
    if flag(row, "model_version_changed"):
        return "invalidated_by_change", "model_version_changed"
    if flag(row, "topology_changed"):
        return "invalidated_by_change", "topology_changed"
    if not flag(row, "collector_identity_current"):
        return "invalidated_by_change", "collector_identity_rotated_without_reenrollment"
    if not flag(row, "trust_policy_current"):
        return "invalidated_by_change", "trust_policy_rotated"
    if flag(row, "redaction_policy_changed"):
        return "invalidated_by_change", "redaction_policy_changed"
    if float(row["workload_overlap_score"]) < 0.80:
        return "revalidation_required", "workload_mix_outside_causal_overlap"
    if flag(row, "scheduler_policy_changed"):
        return "revalidation_required", "scheduler_policy_changed"
    if flag(row, "memory_tier_regime_changed"):
        return "revalidation_required", "memory_tier_latency_or_energy_regime_shifted"
    if float(row["security_deny_rate_delta"]) > 0.02:
        return "revalidation_required", "security_deny_rate_drifted"
    if flag(row, "uncertainty_interval_widened"):
        return "revalidation_required", "uncertainty_interval_widened"
    if not flag(row, "causal_controls_comparable"):
        return "revalidation_required", "causal_controls_no_longer_comparable"
    if flag(row, "copied_old_replay_result"):
        return "revalidation_required", "copied_old_replay_result_not_fresh_revalidation"
    return "currently_supportable", "within_ttl_and_no_drift"


def evaluate() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    rows = read_csv(IN_VALID) + read_csv(IN_INVALID)
    results = []
    revalidation = []
    claims = []
    for row in rows:
        status, reason = classify(row)
        matched = status == row["expected_status"]
        needs_fresh_replay = status in {"expired", "revalidation_required", "invalidated_by_change"}
        lifecycle_currently_supportable = status == "currently_supportable"
        results.append(
            {
                "case_id": row["case_id"],
                "expected_status": row["expected_status"],
                "observed_status": status,
                "matched_expected": str(matched).lower(),
                "primary_reason": reason,
                "age_hours": row["age_hours"],
                "ttl_hours": row["ttl_hours"],
                "evidence_label": row["evidence_label"],
                "upstream_replay_state": row["upstream_replay_state"],
                "copied_old_replay_result": row["copied_old_replay_result"],
            }
        )
        revalidation.append(
            {
                "case_id": row["case_id"],
                "observed_status": status,
                "fresh_production_replay_required": str(needs_fresh_replay).lower(),
                "old_replay_copy_accepted": "false",
                "revalidation_may_use_prior_result_without_new_evidence": "false",
                "operator_action": "none_currently_supportable" if status == "currently_supportable" else "collect_current_material_and_rerun_full_chain",
            }
        )
        claims.append(
            {
                "case_id": row["case_id"],
                "observed_status": status,
                "currently_supportable_lifecycle_state": str(lifecycle_currently_supportable).lower(),
                "production_calibrated": "false",
                "production_ready": "false",
                "threshold_success": "false",
                "causal_validity_granted": "false",
                "claim_credit_allowed": "false",
                "claim_lifecycle_boundary_only": "true",
            }
        )
    return results, revalidation, claims


def main() -> None:
    results, revalidation, claims = evaluate()
    failures = Counter(row["primary_reason"] for row in results if row["observed_status"] != "currently_supportable")
    failure_rows = [{"failure_mode": key, "count": value} for key, value in sorted(failures.items())]
    write_csv(OUT_RESULTS, results, list(results[0]))
    write_csv(OUT_FAILURES, failure_rows, ["failure_mode", "count"])
    write_csv(OUT_REVALIDATION, revalidation, list(revalidation[0]))
    write_csv(OUT_CLAIM, claims, list(claims[0]))


if __name__ == "__main__":
    main()
