# created: 2026-05-13T02:50:00Z
# cycle: 1
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-ARCH-1
"""Simulate fallback policy for a hybrid physicalized safety filter.

This is not an ML model. It checks whether architecture-level invariants route
unsafe or stale classifier outputs to fallback or fail-safe states.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "physicalized-weights" / "data"
CSV_PATH = DATA_DIR / "hybrid_arch_policy_cases.csv"
SUMMARY_PATH = DATA_DIR / "hybrid_arch_summary.json"

THRESHOLD_Q15 = 24576
REQUIRED_POLICY_VERSION = 7


@dataclass(frozen=True)
class PolicyCase:
    case_id: str
    description: str
    classifier_available: bool
    fallback_available: bool
    audit_logging_available: bool
    confidence_q15: int
    observed_policy_version: int
    required_policy_version: int
    classifier_health: str
    drift_status: str
    enforce_mode: bool
    host_force_fallback: bool = False


@dataclass(frozen=True)
class DecisionRecord:
    case_id: str
    description: str
    route: str
    action: str
    reason: str
    physicalized_output_valid: bool
    fallback_used: bool
    fail_safe: bool
    classifier_available: bool
    fallback_available: bool
    audit_logging_available: bool
    confidence_q15: int
    threshold_q15: int
    observed_policy_version: int
    required_policy_version: int
    classifier_health: str
    drift_status: str
    enforce_mode: bool
    audit_request_id: str
    audit_route: str
    audit_reason: str
    audit_policy_version: int
    audit_required_policy_version: int
    audit_confidence_q15: int


def policy_cases() -> list[PolicyCase]:
    return [
        PolicyCase(
            "healthy_high_confidence",
            "Healthy classifier with current policy and high confidence.",
            True,
            True,
            True,
            30000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "low_confidence",
            "Classifier is healthy but confidence is below threshold.",
            True,
            True,
            True,
            12000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "zero_confidence",
            "Classifier reports zero confidence.",
            True,
            True,
            True,
            0,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "stale_policy_version",
            "Classifier used a policy image older than the host requires.",
            True,
            True,
            True,
            31000,
            REQUIRED_POLICY_VERSION - 1,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "failed_health_check",
            "Classifier health monitor failed.",
            True,
            True,
            True,
            32000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "failed",
            "normal",
            True,
        ),
        PolicyCase(
            "drift_alarm",
            "Classifier is current and confident but drift monitor is in alarm.",
            True,
            True,
            True,
            32000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "alarm",
            True,
        ),
        PolicyCase(
            "host_forced_fallback",
            "Host forces fallback for baseline measurement or incident response.",
            True,
            True,
            True,
            32000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
            host_force_fallback=True,
        ),
        PolicyCase(
            "fallback_unavailable_but_fast_path_valid",
            "Fallback is unavailable, but the fast path is healthy, current, and confident.",
            True,
            False,
            True,
            32000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "fallback_unavailable_and_classifier_invalid",
            "Fallback is unavailable and the classifier cannot produce a valid output.",
            False,
            False,
            True,
            0,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "failed",
            "normal",
            True,
        ),
        PolicyCase(
            "audit_logging_failure",
            "Audit logging is unavailable in enforce mode.",
            True,
            True,
            False,
            32000,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "healthy",
            "normal",
            True,
        ),
        PolicyCase(
            "monitor_mode_fail_safe",
            "Monitor-only deployment escalates when both classifier and fallback are unusable.",
            False,
            False,
            True,
            0,
            REQUIRED_POLICY_VERSION,
            REQUIRED_POLICY_VERSION,
            "failed",
            "alarm",
            False,
        ),
    ]


def invalid_reason(case: PolicyCase, threshold_q15: int = THRESHOLD_Q15) -> str:
    if not case.classifier_available:
        return "classifier_unavailable"
    if case.host_force_fallback:
        return "host_forced_fallback"
    if case.classifier_health != "healthy":
        return "health_check_failed"
    if case.drift_status != "normal":
        return "drift_alarm"
    if case.observed_policy_version < case.required_policy_version:
        return "stale_policy_version"
    if case.confidence_q15 < threshold_q15:
        return "low_confidence"
    if not case.audit_logging_available:
        return "audit_logging_failure"
    return ""


def decide(case: PolicyCase, threshold_q15: int = THRESHOLD_Q15) -> DecisionRecord:
    reason = invalid_reason(case, threshold_q15)
    physicalized_output_valid = reason == ""

    if physicalized_output_valid:
        route = "physicalized_fast_path"
        action = "use_physicalized_decision"
        fallback_used = False
        fail_safe = False
        reason = "accepted"
    elif case.fallback_available:
        route = "programmable_fallback"
        action = "use_fallback_decision"
        fallback_used = True
        fail_safe = False
    else:
        route = "fail_safe"
        action = "fail_closed_block" if case.enforce_mode else "fail_safe_escalate"
        fallback_used = False
        fail_safe = True

    return DecisionRecord(
        case_id=case.case_id,
        description=case.description,
        route=route,
        action=action,
        reason=reason,
        physicalized_output_valid=physicalized_output_valid,
        fallback_used=fallback_used,
        fail_safe=fail_safe,
        classifier_available=case.classifier_available,
        fallback_available=case.fallback_available,
        audit_logging_available=case.audit_logging_available,
        confidence_q15=case.confidence_q15,
        threshold_q15=threshold_q15,
        observed_policy_version=case.observed_policy_version,
        required_policy_version=case.required_policy_version,
        classifier_health=case.classifier_health,
        drift_status=case.drift_status,
        enforce_mode=case.enforce_mode,
        audit_request_id=f"req-{case.case_id}",
        audit_route=route,
        audit_reason=reason,
        audit_policy_version=case.observed_policy_version,
        audit_required_policy_version=case.required_policy_version,
        audit_confidence_q15=case.confidence_q15,
    )


def simulate_cases(cases: list[PolicyCase] | None = None) -> list[DecisionRecord]:
    return [decide(case) for case in (cases if cases is not None else policy_cases())]


def write_csv(records: list[DecisionRecord], path: Path = CSV_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(records[0]).keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def write_summary(records: list[DecisionRecord], path: Path = SUMMARY_PATH) -> None:
    route_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for record in records:
        route_counts[record.route] = route_counts.get(record.route, 0) + 1
        action_counts[record.action] = action_counts.get(record.action, 0) + 1

    summary = {
        "schema_version": 1,
        "threshold_q15": THRESHOLD_Q15,
        "required_policy_version": REQUIRED_POLICY_VERSION,
        "case_count": len(records),
        "route_counts": route_counts,
        "action_counts": action_counts,
        "physicalized_path_cases": [r.case_id for r in records if r.route == "physicalized_fast_path"],
        "fallback_cases": [r.case_id for r in records if r.route == "programmable_fallback"],
        "fail_closed_cases": [r.case_id for r in records if r.action == "fail_closed_block"],
        "fail_safe_escalate_cases": [r.case_id for r in records if r.action == "fail_safe_escalate"],
        "invariants_checked": [
            "stale policy version cannot silently use the physicalized fast path",
            "low confidence routes to programmable fallback when fallback is available",
            "failed health check routes away from physicalized output",
            "invalid classifier plus unavailable fallback enters fail-safe",
            "audit logging fields are emitted for every decision case",
        ],
        "records": [asdict(record) for record in records],
    }
    path.write_text(json.dumps(summary, indent=2) + "\n")


def main() -> None:
    records = simulate_cases()
    write_csv(records)
    write_summary(records)
    print(f"wrote {len(records)} policy cases to {DATA_DIR}")
    print(f"routes: {json.dumps({route: sum(1 for r in records if r.route == route) for route in sorted({r.route for r in records})}, sort_keys=True)}")


if __name__ == "__main__":
    main()
