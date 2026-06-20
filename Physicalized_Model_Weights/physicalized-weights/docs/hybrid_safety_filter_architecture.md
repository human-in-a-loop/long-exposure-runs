---
created: 2026-05-13T02:45:00Z
cycle: 1
run_id: run-2026-05-13T015136Z
agent: worker
milestone: M-ARCH-1
---

# Hybrid Safety-Filter Architecture

## Scope and Evidence Level

This note is an architectural proposal for the top target from `M-TARGET-1`: a fixed or semi-fixed safety/filter classifier submodel with programmable fallback. The claim is conditional, not promotional. Prior modeled evidence says software-optimized and programmable-accelerator baselines win about 63% of sampled break-even cases, so this architecture only deserves prototype work if its fast path stays narrow, auditable, high-reuse, and cheaper than dispatching every request through a general programmable classifier.

## System Context

The physicalized block sits before the main model serving stack. It receives compact request features from the host runtime, produces a class decision plus confidence, and never directly emits user-facing content. The host runtime remains responsible for request parsing, feature construction, policy selection, fallback dispatch, final allow/block/escalate action, and audit persistence.

The credible open control plane is a host-controlled memory-mapped accelerator with a RISC-V-compatible integration path. The minimal deployment is a PCIe/CXL/MMIO device or SoC peripheral controlled by the host runtime. The research path is a RISC-V management core or RISC-V SoC exposing the same register map, because RISC-V is a free/open ISA with public specifications [1], [2] and avoids making the classifier block depend on proprietary control instructions.

## Threat and Failure Model

The architecture assumes the fixed classifier can be wrong, stale, unhealthy, or unavailable. It also assumes the programmable fallback can be unavailable under overload or fault. The main threat is silent acceptance of invalid physicalized output: stale policy, low confidence, drift alarms, failed health checks, rollback mismatch, or missing audit records must not pass through as if the fast path were healthy.

Out of scope for this cycle are device-level side channels, exact model architecture, analog drift physics, silicon process details, and HDL timing closure. Those belong after the interface and fallback invariants survive simulation.

## Component Boundary

The fixed/semi-fixed classifier block owns only deterministic inference over a bounded feature vector and a loaded policy slot. It exposes no tokenization, prompt parsing, main-model logits, dynamic attention state, or policy-authoring logic. All mutable policy control stays in software or a programmable management plane.

Fast-path inputs:

| Field | Width / Type | Owner | Notes |
|---|---:|---|---|
| `request_id` | 64-bit | host | Replay and audit correlation. |
| `feature_addr` | 64-bit DMA address | host | Bounded feature buffer, not raw prompt text. |
| `feature_len` | 16-bit | host | Must match configured model slot shape. |
| `required_policy_version` | 32-bit | host/policy store | Minimum acceptable policy version. |
| `policy_slot` | 8-bit | host/control plane | Selects active classifier image. |
| `decision_threshold` | fixed-point | host/control plane | Conservative threshold; can be raised without reflashing weights. |

Fast-path outputs:

| Field | Width / Type | Owner | Notes |
|---|---:|---|---|
| `decision` | enum | classifier | `allow`, `block`, `escalate`, or `invalid`. |
| `confidence_q15` | 16-bit | classifier | `0` means no usable confidence; `32767` means maximum modeled confidence. |
| `observed_policy_version` | 32-bit | classifier/control | Version actually used for inference. |
| `health_status` | enum | control plane | `healthy`, `degraded`, `failed`. |
| `drift_status` | enum | control plane | `normal`, `alarm`. |
| `fallback_reason` | enum | host/control plane | Empty only when fast path is valid and accepted. |
| `audit_digest` | 128-bit | host/control plane | Hash or digest over request id, versions, decision, confidence, and route. |

## Register Map

The register map is intentionally small enough for a host MMIO driver, a RISC-V memory-mapped peripheral, or a later custom instruction shim.

| Offset | Name | Access | Purpose |
|---:|---|---|---|
| `0x00` | `DEVICE_ID` | RO | Stable implementation identifier. |
| `0x04` | `ABI_VERSION` | RO | Register-map compatibility version. |
| `0x08` | `STATUS` | RO | Ready, busy, error, health, drift, audit-backpressure bits. |
| `0x0C` | `CONTROL` | RW | Start, clear, force_fallback, fail_closed_enable. |
| `0x10` | `REQUEST_ID_LO` | RW | Lower 32 bits of request id. |
| `0x14` | `REQUEST_ID_HI` | RW | Upper 32 bits of request id. |
| `0x18` | `FEATURE_ADDR_LO` | RW | Lower feature-buffer address. |
| `0x1C` | `FEATURE_ADDR_HI` | RW | Upper feature-buffer address. |
| `0x20` | `FEATURE_LEN` | RW | Feature vector length. |
| `0x24` | `POLICY_SLOT` | RW | Active slot selector. |
| `0x28` | `REQUIRED_POLICY_VERSION` | RW | Minimum version required by host policy. |
| `0x2C` | `ACTIVE_POLICY_VERSION` | RO | Version bound to the selected classifier slot. |
| `0x30` | `THRESHOLD_Q15` | RW | Runtime decision threshold. |
| `0x34` | `CONFIDENCE_Q15` | RO | Classifier confidence output. |
| `0x38` | `DECISION` | RO | Encoded classifier decision. |
| `0x3C` | `FALLBACK_REASON` | RO | Reason fast path was rejected. |
| `0x40` | `AUDIT_RING_ADDR_LO` | RW | Lower audit ring address. |
| `0x44` | `AUDIT_RING_ADDR_HI` | RW | Upper audit ring address. |
| `0x48` | `AUDIT_RING_SIZE` | RW | Audit ring capacity. |
| `0x4C` | `AUDIT_WRITE_INDEX` | RO | Monotonic audit write index. |
| `0x50` | `ROLLBACK_SLOT` | RW | Known-good fallback classifier slot. |

## Update, Rollback, and Versioning

Weights, thresholds, and policy tables are updated as signed images into inactive slots. Activation requires signature verification, shape compatibility checks, a monotonic policy version, a health self-test, and host acknowledgement. Threshold-only updates are permitted for conservative tightening, but relaxing a threshold requires the same signed policy path as a weight update.

Rollback is slot-based. The host can point `ROLLBACK_SLOT` to the previous validated image and force fallback while the replacement is quarantined. A stale or unknown policy version never silently uses the fast path; it either routes to programmable fallback or enters fail-safe if fallback is unavailable.

## Decision and Fallback Policy

The host accepts the physicalized decision only if all of the following are true:

- Classifier health is `healthy`.
- Drift status is `normal`.
- Observed policy version is greater than or equal to the required policy version.
- Confidence is greater than or equal to the configured threshold.
- Audit logging succeeds or the deployment explicitly permits degraded audit mode.
- The host has not forced fallback for rollout, A/B testing, incident response, or baseline measurement.

Otherwise the request is routed to a software or programmable-accelerator classifier. If both the fast path is invalid and fallback is unavailable, the system enters the documented fail-safe state: `fail_closed_block` for enforce-mode deployments and `fail_safe_escalate` for monitor-mode deployments. The simulator in `physicalized-weights/scripts/fallback_policy_sim.py` models these cases.

## Invariants

| Invariant | Required Behavior |
|---|---|
| Low confidence | Confidence below threshold, including confidence `0`, cannot produce an accepted fast-path decision. |
| Stale version | `observed_policy_version < required_policy_version` routes away from the physicalized output. |
| Failed health | Failed or degraded health invalidates the classifier output. |
| Drift alarm | Drift alarm routes to fallback even if confidence is high. |
| Fallback unavailable | If classifier output is invalid and fallback is unavailable, enter fail-safe rather than accept stale/low-confidence output. |
| Audit fields | Every decision emits request id, route, policy versions, confidence, health, drift, action, and reason fields. |
| Deterministic replay | Given the audit record, feature digest, classifier slot, policy version, and threshold, the decision can be replayed against the same image. |
| Stale-policy behavior | Stale fast-path output is never treated as an approximate answer; it is invalid. |
| Baseline measurement | The host can force fallback to compare fast-path benefit against software and programmable-accelerator baselines. |

Fail-closed is required for enforce-mode safety filters when no valid classifier or fallback exists. Fail-open is only acceptable in monitor-only deployments where the safety filter is advisory and the main serving path has independent controls; that mode must be explicit in policy and audit records.

## Baselines Before Crediting Physicalization

The architecture competes against:

1. A software-optimized classifier using batching, feature caching, quantization, and host/runtime scheduling.
2. A programmable accelerator classifier using existing NPU/GPU/vector resources.
3. The hybrid physicalized classifier with host or RISC-V-compatible control, fallback, versioning, and audit overhead.

The hybrid should be demoted if fallback rate is high, audit writes dominate latency or energy, policy churn is weekly, or software/runtime savings approach the 50% scenario already modeled in `M-MODEL-1`. The hybrid should be promoted only if profiling shows high request volume, low update cadence, low fallback rate, bounded feature extraction cost, and lower per-request movement than the optimized software and programmable-accelerator baselines.

## Prototype Roadmap for M-PROTO-1

The next prototype should not start with a full ML model. It should implement a tiny fixed-weight linear classifier or lookup-plus-dot-product model with the register map above, then run the fallback policy around it.

Recommended `M-PROTO-1` sequence:

1. Extend the policy simulator with request-volume and fallback-rate sweeps.
2. Implement a small fixed-weight classifier in Python and compare against a software fallback path using identical features.
3. If the boundary remains narrow, emit a tiny Verilog register/FSM sketch for the control path and check it with Verilator/Yosys.
4. Keep the software and programmable-accelerator baselines live; do not claim a hardware win unless measured fast-path utilization and overhead beat them under the same workload assumptions.

## Falsification Before HDL

Reject or defer HDL if any of these occur:

- Safety policy updates are weekly or workload-specific enough that slot updates dominate operations.
- Low confidence, stale version, drift, health failure, or audit failure can bypass fallback in simulation.
- The control plane grows into a general programmable classifier, erasing the distinction from a programmable accelerator.
- Feature extraction or audit logging dominates the cost saved by avoiding programmable inference.
- Request volume is too low for amortization, including the `request_volume = 0` special case from the brief.
- Under 50% software/runtime memory-movement savings, the fast path has no remaining plausible advantage.

The architecture is therefore a conditional research target: useful if the safety/filter classifier is stable, isolated, high-volume, and auditable; unattractive if it becomes a brittle policy trap or a programmable accelerator with worse updateability.
