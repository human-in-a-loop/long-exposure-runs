---
created: 2026-05-14T23:55:00Z
cycle: 2
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Finite Gap-Two Recurrence

This note records the independent finite recurrence route for the gap-two partition side. It is not yet promoted to a proof of the product identities.

## L11. Largest-Part Recurrence

**Status:** `proved`

Let `G_N^{(a)}` generate partitions whose parts are at least `a`, adjacent parts differ by at least `2`, and largest part is at most `N`. The empty partition is allowed, and `G_N^{(a)}=1` for `N<a`.

For `N>=a`,

\[
G_N^{(a)}=G_{N-1}^{(a)}+q^N G_{N-2}^{(a)}.
\]

Proof: split the admissible partitions by whether part `N` appears. If `N` is absent, the contribution is `G_{N-1}^{(a)}`. If `N` is present, it appears once because of the gap condition, and every remaining part is at most `N-2`; removing `N` gives contribution `q^N G_{N-2}^{(a)}`. These cases are disjoint and exhaustive.

The Rogers-Ramanujan series sides are the coefficientwise limits:

\[
\lim_{N\to\infty}G_N^{(1)}=A_0,\qquad \lim_{N\to\infty}G_N^{(2)}=A_1,
\]

using the staircase interpretations already proved in L5 and L6.

## Modulo-Five Subsequence Test

The recurrence has period-free coefficients `q^N`; modulo-five structure is therefore not visible from the recurrence alone. It becomes visible only after grouping the finite sequence into residue classes `N=5m+r` or after finding a closed finite form for selected subsequences.

The finite diagnostic in `data/finite_experiments/finite_gap_subsequence.csv` compared `G_N^{(1)}` with the bounded product using parts `<=N` in residues `{1,4}`, and `G_N^{(2)}` with the bounded product using parts `<=N` in residues `{2,3}`. This naive finite product is not the right finite identity: for example, at `N=30`, the first differences occur at coefficient `32` and `31` respectively, so agreement improves with `N` only as a truncation-shadow of the infinite identity.

The current q-difference probe confirms a related fact: the infinite ladder route gives a unique tail-normalized sequence, and the residue products agree with its first two states through the checked truncation. However, no proved finite identity of the form

\[
G_{5m+r}^{(a)}=\text{simple finite residue product with an explicit correction}
\]

has been proved in this cycle. The finite route remains viable, but the next step must be to derive a concrete finite correction pattern rather than infer it from coefficient agreement.

## Obstruction Recorded

The largest-part recurrence is proof-bearing for the series/gap-two side, but it has one scalar state indexed by largest part. The residue products are naturally controlled by allowed part sizes modulo five. A bridge likely needs a five-state finite system or a finite polynomial identity that tracks the correction terms across a full modulo-five block.
