---
created: 2026-05-15T02:45:00Z
cycle: 8
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Derived Bailey-Style Matrix Transform

This note closes the remaining transformed-series gap by deriving the
needed triangular transform directly. The name "Bailey-style" is only a
description of shape; the transform, inverse, and limiting step below are
proved here from finite q-binomial algebra.

## Finite Transform

For a parameter \(a\) with \(1-a\) treated formally during the derivation,
define the lower triangular matrix

\[
M^{(a)}_{n,r}=
\frac{1}{(q;q)_{n-r}(a q;q)_{n+r}},
\qquad 0\le r\le n.
\]

The relation is

\[
\beta_n=\sum_{r=0}^n M^{(a)}_{n,r}\alpha_r.
\]

Since the diagonal entries \(M^{(a)}_{n,n}=1/(a q;q)_{2n}\) are units,
the relation has a unique triangular inverse.

## Inverse Matrix from Finite q-Binomial Algebra

For \(n\ge0\), set

\[
N^{(a)}_{n,j}=
\frac{1-aq^{2n}}{1-a}
\frac{(a;q)_{n+j}}{(q;q)_{n-j}}
(-1)^{n-j}q^{(n-j)(n-j-1)/2},
\qquad 0\le j\le n.
\]

Then

\[
\alpha_n=\sum_{j=0}^n N^{(a)}_{n,j}\beta_j.
\]

To prove this, multiply \(N^{(a)}M^{(a)}\). The \((n,r)\) entry is

\[
\sum_{j=r}^n
\frac{1-aq^{2n}}{1-a}
\frac{(a;q)_{n+j}}{(q;q)_{n-j}}
(-1)^{n-j}q^{(n-j)(n-j-1)/2}
\frac{1}{(q;q)_{j-r}(a q;q)_{j+r}}.
\]

For \(n=r\) this is \(1\). For \(n>r\), put \(m=n-r\) and \(k=n-j\). After
cancelling \((a;q)_{n+j}/(a q;q)_{j+r}\), the remaining sum is a finite
\(m\)-th q-difference of a polynomial in \(q^{-k}\) of degree \(m-1\):

\[
(1-aq^{2n})\sum_{k=0}^{m}
\frac{(-1)^kq^{k(k-1)/2}}{(q;q)_k(q;q)_{m-k}}
(a q^{n+r-k+1};q)_{m-1}.
\]

Expand the last finite product as a polynomial in \(q^{-k}\). Each monomial
term is killed by the finite q-binomial identity

\[
\sum_{k=0}^{m}(-1)^kq^{k(k-1)/2}{m\brack k}_q q^{-tk}=0,
\qquad 0\le t<m,
\]

which is the finite q-binomial theorem applied to
\((q^{-t};q)_m\); one factor is \(1-q^0\). Thus \(N^{(a)}M^{(a)}=I\), so
the inverse is derived from finite algebra.

## Solved Alpha Sequences

Now set \(\beta_n=1/(q;q)_n\).

For \(a=q\), the inverse gives

\[
\alpha^{(1)}_n=
\frac{1-q^{2n+1}}{1-q}
\sum_{j=0}^n
(-1)^{n-j}q^{(n-j)(n-j-1)/2}
\frac{(q;q)_{n+j}}{(q;q)_{n-j}(q;q)_j}.
\]

The same finite q-binomial evaluation gives

\[
\sum_{j=0}^n
(-1)^{n-j}q^{(n-j)(n-j-1)/2}
\frac{(q;q)_{n+j}}{(q;q)_{n-j}(q;q)_j}
=(-1)^nq^{n(3n+1)/2}.
\]

Therefore

\[
\alpha^{(1)}_n
=
(-1)^nq^{n(3n+1)/2}\frac{1-q^{2n+1}}{1-q}.
\]

For \(a=1\), take the formal limit of the inverse. The case \(n=0\) gives
\(\alpha^{(0)}_0=1\). For \(n\ge1\),

\[
\alpha^{(0)}_n
=(1-q^{2n})\sum_{j=0}^n
(-1)^{n-j}q^{(n-j)(n-j-1)/2}
\frac{(q;q)_{n+j-1}}{(q;q)_{n-j}(q;q)_j}.
\]

The finite q-binomial evaluation of this terminating sum is

\[
\sum_{j=0}^n
(-1)^{n-j}q^{(n-j)(n-j-1)/2}
\frac{(q;q)_{n+j-1}}{(q;q)_{n-j}(q;q)_j}
=
\frac{(-1)^nq^{n(3n-1)/2}}{1-q^n},
\]

so

\[
\alpha^{(0)}_n=(-1)^nq^{n(3n-1)/2}(1+q^n).
\]

The probe `scripts/rr/bailey_matrix_probe.wls` independently solves the
triangular systems and clears denominators in the two defining residuals:

\[
\sum_{r=0}^n
\frac{\alpha^{(0)}_r}{(q;q)_{n-r}(q;q)_{n+r}}
=\frac1{(q;q)_n},
\]

\[
\sum_{r=0}^n
\frac{\alpha^{(1)}_r}{(q;q)_{n-r}(q^2;q)_{n+r}}
=\frac1{(q;q)_n}.
\]

The main run checked all cleared residual numerators as exactly zero for
\(0\le n\le12\), which guards the algebra but is not used as a substitute
for the inverse proof above.

## Coefficientwise Limiting Transform

Assume the triangular relation. Then, as formal series,

\[
\sum_{n\ge0}a^nq^{n^2}\beta_n
=
\sum_{r\ge0}
\alpha_r
\sum_{s\ge0}
\frac{a^{r+s}q^{(r+s)^2}}{(q;q)_s(aq;q)_{s+2r}}.
\]

For each coefficient of \(q^K\), only finitely many pairs \((r,s)\) can
contribute, so the interchange is justified by L1-L2. It remains to prove
the inner sum

\[
\sum_{s\ge0}
\frac{a^sq^{s^2+2rs}}{(q;q)_s(aq;q)_{s+2r}}
=\frac1{(aq;q)_\infty}.
\]

Multiply by \((aq;q)_\infty\) and set \(z=aq^{2r+1}\). The claim becomes

\[
\sum_{s\ge0}\frac{z^sq^{s(s-1)}(zq^s;q)_\infty}{(q;q)_s}=1.
\]

Expanding \((zq^s;q)_\infty\) by the coefficientwise limit of the finite
q-binomial theorem, the coefficient of \(z^m\) is

\[
\frac{(-1)^mq^{m(m-1)/2}}{(q;q)_m}
\sum_{s=0}^m(-1)^sq^{s(s-1)/2}{m\brack s}_q.
\]

This is \(1\) for \(m=0\) and \(0\) for \(m>0\) by
\((1;q)_m=0\). Therefore

\[
\sum_{n\ge0}a^nq^{n^2}\beta_n
=
\frac1{(aq;q)_\infty}
\sum_{r\ge0}a^rq^{r^2}\alpha_r.
\]

## Application to Rogers-Ramanujan

For \(a=1\),

\[
\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n}
=
\frac1{(q;q)_\infty}
\left(
1+\sum_{r\ge1}(-1)^r
\left(q^{r(5r-1)/2}+q^{r(5r+1)/2}\right)
\right).
\]

The parenthesized series is
\(\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}\).
By the previously derived finite Jacobi product identity,

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}
=(q^2;q^5)_\infty(q^3;q^5)_\infty(q^5;q^5)_\infty.
\]

Dividing by \((q;q)_\infty\) leaves exactly the reciprocal product over
parts congruent to \(1\) or \(4\) modulo \(5\).

For \(a=q\),

\[
\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}
=
\frac1{(q^2;q)_\infty}
\sum_{r\ge0}q^{r^2+r}\alpha^{(1)}_r.
\]

Multiplying the remaining sum by \(1-q\) gives

\[
(1-q)\sum_{r\ge0}q^{r^2+r}\alpha^{(1)}_r
=
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

Indeed the first term in \(1-q^{2r+1}\) supplies the negative-index
terms \(j=-r\), while the second supplies the positive-index terms
\(j=r+1\). The derived Jacobi product identity gives

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}
=(q;q^5)_\infty(q^4;q^5)_\infty(q^5;q^5)_\infty.
\]

Since \((q;q)_\infty=(1-q)(q^2;q)_\infty\), division again yields the
reciprocal product over parts congruent to \(2\) or \(3\) modulo \(5\).

## Status

This provides the missing M2 transfer mechanism: the Rogers-Ramanujan
series are converted to the already proved Jacobi complementary products
by a derived finite triangular matrix transform and a coefficientwise
limiting argument. The next document can promote this into M3 product-side
formalization and then into the final proof synthesis.
