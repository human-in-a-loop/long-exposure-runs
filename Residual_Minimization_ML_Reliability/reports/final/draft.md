## Introduction And Scope

This report synthesizes a residual-minimization reliability package for scientific machine learning. The central question is not whether physics-informed neural networks (PINNs), neural operators, collocation methods, or residual methods fail in general. The question is narrower: when does a small residual loss fail to certify the physical behavior that a scientific application actually needs?

The package answers that question with explicit objective-function failures and stability baselines. An objective-function failure means the stated loss itself accepts a closed-form bad family; no optimizer pathology or neural-network training run is needed. This separation matters because the examples show that a residual objective can be noncoercive before any optimization algorithm enters the picture.

The final supported thesis is:

> Residual minimization is reliable only when the residual objective is coercive, or otherwise matched, for the physical behavior being claimed. It becomes misleading when the loss controls the wrong seminorm, topology, trace, admissibility class, observation map, quadrature rule, parameter direction, normalization convention, or deployment region.

The work is grounded in small ODE, PDE, spectral, inverse-problem, and surrogate-learning examples. It connects modern residual-learning practice to classical ideas from least-squares finite element methods, numerical PDE stability, scattered-data norming, and conservation-law admissibility [1]-[5]. The examples do not establish that production SciML systems fail. Application relevance is reported as structural analogy or toy demonstration unless a source artifact says otherwise.

## Definitions And Reliability Criterion

A **residual loss** is a scalar objective measuring violation of a differential equation, algebraic invariant, learned vector-field equation, weak form, or discrete residual. A residual loss may be continuous, sampled, quadrature-based, projected onto observations, or averaged over a training distribution.

A **collocation loss** is a residual loss evaluated at finitely many points. It may include endpoint, boundary, or initial penalties. A fixed collocation grid can define a seminorm rather than a norm on unrestricted trial functions.

A **continuous loss** is a residual loss evaluated in a function norm, weak norm, or dual norm over the domain rather than at finitely many samples. Continuous losses can be reliable when the norm is matched to the operator and boundary data, but can be misleading when they measure the wrong topology.

A **boundary or initial condition penalty** is the part of a loss that enforces trace data. If its coefficient vanishes, is omitted, or is evaluated at the wrong locations, the residual may fail to control constants, offsets, inflow conditions, or physically relevant traces.

**Physical correctness** means correctness in the quantity the application needs: a solution norm, observable, invariant set, admissibility class, normalized eigenspace, parameter value, stability property, or deployment behavior. It is not automatically the same as small equation residual.

A **weak solution** satisfies a PDE after integration against test functions. For conservation laws, a weak solution is not necessarily the physically selected solution. An **entropy solution** is a weak solution satisfying additional admissibility inequalities or an equivalent selection rule such as vanishing viscosity.

A **certificate** is an added check, norm, estimate, constraint, or admissibility condition that detects a bad family or restores a stability implication. In this package, certificates include energy estimates, trace inequalities, fill-distance and regularity bounds, exact or overintegrated quadrature, entropy inequalities, positivity checks, observability rank, Fisher information, Lyapunov decrease, normalization, and deployment-domain validation.

The reliability criterion used throughout the package is:

> A residual objective certifies a physical claim only when small loss controls the target physical behavior under the stated hypotheses.

The failure cases violate this criterion. The stability baselines record cases where classical estimates do provide control, so the package does not overclaim.

## Breadth Of The Catalogue

The package contains a broad catalogue rather than one counterexample. The main catalogue artifact is `residual-certificates/residual_case_catalogue.md`, supported by `residual-certificates/broad_synthesis_package.md` and `residual-certificates/application_risk_map.md`.

The recorded breadth is:

| Criterion | Recorded count | Source |
|---|---:|---|
| Attempted mechanisms | 22 | `residual-certificates/residual_case_catalogue.md` |
| Explicit objective or function-family entries | 14+ | `residual-certificates/broad_synthesis_package.md` |
| Theorem-quality failures or rigorous obstructions | 10+ | `residual-certificates/broad_synthesis_package.md` |
| Toy simulations or variants | 10 | `residual-certificates/toy_simulation_results.md` |
| Application motifs | 9+ | `residual-certificates/application_risk_map.md` |

The final audit summary reports 10 validated milestones and 2 not-started milestones, with `promise_check_status` green. The two not-started items are important limitations: M-2 was not validated as a standalone continuous norm-mismatch theorem, and M-4 was not validated as a standalone conservation-law or shock-selection campaign. Related weak-topology, trace-leakage, and Burgers admissibility work covers adjacent mechanisms, but those standalone labels remain open.

The catalogue separates failures from negative controls. For example, fixed finite collocation can fail on unrestricted smooth trial functions, but fresh randomized collocation is a qualified negative control in expectation under sampling and regularity assumptions. Direct weak measurement can miss high-frequency physical error, but a matched elliptic residual in the correct dual norm is a stability baseline.

## Mechanism Taxonomy

### Finite Sampling And Collocation Noncoercivity

Finite point samples need not form a norming set for unrestricted trial functions. A candidate can satisfy all sampled residual equations and boundary samples while oscillating or concentrating between nodes. The recurring certificates are continuous residual norms, fill-distance plus regularity estimates, trace or mean constraints, adaptive resampling, and randomized coverage bounds.

Catalogue entries: CAT-01, CAT-03, CAT-08, and CAT-22.

### Trace And Penalty Leakage

Differential residuals often control derivatives but not constants or traces. If a boundary or initial penalty is missing or weighted by a coefficient that vanishes along the training sequence, the objective can go to zero while the physical solution remains offset. The recurring certificates are fixed positive trace weights, Poincare or fundamental-theorem estimates, and dense boundary checks.

Catalogue entries: CAT-02 and trace variants of CAT-21.

### Weak Topology Mismatch

A weak norm can make oscillatory or localized defects small even when their strong physical error remains fixed. The package distinguishes this from matched residual stability: a weak objective measuring the solution itself can fail, while the correct dual norm of a coercive elliptic operator can be a valid certificate. The recurring certificates are stronger target norms, compactness or regularity assumptions, bandwidth restrictions, and matched coercive residual estimates.

Catalogue entries: CAT-04, CAT-05, and CAT-06.

### Quadrature And Discretization Aliasing

A residual represented as a function can be globally nonzero while the numerical integral used in training is zero. This occurs when quadrature nodes or underintegration rules alias the residual. The recurring certificates are exact integration, overintegration, anti-aliasing, and independent validation nodes.

Catalogue entries: CAT-07 and CAT-16.

### Admissibility, Entropy, And Invariant Gaps

An equality residual can describe a larger mathematical class than the physical solution concept. Weak conservation-law residuals may accept non-entropy solutions; aggregate conservation residuals may accept negative species concentrations. The recurring certificates are entropy inequalities, vanishing-viscosity selection, positivity and simplex checks, and maximum or comparison principles.

Catalogue entries: CAT-09, CAT-10, CAT-12, CAT-13, and CAT-21.

### Observability And Hidden Modes

An objective that only observes or penalizes part of the state can project away a hidden component. Small observed residual then certifies the wrong object. The recurring certificates are observability rank, observability Gramians, full-state residual checks, and invariant checks.

Catalogue entry: CAT-11.

### Deployment-Region Mismatch

A learned vector field or surrogate can match the residual on the training support but behave incorrectly where it will be deployed. The recurring certificates are deployment-domain validation, Lyapunov decrease on the relevant region, coverage certificates, and multi-step stability checks.

Catalogue entries: CAT-14, CAT-19, and CAT-20.

### Inverse Identifiability

Residual and observation losses can be zero for multiple parameters or sources when the trajectory, sensors, or experiments do not excite the relevant directions. The recurring certificates are persistent excitation, Fisher or sensitivity rank, sensor placement, and identifiability analysis.

Catalogue entries: CAT-17 and CAT-18.

### Eigenmode And Nullspace Ambiguity

Homogeneous residuals often do not fix amplitude, phase, sign, or eigenspace component. The residual may be zero for the zero function or for unnormalized eigenmodes. The recurring certificates are normalization, orthogonality, phase or sign conventions, Rayleigh quotient checks, and eigenvalue-gap estimates.

Catalogue entries: CAT-15 and CAT-16.

### Stability Baselines Under Matched Norms

Some attempted failures are false under matched hypotheses. Classical estimates can prove that the residual does control the desired physical behavior. These baselines are part of the package because they prevent turning a targeted critique into a blanket critique.

Catalogue entries: CAT-04, CAT-21, CAT-22, and ODE-SB.

## Representative Theorem-Quality Cases And Obstructions

### CAT-01: Fixed Finite-Collocation Blind Spot

The setting is
\[
u'(x)=0,\qquad x\in(0,1),\qquad u(0)=u(1)=0,
\]
with true solution \(u^\star=0\). Fix uniform collocation nodes \(x_j=j/m\), \(j=0,\ldots,m\), and define
\[
J_m(u)=\frac{1}{m+1}\sum_{j=0}^m |u'(x_j)|^2+|u(0)|^2+|u(1)|^2.
\]

The bad family is
\[
u_n(x)=\sin^2(\pi mnx).
\]
It satisfies \(u_n(0)=u_n(1)=0\) and \(u_n'(x_j)=0\) at every fixed node, so \(J_m(u_n)=0\). Its physical error does not vanish:
\[
\|u_n\|_{L^2(0,1)}=\sqrt{3/8}.
\]

This proves fixed finite collocation is not a coercive certificate for \(L^2\) error on unrestricted smooth trial functions. The continuous certificate
\[
C_{\rm cont}(u)=|u(0)|^2+\|u'\|_{L^2(0,1)}^2
\]
restores control through
\[
\|u\|_{L^2(0,1)}^2\le 2|u(0)|^2+2\|u'\|_{L^2(0,1)}^2.
\]
A sampled repair also appears in the theorem source: fill distance plus an \(H^2\) regularity term controls the between-node variation of \(u'\).

### CAT-02: Underweighted Trace Leakage

The setting is \(u'(x)=0\) on \([0,1]\) with intended trace \(u(0)=0\). The tested objective is
\[
J_n(u)=\|u'\|_{L^2(0,1)}^2+n^{-2}|u(0)|^2.
\]
For the bad family \(u_n(x)=1\), the derivative residual is zero and \(J_n(u_n)=n^{-2}\to0\), but
\[
\|u_n-u^\star\|_{L^2(0,1)}=1.
\]
The correction is a fixed positive trace penalty. The same fundamental-theorem estimate used in CAT-01 shows why a nonvanishing trace term controls the constant mode.

### CAT-06: Direct Weak-Norm Mismatch

For the identity task \(u=0\) on \((0,2\pi)\), consider the objective
\[
J_s(u)=\|u\|_{H^{-s}}^2,\qquad s>0.
\]
For \(L^2\)-normalized sine modes \(u_k\),
\[
\|u_k\|_{L^2}=1,\qquad J_s(u_k)=(1+k^2)^{-s}\to0.
\]
Thus the residual objective vanishes in a weak topology while the \(L^2\) physical error stays fixed.

The weak-topology branch also includes a localized mean-zero bump-dipole \(u_\epsilon\), normalized to \(\|u_\epsilon\|_{L^2}=1\). Its direct \(H^{-1}\) objective decreases as the support scale shrinks; the toy fit records a log-log slope about 1.84. The \(L^2\) norm and local maximum certificate remain nonzero.

The guardrail is CAT-04: for a matched Poisson residual with exact trace, \(-e''=r\) and \(e\in H^1_0\) imply
\[
\|e\|_{H^1_0}\le \|r\|_{H^{-1}}
\]
up to norm convention. Weak norm alone is not the failure; mismatch between objective topology and target behavior is the failure.

### CAT-07: Quadrature Aliasing

The setting is \(u'(x)=0\) on \([-1,1]\), with endpoint penalties, but the residual integral is approximated by \(Q\)-point Gauss-Legendre quadrature:
\[
J_Q(u)=\sum_{i=1}^Q w_i |u'(x_i)|^2+|u(-1)|^2+|u(1)|^2.
\]
Let \(P_Q\) be the Legendre polynomial of degree \(Q\), and define
\[
u_Q'(x)=P_Q(x),\qquad u_Q(x)=\int_{-1}^x P_Q(t)\,dt.
\]
The quadrature nodes are the roots of \(P_Q\), so the quadrature residual is zero. The endpoint penalties also vanish because \(\int_{-1}^1 P_Q(t)\,dt=0\). The exact residual is nonzero:
\[
\|u_Q'\|_{L^2(-1,1)}^2=\|P_Q\|_{L^2(-1,1)}^2=\frac{2}{2Q+1}.
\]
The correction is exact integration, overintegration, independent validation nodes, or a quadrature rule exact for the residual degree.

### CAT-09/CAT-10: Conservation-Law Admissibility Gap

For inviscid Burgers,
\[
u_t+\left(\frac{u^2}{2}\right)_x=0,
\]
take Riemann data \(u_L=-1\), \(u_R=1\). The stationary upward jump
\[
u(t,x)=
\begin{cases}
-1,&x<0,\\
1,&x>0
\end{cases}
\]
satisfies the Rankine-Hugoniot condition with speed \(s=0\), because \(f(1)-f(-1)=0\). It is therefore a weak solution candidate with zero weak conservation residual away from the initial trace.

It is not the entropy solution. For convex Burgers flux and \(u_L<u_R\), the entropy solution is the rarefaction fan, not an upward shock. The missing certificate is entropy admissibility: Oleinik or Lax conditions, Kruzhkov entropy inequalities, or a vanishing-viscosity selection criterion [5].

The final audit records this area as partly absorbed but not a standalone M-4 closure. The proof sketch is present; a full shock-selection toy campaign was not completed.

### CAT-11: Partial-Observation Hidden Mode

The two-state ODE is
\[
x_1'=-x_1,\qquad x_2'=-\alpha x_2.
\]
If the objective observes or enforces only \(x_1\), the bad family \(x(t)=(0,1)\) has zero observed residual and zero observed state error. The hidden-state error remains one, and the full-state residual certificate gives
\[
\|x_2'+\alpha x_2\|_{L^2}^2=\alpha^2.
\]
The observability matrix for \(C=[1,0]\) has rank one in a two-dimensional state space, exposing a hidden nullspace. The correction is full-state residual control, observability rank or Gramian checks, or an invariant that detects the hidden component.

### CAT-12/CAT-13: Positivity And Mass Admissibility

For two species \(c=(c_1,c_2)\), the aggregate mass objective is
\[
R(c)=\left|\frac{d}{dt}(c_1+c_2)\right|^2+|c_1+c_2-1|^2.
\]
For constant paths, both \(c=(0.5,0.5)\) and \(c=(1.5,-0.5)\) have zero residual. The second state preserves total mass but violates positivity.

The certificate is
\[
C_{\rm pos}(c)=\max(0,-c_1)^2+\max(0,-c_2)^2,
\]
with simplex membership \(c_i\ge0\), \(\sum_i c_i=1\). This is an equality-residual versus inequality-admissibility failure.

### CAT-14: Lyapunov And Deployment-Region Mismatch

The true dynamics are \(x'=-x\), stable with \(V(x)=x^2\). If training checks only the equilibrium trajectory \(x(t)=0\), the learned vector field \(\hat f(x)=x\) has zero training residual because \(\hat f(0)=0\). It is wrong on the deployment region: from \(x_0=1\), the learned rollout is \(e^t\), the true rollout is \(e^{-t}\), and the toy records deployment error reaching 7.2537 at \(t=2\).

The Lyapunov certificate separates the fields:
\[
\dot V_f(1)=-2,\qquad \dot V_{\hat f}(1)=2.
\]
The correction is not simply more residual minimization on the same equilibrium trajectory; it is a deployment-domain Lyapunov decrease or coverage certificate.

### CAT-15: Eigenmode Normalization Ambiguity

The eigenproblem is
\[
-u''=u,\qquad u(0)=u(\pi)=0,
\]
with target normalized mode \(u^\star(x)=\sqrt{2/\pi}\sin x\). For \(u_a(x)=a\sin x\), the unnormalized residual
\[
J(a)=\|-u_a''-u_a\|_{L^2(0,\pi)}^2+|u_a(0)|^2+|u_a(\pi)|^2
\]
is zero for every amplitude \(a\), including \(a=0\). The physical normalized-mode error is nonzero unless \(a=\sqrt{2/\pi}\), up to sign convention. The certificate is
\[
C(a)=\left|\|u_a\|_{L^2(0,\pi)}^2-1\right|^2,
\]
with orthogonality and phase conventions needed for broader eigenspaces.

### CAT-17: Inverse ODE Non-Identifiability

For
\[
x'=\theta x,\qquad x(0)=0,
\]
the trajectory \(x(t)\equiv0\) gives zero residual and zero state-data error for every \(\theta\). If the target parameter is \(\theta^\star=-1\), the parameter error can be arbitrary while the residual remains zero.

The sensitivity certificate is
\[
\mathcal I(\theta)=\int_0^T \left(\partial_\theta x(t;\theta)\right)^2dt.
\]
For \(x_0=0\), \(\partial_\theta x=t x_0 e^{\theta t}=0\), so the Fisher or sensitivity information is zero. With nonzero excitation, the certificate becomes positive.

### Stability Baselines And Rigorous Obstructions

The package records several non-failures.

CAT-04 shows that a matched elliptic residual in \(H^{-1}\) with exact trace controls \(H^1_0\) error by an energy estimate.

CAT-05 rejects a tempting weak-derivative example: for \(u_n=\sin(nx)\), the \(H^{-1}\) size of \(u_n'\) stays order one, so the derivative order offsets the negative norm.

CAT-21 records maximum and comparison principles. With exact continuous residual and exact initial or boundary data, heat and Poisson problems do not admit residual-zero overshoot; failures require changed objectives such as trace leakage, sampling, or underintegration.

CAT-22 qualifies fixed-node collocation. Fresh randomized samples can detect a fixed residual in expectation under a sampling density and regularity assumptions.

ODE-SB records the stiff scalar baseline. For \(y'=-\lambda y\), fixed initial value, and continuous residual \(r=u'+\lambda u\), variation of constants gives
\[
e(t)=\int_0^t e^{-\lambda(t-s)}r(s)\,ds,
\]
so continuous residual control implies solution control. Stiffness alone is not an objective-function failure under those matched hypotheses.

## Toy Simulation Suite

The toy suite uses explicit functions or low-dimensional systems. It is designed to show residual loss and physical error side by side, with a certificate column that detects or repairs the failure. The focused tests and generated CSV/PNG artifacts are listed in `MANIFEST.md`.

| Case | Script | Data | Figure | Test | Measured contrast |
|---|---|---|---|---|---|
| CAT-01 fixed collocation | `scripts/collocation_certificate_scaling.py` | `data/collocation_certificate_scaling.csv` | `data/collocation_certificate_scaling.png`; `data/collocation_certificate_profiles.png` | `tests/test_collocation_certificate.py`; `tests/test_triage_scaling.py` | sampled loss zero while \(L^2\) error stays \(\sqrt{3/8}\); continuous certificate grows |
| CAT-02 trace leakage | `scripts/trace_leakage_toy.py` | `data/trace_leakage_scaling.csv` | `data/trace_leakage_scaling.png` | `tests/test_trace_leakage_toy.py` | \(n^{-2}\) trace loss vanishes while physical error stays one |
| CAT-06 high frequency | `scripts/weak_norm_high_frequency_toy.py` | `data/weak_norm_scaling.csv` | `data/weak_norm_scaling.png` | `tests/test_weak_norm_high_frequency_toy.py` | \(H^{-s}\) objective decays while \(L^2\) error stays one |
| CAT-06 localized defect | `scripts/weak_norm_localized_defect.py` | `data/weak_norm_localized_defect.csv` | `data/weak_norm_localized_defect.png` | `tests/test_weak_norm_localized_defect.py` | localized \(H^{-1}\) objective decays with fitted slope about 1.84 while \(L^2=1\) |
| CAT-07 quadrature aliasing | `scripts/quadrature_aliasing_toy.py` | `data/quadrature_aliasing.csv` | `data/quadrature_aliasing.png` | `tests/test_quadrature_aliasing_toy.py` | Gauss-node residual is zero while exact residual is \(2/(2Q+1)\) |
| CAT-11 hidden mode | `scripts/hidden_mode_observability_toy.py` | `data/hidden_mode_observability.csv` | `data/hidden_mode_observability.png` | `tests/test_hidden_mode_observability_toy.py` | observed residual and error are zero while hidden-state error is one |
| CAT-12/CAT-13 positivity/mass | `scripts/positivity_mass_toy.py` | `data/positivity_mass_toy.csv` | `data/positivity_mass_toy.png` | `tests/test_positivity_mass_toy.py` | aggregate mass residual is zero while positivity certificate detects negative species |
| CAT-14 Lyapunov mismatch | `scripts/lyapunov_stability_mismatch_toy.py` | `data/lyapunov_stability_mismatch.csv` | `data/lyapunov_stability_mismatch.png` | `tests/test_lyapunov_stability_mismatch_toy.py` | training residual is zero at equilibrium; deployment error reaches 7.2537 and \(\dot V\) has wrong sign |
| CAT-15 eigenmode normalization | `scripts/eigenmode_normalization_toy.py` | `data/eigenmode_normalization.csv` | `data/eigenmode_normalization.png` | `tests/test_eigenmode_normalization_toy.py` | eigen residual is zero for all amplitudes; normalization detects zero and small modes |
| CAT-17 parameter non-identifiability | `scripts/ode_parameter_nonidentifiability_toy.py` | `data/ode_parameter_nonidentifiability.csv` | `data/ode_parameter_nonidentifiability.png` | `tests/test_ode_parameter_nonidentifiability_toy.py` | zero trajectory fits every \(\theta\); Fisher information is zero without excitation and positive with \(x_0=1\) |

The broad synthesis reports that the full focused toy suite passed with 35 tests in the validation runs. The final audit summary reports no missing figures in the ledger-covered milestones.

## Application Risk Map

The application map states structural relevance, not production failure.

Transport and advection collocation are represented by fixed collocation, derivative nullspaces, localized defects, and randomized-collocation qualifications. The failure mode is that fixed finite samples can miss oscillatory or localized derivative defects. The corrections are continuous residuals, fill-distance and regularity, trace or mean constraints, and randomized or adaptive sampling with coverage guarantees.

Boundary-layer and inflow problems are represented by trace leakage and localized defects. Boundary penalties that vanish, or boundary layers placed between samples, can keep training loss small while boundary physics remains wrong. Nonvanishing trace weights and trace estimates are the corresponding certificates.

Heat transfer and diffusion appear mainly as guardrails. Exact Dirichlet traces plus matched elliptic or parabolic residual norms are stable under classical estimates. Trace leakage, sampling, or underintegration can still create failures, but the matched continuous residual is not the problem.

Conservation laws and shocks are represented by Burgers entropy nonselection. A weak residual can certify a distributional solution without selecting the entropy solution. Entropy inequalities, vanishing viscosity, or finite-volume entropy residuals are the relevant certificates.

Spectral and pseudospectral PDE workflows are represented by quadrature aliasing and sparse spectral checks. Underintegrated residual norms can miss polynomial or high-mode residuals. Overintegration, exactness, anti-aliasing, and independent validation grids are the repairs.

Materials, mechanics, and vibration are represented by eigenmode normalization and sparse beam/plate variants. Homogeneous eigen-residuals can miss amplitude or mode conventions, while sparse residual checks can miss stress or strain defects. Normalization, orthogonality, Rayleigh quotient checks, eigenvalue gaps, and energy norms are the repairs.

Chemical kinetics and biological dynamics are represented by hidden ODE modes and positivity/mass examples. Observing only slow variables can miss hidden components, and aggregate conservation does not imply nonnegative species. Observability, full-state residuals, positivity barriers, and invariant-set checks are the repairs.

Control and robotics are represented by hidden modes and Lyapunov deployment mismatch. A residual/data loss on observed states or training trajectories may not certify hidden-state accuracy or closed-loop stability. Observability Gramians, Lyapunov decrease, invariant sets, and deployment-domain validation are the repairs.

Climate, weather, and geophysical surrogates are represented by conservation-budget, inverse-source, and long-horizon drift motifs. The package treats some of these as structural analogies or deferred cases rather than completed demonstrations. Conservation checks, sensor-rank analysis, multi-step validation, and stability estimates are the proposed certificates.

Inverse problems and parameter identification are represented by CAT-17 and deferred CAT-18. Residual and observation losses can be exactly zero for multiple parameters or source fields. Persistent excitation, Fisher or sensitivity rank, sensor placement, and identifiability checks are the repairs.

Neural operators and surrogate models are represented by weak observables, train-support mismatch, and long-horizon mismatch. Training residual may control weak or training-distribution observables while deployment observables remain uncontrolled. Deployment-distribution validation, stronger operator norms, coverage certificates, and multi-step stability checks are the repairs.

## Certificates, Corrections, And What They Buy

The certificates in the package fall into recurring classes.

Stronger or matched norms prevent topology mismatch. Direct weak objectives such as \(H^{-s}\) measurement can miss \(L^2\)-scale errors; a strong norm, compactness assumption, bandwidth restriction, or matched operator dual norm restores control.

Continuous residuals and fill-distance estimates prevent fixed-sample blind spots. For CAT-01, the sampled residual vanishes on the bad family, but \(\|u'\|_{L^2}\) and the fill-distance plus \(\|u''\|_{L^2}\) certificate detect the oscillation.

Fixed trace penalties prevent constants and boundary leaks from disappearing. A derivative residual alone does not determine the integration constant; a nonvanishing trace, mean, or gauge condition fixes the nullspace.

Exact or overintegrated quadrature prevents aliasing. In CAT-07, the residual polynomial vanishes at Gauss nodes while its exact norm is positive. A quadrature rule exact for the squared residual, or an independent validation grid, detects the defect.

Entropy and admissibility conditions select the physical conservation-law solution. A weak conservation residual can accept a non-entropy shock; entropy inequalities or vanishing-viscosity selection encode the missing physics.

Positivity and invariant-set certificates prevent equality residuals from admitting inadmissible states. Aggregate mass conservation alone permits negative components; simplex constraints and positivity barriers rule them out.

Observability and full-state checks prevent hidden-state failures. If the observation map has a kernel, residual minimization over the observed component cannot certify the full state.

Fisher information and sensitivity rank prevent inverse non-identifiability. If the trajectory gives zero sensitivity to a parameter, a zero residual says nothing about that parameter.

Lyapunov certificates prevent training-support stability claims from leaking into deployment regions. A vector field matching one equilibrium trajectory can still be unstable elsewhere; the certificate must be checked where deployment occurs.

Normalization and orthogonality prevent homogeneous eigen-residual ambiguity. Eigen-residuals determine an eigenspace equation, not an amplitude or phase convention.

Classical energy, maximum-principle, and variation-of-constants estimates explain when a proposed failure disappears. These baselines are certificates in their own right.

## What Collapses Or Remains Lower Priority

Several catalogue entries are not counted as separate core mechanisms because their mathematical reason for failure overlaps stronger entries.

Localized bumps between fixed samples are variants of sampling noncoercivity unless they are used specifically to illustrate weak-topology concentration. Their natural certificates are still fill distance, adaptive sampling, and regularity.

Sparse beam or plate spectral residuals overlap quadrature aliasing and eigenmode ambiguity. They remain application-relevant for mechanics, but the simpler CAT-07 and CAT-15 examples carry the mechanism more cleanly.

Maximum-principle overshoot is not a continuous matched-residual failure with exact data. Classical maximum and comparison principles rule it out. If an overshoot appears after weakening boundary penalties, sampling sparsely, or underintegrating, it should be classified under trace leakage, sampling, or quadrature mismatch.

Stiffness alone is not a matched continuous-residual failure for scalar stable ODEs with fixed initial data. Variation of constants controls the error. Stiffness can still matter through sparse sampling, missing traces, hidden fast components, or optimization conditioning, but those are separate mechanisms.

CAT-18, the inverse PDE/source-sensor nullspace case, remains deferred. It is promising because sensor nullspaces are a real inverse-problem mechanism, but it needs a clean standalone linear algebra or PDE toy before being promoted.

CAT-20, the long-horizon rollout surrogate case, also remains deferred. It is relevant to climate and geophysical surrogates, but the package did not build a clean finite-dimensional rollout toy with a multi-step stability or invariant certificate.

## Limitations, Residual Debt, And Future Work

The final audit summary reports 10 validated milestones and 2 not-started milestones. It also reports one moderate finding, no critical findings, no minor findings, green promise-check status, and no wall-cap hit.

Residual debt is:

| Item | Status | Reported debt |
|---|---|---|
| M-2 | not started | No standalone continuous norm-mismatch theorem was validated; related weak-topology and trace-leakage work only partly cover adjacent mechanisms. |
| M-4 | not started | No standalone conservation-law or shock-selection campaign was completed; Burgers/admissibility analysis partly absorbs the area but does not validate the original milestone. |
| M-6 | validated with artifact-pointer issue | The latest validated M-6 event references missing `reports/final/final_report.md`; later synthesis artifacts preserve the claim. |
| CAT-18 | deferred | Inverse PDE/source-sensor variant remains deferred. |
| CAT-20 | deferred | Long-horizon rollout surrogate variant remains deferred. |

Future work should stay anchored to these items:

- For M-2, prove a standalone continuous noncoercive residual theorem with a corrected norm or certificate, or retire the original M-2 label through a ledger correction.
- For M-4, complete a scalar conservation-law entropy or shock-selection proof and toy campaign, or retire the standalone M-4 milestone label.
- For M-6, repair the artifact pointer from `reports/final/final_report.md` to the actual final report path or emit an archive/correction event.
- For CAT-18, decide whether inverse PDE/source-sensor nullspaces warrant a standalone proof or toy.
- For CAT-20, build a finite-dimensional rollout toy with a multi-step stability or invariant certificate if the application risk remains important.

These gaps do not negate the validated package. They define the boundary of what the package claims.

## Implementation Details Appendix

The main evidence artifacts are:

- `residual-certificates/residual_case_catalogue.md` — 22-entry catalogue of mechanisms, objectives, bad families, certificates, statuses, and application relevance.
- `residual-certificates/application_risk_map.md` — mapping from mechanisms to scientific-ML application motifs and evidence-strength labels.
- `residual-certificates/broad_synthesis_package.md` — integrated synthesis with breadth counts, mechanism taxonomy, closure table, toy-suite summary, theorem/obstruction summary, collapsed mechanisms, and limitations.
- `residual-certificates/collocation_blind_spot_theorem.md` — CAT-01 fixed-collocation theorem and continuous/fill-distance certificates.
- `residual-certificates/weak_topology_branch.md` — CAT-06 weak-topology failures and CAT-04 matched elliptic stability baseline.
- `residual-certificates/admissibility_invariant_branch.md` — Burgers entropy nonselection, positivity/mass toy, and maximum-principle baseline.
- `residual-certificates/ode_reliability_branch.md` — hidden modes, stiff scalar baseline, Lyapunov mismatch, and inverse ODE non-identifiability.
- `residual-certificates/toy_simulation_results.md` — detailed toy simulation descriptions and figure references.

The scripts directly tied to reported toy results are:

- `scripts/collocation_certificate_scaling.py`
- `scripts/trace_leakage_toy.py`
- `scripts/weak_norm_high_frequency_toy.py`
- `scripts/weak_norm_localized_defect.py`
- `scripts/quadrature_aliasing_toy.py`
- `scripts/hidden_mode_observability_toy.py`
- `scripts/positivity_mass_toy.py`
- `scripts/lyapunov_stability_mismatch_toy.py`
- `scripts/eigenmode_normalization_toy.py`
- `scripts/ode_parameter_nonidentifiability_toy.py`

The focused tests directly tied to reported toy results are:

- `tests/test_collocation_certificate.py`
- `tests/test_triage_scaling.py`
- `tests/test_trace_leakage_toy.py`
- `tests/test_weak_norm_high_frequency_toy.py`
- `tests/test_weak_norm_localized_defect.py`
- `tests/test_quadrature_aliasing_toy.py`
- `tests/test_hidden_mode_observability_toy.py`
- `tests/test_positivity_mass_toy.py`
- `tests/test_lyapunov_stability_mismatch_toy.py`
- `tests/test_eigenmode_normalization_toy.py`
- `tests/test_ode_parameter_nonidentifiability_toy.py`

The generated CSV and figure files cited by the synthesis are:

- `data/collocation_certificate_scaling.csv`
- `data/collocation_certificate_scaling.png`
- `data/collocation_certificate_profiles.png`
- `data/trace_leakage_scaling.csv`
- `data/trace_leakage_scaling.png`
- `data/weak_norm_scaling.csv`
- `data/weak_norm_scaling.png`
- `data/weak_norm_localized_defect.csv`
- `data/weak_norm_localized_defect.png`
- `data/quadrature_aliasing.csv`
- `data/quadrature_aliasing.png`
- `data/hidden_mode_observability.csv`
- `data/hidden_mode_observability.png`
- `data/positivity_mass_toy.csv`
- `data/positivity_mass_toy.png`
- `data/lyapunov_stability_mismatch.csv`
- `data/lyapunov_stability_mismatch.png`
- `data/eigenmode_normalization.csv`
- `data/eigenmode_normalization.png`
- `data/ode_parameter_nonidentifiability.csv`
- `data/ode_parameter_nonidentifiability.png`

The referenced validation state comes from the cycle reports, the final audit summary, and `MANIFEST.md`. Stage 3 should use this appendix when updating the required `MANIFEST.md` Key Files section.


Stage 2: Draft body written with assigned synthesis sections, toy suite, application map, certificates, limitations, and implementation appendix.
File: <run-workspace>/reports/final/draft.md
Size: 474 lines / 35381 bytes
