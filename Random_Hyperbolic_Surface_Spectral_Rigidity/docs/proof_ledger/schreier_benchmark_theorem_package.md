---
created: 2026-05-16T23:22:00Z
cycle: 44
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M33-schreier-benchmark-package-synthesis
---

# Schreier Benchmark Theorem Package

## Model

Let `P_a,P_b` be independent uniform permutations of `[n]`, and set

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1}.
```

For fixed `k`, expand

```text
Tr(A_n^k) = sum_{w in {a,A,b,B}^k} Fix(w(P_a,P_b)),
```

where `A=a^{-1}` and `B=b^{-1}`.

## Theorem Package

For every fixed integer `k >= 0`, there is a constant depending only on `k`
such that

```text
E[n^{-1} Tr(A_n^k)] = m_k + O_k(n^{-1}),
Var(n^{-1} Tr(A_n^k)) = O_k(n^{-2}),
```

where `m_k` is the closed-walk moment at the root of the infinite 4-regular
tree. Equivalently, `m_k` is the number of length-`k` words in
`{a,A,b,B}` that freely reduce to the identity.

M30 regenerated the first values:

```text
k:   0  1  2   3   4   5    6
m_k: 1  0  4   0   28  0    232
```

Odd values vanish by tree bipartiteness.

## Deterministic Tree-Word Separation

If a word `w` freely reduces to the identity, then `w(P_a,P_b)` is the
identity permutation for every sample, so

```text
Fix(w)=n.
```

These words give the deterministic tree contribution `m_k` to
`n^{-1}Tr(A_n^k)`. After centering, any covariance term with at least one
freely reducing identity word is zero.

For fixed nonidentity reduced `w`, the M4 labelled-template expectation
identity gives bounded fixed-word expectation after quotient-template
exposure. Summing over the finite length-`k` word set gives the expectation
theorem

```text
E[n^{-1} Tr(A_n^k)] = m_k + O_k(n^{-1}).
```

## Variance Proof

M31 gives the exact paired expansion

```text
Var(n^{-1}Tr(A_n^k))
 = n^{-2} sum_{u,v in {a,A,b,B}^k} Cov(Fix(u),Fix(v)).
```

The deterministic tree-word separation removes all covariance terms where
`u` or `v` freely reduces to the identity. It remains only to handle fixed
nontrivial reduced pairs.

M32 proves that for every fixed nontrivial reduced pair `u,v`,

```text
Cov(Fix(u(P_a,P_b)), Fix(v(P_a,P_b))) = O_{u,v}(1).
```

The proof uses the M4 identity: every conflict-free quotient template
contributes with exponent `V-C_a-C_b`, and the M32 outgoing-constraint
argument gives `C_a+C_b >= V`; conflicting partial-permutation templates
contribute zero. The finite range `n<V` is absorbed into the fixed pair
constant.

Since there are only `4^k` words at fixed `k`, the paired covariance sum is
`O_k(1)`. Multiplying by the outer `n^{-2}` proves

```text
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2}).
```

## Provenance

The generated M33 claim ledger is
`data/final/m33_schreier_theorem_claim_ledger.csv`; the artifact index is
`data/final/m33_schreier_package_artifact_index.csv`.

The proof chain is:

- M4: labelled-template expectation identity.
- M30: fixed-`k` expectation theorem and tree moments.
- M31: paired-word variance expansion and deterministic covariance separation.
- M32: fixed-pair covariance lemma.
- M33: consolidated theorem package and no-transfer firewall.

## Scope Firewall

This package is a theorem for the independent two-permutation free-Schreier
benchmark only. It does not prove a Kim--Tao random hyperbolic cover theorem,
a Selberg trace variance estimate, a surface-group quotient-family bound, an
adjacency-to-Laplacian transfer, or shrinking-window local spectral
statistics.
