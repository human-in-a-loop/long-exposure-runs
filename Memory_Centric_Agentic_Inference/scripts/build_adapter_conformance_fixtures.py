#!/usr/bin/env python3
# created: 2026-05-12T05:20:00Z
# cycle: 26
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PORT-1
"""Build backend-shaped adapter conformance contracts and fixtures."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INTERFACE = DATA / "telemetry_adapter_interface.csv"
JOIN = DATA / "production_telemetry_join_contract.csv"
SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"

OUT_CONTRACT = DATA / "adapter_conformance_contract.csv"
OUT_ALIAS = DATA / "adapter_join_alias_map.csv"
OUT_VALID = DATA / "adapter_backend_profile_fixtures.csv"
OUT_INVALID = DATA / "adapter_backend_profile_invalid_fixtures.csv"

EVIDENCE = "adapter_conformance_fixture"

PROFILE_CLASSES = [
    ("accelerator-power-profile", "accelerator energy/power counters"),
    ("host-power-profile", "host energy/power counters"),
    ("memory-tier-bytes-profile", "source/destination tier byte counters"),
    ("pooled-latency-profile", "CXL or pooled-memory latency p50/p95/p99"),
    ("concurrency-queue-profile", "queue depth and tenant concurrency"),
    ("workload-object-label-profile", "workload/object classification"),
    ("architecture-reuse-profile", "reuse decision and architecture option"),
    ("security-provenance-profile", "security/provenance/retention/verifier gates"),
    ("topology-inventory-profile", "topology inventory"),
]

COMMON = {
    "logical_run_id": "port-run-001",
    "measurement_run_id": "",
    "production_target_id": "conformance-target",
    "hardware_topology_id": "conformance-topology-a",
    "topology_id": "conformance-topology-a",
    "tenant_id": "tenant-a",
    "security_context_id": "secctx-a",
    "workload_id": "workload-code-agent",
    "object_id": "object-kv-branch-001",
    "interval_id": "interval-0001",
    "clock_domain": "monotonic_ns",
    "clock_offset_ms": "1",
    "interval_start_ms": "1000",
    "interval_end_ms": "2000",
    "interval_ms": "1000",
    "schema_version": "production_dc12_v1",
    "collector_trust_domain": "adapter_conformance_fixture_trusted_for_shape_only",
    "adapter_version": "adapter-conformance-v1",
    "evidence_label": EVIDENCE,
    "production_calibrated": "false",
    "production_ready": "false",
}


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


def split_fields(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def build_alias_map(join_rows: list[dict[str, str]], schema_fields: set[str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    canonical_overrides = {
        "run_id": "measurement_run_id",
        "interval_id": "interval_ms",
        "workload_id": "workload_class",
        "object_id": "object_class",
        "topology_id": "hardware_topology_id",
        "tenant_id": "tenant_count",
        "security_context_id": "security_allowed",
    }
    for join in join_rows:
        logical = join["required_key"]
        canonical = canonical_overrides[logical]
        rows.append(
            {
                "join_domain": join["join_domain"],
                "logical_key": logical,
                "canonical_field": canonical,
                "accepted_aliases": logical if logical != canonical else "",
                "canonical_in_production_schema": str(canonical in schema_fields).lower(),
                "source_fields": join["source_fields"],
                "alias_policy": "alias_input_must_emit_canonical_field; unknown_alias_blocks",
                "calibration_blocker": join["calibration_blocker"],
            }
        )
    return rows


def build_contract(interface_rows: list[dict[str, str]], alias_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    alias_by_key = {row["logical_key"]: row["canonical_field"] for row in alias_rows}
    rows: list[dict[str, object]] = []
    for row in interface_rows:
        if row["collector_category"] == "interval alignment and noise-floor metadata":
            continue
        canonical_join = [alias_by_key.get(key, key) for key in split_fields(row["required_join_keys"])]
        rows.append(
            {
                "profile_class": row["collector_category"],
                "adapter_id": row["adapter_id"],
                "required": row["required"],
                "canonical_join_fields": "; ".join(sorted(set(canonical_join))),
                "required_units": "power=W; energy=J; bytes=B; latency=us; timestamp=ms",
                "clock_requirement": "single declared clock_domain; offset <= 10% of interval_ms; byte and power intervals align",
                "schema_version_requirement": "schema_version=production_dc12_v1",
                "provenance_requirement": "adapter_version; collector_trust_domain; fixture evidence only for this kit",
                "evidence_label_allowed": EVIDENCE,
                "production_target_allowed": "false",
                "fail_closed_policy": "unknown alias, invalid unit, missing clock, interval mismatch, stale provenance, missing tenant, or missing security context blocks conformance",
            }
        )
    return rows


def profile(profile_id: str, category: str, payload: dict[str, object]) -> dict[str, object]:
    row: dict[str, object] = {
        "profile_id": profile_id,
        "fixture_case_id": "valid-conformance-profile",
        "fixture_class": "valid",
        "profile_class": category,
        "backend_name": profile_id.replace("-profile", "-backend"),
        "join_alias_used": "run_id",
        "alias_value": COMMON["logical_run_id"],
        "unknown_alias_name": "",
        **COMMON,
        "power_unit": "W",
        "energy_unit": "J",
        "byte_unit": "B",
        "latency_unit": "us",
        "timestamp_unit": "ms",
        "byte_interval_start_ms": "1000",
        "byte_interval_end_ms": "2000",
        "power_interval_start_ms": "1000",
        "power_interval_end_ms": "2000",
        "security_context_fresh_until_ms": "5000",
    }
    row.update(payload)
    return row


def valid_profiles() -> list[dict[str, object]]:
    return [
        profile("accelerator-power-profile", "accelerator energy/power counters", {"joules_measured": "18.5", "power_counter_source": "backend_accel_counter", "energy_noise_floor_j": "0.2", "accelerator_type": "conformance-accelerator-v1"}),
        profile("host-power-profile", "host energy/power counters", {"host_joules_measured": "2.5", "host_power_counter_source": "backend_host_counter"}),
        profile("memory-tier-bytes-profile", "source/destination tier byte counters", {"source_tier": "HBM", "destination_tier": "CXL_pooled_memory", "bytes_moved": "536870912", "resident_bytes": "1073741824"}),
        profile("pooled-latency-profile", "CXL or pooled-memory latency p50/p95/p99", {"latency_p50_us": "8.0", "latency_p95_us": "42.0", "latency_p99_us": "75.0", "topology_scope": "conformance_pool_fixture"}),
        profile("concurrency-queue-profile", "queue depth and tenant concurrency", {"tenant_count": "3", "queue_depth": "9"}),
        profile("workload-object-label-profile", "workload/object classification", {"workload_class": "code agent with verification loop", "object_class": "kv_cache_branch_state", "fixture_id": "adapter-conformance-valid", "notes": "backend-shaped fixture; not production evidence"}),
        profile("architecture-reuse-profile", "reuse decision and architecture option", {"architecture_option": "B_memory_object_reuse_and_tiering", "reuse_decision": "safe_reuse_candidate", "calibration_candidate": "true", "claimed_reuse_credit": "0.55", "claimed_energy_credit_j": "6.0", "constant_id": "DC-001", "threshold_id": "DC001-BYTE-ENERGY-001"}),
        profile("security-provenance-profile", "security/provenance/retention/verifier gates", {"security_allowed": "true", "provenance_valid": "true", "retention_valid": "true", "verifier_valid": "true"}),
        profile("topology-inventory-profile", "topology inventory", {"hardware_topology_id": "conformance-topology-a", "topology_scope": "conformance_pool_fixture", "accelerator_type": "conformance-accelerator-v1"}),
    ]


def invalid_profiles(valid: list[dict[str, object]]) -> list[dict[str, object]]:
    by_id = {row["profile_id"]: row for row in valid}
    cases = [
        ("invalid-unknown-alias", "unknown_alias", "accelerator-power-profile", {"join_alias_used": "operator_run", "unknown_alias_name": "operator_run"}),
        ("invalid-run-id-replacement", "run_id_without_canonicalization", "accelerator-power-profile", {"join_alias_used": "run_id", "measurement_run_id": "port-run-001"}),
        ("invalid-energy-unit", "invalid_unit", "accelerator-power-profile", {"energy_unit": "kWh"}),
        ("invalid-latency-unit", "invalid_unit", "pooled-latency-profile", {"latency_unit": "ns"}),
        ("invalid-missing-clock", "missing_clock_domain", "memory-tier-bytes-profile", {"clock_domain": ""}),
        ("invalid-interval-mismatch", "interval_alignment_failed", "memory-tier-bytes-profile", {"byte_interval_end_ms": "2300"}),
        ("invalid-stale-provenance", "stale_provenance", "workload-object-label-profile", {"collector_trust_domain": "stale_or_untrusted"}),
        ("invalid-missing-tenant", "missing_tenant_label", "concurrency-queue-profile", {"tenant_id": ""}),
        ("invalid-missing-security-context", "missing_security_context", "security-provenance-profile", {"security_context_id": ""}),
        ("invalid-missing-security-stream", "missing_security_stream", "security-provenance-profile", {"drop_profile_class": "security/provenance/retention/verifier gates"}),
        ("invalid-production-target-evidence", "fixture_attempted_production_target", "workload-object-label-profile", {"evidence_label": "production_target", "production_ready": "true"}),
    ]
    rows: list[dict[str, object]] = []
    for case_id, reason, profile_id, patch in cases:
        row = dict(by_id[profile_id])
        row.update(patch)
        row["fixture_case_id"] = case_id
        row["fixture_class"] = "invalid"
        row["expected_blocked_reason"] = reason
        rows.append(row)
    return rows


def main() -> None:
    interface_rows = read_csv(INTERFACE)
    join_rows = read_csv(JOIN)
    schema_rows = read_csv(SCHEMA)
    read_csv(PREFLIGHT)
    schema_fields = {row["field_name"] for row in schema_rows}

    aliases = build_alias_map(join_rows, schema_fields)
    contract = build_contract(interface_rows, aliases)
    valid = valid_profiles()
    invalid = invalid_profiles(valid)
    profile_fields = sorted({key for row in valid + invalid for key in row})

    write_csv(
        OUT_CONTRACT,
        contract,
        [
            "profile_class",
            "adapter_id",
            "required",
            "canonical_join_fields",
            "required_units",
            "clock_requirement",
            "schema_version_requirement",
            "provenance_requirement",
            "evidence_label_allowed",
            "production_target_allowed",
            "fail_closed_policy",
        ],
    )
    write_csv(
        OUT_ALIAS,
        aliases,
        ["join_domain", "logical_key", "canonical_field", "accepted_aliases", "canonical_in_production_schema", "source_fields", "alias_policy", "calibration_blocker"],
    )
    write_csv(OUT_VALID, valid, profile_fields)
    write_csv(OUT_INVALID, invalid, profile_fields)


if __name__ == "__main__":
    main()
