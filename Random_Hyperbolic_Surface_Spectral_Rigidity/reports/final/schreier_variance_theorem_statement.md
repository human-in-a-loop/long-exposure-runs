---
created: 2026-05-16T22:46:00Z
cycle: 43
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M32-schreier-fixed-pair-covariance-lemma
---

# Schreier Variance Theorem Statement

For independent uniform permutations `P_a,P_b in S_n`, set

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1}.
```

For every fixed integer `k >= 0`,

```text
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2}).
```

The proof expands `Tr(A_n^k)` into fixed counts of length-`k` words. Words
freely reducing to the identity are deterministic tree-moment terms. For every
fixed nonidentity reduced pair `u,v`, the M32 quotient-template lemma gives
`Cov(Fix(u),Fix(v))=O_{u,v}(1)`, because every conflict-free quotient template
has exponent `V-C_a-C_b<=0` under the M4 labelled-template identity.

This theorem belongs only to the finite free-Schreier benchmark. It is useful
as a clean random-permutation analogue of the Kim--Tao two-trace bookkeeping,
but it does not imply any random hyperbolic surface, Selberg trace, or
surface-group quotient-family variance theorem.
