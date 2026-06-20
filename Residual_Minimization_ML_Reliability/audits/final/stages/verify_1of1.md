# Final Audit Verify Stage 1 of 1

Run id: `run-2026-05-14T030813Z`
Stage: 2 of 4, verify
Expected file: `<run-workspace>/audits/final/stages/verify_1of1.md`

## Scope

This pass verified all plan milestones assigned by `audits/final/explore.md`: M-1 through M-12. It checked latest ledger status, artifact existence, and whether the evidence supports the terminal claim. It also checked the special cases identified during explore: M-2, M-4, deferred catalogue entries CAT-18/CAT-20, and recurring validator warnings.

## Milestone Findings

| Milestone | Ledger / audit status | Confidence | Evidence checked | Verify result |
|---|---:|---:|---|---|
| M-1 | validated | high | `residual-certificates/candidate_triage.md`, `residual-certificates/top_candidate_proof_sketch.md`, `scripts/triage_residual_sequences.py`, `tests/test_triage_scaling.py`, `data/triage_residual_scaling.csv`, `data/triage_residual_scaling.png`, `data/triage_bad_sequence_profiles.png` | Supported. Candidate triage and definitions exist with ranked mechanisms, explicit objectives/templates, scaling artifacts, and tests. |
| M-2 | not-started | provisional | `residual-certificates/deferred_branches.md`, `residual-certificates/broad_synthesis_package.md`, `reports/residual_minimization_reliability_final_report.md` | Residual debt, not a failed validation. There is no direct M-2 ledger event. Later package files explicitly say M-2 is not separately validated and is only partly represented by weak-topology and trace-leakage results. |
| M-3 | validated | high | `residual-certificates/collocation_blind_spot_theorem.md`, `residual-certificates/collocation_publishability_note.md`, `scripts/collocation_certificate_scaling.py`, `tests/test_collocation_certificate.py`, `data/collocation_certificate_scaling.csv`, `data/collocation_certificate_scaling.png`, `data/collocation_certificate_profiles.png` | Supported. The collocation blind-spot theorem, certificate scaling data, figures, and tests exist. |
| M-4 | not-started | provisional | `residual-certificates/deferred_branches.md`, `residual-certificates/admissibility_invariant_branch.md`, `residual-certificates/broad_synthesis_package.md`, `reports/residual_minimization_reliability_final_report.md` | Residual debt, not a failed validation. There is no direct M-4 ledger event. Later files preserve the limit: M-4 is partly absorbed by Burgers/admissibility analysis but no full shock-selection simulation campaign was completed. |
| M-5 | validated | high | `reports/final/reproducibility_manifest.md`, `reports/final/figure_manifest.md`, `scripts/run_final_checks.sh`, M-1/M-3 CSV and PNG artifacts | Supported. Reproducibility manifests and referenced data/figure artifacts exist. The validation claim is narrower than the later broad toy suite, covering the early collocation package. |
| M-6 | validated | high | `REFERENCES.md`, `residual-certificates/deferred_branches.md`, `residual-certificates/collocation_blind_spot_theorem.md`, `residual-certificates/collocation_publishability_note.md`, final package reports | Partly supported with a broken evidence pointer. The scientific claim is preserved by later reports, but the M-6 latest ledger event still references missing `reports/final/final_report.md`. See finding `FA-V1-001`. |
| M-7 | validated | high | `residual-certificates/residual_case_catalogue.md`, `residual-certificates/application_risk_map.md`, `residual-certificates/toy_simulation_plan.md` | Supported. The catalogue contains 22 attempted mechanisms and the application map links the catalogue to scientific-ML motifs with evidence-strength labels. |
| M-8 | validated | high | `residual-certificates/weak_topology_branch.md`, weak-norm scripts, CSV/PNG data, tests, catalogue updates | Supported. The branch analyzes at least three weak/topology candidates, separates failures from stability baselines, and has supporting data/tests. |
| M-9 | validated | high | `residual-certificates/admissibility_invariant_branch.md`, `scripts/positivity_mass_toy.py`, `data/positivity_mass_toy.csv`, `data/positivity_mass_toy.png`, `tests/test_positivity_mass_toy.py` | Supported. The branch covers entropy/admissibility/invariant constraints and includes a positivity/mass toy with data, figure, and test. |
| M-10 | validated | high | `residual-certificates/ode_reliability_branch.md`, hidden-mode, Lyapunov, and inverse-identifiability scripts/data/figures/tests | Supported. The branch triages ODE reliability mechanisms and includes explicit bad families plus tested toy artifacts. |
| M-11 | validated | high | `residual-certificates/toy_simulation_results.md`, CAT-01/CAT-02/CAT-06/CAT-07/CAT-11/CAT-15 scripts, CSVs, PNGs, focused tests | Supported. At least six documented toy simulations exist, and the broader results note lists ten simulations or variants after later branches. |
| M-12 | validated | high | `residual-certificates/broad_synthesis_package.md`, catalogue, application map, toy results, weak/admissibility/ODE branch reports | Supported. The synthesis integrates the catalogue, application map, toy suite, certificates/corrections, stability baselines, and limitations. It explicitly does not mark M-2/M-4 as standalone validated. |

## Non-Plan Items Checked

| Item | Status | Verify result |
|---|---:|---|
| `_run/final-delivery-ready` | validated/high | Supported by `reports/residual_minimization_reliability_final_report.md`. The report is an index over validated artifacts and preserves limitations for M-2, M-4, CAT-18, and CAT-20. |
| `_manager/validator-warnings` | in-progress/medium | Not a terminal scientific claim. The final report identifies these as historical or pre-existing warnings; the adversarial test stage must run the validators and classify current impact. |
| `_plan/broaden-catalogue-scope` | validated/high | Supported by the plan change and later broad catalogue artifacts. |

## Structured Findings Appended

1. `FA-V1-001` — MODERATE — M-6 latest validated ledger event references `reports/final/final_report.md`, which is absent on disk. Later reports and artifacts support the M-6 scientific claim, so this is evidence-traceability debt rather than a scientific invalidation.

## Residual Debt To Carry Forward

- M-2: `not-started` / `provisional`; no standalone continuous norm-mismatch theorem was validated. Later package files disclose this.
- M-4: `not-started` / `provisional`; no standalone conservation-law or shock-selection campaign was completed. Later package files disclose this.
- CAT-18 and CAT-20: deferred catalogue/application-map entries; not terminal validated claims.
- `_manager/validator-warnings`: current validator impact must be tested in stage 3.

## Gate Check

- Evidence files for each validated milestone exist and support the claim: yes, except the broken historical M-6 pointer recorded in `FA-V1-001`.
- Low/provisional terminal states checked: yes. M-2 and M-4 are not terminal validations; they remain disclosed residual debt.
- Structured findings appended: yes, one MODERATE finding.
