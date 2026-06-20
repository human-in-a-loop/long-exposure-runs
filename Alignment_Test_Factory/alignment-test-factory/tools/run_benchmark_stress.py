# created: 2026-05-13T23:55:00Z
# cycle: 7
# run_id: run-2026-05-13T204826Z
# agent: worker
# milestone: M-7
"""Run benchmark robustness stress probes and export auditable artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from alignment_test_factory.stress import build_stress_summary  # noqa: E402

OUT_DIR = ROOT / "examples" / "stress"
RESULTS_PATH = OUT_DIR / "benchmark_stress_results.json"
MATRIX_PATH = OUT_DIR / "benchmark_stress_matrix.csv"
SVG_PATH = OUT_DIR / "benchmark_stress_matrix.svg"
CAPTION = "Stress probe outcomes by family, stress class, expected outcome, and observed deterministic verdict."


def write_results(summary: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def write_matrix(summary: dict) -> list[dict[str, str]]:
    rows = [
        {
            "probe_id": result["probe_id"],
            "task_id": result["task_id"],
            "stress_class": result["stress_class"],
            "expected_outcome": result["expected_outcome"],
            "observed_outcome": result["observed_outcome"],
            "matched_expectation": str(result["matched_expectation"]).lower(),
            "trace_integrity_ok": str(result["trace_integrity"]["ok"]).lower(),
            "trace_requirements_ok": str(result["trace_requirements"]["ok"]).lower(),
        }
        for result in summary["results"]
    ]
    with MATRIX_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_svg(rows: list[dict[str, str]]) -> None:
    row_h = 26
    left_w = 510
    top_h = 54
    width = 760
    height = top_h + len(rows) * row_h + 44
    colors = {"pass": "#2f7d32", "fail": "#c62828", "inconclusive": "#757575", "invalid_trace": "#6a1b9a"}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,sans-serif;font-size:11px;fill:#202124}.title{font-size:13px;font-weight:700}.caption{font-size:10px;fill:#5f6368}.mono{font-family:Arial,sans-serif;font-size:10px}</style>',
        '<text class="title" x="12" y="22">Benchmark stress probe matrix</text>',
        f'<text class="caption" x="12" y="{height - 14}">{CAPTION}</text>',
    ]
    for idx, row in enumerate(rows):
        y = top_h + idx * row_h
        label = f'{row["probe_id"]} ({row["stress_class"]})'
        observed = row["observed_outcome"]
        expected = row["expected_outcome"]
        match = "match" if row["matched_expectation"] == "true" else "mismatch"
        lines.extend(
            [
                f'<text class="mono" x="12" y="{y + 17}">{_escape(label)}</text>',
                f'<rect x="{left_w}" y="{y + 5}" width="20" height="16" rx="2" fill="{colors[observed]}"/>',
                f'<text x="{left_w + 28}" y="{y + 17}">expected {expected}; observed {observed}; {match}</text>',
            ]
        )
    lines.append("</svg>")
    SVG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main() -> int:
    summary = build_stress_summary()
    write_results(summary)
    rows = write_matrix(summary)
    write_svg(rows)
    verdicts = {row["probe_id"]: row["observed_outcome"] for row in rows}
    print(f"results: {RESULTS_PATH}")
    print(f"matrix: {MATRIX_PATH}")
    print(f"figure: {SVG_PATH}")
    print(f"matched_expectations: {summary['matched_expectations']}/{summary['probe_count']}")
    print(f"verdicts: {verdicts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
