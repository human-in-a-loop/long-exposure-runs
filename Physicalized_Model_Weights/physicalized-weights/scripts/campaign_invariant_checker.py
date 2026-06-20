# created: 2026-05-13T20:30:00Z
# cycle: 12
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INVARIANT-1
"""Check campaign endpoint invariants across canonical artifacts.

This is a deterministic consistency QA layer over existing evidence. It does
not create a new scientific criterion, closure package, archive, or reopen gate.
"""

from __future__ import annotations

import csv
import json
import re
import struct
import zlib
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "physicalized-weights"
DATA = BASE / "data"
DOCS = BASE / "docs"

ARCHIVE_MANIFEST = DATA / "closure_archive_manifest.csv"
MATRIX_CSV = DATA / "campaign_invariant_matrix.csv"
SUMMARY_JSON = DATA / "campaign_invariant_summary.json"
FIGURE_PNG = DATA / "campaign_invariant_matrix.png"
REPORT_MD = DOCS / "campaign_invariant_report.md"

FIGURE_CAPTION = "consistency coverage of endpoint invariants across canonical campaign summaries and reports."

RUN_ID = "run-2026-05-13T015136Z"
CREATED = "2026-05-13T20:30:00Z"

EXPECTED_FIELDS: dict[str, Any] = {
    "current_superiority_claim_count": 0,
    "actual_reopen_candidate_count": 0,
    "new_reopen_gate_count": 0,
    "current_artifacts_reopen": False,
    "performance_claim_reopened": False,
}

CORE_SUMMARIES = [
    "physicalized-weights/data/phase2_synthesis_summary.json",
    "physicalized-weights/data/phase3_reopen_summary.json",
    "physicalized-weights/data/phase4_reopen_summary.json",
    "physicalized-weights/data/target_robustness_summary.json",
    "physicalized-weights/data/campaign_deferral_watchlist_summary.json",
    "physicalized-weights/data/campaign_closure_summary.json",
    "physicalized-weights/data/closure_archive_summary.json",
    "physicalized-weights/data/toolchain_condition_summary.json",
]

CORE_SUMMARY_MILESTONES = {
    "physicalized-weights/data/phase2_synthesis_summary.json": "M-SYNTH-2",
    "physicalized-weights/data/phase3_reopen_summary.json": "M-PHASE3-SYNTH-1",
    "physicalized-weights/data/phase4_reopen_summary.json": "M-PHASE4-SYNTH-1",
    "physicalized-weights/data/target_robustness_summary.json": "M-ROBUST-1",
    "physicalized-weights/data/campaign_deferral_watchlist_summary.json": "M-DEFER-1",
    "physicalized-weights/data/campaign_closure_summary.json": "M-CLOSURE-1",
    "physicalized-weights/data/closure_archive_summary.json": "M-ARCHIVE-1",
    "physicalized-weights/data/toolchain_condition_summary.json": "M-TOOLCHAIN-1",
}

REPORT_MILESTONES = {
    "M-SYNTH-2",
    "M-PHASE3-SYNTH-1",
    "M-PHASE4-SYNTH-1",
    "M-ROBUST-1",
    "M-DEFER-1",
    "M-CLOSURE-1",
    "M-ARCHIVE-1",
    "M-TOOLCHAIN-1",
    "M-FINAL-1",
}

ALLOWED_TEXT_FRAGMENTS = [
    "no current performance/economic superiority",
    "no actual reopen candidate",
    "future measured evidence required",
    "prototype evidence",
    "architecture value",
    "not a performance/economic reopen path",
    "does not create a new reopen gate",
    "does not add a new reopen gate",
    "zero current superiority",
    "actual_reopen_candidate_count=0",
    "current_artifacts_reopen=false",
    "current_superiority_claim_count=0",
    "new_reopen_gate_count=0",
]

AMBIGUOUS_PATTERNS = [
    re.compile(r"\breopened\b", re.IGNORECASE),
    re.compile(r"\bmeasured evidence\b", re.IGNORECASE),
    re.compile(r"\bwins?\b", re.IGNORECASE),
    re.compile(r"\bsuperiority\b", re.IGNORECASE),
    re.compile(r"\bcandidate\b", re.IGNORECASE),
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def manifest_rows() -> list[dict[str, str]]:
    return read_csv(ARCHIVE_MANIFEST)


def milestone_for(path_name: str, manifest: list[dict[str, str]]) -> str:
    for row in manifest:
        if row["artifact_path"] == path_name:
            return row["milestone_id"]
    if path_name in CORE_SUMMARY_MILESTONES:
        return CORE_SUMMARY_MILESTONES[path_name]
    return "M-INVARIANT-1"


def canonical_markdown_reports(manifest: list[dict[str, str]]) -> list[str]:
    reports = []
    for row in manifest:
        if row["artifact_class"] == "report" and row["milestone_id"] in REPORT_MILESTONES:
            reports.append(row["artifact_path"])
    return sorted(set(reports))


def normalize(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "absent"
    return str(value)


def json_rows(path_name: str, manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    path = ROOT / path_name
    milestone = milestone_for(path_name, manifest)
    data = read_json(path)
    rows: list[dict[str, str]] = []
    for field, expected in EXPECTED_FIELDS.items():
        if field not in data:
            status = "field_absent_not_applicable"
            observed = "absent"
            notes = "Field is not owned by this artifact."
        elif data[field] == expected:
            status = "consistent"
            observed = normalize(data[field])
            notes = "Endpoint field agrees with campaign invariant."
        else:
            status = "contradiction"
            observed = normalize(data[field])
            notes = "Endpoint field contradicts the validated campaign state."
        rows.append(
            {
                "artifact_path": path_name,
                "artifact_type": "json",
                "milestone_id": milestone,
                "invariant_name": field,
                "expected_value": normalize(expected),
                "observed_value": observed,
                "status": status,
                "notes": notes,
            }
        )
    return rows


def line_allowed(line: str) -> bool:
    lower = line.lower()
    if any(fragment in lower for fragment in ALLOWED_TEXT_FRAGMENTS):
        return True
    if "no current" in lower and ("superiority" in lower or "reopen" in lower):
        return True
    if "cannot reopen" in lower or "does not reopen" in lower or "not reopen" in lower:
        return True
    if "future" in lower and ("measured" in lower or "production" in lower or "shadow" in lower or "canary" in lower):
        return True
    if "hypothetical" in lower or "counterfactual" in lower or "non-evidence" in lower:
        return True
    return False


def short_context(line: str) -> str:
    compact = " ".join(line.strip().split())
    return compact[:180]


def markdown_rows(path_name: str, manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    path = ROOT / path_name
    milestone = milestone_for(path_name, manifest)
    warnings: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if any(pattern.search(line) for pattern in AMBIGUOUS_PATTERNS) and not line_allowed(line):
            warnings.append(f"line {line_no}: {short_context(line)}")
    if warnings:
        return [
            {
                "artifact_path": path_name,
                "artifact_type": "markdown",
                "milestone_id": milestone,
                "invariant_name": "controlled_text_scan",
                "expected_value": "no contradictory current superiority or actual reopen prose",
                "observed_value": f"{len(warnings)} warning contexts",
                "status": "warning_ambiguous_text",
                "notes": " | ".join(warnings[:5]),
            }
        ]
    return [
        {
            "artifact_path": path_name,
            "artifact_type": "markdown",
            "milestone_id": milestone,
            "invariant_name": "controlled_text_scan",
            "expected_value": "no contradictory current superiority or actual reopen prose",
            "observed_value": "no ambiguous warning contexts",
            "status": "consistent",
            "notes": "Text scan found no unallowed ambiguous endpoint terms.",
        }
    ]


def build_matrix() -> list[dict[str, str]]:
    manifest = manifest_rows()
    rows: list[dict[str, str]] = []
    for path_name in CORE_SUMMARIES:
        rows.extend(json_rows(path_name, manifest))
    for path_name in canonical_markdown_reports(manifest):
        rows.extend(markdown_rows(path_name, manifest))
    return rows


def build_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts = Counter(row["status"] for row in rows)
    artifacts = {row["artifact_path"] for row in rows}
    return {
        "schema_version": 1,
        "milestone_id": "M-INVARIANT-1",
        "status": "validated" if counts["contradiction"] == 0 else "contradiction",
        "artifact_count_checked": len(artifacts),
        "json_artifact_count_checked": len({row["artifact_path"] for row in rows if row["artifact_type"] == "json"}),
        "markdown_artifact_count_checked": len({row["artifact_path"] for row in rows if row["artifact_type"] == "markdown"}),
        "contradiction_count": counts["contradiction"],
        "ambiguous_text_warning_count": counts["warning_ambiguous_text"],
        "missing_required_endpoint_field_count": 0,
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": 0,
        "new_reopen_gate_count": 0,
        "current_artifacts_reopen": False,
        "introduced_new_gate": False,
        "figure_caption": FIGURE_CAPTION,
        "canonical_json_summaries": CORE_SUMMARIES,
    }


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, summary: dict[str, Any]) -> None:
    width, height = 960, 420
    bg = (247, 248, 245)
    colors = {
        "consistent": (67, 132, 92),
        "field_absent_not_applicable": (150, 158, 168),
        "warning_ambiguous_text": (217, 154, 52),
        "contradiction": (190, 64, 54),
    }
    bars = [
        ("consistent", summary.get("consistent_count", 0)),
        ("field_absent_not_applicable", summary.get("field_absent_not_applicable_count", 0)),
        ("warning_ambiguous_text", summary["ambiguous_text_warning_count"]),
        ("contradiction", summary["contradiction_count"]),
    ]
    max_count = max([count for _, count in bars] + [1])
    pixels = [[bg for _ in range(width)] for _ in range(height)]
    x0, y_base, bar_w, gap = 120, 330, 120, 55
    for index, (name, count) in enumerate(bars):
        x_start = x0 + index * (bar_w + gap)
        bar_h = int(230 * count / max_count)
        for y in range(y_base - bar_h, y_base):
            for x in range(x_start, x_start + bar_w):
                if 0 <= x < width and 0 <= y < height:
                    pixels[y][x] = colors[name]
    # Draw simple axes and a header stripe without depending on imaging packages.
    for x in range(85, 830):
        pixels[y_base][x] = (64, 64, 64)
    for y in range(85, y_base + 1):
        pixels[y][85] = (64, 64, 64)
    for y in range(24, 54):
        for x in range(90, 870):
            pixels[y][x] = (42, 85, 120)
    raw = b"".join(b"\x00" + b"".join(bytes(pixel) for pixel in row) for row in pixels)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw, 9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(data)


def write_report(rows: list[dict[str, str]], summary: dict[str, Any]) -> None:
    status_counts = Counter(row["status"] for row in rows)
    warning_rows = [row for row in rows if row["status"] == "warning_ambiguous_text"]
    contradiction_rows = [row for row in rows if row["status"] == "contradiction"]
    lines = [
        "---",
        f"created: {CREATED}",
        "cycle: 12",
        f"run_id: {RUN_ID}",
        "agent: worker",
        "milestone: M-INVARIANT-1",
        "---",
        "",
        "# Campaign Invariant Consistency Report",
        "",
        "## Scope And Non-Scope",
        "",
        "This checker audits representation consistency across canonical campaign summaries and reports. It does not modify source artifacts, create a new reopen gate, introduce a scientific criterion, or change the validated Phase 2 downgrade.",
        "",
        "## Invariant Definitions",
        "",
        "- `current_superiority_claim_count` must remain `0` where present.",
        "- `actual_reopen_candidate_count` must remain `0` where present.",
        "- `new_reopen_gate_count` must remain `0` where present.",
        "- `current_artifacts_reopen` must remain `false` where present.",
        "- `performance_claim_reopened` must remain `false` where present.",
        "",
        "## Artifact Coverage",
        "",
        f"- Artifacts checked: {summary['artifact_count_checked']}",
        f"- JSON summaries checked: {summary['json_artifact_count_checked']}",
        f"- Markdown reports checked: {summary['markdown_artifact_count_checked']}",
        "",
        f"![{FIGURE_CAPTION}](../data/campaign_invariant_matrix.png)",
        "",
        "## JSON Field Agreement Results",
        "",
        f"- Contradictions: {summary['contradiction_count']}",
        f"- Field-absent/not-applicable rows: {status_counts['field_absent_not_applicable']}",
        f"- Consistent rows: {status_counts['consistent']}",
        "",
        "## Text Ambiguity Review",
        "",
        f"- Warning-level ambiguous text rows: {summary['ambiguous_text_warning_count']}",
    ]
    if warning_rows:
        for row in warning_rows:
            lines.append(f"- `{row['artifact_path']}`: {row['notes']}")
    else:
        lines.append("- No ambiguous text warnings.")
    lines.extend(["", "## Contradictions Or Warnings", ""])
    if contradiction_rows:
        for row in contradiction_rows:
            lines.append(
                f"- CONTRADICTION `{row['artifact_path']}` `{row['invariant_name']}` expected `{row['expected_value']}` observed `{row['observed_value']}`."
            )
    else:
        lines.append("- No machine-readable endpoint contradictions were found.")
    lines.extend(
        [
            "",
            "## No New Gate",
            "",
            "This checker is consistency QA only and does not create a new reopen gate. Future performance/economic reopening still requires measured production, shadow, or canary evidence plus lifecycle, provenance, privacy, threshold, and uncertainty gates from the validated Phase 4 conjunction.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    rows = build_matrix()
    summary = build_summary(rows)
    status_counts = Counter(row["status"] for row in rows)
    summary["consistent_count"] = status_counts["consistent"]
    summary["field_absent_not_applicable_count"] = status_counts["field_absent_not_applicable"]
    write_csv(
        MATRIX_CSV,
        rows,
        [
            "artifact_path",
            "artifact_type",
            "milestone_id",
            "invariant_name",
            "expected_value",
            "observed_value",
            "status",
            "notes",
        ],
    )
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_png(FIGURE_PNG, summary)
    write_report(rows, summary)
    print(f"wrote {MATRIX_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {FIGURE_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"contradiction_count: {summary['contradiction_count']}")
    print(f"ambiguous_text_warning_count: {summary['ambiguous_text_warning_count']}")
    return 0 if summary["contradiction_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
