---
created: 2026-05-12T14:20:00Z
cycle: 35
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-CAUSAL-1
---

# Causal Attribution and Control-Arm Validity

M-CAUSAL-1 adds a causal-validity check after custody, enrollment, timing, redaction, gatechain, and statistical uncertainty checks. The causal graph treats the memory-centric intervention, usually Option B or Option C placement/reuse, as the treatment; latency, byte-movement, energy, or planner-value deltas as outcomes; and workload mix, object size, tenant concurrency, hardware topology, model/runtime version, cache warmness, security-deny rate, time-window load, and scheduler pressure as pre-treatment confounders.

The minimum control-arm contract is an Option A control with declared pre-treatment covariates, matching or blocking on workload/model/topology/time windows, standardized mean differences no greater than 0.10 for workload/object/tenant/cache/scheduler fields, security-deny-rate delta no greater than 0.02, time drift no greater than 0.10, and positivity overlap at least 0.80. Post-treatment cache hits, reuse counts, or scheduler outcomes cannot be used as adjustment justifications because they may be mechanisms of the treatment rather than independent controls.

The evaluator separates robust statistical effects into `causally_admissible`, `causally_confounded`, and `causally_unidentified`. A robust threshold pass with workload, topology, tenant, object-size, cache-warmness, scheduler, security, or time-window imbalance is classified as confounded; missing controls, missing covariate contracts, positivity failure, and post-treatment adjustment are unidentified.

This remains a scientific precondition only. Balanced fixture rows may be causally admissible, but all M-CAUSAL-1 rows keep `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false` because the artifacts are fixtures rather than trusted production-target telemetry.
