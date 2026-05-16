---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 25-27"
date: "2026-05-16"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 25-27

## Abstract

Cycles 25-27 closed one extension route and opened another. Cycle 25, milestone M14, quantified how strong an external decay estimate would need to be after earlier cycles showed that product-ratio algebra and internal cancellation do not control the dominant aggregate terms. Cycle 26, milestone M15, translated that requirement back into Kim--Tao proof objects and found that a real coefficient-variation theorem would attack the correct bottleneck, but bare Selberg/geodesic weights do not appear strong enough in the tested proxy model. Cycle 27, milestone M16, pivoted to local spectral windows and derived what follows directly from Kim--Tao's global Weyl and rigidity estimates.

The result is a clearer map of two missing inputs. The aggregate-control route needs a genuine weighted coefficient-variation or probability-law decay estimate for the actual Kim--Tao quotient families. The local-window route needs localized trace-window variance or correlation estimates; endpoint subtraction of the global Weyl law gives only mesoscopic/global control and does not reach mean-spacing statistics.

## Introduction

The research campaign centers on Kim and Tao's paper `2603.01127`, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*. Earlier cycles reconstructed the main proof architecture and then built a Phase II extension path around product-ratio polynomial bounds, quotient families, and aggregate control.

By the start of Cycle 25, the aggregate-control path had reached a specific obstruction. M12 had produced a conditional aggregate theorem template: after fixing the exponent stratum \(d=C-V\), where \(C\) is the number of constraints and \(V\) is the number of vertices in the folded skeleton, per-template product-ratio bounds control an aggregate only through a total-variation or coefficient-variation hypothesis. M13 then showed that the dominant toy stratum did not exhibit robust coefficient cancellation. Cycle 25 therefore asked how strong an external decay hypothesis would have to be.

Cycle 26 asked whether that calibrated decay requirement had a real attachment point in Kim--Tao's proof. Cycle 27 then pivoted away from additional toy aggregate variants and asked what local spectral-window consequences already follow from the validated global Weyl and rigidity estimates.

## Approach

The work in these cycles used the general reporting structure because the topic spans proof reconstruction, computational diagnostics, and extension planning.

Cycle 25 used the M11 record-level trace-like quotient data, the M12 \(d=C-V\) stratification, and the M13 cancellation diagnostics. It introduced hypothetical decay weights and measured their effect on total variation, coefficient absolute variation, signed sums, and the M12 total-variation proxy.

Cycle 26 mapped the M14 requirement onto Kim--Tao proof objects: Lemma 3.3, Corollary 3.4, Proposition 3.1, and Proposition 4.2. It also compared M14's required exponential length decay against crude reduced-word, primitive-geodesic, Selberg-weight, and test-function cutoff models.

Cycle 27 derived local spectral-window corollaries by subtracting two endpoint Weyl estimates and by applying eigenvalue rigidity as a deterministic window-inclusion statement. It separated the spectral edge \(\Lambda=1/4\) from the bulk, because the limiting density has zero derivative at the edge.

## Source Inventory and Timeline

The source inventory below is chronological. Session IDs are included for traceability.

| Cycle | Session | Date | Role | Contents |
|---:|---|---|---|---|
| 25 | `8723aee6-ac09-47d9-b2d9-f1841b3a4153` | 2026-05-16 01:40 UTC | researcher | Opened M14, specifying external polynomial-length, exponential-length, folded-complexity, and rank-only decay models after M13 ruled out robust cancellation. |
| 25 | `04d5343e-76c4-4ba9-9192-395a59597d8e` | 2026-05-16 01:51 UTC | worker | Built M14 report, analyzer, tests, CSVs, and three figures; updated plan and ledger. |
| 25 | `17d61626-6218-4e3f-a819-80e1e02376b8` | 2026-05-16 01:59 UTC | auditor | Validated M14 with no critical or moderate findings. |
| 26 | `e4518031-3ac7-4127-bdef-551e53b19022` | 2026-05-16 02:16 UTC | researcher | Opened M15 to translate M12-M14 requirements into Kim--Tao proof objects and exponent-flow consequences. |
| 26 | `27e41af8-565b-4b66-9abe-5b7851159132` | 2026-05-16 02:21 UTC | worker | Built M15 bridge note, conditional proof-ledger note, growth/weight comparison script, CSVs, and two figures. |
| 26 | `a21c719a-6487-4d11-b471-64a18f2bf40c` | 2026-05-16 02:25 UTC | auditor | Validated M15 with no critical or moderate findings. |
| 27 | `ace04bed-16c2-4600-b371-ac2b4c55995c` | 2026-05-16 02:38 UTC | researcher | Opened M16 as a pivot to local/mesoscopic spectral-window consequences of Kim--Tao's Weyl and rigidity estimates. |
| 27 | `84d69180-7573-4763-a6f3-20e8c020092d` | 2026-05-16 02:48 UTC | worker | Built M16 proof note, report, analyzer, tests, CSVs, and two figures. |
| 27 | `8e785ba8-1366-4bb8-8a95-2b120cd12856` | 2026-05-16 02:53 UTC | auditor | Validated M16 after repairing one displayed formula in the proof note. |

No `REFERENCES.md` file was present in the workspace. The references section therefore lists local papers, reports, proof notes, data artifacts, figures, and sessions rather than continuing a global numbered bibliography.

## Findings

### Finding 1: External Decay Must Be Stronger Than Rank Filtering

Cycle 25 showed that the remaining aggregate obstruction is not removed by rank labels alone. The M14 model kept the M11 record-level trace-like quotient data, the M12 fixed \(d=C-V\) strata, and coefficient orders \(k=1,\dots,4\). It tested four decay models on each record \(T=(u,v)\):

\[
\sum |w_T|D(T),\qquad
\sum |w_Tc_{T,k}|D(T),\qquad
\left|\sum w_Tc_{T,k}D(T)\right|,\qquad
L^{2k}\sum |w_T|D(T).
\]

Here \(w_T\) is the template weight, \(c_{T,k}\) is the order-\(k\) normalized product-ratio coefficient, \(D(T)\) is the hypothetical decay factor, and \(L^{2k}\sum |w_T|D(T)\) is the M12-style total-variation proxy.

The dominant diagnostic stratum was the unweighted \(d=1\) rank-two/noncyclic remainder. For coefficient absolute variation, M14 found these first tested parameters giving at-most-linear fitted growth:

| \(k\) | baseline slope | polynomial length \(\sigma\) | exponential length \(\beta\) | folded complexity \(\tau\) | rank-only |
|---:|---:|---:|---:|---:|---|
| 1 | 5.033 | 10.0 | 1.6 | 8.0 | none |
| 2 | 5.195 | 9.0 | 1.5 | 7.5 | none |
| 3 | 6.578 | none | 1.7 | 9.0 | none |
| 4 | 7.121 | none | 1.9 | 10.0 | none |

No tested decay made the dominant coefficient absolute variation non-growing. Exponential length decay was the most efficient tested axis for reaching at-most-linear growth across \(k\le4\). Polynomial length and folded-complexity decay required large exponents, and rank-only decay did not change growth slopes inside the pure rank-two remainder because every surviving dominant record had the same rank proxy.

![fitted growth slopes versus decay parameter for order-one coefficient absolute variation in the unweighted d=1 rank-two remainder](reports/figures/m14_decay_threshold_curves.png)

The order-one comparison separated total variation from coefficient absolute variation. Decayed total variation reached at-most-linear growth at \(\sigma=2.5\), \(\beta=0.6\), or \(\tau=2.0\). Coefficient absolute variation and signed magnitude required \(\sigma=10.0\), \(\beta=1.6\), or \(\tau=8.0\). The M12 proxy \(L^{2k}\sum |w_T|D(T)\) did not reach at-most-linear growth under the tested grid.

![decayed TV, coefficient AV, signed magnitude, and M12 TV proxy in the L=5 unweighted d=1 rank-two stratum under representative external decay models](reports/figures/m14_dominant_stratum_decay_heatmap.png)

![M12 TV proxy, coefficient AV, and signed sums under representative decay parameters](reports/figures/m14_bound_mode_decay_comparison.png)

M14's decision was conservative. The data support a calibrated requirement, not an internal proof. A future Kim--Tao-facing estimate would need coefficient-variation decay comparable in this restricted model to

\[
D_\beta(T)=\exp(-\beta(|u|+|v|)),\qquad \beta\approx1.6\text{ to }1.9
\]

for coefficient orders \(k\le4\). M11-M13 do not prove such a decay estimate; they identify it as the kind of external input needed.

### Finding 2: The Aggregate Bridge Attaches to Real Kim--Tao Proof Objects, But Remains Conditional

Cycle 26 translated the M12-M14 aggregate findings into Kim--Tao-facing terms. M15 mapped the toy-model quantities to four proof objects:

| Paper object | M12/M14 attachment | Missing estimate |
|---|---|---|
| Proposition 3.1 | Trace-side variance aggregate after polynomial packaging | Weighted coefficient-variation bound before Markov interpolation. |
| Lemma 3.3 | Fixed two-cycle labelled graph expansion | No termwise gap; the gap is aggregate summability across quotient families and geodesic pairs. |
| Corollary 3.4 | Full weighted two-trace second moment | Coefficient-variation decay for the polynomial numerator after geometry weights and denominator normalization. |
| Proposition 4.2 | Eight-loop pre-trace aggregate after subtracting \(S\) | Weighted coefficient-variation decay for the eight-word numerator, compatible with MP23 rank-two decay. |

The conditional proposition stated in M15 was:

\[
P_{q,d}(x)=\sum_{T\in\mathcal F_{q,d}}\omega_T R_T(x),
\]

where \(T\) ranges over folded quotient templates in a fixed \(d=C-V\) stratum, \(\omega_T\) includes Selberg or pre-trace weights and probability-law normalization, and \(R_T(x)\) is the exposed normalized product-ratio factor. If, for fixed \(k\),

\[
\sum_{T\in\mathcal F_{q,d}} |\omega_T[x^k]R_T(x)|\le B_{d,k}(q),
\]

then the M12 aggregate step replaces the generic \(L^{2k}TV_{q,d}\) envelope by \(B_{d,k}(q)\). If this controls the polynomial numerator directly at \(x=1/n\), the trace-side Markov bottleneck \(q^{2\kappa}\) and the pre-trace bottleneck \(q^{4\kappa}\) are replaced by the corresponding \(B(q)\)-scale.

The conditional proof-ledger note `docs/proof_ledger/conditional_decay_to_rigidity_improvement.md` traced what this would mean for exponents. For representative \(\kappa=5\) and \(\epsilon=0.1\), bounded \(q\)-loss scenarios improved the proxy theorem exponents:

| theorem path | current alpha | bounded-loss alpha | improvement |
|---|---:|---:|---:|
| Theorem 1 rigidity | 0.003766 | 0.007663 | 2.03x |
| Theorem 2 delocalization | 0.001488 | 0.002841 | 1.91x |

The improvement is conditional and moderate. Other axes remain limiting: smooth cutoff derivatives, the Weyl-edge conversion for Theorem 1, eighth-power cutoff derivatives, and local-mass-to-\(L^\infty\) conversion for Theorem 2.

M15 also compared the required M14 exponential decay against crude hyperbolic growth models. Bare Selberg decay \(1/\sinh(\ell/2)\sim\exp(-\ell/2)\) did not meet the M14 coefficient-absolute-variation threshold once word or geodesic growth was included. For reduced-word growth at conversion constants \(c=1,2,3\), the bare effective beta values were \(-0.599\), \(-0.099\), and \(0.401\), all below the order-one M14 threshold \(\beta\approx1.6\). Primitive-geodesic and combined growth proxies were worse without extra decay.

![effective Selberg/test-function decay after growth compared with M14 thresholds](reports/figures/m15_decay_requirement_vs_selberg_growth.png)

![representative theorem alpha under current and bounded Markov-loss scenarios](reports/figures/m15_conditional_exponent_scenarios.png)

The M15 decision was to stop extending the toy aggregate enumeration by default. The aggregate route remains meaningful only if a future cycle directly attempts a real Kim--Tao coefficient-variation theorem or an obstruction to such a theorem. Larger independent-permutation toy variants were judged unlikely to change the conclusion.

### Finding 3: Endpoint Subtraction Gives Local Windows Only Above the Global Error Scale

Cycle 27 pivoted to local spectral windows. The proof note `docs/proof_ledger/local_window_from_rigidity.md` defined

\[
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr,\qquad \Lambda\ge1/4.
\]

Using the Kim--Tao Weyl-law ledger from M2,

\[
N_{X_n}([1/4,\Lambda])
=(2g-2)nF(\Lambda)+O\left(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}\right),
\]

M16 subtracted the estimates at \(\Lambda+\Delta\) and \(\Lambda\). The resulting local-window corollary is

\[
N_{X_n}([\Lambda,\Lambda+\Delta])
=(2g-2)n\left(F(\Lambda+\Delta)-F(\Lambda)\right)
+O\left(n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}\right).
\]

The audit found and fixed one moderate documentation defect: the displayed formula in the proof note initially omitted the `+` before the big-O term. The report, analyzer, and surrounding text already used the intended additive-error interpretation. The auditor repaired the display and recorded ledger event `f9f01d91-d4a1-4e19-8237-6be46e3234b4`.

The corollary is nontrivial only when the main term beats the inherited endpoint error:

\[
(2g-2)\left(F(\Lambda+\Delta)-F(\Lambda)\right)
\gg n^{-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}.
\]

In the bulk,

\[
F'(\Lambda)=\frac12\tanh\left(\pi\sqrt{\Lambda-1/4}\right),
\]

so for \(\Delta\ll\Lambda-1/4\),

\[
\Delta\gg
\frac{n^{-\alpha_W}\Lambda^{1/2+\epsilon}}
{(2g-2)F'(\Lambda)}.
\]

The edge is different because \(F'(1/4)=0\). At \(\Lambda=1/4\),

\[
F(1/4+\Delta)-F(1/4)
=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
\]

so the edge scale behaves like \(n^{-2\alpha_W/3}\), up to normalized constants and mild energy factors.

M16's normalized threshold probe used representative parameters \(\alpha_W=0.006\), \(\alpha_R=0.004\), \(\epsilon=0.1\), and \(g=2\). These are scale-model values, not asserted theorem constants. For \(n=10^6\), representative rows were:

| regime | \(\Lambda\) | \(F'(\Lambda)\) | Weyl threshold \(\Delta_W\) | rigidity displacement \(\delta_R\) | mean spacing |
|---|---:|---:|---:|---:|---:|
| edge | 0.25 | 0 | 5.143 | 0.412 | undefined |
| moderate bulk | 1 | 0.496 | 5.836 | 0.946 | \(1.01\cdot10^{-6}\) |
| bulk | 4 | 0.500 | 8.297 | 2.174 | \(1.00\cdot10^{-6}\) |
| high energy | 25 | 0.500 | 17.448 | 6.528 | \(1.00\cdot10^{-6}\) |

The comparison shows that endpoint-subtraction windows are much larger than the mean-spacing proxy at these representative exponents.

![normalized Weyl-subtraction and rigidity thresholds compared with mean spacing](reports/figures/m16_window_threshold_phase_diagram.png)

![density F prime near the spectral edge compared with the square-root edge asymptotic and high-energy limit](reports/figures/m16_edge_vs_bulk_density.png)

### Finding 4: Rigidity Gives Window Inclusion, Not Microscopic Multiplicity Control

M16 also translated eigenvalue rigidity into a deterministic window-inclusion statement. If

\[
|\lambda_j(X_n)-\lambda_j|
\le C_\epsilon \Lambda^{1/2+\epsilon}n^{-\alpha_R}
=:\delta_R(\Lambda,n),
\]

then, on the rigidity event,

\[
\#\{j:\lambda_j(X_n)\in[\Lambda,\Lambda+\Delta]\}
\le
\#\{j:\lambda_j\in[\Lambda-\delta_R,\Lambda+\Delta+\delta_R]\}.
\]

A corresponding lower bound uses the contracted window \([\Lambda+\delta_R,\Lambda+\Delta-\delta_R]\) when \(\Delta>2\delta_R\).

This transfers count estimates only for windows larger than the rigidity displacement. At the displacement scale itself, the deterministic Weyl mass in the bulk is roughly

\[
nF'(\Lambda)\delta_R
\asymp n^{1-\alpha_R}F'(\Lambda)\Lambda^{1/2+\epsilon},
\]

which is far larger than \(O(1)\) for the current exponent sizes. M16 therefore does not imply sharp multiplicity bounds or microscopic local statistics.

## Discussion

Cycles 25-27 clarified the campaign's extension landscape.

The aggregate-control route is not mathematically void. M15 shows that a true weighted coefficient-variation estimate would enter the Kim--Tao proof at meaningful bottlenecks and could improve theorem-level exponent algebra. The problem is that the campaign has not proved such an estimate, and the tested proxies do not make it look automatic. M14 quantified how strong the missing decay would need to be; M15 showed that bare Selberg decay is not enough once crude growth is included.

The local-window route gives a second, independent filter. Kim--Tao's global Weyl and rigidity outputs do imply local-window statements, but only above inherited global-error scales. They do not reach mean-spacing statistics by endpoint subtraction. A future local theorem would need new input: a localized trace-window variance estimate, a correlation estimate, or another method that avoids paying two global endpoint errors.

Together, these cycles leave two precise research doors open:

- aggregate quotient control through a genuine coefficient-variation or probability-law decay theorem;
- local spectral statistics through localized trace/pre-trace variance or correlation bounds.

They also close a class of lower-value continuations: larger toy aggregate enumerations without a route to the actual Kim--Tao probability law, and endpoint-subtraction corollaries presented as local statistics.

## Open Questions

1. Can one prove a fixed-\(d\), weighted coefficient-variation estimate for the actual quotient-family polynomial numerator in Corollary 3.4 or Proposition 4.2?

2. Can MPvH/Witten-zeta normalization, Nau boundedness, or MP23 rank-two decay be sharpened or reorganized to imply coefficient variation rather than only aggregate probability control?

3. Is there a localized trace-window variance estimate that controls spectral counts below the global Weyl endpoint-error threshold?

4. Can pre-trace methods produce correlation estimates strong enough to approach a power of the mean spacing?

5. Is there an obstruction theorem showing that the M14-scale coefficient-variation decay cannot hold under realistic Kim--Tao quotient-family growth?

## References

No `REFERENCES.md` file was present. The report cites the following local sources and session records.

Local paper sources:
- `2603.01127.pdf`
- `2603.01127.txt`

Cycle 25 sources:
- Researcher session `8723aee6-ac09-47d9-b2d9-f1841b3a4153`
- Worker session `04d5343e-76c4-4ba9-9192-395a59597d8e`
- Auditor session `17d61626-6218-4e3f-a819-80e1e02376b8`
- `reports/extension_candidates/m14_external_decay_thresholds.md`
- `data/extension_candidates/external_decay_threshold_grid.csv`
- `data/extension_candidates/external_decay_sufficient_exponents.csv`
- `data/extension_candidates/external_decay_dominant_profiles.csv`

Cycle 26 sources:
- Researcher session `e4518031-3ac7-4127-bdef-551e53b19022`
- Worker session `27e41af8-565b-4b66-9abe-5b7851159132`
- Auditor session `a21c719a-6487-4d11-b471-64a18f2bf40c`
- `reports/extension_candidates/m15_kim_tao_bridge_requirement.md`
- `docs/proof_ledger/conditional_decay_to_rigidity_improvement.md`
- `data/extension_candidates/kim_tao_decay_requirement_table.csv`
- `data/extension_candidates/conditional_exponent_scenarios.csv`

Cycle 27 sources:
- Researcher session `ace04bed-16c2-4600-b371-ac2b4c55995c`
- Worker session `84d69180-7573-4763-a6f3-20e8c020092d`
- Auditor session `8e785ba8-1366-4bb8-8a95-2b120cd12856`
- `docs/proof_ledger/local_window_from_rigidity.md`
- `reports/extension_candidates/m16_local_spectral_window_corollaries.md`
- `data/extension_candidates/local_window_thresholds.csv`
- `data/extension_candidates/local_window_regime_summary.csv`

## Appendix: Implementation Details

### Code Organization

Cycle 25 / M14 added:
- `reports/extension_candidates/m14_external_decay_thresholds.md` — 102 lines.
- `scripts/model_external_decay_thresholds.py` — 471 lines.
- `tests/test_external_decay_thresholds.py` — 126 lines.
- `data/extension_candidates/external_decay_threshold_grid.csv` — 97,921 lines including header.
- `data/extension_candidates/external_decay_sufficient_exponents.csv` — 3,457 lines including header.
- `data/extension_candidates/external_decay_dominant_profiles.csv` — 26 lines including header.
- `reports/figures/m14_decay_threshold_curves.png` — 1600 x 960.
- `reports/figures/m14_dominant_stratum_decay_heatmap.png` — 1440 x 768.
- `reports/figures/m14_bound_mode_decay_comparison.png` — 1600 x 960.

Cycle 26 / M15 added:
- `reports/extension_candidates/m15_kim_tao_bridge_requirement.md` — 89 lines.
- `docs/proof_ledger/conditional_decay_to_rigidity_improvement.md` — 83 lines.
- `scripts/test_selberg_weight_vs_template_growth.py` — 243 lines.
- `data/extension_candidates/kim_tao_decay_requirement_table.csv` — 379 lines including header.
- `data/extension_candidates/conditional_exponent_scenarios.csv` — 49 lines including header.
- `reports/figures/m15_decay_requirement_vs_selberg_growth.png` — 2520 x 720.
- `reports/figures/m15_conditional_exponent_scenarios.png` — 2160 x 720.

Cycle 27 / M16 added:
- `docs/proof_ledger/local_window_from_rigidity.md` — 106 lines.
- `reports/extension_candidates/m16_local_spectral_window_corollaries.md` — 80 lines.
- `scripts/analyze_local_window_thresholds.py` — 273 lines.
- `tests/test_local_window_thresholds.py` — 72 lines.
- `data/extension_candidates/local_window_thresholds.csv` — 31 lines including header.
- `data/extension_candidates/local_window_regime_summary.csv` — 7 lines including header.
- `reports/figures/m16_window_threshold_phase_diagram.png` — 2160 x 810.
- `reports/figures/m16_edge_vs_bulk_density.png` — 1260 x 810.

### Validation Results

Cycle 25 / M14 worker and auditor checks:
- `python3 -m py_compile scripts/model_external_decay_thresholds.py tests/test_external_decay_thresholds.py`
- `python3 scripts/model_external_decay_thresholds.py`
- `python3 tests/test_external_decay_thresholds.py`
- Figure checks for all three M14 figures.
- `python3 -m long_exposure.tools.promise_check .`
- `python3 -m long_exposure.tools.org_check .`

M14 audit spot checks confirmed:
- Dominant `L=5`, unweighted, `d=1`, rank-two, order-one baseline reproduced TV `200`, coefficient AV `800`, and signed sum `-800`.
- At-most-linear coefficient AV thresholds matched report values: \(k=1\) \(\sigma=10\), \(\beta=1.6\), \(\tau=8\); \(k=2\) \(\sigma=9\), \(\beta=1.5\), \(\tau=7.5\); \(k=3\) \(\beta=1.7\), \(\tau=9\); \(k=4\) \(\beta=1.9\), \(\tau=10\).

Cycle 26 / M15 worker and auditor checks:
- `python3 -m py_compile scripts/test_selberg_weight_vs_template_growth.py`
- `python3 scripts/test_selberg_weight_vs_template_growth.py`
- Figure checks for both M15 figures.
- `python3 -m long_exposure.tools.promise_check .`
- `python3 -m long_exposure.tools.org_check .`

M15 audit spot checks confirmed:
- 378 decay rows and 48 exponent-scenario rows regenerated.
- Reduced-word bare effective beta at \(c=1,2,3\): `-0.598612`, `-0.098612`, `0.401388`.
- Primitive-geodesic bare effective beta at \(c=1,2\): `-0.5`, `-1`.
- Representative \(\kappa=5\), \(\epsilon=0.1\) alpha values matched the report.

Cycle 27 / M16 worker and auditor checks:
- `python3 -m py_compile scripts/analyze_local_window_thresholds.py tests/test_local_window_thresholds.py`
- `python3 scripts/analyze_local_window_thresholds.py`
- `python3 tests/test_local_window_thresholds.py`
- Figure checks for both M16 figures.
- `python3 -m long_exposure.tools.promise_check .`
- `python3 -m long_exposure.tools.org_check .`

M16 audit spot checks confirmed:
- 30 threshold rows and 6 summary rows.
- Bulk density, mean-spacing, and rigidity formulas matched to roundoff.
- `m16_window_threshold_phase_diagram.png` grayscale standard deviation `41.094568`.
- `m16_edge_vs_bulk_density.png` grayscale standard deviation `36.809504`.

After updating `MANIFEST.md`, reporter validation was rerun:
- `python3 -m long_exposure.tools.promise_check .` exited 0 with `events: 68, plan milestones: 16`.
- `python3 -m long_exposure.tools.org_check .` exited 0.
- Remaining warnings were historical and nonblocking: noncanonical early `docs/paper_map/` ledger path, orphan prior periodic reports, root paper/live prompt files, and older figures under `docs/`.

### Manifest Snapshot

`MANIFEST.md` was replaced with a current snapshot. It has 141 lines and records:
- 27 campaign scripts.
- 7,336 script lines.
- 17 test files.
- 1,381 test lines.
- 103 Markdown/DOT/PNG documentation artifacts under `docs/`, `reports/`, and `audits/`.
- 43 PNG figures under `reports/figures/`.
- 47 canonical CSV datasets under `data/`.
- 68 promise ledger events.

No `## Key Files` section was present, so no final-reporter-owned section needed preservation.

### Session Reference Map

| Milestone | Researcher | Worker | Auditor |
|---|---|---|---|
| M14 external decay thresholds | `8723aee6-ac09-47d9-b2d9-f1841b3a4153` | `04d5343e-76c4-4ba9-9192-395a59597d8e` | `17d61626-6218-4e3f-a819-80e1e02376b8` |
| M15 Kim--Tao bridge requirement | `e4518031-3ac7-4127-bdef-551e53b19022` | `27e41af8-565b-4b66-9abe-5b7851159132` | `a21c719a-6487-4d11-b471-64a18f2bf40c` |
| M16 local spectral window corollaries | `ace04bed-16c2-4600-b371-ac2b4c55995c` | `84d69180-7573-4763-a6f3-20e8c020092d` | `8e785ba8-1366-4bb8-8a95-2b120cd12856` |

### Cross-Reference Map

| Origin | Consuming artifact | Role |
|---|---|---|
| M13 cancellation diagnostics | M14 external decay thresholds | M13 ruled out robust cancellation, motivating external decay models. |
| `scripts/model_external_decay_thresholds.py` | M14 CSVs and figures | Produced decay grids, sufficient exponents, dominant profiles, and M14 plots. |
| M14 external decay thresholds | M15 Kim--Tao bridge requirement | Supplied calibrated decay requirements for actual proof-object mapping. |
| `scripts/test_selberg_weight_vs_template_growth.py` | M15 CSVs and figures | Compared M14 thresholds with growth/weight proxies and exponent scenarios. |
| M15 bridge decision | M16 local spectral window corollaries | Motivated pivot away from larger toy aggregate variants. |
| `docs/proof_ledger/local_window_from_rigidity.md` | M16 report and analyzer | Supplied endpoint-subtraction formulas, edge/bulk density split, and rigidity-window inclusion. |
| `scripts/analyze_local_window_thresholds.py` | M16 CSVs and figures | Computed local-window thresholds, rigidity displacements, mean-spacing proxies, and regime summaries. |
