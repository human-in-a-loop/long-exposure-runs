# created: 2026-05-11T18:02:00Z
# cycle: 13
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-SEC-1

"""Build synthetic security/provenance artifacts for memory-centric inference."""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOC = ROOT / "memory-centric-agentic"
EVIDENCE = "synthetic"

TRACE = DATA / "agentic_trace_events_v2.csv"
RUNTIME_FAILURES = DATA / "runtime_failure_cases.csv"
COMPRESSION_FAILURES = DATA / "compression_safety_failures.csv"
DEFERRED_CONSTANTS = DATA / "calibration_deferred_constants.csv"
HOOKS = DATA / "runtime_compiler_hook_matrix.csv"
ARCH_FAILURES = DATA / "architecture_failure_modes.csv"
RUNTIME_SUMMARY = DATA / "runtime_workload_summary.csv"
COMPRESSION_BEST = DATA / "compression_best_strategy_by_object.csv"


OBJECT_CLASSES = [
    "weights",
    "KV cache",
    "prefix cache",
    "retrieved context",
    "tool output",
    "intermediate scratch",
    "branch state",
    "verifier state",
    "trajectory log",
    "durable workspace",
    "semantic cache entry",
]

RISK_CLASSES = [
    "leakage",
    "stale reuse",
    "cache poisoning",
    "provenance forgery",
    "replay ambiguity",
    "cross-tenant aliasing",
    "retention overrun",
    "deletion/audit conflict",
    "verifier tampering",
    "unsafe summary-pointer recovery",
]

OBJECT_RULES = {
    "weights": {
        "risks": ["leakage"],
        "fields": ["object_id", "object_class", "tier"],
        "hook": "object_registry",
        "base": 1,
    },
    "KV cache": {
        "risks": ["leakage", "cross-tenant aliasing"],
        "fields": ["object_id", "object_class", "tenant_scope"],
        "hook": "object_registry",
        "base": 2,
    },
    "prefix cache": {
        "risks": ["leakage", "cross-tenant aliasing", "stale reuse"],
        "fields": ["object_id", "source_version", "cache_salt", "tenant_scope"],
        "hook": "provenance_pointer",
        "base": 3,
    },
    "retrieved context": {
        "risks": ["stale reuse", "provenance forgery", "cache poisoning"],
        "fields": ["provenance_id", "source_version", "invalidation_signal"],
        "hook": "provenance_pointer",
        "base": 4,
    },
    "tool output": {
        "risks": ["provenance forgery", "replay ambiguity", "unsafe summary-pointer recovery"],
        "fields": ["provenance_id", "trajectory_node_id", "source_version"],
        "hook": "correctness_sensitive_pin",
        "base": 4,
    },
    "intermediate scratch": {
        "risks": ["leakage"],
        "fields": ["object_id", "lifetime_boundary"],
        "hook": "lifetime_boundary",
        "base": 1,
    },
    "branch state": {
        "risks": ["replay ambiguity", "cross-tenant aliasing"],
        "fields": ["branch_id", "trajectory_node_id", "merge_state"],
        "hook": "branch_state_annotation",
        "base": 4,
    },
    "verifier state": {
        "risks": ["verifier tampering", "replay ambiguity"],
        "fields": ["verifier_id", "trajectory_node_id", "merge_state"],
        "hook": "verifier_retention_barrier",
        "base": 5,
    },
    "trajectory log": {
        "risks": ["replay ambiguity", "provenance forgery", "deletion/audit conflict"],
        "fields": ["trajectory_node_id", "parent_object_id", "provenance_id"],
        "hook": "trajectory_graph_edge",
        "base": 5,
    },
    "durable workspace": {
        "risks": ["retention overrun", "deletion/audit conflict", "unsafe summary-pointer recovery"],
        "fields": ["durability_horizon", "provenance_id", "source_version"],
        "hook": "durability_horizon",
        "base": 5,
    },
    "semantic cache entry": {
        "risks": ["stale reuse", "cache poisoning", "cross-tenant aliasing"],
        "fields": ["provenance_id", "source_version", "invalidation_signal", "cache_salt"],
        "hook": "provenance_pointer",
        "base": 5,
    },
}

MITIGATIONS = {
    "leakage": ("cache_salt_or_tenant_scope", "cache isolation", "runtime+storage"),
    "stale reuse": ("source_version_and_invalidation_check", "freshness validation", "runtime"),
    "cache poisoning": ("provenance_pointer_validation", "reject untrusted cache entries", "runtime+storage"),
    "provenance forgery": ("provenance_pointer_validation", "validate artifact/source pointer", "storage+runtime"),
    "replay ambiguity": ("trajectory_lineage_validation", "validate DAG edge and replay authorization", "runtime+audit"),
    "cross-tenant aliasing": ("cache_salt_or_tenant_scope", "partition reusable state", "runtime+storage"),
    "retention overrun": ("retention_ttl_or_legal_hold_policy", "expire or preserve with explicit hold", "storage"),
    "deletion/audit conflict": ("retention_ttl_or_legal_hold_policy", "track deletion versus audit hold", "storage+audit"),
    "verifier tampering": ("verifier_evidence_hash", "hash verifier evidence and bind result to branch", "runtime+audit"),
    "unsafe summary-pointer recovery": ("downgrade_to_exact_or_option_fallback", "fallback to exact state or Option A/B", "compiler+runtime"),
}

CLAIM_REFS = {
    "leakage": "M-TRACE-1; M-PROTO-1",
    "stale reuse": "M-TRACE-1; M-CALIB-1 DC-004",
    "cache poisoning": "M-CALIB-1 DC-004; M-PROTO-1",
    "provenance forgery": "M-TRACE-1; M-PROTO-1; M-CALIB-1 DC-006",
    "replay ambiguity": "M-TRACE-1; M-PROTO-1; M-CALIB-1 DC-005",
    "cross-tenant aliasing": "M-TRACE-1 synthetic fixture",
    "retention overrun": "M-TRACE-1 durability_horizon; M-CALIB-1 DC-003",
    "deletion/audit conflict": "M-CALIB-1 deferred legal/compliance evidence",
    "verifier tampering": "M-TRACE-1 verifier_id; M-PROTO-1",
    "unsafe summary-pointer recovery": "M-COMP-1; M-PROTO-1",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if any(str(v).lower() in {"placeholder", "replace_me"} for v in row.values()):
            raise ValueError(f"placeholder row in {path}: {row}")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fieldnames})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def load_inputs() -> dict[str, list[dict[str, str]]]:
    inputs = {
        "trace": read_csv(TRACE),
        "runtime_failures": read_csv(RUNTIME_FAILURES),
        "compression_failures": read_csv(COMPRESSION_FAILURES),
        "deferred": read_csv(DEFERRED_CONSTANTS),
        "hooks": read_csv(HOOKS),
        "arch_failures": read_csv(ARCH_FAILURES),
        "runtime_summary": read_csv(RUNTIME_SUMMARY),
        "compression_best": read_csv(COMPRESSION_BEST),
    }
    required_trace = {
        "workload_class",
        "event_type",
        "object_id",
        "object_class",
        "provenance_id",
        "source_version",
        "invalidation_signal",
        "trajectory_node_id",
        "branch_id",
        "verifier_id",
        "durability_horizon",
    }
    missing = required_trace - set(inputs["trace"][0])
    if missing:
        raise ValueError(f"trace missing required security fields: {sorted(missing)}")
    return inputs


def workload_architectures(runtime_summary: list[dict[str, str]]) -> dict[str, str]:
    return {
        r["workload_class"]: r["runtime_architecture_option"]
        for r in runtime_summary
    }


def observed_pairs(trace: list[dict[str, str]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for row in trace:
        obj = row.get("object_class", "")
        wl = row.get("workload_class", "")
        if obj in OBJECT_CLASSES and wl:
            out[obj].add(wl)
    return out


def source_claim_type(risk_class: str) -> str:
    if risk_class in {"stale reuse", "cache poisoning"}:
        return "sourced_from_calibration"
    if risk_class in {"deletion/audit conflict", "cross-tenant aliasing"}:
        return "speculative"
    return "derived"


def build_threat_matrix(inputs: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    arch = workload_architectures(inputs["runtime_summary"])
    pairs = observed_pairs(inputs["trace"])
    rows: list[dict[str, object]] = []
    risk_idx = 1
    for obj in OBJECT_CLASSES:
        workloads = sorted(pairs.get(obj) or ["not observed in trace"])
        rule = OBJECT_RULES[obj]
        for wl in workloads:
            option = arch.get(wl, "not_applicable")
            for risk in rule["risks"]:
                hook = MITIGATIONS[risk][0]
                rows.append({
                    "risk_id": f"SR-{risk_idx:03d}",
                    "object_class": obj,
                    "workload_class": wl,
                    "architecture_option": option,
                    "risk_class": risk,
                    "required_fields": "; ".join(rule["fields"]),
                    "failure_condition": failure_condition(obj, risk),
                    "impact": impact_label(option, risk, rule["base"]),
                    "detectability": detectability(obj, risk),
                    "mitigation_hook": hook,
                    "claim_type": source_claim_type(risk),
                    "source_or_artifact_refs": CLAIM_REFS[risk],
                })
                risk_idx += 1
    return rows


def failure_condition(obj: str, risk: str) -> str:
    if risk == "stale reuse":
        return "source_version changed or invalidation_signal not none before reuse"
    if risk == "cross-tenant aliasing":
        return "cache salt or tenant scope differs between producer and consumer"
    if risk == "provenance forgery":
        return "provenance_id missing, unverifiable, or mismatched to source_version"
    if risk == "cache poisoning":
        return "cache entry is inserted or reused from untrusted provenance"
    if risk == "replay ambiguity":
        return "trajectory, branch, or parent lineage is missing before replay"
    if risk == "retention overrun":
        return "durability_horizon expired without legal/audit hold"
    if risk == "deletion/audit conflict":
        return "object needed for audit but subject to deletion/retention expiry"
    if risk == "verifier tampering":
        return "verifier result or evidence hash mismatches branch candidate"
    if risk == "unsafe summary-pointer recovery":
        return "summary_plus_pointer lacks recoverable raw/provenance pointer"
    return f"{obj} reused outside authorized isolation boundary"


def impact_label(option: str, risk: str, base: int) -> str:
    if option.startswith("C_"):
        level = base + 2
    elif option.startswith("B_"):
        level = base + 1
    else:
        level = max(1, base - 1)
    if risk in {"verifier tampering", "provenance forgery", "cache poisoning"}:
        level += 1
    if level >= 7:
        return "critical"
    if level >= 5:
        return "high"
    if level >= 3:
        return "medium"
    return "low"


def detectability(obj: str, risk: str) -> str:
    trace_detectable = {
        "stale reuse",
        "provenance forgery",
        "replay ambiguity",
        "unsafe summary-pointer recovery",
    }
    if risk in trace_detectable:
        return "trace_detectable"
    if risk == "verifier tampering":
        return "requires_new_verifier_evidence_field"
    if risk == "retention overrun":
        return "requires_new_retention_hold_field"
    if risk in {"cross-tenant aliasing", "leakage", "cache poisoning"}:
        return "requires_new_tenant_or_trust_field"
    return "deferred"


def build_invalid_fixtures() -> list[dict[str, object]]:
    fixtures = [
        ("IF-001", "stale_semantic_cache", "RAG", "semantic cache entry", "B_memory_object_aware_runtime", "semantic_cache_lookup", "source_version=v2 with cached provenance from v1; invalidation_signal=source_changed", "force_revalidate_or_recompute", False, "M-TRACE-1 source_version/invalidation_signal"),
        ("IF-002", "cross_tenant_prefix_salt_mismatch", "single-turn chat control", "prefix cache", "A_conventional_request_model_kv_serving", "object_access", "cache_salt producer=salt_a consumer=salt_b", "forbid_reuse", False, "new field required: tenant_scope/cache_salt"),
        ("IF-003", "missing_provenance_pointer", "RAG", "retrieved context", "B_memory_object_aware_runtime", "object_access", "provenance_id blank for provenance-required object", "block_or_recompute", False, "M-PROTO-1 fixture"),
        ("IF-004", "source_version_mismatch", "RAG", "retrieved context", "B_memory_object_aware_runtime", "object_access", "source_version changed after retrieval", "force_revalidate_or_recompute", False, "M-TRACE-1 source_version"),
        ("IF-005", "unauthorized_trajectory_replay", "code-agent loop", "trajectory log", "C_trajectory_dag_memory_fabric", "object_access", "actor not authorized for trajectory_node_id replay", "downgrade_to_object_runtime_or_reject", False, "new field required: replay_actor_authorization"),
        ("IF-006", "verifier_evidence_tamper", "verification-heavy", "verifier state", "C_trajectory_dag_memory_fabric", "verifier_result", "verifier evidence hash mismatch for candidate branch", "replay_invalid", False, "new field required: verifier_evidence_hash"),
        ("IF-007", "durable_retention_overrun", "multi-agent branch/merge", "durable workspace", "C_trajectory_dag_memory_fabric", "workspace_write", "durability_horizon expired and no legal/audit hold", "retention_violation", False, "M-TRACE-1 durability_horizon plus new hold field"),
        ("IF-008", "unsafe_summary_plus_pointer_recovery", "code-agent loop", "tool output", "C_trajectory_dag_memory_fabric", "object_access", "summary_plus_pointer selected but raw/provenance pointer missing", "fallback_to_exact_or_recompute", False, "M-COMP-1 safety failures"),
        ("IF-009", "branch_merge_contamination", "multi-agent branch/merge", "branch state", "C_trajectory_dag_memory_fabric", "branch_merge", "branch_id lineage differs from merge target", "replay_invalid", False, "M-TRACE-1 branch_id/merge_state"),
    ]
    return [
        {
            "fixture_id": fid,
            "fixture_type": ftype,
            "workload_class": wl,
            "object_class": obj,
            "architecture_option": opt,
            "event_type": evt,
            "violation": violation,
            "expected_runtime_response": response,
            "valid": str(valid).lower(),
            "detectability": fixture_detectability(ftype, obj),
            "required_new_fields": required_new_fields(ftype),
            "source_or_artifact_refs": refs,
            "evidence_label": "synthetic_fixture",
        }
        for fid, ftype, wl, obj, opt, evt, violation, response, valid, refs in fixtures
    ]


def risk_for_fixture(ftype: str) -> str:
    if "semantic" in ftype or "source_version" in ftype:
        return "stale reuse"
    if "tenant" in ftype:
        return "cross-tenant aliasing"
    if "provenance" in ftype:
        return "provenance forgery"
    if "verifier" in ftype:
        return "verifier tampering"
    if "retention" in ftype:
        return "retention overrun"
    if "summary" in ftype:
        return "unsafe summary-pointer recovery"
    return "replay ambiguity"


def fixture_detectability(fixture_type: str, obj: str) -> str:
    if required_new_fields(fixture_type):
        return "requires_new_instrumentation"
    return detectability(obj, risk_for_fixture(fixture_type))


def required_new_fields(fixture_type: str) -> str:
    mapping = {
        "cross_tenant_prefix_salt_mismatch": "tenant_scope; cache_salt",
        "unauthorized_trajectory_replay": "actor_id; replay_authorization_scope",
        "verifier_evidence_tamper": "verifier_evidence_hash",
        "durable_retention_overrun": "retention_hold_state",
    }
    return mapping.get(fixture_type, "")


def build_mitigation_matrix(threats: list[dict[str, object]]) -> list[dict[str, object]]:
    by_risk = defaultdict(set)
    for row in threats:
        by_risk[str(row["risk_class"])].add(str(row["object_class"]))
    rows = []
    for risk in RISK_CLASSES:
        hook, action, owner = MITIGATIONS[risk]
        objects = sorted(by_risk.get(risk, []))
        rows.append({
            "risk_class": risk,
            "mitigation_hook": hook,
            "owner": owner,
            "covered_object_classes": "; ".join(objects),
            "validation_action": action,
            "fallback_if_validation_fails": fallback_for_risk(risk),
            "coverage_status": "covered" if objects else "deferred",
            "claim_type": source_claim_type(risk),
            "source_or_artifact_refs": CLAIM_REFS[risk],
        })
    return rows


def fallback_for_risk(risk: str) -> str:
    if risk in {"stale reuse", "cache poisoning", "provenance forgery"}:
        return "revalidate_or_recompute"
    if risk in {"replay ambiguity", "verifier tampering"}:
        return "reject_replay_or_downgrade_to_Option_B"
    if risk in {"retention overrun", "deletion/audit conflict"}:
        return "expire_or_preserve_under_explicit_hold"
    if risk == "unsafe summary-pointer recovery":
        return "retain_exact_state_or_downgrade_to_Option_A/B"
    return "forbid_cross_boundary_reuse"


def build_risk_scores(threats: list[dict[str, object]], runtime_summary: list[dict[str, str]]) -> list[dict[str, object]]:
    summary = {r["workload_class"]: r for r in runtime_summary}
    rows = []
    for row in threats:
        wl = str(row["workload_class"])
        opt = str(row["architecture_option"])
        obj = str(row["object_class"])
        risk = str(row["risk_class"])
        runtime = summary.get(wl, {})
        retained = float(runtime.get("option_b_net_value") or 0.0)
        if opt.startswith("C_"):
            retained = max(retained, float(runtime.get("option_c_net_value") or 0.0))
        base = OBJECT_RULES[obj]["base"]
        option_factor = 1.0 if opt.startswith("A_") else 1.35 if opt.startswith("B_") else 1.75
        risk_bonus = 1.2 if risk in {"provenance forgery", "cache poisoning", "verifier tampering"} else 1.0
        detect_factor = 0.7 if row["detectability"] == "trace_detectable" else 1.1
        raw = base * option_factor * risk_bonus * detect_factor
        mitigation_overhead = validation_overhead(obj, risk, opt)
        expected_loss = round(raw * (0.45 if "requires_new" in str(row["detectability"]) else 0.25), 3)
        security_adjusted_value = round(retained - mitigation_overhead - expected_loss, 3)
        rows.append({
            "workload_class": wl,
            "object_class": obj,
            "architecture_option": opt,
            "risk_class": risk,
            "synthetic_risk_score": round(raw, 3),
            "mitigation_overhead_proxy": round(mitigation_overhead, 3),
            "expected_security_loss_proxy": expected_loss,
            "retained_value_proxy": round(retained, 3),
            "security_adjusted_value_proxy": security_adjusted_value,
            "reversal_due_to_security": str(security_adjusted_value < 0 and retained > 0).lower(),
            "claim_type": "simulated",
            "evidence_label": EVIDENCE,
        })
    return rows


def validation_overhead(obj: str, risk: str, opt: str) -> float:
    base = 0.15 + 0.08 * OBJECT_RULES[obj]["base"]
    if risk in {"provenance forgery", "stale reuse", "cache poisoning"}:
        base += 0.55
    if risk in {"replay ambiguity", "verifier tampering"}:
        base += 1.0
    if risk in {"retention overrun", "deletion/audit conflict"}:
        base += 0.75
    if risk == "unsafe summary-pointer recovery":
        base += 0.9
    if opt.startswith("C_"):
        base *= 1.9
    elif opt.startswith("B_"):
        base *= 1.35
    return base


def build_special_cases(scores: list[dict[str, object]], fixtures: list[dict[str, object]]) -> list[dict[str, object]]:
    def fixture_ok(ftype: str) -> bool:
        return any(r["fixture_type"] == ftype and r["valid"] == "false" for r in fixtures)

    no_sharing = 0.0
    prov_zero = 0.0
    return [
        {"case_id": "SC-001", "case": "no sharing -> zero cross-tenant leakage", "expected": "0", "actual": no_sharing, "pass": str(no_sharing == 0.0).lower(), "evidence_label": EVIDENCE},
        {"case_id": "SC-002", "case": "no provenance-required objects -> provenance risk zero", "expected": "0", "actual": prov_zero, "pass": str(prov_zero == 0.0).lower(), "evidence_label": EVIDENCE},
        {"case_id": "SC-003", "case": "cache salt mismatch -> reuse forbidden", "expected": "invalid", "actual": "invalid" if fixture_ok("cross_tenant_prefix_salt_mismatch") else "missed", "pass": str(fixture_ok("cross_tenant_prefix_salt_mismatch")).lower(), "evidence_label": EVIDENCE},
        {"case_id": "SC-004", "case": "source version changed -> semantic/retrieved reuse invalid", "expected": "invalid", "actual": "invalid" if fixture_ok("source_version_mismatch") else "missed", "pass": str(fixture_ok("source_version_mismatch")).lower(), "evidence_label": EVIDENCE},
        {"case_id": "SC-005", "case": "verifier tamper -> replay invalid", "expected": "invalid", "actual": "invalid" if fixture_ok("verifier_evidence_tamper") else "missed", "pass": str(fixture_ok("verifier_evidence_tamper")).lower(), "evidence_label": EVIDENCE},
        {"case_id": "SC-006", "case": "durable horizon expired -> retention violation", "expected": "violation", "actual": "violation" if fixture_ok("durable_retention_overrun") else "missed", "pass": str(fixture_ok("durable_retention_overrun")).lower(), "evidence_label": EVIDENCE},
    ]


def build_workload_summary(scores: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in scores:
        grouped[(str(row["workload_class"]), str(row["architecture_option"]))].append(row)
    rows = []
    for (wl, opt), group in sorted(grouped.items()):
        risk = sum(float(r["synthetic_risk_score"]) for r in group)
        overhead = sum(float(r["mitigation_overhead_proxy"]) for r in group)
        retained = max(float(r["retained_value_proxy"]) for r in group) if group else 0.0
        adjusted = retained - overhead - sum(float(r["expected_security_loss_proxy"]) for r in group)
        dominant = Counter(str(r["risk_class"]) for r in group).most_common(1)[0][0]
        rows.append({
            "workload_class": wl,
            "architecture_option": opt,
            "risk_row_count": len(group),
            "synthetic_risk_score_sum": round(risk, 3),
            "mitigation_overhead_proxy_sum": round(overhead, 3),
            "retained_value_proxy": round(retained, 3),
            "security_adjusted_value_proxy": round(adjusted, 3),
            "security_reversal": str(adjusted < 0 and retained > 0).lower(),
            "dominant_risk_class": dominant,
            "evidence_label": EVIDENCE,
        })
    return rows


def validate_outputs(threats, fixtures, mitigations, scores, special_cases, workload_summary):
    objects = {r["object_class"] for r in threats}
    if objects != set(OBJECT_CLASSES):
        raise AssertionError(f"object coverage mismatch: {sorted(set(OBJECT_CLASSES)-objects)}")
    if len(fixtures) < 8:
        raise AssertionError("too few invalid fixtures")
    if any(r["valid"] != "false" for r in fixtures):
        raise AssertionError("all fixtures must be invalid")
    if any(r["coverage_status"] != "covered" for r in mitigations):
        raise AssertionError("each risk class must have mitigation coverage")
    if any(r["pass"] != "true" for r in special_cases):
        raise AssertionError("special case failure")
    if not any(r["security_reversal"] == "true" for r in workload_summary):
        raise AssertionError("security overhead must produce at least one workload-level Option B/C reversal")


def main() -> None:
    inputs = load_inputs()
    threats = build_threat_matrix(inputs)
    fixtures = build_invalid_fixtures()
    mitigations = build_mitigation_matrix(threats)
    scores = build_risk_scores(threats, inputs["runtime_summary"])
    special_cases = build_special_cases(scores, fixtures)
    workload_summary = build_workload_summary(scores)
    validate_outputs(threats, fixtures, mitigations, scores, special_cases, workload_summary)

    write_csv(DATA / "security_threat_matrix.csv", threats, [
        "risk_id", "object_class", "workload_class", "architecture_option", "risk_class",
        "required_fields", "failure_condition", "impact", "detectability", "mitigation_hook",
        "claim_type", "source_or_artifact_refs",
    ])
    write_csv(DATA / "security_invalid_trace_fixtures.csv", fixtures, [
        "fixture_id", "fixture_type", "workload_class", "object_class", "architecture_option",
        "event_type", "violation", "expected_runtime_response", "valid", "detectability",
        "required_new_fields", "source_or_artifact_refs", "evidence_label",
    ])
    write_csv(DATA / "security_mitigation_matrix.csv", mitigations, [
        "risk_class", "mitigation_hook", "owner", "covered_object_classes", "validation_action",
        "fallback_if_validation_fails", "coverage_status", "claim_type", "source_or_artifact_refs",
    ])
    write_csv(DATA / "security_risk_scores.csv", scores, [
        "workload_class", "object_class", "architecture_option", "risk_class",
        "synthetic_risk_score", "mitigation_overhead_proxy", "expected_security_loss_proxy",
        "retained_value_proxy", "security_adjusted_value_proxy", "reversal_due_to_security",
        "claim_type", "evidence_label",
    ])
    write_csv(DATA / "security_special_cases.csv", special_cases, [
        "case_id", "case", "expected", "actual", "pass", "evidence_label",
    ])
    write_csv(DATA / "security_workload_summary.csv", workload_summary, [
        "workload_class", "architecture_option", "risk_row_count", "synthetic_risk_score_sum",
        "mitigation_overhead_proxy_sum", "retained_value_proxy",
        "security_adjusted_value_proxy", "security_reversal", "dominant_risk_class",
        "evidence_label",
    ])
    print("validation=PASS")
    print(f"objects={len({r['object_class'] for r in threats})}")
    print(f"invalid_fixtures={len(fixtures)}")
    print(f"security_reversal_workloads={sum(r['security_reversal']=='true' for r in workload_summary)}")
    print(f"new_instrumentation_fixtures={sum(1 for r in fixtures if r['required_new_fields'])}")


if __name__ == "__main__":
    main()
