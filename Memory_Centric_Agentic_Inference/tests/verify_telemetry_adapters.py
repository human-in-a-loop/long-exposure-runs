#!/usr/bin/env python3
# created: 2026-05-12T04:35:00Z
# cycle: 25
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ADAPTER-1

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
    "missing_stream_class",
    "missing_join_key",
    "clock_alignment_failed",
    "stale_security_context",
    "untrusted_collector_provenance",
    "fixture_attempted_production_target",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def split_fields(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "production_dc12_telemetry_schema.csv")
    interface = read_csv(DATA / "telemetry_adapter_interface.csv")
    fixture_streams = read_csv(DATA / "telemetry_adapter_fixture_streams.csv")
    invalid_streams = read_csv(DATA / "telemetry_adapter_invalid_streams.csv")
    normalized = read_csv(DATA / "telemetry_adapter_normalized_rows.csv")
    join_results = read_csv(DATA / "telemetry_adapter_join_results.csv")
    preflight = read_csv(DATA / "telemetry_adapter_preflight_results.csv")
    boundary = read_csv(DATA / "telemetry_adapter_claim_boundary.csv")

    assert REQUIRED_STREAMS <= {row["collector_category"] for row in interface}
    assert REQUIRED_STREAMS <= {row["collector_category"] for row in fixture_streams}
    assert len(invalid_streams) >= 6

    required_schema = {row["field_name"] for row in schema if row["required"] == "true"}
    covered: set[str] = set()
    for row in interface:
        covered |= split_fields(row["emitted_schema_fields"])
        covered |= {field.split("=")[0].strip() for field in split_fields(row["derived_schema_fields"])}
        assert row["evidence_label_allowed"] == "synthetic_adapter_fixture"
        assert row["production_target_allowed"] == "false"
        assert row["fail_closed_policy"]
    assert not (required_schema - covered), sorted(required_schema - covered)

    valid = next(row for row in normalized if row["fixture_case_id"] == "valid-adapter-candidate")
    assert valid["calibration_candidate"] == "true"
    assert valid["blocked_reason"] == ""
    assert valid["evidence_label"] == "synthetic_adapter_fixture"

    invalid_rows = [row for row in normalized if row["fixture_class"] == "invalid"]
    assert invalid_rows
    assert all(row["blocked_reason"] for row in invalid_rows)
    observed_blocks = {row["blocked_reason"].split(":")[0] for row in invalid_rows}
    assert EXPECTED_BLOCKS <= observed_blocks, observed_blocks

    assert all(row["evidence_label"] == "synthetic_adapter_fixture" for row in normalized)
    assert all(row["production_calibrated"] == "false" for row in normalized)
    assert all(row["production_ready"] == "false" for row in normalized)
    assert all(row["evidence_label"] != "production_target" for row in normalized)

    invalid_join = [row for row in join_results if row["join_valid"] == "false"]
    assert invalid_join and all(row["blocked_reason"] for row in invalid_join)
    assert any(row["blocked_reason"].startswith("missing_join_key") for row in invalid_join)
    assert any(row["blocked_reason"] == "clock_alignment_failed" for row in invalid_join)
    assert any(row["blocked_reason"] == "stale_security_context" for row in invalid_join)

    blocked_preflight = [row for row in preflight if row["passed"] == "false"]
    assert blocked_preflight
    assert all(row["blocks_calibration"] == "true" for row in blocked_preflight)
    assert all(row["blocked_reason"] for row in blocked_preflight)

    assert all(row["input_evidence_label"] == "synthetic_adapter_fixture" for row in boundary)
    assert all(row["production_target_allowed"] == "false" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)

    # Existing M-PRODTELEM-1 ingestion gate must reject direct adapter evidence
    # as non-production evidence. This proves fixtures cannot masquerade as
    # production_target rows through the current ingestion harness.
    req_fields = required_fields(schema)
    thresholds = threshold_map(read_csv(DATA / "cxl_contention_thresholds.csv"))
    gates, reason = blocked_reason(valid, req_fields, thresholds)
    assert gates["schema_valid"], gates
    assert reason == "not_production_evidence_label", reason

    for fig in [
        DATA / "telemetry_adapter_stream_coverage.png",
        DATA / "telemetry_adapter_join_failures.png",
        DATA / "telemetry_adapter_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: telemetry adapter interface verified.")


if __name__ == "__main__":
    main()
