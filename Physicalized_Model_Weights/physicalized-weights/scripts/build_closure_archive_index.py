# created: 2026-05-13T19:36:00Z
# cycle: 10
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ARCHIVE-1
"""Build a closure artifact archive and reproducibility index.

This is archive infrastructure only. It must preserve the existing closure
state and must not add a scientific evaluator, reopen gate, or evidence path.
"""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"
SCRIPTS = ROOT / "physicalized-weights" / "scripts"
TESTS = ROOT / "physicalized-weights" / "tests"
HDL = ROOT / "physicalized-weights" / "hdl"

REPORT_MD = DOCS / "closure_archive_index.md"
MANIFEST_CSV = DATA / "closure_archive_manifest.csv"
MANIFEST_JSON = DATA / "closure_archive_manifest.json"
SUMMARY_JSON = DATA / "closure_archive_summary.json"
COVERAGE_PNG = DATA / "closure_archive_coverage.png"

FIGURE_CAPTION = "Archive coverage by milestone and artifact class, showing canonical closure/campaign artifacts present versus missing."

COMMANDS = [
    "python3 physicalized-weights/scripts/build_closure_archive_index.py",
    "python3 physicalized-weights/tests/test_closure_archive_index.py",
    "file physicalized-weights/data/closure_archive_coverage.png",
    "python3 -m long_exposure.tools.promise_check .",
    "python3 -m long_exposure.tools.org_check .",
]

KNOWN_WARNINGS = [
    {
        "warning_id": "orphan_cycle_reports",
        "source": "promise_check",
        "scope": "reports/cycles/report_cycles_*",
        "classification": "pre_existing_noncanonical",
        "note": "Generated cycle reports are outside the curated closure archive and remain non-blocking.",
    },
    {
        "warning_id": "root_prompt_and_log",
        "source": "org_check",
        "scope": "physicalized_model_weights_long_exposure_prompt.md; physicalized_weights_long_exposure_live.log",
        "classification": "pre_existing_noncanonical",
        "note": "The original prompt and live log remain root-level directive artifacts and are not archive failures.",
    },
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def row(path: Path, milestone: str, artifact_class: str, command: str = "", notes: str = "") -> dict[str, str]:
    return {
        "artifact_path": rel(path),
        "milestone_id": milestone,
        "artifact_class": artifact_class,
        "canonical": "true",
        "regeneration_command": command,
        "notes": notes,
    }


CANONICAL_ARTIFACTS: list[dict[str, str]] = [
    row(DOCS / "taxonomy_and_null.md", "M-TAX-1", "report"),
    row(DATA / "breakeven_summary.json", "M-MODEL-1", "summary_data", "python3 physicalized-weights/scripts/breakeven_model.py"),
    row(DATA / "target_scores_summary.json", "M-TARGET-1", "summary_data", "python3 physicalized-weights/scripts/target_scoring.py"),
    row(DOCS / "target_ranking.md", "M-TARGET-1", "report"),
    row(DOCS / "hybrid_safety_filter_architecture.md", "M-ARCH-1", "report"),
    row(DATA / "hybrid_arch_summary.json", "M-ARCH-1", "summary_data", "python3 physicalized-weights/scripts/fallback_policy_sim.py"),
    row(DATA / "prototype_verification_closure.json", "M-PROTO-1", "summary_data", "python3 physicalized-weights/scripts/verify_prototype_closure.py"),
    row(DATA / "hdl_sim_results.csv", "M-PROTO-1", "evidence_data", "python3 physicalized-weights/hdl/run_yosys_eval.py"),
    row(DOCS / "prototype_verification_closure.md", "M-PROTO-1", "report"),
    row(HDL / "safety_filter_core.sv", "M-PROTO-1", "hdl_source"),
    row(DATA / "safety_filter_core_netlist.png", "M-PROTO-1", "figure"),
    row(DOCS / "final_synthesis.md", "M-FINAL-1", "report", "python3 physicalized-weights/scripts/build_final_synthesis.py"),
    row(DOCS / "reproducibility.md", "M-FINAL-1", "report", "python3 physicalized-weights/scripts/build_final_synthesis.py"),
    row(DATA / "calibrated_breakeven_summary.json", "M-CAL-1", "summary_data", "python3 physicalized-weights/scripts/calibrated_breakeven.py"),
    row(DATA / "workload_summary.json", "M-WORKLOAD-1", "summary_data", "python3 physicalized-weights/scripts/workload_trace_generator.py"),
    row(DATA / "stronger_baseline_summary.json", "M-SWBASE-2", "summary_data", "python3 physicalized-weights/scripts/stronger_baseline_model.py"),
    row(DOCS / "stronger_baseline_comparison.md", "M-SWBASE-2", "report"),
    row(DATA / "stronger_baseline_workload_comparison.png", "M-SWBASE-2", "figure", "python3 physicalized-weights/scripts/stronger_baseline_model.py"),
    row(DATA / "phase2_synthesis_summary.json", "M-SYNTH-2", "summary_data", "python3 physicalized-weights/scripts/build_phase2_synthesis.py"),
    row(DOCS / "phase2_synthesis_downgrade.md", "M-SYNTH-2", "report"),
    row(DATA / "phase2_evidence_map.png", "M-SYNTH-2", "figure", "python3 physicalized-weights/scripts/build_phase2_synthesis.py"),
    row(DATA / "production_trace_schema.json", "M-TRACE-1", "schema", "python3 physicalized-weights/scripts/production_trace_validator.py"),
    row(DATA / "reopen_thresholds_summary.json", "M-REOPEN-1", "summary_data", "python3 physicalized-weights/scripts/reopen_thresholds.py"),
    row(DATA / "reopen_pipeline_summary.json", "M-PIPELINE-1", "summary_data", "python3 physicalized-weights/scripts/reopen_pipeline_demo.py"),
    row(DATA / "evidence_pack_manifest_schema.json", "M-EVIDENCEPACK-1", "schema", "python3 physicalized-weights/scripts/evidence_pack_replay.py"),
    row(DATA / "evidence_pack_replay_summary.json", "M-EVIDENCEPACK-1", "summary_data", "python3 physicalized-weights/scripts/evidence_pack_replay.py"),
    row(DATA / "phase3_reopen_summary.json", "M-PHASE3-SYNTH-1", "summary_data", "python3 physicalized-weights/scripts/build_phase3_reopen_synthesis.py"),
    row(DOCS / "phase3_reopen_pathway_summary.md", "M-PHASE3-SYNTH-1", "report"),
    row(DATA / "evidence_acquisition_readiness_summary.json", "M-ACQUIRE-1", "summary_data", "python3 physicalized-weights/scripts/evidence_acquisition_readiness.py"),
    row(DATA / "evidence_pack_dryrun_summary.json", "M-DRYRUN-1", "summary_data", "python3 physicalized-weights/scripts/evidence_pack_template_dryrun.py", "dry-run fixture summary; non-production control artifact"),
    row(DATA / "evidence_pack_intake_rehearsal_summary.json", "M-INTAKE-1", "summary_data", "python3 physicalized-weights/scripts/evidence_pack_intake_rehearsal.py", "rehearsal fixture summary; non-production control artifact"),
    row(DATA / "reopen_uncertainty_summary.json", "M-UNCERTAINTY-1", "summary_data", "python3 physicalized-weights/scripts/reopen_uncertainty_protocol.py"),
    row(DOCS / "measured_reopen_uncertainty_protocol.md", "M-UNCERTAINTY-1", "report"),
    row(DATA / "evidence_package_lifecycle_summary.json", "M-LIFECYCLE-1", "summary_data", "python3 physicalized-weights/scripts/evidence_package_lifecycle.py"),
    row(DOCS / "evidence_package_lifecycle_state_machine.md", "M-LIFECYCLE-1", "report"),
    row(DATA / "phase4_reopen_summary.json", "M-PHASE4-SYNTH-1", "summary_data", "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py"),
    row(DATA / "phase4_reopen_claim_matrix.csv", "M-PHASE4-SYNTH-1", "evidence_data", "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py"),
    row(DATA / "phase4_reopen_manifest.csv", "M-PHASE4-SYNTH-1", "manifest", "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py"),
    row(DOCS / "phase4_reopen_lifecycle_synthesis.md", "M-PHASE4-SYNTH-1", "report"),
    row(DATA / "phase4_reopen_lifecycle_flow.png", "M-PHASE4-SYNTH-1", "figure", "python3 physicalized-weights/scripts/build_phase4_reopen_synthesis.py"),
    row(DATA / "target_robustness_summary.json", "M-ROBUST-1", "summary_data", "python3 physicalized-weights/scripts/target_robustness_stress.py"),
    row(DATA / "target_robustness_results.csv", "M-ROBUST-1", "evidence_data", "python3 physicalized-weights/scripts/target_robustness_stress.py"),
    row(DOCS / "target_robustness_stress_test.md", "M-ROBUST-1", "report"),
    row(DATA / "target_robustness_frontier.png", "M-ROBUST-1", "figure", "python3 physicalized-weights/scripts/target_robustness_stress.py"),
    row(DATA / "campaign_deferral_watchlist_summary.json", "M-DEFER-1", "summary_data", "python3 physicalized-weights/scripts/build_campaign_deferral_watchlist.py"),
    row(DATA / "campaign_deferral_watchlist_results.csv", "M-DEFER-1", "evidence_data", "python3 physicalized-weights/scripts/build_campaign_deferral_watchlist.py"),
    row(DOCS / "campaign_deferral_watchlist.md", "M-DEFER-1", "report"),
    row(DATA / "campaign_deferral_watchlist.png", "M-DEFER-1", "figure", "python3 physicalized-weights/scripts/build_campaign_deferral_watchlist.py"),
    row(DATA / "campaign_closure_summary.json", "M-CLOSURE-1", "summary_data", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
    row(DATA / "campaign_closure_claim_disposition.csv", "M-CLOSURE-1", "evidence_data", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
    row(DATA / "campaign_closure_manifest.csv", "M-CLOSURE-1", "manifest", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
    row(DOCS / "campaign_closure_report.md", "M-CLOSURE-1", "report", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
    row(DOCS / "campaign_executive_summary.md", "M-CLOSURE-1", "report", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
    row(DATA / "campaign_closure_evidence_flow.png", "M-CLOSURE-1", "figure", "python3 physicalized-weights/scripts/build_campaign_closure_report.py"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def closure_claim_supports() -> set[str]:
    claims_path = DATA / "campaign_closure_claim_disposition.csv"
    supports: set[str] = set()
    for row_item in read_csv(claims_path):
        for support in row_item["supporting_artifacts"].split(";"):
            support = support.strip()
            if support:
                supports.add(support)
    return supports


def build_manifest_rows() -> list[dict[str, str]]:
    rows = [dict(item) for item in CANONICAL_ARTIFACTS]
    present = {item["artifact_path"] for item in rows}
    for support in sorted(closure_claim_supports() - present):
        rows.append(
            {
                "artifact_path": support,
                "milestone_id": "M-CLOSURE-1",
                "artifact_class": "claim_support",
                "canonical": "true",
                "regeneration_command": "",
                "notes": "Added from closure claim-disposition support list.",
            }
        )

    enriched: list[dict[str, str]] = []
    for item in rows:
        path = ROOT / item["artifact_path"]
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        digest = sha256(path) if exists and size > 0 else ""
        enriched.append(
            {
                "artifact_path": item["artifact_path"],
                "milestone_id": item["milestone_id"],
                "artifact_class": item["artifact_class"],
                "canonical": item["canonical"],
                "exists": str(exists).lower(),
                "size_bytes": str(size),
                "sha256": digest,
                "regeneration_command": item["regeneration_command"],
                "notes": item["notes"],
            }
        )
    return enriched


def guard_invariants() -> dict[str, Any]:
    closure = read_json(DATA / "campaign_closure_summary.json")
    phase4 = read_json(DATA / "phase4_reopen_summary.json")
    robust = read_json(DATA / "target_robustness_summary.json")
    defer = read_json(DATA / "campaign_deferral_watchlist_summary.json")
    if closure.get("current_superiority_claim_count") != 0:
        raise RuntimeError("Closure summary reports a current superiority claim")
    if closure.get("actual_reopen_candidate_count") != 0:
        raise RuntimeError("Closure summary reports a current reopen candidate")
    if closure.get("new_reopen_gate_count") != 0:
        raise RuntimeError("Closure summary reports a new reopen gate")
    if closure.get("current_artifacts_reopen") is not False:
        raise RuntimeError("Closure summary reports current artifacts reopening")
    if phase4.get("actual_reopen_candidate_count") != 0:
        raise RuntimeError("Phase 4 summary reports a current reopen candidate")
    if robust.get("current_superiority_claim_count") != 0:
        raise RuntimeError("Robustness summary reports a current superiority claim")
    if defer.get("new_reopen_gate_count") != 0:
        raise RuntimeError("Deferral summary reports a new reopen gate")
    return {"closure": closure, "phase4": phase4, "robust": robust, "defer": defer}


def write_manifest_csv(rows: list[dict[str, str]]) -> None:
    fields = [
        "artifact_path",
        "milestone_id",
        "artifact_class",
        "canonical",
        "exists",
        "size_bytes",
        "sha256",
        "regeneration_command",
        "notes",
    ]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_manifest_json(rows: list[dict[str, str]]) -> None:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for item in rows:
        grouped[item["milestone_id"]].append(item)
    payload = {
        "schema_version": 1,
        "milestone_id": "M-ARCHIVE-1",
        "manifest_kind": "closure_archive_index",
        "artifacts_by_milestone": dict(sorted(grouped.items())),
    }
    MANIFEST_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summary(rows: list[dict[str, str]], invariant_inputs: dict[str, Any]) -> dict[str, Any]:
    canonical = [item for item in rows if item["canonical"] == "true"]
    missing = [item for item in canonical if item["exists"] != "true"]
    zero = [item for item in canonical if item["exists"] == "true" and int(item["size_bytes"]) == 0]
    class_counts = Counter(item["artifact_class"] for item in canonical)
    milestone_counts = Counter(item["milestone_id"] for item in canonical)
    return {
        "schema_version": 1,
        "milestone_id": "M-ARCHIVE-1",
        "status": "validated",
        "canonical_artifact_count": len(canonical),
        "missing_canonical_artifact_count": len(missing),
        "zero_size_canonical_artifact_count": len(zero),
        "current_superiority_claim_count": 0,
        "actual_reopen_candidate_count": invariant_inputs["closure"].get("actual_reopen_candidate_count", 0),
        "new_reopen_gate_count": invariant_inputs["closure"].get("new_reopen_gate_count", 0),
        "current_artifacts_reopen": False,
        "known_warning_count": len(KNOWN_WARNINGS),
        "known_warnings": KNOWN_WARNINGS,
        "artifact_class_counts": dict(sorted(class_counts.items())),
        "milestone_artifact_counts": dict(sorted(milestone_counts.items())),
        "closure_claim_support_count": len(closure_claim_supports()),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": "The archive indexes validated campaign endpoint artifacts for handoff while preserving zero current superiority claims, zero actual reopen candidates, and zero new reopen gates.",
    }


def write_png(rows: list[dict[str, str]], path: Path) -> None:
    width, height = 1100, 520
    pixels = bytearray([248, 249, 247] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            offset = (y * width + max(0, x0)) * 3
            for _ in range(max(0, x0), min(width, x1)):
                pixels[offset : offset + 3] = bytes(color)
                offset += 3

    rect(48, 50, 1050, 470, (235, 239, 242))
    canonical = [item for item in rows if item["canonical"] == "true"]
    milestones = list(dict.fromkeys(item["milestone_id"] for item in canonical))
    class_colors = {
        "report": (77, 120, 162),
        "summary_data": (77, 145, 112),
        "evidence_data": (184, 93, 78),
        "figure": (205, 144, 63),
        "schema": (128, 105, 166),
        "manifest": (81, 145, 156),
        "hdl_source": (96, 96, 96),
        "claim_support": (150, 150, 150),
    }
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    missing: dict[str, int] = defaultdict(int)
    for item in canonical:
        counts[item["milestone_id"]][item["artifact_class"]] += 1
        if item["exists"] != "true":
            missing[item["milestone_id"]] += 1

    max_total = max(sum(counter.values()) for counter in counts.values())
    bar_w = max(18, min(42, 880 // max(1, len(milestones))))
    gap = max(4, (920 - bar_w * len(milestones)) // max(1, len(milestones) + 1))
    x = 75 + gap
    base_y = 430
    scale = 320 / max_total
    for milestone in milestones:
        y = base_y
        for artifact_class, count in sorted(counts[milestone].items()):
            h = max(2, int(count * scale))
            rect(x, y - h, x + bar_w, y, class_colors.get(artifact_class, (120, 120, 120)))
            y -= h
        if missing[milestone]:
            rect(x, 84, x + bar_w, 104, (190, 40, 40))
        x += bar_w + gap

    legend_x = 820
    legend_y = 82
    for i, (artifact_class, color) in enumerate(class_colors.items()):
        y = legend_y + i * 28
        rect(legend_x, y, legend_x + 22, y + 14, color)
        rect(legend_x + 30, y + 4, legend_x + 160, y + 9, (70, 70, 70))
    rect(70, 60, 360, 75, (70, 70, 70))
    rect(70, 462, 1030, 466, (70, 70, 70))

    raw = b"".join(b"\x00" + bytes(pixels[y * width * 3 : (y + 1) * width * 3]) for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def markdown_table(rows: list[dict[str, str]]) -> str:
    lines = ["| Artifact | Milestone | Class | Size | SHA-256 |", "|---|---|---:|---:|---|"]
    for item in rows:
        if item["canonical"] != "true":
            continue
        digest = item["sha256"][:12] + "..." if item["sha256"] else "missing"
        lines.append(
            f"| `{item['artifact_path']}` | `{item['milestone_id']}` | {item['artifact_class']} | {item['size_bytes']} | `{digest}` |"
        )
    return "\n".join(lines)


def write_report(rows: list[dict[str, str]], summary_payload: dict[str, Any]) -> None:
    warnings = "\n".join(
        f"- `{item['warning_id']}` from `{item['source']}`: {item['scope']} ({item['classification']}). {item['note']}"
        for item in KNOWN_WARNINGS
    )
    commands = "\n".join(COMMANDS)
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T19:36:00Z
cycle: 10
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-ARCHIVE-1
---

# Closure Archive Index

## Purpose And Scope

This index is a handoff artifact for the validated campaign endpoint. It maps canonical closure and evidence-chain artifacts to milestone owner, artifact class, byte size, SHA-256 hash, and regeneration command where applicable. It does not add a model, reopen gate, synthetic evidence path, or current superiority claim.

## Canonical Endpoint Artifacts

{markdown_table(rows)}

## Reproduction Commands

Run from `<workspace>`:

```bash
{commands}
```

## Integrity Checks

- `canonical_artifact_count`: {summary_payload['canonical_artifact_count']}
- `missing_canonical_artifact_count`: {summary_payload['missing_canonical_artifact_count']}
- `zero_size_canonical_artifact_count`: {summary_payload['zero_size_canonical_artifact_count']}
- Manifest CSV: `physicalized-weights/data/closure_archive_manifest.csv`
- Manifest JSON: `physicalized-weights/data/closure_archive_manifest.json`
- Summary JSON: `physicalized-weights/data/closure_archive_summary.json`

![{FIGURE_CAPTION}](../data/closure_archive_coverage.png)

## Known Non-Blocking Warnings

{warnings}

## Current Evidence Disposition Invariants

- `current_superiority_claim_count = {summary_payload['current_superiority_claim_count']}`
- `actual_reopen_candidate_count = {summary_payload['actual_reopen_candidate_count']}`
- `new_reopen_gate_count = {summary_payload['new_reopen_gate_count']}`
- `current_artifacts_reopen = false`

Synthetic, proxy, template, rehearsal, vendor-only, and dry-run artifacts may appear as prior fixtures or controls, but this archive does not label them as measured production evidence.
""",
        encoding="utf-8",
    )


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    invariant_inputs = guard_invariants()
    rows = build_manifest_rows()
    summary_payload = summary(rows, invariant_inputs)
    write_png(rows, COVERAGE_PNG)
    write_report(rows, summary_payload)
    write_manifest_csv(rows)
    write_manifest_json(rows)
    SUMMARY_JSON.write_text(json.dumps(summary_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for path in [REPORT_MD, MANIFEST_CSV, MANIFEST_JSON, SUMMARY_JSON, COVERAGE_PNG]:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
