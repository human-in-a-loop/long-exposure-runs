---
created: 2026-05-15T15:56:54Z
cycle: 2
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# Weyl-Law Inversion Detail For Theorem 1

## Scope

This note expands the final sentence of Kim--Tao §3.1: the paper states that eigenvalue rigidity (1.2) is a direct corollary of the uniform Weyl law (1.4). The point checked here is the spectral edge `lambda=1/4`, where the density in `lambda` vanishes.

## Weyl Profile

Define

```text
F(Lambda) = int_0^{sqrt(Lambda - 1/4)} r tanh(pi r) dr,    Lambda >= 1/4.
```

Then

```text
F'(Lambda) = (1/2) tanh(pi sqrt(Lambda - 1/4)).
```

For `t=Lambda-1/4`, the elementary asymptotics are

```text
F(1/4+t) = (pi/3) t^{3/2} + O(t^{5/2})       as t -> 0,
F'(1/4+t) ~ (pi/2) t^{1/2}.
```

On bounded-away-from-edge intervals `Lambda >= 1/4 + eta`, `F'` has a positive lower bound depending on `eta`. At the edge, only the inverse Hölder behavior

```text
|F^{-1}(y+delta) - F^{-1}(y)| <= C |delta|^{2/3}
```

is uniformly valid for small `y,delta`.

## Input Weyl Law

The output of §3.1 is: with probability at least `1-n^{-1/10}`, for all `Lambda >= 1/4`,

```text
|N_Xn(Lambda) - A F(Lambda)|
<= C n^{1-alpha_W} Lambda^{1/2+epsilon},
```

where

```text
A = n(2g-2).
```

Here `alpha_W` is the exponent produced by the Weyl-law step; from the preceding proof ledger it may be taken no larger than `min(alpha_0,1/9,0.01)` after the grid argument.

## Index Offset At The Edge

The theorem compares `lambda_j(X_n)` to `lambda_j` defined by

```text
F(lambda_j) = j / A.
```

Since (1.4) only starts at `1/4`, eigenvalues below `1/4` are not individually located. However, applying the Weyl law at `Lambda=1/4` gives

```text
N_Xn(1/4) <= C n^{1-alpha_W}.
```

Thus the possible below-edge index offset is of the same size as the Weyl error and can be absorbed into the inversion estimate.

## Counting-To-Location Inequality

Let `mu=lambda_j(X_n) >= 1/4`, and assume `mu <= Lambda`. Monotonicity gives, with harmless `O(1)` errors from indexing conventions and multiplicity,

```text
j <= N_Xn(mu)
```

and, after taking a one-sided limit from the left,

```text
j >= N_Xn(mu-) + O(1).
```

Using the uniform Weyl law on both sides yields

```text
|A F(mu) - j| <= C n^{1-alpha_W} Lambda^{1/2+epsilon}.
```

Dividing by `A` and using `F(lambda_j)=j/A`,

```text
|F(mu) - F(lambda_j)| <= C n^{-alpha_W} Lambda^{1/2+epsilon}.
```

Call the right side `delta_F`.

## Away From The Edge

If both `mu` and `lambda_j` are at least `1/4 + eta`, then `F' >= c_eta`, so

```text
|mu - lambda_j| <= C_eta delta_F
<= C_eta Lambda^{1/2+epsilon} n^{-alpha_W}.
```

This is stronger than the theorem's qualitative form, apart from the expected dependence of the constant on a fixed edge cutoff.

## Edge Regime

Near `1/4`, the lower derivative bound fails. The correct uniform inversion is the Hölder estimate

```text
|mu - lambda_j| <= C delta_F^{2/3}.
```

Since `Lambda >= 1/4`, `Lambda^{1/2+epsilon}` is bounded below and above by harmless constants on any fixed edge range. Therefore

```text
|mu - lambda_j|
<= C (n^{-alpha_W} Lambda^{1/2+epsilon})^{2/3}
<= C Lambda^{1/2+epsilon} n^{-2 alpha_W/3},
```

after enlarging constants and, if desired, reducing `epsilon` in the input Weyl law before relabeling it. This proves the same shape as (1.2) with

```text
alpha_R <= 2 alpha_W / 3.
```

This is the implicit exponent weakening hidden by the phrase "direct corollary."

## Uniform Conclusion

Combining the away-from-edge Lipschitz case with the edge Hölder case gives: if (1.4) holds with exponent `alpha_W`, then (1.2) holds with any

```text
alpha_R < 2 alpha_W / 3
```

and the same displayed `Lambda^{1/2+epsilon}` scale after adjusting constants. This is compatible with Theorem 1 because the theorem asserts existence of some positive `alpha(g,epsilon)`, not equality with the Weyl-law exponent produced in §3.1.

## Diagnostic Outcome

The edge hypothesis from the research brief is ruled in: the monotone inversion is valid, but near `1/4` it naturally weakens the exponent by a factor `2/3`. The paper can hide this because all exponents are non-optimized existence exponents. A later cycle should keep separate names for the Weyl-law exponent `alpha_W` and the rigidity exponent `alpha_R` to avoid accidentally reusing the stronger value.
