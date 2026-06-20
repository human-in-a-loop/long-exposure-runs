---
created: 2026-05-15T16:14:00Z
cycle: 3
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Markov Loss Reconstruction

## Precise Polynomial and Interval

The Markov step in §3.2.3 applies Lemma 3.5 to

```text
P(x) = x^2 p(x),
```

where `p` is the polynomial from Corollary 3.4 approximating `E S_n^2`. The relevant interval is

```text
[0, 1/(2 C q^kappa)].
```

The data available before Markov is pointwise control at reciprocal integer points:

```text
|P(1/n)| = n^{-2}|p(1/n)| <= C Lambda0^2 ||htilde||^2,
qquad n >= C q^kappa.
```

The desired output is derivative control on the full interval near `0`.

## Lemma 3.5 Input

Lemma 3.5 states that for a real polynomial of degree at most `q` and `k in N`,

```text
sup_{t in [0, 1/(2 q^{2k})]} |P^{(k)}(t)|
  <= [2^{2k+1} q^{4k} / (2k-1)!!] sup_{n >= q^2} |P(1/n)|.
```

The proof uses this with `k=1`, after absorbing constants and replacing the lemma's `q` scale by a larger threshold comparable to `q^kappa`. In the notation of Proposition 3.1 this yields

```text
||(x^2 p(x))'||_{[0,1/(2Cq^kappa)]}
  <= C q^{2kappa} sup_{n >= C q^kappa} n^{-2}|p(1/n)|.
```

The degree of `p` is actually `<= C Lambda0^{-1/2}q`, but the argument does not exploit this to improve the final exponent; it packages the reciprocal-mesh scale as the `q^kappa` threshold.

## Why a `D^2` Derivative Penalty Is Natural

Classical Markov brothers on `[-1,1]` says a degree-`D` polynomial with sup norm `1` can have derivative of size `D^2`. Chebyshev polynomials saturate this:

```text
T_D(1) = 1,
T_D'(1) = D^2.
```

After rescaling an interval of length `L`, derivative size also carries a factor `1/L`. Lemma 3.5 is a discrete reciprocal-point version of this principle: controlling a polynomial only on the set `{1/n}` near `0` still permits large derivative amplification, and the stated bound records that amplification as a power of the threshold scale.

The sanity script `scripts/check_markov_scaling.py` records `T_D'(1)=D^2` for small degrees and writes `data/polynomial_method/markov_scaling_sanity.csv`. The corresponding figure `markov_scaling_sanity.png` plots degree against derivative amplification on log-log axes.

## From Derivative to Proposition 3.1

For `n >= 2 C q^kappa`, Taylor's theorem gives

```text
|P(1/n)-P(0)| <= (1/n) ||P'||_{[0,1/(2Cq^kappa)]}.
```

Since `P(0)=0`, this becomes

```text
n^{-2}|p(1/n)| <= C Lambda0^2 q^{2kappa} n^{-1} ||htilde||^2.
```

Because `Q_id(1/n)` is bounded above and below, the same estimate applies to the rational main term `p(1/n)/Q_id(1/n)`. The Corollary 3.4 error is smaller in the hard range after choosing `kappa`, so the Markov step closes Proposition 3.1.

## Loss Diagnosis

| Candidate source | Ruled in/out | Reason |
|---|---|---|
| Polynomial degree from Lemma 3.3 | partial | creates a degree-controlled object but not yet `q^{2kappa}` |
| Geodesic counting | ruled out as dominant | contributes support and error-size factors, but no final `q^{2kappa}` |
| Markov derivative amplification | ruled in | the displayed derivative bound is exactly where `q^{2kappa}` appears |
| Interaction with small-`n` fallback | partial | fallback explains why the same bound is acceptable for `n <= 2Cq^kappa`, but does not create the hard-range loss |

## Conclusion

The Markov brothers step is the visible bottleneck inside Proposition 3.1. Replacing it with a sharper discrete interpolation estimate, or exploiting the smaller degree `C Lambda0^{-1/2}q`, is the most plausible local route to improving the proposition-level `q` exponent.
