# created: 2026-05-13T21:44:00Z
# cycle: 14
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-2
"""Map primary MLPerf v6.0 public results to campaign baseline priors.

This is a conservative programmable-baseline refresh. Public MLPerf rows can
update directional priors for programmable systems, but they are not measured
hybrid safety-filter production/shadow/canary evidence.
"""

from __future__ import annotations

import csv
import json
import re
import struct
import urllib.error
import urllib.request
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "physicalized-weights"
DATA = BASE / "data"
DOCS = BASE / "docs"
REFERENCES = ROOT / "REFERENCES.md"

SOURCE_TABLE = DATA / "public_baseline_sources.csv"
STRONGER_BASELINE = DATA / "stronger_baseline_summary.json"
PHASE2_SUMMARY = DATA / "phase2_synthesis_summary.json"

MLPERF_SUMMARY_URL = "https://raw.githubusercontent.com/mlcommons/inference_results_v6.0/main/summary_results.json"
MLPERF_REPO_URL = "https://github.com/mlcommons/inference_results_v6.0"

SUBSET_CSV = DATA / "public_baseline_mlperf_v6_subset.csv"
MAPPING_CSV = DATA / "public_baseline_campaign_mapping.csv"
REFRESH_CSV = DATA / "public_baseline_prior_refresh.csv"
SUMMARY_JSON = DATA / "public_baseline_prior_refresh_summary.json"
FIGURE_PNG = DATA / "public_baseline_prior_refresh.png"
REPORT_MD = DOCS / "public_baseline_prior_refresh.md"


SUBSET_FIELDS = [
    "source_row_id",
    "id",
    "submitter",
    "category",
    "suite",
    "mlperf_benchmark",
    "scenario",
    "system",
    "hardware_family",
    "accelerator",
    "total_accelerators",
    "performance_result",
    "performance_unit",
    "has_power",
    "power_or_energy_metric",
    "source_file",
    "source_url",
]

MAPPING_FIELDS = [
    "source_row_id",
    "mlperf_benchmark",
    "scenario",
    "hardware_family",
    "campaign_dimension",
    "mapping_strength",
    "directly_calibratable",
    "calibration_blocker",
    "recommended_use",
    "notes",
]

REFRESH_FIELDS = [
    "model_term",
    "phase2_assumption",
    "public_baseline_observation",
    "refresh_action",
    "directional_effect_on_null",
    "directional_effect_on_hybrid_margin",
    "evidence_level",
    "notes",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def reference_ids() -> set[str]:
    text = REFERENCES.read_text()
    return set(re.findall(r"^\[(\d+)\]", text, flags=re.MULTILINE))


def primary_v60_source() -> dict[str, str]:
    rows = read_csv(SOURCE_TABLE)
    for row in rows:
        if row["source_id"] == "mlperf_inference_v60_repository":
            if row["primary_or_secondary"] != "primary":
                raise AssertionError("MLCommons v6.0 repository source is not marked primary")
            return row
    raise AssertionError("M-PUBLICBASE-1 source table lacks mlperf_inference_v60_repository")


def fetch_mlperf_summary() -> tuple[list[dict[str, Any]], str]:
    try:
        with urllib.request.urlopen(MLPERF_SUMMARY_URL, timeout=30) as handle:
            return json.load(handle), "ok"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return [], f"source_unavailable: {type(exc).__name__}: {exc}"


def hardware_family(accelerator: str, system: str) -> str:
    text = f"{accelerator} {system}".lower()
    if "mi" in text or "amd" in text:
        return "AMD Instinct accelerator"
    if "nvidia" in text or "gb" in text or "h100" in text or "h200" in text or "b200" in text:
        return "NVIDIA datacenter accelerator"
    if "tpu" in text or "google" in text:
        return "Google TPU accelerator"
    if "cpu" in text and not accelerator:
        return "CPU software/runtime"
    return "programmable accelerator"


def choose_subset(rows: list[dict[str, Any]], limit: int = 12) -> list[dict[str, str]]:
    chosen: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    candidates = [
        row
        for row in rows
        if row.get("version") == "v6.0"
        and row.get("Suite") == "datacenter"
        and row.get("Category") in {"closed", "open"}
        and row.get("Performance_Result") not in ("", None)
    ]
    scenario_order = {"Server": 0, "Offline": 1, "Interactive": 2, "SingleStream": 3, "MultiStream": 4}
    candidates.sort(
        key=lambda r: (
            str(r.get("Model")),
            scenario_order.get(str(r.get("Scenario")), 99),
            str(r.get("Submitter")),
            -float(r.get("Performance_Result") or 0),
        )
    )

    def add_row(row: dict[str, Any]) -> None:
        family = hardware_family(str(row.get("Accelerator", "")), str(row.get("System", "")))
        key = (str(row.get("Model")), str(row.get("Scenario")), family, str(row.get("Submitter")))
        if key in seen or len(chosen) >= limit:
            return
        seen.add(key)
        source_row_id = f"mlperf_v60_{len(chosen) + 1:02d}"
        has_power = bool(row.get("has_power"))
        chosen.append(
            {
                "source_row_id": source_row_id,
                "id": str(row.get("ID", "")),
                "submitter": str(row.get("Submitter", "")),
                "category": str(row.get("Category", "")),
                "suite": str(row.get("Suite", "")),
                "mlperf_benchmark": str(row.get("Model") or row.get("UsedModel") or ""),
                "scenario": str(row.get("Scenario", "")),
                "system": str(row.get("System", "")),
                "hardware_family": family,
                "accelerator": str(row.get("Accelerator", "")),
                "total_accelerators": str(row.get("Total Accelerators", "")),
                "performance_result": str(row.get("Performance_Result", "")),
                "performance_unit": str(row.get("Performance_Units", "")),
                "has_power": str(has_power).lower(),
                "power_or_energy_metric": "explicit_power_present" if has_power else "",
                "source_file": "summary_results.json",
                "source_url": MLPERF_SUMMARY_URL,
            }
        )

    for scenario in ["Server", "Offline", "Interactive"]:
        for row in candidates:
            if row.get("Scenario") == scenario:
                add_row(row)
                if len([r for r in chosen if r["scenario"] == scenario]) >= 4:
                    break
    for row in candidates:
        add_row(row)
        if len(chosen) >= limit:
            break
    return chosen


def build_mapping(subset: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in subset:
        throughput_calibratable = "partial" if row["performance_result"] and row["performance_unit"] else "no"
        rows.extend(
            [
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "programmable_accelerator_throughput_prior",
                    "mapping_strength": "medium",
                    "directly_calibratable": throughput_calibratable,
                    "calibration_blocker": "benchmark throughput is not identical safety-filter request accounting",
                    "recommended_use": "bounded_prior_refresh",
                    "notes": f"Use {row['performance_result']} {row['performance_unit']} as public programmable-system strength context only.",
                },
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "programmable_accelerator_energy_prior",
                    "mapping_strength": "none" if row["has_power"] == "false" else "weak",
                    "directly_calibratable": "no" if row["has_power"] == "false" else "partial",
                    "calibration_blocker": "not_directly_energy_calibratable" if row["has_power"] == "false" else "power field still not campaign per-request energy",
                    "recommended_use": "do_not_update_energy" if row["has_power"] == "false" else "manual_review_required",
                    "notes": "No energy value inferred from throughput-only evidence.",
                },
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "software_runtime_prior",
                    "mapping_strength": "weak",
                    "directly_calibratable": "no",
                    "calibration_blocker": "submitted system includes full benchmark stack, not isolated campaign software-runtime path",
                    "recommended_use": "qualitative_context_only",
                    "notes": "Useful for public runtime maturity context, not direct M-SWBASE-2 replacement.",
                },
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "workload_comparability",
                    "mapping_strength": "weak",
                    "directly_calibratable": "no",
                    "calibration_blocker": "MLPerf benchmark workload differs from safety-filter feature/audit/fallback/update accounting",
                    "recommended_use": "state_non_comparability",
                    "notes": "Scenario labels such as Server or Offline are useful structure, not workload identity.",
                },
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "direct_energy_calibration_usable",
                    "mapping_strength": "none",
                    "directly_calibratable": "no",
                    "calibration_blocker": "no explicit comparable energy-per-request field in selected primary rows",
                    "recommended_use": "block_direct_energy_update",
                    "notes": "Energy calibration remains unchanged until explicit comparable power/energy plus workload accounting exists.",
                },
                {
                    "source_row_id": row["source_row_id"],
                    "mlperf_benchmark": row["mlperf_benchmark"],
                    "scenario": row["scenario"],
                    "hardware_family": row["hardware_family"],
                    "campaign_dimension": "safety_filter_workload_comparable",
                    "mapping_strength": "none",
                    "directly_calibratable": "no",
                    "calibration_blocker": "not the campaign safety-filter production/shadow/canary workload",
                    "recommended_use": "no_hybrid_reopen_credit",
                    "notes": "Does not supply measured hybrid total H or measured best programmable baseline under identical safety-filter workload.",
                },
            ]
        )
    return rows


def build_refresh_rows(subset: list[dict[str, str]], mapping: list[dict[str, str]], stronger: dict[str, Any], phase2: dict[str, Any]) -> list[dict[str, str]]:
    throughput_rows = [r for r in mapping if r["campaign_dimension"] == "programmable_accelerator_throughput_prior" and r["directly_calibratable"] == "partial"]
    energy_rows = [r for r in mapping if r["campaign_dimension"] == "programmable_accelerator_energy_prior" and r["directly_calibratable"] != "no"]
    return [
        {
            "model_term": "programmable_accelerator_throughput_prior",
            "phase2_assumption": f"M-SWBASE-2 winner counts: {stronger['winner_counts']}",
            "public_baseline_observation": f"{len(throughput_rows)} primary MLCommons v6.0 subset rows expose performance results and units across public datacenter scenarios.",
            "refresh_action": "strengthen_programmable_null" if throughput_rows else "not_calibratable_from_public_data",
            "directional_effect_on_null": "strengthens_or_preserves_programmable_baseline",
            "directional_effect_on_hybrid_margin": "less_favorable_to_physicalized_hybrid",
            "evidence_level": "primary_public_benchmark_prior",
            "notes": "Use only as bounded prior context because workload/accounting is not identical.",
        },
        {
            "model_term": "programmable_accelerator_energy_prior",
            "phase2_assumption": "M-SWBASE-2 uses explicit-unit pJ-equivalent proxy terms under identical campaign workload assumptions.",
            "public_baseline_observation": f"{len(energy_rows)} selected primary rows have explicit power/energy fields usable for partial review; throughput-only rows are not converted into energy.",
            "refresh_action": "not_calibratable_from_public_data" if not energy_rows else "requires_future_manual_model_refresh",
            "directional_effect_on_null": "preserve_existing_energy_prior",
            "directional_effect_on_hybrid_margin": "unchanged",
            "evidence_level": "blocked_direct_energy_calibration",
            "notes": "No energy-per-request value is inferred from throughput-only MLPerf evidence.",
        },
        {
            "model_term": "software_runtime_prior",
            "phase2_assumption": "Optimized software runtime wins the zero-invocation control and is charged under the same feature/audit workload.",
            "public_baseline_observation": "MLPerf rows include full submitted systems and software stacks, not isolated optimized software-only safety-filter measurements.",
            "refresh_action": "preserve_phase2_baseline",
            "directional_effect_on_null": "preserves_null",
            "directional_effect_on_hybrid_margin": "unchanged",
            "evidence_level": "qualitative_context_only",
            "notes": "Do not replace the campaign software-runtime term from public benchmark system rows.",
        },
        {
            "model_term": "safety_filter_workload_comparability",
            "phase2_assumption": phase2["reopening_standard"],
            "public_baseline_observation": "The primary public rows are benchmark scenarios, not lifecycle-valid measured hybrid safety-filter packages.",
            "refresh_action": "preserve_phase2_baseline",
            "directional_effect_on_null": "preserves_reopen_blocker",
            "directional_effect_on_hybrid_margin": "unchanged",
            "evidence_level": "non_comparable_workload",
            "notes": "No row supplies measured hybrid total H, accepted fast-path volume, fallback/audit accounting, or Phase 4 lifecycle attestations.",
        },
        {
            "model_term": "phase2_stronger_baseline_downgrade",
            "phase2_assumption": phase2["central_conclusion"],
            "public_baseline_observation": "Public programmable-system throughput evidence can only preserve or strengthen B; no measured hybrid evidence changes H.",
            "refresh_action": "strengthen_programmable_null" if throughput_rows else "preserve_phase2_baseline",
            "directional_effect_on_null": "strengthens_or_preserves_programmable_null",
            "directional_effect_on_hybrid_margin": "less_favorable_or_unchanged_for_physicalized_hybrid",
            "evidence_level": "conservative_directional_refresh",
            "notes": "The Phase 2 downgrade remains preserved and is directionally strengthened where public throughput priors are considered.",
        },
    ]


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, summary: dict[str, Any]) -> None:
    width, height = 960, 420
    pixels = bytearray([248, 249, 250] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            base = y * width * 3
            for x in range(max(0, x0), min(width, x1)):
                pixels[base + x * 3 : base + x * 3 + 3] = bytes(color)

    rect(0, 0, width, height, (248, 249, 250))
    bars = [
        ("primary_mlcommons_rows_ingested", (48, 116, 176)),
        ("throughput_prior_rows", (60, 150, 95)),
        ("direct_energy_calibration_rows", (185, 70, 70)),
        ("safety_filter_direct_workload_rows", (185, 70, 70)),
    ]
    max_value = max(1, int(summary.get("primary_mlcommons_rows_ingested", 0)))
    for idx, (key, color) in enumerate(bars):
        y = 60 + idx * 72
        value = int(summary.get(key, 0))
        rect(40, y, 920, y + 48, (255, 255, 255))
        rect(290, y + 12, 290 + int(560 * value / max_value), y + 36, color)
        if value == 0:
            rect(290, y + 12, 314, y + 36, color)
    if summary["phase2_downgrade_preserved"]:
        rect(40, 350, 920, 382, (58, 150, 95))
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def write_report(summary: dict[str, Any], subset: list[dict[str, str]], mapping: list[dict[str, str]], refresh: list[dict[str, str]], source_status: str) -> None:
    source_lines = [
        "- Primary MLCommons source: [13] `inference_results_v6.0` `summary_results.json`.",
        "- Prior source-screen input: `physicalized-weights/data/public_baseline_sources.csv`; vendor rows remain secondary and are not used for calibration.",
        f"- Source fetch status: `{source_status}`.",
    ]
    subset_lines = "\n".join(
        f"| {r['source_row_id']} | {r['mlperf_benchmark']} | {r['scenario']} | {r['submitter']} | {r['hardware_family']} | {r['performance_result']} {r['performance_unit']} | {r['has_power']} |"
        for r in subset
    )
    if not subset_lines:
        subset_lines = "| source_unavailable | n/a | n/a | n/a | n/a | n/a | false |"
    refresh_lines = "\n".join(
        f"| {r['model_term']} | {r['refresh_action']} | {r['directional_effect_on_null']} | {r['evidence_level']} |"
        for r in refresh
    )
    direct_blocks = sorted({r["calibration_blocker"] for r in mapping if r["directly_calibratable"] == "no"})
    blocker_lines = "\n".join(f"- {b}" for b in direct_blocks)
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T21:44:00Z
cycle: 14
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PUBLICBASE-2
---

# Public Baseline Prior Refresh

## Source List
{chr(10).join(source_lines)}

## MLPerf Result Fields Used
The script reads `ID`, `Submitter`, `Category`, `Suite`, `System`, `Model`, `Scenario`, `Accelerator`, `Total Accelerators`, `Performance_Result`, `Performance_Units`, `has_power`, and source location fields from primary MLCommons v6.0 result metadata.

| row | benchmark | scenario | submitter | hardware family | performance | has power |
|---|---|---|---|---|---|---|
{subset_lines}

## Mapping To Campaign Terms
The mapping table covers programmable accelerator throughput priors, programmable accelerator energy priors, software-runtime priors, workload comparability, direct energy calibration usability, and safety-filter workload comparability. Throughput rows are bounded public priors only; they are not identical campaign workload measurements.

## Explicit Non-Mappings
{blocker_lines}
- No row supplies a lifecycle-valid evidence pack, measured hybrid total, accepted fast-path volume, fallback/audit/update accounting, provenance attestation, and privacy attestation.
- No energy value is inferred from throughput-only MLPerf evidence.

## Refresh Decision
| model term | action | null effect | evidence |
|---|---|---|---|
{refresh_lines}

The conservative decision is `{summary['refresh_decision']}` with programmable-null effect `{summary['programmable_null_effect']}`. Phase 2 remains preserved because public MLPerf rows can affect only public programmable-baseline priors `B`, not the measured hybrid total `H`; these rows are not measured hybrid safety-filter production/shadow/canary evidence.

![conservative mapping from public MLPerf v6.0 programmable-baseline evidence to campaign model terms and directional effect on the null hypothesis.](../data/public_baseline_prior_refresh.png)

## Reproduction Commands
```bash
python3 physicalized-weights/scripts/public_baseline_prior_refresh.py
python3 physicalized-weights/tests/test_public_baseline_prior_refresh.py
file physicalized-weights/data/public_baseline_prior_refresh.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```
""",
        encoding="utf-8",
    )


def main() -> dict[str, Any]:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    refs = reference_ids()
    if "13" not in refs:
        raise AssertionError("REFERENCE [13] is required for the MLCommons v6.0 primary repository")
    source = primary_v60_source()
    if source["primary_or_secondary"] != "primary" or source["publisher"] != "MLCommons":
        raise AssertionError("Primary calibration must use MLCommons source rows")

    stronger = read_json(STRONGER_BASELINE)
    phase2 = read_json(PHASE2_SUMMARY)
    raw_rows, source_status = fetch_mlperf_summary()
    subset = choose_subset(raw_rows)
    mapping = build_mapping(subset)
    refresh = build_refresh_rows(subset, mapping, stronger, phase2)

    direct_energy_rows = sum(
        1 for row in mapping if row["campaign_dimension"] == "programmable_accelerator_energy_prior" and row["directly_calibratable"] != "no"
    )
    throughput_rows = sum(
        1 for row in mapping if row["campaign_dimension"] == "programmable_accelerator_throughput_prior" and row["directly_calibratable"] == "partial"
    )
    safety_rows = sum(
        1 for row in mapping if row["campaign_dimension"] == "safety_filter_workload_comparable" and row["directly_calibratable"] != "no"
    )
    refresh_decision = "strengthen_programmable_null" if throughput_rows else "not_calibratable_from_public_data"
    summary: dict[str, Any] = {
        "schema_version": 1,
        "milestone_id": "M-PUBLICBASE-2",
        "status": "validated" if subset else "source_unavailable",
        "primary_source_reference_id": "13",
        "primary_source_url": MLPERF_REPO_URL,
        "primary_summary_url": MLPERF_SUMMARY_URL,
        "source_status": source_status,
        "primary_mlcommons_rows_ingested": len(subset),
        "raw_primary_rows_available": len(raw_rows),
        "direct_energy_calibration_rows": direct_energy_rows,
        "throughput_prior_rows": throughput_rows,
        "safety_filter_direct_workload_rows": safety_rows,
        "refresh_decision": refresh_decision,
        "programmable_null_effect": "strengthened_or_preserved" if throughput_rows else "preserved_no_direct_refresh",
        "phase2_downgrade_preserved": True,
        "public_sources_reopen_physicalized_claim": False,
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": 0,
        "new_reopen_gate_count": 0,
        "current_artifacts_reopen": False,
        "vendor_secondary_rows_used_for_primary_calibration": 0,
        "energy_values_inferred_from_throughput_only": 0,
        "figure_caption": "conservative mapping from public MLPerf v6.0 programmable-baseline evidence to campaign model terms and directional effect on the null hypothesis.",
    }

    write_csv(SUBSET_CSV, subset, SUBSET_FIELDS)
    write_csv(MAPPING_CSV, mapping, MAPPING_FIELDS)
    write_csv(REFRESH_CSV, refresh, REFRESH_FIELDS)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_png(FIGURE_PNG, summary)
    write_report(summary, subset, mapping, refresh, source_status)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
