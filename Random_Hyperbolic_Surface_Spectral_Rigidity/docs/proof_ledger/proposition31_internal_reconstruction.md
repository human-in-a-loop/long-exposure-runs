---
created: 2026-05-15T16:12:00Z
cycle: 3
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Proposition 3.1 Internal Reconstruction

## Scope

This note reconstructs Kim--Tao Proposition 3.1 from local paper §3.2. It treats the theorem-level smoothing, Chebyshev conversion, grid union bound, and Weyl inversion as downstream material already recorded in `theorem1_exponent_flow.md` and `weyl_inversion_detail.md`. I keep `alpha_W` for the later Weyl-law exponent and `alpha_R` for the post-inversion rigidity exponent; neither is created inside Proposition 3.1.

## Target Statement

Let `h(x)=x htilde(x)` be a polynomial of degree `q`. Proposition 3.1 states that there are `kappa=kappa(g)>2` and `C=C(X)>0` such that, for `Lambda0 >= C`,

```text
E | n^{-1} tr(h o f_Lambda0)(sqrt(Delta_Xn - 1/4))
    - Vol(X_n)/(2 pi n) int_0^infty (h o f_Lambda0)(r) r tanh(pi r) dr |^2
  <= C Lambda0^2 q^{2 kappa} n^{-1} ||htilde||^2.
```

The proposition is proved by applying the twisted Selberg trace formula, reducing the centered statistic to a random geodesic trace sum, approximating its second moment by a polynomial in `1/n`, and then using Markov brothers' inequality to move from control on reciprocal integer points to control at the desired cover degree.

## Mechanism

Define the geodesic-side random sum

```text
S_n := sum_{gamma in P(X)} sum_{k>=1}
       ell_gamma(X) / (2 sinh(k ell_gamma(X)/2))
       (h o f_Lambda0)^vee(k ell_gamma(X)) tr rho(gamma^k).
```

Equation (3.13) identifies the variance target with `n^{-2} E S_n^2`. Expanding the square gives a double sum over `(gamma_1,k_1),(gamma_2,k_2)` weighted by deterministic Selberg coefficients and by

```text
E[tr rho(gamma_1^{k_1}) tr rho(gamma_2^{k_2})].
```

Thus all randomness is pushed into two-trace permutation statistics.

The uniform bound (3.14), proved from the spectral side and Lemma 2.3, gives

```text
n^{-2} E S_n^2 <= C Lambda0^2 ||htilde||^2.
```

This has no useful `1/n` gain, but it is strong enough when `n <= 2 C q^kappa`, since then `1 <= 2 C q^kappa/n` and the desired Proposition 3.1 bound follows after increasing constants. The hard case is `n >= 2 C q^kappa`.

## Lemma 3.3: Two-Trace Polynomialization

Lemma 3.3 is the paper-specific adaptation of the MPvH polynomial method from one trace to two traces. For nontrivial `gamma_1,gamma_2` with `|gamma_1|+|gamma_2| <= q`, it proves that for `1/n in [0,(Cq)^{-C}]`,

```text
E[tr rho(gamma_1) tr rho(gamma_2)]
  = Q_{gamma_1,gamma_2}(1/n) / Q_id(1/n) + O((Cq)^{Cq} n^{-q}),
```

with

```text
deg Q_{gamma_1,gamma_2} <= 9 q (4g+1),
deg Q_id <= 9 q (4g+1)+1,
Q_id(1/n) in [C^{-1}, C] for n >= q^C.
```

The proof builds a folded labeled graph `C_{gamma_1,gamma_2}` made from two disjoint labeled cycles. A fixed point of `rho(gamma_1)` and a fixed point of `rho(gamma_2)` are exactly a morphism from this two-cycle graph into the Schreier graph of the random cover. Each morphism factors through a finite folded quotient `W_r`, so the expectation becomes a finite sum of expected injective embeddings `E_n^emb(W_r)`.

The imported MPvH estimate gives each embedding expectation as a rational expression in `n`, up to `O((Cq)^{Cq} n^{-q})`, after summing over at most `(|gamma_1|+|gamma_2|)!` quotient maps. The conversion to a rational function of `t=1/n` uses the falling factorial denominator and Witten zeta normalization. The external input `[Nau26, Proposition 3.1]` gives boundedness of the two-trace expectation as `n -> infinity`; this kills possible `t^{-1}` and `t^{-2}` terms and leaves an honest polynomial numerator.

## Corollary 3.4: Polynomial for the Full Second Moment

Corollary 3.4 inserts Lemma 3.3 into the double geodesic sum. It defines

```text
p(x) := sum_{gamma_1,gamma_2,k_1,k_2}
        a(gamma_1,k_1) a(gamma_2,k_2)
        (h o f_Lambda0)^vee(k_1 ell_gamma1)
        (h o f_Lambda0)^vee(k_2 ell_gamma2)
        Q_{gamma_1^{k_1}, gamma_2^{k_2}}(x),
```

where `a(gamma,k)=ell_gamma/(2 sinh(k ell_gamma/2))`. Then, for `n >= q^kappa` and `Lambda0 >= C`,

```text
E S_n^2 = p(1/n)/Q_id(1/n)
          + O(Lambda0 (Cq)^{kappa q} n^{-q} ||htilde||^2),
```

and

```text
deg p <= C Lambda0^{-1/2} q,
Q_id(1/n) in [C^{-1},C].
```

The degree drops from the formal `O(q)` scale in Lemma 3.3 to `O(Lambda0^{-1/2} q)` because `(h o f_Lambda0)^vee` is supported in `[-c0 Lambda0^{-1/2}, c0 Lambda0^{-1/2}]`. If a term is nonzero then `k ell_gamma(X) <= c0 Lambda0^{-1/2} q`, and the length-word comparison (3.19) gives `|gamma^k| <= C Lambda0^{-1/2} q`. Taking `Lambda0` large enough ensures this is at most `q/2`, so Lemma 3.3 applies with room left for the `n^{-q}` error.

The error is harmless in the hard range because `n >= q^kappa` with `kappa` chosen large. The deterministic coefficient sum contributes the visible `Lambda0 ||htilde||^2` factor in Corollary 3.4's error, while the main proposition's final `Lambda0^2` scale comes from the spectral-side bound (3.21)/(3.22).

## Markov Step

Equation (3.21) restates the uniform spectral bound as

```text
n^{-2} E S_n^2 <= C Lambda0^2 ||htilde||^2.
```

Combining Corollary 3.4 with this gives pointwise control at reciprocal integer points:

```text
n^{-2} |p(1/n)| <= C Lambda0^2 ||htilde||^2,
qquad n >= C q^kappa.              (3.22)
```

The polynomial to which Lemma 3.5 is applied is not `p` but

```text
P(x) = x^2 p(x).
```

On the interval `[0, 1/(2 C q^kappa)]`, Markov brothers' inequality in the form (3.20) gives

```text
||P'|| <= C q^{2 kappa} sup_{n >= C q^kappa} |P(1/n)|
       <= C q^{2 kappa} Lambda0^2 ||htilde||^2.
```

The displayed `q^{2 kappa}` is the decisive Proposition 3.1 loss. It is a derivative-amplification loss from controlling a polynomial on the mesh of reciprocal integer points near `0`; the earlier geometric and polynomialization steps do not already contain this final power.

For `n >= 2 C q^kappa`, Taylor expansion from `0` to `1/n` yields

```text
|n^{-2} p(1/n)/Q_id(1/n)|
  <= n^{-1} ||(x^2 p(x))'||_{[0,1/(2 C q^kappa)]}
  <= C Lambda0^2 q^{2 kappa} n^{-1} ||htilde||^2.
```

Adding the Corollary 3.4 error gives the desired bound in the hard range. The easy range `n <= 2 C q^kappa` follows from the uniform bound (3.14), completing Proposition 3.1.

## Dependency and Loss Table

| Source statement | Input type | Quantitative parameters | Output estimate | Loss introduced |
|---|---|---|---|---|
| Selberg trace formula (2.2), equation (3.13) | standard trace formula plus random cover representation | `Lambda0`, `q`, `n`, geodesic pairs | variance becomes `n^{-2} E S_n^2` | no loss; exact reduction |
| Uniform bound (3.14) / (3.21) | spectral side plus Lemma 2.3 | `Lambda0`, `||htilde||` | `n^{-2} E S_n^2 <= C Lambda0^2 ||htilde||^2` | loses possible cancellation; no `1/n` gain |
| Lemma 3.3 | imported MPvH embedding expansion adapted to two cycles, plus Witten zeta and Nau boundedness | `|gamma_1|+|gamma_2| <= q`, `1/n <= (Cq)^{-C}` | two-trace expectation equals `Q_pair/Q_id + O((Cq)^{Cq} n^{-q})` | polynomial degree `O_g(q)`, large but exponentially small error coefficient |
| Corollary 3.4 | Lemma 3.3 plus Fourier support and length-word comparison | support `k ell_gamma <= c0 Lambda0^{-1/2} q` | `E S_n^2 = p(1/n)/Q_id(1/n)+error`, `deg p <= C Lambda0^{-1/2}q` | coefficient/error sum costs `Lambda0`; degree governed by support |
| Integer-point control (3.22) | Corollary 3.4 plus uniform bound | `n >= C q^kappa` | `n^{-2}|p(1/n)| <= C Lambda0^2 ||htilde||^2` | converts probabilistic bound into polynomial sample bound |
| Lemma 3.5 Markov brothers | polynomial inequality | applied to `P=x^2 p` on `[0,1/(2Cq^kappa)]` | `||P'|| <= C q^{2kappa} Lambda0^2 ||htilde||^2` | dominant visible `q^{2kappa}` loss |
| Taylor step | calculus plus `Q_id` bounded below | `n >= 2C q^kappa` | `n^{-2}p(1/n)/Q_id(1/n) <= C Lambda0^2 q^{2kappa} n^{-1}||htilde||^2` | one `1/n` gained from interval length |
| Small-`n` fallback | uniform bound | `n <= 2Cq^kappa` | target follows since `q^{2kappa}/n >= c q^kappa` | crude but sufficient |

## Structural vs Technical Losses

The two-trace expansion is structural: the variance genuinely asks for common fixed-point statistics of two words, encoded by the two-cycle graph `C_{gamma_1,gamma_2}` and its folded quotients. The support-to-degree reduction is also structural for compactly supported Selberg transforms.

The `q^{2kappa}` loss is likely technical/non-optimized at this level. It appears when Lemma 3.5 extends discrete reciprocal-point bounds to a uniform derivative bound for `x^2 p(x)`. The paper's own proof idea isolates this as the final polynomial-method step, and the earlier geodesic counting does not already force `q^{2kappa}`. A sharper interpolation or more direct control of `p(1/n)` might lower this visible power, but that would require auditing the imported MPvH Markov lemma rather than only the local paper.

## Diagnostic Outcomes

1. The main hidden loss in Proposition 3.1 is ruled in as polynomial derivative amplification: `q^{2kappa}` enters at Lemma 3.5 applied to `x^2 p(x)`.
2. The two-trace expansion does isolate randomness into common fixed-point / Schreier embedding statistics; geometry contributes support and coefficient size, but not the final `q^{2kappa}`.
3. The loss is plausibly technical rather than structural, conditional on the imported Markov lemma being replaceable. No local-paper evidence shows that the `q^{2kappa}` exponent is sharp.

## Next Proof-Ledger Target

The next target should be Theorem 2's pre-trace/fourth-moment reconstruction, especially Proposition 4.1 and the diagonal term `S`. If remaining in Proposition 3.1, the only deeper audit target is external: unpack the MPvH embedding estimate and Lemma 3.5, which is outside the local-paper-first reconstruction completed here.
