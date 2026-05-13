# created: 2026-05-13T12:32:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ACQUIRE-1

"""Pre-collection readiness evaluator for future measured trace packages."""

from __future__ import annotations

import csv
import json
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
CRITERIA_CSV = DATA / "evidence_acquisition_readiness_criteria.csv"
DESIGNS_CSV = DATA / "evidence_acquisition_designs.csv"
RESULTS_CSV = DATA / "evidence_acquisition_readiness_results.csv"
SUMMARY_JSON = DATA / "evidence_acquisition_readiness_summary.json"
MATRIX_PNG = DATA / "evidence_acquisition_readiness_matrix.png"

MILESTONE_ID = "M-ACQUIRE-1"
FIGURE_CAPTION = (
    "Readiness classification for proposed evidence-acquisition designs, separating "
    "admissible future collection plans from inadmissible, repair-required, and "
    "diagnostic-only designs before any data can affect the Phase 2 downgrade."
)
VALID_GATE_DEPENDENCIES = {
    "M-MEASURE-1",
    "M-TRACE-1",
    "M-REOPEN-1",
    "M-INGEST-1",
    "M-PIPELINE-1",
    "M-EVIDENCEPACK-1",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def as_bool(value: str) -> bool:
    value = str(value).strip().lower()
    if value in {"true", "1", "yes"}:
        return True
    if value in {"false", "0", "no"}:
        return False
    raise ValueError(f"not a boolean: {value!r}")


def criterion_passes(design: dict[str, str], criterion: dict[str, str]) -> bool:
    actual = design[criterion["design_field"]]
    expected = criterion["expected_value"]
    if expected in {"true", "false"}:
        return as_bool(actual) is as_bool(expected)
    return actual == expected


def classify_design(
    design: dict[str, str], criteria: list[dict[str, str]]
) -> dict[str, str | int | bool]:
    failures = [c for c in criteria if not criterion_passes(design, c)]
    fatal_failures = [c for c in failures if as_bool(c["fatal_if_missing"])]
    repairable_failures = [c for c in failures if not as_bool(c["fatal_if_missing"])]
    blockers = [f'{c["criterion_id"]}:{c["downstream_gate_failure"]}' for c in failures]
    fatal_blockers = [
        f'{c["criterion_id"]}:{c["downstream_gate_failure"]}' for c in fatal_failures
    ]
    repair_blockers = [
        f'{c["criterion_id"]}:{c["downstream_gate_failure"]}'
        for c in repairable_failures
    ]

    diagnostic_only = as_bool(design["scaled_synthetic_only"]) or as_bool(
        design["vendor_or_proxy_only"]
    )

    if diagnostic_only:
        readiness_class = "diagnostic_only"
    elif not failures:
        readiness_class = "ready_to_collect_candidate"
    elif fatal_failures:
        readiness_class = "inadmissible_design"
    else:
        readiness_class = "repair_required_before_collection"

    downstream_gate_failures = sorted({c["downstream_gate_failure"] for c in failures})
    missing_criteria = sorted(c["criterion_id"] for c in failures)
    actual_reopen_candidate = False

    return {
        "design_id": design["design_id"],
        "readiness_class": readiness_class,
        "actual_reopen_candidate": actual_reopen_candidate,
        "is_evidence": False,
        "missing_criteria_count": len(failures),
        "fatal_missing_count": len(fatal_failures),
        "repairable_missing_count": len(repairable_failures),
        "blocking_reasons": ";".join(blockers) if blockers else "none",
        "fatal_blocking_reasons": ";".join(fatal_blockers) if fatal_blockers else "none",
        "repair_actions": ";".join(repair_blockers) if repair_blockers else "none",
        "downstream_gate_failures": ";".join(downstream_gate_failures)
        if downstream_gate_failures
        else "none",
        "primary_blocker": blockers[0] if blockers else "none_ready_plan_not_evidence",
        "ingestion_path_id": design["ingestion_path_id"],
        "evidence_source_type": design["evidence_source_type"],
    }


def validate_criteria(criteria: list[dict[str, str]]) -> None:
    for row in criteria:
        gate = row["gate_dependency"]
        if gate not in VALID_GATE_DEPENDENCIES:
            raise ValueError(f'{row["criterion_id"]} maps to unknown gate {gate}')
        if not row["downstream_gate_failure"]:
            raise ValueError(f'{row["criterion_id"]} has no downstream failure mapping')


def write_results(rows: list[dict[str, str | int | bool]]) -> None:
    fieldnames = [
        "design_id",
        "readiness_class",
        "actual_reopen_candidate",
        "is_evidence",
        "missing_criteria_count",
        "fatal_missing_count",
        "repairable_missing_count",
        "blocking_reasons",
        "fatal_blocking_reasons",
        "repair_actions",
        "downstream_gate_failures",
        "primary_blocker",
        "ingestion_path_id",
        "evidence_source_type",
    ]
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    rows: list[dict[str, str | int | bool]], criteria: list[dict[str, str]]
) -> None:
    class_counts: dict[str, int] = {}
    for row in rows:
        cls = str(row["readiness_class"])
        class_counts[cls] = class_counts.get(cls, 0) + 1
    fatal_criteria = [
        c["criterion_id"] for c in criteria if as_bool(c["fatal_if_missing"])
    ]
    summary = {
        "schema_version": 1,
        "milestone_id": MILESTONE_ID,
        "status": "validated",
        "design_count": len(rows),
        "criteria_count": len(criteria),
        "readiness_class_counts": class_counts,
        "ready_to_collect_candidate_count": class_counts.get(
            "ready_to_collect_candidate", 0
        ),
        "actual_reopen_candidate_count": 0,
        "current_artifacts_reopen": False,
        "readiness_is_evidence": False,
        "fatal_criteria": fatal_criteria,
        "validated_gate_dependencies": sorted(
            {c["gate_dependency"] for c in criteria}
        ),
        "future_reopen_condition": (
            "valid_package ∧ hash_match ∧ schema_compatible ∧ "
            "known_threshold_scenario ∧ valid_trace ∧ admissible_ingestion_path ∧ "
            "measured_terms ∧ production_or_shadow_or_canary_source ∧ "
            "provenance_attestation ∧ privacy_attestation ∧ threshold_crossed"
        ),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "Readiness is a pre-collection screen only. A ready design can produce "
            "a future admissible package, but without measured trace data it cannot "
            "satisfy measured_terms or threshold_crossed and cannot reopen the Phase 2 downgrade."
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, width: int, height: int, pixels: bytearray) -> None:
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y * stride : (y + 1) * stride])
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def fill_rect(
    pixels: bytearray,
    width: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int],
) -> None:
    height = len(pixels) // (width * 3)
    x0, x1 = max(0, x0), min(width, x1)
    y0, y1 = max(0, y0), min(height, y1)
    for y in range(y0, y1):
        for x in range(x0, x1):
            idx = (y * width + x) * 3
            pixels[idx : idx + 3] = bytes(color)


def write_matrix_png(rows: list[dict[str, str | int | bool]]) -> None:
    width, height = 960, 440
    pixels = bytearray([248, 249, 250] * width * height)
    colors = {
        "ready_to_collect_candidate": (47, 123, 109),
        "repair_required_before_collection": (219, 155, 48),
        "inadmissible_design": (190, 74, 69),
        "diagnostic_only": (95, 103, 184),
    }
    fill_rect(pixels, width, 0, 0, width, 52, (35, 42, 54))
    left, top, row_h = 245, 82, 26
    col_w = 52
    for i, row in enumerate(rows):
        y = top + i * row_h
        cls = str(row["readiness_class"])
        fill_rect(pixels, width, 30, y, 220, y + 18, (220, 224, 229))
        fill_rect(pixels, width, left, y, left + 4 * col_w, y + 18, (229, 232, 236))
        col_index = [
            "ready_to_collect_candidate",
            "repair_required_before_collection",
            "inadmissible_design",
            "diagnostic_only",
        ].index(cls)
        fill_rect(
            pixels,
            width,
            left + col_index * col_w,
            y,
            left + (col_index + 1) * col_w - 8,
            y + 18,
            colors[cls],
        )
        missing = int(row["missing_criteria_count"])
        fill_rect(
            pixels,
            width,
            500,
            y,
            500 + min(320, missing * 24),
            y + 18,
            (93, 111, 128),
        )
    legend_y = 365
    for j, (label, color) in enumerate(colors.items()):
        x = 40 + j * 220
        fill_rect(pixels, width, x, legend_y, x + 26, legend_y + 18, color)
        fill_rect(pixels, width, x + 34, legend_y, x + 190, legend_y + 18, (225, 228, 232))
    write_png(MATRIX_PNG, width, height, pixels)


def main() -> None:
    criteria = read_csv(CRITERIA_CSV)
    designs = read_csv(DESIGNS_CSV)
    validate_criteria(criteria)
    rows = [classify_design(design, criteria) for design in designs]
    write_results(rows)
    write_summary(rows, criteria)
    write_matrix_png(rows)
    print(f"wrote {RESULTS_CSV.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_JSON.relative_to(ROOT)}")
    print(f"wrote {MATRIX_PNG.relative_to(ROOT)}")
    print("actual_reopen_candidate_count: 0")


if __name__ == "__main__":
    main()
