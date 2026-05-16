---
created: 2026-05-15T17:05:00Z
cycle: 5
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Theorem 1 Rigidity Proof Reconstruction

## Scope

This note consolidates the validated Cycle 2 and Cycle 3 proof-ledger slices into the plan-required Theorem 1 rigidity reconstruction. It is not a new proof audit of the imported polynomial-method inputs; it records how the local Kim--Tao argument composes Proposition 3.1, smoothing, Chebyshev/grid probability, the Weyl law, and monotone inversion into eigenvalue rigidity.

## Theorem-Level Target

For every `epsilon > 0`, Kim--Tao Theorem 1 asserts that there are `alpha=alpha(g,epsilon)>0` and `C=C(X,epsilon)>0` such that, with probability at least `1-n^{-1/10}`, for all `Lambda >= 1/4` and all eigenvalues `lambda_j(X_n) in [1/4,Lambda]`,

```text
|lambda_j(X_n)-lambda_j|
  <= C Lambda^{1/2+epsilon} n^{-alpha},
```

where the comparison point `lambda_j` is defined by

```text
int_0^{sqrt(lambda_j-1/4)} r tanh(pi r) dr = j/(n(2g-2)).
```

The proof proceeds through a uniform Weyl law with exponent `alpha_W`, then possibly weakens the exponent to a rigidity exponent `alpha_R` during inversion near the spectral edge `1/4`.

## Proposition 3.1 Input

The proposition-level estimate is the variance bound for polynomial test functions `h(x)=x htilde(x)` of degree `q`:

```text
E | n^{-1} tr((h o f_Lambda0)(sqrt(Delta_Xn - 1/4)))
    - Vol(X_n)/(2 pi n) int_0^infty (h o f_Lambda0)(r) r tanh(pi r) dr |^2
 <= C Lambda0^2 q^{2 kappa} n^{-1} ||htilde||^2.
```

Its internal mechanism is recorded in `proposition31_internal_reconstruction.md`, `two_trace_expansion_ledger.md`, and `markov_loss_reconstruction.md`:

1. Selberg trace formula turns the centered trace statistic into `n^{-2} E S_n^2`.
2. Expanding `S_n^2` leaves expectations of two permutation traces, `E[tr rho(gamma_1) tr rho(gamma_2)]`.
3. Lemma 3.3 polynomializes these two-trace expectations as rational functions of `1/n`, using folded two-cycle graphs and imported MPvH/Nau inputs.
4. Corollary 3.4 assembles the full second moment into `p(1/n)/Q_id(1/n)` plus a negligible error, with degree controlled by Fourier support and length-word comparison.
5. Markov brothers' inequality is applied to `P(x)=x^2 p(x)` near `x=0`, giving the visible `q^{2 kappa}` derivative-amplification loss.

This is proposition-level, not theorem-level, work. It supplies the random-cover concentration estimate that the later smoothing and probability argument consumes.

## Smooth Cutoff And Weyl Law

The theorem-level passage starts by rewriting Proposition 3.1 as, for every `K >= 0`,

```text
variance <= C_K n^{-1} Lambda0^{-K} ||htilde||_{C^{kappa+3+K}}^2.
```

Choose

```text
K = floor((kappa + 5)/(2 epsilon)) + 1,
m = kappa + 3 + K,
alpha_0 = 1/(3m).
```

The smooth cutoff around `Lambda` has transition width

```text
Delta Lambda = Lambda^{1/2+epsilon} n^{-alpha_0},
```

and derivative growth

```text
|partial_x^j htilde_{Lambda,epsilon}(x)|
  <= C_j Lambda^{j(1/2-epsilon)} n^{j alpha_0}.
```

Inserting the `C^m` norm in the variance estimate gives

```text
variance
 <= C n^{-1} Lambda0^{-K}
    Lambda^{2m(1/2-epsilon)} n^{2m alpha_0}.
```

The choice `alpha_0=1/(3m)` makes the `n` exponent equal to `-1/3`. The choice of `K` forces the large-energy `Lambda` exponent below `-2`, so uniformly for `Lambda >= 1/4`,

```text
E |Z_Lambda|^2 <= C Lambda^{-2} n^{-1/3}.
```

Chebyshev at threshold `n^{-1/9}` gives fixed-`Lambda` failure probability

```text
P(|Z_Lambda| > C n^{-1/9})
  <= C Lambda^{-2} n^{-1/9}.
```

On this event, smoothing converts the trace statistic into the normalized Weyl count with deterministic cutoff error

```text
O(Lambda^{1/2+epsilon} n^{-alpha_0})
```

and probabilistic error `O(n^{-1/9})`. Hence, for fixed `Lambda`,

```text
|N_Xn(Lambda) - n(2g-2)F(Lambda)|
  <= C n^{1-alpha_W} Lambda^{1/2+epsilon},
```

with `alpha_W <= min(alpha_0,1/9)`, where

```text
F(Lambda)=int_0^{sqrt(Lambda-1/4)} r tanh(pi r) dr.
```

## Uniform Probability Grid

The fixed-`Lambda` estimate is made simultaneous by the grid

```text
Lambda(j)=C2^j,
Lambda(j,l)=Lambda(j)+l n^{-0.01} Lambda(j)^{1/2}.
```

For each dyadic level, the number of grid points is `O(n^{0.01}2^{j/2})`, while the failure probability contributes `O(2^{-2j}n^{-1/9})`. The dyadic sum converges and the `n` exponent is

```text
0.01 - 1/9 = -91/900 < -1/10.
```

Monotonicity of `N_Xn` and the grid spacing extend the Weyl law from grid points to all `Lambda`, after reducing `alpha_W` if needed so that `alpha_W <= 0.01`.

## Rigidity Inversion

The final step inverts the Weyl law. Since

```text
F'(Lambda) = (1/2)tanh(pi sqrt(Lambda-1/4)),
```

`F` is Lipschitz-invertible away from the edge but only Hölder-invertible at `Lambda=1/4`. The edge expansion

```text
F(1/4+t) = (pi/3)t^{3/2} + O(t^{5/2})
```

implies the uniform inverse estimate

```text
|F^{-1}(y+delta)-F^{-1}(y)| <= C |delta|^{2/3}.
```

The Weyl law gives

```text
|F(lambda_j(X_n))-F(lambda_j)|
  <= C n^{-alpha_W} Lambda^{1/2+epsilon},
```

up to the below-edge index offset `N_Xn(1/4) <= C n^{1-alpha_W}`. Therefore the rigidity exponent should be tracked separately:

```text
alpha_R < 2 alpha_W / 3
```

is always safe near the edge, while away from `1/4` one can retain the stronger Weyl exponent. The theorem only asserts existence of a positive exponent, so this weakening is harmless but important for the proof ledger.

## Dependency Classification

| Layer | Status | Artifact(s) | Caveat |
|---|---|---|---|
| Selberg trace and proposition target | proposition-level | `proposition31_internal_reconstruction.md` | uses standard trace formula and local paper normalization |
| Two-trace polynomialization | imported plus local adaptation | `two_trace_expansion_ledger.md` | MPvH embedding expansion and Nau boundedness remain black boxes |
| Markov interpolation | technical polynomial-method step | `markov_loss_reconstruction.md` | source of visible `q^{2 kappa}` loss |
| Smooth cutoff conversion | theorem-level | `theorem1_exponent_flow.md` | derivative order `m=kappa+3+K` controls `alpha_0` |
| Chebyshev and grid | theorem-level | `theorem1_exponent_flow.md` | grid union contributes the final `n^{-1/10}` probability scale |
| Weyl inversion | theorem-level analytic conversion | `weyl_inversion_detail.md` | edge may weaken `alpha_W` to `alpha_R <= 2 alpha_W/3` |

## Diagnostic Outcome

The validated slices compose into a complete Theorem 1 reconstruction for `M2-proof-ledger`. The main local-paper losses are separated: Proposition 3.1 contributes `q^{2 kappa}` through Markov interpolation; the theorem-level smoothing contributes derivative order `m=kappa+3+K`; the grid contributes only probability loss; and edge inversion may weaken the Weyl exponent from `alpha_W` to `alpha_R`. Remaining black boxes are the imported MPvH/Nau polynomial-method inputs, which are outside the local reconstruction but are now explicitly identified for later external audit.
