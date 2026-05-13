# created: 2026-05-13T11:02:00Z
# cycle: 3
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-EVIDENCEPACK-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "physicalized-weights" / "scripts" / "evidence_pack_replay.py"
spec = importlib.util.spec_from_file_location("evidence_pack_replay", SCRIPT_PATH)
replay = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["evidence_pack_replay"] = replay
spec.loader.exec_module(replay)


def load_results() -> dict[str, dict[str, str]]:
    with replay.RESULTS_CSV.open(newline="") as f:
        return {row["pack_id"]: row for row in csv.DictReader(f)}


def load_summary() -> dict[str, object]:
    return json.loads(replay.SUMMARY_JSON.read_text())


def test_valid_synthetic_package_replays_without_reopening() -> None:
    row = load_results()["valid_synthetic_proxy"]
    assert row["package_integrity_status"] == "valid_package"
    assert row["pipeline_status"] == "valid_but_insufficient"
    assert row["actual_reopen_candidate"] == "False"


def test_measured_shadow_non_crossing_package_remains_non_reopening() -> None:
    row = load_results()["shadow_non_crossing"]
    assert row["package_integrity_status"] == "valid_package"
    assert row["pipeline_status"] == "threshold_evaluable_not_crossed"
    assert row["threshold_status"] == "not_crossed"
    assert row["actual_reopen_candidate"] == "False"


def test_synthetic_counterfactual_crossing_remains_non_actual() -> None:
    row = load_results()["synthetic_counterfactual_crossed"]
    assert row["package_integrity_status"] == "valid_package"
    assert row["pipeline_status"] == "synthetic_counterfactual_crossed"
    assert row["threshold_status"] == "crossed"
    assert row["actual_reopen_candidate"] == "False"
    assert "source_type=synthetic" in row["blocking_reasons"]


def test_missing_provenance_attestation_blocks_before_threshold() -> None:
    row = load_results()["missing_provenance_attestation"]
    assert row["package_integrity_status"] == "invalid_package"
    assert row["pipeline_status"] == "not_run"
    assert row["threshold_status"] == "not_evaluated"
    assert "provenance_attestation=false" in row["blocking_reasons"]


def test_bad_trace_hash_blocks_before_threshold_evaluation() -> None:
    row = load_results()["bad_trace_hash"]
    assert row["package_integrity_status"] == "invalid_package"
    assert row["hash_match"] == "False"
    assert row["threshold_status"] == "not_evaluated"
    assert "trace_sha256_mismatch" in row["blocking_reasons"]


def test_schema_version_mismatch_blocks() -> None:
    manifest_path = temp_manifest("schema_mismatch")
    manifest = json.loads(replay.MANIFESTS[1].read_text())
    manifest["pack_id"] = "schema_mismatch"
    manifest["schema_version"] = 2
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    row = replay.evaluate_manifest(manifest_path)
    assert row["package_integrity_status"] == "invalid_package"
    assert row["pipeline_status"] == "not_run"
    assert "schema_version_mismatch" in row["blocking_reasons"]


def test_unknown_threshold_scenario_blocks_before_threshold() -> None:
    trace_path = temp_trace("unknown_threshold_scenario")
    replay.pipeline.write_trace(
        trace_path,
        [
            replay.pipeline.base_row(
                1000,
                scenario_id="not_a_known_threshold_scenario",
            )
        ],
    )
    manifest = replay.make_manifest(
        "unknown_threshold_scenario",
        trace_path,
        "shadow_production_dual_run",
        "shadow_production",
        "measured",
        True,
        "not_a_known_threshold_scenario",
        "threshold_evaluable_not_crossed",
    )
    manifest_path = temp_manifest("unknown_threshold_scenario")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    row = replay.evaluate_manifest(manifest_path)
    assert row["package_integrity_status"] == "invalid_package"
    assert row["pipeline_status"] == "not_run"
    assert row["threshold_status"] == "not_evaluated"
    assert "unknown_threshold_scenario_id:not_a_known_threshold_scenario" in row["blocking_reasons"]


def test_invalid_ingestion_path_blocks_downstream_reopen() -> None:
    trace_path = temp_trace("invalid_ingestion")
    replay.pipeline.write_trace(
        trace_path,
        [
            replay.pipeline.base_row(
                1000,
                ingestion_path_id="unknown_ingestion_path",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            )
        ],
    )
    manifest = replay.make_manifest(
        "invalid_ingestion_path",
        trace_path,
        "unknown_ingestion_path",
        "shadow_production",
        "measured",
        True,
        "high_volume_stable_moderation",
        "valid_but_insufficient",
    )
    manifest_path = temp_manifest("invalid_ingestion")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    row = replay.evaluate_manifest(manifest_path)
    assert row["package_integrity_status"] == "valid_package"
    assert row["pipeline_status"] == "valid_but_insufficient"
    assert row["actual_reopen_candidate"] == "False"
    assert "ingestion_class=missing_ingestion_path" in row["blocking_reasons"]


def test_actual_reopen_requires_full_conjunction_and_threshold_crossing() -> None:
    trace_path = temp_trace("actual_candidate_pack")
    replay.pipeline.write_trace(
        trace_path,
        [
            replay.pipeline.base_row(
                1000,
                evidence_source_type="canary_production",
                measurement_environment="production",
                ingestion_path_id="canary_ab_dual_instrumented",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
            replay.pipeline.base_row(
                2000,
                evidence_source_type="canary_production",
                measurement_environment="production",
                ingestion_path_id="canary_ab_dual_instrumented",
                accelerator_energy_proxy_or_measured_pj="3000000000",
                hybrid_energy_proxy_or_measured_pj="1000000000",
            ),
        ],
    )
    manifest = replay.make_manifest(
        "actual_candidate_control",
        trace_path,
        "canary_ab_dual_instrumented",
        "canary_production",
        "measured",
        True,
        "high_volume_stable_moderation",
        "actual_reopen_candidate",
    )
    manifest_path = temp_manifest("actual_candidate_pack")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    row = replay.evaluate_manifest(manifest_path)
    assert row["package_integrity_status"] == "valid_package"
    assert row["hash_match"] == "True"
    assert row["schema_compatible"] == "True"
    assert row["pipeline_status"] == "actual_reopen_candidate"
    assert row["actual_reopen_candidate"] == "True"

    manifest["pack_id"] = "actual_candidate_control_no_privacy"
    manifest["privacy_attestation"] = False
    blocked_path = temp_manifest("actual_candidate_pack_no_privacy")
    blocked_path.write_text(json.dumps(manifest), encoding="utf-8")
    blocked = replay.evaluate_manifest(blocked_path)
    assert blocked["actual_reopen_candidate"] == "False"
    assert blocked["pipeline_status"] == "not_run"
    assert "privacy_attestation=false" in blocked["blocking_reasons"]


def test_current_summary_has_zero_actual_reopen_candidates() -> None:
    summary = load_summary()
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["synthetic_or_proxy_actual_reopen_candidates"] == []
    assert summary["threshold_not_evaluated_count"] >= 1


def test_output_schema_and_figure_are_stable() -> None:
    with replay.RESULTS_CSV.open(newline="") as f:
        assert csv.DictReader(f).fieldnames == replay.FIELDNAMES
    assert replay.OUTPUT_PNG.exists()
    assert replay.OUTPUT_PNG.stat().st_size > 100


def temp_dir() -> Path:
    path = Path(tempfile.gettempdir()) / "physicalized_evidence_pack_tests"
    path.mkdir(exist_ok=True)
    return path


def temp_manifest(name: str) -> Path:
    return temp_dir() / f"{name}.json"


def temp_trace(name: str) -> Path:
    return temp_dir() / f"{name}.csv"


if __name__ == "__main__":
    replay.main([])
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
