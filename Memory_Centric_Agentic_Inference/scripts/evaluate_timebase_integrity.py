#!/usr/bin/env python3
# created: 2026-05-12T11:05:00Z
# cycle: 32
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TIMEBASE-1
"""Evaluate timing and observer-overhead integrity before threshold replay."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "timebase_integrity_schema.csv"
VALID = DATA / "timebase_valid_fixture.csv"
INVALID = DATA / "timebase_invalid_fixtures.csv"
SENSITIVITY = DATA / "timebase_threshold_sensitivity_cases.csv"
THRESHOLD_REPLAY = DATA / "production_dc12_threshold_replay.csv"
GATECHAIN = DATA / "evidence_gatechain_replay_results.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"

OUT_RESULTS = DATA / "timebase_integrity_results.csv"
OUT_FAILURES = DATA / "timebase_failure_modes.csv"
OUT_REPLAY_BOUNDARY = DATA / "timebase_threshold_replay_boundary.csv"
OUT_CLAIM_BOUNDARY = DATA / "timebase_claim_credit_boundary.csv"

KNOWN_SOURCE_FIXTURES = {"valid-dc001-rag-b", "valid-dc002-rag-c", "valid-dc002-code-b", "valid-control-a"}
EXPECTED_MEASUREMENT_RUN_ID = "gatechain-run-001"
EXPECTED_BUNDLE_ID = "gatechain-bundle-001"
EXPECTED_COLLECTOR_ID = "collector-fixture-001"
EXPECTED_SCHEMA_VERSION = "production_dc12_schema_v1"

REQUIRED = [
    "source_fixture_id",
    "measurement_run_id",
    "bundle_id",
    "collector_id",
    "schema_version",
    "evidence_label",
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


def fnum(row: dict[str, str], key: str) -> float:
    return float(row.get(key, ""))


def interval_pair(row: dict[str, str], prefix: str) -> tuple[float, float]:
    return fnum(row, f"{prefix}_interval_start_ms"), fnum(row, f"{prefix}_interval_end_ms")


def block_reason(row: dict[str, str]) -> tuple[str, str]:
    for field in REQUIRED:
        if row.get(field, "") == "":
            if field == "clock_domain_id":
                return "missing_clock_domain", field
            if field == "collector_overhead_pct":
                return "missing_collector_overhead_estimate", field
            return f"missing_{field}", field
    if row["source_fixture_id"] not in KNOWN_SOURCE_FIXTURES:
        return "unknown_source_fixture_id", "source_fixture_id"
    if row["measurement_run_id"] != EXPECTED_MEASUREMENT_RUN_ID:
        return "measurement_run_id_mismatch", "measurement_run_id"
    if row["bundle_id"] != EXPECTED_BUNDLE_ID:
        return "bundle_id_mismatch", "bundle_id"
    if row["collector_id"] != EXPECTED_COLLECTOR_ID:
        return "collector_id_mismatch", "collector_id"
    if row["schema_version"] != EXPECTED_SCHEMA_VERSION:
        return "schema_version_mismatch", "schema_version"
    if row["evidence_label"] == "production_target":
        return "fixture_attempted_production_calibration", "evidence_label"
    if row["clock_sync_status"] != "synchronized":
        return "clock_not_synchronized", "clock_sync_status"
    start = fnum(row, "interval_start_ms")
    end = fnum(row, "interval_end_ms")
    duration = end - start
    if duration <= 0:
        return "zero_or_negative_interval", "interval_end_ms"
    sampling_period = fnum(row, "sampling_period_ms")
    sampling_jitter = fnum(row, "sampling_jitter_ms")
    cross_source_skew = fnum(row, "max_cross_source_skew_ms")
    collector_overhead = fnum(row, "collector_overhead_pct")
    clock_drift = fnum(row, "clock_drift_ppm")
    if sampling_period <= 0:
        return "non_positive_sampling_period", "sampling_period_ms"
    if sampling_jitter < 0:
        return "negative_sampling_jitter", "sampling_jitter_ms"
    if cross_source_skew < 0:
        return "negative_cross_source_skew", "max_cross_source_skew_ms"
    if collector_overhead < 0:
        return "negative_collector_overhead", "collector_overhead_pct"
    if clock_drift < 0:
        return "negative_clock_drift", "clock_drift_ppm"
    for prefix in ["byte", "power", "latency", "queue", "security"]:
        p_start, p_end = interval_pair(row, prefix)
        if p_end <= p_start:
            return "zero_or_negative_interval", f"{prefix}_interval_end_ms"
        if p_start > end or p_end < start:
            return "interval_gap", f"{prefix}_interval_start_ms"
        if p_start != start or p_end != end:
            return "interval_overlap_mismatch", f"{prefix}_interval_start_ms"
    if duration % sampling_period != 0:
        return "inconsistent_sampling_period", "sampling_period_ms"
    if cross_source_skew > fnum(row, "skew_tolerance_ms"):
        return "cross_source_skew_above_tolerance", "max_cross_source_skew_ms"
    if sampling_jitter > fnum(row, "jitter_tolerance_ms"):
        return "sampling_jitter_above_tolerance", "sampling_jitter_ms"
    label_age = end - fnum(row, "workload_label_sampled_at_ms")
    if label_age > fnum(row, "workload_label_max_age_ms"):
        return "stale_workload_label", "workload_label_sampled_at_ms"
    if collector_overhead >= fnum(row, "observer_perturbation_budget_pct"):
        return "observer_overhead_above_budget", "collector_overhead_pct"
    if row["counter_reset_observed"] == "true" or fnum(row, "counter_sequence_end") < fnum(row, "counter_sequence_start"):
        return "counter_reset_inside_interval", "counter_sequence_end"
    if clock_drift > fnum(row, "clock_drift_tolerance_ppm"):
        return "clock_drift_across_bundle", "clock_drift_ppm"
    return "", ""


def threshold_by_fixture() -> dict[str, dict[str, str]]:
    return {row["fixture_id"]: row for row in read_csv(THRESHOLD_REPLAY)}


def evaluate(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    replay = threshold_by_fixture()
    results = []
    for row in rows:
        reason, field = block_reason(row)
        timing_admissible = reason == "" and row["case_type"] == "valid_fixture"
        upstream = replay.get(row["source_fixture_id"], {})
        upstream_crossed = upstream.get("threshold_crossed", "false")
        status = "threshold_passed" if timing_admissible and upstream_crossed == "true" else "measurement_invalid"
        results.append(
            {
                "case_id": row["case_id"],
                "case_type": row["case_type"],
                "source_fixture_id": row["source_fixture_id"],
                "measurement_run_id": row["measurement_run_id"],
                "bundle_id": row["bundle_id"],
                "collector_id": row["collector_id"],
                "schema_version": row["schema_version"],
                "evidence_label": row["evidence_label"],
                "timing_admissible": str(timing_admissible).lower(),
                "threshold_replay_status": status,
                "threshold_crossed_if_valid": upstream_crossed,
                "blocked_field": field,
                "blocked_reason": reason,
                "expected_blocked_reason": row.get("expected_blocked_reason", ""),
                "expected_reason_matched": str((not row.get("expected_blocked_reason")) or row.get("expected_blocked_reason") == reason).lower(),
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "measurement_quality_precondition_only": "true",
            }
        )
    return results


def failure_rows(results: list[dict[str, object]]) -> list[dict[str, object]]:
    counts = Counter(str(row["blocked_reason"]) for row in results if row["blocked_reason"])
    return [
        {"blocked_reason": reason, "case_count": count, "fail_closed": "true", "replay_status": "measurement_invalid"}
        for reason, count in sorted(counts.items())
    ]


def replay_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "case_id": row["case_id"],
            "timing_admissible": row["timing_admissible"],
            "threshold_crossed_if_valid": row["threshold_crossed_if_valid"],
            "threshold_replay_status": row["threshold_replay_status"],
            "blocked_reason": row["blocked_reason"],
            "invalid_timing_is_threshold_miss": "false",
            "dc001_dc002_replay_allowed": str(row["threshold_replay_status"] == "threshold_passed").lower(),
        }
        for row in results
    ]


def claim_boundary(results: list[dict[str, object]]) -> list[dict[str, object]]:
    gatechain_allowed = any(row["production_claim_credit_allowed"] == "true" for row in read_csv(GATECHAIN))
    return [
        {
            "case_id": row["case_id"],
            "timing_admissible": row["timing_admissible"],
            "existing_gatechain_allowed": str(gatechain_allowed).lower(),
            "measurement_quality_precondition_only": "true",
            "production_calibrated": "false",
            "production_ready": "false",
            "claim_credit_allowed": "false",
            "boundary_reason": "timing_quality_precondition_only" if row["timing_admissible"] == "true" else row["blocked_reason"],
        }
        for row in results
    ]


def main() -> None:
    schema = read_csv(SCHEMA)
    declared = {row["field_name"] for row in schema if row["required"] == "true"}
    missing = sorted(set(REQUIRED) - declared)
    if missing:
        raise ValueError(f"timebase schema missing fields: {missing}")
    if any(row["production_ready"] == "true" for row in read_csv(READINESS)):
        raise ValueError("existing final readiness unexpectedly contains production-ready claim")
    sensitivity = read_csv(SENSITIVITY)
    if not any(row["threshold_replay_status"] == "measurement_invalid" for row in sensitivity):
        raise ValueError("sensitivity sweep lacks invalid timing cases")
    missing_sources = KNOWN_SOURCE_FIXTURES - set(threshold_by_fixture())
    if missing_sources:
        raise ValueError(f"timebase source fixtures missing from threshold replay: {sorted(missing_sources)}")
    results = evaluate(read_csv(VALID) + read_csv(INVALID))
    write_csv(
        OUT_RESULTS,
        results,
        [
            "case_id",
            "case_type",
            "source_fixture_id",
            "measurement_run_id",
            "bundle_id",
            "collector_id",
            "schema_version",
            "evidence_label",
            "timing_admissible",
            "threshold_replay_status",
            "threshold_crossed_if_valid",
            "blocked_field",
            "blocked_reason",
            "expected_blocked_reason",
            "expected_reason_matched",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "measurement_quality_precondition_only",
        ],
    )
    write_csv(OUT_FAILURES, failure_rows(results), ["blocked_reason", "case_count", "fail_closed", "replay_status"])
    write_csv(
        OUT_REPLAY_BOUNDARY,
        replay_boundary(results),
        [
            "case_id",
            "timing_admissible",
            "threshold_crossed_if_valid",
            "threshold_replay_status",
            "blocked_reason",
            "invalid_timing_is_threshold_miss",
            "dc001_dc002_replay_allowed",
        ],
    )
    write_csv(
        OUT_CLAIM_BOUNDARY,
        claim_boundary(results),
        [
            "case_id",
            "timing_admissible",
            "existing_gatechain_allowed",
            "measurement_quality_precondition_only",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "boundary_reason",
        ],
    )


if __name__ == "__main__":
    main()
