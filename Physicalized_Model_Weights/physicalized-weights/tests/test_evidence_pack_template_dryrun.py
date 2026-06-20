# created: 2026-05-13T13:18:00Z
# cycle: 4
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-DRYRUN-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "evidence_pack_template_dryrun.py"
spec = importlib.util.spec_from_file_location("evidence_pack_template_dryrun", SCRIPT)
dryrun = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["evidence_pack_template_dryrun"] = dryrun
spec.loader.exec_module(dryrun)


def load_results() -> dict[str, dict[str, str]]:
    with dryrun.RESULTS_CSV.open(newline="", encoding="utf-8") as fh:
        return {row["case_id"]: row for row in csv.DictReader(fh)}


def load_summary() -> dict[str, object]:
    return json.loads(dryrun.SUMMARY_JSON.read_text(encoding="utf-8"))


def test_complete_shadow_and_canary_are_ready_not_evidence() -> None:
    rows = load_results()
    for case_id in ["complete_shadow_template", "complete_canary_template"]:
        row = rows[case_id]
        assert row["dryrun_status"] == "ready_for_collection_not_evidence"
        assert row["actual_reopen_candidate"] == "False"
        assert row["is_evidence"] == "False"
        assert row["primary_blocker"] == "none_ready_template_not_evidence"


def test_no_dryrun_case_becomes_actual_reopen_candidate() -> None:
    rows = load_results()
    assert all(row["actual_reopen_candidate"] == "False" for row in rows.values())
    summary = load_summary()
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["dryrun_is_evidence"] is False


def test_raw_content_columns_are_privacy_blocked() -> None:
    row = load_results()["raw_content_column_present"]
    assert row["dryrun_status"] == "privacy_blocked"
    assert "privacy_disallowed_column:content" in row["blocking_reasons"]


def test_placeholder_attestation_is_provenance_blocked() -> None:
    row = load_results()["placeholder_attestation_unreplaced"]
    assert row["dryrun_status"] == "provenance_blocked"
    assert "placeholder_attestation_unreplaced" in row["blocking_reasons"]


def test_unknown_threshold_scenario_is_mapping_blocked() -> None:
    row = load_results()["unknown_threshold_scenario"]
    assert row["dryrun_status"] == "threshold_mapping_blocked"
    assert "unknown_threshold_scenario:unknown_operator_case" in row["blocking_reasons"]


def test_hash_mismatch_is_integrity_blocked() -> None:
    row = load_results()["hash_mismatch"]
    assert row["dryrun_status"] == "integrity_blocked"
    assert row["hash_match"] == "False"
    assert "trace_sha256_mismatch" in row["blocking_reasons"]


def test_source_measurement_contradictions_are_blocked() -> None:
    row = load_results()["proxy_status_with_production_source"]
    assert row["dryrun_status"] == "schema_blocked"
    assert row["source_measurement_consistent"] == "False"
    assert "source_measurement_contradiction" in row["blocking_reasons"]


def test_invalid_manifest_values_and_ingestion_paths_are_blocked() -> None:
    rows = load_results()
    invalid_source = rows["invalid_manifest_source_value"]
    assert invalid_source["dryrun_status"] == "schema_blocked"
    assert (
        "invalid_manifest_value:evidence_source_type:not_a_real_source"
        in invalid_source["blocking_reasons"]
    )

    invalid_ingestion = rows["unknown_ingestion_path"]
    assert invalid_ingestion["dryrun_status"] == "schema_blocked"
    assert (
        "inadmissible_ingestion_path:unknown_ingestion_path"
        in invalid_ingestion["blocking_reasons"]
    )


def test_missing_baseline_or_energy_columns_are_schema_blocked() -> None:
    rows = load_results()
    baseline = rows["missing_counterfactual_baseline_columns"]
    energy = rows["measured_status_without_energy_columns"]
    assert baseline["dryrun_status"] == "schema_blocked"
    assert "missing_trace_column:software_baseline_latency_ns" in baseline["blocking_reasons"]
    assert "missing_trace_column:accelerator_baseline_latency_ns" in baseline["blocking_reasons"]
    assert energy["dryrun_status"] == "schema_blocked"
    assert "missing_trace_column:accelerator_energy_proxy_or_measured_pj" in energy["blocking_reasons"]
    assert "missing_trace_column:hybrid_energy_proxy_or_measured_pj" in energy["blocking_reasons"]


def test_manifest_field_omission_is_template_incomplete() -> None:
    row = load_results()["missing_required_manifest_field"]
    assert row["dryrun_status"] == "template_incomplete"
    assert "missing_required_manifest_field:trace_sha256" in row["blocking_reasons"]


def test_template_files_are_placeholder_safe() -> None:
    manifest = json.loads(dryrun.MANIFEST_TEMPLATE_JSON.read_text(encoding="utf-8"))
    assert manifest["provenance_attestation"] is False
    assert manifest["privacy_attestation"] is False
    with dryrun.TRACE_TEMPLATE_CSV.open(newline="", encoding="utf-8") as fh:
        fields = next(csv.reader(fh))
    assert "content" not in fields
    assert "raw_prompt" not in fields
    assert set(dryrun.trace_columns()).issubset(set(fields))


def test_summary_and_png_are_stable() -> None:
    summary = load_summary()
    assert summary["ready_for_collection_not_evidence_count"] == 2
    assert summary["status_mismatches"] == []
    assert dryrun.MATRIX_PNG.exists()
    assert dryrun.MATRIX_PNG.stat().st_size > 100


def run() -> int:
    dryrun.main()
    tests = [
        test_complete_shadow_and_canary_are_ready_not_evidence,
        test_no_dryrun_case_becomes_actual_reopen_candidate,
        test_raw_content_columns_are_privacy_blocked,
        test_placeholder_attestation_is_provenance_blocked,
        test_unknown_threshold_scenario_is_mapping_blocked,
        test_hash_mismatch_is_integrity_blocked,
        test_source_measurement_contradictions_are_blocked,
        test_invalid_manifest_values_and_ingestion_paths_are_blocked,
        test_missing_baseline_or_energy_columns_are_schema_blocked,
        test_manifest_field_omission_is_template_incomplete,
        test_template_files_are_placeholder_safe,
        test_summary_and_png_are_stable,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
