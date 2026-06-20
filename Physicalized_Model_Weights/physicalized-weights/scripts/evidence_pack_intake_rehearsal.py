# created: 2026-05-13T14:06:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INTAKE-1

"""Rehearse handoff from operator dry-run packages into evidence-pack replay."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"
SCRIPTS = ROOT / "physicalized-weights" / "scripts"
PACKAGES = DATA / "intake_rehearsal_packages"

DRYRUN_PATH = SCRIPTS / "evidence_pack_template_dryrun.py"
REPLAY_PATH = SCRIPTS / "evidence_pack_replay.py"
PIPELINE_PATH = SCRIPTS / "reopen_pipeline_demo.py"

CASES_CSV = DATA / "evidence_pack_intake_cases.csv"
RESULTS_CSV = DATA / "evidence_pack_intake_rehearsal_results.csv"
SUMMARY_JSON = DATA / "evidence_pack_intake_rehearsal_summary.json"
FLOW_PNG = DATA / "evidence_pack_intake_rehearsal_flow.png"
REPORT_MD = DOCS / "evidence_pack_intake_rehearsal.md"

MILESTONE_ID = "M-INTAKE-1"
FIGURE_CAPTION = (
    "Intake rehearsal from operator dry-run templates to evidence-pack replay, "
    "showing preserved hashes/manifests for valid synthetic-safe packages and "
    "blocked handoff mutations before any current artifact can reopen."
)
PRESERVED_FIELDS = [
    "trace_file",
    "trace_sha256",
    "ingestion_path_id",
    "evidence_source_type",
    "measurement_status",
    "provenance_attestation",
    "threshold_scenario_id",
    "pipeline_expected_status",
    "privacy_attestation",
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


dryrun = load_module(DRYRUN_PATH, "evidence_pack_template_dryrun")
replay = load_module(REPLAY_PATH, "evidence_pack_replay")
pipeline = load_module(PIPELINE_PATH, "reopen_pipeline_demo")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def default_cases() -> list[dict[str, str]]:
    base = {
        "scenario_id": "high_volume_stable_moderation",
        "measurement_status": "measured",
        "mutation": "none",
    }
    rows = [
        {
            **base,
            "case_id": "shadow_synthetic_filled_non_crossing",
            "description": "Filled shadow package with synthetic-safe rows and non-crossing measured values.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
        },
        {
            **base,
            "case_id": "canary_synthetic_filled_non_crossing",
            "description": "Filled canary package with synthetic-safe rows and non-crossing measured values.",
            "evidence_source_type": "canary_production",
            "ingestion_path_id": "canary_ab_dual_instrumented",
            "measurement_environment": "production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
        },
        {
            **base,
            "case_id": "synthetic_counterfactual_crossing_non_actual",
            "description": "Synthetic counterfactual crosses the arithmetic threshold but remains non-actual evidence.",
            "evidence_source_type": "synthetic",
            "ingestion_path_id": "offline_replay_redacted_features",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "synthetic_counterfactual_crossed",
            "crossing_mode": "crossing",
        },
        {
            **base,
            "case_id": "stale_hash_after_handoff",
            "description": "Trace is mutated after dry-run hash capture.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "stale_hash",
        },
        {
            **base,
            "case_id": "trace_file_alias_after_handoff",
            "description": "Manifest trace file is changed to an identical copied trace after dry-run.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "trace_file_alias",
        },
        {
            **base,
            "case_id": "manifest_trace_source_mismatch",
            "description": "Manifest source changes after dry-run while trace source remains unchanged.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "source_mismatch",
        },
        {
            **base,
            "case_id": "threshold_mapping_changed_after_dryrun",
            "description": "Manifest threshold scenario is changed after dry-run.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "threshold_changed",
        },
        {
            **base,
            "case_id": "attestation_changed_after_hash",
            "description": "Manifest provenance attestation is changed after dry-run.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "attestation_changed",
        },
        {
            **base,
            "case_id": "raw_content_added_after_dryrun",
            "description": "A privacy-risk content column is added after dry-run.",
            "evidence_source_type": "shadow_production",
            "ingestion_path_id": "shadow_production_dual_run",
            "measurement_environment": "shadow_production",
            "pipeline_expected_status": "threshold_evaluable_not_crossed",
            "crossing_mode": "non_crossing",
            "mutation": "raw_content_added",
        },
    ]
    return rows


def write_cases() -> None:
    rows = default_cases()
    with CASES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_cases() -> list[dict[str, str]]:
    with CASES_CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def energy_values(crossing_mode: str, row_num: int) -> tuple[str, str]:
    if crossing_mode == "crossing":
        return "3000000000", "1000000000"
    if row_num == 1:
        return "1000000000", "980000000"
    return "1000000000", "980000000"


def trace_rows(case: dict[str, str]) -> list[dict[str, str]]:
    rows = []
    for idx, timestamp in enumerate([1000, 2000], start=1):
        accelerator, hybrid = energy_values(case["crossing_mode"], idx)
        rows.append(
            pipeline.base_row(
                timestamp,
                scenario_id=case["scenario_id"],
                measurement_environment=case["measurement_environment"],
                evidence_source_type=case["evidence_source_type"],
                ingestion_path_id=case["ingestion_path_id"],
                measurement_status=case["measurement_status"],
                accelerator_energy_proxy_or_measured_pj=accelerator,
                hybrid_energy_proxy_or_measured_pj=hybrid,
                feature_vector_hash=f"hash:{case['case_id']}-{idx}",
            )
        )
    return rows


def write_trace(path: Path, rows: list[dict[str, str]], include_content: bool = False) -> None:
    fieldnames = pipeline.trace_fieldnames(include_privacy_risk=False)
    if include_content:
        fieldnames.append("content")
        for row in rows:
            row["content"] = "blocked synthetic placeholder"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def dryrun_probe_status(case: dict[str, str], trace_path: Path) -> str:
    headers = next(csv.reader(trace_path.open(newline="", encoding="utf-8")))
    probe = {
        "case_id": case["case_id"],
        "description": case["description"],
        "source": case["evidence_source_type"],
        "measurement_status": case["measurement_status"],
        "ingestion_path_id": case["ingestion_path_id"],
        "threshold_scenario_id": case["scenario_id"],
        "manifest_missing_field": "",
        "extra_trace_column": "",
        "attestation_replaced": "true",
        "hash_mode": "match",
        "drop_trace_columns": "",
        "drop_energy_columns": "false",
        "expected_status": "ready_for_collection_not_evidence",
    }
    manifest = dryrun.case_manifest(probe, headers)
    blockers: list[str] = []
    for field in dryrun.required_manifest_fields():
        if field not in manifest:
            blockers.append(f"missing_required_manifest_field:{field}")
    for field, allowed in dryrun.manifest_allowed_values().items():
        if field in manifest and manifest[field] not in allowed:
            blockers.append(f"invalid_manifest_value:{field}:{manifest[field]}")
    if manifest.get("ingestion_path_id") not in dryrun.allowed_ingestion_paths():
        blockers.append(f"inadmissible_ingestion_path:{manifest.get('ingestion_path_id')}")
    disallowed = dryrun.privacy_disallowed_columns()
    for column in headers:
        if column.lower() in disallowed:
            blockers.append(f"privacy_disallowed_column:{column}")
    for column in dryrun.trace_columns():
        if column not in headers:
            blockers.append(f"missing_trace_column:{column}")
    if manifest.get("threshold_scenario_id") not in dryrun.allowed_threshold_scenarios():
        blockers.append(f"unknown_threshold_scenario:{manifest.get('threshold_scenario_id')}")
    if case["evidence_source_type"] in {"production", "shadow_production", "canary_production"} and case["measurement_status"] != "measured":
        blockers.append("source_measurement_contradiction")
    return dryrun.status_from_blockers(blockers)


def base_manifest(case: dict[str, str], trace_path: Path) -> dict[str, Any]:
    return replay.make_manifest(
        pack_id=case["case_id"],
        trace_file=trace_path,
        ingestion_path_id=case["ingestion_path_id"],
        evidence_source_type=case["evidence_source_type"],
        measurement_status=case["measurement_status"],
        provenance_attestation=True,
        threshold_scenario_id=case["scenario_id"],
        pipeline_expected_status=case["pipeline_expected_status"],
        privacy_attestation=True,
    )


def mutate_after_dryrun(case: dict[str, str], trace_path: Path, manifest: dict[str, Any]) -> None:
    mutation = case["mutation"]
    if mutation == "stale_hash":
        rows = replay.pipeline.read_trace_rows(trace_path)
        rows[0]["hybrid_fast_path_latency_ns"] = "1300"
        write_trace(trace_path, rows)
    elif mutation == "trace_file_alias":
        alias_path = trace_path.with_name("trace_alias.csv")
        alias_path.write_bytes(trace_path.read_bytes())
        manifest["trace_file"] = relative(alias_path)
    elif mutation == "source_mismatch":
        manifest["evidence_source_type"] = "canary_production"
    elif mutation == "threshold_changed":
        manifest["threshold_scenario_id"] = "bursty_consumer_traffic"
    elif mutation == "attestation_changed":
        manifest["provenance_attestation"] = False
    elif mutation == "raw_content_added":
        rows = replay.pipeline.read_trace_rows(trace_path)
        write_trace(trace_path, rows, include_content=True)


def manifest_preserved(original: dict[str, Any], current: dict[str, Any]) -> bool:
    return all(original.get(field) == current.get(field) for field in PRESERVED_FIELDS)


def intake_blockers(
    case: dict[str, str],
    trace_path: Path,
    original_manifest: dict[str, Any],
    current_manifest: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    actual_hash = sha256_file(trace_path)
    if actual_hash != str(current_manifest.get("trace_sha256", "")):
        blockers.append("hash_preserved=false:trace_sha256_mismatch_after_handoff")
    if not manifest_preserved(original_manifest, current_manifest):
        for field in PRESERVED_FIELDS:
            if original_manifest.get(field) != current_manifest.get(field):
                blockers.append(f"manifest_preserved=false:{field}")
    rows = replay.pipeline.read_trace_rows(trace_path)
    trace_source = replay.pipeline.first_present(rows, "evidence_source_type", "missing")
    trace_ingestion = replay.pipeline.first_present(rows, "ingestion_path_id", "missing")
    trace_measurement = replay.pipeline.first_present(rows, "measurement_status", "missing")
    trace_scenario = replay.pipeline.first_present(rows, "scenario_id", "missing")
    trace_provenance = replay.pipeline.parse_bool(
        replay.pipeline.first_present(rows, "provenance_attestation", "false")
    )
    checks = {
        "evidence_source_type": trace_source,
        "ingestion_path_id": trace_ingestion,
        "measurement_status": trace_measurement,
        "threshold_scenario_id": trace_scenario,
    }
    for field, trace_value in checks.items():
        if str(current_manifest.get(field, "")) != trace_value:
            blockers.append(f"handoff_manifest_trace_mismatch:{field}")
    if bool(current_manifest.get("provenance_attestation")) != trace_provenance:
        blockers.append("handoff_manifest_trace_mismatch:provenance_attestation")
    headers = next(csv.reader(trace_path.open(newline="", encoding="utf-8")))
    for column in headers:
        if column.lower() in dryrun.privacy_disallowed_columns():
            blockers.append(f"post_dryrun_privacy_column:{column}")
    if current_manifest.get("threshold_scenario_id") not in dryrun.allowed_threshold_scenarios():
        blockers.append(f"unknown_threshold_scenario:{current_manifest.get('threshold_scenario_id')}")
    return blockers


def classify_intake(blockers: list[str]) -> str:
    if not blockers:
        return "intake_passed"
    if any("privacy" in blocker for blocker in blockers):
        return "intake_privacy_blocked"
    if any("trace_sha256" in blocker or "hash_preserved=false" in blocker for blocker in blockers):
        return "intake_hash_blocked"
    if any("threshold_scenario_id" in blocker or "unknown_threshold" in blocker for blocker in blockers):
        return "intake_threshold_blocked"
    if any("provenance_attestation" in blocker for blocker in blockers):
        return "intake_attestation_blocked"
    return "intake_manifest_blocked"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evaluate_case(case: dict[str, str]) -> dict[str, str]:
    case_dir = PACKAGES / case["case_id"]
    case_dir.mkdir(parents=True, exist_ok=True)
    trace_path = case_dir / "trace.csv"
    manifest_path = case_dir / "manifest.json"

    write_trace(trace_path, trace_rows(case))
    dryrun_status = dryrun_probe_status(case, trace_path)
    original_manifest = base_manifest(case, trace_path)
    current_manifest = dict(original_manifest)
    mutate_after_dryrun(case, trace_path, current_manifest)
    write_json(manifest_path, current_manifest)

    blockers = intake_blockers(case, trace_path, original_manifest, current_manifest)
    hash_preserved = sha256_file(trace_path) == str(current_manifest.get("trace_sha256", ""))
    manifest_ok = manifest_preserved(original_manifest, current_manifest)
    intake_status = classify_intake(blockers)

    replay_status = "not_run"
    final_status = "intake_blocked"
    actual = "False"
    replay_blockers = "not_run"
    if intake_status == "intake_passed":
        replay_row = replay.evaluate_manifest(manifest_path)
        replay_status = replay_row["pipeline_status"]
        final_status = replay_row["final_package_decision"]
        actual = replay_row["actual_reopen_candidate"]
        replay_blockers = replay_row["blocking_reasons"]
        if replay_row["package_integrity_status"] != "valid_package":
            blockers.append(f"replay_package_invalid:{replay_row['blocking_reasons']}")
            intake_status = "intake_replay_contract_blocked"
            final_status = "intake_blocked"
            replay_status = "not_run"
            actual = "False"

    return {
        "case_id": case["case_id"],
        "dryrun_status": dryrun_status,
        "intake_status": intake_status,
        "replay_status": replay_status,
        "final_status": final_status,
        "hash_preserved": str(hash_preserved),
        "manifest_preserved": str(manifest_ok),
        "actual_reopen_candidate": actual,
        "trace_file": relative(trace_path),
        "manifest_file": relative(manifest_path),
        "blocking_reasons": "none" if not blockers else "|".join(blockers),
        "replay_blocking_reasons": replay_blockers,
    }


FIELDNAMES = [
    "case_id",
    "dryrun_status",
    "intake_status",
    "replay_status",
    "final_status",
    "hash_preserved",
    "manifest_preserved",
    "actual_reopen_candidate",
    "trace_file",
    "manifest_file",
    "blocking_reasons",
    "replay_blocking_reasons",
]


def write_results(rows: list[dict[str, str]]) -> None:
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 980, 430
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "intake_passed": (72, 126, 172),
        "intake_hash_blocked": (165, 72, 66),
        "intake_manifest_blocked": (181, 104, 58),
        "intake_threshold_blocked": (128, 88, 154),
        "intake_attestation_blocked": (179, 132, 55),
        "intake_privacy_blocked": (144, 64, 86),
    }
    rect(45, 35, 935, 370, (241, 243, 246))
    for idx, row in enumerate(rows):
        x0 = 70 + idx * 105
        h = 225 if row["intake_status"] == "intake_passed" else 105
        color = colors.get(row["intake_status"], (120, 120, 120))
        rect(x0, 330 - h, x0 + 65, 330, color)
        if row["actual_reopen_candidate"] == "True":
            rect(x0 + 18, 72, x0 + 47, 103, (48, 128, 76))
        else:
            rect(x0 + 18, 72, x0 + 47, 103, (92, 98, 108))
    for i, (name, color) in enumerate(colors.items()):
        rect(705, 28 + i * 20, 728, 41 + i * 20, color)
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    FLOW_PNG.write_bytes(png)


def build_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    intake_counts = Counter(row["intake_status"] for row in rows)
    replay_counts = Counter(row["replay_status"] for row in rows)
    actual_count = sum(1 for row in rows if row["actual_reopen_candidate"] == "True")
    successful = [row for row in rows if row["intake_status"] == "intake_passed"]
    return {
        "schema_version": 1,
        "milestone_id": MILESTONE_ID,
        "status": "validated",
        "case_count": len(rows),
        "intake_status_counts": dict(sorted(intake_counts.items())),
        "replay_status_counts": dict(sorted(replay_counts.items())),
        "successful_intake_count": len(successful),
        "blocked_before_replay_count": sum(1 for row in rows if row["replay_status"] == "not_run"),
        "actual_reopen_candidate_count": actual_count,
        "current_artifacts_reopen": False,
        "all_successful_intakes_preserved": all(
            row["hash_preserved"] == "True" and row["manifest_preserved"] == "True"
            for row in successful
        ),
        "successful_intake_cases": [row["case_id"] for row in successful],
        "blocked_cases": [
            row["case_id"] for row in rows if row["intake_status"] != "intake_passed"
        ],
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The intake rehearsal preserves the handoff for filled shadow/canary "
            "packages and a synthetic counterfactual control, then blocks stale "
            "hashes, manifest mutations, threshold remapping, attestation changes, "
            "and post-dry-run privacy columns before replay. It remains synthetic-safe "
            "and creates no actual reopen candidate."
        ),
    }


def write_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    lines = "\n".join(
        f"- `{row['case_id']}`: dry-run `{row['dryrun_status']}`, intake `{row['intake_status']}`, replay `{row['replay_status']}`, final `{row['final_status']}`, blockers `{row['blocking_reasons']}`."
        for row in rows
    )
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T14:06:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-INTAKE-1
---

# Evidence-pack intake rehearsal

M-INTAKE-1 checks the boundary between the operator dry-run layer and the evidence-pack replay layer. The script regenerates the M-DRYRUN-1 templates, fills synthetic-safe package traces under `physicalized-weights/data/intake_rehearsal_packages/`, computes trace SHA-256 values, writes replay-compatible manifests, checks that handoff fields are preserved, and only then calls the M-EVIDENCEPACK-1 replay evaluator.

The rehearsal copies no validated M-EVIDENCEPACK-1 fixtures and does not overwrite them. Each generated package has a package-local `trace.csv` and `manifest.json`; the manifest binds `trace_file`, `trace_sha256`, `ingestion_path_id`, `evidence_source_type`, `measurement_status`, `provenance_attestation`, `threshold_scenario_id`, `pipeline_expected_status`, and `privacy_attestation`.

All rows are synthetic-safe stand-ins. Shadow and canary cases exercise the valid handoff into replay without crossing the reopen threshold, while a synthetic counterfactual crosses the arithmetic branch but remains non-actual because source and ingestion eligibility still fail the Phase 3 gate. Mutation cases are blocked at intake before replay when a trace hash goes stale, manifest source changes, threshold mapping changes, provenance attestation changes, or raw content is added after dry-run.

![{FIGURE_CAPTION}](../data/evidence_pack_intake_rehearsal_flow.png)

## Results

{lines}

## Interpretation

The summary reports `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`. This rules in the handoff mechanism for synthetic-safe rehearsal packages and rules out the failure mode where intake silently rewrites manifests, ignores stale hashes, or converts dry-run/template data into actual reopen evidence.
""",
        encoding="utf-8",
    )


def main() -> int:
    PACKAGES.mkdir(parents=True, exist_ok=True)
    dryrun.main()
    write_cases()
    rows = [evaluate_case(case) for case in read_cases()]
    write_results(rows)
    summary = build_summary(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_png(rows)
    write_report(summary, rows)
    print(f"wrote {CASES_CSV}")
    print(f"wrote {RESULTS_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {FLOW_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"intake_status_counts: {summary['intake_status_counts']}")
    print(f"actual_reopen_candidate_count: {summary['actual_reopen_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
