---
title: "Residual Minimization And Scientific ML Reliability — cycles 1-3"
date: "2026-05-14"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Residual Minimization And Scientific ML Reliability — cycles 1-3

## Abstract

Cycles 1-3 shifted the residual-minimization project from a single validated fixed-collocation counterexample into a broader, structured research package. Cycle 1 produced and validated a catalogue of 22 attempted mechanisms and an application risk map. Cycle 2 built and validated the first three new toy demonstrations: boundary/trace leakage, weak-norm topology mismatch, and partial-observation hidden-mode failure. Cycle 3 added quadrature aliasing and eigenmode normalization demonstrations, then validated the toy-suite milestone with at least six completed simulations when the prior fixed-collocation case is included.

The central finding is that residual objectives fail as certificates when the loss controls the wrong seminorm, topology, admissibility class, observation map, quadrature rule, or normalization convention. The validated package now contains one prior fixed-collocation theorem, a validated broad catalogue scaffold, and a validated toy simulation suite spanning six distinct mechanisms. The main remaining gap is admissibility and invariant structure: entropy conditions, positivity, mass conservation, and maximum-principle certificates remain pending.

## Introduction

The directive asks for explicit scientific machine-learning failures where a residual-minimization objective can be small while the learned object remains physically wrong, together with minimal certificates or corrections that prevent the failure. In this report, a **residual objective** means the scalar loss used to measure violation of a differential equation, constraint, observation equation, or surrogate consistency condition. A **collocation** or **quadrature** loss means a discrete approximation to that residual objective using sampled points or numerical integration. A **physical error** means the norm, observable, invariant, admissibility condition, or solution concept that the application actually needs. A **certificate** means an added check, norm, constraint, estimate, or admissibility condition that detects the bad family or restores a stability implication.

The work reported here deliberately separates **objective-function failure** from optimizer failure. The examples use explicit formulas rather than neural-network training, so the low-loss wrong solutions are properties of the residual objectives themselves. This makes the results relevant to physics-informed neural networks and related residual-learning workflows [1], but the claims remain narrower than “PINNs fail.” The package also connects the examples to classical stability and residual-method ideas from least-squares finite elements, numerical PDE analysis, scattered-data norming, and conservation-law admissibility [2–5].

## Approach

Cycles 1-3 followed a chronological build-and-validate sequence.

Cycle 1, led by researcher session `f76a3388-8235-48e0-9c1e-7d0066cd8655`, directed the worker to treat the prior fixed-collocation theorem as one catalogue entry rather than project closure. The worker session `2bb21845-f0eb-4440-b341-0af1126d9e78` created three artifacts: `residual_case_catalogue.md`, `application_risk_map.md`, and `toy_simulation_plan.md`. Auditor session `0b11c654-404d-45fe-a63f-d1e7cb5818c7` validated M-7.

Cycle 2, led by researcher session `dd82a69c-6a31-48bd-a64e-7289b216b39b`, selected three explicit toy cases: CAT-02 trace leakage, CAT-06 weak-norm mismatch, and CAT-11 partial observability. Worker session `0cb80a5a-a487-4214-84c7-dd780cd500b8` built scripts, tests, CSVs, figures, and a prose result note. Auditor session `2e1840ce-5bd9-4d1a-967a-dca10c79f9a8` validated this three-case tranche while explicitly not closing the broader M-8, M-10, or M-11 branches.

Cycle 3, led by researcher session `bae8ab30-f4bf-4066-96a8-57f829bdb9d9`, added two mechanisms that were not just trace or observation kernels: CAT-07 quadrature aliasing and CAT-15 eigenmode normalization. Worker session `b7bd3b8e-eddd-4715-9004-8f898e2bc38d` produced both new toy simulations and updated the result note. Auditor session `17126dbd-5514-4b5c-b9f9-39cd2f20b07e` validated M-11 and the five-toy-suite criterion.

## Findings

### Cycle 1: A Broad Catalogue Was Built And Validated

Cycle 1 produced `residual-certificates/residual_case_catalogue.md`, a ranked table of 22 attempted mechanisms. Each row records the equation or domain, method class, residual objective, bad sequence or counterexample idea, loss behavior, physical-error behavior, failure mechanism, certificate or correction, application relevance, status, and next test.

The catalogue grouped mechanisms into several families:

- Sampling noncoercivity: fixed collocation, localized defects, quadrature aliasing, and sparse spectral checks.
- Missing constraints or admissibility: trace leakage, constant nullspaces, entropy conditions, mass/positivity constraints, Lyapunov checks, and eigenmode normalization.
- Observability and identifiability failures: hidden ODE modes and inverse-problem non-identifiability.
- Norm, topology, and distribution mismatch: weak residual norms, matched-stability negative controls, train/deployment support mismatch, and long-horizon observable mismatch.

The prior fixed-collocation theorem was integrated as CAT-01. It concerns $u'=0$ on $(0,1)$ with endpoint conditions and fixed nodes. The bad family $u_n(x)=\sin^2(\pi mnx)$ has zero sampled residual and endpoint penalty, while its $L^2$ error remains fixed. The catalogue treats this as one validated theorem, not as the endpoint of the research package.

The application risk map, `residual-certificates/application_risk_map.md`, links every CAT entry to at least one scientific-ML motif: transport and advection, heat and diffusion, conservation laws, spectral solvers, mechanics and vibration, chemical kinetics, control, climate/geophysical surrogates, inverse problems, and neural operators. It uses evidence labels such as validated theorem, theorem-quality, theorem-promising, toy-ready, plausible structural analogy, negative control, and deferred.

The M-7 audit validated the catalogue and map. It confirmed 22 catalogue rows, at least 10 explicit objective/function-family entries, at least five theorem-quality or rigorous obstruction entries, full application-map coverage, and a five-simulation triage plan. It also noted that conservation-law examples should remain theorem-promising until a precise weak/entropy construction is written.

### Cycle 2: Three New Toy Mechanisms Were Demonstrated

Cycle 2 built the first new toy/proof tranche beyond CAT-01.

#### CAT-02: Boundary/Trace Leakage

CAT-02 tests the ODE $u'(x)=0$ on $[0,1]$ with intended trace $u(0)=0$ and true solution $u^\star=0$. The residual objective is

$$
J_n(u)=\|u'\|_{L^2(0,1)}^2+n^{-2}|u(0)|^2.
$$

For the bad family $u_n(x)=1$, the derivative residual is zero, $J_n(u_n)=n^{-2}\to0$, and the physical error remains $\|u_n-u^\star\|_{L^2}=1$. The correction is a nonvanishing trace penalty or the standard fundamental-theorem/Poincare-style estimate using a fixed boundary trace term.

![Boundary penalty tends to zero while the wrong constant solution keeps unit physical error.](data/trace_leakage_scaling.png)

The audit spot check recorded, at $n=128$, objective `6.103515625e-05`, physical error `1.0`, and fixed trace certificate `1.0`.

#### CAT-06: Weak-Norm High-Frequency Mismatch

CAT-06 tests direct weak-topology certification. On $(0,2\pi)$, normalized sine modes $u_k$ satisfy

$$
J_k(u_k)=\|u_k\|_{H^{-s}}^2=(1+k^2)^{-s}\to0
$$

for $s>0$, while $\|u_k\|_{L^2}=1$. The certificate is a stronger $L^2$ residual, a bandwidth/regularity restriction, or another compactness condition that prevents high-frequency modes from disappearing in the weak norm.

![Negative-norm residual decays for high-frequency modes while $L^2$ physical error stays fixed.](data/weak_norm_scaling.png)

The script also includes a negative control: a matched elliptic residual row where the attempted weak-norm failure collapses to a stability baseline. The audit recorded the direct weak objective at $k=128,s=1$ as approximately `6.1031431187061336e-05` with physical error `1.0`, while the matched elliptic baseline had objective `1.0`, physical error `1.0`, and classification `stability_baseline`.

#### CAT-11: Partial-Observation Hidden Mode

CAT-11 tests a two-state ODE,

$$
x_1'=-x_1,\qquad x_2'=-\alpha x_2,
$$

when the objective observes or enforces only the first component. The bad family $x(t)=(0,1)$ has zero observed residual and zero observed state error, but hidden-state error remains one. The full-state residual certificate gives $\|x_2'+\alpha x_2\|_{L^2}^2=\alpha^2$, and the observation matrix has a one-dimensional hidden nullspace.

![Observed residual is zero while hidden-state physical error remains nonzero.](data/hidden_mode_observability.png)

The audit spot check recorded, at $\alpha=16$, observed residual `0.0`, observed error `0.0`, hidden error `1.0`, full-state residual certificate `256.0`, and hidden nullspace dimension `1`.

The cycle 2 audit validated the tranche with `9 passed in 14.15s` after regenerating all three artifact sets. It emphasized that this validated the three-case tranche, not full branch closure for M-8, M-10, or M-11.

### Cycle 3: Two Additional Toy Mechanisms Completed The M-11 Suite

Cycle 3 added quadrature aliasing and eigenmode normalization. These were chosen because they extend the suite beyond uncontrolled boundary traces or hidden observation kernels.

#### CAT-07: Quadrature Aliasing

CAT-07 approximates the residual integral for $u'(x)=0$ on $[-1,1]$ using $Q$-point Gauss-Legendre quadrature,

$$
J_Q(u)=\sum_{i=1}^Q w_i |u'(x_i)|^2+|u(-1)|^2+|u(1)|^2.
$$

The bad family is defined by $u_Q'(x)=P_Q(x)$, the Legendre polynomial of degree $Q$, and

$$
u_Q(x)=\int_{-1}^{x}P_Q(t)\,dt.
$$

Since the Gauss nodes are roots of $P_Q$, the quadrature residual term vanishes. Since $\int_{-1}^1 P_Q(t)\,dt=0$, the endpoint penalties also vanish. But the exact residual norm is

$$
\|u_Q'\|_{L^2(-1,1)}^2=\|P_Q\|_{L^2(-1,1)}^2=\frac{2}{2Q+1}>0.
$$

The correction is exact integration, overintegration on independent nodes, randomized resampling, or a fill-distance/regularity certificate. The audit specifically scoped this as a quadrature/discretization seminorm failure, not a continuous-residual failure.

![Gauss-node quadrature reports zero residual while the exact residual norm remains positive.](data/quadrature_aliasing.png)

At $Q=32$, the audit recorded quadrature objective `9.376e-31`, exact residual `0.03076923076923077`, overintegrated certificate `0.030769230769230754`, and endpoint penalties numerically zero.

#### CAT-15: Eigenmode Normalization

CAT-15 tests the first Sturm-Liouville eigenmode,

$$
-u''=u,\qquad u(0)=u(\pi)=0,
$$

with target $u^\star(x)=\sqrt{2/\pi}\sin x$. For $u_a(x)=a\sin x$, the unnormalized residual

$$
J(a)=\|-u_a''-u_a\|_{L^2(0,\pi)}^2+|u_a(0)|^2+|u_a(\pi)|^2
$$

is zero for every amplitude $a$, including $a=0$. The residual does not select the normalized physical eigenfunction. The certificate is

$$
C(a)=\left|\|u_a\|_{L^2(0,\pi)}^2-1\right|^2,
$$

with additional sign, phase, or orthogonality conventions needed for broader eigenspace recovery.

![Eigen-residual is zero for all amplitudes, while normalization detects the physically wrong zero mode.](data/eigenmode_normalization.png)

The audit spot checks recorded: at $a=0$, residual `0`, physical error `1`, normalization certificate `1`; at $a=\sqrt{2/\pi}$, residual `0`, physical error `0`, normalization certificate `0`; and at $a=1$, residual `0`, physical error `0.2533141373`, normalization certificate `0.3258084467`.

The cycle 3 audit regenerated the CAT-07 and CAT-15 outputs, ran the focused toy-suite tests, and reported `15 passed in 22.02s`. It validated M-11 and confirmed that the suite now documents at least six completed simulations: CAT-01, CAT-02, CAT-06, CAT-07, CAT-11, and CAT-15.

## Discussion

Across cycles 1-3, the package establishes a coherent mechanism map: residual minimization is unreliable when the loss fails to control the physical quantity it is being used to certify.

The six completed toy mechanisms are distinct in the recorded sense:

- CAT-01 fails because fixed samples do not control between-node oscillation.
- CAT-02 fails because a boundary trace term is asymptotically unweighted.
- CAT-06 fails because a weak topology suppresses high-frequency content while the target $L^2$ error stays fixed.
- CAT-07 fails because an underintegrated quadrature rule creates a discrete residual nullspace.
- CAT-11 fails because the observation map has a hidden nullspace.
- CAT-15 fails because a homogeneous eigen-residual is scale-invariant without normalization.

The package also records guardrails. CAT-04 is a Poisson stability negative control: under matched residual and trace norms, standard elliptic estimates control the error. CAT-05 is a weak-derivative obstruction: the tempting $H^{-1}$ derivative residual example does not produce the naive failure because the derivative order offsets the negative norm. CAT-22 qualifies the fixed-node result by noting that fresh randomized collocation estimates continuous residuals in expectation under appropriate assumptions.

The literature role of the package is therefore not to reject residual methods. Least-squares and residual methods are reliable when the residual norm is stable for the target error [2], numerical PDE methods require stability and consistency [3], scattered-data and fill-distance conditions explain when samples control functions [4], and conservation laws require admissibility conditions beyond the weak residual [5]. The scientific-ML contribution is the explicit catalogue and toy-suite framing: each low-loss failure is paired with the missing certificate or correction.

## Open Questions

The strongest unfilled area is admissibility and invariant structure. The cycle 3 auditor identified M-9 as the natural next gap: conservation/admissibility, positivity, mass, or maximum-principle candidates need at least one rigorous obstruction note or toy simulation. CAT-09 and CAT-10, the conservation-law entropy-selection entries, remain theorem-promising but not validated. They require a precise weak formulation, a non-entropy weak solution or admissibility violation, and a computable entropy or vanishing-viscosity certificate.

M-8 and M-10 remain open at the branch level even though CAT-06 and CAT-11 have validated toy evidence. Their broader branch criteria were not explicitly audited for closure in these cycles.

M-12, broad synthesis, is pending. The current validated material is sufficient for a serious interim package: a 22-entry catalogue, an application risk map, and six reproducible toy mechanisms. A final synthesis should either close the admissibility/invariant gap or state clearly why it requires a separate research campaign.

## References

[1] M. Raissi, P. Perdikaris, and G. E. Karniadakis, "Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations," Journal of Computational Physics, 378, 686-707, 2019. https://doi.org/10.1016/j.jcp.2018.10.045

[2] P. B. Bochev and M. D. Gunzburger, "Least-Squares Finite Element Methods," Applied Mathematical Sciences 166, Springer, 2009. https://link.springer.com/book/10.1007/b13382

[3] A. Quarteroni and A. Valli, "Numerical Approximation of Partial Differential Equations," Springer Series in Computational Mathematics 23, Springer, 1994. https://link.springer.com/book/10.1007/978-3-540-85268-1

[4] H. Wendland, "Scattered Data Approximation," Cambridge Monographs on Applied and Computational Mathematics 17, Cambridge University Press, 2005. https://www.cambridge.org/core/books/scattered-data-approximation/966D4683385F92FB8D1535F8D0A9585E

[5] R. J. LeVeque, "Finite Volume Methods for Hyperbolic Problems," Cambridge Texts in Applied Mathematics, Cambridge University Press, 2002. https://www.cambridge.org/core/books/finite-volume-methods-for-hyperbolic-problems/CB7B0A27A6D37AE3B906D4AE7C60A708

## Appendix: Implementation Details

### Code Organization

The catalogue and proof notes live in `residual-certificates/`:

- `residual_case_catalogue.md`: 22 ranked mechanisms with objective, bad family, loss behavior, physical-error behavior, mechanism, certificate, application relevance, status, and next test.
- `application_risk_map.md`: mapping from catalogue entries to scientific-ML application motifs.
- `toy_simulation_plan.md`: initial five-toy plan and backup simulations.
- `toy_simulation_results.md`: completed CAT-02, CAT-06, CAT-07, CAT-11, and CAT-15 toy results.
- `collocation_blind_spot_theorem.md`: prior validated CAT-01 fixed-collocation theorem and certificates.

The simulation scripts live in `scripts/`:

- `triage_residual_sequences.py`
- `collocation_certificate_scaling.py`
- `trace_leakage_toy.py`
- `weak_norm_high_frequency_toy.py`
- `hidden_mode_observability_toy.py`
- `quadrature_aliasing_toy.py`
- `eigenmode_normalization_toy.py`
- `run_final_checks.sh`

The focused tests live in `tests/`:

- `test_triage_scaling.py`
- `test_collocation_certificate.py`
- `test_trace_leakage_toy.py`
- `test_weak_norm_high_frequency_toy.py`
- `test_hidden_mode_observability_toy.py`
- `test_quadrature_aliasing_toy.py`
- `test_eigenmode_normalization_toy.py`

### Generated Data And Figures

Cycle 1 reused the prior CAT-01 data and figures:

- `data/collocation_certificate_scaling.csv`
- `data/collocation_certificate_scaling.png`
- `data/collocation_certificate_profiles.png`

Cycle 2 generated:

- `data/trace_leakage_scaling.csv`
- `data/trace_leakage_scaling.png`
- `data/weak_norm_scaling.csv`
- `data/weak_norm_scaling.png`
- `data/hidden_mode_observability.csv`
- `data/hidden_mode_observability.png`

Cycle 3 generated:

- `data/quadrature_aliasing.csv`
- `data/quadrature_aliasing.png`
- `data/eigenmode_normalization.csv`
- `data/eigenmode_normalization.png`

### Test Results

Cycle 2 worker session `0cb80a5a-a487-4214-84c7-dd780cd500b8` reported `9 passed in 13.86s` for the CAT-02, CAT-06, and CAT-11 tests. Auditor session `2e1840ce-5bd9-4d1a-967a-dca10c79f9a8` regenerated all three artifact sets and reported `9 passed in 14.15s`.

Cycle 3 worker session `b7bd3b8e-eddd-4715-9004-8f898e2bc38d` reported `15 passed in 22.50s` for the expanded toy suite. Auditor session `17126dbd-5514-4b5c-b9f9-39cd2f20b07e` regenerated CAT-07 and CAT-15 outputs, reran the focused toy-suite tests, and reported `15 passed in 22.02s`.

Validator warnings remaining after audit were pre-existing or future-scope: unstarted M-2, M-4, M-9, and M-12 items; an old noncanonical artifact path; session DB/report orphans; old manager/final-report artifact warnings; and root-level organization warnings.

### File Counts

The updated `MANIFEST.md` records:

- 8 tracked scripts/check scripts, 857 lines.
- 7 tracked tests, 366 lines.
- 9 tracked residual-certificate notes, 623 lines.
- 2 tracked root reference/ledger files, 45 lines.
- 26 tracked code/test/proof/reference/ledger files, 1891 total lines.

### Session References

- Cycle 1 researcher: `f76a3388-8235-48e0-9c1e-7d0066cd8655`
- Cycle 1 worker: `2bb21845-f0eb-4440-b341-0af1126d9e78`
- Cycle 1 auditor: `0b11c654-404d-45fe-a63f-d1e7cb5818c7`
- Cycle 2 researcher: `dd82a69c-6a31-48bd-a64e-7289b216b39b`
- Cycle 2 worker: `0cb80a5a-a487-4214-84c7-dd780cd500b8`
- Cycle 2 auditor: `2e1840ce-5bd9-4d1a-967a-dca10c79f9a8`
- Cycle 3 researcher: `bae8ab30-f4bf-4066-96a8-57f829bdb9d9`
- Cycle 3 worker: `b7bd3b8e-eddd-4715-9004-8f898e2bc38d`
- Cycle 3 auditor: `17126dbd-5514-4b5c-b9f9-39cd2f20b07e`

### Cross-Reference Map

- `residual_case_catalogue.md` and `application_risk_map.md` were produced in cycle 1 and validated by the M-7 audit.
- `toy_simulation_plan.md` selected the initial five toy directions and backup simulations.
- `trace_leakage_toy.py`, `weak_norm_high_frequency_toy.py`, and `hidden_mode_observability_toy.py` produced the cycle 2 toy artifacts and tests.
- `quadrature_aliasing_toy.py` and `eigenmode_normalization_toy.py` produced the cycle 3 toy artifacts and tests.
- `toy_simulation_results.md` consolidates the completed toy-suite results and records that the M-11 suite contains at least six simulations when CAT-01 is included.
- `REFERENCES.md` supplies the global citation numbering used in this report.
