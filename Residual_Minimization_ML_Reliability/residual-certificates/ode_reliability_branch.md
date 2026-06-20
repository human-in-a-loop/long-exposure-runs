---
created: 2026-05-14T16:45:00Z
cycle: 54
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-10
---

# ODE Reliability Branch

This branch separates ODE residual failures caused by the wrong certified object from cases where a matched continuous residual is classically stable. The mechanisms are objective-function issues, not optimizer failures: each bad family is closed form or follows from a standard estimate.

## Branch Table

| ID | Candidate | Objective controlled | Bad family or obstruction | Residual behavior | Physical error | Certificate/correction | Status |
|---|---|---|---|---|---|---|---|
| CAT-11 | Hidden mode / partial observation | observed component of a two-state ODE | \(x(t)=(0,1)\) while only \(x_1\) is checked | observed residual and observed state error are zero | hidden-state error remains one; full-state residual is \(\alpha^2\) | observability rank/Gramian, full-state residual, invariant check | theorem-quality and toy-demonstrated |
| ODE-SB | Stiff scalar matched residual | \(r=y'+\lambda y\) and fixed \(y(0)\) | obstruction: variation of constants controls the error | continuous residual control implies solution control | no objective failure under the stated continuous norm and trace | Gronwall/variation-of-constants estimate | rigorous stability baseline |
| CAT-14 | Lyapunov / deployment-region mismatch | vector-field residual only on training trajectory \(x=0\) | true \(f(x)=-x\), learned \(\hat f(x)=x\) | training residual is zero at \(x=0\) | rollout from \(x_0=1\) diverges from the true stable system | Lyapunov decrease \(2x\hat f(x)\le0\) on deployment domain | theorem-quality toy demonstration |
| CAT-17 | Inverse parameter non-identifiability | state residual/data for \(x'=\theta x\), \(x(0)=0\) | any \(\theta\) with \(x(t)\equiv0\) | residual and data error are zero for all \(\theta\) | parameter error is arbitrary | persistent excitation; positive Fisher/sensitivity information | theorem-quality toy demonstration |
| CAT-12/CAT-13 link | Positivity and mass ODE admissibility | aggregate invariant \(c_1+c_2=1\) | \(c=(1.5,-0.5)\) | aggregate residual is zero | negative concentration violates admissibility | positivity/simplex certificate | covered by M-9; not duplicated here |

## Candidate Notes

### CAT-11: Hidden Mode / Partial Observation

For \(x_1'=-x_1,\;x_2'=-\alpha x_2\), an objective that only observes \(x_1\) can certify the wrong map. The completed toy uses \(x(t)=(0,1)\): the observed residual and observed state error are zero, but the hidden \(L^2\) state error is one. The full-state residual certificate is \(\|x_2'+\alpha x_2\|_{L^2}^2=\alpha^2\), and the observation matrix \(C=[1,0]\) has rank one in a two-dimensional state space.

### Stiff Scalar Matched-Residual Baseline

For
\[
y'(t)=-\lambda y(t),\qquad y(0)=y_0,
\]
let \(u\) be a candidate with the same initial value and residual \(r=u'+\lambda u\). With \(e=u-y\), the error satisfies \(e'+\lambda e=r,\;e(0)=0\), hence
\[
e(t)=\int_0^t e^{-\lambda(t-s)}r(s)\,ds.
\]
For \(\lambda>0\), this gives \(|e(t)|\le \int_0^t |r(s)|ds\le T^{1/2}\|r\|_{L^2(0,T)}\). Stiffness can stress sparse sampling, optimizer conditioning, underweighted initial conditions, or hidden fast components, but those are sampling, trace, or observability mechanisms already catalogued rather than a matched continuous-residual failure.

### CAT-14: Lyapunov / Deployment-Region Mismatch

The true dynamics \(x'=-x\) are stable with \(V(x)=x^2\) and \(\dot V=-2x^2\). If training checks only the equilibrium trajectory \(x(t)=0\), the learned vector field \(\hat f(x)=x\) has exactly zero training residual because \(\hat f(0)=0\). It is nevertheless unstable off trajectory: from \(x(0)=1\), the learned rollout is \(e^t\) while the true rollout is \(e^{-t}\), and \(\dot V_{\hat f}=2x^2>0\) for \(x\ne0\). The certificate must be evaluated on the deployment domain, not only on the training trajectory.

### CAT-17: Inverse Parameter Non-Identifiability

For \(x'=\theta x,\;x(0)=0\), the trajectory \(x(t)\equiv0\) gives zero state residual and zero data error for every \(\theta\). If the target is \(\theta^\star=-1\), then \(\theta=4\) has residual zero and parameter error five. The sensitivity certificate
\[
\mathcal I(\theta)=\int_0^T \left(\frac{\partial x(t;\theta)}{\partial\theta}\right)^2dt
\]
vanishes for \(x_0=0\) because \(\partial_\theta x=t x_0e^{\theta t}=0\). With \(x_0\ne0\), the same expression becomes positive, giving a persistent-excitation check.

### CAT-12/CAT-13 Link: Positivity And Mass

The ODE admissibility issue was closed in M-9 as an aggregate-objective failure: equality constraints on total mass do not imply positivity of species. It remains relevant to ODE reliability, but duplicating it here would overcount the mechanism. The M-10 status uses it as a cross-branch link and keeps the new ODE branch focused on observability, deployment-region stability, inverse identifiability, and stiffness baselines.

## M-10 Closure Position

M-10 now has three explicit ODE failure mechanisms: hidden-state observability, deployment-region/Lyapunov mismatch, and inverse-parameter non-identifiability. It also records one rigorous baseline: scalar stiff ODEs are stable when continuous residual and initial data are correctly controlled. The branch was subsequently validated by the auditor; M-12 uses it as an input rather than reopening the ODE claims.
