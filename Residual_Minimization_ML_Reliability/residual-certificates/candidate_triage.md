---
created: 2026-05-14T03:20:00Z
cycle: 1
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-1
---

# Candidate Triage Through Residual-to-Error Stability

Working criterion: a residual objective fails as an objective when there is no coercive estimate of the form
\[
\|u-u^\star\|_X \le C\,J(u)^{1/2}
\]
over the admitted approximation class. Collocation losses are judged separately from continuous losses: a fixed sampled residual can fail even when the corresponding continuous residual is a valid certificate.

| Rank | Candidate ID | Equation / domain | True solution | Residual objective | Bad sequence \(u_n\) | Residual asymptotic | Error asymptotic | Mechanism | Minimal certificate | Proof difficulty | Visualization plan | Publishability note |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | C1 fixed-collocation blind spot | \(u'(x)=0\) on \((0,1)\), \(u(0)=u(1)=0\); finite nodes \(x_j=j/m\) | \(u^\star=0\) | \(J_m(u)=m^{-1}\sum_{j=0}^m |u'(x_j)|^2+|u(0)|^2+|u(1)|^2\) | \(u_n(x)=\sin^2(\pi m n x)\) | \(J_m(u_n)=0\) for all \(n\) | \(\|u_n\|_{L^2}=\sqrt{3/8}\) | Sampled derivative and boundary values are not a norming set for unrestricted smooth functions. | Replace sampled derivative residual by \(\|u'\|_{L^2}^2\), or add a regularity/fill-distance certificate bounding between-node oscillation. Poincare gives \(\|u\|_{L^2}\le \|u'\|_{L^2}\) when \(u(0)=0\). | Low | Plot profiles and collocation nodes; plot zero sampled loss against constant physical error and growing continuous derivative certificate. | Strong M-1 flagship: explicit, rigorous, directly tied to PINN-style finite collocation. It is not a continuous residual failure. |
| 2 | C2 underweighted trace leakage | \(u'(x)=0\) on \((0,1)\), intended inflow trace \(u(0)=0\) | \(u^\star=0\) | \(J_n(u)=\|u'\|_{L^2}^2+n^{-2}|u(0)|^2\) | \(u_n(x)=1\) | \(J_n(u_n)=n^{-2}\to0\) | \(\|u_n\|_{L^2}=1\) | Residual is coercive only after the boundary trace is controlled with a nonvanishing weight. | Fixed trace certificate \(|u(0)|^2\), yielding \(\|u\|_{L^2}^2\le 2\|u'\|_{L^2}^2+2|u(0)|^2\). | Low | Semilog trace-penalty loss versus constant error; show constant wrong profile. | Useful as a clean penalty-scaling warning, but less interesting because the objective changes with \(n\). |
| 3 | C3 Poisson stability baseline | \(-u''=f\) on \((0,1)\), \(u(0)=u(1)=0\) | Unique weak solution in \(H^1_0\) | \(J(u)=\|-u''-f\|_{H^{-1}}^2\), or \(L^2\) residual for \(H^2\) candidates plus exact Dirichlet trace | No accepted bad sequence under exact boundary control | Coercive: \(J(u_n)\to0\) implies \(u_n\to u^\star\) in \(H^1_0\) for the \(H^{-1}\) residual | Error vanishes by Lax-Milgram stability | Standard elliptic stability prevents objective failure when residual and boundary spaces are matched. | This is itself the certificate: dual residual norm plus exact Dirichlet trace. | Low | Negative-control panel showing residual and error decrease together for \(u_n=u^\star+n^{-1}\sin(\pi x)\). | Important guardrail: do not overclaim Poisson continuous residual failure. |
| 4 | C4 conservation-law entropy nonselection | Burgers \(u_t+(u^2/2)_x=0\) with Riemann data | Entropy solution | Distributional residual plus weak initial trace | Non-entropy weak shock/rarefaction candidates may satisfy weak residual | Weak residual can be zero while selected physical solution differs | Error can stay \(O(1)\) after shock/rarefaction mismatch | PDE weak formulation is nonunique without entropy admissibility. | Entropy inequality for convex entropies, or Kruzhkov entropy residual certificate. | Medium-high | Space-time diagram contrasting entropy and non-entropy weak solution. | Promising but deferred for M-2/M-4; needs careful statement to avoid handwaving. |
| 5 | C5 high-frequency weak residual probe | Simple linear operators with residual measured in too-weak negative norm | Depends on operator | Candidate \(J(u)=\|Lu-f\|_{H^{-s}}^2\) | High-frequency sines | Mixed: many elliptic choices do not fail because operator order offsets the weak norm | Often either residual fails to vanish or target error also weakens | Possible false positive if classical stability already applies. | Match residual norm to operator mapping and target norm; add compactness only if needed. | Medium | Scaling table of accepted/rejected norm pairs. | Downgraded: useful as a screening theme, not yet a clean counterexample. |

## Rejected or Downgraded Findings

The naive claim "Poisson with small \(L^2\) residual and exact Dirichlet data can have large \(H^1_0\) error" is rejected. For \(e=u-u^\star\in H^1_0\), \(-e''=r\) implies
\[
\|e'\|_{L^2}^2=\langle r,e\rangle \le \|r\|_{H^{-1}}\|e\|_{H^1_0},
\]
so \(\|e\|_{H^1_0}\le \|r\|_{H^{-1}}\), and \(L^2\) residual control is stronger where it is defined.

## Current Ranking

C1 is the best leading result for M-1 because it is exact, visual, and directly separates finite collocation objective failure from continuous residual stability. C2 is the simplest trace-penalty caution. C3 is the negative-control certificate baseline. C4 may become a stronger scientific-ML reliability result, but only after a dedicated entropy-solution cycle.
