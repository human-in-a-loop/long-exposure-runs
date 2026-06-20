---
created: 2026-05-16T22:44:00Z
cycle: 43
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M32-schreier-fixed-pair-covariance-lemma
---

# Schreier Fixed-Pair Covariance Lemma

## Statement

Let `P_a,P_b` be independent uniform permutations of `[n]`, and let `u,v`
be fixed words in the free group on `{a,b}`. If the freely reduced forms of
`u` and `v` are both nonidentity, then

```text
Cov(Fix(u(P_a,P_b)), Fix(v(P_a,P_b))) = O_{u,v}(1).
```

Consequently, for the two-permutation Schreier operator

```text
A_n = P_a + P_a^{-1} + P_b + P_b^{-1},
```

and every fixed `k`,

```text
Var(n^{-1} Tr(A_n^k)) = O_k(n^{-2}).
```

This is a theorem for the finite free-Schreier benchmark only. It is not a
random hyperbolic cover theorem and does not transfer to the Kim--Tao Selberg
trace quotient families.

## Reduction to Paired Expectations

M31 gave the exact expansion

```text
Var(n^{-1}Tr(A_n^k))
 = n^{-2} sum_{w1,w2} Cov(Fix(w1),Fix(w2)).
```

Words that freely reduce to the identity have deterministic fixed count `n`;
their covariance with every word is zero after the deterministic tree term is
separated. Thus it remains to prove the fixed-pair covariance bound for two
nontrivial reduced words.

For fixed `u,v`,

```text
|Cov(Fix(u),Fix(v))|
 <= E[Fix(u)Fix(v)] + E[Fix(u)]E[Fix(v)].
```

The one-word expectation bound `E Fix(u)=O_u(1)` is the same argument with one
trajectory. Therefore it is enough to prove

```text
E[Fix(u)Fix(v)] = O_{u,v}(1).
```

Expanding by marked basepoints,

```text
E Fix(u)Fix(v)
 = sum_x P[u(x)=x and v(x)=x]
   + sum_{x != y} P[u(x)=x and v(y)=y].
```

The first sum is the same-basepoint contribution and the second is the
distinct-basepoint contribution.

## Quotient Templates

For a word trajectory, introduce vertices along the closed walk and labelled
constraints for each occurrence of `a` or `b`. Uppercase letters are normalized
by reversing orientation:

```text
A-edge z_i -> z_j  becomes  a-edge z_j -> z_i,
B-edge z_i -> z_j  becomes  b-edge z_j -> z_i.
```

A quotient template is obtained by identifying trajectory vertices. For each
label `ell in {a,b}`, let `C_ell(H)` be the number of distinct directed
`ell`-constraints in the quotient, and let `V(H)` be the number of quotient
vertices. If two same-label constraints force a partial permutation to send one
source to two different targets, or two sources to one target, the template has
probability zero.

For every conflict-free template, the M4 labelled-template identity gives

```text
E InjEmb_n(H) = (n)_{V(H)} (n)_{-C_a(H)} (n)_{-C_b(H)}.
```

Thus the exponent before lower-order falling-factorial corrections is

```text
V(H) - C_a(H) - C_b(H).
```

## Exponent Lemma

**Lemma.** Let `H` be any conflict-free quotient template arising from one or
two fixed nontrivial reduced word trajectories after cyclic reduction. Then

```text
V(H) - C_a(H) - C_b(H) <= 0.
```

**Proof.** Fixed-point counts are invariant under conjugating a word:

```text
Fix(gug^{-1}) = Fix(u).
```

So each nontrivial reduced word may first be cyclically reduced. In a
conflict-free quotient template, each connected component containing edges
contains the full image of at least one cyclically reduced closed labelled
trajectory. Every quotient vertex in such an image has at least one outgoing
directed labelled constraint from that trajectory. Conflict-freeness lets
multiple occurrences collapse only to a single well-defined same-label partial
permutation constraint, not to zero constraints. Therefore each edge-containing
component has at least as many distinct directed labelled constraints as
vertices. Summing over connected components gives

```text
C_a(H) + C_b(H) >= V(H).
```

Hence `V(H)-C_a(H)-C_b(H)<=0`. Templates with partial-injection conflicts have
zero probability and do not contribute. The finite range `n<V(H)` is absorbed
into the fixed constant depending on `u,v`.

## Consequences

Each admissible quotient template contributes `O_{u,v}(1)` after the M4
identity, and there are only finitely many quotient templates for fixed
`u,v`. Therefore

```text
E Fix(u)Fix(v) = O_{u,v}(1),
E Fix(u) = O_u(1),
E Fix(v) = O_v(1),
Cov(Fix(u),Fix(v)) = O_{u,v}(1).
```

Equal, inverse, cyclic-conjugate, and shared-power pairs may change the finite
constant by creating more quotient coincidences, but they do not change the
exponent because the same closed-walk inequality applies.

For fixed `k`, the trace expansion contains only `4^k` words. After separating
freely reducing identity words as deterministic tree contributions, the
remaining covariance sum has `O_k(1)` total size. Multiplying by the outer
`n^{-2}` in the M31 variance expansion proves

```text
Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2}).
```

## Computation as Audit Harness

The companion script
`scripts/prove_schreier_fixed_pair_covariance.py` enumerates reduced word pairs
through length `6`, classifies identity, generic, inverse, cyclic-conjugate,
and shared-power pairs, records representative base-template exponents, and
checks representative same/distinct-basepoint quotient templates where the full
partition enumeration is cheap. The general quotient exponent bound comes from
the lemma above; the computation is a regression harness for boundary cases,
not a substitute for the proof. It writes:

- `data/extension_candidates/m32_pair_quotient_classification.csv`
- `data/extension_candidates/m32_covariance_exponent_proof_checks.csv`
- `data/extension_candidates/m32_variance_theorem_implication.csv`

The generated audit found no positive exponent class through length `6`; the
maximum nonidentity proof exponent is `0`.
