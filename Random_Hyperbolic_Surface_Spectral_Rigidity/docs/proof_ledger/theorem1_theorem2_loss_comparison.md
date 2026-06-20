---
created: 2026-05-15T16:38:00Z
cycle: 4
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Theorem 1 / Theorem 2 Loss Comparison

## Purpose

This note compares the validated Theorem 1 proof-ledger slices against the Theorem 2 delocalization reconstruction. It is a diagnostic bridge, not a new proof.

## Side-By-Side Losses

| Layer | Theorem 1 Eigenvalue Rigidity | Theorem 2 Eigenfunction Delocalization |
|---|---|---|
| Analytic formula | Selberg trace formula | twisted pre-trace formula |
| Centered object | global trace count minus volume term | local spectral mass minus local Weyl term |
| Proposition-level estimate | Proposition 3.1: variance `<= Lambda0^2 q^{2kappa} n^{-1}` | Proposition 4.1: local fourth statistic `<= Lambda0^8 q^{4kappa} n^{-2}` |
| Polynomial statistic | two-trace common fixed points | eight-word common fixed points after diagonal removal |
| Diagonal issue | identity/volume term removed by trace formula centering | primitive-power diagonal `S` must be subtracted |
| Markov loss | first derivative of `x^2 p(x)`, `q^{2kappa}` | second derivative of `x^2 p(x)`, `q^{4kappa}` |
| Smooth derivative order | `m = kappa+3+K`, with `K ~ epsilon^{-1}` | `2kappa+11` |
| Chosen theorem exponent | `alpha0=1/(3m)` before Weyl inversion | `alpha0=1/(16(2kappa+11))`, final `alpha=alpha0/2` |
| Probability conversion | Chebyshev plus spectral grid | Chebyshev plus fiber union plus spectral grid |
| Final analytic degradation | Weyl inversion near `1/4`, roughly `2/3` exponent loss | Sobolev/elliptic conversion gives `Lambda^{3/2}` |

## Main Similarity

Both proofs use the same macro-template:

```text
compactly supported transform
-> exact trace/pre-trace expansion
-> polynomial approximation in 1/n
-> Markov brothers interpolation
-> Chebyshev and grid union
```

This supports the hypothesis that polynomial-method interpolation is a shared bottleneck across rigidity and delocalization.

## Main Difference

Theorem 2 requires a genuinely local fourth-moment mechanism. The subtraction `S` is needed before the common-fixed-point input gives the `n^{-2}` scale, and the final local mass estimate still has to pass through Sobolev/elliptic regularity. Thus Theorem 2 has two extra losses absent from Theorem 1: the fiber union and the analytic local-mass-to-`L^\infty` conversion.

## Extension Signal

If one wants to improve the `n` exponent, the visible targets are still the Markov interpolation powers and the smooth-window derivative budget. If one wants to improve the `Lambda` exponent in (1.7), the most direct local-paper target is not Proposition 4.1 alone but the last deterministic step converting

```text
int a|u_j|^2 <= Lambda0 n^{-alpha0}
```

into

```text
||u_j||_infty^2 <= Lambda0^3 n^{-alpha0}.
```

The paper already records an interpolation route to `Lambda^{1/4+epsilon}` at the cost of changing the `n` exponent.
