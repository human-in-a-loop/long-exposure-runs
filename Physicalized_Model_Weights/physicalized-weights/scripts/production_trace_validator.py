# created: 2026-05-13T08:42:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-TRACE-1
"""Validate production serving traces for safety/filter reopen evidence."""

from __future__ import annotations

import csv
import json
import math
import sys
import zlib
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"

SCHEMA_JSON = DATA_DIR / "production_trace_schema.json"
SUMMARY_JSON = DATA_DIR / "production_trace_validation_summary.json"
REPORT_CSV = DATA_DIR / "production_trace_validation_report.csv"
COVERAGE_PNG = DATA_DIR / "production_trace_evidence_coverage.png"

STATUS_PRIORITY = [
    "invalid_privacy_risk",
    "invalid_missing_baseline",
    "invalid_units",
    "invalid_schema",
    "invalid_inconsistent_policy",
    "valid_but_insufficient",
    "valid_reopen_candidate",
]
BOOL_TRUE = {"true", "1", "yes"}
BOOL_FALSE = {"false", "0", "no"}
LATENCY_FIELDS = [
    "feature_extract_latency_ns",
    "route_latency_ns",
    "audit_latency_ns",
    "software_baseline_latency_ns",
    "accelerator_baseline_latency_ns",
    "hybrid_fast_path_latency_ns",
]
ENERGY_FIELDS = ["accelerator_energy_proxy_or_measured_pj", "hybrid_energy_proxy_or_measured_pj"]


def load_schema() -> dict[str, object]:
    return json.loads(SCHEMA_JSON.read_text())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def parse_bool(value: str) -> bool | None:
    lowered = value.strip().lower()
    if lowered in BOOL_TRUE:
        return True
    if lowered in BOOL_FALSE:
        return False
    return None


def parse_float(value: str) -> float:
    if value == "":
        return math.nan
    return float(value)


def percentile(values: list[float], q: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


def fmt(value: float) -> str:
    return "" if math.isnan(value) else f"{value:.3f}"


def add_issue(issues: list[dict[str, str]], status: str, field: str, message: str) -> None:
    issues.append({"status": status, "field": field, "message": message})


def choose_status(issues: list[dict[str, str]], reopen_candidate: bool) -> str:
    if not issues:
        return "valid_reopen_candidate" if reopen_candidate else "valid_but_insufficient"
    present = {issue["status"] for issue in issues}
    for status in STATUS_PRIORITY:
        if status in present:
            return status
    return "invalid_schema"


def validate_field(row: dict[str, str], column: dict[str, object], row_num: int, issues: list[dict[str, str]]) -> None:
    name = str(column["name"])
    raw = row.get(name, "")
    if raw == "":
        status = "invalid_missing_baseline" if "baseline" in name else "invalid_schema"
        add_issue(issues, status, name, f"row {row_num}: required value is missing")
        return
    kind = column["type"]
    try:
        if kind == "integer":
            value = int(raw)
            if "min" in column and value < int(column["min"]):
                add_issue(issues, "invalid_units", name, f"row {row_num}: value below minimum")
        elif kind == "float":
            value = float(raw)
            if "min_exclusive" in column and value <= float(column["min_exclusive"]):
                add_issue(issues, "invalid_units", name, f"row {row_num}: value must be positive")
            if "min" in column and value < float(column["min"]):
                add_issue(issues, "invalid_units", name, f"row {row_num}: value below minimum")
            if "max" in column and value > float(column["max"]):
                add_issue(issues, "invalid_units", name, f"row {row_num}: value above maximum")
        elif kind == "boolean":
            if parse_bool(raw) is None:
                add_issue(issues, "invalid_schema", name, f"row {row_num}: invalid boolean")
        elif kind == "category":
            if raw not in column["allowed"]:
                add_issue(issues, "invalid_schema", name, f"row {row_num}: invalid category {raw}")
        elif kind == "string":
            pattern = column.get("pattern")
            if pattern and not raw.startswith(str(pattern)):
                add_issue(issues, "invalid_schema", name, f"row {row_num}: value must start with {pattern}")
    except ValueError:
        status = "invalid_units" if kind in {"integer", "float"} else "invalid_schema"
        add_issue(issues, status, name, f"row {row_num}: cannot parse {kind}")


def validate_trace(path: Path, schema: dict[str, object]) -> dict[str, object]:
    fieldnames, rows = read_csv(path)
    columns = list(schema["columns"])
    required = [str(column["name"]) for column in columns if column["required"]]
    issues: list[dict[str, str]] = []

    disallowed = {name.lower() for name in schema["privacy_disallowed_columns"]}
    for field in fieldnames:
        lowered = field.lower()
        if lowered in disallowed or lowered.startswith("raw_"):
            add_issue(issues, "invalid_privacy_risk", field, "raw or sensitive column is not allowed")

    missing = [name for name in required if name not in fieldnames]
    for name in missing:
        status = "invalid_missing_baseline" if "baseline" in name else "invalid_schema"
        add_issue(issues, status, name, "required column is missing")

    known_columns = {str(column["name"]): column for column in columns}
    for row_num, row in enumerate(rows, start=2):
        for name, column in known_columns.items():
            if name in fieldnames:
                validate_field(row, column, row_num, issues)

    by_scenario: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_scenario[row.get("scenario_id", "")].append(row)
    for scenario_id, scenario_rows in by_scenario.items():
        previous_ts = -1
        policies = set()
        has_update = False
        for row_num, row in enumerate(scenario_rows, start=2):
            try:
                timestamp = int(row.get("timestamp_ns", ""))
                if timestamp < previous_ts:
                    add_issue(issues, "invalid_schema", "timestamp_ns", f"{scenario_id}: timestamps are not monotonic")
                previous_ts = timestamp
            except ValueError:
                pass
            policies.add(row.get("policy_version_hash", ""))
            has_update = has_update or parse_bool(row.get("update_event", "")) is True or parse_bool(row.get("rollback_event", "")) is True
            if row.get("route_decision") == "physicalized_fast_path":
                gate_values = {
                    "fallback_taken": parse_bool(row.get("fallback_taken", "")),
                    "audit_logged": parse_bool(row.get("audit_logged", "")),
                    "health_gate_passed": parse_bool(row.get("health_gate_passed", "")),
                    "drift_gate_passed": parse_bool(row.get("drift_gate_passed", "")),
                }
                if gate_values["fallback_taken"] is True or gate_values["audit_logged"] is not True or gate_values["health_gate_passed"] is not True or gate_values["drift_gate_passed"] is not True:
                    add_issue(issues, "invalid_schema", "route_decision", f"row {row_num}: physicalized fast path requires fallback=false, audit logged, and passing health/drift gates")
        if len(policies) > 1 and not has_update:
            add_issue(issues, "invalid_inconsistent_policy", "policy_version_hash", f"{scenario_id}: mixed policy versions without update or rollback")

    requests = len(rows)
    accepted_fast_path = sum(
        1
        for row in rows
        if row.get("route_decision") == "physicalized_fast_path"
        and parse_bool(row.get("fallback_taken", "")) is False
        and parse_bool(row.get("audit_logged", "")) is True
        and parse_bool(row.get("health_gate_passed", "")) is True
        and parse_bool(row.get("drift_gate_passed", "")) is True
    )
    fallback_count = sum(1 for row in rows if parse_bool(row.get("fallback_taken", "")) is True)
    near_count = sum(1 for row in rows if parse_bool(row.get("near_threshold", "")) is True)
    audit_count = sum(1 for row in rows if parse_bool(row.get("audit_logged", "")) is True)
    health_fail = sum(1 for row in rows if parse_bool(row.get("health_gate_passed", "")) is False)
    drift_fail = sum(1 for row in rows if parse_bool(row.get("drift_gate_passed", "")) is False)
    update_count = sum(1 for row in rows if parse_bool(row.get("update_event", "")) is True)
    rollback_count = sum(1 for row in rows if parse_bool(row.get("rollback_event", "")) is True)

    latency = {}
    for field in LATENCY_FIELDS:
        values = []
        for row in rows:
            try:
                value = parse_float(row.get(field, ""))
                if not math.isnan(value) and value >= 0:
                    values.append(value)
            except ValueError:
                pass
        latency[field] = {"median": percentile(values, 0.50), "p10": percentile(values, 0.10), "p90": percentile(values, 0.90)}

    accelerator_measured = sum(1 for row in rows if row.get("accelerator_energy_status") == "measured")
    hybrid_measured = sum(1 for row in rows if row.get("hybrid_energy_status") == "measured")
    accelerator_proxy = sum(1 for row in rows if row.get("accelerator_energy_status") == "proxy")
    hybrid_proxy = sum(1 for row in rows if row.get("hybrid_energy_status") == "proxy")
    measured_energy_coverage = min(accelerator_measured, hybrid_measured) / requests if requests else 0.0
    production_rows = sum(1 for row in rows if row.get("measurement_environment") in {"production", "shadow_production"})

    insufficient: list[str] = []
    if requests == 0:
        insufficient.append("zero_volume")
    if accepted_fast_path == 0:
        insufficient.append("zero_accepted_fast_path")
    if accelerator_measured != requests or hybrid_measured != requests:
        insufficient.append("measured_energy_required")
    if production_rows != requests:
        insufficient.append("production_or_shadow_environment_required")

    reopen_candidate = not insufficient and not issues
    status = choose_status(issues, reopen_candidate)
    if status == "valid_but_insufficient":
        issues.extend({"status": "valid_but_insufficient", "field": "reopen_eligibility", "message": reason} for reason in insufficient)

    return {
        "trace_file": str(path),
        "status": status,
        "requests": requests,
        "accepted_fast_path_requests": accepted_fast_path,
        "fallback_frequency": fallback_count / requests if requests else 0.0,
        "near_threshold_frequency": near_count / requests if requests else 0.0,
        "audit_logging_rate": audit_count / requests if requests else 0.0,
        "health_gate_failure_rate": health_fail / requests if requests else 0.0,
        "drift_gate_failure_rate": drift_fail / requests if requests else 0.0,
        "update_count": update_count,
        "rollback_count": rollback_count,
        "latency": latency,
        "energy_coverage": {
            "accelerator_measured_rows": accelerator_measured,
            "hybrid_measured_rows": hybrid_measured,
            "accelerator_proxy_rows": accelerator_proxy,
            "hybrid_proxy_rows": hybrid_proxy,
            "measured_energy_coverage": measured_energy_coverage,
        },
        "insufficient_reasons": insufficient,
        "issues": issues,
    }


def report_rows(results: list[dict[str, object]]) -> list[dict[str, str]]:
    rows = []
    for result in results:
        latency = result["latency"]
        rows.append(
            {
                "trace_file": str(result["trace_file"]),
                "status": str(result["status"]),
                "requests": str(result["requests"]),
                "accepted_fast_path_requests": str(result["accepted_fast_path_requests"]),
                "fallback_frequency": f"{float(result['fallback_frequency']):.6f}",
                "near_threshold_frequency": f"{float(result['near_threshold_frequency']):.6f}",
                "audit_logging_rate": f"{float(result['audit_logging_rate']):.6f}",
                "health_gate_failure_rate": f"{float(result['health_gate_failure_rate']):.6f}",
                "drift_gate_failure_rate": f"{float(result['drift_gate_failure_rate']):.6f}",
                "update_count": str(result["update_count"]),
                "rollback_count": str(result["rollback_count"]),
                "feature_extract_median_ns": fmt(latency["feature_extract_latency_ns"]["median"]),
                "route_median_ns": fmt(latency["route_latency_ns"]["median"]),
                "audit_median_ns": fmt(latency["audit_latency_ns"]["median"]),
                "software_baseline_median_ns": fmt(latency["software_baseline_latency_ns"]["median"]),
                "accelerator_baseline_median_ns": fmt(latency["accelerator_baseline_latency_ns"]["median"]),
                "hybrid_fast_path_median_ns": fmt(latency["hybrid_fast_path_latency_ns"]["median"]),
                "measured_energy_coverage": f"{result['energy_coverage']['measured_energy_coverage']:.6f}",
                "issue_count": str(len(result["issues"])),
                "issues": "|".join(f"{issue['status']}:{issue['field']}" for issue in result["issues"]),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "trace_file",
        "status",
        "requests",
        "accepted_fast_path_requests",
        "fallback_frequency",
        "near_threshold_frequency",
        "audit_logging_rate",
        "health_gate_failure_rate",
        "drift_gate_failure_rate",
        "update_count",
        "rollback_count",
        "feature_extract_median_ns",
        "route_median_ns",
        "audit_median_ns",
        "software_baseline_median_ns",
        "accelerator_baseline_median_ns",
        "hybrid_fast_path_median_ns",
        "measured_energy_coverage",
        "issue_count",
        "issues",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, results: list[dict[str, object]]) -> None:
    width, height = 900, 460
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "valid_measured": (56, 132, 87),
        "proxy_only": (213, 153, 62),
        "missing_baseline": (177, 80, 70),
        "privacy_schema_failures": (95, 107, 150),
    }
    rect(55, 40, 845, 410, (238, 240, 242))
    bar_w = 95
    gap = 28
    x = 95
    for result in results:
        requests = max(1, int(result["requests"]))
        measured = result["energy_coverage"]["measured_energy_coverage"]
        proxy = (result["energy_coverage"]["accelerator_proxy_rows"] + result["energy_coverage"]["hybrid_proxy_rows"]) / (2 * requests)
        missing_baseline = 1.0 if any(issue["status"] == "invalid_missing_baseline" for issue in result["issues"]) else 0.0
        privacy_schema = 1.0 if any(issue["status"] in {"invalid_privacy_risk", "invalid_schema", "invalid_units"} for issue in result["issues"]) else 0.0
        values = [measured, proxy, missing_baseline, privacy_schema]
        labels = ["valid_measured", "proxy_only", "missing_baseline", "privacy_schema_failures"]
        for value, label in zip(values, labels):
            h = int(280 * min(1.0, value))
            rect(x, 360 - h, x + bar_w, 360, colors[label])
            x += bar_w + 8
        x += gap
    for i, label in enumerate(colors):
        y = 20 + i * 20
        rect(650, y, 670, y + 12, colors[label])
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    import struct

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def build_summary(results: list[dict[str, object]], schema: dict[str, object]) -> dict[str, object]:
    counts = Counter(str(result["status"]) for result in results)
    issue_counts = Counter(issue["status"] for result in results for issue in result["issues"])
    return {
        "schema_version": schema["schema_version"],
        "milestone_id": "M-TRACE-1",
        "status": "validated",
        "trace_count": len(results),
        "status_counts": dict(sorted(counts.items())),
        "issue_status_counts": dict(sorted(issue_counts.items())),
        "reopen_candidates": [result["trace_file"] for result in results if result["status"] == "valid_reopen_candidate"],
        "privacy_guardrail": "raw prompts, raw user IDs, tenant identifiers, API keys, IPs, emails, and raw content columns are invalid",
        "energy_guardrail": "proxy energy cannot satisfy measured production-energy requirements",
        "interpretation": "Schema-valid traces are only reopen candidates when measured accelerator and hybrid evidence, baselines, audit fields, nonzero accepted fast-path volume, and consistent policy windows are present.",
        "traces": results,
    }


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        args = [str(DATA_DIR / "example_production_trace_valid.csv"), str(DATA_DIR / "example_production_trace_invalid.csv")]
    schema = load_schema()
    results = [validate_trace(Path(arg), schema) for arg in args]
    SUMMARY_JSON.write_text(json.dumps(build_summary(results, schema), indent=2, sort_keys=True) + "\n")
    write_csv(REPORT_CSV, report_rows(results))
    write_png(COVERAGE_PNG, results)
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {REPORT_CSV}")
    print(f"wrote {COVERAGE_PNG}")
    for result in results:
        print(f"{result['trace_file']}: {result['status']} ({len(result['issues'])} issues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
