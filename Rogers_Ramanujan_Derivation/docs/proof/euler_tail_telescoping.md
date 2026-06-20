---
created: 2026-05-15T01:30:00Z
cycle: 6
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Euler-Tail Telescoping Probe

This note tests a new mechanism for the remaining transformed-series
collapse. It does not prove the Rogers-Ramanujan identities. It proves the
Euler-tail double-sum reduction and rejects the low-order rational
telescoping ansatz tested by `scripts/rr/euler_tail_telescoping_probe.wls`.

## Euler-Tail Expansion

The finite q-binomial theorem from L13 gives

\[
(z;q)_M=\sum_{k=0}^{M}(-1)^kq^{k(k-1)/2}{M\brack k}_qz^k.
\]

Set \(z=q^{n+1}\). For fixed coefficient degree \(d\), terms with
\(k(k+1)/2+kn>d\) cannot contribute, and the Gaussian coefficient
\({M\brack k}_q\) stabilizes coefficientwise to \((q;q)_k^{-1}\) once
\(M\) is large enough. Therefore, in \(\mathbb Z[[q]]\),

\[
(q^{n+1};q)_\infty
=
\sum_{k\ge0}\frac{(-1)^kq^{k(k+1)/2+kn}}{(q;q)_k}.
\]

Also,

\[
(q;q)_\infty\frac{q^{n^2+\alpha n}}{(q;q)_n}
=q^{n^2+\alpha n}(q^{n+1};q)_\infty.
\]

Thus the transformed series is

\[
T_\alpha(q)=
\sum_{n,k\ge0}
\frac{(-1)^kq^{n^2+\alpha n+kn+k(k+1)/2}}{(q;q)_k}.
\]

The target remains

\[
T_0(q)=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-1)/2},
\qquad
T_1(q)=\sum_{j\in\mathbb Z}(-1)^jq^{j(5j-3)/2}.
\]

## Certificate Ansatz Tested

Write

\[
F_\alpha(n,k)=
\frac{(-1)^kq^{n^2+\alpha n+kn+k(k+1)/2}}{(q;q)_k},
\quad x=q^n,\quad y=q^k.
\]

The probe tests forward-divergence certificates

\[
F_\alpha(n,k)
=U_\alpha(n,k)-U_\alpha(n+1,k)
+V_\alpha(n,k)-V_\alpha(n,k+1)+R_\alpha(n,k),
\]

with \(U=A(x,y)F_\alpha(n,k)\) and \(V=B(x,y)F_\alpha(n,k)\). The
normalized interior condition is the rational identity

\[
A(x,y)-q^{\alpha+1}x^2yA(qx,y)
+B(x,y)+\frac{qxy}{1-qy}B(x,qy)=1.
\]

The tested ansatz takes \(A\) and \(B\) to be polynomials in \(x,y\) of
total degree at most `DegMax`, with coefficients solved over rational
functions in \(q\). As a first mod-5 diagnostic, it also tests polynomial
monomial support restricted to the congruence-compatible slices

\[
2n+k+\alpha\equiv r\pmod 5.
\]

Each candidate is checked by clearing the denominator \(1-qy\) and solving
the resulting polynomial coefficient equations exactly. Coefficient
agreement is not used to accept a certificate.

## Result

For the main run

```bash
KMAX=40 NMAX=16 DEGMAX=3 OUTDIR=data/finite_experiments wolfram-batch -script scripts/rr/euler_tail_telescoping_probe.wls
```

the probe tested `48` symbolic candidates and found `0` solutions. The
small repro

```bash
KMAX=12 NMAX=8 DEGMAX=2 OUTDIR=data/finite_experiments/test_euler_tail_k12 wolfram-batch -script scripts/rr/euler_tail_telescoping_probe.wls
```

tested `36` candidates and again found `0` solutions.

The same runs also compute finite double-sum truncations. These match the
corrected bilateral targets through the checked degrees (`KMAX=40` in the
main run and `KMAX=12` in the repro), but that is only a consistency check
for the Euler-tail expansion and truncation bounds.

## Obstruction Recorded

This cycle rejects a low-order rational divergence certificate of the
form above, including the first mod-5 monomial-support diagnostic using
\(2n+k+\alpha\). The obstruction is exact: after clearing denominators,
the polynomial coefficient equations have no solution in the tested
ansatz classes.

This does not rule out telescoping with:

- rational functions with nontrivial denominators beyond \(1-q^k\);
- truly piecewise mod-5 certificates rather than monomial-support slices;
- a different linear coordinate system;
- certificates with an additional summation parameter;
- boundary terms built into the ansatz rather than a zero interior
  residual.

The next proof-bearing attempt should therefore either enlarge the
certificate class in one of those concrete ways or pivot to the direct
partition-bijection fallback.
