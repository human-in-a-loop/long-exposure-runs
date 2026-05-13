# created: 2026-05-13T15:00:00Z
# cycle: 5
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-UNCERTAINTY-1
"""Uncertainty-aware decision margin protocol for future reopen packages."""

from __future__ import annotations

import csv
import json
import math
import struct
import zlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

CASES_CSV = DATA_DIR / "reopen_uncertainty_cases.csv"
RESULTS_CSV = DATA_DIR / "reopen_uncertainty_results.csv"
SUMMARY_JSON = DATA_DIR / "reopen_uncertainty_summary.json"
OUTPUT_PNG = DATA_DIR / "reopen_uncertainty_margin_plot.png"
REPORT_MD = DOCS_DIR / "measured_reopen_uncertainty_protocol.md"

MILESTONE_ID = "M-UNCERTAINTY-1"
SCHEMA_VERSION = 1
CONFIDENCE_LEVEL = 0.95
ALPHA = 0.05
Z_ALPHA = 1.645
FIGURE_CAPTION = (
    "Uncertainty intervals for synthetic-safe measured-package scenarios, showing which "
    "point crossings fail or pass the statistical margin rule and why none are current "
    "actual reopen evidence."
)

CASE_FIELDS = [
    "case_id",
    "description",
    "scenario_id",
    "source_actuality",
    "package_gates_pass",
    "measured_terms",
    "admissible_ingestion_path",
    "request_count",
    "accepted_fast_path_count",
    "fallback_frequency",
    "hybrid_total_mean",
    "baseline_total_mean",
    "sigma_hybrid",
    "sigma_baseline",
    "rho",
    "sigma_workload_mix",
    "sigma_meter",
    "guardrail_telemetry_status",
    "expected_classification",
]

UNCERTAINTY_FIELDS = [
    "sigma_hybrid",
    "sigma_baseline",
    "rho",
    "sigma_workload_mix",
    "sigma_meter",
]


DEFAULT_CASES = [
    {
        "case_id": "point_crossing_wide_uncertainty",
        "description": "Nominal hybrid win with uncertainty interval crossing zero.",
        "scenario_id": "high_volume_stable_moderation",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "650000",
        "fallback_frequency": "0.08",
        "hybrid_total_mean": "980.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "45.0",
        "sigma_baseline": "42.0",
        "rho": "0.40",
        "sigma_workload_mix": "18.0",
        "sigma_meter": "12.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "point_crossing_not_statistically_durable",
    },
    {
        "case_id": "synthetic_large_margin_low_uncertainty",
        "description": "Large synthetic control win that passes the statistical margin but is not actual evidence.",
        "scenario_id": "high_volume_stable_moderation",
        "source_actuality": "synthetic_control",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "800000",
        "fallback_frequency": "0.03",
        "hybrid_total_mean": "760.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "10.0",
        "sigma_baseline": "11.0",
        "rho": "0.20",
        "sigma_workload_mix": "5.0",
        "sigma_meter": "4.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "statistically_durable_nonactual_control",
    },
    {
        "case_id": "baseline_favored_positive_delta",
        "description": "Measured candidate where hybrid remains more expensive than the programmable baseline.",
        "scenario_id": "bursty_consumer_traffic",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "900000",
        "accepted_fast_path_count": "500000",
        "fallback_frequency": "0.18",
        "hybrid_total_mean": "1060.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "20.0",
        "sigma_baseline": "18.0",
        "rho": "0.25",
        "sigma_workload_mix": "10.0",
        "sigma_meter": "8.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "baseline_favored",
    },
    {
        "case_id": "inconclusive_near_tie",
        "description": "Near tie whose interval overlaps zero without even a point hybrid win.",
        "scenario_id": "audit_heavy_regulated_deployment",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "700000",
        "accepted_fast_path_count": "350000",
        "fallback_frequency": "0.24",
        "hybrid_total_mean": "1004.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "15.0",
        "sigma_baseline": "15.0",
        "rho": "0.75",
        "sigma_workload_mix": "9.0",
        "sigma_meter": "7.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "inconclusive_overlap",
    },
    {
        "case_id": "missing_baseline_uncertainty",
        "description": "Point win with missing baseline uncertainty, which must not default to zero.",
        "scenario_id": "low_volume_enterprise_deployment",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "10000",
        "accepted_fast_path_count": "6000",
        "fallback_frequency": "0.05",
        "hybrid_total_mean": "900.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "12.0",
        "sigma_baseline": "",
        "rho": "0.10",
        "sigma_workload_mix": "6.0",
        "sigma_meter": "5.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "blocked_missing_uncertainty_terms",
    },
    {
        "case_id": "template_non_actual_source",
        "description": "Template/dry-run source is structurally blocked even with favorable means.",
        "scenario_id": "high_volume_stable_moderation",
        "source_actuality": "template_dryrun",
        "package_gates_pass": "false",
        "measured_terms": "false",
        "admissible_ingestion_path": "false",
        "request_count": "1000000",
        "accepted_fast_path_count": "700000",
        "fallback_frequency": "0.07",
        "hybrid_total_mean": "850.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "20.0",
        "sigma_baseline": "20.0",
        "rho": "0.30",
        "sigma_workload_mix": "8.0",
        "sigma_meter": "6.0",
        "guardrail_telemetry_status": "template",
        "expected_classification": "blocked_non_actual_source",
    },
    {
        "case_id": "zero_volume_control",
        "description": "Zero request volume cannot reopen regardless of favorable means.",
        "scenario_id": "zero_invocation_control",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "0",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "0.0",
        "hybrid_total_mean": "100.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "1.0",
        "sigma_baseline": "1.0",
        "rho": "0.00",
        "sigma_workload_mix": "1.0",
        "sigma_meter": "1.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "blocked_zero_volume",
    },
    {
        "case_id": "all_fallback_control",
        "description": "All-fallback traffic has no accepted physicalized fast-path benefit.",
        "scenario_id": "fallback_all_control",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "600000",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "1.0",
        "hybrid_total_mean": "700.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "5.0",
        "sigma_baseline": "5.0",
        "rho": "0.10",
        "sigma_workload_mix": "2.0",
        "sigma_meter": "2.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "blocked_all_fallback",
    },
    {
        "case_id": "correlated_shared_overhead_cancels_partially",
        "description": "High correlation cancels shared-mode overhead, but independent terms still leave a durable nonactual control.",
        "scenario_id": "audit_heavy_regulated_deployment",
        "source_actuality": "synthetic_control",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "500000",
        "accepted_fast_path_count": "360000",
        "fallback_frequency": "0.12",
        "hybrid_total_mean": "900.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "35.0",
        "sigma_baseline": "34.0",
        "rho": "0.95",
        "sigma_workload_mix": "10.0",
        "sigma_meter": "8.0",
        "guardrail_telemetry_status": "measured_shared_instrumentation",
        "expected_classification": "statistically_durable_nonactual_control",
    },
    {
        "case_id": "high_correlation_without_shared_instrumentation",
        "description": "High correlation is not allowed to cancel uncertainty without explicit shared-instrumentation attestation.",
        "scenario_id": "high_volume_stable_moderation",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "850000",
        "fallback_frequency": "0.04",
        "hybrid_total_mean": "995.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "100.0",
        "sigma_baseline": "100.0",
        "rho": "1.00",
        "sigma_workload_mix": "0.0",
        "sigma_meter": "0.0",
        "guardrail_telemetry_status": "measured",
        "expected_classification": "blocked_missing_uncertainty_terms",
    },
    {
        "case_id": "negative_margin_but_guardrail_missing",
        "description": "Missing guardrail telemetry uncertainty blocks a favorable point estimate.",
        "scenario_id": "frequent_policy_update_regime",
        "source_actuality": "actual_measured_candidate",
        "package_gates_pass": "true",
        "measured_terms": "true",
        "admissible_ingestion_path": "true",
        "request_count": "400000",
        "accepted_fast_path_count": "240000",
        "fallback_frequency": "0.20",
        "hybrid_total_mean": "880.0",
        "baseline_total_mean": "1000.0",
        "sigma_hybrid": "12.0",
        "sigma_baseline": "12.0",
        "rho": "0.50",
        "sigma_workload_mix": "6.0",
        "sigma_meter": "4.0",
        "guardrail_telemetry_status": "missing",
        "expected_classification": "blocked_missing_uncertainty_terms",
    },
]


def ensure_cases() -> None:
    if CASES_CSV.exists():
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with CASES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CASE_FIELDS)
        writer.writeheader()
        writer.writerows(DEFAULT_CASES)


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def parse_float(row: dict[str, str], field: str) -> float | None:
    value = str(row.get(field, "")).strip()
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def missing_uncertainty_terms(row: dict[str, str]) -> list[str]:
    missing = [field for field in UNCERTAINTY_FIELDS if parse_float(row, field) is None]
    if row.get("guardrail_telemetry_status") in {"", "missing"}:
        missing.append("guardrail_telemetry_status")
    rho = parse_float(row, "rho")
    if rho is not None and abs(rho) >= 0.90 and row.get("guardrail_telemetry_status") != "measured_shared_instrumentation":
        missing.append("shared_instrumentation_attestation_for_high_rho")
    return missing


def classify(row: dict[str, str]) -> dict[str, str]:
    request_count = parse_float(row, "request_count") or 0.0
    accepted_fast_path_count = parse_float(row, "accepted_fast_path_count") or 0.0
    fallback_frequency = parse_float(row, "fallback_frequency") or 0.0
    hybrid_total_mean = parse_float(row, "hybrid_total_mean")
    baseline_total_mean = parse_float(row, "baseline_total_mean")
    blockers: list[str] = []

    if request_count <= 0:
        return blocked_row(row, "blocked_zero_volume", "zero_request_volume")
    if accepted_fast_path_count <= 0 or fallback_frequency >= 1.0:
        return blocked_row(row, "blocked_all_fallback", "no_accepted_fast_path_volume")
    if hybrid_total_mean is None or baseline_total_mean is None:
        return blocked_row(row, "blocked_missing_uncertainty_terms", "missing_total_mean")

    missing = missing_uncertainty_terms(row)
    if missing:
        return blocked_row(row, "blocked_missing_uncertainty_terms", "|".join(f"missing:{field}" for field in missing))

    sigma_hybrid = parse_float(row, "sigma_hybrid") or 0.0
    sigma_baseline = parse_float(row, "sigma_baseline") or 0.0
    rho = parse_float(row, "rho") or 0.0
    sigma_workload_mix = parse_float(row, "sigma_workload_mix") or 0.0
    sigma_meter = parse_float(row, "sigma_meter") or 0.0
    rho = max(-1.0, min(1.0, rho))

    delta = hybrid_total_mean - baseline_total_mean
    variance_delta = (
        sigma_hybrid**2
        + sigma_baseline**2
        - 2.0 * rho * sigma_hybrid * sigma_baseline
        + sigma_workload_mix**2
        + sigma_meter**2
    )
    sigma_delta = math.sqrt(max(0.0, variance_delta))
    ucb = delta + Z_ALPHA * sigma_delta
    point_crossing = delta < 0.0
    statistically_durable = ucb < 0.0

    package_gates_pass = parse_bool(row.get("package_gates_pass", "false"))
    measured_terms = parse_bool(row.get("measured_terms", "false"))
    admissible_ingestion_path = parse_bool(row.get("admissible_ingestion_path", "false"))
    source_actuality = row.get("source_actuality", "")
    actual_source = source_actuality == "actual_measured_candidate"
    source_and_package_actual = package_gates_pass and measured_terms and admissible_ingestion_path and actual_source

    if not source_and_package_actual:
        if statistically_durable and source_actuality == "synthetic_control":
            classification = "statistically_durable_nonactual_control"
            blockers.append(f"source_actuality={source_actuality}")
        else:
            classification = "blocked_non_actual_source"
            if not actual_source:
                blockers.append(f"source_actuality={source_actuality}")
            if not package_gates_pass:
                blockers.append("package_gates_pass=false")
            if not measured_terms:
                blockers.append("measured_terms=false")
            if not admissible_ingestion_path:
                blockers.append("admissible_ingestion_path=false")
    elif statistically_durable:
        classification = "statistically_durable_actual_candidate"
    elif point_crossing:
        classification = "point_crossing_not_statistically_durable"
        blockers.append("ucb_alpha_not_below_zero")
    elif delta > 0.0:
        classification = "baseline_favored" if delta > sigma_delta else "inconclusive_overlap"
        blockers.append("delta_mean_nonnegative")
    else:
        classification = "inconclusive_overlap"
        blockers.append("interval_overlaps_zero")

    actual_reopen_candidate = classification == "statistically_durable_actual_candidate" and source_and_package_actual

    return {
        "case_id": row["case_id"],
        "scenario_id": row["scenario_id"],
        "source_actuality": source_actuality,
        "delta_mean": f"{delta:.6f}",
        "sigma_delta": f"{sigma_delta:.6f}",
        "ucb_alpha": f"{ucb:.6f}",
        "confidence_level": f"{CONFIDENCE_LEVEL:.2f}",
        "z_alpha": f"{Z_ALPHA:.3f}",
        "point_crossing": str(point_crossing),
        "statistically_durable": str(statistically_durable),
        "package_gates_pass": str(package_gates_pass),
        "measured_terms": str(measured_terms),
        "admissible_ingestion_path": str(admissible_ingestion_path),
        "actual_reopen_candidate": str(actual_reopen_candidate),
        "classification": classification,
        "expected_classification": row.get("expected_classification", ""),
        "status_matches_expected": str(classification == row.get("expected_classification", "")),
        "blocking_reasons": "|".join(blockers) if blockers else "none",
    }


def blocked_row(row: dict[str, str], classification: str, reason: str) -> dict[str, str]:
    return {
        "case_id": row["case_id"],
        "scenario_id": row["scenario_id"],
        "source_actuality": row.get("source_actuality", ""),
        "delta_mean": "",
        "sigma_delta": "",
        "ucb_alpha": "",
        "confidence_level": f"{CONFIDENCE_LEVEL:.2f}",
        "z_alpha": f"{Z_ALPHA:.3f}",
        "point_crossing": "False",
        "statistically_durable": "False",
        "package_gates_pass": row.get("package_gates_pass", "false"),
        "measured_terms": row.get("measured_terms", "false"),
        "admissible_ingestion_path": row.get("admissible_ingestion_path", "false"),
        "actual_reopen_candidate": "False",
        "classification": classification,
        "expected_classification": row.get("expected_classification", ""),
        "status_matches_expected": str(classification == row.get("expected_classification", "")),
        "blocking_reasons": reason,
    }


def read_cases() -> list[dict[str, str]]:
    ensure_cases()
    with CASES_CSV.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_results(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "case_id",
        "scenario_id",
        "source_actuality",
        "delta_mean",
        "sigma_delta",
        "ucb_alpha",
        "confidence_level",
        "z_alpha",
        "point_crossing",
        "statistically_durable",
        "package_gates_pass",
        "measured_terms",
        "admissible_ingestion_path",
        "actual_reopen_candidate",
        "classification",
        "expected_classification",
        "status_matches_expected",
        "blocking_reasons",
    ]
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 980, 430
    pixels = bytearray([255, 255, 255] * width * height)

    def set_pixel(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            pixels[idx : idx + 3] = bytes(color)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                set_pixel(x, y, color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    set_pixel(x + dx, y + dy, color)

    plot_x0, plot_x1 = 210, 930
    plot_y0, plot_y1 = 45, 360
    rect(0, 0, width, height, (248, 249, 250))
    rect(plot_x0, plot_y0, plot_x1, plot_y1, (255, 255, 255))
    line(plot_x0, plot_y1, plot_x1, plot_y1, (60, 64, 67))
    line(plot_x0, plot_y0, plot_x0, plot_y1, (60, 64, 67))

    numeric = [r for r in rows if r["delta_mean"] and r["sigma_delta"]]
    xs = []
    for r in numeric:
        delta = float(r["delta_mean"])
        sigma = float(r["sigma_delta"])
        xs.extend([delta - Z_ALPHA * sigma, delta, float(r["ucb_alpha"])])
    min_x, max_x = min(xs + [-1.0]), max(xs + [1.0])
    pad = (max_x - min_x) * 0.10
    min_x -= pad
    max_x += pad

    def xscale(value: float) -> int:
        return int(plot_x0 + (value - min_x) / (max_x - min_x) * (plot_x1 - plot_x0))

    zero_x = xscale(0.0)
    line(zero_x, plot_y0, zero_x, plot_y1, (190, 32, 32))

    colors = {
        "point_crossing_not_statistically_durable": (230, 126, 34),
        "statistically_durable_nonactual_control": (39, 137, 74),
        "baseline_favored": (192, 57, 43),
        "inconclusive_overlap": (127, 140, 141),
        "blocked_missing_uncertainty_terms": (108, 92, 231),
        "blocked_non_actual_source": (85, 85, 85),
        "blocked_zero_volume": (52, 73, 94),
        "blocked_all_fallback": (52, 73, 94),
    }
    y_step = 28
    for i, r in enumerate(rows):
        y = plot_y0 + 24 + i * y_step
        color = colors.get(r["classification"], (80, 80, 80))
        rect(18, y - 6, 190, y + 6, color)
        if r["delta_mean"] and r["sigma_delta"]:
            delta = float(r["delta_mean"])
            sigma = float(r["sigma_delta"])
            lo = delta - Z_ALPHA * sigma
            hi = float(r["ucb_alpha"])
            line(xscale(lo), y, xscale(hi), y, color)
            rect(xscale(delta) - 4, y - 4, xscale(delta) + 5, y + 5, color)
            rect(xscale(hi) - 3, y - 7, xscale(hi) + 4, y + 8, (0, 0, 0))
        else:
            rect(plot_x0 + 10, y - 4, plot_x0 + 80, y + 5, color)

    raw_rows = [bytes(pixels[y * width * 3 : (y + 1) * width * 3]) for y in range(height)]
    png_rows = b"".join(b"\x00" + row for row in raw_rows)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    payload = b"\x89PNG\r\n\x1a\n"
    payload += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    payload += chunk(b"IDAT", zlib.compress(png_rows, 9))
    payload += chunk(b"IEND", b"")
    OUTPUT_PNG.write_bytes(payload)


def write_doc(summary: dict[str, object]) -> None:
    text = f"""---
created: 2026-05-13T15:00:00Z
cycle: 5
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-UNCERTAINTY-1
---

# Measured Reopen Uncertainty Protocol

M-UNCERTAINTY-1 refines the future reopen rule from a point inequality to a confidence-bound decision. The operative quantity is `D = H - B`, where `H` is the measured hybrid total and `B` is the measured best programmable baseline total under identical workload, fallback, audit, update, utilization, latency, and energy accounting.

The uncertainty-aware rule is:

`UCB_alpha(D) = delta_mean + z_alpha * sigma_delta < 0`

with:

`delta_mean = hybrid_total_mean - best_programmable_total_mean`

`sigma_delta = sqrt(sigma_hybrid^2 + sigma_baseline^2 - 2*rho*sigma_hybrid*sigma_baseline + sigma_workload_mix^2 + sigma_meter^2)`

This is necessary but not sufficient. A future package must also satisfy all existing Phase 3 gates: valid package, hash match, schema compatibility, known threshold scenario, valid trace, admissible ingestion path, measured terms, production/shadow/canary source, provenance attestation, privacy attestation, threshold crossing, nonzero request volume, and nonzero accepted fast-path volume. Synthetic, proxy, template, dry-run, readiness, and intake-rehearsal artifacts remain non-actual even when the statistical interval is favorable.

## Uncertainty Sources

- Sample variance: finite trace windows make both `H` and `B` estimated totals.
- Meter calibration error: power, timing, and counter calibration uncertainty contributes to `sigma_meter`.
- Correlated measurement error: shared traffic, feature extraction, audit, or instrumentation can be represented by `rho`; high-correlation cancellation requires explicit shared-instrumentation attestation, cancels only the explicitly shared component, and never cancels missing or independent path variance.
- Workload mix uncertainty: sampling or replay mismatch across request classes contributes to `sigma_workload_mix`.
- Missing baseline uncertainty: absent programmable-baseline variance blocks evaluation rather than becoming zero.
- Guardrail-telemetry uncertainty: missing health, drift, audit, or fallback telemetry blocks evaluation because accepted fast-path credit is not trustworthy.

## Current Synthetic-Safe Evaluation

The classifier evaluates {summary["case_count"]} synthetic-safe scenarios. It reports `actual_reopen_candidate_count = {summary["actual_reopen_candidate_count"]}`.

![{FIGURE_CAPTION}](../data/reopen_uncertainty_margin_plot.png)

## Interpretation

No current artifact reopens the Phase 2 downgrade. The added layer is discriminating: small point crossings with intervals overlapping zero are blocked, large synthetic/control crossings can be identified as statistically durable while still non-actual, and zero-volume, all-fallback, missing-uncertainty, and non-actual-source cases preserve the prior Phase 3 blockers.
"""
    REPORT_MD.write_text(text, encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    cases = read_cases()
    rows = [classify(row) for row in cases]
    write_results(rows)
    write_png(rows)
    counts = Counter(row["classification"] for row in rows)
    status_mismatches = [row["case_id"] for row in rows if row["status_matches_expected"] != "True"]
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "status": "validated" if not status_mismatches else "needs_attention",
        "case_count": len(rows),
        "classification_counts": dict(sorted(counts.items())),
        "confidence_level": CONFIDENCE_LEVEL,
        "alpha": ALPHA,
        "z_alpha": Z_ALPHA,
        "actual_reopen_candidate_count": sum(1 for row in rows if row["actual_reopen_candidate"] == "True"),
        "current_artifacts_reopen": False,
        "status_mismatches": status_mismatches,
        "uncertainty_rule": "UCB_alpha(hybrid_total - best_programmable_total) < 0",
        "sigma_delta_formula": "sqrt(sigma_hybrid^2 + sigma_baseline^2 - 2*rho*sigma_hybrid*sigma_baseline + sigma_workload_mix^2 + sigma_meter^2)",
        "future_reopen_condition": (
            "valid_package && hash_match && schema_compatible && known_threshold_scenario && "
            "valid_trace && admissible_ingestion_path && measured_terms && "
            "production_or_shadow_or_canary_source && provenance_attestation && privacy_attestation && "
            "threshold_crossed && UCB_alpha_delta_below_zero"
        ),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The uncertainty layer blocks noisy point crossings, distinguishes statistically durable "
            "nonactual controls, treats missing variance as unevaluable, and preserves zero-volume, "
            "all-fallback, and non-actual-source blockers. No current committed artifact is actual reopen evidence."
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_doc(summary)
    print("classification_counts:", dict(sorted(counts.items())))
    print("actual_reopen_candidate_count:", summary["actual_reopen_candidate_count"])


if __name__ == "__main__":
    main()
