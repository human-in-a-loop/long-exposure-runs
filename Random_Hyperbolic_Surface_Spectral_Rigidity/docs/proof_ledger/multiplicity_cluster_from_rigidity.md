---
created: 2026-05-16T19:58:00Z
cycle: 38
run_id: run-2026-05-15T153635Z
agent: worker
milestone: M27-multiplicity-and-cluster-corollaries-from-rigidity
---

# Multiplicity And Cluster Bounds From Rigidity

## Scope

This note derives deterministic consequences of Kim--Tao Theorem 1. It uses only the high-probability indexed rigidity event and the reference locations
\[
F(\lambda_j)=\frac{j}{(2g-2)n},\qquad
F(\Lambda)=\int_0^{\sqrt{\Lambda-1/4}}r\tanh(\pi r)\,dr.
\]
No level repulsion, variance estimate, or localized trace input is added.

## Deterministic Transport Lemma

**Lemma.** Let \(\mu_j\) and \(\lambda_j\) be two nondecreasing eigenvalue lists. Suppose that for all \(j\) with \(\lambda_j,\mu_j\le \Lambda_{\max}\),
\[
|\mu_j-\lambda_j|\le R_j.
\]
For an interval \(I=[a,b]\), define \(R(I)=\sup\{R_j:\lambda_j\in [a-R(I),b+R(I)]\}\); equivalently one may use any uniform bound \(R\) valid on a containing spectral range. Then
\[
\#\{j:\mu_j\in I\}
\le
\#\{j:\lambda_j\in I^{+R}\},
\qquad
I^{+R}=[a-R,b+R]\cap[1/4,\infty).
\]
If \(I\) is replaced by a point \(\{\lambda\}\), this gives the exact-multiplicity envelope
\[
\operatorname{mult}_{\mu}(\lambda)
\le
\#\{j:|\lambda_j-\lambda|\le R\}.
\]

For the Kim--Tao event, \(R=C_\epsilon \Lambda_{\max}^{1/2+\epsilon}n^{-\alpha_R}\). Thus multiplicity is bounded by the number of deterministic reference locations in a rigidity-scale interval. This is a cluster bound, not a simplicity or level-repulsion theorem.

## Reference Counting

The reference locations are strictly increasing as values of \(F^{-1}(j/((2g-2)n))\) on \([1/4,\infty)\), but their spacing is nonuniform. For any interval \(J\),
\[
\#\{j:\lambda_j\in J\}
\le 1+(2g-2)n\bigl(F(\sup J)-F(\inf J)\bigr),
\]
where the additive \(1\) absorbs endpoint conventions.

In the fixed bulk, \(\Lambda_0>1/4\),
\[
F'(\Lambda_0)
=\frac12\tanh\left(\pi\sqrt{\Lambda_0-1/4}\right)>0.
\]
For a window of width \(w\) centered at \(\Lambda_0\), the rigidity envelope is
\[
N_{X_n}([\Lambda_0-w/2,\Lambda_0+w/2])
\le
1+(2g-2)nF'(\Lambda_0)(w+2R)+O(n(w+2R)^2).
\]
For exact multiplicity, \(w=0\), hence
\[
\operatorname{mult}_{X_n}(\lambda)
\le
1+2(2g-2)nF'(\lambda)C_\epsilon \lambda^{1/2+\epsilon}n^{-\alpha_R}
+O(nR^2).
\]
At the level of exponents this is \(O(n^{1-\alpha_R}F'(\lambda)\lambda^{1/2+\epsilon})\), matching the multiplicity scale stated after Theorem 1.

## Edge Behavior

At \(\Lambda=1/4\), \(F'(1/4)=0\), so the bulk linearization is invalid. Since
\[
\tanh(\pi r)=\pi r+O(r^3),
\qquad
F(1/4+\Delta)=\frac{\pi}{3}\Delta^{3/2}+O(\Delta^{5/2}),
\]
the edge cluster envelope for a point or interval whose upper edge is \(1/4+\Delta\) is
\[
1+(2g-2)n\frac{\pi}{3}(\Delta+R)^{3/2}+O(n(\Delta+R)^{5/2}).
\]
This is structurally different from the bulk \(nF'R\) count, but it is the same edge integral already isolated in M16.

## High Energy

As \(\Lambda\to\infty\), \(F'(\Lambda)\to 1/2\). The density stabilizes, but Theorem 1 supplies a radius
\[
R=C_\epsilon \Lambda^{1/2+\epsilon}n^{-\alpha_R}.
\]
Therefore the zero-width cluster envelope grows like
\[
O\bigl(n^{1-\alpha_R}\Lambda^{1/2+\epsilon}\bigr).
\]
High energy is dominated by the rigidity radius, not by a favorable density effect.

## Falsification Against M16

M27 does produce a correct theorem-level corollary: indexed rigidity deterministically bounds clusters and multiplicities by reference locations in an expanded interval. However, for the representative proved-shape exponents, the numerical grid classifies the bulk and high-energy bounds as `tautological_or_endpoint_only` or `high_energy_loss_dominated`, while the edge rows are `edge_endpoint_equivalent`.

Thus the branch is useful bookkeeping but not a new local-statistics result. It is distinct in formulation from M16 endpoint subtraction because it bounds exact multiplicity via indexed transport, but its scale is still the M16 rigidity/endpoint scale.
