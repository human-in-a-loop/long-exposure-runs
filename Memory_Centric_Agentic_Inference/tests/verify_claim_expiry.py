#!/usr/bin/env python3
# created: 2026-05-12T18:15:00Z
# cycle: 39
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CLAIMEXP-1
"""Verify production claim expiry and revalidation boundaries."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def run(script: str) -> None:
    subprocess.run([sys.executable, str(ROOT / script)], check=True)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{path.relative_to(ROOT)} is empty"
    return rows


def assert_nonblank_png(path: Path) -> None:
    assert path.exists(), f"missing {path.relative_to(ROOT)}"
    assert path.stat().st_size > 1000, f"blank or tiny figure: {path.relative_to(ROOT)}"


def main() -> None:
    run("scripts/build_claim_expiry_fixtures.py")
    run("scripts/evaluate_claim_expiry.py")
    run("scripts/plot_claim_expiry.py")

    results = {row["case_id"]: row for row in read_csv(DATA / "claim_expiry_results.csv")}
    statuses = {row["observed_status"] for row in results.values()}
    assert {"currently_supportable", "revalidation_required", "expired", "invalidated_by_change", "not_production_supported"} <= statuses
    assert all(row["matched_expected"] == "true" for row in results.values())

    assert results["fresh_prior_production_replay"]["observed_status"] == "currently_supportable"
    assert results["t0_without_upstream_production"]["observed_status"] == "not_production_supported"
    assert results["dry_run_fixture_attempt"]["observed_status"] == "not_production_supported"
    assert results["synthetic_proxy_attempt"]["observed_status"] == "not_production_supported"
    assert results["age_exceeds_policy_ttl"]["observed_status"] == "expired"
    assert results["age_equals_policy_ttl"]["observed_status"] == "expired"
    assert results["model_version_changed"]["observed_status"] == "invalidated_by_change"
    assert results["topology_changed"]["observed_status"] == "invalidated_by_change"
    assert results["workload_mix_outside_overlap"]["observed_status"] == "revalidation_required"
    assert results["security_deny_rate_drifted"]["observed_status"] == "revalidation_required"
    assert results["collector_rotated_without_reenrollment"]["observed_status"] == "invalidated_by_change"
    assert results["trust_policy_rotated"]["observed_status"] == "invalidated_by_change"
    assert results["copied_old_replay_after_drift"]["observed_status"] == "revalidation_required"

    revalidation = {row["case_id"]: row for row in read_csv(DATA / "claim_expiry_revalidation_boundary.csv")}
    assert revalidation["fresh_prior_production_replay"]["fresh_production_replay_required"] == "false"
    for case_id, row in revalidation.items():
        assert row["old_replay_copy_accepted"] == "false", case_id
        assert row["revalidation_may_use_prior_result_without_new_evidence"] == "false", case_id
    assert revalidation["copied_old_replay_after_drift"]["fresh_production_replay_required"] == "true"

    claims = {row["case_id"]: row for row in read_csv(DATA / "claim_expiry_claim_boundary.csv")}
    for case_id, row in claims.items():
        if case_id == "fresh_prior_production_replay":
            assert row["currently_supportable_lifecycle_state"] == "true", row
            assert row["claim_credit_allowed"] == "false", row
            assert row["production_ready"] == "false", row
        else:
            assert row["currently_supportable_lifecycle_state"] == "false", row
            assert row["claim_credit_allowed"] == "false", row
            assert row["production_ready"] == "false", row
        assert row["production_calibrated"] == "false", row
        assert row["threshold_success"] == "false", row
        assert row["causal_validity_granted"] == "false", row

    failures = {row["failure_mode"] for row in read_csv(DATA / "claim_expiry_failure_modes.csv")}
    assert {
        "evidence_age_exceeds_or_equals_ttl",
        "model_version_changed",
        "topology_changed",
        "collector_identity_rotated_without_reenrollment",
        "trust_policy_rotated",
        "upstream_or_label_not_production_supported",
    } <= failures

    assert_nonblank_png(DATA / "claim_expiry_timeline.png")
    assert_nonblank_png(DATA / "claim_expiry_failure_modes.png")
    assert_nonblank_png(DATA / "claim_expiry_revalidation_boundary.png")
    print("OK: claim expiry and revalidation verified.")


if __name__ == "__main__":
    main()
