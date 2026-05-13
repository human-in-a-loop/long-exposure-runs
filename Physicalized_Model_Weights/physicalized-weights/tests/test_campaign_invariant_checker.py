# created: 2026-05-13T20:32:00Z
# cycle: 12
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-INVARIANT-1

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights/scripts/campaign_invariant_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("campaign_invariant_checker", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["campaign_invariant_checker"] = module
    spec.loader.exec_module(module)
    return module


checker = load_checker()


def run_checker() -> None:
    assert checker.main() == 0


def read_summary() -> dict:
    return json.loads((ROOT / "physicalized-weights/data/campaign_invariant_summary.json").read_text(encoding="utf-8"))


def read_matrix() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/campaign_invariant_matrix.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_summary_reports_zero_contradictions() -> None:
    run_checker()
    summary = read_summary()
    assert summary["contradiction_count"] == 0
    assert summary["artifact_count_checked"] >= 12
    assert summary["json_artifact_count_checked"] >= 8
    assert summary["markdown_artifact_count_checked"] >= 4


def test_endpoint_counters_remain_zero_or_false() -> None:
    run_checker()
    summary = read_summary()
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False
    assert summary["introduced_new_gate"] is False


def test_every_contradiction_free_artifact_has_matrix_row() -> None:
    run_checker()
    rows = read_matrix()
    contradiction_artifacts = {row["artifact_path"] for row in rows if row["status"] == "contradiction"}
    for artifact in {row["artifact_path"] for row in rows} - contradiction_artifacts:
        assert any(row["artifact_path"] == artifact for row in rows), artifact


def test_core_summary_milestone_ownership_is_preserved_without_manifest_rows() -> None:
    run_checker()
    rows = read_matrix()
    owners = {row["artifact_path"]: row["milestone_id"] for row in rows}
    assert owners["physicalized-weights/data/closure_archive_summary.json"] == "M-ARCHIVE-1"
    assert owners["physicalized-weights/data/toolchain_condition_summary.json"] == "M-TOOLCHAIN-1"


def test_synthetic_fixture_with_nonzero_superiority_is_contradiction() -> None:
    fixture = ROOT / "physicalized-weights/data/tmp_invariant_bad_fixture.json"
    fixture.write_text(json.dumps({"current_superiority_claim_count": 1}), encoding="utf-8")
    try:
        rows = checker.json_rows(str(fixture.relative_to(ROOT)), [])
        match = [row for row in rows if row["invariant_name"] == "current_superiority_claim_count"][0]
        assert match["status"] == "contradiction"
        assert match["observed_value"] == "1"
    finally:
        fixture.unlink(missing_ok=True)


def test_ambiguous_text_is_warning_not_contradiction() -> None:
    fixture = ROOT / "physicalized-weights/docs/tmp_invariant_ambiguous_fixture.md"
    fixture.write_text("This artifact mentions wins without asserting a current endpoint.\n", encoding="utf-8")
    try:
        rows = checker.markdown_rows(str(fixture.relative_to(ROOT)), [])
        assert rows[0]["status"] == "warning_ambiguous_text"
        assert rows[0]["status"] != "contradiction"
    finally:
        fixture.unlink(missing_ok=True)


def test_report_explicitly_says_no_new_reopen_gate() -> None:
    run_checker()
    report = (ROOT / "physicalized-weights/docs/campaign_invariant_report.md").read_text(encoding="utf-8")
    assert "does not create a new reopen gate" in report
    assert "consistency QA only" in report


def test_outputs_exist_and_png_header_is_valid() -> None:
    run_checker()
    expected = [
        ROOT / "physicalized-weights/docs/campaign_invariant_report.md",
        ROOT / "physicalized-weights/data/campaign_invariant_matrix.csv",
        ROOT / "physicalized-weights/data/campaign_invariant_summary.json",
        ROOT / "physicalized-weights/data/campaign_invariant_matrix.png",
    ]
    for path in expected:
        assert path.exists(), path
        assert path.stat().st_size > 0, path
    assert expected[-1].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def run_tests() -> None:
    tests = [
        test_summary_reports_zero_contradictions,
        test_endpoint_counters_remain_zero_or_false,
        test_every_contradiction_free_artifact_has_matrix_row,
        test_core_summary_milestone_ownership_is_preserved_without_manifest_rows,
        test_synthetic_fixture_with_nonzero_superiority_is_contradiction,
        test_ambiguous_text_is_warning_not_contradiction,
        test_report_explicitly_says_no_new_reopen_gate,
        test_outputs_exist_and_png_header_is_valid,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
