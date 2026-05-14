# created: 2026-05-13T23:05:00Z
# cycle: 6
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-6
"""Run all scripted task families and export deterministic score artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from alignment_test_factory.families import build_multi_family_summary  # noqa: E402

OUT_DIR = ROOT / "examples" / "families"
SUMMARY_PATH = OUT_DIR / "multi_family_score_summary.json"
MATRIX_PATH = OUT_DIR / "multi_family_verdict_matrix.csv"
SVG_PATH = OUT_DIR / "multi_family_verdict_matrix.svg"
CAPTION = "Pass/fail/inconclusive verdicts by task family, scripted variant, and deterministic predicate."


def write_summary(summary: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def write_matrix(summary: dict) -> list[dict[str, str]]:
    rows = []
    for sample in summary["samples"]:
        for result in sample["predicate_results"]:
            rows.append(
                {
                    "task_family": sample["task_family"],
                    "task_id": sample["task_id"],
                    "scenario_variant": sample["scenario_variant"],
                    "sample_id": sample["sample_id"],
                    "predicate_id": result["predicate_id"],
                    "verdict": result["verdict"],
                    "evidence_event_ids": "|".join(result["evidence_event_ids"]),
                }
            )
    with MATRIX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_svg(rows: list[dict[str, str]]) -> None:
    cell_w = 34
    row_h = 24
    left_w = 390
    top_h = 54
    width = left_w + cell_w
    height = top_h + len(rows) * row_h + 42
    colors = {"pass": "#2f7d32", "fail": "#c62828", "inconclusive": "#9e9e9e"}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif;font-size:11px;fill:#202124}.title{font-size:13px;font-weight:700}.caption{font-size:10px;fill:#5f6368}</style>',
        '<text class="title" x="12" y="22">Multi-family deterministic verdict matrix</text>',
        f'<text class="caption" x="12" y="{height - 14}">{CAPTION}</text>',
    ]
    for idx, row in enumerate(rows):
        y = top_h + idx * row_h
        label = f'{row["task_id"]} / {row["scenario_variant"]} / {row["predicate_id"]}'
        verdict = row["verdict"]
        lines.extend(
            [
                f'<text x="12" y="{y + 16}">{_escape(label)}</text>',
                f'<rect x="{left_w}" y="{y + 4}" width="22" height="16" rx="2" fill="{colors[verdict]}"/>',
                f'<text x="{left_w + 27}" y="{y + 16}">{verdict}</text>',
            ]
        )
    lines.append("</svg>")
    SVG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    summary = build_multi_family_summary()
    write_summary(summary)
    rows = write_matrix(summary)
    write_svg(rows)
    verdicts = {
        sample["sample_id"]: {item["predicate_id"]: item["verdict"] for item in sample["predicate_results"]}
        for sample in summary["samples"]
    }
    print(f"summary: {SUMMARY_PATH}")
    print(f"matrix: {MATRIX_PATH}")
    print(f"figure: {SVG_PATH}")
    print(f"verdicts: {verdicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
