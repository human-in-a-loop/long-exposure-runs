---
created: 2026-05-16T19:14:00Z
cycle: 36
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M25-local-window-route-synthesis-and-branch-decision
---

# Local-Window Branch Decision Record

## Obstruction Chain

The local-window branch now has a precise dependency chain:

```text
endpoint subtraction
-> variance requirement
-> Paley-Wiener support scaling
-> long-support trace budget
-> localized Corollary 3.4 numerator
-> quotient-family growth
-> transform damping obstruction
```

M16 shows that inherited Kim--Tao Weyl/rigidity estimates do not by themselves give fixed-energy bulk windows below the endpoint-subtraction scale. M17 converts endpoint-beating local windows into a direct smoothed-window variance input. M19 rules out logarithmic-support localization for bulk `Delta=n^{-d}` and forces support `q=n^eta` with `eta>=d` for resolution, with `eta>d` needed for small leakage.

M20 and M21 translate that polynomial support into a trace-side variance budget. In the notation used there, a fixed-energy trace theorem `LSTV_trace(eta,beta)` is sufficient only when

```text
beta > 2 kappa eta + 2d - 1,     eta >= d,     d > alpha_W.
```

M22 then localizes the upstream target to the Corollary 3.4 numerator

```text
p_{Delta,q}(x)
  = sum_{gamma1,gamma2,k1,k2} W_{Delta,q}(gamma1,k1) W_{Delta,q}(gamma2,k2)
      Q_{gamma1^k1,gamma2^k2}(x),
```

where `W_{Delta,q}` denotes the Selberg/geodesic and localized transform weights. A hypothesis of the form

```text
E G_n(h_{Delta,q})^2 <= n q^A n^{-sigma+o(1)}
```

would give the candidate saving

```text
candidate_beta = (2 kappa - A) eta + sigma.
```

Thus the compact-support route needs

```text
(2 kappa - A) eta + sigma > 2 kappa eta + 2d - 1.
```

M23 provides only proxy evidence, not a theorem: quotient/template families can grow enough that no-saving compact weights are inadequate. M24 gives the analytic obstruction that compact-support localized transform decay is controlled by `u=t delta_r`, not by `t`; it therefore does not provide the exponential-in-support damping imagined in the optimistic M23 model.

## Remaining Compact-Support Theorem

The only compact-support path left is direct control of the actual surface-group quotient-polynomial numerator. A minimal sufficient theorem would be:

**Localized Corollary 3.4 coefficient-variation theorem.** Fix a bulk energy window centered at `r0` with width `Delta=n^{-d}` and compact Paley-Wiener support `q=n^eta`, where `d>alpha_W` and `eta>=d`. For the actual Kim--Tao Lemma 3.3 quotient polynomials `Q_{gamma1^k1,gamma2^k2}` appearing in Corollary 3.4 after inserting the localized test, the weighted numerator satisfies a uniform small-`x` or coefficient-variation estimate

```text
p_{Delta,q}(1/n) / Q_id(1/n)
  <= n q^A n^{-sigma+o(1)}
```

after the identity/diagonal contributions are treated exactly, with

```text
(2 kappa - A) eta + sigma > 2 kappa eta + 2d - 1.
```

This theorem must use the actual folded surface-group quotient family. Independent-permutation labelled-template controls, M23 proxy strata, or transform-envelope damping do not suffice.

## Noncompact Replacement Theorem

A noncompact route would need to replace the compact-support trace architecture. A minimal sufficient replacement has three parts:

1. **Spectral localization:** a noncompact test with tail comparable to `exp(-c t)` must still approximate the desired fixed-energy local spectral window with error smaller than the target mean.
2. **Geometric-side convergence and truncation:** the Selberg trace geometric side must remain controlled after removing compact support, including a random-cover error theorem for omitted long geodesics.
3. **Tail-rate dominance:** the effective tail rate must exceed the relevant geodesic and quotient-family growth rate from M23/M24, not merely be positive.

M24's repaired contrast shows that the illustrative `exp(-0.18 t)` rate is insufficient against the positive growth proxies used there. A viable noncompact theorem therefore needs a quantified rate condition `c > rho`, where `rho` is the growth/variation exponent for the actual geometric quotient family being summed.

## Decision

The branch decision is:

```text
preserve_as_followup_problem
```

Immediate continuation on the same empirical/transform-support branch is not justified. Compact-support progress requires a new coefficient-variation theorem for the actual Corollary 3.4 quotient-polynomial family. The noncompact alternative is credible only as a separate theorem-development branch because it changes the trace architecture and needs a geometric-tail error theorem.
