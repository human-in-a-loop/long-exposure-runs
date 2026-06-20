---
created: 2026-05-16T19:16:00Z
cycle: 36
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M25-local-window-route-synthesis-and-branch-decision
---

# Localized Corollary 3.4 Coefficient-Variation Problem

## Problem Statement

Let `X_n` be a random `n`-cover in the Kim--Tao model, and fix a bulk spectral parameter `r0`. For a shrinking window of width `Delta=n^{-d}`, insert a compact Paley-Wiener localizer `h_{Delta,q}` with geometric support `q=n^eta` into the trace-side statistic, where `d>alpha_W` and `eta>=d`.

The local-window problem is to prove a variance estimate strong enough to beat endpoint subtraction:

```text
Var Z_n(h_{Delta,q}) <= n q^{2 kappa} n^{-beta+o(1)}
```

with

```text
beta > 2 kappa eta + 2d - 1.
```

M16-M24 reduce the compact-support version to the following focused question.

## Coefficient-Variation Question

For the actual quotient polynomials `Q_{gamma1^k1,gamma2^k2}` from Kim--Tao Lemma 3.3, does the localized Corollary 3.4 numerator

```text
p_{Delta,q}(x)
  = sum_{gamma1,gamma2,k1,k2}
      W_{Delta,q}(gamma1,k1) W_{Delta,q}(gamma2,k2)
      Q_{gamma1^k1,gamma2^k2}(x)
```

satisfy a uniform small-`x` or coefficient-variation estimate of the form

```text
p_{Delta,q}(1/n) / Q_id(1/n)
  <= n q^A n^{-sigma+o(1)}
```

after the identity/diagonal terms are treated exactly, with

```text
(2 kappa - A) eta + sigma > 2 kappa eta + 2d - 1?
```

The estimate must use the actual folded surface-group quotient family. It cannot rely on compact-support transform damping, because M24 shows the compatible transform decay is in `t Delta`, not in support length `t`.

## Conjectural Fork

Either the actual surface-group quotient family has enough small-`x` cancellation or coefficient variation control to satisfy the inequality above, or fixed-energy local windows below the endpoint-subtraction scale require a noncompact trace-tail theorem with geometric decay rate exceeding quotient/geodesic growth.

This problem is conservative: M23 is only toy/proxy evidence for the obstruction, while M24 is an analytic obstruction to one proposed damping mechanism. The coefficient-variation theorem remains open and is the precise compact-support follow-up target.
