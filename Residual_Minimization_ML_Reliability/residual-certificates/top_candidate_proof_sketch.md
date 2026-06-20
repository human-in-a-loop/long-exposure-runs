---
created: 2026-05-14T03:20:00Z
cycle: 1
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-1
---

# Top Candidate Proof Sketch: Fixed-Collocation Blind Spot

## Statement

Fix an integer \(m\ge 1\) and collocation nodes \(x_j=j/m\), \(j=0,\ldots,m\). Consider the boundary-value problem
\[
u'(x)=0,\quad x\in(0,1),\qquad u(0)=u(1)=0,
\]
whose physical solution is \(u^\star=0\). Define the finite collocation residual objective
\[
J_m(u)=\frac{1}{m+1}\sum_{j=0}^{m}|u'(x_j)|^2+|u(0)|^2+|u(1)|^2.
\]
Then there are smooth functions \(u_n\) with \(J_m(u_n)=0\) for every \(n\), while \(\|u_n-u^\star\|_{L^2(0,1)}=\sqrt{3/8}\).

## Bad Sequence

Let
\[
u_n(x)=\sin^2(\pi m n x).
\]
Then \(u_n(0)=u_n(1)=0\), and
\[
u_n'(x)=\pi m n\sin(2\pi m n x).
\]
At every node \(x_j=j/m\),
\[
u_n'(x_j)=\pi m n\sin(2\pi n j)=0.
\]
Therefore \(J_m(u_n)=0\) exactly.

The physical error does not vanish:
\[
\|u_n\|_{L^2(0,1)}^2=\int_0^1 \sin^4(\pi m n x)\,dx=\frac{3}{8},
\]
because \(mn\) is an integer number of half-period pairs on \([0,1]\).

## Mechanism

The sampled derivative values and endpoint penalties are a seminorm, not a norm, on unrestricted smooth trial functions. The sequence places oscillations between the fixed collocation nodes while making the sampled residual and boundary values exactly zero. This is an objective-function failure for fixed finite collocation, not an optimizer failure and not a continuous residual failure.

## Minimal Certificate

A minimal continuous certificate is the derivative energy
\[
C(u)=\|u'\|_{L^2(0,1)}^2.
\]
For the bad sequence,
\[
C(u_n)=\int_0^1(\pi m n)^2\sin^2(2\pi m n x)\,dx=\frac{(\pi m n)^2}{2},
\]
so the certificate detects the hidden oscillation.

More importantly, replacing the sampled residual by the continuous residual restores convergence. If \(u(0)=0\), then
\[
|u(x)|=\left|\int_0^x u'(s)\,ds\right|\le \|u'\|_{L^2(0,1)}
\]
for every \(x\), hence
\[
\|u-u^\star\|_{L^2(0,1)}=\|u\|_{L^2(0,1)}\le \|u'\|_{L^2(0,1)}.
\]
Thus any sequence with \(\|u_n'\|_{L^2}\to0\) and \(u_n(0)\to0\) converges to the physical solution in \(L^2\).

## Certificate Variant for Sampled Training

A sampled method can also be repaired by making the samples norming for the trial class. One concrete sufficient condition is a regularity certificate bounding the between-node derivative variation, for example a finite element inverse/mesh condition or an \(H^1\)-type derivative certificate. The practical message is limited: fixed collocation points alone do not certify global residual control unless paired with quadrature, fill-distance, or regularity assumptions.

## Scope

This proof does not claim that PINNs generally fail. It shows that a finite sampled residual objective can be noncoercive even for the simplest differential equation. The continuous derivative residual is a positive certificate for the same problem.
