---
created: 2026-05-12T13:20:00Z
cycle: 34
run_id: run-2026-05-11T121649Z
agent: worker
milestone: M-UNCERT-1
---

# Statistical uncertainty and confidence propagation

M-UNCERT-1 adds a statistical validity gate after custody, enrollment, timebase, redaction, and gatechain checks. A telemetry row can have a point estimate above a DC-001/DC-002 threshold while still being scientifically unusable if variance is missing, samples are scarce, confidence intervals overlap the threshold, control/treatment windows drift, or repeated intervals are not independent.

The harness models three threshold outcomes in the evaluated fixture path: `robust_pass`, `robust_fail`, and `statistically_indeterminate`. For higher-is-better metrics, a robust pass requires the confidence interval lower bound to exceed the threshold; for lower-is-better metrics, the upper bound must fall below it. A robust fail requires the interval to exclude the threshold on the fail side. Intervals that cross or exactly touch the threshold are indeterminate, not threshold failures and not readiness evidence.

The required metadata covers metric direction, point estimate, threshold, variance, sample count, confidence bounds, noise model, baseline/control/treatment windows, drift budget, sample independence, and bounded p99/tail-latency intervals. Missing or malformed numeric domains fail as `statistical_invalid`; valid but weak evidence fails as `statistically_indeterminate`.

This gate is necessary but not sufficient. Even the confidence-qualified fixture keeps `production_calibrated=false`, `production_ready=false`, and `claim_credit_allowed=false` because it is a fixture, not trusted production_target telemetry on a complete gatechain.
