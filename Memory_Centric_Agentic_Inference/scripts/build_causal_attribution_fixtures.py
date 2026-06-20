#!/usr/bin/env python3
# created: 2026-05-12T14:00:00Z
# cycle: 35
# run_id: run-2026-05-11T121649Z
# agent: worker
# milestone: M-CAUSAL-1
"""Build causal-attribution fixtures for control-arm validity checks."""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

INPUTS = [
    DATA / "uncertainty_evaluation_results.csv",
    DATA / "uncertainty_threshold_boundary.csv",
    DATA / "production_dc12_threshold_replay.csv",
    DATA / "production_dc12_telemetry_schema.csv",
    DATA / "final_claim_readiness_matrix.csv",
    DATA / "trace_workload_summary.csv",
    DATA / "architecture_policy_matrix.csv",
    DATA / "synthesis_architecture_decision_matrix.csv",
]

OUT_SCHEMA = DATA / "causal_attribution_schema.csv"
OUT_VALID = DATA / "causal_valid_fixture.csv"
OUT_INVALID = DATA / "causal_invalid_fixtures.csv"
OUT_GRID = DATA / "causal_confounder_sensitivity_grid.csv"
OUT_COVARIATES = DATA / "causal_required_covariates.csv"

FIELDS = [
    "case_id",
    "case_type",
    "source_uncertainty_case_id",
    "constant_id",
    "threshold_id",
    "architecture_option",
    "control_policy",
    "treatment_policy",
    "statistical_threshold_status",
    "point_estimate",
    "threshold_value",
    "control_arm_present",
    "pre_treatment_covariates_declared",
    "comparison_method",
    "workload_mix_smd",
    "object_size_smd",
    "tenant_concurrency_smd",
    "topology_match",
    "model_version_match",
    "cache_warmness_smd",
    "security_deny_rate_delta",
    "time_window_drift_fraction",
    "scheduler_load_smd",
    "positivity_overlap_fraction",
    "post_treatment_covariate_used",
    "randomization_unit",
    "blocking_keys",
    "gatechain_eligible",
    "measurement_valid",
    "evidence_label",
    "expected_causal_status",
    "expected_blocked_reason",
    "notes",
]

SCHEMA_ROWS = [
    ("control_arm_present", "true", "true only when an Option A control arm/window exists for the same claim and interval family"),
    ("pre_treatment_covariates_declared", "true", "true only when workload, tenant, topology, model, cache, security, and scheduler covariates are declared before treatment"),
    ("comparison_method", "true", "randomized, blocked, matched, or diff_in_diff comparison design"),
    ("workload_mix_smd", "true", "standardized mean difference for workload class mix; <=0.10 required"),
    ("object_size_smd", "true", "standardized mean difference for object size distribution; <=0.10 required"),
    ("tenant_concurrency_smd", "true", "standardized mean difference for tenant concurrency; <=0.10 required"),
    ("topology_match", "true", "true only when accelerator, host, CXL/pooled-memory, and network topology buckets match"),
    ("model_version_match", "true", "true only when model, tokenizer, runtime, and serving policy versions match"),
    ("cache_warmness_smd", "true", "standardized mean difference for cache warmness/prefix residency; <=0.10 required"),
    ("security_deny_rate_delta", "true", "absolute treatment-control security deny-rate delta; <=0.02 required"),
    ("time_window_drift_fraction", "true", "time-of-day and load drift fraction across control/treatment windows; <=0.10 required"),
    ("scheduler_load_smd", "true", "standardized mean difference for queue/scheduler load; <=0.10 required"),
    ("positivity_overlap_fraction", "true", "fraction of covariate space represented in both arms; >=0.80 required"),
    ("post_treatment_covariate_used", "true", "must be false; post-treatment adjustment can mask causal mechanisms"),
    ("randomization_unit", "true", "tenant, run, object, shard, or blocked time window unit used for assignment"),
    ("blocking_keys", "true", "pre-treatment keys used for blocking or matching"),
]

COVARIATES = [
    ("workload_mix", "block_or_match", "agent workload class, tool-use rate, RAG/code/verifier mix", "pre_treatment", "workload_mix_smd<=0.10"),
    ("object_size_distribution", "match", "prompt/KV/tool-output/trajectory object bytes", "pre_treatment", "object_size_smd<=0.10"),
    ("tenant_concurrency", "block_or_randomize", "active tenants and concurrent trajectories", "pre_treatment", "tenant_concurrency_smd<=0.10"),
    ("hardware_topology", "block", "GPU/HBM, host DRAM, CXL or pooled-memory bucket, network locality", "pre_treatment", "topology_match=true"),
    ("model_version", "block", "model, tokenizer, runtime, quantization, and serving policy version", "pre_treatment", "model_version_match=true"),
    ("cache_warmness", "block_or_measure_before_treatment", "prefix/object residency and warm-cache exposure before intervention", "pre_treatment", "cache_warmness_smd<=0.10"),
    ("security_deny_rate", "block_or_stratify", "authorization/provenance/retention deny-rate before treatment", "pre_treatment", "security_deny_rate_delta<=0.02"),
    ("time_of_day_load", "blocked_time_window_or_diff_in_diff", "diurnal load, batch interference, and maintenance windows", "pre_treatment", "time_window_drift_fraction<=0.10"),
    ("scheduler_load", "block_or_match", "queue depth, admission pressure, and preemption rate", "pre_treatment", "scheduler_load_smd<=0.10"),
    ("post_treatment_cache_hits", "forbidden_adjustment", "cache hits after assigning memory-centric treatment", "post_treatment", "post_treatment_covariate_used=false"),
]

BASE = {
    "case_id": "valid-causally-admissible-fixture",
    "case_type": "valid_fixture",
    "source_uncertainty_case_id": "valid-confidence-qualified-fixture",
    "constant_id": "DC-002",
    "threshold_id": "DC002-RAG-C-p99",
    "architecture_option": "Option C",
    "control_policy": "Option A",
    "treatment_policy": "Option C",
    "statistical_threshold_status": "robust_pass",
    "point_estimate": "7.4",
    "threshold_value": "5.5",
    "control_arm_present": "true",
    "pre_treatment_covariates_declared": "true",
    "comparison_method": "blocked_matched",
    "workload_mix_smd": "0.03",
    "object_size_smd": "0.04",
    "tenant_concurrency_smd": "0.05",
    "topology_match": "true",
    "model_version_match": "true",
    "cache_warmness_smd": "0.04",
    "security_deny_rate_delta": "0.01",
    "time_window_drift_fraction": "0.03",
    "scheduler_load_smd": "0.05",
    "positivity_overlap_fraction": "0.92",
    "post_treatment_covariate_used": "false",
    "randomization_unit": "blocked_trajectory_window",
    "blocking_keys": "workload_class,model_version,topology_bucket,tenant_concurrency_bucket,time_window",
    "gatechain_eligible": "false",
    "measurement_valid": "true",
    "evidence_label": "causal_fixture",
    "expected_causal_status": "causally_admissible",
    "expected_blocked_reason": "",
    "notes": "robust statistical effect with declared pre-treatment balance and overlap; fixture remains non-production",
}

ROBUST_FAIL = {
    **BASE,
    "case_id": "valid-causally-admissible-robust-fail-fixture",
    "source_uncertainty_case_id": "valid-confidence-qualified-fail-fixture",
    "statistical_threshold_status": "robust_fail",
    "point_estimate": "3.9",
    "expected_causal_status": "causally_admissible",
    "notes": "causal design can be admissible even when the robust threshold result does not support the treatment",
}

INVALIDS = [
    ("invalid-missing-option-a-control", {"control_arm_present": "false"}, "causally_unidentified", "missing_option_a_control"),
    ("invalid-workload-mix-mismatch", {"workload_mix_smd": "0.32"}, "causally_confounded", "workload_mix_mismatch"),
    ("invalid-model-version-mismatch", {"model_version_match": "false"}, "causally_confounded", "model_version_mismatch"),
    ("invalid-topology-mismatch", {"topology_match": "false"}, "causally_confounded", "topology_mismatch"),
    ("invalid-tenant-concurrency-imbalance", {"tenant_concurrency_smd": "0.27"}, "causally_confounded", "tenant_concurrency_imbalance"),
    ("invalid-object-size-distribution-shift", {"object_size_smd": "0.24"}, "causally_confounded", "object_size_distribution_shift"),
    ("invalid-cache-warmness-imbalance", {"cache_warmness_smd": "0.29"}, "causally_confounded", "cache_warmness_imbalance"),
    ("invalid-security-deny-rate-shift", {"security_deny_rate_delta": "0.08"}, "causally_confounded", "security_deny_rate_shift"),
    ("invalid-time-window-drift", {"time_window_drift_fraction": "0.21"}, "causally_confounded", "time_window_drift"),
    ("invalid-post-treatment-covariate-leakage", {"post_treatment_covariate_used": "true"}, "causally_unidentified", "post_treatment_covariate_leakage"),
    ("invalid-insufficient-overlap-positivity", {"positivity_overlap_fraction": "0.38"}, "causally_unidentified", "insufficient_overlap_positivity"),
    ("invalid-missing-covariate-contract", {"pre_treatment_covariates_declared": "false"}, "causally_unidentified", "missing_pre_treatment_covariate_contract"),
    ("invalid-scheduler-load-imbalance", {"scheduler_load_smd": "0.26"}, "causally_confounded", "scheduler_load_imbalance"),
    ("invalid-fixture-attempted-production-calibration", {"evidence_label": "production_target"}, "causally_unidentified", "fixture_attempted_production_calibration"),
]


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


def require_inputs() -> None:
    for path in INPUTS:
        read_csv(path)


def invalid_rows() -> list[dict[str, object]]:
    rows = []
    for case_id, overrides, status, reason in INVALIDS:
        row = dict(BASE)
        row.update(overrides)
        row.update(
            {
                "case_id": case_id,
                "case_type": "invalid_fixture",
                "expected_causal_status": status,
                "expected_blocked_reason": reason,
                "notes": "robust statistical threshold pass must fail closed when causal controls or pre-treatment balance are invalid",
            }
        )
        rows.append(row)
    return rows


def grid_rows() -> list[dict[str, object]]:
    rows = []
    for imbalance, overlap, baseline_effect in product([0.0, 0.05, 0.15, 0.30], [0.35, 0.65, 0.85, 0.95], [4.5, 6.0, 7.4]):
        confounder_bias = 5.0 * imbalance + (0.80 - overlap if overlap < 0.80 else 0.0) * 2.0
        estimated_effect = baseline_effect + confounder_bias
        if overlap < 0.80:
            status = "causally_unidentified"
        elif imbalance > 0.10:
            status = "causally_confounded"
        else:
            status = "causally_admissible"
        rows.append(
            {
                "grid_id": f"imbalance-{imbalance}-overlap-{overlap}-effect-{baseline_effect}",
                "max_covariate_imbalance_smd": f"{imbalance:.2f}",
                "positivity_overlap_fraction": f"{overlap:.2f}",
                "baseline_effect_ms": f"{baseline_effect:.2f}",
                "estimated_effect_ms": f"{estimated_effect:.2f}",
                "threshold_value": "5.50",
                "apparent_threshold_passed": str(estimated_effect > 5.5).lower(),
                "causal_status": status,
            }
        )
    return rows


def main() -> None:
    require_inputs()
    schema = [{"field_name": field, "required": required, "purpose": purpose} for field, required, purpose in SCHEMA_ROWS]
    covariates = [
        {"covariate": name, "required_handling": handling, "measurement": measurement, "temporal_role": role, "acceptance_rule": rule}
        for name, handling, measurement, role, rule in COVARIATES
    ]
    write_csv(OUT_SCHEMA, schema, ["field_name", "required", "purpose"])
    write_csv(OUT_VALID, [BASE, ROBUST_FAIL], FIELDS)
    write_csv(OUT_INVALID, invalid_rows(), FIELDS)
    write_csv(OUT_GRID, grid_rows(), ["grid_id", "max_covariate_imbalance_smd", "positivity_overlap_fraction", "baseline_effect_ms", "estimated_effect_ms", "threshold_value", "apparent_threshold_passed", "causal_status"])
    write_csv(OUT_COVARIATES, covariates, ["covariate", "required_handling", "measurement", "temporal_role", "acceptance_rule"])


if __name__ == "__main__":
    main()
