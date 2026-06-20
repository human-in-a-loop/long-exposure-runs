# created: 2026-05-13T03:20:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PROTO-1
"""Tiny fixed-weight safety-filter prototype.

The fixed block is only an int8 dot product plus bias, threshold compare, and
margin output. Policy/version/health/audit/fallback decisions stay outside the
fixed computation, matching the M-ARCH-1 boundary.
"""

from __future__ import annotations

import csv
import json
import struct
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
VECTORS_CSV = DATA_DIR / "prototype_vectors.csv"
ROUTES_CSV = DATA_DIR / "prototype_route_results.csv"
BASELINE_CSV = DATA_DIR / "prototype_baseline_comparison.csv"
SUMMARY_JSON = DATA_DIR / "prototype_summary.json"
ROUTE_PNG = DATA_DIR / "prototype_route_distribution.png"

FEATURE_COUNT = 8
WEIGHTS = [12, -7, 5, 9, -11, 4, 6, -3]
BIAS = -10
THRESHOLD = 64
CONFIDENCE_THRESHOLD = 16
REQUIRED_POLICY_VERSION = 7
ACTIVE_POLICY_VERSION = 7


@dataclass(frozen=True)
class VectorCase:
    case_id: str
    features: list[int]
    classifier_available: bool = True
    fallback_available: bool = True
    audit_logging_available: bool = True
    observed_policy_version: int = ACTIVE_POLICY_VERSION
    required_policy_version: int = REQUIRED_POLICY_VERSION
    classifier_health: str = "healthy"
    drift_status: str = "normal"
    enforce_mode: bool = True
    host_force_fallback: bool = False


@dataclass(frozen=True)
class RouteRecord:
    case_id: str
    features: str
    score: int
    decision: str
    margin: int
    confidence: int
    route: str
    action: str
    reason: str
    physicalized_output_valid: bool
    fallback_used: bool
    fail_safe: bool
    classifier_available: bool
    fallback_available: bool
    audit_logging_available: bool
    observed_policy_version: int
    required_policy_version: int
    classifier_health: str
    drift_status: str
    enforce_mode: bool
    audit_request_id: str


def dot_score(features: list[int]) -> int:
    if len(features) != FEATURE_COUNT:
        raise ValueError(f"expected {FEATURE_COUNT} features, got {len(features)}")
    for value in features:
        if value < -128 or value > 127:
            raise ValueError(f"int8 feature out of range: {value}")
    return sum(feature * weight for feature, weight in zip(features, WEIGHTS)) + BIAS


def classify(features: list[int]) -> tuple[int, str, int, int]:
    score = dot_score(features)
    decision = "block" if score >= THRESHOLD else "allow"
    margin = abs(score - THRESHOLD)
    confidence = min(32767, margin)
    return score, decision, margin, confidence


def invalid_reason(case: VectorCase, confidence: int) -> str:
    if not case.classifier_available:
        return "classifier_unavailable"
    if case.host_force_fallback:
        return "host_forced_fallback"
    if case.classifier_health != "healthy":
        return "health_check_failed"
    if case.drift_status != "normal":
        return "drift_alarm"
    if case.observed_policy_version < case.required_policy_version:
        return "stale_policy_version"
    if confidence < CONFIDENCE_THRESHOLD:
        return "low_confidence"
    if not case.audit_logging_available:
        return "audit_logging_failure"
    return ""


def route_case(case: VectorCase) -> RouteRecord:
    score, decision, margin, confidence = classify(case.features)
    reason = invalid_reason(case, confidence)
    valid = reason == ""

    if valid:
        route = "physicalized_fast_path"
        action = f"use_physicalized_{decision}"
        reason = "accepted"
        fallback_used = False
        fail_safe = False
    elif case.fallback_available:
        route = "programmable_fallback"
        action = "use_fallback_decision"
        fallback_used = True
        fail_safe = False
    else:
        route = "fail_safe"
        action = "fail_closed_block" if case.enforce_mode else "fail_safe_escalate"
        fallback_used = False
        fail_safe = True

    return RouteRecord(
        case_id=case.case_id,
        features=" ".join(str(value) for value in case.features),
        score=score,
        decision=decision,
        margin=margin,
        confidence=confidence,
        route=route,
        action=action,
        reason=reason,
        physicalized_output_valid=valid,
        fallback_used=fallback_used,
        fail_safe=fail_safe,
        classifier_available=case.classifier_available,
        fallback_available=case.fallback_available,
        audit_logging_available=case.audit_logging_available,
        observed_policy_version=case.observed_policy_version,
        required_policy_version=case.required_policy_version,
        classifier_health=case.classifier_health,
        drift_status=case.drift_status,
        enforce_mode=case.enforce_mode,
        audit_request_id=f"proto-{case.case_id}",
    )


def vector_cases() -> list[VectorCase]:
    return [
        VectorCase("all_zero_bias_allow", [0, 0, 0, 0, 0, 0, 0, 0]),
        VectorCase("nominal_block_high_margin", [8, -4, 5, 6, -3, 2, 4, -1]),
        VectorCase("nominal_allow_high_margin", [-4, 6, -3, 0, 8, -2, -5, 3]),
        VectorCase("max_signed_features", [127, 127, 127, 127, 127, 127, 127, 127]),
        VectorCase("min_signed_features", [-128, -128, -128, -128, -128, -128, -128, -128]),
        VectorCase("threshold_equal", [6, 0, 1, 0, 0, 0, 0, 1]),
        VectorCase("near_threshold_allow", [6, 0, 0, 0, 0, 1, 0, 1]),
        VectorCase("near_threshold_block", [6, 0, 0, 0, 0, 0, 1, 1]),
        VectorCase(
            "stale_version_high_confidence",
            [8, -4, 5, 6, -3, 2, 4, -1],
            observed_policy_version=REQUIRED_POLICY_VERSION - 1,
        ),
        VectorCase(
            "failed_health_high_confidence",
            [8, -4, 5, 6, -3, 2, 4, -1],
            classifier_health="failed",
        ),
        VectorCase(
            "drift_alarm_high_confidence",
            [8, -4, 5, 6, -3, 2, 4, -1],
            drift_status="alarm",
        ),
        VectorCase(
            "host_forced_fallback",
            [8, -4, 5, 6, -3, 2, 4, -1],
            host_force_fallback=True,
        ),
        VectorCase(
            "audit_logging_failure",
            [8, -4, 5, 6, -3, 2, 4, -1],
            audit_logging_available=False,
        ),
        VectorCase(
            "fallback_unavailable_valid_fast_path",
            [8, -4, 5, 6, -3, 2, 4, -1],
            fallback_available=False,
        ),
        VectorCase(
            "classifier_and_fallback_unavailable",
            [0, 0, 0, 0, 0, 0, 0, 0],
            classifier_available=False,
            fallback_available=False,
            classifier_health="failed",
        ),
        VectorCase(
            "monitor_mode_unavailable",
            [0, 0, 0, 0, 0, 0, 0, 0],
            classifier_available=False,
            fallback_available=False,
            classifier_health="failed",
            enforce_mode=False,
        ),
    ]


def baseline_rows(records: list[RouteRecord]) -> list[dict[str, float | int | str]]:
    count = len(records)
    fast = sum(1 for record in records if record.route == "physicalized_fast_path")
    fallback = sum(1 for record in records if record.route == "programmable_fallback")
    fail_safe = sum(1 for record in records if record.route == "fail_safe")

    assumptions = {
        "feature_extraction": 12.0,
        "register_control": 4.0,
        "audit_logging": 5.0,
        "fixed_dot": 1.0,
        "software_classifier": 8.0,
        "programmable_classifier": 4.0,
        "fallback_dispatch": 3.0,
        "fail_safe_handling": 2.0,
    }
    common = count * (assumptions["feature_extraction"] + assumptions["audit_logging"])
    hybrid_cost = count * assumptions["register_control"]
    hybrid_cost += fast * assumptions["fixed_dot"]
    hybrid_cost += fallback * (assumptions["fallback_dispatch"] + assumptions["software_classifier"])
    hybrid_cost += fail_safe * assumptions["fail_safe_handling"]

    return [
        {
            "baseline": "software_optimized",
            "case_count": count,
            "fast_path_cases": 0,
            "fallback_cases": count,
            "fail_safe_cases": 0,
            "modeled_cost_units": common + count * assumptions["software_classifier"],
            "notes": "feature extraction and audit retained; optimized int8 software classifier every case",
        },
        {
            "baseline": "programmable_accelerator",
            "case_count": count,
            "fast_path_cases": 0,
            "fallback_cases": count,
            "fail_safe_cases": 0,
            "modeled_cost_units": common + count * assumptions["programmable_classifier"] + count * 2,
            "notes": "feature extraction and audit retained; programmable accelerator dispatch every case",
        },
        {
            "baseline": "hybrid_physicalized",
            "case_count": count,
            "fast_path_cases": fast,
            "fallback_cases": fallback,
            "fail_safe_cases": fail_safe,
            "modeled_cost_units": hybrid_cost,
            "notes": "includes feature extraction, register/control, audit, fixed dot, fallback dispatch, and fail-safe handling",
        },
        {
            "baseline": "hybrid_request_volume_zero",
            "case_count": 0,
            "fast_path_cases": 0,
            "fallback_cases": 0,
            "fail_safe_cases": 0,
            "modeled_cost_units": 0,
            "notes": "no amortization claim when request volume is zero",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_route_png(path: Path, route_counts: dict[str, int]) -> None:
    width, height = 720, 420
    pixels = bytearray([255, 255, 255] * width * height)
    colors = {
        "physicalized_fast_path": (41, 128, 185),
        "programmable_fallback": (243, 156, 18),
        "fail_safe": (192, 57, 43),
    }
    max_count = max(route_counts.values()) if route_counts else 1
    bar_width = 120
    gap = 90
    base_y = 340
    left = 90

    def put_rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                offset = (y * width + x) * 3
                pixels[offset : offset + 3] = bytes(color)

    put_rect(60, base_y, 660, base_y + 2, (80, 80, 80))
    for index, route in enumerate(["physicalized_fast_path", "programmable_fallback", "fail_safe"]):
        count = route_counts.get(route, 0)
        bar_height = int(240 * count / max_count) if max_count else 0
        x0 = left + index * (bar_width + gap)
        put_rect(x0, base_y - bar_height, x0 + bar_width, base_y, colors[route])

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        start = y * width * 3
        raw.extend(pixels[start : start + width * 3])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png.extend(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    png.extend(chunk(b"IDAT", compressed))
    png.extend(chunk(b"IEND", b""))
    path.write_bytes(png)


def run() -> dict[str, object]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cases = vector_cases()
    records = [route_case(case) for case in cases]
    route_counts = {
        route: sum(1 for record in records if record.route == route)
        for route in ["physicalized_fast_path", "programmable_fallback", "fail_safe"]
    }

    vector_rows = []
    for case in cases:
        score, decision, margin, confidence = classify(case.features)
        vector_rows.append(
            {
                "case_id": case.case_id,
                "features": " ".join(str(value) for value in case.features),
                "score": score,
                "decision": decision,
                "margin": margin,
                "confidence": confidence,
            }
        )
    write_csv(VECTORS_CSV, vector_rows)
    write_csv(ROUTES_CSV, [asdict(record) for record in records])
    baselines = baseline_rows(records)
    write_csv(BASELINE_CSV, baselines)
    write_route_png(ROUTE_PNG, route_counts)

    summary = {
        "schema_version": 1,
        "feature_count": FEATURE_COUNT,
        "weights": WEIGHTS,
        "bias": BIAS,
        "threshold": THRESHOLD,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "required_policy_version": REQUIRED_POLICY_VERSION,
        "case_count": len(records),
        "route_counts": route_counts,
        "fast_path_fraction": route_counts["physicalized_fast_path"] / len(records),
        "fallback_fraction": route_counts["programmable_fallback"] / len(records),
        "fail_safe_fraction": route_counts["fail_safe"] / len(records),
        "baseline_comparison": baselines,
        "records": [asdict(record) for record in records],
        "figure_caption": "route distribution for the prototype safety-filter classifier, separating physicalized fast path, programmable fallback, and fail-safe outcomes across nominal and edge-case vectors.",
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    output = run()
    print(f"wrote {output['case_count']} prototype cases to {DATA_DIR}")
    print(f"routes: {json.dumps(output['route_counts'], sort_keys=True)}")
