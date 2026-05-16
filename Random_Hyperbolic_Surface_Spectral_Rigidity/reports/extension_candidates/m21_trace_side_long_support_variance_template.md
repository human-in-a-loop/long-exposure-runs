---
created: 2026-05-16T17:24:00Z
cycle: 32
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M21-trace-side-long-support-variance-template
---

# M21 Trace-Side Long-Support Variance Template

## Purpose

M20 showed that the only remaining compact-support local-window branch worth formulating is fixed-energy trace-side variance with polynomial support. M21 states the missing theorem target in paper-compatible notation and tests the exponent budget against simple candidate beta models.

## Statistic

Fix

```text
Lambda0 > 1/4,        r0 = sqrt(Lambda0 - 1/4),
Delta = n^(-d),       q = n^eta,       eta >= d.
```

The spectral statistic is

```text
Z_n(h_{Lambda0,Delta,q})
  = sum_j h_{Lambda0,Delta,q}(r_j(X_n))
    - n Vol(X)/(2pi) int_0^infty h_{Lambda0,Delta,q}(r) r tanh(pi r) dr.
```

Here `lambda_j(X_n)=r_j(X_n)^2+1/4`, and `h_{Lambda0,Delta,q}` should be an even localized trace test centered at `r0` with `r`-width

```text
delta_r = Delta/(2r0) + O(Delta^2).
```

By Lemma 2.1, the same statistic is the non-identity geometric trace term

```text
sum_{gamma in P(X)} sum_{k>=1}
  ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
  h_{Lambda0,Delta,q}^vee(k ell_gamma(X))
  tr rho(gamma^k).
```

This is the exact attachment point to the trace formula. The remaining construction issue is that Kim--Tao's §2.4 `h o f_Lambda0` class is built for endpoint cutoffs, so M21 requires a localized analogue with the same compact support and polynomialization properties.

## Theorem Template

`LSTV_trace(eta,beta)` says that for fixed `Lambda0>1/4`, `Delta=n^(-d)`, `q=n^eta`, and `eta>=d`,

```text
Var Z_n(h_{Lambda0,Delta,q})
  <= C n^(1 + 2 kappa eta - beta + epsilon)
```

uniformly over normalized admissible localized bumps and over a fixed endpoint-beating `d`-range. The `2 kappa eta` term is the Proposition 3.1 trace-side Markov/interpolation loss after substituting `q=n^eta`; `beta` is the new random-cover saving.

The bulk expected mass is `mu_n ~= n Delta = n^(1-d)`. Chebyshev gives relative smoothed-window control when

```text
1 + 2 kappa eta - beta < 2 - 2d,
```

or

```text
beta > 2 kappa eta + 2d - 1.
```

If also `d>alpha_W`, this beats M16 endpoint subtraction. At minimal support `eta=d`, the threshold is `beta>(2 kappa+2)d-1`; for `kappa=5`, `beta>12d-1`.

## Generated Budget

The analyzer `scripts/analyze_trace_variance_template_budget.py` restricts M20 to fixed-bulk trace rows and evaluates candidate beta models:

- no new saving: `beta=0`;
- constant beta: `0.25`, `0.75`, `1.25`;
- linear beta: `c eta` with `c=4,8,12`;
- saturation beta: `min(c,10 eta)` with `c=0.5,1.0`.

Outputs:

- `data/extension_candidates/trace_variance_template_budget.csv` with 11,664 rows.
- `data/extension_candidates/trace_variance_template_summary.csv` with 81 rows.
- `reports/figures/m21_trace_template_beta_thresholds.png`.
- `reports/figures/m21_trace_template_plausibility_regions.png`.

Across the full generated grid, the plausibility classes are:

| class | rows |
|---|---:|
| support_invalid | 5346 |
| not_endpoint_beating | 3564 |
| conditional_success | 1927 |
| needs_large_saving | 531 |
| needs_moderate_saving | 296 |

For the representative `kappa=5`, `alpha_W=0.006` rows, each beta model has 36 endpoint-beating support-valid `(d,eta)` pairs. The required beta range is:

```text
min required beta    = -0.904
median required beta =  0.07
max required beta    =  2.0
```

Representative model outcomes:

| beta model | local successes / 36 | interpretation |
|---|---:|---|
| `beta=0` | 15 | only the rows with genuinely negative required beta pass |
| `beta=0.75` | 27 | moderate constant saving handles most small windows |
| `beta=8 eta` | 35 | linear saving nearly covers the tested fixed-energy band |
| `min(1,10 eta)` | 28 | saturation helps but fails larger-support rows |

![required trace-side long-support variance saving as a function of window exponent and support exponent](reports/figures/m21_trace_template_beta_thresholds.png)

![conditional success regions for candidate beta models in the fixed-energy trace-side theorem template](reports/figures/m21_trace_template_plausibility_regions.png)

## Dependency Checklist

| dependency | status | reason |
|---|---|---|
| Lemma 2.1 trace formula | existing | It exactly identifies the centered spectral statistic with the non-identity geodesic trace statistic. |
| §2.4 test-function architecture | new localized construction needed | Existing `h o f_Lambda0` endpoint cutoffs give the support/polynomial template, but not a translated local bump. |
| M19 support condition | existing | Fixed-quality compact-support localization forces `eta>=d` in the bulk. |
| Proposition 3.1 variance form | needs uniform long-support extension | Current theorem is not a localized window theorem at `q=n^eta`; M21 only reuses its loss structure. |
| Lemma 3.3 two-trace polynomial expansion | needs uniform extension | The word-length range and constants must survive `q=n^eta` in the endpoint-beating regime. |
| Corollary 3.4 polynomial numerator | new theorem | The needed object is a localized weighted numerator with coefficient-variation or direct small-`x` control. |
| MPvH/Witten-zeta normalization | needs uniform extension | It underlies the rational expansion and denominator control used in Lemma 3.3. |
| Nau boundedness | needs uniform extension | It removes negative powers in the expectation expansion; this must hold uniformly in the longer support range. |
| Markov interpolation | existing but costly | Keeping it gives the `2 kappa eta` loss; improving it is not assumed. |
| De-smoothing | out of scope | M21 proves only a smoothed-window consequence conditional on the variance theorem. |

## Falsifiable Obstruction

This route should be rejected before a proof attempt if the localized test family cannot be expressed through Lemma 2.1 with compact support `q=n^eta`, or if Corollary 3.4's weighted two-trace numerator has coefficient variation too large to permit any positive beta in the endpoint-beating support-valid band. A second hard obstruction would be that the MPvH/Nau inputs cannot be made uniform for `q=n^eta` even in the small endpoint-beating range.

## Decision

Decision: `needs external uniform input before proof attempt`.

The exact next bottleneck is Corollary 3.4, not Proposition 3.1 as a black box. The next artifact should be:

```text
docs/proof_ledger/trace_corollary34_uniform_coefficient_variation_target.md
```

It should define the localized weighted numerator `p_{Delta,q}` and test whether one can prove uniform coefficient-variation or direct numerator control strong enough to produce

```text
Var Z_n <= n^(1 + 2 kappa eta - beta)
```

with `beta > 2 kappa eta + 2d - 1` for some `d>alpha_W`, `eta>=d`.

## Non-Claims

M21 does not prove the long-support variance theorem, does not improve Kim--Tao's exponent, does not prove local spectral statistics, and does not reopen the pre-trace branch. It identifies the theorem target and the proof input that must be strengthened.
