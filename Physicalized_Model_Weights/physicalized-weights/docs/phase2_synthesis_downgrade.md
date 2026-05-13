---
created: 2026-05-13T07:32:00Z
cycle: 2
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-SYNTH-2
---

# Phase 2 Synthesis Downgrade

Under current calibrated assumptions and equal workload accounting, hybrid physicalized safety/filter wins zero workload scenarios. The stronger programmable accelerator wins nine of ten scenarios, and optimized software wins the zero-invocation control. The prior Phase 1 safety/filter result is therefore preserved only as an architectural and failure-mode study, not as a performance or economic superiority claim.

## Claim Status

Phase 2 status counts: `{"falsified": 1, "open": 0, "preserved": 6, "superseded": 1, "weakened": 1}`. The safety/filter performance/economic claim is `falsified`; the target-ranking superiority language is `superseded`; the bounded hybrid control-plane design is `preserved`.

| claim | Phase 1 status | Phase 2 status | evidence | reopen condition |
|---|---:|---:|---:|---|
| Full dense frontier weights remain anti-targets for permanent fixed hardware. | rejected | preserved | modeled | Measured long-lived dense model deployment with slow update cadence, high utilization, and lower total cost than optimized software and programmable accelerators under identical serving workload. |
| Analog or in-memory broad physicalization remains speculative without device calibration. | speculative | preserved | speculative | Device-calibrated data for drift, conversion overhead, precision, yield, repair, retention, and system integration that beats the same programmable baselines. |
| Safety/filter classifier is a credible target for bounded architecture and failure-mode study. | supported | weakened | inferred | Production traces showing stable high effective fast-path volume, low fallback, monthly-or-slower policy updates, bounded audit and feature costs, and durable utilization. |
| Safety/filter classifier physicalization is a performance or economic winner over strong programmable baselines. | provisionally_supported | falsified | modeled | Identical-workload production measurement where hybrid physicalized safety/filter wins at least one durable high-volume regime after feature extraction, audit logging, fallback, updates, utilization, and programmable accelerator costs are charged. |
| Hybrid architecture with fallback, audit, update, health, drift, and rollback controls remains useful. | supported | preserved | simulated | Reopen only if control-plane invariants fail under richer traces, mutable policy logic enters the fixed block, or fallback/audit paths cannot be made reliable. |
| Programmable accelerator is the strongest current baseline for the tested safety/filter workload. | baseline | preserved | modeled | Measured accelerator implementation performs worse than modeled across the same feature, audit, fallback, update, and utilization conditions while hybrid costs remain bounded. |
| Effective fast-path volume, not raw request volume, controls fixed-substrate viability. | implicit | preserved | modeled | Production traces show raw request volume remains predictive even after fallback, near-threshold, stale-policy, drift, audit-failure, and fail-safe routing are accounted for. |
| Measured production traces are required before promoting a physicalized safety/filter product claim. | recommended | preserved | inferred | The claim is satisfied, not reopened, by production traces with feature extraction cost, audit cost, fallback rate, accelerator energy and latency, update cadence, and utilization. |
| Phase 1 safety/filter target ranking remains a sufficient reason to claim hardware superiority. | supported | superseded | modeled | A new target-ranking pass must include stronger-baseline replay or measured production baselines before superiority language can return. |

## Phase 2 Evidence

- `M-CAL-1`: calibrated hybrid winner share `0.07174603174603175` and decision `preserved_but_weakened`.
- `M-WORKLOAD-1`: workload classifications `{"falsified": 4, "preserved": 1, "speculative": 2, "weakened": 3}`.
- `M-SWBASE-2`: winner counts `{"optimized_software_runtime": 1, "programmable_accelerator": 9}`; hybrid workload wins `0`.
- Formerly preserved high-volume stable moderation case winner: `programmable_accelerator` with decision `accelerator_dominates`.

![Phase 1 and Phase 2 claim statuses, showing which claims were preserved, weakened, falsified, or superseded after calibrated workload and stronger-baseline replay.](../data/phase2_evidence_map.png)

## Reopening Standard

The physicalized safety/filter performance case can reopen only with measured production evidence under identical workload accounting: request volume, accepted fast-path volume, fallback and near-threshold frequency, policy update cadence, audit logging cost, feature extraction cost, utilization, accelerator energy and latency, and operational failure behavior must all be charged to the competing alternatives. A reopened claim must show a durable positive hybrid margin against optimized software and the programmable accelerator, not just a lower isolated dot-product cost.
