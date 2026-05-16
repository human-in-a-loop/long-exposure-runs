---
created: 2026-05-16T20:14:00Z
cycle: 39
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M28-theorem2-lp-mass-distribution-corollaries
---

# Theorem 2 Follow-Up Statement

Kim--Tao Theorem 2 implies a high-probability mass-delocalization corollary for random covers. If `||u||_2=1`, `lambda <= Lambda`, and `||u||_infty <= M_{Lambda,n}`, then for every `2 <= p <= infinity`,

```text
||u||_p <= M_{Lambda,n}^{1-2/p},
```

and every measurable set `A` satisfies

```text
int_A |u|^2 <= M_{Lambda,n}^2 vol(A).
```

Consequently any set carrying mass `theta` has volume at least `theta M_{Lambda,n}^{-2}`. With the direct theorem envelope `M_{Lambda,n}=C Lambda^{3/2} n^{-alpha}`, fixed-energy eigenfunctions cannot concentrate unit mass on sets of volume `o(n^{2alpha})`; with the Remark 1.1 envelope the high-energy Lambda loss improves but the `n` exponent changes. This is a useful theorem-level corollary package, not quantum ergodicity or equidistribution.
