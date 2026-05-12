#!/usr/bin/env python3
# created: 2026-05-12T06:15:00Z
# cycle: 27
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-INTAKE-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_SECTIONS = {
    "bundle identity",
    "telemetry payload inventory",
    "join window",
    "provenance",
    "measurement quality",
    "security/privacy",
    "boundary labels",
}
EXPECTED_BLOCKS = {
    "missing_checksum",
    "checksum_mismatch",
    "schema_version_mismatch",
    "missing_adapter_conformance_pointer",
    "unresolved_join_alias",
    "missing_noise_floor",
    "incomplete_security_provenance_stream",
    "stale_collection_window",
    "ambiguous_redaction_policy",
    "invalid_unit",
    "fixture_attempted_production_target",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_png_nonblank(path: Path) -> None:
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.relative_to(ROOT)} is not a PNG"
    assert len(data) > 10_000, f"{path.relative_to(ROOT)} is too small"


def main() -> None:
    schema = read_csv(DATA / "production_intake_bundle_manifest_schema.csv")
    valid_manifest = read_csv(DATA / "production_intake_valid_bundle_manifest.csv")
    invalid_manifest = read_csv(DATA / "production_intake_invalid_bundle_manifests.csv")
    custody = read_csv(DATA / "production_intake_chain_of_custody_requirements.csv")
    results = read_csv(DATA / "production_intake_admission_results.csv")
    failures = read_csv(DATA / "production_intake_failure_modes.csv")
    boundary = read_csv(DATA / "production_intake_downstream_boundary.csv")
    trace = read_csv(DATA / "production_intake_traceability_links.csv")

    assert REQUIRED_SECTIONS <= {row["manifest_section"] for row in schema}
    assert {"file_path", "stream_class", "row_count", "checksum_sha256", "canonical_schema_target"} <= {row["field_name"] for row in schema}
    assert all(row["file_path"] and row["stream_class"] and int(row["row_count"]) > 0 and row["checksum_sha256"] and row["canonical_schema_target"] for row in valid_manifest)
    assert all(len(row["checksum_sha256"]) == 64 for row in valid_manifest)
    assert len(custody) >= 8
    assert any(row["requirement_id"] == "boundary_preserved" for row in custody)

    valid = next(row for row in results if row["bundle_id"] == "valid-intake-bundle")
    assert valid["admission_status"] == "structurally_admissible"
    assert valid["production_target_requested"] == "true"
    assert valid["production_target_granted"] == "false"
    assert valid["evidence_label"] == "production_intake_fixture"
    assert valid["production_calibrated"] == "false"
    assert valid["production_ready"] == "false"
    assert valid["claim_credit_allowed"] == "false"
    assert valid["blocked_reason"] == ""

    invalid = [row for row in results if row["admission_status"] == "blocked"]
    observed = {row["blocked_reason"] for row in invalid}
    assert EXPECTED_BLOCKS <= observed, observed
    assert len(invalid_manifest) == len(invalid)
    assert all(row["expected_blocked_reason"] == row["blocked_reason"] for row in invalid)
    assert any(row["bundle_id"] == "invalid-production-target-fixture" and row["production_target_granted"] == "false" and row["evidence_label"] != "production_target" for row in invalid)

    invalid_unit = next(row for row in results if row["bundle_id"] == "invalid-unit-declaration")
    assert invalid_unit["unit_normalization_attempted"] == "true"
    assert invalid_unit["unit_valid"] == "false"
    assert invalid_unit["blocked_reason"] == "invalid_unit"

    checksum_mismatch = next(row for row in results if row["bundle_id"] == "invalid-checksum-mismatch")
    assert checksum_mismatch["checksum_validation_attempted"] == "true"
    assert checksum_mismatch["checksum_valid"] == "false"
    assert checksum_mismatch["blocked_reason"] == "checksum_mismatch"

    assert all(row["fail_closed"] == "true" for row in failures)
    assert sum(int(row["invalid_bundle_count"]) for row in failures) == len(invalid)
    assert all(row["evidence_label"] == "production_intake_fixture" for row in boundary)
    assert all(row["production_calibrated"] == "false" for row in boundary)
    assert all(row["production_ready"] == "false" for row in boundary)
    assert all(row["claim_credit_allowed"] == "false" for row in boundary)
    assert any(row["bundle_id"] == "valid-intake-bundle" and row["downstream_ingestion_boundary"] == "not_production_evidence_label" for row in boundary)
    assert {row["trace_link_id"] for row in trace} >= {
        "intake-to-adapter-conformance",
        "intake-to-production-ingestion",
        "intake-to-final-readiness",
        "intake-to-handoff",
    }

    for fig in [
        DATA / "production_intake_manifest_coverage.png",
        DATA / "production_intake_failure_modes.png",
        DATA / "production_intake_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: production intake bundle gate verified.")


if __name__ == "__main__":
    main()
