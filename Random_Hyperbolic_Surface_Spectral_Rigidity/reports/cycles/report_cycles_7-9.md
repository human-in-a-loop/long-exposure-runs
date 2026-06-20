---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 7-9"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 7-9

## Abstract

Cycles 7-9 continued `M3-computational-probes`, the computational milestone for the long-exposure study of Kim and Tao's paper *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*. Earlier cycles had already validated the proof map and proof ledger, including the role of polynomial-method common-fixed-point estimates and the diagonal subtraction term in the eigenfunction delocalization proof. These three cycles turned that proof-ledger understanding into a more structured computational ladder.

Cycle 7 added folded trajectory quotient profiles to the Cycle 6 random-permutation fixed-point probe. This separated cyclic/rank-one word families from rank-two/noncyclic controls structurally, but it also confirmed that fixed-basepoint Monte Carlo remains too sparse for rank-two eight-word families.

Cycle 8 changed the observable from fixed-basepoint intersections to direct injective labelled-graph embedding counts. This solved the sparsity problem at the toy level: the cyclic eight-edge template remained order one, while the rank-two eight-edge template had stable nonzero estimates at the expected `n^{-1}` scale. The auditor fixed one inverse-label estimator bug; the published lowercase-template numerical conclusions were unchanged.

Cycle 9 used the Cycle 8 benchmark pair for polynomial-window diagnostics in `x = 1/n`. Degree-3 Chebyshev-window fits extrapolated accurately toward `x = 0`, while deliberately underdetermined degree-6 and degree-8 fits showed large derivative and coefficient growth. The auditor validated this as a toy Markov-amplification diagnostic, not as the actual MPvH/MP23 polynomial or a hyperbolic trace statistic.

## Introduction

The campaign's first two milestones established the local proof architecture of the paper. In that architecture, random-cover trace and pre-trace estimates are reduced to finite permutation statistics. The proof then controls polynomial expressions in reciprocal cover degree, with Markov-type derivative bounds producing visible exponent losses.

Cycles 7-9 focused on a narrow computational question: how much of that finite permutation mechanism can be reproduced in simple random-permutation toy models before adding hyperbolic length weights or actual random-cover spectra?

The answer from these cycles is a three-step computational ladder:

1. A folded trajectory quotient classifies word families by cyclic/rank-one versus rank-two/noncyclic structure.
2. Direct labelled-graph embedding counts give stable nonzero estimates for eight-word rank-two toy templates.
3. Polynomial fits to normalized embedding counts expose a reproducible interpolation-stability cost.

These are validated M3 slices, not closure of M3. The next recommended M3 target remains a Schreier/random-cover toy spectral probe using the Cycle 9 benchmark as a reference.

## Approach

Cycle 7 introduced a **folded trajectory quotient**. For a tuple of words, the script traces each reduced word from a common symbolic basepoint, identifies terminal points back to that basepoint, merges identical labelled edges, and records graph invariants. This is a simplified labelled trajectory quotient, not full Stallings folding and not the MPvH/MP23 quotient expansion.

Cycle 8 introduced a **labelled-graph embedding count**. For a small labelled directed graph `H`, the observable counts injective vertex maps into `[n]` such that every labelled edge constraint `sigma_label(f(u)) = f(v)` is satisfied by independent random permutations. This moves closer to quotient-graph embeddings than asking how many points are fixed by all words in a tuple.

Cycle 9 introduced a **polynomial-window diagnostic**. It reads the Cycle 8 normalized embedding counts as values of a function of `x = 1/n`, fits polynomial surrogates in a Chebyshev basis, and records hold-out error, extrapolation error near `x = 0`, derivative at zero, and coefficient norms.

## Source Inventory and Timeline

### Cycle 7: Folded Word-Graph Probe

Researcher session `980c616d-f011-4fba-a76f-a01ddad32997` set the task: preserve the Cycle 6 random-permutation harness but add quotient-graph structure so cyclic diagonal families and rank-two/noncyclic families could be distinguished before sampling.

Worker session `408bb527-400a-4300-844c-9fa8a3e0f2f7` produced:

- `scripts/probe_folded_word_graphs.py`
- `tests/test_folded_word_graphs.py`
- `data/polynomial_method/folded_word_graph_probe.csv`
- `data/polynomial_method/folded_word_graph_summary.csv`
- `reports/computational_probes/m3_folded_word_graph_probe.md`
- `reports/figures/m3_folded_graph_rank_scaling.png`
- `reports/figures/m3_folded_graph_profile_heatmap.png`

The final run wrote 52,000 raw rows across 13 families and `n = 50,100,200,400`.

![Common-fixed-point scaling grouped by folded word-graph rank/cyclicity.](reports/figures/m3_folded_graph_rank_scaling.png)

![Empirical frequency of folded trajectory profiles across cyclic, mixed, and rank-two word families.](reports/figures/m3_folded_graph_profile_heatmap.png)

Auditor session `5418764b-feb6-4e41-8583-2e5e0f906c83` validated the slice. The auditor found no critical or moderate issues, confirmed tests and figures, and kept `M3-computational-probes` as `in-progress`.

### Cycle 8: Labelled Graph Embedding Probe

Researcher session `ab5df6ec-9450-48c8-a747-1f6dc5e2f9d0` directed the next step: replace fixed-basepoint intersections with direct embeddings of small labelled quotient graphs.

Worker session `9d05ccd8-154c-446b-b477-28ccab54d6e9` produced:

- `scripts/probe_labelled_graph_embeddings.py`
- `tests/test_labelled_graph_embeddings.py`
- `data/polynomial_method/labelled_graph_embedding_probe.csv`
- `data/polynomial_method/labelled_graph_embedding_summary.csv`
- `reports/computational_probes/m3_labelled_graph_embedding_probe.md`
- `reports/figures/m3_labelled_embedding_scaling.png`
- `reports/figures/m3_labelled_embedding_normalized.png`

The final data contain 80 rows over eight templates and the `n` grid `3,4,8,20,50,100,200,400`.

![Estimated labelled-graph embedding counts versus n, grouped by quotient-template rank.](reports/figures/m3_labelled_embedding_scaling.png)

![Embedding counts normalized by the naive n^{|V|-|E|} constraint-count scale.](reports/figures/m3_labelled_embedding_normalized.png)

Auditor session `9474882f-ed40-4e43-806a-b21e8936e24c` found one moderate implementation defect: inverse-labelled edges were mishandled in the Monte Carlo expectation estimator. The auditor repaired the issue in `scripts/probe_labelled_graph_embeddings.py`, added a regression test, and appended ledger event `1b6b42a7-55c3-4d82-9c54-7cf3f7a698e2`. The final Cycle 8 templates used lowercase labels only, so the reported numerical results were unaffected.

### Cycle 9: Polynomial-Window Diagnostics

Researcher session `906e78cd-e243-41f7-ac07-c439cd89eb3f` directed a polynomial-window experiment using the validated Cycle 8 benchmark pair. The goal was to probe interpolation and Markov-type derivative amplification in a toy setting.

Worker session `0ef0e4ce-f292-4584-acd3-b25c7c6a678d` produced:

- `scripts/probe_polynomial_window_diagnostics.py`
- `tests/test_polynomial_window_diagnostics.py`
- `data/polynomial_method/polynomial_window_diagnostics.csv`
- `data/polynomial_method/polynomial_window_fit_summary.csv`
- `reports/computational_probes/m3_polynomial_window_diagnostics.md`
- `reports/figures/m3_polynomial_window_fit_error.png`
- `reports/figures/m3_polynomial_window_derivative_growth.png`
- `reports/figures/m3_polynomial_window_extrapolation.png`

The final run wrote 7,344 diagnostic rows and 18 fit-summary rows.

![Polynomial fit and hold-out errors for cyclic and rank-two labelled-embedding benchmark templates.](reports/figures/m3_polynomial_window_fit_error.png)

![Derivative and coefficient growth versus polynomial degree, illustrating the toy Markov-amplification mechanism.](reports/figures/m3_polynomial_window_derivative_growth.png)

![Extrapolation toward `x = 0` for normalized embedding-count observables.](reports/figures/m3_polynomial_window_extrapolation.png)

Auditor session `ea490aa2-d83a-4f19-994a-85aedb667f55` validated the slice. The audit confirmed that tests passed, smoke output was generated, all figures were readable at `1440 x 864` RGBA, and repository checks passed with known warnings only.

## Findings

### Finding 1: Folded quotient profiles explain the Cycle 6 null result

Cycle 6 showed that naive pointwise common fixed sets are too crude for multiword rank-two families: adding composite words can collapse to the same fixed-point constraint as a smaller pair.

Cycle 7 made this null result structural. The folded trajectory quotient classified `cyclic_pair_a_a2` and `cyclic_eight` as generator-rank-one cyclic families, and both had mean common fixed-point counts near one. Rank-two/noncyclic families were classified separately and had much smaller means.

Selected Cycle 7 means at `n = 400`:

| family | generator rank | cyclic flag | mean |
|---|---:|---:|---:|
| `cyclic_pair_a_a2` | 1 | 1 | 1.016 |
| `cyclic_eight` | 1 | 1 | 1.016 |
| `rank_two_pair_a_b` | 2 | 0 | 0.000 |
| `rank_two_pair_ab_ba` | 2 | 0 | 0.006 |
| `mixed_eight` | 2 | 0 | 0.000 |
| `rank_two_eight` | 2 | 0 | 0.000 |

The conclusion was not that fixed-basepoint Monte Carlo estimates the eight-word mechanism well. It was that quotient structure should be tracked explicitly before choosing an estimator.

### Finding 2: Direct labelled-graph embeddings solve the eight-word sparsity problem at toy level

Cycle 8 changed the observable. Instead of sampling basepoints fixed by all words, it estimated expected injective labelled-graph embeddings. This made rank-two eight-word templates measurable.

Selected Cycle 8 estimates at `n = 400`:

| template | count estimate | naive power | normalized count |
|---|---:|---:|---:|
| `eight_word_cyclic_toy` | 1.000000 | 0 | 1.000000 |
| `eight_word_rank2_toy` | 0.00244389 | -1 | 0.977557 |
| `figure_eight_ab` | 0.0025 | -1 | 1.000000 |
| `trace_pair_toy` | 0.00249373 | -1 | 0.997494 |

The rank-two eight-edge template no longer vanished under sampling. Its raw count scaled like `n^{-1}`, while normalization by the naive constraint scale `n^{|V|-|E|}` brought it close to one.

This supports the Cycle 8 interpretation: the main cyclic/rank-two separation in the toy embedding model is constraint dimension, not an extra anomalous constant after normalization.

### Finding 3: The Cycle 8 audit repaired inverse-label semantics

The Cycle 8 auditor found that uppercase inverse-labelled edges were supported in exact realized checks but mishandled in the Monte Carlo expectation estimator. The repair normalized uppercase labels as reversed partial-permutation constraints.

The published templates used lowercase labels, so the numerical conclusions remained aligned with the worker report. The repair matters for future work because later quotient graphs may naturally contain inverse-labelled edges.

### Finding 4: Degree-3 polynomial-window fits are the current benchmark

Cycle 9 fit normalized Cycle 8 embedding counts as functions of `x = 1/n`. The recommended benchmark is:

- templates: `eight_word_cyclic_toy` and `eight_word_rank2_toy`
- basis: Chebyshev-window fitting
- degree: 3
- use degree 6 and 8 only as instability stress tests

Selected Cycle 9 fit-summary values:

| template | degree | holdout RMSE | extrapolation RMSE | derivative at 0 | coefficient norm |
|---|---:|---:|---:|---:|---:|
| `single_label_cycle` | 1 | 2.22e-16 | 2.22e-16 | -3.30e-16 | 1 |
| `eight_word_cyclic_toy` | 3 | 4.76e-1 | 6.17e-4 | -1.87e-1 | 47.96 |
| `eight_word_rank2_toy` | 3 | 3.81e-1 | 8.90e-4 | -9.19 | 35.71 |
| `eight_word_cyclic_toy` | 8 | 8.23e-1 | 5.58e-1 | 2.06e2 | 1.02e8 |
| `eight_word_rank2_toy` | 8 | 2.76e2 | 1.98 | -6.29e2 | 7.24e8 |

The exact `single_label_cycle` control was recovered to machine precision at low degrees. Its high-degree failures were intentionally treated as conditioning stress tests, not as failures of the constant sequence.

### Finding 5: The toy Markov-amplification signal is concrete but limited

Cycle 9 gives a concrete analogue of the proof ledger's Markov-loss mechanism: as fit degree increases in an underdetermined window, derivative and coefficient diagnostics grow sharply.

The auditor accepted this conclusion with a clear limitation. The diagnostic measures interpolation conditioning for normalized expected labelled-embedding counts. It is not the actual MPvH/MP23 polynomial, and it is not a hyperbolic trace statistic.

## Discussion

Cycles 7-9 advanced M3 from a raw random-permutation baseline into a structured computational framework. Each cycle addressed a defect exposed by the previous one.

Cycle 7 explained why raw common fixed-point intersections were inadequate for rank-two eight-word families. Cycle 8 replaced that sparse observable with direct labelled-graph embeddings. Cycle 9 then used the stable Cycle 8 embedding data to test interpolation stability.

The resulting ladder is now useful for future work because it separates three issues that were previously entangled:

- **Structure:** cyclic/rank-one versus rank-two/noncyclic quotient type.
- **Scale:** raw embedding-count suppression governed by `n^{|V|-|E|}`.
- **Interpolation:** stability or instability of polynomial fits near `x = 0`.

The strongest next target, recorded by the Cycle 9 auditor, is a Schreier/random-cover toy spectral probe. That would move M3 closer to the paper's geometric setting while preserving the degree-3 cyclic/rank-two polynomial-window benchmark as a reference.

## Open Questions

1. How should the current labelled-graph templates be embedded into an actual Schreier/random-cover toy spectral model without losing the clean cyclic/rank-two benchmark?

2. Can the degree-3 polynomial-window benchmark be made less toy-like by adding hyperbolic length weights or trace-window weights while preserving exact controls?

3. Which part of the paper's Markov loss is best represented by the current derivative/coefficient diagnostics: trace-side `q^{2 kappa}`, pre-trace fourth-moment `q^{4 kappa}`, or only the general interpolation-conditioning phenomenon?

4. Can inverse-labelled quotient templates now be added safely after the Cycle 8 audit repair, and do they change the normalized embedding-count behavior?

5. At what point should M3 close? It now has four validated slices, but the audit guidance keeps M3 open for at least a Schreier/random-cover toy spectral probe.

## References

No `REFERENCES.md` file was present in the workspace during this reporter pass. As in the cycles 4-6 report, this section therefore lists local sources and session records rather than global numbered references.

- Kim and Tao, *Eigenvalue rigidity of hyperbolic surfaces in the random cover model*, local files `2603.01127.pdf` and `2603.01127.txt`.
- Cycle 7 researcher session `980c616d-f011-4fba-a76f-a01ddad32997`.
- Cycle 7 worker session `408bb527-400a-4300-844c-9fa8a3e0f2f7`.
- Cycle 7 auditor session `5418764b-feb6-4e41-8583-2e5e0f906c83`.
- Cycle 8 researcher session `ab5df6ec-9450-48c8-a747-1f6dc5e2f9d0`.
- Cycle 8 worker session `9d05ccd8-154c-446b-b477-28ccab54d6e9`.
- Cycle 8 auditor session `9474882f-ed40-4e43-806a-b21e8936e24c`.
- Cycle 9 researcher session `906e78cd-e243-41f7-ac07-c439cd89eb3f`.
- Cycle 9 worker session `0ef0e4ce-f292-4584-acd3-b25c7c6a678d`.
- Cycle 9 auditor session `ea490aa2-d83a-4f19-994a-85aedb667f55`.
- `reports/computational_probes/m3_folded_word_graph_probe.md`.
- `reports/computational_probes/m3_labelled_graph_embedding_probe.md`.
- `reports/computational_probes/m3_polynomial_window_diagnostics.md`.

## Appendix: Implementation Details

### Code Organization

Cycle 7 files:

- `scripts/probe_folded_word_graphs.py`: 398 lines.
- `tests/test_folded_word_graphs.py`: 59 lines.
- `reports/computational_probes/m3_folded_word_graph_probe.md`: 93 lines.
- `data/polynomial_method/folded_word_graph_probe.csv`: 52,001 lines including header.
- `data/polynomial_method/folded_word_graph_summary.csv`: 53 lines including header.

Cycle 8 files:

- `scripts/probe_labelled_graph_embeddings.py`: 444 lines.
- `tests/test_labelled_graph_embeddings.py`: 87 lines.
- `reports/computational_probes/m3_labelled_graph_embedding_probe.md`: 97 lines.
- `data/polynomial_method/labelled_graph_embedding_probe.csv`: 81 lines including header.
- `data/polynomial_method/labelled_graph_embedding_summary.csv`: 81 lines including header.

Cycle 9 files:

- `scripts/probe_polynomial_window_diagnostics.py`: 320 lines.
- `tests/test_polynomial_window_diagnostics.py`: 72 lines.
- `reports/computational_probes/m3_polynomial_window_diagnostics.md`: 91 lines.
- `data/polynomial_method/polynomial_window_diagnostics.csv`: 7,345 lines including header.
- `data/polynomial_method/polynomial_window_fit_summary.csv`: 19 lines including header.

### Validation Results

Cycle 7 validation, from session `5418764b-feb6-4e41-8583-2e5e0f906c83`:

- `py_compile`: passed.
- Direct tests: passed.
- Smoke run: passed.
- Final CSV: 52,000 rows, 13 families, four `n` values, 1,000 rows per `(n, family)`.
- Figures: readable, `1280 x 800` RGBA and `1600 x 800` RGBA.
- Decision: `VALIDATED`.

Cycle 8 validation, from session `9474882f-ed40-4e43-806a-b21e8936e24c`:

- `py_compile`: passed after audit repair.
- Direct tests: passed after audit repair.
- Smoke run: passed.
- Inverse-label regression: exact and estimator outputs agreed within roundoff.
- Final CSV: 80 rows, eight templates, modes `exact` and `monte_carlo`.
- Figures: readable, both `1440 x 880` RGBA.
- Decision: `VALIDATED`.

Cycle 9 validation, from session `ea490aa2-d83a-4f19-994a-85aedb667f55`:

- `py_compile`: passed.
- Direct tests: passed.
- Smoke run: passed, writing 252 diagnostic rows and 9 fit rows.
- Final CSVs: 7,344 diagnostic rows and 18 fit-summary rows.
- Figures: readable, all three `1440 x 864` RGBA.
- Decision: `VALIDATED`.

### Reporter-Side Checks

After updating `MANIFEST.md`, reporter-side checks were run:

- `python3 -m long_exposure.tools.promise_check .`: passed with warnings only. It reported 25 ledger events and known warnings for noncanonical `docs/paper_map/`, pending M4/M5/M6 milestones, and orphan prior periodic reports.
- `python3 -m long_exposure.tools.org_check .`: passed with warnings only. It reported known root-file warnings and historical `docs/` figure-location warnings.

### Manifest Update

`MANIFEST.md` was replaced as a current snapshot. No `## Key Files` section existed, so no final-reporter-owned section needed preservation.

Current manifest totals:

| Metric | Value |
|---|---:|
| Campaign scripts | 5 |
| Campaign script lines | 1,504 |
| Campaign test files | 4 |
| Campaign test lines | 275 |
| Markdown proof/map/report artifacts | 20 |
| PNG figures | 17 |
| Canonical CSV datasets | 9 |
| Promise ledger events | 25 |

### Session Cross-Reference Map

| Cycle | Role | Session ID | Role in report |
|---:|---|---|---|
| 7 | researcher | `980c616d-f011-4fba-a76f-a01ddad32997` | Defined folded word-graph/common-quotient task. |
| 7 | worker | `408bb527-400a-4300-844c-9fa8a3e0f2f7` | Built folded trajectory quotient probe and outputs. |
| 7 | auditor | `5418764b-feb6-4e41-8583-2e5e0f906c83` | Validated Cycle 7 slice. |
| 8 | researcher | `ab5df6ec-9450-48c8-a747-1f6dc5e2f9d0` | Defined direct labelled-graph embedding task. |
| 8 | worker | `9d05ccd8-154c-446b-b477-28ccab54d6e9` | Built embedding-count probe and outputs. |
| 8 | auditor | `9474882f-ed40-4e43-806a-b21e8936e24c` | Repaired inverse-label estimator and validated Cycle 8. |
| 9 | researcher | `906e78cd-e243-41f7-ac07-c439cd89eb3f` | Defined polynomial-window diagnostic task. |
| 9 | worker | `0ef0e4ce-f292-4584-acd3-b25c7c6a678d` | Built polynomial-window diagnostic suite and outputs. |
| 9 | auditor | `ea490aa2-d83a-4f19-994a-85aedb667f55` | Validated Cycle 9 slice. |
