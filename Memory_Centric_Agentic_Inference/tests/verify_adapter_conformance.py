#!/usr/bin/env python3
# created: 2026-05-12T05:35:00Z
# cycle: 26
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PORT-1

from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from ingest_production_dc12_telemetry import blocked_reason, required_fields, threshold_map  # noqa: E402


REQUIRED_STREAMS = {
    "accelerator energy/power counters",
    "host energy/power counters",
    "source/destination tier byte counters",
    "CXL or pooled-memory latency p50/p95/p99",
    "queue depth and tenant concurrency",
    "workload/object classification",
    "reuse decision and architecture option",
    "security/provenance/retention/verifier gates",
    "topology inventory",
}
EXPECTED_BLOCKS = {
    "unknown_alias",
    "run_id_without_canonicalization",
    "invalid_unit",
    "missing_clock_domain",
    "interval_alignment_failed",
    "stale_provenance",
    "missing_tenant_label",
    "missing_security_context",
    "missing_profile_class",
    "fixture_attempted_production_target",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "production_dc12_telemetry_schema.csv")
    schema_fields = {row["field_name"] for row in schema}
    aliases = read_csv(DATA / "adapter_join_alias_map.csv")
    contract = read_csv(DATA / "adapter_conformance_contract.csv")
    profiles = read_csv(DATA / "adapter_backend_profile_fixtures.csv")
    invalid_profiles = read_csv(DATA / "adapter_backend_profile_invalid_fixtures.csv")
    results = read_csv(DATA / "adapter_conformance_results.csv")
    failures = read_csv(DATA / "adapter_conformance_failure_modes.csv")
    boundary = read_csv(DATA / "adapter_conformance_ingestion_boundary.csv")

    assert REQUIRED_STREAMS <= {row["profile_class"] for row in profiles}
    assert REQUIRED_STREAMS <= {row["profile_class"] for row in contract}
    assert len(invalid_profiles) >= 10

    assert all(row["canonical_field"] in schema_fields for row in aliases)
    assert all(row["alias_policy"] for row in aliases)
    run_alias = next(row for row in aliases if row["logical_key"] == "run_id")
    assert run_alias["canonical_field"] == "measurement_run_id"
    assert run_alias["accepted_aliases"] == "run_id"

    valid = next(row for row in results if row["fixture_case_id"] == "valid-conformance-profile")
    assert valid["status"] == "pass"
    assert valid["run_alias_resolved"] == "true"
    assert valid["canonical_measurement_run_id"] == "port-run-001"

    invalid = [row for row in results if row["status"] == "fail"]
    observed = {row["blocked_reason"].split(":")[0] for row in invalid}
    assert EXPECTED_BLOCKS <= observed, observed
    assert all(row["blocked_reason"] for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-unknown-alias" and row["blocked_reason"] == "unknown_alias" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-energy-unit" and row["blocked_reason"] == "invalid_unit" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-latency-unit" and row["blocked_reason"] == "invalid_unit" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-missing-clock" and row["blocked_reason"] == "missing_clock_domain" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-interval-mismatch" and row["blocked_reason"] == "interval_alignment_failed" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-stale-provenance" and row["blocked_reason"] == "stale_provenance" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-missing-tenant" and row["blocked_reason"] == "missing_tenant_label" for row in invalid)
    assert any(row["fixture_case_id"] == "invalid-missing-security-context" and row["blocked_reason"] == "missing_security_context" for row in invalid)

    assert all(row["evidence_label"] == "adapter_conformance_fixture" for row in results)
    assert all(row["production_calibrated"] == "false" for row in results)
    assert all(row["production_ready"] == "false" for row in results)
    assert all(row["fail_closed"] == "true" for row in failures)
    assert sum(int(row["invalid_profile_count"]) for row in failures) == len(invalid)

    assert all(row["evidence_label"] == "adapter_conformance_fixture" for row in boundary)
    assert all(row["production_target_allowed"] == "false" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in boundary)
    assert valid["evidence_label"] != "production_target"

    req_fields = required_fields(schema)
    thresholds = threshold_map(read_csv(DATA / "cxl_contention_thresholds.csv"))
    valid_shape = {row["field_name"]: "" for row in schema}
    valid_shape.update(
        {
            "fixture_id": "adapter-conformance-valid",
            "fixture_class": "valid",
            "measurement_run_id": valid["canonical_measurement_run_id"],
            "evidence_label": valid["evidence_label"],
            "production_target_id": "conformance-target",
            "hardware_topology_id": "conformance-topology-a",
            "accelerator_type": "conformance-accelerator-v1",
            "source_tier": "HBM",
            "destination_tier": "CXL_pooled_memory",
            "object_class": "kv_cache_branch_state",
            "workload_class": "code agent with verification loop",
            "architecture_option": "B_memory_object_reuse_and_tiering",
            "reuse_decision": "safe_reuse_candidate",
            "bytes_moved": "536870912",
            "resident_bytes": "1073741824",
            "interval_ms": "1000",
            "joules_measured": "18.5",
            "power_counter_source": "backend_accel_counter",
            "energy_noise_floor_j": "0.2",
            "latency_p50_us": "8.0",
            "latency_p95_us": "42.0",
            "latency_p99_us": "75.0",
            "tenant_count": "3",
            "queue_depth": "9",
            "security_allowed": "true",
            "provenance_valid": "true",
            "retention_valid": "true",
            "verifier_valid": "true",
            "calibration_candidate": "true",
            "byte_interval_start_ms": "1000",
            "byte_interval_end_ms": "2000",
            "power_interval_start_ms": "1000",
            "power_interval_end_ms": "2000",
            "constant_id": "DC-001",
            "threshold_id": "DC001-BYTE-ENERGY-001",
        }
    )
    gates, reason = blocked_reason(valid_shape, req_fields, thresholds)
    assert gates["schema_valid"], gates
    assert reason == "not_production_evidence_label", reason

    for fig in [
        DATA / "adapter_conformance_coverage.png",
        DATA / "adapter_conformance_failures.png",
        DATA / "adapter_conformance_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: adapter conformance kit verified.")


if __name__ == "__main__":
    main()
