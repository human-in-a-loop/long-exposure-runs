---
created: 2026-05-16T13:45:00Z
cycle: 27
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M16-local-spectral-window-corollaries
---

# Local Windows From Rigidity

## Setup

Let
\[
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}} r\tanh(\pi r)\,dr,
\qquad \Lambda\ge 1/4.
\]
The Kim--Tao Weyl-law ledger from M2 gives, with high probability and with constants depending on the fixed base surface and \(\epsilon\),
\[
N_{X_n}([1/4,\Lambda])
=(2g-2)nF(\Lambda)+O\left(n^{1-\alpha_W}\Lambda^{1/2+\epsilon}\right).
\]
Subtracting the estimate at \(\Lambda+\Delta\) and \(\Lambda\) gives the local-window corollary
\[
N_{X_n}([\Lambda,\Lambda+\Delta])
=(2g-2)n\left(F(\Lambda+\Delta)-F(\Lambda)\right)
+O\left(n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}\right),
\]
where the displayed error absorbs both endpoints.  Endpoint errors are not independent; this is a deterministic subtraction of two simultaneous high-probability bounds.

## Nontriviality Threshold

A sufficient condition for the local Weyl main term to dominate the inherited global error is
\[
(2g-2)n\left(F(\Lambda+\Delta)-F(\Lambda)\right)
\gg n^{1-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}.
\]
Equivalently, after dividing by \(n\),
\[
(2g-2)\left(F(\Lambda+\Delta)-F(\Lambda)\right)
\gg n^{-\alpha_W}(\Lambda+\Delta)^{1/2+\epsilon}.
\]
This is a corollary threshold only; constants in the original theorem are not numerically specified.

For \(\Lambda>1/4\),
\[
F'(\Lambda)
=\frac{1}{2}\tanh\left(\pi\sqrt{\Lambda-1/4}\right).
\]
When \(\Delta\ll \Lambda-1/4\), the bulk approximation is
\[
\Delta \gg
\frac{n^{-\alpha_W}\Lambda^{1/2+\epsilon}}
{(2g-2)F'(\Lambda)}.
\]
At high energy \(F'(\Lambda)\to 1/2\), so the density does not improve beyond a constant factor; the energy dependence is inherited from the endpoint error.

## Edge Regime

At the spectral edge \(\Lambda=1/4\), the bulk linearization fails because \(F'(1/4)=0\).  Since
\[
\tanh(\pi r)=\pi r+O(r^3),
\]
we have
\[
F(1/4+\Delta)-F(1/4)
=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}).
\]
The edge threshold is therefore, heuristically,
\[
\Delta^{3/2}\gg n^{-\alpha_W},
\qquad\text{or}\qquad
\Delta\gg n^{-2\alpha_W/3},
\]
up to the same normalized constants and mild \((1/4+\Delta)^{1/2+\epsilon}\) factor.  This confirms that the edge is genuinely different from the bulk.

## Rigidity Window Inclusion

Kim--Tao rigidity gives deterministic reference locations \(\lambda_j\) and random eigenvalues \(\lambda_j(X_n)\) satisfying, in the M2 notation,
\[
|\lambda_j(X_n)-\lambda_j|
\le C_\epsilon \Lambda^{1/2+\epsilon}n^{-\alpha_R}
=:\delta_R(\Lambda,n)
\]
for eigenvalues in the relevant spectral range.  Therefore, on the rigidity event,
\[
\#\{j:\lambda_j(X_n)\in[\Lambda,\Lambda+\Delta]\}
\le
\#\{j:\lambda_j\in[\Lambda-\delta_R,\Lambda+\Delta+\delta_R]\},
\]
and the corresponding lower bound uses the contracted window
\[
[\Lambda+\delta_R,\Lambda+\Delta-\delta_R]
\]
when \(\Delta>2\delta_R\).

Thus rigidity transfers local windows only after expanding by \(\delta_R\).  It is most informative for windows larger than the displacement scale.  At scales comparable with \(\delta_R\), the deterministic reference density bounds cluster size by a Weyl mass over an interval of radius \(\delta_R\), which is typically of order
\[
nF'(\Lambda)\delta_R
\asymp n^{1-\alpha_R}F'(\Lambda)\Lambda^{1/2+\epsilon}
\]
in the bulk.  This is far larger than \(O(1)\) for the small exponents available here, so it is not an exact multiplicity bound or a local-statistics result.

## Consequence

The paper already implies a local Weyl corollary, but only above the inherited global endpoint-error scale.  The edge requires the integral form of \(F\), while the bulk admits a linear density approximation.  Meaningful microscopic or mean-spacing local statistics would require new variance, trace-window, or correlation input beyond the global Weyl and rigidity estimates.
