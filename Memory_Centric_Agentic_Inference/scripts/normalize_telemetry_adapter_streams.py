#!/usr/bin/env python3
# created: 2026-05-12T04:25:00Z
# cycle: 25
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-ADAPTER-1
"""Normalize offline telemetry adapter streams into schema-shaped candidates."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INTERFACE = DATA / "telemetry_adapter_interface.csv"
STREAMS = DATA / "telemetry_adapter_fixture_streams.csv"
INVALID = DATA / "telemetry_adapter_invalid_streams.csv"
SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
JOIN = DATA / "production_telemetry_join_contract.csv"
PREFLIGHT = DATA / "production_telemetry_preflight_checks.csv"

OUT_ROWS = DATA / "telemetry_adapter_normalized_rows.csv"
OUT_JOIN = DATA / "telemetry_adapter_join_results.csv"
OUT_PREFLIGHT = DATA / "telemetry_adapter_preflight_results.csv"
OUT_BOUNDARY = DATA / "telemetry_adapter_claim_boundary.csv"

EVIDENCE = "synthetic_adapter_fixture"
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
JOIN_KEYS = ["measurement_run_id", "interval_id", "workload_id", "object_id", "topology_id", "tenant_id", "security_context_id"]


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


def truthy(value: object) -> bool:
    return str(value).strip().lower() == "true"


def schema_fields() -> tuple[list[str], list[str]]:
    rows = read_csv(SCHEMA)
    all_fields = [row["field_name"] for row in rows]
    required = [row["field_name"] for row in rows if row["required"] == "true"]
    return all_fields, required


def case_streams(valid: list[dict[str, str]], invalid_row: dict[str, str] | None = None) -> tuple[str, list[dict[str, str]], str]:
    streams = [dict(row) for row in valid]
    if invalid_row is None:
        return "valid-adapter-candidate", streams, ""

    case_id = invalid_row["fixture_case_id"]
    expected = invalid_row.get("expected_blocked_reason", "")
    if expected == "missing_stream_class":
        drop = invalid_row.get("drop_stream_id", "tier-bytes")
        streams = [row for row in streams if row["stream_id"] != drop]
    else:
        for idx, row in enumerate(streams):
            if row["stream_id"] == invalid_row["stream_id"]:
                patched = dict(row)
                for key, value in invalid_row.items():
                    if value != "":
                        patched[key] = value
                    elif key in {"interval_id", "security_context_id"}:
                        patched[key] = ""
                patched["fixture_case_id"] = case_id
                patched["fixture_class"] = "invalid"
                streams[idx] = patched
                break
    return case_id, streams, expected


def merge_payload(streams: list[dict[str, str]], fields: list[str]) -> dict[str, object]:
    row = {field: "" for field in fields}
    for stream in streams:
        for key, value in stream.items():
            if key in row and value != "":
                row[key] = value
    row["fixture_id"] = row.get("fixture_id") or "adapter-valid-candidate"
    row["fixture_class"] = "valid" if all(s.get("fixture_class") == "valid" for s in streams) else "invalid"
    row["evidence_label"] = row.get("evidence_label") or EVIDENCE
    row["production_target_id"] = row.get("production_target_id") or "synthetic-adapter-target"
    row["calibration_candidate"] = str(row.get("calibration_candidate") == "true").lower()
    row["production_calibrated"] = "false"
    row["production_ready"] = "false"
    return row


def classify_block(streams: list[dict[str, str]], required_fields: list[str]) -> str:
    categories = {row["collector_category"] for row in streams}
    if missing := sorted(REQUIRED_STREAMS - categories):
        return "missing_stream_class:" + "|".join(missing)
    if any(row.get("collector_trust_domain") == "unknown_untrusted" for row in streams):
        return "untrusted_collector_provenance"
    if any(row.get("evidence_label") == "production_target" and row.get("is_fixture") == "true" for row in streams):
        return "fixture_attempted_production_target"
    for key in JOIN_KEYS:
        values = {row.get(key, "") for row in streams}
        if "" in values:
            return f"missing_join_key:{key}"
        if len(values) > 1:
            return f"inconsistent_join_key:{key}"
    if any(float(row.get("clock_offset_ms") or 0) > 100 for row in streams):
        return "clock_alignment_failed"
    merged = merge_payload(streams, required_fields)
    if merged.get("power_interval_start_ms") != merged.get("byte_interval_start_ms") or merged.get("power_interval_end_ms") != merged.get("byte_interval_end_ms"):
        return "clock_alignment_failed"
    security_fresh_until = min(float(row.get("security_context_fresh_until_ms") or 999999) for row in streams)
    interval_end = max(float(row.get("interval_end_ms") or 0) for row in streams)
    if security_fresh_until < interval_end:
        return "stale_security_context"
    if any(merged.get(field, "") == "" for field in required_fields):
        return "missing_required_schema_field"
    if not all(truthy(merged.get(field, "")) for field in ["security_allowed", "provenance_valid", "retention_valid", "verifier_valid"]):
        return "security_or_provenance_gate_failed"
    return ""


def main() -> None:
    interface = read_csv(INTERFACE)
    valid = read_csv(STREAMS)
    invalid = read_csv(INVALID)
    all_schema_fields, required = schema_fields()
    read_csv(JOIN)
    preflight_checks = read_csv(PREFLIGHT)

    interface_categories = {row["collector_category"] for row in interface}
    if not REQUIRED_STREAMS <= interface_categories:
        raise ValueError(f"adapter interface missing {sorted(REQUIRED_STREAMS - interface_categories)}")

    normalized_rows: list[dict[str, object]] = []
    join_results: list[dict[str, object]] = []
    preflight_results: list[dict[str, object]] = []

    cases = [case_streams(valid)] + [case_streams(valid, row) for row in invalid]
    for case_id, streams, expected in cases:
        block = classify_block(streams, all_schema_fields)
        merged = merge_payload(streams, all_schema_fields)
        merged["fixture_id"] = case_id
        merged["fixture_case_id"] = case_id
        merged["fixture_class"] = "valid" if case_id == "valid-adapter-candidate" else "invalid"
        merged["evidence_label"] = EVIDENCE
        merged["calibration_candidate"] = str(block == "" and case_id == "valid-adapter-candidate").lower()
        merged["production_calibrated"] = "false"
        merged["production_ready"] = "false"
        merged["blocked_reason"] = block
        normalized_rows.append(merged)

        join_results.append(
            {
                "fixture_case_id": case_id,
                "streams_seen": len(streams),
                "required_streams_seen": len(REQUIRED_STREAMS & {row["collector_category"] for row in streams}),
                "join_keys_present": str(all(all(row.get(key, "") for row in streams) for key in JOIN_KEYS)).lower(),
                "clock_aligned": str(block not in {"clock_alignment_failed"}).lower(),
                "evidence_label": EVIDENCE,
                "join_valid": str(block == "").lower(),
                "expected_blocked_reason": expected,
                "blocked_reason": block,
            }
        )
        for check in preflight_checks:
            passed = block == ""
            preflight_results.append(
                {
                    "fixture_case_id": case_id,
                    "check_id": check["check_id"],
                    "collector_category": check["collector_category"],
                    "passed": str(passed).lower(),
                    "blocks_calibration": check["blocks_calibration"],
                    "fail_closed_consequence": "adapter row rejected before production ingestion" if not passed else "synthetic candidate only",
                    "blocked_reason": "" if passed else block,
                }
            )

    boundary_rows = [
        {
            "boundary_id": "adapter-fixture-evidence",
            "input_evidence_label": EVIDENCE,
            "allowed_ingestion_use": "schema_normalization_test_only",
            "production_target_allowed": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "reason": "offline fixtures do not establish trusted real deployment provenance",
        },
        {
            "boundary_id": "valid-normalized-candidate",
            "input_evidence_label": EVIDENCE,
            "allowed_ingestion_use": "may be translated only to synthetic_production_fixture for existing ingestion-harness dry runs",
            "production_target_allowed": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "reason": "M-PRODTELEM-1 production_target requires trusted real collector source and joined deployment provenance",
        },
        {
            "boundary_id": "invalid-adapter-streams",
            "input_evidence_label": EVIDENCE,
            "allowed_ingestion_use": "rejected_before_ingestion",
            "production_target_allowed": "false",
            "production_calibrated": "false",
            "production_ready": "false",
            "reason": "missing streams, clocks, join keys, stale security, or untrusted provenance fail closed",
        },
    ]

    write_csv(OUT_ROWS, normalized_rows, all_schema_fields + ["fixture_case_id", "production_calibrated", "production_ready", "blocked_reason"])
    write_csv(
        OUT_JOIN,
        join_results,
        ["fixture_case_id", "streams_seen", "required_streams_seen", "join_keys_present", "clock_aligned", "evidence_label", "join_valid", "expected_blocked_reason", "blocked_reason"],
    )
    write_csv(
        OUT_PREFLIGHT,
        preflight_results,
        ["fixture_case_id", "check_id", "collector_category", "passed", "blocks_calibration", "fail_closed_consequence", "blocked_reason"],
    )
    write_csv(
        OUT_BOUNDARY,
        boundary_rows,
        ["boundary_id", "input_evidence_label", "allowed_ingestion_use", "production_target_allowed", "production_calibrated", "production_ready", "reason"],
    )


if __name__ == "__main__":
    main()
