#!/usr/bin/env python3
# created: 2026-05-12T11:00:00Z
# cycle: 32
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-TIMEBASE-1
"""Build timebase and observer-overhead fixtures for production telemetry replay."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = [
    DATA / "production_dc12_telemetry_schema.csv",
    DATA / "production_telemetry_join_contract.csv",
    DATA / "production_telemetry_collector_spec.csv",
    DATA / "production_dc12_ingestion_results.csv",
    DATA / "production_dc12_threshold_replay.csv",
    DATA / "evidence_gatechain_replay_results.csv",
    DATA / "final_claim_readiness_matrix.csv",
]

OUT_SCHEMA = DATA / "timebase_integrity_schema.csv"
OUT_VALID = DATA / "timebase_valid_fixture.csv"
OUT_INVALID = DATA / "timebase_invalid_fixtures.csv"
OUT_SENSITIVITY = DATA / "timebase_threshold_sensitivity_cases.csv"

FIELDS = [
    "case_id",
    "case_type",
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
    "expected_blocked_reason",
    "notes",
]

REQUIRED = {
    "source_fixture_id": "joins timing record to production telemetry threshold replay row",
    "measurement_run_id": "run identity shared by all collector streams",
    "bundle_id": "bundle identity shared with intake, attestation, and gatechain",
    "collector_id": "collector identity enrolled before gatechain replay",
    "schema_version": "production telemetry schema version",
    "evidence_label": "fixture labels remain non-production evidence",
    "clock_domain_id": "clock domain for all joined sources",
    "clock_sync_source": "NTP/PTP/monotonic source or operator-approved equivalent",
    "clock_sync_status": "declares whether the source was synchronized",
    "interval_id": "stable interval join key",
    "interval_start_ms": "canonical interval start",
    "interval_end_ms": "canonical interval end",
    "byte_interval_start_ms": "tier-byte counter interval start",
    "byte_interval_end_ms": "tier-byte counter interval end",
    "power_interval_start_ms": "power counter interval start",
    "power_interval_end_ms": "power counter interval end",
    "latency_interval_start_ms": "CXL/pooled-memory latency interval start",
    "latency_interval_end_ms": "CXL/pooled-memory latency interval end",
    "queue_interval_start_ms": "queue-depth interval start",
    "queue_interval_end_ms": "queue-depth interval end",
    "security_interval_start_ms": "security-gate timing interval start",
    "security_interval_end_ms": "security-gate timing interval end",
    "sampling_period_ms": "collector sampling period",
    "sampling_jitter_ms": "observed sampling jitter",
    "max_cross_source_skew_ms": "maximum offset across joined collector sources",
    "skew_tolerance_ms": "maximum accepted skew before replay becomes non-identifiable",
    "jitter_tolerance_ms": "maximum accepted jitter before replay becomes non-identifiable",
    "workload_label_sampled_at_ms": "time at which workload/object labels were sampled",
    "workload_label_max_age_ms": "maximum accepted label staleness",
    "collector_overhead_pct": "estimated collector-induced perturbation",
    "observer_perturbation_budget_pct": "maximum accepted observer overhead; equality blocks",
    "counter_sequence_start": "monotonic counter sequence at interval start",
    "counter_sequence_end": "monotonic counter sequence at interval end",
    "counter_reset_observed": "must be false within replay interval",
    "clock_drift_ppm": "observed clock drift across the bundle",
    "clock_drift_tolerance_ppm": "maximum accepted drift",
}

BASE = {
    "case_id": "valid-timebase-complete-fixture",
    "case_type": "valid_fixture",
    "source_fixture_id": "valid-dc002-rag-c",
    "measurement_run_id": "gatechain-run-001",
    "bundle_id": "gatechain-bundle-001",
    "collector_id": "collector-fixture-001",
    "schema_version": "production_dc12_schema_v1",
    "evidence_label": "timebase_integrity_fixture",
    "clock_domain_id": "clock-domain-fixture-ptp-a",
    "clock_sync_source": "fixture_ptp_grandmaster",
    "clock_sync_status": "synchronized",
    "interval_id": "interval-0001",
    "interval_start_ms": 0,
    "interval_end_ms": 1000,
    "byte_interval_start_ms": 0,
    "byte_interval_end_ms": 1000,
    "power_interval_start_ms": 0,
    "power_interval_end_ms": 1000,
    "latency_interval_start_ms": 0,
    "latency_interval_end_ms": 1000,
    "queue_interval_start_ms": 0,
    "queue_interval_end_ms": 1000,
    "security_interval_start_ms": 0,
    "security_interval_end_ms": 1000,
    "sampling_period_ms": 50,
    "sampling_jitter_ms": 5,
    "max_cross_source_skew_ms": 0,
    "skew_tolerance_ms": 50,
    "jitter_tolerance_ms": 25,
    "workload_label_sampled_at_ms": 950,
    "workload_label_max_age_ms": 200,
    "collector_overhead_pct": 1.5,
    "observer_perturbation_budget_pct": 5.0,
    "counter_sequence_start": 1000,
    "counter_sequence_end": 1020,
    "counter_reset_observed": "false",
    "clock_drift_ppm": 4,
    "clock_drift_tolerance_ppm": 25,
    "expected_blocked_reason": "",
    "notes": "complete timing fixture; timing admissibility is a measurement-quality precondition only",
}

INVALIDS = [
    ("invalid-unknown-source-fixture", {"source_fixture_id": "unknown-threshold-row"}, "unknown_source_fixture_id"),
    ("invalid-measurement-run-id-mismatch", {"measurement_run_id": "wrong-run"}, "measurement_run_id_mismatch"),
    ("invalid-bundle-id-mismatch", {"bundle_id": "wrong-bundle"}, "bundle_id_mismatch"),
    ("invalid-collector-id-mismatch", {"collector_id": "wrong-collector"}, "collector_id_mismatch"),
    ("invalid-schema-version-mismatch", {"schema_version": "wrong_schema_v9"}, "schema_version_mismatch"),
    ("invalid-missing-clock-domain", {"clock_domain_id": ""}, "missing_clock_domain"),
    ("invalid-cross-source-skew", {"max_cross_source_skew_ms": 75}, "cross_source_skew_above_tolerance"),
    ("invalid-negative-skew", {"max_cross_source_skew_ms": -1}, "negative_cross_source_skew"),
    ("invalid-interval-overlap-mismatch", {"power_interval_start_ms": 100, "power_interval_end_ms": 1100}, "interval_overlap_mismatch"),
    ("invalid-interval-gap", {"latency_interval_start_ms": 1050, "latency_interval_end_ms": 2050}, "interval_gap"),
    ("invalid-inconsistent-sampling-period", {"sampling_period_ms": 333}, "inconsistent_sampling_period"),
    ("invalid-zero-sampling-period", {"sampling_period_ms": 0}, "non_positive_sampling_period"),
    ("invalid-negative-jitter", {"sampling_jitter_ms": -1}, "negative_sampling_jitter"),
    ("invalid-stale-workload-label", {"workload_label_sampled_at_ms": 700}, "stale_workload_label"),
    ("invalid-missing-overhead-estimate", {"collector_overhead_pct": ""}, "missing_collector_overhead_estimate"),
    ("invalid-overhead-above-budget", {"collector_overhead_pct": 5.0}, "observer_overhead_above_budget"),
    ("invalid-negative-overhead", {"collector_overhead_pct": -0.1}, "negative_collector_overhead"),
    ("invalid-counter-reset-inside-interval", {"counter_reset_observed": "true", "counter_sequence_end": 5}, "counter_reset_inside_interval"),
    ("invalid-clock-drift-across-bundle", {"clock_drift_ppm": 40}, "clock_drift_across_bundle"),
    ("invalid-negative-clock-drift", {"clock_drift_ppm": -1}, "negative_clock_drift"),
    ("invalid-fixture-attempted-production-calibration", {"evidence_label": "production_target"}, "fixture_attempted_production_calibration"),
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
    for case_id, overrides, reason in INVALIDS:
        row = dict(BASE)
        row.update(overrides)
        row.update(
            {
                "case_id": case_id,
                "case_type": "invalid_fixture",
                "expected_blocked_reason": reason,
                "notes": "malformed timing must become measurement_invalid, not a threshold miss",
            }
        )
        rows.append(row)
    return rows


def sensitivity_rows() -> list[dict[str, object]]:
    rows = []
    case_no = 1
    for skew_ms in [0, 10, 25, 50, 75, 100]:
        for jitter_ms in [0, 10, 25, 35]:
            for overhead_pct in [0.0, 2.5, 4.9, 5.0, 7.5]:
                identifiable = skew_ms <= 50 and jitter_ms <= 25 and overhead_pct < 5.0
                rows.append(
                    {
                        "sensitivity_case_id": f"timebase-sensitivity-{case_no:03d}",
                        "source_fixture_id": "valid-dc002-rag-c",
                        "skew_ms": skew_ms,
                        "jitter_ms": jitter_ms,
                        "collector_overhead_pct": overhead_pct,
                        "skew_tolerance_ms": 50,
                        "jitter_tolerance_ms": 25,
                        "observer_perturbation_budget_pct": 5.0,
                        "threshold_crossed_if_valid": "true",
                        "threshold_replay_status": "threshold_passed" if identifiable else "measurement_invalid",
                        "interpretability": "identifiable" if identifiable else "non_identifiable",
                    }
                )
                case_no += 1
    return rows


def main() -> None:
    require_inputs()
    schema = [
        {
            "field_name": field,
            "required": str(field in REQUIRED).lower(),
            "type": "number"
            if field.endswith("_ms") or field.endswith("_pct") or field.endswith("_ppm") or field.startswith("counter_sequence")
            else "boolean"
            if field == "counter_reset_observed"
            else "string",
            "gate": REQUIRED.get(field, "diagnostic"),
        }
        for field in FIELDS
        if field not in {"case_id", "case_type", "expected_blocked_reason", "notes"}
    ]
    valid = [dict(BASE)]
    write_csv(OUT_SCHEMA, schema, ["field_name", "required", "type", "gate"])
    write_csv(OUT_VALID, valid, FIELDS)
    write_csv(OUT_INVALID, invalid_rows(), FIELDS)
    write_csv(
        OUT_SENSITIVITY,
        sensitivity_rows(),
        [
            "sensitivity_case_id",
            "source_fixture_id",
            "skew_ms",
            "jitter_ms",
            "collector_overhead_pct",
            "skew_tolerance_ms",
            "jitter_tolerance_ms",
            "observer_perturbation_budget_pct",
            "threshold_crossed_if_valid",
            "threshold_replay_status",
            "interpretability",
        ],
    )


if __name__ == "__main__":
    main()
