#!/usr/bin/env python3
# created: 2026-05-12T09:20:00Z
# cycle: 30
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-GATECHAIN-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_STATES = {
    "raw_bundle_seen",
    "attestation_mechanically_valid",
    "trust_policy_admissible",
    "intake_structurally_admissible",
    "adapter_conformant",
    "adapter_normalized",
    "production_ingestion_accepted",
    "security_provenance_passed",
    "noise_floor_passed",
    "threshold_replay_passed",
    "planner_update_eligible",
    "final_readiness_update_eligible",
    "handoff_traceable",
    "production_claim_credit_allowed",
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


def by_id(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["path_id"]: row for row in rows}


def main() -> None:
    schema = read_csv(DATA / "evidence_gatechain_state_schema.csv")
    rules = read_csv(DATA / "evidence_gatechain_transition_rules.csv")
    valid_paths = read_csv(DATA / "evidence_gatechain_valid_fixture_paths.csv")
    invalid_paths = read_csv(DATA / "evidence_gatechain_invalid_fixture_paths.csv")
    results = read_csv(DATA / "evidence_gatechain_replay_results.csv")
    reasons = read_csv(DATA / "evidence_gatechain_quarantine_reasons.csv")
    boundary = read_csv(DATA / "evidence_gatechain_claim_credit_boundary.csv")
    trace = read_csv(DATA / "evidence_gatechain_traceability_matrix.csv")
    readiness = read_csv(DATA / "final_claim_readiness_matrix.csv")
    handoff = read_csv(DATA / "handoff_claim_traceability.csv")

    assert REQUIRED_STATES <= {row["state_id"] for row in schema}
    assert REQUIRED_STATES <= {row["to_state"] for row in rules}
    assert any(row["path_id"] == "valid-current-fixture-quarantined" for row in valid_paths)
    assert any(row["path_id"] == "invalid-skipped-attestation" for row in invalid_paths)

    result = by_id(results)
    current = result["valid-current-fixture-quarantined"]
    assert current["production_claim_credit_allowed"] == "false"
    assert current["quarantined"] == "true"
    assert current["blocked_reason"] == "non_production_evidence_label"

    synthetic = result["valid-synthetic-production-shaped-quarantined"]
    assert synthetic["production_claim_credit_allowed"] == "false"
    assert synthetic["blocked_at_state"] == "production_ingestion_accepted"

    for row in results:
        assert row["production_claim_credit_allowed"] == "false", row
        if row["case_type"] == "invalid_path":
            assert row["blocked_reason"], row
            assert row["expected_reason_matched"] == "true", row

    expected_mismatches = {
        "invalid-mismatched-bundle-id": ("mismatched_bundle_id", "intake_structurally_admissible"),
        "invalid-mismatched-measurement-run-id": ("mismatched_measurement_run_id", "adapter_normalized"),
        "invalid-mismatched-operator-id": ("mismatched_operator_id", "trust_policy_admissible"),
        "invalid-mismatched-collector-id": ("mismatched_collector_id", "attestation_mechanically_valid"),
        "invalid-mismatched-schema-version": ("mismatched_schema_version", "production_ingestion_accepted"),
    }
    for path_id, (reason, state) in expected_mismatches.items():
        assert result[path_id]["blocked_reason"] == reason
        assert result[path_id]["blocked_at_state"] == state

    assert result["invalid-skipped-attestation"]["blocked_reason"] == "skipped_attestation"
    assert result["invalid-failed-attestation"]["blocked_reason"] == "failed_attestation_mechanically_valid"
    assert result["invalid-failed-attestation"]["blocked_at_state"] == "attestation_mechanically_valid"
    assert result["invalid-skipped-trust-policy"]["blocked_reason"] == "skipped_trust_policy"
    assert result["invalid-skipped-intake"]["blocked_reason"] == "skipped_intake"
    assert result["invalid-skipped-adapter-conformance"]["blocked_reason"] == "skipped_adapter_conformance"
    assert result["invalid-out-of-order-threshold"]["blocked_reason"] == "out_of_order_state"
    assert result["invalid-fixture-evidence-production-ingestion"]["blocked_reason"] == "non_production_evidence_label"
    assert result["invalid-proxy-evidence-threshold-credit"]["blocked_reason"] == "proxy_evidence_threshold_credit_blocked"
    assert result["invalid-threshold-without-security"]["blocked_reason"] == "threshold_without_security_provenance"
    assert result["invalid-threshold-without-noise-floor"]["blocked_reason"] == "threshold_without_noise_floor"
    assert result["invalid-final-readiness-without-handoff"]["blocked_reason"] == "final_readiness_without_handoff_traceability"

    assert all(row["fail_closed"] == "true" for row in reasons)
    assert all(row["production_claim_credit_allowed"] == "false" for row in boundary)
    assert all(row["option_bc_contract_ready_only"] == "true" for row in boundary)
    assert {row["trace_link_id"] for row in trace} >= {
        "gatechain-to-attestation",
        "gatechain-to-intake",
        "gatechain-to-adapter-conformance",
        "gatechain-to-production-ingestion",
        "gatechain-to-final-readiness-handoff",
    }
    assert all(row["production_ready"] == "false" for row in readiness)
    assert all(row["production_endorsed"] == "false" for row in handoff)

    for fig in [
        DATA / "evidence_gatechain_state_coverage.png",
        DATA / "evidence_gatechain_quarantine_reasons.png",
        DATA / "evidence_gatechain_claim_boundary.png",
    ]:
        assert_png_nonblank(fig)

    print("OK: evidence gatechain verified.")


if __name__ == "__main__":
    main()
