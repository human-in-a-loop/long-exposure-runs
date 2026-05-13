---
created: 2026-05-13T13:18:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-DRYRUN-1
---

# Operator evidence-pack template

M-DRYRUN-1 gives an operator a package skeleton to check before measured shadow or canary collection. It sits before M-EVIDENCEPACK-1 and rejects assembly mistakes early; it does not weaken replay requirements and it cannot reopen the Phase 2 downgrade.

Required manifest fields are: `pack_id`, `schema_version`, `created_at_utc`, `trace_schema_version`, `trace_file`, `trace_sha256`, `ingestion_path_id`, `evidence_source_type`, `measurement_status`, `provenance_attestation`, `threshold_scenario_id`, `pipeline_expected_status`, `privacy_attestation`. The canonical manifest template is `physicalized-weights/data/operator_evidence_pack_manifest_template.json`.

Required trace columns are: `timestamp_ns`, `scenario_id`, `policy_version_hash`, `request_class`, `feature_vector_hash`, `feature_length`, `route_decision`, `fallback_taken`, `near_threshold`, `audit_logged`, `health_gate_passed`, `drift_gate_passed`, `feature_extract_latency_ns`, `route_latency_ns`, `audit_latency_ns`, `software_baseline_latency_ns`, `accelerator_baseline_latency_ns`, `hybrid_fast_path_latency_ns`, `accelerator_energy_proxy_or_measured_pj`, `accelerator_energy_status`, `hybrid_energy_proxy_or_measured_pj`, `hybrid_energy_status`, `utilization_fraction`, `update_event`, `rollback_event`, `measurement_environment`. The trace template is header-only and intentionally contains no raw content fields.

Privacy exclusions are `prompt`, `raw_prompt`, `raw_text`, `user_id`, `raw_user_id`, `tenant_id`, `tenant_name`, `api_key`, `email`, `ip_address`, and `content`. Any template that introduces one of those columns is blocked before collection.

Allowed threshold scenario IDs are: `high_volume_stable_moderation`, `bursty_consumer_traffic`, `low_volume_enterprise_deployment`, `high_near_threshold_adversarial`, `frequent_policy_update_regime`, `audit_heavy_regulated_deployment`, `fallback_degraded_outage_regime`, `multi_tenant_underutilized_deployment`, `zero_invocation_control`, `fallback_all_control`. The operator must select one known scenario before collection and must not leave it ambiguous.

Allowed dry-run ingestion paths are: `shadow_production_dual_run`, `canary_ab_dual_instrumented`. Other M-INGEST-1 paths remain diagnostic or inadmissible at this layer and cannot be marked ready for measured collection.

Generate the trace hash after final trace export:

```bash
python3 - <<'PY'
import hashlib
from pathlib import Path
path = Path("physicalized-weights/data/operator_trace_template.csv")
print(hashlib.sha256(path.read_bytes()).hexdigest())
PY
```

The provenance attestation template is `physicalized-weights/data/operator_provenance_attestation_template.md`. Replace every placeholder with source, privacy, measurement, policy-window, counterfactual-baseline, and hash-provenance statements before measured collection.

Expected dry-run statuses are `ready_for_collection_not_evidence`, `template_incomplete`, `privacy_blocked`, `integrity_blocked`, `provenance_blocked`, `schema_blocked`, and `threshold_mapping_blocked`. A ready dry-run remains non-evidence because it has no measured trace rows, no measured margin, and no threshold crossing.

![Dry-run acceptance outcomes for operator evidence-pack templates, showing which package-preparation errors block collection readiness while all placeholder packages remain non-evidence.](../data/evidence_pack_dryrun_status_matrix.png)
