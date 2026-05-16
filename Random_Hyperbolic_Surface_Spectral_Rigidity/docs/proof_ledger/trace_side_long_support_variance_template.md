---
created: 2026-05-16T17:20:00Z
cycle: 32
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M21-trace-side-long-support-variance-template
---

# Trace-Side Long-Support Variance Template

## Purpose

M20 left one conditionally plausible compact-support local-window route: fixed-energy trace-side variance with polynomial geometric support. M21 makes the missing theorem precise enough to attack or reject. It does not prove the theorem.

## Fixed Bulk Setup

Fix a bulk energy

```text
Lambda0 > 1/4,       r0 = sqrt(Lambda0 - 1/4).
```

Let the target lambda-window width be

```text
Delta = n^(-d),      d > 0.
```

In the bulk,

```text
delta_r
  = sqrt(Lambda0 + Delta - 1/4) - sqrt(Lambda0 - 1/4)
  = Delta/(2r0) + O(Delta^2).
```

M19 implies that a compact Fourier/geometric-side test resolving this window with fixed quality must have support exponent at least

```text
q = n^eta,     eta >= d,
```

because Kim--Tao's trace test satisfies, at exponent level for fixed `Lambda0`,

```text
supp((h o f_Lambda0)^vee) <= C(Lambda0) q.
```

The edge case `Lambda0=1/4` is outside this template; M20 handled its separate `eta>=d/2` support budget.

## Centered Statistic

The spectral statistic should be a trace-compatible smoothed window

```text
Z_n(h_{Lambda0,Delta,q})
  = sum_j h_{Lambda0,Delta,q}(r_j(X_n))
    - n Vol(X)/(2pi) int_0^infty h_{Lambda0,Delta,q}(r) r tanh(pi r) dr,
```

where `lambda_j(X_n)=r_j(X_n)^2+1/4`, and `h_{Lambda0,Delta,q}` is even, localized near `r0` at width `delta_r`, and has Fourier transform supported at scale `q=n^eta`.

The closest paper-compatible version is not Kim--Tao's original monotone endpoint cutoff. It is a new localized analogue of the §2.4 class

```text
h_{Lambda0,Delta,q}(r) = H_{Delta,q}(f_Lambda0(r))
```

with `H_{Delta,q}(x)=x \tilde H_{Delta,q}(x)` a polynomial of degree `q`, or a replacement admissible class with the same trace-formula support and polynomialization properties. The original §2.4 construction is existing for endpoint cutoffs; the translated local-window construction is a new dependency.

By Lemma 2.1, the equivalent centered geometric statistic is

```text
G_n(h_{Lambda0,Delta,q})
  = sum_{gamma in P(X)} sum_{k>=1}
      ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
      h_{Lambda0,Delta,q}^vee(k ell_gamma(X))
      tr rho(gamma^k).
```

The deterministic Weyl main term in `Z_n` is exactly the identity term in Lemma 2.1, so

```text
Z_n(h_{Lambda0,Delta,q}) = G_n(h_{Lambda0,Delta,q})
```

for each random cover realization, assuming the chosen test function is admissible for the trace formula.

For comparison with M17, a nonnegative normalized bump should satisfy

```text
sum_j h_{Lambda0,Delta,q}(r_j(X_n))
  ~= sum_j phi((lambda_j(X_n)-Lambda0)/Delta),
```

up to a controlled smoothing error. The expected bulk mass is

```text
mu_n ~= n Delta = n^(1-d)
```

after suppressing fixed constants depending on `X`, `Lambda0`, and the bump.

## Conditional Theorem Template

**Template `LSTV_trace(eta,beta)`.** Fix `Lambda0>1/4`, compact `d`-range

```text
alpha_W < d <= d_max < 1/2,
```

and support exponent `eta>=d`. Suppose there is an admissible localized trace-test class `h_{Lambda0,Delta,q}` with `Delta=n^(-d)` and `q=n^eta` such that, uniformly over the `d`-range and over normalized bumps in the class,

```text
Var Z_n(h_{Lambda0,Delta,q})
  <= C_{Lambda0,phi,epsilon} n^(1 + 2 kappa eta - beta + epsilon)
```

for every fixed `epsilon>0`.

Here `2 kappa eta` is the trace-side Kim--Tao Markov/interpolation loss from Proposition 3.1 after substituting `q=n^eta`, and `beta` is a new random-cover saving beyond the baseline `n q^(2 kappa)` scale.

## Local-Window Consequence

The bulk mean exponent is `1-d`. Chebyshev gives relative smoothed-window control if

```text
1 + 2 kappa eta - beta < 2 - 2d,
```

equivalently

```text
beta > 2 kappa eta + 2d - 1.
```

Thus `LSTV_trace(eta,beta)` implies

```text
Z_n(h_{Lambda0,Delta,q}) = o(n Delta)
```

with high probability whenever the strict beta inequality holds. If also

```text
d > alpha_W,
```

then the smoothed window is below the M16 endpoint-subtraction scale and gives a genuinely new local-window corollary, still smoothed and not an exact interval count.

At minimal support `eta=d`, the requirement is

```text
beta > (2 kappa + 2)d - 1.
```

For `kappa=5`, this is `beta > 12d - 1`.

## Attachment To Kim--Tao Objects

| Input | Role in the template | Status |
|---|---|---|
| Lemma 2.1 twisted Selberg trace formula | Identifies `Z_n` with the non-identity geodesic trace statistic `G_n`. | existing |
| §2.4 endpoint test functions `h o f_Lambda0` | Supplies the paper's polynomial/support architecture and `q` parameter. | existing for endpoint cutoffs; new localized construction needed |
| Proposition 3.1 | Current trace variance bound with loss `Lambda0^2 q^(2 kappa) n^(-1)` for normalized endpoint statistics. | needs uniform long-support/local-window extension |
| Lemma 3.3 | Two-trace expectation becomes `Q_{gamma1,gamma2}(1/n)/Q_id(1/n)` plus small error for word length `<=q`. | needs uniform extension when `q=n^eta`; current statement requires `n>=q^C` and constants must survive the local test family |
| Corollary 3.4 | Packages the weighted two-geodesic sum into a polynomial numerator `p(1/n)` of degree `O(Lambda0^(-1/2)q)`. | needs new theorem controlling localized weighted coefficient variation or numerator size |
| MPvH/Witten-zeta normalization | Gives rational/polynomial expansion and denominator normalization behind Lemma 3.3. | needs uniform extension in the polynomial-support regime |
| Nau boundedness | Removes negative powers in the two-trace expectation expansion. | needs uniformity for the longer word range used by localized support |
| Markov brothers interpolation | Converts mesh control into interval control and produces `q^(2 kappa)`. | existing, but preserving it leaves the `2 kappa eta` loss |
| M19 support obstruction | Forces `eta>=d` for fixed-quality compact-support bulk localization. | existing negative constraint |
| De-smoothing to sharp intervals | Would convert smoothed control to interval counts. | out of scope/new theorem |

## What Would Falsify The Route

The trace-side route should be closed before a proof attempt if any one of these occurs:

1. No localized admissible test family can be made compatible with Lemma 2.1 and the §2.4 polynomial/support architecture at `q=n^eta`.
2. Lemma 3.3 or Corollary 3.4 cannot be made uniform for `q=n^eta` in any endpoint-beating range `d>alpha_W`, `eta>=d`.
3. The weighted two-geodesic polynomial numerator has coefficient variation so large that every endpoint-beating row requires implausibly large `beta`.
4. The only available localized construction requires noncompact geometric tails, moving the problem outside the compact-support trace template.

## Decision For Next Cycle

M21 should not attempt a proof. The next proof-facing bottleneck, if the branch continues, is:

```text
docs/proof_ledger/trace_corollary34_uniform_coefficient_variation_target.md
```

That target should isolate Corollary 3.4's localized weighted numerator `p_{Delta,q}` and ask whether fixed-order coefficient variation or direct small-`x` control can beat the raw Markov envelope uniformly for `q=n^eta`.
