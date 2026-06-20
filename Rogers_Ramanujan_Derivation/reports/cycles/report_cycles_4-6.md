---
title: "Rogers-Ramanujan Derivation — cycles 4-6"
date: "2026-05-15"
toc: true
toc-depth: 2
numbersections: false
fontsize: "10pt"
---
# Rogers-Ramanujan Derivation — cycles 4-6

## Introduction

Cycles 4-6 continued milestone M2: proving the transformed-series collapse needed to complete the product-transform route for the Rogers-Ramanujan identities. Earlier cycles had already established the formal-power-series framework, the gap-two partition interpretation, the q-difference ladder, and the Euler/Jacobi product half. The open task entering cycle 4 was to prove

\[
\lim_{N\to\infty}H_{\alpha,N}(q)
=
\sum_{j\in\mathbb Z}(-1)^j q^{j(5j-(2\alpha+1))/2},
\qquad \alpha\in\{0,1\},
\]

where

\[
H_{\alpha,N}(q)=\sum_{n=0}^{N}q^{n^2+\alpha n}\frac{(q;q)_N}{(q;q)_n}.
\]

The result of cycles 4-6 is a sharper negative map of the remaining bottleneck. The signed-object model was proved, but three mechanism families were rejected: local absorb/release cancellation, pure nonlocal subset transfer, and direct fixed diagonal-window modulo-5 closure. M2 remains open.

## Definitions and Notation

The finite transformed series is

\[
H_{\alpha,N}(q)=\sum_{n=0}^{N}q^{n^2+\alpha n}\frac{(q;q)_N}{(q;q)_n},
\qquad \alpha=0,1.
\]

Cycle 4 expanded the quotient

\[
\frac{(q;q)_N}{(q;q)_n}=\prod_{s=n+1}^{N}(1-q^s)
\]

as a signed subset sum. Thus each term of \(H_{\alpha,N}\) is represented by a signed object \((n,S,\alpha,N)\), with

\[
S\subseteq\{n+1,\ldots,N\},
\qquad
w_\alpha(n,S)=n^2+\alpha n+\sum_{s\in S}s,
\qquad
\operatorname{sgn}(n,S)=(-1)^{|S|}.
\]

This is lemma L17 in `docs/lemmas/lemma_catalogue.md`, proved in `docs/proof/transformed_series_collapse.md`.

## Cycle 4: Signed Objects and Local Cancellation

Cycle 4 targeted the remaining transformed-series collapse directly. The researcher brief (`c5da6827-f96c-490e-9d57-05d2e455cf11`) asked for a signed-object expansion of \(H_{\alpha,N}\), a candidate sign-reversing involution, and a recurrence fallback.

The worker (`4f6ea7e9-9a3e-4e8f-9ec2-876d392a2e79`) built:

- `docs/proof/transformed_series_collapse.md`
- `scripts/rr/transformed_cancellation_probe.wls`
- `scripts/rr/plot_transformed_cancellation_survivors.py`
- CSV outputs under `data/finite_experiments/`
- `data/finite_experiments/transformed_cancellation_survivors.png`

The local rule tested boundary moves that either absorb tail parts into the staircase or release parts from the staircase boundary into the tail. Weight preservation forced the equations

\[
r(2n+\alpha+r)
\]

for increasing \(n\), and

\[
r(2n+\alpha-r)
\]

for decreasing \(n\). Accepted moves were weight-preserving, sign-reversing, and involutive, but the rule was not total. At \(N=12\), it left 1,887 of 4,059 tested \(\alpha=0\) objects unpaired and all 3,865 tested \(\alpha=1\) objects unpaired.

![Signed survivor pattern for \(H_{\alpha,N}\). Blue bars mark predicted pentagonal-support degrees; gray bars are finite boundary corrections.](data/finite_experiments/transformed_cancellation_survivors.png)

The auditor (`4224d822-c5e9-4052-b07b-2b85d891f2e2`) validated the result as a pivot. L17 was accepted as proved, L18 was rejected as non-total, L19 remained conjectural, and L20 was accepted only as scalar stabilization.

## Cycle 5: Fan-Out to Two Mechanisms

Cycle 5 pivoted away from the failed local rule. The researcher (`63b892ac-9174-41ea-91c4-9ce66bee97b8`) split the work into two independent branches:

- Branch A: a nonlocal sign-reversing involution on signed objects \((n,S)\).
- Branch B: a finite modulo-5 or shifted-state recurrence derived from \(H_{\alpha,N}\) alone.

The branch objective was not another coefficient sweep. Each branch had to produce either a mechanism or a precise obstruction.

## Cycle 6: Integrated Fan-Out Results

Cycle 6 integrated both fan-out outputs into the main workspace (`7bf605a8-a233-4221-b34e-8d1de679900d`). The integration updated:

- `docs/lemmas/lemma_catalogue.md`
- `docs/validation.md`
- `promise_ledger.jsonl`

It retained and linked:

- `docs/proof/nonlocal_transformed_involution.md`
- `docs/proof/mod5_state_recurrence.md`

The post-merge audit input validated the integration as complete, but not as proof closure.

## Nonlocal Involution Branch

The nonlocal branch tested a broader pure subset-transfer rule. An upward move \(n\mapsto n+r\) removes an odd subset \(A\subseteq S\) satisfying

\[
\sum A=r(2n+\alpha+r).
\]

A downward move \(n\mapsto n-r\) adds an odd missing subset satisfying

\[
\sum A=r(2n+\alpha-r).
\]

The probe tested deterministic smallest-\(r\) variants with lexicographic tie-breakers. Accepted transfers had no weight, sign, or tail-condition failures, but the family was rejected for two structural reasons.

First, singleton-tail objects create stable non-pentagonal no-move cases. For \(\alpha=0\), \((0,\{t\})\) can move only if \(t=r^2\), so \((0,\{5\})\) is a non-pentagonal no-move object for every \(N\ge5\). For \(\alpha=1\), \((0,\{t\})\) can move only if \(t=r(r+1)\), so \((0,\{3\})\) is a non-pentagonal no-move object for every \(N\ge3\).

Second, the canonical smallest-\(r\) rule is not involutive. For example, at \(\alpha=0\), \((0,\{4\})\) moves to \((2,\varnothing)\), but the smallest reverse move from \((2,\varnothing)\) lands at \((1,\{3\})\), not the original object.

![Fixed and unpaired objects from the nonlocal transfer search, compared against the predicted pentagonal families.](data/finite_experiments/nonlocal_involution_fixed_points.png)

These results became L21-L23: pure nonlocal subset transfer rejected, singleton-tail obstruction proved, and canonical smallest-\(r\) transfer rejected.

## Modulo-5 / Shifted-State Branch

The recurrence branch started from the scalar identity

\[
H_{\alpha,N}=(1-q^N)H_{\alpha,N-1}+q^{N^2+\alpha N}.
\]

Writing

\[
H_{\alpha,N}(q)=\sum_{k\ge0}h_{\alpha,N}(k)q^k,
\]

it derived the coefficient recurrence

\[
h_{\alpha,N}(k)
=
h_{\alpha,N-1}(k)-h_{\alpha,N-1}(k-N)
+\mathbf 1_{k=N^2+\alpha N}.
\]

This triangular recurrence proves coefficient stabilization: for \(N>k\), the coefficient \(h_{\alpha,N}(k)\) no longer changes.

For diagonal states

\[
T_{\alpha,N}(d)=h_{\alpha,N}(N+d),
\]

the branch proved

\[
T_{\alpha,N}(d)
=
T_{\alpha,N-1}(d+1)-h_{\alpha,N-1}(d)
+\mathbf 1_{d=N^2+(\alpha-1)N}.
\]

This exact recurrence creates the obstruction. Any fixed window \(0\le d\le W\) requires the outside state \(T_{\alpha,N-1}(W+1)\). Iterating five steps only moves the missing boundary to \(W+5\), so splitting by \(N\bmod 5\) does not close the system.

![Stable coefficients generated from the \(H_{\alpha,N}\) recurrence, colored by residue class and overlaid with predicted pentagonal exponents.](data/finite_experiments/mod5_state_support.png)

The recurrence branch produced L24-L26: coefficient recurrence proved, shifted diagonal recurrence proved, and fixed diagonal-window modulo-5 closure rejected for the direct finite-window system.

## Integrated Validation

The post-merge integration reran the main and small checks for both branches.

Modulo-5 recurrence run:

```text
KMax=50
NMax=60
WMax=12
Diagonal recurrence max residual: 0
Stable defects against corrected bilateral target: none_through_KMax
N=k non-stability examples: []
Finite offset window obstruction rows: 74
```

Nonlocal main probe at \(N=12\):

| tie breaker | alpha | objects | paired up | paired down | predicted fixed | no move | involution failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| lex largest | 0 | 4059 | 1250 | 1250 | 70 | 423 | 1066 |
| lex smallest | 0 | 4059 | 1241 | 1241 | 70 | 423 | 1084 |
| lex largest | 1 | 3865 | 714 | 714 | 131 | 738 | 1568 |
| lex smallest | 1 | 3865 | 701 | 701 | 131 | 738 | 1594 |

Both figure checks passed, and `promise_check` exited with warnings only. The warnings were process-scope issues: M3/M4 have not started, M2 remains active, and existing unmanaged session/report artifacts remain.

## Current Proof Status

Proved during cycles 4-6:

- L17: finite signed-object expansion for \(H_{\alpha,N}\).
- L20 scalar part: \(H_{\alpha,N}\) stabilizes coefficientwise.
- L22: singleton-tail obstruction to pure subset-transfer cancellation.
- L24: coefficient recurrence for \(H_{\alpha,N}\).
- L25: shifted diagonal recurrence.

Rejected during cycles 4-6:

- L18: local boundary absorb/release involution, because it is not total.
- L21: pure nonlocal subset-transfer rule, because stable non-pentagonal no-move objects exist.
- L23: canonical smallest-\(r\) nonlocal transfer, because it is not involutive.
- L26: direct fixed diagonal-window modulo-5 closure, because the recurrence requires outside boundary states.

Still open:

- L16/L19: the transformed-series bilateral collapse.
- M2: a complete transfer mechanism proving the Rogers-Ramanujan series equal the product/Jacobi side.

## Open Questions

The next mechanism must add structure beyond the rejected families. The records specifically point to:

- a richer involution with an auxiliary marker or compensation part,
- a recurrence with additional boundary states and a real closing identity,
- or a partition-bijection route outside the transformed subset-transfer model.

Another same-axis coefficient comparison is not enough; future computation needs to propose a map, classify its failures, or prove a closed recurrence.

## References

No `REFERENCES.md` file exists in the workspace, and the cycle records state that no web search or external proof lookup was used. No external references are cited in this report.

## Appendix: Implementation Details

Session references:

| cycle | researcher | worker | auditor |
|---|---|---|---|
| 4 | `c5da6827-f96c-490e-9d57-05d2e455cf11` | `4f6ea7e9-9a3e-4e8f-9ec2-876d392a2e79` | `4224d822-c5e9-4052-b07b-2b85d891f2e2` |
| 5 | `63b892ac-9174-41ea-91c4-9ce66bee97b8` | fan-out branches | branch audit records integrated in cycle 6 |
| 6 | post-merge integration | `7bf605a8-a233-4221-b34e-8d1de679900d` | post-merge audit input |

Code organization after integration:

| path | files | role |
|---|---:|---|
| `scripts/rr/` | 14 | Wolfram probes, Python recurrence mirror, and plotting scripts |
| `docs/proof/` | 6 | q-difference, finite-gap, product-transform, transformed-cancellation, nonlocal-involution, and modulo-5 recurrence notes |
| `docs/lemmas/lemma_catalogue.md` | 1 | Lemmas L0-L26 with proof statuses |
| `docs/validation.md` | 1 | Experimental checks, proof statuses, and rejected-route diagnostics |
| `data/finite_experiments/` | 49 | CSV outputs and figures |

Key commands recorded:

```bash
KMAX=40 NMAX=12 OUTDIR=data/finite_experiments \
  wolfram-batch -script scripts/rr/transformed_cancellation_probe.wls

KMAX=40 NMAX=12 OUTDIR=data/finite_experiments \
  wolfram-batch -script scripts/rr/nonlocal_involution_probe.wls

KMAX=50 NMAX=60 WMAX=12 OUTDIR=data/finite_experiments \
  python3 scripts/rr/mod5_state_recurrence_probe.py

python3 -m long_exposure.tools.promise_check <run-workspace>
```

The workspace `MANIFEST.md` was refreshed for this report with the integrated script inventory, line counts, cumulative stats, and cross-references.
