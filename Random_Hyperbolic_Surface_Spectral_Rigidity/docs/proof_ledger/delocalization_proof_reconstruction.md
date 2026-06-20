---
created: 2026-05-15T16:35:00Z
cycle: 4
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Theorem 2 Delocalization Proof Reconstruction

## Scope

This note reconstructs Kim--Tao Theorem 2 from local paper §4. It uses the pre-trace formula and Proposition 4.1 as the eigenfunction-side analogue of the Theorem 1 trace argument, but keeps the exponents separate from the Weyl-law exponent `alpha_W` and rigidity exponent `alpha_R` recorded in earlier ledgers.

## Statement

Let `X` be a compact connected orientable hyperbolic surface of genus `g >= 2`. Theorem 2 states that there are `alpha=alpha(g)>0` and `C=C(X)>0` such that, with probability at least `1-n^{-1/10}`, every normalized eigenfunction

```text
Delta_Xn u_j = lambda_j(X_n) u_j,
||u_j||_L2(X_n) = 1
```

with `lambda_j(X_n) <= Lambda`, `Lambda >= 1/4`, satisfies

```text
||u_j||_Linf(X_n) <= C Lambda^{3/2} n^{-alpha} ||u_j||_L2(X_n).
```

The paper later notes that interpolation with the deterministic/trivial `Lambda^{1/4}` bound gives `Lambda^{1/4+epsilon} n^{-alpha(g,epsilon)}`.

## Pre-Trace Input

Lemma 2.2 gives the twisted pre-trace formula. For an even compactly supported `varphi`,

```text
sum_l varphi_hat(t_l^rho) u_l^rho(z,i) u_l^rho(w,j)
  = sum_{gamma in Gamma} rho_ij(gamma) K_varphi(z,gamma w).
```

At `w=z`, `i=j`, equation (2.5) splits off the identity contribution:

```text
sum_l varphi_hat(t_l^rho) |u_l^rho(z,i)|^2
  = (1/(2 pi)) int_0^infty varphi_hat(r) r tanh(pi r) dr
    + sum_{gamma != id} rho_ii(gamma) K_varphi(z,gamma z).
```

Thus the centered local spectral mass is a non-identity group sum, not a global trace. Lemma 2.4 gives the uniform pointwise bound

```text
|sum_l (h o f_Lambda0)(t_l^rho) |u_l^rho(z,i)|^2|
  <= C Lambda0 ||htilde||.
```

This replaces the trace-side uniform bound used in Proposition 3.1.

## V_n and Proposition 4.1

For `h(x)=x htilde(x)`, §4.1 defines

```text
V_n(h o f_Lambda0)(z,i)
  := ( sum_l h o f_Lambda0(t_l^rho) |u_l^rho(z,i)|^2
       - (1/(2 pi)) int_0^infty h o f_Lambda0(r) r tanh(pi r) dr )^4.
```

The centered sum in parentheses is the non-identity side of (2.5). Its fourth power is expanded into four non-identity kernel factors. The paper also defines a diagonal term `S(h o f_Lambda0)(z,i)` in (4.1), a sum where the four group elements are powers of one primitive element; see `pretrace_diagonal_term.md`.

Proposition 4.1 states that for any nonnegative `a in C_c^\infty(H)` with `int_H a dVol = 1`, for every fixed fiber `i`,

```text
E[ int_H a(z) (V_n(h o f_Lambda0)(z,i) - S(h o f_Lambda0)(z,i))^2 dVol(z) ]
  <= C Lambda0^8 q^{4 kappa} n^{-2} ||htilde||^8.
```

The proposition also has a multilinear version for four different polynomials `h_1,...,h_4`. That version is what justifies applying the estimate after decomposing smooth cutoffs into polynomial/Chebyshev pieces.

For smooth `h`, the same Chebyshev-coefficient conversion as in Theorem 1 rewrites this as (4.5):

```text
E[ int_H a(z) (V_n - S)^2 dVol(z) ]
  <= C Lambda0^{-2} n^{-2} ||htilde||_{C^{2 kappa + 11}}^8.
```

## Proposition-To-Theorem Exponent Flow

The theorem proof chooses

```text
alpha0 = 1 / (16(2 kappa + 11)).
```

For a spectral center `Lambda`, set `Lambda0=Lambda` for large `Lambda` and `Lambda0=C` below the fixed threshold. The smooth cutoff `h_Lambda` selects the window

```text
[Lambda, Lambda + (1+Lambda)n^{-alpha0}]
```

after allowing the one-window overlap/smoothing margin. Its derivatives satisfy

```text
|htilde_Lambda^{(j)}| <= C_j n^{j alpha0}.
```

Substituting `j=2 kappa+11` into (4.5) gives

```text
E[ int a(V_n-S)^2 ] <= C Lambda0^{-2} n^{-2+8(2 kappa+11)alpha0}
                   = C Lambda0^{-2} n^{-3/2}.
```

Chebyshev at threshold `n^{-1/4}` gives, for a fixed fiber `i`,

```text
P( int a(V_n-S)^2 > c n^{-1/4} )
  <= C Lambda0^{-2} n^{-5/4}.
```

Union over `i in [n]` gives fixed-window failure `<= C Lambda0^{-2} n^{-1/4}`. The same grid argument as Theorem 1, now covering windows of length `(1+Lambda)n^{-alpha0}`, yields simultaneous control for all fibers and all windows with total failure `<= n^{-1/10}` after taking the grid constant large.

## Local Mass Bound

On the high-probability event, equation (4.9) controls the local mass in each short spectral window:

```text
sum_{lambda_j in window} int_H a(z)|u_j^rho(z,i)|^2 dVol(z)
  <= int_0^infty h_Lambda o f_Lambda0(r) r tanh(pi r) dr
     + sup_z |S(h_Lambda o f_Lambda0)(z,i)|^{1/4}
     + n^{-1/32}.
```

The three terms are bounded by:

```text
identity/local Weyl term:  <= C Lambda0 n^{-alpha0},
diagonal term:            <= C Lambda0 n^{-alpha0},
fluctuation term:         <= n^{-1/32}.
```

Since `alpha0 <= 1/32`, this yields for every `lambda_j <= Lambda0` and every fiber `i`,

```text
int_H a(z)|u_j^rho(z,i)|^2 dVol(z) <= C Lambda0 n^{-alpha0}.
```

## L2-To-Linf Conversion

Choose a base fundamental domain `F`, a point `z0 in F`, and `R > diam(F)`, so `B(z0,R) x [n]` covers `X_n`. The cutoff `a` is strictly positive on `B(z0,R+2)`.

For each fiber coordinate,

```text
||u_j^rho(.,i)||_{Linf(B(z0,R))}^2
  <= C_R ||u_j^rho(.,i)||_{H^2(B(z0,R))}^2
  <= C_R ( ||u_j^rho||_{L2(B(z0,R+1))}^2
           + ||Delta_H u_j^rho||_{L2(B(z0,R+1))}^2 )
  <= C_R Lambda0^2 int_H a(z)|u_j^rho(z,i)|^2 dVol(z)
  <= C Lambda0^3 n^{-alpha0}.
```

Taking square roots gives

```text
||u_j||_Linf(X_n) <= C Lambda0^{3/2} n^{-alpha0/2}.
```

Thus Theorem 2 holds with `alpha=alpha0/2`.

## Loss Ledger

| Step | Scale introduced | Probability or analytic loss | Comment |
|---|---:|---:|---|
| Proposition 4.1 polynomial case | `Lambda0^8 q^{4 kappa} n^{-2}` | none yet | fourth-moment/pre-trace analogue of Proposition 3.1 |
| Smooth cutoff conversion (4.5) | `Lambda0^{-2}` and `C^{2kappa+11}` norm | derivative order `2kappa+11` | same smoothing technology as Theorem 1, but eighth power |
| Cutoff width | `n^{-alpha0}` | derivative growth `n^{(2kappa+11)alpha0}` to the eighth power | forces `alpha0=1/(16(2kappa+11))` |
| Chebyshev | threshold `n^{-1/4}` | fixed-fiber failure `Lambda0^{-2}n^{-5/4}` | squared fourth-moment statistic |
| Fiber union | factor `n` | fixed-window failure `Lambda0^{-2}n^{-1/4}` | new relative to global trace theorem |
| Window union | polynomial grid | final `1-n^{-1/10}` | parallel to Theorem 1 grid argument |
| Diagonal `S` | `Lambda0^4 n^{-4alpha0}` before fourth root | contributes `Lambda0 n^{-alpha0}` | controlled deterministically |
| Sobolev/elliptic step | multiply local mass by `Lambda0^2` | final square root gives `Lambda0^{3/2}` | dominant visible `Lambda` scale in (1.7) |

## Diagnostic Outcomes

Theorem 2 is structurally parallel to Theorem 1 only after replacing the global trace variance by a local fourth-moment/pre-trace statistic. The random-cover polynomial method still drives Proposition 4.1, but the proof introduces a new diagonal subtraction `S`, an eight-word common-fixed-point estimate, a fiber union bound, and a final analytic local-mass-to-sup-norm conversion.

The diagnostic hypothesis that the final `Lambda^{3/2}` is dominated by local-mass-to-pointwise conversion is ruled in at the theorem level: Proposition 4.1 is converted to a local mass estimate of size `Lambda0 n^{-alpha0}`, and Sobolev/elliptic estimates multiply by `Lambda0^2` before taking a square root. The fourth-moment estimate is still the source of the `n` exponent through `alpha0`, but it is not the final source of the `Lambda^{3/2}` scale.
