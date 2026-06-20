---
created: 2026-05-16T18:50:00Z
cycle: 35
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M24-localized-transform-geodesic-weight-decay-obstruction
---

# Localized Transform And Geodesic Weight Decay

## Purpose

M23 left one concrete question before any coefficient-variation proof attempt: can the localized transform and Selberg/geodesic factors already present in Kim--Tao justify the optimistic extra decay model used as a contrast in the M23 proxy table? This note answers that question for the fixed-energy bulk trace-side route. It does not estimate the actual surface-group quotient family in Lemma 3.3.

## Paper-Facing Localized Numerator

Lemma 2.1 gives the non-identity trace statistic

```text
G_n(h) =
  sum_{gamma in P(X)} sum_{k >= 1}
    ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
    h^vee(k ell_gamma(X))
    tr rho(gamma^k).
```

After squaring and using Lemma 3.3, Corollary 3.4 packages the random-cover expectation into polynomial numerators `Q_{gamma1^k1,gamma2^k2}`. The M22 localized analogue inserts a fixed-energy bulk window `h_{Delta,q}`:

```text
p_{Delta,q}(x) =
  sum_{gamma1,gamma2 in P(X)} sum_{k1,k2 >= 1}
    a(gamma1,k1) a(gamma2,k2)
    h_{Delta,q}^vee(k1 ell_gamma1)
    h_{Delta,q}^vee(k2 ell_gamma2)
    Q_{gamma1^k1,gamma2^k2}(x),
```

where

```text
a(gamma,k)=ell_gamma(X)/(2 sinh(k ell_gamma(X)/2)).
```

The M24 question is only about the product of `a(gamma,k)` and the localized transform values.

## Scaling Lemma

Let `lambda=r^2+1/4`, fix bulk `r0>0`, and let a lambda-window have width `Delta=n^{-d}`. Its r-width is

```text
delta_r = sqrt(Lambda0 + Delta - 1/4) - sqrt(Lambda0 - 1/4)
        = Delta/(2r0) + O(Delta^2).
```

For a translated profile

```text
h_delta(r)=phi((r-r0)/delta_r),
```

the Fourier/Selberg-transform scaling is exactly

```text
h_delta^vee(t) = delta_r exp(-i r0 t) phi^vee(delta_r t).
```

Thus decay inside geometric support is controlled by

```text
u = t delta_r,
```

not by `t` alone. For `q=n^eta`, the support endpoint has

```text
u_endpoint = q delta_r ~= n^(eta-d).
```

The M19 support requirement is `eta>=d` for fixed-quality bulk localization, and `eta>d` for small standard Fourier-tail leakage.

## Candidate Damping Mechanisms

| mechanism | available decay | compatible with Kim--Tao compact-support architecture? | M24 verdict |
|---|---|---|---|
| compact support only | none inside `|t|<=q` | yes | obstructed |
| smooth Paley-Wiener/Schwartz envelope | decay in `u=t delta_r`; polynomial/Schwartz in `u` after transition | yes, as a compactly supported transform envelope | obstructed against exponential-in-support geodesic/family growth |
| integration by parts / vanishing moments | extra powers of `u` or cancellation near selected points | conditional, but zero mean destroys positive window count | not a valid count-positive M22 saving |
| noncompact Gaussian-like tail `exp(-c t)` | exponential in geodesic length | no, unless a new geometric-tail trace theorem replaces finite support | useful contrast only; must have `c` above the relevant growth rate |

The Selberg factor contributes

```text
ell/(2 sinh(k ell/2)) ~= ell exp(-k ell/2)
```

but primitive geodesic growth is of order `exp(L)/L`. Even before quotient-family variation, the crude net geodesic count after one Selberg factor has positive exponential rate in the support length. M23's rank-two and unknown quotient-family proxies add more positive growth, not damping.

Therefore a compatible smooth transform envelope supplies at most scaled `phi^vee(u)` decay. For `eta=d`, `u_endpoint` is constant scale. For `eta>d`, Schwartz decay gives powers of `n^{eta-d}` after choosing a smoothness order, but it is still not an exponential `exp(-c q)` mechanism. It cannot justify the M23 optimistic model `exp(-0.18 t)` inside the compact-support architecture.

## Special-Point Checks

- `t=0`: `|h_delta^vee(0)| = delta_r |phi^vee(0)|`. For a positive counting window, `phi^vee(0)` is nonzero; zeroing it by moments changes the statistic and loses positivity.
- `t ~ 1/delta_r`: this is the first transition scale where `u=t delta_r` is order one. There is no earlier transform decay from scaling alone.
- `t=q`: the endpoint is controlled by `q delta_r=n^(eta-d)`. At `eta=d`, the endpoint envelope is constant scale; at `eta>d`, decay is in the scaled endpoint only.
- `delta_r -> 0`: the transform prefactor `delta_r` is part of the window normalization and must not be double-counted as M22 beta-saving without redoing the variance normalization.
- `q delta_r` bounded: fixed-quality localization is possible, but no growing support-scale damping is available.
- `q delta_r -> infinity`: smooth tails become small in `u`, but compact-support-compatible tails still do not provide exponential-in-`q` damping.
- noncompact Gaussian tail: `exp(-c t)` can offset support-length growth only when `c` exceeds the relevant geodesic/family growth rate; it is outside Kim--Tao's finite-support proof architecture unless a new trace-error theorem controls all omitted geodesic tails.

## Obstruction Statement

**Lemma/obstruction (M24).** In the fixed-energy bulk localized trace-side route, a Kim--Tao-compatible compact-support Paley-Wiener test has transform weight of the form

```text
h_delta^vee(t)=delta_r exp(-i r0 t) phi^vee(delta_r t)
```

on the geometric side. Inside support `0<=t<=q=n^eta`, this gives cutoff-scale or scaled-Schwartz damping in `u=t delta_r`, not exponential damping in `t`. Since the Selberg/geodesic and quotient-family proxies grow with positive exponential rate in support length, these compatible transform weights do not justify M23's optimistic extra factor `exp(-c t)` in the localized numerator. Achieving that kind of damping would require either an independent coefficient-variation theorem not supplied by transform weights, or a noncompact/geometric-tail trace architecture whose tail rate exceeds the relevant growth rate.

## Consequence For The M21-M23 Route

M24 closes the compact-support local-window route as a transform-weight mechanism. A future compact-support theorem would have to attack the actual `Q_{gamma1^k1,gamma2^k2}` coefficient variation directly, not rely on localized transform/geodesic damping to remove the M23 aggregate obstruction. The separate noncompact route remains logically open but would need a new trace-formula tail theorem before it can replace the current Kim--Tao architecture.
