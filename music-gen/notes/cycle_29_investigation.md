---
created: 2026-08-28T23:30:00Z
cycle: 29
run_id: run-2026-08-28T040704Z
agent: worker
milestone: M-GEN-1/collision-model-hash-space-geometry
---

# Cycle 29 — Investigation notes (read-only)

Working notes for the auditor's adjudication direction. Not committed to
the ledger yet — findings folded into the deliverable doc + rubric.

## The 35-cell p-vector

`data/collision_model/hash_uniformity.tsv` contains 35 rows: 7 batches
(`batch_v1`, `batch_v2`, `batch_v3_i3`, `batch_v3_i4`, `batch_v4`,
`batch_v5_n16`, `batch_v6`) × 5 rule_types (harmonic, rhythmic,
melodic, form, arrangement).

Only one cell reaches raw p < 0.05:

    batch_v2 x harmonic
        K = 10, N_salts = 8, unique_winners = 5
        chi^2 = 17.000000, dof = 9
        raw p_value = 0.048716
        winner_index_sequence = [0, 0, 4, 3, 5, 0, 0, 1]

The second-nearest cell is batch_v1 × rhythmic at p = 0.052456
(K=18, N=5, chi²=27.4, dof=17). Not significant even at raw α.

## Populating rule for the significant cell

Salts {0, 1, 5, 6} — four of the eight — pick the same rank-0 rule:

    rule_0271c7a9f3b5f606 (song-level harmonic, cadence + chord_progression + key)
        clip_id: 1d723bf1d16087b6
        transcription_event_id: 5d9f8c9e81684577ca94fb6d14b18b81
        scope.level: song; start_s=0.0, end_s=262.0
        extractor_version: harmonic-v1

This is the "cycle-13 4-salt clique" flagged in the cycle-28 handoff.
It's a **legacy content cluster** — one song-level harmonic rule on
the pre-I3 76-row ledger with an SHA-256 rank-0 digest-prefix that
happens to sit at the front of the sort for a plurality of the
batch_v2 salts.

Under the I3 D-minor augmentation (K=20 in batch_v3_i3 and later),
this cell disappears — every rule_type × batch cell has p ≥ 0.11
except batch_v6 × harmonic p = 0.457. The I3 rewrite of harmonic
rules broke the clique.

## Predicted rubric outcomes

Given the input p-vector:

- 34 of 35 cells have raw p ≥ 0.264. Only 1 cell at raw p = 0.049.
- **Bonferroni** at α=0.05, m=35 → threshold p ≤ 0.001428.
  Result: 0 cells survive. 0.049 fails by a factor of ~34.
- **Šidák** at α=0.05, m=35 → threshold p ≤ 1 − (1 − 0.05)^(1/35) ≈ 0.001465.
  Result: 0 cells survive (essentially identical to Bonferroni here).
- **Benjamini-Hochberg** at q=0.05:
  Sort p-values ascending; compare p_(i) to i × q / m = i × 0.05 / 35 = i × 0.001428.
  Rank 1 = 0.049 vs threshold 0.001428 → FAIL.
  No p smaller than 0.049, so all others fail too.
  Result: 0 cells survive BH.

Therefore the frozen rubric prediction is:

    verdict = M3_COLLAPSES_TO_REFUTES

- No cell survives BH q < 0.05.
- The cycle-28 raw p = 0.049 was a multiple-testing artifact.

## Drop-batch_v2 sensitivity (predicted)

If batch_v2 is excluded, the 35-cell p-vector reduces to 30 cells (5
rule_types × 6 remaining batches). The p = 0.049 cell — the only
raw-significant cell — is removed by construction. The second-nearest
cell (batch_v1 × rhythmic, p = 0.052) remains, but it too fails BH
q = 0.05 (threshold ≈ 0.001667 at rank 1, m=30).

No survivors under drop-v2 either. The overall R²(M3-corrected) is
also expected to move: cycle-28's R² was −0.240 across three
shape-informative batches; dropping batch_v2 leaves only batch_v3_i3
(R² = −0.207) and batch_v6 (R² = −0.840); mean ≈ −0.524.

## Leave-one-cell-out (predicted)

With only one raw-significant cell to begin with, holding out
batch_v2 × harmonic reduces the count of significant cells to 0
before any correction. Every other cell's contribution to the raw
count is 0. So leave-one-cell-out shows total concentration of the
signal in a single cell.

## Auditor's fourth outcome for reference

MIXED would require exactly one BH survivor whose absence under
drop-v2 changes the picture. Since we expect 0 BH survivors from the
start, MIXED is structurally unreachable given this p-vector.

## Sanity checks before running scripts

- The 35-cell p-vector already exists in
  `data/collision_model/hash_geometry_verdict.json` (`per_rule_type_chi2`)
  and in `data/collision_model/hash_uniformity_summary.json`
  (`batches[<b>][<rt>]`). We consume the latter.
- Cycle-28 utilities are read-only anchors — no modification.
- The α = 0.7469387071101908 pin is preserved (drop-v2 and LOCO use
  the same α, only the K-vector and observed-collision-vector change).
