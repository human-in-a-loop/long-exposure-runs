---
created: 2026-05-15T00:25:00Z
cycle: 3
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Product Transform Route

This note records the Euler-product and finite q-binomial part of the
product-transform mechanism. It deliberately separates proved product
algebra from the still-open collapse of the transformed Rogers-Ramanujan
series.

## Euler Complement Reduction

Write

\[
E(q)=(q;q)_\infty=\prod_{m\ge1}(1-q^m).
\]

In formal coefficientwise products, each coefficient depends on only
finitely many factors. Splitting factors by residues modulo 5 gives

\[
E(q)=
(q;q^5)_\infty(q^2;q^5)_\infty(q^3;q^5)_\infty
(q^4;q^5)_\infty(q^5;q^5)_\infty.
\]

Therefore the first Rogers-Ramanujan identity is equivalent, after
multiplication by the invertible series \(E(q)\), to

\[
E(q)\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}
=
(q^2;q^5)_\infty(q^3;q^5)_\infty(q^5;q^5)_\infty.
\]

Similarly the second identity is equivalent to

\[
E(q)\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}
=
(q;q^5)_\infty(q^4;q^5)_\infty(q^5;q^5)_\infty.
\]

The cancellation is legitimate because all products have constant term
1 and are units in \(\mathbb Z[[q]]\).

## Finite q-Binomial Theorem

For \(N\ge0\), define Gaussian binomial coefficients by

\[
{N\brack k}_Q =
\frac{(1-Q^N)(1-Q^{N-1})\cdots(1-Q^{N-k+1})}
{(1-Q)(1-Q^2)\cdots(1-Q^k)}
\]

for \(0\le k\le N\), and \(0\) otherwise. They are polynomials because
they satisfy Pascal's recurrence

\[
{N\brack k}_Q={N-1\brack k}_Q+Q^{N-k}{N-1\brack k-1}_Q,
\]

with boundary values \({N\brack0}_Q={N\brack N}_Q=1\).

Let

\[
P_N(z)=(z;Q)_N=\prod_{r=0}^{N-1}(1-zQ^r).
\]

The expansion

\[
(z;Q)_N=\sum_{k=0}^N
(-1)^kQ^{k(k-1)/2}{N\brack k}_Q z^k
\]

follows by induction. Multiplying \(P_{N-1}(z)\) by \(1-zQ^{N-1}\),
the coefficient of \(z^k\) becomes

\[
(-1)^kQ^{k(k-1)/2}
\left({N-1\brack k}_Q+Q^{N-k}{N-1\brack k-1}_Q\right),
\]

which is exactly Pascal's recurrence.

## Derived Finite Jacobi Identity

The finite identity

\[
(z;Q)_N(Q/z;Q)_N
=
\sum_{j=-N}^{N}(-1)^jz^jQ^{j(j-1)/2}
{2N\brack N+j}_Q
\]

is obtained by multiplying the two finite q-binomial expansions and then
collecting the coefficient of \(z^j\). The required convolution is the
finite Vandermonde identity

\[
\sum_b Q^{b(b+j)}{N\brack b}_Q{N\brack b+j}_Q
=
{2N\brack N+j}_Q,
\]

where terms outside `0 <= b,b+j <= N` are zero. This convolution is
proved by the same Gaussian Pascal recurrence, now with the index
difference \(j\) fixed. Equivalently, both sides have the same
Laurent-polynomial boundary value at \(N=0\) and the collected
coefficients satisfy the recurrence forced by multiplication by
\((1-zQ^N)(1-Q^N/z)\).

For each fixed Laurent monomial \(z^aQ^b\), the coefficient of
\({2N\brack N+j}_Q\) stabilizes coefficientwise to \((Q;Q)_\infty^{-1}\)
as \(N\to\infty\). Hence

\[
(z;Q)_\infty(Q/z;Q)_\infty(Q;Q)_\infty
=
\sum_{j\in\mathbb Z}(-1)^jz^jQ^{j(j-1)/2}.
\]

This is used here as a derived product identity, not as a cited theorem.

## Specializations

Set \(Q=q^5\). With \(z=q^2\),

\[
z^jQ^{j(j-1)/2}=q^{2j+5j(j-1)/2}=q^{j(5j-1)/2},
\]

so

\[
(q^2;q^5)_\infty(q^3;q^5)_\infty(q^5;q^5)_\infty
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}.
\]

With \(z=q\),

\[
z^jQ^{j(j-1)/2}=q^{j+5j(j-1)/2}=q^{j(5j-3)/2},
\]

so

\[
(q;q^5)_\infty(q^4;q^5)_\infty(q^5;q^5)_\infty
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

Thus the product sides are now reduced to explicit bilateral sums by
finite q-binomial algebra and coefficientwise stabilization.

## Transformed Series Status

The remaining proof obligation is

\[
E(q)\sum_{n\ge0}\frac{q^{n^2+\alpha n}}{(q;q)_n}
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-(2\alpha+1))/2}
\]

for \(\alpha=0,1\). The finite approximants used in this cycle are

\[
H_{\alpha,N}=\sum_{n=0}^N q^{n^2+\alpha n}
\frac{(q;q)_N}{(q;q)_n}.
\]

They satisfy the exact recurrence

\[
H_{\alpha,N}=(1-q^N)H_{\alpha,N-1}+q^{N^2+\alpha N},
\qquad H_{\alpha,0}=1.
\]

This recurrence is immediate by separating the \(n=N\) term and factoring
\((q;q)_N=(1-q^N)(q;q)_{N-1}\) in all earlier terms. It proves that
\(H_{\alpha,N}\) has a coefficientwise limit equal to the Euler-multiplied
series, but it does not by itself identify that limit with the bilateral
sum. The probe in `scripts/rr/product_transform_probe.wls` records the
finite candidate searches and the exact obstruction.
