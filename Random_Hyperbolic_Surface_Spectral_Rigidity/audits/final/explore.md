# Final Audit Explore Inventory

- Stage: 1 of 16 (explore)
- Run id: `run-2026-05-15T153635Z`
- Generated: `2026-05-16T15:07:46Z`
- Working directory: `<workspace>`
- Plan file read: `plan_of_record.md` (176 lines)
- Ledger file read: `promise_ledger.jsonl` (150 lines, 150 parsed events, 0 parse errors)
- Reports read: 17 matching files
- Closure/SUPERSEDES docs read: 3 files
- Session/report index: `audits/final/audit_reports_index.md`

## Explore Gate State

- Critical path examined: yes; plan milestones M1-M38, full ledger events, matching reports, closure/supersession documents, and run-session index were inventoried.
- Findings classified: pending; explore does not append findings, but verification risks are flagged by status/confidence/evidence availability below.
- CRITICAL/MODERATE findings to act on: unknown until verify/test stages inspect evidence support; active terminal risks are explicitly queued.

## Status Distribution

| scope | status | count |
|---|---|---:|
| all ledger milestones | `validated` | 76 |
| plan milestones only | `validated` | 39 |

## Confidence Distribution

| confidence | count |
|---|---:|
| `high` | 74 |
| `medium` | 2 |

## Verification Slice Assignment

The seven verify passes should inspect these verdict-pending milestones in order. Each pass verifies evidence files exist and support the latest ledger claim; low/provisional events require subsequent re-verification checks.

### Stage 2 Verify Slice
- `M1-paper-map`
- `M16-local-spectral-window-corollaries`
- `M22-trace-corollary34-uniform-coefficient-variation-target`
- `M29-pretrace-local-mass-intermediate-from-theorem2-proof`
- `M35-surface-corollary34-numerator-obstruction`
- `M6-final-synthesis`
- `_plan/initial-campaign-map`
- `_plan/phase2-local-spectral-window-corollaries`
- `_plan/phase2-post-local-extension-reprioritization`
- `_plan/phase2-schreier-benchmark-theoremization`
- `_plan/phase2-surface-relation-kernel-spc-probe`

### Stage 3 Verify Slice
- `M10-restricted-quotient-aggregate`
- `M17-local-window-variance-input`
- `M23-localized-trace-numerator-quotient-family-model`
- `M3-computational-probes`
- `M36-direct-small-x-surface-numerator-target`
- `M7-product-ratio-bounds`
- `_plan/phase2-aggregate-obstruction`
- `_plan/phase2-local-window-route-synthesis`
- `_plan/phase2-pretrace-local-mass-intermediate`
- `_plan/phase2-schreier-fixed-pair-covariance-lemma`
- `_plan/phase2-test-function-localization-feasibility`

### Stage 4 Verify Slice
- `M11-trace-like-weighted-quotient-class`
- `M18-test-function-localization-feasibility`
- `M24-localized-transform-geodesic-weight-decay-obstruction`
- `M30-schreier-benchmark-theoremization`
- `M37-signed-pointwise-cancellation-surface-aggregate`
- `M8-quotient-family-bridge`
- `_plan/phase2-cancellation-mechanism-diagnostics`
- `_plan/phase2-local-window-variance-input`
- `_plan/phase2-product-ratio-bounds`
- `_plan/phase2-schreier-variance-mechanism`
- `_plan/phase2-theorem2-lp-mass-corollaries`

### Stage 5 Verify Slice
- `M12-restricted-aggregate-theorem-template`
- `M19-smoothed-window-paley-wiener-lemma`
- `M25-local-window-route-synthesis-and-branch-decision`
- `M31-schreier-variance-mechanism-theoremization`
- `M38-surface-native-grouping-problem`
- `M9-aggregate-product-ratio-obstruction`
- `_plan/phase2-direct-small-x-surface-numerator-target`
- `_plan/phase2-localized-trace-numerator-quotient-model`
- `_plan/phase2-quotient-family-bridge`
- `_plan/phase2-signed-pointwise-cancellation-surface-aggregate`
- `_plan/phase2-trace-corollary34-target`

### Stage 6 Verify Slice
- `M13-cancellation-mechanism-diagnostics`
- `M2-proof-ledger`
- `M26-post-local-extension-reprioritization`
- `M32-schreier-fixed-pair-covariance-lemma`
- `M39-surface-relation-kernel-spc-probe`
- `_archive/m3-probe-ladder-d2-source`
- `_plan/phase2-external-decay-thresholds`
- `_plan/phase2-localized-transform-weight-decay`
- `_plan/phase2-restricted-aggregate-theorem-template`
- `_plan/phase2-smoothed-window-paley-wiener-lemma`
- `_plan/phase2-trace-like-weighted-quotient-class`

### Stage 7 Verify Slice
- `M14-external-decay-thresholds`
- `M20-long-support-trace-variance-requirement`
- `M27-multiplicity-and-cluster-corollaries-from-rigidity`
- `M33-schreier-benchmark-package-synthesis`
- `M4-formal-certification`
- `_archive/markov-scaling-duplicate`
- `_plan/phase2-finite-nonshrinking-spectral-statistics`
- `_plan/phase2-long-support-trace-variance-requirement`
- `_plan/phase2-restricted-quotient-aggregate`
- `_plan/phase2-surface-corollary34-numerator-obstruction`
- `_plan/phase2-trace-side-long-support-template`

### Stage 8 Verify Slice
- `M15-kim-tao-bridge-requirement`
- `M21-trace-side-long-support-variance-template`
- `M28-theorem2-lp-mass-distribution-corollaries`
- `M34-finite-nonshrinking-spectral-statistics`
- `M5-extension-candidates`
- `_plan/domain-folders`
- `_plan/phase2-kim-tao-bridge-requirement`
- `_plan/phase2-multiplicity-cluster-corollaries`
- `_plan/phase2-schreier-benchmark-package-synthesis`
- `_plan/phase2-surface-native-grouping-problem`

## Milestone Inventory

| milestone_id | plan? | latest_status | confidence | cycle | ledger_line | latest evidence pointer | verdict_pending | latest narrative |
|---|---:|---|---|---:|---:|---|---:|---|
| `M1-paper-map` | yes | `validated` | `high` | 1 | 5 | `docs/paper_map/cycle1_foundational_map.md`, `docs/paper_map/cycle1_dependency_graph.dot`, `docs/paper_map/cycle1_dependency_graph.png` | yes | Created Cycle 1 foundational Kim--Tao paper map, dependency graph source/render, and open-question bottleneck ledger from local paper text. |
| `M2-proof-ledger` | yes | `validated` | `high` | 5 | 19 | `docs/proof_ledger/rigidity_proof_reconstruction.md`, `docs/proof_ledger/delocalization_proof_reconstruction.md`, `docs/proof_ledger/m2_loss_map.md` | yes | Auditor closes broad M2 proof-ledger narrowly for local proof reconstruction and quantitative dependency/loss accounting; downstream M3/M4/M5/M6 milestones remain pending. |
| `M3-computational-probes` | yes | `validated` | `high` | 11 | 27 | `reports/computational_probes/m3_computational_probe_synthesis.md`, `data/polynomial_method/m3_probe_artifact_index.csv`, `reports/figures/m3_probe_ladder_summary.png` | yes | Closed M3-computational-probes after five validated slices by synthesizing the fixed-point, folded quotient, labelled embedding, polynomial-window, and Schreier spectral probes. Th |
| `M4-formal-certification` | yes | `validated` | `high` | 12 | 29 | `scripts/certify_labelled_embedding_expectation.wls`, `scripts/certify_labelled_embedding_expectation.py`, `tests/test_labelled_embedding_expectation_identity.py` | yes | Opened M4 by certifying the exact falling-factorial expectation identity underlying the M3 labelled-embedding benchmark suite. The certification normalizes inverse-labelled edges b |
| `M5-extension-candidates` | yes | `validated` | `high` | 16 | 33 | `scripts/plot_m5_extension_synthesis.py`, `data/extension_candidates/m5_extension_synthesis_index.csv`, `data/extension_candidates/m5_log_coefficient_summary.csv` | yes | Cycle 16 synthesized the validated M5 evidence into a precise benchmark principle: fixed conflict-free labelled-template expectations are analytically tame after normalization, whi |
| `M6-final-synthesis` | yes | `validated` | `high` | 17 | 35 | `scripts/build_final_synthesis_index.py`, `data/final/final_artifact_index.csv`, `reports/final/final_file_map.md` ; missing refs: `reports/final/final_report.md` | yes | Post-closure M6 audit repair corrected reproducibility wording in the final report, final file map, audit packet, and final artifact-index manifest. The final package now states th |
| `M7-product-ratio-bounds` | yes | `validated` | `high` | 18 | 38 | `reports/extension_candidates/m7_product_ratio_coefficient_bounds.md`, `scripts/analyze_product_ratio_bounds.py`, `tests/test_product_ratio_bounds.py` | yes | M7 formalized the M5 toy product-ratio mechanism: linear-size supports with indices O(L) imply log coefficients O_r(L^{r+1}), ordinary coefficients O_k(L^{2k}) by the exponential p |
| `M8-quotient-family-bridge` | yes | `validated` | `high` | 19 | 42 | `reports/extension_candidates/m8_quotient_family_bridge.md`, `scripts/build_quotient_family_bridge_table.py`, `data/extension_candidates/quotient_family_bridge_table.csv` | yes | M8 remains validated after audit repair. The bridge is now stated as partial at the Kim--Tao probability-law level: M4 identifies the independent-permutation labelled-template skel |
| `M9-aggregate-product-ratio-obstruction` | yes | `validated` | `high` | 20 | 45 | `reports/extension_candidates/m9_aggregate_obstruction_and_enumeration.md`, `scripts/analyze_aggregate_product_ratio_obstruction.py`, `tests/test_aggregate_product_ratio_obstruction.py` | yes | M9 formalized the aggregate obstruction left by M8: M7 per-template product-ratio envelopes imply only a weighted-sum bound proportional to total variation. Deterministic examples  |
| `M10-restricted-quotient-aggregate` | yes | `validated` | `high` | 21 | 48 | `reports/extension_candidates/m10_restricted_quotient_aggregate.md`, `scripts/enumerate_restricted_quotient_aggregates.py`, `tests/test_restricted_quotient_aggregates.py` | yes | M10 tested a first explicit restricted aggregate model after M9. Folding collapses ordered reduced-word pairs but conflict-compatible canonical profiles still grow quickly through  |
| `M11-trace-like-weighted-quotient-class` | yes | `validated` | `high` | 22 | 52 | `reports/extension_candidates/m11_trace_like_weighted_quotient_class.md`, `scripts/enumerate_trace_like_weighted_quotients.py`, `tests/test_trace_like_weighted_quotients.py` | yes | M11 remains validated after audit repair. The repair changes the signed diagonal-subtracted total variation and pair/profile counts by removing the small diagonal/cyclic mass; the  |
| `M12-restricted-aggregate-theorem-template` | yes | `validated` | `high` | 23 | 55 | `reports/extension_candidates/m12_restricted_aggregate_theorem_template.md`, `scripts/analyze_restricted_aggregate_theorem_template.py`, `tests/test_restricted_aggregate_theorem_template.py` | yes | M12 formalized the conditional independent-permutation labelled-template aggregate theorem supported by M7/M9/M11. The result requires stratification by d = C - V: within each n_po |
| `M13-cancellation-mechanism-diagnostics` | yes | `validated` | `high` | 24 | 58 | `reports/extension_candidates/m13_cancellation_mechanism_diagnostics.md`, `scripts/analyze_cancellation_mechanisms.py`, `tests/test_cancellation_mechanisms.py` | yes | M13 shows that the M11 trace-like toy family does not provide a robust coefficient-cancellation mechanism for sharpening the M12 TV theorem. In the dominant unweighted d=1 rank-two |
| `M14-external-decay-thresholds` | yes | `validated` | `high` | 25 | 61 | `reports/extension_candidates/m14_external_decay_thresholds.md`, `scripts/model_external_decay_thresholds.py`, `tests/test_external_decay_thresholds.py` | yes | M14 quantifies the external decay needed after M13 ruled out robust cancellation. In the dominant unweighted d=1 rank-two remainder, no tested decay makes coefficient absolute vari |
| `M15-kim-tao-bridge-requirement` | yes | `validated` | `high` | 26 | 64 | `reports/extension_candidates/m15_kim_tao_bridge_requirement.md`, `docs/proof_ledger/conditional_decay_to_rigidity_improvement.md`, `scripts/test_selberg_weight_vs_template_growth.py` | yes | M15 converts the M12-M14 aggregate findings into a Kim--Tao-facing bridge requirement. The M12/M14 quantities attach conditionally to Corollary 3.4 and Proposition 4.2 as fixed-d w |
| `M16-local-spectral-window-corollaries` | yes | `validated` | `high` | 27 | 68 | `docs/proof_ledger/local_window_from_rigidity.md`, `reports/extension_candidates/m16_local_spectral_window_corollaries.md`, `scripts/analyze_local_window_thresholds.py` | yes | M16 remains validated after a scoped audit repair to the proof-ledger display formula. The correction changes only notation in docs/proof_ledger/local_window_from_rigidity.md and p |
| `M17-local-window-variance-input` | yes | `validated` | `high` | 28 | 71 | `docs/proof_ledger/local_window_variance_input.md`, `reports/extension_candidates/m17_local_window_variance_input.md`, `scripts/analyze_local_window_variance_requirements.py` | yes | M17 formulates the direct smoothed-window variance input needed to beat M16 endpoint subtraction. For Z_n(phi; Lambda, Delta), Chebyshev gives relative smoothed-window control when |
| `M18-test-function-localization-feasibility` | yes | `validated` | `high` | 29 | 75 | `docs/proof_ledger/test_function_localization_feasibility.md`, `reports/extension_candidates/m18_test_function_localization_feasibility.md`, `scripts/analyze_test_function_localization_tradeoffs.py` | yes | M18 remains validated after scoped audit repair. The main conclusion is unchanged: direct retuning of Kim--Tao's existing test functions does not supply the M17 local-window varian |
| `M19-smoothed-window-paley-wiener-lemma` | yes | `validated` | `high` | 30 | 78 | `docs/proof_ledger/smoothed_window_paley_wiener_obstruction.md`, `reports/extension_candidates/m19_smoothed_window_paley_wiener_lemma.md`, `scripts/analyze_smoothed_window_leakage.py` | yes | M19 records a negative obstruction for the logarithmic-support escape route after M18. For h_delta(r)=phi((r-r0)/delta), support truncation /t/<=R loses Fourier tail int_{/u/>R del |
| `M20-long-support-trace-variance-requirement` | yes | `validated` | `high` | 31 | 82 | `docs/proof_ledger/long_support_trace_variance_requirement.md`, `reports/extension_candidates/m20_long_support_trace_variance_requirement.md`, `scripts/analyze_long_support_variance_budget.py` | yes | M20 remains validated after scoped audit repair. The exponent-budget formulas and qualitative conclusion are unchanged: trace-side long-support local-window variance remains the on |
| `M21-trace-side-long-support-variance-template` | yes | `validated` | `high` | 32 | 85 | `docs/proof_ledger/trace_side_long_support_variance_template.md`, `reports/extension_candidates/m21_trace_side_long_support_variance_template.md`, `scripts/analyze_trace_variance_template_budget.py` | yes | M21 formulates the fixed-energy trace-side long-support variance theorem template. The centered statistic Z_n(h) is the spectral trace sum minus the Lemma 2.1 identity term, equiva |
| `M22-trace-corollary34-uniform-coefficient-variation-target` | yes | `validated` | `high` | 33 | 88 | `docs/proof_ledger/trace_corollary34_localized_numerator_target.md`, `reports/extension_candidates/m22_trace_corollary34_uniform_coefficient_variation_target.md`, `scripts/analyze_corollary34_target_budget.py` | yes | M22 isolates the fixed-bulk trace-side Corollary 3.4 numerator target upstream of M21. The localized numerator p_{Delta,q}(x) is Corollary 3.4 formula (3.18) with the M21 localized |
| `M23-localized-trace-numerator-quotient-family-model` | yes | `validated` | `high` | 34 | 91 | `docs/proof_ledger/localized_trace_numerator_quotient_family_model.md`, `reports/extension_candidates/m23_localized_trace_numerator_quotient_family_model.md`, `scripts/model_localized_trace_numerator_quotients.py` | yes | M23 models the fixed-bulk localized Corollary 3.4 numerator family as a stratum-preserving proxy anchored to the paper variables gamma_i, k_i, Selberg weights, localized transform  |
| `M24-localized-transform-geodesic-weight-decay-obstruction` | yes | `validated` | `high` | 35 | 95 | `docs/proof_ledger/localized_transform_geodesic_weight_decay.md`, `reports/extension_candidates/m24_localized_transform_geodesic_weight_decay_obstruction.md`, `scripts/analyze_localized_transform_weight_decay.py` | yes | M24 remains validated after scoped audit repair. The compact-support obstruction is unchanged: paper-compatible localized transform weights decay in u=t delta_r rather than t and d |
| `M25-local-window-route-synthesis-and-branch-decision` | yes | `validated` | `high` | 36 | 99 | `docs/proof_ledger/local_window_branch_decision_record.md`, `reports/extension_candidates/m25_local_window_route_synthesis_and_branch_decision.md`, `reports/final/local_window_followup_problem_statement.md` | yes | M25 remains validated after scoped audit repair. The local-window branch decision is still preserve_as_followup_problem: compact-support progress now requires actual surface-group  |
| `M26-post-local-extension-reprioritization` | yes | `validated` | `high` | 37 | 102 | `reports/extension_candidates/m26_post_local_extension_reprioritization.md`, `docs/proof_ledger/post_local_branch_attachment_points.md`, `reports/final/post_local_followup_ranked_problem_list.md` | yes | M26 re-ranks six post-local candidate branches after M25 preserved shrinking local windows as a follow-up problem. The unique recommended next milestone is M27-multiplicity-and-clu |
| `M27-multiplicity-and-cluster-corollaries-from-rigidity` | yes | `validated` | `high` | 38 | 106 | `scripts/analyze_multiplicity_cluster_bounds.py`, `tests/test_multiplicity_cluster_bounds.py`, `data/extension_candidates/m27_cluster_bound_grid.csv` | yes | M27 remains validated after scoped audit repair. The deterministic rigidity-to-cluster and multiplicity corollary is correct and useful as bookkeeping, but all generated classifica |
| `M28-theorem2-lp-mass-distribution-corollaries` | yes | `validated` | `high` | 39 | 110 | `scripts/analyze_theorem2_lp_mass_corollaries.py`, `tests/test_theorem2_lp_mass_corollaries.py`, `data/extension_candidates/m28_lp_bound_grid.csv` | yes | M28 remains validated after audit repair. The theorem-level Lp, small-set mass, and effective-support corollaries are correct; generated mass-grid rows now distinguish nontrivial_m |
| `M29-pretrace-local-mass-intermediate-from-theorem2-proof` | yes | `validated` | `high` | 40 | 113 | `docs/proof_ledger/pretrace_local_mass_intermediate.md`, `reports/extension_candidates/m29_pretrace_local_mass_intermediate.md`, `reports/final/pretrace_local_mass_followup_statement.md` | yes | M29 extracts a standalone fixed-cutoff/fiber local L2 mass corollary from Kim--Tao Theorem 2 proof before the final Sobolev conversion. The controlled object is the centered pre-tr |
| `M30-schreier-benchmark-theoremization` | yes | `validated` | `high` | 41 | 117 | `scripts/analyze_schreier_trace_benchmark.py`, `tests/test_schreier_trace_benchmark.py`, `data/extension_candidates/m30_schreier_tree_moments.csv` | yes | M30 remains validated after a scoped audit repair. The fixed-k expectation theorem template, exact tree moment regeneration through k=10, variance evidence, and scope firewall are  |
| `M31-schreier-variance-mechanism-theoremization` | yes | `validated` | `high` | 42 | 121 | `docs/proof_ledger/schreier_variance_mechanism.md`, `reports/extension_candidates/m31_schreier_variance_mechanism.md`, `scripts/analyze_schreier_variance_pair_templates.py` | yes | Audit repair closed a certification gap in the M31 pair-template analyzer: covariance-order class summaries are no longer backed by a hardcoded nonidentity O(1) shortcut, but by th |
| `M32-schreier-fixed-pair-covariance-lemma` | yes | `validated` | `high` | 43 | 125 | `docs/proof_ledger/schreier_fixed_pair_covariance_lemma.md`, `reports/extension_candidates/m32_schreier_fixed_pair_covariance_lemma.md`, `scripts/prove_schreier_fixed_pair_covariance.py` | yes | M32 remains validated after scoped audit repair. The fixed-pair covariance lemma and fixed-k Schreier variance theorem are sound within the independent two-permutation benchmark. T |
| `M33-schreier-benchmark-package-synthesis` | yes | `validated` | `high` | 44 | 130 | `docs/proof_ledger/schreier_benchmark_theorem_package.md`, `reports/extension_candidates/m33_schreier_benchmark_package_synthesis.md`, `reports/final/schreier_benchmark_theorem_package.md` | yes | M33 consolidates M30-M32 into a standalone two-permutation Schreier theorem package: fixed-k expectation m_k+O_k(n^-1), deterministic tree-word separation, fixed-pair covariance O_ |
| `M34-finite-nonshrinking-spectral-statistics` | yes | `validated` | `high` | 45 | 134 | `reports/extension_candidates/m34_finite_nonshrinking_spectral_statistics.md`, `docs/proof_ledger/finite_nonshrinking_spectral_statistics.md`, `scripts/analyze_finite_nonshrinking_spectral_statistics.py` | yes | M34 remains validated after scoped audit repair. Fixed positive-width windows give theorem-level endpoint-subtraction count asymptotics with relative error O(n^-alpha_W) up to fixe |
| `M35-surface-corollary34-numerator-obstruction` | yes | `validated` | `high` | 46 | 138 | `docs/proof_ledger/surface_corollary34_numerator_obstruction.md`, `reports/extension_candidates/m35_surface_corollary34_numerator_obstruction.md`, `scripts/analyze_surface_corollary34_numerator_obstruction.py` | yes | M35 remains validated after scoped audit repair. The mathematical decision is unchanged: direct small-x, coefficient-variation, signed-cancellation, and stronger Lemma 3.3 routes r |
| `M36-direct-small-x-surface-numerator-target` | yes | `validated` | `high` | 47 | 141 | `docs/proof_ledger/direct_small_x_surface_numerator_target.md`, `reports/extension_candidates/m36_direct_small_x_surface_numerator_target.md`, `scripts/analyze_direct_small_x_surface_numerator_target.py` | yes | M36 formulates the exact direct evaluation theorem target for the actual Kim--Tao Corollary 3.4 ratio p(1/n)/Q_id(1/n): /p(1/n)/Q_id(1/n)/ <= C n Lambda0^20 //htilde//^2 q^A n^(-si |
| `M37-signed-pointwise-cancellation-surface-aggregate` | yes | `validated` | `high` | 48 | 144 | `docs/proof_ledger/signed_pointwise_cancellation_surface_aggregate.md`, `reports/extension_candidates/m37_signed_pointwise_cancellation_surface_aggregate.md`, `scripts/analyze_signed_pointwise_cancellation_surface_aggregate.py` | yes | M37 reconstructs the signed summand structure of the actual Kim--Tao Corollary 3.4 ratio p(1/n)/Q_id(1/n) and classifies candidate signed cancellation mechanisms. Signed pointwise  |
| `M38-surface-native-grouping-problem` | yes | `validated` | `high` | 49 | 147 | `docs/proof_ledger/surface_native_grouping_problem.md`, `reports/extension_candidates/m38_surface_native_grouping_problem.md`, `scripts/analyze_surface_native_grouping_problem.py` | yes | M38 formulates the paper-native grouping problem for the actual Kim--Tao Corollary 3.4 ratio p(1/n)/Q_id(1/n). Surface-relation kernel grouping and length-shell transform-phase gro |
| `M39-surface-relation-kernel-spc-probe` | yes | `validated` | `high` | 50 | 150 | `docs/proof_ledger/surface_relation_kernel_spc_probe.md`, `reports/extension_candidates/m39_surface_relation_kernel_spc_probe.md`, `scripts/analyze_surface_relation_kernel_spc_probe.py` | yes | M39 reconstructs the Lemma 3.3 surface-relation kernel closure condition: folded quotients W_r must close every path spelling an element of ker(F_{2g}->Gamma), and this condition e |
| `_archive/m3-probe-ladder-d2-source` | no | `validated` | `high` | 11 | 28 | `reports/figures/stale/m3_probe_ladder_summary.d2` | yes | Moved the failed-render D2 source out of the active figure path so M3 closure artifacts remain traceable and canonical reproduction uses scripts/plot_m3_probe_ladder_summary.py. |
| `_archive/markov-scaling-duplicate` | no | `validated` | `high` | 3 | 11 | `scripts/data/polynomial_method/stale/markov_scaling_sanity.csv` | yes | Archived duplicate Markov scaling CSV generated by the figure harness from the scripts working directory; canonical data remains under data/polynomial_method. |
| `_plan/domain-folders` | no | `validated` | `medium` | 1 | 3 | `STRUCTURE.md` | yes | Workspace structure now names campaign-specific domain folders for the random hyperbolic surface rigidity run. |
| `_plan/initial-campaign-map` | no | `validated` | `medium` | 1 | 2 | `plan_of_record.md` | yes | Initial plan-of-record goals and milestones now cover paper map, proof reconstruction, computational probes, formal certification, extension search, and final synthesis. |
| `_plan/phase2-aggregate-obstruction` | no | `validated` | `high` | 20 | 43 | `plan_of_record.md` | yes | Opened Phase II M9 to formalize the aggregate obstruction left by M8: per-template product-ratio envelopes do not by themselves control weighted quotient-family sums. |
| `_plan/phase2-cancellation-mechanism-diagnostics` | no | `validated` | `high` | 24 | 56 | `plan_of_record.md` | yes | Opened Phase II M13 to diagnose whether the M12 stratified TV theorem can be sharpened by coefficient cancellation, structural grouping, rank-sensitive decay, or length-decay in th |
| `_plan/phase2-direct-small-x-surface-numerator-target` | no | `validated` | `high` | 47 | 139 | `plan_of_record.md` | yes | Opened Phase II M36 to attack the narrower direct small-x evaluation theorem target for p(1/n)/Q_id(1/n) before committing to a broader surface-group coefficient-variation theorem. |
| `_plan/phase2-external-decay-thresholds` | no | `validated` | `high` | 25 | 59 | `plan_of_record.md` | yes | Opened Phase II M14 to quantify the external rank, length, and folded-complexity decay needed after M13 ruled out robust coefficient cancellation in the restricted trace-like toy f |
| `_plan/phase2-finite-nonshrinking-spectral-statistics` | no | `validated` | `high` | 45 | 131 | `plan_of_record.md` | yes | Opened Phase II M34 to derive and classify fixed-energy non-shrinking spectral-window statistics from Kim--Tao rigidity and Weyl estimates, with explicit comparison to the M16 endp |
| `_plan/phase2-kim-tao-bridge-requirement` | no | `validated` | `high` | 26 | 62 | `plan_of_record.md` | yes | Opened Phase II M15 to convert M12-M14 aggregate-control and external-decay diagnostics into a Kim--Tao-facing bridge requirement for Proposition 3.1, Lemma 3.3, Corollary 3.4, and |
| `_plan/phase2-local-spectral-window-corollaries` | no | `validated` | `high` | 27 | 65 | `plan_of_record.md` | yes | Opened Phase II M16 to derive local and mesoscopic spectral-window corollaries from Kim--Tao Weyl-law and rigidity estimates after M15 showed diminishing returns for larger aggrega |
| `_plan/phase2-local-window-route-synthesis` | no | `validated` | `high` | 36 | 96 | `plan_of_record.md` | yes | Opened Phase II M25 to synthesize M16-M24 into a local-window route decision record and preserve the remaining compact and noncompact theorem targets as follow-up problems. |
| `_plan/phase2-local-window-variance-input` | no | `validated` | `high` | 28 | 69 | `plan_of_record.md` | yes | Opened Phase II M17 to formulate the direct smoothed-window variance input needed after M16 showed endpoint subtraction only controls windows above inherited global-error scales. |
| `_plan/phase2-localized-trace-numerator-quotient-model` | no | `validated` | `high` | 34 | 89 | `plan_of_record.md` | yes | Opened Phase II M23 to model the weighted quotient/template strata appearing in the localized Corollary 3.4 numerator after M22 isolated the numerator target. |
| `_plan/phase2-localized-transform-weight-decay` | no | `validated` | `high` | 35 | 92 | `plan_of_record.md` | yes | Opened Phase II M24 to determine whether localized transform and Selberg/geodesic weights inside the compact-support Paley-Wiener architecture can justify the optimistic M23 decay  |
| `_plan/phase2-long-support-trace-variance-requirement` | no | `validated` | `high` | 31 | 79 | `plan_of_record.md` | yes | Opened Phase II M20 to quantify the random-cover trace variance saving required if the M17 local-window route accepts polynomial geometric support after the M19 Fourier-scaling obs |
| `_plan/phase2-multiplicity-cluster-corollaries` | no | `validated` | `high` | 38 | 103 | `plan_of_record.md` | yes | Opened Phase II M27 to derive multiplicity and spectral-cluster corollaries directly from Kim--Tao Theorem 1 rigidity and the M2/M16 Weyl-density pipeline. |
| `_plan/phase2-post-local-extension-reprioritization` | no | `validated` | `high` | 37 | 100 | `plan_of_record.md` | yes | Opened Phase II M26 to re-rank post-local extension candidates after M25 preserved the shrinking local-window route as a follow-up problem. |
| `_plan/phase2-pretrace-local-mass-intermediate` | no | `validated` | `high` | 40 | 111 | `plan_of_record.md` | yes | Opened Phase II M29 to mine the pre-Sobolev local-mass intermediate inside Kim--Tao Theorem 2 proof after M28 advanced the direct delocalization consequence branch. |
| `_plan/phase2-product-ratio-bounds` | no | `validated` | `high` | 18 | 36 | `plan_of_record.md` | yes | Opened Phase II as a follow-up to the validated M5 toy mechanism: formal coefficient and derivative bounds for growing labelled-template product ratios. |
| `_plan/phase2-quotient-family-bridge` | no | `validated` | `high` | 19 | 39 | `plan_of_record.md` | yes | Opened Phase II M8 to bridge the validated M7 product-ratio lemma back to Kim--Tao quotient/profile families in the trace and pre-trace polynomialization steps. |
| `_plan/phase2-restricted-aggregate-theorem-template` | no | `validated` | `high` | 23 | 53 | `plan_of_record.md` | yes | Opened Phase II M12 to formalize the restricted aggregate theorem template supported by M7/M9/M11, with explicit stratification by n_power = C - V. |
| `_plan/phase2-restricted-quotient-aggregate` | no | `validated` | `high` | 21 | 46 | `plan_of_record.md` | yes | Opened Phase II M10 to test the first explicit restricted quotient-family aggregate model after the M9 obstruction. |
| `_plan/phase2-schreier-benchmark-package-synthesis` | no | `validated` | `high` | 44 | 126 | `plan_of_record.md` | yes | Opened Phase II M33 to consolidate the validated two-permutation Schreier benchmark results into a theorem-grade package with reproducible artifacts and an explicit no-transfer fir |
| `_plan/phase2-schreier-benchmark-theoremization` | no | `validated` | `high` | 41 | 114 | `plan_of_record.md` | yes | Opened Phase II M30 to theoremize the validated M3 Schreier/random-permutation trace-moment benchmark after M27-M29 exhausted immediate theorem-corollary mining. |
| `_plan/phase2-schreier-fixed-pair-covariance-lemma` | no | `validated` | `high` | 43 | 122 | `plan_of_record.md` | yes | Opened Phase II M32 to prove or sharply localize the arbitrary fixed-k reduced-word pair covariance exponent lemma for the two-permutation Schreier benchmark. |
| `_plan/phase2-schreier-variance-mechanism` | no | `validated` | `high` | 42 | 118 | `plan_of_record.md` | yes | Opened Phase II M31 to upgrade M30 Schreier benchmark variance evidence into a fixed-k paired-word covariance mechanism theorem template using the M4 labelled-template expectation  |
| `_plan/phase2-signed-pointwise-cancellation-surface-aggregate` | no | `validated` | `high` | 48 | 142 | `plan_of_record.md` | yes | Opened Phase II M37 to probe signed pointwise cancellation in the paper-defined Kim--Tao Corollary 3.4 denominator-normalized surface aggregate, while preserving the no-transfer fi |
| `_plan/phase2-smoothed-window-paley-wiener-lemma` | no | `validated` | `high` | 30 | 76 | `plan_of_record.md` | yes | Opened Phase II M19 to isolate the smoothed Paley-Wiener/window Fourier-scaling obstruction identified by M18, comparing logarithmic and polynomial geometric support against shrink |
| `_plan/phase2-surface-corollary34-numerator-obstruction` | no | `validated` | `high` | 46 | 135 | `plan_of_record.md` | yes | Opened Phase II M35 to analyze whether the actual surface-group quotient-polynomial numerator admits coefficient-variation or direct small-x control beyond the Markov interpolation |
| `_plan/phase2-surface-native-grouping-problem` | no | `validated` | `high` | 49 | 145 | `plan_of_record.md` | yes | Opened Phase II M38 to formulate the paper-native grouping problem for the evaluated Corollary 3.4 aggregate, comparing quotient complex, primitive-power structure, length shell, t |
| `_plan/phase2-surface-relation-kernel-spc-probe` | no | `validated` | `high` | 50 | 148 | `plan_of_record.md` | yes | Opened Phase II M39 to inspect the Lemma 3.3 folded-quotient kernel-closure constraint for F_{2g} -> Gamma and test whether it can support signed evaluated cancellation in the actu |
| `_plan/phase2-test-function-localization-feasibility` | no | `validated` | `high` | 29 | 72 | `plan_of_record.md` | yes | Opened Phase II M18 to map the M17 local-window variance target to Kim--Tao test-function localization, geometric support, polynomial degree, and Markov/interpolation costs. |
| `_plan/phase2-theorem2-lp-mass-corollaries` | no | `validated` | `high` | 39 | 107 | `plan_of_record.md` | yes | Opened Phase II M28 to derive Lp interpolation, small-set mass, and effective-support corollaries from Kim--Tao Theorem 2 eigenfunction delocalization after M27 remained bookkeepin |
| `_plan/phase2-trace-corollary34-target` | no | `validated` | `high` | 33 | 86 | `plan_of_record.md` | yes | Opened Phase II M22 to isolate the localized Corollary 3.4 numerator target upstream of the M21 trace-side long-support variance theorem, including coefficient-variation, direct sm |
| `_plan/phase2-trace-like-weighted-quotient-class` | no | `validated` | `high` | 22 | 49 | `plan_of_record.md` | yes | Opened Phase II M11 to test whether trace-like cyclic conjugacy quotienting, primitive/diagonal separation, and explicit length weights improve the M10 aggregate-control picture. |
| `_plan/phase2-trace-side-long-support-template` | no | `validated` | `high` | 32 | 83 | `plan_of_record.md` | yes | Opened Phase II M21 to formulate the trace-side fixed-energy long-support variance theorem template left by M20, including the exact centered statistic, support exponent q=n^eta, b |

## Active Or Risk-Flagged Items For Later Stages

### In Progress / Action Required / Reopened At Explore
- None found in latest milestone states.

### Low Or Provisional Terminal States
- None found in latest milestone states.

### Missing Evidence References In Latest Events
- `M6-final-synthesis`: missing latest-event references `reports/final/final_report.md`.

## Report Inventory
- `reports/cycles/report_cycles_1-3.md` (332 lines, 20099 chars)
- `reports/cycles/report_cycles_10-12.md` (358 lines, 23540 chars)
- `reports/cycles/report_cycles_13-15.md` (290 lines, 19860 chars)
- `reports/cycles/report_cycles_16-18.md` (271 lines, 18816 chars)
- `reports/cycles/report_cycles_19-21.md` (341 lines, 23576 chars)
- `reports/cycles/report_cycles_22-24.md` (429 lines, 30883 chars)
- `reports/cycles/report_cycles_25-27.md` (410 lines, 26438 chars)
- `reports/cycles/report_cycles_28-30.md` (365 lines, 19835 chars)
- `reports/cycles/report_cycles_31-33.md` (495 lines, 25681 chars)
- `reports/cycles/report_cycles_34-36.md` (406 lines, 25484 chars)
- `reports/cycles/report_cycles_37-39.md` (413 lines, 27396 chars)
- `reports/cycles/report_cycles_4-6.md` (277 lines, 18392 chars)
- `reports/cycles/report_cycles_40-42.md` (360 lines, 23172 chars)
- `reports/cycles/report_cycles_43-45.md` (462 lines, 22813 chars)
- `reports/cycles/report_cycles_46-48.md` (464 lines, 24748 chars)
- `reports/cycles/report_cycles_49-50.md` (360 lines, 19755 chars)
- `reports/cycles/report_cycles_7-9.md` (323 lines, 20209 chars)

## Closure / Supersession Document Inventory
- `docs/proof_ledger/m2_closure_dependency_graph.dot` (60 lines, 2472 chars)
- `docs/proof_ledger/m2_closure_dependency_graph.png` (3684 lines, 142808 chars)
- `docs/proof_ledger/m2_proof_ledger_closure.md` (39 lines, 4042 chars)

## Notes For Verify/Test Stages

- The plan of record contains milestones through `M38-surface-native-grouping-problem`; latest prompt ledger summary was truncated, so later stages must use the full local ledger over the prompt summary.
- Stage 1 did not append structured findings; findings should be appended only after evidence-support or adversarial checks produce classified defects.
- `audits/final/audit_reports_index.md` was written from the SQLite session catalog when possible, with report-file fallback if session rows were sparse.
