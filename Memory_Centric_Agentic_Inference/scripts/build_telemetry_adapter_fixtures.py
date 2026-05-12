#!/usr/bin/env python3
# created: 2026-05-12T04:20:00Z
# cycle: 25
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ADAPTER-1
"""Build offline adapter interface rows and synthetic collector streams."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

COLLECTORS = DATA / "production_telemetry_collector_spec.csv"
JOIN = DATA / "production_telemetry_join_contract.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"
SCHEMA = DATA / "production_dc12_telemetry_schema.csv"

OUT_INTERFACE = DATA / "telemetry_adapter_interface.csv"
OUT_STREAMS = DATA / "telemetry_adapter_fixture_streams.csv"
OUT_INVALID = DATA / "telemetry_adapter_invalid_streams.csv"

EVIDENCE = "synthetic_adapter_fixture"
COMMON_KEYS = {
    "measurement_run_id": "adapter-run-synth-001",
    "production_target_id": "synthetic-adapter-target",
    "hardware_topology_id": "synthetic-topology-a",
    "tenant_id": "tenant-a",
    "security_context_id": "secctx-a",
    "workload_id": "workload-code-agent",
    "object_id": "object-kv-branch-001",
    "interval_id": "interval-0001",
    "topology_id": "synthetic-topology-a",
    "clock_id": "synthetic-monotonic-clock",
    "clock_offset_ms": "1",
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


def adapter_id(category: str) -> str:
    return "adapter-" + "".join(ch.lower() if ch.isalnum() else "-" for ch in category).strip("-").replace("--", "-")


def interface_rows() -> list[dict[str, object]]:
    collectors = read_csv(COLLECTORS)
    schema_fields = {row["field_name"] for row in read_csv(SCHEMA)}
    required_join_keys = {row["required_key"] for row in read_csv(JOIN)}
    preflight_by_category = {}
    for row in read_csv(PREFLIGHT):
        preflight_by_category.setdefault(row["collector_category"], []).append(row["check_id"])

    rows: list[dict[str, object]] = []
    for collector in collectors:
        category = collector["collector_category"]
        emitted = split_fields(collector["schema_fields"])
        derived = split_fields(collector["derived_fields"])
        unknown = [field for field in emitted if field not in schema_fields]
        rows.append(
            {
                "adapter_id": adapter_id(category),
                "collector_category": category,
                "stream_class": category,
                "required": "true",
                "input_contract": "newline-delimited records or CSV rows with common join envelope and stream payload",
                "emitted_schema_fields": "; ".join(emitted),
                "derived_schema_fields": "; ".join(derived),
                "required_join_keys": "; ".join(sorted(required_join_keys)),
                "clock_contract": collector["clock_alignment_requirement"],
                "provenance_contract": "collector_instance_id; collector_trust_domain; adapter_version; fixture_source",
                "preflight_checks": "; ".join(preflight_by_category.get(category, [])),
                "coverage_status": "covered" if not unknown else "unknown_schema_field",
                "evidence_label_allowed": EVIDENCE,
                "production_target_allowed": "false",
                "fail_closed_policy": "missing join key, unknown provenance, stale security context, or clock mismatch blocks normalization",
            }
        )
    rows.append(
        {
            "adapter_id": "adapter-topology-inventory",
            "collector_category": "topology inventory",
            "stream_class": "topology inventory",
            "required": "true",
            "input_contract": "deployment inventory records keyed by topology_id and joined to every interval envelope",
            "emitted_schema_fields": "hardware_topology_id; accelerator_type; topology_scope; production_target_id",
            "derived_schema_fields": "topology_id",
            "required_join_keys": "; ".join(sorted(required_join_keys)),
            "clock_contract": "topology inventory version must be valid for the measurement interval",
            "provenance_contract": "collector_instance_id; collector_trust_domain; adapter_version; fixture_source",
            "preflight_checks": "PF-001",
            "coverage_status": "covered",
            "evidence_label_allowed": EVIDENCE,
            "production_target_allowed": "false",
            "fail_closed_policy": "missing or untrusted topology inventory blocks calibration and architecture-option attribution",
        }
    )
    return rows


def base_stream(stream_id: str, category: str, payload: dict[str, object]) -> dict[str, object]:
    row: dict[str, object] = {
        "stream_id": stream_id,
        "fixture_case_id": "valid-adapter-candidate",
        "fixture_class": "valid",
        "collector_category": category,
        "adapter_id": adapter_id(category),
        "collector_instance_id": f"offline-{stream_id}",
        "collector_trust_domain": "offline_fixture_trusted_for_schema_only",
        "adapter_version": "adapter-interface-v1",
        "fixture_source": "offline_fixture",
        "evidence_label": EVIDENCE,
        "is_fixture": "true",
        "stream_timestamp_ms": "1000",
        "interval_start_ms": "1000",
        "interval_end_ms": "2000",
        **COMMON_KEYS,
    }
    row.update(payload)
    return row


def valid_streams() -> list[dict[str, object]]:
    option_b = "B_memory_object_reuse_and_tiering"
    return [
        base_stream(
            "accelerator-power",
            "accelerator energy/power counters",
            {
                "joules_measured": "18.5",
                "power_counter_source": "synthetic_accelerator_counter",
                "energy_noise_floor_j": "0.2",
                "accelerator_type": "synthetic-accelerator-v1",
                "interval_ms": "1000",
                "power_interval_start_ms": "1000",
                "power_interval_end_ms": "2000",
                "constant_id": "DC-001",
                "threshold_id": "DC001-BYTE-ENERGY-001",
            },
        ),
        base_stream(
            "host-power",
            "host energy/power counters",
            {
                "host_joules_measured": "2.5",
                "host_power_counter_source": "synthetic_host_counter",
                "host_energy_noise_floor_j": "0.1",
                "interval_ms": "1000",
            },
        ),
        base_stream(
            "tier-bytes",
            "source/destination tier byte counters",
            {
                "source_tier": "HBM",
                "destination_tier": "CXL_pooled_memory",
                "bytes_moved": "536870912",
                "resident_bytes": "1073741824",
                "byte_interval_start_ms": "1000",
                "byte_interval_end_ms": "2000",
            },
        ),
        base_stream(
            "cxl-latency",
            "CXL or pooled-memory latency p50/p95/p99",
            {
                "latency_p50_us": "8.0",
                "latency_p95_us": "42.0",
                "latency_p99_us": "75.0",
                "topology_scope": "single_pool_single_tenant_fixture",
            },
        ),
        base_stream(
            "tenant-concurrency",
            "queue depth and tenant concurrency",
            {
                "tenant_count": "3",
                "queue_depth": "9",
            },
        ),
        base_stream(
            "workload-labeler",
            "workload/object classification",
            {
                "workload_class": "code agent with verification loop",
                "object_class": "kv_cache_branch_state",
                "fixture_id": "adapter-valid-candidate",
                "fixture_class": "valid",
                "notes": "offline valid adapter fixture; not production evidence",
            },
        ),
        base_stream(
            "reuse-decision",
            "reuse decision and architecture option",
            {
                "architecture_option": option_b,
                "reuse_decision": "safe_reuse_candidate",
                "calibration_candidate": "true",
                "claimed_reuse_credit": "0.55",
                "claimed_energy_credit_j": "6.0",
                "constant_id": "DC-001",
                "threshold_id": "DC001-BYTE-ENERGY-001",
            },
        ),
        base_stream(
            "security-gates",
            "security/provenance/retention/verifier gates",
            {
                "security_allowed": "true",
                "provenance_valid": "true",
                "retention_valid": "true",
                "verifier_valid": "true",
                "security_context_fresh_until_ms": "5000",
            },
        ),
        base_stream(
            "topology-inventory",
            "topology inventory",
            {
                "hardware_topology_id": "synthetic-topology-a",
                "topology_scope": "offline_fixture_pool",
                "accelerator_type": "synthetic-accelerator-v1",
            },
        ),
    ]


def invalid_streams() -> list[dict[str, object]]:
    rows = []
    cases = [
        ("invalid-missing-stream", "missing_stream_class", {"collector_category": "accelerator energy/power counters", "drop_stream_id": "tier-bytes"}),
        ("invalid-missing-interval", "missing_join_key_interval_id", {"stream_id": "tier-bytes", "interval_id": ""}),
        ("invalid-clock-mismatch", "clock_alignment_failed", {"stream_id": "accelerator-power", "power_interval_end_ms": "2300"}),
        ("invalid-missing-security-context", "missing_join_key_security_context_id", {"stream_id": "security-gates", "security_context_id": ""}),
        ("invalid-stale-security", "stale_security_context", {"stream_id": "security-gates", "security_context_fresh_until_ms": "900"}),
        ("invalid-untrusted-provenance", "untrusted_collector_provenance", {"stream_id": "cxl-latency", "collector_trust_domain": "unknown_untrusted"}),
        ("invalid-evidence-target", "fixture_attempted_production_target", {"stream_id": "workload-labeler", "evidence_label": "production_target"}),
    ]
    valid_by_id = {row["stream_id"]: row for row in valid_streams()}
    for case_id, reason, patch in cases:
        stream_id = patch.get("stream_id", "invalid-control")
        base = dict(valid_by_id.get(stream_id, valid_by_id["workload-labeler"]))
        base.update(patch)
        base["fixture_case_id"] = case_id
        base["fixture_class"] = "invalid"
        base["expected_blocked_reason"] = reason
        rows.append(base)
    return rows


def main() -> None:
    # Input checks keep this adapter layer tied to the validated deployment contract.
    for path in [COLLECTORS, JOIN, PREFLIGHT, SCHEMA]:
        read_csv(path)

    interface = interface_rows()
    streams = valid_streams()
    invalid = invalid_streams()
    stream_fields = sorted({key for row in streams + invalid for key in row})

    write_csv(
        OUT_INTERFACE,
        interface,
        [
            "adapter_id",
            "collector_category",
            "stream_class",
            "required",
            "input_contract",
            "emitted_schema_fields",
            "derived_schema_fields",
            "required_join_keys",
            "clock_contract",
            "provenance_contract",
            "preflight_checks",
            "coverage_status",
            "evidence_label_allowed",
            "production_target_allowed",
            "fail_closed_policy",
        ],
    )
    write_csv(OUT_STREAMS, streams, stream_fields)
    write_csv(OUT_INVALID, invalid, stream_fields)


if __name__ == "__main__":
    main()
