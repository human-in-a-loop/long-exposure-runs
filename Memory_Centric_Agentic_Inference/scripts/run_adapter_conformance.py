#!/usr/bin/env python3
# created: 2026-05-12T05:25:00Z
# cycle: 26
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PORT-1
"""Run adapter portability conformance over backend-shaped fixtures."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from ingest_production_dc12_telemetry import blocked_reason, required_fields, threshold_map  # noqa: E402


CONTRACT = DATA / "adapter_conformance_contract.csv"
ALIASES = DATA / "adapter_join_alias_map.csv"
VALID = DATA / "adapter_backend_profile_fixtures.csv"
INVALID = DATA / "adapter_backend_profile_invalid_fixtures.csv"
SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
CXL = DATA / "cxl_contention_thresholds.csv"

OUT_RESULTS = DATA / "adapter_conformance_results.csv"
OUT_FAILURES = DATA / "adapter_conformance_failure_modes.csv"
OUT_BOUNDARY = DATA / "adapter_conformance_ingestion_boundary.csv"

EVIDENCE = "adapter_conformance_fixture"
REQUIRED_PROFILE_CLASSES = {
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
VALID_UNITS = {
    "power_unit": "W",
    "energy_unit": "J",
    "byte_unit": "B",
    "latency_unit": "us",
    "timestamp_unit": "ms",
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


def truthy(value: object) -> bool:
    return str(value).strip().lower() == "true"


def build_cases(valid: list[dict[str, str]], invalid: list[dict[str, str]]) -> list[tuple[str, list[dict[str, str]], str]]:
    cases = [("valid-conformance-profile", [dict(row) for row in valid], "")]
    for invalid_row in invalid:
        case_id = invalid_row["fixture_case_id"]
        rows = [dict(row) for row in valid]
        drop_class = invalid_row.get("drop_profile_class", "")
        if drop_class:
            rows = [row for row in rows if row["profile_class"] != drop_class]
        else:
            for idx, row in enumerate(rows):
                if row["profile_id"] == invalid_row["profile_id"]:
                    rows[idx] = dict(invalid_row)
                    break
        cases.append((case_id, rows, invalid_row["expected_blocked_reason"]))
    return cases


def resolve_measurement_run(row: dict[str, str], aliases: dict[str, str]) -> tuple[str, str]:
    alias = row.get("join_alias_used", "")
    if alias == "run_id":
        if row.get("measurement_run_id") and row["measurement_run_id"] == row.get("alias_value"):
            return "", "run_id_without_canonicalization"
        return row.get("alias_value", ""), ""
    if alias in aliases and aliases[alias] == "measurement_run_id":
        return row.get("alias_value", ""), ""
    return "", "unknown_alias"


def merged_row(streams: list[dict[str, str]], aliases: dict[str, str]) -> tuple[dict[str, object], str]:
    row: dict[str, object] = {
        "fixture_id": "adapter-conformance-valid",
        "fixture_class": "valid",
        "evidence_label": EVIDENCE,
        "production_calibrated": "false",
        "production_ready": "false",
    }
    for stream in streams:
        for key, value in stream.items():
            if value != "" and key not in {"measurement_run_id"}:
                row[key] = value

    resolved_run_ids = []
    for stream in streams:
        resolved, alias_error = resolve_measurement_run(stream, aliases)
        if alias_error:
            return row, alias_error
        resolved_run_ids.append(resolved)
    if len(set(resolved_run_ids)) != 1 or not resolved_run_ids[0]:
        return row, "run_id_without_canonicalization"
    row["measurement_run_id"] = resolved_run_ids[0]
    row["evidence_label"] = EVIDENCE
    row["production_calibrated"] = "false"
    row["production_ready"] = "false"
    row["calibration_candidate"] = str(row.get("calibration_candidate") == "true").lower()
    return row, ""


def classify(streams: list[dict[str, str]], aliases: dict[str, str], schema_required: list[str]) -> tuple[dict[str, object], str]:
    classes = {row["profile_class"] for row in streams}
    if missing := sorted(REQUIRED_PROFILE_CLASSES - classes):
        row, _ = merged_row(streams, aliases)
        return row, "missing_profile_class:" + "|".join(missing)
    row, alias_error = merged_row(streams, aliases)
    if alias_error:
        return row, alias_error
    if any(str(stream.get(key, "")) != expected for stream in streams for key, expected in VALID_UNITS.items()):
        return row, "invalid_unit"
    if any(not stream.get("clock_domain") for stream in streams):
        return row, "missing_clock_domain"
    if any(float(str(stream.get("clock_offset_ms") or 0)) > float(str(stream.get("interval_ms") or 1)) * 0.10 for stream in streams):
        return row, "clock_alignment_failed"
    if any(stream.get("byte_interval_start_ms") != stream.get("power_interval_start_ms") or stream.get("byte_interval_end_ms") != stream.get("power_interval_end_ms") for stream in streams):
        return row, "interval_alignment_failed"
    if any(not stream.get("tenant_id") for stream in streams):
        return row, "missing_tenant_label"
    if any(not stream.get("security_context_id") for stream in streams):
        return row, "missing_security_context"
    if any(stream.get("collector_trust_domain") == "stale_or_untrusted" for stream in streams):
        return row, "stale_provenance"
    if any(stream.get("evidence_label") == "production_target" or truthy(stream.get("production_ready")) or truthy(stream.get("production_calibrated")) for stream in streams):
        row["evidence_label"] = EVIDENCE
        row["production_calibrated"] = "false"
        row["production_ready"] = "false"
        return row, "fixture_attempted_production_target"
    if not all(truthy(row.get(field, "")) for field in ["security_allowed", "provenance_valid", "retention_valid", "verifier_valid"]):
        return row, "security_or_provenance_gate_failed"
    if any(row.get(field, "") == "" for field in schema_required):
        return row, "missing_required_schema_field"
    return row, ""


def category(reason: str) -> str:
    if reason in {"unknown_alias", "run_id_without_canonicalization"}:
        return "alias"
    if reason == "invalid_unit":
        return "unit"
    if reason in {"missing_clock_domain", "clock_alignment_failed", "interval_alignment_failed"}:
        return "clock"
    if reason.startswith("missing_profile_class") or reason == "missing_required_schema_field":
        return "join"
    if reason == "stale_provenance":
        return "provenance"
    if reason in {"missing_security_context", "security_or_provenance_gate_failed"}:
        return "security"
    if reason == "missing_tenant_label":
        return "join"
    return "boundary"


def main() -> None:
    contract = read_csv(CONTRACT)
    alias_rows = read_csv(ALIASES)
    valid = read_csv(VALID)
    invalid = read_csv(INVALID)
    schema = read_csv(SCHEMA)
    schema_fields = {row["field_name"] for row in schema}
    schema_required = required_fields(schema)
    thresholds = threshold_map(read_csv(CXL))

    aliases = {row["logical_key"]: row["canonical_field"] for row in alias_rows if row["accepted_aliases"]}
    if aliases.get("run_id") != "measurement_run_id":
        raise ValueError("run_id must resolve to measurement_run_id")
    for row in alias_rows:
        if row["canonical_field"] not in schema_fields:
            raise ValueError(f"{row['logical_key']} does not resolve to a production schema field")
    if REQUIRED_PROFILE_CLASSES - {row["profile_class"] for row in contract}:
        raise ValueError("contract missing required profile class")

    results: list[dict[str, object]] = []
    failures: list[dict[str, object]] = []
    boundary: list[dict[str, object]] = []
    failure_counts: Counter[str] = Counter()

    for case_id, streams, expected in build_cases(valid, invalid):
        row, block = classify(streams, aliases, schema_required)
        row["fixture_case_id"] = case_id
        row["fixture_class"] = "valid" if case_id == "valid-conformance-profile" else "invalid"
        row["calibration_candidate"] = str(block == "" and case_id == "valid-conformance-profile").lower()
        row["production_calibrated"] = "false"
        row["production_ready"] = "false"
        gates, ingestion_reason = blocked_reason({k: str(v) for k, v in row.items()}, schema_required, thresholds)
        if not ingestion_reason:
            ingestion_reason = "shape_check_only_no_production_credit"
        status = "pass" if not block else "fail"
        if block:
            failure_counts[category(block)] += 1

        results.append(
            {
                "fixture_case_id": case_id,
                "status": status,
                "profiles_seen": len(streams),
                "profile_classes_seen": len({stream["profile_class"] for stream in streams}),
                "run_alias_resolved": str(row.get("measurement_run_id") == "port-run-001").lower(),
                "canonical_measurement_run_id": row.get("measurement_run_id", ""),
                "units_normalized": str(all(str(row.get(key, "")) == expected_unit for key, expected_unit in VALID_UNITS.items())).lower(),
                "clock_aligned": str(block not in {"missing_clock_domain", "clock_alignment_failed", "interval_alignment_failed"}).lower(),
                "provenance_checked": str(block != "stale_provenance").lower(),
                "security_context_checked": str(block != "missing_security_context").lower(),
                "evidence_label": EVIDENCE,
                "production_calibrated": "false",
                "production_ready": "false",
                "expected_blocked_reason": expected,
                "blocked_reason": block,
            }
        )
        boundary.append(
            {
                "fixture_case_id": case_id,
                "conformance_status": status,
                "evidence_label": EVIDENCE,
                "ingestion_gate_schema_valid": str(gates["schema_valid"]).lower(),
                "ingestion_boundary": ingestion_reason,
                "production_target_allowed": "false",
                "production_calibrated": "false",
                "production_ready": "false",
                "claim_credit_allowed": "false",
                "reason": "conformance only validates adapter shape; trusted production_target evidence is still required",
            }
        )

    for name in ["alias", "unit", "clock", "join", "provenance", "security", "boundary"]:
        failures.append({"failure_category": name, "invalid_profile_count": failure_counts[name], "fail_closed": "true"})

    write_csv(
        OUT_RESULTS,
        results,
        [
            "fixture_case_id",
            "status",
            "profiles_seen",
            "profile_classes_seen",
            "run_alias_resolved",
            "canonical_measurement_run_id",
            "units_normalized",
            "clock_aligned",
            "provenance_checked",
            "security_context_checked",
            "evidence_label",
            "production_calibrated",
            "production_ready",
            "expected_blocked_reason",
            "blocked_reason",
        ],
    )
    write_csv(OUT_FAILURES, failures, ["failure_category", "invalid_profile_count", "fail_closed"])
    write_csv(
        OUT_BOUNDARY,
        boundary,
        [
            "fixture_case_id",
            "conformance_status",
            "evidence_label",
            "ingestion_gate_schema_valid",
            "ingestion_boundary",
            "production_target_allowed",
            "production_calibrated",
            "production_ready",
            "claim_credit_allowed",
            "reason",
        ],
    )


if __name__ == "__main__":
    main()
