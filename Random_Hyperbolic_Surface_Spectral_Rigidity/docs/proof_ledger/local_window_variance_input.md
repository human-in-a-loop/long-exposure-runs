---
created: 2026-05-16T14:40:00Z
cycle: 28
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M17-local-window-variance-input
---

# Local Window Variance Input

## Setup

M16 showed that endpoint subtraction from the global Kim--Tao Weyl law gives a local interval estimate only when the deterministic local mass dominates two inherited global errors. In the bulk, where

```text
F'(Lambda)=1/2 tanh(pi sqrt(Lambda-1/4)) > 0,
```

that sufficient scale is

```text
Delta_global >> n^(-alpha_W) Lambda^(1/2+epsilon) / ((2g-2)F'(Lambda)).
```

To beat this threshold one needs a local statistic whose fluctuation is charged to the window, not to the two global endpoints.

Fix a compactly supported smooth function `phi` and define the smoothed bulk statistic

```text
Z_n(phi; Lambda, Delta)
  = sum_j phi((lambda_j(X_n)-Lambda)/Delta)
    - main_n(phi; Lambda, Delta).
```

For bulk `Delta << Lambda-1/4`, the natural main term is

```text
main_n(phi; Lambda, Delta)
  = (2g-2)n Delta F'(Lambda) int phi(u) du
    + lower-order Taylor terms.
```

Near `Lambda=1/4`, this linearization is invalid because `F'(1/4)=0`; the edge main term must be computed from the integral `F(1/4+Delta)-F(1/4) ~ (pi/3)Delta^(3/2)`.

## Conditional Proposition

**Proposition template (smoothed variance to local count).** Fix a bulk energy `Lambda>1/4`, a nonnegative smooth window `phi` with positive integral, and a shrinking scale `Delta=Delta(n)`. Suppose a trace/pre-trace argument gives

```text
Var Z_n(phi; Lambda, Delta) <= V(n,Lambda,Delta).
```

Let

```text
mu_n(phi; Lambda, Delta)
  = (2g-2)n Delta F'(Lambda) int phi(u) du.
```

If

```text
sqrt(V(n,Lambda,Delta)) = o(mu_n(phi; Lambda,Delta)),
```

then Chebyshev gives

```text
Z_n(phi; Lambda, Delta) = o(mu_n(phi; Lambda,Delta))
```

with probability tending to one. Equivalently,

```text
sum_j phi((lambda_j(X_n)-Lambda)/Delta)
  = mu_n(phi; Lambda,Delta)(1+o(1)).
```

This is a smoothed-window statement. It does not by itself imply a sharp interval count unless one also proves a de-smoothing comparison between smooth majorants/minorants and the sharp indicator.

## Exponent Test

Write `Delta=n^{-d}` and suppose at exponent level

```text
Var Z_n(phi; Lambda, Delta) <= n^v.
```

In the bulk,

```text
mu_n ~ n Delta = n^(1-d),
```

so Chebyshev requires

```text
v/2 < 1-d.
```

M16 endpoint subtraction controls only

```text
d < alpha_W
```

up to fixed energy and density constants, because `Delta_global ~ n^(-alpha_W)`. Therefore a variance estimate is genuinely new for local windows only if it controls at least one regime with

```text
d > alpha_W
and
v/2 < 1-d.
```

At the spectral edge, the mean exponent changes to

```text
mu_n ~ n Delta^(3/2) = n^(1-3d/2),
```

and the M16 edge threshold is `d=2 alpha_W/3` at exponent level. The same Chebyshev comparison applies after replacing the bulk mean exponent by `1-3d/2`.

## Model Variance Laws

The M17 analyzer records these exponent models:

```text
V ~ n                                  => v = 1
V ~ n Delta                            => v = 1-d
V ~ n^(1-beta) Delta^theta             => v = 1-beta-theta d
pessimistic global-trace proxy          => v = 2-2 alpha_W
```

The first two models are useful only as exponent benchmarks. The pessimistic global proxy represents reusing global endpoint-size fluctuations; it usually fails to add information below the M16 endpoint threshold.

## Kim--Tao Bridge Requirement

The missing theorem is a window-localized trace/pre-trace variance estimate for smoothed spectral test functions whose spectral support is centered at `Lambda` with width `Delta`. Proving it would require all of the following, not merely a restatement of M16:

1. A test-function construction localized to width `Delta`, with controlled geometric support and derivative losses.
2. A random-cover trace variance estimate for the resulting localized trace statistic.
3. Enough correlation or covariance control between nearby windows if one wants uniform-in-window statements.
4. A conditional de-smoothing argument if the target is a sharp interval count rather than a smoothed statistic.

M17 does not claim Kim--Tao proves this input. It isolates the exact inequality such an input would need to satisfy to beat endpoint subtraction.
