---
created: 2026-05-16T21:52:00Z
cycle: 42
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M31-schreier-variance-mechanism-theoremization
---

# Schreier Variance Mechanism

## Setup

M30 used the two-permutation Schreier adjacency operator

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1}
```

with `P_a,P_b` independent uniform permutations of `[n]`. For fixed `k`,

```text
Tr(A_n^k) = sum_w Fix(w(P_a,P_b)),
```

where `w` ranges over length-`k` words in `{a,A,b,B}` and `A=a^{-1}`, `B=b^{-1}`.

The M30 tree term is deterministic: if `w` freely reduces to the identity, then `Fix(w)=n` for every sample. These words contribute the 4-regular tree moment to `n^{-1}Tr(A_n^k)` and do not contribute variance after centering.

## Paired-Word Expansion

For the centered normalized trace,

```text
Z_k(n) = n^{-1}Tr(A_n^k) - E[n^{-1}Tr(A_n^k)],
```

the variance is exactly

```text
Var Z_k(n)
 = n^{-2} sum_{w1,w2} Cov(Fix(w1),Fix(w2)).
```

Thus a fixed-`k` theorem

```text
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2})
```

follows if every non-deterministic paired-word covariance is `O_k(1)`.

Expanding the covariance by marked basepoints gives

```text
E Fix(w1)Fix(w2)
 = sum_{x=y} P[w1(x)=x and w2(x)=x]
   + sum_{x!=y} P[w1(x)=x and w2(y)=y].
```

The `x=y` and `x!=y` pieces must be separated because they carry different powers of `n`. The M4 labelled-template identity applies to each conflict-free injective template:

```text
E InjEmb_n(H) = (n)_{|V(H)|} product_l (n)_{-|C_l(H)|}.
```

The order probe is the exponent `|V|-sum_l |C_l|`. Positive exponent would signal a possible obstruction to `O_k(1)` covariance. Exponent zero gives an `O(1)` contribution before the outer `n^{-2}` factor; negative exponent is smaller.

## Pair Classes

The M31 analyzer groups length-`k` word pairs by freely reduced representatives and multiplicity. It separates:

- identity/identity pairs;
- one identity and one nontrivial reduced word;
- equal reduced words;
- inverse reduced words;
- cyclic or inverse-conjugate relations;
- shared primitive-power relations;
- generic pairs sharing a generator;
- generic pairs on disjoint generators.

Identity-containing pairs are deterministic covariance-zero classes. They can have positive raw embedding exponents if treated as unconstrained templates, but the covariance is zero because the identity fixed-point count is exactly `n`.

For nontrivial reduced pairs, the same-basepoint and distinct-basepoint templates checked through `k=2,4,6` have classwise maximum exponent `0` when scanned across all reduced pair templates in the class. No checked pair class has a positive-power covariance-order obstruction.

## Small-k Certification

Generated table `data/extension_candidates/m31_variance_order_summary.csv` records:

| k | word pairs | reduced word types | pair classes | max covariance order | normalized order |
|---:|---:|---:|---:|---|---|
| 2 | 256 | 13 | 7 | `O(1)` | `O(n^-2)` |
| 4 | 65536 | 121 | 8 | `O(1)` | `O(n^-2)` |
| 6 | 16777216 | 1093 | 8 | `O(1)` | `O(n^-2)` |

The strongest small-k conclusion is therefore:

**Theorem-template evidence.** For `k=2,4,6`, the reduced paired-word classes in the two-permutation Schreier benchmark show no M4-style labelled-template mechanism that can make `Cov(Fix(w1),Fix(w2))` grow like a positive power of `n`. This supports the fixed-`k` theorem template `Var(n^{-1}Tr(A_n^k))=O_k(n^{-2})`.

## Proof Gap

The current artifact is not a complete all-`k` proof. It does not enumerate every non-injective quotient of every pair trajectory. The remaining proof step is a finite combinatorial lemma:

```text
For every fixed nontrivial reduced pair (u,v), every consistent quotient
template contributing to E Fix(u)Fix(v) has |V|-sum_l |C_l| <= 0.
```

If that lemma is proved, the finite word sum immediately gives the `O_k(n^{-2})` normalized variance theorem. M31 found no small-k counterexample and no relation class suggesting an `O(n)` covariance term.

## Analogy Boundary

The meaningful analogy with Kim--Tao is the two-trace structure: variance becomes a paired fixed-point statistic and then a labelled-template expectation problem. The boundary is equally important: this is a free-group Schreier model with independent permutations, not a surface-group random-cover theorem and not a Selberg trace formula estimate.
