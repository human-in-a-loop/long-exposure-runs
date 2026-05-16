---
title: "Random Hyperbolic Surface Spectral Rigidity — cycles 13-15"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Random Hyperbolic Surface Spectral Rigidity — cycles 13-15

## Abstract

Cycles 13-15 opened and validated the `M5-extension-candidates` milestone. The campaign moved from reconstructing and probing Kim--Tao's random-cover rigidity argument toward a concrete extension program centered on the Markov/interpolation bottleneck identified earlier in the proof ledger.

The three-cycle arc was:

1. Cycle 13 ranked extension candidates and selected a primary path: isolate when Markov-type derivative amplification is a true structural obstacle and when it reflects unstable reconstruction from sparse reciprocal-`n` data.
2. Cycle 14 tested the primary path on fixed labelled templates using the M4 falling-factorial expectation identity. It showed that normalized fixed-template expectations have explicit Taylor expansions at `x=1/n` and are analytically stable near `x=0`.
3. Cycle 15 varied template size. It showed that growing count profiles can produce large coefficient and derivative growth because falling-factorial zero/pole scales move toward `x=0` like `1/L`.

The result is not an improvement to the Kim--Tao rigidity exponent. It is a validated toy benchmark principle: fixed conflict-free labelled-template expectations are stable after normalization, while Kim--Tao-like derivative amplification first reappears when the size, support, or constraint profile grows.

## Introduction

The long-exposure campaign studies Kim and Tao's paper `2603.01127`, "Eigenvalue rigidity of hyperbolic surfaces in the random cover model." Earlier cycles established the proof architecture, reconstructed the main rigidity and delocalization arguments, built computational probes, and certified a finite labelled-template expectation identity.

Cycles 13-15 focused on the fifth milestone, `M5-extension-candidates`: finding a credible research direction that builds on the validated internal evidence without claiming more than the artifacts support.

The central technical object in these cycles is a normalized labelled-template expectation. For a conflict-free labelled template with vertex count `V` and per-generator constraint counts `C_a`, the M4 identity gives

```text
E_H(n) = (n)_V / Product_a (n)_{C_a}.
```

Here `(n)_k` is the falling factorial. The normalized observable is

```text
N_H(n) = n^{C-V} E_H(n),   C = sum_a C_a.
```

After substituting `x=1/n`, the observable becomes a finite product or ratio of factors `(1 - jx)`. This makes fixed-template Taylor expansions explicit. Cycles 14-15 used this identity as a controlled model for the interpolation losses previously identified in the Kim--Tao proof ledger.

## Approach

The cycles used a staged progression.

Cycle 13 was analytical. It inventoried validated evidence from M2, M3, and M4, ranked seven possible extension directions, and selected one primary target. The output was a ranked candidate matrix, a CSV score table, and a primary candidate statement.

Cycle 14 was symbolic and comparative. It expanded fixed-template normalized expectations through order `x^4`, compared them with Cycle 9 polynomial-window fits, and tested whether high-degree fit instability came from the exact expectation or from sparse-grid interpolation.

Cycle 15 was symbolic and computational. It varied the profile size parameter `L`, expanded growing count-profile families through order `x^8`, and measured coefficient growth, derivative growth, and nearest falling-factorial singularity scales.

All three cycles preserved conservative scope. The work is about finite permutation and labelled-template mechanisms that model one bottleneck in the Kim--Tao proof architecture. It does not certify Selberg trace formula inputs, MPvH/Nau/MP23 estimates, or a new rigidity theorem.

## Source Inventory and Timeline

| Cycle | Source sessions | Main artifacts | Decision |
|---|---|---|---|
| 13 | Researcher `d1abcc72-61a9-4c04-87c4-9d033a1fdba4`; worker `97208720-81aa-472a-9a23-6c75eb3a4ab5`; auditor `9b4dadc9-3ce9-4d3b-9dff-6b5ad699c58c` | `m5_extension_candidate_ranking.md`, `m5_primary_candidate_statement.md`, `m5_candidate_scores.csv`, `m5_extension_candidate_matrix.png` | Validated M5 candidate ranking and selected Markov/interpolation-loss sharpening as primary. |
| 14 | Researcher `a24e3475-402a-40e6-842f-a64f72049074`; worker `17268f9e-adbc-44ae-90f5-0dce6fd335dd`; auditor `30702dc0-9920-45f8-8f36-b8e9d6c310c6` | `derive_labelled_embedding_expansions.wls`, `compare_expansions_to_cycle9.py`, expansion CSVs, `m5_expansion_vs_cycle9_fits.png`, `m5_falling_factorial_expansion_test.md` | Validated fixed-template expansion benchmark. |
| 15 | Researcher `bcd1ac47-e279-449f-a77d-dff1d48cdbd5`; worker `66c94dcb-f429-4d34-84f4-d9ef7d8e2f33`; auditor `bb04c33d-3042-4fad-a335-eaee10bdea9f` | `probe_growing_template_expansions.wls`, `plot_growing_template_expansions.py`, growing-template CSVs, three figures, `m5_growing_template_expansion_growth.md` | Validated growing-template amplification benchmark. |

No `REFERENCES.md` file was present in the workspace. The references section therefore lists local source artifacts and session IDs instead of global numbered citations.

## Findings

### Finding 1: The Best M5 Path Is the Markov/Interpolation Bottleneck

Cycle 13 ranked seven extension candidates:

| Rank | Candidate | Decision |
|---:|---|---|
| 1 | Markov/interpolation-loss sharpening | advance-primary |
| 2 | Exact labelled-template polynomial expansion | advance-technical-lemma |
| 3 | Delocalization-side improvement | advance-secondary |
| 4 | Schreier spectral-window benchmark | advance-benchmark |
| 5 | Tree closed-walk moment certification | defer-supporting |
| 6 | Direct Weil-Petersson transfer | reject-defer |
| 7 | Full Selberg trace formalization | reject-defer |

![Ranked M5 candidate matrix comparing value, tractability, evidence strength, dependency risk, and next-test clarity.](reports/figures/m5_extension_candidate_matrix.png)

The decision came from three prior validated facts:

- M2 identified Markov-type amplification in both the trace-side and delocalization-side arguments.
- M3 showed low-degree labelled-template observables were stable while high-degree sparse-grid fits were ill-conditioned.
- M4 certified the exact finite falling-factorial identity underlying one labelled-template class.

The primary candidate was stated conservatively: fixed conflict-free labelled templates should have stable low-degree expansions in `x=1/n`; high-degree sparse-grid instability should not be treated as evidence that the exact expectation is unstable until checked against exact expansions.

### Finding 2: Fixed-Template Expectations Are Analytically Stable

Cycle 14 derived exact normalized expansions through `x^4`.

| Template | Expansion |
|---|---|
| `single_label_cycle` | `1` |
| `eight_word_cyclic_toy` | `1` |
| `trace_pair_toy` | `1 - x - x^2 - x^3 - x^4 + O(x^5)` |
| `eight_word_rank2_toy` | `1 - 9x + 9x^2 + 39x^3 + 81x^4 + O(x^5)` |
| `no_edge_control` | `1 - x` |
| `single_edge_control` | `1 - x` |
| `conflicting_domain` | `0` |

For the key rank-two benchmark,

```text
N_H(n) = n (n)_7 / (n)_4^2
       = ((n - 6)(n - 5)(n - 4)) / ((n - 1)(n - 2)(n - 3)).
```

The Cycle 14 audit confirmed that the Wolfram symbolic path and Python comparison path agreed. It also confirmed that the conflict template vanished exactly and that the recovered `trace_pair_toy` had coefficients `[1, -1, -1, -1, -1]`.

![Exact falling-factorial expansions versus Cycle 9 polynomial-window fits for cyclic and rank-two eight-word templates.](reports/figures/m5_expansion_vs_cycle9_fits.png)

The comparison supported the mechanism split. For `eight_word_rank2_toy`, the exact order-4 Taylor extrapolation RMSE was `2.45e-10`, while the Cycle 9 degree-3 extrapolation RMSE was `8.90e-4`; degree 6 and degree 8 fits were much less stable. The exact fixed-template expectation is therefore not the source of the high-degree blowup observed in sparse-grid fitting.

### Finding 3: Growing Template Size Reintroduces Derivative Amplification

Cycle 15 changed the axis from fixed templates to growing count profiles. The same M4 identity was used, but `V` and the constraint counts `C_a` grew with a size parameter `L`.

Two hand-checkable families behaved benignly:

```text
single_label_cycle_profile: N_L(1/x) = 1

single_label_path_profile:  N_L(1/x) = 1 - Lx
```

Nontrivial rank-two and rank-four profiles showed large coefficient and derivative growth by `L=40`.

| Family | L | L1 coefficient norm through order 8 | Max derivative through order 8 | Radius proxy |
|---|---:|---:|---:|---:|
| `single_label_cycle_profile` | 40 | 1 | 1 | exact cancellation |
| `single_label_path_profile` | 40 | 41 | 40 | `1/40` |
| `rank2_balanced_profile` | 40 | `1.222740960544758e20` | `4.887997076237615e24` | `1/78` |
| `rank2_deficit_k3` | 40 | `3.9254589694304007e19` | `1.5663067375849087e24` | `1/76` |
| `rank4_delocalization_toy_s4` | 40 | `6.802812940161747e26` | `2.7401689056357774e31` | `1/155` |

![Coefficient norms through order 8 versus template size L for controlled labelled-template profiles.](reports/figures/m5_growing_template_coefficient_growth.png)

![Derivatives at x=0 by expansion order for growing labelled-template profiles.](reports/figures/m5_growing_template_derivative_growth.png)

The mechanism was localized to the falling-factorial product structure. As `L` grows, the nearest zero or pole scale approaches `x=0`, roughly like `1/L`.

![Nearest falling-factorial zero/pole scale versus L.](reports/figures/m5_growing_template_radius_proxy.png)

The Cycle 15 audit validated the result and corrected one stale worker note: although the worker reported a local Wolfram license failure, the auditor successfully ran `wolfram-batch -script scripts/probe_growing_template_expansions.wls` and regenerated the CSVs.

### Finding 4: M5 Is Validated as a Benchmark Principle, Not as a Theorem Improvement

The cumulative M5 result has three validated layers:

1. Candidate ranking identified Markov/interpolation loss as the most tractable extension path.
2. Fixed-template expansions showed normalized conflict-free expectations are analytically tame near `x=0`.
3. Growing-template profiles showed coefficient and derivative amplification appears naturally when profile size grows.

This supports a precise research narrative: the finite-template mechanism is stable for fixed templates, but Kim--Tao-like interpolation difficulty reappears when the relevant polynomial family grows in size, support, or degree.

The report does not claim that the Kim--Tao rigidity exponent can be improved. It also does not replace imported MPvH, Nau, or MP23 inputs. Its contribution is a reproducible benchmark that separates fixed-template stability from growing-family derivative amplification.

## Discussion

Cycles 13-15 converted the campaign from broad extension search to a narrow, testable mechanism.

The useful distinction is between two sources of instability:

- **Sparse-grid reconstruction instability:** high-degree fits from few reciprocal-`n` samples can have large coefficient and derivative norms even when the underlying fixed-template expectation is stable.
- **Growing-family analytic instability:** when template size grows, the falling-factorial factors introduce zeros and poles closer to `x=0`, and derivatives can grow rapidly.

This distinction matters because Kim--Tao's proof does not control one fixed finite template. It controls trace/pre-trace polynomial families whose degree, support, or combinatorial size grows. The M5 benchmark therefore does not solve the paper's bottleneck, but it identifies where a finite exact model first begins to resemble that bottleneck.

The most defensible next step is not more random sampling. It is a compact M5 synthesis or a transition to `M6-final-synthesis`, preserving the benchmark principle and its limitations.

## Open Questions

1. Can the growing-template coefficient growth be bounded in a clean asymptotic form in `L` and expansion order `r`?
2. Which growing profiles best model the actual trace-side and fourth-moment polynomial families used in Kim--Tao?
3. Can the fixed-template expansion lemma be stated and certified in a more formal system, or is the current Wolfram/Python validation sufficient for its role?
4. Does the benchmark help isolate a technical improvement path inside the imported MPvH/Nau/MP23 machinery, or does it only explain why the existing Markov loss is structurally expected?
5. Should the next cycle close M5 with a synthesis, or begin `M6-final-synthesis` with the benchmark as the campaign's main extension result?

## References

No `REFERENCES.md` file was present. The report uses the following local sources and session records.

- Kim--Tao local paper files: `2603.01127.pdf`, `2603.01127.txt`.
- Cycle 13 sessions: `d1abcc72-61a9-4c04-87c4-9d033a1fdba4`, `97208720-81aa-472a-9a23-6c75eb3a4ab5`, `9b4dadc9-3ce9-4d3b-9dff-6b5ad699c58c`.
- Cycle 14 sessions: `a24e3475-402a-40e6-842f-a64f72049074`, `17268f9e-adbc-44ae-90f5-0dce6fd335dd`, `30702dc0-9920-45f8-8f36-b8e9d6c310c6`.
- Cycle 15 sessions: `bcd1ac47-e279-449f-a77d-dff1d48cdbd5`, `66c94dcb-f429-4d34-84f4-d9ef7d8e2f33`, `bb04c33d-3042-4fad-a335-eaee10bdea9f`.
- M5 reports: `reports/extension_candidates/m5_extension_candidate_ranking.md`, `reports/extension_candidates/m5_primary_candidate_statement.md`, `reports/extension_candidates/m5_falling_factorial_expansion_test.md`, `reports/extension_candidates/m5_growing_template_expansion_growth.md`.
- M5 data: `data/extension_candidates/m5_candidate_scores.csv`, `data/extension_candidates/labelled_embedding_expansion_coefficients.csv`, `data/extension_candidates/labelled_embedding_expansion_fit_comparison.csv`, `data/extension_candidates/growing_template_expansion_coefficients.csv`, `data/extension_candidates/growing_template_expansion_summary.csv`.

## Appendix: Implementation Details

### Code Organization

New Cycle 13-15 scripts:

| File | Lines | Purpose |
|---|---:|---|
| `scripts/score_m5_extension_candidates.py` | 183 | Regenerates the M5 candidate score CSV and candidate matrix figure. |
| `scripts/derive_labelled_embedding_expansions.wls` | 75 | Exports fixed-template falling-factorial expansions through `x^4`. |
| `scripts/compare_expansions_to_cycle9.py` | 296 | Compares exact expansions against Cycle 9 polynomial-window fits. |
| `scripts/probe_growing_template_expansions.wls` | 154 | Exports growing-template coefficient expansions through `x^8`. |
| `scripts/plot_growing_template_expansions.py` | 371 | Regenerates growing-template CSVs and figures. |

New Cycle 13-15 tests:

| File | Lines | Purpose |
|---|---:|---|
| `tests/test_labelled_embedding_expansions.py` | 83 | Tests fixed-template coefficients, conflict controls, truncation behavior, and missing-fit skip handling. |
| `tests/test_growing_template_expansions.py` | 80 | Tests growing-template hand formulas, truncation agreement, deterministic extraction, and radius monotonicity. |

### Data and Figures

Cycle 13 produced `data/extension_candidates/m5_candidate_scores.csv` with seven ranked candidates and `reports/figures/m5_extension_candidate_matrix.png` at `1890 x 1007`.

Cycle 14 produced `data/extension_candidates/labelled_embedding_expansion_coefficients.csv` with seven template rows, `data/extension_candidates/labelled_embedding_expansion_fit_comparison.csv` with 581 lines including header, and `reports/figures/m5_expansion_vs_cycle9_fits.png` at `2700 x 864`.

Cycle 15 produced `data/extension_candidates/growing_template_expansion_coefficients.csv` with 2494 lines including header, `data/extension_candidates/growing_template_expansion_summary.csv` with 278 lines including header, and three figures:
`m5_growing_template_coefficient_growth.png` at `1440 x 900`,
`m5_growing_template_derivative_growth.png` at `2160 x 900`,
and `m5_growing_template_radius_proxy.png` at `1440 x 900`.

### Validation Results

Cycle 13 validation passed:

- `python3 -m py_compile scripts/score_m5_extension_candidates.py`
- `python3 scripts/score_m5_extension_candidates.py`
- figure readability check for `m5_extension_candidate_matrix.png`
- `promise_check` and `org_check`, both exit 0 with known warnings only

Cycle 14 validation passed:

- `wolfram-batch -script scripts/derive_labelled_embedding_expansions.wls`
- `python3 -m py_compile scripts/compare_expansions_to_cycle9.py tests/test_labelled_embedding_expansions.py`
- `python3 scripts/compare_expansions_to_cycle9.py`
- `python3 tests/test_labelled_embedding_expansions.py`
- figure readability check for `m5_expansion_vs_cycle9_fits.png`
- `promise_check` and `org_check`, both exit 0 with known warnings only

Cycle 15 validation passed:

- `wolfram-batch -script scripts/probe_growing_template_expansions.wls`
- `python3 -m py_compile scripts/plot_growing_template_expansions.py tests/test_growing_template_expansions.py`
- `python3 scripts/plot_growing_template_expansions.py`
- `python3 tests/test_growing_template_expansions.py`
- figure readability checks for all three growing-template figures
- `promise_check` and `org_check`, both exit 0 with known warnings only

After this reporter pass, `MANIFEST.md` was updated to include the M5 artifacts. Follow-up validation reported `promise_check` exit 0 with 32 ledger events and known warnings only, and `org_check` exit 0 with known workspace-organization warnings only.

### Cumulative Snapshot

The updated manifest records:

| Metric | Value |
|---|---:|
| Campaign scripts | 14 |
| Campaign script lines | 3,394 |
| Campaign test files | 8 |
| Campaign test lines | 576 |
| Markdown/DOT/PNG documentation artifacts under `docs/` and `reports/` | 60 |
| PNG figures under `reports/figures/` | 20 |
| Canonical CSV datasets under `data/` | 22 |
| Promise ledger events | 32 |

Current milestone state:

- `M1-paper-map`: validated.
- `M2-proof-ledger`: validated narrowly for local proof reconstruction and quantitative dependency/loss accounting.
- `M3-computational-probes`: validated as a reproducible finite random-permutation and Schreier-operator benchmark suite.
- `M4-formal-certification`: validated for the labelled-template embedding expectation identity.
- `M5-extension-candidates`: validated through candidate ranking, fixed-template expansion testing, and growing-template expansion growth benchmark.
- `M6-final-synthesis`: pending.

### Cross-Reference Map

| Origin | Consuming artifact | Role |
|---|---|---|
| `docs/proof_ledger/m2_loss_map.md` | `m5_extension_candidate_ranking.md` | Identifies Markov/interpolation loss as the primary extension target. |
| `reports/computational_probes/m3_polynomial_window_diagnostics.md` | `m5_primary_candidate_statement.md` | Supplies low-degree stability and high-degree instability evidence. |
| `reports/formal_certification/labelled_embedding_expectation_identity.md` | `m5_falling_factorial_expansion_test.md` | Supplies the exact M4 falling-factorial identity. |
| `derive_labelled_embedding_expansions.wls` | `labelled_embedding_expansion_coefficients.csv` | Exports fixed-template coefficients. |
| `compare_expansions_to_cycle9.py` | `m5_expansion_vs_cycle9_fits.png` | Compares exact expansions with Cycle 9 fits. |
| `m5_falling_factorial_expansion_test.md` | `probe_growing_template_expansions.wls` | Motivates varying template size after fixed-template stability is established. |
| `probe_growing_template_expansions.wls` | `growing_template_expansion_coefficients.csv` | Exports growing-profile expansion data. |
| `plot_growing_template_expansions.py` | growing-template figures | Renders coefficient, derivative, and radius-proxy evidence. |
