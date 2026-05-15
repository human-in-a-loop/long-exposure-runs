---
created: 2026-05-15T02:05:00Z
cycle: 7
run_id: run-2026-05-14T232311Z
agent: worker
milestone: M2
---

# Direct Partition-Bijection Probe

This note records the direct combinatorial pivot for M2. It does not claim
a Rogers-Ramanujan proof. It tests whether the already proved gap-two
interpretations expose a simple 5-abacus or beta-set map to the residue
classes.

## Starting Point

L5 proves that

\[
\frac{q^{n^2}}{(q;q)_n}
\]

generates gap-two partitions with exactly \(n\) parts and smallest part at
least \(1\). L6 proves the analogous statement for

\[
\frac{q^{n^2+n}}{(q;q)_n},
\]

with smallest part at least \(2\). L7 proves that the target products
generate partitions with parts in residues \(\{1,4\}\pmod 5\) for
\(\alpha=0\), and \(\{2,3\}\pmod 5\) for \(\alpha=1\).

Thus a direct M2 closure would be a weight-preserving bijection

\[
G_\alpha(K)\longleftrightarrow R_\alpha(K)
\]

for every weight \(K\), where \(G_\alpha(K)\) is the set of gap-two
partitions of \(K\) with smallest part at least \(1+\alpha\), and
\(R_\alpha(K)\) is the corresponding residue-class partition set.

## Coordinates Tested

The probe `scripts/rr/direct_bijection_probe.py` enumerates exact finite
sets through a chosen weight cutoff. For every gap partition \(\lambda\),
it records:

- length \(n=\ell(\lambda)\);
- staircase remainder
  \[
  \mu_i=\lambda_i-\bigl(2(n-i)+1+\alpha\bigr);
  \]
- standard beta-set \(B(\lambda)=\{\lambda_i+n-i\}\), using one-based
  indexing;
- shifted beta-set \(C_\alpha(\lambda)=\{\lambda_i-i+\alpha\}\);
- residues and 5-runner counts of \(B\), \(C_\alpha\), and \(\mu\).

For every residue partition \(\rho\), it records multiplicities of parts
\(5t+r\), runner counts, quotient sums, and simple residue imbalances.

## Candidate Map Diagnostics

The tested candidate families are intentionally simple:

1. match by length and shifted-beta runner counts;
2. match by length and standard-beta runner counts;
3. match by shifted-beta runner counts and shifted-beta quotient sum;
4. match by standard-beta runner counts and standard-beta quotient sum.
5. slide each standard- or shifted-beta bead independently to the nearest
   allowed runner and treat the resulting bead positions as residue parts.

Each is tested weight by weight. A candidate is rejected at the first
weight where the signatures differ between gap and residue classes or are
not one-to-one on either side. The independent bead-slide rule is rejected
at the first object where the nearest allowed-runner slide changes total
weight. This is not a rejection of all direct bijections; it only rejects
these low-information canonical abacus statistics as sufficient data for a
map.

## Current Outcome

Enumeration confirms that the two classes have equal cardinalities through
the tested range for both values of \(\alpha\), as expected from earlier
coefficient checks. The simple beta-set and runner-count signatures do not
determine a canonical bijection. They fail by minimal low-weight
counterexamples: either a gap signature has no matching residue signature,
or multiple partitions on one side share the same signature.

The conclusion for this cycle is therefore partial and negative:
the direct partition-bijection route remains viable, but it needs richer
structure than raw beta-set runner counts, quotient sums, or length. A
successful map likely needs an ordered bead-sliding process, a charge
with local choices, or a recursive insertion/deletion rule rather than a
static abacus signature.
