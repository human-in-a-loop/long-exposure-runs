---
title: "Residual Minimization And Scientific ML Reliability — cycles 4-6"
date: "2026-05-14"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Residual Minimization And Scientific ML Reliability — cycles 4-6

## Abstract

Cycles 4-6 closed three branch-level gaps in the residual-minimization reliability package. Cycle 4 validated M-9, the admissibility and invariant-constraint branch. Cycle 5 validated M-8, the weak-norm and topology-mismatch branch. Cycle 6 validated M-10, the ODE reliability branch. Together, these cycles expanded the project beyond finite collocation and toy residual aliasing into three broader reliability mechanisms: equality residuals can miss physical admissibility, weak objectives can miss strong physical error, and ODE objectives can certify the wrong state, trajectory, parameter, or deployment region.

The work remained deliberately small and reproducible. Each branch used explicit functions or low-dimensional systems rather than neural-network training, so the failures are objective-function failures rather than optimizer failures. The new artifacts added four CSV/PNG toy demonstrations, three branch reports, focused tests, catalogue updates, and auditor validation events. The remaining main milestone is M-12 broad synthesis.

## Introduction

The project studies residual objectives as certificates. A residual objective is useful only if small loss controls the physical quantity of interest: a solution norm, observable, invariant, admissibility condition, or deployment behavior. The earlier cycle context had already established a broad catalogue, an application map, and several toy simulations. Cycles 4-6 focused on closing the remaining branch-level gaps before synthesis.

The key terms used here are:

- **Residual objective:** the loss or certificate being minimized, such as a PDE residual norm, sampled collocation loss, observed ODE residual, or aggregate conservation penalty.
- **Physical error:** the quantity the application actually cares about, such as strong solution error, hidden-state error, positivity, entropy admissibility, or parameter error.
- **Certificate:** an added condition or estimate that detects the bad family or restores reliability, such as an entropy inequality, positivity check, stronger norm, Lyapunov condition, observability rank, or Fisher-information condition.
- **Stability baseline:** a non-failure case where classical theory already shows that the stated residual controls the desired error.

The literature anchors used in these cycles are the PINN framing of residual-based scientific ML [1], least-squares and stability perspectives from numerical analysis [2,3], and conservation-law entropy theory [5].

## Approach

The cycles followed a branch-closure pattern. Each researcher session specified a narrow gap, each worker session produced branch notes and toy artifacts, and each auditor session checked sufficiency criteria, regenerated outputs, ran focused tests, and appended validation ledger events.

Cycle 4 targeted M-9: equality residuals versus admissibility and invariants. Its source sessions are researcher `1924499b-c472-47c6-b475-f7c95e660ff7`, worker `57220a22-d2b6-40a9-90a3-bcee15c50164`, and auditor `102e6d0b-517b-4aec-a60a-7cf61b714f6e`.

Cycle 5 targeted M-8: weak-norm topology mismatch. Its source sessions are researcher `8d939c38-d6fe-455b-8e33-4866a6f1db47`, worker `2d31b55c-815d-4c37-b135-64c4d0fce566`, and auditor `25d5a03a-a702-4e11-a97d-612e3d94fd99`.

Cycle 6 targeted M-10: ODE reliability. Its source sessions are researcher `1990c73f-c803-4b39-ab4c-631f9dfff48e`, worker `2cba98c7-5738-4a4c-9fae-45882d220b5a`, and auditor `383a8bcc-7317-4b4e-88f6-02c78664de72`.

## Findings

### Cycle 4: Admissibility And Invariant Constraints

Cycle 4 established M-9 as a distinct mechanism class: an equality residual can define a larger mathematical class than the physically admissible solution concept. The worker created `residual-certificates/admissibility_invariant_branch.md`, `scripts/positivity_mass_toy.py`, `tests/test_positivity_mass_toy.py`, `data/positivity_mass_toy.csv`, and `data/positivity_mass_toy.png`, then updated the catalogue and toy-summary documents. The auditor validated M-9.

The branch had three parts.

First, the Burgers note used inviscid Burgers,
\[
u_t+\left(\frac{u^2}{2}\right)_x=0,
\]
with Riemann data \(u_L=-1,\ u_R=1\). The stationary upward jump satisfies the Rankine-Hugoniot weak-solution condition with speed zero because \(f(1)-f(-1)=0\), but it is not the entropy solution. For convex Burgers flux and \(u_L<u_R\), the entropy solution is the rarefaction fan. The correction is an entropy admissibility certificate: Oleinik/Lax admissibility, Kruzhkov entropy inequalities, or a vanishing-viscosity selection criterion [5].

Second, the positivity/mass toy tested two concentrations \(c=(c_1,c_2)\) with only aggregate mass enforced:
\[
R(c)=\left|\frac{d}{dt}(c_1+c_2)\right|^2+|c_1+c_2-1|^2.
\]
The good states \((0.5,0.5)\), \((0,1)\), and \((1,0)\) had zero residual. The bad states \((1.5,-0.5)\) and \((-0.25,1.25)\) also had zero aggregate residual, but violated positivity. The certificate
\[
C_{\rm pos}(c)=\max(0,-c_1)^2+\max(0,-c_2)^2
\]
was zero on admissible simplex states and positive on negative-concentration states.

![Aggregate conservation residual is zero for both admissible and negative-concentration states; positivity certificate separates them.](data/positivity_mass_toy.png)

Third, the maximum-principle candidate was classified as a stability baseline rather than a failure. With exact continuous residual and exact boundary or initial data, classical maximum and comparison principles prevent the proposed overshoot. Any future failure in that family should be labelled as trace leakage, discretization, underintegration, or sampling, not as a continuous maximum-principle residual failure.

The auditor regenerated the positivity/mass artifacts, ran the focused toy suite, and reported `18 passed in 26.64s`. The PNG was valid at `1332 x 1007`. `promise_check` and `org_check` exited 0 with warnings only. The auditor appended M-9 validation event `be8a87a5-9273-4766-a485-c465a5d1b908`.

### Cycle 5: Weak-Norm And Topology Mismatch

Cycle 5 validated M-8 by separating weak-objective failures from matched-residual stability. The worker created `residual-certificates/weak_topology_branch.md`, `scripts/weak_norm_localized_defect.py`, `tests/test_weak_norm_localized_defect.py`, `data/weak_norm_localized_defect.csv`, and `data/weak_norm_localized_defect.png`, then updated the catalogue and toy-summary documents. The auditor validated M-8.

The branch documented three candidates.

WT-1 / CAT-06 reused the existing high-frequency weak-norm toy. For the identity task \(u=0\), the objective
\[
J_s(u)=\|u\|_{H^{-s}}^2
\]
does not certify \(L^2\) accuracy. \(L^2\)-normalized sine modes satisfy \(\|u_k\|_{L^2}=1\), while
\[
J_s(u_k)=(1+k^2)^{-s}\to0.
\]
The correction is to measure in the target norm, add compactness or regularity, restrict bandwidth, or use a matched operator stability estimate.

WT-2 added a localized defect rather than another oscillatory example. The toy used a mean-zero interior bump-dipole, normalized so \(\|u_\epsilon\|_{L^2}=1\). The direct \(H^{-1}\) objective decreased from `0.0094018` at \(\epsilon=0.16\) to `0.0003885` at \(\epsilon=0.028125\), with fitted log-log slope `1.839`. The \(L^2\) and local maximum certificates remained nonzero.

![A localized \(L^2\)-scale defect becomes small in a negative Sobolev norm as its support shrinks.](data/weak_norm_localized_defect.png)

WT-3 / CAT-04 recorded the negative control. For an elliptic residual \(-u''=f\), exact Dirichlet trace, and residual measured in the matched \(H^{-1}\) dual norm, the energy estimate controls the \(H_0^1\) error:
\[
\|e\|_{H_0^1}\le C\|r\|_{H^{-1}}.
\]
This is a certificate, not a weak-norm failure [2,3].

The auditor regenerated the localized-defect artifacts, reported fitted slope `1.839`, and ran `6 passed in 17.17s`. `promise_check` and `org_check` exited 0 with warnings only. The auditor appended M-8 validation event `244a24a4-609f-40d6-a22b-c2b469a8f0f4`.

### Cycle 6: ODE Reliability

Cycle 6 validated M-10 by broadening ODE reliability beyond the earlier hidden-mode toy. The worker created `residual-certificates/ode_reliability_branch.md`, `scripts/lyapunov_stability_mismatch_toy.py`, `scripts/ode_parameter_nonidentifiability_toy.py`, their tests, and four CSV/PNG outputs. The auditor validated M-10.

The branch contains three ODE objective failures and one baseline.

CAT-11, from the earlier toy suite, remained the hidden-mode observability failure. An objective that observes only one component of a two-state ODE can have zero observed residual and zero observed state error while the hidden-state error remains nonzero. The certificate is full-state residual control or an observability rank/Gramian check.

CAT-14 added deployment-region mismatch. The true dynamics are \(x'=-x\), but training only checks the equilibrium trajectory \(x=0\). The bad learned field \(\hat f(x)=x\) satisfies the training residual exactly because \(\hat f(0)=0\). From deployment initial state \(x_0=1\), the true solution at \(t=2\) is `0.1353352832366127`, while the bad rollout is `7.38905609893065`, with error `7.253720815694038`. The Lyapunov certificate flips sign: for \(V=x^2\), the true derivative at \(x=1\) is `-2`, while the bad derivative is `+2`.

![Training residual on the equilibrium trajectory is zero, but the learned vector field violates the Lyapunov decrease certificate off trajectory.](data/lyapunov_stability_mismatch.png)

CAT-17 added inverse-parameter non-identifiability. For \(x'=\theta x\) with \(x(0)=0\), the zero trajectory gives zero residual and zero state-data error for all tested \(\theta\in\{-4,-2,-1,0,2,4\}\). With \(\theta^\star=-1\), \(\theta=4\) has parameter error `5`. The Fisher/sensitivity information is `0` at \(x_0=0\), while the excited check at \(x_0=1\) gives `0.08083089595423305`.

![Zero trajectory gives zero residual for every parameter; excitation restores identifiability.](data/ode_parameter_nonidentifiability.png)

The stiffness note prevented overclaiming. For \(y'=-\lambda y\), fixed initial data, and continuous residual \(r=y'+\lambda y\), variation of constants gives
\[
e(t)=\int_0^t e^{-\lambda(t-s)}r(s)\,ds.
\]
Thus stiffness alone is not an objective-function failure when the continuous residual and initial trace are correctly controlled. Sparse sampling, underweighted initial conditions, and hidden fast components remain separate mechanisms.

The auditor regenerated the two new ODE toy artifacts, ran `9 passed in 12.15s`, and confirmed both new PNGs were valid `1206 x 756` RGBA files. `promise_check` and `org_check` exited 0 with warnings only. The auditor appended M-10 validation event `4bf16b5d-7628-44f0-a8e2-83fa636f87b5`.

## Discussion

Cycles 4-6 changed the package from a set of residual counterexamples into a structured reliability map. M-9 showed that equality residuals can miss admissibility. M-8 showed that weak topology can miss strong physical error, while also recording when matched residuals are stable. M-10 showed that ODE residual objectives can certify the wrong observed state, trajectory support, parameter direction, or deployment region.

The cycles also sharpened the project’s guardrails. Not every small residual is a failure, and not every tempting example should be promoted. Matched elliptic residuals in the correct dual norm can be valid certificates. Heat and Poisson maximum-principle settings with exact continuous residual and exact data are stability baselines. Scalar stiff ODEs with continuous residual control and fixed initial data are stable by variation of constants. These baselines matter because they prevent the catalogue from becoming a broad critique of residual minimization as such.

The validated milestones now include M-1, M-3, M-5, M-6, M-7, M-8, M-9, M-10, and M-11. The remaining main milestone is M-12 broad synthesis. M-2 and M-4 still lack direct ledger events, but the audit guidance says their substance has partly been absorbed into validated catalogue branches and should be handled carefully in synthesis rather than silently closed.

## Open Questions

The next step is M-12 broad synthesis. It should combine the validated branches without reopening them: fixed collocation, catalogue/application mapping, weak topology, admissibility/invariants, ODE reliability, and the toy suite.

Two structural gaps remain as synthesis issues rather than cycle 4-6 defects. First, M-2 and M-4 have no direct ledger events, so the synthesis must state whether their intended substance is covered by later validated milestones. Second, some catalogue cases remain deferred or lower priority, including sensor-nullspace inverse PDEs, long-horizon rollout drift, and operator train/deployment distribution mismatch. The current record treats these as future or synthesis-level items, not as validated branch closures.

## References

[1] M. Raissi, P. Perdikaris, and G. E. Karniadakis, "Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations," Journal of Computational Physics, 378, 686-707, 2019. https://doi.org/10.1016/j.jcp.2018.10.045

[2] P. B. Bochev and M. D. Gunzburger, "Least-Squares Finite Element Methods," Applied Mathematical Sciences 166, Springer, 2009. https://link.springer.com/book/10.1007/b13382

[3] A. Quarteroni and A. Valli, "Numerical Approximation of Partial Differential Equations," Springer Series in Computational Mathematics 23, Springer, 1994. https://link.springer.com/book/10.1007/978-3-540-85268-1

[5] R. J. LeVeque, "Finite Volume Methods for Hyperbolic Problems," Cambridge Texts in Applied Mathematics, Cambridge University Press, 2002. https://www.cambridge.org/core/books/finite-volume-methods-for-hyperbolic-problems/CB7B0A27A6D37AE3B906D4AE7C60A708

## Appendix: Implementation Details

### Code Organization

Cycle 4 added the M-9 branch document, positivity/mass script, test, CSV, and PNG:

- `residual-certificates/admissibility_invariant_branch.md`
- `scripts/positivity_mass_toy.py`
- `tests/test_positivity_mass_toy.py`
- `data/positivity_mass_toy.csv`
- `data/positivity_mass_toy.png`

Cycle 5 added the M-8 branch document, localized-defect script, test, CSV, and PNG:

- `residual-certificates/weak_topology_branch.md`
- `scripts/weak_norm_localized_defect.py`
- `tests/test_weak_norm_localized_defect.py`
- `data/weak_norm_localized_defect.csv`
- `data/weak_norm_localized_defect.png`

Cycle 6 added the M-10 branch document, two ODE scripts, two tests, two CSVs, and two PNGs:

- `residual-certificates/ode_reliability_branch.md`
- `scripts/lyapunov_stability_mismatch_toy.py`
- `scripts/ode_parameter_nonidentifiability_toy.py`
- `tests/test_lyapunov_stability_mismatch_toy.py`
- `tests/test_ode_parameter_nonidentifiability_toy.py`
- `data/lyapunov_stability_mismatch.csv`
- `data/lyapunov_stability_mismatch.png`
- `data/ode_parameter_nonidentifiability.csv`
- `data/ode_parameter_nonidentifiability.png`

### Test Results

Auditor-validated test results:

- Cycle 4 / M-9: `18 passed in 26.64s`; PNG check passed; `promise_check` and `org_check` exited 0 with warnings only.
- Cycle 5 / M-8: `6 passed in 17.17s`; localized-defect figure check passed; `promise_check` and `org_check` exited 0 with warnings only.
- Cycle 6 / M-10: `9 passed in 12.15s`; both new ODE PNG checks passed; `promise_check` and `org_check` exited 0 with warnings only.

Historical validator warnings remain nonblocking: old noncanonical artifact paths, orphan session/report artifacts, pre-existing root-level script/config placement warnings, and unstarted or indirectly absorbed plan milestones M-2/M-4/M-12.

### File Counts

The current manifest snapshot records:

- Scripts/check scripts: 12 files, 1341 lines.
- Tests: 11 files, 554 lines.
- Residual-certificate notes: 12 files, 878 lines.
- Root reference/ledger files: 2 files, 52 lines.
- Total tracked code/test/proof/reference/ledger files: 37 files, 2825 lines.

### Session References

Cycle 4:

- Researcher: `1924499b-c472-47c6-b475-f7c95e660ff7`
- Worker: `57220a22-d2b6-40a9-90a3-bcee15c50164`
- Auditor: `102e6d0b-517b-4aec-a60a-7cf61b714f6e`

Cycle 5:

- Researcher: `8d939c38-d6fe-455b-8e33-4866a6f1db47`
- Worker: `2d31b55c-815d-4c37-b135-64c4d0fce566`
- Auditor: `25d5a03a-a702-4e11-a97d-612e3d94fd99`

Cycle 6:

- Researcher: `1990c73f-c803-4b39-ab4c-631f9dfff48e`
- Worker: `2cba98c7-5738-4a4c-9fae-45882d220b5a`
- Auditor: `383a8bcc-7317-4b4e-88f6-02c78664de72`

### Cross-Reference Map

- M-9 / CAT-09-CAT-13: `admissibility_invariant_branch.md` -> `positivity_mass_toy.py` -> `positivity_mass_toy.csv/png` -> `test_positivity_mass_toy.py`.
- M-8 / CAT-06-WT-2: `weak_topology_branch.md` -> `weak_norm_localized_defect.py` -> `weak_norm_localized_defect.csv/png` -> `test_weak_norm_localized_defect.py`.
- M-10 / CAT-14: `ode_reliability_branch.md` -> `lyapunov_stability_mismatch_toy.py` -> `lyapunov_stability_mismatch.csv/png` -> `test_lyapunov_stability_mismatch_toy.py`.
- M-10 / CAT-17: `ode_reliability_branch.md` -> `ode_parameter_nonidentifiability_toy.py` -> `ode_parameter_nonidentifiability.csv/png` -> `test_ode_parameter_nonidentifiability_toy.py`.
- Catalogue integration: `residual_case_catalogue.md` and `toy_simulation_results.md` now include the M-8, M-9, and M-10 additions.
- Bibliography: `REFERENCES.md` supplies global citation numbering.
