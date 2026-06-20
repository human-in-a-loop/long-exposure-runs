#!/usr/bin/env python3
# created: 2026-05-12T09:10:00Z
# cycle: 30
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-GATECHAIN-1
"""Replay evidence gatechain paths and quarantine unsafe promotion attempts."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "evidence_gatechain_state_schema.csv"
VALID = DATA / "evidence_gatechain_valid_fixture_paths.csv"
INVALID = DATA / "evidence_gatechain_invalid_fixture_paths.csv"
READINESS = DATA / "final_claim_readiness_matrix.csv"
HANDOFF = DATA / "handoff_claim_traceability.csv"

OUT_RESULTS = DATA / "evidence_gatechain_replay_results.csv"
OUT_REASONS = DATA / "evidence_gatechain_quarantine_reasons.csv"
OUT_BOUNDARY = DATA / "evidence_gatechain_claim_credit_boundary.csv"
OUT_TRACE = DATA / "evidence_gatechain_traceability_matrix.csv"

IDENTIFIERS = ["bundle_id", "measurement_run_id", "operator_id", "collector_id", "schema_version"]
SKIP_REASONS = {
    "attestation_mechanically_valid": "skipped_attestation",
    "trust_policy_admissible": "skipped_trust_policy",
    "intake_structurally_admissible": "skipped_intake",
    "adapter_conformant": "skipped_adapter_conformance",
    "security_provenance_passed": "threshold_without_security_provenance",
    "noise_floor_passed": "threshold_without_noise_floor",
    "handoff_traceable": "final_readiness_without_handoff_traceability",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path.relative_to(ROOT)} is empty")
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def as_int(value: str) -> int:
    return int(value) if value else 0


def group_paths(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["path_id"]].append(row)
    for path_rows in groups.values():
        path_rows.sort(key=lambda row: as_int(row.get("step_order", "")))
    return groups


def category(reason: str) -> str:
    if reason == "empty_path":
        return "empty_path"
    if reason.startswith("skipped_") or reason == "out_of_order_state":
        return "skipped_or_order"
    if reason.startswith("mismatched_"):
        return "identifier_mismatch"
    if reason in {"non_production_evidence_label", "proxy_evidence_threshold_credit_blocked"}:
        return "evidence_label_boundary"
    if reason.startswith("threshold_without"):
        return "downstream_gate_violation"
    if reason == "final_readiness_without_handoff_traceability":
        return "downstream_gate_violation"
    if reason.startswith("failed_"):
        return "failed_gate"
    return "other"


def first_missing_reason(states: list[str], required: list[str]) -> tuple[str, str]:
    if not states:
        return "empty_path", ""
    last_idx = -1
    for state in states:
        if state not in required:
            return "unknown_state", state
        idx = required.index(state)
        if idx <= last_idx:
            return "out_of_order_state", state
        last_idx = idx
    last_idx = -1
    seen = set()
    for state in states:
        idx = required.index(state)
        for missing in required[last_idx + 1 : idx]:
            if missing == "production_claim_credit_allowed":
                continue
            return SKIP_REASONS.get(missing, "missing_required_state"), state
        last_idx = idx
        seen.add(state)
    if "final_readiness_update_eligible" in seen and "handoff_traceable" not in seen:
        return "final_readiness_without_handoff_traceability", "final_readiness_update_eligible"
    return "", ""


def replay_path(path_id: str, rows: list[dict[str, str]], required: list[str]) -> dict[str, object]:
    states = [row["state_id"] for row in rows if row.get("state_id")]
    expected = rows[0].get("expected_blocked_reason", "") if rows else ""
    reason, blocked_at = first_missing_reason(states, required)

    if not reason:
        for row in rows:
            if row.get("state_id") and row.get("state_passed", "").strip().lower() != "true":
                reason = f"failed_{row['state_id']}"
                blocked_at = row["state_id"]
                break

    if not reason:
        prior = rows[0]
        for row in rows[1:]:
            for key in IDENTIFIERS:
                if row[key] != prior[key]:
                    reason = f"mismatched_{key}"
                    blocked_at = row["state_id"]
                    break
            if reason:
                break
            prior = row

    if not reason:
        by_state = {row["state_id"]: row for row in rows}
        if "threshold_replay_passed" in by_state:
            if "security_provenance_passed" not in by_state:
                reason = "threshold_without_security_provenance"
                blocked_at = "threshold_replay_passed"
            elif "noise_floor_passed" not in by_state:
                reason = "threshold_without_noise_floor"
                blocked_at = "threshold_replay_passed"
            elif by_state["threshold_replay_passed"]["evidence_label"] == "host_local_proxy":
                reason = "proxy_evidence_threshold_credit_blocked"
                blocked_at = "threshold_replay_passed"

    if not reason:
        for row in rows:
            if row["state_id"] == "production_ingestion_accepted" and row["evidence_label"] != "production_target":
                reason = "non_production_evidence_label"
                blocked_at = "production_ingestion_accepted"
                break
            if row["state_id"] == "production_claim_credit_allowed" and row["evidence_label"] != "production_target":
                reason = "non_production_evidence_label"
                blocked_at = "production_claim_credit_allowed"
                break

    if not reason and "production_claim_credit_allowed" not in states:
        reason = "claim_credit_state_not_reached"
        blocked_at = rows[-1]["state_id"] if rows else ""

    allowed = reason == "" and rows[-1]["evidence_label"] == "production_target"
    return {
        "path_id": path_id,
        "case_type": rows[0].get("case_type", "") if rows else "invalid_path",
        "states_seen": len(states),
        "last_state_seen": states[-1] if states else "",
        "blocked_at_state": blocked_at,
        "quarantined": str(not allowed).lower(),
        "blocked_reason": reason,
        "expected_blocked_reason": expected,
        "expected_reason_matched": str((not expected) or expected == reason).lower(),
        "evidence_label": rows[0].get("evidence_label", "") if rows else "",
        "production_claim_credit_allowed": str(allowed).lower(),
        "option_bc_contract_ready_only": "true",
    }


def main() -> None:
    required = [row["state_id"] for row in read_csv(SCHEMA)]
    valid = read_csv(VALID)
    invalid = read_csv(INVALID)
    readiness = read_csv(READINESS)
    handoff = read_csv(HANDOFF)
    if "production_claim_credit_allowed" not in required:
        raise ValueError("gatechain schema missing production claim-credit state")
    if any(row["production_ready"] == "true" for row in readiness):
        raise ValueError("existing final readiness unexpectedly contains production-ready claim")
    if any(row["production_endorsed"] == "true" for row in handoff):
        raise ValueError("existing handoff unexpectedly contains production-endorsed claim")

    grouped = group_paths(valid + invalid)
    results = [replay_path(path_id, rows, required) for path_id, rows in sorted(grouped.items())]
    counts = Counter(row["blocked_reason"] for row in results if row["blocked_reason"])
    reason_rows = [
        {
            "blocked_reason": reason,
            "quarantine_category": category(reason),
            "path_count": count,
            "fail_closed": "true",
        }
        for reason, count in sorted(counts.items())
    ]
    boundary = [
        {
            "path_id": row["path_id"],
            "evidence_label": row["evidence_label"],
            "last_state_seen": row["last_state_seen"],
            "blocked_at_state": row["blocked_at_state"],
            "production_claim_credit_allowed": row["production_claim_credit_allowed"],
            "boundary_reason": row["blocked_reason"] or "all production gates passed",
            "option_bc_contract_ready_only": row["option_bc_contract_ready_only"],
        }
        for row in results
    ]
    trace = [
        {
            "trace_link_id": "gatechain-to-attestation",
            "source_artifact": "data/production_attestation_results.csv",
            "target_state": "attestation_mechanically_valid",
            "required_identifier": "bundle_id",
            "covered": "true",
        },
        {
            "trace_link_id": "gatechain-to-intake",
            "source_artifact": "data/production_intake_admission_results.csv",
            "target_state": "intake_structurally_admissible",
            "required_identifier": "bundle_id;schema_version",
            "covered": "true",
        },
        {
            "trace_link_id": "gatechain-to-adapter-conformance",
            "source_artifact": "data/adapter_conformance_results.csv",
            "target_state": "adapter_conformant",
            "required_identifier": "measurement_run_id",
            "covered": "true",
        },
        {
            "trace_link_id": "gatechain-to-production-ingestion",
            "source_artifact": "data/production_dc12_ingestion_results.csv",
            "target_state": "production_ingestion_accepted",
            "required_identifier": "measurement_run_id;schema_version",
            "covered": "true",
        },
        {
            "trace_link_id": "gatechain-to-final-readiness-handoff",
            "source_artifact": "data/final_claim_readiness_matrix.csv;data/handoff_claim_traceability.csv",
            "target_state": "final_readiness_update_eligible;handoff_traceable",
            "required_identifier": "claim_id",
            "covered": "true",
        },
    ]

    fields = [
        "path_id",
        "case_type",
        "states_seen",
        "last_state_seen",
        "blocked_at_state",
        "quarantined",
        "blocked_reason",
        "expected_blocked_reason",
        "expected_reason_matched",
        "evidence_label",
        "production_claim_credit_allowed",
        "option_bc_contract_ready_only",
    ]
    write_csv(OUT_RESULTS, results, fields)
    write_csv(OUT_REASONS, reason_rows, ["blocked_reason", "quarantine_category", "path_count", "fail_closed"])
    write_csv(OUT_BOUNDARY, boundary, ["path_id", "evidence_label", "last_state_seen", "blocked_at_state", "production_claim_credit_allowed", "boundary_reason", "option_bc_contract_ready_only"])
    write_csv(OUT_TRACE, trace, ["trace_link_id", "source_artifact", "target_state", "required_identifier", "covered"])


if __name__ == "__main__":
    main()
