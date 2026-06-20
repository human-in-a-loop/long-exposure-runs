# created: 2026-05-13T21:08:00Z
# cycle: 13
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-1
"""Public programmable-baseline recency and calibration-impact probe.

The probe uses a curated source table instead of broad scraping. It screens
new public benchmark evidence for baseline-recency impact while preserving the
existing rule that public accelerator benchmarks are not measured hybrid
production/shadow/canary evidence.
"""

from __future__ import annotations

import csv
import json
import re
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "physicalized-weights"
DATA = BASE / "data"
DOCS = BASE / "docs"
REFERENCES = ROOT / "REFERENCES.md"

SOURCES_CSV = DATA / "public_baseline_sources.csv"
DELTA_CSV = DATA / "public_baseline_delta_matrix.csv"
SUMMARY_JSON = DATA / "public_baseline_recency_summary.json"
FIGURE_PNG = DATA / "public_baseline_delta_matrix.png"
REPORT_MD = DOCS / "public_baseline_recency_report.md"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, object]:
    with path.open() as handle:
        return json.load(handle)


def reference_ids() -> set[str]:
    text = REFERENCES.read_text()
    return set(re.findall(r"^\[(\d+)\]", text, flags=re.MULTILINE))


def curated_sources() -> list[dict[str, str]]:
    return [
        {
            "source_id": "mlperf_inference_docs",
            "reference_id": "10",
            "title": "MLPerf Inference: Datacenter benchmark documentation",
            "publisher": "MLCommons",
            "url": "https://docs.mlcommons.org/inference/",
            "publication_date": "current",
            "source_type": "benchmark_documentation",
            "primary_or_secondary": "primary",
            "machine_readable": "partial",
            "release_name": "MLPerf Inference documentation",
            "benchmark_suite_workloads": "Datacenter inference benchmark suite documentation and LoadGen scenario context.",
            "hardware_families_mentioned": "Architecture-neutral; submitted systems documented in release/result sources.",
            "directly_usable_in_existing_model": "no",
            "satisfies_measured_hybrid_reopen": "no",
            "notes": "Defines MLPerf Inference benchmark context and datacenter suite mechanics used by public submissions.",
        },
        {
            "source_id": "mlperf_inference_v60_results",
            "reference_id": "11",
            "title": "MLPerf Inference v6.0 Results",
            "publisher": "MLCommons",
            "url": "https://mlcommons.org/2026/04/mlperf-inference-v6-0-results/",
            "publication_date": "2026-04-01",
            "source_type": "official_release_page",
            "primary_or_secondary": "primary",
            "machine_readable": "linked_repository",
            "release_name": "MLPerf Inference v6.0",
            "benchmark_suite_workloads": "Datacenter tests with new or updated LLM, reasoning, recommender, text-to-video, VLM, plus edge object detection context.",
            "hardware_families_mentioned": "Public multi-node accelerator systems and datacenter inference submissions; exact systems belong in result tables/repository.",
            "directly_usable_in_existing_model": "partial",
            "satisfies_measured_hybrid_reopen": "no",
            "notes": "Latest official MLPerf Inference release identified in this probe; includes newer public programmable-baseline context.",
        },
        {
            "source_id": "mlperf_inference_v51_results",
            "reference_id": "12",
            "title": "MLPerf Inference v5.1 Results",
            "publisher": "MLCommons",
            "url": "https://mlcommons.org/2025/09/mlperf-inference-v5-1-results/",
            "publication_date": "2025-09-09",
            "source_type": "official_release_page",
            "primary_or_secondary": "primary",
            "machine_readable": "linked_repository",
            "release_name": "MLPerf Inference v5.1",
            "benchmark_suite_workloads": "Official inference benchmark suite update with new models, hardware/software systems, and public submission context.",
            "hardware_families_mentioned": "Public accelerator, CPU, and system submissions described by MLCommons result pages/repositories.",
            "directly_usable_in_existing_model": "partial",
            "satisfies_measured_hybrid_reopen": "no",
            "notes": "Intermediate official release newer than the campaign's original MLPerf documentation reference.",
        },
        {
            "source_id": "mlperf_inference_v60_repository",
            "reference_id": "13",
            "title": "MLPerf Inference Results v6.0",
            "publisher": "MLCommons",
            "url": "https://github.com/mlcommons/inference_results_v6.0",
            "publication_date": "2026-04-01",
            "source_type": "official_results_repository",
            "primary_or_secondary": "primary",
            "machine_readable": "yes",
            "release_name": "MLPerf Inference v6.0",
            "benchmark_suite_workloads": "Machine-readable official submission results for MLPerf Inference v6.0 benchmark scenarios.",
            "hardware_families_mentioned": "Structured submitted systems and accelerators in official result files.",
            "directly_usable_in_existing_model": "partial",
            "satisfies_measured_hybrid_reopen": "no",
            "notes": "Machine-readable official submission repository; useful for future programmable-baseline refresh, not directly comparable to safety-filter economics without mapping.",
        },
        {
            "source_id": "nvidia_mlperf_ai_benchmarks",
            "reference_id": "14",
            "title": "MLPerf AI Benchmarks",
            "publisher": "NVIDIA",
            "url": "https://www.nvidia.com/en-us/data-center/resources/mlperf-benchmarks/",
            "publication_date": "current",
            "source_type": "vendor_context_page",
            "primary_or_secondary": "secondary",
            "machine_readable": "no",
            "release_name": "MLPerf vendor context",
            "benchmark_suite_workloads": "Vendor summary of MLPerf benchmark participation and submitted-system context.",
            "hardware_families_mentioned": "NVIDIA accelerator families only; secondary naming context.",
            "directly_usable_in_existing_model": "no",
            "satisfies_measured_hybrid_reopen": "no",
            "notes": "Secondary context for submitted programmable systems and hardware naming only; not used as a primary calibration source.",
        },
    ]


def delta_rows(stronger: dict[str, object], phase2: dict[str, object]) -> list[dict[str, str]]:
    winner_counts = stronger["winner_counts"]
    phase2_conclusion = phase2["central_conclusion"]
    return [
        {
            "baseline_dimension": "official_release_recency",
            "campaign_assumption": "Campaign cited MLPerf documentation as public programmable-baseline context, not a specific latest results release.",
            "public_update_observation": "MLCommons official MLPerf Inference v6.0 results are newer than the campaign reference set.",
            "materiality": "material",
            "directly_calibratable": "partial",
            "recommended_action": "future_model_refresh_recommended",
            "notes": "Use primary MLCommons release/repository data to refresh programmable-baseline priors in a later cycle.",
        },
        {
            "baseline_dimension": "programmable_accelerator_strength",
            "campaign_assumption": f"M-SWBASE-2 already had programmable_accelerator wins in {winner_counts.get('programmable_accelerator')} of 10 equal-workload scenarios.",
            "public_update_observation": "Newer official public results continue to expose strong programmable accelerator systems and datacenter inference submissions.",
            "materiality": "material",
            "directly_calibratable": "partial",
            "recommended_action": "baseline_strengthened_no_claim_reopen",
            "notes": "The direction strengthens or refreshes the null hypothesis; it does not support a physicalized-weight win.",
        },
        {
            "baseline_dimension": "benchmark_workload_match",
            "campaign_assumption": "Safety-filter economics require identical feature extraction, audit, fallback, update cadence, utilization, energy, and latency accounting.",
            "public_update_observation": "MLPerf benchmark workloads are public accelerator benchmark scenarios, not the campaign's safety-filter production/shadow/canary workload.",
            "materiality": "context_only",
            "directly_calibratable": "no",
            "recommended_action": "do_not_map_directly_to_safety_filter",
            "notes": "Useful as baseline context only unless a later model derives a defensible mapping from benchmark metrics to campaign model terms.",
        },
        {
            "baseline_dimension": "machine_readable_public_data",
            "campaign_assumption": "Calibration inputs should be auditable and sourced rather than vendor-only prose.",
            "public_update_observation": "Official MLCommons v6.0 result repository is machine-readable, while the vendor page is secondary context only.",
            "materiality": "material",
            "directly_calibratable": "partial",
            "recommended_action": "use_primary_repository_not_vendor_page",
            "notes": "A future refresh can parse official repositories; vendor pages must not drive calibration alone.",
        },
        {
            "baseline_dimension": "phase2_conclusion",
            "campaign_assumption": phase2_conclusion,
            "public_update_observation": "No measured hybrid production, shadow, or canary trace package is supplied by public accelerator benchmark updates.",
            "materiality": "preserves_endpoint",
            "directly_calibratable": "no",
            "recommended_action": "preserve_phase2_downgrade",
            "notes": "Public programmable-baseline drift cannot satisfy the Phase 4 hybrid measured-evidence conjunction.",
        },
        {
            "baseline_dimension": "phase4_reopen_path",
            "campaign_assumption": "Actual reopen requires lifecycle-valid measured hybrid evidence against measured best programmable baseline under identical workload accounting.",
            "public_update_observation": "Public MLPerf accelerator results do not include the campaign hybrid path or safety-filter deployment telemetry.",
            "materiality": "not_reopen_evidence",
            "directly_calibratable": "no",
            "recommended_action": "actual_reopen_candidate_count_remains_zero",
            "notes": "Benchmark-only evidence can update baselines but cannot reopen physicalized-superiority claims.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, rows: list[dict[str, str]]) -> None:
    width, height = 960, 420
    pixels = bytearray([249, 250, 251] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            row_base = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                idx = row_base + x * 3
                pixels[idx : idx + 3] = bytes(color)

    weights = {
        "material": 1.0,
        "context_only": 0.55,
        "preserves_endpoint": 0.45,
        "not_reopen_evidence": 0.35,
    }
    colors = {
        "material": (52, 125, 180),
        "context_only": (220, 168, 60),
        "preserves_endpoint": (58, 150, 95),
        "not_reopen_evidence": (120, 130, 145),
    }
    rect(0, 0, width, height, (248, 249, 250))
    left, top, row_h, max_w = 300, 50, 46, 560
    for idx, row in enumerate(rows):
        y = top + idx * row_h
        rect(24, y, width - 24, y + row_h - 6, (255, 255, 255) if idx % 2 == 0 else (241, 245, 248))
        materiality = row["materiality"]
        rect(left, y + 9, left + int(max_w * weights[materiality]), y + row_h - 15, colors[materiality])
        if row["directly_calibratable"] == "no":
            rect(left + max_w + 16, y + 9, left + max_w + 42, y + row_h - 15, (185, 70, 70))
        elif row["directly_calibratable"] == "partial":
            rect(left + max_w + 16, y + 9, left + max_w + 42, y + row_h - 15, (220, 168, 60))
        else:
            rect(left + max_w + 16, y + 9, left + max_w + 42, y + row_h - 15, (58, 150, 95))
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def write_report(summary: dict[str, object], sources: list[dict[str, str]], deltas: list[dict[str, str]]) -> None:
    source_rows = "\n".join(
        f"| {row['source_id']} | [{row['reference_id']}] | {row['release_name']} | {row['publisher']} | {row['publication_date']} | {row['primary_or_secondary']} | {row['machine_readable']} | {row['directly_usable_in_existing_model']} | {row['satisfies_measured_hybrid_reopen']} |"
        for row in sources
    )
    delta_rows_md = "\n".join(
        f"| {row['baseline_dimension']} | {row['materiality']} | {row['directly_calibratable']} | {row['recommended_action']} |"
        for row in deltas
    )
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T21:08:00Z
cycle: 13
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PUBLICBASE-1
---

# Public Baseline Recency Report

## Scope And Method

This probe uses curated official/public sources rather than broad scraping. MLCommons pages and result repositories are primary evidence for public benchmark recency; the vendor page is secondary context for hardware naming and submitted-system interpretation only, not a primary calibration source.

## Latest Official Release

The latest official MLPerf Inference release identified here is {summary['latest_mlperf_inference_release']}, published {summary['latest_mlperf_inference_publication_date']} [11]. It is newer than the campaign's earlier MLPerf documentation reference [10] and newer than the intermediate v5.1 release [12].

## Source Table

| source_id | ref | release | publisher | publication_date | role | machine_readable | directly usable | measured hybrid reopen |
|---|---:|---|---|---|---|---|---|---|
{source_rows}

## Delta Versus Campaign Assumptions

| baseline_dimension | materiality | directly_calibratable | recommended_action |
|---|---|---|---|
{delta_rows_md}

![public programmable-baseline recency and materiality screen against campaign calibrated-baseline assumptions.](../data/public_baseline_delta_matrix.png)

## Calibration Impact

The public update is material enough to recommend a future programmable-baseline refresh, because the latest official MLCommons release and machine-readable v6.0 repository are newer than the campaign reference set and can refresh public accelerator priors. That recommendation is conditional: the public benchmark data are not directly the campaign's safety-filter workload, so they should not be copied into the calibrated model without an explicit mapping to feature extraction, audit, fallback, update cadence, utilization, energy, and latency terms.

## Effect On Phase 2 And Phase 4

The Phase 2 stronger-baseline conclusion is preserved and, if anything, public benchmark drift strengthens the null hypothesis around programmable accelerators. Public accelerator benchmark updates are not measured hybrid production, shadow, or canary evidence; they do not include the campaign hybrid path under identical workload accounting and cannot satisfy the Phase 4 measured hybrid reopen path. Endpoint counters remain zero/false: current_superiority_claim_count=0, actual_reopen_candidate_count=0, new_reopen_gate_count=0, and current_artifacts_reopen=false.
"""
    )


def main() -> None:
    refs = reference_ids()
    sources = curated_sources()
    missing_refs = sorted({row["reference_id"] for row in sources} - refs)
    if missing_refs:
        raise SystemExit(f"Missing REFERENCES.md entries: {', '.join(missing_refs)}")

    stronger = read_json(DATA / "stronger_baseline_summary.json")
    phase2 = read_json(DATA / "phase2_synthesis_summary.json")
    deltas = delta_rows(stronger, phase2)
    material_count = sum(1 for row in deltas if row["materiality"] == "material")
    model_refresh_recommended = any(
        row["recommended_action"] == "future_model_refresh_recommended" and row["materiality"] == "material"
        for row in deltas
    )

    summary = {
        "schema_version": 1,
        "milestone_id": "M-PUBLICBASE-1",
        "status": "validated",
        "latest_mlperf_inference_release": "MLPerf Inference v6.0",
        "latest_mlperf_inference_publication_date": "2026-04-01",
        "latest_mlperf_inference_url": "https://mlcommons.org/2026/04/mlperf-inference-v6-0-results/",
        "newer_than_campaign_reference": True,
        "material_public_baseline_update_count": material_count,
        "outcome": "model_refresh_recommended" if model_refresh_recommended else "baseline_strengthened_no_claim_reopen",
        "model_refresh_recommended": model_refresh_recommended,
        "refresh_scope": "future programmable-baseline prior refresh only; no current physicalized-superiority update",
        "public_sources_reopen_physicalized_claim": False,
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": 0,
        "new_reopen_gate_count": 0,
        "current_artifacts_reopen": False,
        "vendor_only_sources_drive_refresh": False,
        "direct_safety_filter_calibration_available": False,
        "phase2_conclusion_preserved": True,
        "phase4_reopen_path_satisfied": False,
        "source_count": len(sources),
        "primary_source_count": sum(1 for row in sources if row["primary_or_secondary"] == "primary"),
        "machine_readable_primary_source_count": sum(
            1 for row in sources if row["primary_or_secondary"] == "primary" and row["machine_readable"] in {"yes", "linked_repository"}
        ),
        "figure_caption": "public programmable-baseline recency and materiality screen against campaign calibrated-baseline assumptions.",
    }

    write_csv(
        SOURCES_CSV,
        sources,
        [
            "source_id",
            "reference_id",
            "title",
            "publisher",
            "url",
            "publication_date",
            "source_type",
            "primary_or_secondary",
            "machine_readable",
            "release_name",
            "benchmark_suite_workloads",
            "hardware_families_mentioned",
            "directly_usable_in_existing_model",
            "satisfies_measured_hybrid_reopen",
            "notes",
        ],
    )
    write_csv(
        DELTA_CSV,
        deltas,
        [
            "baseline_dimension",
            "campaign_assumption",
            "public_update_observation",
            "materiality",
            "directly_calibratable",
            "recommended_action",
            "notes",
        ],
    )
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    write_png(FIGURE_PNG, deltas)
    write_report(summary, sources, deltas)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
