# created: 2026-05-11T22:14:00Z
# cycle: 17
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SECOPS-1

"""Verify M-SECOPS-1 security enforcement replay artifacts."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.image as mpimg


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows, f"{name} is empty"
    return rows


def as_float(value: str) -> float:
    return float(value or 0.0)


def assert_nonblank_png(name: str) -> None:
    path = DATA / name
    assert path.exists(), f"missing figure {name}"
    img = mpimg.imread(path)
    assert img.size > 0, f"{name} has no pixels"
    assert float(img.max() - img.min()) > 0.001, f"{name} appears blank"


def main() -> None:
    trace = read_csv("security_trace_v3_events.csv")
    decisions = read_csv("security_enforcement_decisions.csv")
    fixtures = read_csv("security_invalid_trace_v3_fixtures.csv")
    ablations = read_csv("security_field_ablation_results.csv")
    arch = read_csv("security_architecture_decision_updates.csv")

    required_trace_fields = {
        "tenant_scope",
        "cache_salt",
        "actor_id",
        "replay_authorization_scope",
        "verifier_evidence_hash",
        "retention_hold_state",
        "validation_gate_ids",
        "validation_decision",
        "validation_lookup_count",
        "validation_queue_wait",
        "validation_start_time",
        "validation_end_time",
        "pointer_valid",
    }
    missing = required_trace_fields - set(trace[0])
    assert not missing, f"missing trace-v3 fields: {sorted(missing)}"

    gates = {gate for row in trace for gate in row["validation_gate_ids"].split("; ") if gate}
    expected_gates = {
        "provenance_presence",
        "source_freshness",
        "tenant_isolation",
        "cache_salt_isolation",
        "trajectory_lineage",
        "replay_authorization",
        "verifier_evidence_binding",
        "retention_hold_compliance",
        "pointer_recoverability",
    }
    assert expected_gates <= gates, f"missing represented gates: {sorted(expected_gates - gates)}"

    invalids = [row for row in fixtures if row["fixture_validity"] == "invalid"]
    assert len(invalids) >= 8, "too few invalid fixtures"
    assert all(row["actual_validation_decision"] in {"denied_reuse", "downgraded_reuse"} for row in invalids)
    assert all(row["unsafe_positive_credit"] == "false" for row in invalids)

    unsafe = [
        row for row in decisions
        if row["validation_decision"] in {"denied_reuse", "downgraded_reuse"} and as_float(row["safe_reuse_credit"]) > 0
    ]
    assert not unsafe, f"unsafe decisions received safe credit: {unsafe[:3]}"
    assert any(as_float(row["raw_reuse_credit"]) > as_float(row["safe_reuse_credit"]) for row in decisions)
    assert {"safe_reuse", "denied_reuse", "downgraded_reuse", "overhead_dominated_reuse"} <= {
        row["validation_decision"] for row in decisions
    }

    controls = [row for row in arch if row["workload_class"].endswith("control")]
    assert controls, "missing control workloads"
    assert all(row["option_after_security"] == "A_conventional_request_model_kv_serving" for row in controls)
    assert not any(row["option_after_security"] == "C_trajectory_dag_memory_fabric" for row in controls)
    assert any(row["changed_by_security"] == "true" for row in arch), "expected at least one security-driven option change"
    assert any(row["causal"] == "true" and as_float(row["safe_credit_delta"]) < 0 for row in ablations)

    for figure in [
        "security_safe_reuse_waterfall.png",
        "security_gate_latency_distribution.png",
        "security_option_update_matrix.png",
    ]:
        assert_nonblank_png(figure)

    print("validation=PASS")
    print(f"trace_rows={len(trace)}")
    print(f"decision_rows={len(decisions)}")
    print(f"invalid_fixtures={len(invalids)}")
    print(f"represented_gates={len(gates)}")
    print(f"security_option_changes={sum(row['changed_by_security'] == 'true' for row in arch)}")


if __name__ == "__main__":
    main()
