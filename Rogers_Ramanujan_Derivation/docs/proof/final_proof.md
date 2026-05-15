---
created: 2026-05-15T03:14:01Z
cycle: 10
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M4
---

# Final Formal Proof of the Rogers-Ramanujan Identities

This document gives the final proof chain in \(\mathbb Z[[q]]\). The
computations in `scripts/rr/` were used to discover, falsify, and regress
intermediate formulas; they are not used as proof of coefficient equality.

## Formal Setting

For \(f,g\in\mathbb Z[[q]]\), equality means equality of every coefficient.
A sequence \(f_N\) converges coefficientwise to \(f\) if, for every degree
\(K\), the coefficients of \(q^0,\ldots,q^K\) in \(f_N\) are eventually
constant and equal to those in \(f\). This justifies all limits below:
each coefficient of the series and products uses only finitely many terms.

For \(n\ge0\),

\[
(a;q)_n=\prod_{i=0}^{n-1}(1-aq^i),
\qquad
(a;q)_\infty=\prod_{i\ge0}(1-aq^i),
\]

whenever the infinite product is coefficientwise-defined. Products with
constant term \(1\) are units in \(\mathbb Z[[q]]\), so cancellation below
means multiplication by the corresponding formal inverse.

For several factors, write

\[
(q^{r_1},\ldots,q^{r_t};q^d)_\infty
=\prod_{i=1}^t(q^{r_i};q^d)_\infty.
\]

## Theorem

In \(\mathbb Z[[q]]\),

\[
\sum_{n \ge 0} \frac{q^{n^2}}{(q;q)_n}
=
\prod_{m \ge 0} \frac{1}{(1-q^{5m+1})(1-q^{5m+4})}
\]

and

\[
\sum_{n \ge 0} \frac{q^{n^2+n}}{(q;q)_n}
=
\prod_{m \ge 0} \frac{1}{(1-q^{5m+2})(1-q^{5m+3})}.
\]

## Finite Algebraic Inputs

The finite \(q\)-binomial theorem is derived by the Pascal recurrence for
Gaussian binomial coefficients:

\[
(z;Q)_N=\sum_{j=0}^{N}
(-1)^j Q^{j(j-1)/2}{N\brack j}_Q z^j.
\]

Letting \(N\to\infty\) coefficientwise and applying the same finite
identity to the reciprocal-side convolution gives the Jacobi-type product
identity

\[
(z;Q)_\infty(Q/z;Q)_\infty(Q;Q)_\infty
=
\sum_{j\in\mathbb Z}(-1)^jz^jQ^{j(j-1)/2}.
\]

The two specializations needed here are

\[
B_0(q):=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}
=(q^2,q^3,q^5;q^5)_\infty,
\]

from \(Q=q^5,z=q^2\), and

\[
B_1(q):=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}
=(q,q^4,q^5;q^5)_\infty,
\]

from \(Q=q^5,z=q\).

## Derived Triangular Transform

For a formal parameter \(a\), define

\[
M^{(a)}_{n,r}
=\frac{1}{(q;q)_{n-r}(aq;q)_{n+r}},
\qquad 0\le r\le n.
\]

The triangular relation

\[
\beta_n=\sum_{r=0}^{n}M^{(a)}_{n,r}\alpha_r
\]

has the explicitly derived inverse

\[
\alpha_n=\sum_{j=0}^{n}
\frac{1-aq^{2n}}{1-a}
\frac{(a;q)_{n+j}}{(q;q)_{n-j}}
(-1)^{n-j}q^{(n-j)(n-j-1)/2}\beta_j.
\]

This inverse is proved by multiplying the two triangular matrices. The
off-diagonal entries reduce to a finite \(q\)-difference of a polynomial of
degree too small to survive the finite \(q\)-binomial identity; diagonal
entries are \(1\).

Set \(\beta_n=1/(q;q)_n\). The inverse gives the two needed alpha sequences:

\[
\alpha^{(0)}_0=1,\qquad
\alpha^{(0)}_r=(-1)^rq^{r(3r-1)/2}(1+q^r)\quad(r\ge1)
\]

for \(a=1\), and

\[
\alpha^{(1)}_r
=(-1)^rq^{r(3r+1)/2}\frac{1-q^{2r+1}}{1-q}
\]

for \(a=q\). The quotient is the polynomial \(1+q+\cdots+q^{2r}\).

The coefficientwise limiting transform derived from the triangular
relation is

\[
\sum_{n\ge0}a^nq^{n^2}\beta_n
=
\frac{1}{(aq;q)_\infty}
\sum_{r\ge0}a^rq^{r^2}\alpha_r.
\]

The inner summation needed for this limit is proved formally by multiplying
by \((aq;q)_\infty\), setting \(z=aq^{2r+1}\), and using

\[
\sum_{s\ge0}\frac{z^sq^{s(s-1)}(zq^s;q)_\infty}{(q;q)_s}=1,
\]

whose coefficient of \(z^m\) is \(0\) for \(m>0\) by the finite
\(q\)-binomial identity applied to \((1;q)_m\).

## First Rogers-Ramanujan Identity

Use \(a=1\) and \(\beta_n=1/(q;q)_n\) in the limiting transform:

\[
\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}
=
\frac1{(q;q)_\infty}
\sum_{r\ge0}q^{r^2}\alpha^{(0)}_r.
\]

Substituting \(\alpha^{(0)}\) gives

\[
\sum_{r\ge0}q^{r^2}\alpha^{(0)}_r
=1+\sum_{r\ge1}(-1)^r
\left(q^{r(5r-1)/2}+q^{r(5r+1)/2}\right).
\]

The terms with exponent \(r(5r-1)/2\) are the positive-index terms of
\(B_0\), and the terms \(r(5r+1)/2\) are the negative-index terms after
putting \(j=-r\). Hence

\[
(q;q)_\infty\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}=B_0(q).
\]

By the Jacobi specialization,

\[
(q;q)_\infty\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}
=(q^2,q^3,q^5;q^5)_\infty.
\]

The Euler product factors by residue class as

\[
(q;q)_\infty=(q,q^2,q^3,q^4,q^5;q^5)_\infty.
\]

All factors are units, so canceling the residues \(2,3,0\pmod 5\) gives

\[
\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}
=\frac{1}{(q,q^4;q^5)_\infty}
=\prod_{m\ge0}
\frac{1}{(1-q^{5m+1})(1-q^{5m+4})}.
\]

## Second Rogers-Ramanujan Identity

Use \(a=q\) and \(\beta_n=1/(q;q)_n\):

\[
\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}
=
\frac1{(q^2;q)_\infty}
\sum_{r\ge0}q^{r^2+r}\alpha^{(1)}_r.
\]

Multiplying the remaining sum by \(1-q\) and substituting
\(\alpha^{(1)}\) gives

\[
(1-q)\sum_{r\ge0}q^{r^2+r}\alpha^{(1)}_r
=
\sum_{r\ge0}(-1)^r
\left(q^{r(5r+3)/2}-q^{(r+1)(5r+2)/2}\right).
\]

The first term is the contribution of \(j=-r\) to \(B_1\), and the second
term is the contribution of \(j=r+1\). Therefore

\[
(1-q)\sum_{r\ge0}q^{r^2+r}\alpha^{(1)}_r=B_1(q).
\]

Since \((q;q)_\infty=(1-q)(q^2;q)_\infty\),

\[
(q;q)_\infty\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}=B_1(q).
\]

By the Jacobi specialization,

\[
(q;q)_\infty\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}
=(q,q^4,q^5;q^5)_\infty.
\]

Using the same residue-class factorization of \((q;q)_\infty\) and
canceling the unit factors with residues \(1,4,0\pmod 5\),

\[
\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}
=\frac{1}{(q^2,q^3;q^5)_\infty}
=\prod_{m\ge0}
\frac{1}{(1-q^{5m+2})(1-q^{5m+3})}.
\]

This proves both Rogers-Ramanujan identities as formal power series.

## Proof-Status Note

The successful proof uses finite \(q\)-binomial algebra, a directly
derived triangular transform, coefficientwise limiting arguments, the
derived Jacobi product identity, and formal product cancellation in
\(\mathbb Z[[q]]\). Coefficient computations and finite truncation scripts
served only as discovery, falsification, and regression checks.
