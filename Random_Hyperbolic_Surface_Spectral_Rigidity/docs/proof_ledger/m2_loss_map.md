---
created: 2026-05-15T17:06:00Z
cycle: 5
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M2-proof-ledger
---

# M2 Cross-Proof Loss Map

## Purpose

This ledger consolidates the dominant losses in the validated Theorem 1 rigidity and Theorem 2 delocalization reconstructions. It separates proposition-level polynomial-method losses, theorem-level smoothing/probability losses, Weyl inversion losses, and final analytic conversion losses.

## Loss Ledger

| Loss source | Proof location | Scale or exponent affected | Classification | Why it matters |
|---|---|---|---|---|
| Proposition 3.1 Markov loss | Trace-side second moment; Markov applied to `P(x)=x^2p(x)` | `q^{2 kappa}` in `Lambda0^2 q^{2 kappa} n^{-1}` | technical | Visible polynomial interpolation loss after two-trace polynomialization; likely non-optimized without external MPvH audit. |
| Two-trace polynomialization inputs | Lemma 3.3 and Corollary 3.4 | polynomial degree `O(Lambda0^{-1/2}q)` and rational expression in `1/n` | imported | Uses MPvH embedding expansion and Nau boundedness; structurally necessary in local proof but externally sourced. |
| Smooth cutoff derivative order | Theorem 1 proposition-to-Weyl passage | `m = kappa + 3 + K`, `K=floor((kappa+5)/(2 epsilon))+1`, `alpha_0=1/(3m)` | technical | Converts polynomial estimates to smooth spectral cutoffs; large `K` is chosen to force summable `Lambda^{-2}` variance. |
| Chebyshev threshold | Theorem 1 fixed-`Lambda` probability | variance `n^{-1/3}` becomes failure `n^{-1/9}` | technical | Probability conversion loses exponent but preserves enough decay for the grid union. |
| Spectral Grid/union probability | Theorem 1 uniform Weyl law | grid factor `n^{0.01}` gives total failure `n^{-1/10}` | technical | Administrative uniformity loss over all `Lambda`; not a new spectral estimate. |
| Weyl edge inversion | Weyl law to eigenvalue rigidity | `alpha_W` may weaken to `alpha_R < 2 alpha_W/3` | analytic-conversion | Near `lambda=1/4`, `F(Lambda) ~ (Lambda-1/4)^{3/2}`, so inversion is only Hölder. |
| Proposition 4.1/4.2 Markov loss | Pre-trace fourth-moment statistic; second derivative of `x^2p` | `q^{4 kappa}` in `Lambda0^8 q^{4 kappa} n^{-2}` | technical | Fourth-moment/eight-word analogue of Proposition 3.1; second derivative doubles the visible Markov power. |
| Eight-word common fixed-point input | Proposition 4.2 polynomialization | `n^{-2}` rank-two scale after diagonal removal | imported | Uses MP23 rank-two common-fixed-point estimate; deepest imported delocalization-side input. |
| Primitive-power diagonal subtraction `S` | Theorem 2 pre-trace/fourth moment | removes cyclic diagonal four-tuples; deterministic bound `|S|^{1/4} <= C Lambda0 n^{-alpha0}` | structural | Required before the remaining fourth-moment statistic has rank-two/common-fixed-point decay. |
| Smooth fourth-moment cutoff | Theorem 2 Proposition 4.1 to smooth windows | derivative order `2kappa+11`, `alpha0=1/(16(2kappa+11))` | technical | Eighth power of the cutoff norm forces a smaller `n` exponent than a second-moment estimate. |
| Fiber union loss | Theorem 2 high-probability local control | fixed-fiber failure `Lambda0^{-2}n^{-5/4}` becomes fixed-window failure `Lambda0^{-2}n^{-1/4}` | technical | New relative to Theorem 1 because delocalization is local in each cover sheet. |
| Window grid/union probability | Theorem 2 simultaneous window control | final event probability `1-n^{-1/10}` | technical | Same role as Theorem 1 grid, now after fiber union. |
| Sobolev/elliptic local-mass-to-`L^\infty` conversion | Theorem 2 final step | local mass `Lambda0 n^{-alpha0}` becomes `||u||_infty <= C Lambda0^{3/2} n^{-alpha0/2}` | analytic-conversion | Dominates the visible `Lambda^{3/2}` scale of the stated theorem. |

## Cross-Proof Diagnostic

The shared bottleneck is polynomial-method interpolation for the `n` exponent: `q^{2 kappa}` on the trace side and `q^{4 kappa}` on the pre-trace fourth-moment side. The final displayed `Lambda` behavior has different causes: Theorem 1 retains the Weyl-law scale `Lambda^{1/2+epsilon}` after inversion, while Theorem 2's `Lambda^{3/2}` is produced by the final elliptic conversion from local mass to pointwise norm.

The distinction between `alpha_W` and `alpha_R` is essential. `alpha_W` is the exponent in the uniform Weyl law; `alpha_R` is the eigenvalue-location exponent after monotone inversion, and the spectral edge safely permits only `alpha_R < 2 alpha_W/3`.

## M3 Surface

The most direct computational follow-up is not hyperbolic spectrum simulation. The proof-ledger shows that the deepest unresolved mechanism is combinatorial: common fixed-point statistics for random permutation representations, including the contrast between cyclic diagonal families and rank-two/noncyclic families. M3 should therefore begin with finite random-permutation probes of fixed-point scaling before attempting geometric spectral models.
