---
created: 2026-05-14T17:25:00Z
cycle: 56
run_id: run-2026-05-14T030813Z
agent: worker
milestone: final-delivery-report
---

# Residual Minimization And Scientific ML Reliability

## Final Thesis

Residual losses are certificates only when they are coercive for the physical behavior being claimed. The validated package shows explicit ODE, PDE, collocation, quadrature, weak-topology, admissibility, observability, inverse-problem, and surrogate-support settings where the stated residual loss vanishes or becomes misleading while the target norm, observable, admissibility condition, parameter, or deployment behavior remains wrong. It also records stability baselines where matched continuous residuals, exact traces, admissibility principles, or randomized sampling qualifications prevent the proposed failure, so the result is not a generic claim that PINNs, neural operators, or residual methods fail.

## Validated Artifact Inventory

| Artifact | Role in the final package |
|---|---|
| `residual-certificates/broad_synthesis_package.md` | Main validated synthesis: thesis, definitions, breadth counts, mechanism taxonomy, closure table, toy-suite table, limitations, and stability baselines. |
| `residual-certificates/residual_case_catalogue.md` | Ranked catalogue of CAT-01 through CAT-22 with objective, bad family or obstruction, loss behavior, physical error, certificate, application motif, and status. |
| `residual-certificates/application_risk_map.md` | Structural map from mechanisms to application motifs, with evidence-strength labels and explicit non-production-claim framing. |
| `residual-certificates/toy_simulation_results.md` | Reader-facing summary of the completed toy simulations, including scripts, data, figures, tests, and measured contrasts. |
| `residual-certificates/collocation_blind_spot_theorem.md` | Validated fixed finite-collocation theorem and certificate package for CAT-01. |
| `residual-certificates/weak_topology_branch.md` | Validated M-8 branch separating direct weak-topology failures from matched elliptic stability baselines. |
| `residual-certificates/admissibility_invariant_branch.md` | Validated M-9 branch for entropy/admissibility, positivity/simplex constraints, and maximum-principle baselines. |
| `residual-certificates/ode_reliability_branch.md` | Validated M-10 branch for hidden modes, Lyapunov deployment mismatch, inverse non-identifiability, and stiff ODE stability baseline. |

## Evidence Table

| Mechanism class | Representative IDs | Failure or baseline | Certificate or correction | Toy/proof artifact |
|---|---|---|---|---|
| Fixed finite collocation noncoercivity | CAT-01, CAT-03, CAT-08, CAT-22 | Failure for fixed finite samples; randomized sampling is a qualification, not the same theorem. | Continuous residual norm, fill-distance plus regularity, trace/mean constraints, randomized coverage bounds. | `residual-certificates/collocation_blind_spot_theorem.md`; `data/collocation_certificate_scaling.csv`; `data/collocation_certificate_scaling.png` |
| Trace or boundary penalty leakage | CAT-02 | Failure when trace information is absent or asymptotically unweighted. | Fixed positive trace penalty and FTC/Poincare estimate. | `scripts/trace_leakage_toy.py`; `data/trace_leakage_scaling.csv`; `data/trace_leakage_scaling.png` |
| Weak topology mismatch | CAT-06 | Failure when a direct weak objective is used to certify strong physical accuracy. | Stronger norm, compactness/regularity, bandwidth control, local certificates. | `residual-certificates/weak_topology_branch.md`; `data/weak_norm_scaling.csv`; `data/weak_norm_localized_defect.csv` |
| Matched elliptic residual | CAT-04 | Stability baseline: matched \(H^{-1}\) residual plus exact trace controls \(H^1_0\) error. | Energy estimate / Lax-Milgram coercivity. | `residual-certificates/weak_topology_branch.md` |
| Quadrature and discretization aliasing | CAT-07, CAT-16 | Failure when numerical quadrature is blind to a represented residual. | Exact integration, overintegration, anti-aliasing, independent validation nodes. | `scripts/quadrature_aliasing_toy.py`; `data/quadrature_aliasing.csv`; `data/quadrature_aliasing.png` |
| Conservation-law admissibility | CAT-09, CAT-10 | Failure when weak residual certifies a weak solution but not the entropy solution. | Kruzhkov/Oleinik/Lax entropy admissibility or vanishing-viscosity selection. | `residual-certificates/admissibility_invariant_branch.md` |
| Positivity, simplex, and invariant gaps | CAT-12, CAT-13 | Failure when aggregate equality residual omits inequality/state admissibility. | Positivity/simplex certificate and invariant checks. | `scripts/positivity_mass_toy.py`; `data/positivity_mass_toy.csv`; `data/positivity_mass_toy.png` |
| Maximum/comparison principle setting | CAT-21 | Stability baseline under exact continuous residual and exact data. | Maximum or comparison principle; failures must come from sampling, trace leakage, or underintegration. | `residual-certificates/admissibility_invariant_branch.md` |
| Hidden modes and observability | CAT-11 | Failure when the objective projects away part of the state. | Observability rank/Gramian, full-state residual, invariant checks. | `scripts/hidden_mode_observability_toy.py`; `data/hidden_mode_observability.csv`; `data/hidden_mode_observability.png` |
| Deployment-region and Lyapunov mismatch | CAT-14, CAT-19, CAT-20 | Failure when training support does not cover deployment behavior; CAT-20 remains deferred. | Deployment-domain validation, Lyapunov decrease, coverage certificates, multi-step stability checks. | `scripts/lyapunov_stability_mismatch_toy.py`; `data/lyapunov_stability_mismatch.csv`; `data/lyapunov_stability_mismatch.png` |
| Eigenmode and nullspace ambiguity | CAT-15 | Failure when a homogeneous residual does not fix amplitude, sign, phase, or eigenspace component. | Normalization, orthogonality, phase convention, eigenvalue gap/Rayleigh checks. | `scripts/eigenmode_normalization_toy.py`; `data/eigenmode_normalization.csv`; `data/eigenmode_normalization.png` |
| Inverse identifiability | CAT-17, CAT-18 | Failure for unexcited parameter directions; CAT-18 remains deferred as a PDE/source-sensor variant. | Persistent excitation, Fisher/sensitivity rank, sensor placement. | `scripts/ode_parameter_nonidentifiability_toy.py`; `data/ode_parameter_nonidentifiability.csv`; `data/ode_parameter_nonidentifiability.png` |
| Stiff scalar matched ODE residual | ODE-SB | Stability baseline: stiffness alone is not an objective failure with continuous residual and fixed initial data. | Variation-of-constants / Gronwall estimate. | `residual-certificates/ode_reliability_branch.md` |

## Toy Evidence Summary

The completed toy suite uses closed-form bad families rather than neural-network training, so the computations isolate objective design from optimizer behavior. The validated suite covers CAT-01 fixed collocation, CAT-02 trace leakage, CAT-06 high-frequency weak topology, CAT-06 localized weak defect, CAT-07 quadrature aliasing, CAT-11 hidden mode, CAT-12/CAT-13 positivity and mass, CAT-14 Lyapunov deployment mismatch, CAT-15 eigenmode normalization, and CAT-17 parameter non-identifiability. Each toy has a script under `scripts/`, data and a PNG figure under `data/`, and a focused test under `tests/`. The consolidated narrative is `residual-certificates/toy_simulation_results.md`.

## Reproducibility

Run the focused toy-test suite:

```bash
.sciml-venv/bin/python -m pytest \
  tests/test_triage_scaling.py \
  tests/test_collocation_certificate.py \
  tests/test_trace_leakage_toy.py \
  tests/test_weak_norm_high_frequency_toy.py \
  tests/test_weak_norm_localized_defect.py \
  tests/test_hidden_mode_observability_toy.py \
  tests/test_quadrature_aliasing_toy.py \
  tests/test_eigenmode_normalization_toy.py \
  tests/test_positivity_mass_toy.py \
  tests/test_lyapunov_stability_mismatch_toy.py \
  tests/test_ode_parameter_nonidentifiability_toy.py
```

Then run the workspace checks:

```bash
python3 -m long_exposure.tools.promise_check <run-workspace>
python3 -m long_exposure.tools.org_check <run-workspace>
```

Known warnings from the latest validated checks are historical or pre-existing: old noncanonical artifact paths, pending M-2 and M-4 milestone labels, orphan session database files and old report artifacts, missing old manager assessment/report artifacts, and root-layout warnings for `launch_residual_minimization.py`, `residual_minimization_run_config.yaml`, and `run_residual_minimization_detached.sh`.

## Limitations And Nonclaims

- This report does not claim that PINNs, neural operators, collocation methods, or residual minimization fail in general.
- It does not claim production-system or industrial scientific-ML failures; application relevance is structural analogy or toy demonstration unless an artifact explicitly says otherwise.
- M-2 is not separately validated as a standalone continuous norm-mismatch theorem. Its substance is partly represented by weak-topology and trace-leakage results, but the milestone label remains pending / partly absorbed.
- M-4 is partly absorbed by the Burgers admissibility proof sketch and M-9 branch, but this run did not complete a full shock-selection simulation campaign.
- CAT-18 and CAT-20 remain deferred: the inverse PDE/source sensor-nullspace case and long-horizon surrogate drift case need separate clean setups.
- The simulations demonstrate explicit objective-function failures, not optimizer frequency or practical training prevalence.

## Final Reading Path

Start with `residual-certificates/broad_synthesis_package.md` for the validated closure argument. Use `residual-certificates/residual_case_catalogue.md` for individual mechanisms, `residual-certificates/application_risk_map.md` for application relevance, and `residual-certificates/toy_simulation_results.md` for reproducible numerical evidence. The branch notes are the audit trail for the main distinctions: weak topology versus matched dual norms, equality residuals versus admissibility, and ODE residuals versus observability, deployment support, identifiability, and stability baselines.
