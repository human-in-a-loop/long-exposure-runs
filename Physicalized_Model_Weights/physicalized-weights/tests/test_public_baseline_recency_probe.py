# created: 2026-05-13T21:10:00Z
# cycle: 13
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-PUBLICBASE-1
"""Direct tests for M-PUBLICBASE-1 public baseline recency probe."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights" / "scripts" / "public_baseline_recency_probe.py"
DATA = ROOT / "physicalized-weights" / "data"
REPORT = ROOT / "physicalized-weights" / "docs" / "public_baseline_recency_report.md"
REFERENCES = ROOT / "REFERENCES.md"

spec = importlib.util.spec_from_file_location("public_baseline_recency_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["public_baseline_recency_probe"] = probe
spec.loader.exec_module(probe)


def regenerate() -> dict[str, object]:
    probe.main()
    with (DATA / "public_baseline_recency_summary.json").open() as handle:
        return json.load(handle)


def test_reference_ids_are_present_for_every_cited_source() -> None:
    regenerate()
    refs = set(re.findall(r"^\[(\d+)\]", REFERENCES.read_text(), flags=re.MULTILINE))
    with (DATA / "public_baseline_sources.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["reference_id"] for row in rows}.issubset(refs)


def test_sources_record_required_materiality_fields() -> None:
    regenerate()
    with (DATA / "public_baseline_sources.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "release_name",
        "benchmark_suite_workloads",
        "hardware_families_mentioned",
        "directly_usable_in_existing_model",
        "satisfies_measured_hybrid_reopen",
    }
    assert rows
    for row in rows:
        assert required.issubset(row)
        assert all(row[field] for field in required)
        assert row["satisfies_measured_hybrid_reopen"] == "no"
    assert any(row["release_name"] == "MLPerf Inference v6.0" for row in rows)


def test_newer_public_benchmark_sources_cannot_set_actual_reopen_candidate_count() -> None:
    summary = regenerate()
    assert summary["newer_than_campaign_reference"] is True
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["phase4_reopen_path_satisfied"] is False


def test_public_sources_do_not_reopen_physicalized_claim() -> None:
    summary = regenerate()
    assert summary["public_sources_reopen_physicalized_claim"] is False
    assert summary["current_artifacts_reopen"] is False


def test_model_refresh_recommendation_is_primary_material_not_vendor_only() -> None:
    summary = regenerate()
    with (DATA / "public_baseline_delta_matrix.csv").open(newline="") as handle:
        deltas = list(csv.DictReader(handle))
    with (DATA / "public_baseline_sources.csv").open(newline="") as handle:
        sources = list(csv.DictReader(handle))
    if summary["model_refresh_recommended"]:
        assert any(
            row["recommended_action"] == "future_model_refresh_recommended" and row["materiality"] == "material"
            for row in deltas
        )
        assert summary["vendor_only_sources_drive_refresh"] is False
        assert any(row["publisher"] == "MLCommons" and row["primary_or_secondary"] == "primary" for row in sources)


def test_endpoint_counters_remain_zero_or_false() -> None:
    summary = regenerate()
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False


def test_report_distinguishes_benchmark_from_measured_hybrid_evidence() -> None:
    regenerate()
    text = REPORT.read_text()
    assert "not measured hybrid production, shadow, or canary evidence" in text
    assert "cannot satisfy the Phase 4 measured hybrid reopen path" in text
    assert "vendor page is secondary context" in text


def test_outputs_exist_and_schema_is_stable() -> None:
    regenerate()
    expected = [
        DATA / "public_baseline_sources.csv",
        DATA / "public_baseline_delta_matrix.csv",
        DATA / "public_baseline_recency_summary.json",
        DATA / "public_baseline_delta_matrix.png",
        REPORT,
    ]
    for path in expected:
        assert path.exists()
        assert path.stat().st_size > 0
    with (DATA / "public_baseline_delta_matrix.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "baseline_dimension",
            "campaign_assumption",
            "public_update_observation",
            "materiality",
            "directly_calibratable",
            "recommended_action",
            "notes",
        ]
    assert (DATA / "public_baseline_delta_matrix.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def run_tests() -> None:
    for name, func in sorted(globals().items()):
        if name.startswith("test_") and callable(func):
            func()
            print(f"PASS {name}")


if __name__ == "__main__":
    run_tests()
