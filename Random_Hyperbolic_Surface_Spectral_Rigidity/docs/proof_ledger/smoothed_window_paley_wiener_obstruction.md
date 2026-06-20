---
created: 2026-05-16T16:06:00Z
cycle: 30
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M19-smoothed-window-paley-wiener-lemma
---

# Smoothed Window Paley-Wiener Obstruction

## Purpose

M18 left one possible escape route for the M17 local-window variance program: perhaps a translated smoothed spectral window can keep Kim--Tao-compatible geometric support, for example `R=O(log n)`, while still resolving a shrinking window `Delta=n^{-d}`. This note isolates the Fourier-scaling obstruction. It does not prove or assume any new random-cover variance estimate.

## Fourier-Scaling Lemma

Use the non-unitary Fourier convention

```text
hat h(t) = int_R h(r) exp(-i r t) dr.
```

Let `phi` be a Schwartz window profile with integrable transform, let `r0>=0`, and define

```text
h_delta(r) = phi((r-r0)/delta),       delta > 0.
```

Then the exact scaling identity is

```text
hat h_delta(t) = delta exp(-i r0 t) hat phi(delta t).
```

This is the substitution `u=(r-r0)/delta`. It is the whole obstruction: after truncating geometric/Fourier support to `|t|<=R`, the retained scaled transform only sees `|u|<=R delta`.

## Leakage From Support Truncation

The Fourier `L1` tail lost by truncation is

```text
tail_phi(R delta)
  = int_{|u|>R delta} |hat phi(u)| du.
```

Thus a fixed-quality smoothed localized window requires

```text
R delta >= c_phi > 0,
```

and small leakage for standard Schwartz tails requires

```text
R delta -> infinity.
```

If `R delta -> 0`, the truncated transform retains only a vanishing scaled neighborhood of the origin. For ordinary nonzero window profiles this loses order-one Fourier mass. Constants and normalization do not affect the exponent conclusion.

## Lambda Width To r Width

The spectral variable in the paper is

```text
lambda = r^2 + 1/4.
```

For a lambda-window `[Lambda, Lambda+Delta]`, the exact r-width is

```text
delta_r = sqrt(Lambda + Delta - 1/4) - sqrt(Lambda - 1/4).
```

In fixed bulk energy, `Lambda>1/4`,

```text
delta_r = Delta / (2 sqrt(Lambda-1/4)) + O(Delta^2).
```

At the spectral edge,

```text
Lambda = 1/4,     delta_r = sqrt(Delta).
```

At high energy, fixed lambda-width has an extra constant penalty `1/(2 sqrt(Lambda-1/4))`; the exponent in `n` is unchanged for fixed `Lambda`, but the support constant worsens.

## Exponent Consequence

Let `Delta=n^{-d}`.

In the fixed bulk,

```text
delta_r ~= n^{-d},
```

so `R=O(log n)` gives

```text
R delta_r ~= (log n) n^{-d} -> 0
```

for every fixed `d>0`. Logarithmic support therefore cannot give a fixed-quality smoothed spectral window at polynomially shrinking bulk width. Polynomial support `R=n^eta` has

```text
R delta_r ~= n^{eta-d}.
```

It resolves the window at fixed quality only when `eta>=d`, and gives small leakage only when `eta>d`.

At the edge,

```text
delta_r = n^{-d/2},
```

so the corresponding threshold is `eta>=d/2`. The edge changes the exponent by a factor of one half; it does not remove the uncertainty obstruction.

## Gaussian And Compact-Support Kernels

A Gaussian profile illustrates the tradeoff rather than escaping it. Its Fourier tail decays quickly once `R delta_r` is large, but if `R delta_r -> 0`, the retained mass still tends to zero and leakage remains order one. Noncompact Gaussian support also falls outside the compact-support Selberg-transform architecture unless a new geometric-tail estimate replaces Kim--Tao's finite-support argument.

Compactly supported Fourier kernels fit the trace architecture, but their spectral transition width is itself `~1/R`; using them for a narrower window again requires `R delta_r` bounded below. Fejer/triangular smoothing changes the leakage profile near the transition, not the inverse-width scaling.

## Negative Proposition To Carry Forward

**Proposition (Fourier-support obstruction, scaling form).** Fix a nonzero Schwartz profile `phi` with integrable Fourier transform. Any family of translated windows `phi((r-r0)/delta_r)` approximated by truncating the geometric/Fourier side to `|t|<=R_n` has Fourier-tail leakage

```text
int_{|u|>R_n delta_r} |hat phi(u)| du.
```

Consequently, fixed-quality localization requires `R_n delta_r` bounded below, and vanishing Fourier-tail leakage for standard kernels requires `R_n delta_r -> infinity`. In particular, for fixed bulk `Lambda>1/4` and `Delta=n^{-d}`, logarithmic or sub-polynomial support cannot resolve the window for any fixed `d>0`; polynomial support must have exponent at least `d`. At `Lambda=1/4`, the same statement holds with threshold `d/2`.

This is a negative obstruction inside the compactly supported Kim--Tao test-function architecture. It does not rule out a different theorem with noncompact geometric tails, a weaker leakage tolerance, or a new random-cover variance estimate adapted to long support. De-smoothing from smoothed counts to sharp interval counts is also conditional and outside this lemma.
