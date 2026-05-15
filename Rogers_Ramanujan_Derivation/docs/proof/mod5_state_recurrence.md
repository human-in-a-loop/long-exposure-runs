---
created: 2026-05-15T01:05:00Z
cycle: fork-88b3b9161814-clone-1
run_id: run-2026-05-14T232311Z
agent: worker-clone-1
milestone: M2
---

# Modulo-5 / Shifted-State Recurrence From \(H_{\alpha,N}\)

This branch tests whether the transformed sums

\[
H_{\alpha,N}(q)=\sum_{n=0}^N q^{n^2+\alpha n}{(q;q)_N\over(q;q)_n},
\qquad \alpha\in\{0,1\},
\]

carry a finite modulo-5 or shifted-state recurrence that identifies the
coefficientwise limit without product-side input.

The corrected target bilateral series are

\[
B_0(q)=\sum_{j\in\mathbb Z}(-1)^j q^{j(5j-1)/2},
\qquad
B_1(q)=\sum_{j\in\mathbb Z}(-1)^j q^{j(5j-3)/2}.
\]

Equivalently, the exponent is \(j(5j-(2\alpha+1))/2\).

## Definitions

Write

\[
H_{\alpha,N}(q)=\sum_{k\ge 0}h_{\alpha,N}(k)q^k.
\]

The stable coefficient is

\[
c_\alpha(k)=\lim_{N\to\infty}h_{\alpha,N}(k).
\]

The predicted bilateral coefficient is

\[
b_\alpha(k)=\sum_{j\in\mathbb Z}(-1)^j
\mathbf 1_{k=j(5j-(2\alpha+1))/2}.
\]

For diagonal states, set

\[
T_{\alpha,N}(d)=h_{\alpha,N}(N+d).
\]

## L24. Scalar Polynomial Recurrence

For \(N\ge 1\),

\[
H_{\alpha,N}=(1-q^N)H_{\alpha,N-1}+q^{N^2+\alpha N}.
\]

Proof. Split the defining sum into \(n<N\) and \(n=N\). For \(n<N\),

\[
{(q;q)_N\over(q;q)_n}=(1-q^N){(q;q)_{N-1}\over(q;q)_n}.
\]

The \(n=N\) term is \(q^{N^2+\alpha N}\). This proves the recurrence.

## L25. Coefficient Recurrence

Taking the coefficient of \(q^k\) in L24 gives

\[
h_{\alpha,N}(k)
=h_{\alpha,N-1}(k)-h_{\alpha,N-1}(k-N)
+\mathbf 1_{k=N^2+\alpha N},
\]

with the convention \(h_{\alpha,N-1}(r)=0\) for \(r<0\).

This recurrence is triangular: \(h_{\alpha,N}(k)\) only depends on the
previous row at degrees \(k\) and \(k-N\). It also proves stabilization.
If \(M>k\), then

\[
h_{\alpha,M}(k)-h_{\alpha,M-1}(k)
=-h_{\alpha,M-1}(k-M)
+\mathbf 1_{k=M^2+\alpha M}=0.
\]

Therefore \(h_{\alpha,N}(k)=c_\alpha(k)\) for every \(N\ge k\). In
particular, \(c_\alpha(k)=h_{\alpha,k}(k)\) for \(k>0\), and
\(c_\alpha(0)=1\).

## L26. Shifted Diagonal Recurrence

Set \(k=N+d\) in L25. Then

\[
T_{\alpha,N}(d)
=T_{\alpha,N-1}(d+1)-h_{\alpha,N-1}(d)
+\mathbf 1_{d=N^2+(\alpha-1)N}.
\]

This is exact. It is also the main obstruction to a naive finite shifted
state vector: the update of offset \(d\) requires offset \(d+1\) from the
previous row.

Repeating the formula five times gives

\[
T_{\alpha,N}(d)
=T_{\alpha,N-5}(d+5)
-\sum_{i=0}^4 h_{\alpha,N-1-i}(d+i)
+\sum_{i=0}^4
\mathbf 1_{d+i=(N-i)^2+(\alpha-1)(N-i)}.
\]

Modulo 5 periodicity of \(N\) does not close the system by itself; the
terminal diagonal offset has moved from \(d\) to \(d+5\).

## Mechanism Attempt

The probe `scripts/rr/mod5_state_recurrence_probe.wls` was written to
compute the coefficient table solely from L25. The local Wolfram Engine
could not execute because its license is expired, so the mirror fallback
`scripts/rr/mod5_state_recurrence_probe.py` generated the data. The
fallback implements the same recurrence and does not use products.

Main run:

```bash
KMAX=50 NMAX=60 WMAX=12 OUTDIR=data/finite_experiments \
  python3 scripts/rr/mod5_state_recurrence_probe.py
```

Output:

```text
KMax=50
NMax=60
WMax=12
Diagonal recurrence max residual: 0
Stable defects against corrected bilateral target: none_through_KMax
N=k non-stability examples: []
Finite offset window obstruction rows: 74
Wrote outputs in data/finite_experiments
```

Small reproduction:

```bash
KMAX=12 NMAX=18 WMAX=5 OUTDIR=data/finite_experiments/test_mod5_state_k12 \
  python3 scripts/rr/mod5_state_recurrence_probe.py
```

Output:

```text
KMax=12
NMax=18
WMax=5
Diagonal recurrence max residual: 0
Stable defects against corrected bilateral target: none_through_KMax
N=k non-stability examples: []
Finite offset window obstruction rows: 12
Wrote outputs in data/finite_experiments/test_mod5_state_k12
```

The generated files are:

- `data/finite_experiments/mod5_state_tables.csv`
- `data/finite_experiments/mod5_transition_candidates.csv`
- `data/finite_experiments/mod5_state_failures.csv`
- `data/finite_experiments/mod5_state_support.png`

![Stable coefficients \(c_\alpha(k)\) generated from the \(H_{\alpha,N}\) recurrence; x-axis is degree \(k\), bar color is \(k\bmod 5\), and black markers show the predicted exponent sets \(j(5j-1)/2\) and \(j(5j-3)/2\).](../../data/finite_experiments/mod5_state_support.png)

## Finite-Window Obstruction

For any fixed offset window \(0\le d\le W\), L26 requires
\(T_{\alpha,N-1}(W+1)\) to update \(T_{\alpha,N}(W)\). The five-step
version requires \(T_{\alpha,N-5}(W+5)\). Thus the family
\(\{T_{\alpha,N}(d):0\le d\le W\}\), even split by \(N\bmod 5\), is not
closed under the exact recurrence.

This is not merely a numerical failure. It follows formally from L26:
the coefficient \(T_{\alpha,N-1}(W+1)\) appears with coefficient \(+1\),
and no term inside the window determines it. A closed finite state system
would need an additional relation expressing the next boundary offset in
terms of the tracked states. This branch did not find or prove such a
relation.

The obstruction is limited in scope. It rules out the direct finite
diagonal-window closure derived from \(H_{\alpha,N}\) alone; it does not
rule out a richer state system, a nonlocal involution, or a partition
bijection.

## Uniqueness

L25 gives uniqueness of the full triangular array from the initial row
\(h_{\alpha,0}(0)=1\), \(h_{\alpha,0}(k)=0\) for \(k>0\). Consequently
the stable sequence \(c_\alpha(k)\) is uniquely determined by
\(H_{\alpha,N}\).

What remains unproved is a closed finite modulo-5 recurrence in \(k\) for
the stable sequence alone. The computed stable coefficients agree with
\(b_\alpha(k)\) through degree 50, but this agreement is a consistency
check, not proof.

## Outcome

This branch proves L24-L26 and gives a precise obstruction to the naive
finite shifted modulo-5 state route. The scalar triangular recurrence
uniquely determines the stable coefficient sequence and boundary terms
escape beyond every fixed coefficient cutoff, but the derived diagonal
states do not close in any fixed finite offset window. The transformed
series collapse remains open from this route.
