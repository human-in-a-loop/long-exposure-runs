---
created: 2026-05-16T23:59:55Z
cycle: 46
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M35-surface-corollary34-numerator-obstruction
---

# Surface Corollary 3.4 Numerator Obstruction

## Purpose

This note returns to the actual Kim--Tao Lemma 3.3 / Corollary 3.4 object after the fixed-window M34 corollary. The goal is not to prove a new numerator theorem, but to state exactly what the current paper proves, where the `q^{2 kappa}` trace-side loss enters, and which replacements would require new surface-group quotient-family input.

## Exact Paper Object

Proposition 3.1 studies the Selberg trace statistic

```text
G_n(h)
  = sum_{gamma in P(X)} sum_{k>=1}
      ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))
      (h o f_Lambda0)^vee(k ell_gamma(X))
      tr rho(gamma^k).
```

The second moment expands into a two-trace weighted sum over `gamma1,gamma2 in P(X)` and `k1,k2 >= 1`. Lemma 3.3 states that for nontrivial surface-group elements with `|gamma1|+|gamma2| <= q`,

```text
E[tr rho(gamma1) tr rho(gamma2)]
  = Q_{gamma1,gamma2}(1/n) / Q_id(1/n)
    + O((Cq)^(Cq) n^(-q)),
```

valid for `1/n in [0,(Cq)^(-C)]`, in particular for `n >= q^C` after enlarging constants. The polynomial degrees satisfy

```text
deg Q_{gamma1,gamma2} <= 9q(4g+1),
deg Q_id <= 9q(4g+1)+1,
Q_id(1/n) in [C^(-1), C] for n >= q^C.
```

Corollary 3.4 inserts the Selberg/geodesic weights and defines the weighted numerator

```text
p(x)
 = sum_{gamma1,gamma2 in P(X)} sum_{k1,k2>=1}
     ell_gamma1(X) ell_gamma2(X)
     ------------------------------------------------
     4 sinh(k1 ell_gamma1(X)/2) sinh(k2 ell_gamma2(X)/2)

     * (h o f_Lambda0)^vee(k1 ell_gamma1(X))
     * (h o f_Lambda0)^vee(k2 ell_gamma2(X))
     * Q_{gamma1^k1,gamma2^k2}(x).
```

Then

```text
E[G_n(h)^2]
  = p(1/n) / Q_id(1/n)
    + O(Lambda0 (Cq)^(kappa q) n^(-q) ||htilde||^2),
```

for `n >= q^kappa` and `Lambda0 >= C`. The transform support and word-length comparison imply

```text
deg p <= C Lambda0^(-1/2) q,
Q_id(1/n) in [C^(-1), C].
```

The support condition is encoded by `(h o f_Lambda0)^vee`; nonzero terms satisfy `k ell_gamma(X) <= c Lambda0^(-1/2) q`, hence `|gamma^k| <= C Lambda0^(-1/2) q`. Taking `Lambda0` large enough makes the Lemma 3.3 word-length condition fit inside the parameter `q`.

## Where `q^{2 kappa}` Enters

The uniform spectral-side estimate gives reciprocal-integer control:

```text
n^(-2) |p(1/n)| <= C Lambda0^20 ||htilde||^2,
qquad n >= C q^kappa.
```

The proof then applies the Markov brothers inequality to

```text
P(x) = x^2 p(x).
```

On the small interval `[0, 1/(2C q^kappa)]`, this yields

```text
||(x^2 p(x))'|| <= C q^(2 kappa) Lambda0^20 ||htilde||^2.
```

Taylor expansion from `0` to `1/n`, using `P(0)=0`, gives

```text
n^(-2) |p(1/n)| / |Q_id(1/n)|
  <= C q^(2 kappa) Lambda0^20 n^(-1) ||htilde||^2
```

for the hard range `n >= 2C q^kappa`. Thus the visible `q^(2 kappa)` loss appears at reciprocal-integer interpolation/Markov derivative control of `x^2 p(x)`, not at the point where Corollary 3.4 merely defines the weighted numerator.

## Replacement Targets

A theorem-level replacement must control the paper-defined `p(1/n)/Q_id(1/n)`, or a localized version of the same object, without relying on the Markov derivative envelope.

One possible coefficient-variation target writes

```text
p(x) = sum_m c_m x^m
```

and proves that the actual Selberg-weighted surface-group aggregate has controlled absolute or signed coefficient variation at `x=1/n`. Termwise product-ratio bounds are insufficient unless the geodesic weights, quotient-family count, signs, denominator normalization, and surface-group probability law are all controlled together.

A direct small-`x` target bypasses coefficient variation:

```text
|p(1/n)| / |Q_id(1/n)| <= n q^A n^(-sigma+o(1)).
```

This could use cancellation invisible to coefficient norms, but it is stronger and less structured. Cancellation at `x=0` alone is not enough; the target point is `x=1/n` in the range `n >= q^kappa`.

The M22 beta algebra is unchanged. If a future theorem gives

```text
E G_n(h)^2 <= n q^A n^(-sigma+o(1)),
```

then the numerator saving relative to the current trace baseline is

```text
beta = (2 kappa - A) eta + sigma,
```

after substituting `q=n^eta`. For the local-window branch this would need

```text
beta > 2 kappa eta + 2d - 1.
```

M35 does not prove such a beta saving.

## Special Points

| Point | Classification | Check |
|---|---|---|
| `x=0` | vacuous alone | `P(0)=0` is used by Taylor, but a numerator expansion at zero does not bound `p(1/n)/Q_id(1/n)` without coefficient or neighborhood control. |
| `x=1/n` | target point | This is the actual evaluation point in Lemma 3.3/Corollary 3.4 and must remain in the range `n >= q^kappa`. |
| `n=q^kappa` | boundary | This is the hard/easy boundary where reciprocal sample control starts and the Markov mesh argument is invoked. |
| `q -> infinity` | growing complexity | `deg p <= C Lambda0^(-1/2)q` and the folded quotient/geodesic support grow with `q`. |
| fixed `Lambda0` | isolates trace loss | Holding energy fixed isolates the trace-side `q` loss. |
| high `Lambda0` | not solved here | The current statement retains existing energy factors and does not prove uniform high-energy improvement. |
| `Q_id(1/n)` | normalization required | Numerator savings are meaningful only after the denominator is bounded away from zero, as in the paper's range. |

## No Transfer From Schreier Benchmarks

M30-M33 prove a standalone two-permutation Schreier benchmark: fixed-k trace moments and normalized variance behave well in an independent random-permutation model. That theorem does not imply any Kim--Tao surface numerator estimate. The surface problem uses the surface-group relation, MPvH/Witten-zeta normalization, Nau boundedness, the denominator `Q_id`, geodesic Selberg weights, and a growing folded quotient-family sum. M35 therefore treats Schreier evidence as analogy only, never as a proof input for `p(x)/Q_id(x)`.

## Generated Ledger

The executable classifier is:

```text
scripts/analyze_surface_corollary34_numerator_obstruction.py
```

It writes:

```text
data/extension_candidates/m35_interpolation_loss_budget.csv
data/extension_candidates/m35_candidate_mechanism_classification.csv
data/extension_candidates/m35_surface_input_gap_matrix.csv
data/extension_candidates/m35_direct_vs_markov_regime_grid.csv
```

and figures:

```text
reports/figures/m35_corollary34_interpolation_loss.png
reports/figures/m35_mechanism_dependency_graph.png
reports/figures/m35_direct_vs_coefficient_variation_map.png
```
