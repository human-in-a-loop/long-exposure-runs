---
created: 2026-05-17T01:07:00Z
cycle: 49
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M38-surface-native-grouping-problem
---

# Surface-Native Grouping Problem

M38 refines M37 from generic signed cancellation to the paper-native grouping problem for the actual Kim--Tao Corollary 3.4 aggregate.  The object remains

```text
E S_n(h)^2
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2),
```

where

```text
p(x) = sum_{gamma1,gamma2 in P(X)} sum_{k1,k2>=1}
       w(gamma1,k1) w(gamma2,k2)
       Q_{gamma1^k1,gamma2^k2}(x)
```

and

```text
w(gamma,k)
  = ell_gamma / (2 sinh(k ell_gamma/2))
    * (h o f_Lambda0)^vee(k ell_gamma).
```

The positive factor is `ell_gamma/(2 sinh(k ell_gamma/2))`.  Signs can enter only through transform values and the evaluated quotient polynomial value `Q_{gamma1^k1,gamma2^k2}(1/n)`.  The denominator `Q_id(1/n)` is safe only in the paper range, where it is bounded above and below.

## Summand Schema

A summand in the normalized ratio has the schema

```text
w(gamma1,k1) w(gamma2,k2)
Q_{gamma1^k1,gamma2^k2}(1/n) / Q_id(1/n).
```

Paper-native invariants attached to this summand are:

| invariant | paper visibility | role |
|---|---|---|
| fixed `d=C-V` or quotient-complexity profile | visible through the quotient-polynomial/probability-law architecture | tracks polynomial degree and template complexity but becomes coefficient variation if controlled absolutely |
| primitive-power profile `(gamma,k)` | visible in Proposition 3.1 and Corollary 3.4 | separates primitive geodesics from their powers |
| length shell | visible through `ell_gamma` and Selberg weights | carries positive length weight and transform sign/phase information |
| diagonal/off-diagonal relation | visible in the two-trace aggregate | may isolate same-word or related-word terms but needs real surface cancellation to beat Markov |
| transform-sign/phase class | visible through `(h o f_Lambda0)^vee` | genuine sign source, but useful only after interaction with quotient evaluations |
| surface-relation kernel constraint | implicit in Lemma 3.3 quotient families | most surface-native candidate, because it could use the base surface relation rather than imported free/Schreier pairings |
| Schreier or independent-permutation pairing | imported toy invariant | negative control only; not theorem evidence for the surface aggregate |

## Grouped Theorem Template

For a grouping invariant `G`, the direct pointwise target is:

```text
SPC_G(A,sigma):
|sum_{i in G} w_i Q_i(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

This is a genuine signed pointwise route only if:

1. `G` is native to Lemma 3.3 / Corollary 3.4.
2. The value is evaluated at `x=1/n`, not only at `x=0`.
3. `Q_id(1/n)` is in the paper-safe denominator regime or the denominator loss `D` is explicitly paid.
4. The proof does not replace the grouped signed sum by `sum |w_i Q_i|` or by coefficient total variation inside fixed strata.

For `q=n^eta`, the saving bookkeeping is still

```text
beta = (2 kappa - A) eta + sigma - D.
```

The Markov baseline is `A=2 kappa`, `sigma=0`, `D=0`, with `Lambda0^20`.

## Classification

The surviving direct theorem targets are narrow:

| grouping | classification | reason |
|---|---|---|
| surface-relation kernel grouping | `surface_theorem_target` | paper-native, pointwise at `x=1/n`, and potentially uses information absent from toy models |
| length-shell transform phase grouping | `surface_theorem_target` | uses an actual sign source in the weighted summand, but still needs a surface theorem |
| quotient-complex profile grouping | `underdetermined_surface_input` | native and pointwise, but no current input supplies sign cancellation inside profiles |
| diagonal/off-diagonal relation balance | `underdetermined_surface_input` | native, but diagonal terms are not automatically canceling |
| primitive-power profile | `underdetermined_surface_input` | native to the Selberg sum, but no signed cancellation input is available |

Rows that require absolute control in fixed `d=C-V`, length, primitive-power, quotient-complexity, or coefficient strata are `coefficient_variation_equivalent`.  They may be the right next route, but they are not a direct signed pointwise theorem.

Rows based on `x=0` cancellation are `range_blocked` because they do not control `p(1/n)/Q_id(1/n)` without neighborhood or coefficient input.  Rows outside the paper-safe reciprocal range are also `range_blocked`.  Rows with near-zero `Q_id(1/n)` are `denominator_blocked` because `D` subtracts from beta and can erase every numerator saving.  Schreier or independent-permutation groupings are `toy_only`.

## Pivot Rule

Continue the direct small-`x` branch only if the next proof attacks an `SPC_G(A,sigma)` target for a paper-native grouping at `x=1/n`.  If every plausible proof step needs absolute mass or coefficient variation inside fixed quotient-complexity, length, primitive-power, or `d=C-V` strata, pivot to a coefficient/signed-variation theorem for the actual surface numerator.

M38 proves no exponent improvement, local spectral statistics, variance law, shrinking-window theorem, or surface cancellation theorem.
