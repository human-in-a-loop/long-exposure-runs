---
created: 2026-05-16T23:24:00Z
cycle: 44
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M33-schreier-benchmark-package-synthesis
---

# Schreier Benchmark Theorem Package

Let `P_a,P_b` be independent uniform permutations of `[n]` and let

```text
A_n=P_a+P_a^{-1}+P_b+P_b^{-1}.
```

For every fixed `k >= 0`,

```text
E[n^{-1}Tr(A_n^k)] = m_k + O_k(n^{-1}),
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2}),
```

where `m_k` is the length-`k` closed-walk moment of the infinite 4-regular
tree, equivalently the number of length-`k` words in `{a,a^{-1},b,b^{-1}}`
that freely reduce to identity.

Proof sketch: expand `Tr(A_n^k)` as a finite sum of fixed-point counts
`Fix(w)`. Freely reducing identity words have `Fix(w)=n` deterministically,
giving the tree term and zero covariance after centering. M31 gives

```text
Var(n^{-1}Tr(A_n^k))=n^{-2} sum_{u,v} Cov(Fix(u),Fix(v)).
```

M32 proves `Cov(Fix(u),Fix(v))=O_{u,v}(1)` for fixed nontrivial reduced
`u,v`, using the M4 labelled-template expectation identity and the quotient
exponent bound `V-C_a-C_b <= 0`. The fixed-`k` word sum is finite, so the
normalized variance is `O_k(n^{-2})`.

This is a finite independent-permutation Schreier benchmark. It does not
prove any Kim--Tao random hyperbolic cover theorem, Selberg trace transfer,
surface-group quotient-family estimate, adjacency-to-Laplacian transfer, or
shrinking-window local spectral statistic.
