---
created: 2026-05-15T03:20:00Z
cycle: 9
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M3
---

# Product-Side Formalization

This note closes the product-side step after the validated Bailey-matrix
transfer. All equalities are in \(\mathbb Z[[q]]\).

## Formal Products and Units

For \(d\ge1\) and \(r\ge1\), write

\[
(q^r;q^d)_\infty=\prod_{m\ge0}(1-q^{r+dm}).
\]

For several starting exponents,

\[
(q^{r_1},\ldots,q^{r_t};q^d)_\infty
=\prod_{i=1}^t(q^{r_i};q^d)_\infty.
\]

Every factor has constant term \(1\), and for any fixed coefficient
degree only finitely many factors can contribute. Thus these products are
well-defined formal power series with constant term \(1\), hence units in
\(\mathbb Z[[q]]\). Cancellation below is multiplication by these formal
inverses, not analytic division.

## Euler Factorization by Residue Class

The positive integers split uniquely into the five residue classes
\(1,2,3,4,0\pmod 5\). Therefore

\[
(q;q)_\infty
=(q,q^2,q^3,q^4,q^5;q^5)_\infty.
\]

This is a coefficientwise regrouping of the same formal product; each
coefficient sees only finitely many factors.

## Transformed Series

Let

\[
S_1(q)=\sum_{n\ge0}\frac{q^{n^2}}{(q;q)_n},
\qquad
S_2(q)=\sum_{n\ge0}\frac{q^{n^2+n}}{(q;q)_n}.
\]

By the validated Bailey-matrix transfer L33-L36,

\[
S_1(q)=
\frac{1}{(q;q)_\infty}
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2},
\]

and

\[
S_2(q)=
\frac{1}{(q;q)_\infty}
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

The second formula uses the cancellation
\((1-q)(q^2;q)_\infty=(q;q)_\infty\), already included in L36.

By the derived Jacobi product identity L14, specialized with
\(Q=q^5\), first \(z=q^2\) and then \(z=q\),

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2}
=(q^2,q^3,q^5;q^5)_\infty,
\]

\[
\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}
=(q,q^4,q^5;q^5)_\infty.
\]

Hence

\[
(q;q)_\infty S_1(q)=(q^2,q^3,q^5;q^5)_\infty,
\qquad
(q;q)_\infty S_2(q)=(q,q^4,q^5;q^5)_\infty.
\]

## Formal Cancellation

Using the Euler factorization,

\[
S_1(q)
=\frac{(q^2,q^3,q^5;q^5)_\infty}
{(q,q^2,q^3,q^4,q^5;q^5)_\infty}
=\frac{1}{(q,q^4;q^5)_\infty}.
\]

The factors with residues \(2,3,0\pmod 5\) cancel, leaving exactly the
inverse factors with residues \(1\) and \(4\pmod 5\).

Similarly,

\[
S_2(q)
=\frac{(q,q^4,q^5;q^5)_\infty}
{(q,q^2,q^3,q^4,q^5;q^5)_\infty}
=\frac{1}{(q^2,q^3;q^5)_\infty}.
\]

The factors with residues \(1,4,0\pmod 5\) cancel, leaving exactly the
inverse factors with residues \(2\) and \(3\pmod 5\).

Translating the compact notation gives the target products:

\[
S_1(q)
=\prod_{m\ge0}
\frac{1}{(1-q^{5m+1})(1-q^{5m+4})},
\]

\[
S_2(q)
=\prod_{m\ge0}
\frac{1}{(1-q^{5m+2})(1-q^{5m+3})}.
\]

No numerical coefficient check is used in this proof; the companion script
`scripts/rr/product_side_formal_check.wls` is only a regression check for
transcription of the displayed products and exponents.
