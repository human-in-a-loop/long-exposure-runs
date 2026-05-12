#!/usr/bin/env python3
# created: 2026-05-12T18:00:00Z
# cycle: 39
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CLAIMEXP-1
"""Build claim expiry and revalidation fixtures."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OUT_SCHEMA = DATA / "claim_expiry_schema.csv"
OUT_POLICY = DATA / "claim_expiry_policy_profiles.csv"
OUT_VALID = DATA / "claim_expiry_valid_fixture.csv"
OUT_INVALID = DATA / "claim_expiry_invalid_fixtures.csv"
OUT_DRIFT = DATA / "claim_expiry_drift_events.csv"


FIELDS = [
    ("case_id", "string", "unique lifecycle probe id"),
    ("upstream_replay_state", "enum", "production_supported or not_production_supported"),
    ("evidence_label", "enum", "production_target or non-production fixture/proxy label"),
    ("age_hours", "number", "hours since replay completion"),
    ("ttl_hours", "number", "policy validity window; age >= ttl expires"),
    ("model_version_changed", "boolean", "model version differs from replay"),
    ("topology_changed", "boolean", "topology differs from replay envelope"),
    ("workload_overlap_score", "number", "causal overlap score in [0,1]"),
    ("scheduler_policy_changed", "boolean", "scheduler policy differs from replay"),
    ("memory_tier_regime_changed", "boolean", "tier latency/energy regime differs from replay"),
    ("collector_identity_current", "boolean", "collector/root identity is current or re-enrolled"),
    ("trust_policy_current", "boolean", "operator trust policy remains current"),
    ("security_deny_rate_delta", "number", "absolute deny-rate drift since replay"),
    ("redaction_policy_changed", "boolean", "redaction policy differs from replay"),
    ("uncertainty_interval_widened", "boolean", "robust interval no longer excludes threshold"),
    ("causal_controls_comparable", "boolean", "control arm and covariates remain comparable"),
    ("copied_old_replay_result", "boolean", "row attempts to satisfy revalidation by copying old replay output"),
    ("expected_status", "enum", "expected lifecycle status"),
]

POLICIES = [
    {
        "policy_id": "default_claim_lifecycle",
        "ttl_hours": 168,
        "workload_overlap_min": 0.80,
        "security_deny_rate_delta_max": 0.02,
        "ttl_boundary_rule": "expired_when_age_greater_or_equal_ttl",
        "identity_change_rule": "invalidated_by_change",
        "drift_rule": "revalidation_required_unless_identity_or_trust_breaks",
    },
    {
        "policy_id": "short_pilot_lifecycle",
        "ttl_hours": 24,
        "workload_overlap_min": 0.85,
        "security_deny_rate_delta_max": 0.01,
        "ttl_boundary_rule": "expired_when_age_greater_or_equal_ttl",
        "identity_change_rule": "invalidated_by_change",
        "drift_rule": "revalidation_required_unless_identity_or_trust_breaks",
    },
]

BASE = {
    "upstream_replay_state": "production_supported",
    "evidence_label": "production_target",
    "age_hours": 0,
    "ttl_hours": 168,
    "model_version_changed": "false",
    "topology_changed": "false",
    "workload_overlap_score": 0.92,
    "scheduler_policy_changed": "false",
    "memory_tier_regime_changed": "false",
    "collector_identity_current": "true",
    "trust_policy_current": "true",
    "security_deny_rate_delta": 0.0,
    "redaction_policy_changed": "false",
    "uncertainty_interval_widened": "false",
    "causal_controls_comparable": "true",
    "copied_old_replay_result": "false",
}

CASES = [
    ("fresh_prior_production_replay", {}, "currently_supportable"),
    ("t0_without_upstream_production", {"upstream_replay_state": "not_production_supported"}, "not_production_supported"),
    ("dry_run_fixture_attempt", {"evidence_label": "collector_dry_run_fixture"}, "not_production_supported"),
    ("synthetic_proxy_attempt", {"evidence_label": "synthetic_proxy"}, "not_production_supported"),
    ("age_exceeds_policy_ttl", {"age_hours": 169}, "expired"),
    ("age_equals_policy_ttl", {"age_hours": 168}, "expired"),
    ("model_version_changed", {"model_version_changed": "true"}, "invalidated_by_change"),
    ("topology_changed", {"topology_changed": "true"}, "invalidated_by_change"),
    ("workload_mix_outside_overlap", {"workload_overlap_score": 0.63}, "revalidation_required"),
    ("scheduler_policy_changed", {"scheduler_policy_changed": "true"}, "revalidation_required"),
    ("memory_tier_regime_shifted", {"memory_tier_regime_changed": "true"}, "revalidation_required"),
    ("collector_rotated_without_reenrollment", {"collector_identity_current": "false"}, "invalidated_by_change"),
    ("trust_policy_rotated", {"trust_policy_current": "false"}, "invalidated_by_change"),
    ("security_deny_rate_drifted", {"security_deny_rate_delta": 0.05}, "revalidation_required"),
    ("redaction_policy_changed", {"redaction_policy_changed": "true"}, "invalidated_by_change"),
    ("uncertainty_interval_widened", {"uncertainty_interval_widened": "true"}, "revalidation_required"),
    ("causal_controls_not_comparable", {"causal_controls_comparable": "false"}, "revalidation_required"),
    ("copied_old_replay_after_drift", {"scheduler_policy_changed": "true", "copied_old_replay_result": "true"}, "revalidation_required"),
]


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def rows() -> list[dict[str, object]]:
    out = []
    for case_id, updates, expected in CASES:
        row = dict(BASE)
        row.update(updates)
        row["case_id"] = case_id
        row["expected_status"] = expected
        out.append(row)
    return out


def drift_rows(all_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for row in all_rows:
        if row["case_id"] in {"fresh_prior_production_replay", "t0_without_upstream_production", "dry_run_fixture_attempt", "synthetic_proxy_attempt"}:
            continue
        changed = [
            axis
            for axis in [
                "model_version_changed",
                "topology_changed",
                "scheduler_policy_changed",
                "memory_tier_regime_changed",
                "redaction_policy_changed",
                "uncertainty_interval_widened",
                "copied_old_replay_result",
            ]
            if row[axis] == "true"
        ]
        if float(row["age_hours"]) >= float(row["ttl_hours"]):
            changed.append("evidence_age_exceeds_or_equals_ttl")
        if float(row["workload_overlap_score"]) < 0.80:
            changed.append("workload_mix_outside_causal_overlap")
        if row["collector_identity_current"] == "false":
            changed.append("collector_identity_rotated_without_reenrollment")
        if row["trust_policy_current"] == "false":
            changed.append("trust_policy_rotated")
        if float(row["security_deny_rate_delta"]) > 0.02:
            changed.append("security_deny_rate_drifted")
        if row["causal_controls_comparable"] == "false":
            changed.append("causal_controls_no_longer_comparable")
        result.append(
            {
                "case_id": row["case_id"],
                "drift_axis": ";".join(changed),
                "expected_lifecycle_effect": row["expected_status"],
                "operator_action": "new_production_replay_required" if row["expected_status"] != "expired" else "rerun_after_ttl_expiry",
            }
        )
    return result


def main() -> None:
    all_rows = rows()
    write_csv(OUT_SCHEMA, [{"field": a, "type": b, "description": c} for a, b, c in FIELDS], ["field", "type", "description"])
    write_csv(OUT_POLICY, POLICIES, list(POLICIES[0]))
    write_csv(OUT_VALID, [all_rows[0]], list(all_rows[0]))
    write_csv(OUT_INVALID, all_rows[1:], list(all_rows[0]))
    write_csv(OUT_DRIFT, drift_rows(all_rows), ["case_id", "drift_axis", "expected_lifecycle_effect", "operator_action"])


if __name__ == "__main__":
    main()
