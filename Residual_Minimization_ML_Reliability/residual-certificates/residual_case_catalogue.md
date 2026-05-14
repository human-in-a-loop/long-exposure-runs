---
created: 2026-05-14T14:05:00Z
cycle: 48
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-7
---

# Residual Case Catalogue

This catalogue treats residual objectives as certificates. A case is a failure when the stated objective has loss tending to zero while the stated physical error, observable error, or admissibility defect stays nonzero over the admitted class. A case is a negative control when a standard stability estimate shows that the attempted failure is false under the stated norms.

## Definitions Used In The Table

- Residual objective: the scalar loss actually minimized or certified.
- Physical error: the norm, observable, invariant, or solution concept the application cares about.
- Certificate/correction: the smallest added norm, admissibility check, sampling condition, or estimate that detects the bad family or restores a known stability implication.
- Status: validated theorem, theorem-quality, theorem-promising, toy-ready, plausible, negative control, obstruction, or deferred.

## Ranked Catalogue

| Rank | ID | Equation/domain | Method class | Residual objective | Bad sequence or counterexample idea | Loss behavior | Physical-error behavior | Mechanism | Certificate/correction | Application relevance | Status | Next test |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | CAT-01 | \(u'=0\) on \((0,1)\), \(u(0)=u(1)=0\), nodes \(x_j=j/m\) | fixed finite collocation/PINN-style sampled residual | \(J_m(u)=\frac1{m+1}\sum_j |u'(x_j)|^2+|u(0)|^2+|u(1)|^2\) | \(u_n(x)=\sin^2(\pi mnx)\) | \(J_m(u_n)=0\) | \(\|u_n\|_{L^2}=\sqrt{3/8}\) | finite samples are not a norming set for unrestricted smooth functions | continuous \(\|u'\|_{L^2}\) certificate or fill-distance plus \(\|u''\|_{L^2}\) regularity | transport-like collocation and derivative constraints | validated theorem | already covered by `collocation_blind_spot_theorem.md`, `scripts/collocation_certificate_scaling.py`, `data/collocation_certificate_scaling.csv` |
| 2 | CAT-02 | \(u'=0\) on \((0,1)\), intended \(u(0)=0\) | continuous residual with vanishing trace weight | \(J_n(u)=\|u'\|_{L^2}^2+n^{-2}|u(0)|^2\) | \(u_n(x)=1\) | \(J_n(u_n)=n^{-2}\to0\) | \(\|u_n\|_{L^2}=1\) | boundary trace is present but asymptotically unweighted | fixed positive trace penalty and FTC/Poincare estimate | inflow conditions, heat/Poisson boundary leakage | theorem-quality | generate `data/trace_leakage_scaling.csv/png` |
| 3 | CAT-03 | \(u'=0\), nodes omit boundary \(x_j\in(0,1)\) | interior-only collocation | \(J(u)=\sum_j |u'(x_j)|^2\) | \(u_a(x)=a\), \(a\ne0\) | \(J(u_a)=0\) | \(\|u_a\|_{L^2}=|a|\) | derivative residual has constant nullspace | one trace, mean, or mass constraint | dynamics with unobserved offsets, pressure gauges | theorem-quality | include as constant-nullspace negative example in trace toy |
| 4 | CAT-04 | \(-u''=f\) on \((0,1)\), \(u(0)=u(1)=0\) | continuous least-squares/Galerkin | \(J(u)=\|-u''-f\|_{H^{-1}}^2\) with exact trace | attempted high-frequency \(u^\star+\epsilon_n\sin(nx)\) | residual controls error | \(H^1_0\) error vanishes if \(J\to0\) | no failure: elliptic stability when residual and trace spaces match | Lax-Milgram energy estimate | heat/diffusion and elliptic PINN guardrail | negative control | document as stability baseline; do not simulate as failure |
| 5 | CAT-05 | \(u'=0\), residual measured in \(H^{-1}\) | weak-norm residual | \(J(u)=\|u'\|_{H^{-1}}^2+|u(0)|^2\) | \(u_n(x)=\sin(nx)\) with \(u_n(0)=0\) | \(\|u_n'\|_{H^{-1}}\approx O(1)\), not vanishing | \(\|u_n\|_{L^2}\approx 1/\sqrt2\) | naive weak-norm failure collapses for derivative order | use matched operator/norm analysis before claiming failure | topology mismatch screening | rigorous obstruction | compute scaling in weak-norm triage script |
| 6 | CAT-06 | identity equation \(u=0\) on \((0,2\pi)\) | wrong weak residual norm | \(J_s(u)=\|u\|_{H^{-s}}^2\), \(s>0\) | \(u_n(x)=\sin(nx)\); localized mean-zero \(L^2\)-scale defects | \(J_s(u_n)\sim (1+n^2)^{-s}\to0\); localized \(H^{-1}\) objective decays with fitted slope \(1.84\) | \(\|u_n\|_{L^2}=O(1)\); localized defect keeps \(\|u_\epsilon\|_{L^2}=1\) | training norm weaker than target physical norm | measure residual in \(L^2\), add compactness/regularity bound, restrict bandwidth, or add local sampling/certificates | operator surrogates validated only in weak observables | theorem-quality and toy-demonstrated | see `residual-certificates/weak_topology_branch.md`, `data/weak_norm_scaling.csv/png`, `data/weak_norm_localized_defect.csv/png` |
| 7 | CAT-07 | quadrature for \(\|u'\|_{L^2}^2\) on \([-1,1]\) | spectral/quadrature residual | \(Q\)-point Gauss quadrature of \(|u'|^2\) | \(u_Q'(x)=P_Q(x)\), \(u_Q(x)=\int_{-1}^xP_Q(t)dt\) | discrete quadrature loss zero | exact residual \(2/(2Q+1)>0\) | quadrature aliasing, not continuous residual failure | exact integration, overintegration, independent residual nodes, or fill-distance/regularity check | spectral PINNs, pseudospectral PDE solvers | toy-completed | see `scripts/quadrature_aliasing_toy.py`, `data/quadrature_aliasing.csv/png` |
| 8 | CAT-08 | localized boundary layer between samples for \(u'=0\) | adaptive/fixed collocation | \(\sum_j |u'(x_j)|^2+|u(0)|^2+|u(1)|^2\) | narrow smooth bump supported between two nodes | sampled loss zero if support avoids nodes | \(L^p\) error depends on amplitude/width; can keep \(L^\infty\) large and \(L^2\) if amplitude scales | localized mass missed by samples | fill distance plus Lipschitz/variation/Sobolev bound; randomized resampling only probabilistic | boundary layers and shocks | toy-ready, variant of CAT-01 | include only as localized-defect variant, not distinct theorem |
| 9 | CAT-09 | Burgers \(u_t+(u^2/2)_x=0\), Riemann data \((-1,1)\) | weak-form residual | distributional PDE residual plus initial trace | stationary upward jump satisfying Rankine-Hugoniot with \(s=0\) | weak residual zero | non-entropy jump differs from rarefaction entropy solution | PDE residual enforces weak solution, not physical admissibility | Kruzhkov entropy inequalities, Oleinik/Lax admissibility, or vanishing-viscosity residual | fluid transport and shocks | theorem-quality proof sketch | see `residual-certificates/admissibility_invariant_branch.md` |
| 10 | CAT-10 | scalar conservation law with stationary discontinuity | weak-form residual | weak residual on test functions | jump satisfying Rankine-Hugoniot but violating entropy | residual zero | wrong admissible branch persists | missing entropy condition | entropy flux inequality at shocks | traffic flow, gas dynamics | theorem-quality as CAT-09 specialization | see Burgers stationary-jump proof sketch |
| 11 | CAT-11 | stiff ODE \(y_1'=-y_1,\; y_2'=-\lambda y_2\) | observed residual only | \(J(y)=\|y_1'+y_1\|^2+\) observed \(y_1\) data | \(y_2(t)=1\) or wrong fast transient | observed loss zero | hidden-state error/invariant error nonzero | objective observes wrong state components | observability rank/Gramian and full-state residual or invariant check | chemical kinetics, biology, control | theorem-quality and toy-demonstrated | see `residual-certificates/ode_reliability_branch.md`, `data/hidden_mode_observability.csv/png` |
| 12 | CAT-12 | aggregate mass state \(c_1+c_2=1\) | residual omits species admissibility | \(R(c)=|(c_1+c_2)'|^2+|c_1+c_2-1|^2\) | constant \(c=(1.5,-0.5)\) | \(R(c)=0\) | total mass correct but species concentration negative | aggregate invariant does not imply simplex admissibility | positivity certificate plus simplex constraint \(c_i\ge0,\sum_i c_i=1\) | kinetics, climate budgets, plasma | toy-completed | see `scripts/positivity_mass_toy.py`, `data/positivity_mass_toy.csv/png` |
| 13 | CAT-13 | positivity-constrained reaction or concentration state | ODE/state residual without admissibility | equality residual checked without state inequality | negative species values or dips | equality residual can be zero/small | violates positivity and physical admissibility | residual omits state constraint | positivity barrier checked on dense grid or comparison-principle certificate | chemical kinetics/biology | toy-completed for aggregate-state variant | see CAT-12 positivity/mass toy; sparse-sample reaction dip remains variant |
| 14 | CAT-14 | Lyapunov-stable system \(\dot x=-x\) | trajectory-supported vector-field residual | residual/data checked only on equilibrium trajectory \(x(t)=0\) | learned \(\hat f(x)=x\) matches \(f(0)=0\) but has positive \(dV/dt\) elsewhere | training residual zero | unstable rollout from \(x_0=1\) and Lyapunov violation off trajectory | local trajectory fit does not certify deployment-domain stability | Lyapunov decrease certificate/SOS on the deployment domain | control and robotics | theorem-quality and toy-demonstrated | see `residual-certificates/ode_reliability_branch.md`, `data/lyapunov_stability_mismatch.csv/png` |
| 15 | CAT-15 | Sturm-Liouville \(-u''=\lambda u\) | eigen residual | \(\|-u''-\lambda u\|^2\) without normalization/orthogonality | \(u_a(x)=a\sin x\), including \(a=0\) | residual zero for all \(a\) | normalized-mode error nonzero unless \(a=\sqrt{2/\pi}\) up to sign | eigenproblem scale ambiguity | normalization, orthogonality, Rayleigh quotient/eigenvalue gap | mechanics, vibration, quantum surrogates | toy-completed/theorem-quality | see `scripts/eigenmode_normalization_toy.py`, `data/eigenmode_normalization.csv/png` |
| 16 | CAT-16 | beam/plate eigenmode with sparse collocation | spectral collocation | sampled PDE residual and boundary residual | high-frequency mode satisfying samples | sampled loss zero | stress/strain field wrong | spectral aliasing plus eigenmode ambiguity | energy norm and boundary trace/quadrature exactness | materials and mechanics | toy-ready | lower priority than CAT-15 because overlaps CAT-01/07 |
| 17 | CAT-17 | inverse ODE \(y'=\theta y\) with \(y(0)=0\) | parameter identification | residual/data fit | any \(\theta\) with \(y\equiv0\) | loss zero for all \(\theta\) | parameter error arbitrary | non-identifiability from uninformative trajectory | persistent excitation/Fisher information or sensitivity rank condition | inverse problems, system identification | theorem-quality and toy-demonstrated | see `residual-certificates/ode_reliability_branch.md`, `data/ode_parameter_nonidentifiability.csv/png` |
| 18 | CAT-18 | inverse diffusion/source with observations in nullspace | inverse PDE residual/data | PDE residual plus limited sensor observations | source component in sensor nullspace | observation loss zero | parameter/source error nonzero | measurement operator nullspace | sensor placement/rank condition and posterior identifiability check | geophysics, medical imaging | theorem-promising | needs separate linear algebra toy |
| 19 | CAT-19 | neural operator trained residual on distribution \(\mu_{\rm train}\) | operator learning | expected residual over train input distribution | operator correct on train support, wrong off support | train residual zero | deployment observable error nonzero | distribution/support mismatch | validation over deployment distribution or coverage certificate | neural operators/surrogates | theorem-quality as measure-support obstruction | write finite-dimensional toy if needed |
| 20 | CAT-20 | long-horizon rollout surrogate | residual one-step loss | one-step residual/data loss | model with small local error but unstable compounding | one-step loss small | long-horizon invariant/drift error grows | wrong target observable and stability not certified | multi-step/stability/conservation certificate | climate/weather/geophysical surrogates | plausible | defer; not a clean residual theorem yet |
| 21 | CAT-21 | maximum principle for heat/Poisson equation | matched continuous residual with exact data | exact PDE residual plus exact boundary/initial data | attempted residual-zero overshoot | obstruction: residual-zero classical solution obeys comparison principle | no admissibility failure under matched hypotheses | classical maximum/comparison principle controls range | fixed data, matched residual norm, and maximum-principle check | heat transfer/diffusion | stability baseline/rigorous obstruction | see `residual-certificates/admissibility_invariant_branch.md` |
| 22 | CAT-22 | randomized collocation per epoch | stochastic collocation | empirical sampled residual | fixed adversarial function cannot avoid all future samples | expected loss detects \(L^2\) residual under sampling density | no deterministic finite-node failure in expectation | negative control for CAT-01 under fresh random sampling and integrable residual | concentration/sample complexity plus regularity | PINN training practice | negative control/qualification | state as limit of CAT-01, no simulation now |

## Explicit Families And Proof Notes For Top Candidates

### CAT-01 Fixed finite-collocation blind spot

The validated family is \(u_n(x)=\sin^2(\pi mnx)\). It gives zero sampled derivative and endpoint penalties at fixed nodes while preserving \(L^2\) error \(\sqrt{3/8}\). The continuous derivative certificate detects it because \(\|u_n'\|_{L^2}^2=(\pi mn)^2/2\), and the fill-distance certificate detects it through \(\|u_n''\|_{L^2}^2=2(\pi mn)^4\). This is a finite-collocation objective failure only.

### CAT-02 Underweighted trace leakage

For \(u'=0\) with intended \(u(0)=0\), define \(J_n(u)=\|u'\|_{L^2}^2+n^{-2}|u(0)|^2\). The constant \(u_n\equiv1\) has \(J_n(u_n)=n^{-2}\to0\) but \(\|u_n\|_{L^2}=1\). With a fixed trace weight, the estimate \(\|u\|_{L^2}^2\le2|u(0)|^2+2\|u'\|_{L^2}^2\) restores control.

### CAT-03 Interior-only derivative nullspace

For \(u'=0\) and interior sampled derivative loss only, every constant \(u_a=a\) has zero loss. The physical error is \(|a|\) in \(L^2\). The correction is not more interior derivative samples; it is one trace, one mean, or one conserved quantity that fixes the nullspace.

### CAT-04 Poisson stability negative control

The attempted counterexample is rejected. If \(e=u-u^\star\in H^1_0(0,1)\) and \(-e''=r\), then \(\|e\|_{H^1_0}\le \|r\|_{H^{-1}}\). Thus continuous residual control in the dual norm and exact trace control is a certificate, not a failure. This guards against overextending the catalogue.

### CAT-05 Weak derivative residual obstruction

The tempting family \(u_n=\sin(nx)\) does not prove a derivative residual failure for \(u'=0\) measured in \(H^{-1}\): \(u_n'\) has \(H^{-1}\) size of order one. The derivative order offsets the negative norm. This is a useful null result because it says weak-norm failures must be matched to the operator order.

### CAT-06 Pure topology mismatch

For the residual equation \(u=0\), \(J_s(u)=\|u\|_{H^{-s}}^2\) and \(u_n=\sin(nx)\) give \(J_s(u_n)\sim(1+n^2)^{-s}\to0\) while \(\|u_n\|_{L^2}\) is constant. This is theorem-quality but less physically rich; it is best used as a minimal topology mismatch lemma.

The M-8 branch adds a localized variant that is not a fixed-sample blind spot: a mean-zero interior bump-dipole is normalized to \(\|u_\epsilon\|_{L^2}=1\), while the direct \(H^{-1}\) objective decreases as the support scale shrinks. The tested range gives fitted log-log slope \(1.84\). The mean-zero construction is intentional because a nonzero mean would create a low-frequency obstruction rather than a clean concentration/topology example.

### CAT-07 Quadrature aliasing

Underintegrated residual norms can vanish for residuals that are orthogonal to, or aliased by, the chosen quadrature rule. The completed toy uses \(u_Q'(x)=P_Q(x)\), whose values vanish at the \(Q\)-point Gauss nodes while \(\|P_Q\|_{L^2(-1,1)}^2=2/(2Q+1)>0\). This is distinct from CAT-01 when the residual is represented globally but the integral norm is computed by insufficient quadrature. The correction is quadrature exactness for the residual degree, overintegration, or independent residual sampling.

### CAT-09/CAT-10 Conservation-law admissibility

A weak residual for a scalar conservation law certifies only distributional solution status. The M-9 branch records a precise Burgers Riemann example with \(u_L=-1,u_R=1\): the stationary upward jump satisfies Rankine-Hugoniot because \(s=(f(1)-f(-1))/(1-(-1))=0\), but it is not the entropy solution, which is the rarefaction for convex flux and \(u_L<u_R\). The minimal certificate is an entropy inequality, Oleinik/Lax admissibility, or vanishing-viscosity selection. This is a genuinely distinct mechanism because the residual is not under-sampled; it enforces the wrong solution concept.

### CAT-12/CAT-13 Positivity and simplex admissibility

The completed M-9 toy separates aggregate conservation from species admissibility. Constant states \(c=(0.5,0.5)\), \(c=(0,1)\), \(c=(1,0)\), and \(c=(1.5,-0.5)\) all have zero aggregate residual \(R(c)=|(c_1+c_2)'|^2+|c_1+c_2-1|^2\), but the last state is physically inadmissible as a concentration. The positivity certificate \(C_{\rm pos}=\max(0,-c_1)^2+\max(0,-c_2)^2\) is zero on the simplex boundary and positive on negative states. This is an admissibility-constraint failure of the equality objective, not a full species-ODE residual failure.

### CAT-11 Observability and hidden stiff modes

For \(y_1'=-y_1,\; y_2'=-\lambda y_2\), an objective that observes only \(y_1\) cannot certify \(y_2\). The family \(y_1(t)=e^{-t}\), \(y_2(t)=1\) has zero observed residual and data fit if \(y_2\) is omitted, while hidden-state error relative to \(e^{-\lambda t}y_2(0)\) remains large near \(t>0\). The correction is an observability/rank condition or full-state residual/invariant check.

The M-10 branch also records the important stiffness baseline: for the scalar matched problem \(y'=-\lambda y\), fixed \(y(0)\), and continuous residual \(r=y'+\lambda y\), variation of constants gives \(e(t)=\int_0^t e^{-\lambda(t-s)}r(s)ds\). This rules out treating stiffness alone as an objective failure under matched continuous residual control; sparse sampling, missing fast state, and trace leakage are separate mechanisms.

### CAT-14 Lyapunov and deployment-region mismatch

For the stable true dynamics \(x'=-x\), a vector-field objective checked only on the equilibrium trajectory \(x(t)=0\) is blind to off-trajectory behavior. The learned field \(\hat f(x)=x\) has zero residual on the training trajectory because \(\hat f(0)=0\), but its deployment rollout from \(x_0=1\) is \(e^t\) instead of \(e^{-t}\). With \(V=x^2\), the true certificate is \(\dot V=-2x^2<0\), while the learned field has \(\dot V_{\hat f}=2x^2>0\) for \(x\ne0\). This is a support/deployment-region failure, not a failure of a full-domain vector-field residual.

### CAT-15 Eigenmode ambiguity

The eigen residual \(\|-u''-\lambda u\|\) alone is minimized by \(u=0\) and by every scalar multiple of a matching eigenfunction, so it cannot certify a normalized eigenmode. The completed toy for \(-u''=u\) on \((0,\pi)\) uses \(u_a=a\sin x\): residual is zero for all \(a\), while the error to \(\sqrt{2/\pi}\sin x\) is nonzero away from the normalized amplitude. Repeated or close eigenspaces also require normalization and orthogonality/phase conventions. The correction is a Rayleigh quotient or residual plus normalization, orthogonality to previous modes, and an eigenvalue gap estimate.

### CAT-17 Inverse non-identifiability

For \(y'=\theta y\), \(y(0)=0\), the trajectory \(y\equiv0\) makes the residual zero for every \(\theta\). Parameter error is unconstrained. This is a rigorous obstruction, not an optimization problem. The completed M-10 toy uses \(\theta^\star=-1\) and candidate values from \(-4\) to \(4\); all have zero state residual on the zero trajectory, while \(\theta=4\) has parameter error 5. A certificate requires persistent excitation or an identifiability rank condition: the Fisher/sensitivity information is zero for \(x_0=0\) and positive for the tested \(x_0=1\) excitation.

### CAT-19 Operator train/deployment support mismatch

Let the operator input \(a\) be drawn from a training distribution supported on set \(S\). Any surrogate matching the PDE residual on \(S\) but arbitrary on deployment inputs outside \(S\) has zero training residual and uncontrolled deployment error. The correction is a coverage certificate, deployment-distribution validation, or a uniform operator-norm estimate over the admissible input class.

## Deferred Or Lower-Value Cases

CAT-08 and CAT-16 are useful application variants but overlap strongly with CAT-01/CAT-07 sampling and quadrature mechanisms. The sparse-sample reaction version of CAT-13 and the underweighted-boundary version of CAT-21 are variants of sampling or trace leakage; the M-9 updates promote only the aggregate-positivity toy and the continuous maximum-principle obstruction. CAT-20 remains important for climate surrogates, but a clean theorem statement requires a chosen rollout horizon, stability class, and deployment observable. CAT-18 is likely valuable but needs a separate linear inverse-problem setup to avoid vague sensor-nullspace claims. CAT-22 is a negative control: fresh random collocation estimates the continuous residual in expectation, so the fixed-node theorem should not be misreported as a theorem about randomized residual training.
