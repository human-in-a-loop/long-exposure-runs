#!/usr/bin/env python3
# created: 2026-05-12T03:07:00Z
# cycle: 23
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODDEPLOY-1

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def require_columns(rows: list[dict[str, str]], cols: set[str], path: Path) -> None:
    assert rows, f"{path} is empty"
    missing = cols - set(rows[0])
    assert not missing, f"{path} missing columns {sorted(missing)}"


def field_set(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def test_deployment_kit() -> None:
    schema = read_csv(DATA / "production_dc12_telemetry_schema.csv")
    collectors = read_csv(DATA / "production_telemetry_collector_spec.csv")
    join_contract = read_csv(DATA / "production_telemetry_join_contract.csv")
    preflight = read_csv(DATA / "production_telemetry_preflight_checks.csv")
    pilot = read_csv(DATA / "production_telemetry_pilot_design.csv")
    claims = read_csv(DATA / "final_claim_readiness_matrix.csv")

    require_columns(
        collectors,
        {
            "collector_category",
            "collection_surface",
            "schema_fields",
            "derived_fields",
            "required_join_keys",
            "clock_alignment_requirement",
            "noise_floor_treatment",
            "evidence_boundary",
            "calibration_blocker",
            "claim_impact",
            "deployment_status",
        },
        DATA / "production_telemetry_collector_spec.csv",
    )
    require_columns(join_contract, {"join_domain", "required_key", "source_fields", "failure_consequence", "calibration_blocker"}, DATA / "production_telemetry_join_contract.csv")
    require_columns(preflight, {"check_id", "collector_category", "blocks_calibration", "fail_closed_consequence", "claim_impact"}, DATA / "production_telemetry_preflight_checks.csv")
    require_columns(pilot, {"pilot_step", "scope", "architecture_options", "minimum_collectors", "claim_boundary"}, DATA / "production_telemetry_pilot_design.csv")

    required_fields = {r["field_name"] for r in schema if r["required"] == "true"}
    covered_fields: set[str] = set()
    for row in collectors:
        covered_fields |= field_set(row["schema_fields"])
        assert row["clock_alignment_requirement"].strip(), row
        assert "noise" in row["noise_floor_treatment"].lower() or "numeric" in row["noise_floor_treatment"].lower(), row
        assert row["evidence_boundary"] == "deployment_blueprint_only_not_measured_evidence", row
        assert row["deployment_status"] == "deployment_specific_required", row
    assert not (required_fields - covered_fields), sorted(required_fields - covered_fields)

    required_join_keys = {"run_id", "interval_id", "workload_id", "object_id", "topology_id", "tenant_id", "security_context_id"}
    seen_join_keys = {row["required_key"] for row in join_contract}
    assert required_join_keys <= seen_join_keys, sorted(required_join_keys - seen_join_keys)
    for row in join_contract:
        assert row["calibration_blocker"] == "true", row
        assert "false" in row["failure_consequence"].lower() or "zero" in row["failure_consequence"].lower() or "unusable" in row["failure_consequence"].lower(), row

    required_categories = {
        "accelerator energy/power counters",
        "host energy/power counters",
        "source/destination tier byte counters",
        "CXL or pooled-memory latency p50/p95/p99",
        "queue depth and tenant concurrency",
        "workload/object classification",
        "reuse decision and architecture option",
        "security/provenance/retention/verifier gates",
        "interval alignment and noise-floor metadata",
    }
    assert required_categories <= {r["collector_category"] for r in collectors}
    assert required_categories <= {r["collector_category"] for r in preflight}
    for row in preflight:
        assert row["blocks_calibration"] == "true", row
        assert any(term in row["fail_closed_consequence"].lower() for term in ["blocked", "false", "zero", "rejected", "unusable"]), row

    assert any("Option A" in row["scope"] for row in pilot), "missing Option A control pilot"
    assert any("Option B" in row["scope"] for row in pilot), "missing Option B pilot"
    assert any("Option C" in row["scope"] for row in pilot), "missing Option C pilot"
    for row in pilot:
        assert "no production recommendation" in row["claim_boundary"] or "blueprint only" in row["claim_boundary"] or "does not endorse" in row["claim_boundary"] or "tests negative control only" in row["claim_boundary"], row

    assert all(row["production_ready"] == "false" for row in claims), "deployment kit must not promote production readiness"
    for path in [
        DATA / "production_telemetry_join_graph.png",
        DATA / "production_telemetry_preflight_matrix.png",
        DATA / "production_telemetry_pilot_scope.png",
    ]:
        assert path.exists(), path
        assert path.stat().st_size > 10_000, f"{path} looks blank or trivial"


if __name__ == "__main__":
    test_deployment_kit()
    print("OK: production telemetry deployment kit verified.")
