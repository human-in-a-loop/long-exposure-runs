# Project Manifest

## Key Files

The following workspace files produced results cited in
final_report.md. Downstream packaging should include
these; other files are supporting or exploratory.

- `residual-certificates/residual_case_catalogue.md` — Catalogue breadth, mechanism statuses, objectives, bad families, and certificates cited in "Breadth Of The Catalogue" and "Mechanism Taxonomy".
- `residual-certificates/application_risk_map.md` — Application-domain mapping cited in "Application Risk Map".
- `residual-certificates/broad_synthesis_package.md` — Breadth counts, mechanism taxonomy, synthesis framing, validation state, and limitations used throughout the report.
- `residual-certificates/collocation_blind_spot_theorem.md` — CAT-01 fixed-collocation theorem and continuous/fill-distance certificates cited in "Representative Theorem-Quality Cases And Obstructions".
- `residual-certificates/weak_topology_branch.md` — CAT-06 weak-topology failures and matched elliptic stability baseline cited in the weak-norm sections.
- `residual-certificates/admissibility_invariant_branch.md` — Burgers entropy, positivity/mass, and maximum-principle results cited in admissibility and invariant sections.
- `residual-certificates/ode_reliability_branch.md` — Hidden-mode, stiff-ODE baseline, Lyapunov mismatch, and inverse ODE non-identifiability results cited in ODE reliability sections.
- `residual-certificates/toy_simulation_results.md` — Toy-suite measurements and artifact map cited in "Toy Simulation Suite".
- `scripts/collocation_certificate_scaling.py` — Reproducible CAT-01 fixed-collocation toy cited in the toy suite.
- `scripts/trace_leakage_toy.py` — Reproducible CAT-02 trace-leakage toy cited in the toy suite.
- `scripts/weak_norm_high_frequency_toy.py` — Reproducible CAT-06 high-frequency weak-norm toy cited in the toy suite.
- `scripts/weak_norm_localized_defect.py` — Reproducible localized weak-defect toy cited in the toy suite.
- `scripts/quadrature_aliasing_toy.py` — Reproducible CAT-07 quadrature-aliasing toy cited in the toy suite.
- `scripts/hidden_mode_observability_toy.py` — Reproducible CAT-11 hidden-mode observability toy cited in the toy suite.
- `scripts/positivity_mass_toy.py` — Reproducible CAT-12/CAT-13 positivity and mass-admissibility toy cited in the toy suite.
- `scripts/lyapunov_stability_mismatch_toy.py` — Reproducible CAT-14 deployment-region Lyapunov toy cited in the toy suite.
- `scripts/eigenmode_normalization_toy.py` — Reproducible CAT-15 eigenmode-normalization toy cited in the toy suite.
- `scripts/ode_parameter_nonidentifiability_toy.py` — Reproducible CAT-17 inverse ODE identifiability toy cited in the toy suite.
- `tests/test_collocation_certificate.py` — Focused validation for CAT-01 sampled loss, physical error, and certificate behavior cited in the appendix.
- `tests/test_triage_scaling.py` — Focused validation for CAT-01 triage scaling cited in the appendix.
- `tests/test_trace_leakage_toy.py` — Focused validation for CAT-02 trace leakage cited in the appendix.
- `tests/test_weak_norm_high_frequency_toy.py` — Focused validation for CAT-06 weak-norm decay and matched-control behavior cited in the appendix.
- `tests/test_weak_norm_localized_defect.py` — Focused validation for localized weak-defect scaling cited in the appendix.
- `tests/test_quadrature_aliasing_toy.py` — Focused validation for CAT-07 quadrature aliasing cited in the appendix.
- `tests/test_hidden_mode_observability_toy.py` — Focused validation for CAT-11 hidden-mode observability cited in the appendix.
- `tests/test_positivity_mass_toy.py` — Focused validation for CAT-12/CAT-13 positivity and mass separation cited in the appendix.
- `tests/test_lyapunov_stability_mismatch_toy.py` — Focused validation for CAT-14 deployment and Lyapunov behavior cited in the appendix.
- `tests/test_eigenmode_normalization_toy.py` — Focused validation for CAT-15 eigenmode normalization cited in the appendix.
- `tests/test_ode_parameter_nonidentifiability_toy.py` — Focused validation for CAT-17 Fisher-information correction cited in the appendix.
- `data/collocation_certificate_scaling.csv` — CAT-01 measured scaling data cited in the toy suite.
- `data/collocation_certificate_scaling.png` — CAT-01 scaling figure cited in the toy suite.
- `data/collocation_certificate_profiles.png` — CAT-01 profile figure cited in the toy suite.
- `data/trace_leakage_scaling.csv` — CAT-02 trace-leakage scaling data cited in the toy suite.
- `data/trace_leakage_scaling.png` — CAT-02 trace-leakage figure cited in the toy suite.
- `data/weak_norm_scaling.csv` — CAT-06 high-frequency weak-norm data cited in the toy suite.
- `data/weak_norm_scaling.png` — CAT-06 high-frequency weak-norm figure cited in the toy suite.
- `data/weak_norm_localized_defect.csv` — Localized weak-defect data cited in the toy suite.
- `data/weak_norm_localized_defect.png` — Localized weak-defect figure cited in the toy suite.
- `data/quadrature_aliasing.csv` — CAT-07 quadrature-aliasing data cited in the toy suite.
- `data/quadrature_aliasing.png` — CAT-07 quadrature-aliasing figure cited in the toy suite.
- `data/hidden_mode_observability.csv` — CAT-11 hidden-mode data cited in the toy suite.
- `data/hidden_mode_observability.png` — CAT-11 hidden-mode figure cited in the toy suite.
- `data/positivity_mass_toy.csv` — CAT-12/CAT-13 positivity and mass data cited in the toy suite.
- `data/positivity_mass_toy.png` — CAT-12/CAT-13 positivity and mass figure cited in the toy suite.
- `data/lyapunov_stability_mismatch.csv` — CAT-14 Lyapunov mismatch data cited in the toy suite.
- `data/lyapunov_stability_mismatch.png` — CAT-14 Lyapunov mismatch figure cited in the toy suite.
- `data/eigenmode_normalization.csv` — CAT-15 eigenmode-normalization data cited in the toy suite.
- `data/eigenmode_normalization.png` — CAT-15 eigenmode-normalization figure cited in the toy suite.
- `data/ode_parameter_nonidentifiability.csv` — CAT-17 inverse ODE identifiability data cited in the toy suite.
- `data/ode_parameter_nonidentifiability.png` — CAT-17 inverse ODE identifiability figure cited in the toy suite.
- `REFERENCES.md` — Numbered bibliography reproduced in "References".

## Script Inventory

### scripts/

- `scripts/triage_residual_sequences.py` — 133 lines — Generates the CAT-01 triage scaling CSV and profile figures.
- `scripts/collocation_certificate_scaling.py` — 174 lines — Regenerates the validated CAT-01 fixed-collocation certificate data and figures.
- `scripts/trace_leakage_toy.py` — 115 lines — Generates the CAT-02 trace-leakage scaling CSV and figure.
- `scripts/weak_norm_high_frequency_toy.py` — 113 lines — Generates the CAT-06 high-frequency weak-norm topology-mismatch CSV and figure, including a matched elliptic negative control.
- `scripts/weak_norm_localized_defect.py` — 138 lines — Generates the M-8 localized mean-zero defect scaling CSV and figure.
- `scripts/hidden_mode_observability_toy.py` — 98 lines — Generates the CAT-11 partial-observation hidden-mode CSV and figure.
- `scripts/quadrature_aliasing_toy.py` — 113 lines — Generates the CAT-07 Gauss quadrature aliasing CSV and figure.
- `scripts/eigenmode_normalization_toy.py` — 96 lines — Generates the CAT-15 eigenmode normalization CSV and figure.
- `scripts/positivity_mass_toy.py` — 122 lines — Generates the M-9 aggregate-mass versus positivity-certificate CSV and figure.
- `scripts/lyapunov_stability_mismatch_toy.py` — 115 lines — Generates the CAT-14 equilibrium-training versus deployment-stability CSV and figure.
- `scripts/ode_parameter_nonidentifiability_toy.py` — 109 lines — Generates the CAT-17 zero-excitation parameter non-identifiability CSV and figure.
- `scripts/run_final_checks.sh` — 15 lines — Regenerates the earlier CAT-01 data/figures and runs the focused legacy final checks.

### tests/

- `tests/test_triage_scaling.py` — 54 lines — Checks CAT-01 triage CSV behavior and certificate/control scaling.
- `tests/test_collocation_certificate.py` — 72 lines — Checks CAT-01 sampled loss, physical error, and certificate bounds.
- `tests/test_trace_leakage_toy.py` — 45 lines — Checks CAT-02 decaying trace objective, nondecaying physical error, and fixed trace certificate.
- `tests/test_weak_norm_high_frequency_toy.py` — 54 lines — Checks CAT-06 weak-norm decay, fixed L2 error, and matched elliptic negative control.
- `tests/test_weak_norm_localized_defect.py` — 44 lines — Checks M-8 localized-defect weak-norm decay, fixed L2 scale, suppressed mean mode, and local certificate.
- `tests/test_hidden_mode_observability_toy.py` — 45 lines — Checks CAT-11 observed residual blindness and full-state/observability certificates.
- `tests/test_quadrature_aliasing_toy.py` — 46 lines — Checks CAT-07 zero Gauss-node objective, exact residual norm, and endpoint penalties.
- `tests/test_eigenmode_normalization_toy.py` — 50 lines — Checks CAT-15 zero eigen-residual across amplitudes and normalization detection.
- `tests/test_positivity_mass_toy.py` — 52 lines — Checks M-9 aggregate residual blindness, positivity-certificate separation, and boundary-state coverage.
- `tests/test_lyapunov_stability_mismatch_toy.py` — 46 lines — Checks CAT-14 zero equilibrium residual, deployment error, and Lyapunov derivative sign.
- `tests/test_ode_parameter_nonidentifiability_toy.py` — 46 lines — Checks CAT-17 zero-excitation residual blindness and Fisher-information correction.

### residual-certificates/

- `residual-certificates/residual_case_catalogue.md` — 111 lines — Catalogue of 22 residual-minimization mechanisms with objectives, bad families, certificates, application relevance, and status.
- `residual-certificates/application_risk_map.md` — 70 lines — Maps CAT entries to scientific-ML application motifs and evidence strength.
- `residual-certificates/broad_synthesis_package.md` — 120 lines — Validated M-12 synthesis with breadth counts, mechanism taxonomy, closure table, toy-suite table, and limitations.
- `residual-certificates/toy_simulation_plan.md` — 37 lines — Plans the initial five-toy suite and backup simulations.
- `residual-certificates/toy_simulation_results.md` — 161 lines — Summarizes completed toy results across CAT-02, CAT-06, WT-2, CAT-07, CAT-11, CAT-12/CAT-13, CAT-14, CAT-15, and CAT-17.
- `residual-certificates/admissibility_invariant_branch.md` — 79 lines — M-9 branch note on Burgers entropy nonselection, positivity/mass admissibility, and maximum-principle baseline.
- `residual-certificates/weak_topology_branch.md` — 45 lines — M-8 branch note on oscillatory weak topology, localized concentration defects, and matched elliptic stability.
- `residual-certificates/ode_reliability_branch.md` — 59 lines — M-10 branch note on hidden modes, stiffness baseline, Lyapunov deployment mismatch, inverse non-identifiability, and admissibility links.
- `residual-certificates/collocation_blind_spot_theorem.md` — 154 lines — States and proves the prior validated CAT-01 fixed-collocation theorem and certificates.
- `residual-certificates/candidate_triage.md` — 35 lines — Earlier triage table for initial candidate residual-failure mechanisms.
- `residual-certificates/top_candidate_proof_sketch.md` — 77 lines — Earlier theorem-shaped proof sketch for CAT-01.
- `residual-certificates/collocation_publishability_note.md` — 29 lines — Positions CAT-01 against PINN-style collocation and classical numerical analysis.
- `residual-certificates/deferred_branches.md` — 21 lines — Earlier deferral note for continuous norm mismatch and entropy-selection branches.

### reports/

- `reports/residual_minimization_reliability_final_report.md` — 89 lines — Validated reader-facing final report indexing the catalogue, synthesis, toy evidence, certificates, reproducibility path, and limitations.
- `reports/final/reproducibility_manifest.md` — 45 lines — Legacy reproducibility manifest for the earlier fixed-collocation package.
- `reports/final/figure_manifest.md` — 41 lines — Legacy figure manifest for the earlier fixed-collocation package.
- `reports/cycles/report_cycles_1-3.md` — 289 lines — Historical cycle report for initial triage, fixed-collocation theorem work, and early toy planning.
- `reports/cycles/report_cycles_1-3.pdf` — rendered historical cycle report.
- `reports/cycles/report_cycles_4-6.md` — 225 lines — Cycle report for M-8, M-9, and M-10 branch closures.
- `reports/cycles/report_cycles_7-9.md` — 281 lines — Cycle report for M-12 synthesis, final-delivery packaging, and closure pivot.
- `reports/cycles/report_cycles_7-9.pdf` — rendered cycle 7-9 report.
- `reports/cycles/report_cycles_10-12.md` — 186 lines — Cycle report for repeated closure confirmation and handoff pivot.
- `reports/cycles/report_cycles_10-12.pdf` — rendered cycle 10-12 report.
- `reports/cycles/report_cycles_13-15.md` — 178 lines — Cycle report for continued procedural closure confirmation and handoff pivot.
- `reports/cycles/report_cycles_13-15.pdf` — rendered cycle 13-15 report.

### root

- `REFERENCES.md` — 11 lines — Global numbered bibliography.
- `promise_ledger.jsonl` — 48 lines — Milestone and auditor validation ledger.

## Cumulative Stats

- Total tracked scripts/check scripts: 12 files, 1341 lines.
- Total tracked tests: 11 files, 554 lines.
- Total tracked residual-certificate notes: 13 files, 998 lines.
- Total tracked final/report/cycle-report manifest files: 8 files, 1334 lines.
- Total tracked root reference/ledger files: 2 files, 59 lines.
- Total tracked code/test/proof/report/reference/ledger files in this manifest: 46 files, 4286 lines.
- Sub-topics represented: CAT-01 fixed finite-collocation blind spot; M-7 broad catalogue and application map; M-8 weak topology; M-9 admissibility/invariant certificates; M-10 ODE reliability; M-11 toy suite; M-12 broad synthesis; final-delivery packaging; CAT-02 trace leakage; CAT-06 weak-norm mismatch; CAT-07 quadrature aliasing; CAT-11 hidden observability; CAT-12/CAT-13 positivity and mass; CAT-14 Lyapunov deployment mismatch; CAT-15 eigenmode normalization; CAT-17 inverse non-identifiability.
- Open or deferred areas: M-2 and M-4 remain pending / partly absorbed; CAT-18 and CAT-20 remain deferred. These are documented limitations, not blockers for the validated package.

## Cross-References

- `residual-certificates/residual_case_catalogue.md` -> `residual-certificates/application_risk_map.md` -> `residual-certificates/toy_simulation_plan.md` defines the M-7 catalogue, application mapping, and toy-suite plan.
- `residual-certificates/broad_synthesis_package.md` integrates the validated catalogue, application map, branch notes, toy evidence, stability baselines, and limitations for M-12.
- `reports/residual_minimization_reliability_final_report.md` indexes the validated synthesis package for human use and gives the final reproducibility path.
- `scripts/collocation_certificate_scaling.py` -> `data/collocation_certificate_scaling.csv/png` and `data/collocation_certificate_profiles.png` -> `residual-certificates/collocation_blind_spot_theorem.md` supplies CAT-01.
- `scripts/trace_leakage_toy.py` -> `data/trace_leakage_scaling.csv/png` -> `tests/test_trace_leakage_toy.py` -> `residual-certificates/toy_simulation_results.md` supplies CAT-02.
- `scripts/weak_norm_high_frequency_toy.py` -> `data/weak_norm_scaling.csv/png` -> `tests/test_weak_norm_high_frequency_toy.py` -> `residual-certificates/weak_topology_branch.md` supplies CAT-06 / WT-1.
- `scripts/weak_norm_localized_defect.py` -> `data/weak_norm_localized_defect.csv/png` -> `tests/test_weak_norm_localized_defect.py` -> `residual-certificates/weak_topology_branch.md` supplies M-8 / WT-2.
- `scripts/hidden_mode_observability_toy.py` -> `data/hidden_mode_observability.csv/png` -> `tests/test_hidden_mode_observability_toy.py` -> `residual-certificates/ode_reliability_branch.md` supplies CAT-11.
- `scripts/quadrature_aliasing_toy.py` -> `data/quadrature_aliasing.csv/png` -> `tests/test_quadrature_aliasing_toy.py` -> `residual-certificates/toy_simulation_results.md` supplies CAT-07.
- `scripts/eigenmode_normalization_toy.py` -> `data/eigenmode_normalization.csv/png` -> `tests/test_eigenmode_normalization_toy.py` -> `residual-certificates/toy_simulation_results.md` supplies CAT-15.
- `scripts/positivity_mass_toy.py` -> `data/positivity_mass_toy.csv/png` -> `tests/test_positivity_mass_toy.py` -> `residual-certificates/admissibility_invariant_branch.md` supplies M-9 / CAT-12/CAT-13.
- `scripts/lyapunov_stability_mismatch_toy.py` -> `data/lyapunov_stability_mismatch.csv/png` -> `tests/test_lyapunov_stability_mismatch_toy.py` -> `residual-certificates/ode_reliability_branch.md` supplies M-10 / CAT-14.
- `scripts/ode_parameter_nonidentifiability_toy.py` -> `data/ode_parameter_nonidentifiability.csv/png` -> `tests/test_ode_parameter_nonidentifiability_toy.py` -> `residual-certificates/ode_reliability_branch.md` supplies M-10 / CAT-17.
- `promise_ledger.jsonl` records M-12 validated at `2026-05-14T17:11:00Z` and `_run/final-delivery-ready` validated at `2026-05-14T17:31:00Z`.
- `REFERENCES.md` provides citation numbering for cycle and synthesis reports.
