#!/usr/bin/env python3
# created: 2026-05-12T03:05:00Z
# cycle: 23
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-PRODDEPLOY-1
"""Build an operator-facing production telemetry deployment kit.

The outputs are collection plans and preflight gates only. They are not
measured production telemetry and must not promote any claim to production-ready.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SCHEMA = DATA / "production_dc12_telemetry_schema.csv"
MISSING = DATA / "production_dc12_missing_fields_report.csv"
BACKLOG = DATA / "final_production_experiment_backlog.csv"
OPEN_QUESTIONS = DATA / "handoff_open_questions.csv"
CLAIMS = DATA / "final_claim_readiness_matrix.csv"

COLLECTOR_OUT = DATA / "production_telemetry_collector_spec.csv"
JOIN_OUT = DATA / "production_telemetry_join_contract.csv"
PREFLIGHT_OUT = DATA / "production_telemetry_preflight_checks.csv"
PILOT_OUT = DATA / "production_telemetry_pilot_design.csv"

COMMON_KEYS = "run_id; interval_id; workload_id; object_id; topology_id; tenant_id; security_context_id"
CLOCK = "single monotonic collector clock or bounded clock offset <= 10% of interval_ms"
BOUNDARY = "deployment_blueprint_only_not_measured_evidence"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})
    print(f"wrote {path.relative_to(ROOT)} rows={len(rows)}")


def required_schema_fields() -> set[str]:
    return {r["field_name"] for r in read_csv(SCHEMA) if r["required"] == "true"}


def collector_rows() -> list[dict[str, object]]:
    return [
        {
            "collector_category": "accelerator energy/power counters",
            "collection_surface": "accelerator telemetry API, board power counter, or rack power feed joined to accelerator_id",
            "schema_fields": "joules_measured; power_counter_source; energy_noise_floor_j; accelerator_type; interval_ms; power_interval_start_ms; power_interval_end_ms",
            "derived_fields": "energy_per_byte_j = joules_measured / bytes_moved after byte join",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block DC-001 calibration when joules_measured <= energy_noise_floor_j or counter source is absent",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "missing accelerator or host power source blocks DC-001 and CL-012 production calibration",
            "claim_impact": "CL-004; CL-005; CL-012",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "host energy/power counters",
            "collection_surface": "host BMC/RAPL/PDU counter or operator-approved equivalent joined to host_id and accelerator_id",
            "schema_fields": "joules_measured; power_counter_source; energy_noise_floor_j; interval_ms; power_interval_start_ms; power_interval_end_ms",
            "derived_fields": "host_energy_share_j when accelerator-only counters are incomplete",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block production calibration when host energy contribution noise floor cannot be separated or bounded",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "unbounded host energy makes joules/byte scientifically unusable",
            "claim_impact": "CL-012",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "source/destination tier byte counters",
            "collection_surface": "runtime memory-object registry, DMA/CXL fabric counters, cache/pager counters, or allocator movement logs",
            "schema_fields": "source_tier; destination_tier; bytes_moved; resident_bytes; byte_interval_start_ms; byte_interval_end_ms",
            "derived_fields": "tier_pair = source_tier + '->' + destination_tier",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block joules/byte claims when bytes_moved is zero, missing, or below byte-counter noise floor/instrumentation resolution",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "missing tier-specific bytes blocks DC-001 attribution and Option B/C placement evaluation",
            "claim_impact": "CL-004; CL-005; CL-012",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "CXL or pooled-memory latency p50/p95/p99",
            "collection_surface": "CXL switch/device counters, pooled-memory service histograms, fabric probe, or runtime tail-latency sampler",
            "schema_fields": "latency_p50_us; latency_p95_us; latency_p99_us; hardware_topology_id; topology_scope",
            "derived_fields": "tail_penalty_us = latency_p99_us - latency_p50_us",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block DC-002 calibration when latency histogram noise floor or bucket width hides threshold crossings",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "missing p95/p99 under target topology blocks contention claims",
            "claim_impact": "CL-004; CL-005",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "queue depth and tenant concurrency",
            "collection_surface": "scheduler queue log, admission controller, runtime object-service queue, and tenant placement metadata",
            "schema_fields": "tenant_count; queue_depth; production_target_id; hardware_topology_id",
            "derived_fields": "tenant_id; interval_concurrency_class",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block contention calibration when queue-depth noise floor or sampling interval is coarser than interval_ms",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "unjoined tenant concurrency makes DC-002 threshold replay unusable",
            "claim_impact": "CL-004; CL-005",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "workload/object classification",
            "collection_surface": "agent runtime trace, request router labels, object registry, and trace-v3 object metadata",
            "schema_fields": "workload_class; object_class; measurement_run_id; production_target_id; fixture_id; fixture_class; notes",
            "derived_fields": "workload_id; object_id; interval_id",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "not numeric; block replay when labels are sampled after aggregation and cannot identify per-object bytes or security decisions",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "unlabeled workload/object rows cannot update Option A/B/C evidence",
            "claim_impact": "CL-002; CL-003; CL-004; CL-005; CL-012",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "reuse decision and architecture option",
            "collection_surface": "memory planner decision log and runtime registry action stream",
            "schema_fields": "architecture_option; reuse_decision; calibration_candidate; claimed_reuse_credit; claimed_energy_credit_j; constant_id; threshold_id",
            "derived_fields": "planner_decision_id",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "not numeric; zero claimed credits unless security gates and evidence_label=production_target pass",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "missing reuse decisions prevent energy-credit and control-row checks",
            "claim_impact": "CL-002; CL-003; CL-004; CL-005; CL-012; CONTROL-OPTION-A",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "security/provenance/retention/verifier gates",
            "collection_surface": "authorization service, provenance store, retention policy engine, verifier trace, and security enforcement replay log",
            "schema_fields": "security_allowed; provenance_valid; retention_valid; verifier_valid",
            "derived_fields": "security_context_id; provenance_chain_id; verifier_run_id",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "not numeric; any false or missing gate forces reuse and energy credit to zero",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "missing security/provenance join makes production run scientifically unusable for reuse claims",
            "claim_impact": "CL-002; CL-003; CL-009; SECURITY-GATE-ENERGY-001",
            "deployment_status": "deployment_specific_required",
        },
        {
            "collector_category": "interval alignment and noise-floor metadata",
            "collection_surface": "collection coordinator emitting run manifest, clock sync status, interval map, and counter-resolution table",
            "schema_fields": "measurement_run_id; evidence_label; production_target_id; interval_ms; energy_noise_floor_j; byte_interval_start_ms; byte_interval_end_ms; power_interval_start_ms; power_interval_end_ms",
            "derived_fields": "run_id; interval_id; clock_offset_ms; counter_resolution",
            "required_join_keys": COMMON_KEYS,
            "clock_alignment_requirement": CLOCK,
            "noise_floor_treatment": "block production_calibrated when evidence_label != production_target or noise floors are unknown",
            "evidence_boundary": BOUNDARY,
            "calibration_blocker": "clock mismatch beyond tolerance or missing production_target label blocks all calibration",
            "claim_impact": "all production-calibrated claims",
            "deployment_status": "deployment_specific_required",
        },
    ]


def join_rows() -> list[dict[str, object]]:
    return [
        {
            "join_domain": "run identity",
            "required_key": "run_id",
            "source_fields": "measurement_run_id; production_target_id; evidence_label",
            "joins": "all collector streams in one production run",
            "required_for": "prevents mixing synthetic, host-local, and production_target evidence",
            "failure_consequence": "production_calibrated=false for every row",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "interval alignment",
            "required_key": "interval_id",
            "source_fields": "interval_ms; byte_interval_start_ms; byte_interval_end_ms; power_interval_start_ms; power_interval_end_ms",
            "joins": "power, bytes, latency, queue, and decision windows",
            "required_for": "DC-001 joules/byte and DC-002 latency-tail replay",
            "failure_consequence": "production_calibrated=false; row is unjoinable",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "workload classification",
            "required_key": "workload_id",
            "source_fields": "workload_class; measurement_run_id",
            "joins": "workload thresholds, controls, and experiment backlog rows",
            "required_for": "Option A vs B/C comparison",
            "failure_consequence": "production_calibrated=false; row can be stored for diagnostics but cannot update claims",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "memory object identity",
            "required_key": "object_id",
            "source_fields": "object_class; source_tier; destination_tier; bytes_moved; resident_bytes",
            "joins": "tier movement, object policy, reuse decision, and security gates",
            "required_for": "object-level retained value and tier placement claims",
            "failure_consequence": "production_calibrated=false; Option B/C evidence unusable",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "target topology",
            "required_key": "topology_id",
            "source_fields": "production_target_id; hardware_topology_id; accelerator_type; topology_scope",
            "joins": "power counters, tier bytes, CXL/pool latency, and tenant placement",
            "required_for": "target-specific DC-001/DC-002 calibration",
            "failure_consequence": "production_calibrated=false; run cannot be generalized to target topology",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "tenant concurrency",
            "required_key": "tenant_id",
            "source_fields": "tenant_count; queue_depth; production_target_id",
            "joins": "queue depth, security context, and topology placement",
            "required_for": "multi-tenant contention replay",
            "failure_consequence": "production_calibrated=false; DC-002 blocked and contention rows are diagnostic only",
            "calibration_blocker": "true",
        },
        {
            "join_domain": "security and provenance",
            "required_key": "security_context_id",
            "source_fields": "security_allowed; provenance_valid; retention_valid; verifier_valid",
            "joins": "reuse decision, claimed credits, and object identity",
            "required_for": "zero-credit enforcement and safe reuse accounting",
            "failure_consequence": "zero reuse_credit_granted and zero energy_credit_granted_j",
            "calibration_blocker": "true",
        },
    ]


def preflight_rows() -> list[dict[str, object]]:
    return [
        {
            "check_id": "PF-001",
            "collector_category": "interval alignment and noise-floor metadata",
            "check": "run manifest declares evidence_label=production_target and a stable production_target_id",
            "blocks_calibration": "true",
            "fail_closed_consequence": "production_calibrated=false for all rows",
            "claim_impact": "all",
        },
        {
            "check_id": "PF-002",
            "collector_category": "accelerator energy/power counters",
            "check": "accelerator or bounded host+accelerator joules counter is present above energy_noise_floor_j",
            "blocks_calibration": "true",
            "fail_closed_consequence": "DC-001 and CL-012 blocked",
            "claim_impact": "CL-012",
        },
        {
            "check_id": "PF-003",
            "collector_category": "host energy/power counters",
            "check": "host energy counter is present or host contribution is bounded relative to accelerator counter noise floor",
            "blocks_calibration": "true",
            "fail_closed_consequence": "CL-012 blocked when host energy cannot be separated or bounded",
            "claim_impact": "CL-012",
        },
        {
            "check_id": "PF-004",
            "collector_category": "source/destination tier byte counters",
            "check": "bytes_moved and resident_bytes are emitted by source_tier, destination_tier, object_class, and interval_id",
            "blocks_calibration": "true",
            "fail_closed_consequence": "joules/byte and placement claims are unusable",
            "claim_impact": "CL-004; CL-005; CL-012",
        },
        {
            "check_id": "PF-005",
            "collector_category": "CXL or pooled-memory latency p50/p95/p99",
            "check": "latency p50/p95/p99 histograms are captured under the target hardware_topology_id",
            "blocks_calibration": "true",
            "fail_closed_consequence": "DC-002 contention replay blocked",
            "claim_impact": "CL-004; CL-005",
        },
        {
            "check_id": "PF-006",
            "collector_category": "queue depth and tenant concurrency",
            "check": "tenant_count and queue_depth share interval_id, topology_id, and tenant/security context",
            "blocks_calibration": "true",
            "fail_closed_consequence": "DC-002 blocked; multi-tenant contention rows are diagnostic only",
            "claim_impact": "CL-004; CL-005",
        },
        {
            "check_id": "PF-007",
            "collector_category": "workload/object classification",
            "check": "every counter row joins to workload_class, object_class, workload_id, and object_id before aggregation",
            "blocks_calibration": "true",
            "fail_closed_consequence": "Option A/B/C replay is unjoinable and unusable for calibration",
            "claim_impact": "CL-002; CL-003; CL-004; CL-005; CL-012",
        },
        {
            "check_id": "PF-008",
            "collector_category": "reuse decision and architecture option",
            "check": "architecture_option and reuse_decision are emitted for controls and candidate Option B/C rows",
            "blocks_calibration": "true",
            "fail_closed_consequence": "claimed reuse and energy credits are zero",
            "claim_impact": "CL-002; CL-003; CONTROL-OPTION-A",
        },
        {
            "check_id": "PF-009",
            "collector_category": "security/provenance/retention/verifier gates",
            "check": "security_allowed, provenance_valid, retention_valid, and verifier_valid join to object_id and decision_id",
            "blocks_calibration": "true",
            "fail_closed_consequence": "zero reuse_credit_granted and zero energy_credit_granted_j",
            "claim_impact": "CL-002; CL-003; CL-009; SECURITY-GATE-ENERGY-001",
        },
        {
            "check_id": "PF-010",
            "collector_category": "interval alignment and noise-floor metadata",
            "check": "clock offset and interval drift are within tolerance across power, byte, latency, queue, and security streams",
            "blocks_calibration": "true",
            "fail_closed_consequence": "row is rejected before threshold replay",
            "claim_impact": "all",
        },
    ]


def pilot_rows() -> list[dict[str, object]]:
    return [
        {
            "pilot_step": 1,
            "scope": "run preflight with no claim update",
            "workload_class": "all candidate workloads",
            "architecture_options": "A; B; C",
            "minimum_collectors": "all categories from production_telemetry_collector_spec.csv",
            "minimum_duration": "operator-defined; must cover repeated intervals with stable run_id and topology_id",
            "success_signal": "all PF checks pass and no row is labeled production_ready by the kit",
            "claim_boundary": "blueprint only; no measured evidence in this milestone",
        },
        {
            "pilot_step": 2,
            "scope": "Option A control replay",
            "workload_class": "single-turn chat control or batch/offline control",
            "architecture_options": "A",
            "minimum_collectors": "workload/object labels; reuse decisions; security gates; queue depth; interval manifest",
            "minimum_duration": "enough intervals to show zero non-KV retained value under controls",
            "success_signal": "controls remain Option A with zero positive reuse credit",
            "claim_boundary": "tests negative control only",
        },
        {
            "pilot_step": 3,
            "scope": "Option B object-reuse candidate",
            "workload_class": "RAG or semantic-cache workload",
            "architecture_options": "A; B",
            "minimum_collectors": "power; tier bytes; workload/object labels; reuse decisions; security/provenance gates",
            "minimum_duration": "paired intervals with and without safe reuse under same topology",
            "success_signal": "safe object reuse has joined bytes, joules, and security gates above noise",
            "claim_boundary": "can feed ingestion later; does not endorse Option B here",
        },
        {
            "pilot_step": 4,
            "scope": "Option C trajectory/DAG candidate",
            "workload_class": "code-agent loop or multi-agent branch/merge",
            "architecture_options": "A; B; C",
            "minimum_collectors": "Option B collectors plus CXL/pool latency tails, queue depth, branch/verifier/durable object labels",
            "minimum_duration": "paired branch/merge intervals covering p95/p99 contention tails",
            "success_signal": "trajectory objects join to latency tails, queue depth, and security-valid reuse decisions",
            "claim_boundary": "can test Option C against B later; no production recommendation here",
        },
        {
            "pilot_step": 5,
            "scope": "fail-closed audit replay",
            "workload_class": "mixed control and candidate workloads",
            "architecture_options": "A; B; C",
            "minimum_collectors": "same as steps 2-4 with deliberately withheld shadow rows during preflight only",
            "minimum_duration": "one dry-run window before measurement collection",
            "success_signal": "missing/unjoinable/security-denied rows are rejected or zero-credit",
            "claim_boundary": "blueprint only deployment readiness check",
        },
    ]


def assert_coverage(rows: list[dict[str, object]]) -> None:
    covered: set[str] = set()
    for row in rows:
        covered.update(part.strip() for part in str(row["schema_fields"]).split(";") if part.strip())
    missing = required_schema_fields() - covered
    if missing:
        raise AssertionError(f"required schema fields without collector mapping: {sorted(missing)}")


def main() -> None:
    for path in [SCHEMA, MISSING, BACKLOG, OPEN_QUESTIONS, CLAIMS]:
        if not path.exists():
            raise FileNotFoundError(path)
    collectors = collector_rows()
    assert_coverage(collectors)
    write_csv(
        COLLECTOR_OUT,
        collectors,
        [
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
        ],
    )
    write_csv(
        JOIN_OUT,
        join_rows(),
        ["join_domain", "required_key", "source_fields", "joins", "required_for", "failure_consequence", "calibration_blocker"],
    )
    write_csv(
        PREFLIGHT_OUT,
        preflight_rows(),
        ["check_id", "collector_category", "check", "blocks_calibration", "fail_closed_consequence", "claim_impact"],
    )
    write_csv(
        PILOT_OUT,
        pilot_rows(),
        ["pilot_step", "scope", "workload_class", "architecture_options", "minimum_collectors", "minimum_duration", "success_signal", "claim_boundary"],
    )


if __name__ == "__main__":
    main()
