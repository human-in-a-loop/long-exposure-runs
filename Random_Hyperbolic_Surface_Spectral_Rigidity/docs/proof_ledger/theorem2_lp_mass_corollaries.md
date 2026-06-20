---
created: 2026-05-16T20:12:00Z
cycle: 39
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M28-theorem2-lp-mass-distribution-corollaries
---

# Theorem 2 Lp and Mass Corollaries

## Input

Kim--Tao Theorem 2 states that for a compact connected orientable hyperbolic surface `X` of genus `g >= 2`, there are `alpha=alpha(g)>0` and `C=C(X)>0` such that, with probability at least `1-n^{-1/10}`, every `L^2`-normalized eigenfunction on the random degree-`n` cover `X_n` with eigenvalue `lambda_j(X_n) <= Lambda`, `Lambda >= 1/4`, satisfies

```text
||u_j||_infty <= C Lambda^{3/2} n^{-alpha}.
```

Remark 1.1 records a different high-energy tradeoff: for every `epsilon>0`, there are `alpha'=alpha(g,epsilon)>0` and `C=C(X,epsilon)` such that

```text
||u_j||_infty <= C Lambda^{1/4+epsilon} n^{-alpha'}.
```

The two inputs should not be conflated: the improved Lambda exponent changes the `n` exponent and constant.

## Deterministic Norm Consequences

Let `M_{Lambda,n}` denote either of the two Theorem 2 amplitude envelopes above, and assume `||u||_2=1`. For `2 <= p <= infinity`,

```text
||u||_p <= ||u||_infty^{1-2/p} ||u||_2^{2/p}
        <= M_{Lambda,n}^{1-2/p}.
```

For the direct paper model, this gives

```text
||u||_p <= C^{1-2/p} Lambda^{(3/2)(1-2/p)} n^{-alpha(1-2/p)}.
```

For the interpolation-remark model, this gives

```text
||u||_p <= C_epsilon^{1-2/p}
           Lambda^{(1/4+epsilon)(1-2/p)}
           n^{-alpha'(1-2/p)}.
```

The endpoint checks are exact: at `p=2` this is `||u||_2=1`, and at `p=infinity` it recovers the chosen Theorem 2 sup-norm input.

## Small-Set Mass

For any measurable set `A subset X_n`,

```text
int_A |u|^2 <= ||u||_infty^2 vol(A)
             <= M_{Lambda,n}^2 vol(A).
```

This is nontrivial relative to the identity `int_A |u|^2 <= 1` when

```text
vol(A) < M_{Lambda,n}^{-2}.
```

At fixed energy in the direct model, `M_{Lambda,n}^2 <= C_Lambda n^{-2alpha}`, so the estimate excludes concentration of unit mass on sets of volume `o(n^{2alpha})`. Since `vol(X_n)=n vol(X)`, this is only partial delocalization unless `2alpha` reaches the full cover-volume exponent `1`.

## Effective Support

If a measurable set `E` carries mass `theta`, then

```text
theta <= int_E |u|^2 <= M_{Lambda,n}^2 vol(E),
```

hence

```text
vol(E) >= theta M_{Lambda,n}^{-2}.
```

In particular, the support of an `L^2`-normalized eigenfunction satisfies

```text
vol(supp u) >= M_{Lambda,n}^{-2}.
```

For fixed energy in the direct Theorem 2 model this is a polynomial lower bound `vol(supp u) >= c_Lambda n^{2alpha}`.

## Local-Mass Ledger Input

The M2 delocalization reconstruction records a stronger intermediate statement before the final Sobolev conversion: for fundamental-domain cutoffs `a` on each fiber,

```text
int_H a(z)|u_j^rho(z,i)|^2 dVol(z) <= C Lambda_0 n^{-alpha_0}.
```

This is spatially local at the fixed base-domain scale and is stronger in Lambda than the final pointwise estimate. M28 treats it only as an internal proof-ledger observation, not as a new global small-ball theorem, because extending it to arbitrary moving sets or all balls would require restating and revalidating the full Proposition 4.1 cutoff architecture.

## Nonclaims

These corollaries do not imply quantum ergodicity, equidistribution on every region, lower mass on all balls, level repulsion, simplicity, or nodal-domain estimates. The mechanism is amplitude delocalization: high-probability sup-norm control prevents too much mass from fitting into sets below the `M^{-2}` volume scale, but it does not force mass to appear in any specified region.
