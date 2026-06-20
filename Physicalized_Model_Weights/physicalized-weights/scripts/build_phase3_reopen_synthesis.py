# created: 2026-05-13T11:48:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PHASE3-SYNTH-1

"""Build the Phase 3 reopen-pathway synthesis package.

This is an aggregation layer over validated Phase 3 gates. It does not create
a new scoring rule; it records the conjunction required for future evidence to
challenge the Phase 2 downgrade and fails if any committed artifact is already
classified as actual reopen evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import zlib
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"

CLAIM_MATRIX_CSV = DATA / "phase3_reopen_claim_matrix.csv"
MANIFEST_CSV = DATA / "phase3_reopen_manifest.csv"
SUMMARY_JSON = DATA / "phase3_reopen_summary.json"
FLOW_PNG = DATA / "phase3_reopen_evidence_flow.png"
REPORT_MD = DOCS / "phase3_reopen_pathway_summary.md"
FINAL_SYNTHESIS_MD = DOCS / "final_synthesis.md"
REPRO_MD = DOCS / "reproducibility.md"
TEST_PATH = ROOT / "physicalized-weights" / "tests" / "test_phase3_reopen_synthesis.py"

FUTURE_REOPEN_CONDITION = (
    "valid_package ∧ hash_match ∧ schema_compatible ∧ known_threshold_scenario ∧ "
    "valid_trace ∧ admissible_ingestion_path ∧ measured_terms ∧ "
    "production_or_shadow_or_canary_source ∧ provenance_attestation ∧ "
    "privacy_attestation ∧ threshold_crossed"
)

PHASE3_COMMANDS = [
    "python3 physicalized-weights/scripts/local_overhead_benchmark.py",
    "python3 physicalized-weights/scripts/production_trace_validator.py physicalized-weights/data/example_production_trace_valid.csv physicalized-weights/data/example_production_trace_invalid.csv",
    "python3 physicalized-weights/scripts/reopen_thresholds.py",
    "wolfram-batch -script physicalized-weights/scripts/symbolic_reopen_thresholds.wls",
    "python3 physicalized-weights/scripts/trace_ingestion_path_evaluator.py",
    "python3 physicalized-weights/scripts/reopen_pipeline_demo.py",
    "python3 physicalized-weights/scripts/evidence_pack_replay.py",
    "python3 physicalized-weights/scripts/build_phase3_reopen_synthesis.py",
]

PHASE3_TEST_COMMANDS = [
    "python3 physicalized-weights/tests/test_local_overhead_benchmark.py",
    "python3 physicalized-weights/tests/test_production_trace_validator.py",
    "python3 physicalized-weights/tests/test_reopen_thresholds.py",
    "python3 physicalized-weights/tests/test_trace_ingestion_path_evaluator.py",
    "python3 physicalized-weights/tests/test_reopen_pipeline_demo.py",
    "python3 physicalized-weights/tests/test_evidence_pack_replay.py",
    "python3 physicalized-weights/tests/test_phase3_reopen_synthesis.py",
]


REQUIRED_INPUTS = {
    "M-MEASURE-1": [
        DATA / "local_overhead_summary.json",
        DATA / "measurement_gap_matrix.csv",
        DOCS / "production_measurement_requirements.md",
    ],
    "M-TRACE-1": [
        DATA / "production_trace_schema.json",
        DATA / "production_trace_validation_summary.json",
        DATA / "production_trace_validation_report.csv",
        DOCS / "production_trace_schema.md",
    ],
    "M-REOPEN-1": [
        DATA / "reopen_thresholds_summary.json",
        DATA / "reopen_thresholds.csv",
        DATA / "symbolic_reopen_thresholds.json",
        DOCS / "reopen_thresholds.md",
    ],
    "M-INGEST-1": [
        DATA / "trace_ingestion_path_summary.json",
        DATA / "trace_ingestion_path_scores.csv",
        DOCS / "trace_ingestion_paths.md",
    ],
    "M-PIPELINE-1": [
        DATA / "reopen_pipeline_summary.json",
        DATA / "reopen_pipeline_results.csv",
        DOCS / "end_to_end_reopen_pipeline.md",
    ],
    "M-EVIDENCEPACK-1": [
        DATA / "evidence_pack_manifest_schema.json",
        DATA / "evidence_pack_replay_summary.json",
        DATA / "evidence_pack_replay_results.csv",
        DOCS / "evidence_pack_replay_harness.md",
    ],
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def require_inputs() -> None:
    missing = [rel(path) for paths in REQUIRED_INPUTS.values() for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing Phase 3 input artifacts: " + ", ".join(missing))


def load_inputs() -> dict[str, Any]:
    require_inputs()
    return {
        "measure": read_json(DATA / "local_overhead_summary.json"),
        "trace": read_json(DATA / "production_trace_validation_summary.json"),
        "reopen": read_json(DATA / "reopen_thresholds_summary.json"),
        "ingest": read_json(DATA / "trace_ingestion_path_summary.json"),
        "pipeline": read_json(DATA / "reopen_pipeline_summary.json"),
        "pipeline_rows": read_csv(DATA / "reopen_pipeline_results.csv"),
        "evidence_pack": read_json(DATA / "evidence_pack_replay_summary.json"),
        "evidence_pack_rows": read_csv(DATA / "evidence_pack_replay_results.csv"),
        "threshold_rows": read_csv(DATA / "reopen_thresholds.csv"),
        "ingestion_rows": read_csv(DATA / "trace_ingestion_path_scores.csv"),
    }


def actual_reopen_count(inputs: dict[str, Any]) -> int:
    total = 0
    total += int(inputs["pipeline"].get("actual_reopen_candidate_count", 0))
    total += int(inputs["evidence_pack"].get("actual_reopen_candidate_count", 0))
    total += int(inputs["ingest"].get("actual_reopened_count", 0))
    total += sum(1 for row in inputs["pipeline_rows"] if row.get("actual_reopen_candidate") == "True")
    total += sum(1 for row in inputs["evidence_pack_rows"] if row.get("actual_reopen_candidate") == "True")
    return total


def guard_non_reopen(inputs: dict[str, Any]) -> None:
    count = actual_reopen_count(inputs)
    if count != 0:
        raise RuntimeError(f"Committed artifacts report {count} actual reopen candidates")

    bad_rows = []
    for row in inputs["pipeline_rows"]:
        source = row.get("evidence_source_type", "")
        measurement = row.get("measurement_status", "")
        if row.get("actual_reopen_candidate") == "True" and (source == "synthetic" or measurement in {"proxy", "local_proxy"}):
            bad_rows.append(row.get("trace_file", "unknown"))
    for row in inputs["evidence_pack_rows"]:
        source = row.get("evidence_source_type", "")
        measurement = row.get("measurement_status", "")
        vendor_only = row.get("ingestion_path_id", "") == "accelerator_vendor_benchmark_only"
        if row.get("actual_reopen_candidate") == "True" and (
            source == "synthetic" or measurement in {"proxy", "local_proxy"} or vendor_only
        ):
            bad_rows.append(row.get("manifest_file", "unknown"))
    if bad_rows:
        raise RuntimeError("Synthetic/proxy/local/vendor-only evidence is marked as reopening: " + ", ".join(bad_rows))


def blocked_classes(inputs: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "evidence_class": "synthetic",
            "blocked_by": "eligible source and ingestion path gates",
            "example_artifact": "physicalized-weights/data/evidence_pack_synthetic_counterfactual_manifest.json",
            "observed_status": "synthetic_counterfactual_crossed",
        },
        {
            "evidence_class": "proxy/local",
            "blocked_by": "measured_terms gate",
            "example_artifact": "physicalized-weights/data/evidence_pack_valid_synthetic_manifest.json",
            "observed_status": "valid_but_insufficient",
        },
        {
            "evidence_class": "vendor-only",
            "blocked_by": "counterfactual workload and admissible ingestion gates",
            "example_artifact": "physicalized-weights/data/trace_ingestion_path_scores.csv",
            "observed_status": "valid_but_insufficient",
        },
        {
            "evidence_class": "privacy-risk",
            "blocked_by": "privacy/schema gate",
            "example_artifact": "physicalized-weights/data/pipeline_trace_invalid_privacy.csv",
            "observed_status": "invalid_trace",
        },
        {
            "evidence_class": "stale-hash",
            "blocked_by": "valid_package and hash_match gates",
            "example_artifact": "physicalized-weights/data/evidence_pack_bad_hash_manifest.json",
            "observed_status": "package_invalid",
        },
        {
            "evidence_class": "unknown-threshold",
            "blocked_by": "known_threshold_scenario gate",
            "example_artifact": "physicalized-weights/scripts/evidence_pack_replay.py",
            "observed_status": "package_invalid before downstream evaluation",
        },
        {
            "evidence_class": "non-crossing measured packages",
            "blocked_by": "threshold_crossed gate",
            "example_artifact": "physicalized-weights/data/evidence_pack_shadow_non_crossing_manifest.json",
            "observed_status": "threshold_evaluable_not_crossed",
        },
    ]


def claim_rows(inputs: dict[str, Any]) -> list[dict[str, str]]:
    classes = blocked_classes(inputs)
    blocked = "; ".join(f"{row['evidence_class']} ({row['blocked_by']})" for row in classes)
    rows = [
        {
            "claim_id": "P3-C1",
            "pathway_stage": "campaign conclusion",
            "current_status": "downgrade_preserved",
            "evidence_class": "current committed artifacts",
            "accepted_or_rejected": "rejected_as_reopen_evidence",
            "required_evidence": FUTURE_REOPEN_CONDITION,
            "blocked_evidence_classes": blocked,
            "artifact_pointers": "physicalized-weights/data/phase3_reopen_summary.json; physicalized-weights/docs/phase3_reopen_pathway_summary.md",
            "conclusion": "No current artifact reopens the Phase 2 downgrade or makes safety/filter physicalization a current performance/economic winner.",
        },
        {
            "claim_id": "P3-C2",
            "pathway_stage": "measurement contract",
            "current_status": "production_required",
            "evidence_class": "local proxy measurements",
            "accepted_or_rejected": "accepted_as_overhead_proxy_only",
            "required_evidence": "measured production accelerator and hybrid latency/energy/utilization under identical workload accounting",
            "blocked_evidence_classes": "proxy/local",
            "artifact_pointers": "physicalized-weights/data/local_overhead_summary.json; physicalized-weights/data/measurement_gap_matrix.csv",
            "conclusion": "M-MEASURE-1 decomposes overheads but cannot reopen the downgraded claim.",
        },
        {
            "claim_id": "P3-C3",
            "pathway_stage": "trace validation",
            "current_status": "schema_guarded",
            "evidence_class": "production traces",
            "accepted_or_rejected": "accepted_only_if_valid_reopen_candidate",
            "required_evidence": "privacy-safe trace with required baselines, measured energy, accepted fast-path credit, and production/shadow/canary environment",
            "blocked_evidence_classes": "privacy-risk; proxy energy; missing baseline; inconsistent policy",
            "artifact_pointers": "physicalized-weights/data/production_trace_schema.json; physicalized-weights/data/production_trace_validation_summary.json",
            "conclusion": "M-TRACE-1 makes schema validity necessary but not sufficient for reopening.",
        },
        {
            "claim_id": "P3-C4",
            "pathway_stage": "quantitative threshold",
            "current_status": "not_crossed_by_current_artifacts",
            "evidence_class": "threshold rows",
            "accepted_or_rejected": "accepted_only_if_measured_margin_positive",
            "required_evidence": "measured_hybrid_total < measured_best_programmable_baseline under identical accounting",
            "blocked_evidence_classes": "zero-volume; all-fallback; unknown-threshold; non-crossing measured packages",
            "artifact_pointers": "physicalized-weights/data/reopen_thresholds_summary.json; physicalized-weights/data/reopen_thresholds.csv",
            "conclusion": "M-REOPEN-1 provides finite thresholds for eight scenarios and unreopenable controls for zero-volume/all-fallback cases.",
        },
        {
            "claim_id": "P3-C5",
            "pathway_stage": "ingestion admissibility",
            "current_status": "admissibility_guarded",
            "evidence_class": "evidence acquisition paths",
            "accepted_or_rejected": "accepted_only_for_dual_measured_production_paths",
            "required_evidence": "privacy-safe dual-run production, shadow, or canary path with measured hybrid and programmable baseline terms",
            "blocked_evidence_classes": "synthetic; vendor-only; sampled logs without baselines; privacy-risk",
            "artifact_pointers": "physicalized-weights/data/trace_ingestion_path_scores.csv; physicalized-weights/data/trace_ingestion_path_summary.json",
            "conclusion": "M-INGEST-1 identifies only shadow production dual-run and canary A/B dual-instrumented paths as future candidate paths.",
        },
        {
            "claim_id": "P3-C6",
            "pathway_stage": "end-to-end gate",
            "current_status": "zero_actual_reopen_candidates",
            "evidence_class": "trace-like artifacts",
            "accepted_or_rejected": "rejected_unless_all_conjuncts_hold",
            "required_evidence": "valid trace, reopen-candidate ingestion path, measured terms, eligible source, provenance attestation, and threshold crossing",
            "blocked_evidence_classes": "synthetic; proxy/local; privacy-risk; non-crossing measured packages",
            "artifact_pointers": "physicalized-weights/data/reopen_pipeline_summary.json; physicalized-weights/data/reopen_pipeline_results.csv",
            "conclusion": "M-PIPELINE-1 keeps synthetic numeric threshold crossing from becoming actual reopen evidence.",
        },
        {
            "claim_id": "P3-C7",
            "pathway_stage": "evidence-pack replay",
            "current_status": "zero_actual_reopen_candidates",
            "evidence_class": "manifested evidence packs",
            "accepted_or_rejected": "rejected_unless_package_and_downstream_gates_pass",
            "required_evidence": FUTURE_REOPEN_CONDITION,
            "blocked_evidence_classes": "stale-hash; missing attestation; unknown-threshold; synthetic; proxy/local; non-crossing measured packages",
            "artifact_pointers": "physicalized-weights/data/evidence_pack_replay_summary.json; physicalized-weights/data/evidence_pack_replay_results.csv",
            "conclusion": "M-EVIDENCEPACK-1 rejects malformed packages before threshold evaluation and preserves zero current actual reopen candidates.",
        },
    ]
    for blocked_row in classes:
        rows.append(
            {
                "claim_id": f"P3-BLOCK-{blocked_row['evidence_class'].replace('/', '-').replace(' ', '-').upper()}",
                "pathway_stage": "blocked evidence class",
                "current_status": "blocked",
                "evidence_class": blocked_row["evidence_class"],
                "accepted_or_rejected": "rejected_as_current_reopen_evidence",
                "required_evidence": FUTURE_REOPEN_CONDITION,
                "blocked_evidence_classes": blocked_row["blocked_by"],
                "artifact_pointers": blocked_row["example_artifact"],
                "conclusion": f"{blocked_row['evidence_class']} evidence remains blocked: {blocked_row['observed_status']}.",
            }
        )
    return rows


def manifest_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for milestone, paths in REQUIRED_INPUTS.items():
        for path in paths:
            rows.append(
                {
                    "milestone_id": milestone,
                    "artifact_path": rel(path),
                    "artifact_sha256": sha256(path),
                    "artifact_role": "input",
                    "replay_command": "",
                }
            )
    for path in [Path(__file__).resolve(), TEST_PATH, CLAIM_MATRIX_CSV, SUMMARY_JSON, FLOW_PNG, REPORT_MD, FINAL_SYNTHESIS_MD, REPRO_MD]:
        role = "output" if path in {CLAIM_MATRIX_CSV, SUMMARY_JSON, FLOW_PNG, REPORT_MD} else "canonical_report"
        if path == Path(__file__).resolve() or path == TEST_PATH:
            role = "implementation"
        rows.append(
            {
                "milestone_id": "M-PHASE3-SYNTH-1",
                "artifact_path": rel(path),
                "artifact_sha256": sha256(path) if path.exists() else "",
                "artifact_role": role,
                "replay_command": "python3 physicalized-weights/scripts/build_phase3_reopen_synthesis.py",
            }
        )
    return rows


def write_claim_matrix(rows: list[dict[str, str]]) -> None:
    fields = [
        "claim_id",
        "pathway_stage",
        "current_status",
        "evidence_class",
        "accepted_or_rejected",
        "required_evidence",
        "blocked_evidence_classes",
        "artifact_pointers",
        "conclusion",
    ]
    with CLAIM_MATRIX_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_manifest() -> None:
    rows = manifest_rows()
    fields = ["milestone_id", "artifact_path", "artifact_sha256", "artifact_role", "replay_command"]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_png(path: Path, rows: list[dict[str, str]]) -> None:
    width, height = 980, 500
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
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

    stages = [
        "M-MEASURE-1",
        "M-TRACE-1",
        "M-REOPEN-1",
        "M-INGEST-1",
        "M-PIPELINE-1",
        "M-EVIDENCEPACK-1",
        "M-PHASE3-SYNTH-1",
    ]
    colors = [
        (83, 126, 185),
        (80, 150, 112),
        (204, 132, 65),
        (141, 102, 178),
        (76, 145, 158),
        (174, 90, 92),
        (72, 72, 72),
    ]
    points = [(85 + i * 135, 155 + (i % 2) * 70) for i in range(len(stages))]
    rect(45, 60, 935, 370, (241, 243, 246))
    for left, right in zip(points, points[1:]):
        line(left[0], left[1], right[0], right[1], (170, 176, 185))
    for idx, (x, y) in enumerate(points):
        rect(x - 42, y - 28, x + 42, y + 28, colors[idx])
        rect(x - 34, y - 20, x + 34, y + 20, (255, 255, 255))
        rect(x - 25, y - 12, x + 25, y + 12, colors[idx])
    blocked_count = sum(1 for row in rows if row["pathway_stage"] == "blocked evidence class")
    rect(100, 420 - blocked_count * 22, 250, 420, (174, 90, 92))
    rect(330, 420 - 7 * 22, 480, 420, (72, 72, 72))
    rect(560, 420 - 1 * 22, 710, 420, (80, 150, 112))
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def build_summary(inputs: dict[str, Any], rows: list[dict[str, str]]) -> dict[str, Any]:
    class_counts = Counter(row["evidence_class"] for row in rows if row["pathway_stage"] == "blocked evidence class")
    return {
        "schema_version": 1,
        "milestone_id": "M-PHASE3-SYNTH-1",
        "status": "validated",
        "central_conclusion": "Current evidence remains downgraded; physicalized safety/filter is not a current performance/economic winner against the strong programmable accelerator baseline.",
        "actual_reopen_candidate_count": actual_reopen_count(inputs),
        "current_artifacts_reopen": False,
        "future_reopen_condition": FUTURE_REOPEN_CONDITION,
        "integrated_milestones": list(REQUIRED_INPUTS.keys()),
        "claim_count": len(rows),
        "blocked_evidence_classes": sorted(class_counts),
        "pipeline_final_status_counts": inputs["pipeline"].get("final_status_counts", {}),
        "evidence_pack_final_decision_counts": inputs["evidence_pack"].get("final_package_decision_counts", {}),
        "reopen_threshold_evidence_status": inputs["reopen"].get("evidence_status", ""),
        "ingestion_actual_reopened_count": inputs["ingest"].get("actual_reopened_count", 0),
        "figure_caption": "Phase 3 evidence chain from measurement requirements through evidence-pack replay, showing that all current committed artifacts preserve the Phase 2 downgrade and only a measured eligible threshold-crossing package can reopen.",
    }


def write_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    gate_lines = "\n".join(
        f"- `{row['claim_id']}`: {row['conclusion']}"
        for row in rows
        if row["claim_id"].startswith("P3-C")
    )
    blocked_lines = "\n".join(
        f"- `{row['evidence_class']}`: {row['blocked_evidence_classes']}; example `{row['artifact_pointers']}`."
        for row in rows
        if row["pathway_stage"] == "blocked evidence class"
    )
    commands = "\n".join(PHASE3_COMMANDS)
    tests = "\n".join(PHASE3_TEST_COMMANDS)
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T11:48:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-PHASE3-SYNTH-1
---

# Phase 3 Reopen-Pathway Summary

Phase 3 closes the reopen evidence pathway without reopening the Phase 2 downgrade. The integrated result is explicit: current evidence remains downgraded, and physicalized safety/filter is not a current performance/economic winner over the strong programmable accelerator baseline.

The future reopen condition is conjunctive:

```text
{FUTURE_REOPEN_CONDITION}
```

No current committed artifact satisfies that conjunction. The current `actual_reopen_candidate_count` is `{summary['actual_reopen_candidate_count']}` across the end-to-end gate and evidence-pack replay layers.

![Phase 3 evidence chain from measurement requirements through evidence-pack replay, showing that all current committed artifacts preserve the Phase 2 downgrade and only a measured eligible threshold-crossing package can reopen.](../data/phase3_reopen_evidence_flow.png)

## Integrated Gate Chain

{gate_lines}

## Blocked Evidence Classes

{blocked_lines}

## Replay From One Place

Run these commands from `<workspace>` to reproduce the Phase 3 chain:

```bash
{commands}
```

Then run:

```bash
{tests}
file physicalized-weights/data/phase3_reopen_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```

## Interpretation

The accepted future class is narrow: a replayable package with integrity-matched traces, schema compatibility, known threshold scenario, valid trace status, admissible ingestion path, measured terms, eligible production/shadow/canary source, provenance and privacy attestations, and a measured threshold crossing. Synthetic counterfactuals, proxy/local measurements, vendor-only benchmarks, privacy-risk traces, stale hashes, unknown thresholds, and non-crossing measured packages are useful diagnostics, but they cannot challenge the Phase 2 downgrade.
""",
        encoding="utf-8",
    )


def replace_section(text: str, heading: str, section: str) -> str:
    marker = f"\n## {heading}\n"
    if marker not in text:
        return text.rstrip() + "\n" + marker + "\n" + section.strip() + "\n"
    start = text.index(marker) + 1
    next_start = text.find("\n## ", start + len(marker))
    if next_start == -1:
        return text[:start] + f"## {heading}\n\n" + section.strip() + "\n"
    return text[:start] + f"## {heading}\n\n" + section.strip() + "\n" + text[next_start:]


def update_final_synthesis(summary: dict[str, Any]) -> None:
    text = FINAL_SYNTHESIS_MD.read_text(encoding="utf-8")
    section = f"""Phase 3 integrates the production measurement contract, production trace schema, quantitative reopen thresholds, ingestion-path admissibility, end-to-end reopen gate, and replayable evidence-pack manifest into one canonical pathway. The result preserves the Phase 2 conclusion: current evidence remains downgraded, and physicalized safety/filter is not a current performance/economic winner.

The current committed Phase 3 artifacts report `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`. Synthetic threshold crossings, proxy/local measurements, vendor-only benchmark paths, privacy-risk traces, stale hashes, unknown threshold scenarios, and non-crossing measured packages are represented as blocked evidence classes in `physicalized-weights/data/phase3_reopen_claim_matrix.csv`.

Future reopening requires exactly this conjunction:

```text
{FUTURE_REOPEN_CONDITION}
```

The generated Phase 3 report is `physicalized-weights/docs/phase3_reopen_pathway_summary.md`, the manifest is `physicalized-weights/data/phase3_reopen_manifest.csv`, and the compact summary is `physicalized-weights/data/phase3_reopen_summary.json`."""
    FINAL_SYNTHESIS_MD.write_text(replace_section(text, "Phase 3 Reopen-Pathway Addendum", section), encoding="utf-8")


def update_reproducibility() -> None:
    text = REPRO_MD.read_text(encoding="utf-8")
    commands = "\n".join(PHASE3_COMMANDS)
    tests = "\n".join(PHASE3_TEST_COMMANDS)
    section = f"""The Phase 3 closure package is replayed in dependency order so a reader can reproduce the non-reopen conclusion from one command block:

```bash
{commands}
```

Expected non-reopen outcomes:

- `physicalized-weights/data/reopen_pipeline_summary.json` keeps `actual_reopen_candidate_count` at `0`.
- `physicalized-weights/data/evidence_pack_replay_summary.json` keeps `actual_reopen_candidate_count` at `0`.
- `physicalized-weights/data/phase3_reopen_summary.json` reports `current_artifacts_reopen: false`.
- `physicalized-weights/data/phase3_reopen_claim_matrix.csv` includes blocked classes for synthetic, proxy/local, vendor-only, privacy-risk, stale-hash, unknown-threshold, and non-crossing measured packages.

Validation:

```bash
{tests}
file physicalized-weights/data/phase3_reopen_evidence_flow.png
python3 -m long_exposure.tools.promise_check .
python3 -m long_exposure.tools.org_check .
```"""
    REPRO_MD.write_text(replace_section(text, "Phase 3 Reopen Pathway Replay", section), encoding="utf-8")


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    inputs = load_inputs()
    guard_non_reopen(inputs)
    rows = claim_rows(inputs)
    write_claim_matrix(rows)
    write_png(FLOW_PNG, rows)
    summary = build_summary(inputs, rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(summary, rows)
    update_final_synthesis(summary)
    update_reproducibility()
    write_manifest()

    print(f"wrote {CLAIM_MATRIX_CSV}")
    print(f"wrote {MANIFEST_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {FLOW_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"updated {FINAL_SYNTHESIS_MD}")
    print(f"updated {REPRO_MD}")
    print("actual_reopen_candidate_count:", summary["actual_reopen_candidate_count"])
    print("blocked_evidence_classes:", ", ".join(summary["blocked_evidence_classes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
