---
created: 2026-05-15T16:13:00Z
cycle: 3
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Two-Trace Expansion Ledger

## Question

How does the variance of the centered normalized twisted trace reduce to a double geodesic sum and then to common fixed-point statistics?

## Expansion

With `h(x)=x htilde(x)`, the twisted Selberg trace formula (2.2) gives the centered spectral statistic as the geodesic sum

```text
n^{-1} S_n =
n^{-1} sum_{gamma in P(X)} sum_{k>=1}
      ell_gamma(X) / (2 sinh(k ell_gamma(X)/2))
      (h o f_Lambda0)^vee(k ell_gamma(X)) tr rho(gamma^k).
```

Squaring and taking expectation gives equation (3.13):

```text
n^{-2} sum_{gamma_1,gamma_2 in P(X)} sum_{k_1,k_2>=1}
  a(gamma_1,k_1) a(gamma_2,k_2)
  (h o f_Lambda0)^vee(k_1 ell_gamma1)
  (h o f_Lambda0)^vee(k_2 ell_gamma2)
  E[tr rho(gamma_1^{k_1}) tr rho(gamma_2^{k_2})],
```

where `a(gamma,k)=ell_gamma(X)/(2 sinh(k ell_gamma(X)/2))`.

This is the exact place where the variance becomes a two-trace problem.

## Common Fixed-Point Interpretation

For any two words `gamma_1,gamma_2`,

```text
tr rho(gamma_1) tr rho(gamma_2)
  = Fix(phi(gamma_1)) Fix(phi(gamma_2)).
```

Lemma 3.3 encodes this product as the number of morphisms from a labeled graph
`C_{gamma_1,gamma_2}` into the random Schreier graph. Here
`C_{gamma_1,gamma_2}` is the disjoint union of two directed labeled cycles spelling the cyclically reduced words for `gamma_1` and `gamma_2`.

Every folded labeled morphism factors uniquely as

```text
C_{gamma_1,gamma_2} ->> W_r -> X_phi,
```

where the first map is a surjective quotient and the second is an injective morphism into the Schreier graph. Hence

```text
E[tr rho(gamma_1) tr rho(gamma_2)]
  = sum_{r in R} E_n^emb(W_r).
```

This is the local-paper version of the common fixed-point reduction: all randomness is now in expected injective embeddings of finite folded quotient graphs.

## Polynomial Output

The imported MPvH embedding expansion and the Witten-zeta normalization imply

```text
E[tr rho(gamma_1) tr rho(gamma_2)]
  = Q_{gamma_1,gamma_2}(1/n)/Q_id(1/n)
    + O((Cq)^{Cq} n^{-q})
```

whenever `|gamma_1|+|gamma_2| <= q` and `1/n <= (Cq)^{-C}`. The degree bounds are

```text
deg Q_{gamma_1,gamma_2} <= 9q(4g+1),
deg Q_id <= 9q(4g+1)+1.
```

The boundedness input `[Nau26, Proposition 3.1]` is used only to remove possible negative powers of `t=1/n`; without it the expression obtained from falling factorials could contain `t^{-1}` and `t^{-2}` terms.

## Identity, Diagonal, and Non-Diagonal Terms

The paper states Lemma 3.3 for `gamma_1,gamma_2 != id`; identity contributions are not part of the geodesic side because the identity term has already been subtracted into the volume integral on the spectral side. Thus the relevant expansion is over nontrivial primitive geodesic powers.

Diagonal pairs such as `gamma_1^{k_1}=gamma_2^{k_2}` are not isolated by a separate probabilistic lemma in §3.2. They are included in the same two-cycle graph formalism and enter the polynomial `Q_{gamma_1^{k_1},gamma_2^{k_2}}`. Their larger correlation is therefore absorbed into `p(1/n)` and later bounded by the spectral-side estimate plus Markov.

Genuinely non-diagonal correlated pairs are also encoded by quotient graphs `W_r`: any common fixed point or overlap pattern appears as a folded quotient of the two disjoint cycles. This is the exact analogy with random regular graph trace methods, except the ambient group is the surface group and the normalization includes the Witten zeta factor for `Hom(Gamma,S_n)`.

## Loss Accounting

| Step | Parameter effect | Interpretation |
|---|---|---|
| Two-cycle graph `C_{gamma_1,gamma_2}` | `#R <= (|gamma_1|+|gamma_2|)!` | combinatorial complexity absorbed into `(Cq)^{Cq}` error |
| MPvH embedding expansion | degree `<= 9q(4g+1)+2` before cleanup | imported polynomial-method machinery |
| Rational-to-polynomial cleanup | kills `t^{-1},t^{-2}` using boundedness | paper relies on external boundedness, not a new local estimate |
| Fourier support of `(h o f_Lambda0)^vee` | `k ell_gamma <= c0 Lambda0^{-1/2} q` | truncates geodesic powers |
| Length-word comparison (3.19) | `|gamma^k| <= C Lambda0^{-1/2}q` | converts geometric support to word-length input for Lemma 3.3 |
| Geodesic coefficient sum | `O_X(e^{2q} Lambda0 ||htilde||^2)` before absorption | contributes to Corollary 3.4 error, not final `q^{2kappa}` |

## Conclusion

The two-trace expansion supports the diagnostic hypothesis: after the Selberg trace formula, all nontrivial randomness is reduced to common fixed-point statistics of two words. The local geometric contribution sets support and coefficient sizes. The final `q^{2kappa}` loss is not already present in this expansion; it enters later through Markov derivative control.
