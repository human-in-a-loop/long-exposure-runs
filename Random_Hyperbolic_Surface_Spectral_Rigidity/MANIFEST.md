# Long-Exposure Workspace Manifest

Snapshot after cycles 49-50. This file is a compact navigation aid for the Kim--Tao random-cover spectral-rigidity campaign.

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `scripts/certify_labelled_embedding_expectation.py` — labelled-template expectation identity cited in First Computational and Formal Probes.
- `scripts/analyze_product_ratio_bounds.py` — product-ratio stability and growing-template envelope results cited in Product-Ratio Stability and Its Boundary.
- `scripts/build_local_window_route_synthesis.py` — local-window obstruction and branch decision cited in Local Spectral Windows and the Compact-Support Obstruction.
- `scripts/build_schreier_benchmark_package.py` — standalone Schreier benchmark theorem package cited in Standalone Schreier Benchmark Theorem.
- `scripts/analyze_surface_corollary34_numerator_obstruction.py` — Corollary 3.4 numerator reconstruction and Markov-loss localization cited in The Corollary 3.4 Numerator Bottleneck.
- `scripts/analyze_direct_small_x_surface_numerator_target.py` — direct small-`x` target and denominator-loss budget cited in The Corollary 3.4 Numerator Bottleneck.
- `scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py` — signed pointwise cancellation classification cited in The Corollary 3.4 Numerator Bottleneck.
- `scripts/analyze_surface_native_grouping_problem.py` — surface-native grouping taxonomy cited in Surface-Native Grouping and the Current Pivot.
- `scripts/analyze_surface_relation_kernel_spc_probe.py` — kernel-closure signed-cancellation probe and pivot cited in Surface-Native Grouping and the Current Pivot.

## Cumulative Stats

- Python scripts: 48 files, 15,289 lines.
- Python tests: 40 files, 3,604 lines.
- Canonical CSV datasets: 114 files under `data/`.
- PNG figures: 98 files under `reports/figures/`.
- Documentation/report artifacts: 222 Markdown/DOT/PNG files under `docs/`, `reports/`, and `audits/`.
- Promise ledger events: 150.
- Plan milestones: 39.

## Script Inventory

### Toy Random-Cover And Polynomial Probes

- `scripts/probe_common_fixed_points.py` (282 lines) - common fixed-point statistics for random permutation words.
- `scripts/probe_folded_word_graphs.py` (398 lines) - folded word-graph profile experiments.
- `scripts/probe_labelled_graph_embeddings.py` (444 lines) - labelled graph embedding probes.
- `scripts/probe_polynomial_window_diagnostics.py` (320 lines) - polynomial-window approximation diagnostics.
- `scripts/probe_schreier_spectral_toy.py` (367 lines) - Schreier-style spectral toy model.
- `scripts/check_markov_scaling.py` (60 lines) - Markov scaling sanity checks.
- `scripts/certify_labelled_embedding_expectation.py` (240 lines) - Python certification for labelled embedding expectation identity.
- `scripts/test_selberg_weight_vs_template_growth.py` (243 lines) - Selberg weight versus quotient-template growth probe.

### Product-Ratio And Aggregate-Control Branch

- `scripts/analyze_product_ratio_bounds.py` (237 lines) - product-ratio envelope calculations.
- `scripts/build_quotient_family_bridge_table.py` (243 lines) - quotient-family bridge taxonomy.
- `scripts/analyze_aggregate_product_ratio_obstruction.py` (231 lines) - aggregate product-ratio obstruction grid.
- `scripts/enumerate_restricted_quotient_aggregates.py` (404 lines) - restricted quotient aggregate enumeration.
- `scripts/enumerate_trace_like_weighted_quotients.py` (568 lines) - trace-like weighted quotient-class enumeration.
- `scripts/analyze_restricted_aggregate_theorem_template.py` (224 lines) - conditional restricted-aggregate theorem template.
- `scripts/analyze_cancellation_mechanisms.py` (425 lines) - cancellation mechanism diagnostics.
- `scripts/model_external_decay_thresholds.py` (471 lines) - external decay threshold calibration.
- `scripts/analyze_surface_corollary34_numerator_obstruction.py` (400 lines) - localizes the actual Corollary 3.4 numerator Markov/interpolation loss.
- `scripts/analyze_direct_small_x_surface_numerator_target.py` (445 lines) - classifies direct small-`x` replacement targets and denominator-loss budgets.
- `scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py` (503 lines) - classifies signed pointwise cancellation mechanisms for the evaluated surface aggregate.
- `scripts/analyze_surface_native_grouping_problem.py` (562 lines) - classifies paper-native grouping invariants for the evaluated Corollary 3.4 aggregate.
- `scripts/analyze_surface_relation_kernel_spc_probe.py` (678 lines) - probes whether Lemma 3.3 surface-relation kernel closure supplies evaluated signed cancellation.

### Local-Window Route

- `scripts/analyze_local_window_thresholds.py` (273 lines) - endpoint-subtraction local-window threshold map.
- `scripts/analyze_local_window_variance_requirements.py` (172 lines) - smoothed-window variance input budget.
- `scripts/analyze_test_function_localization_tradeoffs.py` (261 lines) - Kim--Tao test-function localization feasibility.
- `scripts/analyze_smoothed_window_leakage.py` (251 lines) - Paley-Wiener/logarithmic-support leakage obstruction.
- `scripts/analyze_long_support_variance_budget.py` (278 lines) - polynomial long-support trace/pre-trace variance budget.
- `scripts/analyze_trace_variance_template_budget.py` (268 lines) - fixed-energy trace-side theorem-template budget.
- `scripts/analyze_corollary34_target_budget.py` (245 lines) - localized Corollary 3.4 numerator beta budget.
- `scripts/model_localized_trace_numerator_quotients.py` (288 lines) - localized numerator quotient-family proxy model.
- `scripts/analyze_localized_transform_weight_decay.py` (296 lines) - localized transform/geodesic damping obstruction model.
- `scripts/build_local_window_route_synthesis.py` (279 lines) - local-window branch synthesis and decision tables.

### Post-Local Corollaries And Surface-Facing Packages

- `scripts/score_post_local_extension_candidates.py` (324 lines) - scores post-local extension candidates.
- `scripts/analyze_multiplicity_cluster_bounds.py` (240 lines) - computes rigidity-scale multiplicity and cluster envelopes.
- `scripts/analyze_theorem2_lp_mass_corollaries.py` (247 lines) - computes Theorem 2 `L^p`, small-set mass, and support grids.
- `scripts/analyze_pretrace_local_mass_budget.py` (224 lines) - compares pre-trace local-mass bounds with final sup-norm consequences.
- `scripts/analyze_finite_nonshrinking_spectral_statistics.py` (359 lines) - derives fixed positive-width spectral-window count corollaries and scope classifications.

### Schreier Benchmark Program

- `scripts/analyze_schreier_window_variance_benchmark.py` (138 lines) - early Schreier window variance benchmark.
- `scripts/analyze_schreier_trace_benchmark.py` (417 lines) - regenerates Schreier tree moments and variance-scaling benchmark tables.
- `scripts/analyze_schreier_variance_pair_templates.py` (597 lines) - classifies fixed-word pair templates and covariance orders.
- `scripts/prove_schreier_fixed_pair_covariance.py` (491 lines) - proof companion for fixed-pair covariance quotient-template bounds.
- `scripts/build_schreier_benchmark_package.py` (311 lines) - consolidates M30-M32 into the M33 standalone theorem package.

### Reporting And Figure Utilities

- `scripts/score_m5_extension_candidates.py` (183 lines) - ranks initial extension candidates.
- `scripts/plot_m5_extension_synthesis.py` (230 lines) - plots M5 extension synthesis.
- `scripts/compare_expansions_to_cycle9.py` (296 lines) - compares expansion models with earlier cycle fits.
- `scripts/plot_growing_template_expansions.py` (371 lines) - plots growing-template expansion diagnostics.
- `scripts/plot_m3_probe_ladder_summary.py` (112 lines) - plots M3 probe ladder summary.
- `scripts/build_final_synthesis_index.py` (207 lines) - builds final synthesis index data.
- `scripts/plot_final_campaign_summary.py` (186 lines) - plots final campaign summary figures.

## Test Inventory

### Local-Window Cycle Tests

- `tests/test_local_window_thresholds.py` (72 lines) - validates endpoint threshold calculations.
- `tests/test_local_window_variance_requirements.py` (76 lines) - validates variance-requirement algebra.
- `tests/test_test_function_localization_tradeoffs.py` (82 lines) - validates localization feasibility regimes.
- `tests/test_smoothed_window_leakage.py` (70 lines) - validates Paley-Wiener leakage classification.
- `tests/test_long_support_variance_budget.py` (99 lines) - validates long-support variance-budget formulas.
- `tests/test_trace_variance_template_budget.py` (94 lines) - validates trace template thresholds.
- `tests/test_corollary34_target_budget.py` (90 lines) - validates numerator beta mapping.
- `tests/test_localized_trace_numerator_quotients.py` (88 lines) - validates quotient strata and certification tags.
- `tests/test_localized_transform_weight_decay.py` (91 lines) - validates transform scaling and success classification.
- `tests/test_local_window_route_synthesis.py` (78 lines) - validates evidence index and decision table.

### Post-Local And Surface-Facing Tests

- `tests/test_post_local_extension_candidates.py` (72 lines) - validates post-local ranking and next milestone.
- `tests/test_multiplicity_cluster_bounds.py` (72 lines) - validates density formulas, edge scaling, and branch decision.
- `tests/test_theorem2_lp_mass_corollaries.py` (83 lines) - validates interpolation exponents, mass thresholds, and classification.
- `tests/test_pretrace_local_mass_budget.py` (76 lines) - validates local-mass classification and safeguards.
- `tests/test_finite_nonshrinking_spectral_statistics.py` (100 lines) - validates fixed-window Weyl derivatives, edge expansion, shrinking-window exclusion, and no-local-statistics rows.

### Schreier Benchmark Tests

- `tests/test_schreier_spectral_toy.py` (59 lines) - validates Schreier spectral toy outputs.
- `tests/test_schreier_trace_benchmark.py` (87 lines) - validates tree moments, reproducibility, and classification.
- `tests/test_schreier_variance_pair_templates.py` (95 lines) - validates pair classes and all-pair class-order repair.
- `tests/test_schreier_fixed_pair_covariance.py` (99 lines) - validates fixed-pair covariance theorem companion outputs and representative templates.
- `tests/test_schreier_benchmark_package.py` (81 lines) - validates M33 claim ledger, artifact index, and scope firewall.

### Earlier Probe And Aggregate Tests

- `tests/test_product_ratio_bounds.py` (70 lines) - validates product-ratio bounds.
- `tests/test_quotient_family_bridge_table.py` (73 lines) - validates quotient bridge taxonomy.
- `tests/test_aggregate_product_ratio_obstruction.py` (67 lines) - validates aggregate obstruction formulas.
- `tests/test_restricted_quotient_aggregates.py` (68 lines) - validates restricted quotient enumeration.
- `tests/test_trace_like_weighted_quotients.py` (108 lines) - validates weighted quotient profiles.
- `tests/test_restricted_aggregate_theorem_template.py` (94 lines) - validates theorem-template strata.
- `tests/test_cancellation_mechanisms.py` (127 lines) - validates cancellation diagnostics.
- `tests/test_external_decay_thresholds.py` (126 lines) - validates external decay thresholds.
- `tests/test_surface_corollary34_numerator_obstruction.py` (109 lines) - validates M35 numerator-object, Markov-loss, special-point, and no-transfer classifications.
- `tests/test_direct_small_x_surface_numerator_target.py` (129 lines) - validates M36 direct ratio target, denominator-loss algebra, `Lambda0^20`, and no-transfer guards.
- `tests/test_signed_pointwise_cancellation_surface_aggregate.py` (151 lines) - validates M37 signed-cancellation classifications, denominator degradation, and regression guards.
- `tests/test_surface_native_grouping_problem.py` (152 lines) - validates M38 grouping taxonomy, theorem templates, denominator beta loss, and pivot guards.
- `tests/test_surface_relation_kernel_spc_probe.py` (149 lines) - validates M39 kernel-closure reconstruction, classification, beta algebra, and pivot guards.
- `tests/test_labelled_embedding_expectation_identity.py` (79 lines) - validates labelled embedding expectation identity.
- `tests/test_labelled_graph_embeddings.py` (87 lines) - validates labelled graph embedding probes.
- `tests/test_folded_word_graphs.py` (59 lines) - validates folded word graph probes.
- `tests/test_polynomial_window_diagnostics.py` (72 lines) - validates polynomial window diagnostics.
- `tests/test_permutation_word_eval.py` (57 lines) - validates permutation word evaluation helpers.
- `tests/test_growing_template_expansions.py` (80 lines) - validates growing-template expansions.
- `tests/test_labelled_embedding_expansions.py` (83 lines) - validates labelled embedding expansion coefficients.

## Cycle 43-50 Artifacts

### M32 Schreier Fixed-Pair Covariance Lemma

- `docs/proof_ledger/schreier_fixed_pair_covariance_lemma.md` (181 lines) - proves the fixed-pair covariance lemma using quotient-template exponent bounds.
- `reports/extension_candidates/m32_schreier_fixed_pair_covariance_lemma.md` (101 lines) - states the decision and proof/audit-harness distinction.
- `reports/final/schreier_variance_theorem_statement.md` (32 lines) - concise fixed-`k` Schreier variance theorem statement.
- `data/extension_candidates/m32_pair_quotient_classification.csv` (91 lines) - 90 length/class rows through reduced length 6.
- `data/extension_candidates/m32_covariance_exponent_proof_checks.csv` (181 lines) - 180 same/distinct-basepoint representative audit rows.
- `data/extension_candidates/m32_variance_theorem_implication.csv` (5 lines) - fixed-pair, exceptional-class, fixed-`k`, and scope-firewall implications.
- `reports/figures/m32_pair_quotient_exponent_map.png` - 1669x863 pair quotient exponent map.
- `reports/figures/m32_variance_theorem_dependency_map.png` - 1570x756 dependency map.

### M33 Schreier Benchmark Theorem Package

- `docs/proof_ledger/schreier_benchmark_theorem_package.md` (124 lines) - self-contained fixed-`k` expectation and variance theorem package.
- `reports/extension_candidates/m33_schreier_benchmark_package_synthesis.md` (87 lines) - synthesis report with claim ledger and scope firewall.
- `reports/final/schreier_benchmark_theorem_package.md` (44 lines) - concise publication-facing theorem statement.
- `data/final/m33_schreier_package_artifact_index.csv` (26 lines) - 25 source/output artifact rows.
- `data/final/m33_schreier_theorem_claim_ledger.csv` (8 lines) - seven claim rows.
- `data/final/m33_schreier_dependency_edges.csv` (11 lines) - ten dependency edges.
- `data/final/m33_schreier_scope_firewall.csv` (8 lines) - seven inside/outside-scope rows.
- `reports/figures/m33_schreier_theorem_dependency_graph.png` - 2700x1170 theorem dependency graph.
- `reports/figures/m33_schreier_scope_firewall.png` - 2160x900 scope-firewall figure.
- `reports/figures/m33_schreier_variance_package_summary.png` - 1260x900 variance package summary.

### M34 Finite Non-Shrinking Spectral Statistics

- `docs/proof_ledger/finite_nonshrinking_spectral_statistics.md` (82 lines) - fixed-window endpoint-subtraction theorem and scope boundary.
- `reports/extension_candidates/m34_finite_nonshrinking_spectral_statistics.md` (58 lines) - fixed-window corollary package and classification.
- `reports/final/nonshrinking_statistics_followup_statement.md` (18 lines) - concise follow-up statement.
- `data/extension_candidates/m34_fixed_window_thresholds.csv` (64 lines) - 63 fixed/shrinking threshold rows.
- `data/extension_candidates/m34_fixed_window_classification.csv` (8 lines) - seven theorem/bookkeeping/no-claim rows.
- `data/extension_candidates/m34_endpoint_vs_rigidity_comparison.csv` (16 lines) - 15 endpoint-vs-rigidity comparison rows.
- `reports/figures/m34_fixed_window_relative_error.png` - 1475x900 relative error figure.
- `reports/figures/m34_endpoint_vs_rigidity_map.png` - 1260x864 endpoint-vs-rigidity map.
- `reports/figures/m34_window_regime_classification.png` - 1512x900 regime classification figure.

### M35 Surface Corollary 3.4 Numerator Obstruction

- `docs/proof_ledger/surface_corollary34_numerator_obstruction.md` (183 lines) - reconstructs the actual Corollary 3.4 ratio and locates the `q^(2 kappa)` loss at Markov interpolation.
- `reports/extension_candidates/m35_surface_corollary34_numerator_obstruction.md` (133 lines) - mechanism classification for Markov, coefficient variation, direct small-`x`, signed cancellation, stronger Lemma 3.3, and toy-only routes.
- `data/extension_candidates/m35_interpolation_loss_budget.csv` (91 lines) - 90 exponent-budget rows recovering the Markov baseline and conditional replacement algebra.
- `data/extension_candidates/m35_candidate_mechanism_classification.csv` (14 lines) - 13 mechanism/special-point/no-transfer rows.
- `data/extension_candidates/m35_surface_input_gap_matrix.csv` (7 lines) - six paper-input and missing-surface-input rows.
- `data/extension_candidates/m35_direct_vs_markov_regime_grid.csv` (101 lines) - 100 conditional direct-vs-Markov regime rows.
- `reports/figures/m35_corollary34_interpolation_loss.png` - 1360x736 interpolation-loss figure.
- `reports/figures/m35_mechanism_dependency_graph.png` - 1472x800 dependency graph.
- `reports/figures/m35_direct_vs_coefficient_variation_map.png` - 1680x608 direct-vs-coefficient-variation map.

### M36 Direct Small-x Surface Numerator Target

- `docs/proof_ledger/direct_small_x_surface_numerator_target.md` (123 lines) - states the direct theorem target for `p(1/n)/Q_id(1/n)` and denominator-normalization conditions.
- `reports/extension_candidates/m36_direct_small_x_surface_numerator_target.md` (81 lines) - classifies direct evaluation, coefficient variation, signed cancellation, denominator control, and toy-transfer firewalls.
- `data/extension_candidates/m36_direct_small_x_budget.csv` (121 lines) - 120 direct small-`x` exponent-budget rows.
- `data/extension_candidates/m36_denominator_obstruction_grid.csv` (401 lines) - 400 denominator-loss rows.
- `data/extension_candidates/m36_mechanism_classification.csv` (17 lines) - 16 mechanism/special-point rows.
- `data/extension_candidates/m36_direct_vs_cv_implication_table.csv` (6 lines) - five direct-vs-coefficient-variation implication rows.
- `reports/figures/m36_direct_small_x_budget_map.png` - 1620x990 direct-budget figure.
- `reports/figures/m36_denominator_obstruction_map.png` - 1350x936 denominator-obstruction figure.
- `reports/figures/m36_direct_vs_cv_dependency_graph.png` - 1800x1044 dependency graph.

### M37 Signed Pointwise Cancellation Surface Aggregate

- `docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md` (96 lines) - reconstructs the signed aggregate and states the signed pointwise cancellation target.
- `reports/extension_candidates/m37_signed_pointwise_cancellation_surface_aggregate.md` (65 lines) - classifies viable surface-attached signed mechanisms versus coefficient-variation-equivalent, range-blocked, denominator-blocked, and toy-only rows.
- `data/extension_candidates/m37_signed_mechanism_classification.csv` (19 lines) - 18 mechanism classification rows.
- `data/extension_candidates/m37_stratum_cancellation_grid.csv` (436 lines) - 435 stratum/cancellation budget rows.
- `data/extension_candidates/m37_denominator_signed_saving_grid.csv` (126 lines) - 125 denominator-signed-saving rows.
- `data/extension_candidates/m37_theorem_target_table.csv` (6 lines) - five theorem-target and blocked-route rows.
- `reports/figures/m37_signed_mechanism_map.png` - 1530x864 signed mechanism map.
- `reports/figures/m37_stratum_cancellation_budget.png` - 1620x864 stratum cancellation budget figure.
- `reports/figures/m37_direct_vs_cv_cancellation_boundary.png` - 1530x864 direct-vs-coefficient-variation boundary figure.

### M38 Surface-Native Grouping Problem

- `docs/proof_ledger/surface_native_grouping_problem.md` (103 lines) - formulates candidate paper-native grouping invariants for the evaluated Corollary 3.4 aggregate.
- `reports/extension_candidates/m38_surface_native_grouping_problem.md` (68 lines) - classifies grouping routes and states the direct `SPC_G(A,sigma)` theorem templates.
- `data/extension_candidates/m38_grouping_invariant_classification.csv` (13 lines) - 12 grouping classification rows.
- `data/extension_candidates/m38_grouping_beta_budget.csv` (721 lines) - 720 denominator-safe and denominator-loss beta-budget rows.
- `data/extension_candidates/m38_grouping_dependency_matrix.csv` (85 lines) - 84 grouping dependency and obstruction rows.
- `data/extension_candidates/m38_candidate_spc_theorem_templates.csv` (6 lines) - five candidate direct signed pointwise theorem templates.
- `reports/figures/m38_surface_grouping_invariant_map.png` - 1620x864 grouping invariant classification map.
- `reports/figures/m38_grouping_beta_budget.png` - 1710x936 grouping beta-budget figure.
- `reports/figures/m38_grouping_vs_coefficient_variation_boundary.png` - 1584x864 direct-vs-coefficient-variation boundary figure.

### M39 Surface-Relation Kernel SPC Probe

- `docs/proof_ledger/surface_relation_kernel_spc_probe.md` (75 lines) - reconstructs Lemma 3.3 kernel closure and its path into evaluated quotient polynomials.
- `reports/extension_candidates/m39_surface_relation_kernel_spc_probe.md` (44 lines) - records the `kernel_spc_not_currently_theorem_ready` decision and pivot recommendation.
- `data/extension_candidates/m39_kernel_constraint_schema.csv` (6 lines) - five rows describing the kernel-closure flow.
- `data/extension_candidates/m39_kernel_spc_classification.csv` (11 lines) - ten kernel mechanism classification rows.
- `data/extension_candidates/m39_kernel_beta_budget.csv` (601 lines) - 600 beta-budget rows for candidate kernel scenarios.
- `data/extension_candidates/m39_kernel_pivot_decision.csv` (4 lines) - three pivot decision rows.
- `reports/figures/m39_kernel_constraint_flow.png` - 1800x900 kernel constraint flow figure.
- `reports/figures/m39_kernel_spc_decision_map.png` - 1800x864 kernel SPC decision map.
- `reports/figures/m39_kernel_beta_budget.png` - 1710x864 kernel beta-budget figure.

## Milestone State

- M1-M6: validated paper map, proof ledger, computational probes, formal certification, extension candidates, and final synthesis.
- M7-M15: validated product-ratio, quotient-family, aggregate-control, cancellation, external-decay, and Kim--Tao bridge-requirement branch.
- M16-M25: validated shrinking local-window branch; preserved as follow-up problem after support/localization obstructions.
- M26-M29: validated post-local prioritization, rigidity cluster/multiplicity bookkeeping, Theorem 2 `L^p`/mass corollaries, and fixed-cutoff pre-trace local mass corollary.
- M30: validated after classifier repair; Schreier trace-moment benchmark gives exact tree moments and reproducible variance evidence.
- M31: validated after all-pair class-order repair; paired-word variance mechanism supports the fixed-`k` variance theorem target.
- M32: validated after proof-harness wording repair; fixed-pair covariance lemma proves `Cov(Fix(u),Fix(v))=O_{u,v}(1)` for fixed nontrivial reduced words.
- M33: validated; Schreier benchmark branch is consolidated as a standalone theorem package with fixed-`k` expectation and `O_k(n^-2)` normalized variance.
- M34: validated after figure-link repair; Kim--Tao Theorem 1 gives fixed positive-width spectral-window count asymptotics with relative error `O(n^-alpha_W)`, but no variance or local-statistics claim.
- M35: validated after `Lambda0^20` repair; actual Corollary 3.4 numerator obstruction localized the `q^(2 kappa)` loss to Markov interpolation of `x^2 p(x)`.
- M36: validated; direct small-`x` evaluation of `p(1/n)/Q_id(1/n)` is a distinct conditional target only if a new surface-ratio estimate is proved.
- M37: validated; signed pointwise cancellation remains independent only as a surface-attached theorem at `x=1/n`; absolute fixed-stratum control collapses into coefficient variation.
- M38: validated; surface-native grouping was formulated, with surface-relation kernel grouping and length-shell transform phase surviving only as conditional `SPC_G(A,sigma)` theorem targets.
- M39: validated; Lemma 3.3 surface-relation kernel closure is paper-native but currently supplies admissibility/structure rather than evaluated sign-pairing, so kernel SPC is not theorem-ready.

## Cross-References

- M4 labelled-template identity -> M32 fixed-pair covariance: quotient templates contribute at exponent `V-C_a-C_b`; the M32 closed-walk constraint lemma bounds this exponent by `0`.
- M31 variance expansion -> M32 theorem consequence: fixed-pair `O(1)` covariance turns `n^{-2} sum Cov(Fix(u),Fix(v))` into fixed-`k` variance `O_k(n^-2)`.
- M30-M32 -> M33 package: expectation, tree-word separation, variance expansion, and fixed-pair covariance are consolidated into one theorem-grade Schreier benchmark.
- M16 endpoint subtraction -> M34 fixed windows: fixed `I=[a,b]` has main term `(2g-2)n(F(b)-F(a))` and inherited endpoint error `O(n^{1-alpha_W}b^{1/2+epsilon})`.
- M34 shrinking exclusions -> M16-M25: rows with `Delta=n^{-d}` return to the unresolved shrinking-window support/variance obstruction chain.
- M15/M22/M25 compact-support obstruction -> M35 actual numerator: M35 identifies the paper-defined ratio `p(1/n)/Q_id(1/n)` as the remaining surface object and locates the Markov loss.
- M35 numerator obstruction -> M36 direct target: M36 isolates the theorem target `|p(1/n)/Q_id(1/n)| <= C n Lambda0^20 ||htilde||^2 q^A n^(-sigma+o(1))`.
- M36 direct target -> M37 signed cancellation: M37 shows the direct route is independent only if the proof uses signed pointwise cancellation at `x=1/n`; absolute stratum bounds are coefficient-variation targets.
- M37 signed cancellation -> M38 grouping taxonomy: M38 turns the generic signed route into explicit candidate groupings by quotient profile, relation kernel, diagonal/off-diagonal class, primitive-power profile, and length-shell transform phase.
- M38 surface-relation kernel grouping -> M39 kernel probe: M39 tests the strongest paper-native grouping and finds that kernel closure does not currently provide evaluated `Q_i(1/n)` sign cancellation.

## Current Research Posture

The Schreier/random-permutation benchmark branch is now closed as a standalone finite-model theorem package. It proves fixed-`k` expectation and normalized trace variance for the two-permutation free-Schreier operator, but it does not transfer to Kim--Tao random hyperbolic covers without a new surface-group quotient-family theorem.

The direct Kim--Tao theorem-consequence pass now includes three surface-facing corollary packages after M25: rigidity cluster/multiplicity bookkeeping, Theorem 2 mass consequences, and fixed non-shrinking spectral-window counts. These are theorem-level corollaries or deterministic bounds, not new local spectral statistics.

The strongest open surface-facing direction has pivoted from direct signed pointwise cancellation to coefficient/signed variation for the actual denominator-normalized Corollary 3.4 value `p(1/n)/Q_id(1/n)`. M38 preserved surface-relation kernel grouping and length-shell transform phase as conditional direct templates, but M39 found the kernel route not currently theorem-ready. Length-shell transform phase remains secondary because transform signs are not relation-kernel signs.

The fixed-window M34 result should not be treated as evidence for variance asymptotics, limiting laws, level repulsion, local universality, or shrinking-window statistics. The M35-M39 compact-support work proves no exponent improvement; it only converts the remaining bottleneck into precise theorem targets, blocked-route classifications, and a pivot rule toward coefficient/signed variation.
