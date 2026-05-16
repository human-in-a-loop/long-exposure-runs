---
created: 2026-05-16T13:05:00Z
cycle: 26
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M15-kim-tao-bridge-requirement
---

# M15 Kim--Tao Bridge Requirement

## Purpose

M12 gave a restricted aggregate theorem template: after fixing \(d=C-V\), per-template product-ratio bounds control aggregate coefficients only through a total-variation or coefficient-variation hypothesis.  M13 found no robust cancellation mechanism in the dominant toy stratum.  M14 calibrated the missing external decay: in the unweighted \(d=1\) rank-two remainder, coefficient absolute variation needs roughly exponential length decay \(\beta\approx1.6\) to \(1.9\) to have at-most-linear growth through coefficient orders \(k\le4\).

M15 asks whether this requirement can be attached to actual Kim--Tao proof objects, and whether it would improve the theorem-level exponent path rather than merely rephrasing the existing MPvH/Nau/MP23 inputs.

## Attachment Map

| Paper object | Quotient-family source | Weights and decomposition | Current imported estimate | M12/M14 attachment | Missing estimate |
|---|---|---|---|---|---|
| Proposition 3.1 | Selberg trace variance; two non-identity geodesic words \((\gamma_1,\gamma_2)\) | coefficients \(a(\gamma,k)=\ell_\gamma/(2\sinh(k\ell_\gamma/2))\), Fourier support \(k\ell_\gamma\lesssim \Lambda_0^{-1/2}q\) | Lemma 3.3 plus Corollary 3.4 package the sum into \(p(1/n)/Q_{\mathrm{id}}\); Markov gives \(q^{2\kappa}\) | M12 can only attach after the weighted quotient sum is stratified by the analogue of \(d=C-V\) | weighted coefficient-variation bound for the trace polynomial coefficients before Markov interpolation |
| Lemma 3.3 | fixed two-cycle labelled graph \(C_{\gamma_1,\gamma_2}\), folded through quotients \(W_r\) | no aggregate geodesic weight yet; fixed word-pair probability law | MPvH embedding expansion, Witten-zeta normalization, Nau boundedness removing negative powers | M4/M7 attach termwise to conflict-free labelled-template skeletons | none termwise; the gap is aggregate summability across quotient families and word/geodesic pairs |
| Corollary 3.4 | full weighted two-trace second moment | Selberg/geodesic coefficients, support-length truncation, denominator \(Q_{\mathrm{id}}\) | converts Lemma 3.3 into a polynomial \(p\) of degree \(O(\Lambda_0^{-1/2}q)\) | closest trace-side location for an M14-style hypothesis | coefficient-variation decay for \(p\)'s fixed-order \(1/n\) coefficients after geometry weights and denominator normalization |
| Proposition 4.2 | eight-loop graph \(C_{\gamma_1,\ldots,\gamma_8}\) after subtracting \(S\) | pre-trace kernels, diagonal primitive-power four-tuples removed, rank-two/noncyclic remainder | MP23 rank-two common-fixed-point estimate supplies the \(n^{-2}\) scale; Markov second derivative gives \(q^{4\kappa}\) | M12/M14 attach to the rank-two/noncyclic aggregate after \(S\) removal | weighted coefficient-variation decay for the eight-word polynomial numerator, compatible with MP23 rank-two decay |

This map rules in H1 only conditionally.  The M12/M14 quantities have real analogues: quotient families, geometry weights, rank/cyclic decomposition, and \(1/n\)-polynomial coefficients.  But the independent-permutation product-ratio algebra is not itself the Kim--Tao surface-group probability law.  MPvH/Witten-zeta, Nau boundedness, and MP23 remain structural prerequisites.

## Conditional Proposition

**Conditional weighted coefficient-variation proposition.**  Fix a trace or pre-trace Kim--Tao polynomialization step with support scale \(q\), and after identity/diagonal terms have been removed, decompose the relevant numerator into fixed \(d=C-V\) strata:

\[
P_{q,d}(x)=\sum_{T\in\mathcal F_{q,d}} \omega_T R_T(x),
\]

where \(T\) ranges over folded quotient templates, \(\omega_T\) includes Selberg or pre-trace kernel weights and probability-law normalization, and \(R_T(x)\) is the exposed normalized product-ratio factor.  Suppose that for fixed coefficient order \(k\),

\[
\sum_{T\in\mathcal F_{q,d}} |\omega_T [x^k]R_T(x)| \le B_{d,k}(q).
\]

Then the M12 aggregate step replaces the generic \(L^{2k}TV_{q,d}\) envelope by \(B_{d,k}(q)\) in that stratum.  If this bound is strong enough to control the polynomial numerator directly at \(x=1/n\), the trace-side Proposition 3.1 Markov bottleneck \(q^{2\kappa}\) is replaced by the corresponding \(B(q)\)-scale, and the pre-trace Proposition 4.2 bottleneck \(q^{4\kappa}\) is replaced by the analogous eight-word \(B(q)\)-scale.

This is a conditional algebra statement, not a new Kim--Tao theorem.  It says exactly what estimate would be useful: coefficient variation, not merely termwise product-ratio bounds and not merely rank labels.

## Selberg Weight Diagnostic

The script `scripts/test_selberg_weight_vs_template_growth.py` compares M14's required word-length decay with crude growth models under \(\ell\approx cL\):

- reduced-word growth: \(3^L\);
- primitive-geodesic growth proxy: \(\exp(\ell)/\ell\);
- Selberg hyperbolic weight: \(1/\sinh(\ell/2)\approx\exp(-\ell/2)\);
- optional extra test-function decay: \(\exp(-\delta\ell)\).

Bare Selberg decay is not enough in the proxy model.  At \(\delta=0\), the effective beta after growth is negative for primitive-geodesic and combined growth, and for reduced-word growth remains below the M14 coefficient-AV threshold even at \(c=3\):

| model | \(c\) | bare effective beta | meets \(\beta=1.6\)? |
|---|---:|---:|---|
| reduced-word growth | 1 | -0.599 | no |
| reduced-word growth | 2 | -0.099 | no |
| reduced-word growth | 3 | 0.401 | no |
| primitive-geodesic growth | 1 | -0.500 | no |
| primitive-geodesic growth | 2 | -1.000 | no |
| combined word/geodesic growth | 1 | -1.599 | no |

The first grid points meeting the order-one coefficient-AV threshold require strong extra decay, for example \(\delta=2.5\) at \(c=1\) in the reduced-word and primitive-geodesic models.  The combined model needs at least \(c=1.5,\delta=2.5\) on the tested grid.  Thus H2 is ruled out for bare Selberg weights and left unresolved only if the test function, surface geometry, or probability law supplies additional exponential damping beyond \(\exp(-\ell/2)\).

![effective Selberg/test-function decay after growth compared with M14 thresholds](reports/figures/m15_decay_requirement_vs_selberg_growth.png)

## Decision

The aggregate-control route remains mathematically meaningful only as a conditional bridge: a real coefficient-variation theorem for Kim--Tao quotient families would target the correct bottleneck and could improve the exponent algebra.  But M15 does not find evidence that Selberg weights alone plausibly supply the M14-scale decay once geodesic or word growth is included.  Rank-only decay is also insufficient by M14, because the dominant toy remainder is already pure rank two.

Recommended next move: pivot away from extending the toy aggregate model.  The best follow-up is either a focused attempt to prove or disprove a Kim--Tao weighted coefficient-variation estimate inside Corollary 3.4/Proposition 4.2, or a new extension path such as local spectral window statistics where the needed input is not as strong as the theorem one wants.

## Non-Claims

- This note does not prove the coefficient-variation hypothesis.
- It does not replace MPvH/Witten-zeta normalization, Nau boundedness, or MP23 rank-two common-fixed-point decay.
- It does not claim actual Kim--Tao quotient families have the same growth as the crude proxy models.
- It does not improve the Kim--Tao rigidity or delocalization exponent unconditionally.

## Artifacts

- `scripts/test_selberg_weight_vs_template_growth.py`
- `data/extension_candidates/kim_tao_decay_requirement_table.csv`
- `data/extension_candidates/conditional_exponent_scenarios.csv`
- `reports/figures/m15_decay_requirement_vs_selberg_growth.png`
- `reports/figures/m15_conditional_exponent_scenarios.png`
