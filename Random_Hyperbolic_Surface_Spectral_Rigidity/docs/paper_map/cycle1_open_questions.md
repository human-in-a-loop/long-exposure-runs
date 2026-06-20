---
created: 2026-05-15T15:36:35Z
cycle: 1
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M1-paper-map
---

# Cycle 1 Open Questions And Bottlenecks

These are not extension claims. They are Cycle 1 bottlenecks promoted to later milestones.

## 1. Exact Exponent Flow From Proposition 3.1 To Theorem 1

- Location: §3.1, especially (3.5)-(3.12).
- Suspected mechanism: `alpha_0 = 1/(3(kappa+3+K))` is set after the Chebyshev expansion and cutoff derivative bounds, with `K = floor((kappa+5)/(2epsilon)) + 1`.
- Why it matters: this appears to be one of the first places where the final rigidity exponent is fixed rather than merely bounded by the polynomial method.
- Proposed next-cycle artifact: `docs/proof_ledger/theorem1_exponent_flow.md`, deriving each power of `Lambda`, `n`, `q`, `K`, and `kappa`.

## 2. Markov Brothers' Inequality As Dominant Loss Candidate

- Location: Lemma 3.5 and its uses in §3.2.3 and §4.2.3.
- Suspected mechanism: derivative control costs `q^{2kappa}` in Proposition 3.1 and `q^{4kappa}` in Proposition 4.1.
- Why it matters: any sharper rigidity exponent likely needs either a sharper polynomial derivative step or a different way to evaluate `p(1/n)` from values at reciprocal integers.
- Proposed next-cycle artifact: `docs/proof_ledger/markov_loss_reconstruction.md`, plus a small numerical polynomial experiment under `data/polynomial_method/` in `M3-computational-probes`.

## 3. Two-Trace Polynomial Expansion Adaptation

- Location: Lemma 3.3, especially the replacement of `C_gamma` by `C_{gamma_1,gamma_2}`.
- Suspected mechanism: the proof imports the [MPvH25] graph morphism expansion and asserts the same argument works for two disjoint cycles.
- Why it matters: this is a paper-specific adaptation and should be made inspectable before using the method for new statistics.
- Proposed next-cycle artifact: `docs/proof_ledger/two_trace_expansion_ledger.md`, with a finite Schreier-graph toy script later in `M3-computational-probes`.

## 4. Fourth-Order Common-Fixed-Point Estimate

- Location: Proposition 4.2, especially (4.15).
- Suspected mechanism: the eight-loop graph expansion reduces to common fixed points of two free generators and imports `[MP23, Theorem 1.3]` for an `O_q(n^{-2})` scale.
- Why it matters: Theorem 2 diverges from Theorem 1 here; this estimate controls whether the eigenfunction proof is a formal analogue or a genuinely stronger random-cover statistic.
- Proposed next-cycle artifact: `docs/proof_ledger/eigenfunction_fourth_moment_ledger.md`.

## 5. The Diagonal Term `S`

- Location: (4.1), (4.9), and the bound following (4.9).
- Suspected mechanism: `S` records diagonal correlations in the pre-trace expansion and is controlled by kernel localization plus exponential hyperbolic decay.
- Why it matters: this term has no analogue in the global trace proof and may be the bottleneck for sharper eigenfunction delocalization or finer window statistics.
- Proposed next-cycle artifact: `docs/proof_ledger/pretrace_diagonal_term.md`.

## 6. Weyl-Law Inversion Details

- Location: final sentence of §3.1.
- Suspected mechanism: the paper states that eigenvalue rigidity (1.2) is a direct corollary of the Weyl law (1.4), relying on monotonicity and density of the hyperbolic spectral measure.
- Why it matters: the edge `lambda=1/4` has density starting at zero in `lambda` coordinates, so a careful inversion should track why the stated `Lambda^{1/2+epsilon}` error remains valid.
- Proposed next-cycle artifact: `docs/proof_ledger/weyl_inversion_detail.md`.

## 7. Low-Energy Below-`1/4` New Eigenvalues

- Location: discussion after (1.5).
- Suspected mechanism: combining (1.4) with the polynomial spectral gap of Hide--Macera--Thomas gives a below-threshold rigidity statement with modified exponent `min(2alpha/3,b)`.
- Why it matters: this is outside the main theorem's `[1/4,infinity)` rigidity range but may produce a clean corollary or extension target.
- Proposed next-cycle artifact: `docs/proof_ledger/below_quarter_corollary.md`.

## 8. Transfer To Weil-Petersson Model

- Location: introduction after the random cover model definition.
- Suspected mechanism: the authors state that formulas from [AM23] and [HMT25b] make the Theorem 1 method apply to Weil--Petersson random surfaces.
- Why it matters: this is a high-value later extension, but Cycle 1 intentionally avoids external literature expansion.
- Proposed next-cycle artifact: defer to `M5-extension-candidates` after `M2-proof-ledger` validates the trace-to-polynomial pipeline.

