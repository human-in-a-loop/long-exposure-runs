---
created: 2026-05-16T17:48:00Z
cycle: 33
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M22-trace-corollary34-uniform-coefficient-variation-target
---

# Trace Corollary 3.4 Localized Numerator Target

## Purpose

M21 reduced the fixed-energy local-window route to a long-support trace variance theorem. M22 narrows that theorem to the exact Corollary 3.4 numerator problem. This note is a proof target, not a proof of beta saving.

## Paper Attachment Point

Kim--Tao Proposition 3.1 studies the normalized centered trace statistic

```text
(1/n) G_n(h)
```

where, by Lemma 2.1,

```text
G_n(h)
  = sum_{gamma in P(X)} sum_{k>=1}
      ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
      (h o f_Lambda0)^vee(k ell_gamma(X))
      tr rho(gamma^k).
```

The second moment expands as a two-trace weighted sum:

```text
E G_n(h)^2
 = sum_{gamma1,gamma2} sum_{k1,k2>=1}
     a(gamma1,k1) a(gamma2,k2)
     Hhat(k1 ell_gamma1) Hhat(k2 ell_gamma2)
     E[tr rho(gamma1^k1) tr rho(gamma2^k2)],
```

with

```text
a(gamma,k) = ell_gamma(X)/(2 sinh(k ell_gamma(X)/2)),
Hhat(t) = (h o f_Lambda0)^vee(t).
```

Lemma 3.3 gives, for word length at most `q`,

```text
E[tr rho(gamma1) tr rho(gamma2)]
  = Q_{gamma1,gamma2}(1/n)/Q_id(1/n) + O((Cq)^(Cq)n^(-q)).
```

Corollary 3.4 packages the weighted sum into a polynomial numerator

```text
p(x)
 = sum_{gamma1,gamma2} sum_{k1,k2>=1}
     a(gamma1,k1) a(gamma2,k2)
     Hhat(k1 ell_gamma1) Hhat(k2 ell_gamma2)
     Q_{gamma1^k1,gamma2^k2}(x),
```

so that

```text
E G_n(h)^2 = p(1/n)/Q_id(1/n) + error.
```

The paper then uses uniform boundedness plus Markov brothers' inequality to convert mesh control of `x^2 p(x)` into the Proposition 3.1 loss `q^(2 kappa)`.

## Localized Numerator

Fix bulk `Lambda0>1/4`, `Delta=n^(-d)`, and `q=n^eta` with `eta>=d`. Let `h_{Delta,q}` be the M21 localized trace test centered at

```text
r0 = sqrt(Lambda0 - 1/4)
```

with `r`-width comparable to `Delta/(2r0)` and compact transform support at scale `q`.

The localized Corollary 3.4 numerator is the direct analogue

```text
p_{Delta,q}(x)
 = sum_{gamma1,gamma2 in P(X)} sum_{k1,k2>=1}
     a(gamma1,k1) a(gamma2,k2)
     h_{Delta,q}^vee(k1 ell_gamma1)
     h_{Delta,q}^vee(k2 ell_gamma2)
     Q_{gamma1^k1,gamma2^k2}(x),
```

restricted by the support condition

```text
k_i ell_gamma_i <= C(Lambda0) q.
```

If the localized test is literally expressible as Kim--Tao's `h o f_Lambda0`, this is exactly Corollary 3.4's `p` with a new choice of polynomial `h`. If the localized construction needs a different admissible test class, `p_{Delta,q}` is not literally the paper's numerator; it is the closest exact object and requires a new lemma showing the same Lemma 3.3 package, denominator `Q_id`, degree bound, and error term survive.

## Baseline And Beta Algebra

For the unnormalized local statistic `Z_n(h_{Delta,q})=G_n(h_{Delta,q})`, the M21 baseline is

```text
Var Z_n <= n q^(2 kappa) = n^(1 + 2 kappa eta).
```

A candidate numerator theorem of the form

```text
E G_n(h_{Delta,q})^2 <= n q^A n^(-sigma + o(1))
```

implies

```text
Var Z_n <= n^(1 + A eta - sigma + o(1))
```

and therefore

```text
beta = (2 kappa - A) eta + sigma.
```

The M21 Chebyshev condition for endpoint-beating fixed-bulk windows is

```text
d > alpha_W,       eta >= d,       beta > 2 kappa eta + 2d - 1.
```

Equivalently, the numerator theorem itself must give

```text
1 + A eta - sigma < 2 - 2d.
```

## Candidate Sufficient Targets

### 1. Coefficient-Variation Target

Write

```text
p_{Delta,q}(x) = sum_{m=0}^{D(q)} c_m(Delta,q) x^m.
```

A coefficient-variation target asks for fixed `M` and a controlled tail:

```text
sum_{m<=M} |c_m(Delta,q)| n^(-m)
  + tail_M(1/n)
  <= n q^A n^(-sigma + o(1)).
```

This is useful only if it controls the signed weighted aggregate after Selberg weights and denominator normalization, not just termwise product ratios. The implied beta is

```text
beta_CV = (2 kappa - A) eta + sigma.
```

Pure Kim--Tao Markov interpolation corresponds to `A=2 kappa`, `sigma=0`, hence `beta_CV=0`.

### 2. Direct Small-x Target

A direct small-`x` target bypasses coefficient expansion:

```text
|p_{Delta,q}(1/n)|/Q_id(1/n)
  <= n q^A n^(-sigma + o(1)).
```

This may use cancellation that is invisible to absolute coefficient variation. Cancellation only at `x=0` is insufficient; the bound must hold in a neighborhood containing `x=1/n` for `n>=q^C`. The implied beta is again

```text
beta_direct = (2 kappa - A) eta + sigma.
```

### 3. Stratified Weighted Target

Decompose the numerator by the quotient-template power analogue `s=C-V`:

```text
p_{Delta,q}(x)
  = sum_s p_{Delta,q,s}(x),
  p_{Delta,q,s}(x)=sum_{T in F_{q,s}} omega_T R_T(x).
```

Here `omega_T` contains Selberg weights, localized transform weights, and surface-group probability-law normalization. A stratified target asks for

```text
sum_s |p_{Delta,q,s}(1/n)|
  <= n q^A W(q) n^(-sigma + o(1)).
```

If `W(q)=q^omega`, then

```text
beta_strat = (2 kappa - A - omega) eta + sigma.
```

If the stratification supplies decay `W(q)=q^(-omega)`, replace `A+omega` by `A-omega`.

## Imported Inputs Touched

| Input | Touched by M22 target? | Reason |
|---|---|---|
| Lemma 2.1 trace formula | yes | Identifies the centered statistic with the geodesic trace statistic. |
| Lemma 3.3 | yes | Supplies the two-trace rational expansion for each word pair. Needs uniformity for `q=n^eta`. |
| Corollary 3.4 | yes | Defines the weighted numerator `p`; M22 localizes this object. |
| MPvH/Witten-zeta normalization | yes | Structural source of `Q_id` and polynomial expansion. |
| Nau boundedness | yes | Removes negative powers in the rational expansion; must remain uniform. |
| Markov interpolation | only as baseline | The targets may avoid or improve the Markov envelope, but M22 does not prove a new Markov inequality. |
| MP23 rank-two decay | no in this trace-side target | MP23 enters the pre-trace/eigenfunction branch, which is held out of scope. |

## Falsifiable Decision

M22 rules in the numerator target only conditionally. The object is precise: `p_{Delta,q}` is Corollary 3.4's weighted numerator with the M21 localized test inserted, provided the localized test belongs to the paper-compatible `h o f_Lambda0` class. The next proof attempt should not be global Proposition 3.1; it should either construct that localized test class and prove the Corollary 3.4 package uniformly for `q=n^eta`, or build a quotient-family model for `p_{Delta,q}` that can test coefficient variation and direct small-`x` cancellation.

Decision:

```text
needs quotient-family model before proof attempt
```
