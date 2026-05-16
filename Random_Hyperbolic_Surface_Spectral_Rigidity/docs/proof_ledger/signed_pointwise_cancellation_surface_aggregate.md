---
created: 2026-05-17T00:36:30Z
cycle: 48
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M37-signed-pointwise-cancellation-surface-aggregate
---

# Signed Pointwise Cancellation Surface Aggregate

M37 inspects the only route left open by M36 that is genuinely narrower than coefficient variation: signed pointwise cancellation in the actual Kim--Tao Corollary 3.4 ratio at `x=1/n`.

The paper-defined aggregate is

```text
E S_n(h)^2
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2),
```

with

```text
p(x)
 = sum_{gamma1,gamma2 in P(X)} sum_{k1,k2>=1}
     ell_gamma1 ell_gamma2
     ------------------------------------------------
     4 sinh(k1 ell_gamma1/2) sinh(k2 ell_gamma2/2)
     * (h o f_Lambda0)^vee(k1 ell_gamma1)
     * (h o f_Lambda0)^vee(k2 ell_gamma2)
     * Q_{gamma1^k1,gamma2^k2}(x).
```

The sign of an individual summand can only enter through the transform values and the evaluated quotient polynomial `Q_{gamma1^k1,gamma2^k2}(1/n)`.  The Selberg length factor is positive, while `Q_id(1/n)` is a normalization factor bounded above and below in the paper-safe range.  Therefore a direct signed theorem must control the weighted signed sum after evaluation and normalization, not merely individual quotient templates.

## Baseline and Target

The repaired paper baseline is

```text
n^(-2) |p(1/n)| <= C Lambda0^20 ||htilde||^2,
```

followed by Markov control of `P(x)=x^2 p(x)`,

```text
||(x^2 p(x))'|| <= C q^(2 kappa) Lambda0^20 ||htilde||^2.
```

The signed pointwise theorem target is:

**Target SPC(A,sigma).**  In the paper-safe range `n >= C q^kappa`, prove for the actual Corollary 3.4 aggregate

```text
|p(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)),
```

using signed cancellation at the evaluated point `x=1/n`.

For `q=n^eta`, and denominator loss modeled by `|Q_id(1/n)|^(-1) <= n^D`, the effective saving against Markov remains

```text
beta = (2 kappa - A) eta + sigma - D.
```

In the paper-safe denominator regime, `D=0`.  Outside it, zeros or near-zeros of `Q_id(1/n)` can erase every signed numerator saving.

## Mechanism Classification

The viable independent target is a surface-attached grouping of the actual summands:

```text
sum w(gamma1,k1) w(gamma2,k2)
    Q_{gamma1^k1,gamma2^k2}(1/n) / Q_id(1/n),
```

where the grouping is by a surface-relevant stratum such as fixed `d=C-V`, length, primitive-power type, or quotient complexity.  It must show cancellation after all weights and after evaluation at `x=1/n`.

Candidate mechanisms classify as follows:

| mechanism | classification | reason |
|---|---|---|
| signed pointwise grouping of surface quotient strata | `surface_theorem_target` | Could prove a direct value saving without bounding all coefficients. |
| diagonal/off-diagonal signed balance | `surface_theorem_target` | Independent only if the actual surface diagonal and off-diagonal pieces cancel at `x=1/n`. |
| transform phase oscillation | `surface_theorem_target` | Possible only if transform signs interact with quotient evaluations in the surface aggregate. |
| fixed-stratum absolute control | `coefficient_variation_equivalent` | Absolute values within fixed strata are coefficient/variation control in substance. |
| coefficient sign-variation control | `coefficient_variation_equivalent` | Expands and controls coefficients instead of only the evaluated value. |
| cancellation at `x=0` | `range_blocked` | Wrong point; it does not control `p(1/n)/Q_id(1/n)` without neighborhood or coefficient input. |
| off-range reciprocal cancellation | `range_blocked` | Leaves the Corollary 3.4 safe range. |
| near-zero denominator saving | `denominator_blocked` | The loss `D` subtracts from beta and may make the ratio undefined. |
| Schreier or independent-permutation pairing | `toy_only` | Missing the surface relation, MPvH/Witten-zeta normalization, Nau boundedness, `Q_id`, and Selberg weights. |

## Decision

Signed pointwise cancellation remains an independent next theorem target only in the exact `SPC(A,sigma)` form above.  The route should be abandoned in favor of coefficient variation if the proof requires absolute control in every fixed `d`, length, primitive-power, or quotient-complexity stratum.  M37 does not prove exponent improvement, local spectral statistics, a variance law, or a shrinking-window theorem; it sharpens the falsifiable target for the next attack.
