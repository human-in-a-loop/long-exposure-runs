---
created: 2026-05-15T15:36:35Z
run_id: run-2026-05-15T153635Z
agent: researcher
---

# Plan of Record — # Long-Exposure Research Prompt: Random Hyperbolic Surface S

**Created:** 2026-05-15T15:36:35Z
**Run id:** run-2026-05-15T153635Z

## Directive (verbatim)

# Long-Exposure Research Prompt: Random Hyperbolic Surface Spectral Rigidity

## Core Directive

Run a long-horizon autonomous research program centered on the paper:

- `2603.01127.pdf`
- `2603.01127.txt`

The paper is "Eigenvalue rigidity of hyperbolic surfaces in the random cover model" by Elena Kim and Zhongkai Tao. The first objective is to understand and rederive the paper's key results from first principles, with enough detail that the proof architecture, dependencies, and technical bottlenecks are explicit and inspectable. The second objective is to build from that understanding toward genuinely new research directions in random hyperbolic surfaces, spectral rigidity, eigenfunction delocalization, random covers, trace/pre-trace formula methods, and polynomial-method analogies with random regular graphs.

The intended outcome is not a summary. The intended outcome is a serious research campaign that may take weeks, producing derivations, validation artifacts, computational experiments, proof sketches, counterexample searches, and eventually one or more novel findings or conjectural pathways that could add real value to active research in this domain.

## Autonomy

Long-exposure decides what to do. No user ratification or guidance will be provided to unblock choices during the live run. When there are multiple plausible paths, choose the path with the best balance of mathematical significance, tractability, and evidence production. Use parallel branches for genuinely independent workstreams, such as analytic rederivation, computational experiments, formalized sublemmas, and literature-context mapping.

Milestones and deliverables below are initial scaffolding only. Revise them as the run learns more.

## Initial Research Ladder

1. Establish a precise map of the paper.
   - State the main theorems in the run's own notation.
   - Identify all critical inputs: Selberg trace formula, pre-trace formula, random cover model, permutation representation trace statistics, polynomial approximation, Markov brothers' inequality, Weyl law conversion, and eigenfunction estimates.
   - Separate standard background from paper-specific innovations.

2. Reconstruct the proof.
   - Rebuild the main eigenvalue rigidity argument step by step.
   - Rebuild the eigenfunction delocalization argument and show where it diverges from the eigenvalue proof.
   - Track every nontrivial dependency in a proof ledger.
   - Make explicit which estimates are quantitative, which constants/exponents are non-optimized, and where losses enter.

3. Build computational probes.
   - Implement finite and toy models that mimic random cover behavior through permutation representations and Schreier-style constructions.
   - Test trace-statistic concentration and polynomial-window approximations in simplified settings.
   - Compare toy random-cover behavior with random regular graph analogies where appropriate.
   - Produce reproducible scripts, datasets, and figures.

4. Formalize or certify isolated pieces where useful.
   - Use Lean for small self-contained lemmas: polynomial inequalities, finite combinatorial identities, elementary expectation manipulations, or proof-skeleton checks.
   - Do not attempt to formalize the full Selberg trace formula unless a focused subproblem makes that worthwhile.

5. Search for real extensions.
   - Identify which assumptions are structural and which may be relaxable.
   - Explore whether sharper exponents, improved eigenfunction norms, finer window statistics, multiplicity bounds, or transfer to related random surface models are plausible.
   - Look for a tractable new proposition, conjecture-with-evidence, or technical lemma that meaningfully extends the paper.
   - Prefer one solid new contribution with evidence over many shallow speculations.

6. Produce research-grade artifacts.
   - Maintain `plan_of_record.md`, `promise_ledger.jsonl`, and structured notes.
   - Produce periodic reports that distinguish proven facts, numerically supported hypotheses, failed routes, and open gaps.
   - Keep code and generated data reproducible.
   - End-state outputs should include a final report, audit, curated file map, and a ranked list of credible follow-up research problems.

## Available Workspace Tools

The run is launched from `<workspace>`, which contains the paper and tool support.

Use these tools when they add value:

- Wolfram Language through `wolfram-batch`; use this for symbolic algebra, asymptotics, special-function manipulations, exact checks, and heavier analytic experiments.
- `workspace/wolfram-bridge` is available as a local skill/tool reference for Wolfram-backed workflows. It is not a replacement for direct Wolfram smoke tests.
- Lean 4 and Lake are available; use them selectively for small formal checks.
- GAP is installed minimally with FGA and IO; use it for free groups, finitely presented groups, permutation groups, and group-action toy models.
- Python scientific stack is available: NumPy, SciPy, SymPy, Matplotlib, Pandas, and NetworkX.
- LaTeX/Pandoc/Tectonic are available for report rendering and formula-heavy artifacts.
- Web access is available, but do not use web search as a shortcut for understanding the paper. Use external sources to contextualize, verify, and extend after reconstructing the core argument from the local paper.

## Working Standards

- Be mathematically conservative: label claims as theorem, lemma, heuristic, numerical evidence, conjecture, or failed route.
- Reproduce before extending. Any proposed extension should cite the internal derivation step it builds on.
- Prefer simple robust computations and exact finite checks before expensive experiments.
- Use Wolfram, GAP, Python, and Lean as complementary tools rather than forcing all work through one system.
- Keep artifacts topic-specific and publication-facing; avoid local-machine assumptions in final outputs.
- If a path becomes unproductive, document why and pivot.

## High-Value Targets

Potential high-impact directions include, but are not limited to:

- Sharpening the polynomial rigidity exponent or isolating the dominant exponent loss.
- A toy theorem or experimentally supported conjecture linking the random-cover trace expansion to graph rigidity mechanisms.
- A framework for testing local spectral statistics at windows that shrink with cover degree.
- New multiplicity or delocalization consequences from the paper's estimates.
- A transferable proof template for Weil-Petersson random surfaces or variable-curvature covers.
- A computational benchmark suite for random-cover spectral rigidity heuristics.

The run should remain open to better directions discovered during the work.

## Goals

| Goal ID | Goal | Owner |
|---------|------|-------|
| G1 | Establish an inspectable map of Kim--Tao `2603.01127`: notation, theorem statements, inputs, and proof architecture. | researcher |
| G2 | Reconstruct the eigenvalue rigidity and eigenfunction delocalization proofs from first principles, with dependency and loss ledgers. | researcher |
| G3 | Build reproducible finite/toy computational probes for random-cover trace statistics and polynomial-window approximations. | researcher |
| G4 | Certify isolated technical lemmas where formal or symbolic tooling is useful. | researcher |
| G5 | Identify and test credible extension pathways, prioritizing one mathematically substantive conjecture, lemma, or benchmark suite. | researcher |
| G6 | Develop post-synthesis follow-up results from the strongest validated extension pathway without reopening the completed M1-M6 campaign. | researcher |

## Milestones

| Milestone ID | Goal | Description | Success criteria (falsifiable) | Dependencies |
|--------------|------|-------------|--------------------------------|--------------|
| M1-paper-map | G1 | Produce a paper map of theorem statements, notation, section architecture, and standard-vs-novel inputs. | `docs/paper_map/cycle1_foundational_map.md` names Theorems 1-2 in run notation, lists every cited technical input used in §§2-4, and identifies at least five open unknowns for later cycles. | — |
| M2-proof-ledger | G2 | Reconstruct Theorem 1 and Theorem 2 proof pipelines with quantitative dependencies and exponent-loss locations. | `docs/proof_ledger/rigidity_proof_reconstruction.md` and `docs/proof_ledger/delocalization_proof_reconstruction.md` derive the proposition-to-theorem reductions and record all nontrivial estimates with source locations. | M1-paper-map |
| M3-computational-probes | G3 | Implement random permutation/Schreier-style toy models and polynomial-window diagnostics. | Scripts under `scripts/` generate reproducible CSV data under `data/polynomial_method/` plus at least one named plot comparing concentration or approximation behavior across n/q regimes. | M1-paper-map |
| M4-formal-certification | G4 | Select and certify small standalone lemmas such as polynomial inequalities or finite expectation identities. | At least one Lean/Wolfram/GAP artifact verifies a lemma with an accompanying prose note explaining scope and non-scope. | M1-paper-map, M2-proof-ledger |
| M5-extension-candidates | G5 | Rank extension pathways and test the strongest tractable candidate. | A report states at least three candidates, rejects or advances each with evidence, and formulates one conjecture/lemma/benchmark with reproducible support. | M2-proof-ledger, M3-computational-probes |
| M6-final-synthesis | G1-G5 | Produce end-state research-grade synthesis and audit-ready file map. | `reports/final/final_report.*` distinguishes proven facts, numerical evidence, failed routes, and open gaps; `audits/final/` contains final audit artifacts. | M1-paper-map, M2-proof-ledger, M3-computational-probes, M5-extension-candidates |
| M7-product-ratio-bounds | G6 | Prove and test fixed-order coefficient and derivative envelopes for growing labelled-template product ratios. | `reports/extension_candidates/m7_product_ratio_coefficient_bounds.md` proves the log-coefficient identity and fixed-order envelopes, while `scripts/analyze_product_ratio_bounds.py` validates Cycle 15 families against generated CSV data and a figure. | M5-extension-candidates, M6-final-synthesis |
| M8-quotient-family-bridge | G6 | Classify where the M4/M7 labelled-template product-ratio framework attaches to Kim--Tao trace and pre-trace quotient-family objects. | `reports/extension_candidates/m8_quotient_family_bridge.md` classifies Proposition 3.1/Lemma 3.3/Corollary 3.4 and Proposition 4.2 objects as covered, partially covered, heuristic-only, or not covered, with explicit obstructions and a generated CSV/figure taxonomy. | M2-proof-ledger, M7-product-ratio-bounds |
| M9-aggregate-product-ratio-obstruction | G6 | Formalize what per-template M7 product-ratio bounds do and do not imply for weighted quotient-family sums. | `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md` proves a conditional aggregate coefficient bound and gives deterministic toy examples showing that per-template bounds alone do not control aggregate sums without family-count, total-weight, cancellation, or rank-decay input. | M7-product-ratio-bounds, M8-quotient-family-bridge |
| M10-restricted-quotient-aggregate | G6 | Enumerate a restricted two-word folded quotient-family aggregate model over the free group on two generators. | `reports/extension_candidates/m10_restricted_quotient_aggregate.md` gives deterministic folded profile enumeration, rank-one/rank-two filtering, aggregate coefficient summaries, figures, and a conclusion about whether restricted family-count control is plausible in this toy bridge setting. | M7-product-ratio-bounds, M8-quotient-family-bridge, M9-aggregate-product-ratio-obstruction |
| M11-trace-like-weighted-quotient-class | G6 | Enumerate a trace-like weighted quotient-class model using cyclically reduced conjugacy representatives with primitive and diagonal separation before folding. | `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md` compares raw ordered-pair counts, conjugacy-class representatives, folded profile counts, explicit `n^(C-V)` separation, length-weighted total variation, and diagonal-subtracted coefficient summaries against the M10 obstruction. | M7-product-ratio-bounds, M8-quotient-family-bridge, M9-aggregate-product-ratio-obstruction, M10-restricted-quotient-aggregate |
| M12-restricted-aggregate-theorem-template | G6 | Formalize the restricted aggregate theorem template supported by M7, M9, and M11 with explicit `n_power = C - V` stratification. | `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md` states and proves a conditional independent-permutation labelled-template aggregate proposition, while generated strata and bound-check CSVs test the hypotheses against M11 data without claiming a Kim--Tao trace theorem. | M7-product-ratio-bounds, M9-aggregate-product-ratio-obstruction, M11-trace-like-weighted-quotient-class |
| M13-cancellation-mechanism-diagnostics | G6 | Diagnose whether the M12 stratified total-variation bound can be sharpened by coefficient-level cancellation, rank-sensitive decay, or length-decay in the M11 trace-like toy family. | `reports/extension_candidates/m13_cancellation_mechanism_diagnostics.md` compares signed coefficient sums, coefficient absolute variation, grouped cancellation ratios, candidate opposite-sign pairings, and bound modes within fixed `n_power = C - V` strata, with figures and CSVs distinguishing robust mechanisms from total-variation restatements. | M9-aggregate-product-ratio-obstruction, M11-trace-like-weighted-quotient-class, M12-restricted-aggregate-theorem-template |
| M14-external-decay-thresholds | G6 | Quantify what external rank, length, or folded-complexity decay would be needed to make the M12 aggregate theorem useful after M13 ruled out robust coefficient cancellation. | `reports/extension_candidates/m14_external_decay_thresholds.md` reports polynomial length, exponential length, folded-complexity, and rank-penalty threshold grids for decayed TV, coefficient absolute variation, signed sums, and M12-style bound proxies in the M11/M13 dominant strata. | M11-trace-like-weighted-quotient-class, M12-restricted-aggregate-theorem-template, M13-cancellation-mechanism-diagnostics |
| M15-kim-tao-bridge-requirement | G6 | Convert the M12-M14 aggregate theorem and threshold findings into a Kim--Tao-facing bridge requirement for the actual trace/pre-trace proof objects. | `reports/extension_candidates/m15_kim_tao_bridge_requirement.md` maps Proposition 3.1, Lemma 3.3, Corollary 3.4, and Proposition 4.2 to the M12/M14 framework; `docs/proof_ledger/conditional_decay_to_rigidity_improvement.md` traces conditional exponent consequences; generated CSVs and figures compare M14 decay thresholds with crude Selberg/geodesic growth proxies. | M2-proof-ledger, M8-quotient-family-bridge, M12-restricted-aggregate-theorem-template, M13-cancellation-mechanism-diagnostics, M14-external-decay-thresholds |
| M16-local-spectral-window-corollaries | G6 | Derive and test local/mesoscopic spectral-window consequences of Kim--Tao's Weyl-law and rigidity estimates after the M15 aggregate-control pivot. | `docs/proof_ledger/local_window_from_rigidity.md` derives endpoint-subtraction and rigidity-window corollaries; `reports/extension_candidates/m16_local_spectral_window_corollaries.md` records threshold consequences and limitations; generated CSVs and figures compare Weyl-subtraction, rigidity-displacement, and mean-spacing scales across edge, bulk, and high-energy regimes. | M2-proof-ledger, M15-kim-tao-bridge-requirement |
| M17-local-window-variance-input | G6 | Formulate the localized smoothed-window variance input needed to beat M16 endpoint-subtraction thresholds and benchmark the question on M3 Schreier spectral toy data. | `docs/proof_ledger/local_window_variance_input.md` derives a conditional Chebyshev variance-to-window-count proposition; `reports/extension_candidates/m17_local_window_variance_input.md` compares exponent thresholds and Schreier toy variance scaling; generated CSVs and figures distinguish variance regimes that beat M16 endpoint subtraction from those that do not. | M2-proof-ledger, M3-computational-probes, M16-local-spectral-window-corollaries |
| M18-test-function-localization-feasibility | G6 | Convert the M17 localized variance requirement into a Kim--Tao-facing feasibility map for trace/pre-trace test-function localization. | `docs/proof_ledger/test_function_localization_feasibility.md` records the paper's `f_{Lambda0}`, `h`, `q`, support, and Markov-loss roles; `reports/extension_candidates/m18_test_function_localization_feasibility.md` and generated CSVs/figures compare spectral-window width, `r`-width, geometric support scale, and trace/pre-trace polynomial-loss proxies. | M2-proof-ledger, M16-local-spectral-window-corollaries, M17-local-window-variance-input |
| M19-smoothed-window-paley-wiener-lemma | G6 | Isolate the Fourier-scaling obstruction for smoothed Paley-Wiener spectral windows after M18. | `docs/proof_ledger/smoothed_window_paley_wiener_obstruction.md` states the scaling/leakage lemma; `reports/extension_candidates/m19_smoothed_window_paley_wiener_lemma.md` and generated CSVs/figures classify logarithmic, sub-polynomial, and polynomial support for shrinking bulk and edge windows. | M17-local-window-variance-input, M18-test-function-localization-feasibility |
| M20-long-support-trace-variance-requirement | G6 | Quantify the random-cover variance saving required if the local-window trace route accepts polynomial geometric support after M19. | `docs/proof_ledger/long_support_trace_variance_requirement.md` states the exponent-budget theorem template; `reports/extension_candidates/m20_long_support_trace_variance_requirement.md` and generated CSVs/figures separate trace and pre-trace long-support loss budgets and identify any endpoint-beating regimes that remain conditionally plausible. | M17-local-window-variance-input, M18-test-function-localization-feasibility, M19-smoothed-window-paley-wiener-lemma |
| M21-trace-side-long-support-variance-template | G6 | Formulate the missing fixed-energy trace-side long-support variance theorem template precisely enough to attack or reject. | `docs/proof_ledger/trace_side_long_support_variance_template.md` names the spectral and trace-formula statistics, states `LSTV_trace(eta,beta)`, derives the local-window consequence, and maps required Kim--Tao proof-input strengthenings; `reports/extension_candidates/m21_trace_side_long_support_variance_template.md` and generated CSVs/figures classify candidate beta models and state the next decision. | M17-local-window-variance-input, M18-test-function-localization-feasibility, M19-smoothed-window-paley-wiener-lemma, M20-long-support-trace-variance-requirement |
| M22-trace-corollary34-uniform-coefficient-variation-target | G6 | Isolate the localized Corollary 3.4 numerator target needed upstream of the M21 long-support trace variance theorem. | `docs/proof_ledger/trace_corollary34_localized_numerator_target.md` defines the localized weighted numerator or documents the exact mismatch with Kim--Tao's `p`; `reports/extension_candidates/m22_trace_corollary34_uniform_coefficient_variation_target.md` and generated CSVs/figures translate coefficient-variation, direct small-`x`, and stratified weighted numerator hypotheses into beta-saving budgets and state the next decision. | M15-kim-tao-bridge-requirement, M19-smoothed-window-paley-wiener-lemma, M20-long-support-trace-variance-requirement, M21-trace-side-long-support-variance-template |
| M23-localized-trace-numerator-quotient-family-model | G6 | Model the weighted quotient/template strata appearing in the localized Corollary 3.4 numerator. | `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md` extracts the summation variables and row schema; `reports/extension_candidates/m23_localized_trace_numerator_quotient_family_model.md`, generated CSVs, tests, and figures compare transform-weight damping against quotient-family growth proxies while preserving `d=C-V` stratification and surface-group-law uncertainty. | M21-trace-side-long-support-variance-template, M22-trace-corollary34-uniform-coefficient-variation-target |
| M24-localized-transform-geodesic-weight-decay-obstruction | G6 | Determine whether paper-compatible localized transform and Selberg/geodesic weights can justify the optimistic M23 decay inside the localized Corollary 3.4 numerator. | `docs/proof_ledger/localized_transform_geodesic_weight_decay.md` classifies compact-support, Paley-Wiener, moment-decay, and noncompact-tail mechanisms; `reports/extension_candidates/m24_localized_transform_geodesic_weight_decay_obstruction.md`, generated CSVs, tests, and figures compare transform envelopes against geodesic/family growth proxies and state whether the compact-support local-window route remains viable. | M19-smoothed-window-paley-wiener-lemma, M21-trace-side-long-support-variance-template, M22-trace-corollary34-uniform-coefficient-variation-target, M23-localized-trace-numerator-quotient-family-model |
| M25-local-window-route-synthesis-and-branch-decision | G6 | Synthesize M16-M24 into a decision-quality local-window branch record and identify the remaining proof targets. | `docs/proof_ledger/local_window_branch_decision_record.md`, `reports/extension_candidates/m25_local_window_route_synthesis_and_branch_decision.md`, and `reports/final/local_window_followup_problem_statement.md` classify the evidence chain, state the compact coefficient-variation and noncompact trace-tail theorem targets, generate decision CSVs/figures, and record the final branch decision. | M16-local-spectral-window-corollaries, M17-local-window-variance-input, M18-test-function-localization-feasibility, M19-smoothed-window-paley-wiener-lemma, M20-long-support-trace-variance-requirement, M21-trace-side-long-support-variance-template, M22-trace-corollary34-uniform-coefficient-variation-target, M23-localized-trace-numerator-quotient-family-model, M24-localized-transform-geodesic-weight-decay-obstruction |
| M26-post-local-extension-reprioritization | G6 | Re-rank post-local extension branches after M25 preserved the shrinking local-window branch as a follow-up problem. | `reports/extension_candidates/m26_post_local_extension_reprioritization.md`, `docs/proof_ledger/post_local_branch_attachment_points.md`, and `reports/final/post_local_followup_ranked_problem_list.md` score at least five candidate branches, distinguish theorem-level corollaries from toy/model programs, and recommend exactly one next milestone independent of the M25 open theorem. | M2-proof-ledger, M3-computational-probes, M4-formal-certification, M15-kim-tao-bridge-requirement, M16-local-spectral-window-corollaries, M25-local-window-route-synthesis-and-branch-decision |
| M27-multiplicity-and-cluster-corollaries-from-rigidity | G6 | Derive theorem-level multiplicity and spectral-cluster envelopes from Kim--Tao Theorem 1 rigidity without adding new trace or local-window variance input. | `docs/proof_ledger/multiplicity_cluster_from_rigidity.md` states the deterministic rigidity-to-cluster lemma; `reports/extension_candidates/m27_multiplicity_cluster_corollaries.md` separates bulk, edge, and high-energy regimes; generated CSVs and figures classify when the corollary is nontrivial, endpoint-equivalent, or high-energy-loss dominated. | M2-proof-ledger, M16-local-spectral-window-corollaries, M26-post-local-extension-reprioritization |
| M28-theorem2-lp-mass-distribution-corollaries | G6 | Derive theorem-level `L^p`, small-set mass, and effective-support consequences from Kim--Tao Theorem 2 eigenfunction delocalization. | `docs/proof_ledger/theorem2_lp_mass_corollaries.md` states deterministic norm/mass corollaries; `reports/extension_candidates/m28_theorem2_lp_mass_corollaries.md` classifies the consequences; generated CSVs and figures compare direct and interpolation-improved Lambda models across p, n, energy, and set-volume regimes. | M2-proof-ledger, M26-post-local-extension-reprioritization, M27-multiplicity-and-cluster-corollaries-from-rigidity |
| M29-pretrace-local-mass-intermediate-from-theorem2-proof | G6 | Mine Kim--Tao Theorem 2's pre-trace proof for a standalone fixed-cutoff local `L^2` mass statement before the final Sobolev/elliptic `L^\infty` conversion. | `docs/proof_ledger/pretrace_local_mass_intermediate.md` identifies the controlled statistic and valid quantifiers; `reports/extension_candidates/m29_pretrace_local_mass_intermediate.md` classifies whether the result is geometric, smoothed-kernel, or proof-internal; generated CSVs and figures compare the pre-Sobolev local-mass budget with M28's final sup-norm-derived mass bound. | M2-proof-ledger, M26-post-local-extension-reprioritization, M28-theorem2-lp-mass-distribution-corollaries |
| M30-schreier-benchmark-theoremization | G6 | Turn the validated M3 Schreier/random-permutation spectral probe into a theorem-grade finite benchmark for trace moments, tree subtraction, and fluctuation scaling. | `docs/proof_ledger/schreier_trace_moment_benchmark.md` states the fixed-k expectation theorem template; `reports/extension_candidates/m30_schreier_benchmark_theoremization.md` scopes the analogy to Kim--Tao trace methods; generated CSVs and figures regenerate 4-regular tree moments through k=10 and test centered variance scaling across at least four n-values and three even moments. | M3-computational-probes, M4-formal-certification, M26-post-local-extension-reprioritization, M29-pretrace-local-mass-intermediate-from-theorem2-proof |
| M31-schreier-variance-mechanism-theoremization | G6 | Upgrade M30's numerical variance evidence into a fixed-k paired-word covariance mechanism theorem template for the two-permutation Schreier benchmark. | `docs/proof_ledger/schreier_variance_mechanism.md` derives the paired fixed-word variance expansion; `reports/extension_candidates/m31_schreier_variance_mechanism.md` compares small-k pair-template certifications with M30 slopes; generated CSVs and figures classify covariance orders for k=2,4,6 and state whether to advance the variance theorem branch. | M4-formal-certification, M26-post-local-extension-reprioritization, M30-schreier-benchmark-theoremization |
| M32-schreier-fixed-pair-covariance-lemma | G6 | Prove the arbitrary fixed-k reduced-word pair covariance exponent lemma left open by M31 for the two-permutation Schreier benchmark. | `docs/proof_ledger/schreier_fixed_pair_covariance_lemma.md` states and proves or sharply localizes the quotient-template exponent lemma; `reports/extension_candidates/m32_schreier_fixed_pair_covariance_lemma.md` connects it to `Var(n^{-1}Tr(A_n^k)) = O_k(n^{-2})`; generated CSVs, tests, and figures compare the proof classification against M31 small-k template evidence. | M4-formal-certification, M30-schreier-benchmark-theoremization, M31-schreier-variance-mechanism-theoremization |
| M33-schreier-benchmark-package-synthesis | G6 | Consolidate M30-M32 into a standalone theorem-grade benchmark package for the two-permutation Schreier model. | `docs/proof_ledger/schreier_benchmark_theorem_package.md` states the fixed-k expectation, deterministic tree-word separation, fixed-pair covariance, and normalized variance theorem in one coherent proof; `reports/extension_candidates/m33_schreier_benchmark_package_synthesis.md` and `reports/final/schreier_benchmark_theorem_package.md` provide a reproducible benchmark suite, artifact index, dependency map, and explicit no-transfer firewall. | M30-schreier-benchmark-theoremization, M31-schreier-variance-mechanism-theoremization, M32-schreier-fixed-pair-covariance-lemma |
| M34-finite-nonshrinking-spectral-statistics | G6 | Derive and classify fixed-energy, non-shrinking spectral-window statistics from Kim--Tao rigidity and Weyl estimates after closing the Schreier benchmark branch. | `docs/proof_ledger/finite_nonshrinking_spectral_statistics.md` states fixed-width endpoint-subtraction, rigidity, and centered-count consequences with explicit edge/bulk regimes; `reports/extension_candidates/m34_finite_nonshrinking_spectral_statistics.md` and generated CSVs/figures compare each statement against the M16 endpoint baseline and classify whether it is theorem-level content or bookkeeping. | M2-proof-ledger, M16-local-spectral-window-corollaries, M25-local-window-route-synthesis-and-branch-decision, M33-schreier-benchmark-package-synthesis |
| M35-surface-corollary34-numerator-obstruction | G6 | Return to the actual Kim--Tao Lemma 3.3 / Corollary 3.4 surface-group numerator after M34, and determine whether a coefficient-variation or direct small-`x` saving is plausibly attackable or obstructed by the paper's existing quotient-polynomial architecture. | `docs/proof_ledger/surface_corollary34_numerator_obstruction.md` states the exact numerator, denominator, degree/support, and interpolation step from the paper; `reports/extension_candidates/m35_surface_corollary34_numerator_obstruction.md` and generated CSVs/figures compare Markov interpolation, coefficient-variation, and direct evaluation mechanisms, classifying which would be theorem-level and which are blocked by missing surface-group inputs. | M2-proof-ledger, M8-quotient-family-bridge, M15-kim-tao-bridge-requirement, M22-trace-corollary34-uniform-coefficient-variation-target, M25-local-window-route-synthesis-and-branch-decision, M34-finite-nonshrinking-spectral-statistics |
| M36-direct-small-x-surface-numerator-target | G6 | Attack the M35 open target by formulating and testing the narrowest direct small-`x` theorem target for the actual denominator-normalized Corollary 3.4 surface numerator, before committing to a broader coefficient-variation theorem. | `docs/proof_ledger/direct_small_x_surface_numerator_target.md` states the exact direct-evaluation bound on `p(1/n)/Q_id(1/n)` that would replace Markov interpolation; `reports/extension_candidates/m36_direct_small_x_surface_numerator_target.md` and generated CSVs/figures compare denominator normalization, Lemma 3.3 range/error, endpoint exponent budgets, and obstruction scenarios, classifying the target as theorem-ready, conditional, or blocked. | M2-proof-ledger, M15-kim-tao-bridge-requirement, M22-trace-corollary34-uniform-coefficient-variation-target, M25-local-window-route-synthesis-and-branch-decision, M35-surface-corollary34-numerator-obstruction |
| M37-signed-pointwise-cancellation-surface-aggregate | G6 | Probe whether the direct small-`x` target from M36 can be supported by genuine signed pointwise cancellation in the actual Kim--Tao Corollary 3.4 surface aggregate at `x=1/n`, rather than by absolute coefficient variation or toy-model transfer. | `docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md` reconstructs the signed summand structure, denominator normalization, and candidate cancellation groupings for the paper-defined ratio; `reports/extension_candidates/m37_signed_pointwise_cancellation_surface_aggregate.md` plus generated CSVs/figures classify sign-pairing, stratum cancellation, phase/oscillation, and denominator scenarios as theorem-target, coefficient-variation-equivalent, or blocked. | M2-proof-ledger, M15-kim-tao-bridge-requirement, M22-trace-corollary34-uniform-coefficient-variation-target, M35-surface-corollary34-numerator-obstruction, M36-direct-small-x-surface-numerator-target |
| M38-surface-native-grouping-problem | G6 | Formulate the actual surface-attached grouping problem for the evaluated Corollary 3.4 aggregate, testing whether quotient complex, primitive-power structure, length shell, or surface-relation kernel constraints define natural cancellation groups at `x=1/n`. | `docs/proof_ledger/surface_native_grouping_problem.md` reconstructs the candidate paper-native invariants and their relation to Lemma 3.3 / Corollary 3.4 summands; `reports/extension_candidates/m38_surface_native_grouping_problem.md` plus generated CSVs/figures classify each grouping as signed-pointwise theorem-ready, coefficient-variation-equivalent, denominator/range blocked, or underdetermined by current paper inputs. | M2-proof-ledger, M15-kim-tao-bridge-requirement, M22-trace-corollary34-uniform-coefficient-variation-target, M35-surface-corollary34-numerator-obstruction, M36-direct-small-x-surface-numerator-target, M37-signed-pointwise-cancellation-surface-aggregate |
| M39-surface-relation-kernel-spc-probe | G6 | Probe the strongest M38 direct target by inspecting whether the Lemma 3.3 folded-quotient kernel-closure condition for `F_{2g} -> Gamma` can generate signed evaluated cancellation in `p(1/n)/Q_id(1/n)` at `x=1/n`. | `docs/proof_ledger/surface_relation_kernel_spc_probe.md` reconstructs the kernel-closure constraint and candidate signed grouping theorem; `reports/extension_candidates/m39_surface_relation_kernel_spc_probe.md` plus generated CSVs/figures decide whether the relation-kernel route is theorem-ready, underdetermined, coefficient-variation-equivalent, or blocked. | M2-proof-ledger, M15-kim-tao-bridge-requirement, M22-trace-corollary34-uniform-coefficient-variation-target, M35-surface-corollary34-numerator-obstruction, M36-direct-small-x-surface-numerator-target, M37-signed-pointwise-cancellation-surface-aggregate, M38-surface-native-grouping-problem |

## Out of scope (explicit)

- Formalizing the full Selberg trace formula or full random-cover spectral theory in Lean.
- Treating web/literature search as a substitute for reconstructing the local paper.
- Optimizing constants or exponents before the source of exponent loss is mapped.

## Pointer to ledger

Every milestone status, history, and judgment lives in `promise_ledger.jsonl`,
filtered by `milestone_id`. Run `promise_check` to materialize the current
state for the human; agents call it via Bash:

    python3 -m long_exposure.tools.promise_check .

The directive section above is **immutable** after creation. Goals and
milestones tables are mutable, but every edit must emit a ledger event with
`milestone_id: "_plan/<descriptive-change-name>"` so the audit trail is
complete.
