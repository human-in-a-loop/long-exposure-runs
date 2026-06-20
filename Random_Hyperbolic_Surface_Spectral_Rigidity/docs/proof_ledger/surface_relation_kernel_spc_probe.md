---
created: 2026-05-17T01:30:00Z
cycle: 50
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M39-surface-relation-kernel-spc-probe
---

# Surface-Relation Kernel SPC Probe

## Lemma 3.3 Reconstruction

Kim--Tao Lemma 3.3 starts with the two-cycle labelled graph
`C_{gamma1,gamma2}` built from cyclically reduced words for `gamma1` and
`gamma2`.  The quotient family `R` consists of surjective labelled-graph
morphisms `r: C_{gamma1,gamma2} -> W_r` such that `W_r` is folded and every
path in `W_r` spelling an element of `ker(F_{2g} -> Gamma)` is closed.

That condition enters before any polynomial is evaluated.  It defines the
admissible folded targets `W_r`; each morphism into a Schreier graph factors
uniquely as `C_{gamma1,gamma2} -> W_r -> X_phi`, and the expectation becomes
`sum_{r in R} E_emb_n(W_r)`.  MPvH/Nau inputs then express each embedding
expectation through a polynomial contribution `p_r(n)`, these contributions
sum to `p_{gamma1,gamma2}(n)`, and the reciprocal variable `t=1/n` conversion
produces `Q_{gamma1,gamma2}(t)/Q_id(t)`.

## Consequence For Corollary 3.4

In Corollary 3.4 the same lemma is applied to `gamma1^k1` and `gamma2^k2`,
giving summands

```text
w(gamma1,k1) w(gamma2,k2)
Q_{gamma1^k1,gamma2^k2}(1/n) / Q_id(1/n).
```

The positive Selberg length/sinh factors do not create signs.  Remaining
signs can come from transform values and from the evaluated quotient
polynomials `Q_i(1/n)`.  Kernel closure is therefore a paper-native label on
admissible quotient classes, but Lemma 3.3 by itself does not identify an
opposite-sign pairing, orthogonality relation, or sign distribution for
`Q_i(1/n)`.

## Candidate Template

A non-vacuous direct target must be evaluated at x=1/n and would have to be:

```text
SPC_kernel(A,sigma):
|sum_{i in G_kernel} w_i Q_i(1/n) / Q_id(1/n)|
  <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1)).
```

For `q=n^eta`, denominator loss `|Q_id(1/n)|^{-1} <= n^D` gives

```text
beta = (2*kappa - A)*eta + sigma - D.
```

The Markov baseline is `A=2*kappa`, `sigma=0`, `D=0`, with `Lambda0^20`.

## Decision

The relation-kernel route is not currently theorem-ready.  The honest status
is conditional: `kernel_class_signed_pairing` and
`quotient_polynomial_sign_grouping` are valid theorem templates only if a new
surface theorem supplies evaluated `Q_i(1/n)` sign cancellation inside
relation-compatible quotient classes.

Hard pivot rule: if the proof uses only a smaller admissible family, or if it
requires `sum_i |w_i Q_i(1/n)|` or coefficient total variation inside fixed
kernel strata, the branch is coefficient/signed variation for the actual
surface numerator, not direct signed pointwise cancellation.  If the only
signs used are transform signs, the mechanism belongs to the weaker
length-shell transform-phase branch.
