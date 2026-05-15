---
created: 2026-05-15T01:05:00Z
cycle: 5
run_id: run-2026-05-14T232311Z
agent: worker-clone-0
milestone: M2
---

# Nonlocal Transformed Involution

This branch tests a nonlocal sign-reversing involution for

\[
H_{\alpha,N}(q)=\sum_{n=0}^N q^{n^2+\alpha n}{(q;q)_N\over(q;q)_n},
\qquad \alpha\in\{0,1\}.
\]

The tested family is broader than the previous local boundary rule: it may
move any non-adjacent subset of the tail, provided the subset has exactly the
weight needed to change the staircase length. The result is a rejection of
this pure subset-transfer family, not a rejection of all possible involutions.

## Signed Object Model

For \(0\le n\le N\),

\[
{(q;q)_N\over(q;q)_n}=\prod_{s=n+1}^N(1-q^s)
=\sum_{S\subseteq\{n+1,\ldots,N\}}(-1)^{|S|}q^{\sum_{s\in S}s}.
\]

Thus

\[
H_{\alpha,N}(q)=
\sum_{n=0}^N\sum_{S\subseteq\{n+1,\ldots,N\}}
(-1)^{|S|}q^{w_\alpha(n,S)}
\]

where

\[
w_\alpha(n,S)=n^2+\alpha n+\sum_{s\in S}s.
\]

The base term is a staircase:

\[
n^2=1+3+\cdots+(2n-1),
\qquad
n^2+n=2+4+\cdots+2n.
\]

The sign of an object is \((-1)^{|S|}\), so a pure absorb/release transfer
must move an odd number of tail parts.

## Nonlocal Transfer Rule Candidate

For an upward move \(n\mapsto n+r\), weight preservation forces

\[
\Delta^+_\alpha(n,r)
=(n+r)^2+\alpha(n+r)-n^2-\alpha n
=r(2n+\alpha+r).
\]

The candidate removes an odd subset

\[
A\subseteq S,\qquad \sum A=\Delta^+_\alpha(n,r),
\]

and replaces \((n,S)\) by \((n+r,S\setminus A)\), subject to the new tail
condition \(S\setminus A\subseteq\{n+r+1,\ldots,N\}\).

For a downward move \(n\mapsto n-r\), weight preservation forces

\[
\Delta^-_\alpha(n,r)
=n^2+\alpha n-(n-r)^2-\alpha(n-r)
=r(2n+\alpha-r).
\]

The candidate adds an odd subset

\[
A\subseteq\{n-r+1,\ldots,N\}\setminus S,
\qquad \sum A=\Delta^-_\alpha(n,r),
\]

and replaces \((n,S)\) by \((n-r,S\cup A)\).

The probe tests two deterministic choices:

1. choose the smallest admissible \(r\), then the lexicographically largest
   transfer subset in decreasing order;
2. choose the smallest admissible \(r\), then the lexicographically smallest
   transfer subset in decreasing order.

When upward and downward moves exist for the same smallest \(r\), the probe
chooses the upward move. The rejection below does not depend on this priority,
because the decisive no-move obstructions have no downward move and no upward
move.

## Failure Classifier

The probe is `scripts/rr/nonlocal_involution_probe.wls`. It writes:

- `data/finite_experiments/nonlocal_involution_candidates.csv`
- `data/finite_experiments/nonlocal_involution_failures.csv`
- `data/finite_experiments/nonlocal_involution_fixed_points.csv`
- `data/finite_experiments/nonlocal_involution_summary.csv`

It classifies objects as `paired_up`, `paired_down`, `fixed_predicted`,
`no_admissible_move`, `involution_failure`, `weight_failure`,
`sign_failure`, or `tail_condition_failure`.

Main command:

```bash
KMAX=40 NMAX=12 OUTDIR=data/finite_experiments wolfram-batch -script scripts/rr/nonlocal_involution_probe.wls
```

Output summary at \(N=12\):

| tie breaker | alpha | objects | paired up | paired down | predicted fixed | no move | involution failures | weight/sign/tail failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| lex largest | 0 | 4059 | 1250 | 1250 | 70 | 423 | 1066 | 0 |
| lex smallest | 0 | 4059 | 1241 | 1241 | 70 | 423 | 1084 | 0 |
| lex largest | 1 | 3865 | 714 | 714 | 131 | 738 | 1568 | 0 |
| lex smallest | 1 | 3865 | 701 | 701 | 131 | 738 | 1594 | 0 |

Small repro:

```bash
KMAX=12 NMAX=6 OUTDIR=data/finite_experiments/test_nonlocal_involution_k12 wolfram-batch -script scripts/rr/nonlocal_involution_probe.wls
```

This already shows both `no_admissible_move` and `involution_failure`
classes for both tie-breakers.

![Fixed and unpaired objects for the nonlocal transfer search, plotted by exponent and compared against the predicted pentagonal families for \(\alpha=0,1\).](../../data/finite_experiments/nonlocal_involution_fixed_points.png)

## Rejection

The pure subset-transfer family fails before any tie-breaker matters.

For \(\alpha=0\), take the object \((n,S)=(0,\{t\})\) with \(N\ge t\). A
downward move is impossible because \(n=0\). An upward move by \(r\) must
remove an odd subset \(A\subseteq\{t\}\). To change sign, \(A=\{t\}\), and
weight preservation requires

\[
t=\Delta^+_0(0,r)=r^2.
\]

Therefore \((0,\{t\})\) has no admissible pure transfer whenever \(t\) is not
a square. The first useful instance is \(t=5\): its exponent is \(5\), which
is not of the form \(j(5j-1)/2\) for any integer \(j\) in the relevant range
(\(0,2,3,9,\ldots\) are the first values). Thus the rule canonically leaves a
non-pentagonal object unpaired.

For \(\alpha=1\), the same singleton-tail obstruction gives

\[
t=\Delta^+_1(0,r)=r(r+1).
\]

So \((0,\{t\})\) has no admissible pure transfer whenever \(t\) is not pronic.
The first useful instance is \(t=3\): its exponent is \(3\), while the target
exponents \(j(5j-3)/2\) begin \(0,1,4,7,\ldots\). This is again a stable
non-pentagonal no-move object.

These are structural obstructions. They survive for every \(N\ge5\) in the
\(\alpha=0\) case and every \(N\ge3\) in the \(\alpha=1\) case, and they are
not boundary artifacts. They also do not depend on choosing lexicographically
largest or smallest admissible subsets, since no admissible subset exists.

The candidate family also has involutivity failures where a move exists. For
example, with \(\alpha=0\), \(N\ge4\), the object \((0,\{4\})\) moves upward
by \(r=2\) to \((2,\varnothing)\). But the smallest admissible reverse move
from \((2,\varnothing)\) is \(r=1\), releasing \(\{3\}\), so the map sends it
to \((1,\{3\})\), not back to \((0,\{4\})\). This shows that the smallest-\(r\)
canonical rule is not involutive even on objects that do admit a transfer.

Consequently this branch does not close M2. Any successful involution must
use extra structure beyond pure exact subset transfer between the staircase
and the signed distinct tail, such as an auxiliary marker, a parity-changing
compensation part, or a different finite-state mechanism.
