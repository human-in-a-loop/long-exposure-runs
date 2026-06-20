---
created: 2026-05-17T00:14:30Z
cycle: 47
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M36-direct-small-x-surface-numerator-target
---

# Direct Small-x Surface Numerator Target

This note sharpens the M35 obstruction into a theorem target at the actual evaluation point `x=1/n`.  The object is the Kim--Tao Corollary 3.4 ratio

```text
E S_n(h)^2
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2),
```

where `p` is the weighted two-trace numerator from Corollary 3.4,

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

The paper gives

```text
deg p <= C Lambda0^(-1/2) q,
Q_id(1/n) in [C^(-1), C] for n >= q^kappa,
```

after choosing constants so the Lemma 3.3 range is compatible with Corollary 3.4.

## Baseline

The paper first obtains reciprocal-integer control

```text
n^(-2) |p(1/n)| <= C Lambda0^20 ||htilde||^2,
n >= C q^kappa.
```

It then applies the Markov brothers inequality to `P(x)=x^2 p(x)`, producing

```text
||(x^2 p(x))'|| <= C q^(2 kappa) Lambda0^20 ||htilde||^2
```

on the small interval used in Proposition 3.1.  Taylor expansion from `0` gives the Proposition 3.1 trace-side envelope

```text
E S_n(h)^2 <= C n Lambda0^20 ||htilde||^2 q^(2 kappa)
```

up to the exponentially small Corollary 3.4 error.

## Direct Theorem Target

A direct replacement for Markov interpolation would be the following conditional theorem.

**Target DSE(A,sigma).**  Fix the paper's compact-support Corollary 3.4 architecture.  For `n >= C q^kappa` and `Lambda0 >= C`, prove

```text
|p(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

The Markov baseline is recovered by `A=2 kappa` and `sigma=0`.  Any useful direct theorem has effective saving

```text
beta = (2 kappa - A) eta + sigma - D
```

when `q=n^eta` and denominator loss is modeled as `|Q_id(1/n)|^(-1) <= n^D`.  In the paper-proved denominator regime, `D=0`.

For the M21/M22 local-window budget, a direct theorem would beat the compact-support trace baseline only if

```text
(2 kappa - A) eta + sigma - D
  > 2 kappa eta + 2d - 1.
```

M36 proves none of these inequalities; it records the exact theorem target and the obstruction points.

## Denominator Normalization

Inside the paper's range, denominator normalization is safe: Corollary 3.4 records `Q_id(1/n) in [C^(-1), C]` for `n >= q^kappa`, after increasing constants.  Thus direct numerator savings survive normalization in that range.

Outside this range, denominator control is a real obstruction.  A zero of `Q_id(1/n)` makes the ratio undefined, and a near-zero denominator with loss `D` changes the saving from `(2 kappa-A)eta+sigma` to `(2 kappa-A)eta+sigma-D`.  The M36 denominator grid records exactly when this loss erases a nominal direct gain.

## Lemma 3.3 Range

Lemma 3.3 is stated for `1/n in [0,(Cq)^(-C)]`.  Corollary 3.4 is then formulated for `n >= q^kappa`; this is compatible after choosing `kappa` and constants large enough relative to the Lemma 3.3 exponent.  Therefore the direct target is not forced outside the paper-proved range at the boundary `n=Cq^kappa`, but it cannot use values below that boundary without new input.

## Relation to Coefficient Variation

Direct small-`x` control is logically weaker than coefficient variation because it only asks for one denominator-normalized value at `x=1/n`; signed cancellation can occur at that point without bounded coefficient variation.  It is not automatically easier.  Any proof from fixed-pair `Q_{gamma1,gamma2}` estimates alone still needs aggregate signed control over geodesic weights, folded quotient families, denominator normalization, and the surface-group probability law.

Thus M36 classifies direct evaluation as a distinct conditional route, but only if a new surface-group ratio estimate is proved.  If the only available method expands and bounds coefficients or total variation, the route collapses back into a coefficient-variation theorem.

## Special Points

| point | conclusion |
|---|---|
| `x=0` | `P(0)=0` is useful for Taylor in the existing proof, but value control at zero alone does not bound `p(1/n)/Q_id(1/n)`. |
| `x=1/n` | This is the actual target point and must remain denominator-normalized. |
| `n=Cq^kappa` | This is compatible with Lemma 3.3 only after constants are chosen as in Corollary 3.4; it is the hard boundary for direct replacement. |
| `q->infinity` | Degree and quotient-family complexity grow as `deg p=O(Lambda0^(-1/2)q)`. |
| fixed `Lambda0` | Isolates the trace-side `q` exponent. |
| high `Lambda0` | M36 preserves the paper factor `Lambda0^20`; it does not prove high-energy improvement. |
| `Q_id(1/n)=0` | Excluded by the paper range but fatal outside it. |
| `Q_id(1/n)` near-zero | Modeled by denominator loss `D`; this can erase every direct numerator saving. |

## Decision

Direct small-`x` evaluation remains a credible independent theorem target only in the precise ratio form above.  It is not implied by M30-M33 Schreier benchmarks or independent-permutation template evidence, and M36 gives no exponent improvement without a new surface-group estimate for `p(1/n)/Q_id(1/n)`.
