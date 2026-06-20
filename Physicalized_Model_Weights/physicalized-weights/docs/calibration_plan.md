---
created: 2026-05-13T05:22:00Z
cycle: 2
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-CAL-1
---

# Calibration Plan

## Scope

`M-CAL-1` does not replace the Phase 1 break-even model. It adds a calibrated companion with explicit units, source labels, and uncertainty bounds so the first-arc conclusion can be weakened or preserved without pretending to have process-specific silicon data.

## Phase 1 Placeholders Still Open

The normalized Phase 1 variables that most need calibration are off-chip memory movement, local/on-chip memory movement, int8 compute cost, fixed-substrate amortization, software/runtime memory savings, utilization, control/register overhead, audit logging overhead, fallback dispatch, update/rollback overhead, request volume, and update cadence. The strongest remaining placeholder is not the int8 dot product itself; it is the system overhead around feature extraction, audit, fallback, and software baselines.

## Candidate Data Sources

| Variable family | Current source class | Candidate source or artifact |
|---|---:|---|
| Memory and compute energy scale | sourced | Horowitz ISSCC 2014 energy table for rough 45 nm operation and memory-access scale [7], [8]. |
| Programmable accelerator throughput/power proxy | sourced/inferred | NVIDIA H100 public product page for accelerator-class INT8/FP8 context [9]; use only as a broad bound, not a per-request claim. |
| Benchmark methodology and system-level measurement discipline | sourced | MLPerf Inference documentation for latency/quality/system-scope measurement framing [10]. |
| Python dot product, audit, and branch overheads | local_measured | `physicalized-weights/scripts/local_overhead_probe.py` on this host. |
| Feature extraction and fallback frequency | modeled/speculative | Bounded assumptions until `M-WORKLOAD-1` produces traces. |
| Fixed substrate and integration amortization | modeled/speculative | Retain Phase 1 normalized proxy, now exposed as `nre_equivalent_request_cost`. |

## Unit Conventions

Energy is reported as picojoules (`pJ`) for primitive operations and converted to normalized per-request energy proxies inside the calibrated model. Latency is reported as microseconds (`us`) for local probes. Request volume is `requests/day`, update cadence is `days/update`, and amortization is `requests/update = requests/day * days/update`. A physicalized strategy cannot win at zero request volume when any fixed cost is nonzero.

## Calibration Risks

Public operation-energy tables are process- and era-dependent, so they are used for ratios and order-of-magnitude bounds, not exact modern chip estimates. Vendor accelerator pages are system/product marketing surfaces and do not expose the full serving stack, batching, feature extraction, or audit path. Local Python probes measure interpreter and filesystem behavior on this machine, not hardware truth. Synthetic workload ranges can bias the result if they understate near-threshold fallback, audit logging, or policy churn.

## Decision Rule

The safety/filter conclusion survives `M-CAL-1` if the hybrid safety/filter fast path remains viable across non-optimistic bounds: nonzero request volume, update cadence at least monthly, fallback frequency below 50%, audit/control overhead below the fixed-path savings, and software/runtime savings below the point where programmable baselines dominate. It is weakened if it only wins at quarterly-or-slower updates with low fallback and high reuse. It is reopened or downgraded if zero/low volume, weekly updates, 50% software memory savings, or audit/control/fallback overhead erase the calibrated advantage.
