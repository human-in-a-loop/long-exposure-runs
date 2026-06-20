---
created: 2026-05-14T23:55:00Z
cycle: 2
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Q-Difference Mechanism

This note proves the series-side q-difference ladder in the formal series ring `Z[[z,q]]`, proves uniqueness under a coefficientwise tail condition, and records the current product-side obstruction.

## Auxiliary Series

Define

\[
F(z,q)=\sum_{n\ge0}\frac{z^n q^{n^2}}{(q;q)_n}.
\]

For any fixed total `q`-degree bound `K`, only `n<=floor(sqrt(K))` contributes to coefficients through degree `K`; each denominator has constant term `1`. Thus the expression is well-defined coefficientwise in `Z[z][[q]]`, and the specializations below are valid formal power series.

## L8. Auxiliary Q-Difference Identity

**Status:** `proved`

\[
F(z,q)-F(zq,q)=zqF(zq^2,q).
\]

Proof:

\[
F(z,q)-F(zq,q)
=\sum_{n\ge0}\frac{z^nq^{n^2}(1-q^n)}{(q;q)_n}.
\]

The `n=0` term is zero. For `n>=1`, `(1-q^n)/(q;q)_n=1/(q;q)_{n-1}`. Reindex with `m=n-1`:

\[
\sum_{n\ge1}\frac{z^nq^{n^2}}{(q;q)_{n-1}}
=\sum_{m\ge0}\frac{z^{m+1}q^{(m+1)^2}}{(q;q)_m}
=zq\sum_{m\ge0}\frac{(zq^2)^m q^{m^2}}{(q;q)_m}
=zqF(zq^2,q).
\]

Every step is coefficientwise finite through any fixed `q`-degree, so the identity holds formally.

## L9. Infinite Ladder

**Status:** `proved`

Let

\[
A_r(q)=F(q^r,q)=\sum_{n\ge0}\frac{q^{n^2+rn}}{(q;q)_n}.
\]

Specializing L8 at `z=q^r` gives

\[
A_r=A_{r+1}+q^{r+1}A_{r+2},\qquad r\ge0.
\]

The target series are `A_0=S_1` and `A_1=S_2`.

## L10. Tail-Normalized Uniqueness

**Status:** `proved`

There is at most one sequence `(C_r)_{r>=0}` in `Z[[q]]` satisfying

\[
C_r=C_{r+1}+q^{r+1}C_{r+2}
\]

and the coefficientwise tail condition

\[
\forall K\ge0,\quad C_r\equiv 1\pmod {q^{K+1}}\quad\text{for all sufficiently large }r.
\]

Proof: suppose `(C_r)` and `(D_r)` both satisfy the recurrence and tail condition, and set `E_r=C_r-D_r`. Then

\[
E_r=E_{r+1}+q^{r+1}E_{r+2}
\]

and for each `K`, `E_r≡0 mod q^(K+1)` for all sufficiently large `r`. Fix a coefficient bound `K` and choose `R>=K+1` such that `E_R` and `E_{R+1}` vanish modulo `q^(K+1)`. The recurrence run backward determines `E_{R-1},E_{R-2},...,E_0` modulo `q^(K+1)` from these two zero tails, so each is also zero modulo `q^(K+1)`. Since `K` is arbitrary, all coefficients of every `E_r` vanish. Hence `C_r=D_r`.

Existence is given by the explicit series `A_r`: for fixed `K`, all `n>=1` terms in `A_r` have degree at least `r+1`, so `A_r≡1 mod q^(K+1)` whenever `r>=K`.

## Product-Side Status

The ladder uniquely characterizes the two Rogers-Ramanujan series once the tail condition is accepted. It does not yet prove either product identity, because the residue products have only supplied two initial candidates:

\[
P_1=\prod_{m\ge0}(1-q^{5m+1})^{-1}(1-q^{5m+4})^{-1},\quad
P_2=\prod_{m\ge0}(1-q^{5m+2})^{-1}(1-q^{5m+3})^{-1}.
\]

Starting with `B_0=P_1`, `B_1=P_2`, the recurrence formally forces

\[
B_{r+2}=q^{-(r+1)}(B_r-B_{r+1}).
\]

The computational probe shows this forced sequence matches the tail-normalized backsolve through degree `40` for `r<=14`, and the forced tail has first nonconstant term at the expected degree scale, but this is diagnostic only. The missing proof step is a product-side construction of all `B_r` with the same ladder and coefficientwise tail, or an equivalent finite product identity that implies the same boundary-value problem.

Current status: series-side ladder and uniqueness are proved; product-side closure remains open. This is a partial M2 success and points to the finite largest-part recurrence route as the next mechanism to derive a product-side bridge.
