---
created: 2026-05-15T00:45:00Z
cycle: 4
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Transformed Series Collapse

This note attacks the remaining product-transform bottleneck:

\[
H_{\alpha,N}(q)=\sum_{n=0}^N q^{n^2+\alpha n}{(q;q)_N\over(q;q)_n},
\qquad \alpha\in\{0,1\}.
\]

The intended limit is

\[
\lim_{N\to\infty}H_{0,N}
=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2},
\qquad
\lim_{N\to\infty}H_{1,N}
=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

The second exponent is \(j(5j-3)/2\), matching the validated
\((Q,z)=(q^5,q)\) Jacobi specialization from the product-transform route.

## Finite Signed Objects

For \(0\le n\le N\),

\[
{(q;q)_N\over(q;q)_n}=\prod_{s=n+1}^N(1-q^s)
=\sum_{S\subseteq\{n+1,\ldots,N\}}(-1)^{|S|}q^{\sum_{s\in S}s}.
\]

Therefore

\[
H_{\alpha,N}
=\sum_{n=0}^N\sum_{S\subseteq\{n+1,\ldots,N\}}
(-1)^{|S|}q^{n^2+\alpha n+\sum_{s\in S}s}.
\]

Thus each term is a signed object \((n,S,\alpha,N)\) with weight

\[
w_\alpha(n,S)=n^2+\alpha n+\sum_{s\in S}s
\]

and sign \((-1)^{|S|}\). This proves the finite signed-object expansion
used by `scripts/rr/transformed_cancellation_probe.wls`.

## Hard Filter For Boundary Moves

Any weight-preserving move from \(n\) to \(n+r\) must remove selected tail
parts of total weight

\[
(n+r)^2+\alpha(n+r)-n^2-\alpha n=r(2n+\alpha+r).
\]

Similarly, any move from \(n\) to \(n-r\) must add tail parts of total
weight

\[
n^2+\alpha n-(n-r)^2-\alpha(n-r)=r(2n+\alpha-r).
\]

The probe tested the natural local family forced by the moving boundary:
increase \(n\) only by absorbing selected parts at or below the new
boundary, and decrease \(n\) only by releasing missing parts between the
new and old boundary. The hard filter above was applied before any move
was accepted.

This local family is rejected as a complete sign-reversing involution.
For the main run `KMAX=40, NMAX=12`, the summary was:

| alpha | N | objects tested | paired | unpaired | not involutive | not weight preserving | not sign reversing |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 12 | 4059 | 2172 | 1887 | 0 | 0 | 0 |
| 1 | 12 | 3865 | 0 | 3865 | 0 | 0 | 0 |

The zero failure counts for weight, sign, and involutivity mean accepted
moves were internally valid; the obstruction is lack of totality. Minimal
unpaired examples include the constant object \((0,\varnothing)\), which
should be fixed, but also non-fixed low objects such as
\((\alpha,N,n,S)=(0,2,0,\{2\})\) at weight \(2\). Hence this local
absorb/release rule is not the missing cancellation proof.

## Survivor Pattern

The signed coefficients of \(H_{\alpha,N}\) show the expected finite
boundary behavior. For `NMAX=12`, the nonzero signed coefficient degrees
reported by the probe begin as

\[
\alpha=0:\quad 0,2,3,9,11,\ldots
\]

and

\[
\alpha=1:\quad 0,1,4,7,\ldots .
\]

These are exactly the early exponents \(j(5j-1)/2\) and \(j(5j-3)/2\)
before boundary corrections begin. The same run also records additional
degrees above the stabilization boundary; those are finite-\(N\) boundary
terms, not limiting survivors.

![Signed survivor pattern for \(H_{\alpha,N}\); x-axis is coefficient degree \(k\), y-axis is signed coefficient, blue bars mark bilateral pentagonal-support degrees, and finite boundary corrections begin above the low-degree stabilization range.](../../data/finite_experiments/transformed_cancellation_survivors.png)

## Recurrence Fallback

The finite recurrence from the product-transform route remains valid:

\[
H_{\alpha,N}=(1-q^N)H_{\alpha,N-1}+q^{N^2+\alpha N},
\qquad H_{\alpha,0}=1.
\]

Equivalently,

\[
H_{\alpha,N}-H_{\alpha,N-1}
=-q^N H_{\alpha,N-1}+q^{N^2+\alpha N}.
\]

This proves coefficient stabilization: for fixed \(K\), the coefficients
through degree \(K\) stop changing once \(N>K\), because the right-hand
side has lowest degree at least \(N\). Therefore the limit

\[
H_\alpha(q)=\lim_{N\to\infty}H_{\alpha,N}(q)
\]

exists coefficientwise and equals

\[
\sum_{n\ge0}q^{n^2+\alpha n}(q^{n+1};q)_\infty.
\]

This recurrence explains why naive finite bilateral comparisons first
fail at the moving boundary, but it does not identify the stabilized
coefficients with the bilateral pentagonal series. A proof-bearing
recurrence route still needs extra shifted or modulo-five states; the
single scalar recurrence is insufficient.

## Status

This cycle proves the finite signed-object expansion and rejects one
natural local involution family. It does not prove the transformed-series
collapse. The next proof attempt should either search for a nonlocal
sign-reversing involution or build a finite state system whose limiting
solution is uniquely the bilateral pentagonal-support series.
