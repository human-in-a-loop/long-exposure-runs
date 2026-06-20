---
created: 2026-05-16T16:42:00Z
cycle: 31
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M20-long-support-trace-variance-requirement
---

# Long-Support Trace Variance Requirement

## Purpose

M19 closed the logarithmic-support smoothing escape route for shrinking local windows: a bulk window `Delta=n^{-d}` requires polynomial geometric support `R=n^eta` with `eta>=d`, and an edge window requires `eta>=d/2`. M20 keeps that long support and asks only what random-cover variance saving would be needed for the M17 Chebyshev criterion.

This is a feasibility budget, not a theorem about Kim--Tao's trace expansion.

## Exponent Template

For the smoothed statistic from M17,

```text
Z_n(phi; Lambda, Delta)
  = sum_j phi((lambda_j(X_n)-Lambda)/Delta)
    - main_n(phi; Lambda, Delta),
```

relative local control follows from

```text
sqrt(Var Z_n) << mean_n.
```

In the bulk, `mean_n ~ n Delta = n^(1-d)`. At the edge,

```text
mean_n ~ n Delta^(3/2) = n^(1-3d/2).
```

Model a future long-support random-cover trace theorem as

```text
Var Z_n <= n^(1 + L(eta) - beta(eta)).
```

Here `L(eta)` records support, polynomial degree, and Markov/interpolation loss, while `beta(eta)` is the new random-cover saving beyond the baseline `n` scale.

## Bulk Requirement

The bulk Chebyshev condition is

```text
1 + L(eta) - beta(eta) < 2 - 2d,
```

equivalently

```text
beta(eta) > L(eta) + 2d - 1.
```

M19 also requires

```text
eta >= d.
```

Endpoint subtraction from M16 is beaten only when

```text
d > alpha_W.
```

## Edge Requirement

At the edge the mean exponent is `1-3d/2`, hence

```text
1 + L(eta) - beta(eta) < 2 - 3d,
```

or

```text
beta(eta) > L(eta) + 3d - 1.
```

M19 requires

```text
eta >= d/2.
```

The M16 edge endpoint threshold is `d>2 alpha_W/3` at exponent level.

## Kim--Tao Support Map

M18 records the compact-support side of Kim--Tao's test-function architecture:

```text
supp((h o f_Lambda0)^vee) <= c0 Lambda0^(-1/2) q.
```

For fixed `Lambda0`, polynomial support `R=n^eta` therefore corresponds to

```text
q = n^eta
```

at exponent level. The factor `Lambda0^(-1/2)` changes constants, not the `n`-power. If `Lambda0` grows with `n`, this ledger would need a separate high-energy scaling model; M20 does not use one.

## Trace and Pre-Trace Loss Budgets

The existing Kim--Tao loss proxies from M18 give

```text
L_trace(eta) = 2 kappa eta,
L_pretrace(eta) = 4 kappa eta.
```

At minimal resolving support this becomes:

| regime | support | trace required beta | pre-trace required beta |
|---|---:|---:|---:|
| bulk/high energy | `eta=d` | `(2 kappa + 2)d - 1` | `(4 kappa + 2)d - 1` |
| edge | `eta=d/2` | `(kappa + 3)d - 1` | `(2 kappa + 3)d - 1` |

For the representative `kappa=5`, the minimal-support thresholds are:

```text
bulk trace:      beta > 12d - 1
bulk pre-trace:  beta > 22d - 1
edge trace:      beta > 8d - 1
edge pre-trace:  beta > 13d - 1
```

These inequalities are necessary only inside this exponent model. They do not prove that the modeled variance law is available.

## Generated Budget Table

The analyzer `scripts/analyze_long_support_variance_budget.py` writes:

- `data/extension_candidates/long_support_variance_budget.csv`.
- `data/extension_candidates/long_support_variance_summary.csv`.
- `reports/figures/m20_required_variance_saving.png`.
- `reports/figures/m20_long_support_feasibility_map.png`.

The generated grid has 4356 rows over `d`, `eta`, `kappa`, `Lambda0`, regime, and architecture. Classification counts are:

| feasibility class | rows |
|---|---:|
| impossible_by_support | 1872 |
| outside_current_architecture | 1284 |
| requires_no_extra_saving | 510 |
| requires_moderate_new_saving | 192 |
| requires_large_new_saving | 498 |

For `kappa=5`, fixed `Lambda0=4`, and endpoint-beating rows satisfying the M19 support threshold:

| regime | architecture | rows | min required beta | median required beta |
|---|---|---:|---:|---:|
| bulk | trace | 28 | -0.904 | 0.15 |
| bulk | pre-trace | 28 | -0.824 | 1.15 |
| edge | trace | 44 | -0.942 | -0.091 |
| edge | pre-trace | 44 | -0.902 | 0.659 |
| high_energy | trace | 28 | -0.904 | 0.15 |
| high_energy | pre-trace | 28 | -0.824 | 1.15 |

Negative required beta means the crude baseline exponent `Var <= n^(1+L)` would already satisfy Chebyshev in that row. This is an exponent-budget statement only; the actual obstacle remains proving such a localized long-support variance theorem for the trace statistic.

## Consequence

The trace side remains the only conditionally plausible compact-support local-window route. For small endpoint-beating windows, it asks for no or moderate additional saving in this exponent bookkeeping. The pre-trace route rapidly asks for order-one or larger saving because its loss is doubled.

The next mathematical target, if this branch continues, is a precise long-support trace variance conjecture with support `R=n^eta`, `eta>=d`, and variance exponent

```text
Var Z_n <= n^(1 + 2 kappa eta - beta(eta))
```

where `beta(eta)` beats `2 kappa eta + 2d - 1` in the bulk. Under current proved Kim--Tao inputs this theorem is absent, so M20 does not claim local spectral statistics or an improved rigidity exponent.
