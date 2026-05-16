---
created: 2026-05-16T21:10:00Z
cycle: 41
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M30-schreier-benchmark-theoremization
---

# Schreier Trace Moment Benchmark

## Model

Let `P_a,P_b` be independent uniform permutation matrices on `[n]`. The M30 Schreier benchmark uses the 4-regular multigraph adjacency operator

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1}.
```

Loops and parallel edges are retained, so every row sum is exactly `4`. This is a free-group random permutation model, not a surface-group random cover and not a hyperbolic Laplacian model.

## Word Expansion

For each fixed `k`,

```text
Tr(A_n^k) = sum_{w in {a,a^{-1},b,b^{-1}}^k} Fix(w(P_a,P_b)).
```

This is just expansion of the matrix product: each letter chooses one of the four summands, and the trace counts starting vertices returned to themselves by the resulting word map.

If a word freely reduces to the identity, then `w(P_a,P_b)` is the identity permutation for every sample, so `Fix(w)=n`. The number of such words is the closed-walk count from the root of the infinite 4-regular tree. M30 regenerated:

| k | tree moment |
|---:|---:|
| 0 | 1 |
| 2 | 4 |
| 4 | 28 |
| 6 | 232 |
| 8 | 2092 |
| 10 | 19864 |

Odd tree moments vanish because the 4-regular tree is bipartite.

## Theorem Template

**Theorem template.** For every fixed `k`,

```text
E[n^{-1} Tr(A_n^k)] = m_k + O_k(n^{-1}),
```

where `m_k` is the infinite 4-regular tree closed-walk moment.

Proof sketch: split the word expansion by free reduction. Identity-reducing words contribute exactly `n m_k` to `E Tr(A_n^k)`. Every other word reduces to a nontrivial reduced word of length at most `k`. For fixed reduced nontrivial word, the expected number of fixed points of its evaluation on independent uniform permutations is `O_k(1)` by exposing the finite orbit constraints; summing over at most `4^k` words gives an `O_k(1)` contribution to `E Tr(A_n^k)`, hence `O_k(n^{-1})` after normalization.

This is a theorem template rather than a fully formalized lemma here: the fixed-word `O_k(1)` estimate is standard finite permutation exposure bookkeeping and is directly compatible with the M4 labelled-template expectation identity, but M30 does not mechanize it in Lean or GAP.

## Variance Evidence

The analyzer simulated `n in {80,140,220,320}` with `24` trials and seed `20260516`. For the centered statistic

```text
n^{-1} Tr(A_n^k) - m_k,
```

the fitted log-log variance slopes for the main even moments were:

| k | fitted variance slope |
|---:|---:|
| 2 | -1.765 |
| 4 | -1.716 |
| 6 | -1.762 |

This supports a polynomially decaying fixed-k fluctuation benchmark, closer to the `n^{-2}` reference than to the `n^{-1}` reference on this grid. It is numerical evidence, not a proved variance theorem.

## Analogy Boundary

Real analogy:

- trace expansion as a sum over word/fixed-point statistics;
- deterministic identity/tree contribution separated before fluctuation analysis;
- finite permutation constraints expose where labelled-template expectations enter.

Scope firewall:

- the group law is free, not a surface-group relation;
- the spectrum is adjacency spectrum, not hyperbolic Laplacian spectrum;
- this does not replace the MPvH, Nau, or MP23 inputs used by Kim--Tao;
- this does not solve the M25 localized quotient-family obstruction.
