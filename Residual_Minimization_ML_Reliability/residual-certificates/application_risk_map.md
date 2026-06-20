---
created: 2026-05-14T14:10:00Z
cycle: 48
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-7
---

# Application Risk Map

This map states structural relevance only. It does not claim that a production scientific-ML system fails unless the evidence column says the mechanism has been demonstrated in that setting.

## Evidence Strength Labels

- validated theorem: proved in the current workspace and reproducibly demonstrated.
- theorem-quality: proof is short enough to be written from the catalogue statement.
- theorem-promising: likely rigorous but needs a careful standalone proof.
- toy-ready: explicit enough for a small numerical experiment.
- plausible structural analogy: mechanism is relevant but not yet reduced to a clean theorem.
- negative control: attempted failure collapses to a stability theorem or qualified setting.
- deferred: lower value or needs a separate research cycle.

## Motif Map

| Application motif | Relevant catalogue entries | Evidence strength | What can go wrong | Certificate or correction |
|---|---|---|---|---|
| Transport and advection collocation | CAT-01, CAT-03, CAT-08, CAT-22 | CAT-01 validated theorem; CAT-03 theorem-quality; CAT-08 toy-ready; CAT-22 negative control | Fixed finite samples can miss oscillatory or localized derivative defects; constants can sit in derivative nullspaces if traces are omitted. Fresh randomized sampling weakens this deterministic failure claim. | continuous residual norm, fill-distance plus regularity, trace/mean constraints, randomized or adaptive resampling with concentration bounds |
| Boundary-layer and inflow problems | CAT-02, CAT-08, CAT-21 | CAT-02 theorem-quality; CAT-08/CAT-21 variants | Boundary penalties that vanish or boundary layers placed between samples can keep loss small while boundary/inflow physics remains wrong. | nonvanishing trace weights, trace theorem/Poincare estimates, maximum-principle checks, dense/adaptive boundary sampling |
| Heat transfer and diffusion | CAT-04, CAT-21 | CAT-04 negative control; CAT-21 theorem-promising variant | Exact Dirichlet traces plus matched elliptic/parabolic residual norms are stable, so naive continuous-residual failure claims are false; trace leakage remains a real objective-design risk. | energy estimates in \(H^{-1}\)/\(H^1_0\), fixed initial/boundary penalties, maximum principle |
| Conservation laws and shocks | CAT-09, CAT-10 | theorem-promising | A weak residual can certify a distributional solution while failing to select the entropy solution. | entropy inequalities, vanishing-viscosity checks, finite-volume entropy residuals, Rankine-Hugoniot plus entropy admissibility |
| Spectral and pseudospectral PDE solvers | CAT-07, CAT-16 | CAT-07 theorem-quality toy-demonstrated; CAT-16 lower-priority toy-ready | Underintegrated residual norms or aliased high modes can make a discrete residual norm misleading. | overintegration, quadrature exactness for residual degree, anti-aliasing, independent validation grid |
| Materials, mechanics, and vibration | CAT-15, CAT-16 | CAT-15 theorem-quality; CAT-16 toy-ready | Eigen residuals without normalization can return the zero function; sparse residual checks can miss high-frequency strain/stress defects. | normalization, orthogonality, Rayleigh quotient, eigenvalue gap estimates, energy norms |
| Chemical kinetics and biological dynamics | CAT-11, CAT-12, CAT-13 | CAT-11 theorem-quality toy-demonstrated; CAT-12/CAT-13 toy-demonstrated | Observing only slow variables misses hidden stiff modes; residuals can omit mass/positivity constraints. | observability rank, full-state residual, positivity barrier, mass/invariant certificate |
| Control and robotics | CAT-11, CAT-14 | CAT-11 theorem-quality toy-demonstrated; CAT-14 theorem-quality toy-demonstrated | A residual/data loss on observed states or training points may not certify hidden state accuracy or closed-loop stability. | observability Gramian, Lyapunov decrease certificate, invariant-set checks, deployment-domain validation |
| Climate, weather, and geophysical surrogates | CAT-12, CAT-18, CAT-20 | plausible structural analogy; CAT-18 theorem-promising | Small local residual or observation loss may miss conserved budgets, hidden modes, or long-horizon drift. | conservation checks, sensor-rank/identifiability analysis, multi-step validation, stability estimates |
| Inverse problems and parameter identification | CAT-17, CAT-18 | CAT-17 theorem-quality toy-demonstrated; CAT-18 theorem-promising | Residual and observation losses can be exactly zero for multiple parameters or source fields. | persistent excitation, Fisher/observability rank, sensor placement, prior or regularization justified by identifiability |
| Neural operators and surrogate models | CAT-06, CAT-19, CAT-20 | CAT-06 theorem-quality topology toy; CAT-19 theorem-quality support obstruction; CAT-20 plausible | Training residual can control weak or training-distribution observables while deployment observables remain uncontrolled. | deployment-distribution validation, uniform operator norms, coverage certificates, stronger observable loss |

## Entry Coverage

Every catalogue entry has at least one mapped motif:

| Entry | Primary motif | Evidence strength | Low application value? |
|---|---|---|---|
| CAT-01 | transport/advection collocation | validated theorem | no |
| CAT-02 | boundary/inflow and diffusion | theorem-quality | no |
| CAT-03 | transport/nullspace and gauges | theorem-quality | no |
| CAT-04 | heat/diffusion | negative control | no; important guardrail |
| CAT-05 | topology screening | rigorous obstruction | yes as standalone; useful guardrail |
| CAT-06 | neural-operator observable mismatch | theorem-quality topology toy | medium; artificial equation |
| CAT-07 | spectral/pseudospectral solvers | theorem-quality toy-demonstrated | no |
| CAT-08 | boundary layers/shocks | toy-ready | no, but variant of CAT-01 |
| CAT-09 | conservation laws/shocks | theorem-promising | no |
| CAT-10 | conservation laws/traffic flow | theorem-promising | no |
| CAT-11 | kinetics/control observability | theorem-quality toy-demonstrated | no |
| CAT-12 | conservation budgets | toy-demonstrated | no |
| CAT-13 | kinetics positivity | toy-demonstrated aggregate-state variant | no |
| CAT-14 | control stability | theorem-quality toy-demonstrated | no |
| CAT-15 | mechanics/eigenmodes | theorem-quality | no |
| CAT-16 | mechanics spectral aliasing | toy-ready | no, but overlaps CAT-07 |
| CAT-17 | inverse parameter ID | theorem-quality toy-demonstrated | no |
| CAT-18 | inverse/source ID | theorem-promising | no |
| CAT-19 | neural operators/surrogates | theorem-quality obstruction | no |
| CAT-20 | climate/geophysical long-horizon surrogates | plausible structural analogy | no, but needs separate setup |
| CAT-21 | heat/diffusion boundary leakage | theorem-promising variant | no, but overlaps CAT-02 |
| CAT-22 | randomized collocation | negative control | no; prevents overclaim |

## Practical Reading

The catalogue currently separates into four mechanism families. Sampling noncoercivity covers CAT-01, CAT-07, CAT-08, CAT-13, CAT-16, and qualified CAT-22. Missing constraints or admissibility covers CAT-02, CAT-03, CAT-09, CAT-10, CAT-12, CAT-14, CAT-15, and CAT-21. Observability and identifiability failures cover CAT-11, CAT-17, and CAT-18. Norm or distribution mismatch covers CAT-04, CAT-05, CAT-06, CAT-19, and CAT-20, with CAT-04/CAT-05 included mainly as guardrails against false claims.
