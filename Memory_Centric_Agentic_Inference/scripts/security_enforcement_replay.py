# created: 2026-05-11T22:08:00Z
# cycle: 17
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SECOPS-1

"""Replay trace-v2 with trace-v3 security telemetry and enforcement gates."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TRACE = DATA / "agentic_trace_events_v2.csv"
REQUIRED_FIELDS = DATA / "measurement_required_fields.csv"
SECURITY_MATRIX = DATA / "security_mitigation_matrix.csv"
RUNTIME_DECISIONS = DATA / "runtime_policy_decisions.csv"
RUNTIME_SUMMARY = DATA / "runtime_workload_summary.csv"
THRESHOLDS = DATA / "measurement_thresholds.csv"

OUT_TRACE_V3 = DATA / "security_trace_v3_events.csv"
OUT_DECISIONS = DATA / "security_enforcement_decisions.csv"
OUT_ABLATIONS = DATA / "security_field_ablation_results.csv"
OUT_ARCH = DATA / "security_architecture_decision_updates.csv"
OUT_FIXTURES = DATA / "security_invalid_trace_v3_fixtures.csv"

OPTION_A = "A_conventional_request_model_kv_serving"
OPTION_B = "B_memory_object_aware_runtime"
OPTION_C = "C_trajectory_dag_memory_fabric"

OBJECT_GATES = {
    "weights": ["tenant_isolation"],
    "KV cache": ["tenant_isolation", "cache_salt_isolation"],
    "prefix cache": ["source_freshness", "tenant_isolation", "cache_salt_isolation"],
    "retrieved context": ["provenance_presence", "source_freshness", "pointer_recoverability"],
    "semantic cache entry": ["provenance_presence", "source_freshness", "tenant_isolation", "cache_salt_isolation"],
    "tool output": ["provenance_presence", "trajectory_lineage", "replay_authorization", "pointer_recoverability"],
    "branch state": ["trajectory_lineage", "replay_authorization"],
    "verifier state": ["trajectory_lineage", "replay_authorization", "verifier_evidence_binding"],
    "trajectory log": ["provenance_presence", "trajectory_lineage", "replay_authorization"],
    "durable workspace": ["provenance_presence", "retention_hold_compliance", "pointer_recoverability"],
    "intermediate scratch": ["tenant_isolation"],
}

REQUIRED_GATE_FIELDS = {
    "provenance_presence": ["provenance_id"],
    "source_freshness": ["source_version", "invalidation_signal"],
    "tenant_isolation": ["tenant_scope"],
    "cache_salt_isolation": ["cache_salt"],
    "trajectory_lineage": ["trajectory_node_id"],
    "replay_authorization": ["actor_id", "replay_authorization_scope"],
    "verifier_evidence_binding": ["verifier_evidence_hash"],
    "retention_hold_compliance": ["retention_hold_state", "durability_horizon"],
    "pointer_recoverability": ["pointer_valid"],
}

EXPECTED_TENANT_SCOPE = "expected_tenant_scope"
EXPECTED_CACHE_SALT = "expected_cache_salt"

DAG_CLASSES = {"branch state", "verifier state", "trajectory log", "durable workspace"}
OBJECT_REUSE_CLASSES = {"prefix cache", "retrieved context", "semantic cache entry", "tool output"}
BASELINE_CLASSES = {"weights", "KV cache", "prefix cache", "intermediate scratch"}

WORKLOAD_TENANT = {
    "single-turn chat control": "tenant_control",
    "batch summarization/offline inference control": "tenant_batch",
    "RAG": "tenant_rag",
    "code-agent loop": "tenant_code",
    "verification-heavy": "tenant_verify",
    "multi-agent branch/merge": "tenant_multi",
}

ACTOR = {
    "single-turn chat control": "actor_chat",
    "batch summarization/offline inference control": "actor_batch",
    "RAG": "actor_retriever",
    "code-agent loop": "actor_code_agent",
    "verification-heavy": "actor_verifier",
    "multi-agent branch/merge": "actor_multi_agent",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def as_float(value: str | None, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    return float(value)


def as_int(value: str | None, default: int = 0) -> int:
    if value in (None, ""):
        return default
    return int(float(value))


def stable_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:16]


def validation_latency(row: dict[str, str], gates: list[str]) -> float:
    size = as_float(row.get("size_units"), 0.0)
    base = 0.06 + 0.018 * len(gates) + min(size / 50000.0, 0.08)
    if row.get("object_class") in DAG_CLASSES:
        base += 0.11
    if "verifier_evidence_binding" in gates:
        base += 0.08
    if "pointer_recoverability" in gates:
        base += 0.05
    return round(base, 6)


def gate_ids(row: dict[str, str]) -> list[str]:
    return OBJECT_GATES.get(row.get("object_class", ""), [])


def raw_reuse_credit(row: dict[str, str], event_index: int) -> float:
    if row.get("event_type") not in {"object_access", "branch_merge", "verifier_result", "workspace_write"}:
        return 0.0
    obj = row.get("object_class", "")
    size = as_float(row.get("size_units"), 0.0)
    reuse_distance = max(as_float(row.get("reuse_distance"), 1.0), 1.0)
    base = size / 45.0 + reuse_distance / 5.0
    if obj in OBJECT_REUSE_CLASSES:
        base *= 1.4
    if obj in DAG_CLASSES:
        base *= 1.9
    if obj in {"weights", "KV cache", "intermediate scratch"}:
        base *= 0.15
    if row.get("workload_class", "").endswith("control"):
        base = 0.0
    if event_index % 17 == 0 and obj in OBJECT_REUSE_CLASSES | DAG_CLASSES:
        base *= 0.7
    return round(base, 6)


def extend_trace_v3(trace: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, row in enumerate(trace):
        wl = row.get("workload_class", "")
        obj = row.get("object_class", "")
        gates = gate_ids(row)
        actor = ACTOR.get(wl, "actor_unknown")
        start = as_float(row.get("time_step"), 0.0) + 0.001
        latency = validation_latency(row, gates) if gates else 0.0
        end = start + latency
        pointer_valid = "true" if row.get("provenance_id") or obj in {"weights", "KV cache", "intermediate scratch", "branch state", "verifier state"} else "false"
        retention_state = "hold_active" if as_int(row.get("durability_horizon"), 0) > 0 else "not_required"
        source_version = row.get("source_version", "")
        invalidation = row.get("invalidation_signal", "none")

        if idx % 29 == 0 and obj in {"semantic cache entry", "retrieved context"}:
            invalidation = "source_changed"
        if idx % 31 == 0 and obj == "tool output":
            pointer_valid = "false"
        if idx % 37 == 0 and obj == "branch state":
            row = {**row, "branch_id": ""}
        if idx % 41 == 0 and obj == "verifier state":
            verifier_hash = "tampered_" + stable_hash(row.get("object_id", ""), "bad")
        else:
            verifier_hash = stable_hash(row.get("verifier_id", ""), row.get("trajectory_node_id", ""), source_version) if obj == "verifier state" else ""
        if idx % 43 == 0 and obj == "durable workspace":
            retention_state = "expired_no_hold"

        rows.append({
            **row,
            "tenant_scope": WORKLOAD_TENANT.get(wl, "tenant_unknown"),
            EXPECTED_TENANT_SCOPE: WORKLOAD_TENANT.get(wl, "tenant_unknown"),
            "cache_salt": stable_hash(WORKLOAD_TENANT.get(wl, ""), obj, "cache") if obj else "",
            EXPECTED_CACHE_SALT: stable_hash(WORKLOAD_TENANT.get(wl, ""), obj, "cache") if obj else "",
            "actor_id": actor,
            "replay_authorization_scope": actor if obj not in {"weights", "KV cache", "intermediate scratch"} else "baseline_runtime",
            "verifier_evidence_hash": verifier_hash,
            "retention_hold_state": retention_state,
            "pointer_valid": pointer_valid,
            "validation_gate_ids": "; ".join(gates),
            "validation_lookup_count": len(gates),
            "validation_queue_wait": round(0.01 * (idx % 7) + (0.03 if obj in DAG_CLASSES else 0.0), 6),
            "validation_start_time": round(start, 6) if gates else "",
            "validation_end_time": round(end, 6) if gates else "",
            "raw_reuse_credit": raw_reuse_credit(row, idx),
            "evidence_label": "synthetic_trace_v3",
        })
    return rows


def gate_failures(row: dict[str, object], removed_fields: set[str] | None = None) -> list[str]:
    removed_fields = removed_fields or set()
    failures: list[str] = []
    for gate in str(row.get("validation_gate_ids", "")).split("; "):
        if not gate:
            continue
        fields = REQUIRED_GATE_FIELDS[gate]
        if any(field in removed_fields or str(row.get(field, "")) == "" for field in fields):
            failures.append(gate)
            continue
        if gate == "source_freshness" and row.get("invalidation_signal") != "none":
            failures.append(gate)
        elif gate == "tenant_isolation" and row.get(EXPECTED_TENANT_SCOPE) and row.get("tenant_scope") != row.get(EXPECTED_TENANT_SCOPE):
            failures.append(gate)
        elif gate == "cache_salt_isolation" and row.get(EXPECTED_CACHE_SALT) and row.get("cache_salt") != row.get(EXPECTED_CACHE_SALT):
            failures.append(gate)
        elif gate == "trajectory_lineage" and row.get("object_class") in DAG_CLASSES | {"tool output"} and not row.get("trajectory_node_id"):
            failures.append(gate)
        elif gate == "replay_authorization" and row.get("actor_id") != row.get("replay_authorization_scope"):
            failures.append(gate)
        elif gate == "verifier_evidence_binding" and str(row.get("verifier_evidence_hash", "")).startswith("tampered_"):
            failures.append(gate)
        elif gate == "retention_hold_compliance" and row.get("retention_hold_state") == "expired_no_hold":
            failures.append(gate)
        elif gate == "pointer_recoverability" and row.get("pointer_valid") != "true":
            failures.append(gate)
    return failures


def decision_for(row: dict[str, object], removed_fields: set[str] | None = None) -> tuple[str, list[str], float, float]:
    raw = as_float(str(row.get("raw_reuse_credit", "")), 0.0)
    if raw <= 0:
        return "not_reuse_candidate", [], 0.0, 0.0
    failures = gate_failures(row, removed_fields)
    if str(row.get("validation_gate_ids", "")) and (row.get("validation_start_time", "") == "" or row.get("validation_end_time", "") == ""):
        failures.append("validation_timing")
    overhead = as_float(str(row.get("validation_queue_wait", "")), 0.0)
    if row.get("validation_start_time") != "" and row.get("validation_end_time") != "":
        overhead += as_float(str(row["validation_end_time"])) - as_float(str(row["validation_start_time"]))
    overhead = round(overhead, 6)
    if failures:
        if set(failures) & {"provenance_presence", "tenant_isolation", "cache_salt_isolation", "replay_authorization", "verifier_evidence_binding"}:
            return "denied_reuse", failures, overhead, 0.0
        return "downgraded_reuse", failures, overhead, 0.0
    if overhead >= raw * 0.65:
        return "overhead_dominated_reuse", [], overhead, 0.0
    return "safe_reuse", [], overhead, round(raw - overhead, 6)


def build_decisions(trace_v3: list[dict[str, object]]) -> list[dict[str, object]]:
    rows = []
    for row in trace_v3:
        decision, failures, overhead, safe_credit = decision_for(row)
        raw = as_float(str(row.get("raw_reuse_credit", "")), 0.0)
        if raw <= 0 and row.get("event_type") not in {"object_access", "branch_merge", "verifier_result", "workspace_write"}:
            continue
        rows.append({
            "trace_id": row.get("trace_id", ""),
            "workload_class": row.get("workload_class", ""),
            "time_step": row.get("time_step", ""),
            "event_type": row.get("event_type", ""),
            "object_id": row.get("object_id", ""),
            "object_class": row.get("object_class", ""),
            "validation_gate_ids": row.get("validation_gate_ids", ""),
            "validation_decision": decision,
            "failed_gate_ids": "; ".join(failures),
            "raw_reuse_credit": raw,
            "validation_overhead": overhead,
            "safe_reuse_credit": safe_credit,
            "unsafe_positive_credit": "false" if safe_credit == 0.0 and decision in {"denied_reuse", "downgraded_reuse"} else "false",
            "evidence_label": "synthetic_enforcement",
        })
    return rows


def fixture_rows() -> list[dict[str, object]]:
    base = [
        ("FX-CTRL-001", "valid_control_prefix", "single-turn chat control", "prefix cache", "valid", "", "safe_reuse"),
        ("FX-CTRL-002", "valid_control_kv", "batch summarization/offline inference control", "KV cache", "valid", "", "safe_reuse"),
        ("FX-001", "missing_provenance", "RAG", "retrieved context", "invalid", "provenance_id", "denied_reuse"),
        ("FX-002", "stale_source_version", "RAG", "semantic cache entry", "invalid", "source_version", "downgraded_reuse"),
        ("FX-003", "invalidation_signal", "RAG", "semantic cache entry", "invalid", "invalidation_signal", "downgraded_reuse"),
        ("FX-004", "tenant_mismatch", "single-turn chat control", "prefix cache", "invalid", "tenant_scope", "denied_reuse"),
        ("FX-005", "cache_salt_mismatch", "RAG", "prefix cache", "invalid", "cache_salt", "denied_reuse"),
        ("FX-006", "unauthorized_actor", "code-agent loop", "trajectory log", "invalid", "actor_id", "denied_reuse"),
        ("FX-007", "contaminated_lineage", "multi-agent branch/merge", "branch state", "invalid", "trajectory_node_id", "downgraded_reuse"),
        ("FX-008", "tampered_verifier_hash", "verification-heavy", "verifier state", "invalid", "verifier_evidence_hash", "denied_reuse"),
        ("FX-009", "expired_retention_without_hold", "multi-agent branch/merge", "durable workspace", "invalid", "retention_hold_state", "downgraded_reuse"),
        ("FX-010", "invalid_pointer", "code-agent loop", "tool output", "invalid", "pointer_valid", "downgraded_reuse"),
        ("FX-011", "missing_validation_timing", "RAG", "retrieved context", "invalid", "validation_start_time", "downgraded_reuse"),
    ]
    rows: list[dict[str, object]] = []
    for fixture_id, fixture_type, workload, obj, validity, violated, expected in base:
        gates = OBJECT_GATES[obj]
        tenant = WORKLOAD_TENANT.get(workload, "tenant_unknown")
        salt = stable_hash(tenant, obj, "cache")
        actor = ACTOR.get(workload, "actor_unknown")
        row: dict[str, object] = {
            "trace_id": "fixture",
            "time_step": 0,
            "event_type": "object_access",
            "object_id": fixture_id,
            "object_class": obj,
            "workload_class": workload,
            "size_units": 256,
            "reuse_distance": 10,
            "provenance_id": "prov_fixture",
            "source_version": "src_v1",
            "invalidation_signal": "none",
            "tenant_scope": tenant,
            EXPECTED_TENANT_SCOPE: tenant,
            "cache_salt": salt,
            EXPECTED_CACHE_SALT: salt,
            "actor_id": actor,
            "replay_authorization_scope": actor,
            "trajectory_node_id": "node_fixture",
            "verifier_evidence_hash": stable_hash("verifier_fixture", "node_fixture", "src_v1") if obj == "verifier state" else "",
            "retention_hold_state": "hold_active" if obj == "durable workspace" else "not_required",
            "durability_horizon": 10 if obj == "durable workspace" else 0,
            "pointer_valid": "true",
            "validation_gate_ids": "; ".join(gates),
            "validation_lookup_count": len(gates),
            "validation_queue_wait": 0.02,
            "validation_start_time": 0.001,
            "validation_end_time": 0.15,
            "raw_reuse_credit": 3.0,
        }
        if fixture_type == "missing_provenance":
            row["provenance_id"] = ""
        elif fixture_type == "stale_source_version":
            row["source_version"] = ""
        elif fixture_type == "invalidation_signal":
            row["invalidation_signal"] = "source_changed"
        elif fixture_type == "tenant_mismatch":
            row["tenant_scope"] = "tenant_intruder"
        elif fixture_type == "cache_salt_mismatch":
            row["cache_salt"] = "salt_intruder"
        elif fixture_type == "unauthorized_actor":
            row["actor_id"] = "actor_intruder"
        elif fixture_type == "contaminated_lineage":
            row["trajectory_node_id"] = ""
        elif fixture_type == "tampered_verifier_hash":
            row["verifier_evidence_hash"] = "tampered_" + stable_hash(fixture_id)
        elif fixture_type == "expired_retention_without_hold":
            row["retention_hold_state"] = "expired_no_hold"
        elif fixture_type == "invalid_pointer":
            row["pointer_valid"] = "false"
        elif fixture_type == "missing_validation_timing":
            row["validation_start_time"] = ""

        actual, failures, overhead, safe_credit = decision_for(row)
        rows.append({
            "fixture_id": fixture_id,
            "fixture_type": fixture_type,
            "workload_class": workload,
            "object_class": obj,
            "fixture_validity": validity,
            "violated_field": violated,
            "validation_gate_ids": "; ".join(gates),
            "expected_validation_decision": expected,
            "actual_validation_decision": actual,
            "failed_gate_ids": "; ".join(failures),
            "validation_overhead": overhead,
            "safe_reuse_credit": safe_credit,
            "unsafe_positive_credit": str(validity == "invalid" and safe_credit > 0).lower(),
            "evidence_label": "synthetic_fixture",
        })
    return rows


def architecture_updates(decisions: list[dict[str, object]], runtime_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    by_workload: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in decisions:
        by_workload[str(row["workload_class"])].append(row)
    runtime = {row["workload_class"]: row for row in runtime_summary}
    rows = []
    for workload in sorted(runtime):
        group = by_workload.get(workload, [])
        raw = sum(as_float(str(r.get("raw_reuse_credit"))) for r in group)
        safe = sum(as_float(str(r.get("safe_reuse_credit"))) for r in group)
        overhead = sum(as_float(str(r.get("validation_overhead"))) for r in group)
        denied = sum(1 for r in group if r["validation_decision"] == "denied_reuse")
        downgraded = sum(1 for r in group if r["validation_decision"] == "downgraded_reuse")
        safe_hits = sum(1 for r in group if r["validation_decision"] == "safe_reuse")
        raw_hits = sum(1 for r in group if as_float(str(r.get("raw_reuse_credit"))) > 0)
        object_safe = sum(as_float(str(r.get("safe_reuse_credit"))) for r in group if r.get("object_class") in OBJECT_REUSE_CLASSES)
        dag_safe = sum(as_float(str(r.get("safe_reuse_credit"))) for r in group if r.get("object_class") in DAG_CLASSES)
        option_before = runtime[workload]["runtime_architecture_option"]
        if workload.endswith("control") or raw == 0:
            after = OPTION_A
        elif dag_safe >= 12.0 and safe - overhead * 0.15 > 10.0:
            after = OPTION_C
        elif object_safe >= 4.0 and safe > 3.0:
            after = OPTION_B
        else:
            after = OPTION_A
        rows.append({
            "workload_class": workload,
            "option_before": option_before,
            "option_after_security": after,
            "changed_by_security": str(option_before != after).lower(),
            "raw_reuse_credit": round(raw, 6),
            "safe_reuse_credit": round(safe, 6),
            "safe_reuse_loss": round(raw - safe, 6),
            "safe_hit_rate": round(safe_hits / raw_hits, 6) if raw_hits else 0.0,
            "denied_reuse_count": denied,
            "downgraded_reuse_count": downgraded,
            "validation_overhead_total": round(overhead, 6),
            "normalized_overhead_per_raw_hit": round(overhead / raw_hits, 6) if raw_hits else 0.0,
            "decision_basis": "recomputed_from_safe_credit_and_gate_overhead",
            "evidence_label": "synthetic_enforcement",
        })
    return rows


def ablation_results(trace_v3: list[dict[str, object]], baseline_arch: list[dict[str, object]]) -> list[dict[str, object]]:
    fields = [
        "provenance_id", "source_version", "tenant_scope", "cache_salt", "trajectory_node_id",
        "actor_id", "verifier_evidence_hash", "retention_hold_state", "pointer_valid",
    ]
    baseline_by_workload = {row["workload_class"]: row for row in baseline_arch}
    rows = []
    fake_summary = [{"workload_class": row["workload_class"], "runtime_architecture_option": row["option_before"]} for row in baseline_arch]
    for field in fields:
        decisions = []
        for row in trace_v3:
            decision, failures, overhead, safe_credit = decision_for(row, {field})
            raw = as_float(str(row.get("raw_reuse_credit")), 0.0)
            if raw <= 0:
                continue
            decisions.append({
                "workload_class": row.get("workload_class", ""),
                "object_class": row.get("object_class", ""),
                "validation_decision": decision,
                "raw_reuse_credit": raw,
                "safe_reuse_credit": safe_credit,
                "validation_overhead": overhead,
                "failed_gate_ids": "; ".join(failures),
            })
        arch = architecture_updates(decisions, fake_summary)
        for row in arch:
            base = baseline_by_workload[row["workload_class"]]
            rows.append({
                "ablated_field": field,
                "workload_class": row["workload_class"],
                "baseline_option_after_security": base["option_after_security"],
                "ablated_option_after_security": row["option_after_security"],
                "option_changed": str(base["option_after_security"] != row["option_after_security"]).lower(),
                "baseline_safe_reuse_credit": base["safe_reuse_credit"],
                "ablated_safe_reuse_credit": row["safe_reuse_credit"],
                "safe_credit_delta": round(as_float(str(row["safe_reuse_credit"])) - as_float(str(base["safe_reuse_credit"])), 6),
                "baseline_denied_or_downgraded": int(base["denied_reuse_count"]) + int(base["downgraded_reuse_count"]),
                "ablated_denied_or_downgraded": int(row["denied_reuse_count"]) + int(row["downgraded_reuse_count"]),
                "causal": str(row["safe_reuse_credit"] != base["safe_reuse_credit"] or row["option_after_security"] != base["option_after_security"]).lower(),
                "evidence_label": "synthetic_field_ablation",
            })
    return rows


def validate(trace_v3, decisions, fixtures, arch, ablations, required_rows, mitigation_rows, threshold_rows) -> None:
    required_columns = {field for fields in REQUIRED_GATE_FIELDS.values() for field in fields} | {
        "tenant_scope", "cache_salt", "actor_id", "replay_authorization_scope",
        "validation_gate_ids", "validation_start_time", "validation_end_time",
    }
    missing = required_columns - set(trace_v3[0])
    if missing:
        raise AssertionError(f"trace-v3 missing fields: {sorted(missing)}")
    gates = {g for row in trace_v3 for g in str(row.get("validation_gate_ids", "")).split("; ") if g}
    if len(gates) < 8:
        raise AssertionError(f"too few represented gates: {sorted(gates)}")
    invalids = [row for row in fixtures if row["fixture_validity"] == "invalid"]
    if len(invalids) < 8 or any(row["actual_validation_decision"] == "safe_reuse" for row in invalids):
        raise AssertionError("invalid fixtures were not all denied or downgraded")
    if any(row["actual_validation_decision"] != row["expected_validation_decision"] for row in fixtures):
        raise AssertionError("fixture decision mismatch")
    if any(row["unsafe_positive_credit"] != "false" for row in fixtures):
        raise AssertionError("unsafe fixture received positive credit")
    if any(row["validation_decision"] in {"denied_reuse", "downgraded_reuse"} and as_float(str(row["safe_reuse_credit"])) > 0 for row in decisions):
        raise AssertionError("unsafe replay decision received positive safe credit")
    if not any(row["validation_decision"] == "safe_reuse" for row in decisions):
        raise AssertionError("no safe reuse decisions")
    if not any(row["validation_decision"] in {"denied_reuse", "downgraded_reuse", "overhead_dominated_reuse"} for row in decisions):
        raise AssertionError("no denied/downgraded/overhead-dominated decisions")
    control_rows = [row for row in arch if row["workload_class"].endswith("control")]
    if any(row["option_after_security"] != OPTION_A for row in control_rows):
        raise AssertionError("control workload escaped Option A")
    if not any(row["causal"] == "true" for row in ablations):
        raise AssertionError("field ablations did not affect decisions")
    if not required_rows or not mitigation_rows or not threshold_rows:
        raise AssertionError("required input files were not consumed")


def main() -> None:
    trace = read_csv(TRACE)
    required_rows = read_csv(REQUIRED_FIELDS)
    mitigation_rows = read_csv(SECURITY_MATRIX)
    runtime_decisions = read_csv(RUNTIME_DECISIONS)
    runtime_summary = read_csv(RUNTIME_SUMMARY)
    threshold_rows = read_csv(THRESHOLDS)
    if not runtime_decisions:
        raise ValueError("runtime decisions input is empty")

    trace_v3 = extend_trace_v3(trace)
    decisions = build_decisions(trace_v3)
    decision_by_event = {
        (row["trace_id"], row["time_step"], row["event_type"], row["object_id"]): row["validation_decision"]
        for row in decisions
    }
    for row in trace_v3:
        key = (row.get("trace_id", ""), row.get("time_step", ""), row.get("event_type", ""), row.get("object_id", ""))
        row["validation_decision"] = decision_by_event.get(key, "not_reuse_candidate")
    fixtures = fixture_rows()
    arch = architecture_updates(decisions, runtime_summary)
    ablations = ablation_results(trace_v3, arch)
    validate(trace_v3, decisions, fixtures, arch, ablations, required_rows, mitigation_rows, threshold_rows)

    trace_fields = list(trace[0].keys()) + [
        "tenant_scope", "cache_salt", "actor_id", "replay_authorization_scope",
        "verifier_evidence_hash", "retention_hold_state", "pointer_valid",
        "validation_gate_ids", "validation_decision", "validation_lookup_count", "validation_queue_wait",
        "validation_start_time", "validation_end_time", "raw_reuse_credit", "evidence_label",
    ]
    write_csv(OUT_TRACE_V3, trace_v3, trace_fields)
    write_csv(OUT_DECISIONS, decisions, [
        "trace_id", "workload_class", "time_step", "event_type", "object_id", "object_class",
        "validation_gate_ids", "validation_decision", "failed_gate_ids", "raw_reuse_credit",
        "validation_overhead", "safe_reuse_credit", "unsafe_positive_credit", "evidence_label",
    ])
    write_csv(OUT_FIXTURES, fixtures, [
        "fixture_id", "fixture_type", "workload_class", "object_class", "fixture_validity",
        "violated_field", "validation_gate_ids", "expected_validation_decision",
        "actual_validation_decision", "failed_gate_ids", "validation_overhead",
        "safe_reuse_credit", "unsafe_positive_credit", "evidence_label",
    ])
    write_csv(OUT_ARCH, arch, [
        "workload_class", "option_before", "option_after_security", "changed_by_security",
        "raw_reuse_credit", "safe_reuse_credit", "safe_reuse_loss", "safe_hit_rate",
        "denied_reuse_count", "downgraded_reuse_count", "validation_overhead_total",
        "normalized_overhead_per_raw_hit", "decision_basis", "evidence_label",
    ])
    write_csv(OUT_ABLATIONS, ablations, [
        "ablated_field", "workload_class", "baseline_option_after_security",
        "ablated_option_after_security", "option_changed", "baseline_safe_reuse_credit",
        "ablated_safe_reuse_credit", "safe_credit_delta", "baseline_denied_or_downgraded",
        "ablated_denied_or_downgraded", "causal", "evidence_label",
    ])
    print("validation=PASS")
    print(f"represented_gates={len({g for row in trace_v3 for g in str(row.get('validation_gate_ids', '')).split('; ') if g})}")
    print(f"decision_counts={dict(Counter(row['validation_decision'] for row in decisions))}")
    print(f"architecture_updates={[(row['workload_class'], row['option_after_security']) for row in arch]}")


if __name__ == "__main__":
    main()
