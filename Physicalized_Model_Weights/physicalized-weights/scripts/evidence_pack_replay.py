# created: 2026-05-13T11:02:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-EVIDENCEPACK-1
"""Replay evidence-pack manifests through the validated reopen pipeline."""

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
DATA_DIR = ROOT / "physicalized-weights" / "data"
DOCS_DIR = ROOT / "physicalized-weights" / "docs"
PIPELINE_PATH = ROOT / "physicalized-weights" / "scripts" / "reopen_pipeline_demo.py"

MANIFEST_SCHEMA_JSON = DATA_DIR / "evidence_pack_manifest_schema.json"
RESULTS_CSV = DATA_DIR / "evidence_pack_replay_results.csv"
SUMMARY_JSON = DATA_DIR / "evidence_pack_replay_summary.json"
OUTPUT_PNG = DATA_DIR / "evidence_pack_replay_flow.png"
REPORT_MD = DOCS_DIR / "evidence_pack_replay_harness.md"

MANIFESTS = [
    DATA_DIR / "evidence_pack_valid_synthetic_manifest.json",
    DATA_DIR / "evidence_pack_shadow_non_crossing_manifest.json",
    DATA_DIR / "evidence_pack_synthetic_counterfactual_manifest.json",
    DATA_DIR / "evidence_pack_missing_attestation_manifest.json",
    DATA_DIR / "evidence_pack_bad_hash_manifest.json",
]


def load_pipeline():
    spec = importlib.util.spec_from_file_location("reopen_pipeline_demo", PIPELINE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["reopen_pipeline_demo"] = module
    spec.loader.exec_module(module)
    return module


pipeline = load_pipeline()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workspace_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_manifest_schema() -> dict[str, Any]:
    return json.loads(MANIFEST_SCHEMA_JSON.read_text())


def make_manifest(
    pack_id: str,
    trace_file: Path,
    ingestion_path_id: str,
    evidence_source_type: str,
    measurement_status: str,
    provenance_attestation: bool,
    threshold_scenario_id: str,
    pipeline_expected_status: str,
    privacy_attestation: bool = True,
    bad_hash: bool = False,
) -> dict[str, Any]:
    digest = sha256_file(trace_file)
    if bad_hash:
        digest = "0" * 64
    return {
        "pack_id": pack_id,
        "schema_version": 1,
        "created_at_utc": "2026-05-13T11:02:00Z",
        "trace_schema_version": 1,
        "trace_file": relative(trace_file),
        "trace_sha256": digest,
        "ingestion_path_id": ingestion_path_id,
        "evidence_source_type": evidence_source_type,
        "measurement_status": measurement_status,
        "provenance_attestation": provenance_attestation,
        "threshold_scenario_id": threshold_scenario_id,
        "pipeline_expected_status": pipeline_expected_status,
        "privacy_attestation": privacy_attestation,
    }


def write_default_manifests() -> None:
    pipeline.main()
    manifests = [
        make_manifest(
            "valid_synthetic_proxy",
            pipeline.FIXTURE_VALID_INSUFFICIENT,
            "synthetic_fixture_only",
            "synthetic",
            "proxy",
            True,
            "high_volume_stable_moderation",
            "valid_but_insufficient",
        ),
        make_manifest(
            "shadow_non_crossing",
            pipeline.FIXTURE_THRESHOLD_NOT_CROSSED,
            "shadow_production_dual_run",
            "shadow_production",
            "measured",
            True,
            "high_volume_stable_moderation",
            "threshold_evaluable_not_crossed",
        ),
        make_manifest(
            "synthetic_counterfactual_crossed",
            pipeline.FIXTURE_COUNTERFACTUAL_CROSSED,
            "offline_replay_redacted_features",
            "synthetic",
            "measured",
            True,
            "high_volume_stable_moderation",
            "synthetic_counterfactual_crossed",
        ),
        make_manifest(
            "missing_provenance_attestation",
            pipeline.FIXTURE_THRESHOLD_NOT_CROSSED,
            "shadow_production_dual_run",
            "shadow_production",
            "measured",
            False,
            "high_volume_stable_moderation",
            "threshold_evaluable_not_crossed",
        ),
        make_manifest(
            "bad_trace_hash",
            pipeline.FIXTURE_THRESHOLD_NOT_CROSSED,
            "shadow_production_dual_run",
            "shadow_production",
            "measured",
            True,
            "high_volume_stable_moderation",
            "threshold_evaluable_not_crossed",
            bad_hash=True,
        ),
    ]
    for path, manifest in zip(MANIFESTS, manifests):
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_manifest(manifest: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    required = [str(field) for field in schema["required_fields"]]
    for field in required:
        if field not in manifest:
            blockers.append(f"missing_required_field:{field}")
    allowed = schema["allowed_values"]
    for field, values in allowed.items():
        if field in manifest and manifest[field] not in values:
            blockers.append(f"invalid_value:{field}={manifest[field]}")
    if manifest.get("schema_version") != schema["schema_version"]:
        blockers.append("schema_version_mismatch")
    if manifest.get("trace_schema_version") != 1:
        blockers.append("trace_schema_version_mismatch")
    threshold_scenario_id = manifest.get("threshold_scenario_id")
    if threshold_scenario_id not in pipeline.load_thresholds():
        blockers.append(f"unknown_threshold_scenario_id:{threshold_scenario_id}")
    if manifest.get("privacy_attestation") is not True:
        blockers.append("privacy_attestation=false")
    if manifest.get("provenance_attestation") is not True:
        blockers.append("provenance_attestation=false")
    return blockers


def check_manifest_trace_consistency(manifest: dict[str, Any], trace_path: Path) -> list[str]:
    rows = pipeline.read_trace_rows(trace_path)
    checks = {
        "ingestion_path_id": pipeline.first_present(rows, "ingestion_path_id", "missing"),
        "evidence_source_type": pipeline.first_present(rows, "evidence_source_type", "missing"),
        "measurement_status": pipeline.first_present(rows, "measurement_status", "missing"),
        "threshold_scenario_id": pipeline.first_present(rows, "scenario_id", "missing"),
    }
    blockers = []
    for field, trace_value in checks.items():
        if str(manifest.get(field, "")) != trace_value:
            blockers.append(f"manifest_trace_mismatch:{field}")
    trace_provenance = pipeline.parse_bool(pipeline.first_present(rows, "provenance_attestation", "false"))
    if bool(manifest.get("provenance_attestation")) != trace_provenance:
        blockers.append("manifest_trace_mismatch:provenance_attestation")
    return blockers


def evaluate_manifest(path: Path) -> dict[str, str]:
    manifest_path = path
    schema = load_manifest_schema()
    try:
        manifest = json.loads(manifest_path.read_text())
    except Exception as exc:  # pragma: no cover - defensive path for malformed future packs.
        return invalid_row(manifest_path, "unreadable_manifest", f"manifest_read_error:{exc}")

    blockers = validate_manifest(manifest, schema)
    trace_path = workspace_path(str(manifest.get("trace_file", "")))
    hash_match = False
    trace_exists = trace_path.exists()
    if not trace_exists:
        blockers.append("trace_file_missing")
    elif "schema_version_mismatch" not in blockers and "trace_schema_version_mismatch" not in blockers:
        actual_hash = sha256_file(trace_path)
        expected_hash = str(manifest.get("trace_sha256", ""))
        hash_match = actual_hash == expected_hash
        if not hash_match:
            blockers.append("trace_sha256_mismatch")
        else:
            blockers.extend(check_manifest_trace_consistency(manifest, trace_path))

    can_run_pipeline = (
        trace_exists
        and hash_match
        and "schema_version_mismatch" not in blockers
        and "trace_schema_version_mismatch" not in blockers
        and not any(b.startswith("unknown_threshold_scenario_id:") for b in blockers)
        and not any(b.startswith("missing_required_field:") or b.startswith("invalid_value:") for b in blockers)
        and "privacy_attestation=false" not in blockers
        and "provenance_attestation=false" not in blockers
        and not any(b.startswith("manifest_trace_mismatch:") for b in blockers)
    )

    pipeline_row: dict[str, str] | None = None
    if can_run_pipeline:
        pipeline_row = pipeline.evaluate_trace(
            trace_path,
            pipeline.load_schema(),
            pipeline.load_ingestion_scores(),
            pipeline.load_thresholds(),
        )
        if pipeline_row["final_status"] != str(manifest.get("pipeline_expected_status")):
            blockers.append("pipeline_expected_status_mismatch")

    package_status = "valid_package" if not blockers else "invalid_package"
    if pipeline_row:
        threshold_status = "crossed" if pipeline_row["threshold_crossed"] == "True" else "not_crossed"
        pipeline_status = pipeline_row["final_status"]
        package_decision = pipeline_status if package_status == "valid_package" else "package_invalid"
        actual = pipeline_row["actual_reopen_candidate"] == "True" and package_status == "valid_package"
    else:
        threshold_status = "not_evaluated"
        pipeline_status = "not_run"
        package_decision = "package_invalid"
        actual = False

    display_blockers = list(blockers)
    if pipeline_row and pipeline_row["primary_blockers"] != "none":
        display_blockers.append(f"pipeline:{pipeline_row['primary_blockers']}")

    return {
        "manifest_file": relative(manifest_path),
        "pack_id": str(manifest.get("pack_id", "missing")),
        "package_integrity_status": package_status,
        "hash_match": str(hash_match),
        "schema_compatible": str("schema_version_mismatch" not in blockers and "trace_schema_version_mismatch" not in blockers),
        "privacy_attestation": str(manifest.get("privacy_attestation", "missing")),
        "provenance_attestation": str(manifest.get("provenance_attestation", "missing")),
        "ingestion_path_id": str(manifest.get("ingestion_path_id", "missing")),
        "evidence_source_type": str(manifest.get("evidence_source_type", "missing")),
        "measurement_status": str(manifest.get("measurement_status", "missing")),
        "threshold_scenario_id": str(manifest.get("threshold_scenario_id", "missing")),
        "trace_file": str(manifest.get("trace_file", "missing")),
        "pipeline_status": pipeline_status,
        "threshold_status": threshold_status,
        "final_package_decision": package_decision,
        "actual_reopen_candidate": str(actual),
        "blocking_reasons": "none" if not display_blockers else "|".join(display_blockers),
    }


def invalid_row(path: Path, status: str, reason: str) -> dict[str, str]:
    return {
        "manifest_file": relative(path),
        "pack_id": "missing",
        "package_integrity_status": status,
        "hash_match": "False",
        "schema_compatible": "False",
        "privacy_attestation": "missing",
        "provenance_attestation": "missing",
        "ingestion_path_id": "missing",
        "evidence_source_type": "missing",
        "measurement_status": "missing",
        "threshold_scenario_id": "missing",
        "trace_file": "missing",
        "pipeline_status": "not_run",
        "threshold_status": "not_evaluated",
        "final_package_decision": "package_invalid",
        "actual_reopen_candidate": "False",
        "blocking_reasons": reason,
    }


FIELDNAMES = [
    "manifest_file",
    "pack_id",
    "package_integrity_status",
    "hash_match",
    "schema_compatible",
    "privacy_attestation",
    "provenance_attestation",
    "ingestion_path_id",
    "evidence_source_type",
    "measurement_status",
    "threshold_scenario_id",
    "trace_file",
    "pipeline_status",
    "threshold_status",
    "final_package_decision",
    "actual_reopen_candidate",
    "blocking_reasons",
]


def write_results(rows: list[dict[str, str]]) -> None:
    with RESULTS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 900, 460
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "package_invalid": (166, 75, 70),
        "valid_but_insufficient": (211, 151, 63),
        "threshold_evaluable_not_crossed": (84, 128, 176),
        "synthetic_counterfactual_crossed": (116, 90, 158),
        "actual_reopen_candidate": (47, 129, 83),
    }
    rect(50, 38, 850, 410, (239, 241, 244))
    for idx, row in enumerate(rows):
        x0 = 78 + idx * 155
        decision = row["final_package_decision"]
        h = 252 if row["threshold_status"] == "crossed" else 145
        if row["package_integrity_status"] != "valid_package":
            h = 100
        rect(x0, 360 - h, x0 + 105, 360, colors.get(decision, (120, 120, 120)))
        if row["actual_reopen_candidate"] == "True":
            rect(x0 + 35, 80, x0 + 70, 116, (30, 96, 60))
        else:
            rect(x0 + 35, 80, x0 + 70, 116, (92, 98, 108))
    for i, (name, color) in enumerate(colors.items()):
        rect(610, 24 + i * 20, 632, 37 + i * 20, color)
    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    OUTPUT_PNG.write_bytes(png)


def build_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "milestone_id": "M-EVIDENCEPACK-1",
        "status": "validated",
        "pack_count": len(rows),
        "package_integrity_counts": dict(sorted(Counter(row["package_integrity_status"] for row in rows).items())),
        "final_package_decision_counts": dict(sorted(Counter(row["final_package_decision"] for row in rows).items())),
        "actual_reopen_candidate_count": sum(1 for row in rows if row["actual_reopen_candidate"] == "True"),
        "threshold_not_evaluated_count": sum(1 for row in rows if row["threshold_status"] == "not_evaluated"),
        "synthetic_or_proxy_actual_reopen_candidates": [
            row["manifest_file"]
            for row in rows
            if row["actual_reopen_candidate"] == "True"
            and (row["evidence_source_type"] == "synthetic" or row["measurement_status"] == "proxy")
        ],
        "required_actual_reopen_conjunction": [
            "valid_package",
            "hash_match",
            "schema_compatible",
            "known_threshold_scenario",
            "valid_trace",
            "admissible_ingestion_path",
            "measured_terms",
            "production_or_shadow_or_canary_source",
            "provenance_attestation",
            "threshold_crossed",
        ],
        "figure_caption": "Evidence-pack replay outcomes showing that package integrity, provenance, measured-source eligibility, ingestion admissibility, and threshold crossing are conjunctive gates before any actual reopen candidate can exist.",
    }


def write_report(summary: dict[str, Any], rows: list[dict[str, str]]) -> None:
    row_lines = "\n".join(
        f"- `{row['pack_id']}`: package `{row['package_integrity_status']}`, pipeline `{row['pipeline_status']}`, final `{row['final_package_decision']}`, blockers `{row['blocking_reasons']}`."
        for row in rows
    )
    REPORT_MD.write_text(
        f"""---
created: 2026-05-13T11:02:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-EVIDENCEPACK-1
---

# Evidence-pack replay harness

M-EVIDENCEPACK-1 packages candidate future trace evidence into a replayable manifest. The harness verifies manifest completeness, schema version, trace SHA-256, privacy attestation, provenance attestation, manifest-to-trace consistency, ingestion-path declaration, threshold scenario mapping, and then delegates the downstream decision to the M-PIPELINE-1 gate. It packages evidence; it does not lower the reopen standard.

Required manifest fields are `pack_id`, `schema_version`, `created_at_utc`, `trace_schema_version`, `trace_file`, `trace_sha256`, `ingestion_path_id`, `evidence_source_type`, `measurement_status`, `provenance_attestation`, `threshold_scenario_id`, `pipeline_expected_status`, and `privacy_attestation`. A package can become an actual reopen candidate only if the package preconditions and the downstream gate are both satisfied: valid package, hash match, schema compatibility, known threshold scenario, valid trace, admissible ingestion path, measured terms, production/shadow/canary source, provenance attestation, and threshold crossing.

![Evidence-pack replay outcomes showing that package integrity, provenance, measured-source eligibility, ingestion admissibility, and threshold crossing are conjunctive gates before any actual reopen candidate can exist.](../data/evidence_pack_replay_flow.png)

## Replay Results

{row_lines}

## Interpretation

The committed fixtures are privacy-safe stand-ins and report `actual_reopen_candidate_count = {summary['actual_reopen_candidate_count']}`. The bad-hash and missing-attestation packages are rejected before threshold evaluation, while the synthetic counterfactual reaches the threshold-crossed arithmetic branch but remains non-actual because its source and ingestion path are not eligible production evidence. Future measured production, shadow, or canary packages must pass the same manifest and downstream gates before they can challenge the Phase 2 downgrade.
""",
        encoding="utf-8",
    )


def replay_manifests(paths: list[Path]) -> list[dict[str, str]]:
    return [evaluate_manifest(path) for path in paths]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        paths = [workspace_path(arg) for arg in argv]
    else:
        write_default_manifests()
        paths = MANIFESTS
    rows = replay_manifests(paths)
    summary = build_summary(rows)
    write_results(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_png(rows)
    write_report(summary, rows)
    for path in paths:
        print(f"replayed {path}")
    print(f"wrote {RESULTS_CSV}")
    print(f"wrote {SUMMARY_JSON}")
    print(f"wrote {OUTPUT_PNG}")
    print(f"wrote {REPORT_MD}")
    print(f"final_package_decision_counts: {summary['final_package_decision_counts']}")
    print(f"actual_reopen_candidate_count: {summary['actual_reopen_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
