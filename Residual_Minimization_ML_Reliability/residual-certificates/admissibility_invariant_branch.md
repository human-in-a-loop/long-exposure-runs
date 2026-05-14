---
created: 2026-05-14T16:05:00Z
cycle: 52
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-9
---

# Admissibility And Invariant-Constraint Branch

M-9 tests a mechanism that is not sampling aliasing, trace leakage, or observability: an equality residual can define a larger mathematical class than the physical solution concept. The missing information is an inequality or invariant certificate such as entropy admissibility, positivity, simplex membership, or a maximum/comparison principle.

## Candidate Summary

| Candidate | Equation or task | Equality residual | Bad family or obstruction | Admissibility error | Certificate/correction | Status |
|---|---|---|---|---|---|---|
| Burgers entropy nonselection | \(u_t+(u^2/2)_x=0\), Riemann data \(u_L=-1,u_R=1\) | distributional weak residual plus initial trace | stationary upward jump \(u=-1\) for \(x<0\), \(u=1\) for \(x>0\) | weak solution is not the entropy solution; entropy solution is rarefaction | Oleinik/Lax entropy admissibility, Kruzhkov entropy inequalities, or vanishing-viscosity selection | theorem-quality proof sketch |
| Positivity/mass admissibility | two concentrations \(c=(c_1,c_2)\) with aggregate mass one | \(R(c)=|(c_1+c_2)'|^2+|c_1+c_2-1|^2\) for constant paths | \(c(t)=(1.5,-0.5)\) | negative concentration with correct aggregate mass | \(C_{\rm pos}(c)=\max(0,-c_1)^2+\max(0,-c_2)^2\), plus simplex check | toy-completed |
| Maximum-principle baseline | heat equation or Poisson equation with exact continuous residual and exact boundary/initial data | matched continuous residual and exact data | attempted residual-zero overshoot | obstruction: classical maximum/comparison principles rule out the overshoot | retain exact data, matched residual norm, and maximum-principle check; failures require discretization or trace leakage | stability baseline |

## Burgers Entropy Nonselection

Consider inviscid Burgers
\[
u_t+\left(\frac{u^2}{2}\right)_x=0
\]
with Riemann data \(u(0,x)=-1\) for \(x<0\) and \(u(0,x)=1\) for \(x>0\). Define the stationary jump
\[
u(t,x)=\begin{cases}
-1,&x<0,\\
1,&x>0.
\end{cases}
\]
For a discontinuity moving with speed \(s\), the Rankine-Hugoniot condition is
\[
s[u]=[f(u)],\qquad f(u)=u^2/2.
\]
Here \([u]=1-(-1)=2\) and \([f]=f(1)-f(-1)=1/2-1/2=0\), so \(s=0\). Therefore the stationary jump satisfies the conservation law in the distributional weak sense and has zero weak PDE residual away from the initial trace.

It is not the entropy solution. For convex Burgers flux and \(u_L<u_R\), the admissible Riemann solution is the rarefaction fan
\[
u_{\rm ent}(t,x)=
\begin{cases}
-1,&x/t<-1,\\
x/t,&-1\le x/t\le 1,\\
1,&x/t>1.
\end{cases}
\]
The stationary upward jump violates the Lax/Oleinik entropy admissibility condition: Burgers shocks are entropy-admissible for downward jumps \(u_L>u_R\), while upward jumps are replaced by rarefactions. Equivalently, the weak residual alone selects weak solutions, not the entropy solution concept described by entropy inequalities for convex entropies; see the scalar conservation-law grounding in [5].

The certificate is not another equality residual on \(u_t+f(u)_x\). It is an admissibility check: impose entropy inequalities \(\partial_t\eta(u)+\partial_x q(u)\le0\) for convex entropy pairs, an Oleinik one-sided condition, or a vanishing-viscosity residual/limit criterion. This is a genuinely new M-9 mechanism because the candidate can satisfy the exact weak conservation law and still be physically wrong.

## Positivity And Mass Admissibility

The toy concentration task uses \(c=(c_1,c_2)\) as two species concentrations and verifies only aggregate conservation:
\[
R(c)=\left|\frac{d}{dt}(c_1+c_2)\right|^2+|c_1+c_2-1|^2.
\]
For constant paths, both \(c=(0.5,0.5)\) and \(c=(1.5,-0.5)\) have \(R(c)=0\). The bad path preserves total mass exactly but violates the physical state constraint \(c_i\ge0\).

The positivity certificate
\[
C_{\rm pos}(c)=\max(0,-c_1)^2+\max(0,-c_2)^2
\]
is zero on admissible simplex states and positive on the negative-concentration state. The completed toy evaluates the interior state, both positivity-boundary states \(c_1=0\) and \(c_2=0\), and two mass-correct inadmissible states. This toy tests an aggregate/invariant residual objective, not a full species ODE residual.

Artifacts: `scripts/positivity_mass_toy.py`, `data/positivity_mass_toy.csv`, `data/positivity_mass_toy.png`, `tests/test_positivity_mass_toy.py`.

## Maximum-Principle Baseline

A tempting M-9 claim is that a heat or Poisson residual might be zero while the solution violates a maximum principle. With exact continuous residual and exact boundary/initial data, that claim is false in the classical setting.

For example, if \(u_t-u_{xx}=0\) on a parabolic cylinder with exact initial and boundary data bounded between \(m\) and \(M\), the parabolic maximum principle gives \(m\le u\le M\). For Poisson or Laplace problems with matching hypotheses, comparison principles similarly control interior extrema from boundary data and forcing. Thus a residual-zero classical solution with exact data cannot overshoot the admissible range; the maximum principle is a positive certificate.

Failures in this family should be labelled as variants of other mechanisms unless the objective is changed. Underweighted boundary data reduces to trace leakage, finite or sparse checks reduce to sampling/collocation blind spots, and underintegrated norms reduce to quadrature or discretization mismatch. The useful M-9 outcome is the guardrail: do not advertise a continuous maximum-principle failure when the matched PDE residual and exact data already imply admissibility.

## Mechanism Assessment

M-9 adds a distinct mechanism class: equality residuals may certify the wrong solution concept. Burgers shows equality weak residual versus entropy admissibility. The concentration toy shows equality aggregate mass versus positivity/simplex membership. The maximum-principle note records the complementary obstruction: sometimes classical theory proves the admissibility property once the continuous residual and data are matched, so any failure must come from a different already-catalogued defect.
