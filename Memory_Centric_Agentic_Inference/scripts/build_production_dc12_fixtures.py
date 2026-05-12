#!/usr/bin/env python3
# created: 2026-05-11T23:30:00Z
# cycle: 20
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODTELEM-1
"""Build production-shaped DC-001/DC-002 telemetry fixtures.

The fixtures are synthetic contract probes, not empirical production evidence.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA_OUT = DATA / "production_dc12_telemetry_schema.csv"
VALID_OUT = DATA / "production_dc12_valid_fixture.csv"
INVALID_OUT = DATA / "production_dc12_invalid_fixtures.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

FIELDS = [
    "fixture_id",
    "fixture_class",
    "constant_id",
    "threshold_id",
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
    "byte_interval_start_ms",
    "byte_interval_end_ms",
    "power_interval_start_ms",
    "power_interval_end_ms",
    "topology_scope",
    "claimed_reuse_credit",
    "claimed_energy_credit_j",
    "notes",
]

REQUIRED_FIELDS = {
    "measurement_run_id": "joins all rows from one target measurement run",
    "evidence_label": "separates host_local_proxy, synthetic fixtures, and real production targets",
    "production_target_id": "prevents unjoined counter rows from different deployments",
    "hardware_topology_id": "binds power/byte/latency data to a target topology",
    "accelerator_type": "records accelerator generation and memory hierarchy",
    "source_tier": "supports tier-specific byte movement",
    "destination_tier": "supports tier-specific byte movement",
    "object_class": "joins telemetry to memory-object policy thresholds",
    "workload_class": "joins telemetry to workload thresholds and controls",
    "architecture_option": "joins measurements to Option A/B/C decisions",
    "reuse_decision": "binds energy credit to reuse or recompute outcome",
    "bytes_moved": "required for DC-001 joules/byte",
    "resident_bytes": "required for residency and retained-value context",
    "interval_ms": "normalizes joined counters over a common interval",
    "joules_measured": "direct target energy counter value for DC-001",
    "power_counter_source": "documents accelerator/host power source",
    "energy_noise_floor_j": "blocks below-noise energy claims",
    "latency_p50_us": "required for DC-002 contention distribution",
    "latency_p95_us": "required for DC-002 contention distribution",
    "latency_p99_us": "required for DC-002 contention distribution",
    "tenant_count": "required contention join key",
    "queue_depth": "required contention join key",
    "security_allowed": "hard gate for reuse credit",
    "provenance_valid": "hard gate for reuse credit",
    "retention_valid": "hard gate for reuse credit",
    "verifier_valid": "hard gate for reuse credit",
    "calibration_candidate": "declares whether fixture is intended to probe promotion gates",
}


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def base_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "fixture_id": "",
        "fixture_class": "valid",
        "constant_id": "DC-001",
        "threshold_id": "DC001-BYTE-ENERGY-001",
        "measurement_run_id": "prod-dc12-synth-run-001",
        "evidence_label": "synthetic_production_fixture",
        "production_target_id": "target-gpu-cxl-cluster-a",
        "hardware_topology_id": "topo-gpu-hbm-cxlpool-a",
        "accelerator_type": "synthetic_gpu_hbm",
        "source_tier": "HBM",
        "destination_tier": "CXL_or_pooled_memory_warm_tier",
        "object_class": "retrieved context; prefix cache; semantic cache entry; tool output",
        "workload_class": "RAG",
        "architecture_option": OPTION_B,
        "reuse_decision": "safe_reuse",
        "bytes_moved": 1_073_741_824,
        "resident_bytes": 536_870_912,
        "interval_ms": 1000,
        "joules_measured": 140.0,
        "power_counter_source": "accelerator_and_host_power_counter",
        "energy_noise_floor_j": 5.0,
        "latency_p50_us": 1.2,
        "latency_p95_us": 2.0,
        "latency_p99_us": 8.0,
        "tenant_count": 8,
        "queue_depth": 32,
        "security_allowed": "true",
        "provenance_valid": "true",
        "retention_valid": "true",
        "verifier_valid": "true",
        "calibration_candidate": "true",
        "byte_interval_start_ms": 0,
        "byte_interval_end_ms": 1000,
        "power_interval_start_ms": 0,
        "power_interval_end_ms": 1000,
        "topology_scope": "target_cxl_pool",
        "claimed_reuse_credit": 10.0,
        "claimed_energy_credit_j": 60.0,
        "notes": "synthetic production-shaped fixture",
    }
    row.update(overrides)
    return row


def build_schema() -> list[dict[str, object]]:
    return [
        {
            "field_name": field,
            "required": str(field in REQUIRED_FIELDS).lower(),
            "type": "number"
            if field
            in {
                "bytes_moved",
                "resident_bytes",
                "interval_ms",
                "joules_measured",
                "energy_noise_floor_j",
                "latency_p50_us",
                "latency_p95_us",
                "latency_p99_us",
                "tenant_count",
                "queue_depth",
                "byte_interval_start_ms",
                "byte_interval_end_ms",
                "power_interval_start_ms",
                "power_interval_end_ms",
                "claimed_reuse_credit",
                "claimed_energy_credit_j",
            }
            else "boolean"
            if field
            in {
                "security_allowed",
                "provenance_valid",
                "retention_valid",
                "verifier_valid",
                "calibration_candidate",
            }
            else "string",
            "gate": REQUIRED_FIELDS.get(field, "diagnostic/provenance"),
        }
        for field in FIELDS
    ]


def build_valid() -> list[dict[str, object]]:
    return [
        base_row(fixture_id="valid-dc001-rag-b", notes="DC-001 above-noise byte/energy row"),
        base_row(
            fixture_id="valid-dc002-rag-c",
            constant_id="DC-002",
            threshold_id="DC002-RAG-C-p99",
            object_class="branch state; verifier state; trajectory log; durable workspace",
            architecture_option=OPTION_C,
            latency_p50_us=1.3,
            latency_p95_us=2.4,
            latency_p99_us=9.2,
            notes="DC-002 contention row crossing the existing RAG-C p99 threshold",
        ),
        base_row(
            fixture_id="valid-dc002-code-b",
            constant_id="DC-002",
            threshold_id="DC002-code-agent loop-B-p95",
            workload_class="code-agent loop",
            architecture_option=OPTION_B,
            latency_p50_us=1.1,
            latency_p95_us=3.0,
            latency_p99_us=7.5,
            notes="DC-002 contention row below the existing code-agent B p95 threshold",
        ),
        base_row(
            fixture_id="valid-control-a",
            constant_id="DC-002",
            threshold_id="DC002-single-turn chat control-B-p95",
            workload_class="single-turn chat control",
            object_class="retrieved context; prefix cache; semantic cache entry; tool output",
            architecture_option=OPTION_A,
            reuse_decision="not_reuse_candidate",
            claimed_reuse_credit=0.0,
            claimed_energy_credit_j=0.0,
            calibration_candidate="false",
            notes="control remains Option A even with complete telemetry",
        ),
    ]


def build_invalid() -> list[dict[str, object]]:
    cases = [
        ("invalid-missing-power-interval", {"power_interval_start_ms": "", "power_interval_end_ms": ""}),
        ("invalid-missing-tier-bytes", {"bytes_moved": "", "source_tier": ""}),
        ("invalid-missing-label", {"workload_class": "", "object_class": ""}),
        ("invalid-missing-topology-tenant", {"hardware_topology_id": "", "tenant_count": ""}),
        ("invalid-unaligned-interval", {"power_interval_start_ms": 100, "power_interval_end_ms": 1100}),
        ("invalid-below-noise", {"joules_measured": 3.0, "energy_noise_floor_j": 5.0}),
        (
            "invalid-security-positive-credit",
            {
                "security_allowed": "false",
                "reuse_decision": "denied_reuse",
                "claimed_reuse_credit": 9.0,
                "claimed_energy_credit_j": 45.0,
            },
        ),
        (
            "invalid-host-proxy-mislabeled",
            {
                "evidence_label": "host_local_proxy",
                "production_target_id": "local-host",
                "topology_scope": "host_local_proxy",
            },
        ),
    ]
    return [
        base_row(
            fixture_id=fixture_id,
            fixture_class="invalid",
            notes=fixture_id.replace("invalid-", "").replace("-", " "),
            **overrides,
        )
        for fixture_id, overrides in cases
    ]


def main() -> None:
    write_csv(SCHEMA_OUT, build_schema(), ["field_name", "required", "type", "gate"])
    write_csv(VALID_OUT, build_valid(), FIELDS)
    write_csv(INVALID_OUT, build_invalid(), FIELDS)


if __name__ == "__main__":
    main()
