---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 28-30"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 28-30

## Abstract

Cycles 28-30 continued the local spectral-window branch opened by M16. M16 had shown that subtracting two global Kim--Tao Weyl-law estimates controls local spectral windows only above the inherited global endpoint-error scale. These three cycles asked whether that obstruction could be bypassed by a direct localized trace or pre-trace statistic.

The result is a clean conditional-and-negative synthesis. M17 formulated the exact smoothed-window variance estimate needed to beat endpoint subtraction. M18 mapped that estimate into Kim--Tao's existing test-function architecture and found that shrinking windows force larger geometric support and larger polynomial degree, reintroducing the `q^{2\kappa}` trace loss and the `q^{4\kappa}` pre-trace loss. M19 then tested the remaining logarithmic-support smoothing escape route and validated a Fourier-scaling obstruction: within compactly supported Selberg-transform tests, resolving a polynomially shrinking window requires polynomially growing support.

The local-window program now has a precise fork. It can continue only by proving genuinely new long-support localized random-cover variance input, developing a noncompact geometric-tail trace/pre-trace method, or recording a negative synthesis for shrinking local-window statistics under the current Kim--Tao architecture.

## Introduction

The campaign studies Kim and Tao's paper `2603.01127`, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*. Earlier cycles reconstructed the global Weyl-law and rigidity estimates, explored aggregate quotient-control routes, and then pivoted to local spectral windows.

The immediate predecessor, M16, derived a local-window corollary by endpoint subtraction. If

\[
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr,
\]

then subtracting the global Weyl law at `Lambda` and `Lambda+Delta` gives a local estimate with an inherited endpoint error. In the bulk, where

\[
F'(\Lambda)=\frac12\tanh(\pi\sqrt{\Lambda-1/4})>0,
\]

the local main term is proportional to `n F'(\Lambda)\Delta`. The global-error threshold is therefore much larger than mean spacing. M16 concluded that true local statistics require a new localized variance or correlation input rather than another endpoint-subtraction corollary.

Cycles 28-30 investigate that input.

## Approach

The three cycles form one chain.

Cycle 28, M17, defined a smoothed local spectral statistic and derived the variance scale needed for it to control local windows. It also benchmarked the idea against existing Schreier spectral-window toy data.

Cycle 29, M18, asked whether Kim--Tao's current test functions could supply such a localized statistic. It mapped window width to the spectral parameter `r`, then to Fourier/geometric support and polynomial degree.

Cycle 30, M19, isolated the Paley-Wiener or Fourier-scaling mechanism behind that support requirement. It checked whether smoothing could keep logarithmic support while resolving polynomially shrinking windows.

All three cycles were audited and validated. M18 required an audit repair to two generated-data details: the support metadata was corrected to `\Lambda_0^{-1/2}q`, and exact edge rows were corrected to use the `\Delta^{-1/2}` scale. M19 required no audit repair.

## Source Inventory and Timeline

Cycle 28 researcher session `3c692209-62b8-4ae4-8f67-ae11518f55e1` opened M17, with the goal of replacing endpoint subtraction by a direct smoothed-window variance framework.

Cycle 28 worker session `1c71a754-9aea-4f05-84dd-8a217044c143` built the M17 proof note, report, analyzers, tests, CSVs, and figures. It reported the bulk criterion `v/2 < 1-d` for `Delta=n^{-d}` and `Var Z_n <= n^v`, together with the requirement `d>alpha_W` to beat M16 endpoint subtraction.

Cycle 28 auditor session `2c824b5d-03c6-4cb6-813e-3aab351dc27c` validated M17 with no critical or moderate findings.

Cycle 29 researcher session `b799f376-40ae-4ce1-9592-d1bd79d780cf` opened M18 to map M17's variance target into Kim--Tao's test-function support, polynomial degree, and Markov/interpolation losses.

Cycle 29 worker session `e90d9bed-c6ce-43b4-b8d4-531483d52879` built the M18 feasibility map and reported that Kim--Tao's `q` controls both degree and geometric support, with trace-side loss `q^{2\kappa}` and pre-trace loss `q^{4\kappa}`.

Cycle 29 auditor session `b068f57a-3935-4ffb-88c7-a1a5d8637745` validated M18 after repairing the support metadata and exact-edge support exponent.

Cycle 30 researcher session `126e3b5d-29b2-4b11-9175-e5fe1cc28036` opened M19 to isolate whether a smoothed Paley-Wiener window could resolve shrinking windows with logarithmic or sub-polynomial support.

Cycle 30 worker session `8fec643c-4e8e-49c7-8f0c-c7869c46665e` built the M19 Fourier-scaling package, including a Wolfram symbolic certificate, leakage analyzer, tests, CSVs, and figures.

Cycle 30 auditor session `201e09c7-14bc-4c5f-ac88-8cb706ef3ab4` validated M19 with no critical or moderate findings.

No `REFERENCES.md` file was present in the workspace during this report pass. The references section therefore lists local source artifacts rather than global numbered bibliography entries.

## Findings

### Finding 1: M17 Defines the Exact Variance Input Needed to Beat Endpoint Subtraction

M17 introduced the smoothed statistic

\[
Z_n(\phi;\Lambda,\Delta)
=
\sum_j \phi\left(\frac{\lambda_j(X_n)-\Lambda}{\Delta}\right)
-
\operatorname{main}_n(\phi;\Lambda,\Delta).
\]

In the bulk, the main term has size

\[
\mu_n(\phi;\Lambda,\Delta)
\sim
(2g-2)n\Delta F'(\Lambda)\int\phi.
\]

The conditional proposition is direct: if

\[
\operatorname{Var} Z_n(\phi;\Lambda,\Delta)\le V(n,\Lambda,\Delta)
\]

and

\[
\sqrt{V(n,\Lambda,\Delta)}=o(\mu_n(\phi;\Lambda,\Delta)),
\]

then Chebyshev's inequality gives relative control of the smoothed local count with high probability.

For `Delta=n^{-d}` and `Var Z_n <= n^v`, the bulk condition is

\[
\frac{v}{2}<1-d.
\]

To be genuinely stronger than M16 endpoint subtraction, the window must also lie below the endpoint threshold, so in bulk it must satisfy

\[
d>\alpha_W.
\]

At the spectral edge, M17 replaced the bulk mean `n Delta` by the edge mass `n Delta^{3/2}`. The edge mean exponent becomes `1-3d/2`, and the endpoint threshold exponent becomes `2 alpha_W/3`.

![conditional variance regimes showing where smoothed-window Chebyshev control beats M16 endpoint subtraction](reports/figures/m17_variance_requirement_phase_diagram.png)

M17 also reused M3 Schreier spectral-window data as a toy benchmark. The fitted normalized-variance slopes were approximately:

| Window | Fitted normalized variance slope |
|---|---:|
| `window_neg_edge` | `-1.9409` |
| `window_neg_mid` | `-1.8929` |
| `window_pos_edge` | `-2.0488` |
| `window_pos_mid` | `-1.9315` |

The cycle treated these as toy evidence only. They show that a local-window variance question is meaningful in a finite Schreier model, not that Kim--Tao random covers satisfy the needed hyperbolic trace variance theorem.

![empirical variance scaling for M3 Schreier spectral-window counts by window and n](reports/figures/m17_schreier_window_variance_scaling.png)

### Finding 2: M18 Shows Existing Kim--Tao Test Functions Do Not Localize for Free

M18 connected the M17 variance target to Kim--Tao's §2.4 test-function setup. In that setup,

\[
f_{\Lambda_0}(x)=f(c_0\Lambda_0^{-1/2}x),
\qquad
\widehat{\phi}(x)=h\circ f_{\Lambda_0}(x),
\]

where `h` is a polynomial of degree `q`. The support relation used in the trace and pre-trace arguments is

\[
\operatorname{supp}((h\circ f_{\Lambda_0})^\vee)
\subset
[-c_0\Lambda_0^{-1/2}q,\;c_0\Lambda_0^{-1/2}q].
\]

Thus `q` controls both polynomial degree and geometric-side support length, up to the fixed-energy factor `\Lambda_0^{-1/2}`.

For `lambda=r^2+1/4`, a `lambda`-window `[Lambda,Lambda+Delta]` has exact `r`-width

\[
\delta_r
=
\sqrt{\Lambda+\Delta-1/4}
-
\sqrt{\Lambda-1/4}.
\]

In fixed bulk energy this is `Delta/(2 sqrt(Lambda-1/4)) + O(Delta^2)`. At the exact edge `Lambda=1/4`, it is `sqrt(Delta)`, so edge inverse-width support scales like `Delta^{-1/2}` rather than `Delta^{-1}`.

M18's conclusion was conservative. Direct inverse-width localization for `Delta=n^{-d}` heuristically forces `q` to grow polynomially in `n`. The existing proof architecture then pays the known losses:

\[
\text{trace side: } q^{2\kappa},
\qquad
\text{pre-trace side: } q^{4\kappa}.
\]

The trace side is less obstructed than the pre-trace side, but neither gives M17's local-window variance input by retuning the existing cutoff.

![required geometric support or transform scale versus spectral-window exponent d, separated by bulk, edge, and high-energy regimes](reports/figures/m18_localization_support_vs_window.png)

The generated M18 tables had 330 tradeoff rows and 18 summary rows. Their dominant classification was not that the architecture proves local variance, but that the next step would need either a new local test-function construction or a new localized random-cover variance estimate.

![symbolic feasibility map comparing M17 variance-improvement region with Kim--Tao-style trace and pre-trace polynomial-loss proxies](reports/figures/m18_markov_loss_feasibility_map.png)

### Finding 3: M19 Closes the Logarithmic-Support Smoothing Escape Route

M19 tested the remaining possibility from M18: perhaps smoothing could resolve a shrinking spectral window while retaining Kim--Tao-compatible logarithmic or sub-polynomial support.

The central lemma is the Fourier-scaling identity. With the convention

\[
\widehat{h}(t)=\int h(r)e^{-irt}\,dr,
\]

a translated and rescaled window

\[
h_\delta(r)=\phi\left(\frac{r-r_0}{\delta}\right)
\]

has transform

\[
\widehat{h_\delta}(t)
=
\delta e^{-ir_0t}\widehat{\phi}(\delta t).
\]

Truncating geometric support to `|t| <= R` loses the scaled tail

\[
\int_{|u|>R\delta}|\widehat{\phi}(u)|\,du.
\]

Therefore fixed-quality localization requires `R delta` bounded below, and small standard leakage requires `R delta -> infinity`.

M19 translated this to the Kim--Tao spectral variable. For `Delta=n^{-d}` in fixed bulk energy, `delta_r` has exponent `d`, so logarithmic support gives

\[
R\delta_r\sim(\log n)n^{-d}\to 0
\]

for every fixed `d>0`. Polynomial support `R=n^\eta` resolves a bulk window only when `eta>=d`, and gives vanishing model leakage only when `eta>d`. At the edge, the threshold is halved to `eta>=d/2`.

![model leakage as a function of R delta_r for Gaussian and exponential Fourier-tail proxies](reports/figures/m19_kernel_leakage_profiles.png)

The M19 tradeoff table had 2,376 rows. Classification counts were:

| Classification | Rows |
|---|---:|
| `negative obstruction` | 1,116 |
| `fixed-quality only` | 168 |
| `small leakage asymptotically` | 1,092 |

All tested positive-`d` logarithmic-support rows were classified as negative obstruction.

![support-growth exponent needed to resolve shrinking bulk and edge windows](reports/figures/m19_support_resolution_phase_diagram.png)

### Finding 4: The Local-Window Route Has Reached a Clean Fork

The combined result of M16-M19 is now explicit.

Endpoint subtraction gives only mesoscopic or global-error-scale local-window control. A direct smoothed-window statistic would beat that only if a variance estimate satisfies

\[
\sqrt{\operatorname{Var} Z_n}
=
o(nF'(\Lambda)\Delta)
\]

in a regime below the endpoint threshold. Existing Kim--Tao test functions do not provide that statistic by simple retuning, because the necessary localization increases support and degree. Smoothing does not preserve logarithmic support for polynomially shrinking windows under standard Fourier scaling.

The remaining paths must change an assumption. The cycle records identify three possible changes:

- Prove a genuinely new long-support localized random-cover variance theorem.
- Develop a trace or pre-trace method with noncompact geometric tails and new tail estimates.
- Stop the shrinking local-window program under current Kim--Tao inputs and synthesize the obstruction as a negative result.

## Discussion

Cycles 28-30 did not produce a new local spectral-statistics theorem. Their contribution is a sharper map of what such a theorem would require.

The strongest positive output is M17's conditional variance proposition. It turns the vague phrase "localized trace variance" into a concrete inequality, with exponent thresholds. That gives future work a falsifiable target.

The strongest negative output is M19's Fourier-support obstruction. It closes the most plausible cheap escape route after M18: logarithmic-support smoothing cannot resolve polynomially shrinking windows inside the compactly supported Selberg-transform architecture. This makes the local-window branch structurally similar to the earlier aggregate-control branch. In both cases, the existing Kim--Tao architecture identifies the correct bottleneck but does not automatically supply the missing improvement.

The validated state after cycle 30 is therefore not "local windows are impossible." It is narrower: under the current compact-support test-function architecture and current random-cover variance inputs, polynomially shrinking local spectral windows are not reached by endpoint subtraction, cutoff retuning, or logarithmic-support smoothing.

## Open Questions

1. Can one prove a long-support localized random-cover variance theorem with support growing like `n^eta`, where `eta` is large enough to resolve the desired window but small enough that the random-cover expansion remains controlled?

2. Can a noncompact geometric-tail trace or pre-trace method replace compact support while keeping random-cover error terms summable?

3. Is there a useful intermediate theorem for smoothed counts with fixed-quality leakage, rather than vanishing leakage, that still gives meaningful spectral information?

4. Can edge windows exploit the weaker `eta>=d/2` threshold to produce a tractable theorem before bulk windows?

5. Should the next cycle pursue one of these altered assumptions, or should it write a negative synthesis closing the local-window route under the current Kim--Tao inputs?

## References

No `REFERENCES.md` file was present in the workspace during this report pass, so there are no global numbered references to continue. The report uses the following local source artifacts and session records:

- Kim and Tao source files: `2603.01127.pdf`, `2603.01127.txt`.
- M17 sessions: researcher `3c692209-62b8-4ae4-8f67-ae11518f55e1`, worker `1c71a754-9aea-4f05-84dd-8a217044c143`, auditor `2c824b5d-03c6-4cb6-813e-3aab351dc27c`.
- M18 sessions: researcher `b799f376-40ae-4ce1-9592-d1bd79d780cf`, worker `e90d9bed-c6ce-43b4-b8d4-531483d52879`, auditor `b068f57a-3935-4ffb-88c7-a1a5d8637745`.
- M19 sessions: researcher `126e3b5d-29b2-4b11-9175-e5fe1cc28036`, worker `8fec643c-4e8e-49c7-8f0c-c7869c46665e`, auditor `201e09c7-14bc-4c5f-ac88-8cb706ef3ab4`.
- Proof notes: `docs/proof_ledger/local_window_variance_input.md`, `docs/proof_ledger/test_function_localization_feasibility.md`, `docs/proof_ledger/smoothed_window_paley_wiener_obstruction.md`.
- Reports: `reports/extension_candidates/m17_local_window_variance_input.md`, `reports/extension_candidates/m18_test_function_localization_feasibility.md`, `reports/extension_candidates/m19_smoothed_window_paley_wiener_lemma.md`.
- Data artifacts under `data/extension_candidates/` for local-window variance, localization feasibility, smoothed-window leakage, and symbolic checks.

## Appendix: Implementation Details

### Code Organization

Cycles 28-30 added five campaign scripts:

| File | Lines | Role |
|---|---:|---|
| `scripts/analyze_local_window_variance_requirements.py` | 172 | M17 variance exponent grid and phase diagram. |
| `scripts/analyze_schreier_window_variance_benchmark.py` | 138 | M17 Schreier toy variance benchmark. |
| `scripts/analyze_test_function_localization_tradeoffs.py` | 261 | M18 support, degree, and trace/pre-trace feasibility map. |
| `scripts/analyze_smoothed_window_leakage.py` | 251 | M19 leakage and support-resolution diagnostics. |
| `scripts/certify_smoothed_window_scaling.wls` | 51 | M19 Wolfram symbolic certificate. |

Cycles 28-30 added three test files:

| File | Lines | Role |
|---|---:|---|
| `tests/test_local_window_variance_requirements.py` | 76 | Tests M17 Chebyshev and endpoint-beating logic. |
| `tests/test_test_function_localization_tradeoffs.py` | 82 | Tests M18 lambda-to-r conversion, edge handling, and loss coverage. |
| `tests/test_smoothed_window_leakage.py` | 70 | Tests M19 leakage monotonicity and support thresholds. |

### Generated Data

The generated cycle datasets were:

| File | Rows including header |
|---|---:|
| `data/extension_candidates/local_window_variance_requirements.csv` | 361 |
| `data/extension_candidates/schreier_window_variance_benchmark.csv` | 17 |
| `data/extension_candidates/test_function_localization_tradeoffs.csv` | 331 |
| `data/extension_candidates/test_function_localization_regime_summary.csv` | 19 |
| `data/extension_candidates/smoothed_window_leakage_tradeoffs.csv` | 2,377 |
| `data/extension_candidates/smoothed_window_leakage_summary.csv` | 19 |
| `data/extension_candidates/smoothed_window_symbolic_checks.csv` | 8 |

### Validation Results

M17 validation passed with no critical or moderate findings. The auditor reran Python compilation, both analyzers, the M17 test file, figure checks, `promise_check`, and `org_check`.

M18 validation passed after two moderate repairs: support metadata was corrected to the paper's `\Lambda_0^{-1/2}q` dependence, and exact-edge inverse-width support was corrected to the `\Delta^{-1/2}` scale. The auditor regenerated CSVs and figures and added regression coverage.

M19 validation passed with no critical or moderate findings. The auditor reran the Wolfram certificate, Python compilation, analyzer, tests, figure checks, `promise_check`, and `org_check`.

After the manifest update for this report, `promise_check` exited 0 with `events: 78, plan milestones: 19`. Its warnings were historical: an old noncanonical `docs/paper_map/` artifact and orphan prior cycle reports. `org_check` exited 0 with historical warnings about root paper/live-run files and older figures under `docs/`.

### Manifest Snapshot

`MANIFEST.md` was replaced with a current snapshot. There was no `## Key Files` section to preserve.

Current manifest totals:

| Metric | Value |
|---|---:|
| Campaign scripts | 32 |
| Campaign script lines | 8,209 |
| Campaign test files | 20 |
| Campaign test lines | 1,609 |
| Markdown/DOT/PNG documentation artifacts under `docs/`, `reports/`, and `audits/` | 116 |
| PNG figures under `reports/figures/` | 49 |
| Canonical CSV datasets under `data/` | 54 |
| Promise ledger events | 78 |

### Cross-Reference Map

M16 local-window endpoint subtraction fed M17's variance target through `docs/proof_ledger/local_window_from_rigidity.md` to `docs/proof_ledger/local_window_variance_input.md`.

M17's variance target fed M18's test-function feasibility map through `docs/proof_ledger/local_window_variance_input.md` to `docs/proof_ledger/test_function_localization_feasibility.md`.

M18's support/localization obstruction fed M19's smoothing check through `docs/proof_ledger/test_function_localization_feasibility.md` to `docs/proof_ledger/smoothed_window_paley_wiener_obstruction.md`.

M19 closes the logarithmic-support escape route and points the next cycle toward either long-support random-cover variance, noncompact geometric-tail trace methods, or a negative synthesis of the local-window branch.
