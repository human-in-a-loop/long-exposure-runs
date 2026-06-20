# created: 2026-05-13T19:38:00Z
# cycle: 10
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ARCHIVE-1

from __future__ import annotations

import csv
import importlib.util
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "physicalized-weights/scripts/build_closure_archive_index.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_closure_archive_index", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules["build_closure_archive_index"] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


def run_builder() -> None:
    assert builder.main() == 0


def read_summary() -> dict:
    return json.loads((ROOT / "physicalized-weights/data/closure_archive_summary.json").read_text(encoding="utf-8"))


def read_manifest() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/closure_archive_manifest.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_closure_claims() -> list[dict[str, str]]:
    with (ROOT / "physicalized-weights/data/campaign_closure_claim_disposition.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_required_counters_preserve_closed_state() -> None:
    run_builder()
    summary = read_summary()
    assert summary["canonical_artifact_count"] > 40
    assert summary["missing_canonical_artifact_count"] == 0
    assert summary["zero_size_canonical_artifact_count"] == 0
    assert summary["current_superiority_claim_count"] == 0
    assert summary["actual_reopen_candidate_count"] == 0
    assert summary["new_reopen_gate_count"] == 0
    assert summary["current_artifacts_reopen"] is False
    assert summary["known_warning_count"] >= 2


def test_every_canonical_artifact_exists_and_hashes() -> None:
    run_builder()
    hex64 = re.compile(r"^[0-9a-f]{64}$")
    for row in read_manifest():
        if row["canonical"] != "true":
            continue
        assert row["exists"] == "true", row["artifact_path"]
        assert int(row["size_bytes"]) > 0, row["artifact_path"]
        assert hex64.match(row["sha256"]), row["artifact_path"]


def test_closure_claim_supports_are_present_in_archive_manifest() -> None:
    run_builder()
    manifest_paths = {row["artifact_path"] for row in read_manifest()}
    for claim in read_closure_claims():
        supports = [item.strip() for item in claim["supporting_artifacts"].split(";") if item.strip()]
        assert supports, claim["claim_id"]
        for support in supports:
            assert support in manifest_paths, f"{claim['claim_id']} support missing from archive: {support}"


def test_no_fixture_row_is_labeled_measured_production_evidence() -> None:
    run_builder()
    guarded = ["synthetic", "proxy", "template", "dry-run", "dryrun", "rehearsal"]
    for row in read_manifest():
        text = " ".join(row.values()).lower()
        if any(word in text for word in guarded):
            assert row["artifact_class"] != "measured_production_evidence", row["artifact_path"]
            assert "measured production evidence" not in row["notes"].lower(), row["artifact_path"]


def test_no_new_reopen_gate() -> None:
    run_builder()
    assert read_summary()["new_reopen_gate_count"] == 0


def test_outputs_exist_and_figure_is_embedded() -> None:
    run_builder()
    expected = [
        ROOT / "physicalized-weights/docs/closure_archive_index.md",
        ROOT / "physicalized-weights/data/closure_archive_manifest.csv",
        ROOT / "physicalized-weights/data/closure_archive_manifest.json",
        ROOT / "physicalized-weights/data/closure_archive_summary.json",
        ROOT / "physicalized-weights/data/closure_archive_coverage.png",
    ]
    for path in expected:
        assert path.exists(), path
        assert path.stat().st_size > 0, path
    png = expected[-1].read_bytes()
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    doc = expected[0].read_text(encoding="utf-8")
    assert "](../data/closure_archive_coverage.png)" in doc


def run_tests() -> None:
    tests = [
        test_required_counters_preserve_closed_state,
        test_every_canonical_artifact_exists_and_hashes,
        test_closure_claim_supports_are_present_in_archive_manifest,
        test_no_fixture_row_is_labeled_measured_production_evidence,
        test_no_new_reopen_gate,
        test_outputs_exist_and_figure_is_embedded,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")


if __name__ == "__main__":
    run_tests()
