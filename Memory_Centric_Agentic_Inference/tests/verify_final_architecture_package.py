# created: 2026-05-12T00:45:00Z
# cycle: 21
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-FINALPKG-1

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_final_architecture_package import readiness_for_claim

DATA = ROOT / "data"

INPUTS = [
    DATA / "synthesis_claims_register.csv",
    DATA / "synthesis_architecture_decision_matrix.csv",
    DATA / "research_agenda_ranked.csv",
    DATA / "energy_claim_update_matrix.csv",
    DATA / "security_architecture_decision_updates.csv",
    DATA / "memory_plan_constraint_sensitivity.csv",
    DATA / "dc12_claim_update_matrix.csv",
    DATA / "production_dc12_claim_update_matrix.csv",
    DATA / "production_dc12_ingestion_results.csv",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_columns(rows: list[dict[str, str]], cols: set[str], path: Path) -> None:
    assert rows, f"{path} is empty"
    missing = cols - set(rows[0])
    assert not missing, f"{path} missing {missing}"


def test_final_package() -> None:
    before = {path: digest(path) for path in INPUTS}
    for path in INPUTS:
        assert path.exists(), path

    claims = read_csv(DATA / "final_claim_readiness_matrix.csv")
    options = read_csv(DATA / "final_architecture_option_readiness.csv")
    backlog = read_csv(DATA / "final_production_experiment_backlog.csv")
    blocked = read_csv(DATA / "final_blocked_claims.csv")
    ingest = read_csv(DATA / "production_dc12_ingestion_results.csv")

    require_columns(claims, {"claim_id", "readiness_label", "production_ready", "evidence_classes", "gate_status"}, DATA / "final_claim_readiness_matrix.csv")
    require_columns(options, {"workload_class", "option", "readiness_label", "production_ready", "known_blockers"}, DATA / "final_architecture_option_readiness.csv")
    require_columns(backlog, {"rank", "experiment", "expected_evidence_type", "priority_score", "production_boundary"}, DATA / "final_production_experiment_backlog.csv")
    require_columns(blocked, {"claim_id", "blocker_type", "source_artifact", "readiness_label"}, DATA / "final_blocked_claims.csv")

    forbidden_labels = {"synthetic_production_fixture", "host_local_proxy"}
    for row in ingest:
        if row["evidence_label"] in forbidden_labels:
            assert row["production_calibrated"] == "false"
            assert float(row["reuse_credit_granted"]) == 0.0 or row["fixture_class"] == "valid"
            assert row["production_calibrated"] == "false"
    for row in claims:
        if any(label in row["evidence_classes"] for label in forbidden_labels):
            assert row["production_ready"] == "false", row

    security_blocked = [r for r in ingest if r.get("security_credit_allowed") == "false"]
    assert security_blocked, "expected a security blocked row"
    for row in security_blocked:
        assert float(row["reuse_credit_granted"]) == 0.0
        assert float(row["energy_credit_granted_j"]) == 0.0

    assert any(r["option"] == "A" and ("control" in r["workload_class"] or r["readiness_label"] == "validated_mechanism") for r in options)
    assert all(r["required_telemetry"].strip("; ") for r in backlog)
    assert any("accelerator_power_counters" in r["required_telemetry"] for r in backlog)
    downgraded = [r for r in options if r["option"] in {"B", "C"} and any(b in r["known_blockers"] for b in ["queueing", "contention", "validation", "compression", "security"])]
    assert downgraded, "expected B/C downgrade blockers"
    assert all(r["production_ready"] == "false" for r in downgraded)

    for path in [
        DATA / "final_claim_readiness_heatmap.png",
        DATA / "final_architecture_option_readiness.png",
        DATA / "final_production_experiment_priority.png",
    ]:
        assert path.exists(), path
        assert path.stat().st_size > 10_000, f"{path} looks blank or trivial"

    after = {path: digest(path) for path in INPUTS}
    assert before == after, "upstream input artifacts changed during verification"

    passing_dc001 = {
        "constant_id": "DC-001",
        "evidence_label": "production_target",
        "schema_valid": "true",
        "join_valid": "true",
        "noise_floor_passed": "true",
        "security_credit_allowed": "true",
        "threshold_crossed": "true",
        "calibration_candidate": "true",
        "production_calibrated": "true",
    }
    assert readiness_for_claim("CL-012", "simulated", [passing_dc001], [])[2] is True
    assert readiness_for_claim("CL-002", "simulated", [passing_dc001], [])[2] is False


if __name__ == "__main__":
    test_final_package()
    print("OK: final architecture package verified.")
