---
created: 2026-05-14T17:05:00Z
cycle: 55
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-12
---

# Broad Synthesis Package

## Executive Claim

Residual minimization is not intrinsically unreliable. It fails as a certificate when the loss is not coercive for the desired physical behavior: the induced seminorm has a nullspace, weak topology, missing trace or admissibility condition, unobserved state, unexcited parameter direction, insufficient quadrature, or support mismatch relative to deployment. The validated catalogue shows explicit ODE/PDE and surrogate-learning settings where residual loss vanishes or becomes misleading while the target error, invariant, admissibility condition, or deployment behavior remains wrong. It also records stability baselines where matched continuous residuals and exact data do certify correctness, so the package is not a generic critique of PINNs or residual methods.

## Definitions

- Residual loss: a scalar objective measuring violation of a differential equation, algebraic invariant, learned vector-field equation, or weak/discrete residual.
- Collocation loss: a residual loss evaluated only at finitely many points, possibly with endpoint or boundary penalties.
- Continuous loss: a residual loss evaluated in a function norm, weak norm, or dual norm over the domain rather than at finitely many samples.
- Physical correctness: convergence or correctness in the target norm, observable, admissibility class, invariant set, normalized eigenspace, parameter value, or deployment behavior.
- Certificate: an added check or estimate that makes the residual objective coercive for the target behavior, or proves that a proposed failure cannot occur under matched hypotheses.
- Objective-function failure: the stated loss accepts a closed-form bad family; no optimizer pathology is needed.
- Optimization failure: the intended objective would certify correctness, but a training algorithm fails to minimize it. This package intentionally does not rely on optimization failures.

## Breadth Check

| Criterion from directive | Synthesis count | Evidence |
|---|---:|---|
| Attempted mechanisms | 22 | `residual-certificates/residual_case_catalogue.md` has CAT-01 through CAT-22. |
| Explicit objective/family entries | 14+ | CAT-01, CAT-02, CAT-03, CAT-06, CAT-07, CAT-09/CAT-10, CAT-11, CAT-12/CAT-13, CAT-14, CAT-15, CAT-17, CAT-19 plus stability baselines CAT-04, CAT-21, ODE-SB. |
| Theorem-quality failures or rigorous obstructions | 10+ | CAT-01, CAT-02, CAT-03, CAT-04, CAT-05, CAT-06, CAT-09/CAT-10, CAT-11, CAT-14, CAT-15, CAT-17, CAT-21, CAT-22. |
| Toy simulations or variants | 10 | CAT-01, CAT-02, CAT-06 high-frequency, CAT-06 localized defect, CAT-07, CAT-11, CAT-12/CAT-13, CAT-14, CAT-15, CAT-17. |
| Application motifs | 9+ | Transport, boundary/inflow, heat/diffusion, conservation laws, spectral solvers, mechanics, kinetics/biology, control, inverse problems, neural operators. |

The breadth criteria are met by validated or in-progress-audited artifacts except for standalone milestone labels M-2 and M-4. Their substance is partly represented by the weak-topology and admissibility branches, but this package does not mark those standalone milestones validated.

## Validated Mechanism Taxonomy

| Mechanism family | Catalogue IDs | Why it is distinct | Recurring certificate |
|---|---|---|---|
| Finite sampling and collocation noncoercivity | CAT-01, CAT-03, CAT-08, CAT-22 | Point samples do not form a norming set for unrestricted trial functions; fresh randomized sampling is a qualification. | Continuous norm, fill-distance plus regularity, trace/mean constraints, randomized coverage bounds. |
| Trace and penalty leakage | CAT-02, trace variants of CAT-21 | Residual controls derivatives but the coefficient on boundary/initial data vanishes or is omitted. | Fixed positive trace weight, Poincare/FTC estimate, dense boundary checks. |
| Weak topology mismatch | CAT-05, CAT-06, CAT-04 baseline | A weak objective may miss high-frequency or localized \(L^2\)-scale defects, while matched operator dual norms may be stable. | Stronger target norm, compactness/regularity, bandwidth control, matched coercive residual estimate. |
| Quadrature and discretization aliasing | CAT-07, CAT-16 | A represented residual is globally nonzero but the numerical integral is blind to it. | Exact integration, overintegration, anti-aliasing, independent validation nodes. |
| Admissibility, entropy, and invariant gaps | CAT-09, CAT-10, CAT-12, CAT-13, CAT-21 baseline | Equality residuals can certify the wrong solution concept or omit inequality constraints. | Entropy inequalities, vanishing viscosity, positivity/simplex checks, maximum/comparison principle. |
| Observability and hidden modes | CAT-11 | The objective projects away part of the state, leaving hidden dynamics uncontrolled. | Observability rank/Gramian, full-state residual, invariant checks. |
| Deployment-region mismatch | CAT-14, CAT-19, CAT-20 | Training support is not the domain where behavior is required. | Deployment-domain validation, Lyapunov decrease, coverage certificates, multi-step stability checks. |
| Inverse identifiability | CAT-17, CAT-18 | Multiple parameters or sources produce the same residual/data fit. | Persistent excitation, Fisher/sensitivity rank, sensor placement. |
| Eigenmode and nullspace ambiguity | CAT-15, CAT-16 | Homogeneous residuals do not fix amplitude, phase, or eigenspace component. | Normalization, orthogonality, phase convention, eigenvalue gap/Rayleigh checks. |
| Stability baselines under matched norms | CAT-04, CAT-21, ODE-SB, CAT-22 | Classical estimates or sampling-in-expectation rule out the proposed failure under stated hypotheses. | Energy estimate, maximum principle, variation of constants, concentration/sample complexity. |

## Closure Table

| ID | Objective or setting | Bad family / obstruction | Loss behavior | Physical error or target defect | Certificate / correction | Status | Source artifact | Application motif |
|---|---|---|---|---|---|---|---|---|
| CAT-01 | Fixed-node derivative collocation for \(u'=0\). | \(u_n=\sin^2(\pi mnx)\). | sampled residual and endpoint loss are zero. | \(L^2\) error \(\sqrt{3/8}\). | continuous \(\|u'\|_{L^2}\), fill-distance plus \(\|u''\|_{L^2}\). | validated theorem and toy | `collocation_blind_spot_theorem.md`; `data/collocation_certificate_scaling.csv/png` | transport/advection collocation |
| CAT-02 | Continuous derivative residual with trace weight \(n^{-2}\). | \(u_n\equiv1\). | \(J_n=n^{-2}\to0\). | \(L^2\) error one. | fixed trace penalty and FTC/Poincare estimate. | theorem-quality toy | `toy_simulation_results.md`; `data/trace_leakage_scaling.csv/png` | boundary/inflow leakage |
| CAT-03 | Interior derivative samples without trace/mean. | constants \(u_a=a\). | zero. | \(L^2\) offset \(|a|\). | one trace, mean, or gauge condition. | theorem-quality | `residual_case_catalogue.md` | gauges, offsets, pressure nullspaces |
| CAT-04 | Poisson residual in matched \(H^{-1}\) norm with exact trace. | attempted oscillatory error. | residual controls error. | no failure. | Lax-Milgram energy estimate. | negative control | `weak_topology_branch.md` | heat/diffusion guardrail |
| CAT-05 | Derivative residual measured in \(H^{-1}\). | \(u_n=\sin(nx)\) attempt. | derivative \(H^{-1}\) norm stays order one. | no claimed failure. | matched operator-order analysis. | rigorous obstruction | `residual_case_catalogue.md` | topology screening |
| CAT-06 | Direct weak objective \(J=\|u\|_{H^{-s}}^2\). | normalized high-frequency modes and mean-zero localized defects. | \(J\to0\). | \(L^2\) scale stays one. | \(L^2\) check, compactness/regularity, local certificates. | theorem-quality and toy-demonstrated | `weak_topology_branch.md`; `data/weak_norm_scaling.csv/png`; `data/weak_norm_localized_defect.csv/png` | weak observables, neural operators |
| CAT-07 | Underintegrated quadrature of \(\|u'\|_{L^2}^2\). | \(u_Q'=P_Q\) at Gauss roots. | quadrature loss zero. | exact residual \(2/(2Q+1)>0\). | exact/overintegration and validation nodes. | theorem-quality toy | `data/quadrature_aliasing.csv/png` | spectral residual objectives |
| CAT-08 | Localized bump between fixed samples. | narrow support avoiding nodes. | sampled loss zero. | local or scaled \(L^p\) defect remains. | fill-distance plus regularity, adaptive sampling. | variant/toy-ready | `residual_case_catalogue.md` | boundary layers, shocks |
| CAT-09/10 | Conservation-law weak residual. | Burgers stationary upward jump. | weak residual zero. | not entropy solution. | Kruzhkov/Oleinik/Lax entropy or vanishing viscosity. | theorem-quality proof sketch | `admissibility_invariant_branch.md` | shocks and transport |
| CAT-11 | Observed component of two-state ODE. | \(x(t)=(0,1)\) while only \(x_1\) is checked. | observed residual/error zero. | hidden-state error one. | observability rank/Gramian, full-state residual. | theorem-quality toy | `ode_reliability_branch.md`; `data/hidden_mode_observability.csv/png` | kinetics, control |
| CAT-12/13 | Aggregate mass equality for two concentrations. | \(c=(1.5,-0.5)\). | aggregate residual zero. | negative concentration. | positivity/simplex certificate. | toy-demonstrated | `admissibility_invariant_branch.md`; `data/positivity_mass_toy.csv/png` | chemical kinetics, budgets |
| CAT-14 | Vector-field residual only on equilibrium trajectory. | true \(f=-x\), learned \(\hat f=x\). | train residual zero at \(x=0\). | unstable deployment rollout; \(\dot V>0\). | Lyapunov decrease on deployment domain. | theorem-quality toy | `ode_reliability_branch.md`; `data/lyapunov_stability_mismatch.csv/png` | control and robotics |
| CAT-15 | Eigen residual without normalization. | \(u_a=a\sin x\), including \(a=0\). | residual zero for all amplitudes. | normalized-mode error nonzero. | normalization, orthogonality, phase/gap checks. | theorem-quality toy | `data/eigenmode_normalization.csv/png` | mechanics and vibration |
| CAT-16 | Beam/plate sparse spectral residual. | high-frequency sampled mode. | sampled/aliased loss can vanish. | stress/strain wrong. | energy norm, boundary trace, exact quadrature. | lower-priority variant | `residual_case_catalogue.md` | materials/mechanics |
| CAT-17 | Inverse ODE with zero excitation \(x'=\theta x,\;x(0)=0\). | any \(\theta\) with \(x\equiv0\). | residual/data zero for all \(\theta\). | parameter error arbitrary. | persistent excitation, Fisher/sensitivity rank. | theorem-quality toy | `ode_reliability_branch.md`; `data/ode_parameter_nonidentifiability.csv/png` | inverse problems |
| CAT-18 | Inverse PDE/source observations in sensor nullspace. | source component invisible to sensors. | observation residual zero. | source error nonzero. | sensor rank and identifiability analysis. | theorem-promising | `residual_case_catalogue.md` | geophysics, imaging |
| CAT-19 | Operator training residual over support \(S\). | surrogate arbitrary off \(S\). | train residual zero. | deployment error off support. | deployment-distribution coverage/uniform norm. | theorem-quality support obstruction | `residual_case_catalogue.md` | neural operators |
| CAT-20 | One-step residual for rollout surrogate. | locally accurate but unstable model. | one-step loss small. | long-horizon drift. | multi-step/stability/conservation certificate. | plausible/deferred | `residual_case_catalogue.md` | climate/weather |
| CAT-21 | Matched heat/Poisson residual and exact data. | attempted residual-zero overshoot. | comparison principle controls solution. | no continuous failure. | maximum/comparison principle. | stability baseline | `admissibility_invariant_branch.md` | heat/diffusion |
| CAT-22 | Fresh randomized collocation. | fixed adversarial function cannot avoid all future samples. | expected loss detects \(L^2\) residual. | fixed-node theorem does not transfer directly. | sample complexity plus regularity. | negative control | `residual_case_catalogue.md` | PINN sampling qualification |
| ODE-SB | Stiff scalar \(y'=-\lambda y\) with fixed initial value and continuous residual. | attempted stiffness-only failure. | variation of constants controls error. | no matched objective failure. | Gronwall/variation-of-constants estimate. | rigorous stability baseline | `ode_reliability_branch.md` | stiff ODE guardrail |

## Toy-Suite Summary

| Case | Script | Data | Figure | Test | Critical measured contrast |
|---|---|---|---|---|---|
| CAT-01 fixed collocation | `scripts/collocation_certificate_scaling.py` | `data/collocation_certificate_scaling.csv` | `data/collocation_certificate_scaling.png`; `data/collocation_certificate_profiles.png` | `tests/test_collocation_certificate.py`; `tests/test_triage_scaling.py` | sampled loss zero while \(L^2\) error stays \(\sqrt{3/8}\); continuous certificate grows. |
| CAT-02 trace leakage | `scripts/trace_leakage_toy.py` | `data/trace_leakage_scaling.csv` | `data/trace_leakage_scaling.png` | `tests/test_trace_leakage_toy.py` | \(n^{-2}\) trace loss vanishes while physical error stays one. |
| CAT-06 high frequency | `scripts/weak_norm_high_frequency_toy.py` | `data/weak_norm_scaling.csv` | `data/weak_norm_scaling.png` | `tests/test_weak_norm_high_frequency_toy.py` | \(H^{-s}\) objective decays while \(L^2\) error stays one; matched elliptic row is stable. |
| CAT-06 localized defect | `scripts/weak_norm_localized_defect.py` | `data/weak_norm_localized_defect.csv` | `data/weak_norm_localized_defect.png` | `tests/test_weak_norm_localized_defect.py` | localized \(H^{-1}\) objective decays with fitted slope about 1.84 while \(L^2=1\). |
| CAT-07 quadrature aliasing | `scripts/quadrature_aliasing_toy.py` | `data/quadrature_aliasing.csv` | `data/quadrature_aliasing.png` | `tests/test_quadrature_aliasing_toy.py` | Gauss-node residual is zero while exact residual is \(2/(2Q+1)\). |
| CAT-11 hidden mode | `scripts/hidden_mode_observability_toy.py` | `data/hidden_mode_observability.csv` | `data/hidden_mode_observability.png` | `tests/test_hidden_mode_observability_toy.py` | observed residual/error zero while hidden-state error is one. |
| CAT-12/13 positivity/mass | `scripts/positivity_mass_toy.py` | `data/positivity_mass_toy.csv` | `data/positivity_mass_toy.png` | `tests/test_positivity_mass_toy.py` | aggregate mass residual zero while positivity certificate detects negative species. |
| CAT-14 Lyapunov mismatch | `scripts/lyapunov_stability_mismatch_toy.py` | `data/lyapunov_stability_mismatch.csv` | `data/lyapunov_stability_mismatch.png` | `tests/test_lyapunov_stability_mismatch_toy.py` | training residual zero at equilibrium; deployment error reaches 7.2537 and \(\dot V\) has wrong sign. |
| CAT-15 eigenmode normalization | `scripts/eigenmode_normalization_toy.py` | `data/eigenmode_normalization.csv` | `data/eigenmode_normalization.png` | `tests/test_eigenmode_normalization_toy.py` | eigen residual zero for all amplitudes; normalization detects zero/small modes. |
| CAT-17 parameter non-identifiability | `scripts/ode_parameter_nonidentifiability_toy.py` | `data/ode_parameter_nonidentifiability.csv` | `data/ode_parameter_nonidentifiability.png` | `tests/test_ode_parameter_nonidentifiability_toy.py` | zero trajectory fits every \(\theta\); Fisher information is zero without excitation and positive with \(x_0=1\). |

## Theorem And Obstruction Summary

- CAT-01 fixed collocation: validated theorem; fixed finite samples are a noncoercive seminorm on unrestricted smooth functions, repaired by continuous residual or fill-distance/regularity.
- CAT-02 trace leakage: theorem-quality; derivative residual plus vanishing trace coefficient cannot control constants, repaired by fixed trace weight.
- CAT-06 weak topology: theorem-quality; direct \(H^{-s}\) measurement can miss oscillatory and localized \(L^2\)-scale defects, repaired by stronger norms or compactness/regularity.
- CAT-07 quadrature aliasing: theorem-quality toy; insufficient quadrature can turn a nonzero polynomial residual into zero numerical loss, repaired by overintegration/exactness.
- CAT-09/CAT-10 conservation laws: theorem-quality proof sketch; weak residual selects weak solutions, not necessarily entropy solutions, repaired by entropy/vanishing-viscosity admissibility.
- CAT-11 hidden modes: theorem-quality toy; projected observations can leave hidden state components unconstrained, repaired by observability or full-state residuals.
- CAT-14 deployment mismatch: theorem-quality toy; trajectory-supported vector-field residual does not certify off-trajectory Lyapunov stability, repaired by deployment-domain Lyapunov checks.
- CAT-15 eigenmodes: theorem-quality toy; homogeneous eigen residual does not fix amplitude/sign/eigenspace, repaired by normalization and orthogonality/gap conditions.
- CAT-17 inverse parameters: theorem-quality toy; zero excitation gives zero Fisher information and arbitrary parameter error, repaired by persistent excitation.
- Stability baselines: matched elliptic residual with exact trace, classical maximum principles, randomized collocation in expectation, and stiff scalar continuous residuals are guardrails against overclaiming.

## What Collapses To Fewer Mechanisms

Several catalogue entries are intentionally not counted as separate core theorems. CAT-08 and CAT-16 are application variants of sampling/quadrature noncoercivity. Sparse-sample positivity dips reduce to sampling or trace leakage unless the objective itself omits positivity, which is CAT-12/CAT-13. Maximum-principle overshoot is not a continuous residual failure under exact data; it becomes a failure only after changing the objective through trace leakage, sampling, or underintegration. Stiffness alone is not a residual-objective failure under continuous residual and fixed initial data; the real ODE mechanisms are hidden components, missing traces, sparse sampling, deployment support, or optimization conditioning.

## Open Limitations

- M-2 remains pending as a standalone continuous norm-mismatch theorem. The validated weak-topology branch covers direct weak measurement failures, and the trace-leakage branch covers continuous residual plus vanishing boundary weight, but the original M-2 label is not separately closed here.
- M-4 remains partly absorbed rather than separately validated. The Burgers stationary-jump example is a precise admissibility proof sketch, but this run did not build a full shock-selection simulation campaign.
- CAT-18 and CAT-20 remain useful but deferred. They need cleaner linear inverse-problem and long-horizon surrogate setups to avoid vague claims.
- No production PINN, neural-operator, or industrial SciML failure is claimed. Application relevance is structural analogy or toy demonstration unless explicitly stated otherwise.
- The simulations use explicit function families and closed-form bad examples. That is a strength for isolating objective failures, but it does not measure how often optimizers find such examples in practice.

## Closure Position

The validated package supports the final claim in limited scope: residual losses become unreliable when they fail to certify the target norm, admissibility class, observable, parameter, or deployment behavior, and the minimal repairs are classical coercivity or verification conditions. Across the catalogue, those repairs recur as stronger norms, fill-distance/regularity, nonvanishing trace penalties, entropy/admissibility constraints, positivity/invariant checks, Lyapunov certificates, observability ranks, Fisher information, normalization, exact quadrature, and deployment-distribution coverage. This is sufficient for M-12 worker completion, with validation left to the auditor.
