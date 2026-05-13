# created: 2026-05-13T13:18:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-DRYRUN-1

"""Generate and dry-run operator evidence-pack templates before collection."""

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

TRACE_SCHEMA_JSON = DATA / "production_trace_schema.json"
MANIFEST_SCHEMA_JSON = DATA / "evidence_pack_manifest_schema.json"
REOPEN_THRESHOLDS_CSV = DATA / "reopen_thresholds.csv"
INGESTION_PATH_SCORES_CSV = DATA / "trace_ingestion_path_scores.csv"

DOC_MD = DOCS / "operator_evidence_pack_template.md"
MANIFEST_TEMPLATE_JSON = DATA / "operator_evidence_pack_manifest_template.json"
TRACE_TEMPLATE_CSV = DATA / "operator_trace_template.csv"
ATTESTATION_TEMPLATE_MD = DATA / "operator_provenance_attestation_template.md"
CASES_CSV = DATA / "evidence_pack_dryrun_cases.csv"
RESULTS_CSV = DATA / "evidence_pack_dryrun_results.csv"
SUMMARY_JSON = DATA / "evidence_pack_dryrun_summary.json"
MATRIX_PNG = DATA / "evidence_pack_dryrun_status_matrix.png"

MILESTONE_ID = "M-DRYRUN-1"
PLACEHOLDER = "REPLACE_BEFORE_COLLECTION"
FUTURE_REOPEN_CONDITION = (
    "valid_package ∧ hash_match ∧ schema_compatible ∧ known_threshold_scenario ∧ "
    "valid_trace ∧ admissible_ingestion_path ∧ measured_terms ∧ "
    "production_or_shadow_or_canary_source ∧ provenance_attestation ∧ "
    "privacy_attestation ∧ threshold_crossed"
)
FIGURE_CAPTION = (
    "Dry-run acceptance outcomes for operator evidence-pack templates, showing "
    "which package-preparation errors block collection readiness while all "
    "placeholder packages remain non-evidence."
)

STATUS_ORDER = [
    "ready_for_collection_not_evidence",
    "template_incomplete",
    "privacy_blocked",
    "integrity_blocked",
    "provenance_blocked",
    "schema_blocked",
    "threshold_mapping_blocked",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def trace_columns() -> list[str]:
    schema = read_json(TRACE_SCHEMA_JSON)
    return [str(col["name"]) for col in schema["columns"] if col.get("required")]


def privacy_disallowed_columns() -> set[str]:
    schema = read_json(TRACE_SCHEMA_JSON)
    return {str(col).lower() for col in schema["privacy_disallowed_columns"]}


def required_manifest_fields() -> list[str]:
    return [str(field) for field in read_json(MANIFEST_SCHEMA_JSON)["required_fields"]]


def manifest_allowed_values() -> dict[str, list[Any]]:
    return dict(read_json(MANIFEST_SCHEMA_JSON).get("allowed_values", {}))


def allowed_threshold_scenarios() -> list[str]:
    with REOPEN_THRESHOLDS_CSV.open(newline="", encoding="utf-8") as fh:
        return [row["scenario_id"] for row in csv.DictReader(fh)]


def allowed_ingestion_paths() -> list[str]:
    with INGESTION_PATH_SCORES_CSV.open(newline="", encoding="utf-8") as fh:
        return [
            row["path_id"]
            for row in csv.DictReader(fh)
            if row["classification"] == "reopen_candidate_path"
        ]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def write_trace_template() -> None:
    with TRACE_TEMPLATE_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(trace_columns())


def manifest_template(trace_hash: str) -> dict[str, Any]:
    return {
        "pack_id": "shadow_or_canary_pack_id_REPLACE_BEFORE_COLLECTION",
        "schema_version": 1,
        "created_at_utc": "REPLACE_BEFORE_COLLECTION_UTC_TIMESTAMP",
        "trace_schema_version": 1,
        "trace_file": relative(TRACE_TEMPLATE_CSV),
        "trace_sha256": trace_hash,
        "ingestion_path_id": "shadow_production_dual_run",
        "evidence_source_type": "shadow_production",
        "measurement_status": "measured",
        "provenance_attestation": False,
        "threshold_scenario_id": "high_volume_stable_moderation",
        "pipeline_expected_status": "threshold_evaluable_not_crossed",
        "privacy_attestation": False,
        "operator_replace_before_collection": [
            "pack_id",
            "created_at_utc",
            "trace_file",
            "trace_sha256",
            "provenance_attestation",
            "privacy_attestation",
            "threshold_scenario_id",
            "pipeline_expected_status",
        ],
        "dryrun_notice": (
            "Template only. This file is not measured evidence and cannot satisfy "
            "measured_terms or threshold_crossed."
        ),
    }


def write_manifest_template() -> None:
    trace_hash = sha256_file(TRACE_TEMPLATE_CSV)
    MANIFEST_TEMPLATE_JSON.write_text(
        json.dumps(manifest_template(trace_hash), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_attestation_template() -> None:
    ATTESTATION_TEMPLATE_MD.write_text(
        """---
created: 2026-05-13T13:18:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-DRYRUN-1
---

# Operator provenance and privacy attestation template

Replace every `REPLACE_BEFORE_COLLECTION` token before measured collection.

- Source: I attest that the trace source is `REPLACE_BEFORE_COLLECTION` and is one of production, shadow production, or canary production.
- Privacy: I attest that the trace contains no prompt, raw text, raw user identifier, tenant identifier, API key, email, IP address, or content column.
- Measurement status: I attest that accelerator and hybrid latency and energy terms are measured for the same request window, not proxy, modeled, or mixed.
- Policy window: I attest that policy hashes are consistent within the collection window except for explicitly logged update or rollback events.
- Counterfactual baseline: I attest that the programmable accelerator baseline and hybrid path were collected for the same request classes, fallback decisions, audit logging, utilization, and policy window.
- Hash provenance: I attest that the manifest trace SHA-256 was generated after final trace export and before evidence-pack replay.

Dry-run templates are not evidence. A future measured package must replace this attestation with signed operator-specific language before it can enter M-EVIDENCEPACK-1.
""",
        encoding="utf-8",
    )


def write_doc() -> None:
    cols = ", ".join(f"`{name}`" for name in trace_columns())
    manifest_fields = ", ".join(f"`{name}`" for name in required_manifest_fields())
    scenarios = ", ".join(f"`{name}`" for name in allowed_threshold_scenarios())
    ingestion_paths = ", ".join(f"`{name}`" for name in allowed_ingestion_paths())
    DOC_MD.write_text(
        f"""---
created: 2026-05-13T13:18:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-DRYRUN-1
---

# Operator evidence-pack template

M-DRYRUN-1 gives an operator a package skeleton to check before measured shadow or canary collection. It sits before M-EVIDENCEPACK-1 and rejects assembly mistakes early; it does not weaken replay requirements and it cannot reopen the Phase 2 downgrade.

Required manifest fields are: {manifest_fields}. The canonical manifest template is `physicalized-weights/data/operator_evidence_pack_manifest_template.json`.

Required trace columns are: {cols}. The trace template is header-only and intentionally contains no raw content fields.

Privacy exclusions are `prompt`, `raw_prompt`, `raw_text`, `user_id`, `raw_user_id`, `tenant_id`, `tenant_name`, `api_key`, `email`, `ip_address`, and `content`. Any template that introduces one of those columns is blocked before collection.

Allowed threshold scenario IDs are: {scenarios}. The operator must select one known scenario before collection and must not leave it ambiguous.

Allowed dry-run ingestion paths are: {ingestion_paths}. Other M-INGEST-1 paths remain diagnostic or inadmissible at this layer and cannot be marked ready for measured collection.

Generate the trace hash after final trace export:

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path
path = Path("physicalized-weights/data/operator_trace_template.csv")
print(hashlib.sha256(path.read_bytes()).hexdigest())
PY
```

The provenance attestation template is `physicalized-weights/data/operator_provenance_attestation_template.md`. Replace every placeholder with source, privacy, measurement, policy-window, counterfactual-baseline, and hash-provenance statements before measured collection.

Expected dry-run statuses are `ready_for_collection_not_evidence`, `template_incomplete`, `privacy_blocked`, `integrity_blocked`, `provenance_blocked`, `schema_blocked`, and `threshold_mapping_blocked`. A ready dry-run remains non-evidence because it has no measured trace rows, no measured margin, and no threshold crossing.

![{FIGURE_CAPTION}](../data/evidence_pack_dryrun_status_matrix.png)
""",
        encoding="utf-8",
    )


def default_cases() -> list[dict[str, str]]:
    return [
        {
            "case_id": "complete_shadow_template",
            "description": "Complete shadow-production dry-run with safe dummy values.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "ready_for_collection_not_evidence",
        },
        {
            "case_id": "complete_canary_template",
            "description": "Complete canary dry-run with safe dummy values.",
            "source": "canary_production",
            "measurement_status": "measured",
            "ingestion_path_id": "canary_ab_dual_instrumented",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "ready_for_collection_not_evidence",
        },
        {
            "case_id": "missing_required_manifest_field",
            "description": "Manifest omits trace_sha256.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "trace_sha256",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "template_incomplete",
        },
        {
            "case_id": "raw_content_column_present",
            "description": "Trace header adds raw content.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "content",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "privacy_blocked",
        },
        {
            "case_id": "placeholder_attestation_unreplaced",
            "description": "Attestation remains placeholder text.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "false",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "provenance_blocked",
        },
        {
            "case_id": "unknown_threshold_scenario",
            "description": "Scenario mapping is not in reopen thresholds.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "unknown_operator_case",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "threshold_mapping_blocked",
        },
        {
            "case_id": "hash_mismatch",
            "description": "Manifest hash does not match trace template.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "mismatch",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "integrity_blocked",
        },
        {
            "case_id": "proxy_status_with_production_source",
            "description": "Production source declares proxy measurement.",
            "source": "production",
            "measurement_status": "proxy",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "schema_blocked",
        },
        {
            "case_id": "invalid_manifest_source_value",
            "description": "Manifest source is outside the evidence-pack schema allow-list.",
            "source": "not_a_real_source",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "schema_blocked",
        },
        {
            "case_id": "unknown_ingestion_path",
            "description": "Manifest ingestion path is not a reopen-candidate path.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "unknown_ingestion_path",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "false",
            "expected_status": "schema_blocked",
        },
        {
            "case_id": "missing_counterfactual_baseline_columns",
            "description": "Trace header omits baseline latency columns.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "software_baseline_latency_ns|accelerator_baseline_latency_ns",
            "drop_energy_columns": "false",
            "expected_status": "schema_blocked",
        },
        {
            "case_id": "measured_status_without_energy_columns",
            "description": "Measured package lacks energy columns.",
            "source": "shadow_production",
            "measurement_status": "measured",
            "ingestion_path_id": "shadow_production_dual_run",
            "threshold_scenario_id": "high_volume_stable_moderation",
            "manifest_missing_field": "",
            "extra_trace_column": "",
            "attestation_replaced": "true",
            "hash_mode": "match",
            "drop_trace_columns": "",
            "drop_energy_columns": "true",
            "expected_status": "schema_blocked",
        },
    ]


def write_cases() -> None:
    rows = default_cases()
    with CASES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_cases() -> list[dict[str, str]]:
    with CASES_CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def case_headers(row: dict[str, str]) -> list[str]:
    columns = trace_columns()
    drops = {name for name in row["drop_trace_columns"].split("|") if name}
    if parse_bool(row["drop_energy_columns"]):
        drops.update(
            {
                "accelerator_energy_proxy_or_measured_pj",
                "accelerator_energy_status",
                "hybrid_energy_proxy_or_measured_pj",
                "hybrid_energy_status",
            }
        )
    columns = [name for name in columns if name not in drops]
    if row["extra_trace_column"]:
        columns.append(row["extra_trace_column"])
    return columns


def trace_hash_for_headers(headers: list[str]) -> str:
    content = ",".join(headers) + "\r\n"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def case_manifest(row: dict[str, str], headers: list[str]) -> dict[str, Any]:
    manifest = {
        "pack_id": row["case_id"],
        "schema_version": 1,
        "created_at_utc": "2026-05-13T13:18:00Z",
        "trace_schema_version": 1,
        "trace_file": relative(TRACE_TEMPLATE_CSV),
        "trace_sha256": trace_hash_for_headers(headers),
        "ingestion_path_id": row["ingestion_path_id"],
        "evidence_source_type": row["source"],
        "measurement_status": row["measurement_status"],
        "provenance_attestation": parse_bool(row["attestation_replaced"]),
        "threshold_scenario_id": row["threshold_scenario_id"],
        "pipeline_expected_status": "threshold_evaluable_not_crossed",
        "privacy_attestation": True,
    }
    if row["hash_mode"] == "mismatch":
        manifest["trace_sha256"] = "0" * 64
    if row["manifest_missing_field"]:
        manifest.pop(row["manifest_missing_field"], None)
    return manifest


def status_from_blockers(blockers: list[str]) -> str:
    priority = [
        ("missing_required_manifest_field:", "template_incomplete"),
        ("privacy_disallowed_column:", "privacy_blocked"),
        ("trace_sha256_mismatch", "integrity_blocked"),
        ("placeholder_attestation_unreplaced", "provenance_blocked"),
        ("unknown_threshold_scenario:", "threshold_mapping_blocked"),
        ("invalid_manifest_value:", "schema_blocked"),
        ("inadmissible_ingestion_path:", "schema_blocked"),
        ("missing_trace_column:", "schema_blocked"),
        ("source_measurement_contradiction", "schema_blocked"),
    ]
    for prefix, status in priority:
        if any(blocker.startswith(prefix) for blocker in blockers):
            return status
    return "ready_for_collection_not_evidence"


def evaluate_case(row: dict[str, str]) -> dict[str, str]:
    headers = case_headers(row)
    manifest = case_manifest(row, headers)
    blockers: list[str] = []

    for field in required_manifest_fields():
        if field not in manifest:
            blockers.append(f"missing_required_manifest_field:{field}")

    for field, allowed in manifest_allowed_values().items():
        if field in manifest and manifest[field] not in allowed:
            blockers.append(f"invalid_manifest_value:{field}:{manifest[field]}")

    if manifest.get("ingestion_path_id") not in allowed_ingestion_paths():
        blockers.append(f"inadmissible_ingestion_path:{manifest.get('ingestion_path_id')}")

    disallowed = privacy_disallowed_columns()
    for column in headers:
        if column.lower() in disallowed:
            blockers.append(f"privacy_disallowed_column:{column}")

    for column in trace_columns():
        if column not in headers:
            blockers.append(f"missing_trace_column:{column}")

    if manifest.get("threshold_scenario_id") not in allowed_threshold_scenarios():
        blockers.append(f"unknown_threshold_scenario:{manifest.get('threshold_scenario_id')}")

    if "trace_sha256" in manifest and manifest["trace_sha256"] != trace_hash_for_headers(headers):
        blockers.append("trace_sha256_mismatch")

    if not parse_bool(row["attestation_replaced"]):
        blockers.append("placeholder_attestation_unreplaced")

    production_like = {"production", "shadow_production", "canary_production"}
    if row["source"] in production_like and row["measurement_status"] != "measured":
        blockers.append("source_measurement_contradiction")

    status = status_from_blockers(blockers)
    return {
        "case_id": row["case_id"],
        "dryrun_status": status,
        "expected_status": row["expected_status"],
        "status_matches_expected": str(status == row["expected_status"]),
        "actual_reopen_candidate": "False",
        "is_evidence": "False",
        "manifest_complete": str(
            not any(b.startswith("missing_required_manifest_field:") for b in blockers)
        ),
        "trace_schema_headers_present": str(
            not any(b.startswith("missing_trace_column:") for b in blockers)
        ),
        "privacy_safe_header": str(
            not any(b.startswith("privacy_disallowed_column:") for b in blockers)
        ),
        "known_threshold_scenario": str(
            not any(b.startswith("unknown_threshold_scenario:") for b in blockers)
        ),
        "hash_match": str("trace_sha256_mismatch" not in blockers),
        "attestation_replaced": str("placeholder_attestation_unreplaced" not in blockers),
        "source_measurement_consistent": str(
            "source_measurement_contradiction" not in blockers
        ),
        "primary_blocker": "none_ready_template_not_evidence" if not blockers else blockers[0],
        "blocking_reasons": "none" if not blockers else "|".join(blockers),
    }


FIELDNAMES = [
    "case_id",
    "dryrun_status",
    "expected_status",
    "status_matches_expected",
    "actual_reopen_candidate",
    "is_evidence",
    "manifest_complete",
    "trace_schema_headers_present",
    "privacy_safe_header",
    "known_threshold_scenario",
    "hash_match",
    "attestation_replaced",
    "source_measurement_consistent",
    "primary_blocker",
    "blocking_reasons",
]


def write_results(rows: list[dict[str, str]]) -> None:
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def build_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    counts = Counter(row["dryrun_status"] for row in rows)
    mismatches = [row["case_id"] for row in rows if row["status_matches_expected"] != "True"]
    return {
        "schema_version": 1,
        "milestone_id": MILESTONE_ID,
        "status": "validated",
        "case_count": len(rows),
        "dryrun_status_counts": dict(sorted(counts.items())),
        "ready_for_collection_not_evidence_count": counts["ready_for_collection_not_evidence"],
        "actual_reopen_candidate_count": 0,
        "current_artifacts_reopen": False,
        "dryrun_is_evidence": False,
        "status_mismatches": mismatches,
        "required_trace_column_count": len(trace_columns()),
        "required_manifest_fields": required_manifest_fields(),
        "allowed_threshold_scenarios": allowed_threshold_scenarios(),
        "allowed_ingestion_paths": allowed_ingestion_paths(),
        "future_reopen_condition": FUTURE_REOPEN_CONDITION,
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The dry-run package layer proves structural readiness only. Complete "
            "shadow/canary templates can be ready for measured collection, but all "
            "template artifacts remain non-evidence because they lack measured trace "
            "rows, measured terms, and threshold crossing."
        ),
    }


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 980, 430
    pixels = bytearray([255, 255, 255] * width * height)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                idx = (y * width + x) * 3
                pixels[idx : idx + 3] = bytes(color)

    colors = {
        "ready_for_collection_not_evidence": (70, 135, 92),
        "template_incomplete": (177, 119, 62),
        "privacy_blocked": (172, 70, 68),
        "integrity_blocked": (111, 88, 160),
        "provenance_blocked": (91, 109, 161),
        "schema_blocked": (203, 146, 61),
        "threshold_mapping_blocked": (128, 92, 73),
    }
    rect(42, 42, 928, 350, (239, 242, 245))
    for idx, row in enumerate(rows):
        x0 = 66 + idx * 84
        color = colors[row["dryrun_status"]]
        rect(x0, 126, x0 + 48, 318, color)
        rect(x0 + 16, 84, x0 + 32, 106, (93, 99, 110))
    for idx, status in enumerate(STATUS_ORDER):
        x0 = 572
        y0 = 28 + idx * 20
        rect(x0, y0, x0 + 20, y0 + 12, colors[status])
    raw = b"".join(
        b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3]
        for y in range(height)
    )
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += png_chunk(b"IDAT", zlib.compress(raw, 9))
    png += png_chunk(b"IEND", b"")
    MATRIX_PNG.write_bytes(png)


def generate_templates_and_cases() -> None:
    write_trace_template()
    write_manifest_template()
    write_attestation_template()
    write_doc()
    write_cases()


def main() -> int:
    generate_templates_and_cases()
    rows = [evaluate_case(row) for row in read_cases()]
    write_results(rows)
    summary = build_summary(rows)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_png(rows)
    for path in [
        DOC_MD,
        MANIFEST_TEMPLATE_JSON,
        TRACE_TEMPLATE_CSV,
        ATTESTATION_TEMPLATE_MD,
        CASES_CSV,
        RESULTS_CSV,
        SUMMARY_JSON,
        MATRIX_PNG,
    ]:
        print(f"wrote {path}")
    print(f"dryrun_status_counts: {summary['dryrun_status_counts']}")
    print(f"actual_reopen_candidate_count: {summary['actual_reopen_candidate_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
