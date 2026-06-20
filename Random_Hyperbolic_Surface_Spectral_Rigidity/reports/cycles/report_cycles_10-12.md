---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 10-12"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 10-12

## Abstract

Cycles 10-12 moved the campaign from validated computational probes toward milestone closure and first formal certification. Cycle 10 added an operator-level toy model: random permutations generate finite Schreier adjacency operators, and their normalized eigenvalue-window counts and centered trace moments were measured across $n=100,200,400,800$. Cycle 11 consolidated all five M3 computational slices into a benchmark suite and marked `M3-computational-probes` validated. Cycle 12 opened `M4-formal-certification` by certifying the exact finite expectation identity behind the labelled-template embedding counts used in M3.

The main result of these cycles is a coherent chain of evidence with clear scope. M3 is now validated as a reproducible finite random-permutation and Schreier-operator benchmark suite, not as a theorem about hyperbolic surfaces. M4 has one validated narrow certification: the labelled-template expectation formula

\[
\mathbf{E}\,\mathrm{InjEmb}_n(H)
=
(n)_{|V|}
\prod_a \frac{1}{(n)_{|C_a(H)|}},
\]

when each normalized label constraint set $C_a(H)$ is a partial injection and $n \ge |V|$, with zero expectation for conflicts or too few vertices. The strongest next research target remains the Markov/interpolation loss identified in M2 and stress-tested in M3.

## Introduction

The broader research campaign studies Kim and Tao's paper `2603.01127`, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model." Earlier cycles mapped the paper, reconstructed the proof architecture, and built a computational ladder for finite random-permutation analogues of the trace and polynomial-method mechanisms. Cycles 7-9 had already established three key M3 slices: folded quotient profiles, direct labelled-graph embeddings, and polynomial-window diagnostics.

Cycles 10-12 continued from that point. The immediate question was whether the finite combinatorial probes could be connected to an actual operator statistic, then whether the M3 computational evidence was mature enough to close the milestone, and finally whether one small piece of the benchmark suite could be certified exactly.

This report follows the work chronologically:

- Cycle 10 built the Schreier/random-cover spectral toy probe.
- Cycle 11 synthesized and closed M3.
- Cycle 12 certified the labelled-template embedding expectation identity for M4.

The report is based on the supplied cycle sessions, the Cycle 12 audit report, generated artifacts in the workspace, and the updated `MANIFEST.md`. No `REFERENCES.md` file was present, so the References section cites local paper files, sessions, and artifacts rather than global numbered bibliography entries.

## Approach

The cycles used a general research workflow rather than a single mathematical proof. The relevant terms are:

- A **Schreier adjacency operator** is the adjacency matrix built from a group action. In Cycle 10, two random permutations $a,b$ on $[n]$ define
  \[
  A = P_a + P_a^T + P_b + P_b^T.
  \]
  Loops and multiple edges are retained, so every row sum is exactly $4$.

- A **spectral window count** is the normalized fraction of eigenvalues lying in a fixed interval, such as $[0,2]$ or $[2,4]$.

- A **centered trace moment** is a trace statistic such as $\mathrm{tr}(A^k)/n$ after subtracting the infinite 4-regular tree closed-walk baseline.

- A **labelled-template embedding** is an injective placement of the vertices of a finite labelled directed graph into $[n]$ such that each labelled edge is realized by the corresponding random permutation or inverse permutation.

- A **partial injection constraint set** means that for a fixed label $a$, no source is forced to two different targets and no two sources are forced to the same target.

The work remained conservative about scope. The Schreier model is a graph-spectral toy analogue, not a discretization of the hyperbolic Laplacian. The M4 certified identity is a finite combinatorial expectation formula, not a certification of the Kim--Tao trace expansion or of the imported MPvH/MP23 inputs.

## Source Inventory and Timeline

### Cycle 10: Schreier Spectral Toy Probe

Cycle 10 was directed by researcher session `7fe5106f-b4b2-48b2-a9e0-bef0631ff27a`. The research brief identified the missing M3 layer: previous probes studied fixed points, quotient profiles, labelled embeddings, and polynomial-window fits, but not an actual operator spectrum. The requested probe was a random Schreier graph model built from two independent random permutations.

Worker session `566c2736-3f4c-409a-b14c-060d0bcdd337` produced:

- `scripts/probe_schreier_spectral_toy.py`
- `tests/test_schreier_spectral_toy.py`
- `data/polynomial_method/schreier_spectral_toy_trials.csv`
- `data/polynomial_method/schreier_spectral_toy_summary.csv`
- `data/polynomial_method/schreier_spectral_window_fits.csv`
- `reports/figures/m3_schreier_spectral_eigenvalue_histograms.png`
- `reports/figures/m3_schreier_spectral_trace_scaling.png`
- `reports/figures/m3_schreier_spectral_window_fit.png`
- `reports/computational_probes/m3_schreier_spectral_toy.md`

The full run used `n=100,200,400,800`, `30` trials per size, seed `20260515`, and wrote `2160` trial-observable rows, `72` summary rows, and `20` polynomial-window fit rows.

![Empirical normalized adjacency spectra across n, showing stabilization of the Schreier toy spectral distribution.](reports/figures/m3_schreier_spectral_eigenvalue_histograms.png)

The selected spectral means were stable across the tested range:

| Observable | n=100 | n=200 | n=400 | n=800 |
|---|---:|---:|---:|---:|
| `spectral_radius_nontrivial` | 3.4224 | 3.4349 | 3.4507 | 3.4534 |
| `window_neg_edge` | 0.2133 | 0.2142 | 0.2167 | 0.2163 |
| `window_pos_mid` | 0.2787 | 0.2808 | 0.2824 | 0.2833 |
| `window_pos_edge` | 0.2267 | 0.2208 | 0.2191 | 0.2174 |

![Centered trace-moment means and variances versus n for small even moments, using infinite 4-regular tree moments as the baseline.](reports/figures/m3_schreier_spectral_trace_scaling.png)

Centered trace moments decreased after subtracting infinite 4-regular tree moments:

| Observable | n=100 | n=200 | n=400 | n=800 |
|---|---:|---:|---:|---:|
| `centered_trace_moment_2` | 0.1573 | 0.0713 | 0.0433 | 0.0163 |
| `centered_trace_moment_4` | 2.9067 | 1.3220 | 0.7427 | 0.3233 |
| `centered_trace_moment_6` | 47.2193 | 21.9683 | 11.8943 | 5.4633 |
| `centered_trace_moment_8` | 745.0453 | 353.3093 | 187.3477 | 88.5027 |

![Low-degree polynomial-window fits in x = 1/n for selected spectral observables, compared with held-out values.](reports/figures/m3_schreier_spectral_window_fit.png)

The polynomial-window result was mixed. Degree-1 fits were stable for smooth spectral windows. Degree-3 fits, which had been useful for the low-noise Cycle 9 labelled-embedding benchmark, were underdetermined on only four spectral sample sizes. For example, `window_pos_mid` had degree-1 extrapolation RMSE `8.33e-05`, while the degree-3 extrapolation RMSE was `0.854`.

Auditor session `513a74d3-ab59-41f9-8550-6fcf9d0d6b1f` validated the cycle with no critical or moderate defects. The audit confirmed symmetric adjacency matrices, exact row sum `4`, top eigenvalue `4`, tree moments `{2: 4, 4: 28, 6: 232, 8: 2092}`, complete CSV outputs, readable figures, and validator warnings only from legacy or future-milestone issues.

### Cycle 11: M3 Computational-Probe Synthesis and Closure

Cycle 11 was directed by researcher session `d99438fe-a5d8-4be7-947d-3c284114f35e`. The brief concluded that another same-axis probe was no longer the best use of M3. Instead, the work should synthesize five validated slices:

1. Common fixed-point random-permutation baseline.
2. Folded trajectory quotient profiles.
3. Direct labelled-graph embedding counts.
4. Polynomial-window diagnostics.
5. Schreier operator spectra.

Worker session `de1dfecd-b5e8-4e45-90fe-d659502577a7` produced:

- `reports/computational_probes/m3_computational_probe_synthesis.md`
- `data/polynomial_method/m3_probe_artifact_index.csv`
- `reports/figures/m3_probe_ladder_summary.png`
- `scripts/plot_m3_probe_ladder_summary.py`

It also archived an unused failed D2 source as `reports/figures/stale/m3_probe_ladder_summary.d2`, because the local D2 rendering backend was unavailable. The canonical figure source became the matplotlib script.

![Five-stage computational ladder from random-permutation fixed points to Schreier operator spectra, showing the observable varied, the stable signal found, and the main limitation at each stage.](reports/figures/m3_probe_ladder_summary.png)

The synthesis made the M3 claim precise. M3 validates a finite benchmark suite and mechanism analogue, not the hyperbolic theorem. Its core narrative is:

- Cyclic or rank-one contributions remain order one in raw fixed-point and quotient observables.
- Rank-two or noncyclic constraints are suppressed before normalization.
- Direct labelled-template embeddings explain much of the raw separation through constraint dimension.
- Low-degree polynomial-window fits can be stable for low-noise normalized embedding observables.
- High-degree fits expose derivative and coefficient amplification.
- Schreier spectral windows provide an operator-level toy bridge, but spectral polynomial-window fitting needs more sample sizes or lower-degree models.

The artifact index contained `42` rows covering cycles 6-11, with no missing artifact paths. It indexed scripts, tests, data files, figures, and reports for the M3 benchmark suite.

Auditor session `8af277cc-befb-436c-9f81-3814f09082c1` validated the closure. The audit verified all new artifacts, confirmed all `13` indexed M3 PNG figures were readable, checked that `scripts/plot_m3_probe_ladder_summary.py` compiles and regenerates the figure, and confirmed that the latest `M3-computational-probes` ledger event was `validated/high`. The only minor issue was visual crowding in the ladder figure labels.

### Cycle 12: Labelled-Embedding Expectation Certification

Cycle 12 was directed by researcher session `1f5735b4-11fb-4d22-a591-3f5495c2b125`. The brief chose the first M4 target: certify the finite labelled-template expectation identity underlying the M3 direct embedding benchmark. This target was selected because Cycle 8 had exposed and repaired a subtle inverse-label semantics bug, and M3’s strongest reusable benchmark depends on the corrected labelled-template estimator.

Worker session `b28602d5-c638-4b06-bee3-e91d7202407c` produced:

- `scripts/certify_labelled_embedding_expectation.wls`
- `scripts/certify_labelled_embedding_expectation.py`
- `tests/test_labelled_embedding_expectation_identity.py`
- `data/formal_certification/labelled_embedding_expectation_symbolic.csv`
- `data/formal_certification/labelled_embedding_expectation_exhaustive.csv`
- `reports/formal_certification/labelled_embedding_expectation_identity.md`

The certified lemma is:

\[
\mathbf{E}\,\mathrm{InjEmb}_n(H)
=
(n)_{|V|}
\prod_a \frac{1}{(n)_{|C_a(H)|}},
\]

provided each normalized constraint set $C_a(H)$ is a partial injection and $n \ge |V|$. If a constraint set is not a partial injection, or if $n<|V|$, the expectation is zero. Inverse-labelled edges are normalized by reversing edge orientation before forming forward constraints.

The Wolfram symbolic checks included no-edge, single-edge, same-label path, conflicting domain, conflicting image, inverse edge, the Cycle 8 inverse-label regression pair, and both M3 eight-word templates. Selected symbolic rows were:

| Template | Formula |
|---|---:|
| `single_edge` | `n - 1` |
| `same_label_path` | `n - 2` |
| `conflicting_domain` | `0` |
| `conflicting_image` | `0` |
| `inverse_regression_pair` | `1` |
| `eight_word_cyclic_toy` | `1` |
| `eight_word_rank2_toy` | `(n-6)(n-5)(n-4)/(n(n-1)(n-2)(n-3))` |

The Python exhaustive checker enumerated permutation tuples over small symmetric groups for `n=2,3,4`, wrote `27` exhaustive rows, and matched the formula in every feasible case.

Auditor session `f4d815d9-41ad-49be-bd8a-3d842677ccc1` validated the M4 slice with no critical or moderate defects. The audit reran the Wolfram script, Python compilation, exhaustive checker, direct tests, `promise_check`, and `org_check`. It confirmed that inverse-labelled edges are handled by reversing orientation, conflicts return zero, and brute-force enumeration agrees with the symbolic formula. The M4 ledger event `c39dbad7-b7e8-4c80-a7b1-7028f07658f6` was judged defensible as `validated/high`.

## Findings

### Finding 1: Schreier Spectral Windows Are Stable Toy Operator Observables

Cycle 10 showed that coarse normalized adjacency-window counts stabilize across `n=100,200,400,800` in the random 4-regular Schreier multigraph model. The strongest future spectral observables are `window_pos_mid` and `window_pos_edge`, because they are operator-level quantities and remain less noisy than high trace moments.

This does not transfer directly to Kim--Tao’s hyperbolic Laplacian. It establishes that, within the finite random-permutation toy model, a spectral observable can concentrate enough to be useful for benchmark design.

### Finding 2: Centered Trace Moments Separate Tree-Like Backtracking but Are Noisy

Cycle 10 also showed that centered trace moments decrease with `n` after subtracting infinite 4-regular tree moments. This supports the intended trace-formula analogy: deterministic tree-like or backtracking contributions should be separated before studying finite-cover fluctuations.

The limitation is that high moments amplify noise. The synthesis therefore recommends centered trace moments as trace-formula analogues, not as the primary predictive benchmark.

### Finding 3: Degree-3 Polynomial Fits Do Not Automatically Transfer to Spectral Data

Cycle 9 had identified degree-3 Chebyshev-window fits as a clean benchmark for low-noise normalized labelled-embedding counts. Cycle 10 tested whether that benchmark transfers to Schreier spectral observables. On the four-size grid `n=100,200,400,800`, it did not.

The conclusion is a negative boundary, not a failure. Degree-1 fits were stable for smooth spectral windows, while degree 3 and higher became stress tests. Future spectral interpolation work needs either more `n` values, stronger analytic structure, or lower-degree fits.

### Finding 4: M3 Is Now Validated as a Reproducible Benchmark Suite

Cycle 11 closed `M3-computational-probes` as `validated/high`. The milestone now contains a complete computational ladder from finite random-permutation fixed points to Schreier operator spectra.

The closure scope matters. M3 validates scripts, datasets, figures, and finite toy mechanisms. It does not validate the Selberg trace formula, the Kim--Tao rigidity theorem, the MPvH expansion, Nau boundedness, or MP23 rank-two estimates.

### Finding 5: The M4 Labelled-Embedding Identity Certifies a Core M3 Mechanism

Cycle 12 turned the labelled-embedding estimator into a self-contained finite lemma. The certified formula explains why the M3 cyclic eight-template remains order one while the rank-two eight-template carries a different constraint dimension. It also formalizes the inverse-label normalization repaired in Cycle 8.

The certification is narrow and useful. It confirms an exact finite expectation mechanism in independent uniform permutations. It does not certify the full random-cover trace expansion or any hyperbolic spectral conclusion.

## Discussion

Cycles 10-12 changed the campaign status in two ways.

First, M3 moved from an active set of probes to a closed benchmark suite. The computational evidence now has a stable internal structure: cyclic/rank-one observables are order one, rank-two/noncyclic observables are suppressed before normalization, and normalized labelled-template embeddings provide the cleanest low-noise data for polynomial-window diagnostics. The Schreier spectral probe adds an operator layer, but also shows where interpolation becomes fragile.

Second, M4 began with a certification that directly supports the M3 benchmark. This was the right first formal slice because it is small, exact, and tied to a real bug found earlier in the campaign. The finite identity now provides a reliable base for future extension work involving labelled-template counts.

The main research pressure point remains the Markov/interpolation loss. Earlier proof-ledger work identified it as a quantitative bottleneck in the Kim--Tao architecture. M3 made it concrete in finite data: low-degree normalized fits can behave well, while high-degree fits amplify derivatives and coefficients quickly. Cycle 10 showed that this behavior depends on the observable and grid size. Cycle 12 certified the finite expectation formula behind the cleanest benchmark. The next useful step is therefore not another broad empirical run, but a ranked M5 extension analysis focused on which parts of the interpolation loss are structural and which may be technical.

## Open Questions

1. Can the Markov/interpolation loss be separated into structural and technical components using the M2 loss ledger plus the M3/M4 benchmark suite?

2. Is there a tractable conjecture for normalized labelled-template observables that predicts when low-degree reciprocal or Chebyshev-window fits remain stable?

3. Would an additional M4 certification of the 4-regular tree closed-walk recurrence materially improve the M5 extension analysis, or is the labelled-template identity sufficient for now?

4. Can Schreier spectral-window observables be tested on a larger `n` grid without losing auditability, so degree-2 or degree-3 spectral interpolation can be evaluated fairly?

5. Which M5 extension candidate is strongest: sharpening the Markov exponent, replacing the interpolation step, deriving a multiplicity/delocalization consequence, or formulating a finite random-cover benchmark theorem?

## References

No `REFERENCES.md` file was present in the workspace. The report therefore cites local sources and session records used for this cycle range:

- Local paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 10 sessions: researcher `7fe5106f-b4b2-48b2-a9e0-bef0631ff27a`, worker `566c2736-3f4c-409a-b14c-060d0bcdd337`, auditor `513a74d3-ab59-41f9-8550-6fcf9d0d6b1f`.
- Cycle 11 sessions: researcher `d99438fe-a5d8-4be7-947d-3c284114f35e`, worker `de1dfecd-b5e8-4e45-90fe-d659502577a7`, auditor `8af277cc-befb-436c-9f81-3814f09082c1`.
- Cycle 12 sessions: researcher `1f5735b4-11fb-4d22-a591-3f5495c2b125`, worker `b28602d5-c638-4b06-bee3-e91d7202407c`, auditor `f4d815d9-41ad-49be-bd8a-3d842677ccc1`.
- Cycle artifacts:
  - `reports/computational_probes/m3_schreier_spectral_toy.md`
  - `reports/computational_probes/m3_computational_probe_synthesis.md`
  - `reports/formal_certification/labelled_embedding_expectation_identity.md`
  - `data/polynomial_method/schreier_spectral_toy_summary.csv`
  - `data/polynomial_method/schreier_spectral_window_fits.csv`
  - `data/polynomial_method/m3_probe_artifact_index.csv`
  - `data/formal_certification/labelled_embedding_expectation_symbolic.csv`
  - `data/formal_certification/labelled_embedding_expectation_exhaustive.csv`

## Appendix: Implementation Details

### Code Organization

Cycle 10 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/probe_schreier_spectral_toy.py` | 367 | Builds Schreier adjacency operators and computes spectral windows, trace moments, and polynomial-window fits. |
| `tests/test_schreier_spectral_toy.py` | 59 | Tests graph construction, row sums, trace/eigenvalue identities, tree moments, and reproducibility. |

Cycle 11 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/plot_m3_probe_ladder_summary.py` | 112 | Regenerates the M3 ladder summary figure. |
| `data/polynomial_method/m3_probe_artifact_index.csv` | 43 | Indexes the canonical M3 artifacts from cycles 6-11. |

Cycle 12 added:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/certify_labelled_embedding_expectation.py` | 240 | Exhaustively validates the labelled-template expectation formula over small symmetric groups. |
| `scripts/certify_labelled_embedding_expectation.wls` | 92 | Performs symbolic special-case checks in Wolfram. |
| `tests/test_labelled_embedding_expectation_identity.py` | 79 | Tests conflicts, inverse labels, brute-force agreement, and Cycle 8 regression behavior. |

### Data and Figure Outputs

Cycle 10 data:

| File | Lines |
|---|---:|
| `data/polynomial_method/schreier_spectral_toy_trials.csv` | 2161 |
| `data/polynomial_method/schreier_spectral_toy_summary.csv` | 73 |
| `data/polynomial_method/schreier_spectral_window_fits.csv` | 21 |

Cycle 12 data:

| File | Lines |
|---|---:|
| `data/formal_certification/labelled_embedding_expectation_symbolic.csv` | 10 |
| `data/formal_certification/labelled_embedding_expectation_exhaustive.csv` | 28 |

Figure dimensions checked during reporting:

| Figure | Dimensions |
|---|---:|
| `reports/figures/m3_schreier_spectral_eigenvalue_histograms.png` | 1440 x 864 |
| `reports/figures/m3_schreier_spectral_trace_scaling.png` | 1760 x 768 |
| `reports/figures/m3_schreier_spectral_window_fit.png` | 1760 x 768 |
| `reports/figures/m3_probe_ladder_summary.png` | 2520 x 864 |

### Validation Results

Cycle audits reported:

- Cycle 10: `VALIDATED`, no critical or moderate defects.
- Cycle 11: `VALIDATED`, no critical or moderate defects.
- Cycle 12: `VALIDATED`, no critical or moderate defects.

Reporter-side post-manifest checks:

```text
python3 -m long_exposure.tools.promise_check .
events: 29, plan milestones: 6
warnings only: legacy noncanonical docs path, pending M5/M6, and orphan prior cycle reports
```

```text
python3 -m long_exposure.tools.org_check .
exit 0 with warnings only: root preload/runtime files and historical figures under docs/
```

`MANIFEST.md` was replaced with a current snapshot and now has `85` lines. No `## Key Files` section existed, so no preserved final-reporter section was modified.

### Cumulative Snapshot After Cycle 12

| Metric | Value |
|---|---:|
| Campaign scripts | 9 |
| Campaign script lines | 2,315 |
| Campaign test files | 6 |
| Campaign test lines | 413 |
| CSV datasets under `data/` | 17 |
| PNG figures under `reports/` | 15 |
| Promise ledger events | 29 |

Current milestone state:

| Milestone | Status |
|---|---|
| `M1-paper-map` | validated |
| `M2-proof-ledger` | validated narrowly for proof reconstruction and loss accounting |
| `M3-computational-probes` | validated as a finite benchmark suite |
| `M4-formal-certification` | validated for first narrow slice |
| `M5-extension-candidates` | pending |
| `M6-final-synthesis` | pending |

### Session Cross-Reference Map

| Cycle | Researcher | Worker | Auditor | Main outcome |
|---:|---|---|---|---|
| 10 | `7fe5106f-b4b2-48b2-a9e0-bef0631ff27a` | `566c2736-3f4c-409a-b14c-060d0bcdd337` | `513a74d3-ab59-41f9-8550-6fcf9d0d6b1f` | Built and validated Schreier spectral toy probe. |
| 11 | `d99438fe-a5d8-4be7-947d-3c284114f35e` | `de1dfecd-b5e8-4e45-90fe-d659502577a7` | `8af277cc-befb-436c-9f81-3814f09082c1` | Synthesized and closed M3 as `validated/high`. |
| 12 | `1f5735b4-11fb-4d22-a591-3f5495c2b125` | `b28602d5-c638-4b06-bee3-e91d7202407c` | `f4d815d9-41ad-49be-bd8a-3d842677ccc1` | Certified labelled-template expectation identity and validated first M4 slice. |
