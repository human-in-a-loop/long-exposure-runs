---
created: 2026-05-12T10:25:00Z
cycle: 31
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-ROOTINT-1
---

# Production Root Enrollment Preflight

M-ROOTINT-1 adds a pre-gatechain deployment-root enrollment model for collector-root, firmware, topology, schema, counter-source, tenant, and security-context bindings. The model sits before attestation, trust policy, intake, adapter conformance, production ingestion, and gatechain replay: a telemetry bundle is not eligible for those stages unless the enrollment facts are complete, internally consistent, and bound to stable downstream identifiers.

The required stable identifiers are `bundle_id`, `measurement_run_id`, `operator_id`, `collector_id`, and `schema_version`; enrollment also records deployment root lifecycle, key identity, key rotation epoch, collector firmware identity, topology identity/version, counter source, tenant, and security context. Invalid fixtures cover unknown roots, unknown keys, missing or stale firmware identity, duplicate collector IDs under different operators, key rotation gaps, stale root windows, topology ID drift, topology-version drift, schema mismatch, measurement-run mismatch, bundle mismatch, missing counter binding, missing tenant/security binding, replayed enrollment IDs, and fixture attempts to claim a production root.

Enrollment admissibility is only a precondition. The complete fixture reaches `enrollment_admissible=true`, but it keeps `production_target_granted=false`, `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false`; all malformed enrollments fail before downstream gatechain replay.

Future real production telemetry would use this preflight as the operator-facing enrollment audit trail before M-ATTEST-1, M-TRUSTPOL-1, M-INTAKE-1, M-PORT-1, M-PRODTELEM-1, and M-GATECHAIN-1. No fixture enrollment, structurally admissible bundle, attestation record, trust-policy profile, or adapter conformance row can create production claim credit without real `production_target` evidence and the existing gatechain.
