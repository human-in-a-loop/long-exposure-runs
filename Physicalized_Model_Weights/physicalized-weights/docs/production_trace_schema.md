---
created: 2026-05-13T08:42:00Z
cycle: 3
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-TRACE-1
---

# Production Trace Schema

`M-TRACE-1` defines the serving-trace contract required before production telemetry can challenge the Phase 2 downgrade. It does not reopen the claim; it prevents incomplete telemetry, proxy energy, missing baselines, privacy-risk content, and inconsistent policy windows from being counted as reopening evidence.

## Privacy Boundary

Production traces must not contain raw prompts, raw user identifiers, tenant identifiers, API keys, IP addresses, emails, tenant names, or sensitive content. The allowed request identifiers are hashed feature vectors, hashed policy versions, categorical request classes, aggregate timing/energy values, route flags, and non-sensitive environment labels.

## Required Columns

The machine-readable schema is `physicalized-weights/data/production_trace_schema.json`. Required fields cover timestamp ordering, scenario identity, hashed policy version, request class, hashed feature vector, feature length, route decision, fallback/near-threshold/audit/health/drift flags, feature/route/audit/software/accelerator/hybrid latency, accelerator and hybrid energy values plus measurement status, utilization, update/rollback events, and measurement environment.

All latency fields use nanoseconds per request. Energy fields use picojoules per request and must be labeled `measured`, `proxy`, or `missing`; proxy energy is useful for diagnostics but cannot satisfy production-energy evidence requirements.

## Reopen Eligibility

A trace can be classified `valid_reopen_candidate` only when it has nonzero requests, nonzero accepted physicalized fast-path requests, measured accelerator energy, measured hybrid energy, required software and accelerator baseline latency fields, audit fields, passing health/drift gates for accepted fast-path rows, and a consistent policy window. Zero-volume traces, all-fallback traces, traces with proxy-only energy, traces with failed fast-path gates, and traces lacking accelerator baseline measurements are valid controls or diagnostics but cannot reopen the Phase 2 downgrade.

Failure statuses are:

| status | meaning |
|---|---|
| `valid_reopen_candidate` | Schema-valid and contains measured production-quality evidence with nonzero accepted fast-path volume. |
| `valid_but_insufficient` | Schema-valid but cannot reopen because volume, fast-path credit, measured energy, or production environment evidence is insufficient. |
| `invalid_schema` | Required columns are absent or categorical/type checks fail. |
| `invalid_units` | Numeric ranges or physically possible timing/energy constraints fail. |
| `invalid_missing_baseline` | Software or accelerator baseline fields are absent or empty. |
| `invalid_privacy_risk` | Raw prompt, raw user, tenant, API key, IP, email, or content-like columns are present. |
| `invalid_inconsistent_policy` | A scenario contains multiple policy hashes without update/rollback events to explain the transition. |

## Mapping to Prior Models

| trace field or metric | mapped quantity |
|---|---|
| `requests` | `raw_requests_per_day` / workload volume in `M-WORKLOAD-1` after time normalization |
| `accepted_fast_path_requests` | effective fast-path volume and amortization credit |
| `fallback_taken` | fallback frequency |
| `near_threshold` | near-threshold frequency |
| `audit_logged`, `audit_latency_ns` | audit coverage and audit overhead from `M-MEASURE-1` |
| `feature_extract_latency_ns` | feature extraction overhead from `M-MEASURE-1` |
| `update_event`, `rollback_event`, `policy_version_hash` | update cadence and policy consistency |
| `utilization_fraction` | utilization in calibrated and stronger-baseline models |
| `software_baseline_latency_ns`, `accelerator_baseline_latency_ns` | equal-workload baseline path from `M-SWBASE-2` |
| `accelerator_energy_*`, `hybrid_energy_*` | production energy gaps from `M-MEASURE-1` |

![coverage of required production-trace evidence fields, separating valid measured evidence, proxy-only evidence, missing baseline evidence, and privacy/schema failures](../data/production_trace_evidence_coverage.png)
