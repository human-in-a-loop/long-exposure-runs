---
created: 2026-05-15T23:55:00Z
cycle: 13
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M5-extension-candidates
---

# Primary M5 Candidate Statement

## Candidate Lemma/Conjecture

Let `H_n` be a fixed labelled directed template, independent of `n`, with vertex set `V`, normalized forward constraint sets `C_a(H)` for each generator label `a`, and no same-label source or image conflict. Define

```text
E_H(n) = (n)_{|V|} prod_a (n)_{-|C_a(H)|}
```

for `n >= |V|`, and let

```text
d(H) = |V| - sum_a |C_a(H)|.
```

The normalized expectation

```text
N_H(n) = n^{-d(H)} E_H(n)
```

admits an asymptotic expansion in `x=1/n`,

```text
N_H(1/x) = 1 + b_1(H) x + b_2(H) x^2 + ...,
```

whose first coefficients are determined by the finite constraint counts in the M4 falling-factorial identity. For bounded template size and bounded constraint counts, the exact expectation is therefore a stable low-degree analytic object near `x=0`; large derivative or coefficient growth observed in high-degree fits from sparse reciprocal grids should be treated as interpolation conditioning unless it persists after comparison with the exact expansion.

## Exact Hypotheses

- The template has finitely many vertices and labelled directed edges, with all inverse-labelled edges normalized by reversing orientation.
- For each generator `a`, the distinct normalized constraints `C_a(H)` form a partial injection.
- Template size and all `|C_a(H)|` are fixed while `n -> infinity`.
- The asymptotic expansion is only asserted for `n >= |V|`, equivalently near `x=0` inside the valid large-`n` domain.
- Conflict cases are excluded from the expansion statement because M4 proves their expectation is identically zero.

## Already Proven By M4

M4 proves the exact identity

```text
E InjEmb_n(H) = (n)_{|V|} prod_a 1/(n)_{|C_a(H)|}
```

for conflict-free templates and proves expectation zero for conflicting templates or for `n < |V|`. It also verifies inverse-label normalization and small-`n` exact enumeration against the formula. In particular,

```text
E(eight_word_cyclic_toy) = 1
E(eight_word_rank2_toy) = (n)_7/(n)_4^2
```

on their valid domains.

## Still Conjectural Or Not Yet Built

The general coefficient formulas `b_1(H), b_2(H), ...` have not yet been derived as reusable expressions. The comparison between exact expansion coefficients and Cycle 9 Chebyshev-window fitted coefficients has not yet been run. Most importantly, this statement does not prove anything about the full Kim--Tao trace/pre-trace polynomials, whose construction depends on imported MPvH, Nau, and MP23 inputs.

## Connection To The Kim--Tao Markov Loss

M2 isolates a shared Markov/interpolation amplification: `q^{2 kappa}` in the trace-side variance and `q^{4 kappa}` in the delocalization-side fourth-moment estimate. M3 shows a toy analogue: low-degree normalized labelled-template fits are stable, while high-degree fits from sparse reciprocal grids produce large derivative and coefficient norms. M4 supplies an exact source for the underlying expectation in one finite-template class.

The proposed M5 path is to test whether the toy instability belongs to interpolation reconstruction rather than to the exact expectation itself. This can clarify which part of the Markov loss is plausibly technical. It does not replace the imported Kim--Tao polynomial-method inputs.

## Falsification Plan

The next cycle should derive symbolic expansions for the certified M4 templates and compare them to existing Cycle 9 fit behavior. The primary candidate is weakened if:

- normalized exact expansions for the canonical templates require unexpectedly high-degree or unstable coefficients near `x=0`;
- the `eight_word_rank2_toy` expansion fails to explain the observed normalized finite-size trend from Cycle 8 and Cycle 9;
- conflict-free bounded templates show singular behavior not visible in the falling-factorial identity;
- any claimed improvement route requires black-box assumptions as strong as MPvH/Nau/MP23 rather than an isolated finite-template argument.

The first concrete target is the expansion

```text
n * (n)_7/(n)_4^2
  = ((n-6)(n-5)(n-4))/((n-1)(n-2)(n-3))
```

as a polynomial power series in `x=1/n`, then comparison with the degree-1, degree-2, and degree-3 Cycle 9 fits for `eight_word_rank2_toy`.
