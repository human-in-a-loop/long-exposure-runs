# created: 2026-05-13T10:24:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PIPELINE-1
"""Compose trace validation, ingestion admissibility, and reopen thresholds."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"
VALIDATOR_PATH = ROOT / "physicalized-weights" / "scripts" / "production_trace_validator.py"

TRACE_SCHEMA_JSON = DATA_DIR / "production_trace_schema.json"
REOPEN_THRESHOLDS_CSV = DATA_DIR / "reopen_thresholds.csv"
INGESTION_SCORES_CSV = DATA_DIR / "trace_ingestion_path_scores.csv"

FIXTURE_INVALID_PRIVACY = DATA_DIR / "pipeline_trace_invalid_privacy.csv"
FIXTURE_VALID_INSUFFICIENT = DATA_DIR / "pipeline_trace_valid_insufficient.csv"
FIXTURE_THRESHOLD_NOT_CROSSED = DATA_DIR / "pipeline_trace_threshold_evaluable_not_crossed.csv"
FIXTURE_COUNTERFACTUAL_CROSSED = DATA_DIR / "pipeline_trace_synthetic_counterfactual_crossed.csv"
RESULTS_CSV = DATA_DIR / "reopen_pipeline_results.csv"
SUMMARY_JSON = DATA_DIR / "reopen_pipeline_summary.json"
OUTPUT_PNG = DATA_DIR / "reopen_pipeline_decision_flow.png"
REPORT_MD = DOCS_DIR / "end_to_end_reopen_pipeline.md"

PROVENANCE_FIELDS = [
    "evidence_source_type",
    "ingestion_path_id",
    "measurement_status",
    "provenance_attestation",
]
SOURCE_TYPES_FOR_ACTUAL = {"production", "shadow_production", "canary_production"}


def load_validator():
    spec = importlib.util.spec_from_file_location("production_trace_validator", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["production_trace_validator"] = module
    spec.loader.exec_module(module)
    return module


validator = load_validator()


def load_schema() -> dict[str, object]:
    return json.loads(TRACE_SCHEMA_JSON.read_text())


def load_ingestion_scores() -> dict[str, dict[str, str]]:
    with INGESTION_SCORES_CSV.open(newline="") as f:
        return {row["path_id"]: row for row in csv.DictReader(f)}


def load_thresholds() -> dict[str, dict[str, str]]:
    with REOPEN_THRESHOLDS_CSV.open(newline="") as f:
        return {row["scenario_id"]: row for row in csv.DictReader(f)}


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def trace_fieldnames(include_privacy_risk: bool = False) -> list[str]:
    names = [str(column["name"]) for column in load_schema()["columns"]]
    names.extend(PROVENANCE_FIELDS)
    if include_privacy_risk:
        names.append("raw_prompt")
    return names


def base_row(timestamp_ns: int, **overrides: str) -> dict[str, str]:
    row = {
        "timestamp_ns": str(timestamp_ns),
        "scenario_id": "high_volume_stable_moderation",
        "policy_version_hash": "hash:pipeline-policy",
        "request_class": "standard",
        "feature_vector_hash": f"hash:pipeline-{timestamp_ns}",
        "feature_length": "8",
        "route_decision": "physicalized_fast_path",
        "fallback_taken": "false",
        "near_threshold": "false",
        "audit_logged": "true",
        "health_gate_passed": "true",
        "drift_gate_passed": "true",
        "feature_extract_latency_ns": "1000",
        "route_latency_ns": "300",
        "audit_latency_ns": "5000",
        "software_baseline_latency_ns": "9000",
        "accelerator_baseline_latency_ns": "4000",
        "hybrid_fast_path_latency_ns": "1200",
        "accelerator_energy_proxy_or_measured_pj": "1000000000",
        "accelerator_energy_status": "measured",
        "hybrid_energy_proxy_or_measured_pj": "980000000",
        "hybrid_energy_status": "measured",
        "utilization_fraction": "0.70",
        "update_event": "false",
        "rollback_event": "false",
        "measurement_environment": "shadow_production",
        "evidence_source_type": "shadow_production",
        "ingestion_path_id": "shadow_production_dual_run",
        "measurement_status": "measured",
        "provenance_attestation": "true",
    }
    row.update(overrides)
    return row


def write_trace(path: Path, rows: list[dict[str, str]], include_privacy_risk: bool = False) -> None:
    fieldnames = trace_fieldnames(include_privacy_risk)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def generate_fixtures() -> list[Path]:
    write_trace(
        FIXTURE_INVALID_PRIVACY,
        [
            base_row(
                1000,
                evidence_source_type="production",
                ingestion_path_id="privacy_risk_raw_logs",
                raw_prompt="blocked raw content",
            )
        ],
        include_privacy_risk=True,
    )
    write_trace(
        FIXTURE_VALID_INSUFFICIENT,
        [
            base_row(
                1000,
                evidence_source_type="synthetic",
                ingestion_path_id="synthetic_fixture_only",
                measurement_status="proxy",
                measurement_environment="synthetic",
                accelerator_energy_status="measured",
                hybrid_energy_status="proxy",
            ),
            base_row(
                2000,
                evidence_source_type="synthetic",
                ingestion_path_id="synthetic_fixture_only",
                measurement_status="proxy",
                measurement_environment="synthetic",
                accelerator_energy_status="measured",
                hybrid_energy_status="proxy",
            ),
        ],
    )
    write_trace(
        FIXTURE_THRESHOLD_NOT_CROSSED,
        [
            base_row(1000, accelerator_energy_proxy_or_measured_pj="1000000000", hybrid_energy_proxy_or_measured_pj="980000000"),
            base_row(2000, accelerator_energy_proxy_or_measured_pj="1000000000", hybrid_energy_proxy_or_measured_pj="980000000"),
        ],
    )
    write_trace(
        FIXTURE_COUNTERFACTUAL_CROSSED,
        [
            base_row(
                1000,
                evidence_source_type="synthetic",
                ingestion_path_id="offline_replay_redacted_features",
                measurement_environment="shadow_production",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
            base_row(
                2000,
                evidence_source_type="synthetic",
                ingestion_path_id="offline_replay_redacted_features",
                measurement_environment="shadow_production",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
        ],
    )
    return [
        FIXTURE_INVALID_PRIVACY,
        FIXTURE_VALID_INSUFFICIENT,
        FIXTURE_THRESHOLD_NOT_CROSSED,
        FIXTURE_COUNTERFACTUAL_CROSSED,
    ]


def read_trace_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def first_present(rows: list[dict[str, str]], field: str, default: str = "") -> str:
    for row in rows:
        if row.get(field, ""):
            return row[field]
    return default


def aggregate_energy(rows: list[dict[str, str]]) -> tuple[float, float]:
    accelerator = 0.0
    hybrid = 0.0
    for row in rows:
        accelerator += float(row.get("accelerator_energy_proxy_or_measured_pj") or 0.0)
        hybrid += float(row.get("hybrid_energy_proxy_or_measured_pj") or 0.0)
    return accelerator, hybrid


def evaluate_trace(
    path: Path,
    schema: dict[str, object],
    ingestion_scores: dict[str, dict[str, str]],
    thresholds: dict[str, dict[str, str]],
) -> dict[str, str]:
    rows = read_trace_rows(path)
    validation = validator.validate_trace(path, schema)
    source_type = first_present(rows, "evidence_source_type", "missing")
    ingestion_path_id = first_present(rows, "ingestion_path_id", "missing")
    measurement_status = first_present(rows, "measurement_status", "missing")
    provenance_attestation = parse_bool(first_present(rows, "provenance_attestation", "false"))
    scenario_id = first_present(rows, "scenario_id", "missing")
    ingestion = ingestion_scores.get(ingestion_path_id, {})
    ingestion_class = ingestion.get("classification", "missing_ingestion_path")
    can_evaluate_ingestion = ingestion.get("can_evaluate_m_reopen_1", "False") == "True"
    threshold = thresholds.get(scenario_id, {})
    required_reduction = float(threshold.get("required_hybrid_daily_reduction_to_tie_pj_equivalent_per_day", "inf"))
    accelerator_energy, hybrid_energy = aggregate_energy(rows)
    threshold_margin = (accelerator_energy - hybrid_energy) - required_reduction
    threshold_crossed = math.isfinite(threshold_margin) and threshold_margin > 0.0
    measured_terms = (
        measurement_status == "measured"
        and validation["energy_coverage"]["accelerator_measured_rows"] == validation["requests"]
        and validation["energy_coverage"]["hybrid_measured_rows"] == validation["requests"]
    )
    source_ok = source_type in SOURCE_TYPES_FOR_ACTUAL
    trace_candidate = validation["status"] == "valid_reopen_candidate"
    actual_ready = (
        trace_candidate
        and ingestion_class == "reopen_candidate_path"
        and can_evaluate_ingestion
        and measured_terms
        and source_ok
        and provenance_attestation
        and threshold_crossed
    )
    if str(validation["status"]).startswith("invalid_"):
        final_status = "invalid_trace"
    elif actual_ready:
        final_status = "actual_reopen_candidate"
    elif threshold_crossed and source_type == "synthetic":
        final_status = "synthetic_counterfactual_crossed"
    elif not trace_candidate or not measured_terms or not can_evaluate_ingestion or ingestion_class in {"valid_but_insufficient", "threshold_evaluable_if_measured", "missing_ingestion_path"}:
        final_status = "valid_but_insufficient"
    elif not threshold_crossed:
        final_status = "threshold_evaluable_not_crossed"
    else:
        final_status = "valid_but_insufficient"
    blocker_parts = []
    if not trace_candidate:
        blocker_parts.append(f"trace_status={validation['status']}")
    if ingestion_class != "reopen_candidate_path":
        blocker_parts.append(f"ingestion_class={ingestion_class}")
    if not measured_terms:
        blocker_parts.append("measured_terms=false")
    if not source_ok:
        blocker_parts.append(f"source_type={source_type}")
    if not provenance_attestation:
        blocker_parts.append("provenance_attestation=false")
    if not threshold_crossed:
        blocker_parts.append("threshold_crossed=false")
    try:
        trace_file = str(path.relative_to(ROOT))
    except ValueError:
        trace_file = str(path)
    return {
        "trace_file": trace_file,
        "scenario_id": scenario_id,
        "trace_validation_status": str(validation["status"]),
        "ingestion_path_id": ingestion_path_id,
        "ingestion_class": ingestion_class,
        "evidence_source_type": source_type,
        "measurement_status": measurement_status,
        "provenance_attestation": str(provenance_attestation),
        "measured_terms_sufficient": str(measured_terms),
        "m_trace_1_valid_reopen_candidate": str(trace_candidate),
        "m_ingest_1_reopen_candidate_path": str(ingestion_class == "reopen_candidate_path"),
        "requests": str(validation["requests"]),
        "accepted_fast_path_requests": str(validation["accepted_fast_path_requests"]),
        "accelerator_energy_sum_pj": f"{accelerator_energy:.6f}",
        "hybrid_energy_sum_pj": f"{hybrid_energy:.6f}",
        "required_reduction_to_tie_pj_equivalent": f"{required_reduction:.6f}",
        "threshold_margin_pj_equivalent": f"{threshold_margin:.6f}",
        "threshold_crossed": str(threshold_crossed),
        "final_status": final_status,
        "actual_reopen_candidate": str(final_status == "actual_reopen_candidate"),
        "primary_blockers": "none" if not blocker_parts else "|".join(blocker_parts),
    }


def write_results_csv(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "trace_file",
        "scenario_id",
        "trace_validation_status",
        "ingestion_path_id",
        "ingestion_class",
        "evidence_source_type",
        "measurement_status",
        "provenance_attestation",
        "measured_terms_sufficient",
        "m_trace_1_valid_reopen_candidate",
        "m_ingest_1_reopen_candidate_path",
        "requests",
        "accepted_fast_path_requests",
        "accelerator_energy_sum_pj",
        "hybrid_energy_sum_pj",
        "required_reduction_to_tie_pj_equivalent",
        "threshold_margin_pj_equivalent",
        "threshold_crossed",
        "final_status",
        "actual_reopen_candidate",
        "primary_blockers",
    ]
    with RESULTS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 900, 460
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "invalid_trace": (170, 72, 65),
        "valid_but_insufficient": (213, 153, 62),
        "threshold_evaluable_not_crossed": (86, 132, 180),
        "synthetic_counterfactual_crossed": (117, 92, 160),
        "actual_reopen_candidate": (52, 132, 86),
    }
    rect(55, 38, 845, 408, (239, 241, 244))
    bar_w = 130
    for idx, row in enumerate(rows):
        x0 = 95 + idx * 185
        crossed = row["threshold_crossed"] == "True"
        candidate = row["actual_reopen_candidate"] == "True"
        h = 260 if crossed else 145
        color = colors[row["final_status"]]
        rect(x0, 360 - h, x0 + bar_w, 360, color)
        if candidate:
            rect(x0 + 42, 82, x0 + 88, 118, (30, 96, 60))
        else:
            rect(x0 + 42, 82, x0 + 88, 118, (90, 96, 105))
    for i, color in enumerate(colors.values()):
        rect(635, 24 + i * 20, 655, 36 + i * 20, color)
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    OUTPUT_PNG.write_bytes(png)


def write_report(summary: dict[str, object], rows: list[dict[str, str]]) -> None:
    status_lines = "\n".join(
        f"- `{row['trace_file']}`: `{row['final_status']}`; blockers `{row['primary_blockers']}`."
        for row in rows
    )
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T10:24:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PIPELINE-1
---

# End-to-end reopen pipeline

M-PIPELINE-1 composes the three existing evidence gates before a trace-like artifact can affect the Phase 2 downgrade. The pipeline validates trace schema and privacy guardrails with M-TRACE-1, checks ingestion-path admissibility with M-INGEST-1, maps per-trace hybrid and programmable-baseline energy terms onto the M-REOPEN-1 threshold row, and emits a final status.

The final statuses are `invalid_trace`, `valid_but_insufficient`, `threshold_evaluable_not_crossed`, `synthetic_counterfactual_crossed`, and `actual_reopen_candidate`. Actual reopen requires the conjunction: M-TRACE-1 `valid_reopen_candidate`, M-INGEST-1 `reopen_candidate_path`, measured hybrid and programmable baseline terms, production/shadow/canary source type, provenance attestation, and threshold crossing.

![end-to-end reopen gate outcomes for invalid, insufficient, threshold-evaluable, and synthetic counterfactual traces, showing that no current artifact becomes actual production reopen evidence](../data/reopen_pipeline_decision_flow.png)

## Fixture results

{status_lines}

## Interpretation

No current artifact is actual production, shadow, or canary measured evidence that crosses the threshold with full provenance. The synthetic counterfactual crosses the numeric threshold only to exercise the arithmetic branch; it remains `synthetic_counterfactual_crossed`, not `actual_reopen_candidate`. The summary reports `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`, preserving the Phase 2 downgrade.
""",
        encoding="utf-8",
    )


def build_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    counts = Counter(row["final_status"] for row in rows)
    return {
        "schema_version": 1,
        "milestone_id": "M-PIPELINE-1",
        "status": "validated",
        "fixture_count": len(rows),
        "final_status_counts": dict(sorted(counts.items())),
        "actual_reopen_candidate_count": sum(1 for row in rows if row["actual_reopen_candidate"] == "True"),
        "synthetic_or_proxy_actual_reopen_candidates": [
            row["trace_file"]
            for row in rows
            if row["actual_reopen_candidate"] == "True"
            and (row["evidence_source_type"] == "synthetic" or row["measurement_status"] == "proxy")
        ],
        "required_actual_reopen_conditions": [
            "M-TRACE-1 valid_reopen_candidate",
            "M-INGEST-1 reopen_candidate_path",
            "measured hybrid and programmable baseline terms",
            "production/shadow/canary source type",
            "provenance attestation",
            "threshold crossed",
        ],
        "figure_caption": "end-to-end reopen gate outcomes for invalid, insufficient, threshold-evaluable, and synthetic counterfactual traces, showing that no current artifact becomes actual production reopen evidence",
    }


def main() -> int:
    paths = generate_fixtures()
    schema = load_schema()
    ingestion_scores = load_ingestion_scores()
    thresholds = load_thresholds()
    rows = [evaluate_trace(path, schema, ingestion_scores, thresholds) for path in paths]
    summary = build_summary(rows)
    write_results_csv(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(rows)
    write_report(summary, rows)
    for path in paths:
        print(f"wrote {path}")
    print(f"wrote {RESULTS_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {OUTPUT_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"final_status_counts: {summary['final_status_counts']}")
    print(f"actual_reopen_candidate_count: {summary['actual_reopen_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
