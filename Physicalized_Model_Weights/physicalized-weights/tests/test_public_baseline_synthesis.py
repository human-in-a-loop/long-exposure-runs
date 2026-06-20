# created: 2026-05-13T22:36:00Z
# cycle: 15
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-SYNTH-1

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "build_public_baseline_synthesis.py"
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"

REQUIRED_CLAIMS = {
    "public_mlperf_recency",
    "programmable_null_strength",
    "direct_energy_calibration_from_public_mlperf",
    "safety_filter_workload_comparability",
    "phase2_downgrade_after_public_refresh",
    "physicalized_reopen_from_public_benchmark",
    "future_model_refresh_scope",
}


def load_builder():
    spec = importlib.util.spec_from_file_location("build_public_baseline_synthesis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_builder() -> dict:
    module = load_builder()
    return module.main()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_summary_preserves_endpoint_counters() -> None:
    summary = run_builder()
    assert summary["public_baseline_refresh_integrated"] is True
    assert summary["phase2_downgrade_preserved"] is True
    assert summary["phase4_reopen_condition_unchanged"] is True
    assert summary["public_sources_reopen_physicalized_claim"] is False
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False


def test_claim_matrix_includes_required_claim_ids() -> None:
    run_builder()
    rows = read_csv(DATA / "public_baseline_synthesis_claim_matrix.csv")
    assert {row["claim_id"] for row in rows} == REQUIRED_CLAIMS


def test_direct_energy_is_not_supported_when_rows_are_zero() -> None:
    summary = run_builder()
    rows = read_csv(DATA / "public_baseline_synthesis_claim_matrix.csv")
    energy = next(row for row in rows if row["claim_id"] == "direct_energy_calibration_from_public_mlperf")
    assert summary["direct_energy_calibration_rows"] == 0
    assert energy["disposition"] == "unsupported"
    assert "energy value is inferred" in energy["notes"]


def test_public_benchmark_does_not_reopen_physicalized_claim() -> None:
    run_builder()
    rows = read_csv(DATA / "public_baseline_synthesis_claim_matrix.csv")
    reopen = next(row for row in rows if row["claim_id"] == "physicalized_reopen_from_public_benchmark")
    assert reopen["disposition"] == "falsified_public_benchmark_only"
    assert "production, shadow, or canary measured hybrid evidence" in reopen["notes"]


def test_final_synthesis_has_addendum_and_unchanged_phase4_rule() -> None:
    run_builder()
    text = (DOCS / "final_synthesis.md").read_text(encoding="utf-8")
    assert "## Post-Closure Public Baseline Refresh" in text
    assert "physicalized-weights/docs/public_baseline_refresh_synthesis.md" in text
    assert "The Phase 4 reopen condition remains unchanged" in text


def test_reproducibility_contains_replay_commands() -> None:
    run_builder()
    text = (DOCS / "reproducibility.md").read_text(encoding="utf-8")
    assert "## Public Baseline Refresh Replay" in text
    assert "python3 physicalized-weights/scripts/public_baseline_recency_probe.py" in text
    assert "python3 physicalized-weights/scripts/public_baseline_prior_refresh.py" in text
    assert "python3 physicalized-weights/scripts/build_public_baseline_synthesis.py" in text


def test_every_claim_support_path_exists() -> None:
    run_builder()
    for row in read_csv(DATA / "public_baseline_synthesis_claim_matrix.csv"):
        for raw_path in row["supporting_artifacts"].split(";"):
            path = ROOT / raw_path.strip()
            assert path.exists(), f"missing support path for {row['claim_id']}: {path}"


def test_manifest_paths_exist_and_summary_schema_is_stable() -> None:
    summary = run_builder()
    for path in [
        DOCS / "public_baseline_refresh_synthesis.md",
        DATA / "public_baseline_synthesis_claim_matrix.csv",
        DATA / "public_baseline_synthesis_manifest.csv",
        DATA / "public_baseline_synthesis_summary.json",
        DATA / "public_baseline_synthesis_flow.png",
    ]:
        assert path.exists()
        assert path.stat().st_size > 0
    manifest = read_csv(DATA / "public_baseline_synthesis_manifest.csv")
    assert manifest
    assert all((ROOT / row["artifact_path"]).exists() for row in manifest)
    persisted = json.loads((DATA / "public_baseline_synthesis_summary.json").read_text(encoding="utf-8"))
    assert persisted["schema_version"] == 1
    assert persisted["milestone_id"] == "M-PUBLICBASE-SYNTH-1"
    assert persisted["programmable_null_effect"] == summary["programmable_null_effect"]


if __name__ == "__main__":
    tests = [
        test_summary_preserves_endpoint_counters,
        test_claim_matrix_includes_required_claim_ids,
        test_direct_energy_is_not_supported_when_rows_are_zero,
        test_public_benchmark_does_not_reopen_physicalized_claim,
        test_final_synthesis_has_addendum_and_unchanged_phase4_rule,
        test_reproducibility_contains_replay_commands,
        test_every_claim_support_path_exists,
        test_manifest_paths_exist_and_summary_schema_is_stable,
    ]
    for test in tests:
        test()
    print(f"{len(tests)} tests passed")
