---
created: 2026-05-14T03:45:00Z
cycle: 1
run_id: run-2026-05-14T030813Z
agent: worker
milestone: M-3
---

# Fixed-Collocation Blind Spot and Sampled Certificate

## Setting

Consider
\[
u'(x)=0,\qquad x\in(0,1),\qquad u(0)=u(1)=0.
\]
The unique physical solution is \(u^\star=0\). Fix an integer \(m\ge 1\) and uniform collocation nodes \(x_j=j/m\), \(j=0,\ldots,m\). The finite collocation objective is
\[
J_m(u)=\frac{1}{m+1}\sum_{j=0}^m |u'(x_j)|^2+|u(0)|^2+|u(1)|^2.
\]
The target physical error norm is \(\|u-u^\star\|_{L^2(0,1)}=\|u\|_{L^2(0,1)}\).

## Theorem A: Fixed-Collocation Failure

For every fixed \(m\ge 1\), there exists a smooth sequence \(u_n\) such that
\[
J_m(u_n)=0,\qquad \|u_n\|_{L^2(0,1)}=\sqrt{3/8}
\]
for all \(n\ge 1\). Hence \(J_m\) is not coercive with respect to the \(L^2\) physical error on unrestricted smooth trial functions.

### Proof

Let
\[
u_n(x)=\sin^2(\pi m n x).
\]
Then \(u_n(0)=u_n(1)=0\), because \(mn\) is an integer, and
\[
u_n'(x)=\pi mn\sin(2\pi mnx).
\]
At each collocation node \(x_j=j/m\),
\[
u_n'(x_j)=\pi mn\sin(2\pi n j)=0.
\]
Thus every sampled derivative residual and both endpoint penalties vanish, so \(J_m(u_n)=0\).

The \(L^2\) error is fixed:
\[
\|u_n\|_{L^2(0,1)}^2
=\int_0^1 \sin^4(\pi mnx)\,dx
=\frac{3}{8},
\]
since \(\sin^4 y=(3-4\cos(2y)+\cos(4y))/8\), and the cosine terms integrate to zero over an integer number of periods. Therefore \(\|u_n\|_{L^2(0,1)}=\sqrt{3/8}\).

If a constant \(C_m\) satisfied \(\|u\|_{L^2}^2\le C_m J_m(u)\) for all smooth \(u\), applying it to \(u_n\) would give \(3/8\le 0\), a contradiction. The sampled objective is therefore a noncoercive seminorm. This is an objective-function failure for fixed finite collocation, not an optimization failure.

## Theorem B: Continuous Certificate

For every \(u\in H^1(0,1)\),
\[
\|u\|_{L^2(0,1)}^2\le 2|u(0)|^2+2\|u'\|_{L^2(0,1)}^2.
\]
In particular, the continuous certificate
\[
C_{\mathrm{cont}}(u)=|u(0)|^2+\|u'\|_{L^2(0,1)}^2
\]
controls the physical error and restores convergence to \(u^\star=0\).

### Proof

For almost every \(x\in(0,1)\), the fundamental theorem of calculus for Sobolev functions gives
\[
u(x)=u(0)+\int_0^x u'(s)\,ds.
\]
By \((a+b)^2\le 2a^2+2b^2\) and Cauchy-Schwarz,
\[
|u(x)|^2
\le 2|u(0)|^2+2\left(\int_0^x |u'(s)|\,ds\right)^2
\le 2|u(0)|^2+2\|u'\|_{L^2(0,1)}^2.
\]
Integrating over \(x\in(0,1)\) proves the bound.

Therefore, if \(|u_k(0)|\to 0\) and \(\|u_k'\|_{L^2}\to 0\), then \(\|u_k-u^\star\|_{L^2}\to 0\). The same ODE is stable under the continuous derivative residual; the failure in Theorem A comes from sampling the residual at fixed finite points.

For the bad sequence,
\[
\|u_n'\|_{L^2(0,1)}^2
=\int_0^1(\pi mn)^2\sin^2(2\pi mnx)\,dx
=\frac{(\pi mn)^2}{2},
\]
so the continuous certificate detects the hidden oscillation.

## Theorem C: Sampled Fill-Distance Plus Regularity Certificate

Let \(m\ge 1\), \(h=1/m\), and \(x_j=jh\), \(j=0,\ldots,m\). For every \(u\in H^2(0,1)\),
\[
\|u'\|_{L^2(0,1)}^2
\le 2h\sum_{j=0}^{m-1}|u'(x_j)|^2+2h^2\|u''\|_{L^2(0,1)}^2.
\]
Consequently,
\[
\|u\|_{L^2(0,1)}^2
\le 2|u(0)|^2
   +4h\sum_{j=0}^{m-1}|u'(x_j)|^2
   +4h^2\|u''\|_{L^2(0,1)}^2.
\]

### Proof

Set \(v=u'\). Since \(u\in H^2(0,1)\), \(v\in H^1(0,1)\) and point values are well-defined by the one-dimensional Sobolev representative. On each cell \(I_j=[x_j,x_{j+1}]\),
\[
v(x)=v(x_j)+\int_{x_j}^x v'(s)\,ds.
\]
Using \((a+b)^2\le 2a^2+2b^2\) and Cauchy-Schwarz,
\[
|v(x)|^2
\le 2|v(x_j)|^2
+2(x-x_j)\int_{I_j}|v'(s)|^2\,ds
\le 2|v(x_j)|^2+2h\int_{I_j}|v'(s)|^2\,ds.
\]
Integrating over \(I_j\) gives
\[
\int_{I_j}|v(x)|^2\,dx
\le 2h|v(x_j)|^2+2h^2\int_{I_j}|v'(s)|^2\,ds.
\]
Summing over \(j=0,\ldots,m-1\) yields
\[
\|u'\|_{L^2(0,1)}^2
\le 2h\sum_{j=0}^{m-1}|u'(x_j)|^2+2h^2\|u''\|_{L^2(0,1)}^2.
\]
Combining this with Theorem B proves the sampled certificate estimate.

For \(u_n(x)=\sin^2(\pi mnx)\), the left-node derivative samples vanish:
\[
u_n'(x_j)=\pi mn\sin(2\pi nj)=0,\qquad j=0,\ldots,m-1.
\]
However,
\[
u_n''(x)=2(\pi mn)^2\cos(2\pi mnx),
\]
and therefore
\[
\|u_n''\|_{L^2(0,1)}^2=2(\pi mn)^4.
\]
The regularity part of the sampled certificate is
\[
4h^2\|u_n''\|_{L^2}^2
=8\pi^4 m^2 n^4,
\]
which grows with the hidden oscillation. The fill-distance certificate repairs the blind spot by charging the between-node variation of the sampled residual.

## Scope

The result is deliberately limited. It shows that fixed finite collocation over unrestricted smooth or \(H^2\) trial functions can be noncoercive even for the ODE \(u'=0\). It does not show that continuous residual minimization fails, and it does not show that practical PINNs fail in general. It does show that sampled residual values alone are not a global certificate unless paired with a norming-set, quadrature, fill-distance, or regularity condition.
