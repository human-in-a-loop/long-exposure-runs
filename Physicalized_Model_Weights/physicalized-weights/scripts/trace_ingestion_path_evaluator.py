# created: 2026-05-13T09:54:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INGEST-1
"""Evaluate trace-ingestion paths against M-TRACE-1 and M-REOPEN-1."""

from __future__ import annotations

import csv
import json
import struct
import zlib
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"

TRACE_SCHEMA_JSON = DATA_DIR / "production_trace_schema.json"
REOPEN_SUMMARY_JSON = DATA_DIR / "reopen_thresholds_summary.json"

PATHS_CSV = DATA_DIR / "trace_ingestion_paths.csv"
SCORES_CSV = DATA_DIR / "trace_ingestion_path_scores.csv"
SUMMARY_JSON = DATA_DIR / "trace_ingestion_path_summary.json"
OUTPUT_PNG = DATA_DIR / "trace_ingestion_path_admissibility.png"
REPORT_MD = DOCS_DIR / "trace_ingestion_paths.md"

CLASS_ORDER = [
    "inadmissible",
    "valid_but_insufficient",
    "threshold_evaluable_if_measured",
    "reopen_candidate_path",
]


@dataclass(frozen=True)
class IngestionPath:
    path_id: str
    description: str
    environment: str
    schema_complete: int
    measured_hybrid_coverage: int
    measured_accelerator_baseline_coverage: int
    measured_energy_coverage: int
    accepted_fast_path_validity: int
    fallback_audit_update_accounting: int
    policy_consistency: int
    privacy_safety: int
    workload_fidelity: int
    threshold_evaluability: int
    counterfactual_baseline_validity: int
    contains_privacy_risk: bool
    identical_workload_accounting: bool
    production_or_shadow: bool
    missing_fields_or_gaps: str
    recommended_next_instrumentation: str


@dataclass(frozen=True)
class ScoreRow:
    path_id: str
    classification: str
    actual_reopened: bool
    total_score: int
    max_score: int
    schema_completeness: int
    measured_hybrid_coverage: int
    measured_accelerator_baseline_coverage: int
    measured_energy_coverage: int
    accepted_fast_path_validity: int
    fallback_audit_update_accounting: int
    policy_consistency: int
    privacy_safety: int
    workload_fidelity: int
    threshold_evaluability: int
    counterfactual_baseline_validity: int
    can_pass_m_trace_1: bool
    can_evaluate_m_reopen_1: bool
    primary_blocker: str


def candidate_paths() -> list[IngestionPath]:
    return [
        IngestionPath(
            "synthetic_fixture_only",
            "Validator fixture or generated trace with no production measurement status.",
            "synthetic",
            4,
            1,
            1,
            0,
            3,
            3,
            4,
            4,
            1,
            0,
            1,
            False,
            False,
            False,
            "production/shadow environment, measured energy, and measured same-workload counterfactual baselines are absent",
            "Use only for validator testing; replace with shadow or canary dual-run production telemetry before threshold evaluation.",
        ),
        IngestionPath(
            "offline_replay_redacted_features",
            "Privacy-safe replay over hashed/redacted feature vectors with both paths instrumented outside production.",
            "staging",
            4,
            2,
            2,
            1,
            3,
            3,
            3,
            4,
            2,
            2,
            3,
            False,
            True,
            False,
            "production/shadow environment and measured deployment energy/utilization are absent",
            "Run the same dual-path instrumentation in shadow production and replace proxy/replay energy with measured hardware energy.",
        ),
        IngestionPath(
            "sampled_production_logs_without_baselines",
            "Sampled production logs from the live path without programmable and hybrid counterfactuals.",
            "production",
            2,
            1,
            0,
            1,
            2,
            2,
            3,
            3,
            3,
            0,
            0,
            False,
            False,
            True,
            "software/accelerator/hybrid counterfactual baselines and accepted fast-path gate evidence are incomplete",
            "Add dual-run baseline capture, measured accelerator/hybrid energy, and audit/health/drift gate telemetry for the same requests.",
        ),
        IngestionPath(
            "shadow_production_dual_run",
            "Shadow production path that evaluates hybrid and programmable accelerator baselines on the same requests.",
            "shadow_production",
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            False,
            True,
            True,
            "none if raw content is excluded and measured energy is captured for both paths",
            "Keep raw prompts out, enforce consistent policy windows, and export M-TRACE-1 rows plus measured energy/latency/utilization.",
        ),
        IngestionPath(
            "canary_ab_dual_instrumented",
            "Limited canary or A/B production path with dual instrumentation and measured counterfactuals.",
            "production",
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            4,
            False,
            True,
            True,
            "none if traffic assignment preserves identical workload accounting and no raw sensitive columns are exported",
            "Pin policy versions, log audit/fallback/update gates, and capture measured energy and latency for both alternatives per request class.",
        ),
        IngestionPath(
            "accelerator_vendor_benchmark_only",
            "Vendor accelerator benchmark measured outside the safety/filter serving workload.",
            "synthetic",
            1,
            0,
            3,
            3,
            0,
            0,
            1,
            4,
            1,
            0,
            0,
            False,
            False,
            False,
            "hybrid path, fallback/audit/update accounting, policy windows, and identical workload mapping are absent",
            "Treat as a component prior only; collect same-request shadow/canary traces before comparing against reopen thresholds.",
        ),
        IngestionPath(
            "privacy_risk_raw_logs",
            "Raw production logs containing prompts, user identifiers, tenant names, or sensitive content.",
            "production",
            3,
            4,
            4,
            4,
            4,
            4,
            4,
            0,
            4,
            0,
            4,
            True,
            True,
            True,
            "privacy-disallowed raw columns make the evidence inadmissible regardless of metric richness",
            "Drop raw content and identifiers before export; use feature hashes, aggregate route labels, and privacy-safe operational telemetry.",
        ),
        IngestionPath(
            "simulated_scaled_workload",
            "Synthetic load scaled from assumptions or modeled production volume without measured serving paths.",
            "synthetic",
            3,
            1,
            1,
            0,
            2,
            2,
            3,
            4,
            1,
            0,
            1,
            False,
            False,
            False,
            "production measurement status, measured energy, and same-request counterfactual baseline totals are absent",
            "Use for planning only; validate with privacy-safe production or shadow-production dual-run telemetry.",
        ),
    ]


def classify(path: IngestionPath) -> tuple[str, str, bool, bool]:
    if path.contains_privacy_risk or path.privacy_safety == 0:
        return "inadmissible", "privacy_risk_raw_or_sensitive_columns", False, False

    can_pass_trace = (
        path.schema_complete == 4
        and path.measured_hybrid_coverage == 4
        and path.measured_accelerator_baseline_coverage == 4
        and path.measured_energy_coverage == 4
        and path.accepted_fast_path_validity == 4
        and path.fallback_audit_update_accounting == 4
        and path.policy_consistency == 4
        and path.production_or_shadow
        and path.privacy_safety == 4
    )
    can_evaluate_threshold = (
        can_pass_trace
        and path.threshold_evaluability == 4
        and path.counterfactual_baseline_validity == 4
        and path.identical_workload_accounting
    )
    if can_pass_trace and can_evaluate_threshold:
        return "reopen_candidate_path", "none_path_can_instantiate_measured_delta", True, True

    if path.threshold_evaluability >= 2 and path.counterfactual_baseline_validity >= 3 and path.privacy_safety == 4:
        return "threshold_evaluable_if_measured", "needs_production_or_shadow_measured_energy_and_utilization", False, False

    if path.measured_accelerator_baseline_coverage == 0 or path.counterfactual_baseline_validity == 0:
        return "valid_but_insufficient", "missing_same_workload_counterfactual_baseline", False, False

    if path.measured_energy_coverage < 4:
        return "valid_but_insufficient", "measured_energy_required", False, False

    return "valid_but_insufficient", "missing_trace_or_threshold_requirements", False, False


def score_rows(paths: list[IngestionPath]) -> list[ScoreRow]:
    rows: list[ScoreRow] = []
    for path in paths:
        classification, blocker, can_pass, can_eval = classify(path)
        scores = [
            path.schema_complete,
            path.measured_hybrid_coverage,
            path.measured_accelerator_baseline_coverage,
            path.measured_energy_coverage,
            path.accepted_fast_path_validity,
            path.fallback_audit_update_accounting,
            path.policy_consistency,
            path.privacy_safety,
            path.workload_fidelity,
            path.threshold_evaluability,
            path.counterfactual_baseline_validity,
        ]
        rows.append(
            ScoreRow(
                path_id=path.path_id,
                classification=classification,
                actual_reopened=False,
                total_score=sum(scores),
                max_score=44,
                schema_completeness=path.schema_complete,
                measured_hybrid_coverage=path.measured_hybrid_coverage,
                measured_accelerator_baseline_coverage=path.measured_accelerator_baseline_coverage,
                measured_energy_coverage=path.measured_energy_coverage,
                accepted_fast_path_validity=path.accepted_fast_path_validity,
                fallback_audit_update_accounting=path.fallback_audit_update_accounting,
                policy_consistency=path.policy_consistency,
                privacy_safety=path.privacy_safety,
                workload_fidelity=path.workload_fidelity,
                threshold_evaluability=path.threshold_evaluability,
                counterfactual_baseline_validity=path.counterfactual_baseline_validity,
                can_pass_m_trace_1=can_pass,
                can_evaluate_m_reopen_1=can_eval,
                primary_blocker=blocker,
            )
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, rows: list[ScoreRow]) -> None:
    width, height = 900, 460
    pixels = bytearray([255, 255, 255] * width * height)
    colors = {
        "inadmissible": (190, 54, 42),
        "valid_but_insufficient": (224, 151, 47),
        "threshold_evaluable_if_measured": (82, 132, 196),
        "reopen_candidate_path": (54, 148, 97),
    }

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        for y in range(y0, y1):
            base = y * width * 3
            for x in range(x0, x1):
                idx = base + x * 3
                pixels[idx : idx + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < width and 0 <= y0 < height:
                idx = (y0 * width + x0) * 3
                pixels[idx : idx + 3] = bytes(color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    margin_left, margin_bottom = 70, 70
    chart_top, chart_right = 40, 860
    baseline = height - margin_bottom
    max_score = 44
    line(margin_left, chart_top, margin_left, baseline, (50, 50, 50))
    line(margin_left, baseline, chart_right, baseline, (50, 50, 50))
    for tick in range(0, max_score + 1, 11):
        y = baseline - int((baseline - chart_top) * tick / max_score)
        line(margin_left - 5, y, chart_right, y, (225, 225, 225))
    slot = (chart_right - margin_left) // len(rows)
    for i, row in enumerate(rows):
        x0 = margin_left + i * slot + 12
        x1 = margin_left + (i + 1) * slot - 12
        bar_h = int((baseline - chart_top) * row.total_score / max_score)
        rect(x0, baseline - bar_h, x1, baseline, colors[row.classification])
        if row.can_evaluate_m_reopen_1:
            rect(x0, baseline - bar_h - 8, x1, baseline - bar_h - 3, (20, 20, 20))

    legend_x, legend_y = 530, 48
    for idx, name in enumerate(CLASS_ORDER):
        rect(legend_x, legend_y + idx * 26, legend_x + 22, legend_y + idx * 26 + 14, colors[name])

    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    for chunk_type, chunk_data in [
        (b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
        (b"IDAT", zlib.compress(raw, 9)),
        (b"IEND", b""),
    ]:
        png += struct.pack(">I", len(chunk_data)) + chunk_type + chunk_data
        png += struct.pack(">I", zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF)
    path.write_bytes(png)


def write_report(paths: list[IngestionPath], rows: list[ScoreRow], summary: dict[str, object]) -> None:
    score_by_id = {row.path_id: row for row in rows}
    lines = [
        "---",
        "created: 2026-05-13T09:54:00Z",
        "cycle: 3",
        "run_id: run-2026-05-13T015136Z",
        "agent: worker",
        "milestone: M-INGEST-1",
        "---",
        "",
        "# Trace Ingestion Path Admissibility",
        "",
        "This note ranks candidate evidence-acquisition paths against the M-TRACE-1 validator and the M-REOPEN-1 threshold contract. A path can challenge the downgraded safety/filter claim only if it can form `measured_hybrid_total - measured_best_programmable_total` for the same requests, policy window, fallback/audit decisions, utilization, latency, and energy accounting.",
        "",
        f"Current result: {summary['reopen_candidate_path_count']} path designs can become reopen-candidate paths, but no path is actual reopened evidence because no measured production trace was supplied.",
        "",
        "![admissibility and evidence coverage of candidate production-trace ingestion paths, separating privacy failures, missing-baseline failures, proxy-only evidence, and threshold-evaluable measured paths](../data/trace_ingestion_path_admissibility.png)",
        "",
        "## Candidate Paths",
        "",
    ]
    for path in paths:
        score = score_by_id[path.path_id]
        lines.extend(
            [
                f"### `{path.path_id}`",
                "",
                f"- Classification: `{score.classification}`.",
                f"- Can pass M-TRACE-1: `{str(score.can_pass_m_trace_1).lower()}`.",
                f"- Can evaluate M-REOPEN-1: `{str(score.can_evaluate_m_reopen_1).lower()}`.",
                f"- Privacy status: `{'privacy_risk' if path.contains_privacy_risk else 'privacy_safe'}`.",
                f"- Workload fidelity score: `{path.workload_fidelity}/4`.",
                f"- Counterfactual baseline validity score: `{path.counterfactual_baseline_validity}/4`.",
                f"- Missing fields or measurement gaps: {path.missing_fields_or_gaps}.",
                f"- Recommended next instrumentation: {path.recommended_next_instrumentation}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "Synthetic fixtures, simulated scaled workloads, vendor-only accelerator benchmarks, and sampled logs without counterfactual baselines cannot reopen the claim. Offline redacted replay is useful for rehearsing the pipeline, but it remains below the measured-evidence standard until it is converted into production or shadow-production dual-run telemetry with measured energy and utilization. Privacy-risk raw logs are inadmissible regardless of metric richness because M-TRACE-1 explicitly disallows raw prompt, user, tenant, address, key, email, IP, and content columns.",
            "",
            "Only `shadow_production_dual_run` and `canary_ab_dual_instrumented` are classified as reopen-candidate path designs. That classification means the path can generate admissible rows if implemented with the stated instrumentation; it does not mean the safety/filter performance claim has reopened or won.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines))


def build_summary(rows: list[ScoreRow]) -> dict[str, object]:
    counts = Counter(row.classification for row in rows)
    return {
        "schema_version": 1,
        "milestone_id": "M-INGEST-1",
        "status": "validated",
        "path_count": len(rows),
        "classification_counts": {name: counts.get(name, 0) for name in CLASS_ORDER},
        "reopen_candidate_path_count": counts.get("reopen_candidate_path", 0),
        "actual_reopened_count": sum(1 for row in rows if row.actual_reopened),
        "can_pass_m_trace_1": [row.path_id for row in rows if row.can_pass_m_trace_1],
        "can_evaluate_m_reopen_1": [row.path_id for row in rows if row.can_evaluate_m_reopen_1],
        "blocked_convenient_sources": [
            row.path_id
            for row in rows
            if row.path_id
            in {
                "synthetic_fixture_only",
                "sampled_production_logs_without_baselines",
                "accelerator_vendor_benchmark_only",
                "privacy_risk_raw_logs",
                "simulated_scaled_workload",
            }
            and row.classification != "reopen_candidate_path"
        ],
        "trace_contract": json.loads(REOPEN_SUMMARY_JSON.read_text())["trace_contract"],
        "privacy_disallowed_columns": json.loads(TRACE_SCHEMA_JSON.read_text())["privacy_disallowed_columns"],
        "figure_caption": "admissibility and evidence coverage of candidate production-trace ingestion paths, separating privacy failures, missing-baseline failures, proxy-only evidence, and threshold-evaluable measured paths.",
    }


def main() -> None:
    paths = candidate_paths()
    rows = score_rows(paths)
    write_csv(PATHS_CSV, [asdict(path) for path in paths], list(asdict(paths[0]).keys()))
    write_csv(SCORES_CSV, [asdict(row) for row in rows], list(asdict(rows[0]).keys()))
    summary = build_summary(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(OUTPUT_PNG, rows)
    write_report(paths, rows, summary)
    print(f"wrote {PATHS_CSV}")
    print(f"wrote {SCORES_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {OUTPUT_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"classification_counts: {summary['classification_counts']}")
    print(f"actual_reopened_count: {summary['actual_reopened_count']}")


if __name__ == "__main__":
    main()
