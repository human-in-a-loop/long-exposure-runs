#!/usr/bin/env python3
# created: 2026-05-12T00:02:00Z
# cycle: 19
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-DC12-1
"""Verify M-DC12-1 local proxy calibration artifacts."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

OPTION_A = "A_conventional_request_model_kv_serving"
CONTROL_WORKLOADS = {
    "single-turn chat control",
    "batch summarization/offline inference control",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path} is empty"
    return rows


def assert_fields(rows: list[dict[str, str]], fields: set[str], name: str) -> None:
    assert fields <= set(rows[0]), f"{name} missing {fields - set(rows[0])}"


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path} is not a PNG"
    assert len(data) > 10_000, f"{path} is too small to be a useful figure"


def fnum(row: dict[str, str], key: str) -> float:
    return float(row.get(key, "") or 0.0)


def main() -> None:
    metadata = read_csv(DATA / "dc12_local_bench_metadata.csv")
    byte_rows = read_csv(DATA / "dc12_byte_movement_measurements.csv")
    contention = read_csv(DATA / "dc12_contention_measurements.csv")
    overlay = read_csv(DATA / "dc12_proxy_threshold_overlay.csv")
    claims = read_csv(DATA / "dc12_claim_update_matrix.csv")
    missing = read_csv(DATA / "dc12_missing_production_telemetry.csv")

    assert_fields(metadata, {"measurement_id", "metadata_key", "metadata_value", "evidence_label"}, "metadata")
    assert_fields(
        byte_rows,
        {
            "measurement_id",
            "access_pattern",
            "buffer_size_bytes",
            "bytes_touched",
            "throughput_mb_s",
            "latency_p95_us",
            "power_source",
            "evidence_label",
        },
        "byte measurements",
    )
    assert_fields(
        contention,
        {
            "measurement_id",
            "worker_count",
            "latency_p50_us",
            "latency_p95_us",
            "latency_p99_us",
            "contention_proxy_p95_over_1w",
            "contention_proxy_p99_over_1w",
            "evidence_label",
        },
        "contention measurements",
    )
    assert_fields(
        overlay,
        {
            "constant_id",
            "source_threshold_id",
            "workload_class",
            "proxy_measurement_id",
            "threshold_crossed",
            "option_after_proxy",
            "production_calibrated",
            "evidence_label",
        },
        "threshold overlay",
    )

    assert len({row["buffer_size_bytes"] for row in byte_rows}) >= 3
    assert len({row["worker_count"] for row in contention}) >= 3
    assert {row["constant_id"] for row in overlay} >= {"DC-001", "DC-002"}
    assert any(row["source_threshold_id"] == "DC001-BYTE-ENERGY-001" for row in overlay)
    assert any(row["source_threshold_id"].startswith("DC002-") for row in overlay)

    for row in overlay:
        assert row["production_calibrated"] == "false", row
        if row["workload_class"] in CONTROL_WORKLOADS:
            assert row["option_after_proxy"] == OPTION_A, row

    cl012 = next(row for row in claims if row["claim_id"] == "CL-012")
    assert cl012["production_calibrated"] == "false", cl012
    assert cl012["update_status"] in {"proxy_only", "speculative"}, cl012

    security_claim = next(row for row in claims if row["claim_id"] == "SECURITY-GATE-ENERGY-001")
    assert "denied_safe_reuse_credit=0" in security_claim["basis"], security_claim

    dc002 = [row for row in overlay if row["constant_id"] == "DC-002"]
    assert any(row["threshold_crossed"] == "true" for row in dc002) or any(
        row["claim_effect"] == "proxy_contention_does_not_cross_existing_threshold" for row in dc002
    ), "high contention must either cross or explicitly report non-crossing"

    original_energy = read_csv(DATA / "energy_architecture_sensitivity.csv")
    original_plan = read_csv(DATA / "memory_plan_constraint_sensitivity.csv")
    assert all(row["evidence_label"] == "synthetic_sensitivity" for row in original_energy)
    assert all(row["evidence_label"] == "synthetic_planning" for row in original_plan)
    assert all(row["production_calibrated"] == "false" for row in claims)

    required_missing = {
        "accelerator_power_counters",
        "tier_specific_bytes",
        "cxl_pooled_memory_latency",
        "tenant_concurrency",
        "workload_object_labels",
    }
    assert required_missing <= {row["telemetry_id"] for row in missing}

    for fig in [
        DATA / "dc12_byte_movement_proxy.png",
        DATA / "dc12_contention_latency_proxy.png",
        DATA / "dc12_threshold_overlay.png",
    ]:
        assert_png_nonblank(fig)

    assert all(fnum(row, "throughput_mb_s") > 0 for row in byte_rows)
    assert all(fnum(row, "latency_p99_us") >= fnum(row, "latency_p50_us") for row in contention)

    print("verify_dc12_proxy_calibration: ok")


if __name__ == "__main__":
    main()
