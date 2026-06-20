---
created: 2026-05-13T14:06:00Z
cycle: 4
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-INTAKE-1
---

# Evidence-pack intake rehearsal

M-INTAKE-1 checks the boundary between the operator dry-run layer and the evidence-pack replay layer. The script regenerates the M-DRYRUN-1 templates, fills synthetic-safe package traces under `physicalized-weights/data/intake_rehearsal_packages/`, computes trace SHA-256 values, writes replay-compatible manifests, checks that handoff fields are preserved, and only then calls the M-EVIDENCEPACK-1 replay evaluator.

The rehearsal copies no validated M-EVIDENCEPACK-1 fixtures and does not overwrite them. Each generated package has a package-local `trace.csv` and `manifest.json`; the manifest binds `trace_file`, `trace_sha256`, `ingestion_path_id`, `evidence_source_type`, `measurement_status`, `provenance_attestation`, `threshold_scenario_id`, `pipeline_expected_status`, and `privacy_attestation`.

All rows are synthetic-safe stand-ins. Shadow and canary cases exercise the valid handoff into replay without crossing the reopen threshold, while a synthetic counterfactual crosses the arithmetic branch but remains non-actual because source and ingestion eligibility still fail the Phase 3 gate. Mutation cases are blocked at intake before replay when a trace hash goes stale, manifest source changes, threshold mapping changes, provenance attestation changes, or raw content is added after dry-run.

![Intake rehearsal from operator dry-run templates to evidence-pack replay, showing preserved hashes/manifests for valid synthetic-safe packages and blocked handoff mutations before any current artifact can reopen.](../data/evidence_pack_intake_rehearsal_flow.png)

## Results

- `shadow_synthetic_filled_non_crossing`: dry-run `ready_for_collection_not_evidence`, intake `intake_passed`, replay `threshold_evaluable_not_crossed`, final `threshold_evaluable_not_crossed`, blockers `none`.
- `canary_synthetic_filled_non_crossing`: dry-run `ready_for_collection_not_evidence`, intake `intake_passed`, replay `threshold_evaluable_not_crossed`, final `threshold_evaluable_not_crossed`, blockers `none`.
- `synthetic_counterfactual_crossing_non_actual`: dry-run `schema_blocked`, intake `intake_passed`, replay `synthetic_counterfactual_crossed`, final `synthetic_counterfactual_crossed`, blockers `none`.
- `stale_hash_after_handoff`: dry-run `ready_for_collection_not_evidence`, intake `intake_hash_blocked`, replay `not_run`, final `intake_blocked`, blockers `hash_preserved=false:trace_sha256_mismatch_after_handoff`.
- `trace_file_alias_after_handoff`: dry-run `ready_for_collection_not_evidence`, intake `intake_manifest_blocked`, replay `not_run`, final `intake_blocked`, blockers `manifest_preserved=false:trace_file`.
- `manifest_trace_source_mismatch`: dry-run `ready_for_collection_not_evidence`, intake `intake_manifest_blocked`, replay `not_run`, final `intake_blocked`, blockers `manifest_preserved=false:evidence_source_type|handoff_manifest_trace_mismatch:evidence_source_type`.
- `threshold_mapping_changed_after_dryrun`: dry-run `ready_for_collection_not_evidence`, intake `intake_threshold_blocked`, replay `not_run`, final `intake_blocked`, blockers `manifest_preserved=false:threshold_scenario_id|handoff_manifest_trace_mismatch:threshold_scenario_id`.
- `attestation_changed_after_hash`: dry-run `ready_for_collection_not_evidence`, intake `intake_attestation_blocked`, replay `not_run`, final `intake_blocked`, blockers `manifest_preserved=false:provenance_attestation|handoff_manifest_trace_mismatch:provenance_attestation`.
- `raw_content_added_after_dryrun`: dry-run `ready_for_collection_not_evidence`, intake `intake_privacy_blocked`, replay `not_run`, final `intake_blocked`, blockers `hash_preserved=false:trace_sha256_mismatch_after_handoff|post_dryrun_privacy_column:content`.

## Interpretation

The summary reports `actual_reopen_candidate_count = 0`. This rules in the handoff mechanism for synthetic-safe rehearsal packages and rules out the failure mode where intake silently rewrites manifests, ignores stale hashes, or converts dry-run/template data into actual reopen evidence.
