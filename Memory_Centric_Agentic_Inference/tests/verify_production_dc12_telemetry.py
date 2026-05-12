#!/usr/bin/env python3
# created: 2026-05-11T23:45:00Z
# cycle: 20
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODTELEM-1
"""Verify production DC-001/DC-002 telemetry contract artifacts."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_SCHEMA_FIELDS = {
    "measurement_run_id",
    "evidence_label",
    "production_target_id",
    "hardware_topology_id",
    "accelerator_type",
    "source_tier",
    "destination_tier",
    "object_class",
    "workload_class",
    "architecture_option",
    "reuse_decision",
    "bytes_moved",
    "resident_bytes",
    "interval_ms",
    "joules_measured",
    "power_counter_source",
    "energy_noise_floor_j",
    "latency_p50_us",
    "latency_p95_us",
    "latency_p99_us",
    "tenant_count",
    "queue_depth",
    "security_allowed",
    "provenance_valid",
    "retention_valid",
    "verifier_valid",
    "calibration_candidate",
}

BASELINES = [
    DATA / "energy_measurement_requirements.csv",
    DATA / "cxl_contention_thresholds.csv",
    DATA / "energy_architecture_sensitivity.csv",
    DATA / "memory_plan_constraint_sensitivity.csv",
    DATA / "security_enforcement_decisions.csv",
    DATA / "dc12_claim_update_matrix.csv",
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_fields(rows: list[dict[str, str]], fields: set[str], name: str) -> None:
    assert fields <= set(rows[0]), f"{name} missing {fields - set(rows[0])}"


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    before = {path: digest(path) for path in BASELINES}

    schema = read_csv(DATA / "production_dc12_telemetry_schema.csv")
    valid = read_csv(DATA / "production_dc12_valid_fixture.csv")
    invalid = read_csv(DATA / "production_dc12_invalid_fixtures.csv")
    results = read_csv(DATA / "production_dc12_ingestion_results.csv")
    replay = read_csv(DATA / "production_dc12_threshold_replay.csv")
    claims = read_csv(DATA / "production_dc12_claim_update_matrix.csv")
    missing = read_csv(DATA / "production_dc12_missing_fields_report.csv")

    assert REQUIRED_SCHEMA_FIELDS <= {row["field_name"] for row in schema if row["required"] == "true"}
    assert_fields(results, {"schema_valid", "join_valid", "noise_floor_passed", "security_credit_allowed", "threshold_crossed", "production_calibrated", "blocked_reason"}, "ingestion results")
    assert_fields(replay, {"fixture_id", "constant_id", "threshold_id", "measured_value", "threshold_value", "threshold_crossed"}, "threshold replay")
    assert {row["constant_id"] for row in valid} >= {"DC-001", "DC-002"}
    assert len(invalid) >= 8

    invalid_results = [row for row in results if row["fixture_class"] == "invalid"]
    assert invalid_results and all(row["production_calibrated"] == "false" for row in invalid_results)
    assert all(row["blocked_reason"] for row in invalid_results), invalid_results
    assert all(float(row["reuse_credit_granted"]) == 0.0 for row in invalid_results), invalid_results
    assert all(float(row["energy_credit_granted_j"]) == 0.0 for row in invalid_results), invalid_results
    assert {row["blocked_reason"] for row in invalid_results} >= {
        "missing_required_field",
        "power_byte_interval_mismatch",
        "below_noise_floor",
        "security_denied_positive_credit",
        "not_production_evidence_label",
    }

    host_proxy = next(row for row in results if row["fixture_id"] == "invalid-host-proxy-mislabeled")
    assert host_proxy["production_calibrated"] == "false"
    assert host_proxy["blocked_reason"] == "not_production_evidence_label"

    below_noise = next(row for row in results if row["fixture_id"] == "invalid-below-noise")
    assert below_noise["noise_floor_passed"] == "false"
    assert below_noise["production_calibrated"] == "false"

    denied = next(row for row in results if row["fixture_id"] == "invalid-security-positive-credit")
    assert denied["security_credit_allowed"] == "false"
    assert denied["reuse_credit_granted"] == "0.0"
    assert denied["energy_credit_granted_j"] == "0.0"

    candidates = [row for row in results if row["calibration_candidate"] == "true"]
    assert candidates, "valid synthetic rows should become candidate-only rows"
    assert all(row["evidence_label"] == "synthetic_production_fixture" for row in candidates)
    assert all(row["production_calibrated"] == "false" for row in results)
    assert any(row["threshold_crossed"] == "true" for row in replay if row["constant_id"] == "DC-002")

    cl012 = next(row for row in claims if row["claim_id"] == "CL-012")
    assert cl012["production_calibrated"] == "false"
    assert cl012["evidence_label"] == "synthetic_production_fixture"
    control = next(row for row in claims if row["claim_id"] == "CONTROL-OPTION-A")
    assert "controls remain Option A" in control["basis"]

    required_missing = {
        "accelerator_power_counters",
        "tier_specific_bytes",
        "cxl_pooled_memory_latency",
        "tenant_concurrency",
        "workload_object_labels",
    }
    assert required_missing <= {row["telemetry_id"] for row in missing}
    assert all(row["covered_by_schema"] == "true" for row in missing)

    for fig in [
        DATA / "production_dc12_telemetry_coverage.png",
        DATA / "production_dc12_threshold_replay.png",
        DATA / "production_dc12_claim_gate_matrix.png",
    ]:
        assert_png_nonblank(fig)

    after = {path: digest(path) for path in BASELINES}
    assert before == after, "baseline CSVs were modified during verification"

    print("verify_production_dc12_telemetry: ok")


if __name__ == "__main__":
    main()
