---
created: 2026-05-15T23:10:00Z
cycle: 12
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M4-formal-certification
---

# Labelled Embedding Expectation Identity

## Lemma

Let `H=(V,E)` be a finite directed graph whose edges are labelled by formal generators and inverse generators. Normalize every inverse-labelled edge `(u,v,A)` by replacing it with the forward constraint `(v,u,a)`. For each generator `a`, let `C_a(H)` be the set of distinct normalized constraints `(u -> v)` with label `a`.

If some `C_a(H)` is not a partial injection, meaning one source has two distinct images or two sources have the same image, then the expected number of injective embeddings into independent uniform permutations on `[n]` is zero. If every `C_a(H)` is a partial injection and `n >= |V|`, then

```text
E InjEmb_n(H) = (n)_{|V|} * Product_a 1/(n)_{|C_a(H)|}.
```

If `n < |V|`, the expectation is zero. Here `(n)_k = n(n-1)...(n-k+1)`.

## Proof Sketch

Choose an injective vertex placement `phi: V -> [n]`; there are `(n)_{|V|}` such placements. For a fixed label `a`, the normalized constraints require a uniform random permutation `sigma_a` to map each `phi(u)` to `phi(v)` for `(u -> v) in C_a(H)`.

If `C_a(H)` is not a partial injection, these requirements contradict the definition of a permutation. Otherwise, the images of the distinct constrained sources are distinct and the probability that `sigma_a` realizes all `|C_a(H)|` assignments is exactly `1/(n)_{|C_a(H)|}`. The generator permutations are independent, so the probabilities multiply over labels, and linearity of expectation gives the formula.

## Symbolic Checks

`scripts/certify_labelled_embedding_expectation.wls` evaluates the formula symbolically on the following cases and writes `data/formal_certification/labelled_embedding_expectation_symbolic.csv`:

| template | formula |
|---|---:|
| no-edge two-vertex graph | `(n)_2` |
| one labelled edge | `n-1` |
| two-edge same-label directed path | `n-2` |
| conflicting same-label domain | `0` |
| conflicting same-label image | `0` |
| inverse-labelled edge | `n-1` |
| Cycle 8 inverse-label regression pair | `1` |
| `eight_word_cyclic_toy` | `1` |
| `eight_word_rank2_toy` | `(n)_7 / (n)_4^2` |

The last two entries match the Cycle 8 scaling logic: the cyclic eight-edge template has `|V|=8` and one label with eight constraints, while the rank-two template has `|V|=7` and two labels with four constraints each.

## Exhaustive Finite Validation

`scripts/certify_labelled_embedding_expectation.py` enumerates all permutation tuples for `n=2,3,4` and compares the exact average embedding count with the formula using rational arithmetic. It writes `data/formal_certification/labelled_embedding_expectation_exhaustive.csv`.

This validation is intentionally small. Its purpose is not numerical evidence; it is a brute-force check that the symbolic normalization and the explicit permutation semantics agree in every listed special case that is feasible at small `n`.

## Scope

This certifies one finite combinatorial identity for independent uniform permutations. It supports the M3 labelled-embedding benchmark by turning the expectation estimator and inverse-label repair into a self-contained lemma.

It does not certify the Kim--Tao trace expansion, the MPvH embedding expansion, Nau boundedness, MP23 rank-two common-fixed-point estimates, or any hyperbolic spectral-rigidity statement.
