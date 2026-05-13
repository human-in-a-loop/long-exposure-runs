# created: 2026-05-13T15:48:00Z
# cycle: 5
# run_id: run-2026-05-13T015136Z
# agent: worker
# milestone: M-LIFECYCLE-1
"""Compose validated evidence-package gates into one lifecycle state machine."""

from __future__ import annotations

import csv
import json
import struct
import zlib
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "physicalized-weights" / "data"
DOCS = ROOT / "physicalized-weights" / "docs"

CASES_CSV = DATA / "evidence_package_lifecycle_cases.csv"
RESULTS_CSV = DATA / "evidence_package_lifecycle_results.csv"
SUMMARY_JSON = DATA / "evidence_package_lifecycle_summary.json"
FLOW_PNG = DATA / "evidence_package_lifecycle_flow.png"
REPORT_MD = DOCS / "evidence_package_lifecycle_state_machine.md"

MILESTONE_ID = "M-LIFECYCLE-1"
SCHEMA_VERSION = 1
FIGURE_CAPTION = (
    "State-machine flow from acquisition design through dry-run, intake, replay, "
    "threshold, and uncertainty gates, with terminal non-reopen states and the "
    "single hypothetical actual-measured candidate path highlighted."
)

CASE_FIELDS = [
    "case_id",
    "description",
    "artifact_class",
    "source_actuality",
    "acquisition_ready",
    "dryrun_ready",
    "intake_preserved",
    "package_valid",
    "hash_match",
    "threshold_mapping_known",
    "privacy_attestation",
    "provenance_attestation",
    "replay_valid",
    "admissible_source",
    "measured_terms",
    "request_count",
    "accepted_fast_path_count",
    "fallback_frequency",
    "threshold_crossed",
    "uncertainty_classification",
    "uncertainty_durable",
    "hypothetical_control",
    "current_artifact",
    "expected_terminal_state",
]

LIFECYCLE_STATES = [
    "design_screened",
    "collection_ready_not_evidence",
    "dryrun_ready_not_evidence",
    "intake_rehearsed_not_evidence",
    "replay_valid_nonactual",
    "replay_blocked",
    "threshold_evaluable_not_crossed",
    "threshold_crossed_nonactual",
    "uncertainty_inconclusive",
    "statistically_durable_nonactual",
    "actual_reopen_candidate",
    "blocked_invalid_or_unsafe",
]

STATE_OWNERS = {
    "design_screened": "M-ACQUIRE-1",
    "collection_ready_not_evidence": "M-ACQUIRE-1",
    "dryrun_ready_not_evidence": "M-DRYRUN-1",
    "intake_rehearsed_not_evidence": "M-INTAKE-1",
    "replay_valid_nonactual": "M-EVIDENCEPACK-1",
    "replay_blocked": "M-EVIDENCEPACK-1",
    "threshold_evaluable_not_crossed": "M-REOPEN-1",
    "threshold_crossed_nonactual": "M-REOPEN-1",
    "uncertainty_inconclusive": "M-UNCERTAINTY-1",
    "statistically_durable_nonactual": "M-UNCERTAINTY-1",
    "actual_reopen_candidate": "M-UNCERTAINTY-1",
    "blocked_invalid_or_unsafe": "M-EVIDENCEPACK-1/M-REOPEN-1",
}

ACTUAL_SOURCES = {
    "actual_measured_shadow",
    "actual_measured_canary",
    "actual_measured_production",
}


DEFAULT_CASES = [
    {
        "case_id": "acquisition_shadow_ready_design",
        "description": "M-ACQUIRE-1-ready shadow design before collection.",
        "artifact_class": "acquisition_design",
        "source_actuality": "readiness_plan",
        "acquisition_ready": "true",
        "dryrun_ready": "false",
        "intake_preserved": "false",
        "package_valid": "false",
        "hash_match": "false",
        "threshold_mapping_known": "true",
        "privacy_attestation": "false",
        "provenance_attestation": "false",
        "replay_valid": "false",
        "admissible_source": "true",
        "measured_terms": "false",
        "request_count": "0",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "0",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "collection_ready_not_evidence",
    },
    {
        "case_id": "dryrun_complete_template_only",
        "description": "M-DRYRUN-1 complete template with no measured rows.",
        "artifact_class": "dryrun_template",
        "source_actuality": "template_dryrun",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "false",
        "package_valid": "false",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "false",
        "provenance_attestation": "false",
        "replay_valid": "false",
        "admissible_source": "true",
        "measured_terms": "false",
        "request_count": "0",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "0",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "dryrun_ready_not_evidence",
    },
    {
        "case_id": "intake_shadow_synthetic_non_crossing",
        "description": "M-INTAKE-1 shadow rehearsal package that reaches replay as non-crossing.",
        "artifact_class": "intake_rehearsal",
        "source_actuality": "synthetic_safe_rehearsal",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "6",
        "accepted_fast_path_count": "4",
        "fallback_frequency": "0.33",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "intake_rehearsed_not_evidence",
    },
    {
        "case_id": "intake_canary_synthetic_non_crossing",
        "description": "M-INTAKE-1 canary rehearsal package that reaches replay as non-crossing.",
        "artifact_class": "intake_rehearsal",
        "source_actuality": "synthetic_safe_rehearsal",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "6",
        "accepted_fast_path_count": "4",
        "fallback_frequency": "0.33",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "intake_rehearsed_not_evidence",
    },
    {
        "case_id": "synthetic_counterfactual_threshold_crossing",
        "description": "Synthetic replay crosses the point threshold but is not actual evidence.",
        "artifact_class": "evidence_pack_replay",
        "source_actuality": "synthetic_control",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "false",
        "measured_terms": "true",
        "request_count": "6",
        "accepted_fast_path_count": "4",
        "fallback_frequency": "0.33",
        "threshold_crossed": "true",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "threshold_crossed_nonactual",
    },
    {
        "case_id": "uncertainty_durable_synthetic_control",
        "description": "Synthetic control crosses the threshold and uncertainty rule but remains nonactual.",
        "artifact_class": "uncertainty_control",
        "source_actuality": "synthetic_control",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "false",
        "measured_terms": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "800000",
        "fallback_frequency": "0.03",
        "threshold_crossed": "true",
        "uncertainty_classification": "statistically_durable_nonactual_control",
        "uncertainty_durable": "true",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "statistically_durable_nonactual",
    },
    {
        "case_id": "noisy_point_crossing_actual_like_blocked_by_uncertainty",
        "description": "Actual-like package crosses the point threshold but fails UCB durability.",
        "artifact_class": "future_measured_candidate_control",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "650000",
        "fallback_frequency": "0.08",
        "threshold_crossed": "true",
        "uncertainty_classification": "point_crossing_not_statistically_durable",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "false",
        "expected_terminal_state": "uncertainty_inconclusive",
    },
    {
        "case_id": "missing_privacy_attestation",
        "description": "Package has no privacy attestation and must stop before replay.",
        "artifact_class": "evidence_pack_replay",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "false",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "false",
        "provenance_attestation": "true",
        "replay_valid": "false",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000",
        "accepted_fast_path_count": "700",
        "fallback_frequency": "0.1",
        "threshold_crossed": "true",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "blocked_invalid_or_unsafe",
    },
    {
        "case_id": "stale_trace_hash",
        "description": "Hash mismatch from M-EVIDENCEPACK-1/M-INTAKE-1 blocks before threshold evaluation.",
        "artifact_class": "evidence_pack_replay",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "false",
        "package_valid": "false",
        "hash_match": "false",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "false",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000",
        "accepted_fast_path_count": "700",
        "fallback_frequency": "0.1",
        "threshold_crossed": "true",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "replay_blocked",
    },
    {
        "case_id": "unknown_threshold_mapping",
        "description": "Unknown threshold scenario blocks before threshold or uncertainty evaluation.",
        "artifact_class": "evidence_pack_replay",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "false",
        "hash_match": "true",
        "threshold_mapping_known": "false",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "false",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000",
        "accepted_fast_path_count": "700",
        "fallback_frequency": "0.1",
        "threshold_crossed": "true",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "replay_blocked",
    },
    {
        "case_id": "zero_volume_measured_like",
        "description": "Measured-like package with zero request volume cannot create amortized margin evidence.",
        "artifact_class": "future_measured_candidate_control",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "0",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "0",
        "threshold_crossed": "true",
        "uncertainty_classification": "blocked_zero_volume",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "false",
        "expected_terminal_state": "blocked_invalid_or_unsafe",
    },
    {
        "case_id": "all_fallback_measured_like",
        "description": "Measured-like package with all fallback has no accepted physicalized fast-path credit.",
        "artifact_class": "future_measured_candidate_control",
        "source_actuality": "actual_measured_canary",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "100000",
        "accepted_fast_path_count": "0",
        "fallback_frequency": "1",
        "threshold_crossed": "true",
        "uncertainty_classification": "blocked_all_fallback",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "false",
        "expected_terminal_state": "blocked_invalid_or_unsafe",
    },
    {
        "case_id": "proxy_replay_valid_nonactual",
        "description": "Proxy package is replay-valid enough to diagnose but cannot proceed as actual evidence.",
        "artifact_class": "evidence_pack_replay",
        "source_actuality": "local_proxy",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "false",
        "measured_terms": "false",
        "request_count": "100000",
        "accepted_fast_path_count": "60000",
        "fallback_frequency": "0.1",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "true",
        "expected_terminal_state": "replay_valid_nonactual",
    },
    {
        "case_id": "actual_measured_threshold_not_crossed_control",
        "description": "Actual-like measured package reaches threshold evaluation but does not cross.",
        "artifact_class": "future_measured_candidate_control",
        "source_actuality": "actual_measured_shadow",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "700000",
        "fallback_frequency": "0.05",
        "threshold_crossed": "false",
        "uncertainty_classification": "not_evaluated",
        "uncertainty_durable": "false",
        "hypothetical_control": "false",
        "current_artifact": "false",
        "expected_terminal_state": "threshold_evaluable_not_crossed",
    },
    {
        "case_id": "hypothetical_actual_measured_durable_candidate_control",
        "description": "Positive control for a future fully measured, durable, privacy-safe candidate branch.",
        "artifact_class": "future_measured_candidate_control",
        "source_actuality": "actual_measured_canary",
        "acquisition_ready": "true",
        "dryrun_ready": "true",
        "intake_preserved": "true",
        "package_valid": "true",
        "hash_match": "true",
        "threshold_mapping_known": "true",
        "privacy_attestation": "true",
        "provenance_attestation": "true",
        "replay_valid": "true",
        "admissible_source": "true",
        "measured_terms": "true",
        "request_count": "1000000",
        "accepted_fast_path_count": "850000",
        "fallback_frequency": "0.02",
        "threshold_crossed": "true",
        "uncertainty_classification": "statistically_durable_actual_candidate",
        "uncertainty_durable": "true",
        "hypothetical_control": "true",
        "current_artifact": "false",
        "expected_terminal_state": "actual_reopen_candidate",
    },
]


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_float(value: str) -> float:
    try:
        return float(str(value).strip())
    except ValueError:
        return 0.0


def ensure_cases() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if CASES_CSV.exists():
        return
    with CASES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CASE_FIELDS)
        writer.writeheader()
        writer.writerows(DEFAULT_CASES)


def read_cases() -> list[dict[str, str]]:
    ensure_cases()
    with CASES_CSV.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def result(row: dict[str, str], state: str, rationale: str, evaluated: bool = False) -> dict[str, str]:
    actual_branch = state == "actual_reopen_candidate"
    hypothetical = parse_bool(row["hypothetical_control"])
    current = parse_bool(row["current_artifact"])
    return {
        "case_id": row["case_id"],
        "artifact_class": row["artifact_class"],
        "source_actuality": row["source_actuality"],
        "terminal_state": state,
        "expected_terminal_state": row["expected_terminal_state"],
        "status_matches_expected": str(state == row["expected_terminal_state"]),
        "owning_gate": STATE_OWNERS[state],
        "reopen_allowed": str(actual_branch),
        "actual_reopen_candidate": str(actual_branch and not hypothetical),
        "hypothetical_actual_candidate_control": str(actual_branch and hypothetical),
        "current_artifact": str(current),
        "threshold_evaluated": str(evaluated or state in {"threshold_evaluable_not_crossed", "threshold_crossed_nonactual", "uncertainty_inconclusive", "statistically_durable_nonactual", "actual_reopen_candidate"}),
        "uncertainty_evaluated": str(state in {"uncertainty_inconclusive", "statistically_durable_nonactual", "actual_reopen_candidate"}),
        "rationale": rationale,
    }


def classify(row: dict[str, str]) -> dict[str, str]:
    artifact_class = row["artifact_class"]
    source_actuality = row["source_actuality"]
    package_valid = parse_bool(row["package_valid"])
    hash_match = parse_bool(row["hash_match"])
    threshold_mapping_known = parse_bool(row["threshold_mapping_known"])
    privacy_attestation = parse_bool(row["privacy_attestation"])
    provenance_attestation = parse_bool(row["provenance_attestation"])
    replay_valid = parse_bool(row["replay_valid"])
    admissible_source = parse_bool(row["admissible_source"])
    measured_terms = parse_bool(row["measured_terms"])
    threshold_crossed = parse_bool(row["threshold_crossed"])
    uncertainty_durable = parse_bool(row["uncertainty_durable"])
    request_count = parse_float(row["request_count"])
    accepted_fast_path_count = parse_float(row["accepted_fast_path_count"])
    fallback_frequency = parse_float(row["fallback_frequency"])

    if artifact_class == "acquisition_design" and parse_bool(row["acquisition_ready"]):
        return result(row, "collection_ready_not_evidence", "M-ACQUIRE-1 screens a future collection design; readiness is not measured evidence.")
    if artifact_class == "dryrun_template" and parse_bool(row["dryrun_ready"]):
        return result(row, "dryrun_ready_not_evidence", "M-DRYRUN-1 templates are placeholder-safe and contain no measured trace rows.")
    if artifact_class == "intake_rehearsal":
        if parse_bool(row["intake_preserved"]):
            return result(row, "intake_rehearsed_not_evidence", "M-INTAKE-1 rehearses handoff mechanics with synthetic-safe rows; rehearsal is not current evidence.")
        return result(row, "replay_blocked", "M-INTAKE-1 preservation failed before evidence-pack replay.")

    if not privacy_attestation or not provenance_attestation:
        missing = []
        if not privacy_attestation:
            missing.append("privacy_attestation")
        if not provenance_attestation:
            missing.append("provenance_attestation")
        return result(row, "blocked_invalid_or_unsafe", "M-EVIDENCEPACK-1 blocks missing attestations: " + ",".join(missing))
    if not hash_match:
        return result(row, "replay_blocked", "M-EVIDENCEPACK-1/M-INTAKE-1 hash preservation failed before threshold evaluation.")
    if not threshold_mapping_known:
        return result(row, "replay_blocked", "M-EVIDENCEPACK-1 requires a known M-REOPEN-1 threshold scenario before threshold evaluation.")
    if not package_valid or not replay_valid:
        return result(row, "replay_blocked", "M-EVIDENCEPACK-1 replay contract did not accept the package.")

    if request_count <= 0:
        return result(row, "blocked_invalid_or_unsafe", "M-REOPEN-1 zero-volume special case blocks margin credit before uncertainty evaluation.")
    if accepted_fast_path_count <= 0 or fallback_frequency >= 1.0:
        return result(row, "blocked_invalid_or_unsafe", "M-REOPEN-1 all-fallback special case has no accepted physicalized fast-path credit.")

    actual_source = source_actuality in ACTUAL_SOURCES
    if not admissible_source or not measured_terms or not actual_source:
        if threshold_crossed and uncertainty_durable:
            return result(row, "statistically_durable_nonactual", "M-UNCERTAINTY-1 durable interval is nonactual because source or measured-term gates fail.", evaluated=True)
        if threshold_crossed:
            return result(row, "threshold_crossed_nonactual", "M-REOPEN-1 point threshold crossed, but M-PIPELINE-1/M-EVIDENCEPACK-1 source gates are nonactual.", evaluated=True)
        return result(row, "replay_valid_nonactual", "M-EVIDENCEPACK-1 package is diagnostically valid but lacks actual measured admissible source terms.")

    if not threshold_crossed:
        return result(row, "threshold_evaluable_not_crossed", "M-REOPEN-1 evaluated the measured package and the point threshold was not crossed.", evaluated=True)

    if not uncertainty_durable:
        return result(row, "uncertainty_inconclusive", "M-UNCERTAINTY-1 blocks the point crossing because UCB_alpha is not below zero.", evaluated=True)

    return result(row, "actual_reopen_candidate", "All lifecycle gates pass: actual measured source, measured terms, threshold crossing, and durable uncertainty margin.", evaluated=True)


def write_results(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "case_id",
        "artifact_class",
        "source_actuality",
        "terminal_state",
        "expected_terminal_state",
        "status_matches_expected",
        "owning_gate",
        "reopen_allowed",
        "actual_reopen_candidate",
        "hypothetical_actual_candidate_control",
        "current_artifact",
        "threshold_evaluated",
        "uncertainty_evaluated",
        "rationale",
    ]
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_png(rows: list[dict[str, str]]) -> None:
    width, height = 980, 430
    pixels = bytearray([248, 249, 250] * width * height)

    def set_pixel(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            pixels[idx : idx + 3] = bytes(color)

    def rect(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        for y in range(max(0, y0), min(height, y1)):
            for x in range(max(0, x0), min(width, x1)):
                set_pixel(x, y, color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    set_pixel(x + dx, y + dy, color)

    path = [
        ("Acquire", 45, 55, 155, 115, (191, 219, 254)),
        ("DryRun", 185, 55, 295, 115, (191, 219, 254)),
        ("Intake", 325, 55, 435, 115, (191, 219, 254)),
        ("Replay", 465, 55, 575, 115, (204, 251, 241)),
        ("Thresh", 605, 55, 715, 115, (204, 251, 241)),
        ("Uncert", 745, 55, 855, 115, (204, 251, 241)),
        ("Actual", 875, 55, 960, 115, (187, 247, 208)),
    ]
    terminal_counts = Counter(row["terminal_state"] for row in rows)
    rect(0, 0, width, height, (248, 249, 250))
    for _label, x0, y0, x1, y1, color in path:
        rect(x0, y0, x1, y1, color)
        line(x0, y0, x1, y0, (51, 65, 85))
        line(x1, y0, x1, y1, (51, 65, 85))
        line(x1, y1, x0, y1, (51, 65, 85))
        line(x0, y1, x0, y0, (51, 65, 85))
    for i in range(len(path) - 1):
        line(path[i][3], 85, path[i + 1][1], 85, (51, 65, 85))

    states = [
        ("collection_ready_not_evidence", (59, 130, 246)),
        ("dryrun_ready_not_evidence", (59, 130, 246)),
        ("intake_rehearsed_not_evidence", (59, 130, 246)),
        ("replay_valid_nonactual", (13, 148, 136)),
        ("replay_blocked", (220, 38, 38)),
        ("threshold_evaluable_not_crossed", (13, 148, 136)),
        ("threshold_crossed_nonactual", (245, 158, 11)),
        ("uncertainty_inconclusive", (245, 158, 11)),
        ("statistically_durable_nonactual", (245, 158, 11)),
        ("blocked_invalid_or_unsafe", (220, 38, 38)),
        ("actual_reopen_candidate", (22, 163, 74)),
    ]
    max_count = max(terminal_counts.values() or [1])
    x0 = 60
    y = 170
    for idx, (state, color) in enumerate(states):
        count = terminal_counts.get(state, 0)
        bar_w = 22 + int(180 * count / max_count)
        row_y = y + idx * 20
        rect(x0, row_y, x0 + bar_w, row_y + 12, color)
        rect(x0 + bar_w, row_y, x0 + bar_w + 5, row_y + 12, (51, 65, 85))

    actual = next((row for row in rows if row["terminal_state"] == "actual_reopen_candidate"), None)
    if actual:
        rect(790, 310, 940, 370, (187, 247, 208))
        line(790, 310, 940, 370, (22, 163, 74))
        line(790, 370, 940, 310, (22, 163, 74))

    raw = b"".join(b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3] for y in range(height))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    FLOW_PNG.write_bytes(png)


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def write_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    current_actual_count = sum(
        1
        for row in rows
        if row["terminal_state"] == "actual_reopen_candidate"
        and row["current_artifact"] == "True"
        and row["hypothetical_actual_candidate_control"] != "True"
    )
    hypothetical_count = sum(
        1
        for row in rows
        if row["terminal_state"] == "actual_reopen_candidate"
        and row["hypothetical_actual_candidate_control"] == "True"
    )
    summary = {
        "schema_version": SCHEMA_VERSION,
        "milestone_id": MILESTONE_ID,
        "status": "validated",
        "case_count": len(rows),
        "terminal_state_counts": dict(sorted(Counter(row["terminal_state"] for row in rows).items())),
        "owning_gate_counts": dict(sorted(Counter(row["owning_gate"] for row in rows).items())),
        "actual_reopen_candidate_count": current_actual_count,
        "hypothetical_actual_candidate_control_count": hypothetical_count,
        "current_artifacts_reopen": current_actual_count > 0,
        "status_mismatches": [row["case_id"] for row in rows if row["status_matches_expected"] != "True"],
        "states_defined": LIFECYCLE_STATES,
        "state_owners": STATE_OWNERS,
        "future_reopen_condition": (
            "valid_package && hash_match && schema_compatible && known_threshold_scenario && "
            "valid_trace && admissible_ingestion_path && measured_terms && "
            "production_or_shadow_or_canary_source && provenance_attestation && "
            "privacy_attestation && threshold_crossed && UCB_alpha_delta_below_zero"
        ),
        "figure_caption": FIGURE_CAPTION,
        "interpretation": (
            "The lifecycle composes validated gate outputs without changing semantics: "
            "readiness, dry-run, intake, synthetic, proxy, stale-hash, unknown-threshold, "
            "zero-volume, all-fallback, and noisy point-crossing artifacts terminate in "
            "named non-reopen states. Only the labeled hypothetical measured durable "
            "control exercises the future actual candidate branch."
        ),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def write_report(summary: dict[str, object]) -> None:
    rows = [
        "---",
        "created: 2026-05-13T15:48:00Z",
        "cycle: 5",
        "run_id: run-2026-05-13T015136Z",
        "agent: worker",
        f"milestone: {MILESTONE_ID}",
        "---",
        "",
        "# Evidence-Package Lifecycle State Machine",
        "",
        "M-LIFECYCLE-1 composes the already validated acquisition, dry-run, intake, evidence-pack replay, threshold, and uncertainty gates into a deterministic state machine. It does not replace the upstream validators; it consumes normalized gate outcomes and records which validated milestone owns each terminal state.",
        "",
        "Only measured, privacy-safe, provenance-attested production, shadow-production, or canary-production packages with preserved hashes, known threshold mappings, measured terms, point threshold crossing, and `UCB_alpha(hybrid_total - best_programmable_total) < 0` can reach `actual_reopen_candidate`.",
        "",
        "## States",
        "",
        "| State | Owning gate | Meaning |",
        "|---|---|---|",
    ]
    meanings = {
        "design_screened": "Design was inspected before collection but is not yet collection-ready evidence.",
        "collection_ready_not_evidence": "M-ACQUIRE-1 says a collection design can proceed; no measured package exists.",
        "dryrun_ready_not_evidence": "M-DRYRUN-1 templates are complete but contain placeholders or no measured rows.",
        "intake_rehearsed_not_evidence": "M-INTAKE-1 handoff mechanics are preserved using synthetic-safe rehearsal rows.",
        "replay_valid_nonactual": "Replay can diagnose the package, but source or measured-term gates remain nonactual.",
        "replay_blocked": "Evidence-pack integrity, hash, threshold mapping, or replay contract failed before threshold evaluation.",
        "threshold_evaluable_not_crossed": "Measured package can be evaluated, but M-REOPEN-1 threshold is not crossed.",
        "threshold_crossed_nonactual": "Point threshold crossed, but source or package actuality gates block reopening.",
        "uncertainty_inconclusive": "Point threshold crossed, but M-UNCERTAINTY-1 UCB rule is not durable.",
        "statistically_durable_nonactual": "Uncertainty rule is favorable, but the package is synthetic/proxy/template/rehearsal/nonactual.",
        "actual_reopen_candidate": "All package, source, threshold, and uncertainty gates pass for a measured actual source.",
        "blocked_invalid_or_unsafe": "Privacy/provenance, zero-volume, all-fallback, or other unsafe invalid cases block evaluation.",
    }
    for state in LIFECYCLE_STATES:
        rows.append(f"| `{state}` | `{STATE_OWNERS[state]}` | {meanings[state]} |")
    rows.extend(
        [
            "",
            "## Ordering",
            "",
            "The automaton stops readiness artifacts before replay, stops stale hashes and unknown threshold mappings before threshold evaluation, stops zero-volume and all-fallback cases before margin credit, stops nonactual sources before actual candidacy, and stops noisy point crossings at the uncertainty gate.",
            "",
            f"![{FIGURE_CAPTION}](../data/evidence_package_lifecycle_flow.png)",
            "",
            "## Current Result",
            "",
            f"`actual_reopen_candidate_count` for current/synthetic/template/proxy/rehearsal artifacts is `{summary['actual_reopen_candidate_count']}`.",
            f"`hypothetical_actual_candidate_control_count` is `{summary['hypothetical_actual_candidate_control_count']}`; that row is a labeled positive-control branch, not current evidence.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(rows), encoding="utf-8")


def main() -> None:
    cases = read_cases()
    rows = [classify(row) for row in cases]
    write_results(rows)
    write_png(rows)
    summary = write_summary(rows)
    write_report(summary)
    print("terminal_state_counts:", summary["terminal_state_counts"])
    print("actual_reopen_candidate_count:", summary["actual_reopen_candidate_count"])
    print("hypothetical_actual_candidate_control_count:", summary["hypothetical_actual_candidate_control_count"])


if __name__ == "__main__":
    main()
