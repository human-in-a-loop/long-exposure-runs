---
created: 2026-05-16T21:14:00Z
cycle: 41
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M30-schreier-benchmark-theoremization
---

# Schreier Benchmark Follow-Up Statement

The finite Schreier model

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1}
```

now has a clean fixed-k trace-moment benchmark: after expanding `Tr(A_n^k)` into word fixed-point counts, freely reducing words give the 4-regular tree moment `m_k`, and all nontrivial reduced fixed-k words contribute only `O_k(1)` expected fixed points. Thus

```text
E[n^{-1} Tr(A_n^k)] = m_k + O_k(n^{-1}).
```

M30 regenerated `m_2=4`, `m_4=28`, `m_6=232`, `m_8=2092`, and `m_10=19864`, and the centered variance experiment on `n=80,140,220,320` found slopes near `-1.7` for `k=2,4,6`. The variance statement remains empirical, but it is strong enough to keep the Schreier benchmark as a standalone model program for trace expansion, tree subtraction, and finite permutation fluctuation scaling. This is not a hyperbolic random-cover theorem and does not address the Kim--Tao surface-group quotient-family obstruction.
