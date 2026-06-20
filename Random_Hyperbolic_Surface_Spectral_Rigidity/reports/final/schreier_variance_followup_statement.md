---
created: 2026-05-16T21:56:00Z
cycle: 42
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M31-schreier-variance-mechanism-theoremization
---

# Schreier Variance Follow-Up Statement

M31 identifies the next theorem-grade target inside the finite Schreier benchmark:

```text
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2})
```

for fixed `k` in the model `A_n=P_a+P_a^{-1}+P_b+P_b^{-1}`. The variance expands into a finite sum of paired fixed-word covariances; identity/tree words are deterministic after normalization, while nontrivial reduced word pairs are checked by same-basepoint and distinct-basepoint labelled-template constraints.

For `k=2,4,6`, the pair-template analyzer finds maximum covariance order `O(1)` before the outer `n^{-2}` factor and no positive-power obstruction. This makes M30's empirical slopes near `-1.7` better viewed as finite-size crossover evidence for an `n^{-2}` fixed-`k` mechanism than as evidence for a true `n^{-1}` covariance term.

The result remains a theorem template, not a completed proof for all fixed `k`: the remaining finite combinatorial lemma is to show that every consistent quotient template for every fixed nontrivial reduced word pair has exponent `|V|-sum_l |C_l| <= 0`. No transfer to hyperbolic random covers or Selberg trace statistics is claimed.
